"""Reproducible primary development screens, without engineering release authority."""
from copy import deepcopy
from hashlib import sha256
import itertools
import math
from pathlib import Path
import re
import tomllib

from . import workbook

ROOT = Path(__file__).resolve().parents[2]
POLICY = ROOT / 'lib/templates/infrastructure.toml'
INPUT = ROOT / 'ferrite-maglev-study.toml'
SPEC = ROOT / 'OpenSourceRail_Ferrite_Maglev_Rework_Specification.md'
FLAGS = dict(design_complete=False, physical_validation=False, manufacturing_release=False, physical_release=False)


def positive(value, name, *, zero=False):
    if type(value) not in (int, float) or not math.isfinite(value) or (value < 0 if zero else value <= 0):
        raise ValueError('finite ' + ('nonnegative ' if zero else 'positive ') + name + ' required')
    return value


def validate(c):
    if c['metadata']['schema'] != 'osr-ferrite-maglev-study/1' or c['metadata']['family'] != 'ferrite-pm-maglev-study':
        raise ValueError('explicit primary maglev schema/family required')
    for key in ('fabrication_release_allowed', 'operational_authorisation', 'electromagnetic_force_map_validated',
                'vehicle_mass_measured', 'civil_design_released', 'costs_are_supplier_quotes'):
        if c['metadata'].get(key) is not False:
            raise ValueError('unqualified study cannot assert ' + key)
    a = c['architecture']
    if a['primary_study_suspension'] != 'pm-biased-active-attraction-to-wide-horizontal-iron-faces':
        raise ValueError('alternative circuit requires a separately qualified adapter')
    if any(a.get(k) is not False for k in ('route_powered_stator', 'route_permanent_magnets',
               'ferrite_as_primary_crash_or_tensile_structure', 'unpowered_all_axis_contactless_stability_claimed',
               'shared_magnetic_volume_demonstrated')):
        raise ValueError('unsupported architecture claim')
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
    for name in ('normal_drive_efficiency', 'hot_drive_efficiency', 'normal_regen_efficiency', 'hot_regen_efficiency', 'eol_capacity_fraction'):
        if not 0 < p[name] <= 1: raise ValueError('efficiency/fraction outside (0,1]')
    if not 0 <= p['normal_soc_low'] < p['normal_soc_high'] <= 1:
        raise ValueError('bounded ordered SOC window required')
    if p['charger_effective_seconds'] > p['station_dwell_seconds']:
        raise ValueError('charging time exceeds dwell')
    masses = c['mass']
    keys = ('structural_body_floor_doors_glazing_interior', 'ferrite_base',
            'cores_all_windings_carriers_drives_local_sensors_cooling', 'capture_landing_emergency_braking',
            'battery_150kwh_installed', 'cabin_hvac_ducting', 'auxiliary_electrical_train_controls_wiring',
            'couplers_gangway_interfaces_solar', 'growth_reserve')
    if not math.isclose(sum(masses[k] for k in keys), masses['base_tare_target_150kwh_3t_ferrite']):
        raise ValueError('mass allocation does not close')
    expected = masses['base_tare_target_150kwh_3t_ferrite'] + (
        p['gross_battery_matched_kwh_per_car'] - p['gross_battery_reduced_option_kwh_per_car']) * 1000 / p['installed_pack_specific_energy_wh_kg']
    if not math.isclose(expected, masses['matched_tare_target_225kwh_3t_ferrite']):
        raise ValueError('matched mass allocation differs')
    box = c['civil']['narrow_box_screen']
    calculated = section(box['outer_width_m'], box['outer_depth_m'], box['web_thickness_m'], box['flange_thickness_m'])
    for actual, expected in [('area_m2', 'derived_concrete_area_m2'), ('vertical_i_m4', 'derived_gross_vertical_i_m4'), ('lateral_i_m4', 'derived_gross_lateral_i_m4')]:
        if not math.isclose(calculated[actual], box[expected], rel_tol=1e-6):
            raise ValueError('derived section value is stale: '+expected)
    return c


