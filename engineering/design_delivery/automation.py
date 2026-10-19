"""Qualified, bounded publication; Git mutations are scoped to one owned package."""
from pathlib import Path
import fcntl
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import sqlite3

from engineering.twin_workflow import core
from . import pipeline

DESTINATION='docs/design-engine/continuous-delivery'


def git(repository,*args):
    return subprocess.run(['git','-C',str(repository),*args],capture_output=True,text=True,check=True,timeout=120).stdout.strip()


def qualify(output):
    output=Path(output).resolve();output.mkdir(parents=True,exist_ok=False);before=pipeline.sources()
    command=[sys.executable,'-m','pytest',*pipeline.QUALIFICATION_TESTS,'-q']
    call=subprocess.run(command,cwd=core.ROOT,capture_output=True,text=True,timeout=900,
        env={**os.environ,'OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1','PYTHONPATH':str(core.ROOT)+':'+str(core.ROOT/'design/component-catalogue/src')})
    (output/'tests.log').write_text(call.stdout+call.stderr)
    receipt=dict(schema='osr-delivery-qualification/1',passed=call.returncode==0 and before==pipeline.sources(),
        sources=before,source_commit=git(core.ROOT,'rev-parse','HEAD'),command=command,returncode=call.returncode,
        log_sha256=core.sha(output/'tests.log'),tested_unix=time.time(),**core.FLAGS)
    core.write(output/'qualification.json',receipt)
    if not receipt['passed']:raise ValueError('publication qualification failed; see '+str(output/'tests.log'))
    return receipt


def commit_package(repository,package,*,expected_head,push=False):
    """Stage only the owned package. Dirty source, stale head and failed seals veto."""
    repository=Path(repository).resolve();package=Path(package).resolve();pipeline.verify(package)
    if git(repository,'rev-parse','--abbrev-ref','HEAD')!='main':raise ValueError('publication requires main')
    if git(repository,'rev-parse','HEAD')!=expected_head or git(repository,'status','--porcelain'):
        raise ValueError('repository changed or contains unrelated edits')
    # The package was built outside the source checkout; move it atomically with
    # the existing controlled-directory publication helper and retain prior bytes.
    from engineering.design_engine.publication import publish
    manifest=core.read(package/'manifest.json',maximum=20_000_000)
    if not all((repository/name).is_file() and core.sha(repository/name)==digest for name,digest in manifest['publisher_sources'].items()):
        raise ValueError('qualification sources differ from repository')
    payload={p.relative_to(package).as_posix():p.read_bytes() for p in package.rglob('*') if p.is_file()}
    # No stale/unsealed files may survive replacement of a selected model set.
    target=repository/DESTINATION
    if target.exists():
        old={p.relative_to(target).as_posix() for p in target.rglob('*') if p.is_file()}
        if old-set(payload):
            # Publish an entirely new generation by atomic directory exchange.
            from engineering.design_engine.publication import exchange
            stage=Path(tempfile.mkdtemp(prefix='.osr-publication-stage-',dir=target.parent))
            shutil.copytree(package,stage,dirs_exist_ok=True)
            if git(repository,'rev-parse','HEAD')!=expected_head or git(repository,'status','--porcelain'):raise ValueError('repository changed before publication')
            exchange(stage,target)
            history=package.parent/'history';history.mkdir(exist_ok=True)
            stage.rename(history/('previous-'+str(time.time_ns())))
        else:
            publish(target,payload,repository=repository,sources=manifest['publisher_sources'],history=package.parent/'history')
    else:publish(target,payload,repository=repository,sources=manifest['publisher_sources'],history=package.parent/'history')
    pipeline.verify(target)
    if git(repository,'rev-parse','HEAD')!=expected_head:raise ValueError('repository head changed before publication commit')
    if not all((repository/name).is_file() and core.sha(repository/name)==digest for name,digest in manifest['publisher_sources'].items()):raise ValueError('source changed before publication commit')
    git(repository,'add','--',DESTINATION)
    staged=git(repository,'diff','--cached','--name-only').splitlines()
    if not staged:return dict(changed=False)
    if any(not name.startswith(DESTINATION+'/') for name in staged):raise ValueError('unrelated staged edits; publication commit refused')
    git(repository,'commit','-m','Publish confirmed design evidence, completion gates and assembly videos')
    commit=git(repository,'rev-parse','HEAD')
    if push:git(repository,'push','origin','main')
    return dict(changed=True,commit=commit,pushed=push)


