"""Adversarial units, occurrence identity, reference mapping and receipt checks."""
from copy import deepcopy
import json
from unittest.mock import patch
import pytest
from engineering.design_search.craft_backends import pilot, cases, native
from engineering.design_search.craft_backends.__main__ import main


@pytest.fixture
def control():return cases.cases()[-1]


def measured(case):
    return deepcopy(dict(bodies=[dict(id=name,volume_m3=p['volume_m3'],center_of_mass_m=p['centroid_m'],
        bbox_m=dict(zip(('min','max'),p['bounds_m'])),closed=True,valid=True)
        for name,p in case['expected']['part_measures'].items()]))


def test_wrong_mm_and_m_is_detected_even_with_correct_total_and_ids(control):
    value=measured(control);assert pilot.compare_geometry(control,value,exact=True)['comparison_passed']
    value['bodies'][0]['center_of_mass_m']=[x*1000 for x in value['bodies'][0]['center_of_mass_m']]
    assert not pilot.compare_geometry(control,value,exact=True)['comparison_passed']


def test_field_geometry_readback_does_not_invent_closure(control):
    value=measured(control);value['bodies'][0].pop('closed')
    with pytest.raises(ValueError):pilot.compare_geometry(control,value)
    check=pilot.compare_geometry(control,value,require_closed=False)
    assert check['comparison_passed'] and not check['closure_checked']


def test_generic_step_label_maps_only_by_unique_exact_geometry_and_reports_loss(control):
    value=measured(control);value['bodies'][0]['id']='assembly'
    value['native']=dict(bodies=value['bodies'])
    associated=pilot.associate_exact(control,value,{'exact_volume_relative':1e-7,'exact_position_m':1e-7})
    assert associated['native_names_preserved'] is False
    assert associated['bodies'][0]['id']==control['entities'][0]['id']
    assert value['bodies'][0]['id']=='assembly'
    assert associated['native']['bodies'][0]['id']=='assembly'
    reloaded=json.loads(json.dumps(value))
    assert pilot.associate_exact(control,reloaded,{'exact_volume_relative':1e-7,'exact_position_m':1e-7})==associated
    value['bodies'][0]['bbox_m']['min'][0]+=.1
    with pytest.raises(ValueError):pilot.associate_exact(control,value,{'exact_volume_relative':1e-7,'exact_position_m':1e-7})


def test_compensating_volume_errors_and_duplicate_names_are_refused():
    case=cases.cases()[0];value=measured(case)
    value['bodies'][0]['volume_m3']+=.01;value['bodies'][1]['volume_m3']-=.01
    assert not pilot.compare_geometry(case,value,exact=True)['comparison_passed']
    value=measured(case);value['bodies'][1]['id']=value['bodies'][0]['id']
    with pytest.raises(ValueError):pilot.compare_geometry(case,value)


def test_success_requires_persistent_face_set_and_all_native_screens():
    request=dict(cases=[dict(case_id='asymmetric-si-control')])
    stage=dict(status='completed',result=dict(geometry_comparison_passed=True,
        fieldcraft_interchange=dict(geometry_names_and_units_verified=True,named_face_set_reopen_verified=False)))
    stages={'asymmetric-si-control':stage,'linear-controls':dict(status='completed',result=dict(numerical_controls_passed=True))}
    assert not pilot.software_screen(stages,request)
    stage['result']['fieldcraft_interchange']['named_face_set_reopen_verified']=True
    assert pilot.software_screen(stages,request)
    stages['linear-controls']['result']['numerical_controls_passed']=False
    assert not pilot.software_screen(stages,request)


def held_package(tmp_path):
    request=dict(evaluation_id='a'*64,cases=[],execution_options=dict(include_rc=False))
    stage=dict(status='held',reason='independent evidence unavailable',**pilot.FLAGS)
    native.write(tmp_path/'request.json',request);native.write(tmp_path/'linear-controls/stage.json',stage)
    native.write(tmp_path/'delivery-handoffs.json',[])
    value=dict(evaluation_id=request['evaluation_id'],stages={'linear-controls':stage},software_pilot_passed=False,
        artifact_sha256={str(p.relative_to(tmp_path)):native.digest(p) for p in tmp_path.rglob('*') if p.is_file()},**pilot.FLAGS)
    value['result_id']=pilot.identity(value);native.write(tmp_path/'manifest.json',value)
    return request,value


