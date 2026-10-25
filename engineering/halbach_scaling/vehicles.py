"""Counted lighter-car proposals with disjoint removals and module-mass feedback.

The new six-cell lower rails are analytical extrusion proposals, not a qualified
carbody. Every metal wall/web is counted. Local member screens do not establish
global body, bracing, joints, crash, fatigue or installation suitability.
"""
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
import json
import math
from pathlib import Path

from engineering.vehicle_optimisation import equipment, hvac, ledger
from engineering.ferrite_maglev import candidate_magnetics as canonical

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = 'osr-halbach-scaling-vehicle/1'
FLAGS = dict(physical_accepted=False, engineering_accepted=False,
             configuration_adopted=False, installed_mass_complete=False,
             manufacturing_release=False)
G = 9.80665
RESERVE = 1.3
UNCLOSED_MASS_KG = (0., 1000., 2000., 3000.)
MATERIAL = dict(id='EN-AW-6082-T6-proposal', alloy='EN-AW-6082', temper='T6',
    density_kg_m3=2710., young_Pa=69e9, proof_strength_Pa=250e6,
    poisson_ratio=.33, HAZ_retention_hypothesis=.5, safety_factor=1.5,
    source=equipment.HYDRO_6082, reviewed_date='2026-10-25',
    basis='Hydro 6082 Rev.4 03/2023: hollow T6 profile <=5 mm minimum Rp0.2 250 MPa; density 2.71 g/cm3, nominal E 70 GPa. Conservative E 69 GPa retained. Batch, extrusion geometry, joints and heat effects are unqualified.',
    material_qualified=False)


def encoded(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)+'\n').encode()


def identity(value):
    return sha256(encoded(value)).hexdigest()


def sources(root=ROOT):
    root = Path(root).resolve()
    records = equipment.sources(root) | hvac.source_inputs(root)['local_sha256']
    for module in (equipment, hvac, ledger, canonical):
        path = Path(module.__file__).resolve()
        name = path.relative_to(path.parents[2]).as_posix()
        actual = sha256(path.read_bytes()).hexdigest()
        if name in records and records[name] != actual:
            raise ValueError('executing and retained vehicle sources disagree: '+name)
        records[name] = actual
    records[Path(__file__).resolve().relative_to(ROOT).as_posix()] = sha256(Path(__file__).read_bytes()).hexdigest()
    return dict(sorted(records.items()))


def _positive(value, name):
    if type(value) not in (float, int) or not math.isfinite(value) or value <= 0:
        raise ValueError('finite positive '+name+' required')
    return float(value)


def extrusion_section(width_m, height_m, wall_m, *, web_m=None):
    """Disjoint rectangles for RHS or six-cell RHS; exact centroidal properties.

    Local y/z coordinates run from zero to the profile's outer width/height.
    One vertical and two horizontal integral webs make six cells. Crossings
    are partitioned rather than counted twice. Plate buckling treats those
    integral intersections as supports; their manufacturing/joint quality is
    not established by this necessary calculation.
    """
    b, h, t = (_positive(v, n) for v, n in zip((width_m, height_m, wall_m), ('width', 'height', 'wall')))
    if 2*t >= min(b, h):
        raise ValueError('profile requires a nonempty bore')
    ib, ih = b-2*t, h-2*t
    rectangles = [dict(id='left-wall', y=0., z=0., width=t, height=h),
                  dict(id='right-wall', y=b-t, z=0., width=t, height=h),
                  dict(id='bottom-wall', y=t, z=0., width=ib, height=t),
                  dict(id='top-wall', y=t, z=h-t, width=ib, height=t)]
    plates = [(ib, t), (ih, t)]
    if web_m is not None:
        w = _positive(web_m, 'web thickness')
        if w >= min(ib, ih/3):
            raise ValueError('webs must leave six open cells')
        rectangles.append(dict(id='vertical-web', y=(b-w)/2, z=t, width=w, height=ih))
        half = (ib-w)/2
        for index, z in enumerate((t+ih/3-w/2, t+2*ih/3-w/2)):
            rectangles.extend([dict(id=f'horizontal-web-{index}-left', y=t, z=z, width=half, height=w),
                               dict(id=f'horizontal-web-{index}-right', y=(b+w)/2, z=z, width=half, height=w)])
        longest_vertical = ih/3-w/2
        plates = [(half, t), (longest_vertical, t), (half, w), (longest_vertical, w)]
    area = math.fsum(r['width']*r['height'] for r in rectangles)
    cy = math.fsum(r['width']*r['height']*(r['y']+r['width']/2) for r in rectangles)/area
    cz = math.fsum(r['width']*r['height']*(r['z']+r['height']/2) for r in rectangles)/area
    iy = math.fsum(r['width']*r['height']**3/12+r['width']*r['height']*(r['z']+r['height']/2-cz)**2 for r in rectangles)
    iz = math.fsum(r['height']*r['width']**3/12+r['width']*r['height']*(r['y']+r['width']/2-cy)**2 for r in rectangles)
    E, nu = MATERIAL['young_Pa'], MATERIAL['poisson_ratio']
    critical = min(4*math.pi**2*E/(12*(1-nu**2))*(thickness/span)**2 for span, thickness in plates)
    return dict(width_m=b, height_m=h, wall_m=t, web_m=web_m, cell_count=1 if web_m is None else 6,
                rectangles=rectangles, area_m2=area, centroid_yz_m=[cy, cz],
                I_strong_m4=iy, I_weak_m4=iz, Z_vertical_m3=iy/max(cz, h-cz),
                elastic_local_plate_critical_Pa=critical,
                local_plate_basis='Simply supported long plates, k=4, integral web intersections; local necessary bound only')


