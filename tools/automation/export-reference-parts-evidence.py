#!/usr/bin/env python3
"""Publish compact native/operating evidence without promoting failed cases."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT),str(ROOT/'design/component-catalogue/src')]
from osr_mech.engineering_definition import load_definition,fingerprint


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--package',type=Path,required=True);p.add_argument('--cad',type=Path,required=True)
    p.add_argument('--native',type=Path,required=True);p.add_argument('--audit',type=Path,required=True)
    p.add_argument('--service',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    if a.output.exists():raise ValueError('evidence output exists; retain previous evidence')
    subprocess.run([sys.executable,str(ROOT/'tools/automation/compile-reference-parts.py'),'verify','--output',str(a.package)],check=True)
    subprocess.run([sys.executable,str(ROOT/'tools/automation/shared-service-envelope.py'),'verify','--output',str(a.service)],check=True)
    review=load_definition(a.package/'review.json');model=load_definition(a.package/'model.json')
    native=load_definition(a.native);audit=load_definition(a.audit);service=load_definition(a.service/'summary.json')
    config=fingerprint(model);cad_hash=sha(a.cad)
    if native['configuration_sha256']!=config or audit['configuration_sha256']!=config or service['hardware_definition_sha256']!=config:
        raise ValueError('native/service evidence belongs to another hardware variant')
    if native['fcstd_sha256']!=cad_hash or audit['fcstd_sha256']!=cad_hash:
        raise ValueError('native evidence geometry hash differs')
    for relative,digest in native['sources_sha256'].items():
        if sha(ROOT/relative)!=digest:raise ValueError('native CAD source changed: '+relative)
    if audit['audit_source_sha256']!=sha(ROOT/'tools/automation/verify-reference-parts-freecad.py'):
        raise ValueError('native audit source changed')
    if (native['native_solver_result']!='0' or not native['nominal_datums_reconciled'] or
        not audit['independent_geometry_integrals_passed'] or audit['restored_native_solver_result']!=0 or
        any(v<=0 for v in native['drawing_visible_edges'].values())):
        raise ValueError('native placement/integral/drawing checks did not pass')
    complete=[r['case'] for r in service['cases'] if r['status']=='completed' and r.get('complete_passage') and r.get('full_family_represented') and r.get('within_adapter_domain')]
    result=dict(schema='osr-automated-parts-evidence/1',configuration_sha256=config,
        compiler_review_sha256=sha(a.package/'review.json'),
        cad=dict(fcstd_sha256=cad_hash,native_receipt_sha256=sha(a.native),audit_sha256=sha(a.audit),
            instance_count=native['instance_count'],represented_car_count=native['represented_car_count'],
            native_solver_result=0,restored_solver_result=audit['restored_native_solver_result'],
            maximum_joint_datum_residual_mm=max(j['datum_residual_mm'] for j in native['joints']),
            drawing_visible_edges=native['drawing_visible_edges'],drawing_issued=False,
            analytic_occ_primitive_checks=audit['analytic_occ_primitive_checks'],
            maximum_relative_inertia_error=audit['maximum_relative_inertia_error']),
        service=dict(receipt_sha256=sha(a.service/'receipt.json'),cases=service['cases'],
            complete_full_family_case_ids=complete,unexecuted_case_ids=service['unexecuted_case_ids'],
            budgets=service['budgets'],numerical_time_and_mesh_confirmation_performed=False,
            retained_history_sha256={path:digest for path,digest in load_definition(a.service/'receipt.json')['outputs_sha256'].items() if path.endswith('history.jsonl.gz')}),
        publisher_sha256=sha(Path(__file__)),production_released=False,physical_validation=False,
        engineering_constraints_passed=None,
        remaining_gates=review['remaining_gates'])
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(dict(native_parts_verified=True,complete_full_family_passages=len(complete),physical_validation=False)))


if __name__=='__main__':main()
