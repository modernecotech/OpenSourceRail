#!/usr/bin/env python3
"""Bind executed native and numerical study evidence to the published design."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT),str(ROOT/'design/component-catalogue/src')]
from osr_mech.engineering_definition import load_definition,fingerprint
PUBLIC=ROOT/'engineering/models/digital-twins/best-practice'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--package',type=Path,required=True);a=parser.parse_args();folder=a.package.resolve()
    subprocess.run([sys.executable,str(ROOT/'tools/automation/design-best-practice-twin.py'),'verify','--output',str(folder)],check=True)
    subprocess.run([sys.executable,str(ROOT/'tools/automation/design-best-practice-twin.py'),'check-public'],check=True)
    model=load_definition(folder/'model.json');review=load_definition(folder/'review.json');config=fingerprint(model)
    native=load_definition(folder/'reference-twin.native.json');smoke=load_definition(folder/'spatial-smoke.json')
    if native['configuration_sha256']!=config or smoke['hardware_definition_sha256']!=config:raise ValueError('executed evidence targets another twin')
    if fingerprint(load_definition(PUBLIC/'review.json'))!=fingerprint(review):raise ValueError('published review differs from executed package')
    if native['compiler_review_sha256']!=sha(folder/'review.json') or smoke['compiler_review_sha256']!=sha(folder/'review.json'):raise ValueError('compiled review hash differs')
    if native['generator_sha256']!=sha(ROOT/'tools/automation/design-twin-freecad.py') or smoke['producer_sha256']!=sha(ROOT/'tools/automation/design-twin-smoke.py'):raise ValueError('execution producer changed')
    if native['fcstd_sha256']!=sha(folder/'reference-twin.FCStd') or native['step_sha256']!=sha(folder/'reference-twin.step'):raise ValueError('native geometry bytes changed')
    if smoke['retained_history_sha256']!=sha(folder/'spatial-smoke.history.json.gz'):raise ValueError('raw numerical history changed')
    if native['native_solver_result']!='0' or native['reopened_solver_result']!=0 or native['new_car_component_collisions'] or native['intra_component_collisions']:raise ValueError('native constraints or occupied-volume checks failed')
    if any(v<=0 for v in native['drawing_edges'].values()) or native['maximum_relative_primitive_inertia_error']>1e-8 or native['step_roundtrip_relative_volume_error']>1e-8:raise ValueError('native drawing/integral checks failed')
    if smoke['steps']!=4 or not smoke['within_adapter_domain'] or smoke['complete_passage_qualified']:raise ValueError('integration smoke scope changed')
    if any(r['physical_validation'] is not False for r in (review,native,smoke)):raise ValueError('study evidence cannot establish physical validation')
    names=['reference-twin.FCStd','reference-twin.step','reference-twin.native.json','spatial-smoke.json']
    for name in names:
        if (folder/name).stat().st_size>50*1024*1024:raise ValueError('native artifact exceeds repository size policy')
        shutil.copyfile(folder/name,PUBLIC/name)
    execution=dict(schema='osr-executed-design-twin-evidence/1',configuration_sha256=config,
        producer_sha256=sha(Path(__file__)),compiled_review_sha256=sha(folder/'review.json'),published_review_sha256=sha(PUBLIC/'review.json'),
        published_twin_sha256=sha(PUBLIC/'reference-twin.json'),
        artifact_sha256={name:sha(PUBLIC/name) for name in names},native_constraint_and_geometry_checks_passed=True,
        coupled_smoke_completed=True,complete_passage_qualified=False,physical_validation=False,production_released=False)
    (PUBLIC/'execution.json').write_text(json.dumps(execution,indent=2,sort_keys=True)+'\n')
    print(json.dumps(dict(executed_design_twin_published=True,configuration_sha256=config,physical_validation=False)))


if __name__=='__main__':main()