def _frame_stock_member(old, section):
    axis = old['axis'];cross = [k for k in range(3) if k != axis]
    at = list(old['at_m'])
    # Keep the old upper/outside datum, allowing explicitly unqualified growth
    # into the underfloor/inside envelope rather than moving magnetic mounts.
    if axis == 0:
        at[2] += old['depth_m']-section['height_m']
        if at[1] > 0:
            at[1] += old['width_m']-section['width_m']
    rows = []
    for rectangle in section['rectangles']:
        size = [0., 0., 0.];position = list(at)
        size[axis] = old['length_m'];size[cross[0]] = rectangle['width'];size[cross[1]] = rectangle['height']
        position[cross[0]] += rectangle['y'];position[cross[1]] += rectangle['z']
        volume = math.prod(size)
        rows.append(dict(id='extrusion/'+old['id']+'/'+rectangle['id'], engineering_part_id='extrusion/'+old['id'],
            kind='material-prism-in-one-extrusion', quantity=1, size_m=size, at_m=position,
            volume_m3_each=volume, total_volume_m3=volume, density_kg_m3=MATERIAL['density_kg_m3'],
            material_id=MATERIAL['id'], unit_mass_kg=volume*MATERIAL['density_kg_m3'],
            total_mass_kg=volume*MATERIAL['density_kg_m3'], status='counted-material',
            manufacturing_basis='Prisms partition one hollow extruded member; not separate assembly pieces',
            drilling_basis='Gross undrilled stock. Effective sections, holes, splices and fatigue remain unqualified'))
    return rows


