"""Repository front doors for the explicitly selected development design.

Historical calculations are available through the separate ``legacy`` namespace.
No command substitutes their mass, operating assumptions or qualification state.
"""
from __future__ import annotations

import argparse
from functools import lru_cache
from hashlib import sha256
import importlib
import json
from pathlib import Path
import subprocess
import sys

from . import FLAGS, INPUT, OUTPUT, ROOT
from . import selection

IDS = ('candidate_id', 'body_candidate_id', 'support_component_id', 'propulsion_component_id')


class CurrentUnavailable(ValueError):
    """Missing, stale or incompatible evidence must remain an explicit hold."""


def checked_path(root, relative):
    root = Path(root).resolve()
    path = Path(relative)
    if path.is_absolute() or not path.parts or any(p in ('..', '') for p in path.parts):
        raise CurrentUnavailable('Expected an ordinary repository-relative path')
    target = root / path
    for part in (target, *target.parents):
        if part == root:
            break
        if part.is_symlink():
            raise CurrentUnavailable('Symlinks are not evidence paths: ' + str(relative))
    if not target.resolve().is_relative_to(root):
        raise CurrentUnavailable('Evidence path escapes repository')
    return target


def stamp(path):
    st = path.stat()
    return st.st_dev, st.st_ino, st.st_size, st.st_mtime_ns, st.st_ctime_ns


@lru_cache(maxsize=8192)
def _digest(path, signature):
    h = sha256()
    with Path(path).open('rb') as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b''):
            h.update(chunk)
    if stamp(Path(path)) != signature:
        raise CurrentUnavailable('Evidence changed while reading: ' + path)
    return h.hexdigest()


def digest(path):
    path = Path(path)
    return _digest(str(path), stamp(path))


@lru_cache(maxsize=8)
def _selected(root, signatures):
    value = selection.load(Path(root))
    # load() already checks publication bytes and identities; the stamps keep
    # repeated read-only requests cheap while invalidating edits immediately.
    if _selection_stamps(Path(root)) != signatures:
        raise CurrentUnavailable('Selection changed while reading')
    return value


def _selection_stamps(root):
    import tomllib
    selector = checked_path(root, INPUT)
    config = tomllib.loads(selector.read_text())
    if config.get('family') != 'wheel_rail_station_lim':
        raise CurrentUnavailable('The current front door requires the explicit v0.6 wheel-supported selector')
    # Physical definitions are generated from the selected source. A running
    # Workbench must invalidate its cached selection when those producers change,
    # including a rebuild that leaves the selector TOML unchanged.
    paths = [INPUT, config['source_brief']]
    paths += [p.relative_to(root).as_posix() for p in
              sorted((root / 'engineering/station_rail').glob('*.py'))]
    return tuple((p, stamp(checked_path(root, p))) for p in sorted(set(paths)))


def selected(root=ROOT):
    root = Path(root).resolve()
    return _selected(str(root), _selection_stamps(root))


def check_identity(value, baseline):
    expected = baseline['vehicle']
    if value.get('selection_id') != baseline['selection_id']:
        raise CurrentUnavailable('Current packet uses a different selection')
    for key in IDS:
        if value.get(key) != expected[key]:
            raise CurrentUnavailable('Current packet uses a different ' + key)
    if value.get('development_default') is not True:
        raise CurrentUnavailable('Current packet is not the selected development default')
    # Every current packet carries all dispositions explicitly. Execution and
    # adoption never confer engineering/manufacturing/operating acceptance.
    for key, expected_value in FLAGS.items():
        if value.get(key) is not expected_value:
            raise CurrentUnavailable('Unsupported acceptance disposition: ' + key)


