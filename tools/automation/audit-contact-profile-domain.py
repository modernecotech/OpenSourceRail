#!/usr/bin/env python3
"""Audit an immutable current or archived service campaign's profile footprints."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT),str(ROOT/'design/component-catalogue/src')]
from osr_mech.engineering_definition import load_definition
from engineering.analysis.contact_domain import audit_history


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--campaign',type=Path,required=True)
    p.add_argument('--case',default='empty-15mps');p.add_argument('--revision',help='producing git revision, for archived solver sources')
    p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    folder=a.campaign.resolve();receipt=load_definition(folder/'receipt.json')
    if a.output.exists():raise ValueError('use a fresh profile-audit output')
    for relative,digest in receipt['outputs_sha256'].items():
        path=(folder/relative).resolve()
        if not path.is_relative_to(folder) or not path.is_file() or sha(path)!=digest:raise ValueError('retained campaign output changed: '+relative)
    revision=None
    if a.revision:
        revision=subprocess.check_output(['git','rev-parse','--verify','--end-of-options',a.revision+'^{commit}'],cwd=ROOT,text=True).strip()
    for relative,digest in receipt['sources_sha256'].items():
        path=Path(relative)
        if path.is_absolute() or '..' in path.parts:raise ValueError('repository-relative source path required')
        actual=(hashlib.sha256(subprocess.check_output(['git','show',revision+':'+relative],cwd=ROOT)).hexdigest() if revision else sha(ROOT/path))
        if actual!=digest:raise ValueError('campaign source does not match its producing revision: '+relative)
    case=(folder/a.case).resolve()
    if not case.is_relative_to(folder):raise ValueError('case path outside campaign')
    model=load_definition(folder/'definition.json');configuration=load_definition(case/'configuration.json');history=case/'history.jsonl.gz'
    result=audit_history(model,configuration,history)
    summary=load_definition(folder/'summary.json')
    if summary['hardware_definition_sha256']!=result['hardware_definition_sha256']:raise ValueError('campaign summary targets another hardware definition')
    result.update(campaign_receipt_sha256=sha(folder/'receipt.json'),history_sha256=sha(history),
        campaign_budgets=summary['budgets'],campaign_cases=summary['cases'],
        producer_sources_verified=True,producing_commit=revision,solver_environment_reverified=False,
        audit_sources_sha256={str(path.relative_to(ROOT)):sha(path) for path in [Path(__file__),
            ROOT/'engineering/analysis/contact_domain.py',ROOT/'engineering/civil_exploration/wheel_contact.py']})
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(dict(first_footprint_exceedance=result['first_footprint_exceedance'],
        footprint_exceedance_count=result['footprint_exceedance_count'],physical_validation=False)))


if __name__=='__main__':main()
