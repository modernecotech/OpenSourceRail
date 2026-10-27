#!/usr/bin/env python3
"""Four bounded axial-method fixtures; never full-body or physical acceptance."""
import argparse,json,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from engineering.design_search import grammar_structure as method
from engineering.station_rail.common import encoded,identity


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'build/generative-native-ci')
    parser.add_argument('--plan',action='store_true')
    args=parser.parse_args();plan=method.benchmark_plan()
    if args.plan:
        print(json.dumps(plan,sort_keys=True));return 0
    if args.output.exists():raise ValueError('Fresh benchmark output directory required')
    args.output.mkdir(parents=True);(args.output/'plan.json').write_bytes(encoded(plan));results=[]
    for job in plan['native_jobs']:
        result=method.run(job['graph'],args.output/job['id'],subdivisions=job['subdivisions'],memory_mb=1024,timeout_s=45)
        results.append(result)
    expected=plan['analytical_checks'];bar,tripod=results[0],results[2]
    status=all(r.get('numerical_validity')=='verified_axial_method' for r in results)
    status=status and abs(bar.get('displacements_m',{}).get('tip',[0])[0]-expected['axial_tip_x_m'])<=abs(expected['axial_tip_x_m'])*1e-4
    status=status and abs(tripod.get('displacements_m',{}).get('3',[0,0,0])[2]-expected['tripod_tip_z_m'])<=abs(expected['tripod_tip_z_m'])*1e-4
    summary=dict(schema='osr-generative-method-CI/1',status='pass' if status else 'fail',results=results,
        scope=method.SCOPE,physical_accepted=False,full_body_model_admitted=False)
    summary['run_id']=identity(summary);(args.output/'summary.json').write_bytes(encoded(summary))
    print(json.dumps(dict(status=summary['status'],native_cases=len(results),physical_accepted=False),sort_keys=True));return 0 if status else 1


if __name__=='__main__':raise SystemExit(main())
