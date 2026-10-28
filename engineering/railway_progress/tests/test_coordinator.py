"""Scoped real V1 journeys exercise persistent replay without ten full cases."""
from copy import deepcopy
from pathlib import Path
import shutil
import pytest
from engineering.reference_cell import vehicles
from engineering.railway_progress import coordinator as c,journey,identity,digest,FLAGS,ROOT


@pytest.fixture(scope='module')
def campaign(tmp_path_factory):
    vehicle=vehicles.evaluate('V1');folder=tmp_path_factory.mktemp('continuing-source-bound')/'state'
    request=dict(vehicle_id='V1',distance_m=2000.,kind='station-pinch-rollers')
    epoch={'engineering/reference_cell/vehicles.py':digest(ROOT/'engineering/reference_cell/vehicles.py')}
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(c,'sources',lambda root=ROOT:dict(epoch))
        mp.setattr(c,'plan',lambda:dict(requests=[deepcopy(request)]))
        mp.setattr(c.vehicles,'evaluate',lambda vid,root=ROOT:deepcopy(vehicle))
        mp.setattr(c,'contexts',lambda distance:[dict(name=name,scenario=journey.scenario(distance_m=distance,**changes)) for name,changes in (
            ('normal',{}),('uphill',{'grade_fraction':.04}),('bank-failure',{'failed_banks':[0]}))])
        report=c.run(folder,max_cases=1)
        yield dict(folder=folder,report=report,epoch=epoch,request=request,vehicle=vehicle)


@pytest.fixture
def state(campaign,tmp_path):
    p=tmp_path/'state';shutil.copytree(campaign['folder'],p);return p


def rewrite(state,value):
    latest=c._read(state/'latest.json');row=latest['cases'][0]
    value['evaluation_id']=identity({k:v for k,v in value.items() if k!='evaluation_id'})
    c._write(state/row['path'],value);row['summary']=c.compact(value)
    latest['run_id']=identity({k:v for k,v in latest.items() if k not in ('run_id','new_cases')})
    c._write(state/'latest.json',latest)


def first(state):
    row=c._read(state/'latest.json')['cases'][0];return c._read(state/row['path'])


def test_actual_conditional_run_finishes_nominal_and_retains_adverse_failures(state):
    result=first(state)
    assert result['conditional_numerical_arrivals']==1
    assert result['qualified_numerical_arrivals']==0 and result['admitted_operating_maps']==0
    cases={x['name']:x['result'] for x in result['journeys']}
    assert cases['normal']['execution']=='stopped' and cases['normal']['conditional_numerical_arrival']
    assert cases['uphill']['execution']=='stalled' and cases['bank-failure']['execution']=='stalled'
    assert all(result[k] is False for k in FLAGS) and result['integrated_winner'] is None
    assert c.verify(state,replay=True)['semantic_replay_executed']


def test_same_epoch_run_reuses_exact_case_without_recalculating(state):
    before=c._read(state/'latest.json');result=c.run(state,max_cases=0)
    assert result['new_cases']==0 and result['run_id']==before['run_id']
    assert not result['pending']
    assert c.verify(state,replay=False)['semantic_replay_executed'] is False


def test_case_summary_cannot_forge_more_arrivals(state):
    latest=c._read(state/'latest.json');latest['cases'][0]['summary']['conditional_numerical_arrivals']=100
    latest['run_id']=identity({k:v for k,v in latest.items() if k not in ('run_id','new_cases')})
    c._write(state/'latest.json',latest)
    with pytest.raises(ValueError,match='summary'):c.verify(state,replay=False)


def test_resealed_case_numerical_forgery_is_caught_by_real_semantic_replay(state):
    value=first(state);value['journeys'][0]['result']['final_front_m']=2000.
    value['journeys'][0]['result']['stopping_error_m']=0.;rewrite(state,value)
    with pytest.raises(ValueError):c.verify(state,replay=True)


