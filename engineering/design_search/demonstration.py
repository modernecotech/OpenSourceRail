"""Execute the 1.5/2 km integration matrix without inventing missing plants.

Each distance and architecture materializes its own canonical physical bundle.
Demand, brake hypotheses, civil loads and manufacturing/economic quantities share
that bundle. No generated demand curve is an available motor, and a checksum is
not a measured or independently approved component qualification.
"""
from pathlib import Path
import fcntl
import gzip
import json
import time
import tomllib

from engineering.station_rail import ROOT
from engineering.station_rail.common import digest, encoded, identity
from . import design_grammar as grammar, equipped_candidates, railway_bundle
from . import railway_campaign, revision_planner, system_motion, system_inventory
from . import route_bundle, fault_response

PRODUCER = 'engineering/design_search/demonstration.py'
SPEC = 'campaigns/end-to-end-railway-closure.toml'
OUTPUT = 'docs/design-engine/railway-closure'
FLAGS = dict(grammar.FLAGS, physical_journey_completed=False)


def specification(root=ROOT):
    value = tomllib.loads((Path(root) / SPEC).read_text())
    fixed = dict(schema='osr-end-to-end-railway-closure/1',
                 reference_changes_allowed=False, maximum_bundle_cases=12,
                 maximum_native_jobs=0, maintain_pending_tasks=True,
                 unknown_installed_quantities_are_zero=False,
                 allow_synthetic_operating_maps=False,
                 body_families=['aluminium_frame', 'aluminium_stressed_skin', 'gfrp_semimonocoque'],
                 architecture_families=['P1', 'P4'], distances_m=[1500., 2000.],
                 loads=['empty', 'normal', 'crowd', 'adverse-normal'],
                 faults=['failed-launch', 'wayside-power-loss', 'stranded-train-recovery'])
    if any(value.get(k) != v for k, v in fixed.items()):
        raise ValueError('Changed closure scope requires an explicit evaluator revision')
    if type(value['maximum_seconds']) is not int or not 1 <= value['maximum_seconds'] <= 300:
        raise ValueError('Closure execution budget must be at most 300 seconds')
    if value['completion'] != dict(equipped_candidates=3, authenticated_inputs_required=True,
            validated_available_force_map_required=True, independent_braking_and_fault_protection_required=True,
            whole_system_quantities_and_cost_required=True, automatic_physical_acceptance_allowed=False):
        raise ValueError('Physical completion obligations cannot be relaxed')
    return value


def sources(root=ROOT):
    root = Path(root)
    result = railway_campaign.source_epoch(root)
    for name in (PRODUCER, SPEC, route_bundle.PRODUCER, equipped_candidates.PRODUCER, fault_response.PRODUCER, 'engineering/development_baseline/entrypoint.py'):
        result[name] = digest(root / name)
    # Every producer must execute from this source tree, including a relocated checkout.
    if digest(root / PRODUCER) != digest(__file__):
        raise ValueError('Executing closure producer differs from declared source root')
    return result


def _write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.pending')
    temporary.write_bytes(encoded(value))
    temporary.replace(path)


def _seal(value):
    value['record_id'] = identity(value)
    return value


def _read(path):
    value = json.loads(Path(path).read_bytes())
    if value.get('record_id') != identity({k: v for k, v in value.items() if k != 'record_id'}):
        raise ValueError('Modified closure record: ' + str(path))
    if any(value.get(k) is not False for k in FLAGS):
        raise ValueError('Research evidence cannot grant physical acceptance or release')
    return value


def _scenarios(spec):
    return [('empty', dict(load='empty')), ('normal', dict(load='normal')),
            ('crowd', dict(load='crowd')),
            ('adverse-normal', dict(load='normal', **spec['adverse_hypothesis']))]


