#!/usr/bin/env python3
"""Loopback, read-only primary v0.5 design review UI."""
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

    def send_head(self):
        name = unquote(urlsplit(self.path).path)
        if name == '/':
            self.send_response(303)
            self.send_header('Location', '/docs/workbench/maglev/')
            self.end_headers()
            return None
        allowed = ('/docs/workbench/maglev/', '/docs/workbench/planning/', '/docs/design-engine/ferrite-maglev/')
        exact = {'/engineering/ferrite_maglev/city-index.json', '/engineering/ferrite_maglev/city-index.md',
                 '/OpenSourceRail-Book.pdf', '/OpenSourceRail maglev station concept.png',
                 '/Vertical spiral escape chute concept.png'}
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
    args = parser.parse_args()
    from engineering.ferrite_maglev import delivery
    delivery.verify()
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f'Primary maglev Workbench: http://{args.host}:{server.server_port}/', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
