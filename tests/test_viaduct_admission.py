from copy import deepcopy
import pytest
from engineering.station_rail.common import identity
from engineering.design_search.craft_backends import viaduct_admission as gate


def seal(value,key):
    value.pop(key,None);value[key]=identity(value);return value


def records():
    case=dict(case_id='box',candidate_id='physical',component_geometry_id='geometry',case_definition_id='case',**gate.FLAGS)
    request=seal(dict(cases=[case],evaluations=[dict(evaluation_id='evaluation')],limits=dict(maximum_native_processes=16),**gate.FLAGS),'request_id')
    row=dict(candidate_id='physical',component_geometry_id='geometry',evaluation_id='evaluation',execution='completed',
        diagnostic=dict(comparison_passed=True),exact_step=dict(comparison_passed=True),**gate.FLAGS)
    manifest=seal(dict(request_id=request['request_id'],cases=dict(box=row),case_count=1,
        nominal_geometry_comparison_passed=True,native_processes=2,fresh_native_processes=2,cached_native_evaluations=0,
        default_backend_changed=False,complete_bridge_analysis=False,artifact_sha256={'request.json':'sha'},**gate.FLAGS),'result_id')
    return manifest,request,[dict(execution='executed',returncode=0),dict(execution='completed',returncode=0)],{'request.json':'sha'}


def test_recompute_summary_without_native_execution():
    values=records();original=deepcopy(values)
    assert gate.check_claims(*values)
    assert values==original


@pytest.mark.parametrize('change,match',[
    (lambda m:m.update(nominal_geometry_comparison_passed=False),'aggregate'),
    (lambda m:m.update(native_processes=1),'execution accounting'),
    (lambda m:m.update(cached_native_evaluations=2),'execution accounting'),
    (lambda m:m.update(case_count=2),'coverage'),
    (lambda m:m['cases']['box'].update(evaluation_id='other'),'evaluation'),
    (lambda m:m['cases']['box']['exact_step'].update(physical_accepted=True),'promote'),
    (lambda m:m.update(default_backend_changed=True),'select a default'),
])
def test_resealed_misleading_claims_are_rejected(change,match):
    m,r,e,i=records();change(m);seal(m,'result_id')
    with pytest.raises(ValueError,match=match):gate.check_claims(m,r,e,i)


def test_failed_execution_and_unlisted_nested_manifest_are_not_hidden():
    m,r,e,i=records();e[0].update(execution='failed',returncode=1)
    with pytest.raises(ValueError,match='recorded executions'):gate.check_claims(m,r,e,i)
    m,r,e,i=records();i['nested/manifest.json']='unlisted'
    with pytest.raises(ValueError,match='nested manifests'):gate.check_claims(m,r,e,i)
