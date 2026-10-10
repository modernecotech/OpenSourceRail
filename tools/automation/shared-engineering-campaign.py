#!/usr/bin/env python3
"""Run or verify retained spatial, joint, material, search and correlation work."""
from __future__ import annotations
import argparse
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import runpy
import sys
for key in ('OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','OMP_NUM_THREADS'):os.environ[key]='1'
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT),str(ROOT/'design/component-catalogue/src')]
from osr_mech.engineering_definition import load_definition,fingerprint
from engineering.civil_exploration.shared_demo import demonstration
from engineering.civil_exploration.spatial_demo import scenarios,configuration
from engineering.civil_exploration.spatial_vehicle import run_spatial
from engineering.civil_exploration.spatial_structure import native_beam_benchmark
from engineering.civil_exploration.wheel_contact import benchmarks
from engineering.civil_exploration.assembled_materials import assess,synthetic_laws
from engineering.civil_exploration.correlation import protocols,calibrate,evidence
from engineering.civil_exploration.joint_submodel import load_case,run as run_joint
from engineering.civil_exploration.shared_search import search
from engineering.civil_exploration.constraints import convergence


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def common_api():return runpy.run_path(str(ROOT/'tools/automation/shared-train-viaduct.py'))


def sources(api):
    return {**api['source_hashes'](),str(Path(__file__).relative_to(ROOT)):sha(__file__),
            **{str(p.relative_to(ROOT)):sha(p) for p in sorted((ROOT/'engineering/civil_exploration/config').glob('*.json'))}}


def publish(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+'\n')