def evaluate(body, bundle, spec, *, root=ROOT):
    """Calculate actual conditional demands; leave unavailable fault plants held."""
    railway_bundle.validate(bundle)
    if body['candidate_id'] != bundle['body_candidate_id']:
        raise ValueError('Body and railway composition differ')
    architecture = railway_bundle.assess_architecture(bundle)
    civil = railway_bundle.assess_civil(bundle)
    inventory = system_inventory.evaluate(body, bundle_id=bundle['bundle_id'], source_root=root,
        component_substitutions=bundle['component_substitutions'], extra_equipment_tasks=bundle['unweighed_architecture_equipment'])
    if abs(inventory['known_accounted_mass_subtotal_kg'] - bundle['mass']['accounted_tare_kg_per_car']) > 1e-6:
        raise ValueError('Inventory and journey accounted-mass scopes differ')
    motion = []
    for name, overrides in _scenarios(spec):
        value = system_motion.evaluate(bundle, scenario_overrides=overrides)
        if value['candidate_id'] != bundle['candidate_id']:
            raise ValueError('Mixed longitudinal result')
        motion.append(dict(name=name, result=value))
    propulsion = railway_campaign.propulsion(bundle, architecture)
    economics = railway_campaign.economics(bundle, inventory, architecture,
                                          propulsion, motion[1]['result'], civil)
    responses = fault_response.evaluate(bundle, root=root)
    faults = [dict(name=name, execution='not-run', engineering_screen='unknown',
                   candidate_id=bundle['candidate_id'],
                   reason='Full fault journey held: validated propulsion, brake supply/protection/recovery plant and installed train state are absent; separate conditional responses start from declared hypotheses',
                   conditional_response_matrix_id=responses['evaluation_id'],
                   independent_brake_hypotheses_id=identity(motion[1]['result']['braking']),
                   **FLAGS) for name in spec['faults']]
    observation = dict(candidate_id=bundle['candidate_id'], evaluation_id=identity(motion),
                       requirement_revision=bundle['requirement_revision'], execution='completed',
                       numerical_validity='valid', failure_class='evidence-gap', domain='propulsion',
                       diagnosis='Installed train state and validated available moving-LIM map are absent; required thrust is conditional demand')
    plan = revision_planner.plan(bundle['candidate_id'], observation, maximum_proposals=2)
    return dict(candidate_id=bundle['candidate_id'], body_candidate_id=body['candidate_id'],
                family_id=bundle['family_id'], distance_m=bundle['architecture_case']['physical_definition']['route']['station_spacing_m'],
                mass_scope=bundle['mass_scope'], architecture=architecture, propulsion=propulsion,
                inventory_evaluation_id=inventory['evaluation_id'], inventory_summary=railway_campaign._inventory_summary(inventory),
                motion=motion, faults=faults, conditional_fault_responses=responses, civil=civil, economics=economics,
                next_experiments=plan, complete_installed_mass_kg=None, **FLAGS)


def run(root=ROOT, *, state=None, maximum_new_bundles=None):
    root = Path(root)
    spec = specification(root)
    if maximum_new_bundles is not None and (type(maximum_new_bundles) is not int or not 0 <= maximum_new_bundles <= 12):
        raise ValueError('Zero to twelve new bundles per invocation required')
    folder = Path(state) if state is not None else root / 'build/railway-closure'
    folder.mkdir(parents=True, exist_ok=True)
    with (folder / 'campaign.lock').open('w') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        epoch = sources(root)
        contract = dict(specification=spec, source_sha256=epoch)
        contract_id = identity(contract)
        start = time.monotonic()
        # The equipped inventory is stored once; route/load cases reference it.
        equipped_path = folder / 'equipped' / (contract_id + '.json')
        if equipped_path.is_file():
            equipped = _read(equipped_path)
            if equipped['request'] != contract:
                raise ValueError('Equipped cache source identity differs')
        else:
            equipped = _seal(dict(request=contract, output=equipped_candidates.comparison(root), **FLAGS))
            if sources(root) != epoch:
                raise ValueError('Source epoch changed during equipped generation')
            _write(equipped_path, equipped)
        rows, pending, new, reused = [], [], 0, 0
        for parent in equipped['output']['candidates']:
            body = parent['body']
            for family in spec['architecture_families']:
                for distance in spec['distances_m']:
                    bundle = route_bundle.materialize(body, family=family, distance_m=distance, root=root)
                    request = dict(bundle_definition_id=bundle['definition_id'], bundle_id=bundle['bundle_id'],
                                   equipped_record_id=equipped['record_id'], contract_id=contract_id)
                    path = folder / 'cases' / (identity(request) + '.json')
                    if path.is_file():
                        record = _read(path)
                        if record['request'] != request or record['bundle'] != bundle:
                            raise ValueError('Closure case cache differs from exact bundle request')
                        reused += 1
                    elif (maximum_new_bundles is not None and new >= maximum_new_bundles) or time.monotonic() - start >= spec['maximum_seconds']:
                        pending.append(request)
                        continue
                    else:
                        if sources(root) != epoch:
                            raise ValueError('Closure sources changed before execution')
                        value = evaluate(body, bundle, spec, root=root)
                        if sources(root) != epoch:
                            raise ValueError('Closure sources changed during execution')
                        record = _seal(dict(request=request, bundle=bundle, output=value, **FLAGS))
                        _write(path, record)
                        new += 1
                    rows.append(record)
        result = dict(schema='osr-end-to-end-railway-closure-result/1', contract=contract,
                      contract_id=contract_id, equipped_record_id=equipped['record_id'], rows=rows,
                      pending=pending, new_bundles=new, reused_bundles=reused,
                      integrated_selection=None, selected_reference_changed=False, **FLAGS)
        result['evaluation_id'] = identity({k: v for k, v in result.items() if k not in ('new_bundles', 'reused_bundles')})
        _write(folder / 'latest.json', result)
        return result


