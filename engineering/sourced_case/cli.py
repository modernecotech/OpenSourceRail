"""Bounded source-backed design experiments; no production transactions."""
import argparse,json
from . import ROOT
from . import coordinator


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('action',choices=['plan','run','verify','publish','verify-publication','dashboard','serve','verify-methods','publish-geometry','verify-geometry'])
    p.add_argument('--state',default='build/sourced-cell');p.add_argument('--max-cases',type=int,default=30)
    p.add_argument('--output');p.add_argument('--port',type=int,default=8772)
    a=p.parse_args(argv)
    if a.action=='plan':v=dict(cases=coordinator.plan(),qualified=False)
    elif a.action=='run':v=coordinator.run(a.state,max_cases=a.max_cases)
    elif a.action=='verify':v=coordinator.verify(a.state)
    elif a.action=='publish':v=coordinator.publish(a.state,output=a.output)
    elif a.action=='verify-publication':v=coordinator.verify_publication(output=a.output)
    elif a.action=='verify-methods':
        from . import methods
        v=methods.verify(a.output or ROOT/coordinator.OUTPUT)
    elif a.action=='publish-geometry':
        from . import geometry
        v=geometry.publish(a.state,a.output or ROOT/coordinator.OUTPUT)
    elif a.action=='verify-geometry':
        from . import geometry
        v=geometry.verify_publication(a.output or ROOT/coordinator.OUTPUT)
    elif a.action=='dashboard':
        from . import closure
        v=closure.build(a.state)
    else:
        from .workbench import serve
        serve(a.state,port=a.port);return
    print(json.dumps(v,indent=2,sort_keys=True))


if __name__=='__main__':main()
