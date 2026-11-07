"""Battery/auxiliary screening with explicit catalogue domains and mission bounds."""
from pathlib import Path
from math import prod,isfinite,exp,fsum
import json
from engineering.station_rail.common import identity,digest
from . import ROOT,FLAGS

POLICY='engineering/railway_closure/electrical-policy.json'
FACTS='engineering/railway_closure/data/battery-facts.json'


def load(root=ROOT):
    root=Path(root);p=json.loads((root/POLICY).read_bytes());f=json.loads((root/FACTS).read_bytes())
    if p.get('schema')!='osr-closure-electrical-policy/1' or f.get('schema')!='osr-battery-catalogue-facts/1':
        raise ValueError('Explicit electrical policy and source catalogue required')
    for k in ('operating_soc_fraction','capacity_derating_hypothesis','battery_output_efficiency_hypothesis',
              'charging_efficiency_hypothesis','module_current_lower_fraction_hypothesis'):
        if not 0<p[k]<=1:raise ValueError('Physical fraction outside range: '+k)
    return p,f


def battery(module_name,parallel,*,root=ROOT):
    p,f=load(root)
    if module_name not in f['modules'] or type(parallel) is not int or parallel<1 or parallel>4:
        raise ValueError('Explicit supported module and parallel-string count required')
    m=f['modules'][module_name];series=p['series_modules'];modules=series*parallel
    nominal=modules*m['nominal_energy_Wh']/1000
    usable=nominal*p['operating_soc_fraction']*p['capacity_derating_hypothesis']*p['battery_output_efficiency_hypothesis']
    # Auxiliary converter outages while traction remains supplied; traction loss
    # itself requires independent stopping and emergency service, not battery traction.
    outage_s=p['auxiliary_converter_outage_intervals']*(p['maximum_interval_run_s']+p['interval_dwell_s'])
    missions={}
    minimum_voltage=series*m['voltage_range_V'][0]
    max_voltage=series*m['voltage_range_V'][1]
    nominal_voltage=series*m['voltage_V']
    current_hypothesis=m['catalogue_continuous_current_A_at_25C']*p['module_current_lower_fraction_hypothesis']
    for label,hotel in (('normal',p['normal_hotel_kw_per_car']),('hot',p['hot_hotel_kw_per_car'])):
        requested=hotel*(p['emergency_full_hotel_minutes']/60+outage_s/3600)
        discharge=hotel*1000/p['battery_output_efficiency_hypothesis']/minimum_voltage/parallel
        charge_kw=min(nominal*p['charge_c_rate_request'],
            max(0.,p['onboard_converter_rating_kw_per_car']-hotel)*p['charging_efficiency_hypothesis'])
        charge=charge_kw*1000/minimum_voltage/parallel
        missions[label]=dict(hotel_kw_per_car=hotel,emergency_plus_outages_requested_kwh=requested,
            delivered_usable_kwh_hypothesis=usable,reserve_margin_kwh=usable-requested,
            maximum_module_discharge_current_A=discharge,maximum_module_charge_current_A=charge,
            hypothetical_derated_current_limit_A=current_hypothesis,
            charge_power_to_battery_kw=charge_kw,full_mission_replenish_time_s=requested/p['battery_output_efficiency_hypothesis']/charge_kw*3600 if charge_kw else None,
            energy_screen=usable>=requested,provisional_current_screen=max(discharge,charge)<=current_hypothesis,
            catalogue_current_verified_at_pack_target=False)
    pods=modules/p['modules_per_pod']
    if pods!=int(pods):raise ValueError('This pod layout uses five whole modules')
    dims=p['pod_external_dimensions_m'][module_name]
    area=2*(dims[0]*dims[1]+dims[0]*dims[2]+dims[1]*dims[2])*pods
    worst_current=max(v['maximum_module_discharge_current_A'] for v in missions.values())
    charge_current=max(v['maximum_module_charge_current_A'] for v in missions.values())
    # This resistance is an explicit assumed STRING value, not inferred from a
    # nominal catalogue efficiency or presented as a measured hot resistance.
    R=p['pack_resistance_ohm_per_string_hypothesis'];ohmic=parallel*max(worst_current,charge_current)**2*R
    ambient=p['external_ambient_C'];target=p['conditioned_pack_target_C'];delta=max(0.,ambient-target)
    heat=[ohmic+area*U*delta for U in p['insulation_U_W_m2K_cases']]
    cooling=p['conditioner_cooling_kw_hypothesis']*1000
    direct_ambient=m['ambient_range_C'][0]<=ambient<=m['ambient_range_C'][1]
    result=dict(schema='osr-service-battery-outline/1',module_name=module_name,manufacturer_model=m['model'],
        series_modules=series,parallel_strings=parallel,modules_per_car=modules,modules_per_six_car_train=6*modules,
        nominal_pack_voltage_V=nominal_voltage,pack_voltage_range_V=[minimum_voltage,max_voltage],
        nominal_pack_energy_kwh=nominal,module_mass_kg_per_car=modules*m['mass_kg'],
        five_module_pods_per_car=int(pods),module_envelope_m=m['envelope_m'],pod_external_dimensions_m=dims,
        pod_outer_surface_m2_per_car=area,missions=missions,
        thermal=dict(external_ambient_C=ambient,conditioned_target_C=target,
            catalogue_direct_ambient_screen=direct_ambient,active_conditioning_required=True,
            catalogue_current_rating_ambient_C=f['current_rating_temperature_C'],
            worst_ohmic_heat_W_hypothesis=ohmic,ambient_and_ohmic_heat_W_cases=heat,
            cooling_capacity_W_hypothesis=cooling,cooling_margin_W_cases=[cooling-x for x in heat],
            conditioner_electric_power_W_hypothesis=cooling/p['conditioner_COP_hypothesis'],
            cooler_load_already_in_hotel_allowance=True,thermal_hardware_characteristic_measured=False),
        internal_energy_screen=all(v['energy_screen'] for v in missions.values()),
        current_hypothesis_screen=all(v['provisional_current_screen'] for v in missions.values()),
        conditioned_thermal_screen=all(cooling>=x for x in heat),
        source=f['source'],manufacturer_hot_current_curve_received=p['manufacturer_hot_current_curve_received'],
        source_sha256={POLICY:digest(Path(root)/POLICY),FACTS:digest(Path(root)/FACTS),
            'engineering/railway_closure/electrical.py':digest(Path(root)/'engineering/railway_closure/electrical.py')},
        scope='Calculated emergency/auxiliary-converter-outage reserve. Continuous traction/aux feed, pack protection, cooling and hot current curves require independent engineering evidence. No battery propulsion assumed.',**FLAGS)
    result['evaluation_id']=identity(result);return result


