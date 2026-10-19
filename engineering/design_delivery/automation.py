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


def recover_publication(repository,state_path,*,push):
    """Resume an owned transaction before considering fresh design selections.

    A crash after commit but before recording it is recovered from the exact
    parent, manifest and path-limited diff. Push only that recorded commit.
    """
    if not state_path.exists():return None
    state=core.read(state_path)
    if state['repository']!=str(repository):raise ValueError('publication recovery repository differs')
    if state['phase']=='pushed':
        stage=Path(state['stage'])
        if stage.parent==state_path.parent and stage.name.startswith('package-') and stage.is_dir() and not stage.is_symlink():shutil.rmtree(stage)
        return None
    if state['phase']=='built':
        stage=Path(state['stage'])
        if stage.parent!=state_path.parent or stage.is_symlink() or not stage.name.startswith('package-'):
            raise ValueError('publication recovery stage is not owned')
        pipeline.verify(stage)
        if core.sha(stage/'manifest.json')!=state['manifest_sha256']:raise ValueError('publication recovery manifest changed')
        head=git(repository,'rev-parse','HEAD')
        if head==state['parent']:
            dirty=git(repository,'status','--porcelain')
            if dirty:
                # Atomic replacement may have completed before a crash. Only
                # the exact already-verified target generation may be committed.
                target=repository/DESTINATION;pipeline.verify(target)
                if core.sha(target/'manifest.json')!=state['manifest_sha256']:
                    raise ValueError('publication recovery target changed')
                names=git(repository,'diff','HEAD','--name-only').splitlines()+git(repository,'ls-files','--others','--exclude-standard').splitlines()
                if any(not n.startswith(DESTINATION+'/') for n in names):raise ValueError('unrelated recovery edits')
                manifest=core.read(target/'manifest.json',maximum=20_000_000)
                if not all((repository/n).is_file() and core.sha(repository/n)==d for n,d in manifest['publisher_sources'].items()):raise ValueError('recovery qualification sources changed')
                if git(repository,'rev-parse','--abbrev-ref','HEAD')!='main':raise ValueError('recovery requires main')
                git(repository,'add','--',DESTINATION)
                git(repository,'commit','-m','Publish confirmed design evidence, completion gates and assembly videos')
                head=git(repository,'rev-parse','HEAD')
            else:
                result=commit_package(repository,stage,expected_head=state['parent'])
                if not result.get('changed'):raise ValueError('recovery produced no owned publication commit')
                head=result['commit']
        if git(repository,'rev-parse',head+'^')!=state['parent']:raise ValueError('publication recovery parent changed')
        names=git(repository,'diff-tree','--no-commit-id','--name-only','-r',head).splitlines()
        if not names or any(not n.startswith(DESTINATION+'/') for n in names):raise ValueError('publication recovery commit has unrelated paths')
        # Read committed bytes, not mutable working-copy bytes.
        import hashlib
        committed=subprocess.run(['git','-C',str(repository),'show',head+':'+DESTINATION+'/manifest.json'],check=True,capture_output=True,timeout=30).stdout
        if hashlib.sha256(committed).hexdigest()!=state['manifest_sha256']:raise ValueError('publication recovery committed manifest differs')
        state.update(phase='committed',commit=head);core.write(state_path,state)
    if state['phase']!='committed':raise ValueError('unknown publication transaction phase')
    commit=state['commit']
    if git(repository,'rev-parse',commit+'^')!=state['parent']:raise ValueError('publication retry parent differs')
    names=git(repository,'diff-tree','--no-commit-id','--name-only','-r',commit).splitlines()
    if not names or any(not n.startswith(DESTINATION+'/') for n in names):raise ValueError('publication retry includes unrelated paths')
    import hashlib
    committed=subprocess.run(['git','-C',str(repository),'show',commit+':'+DESTINATION+'/manifest.json'],check=True,capture_output=True,timeout=30).stdout
    if hashlib.sha256(committed).hexdigest()!=state['manifest_sha256']:raise ValueError('publication retry manifest differs')
    if not push:return dict(changed=True,commit=state['commit'],pushed=False,phase='committed',recovered=True)
    # Explicit commit refspec cannot accidentally push unrelated later edits.
    git(repository,'push','origin',state['commit']+':refs/heads/main')
    state.update(phase='pushed',pushed_unix=time.time());core.write(state_path,state)
    stage=Path(state['stage'])
    if stage.parent==state_path.parent and stage.name.startswith('package-') and stage.is_dir() and not stage.is_symlink():shutil.rmtree(stage)
    return dict(changed=True,commit=state['commit'],pushed=True,phase='pushed',recovered=True)


def cycle(workspace,repository,qualification,*,push=False,force=False):
    workspace=Path(workspace).resolve();root=workspace/'publications';root.mkdir(exist_ok=True)
    with (root/'.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        repository=Path(repository).resolve();state_path=root/'transaction.json'
        recovered=recover_publication(repository,state_path,push=push)
        if recovered:return recovered
        head=git(repository,'rev-parse','HEAD')
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
        except BaseException:
            # No Git mutation or journal exists yet; discard only this call's
            # failed scratch build. Journalled generations remain recoverable.
            if stage.is_dir() and not stage.is_symlink():shutil.rmtree(stage)
            raise
        # Persist built state BEFORE any working-tree/Git mutation. Keep stage
        # until successful push so either side of a crash can be reconstructed.
        transaction=dict(schema='osr-publication-transaction/1',phase='built',repository=str(repository),
            stage=str(stage),parent=head,signature=state['signature'],manifest_sha256=core.sha(stage/'manifest.json'))
        core.write(state_path,transaction)
        result=recover_publication(repository,state_path,push=push)
        history=root/'history'
        if history.exists():
            owned=sorted((p for p in history.iterdir() if p.is_dir() and not p.is_symlink() and (p.name.startswith('previous-') or p.name.startswith('continuous-delivery-'))),key=lambda p:p.stat().st_mtime,reverse=True)
            for old in owned[2:]:shutil.rmtree(old)
        return result