def maintain(workspace,*,now=None):
    """Give starved task families one slot; preserve jobs, receipts and lane caps."""
    now=time.time() if now is None else now;workspace=Path(workspace).resolve()
    baseline=core.read(workspace/'active.json')['baseline_sha256'];db=sqlite3.connect(workspace/'queue.sqlite',timeout=30);db.row_factory=sqlite3.Row;changes=[]
    try:
        with db:
            db.execute('BEGIN IMMEDIATE')
            kinds=list(db.execute("SELECT lane,json_extract(task,'$.kind') kind,MAX(finished) last FROM jobs WHERE baseline=? GROUP BY lane,kind",(baseline,)))
            for kind in kinds:
                if kind['last'] is not None and now-kind['last']<900:continue
                row=db.execute("SELECT key,status,priority FROM jobs WHERE baseline=? AND lane=? AND json_extract(task,'$.kind')=? AND status IN ('queued','deferred') AND ready<=? ORDER BY priority,created LIMIT 1",(baseline,kind['lane'],kind['kind'],now)).fetchone()
                if row is None or row['priority']<=-45:continue
                displaced=None
                if row['status']=='deferred':
                    pending=db.execute("SELECT COUNT(*) FROM jobs WHERE baseline=? AND lane=? AND status IN ('queued','running')",(baseline,kind['lane'])).fetchone()[0]
                    if pending>=64:
                        other=db.execute("SELECT key FROM jobs WHERE baseline=? AND lane=? AND status='queued' AND priority>-45 ORDER BY priority DESC,created DESC LIMIT 1",(baseline,kind['lane'])).fetchone()
                        if not other:continue
                        displaced=other['key'];db.execute("UPDATE jobs SET status='deferred' WHERE key=?",(displaced,))
                db.execute("UPDATE jobs SET status='queued',priority=-45 WHERE key=?",(row['key'],))
                change=dict(baseline=baseline,kind=kind['kind'],key=row['key'],previous=dict(row),displaced_without_deletion=displaced)
                db.execute('INSERT INTO events(at,kind,payload) VALUES(?,?,?)',(now,'delivery-task-family-coverage',json.dumps(change)));changes.append(change)
            if core.read(workspace/'active.json')['baseline_sha256']!=baseline:raise ValueError('epoch changed during queue maintenance')
        return dict(prioritised=len(changes),baseline=baseline,deleted_jobs=0)
    finally:db.close()


def cycle(workspace,repository,qualification,*,push=False,force=False):
    workspace=Path(workspace).resolve();root=workspace/'publications';root.mkdir(exist_ok=True)
    with (root/'.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        repository=Path(repository).resolve();head=git(repository,'rev-parse','HEAD')
        if git(repository,'status','--porcelain'):raise ValueError('publication waits for a clean source checkout')
        state=pipeline.inspect(workspace);existing=repository/DESTINATION/'manifest.json'
        if existing.exists():
            current=core.read(existing,maximum=20_000_000)
            if current['signature']==state['signature']:
                pipeline.verify(existing.parent);return dict(changed=False,reason='selected confirmed revisions unchanged')
            if not force and time.time()-current['created_unix']<86400:
                return dict(changed=False,reason='daily binary publication budget; next candidate package waits')
        stage=root/('package-'+str(time.time_ns()))
        try:
            pipeline.build(workspace,stage,qualification)
            if pipeline.inspect(workspace)['signature']!=state['signature']:raise ValueError('live selection changed before Git publication')
            result=commit_package(repository,stage,expected_head=head,push=push)
            return result
        finally:
            # Only this call's disposable staging generation is removed. Final
            # Git package, tests, previous retained evidence and worker data stay.
            if stage.exists():shutil.rmtree(stage)
            history=root/'history'
            if history.exists():
                owned=sorted((p for p in history.iterdir() if p.is_dir() and not p.is_symlink() and (p.name.startswith('previous-') or p.name.startswith('continuous-delivery-'))),key=lambda p:p.stat().st_mtime,reverse=True)
                for old in owned[2:]:shutil.rmtree(old)
