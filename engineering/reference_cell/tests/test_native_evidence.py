"""Disposable mocked execution records test publication, not physical evidence.

The coordinator separately publishes/verifies the actual retained native pair.
No field solver is run here and these fake packages cannot pass motor.verify.
"""
from copy import deepcopy
from pathlib import Path
import gzip
import io
import json
import tarfile

import pytest

from engineering.reference_cell import native_evidence as n
from engineering.station_rail.common import encoded,identity,digest


@pytest.fixture
def state(tmp_path,monkeypatch):
    directory=tmp_path/'synthetic-only';directory.mkdir()
    for name,dt,steps,force,current in (('coarse',.002,64,100.,10.),('fine',.001,128,125.,12.)):
        folder=directory/name;folder.mkdir()
        request=dict(bundle_id='a'*64,motor_component_id='b'*64,body_candidate_id='c'*64,
            dt_s=dt,steps=steps,frequency_Hz=50.,maximum_seconds=600.,mesh_m=.08)
        request['request_id']=identity(request)
        trace=[dict(time_s=(i+1)*dt,thrust_N=force,path_currents_A=[current,-current,0.],
            terminal_W=force*20+70,primary_copper_W=50.,secondary_Joule_W=20.,mechanical_W=force*20,
            magnetic_energy_J=0.,external_leakage_energy_J=0.,backward_Euler_dissipation_W=0.,
            external_leakage_BE_dissipation_W=0.,stabilization_work_W=0.,discrete_power_residual_W=0.) for i in range(steps)]
        result=dict(execution='completed',state='completed',trace=trace,actual_mesh=dict(mesh_id='d'*64))
        result['evaluation_id']=identity(result)
        for filename in n.FILES:(folder/filename).write_bytes(b'DISPOSABLE MOCK; NOT EXECUTED PHYSICS\n')
        (folder/'input.json').write_bytes(encoded(dict(request=request)))
        (folder/'result.json').write_bytes(encoded(result))
    calls=[]
    def verified(folder,*,root,require_current_tool):
        calls.append(require_current_tool)
        assert require_current_tool is False
        return dict(verified=True,recorded_tool_identity=dict(python='MOCK',python_sha256='e'*64,
            numpy='MOCK',scipy='MOCK',superlu_sha256='f'*64))
    monkeypatch.setattr(n.motor,'verify',verified)
    monkeypatch.setattr(n.motor,'compare',lambda *a,**kw:(_ for _ in ()).throw(AssertionError('Old current-tool comparison must not be used')))
    return directory,calls


def edit_state(state,kind,key,value):
    path=state[0]/kind/'result.json';data=json.loads(path.read_bytes());data[key]=value
    path.write_bytes(encoded(data))


def reseal(folder,mutation):
    path=folder/n.MANIFEST;value=json.loads(path.read_bytes());mutation(value)
    value['publication_id']=identity({k:v for k,v in value.items() if k!='publication_id'})
    path.write_bytes(encoded(value))


def test_portable_publication_recomputes_weighted_matched_time_statistics(state,tmp_path):
    folder=tmp_path/'publication';manifest=n.publish(state[0],folder);value=manifest['comparison']
    assert state[1] and all(value is False for value in state[1])
    assert value['matched_points']==64 and value['completed_same_horizon']
    assert value['relative_matched_thrust_RMS_change']==pytest.approx(.2)
    assert value['relative_matched_current_RMS_change']==pytest.approx(1/6)
    assert [r['mean_thrust_N'] for r in value['tail_cycle_statistics']]==pytest.approx([100.,125.])
    assert [r['duration_s'] for r in value['tail_cycle_statistics']]==pytest.approx([.04,.04])
    assert [r['mechanical_work_J'] for r in value['tail_cycle_statistics']]==pytest.approx([80.,100.])
    assert all(abs(r['recomputed_discrete_energy_residual_J'])<1e-10 for r in value['full_horizon_statistics'])
    assert value['approved_convergence_limit'] is None and value['numerical_time_convergence']=='unconfirmed'
    assert value['available_operating_map'] is None
    assert value['whole_vehicle_candidate_ids_admitted']==[]
    assert not value['current_tool_identity_asserted'] and not value['numerical_replayed'] and not value['native_reuse_eligible']
    actual=n.verify_publication(folder)
    assert actual['verified'] and not actual['operating_map_admitted']
    assert all(actual[key] is False for key in n.FLAGS)


@pytest.mark.parametrize('field,value',[
    ('relative_matched_thrust_RMS_change',0.),('numerical_time_convergence','passed'),
    ('numerical_replayed',True),('new_vehicle_candidate_inheritance_allowed',True),
    ('whole_vehicle_candidate_ids_admitted',['0'*64])])
