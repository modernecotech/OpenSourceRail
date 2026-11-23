"""Loopback Workbench entry point for one bounded Airport scenario."""
import json
from threading import BoundedSemaphore

from engineering.performance import disk_reservation
from engineering.trip_dynamics.interactive import _loopback
from . import scenario

ACTIVE = BoundedSemaphore(1)


def serve(handler):
    if not _loopback(handler, post=True):
        return handler.respond(403, {"error": "Use the local Workbench origin"})
    if handler.headers.get_content_type() != "application/json":
        return handler.respond(415, {"error": "Send a JSON scenario"})
    size = handler.headers.get("Content-Length", "")
    if not size.isdecimal() or not 0 < int(size) <= 2048:
        return handler.respond(413, {"error": "One bounded scenario is required"})
    try:
        body = json.loads(handler.rfile.read(int(size)))
        if not isinstance(body, dict) or set(body) not in ({"inputs"}, {"inputs", "export"}):
            raise ValueError("Supply scenario inputs and optional export")
        if type(body.get("export", False)) is not bool:
            raise ValueError("Export must be true or false")
        inputs = scenario.selections(body["inputs"])
    except (ValueError, TypeError) as exc:
        return handler.respond(400, {"error": str(exc)})
    if not ACTIVE.acquire(blocking=False):
        return handler.respond(429, {"error": "Another Airport scenario is running. Retry after completion."})
    try:
        with disk_reservation(scenario.ROOT, scenario.ROOT, "Workbench Airport calculation", 32 << 20):
            result = scenario.run_case(inputs)
            if body.get("export"):
                return handler.respond(200, scenario.dossier(result), "application/zip")
            return handler.respond(200, result)
    except (ValueError, KeyError, OSError) as exc:
        return handler.respond(422, {"error": str(exc)})
    finally:
        ACTIVE.release()
