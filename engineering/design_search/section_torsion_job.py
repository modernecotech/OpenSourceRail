"""Run and replay a bounded actual-wall cross-section torsion study.

The child is a resource-limited Python process, not a filesystem sandbox.
Completion is a declared numerical convergence screen, never material or
physical acceptance. Verification reassembles saved fields without solving.
"""
from __future__ import annotations

from copy import deepcopy
import json
import math
import os
from pathlib import Path
import platform
import resource
import stat
import subprocess
import sys

import numpy as np
import scipy
from scipy.sparse.linalg._dsolve import _superlu

from engineering.station_rail import ROOT, common
from engineering.station_rail.common import digest, encoded, identity
from . import section_torsion

PRODUCER = "engineering/design_search/section_torsion_job.py"
LEVELS = (1, 2, 4, 8)
MAX_FILE_BYTES = 32 * 1024**2
THREADS = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS")
FLAGS = dict(physical_accepted=False, engineering_accepted=False, configuration_adopted=False,
             manufacturing_release=False, operating_release=False, installed_mass_complete=False)
LOADED = {PRODUCER:digest(__file__), section_torsion.PRODUCER:digest(section_torsion.__file__),
          "engineering/station_rail/common.py":digest(common.__file__)}
POLICY = dict(levels=list(LEVELS), residual_maximum=1e-8, nonincrease_relative_tolerance=1e-10,
              final_change_relative_maximum=0.01,
              scope="Numerical successive-mesh rule; not a certified error bound or physical acceptance")


def _sources(root):
    root = Path(root).resolve()
    if root != Path(ROOT).resolve():
        raise ValueError("Use the checkout from which the worker was imported")
    for name, expected in LOADED.items():
        path = root / name
        if not stat.S_ISREG(path.lstat().st_mode) or digest(path) != expected:
            raise ValueError("Section worker source changed: " + name)
    if digest(__file__) != LOADED[PRODUCER] or digest(section_torsion.__file__) != LOADED[section_torsion.PRODUCER] or digest(common.__file__) != LOADED["engineering/station_rail/common.py"]:
        raise ValueError("Executing section worker source changed")
    return dict(sorted(LOADED.items()))


def _runtime(*, child=False):
    exe = Path(sys.executable).resolve()
    lib = Path(_superlu.__file__).resolve()
    return dict(python_implementation=platform.python_implementation(), python_version=platform.python_version(), python_full_version=sys.version,
                python_executable=str(exe), python_executable_sha256=digest(exe), numpy_version=np.__version__,
                scipy_version=scipy.__version__, superlu_path=str(lib), superlu_sha256=digest(lib),
                thread_environment={k:("1" if child else os.environ.get(k)) for k in THREADS})


def _resources():
    def cap(kind, maximum):
        finite = [n for n in resource.getrlimit(kind) if n != resource.RLIM_INFINITY]
        value = min([maximum, *finite])
        if value <= 0:
            raise ValueError("Positive effective child resource limit required")
        return value
    return dict(effective_memory_bytes=cap(resource.RLIMIT_AS, 1024*1024**2),
                effective_cpu_seconds=cap(resource.RLIMIT_CPU, 30), wall_seconds=30, threads=1,
                enforcement="Child POSIX RLIMIT_AS/RLIMIT_CPU and subprocess wall timeout; no filesystem sandbox")


def _section(value):
    if not isinstance(value, dict) or set(value) != {"width_m", "height_m", "wall_m"}:
        raise ValueError("Explicit three-field hollow RHS geometry required")
    result = {}
    for name in ("width_m", "height_m", "wall_m"):
        v = value[name]
        if type(v) not in (int, float) or not math.isfinite(v) or v <= 0:
            raise ValueError("Positive finite hollow RHS dimensions required")
        result[name] = v
    if 2*result["wall_m"] >= min(result["width_m"],result["height_m"]):
        raise ValueError("Hollow RHS requires a positive interior")
    return result


def _request(section, root):
    value = dict(schema="osr-bounded-section-torsion-request/1", section=_section(section),
                 sources=_sources(root), parent_runtime=_runtime(), child_runtime=_runtime(child=True),
                 resources=_resources(), policy=deepcopy(POLICY))
    value["request_id"] = identity(value)
    return value


