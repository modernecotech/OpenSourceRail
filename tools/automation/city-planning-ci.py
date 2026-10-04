#!/usr/bin/env python3
"""Run and import source-bound native planning screens from partitioned CI."""
from concurrent.futures import ThreadPoolExecutor, as_completed
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
import tomllib

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('planning_batch',ROOT/'tools/automation/validate-city-batch.py')
batch=importlib.util.module_from_spec(spec);spec.loader.exec_module(batch)
SCHEMA='osr-city-planning-ci/1'


def designs():
    return {tomllib.loads(p.read_text())['city']['slug']:p for p in (ROOT/'cities/catalogue').glob('*/*/*/design.toml')}


def inputs(design):
    result=batch.source_inputs(design,design.parent/(tomllib.loads(design.read_text())['city']['slug']+'.toml'))
    for p in [Path(__file__).resolve(),ROOT/'.github/workflows/city-planning.yml']:
        result[p.relative_to(ROOT).as_posix()]=batch.sha(p)
    return result


def verify(folder,design,commit):
    """Reject stale inputs, incomplete cases, mixed builds and changed outputs."""
    record=json.loads((folder/'execution.json').read_text())
    report_path=folder/'validation.json';report=json.loads(report_path.read_text())
    slug=tomllib.loads(design.read_text())['city']['slug']
    if (record.get('schema')!=SCHEMA or record.get('city')!=slug or record.get('commit')!=commit
            or record.get('exit_code')!=0 or record.get('inputs_unchanged') is not True
            or record.get('passed') is not True or record.get('inputs')!=inputs(design)):
        raise ValueError('Failed or stale CI execution: '+slug)
    if (record.get('report_sha256')!=batch.sha(report_path) or report.get('passed') is not True
            or report.get('design_sha256')!=batch.sha(design)
            or report.get('scenario_sha256')!=batch.sha(design.parent/(slug+'.toml'))
            or report.get('generator_sha256')!=batch.sha(ROOT/'tools/automation/validate-city-simulation.py')
            or report.get('trainset_contract',{}).get('passed') is not True
            or report.get('resilience_required') is not True or report.get('resilience_passed') is not True):
        raise ValueError('Failed or altered planning report: '+slug)
    runs=report.get('runs',[]);cases=report.get('resilience_cases',[])
    if len(runs)!=2 or runs[-1].get('duration_s')!=90000 or len(cases)!=8:
        raise ValueError('Incomplete full-day planning screens: '+slug)
    if len({c['label'] for c in cases})!=8:
        raise ValueError('Duplicate degraded case: '+slug)
    for case in runs+cases:
        receipt=case['execution_receipt'];case_inputs=receipt['inputs']
        key=hashlib.sha256(json.dumps(case_inputs,sort_keys=True).encode()).hexdigest()
        raw=folder/'native-runs'/(key+'.json')
        if (receipt.get('cache_key')!=key or case_inputs.get('simulator_sha256')!=report['simulator_sha256']
                or case_inputs.get('duration_s')!=case['duration_s'] or not case_inputs.get('compact_json')
                or case_inputs.get('ma_check_every')!=0 or batch.sha(raw)!=receipt['output_sha256']):
            raise ValueError('Native output differs from its execution receipt: '+slug)
        if case in cases and (case.get('duration_s')!=90000 or case.get('passed') is not True):
            raise ValueError('Failed degraded screen: '+slug)
        if case in runs and case_inputs.get('scenario_sha256')!=report['scenario_sha256']:
            raise ValueError('Nominal run used another scenario: '+slug)
    return record,report


