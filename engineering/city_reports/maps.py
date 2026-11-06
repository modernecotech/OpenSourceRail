"""Deterministic geographic drawings and WGS84 GIS layers for a verified atlas.

The caller authenticates the atlas packet and its source SHA256 before calling.
Context is ignored unless ``context_verified=True`` explicitly records the
caller's successful verification against ``packet.map_context.sha256``. No tiles,
network requests, numerical evaluations or historical engineering results occur.
Selected routes retain every coordinate. Only background context is generalized
at 0.8 drawing pixels; two-decimal SVG coordinates are presentation rounding.
GIS retains source coordinates, chainages, IDs and unlocated requirements.
"""
from bisect import bisect_right
from copy import deepcopy
from html import escape
import json
from math import cos, floor, isfinite, log10, pi
import re
import unicodedata


PALETTE = ('#176c9c', '#b04a40', '#527c30', '#8754a0', '#bd761d', '#168078', '#a34274')
RELEASE_FLAGS = ('engineering_accepted', 'physical_accepted', 'operating_release',
    'manufacturing_release', 'movement_authority', 'procurement_approved',
    'procurement_ready', 'physical_journey_completed', 'physical_reference_changed',
    'selected_reference_changed', 'installed_mass_complete', 'timetable_qualified',
    'independent_braking_qualified', 'business_records_submitted')


def natural_key(value):
    return tuple((1, int(s)) if s.isdigit() else (0, s.casefold())
                 for s in re.split(r'(\d+)', str(value)))


def _position(row):
    p = row.get('coordinates')
    if not isinstance(p, (list, tuple)) or len(p) != 2:
        p = [row.get('lon'), row.get('lat')]
    if not _point_ok(p):
        raise ValueError('Finite WGS84 point required')
    return list(p)


def _point_ok(p):
    return (isinstance(p, (list, tuple)) and len(p) == 2
            and all(type(v) in (int, float) and isfinite(v) for v in p)
            and -180 <= p[0] <= 180 and -90 <= p[1] <= 90)


def _lines(packet):
    if packet.get('schema') != 'osr-city-atlas/1' or not packet.get('packet_id'):
        raise ValueError('Source-bound osr-city-atlas/1 packet required')
    if any(packet.get(k) not in (None, False) for k in RELEASE_FLAGS):
        raise ValueError('City map cannot grant physical or operating release')
    rows = packet.get('lines', [])
    if not rows or len({r['line_id'] for r in rows}) != len(rows):
        raise ValueError('Nonempty unique selected line identities required')
    out = []
    # Preserve current UI colours, which are assigned in packet order. Sort the
    # resulting rows naturally without changing those colours for line-10 etc.
    for i, row in enumerate(rows):
        if len(row.get('coordinates', [])) < 2 or not all(map(_point_ok, row['coordinates'])):
            raise ValueError('Explicit selected route coordinates required')
        colour = row.get('colour', row.get('color', ''))
        if not re.fullmatch(r'#[0-9a-fA-F]{6}', colour):
            colour = PALETTE[i % len(PALETTE)]
        out.append((row, colour))
    return sorted(out, key=lambda item: natural_key(item[0]['line_id']))


def line_label(line):
    return line.get('name') or re.sub(r'^line[-_ ]', 'Line ', str(line['line_id']), flags=re.I)


def station_label(line, stop, index):
    """Display references are indices, not invented surveyed station names."""
    if stop.get('name'):
        return str(stop['name'])
    ref = re.sub(r'^line[-_ ]', 'L', str(line['line_id']), flags=re.I)
    return f'{ref}/{index + 1:02d}'


def clip_route(coordinates, chainages_m, start_m, end_m):
    """Clip at declared chainages, preserving interior vertices and continuity.

    Platform intervals can extend outside the route; drawable geometry is clipped
    while the GIS properties retain the full original interval. Civil exporters
    separately reject runs outside the declared route domain (0.05 m tolerance).
    """
    chain = chainages_m
    if (len(coordinates) < 2 or len(chain) != len(coordinates)
            or not all(type(x) in (int, float) and isfinite(x) for x in chain)
            or chain[0] != 0 or any(b < a for a, b in zip(chain, chain[1:]))
            or chain[-1] <= 0):
        raise ValueError('Monotonic source coordinate_chainages_m required')
    if not all(type(x) in (int, float) and isfinite(x) for x in (start_m, end_m)) or end_m < start_m:
        raise ValueError('Ordered finite clipping interval required')
    a, b = max(0., start_m), min(chain[-1], end_m)
    if a > b:
        return []

    def point(at):
        if at == chain[-1]:
            return list(coordinates[-1])
        i = min(len(chain) - 2, max(0, bisect_right(chain, at) - 1))
        f = (at - chain[i]) / (chain[i + 1] - chain[i]) if chain[i + 1] > chain[i] else 0.
        return [coordinates[i][k] + f * (coordinates[i + 1][k] - coordinates[i][k]) for k in (0, 1)]

    return [point(a), *[list(p) for p, at in zip(coordinates, chain) if a < at < b], point(b)]


