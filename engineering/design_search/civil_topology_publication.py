"""Publish immutable topology experiments without promoting their railway design."""
import argparse
import gzip
from html import escape
import json
from pathlib import Path
import shutil
import tempfile

import numpy as np

from engineering.station_rail import ROOT
from engineering.station_rail.common import digest, encoded, identity
from . import civil_topology as experiment, topology_geometry as geometry
from . import topology_cost, topology_system_cost, quality_diversity

PRODUCER = 'engineering/design_search/civil_topology_publication.py'
FLAGS = experiment.FLAGS
OUTPUT = experiment.OUTPUT


def sources(root=ROOT):
    return {**experiment.sources(root), **{name: digest(Path(root)/name) for name in
        (PRODUCER, 'engineering/design_search/quality_diversity.py')}}


def _payload(folder):
    return {path.relative_to(folder).as_posix(): digest(path)
        for path in folder.rglob('*') if path.is_file() and path != folder/'manifest.json'}


def _check(folder):
    folder = Path(folder)
    if (any(path.is_symlink() for path in (folder, *folder.parents))
            or not folder.is_dir() or any(path.is_symlink() or not (path.is_file() or path.is_dir()) for path in folder.rglob('*'))):
        raise ValueError('Linked topology publication payload is not permitted')
    record = json.loads((folder/'manifest.json').read_bytes())
    experiment._sealed(record, 'manifest_id')
    if (record.get('schema') != 'osr-civil-topology-publication/1'
            or record.get('files_sha256') != _payload(folder)
            or any(record.get(key) is not value for key, value in FLAGS.items())):
        raise ValueError('Topology publication inventory or disposition differs')
    return record


def _inputs(folder, root, *, recalculate=True):
    """Verify preserved execution inputs without claiming host-tool equality."""
    state = json.loads((folder/'state.json').read_bytes())
    configured = state['plan']; experiment._sealed(configured, 'campaign_id')
    expected = experiment.plan(root)
    # Binaries and environment paths belong to the recorded execution. A CI
    # host verifies them as evidence; a new numerical replay gets its own ID.
    for key in set(expected)-{'tool_context', 'campaign_id'}:
        if configured.get(key) != expected[key]:
            raise ValueError('Topology publication inputs differ: '+key)
    experiment._sealed(configured['tool_context'], 'tool_context_id')
    baseline_path = folder/'baseline.json.gz'
    if digest(baseline_path) != state['baseline']['file_sha256']:
        raise ValueError('Topology publication baseline bytes differ')
    baseline = json.loads(gzip.decompress(baseline_path.read_bytes()))
    if baseline['baseline_id'] != state['baseline']['baseline_id']:
        raise ValueError('Topology publication baseline identity differs')
    topology_system_cost.validate_baseline(baseline, root, require_current_tools=False)
    if baseline['load_context'] != configured['load_context']:
        raise ValueError('Topology publication baseline and mechanical loads differ')
    expected_ids = {trial['trial_id'] for trial in configured['trials']}
    done = [row['trial_id'] for row in state['completed']]
    if (state.get('schema') != 'osr-civil-topology-state/1' or state['pending_trial_ids']
            or len(done) != len(set(done)) or set(done) != expected_ids):
        raise ValueError('Complete terminal topology attempt coverage required')
    results = []
    for attempt in state['completed']:
        result = experiment._read_attempt(folder, attempt, configured, state['baseline'])
        if result is not None and result['execution'] == 'completed' and recalculate:
            candidate = result['physical_geometry']
            geometry.validate(candidate)
            q = geometry.quantities(candidate, result['quantities']['densities_kg_m3'],
                reserves_kg=configured['cost_specification']['reserve_mass_kg'],
                module_length_m=configured['cost_specification']['module_length_m'])
            if q != result['quantities']:
                raise ValueError('Topology published quantities do not reproduce')
            cost = topology_cost.estimate(candidate, q, configured['cost_specification'], baseline['assumptions'])
            support = experiment.support_demands(candidate, q, baseline, configured['specification'])
            system = topology_system_cost.compare(candidate, q, cost, baseline, support,
                root=root, require_current_tools=False)
            if (cost != result['span_cost'] or support != result['support_demands']
                    or _system_semantics(system) != _system_semantics(result['system_cost'])
                    or result['baseline_id'] != baseline['baseline_id']):
                raise ValueError('Topology whole-system costs or support demands do not reproduce')
        results.append((attempt, result))
    return state, baseline, results


