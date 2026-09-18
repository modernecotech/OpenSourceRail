#!/usr/bin/env python3
"""Verify complete, current catalogue CI artifacts without granting operating release."""
import argparse
import importlib.util
import json
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[2]


def module(name,path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path)
    result=importlib.util.module_from_spec(spec);spec.loader.exec_module(result);return result


batch=module('collection_batch','tools/automation/validate-city-batch.py')


def collect(folder,catalogue,commit,basis='generator-candidate',resilience=False):
    folder=folder.resolve();seen=set();rows={};errors=[]
    for path in sorted(folder.rglob('execution.json')):
        try:
            if not path.resolve().is_relative_to(folder):raise ValueError('Artifact escapes collection root')
            record=json.loads(path.read_text());city=record['city']
            if city not in catalogue or city!=path.parent.name:raise ValueError('Unknown/misplaced city record')
            if city in seen:raise ValueError('Duplicate city record: '+city)
            seen.add(city)
            design=catalogue[city][0];canonical=design.parent/(city+'.toml')
            for name in ['validation.json',*([city+'.toml','design.toml'] if basis=='generator-candidate' else [])]:
                if not (path.parent/name).resolve().is_relative_to(folder):raise ValueError('Artifact escapes collection root')
            current=batch.source_inputs(design,canonical)
            if record.get('schema')!='osr-city-simulation-execution/1' or record.get('commit')!=commit:
                raise ValueError('Wrong execution schema or commit: '+city)
            if record.get('exit_code')!=0 or record.get('inputs_unchanged') is not True:
                raise ValueError('Failed execution or changed inputs: '+city)
            if batch.reusable(path.parent,current,resilience,basis) is None:
                raise ValueError('Failed, stale or altered evidence: '+city)
            report=json.loads((path.parent/'validation.json').read_text())
            scenario=path.parent/(city+'.toml') if basis=='generator-candidate' else canonical
            if (record.get('canonical_scenario_sha256')!=batch.sha(canonical) or
                    record.get('tested_scenario_sha256')!=batch.sha(scenario) or
                    record.get('design_sha256')!=batch.sha(design) or
                    report.get('scenario_sha256')!=batch.sha(scenario) or
                    report.get('design_sha256')!=batch.sha(design)):
                raise ValueError('Scenario/design provenance differs: '+city)
            if (report.get('trainset_contract',{}).get('passed') is not True or
                    not report.get('runs') or any(r.get('duration_s',0)<90000 for r in report['runs']) or
                    report.get('resilience_required') is not resilience or
                    (resilience and report.get('resilience_passed') is not True)):
                raise ValueError('Incomplete full-window acceptance: '+city)
            rows[city]=dict(passed=True,report_sha256=record['report_sha256'],
                execution_artifact=path.relative_to(folder).as_posix(),elapsed_seconds=record.get('elapsed_seconds'))
        except (OSError,ValueError,KeyError,TypeError,AttributeError) as error:
            errors.append(dict(artifact=path.relative_to(folder).as_posix(),error=str(error)))
    missing=sorted(set(catalogue)-seen)
    return dict(schema='osr-catalogue-ci-acceptance/1',commit=commit,scenario_basis=basis,
        resilience_required=resilience,selected=len(catalogue),completed=len(seen),passed_cities=len(rows),
        passed=not errors and not missing and len(rows)==len(catalogue),missing=missing,errors=errors,results=rows,
        physical_release=False,operating_release=False,
        scope='Recorded full-window software scenarios only; canonical promotion and independent physical/operating acceptance remain separate')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--basis',choices=['canonical','generator-candidate'],default='generator-candidate')
    p.add_argument('--resilience',action='store_true');args=p.parse_args()
    cities=module('collection_cities','tools/automation/erpnext-city.py').catalogue()
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    result=collect(args.input,cities,commit,args.basis,args.resilience)
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(f"{result['passed_cities']}/{result['selected']} city artifacts passed; {len(result['errors'])} errors; {len(result['missing'])} missing")
    return 0 if result['passed'] else 1


if __name__=='__main__':raise SystemExit(main())