def forward(model,cfg,parameters,test,dt,mesh,rail):
    import numpy as np
    m=deepcopy(model);c=deepcopy(cfg)
    for name,value in parameters.items():
        value=float(value)
        if name in ('primary_factor','secondary_factor'):
            for joint in m['joints']:
                if joint['connection']==name.removesuffix('_factor'):
                    law=c['joint_laws'][joint['id']];law['stiffness_si']=(np.asarray(law['stiffness_si'])*value).tolist()
        elif name=='deck_modulus_factor':m['bridge']['candidate']['material']['youngs_modulus_pa']*=value
        elif name=='contact_modulus_factor':c['contact']['effective_modulus_pa']*=value
        elif name=='friction_coefficient':c['contact']['friction_coefficient']=value
        else:raise ValueError('unregistered spatial calibration parameter: '+name)
    r=run_spatial(m,c,dt=dt,duration_s=max(test['time_s']),deck_mesh=mesh,rail_step=rail)
    values=[];channel=test['channel']
    for h in r['history']:
        row=next(x for x in h['contacts'] if x['train']==channel['train'] and x['wheelset']==channel['wheelset'] and x['side']==channel['side'])
        if channel['metric'] not in ('normal_n','lateral_n','longitudinal_n'):raise ValueError('unsupported calibration channel')
        values.append(row[channel['metric']])
    if min(test['time_s'])<dt:raise ValueError('measured sample predates the forward solver output')
    return np.interp(test['time_s'],[h['time_s'] for h in r['history']],values)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('task',choices=['spatial','search','joint','correlate','protocols','verify'])
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--model',type=Path);parser.add_argument('--config',type=Path)
    parser.add_argument('--material-laws',type=Path,help='retained explicit region-specific material records')
    parser.add_argument('--dt',type=float,default=.001);parser.add_argument('--duration',type=float,default=.1)
    parser.add_argument('--mesh',type=int,default=4);parser.add_argument('--rail-step',type=float,default=1.)
    parser.add_argument('--evaluations',type=int,default=8);parser.add_argument('--seeds',default='11,23')
    parser.add_argument('--dynamic-result',type=Path);parser.add_argument('--joint-id',default='car-1/bogie-1/secondary')
    parser.add_argument('--train-id',default='train-A');parser.add_argument('--solid-mesh',type=float,default=.009)
    parser.add_argument('--measurements',type=Path);parser.add_argument('--parameters',type=Path);parser.add_argument('--holdout-specimens')
    args=parser.parse_args();api=common_api();source=sources(api);environment=api['solver_environment']();output=args.output.resolve()
    if args.task=='verify':
        receipt=json.loads((output/'receipt.json').read_text())
        if receipt['sources_sha256']!=source or receipt['solver_environment']!=environment:raise ValueError('campaign implementation or solver environment changed')
        for relative,digest in receipt['outputs_sha256'].items():
            path=(output/relative).resolve()
            if not path.is_relative_to(output) or not path.is_file() or sha(path)!=digest:raise ValueError('campaign output changed: '+relative)
        load_definition(output/'definition.json')
        if (output/'measurements.json').is_file():
            for test in json.loads((output/'measurements.json').read_text())['tests']:
                for reference in (test['source'],test['calibration_record']):evidence(reference,ROOT)
        print(json.dumps(dict(verified=True,task=receipt['task'],engineering_released=False)));return
    if output.exists():raise ValueError('campaign output already exists; use a new evidence directory')
    model=load_definition(args.model) if args.model else demonstration()
    if args.model and args.task=='spatial' and not args.config:
        raise ValueError('a supplied hardware model requires its own explicit spatial configuration')
    if args.model and args.task=='search':
        raise ValueError('the built-in mixed search uses the explicitly synthetic allocation; supplied hardware needs a reviewed search space')
    output.mkdir(parents=True);publish(output/'definition.json',model);publish(output/'protocols.json',protocols(model))
    try:
        if args.task=='spatial':
            cases={'supplied':json.loads(args.config.read_text())} if args.config else scenarios(model)
            results={};summary=[]
            for name,cfg in cases.items():
                publish(output/name/'configuration.json',cfg)
                result=run_spatial(model,cfg,dt=args.dt,duration_s=args.duration,deck_mesh=args.mesh,rail_step=args.rail_step)
                results[name]=result;publish(output/name/'dynamics.json',result)
                laws=json.loads(args.material_laws.read_text()) if args.material_laws else ({} if args.model else synthetic_laws(model))
                publish(output/name/'material-laws.json',laws)
                material=assess(model,result,laws);publish(output/name/'materials.json',material)
                summary.append(dict(case=name,within_adapter_domain=result['within_adapter_domain'],
                    peak_carbody_acceleration_m_s2=result['peak_ride_acceleration_m_s2'],
                    peak_contact_n=result['maximum_wheel_contact_n'],unloading=result['maximum_wheel_unloading'],
                    contact_work_residual_w=result['contact_power_balance_residual_w'],
                    capacity_accepted=False))
                print(json.dumps(summary[-1]),flush=True)
            metrics=['maximum_wheel_contact_n','peak_structure_displacement_m','peak_ride_acceleration_m_s2','maximum_wheel_unloading']
            baseline=next(iter(cases));levels=[results[baseline]];dt=args.dt
            for _ in range(4):
                if dt/2<.0000625:break
                dt/=2
                r=run_spatial(model,cases[baseline],dt=dt,duration_s=args.duration,deck_mesh=args.mesh,rail_step=args.rail_step)
                levels.append(r);publish(output/'refinement'/f'dt-{dt}-mesh-{args.mesh}-rail-{args.rail_step}.json',r)
                if convergence(levels,metrics)['passed']:break
            if len(levels)<2:raise ValueError('time step must allow at least one independent temporal refinement')
            refined=run_spatial(model,cases[baseline],dt=dt,duration_s=args.duration,deck_mesh=args.mesh*2,rail_step=args.rail_step/2)
            publish(output/'refinement'/f'dt-{dt}-mesh-{args.mesh*2}-rail-{args.rail_step/2}.json',refined)
            report=dict(schema='osr-spatial-campaign/1',cases=summary,native_structure=native_beam_benchmark(),contact_benchmark=benchmarks(),
                temporal_levels_s=[r['time_step_s'] for r in levels],
                temporal_refinement=convergence(levels,metrics),spatial_refinement=convergence([levels[-1],refined],metrics),
                refinement_tolerance_basis='5% numerical research check; not a railway acceptance limit',
                adopted_project_standards=None,physical_validation=False,engineering_released=False)
            publish(output/'summary.json',report)
        elif args.task=='search':
            report=search(model,seeds=tuple(map(int,args.seeds.split(','))),evaluations=args.evaluations)
            publish(output/'search.json',report)
        elif args.task=='joint':
            if args.dynamic_result is None:raise ValueError('joint submodel requires a retained dynamic result')
            result=json.loads(args.dynamic_result.read_text());case=load_case(result,args.joint_id,args.train_id)
            publish(output/'load-case.json',case);publish(output/'summary.json',run_joint(output/'native',model,case,size=args.solid_mesh))
        elif args.task=='correlate':
            if not all((args.model,args.config,args.measurements,args.parameters,args.holdout_specimens)):
                raise ValueError('physical correlation requires model, config, measurements, parameters and holdout specimen IDs')
            cfg=json.loads(args.config.read_text());dataset=json.loads(args.measurements.read_text());parameters=json.loads(args.parameters.read_text())
            report=calibrate(model,dataset,parameters,lambda p,t:forward(model,cfg,p,t,args.dt,args.mesh,args.rail_step),
                root=ROOT,holdout_specimens=args.holdout_specimens.split(','))
            publish(output/'configuration.json',cfg);publish(output/'measurements.json',dataset);publish(output/'parameters.json',parameters);publish(output/'correlation.json',report)
        if sources(api)!=source:raise ValueError('source changed during campaign')
        outputs={p.relative_to(output).as_posix():sha(p) for p in sorted(output.rglob('*')) if p.is_file()}
        publish(output/'receipt.json',dict(schema='osr-shared-campaign-receipt/1',task=args.task,sources_sha256=source,
            solver_environment=environment,outputs_sha256=outputs,physical_validation=False,engineering_released=False))
    except Exception as error:
        publish(output/'failure.json',dict(error=type(error).__name__,message=str(error),sources_sha256=source,
            solver_environment=environment,physical_validation=False,engineering_released=False))
        raise


if __name__=='__main__':main()