def _frame(kind, root):
    old = equipment._members(root)
    if kind == 'retained-frame':
        return None
    dimensions = {'6082-six-cell-compact': (.20, .32, .003, .002),
                  '6082-six-cell-deep': (.22, .36, .003, .002)}
    if kind not in dimensions:
        raise ValueError('bounded frame family required')
    members, stock = [], []
    for previous in old:
        name = previous['id']
        if 'lower-stringer' in name:
            b, h, t, w = dimensions[kind]
            section = extrusion_section(b, h, t, web_m=w)
        elif 'roof-longitudinal' in name:
            section = extrusion_section(.10, .25, .0025)
        else:
            b, h = previous['width_m'], previous['depth_m']
            t = equipment.same_stiffness_wall(b, h, previous['reference_EI_N_m2'], min_wall_m=.0015)
            section = extrusion_section(b, h, t)
        if max(section['wall_m'], section['web_m'] or 0.) > .005:
            raise ValueError('6082 T6 <=5 mm property screen exceeded')
        proposed = [MATERIAL['young_Pa']*section[k] for k in ('I_strong_m4', 'I_weak_m4')]
        members.append(dict(id=name, axis=previous['axis'], length_m=previous['length_m'],
            section=section, reference_EI_N_m2=previous['reference_EI_N_m2'], proposed_EI_N_m2=proposed,
            stiffness_necessary_pass=all(a >= b*(1-1e-9) for a, b in zip(proposed, previous['reference_EI_N_m2']))))
        stock.extend(_frame_stock_member(previous, section))
    # Reuse the prior counted end-detail inventory. Only its 6082 18 mm
    # spreader option is retained; member profiles above are newly generated.
    joint_reference = next(c for c in equipment.chassis_candidates(root=root) if c['id']=='6082-T6-deep-stringers')
    for original in joint_reference['stock_parts']:
        if original['id'].startswith('extrusion/'):
            continue
        part = deepcopy(original)
        part['source_detail_id'] = 'equipment/6082-T6-deep-stringers/'+part['id']
        part['material_id'] = ('unqualified-GFRP-isolator' if 'GFRP' in part['id'] else
            'unqualified-bond-stock' if 'bond' in part['id'] else
            'unqualified-steel-joint-stock' if part['density_kg_m3']==7850. else
            'unqualified-aluminium-joint-stock')
        part['installed_position_m'] = None
        stock.append(part)
    value = dict(id=kind, material=deepcopy(MATERIAL), members=members, stock_parts=stock,
        removed_stock_ids=joint_reference['removed_stock_ids'],
        removed_counted_frame_kg=joint_reference['removed_counted_frame_kg'],
        counted_material_mass_kg=math.fsum(p['total_mass_kg'] for p in stock),
        engineering_member_count=65, lower_rail_cell_count=6, member_end_count=130,
        joint_bolt_count=520, roof_spreader_count=24, roof_spreader_thickness_m=.018,
        budget=dict(max_section_families=2, maximum_seconds_per_trial=300),
        unknown_installed_inventory=[dict(id='frame/global-shear-torsion-crash-fatigue-and-joints', mass_kg=None),
            dict(id='frame/actual-lateral-restraint-and-brace-load-path', mass_kg=None),
            dict(id='frame/deeper-rail-floor-door-equipment-packing', mass_kg=None),
            dict(id='frame/corrosion-extrusion-splices-manufacturing-tolerances', mass_kg=None)],
        installed_mass_kg=None, installed_CG_m=None, installed_inertia_kg_m2=None,
        hold='Section stiffness and local loads do not qualify the body, bracing, attachments, crash or fatigue', **FLAGS)
    value['frame_id'] = identity(dict(kind=kind, alloy=MATERIAL['alloy'], temper=MATERIAL['temper'],
        members=[dict(id=m['id'], axis=m['axis'], length_m=m['length_m'],
            profile={k:m['section'][k] for k in ('width_m','height_m','wall_m','web_m','cell_count')}) for m in members],
        stock_parts=[{k:deepcopy(p[k]) for k in ('id','kind','quantity','size_m','at_m','volume_m3_each','material_id') if k in p} for p in stock]))
    return value


