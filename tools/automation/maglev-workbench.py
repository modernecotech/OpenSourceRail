#!/usr/bin/env python3
"""Loopback research Workbench with bounded private trip jobs and public evidence."""
import argparse
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import sys
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def _trip_api(self):
        if not urlsplit(self.path).path.startswith('/api/trip/'):
            return False
        if getattr(self.server, 'trip_service', None) is None:
            self.send_error(503, 'Trip service is not configured')
            return True
        from engineering.trip_dynamics.interactive import handle_api
        return handle_api(self)

    def do_GET(self):
        if not self._trip_api():
            super().do_GET()

    def do_POST(self):
        if not self._trip_api():
            self.send_error(501, 'Only the bounded trip job API accepts POST')

    def send_head(self):
        name = unquote(urlsplit(self.path).path)
        if name == '/':
            self.send_response(303)
            self.send_header('Location', '/docs/workbench/maglev/')
            self.end_headers()
            return None
        allowed = ('/docs/workbench/maglev/', '/docs/workbench/planning/', '/docs/workbench/trip/',
                   '/docs/design-engine/ferrite-maglev/', '/docs/design-engine/trip-dynamics/',
                   '/docs/design-engine/passive-suspension/', '/docs/design-engine/vehicle-optimisation/',
                   '/docs/design-engine/design-search/', '/docs/design-engine/design-search-twins/')
        exact = {'/engineering/ferrite_maglev/city-index.json', '/engineering/ferrite_maglev/city-index.md',
                 '/OpenSourceRail-Book.pdf', '/OpenSourceRail maglev station concept.png',
                 '/Vertical spiral escape chute concept.png', '/engineering/design_search/README.md',
                 '/docs/design-engine/design-search-interpretation.md', '/engineering/trip_dynamics/README.md'}
        lexical = ROOT/name.lstrip('/')
        path = lexical.resolve()
        roots = [ROOT/p.lstrip('/') for p in allowed]
        is_city = (name.startswith('/cities/catalogue/') and '/engineering/maglev/' in name
                   and path.is_relative_to(ROOT/'cities/catalogue')
                   and path.parent.name == 'maglev'
                   and path.name in {'summary.json', 'README.md', 'retained-records.json', 'manufacturing.json', 'network.svg'})
        is_city_brief = (path.is_relative_to(ROOT/'cities/catalogue')
                         and len(path.relative_to(ROOT/'cities/catalogue').parts) == 4
                         and path.name == 'README.md' and (path.parent/'city.json').is_file())
        if (path != lexical or not path.is_relative_to(ROOT) or any(part in {'.', '..'} for part in name.split('/'))
                or not (name in exact or is_city or is_city_brief or any(path.is_relative_to(p) for p in roots))):
            self.send_error(404)
            return None
        if path.is_dir() and not (path/'index.html').is_file():
            self.send_error(404)
            return None
        return super().send_head()

    def end_headers(self):
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Cache-Control', 'no-cache')
        self.send_header('Content-Security-Policy', "default-src 'self'; connect-src 'self' blob:; img-src 'self' blob:; media-src 'self' blob:; style-src 'self' 'unsafe-inline'; object-src 'none'; base-uri 'none'")
        super().end_headers()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--host', default='127.0.0.1', choices=('127.0.0.1', 'localhost'))
    parser.add_argument('--port', type=int, default=8090)
    parser.add_argument('--verify-full', action='store_true',
                        help='reproduce the full existing engineering verification before listening')
    args = parser.parse_args()
    from engineering.trip_dynamics.interface_integrity import primary_integrity
    integrity = primary_integrity(ROOT)
    if args.verify_full:
        from engineering.ferrite_maglev import delivery
        delivery.verify()
        integrity['numerical_verification_executed'] = True
    from engineering.trip_dynamics.interactive import TripService
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    server.publication_integrity = integrity
    server.trip_service = TripService(ROOT)
    print(f'Primary maglev Workbench: http://{args.host}:{server.server_port}/', flush=True)
    print(f'Trip tools: http://{args.host}:{server.server_port}/docs/workbench/trip/ · publication integrity: {integrity["state"]}', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.trip_service.close()
        server.server_close()


if __name__ == '__main__':
    main()
