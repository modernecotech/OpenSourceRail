"""Manufacturing/joint evidence cannot gain validity from resealing its files."""
from copy import deepcopy
import shutil

import pytest

from engineering.assembly_design import baseline, carbody_assembly, carbody_frame
from engineering.assembly_design import connection_studies as connections, design_studies as studies
from engineering.twin_workflow import core


@pytest.fixture(scope='module')
def generated(tmp_path_factory):
    policy = core.read(baseline.DATA)
    candidate = carbody_assembly.build(policy, list(carbody_assembly.candidates(policy))[4])
    frame = carbody_frame.report(candidate)
    folder = tmp_path_factory.mktemp('joint-companion')/'systems'
    folder.mkdir()
    (folder/'carbody-assembly').mkdir()
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(studies.study_confirmation, 'native', lambda *a: (None, 'hold', 'Deliberate unavailable-native fixture'))
        value = connections.build(dict(policy=policy), folder/'connections', candidate, frame)
    return folder, dict(policy=policy), candidate, frame, value


@pytest.fixture
def package(tmp_path, generated):
    source, prepared, candidate, frame, value = generated
    folder = tmp_path/'systems'
    shutil.copytree(source, folder)
    return folder, prepared, candidate, frame, deepcopy(value)


def test_exact_bound_connections_preserve_defects_and_holds(package):
    folder, prepared, candidate, frame, value = package
    assert len(value['models']) == value['variant_count'] == 3
    assert all(m['native_state'] == 'hold' and not m['eligible_for_research'] for m in value['models'])
    defects = [m for m in value['models'] if 'full' not in m['kind']]
    assert len(defects) == 2 and all(m['failed_checks'] for m in defects)
    assert not value['installed_connection_qualified']
    assert all(value[k] is False for k in core.FLAGS)
    assert connections.verify(prepared, folder/'connections', candidate, frame) == value
    exhibits = connections.exhibits(folder, value)
    assert len(exhibits) == 3 and all(e['path'].startswith('connections/') for e in exhibits)


@pytest.mark.parametrize('defect', ('response', 'demands', 'missing-defect', 'promoted-defect', 'displayed-plot', 'source-card', 'section-drawing', 'displayed-comparison', 'displayed-demands'))
def test_resealed_connection_evidence_is_reconstructed(package, defect):
    folder, prepared, candidate, frame, value = package
    root = folder/'connections'
    if defect in {'response', 'demands'}:
        name = 'joint-response.json' if defect == 'response' else 'splice-demands.json'
        report = studies.read_record(root, name)
        report['candidate_revision'] = '0'*64
        studies.write_record(root, name, report)
    elif defect == 'missing-defect':
        value['models'].pop(0)
        value['variant_count'] -= 1
        studies.write_record(root, 'summary.json', value)
    elif defect == 'promoted-defect':
        value['models'][0]['eligible_for_research'] = True
        core.write(root/value['models'][0]['kind']/'result.json', value['models'][0])
        studies.write_record(root, 'summary.json', value)
    elif defect == 'displayed-plot':
        (folder/'carbody-assembly/joint-response.png').write_bytes(b'fabricated favourable plot')
    elif defect == 'source-card':
        refs = core.read(root/'reference-sources.json')
        refs['sources'][0]['approved'] = True
        core.write(root/'reference-sources.json', refs)
    else:
        coupon = root/value['models'][0]['kind']
        if defect == 'section-drawing':
            (coupon/'splice-section.svg').write_text('<svg>All gaps are filled</svg>')
        elif defect == 'displayed-comparison':
            (coupon/'alternatives.csv').write_text('No defects')
        else:
            studies.write_record(coupon, 'splice-demands.json', dict(adopted_joint_demands=True))
    with pytest.raises(ValueError):
        connections.verify(prepared, root, candidate, frame)
