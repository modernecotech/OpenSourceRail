"""Recorded optional backend pilot; existing default backends are unchanged."""
import argparse
import json
from . import native, pilot


def main(argv=None, *, root=pilot.ROOT):
    parser=argparse.ArgumentParser(prog='./osr design backends')
    commands=parser.add_subparsers(dest='command',required=True)
    p=commands.add_parser('plan');p.add_argument('--full',action='store_true');p.add_argument('--include-rc',action='store_true')
    p=commands.add_parser('install');p.add_argument('tools',nargs='*',choices=['solidcraft','fieldcraft','solidcraft-rc'])
    p.add_argument('--tool-root',default=str(native.DEFAULT_TOOLS))
    p=commands.add_parser('run');p.add_argument('--output',required=True)
    p.add_argument('--tool-root',default=str(native.DEFAULT_TOOLS));p.add_argument('--include-rc',action='store_true')
    p=commands.add_parser('verify');p.add_argument('--output',required=True)
    args=parser.parse_args(argv)
    if args.command=='plan':
        value=pilot.plan(root,include_rc=args.include_rc)
        if not args.full:value={k:v for k,v in value.items() if k!='cases'}|dict(cases=[dict(case_id=c['case_id'],candidate_id=c['candidate_id'],
            component_geometry_id=c['component_geometry_id'],parts=c['expected']['part_count'],scope=c['scope']) for c in value['cases']])
    elif args.command=='install':value=[native.install(n,args.tool_root) for n in (args.tools or ['solidcraft','fieldcraft'])]
    elif args.command=='run':value=pilot.run(args.output,root=root,tool_root=args.tool_root,include_rc=args.include_rc)
    else:value=pilot.verify(args.output,root=root)
    if args.command in ('run','verify'):
        value={k:v for k,v in value.items() if k not in ('artifact_sha256','stages')}
    print(json.dumps(value,sort_keys=True,indent=2,allow_nan=False))
    return 3 if isinstance(value,dict) and value.get('software_pilot_passed') is False else 0


if __name__=='__main__':raise SystemExit(main())
