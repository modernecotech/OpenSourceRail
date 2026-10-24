"""One resource-bounded evaluation; no domain imports before process limits."""
import argparse
import json
from pathlib import Path


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input',required=True,type=Path);parser.add_argument('--output',required=True,type=Path)
    parser.add_argument('--memory-mb',required=True,type=int);parser.add_argument('--timeout-s',required=True,type=float)
    parser.add_argument('--parent-pid',type=int);parser.add_argument('--parent-start')
    args=parser.parse_args()
    # This module and its parent namespaces have only stdlib imports here.
    from .resource_limits import apply
    from .storage import atomic_immutable
    limits=apply(args.memory_mb,args.timeout_s,parent_pid=args.parent_pid,parent_start=args.parent_start)
    atomic_immutable(args.output.parent/'resource-limits.json',(json.dumps(limits,sort_keys=True)+'\n').encode())
    if args.input.is_symlink() or args.input.stat().st_size>16*1024**2:raise ValueError('bounded ordinary worker input required')
    job=json.loads(args.input.read_bytes())
    declared=job['worker_limits']
    if declared['memory_mb']!=args.memory_mb or declared['timeout_s']!=args.timeout_s:raise ValueError('worker descriptor and OS budgets differ')
    from . import contracts
    candidate=contracts.validate_candidate(job['candidate']);request=contracts.validate_request(job['request'])
    if candidate['candidate_id']!=request['candidate_id'] or candidate['requirement_revision']!=request['requirement_revision']:
        raise ValueError('worker candidate/request context mismatch')
    if job['mode']=='verify':
        from .verification import confirm
        value=confirm(candidate,request,job['primary'])
    elif job['mode']=='evaluate':
        from .evaluators import evaluate
        value=evaluate(candidate,request['evaluator_id'],**{key:request[key] for key in ('purpose','hypothesis','settings','mesh','scenario','environment')})
    else:raise ValueError('registered worker mode required')
    if value['request']!=request:raise ValueError('worker evaluation did not use the declared exact context')
    atomic_immutable(args.output,contracts.encoded(contracts.validate_result(value)))


if __name__=='__main__':main()
