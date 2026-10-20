"""Connected provisional carbody/civil exhibits in the existing qualified epoch.

Complete geometric scope is distinguished from engineering completion. These
models do not replace the adopted vehicle mass or the accepted civil load path.
Every explored recipe, including failed alternatives, remains available.
"""
from pathlib import Path
import json
import csv
import io
import gzip
import tempfile

from engineering.twin_workflow import core


def adapters():
    from . import carbody_assembly, civil_assembly
    return (carbody_assembly, civil_assembly)


def alternatives(prepared):
    policy = prepared['policy']
    groups = []
    for adapter in adapters():
        pairs = []
        for variables in adapter.candidates(policy):
            candidate = adapter.build(policy, variables)
            assessment = adapter.evaluate(policy, candidate)
            pairs.append((json.loads(core.encoded(candidate)), json.loads(core.encoded(assessment))))
        if not pairs:
            raise ValueError('bounded connected-system domain required')
        groups.append(pairs)
    return groups


def comparison(pairs):
    stream=io.StringIO()
    fields=['candidate_revision','variables','represented_mass_kg','complete_installed_mass_kg','installed_cost_usd','failed_screens','open_checks','scope']
    writer=csv.DictWriter(stream,fieldnames=fields);writer.writeheader()
    for candidate,assessment in pairs:
        writer.writerow(dict(candidate_revision=candidate['revision'],variables=json.dumps(candidate['variables'],sort_keys=True),
            represented_mass_kg=sum(p['properties']['mass_kg'] for p in candidate['contract']['parts']),
            complete_installed_mass_kg='unknown',installed_cost_usd='unknown',
            failed_screens='; '.join(assessment['failed_checks']),open_checks='; '.join(assessment['held_checks']),
            scope=candidate['source_scope']))
    return stream.getvalue()


def _exhibits(folder, models):
    from . import design_studies as studies
    exhibits = []
    for model in models:
        path = model['kind']
        candidate = studies.read_record(Path(folder)/path, 'candidate.json')
        assessment = studies.read_record(Path(folder)/path, 'assessment.json')
        entry = dict(candidate=candidate, assessment=assessment, result=model, path=path)
        if model['native_state'] == 'passed':
            with studies.exchange_files(Path(folder)/path/'bim') as paths:
                entry['mesh'] = core.read(paths['native-mesh.json'], maximum=60_000_000)
        exhibits.append(entry)
    return exhibits


def installed_check(folder, models, installed, *, verify=False):
    """A joint configuration has its own eligibility; zero overlap is no release."""
    from . import installed_geometry
    if installed is None:
        return dict(state='hold', geometry_state='hold', reason='Exact installed equipment/native inputs not provided',
            admitted_for_system_simulation=False, **core.FLAGS)
    candidate, cassette_root, equipment = installed
    body = next(m for m in models if m['kind']=='carbody-assembly')
    cassette_result = core.read(Path(cassette_root)/'result.json')
    if body['native_state']!='passed' or cassette_result['native_state']!='passed':
        return dict(state='hold', geometry_state='hold', reason='Installed configuration awaits both native confirmations',
            admitted_for_system_simulation=False, **core.FLAGS)
    from . import design_studies as studies
    body_root = Path(folder)/body['kind']
    body_candidate = studies.read_record(body_root, 'candidate.json')
    operation = installed_geometry.verify if verify else installed_geometry.build
    result = operation(body_candidate, body_root/'native/candidate.FCStd',
        candidate, Path(cassette_root)/'native/candidate.FCStd', equipment, Path(folder)/'installed-geometry')
    return core.read(Path(folder)/'installed-geometry/result.json',maximum=20_000_000) if verify else result