def structure_screen(frame, aw3_kg):
    mass = _positive(aw3_kg, 'AW3 mass')
    if frame is None:
        return dict(state='unknown-retained-body-load-path', reference_aw3_kg=mass,
                    member_level_necessary_pass=None, global_body_qualified=False, **FLAGS)
    E = frame['material']['young_Pa'];allow = frame['material']['proof_strength_Pa']*.5/1.5
    force = mass*G*RESERVE/24;pitch = 17/12
    roof = next(q for q in frame['members'] if 'roof-longitudinal' in q['id'])['section']
    rail = next(q for q in frame['members'] if 'lower-stringer' in q['id'])['section']
    sigma = force*pitch/(4*roof['Z_vertical_m3']);deflection = force*pitch**3/(48*E*roof['I_strong_m4'])
    plate = 6*(force*.08/2)/(.22*.018**2)
    compression = 250000.;axial = compression/rail['area_m2']
    critical = rail['elastic_local_plate_critical_Pa']
    euler_17 = math.pi**2*E*min(rail['I_strong_m4'], rail['I_weak_m4'])/17**2
    euler_2 = math.pi**2*E*min(rail['I_strong_m4'], rail['I_weak_m4'])/2**2
    matched = all(q['stiffness_necessary_pass'] for q in frame['members'])
    passed = matched and sigma <= allow and deflection <= .002 and plate <= 80e6 and axial <= min(allow, critical)
    return dict(state='member-screens-pass-global-body-held' if passed else 'member-necessary-screen-fail',
        reference_aw3_kg=mass, roof_force_N_per_module=force, roof_pitch_m=pitch,
        matched_both_axis_section_stiffness=matched, roof_stress_Pa=sigma, roof_deflection_m=deflection,
        roof_HAZ_allowable_Pa=allow, spreader_stress_Pa=plate, spreader_allowable_Pa=80e6,
        spreader_material_basis='Retained unqualified 80 MPa plate-detail hypothesis, not 6082 certificate',
        coupler_compression_N_per_rail=compression, rail_axial_stress_Pa=axial,
        rail_local_plate_critical_Pa=critical, rail_Euler_17m_N=euler_17, rail_Euler_assumed_2m_N=euler_2,
        full_length_unbraced_Euler_screen_pass=compression <= euler_17,
        hypothetical_2m_braced_Euler_screen_pass=compression <= euler_2,
        actual_bracing_qualified=False, global_body_qualified=False,
        member_level_necessary_pass=passed, **FLAGS)


def _system_modes():
    fitout = next(q for q in equipment.equipment_candidates() if q['id']=='aluminium-sandwich-ES2-reference/solar-laminated-6.76mm')
    climates = {q['id']:q for q in hvac.candidates()}
    return [dict(id='retained-equipment', fitout=None, climate=None),
            *[dict(id=key, fitout=fitout, climate=climates[key]) for key in
              ('bus-ul700-electric-two','bus-ul500-electric-three','bus-ul700-electric-three')]]


def _changes(frame, mode, root):
    bindings = sources(root);rows = []
    if frame is not None:
        rows.append(dict(id='frame', removal_kind='counted-stock', removed_part_ids=frame['removed_stock_ids'],
            removed_kg_per_car=frame['removed_counted_frame_kg'], added_known_kg_per_car=frame['counted_material_mass_kg'],
            source_bindings=bindings, basis='Replace exact 65-member stock only; retain GFRP panels, collectors, retained hardpoints and other equipment',
            unknown_installed_inventory=frame['unknown_installed_inventory']))
    fitout, climate = mode['fitout'], mode['climate']
    if fitout is not None:
        audit = equipment.allocation_audit(root=root)
        rows.append(dict(id='doors-windows', removal_kind='inherited-allocation',
            removed_allocation_ids=[r['id'] for r in audit['eligible_removals']],
            removed_kg_per_car=math.fsum(r['mass_kg'] for r in audit['eligible_removals']),
            added_known_kg_per_car=fitout['counted_material_mass_kg']+fitout['supplier_mechanism_reference_mass_kg'],
            source_bindings=bindings, basis='Remove ancestor 500 kg doors and 500 kg fixed glazing allowances once; add counted stock and separate supplier mechanism references',
            unknown_installed_inventory=fitout['unknown_installed_inventory']))
    if climate is not None:
        trace = hvac.allocation_trace(root)
        band = climate['package_hardware_mass_range_kg_per_car']
        if band is None or band[0] != band[1]:
            raise ValueError('one explicit hardware-mass point required')
        rows.append(dict(id='hvac', removal_kind='inherited-allocation', removed_allocation_ids=['hvac'],
            removed_kg_per_car=trace['mass_kg'], added_known_kg_per_car=band[0],
            source_bindings=bindings, basis='Remove single unweighed 800 kg HVAC ancestor allowance; add catalogue hardware only, never an installed saving',
            unknown_installed_inventory=[dict(id='hvac/'+str(item), mass_kg=None) for item in climate['unknown_items']]))
    return rows


