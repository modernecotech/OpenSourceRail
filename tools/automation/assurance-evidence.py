#!/usr/bin/env python3
"""Execute declared Kani evidence and verify independently signed acceptance bundles.

Reports record actual executions, including timeouts. Local exports are not trusted
runner attestations. Acceptance requires a separately maintained public-key policy.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import tempfile
import time
import tomllib

ROOT=Path(__file__).resolve().parents[2]

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def declared():
    rows=[]
    for path in sorted((ROOT/'docs/safety-case/gsn').glob('*.toml')):
        for solution in tomllib.loads(path.read_text()).get('solution',[]):
            evidence=solution['evidence']
            if evidence['kind']=='kani':rows.append(dict(solution=solution['id'],**evidence))
    return rows


def scope():
    # Include untracked source too: a local source file must not silently escape scope.
    names=subprocess.check_output(['git','ls-files','-z','--cached','--others','--exclude-standard'],cwd=ROOT).decode().split('\0')
    selected={p for p in names if p and (p.endswith('.rs') or Path(p).name in {'Cargo.toml','Cargo.lock','rust-toolchain.toml','rust-toolchain'} or p.startswith('.cargo/') or p.startswith('docs/safety-case/gsn/'))}
    selected.update({'tools/automation/assurance-evidence.py','.github/workflows/kani.yml'})
    return {p:sha(ROOT/p) for p in sorted(selected) if (ROOT/p).is_file()}


def toml(records):
    lines=['schema = "osr-evidence-results/1"','']
    for row in records:
        lines+=['[[result]]']
        for key,value in row.items():
            if key!='inputs':lines.append(key+' = '+json.dumps(value))
        lines+=['[result.inputs]']
        lines += [json.dumps(k)+' = '+json.dumps(v) for k,v in row['inputs'].items()]
        lines.append('')
    return '\n'.join(lines)


def execute(output,seconds,selected=None,package=None):
    output=output.resolve()
    if not output.is_relative_to(ROOT):raise ValueError('Evidence must be within the repository evidence root')
    output.mkdir(parents=True,exist_ok=True)
    inputs=scope();records=[]
    version=subprocess.check_output(['cargo-kani','--version'],text=True).strip()
    if version!='cargo-kani 0.67.0':raise ValueError('Use the reviewed Kani 0.67.0 toolchain')
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    runner=('github:'+os.environ['GITHUB_REPOSITORY']+'/actions/runs/'+os.environ['GITHUB_RUN_ID']) if os.environ.get('GITHUB_ACTIONS')=='true' else 'local-unattested'
    chosen=[row for row in declared() if (not selected or row['solution'] in selected) and (not package or row['path'].split('/')[1]==package)]
    if not chosen or selected and set(selected)-{r['solution'] for r in chosen}:raise ValueError('Unknown selected proof solution')
    for row in chosen:
        anchor=row['anchor'];source=ROOT/row['path']
        if 'fn '+anchor+'(' not in source.read_text():raise ValueError('Declared harness missing: '+anchor)
        command=['cargo','kani','-p',row['path'].split('/')[1],'--harness','kani_proofs::'+anchor,'--exact']
        path=output/(row['solution']+'.log');started=time.monotonic()
        with path.open('w') as stream:
            stream.write(json.dumps(dict(command=command,tool_version=version,source_commit=commit,timeout_seconds=seconds))+'\n');stream.flush()
            proc=subprocess.Popen(command,cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT,start_new_session=True)
            try:code=proc.wait(timeout=seconds)
            except subprocess.TimeoutExpired:
                os.killpg(proc.pid,signal.SIGTERM)
                try:proc.wait(timeout=5)
                except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGKILL);proc.wait()
                code=124;stream.write('\nRunner timeout; proof not established.\n')
        success=code==0 and any(line.strip() in {'VERIFICATION:- SUCCESSFUL','VERIFICATION: SUCCESSFUL'} for line in path.read_text().splitlines())
        if scope()!=inputs:raise ValueError('Source inputs changed during proof execution; discard this run')
        record=dict(solution=row['solution'],kind='kani',path=row['path'],anchor=anchor,tool='cargo-kani',tool_version=version,
            bounds='Exact harness; unwind/assumptions are those in hashed source. Command: '+json.dumps(command)+'; timeout_seconds='+str(seconds)+'; dependency_scope=workspace Rust/manifests/lockfiles/GSN and runner/workflow; external dependencies pinned by Cargo.lock; toolchain/supply-chain review remains independent.',
            executed_by=runner,status='passed' if success else 'failed',exit_code=code,report=path.relative_to(ROOT).as_posix(),report_sha256=sha(path),inputs=inputs)
        records.append(record)
        (output/'results.toml').write_text(toml(records))
        print(row['solution'],record['status'],'exit',code,'seconds',round(time.monotonic()-started,1),flush=True)
    manifest=dict(schema='osr-controlled-execution/1',commit=commit,runner=runner,results_sha256=sha(output/'results.toml'),
        inputs=inputs,passed=all(r['status']=='passed' for r in records),solutions=[r['solution'] for r in records],
        independently_accepted=False,runner_authenticated=False,runner_provenance_requires_external_verification=True)
    (output/'execution.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return manifest


def verify_acceptance(results,envelope,signature,policy):
    """Verify bytes with an authorized Ed25519 public key; never create acceptance."""
    data=json.loads(envelope.read_text());trusted=json.loads(policy.read_text())
    if data.get('schema')!='osr-independent-acceptance/1' or data.get('status')!='accepted':raise ValueError('Invalid acceptance envelope')
    reviewer=data.get('reviewer');identity=trusted.get('reviewers',{}).get(reviewer)
    if not identity or not identity.get('enabled') or not data.get('reference'):raise ValueError('Unknown/disabled reviewer or missing review reference')
    if data.get('results_sha256')!=sha(results):raise ValueError('Acceptance binds different result bytes')
    records=tomllib.loads(results.read_text()).get('result',[])
    if tomllib.loads(results.read_text()).get('schema')!='osr-evidence-results/1':raise ValueError('Unknown execution schema')
    if not records or any(r['executed_by']==reviewer for r in records):raise ValueError('Reviewer must be independent of every executing identity')
    if set(data.get('solutions',[]))!={r['solution'] for r in records}:raise ValueError('Acceptance solution scope differs')
    if data.get('dependency_scope_reviewed') is not True:raise ValueError('Dependency scope was not reviewed')
    key=(policy.parent/identity['public_key']).resolve()
    if not key.is_file() or sha(key)!=identity.get('public_key_sha256'):raise ValueError('Reviewer key changed')
    subprocess.run(['openssl','pkeyutl','-verify','-pubin','-inkey',str(key),'-rawin','-in',str(envelope),'-sigfile',str(signature)],check=True,capture_output=True)
    # Verify the recorded executions and all bytes independently of the signature.
    solutions={r['solution']:r for r in declared()}
    current_inputs=scope()
    if len({r['solution'] for r in records})!=len(records):raise ValueError('Duplicate execution records')
    for record in records:
        expected=solutions.get(record['solution'])
        if not expected or any(record.get(k)!=expected.get(k) for k in ['kind','path','anchor']):raise ValueError('Result does not match declared Kani evidence')
        if record.get('inputs')!=current_inputs:raise ValueError('Stale or incomplete dependency scope')
        if record['path'] not in record['inputs'] or record['report']==record['path'] or any(not record.get(k) for k in ['tool','tool_version','bounds','executed_by']):raise ValueError('Incomplete execution record')
        if record['status']!='passed' or record['exit_code']!=0:raise ValueError('Acceptance cannot cover failed execution')
        for path,digest in {**record['inputs'],record['report']:record['report_sha256']}.items():
            target=(ROOT/path).resolve()
            if not target.is_relative_to(ROOT) or not target.is_file() or sha(target)!=digest:raise ValueError('Stale or unsafe evidence input')
    return dict(reviewer=reviewer,reference=data['reference'],authenticated=True,solutions=sorted(data['solutions']),scope='Only the listed execution records; the complete safety case remains separate',physical_release=False)


def main():
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='action',required=True)
    run=sub.add_parser('run');run.add_argument('--output',type=Path,required=True);run.add_argument('--timeout',type=int,default=300);run.add_argument('--solution',action='append');run.add_argument('--package')
    verify=sub.add_parser('verify-acceptance')
    for name in ['results','envelope','signature','policy']:verify.add_argument('--'+name,type=Path,required=True)
    args=parser.parse_args()
    if args.action=='run':
        result=execute(args.output,args.timeout,args.solution,args.package)
        if not result['passed']:raise SystemExit(1)
    else:print(json.dumps(verify_acceptance(args.results,args.envelope,args.signature,args.policy)))
if __name__=='__main__':main()
