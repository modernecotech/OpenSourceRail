"""v0.6 service energy and passive LIM secondary necessary bounds.

No traction battery is fitted. Supplier reference figures below define an
analytical service-pack alternative; they do not qualify a railway pack.
"""
from __future__ import annotations
from math import ceil
from . import ROOT, FLAGS
from .common import brief, identity, source_map

BATTERY_SOURCE = {
    'title': 'Toshiba Battery System Components, April 2025, pp.6–8',
    'url': 'https://www.global.toshiba/content/dam/toshiba/ww/products-solutions/battery/scib/pdf/BatterySystemComponents-en202504.pdf',
    'retrieved': '2026-10-26',
    'pdf_sha256': '11b6d5b66ae2d755d5d2175df27f68cf7b2b9907ebf4be53b2424c9ec6abe86a',
    'scope': 'Type3-20 module reference, not rail application approval; catalogue values are not guaranteed. Some listed peripherals were due to cease sale in March 2026. No discontinued peripheral is selected here.',
}
CELL_SOURCE = {
    'url': 'https://www.global.toshiba/ww/products-solutions/battery/scib/product-next/product/cell/high-energy.html',
    'retrieved': '2026-10-26', 'scope': '20Ah cell nominal mass/energy only; do not add cell mass to module mass.',
}
PRODUCERS = ('engineering/station_rail/electrical.py',)


def battery_definition(root=ROOT, *, parallel_strings=3):
    if parallel_strings not in (2, 3):
        raise ValueError('Compare the explicit 50- or 75-module architectures')
    modules = 25 * parallel_strings
    accessories = [
        dict(component='enclosure and module racks',mass_kg=45.0*parallel_strings),
        dict(component='DC protection, monitoring and busbars',mass_kg=45.0),
        dict(component='cooled enclosure circuit and heat exchanger',mass_kg=55.0),
        dict(component='isolated service DC/DC and low voltage supplies',mass_kg=30.0),
        dict(component='station charge connector and isolation',mass_kg=20.0),
        dict(component='isolation and retention mounts',mass_kg=10.0),
    ]
    v = dict(schema='osr-service-battery-definition/1',
        role='Services and essential systems only; no wheel-drive connection',
        supplier_reference='Toshiba SCiB Type3-20 FM01202CCA04A',
        modules_in_series=25,parallel_strings=parallel_strings,module_count=modules,
        cells_per_module=24,cells_in_series=300,cells_in_parallel=2*parallel_strings,
        nominal_voltage_V=25*27.6,catalogue_voltage_range_V=[25*18.0,25*32.4],
        gross_energy_kWh=modules*1.104,nominal_capacity_Ah=40.*parallel_strings,
        continuous_current_reference_A=160.*parallel_strings,
        conservative_voltage_current_power_kW=25*18.*160*parallel_strings/1000,
        supplier_module_mass_kg=14.*modules,
        cell_mass_kg=.515*24*modules,
        accessories=accessories,
        unlocated_allowance_kg=sum(a['mass_kg'] for a in accessories),
        mass_kg=14.*modules+sum(a['mass_kg'] for a in accessories),
        catalogue_ambient_range_C=[-30.,45.],
        installed_mass_complete=False,geometry_complete=False,
        supplier_railway_approval=False,
        temperature_and_SOC_charge_map=None,
        ambient50C_disposition='outside module ambient catalogue range; cooled enclosure needs demonstrated temperature control',
        sources=[BATTERY_SOURCE,CELL_SOURCE],
        component_id=None,**{k:v for k,v in FLAGS.items() if k!='installed_mass_complete'})
    v['component_id']=identity({k:value for k,value in v.items() if k!='component_id'})
    return v


