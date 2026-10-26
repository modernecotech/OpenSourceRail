#!/usr/bin/env python3
"""Bounded nightly v0.6 numerical methods; failed structure stays an engineering fail."""
from pathlib import Path
import argparse,json,shutil,sys
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from engineering.station_rail import native_drive,native,vehicle
from engineering.station_rail.common import encoded

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    a.output.mkdir(parents=True,exist_ok=False)
    result=native_drive.run(a.output/'secondary',ROOT,getdp=shutil.which('getdp'),gmsh=shutil.which('gmsh'))
    v=vehicle.build(ROOT);sills=[native._run_ccx(a.output/name,v,dx) for name,dx in (('sill-coarse',.2),('sill-fine',.1))]
    value=dict(schema='osr-v06-nightly-methods/1',candidate_id=v['candidate_id'],drive_method_convergence=result['convergence_screen'],
       underframe_fixtures=sills,physical_accepted=False,complete_physical_journey=False,
       scope='Method execution and regression. Underframe screen failures are preserved; they are not solver/tool errors.')
    (a.output/'summary.json').write_bytes(encoded(value));print(json.dumps(value,indent=2))
    return 0 if result['convergence_screen']=='pass' else 1
if __name__=='__main__':raise SystemExit(main())
