#!/usr/bin/env python3
"""Resumable, bounded city simulation runs; never promote physical acceptance."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[2]


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def source_inputs(design, scenario):
    names=subprocess.check_output(['git','ls-files','-z','--cached','--others','--exclude-standard'],cwd=ROOT).decode().split('\0')
    names={p for p in names if p and ((p.startswith('crates/') and p.endswith('.rs')) or Path(p).name in {'Cargo.toml','Cargo.lock','rust-toolchain.toml'} or p.startswith(('lib/templates/','design/city-generation/src/','design/component-catalogue/catalog/buildable-trainset/')))}
    names.update(str(p.relative_to(ROOT)) for p in [design,scenario,Path(__file__).resolve(),ROOT/'tools/automation/validate-city-simulation.py'])
    return {p:sha(ROOT/p) for p in sorted(names) if (ROOT/p).is_file()}


def reusable(folder, inputs, resilience, basis='canonical'):
    try:
        record=json.loads((folder/'execution.json').read_text())
        return record if record.get('scenario_basis','canonical')==basis and record['inputs']==inputs and record['resilience_required']==resilience and record['passed'] is True and record['report_sha256']==sha(folder/'validation.json') and json.loads((folder/'validation.json').read_text()).get('passed') is True else None
    except (OSError,ValueError,KeyError):return None


def run_city(city, design, output, timeout, resilience, resume, regenerate=False):
    scenario=design.parent/(city+'.toml');folder=output/city;folder.mkdir(parents=True,exist_ok=True)
    inputs=source_inputs(design,scenario)
    basis='generator-candidate' if regenerate else 'canonical'
    if resume and (cached:=reusable(folder,inputs,resilience,basis)):return cached
    tested_scenario=scenario
    if regenerate:
        sys.path.insert(0,str(ROOT/'design/city-generation/src'))
        from osr_scenario.generator import generate_from_path
        tested_scenario=folder/(city+'.toml')
        tested_scenario.write_text(generate_from_path(design))
        (folder/'design.toml').write_bytes(design.read_bytes())
    report=folder/'validation.json'
    if report.exists():report.unlink()  # Only this runner's previous generated report.
    command=[sys.executable,str(ROOT/'tools/automation/validate-city-simulation.py'),'--scenario',str(tested_scenario),'--output',str(report),'--full-only']
    if resilience:command.append('--resilience')
    started=time.monotonic()
    with (folder/'execution.log').open('w') as log:
        proc=subprocess.Popen(command,cwd=ROOT,env={**os.environ,'OSR_RESILIENCE_JOBS':'1'},stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
        try:code=proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid,signal.SIGTERM)
            try:proc.wait(timeout=5)
            except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGKILL);proc.wait()
            code=124
    result=json.loads(report.read_text()) if report.exists() else {}
    unchanged=inputs==source_inputs(design,scenario)
    record=dict(schema='osr-city-simulation-execution/1',city=city,commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        inputs=inputs,inputs_unchanged=unchanged,command=command,exit_code=code,elapsed_seconds=round(time.monotonic()-started,1),
        scenario_basis=basis,canonical_scenario_sha256=sha(scenario),tested_scenario_sha256=sha(tested_scenario),
        report_sha256=sha(report) if report.exists() else None,resilience_required=resilience,passed=code==0 and result.get('passed') is True and unchanged,
        physical_release=False,scope='Full-window software simulation of the recorded scenario basis; generated candidates do not promote canonical packages. Capacity, physical fit, site energy and independent operating acceptance remain separate')
    (folder/'execution.json').write_text(json.dumps(record,indent=2)+'\n')
    return record


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    select=parser.add_mutually_exclusive_group(required=True);select.add_argument('--all',action='store_true');select.add_argument('--city',action='append')
    parser.add_argument('--jobs',type=int,default=2);parser.add_argument('--timeout',type=int,default=1800)
    parser.add_argument('--nominal-only',action='store_true');parser.add_argument('--resume',action='store_true');parser.add_argument('--output',type=Path,default=ROOT/'build/city-validation/batch')
    parser.add_argument('--regenerate',action='store_true',help='Test generated scenario candidates in build/; leave canonical packages unchanged')
    args=parser.parse_args()
    if args.jobs<1 or args.jobs>8 or args.timeout<1:parser.error('Use 1–8 workers and a positive timeout')
    spec=importlib.util.spec_from_file_location('batch_cities',ROOT/'tools/automation/erpnext-city.py');cities=importlib.util.module_from_spec(spec);spec.loader.exec_module(cities)
    catalogue=cities.catalogue();selected=sorted(catalogue if args.all else set(args.city))
    if set(selected)-catalogue.keys():parser.error('Unknown city slug')
    output=args.output.resolve()
    if not output.is_relative_to(ROOT/'build'):parser.error('Output must be inside the generated build directory')
    output.mkdir(parents=True,exist_ok=True);records={}
    def save():
        report=dict(schema='osr-city-validation-batch/1',selected=selected,completed=len(records),passed=len(records)==len(selected) and all(r['passed'] for r in records.values()),physical_release=False,results=records)
        (output/'summary.json').write_text(json.dumps(report,indent=2)+'\n')
    save()
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        pending={pool.submit(run_city,c,catalogue[c][0],output,args.timeout,not args.nominal_only,args.resume,args.regenerate):c for c in selected}
        for future in as_completed(pending):
            city=pending[future]
            try:records[city]=future.result()
            except Exception as error:records[city]=dict(city=city,passed=False,error=str(error),physical_release=False)
            save();print(city,'PASS' if records[city]['passed'] else 'OPEN/FAILED',f'{len(records)}/{len(selected)}',flush=True)
    return 0 if all(r['passed'] for r in records.values()) else 1

if __name__=='__main__':raise SystemExit(main())