def load():
    policy = tomllib.loads(POLICY.read_text())
    if policy['development']['primary_family'] != 'ferrite-pm-maglev-study' or policy['development']['automatic_legacy_fallback'] is not False:
        raise ValueError('primary architecture policy differs')
    if policy['development']['primary_input']!='ferrite-maglev-study.toml' or policy['development']['primary_runner']!='tools/automation/ferrite-maglev-study.py':
        raise ValueError('selected input/adapter differs from the installed primary adapter')
    if (ROOT/'VERSION').read_text().strip()!='0.5':raise ValueError('primary architecture version differs')
    if any(policy['release'].get(k) is not False for k in FLAGS):
        raise ValueError('primary study is not a release adapter')
    c = validate(tomllib.loads(INPUT.read_text()))
    if policy['controls']['language']!=c['controls']['implementation_language'] or policy['controls']['preferred_host']!=c['controls']['preferred_host']:
        raise ValueError('primary control policy and input differ')
    cost_path = ROOT / c['cost']['cost_input_file']
    if cost_path.resolve() != (ROOT / 'OpenSourceRail_Ferrite_Maglev_Cost_Model.xlsx').resolve():
        raise ValueError('controlled supplied workbook required')
    costs = workbook.read(cost_path)
    f = costs['fixed']; v = c['vehicle']; p = c['power']
    agreement = [(f['cars'], v['cars_per_train']), (f['aw2_passengers'], v['aw2_passengers_per_car']),
                 (f['aw3_passengers'], v['aw3_passengers_per_car']), (f['passenger_kg'], v['passenger_mass_screen_kg']),
                 (f['pack_wh_kg'], p['installed_pack_specific_energy_wh_kg']),
                 (f['base_ferrite_kg'], c['mass']['ferrite_base']),
                 (f['base_tare_kg'], c['mass']['base_tare_target_150kwh_3t_ferrite']),
                 (f['base_battery_kwh'], p['gross_battery_reduced_option_kwh_per_car']),
                 (f['battery_kwh_train'], p['gross_battery_matched_kwh_per_car']*v['cars_per_train'])]
    if any(a != b for a, b in agreement): raise ValueError('workbook and physical profile disagree')
    # Check the live comparator; never silently read a different old cost revision.
    import json
    ref = json.loads((ROOT / 'design/component-catalogue/catalog/buildable-trainset/trainset-build-cost.json').read_text())
    civil = tomllib.loads((ROOT / 'lib/templates/civil-cost-model.toml').read_text())
    if f['direct_usd'] != ref['direct_material_and_supplier_cost_usd'] or f['elevated_usd_km'] != civil['civil_usd_per_km']['elevated']:
        raise ValueError('comparator changed; reconcile supplied workbook before comparison')
    return policy, c, costs


def mass(c, ferrite, battery):
    p = c['power']; m = c['mass']; v = c['vehicle']
    tare = m['base_tare_target_150kwh_3t_ferrite'] + ferrite-m['ferrite_base'] + (
        battery-p['gross_battery_reduced_option_kwh_per_car'])*1000/p['installed_pack_specific_energy_wh_kg']
    return dict(tare_kg=tare, aw2_kg=tare+v['aw2_passengers_per_car']*v['passenger_mass_screen_kg'],
                aw3_kg=tare+v['aw3_passengers_per_car']*v['passenger_mass_screen_kg'],
                battery_mass_kg=battery*1000/p['installed_pack_specific_energy_wh_kg'],
                eol_window_kwh=battery*p['eol_capacity_fraction']*(p['normal_soc_high']-p['normal_soc_low']),
                cg_m=None, inertia_kg_m2=None, actual_mass_verified=False)


def cost_case(c, costs, scenario, ferrite, battery, *, hardware_target=None):
    f, s = costs['fixed'], costs['scenarios'][scenario]
    removed = sum(f[k] for k in ('remove_bogies_usd', 'remove_motors_usd', 'remove_gears_usd', 'remove_drives_usd', 'remove_cooling_usd'))
    bundle = sum(s[k] for k in ('iron_carriers_usd', 'windings_usd', 'drives_usd', 'sensing_usd', 'cooling_usd', 'finished_array_usd'))
    if hardware_target is not None:
        bundle = positive(hardware_target, 'magnetic hardware target')
    raw = ferrite*f['cars']*f['ferrite_usd_kg']
    credit = (f['battery_kwh_train']-battery*f['cars'])*f['battery_pack_usd_train']/f['battery_kwh_train']
    labour = s['integration_hours']*f['labour_usd_h']
    direct = f['direct_usd']-removed-credit+raw+bundle+s['capture_usd']
    ref = (f['direct_usd']+f['labour_hours']*f['labour_usd_h'])*(1+f['premium'])
    train = (direct+labour)*(1+f['premium'])
    old_structure = f['supplied_components_usd_km']-f['rail_supply_usd_km']
    rows = dict(structural_supply=old_structure*s['structure_factor'], conventional_rail=0,
                passive_rail_supply=s['rail_supply_usd_km'], walkway_brackets=s['brackets_usd_km'])
    for scope in ('erection', 'transport', 'temporary', 'installation', 'night', 'qa', 'relocation', 'traffic', 'supports'):
        rows[scope] = f[scope+'_usd_km']*s[scope+'_factor']
    pilot_subtotal = s['engineering_fte_years']*f['fte_usd_year']+sum(s[k] for k in (
        'independent_testing_usd', 'rigs_usd', 'fixtures_usd', 'first_article_usd', 'pilot_guideway_usd', 'site_power_recovery_usd'))
    return dict(scenario=scenario, ferrite_kg_car=ferrite, battery_kwh_car=battery,
                hardware_target_usd_train=hardware_target, magnetic_bundle_usd_train=bundle,
                raw_ferrite_usd_train=raw, removed_direct_usd_train=removed,
                battery_credit_usd_train=credit, train_usd=train, reference_train_usd=ref,
                train_saving_fraction=1-train/ref, civil_usd_dual_km=sum(rows.values()), civil_rows_usd_dual_km=rows,
                lower_rail_350_usd_beam_m_sensitivity=sum(rows.values())-s['rail_supply_usd_km']+350*f['beam_m_km'],
                pilot_subtotal_usd=pilot_subtotal, pilot_usd=pilot_subtotal*(1+s['pilot_reserve']),
                city_total_usd=None, epc_included=False, costs_are_quotes=False,
                scope='Repeat train and ordinary dual-direction elevated guideway separately; pilot includes first train once',
                limits='Target cases change bundle allowance only; hardware quantities, origin, costs and feasibility remain open')


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


