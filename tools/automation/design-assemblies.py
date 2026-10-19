#!/usr/bin/env python3
"""Qualify and run the source-bound Baghdad assembly design programme."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT),str(ROOT/'design/component-catalogue/src')]
from engineering.assembly_design import workflow,publication,baseline,development
from engineering.twin_workflow import core


def units(workspace):
    def quote(x):return '"'+str(x).replace('\\','\\\\').replace('"','\\"').replace('%','%%')+'"'
    command=' '.join(map(quote,[sys.executable,Path(__file__).resolve(),'cycle','--workspace',Path(workspace).resolve(),'--budget','6']))
    developer=' '.join(map(quote,[sys.executable,Path(__file__).resolve(),'develop','--workspace',Path(workspace).resolve()]))
    return {'osr-assembly-capability.service':'[Unit]\nDescription=OpenSourceRail isolated assembly capability development and review\n\n[Service]\nType=oneshot\nExecStart='+developer+'\nEnvironment=OPENBLAS_NUM_THREADS=1\nEnvironment=OMP_NUM_THREADS=1\nNice=15\nCPUQuota=150%\nMemoryMax=2G\nTasksMax=256\nTimeoutStartSec=30min\nUMask=0077\n',
        'osr-assembly-capability.timer':'[Unit]\nDescription=OpenSourceRail hourly assembly capability development\n\n[Timer]\nOnBootSec=3min\nOnUnitActiveSec=1h\nPersistent=true\n\n[Install]\nWantedBy=timers.target\n',
        'osr-assembly-design.service':'[Unit]\nDescription=OpenSourceRail sourced assembly design and verification\n\n[Service]\nType=oneshot\nExecStart='+command+'\nEnvironment=OPENBLAS_NUM_THREADS=1\nEnvironment=OMP_NUM_THREADS=1\nNice=15\nCPUQuota=150%\nMemoryMax=2G\nTasksMax=256\nTimeoutStartSec=15min\nUMask=0077\n',
        'osr-assembly-design.timer':'[Unit]\nDescription=OpenSourceRail automatic assembly design cadence\n\n[Timer]\nOnBootSec=2min\nOnUnitActiveSec=5min\nPersistent=true\n\n[Install]\nWantedBy=timers.target\n'}


def cycle(workspace,budget):
    result=workflow.run(workspace,budget=budget)
    latest=workspace/'latest'
    # Heartbeats/cadence do not create duplicate presentation generations.
    with workflow.locked(workspace) as (workspace,db):
        active=core.read(workspace/'active.json');prepared=core.read(workspace/'epochs'/active['epoch']/'baseline.json',maximum=30_000_000)
        signature=core.digest(workflow.summary(workspace,db,active['epoch'],prepared))
    if latest.exists() and core.read(latest/'manifest.json',maximum=20_000_000)['progress_digest']==signature:
        publication.verify(latest);return result
    stage=Path(tempfile.mkdtemp(prefix='.assembly-export-',dir=workspace));stage.rmdir()
    try:
        publication.export(workspace,stage)
        if latest.exists():
            from engineering.design_engine.publication import exchange
            exchange(stage,latest);shutil.rmtree(stage)
        else:stage.rename(latest)
    finally:
        if stage.exists():shutil.rmtree(stage)
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=('qualify','run','cycle','status','export','verify','install','develop'))
    p.add_argument('--workspace',type=Path,default=workflow.DEFAULT);p.add_argument('--output',type=Path);p.add_argument('--budget',type=int,default=6);p.add_argument('--no-native',action='store_true');a=p.parse_args();a.workspace=a.workspace.resolve()
    if a.action=='qualify':result={'qualification':str(workflow.qualify(a.workspace))}
    elif a.action=='run':result=workflow.run(a.workspace,budget=a.budget,native=not a.no_native)
    elif a.action=='cycle':result=cycle(a.workspace,a.budget)
    elif a.action=='develop':
        result=development.run(a.workspace);core.write(a.workspace/'development/status.json',result)
    elif a.action=='status':result=core.read(a.workspace/'status.json',maximum=20_000_000)
    elif a.action in {'export','verify'}:
        if a.output is None:p.error('--output required')
        result=publication.export(a.workspace,a.output) if a.action=='export' else publication.verify(a.output)
    else:
        workflow.qualification(a.workspace);folder=Path.home()/'.config/systemd/user';folder.mkdir(parents=True,exist_ok=True)
        for name,body in units(a.workspace).items():
            path=folder/name
            if path.exists() and 'Description=OpenSourceRail' not in path.read_text():raise ValueError('unit is owned by another application')
            path.write_text(body)
        subprocess.run(['systemctl','--user','daemon-reload'],check=True)
        subprocess.run(['systemctl','--user','enable','--now','osr-assembly-design.timer','osr-assembly-capability.timer'],check=True)
        result=dict(timer='osr-assembly-design.timer',cadence='five minutes',workspace=str(a.workspace),report=str(a.workspace/'latest/index.html'))
    if 'trials' in result:result={k:result[k] for k in ('epoch','controller_state','executed_this_cycle','counts','selected') if k in result}
    elif 'files_sha256' in result:result={k:result[k] for k in ('schema','epoch','design_complete')}
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
