"""Connected-system scope and exact design reconstruction survive resealing."""
from copy import deepcopy
import shutil
import pytest

from engineering.assembly_design import baseline, complete_systems as systems, design_studies as studies
from engineering.twin_workflow import core


@pytest.fixture(scope='module')
def built(tmp_path_factory):
    # Keep these publication/adversarial tests independent of native execution;
    # the actual native carbody and bay have their own equipped-runner tests.
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(studies.study_confirmation, 'native', lambda *a: (None, 'hold', 'Intentionally unavailable fixture'))
        prepared = dict(policy=core.read(baseline.DATA))
        root = tmp_path_factory.mktemp('connected-systems')/'systems'
        value = systems.build(prepared, root)
    return root, prepared, value


@pytest.fixture
def package(tmp_path, built):
    original, prepared, value = built
    folder = tmp_path/'systems'
    shutil.copytree(original, folder)
    return folder, prepared, deepcopy(value)


def test_whole_geometric_exhibits_do_not_grant_full_design_completion(package):
    folder, prepared, value = package
    assert len(value['models']) == 2 and value['variant_count'] == 15
    assert all(m['native_state'] == 'hold' and not m['eligible_for_research'] for m in value['models'])
    assert all(m['assembly_media']['state'] == 'hold' for m in value['models'])
    assert not value['engineering_complete'] and not value['full_vehicle_equipment_complete']
    assert systems.verify(prepared, folder) == value


def test_installed_verifier_success_retains_actual_held_report_not_a_boolean(tmp_path,monkeypatch):
    from engineering.assembly_design import installed_geometry
    cassette=tmp_path/'cassette';cassette.mkdir()
    core.write(cassette/'result.json',dict(native_state='passed'))
    root=tmp_path/'systems';(root/'installed-geometry').mkdir(parents=True)
    held=dict(state='hold',geometry_state='passed',admitted_for_system_simulation=False,**core.FLAGS)
    core.write(root/'installed-geometry/result.json',held)
    monkeypatch.setattr(studies,'read_record',lambda *args:dict(revision='body'))
    calls=[]
    def verify(*args):
        calls.append(args)
        return True  # The native verifier's public API returns success, not a report.
    monkeypatch.setattr(installed_geometry,'verify',verify)
    result=systems.installed_check(root,[dict(kind='carbody-assembly',native_state='passed')],
        (dict(revision='cassette'),cassette,dict(revision='equipment')),verify=True)
    assert result==held and len(calls)==1 and result['admitted_for_system_simulation'] is False


@pytest.mark.parametrize('defect', ('dropped-rejection', 'part-geometry', 'hidden-failure', 'promoted', 'media', 'viewer', 'handoff'))
def test_inner_design_changes_fail_independently_of_outer_receipts(package, defect, monkeypatch):
    folder, prepared, value = package
    # Exercise corruption against the immutable, genuinely generated baseline
    # without repeatedly solving the same fifteen designs for each byte defect.
    # The positive test above uses the real controlled reconstruction, and each
    # generator/solver has separate adverse/numerical/native benchmarks.
    frozen=studies.read_record(folder,'variants.json')
    groups=[[(v['candidate'],v['assessment']) for v in frozen if v['candidate']['kind']==m['kind']]
            for m in value['models']]
    monkeypatch.setattr(systems,'alternatives',lambda prepared:deepcopy(groups))
    root = folder/value['models'][0]['kind']
    if defect == 'dropped-rejection':
        variants = studies.read_record(folder, 'variants.json')
        variants.pop()
        studies.write_record(folder, 'variants.json', variants)
        value['variant_count'] -= 1
        studies.write_record(folder, 'summary.json', value)
    elif defect == 'part-geometry':
        candidate = studies.read_record(root, 'candidate.json')
        candidate['contract']['parts'][0]['manufacturing']['primitives'][0]['dimensions_m'][0] += .001
        studies.write_record(root, 'candidate.json', candidate)
        studies.write_record(root, 'definition.json', candidate['contract'])
    elif defect == 'hidden-failure':
        assessment = studies.read_record(root, 'assessment.json')
        assessment['checks']['unreported-failure'] = False
        studies.write_record(root, 'assessment.json', assessment)
    elif defect in {'promoted', 'media'}:
        if defect == 'promoted': value['models'][0]['eligible_for_research'] = True
        else: value['models'][0]['assembly_media']['state'] = 'executed'
        core.write(root/'result.json', value['models'][0])
        studies.write_record(folder, 'summary.json', value)
    elif defect == 'viewer': (folder/'index.html').write_text('The railway is complete')
    else: (root/'manufacturing-bom.csv').write_text('Wrong material and mass')
    with pytest.raises(ValueError): systems.verify(prepared, folder)


def _failed_history(folder, value):
    """Genuine controlled bytes, with an explicit simulated native failure."""
    model = value['models'][0]
    path = 'failed-native/exact-selected-revision'
    shutil.copytree(folder/model['kind'], folder/path)
    result = deepcopy(model)
    result.update(native_state='failed', eligible_for_research=False,
        native_error='Deliberate failure-history fixture; no geometry result inferred')
    core.write(folder/path/'result.json', result)
    return dict(path=path, result=result)


def test_known_failed_revision_vetoes_selected_exhibit_even_after_resealing(package, monkeypatch):
    folder, prepared, value = package
    frozen = studies.read_record(folder, 'variants.json')
    groups = [[(v['candidate'], v['assessment']) for v in frozen if v['candidate']['kind'] == m['kind']]
        for m in value['models']]
    monkeypatch.setattr(systems, 'alternatives', lambda prepared: deepcopy(groups))
    diagnostic = _failed_history(folder, value)
    # The diagnostic itself is exactly bound and valid. It must still veto
    # selecting that same revision, including a later passing/held observation.
    assert systems._verify_diagnostic(folder, diagnostic, frozen) == value['models'][0]['candidate_revision']
    value['native_diagnostics'] = [diagnostic]
    studies.write_record(folder, 'summary.json', value)
    with pytest.raises(ValueError, match='failed native history'):
        systems.verify(prepared, folder)


@pytest.mark.parametrize('field', ('candidate_revision', 'kind', 'parts', 'scope', 'failed_checks', 'definition', 'manufacturing_release'))
def test_native_diagnostic_cannot_blacklist_another_revision_or_change_scope(package, field):
    folder, prepared, value = package
    frozen = studies.read_record(folder, 'variants.json')
    diagnostic = _failed_history(folder, value)
    result = diagnostic['result']
    if field == 'candidate_revision':
        other = next(v for v in frozen if v['candidate']['revision'] != result['candidate_revision'])
        result[field] = other['candidate']['revision']
    elif field == 'parts': result[field] += 1
    elif field == 'failed_checks': result[field] = ['fabricated-rejection']
    elif field == 'definition':
        definition = studies.read_record(folder/diagnostic['path'], 'definition.json')
        definition['name'] = 'Different physical definition'
        studies.write_record(folder/diagnostic['path'], 'definition.json', definition)
    elif field == 'manufacturing_release': result[field] = True
    else: result[field] = 'different'
    core.write(folder/diagnostic['path']/'result.json', result)
    with pytest.raises(ValueError):
        systems._verify_diagnostic(folder, diagnostic, frozen)
