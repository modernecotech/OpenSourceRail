"""Reproducible primary development screens, without engineering release authority."""
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
import itertools
import json
import math
from pathlib import Path
import re
import tomllib

from . import manufacturing

ROOT = Path(__file__).resolve().parents[2]
POLICY = ROOT / 'lib/templates/infrastructure.toml'
INPUT = ROOT / 'ferrite-maglev-study.toml'
SPEC = ROOT / 'engineering/ferrite_maglev/data/requirements.json'
RELEASE_VERSION = tomllib.loads((ROOT/'Cargo.toml').read_text())['workspace']['package']['version']
FLAGS = dict(design_complete=False, physical_validation=False, manufacturing_release=False, physical_release=False)


def positive(value, name, *, zero=False):
    if type(value) not in (int, float) or not math.isfinite(value) or (value < 0 if zero else value <= 0):
        raise ValueError('finite ' + ('nonnegative ' if zero else 'positive ') + name + ' required')
    return value


def validate(c):
    if c['metadata']['schema'] != 'osr-ferrite-maglev-study/2' or c['metadata']['family'] != 'ferrite-pm-maglev-study':
        raise ValueError('explicit primary maglev schema/family required')
    for key in ('fabrication_release_allowed', 'operational_authorisation', 'electromagnetic_force_map_validated',
                'vehicle_mass_measured', 'civil_design_released', 'costs_are_supplier_quotes'):
        if c['metadata'].get(key) is not False:
            raise ValueError('unqualified study cannot assert ' + key)
    a = c['architecture']
    if a['primary_study_suspension'] != 'pm-biased-active-attraction-to-wide-horizontal-iron-faces':
        raise ValueError('alternative circuit requires a separately qualified adapter')
    if any(a.get(k) is not False for k in ('route_permanent_magnets', 'onboard_main_traction', 'interstation_continuous_powered_stator',
               'ferrite_as_primary_crash_or_tensile_structure', 'unpowered_all_axis_contactless_stability_claimed',
               'shared_magnetic_volume_demonstrated')):
        raise ValueError('unsupported architecture claim')
    if (a.get('route_powered_stator') is not True or a.get('station_zone_powered_stator') is not True
            or a.get('onboard_support_guidance_windings') is not True
            or a.get('interstation_powered_propulsion') is not True
            or a.get('located_booster_powered_stator') is not True
            or a.get('primary_costed_propulsion')!='station-and-located-booster-lsm-shared-vehicle-pm'):
        raise ValueError('fixed station/located booster traction and independent onboard support architecture required')
    strategy=c['operating_strategy']
    for name in ('urban_minimum_stop_spacing_m','urban_target_stop_spacing_m',
                 'suburban_minimum_stop_spacing_m','suburban_maximum_stop_spacing_m'):
        positive(strategy[name],name)
    if not (strategy['urban_minimum_stop_spacing_m'] <= strategy['urban_target_stop_spacing_m']
            < strategy['suburban_minimum_stop_spacing_m'] <= strategy['suburban_maximum_stop_spacing_m']):
        raise ValueError('ordered urban/suburban station spacing required')
    if (strategy.get('longer_leg_boosters_enabled') is not True
            or strategy.get('junction_operation')!='passenger-transfer-between-fixed-lines'
            or strategy.get('route_alignment')!='straight-fixed-lines-subject-to-site-feasibility'
            or strategy.get('short_interchange_spacing_policy')!='retain-and-flag-exception'
            or strategy.get('legacy_reference_role')!='retained-1000m-component-benchmark'):
        raise ValueError('explicit fixed-line spacing, transfer and retained benchmark policy required')
    if c['controls']['implementation_language'] != 'Rust' or c['controls']['preferred_host'] != 'off-the-shelf-SBC':
        raise ValueError('primary Rust/SBC architecture required')
    if c['controls']['target_timing_measured'] is not False or c['validation']['citywide_savings_released'] is not False:
        raise ValueError('physical timing/city acceptance requires an external evidence adapter')
    for group in ('vehicle', 'mass', 'magnets', 'power', 'civil'):
        for name, value in c[group].items():
            unresolved = name in {'protected_emergency_energy_kwh', 'passive_rail_kg_per_beam_m', 'vertical_curve_minimum_radius_m'} and isinstance(value,str) and value.startswith('TBD')
            if re.search(r'(_m|_kg|_kwh|_kw|_v|_hz|_seconds|_per_car|_fraction|_efficiency|_kg_m3|_m_s2|_kmh)$', name) and not isinstance(value, (list, dict)) and not unresolved:
                positive(value, group + '.' + name, zero=name in {'normal_soc_low'})
            if type(value) in (int, float):
                signed = 'coefficient' in name
                if signed:
                    if not math.isfinite(value): raise ValueError('finite coefficient required')
                else: positive(value, group + '.' + name, zero=name=='normal_soc_low')
    p = c['power']
    for name in ('normal_soc_low','normal_soc_high'):
        positive(p[name],name,zero=name=='normal_soc_low')
    for group,name in [('magnets','temperature_screen_c'),('magnets','aw0_to_aw2_movement_sensitivities_m'),
                       ('power','charger_candidates_kw_per_car'),('civil','span_sensitivity_m'),('civil','horizontal_radius_screens_m')]:
        values=c[group][name]
        if not isinstance(values,list) or not 1 <= len(values) <= 100:raise ValueError('bounded nonempty sensitivity list required')
        for value in values:
            if name=='temperature_screen_c':
                if type(value) not in (float,int) or not math.isfinite(value):raise ValueError('finite temperature required')
            else:positive(value,name)
    for group,name in [('vehicle','cars_per_train'),('vehicle','aw2_passengers_per_car'),('vehicle','aw3_passengers_per_car'),('magnets','screening_module_count_per_car')]:
        if type(c[group][name]) is not int or c[group][name] <= 0:raise ValueError('positive integer count required: '+name)
    for name in ('station_drive_efficiency', 'station_generating_efficiency', 'station_charger_efficiency_assumption', 'eol_capacity_fraction'):
        if type(p[name]) not in (int,float) or not math.isfinite(p[name]) or not 0 < p[name] <= 1: raise ValueError('efficiency/fraction outside (0,1]')
    if not 0 <= p['normal_soc_low'] < p['normal_soc_high'] <= 1:
        raise ValueError('bounded ordered SOC window required')
    if p['charger_effective_seconds'] > p['station_dwell_seconds']:
        raise ValueError('charging time exceeds dwell')
    masses = c['mass']
    keys = ('structural_body_floor_doors_glazing_interior', 'ferrite_base',
            'support_guidance_cores_windings_carriers_drives_sensors_cooling', 'capture_landing_emergency_braking',
            'services_battery_low_case_installed_kg', 'cabin_hvac_ducting', 'auxiliary_electrical_train_controls_wiring',
            'couplers_gangway_interfaces_solar', 'growth_reserve')
    if not math.isclose(sum(masses[k] for k in keys), masses['base_tare_low_storage_target_kg']):
        raise ValueError('mass allocation does not close')
    expected = masses['base_tare_low_storage_target_kg'] + (
        p['services_battery_kwh_per_car'] - p['services_battery_low_case_kwh_per_car']) * 1000 / p['installed_pack_specific_energy_wh_kg']
    if not math.isclose(expected, masses['matched_tare_target_kg']):
        raise ValueError('matched mass allocation differs')
    box = c['civil']['narrow_box_screen']
    calculated = section(box['outer_width_m'], box['outer_depth_m'], box['web_thickness_m'], box['flange_thickness_m'])
    for actual, expected in [('area_m2', 'derived_concrete_area_m2'), ('vertical_i_m4', 'derived_gross_vertical_i_m4'), ('lateral_i_m4', 'derived_gross_lateral_i_m4')]:
        if not math.isclose(calculated[actual], box[expected], rel_tol=1e-6):
            raise ValueError('derived section value is stale: '+expected)
    return c


