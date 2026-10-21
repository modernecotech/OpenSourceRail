"""Calculated manufactured-detail dossier; qualified properties/acceptance stay open.

Strength factors, loads and material allowables below are explicit project study
assumptions. Algebraic margins are not railway code compliance, fatigue/crash
qualification, measured magnetic capacity or permission to manufacture.
"""
from copy import deepcopy
from hashlib import sha256
from functools import lru_cache
from pathlib import Path
import gzip
import json
import math
import os
import tomllib

from . import station_structure as structure, requirements, transition, configuration

ROOT = Path(__file__).resolve().parents[2]
INPUT = Path(__file__).with_suffix('.toml')
OBLIGATIONS = Path(__file__).with_name('closure-obligations.json')
OUTPUT = ROOT/'docs/design-engine/ferrite-maglev/manufactured-dossier'
FLAGS = dict(design_complete=False, physical_validation=False, manufacturing_release=False, physical_release=False)
FILES = {'dossier.json.gz', 'detail-definition.json', 'README.md'}
MAX_BYTES = 16*1024*1024
PACKETS = {'station-structure': 'manifest.json', 'station-native': 'manifest.json', 'native': 'manifest.json',
           'beam-only': 'manifest.json', 'station-powered': 'manifest.json', 'station-protocol': 'manifest.json',
           'system-development': 'manifest.json', 'baghdad-reference': 'manifest.json', 'coupled': 'receipt.json',
           'moving-train': 'manifest.json', 'system-campaign': 'manifest.json', 'booster-kit':'manifest.json', 'corridor':'manifest.json'}

RECEIPT_SCHEMAS = {
    'station-structure':'osr-station-structure-packet/1',
    'station-native':'osr-station-native-publication/1',
    'native':'osr-maglev-native-packet/1',
    'beam-only':'osr-beam-only-native/1',
    'station-powered':'osr-station-powered-study/1',
    'station-protocol':'osr-station-protocol-publication/1',
    'system-development':'osr-system-development-packet/1',
    'baghdad-reference':'osr-baghdad-reference-packet/1',
    'coupled':'osr-coupled-guideway-publication/1',
    'moving-train':'osr-moving-train-publication/1',
    'system-campaign':'osr-system-campaign-publication/1',
    'booster-kit':'osr-booster-kit-publication/1',
    'corridor':'osr-fixed-corridor-publication/1',
}


def _positive(value, name, zero=False):
    if type(value) not in (int, float) or not math.isfinite(value) or (value < 0 if zero else value <= 0):
        raise ValueError('finite positive '+name+' required')
    return value


def load():
    a = tomllib.loads(INPUT.read_text())
    if a['schema'] != 'osr-manufactured-design-dossier/1':
        raise ValueError('controlled detail dossier required')
    for group in ('materials', 'body', 'stator', 'civil', 'emergency', 'anchored_bay', 'coupler', 'frame_remainder', 'foundation_cost'):
        for name, value in a[group].items():
            if type(value) in (int, float):
                if name == 'top_eccentricity_m':
                    if not math.isfinite(value) or value >= 0: raise ValueError('top tendons must be above centroid')
                else: _positive(value, name, name == 'joint_additional_compliance_m_n')
    if a['materials']['material_properties_qualified'] is not False or a['emergency']['thermal_and_wear_capacity_qualified'] is not False:
        raise ValueError('no qualified material or brake adapter supplied')
    if a['anchored_bay']['foundation_selection_is_geotechnical_acceptance'] is not False:
        raise ValueError('ground evidence cannot be inferred from a pressure screen')
    for name in ('hot_strength_retention',):
        if not 0 < a['materials'][name] <= 1:
            raise ValueError('bounded retained strength required')
    for name in ('initial_stress_fraction', 'prestress_loss_fraction'):
        if not 0 < a['civil'][name] < 1:
            raise ValueError('bounded prestress fraction required')
    for group, names in [('body', ['stringers', 'floor_ribs', 'hardpoint_bolts', 'failed_cartridges', 'lap_faces']),
                         ('civil', ['prestress_bottom_strands', 'prestress_top_strands', 'proposed_end_debonded_bottom_strands', 'column_longitudinal_bars']),
                         ('emergency', ['units', 'two_direction_coincidence'])]:
        for name in names:
            if type(a[group][name]) is not int or a[group][name] < 1:
                raise ValueError('positive integer '+name+' required')
    if a['body']['failed_cartridges'] >= structure.load()['magnetic']['cartridges']:
        raise ValueError('no support cartridges remain')
    if a['civil']['proposed_end_debonded_bottom_strands'] >= a['civil']['prestress_bottom_strands']:
        raise ValueError('no bonded bottom tendons remain')
    for name in ('foundation_square_sides_m', 'brake_unit_offsets_from_car_front_m'):
        values = a['anchored_bay'][name]
        if not 1 <= len(values) <= 32 or values != sorted(set(values)):
            raise ValueError('ordered bounded distinct '+name+' required')
        for value in values:
            _positive(value, name)
    return a


def margin(capacity, demand):
    _positive(capacity, 'capacity'); _positive(demand, 'demand', True)
    return dict(capacity=capacity, demand=demand, capacity_over_demand=capacity/demand if demand else None,
                screen_pass=demand <= capacity, qualified_acceptance=False)


def _tube(width, depth, wall):
    return structure.section(width, depth, wall, wall)


