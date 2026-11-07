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
    commands.add_parser('providers',help='Show scoped provider interfaces and retained specialist routes')
    group=commands.add_parser('viaduct',help='Same-candidate 20 m CAD, numerical and delivery comparison').add_subparsers(dest='action',required=True)
    p=group.add_parser('plan');p.add_argument('--full',action='store_true')
    p=group.add_parser('run');p.add_argument('--output',required=True);p.add_argument('--cad-state')
    p.add_argument('--analysis-state',action='append',default=[]);p.add_argument('--resource-state',action='append',default=[])
    p.add_argument('--execute',action='store_true',help='Dispatch fresh bounded native workers for missing evidence')
    p.add_argument('--verification-python',help='Explicit original numerical coordinator for strict historical replay')
    p=group.add_parser('verify');p.add_argument('--output',required=True)
    p=group.add_parser('publish');p.add_argument('--state',required=True);p.add_argument('--evidence',required=True);p.add_argument('--output',required=True)
    p=group.add_parser('verify-publication');p.add_argument('--output')
    args=parser.parse_args(argv)
    if args.command=='providers':
        from . import backend_api
        value=backend_api.registry()
    elif args.command=='viaduct':
        from . import viaduct_workflow
        if args.action=='plan':
            value=viaduct_workflow.plan(root=root)
            if not args.full:
                value=dict(schema='osr-viaduct-backend-plan-summary/1',source_request_id=value['request_id'],
                    cases=[dict(case_id=c['case_id'],candidate_id=c['candidate_id'],component_geometry_id=c['component_geometry_id']) for c in value['cases']],
                    numerical_finalists=value['numerical_finalists'],limits=value['limits'],selected_reference_changed=False,physical_accepted=False)
        elif args.action=='run':
            value=viaduct_workflow.run(args.output,cad_state=args.cad_state,analysis_states=args.analysis_state,
                resource_states=args.resource_state,execute=args.execute,root=root,verification_python=args.verification_python)
            # Historical replay can require a different, explicitly pinned NumPy runtime.
            value=dict(schema='osr-viaduct-backend-run-summary/1',source_result_id=value['result_id'],
                output=args.output,complete_calculated_geometry_outlines=value['complete_calculated_geometry_outlines'],
                fresh_native_invocations=value['fresh_native_invocations'],selected_reference_changed=False,physical_accepted=False)
        elif args.action in ('publish','verify-publication'):
            from . import viaduct_publication
            value=(viaduct_publication.publish(args.state,args.evidence,args.output,root=root)
                if args.action=='publish' else viaduct_publication.verify(args.output,root=root))
        else:value=viaduct_workflow.verify(args.output,root=root)
    elif args.command=='plan':
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
