"""Resource-bounded worker for one immutable mapped-city calculation."""
import argparse
import json
import os
from pathlib import Path
import resource


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--request',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--root',type=Path,required=True)
    parser.add_argument('--parent-snapshot',type=Path,help='Server-owned verified parent custody file')
    args=parser.parse_args()
    for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[key]='1'
    resource.setrlimit(resource.RLIMIT_CPU,(90,95))
    resource.setrlimit(resource.RLIMIT_AS,(3*1024**3,3*1024**3))
    resource.setrlimit(resource.RLIMIT_FSIZE,(32*1024**2,32*1024**2))
    resource.setrlimit(resource.RLIMIT_NOFILE,(256,256))
    from . import city_workflow
    request=json.loads(args.request.read_bytes())
    parent=None
    if args.parent_snapshot is not None:
        file=city_workflow.completion._ordinary(args.parent_snapshot)
        if file.stat().st_size>city_workflow.MAX_PARENT_SNAPSHOT_BYTES:raise ValueError('Bounded server parent snapshot required')
        parent=json.loads(file.read_bytes())
    manifest=city_workflow.run(request,args.output,root=args.root,parent=parent)
    print(json.dumps({'manifest_id':manifest['manifest_id'],'evaluation_id':manifest['evaluation_id']}),flush=True)


if __name__=='__main__':main()