def body_interfaces(*, load_multiplier=1., rib_span_m=None, car_mass_kg=None):
    _positive(load_multiplier, 'body load multiplier')
    a = load(); b = a['body']; m = a['materials']; body = structure.body(); cfg = structure.load()
    count = cfg['magnetic']['cartridges']; g = 9.81
    mass=body['aw3_target_kg'] if car_mass_kg is None else _positive(car_mass_kg,'per-car gross mass')
    interface_force = mass*g*b['normal_load_multiplier']*b['unequal_cartridge_multiplier']/(count-b['failed_cartridges'])*load_multiplier
    bolts = b['hardpoint_bolts']; shear_each = interface_force/bolts
    moment = interface_force*b['hardpoint_force_offset_m']
    tension_each = moment/(b['bolt_row_pitch_m']*(bolts/2))
    shear_cap = b['bolt_thread_area_m2']*m['bolt_shear_pa']
    tension_cap = b['bolt_thread_area_m2']*m['bolt_tension_pa']
    interaction = math.hypot(shear_each/shear_cap, tension_each/tension_cap)
    laminate_bearing = shear_each/(b['bolt_diameter_m']*b['hardpoint_solid_laminate_m'])
    pull_through = math.pi*b['washer_diameter_m']*b['hardpoint_solid_laminate_m']*m['gfrp_punching_shear_pa']*m['hot_strength_retention']
    carrier = _tube(b['carrier_box_width_m'], b['carrier_box_depth_m'], b['carrier_box_wall_m'])
    carrier_stress = moment/(carrier['vertical_inertia_m4']/(b['carrier_box_depth_m']/2))
    floor = next(row for row in body['panels'] if row['id'] == 'floor')
    face = floor['face_thickness_total_m']/2; core = floor['core_thickness_m']
    inertia = 2*(face**3/12+face*(core/2+face/2)**2)
    pressure = body['payload_floor_average_kpa']*1000*b['floor_load_multiplier']*load_multiplier
    floor_cases = []
    spans = [b['floor_span_without_rib_m'], b['floor_span_with_rib_m'] if rib_span_m is None else rib_span_m]
    for span in spans:
        _positive(span, 'floor support span')
        bending = pressure*span**2/8
        stress = bending/(face*(core+face))
        deflection = 5*pressure*span**4/(384*m['gfrp_longitudinal_e_pa']*inertia)
        shear = pressure*span/(2*core)
        floor_cases.append(dict(span_m=span, face_stress_pa=stress, estimated_core_shear_pa=shear,
            face_strength=margin(m['gfrp_strength_pa']*m['hot_strength_retention'], stress),
            deflection_m=deflection, deflection=margin(span/b['floor_deflection_divisor'], deflection),
            core_shear_capacity_pa=None, indentation_wrinkling_and_bond_acceptance=False))
    line = b['panel_joint_design_line_load_n_m']*load_multiplier*b['lap_load_concentration_factor']
    joint_capacity = b['lap_faces']*b['lap_overlap_m']*m['adhesive_shear_pa']*m['hot_strength_retention']
    stringer = _tube(b['stringer_outer_width_m'], b['stringer_outer_depth_m'], b['stringer_wall_m'])
    each_long = b['primary_longitudinal_load_n']*load_multiplier/b['stringers']
    euler = math.pi**2*m['gfrp_longitudinal_e_pa']*min(stringer['vertical_inertia_m4'], stringer['lateral_inertia_m4'])/b['stringer_bracing_pitch_m']**2
    rib = _tube(b['rib_width_m'], b['rib_depth_m'], b['rib_wall_m'])
    masses = dict(stringers_kg=b['stringers']*body['envelope_m']['length']*stringer['area_m2']*1900,
        ribs_kg=b['floor_ribs']*body['envelope_m']['width']*rib['area_m2']*m['aluminium_density_kg_m3'],
        local_laminate_patches_kg=count*b['hardpoint_length_m']*b['hardpoint_width_m']*b['hardpoint_solid_laminate_m']*1900,
        body_spreader_plates_kg=count*b['hardpoint_length_m']*b['hardpoint_width_m']*b['hardpoint_aluminium_spreader_m']*m['aluminium_density_kg_m3'])
    primary = sum(masses.values())
    rib_span=2.2
    rib_line=pressure*body['envelope_m']['length']/(b['floor_ribs']+1)
    rib_moment=rib_line*rib_span**2/8
    rib_stress=rib_moment/(rib['vertical_inertia_m4']/(b['rib_depth_m']/2))
    rib_deflection=5*rib_line*rib_span**4/(384*m['aluminium_e_pa']*rib['vertical_inertia_m4'])
    thin=_tube(.04,.08,.003)
    return dict(id='body-joints-hardpoints',car_mass_kg=mass,
        floor_loading_basis='Passenger payload unchanged between pack cases; battery mounts and local equipment attachments require separate qualified load paths',
        maximum_cartridge_interface_force_n=interface_force,
        load_path=['passenger/floor into cross-floor ribs and sandwich skins', 'continuous longitudinal tubes and local solid laminate hardpoints',
                   'bolted aluminium body spreader', 'separately owned magnetic-carrier box and retained ferrite cartridge'],
        hardpoint=dict(geometry={key: value for key, value in b.items() if key.startswith(('hardpoint', 'bolt', 'washer', 'carrier'))},
            bolt_shear_n=shear_each, bolt_tension_n=tension_each, interaction_ratio=interaction,
            bolt_combined=margin(1., interaction), laminate_bearing=margin(m['gfrp_bearing_pa']*m['hot_strength_retention'], laminate_bearing),
            local_pull_through=margin(pull_through, tension_each), carrier_bending=margin(m['aluminium_allowable_pa'], carrier_stress),
            peel_prying_fatigue_core_crushing_and_fastener_preload_qualified=False),
        floor_cases=floor_cases, floor_rib=dict(span_between_stringers_m=rib_span,
            tributary_length_m=body['envelope_m']['length']/(b['floor_ribs']+1),
            bending=margin(m['aluminium_allowable_pa'],rib_stress),
            deflection=margin(rib_span/b['floor_deflection_divisor'],rib_deflection),
            thin_80mm_rib_negative_control=margin(m['aluminium_allowable_pa'],rib_moment/(thin['vertical_inertia_m4']/.04))),
        panel_joint=dict(two_face_overlap_m=b['lap_overlap_m'],
            design_line_load_n_m=line, adhesive_shear=margin(joint_capacity, line),
            peel_fatigue_creep_fire_and_manufacturing_qualified=False),
        longitudinal_members=dict(section=stringer, total_longitudinal_load_n=b['primary_longitudinal_load_n']*load_multiplier,
            axial_strength=margin(stringer['area_m2']*m['gfrp_strength_pa']*m['hot_strength_retention'], each_long),
            braced_euler=margin(euler, each_long), crash_coupler_and_joint_qualification=False),
        partial_body_primary_masses_kg=masses, partial_primary_mass_kg=primary,
        body_primary_target_kg=cfg['body']['cases']['central']['primary_load_paths_kg'],
        remaining_before_bolts_joints_and_misc_kg=cfg['body']['cases']['central']['primary_load_paths_kg']-primary,
        ownership=dict(body='stringers/ribs/solid hardpoint patch/spreader, charged to existing 800kg primary allowance',
                       magnetic='carrier box/cartridge/coil: separate1500kg equipment allowance; not added again to body',
                       unresolved='bolt sets, actual overlaps, inserts, end frames, primary joints and equipment reinforcements need complete reconciliation'),
        complete_body_mass_closed=False, properties_qualified=False, **FLAGS)


def primary_frame_families(*, emergency_mass_kg=None, car_mass_kg=None):
    a=load();f=a['frame_remainder'];b=a['body'];m=a['materials'];body=structure.body();L=body['envelope_m']['length'];W=body['envelope_m']['width'];H=body['envelope_m']['height']
    families=[]
    def tube(name,count,run,w,d,t,material,owner):
        section=_tube(w,d,t);rho=1900. if material=='gfrp' else m['aluminium_density_kg_m3']
        families.append(dict(id=name,quantity=count,cut_length_m=run,section=section,material=material,
            owner=owner,total_mass_kg=count*run*section['area_m2']*rho,joining='bonded sleeve/local bolted hardpoint; exact joint tests open'))
    tube('lower-longitudinal-stringer',2,L,b['stringer_outer_width_m'],b['stringer_outer_depth_m'],b['stringer_wall_m'],'gfrp','primary800')
    tube('floor-cross-rib',b['floor_ribs'],W,b['rib_width_m'],b['rib_depth_m'],b['rib_wall_m'],'aluminium','primary800')
    tube('end-frame-post',2*f['end_frames'],H,f['end_frame_width_m'],f['end_frame_depth_m'],f['end_frame_wall_m'],'gfrp','primary800')
    tube('end-frame-crossmember',2*f['end_frames'],W,f['end_frame_width_m'],f['end_frame_depth_m'],f['end_frame_wall_m'],'gfrp','primary800')
    tube('roof-longitudinal',f['roof_longitudinals'],L,f['roof_rail_width_m'],f['roof_rail_depth_m'],f['roof_rail_wall_m'],'gfrp','primary800')
    tube('side-post',f['side_posts'],H,f['post_width_m'],f['post_depth_m'],f['post_wall_m'],'gfrp','primary800')
    tube('roof-crossmember',f['roof_crossmembers'],W,f['post_width_m'],f['post_depth_m'],f['post_wall_m'],'gfrp','primary800')
    tube('door-frame-post',2*f['door_frames'],2.1,f['door_frame_width_m'],f['door_frame_depth_m'],f['door_frame_wall_m'],'gfrp','opening-joints400')
    tube('door-frame-header-and-threshold',2*f['door_frames'],1.4,f['door_frame_width_m'],f['door_frame_depth_m'],f['door_frame_wall_m'],'gfrp','opening-joints400')
    base=body_interfaces();local={k:v for k,v in base['partial_body_primary_masses_kg'].items() if k not in {'stringers_kg','ribs_kg'}}
    for key,value in local.items():families.append(dict(id=key,quantity=24,total_mass_kg=value,owner='primary800',specification='24 exact body-side patches/spreaders; magnetic carrier excluded'))
    families.append(dict(id='primary-fastener-set',quantity=f['primary_fastener_sets'],total_mass_kg=f['primary_fastener_sets']*f['primary_fastener_set_mass_kg'],owner='primary800',specification='M12 four-per-hardpoint bolt/head/nut/washer set; net section and preload qualified externally'))
    families.append(dict(id='corner-load-connector',quantity=f['corner_connectors'],total_mass_kg=f['corner_connectors']*f['corner_connector_mass_kg'],owner='primary800',specification='Local aluminium connector allowance with an explicit count; exact geometry still requires joint design'))
    straps=f['bonded_joint_count']*f['joint_strap_length_m']*f['joint_strap_width_m']*f['joint_strap_m']*1900
    bond=f['bonded_joint_count']*f['joint_strap_length_m']*f['joint_strap_width_m']*f['joint_bondline_m']*1000
    families.append(dict(id='service-joint-strap-and-bond',quantity=f['bonded_joint_count'],total_mass_kg=straps+bond,owner='opening-joints400',specification='Counted300x100x3mm GFRP straps and1mm bondline; no peel/crash/fatigue capacity credit'))
    primary=sum(x['total_mass_kg'] for x in families if x['owner']=='primary800')
    opening=sum(x['total_mass_kg'] for x in families if x['owner']=='opening-joints400')
    excess=max(0.,primary-800)+max(0.,opening-400)
    from . import system_campaign
    reserve=structure.load()['vehicle']['growth_reserve_kg']
    mass=body['aw3_target_kg'] if car_mass_kg is None else _positive(car_mass_kg,'per-car gross mass')
    brake=system_campaign.emergency_brake(car_mass_kg=car_mass_kg)['added_mass_kg_per_car'] if emergency_mass_kg is None else _positive(emergency_mass_kg,'emergency mass allocation',True)
    return dict(id='provisional-complete-primary-frame-family-takeoff',families=families,
        defined_member_piece_count=sum(x['quantity'] for x in families if 'cut_length_m' in x),
        primary_family_mass_kg=primary,opening_and_joint_family_mass_kg=opening,
        primary_allowance_kg=800.,opening_joints_allowance_kg=400.,frame_budget_overrun_kg=excess,
        reserve_allocation=dict(existing_kg=reserve,frame_overrun_kg=excess,separately_proposed_emergency_kg=brake,
            additional_pack_mass_already_in_tare_kg=mass-body['aw3_target_kg'],
            remaining_before_other_system_growth_kg=reserve-excess-brake,
            nominal_tare_including_existing_reserve_kg=14200.+mass-body['aw3_target_kg'],reserve_is_new_mass_credit=False,
            emergency_quantity_basis='Exact system_campaign.emergency_brake per-car input thermal and hardware calculation; no study()/publication invoked',
            mass_accounting_scope='Pack increment is included once in tare/gross mass; retained growth reserve is debited for frame overrun and exact brake proposal only'),
        provisional_family_taxonomy_fully_counted=True,complete_manufacturing_drawings=False,
        remaining=['128 joints need exact node/part mapping and fatigue/fire/peel qualification',
            '48 connector shapes and primary fastener details require joined-member load cases',
            'Complete equipment, magnetic carrier, gangway/crash, doorway and payload reaction mapping and mass/CG/inertia remain open'],**FLAGS)


