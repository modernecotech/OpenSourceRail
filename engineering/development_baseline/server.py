"""Read-only, source-bound current-design Workbench and city endpoints."""
from __future__ import annotations

import argparse
from functools import partial
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import mimetypes
from pathlib import Path
from urllib.parse import unquote, urlsplit
import webbrowser

from . import ROOT, FLAGS, WORKBENCH
from .entrypoint import (CurrentUnavailable, checked_path, check_identity, digest,
                         read_packet, selected, status)


class Handler(BaseHTTPRequestHandler):
    server_version = 'OpenSourceRailCurrent/1'

    def __init__(self, *args, root=ROOT, **kwargs):
        self.root = Path(root).resolve()
        super().__init__(*args, **kwargs)

    def respond(self, code, content, content_type='application/json; charset=utf-8'):
        if isinstance(content, (dict, list)):
            content = (json.dumps(content, sort_keys=True, allow_nan=False) + '\n').encode()
        elif isinstance(content, str):
            content = content.encode()
        self.send_response(code)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(content)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; object-src 'none'; frame-ancestors 'none'")
        self.end_headers()
        if self.command != 'HEAD':
            self.wfile.write(content)

    def hold(self, reason, code=503):
        self.respond(code, dict(schema='osr-current-api-hold/1', execution='held',
                                reason=str(reason), development_default=True, **FLAGS))

    def do_HEAD(self):
        self.do_GET()

    def city_summary(self, slug):
        from . import cities
        catalogue = cities.catalogue(root=self.root)
        entry = next((row for row in catalogue if row['slug'] == slug), None)
        if entry is None:
            raise CurrentUnavailable('Unknown selected city')
        if entry.get('execution') == 'held':
            # The v0.6 catalogue exposes preserved geography, never old city
            # performance as if it belonged to the new physical candidate.
            return cities.evaluate_city(slug, root=self.root)
        raise CurrentUnavailable('No v0.6 city performance packet is authorized; regenerate the geographic hold register')

    def do_GET(self):
        path = unquote(urlsplit(self.path).path)
        if path == '/':
            self.send_response(302)
            self.send_header('Location', '/' + WORKBENCH + '/')
            self.send_header('Cache-Control', 'no-store')
            self.end_headers()
            return
        try:
            if path == '/api/default-design':
                # Refuse a stale packet even though CLI status may usefully
                # report its selected identity alongside a publication hold.
                read_packet(self.root)
                self.respond(200, status(self.root))
                return
            if path in ('/api/campaigns/current','/api/design-space/current','/api/architectures/current','/api/adaptive/current'):
                _,publication=read_packet(self.root)
                campaign=path=='/api/campaigns/current'
                architecture=path=='/api/architectures/current'
                adaptive=path=='/api/adaptive/current'
                relative='docs/design-engine/'+('v06-optimisation' if campaign else 'v06-adaptive-design' if adaptive else 'v06-architecture' if architecture else 'v06-design-space')+'/summary.json';source=checked_path(self.root,relative)
                if publication.get('source_sha256',{}).get(relative)!=digest(source):raise CurrentUnavailable('Campaign summary lacks a current source binding')
                value=json.loads(source.read_bytes())
                schema='osr-wheel-iterative-campaign-publication/1' if campaign else 'osr-adaptive-design-summary/1' if adaptive else 'osr-railway-architecture-summary/1' if architecture else 'osr-expanded-design-space-summary/1'
                if value.get('schema')!=schema or any(value.get(k) is not False for k in ('physical_accepted','engineering_accepted','configuration_adopted','manufacturing_release','operating_release')):
                    raise CurrentUnavailable('Unaccepted research campaign required')
                self.respond(200,value)
                return
            if path == '/api/cities':
                read_packet(self.root)
                from . import cities
                value = cities.read_catalogue(root=self.root)
                check_identity(value, selected(self.root))
                self.respond(200, value)
                return
            if path.startswith('/api/city/'):
                read_packet(self.root)
                value = self.city_summary(path.removeprefix('/api/city/'))
                self.respond(503 if value.get('execution') == 'held' else 200, value)
                return
            if path.startswith('/api/'):
                self.hold('No current-design read-only endpoint exists here. Historical execution is isolated.', 410)
                return
            relative = path.lstrip('/')
            if not (relative.startswith(('docs/', 'cities/')) or relative == 'OpenSourceRail-Book.pdf'):
                self.hold('Static route unavailable', 404)
                return
            if any(part.startswith('.') for part in Path(relative).parts):
                self.hold('Static route unavailable', 404)
                return
            target = checked_path(self.root, relative)
            if target.is_dir():
                target = checked_path(self.root, str(Path(relative) / 'index.html'))
            if not target.is_file():
                self.hold('Current artifact missing; run ./osr build', 404)
                return
            # Current templates/assets are publication outputs. Validate them
            # before serving so modified scripts cannot masquerade as current.
            if relative.startswith(WORKBENCH + '/'):
                _, manifest = read_packet(self.root)
                bindings = manifest.get('workbench_files_sha256', {})
                expected = bindings.get(target.name) or bindings.get(str(target.relative_to(self.root)))
                if not expected or digest(target) != expected:
                    raise CurrentUnavailable('Current Workbench asset changed')
            self.respond(200, target.read_bytes(), mimetypes.guess_type(str(target))[0] or 'application/octet-stream')
        except (OSError, ValueError, KeyError) as exc:
            self.hold(exc)

    def do_POST(self):
        self.hold('Current Workbench is read-only. Typed, candidate-bound job adapters are required for execution.', 405)

    do_PUT = do_POST
    do_PATCH = do_POST
    do_DELETE = do_POST


def make_server(root=ROOT, host='127.0.0.1', port=8090):
    return ThreadingHTTPServer((host, port), partial(Handler, root=root))


def serve(root=ROOT, host='127.0.0.1', port=8090, open_browser=False):
    server = make_server(root=root, host=host, port=port)
    origin = 'http://%s:%s' % server.server_address
    print(origin, flush=True)
    if open_browser:
        webbrowser.open(origin)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


def main(argv=None, root=ROOT):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8090)
    parser.add_argument('--host', choices=('127.0.0.1', 'localhost', '::1'), default='127.0.0.1')
    parser.add_argument('--open', action='store_true')
    parser.add_argument('--no-browser', action='store_true', help=argparse.SUPPRESS)
    parser.add_argument('--root', type=Path, default=Path(root), help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    return serve(root=args.root, host=args.host, port=args.port, open_browser=args.open and not args.no_browser)


if __name__ == '__main__':
    raise SystemExit(main())
