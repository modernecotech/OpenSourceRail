#!/usr/bin/env python3
"""Reproduce a native CAD/solver change, then exercise its native ERP consequences."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import uuid

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('change_workflow',ROOT/'engineering/changes/workflow.py')
w=importlib.util.module_from_spec(spec);spec.loader.exec_module(w)


def prepare(profile,output):
    profile=profile.resolve()
    if not profile.is_relative_to(ROOT):raise ValueError('Configuration must be retained inside the repository')
    config=json.loads((ROOT/'engineering/changes/config/generic.json').read_text())
    config.update(json.loads(profile.read_text()));w.validate_config(ROOT,config)
    output=output.resolve();output.mkdir(parents=True,exist_ok=False)
    # FreeCADCmd can return zero after a script exception: require its complete
    # result files and validate them before creating the bundle manifest.
    wrapper=output/'run-freecad.py'
    wrapper.write_text('import runpy\nfrom pathlib import Path\n'
        'folder = Path(__file__).resolve().parent\n'
        'root = next(p for p in folder.parents if (p / "engineering/changes/freecad_change.py").is_file())\n'
        'module = runpy.run_path(str(root / "engineering/changes/freecad_change.py"))\n'
        'module["main"](' + repr(config) + ', str(folder))\n')
    binary=shutil.which('FreeCADCmd') or shutil.which('freecadcmd')
    args=[binary,str(wrapper)] if binary else ['flatpak','run','--filesystem='+str(ROOT),'--filesystem='+str(output),'--command=FreeCADCmd','org.freecad.FreeCAD',str(wrapper)]
    with (output/'freecad.log').open('w') as log:subprocess.run(args,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=600)
    manifest=w.seal(ROOT,output,config,['engineering/changes/config/generic.json',profile.relative_to(ROOT).as_posix()]);w.verify(ROOT,output)
    print(json.dumps(dict(bundle=str(output),sha256=manifest['sha256'],maturity='screening',erp_executed=False)))


def execute(args):
    folder=args.bundle.resolve();manifest=w.verify(ROOT,folder)
    if args.report.exists():raise ValueError('Use a new report path; previous native results must remain inspectable')
    if args.report.resolve().is_relative_to(folder):raise ValueError('Native report must be outside the sealed bundle')
    config=json.loads((folder/'resolved-config.json').read_text());cad=json.loads((folder/'cad-results.json').read_text())
    payload=dict(site=args.site,reference_project=args.reference_project,run=uuid.uuid4().hex[:12],
        city=manifest['city'],asset_id=manifest['asset_id'],component=manifest['component'],manifest_sha256=manifest['sha256'],
        purchase_allowance=config['purchase_allowance'],quantities={name:cad[name] for name in ['baseline','candidate']},
        cad_sha256=dict(baseline=cad['source_sha256'],candidate=cad['candidate_sha256']))
    script=ROOT/'engineering/changes/erp_change.py';source_hash=w.sha(script)
    docker=shutil.which('docker') or str(Path.home()/'bin/docker')
    command=[docker,'compose','-p',args.compose_project,'-f',str(args.compose_file.resolve()),'exec','-T','backend','env/bin/python','-']
    result=subprocess.run(command,input='INPUT = '+repr(payload)+'\n'+script.read_text(),text=True,capture_output=True,cwd=ROOT,timeout=300)
    private=ROOT/'var/engineering-change';private.mkdir(parents=True,exist_ok=True,mode=0o700)
    log=private/(payload['run']+'.log');log.write_text(result.stdout+result.stderr);log.chmod(0o600)
    if result.returncode:raise RuntimeError('Native ERP change failed; inspect '+str(log))
    records=[line.removeprefix('OSR_CHANGE_RESULT:') for line in result.stdout.splitlines() if line.startswith('OSR_CHANGE_RESULT:')]
    if len(records)!=1:raise ValueError('Missing native ERP result; inspect private log before retrying')
    report=json.loads(records[0]);w.verify(ROOT,folder)
    if source_hash!=w.sha(script):raise ValueError('Native runner changed during execution')
    report.update(checkout_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        working_tree_dirty=bool(subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True).strip()),
        source_sha256={'engineering/changes/erp_change.py':source_hash,'tools/automation/engineering-change.py':w.sha(Path(__file__))})
    args.report.parent.mkdir(parents=True,exist_ok=True);w.write(args.report,report)
    print(json.dumps(dict(passed=report['passed'],checks=len(report['checks']),project=report['project'],report=str(args.report),engineering_acceptance=False)))


def main():
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='action',required=True)
    p=sub.add_parser('prepare');p.add_argument('--profile',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p=sub.add_parser('verify');p.add_argument('bundle',type=Path)
    p=sub.add_parser('execute');p.add_argument('bundle',type=Path);p.add_argument('--reference-project',required=True)
    p.add_argument('--compose-project',default='osr-example-erp');p.add_argument('--compose-file',type=Path,default=ROOT/'var/city-example/erp.json')
    p.add_argument('--site',default='osr-example.localhost');p.add_argument('--report',type=Path,required=True)
    args=parser.parse_args()
    if args.action=='prepare':prepare(args.profile,args.output)
    elif args.action=='verify':w.verify(ROOT,args.bundle.resolve());print('Current source and all bundle artifacts verified')
    else:execute(args)


if __name__=='__main__':main()
