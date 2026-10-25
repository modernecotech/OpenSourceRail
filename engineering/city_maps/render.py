"""Offline geographic context beneath the current, unqualified city proposal.

Both layers use Web Mercator. Basemap features are retained inputs, never a
road-routing instruction or a building/utility clearance measurement.
"""
from hashlib import sha256
from html import escape
import json
import math
from pathlib import Path
import unicodedata

WIDTH, HEIGHT = 1600, 1200
LEFT, TOP, PLOT_W, PLOT_H = 40, 110, 1520, 910
PALETTE = ('#063eae', '#b51932', '#14703c', '#7243a3', '#bc5809',
           '#007c89', '#aa2676', '#56523b', '#21387d', '#8f3227')


def mercator(point):
    lon, lat = point[:2]
    if (type(lon) not in (int, float) or type(lat) not in (int, float)
            or not math.isfinite(lon) or not math.isfinite(lat)
            or not -180 <= lon <= 180 or not -85.05112878 <= lat <= 85.05112878):
        raise ValueError('finite longitude/Web Mercator latitude required')
    return ((lon + 180) / 360,
            (1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2)


def lonlat(point):
    x, y = point
    return [x * 360 - 180, math.degrees(math.atan(math.sinh(math.pi * (1 - 2*y))))]


def route_lines(geojson):
    data = json.loads(Path(geojson).read_bytes())
    lines = []
    for feature in data['features']:
        geometry = feature.get('geometry') or {}
        properties = feature.get('properties') or {}
        name = str(properties.get('name', properties.get('line', 'route')))
        if geometry.get('type') == 'LineString':
            lines.append((name, geometry['coordinates']))
        elif geometry.get('type') == 'MultiLineString':
            lines.extend((name, points) for points in geometry['coordinates'])
    if not lines or any(len(points) < 2 for _, points in lines):
        raise ValueError('geographic route lines required')
    return lines


def viewport(design, geojson):
    points = [p for _, coordinates in route_lines(geojson) for p in coordinates]
    points += [[s['lon'], s['lat']] for s in design['stations']]
    projected = [mercator(p) for p in points]
    x0, x1 = min(p[0] for p in projected), max(p[0] for p in projected)
    y0, y1 = min(p[1] for p in projected), max(p[1] for p in projected)
    dx, dy = max(x1-x0, 1e-5)*1.13, max(y1-y0, 1e-5)*1.13
    dx, dy = max(dx, dy*PLOT_W/PLOT_H), max(dy, dx*PLOT_H/PLOT_W)
    cx, cy = (x0+x1)/2, (y0+y1)/2
    west, north = lonlat((cx-dx/2, cy-dy/2))
    east, south = lonlat((cx+dx/2, cy+dy/2))
    bounds = [west, south, east, north]
    # About two source pixels per display pixel; cap network/memory per map.
    zoom = max(6, min(13, math.floor(math.log2(PLOT_W/(256*dx)))+1))
    while zoom > 0:
        n = 2**zoom
        tiles = ((math.floor((cx+dx/2)*n)-math.floor((cx-dx/2)*n)+1)
                 * (math.floor((cy+dy/2)*n)-math.floor((cy-dy/2)*n)+1))
        if tiles <= 64:
            break
        zoom -= 1
    return bounds, zoom


def _simplify(points, tolerance=.3):
    if len(points) < 3:
        return points
    keep = {0, len(points)-1}
    pending = [(0, len(points)-1)]
    while pending:
        start, end = pending.pop()
        ax, ay = points[start]; bx, by = points[end]
        dx, dy = bx-ax, by-ay; length = dx*dx+dy*dy
        best, index = tolerance*tolerance, None
        for i in range(start+1, end):
            x, y = points[i]
            t = max(0, min(1, ((x-ax)*dx+(y-ay)*dy)/length)) if length else 0
            distance = (x-ax-t*dx)**2+(y-ay-t*dy)**2
            if distance > best:
                best, index = distance, i
        if index is not None:
            keep.add(index); pending.extend(((start, index), (index, end)))
    return [points[i] for i in sorted(keep)]


def _paths(geometry, project):
    if geometry['type'] == 'GeometryCollection':
        return [path for child in geometry['geometries'] for path in _paths(child,project)]
    kind = geometry['type']; coordinates = geometry['coordinates']
    if kind == 'LineString': groups = [[coordinates]]
    elif kind == 'MultiLineString': groups = [[line] for line in coordinates]
    elif kind == 'Polygon': groups = [coordinates]
    elif kind == 'MultiPolygon': groups = coordinates
    else: return []
    closed = kind in ('Polygon', 'MultiPolygon')
    result = []
    for group in groups:
        parts = []
        for ring in group:
            points = _simplify([project(p) for p in ring])
            if not points: continue
            parts.append('M'+'L'.join(f'{x:.2f},{y:.2f}' for x,y in points)+('Z' if closed else ''))
        result.append(''.join(parts))
    return result


def _name(properties):
    for key in ('name:en', 'pgf:name:en', 'name'):
        value = properties.get(key)
        if isinstance(value, str) and value.strip():
            # Use an actual source English/Latin name. Other scripts remain
            # in the context packet; absent fonts/shaping must not yield
            # square boxes or an invented translation in static exports.
            if all((not unicodedata.category(ch).startswith('L') or 'LATIN' in unicodedata.name(ch,''))
                   and not unicodedata.category(ch).startswith('C') for ch in value):
                return value.strip()
    return None


def render(design, geojson, output, *, context_path=None):
    from .basemap import load
    geojson, output = Path(geojson), Path(output)
    context_path = Path(context_path) if context_path else geojson.with_name('map-context.json.gz')
    if not context_path.is_file():
        raise ValueError('retained city basemap required: '+str(context_path))
    context = load(context_path)
    bounds, zoom = viewport(design, geojson)
    if zoom != context['zoom'] or any(abs(a-b) > 1e-8 for a,b in zip(bounds, context['bounds_wsen'])):
        raise ValueError('basemap viewport differs from current corridors/stops; extract again')
    layers = context['layers']
    if not layers.get('roads') or not layers.get('places'):
        raise ValueError('basemap lacks roads or place context')
    west, south, east, north = bounds
    x0,y0 = mercator((west,north)); x1,y1 = mercator((east,south))
    def project(p):
        x,y = mercator(p)
        return LEFT+(x-x0)/(x1-x0)*PLOT_W, TOP+(y-y0)/(y1-y0)*PLOT_H
    counts = {name:len(features) for name,features in layers.items()}
    metadata = dict(context_sha256=sha256(context_path.read_bytes()).hexdigest(),
        corridor_sha256=sha256(geojson.read_bytes()).hexdigest(),bounds_wsen=bounds,zoom=zoom,
        current_stations_sha256=sha256(json.dumps(design['stations'],sort_keys=True).encode()).hexdigest(),
        source=context['source'],layer_feature_counts=counts)
    rows = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img">',
        '<title>'+escape(design['name'])+' — current network in its city context</title>',
        '<desc>Current proposed corridors and stops over attributed OpenStreetMap roads, water, land use, buildings and place names. Geographic context is not surveyed clearance.</desc>',
        '<metadata>'+escape(json.dumps(metadata,sort_keys=True,separators=(',',':')))+' </metadata>',
        '<defs><clipPath id="map-clip"><rect x="40" y="110" width="1520" height="910"/></clipPath></defs>',
        '<rect width="1600" height="1200" fill="white"/>',
        '<g font-family="DejaVu Sans, Noto Sans, sans-serif" fill="#183348">',
        '<text x="40" y="45" font-size="30" font-weight="bold">'+escape(design['name'])+' · proposed PM-maglev network</text>',
        '<text x="40" y="78" font-size="17">Current geographic corridors and proposed stops · city background restored from OpenStreetMap</text>',
        '<g clip-path="url(#map-clip)"><rect x="40" y="110" width="1520" height="910" fill="#f2f0e9"/>']
    for layer in ('earth','landcover','landuse','water','buildings','roads'):
        rows.append(f'<g id="basemap-{layer}" data-feature-count="{counts.get(layer,0)}">')
        for feature in layers.get(layer,[]):
            properties=feature.get('properties',{});kind=properties.get('kind','')
            geometry=feature['geometry'];polygon='Polygon' in geometry['type']
            style='fill="#f2f0e9" stroke="none"'
            if layer in ('landcover','landuse'):
                colour=('#d8e6cb' if kind in ('park','forest','wood','grass','garden','nature_reserve','national_park','recreation_ground','grassland','scrub')
                        else '#e2dfda' if kind in ('residential','urban_area','industrial','commercial') else '#ebe7db')
                style=f'fill="{colour}" stroke="none"'
            elif layer=='water':style='fill="#a9d2e5" stroke="#8abfd9" stroke-width="1.1"' if polygon else 'fill="none" stroke="#91c5df" stroke-width="1.7"'
            elif layer=='buildings':style='fill="#d9d3cc" stroke="none"'
            elif layer=='roads':
                detail=properties.get('kind_detail','')
                colour,width=('#dfae6d',2.5) if detail in ('motorway','trunk','primary') else ('#c7b99e',1.6) if detail in ('secondary','tertiary') else ('#bcbcbc',.7) if kind=='rail' else ('#fff',.8)
                style=f'fill="none" stroke="{colour}" stroke-width="{width}"'+(' stroke-dasharray="3 3"' if kind=='rail' else '')
            for path in _paths(geometry,project):
                rows.append(f'<path d="{path}" {style} fill-rule="evenodd"/>')
        rows.append('</g>')
    # Named locations and a bounded set of street labels, with deterministic
    # collision suppression. No invented streets or labels fill missing data.
    labels=[];unsupported=0
    for feature in layers.get('places',[]):
        if feature['geometry']['type']!='Point':continue
        p=feature.get('properties',{});name=_name(p)
        if not name:
            unsupported+=int(any(isinstance(p.get(k),str) for k in ('name:en','pgf:name:en','name')))
            continue
        x,y=project(feature['geometry']['coordinates'])
        importance=0 if p.get('kind_detail')=='city' else 1 if p.get('kind_detail')=='town' else 2
        labels.append((importance,name,x,y,21 if importance==0 else 16))
    for feature in layers.get('roads',[]):
        name=_name(feature.get('properties',{}));g=feature['geometry']
        if not name or g['type'] not in ('LineString','MultiLineString'):continue
        for line in ([g['coordinates']] if g['type']=='LineString' else g['coordinates']):
            if len(line)<2:continue
            coordinates=[project(p) for p in line]
            a,b=max(zip(coordinates,coordinates[1:]),key=lambda pair:math.dist(*pair))
            if math.dist(a,b)>len(name)*6+20:
                labels.append((3,name,(a[0]+b[0])/2,(a[1]+b[1])/2,12))
    used=[];names=set();label_count=0
    rows.append('<g id="basemap-labels" text-anchor="middle">')
    for priority,name,x,y,size in sorted(labels):
        if not (LEFT+20<x<LEFT+PLOT_W-20 and TOP+20<y<TOP+PLOT_H-20):continue
        key=(name,round(x/200),round(y/200))
        width=min(len(name)*size*.58,350);box=(x-width/2,y-size,x+width/2,y+size*.3)
        if key in names or any(box[0]<b[2]+5 and box[2]>b[0]-5 and box[1]<b[3]+5 and box[3]>b[1]-5 for b in used):continue
        names.add(key);used.append(box);label_count+=1
        # Two passes also retain readable halos in CairoSVG/PDF converters
        # that do not implement SVG2 paint-order.
        rows.append(f'<text x="{x:.2f}" y="{y:.2f}" font-size="{size}" fill="#f8f7f3" stroke="#f8f7f3" stroke-width="3" stroke-linejoin="round">{escape(name)}</text>')
        rows.append(f'<text x="{x:.2f}" y="{y:.2f}" font-size="{size}" fill="#485157">{escape(name)}</text>')
        if label_count>=220:break
    rows.append('</g><g id="current-proposal">')
    lines=route_lines(geojson);line_names=list(dict.fromkeys(name for name,_ in lines))
    topology={str(l.get('name',l.get('id'))):l.get('shape') for l in design.get('lines',[])}
    colours={name:('#20242a' if topology.get(name)=='ring' else PALETTE[i%len(PALETTE)]) for i,name in enumerate(line_names)}
    for name,coordinates in lines:
        points=_simplify([project(p) for p in coordinates],.25)
        d=' '.join(f'{x:.2f},{y:.2f}' for x,y in points)
        rows.append(f'<polyline points="{d}" stroke="white" fill="none" stroke-width="8" opacity=".85"/>')
        rows.append(f'<polyline points="{d}" stroke="{colours[name]}" fill="none" stroke-width="4.4" stroke-linejoin="round"><title>{escape(name)}</title></polyline>')
    terminals=set()
    for name in line_names:
        if topology.get(name)=='ring':continue
        stops=sorted((s for s in design['stations'] if s.get('line')==name),key=lambda s:s.get('s_m',0))
        if stops:terminals.update((stops[0]['id'],stops[-1]['id']))
    for station in design['stations']:
        x,y=project((station['lon'],station['lat']))
        if station['id'] in terminals:
            rows.append(f'<rect x="{x-4.5:.2f}" y="{y-4.5:.2f}" width="9" height="9" fill="white" stroke="#142b3f" stroke-width="2"><title>{escape(station["id"])}</title></rect>')
        else:rows.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="3.5" fill="white" stroke="#142b3f" stroke-width="1.5"><title>{escape(station["id"])}</title></circle>')
    for transfer in design.get('interchanges',[]):
        if 'lon' not in transfer or 'lat' not in transfer:continue
        x,y=project((transfer['lon'],transfer['lat']))
        rows.append(f'<path d="M{x:.2f},{y-6:.2f}L{x+6:.2f},{y:.2f}L{x:.2f},{y+6:.2f}L{x-6:.2f},{y:.2f}Z" fill="#f4ba48" stroke="#473b20" stroke-width="1.5"><title>Retained transfer location {escape(str(transfer.get("id","")))}</title></path>')
    rows += ['</g></g>', '<rect x="40" y="110" width="1520" height="910" fill="none" stroke="#a8afb5"/>',
        '<path d="M1520 175V130M1512 143L1520 128L1528 143" fill="none" stroke="#183348" stroke-width="2"/><text x="1520" y="123" font-size="17" text-anchor="middle">N</text>']
    for i,name in enumerate(line_names):
        x=45+(i%7)*218;y=1054+(i//7)*27
        rows.append(f'<path d="M{x} {y-5}h28" stroke="{colours[name]}" stroke-width="5"/><text x="{x+36}" y="{y}" font-size="15">{escape(name)}</text>')
    rows += ['<text x="40" y="1125" font-size="15">○ Proposed stop   □ Terminal   ◆ Retained transfer location · alignment and station fit remain unqualified</text>',
        '<text x="40" y="1152" font-size="14">Map data © OpenStreetMap contributors (ODbL) · Natural Earth · Protomaps basemap, 24 October 2026</text>',
        '<text x="40" y="1178" font-size="14">Geographic context only; no building, utility, water or construction clearance is established.</text>', '</g></svg>']
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text('\n'.join(rows)+'\n')
    return dict(metadata,label_count=label_count,unsupported_place_labels_retained_not_rendered=unsupported,
                label_policy='Source English/Latin names with verified static-font coverage; other scripts retained in context, no invented translation',
                projection='EPSG:3857',context_file=context_path.name)


def source_paths():
    return [Path(__file__),Path(__file__).with_name('basemap.py'),Path(__file__).with_name('__init__.py'),Path(__file__).with_name('requirements.txt')]
