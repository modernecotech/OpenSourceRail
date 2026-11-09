"""Exactly three frozen, private deterministic trials; no CAD/FEM execution."""
import argparse,json,os,resource,subprocess,sys,time,traceback
from pathlib import Path
from engineering.station_rail.common import identity,digest
from . import ROOT,FLAGS
from .common import policy,parent,sources,write,read
from .design import build,SUPPORT_VARIANTS
from .evaluate import evaluate


def trial(output,config_id,*,root=ROOT,support_family=None):
    out=Path(output);out.mkdir(parents=True,exist_ok=False);before=sources(root);p=policy(root);started=time.monotonic()
    request=dict(schema='osr-compact-drive-trial-input/1',config=next(c for c in p['configs'] if c['id']==config_id),source_sha256=before,parent_candidate_id=parent(root)['candidate_id'],limits=p['limits'],**FLAGS)
    if support_family is not None:request['support_family']=support_family
    write(out/'input.json',request)
    result=dict(schema='osr-compact-drive-trial-result/1',config_id=config_id,execution='failed',**FLAGS)
    try:
        body=build(config_id=config_id,root=root,support_family=support_family);write(out/'body.json.gz',body)
        write(out/'interface-contract.json',body['compact_drive_contract'])
        report=evaluate(body,root=root);write(out/'geometry.json',report)
        result.update(execution='completed',candidate_id=body['candidate_id'],body_evaluation_id=body['evaluation_id'],geometry_evaluation_id=report['evaluation_id'],nominal_mass_kg=body['nominal_part_mass_kg'],direct_parts_process_usd=body['direct_parts_process_usd'],nominal_findings=len(report['nominal_findings']),continuous_interface_holds=len(report['continuous_and_interface_holds']),geometry_screen=report['geometry_screen'],known_geometry_screen_pass=report['known_geometry_screen_pass'])
    except Exception as exc:
        result.update(failure_type=type(exc).__name__,failure_reason=str(exc),traceback=traceback.format_exc())
    u=resource.getrusage(resource.RUSAGE_SELF);result.update(source_before=before,source_after=sources(root),source_unchanged=before==sources(root),wall_s=time.monotonic()-started,usage=dict(user_s=u.ru_utime,system_s=u.ru_stime,peak_rss_kib=u.ru_maxrss),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip())
    result['evaluation_id']=identity(result);write(out/'result.json',result)
    return result


def campaign(output,*,root=ROOT):
    root=Path(root);out=Path(output).resolve();out.mkdir(parents=True,exist_ok=False)
    changed=subprocess.check_output(['git','diff','--name-only','HEAD','--','engineering/compact_drive','tests/test_compact_drive.py'],cwd=root,text=True).strip()
    untracked=subprocess.check_output(['git','ls-files','--others','--exclude-standard','engineering/compact_drive','tests/test_compact_drive.py'],cwd=root,text=True).strip()
    if changed or untracked:raise ValueError('Freeze andcommit compactsource before trials')
    p=policy(root);configurations=p['configs'];assert len(configurations)==3
    before=sources(root);write(out/'request.json',dict(schema='osr-compact-drive-campaign-request/1',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),source_sha256=before,limits=p['limits'],source_isolation='IsolatedGit worktree and integrityhashes; noOSsource read-onlysandbox claimed',native_jobs=0,**FLAGS))
    records=[]
    for c in configurations:
        target=out/c['id'];cmd=[sys.executable,'-m','engineering.compact_drive.run','--trial',c['id'],'--output',str(target)]
        def limits():
            resource.setrlimit(resource.RLIMIT_CPU,(60,62));resource.setrlimit(resource.RLIMIT_AS,(1024**3,1024**3));resource.setrlimit(resource.RLIMIT_CORE,(0,0))
        with (out/(c['id']+'.stdout.log')).open('wb') as stdout,(out/(c['id']+'.stderr.log')).open('wb') as stderr:
            try:r=subprocess.run(cmd,cwd=root,stdout=stdout,stderr=stderr,timeout=90,preexec_fn=limits,env={**os.environ,'OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1','MKL_NUM_THREADS':'1'})
            except subprocess.TimeoutExpired:r=None
        if (target/'result.json').exists():record=read(target/'result.json')
        else:
            record=dict(config_id=c['id'],execution='interrupted',exit_code=None if r is None else r.returncode,reason='CPU/memory/wall budget or worker failure; original logs retained',**FLAGS);record['evaluation_id']=identity(record);write(out/(c['id']+'-interrupted.json'),record)
        records.append(record)
    final=dict(schema='osr-compact-drive-campaign/1',source_before=before,source_after=sources(root),source_unchanged=before==sources(root),trials=records,native_jobs=0,**FLAGS)
    final['evaluation_id']=identity(final);write(out/'summary.json',final);write(out/'manifest.json',dict(evaluation_id=final['evaluation_id'],files_sha256={f.relative_to(out).as_posix():digest(f) for f in sorted(out.rglob('*')) if f.is_file()},**FLAGS));return final


if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--output',required=True,type=Path);a.add_argument('--trial');a.add_argument('--support-family',choices=sorted(SUPPORT_VARIANTS));args=a.parse_args()
    if args.support_family is not None and args.trial is None:a.error('--support-family requires --trial')
    r=trial(args.output,args.trial,support_family=args.support_family) if args.trial else campaign(args.output)
    print(json.dumps({k:r[k] for k in ('evaluation_id','execution','config_id') if k in r}))
