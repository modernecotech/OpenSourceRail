"""Exact native interference, host exclusion and nonadmission after zero overlap."""
from copy import deepcopy
from pathlib import Path
import shutil
import subprocess
import pytest
from osr_mech.family_definition import family_definition
from engineering.twin_workflow import core
from engineering.design_consistency import contracts
from engineering.continuous_design import study_confirmation
from engineering.assembly_design import installed_geometry as geometry, installed_equipment


def candidate(kind,positive=False):
    materials={'steel':{'density_kg_m3':7850.}}
    def box(identity,centre):
        return contracts.part(identity,'steel',dict(role=identity,primitives=[contracts.box(identity,.05,.05,.05,centre)]),materials)
    if kind=='cassette':
        parts=[box('owned',[0,0,0]),box('excluded-host',[0,.23,0])]
    elif positive:
        parts=[box('body',installed_equipment.layout()['cassette_local_positions_m'][0])]
    else:
        point=installed_equipment.layout()['cassette_local_positions_m'][0]
        parts=[contracts.member('body',.5,.5,.5,.02,'steel',materials,centre=point)]
    contract=dict(schema='osr-engineering-representations/1',name='TEST-ONLY-'+kind,revision='TEST-1',parts=parts,materials=materials,
        assembly_joints=[],construction_stages=[],mandatory_evidence=[],physical_validation=False,production_released=False)
    return dict(kind='TEST-ONLY-'+kind,revision=core.digest(contract),contract=contract,
        metadata={'cassette_installed_part_ids':['owned']} if kind=='cassette' else {},**core.FLAGS)


def equipment(cassette):
    layout=installed_equipment.layout();family=family_definition('metro-6car');instances=[];allocations=[]
    for car in family['cars']:
        for i,point in enumerate(layout['cassette_local_positions_m'],1):
            row=dict(id=car['id']+'/service-cassette-'+str(i).zfill(2),body_id=car['id'],
                candidate_revision=cassette['revision'],translation_m=[point[0]+car['centre_x_m'],point[1],point[2]],
                rotation=[[1.,0.,0.],[0.,1.,0.],[0.,0.,1.]])
            allocations.append(row);instances.append(dict(**row,local_position_m=point))
    result=dict(schema='TEST-ONLY',architecture=layout['architecture'],layout_sha256=core.sha(installed_equipment.DATA),
        candidate_revision=cassette['revision'],car_count=family['car_count'],counts=installed_equipment.counts(),
        represented_part_ids=['owned'],instances=instances,allocations=allocations,**core.FLAGS)
    result['revision']=core.digest(result);return result


def fake_native(candidate,folder):
    folder.mkdir();cad=folder/'candidate.FCStd';cad.write_bytes(b'TEST FAKE CAD; no native success claimed')
    core.write(folder/'native-cad.json',dict(input_sha256=core.digest(candidate['contract']),files_sha256={cad.name:core.sha(cad)},
        physical_ids_preserved=True,native_reopened=True,step_volume_reconciled=True))
    return cad


@pytest.fixture
def inputs(tmp_path):
    body,cassette=candidate('body'),candidate('cassette')
    return body,fake_native(body,tmp_path/'body'),cassette,fake_native(cassette,tmp_path/'cassette'),equipment(cassette)


def reseal(e):
    e['revision']=core.digest({k:v for k,v in e.items() if k!='revision'})


def test_receipt_bytes_and_exact_contract_are_checked_before_native_execution(inputs,tmp_path):
    body,bc,cassette,cc,e=inputs
    data=geometry._input(*inputs)
    assert len(data['placements'])==8 and all(len(p['instance_ids'])==6 for p in data['placements'])
    assert data['cassette_installed_part_ids']==['owned'] and data['excluded_cassette_part_ids']==['excluded-host']
    assert data['placements'][0]['local_position_m'][2]==2.3
    assert not data['frame_alignment_verified']
    bc.write_bytes(b'mutated CAD')
    with pytest.raises(ValueError,match='proof'):geometry.build(*inputs,tmp_path/'study')
    assert not (tmp_path/'study').exists()


@pytest.mark.parametrize('change',[
    lambda e:e['instances'][0]['local_position_m'].__setitem__(2,9.),
    lambda e:e['instances'][0]['translation_m'].__setitem__(2,9.),
    lambda e:e['instances'][0].update(id='other-instance'),
    lambda e:e['allocations'].pop(),
    lambda e:e.update(layout_sha256='0'*64),
    lambda e:e.update(represented_part_ids=['excluded-host']),
])
def test_resealed_placements_cannot_override_controlled_source_layout(inputs,change):
    body,bc,cassette,cc,e=deepcopy(inputs)
    # Equipment fixture copies the source JSON lists; deep copy here is necessary
    # to keep its own shared instance/allocation lists intact across mutations.
    change(e);reseal(e)
    with pytest.raises(ValueError):geometry._input(body,bc,cassette,cc,e)


