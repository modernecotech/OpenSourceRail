#!/usr/bin/env python3
"""Generate/verify a complete, traceable OSR reference-parts variant package."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[key]='1'
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT),str(ROOT/'design/component-catalogue/src')]
from osr_mech.engineering_definition import load_definition, fingerprint
from engineering.civil_exploration.variant_compiler import compile_variant, BASIS_PATH, CHOICES_PATH


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('task',choices=['generate','verify','check-review'])
    parser.add_argument('--choices',type=Path,default=CHOICES_PATH)
    parser.add_argument('--basis',type=Path,default=BASIS_PATH)
    parser.add_argument('--output',type=Path)
    parser.add_argument('--review',type=Path)
    args=parser.parse_args()
    if args.task=='verify':
        if args.output is None:parser.error('verify requires --output')
        folder=args.output.resolve();receipt=load_definition(folder/'receipt.json')
        for relative,digest in receipt['outputs_sha256'].items():
            path=(folder/relative).resolve()
            if not path.is_relative_to(folder) or not path.is_file() or sha(path)!=digest:
                raise ValueError('changed generated part output: '+relative)
        for relative,digest in receipt['sources_sha256'].items():
            if sha(ROOT/relative)!=digest:raise ValueError('part compiler source changed: '+relative)
        choices=load_definition(folder/'choices.json');basis=load_definition(folder/'industry-basis.json')
        result=compile_variant(choices,basis=basis)
        result['review']['sources_sha256'][str(Path(__file__).relative_to(ROOT))]=sha(Path(__file__))
        for key,value in result.items():
            if fingerprint(load_definition(folder/(key+'.json')))!=fingerprint(value):
                raise ValueError('compiled variant no longer reconciles: '+key)
        print(json.dumps(dict(verified=True,configuration_sha256=result['review']['configuration_sha256'],production_released=False)))
        return
    choices=load_definition(args.choices);basis=load_definition(args.basis);result=compile_variant(choices,basis=basis)
    result['review']['sources_sha256'][str(Path(__file__).relative_to(ROOT))]=sha(Path(__file__))
    # Keep the CLI itself in provenance without changing compile_variant's pure
    # dependency register. The review is a separate output, verified separately.
    if args.task=='check-review':
        if args.review is None:parser.error('check-review requires --review')
        if load_definition(args.review)!=result['review']:raise ValueError('published automated parts review is stale')
        print(json.dumps(dict(review_current=True,production_released=False)));return
    if args.output is None:parser.error('generate requires --output')
    folder=args.output.resolve()
    if folder.exists():raise ValueError('use a fresh generated-parts evidence directory')
    folder.mkdir(parents=True)
    for name,value in dict(choices=choices,**{'industry-basis':basis},**result).items():
        (folder/(name+'.json')).write_text(json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+'\n')
    outputs={p.relative_to(folder).as_posix():sha(p) for p in sorted(folder.iterdir()) if p.is_file()}
    receipt=dict(schema='osr-reference-parts-receipt/1',sources_sha256=result['review']['sources_sha256'],
        outputs_sha256=outputs,configuration_sha256=result['review']['configuration_sha256'],production_released=False)
    (folder/'receipt.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    if args.review:
        if args.review.exists():raise ValueError('review output already exists; retain previous evidence before republishing')
        args.review.parent.mkdir(parents=True,exist_ok=True)
        args.review.write_text((folder/'review.json').read_text())
    print(json.dumps({k:result['review'][k] for k in ('family','car_count','wheelset_count','instance_count','joint_count','total_mass_kg','physical_validation')}))


if __name__=='__main__':main()
