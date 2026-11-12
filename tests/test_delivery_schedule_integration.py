"""Explicit production delivery backend keeps physical identity and resource claims."""
import importlib.util,json,os
from pathlib import Path
import pytest
ROOT=Path(__file__).parents[1]
spec=importlib.util.spec_from_file_location('delivery_fixture',ROOT/'tests/test_outline_delivery_plan.py')
fixture=importlib.util.module_from_spec(spec);spec.loader.exec_module(fixture)
from engineering.outline import delivery_plan as dp


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


def test_direct_run_retains_stale_input_failure_and_does_not_relabel(tmp_path,monkeypatch):
    import engineering.performance
    monkeypatch.setattr(engineering.performance,'disk_admission',lambda *a,**k:{'admitted':True})
    record=fixture.city();record['source_sha256']={'missing-source':'f'*64};record.pop('evaluation_id');dp.seal(record,'evaluation_id')
    request=tmp_path/'request.json';request.write_bytes(dp.encoded(record));output=tmp_path/'failed'
    with pytest.raises(FileNotFoundError):dp.run_delivery(request,output,root=ROOT)
    assert (output/'request.json').read_bytes()==request.read_bytes()
    assert json.loads((output/'failure.json').read_bytes())['execution']=='failed'
    assert not (output/'delivery-plan.json').exists()


def test_direct_run_refuses_source_checkout_output():
    with pytest.raises(ValueError,match='External fresh'):
        dp.run_delivery(ROOT/'unused',ROOT/'in-source-output',root=ROOT)
