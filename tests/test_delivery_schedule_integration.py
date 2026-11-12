"""Explicit production delivery backend keeps physical identity and resource claims."""
import importlib.util,json,os
from pathlib import Path
import pytest
SOURCE_ROOT=Path(__file__).parents[1]
ROOT=SOURCE_ROOT
spec=importlib.util.spec_from_file_location('delivery_fixture',ROOT/'tests/test_outline_delivery_plan.py')
fixture=importlib.util.module_from_spec(spec);spec.loader.exec_module(fixture)
from engineering.outline import delivery_plan as dp
ROOT=dp.ROOT


def test_python_default_records_zero_helpers_and_unchanged_physical_ids():
    c=fixture.city();p=dp.evaluate(c,root=ROOT)
    assert p['scheduler_backend']['backend']=='python'
    assert p['scheduler_backend']['native_helper_jobs']==0
    assert p['reference_candidate_ids']==c['reference_candidate_ids']
    assert p['research_configuration_id']==c['research_configuration_id']
    assert p['assumptions']['native_solver_jobs']==0


@pytest.mark.parametrize('backend,binary,reason',[('invalid',None,'Known explicit'),('rust',None,'prebuilt'),('python','unused','does not accept')])
def test_backend_requests_refused_without_fallback(backend,binary,reason):
    with pytest.raises(ValueError,match=reason):
        dp.evaluate(fixture.city(),root=ROOT,scheduler_backend=backend,scheduler_binary=binary)


def test_explicit_unavailable_binary_is_refused():
    with pytest.raises(FileNotFoundError):
        dp.evaluate(fixture.city(),root=ROOT,scheduler_backend='rust',scheduler_binary=ROOT/'does-not-exist')


def test_native_complete_compilation_has_only_evaluation_differences():
    binary=os.environ.get('OSR_SCHEDULE_BINARY')
    if not binary:pytest.skip('Explicit prebuilt verified binary required; never auto-build')
    c=fixture.city();py=dp.evaluate(c,root=ROOT)
    rs=dp.evaluate(c,root=ROOT,scheduler_backend='rust',scheduler_binary=binary)
    for key in ('plan_id','scheduler_backend','source_sha256'):
        py.pop(key);rs.pop(key)
    assert dp.encoded(py)==dp.encoded(rs)
    assert rs['reference_candidate_ids']==c['reference_candidate_ids']


def test_direct_run_rejects_unbound_raw_record(tmp_path,monkeypatch):
    import engineering.performance
    monkeypatch.setattr(engineering.performance,'disk_admission',lambda *a,**k:{'admitted':True})
    request=tmp_path/'raw-record.json';request.write_bytes(dp.encoded(fixture.city()))
    with pytest.raises(ValueError,match='study directory'):
        dp.run_delivery(request,tmp_path/'not-created',root=ROOT)
    assert not (tmp_path/'not-created').exists()


@pytest.fixture
def current_packet():
    path=os.environ.get('OSR_DELIVERY_STUDY')
    if not path:pytest.skip('Explicit fresh admitted city-study packet required; no implicit regeneration')
    return Path(path)


def test_public_run_equals_verified_record(current_packet,tmp_path,monkeypatch):
    import engineering.performance
    from engineering.outline import city_workflow
    monkeypatch.setattr(engineering.performance,'disk_admission',lambda *a,**k:{'admitted':True})
    manifest=city_workflow.verify(current_packet,root=ROOT)
    expected=dp.evaluate(city_workflow.read_json(current_packet,'result.json')['city_outline'],root=ROOT)
    result=dp.run_delivery(current_packet,tmp_path/'compiled',root=ROOT)
    actual=json.loads((tmp_path/'compiled/delivery-plan.json').read_bytes())
    assert dp.encoded(actual)==dp.encoded(expected)
    assert result['upstream']['manifest_id']==manifest['manifest_id']
    assert result['native_helper_jobs']==0
    assert result['measurements']['own_cpu_seconds']>=0


@pytest.mark.parametrize('tamper',['source','artifact'])
def test_public_run_rejects_stale_or_tampered_packet(current_packet,tmp_path,monkeypatch,tamper):
    import shutil,engineering.performance
    from engineering.outline import city_workflow
    monkeypatch.setattr(engineering.performance,'disk_admission',lambda *a,**k:{'admitted':True})
    copy=tmp_path/'packet';shutil.copytree(current_packet,copy)
    if tamper=='source':
        path=copy/'manifest.json';m=json.loads(path.read_bytes())
        name=next(iter(m['source_sha256']));m['source_sha256'][name]='f'*64
        m.pop('manifest_id');m['manifest_id']=dp.identity(m);path.write_bytes(dp.encoded(m))
    else:
        path=copy/'summary.json';path.write_bytes(path.read_bytes()+b' ')
    with pytest.raises(ValueError):dp.run_delivery(copy,tmp_path/'failed',root=ROOT)
    assert (tmp_path/'failed/upstream-manifest.json').is_file()
    assert json.loads((tmp_path/'failed/failure.json').read_bytes())['execution']=='failed'
    assert not (tmp_path/'failed/delivery-plan.json').exists()


def test_direct_run_refuses_source_checkout_output():
    with pytest.raises(ValueError,match='External fresh'):
        dp.run_delivery(ROOT/'unused',ROOT/'in-source-output',root=ROOT)