def charge_leg(runtime_s, dwell_s=35., hotel_kW=35., charging_power_kW=200.,
               *, root=ROOT, parallel_strings=3, efficiency=.95,
               module_environment_C=25.):
    """Energy balance with hotel consumption during charging and catalogue I cap.

    Charge power is capped using the *lowest* catalogue module voltage. This
    does not assume a flat 690 V pack. The missing temperature/SOC charge map is
    a separate unknown even when this necessary energy/current bound passes.
    """
    values=(runtime_s,dwell_s,hotel_kW,charging_power_kW,efficiency)
    if runtime_s is None or any(float(x)<0 for x in values) or not 0<efficiency<=1:
        raise ValueError('Nonnegative duration/power and positive efficiency required')
    battery=battery_definition(root,parallel_strings=parallel_strings)
    allowed=min(charging_power_kW,battery['conservative_voltage_current_power_kW'])
    flight=hotel_kW*runtime_s/3600
    dwell_hotel=hotel_kW*dwell_s/3600
    charge=allowed*efficiency*dwell_s/3600
    net=charge-dwell_hotel
    deficit=max(0.,flight-net)
    net_rate=allowed*efficiency-hotel_kW
    extra=deficit*3600/net_rate if net_rate>0 else None
    balanced=deficit<=1e-10
    return dict(schema='osr-wheel-service-energy-leg/1',
        runtime_s=runtime_s,dwell_s=dwell_s,hotel_kW_per_car=hotel_kW,
        requested_charge_power_kW_per_car=charging_power_kW,
        catalogue_low_voltage_current_capped_charge_kW_per_car=allowed,
        charging_efficiency_hypothesis=efficiency,
        energy_used_kWh_per_car=flight,
        dwell_hotel_energy_kWh_per_car=dwell_hotel,
        gross_charge_input_kWh_per_car=allowed*dwell_s/3600,
        battery_energy_from_charger_kWh_per_car=charge,
        net_charge_energy_kWh_per_car=net,
        energy_deficit_kWh_per_car=deficit,
        energy_surplus_kWh_per_car=max(0.,net-flight),
        minimum_extra_terminal_charge_s_per_leg=extra,
        minimum_sustainable_dwell_s=flight*3600/net_rate if net_rate>0 else None,
        energy_balance_screen='pass' if balanced else 'fail',
        module_environment_C=module_environment_C,
        ambient_catalogue_screen='pass' if -30<=module_environment_C<=45 else 'fail',
        actual_charge_power_available=None,
        actual_charge_qualified=False,
        battery_component_id=battery['component_id'])


def state_of_charge(legs, *, initial_SOC=.9, minimum_SOC=.2, maximum_SOC=.9,
                    hotel_kW=35., charging_power_kW=200., dwell_s=35.,
                    end_of_life_fraction=.8,hot_capacity_fraction=.9,
                    root=ROOT,parallel_strings=3):
    """Propagate retained energy, include charge saturation and station hotel load."""
    if not 0<=minimum_SOC<=initial_SOC<=maximum_SOC<=1:
        raise ValueError('Invalid SOC interval')
    battery=battery_definition(root,parallel_strings=parallel_strings)
    effective=battery['gross_energy_kWh']*end_of_life_fraction*hot_capacity_fraction
    energy=effective*initial_SOC;floor=effective*minimum_SOC;ceiling=effective*maximum_SOC
    rows=[];lowest=initial_SOC
    for i,leg in enumerate(legs):
        seconds=leg.get('runtime_s') if isinstance(leg,dict) else leg
        if seconds is None: raise ValueError('Cannot propagate an unexecuted leg')
        bal=charge_leg(seconds,dwell_s,hotel_kW,charging_power_kW,root=root,parallel_strings=parallel_strings)
        arrival=energy-bal['energy_used_kWh_per_car'];lowest=min(lowest,arrival/effective)
        after=min(ceiling,arrival+bal['net_charge_energy_kWh_per_car'])
        rows.append(dict(leg=i,depart_SOC=energy/effective,arrival_SOC=arrival/effective,
            after_dwell_SOC=after/effective,arrival_energy_kWh=arrival,
            floor_violated=arrival<floor,balance=bal))
        energy=after
    missing=max(0.,ceiling-energy)
    allowed=min(charging_power_kW,battery['conservative_voltage_current_power_kW'])
    rate=.95*allowed-hotel_kW
    return dict(schema='osr-service-battery-route/1',battery_component_id=battery['component_id'],
        effective_capacity_kWh=effective,usable_SOC_window_kWh=effective*(maximum_SOC-minimum_SOC),
        end_of_life_fraction_hypothesis=end_of_life_fraction,
        hot_capacity_fraction_hypothesis=hot_capacity_fraction,legs=rows,
        lowest_SOC=lowest,final_SOC=energy/effective,
        reserve_screen='pass' if lowest>=minimum_SOC else 'fail',
        terminal_replenishment_energy_kWh_per_car=missing,
        minimum_terminal_extra_charge_s=missing*3600/rate if rate>0 else None,
        thermal_and_supplier_qualification='unknown')