def geojson_layers(packet):
    """Return named FeatureCollections, all bound to one packet and selection.

    Layers: routes, stations, platforms, original_access_markers, interchanges,
    civil_segments, access_connectors, unlocated_requirements. The last layer uses
    valid GeoJSON null geometry; quantities do not imply geographically sited
    depots, substations, chargers or energy supply equipment. Route intersections
    are never inferred to be interchanges. No input is mutated.
    """
    lines = _lines(packet)
    meta = dict(packet_id=packet['packet_id'], identity=deepcopy(packet.get('identity', {})),
                evidence_maturity='calculated-outline', physical_acceptance='open')
    layers = {k: dict(type='FeatureCollection', name=k, **deepcopy(meta), features=[]) for k in
              ('routes', 'stations', 'platforms', 'original_access_markers', 'interchanges',
               'civil_segments', 'access_connectors', 'unlocated_requirements')}

    def add(layer, fid, geometry, properties):
        layers[layer]['features'].append(dict(type='Feature', id=str(fid), geometry=deepcopy(geometry),
            properties=dict(packet_id=packet['packet_id'], **deepcopy(properties))))

    def geom(kind, points):
        return dict(type=kind, coordinates=points)

    by_id = {l['line_id']: l for l, _ in lines}
    for line, colour in lines:
        lid = line['line_id']
        props = dict(line_id=lid, label=line_label(line), colour=colour,
            selection_role='selected', service_evaluation_id=line.get('service_evaluation_id'))
        add('routes', lid, geom('LineString', line['coordinates']), props)
        for i, stop in enumerate(line.get('operational_stops', [])):
            add('stations', stop['id'], geom('Point', _position(stop)),
                {**props, **stop, 'label': station_label(line, stop, i)})
        for stop in line.get('original_stops', []):
            add('original_access_markers', stop['id'], geom('Point', _position(stop)),
                {**props, **stop, 'role': 'original-access-marker'})
        for comp in line.get('station_complexes', []):
            sid = comp['operational_stop_id']
            for i, interval in enumerate(comp.get('boarding_platform_intervals_m', [])):
                coords = clip_route(line['coordinates'], line['coordinate_chainages_m'], *interval)
                if coords:
                    add('platforms', f'{sid}:platform:{i}', geom('LineString', coords),
                        dict(**props, operational_stop_id=sid, declared_interval_m=interval,
                             geometry_basis='Declared chainage envelope on route centreline; unverified'))
            for i, conn in enumerate(comp.get('access_connectors', [])):
                points = [conn['from_coordinates'], conn['to_coordinates']]
                if not all(map(_point_ok, points)):
                    raise ValueError('Explicit access connector endpoints required')
                add('access_connectors', f'{sid}:access:{i}', geom('LineString', points),
                    dict(**props, **conn, operational_stop_id=sid,
                         actual_accessible_path_surveyed=False))
    for row in packet.get('interchanges', []):
        if any(lid not in by_id for lid in row.get('lines', [])):
            raise ValueError('Interchange references another candidate line')
        add('interchanges', row['id'], geom('Point', _position(row)), row)
    for i, run in enumerate(packet.get('civil', {}).get('quantities', {}).get('runs', [])):
        if run['line_id'] not in by_id:
            raise ValueError('Civil run references another candidate line')
        line = by_id[run['line_id']]
        chain = line['coordinate_chainages_m']
        if run['from_m'] < -.05 or run['to_m'] > chain[-1] + .05:
            raise ValueError('Civil run lies outside selected chainage domain')
        coords = clip_route(line['coordinates'], chain, run['from_m'], run['to_m'])
        add('civil_segments', f'{run["line_id"]}:civil:{i:05d}', geom('LineString', coords),
            dict(**run, geometry_basis='Exact selected route clipped at declared source chainages'))
    resources = packet.get('resources', {})
    quantities = {k: v for k, v in resources.items() if any(s in k.lower() for s in ('depot', 'energy', 'charg', 'power'))}
    if quantities:
        add('unlocated_requirements', 'resource-requirements', None,
            dict(quantities=quantities, location_status='unlocated', site_count=None,
                 note='Quantities do not establish site locations or number of sites'))
    for ledger in ('capital_lines', 'lifecycle_lines'):
        for row in packet.get('costs', {}).get(ledger, []):
            text = (str(row.get('key', '')) + ' ' + str(row.get('scope', ''))).lower()
            if any(s in text for s in ('depot', 'energy', 'charg', 'power', 'traction-feed')):
                add('unlocated_requirements', f'{ledger}:{row.get("line_id", row.get("key"))}', None,
                    dict(source_ledger=ledger, source_record=row, location_status='unlocated',
                         site_count=None, note='Equipment siting and connections remain design requirements'))
    if not layers['unlocated_requirements']['features']:
        add('unlocated_requirements', 'depot-energy-siting', None,
            dict(location_status='unlocated', quantities=None, site_count=None,
                 note='Depot and energy equipment locations/quantities not established in this packet'))
    return layers


