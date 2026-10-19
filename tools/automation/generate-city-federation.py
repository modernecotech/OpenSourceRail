#!/usr/bin/env python3
"""Federate retained station product geometry at controlled city coordinates.

This is an IFC coordination model: local z=0 is an unapproved datum, route
segment tangents are provisional, and no foundations/site acceptance are implied.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
from html import escape
import json
import math
from pathlib import Path
import tomllib
import uuid

ROOT = Path(__file__).resolve().parents[2]
MAX_BYTES = 50 * 1024 * 1024
SCHEMA = 'osr-city-station-federation/1'
HOLDS = ['Surveyed station coordinates and setting-out approval',
         'Vertical datum, terrain, formation and station level survey',
         'Horizontal alignment, orientation and transition geometry approval',
         'Site foundation, utilities, access, structural and interface acceptance',
         'Source geometry is retained planning geometry, not manufacturing release']


def digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def encoded(value):
    return (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n').encode()


def controlled(root, name):
    path = (root / name).resolve()
    if not path.is_relative_to(root.resolve()) or not path.is_file():
        raise ValueError('Missing or unsafe controlled source: ' + str(name))
    return path


def inputs(city, root=ROOT):
    city = Path(city).resolve(); root = Path(root).resolve()
    design = tomllib.loads((city / 'design.toml').read_text())
    slug = design['city']['slug']; connected = city / 'engineering/connected-build'
    manifest_path = connected / 'manifest.json'
    if not manifest_path.is_file():
        if connected.exists() and any(connected.iterdir()):
            raise ValueError('Partial connected package requires its source manifest')
        return shared_inputs(city, design, root)
    manifest = json.loads(manifest_path.read_text())
    # A fresh timestamp cannot replace exact upstream receipt checks.
    for name, expected in manifest['source_sha256'].items():
        if digest(controlled(root, name)) != expected:
            raise ValueError('Stale connected source: ' + name)
    paths = [city / 'design.toml', city / f'{slug}.stations.json',
             city / f'{slug}.corridor.geojson', connected / 'stations.json', manifest_path]
    stations = json.loads((connected / 'stations.json').read_text())
    positions = json.loads((city / f'{slug}.stations.json').read_text())
    if len({s['id'] for s in stations}) != len(stations) or len({s['id'] for s in positions}) != len(positions):
        raise ValueError('Duplicate station identity')
    locations = {s['id']: s for s in positions}
    if {s['id'] for s in stations} != set(locations) or {s['id'] for s in stations} != {s['id'] for s in design['stations']}:
        raise ValueError('Station inventories differ')
    for s in design['stations']:
        actual = locations[s['id']]
        # Native design TOML serialises chainage to 0.1 m; the retained
        # station JSON preserves full precision. This is a declared rounding
        # tolerance, not permission to move station coordinates.
        if actual['line'] != s['line'] or any(actual[k] != s[k] for k in ('lat', 'lon')) or abs(actual['s_m'] - s['s_m']) > 0.050001:
            raise ValueError('Station coordinates differ from controlled design: ' + s['id'])
    variants = {}
    for variant in sorted({s['product_variant'] for s in stations}):
        if not variant or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_' for c in variant):
            raise ValueError('Unsafe variant identifier')
        relative = f'ifc/station-{variant}.ifc'; path = connected / relative
        if not path.is_file() or manifest.get('output_sha256', {}).get(relative) != digest(path):
            raise ValueError('Missing/stale source IFC geometry: ' + variant)
        variants[variant] = path; paths.append(path)
    for name in ('stations.json',):
        path = connected / name
        if manifest.get('output_sha256', {}).get(name) != digest(path):
            raise ValueError('Stale connected station register')
    paths += [controlled(root, name) for name in manifest['source_sha256']]
    generator = Path(__file__).resolve()
    hashes = {p.relative_to(root).as_posix(): digest(p) for p in paths}
    # A test root can differ from the installed generator root.
    if generator.is_relative_to(root): hashes[generator.relative_to(root).as_posix()] = digest(generator)
    return design, stations, locations, variants, hashes


def shared_inputs(city, design, root):
    """Use this city's own station schedule and shared archetypes, never Baghdad."""
    slug = design['city']['slug']
    location_path = city / f'{slug}.stations.json'
    positions = json.loads(location_path.read_text())
    locations = {s['id']: s for s in positions}
    stations = design.get('stations', [])
    if len(locations) != len(positions) or len({s['id'] for s in stations}) != len(stations) or set(locations) != {s['id'] for s in stations}:
        raise ValueError('Station inventories differ')
    paths = [city / 'design.toml', location_path, city / f'{slug}.corridor.geojson']
    manifest = root / 'design/component-catalogue/catalog/buildable-stations/station-kit-manifest.json'
    product_map = city / 'engineering/station-product-map.json'
    paths.extend([manifest, product_map])
    if product_map.is_file():
        report = json.loads(product_map.read_text())
        if report.get('design_sha256') != digest(city / 'design.toml'):
            raise ValueError('Stale city station product map')
        if manifest.is_file() and report.get('manifest_sha256') != digest(manifest):
            raise ValueError('Stale shared station manifest')
        mapped = {s['station_id']: s['archetype'] for s in report.get('stations', [])}
        if mapped != {s['id']: s['archetype'] for s in stations}:
            raise ValueError('City station archetype inventories differ')
    variants = {}; rows = []
    for station in stations:
        actual = locations[station['id']]
        if station['line'] != actual['line'] or any(station[k] != actual[k] for k in ('lat', 'lon')) or abs(station['s_m'] - actual['s_m']) > .050001:
            raise ValueError('Station coordinates differ from controlled design: ' + station['id'])
        archetype = station['archetype']
        if not archetype or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_' for c in archetype):
            raise ValueError('Unsafe archetype identifier')
        path = root / 'build/engineering/interchange/stations' / f'station-{archetype}.ifc'
        variants[archetype] = path if path.is_file() else None
        paths.append(path)
        rows.append(dict(id=station['id'], line=station['line'], s_m=station['s_m'], product_variant=archetype))
    hashes = {p.relative_to(root).as_posix(): digest(p) if p.is_file() else None for p in paths}
    generator = Path(__file__).resolve()
    if generator.is_relative_to(root): hashes[generator.relative_to(root).as_posix()] = digest(generator)
    return design, rows, locations, variants, hashes