def read_packet(root=ROOT, output=OUTPUT):
    root = Path(root).resolve()
    baseline = selected(root)
    directory = checked_path(root, output)
    manifest_path = checked_path(root, str(Path(output) / 'manifest.json'))
    if not manifest_path.is_file():
        raise CurrentUnavailable('Current publication is missing; run ./osr build')
    manifest = json.loads(manifest_path.read_text())
    check_identity(manifest, baseline)
    bindings = manifest.get('files_sha256', {})
    if 'summary.json' not in bindings:
        raise CurrentUnavailable('Current summary has no publication binding')
    for relative, expected in bindings.items():
        path = checked_path(root, str(Path(output) / relative))
        if not path.is_file() or digest(path) != expected:
            raise CurrentUnavailable('Current output is missing or modified: ' + relative)
    sources = manifest.get('source_sha256')
    if not isinstance(sources, dict) or not sources:
        raise CurrentUnavailable('Current publication has no source bindings')
    for relative, expected in sources.items():
        path = checked_path(root, relative)
        if not path.is_file() or digest(path) != expected:
            raise CurrentUnavailable('Current source changed: ' + relative)
    summary_bytes = (directory / 'summary.json').read_bytes()
    if sha256(summary_bytes).hexdigest() != bindings['summary.json']:
        raise CurrentUnavailable('Current summary changed while reading')
    result = json.loads(summary_bytes)
    check_identity(result, baseline)
    return result, manifest


def status(root=ROOT):
    baseline = selected(root)
    config = baseline['selection']
    vehicle = baseline['vehicle']
    result = dict(schema='osr-default-entrypoint/1', selection_id=baseline['selection_id'],
                  development_default=True, selection_revision=config['revision'],
                  family=config['family'], vehicle=config['vehicle'],
                  service=config['service'], mass=vehicle['mass'],
                  network_proposal_id=config['network_proposal_id'],
                  publication_path=OUTPUT, **{key: vehicle[key] for key in IDS}, **FLAGS)
    try:
        result['publication'], _ = read_packet(root)
        result['publication_state'] = 'current'
    except (OSError, ValueError, KeyError) as exc:
        result['publication_state'] = 'hold'
        result['hold_reason'] = str(exc)
    return result


def emit(value):
    print(json.dumps(value, indent=2, sort_keys=True, allow_nan=False))


def hold(root, action, reason):
    value = status(root)
    value.update(execution='held', requested_action=action, reason=reason)
    emit(value)
    return 3


def _module(name):
    return importlib.import_module('engineering.development_baseline.' + name)


