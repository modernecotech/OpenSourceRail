#!/usr/bin/env python3
"""Build, validate, edit and serve the owner/builder planning workspace."""
import argparse
import importlib.util
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from engineering.ferrite_maglev import platform_publication as platform

def main():
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='action',required=True)
    sub.add_parser('build');sub.add_parser('check')
    compile=sub.add_parser('compile');compile.add_argument('edits',type=Path);compile.add_argument('--output',type=Path,required=True)
    serve=sub.add_parser('serve');serve.add_argument('--port',type=int,default=8090)
    args=parser.parse_args()
    if args.action=='build':platform.publish();print('Built current owner/builder planning revisions')
    elif args.action=='check':print(json.dumps(platform.verify()))
    elif args.action=='compile':
        from engineering.ferrite_maglev import candidate_magnetics
        candidate=candidate_magnetics.definition()
        value=platform.compile_edits(json.loads(args.edits.read_bytes()),args.output,configuration_sha256=candidate['configuration_sha256'])
        print(json.dumps(dict(revision=value['planning_revision_sha256'],configuration=value['configuration_sha256'],output=str(args.output),physical_release=False)))
    else:
        platform.verify(recompute=False)
        from http.server import ThreadingHTTPServer
        spec=importlib.util.spec_from_file_location('osr_planning_handler',ROOT/'tools/automation/maglev-workbench.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        server=ThreadingHTTPServer(('127.0.0.1',args.port),module.Handler)
        print(f'Owner/builder planning: http://127.0.0.1:{server.server_port}/docs/workbench/planning/',flush=True)
        try:server.serve_forever()
        except KeyboardInterrupt:pass
        finally:server.server_close()

if __name__=='__main__':main()
