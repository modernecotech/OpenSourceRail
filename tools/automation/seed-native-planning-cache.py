#!/usr/bin/env python3
"""Seed exact executable/input caches from verified historical CI run bytes."""
import argparse
from functools import lru_cache
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('planning_ci',ROOT/'tools/automation/city-planning-ci.py')
ci=importlib.util.module_from_spec(spec);spec.loader.exec_module(ci)


def sha(raw):return hashlib.sha256(raw).hexdigest()


def checked_cases(folder,record,report):
    if (record.get('schema')!='osr-city-planning-ci/1' or record.get('passed') is not True
            or record.get('exit_code')!=0 or record.get('inputs_unchanged') is not True
            or record.get('report_sha256')!=sha((folder/'validation.json').read_bytes())
            or report.get('passed') is not True or report.get('resilience_passed') is not True
            or report.get('resilience_required') is not True
            or report.get('trainset_contract',{}).get('passed') is not True):
        raise ValueError('Unsuccessful historical planning execution')
    runs=report.get('runs',[]);cases=report.get('resilience_cases',[])
    if (len(runs)!=2 or runs[-1].get('duration_s')!=90000 or len(cases)!=8
            or len({case['label'] for case in cases})!=8):
        raise ValueError('Incomplete historical native cases')
    results=[]
    for case in runs+cases:
        receipt=case['execution_receipt'];inputs=receipt['inputs']
        key=sha(json.dumps(inputs,sort_keys=True).encode());source=folder/'native-runs'/(key+'.json')
        if (receipt.get('cache_key')!=key or inputs.get('simulator_sha256')!=report['simulator_sha256']
                or inputs.get('duration_s')!=case['duration_s'] or inputs.get('compact_json') is not True
                or inputs.get('ma_check_every')!=0 or sha(source.read_bytes())!=receipt['output_sha256']):
            raise ValueError('Historical native output differs from receipt')
        if case in cases and (case.get('passed') is not True or case['duration_s']!=90000):
            raise ValueError('Failed historical degraded case')
        if case in runs and inputs['scenario_sha256']!=report['scenario_sha256']:
            raise ValueError('Historical nominal scenario differs')
        results.append((key,source,receipt))
    return results


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input',type=Path,required=True);parser.add_argument('--commit',required=True)
    parser.add_argument('--run',type=int);parser.add_argument('--partition',type=int)
    args=parser.parse_args()
    commit=subprocess.check_output(['git','rev-parse',args.commit+'^{commit}'],cwd=ROOT,text=True).strip()
    if args.run is not None:
        if args.run<1 or args.partition is None or not 0<=args.partition<64:
            raise ValueError('Historical CI run/partition invalid')
        run=json.loads(subprocess.check_output(['gh','run','view',str(args.run),'--json','headSha,status,conclusion,workflowName'],cwd=ROOT,text=True))
        if (run.get('headSha')!=commit or run.get('status')!='completed'
                or run.get('conclusion') not in {'success','failure'} or run.get('workflowName')!='city-planning'):
            raise ValueError('Historical CI run is not the completed requested source revision')
        subprocess.run(['gh','run','download',str(args.run),'--name',f'city-planning-{args.partition}',
                        '--dir',str(args.input)],cwd=ROOT,check=True)
    catalogue=ci.designs();cache=ROOT/'.cache/osr-pipeline/native-runs';simulator=sha((ROOT/'target/release/osr-sim').read_bytes())
    names=subprocess.check_output(['git','ls-tree','-r','--name-only',commit],cwd=ROOT,text=True).splitlines()
    historical_sources={p for p in names if ((p.startswith('crates/') and p.endswith('.rs'))
        or Path(p).name in {'Cargo.toml','Cargo.lock','rust-toolchain.toml'}
        or p.startswith(('lib/templates/','design/city-generation/src/','design/component-catalogue/catalog/buildable-trainset/')))}
    historical_sources.update({'tools/automation/validate-city-batch.py','tools/automation/validate-city-simulation.py',
        'tools/automation/validate-city-service.py','tools/automation/city-planning-ci.py','.github/workflows/city-planning.yml'})
    if 'tools/automation/seed-native-planning-cache.py' in names:historical_sources.add('tools/automation/seed-native-planning-cache.py')
    @lru_cache(maxsize=None)
    def frozen_sha(relative):
        if Path(relative).is_absolute() or '..' in Path(relative).parts:raise ValueError('Unsafe historical source path')
        return sha(subprocess.check_output(['git','show',commit+':'+relative],cwd=ROOT))
    checked=[]
    for execution in args.input.rglob('execution.json'):
        folder=execution.parent;record=json.loads(execution.read_text())
        if record.get('passed') is not True:
            print('No reusable successful execution:',record.get('city'));continue
        report=json.loads((folder/'validation.json').read_text())
        slug=record['city'];design=catalogue[slug]
        if record.get('commit')!=commit or folder.name!=slug:raise ValueError('Historical source revision differs')
        # Source paths remain complete, including editor and workflow sources.
        # Validate their old bytes against Git; never retag an execution record.
        expected=historical_sources|{design.relative_to(ROOT).as_posix(),(design.parent/(slug+'.toml')).relative_to(ROOT).as_posix()}
        if set(record['inputs'])!=expected:raise ValueError('Historical source inventory differs')
        if any(frozen_sha(path)!=digest for path,digest in record['inputs'].items()):
            raise ValueError('Historical source receipt differs from immutable Git revision')
        if report['generator_sha256']!=frozen_sha('tools/automation/validate-city-simulation.py'):
            raise ValueError('Historical validation generator differs from its source snapshot')
        if report['design_sha256']!=sha(design.read_bytes()) or report['scenario_sha256']!=sha((design.parent/(slug+'.toml')).read_bytes()):
            raise ValueError('Historical city input differs from current inventory')
        for key,source,receipt in checked_cases(folder,record,report):
            # A changed executable gets an actual rerun through the normal
            # validator. Matching caches retain their original output hashes.
            if receipt['inputs']['simulator_sha256']==simulator:
                # Preserve all original runtime inputs/checksums and expose
                # the historical execution provenance in the reused receipt.
                receipt={**receipt,'cache_origin':receipt.get('cache_origin',dict(
                    source_commit=commit,ci_run=args.run,city=slug,
                    execution_sha256=sha(execution.read_bytes()),report_sha256=record['report_sha256']))}
                checked.append((key,source,receipt))
    cache.mkdir(parents=True,exist_ok=True)
    for key,source,receipt in checked:
        shutil.copyfile(source,cache/(key+'.json'))
        (cache/(key+'.receipt.json')).write_text(json.dumps(receipt,sort_keys=True)+'\n')
    print('Seeded',len(checked),'verified exact-executable historical outputs; current source-bound validation still required')


if __name__=='__main__':main()