def build(prepared, folder, *, installed=None):
    from . import design_studies as studies, assembly_media, design_explorer
    folder = Path(folder)
    folder.mkdir()
    groups = alternatives(prepared)
    models, diagnostics = [], []
    for pairs in groups:
        pair, model, failed = studies.confirm_alternatives(pairs, folder)
        diagnostics.extend(failed)
        root = folder/model['kind']
        (root/'alternatives.csv').write_text(comparison(pairs))
        if model['native_state'] == 'passed':
            with studies.exchange_files(root/'bim') as paths:
                model['assembly_media'] = assembly_media.build(pair[0], paths['native-mesh.json'], root)
        else:
            model['assembly_media'] = dict(state='hold', reason='Native geometry not confirmed',
                scope=assembly_media.SCOPE, **core.FLAGS)
        core.write(root/'result.json', model)
        models.append(model)
    variants = [dict(candidate=candidate, assessment=assessment) for pairs in groups for candidate, assessment in pairs]
    # Compact JSON retains every raw case but avoids whitespace multiplying a
    # full multi-load frame history across fifteen alternatives.
    (folder/'variants.json.gz').write_bytes(gzip.compress(json.dumps(variants,separators=(',',':'),allow_nan=False).encode(),mtime=0))
    value = dict(schema='osr-connected-system-studies/1', epoch=core.digest(prepared),
        models=models, native_diagnostics=diagnostics, variant_count=len(variants),
        selection='Exhibit selection excludes known failed screens where alternatives exist; unknown costs and engineering holds are not zero or acceptance',
        engineering_complete=False, full_vehicle_equipment_complete=False, **core.FLAGS)
    value['installed_geometry'] = installed_check(folder, models, installed)
    studies.write_record(folder, 'summary.json', value)
    design_explorer.build(folder, _exhibits(folder, models))
    return value


def _verify_model(root, candidate, assessment, model):
    from hashlib import sha256
    import gzip
    from . import design_studies as studies, workflow, bim, assembly_media
    if model != core.read(root/'result.json') or studies.read_record(root, 'candidate.json') != candidate:
        raise ValueError('connected-system candidate identity differs')
    if studies.read_record(root, 'assessment.json') != assessment or studies.read_record(root, 'definition.json') != candidate['contract']:
        raise ValueError('connected-system geometry or checks differ')
    if any(item.get(k) is not False for item in (candidate, assessment, model) for k in core.FLAGS):
        raise ValueError('connected-system exhibit cannot assert engineering release')
    if model['candidate_revision'] != candidate['revision'] or model['kind'] != candidate['kind'] or model['parts'] != len(candidate['contract']['parts']):
        raise ValueError('connected-system counts or revision differ')
    if model['scope'] != candidate['source_scope'] or model['failed_checks'] != assessment['failed_checks'] or model['held_checks'] != assessment['held_checks']:
        raise ValueError('connected-system scope or exclusions differ')
    if model['eligible_for_research'] != (model['native_state'] == 'passed' and not assessment['failed_checks']):
        raise ValueError('connected-system failed exhibit promoted')
    if studies.read_record(root, 'qa-plan.json') != candidate['qa_plan']:
        raise ValueError('connected-system inspection plan differs')
    frame=assessment.get('supplemental_evidence',{}).get('carbody-frame')
    if frame is not None:
        if studies.read_record(root,'carbody-frame.json')!=frame or model.get('frame_response_sha256')!=core.sha(root/'frame-response.png'):
            raise ValueError('connected-frame analytical evidence or plot differs')
    with tempfile.TemporaryDirectory(prefix='osr-system-handoff-') as temporary:
        workflow.tables(candidate, Path(temporary))
        for name in ('manufacturing-bom.csv', 'inspection.svg'):
            if (Path(temporary)/name).read_bytes() != (root/name).read_bytes():
                raise ValueError('connected-system BOM or drawing differs')
    if model['native_state'] == 'passed':
        proof = core.read(root/'native/native-cad.json', maximum=10_000_000)
        if proof != model['native_proof'] or proof['input_sha256'] != core.digest(candidate['contract']):
            raise ValueError('connected-system native proof differs')
        if any(proof.get(k) is not True for k in ('physical_ids_preserved', 'native_reopened', 'step_volume_reconciled', 'manufacturing_unit_ids_preserved')):
            raise ValueError('connected-system native correspondence failed')
        if proof['files_sha256']['candidate.FCStd'] != core.sha(root/'native/candidate.FCStd') or proof['files_sha256']['candidate.step'] != sha256(gzip.decompress((root/'model.step.gz').read_bytes())).hexdigest():
            raise ValueError('connected-system native/STEP bytes differ')
        if core.sha(root/'model.step.gz') != model['native_step_compressed_sha256']:
            raise ValueError('connected-system compressed STEP differs')
        with studies.exchange_files(root/'bim') as paths:
            check = bim.verify(candidate, paths['assembly.ifc'], ids_path=paths['requirements.ids'])
            receipt = core.read(root/'bim/receipt.json')
            if check['state'] != 'information-pass' or check != core.read(root/'bim/ids-report.json'):
                raise ValueError('connected-system IFC information differs')
            if receipt['candidate_revision'] != candidate['revision'] or receipt['source_cad_sha256'] != core.sha(root/'native/candidate.FCStd'):
                raise ValueError('connected-system IFC source differs')
            if any(receipt['files_sha256'][name] != core.sha(path) for name, path in paths.items()):
                raise ValueError('connected-system native exchange bytes differ')
            studies.verify_exchange_mesh(candidate, root/'bim', paths=paths)
            assembly_media.verify(candidate, paths['native-mesh.json'], root, model['assembly_media'])
    elif model['assembly_media']['state'] != 'hold':
        raise ValueError('unconfirmed geometry cannot support assembly media')