def load():
    policy = tomllib.loads(POLICY.read_text())
    if policy['development']['primary_family'] != 'ferrite-pm-maglev-study':
        raise ValueError('primary architecture policy differs')
    if policy['development']['primary_input']!='ferrite-maglev-study.toml' or policy['development']['primary_runner']!='tools/automation/ferrite-maglev-study.py':
        raise ValueError('selected input/adapter differs from the installed primary adapter')
    if (ROOT/'VERSION').read_text().strip()!='0.5':raise ValueError('primary architecture version differs')
    if any(policy['release'].get(k) is not False for k in FLAGS):
        raise ValueError('primary study is not a release adapter')
    if (any(policy['objectives'].get(k) is not False for k in (
            'normal_running_rotating_traction_motors', 'normal_running_conventional_wheelsets', 'all_vehicle_moving_parts_eliminated'))
            or policy['objectives'].get('linear_electromagnetic_propulsion_required') is not True):
        raise ValueError('fixed-module running gear/linear propulsion policy differs')
    c = validate(tomllib.loads(INPUT.read_text()))
    if (policy['development'].get('propulsion_architecture')!='fixed-station-and-located-booster-lsm-with-passive-coast-sections'
            or policy['objectives'].get('onboard_main_traction') is not False
            or policy['objectives'].get('station_zones_powered') is not True
            or policy['objectives'].get('interstation_traction_powered') is not True
            or policy['objectives'].get('interstation_continuous_powered_stator') is not False
            or policy['objectives'].get('junction_operation')!=c['operating_strategy']['junction_operation']):
        raise ValueError('primary policy and fixed station/booster/transfer architecture differ')
    if any(policy['objectives'].get(k) is not False for k in ('walkway_removal_approved','concrete_only_magnetic_reaction_claimed')):
        raise ValueError('unqualified beam-only/evacuation claim in primary policy')
    from . import optimisation
    if policy['objectives']['target_elevated_mainline_fraction']!=optimisation.load()['route']['target_elevated_mainline_fraction']:
        raise ValueError('primary policy and elevated optimisation target differ')
    if policy['controls']['language']!=c['controls']['implementation_language'] or policy['controls']['preferred_host']!=c['controls']['preferred_host']:
        raise ValueError('primary control policy and input differ')
    if c['cost']['cost_input_file'] != manufacturing.INPUT.relative_to(ROOT).as_posix():
        raise ValueError('controlled process rate input required')
    from . import station_structure
    shared=station_structure.load();body=shared['body'];vehicle=shared['vehicle'];cv=shared['civil']
    if (c['mass']['structural_body_floor_doors_glazing_interior']!=body['cases']['central']['rounded_equipped_target_kg']
            or c['vehicle']['passenger_doors_per_side']!=body['doors_per_side']
            or c['mass']['ferrite_base']!=vehicle['ferrite_kg']
            or c['power']['services_battery_kwh_per_car']!=vehicle['services_battery_kwh']
            or c['civil']['narrow_box_screen']['web_thickness_m']!=cv['web_m']):
        raise ValueError('primary configuration and controlled body/civil target contract differ')
    costs = manufacturing.load()
    return policy, c, costs


