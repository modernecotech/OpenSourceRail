#!/usr/bin/env python3
"""Plan/run full-passage research cases and report actual coverage and ride data."""
from __future__ import annotations
import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import runpy
import sys
import time
for key in ('OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','OMP_NUM_THREADS'):os.environ[key]='1'
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT),str(ROOT/'design/component-catalogue/src')]
from osr_mech.engineering_definition import fingerprint,load_definition
from engineering.analysis.shared_service import case_matrix,coverage,ride_diagnostics
from engineering.civil_exploration.shared_demo import demonstration
from engineering.civil_exploration.spatial_demo import configuration
from engineering.civil_exploration.spatial_vehicle import run_spatial


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+'\n')


def source_hashes(api):
    return {**api['sources'](api['common_api']()),
        'engineering/analysis/shared_service.py':sha(ROOT/'engineering/analysis/shared_service.py'),
        str(Path(__file__).relative_to(ROOT)):sha(__file__)}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('task',choices=['plan','run','verify']);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--model',type=Path);p.add_argument('--config',type=Path)
    p.add_argument('--speeds',default='10,15,20');p.add_argument('--resonance-band',help='min:max:step in m/s')
    p.add_argument('--cases',default='empty-15mps',help='comma-separated exact plan IDs, or all')
    p.add_argument('--dt',type=float,default=.005);p.add_argument('--mesh',type=int,default=2);p.add_argument('--rail-step',type=float,default=2.)
    p.add_argument('--wall-seconds',type=int,default=1800)
    a=p.parse_args();api=runpy.run_path(str(ROOT/'tools/automation/shared-engineering-campaign.py'))
    sources=source_hashes(api);environment=api['common_api']()['solver_environment']();output=a.output.resolve()
    if a.task=='verify':
        receipt=json.loads((output/'receipt.json').read_text())
        if receipt['sources_sha256']!=sources or receipt['solver_environment']!=environment:raise ValueError('service campaign source/environment changed')
        for relative,digest in receipt['outputs_sha256'].items():
            path=(output/relative).resolve()
            if not path.is_relative_to(output) or not path.is_file() or sha(path)!=digest:raise ValueError('service output changed: '+relative)
        load_definition(output/'definition.json')
        print(json.dumps(dict(verified=True,engineering_released=False)));return 0
    if output.exists():raise ValueError('use a fresh service evidence directory')
    if not 30<=a.wall_seconds<=14400:raise ValueError('service wall budget outside bounds')
    if bool(a.model)!=bool(a.config):raise ValueError('a supplied model and its spatial configuration must be supplied together')
    model=load_definition(a.model) if a.model else demonstration()
    cfg=json.loads(a.config.read_text()) if a.config else configuration(model)
    speeds=tuple(map(float,a.speeds.split(',')))
    band=tuple(map(float,a.resonance_band.split(':'))) if a.resonance_band else None
    if band is not None and len(band)!=3:raise ValueError('resonance band requires min:max:step')
    matrix=case_matrix(model,cfg,speeds,band);wanted={r['id'] for r in matrix['cases']} if a.cases=='all' else set(a.cases.split(','))
    if wanted-{r['id'] for r in matrix['cases']}:raise ValueError('requested service case not present in the plan')
    output.mkdir(parents=True);write(output/'definition.json',model);write(output/'case-matrix.json',matrix)
    started=time.monotonic();summaries=[];failed=False;budget_exhausted=False
    if a.task=='run':
        for case in matrix['cases']:
            if case['id'] not in wanted:continue
            if time.monotonic()-started>a.wall_seconds:budget_exhausted=True;break
            folder=output/case['id'];write(folder/'configuration.json',case['configuration']);write(folder/'plan.json',case['passage_plan'])
            try:
                duration=case['passage_plan']['duration_s']
                with (folder/'history.jsonl.gz').open('wb') as raw, gzip.GzipFile(filename='',fileobj=raw,mode='wb',mtime=0) as stream:
                    def retained(sample):
                        stream.write((json.dumps(sample,separators=(',',':'),allow_nan=False)+'\n').encode())
                        if time.monotonic()-started>a.wall_seconds:raise TimeoutError('service wall budget exhausted; converged samples retained')
                    r=run_spatial(model,case['configuration'],dt=a.dt,duration_s=duration,deck_mesh=a.mesh,rail_step=a.rail_step,sample_callback=retained)
                covered=coverage(r,case['passage_plan']);ride=ride_diagnostics(r)
                r.pop('history')
                write(folder/'dynamics.json',r);write(folder/'coverage.json',covered);write(folder/'ride.json',ride)
                row=dict(case=case['id'],kind=case['kind'],status='completed',duration_s=duration,steps=r['steps'],
                    complete_passage=covered['complete_passage'],full_family_represented=covered['full_family_represented'],
                    within_adapter_domain=r['within_adapter_domain'],domain_exceedances=r['domain_exceedances'],
                    minimum_contact_n=r['minimum_wheel_contact_n'],maximum_contact_n=r['maximum_wheel_contact_n'],
                    peak_carbody_acceleration_m_s2=r['peak_total_carbody_acceleration_m_s2'],ride=ride,
                    force_history_sha256=sha(folder/'history.jsonl.gz'),physical_validation=False,engineering_released=False)
                if not r['within_adapter_domain']:failed=True
            except (ValueError,RuntimeError,TimeoutError) as error:
                if isinstance(error,TimeoutError):budget_exhausted=True
                failed=True;row=dict(case=case['id'],kind=case['kind'],status='failed',error=str(error),
                    complete_passage=False,physical_validation=False,engineering_released=False)
                write(folder/'failure.json',row)
            summaries.append(row);print(json.dumps({k:v for k,v in row.items() if k!='ride'}),flush=True)
    executed={r['case'] for r in summaries};missing=[r['id'] for r in matrix['cases'] if r['id'] not in executed]
    report=dict(schema='osr-service-envelope-campaign/1',hardware_definition_sha256=fingerprint(model),
        task=a.task,cases=summaries,unexecuted_case_ids=missing,all_planned_cases_executed=not missing,
        budgets=dict(time_step_s=a.dt,deck_mesh=a.mesh,rail_step_m=a.rail_step,wall_seconds=a.wall_seconds),
        budget_exhausted=budget_exhausted,elapsed_s=time.monotonic()-started,
        numerical_time_and_mesh_confirmation_performed=False,iso_comfort_evaluated=False,
        physical_validation=False,engineering_released=False,
        open_gates=['complete family and supplier installation data','independent passage timestep/mesh refinement',
            'unexecuted matrix cases and fine resonance coverage','controlled ISO ride weighting and actual seat transfer',
            'geometry-specific force limits, material resistance and physical holdouts'])
    write(output/'summary.json',report)
    if source_hashes(api)!=sources:raise ValueError('service implementation changed during campaign; outputs retained')
    outputs={p.relative_to(output).as_posix():sha(p) for p in sorted(output.rglob('*')) if p.is_file()}
    write(output/'receipt.json',dict(schema='osr-service-envelope-receipt/1',sources_sha256=sources,solver_environment=environment,
        outputs_sha256=outputs,physical_validation=False,engineering_released=False))
    return 2 if failed or budget_exhausted else 0


if __name__=='__main__':raise SystemExit(main())
