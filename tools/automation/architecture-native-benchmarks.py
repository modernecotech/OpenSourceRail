#!/usr/bin/env python3
"""Bounded joint and nonlinear magnetic method checks, never physical release."""
from pathlib import Path
import argparse,json,sys
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from engineering.design_search import joint_models as j,nonlinear_motor as n
from engineering.station_rail.common import encoded


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--quick',action='store_true',help='One finite-area joint and one DC circuit; no mesh/energy-gradient claim')
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    joint=j.run_benchmarks(a.output/'joint',plan=[('finite_area',2)] if a.quick else [('finite_area',m) for m in (2,3,4)],timeout_s=90)
    samples={}
    for name,gap in ([('centre',.001)] if a.quick else [('minus',.00099),('centre',.001),('plus',.00101)]):
        samples[name]=n.run_benchmark(n.benchmark_case(gap_m=gap),a.output/name)
    magnetic_ok=all(r['execution']=='completed' and r['numerical_validity']=='valid' for r in samples.values())
    gradient=None
    if magnetic_ok and not a.quick:gradient=n.energy_gradient(samples['minus'],samples['centre'],samples['plus'])
    joint_ok=joint['execution']=='completed' and all(r.get('numerical_validity')=='valid' for r in joint['cases'])
    if not a.quick:joint_ok=joint_ok and all(r.get('mesh_confirmed') is True for r in joint['refinements'])
    # Preserve numerical failures and the exact records before returning CI failure.
    value=dict(schema='osr-architecture-nightly-methods/1',quick=a.quick,joint=joint,magnetic_samples=samples,
        coenergy_gradient=gradient,method_checks_pass=joint_ok and magnetic_ok and (gradient is None or gradient['relative_difference']<.001),
        scope='Synthetic finite-area transfer and generic nonlinear DC magnetic circuit only; no moving LIM or full-body validation',
        physical_accepted=False,engineering_accepted=False,manufacturing_release=False,operating_release=False)
    (a.output/'summary.json').write_bytes(encoded(value))
    print(json.dumps(dict(method_checks_pass=value['method_checks_pass'],physical_accepted=False,output=str(a.output))))
    return 0 if value['method_checks_pass'] else 1


if __name__=='__main__':raise SystemExit(main())
