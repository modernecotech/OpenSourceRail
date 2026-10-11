#!/usr/bin/env python3
"""Generate and verify original best-practice designs in the shared twin."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS'):os.environ[key]='1'
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT),str(ROOT/'design/component-catalogue/src')]
from osr_mech.engineering_definition import fingerprint,load_definition
from engineering.twin_design.compiler import compile_design
from engineering.twin_design.viewer import html,netlist,circuit_svg,component_csv

PUBLIC=ROOT/'engineering/models/digital-twins/best-practice'


def encoded(value):return json.dumps(value,sort_keys=True,ensure_ascii=False,allow_nan=False,separators=(',',':'))+'\n'


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def published(result):
    return dict(schema='osr-best-practice-design-twin/1',configuration_sha256=fingerprint(result['model']),
        train_model=result['model'],interfaces=result['interfaces'],infrastructure=result['infrastructure'],
        feature_register=[{k:v for k,v in row.items() if k not in ('geometry','position_m')} for row in result['features']],
        studies=result['studies'],review=result['review'],
        authority='engineering/twin_design/data/design-inputs.json and compiler; generated review asset',
        production_released=False,physical_validation=False)


def check_public(result):
    expected=encoded(published(result))
    if (PUBLIC/'reference-twin.json').read_bytes()!=expected.encode():raise ValueError('published design twin is stale')
    if load_definition(PUBLIC/'review.json')!=result['review']:raise ValueError('published design review is stale')
    for name,value in exports(result).items():
        if (PUBLIC/name).read_bytes()!=value.encode():raise ValueError('published design export is stale: '+name)


def exports(result):
    sources=load_definition(ROOT/'engineering/best_practice/data/sources.json')
    return {'index.html':html(result,sources),'circuit.json':encoded(netlist(result)),
            'precharge.svg':circuit_svg(result),'component-schedule.csv':component_csv(result)}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['generate','verify','check-public'])
    parser.add_argument('--output',type=Path);parser.add_argument('--inputs',type=Path)
    parser.add_argument('--publish',action='store_true')
    args=parser.parse_args()
    if args.command=='check-public':
        result=compile_design();check_public(result)
    elif args.command=='generate':
        if args.output is None:parser.error('generate requires --output')
        result=compile_design(load_definition(args.inputs) if args.inputs else None)
        if args.output.exists():raise ValueError('use a fresh retained study directory')
        args.output.mkdir(parents=True)
        for name,value in result.items():(args.output/(name+'.json')).write_text(encoded(value))
        receipt=dict(schema='osr-design-twin-receipt/1',configuration_sha256=fingerprint(result['model']),
            source_sha256=result['review']['source_sha256'],
            outputs_sha256={p.name:sha(p) for p in sorted(args.output.glob('*.json'))},production_released=False)
        (args.output/'receipt.json').write_text(encoded(receipt))
        if args.publish:
            if args.inputs:parser.error('published reference uses canonical inputs')
            PUBLIC.mkdir(parents=True,exist_ok=True)
            (PUBLIC/'reference-twin.json').write_text(encoded(published(result)))
            (PUBLIC/'review.json').write_text(json.dumps(result['review'],indent=2,sort_keys=True)+'\n')
            for name,value in exports(result).items():(PUBLIC/name).write_bytes(value.encode())
            check_public(result)
    else:
        if args.output is None:parser.error('verify requires --output')
        folder=args.output.resolve();receipt=load_definition(folder/'receipt.json')
        for relative,digest in receipt['outputs_sha256'].items():
            p=(folder/relative).resolve()
            if not p.is_relative_to(folder) or not p.is_file() or sha(p)!=digest:raise ValueError('changed study output: '+relative)
        for relative,digest in receipt['source_sha256'].items():
            p=(ROOT/relative).resolve()
            if not p.is_relative_to(ROOT) or sha(p)!=digest:raise ValueError('changed study source: '+relative)
        result=compile_design(load_definition(folder/'inputs.json'))
        for name,value in result.items():
            if fingerprint(load_definition(folder/(name+'.json')))!=fingerprint(value):raise ValueError('study no longer reproduces: '+name)
    print(json.dumps({k:result['review'][k] for k in ('configuration_sha256','instance_count','added_instance_count',
        'infrastructure_instance_count','total_train_mass_kg','one_module_out_comfort_screen_passed','physical_validation')}))


if __name__=='__main__':main()