def foundation_cost_delta(*, depth=None, span=None, car_mass_kg=None):
    a=load();r=a['foundation_cost'];cv=_current_civil(depth=depth,span=span,car_mass_kg=car_mass_kg);path=emergency_load_path(depth=depth,span=span,car_mass_kg=car_mass_kg)
    selected=path['conditional_foundation_candidate']
    if selected is None:return dict(state='hold-no-footing-candidate',proposed_support_allowance_usd=None,qualified_foundation_selection=None,**FLAGS)
    baseline=r['baseline_footing_side_m']**2*structure.load()['civil']['footing_thickness_m']
    proposed=selected['concrete_m3'];extra=proposed-baseline
    clearance=r['excavation_clearance_each_side_m'];depth_exc=r['excavation_depth_m']
    old_exc=(r['baseline_footing_side_m']+2*clearance)**2*depth_exc
    new_exc=(selected['square_side_m']+2*clearance)**2*depth_exc
    quantities=dict(baseline_footing_concrete_m3=baseline,proposed_footing_concrete_m3=proposed,
        extra_concrete_m3=extra,extra_reinforcement_kg=extra*r['reinforcement_kg_m3'],
        extra_excavation_m3=new_exc-old_exc,extra_backfill_m3=(new_exc-proposed)-(old_exc-baseline))
    rows=[dict(id='extra-concrete',quantity=extra,unit='m3',rate_usd=r['concrete_cast_usd_m3']),
        dict(id='extra-reinforcement',quantity=quantities['extra_reinforcement_kg'],unit='kg',rate_usd=r['reinforcement_fabricated_usd_kg']),
        dict(id='extra-excavation',quantity=quantities['extra_excavation_m3'],unit='m3',rate_usd=r['excavation_usd_m3']),
        dict(id='extra-backfill',quantity=quantities['extra_backfill_m3'],unit='m3',rate_usd=r['backfill_usd_m3'])]
    for row in rows:row['amount_usd']=row['quantity']*row['rate_usd'];row['supplier_quote']=False
    delta=sum(x['amount_usd'] for x in rows)
    return dict(id='conditional-anchored-bay-foundation-cost-delta',car_mass_kg=cv['loading']['aw3_mass_kg_per_car'],quantity_basis=quantities,
        foundation_square_side_m=selected['square_side_m'],footing_thickness_m=selected['thickness_m'],rows=rows,
        baseline_support_allowance_usd=r['baseline_support_allowance_usd'],incremental_support_allowance_usd=delta,
        proposed_support_allowance_usd=r['baseline_support_allowance_usd']+delta,
        supports_per_two_direction_route_km=1000/cv['span_m'],incremental_ordinary_route_km_allowance_usd=delta*1000/cv['span_m'],
        comparative_basis='Baseline22k ordinary package assumed to include4.5m-square0.8m footing and180kg/m3 reinforcing intensity; only differential quantities charged, not a quotation',
        unpriced=['actual ground/piles/dewatering/utilities','pier hoop/longitudinal/anchor/socket reinforcement reconciled against existing package','formwork, soil support, property footprint, schedule and lifting effects','brake reaction rail, complete bearing/anchor proof and programme overhead'],
        complete_installed_support_price_usd=None,qualified_foundation_selection=None,costs_are_supplier_quotes=False,**FLAGS)


def stator_interfaces(*, thrust_multiplier=1., car_mass_kg=None):
    _positive(thrust_multiplier, 'thrust multiplier')
    a = load(); s = a['stator']; m = a['materials']; cv = structure.load()['civil']
    formation=configuration.selected().formation
    magnetic_fill=(12.*formation.cars)/formation.assumed_overall_length_m
    active_density=s['force_density_n_per_envelope_m']/magnetic_fill
    force = s['cassette_length_m']*active_density*s['thrust_load_multiplier']*thrust_multiplier
    per_face = force/s['cassette_faces']; each = per_face/s['mounts_per_face_cassette']
    plate_moment = each*s['mount_outstand_m']; modulus = s['mount_width_m']*s['mount_plate_m']**2/6
    mass=structure.body()['aw3_target_kg'] if car_mass_kg is None else _positive(car_mass_kg,'per-car gross mass')
    vertical = mass*9.81/24*s['vertical_cartridge_force_multiplier']
    faces = 2*s['cassette_faces'] # two directions
    cassettes = faces*math.ceil(s['winding_length_per_direction_m']/s['cassette_length_m'])
    return dict(id='station-motor-interfaces',car_mass_kg=mass,paired_cassette_design_thrust_n=force,
        equivalent_envelope_force_density_n_m=s['force_density_n_per_envelope_m'],actual_active_band_force_density_n_m=active_density,
        per_face_thrust_n=per_face, per_mount_thrust_n=each,
        bolt_shear=margin(s['bolt_thread_area_m2']*m['bolt_shear_pa'], each),
        simple_mount_bending=margin(m['steel_allowable_pa'], plate_moment/modulus),
        quantities_per_two_direction_station=dict(face_cassettes=cassettes, paired_cassettes=cassettes/2,
            addressable_sections=2*math.ceil(s['winding_length_per_direction_m']/s['addressable_section_m']),
            mount_bolts=cassettes*s['mounts_per_face_cassette'],
            cassette_to_25m_bay_sets_per_face=cv['span_m']/s['cassette_length_m']),
        required_unmeasured_stator_normal_force_n=None,
        passive_support_local_vertical_force_n=vertical,
        local_vertical_anchor_and_concrete_capacity_n=None,
        interface_spec=dict(cassette_length_m=s['cassette_length_m'], section_length_m=s['addressable_section_m'],
            bolt_nominal_diameter_m=s['bolt_diameter_m'], four_mounts_per_face=True,
            adjustment='inspectable slotted/aligned bracket datum; hole travel and preload to follow actual tolerance chain',
            separation='passive support iron and active motor mounts have separately recorded normal/thrust reactions'),
        connection_release=False, missing=['actual winding/steel/normal-force maps', 'out-of-plane bolt prying and fatigue',
            'embedded anchors, edge distances, concrete breakout, rail corbels and local beam torsion',
            'full R/L/current/voltage/temperature and phase-coherent full-train performance'], **FLAGS)


def _current_civil(*,depth=None,span=None,car_mass_kg=None):
    cv=configuration.selected().civil
    return structure.civil(width=cv.width_m,depth=cv.depth_m if depth is None else depth,
        web=cv.web_m,flange=cv.flange_m,span=cv.span_m if span is None else span,pier_height=cv.pier_height_m,car_mass_kg=car_mass_kg)


