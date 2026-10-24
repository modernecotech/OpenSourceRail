"""Stdlib-only worker limits and process-group death supervision."""
import json
import math
import os
from pathlib import Path
import resource
import signal
import time


def process_start(pid):
    try:
        raw=Path(f'/proc/{pid}/stat').read_text();return raw[raw.rfind(')')+2:].split()[19]
    except (OSError,IndexError):return None


def group_members(pgid):
    found=[]
    for path in Path('/proc').glob('[0-9]*/stat'):
        try:
            raw=path.read_text();fields=raw[raw.rfind(')')+2:].split()
            if int(fields[2])==pgid and fields[0]!='Z':found.append(int(path.parent.name))
        except (OSError,ValueError,IndexError):pass
    return found


def stop_group(pgid,*,expected_start=None,wait_s=2.):
    """Kill an isolated worker group, never the coordinator's own process group."""
    if type(pgid) is not int or pgid<=1 or pgid==os.getpgrp():raise ValueError('isolated worker group required')
    if expected_start is not None:
        actual=process_start(pgid)
        if actual is not None and actual!=expected_start:raise ValueError('worker PID was reused; process group ownership differs')
    try:os.killpg(pgid,signal.SIGKILL)
    except ProcessLookupError:pass
    until=time.monotonic()+wait_s
    while group_members(pgid) and time.monotonic()<until:time.sleep(.01)
    if group_members(pgid):raise RuntimeError('worker descendants remain after process-group cleanup')


def apply(memory_mb,timeout_s,*,parent_pid=None,parent_start=None):
    """Apply before NumPy/domain imports; watchdog survives a killed worker."""
    if type(memory_mb) is not int or not 256<=memory_mb<=16384 or not isinstance(timeout_s,(int,float)) or isinstance(timeout_s,bool) or not math.isfinite(timeout_s) or not 0<timeout_s<=3600:
        raise ValueError('bounded worker memory/time limits required')
    resource.setrlimit(resource.RLIMIT_AS,(memory_mb*1024**2,memory_mb*1024**2))
    cpu=max(1,math.ceil(timeout_s));resource.setrlimit(resource.RLIMIT_CPU,(cpu+1,cpu+2))
    resource.setrlimit(resource.RLIMIT_FSIZE,(64*1024**2,64*1024**2));resource.setrlimit(resource.RLIMIT_CORE,(0,0))
    worker=os.getpid();group=os.getpgrp();isolated=group==worker;watchdog=False
    if hasattr(os,'fork'):
        started=time.monotonic();child=os.fork()
        if child==0:
            try:
                while True:
                    parent_gone=parent_pid is not None and (process_start(parent_pid)!=parent_start)
                    if os.getppid()!=worker or parent_gone or time.monotonic()-started>timeout_s+2:
                        if isolated:
                            try:os.killpg(group,signal.SIGKILL)
                            except ProcessLookupError:pass
                        else:
                            try:os.kill(worker,signal.SIGKILL)
                            except ProcessLookupError:pass
                        os._exit(0)
                    time.sleep(.05)
            finally:os._exit(1)
        watchdog=isolated
    return dict(memory_limit_bytes=resource.getrlimit(resource.RLIMIT_AS)[0],cpu_limit_s=resource.getrlimit(resource.RLIMIT_CPU)[0],
        file_limit_bytes=resource.getrlimit(resource.RLIMIT_FSIZE)[0],watchdog_process_group_cleanup=watchdog,
        worker_pid=worker,process_group=group,limits_before_domain_import=True)
