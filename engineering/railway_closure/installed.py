"""Transfer one counted body and explicit drive/interface additions to axle loads.

This is a positive mass/placement hypothesis, not admission of a motor into the
passive bogie. Supplier housings, mounts and clashes remain a separate gate.
"""
from copy import deepcopy
from math import fsum, isfinite
from pathlib import Path
import json

from engineering.station_rail.common import identity, digest
from engineering.station_pair import coordinator as pair
from engineering.station_cycle import design as recovery
from . import ROOT, FLAGS
from .service import brief, terminal_geometry

G = 9.80665
CASES = ('low', 'base', 'high')


def seal(value):
    value['evaluation_id'] = identity(value)
    return value


def _validate_body(body, root):
    if body.get('schema') != 'osr-vehicle-installation/1':
        raise ValueError('Counted installed body packet required')
    if body.get('candidate_id') != identity(body['physical_definition']):
        raise ValueError('Mixed physical body identity')
    if body.get('evaluation_id') != identity({k: v for k, v in body.items() if k != 'evaluation_id'}):
        raise ValueError('Body evaluation is not sealed')
    for name, expected in body['source_sha256'].items():
        p = Path(name)
        if p.is_absolute() or '..' in p.parts or digest(Path(root) / p) != expected:
            raise ValueError('Body upstream source changed: ' + name)


