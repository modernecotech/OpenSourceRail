import argparse,json,time
from pathlib import Path
from . import model,export


def main(argv=None):
    p=argparse.ArgumentParser(prog='python -m engineering.vehicle_installation');p.add_argument('--output',required=True,type=Path);p.add_argument('--cad',action='store_true');p.add_argument('--battery-layout',choices=('thin-distributed','above-floor-control'),default='thin-distributed');a=p.parse_args(argv)
    start=time.monotonic();result=model.build(battery_layout=a.battery_layout);out=export.write(result,a.output,cad=a.cad)
    print(json.dumps(dict(candidate_id=result['candidate_id'],evaluation_id=result['evaluation_id'],patterns=len(result['patterns']),occurrences=result['total_occurrences'],nominal_mass_kg=result['nominal_part_mass_kg'],wall_s=time.monotonic()-start,manifest_id=out['manifest_id']),indent=2))
    return 0


if __name__=='__main__':raise SystemExit(main())
