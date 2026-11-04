"""Bounded cross-section child and solver-free integrity replay controls."""
from copy import deepcopy
import json
from pathlib import Path
import resource
import subprocess

import pytest

from engineering.design_search import section_torsion as core, section_torsion_job as job
from engineering.station_rail.common import digest, encoded, identity


SECTION = dict(width_m=.08, height_m=.16, wall_m=.006)


def seal(value, key):
    value[key] = identity({k:v for k,v in value.items() if k != key})
    return value


def reseal_manifest(folder):
    manifest = json.loads((folder/"manifest.json").read_bytes())
    manifest["files"] = job._inventory(folder)
    result = json.loads((folder/"result.json").read_bytes())
    manifest["evaluation_id"] = result["evaluation_id"]
    manifest["request_id"] = result["request_id"]
    (folder/"manifest.json").write_bytes(encoded(seal(manifest,"manifest_id")))


@pytest.fixture(scope="module")
def real_study(tmp_path_factory):
    path=tmp_path_factory.mktemp("section-worker")/"job"
    result=job.run(SECTION,path)
    return path,result


def test_real_bounded_job_and_solver_free_replay(real_study, monkeypatch):
    path,result=real_study
    assert result["execution"]=="completed"
    assert result["gate"]["state"]=="converged-under-declared-rule"
    assert len(result["level_evaluation_ids"])==4
    assert result["gate"]["final_change_relative"]<.01
    assert result["gate"]["selected_J_m4"]>0
    assert all(result[k] is False for k in job.FLAGS)
    def forbidden(*args,**kwargs):pytest.fail("verification attempted a solve or child process")
    monkeypatch.setattr(core,"spsolve",forbidden)
    monkeypatch.setattr(job.subprocess,"run",forbidden)
    assert job.verify(path)["evaluation_id"]==result["evaluation_id"]
    with pytest.raises(FileExistsError):job.run(SECTION,path)


def test_pure_request_binds_geometry_and_resources():
    first=job.request(SECTION); second=job.request(SECTION)
    changed=job.request(dict(SECTION,wall_m=.005))
    assert first==second and first["request_id"]==identity({k:v for k,v in first.items() if k!="request_id"})
    assert changed["request_id"]!=first["request_id"]
    assert first["child_runtime"]["thread_environment"]=={k:"1" for k in job.THREADS}
    assert first["resources"]["effective_memory_bytes"]<=1024*1024**2
    first["policy"]["levels"].clear()
    assert job.request(SECTION)==second


def test_worker_failure_keeps_logs_and_never_promotes(tmp_path,monkeypatch):
    monkeypatch.setattr(job.subprocess,"run",lambda *a,**k: subprocess.CompletedProcess(a[0],19))
    path=tmp_path/"failed";result=job.run(SECTION,path)
    assert result["execution"]=="failed" and result["gate"]["state"]=="held"
    assert result["gate"]["selected_J_m4"] is None and "missing-mesh-levels" in result["gate"]["reasons"]
    assert (path/"stdout.log").is_file() and (path/"stderr.log").is_file()
    assert job.verify(path)["verified"]


def test_interrupted_partial_level_is_preserved_as_held(tmp_path,monkeypatch):
    path=tmp_path/"interrupted"
    def timeout(*args,**kwargs):
        (path/"level-1.partial").write_bytes(b'{"partial":')
        raise subprocess.TimeoutExpired(args[0],30)
    monkeypatch.setattr(job.subprocess,"run",timeout)
    result=job.run(SECTION,path)
    assert result["execution"]=="interrupted" and result["gate"]["state"]=="held"
    assert result["gate"]["selected_J_m4"] is None
    assert (path/"level-1.partial").read_bytes()==b'{"partial":'
    assert job.verify(path)["verified"]


def test_success_exit_without_results_is_held(tmp_path,monkeypatch):
    monkeypatch.setattr(job.subprocess,"run",lambda *a,**k: subprocess.CompletedProcess(a[0],0))
    result=job.run(SECTION,tmp_path/"incomplete")
    assert result["execution"]=="failed" and result["reason"]=="child-incomplete-output"
    assert result["gate"]["state"]=="held" and result["gate"]["selected_J_m4"] is None


def test_consistent_saved_field_with_bad_residual_returns_unverified_hold(tmp_path,real_study,monkeypatch):
    source,_=real_study;path=tmp_path/"poor-convergence"
    rows=[json.loads((source/f"level-{n}.json").read_bytes()) for n in job.LEVELS]
    altered=rows[0]["warping_m2"][:];altered[1]+=1e-8
    rows[0]=core._rhs(SECTION,through_wall=1,gauge_node=0,saved_warping=altered)
    assert rows[0]["numerical"]["weak_residual_relative"]>1e-8
    def completed(*args,**kwargs):
        for n,row in zip(job.LEVELS,rows):job._write(path/f"level-{n}.json",row)
        return subprocess.CompletedProcess(args[0],0)
    monkeypatch.setattr(job.subprocess,"run",completed)
    result=job.run(SECTION,path)
    assert result["verified"] is False and result["execution"]=="completed"
    assert result["gate"]["state"]=="held" and result["gate"]["selected_J_m4"] is None
    assert "numerical-consistency-weak_residual_relative" in result["gate"]["reasons"]
    assert (path/"stderr.log").exists() and (path/"level-8.json").exists()
    monkeypatch.setattr(core,"spsolve",lambda *a,**k: pytest.fail("held replay attempted sparse solve"))
    replay=job.verify(path)
    assert replay==result and replay["verified"] is False
    # A numerical hold at the first level must not bypass reconstruction of a
    # later level, even if its altered identity and manifest are resealed.
    later_path=path/"level-8.json";later=json.loads(later_path.read_bytes())
    later["J_energy_m4"]*=.9
    later_path.write_bytes(encoded(seal(later,"evaluation_id")))
    saved=json.loads((path/"result.json").read_bytes());saved["level_evaluation_ids"][-1]=later["evaluation_id"]
    (path/"result.json").write_bytes(encoded(seal(saved,"evaluation_id")));reseal_manifest(path)
    with pytest.raises(ValueError,match="Saved torsion field"):
        job.verify(path)