@pytest.mark.parametrize('flag',['physical_accepted','operating_release','manufacturing_release'])
def test_case_release_cannot_be_hidden_by_compact_reset_or_resealed_outer_ids(state,flag):
    value=first(state);value[flag]=True;rewrite(state,value)
    with pytest.raises(ValueError):c.verify(state,replay=False)
    with pytest.raises(ValueError):c.run(state,max_cases=0)


def test_case_source_epoch_cannot_be_resealed_under_valid_run_source(state):
    value=first(state);value['source_sha256']['engineering/reference_cell/vehicles.py']='f'*64;rewrite(state,value)
    with pytest.raises(ValueError):c.verify(state,replay=False)


def test_request_coverage_and_case_paths_remain_exact(state):
    latest=c._read(state/'latest.json');latest['cases'][0]['path']='cases/../outside.json.gz'
    latest['run_id']=identity({k:v for k,v in latest.items() if k not in ('run_id','new_cases')});c._write(state/'latest.json',latest)
    with pytest.raises(ValueError,match='path'):c.verify(state,replay=False)


def test_unexpected_files_and_root_state_symlink_are_refused(state,tmp_path):
    extra=state/'stray.tmp';extra.write_text('not-issued')
    with pytest.raises(ValueError):c.verify(state,replay=False)
    extra.unlink();linked=tmp_path/'linked-state';linked.symlink_to(state,target_is_directory=True)
    with pytest.raises(ValueError):c.verify(linked,replay=False)


def test_changed_source_epoch_preserves_existing_run_instead_of_rebinding(state,campaign):
    old=dict(campaign['epoch']);campaign['epoch']['changed-source.py']='f'*64
    try:
        with pytest.raises((ValueError,FileNotFoundError)):c.run(state,max_cases=0)
        with pytest.raises(ValueError):c.verify(state,replay=False)
    finally:campaign['epoch'].clear();campaign['epoch'].update(old)


def test_bounded_pending_run_has_no_invented_case_or_arrival(tmp_path,campaign):
    result=c.run(tmp_path/'pending',max_cases=0)
    assert result['cases']==[] and len(result['pending'])==1 and result['new_cases']==0
    verified=c.verify(tmp_path/'pending',replay=True)
    assert verified['cases']==0 and verified['conditional_numerical_arrivals']==0


def test_read_rejects_linked_payloads(tmp_path):
    p=tmp_path/'raw.json';p.write_text('{}');linked=tmp_path/'link.json';linked.symlink_to(p)
    with pytest.raises(ValueError):c._read(linked)


def test_workbench_rejects_resealed_case_release_before_serving_summary(state):
    from engineering.railway_progress import workbench
    value=first(state);value['operating_release']=True;rewrite(state,value)
    with pytest.raises(ValueError):workbench.handler(state)


def test_nested_trajectory_release_cannot_hide_inside_unreleased_outer_case(state):
    value=first(state);j=value['journeys'][0]['result'];j['operating_release']=True
    j['evaluation_id']=identity({k:v for k,v in j.items() if k!='evaluation_id'});rewrite(state,value)
    with pytest.raises(ValueError):c.verify(state,replay=False)


def test_composition_uses_new_launch_identity_and_actual_brake_subcomponent(state):
    value=first(state);b=value['bundle'];a=value['alternative']
    assert b['schema']=='osr-continuing-reference-cell-bundle/1'
    assert b['definition_id']==identity({k:v for k,v in b.items() if k!='definition_id'})
    assert b['candidate_id']==identity(b['architecture_case']['physical_definition'])
    assert b['propulsion_component_id']==a['candidate_id']==b['brake_definition']['propulsion_component_id']
    assert b['candidate_id']==b['brake_definition']['candidate_id']==value['civil']['candidate_id']
    assert b['body_candidate_id']==b['brake_definition']['body_candidate_id']==a['body_candidate_id']
    assert 'motor_definition' not in b and 'wayside_primary_stock' not in b