def verify(prepared, folder, *, installed=None):
    from . import design_studies as studies, design_explorer
    folder = Path(folder)
    value = studies.read_record(folder, 'summary.json')
    if value['epoch'] != core.digest(prepared) or value['engineering_complete'] is not False or value['full_vehicle_equipment_complete'] is not False:
        raise ValueError('connected-system source or completion differs')
    if any(value.get(k) is not False for k in core.FLAGS):
        raise ValueError('connected-system cannot assert release')
    groups = alternatives(prepared)
    variants = [dict(candidate=candidate, assessment=assessment) for pairs in groups for candidate, assessment in pairs]
    if studies.read_record(folder, 'variants.json') != variants or value['variant_count'] != len(variants):
        raise ValueError('connected-system alternatives differ from controlled generator')
    if len(value['models']) != len(groups):
        raise ValueError('connected-system family coverage differs')
    for pairs, model in zip(groups, value['models']):
        matches = [(c, a) for c, a in pairs if c['revision'] == model['candidate_revision']]
        if len(matches) != 1:
            raise ValueError('connected-system exhibit outside controlled domain')
        candidate, assessment = matches[0]
        _verify_model(folder/model['kind'], candidate, assessment, model)
        if (folder/model['kind']/'alternatives.csv').read_bytes()!=comparison(pairs).encode():
            raise ValueError('connected-system comparison differs')
        failed_native = {d['result']['candidate_revision'] for d in value['native_diagnostics']}
        if assessment['failed_checks'] and any(not a['failed_checks'] and c['revision'] not in failed_native for c, a in pairs):
            raise ValueError('failed system selected over available passing screens')
    for diagnostic in value['native_diagnostics']:
        path = diagnostic['path']
        if not path.startswith('failed-native/') or Path(path).is_absolute() or '..' in Path(path).parts:
            raise ValueError('unsafe connected-system diagnostic path')
        result = diagnostic['result']
        if result != core.read(folder/path/'result.json') or result['native_state'] != 'failed' or result['eligible_for_research'] is not False:
            raise ValueError('connected-system native failure changed or promoted')
        if not any(v['candidate'] == studies.read_record(folder/path, 'candidate.json') and v['assessment'] == studies.read_record(folder/path, 'assessment.json') for v in variants):
            raise ValueError('connected-system diagnostic outside domain')
    if value['installed_geometry'] != installed_check(folder, value['models'], installed, verify=True):
        raise ValueError('installed configuration geometry or eligibility differs')
    # Regenerate the static UI from exact retained geometry and checks. A forged
    # UI cannot become valid just by refreshing outer package checksums.
    with tempfile.TemporaryDirectory(prefix='osr-system-ui-') as temporary:
        expected = Path(temporary)
        design_explorer.build(expected, _exhibits(folder, value['models']), asset_root=folder)
        for name in ('index.html', 'explorer-data.json'):
            if (folder/name).read_bytes() != (expected/name).read_bytes():
                raise ValueError('connected-system explorer differs from retained evidence')
    return value
