"""Current-release backend pilot with exact tool identities per native run."""
import argparse
import json
from pathlib import Path
from . import native, pilot


def main(argv=None, *, root=pilot.ROOT):
    parser=argparse.ArgumentParser(prog='./osr design backends')
    commands=parser.add_subparsers(dest='command',required=True)
    p=commands.add_parser('plan');p.add_argument('--full',action='store_true')
    p=commands.add_parser('refresh',help='Resolve latest stable official releases and seal exact tool bytes')
    p.add_argument('tools',nargs='*',choices=native.ACTIVE_TOOLS)
    p.add_argument('--tool-root',default=str(native.DEFAULT_TOOLS))
    p=commands.add_parser('install');p.add_argument('tools',nargs='*',choices=native.ACTIVE_TOOLS)
    p.add_argument('--tool-root',default=str(native.DEFAULT_TOOLS))
    p=commands.add_parser('run');p.add_argument('--output',required=True)
    p.add_argument('--tool-root',default=str(native.DEFAULT_TOOLS))
    p=commands.add_parser('verify');p.add_argument('--output',required=True)
    p=commands.add_parser('code-aster-box',help='Explicit exact-STEP numerical handoff control')
    p.add_argument('--step',required=True);p.add_argument('--output',required=True)
    p.add_argument('--candidate-id',required=True);p.add_argument('--image',required=True)
    p.add_argument('--fieldcraft-rejection',required=True,
                   help='Held readback for the same candidate and exact STEP bytes')
    p.add_argument('--python',required=True,help='Python with a current Gmsh installation')
    p=commands.add_parser('verify-code-aster-box',help='Verify preserved handoff without a fresh solve')
    p.add_argument('--output',required=True)
    p=commands.add_parser('code-aster-candidate',help='Bounded same-candidate STEP component FEA handoff')
    p.add_argument('--step',required=True);p.add_argument('--definition',required=True)
    p.add_argument('--fieldcraft-rejection',required=True);p.add_argument('--output',required=True)
    p.add_argument('--image',required=True);p.add_argument('--python',required=True)
    p=commands.add_parser('verify-code-aster-candidate',help='Verify preserved candidate handoff')
    p.add_argument('--output',required=True)
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
    resource_action = ('backend-'+args.command if args.command in ('refresh','install','run','code-aster-box','code-aster-candidate') else
        'backend-viaduct-run' if args.command=='viaduct' and args.action=='run' else None)
    if resource_action is not None:
        from engineering.development_baseline import FLAGS
        from engineering.performance import disk_hold_record
        admission_target=(Path(args.output).resolve().parent
                          if args.command in ('code-aster-box','code-aster-candidate') else root)
        hold=disk_hold_record(admission_target,resource_action,FLAGS)
        if hold is not None:
            print(json.dumps(hold,sort_keys=True,indent=2,allow_nan=False));return 3
    if args.command in ('code-aster-box','verify-code-aster-box'):
        from . import code_aster_control
        value=(code_aster_control.run_box(args.step,args.output,candidate_id=args.candidate_id,
                image=args.image,fieldcraft_rejection=args.fieldcraft_rejection,
                python=args.python) if args.command=='code-aster-box'
                else code_aster_control.verify_box(args.output))
    elif args.command in ('code-aster-candidate','verify-code-aster-candidate'):
        from . import code_aster_candidate
        value=(code_aster_candidate.run_candidate(args.step,args.output,
                json.loads(Path(args.definition).read_text()),
                fieldcraft_rejection=args.fieldcraft_rejection,image=args.image,python=args.python)
                if args.command=='code-aster-candidate'
                else code_aster_candidate.verify_candidate(args.output))
    elif args.command=='providers':
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
        value=pilot.plan(root)
        if not args.full:value={k:v for k,v in value.items() if k!='cases'}|dict(cases=[dict(case_id=c['case_id'],candidate_id=c['candidate_id'],
            component_geometry_id=c['component_geometry_id'],parts=c['expected']['part_count'],scope=c['scope']) for c in value['cases']])
    elif args.command=='refresh':value=native.refresh_latest(args.tools or native.ACTIVE_TOOLS,args.tool_root)
    elif args.command=='install':value=[native.install(n,args.tool_root) for n in (args.tools or native.ACTIVE_TOOLS)]
    elif args.command=='run':value=pilot.run(args.output,root=root,tool_root=args.tool_root)
    else:value=pilot.verify(args.output,root=root)
    if args.command in ('run','verify'):
        value={k:v for k,v in value.items() if k not in ('artifact_sha256','stages')}
    print(json.dumps(value,sort_keys=True,indent=2,allow_nan=False))
    return 3 if isinstance(value,dict) and (value.get('software_pilot_passed') is False or
        (args.command in ('code-aster-box','code-aster-candidate') and
         (value.get('state')!='executed' or not value.get('numerical_checks',{}).get('numerical_screen_passed')))) else 0


if __name__=='__main__':raise SystemExit(main())