def civil_stages(*, load_multiplier=1., depth=None, span=None, car_mass_kg=None):
    _positive(load_multiplier, 'civil load multiplier')
    a = load(); s = a['civil']; m = a['materials']; cv = _current_civil(depth=depth,span=span,car_mass_kg=car_mass_kg); section = cv['section']
    length = cv['span_m']; area = section['area_m2']; modulus = section['vertical_inertia_m4']/(section['depth_m']/2)
    dead = cv['beam']['concrete_plus_iron_kg']/length*9.81
    live = cv['loading']['aw3_mass_kg_per_car']/structure.body()['envelope_m']['length']*9.81
    bottom = s['prestress_bottom_strands']; top = s['prestress_top_strands']; total = bottom+top
    depth_change=(section['depth_m']-1.8)/2
    bottom_ecc=s['bottom_eccentricity_m']+depth_change
    top_ecc=s['top_eccentricity_m']-depth_change
    initial = s['strand_area_m2']*s['strand_fpu_pa']*s['initial_stress_fraction']
    effective = initial*(1-s['prestress_loss_fraction'])
    def stress(moment, nb, nt, per_strand, limit):
        axial = (nb+nt)*per_strand/area
        pm = (nb*bottom_ecc+nt*top_ecc)*per_strand
        top_stress = axial-pm/modulus+moment/modulus
        bottom_stress = axial+pm/modulus-moment/modulus
        return dict(top_compression_pa=top_stress, bottom_compression_pa=bottom_stress,
            compression=margin(limit, max(0.,top_stress,bottom_stress)),
            tension=margin(m['concrete_tension_screen_pa'], max(0.,-top_stress,-bottom_stress)),
            prestress_n=(nb+nt)*per_strand)
    service_moment = (s['dead_load_multiplier']*dead+s['live_load_multiplier']*live)*length**2/8*load_multiplier
    lift = s['lifting_point_from_end_m']; supports = length-2*lift
    if supports <= 0:
        raise ValueError('lifting supports cross')
    handling_q = dead*s['handling_dynamic_multiplier']*load_multiplier
    mid_moment = handling_q*(supports**2/8-lift**2/2)
    end_moment = -handling_q*lift**2/2
    service = stress(service_moment,bottom,top,effective,m['concrete_strength_pa']*m['concrete_compression_fraction'])
    transfer_mid = stress(mid_moment,bottom,top,initial,m['concrete_transfer_strength_pa']*m['concrete_transfer_compression_fraction'])
    original_end = stress(end_moment,bottom,top,initial,m['concrete_transfer_strength_pa']*m['concrete_transfer_compression_fraction'])
    bonded_end = stress(end_moment,bottom-s['proposed_end_debonded_bottom_strands'],top,initial,
        m['concrete_transfer_strength_pa']*m['concrete_transfer_compression_fraction'])
    reaction = cv['beam']['concrete_plus_iron_kg']*9.81*s['handling_dynamic_multiplier']/2*load_multiplier
    flange=section['flange_m'];bar=s['strand_nominal_diameter_m'];pitch=s['strand_row_pitch_m']
    cover=(flange-pitch-bar)/2
    return dict(id='civil-strength-stages',section=section,span_m=length,car_mass_kg=cv['loading']['aw3_mass_kg_per_car'],
        strand_layout=dict(bottom_rows=2,bottom_strands_per_row=bottom//2,top_rows=1,top_strands=top,
            bottom_row_pitch_m=pitch,net_vertical_strand_clearance_m=pitch-bar,
            flange_outer_and_inner_cover_m=cover,
            cover_screen_pass=cover>=s['minimum_cover_study_m'],
            concrete_flow_clearance_screen_pass=pitch-bar>=s['minimum_strand_clearance_study_m'],
            no_strands_in_void=True,layout_qualified=False), load_cases=dict(dead_line_n_m=dead, live_line_n_m=live,
        factored_service_moment_nm=service_moment, demould_lift_mid_moment_nm=mid_moment,
        demould_lift_overhang_moment_nm=end_moment, per_lifting_point_vertical_n=reaction),
        prestress_spec=dict(bottom_strands=bottom,top_strands=top,strand_nominal_diameter_m=s['strand_nominal_diameter_m'],
            strand_metal_area_m2=s['strand_area_m2'],initial_force_per_strand_n=initial,effective_force_per_strand_n=effective,
            bottom_eccentricity_m=bottom_ecc,top_eccentricity_m=top_ecc,
            end_debond_candidate_count=s['proposed_end_debonded_bottom_strands'],end_debond_length_m=s['end_debond_length_m'],
            straight_tendon_length_m=total*length,anchorages_and_transfer_design_qualified=False),
        service=service,transfer_mid=transfer_mid,unmodified_end_negative_control=original_end,
        reduced_bonded_end_candidate=bonded_end,
        handling_spec=dict(support_from_each_end_m=lift, dynamic_multiplier=s['handling_dynamic_multiplier'],
            lifting_insert_design_n=reaction,required_release_strength_pa=m['concrete_transfer_strength_pa'],
            release_strength_measured=False,crane_capacity_at_radius_proved=False,temporary_lateral_bracing_qualified=False),
        notes=['Gross uncracked stress only; actual tendon transfer/debond length, shear, end zones and anchorage unsolved',
            'Middle/end-section homogenisation and UDL replace variable-section moving cartridge loads only for this screen',
            'Thermal gradients, creep, shrinkage, cracking, torsion, fatigue and relative magnetic gap require qualified models'], **FLAGS)


@lru_cache(maxsize=2)
def _corridor_force_values(path,expected_digest):
    data=Path(path).read_bytes()
    if sha256(data).hexdigest()!=expected_digest:raise ValueError('corridor force payload changed')
    with gzip.open(path,'rb') as stream:raw=stream.read(128*1024*1024+1)
    if len(raw)>128*1024*1024:raise ValueError('bounded corridor force evidence required')
    value=json.loads(raw)
    if value.get('schema')!='osr-fixed-corridor-study/1' or value.get('executed_numerical_study_pass') is not True:
        raise ValueError('executed corridor force evidence required')
    roles=[mode+'/'+role for mode in ('urban','suburban') for role in ('nominal','reduced-E-positive-bias','reduced-E-negative-bias')]
    peaks={}
    for role in roles:
        run=value['moving'][role]['run']
        if run.get('study_pass') is not True or run.get('completed_moving_steps')!=run.get('planned_moving_steps'):
            raise ValueError('complete exact moving force reference required')
        peaks[role]=_positive(run['peak_coupler_force_n'],'executed coupler force',True)
    return peaks


def _corridor_force_reference():
    folder=ROOT/'docs/design-engine/ferrite-maglev/corridor';receipt=folder/'manifest.json';payload=folder/'result.json.gz'
    hold=dict(state='hold-no-current-exact-corridor-reference',maximum_peak_force_n=None,peaks_by_exact_case_n={},manifest_sha256=None)
    if not receipt.is_file() or receipt.is_symlink() or not payload.is_file() or payload.is_symlink():return hold
    try:
        raw=receipt.read_bytes();manifest=json.loads(raw);sources=manifest.get('source_sha256',{})
        if manifest.get('schema')!='osr-fixed-corridor-publication/1' or not sources:return hold
        safe=lambda p:isinstance(p,str) and p and not Path(p).is_absolute() and '..' not in Path(p).parts and Path(p).as_posix()==p
        if any(not safe(name) or not (ROOT/name).is_file() or (ROOT/name).is_symlink() or sha256((ROOT/name).read_bytes()).hexdigest()!=expected for name,expected in sources.items()):return hold
        expected=manifest['files_sha256']['result.json.gz']
        if payload.stat().st_size>64*1024*1024 or sha256(payload.read_bytes()).hexdigest()!=expected:return hold
        peaks=_corridor_force_values(str(payload),expected)
        return dict(state='current-executed-corridor-reference',maximum_peak_force_n=max(peaks.values()),peaks_by_exact_case_n=peaks,
            manifest_sha256=sha256(raw).hexdigest(),physical_force_qualified=False)
    except (OSError,ValueError,KeyError,TypeError):return hold


def coupler_detail(*, peak_force_n=None):
    a=load();c=a['coupler'];m=a['materials']
    assumed=c['assumed_operating_peak_envelope_n']
    observed=assumed if peak_force_n is None else _positive(peak_force_n,'coupler force probe')
    reference=_corridor_force_reference();exact=reference['maximum_peak_force_n']
    within=exact is not None and exact<=assumed
    area=math.pi*c['rod_diameter_m']**2/4
    total_area=c['rods']*area
    stiffness=m['steel_young_pa']*total_area/c['rod_effective_length_m']
    additional=c['joint_additional_compliance_m_n']
    if additional<0:raise ValueError('negative joint compliance')
    stiffness=1/(1/stiffness+additional)
    demand=max(c['structural_force_study_n'],observed*2)
    each=demand/c['rods']
    i=math.pi*c['rod_diameter_m']**4/64
    unbraced=math.pi**2*m['steel_young_pa']*i/c['rod_effective_length_m']**2*c['rods']
    guided=math.pi**2*m['steel_young_pa']*i/c['lateral_guide_pitch_m']**2*c['rods']
    thread=c['rods']*c['end_thread_stress_area_m2']*c['rod_stress_screen_pa']
    pin_area=math.pi*c['end_pin_diameter_m']**2/4
    return dict(id='guided-longitudinal-coupler',specification=c,
        source_peak_note='100kN is an ASSUMED operating design envelope, not an observed or qualified force. Exact nominal/adverse numerical force peaks are retained separately.',
        assumed_operating_force_envelope_n=assumed,exact_executed_force_reference=reference,
        exact_executed_peak_pair_force_n=exact,operating_force_envelope_screen_pass=within,
        operating_force_evidence_state='within-assumed-envelope' if within else 'hold-no-current-reference' if exact is None else 'hold-exact-force-exceeds-assumed-envelope',
        assumed_peak_pair_force_n=observed,design_force_n=demand,
        rod_assembly_stiffness_n_m=stiffness,target_stiffness_n_m=c['target_stiffness_n_m'],
        peak_elastic_extension_m=observed/stiffness,
        maximum_five_joint_extension_m=5*observed/stiffness,
        rod_stress=margin(c['rod_stress_screen_pa'],each/area),
        end_thread_tension=margin(thread,demand),
        double_shear_pin=margin(c['rods']*2*pin_area*m['bolt_shear_pa'],demand),
        double_fork_bearing=margin(c['rods']*2*c['end_pin_diameter_m']*c['fork_plate_each_m']*m['steel_allowable_pa'],demand),
        unsupported_compression_negative_control=margin(unbraced,demand),
        guided_compression=margin(guided,demand),
        rod_mass_kg=total_area*c['rod_effective_length_m']*m['steel_density_kg_m3'],
        physical_length_inside_each_car_assumption_m=(c['rod_effective_length_m']-.5)/2,
        body_and_pin_compliance_included=False,
        full_assembly_stiffness_qualified=False,
        remaining=['forged/rolled M36 enlarged ends on30mm rods, heat treatment and fatigue/corrosion proof',
            'positive compression guides at250mm, guide wear, articulation, lateral/vertical sweep and secure pin retention',
            'gangway/crash energy/anti-climb, body hardpoint compliance, tolerance/backlash and measured six-car phase indexing'],**FLAGS)


