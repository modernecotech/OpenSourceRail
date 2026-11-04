"""Bounded, loopback-only outline calculations inside the existing Workbench."""
from pathlib import Path
import json
import re
import threading
from urllib.parse import unquote, urlsplit
from uuid import uuid4

from engineering.station_rail.common import digest
from engineering.trip_dynamics.interactive import _loopback
from . import coordinator

MAX_REQUEST_BYTES=16*1024
MAX_STORE_BYTES=256*1024**2
_lock=threading.Lock()
ARTIFACTS={'summary.json','result.json','manifest.json','performance.json'}


def _request(raw):
    def pairs(items):
        value={}
        for key,item in items:
            if key in value:raise ValueError('Duplicate input key')
            value[key]=item
        return value
    value=json.loads(raw,object_pairs_hook=pairs,
        parse_constant=lambda x:(_ for _ in ()).throw(ValueError('Finite JSON required')))
    if not isinstance(value,dict) or set(value)-{'brief','variables','pricing_scenario'}:raise ValueError('Brief and optional bounded variables/pricing scenario required')
    # Service-search validation supplies the numerical and variable-count caps.
    return value


def handle_api(handler):
    path=unquote(urlsplit(handler.path).path)
    if path=='/api/outline-approaches':
        if handler.command not in ('GET','HEAD'):
            handler.respond(405,{'error':'Read-only approach catalogue'});return True
        if not _loopback(handler,post=False):
            handler.respond(403,{'error':'Matching loopback Host required'});return True
        from .approaches import catalogue
        handler.respond(200,catalogue(root=handler.root));return True
    if path!='/api/outline-study' and not path.startswith('/api/outline-study/'):
        return False
    post=handler.command=='POST'
    if handler.command not in ('GET','HEAD','POST'):
        handler.respond(405,{'error':'GET or POST required'});return True
    if not _loopback(handler,post=post):
        handler.respond(403,{'error':'Matching loopback Host and Origin required'});return True
    store=Path(handler.root)/'build/outline-workbench'
    try:
        if post:
            if path!='/api/outline-study':raise ValueError('POST the study endpoint')
            if handler.headers.get('Content-Type','').split(';')[0]!='application/json':raise ValueError('application/json required')
            length=handler.headers.get('Content-Length','')
            if not length.isdecimal() or not 0<int(length)<=MAX_REQUEST_BYTES:raise ValueError('Bounded Content-Length required')
            value=_request(handler.rfile.read(int(length)))
            if not _lock.acquire(blocking=False):
                handler.respond(429,{'error':'One bounded outline study is already running'});return True
            try:
                if any(p.is_symlink() for p in (store,*store.parents)):
                    raise ValueError('Ordinary private output directory and ancestors required')
                store.mkdir(parents=True,exist_ok=True)
                if sum(p.stat().st_size for p in store.rglob('*') if p.is_file())>=MAX_STORE_BYTES:
                    handler.respond(507,{'error':'Outline output budget reached; preserve/export runs before cleanup'});return True
                output=store/uuid4().hex
                manifest=coordinator.run(output,brief=value.get('brief'),variables=value.get('variables'),root=handler.root,pricing_scenario=value.get('pricing_scenario'))
                response=json.loads((output/'summary.json').read_bytes())
                response['artifact_url']='/api/outline-study/'+output.name+'/'
                response['manifest_id']=manifest['manifest_id']
                handler.respond(200,response)
            finally:_lock.release()
            return True
        suffix=path.removeprefix('/api/outline-study/')
        if path=='/api/outline-study':
            from . import supply_economics
            handler.respond(200,dict(brief=coordinator.DEFAULT_BRIEF,variables=coordinator.DEFAULT_VARIABLES,
                pricing_scenarios=list(supply_economics.SCENARIOS),default_pricing_scenario=supply_economics.policy(handler.root)['default_scenario'],
                workflow=['requirements','generate','compare','accept outline','detail and validate','prepare delivery'],**coordinator.FLAGS))
            return True
        parts=suffix.split('/')
        if len(parts)!=2 or not re.fullmatch('[0-9a-f]{32}',parts[0]) or parts[1] not in ARTIFACTS:
            raise ValueError('Known immutable study and artifact required')
        output=store/parts[0]
        if any(p.is_symlink() for p in (output,*output.parents)) or any((output/n).is_symlink() for n in ARTIFACTS):raise ValueError('Linked study artifact refused')
        manifest=coordinator.verify(output,root=handler.root,replay=False)
        raw=(output/parts[1]).read_bytes()
        if parts[1]!='manifest.json' and digest(output/parts[1])!=manifest['files_sha256'][parts[1]]:
            raise ValueError('Study artifact differs')
        handler.respond(200,raw);return True
    except (ValueError,KeyError,TypeError,OSError) as exc:
        handler.respond(400,{'error':str(exc),'physical_accepted':False});return True