def _maximum_deflection(result):
    replay = result['fine_replay']
    if replay['execution'] != 'completed' or not replay['declared_residual_request_met']:
        return None
    return max(row['maximum_vertical_displacement_m'] for row in replay['cases']
        if row['load_case'] == 'crowd_control' and row['vehicle_mass_case'] == row['span_mass_case'] == 'high')


def _system_semantics(system):
    # Algebraic replay reports its actual host separately; execution metadata
    # cannot be stamped onto the preserved original evaluation identity.
    return {key: value for key, value in system.items() if key not in ('evaluation_id', 'replay_context')}


def _cost_summary(system):
    return dict(evaluation_id=system['evaluation_id'],
        comparison_to_corrected_canonical_baseline=system['comparison_to_corrected_canonical_baseline'],
        cases={name: {key: row[key] for key in ('factory_gate_cost_iqd', 'delivered_cost_iqd',
            'model_based_installed_CAPEX_iqd', 'model_based_whole_life_NPV_iqd', 'scope_totals_iqd', 'production_plan')}
            for name, row in system['cases'].items()})


def summarize(state, baseline, attempts):
    rows, eligible = [], {}
    for attempt, result in attempts:
        row = dict(trial_id=attempt['trial_id'], request_id=attempt['request_id'],
            attempt_id=attempt['attempt_id'], execution=attempt['execution'],
            runtime_seconds=attempt['runtime_seconds'], candidate_id=None,
            binary_replay=None, nominal_stock_mass_kg=None, steel_net_mass_kg=None,
            maximum_crowd_high_accounted_mass_model_displacement_m=None,
            system_cost=None, refinement_status=None, **FLAGS)
        if result is not None and result['execution'] == 'completed':
            candidate = result['physical_geometry']; q = result['quantities']['quantities']
            row.update(candidate_id=candidate['candidate_id'], evaluation_id=result['evaluation_id'],
                composition_candidate_id=result['system_cost']['candidate_id'],
                binary_replay=result['fine_replay']['execution'],
                binary_failure_reason=result['fine_replay'].get('failure_reason'),
                binary_residual_request_met=result['fine_replay'].get('declared_residual_request_met', False),
                nominal_stock_mass_kg=q['nominal_mass_kg'], steel_net_mass_kg=q['steel_net_mass_kg'],
                maximum_crowd_high_accounted_mass_model_displacement_m=_maximum_deflection(result),
                system_cost=_cost_summary(result['system_cost']),
                refinement_status=result['numerical_refinement_status'],
                compliance_relative_changes=result['compliance_relative_changes'],
                span_installed_cost_iqd={r['case']: r['scoped_installed_iqd'] for r in result['span_cost']['cases']},
                factory_person_hours={r['case']: r['total_factory_person_hours'] for r in result['span_cost']['cases']},
                trial=result['trial'], quantity_evaluation_id=result['quantities']['evaluation_id'],
                optimization_termination=(result['optimization']['termination'] if result['optimization'] else 'full-solid-reference'))
            valid = (result['coarse_replay']['execution'] == result['fine_replay']['execution'] == 'completed'
                and result['coarse_replay'].get('declared_residual_request_met') is True
                and result['fine_replay'].get('declared_residual_request_met') is True
                and candidate['web_geometry']['one_finite_edge_component'] is True
                and candidate['web_geometry']['corner_only_contacts'] == 0)
            row['binary_replay_admitted_to_archive'] = valid
            if valid:
                # Duplicate physical results retain every evaluation/attempt,
                # but enter a diversity cell once. No cross-family selection.
                cid = candidate['candidate_id']; fraction = q['steel_net_mass_kg']/q['steel_full_stock_envelope_kg']
                eligible.setdefault(cid, dict(candidate_id=cid,
                    descriptor=dict(material='steel-concrete', manufacture='cut-plate-and-precast-deck',
                        solid_fraction_band=min(4, int(fraction*5))),
                    metrics=dict(nominal_stock_mass_kg=q['nominal_mass_kg'],
                        base_whole_life_npv_iqd=_base_npv(result['system_cost']),
                        crowd_high_model_displacement_m=_maximum_deflection(result))))
        rows.append(row)
    archive = quality_diversity.archive(list(eligible.values()),
        ['nominal_stock_mass_kg', 'base_whole_life_npv_iqd', 'crowd_high_model_displacement_m'],
        ['material', 'manufacture', 'solid_fraction_band'])
    value = dict(schema='osr-civil-topology-portfolio/1', campaign_id=state['plan']['campaign_id'],
        baseline_id=baseline['baseline_id'], selection_id=baseline['selected']['selection_id'],
        vehicle_evaluation_id=baseline['selected']['vehicle_evaluation_id'], load_context_id=baseline['load_context_id'],
        selected_vehicle_candidate_id=baseline['selected']['candidate_id'],
        trial_count=len(rows), unique_realized_candidate_count=len({row['candidate_id'] for row in rows if row['candidate_id']}),
        numerically_replayed_candidate_count=len(eligible), attempts=rows, archive=archive,
        ranking_scope='Next-experiment, unqualified two-dimensional paired-web hypothesis only; no integrated baseline ranking',
        physical_qualification_pending=['three-dimensional torsion and lateral transfer', 'bearing contact and unequal wheel/web load sharing',
            'material strength, buckling, fatigue and durability', 'steel/deck connections, reinforcement, splices and bracing',
            'transport, temporary works, lifting points and manufacturing tolerances',
            'site geotechnics, foundations, seismic actions and independent review'],
        integrated_selection=None, **FLAGS)
    value['portfolio_id'] = identity(value)
    return value