def _maximum_span_units(positions, span):
    """Exact event-based maximum point count in one half-open simply supported bay."""
    if not positions or len(positions)>1000:
        raise ValueError('bounded nonempty pad positions required')
    _positive(span,'span')
    events=sorted({p%span for p in positions}); shifts={0.}
    for phase in events:
        shifts.update(((-phase)%span,(-phase+1e-7)%span,(-phase-1e-7)%span))
    best=0;translation=None;occupancy=None
    for shift in sorted(shifts):
        bins={}
        for pos in positions:
            key=math.floor((pos+shift)/span);bins[key]=bins.get(key,0)+1
        peak=max(bins.values())
        if peak>best:best=peak;translation=shift;occupancy=bins
    return dict(maximum_units_per_span=best,translation_m=translation,span_occupancy={str(k):v for k,v in occupancy.items()},
        method='All pad/span-boundary translation events and both sides; half-open bays avoid double counting boundary pads')


def emergency_load_path(brake=None,*,depth=None,span=None,car_mass_kg=None):
    a=load();e=a['emergency'];s=a['civil'];m=a['materials'];b=a['anchored_bay'];cfg=structure.load()
    if brake is not None and 'train_mass_kg' in brake:
        inferred=_positive(brake['train_mass_kg'],'brake train mass')/cfg['vehicle']['cars']
        if car_mass_kg is not None and not math.isclose(car_mass_kg,inferred,rel_tol=1e-10):
            raise ValueError('brake and structural per-car masses differ')
        car_mass_kg=inferred
    cv=_current_civil(depth=depth,span=span,car_mass_kg=car_mass_kg)
    if brake is None:
        # Read the pure force/energy proposal only; study()/sources() are not
        # invoked, so retained moving/campaign receipts do not form a cycle.
        from . import system_campaign
        brake=system_campaign.emergency_brake(car_mass_kg=car_mass_kg)
    force=_positive(brake['braking_force_n'],'emergency braking force')
    units=e['units'];pad_area=_positive(brake.get('interface_loads',{}).get('pad_area_m2',e['pad_area_m2']),'pad area')
    car_length=structure.body()['envelope_m']['length'];pitch=car_length+.5;cars=cfg['vehicle']['cars']
    positions=[car*pitch+x for car in range(cars) for x in b['brake_unit_offsets_from_car_front_m']]
    if len(positions)!=units:raise ValueError('brake count and physical pad layout differ')
    span=cv['span_m'];occupancy=_maximum_span_units(positions,span)
    span_force=force/units*occupancy['maximum_units_per_span']
    height=cv['supports']['column_height_m']+.9+cv['section']['depth_m']
    cg_height=height+b['train_cg_above_beam_m']
    normal=cv['supports']['foundation_top_gravity_kn']*1000
    column_area=math.pi/4*(cfg['civil']['column_outer_diameter_m']**2-cfg['civil']['column_inner_diameter_m']**2)
    column_i=math.pi/64*(cfg['civil']['column_outer_diameter_m']**4-cfg['civil']['column_inner_diameter_m']**4)
    column_z=column_i/(cfg['civil']['column_outer_diameter_m']/2)
    euler=math.pi**2*cfg['civil']['concrete_young_pa']*column_i/(s['column_effective_length_factor']*cv['supports']['column_height_m'])**2
    pdelta=1/(1-normal/euler) if normal<euler else None
    reinforcement_area=s['column_longitudinal_bars']*math.pi*s['column_bar_diameter_m']**2/4
    bar_volume=reinforcement_area*cv['supports']['column_height_m']
    net_bar_mass=bar_volume*(m['steel_density_kg_m3']-cfg['civil']['concrete_density_kg_m3'])
    normal+=net_bar_mass*9.81
    moment_capacity=reinforcement_area/2*s['column_bar_design_stress_pa']*s['column_bar_lever_arm_m']
    axial_capacity=column_area*m['concrete_strength_pa']*m['concrete_compression_fraction']
    curve_accel=(b['curve_speed_kmh']/3.6)**2/b['route_curve_radius_m']
    # Every guidebeam has one longitudinal fixed bearing at its downstream end
    # and one guided bearing. Its pad forces transfer to that one fixed support.
    # This is an explicit restraint proposal, not a load divided by train length.
    longitudinal=e['two_direction_coincidence']*span_force
    lateral=e['two_direction_coincidence']*cv['loading']['aw3_mass_kg_per_car']/car_length*span*curve_accel
    one_lane_eccentric_live=cv['loading']['aw3_mass_kg_per_car']/car_length*span*9.81*cfg['civil']['beam_centres_m']/2
    mx=longitudinal*(height-.3)+s['column_wind_moment_knm']*1000
    my=lateral*cg_height+one_lane_eccentric_live
    resultant=math.hypot(mx,my)*(pdelta if pdelta else 1e6)
    interaction=normal/axial_capacity+resultant/moment_capacity
    footings=[]
    rho=cfg['civil']['concrete_density_kg_m3'];thickness=cfg['civil']['footing_thickness_m']
    for width in b['foundation_square_sides_m']:
        q0=normal/width**2+rho*9.81*thickness
        q_moment=6*(abs(mx)+abs(my))/width**3
        maxp=q0+q_moment;minp=q0-q_moment
        footings.append(dict(square_side_m=width,thickness_m=thickness,concrete_m3=width**2*thickness,
            maximum_pressure_pa=maxp,minimum_pressure_pa=minp,
            pressure_screen=margin(s['foundation_allowable_pressure_pa'],maxp),
            no_tension_screen_pass=minp>=0,
            sliding=margin((normal+width**2*thickness*rho*9.81)*s['foundation_friction_coefficient'],math.hypot(longitudinal,lateral)),
            screen_pass=maxp<=s['foundation_allowable_pressure_pa'] and minp>=0,
            ground_or_structural_acceptance=False))
    selected=next((row for row in footings if row['screen_pass']),None)
    rail_cases=[];dedicated=_tube(e['dedicated_box_width_m'],e['dedicated_box_depth_m'],e['dedicated_box_wall_m'])
    for mu in e['friction_screens']:
        _positive(mu,'friction coefficient')
        clamp=force/mu;per=clamp/units
        rail_stress=per*e['existing_plate_outstand_m']/(e['existing_plate_effective_strip_width_m']*e['existing_reaction_plate_m']**2/6)
        dedicated_stress=per*e['dedicated_outstand_m']/(dedicated['vertical_inertia_m4']/(e['dedicated_box_depth_m']/2))
        rail_cases.append(dict(friction_coefficient=mu,total_clamp_force_n=clamp,per_unit_clamp_force_n=per,
            pad_bearing=margin(e['pad_bearing_allowable_pa'],per/pad_area),
            existing_unstiffened_iron_negative_control=margin(m['steel_allowable_pa'],rail_stress),
            dedicated_reaction_box=margin(m['steel_allowable_pa'],dedicated_stress),
            dedicated_box_section=dedicated,local_concrete_anchor_capacity_n=None,
            thermal_wear_magnetic_and_fault_qualification=False))
    anchor_shear=b['fixed_anchor_bolts']*b['anchor_thread_area_m2']*m['bolt_shear_pa']
    vertical_reaction=(cv['beam']['concrete_plus_iron_kg']+cv['loading']['aw3_mass_kg_per_car']/car_length*span)*9.81/2
    return dict(id='emergency-brake-and-curve-load-path',car_mass_kg=cv['loading']['aw3_mass_kg_per_car'],input_brake=brake,
        per_unit_longitudinal_force_n=force/units,brake_unit_positions_from_consist_front_m=positions,span_pad_occupancy=occupancy,
        restraint_spec=dict(fixed_bearings_per_beam=1,guided_bearings_per_beam=1,
            fixed_bearing_design_longitudinal_n=span_force, shared_support_two_lane_longitudinal_n=longitudinal,
            anchor_bolts=b['fixed_anchor_bolts'],anchor_nominal_diameter_m=b['anchor_diameter_m'],
            bolt_shear_only=margin(anchor_shear,span_force),concrete_anchor_bearing_and_fatigue_qualified=False,
            bearing_average_vertical_pressure_pa=vertical_reaction/(b['bearing_length_m']*b['bearing_width_m']),
            bearing_compression=margin(b['bearing_compression_screen_pa'],vertical_reaction/(b['bearing_length_m']*b['bearing_width_m'])),
            thermal_movement='one guided/sliding end per span; rail/drive joints must preserve movement; no restraint across every expansion gap'),
        curve_case=dict(radius_m=b['route_curve_radius_m'],speed_kmh=b['curve_speed_kmh'],lateral_acceleration_m_s2=curve_accel,
            shared_support_lateral_n=lateral,unbalanced_lane_live_overturning_nm=one_lane_eccentric_live,
            rigid_12m_chord_sagitta_m=12**2/(8*b['route_curve_radius_m']),
            car_chord_arc_index_difference_m=2*b['route_curve_radius_m']*math.asin(pitch/(2*b['route_curve_radius_m']))-pitch,
            car_chord_arc_electrical_phase_degrees=(2*b['route_curve_radius_m']*math.asin(pitch/(2*b['route_curve_radius_m']))-pitch)/.5*360,
            rigid_array_clearance_accepted=False,magnetic_face_and_vehicle_sweep_qualified=False),
        support=dict(axial_n=normal,moment_x_nm=mx,moment_y_nm=my,resultant_with_pdelta_nm=resultant,
            euler_critical_n=euler,pdelta_multiplier=pdelta,
            bare_concrete_tension_pa=max(0.,resultant/column_z-normal/column_area),
            longitudinal_bars=s['column_longitudinal_bars'],bar_diameter_m=s['column_bar_diameter_m'],
            longitudinal_bar_length_m=s['column_longitudinal_bars']*cv['supports']['column_height_m'],
            longitudinal_bar_mass_kg=bar_volume*m['steel_density_kg_m3'],displaced_concrete_m3=bar_volume,
            net_mass_above_gross_concrete_assumption_kg=net_bar_mass,
            nominal_reinforcing_moment_nm=moment_capacity,nominal_axial_screen_n=axial_capacity,
            assumed_linear_interaction=margin(1.,interaction),
            full_section_interaction_confinement_shear_and_socket_design_qualified=False),
        footing_cases=footings,conditional_foundation_candidate=selected,qualified_foundation_selection=None,
        single_support_full_train_negative_control=dict(longitudinal_n=force*e['two_direction_coincidence'],
            base_moment_nm=force*e['two_direction_coincidence']*(height-.3),
            baseline_4p5m_maximum_pressure_pa=normal/4.5**2+rho*9.81*thickness+6*force*e['two_direction_coincidence']*(height-.3)/4.5**3,
            pressure_screen_pass=(normal/4.5**2+rho*9.81*thickness+6*force*e['two_direction_coincidence']*(height-.3)/4.5**3)<=s['foundation_allowable_pressure_pa']),
        clamp_rail_cases=rail_cases,
        remaining=['bearing anchors/end blocks and guided movements under all loads','pad reaction channel continuity, anchors and magnetic coexistence',
            'actual friction at temperature/wear/contamination, heat rejection and emergency stopping proof',
            'ground bearing/settlement/sliding, nonlinear reinforced pier/socket/pile design',
            'moving six-car and curved magnetic carrier/rail/stator interaction'], **FLAGS)


