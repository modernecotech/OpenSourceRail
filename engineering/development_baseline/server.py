"""Source-bound v0.6 Workbench plus bounded, separate trip-research jobs."""
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
from .entrypoint import (CurrentUnavailable, IDS, checked_path, check_identity, digest,
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
        from engineering.rustgis.api import handle_api as gis_api
        if gis_api(self):
            return
        from engineering.outline.city_atlas_api import handle_api as atlas_api
        if atlas_api(self):
            return
        from engineering.outline.city_jobs import handle_api as city_api
        if city_api(self):
            return
        from engineering.outline.interactive import handle_api as outline_api
        if outline_api(self):
            return
        from engineering.trip_dynamics.interactive import handle_api
        if handle_api(self):
            return
        if path == '/':
            self.send_response(302)
            self.send_header('Location', '/' + WORKBENCH + '/')
            self.send_header('Cache-Control', 'no-store')
            self.end_headers()
            return
        try:
            if path == '/api/v07/door-module':
                from engineering.vehicle_parts.door_module import build
                self.respond(200, build(root=self.root))
                return
            if path == '/api/default-design':
                # The selected bundle is independently source checked. A
                # stale integrated publication remains a visible hold, while
                # the Workbench can still expose current, city-scoped inputs.
                self.respond(200, status(self.root))
                return
            if path == '/api/portfolios/current':
                from . import portfolio_view
                _, publication = read_packet(self.root)
                self.respond(200, portfolio_view.read(self.root, publication, selected(self.root)))
                return
            research_routes={
                '/api/campaigns/current':('v06-optimisation','osr-wheel-iterative-campaign-publication/1'),
                '/api/design-space/current':('v06-design-space','osr-expanded-design-space-summary/1'),
                '/api/architectures/current':('v06-architecture','osr-railway-architecture-summary/1'),
                '/api/adaptive/current':('v06-adaptive-design','osr-adaptive-design-summary/1'),
                '/api/generative/current':('generative-structure','osr-generative-structure-summary/1'),
                '/api/railway/current':('coupled-railway','osr-coupled-railway-summary/1')}
            if path in research_routes:
                _,publication=read_packet(self.root)
                folder,schema=research_routes[path]
                relative='docs/design-engine/'+folder+'/summary.json';source=checked_path(self.root,relative)
                if publication.get('source_sha256',{}).get(relative)!=digest(source):raise CurrentUnavailable('Campaign summary lacks a current source binding')
                value=json.loads(source.read_bytes())
                if value.get('schema')!=schema or any(value.get(k) is not False for k in ('physical_accepted','engineering_accepted','configuration_adopted','manufacturing_release','operating_release')):
                    raise CurrentUnavailable('Unaccepted research campaign required')
                if path in ('/api/generative/current','/api/railway/current') and (value.get('selected_reference_changed') is not False or value.get('integrated_selection') is not None):
                    raise CurrentUnavailable('Generative research cannot select an integrated replacement')
                self.respond(200,value)
                return
            if path == '/api/cities':
                from . import cities
                baseline = selected(self.root)
                value = dict(schema='osr-workbench-city-options/1',
                    family='wheel_rail_vehicle_reference',
                    selection_id=baseline['selection_id'],
                    **{key: baseline['vehicle'][key] for key in IDS},
                    development_default=True, execution='source-geography',
                    performance_evaluated=False, cities=cities.catalogue(root=self.root),
                    **FLAGS)
                self.respond(200, value)
                return
            if path.startswith('/api/city/'):
                value = self.city_summary(path.removeprefix('/api/city/'))
                check_identity(value, selected(self.root))
                self.respond(503 if value.get('execution') == 'held' else 200, value)
                return
            if path.startswith('/api/'):
                self.hold('No current-design read-only endpoint exists here. Historical execution is isolated.', 410)
                return
            relative = path.lstrip('/')
            if relative == 'docs/workbench/maglev' or relative.startswith('docs/workbench/maglev/'):
                self.hold('This interface is not part of the selected v0.6 Workbench.', 410)
                return
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
            served_relative = target.relative_to(self.root).as_posix()
            if served_relative.startswith(('docs/design-engine/reconciled-pilot/','docs/design-engine/reconciled-pilot-no-store/','docs/design-engine/reconciled-pilot-bogie-detail/')):
                from engineering.railway_closure.web_assets import verify_asset
                verify_asset(self.root,served_relative,target)
            if served_relative.startswith('docs/design-engine/station-cycle/'):
                from engineering.station_cycle.web_assets import verify_asset
                verify_asset(self.root,served_relative,target)
            if served_relative.startswith('docs/design-engine/station-pair/'):
                from engineering.station_pair.web_assets import verify_asset
                verify_asset(self.root,served_relative,target)
            if served_relative.startswith('docs/design-engine/vehicle-parts/'):
                from engineering.vehicle_parts.web_assets import verify_asset
                verify_asset(self.root,served_relative,target)
            if served_relative.startswith('docs/workbench/trip/'):
                self.server.trip_service.verify_ui_asset(served_relative, target)
            # Current templates/assets are publication outputs. Validate them
            # before serving so modified scripts cannot masquerade as current.
            if relative.startswith(WORKBENCH + '/'):
                from engineering.outline.city_atlas_api import ASSETS,verify_asset
                if target.name in ASSETS:
                    verify_asset(self.root,target.name,target)
                else:
                    # Static application files are mirrored from this
                    # authoritative source tree. Their integrity does not
                    # depend on the unrelated engineering dossier being
                    # current, but both copies must match exactly.
                    source=checked_path(self.root,'engineering/development_baseline/web/'+target.name)
                    if (target.name not in ('index.html','app.js','app.css')
                            or not source.is_file() or digest(target)!=digest(source)):
                        raise CurrentUnavailable('Workbench asset differs from its authoritative source')
            self.respond(200, target.read_bytes(), mimetypes.guess_type(str(target))[0] or 'application/octet-stream')
        except (OSError, ValueError, KeyError) as exc:
            self.hold(exc)

    def do_POST(self):
        from engineering.rustgis.api import handle_api as gis_api
        if gis_api(self):
            return
        from engineering.outline.city_jobs import handle_api as city_api
        if city_api(self):
            return
        from engineering.outline.interactive import handle_api as outline_api
        if outline_api(self):
            return
        from engineering.trip_dynamics.interactive import handle_api
        if handle_api(self):
            return
        self.hold('Current Workbench is read-only. Typed, candidate-bound job adapters are required for execution.', 405)

    do_PUT = do_POST
    do_PATCH = do_POST
    do_DELETE = do_POST


class WorkbenchHTTPServer(ThreadingHTTPServer):
    def __init__(self, address, handler, *, root, city_study_store=None,
                 trip_store=None,city_study_workers=1,city_resource_ledger=None):
        from engineering.trip_dynamics.interactive import TripService
        from engineering.outline.city_jobs import CityStudyService
        from engineering.outline.city_resources import DEFAULT_LEDGER
        self.root = Path(root).resolve()
        self.trip_service = None
        self.city_studies = None
        try:
            self.trip_service = TripService(self.root) if trip_store is None else TripService(
                self.root,output_root=trip_store)
            self.city_studies = CityStudyService(self.root,store=city_study_store,max_workers=city_study_workers,
                resource_ledger=city_resource_ledger or DEFAULT_LEDGER,minimum_free_gib=20.0)
            super().__init__(address, handler)
        except BaseException:
            try:
                if getattr(self, 'socket', None) is not None:
                    super().server_close()
            finally:
                if self.trip_service is not None:
                    self.trip_service.close()
                if self.city_studies is not None:
                    self.city_studies.close()
            raise

    def server_close(self):
        try:
            super().server_close()
        finally:
            city_studies = getattr(self, 'city_studies', None)
            if city_studies is not None:
                city_studies.close()
            service = getattr(self, 'trip_service', None)
            if service is not None:
                service.close()


def make_server(root=ROOT, host='127.0.0.1', port=8090,
                city_study_store=None, trip_store=None,city_study_workers=1,city_resource_ledger=None):
    return WorkbenchHTTPServer((host, port), partial(Handler, root=root), root=root,
        city_study_store=city_study_store,trip_store=trip_store,
        city_study_workers=city_study_workers,city_resource_ledger=city_resource_ledger)


def serve(root=ROOT, host='127.0.0.1', port=8090, open_browser=False,
          city_study_store=None, trip_store=None,city_study_workers=1,city_resource_ledger=None):
    server = make_server(root=root, host=host, port=port,
        city_study_store=city_study_store,trip_store=trip_store,
        city_study_workers=city_study_workers,city_resource_ledger=city_resource_ledger)
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
    parser.add_argument('--city-study-store', type=Path,
        help='Optional bounded city-study output directory outside the source checkout')
    parser.add_argument('--city-study-workers',type=int,choices=(1,2),default=1,
        help='Maximum simultaneous bounded analytic city workers')
    parser.add_argument('--city-resource-ledger',type=Path,
        help='Optional shared external analytic-worker reservation ledger')
    parser.add_argument('--trip-store', type=Path,
        help='Optional trip-research output directory outside the source checkout')
    args = parser.parse_args(argv)
    return serve(root=args.root, host=args.host, port=args.port,
                 open_browser=args.open and not args.no_browser,
                 city_study_store=args.city_study_store,
                 trip_store=args.trip_store,city_study_workers=args.city_study_workers,
                 city_resource_ledger=args.city_resource_ledger)


if __name__ == '__main__':
    raise SystemExit(main())
