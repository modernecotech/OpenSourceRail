"""Small single-process CalculiX runner for explicit resource revisions.

Only the separately reviewed 8 GiB/240 s continuation profile is admitted.
The OS address-space limit applies to the solver child; no container, user,
filesystem, or network isolation is asserted.
"""
from __future__ import annotations

import os
import resource
import subprocess
import time
from pathlib import Path

from engineering.station_rail.common import digest, encoded
from . import grammar_shell

PRODUCER = "engineering/design_search/railway_native_execution.py"
SOLVER = "/usr/bin/ccx"


def execute(raw, definition, output, *, memory_mb: int, timeout_s: int):
    if (type(memory_mb) is not int or memory_mb!=8192 or type(timeout_s) is not int or timeout_s!=240):
        raise ValueError("This runner accepts only the explicit 8 GiB/240 s refinement profile")
    output=Path(output);output.mkdir(parents=True)
    (output/"model.inp").write_text(raw)
    (output/"definition.json").write_bytes(encoded(definition))
    inherited=[x for x in resource.getrlimit(resource.RLIMIT_AS) if x!=resource.RLIM_INFINITY]
    cap=min([memory_mb*1024**2,*inherited]) if inherited else memory_mb*1024**2
    solver_hash=digest(SOLVER)
    tool=dict(ccx_path=SOLVER,ccx_sha256=solver_hash,requested_memory_mb=memory_mb,
        RLIMIT_AS_bytes=cap,OMP_threads=1,timeout_s=timeout_s,
        resource_control="POSIX RLIMIT_AS on native solver child; shared host workspace, no container isolation")
    started=time.monotonic();result=dict(execution="tool_error",numerical_validity="unknown",engineering_screen="unknown")
    def bounded():resource.setrlimit(resource.RLIMIT_AS,(cap,cap))
    try:
        proc=subprocess.run([SOLVER,"model"],cwd=output,capture_output=True,timeout=timeout_s,
            preexec_fn=bounded,env={**os.environ,"OMP_NUM_THREADS":"1"})
        (output/"stdout.log").write_bytes(proc.stdout);(output/"stderr.log").write_bytes(proc.stderr)
        result['returncode']=proc.returncode
        if proc.returncode==0:result.update(grammar_shell.analyse(definition,output/"model.dat"))
    except subprocess.TimeoutExpired as error:
        (output/"stdout.log").write_bytes(error.stdout or b'')
        (output/"stderr.log").write_bytes(error.stderr or b'')
        result.update(execution="interrupted",reason="bounded native time limit")
    except (OSError,ValueError,KeyError,subprocess.SubprocessError) as error:
        result['reason']=str(error)
    if digest(SOLVER)!=solver_hash:raise ValueError("Native solver changed during execution")
    return dict(**result,tool=tool,runtime_s=time.monotonic()-started,
        mesh_summary={k:v for k,v in definition.items() if k not in ('nodes','loads_N','supports')})