def summary(value):
    rows = [r['output'] for r in value['rows']]
    return dict(schema='osr-end-to-end-railway-closure-summary/1', evaluation_id=value['evaluation_id'],
                contract_id=value['contract_id'], evaluated_bundles=len(rows), pending_bundles=len(value['pending']),
                conditional_loading_screens=sum(len(r['motion']) for r in rows),
                fault_scenarios_held=sum(len(r['faults']) for r in rows),
                conditional_brake_response_cases=sum(len(r['conditional_fault_responses']['cases']) for r in rows),
                complete_equipped_candidates=0, validated_operating_maps=0,
                physically_supported_journeys=0, complete_whole_life_costs=0,
                installed_mass_kg=None, whole_life_cost_USD=None, integrated_selection=None,
                completion_status='held-for-installed-and-authenticated-physical-inputs',
                open_obligations=['Located and counted equipment, joints, wiring, protection and maintenance access',
                  'Directional material/joint laws, strength, buckling, fatigue and approved load cases',
                  'Converged and independently validated finite-position LIM map with circuit and repeated thermal duty',
                  'Independent brake hardware, precise stopping and protected failed-launch/recovery demonstrations',
                  'Site-specific beam, pier, foundation, erection, station and access design',
                  'Manufacturing/installation quotes, energy purchases, service reliability and whole-life costs'], **FLAGS)


def _contract(value, root):
    current = dict(specification=specification(root), source_sha256=sources(root))
    if value.get('contract') != current or value.get('contract_id') != identity(current):
        raise ValueError('Closure contract differs from the current campaign and producer sources')


def _coverage(value, equipped, root):
    expected = []
    spec = value['contract']['specification']
    if len(equipped['output']['candidates']) != 3 or {r['body']['parameters']['family'] for r in equipped['output']['candidates']} != set(spec['body_families']):
        raise ValueError('Exactly three physically distinct equipped projections required')
    for parent in equipped['output']['candidates']:
        for family in spec['architecture_families']:
            for distance in spec['distances_m']:
                bundle = route_bundle.materialize(parent['body'], family=family, distance_m=distance, root=root)
                expected.append(dict(bundle_definition_id=bundle['definition_id'], bundle_id=bundle['bundle_id'],
                                     equipped_record_id=equipped['record_id'], contract_id=value['contract_id']))
    actual = [r['request'] for r in value['rows']] + value['pending']
    if len(expected) != 12 or len(actual) != 12 or sorted(map(identity, actual)) != sorted(map(identity, expected)):
        raise ValueError('Executed and pending requests must cover the complete disjoint twelve-bundle matrix')