def test_parent_and_forced_child_thread_contexts_are_distinct(tmp_path,monkeypatch):
    monkeypatch.setenv("OPENBLAS_NUM_THREADS","2")
    path=tmp_path/"worker";request=job.request(SECTION);result=job.run(SECTION,path)
    assert request["parent_runtime"]["thread_environment"]["OPENBLAS_NUM_THREADS"]=="2"
    assert request["child_runtime"]["thread_environment"]["OPENBLAS_NUM_THREADS"]=="1"
    assert result["execution"]=="completed" and job.verify(path)["verified"]
    monkeypatch.setenv("OPENBLAS_NUM_THREADS","3")
    with pytest.raises(ValueError,match="request, source, tool, runtime or resources"):
        job.verify(path)


def test_held_due_to_nonconvergent_mesh_rule():
    rows=[dict(request=dict(through_wall=n),J_energy_m4=j,quantities=dict(polar_inertia_m4=10.),
               numerical=dict(weak_residual_relative=0.,energy_torque_relative_difference=0.,stationary_energy_relative_difference=0.),
               evaluation_id=str(n)) for n,j in zip(job.LEVELS,(4.,3.,2.,1.))]
    value=job._gate(rows)
    assert value["state"]=="held" and value["selected_J_m4"] is None
    assert "last-mesh-change-exceeds-rule" in value["reasons"]


def test_resealed_geometry_and_source_cannot_change(tmp_path,real_study):
    import shutil
    source,_=real_study;path=tmp_path/"copy";shutil.copytree(source,path)
    request=json.loads((path/"request.json").read_bytes());request["sources"][core.PRODUCER]="0"*64
    (path/"request.json").write_bytes(encoded(seal(request,"request_id")))
    result=json.loads((path/"result.json").read_bytes());result["request_id"]=request["request_id"]
    (path/"result.json").write_bytes(encoded(seal(result,"evaluation_id")));reseal_manifest(path)
    with pytest.raises(ValueError,match="request, source, tool, runtime or resources"):
        job.verify(path)


@pytest.mark.parametrize("field",["J_energy_m4","warping_m2"])
def test_resealed_level_field_cannot_be_promoted(tmp_path,real_study,field):
    import shutil
    source,_=real_study;path=tmp_path/"copy";shutil.copytree(source,path)
    p=path/"level-8.json";row=json.loads(p.read_bytes())
    if field=="J_energy_m4":row[field]*=.9
    else:row[field][1]+=.01
    p.write_bytes(encoded(seal(row,"evaluation_id")))
    result=json.loads((path/"result.json").read_bytes());result["level_evaluation_ids"][-1]=row["evaluation_id"]
    result["gate"]["selected_evaluation_id"]=row["evaluation_id"]
    result["gate"]["selected_J_m4"]=row["J_energy_m4"]
    (path/"result.json").write_bytes(encoded(seal(result,"evaluation_id")));reseal_manifest(path)
    with pytest.raises(ValueError):job.verify(path)


def test_lower_parent_caps_are_never_raised(monkeypatch):
    real=resource.getrlimit
    def lower(kind):
        if kind==resource.RLIMIT_AS:return (800*1024**2,900*1024**2)
        if kind==resource.RLIMIT_CPU:return (12,15)
        return real(kind)
    monkeypatch.setattr(resource,"getrlimit",lower)
    limits=job._resources()
    assert limits["effective_memory_bytes"]==800*1024**2 and limits["effective_cpu_seconds"]==12


def test_symlinked_payload_rejected(tmp_path,real_study):
    import shutil
    source,_=real_study;path=tmp_path/"copy";shutil.copytree(source,path)
    (path/"stdout.log").unlink();(path/"stdout.log").symlink_to(path/"stderr.log")
    with pytest.raises(ValueError):job.verify(path)


def test_resealed_manifest_schema_or_extra_field_is_rejected(tmp_path,real_study):
    import shutil
    source,_=real_study
    for name,mutate in (("schema",lambda m:m.update(schema="unrecognized")),
                        ("extra",lambda m:m.update(unverified_extra=True))):
        path=tmp_path/name;shutil.copytree(source,path)
        manifest=json.loads((path/"manifest.json").read_bytes());mutate(manifest)
        (path/"manifest.json").write_bytes(encoded(seal(manifest,"manifest_id")))
        with pytest.raises(ValueError,match="manifest or inventory"):job.verify(path)