def run_city(slug,design,output,timeout):
    folder=output/slug;folder.mkdir(parents=True,exist_ok=True)
    source_inputs=inputs(design)
    command=[sys.executable,str(ROOT/'tools/automation/validate-city-simulation.py'),
             '--scenario',str(design.parent/(slug+'.toml')),'--output',str(folder/'validation.json'),'--resilience']
    started=time.monotonic()
    with (folder/'execution.log').open('w') as log:
        process=subprocess.Popen(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
        try:code=process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid,signal.SIGTERM)
            try:process.wait(timeout=5)
            except subprocess.TimeoutExpired:os.killpg(process.pid,signal.SIGKILL);process.wait()
            code=124
    report=json.loads((folder/'validation.json').read_text()) if (folder/'validation.json').exists() else {}
    record=dict(schema=SCHEMA,city=slug,commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                inputs=source_inputs,inputs_unchanged=source_inputs==inputs(design),exit_code=code,
                report_sha256=batch.sha(folder/'validation.json') if report else None,
                passed=code==0 and report.get('passed') is True and source_inputs==inputs(design),
                elapsed_seconds=round(time.monotonic()-started,3),physical_release=False,operating_release=False,
                scope='Native full-day aggregate planning and degraded software screens; depot launch and per-line operating qualification remain separate.')
    for case in report.get('runs',[])+report.get('resilience_cases',[]):
        key=case['execution_receipt']['cache_key'];destination=folder/'native-runs';destination.mkdir(exist_ok=True)
        (destination/(key+'.json')).write_bytes((ROOT/'.cache/osr-pipeline/native-runs'/(key+'.json')).read_bytes())
    (folder/'execution.json').write_text(json.dumps(record,indent=2)+'\n')
    return record


def main():
    p=argparse.ArgumentParser(description=__doc__);commands=p.add_subparsers(dest='command',required=True)
    run=commands.add_parser('run');run.add_argument('--partition',required=True);run.add_argument('--jobs',type=int,default=2)
    run.add_argument('--timeout',type=int,default=5400);run.add_argument('--cities',default='')
    run.add_argument('--output',type=Path,default=ROOT/'build/city-planning/partition')
    receive=commands.add_parser('import');receive.add_argument('--input',type=Path,required=True)
    receive.add_argument('--commit',required=True);receive.add_argument('--cities',default='')
    args=p.parse_args();catalogue=designs();selected=set(args.cities.split(',')) if args.cities else set(catalogue)
    if selected-catalogue.keys():p.error('Unknown city')
    if args.command=='run':
        if not 1<=args.jobs<=8 or args.timeout<1:p.error('Invalid worker count or timeout')
        selected=batch.partition(selected,args.partition);args.output.mkdir(parents=True,exist_ok=True);results={}
        with ThreadPoolExecutor(max_workers=args.jobs) as pool:
            futures={pool.submit(run_city,s,catalogue[s],args.output,args.timeout):s for s in selected}
            for future in as_completed(futures):
                s=futures[future]
                try:results[s]=future.result()
                except Exception as e:results[s]=dict(city=s,passed=False,error=str(e))
                print(s,'PASS' if results[s]['passed'] else 'FAILED',flush=True)
                (args.output/'summary.json').write_text(json.dumps(dict(results=results,passed=all(r['passed'] for r in results.values())),indent=2)+'\n')
        return int(not all(r['passed'] for r in results.values()))
    found={};validated={}
    for f in args.input.rglob('execution.json'):
        record=json.loads(f.read_text());slug=record['city']
        if slug not in selected:continue
        if slug in found or f.parent.name!=slug:raise ValueError('Duplicate or misplaced CI record: '+slug)
        if not f.resolve().is_relative_to(args.input.resolve()):raise ValueError('Artifact escapes input directory')
        found[slug]=f.parent;validated[slug]=verify(f.parent,catalogue[slug],args.commit)
    if set(found)!=selected:raise ValueError('Missing CI cities: '+', '.join(sorted(selected-set(found))))
    # Validate the complete selection before changing any canonical evidence.
    for slug,(record,report) in sorted(validated.items()):
        dest=catalogue[slug].parent/'engineering/simulation';dest.mkdir(parents=True,exist_ok=True)
        (dest/'validation-summary.json').write_bytes((found[slug]/'validation.json').read_bytes())
        (dest/'ci-execution.json').write_text(json.dumps(record,indent=2)+'\n')
    print('Imported',len(validated),'actual source-bound CI planning reports; releases remain open')
    return 0

if __name__=='__main__':raise SystemExit(main())