class Projection:
    """North-up local equirectangular projection with equal metres/pixel axes.

    The 111320 m/degree and cosine longitude approximation matches the current
    atlas UI. It is appropriate for city context, not surveying or engineering.
    """
    def __init__(self, points, box):
        self.west = min(p[0] for p in points)
        self.east = max(p[0] for p in points)
        self.south = min(p[1] for p in points)
        self.north = max(p[1] for p in points)
        self.lon_m = 111320 * max(.01, cos((self.north + self.south) / 2 * pi / 180))
        w = max(1., (self.east - self.west) * self.lon_m)
        h = max(1., (self.north - self.south) * 111320)
        x, y, bw, bh = box
        self.pixels_per_m = min(bw / w, bh / h)
        self.left = x + (bw - w * self.pixels_per_m) / 2
        self.top = y + (bh - h * self.pixels_per_m) / 2

    def __call__(self, p):
        return (self.left + (p[0] - self.west) * self.lon_m * self.pixels_per_m,
                self.top + (self.north - p[1]) * 111320 * self.pixels_per_m)


def scale_length(pixels_per_m, target_px=140):
    """Return a 1/2/5 km scale bar fitting target_px, in metres."""
    metres = target_px / pixels_per_m
    base = 10 ** floor(log10(metres))
    return max(v * base for v in (.1, .2, .5, 1, 2, 5) if v * base <= metres)


def _simplify(points, tolerance=.8):
    # Iterative Ramer-Douglas-Peucker in drawing space; backgrounds only.
    if len(points) < 3:
        return points
    keep = {0, len(points) - 1}
    stack = [(0, len(points) - 1)]
    while stack:
        a, b = stack.pop()
        x, y = points[a]
        dx, dy = points[b][0] - x, points[b][1] - y
        den = dx * dx + dy * dy
        far, index = tolerance * tolerance, None
        for i in range(a + 1, b):
            px, py = points[i]
            t = max(0., min(1., ((px - x) * dx + (py - y) * dy) / den)) if den else 0.
            dist = (px - x - t * dx) ** 2 + (py - y - t * dy) ** 2
            if dist > far:
                far, index = dist, i
        if index is not None:
            keep.add(index)
            stack.extend(((a, index), (index, b)))
    return [points[i] for i in sorted(keep)]