def integrate(body, *, with_recovery=True, root=ROOT):
    """Keep static force and first moment exact; apply no dynamic factor here."""
    root = Path(root)
    _validate_body(body, root)
    parent = next(d for d in recovery.variants(root)[3]
                  if d['variant']['family'] == 'powered-wheel'
                  and d['technology'] == ('hydraulic' if with_recovery else None)
                  and (not with_recovery or d['capacity_j'] == 4e6))
    v = deepcopy(parent['variant'])
    v['geometry']['passive_secondary_retained']=any(p['assembly_id']=='services/secondary' for p in body['parts'])
    electrical_policy=json.loads((root/'engineering/railway_closure/electrical-policy.json').read_bytes())
    supply_policy=json.loads((root/'engineering/railway_closure/supply-policy.json').read_bytes())
    v['grid_power_limit_W_per_train']=supply_policy['grid_power_limit_W_per_train']
    v['inventory'].append(dict(id='auxiliary-DC-DC-partition',quantity=6,location='train body proposed BOP zones',
        rating_kw_each=electrical_policy['onboard_converter_rating_kw_per_car'],
        mass_kg_each=dict(zip(CASES,electrical_policy['onboard_converter_mass_kg'])),
        included_in='inverter-cooling-mounting-collector-reserve',additional_mass_not_added=True,
        physical_shape_and_ratings_verified=False))
    terminal = terminal_geometry(brief(root))
    # One driven axle per bogie: supplier shaft/mount geometry remains unknown.
    driven = list(range(0, 24, 2))
    physical = dict(
        schema='osr-installed-railway-research/1', body_candidate_id=body['candidate_id'],
        propulsion_parent_candidate_id=v['candidate_id'], family='powered-wheel',
        drive_geometry=v['geometry'], drive_inventory=v['inventory'],
        station_energy_module=v['physical_definition'].get('station_energy_module'),
        auxiliary_feed=dict(continuous_conductor_feed=True,onboard_converter_count=6,
            converter_rating_kw_each=electrical_policy['onboard_converter_rating_kw_per_car'],
            converter_mass_is_partition_of_existing_BOP=True,traction_battery=False,
            battery_modules_and_enclosures='Exact installed body component list; no uncounted Type4 substitution'),
        line_conductor=dict(material='aluminium procurement hypothesis',cross_section_m2=supply_policy['aluminium_conductor_area_m2'],
            density_kg_m3_hypothesis=supply_policy['conductor_density_kg_m3_hypothesis'],
            insulators_brackets_guards_mass_kg_track_m_hypothesis=supply_policy['insulators_brackets_guards_mass_kg_track_m_hypothesis'],
            lateral_offset_from_track_centre_m=supply_policy['conductor_lateral_offset_from_track_centre_m'],
            nominal_voltage_V=supply_policy['nominal_feed_V'],track_length_m=terminal['track_quantities']['total_track_m'],
            grid_power_limit_W_per_train=v['grid_power_limit_W_per_train'],
            rail_return_in_civil_inventory=True,protection_and_ampacity_verified=False),
        driven_axle_indices=driven,
        placements=dict(motor_and_gear='796 kg at each declared driven axle; proposed centre z=.55 m, y=0',
                        drive_reserve='Equal six-car share at car centre, z=.70 m, y=0; envelope not admitted',
                        recovery_interface='Equal six-car share at car centre, z=.45 m, y=0; attachment design open'),
        terminal_geometry_id=terminal['geometry_id'],
        control_hardware='Existing independent grid drive and service/emergency brakes retained; recovery replaces grid effort only',
        selected_reference_changed=False)
    cid = identity(physical)
    v['parent_candidate_id'] = v['candidate_id']
    v['candidate_id'] = cid
    v['physical_definition'] = physical
    v['body_candidate_id'] = body['candidate_id']
    source = dict(body['source_sha256'])
    source.update(v['source_sha256'])
    source.update(recovery.sources(root))
    for n in ('engineering/railway_closure/installed.py', 'engineering/railway_closure/brief.json',
              'engineering/railway_closure/service.py','engineering/railway_closure/electrical-policy.json',
              'engineering/railway_closure/supply-policy.json'):
        source[n] = digest(root / n)
    rows = []
    for r in body['mass_scenarios']:
        c = r['case']
        axles = deepcopy(r['axles'])
        if len(axles) != 24:
            raise ValueError('This drive revision requires exactly 24 named axles')
        known = 12 * (486. + 310.)
        interface = recovery.policy(root)['interface_reserve_kg_per_train'][c] if with_recovery else 0.
        reserve = v['onboard_added_mass_kg'][c] - known - interface
        if reserve <= 0:
            raise ValueError('Missing drive balance-of-plant mass cannot become zero')
        additions = [(796., [axles[i]['x_m'], 0., .55], [i]) for i in driven]
        for car in range(6):
            cx = 8.5 + 17.65 * car
            additions.extend([(reserve / 6, [cx, 0., .70], list(range(4*car, 4*car+4))),
                              (interface / 6, [cx, 0., .45], list(range(4*car, 4*car+4)))])
        for mass, position, indices in additions:
            # Centre-of-car additions split equally over symmetric supports;
            # axle-mounted additions pass straight into their named axle.
            for i in indices:
                axles[i]['vertical_force_N'] += mass * G / len(indices)
        total = r['train_mass_kg'] + fsum(m for m, _, _ in additions)
        cg = [(r['train_mass_kg'] * r['CG_m'][a] + fsum(m*x[a] for m, x, _ in additions)) / total for a in range(3)]
        force_residual = fsum(a['vertical_force_N'] for a in axles) - total * G
        moment_residual = fsum(a['vertical_force_N'] * a['x_m'] for a in axles) - total * G * cg[0]
        if not all(isfinite(x) for x in [total, *cg]) or abs(force_residual) > 1e-7 or abs(moment_residual) > 1e-6:
            raise ValueError('Added drive/interface masses do not conserve support transfer')
        rows.append(dict(name=r['name'], train_mass_kg=total, CG_m=cg, axles=axles,
                         lateral_acceleration_m_s2=r['lateral_acceleration_m_s2'],
                         force_residual_N=force_residual, moment_residual_Nm=moment_residual,
                         body_mass_kg=r['train_mass_kg'], added_known_drive_kg=known,
                         added_drive_reserve_kg=reserve, added_capture_interface_kg=interface,
                         driven_static_axle_force_N=fsum(axles[i]['vertical_force_N'] for i in driven)))
    result = dict(schema='osr-integrated-installed-mass/1', candidate_id=cid,
                  physical_definition=physical, vehicle_candidate_id=body['candidate_id'],
                  body_evaluation_id=body['evaluation_id'], variant=v, recovery_design=dict(parent, variant=v),
                  terminal_geometry=terminal, load_cases=rows, source_sha256=source,
                  packaging_screen='hold: proposed powered bogie motor envelopes intersect retained passive frame; actual mount revision required',
                  installed_mass_complete=False, **FLAGS)
    return seal(result)


def axle_packet(installed):
    if installed['evaluation_id'] != identity({k: v for k, v in installed.items() if k != 'evaluation_id'}):
        raise ValueError('Sealed integrated mass required')
    fields = ('name', 'train_mass_kg', 'axles', 'CG_m', 'lateral_acceleration_m_s2')
    return seal(dict(schema='osr-pilot-axle-loads/1', candidate_id=installed['candidate_id'],
                     vehicle_candidate_id=installed['vehicle_candidate_id'],
                     mass_evaluation_id=installed['evaluation_id'],
                     load_cases=[{k: deepcopy(r[k]) for k in fields} for r in installed['load_cases']],
                     line_equipment=deepcopy(installed['physical_definition']['line_conductor']),
                     source_sha256=installed['source_sha256'],
                     scope='Static full-axle force across both rails, drive and recovery fittings counted once; no civil dynamic factor or physical acceptance',
                     installed_mass_complete=False, **FLAGS))
