import argparse,json
from pathlib import Path
from . import FLAGS,coordinator,publication,history


def main(argv=None):
    p=argparse.ArgumentParser(prog='./osr design station-cycle')
    sub=p.add_subparsers(dest='command',required=True)
    sub.add_parser('plan');sub.add_parser('history-verify')
    c=sub.add_parser('run');c.add_argument('--output',required=True,type=Path)
    c=sub.add_parser('publish');c.add_argument('--run',required=True,type=Path);c.add_argument('--output',type=Path)
    c=sub.add_parser('verify');c.add_argument('--output',type=Path);c.add_argument('--replay',action='store_true');c.add_argument('--state',type=Path)
    a=p.parse_args(argv)
    if a.command=='plan':
        brief,bundle,mass,p,requests=coordinator.requests()
        value=dict(physical_candidates=len({m['design']['variant']['candidate_id'] for m in requests}),
            nominal_cases=sum(m['nominal'] for m in requests),fault_cases=sum(not m['nominal'] for m in requests),
            maximum_native_cases_per_batch=16,native_cpu_s_per_batch=60,native_address_space_bytes=1073741824,
            cold_start=True,requested_headway_s=200,modeled_serial_direction_headway_s=2*p['leg_departure_interval_s'],
            concurrent_service_verified=False,body_candidate_id=bundle['candidate_id'],**FLAGS)
    elif a.command=='history-verify':value=history.verify()
    elif a.command=='run':
        r=coordinator.run(a.output)
        value=dict(study_id=r['study_id'],cases=len(r['records']),execution_wall_s=r['execution_wall_s'],**FLAGS)
    elif a.command=='publish':value=publication.publish(a.run,output=a.output)
    else:value=publication.verify(output=a.output,replay=a.replay,state=a.state)
    print(json.dumps(value,sort_keys=True,indent=2,allow_nan=False));return 0


if __name__=='__main__':raise SystemExit(main())