def mass(c, ferrite, battery):
    p = c['power']; m = c['mass']; v = c['vehicle']
    tare = m['base_tare_low_storage_target_kg'] + ferrite-m['ferrite_base'] + (
        battery-p['services_battery_low_case_kwh_per_car'])*1000/p['installed_pack_specific_energy_wh_kg']
    return dict(tare_kg=tare, aw2_kg=tare+v['aw2_passengers_per_car']*v['passenger_mass_screen_kg'],
                aw3_kg=tare+v['aw3_passengers_per_car']*v['passenger_mass_screen_kg'],
                battery_mass_kg=battery*1000/p['installed_pack_specific_energy_wh_kg'],
                eol_window_kwh=battery*p['eol_capacity_fraction']*(p['normal_soc_high']-p['normal_soc_low']),
                cg_m=None, inertia_kg_m2=None, actual_mass_verified=False)


def cost_case(c, costs, scenario, ferrite, battery, *, hardware_target=None, cars=None):
    vehicle=manufacturing.vehicle(c,costs,ferrite,battery,cars=cars,hardware_target=hardware_target,scenario=scenario)
    civil=manufacturing.civil(c,costs,scenario=scenario)
    rows={r['id']:r['amount_usd'] for r in civil['rows']}
    return dict(scenario=scenario,cars=vehicle['cars'],ferrite_kg_car=ferrite,battery_kwh_car=battery,
        hardware_target_usd_train=hardware_target,
        magnetic_bundle_usd_train=next(r['amount_usd'] for r in vehicle['rows'] if r['id']=='magnetic-modules'),
        raw_ferrite_usd_train=next(r['amount_usd'] for r in vehicle['rows'] if r['id']=='ferrite'),
        train_usd=vehicle['total_allowance_usd'],vehicle_bill=vehicle,
        civil_usd_dual_km=civil['total_allowance_usd_dual_km'],civil_rows_usd_dual_km=rows,civil_bill=civil,
        pilot_subtotal_usd=None,pilot_usd=None,city_total_usd=None,epc_included=False,costs_are_quotes=False,
        scope='Independent maglev formation and ordinary dual-direction elevated guideway allowances; pilot/NRE and complete programme unpriced',
        limits='Quantity/process assumptions; site ground, force maps, manufacturing cycle times, prices and origins require qualification')


def section(width, depth, web, flange):
    for name, v in [('width', width), ('depth', depth), ('web', web), ('flange', flange)]: positive(v, name)
    wi, hi = width-2*web, depth-2*flange
    if wi <= 0 or hi <= 0: raise ValueError('hollow box has no positive inner void')
    return dict(area_m2=width*depth-wi*hi, vertical_i_m4=(width*depth**3-wi*hi**3)/12,
                lateral_i_m4=(depth*width**3-hi*wi**3)/12)


def sagitta(length, radius):
    positive(length, 'chord'); positive(radius, 'radius')
    if length >= 2*radius: raise ValueError('chord exceeds circle diameter')
    # Rationalised expression avoids cancellation on very large radii.
    return (length/2)**2 / (radius+math.sqrt(radius**2-(length/2)**2))


def civil_case(c, width, depth, span, *, walkway_area_m2=.12):
    positive(walkway_area_m2,'walkway material area',zero=True)
    b = c['civil']['narrow_box_screen']; s = section(width, depth, b['web_thickness_m'], b['flange_thickness_m'])
    g, rho, young = 9.81, 2500, b['gross_uncracked_concrete_e_pa']
    vehicle = mass(c, c['mass']['ferrite_base'], c['power']['services_battery_kwh_per_car'])
    from .geometry import guideway_quantities,MATERIALS
    quantities=guideway_quantities(span,width=width,depth=depth,web=b['web_thickness_m'],flange=b['flange_thickness_m'])
    rho=MATERIALS['concrete']
    dead = quantities['total_line_mass_kg_m']+walkway_area_m2*rho
    live = vehicle['aw3_kg']/c['vehicle']['nominal_car_length_m'];w=(dead+live)*g
    s.update(magnetic_quantities=quantities,width_m=width, depth_m=depth, span_m=span, bare_beam_mass_kg=quantities['beam_concrete_mass_kg'],
             listed_concrete_m3_dual_km=(quantities['beam_concrete_line_mass_kg_m']/rho+walkway_area_m2)*2000,
             shared_piers_per_route_km=1000/span, dead_line_mass_kg_m=dead, vehicle_line_mass_kg_m=live,
             total_moment_nm=w*span**2/8, total_elastic_deflection_m=5*w*span**4/(384*young*s['vertical_i_m4']),
             section_strength_accepted=None, lateral_torsional_accepted=None, relative_gap_accepted=None,
             scope='Gross uncracked simply supported UDL screen; excludes prestress, local details, rebar, brackets and coupled dynamics')
    return s