def _base_npv(system):
    # The adapter carries both independent mass and financial axes explicitly.
    return system['cases']['base']['model_based_whole_life_NPV_iqd'][1]


def _svg(attempts):
    drawings = []
    for index, (attempt, result) in enumerate(attempts):
        y = index*112+28
        drawings.append(f'<text x="12" y="{y}" font-size="13">{escape(attempt["trial_id"][:12])}</text>')
        if result is None or result['execution'] != 'completed':
            drawings.append(f'<text x="150" y="{y}" font-size="13">{escape(attempt["execution"])}</text>')
            continue
        drawings.append(f'<rect x="12" y="{y+10}" width="1000" height="9" fill="#93a4b2"/>')
        for x0, x1, z0, z1 in result['physical_geometry']['web_geometry']['rectangles_xz_m']:
            drawings.append(f'<rect x="{12+50*x0:.5f}" y="{y+19+50*(-.18-z1):.5f}" width="{50*(x1-x0):.5f}" height="{50*(z1-z0):.5f}" fill="#287a9c"/>')
    return '<svg xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Realized 20 metre topology experiments; unqualified research geometry" viewBox="0 0 1030 '+str(112*len(attempts)+10)+'"><rect width="100%" height="100%" fill="white"/><g font-family="sans-serif" fill="#182b38">'+''.join(drawings)+'</g></svg>\n'