def _evidence():
    records={}
    for name,receipt_name in PACKETS.items():
        folder=ROOT/'docs/design-engine/ferrite-maglev'/name;receipt=folder/receipt_name
        row=dict(path=receipt.relative_to(ROOT).as_posix(),sha256=None,state='missing',engineering_acceptance=False)
        if receipt.is_file() and not receipt.is_symlink():
            row['sha256']=sha256(receipt.read_bytes()).hexdigest()
            value=json.loads(receipt.read_text())
            if value.get('schema')!=RECEIPT_SCHEMAS[name]:
                row.update(state='hold-unknown-receipt-schema',schema=value.get('schema'),source_and_payload_consistent=False)
                records[name]=row;continue
            sources=value.get('source_sha256',value.get('sources_sha256',{}));conflicting_source=False
            if name=='native':
                # This established packet separates configuration provenance from
                # its generator and exporter identities. Verify their union
                # directly without calling another verifier or study().
                sources=dict(value.get('geometry_sources_sha256',{}))
                for path,expected in (('engineering/ferrite_maglev/geometry.py',value.get('geometry_sha256')),
                        ('engineering/factory_examples/native.py',value.get('exporter_sha256'))):
                    if path in sources and sources[path]!=expected:conflicting_source=True
                    sources[path]=expected
            payloads=value.get('files_sha256',{})
            safe=lambda p: isinstance(p,str) and p and not Path(p).is_absolute() and '..' not in Path(p).parts and Path(p).as_posix()==p
            current=not conflicting_source and bool(sources) and all(safe(p) and (ROOT/p).is_file() and not (ROOT/p).is_symlink() and sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in sources.items())
            intact=bool(payloads) and all(safe(p) and (folder/p).is_file() and not (folder/p).is_symlink() and sha256((folder/p).read_bytes()).hexdigest()==h for p,h in payloads.items())
            row.update(state='current-retained-digital-records' if current and intact else 'stale-or-incomplete',
                source_and_payload_consistent=current and intact,scope=value.get('scope','Bounded digital study; see exact receipt and source'))
        records[name]=row
    return records


def obligations(evidence=None):
    controlled=json.loads(OBLIGATIONS.read_text());groups=controlled['groups']
    if controlled.get('schema')!='osr-design-dossier-obligation-map/1' or len({g['id'] for g in groups})!=len(groups):
        raise ValueError('controlled unique deliverable groups required')
    reqs=requirements.register()['requirements'];systems=transition.inventory_inputs()
    system_ids=[i for g in groups for i in g['system_ids']]
    sp_numbers=[n for g in groups for n in g['sp_numbers']]
    if sorted(system_ids)!=sorted(r['id'] for r in systems) or len(system_ids)!=len(set(system_ids)) or sorted(sp_numbers)!=list(range(1,101)):
        raise ValueError('every system and all100 specification obligations must have exactly one primary owner')
    evidence=_evidence() if evidence is None else evidence
    rows=[]
    for r in reqs:
        if r['id'].startswith('SP-'):
            assigned=[g for g in groups if r['number'] in g['sp_numbers']]
        elif r['id'].startswith('EVAC-'):
            assigned=[g for g in groups if g['id']=='station-egress']
        else:
            assigned=[g for g in groups if set(r.get('work_package_ids',[])) & set(g['work_packages'])]
        if not assigned:raise ValueError('requirement lacks concrete deliverable allocation: '+r['id'])
        rows.append(dict(id=r['id'],requirement=r['requirement'],deliverable_ids=[g['id'] for g in assigned],
            concrete_deliverables=[g['deliverable'] for g in assigned],
            retained_evidence=[evidence[name] for name in sorted({p for g in assigned for p in g['current_evidence_packets']})],
            missing_evaluators_or_external_tests=sorted({p for g in assigned for p in g['missing_evaluators_or_external_tests']}),
            state='calculated-details-and-retained-studies; full-obligation-acceptance-open',accepted=False))
    return dict(requirements=rows,systems=[dict(id=r['id'],title=r['title'],
        deliverable_id=next(g['id'] for g in groups if r['id'] in g['system_ids']),source=r['source'],
        process_route=r['process_route'],complete_production_specification=False,accepted=False) for r in systems],
        deliverable_groups=groups,requirement_count=len(rows),system_count=len(systems),accepted_requirements=0,
        coverage_means='Every obligation has a specific deliverable and explicit evidence gap; allocation is not engineering completion',**FLAGS)