def civil_case(c, width, depth, span):
    b = c['civil']['narrow_box_screen']; s = section(width, depth, b['web_thickness_m'], b['flange_thickness_m'])
    g, rho, young = 9.81, 2500, b['gross_uncracked_concrete_e_pa']
    vehicle = mass(c, c['mass']['ferrite_base'], c['power']['gross_battery_matched_kwh_per_car'])
    dead = (s['area_m2']+.12)*rho+b['magnetic_hardware_line_mass_screen_kg_m_per_direction']
    live = vehicle['aw3_kg']/c['vehicle']['nominal_car_length_m'];w=(dead+live)*g
    s.update(width_m=width, depth_m=depth, span_m=span, bare_beam_mass_kg=s['area_m2']*span*rho,
             listed_concrete_m3_dual_km=(s['area_m2']+.12)*2000,
             shared_piers_per_route_km=1000/span, dead_line_mass_kg_m=dead, vehicle_line_mass_kg_m=live,
             total_moment_nm=w*span**2/8, total_elastic_deflection_m=5*w*span**4/(384*young*s['vertical_i_m4']),
             section_strength_accepted=None, lateral_torsional_accepted=None, relative_gap_accepted=None,
             scope='Gross uncracked simply supported UDL screen; excludes prestress, local details, rebar, brackets and coupled dynamics')
    return s


def geometry(c):
    m = c['magnets'];length=m['seed_strip_length_m'];area=m['seed_strips']*length*m['seed_strip_width_m']
    volume=area*m['seed_strip_thickness_m'];load=mass(c,c['mass']['ferrite_base'],c['power']['gross_battery_matched_kwh_per_car'])['aw3_kg']*9.81
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