def geometry(c):
    m = c['magnets'];length=m['seed_strip_length_m'];area=m['seed_strips']*length*m['seed_strip_width_m']
    volume=area*m['seed_strip_thickness_m'];load=mass(c,c['mass']['ferrite_base'],c['power']['services_battery_kwh_per_car'])['aw3_kg']*9.81
    return dict(seed_ferrite_mass_kg=volume*m['reference_density_kg_m3'], seed_area_m2=area,
                seed_blocks=volume/m['seed_block_edge_m']**3,
                field_demand_static_t=math.sqrt(2*4*math.pi*1e-7*load/area),
                field_demand_1p3_t=math.sqrt(2*4*math.pi*1e-7*load*m['initial_dynamic_lift_screen_multiplier']/area),
                actual_field_force_map=None, shared_lift_guidance_propulsion_allocation=None,
                maxwell_pressure_is_force_prediction=False,
                curves=[dict(radius_m=r, lateral_sagitta_m=sagitta(length,r),
                             face_width_before_margins_m=m['seed_strip_width_m']+2*sagitta(length,r),
                             vertical_gap_consumed_by_horizontal_sagitta_m=0,
                             complete_swept_envelope_accepted=False) for r in c['civil']['horizontal_radius_screens_m']],
                temperature=[dict(temperature_c=t, remanence_sensitivity_t=m['remanence_20c_screen_t']*(
                    1+m['remanence_temp_coefficient_sensitivity_per_k']*(t-20)),
                    ideal_unsaturated_force_ratio=(1+m['remanence_temp_coefficient_sensitivity_per_k']*(t-20))**2)
                    for t in m['temperature_screen_c']],
                stiffness_n_m=[dict(movement_m=d, aw0_aw2_required_n_m=c['vehicle']['aw2_passengers_per_car']*
                                   c['vehicle']['passenger_mass_screen_kg']*9.81/d) for d in m['aw0_to_aw2_movement_sensitivities_m']])


def station_zone_screen(c, trajectory, *, cars=None,winding_start_m=None,winding_end_m=None):
    """Check fixed-zone force against actual band intersections, without sizing it.

    The longitudinal plant scales per-car resistance and mass linearly, so its
    acceleration/position history is reusable for the declared full consist.
    Force density remains an unvalidated assumption; this check rejects known
    geometric impossibility without crediting unlocated intermediate stations.
    """
    from . import station,configuration
    import numpy as np
    count=c['vehicle']['cars_per_train'] if cars is None else cars
    if type(count) is not int or not 1<=count<=12:raise ValueError('bounded station-duty consist required')
    a=station.load();v=a['vehicle'];s=a['station']
    if (winding_start_m is None)!=(winding_end_m is None):raise ValueError('both winding endpoints required')
    if winding_start_m is not None:
        if any(type(x) not in (int,float) or not math.isfinite(x) or abs(x)>1000 for x in (winding_start_m,winding_end_m)) or winding_end_m-winding_start_m<10:
            raise ValueError('finite bounded ordered winding endpoints required')
        s['winding_start_m']=winding_start_m;s['winding_end_m']=winding_end_m
    cfg=configuration.selected(c,city='station-duty',cars=count)
    length=cfg.formation.assumed_overall_length_m;body=cfg.formation.body_length_m
    band=v['magnetic_band_m_per_car'];pitch=body+cfg.formation.coupling_gap_assumption_m
    offset=(body-band)/2
    if offset<0:raise ValueError('magnetic band exceeds the body length')
    bands=np.array([[-offset-band-i*pitch,-offset-i*pitch] for i in range(count)])
    density=s['equivalent_envelope_force_n_m']*length/(band*count)
    result=dict(cars=count,train_length_assumption_m=length,
        magnetic_bands_relative_to_front_m=bands.tolist(),
        winding_start_m=s['winding_start_m'],winding_end_m=s['winding_end_m'],
        equivalent_envelope_force_density_n_m=s['equivalent_envelope_force_n_m'],
        active_band_force_density_n_m=density,force_map_validated=False,
        phase_registration_validated=False,engineering_accepted=False,**FLAGS)
    if not trajectory.get('study_pass'):
        return dict(result,study_pass=False,status='hold',reason='No feasible pure longitudinal trajectory')
    values=dict(base=result,mass=trajectory['inputs']['car_mass_kg']*count,
        grade=trajectory['inputs']['grade'],resistance=trajectory['resistance'],
        segments=trajectory['segments'],braking_distance_m=trajectory['phases']['braking']['distance_m'],
        sample_interval_s=a['motion']['overlap_sample_interval_s'])
    return deepcopy(_station_zone_cached(json.dumps(values,sort_keys=True,allow_nan=False)))


