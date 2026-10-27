"""Actual archived component packages cannot acquire rehashed extra claims."""
from pathlib import Path
import gzip,io,json,shutil,tarfile
import pytest
from engineering.design_search import moving_lim_publication as p

ROOT=Path(__file__).resolve().parents[3]
PACKET=ROOT/p.OUTPUT


def _reseal(folder,mutate):
    report=p._read(folder/'assessment.json');mutate(report)
    report.pop('publication_id');report['publication_id']=p.identity(report)
    (folder/'assessment.json').write_bytes(p.encoded(report));(folder/'README.md').write_text(p._readme(report))
    manifest=p._read(folder/'manifest.json');manifest['publication_id']=report['publication_id']
    manifest['files_sha256']={f.name:p.digest(f) for f in folder.iterdir() if f.name!='manifest.json'}
    manifest.pop('manifest_id');manifest['manifest_id']=p.identity(manifest)
    (folder/'manifest.json').write_bytes(p.encoded(manifest))


def test_actual_archive_replays_independent_accounting_and_remains_small():
    result=p.verify(PACKET)
    assert result['sealed_packages']==22 and not result['operating_map_admitted']
    assert (PACKET/'native-runs.tar.gz').stat().st_size<5*1024*1024
    assessment=p._read(PACKET/'assessment.json')
    assert assessment['attempted_cases']==23
    assert assessment['comparisons']['spatial_time_convergence_established'] is False
    partial=next(r for r in assessment['rows'] if r['name']=='low-mesh-25mm')
    assert partial['execution']=='interrupted' and partial['trace_scope']=='interrupted partial log only'
    assert partial['last']['time_s']<partial['dt_s']*partial['steps']
    assert assessment['comparisons']['continuation']['mesh_30_to_25mm_relative_change'] is None
    assert any(r['stabilization_work_J']<0 for r in assessment['rows'])
    critical=assessment['comparisons']['critical_mesh']
    assert critical['zero_excitation_control_passed']
    assert critical['powered_startup_thrust_all_negative'] and not critical['positive_nominal_slip_proves_propulsion']
    time=assessment['comparisons']['fine_timestep']
    assert time['same_actual_mesh_verified'] and time['recorded_tool_identities_equal']
    assert not time['spatial_time_convergence_established'] and time['powered_startup_thrust_all_negative']
    assert time['half_to_quarter_ms']['final_force_relative_change']>.1
    assert time['signed_SUPG_work_J'][-1]<0 and time['backward_Euler_work_J'][-1]>time['physical_secondary_Joule_J'][-1]
    blocked=assessment['comparisons']['blocked_probe']
    assert blocked['execution']=='interrupted' and (blocked['recorded_steps'],blocked['requested_steps'])==(35,128)
    assert blocked['first_cycle_mean_thrust_N']==pytest.approx(.22613764641671233)
    assert blocked['late_cycle_80_to_100ms_mean_thrust_N'] is None and blocked['late_cycle_100_to_120ms_mean_thrust_N'] is None
    assert blocked['available_operating_force_N'] is None and not blocked['controlled_single_variable_comparison']


def test_resealed_small_timestep_error_claim_is_rejected(tmp_path):
    packet=tmp_path/'packet';shutil.copytree(PACKET,packet)
    _reseal(packet,lambda report:report['comparisons']['fine_timestep']['half_to_quarter_ms'].update(final_force_relative_change=0.))
    with pytest.raises(ValueError,match='assessment differs from immutable runs'):p.verify(packet)


def test_interrupted_blocked_cycle_cannot_fill_unavailable_late_window(tmp_path):
    packet=tmp_path/'packet';shutil.copytree(PACKET,packet)
    _reseal(packet,lambda report:report['comparisons']['blocked_probe'].update(late_cycle_80_to_100ms_mean_thrust_N=0.))
    with pytest.raises(ValueError,match='assessment differs from immutable runs'):p.verify(packet)


def test_resealed_timestep_budget_change_is_rejected(tmp_path):
    runs=tmp_path/'runs';runs.mkdir()
    with tarfile.open(PACKET/'native-runs.tar.gz') as tar:
        for member in tar:
            target=runs/member.name;target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(tar.extractfile(member).read())
    path=runs/'time-context'/'plan.json';plan=p._read(path)
    plan['maximum_component_jobs']=3;plan.pop('plan_id');plan['plan_id']=p.identity(plan)
    path.write_bytes(p.encoded(plan))
    with pytest.raises(ValueError,match='Fine timestep resource'):p.collect(runs)


