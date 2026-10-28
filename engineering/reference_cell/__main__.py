"""Sourced reference-cell research tools; no automatic hardware or business release."""
import argparse,json
from pathlib import Path
from . import ROOT
from . import coordinator as c, vehicles
from engineering.railway_twin.pipeline import IncompleteDesign


def main():
    p=argparse.ArgumentParser(description=__doc__);s=p.add_subparsers(dest='action',required=True)
    s.add_parser('plan')
    run=s.add_parser('run');run.add_argument('--state',type=Path,default=Path('build/reference-cell'));run.add_argument('--max-cases',type=int,default=2)
    verify=s.add_parser('verify');verify.add_argument('state',type=Path);verify.add_argument('--require-complete',action='store_true')
    pub=s.add_parser('publish');pub.add_argument('state',type=Path)
    s.add_parser('verify-publication')
    ui=s.add_parser('workbench');ui.add_argument('--state',type=Path,default=Path('build/reference-cell'));ui.add_argument('--port',type=int,default=8770)
    cad=s.add_parser('cad');cad.add_argument('--vehicle',choices=vehicles.variants(),default='V1');cad.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    try:
        if a.action=='plan':v=c.plan()
        elif a.action=='run':
            r=c.run(a.state,max_cases=a.max_cases);v=dict(run_id=r['run_id'],cases=len(r['cases']),pending=len(r['pending']),engineering_complete=False)
        elif a.action=='verify':v=c.verify(a.state,strict=a.require_complete)
        elif a.action=='publish':v=c.publish(a.state)
        elif a.action=='verify-publication':v=c.verify_publication()
        elif a.action=='cad':
            from . import geometry
            v=geometry.export_ifc(vehicles.evaluate(a.vehicle),a.output)
        else:
            from .server import serve
            serve(a.state,port=a.port);return 0
    except IncompleteDesign as e:
        print(json.dumps(dict(complete=False,open_items=e.blockers)));return 3
    print(json.dumps(v,indent=2,allow_nan=False));return 0


if __name__=='__main__':raise SystemExit(main())
