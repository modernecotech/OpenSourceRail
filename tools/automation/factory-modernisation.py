#!/usr/bin/env python3
"""Generate/verify the open trainset design-to-factory improvement programme."""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import sys
for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[key]='1'
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT),str(ROOT/'design/component-catalogue/src')]
from osr_mech.engineering_definition import load_definition,fingerprint
from engineering.civil_exploration.variant_compiler import compile_variant
from engineering.industrialisation.expansion import build_package,demonstrations
from engineering.industrialisation.production import assess_traveler


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path,value):path.write_text(json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+'\n')


def open_exports(folder,result):
    with (folder/'assembly-operations.csv').open('w',newline='') as stream:
        fields=['id','title','instance_id','part_id','part_revision','serial','batch','resource','predecessors','required_evidence_kinds']
        writer=csv.DictWriter(stream,fieldnames=fields);writer.writeheader()
        for row in result['production_package']['operations']:
            writer.writerow({key:'|'.join(row[key]) if isinstance(row[key],list) else row[key] for key in fields})
    with (folder/'material-passports.csv').open('w',newline='') as stream:
        fields=['material_id','part_id','unit','candidate_material_family','released_grade','material_accepted']
        writer=csv.DictWriter(stream,fieldnames=fields);writer.writeheader()
        for row in result['material_passports']:
            writer.writerow({**{key:row[key] for key in fields if key!='candidate_material_family'},'candidate_material_family':row['candidate_spec']['material_family']})
    lines=['# OpenSourceRail factory work instructions — unissued',
        'Configuration: '+result['review']['configuration_sha256'],
        'Generated planning instructions. Issued drawings, qualified processes, actual records and independent review remain required.']
    for route in result['process_routes']:
        lines.extend(['','## '+route['part_id'],route['source_process']['release_level'],'',
            *[str(i+1)+'. '+step for i,step in enumerate(route['source_process']['primary_processes'])],
            '', 'Controls: '+', '.join(route['control_ids']),
            'Evidence: '+', '.join(route['source_process']['special_process_controls'])])
    (folder/'work-instructions.md').write_text('\n'.join(lines)+'\n')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('task',choices=['generate','verify','assess']);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--model',type=Path);p.add_argument('--battery',type=Path);p.add_argument('--record',type=Path)
    p.add_argument('--review',type=Path);a=p.parse_args();folder=a.output.resolve()
    if a.task=='assess':
        if a.record is None:p.error('assess needs --record')
        result=assess_traveler(load_definition(folder/'production_package.json'),load_definition(a.record),ROOT)
        print(json.dumps(result,indent=2,sort_keys=True));return
    if a.task=='verify':
        receipt=load_definition(folder/'receipt.json')
        for relative,digest in receipt['source_sha256'].items():
            if sha(ROOT/relative)!=digest:raise ValueError('factory source changed: '+relative)
        for relative,digest in receipt['outputs_sha256'].items():
            path=(folder/relative).resolve()
            if not path.is_relative_to(folder) or not path.is_file() or sha(path)!=digest:raise ValueError('factory output changed: '+relative)
        package=build_package(load_definition(folder/'model.json'),load_definition(folder/'battery.json'))
        package['demonstrations']=demonstrations();package['review']['source_sha256'][str(Path(__file__).relative_to(ROOT))]=sha(Path(__file__))
        for key,value in package.items():
            if fingerprint(load_definition(folder/(key+'.json')))!=fingerprint(value):raise ValueError('factory result no longer reproduces: '+key)
        print(json.dumps(dict(verified=True,production_released=False,physical_validation=False)));return
    if folder.exists():raise ValueError('use a fresh factory evidence directory')
    if bool(a.model)!=bool(a.battery):p.error('supply model and its compiled battery together')
    if a.model:model,battery=load_definition(a.model),load_definition(a.battery)
    else:
        variant=compile_variant();model,battery=variant['model'],variant['battery']
    result=build_package(model,battery);result['demonstrations']=demonstrations()
    result['review']['source_sha256'][str(Path(__file__).relative_to(ROOT))]=sha(Path(__file__))
    if a.review and a.review.exists():raise ValueError('review already exists; preserve previous evidence')
    folder.mkdir(parents=True)
    for name,value in dict(model=model,battery=battery,**result).items():write(folder/(name+'.json'),value)
    open_exports(folder,result)
    receipt=dict(schema='osr-industrialisation-receipt/1',source_sha256=result['review']['source_sha256'],
        outputs_sha256={path.name:sha(path) for path in sorted(folder.iterdir()) if path.is_file()},
        production_released=False,physical_validation=False)
    write(folder/'receipt.json',receipt)
    if a.review:a.review.parent.mkdir(parents=True,exist_ok=True);write(a.review,result['review'])
    print(json.dumps({k:v for k,v in result['review'].items() if k not in ('source_sha256','remaining_physical_gates','work_packages')}))


if __name__=='__main__':main()