def publish(root=ROOT, *, state=None, output=None):
    root = Path(root)
    folder = Path(state) if state is not None else root / 'build/railway-closure'
    value = json.loads((folder / 'latest.json').read_bytes())
    _contract(value, root)
    # Verify all immutable records before publishing their index and data.
    equipped = _read(folder / 'equipped' / (value['contract_id'] + '.json'))
    if equipped['record_id'] != value['equipped_record_id']:
        raise ValueError('Equipped parent differs')
    _coverage(value, equipped, root)
    for row in value['rows']:
        if _read(folder / 'cases' / (identity(row['request']) + '.json')) != row:
            raise ValueError('Published case differs from retained execution')
    target = Path(output) if output is not None else root / OUTPUT
    target.mkdir(parents=True, exist_ok=True)
    s = summary(value)
    _write(target / 'summary.json', s)
    _write(target / 'source-epochs.json', sources(root))
    (target / 'cases.json.gz').write_bytes(gzip.compress(encoded(value), mtime=0))
    (target / 'equipped.json.gz').write_bytes(gzip.compress(encoded(equipped), mtime=0))
    text = ('# Candidate-to-journey closure\n\n'
            f"Three distinct body definitions feed {s['evaluated_bundles']} same-candidate railway bundles "
            'over 1.5 km and 2 km, with station-only P1 and separately identified P4 recovery-drive research. '
            f"{s['conditional_loading_screens']} empty, normal, crowd and adverse loading calculations "
            'propagate accounted mass to required force, independent brake hypotheses, civil loads and quantity coefficients. '
            f"{s['fault_scenarios_held']} full fault journeys remain explicitly not-run. "
            f"{s['conditional_brake_response_cases']} separate brake-response calculations use declared initial states, "
            'command latency, pressure rise, lost channels/pressure and adhesion. Static holding and rollback are resolved '
            'without reverse propulsion from a brake command. These are unqualified hypotheses, not completed fault journeys.\n\n'
            '**Zero complete installed vehicles, validated operating maps or physically supported journeys.** '
            'These are conditional calculations. Unlocated equipment accounts, GFRP/joint properties, '
            'actual electrical/thermal duty, brake hardware, site data and prices remain open. '
            'No preferred railway or physical release is selected.\n\n'
            'The moving-conductor LIM method is a separate numerical component experiment; '
            'its benchmark, refinement and domain limitations remain separate from operating-map admission.\n\n'
            'Run `./osr design railway demonstrate --max-bundles 12`; resume the same command for pending cases. '
            'Use `./osr design railway demonstration-publish` and '
            '`./osr design railway demonstration-verify` to regenerate/check this packet.\n\n'
            '[Summary](summary.json) · [Executed cases](cases.json.gz) · '
            '[Bodies and equipped projections](equipped.json.gz) · [Sources](source-epochs.json)\n')
    (target / 'README.md').write_text(text)
    manifest = dict(schema='osr-end-to-end-railway-closure-publication/1', evaluation_id=value['evaluation_id'],
                    sources=sources(root), files={name: digest(target / name) for name in
                    ('README.md', 'summary.json', 'source-epochs.json', 'cases.json.gz', 'equipped.json.gz')}, **FLAGS)
    manifest['publication_id'] = identity(manifest)
    _write(target / 'manifest.json', manifest)
    return verify(root, output=target)


def verify(root=ROOT, *, output=None):
    target = Path(output) if output is not None else Path(root) / OUTPUT
    manifest = json.loads((target / 'manifest.json').read_bytes())
    if manifest.get('publication_id') != identity({k: v for k, v in manifest.items() if k != 'publication_id'}):
        raise ValueError('Closure publication identity differs')
    if manifest['sources'] != sources(root) or any(digest(target / n) != h for n, h in manifest['files'].items()):
        raise ValueError('Closure source or payload differs')
    value = json.loads(gzip.decompress((target / 'cases.json.gz').read_bytes()))
    _contract(value, root)
    if value['evaluation_id'] != identity({k: v for k, v in value.items() if k not in ('evaluation_id', 'new_bundles', 'reused_bundles')}):
        raise ValueError('Closure evaluation differs')
    if json.loads((target / 'summary.json').read_bytes()) != summary(value):
        raise ValueError('Closure summary differs')
    equipped = json.loads(gzip.decompress((target / 'equipped.json.gz').read_bytes()))
    if equipped.get('record_id') != identity({k: v for k, v in equipped.items() if k != 'record_id'}) or equipped['record_id'] != value['equipped_record_id']:
        raise ValueError('Closure equipped evidence differs')
    _coverage(value, equipped, root)
    if equipped['request'] != value['contract'] or equipped['output'] != equipped_candidates.comparison(root):
        raise ValueError('Equipped stock and installation projection do not reproduce')
    bodies = {p['body']['candidate_id']: p['body'] for p in equipped['output']['candidates']}
    for row in value['rows']:
        if row.get('record_id') != identity({k: v for k, v in row.items() if k != 'record_id'}):
            raise ValueError('Closure case identity differs')
        railway_bundle.validate(row['bundle'])
        if row['request'] != dict(bundle_definition_id=row['bundle']['definition_id'], bundle_id=row['bundle']['bundle_id'],
                                  equipped_record_id=equipped['record_id'], contract_id=value['contract_id']):
            raise ValueError('Closure case dependency request differs')
        if row['output'] != evaluate(bodies[row['bundle']['body_candidate_id']], row['bundle'], value['contract']['specification'], root=root):
            raise ValueError('Closure calculation does not reproduce')
    if any(manifest.get(k) is not False or value.get(k) is not False for k in FLAGS):
        raise ValueError('Closure cannot grant physical acceptance')
    if sources(root) != manifest['sources']:
        raise ValueError('Closure sources changed during verification')
    return dict(publication_id=manifest['publication_id'], **summary(value))