def _thermal(mode):
    fitout, climate = mode['fitout'], mode['climate']
    if fitout is None:
        return dict(complete_equipment_rating_known=False, comparison=None,
                    reason='Retained allowance has no correlated package capacity/power map', **FLAGS)
    interface = fitout['hvac_interface'];door = fitout['door']
    common = dict(glazing_m2=interface['total_glazing_area_m2'], solar_factor=interface['solar_factor_g'],
                  glazing_U_W_m2K=interface['U_W_m2K'], door_width_m=door['door_width_m'], door_height_m=door['door_height_m'])
    loads = [hvac.heat_load(hvac.default_scenario(name='AW2-50C-matched', **common)),
             hvac.heat_load(hvac.default_scenario(name='AW3-50C-humid-doors60s-matched', passengers=160,
                 outdoor_RH=.30, door_open_s=60., **common))]
    return dict(complete_equipment_rating_known=False, loads=loads,
        comparisons=[hvac.assess(climate, load) for load in loads],
        passenger_ventilation_reduced=False, thermal_load_depends_on_body_mass=False,
        complete_installed_hvac_mass_kg=None, complete_electric_input_kW=None, **FLAGS)


@lru_cache(maxsize=8)
def _variants(root_name, source_key):
    root = Path(root_name);bindings = sources(root)
    if source_key != identity(bindings):
        raise ValueError('vehicle source identity changed before generation')
    base = canonical.definition();result = []
    for kind in ('retained-frame','6082-six-cell-compact','6082-six-cell-deep'):
        frame = _frame(kind, root)
        for mode in _system_modes():
            changes = _changes(frame, mode, root)
            provisional = ledger.compose(base['controlled_tare_kg'], changes,
                unresolved=[dict(id='retained/unlocated-equipment-and-mounting-locations', mass_kg=None)])
            fitout = mode['fitout']
            physical_fitout = None if fitout is None else dict(id=fitout['id'],
                door_geometry={k:fitout['door'][k] for k in ('door_count','door_width_m','door_height_m','leaves_per_door')},
                glazing_id=fitout['glazing']['id'],
                stock_parts=[{k:deepcopy(p[k]) for k in ('id','kind','quantity','volume_m3_each','area_m2','thickness_m') if k in p}
                             for p in fitout['stock_parts']])
            architecture = dict(frame='retained-frame' if frame is None else frame['frame_id'],
                equipment=mode['id'], fitout=physical_fitout,
                HVAC=None if mode['climate'] is None else dict(id=mode['climate']['id'], units=mode['climate']['units_per_car']),
                service=deepcopy(ledger.SERVICE))
            value = dict(schema=SCHEMA, name=kind+'/'+mode['id'], physical_definition=architecture,
                candidate_id=identity(architecture), source_sha256=bindings, source_configuration_sha256=base['configuration_sha256'],
                base_empty_kg_per_car=base['controlled_tare_kg'], base_canonical_module_mass_kg=base['module']['mass_kg'],
                frame=frame, equipment=deepcopy(mode['fitout']), HVAC=deepcopy(mode['climate']),
                replacement_changes=changes, nonmagnetic_replacement_delta_kg=provisional['comparison_empty_kg_per_car']-base['controlled_tare_kg'],
                thermal=_thermal(mode), service=deepcopy(ledger.SERVICE),
                unclosed_mass_sensitivity_kg_per_car=list(UNCLOSED_MASS_KG),
                unknown_installed_inventory=provisional['unknown_installed_inventory'],
                installed_empty_kg_per_car=None, installed_aw3_kg_per_car=None, cg_m=None, inertia_kg_m2=None,
                complete_installed_cost=None,
                scope='Body/equipment proposal before support replacement. Counted material and supplier reference values replace disjoint old accounts; no installed mass or whole-body acceptance.', **FLAGS)
            value['bundle_sha256'] = identity(value);result.append(encoded(value))
    if sources(root) != bindings:
        raise ValueError('vehicle sources changed during generation')
    return tuple(result)


def variants(root=ROOT):
    """Twelve named physical alternatives; independent of magnetic evaluations."""
    root = Path(root).resolve()
    return [json.loads(raw) for raw in _variants(str(root), identity(sources(root)))]


def validate(value, root=ROOT):
    if not isinstance(value, dict) or value.get('schema') != SCHEMA:
        raise ValueError('supported vehicle bundle required')
    name = value.get('name')
    expected = next((q for q in variants(root) if q['name']==name), None)
    if expected is None or value != expected:
        raise ValueError('unsupported or modified vehicle geometry/material/accounting')
    return value