def cycle(c, mass_kg, *, hot=False, speed_kmh=80, regen=True):
    """Velocity-domain quadrature; fixed assumed efficiencies and level straight track."""
    from scipy.integrate import quad
    from scipy.optimize import brentq
    p, v = c['power'], c['vehicle'];positive(mass_kg, 'mass');positive(speed_kmh, 'speed')
    eta=p['hot_drive_efficiency' if hot else 'normal_drive_efficiency']
    er=p['hot_regen_efficiency' if hot else 'normal_regen_efficiency'] if regen else 0
    hotel=p['hot_hotel_kw_per_car' if hot else 'normal_hotel_kw_per_car']*1000
    cap=p['total_motoring_dc_cap_per_car_kw']*1000
    if cap <= hotel: raise ValueError('no propulsion power after services')
    amax=v['maximum_initial_acceleration_m_s2'];brake=v['service_deceleration_study_m_s2'];top=speed_kmh/3.6
    drag=lambda speed:p['passive_rail_drag_study_n_per_car']+.5*p['air_density_study_kg_m3']*p['drag_area_study_m2_per_car']*speed**2
    crossover=brentq(lambda speed:(mass_kg*amax+drag(speed))*speed/eta+hotel-cap,0, max(top,1)*100)
    equilibrium=brentq(lambda speed:drag(speed)*speed-(cap-hotel)*eta,0,max(top,1)*100)
    if top >= equilibrium: raise ValueError('requested speed exceeds steady power envelope')
    def accel(speed):return amax if speed <= crossover else ((cap-hotel)*eta/speed-drag(speed))/mass_kg
    def integral(fn,upper):return quad(fn,0,upper,epsabs=1e-7,points=[crossover] if crossover<upper else None)[0]
    distance=lambda speed:integral(lambda x:x/accel(x),speed)
    length=p['station_spacing_study_m']
    if distance(top)+top**2/(2*brake)>length:
        top=brentq(lambda speed:distance(speed)+speed**2/(2*brake)-length,1e-6,top)
    ta=integral(lambda x:1/accel(x),top);da=distance(top);db=top**2/(2*brake);dc=max(0,length-da-db)
    tc=dc/top;tb=top/brake;duration=ta+tc+tb+p['station_dwell_seconds']
    traction=integral(lambda x:(mass_kg*accel(x)+drag(x))*x/(eta*accel(x)),top)+drag(top)*dc/eta
    recovered=er*integral(lambda x:max(0,mass_kg*brake-drag(x))*x/brake,top)
    energy=(traction-recovered+hotel*duration)/3.6e6
    return dict(mass_kg=mass_kg, hot=hot, requested_speed_kmh=speed_kmh, achieved_speed_kmh=top*3.6,
                regeneration_available=regen, moving_seconds=duration-p['station_dwell_seconds'],
                cycle_seconds=duration, commercial_speed_kmh=length/duration*3.6,
                propulsion_dc_kwh=traction/3.6e6, recovered_dc_kwh=recovered/3.6e6,
                services_kwh=hotel*duration/3.6e6, cycle_kwh=energy,
                balanced_charger_kw=energy*3600/p['charger_effective_seconds'],
                taper_start_kmh=crossover*3.6, charger_balance_kwh={str(int(kw)):kw*p['charger_effective_seconds']/3600-energy for kw in p['charger_candidates_kw_per_car']},
                actual_motor_loss_map=None, route_acceptance=False,
                exclusions=['jerk', 'grid/charger and battery internal losses', 'charge taper', 'grade/curves/wind', 'protected emergency reserve'])


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
    text=SPEC.read_text();records={}
    for number,line in enumerate(text.splitlines(),1):
        match=re.match(r'(?:\| )?((?:SYS|MASS|GEO|PWR|CIV|OPS|CTL|MFG|MAG)-\d{3})(?:[.: ]| \|)',line)
        if match:
            identity=match.group(1)
            if identity in records:raise ValueError('duplicate requirement '+identity)
            records[identity]=dict(id=identity,source_line=number,requirement=line,state='open',accepted=False)
    return list(records.values())


def sources():
    paths=[POLICY,INPUT,SPEC,ROOT/'OpenSourceRail_Ferrite_Maglev_Cost_Model.xlsx',ROOT/'VERSION',ROOT/'Cargo.toml',ROOT/'Cargo.lock',ROOT/'osr',ROOT/'package.json',ROOT/'package-lock.json',
           ROOT/'tools/automation/ferrite-maglev-study.py',ROOT/'engineering/analysis/tests/test_ferrite_maglev.py',
           ROOT/'design/component-catalogue/catalog/buildable-trainset/trainset-build-cost.json',ROOT/'lib/templates/civil-cost-model.toml']
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
    return {p.relative_to(ROOT).as_posix():sha256(p.read_bytes()).hexdigest() for p in sorted(set(paths))}