def render(packet, context=None, *, context_verified=False, width=1400, height=1050):
    """Render a standalone static SVG; authentication is the caller's duty.

    Geographic context is only used with an explicit True verification flag.
    Full IDs remain in SVG titles/metadata and GIS, never shortened source data.
    Dense station labels are collision culled; marker positions never move.
    """
    if not (900 <= width <= 5000 and 750 <= height <= 5000):
        raise ValueError('Map dimensions must be 900..5000 by 750..5000')
    rows = _lines(packet)
    layers = geojson_layers(packet)
    context = context if context_verified is True else None
    sidebar = 266
    mx, my, mw, mh = 28, 146, width - sidebar - 80, height - 280
    project = Projection([p for line, _ in rows for p in line['coordinates']],
                         (mx + 45, my + 35, mw - 90, mh - 90))
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" fill="#253c48" role="img" aria-labelledby="map-title map-description">']
    esc = lambda value: escape(str(value), quote=True)
    parts.append('<title id="map-title">' + esc(packet['city']['name']) + ' selected network outline</title>')
    parts.append('<desc id="map-description">Exact selected atlas route geometry and operational stops. Calculated outline; physical acceptance open. North up, approximate local metric projection. Access connectors are schematic, not surveyed paths.</desc>')
    parts.append('<metadata>' + esc(json.dumps(dict(packet_id=packet['packet_id'], identity=packet.get('identity'),
        sources=packet.get('sources'), context=packet.get('map_context') if context else None,
        rendering=dict(projection='local-equirectangular-111320', background_simplification_px=.8,
            selected_geometry_simplified=False, drawing_coordinate_decimals=2),
        physical_acceptance='open'), sort_keys=True, separators=(',', ':'))) + '</metadata>')
    parts.append('<style>text{font-family:DejaVu Sans,Arial,sans-serif}.muted{fill:#637782}.label{font-size:11px}.place{font-size:12px;fill:#69786f}</style>')
    parts.append(f'<defs><clipPath id="map-clip"><rect x="{mx}" y="{my}" width="{mw}" height="{mh}" rx="12"/></clipPath></defs>')
    parts.append(f'<rect width="{width}" height="{height}" fill="#fcfbf7"/>')

    def text(x, y, value, size=13, **attrs):
        a = ' '.join(f'{k.replace("_", "-")}="{esc(v)}"' for k, v in attrs.items())
        parts.append(f'<text x="{x:.2f}" y="{y:.2f}" font-size="{size}" {a}>{esc(value)}</text>')

    def path(coords, **attrs):
        d = 'M' + 'L'.join(f'{x:.2f},{y:.2f}' for x, y in coords)
        a = ' '.join(f'{k.replace("_", "-")}="{esc(v)}"' for k, v in attrs.items())
        parts.append(f'<path d="{d}" {a}/>')

    text(30, 35, 'OPENSOURCERAIL  /  CITY NETWORK', 13, letter_spacing=2, **{'class': 'muted'})
    text(28, 83, packet['city']['name'], 38, font_weight=700)
    text(30, 114, 'Selected alignment · operational station complexes · geographic outline', 15)
    parts.append(f'<rect x="{mx}" y="{my}" width="{mw}" height="{mh}" rx="12" fill="#f1f3ed" stroke="#dbe2da"/>')
    parts.append('<g clip-path="url(#map-clip)">')

    def context_paths(g):
        kind, coords = g.get('type'), g.get('coordinates', [])
        if kind == 'LineString':
            yield coords, False
        elif kind in ('MultiLineString', 'Polygon'):
            for ring in coords:
                yield ring, kind == 'Polygon'
        elif kind == 'MultiPolygon':
            for polygon in coords:
                for ring in polygon:
                    yield ring, True
        elif kind == 'GeometryCollection':
            for child in g.get('geometries', []):
                yield from context_paths(child)

    # Multiple rings form one path with evenodd fill, preserving polygon holes.
    if context:
        for layer, fill, stroke, weight in (('landuse', '#e0e7d7', '#d9e2d0', .35),
                ('water', '#bbdce8', '#9cc7da', .7), ('roads', 'none', '#d3c6b0', 1.0)):
            parts.append(f'<g id="context-{layer}" fill="none" stroke="{stroke}" stroke-width="{weight}" fill-rule="evenodd">')
            for feature in context.get('layers', {}).get(layer, []):
                # SVG fills implicitly close even an open path. River/canal
                # centre lines must never inherit an area fill: otherwise the
                # chord between their endpoints paints a blue wedge on land.
                # Keep polygon rings together for holes, but separate lines
                # even inside mixed GeometryCollections.
                paths = {False: [], True: []}
                for coords, closed in context_paths(feature.get('geometry', {})):
                    if len(coords) < 2 or not all(map(_point_ok, coords)):
                        continue
                    pts = _simplify([project(p) for p in coords])
                    if max(p[0] for p in pts) < mx or min(p[0] for p in pts) > mx + mw or max(p[1] for p in pts) < my or min(p[1] for p in pts) > my + mh:
                        continue
                    paths[closed].append('M' + 'L'.join(f'{x:.2f},{y:.2f}' for x, y in pts) + ('Z' if closed else ''))
                for closed, segments in paths.items():
                    if segments:
                        geometry_kind = 'area' if closed else 'line'
                        colour = fill if closed else 'none'
                        parts.append(f'<path d="{"".join(segments)}" fill="{colour}" data-geometry="{geometry_kind}"/>')
            parts.append('</g>')
    for route_index, (line, colour) in enumerate(rows):
        points = [project(p) for p in line['coordinates']]
        parts.append('<g><title>' + esc(line['line_id']) + '</title>')
        d = 'M' + 'L'.join(f'{x:.2f},{y:.2f}' for x, y in points)
        ref = f'selected-route-{route_index}'
        parts.append(f'<defs><path id="{ref}" d="{d}"/></defs>')
        parts.append(f'<g fill="none" stroke-linejoin="round" stroke-linecap="round"><use href="#{ref}" stroke="#fff" stroke-width="7"/><use href="#{ref}" stroke="{colour}" stroke-width="3.5"/></g>')
        parts.append('</g>')
    for feature in layers['access_connectors']['features']:
        points = feature['geometry']['coordinates']
        if points[0] != points[-1]:
            parts.append('<g><title>' + esc(feature['id']) + ' — schematic access connector; unsurveyed</title>')
            path([project(p) for p in points], stroke='#4b5964', stroke_width=1.4, stroke_dasharray='3 3', fill='none')
            parts.append('</g>')
    for feature in layers['original_access_markers']['features']:
        x, y = project(feature['geometry']['coordinates'])
        parts.append(f'<rect x="{x-2.6:.2f}" y="{y-2.6:.2f}" width="5.2" height="5.2" fill="#f8f5ec" stroke="#65726c" stroke-width="1"><title>{esc(feature["id"])} — original access marker</title></rect>')
    for feature in layers['platforms']['features']:
        parts.append('<g><title>' + esc(feature['id']) + ' — declared platform envelope</title>')
        path([project(p) for p in feature['geometry']['coordinates']], fill='none',
             stroke=feature['properties']['colour'], stroke_width=7, stroke_linecap='round')
        parts.append('</g>')
    labels = []
    for feature in layers['stations']['features']:
        x, y = project(feature['geometry']['coordinates'])
        p = feature['properties']
        parts.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="4" fill="#fff" stroke="{p["colour"]}" stroke-width="1.8"><title>{esc(p["label"])} — {esc(feature["id"])}</title></circle>')
        labels.append((x, y, p['label'], p['colour']))
    for feature in layers['interchanges']['features']:
        x, y = project(feature['geometry']['coordinates'])
        parts.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="6.5" fill="none" stroke="#263d49" stroke-width="1.4"><title>{esc(feature["id"])} — explicit interchange; {esc(", ".join(feature["properties"].get("lines", [])))}</title></circle>')

    occupied = []

    def label(x, y, value, cls='label', colour=None):
        bw, bh = len(value) * (6.2 if cls == 'label' else 6.8), 15
        for dx, dy in ((9, -8), (9, 17), (-bw - 9, -8), (-bw - 9, 17), (-bw / 2, -13), (-bw / 2, 23)):
            box = (x + dx - 2, y + dy - bh, x + dx + bw + 2, y + dy + 3)
            if box[0] < mx + 6 or box[1] < my + 6 or box[2] > mx + mw - 6 or box[3] > my + mh - 6:
                continue
            if any(box[0] < b[2] and box[2] > b[0] and box[1] < b[3] and box[3] > b[1] for b in occupied):
                continue
            occupied.append(box)
            # Explicit halo then foreground works in CairoSVG and GitHub SVG
            # renderers that do not implement the SVG2 paint-order property.
            text(x + dx, y + dy, value, 11 if cls == 'label' else 12,
                 **{'class': cls}, stroke='#fff', stroke_width=3, stroke_linejoin='round',
                 aria_hidden='true')
            text(x + dx, y + dy, value, 11 if cls == 'label' else 12, **{'class': cls}, **({'fill': colour} if colour else {}))
            return True
        return False

    for x, y, value, colour in labels:
        label(x, y, value, colour=colour)
    if context:
        places = context.get('layers', {}).get('places', [])
        places = sorted(places, key=lambda f: (-f.get('properties', {}).get('population', 0), str(f.get('id', ''))))
        seen = set()
        for feature in places:
            p, g = feature.get('properties', {}), feature.get('geometry', {})
            name = p.get('name:en') or p.get('name')
            # Cairo's SVG text backend does not consistently shape/bidi Arabic.
            # Omit these background labels if no transliteration exists; the
            # verified context source retains the original names verbatim.
            if name and any(unicodedata.bidirectional(c) in ('R', 'AL', 'AN') for c in name):
                continue
            if g.get('type') != 'Point' or not _point_ok(g.get('coordinates')) or not name or name in seen:
                continue
            seen.add(name)
            if len(name) <= 30:
                label(*project(g['coordinates']), name, cls='place')
            if len(seen) >= 28:
                break
    parts.append('</g>')

    # Cartographic furniture is outside the geometry group and never shifts it.
    nx, ny = mx + mw - 30, my + 32
    path([(nx, ny + 20), (nx, ny - 1)], stroke='#253c48', stroke_width=2)
    path([(nx - 5, ny + 7), (nx, ny - 3), (nx + 5, ny + 7)], fill='#253c48')
    text(nx - 5, ny - 9, 'N', 13, font_weight=700)
    scale_m = scale_length(project.pixels_per_m)
    scale_px = scale_m * project.pixels_per_m
    sx, sy = mx + 18, my + mh - 23
    parts.append(f'<rect x="{sx-8}" y="{sy-26}" width="{scale_px+32:.2f}" height="42" rx="4" fill="#fcfbf7" fill-opacity=".93"/>')
    path([(sx, sy - 5), (sx, sy), (sx + scale_px, sy), (sx + scale_px, sy - 5)], stroke='#253c48', stroke_width=2, fill='none')
    text(sx, sy - 10, f'{scale_m / 1000:g} km', 12)
    lx = width - sidebar - 24
    text(lx, 171, 'SELECTED LINES', 13, letter_spacing=1.2, font_weight=700)
    for i, (line, colour) in enumerate(rows):
        y = 203 + i * 25
        path([(lx, y - 5), (lx + 24, y - 5)], stroke=colour, stroke_width=4, stroke_linecap='round')
        text(lx + 36, y, line_label(line), 14)
        text(width - 26, y, line['shape'].capitalize(), 11, text_anchor='end', **{'class': 'muted'})
    ly = 235 + len(rows) * 25
    text(lx, ly, 'MAP KEY', 13, letter_spacing=1.2, font_weight=700)
    parts.append(f'<circle cx="{lx+7}" cy="{ly+28}" r="4" fill="#fff" stroke="#176c9c" stroke-width="2"/>')
    text(lx + 26, ly + 33, 'Operational station complex', 12)
    path([(lx, ly + 53), (lx + 15, ly + 53)], stroke='#176c9c', stroke_width=7, stroke_linecap='round')
    text(lx + 26, ly + 58, 'Declared platform envelope', 12)
    parts.append(f'<rect x="{lx+4}" y="{ly+74}" width="6" height="6" fill="#f8f5ec" stroke="#65726c"/>')
    text(lx + 26, ly + 83, 'Original access marker', 12)
    path([(lx, ly + 102), (lx + 16, ly + 102)], stroke='#4b5964', stroke_width=1.4, stroke_dasharray='3 3')
    text(lx + 26, ly + 107, 'Schematic access connector', 12)
    parts.append(f'<circle cx="{lx+7}" cy="{ly+128}" r="6.5" fill="none" stroke="#263d49" stroke-width="1.4"/>')
    text(lx + 26, ly + 133, 'Explicit interchange', 12)
    for i, value in enumerate(('L1/01 = line / station reference.', 'Labels shown where space allows.', 'Full source IDs: SVG titles + GIS.', 'Coincident original markers may', 'sit beneath operational symbols.', 'Access paths remain unsurveyed.', 'Depot and energy siting: unlocated.')):
        text(lx, ly + 169 + i * 18, value, 11, **{'class': 'muted'})
    fy = height - 102
    text(30, fy, 'CALCULATED OUTLINE  ·  Physical acceptance, detailed engineering and operating release remain open.', 13, font_weight=700)
    text(30, fy + 23, f'Packet {packet["packet_id"][:20]}  ·  Alignment {str(packet.get("identity", {}).get("selected_alignment_id", "not supplied"))[:20]}', 11, **{'class': 'muted'})
    attribution = ' · '.join(a.get('name', '') for a in (context or {}).get('attribution', []))
    text(30, fy + 44, 'Context: ' + (attribution or 'not supplied / not verified') + '  ·  Background generalized ≤0.8 px; selected route vertices retained.', 10, **{'class': 'muted'})
    if context:
        parts.append('<metadata id="context-attribution">' + esc(json.dumps(context.get('attribution', []), sort_keys=True)) + '</metadata>')
    text(30, fy + 63, 'North up · local approximate metric projection · platform envelopes are centreline hypotheses, not surveyed footprints.', 10, **{'class': 'muted'})
    parts.append('</svg>')
    return ''.join(parts)