def test_tool_unavailability_produces_hold_never_admission(inputs,tmp_path,monkeypatch):
    monkeypatch.setattr(geometry.shutil,'which',lambda _:None)
    def missing(*args,**kwargs):raise FileNotFoundError('TEST missing native tool')
    monkeypatch.setattr(geometry.subprocess,'run',missing)
    report=geometry.build(*inputs,tmp_path/'study')
    assert report['geometry_state']=='hold' and report['interference_volume_m3'] is None
    assert report['execution_error'] and not report['admitted_for_system_simulation']
    assert geometry.verify(*inputs,tmp_path/'study')
    changed=deepcopy(report);changed['admitted_for_system_simulation']=True
    changed['revision']=core.digest({k:v for k,v in changed.items() if k!='revision'})
    core.write(tmp_path/'study/result.json',changed)
    with pytest.raises(ValueError,match='result differs'):geometry.verify(*inputs,tmp_path/'study')


@pytest.fixture(scope='module')
def native_inputs(tmp_path_factory):
    if not shutil.which('FreeCADCmd') and not shutil.which('freecadcmd'):
        if not shutil.which('flatpak') or subprocess.run(['flatpak','info','org.freecad.FreeCAD'],capture_output=True).returncode:
            pytest.skip('native FreeCAD unavailable')
    root=tmp_path_factory.mktemp('native-installed-fixtures');models=[]
    for name,c in [('cassette',candidate('cassette')),('empty-opening',candidate('body')),('obstruction',candidate('body',True))]:
        source=root/(name+'.json');core.write(source,c['contract'])
        proof,state,error=study_confirmation.native(source,root/name)
        assert state=='passed',error
        models.append((c,root/name/'candidate.FCStd'))
    return models


def test_native_hollow_opening_has_overlapping_bounds_but_no_solid_interference(native_inputs,tmp_path):
    (cassette,cc),(body,bc),_=native_inputs;e=equipment(cassette)
    report=geometry.build(body,bc,cassette,cc,e,tmp_path/'study')
    assert report['geometry_state']=='passed',report
    assert report['native_boolean_tests']>0 # Bound overlap alone was not a failure.
    assert report['interference_volume_m3']==0 and report['interferences']==[]
    assert report['state']=='hold' and not report['admitted_for_system_simulation']
    assert report['train_instance_count']==48 and report['excluded_part_ids']==['excluded-host']
    assert report['holds'] and geometry.verify(body,bc,cassette,cc,e,tmp_path/'study')


def test_native_obstruction_reports_exact_part_and_all_six_instance_ids(native_inputs,tmp_path):
    (cassette,cc),_,(body,bc)=native_inputs;e=equipment(cassette)
    report=geometry.build(body,bc,cassette,cc,e,tmp_path/'study')
    assert report['geometry_state']=='failed' and report['state']=='failed'
    assert report['interference_volume_m3']==pytest.approx(.05**3*6)
    hit=report['interferences'][0]
    assert hit['carbody_part_id']=='body'
    assert len(hit['instance_ids'])==6 and hit['instance_ids'][0]=='car-1/service-cassette-01'
    assert hit['part_pairs'][0]['cassette_part_id']=='owned'
    assert hit['part_pairs'][0]['intersection_volume_m3']==pytest.approx(.05**3)
    assert not report['admitted_for_system_simulation']
    assert geometry.verify(body,bc,cassette,cc,e,tmp_path/'study')
    # Resealing the result cannot promote the retained native rejection.
    report['geometry_state']='passed';report['state']='hold'
    report['revision']=core.digest({k:v for k,v in report.items() if k!='revision'})
    core.write(tmp_path/'study/result.json',report)
    with pytest.raises(ValueError,match='result differs'):geometry.verify(body,bc,cassette,cc,e,tmp_path/'study')


def test_held_study_can_be_verified_after_portable_relocation(inputs,tmp_path,monkeypatch):
    def missing(*args,**kwargs):raise FileNotFoundError('TEST unavailable tool')
    monkeypatch.setattr(geometry.subprocess,'run',missing)
    body,bc,cassette,cc,e=inputs
    geometry.build(*inputs,tmp_path/'study')
    relocated=tmp_path/'relocated';relocated.mkdir()
    for name,path in [('body',bc.parent),('cassette',cc.parent),('study',tmp_path/'study')]:
        shutil.copytree(path,relocated/name)
    assert geometry.verify(body,relocated/'body/candidate.FCStd',cassette,relocated/'cassette/candidate.FCStd',e,relocated/'study')
    assert str(tmp_path).encode() not in (relocated/'study/input.json').read_bytes()


def test_resealed_native_report_cannot_promote_unknown_part_or_known_failure(inputs):
    data=geometry._input(*inputs)
    rows=[dict(**p,intersection_volume_m3=0.,interferences=[]) for p in data['placements']]
    hit=dict(carbody_part_id='body',intersection_volume_m3=.01,
        part_pairs=[dict(carbody_part_id='body',cassette_part_id='excluded-host',intersection_volume_m3=.01)])
    rows[0].update(intersection_volume_m3=.01,interferences=[hit])
    raw=dict(geometry_state='failed',source_models_unchanged=True,native_boolean_tests=2,placements=rows,
        interferences=[dict(placement_id=rows[0]['id'],instance_ids=rows[0]['instance_ids'],**hit)],interference_volume_m3=.06)
    with pytest.raises(ValueError,match='unknown installed-part'):geometry._validate_raw(data,raw)
    hit['part_pairs'][0]['cassette_part_id']='owned'
    raw['interferences']=[dict(placement_id=rows[0]['id'],instance_ids=rows[0]['instance_ids'],**hit)]
    geometry._validate_raw(data,raw)
    raw['geometry_state']='passed'
    with pytest.raises(ValueError,match='promoted'):geometry._validate_raw(data,raw)