def study():
    evidence=_evidence()
    selected=configuration.selected().civil
    current=configuration.document(ROOT/'ferrite-maglev-study.toml')
    from . import model, system_campaign
    # Match the executed wider corridor references. The retained 30 kWh model
    # remains an explicit comparison, not evidence for the heavier formation.
    primary_mass=model.mass(current,current['mass']['ferrite_base'],50.)
    per_car=primary_mass['aw3_kg'];cars=current['vehicle']['cars_per_train']
    brake=system_campaign.emergency_brake(current,car_mass_kg=per_car)
    primary_path=emergency_load_path(brake,car_mass_kg=per_car)
    return dict(schema='osr-manufactured-design-dossier/1',configuration=load(),evidence=evidence,
        primary_mass_case=dict(role='50kWh urban/suburban corridor reference; unweighed design hypothesis',battery_kwh_per_car=50.,
            car_mass_kg=per_car,train_mass_kg=per_car*cars,tare_kg_per_car=primary_mass['tare_kg'],
            physical_mass_accepted=False,mass_and_inertia_measurements_required=True),
        body_interfaces=body_interfaces(car_mass_kg=per_car),primary_frame_families=primary_frame_families(car_mass_kg=per_car),
        foundation_cost_delta=foundation_cost_delta(car_mass_kg=per_car),stator_interfaces=stator_interfaces(car_mass_kg=per_car),
        civil_stages=civil_stages(car_mass_kg=per_car),coupler_detail=coupler_detail(),
        emergency_brake_case=brake,emergency_and_curve_load_path=primary_path,
        moving_profile_candidate=dict(depth_m=selected.depth_m,span_m=selected.span_m,runtime_s=current['vehicle']['runtime_reference_seconds'],
            role='50kWh static load envelope on common geometry; runtime field is retained 30kWh/1km benchmark reference, not an executed 50kWh moving case',
            car_mass_kg=per_car,civil_stages=civil_stages(car_mass_kg=per_car),emergency_load_path=primary_path),
        retained_30kwh_benchmark=dict(role='Retained configured 30kWh/1km benchmark; does not qualify the heavier 50kWh formation',
            battery_kwh_per_car=current['power']['services_battery_kwh_per_car'],car_mass_kg=structure.body()['aw3_target_kg'],
            body_interfaces=body_interfaces(),primary_frame_families=primary_frame_families(),stator_interfaces=stator_interfaces(),
            civil_stages=civil_stages(),emergency_brake_case=system_campaign.emergency_brake(),emergency_and_curve_load_path=emergency_load_path()),
        authored_specification_comparator=dict(depth_m=1.8,runtime_s=90.,civil_stages=civil_stages(depth=1.8)),closure=obligations(evidence),
        complete_manufactured_system=False,independent_acceptance=False,
        scope='Provisional drawings/quantities/load paths and inspectable analytical margins; no qualified materials, force maps, full structural verification or physical release',**FLAGS)


def definition():
    """Separate inspectable joint/hardpoint/cassette/bearing detail material regions."""
    a=load();b=a['body'];s=a['stator'];parts=[];groups={}
    def add(identity,size,at,material,group,**kw):
        parts.append(dict(id=identity,size_m=size,at_m=at,material=material,kind='box',
            role='detail-study',basis='provisional connection candidate; material/assembly acceptance open',**kw))
        groups.setdefault(group,[]).append(identity)
    add('hardpoint/solid-laminate',[b['hardpoint_length_m'],b['hardpoint_width_m'],b['hardpoint_solid_laminate_m']],[0,0,0],'gfrp','body-hardpoint')
    holes=[]
    for x in (.075,.275):
        for y in (.035,.215):
            holes.append(dict(axis='z',x_m=x,y_m=y,diameter_m=b['bolt_hole_m']))
            add(f'hardpoint/bolt-{x}-{y}',[.012,.012,.07],[x-.006,y-.006,-.025],'steel','body-hardpoint',kind_override='cylinder')
            add(f'hardpoint/washer-{x}-{y}',[.04,.04,.003],[x-.02,y-.02,.031],'steel','body-hardpoint',kind_override='cylinder',holes=[dict(axis='z',x_m=.02,y_m=.02,diameter_m=.013)])
    parts[0]['holes']=deepcopy(holes)
    add('hardpoint/body-spreader',[.35,.25,.012],[0,0,.018],'aluminium','body-hardpoint',holes=deepcopy(holes))
    add('hardpoint/carrier-box',[.20,.12,.16],[.075,.065,-.16],'aluminium','separate-magnetic-carrier',kind_override='tube',axis=0,wall_m=.008)
    # Developed balanced double-lap service joint; exact joint chemistry/peel and
    # primary body/coupler continuity remain unqualified, not replaced by this lap.
    add('panel-joint/left-skin',[.25,.5,.002],[.7,0,0],'gfrp','panel-service-joint')
    add('panel-joint/right-skin',[.25,.5,.002],[.95,0,0],'gfrp','panel-service-joint')
    for sign in (-1,1):
        add(f'panel-joint/strap-{sign}',[.30,.5,.004],[.8,0,.003 if sign>0 else -.005],'gfrp','panel-service-joint')
        add(f'panel-joint/bond-{sign}',[.30,.5,.001],[.8,0,.002 if sign>0 else -.001],'bond-surface','panel-service-joint')
    for side in (-1,1):
        y=side*.4;add(f'stator/face-{side}/mounting-plate',[2.5,.12,.012],[-1.25,y, .3],'steel','station-cassette-mount')
        for x in (-1.,-.3,.3,1.):
            add(f'stator/face-{side}/bolt-{x}',[.016,.016,.1],[x-.008,y+.06-.008,.26],'steel','station-cassette-mount',kind_override='cylinder')
    add('bearing/fixed-base',[.4,.4,.025],[-.2,1.,0],'steel','fixed-bearing-load-path')
    for x in (-.12,.12):
        for y in (1.05,1.15,1.25,1.35):
            add(f'bearing/anchor-{x}-{y}',[.024,.024,.4],[x-.012,y-.012,-.35],'steel','fixed-bearing-load-path',kind_override='cylinder')
    cp=a['coupler']; rod=cp['rod_diameter_m']; run=cp['rod_effective_length_m']
    add('coupler/compression-guide-envelope',[run,.18,.12],[2.,-.03,.10],'steel','guided-coupler',kind_override='tube',axis=0,wall_m=.008)
    for index,y in enumerate((0.,.09)):
        add(f'coupler/longitudinal-rod-{index}',[rod,rod,run],[2.,y-rod/2,.16-rod/2],'steel','guided-coupler',kind_override='cylinder',cylinder_axis='x')
    for index in range(1,math.ceil(run/cp['lateral_guide_pitch_m'])):
        x=2.+index*cp['lateral_guide_pitch_m']
        add(f'coupler/compression-guide-{index}',[.008,.164,.104],[x,-.022,.108],'steel','guided-coupler',holes=[
            dict(axis='x',y_m=.022,z_m=.052,diameter_m=.031,length_m=.008),
            dict(axis='x',y_m=.112,z_m=.052,diameter_m=.031,length_m=.008)])
    for p in parts:
        if 'kind_override' in p:p['kind']=p.pop('kind_override')
    frame=primary_frame_definition()
    parts.extend(frame['parts']);groups['primary-frame-cut-stock']=[p['id'] for p in frame['parts']]
    return dict(schema='osr-maglev-development-solids/1',id='OSR-PROVISIONAL-MANUFACTURED-CONNECTION-DETAILS',parts=parts,
        construction_stages=[dict(id=k,parts=v) for k,v in groups.items()],
        material_density_assumptions_kg_m3={'gfrp':1900.,'steel':7850.,'aluminium':2700.,'bond-surface':1000.},
        scope='Detail material subassemblies only; no assembled train, real winding, embedded anchor or complete bearing/bolt/thread/washer/nut qualification',
        holds=['hardpoint bolt/washer positions, prying and preload need exact joined-member design','double-lap peel/fire/ageing tests',
            'mount plates/normal force/concrete anchors and true fixed/guided bearing design','negative-control rail clamp cannot be credited as a brake face'],**FLAGS)