def repeated_thermal(heat_intervals,*,initial_C,ambient_C,capacity_J_K,rejection_W_K,cooling_W=0.):
    """Exact piecewise-constant one-node RC method; numerical hypothesis only."""
    for value in (initial_C,ambient_C,capacity_J_K,rejection_W_K,cooling_W):
        if not isfinite(value):raise ValueError('Finite thermal inputs required')
    if capacity_J_K<=0 or min(rejection_W_K,cooling_W)<0:raise ValueError('Positive C and nonnegative K/cooling required')
    t=0.;temperature=initial_C;rows=[];input_J=0.;removed_J=0.
    for interval in heat_intervals:
        duration=interval['duration_s'];power=interval['heat_W']
        if not isfinite(duration) or not isfinite(power) or duration<=0 or power<0:raise ValueError('Positive time and nonnegative heat required')
        net=power-cooling_W
        if rejection_W_K==0:new=temperature+net*duration/capacity_J_K
        else:
            equilibrium=ambient_C+net/rejection_W_K
            new=equilibrium+(temperature-equilibrium)*exp(-rejection_W_K*duration/capacity_J_K)
        supplied=power*duration;removed=supplied-capacity_J_K*(new-temperature)
        input_J+=supplied;removed_J+=removed;t+=duration
        rows.append(dict(end_s=t,initial_C=temperature,final_C=new,heat_input_J=supplied,total_heat_removed_J=removed))
        temperature=new
    return dict(schema='osr-piecewise-thermal-proxy/1',intervals=rows,initial_C=initial_C,final_C=temperature,
        input_heat_J=input_J,removed_heat_J=removed_J,stored_heat_change_J=capacity_J_K*(temperature-initial_C),
        balance_residual_J=input_J-removed_J-capacity_J_K*(temperature-initial_C),
        active_cooling_control='Declared constant capacity; thermostat and actual hot-performance curve not modelled',physical_accepted=False)