def main(argv=None, root=ROOT):
    parser = argparse.ArgumentParser(
        description=__doc__,
        epilog=('Historical command writers use a pinned external worktree: '
                './osr legacy checkout v0.5.1 --path /absolute/path. Read '
                'docs/releases/v0.6-functionality-reconciliation.md for the '
                'historical command list, runtime requirements and scope limits.'))
    parser.add_argument('--root', type=Path, default=Path(root), help=argparse.SUPPRESS)
    parser.add_argument('command', nargs='?', default='status')
    parser.add_argument('arguments', nargs=argparse.REMAINDER)
    args = parser.parse_args(argv)
    root = args.root.resolve()
    command, rest = args.command, args.arguments
    if command in ('design', 'infrastructure') and rest in (['-h'], ['--help'], ['help']):
        print('Usage: ./osr design COMMAND [arguments]\n\n'
              '  status, build, verify     Selected v0.6 reference packet\n'
              '  railway plan/run/...      Coordinated whole-railway research\n'
              '  journey-study run/publish/verify [--replay] Conditional P1 study\n'
              '  adaptive, architecture    Function-first and architecture studies\n'
              '  generative, space         Structural grammar and design space\n'
              '  campaign                  Bounded candidate campaign lifecycle\n'
              '  sourced                   Source-backed component alternatives\n'
              '  progress                  Continuing reference-cell analysis\n'
              'Use ./osr design railway --help or ./osr plan --help for details.')
        return 0
    # design/infrastructure are aliases, including their own status default.
    if command in ('design', 'infrastructure'):
        command, rest = (rest[0], rest[1:]) if rest else ('status', [])
    try:
        if command=='journey-study':
            if rest in (['-h'],['--help'],['help']):
                print('Usage: ./osr design journey-study {run|publish|verify} [--replay]')
                return 0
            action=rest[0] if rest else 'run'
            options=argparse.ArgumentParser(prog='./osr design journey-study '+action)
            if action=='verify':options.add_argument('--replay',action='store_true')
            parsed=options.parse_args(rest[1:] if rest else [])
            from engineering.design_search import conditional_journey_study as study,conditional_journey_publication as publication
            if action=='run':emit(study.run(root));return 0
            if action=='publish':emit(publication.build(root));return 0
            if action=='verify':emit(publication.verify(root,replay=parsed.replay));return 0
            raise ValueError('Use journey-study run, publish, or verify [--replay]')
        if command=='progress':
            from engineering.railway_progress.cli import main as progress_main
            return progress_main(rest,root=root)
        if command=='railway':
            if rest in (['-h'], ['--help'], ['help']):
                print('Usage: ./osr design railway COMMAND [arguments]\n\n'
                      '  plan, run [--max-bundles N] [--native-jobs N], publish, verify\n'
                      '  refine/refine-verify --parent-result PATH --candidate-id ID\n'
                      '  refine-current/refine-current-verify --parent-result PATH --candidate-id ID\n'
                      '  refine-current-fine/refine-current-fine-verify --parent-result PATH --candidate-id ID\n'
                      '  refine-current-fine-reconcile --parent-result PATH --candidate-id ID --request-id ID\n'
                      '  refine-next/refine-next-verify --parent-result PATH --candidate-id ID\n'
                      '  refine-next-resource/refine-next-resource-verify/refine-next-resource-reconcile --parent-result PATH --candidate-id ID\n'
                      '  demonstration-plan, demonstrate [--max-bundles N], demonstration-publish, demonstration-verify')
                return 0
            from engineering.design_search import railway_campaign,railway_publication,railway_refinement,railway_fine_refinement,railway_fine_refinement_resource,remit
            if rest and rest[0] in ('demonstration-plan','demonstrate','demonstration-publish','demonstration-verify'):
                from engineering.design_search import demonstration
                action=rest[0]
                if action=='demonstration-plan' and len(rest)==1:
                    emit(demonstration.specification(root));return 0
                options=argparse.ArgumentParser(prog='./osr design railway '+action)
                options.add_argument('--state',type=Path)
                if action=='demonstrate':options.add_argument('--max-bundles',type=int)
                parsed=options.parse_args(rest[1:])
                if action=='demonstrate':
                    result=demonstration.run(root,state=parsed.state,maximum_new_bundles=parsed.max_bundles)
                    emit(dict(new_bundles=result['new_bundles'],reused_bundles=result['reused_bundles'],**demonstration.summary(result)));return 0
                if action=='demonstration-publish':emit(demonstration.publish(root,state=parsed.state));return 0
                if action=='demonstration-verify':
                    if parsed.state is not None:raise ValueError('Publication verification uses published inputs, not a local state override')
                    emit(demonstration.verify(root));return 0
                raise ValueError('Use demonstration-plan without options')
            if rest==['plan']:
                emit(dict(specification=railway_campaign.specification(root),remit=remit.default(),dependency_graph=railway_campaign.EDGES,physical_accepted=False));return 0
            if rest==['publish']:emit(railway_publication.build(root));return 0
            if rest==['verify']:emit(railway_publication.verify(root));return 0
            if rest and rest[0] in ('refine','refine-verify','refine-current','refine-current-verify','refine-current-fine','refine-current-fine-verify','refine-current-fine-reconcile','refine-next','refine-next-verify','refine-next-resource','refine-next-resource-verify','refine-next-resource-reconcile'):
                action=rest[0]
                options=argparse.ArgumentParser(prog='./osr design railway '+action)
                options.add_argument('--parent-result',type=Path,required=True)
                options.add_argument('--candidate-id',required=True)
                options.add_argument('--request-id',required=action=='refine-current-fine-reconcile')
                parsed=options.parse_args(rest[1:])
                parent_result=parsed.parent_result if parsed.parent_result.is_absolute() else root/parsed.parent_result
                if action=='refine-current-fine-reconcile' or action=='refine-current-fine-verify' and parsed.request_id:
                    from engineering.design_search import railway_refinement_current_fine_reconcile as reconcile
                    if action=='refine-current-fine-reconcile':
                        emit(reconcile.reconcile(root,parent_result=parent_result,candidate_id=parsed.candidate_id,request_id=parsed.request_id))
                    else:
                        emit(reconcile.verify(root,parent_result=parent_result,candidate_id=parsed.candidate_id,request_id=parsed.request_id))
                    return 0
                if action in ('refine','refine-verify'):
                    evaluator=railway_refinement
                elif action in ('refine-current','refine-current-verify'):
                    from engineering.design_search import railway_refinement_current
                    evaluator=railway_refinement_current
                elif action in ('refine-current-fine','refine-current-fine-verify'):
                    from engineering.design_search import railway_refinement_current_fine
                    evaluator=railway_refinement_current_fine
                elif action in ('refine-next','refine-next-verify'):
                    evaluator=railway_fine_refinement
                else:
                    evaluator=railway_fine_refinement_resource
                if action in ('refine-next-resource-verify','refine-next-resource-reconcile'):
                    from engineering.design_search import railway_fine_refinement_recovery
                    if action == 'refine-next-resource-reconcile':
                        emit(railway_fine_refinement_recovery.reconcile(
                            root, parent_result=parent_result, candidate_id=parsed.candidate_id))
                    else:
                        emit(railway_fine_refinement_recovery.verify(
                            root, parent_result=parent_result, candidate_id=parsed.candidate_id))
                    return 0
                if action in ('refine','refine-current','refine-current-fine','refine-next','refine-next-resource'):
                    emit(evaluator.run(root,parent_result=parent_result,candidate_id=parsed.candidate_id));return 0
                if action=='refine-current-verify':
                    from engineering.design_search import railway_refinement_current_verifier
                    emit(railway_refinement_current_verifier.verify(
                        root,parent_result=parent_result,candidate_id=parsed.candidate_id));return 0
                emit(evaluator.verify(root,parent_result=parent_result,candidate_id=parsed.candidate_id));return 0
            if rest and rest[0]=='run':
                options=argparse.ArgumentParser(prog='./osr design railway run');options.add_argument('--max-bundles',type=int);options.add_argument('--native-jobs',type=int,default=0)
                parsed=options.parse_args(rest[1:]);r=railway_campaign.run(root,maximum_new_bundles=parsed.max_bundles,native_jobs=parsed.native_jobs)
                if r.get('integrated_selection') is not None or r.get('selected_reference_changed') is not False or any(r.get(k) is not False for k in ('physical_accepted','engineering_accepted','configuration_adopted','manufacturing_release','operating_release')):raise ValueError('Coordinated research cannot select or release a railway')
                emit(dict(campaign_id=r['campaign_id'],contract_id=r['contract_id'],body_definitions=len(r['bodies']),evaluated_bundles=len(r['rows']),
                    new_bundles=r['new_bundles'],reused_bundles=r['reused_bundles'],frontier_items=len(r['frontier']),integrated_selection=None,physical_accepted=False));return 0
            raise ValueError('Use ./osr design railway plan, run [--max-bundles N] [--native-jobs N], publish, verify, refinement commands, demonstration-plan, demonstrate [--max-bundles N] [--state PATH], demonstration-publish or demonstration-verify')
        if command=='generative':
            from engineering.design_search import generative_campaign,generative_publication
            if rest==['plan']:emit(generative_campaign.specification());return 0
            if rest==['publish']:emit(generative_publication.build(root=root));return 0
            if rest==['verify']:emit(generative_publication.verify(root=root));return 0
            if rest==['run']:
                result=generative_campaign.run(root=root)
                if result.get('integrated_selection') is not None or result.get('selected_reference_changed') is not False or any(result.get(k) is not False for k in ('physical_accepted','engineering_accepted','configuration_adopted','manufacturing_release','operating_release')):
                    raise ValueError('Generative research cannot select or release an integrated design')
                emit(dict(campaign_id=result['campaign_id'],candidate_count=len(result['candidates']),rewrite_count=len(result['executed_rewrites']),
                    integrated_selection=None,selected_reference_changed=False,configuration_adopted=False,**FLAGS));return 0
            raise ValueError('Use ./osr design generative plan, run, publish or verify')
        if command=='adaptive':
            from engineering.design_search import adaptive_campaign,adaptive_publication,body_revision,design_variables,requirement_policy,section_proposals
            if rest==['plan']:
                from engineering.station_rail import vehicle
                emit(dict(specification=adaptive_campaign.specification(root),variables=design_variables.catalogue(),requirements=requirement_policy.catalogue(),
                    body_experiments=body_revision.plan(vehicle.build(root),root=root),
                    additional_section_definitions=section_proposals.generate(vehicle.build(root),samples=adaptive_campaign.specification(root)['exploration']['section_samples'],root=root),physical_accepted=False));return 0
            if rest==['publish']:emit(adaptive_publication.build(root));return 0
            if rest==['verify']:emit(adaptive_publication.verify(root));return 0
            if rest and rest[0]=='run' and len(rest) in (1,3):
                limit=None
                if len(rest)==3:
                    if rest[1]!='--max-jobs':raise ValueError('Use --max-jobs N')
                    limit=int(rest[2])
                r=adaptive_campaign.run(root,maximum_new_jobs=limit)
                emit(dict(campaign_id=r['campaign_id'],contract_id=r['contract_id'],new_native_jobs=r['new_native_jobs'],reused_native_jobs=r['reused_native_jobs'],
                    frontier_items=len(r['frontier']),search_status=r['search_status'],integrated_selection=None,physical_accepted=False));return 0
            raise ValueError('Use ./osr design adaptive plan, run [--max-jobs N], publish or verify')
        if command=='architecture':
            from engineering.design_search import railway_architecture as architecture,architecture_publication
            if rest in (['build'],['publish']):emit(architecture_publication.build(root));return 0
            if rest==['verify']:emit(architecture_publication.verify(root));return 0
            if rest and rest[0]=='run' and len(rest) in (1,3):
                limit=None
                if len(rest)==3:
                    if rest[1]!='--max-cases':raise ValueError('Use --max-cases N')
                    limit=int(rest[2])
                result=architecture.evaluate_campaign(root,max_new_cases=limit)
                if result.get('state')=='interrupted':
                    from engineering.station_rail.common import encoded
                    target=root/'build/v06-architecture/umbrella-interruption-final.json';target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(encoded(result));emit(result);return 3
                emit(dict(campaign_id=result['campaign_id'],contract_id=result['contract_id'],evaluation_cases=len(result['cases']),physical_definitions=result['distinct_physical_candidates'],integrated_selection=result['integrated_selection'],physical_accepted=False));return 0
            raise ValueError('Use ./osr design architecture run [--max-cases N], publish or verify')
        if command=='space':
            from engineering.station_rail import design_space
            if rest==['build']:emit(design_space.build(root));return 0
            if rest==['verify']:emit(design_space.verify(root));return 0
            raise ValueError('Use ./osr design space build or verify')
        if command=='campaign':
            from engineering.design_search import campaign
            if not rest:raise ValueError('Use campaign create/run/compare/publish')
            action=rest[0]
            if action=='create' and len(rest)==2:emit(campaign.create(root/rest[1]));return 0
            if action=='run' and len(rest) in (2,4):
                limit=None
                if len(rest)==4:
                    if rest[2]!='--max-jobs':raise ValueError('Use --max-jobs N')
                    limit=int(rest[3])
                journal=campaign.run(rest[1],max_jobs=limit);emit(journal);return 0 if journal['state']=='completed' else 3
            if action=='compare' and len(rest)==2:
                result=campaign.compare(rest[1]);emit(dict(campaign_id=rest[1],candidate_count=len(result['candidates']),primary_jobs=len(result['results']),next_experiment=result['next_experiment'],integrated_baseline=result['integrated_baseline']));return 0
            if action=='publish' and len(rest)==2:
                from engineering.design_search import wheel_publication as pub
                from engineering.station_rail import twin_recovery
                twin_recovery.ensure_all(rest[1])
                target=pub.OUTPUT
                if target.exists() and not (target/'manifest.json').is_file():
                    import shutil,time
                    preserved=root/'build/v06-loop/incomplete-publications'/str(time.time_ns());preserved.parent.mkdir(parents=True,exist_ok=True);shutil.move(target,preserved)
                pub.publish(rest[1])
                emit(twin_recovery.bind_publication(target));return 0
            raise ValueError('Use campaign create PATH, run ID [--max-jobs N], compare ID or publish ID')
        if command == 'legacy':
            return _module('legacy').main(rest, root=root)
        if command in ('plan', 'planning'):
            if not rest or rest in (['-h'], ['--help'], ['help']):
                print('Usage: ./osr plan COMMAND [arguments]\n\n'
                      '  compile EDITS.json --output DIR  Bind a GIS proposal to the selected v0.6 candidate\n'
                      '  verify DIR                       Verify handoff sources and identities\n'
                      '  serve [--port PORT]              Serve the local planning workspace\n\n'
                      'The handoff contains geography and unaccepted service proposals only. It does not\n'
                      'create v0.6 performance, procurement quantities, costs, or release evidence.')
                return 0
            action = rest[0]
            if action in ('-h', '--help', 'help'):
                return main(['plan', *rest[1:]], root=root)
            if action == 'compile':
                options = argparse.ArgumentParser(prog='./osr plan compile', description='Create a v0.6-bound planning handoff without importing historical train or cost results.')
                options.add_argument('bundle', type=Path, help='Planning edit bundle exported from the GIS workspace')
                options.add_argument('--output', type=Path, required=True, help='New repository-relative output directory')
                parsed = options.parse_args(rest[1:])
                bundle_path = checked_path(root, parsed.bundle)
                output_path = checked_path(root, parsed.output)
                from . import planning
                baseline = selected(root)
                current_summary, current_manifest = read_packet(root)
                result = planning.compile_bundle(root=root,
                    baseline=baseline, current_summary=current_summary, current_manifest=current_manifest,
                    bundle_path=bundle_path, output_path=output_path)
                emit(result)
                return 0
            if action == 'verify':
                options = argparse.ArgumentParser(prog='./osr plan verify', description='Verify a candidate-bound planning handoff and its source files.')
                options.add_argument('directory', type=Path, help='Repository-relative planning handoff directory')
                parsed = options.parse_args(rest[1:])
                directory = checked_path(root, parsed.directory)
                baseline = selected(root)
                current_summary, _ = read_packet(root)
                from . import planning
                emit(planning.verify_handoff(directory, root=root, baseline=baseline, current_summary=current_summary))
                return 0
            if action in ('serve', 'open'):
                return _module('server').main(rest[1:], root=root)
            return hold(root, 'plan ' + ' '.join(rest), 'Use ./osr plan compile EDITS.json --output DIR or ./osr plan serve')
        if command in ('status', 'readiness'):
            if rest and rest != ['--json']:
                return hold(root, command, 'Unsupported current status options')
            emit(status(root))
            return 0
        if command in ('build', 'run', 'cycle', 'publish', 'verify', 'check'):
            allowed = {'--force'} if command in ('build', 'run', 'cycle') else set()
            if set(rest) - allowed:
                return hold(root, command, 'Unsupported current command options')
            module = _module('publication')
            if command in ('build', 'run', 'cycle'):
                result = module.build(root=root, force='--force' in rest)
            elif command == 'publish':
                result = module.publish(root=root, output=root / OUTPUT)
            else:
                result = module.verify(root=root, output=root / OUTPUT)
            emit(result)
            return 0
        if command == 'release-check':
            return hold(root, command, 'Development adoption is not a manufacturing or operating release; physical qualification remains open')
        if command == 'book':
            if rest not in ([], ['--check']):
                return hold(root, command, 'Use ./osr book [--check] for the selected reader')
            emit(_module('book').build(root=root, output=root / 'OpenSourceRail-Book.pdf', check=bool(rest)))
            return 0
        if command in ('catalogue', 'capabilities'):
            if rest and rest not in (['status'], ['--json']):
                return hold(root, command, 'Current catalogue supports read-only status; use ./osr build to regenerate selected city packages')
            emit(_module('cities').read_catalogue(root=root))
            return 0
        if command in ('city', 'sim'):
            slug = rest[0] if rest else 'baghdad'
            if len(rest) > 1:
                return hold(root, command, 'Only a selected city slug is supported')
            module = _module('cities')
            # Both are the same explicitly analytical selected-city evaluator.
            # Neither command is a native dynamic or operational qualification.
            result = module.publish_city(slug, root=root) if command == 'city' else module.evaluate_city(slug, root=root)
            emit(result)
            return 3 if result.get('execution') == 'held' else 0
        if command == 'twin' and rest and rest[0] in ('compile', 'export'):
            baseline = selected(root)
            if len(rest) > 2 or (len(rest) == 2 and rest[1] != baseline['vehicle']['candidate_id']):
                return hold(root, 'twin ' + ' '.join(rest),
                            'Current twin exports require the exact selected physical candidate. Run ./osr build to regenerate them.')
            verification = _module('publication').verify(root=root, output=root / OUTPUT)
            read_packet(root)
            directory = checked_path(root, OUTPUT + '/exports')
            manifest = json.loads((directory / 'manifest.json').read_bytes())
            for key in IDS:
                if manifest.get(key) != baseline['vehicle'][key]:
                    raise CurrentUnavailable('Current twin uses a different ' + key)
            if manifest.get('selection_id') != baseline['selection_id']:
                raise CurrentUnavailable('Current twin uses a different selection')
            for key, value in FLAGS.items():
                if manifest.get(key) is not value:
                    raise CurrentUnavailable('Unsupported twin qualification disposition: ' + key)
            artifacts = []
            for name, expected in manifest['files_sha256'].items():
                path = checked_path(root, OUTPUT + '/exports/' + name)
                if digest(path) != expected:
                    raise CurrentUnavailable('Current twin artifact changed: ' + name)
                artifacts.append(str(path.relative_to(root)))
            emit(dict(schema='osr-current-twin-entrypoint/1', execution='verified-published-export',
                      action='read-only; ./osr build regenerates the selected exports',
                      selection_id=baseline['selection_id'],
                      **{key: baseline['vehicle'][key] for key in IDS},
                      development_default=True, manifest=manifest,
                      artifacts=artifacts, verification=verification, **FLAGS))
            return 0
        if command == 'trip':
            from engineering.trip_dynamics.__main__ import main as trip_main
            if not rest:
                return trip_main(['status', '--source-root', str(root)])
            action = rest[0]
            if action in ('-h', '--help'):
                return trip_main(rest)
            if action == 'run' and len(rest) > 1 and not rest[1].startswith('-'):
                return hold(root, 'trip ' + ' '.join(rest),
                    'Use the explicit bounded trip research options; a positional distance is not a current v0.6 journey run')
            supported = {'status', 'catalogue', 'cases', 'simulate', 'fixture', 'execute-job',
                'setup-tools', 'validate-map', 'validate-modal', 'epm', 'magnetic-confirmation',
                'run', 'verify', 'probe'}
            if action in supported:
                return trip_main([*rest, '--source-root', str(root)])
            if action == 'plan':
                return trip_main(rest)
            return hold(root, 'trip ' + ' '.join(rest),
                'Use ./osr trip --help for source-bound trip research actions; current v0.6 journey acceptance remains held')
        if command == 'twin':
            action = rest[0] if rest else 'status'
            if action in ('status', 'cases', 'catalogue', 'list'):
                emit(status(root))
                return 0
            return hold(root, command + ' ' + ' '.join(rest),
                        'This current-design action has no verified candidate-bound adapter. See ./osr status for actual gates; historical methods use ./osr legacy')
        if command == 'workbench':
            return _module('server').main(rest, root=root)
        if command == 'test':
            if rest:
                return hold(root, command, 'Current tests take no extra arguments')
            subprocess.run([sys.executable, '-m', 'pytest', '-q', '--import-mode=importlib',
                            str(Path(__file__).parent / 'tests'),
                            str(root / 'engineering/station_rail/tests')], cwd=root, check=True)
            emit(_module('publication').verify(root=root, output=root / OUTPUT))
            subprocess.run(['node', str(root / 'tools/automation/tests/verify-development-baseline.mjs')], cwd=root, check=True)
            return 0
        return hold(root, command, 'Unsupported current-design command; use ./osr --help or ./osr legacy for retained methods')
    except (OSError, ValueError, KeyError, ImportError, subprocess.CalledProcessError) as exc:
        emit(dict(schema='osr-default-entrypoint-error/1', execution='held',
                  requested_action=command, reason=str(exc), development_default=True, **FLAGS))
        return 3


if __name__ == '__main__':
    raise SystemExit(main())