@lru_cache(maxsize=4096)
def _station_zone_cached(canonical):
    """Immutable numerical/geometric keys; no sizing solver or shared results."""
    from . import station
    import numpy as np
    values=json.loads(canonical);result=values['base'];count=result['cars'];mass=values['mass']
    bands=np.array(result['magnetic_bands_relative_to_front_m']);density=result['active_band_force_density_n_m']
    constant=values['resistance']['constant_n_per_car']*count+mass*9.81*values['grade']
    quadratic=values['resistance']['quadratic_n_per_car_per_m_s_squared']*count
    margins={};zero_overlap=False;sample_count=0
    for name in ('launch','braking'):
        _,positions,velocity,acceleration=station._phase_samples(
            values['segments'][name],values['sample_interval_s'])
        if name=='braking':positions=positions-values['braking_distance_m']
        force=np.abs(mass*acceleration+constant+quadratic*velocity**2)
        overlap=station._overlap(positions,bands,result['winding_start_m'],result['winding_end_m'])
        active=force>1.
        margins[name]=float(np.min(overlap[active]*density/force[active])-1.) if np.any(active) else None
        zero_overlap=zero_overlap or bool(np.any((overlap<1e-9)&active))
        sample_count+=len(positions)
    passed=all(value is not None and value>=-1e-7 for value in margins.values())
    reason=None if passed else ('Fixed station winding has zero magnetic overlap while nonzero motor force is required'
        if zero_overlap else 'Fixed station winding cannot supply the sampled force demand at the assumed overlap force density')
    return dict(result,study_pass=passed,status='conditional-study-pass' if passed else 'hold',reason=reason,
        minimum_force_reserve_fraction=margins,zero_overlap_with_nonzero_force=zero_overlap,
        sample_interval_max_s=values['sample_interval_s'],samples_evaluated=sample_count,
        intermediate_station_credit_applied=False,
        scope='Fixed installed winding and exact rectangular bands; no current/voltage/thermal, phase or fault qualification')


def cycle(c, mass_kg, *, hot=False, speed_kmh=80, regen=True,cars=None):
    """Station launch/coast/receive demand and a separate services-only battery.

    Arbitrary city distances use an explicit runtime allocation, not a qualified
    timetable. Infeasible longitudinal cases remain held rather than restoring
    powered cruise. Station braking energy is never credited to the vehicle pack.
    """
    from . import station
    p=c['power'];v=c['vehicle'];positive(mass_kg,'mass');positive(speed_kmh,'speed')
    distance=p['station_spacing_study_m'];positive(distance,'distance')
    runtime=max(v['runtime_reference_seconds']*distance/1000,
                1.5*distance/(speed_kmh/3.6),2*math.sqrt(distance/v['maximum_initial_acceleration_m_s2'])+6.)
    runtime=round(max(20.,runtime),4)
    try:
        t=station.trajectory(distance_m=distance,runtime_s=runtime,car_mass_kg=mass_kg,cars=1,
            acceleration=v['maximum_initial_acceleration_m_s2'],deceleration=v['service_deceleration_study_m_s2'],
            jerk=v['jerk_study_m_s3'],speed_limit_kmh=speed_kmh,record_trace=False,
            motoring_efficiency=p['station_drive_efficiency'],generating_efficiency=p['station_generating_efficiency'],
            resistance_constant_n_per_car=p['passive_rail_drag_study_n_per_car'],
            resistance_quadratic_n_per_car=.5*p['air_density_study_kg_m3']*p['drag_area_study_m2_per_car'])
    except ValueError as exc:
        t=dict(study_pass=False,reason='outside bounded station trajectory domain: '+str(exc))
    hotel=p['hot_hotel_kw_per_car' if hot else 'normal_hotel_kw_per_car']
    dwell=p['station_dwell_seconds'];connected=p['charger_effective_seconds'];duration=runtime+dwell
    services=hotel*duration/3600;replacement=hotel*(runtime+dwell-connected)/3600
    balanced=hotel+replacement*3600/connected
    pure_pass=t['study_pass'];zone=station_zone_screen(c,t,cars=cars)
    passed=pure_pass and zone['study_pass']
    return dict(mass_kg=mass_kg,hot=hot,requested_speed_kmh=speed_kmh,
        achieved_speed_kmh=t['peak_speed_kmh'] if passed else None,
        regeneration_available=regen,regeneration_destination='station DC/resistor; no vehicle-pack credit',
        moving_seconds=runtime,cycle_seconds=duration,commercial_speed_kmh=distance/duration*3.6,
        propulsion_dc_kwh=0.,recovered_dc_kwh=0.,services_kwh=services,cycle_kwh=services,
        station_traction_input_kwh=t['station_positive_input_kwh'] if passed else None,
        station_brake_dc_kwh=t['receiving_brake_dc_kwh'] if passed else None,
        station_traction_peak_kw=t['peak_traction_input_kw'] if passed else None,
        services_battery_moving_kwh=hotel*runtime/3600,
        battery_replacement_kwh=replacement,balanced_charger_kw=balanced/p['station_charger_efficiency_assumption'],
        balanced_dc_interface_kw=balanced,charger_efficiency_assumption=p['station_charger_efficiency_assumption'],taper_start_kmh=None,
        charger_balance_kwh={str(int(kw)):(kw*p['station_charger_efficiency_assumption']-hotel)*connected/3600-replacement for kw in p['charger_candidates_kw_per_car']},
        pure_trajectory_screen_pass=pure_pass,station_zone_screen_pass=zone['study_pass'],station_zone=zone,
        kinematic_screen_pass=passed,kinematic_hold=None if passed else (zone['reason'] if pure_pass else t.get('reason','station coast infeasible')),
        runtime_basis='max(configured reference runtime/km, speed-limited1.5x travel time, jerk/acceleration planning floor); infeasible routes remain held',
        actual_motor_loss_map=None,route_acceptance=False,
        exclusions=['measured force/current/voltage/thermal and six-car phase maps','grade/curves/wind',
                    'qualified timetable and receiver-fault stopping','charge taper and protected reserve qualification'])


