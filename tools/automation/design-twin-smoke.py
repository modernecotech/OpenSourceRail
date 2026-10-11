#!/usr/bin/env python3
"""Retain a four-step coupled integration check without full-passage acceptance."""
import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS'):os.environ[key]='1'
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT),str(ROOT/'design/component-catalogue/src')]
from osr_mech.engineering_definition import load_definition,fingerprint
from engineering.civil_exploration.spatial_vehicle import run_spatial


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--package',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if a.output.exists():raise ValueError('retain earlier integration evidence; use a fresh output path')
    subprocess.run([sys.executable,str(ROOT/'tools/automation/design-best-practice-twin.py'),'verify','--output',str(a.package)],check=True)
    model=load_definition(a.package/'model.json');configuration=load_definition(a.package/'spatial_configuration.json')
    result=run_spatial(model,configuration,dt=.005,duration_s=.02)
    history=json.dumps(result.pop('history'),sort_keys=True,allow_nan=False).encode()
    raw=a.output.with_suffix('.history.json.gz');raw.write_bytes(gzip.compress(history,mtime=0))
    result.update(scope='four-step coupled integration smoke test; no timestep/mesh or full-passage acceptance',
        complete_passage_qualified=False,physical_validation=False,
        producer_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        compiler_review_sha256=hashlib.sha256((a.package/'review.json').read_bytes()).hexdigest(),
        retained_history_sha256=hashlib.sha256(raw.read_bytes()).hexdigest(),
        retained_history_uncompressed_sha256=hashlib.sha256(history).hexdigest())
    a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(dict(configuration_sha256=fingerprint(model),steps=result['steps'],within_adapter_domain=result['within_adapter_domain'],complete_passage_qualified=False)))


if __name__=='__main__':main()
