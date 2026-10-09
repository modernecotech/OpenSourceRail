#!/usr/bin/env python3
"""Recompute Baghdad dependencies in order after city engineering regeneration."""
import argparse
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]
CITY='cities/catalogue/west-asia/Iraq/Baghdad'
OPERATIONS=('tools/automation/generate-qa-maintenance-data.py','--design',CITY+'/design.toml','--scenario',CITY+'/baghdad.toml','--out-dir',CITY+'/operations')
STEPS=(
    OPERATIONS,
    ('tools/automation/generate-city-finance.py','--design',CITY+'/design.toml'),
    OPERATIONS,
    ('tools/automation/generate-city-finance.py','--design',CITY+'/design.toml'),
    OPERATIONS,
    ('tools/automation/generate-depot-scope.py','--design',CITY+'/design.toml'),
    'tools/automation/generate-factory-plan.py',
    'tools/automation/generate-iraq-funding-programme.py',
    'engineering/baghdad_detail.py',
    'tools/automation/baghdad_delivery_stress.py',
    'tools/automation/baghdad_qualification.py',
    'tools/automation/baghdad_viaduct_rentals.py',
    'tools/automation/baghdad_financing_redesign.py',
    'tools/automation/baghdad_equity.py',
    'tools/automation/baghdad_delivery_baseline.py',
    'tools/automation/baghdad_delivery_closure.py',
    'tools/automation/baghdad_viaduct_comparison.py',
    'tools/automation/baghdad_programme_recalculation.py',
    'tools/automation/baghdad_demand_bridge.py',
    'tools/automation/baghdad_cost_reconciliation.py',
    ('tools/automation/integrated-network-plan.py','--geometry-only'),
    ('tools/automation/connected-build-study.py','--refresh-cad'),
    ('tools/automation/generate-national-briefs.py','--country','IQ'),
    'tools/automation/generate-national-briefs.py',
    'tools/automation/generate-portfolio-summary.py',
    'tools/automation/publish-city-summary.py',
    'tools/automation/industrialisation-study.py',
    'tools/automation/coupled-programme-study.py',
    'tools/automation/civil-works-plan.py',
    'tools/automation/integrated-network-plan.py',
)
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--skip-portfolio',action='store_true',help='refresh city dependencies only; publish the portfolio after all city packages finish')
    parser.add_argument('--skip-connected',action='store_true',help='use a separately regenerated connected/CAD package; its source check still applies')
    args=parser.parse_args()
    if args.skip_connected:
        subprocess.run([sys.executable,str(ROOT/'tools/automation/connected-build-study.py'),
                        '--city','baghdad','--check'],cwd=ROOT,check=True)
    deferred={'tools/automation/generate-national-briefs.py','tools/automation/generate-portfolio-summary.py','tools/automation/publish-city-summary.py'}
    steps=tuple(step for step in STEPS if (not args.skip_portfolio or step not in deferred)
                and (not args.skip_connected or not isinstance(step,tuple) or step[0]!='tools/automation/connected-build-study.py'))
    for step in steps:
        command=(step,) if isinstance(step,str) else step
        print('Recomputing '+command[0],flush=True)
        subprocess.run([sys.executable,str(ROOT/command[0]),*command[1:]],cwd=ROOT,check=True)
if __name__=='__main__':main()