def _readme(value):
    lines = ['# Material-distribution experiments for a 20 m civil span', '',
        'These experiments generate steel-web material layouts within a fixed two-web/concrete-deck envelope. They do not change the selected v0.6 railway. Each density optimization is thresholded into explicit cut stock and independently replayed with void elements removed. Failed, interrupted and disconnected results remain in their immutable attempt packages.', '',
        f'The bounded study contains {value["trial_count"]} terminal attempts, {value["unique_realized_candidate_count"]} distinct realized geometries and {value["numerically_replayed_candidate_count"]} geometries meeting the declared replay residual request. Numerical completion does not establish a physical pass.', '',
        '![Generated stock layouts](topologies.svg)', '',
        '| Trial | Steel stock (kg) | Binary replay | Crowd/high mass model displacement (mm) | Refinement |',
        '|---|---:|---|---:|---|']
    for row in value['attempts']:
        mass = '—' if row['steel_net_mass_kg'] is None else f'{row["steel_net_mass_kg"]:.1f}'
        disp = row['maximum_crowd_high_accounted_mass_model_displacement_m']
        binary = str(row['binary_replay'] or row['execution'])
        if row.get('binary_failure_reason'):
            binary += ': '+row['binary_failure_reason']
        lines.append('| '+row['trial_id'][:12]+' | '+mass+' | '+binary+' | '+('—' if disp is None else f'{disp*1000:.2f}')+' | '+str(row['refinement_status'] or 'not established')+' |')
    lines += ['', 'The displacement values are demands in an unqualified elastic plane model. The two webs share load equally by hypothesis; concrete contributes gravity but no stiffness. Finite 250 mm wheel patches and three mean bearing translations preserve force and first moment without clamping end rotation. The three train positions are representative influence controls, not an all-position compliance, stress or journey envelope. Empty, normal and crowd-control loads cross three vehicle-mass and three span-mass cases (81 right-hand sides per binary mesh).', '',
        'The physical stock identity excludes mesh, elastic modulus, density and prices. Refining the same occupancy preserves that identity exactly. The SIMP density field and minimum soft-void stiffness are numerical devices; neither becomes installed material or physical resistance. The mesh-change target is a research diagnostic, not a structural acceptance limit.', '',
        'Manufacturing estimates count full purchased steel blanks, cut perimeters, pierces, provisional 5 m handling modules, splice ligaments, coating, QA, deck production, delivery and erection. No uncontracted offcut reuse is credited. Plant and tooling investment is charged separately from per-span process costs. Production and civil work retain two 8-hour shifts; operating hours and workforce remain separate assumptions.', '',
        'Each realized alternative replaces the affected civil, plant, construction and lifecycle lines in the same six-kilometre/two-trackway, three-station Class C scenario. All fourteen cost scopes and both independent uncertainty axes remain visible in the raw package. Unchanged vehicle, propulsion and conditional service calculations are reused by exact identity. Site prices remain explicit proxies; gravity sizing areas do not qualify foundations. Shared baseline fastener and asset-renewal corrections are applied to both sides before comparisons and are not attributed to topology savings.', '',
        'The diversity archive preserves nondominated designs in solid-fraction cells. Its cost and stiffness ordering is for the next experiment only. No candidate is accepted, adopted or released for manufacture or operation.', '',
        '## Reproduce', '', '```bash', './osr design topology plan', './osr design topology run --state build/my-topology --max-trials 1', '# Resume the same state until all seven bounded attempts terminate.', './osr design topology publish --state build/my-topology', './osr design topology verify', './osr design topology verify --replay --state build/my-topology-replay', '```', '',
        'Each numerical worker has actual address-space and CPU limits and a coordinator wall deadline. Thread environment variables request one BLAS thread; receipts record observed threads and peak RSS. These controls do not provide filesystem or network isolation. Successful iterations and phases are checkpointed before later work; terminal failures are retained rather than silently retried.', '',
        'The independent Python Q4/SIMP implementation follows the density/filter and optimality-criteria method described by the [Technical University of Denmark topology-optimization paper](https://www.topopt.mek.dtu.dk/-/media/subsites/topopt/apps/dokumenter-og-filer-til-apps/topopt88.pdf). It is not a TopOpt.jl integration. These experiments cover two-dimensional cut-plate layouts; arbitrary three-dimensional implicit surfaces and a validated full-railway topology evaluator remain open.', '',
        '[Portfolio and comparison records](result.json) · [Source and payload manifest](manifest.json) · [Campaign parameters](../../../campaigns/civil-topology.toml)', '']
    return '\n'.join(lines)


def publish(folder, *, root=ROOT, output=None):
    root = Path(root).resolve(); folder = Path(folder).resolve()
    experiment._state(folder, root)
    # Copy and render authenticated attempts first. The independent staged
    # verifier below performs the complete cost replay once before publication.
    state, baseline, attempts = _inputs(folder, root, recalculate=False)
    value = summarize(state, baseline, attempts)
    out = root/OUTPUT if output is None else Path(output)
    out.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix='.topology-publication-', dir=out.parent))
    try:
        for name in ('state.json', 'baseline.json.gz'):
            shutil.copyfile(folder/name, stage/name)
        shutil.copytree(folder/'trials', stage/'trials')
        (stage/'result.json').write_bytes(encoded(value))
        (stage/'topologies.svg').write_text(_svg(attempts))
        (stage/'README.md').write_text(_readme(value))
        manifest = dict(schema='osr-civil-topology-publication/1', portfolio_id=value['portfolio_id'],
            source_sha256=sources(root), files_sha256=_payload(stage), **FLAGS)
        manifest['manifest_id'] = identity(manifest)
        (stage/'manifest.json').write_bytes(encoded(manifest))
        # Release large original ledgers before independently reopening the
        # staged copy. Holding both complete copies can exceed the declared
        # publication memory envelope without adding verification evidence.
        del state, baseline, attempts, value
        report = verify(root=root, output=stage)
        if out.exists():
            old = _check(out)
            if old == manifest:
                return report
            backup = root/'build/civil-topology/replaced-publications'/old['manifest_id']
            if backup.exists():
                raise ValueError('Prior topology publication already retained; inspect replacement')
            backup.parent.mkdir(parents=True, exist_ok=True); shutil.move(out, backup)
        stage.rename(out)
    finally:
        if stage.exists():
            shutil.rmtree(stage)
    return report