def localisation(rows):
    """Local value added, not address of final assembly or elimination of bought scope."""
    total=0;local=0;missing=[]
    for row in rows:
        cost=positive(row['cost_usd'], 'row cost', zero=True);total+=cost
        imported=row.get('imported_input_usd')
        if imported is None:missing.append(row['id']);continue
        positive(imported, 'imported input', zero=True)
        if imported>cost:raise ValueError('imported content exceeds row value')
        local+=cost-imported
    return dict(total_value_usd=total, known_local_value_added_usd=local,
                local_fraction=local/total if total and not missing else None, missing_origin_cost_rows=missing)


def requirement_register():
    import json
    data=json.loads(SPEC.read_text())
    records=data['requirements']
    if len({r['id'] for r in records})!=len(records):raise ValueError('duplicate requirement')
    return deepcopy(records)


def sources(*,include_generated=True):
    paths=[ROOT/'OpenSourceRail maglev station concept.png',ROOT/'Vertical spiral escape chute concept.png',POLICY,INPUT,SPEC,manufacturing.INPUT,ROOT/'VERSION',ROOT/'OpenSourceRail_Station_Powered_Maglev_Design_Specification.docx',ROOT/'Cargo.toml',ROOT/'Cargo.lock',ROOT/'osr',ROOT/'package.json',ROOT/'package-lock.json',
           ROOT/'tools/automation/ferrite-maglev-study.py',ROOT/'engineering/analysis/tests/test_ferrite_maglev.py']
    paths+=list(Path(__file__).parent.glob('*.py'))
    paths+=list(Path(__file__).parent.glob('*.txt'))
    paths+=list(Path(__file__).parent.glob('*.toml'))
    paths+=list((Path(__file__).parent/'data').glob('*.json'))
    paths+=list((ROOT/'engineering/analysis/tests').glob('test_ferrite_maglev_*.py'))
    from . import transition,cities
    extra=transition.sources()
    paths += [ROOT/name for name in extra]
    paths += cities.source_paths()
    index=Path(__file__).parent/'city-index.json'
    if index.exists():paths.append(index)
    paths+=list((ROOT/'crates/osr-maglev-control').rglob('*.rs'))+[ROOT/'crates/osr-maglev-control/Cargo.toml']
    paths += [ROOT/name for name in ('tools/automation/maglev-workbench.py', 'install.sh',
        'tools/automation/generate-public-overview.py', 'tools/automation/build-doc-book.py',
        'docs/workbench/maglev/index.html', 'docs/workbench/maglev/app.js', 'docs/workbench/maglev/pilot.js', 'docs/workbench/maglev/app.css')]
    from . import navigation
    paths += navigation.source_paths()
    from . import pilot_lifecycle,pilot_assurance
    paths += pilot_lifecycle.source_paths()+pilot_assurance.source_paths()
    def included(path):
        name=path.relative_to(ROOT).as_posix()
        return include_generated or not (
            name.startswith('docs/design-engine/ferrite-maglev/') or '/engineering/maglev/' in name
            or name.startswith('engineering/ferrite_maglev/city-index.')
            or (name.startswith('cities/catalogue/') and name.endswith('/README.md')))
    return {p.relative_to(ROOT).as_posix():sha256(p.read_bytes()).hexdigest() for p in sorted(set(paths)) if included(p)}