def request(section, *, root=ROOT):
    """Return the exact sealed request before allocating a job or its budget."""
    return _request(section, Path(root).resolve())


def _core_child_runtime(child):
    return dict(python=child["python_full_version"], numpy=child["numpy_version"], scipy=child["scipy_version"],
                implementation=child["python_implementation"], python_executable_sha256=child["python_executable_sha256"],
                numerical_thread_environment=child["thread_environment"])


def _write(path, data):
    raw = encoded(data)
    if len(raw) > MAX_FILE_BYTES:
        raise ValueError("Section study record exceeds file limit")
    with Path(path).open("xb") as handle:
        handle.write(raw)


def _read(path):
    descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    try:
        meta = os.fstat(descriptor)
        if not stat.S_ISREG(meta.st_mode) or meta.st_size > MAX_FILE_BYTES:
            raise ValueError("Bounded regular section study file required")
        with os.fdopen(descriptor,"rb",closefd=False) as handle:
            raw = handle.read(MAX_FILE_BYTES+1)
        after=os.fstat(descriptor)
        if (len(raw) != meta.st_size or len(raw)>MAX_FILE_BYTES or
                any(getattr(meta,k)!=getattr(after,k) for k in ("st_dev","st_ino","st_size","st_mtime_ns","st_ctime_ns"))):
            raise ValueError("Section study file changed or exceeds its limit")
        return raw
    finally:
        os.close(descriptor)


def _parse(raw):
    def pairs(items):
        result = {}
        for k,v in items:
            if k in result:raise ValueError("Duplicate section study JSON key")
            result[k]=v
        return result
    def bad(_):raise ValueError("Non-finite section study JSON")
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=bad)


def _inventory(path):
    result = {}
    for entry in Path(path).iterdir():
        if entry.name == "manifest.json":continue
        if entry.is_symlink() or not stat.S_ISREG(entry.lstat().st_mode):
            raise ValueError("Section study permits regular files only")
        result[entry.name] = digest_bytes(_read(entry))
    return dict(sorted(result.items()))


def digest_bytes(raw):
    from hashlib import sha256
    return sha256(raw).hexdigest()


def _gate(records):
    reasons=[]
    if len(records)!=len(LEVELS):
        reasons.append("missing-mesh-levels")
    values=[]
    for level, row in zip(LEVELS, records):
        if row.get("request",{}).get("through_wall") != level:
            reasons.append("mesh-level-order-differs")
        j=row.get("J_energy_m4"); ip=row.get("quantities",{}).get("polar_inertia_m4")
        if type(j) not in (int,float) or not math.isfinite(j) or j<=0 or type(ip) not in (int,float) or not math.isfinite(ip) or j>ip*(1+1e-10):
            reasons.append("invalid-torsion-or-polar-bound")
        else:values.append(float(j))
        for key in ("weak_residual_relative","energy_torque_relative_difference","stationary_energy_relative_difference"):
            v=row.get("numerical",{}).get(key)
            if type(v) not in (int,float) or not math.isfinite(v) or v<0 or v>POLICY["residual_maximum"]:
                reasons.append("numerical-consistency-"+key)
    change=None
    if len(values)==len(LEVELS):
        if any(b>a*(1+POLICY["nonincrease_relative_tolerance"]) for a,b in zip(values,values[1:])):
            reasons.append("nonmonotonic-nested-energies")
        change=abs(values[-1]-values[-2])/values[-1]
        if change>POLICY["final_change_relative_maximum"]:reasons.append("last-mesh-change-exceeds-rule")
    return dict(state="held" if reasons else "converged-under-declared-rule", reasons=sorted(set(reasons)),
                final_change_relative=change, selected_evaluation_id=None if reasons else records[-1]["evaluation_id"],
                selected_J_m4=None if reasons else values[-1], policy=deepcopy(POLICY))


def _limits(resources):
    resource.setrlimit(resource.RLIMIT_AS, (resources["effective_memory_bytes"],)*2)
    resource.setrlimit(resource.RLIMIT_CPU, (resources["effective_cpu_seconds"],)*2)


