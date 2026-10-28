"""One actual scoped source-cell replay and hostile cached/publication metadata."""
from copy import deepcopy
from pathlib import Path
import shutil
import pytest
from engineering.sourced_case import coordinator as c,operating,identity,digest,ROOT,FLAGS
from engineering.sourced_case.tests.test_operating import prepared


@pytest.fixture(scope='module')
def campaign(tmp_path_factory):
    from engineering.sourced_case import power_revision
    e=power_revision.revise(prepared(),parallel_strings=8);folder=tmp_path_factory.mktemp('source-cell')/'state'
    request=dict(vehicle_id='V1',distance_m=2000.,variant='parker400-dpw-h300',distributed=False,ambient_C=55.)
    epoch={'engineering/reference_cell/vehicles.py':digest(ROOT/'engineering/reference_cell/vehicles.py')}
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(c,'sources',lambda root=ROOT:dict(epoch));mp.setattr(c,'plan',lambda:[deepcopy(request)])
        mp.setattr(c,'revised',lambda vehicle_id='V1',root=ROOT:deepcopy(e))
        mp.setattr(c,'contexts',lambda distance,ambient,aux:[dict(name='normal',scenario=operating.scenario(distance_m=distance,ambient_C=ambient,auxiliary_W_per_car=aux))])
        value=c.run(folder,max_cases=1);yield dict(folder=folder,epoch=epoch,run=value)


@pytest.fixture
def state(campaign,tmp_path):
    folder=tmp_path/'state';shutil.copytree(campaign['folder'],folder);return folder


def case(state):
    latest=c.read(state/'latest.json');row=latest['cases'][0];return latest,row,c.read(state/row['path'])


def reseal(state,latest):
    latest['run_id']=identity({k:v for k,v in latest.items() if k!='run_id'});c.write(state/'latest.json',latest)


def replace(state,latest,row,value):
    value['evaluation_id']=identity({k:v for k,v in value.items() if k!='evaluation_id'})
    c.write(state/row['path'],value);row['evaluation_id']=value['evaluation_id'];reseal(state,latest)


def test_actual_one_case_pipeline_binds_vehicle_drive_brake_civil_manufacture_and_charge(state):
    latest,row,v=case(state);b=v['bundle'];cid=v['candidate_id']
    assert cid==b['candidate_id']==v['civil']['candidate_id']==v['manufacturing']['candidate_id']
    assert b['propulsion_component_id']==v['drive']['candidate_id']==b['brake_definition']['propulsion_component_id']
    assert b['sourced_brake']['equipment_evaluation_id']
    assert v['conditional_arrivals']==1 and v['qualified_journeys']==0
    assert v['charging']['protected_headway_qualified'] is False
    assert v['whole_life_cost'] is None and v['integrated_winner'] is None
    assert c.verify(state,replay=True)['semantic_replay_executed']


@pytest.mark.parametrize('field,value',[('arrivals',1000),('motion_screens',1000),('candidate_id','f'*64)])
def test_resealed_dashboard_summary_cannot_misrepresent_actual_case(state,field,value):
    latest,row,v=case(state);row[field]=value;reseal(state,latest)
    with pytest.raises(ValueError):c.verify(state,replay=False)


def test_top_level_research_release_cannot_be_self_signed(state):
    latest,_,_=case(state);latest['operating_release']=True;reseal(state,latest)
    with pytest.raises(ValueError):c.verify(state,replay=False)


def test_nested_case_release_rejected_in_verifier_and_cached_run(state):
    latest,row,v=case(state);v['journeys'][0]['result']['operating_release']=True;replace(state,latest,row,v)
    with pytest.raises(ValueError):c.verify(state,replay=False)
    with pytest.raises(ValueError):c.run(state,max_cases=0)


def test_resealed_case_source_epoch_mismatch_cannot_hide_under_valid_run_epoch(state):
    latest,row,v=case(state);v['source_sha256']['engineering/reference_cell/vehicles.py']='f'*64;replace(state,latest,row,v)
    with pytest.raises(ValueError):c.verify(state,replay=False)


def test_paths_links_and_extra_files_are_not_owned_case_inputs(state,tmp_path):
    latest,row,v=case(state);row['path']='cases/../outside.json.gz';reseal(state,latest)
    with pytest.raises(ValueError):c.verify(state,replay=False)
    original=tmp_path/'empty';original.mkdir();link=tmp_path/'state-link';link.symlink_to(original,target_is_directory=True)
    with pytest.raises(ValueError):c.run(link,max_cases=0)


def test_resealed_numerical_result_is_caught_by_actual_semantic_reconstruction(state):
    latest,row,v=case(state);v['journeys'][0]['result']['stopping_error_m']=0.;replace(state,latest,row,v)
    with pytest.raises(ValueError):c.verify(state,replay=True)


def test_source_epoch_change_cannot_overwrite_existing_run_inputs(state,campaign):
    old=dict(campaign['epoch']);campaign['epoch']['nonexistent.py']='f'*64
    try:
        with pytest.raises((ValueError,FileNotFoundError)):c.run(state,max_cases=0)
    finally:campaign['epoch'].clear();campaign['epoch'].update(old)