def retained_system_details():
    """Small verified packet interfaces; full traces stay in bounded archives."""
    import gzip,json
    from . import moving_train,system_campaign,closure
    moving=moving_train.read_selected()
    with gzip.open(moving_train.OUTPUT/'result.json.gz','rb') as stream:run=json.load(stream)
    moving.update(packet_path=moving_train.OUTPUT.relative_to(ROOT).as_posix(),
        manifest_sha256=sha256((moving_train.OUTPUT/'manifest.json').read_bytes()).hexdigest(),
        numerical_controls=run['numerical_controls'],completed_moving_steps=run['moving_run']['completed_moving_steps'],
        planned_moving_steps=run['moving_run']['planned_moving_steps'])
    closure.verify()
    with gzip.open(closure.OUTPUT/'dossier.json.gz','rb') as stream:dossier=json.load(stream)
    details=dict(packet_path=closure.OUTPUT.relative_to(ROOT).as_posix(),manifest_sha256=sha256((closure.OUTPUT/'manifest.json').read_bytes()).hexdigest(),
        requirement_count=dossier['closure']['requirement_count'],system_count=dossier['closure']['system_count'],
        detail_part_count=len(closure.definition()['parts']),accepted_requirements=0,
        primary_frame_families=dossier['primary_frame_families'],body_interfaces=dossier['body_interfaces'],
        civil_stages=dossier['civil_stages'],foundation_cost_delta=dossier['foundation_cost_delta'],
        emergency_and_curve_load_path=dossier['emergency_and_curve_load_path'],complete_manufactured_system=False,**FLAGS)
    return moving,system_campaign.read_summary(),details