@pytest.mark.parametrize('attack',['stage','aggregate','acceptance','artifact'])
def test_resealed_manifest_cannot_contradict_its_immutable_receipts(tmp_path,attack):
    request,value=held_package(tmp_path)
    if attack=='stage':value['stages']['linear-controls']['status']='completed'
    if attack=='aggregate':value['software_pilot_passed']=True
    if attack=='acceptance':value['physical_accepted']=True
    if attack=='artifact':(tmp_path/'request.json').write_text('{}')
    value['result_id']=pilot.identity({k:v for k,v in value.items() if k!='result_id'})
    (tmp_path/'manifest.json').write_text(json.dumps(value))
    with patch.object(pilot,'plan',return_value=request),pytest.raises((ValueError,KeyError)):
        pilot.verify(tmp_path)


def test_install_cli_handles_list_result_without_attribute_error(capsys):
    with patch.object(native,'install',return_value=dict(installed=True)) as install:
        assert main(['install','solidcraft'])==0
        install.assert_called_once()
    assert 'installed' in capsys.readouterr().out


def test_cross_candidate_stage_refused_even_with_resealed_stage_and_manifest(tmp_path,control):
    request=dict(evaluation_id='a'*64,cases=[control],execution_options=dict(include_rc=False))
    stage=dict(status='completed',result=dict(case_id=control['case_id'],candidate_id='b'*64,
        component_geometry_id=control['component_geometry_id']),**pilot.FLAGS)
    held=dict(status='held',reason='pending',**pilot.FLAGS)
    native.write(tmp_path/'request.json',request)
    native.write(tmp_path/control['case_id']/'stage.json',stage)
    native.write(tmp_path/'linear-controls/stage.json',held)
    value=dict(evaluation_id=request['evaluation_id'],stages={control['case_id']:stage,'linear-controls':held},
        software_pilot_passed=False,artifact_sha256={str(p.relative_to(tmp_path)):native.digest(p) for p in tmp_path.rglob('*') if p.is_file()},**pilot.FLAGS)
    value['result_id']=pilot.identity(value);native.write(tmp_path/'manifest.json',value)
    with patch.object(pilot,'plan',return_value=request),pytest.raises(ValueError,match='Mixed pilot candidate'):
        pilot.verify(tmp_path)


def test_native_failure_preserves_stage_receipt(tmp_path):
    def fail():raise ValueError('expected unsupported native format')
    stage=pilot._capture(tmp_path/'failed',fail)
    assert stage['status']=='held' and stage['physical_accepted'] is False
    assert json.loads((tmp_path/'failed/stage.json').read_text())==stage


def test_interchange_requires_raw_si_measures_and_successful_face_reopen(control):
    e=next(iter(control['expected']['part_measures'].values()))
    opened=dict(errors=[],renamed=[],mismatched=[],stale=dict(sets=[]))
    inspected=dict(model=dict(display_units='m-kg-s-N-Pa',own_units=True,definitions=dict(sets=1)),
        bodies=[dict(name=control['entities'][0]['id'],volume=e['volume_m3'],centroid=e['centroid_m'],bbox=e['bounds_m'])])
    values=[{},None,{},opened,inspected,{},opened,inspected]
    replies=[]
    for i,value in enumerate(values,1):
        result=dict(isError=True,content=[dict(type='text',text='unsupported .sc extension')]) if value is None else dict(content=[dict(type='text',text=json.dumps(value))])
        replies.append(dict(id=i,result=result))
    decoded=pilot.decode_interchange(replies,control)
    assert decoded['geometry_names_and_units_verified'] and decoded['named_face_set_reopen_verified']
    bad=deepcopy(replies);bad[5]['result']=dict(isError=True,content=[dict(type='text',text='face not found')])
    assert not pilot.decode_interchange(bad,control)['named_face_set_reopen_verified']
    bad=deepcopy(replies);wrong=deepcopy(inspected);wrong['model']['display_units']='mm-t-s-N-MPa'
    bad[4]['result']['content'][0]['text']=json.dumps(wrong)
    with pytest.raises(ValueError,match='explicit SI'):pilot.decode_interchange(bad,control)
    with pytest.raises(ValueError,match='coverage'):pilot.decode_interchange(replies[:-1],control)