def _time_runs(tmp_path,mutate,case_name='motoring-fine-dt-quarter'):
    runs=tmp_path/'runs';runs.mkdir()
    with tarfile.open(PACKET/'native-runs.tar.gz') as tar:
        for member in tar:
            target=runs/member.name;target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(tar.extractfile(member).read())
    case=runs/case_name;value=p._read(case/'result.json');mutate(value)
    value.pop('evaluation_id');value['evaluation_id']=p.identity(value);(case/'result.json').write_bytes(p.encoded(value))
    manifest=p._read(case/'manifest.json');manifest['evaluation_id']=value['evaluation_id']
    manifest['files_sha256']['result.json']=p.digest(case/'result.json')
    manifest.pop('manifest_id');manifest['manifest_id']=p.identity(manifest)
    (case/'manifest.json').write_bytes(p.encoded(manifest));return runs


def test_resealed_executed_tool_mismatch_cannot_inherit_planning_tool_identity(tmp_path):
    runs=_time_runs(tmp_path,lambda result:result['tool'].update(python_sha256='0'*64))
    with pytest.raises(ValueError,match='Executed timestep tool identities'):p.collect(runs)


def test_resealed_blocked_tool_cannot_inherit_frozen_planning_tool(tmp_path):
    runs=_time_runs(tmp_path,lambda result:result['tool'].update(python_sha256='0'*64),p.BLOCKED_CASE)
    with pytest.raises(ValueError,match='Blocked probe executed tool'):p.collect(runs)


def test_blocked_worker_cannot_drop_recorded_executable_identity(tmp_path):
    runs=_time_runs(tmp_path,lambda result:result['tool'].pop('python_sha256'),p.BLOCKED_CASE)
    with pytest.raises(ValueError,match='Blocked probe executed tool'):p.collect(runs)


def test_resealed_blocked_campaign_must_bind_actual_interrupted_execution(tmp_path):
    runs=_time_runs(tmp_path,lambda result:None,p.BLOCKED_CASE)
    path=runs/'blocked-context'/'campaign.json';value=p._read(path);value['evaluation_id']='0'*64
    value.pop('campaign_id');value['campaign_id']=p.identity(value);path.write_bytes(p.encoded(value))
    with pytest.raises(ValueError,match='Blocked probe campaign/execution binding'):p.collect(runs)


def test_interrupted_timestep_keeps_unavailable_complete_work_unknown(tmp_path):
    def interrupted(result):
        result['execution']='interrupted';result['state']='interrupted';result.pop('trace');result.pop('actual_mesh')
    runs=_time_runs(tmp_path,interrupted)
    rows,zero,comparisons=p.collect(runs);time=comparisons['fine_timestep']
    assert time['half_to_quarter_ms']['final_force_relative_change'] is None
    assert time['backward_Euler_work_J']==[None]*3 and time['signed_SUPG_work_J']==[None]*3
    assert time['physical_secondary_Joule_J']==[None]*3 and time['powered_startup_thrust_all_negative'] is None


def test_rehashed_force_claim_is_rejected_against_actual_archived_trace(tmp_path):
    packet=tmp_path/'packet';shutil.copytree(PACKET,packet)
    def change(report):report['rows'][1]['last']['thrust_N']+=1.
    _reseal(packet,change)
    with pytest.raises(ValueError,match='assessment differs from immutable runs'):p.verify(packet)


def test_duplicate_archive_member_is_rejected_even_with_rehashed_receipts(tmp_path):
    packet=tmp_path/'packet';shutil.copytree(PACKET,packet);stream=io.BytesIO()
    with tarfile.open(fileobj=io.BytesIO((packet/'native-runs.tar.gz').read_bytes()),mode='r:gz') as old,tarfile.open(fileobj=stream,mode='w') as new:
        members=old.getmembers()
        for item in members:new.addfile(item,io.BytesIO(old.extractfile(item).read()))
        item=members[0];new.addfile(item,io.BytesIO(old.extractfile(item).read()))
    archive=gzip.compress(stream.getvalue(),mtime=0);(packet/'native-runs.tar.gz').write_bytes(archive)
    _reseal(packet,lambda report:report.update(archive_sha256=p.sha256(archive).hexdigest()))
    with pytest.raises(ValueError,match='unique bounded'):p.verify(packet)


def test_regenerating_current_packet_preserves_exact_old_native_bytes(tmp_path):
    runs=tmp_path/'runs';runs.mkdir()
    with tarfile.open(PACKET/'native-runs.tar.gz') as tar:
        for member in tar:
            target=runs/member.name;target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(tar.extractfile(member).read())
    output=tmp_path/'published';first=p.publish(runs,output)
    archive=(output/'native-runs.tar.gz').read_bytes()
    second=p.publish(runs,output,replace=True)
    assert second['publication_id']==first['publication_id']
    assert (output/'native-runs.tar.gz').read_bytes()==archive