def build():
    from . import transition,coupled,optimisation,evacuation,system_development,requirements,configuration
    from . import corridor,booster_kit,booster_native
    from . import geometry as native_geometry
    policy,c,costs=load();cost_cases=[];energies=[];masses=[]
    moving_summary,campaign_summary,manufactured_summary=retained_system_details()
    for ferrite,battery in itertools.product((c['mass']['ferrite_base'],c['mass']['ferrite_sensitivity']),
                  (c['power']['services_battery_kwh_per_car'],c['power']['services_battery_low_case_kwh_per_car'])):
        m=mass(c,ferrite,battery);masses.append(dict(ferrite_kg_car=ferrite,battery_kwh_car=battery,**m))
        for scenario in costs['scenario_multipliers']:cost_cases.append(cost_case(c,costs,scenario,ferrite,battery))
        for load_case,hot in itertools.product(('aw2_kg','aw3_kg'),(False,True)):
            energies.append(dict(ferrite_kg_car=ferrite,battery_kwh_car=battery,load=load_case,**cycle(c,m[load_case],hot=hot)))
    targets=[cost_case(c,costs,'base',c['mass']['ferrite_base'],c['power']['services_battery_kwh_per_car'],hardware_target=h) for h in (90000,60000)]
    heaviest=max(m['aw3_kg'] for m in masses)
    adverse=[cycle(c,heaviest,hot=True,speed_kmh=speed,regen=regen) for speed,regen in ((80,False),(90,True),(90,False))]
    from . import station,station_structure,specification
    station_study=station.evaluate(c)
    station_study['evidence_role']='retained-1000m-component-benchmark; not verification of longer operational corridors'
    moving_summary['evidence_role']='retained-1000m-moving-benchmark; longer profiles have separate confirmation'
    campaign_summary['evidence_role']='retained-1000m-station-protection-benchmark; longer profiles have separate replay'
    corridor_summary=corridor.read_summary()
    booster_receipt=booster_kit.verify();booster_native_receipt=booster_native.verify()
    booster_summary=dict(packet_path=booster_kit.OUTPUT.relative_to(ROOT).as_posix(),
        manifest_sha256=sha256((booster_kit.OUTPUT/'manifest.json').read_bytes()).hexdigest(),
        native_packet_path=booster_native.OUTPUT.relative_to(ROOT).as_posix(),
        native_manifest_sha256=sha256((booster_native.OUTPUT/'manifest.json').read_bytes()).hexdigest(),
        native_part_count=booster_native_receipt['part_count'],
        source_current=bool(booster_receipt),passenger_station=False,physical_rescue_accepted=False,**FLAGS)
    grade_speed=None
    boxes=[civil_case(c,w,d,l) for w,d,l in itertools.product((.8,1.,1.2),optimisation.load()['civil']['depths_m'],c['civil']['span_sensitivity_m'])]
    gates=[dict(id='G'+str(i),name=name,state='open',accepted=False) for i,name in enumerate(c['validation']['gate_order'])]
    manufacturing=[dict(id=k,local_operation_candidate=True,cost_usd=None,imported_input_usd=None,
                        exact_material=None,routing_qualified=False) for k in c['industrialisation']['make_local_candidates']]
    packages=[
        ('requirements-profile','profile, source trace and initial quantitative screens','implemented-study',[]),
        ('magnetic-cad','dimensioned retained ferrite/core/coil/reaction-rail assemblies','capability-required',['requirements-profile']),
        ('magnetic-force-loss','nonlinear 2D/3D force, loss, thermal and demagnetisation maps','capability-required',['magnetic-cad']),
        ('vehicle-mass','component-level mass, CG, inertia and distribution','open',['magnetic-cad']),
        ('civil-kit','complete guideway, supports, foundations, walkways and erection stages','open',['magnetic-force-loss','vehicle-mass']),
        ('rust-support-control','24-module heave/roll/pitch allocation and fault/stop policy; hardware I/O and measured force maps remain open','implemented-subset',['requirements-profile']),
        ('coupled-dynamics','6-DOF, flexible body/guideway, mapped actuators and faults','capability-required',['magnetic-force-loss','rust-support-control','civil-kit']),
        ('sbc-io-timing','isolated hardware I/O, independent protection and measured host deadlines','hardware-evidence-required',['rust-support-control','magnetic-force-loss']),
        ('switch-free-city','equal-capacity formation, service, terminals, charging, depot and recovery','capability-required',['coupled-dynamics']),
        ('local-mbom-cost','priced origin-traced processes, tooling, yield, test and repair','supplier/process-evidence-required',['magnetic-cad','civil-kit']),
        ('rig-and-demonstrator','G1–G5 physical tests with preset limits and authenticated evidence','physical-evidence-required',['coupled-dynamics','sbc-io-timing','local-mbom-cost']),
    ]
    transition_register=transition.build(work_packages=[dict(id=p[0]) for p in packages])
    native=native_geometry.interface()
    capability_states={'magnetic-cad':'dimensioned-native-study',
        'magnetic-force-loss':'2D-numerical-hypothesis; 3D/material/loss validation open',
        'vehicle-mass':'partial-interface-material-ledger; whole-vehicle closure open',
        'civil-kit':'native detail, staged gross stress, prestress and conditional foundation proposals; physical ground/connection qualification open',
        'rust-support-control':'24-station five-mode study; actual actuation open',
        'coupled-dynamics':'moving six-car two-way beam/control numerical study with coupler indexing and adverse-stiffness/sensor confirmations; mapped magnetic/soil/flexible-body qualification open',
        'switch-free-city':'located operating stops, protected headways, curved terminal proposals and repeated loss-inclusive charging replay; site/guidance acceptance open',
        'local-mbom-cost':'quantity/process planning; supplier-validated production MBOM open'}
    catalogue_path=Path(__file__).parent/'city-index.json'
    import json
    catalogue=json.loads(catalogue_path.read_text()) if catalogue_path.is_file() else None
    return dict(schema='osr-primary-infrastructure-study/2',version=RELEASE_VERSION,family=policy['development']['primary_family'],
                architecture=policy['development']['primary_family'],configuration_revision=configuration.selected().revision,
                publication_role='primary-provisional-design',city='Baghdad six-car reference',
                formation=dict(baghdad_cars=6,nominal_body_length_m=102.),
                financial_scope='Partial fleet, ordinary/terminal civil, station/booster electrical and conditional foundation/recovery quantities; total installed programme and localisation unknown',
                selected_configuration=configuration.selected().record(),applicable_requirements=requirements.register(),
                primary_development=True,controller_state='migration and numerical studies implemented; physical design/acceptance closure remains open',
                policy=policy,inputs=c,process_cost_inputs=costs,mass_variants=masses,cost_cases=cost_cases,
                local_manufacture_cost_targets=targets,energy_cases=energies,adverse_energy_cases=adverse,
                station_powered=station_study,station_structure=station_structure.study(),
                operating_strategy=deepcopy(c['operating_strategy']),corridor_powered=corridor_summary,booster_recovery_kit=booster_summary,
                source_specification=specification.register(),moving_six_car=moving_summary,integrated_system=campaign_summary,manufactured_design=manufactured_summary,
                hot_5percent_grade_steady_speed_kmh=grade_speed,geometry=geometry(c),civil_section_candidates=boxes,
                localisation=dict(local_fraction=None,method='(finished value - imported inputs) / finished value; origin/cost evidence required',
                                  operations=manufacturing,bought_inputs=c['industrialisation']['bought_input_categories']),
                requirements=requirement_register(),gates=gates,
                transition_inventory=transition_register['inventory_counts'],transition_dispositions=transition_register['disposition_counts'],
                geometric_interface=dict(parts=len(native['parts']),modelled_material_mass_kg=native['modelled_material_mass_kg'],
                    magnet_budget=native['magnet_budget'],clearances=native['clearances'],holds=native['holds']),
                flexible_guideway_benchmark=coupled.static_benchmark(),
                whole_system_optimisation={k:v for k,v in optimisation.study(c,costs).items() if k not in {'candidates','beam_only_candidates'}},
                linked_system_development={k:v for k,v in system_development.study().items() if k!='support_cases'},
                onboard_evacuation={k:v for k,v in evacuation.study().items() if k not in {'geometry_envelopes','landing_cases','optimistic_flow_bounds'}},
                city_catalogue=dict(city_count=catalogue['city_count'],catalogue_complete=catalogue['catalogue_complete'],
                    planning_acceptance=False) if catalogue else dict(city_count=0,catalogue_complete=False),
                work_packages=[dict(id=i,scope=s,state=capability_states.get(i,state),depends_on=deps,accepted=False) for i,s,state,deps in packages],migration=dict(
                    maglev_city_compiler='implemented provisional formation/service/charging compiler; route/physical acceptance open',
                    native_magnetic_cad_and_force_solver='native geometry and 2D nonlinear-hypothesis backend; 3D/material/force validation open',
                    rust_control='24-module five-mode and flexible-guideway offline coupling; physical adapter/timing open'),**FLAGS)
