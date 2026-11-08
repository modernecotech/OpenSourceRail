"""Bounded loopback download of a project for the exact displayed city packet."""
import re
import threading
import subprocess
from pathlib import Path
from urllib.parse import unquote, urlsplit, parse_qs
from engineering.trip_dynamics.interactive import _loopback
from . import adapter

WORKERS = threading.BoundedSemaphore(1)


def handle_api(handler):
    path = unquote(urlsplit(handler.path).path)
    if not path.startswith('/api/rustgis/'):
        return False
    post=handler.command=='POST'
    if handler.command not in ('GET', 'HEAD','POST'):
        handler.respond(405, {'error':'GET or typed native-project POST required'});return True
    if not _loopback(handler, post=post):
        handler.respond(403, {'error':'Matching loopback Host and Origin required'});return True
    if path.startswith('/api/rustgis/import/'):
        if not post:handler.respond(405,{'error':'POST a native project to import'});return True
        return _import(handler,path)
    if post:
        handler.respond(405,{'error':'POST the native-project import endpoint'});return True
    retained=re.fullmatch(r'/api/rustgis/imports/([a-f0-9]{32})/(manifest|comparison|failure)\.json',path)
    if retained:
        try:
            folder=adapter._local(Path(handler.root),'build/rustgis-imports/'+retained[1])
            file=adapter._local(folder,retained[2]+'.json')
            if not file.is_file() or file.stat().st_size>2*1024**2:raise ValueError('Known retained native import record required')
            handler.respond(200,file.read_bytes(),'application/json')
        except (OSError,ValueError) as exc:handler.respond(404,{'error':str(exc)})
        return True
    study=re.fullmatch(r'/api/rustgis/study/([a-f0-9]{32})/([a-f0-9]{64})\.zip',path)
    match = re.fullmatch(r'/api/rustgis/([a-z0-9]+(?:-[a-z0-9]+)*)/([a-f0-9]{64})\.zip', path)
    if not match and not study:
        handler.respond(404, {'error':'Exact city and packet required'});return True
    if not WORKERS.acquire(blocking=False):
        handler.respond(503, {'error':'Another GIS export is active; retry shortly'});return True
    try:
        if study:
            study_id,packet_id=study.groups()
            service=getattr(handler.server,'city_studies',None)
            if service is None:raise ValueError('Local city study service required')
            packet,*_=adapter.study_input(study_id,root=handler.root,service=service)
        else:
            slug, packet_id = match.groups()
            context = adapter.inputs(handler.root)
            packet, *_ = adapter.city_input(slug, context)
        if packet['packet_id'] != packet_id:
            handler.respond(409, {'error':'Displayed city changed; reload before exporting'});return True
        result = (adapter.export_study(study_id,root=handler.root,service=service) if study else
            adapter.export(slug, root=handler.root, context=context))
        handler.respond(200, Path(result['archive']).read_bytes(), 'application/zip')
    except (OSError, ValueError, KeyError, TimeoutError, subprocess.SubprocessError) as exc:
        handler.respond(503, {'error':str(exc), 'physical_accepted':False})
    finally:
        WORKERS.release()
    return True


def _import(handler,path):
    from . import revision
    match=re.fullmatch(r'/api/rustgis/import/([a-z0-9]+(?:-[a-z0-9]+)*)/([a-f0-9]{64})',path)
    if not match:handler.respond(404,{'error':'Exact city and displayed GIS packet required'});return True
    length=handler.headers.get('Content-Length','')
    if (handler.headers.get('Content-Type','').split(';')[0] not in ('application/json','application/vnd.rustgis+json') or
            not length.isdecimal() or not 0<int(length)<=revision.MAX_PROJECT):
        handler.respond(413,{'error':'Upload one bounded .rgis JSON file','maximum_bytes':revision.MAX_PROJECT});return True
    if not WORKERS.acquire(blocking=False):
        handler.respond(503,{'error':'Another native GIS operation is active; retry shortly'});return True
    try:
        fields=parse_qs(urlsplit(handler.path).query,keep_blank_values=True,max_num_fields=5)
        if (set(fields)-{'actor','reason','data_crs','base_study_id'} or
                any(len(v)!=1 for v in fields.values()) or not {'actor','reason','data_crs'}<=set(fields)):
            raise ValueError('Named actor, reason and explicit data CRS required')
        service=getattr(handler.server,'city_studies',None)
        if service is None:raise ValueError('Mapped-city calculation service unavailable')
        slug,packet_id=match.groups()
        connection=getattr(handler,'connection',None)
        timeout=connection.gettimeout() if connection is not None else None
        try:
            if connection is not None:connection.settimeout(15)
            raw=handler.rfile.read(int(length))
        finally:
            if connection is not None:connection.settimeout(timeout)
        if len(raw)!=int(length):raise ValueError('Complete native project upload required')
        record=revision.import_project(raw,slug,packet_id,root=handler.root,
            actor=fields['actor'][0],reason=fields['reason'][0],data_crs=fields['data_crs'][0],
            study_id=fields.get('base_study_id',[None])[0],service=service)
        result=dict(import_id=record['import_id'],import_evaluation_id=record['evaluation_id'],
            state=record['execution'],comparison=record['comparison'],job=record['job'],
            evidence_url='/api/rustgis/imports/'+record['import_id']+'/manifest.json',**revision.FLAGS)
        handler.respond(200 if record['execution']=='no-op' else 202,result)
    except (OSError,ValueError,KeyError,TypeError,subprocess.SubprocessError) as exc:
        retained=getattr(exc,'import_id',None)
        handler.respond(400,dict(error=str(exc),input_retained=bool(retained),
            evidence_url='/api/rustgis/imports/'+retained+'/failure.json' if retained else None,**revision.FLAGS))
    finally:WORKERS.release()
    return True