def test_resealed_diagnostics_cannot_claim_convergence_or_new_vehicle_inheritance(state,tmp_path,field,value):
    folder=tmp_path/'publication';n.publish(state[0],folder)
    reseal(folder,lambda m:m['comparison'].update({field:value}))
    with pytest.raises(ValueError,match='semantic'):n.verify_publication(folder)


def test_physical_qualification_and_source_identity_cannot_be_relabelled(state,tmp_path):
    folder=tmp_path/'publication';n.publish(state[0],folder)
    original=(folder/n.MANIFEST).read_bytes()
    reseal(folder,lambda m:m.update(physical_qualification=True))
    with pytest.raises(ValueError):n.verify_publication(folder)
    (folder/n.MANIFEST).write_bytes(original)
    reseal(folder,lambda m:m['source_sha256'].update({n.PRODUCER:'0'*64}))
    with pytest.raises(ValueError):n.verify_publication(folder)


def test_incomplete_execution_does_not_get_full_horizon_or_cycle_integrals(state):
    edit_state(state,'fine','execution','interrupted')
    value=n.assess(state[0])
    assert not value['completed_same_horizon']
    assert value['full_horizon_statistics'] is None and value['tail_cycle_statistics'] is None
    assert value['matched_points']==0


@pytest.mark.parametrize('key,value', [('mesh_m',.04),('bundle_id','0'*64),('steps',127)])
def test_mixed_candidate_mesh_or_horizon_requests_are_rejected(state,key,value):
    path=state[0]/'fine'/'input.json';value0=json.loads(path.read_bytes());value0['request'][key]=value
    path.write_bytes(encoded(value0))
    with pytest.raises(ValueError):n.assess(state[0])


def test_actual_mesh_mismatch_is_rejected_even_with_completed_traces(state):
    edit_state(state,'fine','actual_mesh',dict(mesh_id='0'*64))
    with pytest.raises(ValueError,match='mesh'):n.assess(state[0])


@pytest.mark.parametrize('mode',['traversal','symlink','duplicate'])
def test_native_archive_rejects_unsafe_member_forms_before_extraction(state,tmp_path,mode):
    folder=tmp_path/'publication';n.publish(state[0],folder);path=folder/n.ARCHIVE
    stream=io.BytesIO()
    with tarfile.open(path,'r:gz') as old,tarfile.open(fileobj=stream,mode='w') as new:
        for index,item in enumerate(old.getmembers()):
            raw=old.extractfile(item).read();copy=deepcopy(item)
            if index==0 and mode=='traversal':copy.name='../escape.json'
            if index==0 and mode=='symlink':copy.type=tarfile.SYMTYPE;copy.linkname='/tmp/unowned';copy.size=0
            new.addfile(copy,io.BytesIO(raw) if copy.isfile() else None)
            if index==0 and mode=='duplicate':new.addfile(item,io.BytesIO(raw))
    path.write_bytes(gzip.compress(stream.getvalue(),mtime=0))
    reseal(folder,lambda m:m.update(archive_sha256=digest(path)))
    with pytest.raises(ValueError):n.verify_publication(folder)


def test_expansion_budget_is_checked_before_tar_parsing(state,tmp_path,monkeypatch):
    folder=tmp_path/'publication';n.publish(state[0],folder);path=folder/n.ARCHIVE
    path.write_bytes(gzip.compress(b'0'*20000,mtime=0))
    reseal(folder,lambda m:m.update(archive_sha256=digest(path)))
    monkeypatch.setattr(n,'MAX_BYTES',16000)
    with pytest.raises(ValueError,match='Expanded'):n.verify_publication(folder)


def test_unknown_or_linked_native_files_cannot_enter_publication(state,tmp_path):
    extra=state[0]/'coarse'/'extra';extra.write_text('not a declared artifact')
    with pytest.raises(ValueError):n.publish(state[0],tmp_path/'publication')
    extra.unlink();path=state[0]/'coarse'/'stdout.log';path.unlink();path.symlink_to(state[0]/'fine'/'stdout.log')
    with pytest.raises(ValueError):n.publish(state[0],tmp_path/'publication')


def test_discrete_integral_residual_is_independently_recomputed(state):
    path=state[0]/'fine'/'result.json';value=json.loads(path.read_bytes());value['trace'][30]['terminal_W']+=1000.
    path.write_bytes(encoded(value))
    with pytest.raises(ValueError,match='energy arithmetic'):n.assess(state[0])


def test_source_directory_and_published_package_are_not_overwritten(state,tmp_path):
    before={p.relative_to(state[0]).as_posix():digest(p) for p in state[0].rglob('*') if p.is_file()}
    folder=tmp_path/'publication';n.publish(state[0],folder)
    assert before=={p.relative_to(state[0]).as_posix():digest(p) for p in state[0].rglob('*') if p.is_file()}
    with pytest.raises(ValueError,match='immutable'):n.publish(state[0],folder)
