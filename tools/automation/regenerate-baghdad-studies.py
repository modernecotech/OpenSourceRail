#!/usr/bin/env python3
"""Recompute Baghdad dependencies in order after city engineering regeneration."""
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]
STEPS=(
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
    'tools/automation/generate-national-briefs.py',
    'tools/automation/generate-portfolio-summary.py',
)
def main():
    if sys.argv[1:]:raise SystemExit('usage: regenerate-baghdad-studies.py')
    for step in STEPS:
        print('Recomputing '+step,flush=True)
        subprocess.run([sys.executable,str(ROOT/step)],cwd=ROOT,check=True)
if __name__=='__main__':main()
