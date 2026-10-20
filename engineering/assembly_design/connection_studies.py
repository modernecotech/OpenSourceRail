"""Revision-bound joint compliance and manufacturing coupons in one design epoch.

Finite stiffness is a sensitivity, not a measured joint law. Weld coupons are
separate research fixtures, including deliberately defective penetration cases;
their geometry never replaces an installed vehicle connection or acceptance.
"""
from pathlib import Path
import shutil
import tempfile

from engineering.twin_workflow import core

SOURCES = Path(__file__).parent/'data/carbody-connection-sources.json'


def _body(folder, models):
    from . import design_studies as studies
    model = next(m for m in models if m['kind'] == 'carbody-assembly')
    root = Path(folder)/model['kind']
    candidate = studies.read_record(root, 'candidate.json')
    assessment = studies.read_record(root, 'assessment.json')
    return candidate, assessment['supplemental_evidence']['carbody-frame']


def build(prepared, folder, candidate, frame_report):
    from . import carbody_joint_response as response, carbody_splice as splice
    from . import design_studies as studies, assembly_media, complete_systems
    folder = Path(folder)
    folder.mkdir()
    joint = response.report(candidate, frame_report=frame_report)
    studies.write_record(folder, 'joint-response.json', joint)
    response.plot(joint, folder/'joint-response.png')
    body_folder = folder.parent/'carbody-assembly'
    studies.write_record(body_folder, 'joint-response.json', joint)
    shutil.copyfile(folder/'joint-response.png', body_folder/'joint-response.png')
    core.write(folder/'reference-sources.json', core.read(SOURCES))
    demands = splice.demand_register(candidate, frame_report=frame_report)
    studies.write_record(folder, 'splice-demands.json', demands)
    models, pairs = [], []
    for variables in splice.candidates(prepared['policy']):
        coupon = splice.build(prepared['policy'], variables, carbody=candidate, frame_report=frame_report)
        assessment = splice.evaluate(prepared['policy'], coupon)
        root = folder/coupon['kind']
        model = studies._model(coupon, assessment, root)
        (root/'splice-section.svg').write_text(splice.section_svg(coupon))
        studies.write_record(root, 'splice-demands.json', demands)
        if model['native_state'] == 'passed':
            with studies.exchange_files(root/'bim') as paths:
                model['assembly_media'] = assembly_media.build(coupon, paths['native-mesh.json'], root)
        else:
            model['assembly_media'] = dict(state='hold', reason='Native coupon geometry not confirmed',
                scope=assembly_media.SCOPE, **core.FLAGS)
        core.write(root/'result.json', model)
        models.append(model)
        pairs.append((coupon, assessment))
    comparison = complete_systems.comparison(pairs)
    (folder/'alternatives.csv').write_text(comparison)
    for model in models:
        (folder/model['kind']/'alternatives.csv').write_text(comparison)
    value = dict(schema='osr-carbody-connection-studies/1',
        carbody_revision=candidate['revision'], frame_report_sha256=core.digest(frame_report),
        joint_response_sha256=core.digest(joint), splice_demands_sha256=core.digest(demands),
        reference_sources_sha256=core.sha(SOURCES), response_plot_sha256=core.sha(folder/'joint-response.png'),
        models=models, variant_count=len(pairs),
        scope='Finite joint-stiffness sensitivities and separate weld-penetration coupons; no measured joint law, installed weld preparation, resistance, fatigue or physical acceptance',
        installed_connection_qualified=False, **core.FLAGS)
    studies.write_record(folder, 'summary.json', value)
    return value


def verify(prepared, folder, candidate, frame_report):
    from . import carbody_joint_response as response, carbody_splice as splice
    from . import design_studies as studies, complete_systems
    folder = Path(folder)
    actual = studies.read_record(folder, 'summary.json')
    joint = response.report(candidate, frame_report=frame_report)
    demands = splice.demand_register(candidate, frame_report=frame_report)
    if studies.read_record(folder, 'joint-response.json') != joint:
        raise ValueError('joint response differs from exact candidate/source/loads')
    body_folder = folder.parent/'carbody-assembly'
    if studies.read_record(body_folder, 'joint-response.json') != joint or core.sha(body_folder/'joint-response.png') != core.sha(folder/'joint-response.png'):
        raise ValueError('displayed body joint evidence differs')
    if studies.read_record(folder, 'splice-demands.json') != demands:
        raise ValueError('splice demands differ from exact candidate and simultaneous cases')
    if core.read(folder/'reference-sources.json') != core.read(SOURCES):
        raise ValueError('connection manufacturing source references changed')
    models = actual['models']
    recipes = list(splice.candidates(prepared['policy']))
    if len(models) != len(recipes):
        raise ValueError('connection coupon alternative omitted')
    pairs = []
    for variables, model in zip(recipes, models):
        coupon = splice.build(prepared['policy'], variables, carbody=candidate, frame_report=frame_report)
        assessment = splice.evaluate(prepared['policy'], coupon)
        complete_systems._verify_model(folder/coupon['kind'], coupon, assessment, model)
        if (folder/coupon['kind']/'splice-section.svg').read_bytes() != splice.section_svg(coupon).encode():
            raise ValueError('coupon section drawing differs from represented material')
        if studies.read_record(folder/coupon['kind'], 'splice-demands.json') != demands:
            raise ValueError('displayed coupon demands differ from exact member cuts')
        pairs.append((coupon, assessment))
    comparison = complete_systems.comparison(pairs).encode()
    if (folder/'alternatives.csv').read_bytes() != comparison:
        raise ValueError('connection coupon comparison differs')
    if any((folder/model['kind']/'alternatives.csv').read_bytes() != comparison for model in models):
        raise ValueError('displayed coupon comparison differs')
    expected = dict(schema='osr-carbody-connection-studies/1',
        carbody_revision=candidate['revision'], frame_report_sha256=core.digest(frame_report),
        joint_response_sha256=core.digest(joint), splice_demands_sha256=core.digest(demands),
        reference_sources_sha256=core.sha(SOURCES), response_plot_sha256=core.sha(folder/'joint-response.png'),
        models=models, variant_count=len(pairs),
        scope='Finite joint-stiffness sensitivities and separate weld-penetration coupons; no measured joint law, installed weld preparation, resistance, fatigue or physical acceptance',
        installed_connection_qualified=False, **core.FLAGS)
    if actual != expected:
        raise ValueError('connection-study identity or scope differs')
    with tempfile.TemporaryDirectory(prefix='osr-connection-plot-') as temp:
        image = Path(temp)/'joint-response.png'
        response.plot(joint, image)
        if core.sha(image) != expected['response_plot_sha256']:
            raise ValueError('connection response plot differs from retained numerical cases')
    return actual


def exhibits(folder, value):
    from . import complete_systems
    rows = complete_systems._exhibits(Path(folder)/'connections', value['models'])
    for row in rows:
        row['path'] = 'connections/'+row['path']
    return rows
