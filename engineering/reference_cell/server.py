"""Read-only local engineering Workbench; no activation or train-control endpoint."""
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit
import json
from . import ROOT,encoded,FLAGS
from . import coordinator as c,architecture


def handler(state,root=ROOT):
    state=Path(state).resolve();root=Path(root).resolve();c.verify(state,root=root)
    index=c._read(state/'latest.json');cases={(r['request']['vehicle_id'],str(int(r['request']['distance_m']))):state/r['path'] for r in index['cases']}
    case_bytes={key:path.read_bytes() for key,path in cases.items()}
    vehicle_bytes={key:(state/'vehicles'/(key+'.json.gz')).read_bytes() for key in {key[0] for key in cases}}
    # Immutable response snapshots prevent post-validation file edits from being served.
    web=root/'engineering/reference_cell/web'
    summary=dict(schema='osr-reference-cell-workbench/1',cases=[r['summary'] for r in index['cases']],pending=index['pending'],
        architecture_records=list(architecture.defaults().records.values()),**FLAGS)
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            path=urlsplit(self.path).path;encoding=None
            if path=='/api/summary':raw=encoded(summary);kind='application/json'
            elif path.startswith('/api/case/'):
                words=path.split('/')
                if len(words)!=5 or (words[3],words[4]) not in cases:self.send_error(404);return
                raw=case_bytes[words[3],words[4]];kind='application/json';encoding='gzip'
            elif path.startswith('/api/vehicle/'):
                words=path.split('/');name=words[-1]
                if len(words)!=4 or name not in {k[0] for k in cases}:self.send_error(404);return
                raw=vehicle_bytes[name];kind='application/json';encoding='gzip'
            elif path=='/geography':
                raw=b'<!doctype html><title>v0.6 city planning</title><h1>City geography and service evaluation</h1><p>The retained 266 city geographies remain planning inputs. Current v0.6 performance, protected headway, fleet and economics remain held until validated vehicle, drive, braking and site inputs exist.</p><p>The historical planning editor does not run current v0.6 evaluation. This reference-cell Workbench is the current engineering view.</p><a href="/">Return to current reference-cell engineering</a>';kind='text/html; charset=utf-8'
            elif path in ('/','/index.html','/app.js','/app.css'):
                name='index.html' if path=='/' else path[1:];raw=(web/name).read_bytes();kind={'index.html':'text/html; charset=utf-8','app.js':'text/javascript','app.css':'text/css'}[name]
            else:self.send_error(404);return
            self.send_response(200);self.send_header('Content-Type',kind);self.send_header('Content-Length',str(len(raw)))
            if encoding:self.send_header('Content-Encoding',encoding)
            self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff');self.end_headers();self.wfile.write(raw)
        def do_POST(self):self.send_error(405,'Read-only engineering review')
        do_PUT=do_POST;do_DELETE=do_POST;do_PATCH=do_POST
        def log_message(self,*args):pass
    return Handler


def serve(state,*,root=ROOT,port=8770):
    if type(port) is not int or not 1024<=port<=65535:raise ValueError('Explicit local review port required')
    server=ThreadingHTTPServer(('127.0.0.1',port),handler(state,root))
    print(f'Reference-cell Workbench http://127.0.0.1:{port} · read-only · physical release pending',flush=True)
    try:server.serve_forever()
    finally:server.server_close()
