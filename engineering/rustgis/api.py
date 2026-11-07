"""Bounded loopback download of a project for the exact displayed city packet."""
import re
import threading
import subprocess
from pathlib import Path
from urllib.parse import unquote, urlsplit
from engineering.trip_dynamics.interactive import _loopback
from . import adapter

WORKERS = threading.BoundedSemaphore(1)


def handle_api(handler):
    path = unquote(urlsplit(handler.path).path)
    if not path.startswith('/api/rustgis/'):
        return False
    if handler.command not in ('GET', 'HEAD'):
        handler.respond(405, {'error':'GIS exports are read-only'});return True
    if not _loopback(handler, post=False):
        handler.respond(403, {'error':'Matching loopback Host required'});return True
    match = re.fullmatch(r'/api/rustgis/([a-z0-9]+(?:-[a-z0-9]+)*)/([a-f0-9]{64})\.zip', path)
    if not match:
        handler.respond(404, {'error':'Exact city and packet required'});return True
    if not WORKERS.acquire(blocking=False):
        handler.respond(503, {'error':'Another GIS export is active; retry shortly'});return True
    try:
        slug, packet_id = match.groups()
        context = adapter.inputs(handler.root)
        packet, *_ = adapter.city_input(slug, context)
        if packet['packet_id'] != packet_id:
            handler.respond(409, {'error':'Displayed city changed; reload before exporting'});return True
        result = adapter.export(slug, root=handler.root, context=context)
        handler.respond(200, Path(result['archive']).read_bytes(), 'application/zip')
    except (OSError, ValueError, KeyError, TimeoutError, subprocess.SubprocessError) as exc:
        handler.respond(503, {'error':str(exc), 'physical_accepted':False})
    finally:
        WORKERS.release()
    return True