def primary_frame_definition():
    a=load();b=a['body'];f=a['frame_remainder'];body=structure.body();L=body['envelope_m']['length'];W=body['envelope_m']['width'];H=body['envelope_m']['height'];parts=[]
    def member(identity,run,w,d,t,at,axis,material='gfrp'):
        size=[w,d,run] if axis==2 else [run,w,d] if axis==0 else [w,run,d]
        parts.append(dict(id='primary-frame/'+identity,size_m=size,at_m=at,material=material,kind='tube',axis=axis,wall_m=t,
            role='primary-member-cut-stock',basis='Untrimmed member cut-stock at provisional assembly datums; exact mitres/node joints open'))
    x_shift=25.
    for side in (-1,1):
        member(f'lower-stringer-{side}',L,b['stringer_outer_width_m'],b['stringer_outer_depth_m'],b['stringer_wall_m'],
            [x_shift-L/2,side*1.1-b['stringer_outer_width_m']/2,.3-b['stringer_outer_depth_m']],0)
        member(f'roof-longitudinal-{side}',L,f['roof_rail_width_m'],f['roof_rail_depth_m'],f['roof_rail_wall_m'],
            [x_shift-L/2,side*(W/2-.04)-.04,.3+H-f['roof_rail_depth_m']],0)
    for i in range(b['floor_ribs']):
        x=x_shift-L/2+(i+1)*L/(b['floor_ribs']+1)
        member(f'floor-rib-{i}',W,b['rib_width_m'],b['rib_depth_m'],b['rib_wall_m'],[x-b['rib_width_m']/2,-W/2,.3-b['rib_depth_m']],1,'aluminium')
    for side in (-1,1):
        x=x_shift+side*L/2-(f['end_frame_width_m'] if side>0 else 0)
        for edge in (-1,1):
            member(f'end-{side}-post-{edge}',H,f['end_frame_width_m'],f['end_frame_depth_m'],f['end_frame_wall_m'],
                [x,edge*W/2-(f['end_frame_depth_m'] if edge>0 else 0),.3],2)
        for level in (0,1):
            member(f'end-{side}-cross-{level}',W,f['end_frame_width_m'],f['end_frame_depth_m'],f['end_frame_wall_m'],
                [x,-W/2,.3+(H if level else 0)-f['end_frame_depth_m']],1)
    for i in range(f['roof_crossmembers']):
        x=x_shift-L/2+(i+1)*L/(f['roof_crossmembers']+1)
        member(f'roof-cross-{i}',W,f['post_width_m'],f['post_depth_m'],f['post_wall_m'],[x-f['post_width_m']/2,-W/2,.3+H-f['post_depth_m']],1)
    for side in (-1,1):
        y=side*W/2-(f['post_depth_m'] if side>0 else 0)
        for i,x in enumerate((-7.5,-2.8,2.8,7.5)):
            member(f'side-{side}-post-{i}',H,f['post_width_m'],f['post_depth_m'],f['post_wall_m'],[x_shift+x,y,.3],2)
        for centre in (-4.5,4.5):
            for edge in (-1,1):
                x=x_shift+centre+edge*.7-(f['door_frame_width_m'] if edge<0 else 0)
                member(f'door-{side}-{centre}-post-{edge}',2.1,f['door_frame_width_m'],f['door_frame_depth_m'],f['door_frame_wall_m'],[x,y,.3],2)
            for level in (0,1):
                member(f'door-{side}-{centre}-header-{level}',1.4,f['door_frame_width_m'],f['door_frame_depth_m'],f['door_frame_wall_m'],
                    [x_shift+centre-.7,y,.3+level*2.1-f['door_frame_depth_m']],0)
    return dict(parts=parts,scope='63 explicitly counted primary/opening frame member cut-stocks in an isolated assembly scene; complete nodes, hardpoints, panel fit-up and buckling/crash/fatigue qualification remain open')


def source_paths():
    paths={Path(__file__),INPUT,OBLIGATIONS,*structure.source_paths(),Path(requirements.__file__),Path(transition.__file__),
        ROOT/'engineering/ferrite_maglev/specification.py',ROOT/'engineering/ferrite_maglev/evacuation.py',
        ROOT/'engineering/ferrite_maglev/data/requirements.json',ROOT/'engineering/ferrite_maglev/data/systems-inventory.json',
        ROOT/'engineering/ferrite_maglev/data/station-powered-specification.json',ROOT/'OpenSourceRail_Station_Powered_Maglev_Design_Specification.docx',
        ROOT/'engineering/ferrite_maglev/system_campaign.py',ROOT/'engineering/ferrite_maglev/system-campaign.toml',
        *configuration.source_paths()}
    paths.update(ROOT/'docs/design-engine/ferrite-maglev'/name/receipt for name,receipt in PACKETS.items() if (ROOT/'docs/design-engine/ferrite-maglev'/name/receipt).is_file())
    return sorted(paths)


def _sources():return {p.relative_to(ROOT).as_posix():sha256(p.read_bytes()).hexdigest() for p in source_paths()}
def _encoded(value):return (json.dumps(value,sort_keys=True,indent=2,allow_nan=False)+'\n').encode()


def _readme(r):
    body=r['body_interfaces'];path=r['emergency_and_curve_load_path'];selected=path['conditional_foundation_candidate']
    side=f"{selected['square_side_m']:g} m" if selected else 'No passing candidate'
    return ('# Provisional manufactured design dossier\n\n'
        'This packet adds calculated panel/rib/stringer/hardpoint/lap and cassette/bearing connection candidates, '
        'prestress/handling screens and a spatially allocated emergency-brake/curve load path. All material limits are unqualified project assumptions.\n\n'
        '[Complete dossier, obligations, margins and source evidence](dossier.json.gz) · [Partial connection material geometry](detail-definition.json) · [Receipt](manifest.json)\n\n'
        f"Primary static/detail/emergency cases use {r['primary_mass_case']['car_mass_kg']/1000:.1f} t AW3 per car ({r['primary_mass_case']['train_mass_kg']/1000:.1f} t six-car train), including the 50kWh pack. Tare is a {r['primary_mass_case']['tare_kg_per_car']/1000:.1f} t hypothesis. The 30kWh/26.2t case remains separately retained. The exact heavier-case brake energy/thermal allocation is used in its body, bearing, column, foundation and growth-reserve screens. No measured mass/CG or physical brake proof is inferred.\n\n"
        f"The floor comparison retains unreinforced-span/thin-rib failures and a stronger rib-supported candidate. The counted primary frame family is {r['primary_frame_families']['primary_family_mass_kg']:.1f} kg, consuming {r['primary_frame_families']['frame_budget_overrun_kg']:.1f} kg beyond the existing800kg allowance from the growth reserve; joined-member qualification and complete hardware remain open. "
        f"The physical bearing proposal fixes one end of each25m beam and guides the other. Worst translation places {path['span_pad_occupancy']['maximum_units_per_span']} brake units in one span. Under declared load/soil assumptions the first no-tension/bearing footing candidate is {side} square; this is not geotechnical selection.\n\n"
        'The existing unstiffened reaction plate is retained as a failed brake-clamp negative control. A dedicated reaction box is a separate unqualified alternative; anchors, heat, wear, magnetic coexistence and complete emergency stopping remain open. '
        'All100 supplied specification obligations, current179 applicable requirements and current system responsibilities map to concrete deliverables and identified missing evidence. Mapping does not complete them. No manufacturing, operating or physical release is claimed.\n').encode()


def publish(output=OUTPUT):
    output=Path(output)
    if output.is_symlink() or (output.exists() and any(p.name not in FILES|{'manifest.json'} or p.is_symlink() or not p.is_file() for p in output.iterdir())):
        raise ValueError('ordinary owned dossier packet required')
    sources=_sources();r=study();r['source_sha256']=sources
    payload={'dossier.json.gz':gzip.compress(_encoded(r),mtime=0),'detail-definition.json':_encoded(definition()),'README.md':_readme(r)}
    if _sources()!=sources:raise ValueError('dossier sources changed')
    manifest=dict(schema='osr-manufactured-design-publication/1',source_sha256=sources,
        files_sha256={name:sha256(raw).hexdigest() for name,raw in payload.items()},release_authority=False,**FLAGS)
    output.mkdir(parents=True,exist_ok=True)
    for name,raw in {**payload,'manifest.json':_encoded(manifest)}.items():
        if len(raw)>MAX_BYTES:raise ValueError('bounded dossier payload required')
        temp=output/(name+'.pending')
        if temp.is_symlink():raise ValueError('ordinary dossier temporary file required')
        with temp.open('wb') as handle:handle.write(raw);handle.flush();os.fsync(handle.fileno())
        temp.replace(output/name)
    return verify(output)


def verify(output=OUTPUT):
    output=Path(output)
    if output.is_symlink() or not output.is_dir() or {p.name for p in output.iterdir()}!=FILES|{'manifest.json'}:
        raise ValueError('exact dossier inventory required')
    payload={}
    for name in FILES|{'manifest.json'}:
        path=output/name
        if path.is_symlink() or not path.is_file() or path.stat().st_size>MAX_BYTES:raise ValueError('bounded ordinary dossier file required')
        payload[name]=path.read_bytes()
    manifest=json.loads(payload['manifest.json']);sources=_sources()
    if manifest.get('source_sha256')!=sources:raise ValueError('stale dossier sources')
    if manifest.get('files_sha256')!={name:sha256(payload[name]).hexdigest() for name in FILES}:raise ValueError('dossier payload differs')
    with gzip.open(output/'dossier.json.gz','rb') as stream:raw=stream.read(MAX_BYTES+1)
    if len(raw)>MAX_BYTES:raise ValueError('bounded decompressed dossier required')
    expected=study();expected['source_sha256']=sources
    if json.loads(raw)!=expected or json.loads(payload['detail-definition.json'])!=definition() or payload['README.md']!=_readme(expected):
        raise ValueError('dossier differs from calculated details/obligations')
    if manifest.get('release_authority') is not False or any(manifest.get(k) is not False for k in FLAGS):raise ValueError('dossier release remains open')
    return dict(state='verified-provisional-detail-records',requirements=expected['closure']['requirement_count'],
        systems=expected['closure']['system_count'],detail_parts=len(definition()['parts']),accepted_requirements=0,**FLAGS)