def verify(*, root=ROOT, output=None, replay=False, state=None):
    root = Path(root).resolve(); out = root/OUTPUT if output is None else Path(output)
    manifest = _check(out)
    if manifest['source_sha256'] != sources(root):
        raise ValueError('Topology publication sources differ')
    stored, baseline, attempts = _inputs(out, root)
    expected = summarize(stored, baseline, attempts)
    if (json.loads((out/'result.json').read_bytes()) != expected
            or manifest['portfolio_id'] != expected['portfolio_id']
            or (out/'README.md').read_text() != _readme(expected)
            or (out/'topologies.svg').read_text() != _svg(attempts)):
        raise ValueError('Topology portfolio does not reproduce its authenticated attempts')
    replay_record = None
    if replay:
        if state is None or Path(state).resolve() == out.resolve():
            raise ValueError('Numerical replay requires a private, separate --state directory')
        experiment.run(state, root=root, max_trials=7)
        fresh = experiment._state(state, root)
        if fresh['pending_trial_ids']:
            raise ValueError('Numerical replay is incomplete')
        observed = {r['trial_id']: (r, experiment._read_attempt(state, r, fresh['plan'], fresh['baseline'])) for r in fresh['completed']}
        checks = []
        tolerances = stored['plan']['specification']['publication']
        for old_attempt, old_result in attempts:
            new_attempt, new_result = observed[old_attempt['trial_id']]
            if (old_result is None) != (new_result is None):
                raise ValueError('Topology replay terminal execution differs')
            if old_result is None:
                checks.append(dict(trial_id=old_attempt['trial_id'], comparison='both terminal failures; no numerical agreement claimed'))
                continue
            if old_result['physical_geometry'] != new_result['physical_geometry']:
                raise ValueError('Numerical replay changed the physical topology')
            for mesh in ('coarse_replay', 'fine_replay'):
                a, b = old_result[mesh], new_result[mesh]
                if (a['execution'] != b['execution']
                        or a.get('declared_residual_request_met') != b.get('declared_residual_request_met')):
                    raise ValueError('Topology replay numerical status differs')
                if a['execution'] == 'completed':
                    for metric in ('compliance_J', 'strain_energy_J', 'maximum_absolute_displacement_m', 'maximum_vertical_displacement_m'):
                        if not np.allclose([r[metric] for r in a['cases']], [r[metric] for r in b['cases']],
                                rtol=tolerances['replay_relative_tolerance'], atol=tolerances['replay_absolute_tolerance']):
                            raise ValueError('Topology replay numerical result differs: '+metric)
            checks.append(dict(trial_id=old_attempt['trial_id'], comparison='exact geometry and declared numerical tolerances',
                original_request_id=old_attempt['request_id'], replay_request_id=new_attempt['request_id']))
        replay_record = dict(schema='osr-civil-topology-replay/1', original_portfolio_id=expected['portfolio_id'],
            replay_campaign_id=fresh['plan']['campaign_id'], replay_tool_context=fresh['plan']['tool_context'], checks=checks, **FLAGS)
        replay_record['replay_id'] = identity(replay_record)
        experiment._write(Path(state)/'publication-replay.json', replay_record)
    return dict(verified=True, manifest_id=manifest['manifest_id'], portfolio_id=expected['portfolio_id'],
        trial_count=expected['trial_count'], realized_candidates=expected['unique_realized_candidate_count'],
        numerically_replayed_candidates=expected['numerically_replayed_candidate_count'],
        new_numerical_replay_id=None if replay_record is None else replay_record['replay_id'], **FLAGS)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('publish', 'verify'))
    parser.add_argument('--state', type=Path)
    parser.add_argument('--replay', action='store_true')
    args = parser.parse_args(argv)
    if args.action == 'publish':
        if args.state is None:
            raise ValueError('Publish requires the immutable trial --state')
        result = publish(args.state)
    else:
        result = verify(replay=args.replay, state=args.state)
    print(json.dumps(result, indent=2, allow_nan=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