def build():
    from . import transition,coupled
    from . import geometry as native_geometry
    policy,c,costs=load();cost_cases=[];energies=[];masses=[]
    for ferrite,battery in itertools.product((c['mass']['ferrite_base'],c['mass']['ferrite_sensitivity']),
                  (c['power']['gross_battery_matched_kwh_per_car'],c['power']['gross_battery_reduced_option_kwh_per_car'])):
        m=mass(c,ferrite,battery);masses.append(dict(ferrite_kg_car=ferrite,battery_kwh_car=battery,**m))
        for scenario in costs['scenarios']:cost_cases.append(cost_case(c,costs,scenario,ferrite,battery))
        for load_case,hot in itertools.product(('aw2_kg','aw3_kg'),(False,True)):
            energies.append(dict(ferrite_kg_car=ferrite,battery_kwh_car=battery,load=load_case,**cycle(c,m[load_case],hot=hot)))
    targets=[cost_case(c,costs,'base',c['mass']['ferrite_base'],c['power']['gross_battery_matched_kwh_per_car'],hardware_target=h) for h in (90000,60000)]
    heaviest=max(m['aw3_kg'] for m in masses)
    adverse=[cycle(c,heaviest,hot=True,speed_kmh=speed,regen=regen) for speed,regen in ((80,False),(90,True),(90,False))]
    g=9.81;grade=c['power']['minimum_service_grade_case_percent']/100
    from scipy.optimize import brentq
    force=heaviest*g*math.sin(math.atan(grade));p=c['power']
    grade_speed=brentq(lambda v:(force+p['passive_rail_drag_study_n_per_car']+.5*p['air_density_study_kg_m3']*p['drag_area_study_m2_per_car']*v*v)*v-
                      (p['total_motoring_dc_cap_per_car_kw']-p['hot_hotel_kw_per_car'])*1000*p['hot_drive_efficiency'],0,100)*3.6
    boxes=[civil_case(c,w,d,l) for w,d,l in itertools.product((.8,1.,1.2),(1.4,1.6,1.8),c['civil']['span_sensitivity_m'])]
    gates=[dict(id='G'+str(i),name=name,state='open',accepted=False) for i,name in enumerate(c['validation']['gate_order'])]
    manufacturing=[dict(id=k,local_operation_candidate=True,cost_usd=None,imported_input_usd=None,
                        exact_material=None,routing_qualified=False) for k in c['industrialisation']['make_local_candidates']]
    packages=[
        ('requirements-profile','profile, source trace and initial quantitative screens','implemented-study',[]),
        ('magnetic-cad','dimensioned retained ferrite/core/coil/reaction-rail assemblies','capability-required',['requirements-profile']),
        ('magnetic-force-loss','nonlinear 2D/3D force, loss, thermal and demagnetisation maps','capability-required',['magnetic-cad']),
        ('vehicle-mass','component-level mass, CG, inertia and distribution','open',['magnetic-cad']),
        ('civil-kit','complete guideway, supports, foundations, walkways and erection stages','open',['magnetic-force-loss','vehicle-mass']),
        ('rust-support-control','single-module study and fault/stop policy; multimodule allocation remains','implemented-subset',['requirements-profile']),
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
        'civil-kit':'dimensioned-bay study; reinforcement/ground/connections open',
        'rust-support-control':'24-station five-mode study; actual actuation open',
        'coupled-dynamics':'two-way rigid-car/vertical-beam numerical study; full dynamics open',
        'switch-free-city':'all-catalogue provisional compiler and charging replay',
        'local-mbom-cost':'complete migration obligations; priced production MBOM open'}
    catalogue_path=Path(__file__).parent/'city-index.json'
    import json
    catalogue=json.loads(catalogue_path.read_text()) if catalogue_path.is_file() else None
    return dict(schema='osr-primary-infrastructure-study/1',version='0.5.0',family=policy['development']['primary_family'],
                primary_development=True,controller_state='migration and numerical studies implemented; physical design/acceptance closure remains open',
                policy=policy,inputs=c,workbook_inputs=costs,mass_variants=masses,cost_cases=cost_cases,
                local_manufacture_cost_targets=targets,energy_cases=energies,adverse_energy_cases=adverse,
                hot_5percent_grade_steady_speed_kmh=grade_speed,geometry=geometry(c),civil_section_candidates=boxes,
                localisation=dict(local_fraction=None,method='(finished value - imported inputs) / finished value; origin/cost evidence required',
                                  operations=manufacturing,bought_inputs=c['industrialisation']['bought_input_categories']),
                requirements=requirement_register(),gates=gates,
                transition_inventory=transition_register['inventory_counts'],transition_dispositions=transition_register['disposition_counts'],
                geometric_interface=dict(parts=len(native['parts']),modelled_material_mass_kg=native['modelled_material_mass_kg'],
                    magnet_budget=native['magnet_budget'],clearances=native['clearances'],holds=native['holds']),
                flexible_guideway_benchmark=coupled.static_benchmark(),
                city_catalogue=dict(city_count=catalogue['city_count'],catalogue_complete=catalogue['catalogue_complete'],
                    planning_acceptance=False) if catalogue else dict(city_count=0,catalogue_complete=False),
                work_packages=[dict(id=i,scope=s,state=capability_states.get(i,state),depends_on=deps,accepted=False) for i,s,state,deps in packages],migration=dict(
                    legacy='wheel-rail-reference',legacy_baseline=policy['development']['legacy_baseline_commit'],
                    retained_city_outputs='v0.4 wheel/rail comparators; no maglev fleet, cost or acceptance transfer',
                    maglev_city_compiler='implemented provisional formation/service/charging compiler; route/physical acceptance open',
                    native_magnetic_cad_and_force_solver='native geometry and 2D nonlinear-hypothesis backend; 3D/material/force validation open',
                    rust_control='24-module five-mode and flexible-guideway offline coupling; physical adapter/timing open'),**FLAGS)
