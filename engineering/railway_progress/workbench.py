"""Read-only current progress views; JSON inputs cannot execute transactions."""
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from urllib.parse import urlsplit
from pathlib import Path
import json
from . import ROOT,encoded,digest,identity
from . import coordinator


def handler(state,root=ROOT):
    folder=Path(state);coordinator.verify(folder,root=root,replay=False);index=coordinator._read(folder/'latest.json')
    if index['source_sha256']!=coordinator.sources(root):raise ValueError('Rebuild workbench state for current sources')
    if index['run_id']!=identity({k:v for k,v in index.items() if k not in ('run_id','new_cases')}):raise ValueError('Workbench state identity differs')
    rows={r['summary']['candidate_id']:r for r in index['cases']};vehicles={}
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            path=urlsplit(self.path).path
            try:
                if path=='/':raw=(Path(root)/'engineering/railway_progress/web/index.html').read_bytes();mime='text/html; charset=utf-8'
                elif path=='/api/summary':raw=encoded(dict(run_id=index['run_id'],cases=[r['summary'] for r in index['cases']],pending=index['pending']));mime='application/json'
                elif path.startswith('/api/cases/') and path[11:] in rows:
                    row=rows[path[11:]];value=coordinator._read(folder/row['path'])
                    if value['evaluation_id']!=identity({k:v for k,v in value.items() if k!='evaluation_id'}) or encoded(coordinator.compact(value))!=encoded(row['summary']):raise ValueError('Workbench payload differs')
                    raw=encoded(value);mime='application/json'
                elif path.startswith('/api/vehicles/') and path[14:] in coordinator.vehicles.variants():
                    key=path[14:]
                    if key not in vehicles:vehicles[key]=coordinator.vehicles.evaluate(key,root)
                    raw=encoded(vehicles[key]);mime='application/json'
                else:self.send_error(404);return
                self.send_response(200);self.send_header('Content-Type',mime);self.send_header('Cache-Control','no-store')
                self.send_header('X-Content-Type-Options','nosniff');self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw)
            except (ValueError,OSError,KeyError):self.send_error(409,'Engineering package integrity check failed')
        def do_POST(self):self.send_error(405,'Read-only engineering review')
    return Handler


def serve(state,*,port=8771,root=ROOT):
    if type(port) is not int or not 1024<=port<=65535:raise ValueError('Unprivileged local review port required')
    server=ThreadingHTTPServer(('127.0.0.1',port),handler(state,root));print(f'Continuing engineering Workbench: http://127.0.0.1:{port}',flush=True)
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close()
    return 0
