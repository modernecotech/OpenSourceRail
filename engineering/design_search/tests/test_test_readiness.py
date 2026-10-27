from copy import deepcopy
import json
from pathlib import Path
import pytest
from engineering.design_search import design_grammar, railway_bundle, route_bundle, test_readiness as t


@pytest.fixture(scope='module')
def body():
    return design_grammar.build(design_grammar.parameters())


def test_all_physical_tests_are_actionable_but_unexecuted_and_unapproved(body):
    bundle=railway_bundle.materialize(body);p=t.build(bundle)
    assert len(p['protocols'])==10 and p['executed_physical_tests']==0 and p['approved_numeric_limits']==0
    assert not p['native_dispatch_allowed'] and p['complete_equipped_vehicles']==0
    for row in p['protocols']:
        assert row['measured_channels'] and row['load_duty_environment'] and row['acceptance_criteria']
        assert row['subject_binding']['numerical_parent_bundle_id']==bundle['bundle_id']
        assert row['article_binding']['as_built_candidate_id'] is None and row['article_binding']['as_built_revision_required']
        assert row['executed'] is False and row['native_dispatch_allowed'] is False
        assert all(c['limit'] is None and c['approval_status']=='unassigned' for c in row['acceptance_criteria'])
        assert row['unaccepted_record_template']['accepted'] is False
    assert 'adapter' in p['qualification_admission']
    assert t.verify(p,bundle)['verified']


def test_route_and_architecture_change_scoped_requests_without_changing_approval(body):
    long=railway_bundle.materialize(body)
    short=route_bundle.materialize(body,distance_m=1500.)
    recovery=railway_bundle.materialize(body,family='P4')
    a,b,c=[t.build(v) for v in (long,short,recovery)]
    assert len({v['evaluation_id'] for v in (a,b,c)})==3
    assert b['protocols'][0]['planning_context']['station_spacing_m']==1500.
    assert c['protocols'][0]['planning_context']['unweighed_architecture_equipment']
    c['protocols'][0]['planning_context']['unweighed_architecture_equipment'].append('output-only edit')
    railway_bundle.validate(recovery)
    with pytest.raises(ValueError,match='exact candidate'):t.verify(a,short)
    motor=next(p for p in a['protocols'] if p['id']=='T05')
    journey=next(p for p in a['protocols'] if p['id']=='T08')
    assert motor['coordinate_definition']!=journey['coordinate_definition']


def test_resealed_planning_record_cannot_assert_acceptance_or_dispatch(body):
    bundle=railway_bundle.materialize(body);p=t.build(bundle)
    for field,value in [('physical_accepted',True),('executed_physical_tests',1),('native_dispatch_allowed',True)]:
        changed=deepcopy(p);changed[field]=value;changed.pop('evaluation_id');changed['evaluation_id']=t.identity(changed)
        with pytest.raises(ValueError):t.verify(changed,bundle)


def test_wheel_traction_cannot_receive_station_LIM_protocols(body):
    other=railway_bundle.materialize(body,family='P6')
    with pytest.raises(ValueError,match='another propulsion family'):t.build(other)


def test_definition_file_cannot_hide_measurements_approved_limits_or_missing_test_family(tmp_path):
    original=t.definitions();path=tmp_path/t.DEFINITIONS;path.parent.mkdir(parents=True)
    changes=[]
    q=deepcopy(original);q['protocols'][0]['acceptance_criteria'][0]['limit']=20000.;changes.append(q)
    q=deepcopy(original);q['protocols'][0]['raw_measurement_files']=['fictional.csv'];changes.append(q)
    q=deepcopy(original);q['protocols'][0]['executed']=True;changes.append(q)
    q=deepcopy(original);q['protocols'].pop();changes.append(q)
    q=deepcopy(original);q['protocols'][0]['measured_channels']=[];changes.append(q)
    q=deepcopy(original);q['protocols'][0]['acceptance_criteria'][0].pop('unit');changes.append(q)
    q=deepcopy(original);q['protocols'][0]['acceptance_criteria'][0]['observable']='';changes.append(q)
    for q in changes:
        path.write_text(json.dumps(q))
        with pytest.raises(ValueError):t.definitions(tmp_path)
