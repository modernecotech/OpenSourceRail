"""Nonoverlapping quantity/process budgets under one declared pilot service.

All rates are explicit research allowances. Existing civil geometry quantities
are reused; its earlier installed budget or structural loads are not inherited.
"""
from math import ceil,fsum
from copy import deepcopy
import json
from pathlib import Path
from engineering.station_rail.common import identity,digest
from . import ROOT,FLAGS
CASES=('low','base','high')
POLICY='engineering/station_pair/cost-policy.json'
CIVIL='docs/design-engine/viaduct-backends/summary.json'


def evaluate(variant,journey,bundle,reconciliation,brief,*,civil_case='reference_box--reference',root=ROOT):
    if (variant['body_candidate_id']!=bundle['candidate_id'] or reconciliation['source_bundle_id']!=bundle['bundle_id']
        or reconciliation['candidate_id']!=bundle['candidate_id'] or variant['body_bundle_id']!=bundle['bundle_id']
        or reconciliation['evaluation_id']!=identity({k:v for k,v in reconciliation.items() if k!='evaluation_id'})
        or variant['candidate_id']!=identity(variant['physical_definition'])):
        raise ValueError('Costs require the exact same vehicle/mass candidate')
    if journey is not None and (journey['candidate_id']!=variant['candidate_id']
        or journey['evaluation_id']!=identity({k:v for k,v in journey.items() if k!='evaluation_id'})):
        raise ValueError('Costs cannot inherit another journey')
    root=Path(root);p=json.loads((root/POLICY).read_bytes())
    civil=json.loads((root/CIVIL).read_bytes());beam=next(r for r in civil['rows'] if r['case_id']==civil_case)
    if beam['family'] not in ('reference_box','folded_plate') or p['concrete_density_kg_m3']!=2500:
        raise ValueError('This quantity bridge supports only the canonical 2500 kg/m3 all-concrete cases')
    if variant['physical_definition'].get('civil_geometry_id')!=beam['component_geometry_id']:
        raise ValueError('Civil cost geometry differs from the canonical system candidate')
    distance=variant['physical_definition']['station_spacing_m'];spans=ceil(distance/20);beams=2*spans
    headway=max(h for h in brief['headway_options_s'] if h<=brief['maximum_wait_s']
        and brief['normal_people']*3600/h*brief['planning_occupancy']>=brief['peak_demand_pphpd'])
    # Held architectures retain a declared bounded runtime budget, not a fabricated successful trip.
    one_way=journey['elapsed_s'] if journey is not None and journey['normal_numerical_arrival'] else brief['maximum_pair_journey_s']
    cycle=2*(one_way+brief['dwell_s']+brief['terminal_turnaround_s'])
    active=ceil(cycle/headway);spares=max(1,ceil(active*brief['spare_fraction']));fleet=active+spares
    usage=dict(headway_s=headway,normal_places=brief['normal_people'],planning_occupancy=brief['planning_occupancy'],
        planning_capacity_pphpd=brief['normal_people']*3600/headway*brief['planning_occupancy'],
        peak_demand_pphpd=brief['peak_demand_pphpd'],one_way_s=one_way,cycle_s=cycle,
        active_trainsets=active,spare_trainsets=spares,total_trainsets=fleet,
        runtime_basis='computed conditional arrival' if journey is not None and journey['normal_numerical_arrival'] else 'explicit provisional maximum-runtime allowance',
        operating_timetable_verified=False,terminal_crossover_protection_verified=False)
    rows=[]
    def add(owner,quantity,unit,values,basis,confidence='calculated-with-allowances'):
        rows.append(dict(owner=owner,quantity=quantity,unit=unit,
            cost_usd={c:quantity*values[i] for i,c in enumerate(CASES)},basis=basis,confidence=confidence))
    volume=beam['nominal_stock_mass_kg']/p['concrete_density_kg_m3']
    labour_factor=p['folded_plate_labour_factor'] if beam['family']=='folded_plate' else 1.
    factory=[]
    for i in range(3):
        direct=volume*p['concrete_usd_m3'][i]+volume*p['rebar_kg_m3_hypothesis'][i]*p['rebar_usd_kg'][i]
        direct+=p['prestress_kg_per_beam_reserve'][i]*p['prestress_usd_kg'][i]
        direct+=p['reference_beam_labour_h'][i]*labour_factor*p['fabrication_loaded_wage_usd_h'][i]+p['beam_equipment_and_formwork_usd'][i]*labour_factor
        factory.append(direct*(1+p['beam_factory_QA_and_overhead_fraction'][i]))
    add('civil-beam-factory',beams,'20 m nominal beams',factory,'Native CAD nominal concrete quantity; new process/rate scenarios. Reinforcement and prestress are unverified reserves')
    add('shared-pier-foundation-bearings',spans+1,'two-track support packages',p['pier_foundation_bearing_package_usd'],'Shared bents counted once, not once per beam. Ground design remains open','provisional-site-reserve')
    add('beam-transport-and-erection',beams,'beams',p['beam_transport_and_erection_usd'],'Rigging, crane selection/radius and temporary stability unverified')
    add('running-rails',4*distance*p['rail_kg_per_m'],'kg',p['rail_usd_kg'],'Two tracks, two rails each; source rail mass class retained')
    add('running-rail-fastenings',ceil(4*distance/p['fastening_pitch_m']),'sets',p['fastening_set_usd'],'Explicit planning pitch; anchor/civil interface requires design')
    add('station-civil-accessibility',2,'stations',p['station_civil_accessibility_usd'],'Platforms, access, lifts, egress and enclosure budget; no duplicated launch equipment','provisional-site-reserve')
    add('station-common-grid-feed',2,'feeds',p['station_common_grid_feed_usd'],'Grid connection/transformer allowance; drive/VFD local panels in propulsion scope')
    add('station-hotel-battery-chargers',2,'independent-car charging installations',p['station_hotel_charger_usd'],'Positive station charger allowance; actual installed charging hardware/map remains unselected')
    add('signalling-protection-turnbacks',1,'pilot system',p['signals_communications_protection_turnbacks_usd'],'Protected controls, communications and terminal interfaces; no operating authority')
    add('depot-tools-utilities',1,'pilot facility',p['depot_tools_utilities_usd'],'Maintenance facilities distinct from optional production factory')
    vehicle=[]
    for i,c in enumerate(CASES):
        direct=bundle['direct_parts_process_usd']['known_leaf_subtotal'][c]
        reserve=brief['unlocated_installation_reserve_kg'][c]*p['uncatalogued_installation_usd_per_reserved_kg'][i]
        final=p['train_final_assembly_h'][i]*p['fabrication_loaded_wage_usd_h'][i]+p['train_whole_vehicle_test_allowance_usd'][i]
        extra=0.
        if variant['family']=='powered-wheel':
            extra=variant['geometry']['driven_axles']*p['powered_axle_drive_unit_usd'][i]+p['train_traction_inverter_collector_cooling_usd'][i]
        vehicle.append((direct+reserve+final+extra)*(1+p['train_delivery_and_spares_fraction'][i]))
    add('rolling-stock-delivered',fleet,'six-car trainsets',vehicle,'605-leaf direct allowances + named unknown-installation reserve + final assembly/testing + new architecture hardware + delivery. No parent masses or vehicle prices added')
    if variant['family']=='cable':
        n=variant['geometry']['motors'];L=variant['geometry']['powered_front_window_m'][1]
        hardware=[n*(p['motor_class_unit_usd'][i]+p['motor_VFD_protection_cooling_unit_usd'][i]+p['gear_drum_drive_unit_usd'][i])
            +variant['geometry']['parallel_ropes']*variant['geometry']['rope_loop_length_m_each']*p['rope_usd_m'][i]
            +p['grip_return_guard_hardware_per_station_usd'][i]+L*p['launcher_track_support_usd_m'][i] for i in range(3)]
        add('wayside-propulsion',2,'departure launch installations',hardware,'Independent material/process allowances for source-rating class; not ABB purchase quotation')
    elif variant['family']=='powered-wheel':
        add('wayside-propulsion',2*distance,'conductor track-m',p['conductor_supply_protection_usd_track_m'],'Onboard drives counted in vehicles; conductor hardware and protection counted here')
    else:
        hardware=list(p['unresolved_compact_LIM_station_budget_usd'])
        if variant['family']=='hybrid':hardware=[v+p['hybrid_mechanical_starter_station_budget_usd'][i] for i,v in enumerate(hardware)]
        add('wayside-propulsion',2,'station systems',hardware,'Positive explicit provisional equipment budget; force and detailed quantities remain unknown','provisional-equipment-reserve')
    direct={c:fsum(r['cost_usd'][c] for r in rows) for c in CASES}
    modes=[]
    for mode,setup in [('purchased-custom-outline',p['purchased_custom_vehicle_setup_usd']),('local-assembly-factory',p['local_assembly_factory_setup_usd'])]:
        cap={};life={};annual={};components={}
        for i,c in enumerate(CASES):
            engineering=(direct[c]+setup[i])*p['design_integration_verification_fraction'][i]
            subtotal=direct[c]+setup[i]+engineering;contingency=subtotal*p['contingency_fraction'][i]
            cap[c]=subtotal+contingency
            components[c]=dict(direct_accounts=direct[c],one_campaign_setup=setup[i],integration_verification=engineering,contingency=contingency)
            departures=2*3600/headway*brief['operation_hours_day']*brief['operation_days_year']
            reset_J=0.
            if variant['family']=='cable':
                reset_J=(.5*variant['external_mass_kg']*5.**2+variant['external_resistance_N']*variant['geometry']['powered_front_window_m'][1])/variant['electrical_efficiency_hypothesis']
            hotel_j=None if journey is None or not journey['normal_numerical_arrival'] else journey['auxiliary_energy_j']+journey['auxiliary_energy_j']/journey['journey_plus_dwell_s']*brief['terminal_turnaround_s']
            trip_kwh=None if hotel_j is None else (journey['grid_energy_j']+reset_J+hotel_j/brief['hotel_charge_efficiency_hypothesis'])/3.6e6
            energy=None if trip_kwh is None else (departures*trip_kwh+2*p['station_auxiliary_W_each'][i]/1000*brief['operation_hours_day']*brief['operation_days_year'])*brief['tariff_usd_kwh'][c]
            maintenance=vehicle[i]*fleet*p['vehicle_annual_maintenance_fraction'][i]
            maintenance+=fsum(r['cost_usd'][c] for r in rows if r['owner'].startswith(('civil','shared','running')))*p['civil_annual_maintenance_fraction'][i]
            maintenance+=next(r['cost_usd'][c] for r in rows if r['owner']=='wayside-propulsion')*p['propulsion_annual_maintenance_fraction'][i]
            staff=p['paid_operating_maintenance_staff'][i]*p['loaded_staff_usd_year'][i]
            annual[c]=dict(energy_usd=energy,maintenance_usd=maintenance,staff_usd=staff,complete_operating_cost=None if energy is None else energy+maintenance+staff)
            factor=fsum((1+brief['discount_rate'])**-y for y in range(1,brief['design_life_years']+1))
            renewal=vehicle[i]*fleet/(1+brief['discount_rate'])**p['vehicle_replacement_year']
            life[c]=None if energy is None else cap[c]+factor*(energy+maintenance+staff)+renewal
        modes.append(dict(method=mode,installed_capital_usd=cap,capital_components=components,
            capital_per_route_km_usd={c:cap[c]/(distance/1000) for c in CASES},annual_operating=annual,
            whole_life_NPV_usd=life,future_order_or_resale_credit=False,production_campaign_trainsets=fleet,
            comparison_scope='Setup allowance sensitivity; not demonstrated make-versus-buy productivity or supplier advantage'))
    value=dict(schema='osr-station-pair-cost/1',candidate_id=variant['candidate_id'],body_candidate_id=bundle['candidate_id'],
        body_bundle_id=bundle['bundle_id'],mass_evaluation_id=reconciliation['evaluation_id'],
        journey_evaluation_id=None if journey is None else journey.get('evaluation_id'),service=usage,
        civil_geometry_reference=dict(candidate_id=beam['candidate_id'],geometry_id=beam['component_geometry_id'],
            family=beam['family'],span_m=20.,nominal_stock_mass_kg=beam['nominal_stock_mass_kg'],
            numerical_load_case_inherited=False,new_axle_moving_loads_required=True,
            required_lifting_mass_base_kg=beam['nominal_stock_mass_kg']+volume*p['rebar_kg_m3_hypothesis'][1]+p['prestress_kg_per_beam_reserve'][1]+1500.,
            crane_capacity_at_actual_radius_known=False),
        accounts=rows,methods=modes,price_level='scenario allowances; not confidence quantiles or supplier offers',
        hotel_charging=dict(required_average_grid_power_W=None if journey is None or not journey['normal_numerical_arrival'] else (journey['auxiliary_energy_j']+journey['auxiliary_energy_j']/journey['journey_plus_dwell_s']*brief['terminal_turnaround_s'])/brief['dwell_s']/brief['hotel_charge_efficiency_hypothesis'],
            hotel_scope='Journey, dwell and terminal turn; assumed replenishment within dwell only. Spare/depot conditioning demand remains outside this subtotal',
            charging_efficiency_hypothesis=brief['hotel_charge_efficiency_hypothesis'],
            actual_charger_map_available=False,battery_state_and_charge_limits_verified=False),
        source_sha256={POLICY:digest(root/POLICY),CIVIL:digest(root/CIVIL),'engineering/station_pair/economics.py':digest(__file__)},
        remaining_scope=['Actual installed equipment and trim','Site/ground/utilities/land and detailed lift plan',
            'Actuator/inverter efficiencies and recurring thermal duty','Replacement of all remaining proxies with design or supplier evidence'],
        transactions_performed=False,procurement_ready=False,**FLAGS)
    value['evaluation_id']=identity(value);return value