def _child(request_path, output):
    request=_parse(_read(request_path)); root=Path(ROOT).resolve()
    if request.get("sources") != _sources(root) or request.get("child_runtime") != _runtime():
        raise ValueError("Child worker source or forced runtime differs")
    if request.get("request_id") != identity({k:v for k,v in request.items() if k!="request_id"}):
        raise ValueError("Child request identity differs")
    if request.get("policy") != POLICY or _section(request.get("section")) != request["section"]:
        raise ValueError("Child geometry or numerical policy differs")
    for level in LEVELS:
        row=section_torsion.evaluate(request["section"],through_wall=level)
        partial=Path(output)/f"level-{level}.partial"
        final=Path(output)/f"level-{level}.json"
        _write(partial,row)
        if final.exists():raise FileExistsError("Section mesh result already exists")
        os.replace(partial,final)


def run(section, output, *, root=ROOT):
    """Run one fresh bounded child; retain partial records and diagnostic logs."""
    root=Path(root).resolve(); request=_request(section,root)
    folder=Path(output).absolute(); folder.mkdir(parents=True,exist_ok=False)
    _write(folder/"request.json",request)
    environment=dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONNOUSERSITE="1", PYTHONPATH=str(root),
                     **{name:"1" for name in THREADS})
    environment.pop("PYTHONHOME",None)
    execution="failed"; reason=None; returncode=None
    with (folder/"stdout.log").open("xb") as stdout,(folder/"stderr.log").open("xb") as stderr:
        try:
            completed=subprocess.run([sys.executable,"-m","engineering.design_search.section_torsion_job",
                                      "--worker",str(folder/"request.json"),str(folder)],cwd=root,env=environment,
                                     stdout=stdout,stderr=stderr,timeout=request["resources"]["wall_seconds"],
                                     preexec_fn=lambda:_limits(request["resources"]),check=False)
            returncode=completed.returncode
            if returncode==0:execution="completed"
            else:reason="child-process-failed"
        except subprocess.TimeoutExpired:
            execution="interrupted";reason="child-wall-timeout"
        except (OSError,subprocess.SubprocessError) as exc:
            reason="child-launch-failed: "+str(exc)
    if _request(section,root)!=request:raise ValueError("Section worker source, runtime or resources changed")
    records=[]
    for level in LEVELS:
        path=folder/f"level-{level}.json"
        if not path.exists():break
        records.append(_parse(_read(path)))
    if execution=="completed" and len(records)!=len(LEVELS):
        execution="failed";reason="child-incomplete-output"
    gate=_gate(records)
    if execution!="completed":
        gate.update(state="held",selected_evaluation_id=None,selected_J_m4=None)
        gate["reasons"]=sorted(set(gate["reasons"]+[reason or "worker-incomplete"]))
    result=dict(schema="osr-bounded-section-torsion-result/1",request_id=request["request_id"],
                execution=execution,reason=reason,returncode=returncode,gate=gate,
                level_evaluation_ids=[r["evaluation_id"] for r in records],
                native_solver_jobs=0,integrated_selection=None,**FLAGS)
    result["evaluation_id"]=identity(result);_write(folder/"result.json",result)
    manifest=dict(schema="osr-bounded-section-torsion-manifest/1",request_id=request["request_id"],
                  evaluation_id=result["evaluation_id"],files=_inventory(folder),**FLAGS)
    manifest["manifest_id"]=identity(manifest);_write(folder/"manifest.json",manifest)
    return verify(folder,root=root)