def layout(city, design, stations, locations):
    from pyproj import Transformer
    slug = design['city']['slug']
    lons = [float(s['lon']) for s in locations.values()]; lats = [float(s['lat']) for s in locations.values()]
    if not lons or any(not math.isfinite(v) for v in lons + lats) or any(abs(v) > 180 for v in lons) or any(abs(v) > 80 for v in lats):
        raise ValueError('Finite nonpolar city coordinates required')
    lon = sum(lons) / len(lons); lat = sum(lats) / len(lats)
    zone = min(60, max(1, int((lon + 180) // 6) + 1)); epsg = (32600 if lat >= 0 else 32700) + zone
    transform = Transformer.from_crs(4326, epsg, always_xy=True)
    origin = transform.transform(lon, lat)
    routes = json.loads((city / f'{slug}.corridor.geojson').read_text())
    byline = {}
    for feature in routes['features']:
        props = feature.get('properties', {}); name = props.get('line') or props.get('name')
        geom = feature['geometry']; coords = geom['coordinates']
        if geom['type'] == 'LineString': coords = [coords]
        elif geom['type'] != 'MultiLineString': continue
        byline.setdefault(name, []).extend([[transform.transform(*p[:2]) for p in section] for section in coords])
    rows = []
    for station in sorted(stations, key=lambda s: s['id']):
        p = locations[station['id']]
        if station['line'] != p['line'] or abs(float(station['s_m']) - float(p['s_m'])) > 0.050001:
            raise ValueError('Connected station chainage/line differs')
        east, north = transform.transform(p['lon'], p['lat']); nearest = None
        for section in byline.get(p['line'], []):
            for a, b in zip(section, section[1:]):
                dx, dy = b[0] - a[0], b[1] - a[1]; denominator = dx * dx + dy * dy
                if denominator <= 1e-12: continue
                t = max(0, min(1, ((east - a[0]) * dx + (north - a[1]) * dy) / denominator))
                error = math.hypot(east - a[0] - t * dx, north - a[1] - t * dy)
                candidate = (error, math.atan2(dy, dx))
                if nearest is None or candidate < nearest: nearest = candidate
        if nearest is None: raise ValueError('Missing route tangent for ' + p['line'])
        rows.append(dict(id=station['id'], line=p['line'], product_variant=station['product_variant'],
            longitude=p['lon'], latitude=p['lat'], chainage_m=p['s_m'],
            translation_m=[east - origin[0], north - origin[1], 0.0],
            rotation_about_z_rad=nearest[1], tangent_offset_m=nearest[0],
            source_station_elevation=station.get('layout', {}).get('elevation', 'unknown'),
            vertical_datum='arbitrary-local-zero-not-surveyed',
            orientation_basis='nearest directed retained corridor segment; unapproved',
            engineering_qualified=False, manufacturing_release=False))
    return dict(epsg=epsg, origin_easting_m=origin[0], origin_northing_m=origin[1],
        orthogonal_height_m=0.0, vertical_datum='unapproved-local-zero', instances=rows)


def guid(value):
    import ifcopenshell.guid
    return ifcopenshell.guid.compress(uuid.uuid5(uuid.NAMESPACE_URL, value).hex)


def write_ifc(output, plan, variants, city_slug):
    import ifcopenshell
    import ifcopenshell.util.placement
    import ifcopenshell.util.unit
    sources = {name: ifcopenshell.open(str(path)) for name, path in variants.items()}
    schemas = {f.schema for f in sources.values()}
    if len(schemas) != 1: raise ValueError('Mixed IFC schemas require an explicit migration')
    f = ifcopenshell.file(schema=schemas.pop())
    def point(v): return f.create_entity('IfcCartesianPoint', Coordinates=tuple(float(x) for x in v))
    def direction(v): return f.create_entity('IfcDirection', DirectionRatios=tuple(float(x) for x in v))
    def axis(translation=(0., 0., 0.), x=(1., 0., 0.), z=(0., 0., 1.)):
        return f.create_entity('IfcAxis2Placement3D', Location=point(translation), Axis=direction(z), RefDirection=direction(x))
    context = f.create_entity('IfcGeometricRepresentationContext', ContextIdentifier='Body', ContextType='Model',
        CoordinateSpaceDimension=3, Precision=1e-5, WorldCoordinateSystem=axis())
    unit = f.create_entity('IfcSIUnit', UnitType='LENGTHUNIT', Name='METRE')
    project = f.create_entity('IfcProject', GlobalId=guid(city_slug + '/project'), Name=city_slug + ' station coordination federation',
        RepresentationContexts=[context], UnitsInContext=f.create_entity('IfcUnitAssignment', Units=[unit]))
    site = f.create_entity('IfcSite', GlobalId=guid(city_slug + '/site'), Name='Provisional horizontal coordination; vertical datum unresolved',
        ObjectPlacement=f.create_entity('IfcLocalPlacement', RelativePlacement=axis()), CompositionType='ELEMENT')
    f.create_entity('IfcRelAggregates', GlobalId=guid(city_slug + '/site-rel'), RelatingObject=project, RelatedObjects=[site])
    crs = f.create_entity('IfcProjectedCRS', Name='EPSG:' + str(plan['epsg']), Description='Horizontal UTM projection; vertical datum unapproved', MapUnit=unit)
    f.create_entity('IfcMapConversion', SourceCRS=context, TargetCRS=crs,
        Eastings=plan['origin_easting_m'], Northings=plan['origin_northing_m'], OrthogonalHeight=0., XAxisAbscissa=1., XAxisOrdinate=0., Scale=1.)
    maps = {}; counts = {}
    identity = f.create_entity('IfcCartesianTransformationOperator3D', LocalOrigin=point((0, 0, 0)), Scale=1.)
    for name, source in sources.items():
        if abs(ifcopenshell.util.unit.calculate_unit_scale(source) - 1.) > 1e-12:
            raise ValueError('Source geometry must use metres')
        items = []; product_count = 0
        for product in sorted(source.by_type('IfcProduct'), key=lambda p: p.GlobalId):
            if not product.Representation: continue
            for representation in product.Representation.Representations:
                if representation.RepresentationIdentifier != 'Body': continue
                copied = [f.add(item) for item in representation.Items]
                if not copied: continue
                matrix = ifcopenshell.util.placement.get_local_placement(product.ObjectPlacement)
                # Mapping origin is inverse-applied by IFC; preserve source placements
                # through a target transform rather than inverting it implicitly.
                rep = f.create_entity('IfcShapeRepresentation', ContextOfItems=context, RepresentationIdentifier='Body',
                    RepresentationType=representation.RepresentationType, Items=copied)
                source_map = f.create_entity('IfcRepresentationMap', MappingOrigin=axis(), MappedRepresentation=rep)
                transform = f.create_entity('IfcCartesianTransformationOperator3D', Axis1=direction(matrix[:3, 0]),
                    Axis2=direction(matrix[:3, 1]), Axis3=direction(matrix[:3, 2]), LocalOrigin=point(matrix[:3, 3]), Scale=1.)
                items.append(f.create_entity('IfcMappedItem', MappingSource=source_map, MappingTarget=transform)); product_count += 1
        if not items: raise ValueError('Source variant has no body geometry: ' + name)
        rep = f.create_entity('IfcShapeRepresentation', ContextOfItems=context, RepresentationIdentifier='Body', RepresentationType='MappedRepresentation', Items=items)
        maps[name] = f.create_entity('IfcRepresentationMap', MappingOrigin=axis(), MappedRepresentation=rep)
        counts[name] = dict(source_body_representation_count=product_count, source_ifc_sha256=digest(variants[name]))
    elements = []
    for row in plan['instances']:
        theta = row['rotation_about_z_rad']; placement = f.create_entity('IfcLocalPlacement', PlacementRelTo=site.ObjectPlacement,
            RelativePlacement=axis(row['translation_m'], (math.cos(theta), math.sin(theta), 0.)))
        mapped = f.create_entity('IfcMappedItem', MappingSource=maps[row['product_variant']], MappingTarget=identity)
        rep = f.create_entity('IfcShapeRepresentation', ContextOfItems=context, RepresentationIdentifier='Body', RepresentationType='MappedRepresentation', Items=[mapped])
        element = f.create_entity('IfcElementAssembly', GlobalId=guid(city_slug + '/station/' + row['id']), Name=row['id'],
            ObjectType='Planning station product geometry: ' + row['product_variant'], ObjectPlacement=placement,
            Representation=f.create_entity('IfcProductDefinitionShape', Representations=[rep]), AssemblyPlace='SITE', PredefinedType='USERDEFINED')
        properties = dict(StationId=row['id'], SourceVariant=row['product_variant'], SourceIFCSHA256=counts[row['product_variant']]['source_ifc_sha256'],
            VerticalDatum='unapproved local zero', OrientationBasis=row['orientation_basis'], Release='planning coordination only')
        props = [f.create_entity('IfcPropertySingleValue', Name=k, NominalValue=f.create_entity('IfcText', str(v))) for k, v in properties.items()]
        pset = f.create_entity('IfcPropertySet', GlobalId=guid(city_slug + '/' + row['id'] + '/properties'), Name='OSR_CoordinationProvenance', HasProperties=props)
        f.create_entity('IfcRelDefinesByProperties', GlobalId=guid(city_slug + '/' + row['id'] + '/property-rel'), RelatedObjects=[element], RelatingPropertyDefinition=pset)
        elements.append(element)
    f.create_entity('IfcRelContainedInSpatialStructure', GlobalId=guid(city_slug + '/containment'), RelatedElements=elements, RelatingStructure=site)
    f.write(str(output))
    reopened = ifcopenshell.open(str(output))
    if len(reopened.by_type('IfcElementAssembly')) != len(plan['instances']): raise ValueError('IFC station count mismatch')
    if len({p.GlobalId for p in reopened.by_type('IfcRoot')}) != len(reopened.by_type('IfcRoot')): raise ValueError('Duplicate IFC identity')
    return dict(schema=f.schema, station_instances=len(elements), variant_geometry=counts,
        representation_reuse='nested IfcRepresentationMap/IfcMappedItem; source body geometry retained once per variant', reopen_validated=True)


def preview(output, model, plan, variants, *, video=True):
    """Render actual retained IFC triangles; the movie moves only the camera."""
    import ifcopenshell
    import ifcopenshell.geom
    import numpy as np
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    import shutil
    import subprocess
    for name in ('geometry-preview.png', 'geometry-turntable.mp4'):
        (output / name).unlink(missing_ok=True)
    report = dict(status='hold', scope='Camera inspection of retained geometry only; not assembly, motion or collision simulation',
        tool_versions=dict(ifcopenshell=ifcopenshell.version, numpy=np.__version__, matplotlib=matplotlib.__version__), files=[])
    if not variants:
        return {**report, 'reason': 'No source IFC geometry available'}
    try:
        elevated = {r['product_variant'] for r in plan['instances'] if r.get('source_station_elevation') == 'elevated'} & set(variants)
        variant = max(elevated or variants, key=lambda name: variants[name].stat().st_size)
        station = next(row for row in plan['instances'] if row['product_variant'] == variant)
        f = ifcopenshell.open(str(output / 'model.ifc'))
        element = next(e for e in f.by_type('IfcElementAssembly') if e.Name == station['id'])
        settings = ifcopenshell.geom.settings(); settings.set(settings.USE_WORLD_COORDS, False)
        shape = ifcopenshell.geom.create_shape(settings, element)
        vertices = np.asarray(shape.geometry.verts).reshape(-1, 3)
        faces = np.asarray(shape.geometry.faces).reshape(-1, 3)
        if not len(faces) or not np.isfinite(vertices).all() or len(faces) > 500_000:
            raise ValueError('Missing/nonfinite/unbounded tessellation')
        sample_step = max(1, math.ceil(len(faces) / 16000)); shown = faces[::sample_step]
        bounds = np.array([vertices.min(0), vertices.max(0)]); centre = bounds.mean(0)
        triangles = (vertices - centre)[shown]
        fig = plt.figure(figsize=(8, 6), dpi=100, facecolor='#ecf1f5')
        ax = fig.add_subplot(projection='3d'); ax.set_proj_type('ortho')
        colours = plt.get_cmap('viridis')((vertices[shown].mean(1)[:, 2] - bounds[0, 2]) / max(bounds[1, 2] - bounds[0, 2], .001))
        collection = Poly3DCollection(triangles, facecolors=colours, edgecolor='none', alpha=1.)
        ax.add_collection3d(collection)
        span = np.maximum(bounds[1] - bounds[0], .01)
        for setter, i in ((ax.set_xlim, 0), (ax.set_ylim, 1), (ax.set_zlim, 2)): setter(-span[i] * .55, span[i] * .55)
        ax.set_box_aspect(span); ax.set_axis_off(); ax.view_init(elev=22, azim=-65)
        ax.set_title(station['id'] + '\n' + variant + ' retained geometry — provisional', fontsize=10)
        fig.text(.5, .03, 'Camera inspection only; site levels, foundations and engineering acceptance open.', ha='center', fontsize=8)
        fig.savefig(output / 'geometry-preview.png', dpi=100)
        report.update(status='rendered', representative_station=station['id'], source_variant=variant,
            source_ifc_sha256=digest(variants[variant]), native_vertex_count=len(vertices), native_triangle_count=len(faces),
            rendered_triangle_count=len(shown), local_geometry_bounds_m=bounds.tolist(), files=['geometry-preview.png'])
        ffmpeg = shutil.which('ffmpeg')
        if video and ffmpeg:
            report['tool_versions']['ffmpeg'] = subprocess.check_output([ffmpeg, '-version'], text=True).splitlines()[0]
            report['ffmpeg_binary_sha256'] = digest(ffmpeg)
            command = [ffmpeg, '-hide_banner', '-loglevel', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgba',
                '-s', '800x600', '-r', '8', '-i', '-', '-an', '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
                '-movflags', '+faststart', str(output / 'geometry-turntable.mp4')]
            process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
            try:
                for frame in range(24):
                    ax.view_init(elev=22, azim=-65 + 360 * frame / 24)
                    fig.canvas.draw(); process.stdin.write(fig.canvas.buffer_rgba())
                process.stdin.close(); stderr = process.stderr.read(); code = process.wait(timeout=30)
                if code: raise ValueError('FFmpeg failed: ' + stderr.decode(errors='replace')[:500])
                report['files'].append('geometry-turntable.mp4'); report['video_duration_s'] = 3
                report['video_status'] = 'rendered-camera-only'
            except Exception:
                process.kill(); process.wait(); raise
        else:
            report['video_status'] = 'hold; FFmpeg unavailable' if video else 'not-requested'
        plt.close(fig)
    except Exception as exc:
        report['status'] = 'hold' if not report['files'] else 'image-rendered-video-hold'
        report['reason'] = type(exc).__name__ + ': ' + str(exc)[:800]
        (output / 'geometry-turntable.mp4').unlink(missing_ok=True)
    return report


def generate(city, output=None, root=ROOT):
    city = Path(city).resolve(); output = Path(output or city / 'engineering/federation').resolve()
    design, stations, locations, variants, hashes = inputs(city, root)
    plan = layout(city, design, stations, locations)
    output.mkdir(parents=True, exist_ok=True)
    available = {name: path for name, path in variants.items() if path is not None}
    geometry_plan = {**plan, 'instances': [row for row in plan['instances'] if row['product_variant'] in available]}
    if available:
        model = write_ifc(output / 'model.ifc', geometry_plan, available, design['city']['slug'])
        model['geometry_instances'] = model['station_instances']
        model['station_instances'] = len(plan['instances'])
    else:
        (output / 'model.ifc').unlink(missing_ok=True)
        model = dict(schema=None, station_instances=len(plan['instances']), geometry_instances=0,
            variant_geometry={}, reopen_validated=False)
    missing = sorted(set(variants) - set(available))
    model['missing_geometry_variants'] = missing
    model['geometry_status'] = 'geometry-unavailable' if not available else 'partial-geometry' if missing else 'placed-retained-geometry'
    model['source_mode'] = 'city-connected-build' if (city / 'engineering/connected-build/manifest.json').is_file() else 'shared-archetypes-for-own-city'
    plan['instances'] = [{**r, 'geometry_status': 'source-geometry-unavailable' if r['product_variant'] in missing else 'retained-source-geometry'} for r in plan['instances']]
    features = [dict(type='Feature', geometry=dict(type='Point', coordinates=[r['longitude'], r['latitude']]), properties=r) for r in plan['instances']]
    (output / 'layout.geojson').write_bytes(encoded(dict(type='FeatureCollection', features=features)))
    (output / 'instances.json').write_bytes(encoded(plan))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(10, 10), layout='constrained')
    for variant in sorted(variants):
        selected = [r for r in plan['instances'] if r['product_variant'] == variant]
        ax.scatter([r['translation_m'][0] / 1000 for r in selected], [r['translation_m'][1] / 1000 for r in selected], s=15, label=variant)
    ax.set_aspect('equal'); ax.set_xlabel('Local projected east / km'); ax.set_ylabel('Local projected north / km')
    ax.set_title(design['city']['slug'] + ' — station geometry instances\nPlanning coordination; unsurveyed levels and foundations')
    ax.legend(fontsize=7); ax.grid(alpha=.2); fig.savefig(output / 'layout.png', dpi=140); plt.close(fig)
    media = preview(output, model, plan, available)
    links = (['model.ifc'] if available else []) + ['instances.json', 'layout.geojson', 'layout.png'] + media['files']
    html = '<!doctype html><meta charset="utf-8"><title>Station federation</title><h1>' + escape(design['city']['slug']) + ' station geometry federation</h1><p>' + str(len(stations)) + ' placed instances; ' + str(len(variants)) + ' archetypes; geometry status: ' + escape(model['geometry_status']) + '. Missing geometry is held, never replaced by fabricated envelopes. Planning coordination only.</p><p>' + ' '.join('<a href="' + n + '">' + n + '</a>' for n in links) + '</p><img width="800" src="layout.png"><ul>' + ''.join('<li>' + escape(h) + '</li>' for h in HOLDS) + '</ul>'
    if 'geometry-preview.png' in media['files']: html += '<h2>Retained geometry inspection</h2><p>' + escape(media['scope']) + '</p><img width=800 src=geometry-preview.png>'
    if 'geometry-turntable.mp4' in media['files']: html += '<video width=800 controls src=geometry-turntable.mp4></video>'
    (output / 'index.html').write_text(html)
    report = dict(schema=SCHEMA, city=design['city']['slug'], source_sha256=hashes, generator_sha256=digest(Path(__file__)), model=model, media=media,
        holds=HOLDS, engineering_qualified=False, manufacturing_release=False, physical_release=False,
        output_sha256={name: digest(output / name) for name in links + ['index.html']})
    if sum((output / name).stat().st_size for name in report['output_sha256']) > MAX_BYTES:
        raise ValueError('Federation exceeds bounded 50 MiB package')
    (output / 'summary.json').write_bytes(encoded(report))
    verify(city, output, root)
    return report


def verify(city, output=None, root=ROOT):
    import ifcopenshell
    import ifcopenshell.util.placement
    city = Path(city).resolve(); output = Path(output or city / 'engineering/federation').resolve()
    report = json.loads((output / 'summary.json').read_text())
    design, stations, locations, variants, hashes = inputs(city, root)
    if report.get('schema') != SCHEMA or report.get('source_sha256') != hashes or report.get('generator_sha256') != digest(Path(__file__)):
        raise ValueError('Stale federation source receipt')
    if any(report.get(k) is not False for k in ('engineering_qualified', 'manufacturing_release', 'physical_release')):
        raise ValueError('Unsupported federation release claim')
    expected = layout(city, design, stations, locations)
    available = {name for name, path in variants.items() if path is not None}
    expected['instances'] = [{**r, 'geometry_status': 'retained-source-geometry' if r['product_variant'] in available else 'source-geometry-unavailable'} for r in expected['instances']]
    if json.loads((output / 'instances.json').read_text()) != expected: raise ValueError('Changed instance placements')
    for name, expected_hash in report['output_sha256'].items():
        if Path(name).name != name or digest(output / name) != expected_hash: raise ValueError('Changed federation output')
    if not available:
        if (output / 'model.ifc').exists() or report['model']['geometry_instances'] != 0 or report['model']['geometry_status'] != 'geometry-unavailable':
            raise ValueError('Missing source geometry cannot create IFC model')
        return report
    f = ifcopenshell.open(str(output / 'model.ifc'))
    assemblies = {s.Name: s for s in f.by_type('IfcElementAssembly')}
    if set(assemblies) != {s['id'] for s in expected['instances'] if s['product_variant'] in available}: raise ValueError('IFC station inventory differs')
    for row in expected['instances']:
        if row['product_variant'] not in available: continue
        matrix = ifcopenshell.util.placement.get_local_placement(assemblies[row['id']].ObjectPlacement)
        if any(abs(matrix[i, 3] - row['translation_m'][i]) > 1e-7 for i in range(3)) or abs(math.atan2(matrix[1, 0], matrix[0, 0]) - row['rotation_about_z_rad']) > 1e-7:
            raise ValueError('IFC placement differs')
        if not assemblies[row['id']].Representation: raise ValueError('IFC station geometry missing')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--design', type=Path, required=True)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    report = (verify if args.check else generate)(args.design.resolve().parent, args.output)
    print(json.dumps(dict(city=report['city'], stations=report['model']['station_instances'],
        variants=len(report['model']['variant_geometry']), engineering_qualified=False)))


if __name__ == '__main__': main()