def secondary_heat(profile, secondary_aluminium_mass_kg, *, slip=.1,
                   ambient_C=50., heat_capacity_J_kg_K=900.,
                   receiving_mode='friction-brake'):
    """Necessary LIM acceleration secondary heat: s/(1-s) times useful work.

    Assumes fixed motoring slip. It is not a thrust model. Default arrival uses
    independent friction brakes, so no assumed motor regen reduces duty. A
    receiving induction-brake heat bound requires its own slip/circuit map.
    """
    if not 0<slip<1 or secondary_aluminium_mass_kg<=0:
        raise ValueError('Finite positive secondary mass and slip in (0,1) required')
    useful=profile['launch_mechanical_energy_J_per_car']
    loss=slip/(1-slip)*useful
    delta=loss/(secondary_aluminium_mass_kg*heat_capacity_J_kg_K)
    interval=profile['runtime_s']+35.
    return dict(slip_hypothesis=slip,launch_secondary_loss_J_per_car=loss,
        counted_secondary_aluminium_mass_kg=secondary_aluminium_mass_kg,
        specific_heat_J_kg_K_hypothesis=heat_capacity_J_kg_K,
        adiabatic_temperature_rise_K=delta,
        launch_after_temperature_C=ambient_C+delta,
        repeated_duty_heat_rejection_W_per_car=loss/interval,
        receiving_mode=receiving_mode,
        receiving_secondary_heat_J=None if receiving_mode!='friction-brake' else 0.,
        actual_secondary_temperature_C=None,
        thermal_screen='unknown',
        heat_capacity_participation_hypothesis='All supplied aluminium mass is instantaneously isothermal; active-fin-only bound must also be inspected',
        contact_conductance_W_K=None,
        reason='End effects, skin effect, actual slip map, joints, heat transfer and receiving motor losses require coupled electromagnetic/thermal calculation')


def evaluate(vehicle, profiles, root=ROOT):
    config=brief(root);service=config['services'];default=battery_definition(root)
    reference=next(p for p in profiles if p['inputs']['distance_m']==2000 and p['inputs'].get('loading')=='normal')
    alternatives=[]
    for strings in (2,3):
        b=battery_definition(root,parallel_strings=strings)
        for hotel in (service['reference_hotel_kW_per_car'],service['adverse_hotel_kW_per_car']):
            r=charge_leg(reference['runtime_s'],config['service']['dwell_s'],hotel,
                service['charging_power_kW_per_car_target'],root=root,parallel_strings=strings)
            alternatives.append(dict(battery=b,hotel_kW_per_car=hotel,leg=r))
    rows=[dict(profile_id=p['profile_id'],loading=p['inputs'].get('loading'),
        distance_m=p['inputs']['distance_m'],
        reference=charge_leg(p['runtime_s'],root=root),
        adverse=charge_leg(p['runtime_s'],hotel_kW=50.,root=root,module_environment_C=50.))
        for p in profiles if p['reachable']]
    sec=vehicle.get('propulsion',{}).get('secondary_aluminium_mass_kg',58.536)
    active=vehicle.get('propulsion',{}).get('active_fin_aluminium_mass_kg',58.536)
    heat=[]
    for slip in (.02,.05,.1,.15,.25):
        whole=secondary_heat(reference,sec,slip=slip)
        local=secondary_heat(reference,active,slip=slip)
        heat.append(dict(profile_id=reference['profile_id'],**whole,
            active_fin_only_bound=dict(active_fin_aluminium_mass_kg=active,
                adiabatic_temperature_rise_K=local['adiabatic_temperature_rise_K'],
                initial_ambient_C=50.,contact_conductance_W_K=None,
                actual_secondary_temperature_C=None,
                note='Heat initially restricted to active plate; spreader/hanger heat capacity not credited before a transient conduction model exists.')))
    effective=default['gross_energy_kWh']*.8*.9*.7
    value=dict(schema='osr-wheel-electrical-evaluation/1',
        **{k:vehicle[k] for k in ('candidate_id','body_candidate_id','support_component_id','propulsion_component_id')},
        battery=default,battery_alternatives=alternatives,service_legs=rows,
        secondary_thermal=heat,
        minimum_usable_battery_energy_kWh_hypothesis=effective,
        emergency_endurance_s_hypothesis=dict(essential_5kW=effective/5*3600,
            hotel_35kW=effective/35*3600,adverse_50kW=effective/50*3600,
            target_s=service['emergency_endurance_s_target'],
            note='Full permitted SOC window at hot EOL; dispatch reserve must also preserve this after worst leg.'),
        station_charging_train_target_kW=6*service['charging_power_kW_per_car_target'],
        installed_station_supply_kW=None,
        HVAC=dict(reference_electrical_kW_per_car=35.,adverse_electrical_kW_per_car=50.,
            delivered_cooling_kW_at_50C=None,thermal_comfort_and_air_quality='unknown',
            note='Hotel power scenarios are energy hypotheses, not demonstrated HVAC capacity.'),
        source_sha256=source_map(root,PRODUCERS),**FLAGS)
    value['evaluation_id']=identity(value)
    return value