def compose(vehicle, magnetic_bundle, modules=24, *, root=ROOT):
    """Reclose comparison mass after actual magnetic stock, without force credit.

    The 0/1/2/3 t sensitivity is explicitly additional UNWEIGHED equipment mass,
    not hardware, accepted mass or a probability bound. HVAC external bands are
    retained as their original named scenarios and are not added a second time.
    """
    validate(vehicle, root)
    if type(modules) is not int or modules != 24:
        raise ValueError('unchanged 24-module support layout required')
    from . import candidates
    candidates.validate(magnetic_bundle, root)
    stock = magnetic_bundle['stock'];known = _positive(stock['train_known_mass_kg_per_module'], 'magnetic module stock')
    counted = math.fsum(q['mass_kg'] for q in magnetic_bundle['stock_parts'] if q['group']=='train')
    if not math.isclose(known, counted, rel_tol=1e-12, abs_tol=1e-8):
        raise ValueError('magnetic module stock subtotal differs from exact train inventory')
    changes = [dict(id='support', removal_kind='counted-stock',
        removed_part_ids=[f'a79/support-module/{i}' for i in range(modules)],
        removed_kg_per_car=modules*vehicle['base_canonical_module_mass_kg'], added_known_kg_per_car=modules*known,
        source_bindings=vehicle['source_sha256'], basis='Replace only the 24 exact canonical support modules; propulsion and all other old equipment remain',
        unknown_installed_inventory=magnetic_bundle['unknown_installed_inventory']), *deepcopy(vehicle['replacement_changes'])]
    mass = ledger.compose(vehicle['base_empty_kg_per_car'], changes,
        unresolved=[dict(id='retained/unlocated-equipment-and-mounting-locations', mass_kg=None)])
    points = []
    for extra in UNCLOSED_MASS_KG:
        aw3 = mass['comparison_aw3_kg_per_car']+extra
        points.append(dict(unclosed_additional_mass_kg_per_car=extra, comparison_aw3_kg_per_car=aw3,
            comparison_train_aw3_kg=6*aw3, required_force_N_per_module=aw3*G*RESERVE/modules,
            reserve_factor=RESERVE, structure=structure_screen(vehicle['frame'], aw3),
            actual_installed_mass_known=False, **FLAGS))
    climate = vehicle['HVAC']
    band = None if climate is None else [x-climate['package_hardware_mass_range_kg_per_car'][i]
        for i, x in enumerate(climate['provisional_installed_mass_scenario_kg'])]
    value = dict(schema='osr-halbach-scaling-composition/1', body_candidate_id=vehicle['candidate_id'],
        magnet_component_id=magnetic_bundle['physical_id'],
        candidate_id=identity(dict(body=vehicle['physical_definition'], magnet=magnetic_bundle['physical_id'], modules=modules)),
        source_sha256=vehicle['source_sha256'], module_count_per_car=modules,
        magnetic_known_stock_kg_per_module=known, magnetic_known_stock_kg_per_car=modules*known,
        comparison_empty_kg_per_car=mass['comparison_empty_kg_per_car'],
        comparison_aw3_kg_per_car=mass['comparison_aw3_kg_per_car'],
        accounted_comparison_floor_aw3_kg_per_car=mass['comparison_aw3_kg_per_car'],
        comparison_floor_basis='Lower end of this retained-allocation accounting model, not a rigorous lower bound on actual equipped mass',
        comparison_train_aw3_kg=mass['comparison_train_aw3_kg'], ledger=mass,
        support_requirements_by_unclosed_mass=points,
        HVAC_external_installation_scenario_band_kg=band,
        unclosed_mass_basis='0/1/2/3 t additional unknown-mass sensitivity, not a measured inventory or confidence bound. It encompasses unresolved new installation, including HVAC external interfaces; do not add that HVAC band again.',
        thermal=vehicle['thermal'], unknown_installed_inventory=mass['unknown_installed_inventory'],
        installed_empty_kg_per_car=None, installed_aw3_kg_per_car=None, cg_m=None, inertia_kg_m2=None,
        complete_installed_cost=None, total_equipped_mass_bounded=False,
        service=deepcopy(ledger.SERVICE), overall_structure_qualified=False,
        integrated_candidate_eligible=False, **FLAGS)
    value['evaluation_id'] = identity(value)
    return value