def verify(output, *, root=ROOT):
    """Rebuild the request, mesh and saved fields; never launch or solve."""
    root=Path(root).resolve();folder=Path(output)
    if folder.is_symlink() or not folder.is_dir():raise ValueError("Regular section study directory required")
    manifest=_parse(_read(folder/"manifest.json"));request=_parse(_read(folder/"request.json"));result=_parse(_read(folder/"result.json"))
    if (set(manifest)!={"schema","request_id","evaluation_id","files","manifest_id",*FLAGS}
            or manifest.get("schema")!="osr-bounded-section-torsion-manifest/1"
            or manifest.get("manifest_id")!=identity({k:v for k,v in manifest.items() if k!="manifest_id"})
            or manifest.get("files")!=_inventory(folder)):
        raise ValueError("Section study manifest or inventory differs")
    if request != _request(request.get("section"),root):raise ValueError("Section study request, source, tool, runtime or resources differ")
    names=set(manifest["files"]); required={"request.json","result.json","stdout.log","stderr.log"}
    allowable={f"level-{n}.json" for n in LEVELS}|{f"level-{n}.partial" for n in LEVELS}
    if not required<=names or names-required-allowable:
        raise ValueError("Section study file membership differs")
    records=[]
    for level in LEVELS:
        name=f"level-{level}.json"
        if name not in names:break
        records.append(_parse(_read(folder/name)))
    full={f"level-{n}.json" for n in LEVELS[:len(records)]}
    partial=names-required-full
    if partial and (len(records)==len(LEVELS) or partial!={f"level-{LEVELS[len(records)]}.partial"}):
        raise ValueError("Partial section levels are not a contiguous prefix")
    numerical_failure = False
    numerical_failure_reason = "Saved warping fails the declared 1e-8 numerical equation/energy consistency checks"
    for level,row in zip(LEVELS,records):
        if row.get("geometry") != dict(kind="rhs",**request["section"]) or row.get("request") != dict(through_wall=level,gauge_node=0):
            raise ValueError("Section level geometry or mesh request differs")
        try:
            section_torsion.verify_result(row,expected_runtime=_core_child_runtime(request["child_runtime"]))
        except ValueError as exc:
            # Core checks exact reconstruction first, then raises this specific
            # error only for an excessive numerical residual. Keep validating
            # every remaining field and the sealed hold before returning it.
            if str(exc)!=numerical_failure_reason:
                raise
            numerical_failure = True
    execution=result.get("execution");reason=result.get("reason");rc=result.get("returncode")
    if execution=="completed":
        if rc!=0 or reason is not None or len(records)!=len(LEVELS) or partial:raise ValueError("Completed section child is incomplete")
    elif execution=="interrupted":
        if rc is not None or reason!="child-wall-timeout":raise ValueError("Interrupted section state differs")
    elif execution=="failed":
        if not ((reason=="child-process-failed" and type(rc) is int and rc!=0)
                or (reason=="child-incomplete-output" and rc==0 and len(records)<len(LEVELS))
                or (isinstance(reason,str) and reason.startswith("child-launch-failed: ") and rc is None)):
            raise ValueError("Failed section state or return code differs")
    else:raise ValueError("Unknown section execution state")
    gate=_gate(records)
    if execution!="completed":
        gate.update(state="held",selected_evaluation_id=None,selected_J_m4=None)
        gate["reasons"]=sorted(set(gate["reasons"]+[reason or "worker-incomplete"]))
    expected=dict(schema="osr-bounded-section-torsion-result/1",request_id=request["request_id"],execution=execution,
                  reason=reason,returncode=rc,gate=gate,level_evaluation_ids=[r["evaluation_id"] for r in records],
                  native_solver_jobs=0,integrated_selection=None,**FLAGS)
    expected["evaluation_id"]=identity(expected)
    if result!=expected or manifest.get("request_id")!=request["request_id"] or manifest.get("evaluation_id")!=result["evaluation_id"] or any(manifest.get(k) is not False for k in FLAGS):
        raise ValueError("Section result or non-promoting disposition differs")
    if numerical_failure:
        if gate["state"]!="held" or gate["selected_J_m4"] is not None or gate["selected_evaluation_id"] is not None:
            raise ValueError("Numerically invalid section cannot be promoted")
        return dict(verified=False,verification_reason=numerical_failure_reason,manifest_id=manifest["manifest_id"],**result)
    return dict(verified=True,manifest_id=manifest["manifest_id"],**result)


if __name__ == "__main__":
    if len(sys.argv)!=4 or sys.argv[1]!="--worker":raise SystemExit("Internal bounded child only")
    _child(Path(sys.argv[2]),Path(sys.argv[3]))
