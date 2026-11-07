"""Bounded native GIS handoff; no railway recalculation or baseline selection.

RustGIS owns import, project serialization, styling, export and rendering. Python
authenticates OSR inputs, preserves exact source files and verifies round trips.
"""
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import fcntl
import gzip
import io
import json
import os
import re
import shutil
import subprocess
import tempfile
import time
import zipfile

from engineering.station_rail import ROOT, FLAGS
from engineering.station_rail.common import encoded, identity, digest

PACKAGE = Path(__file__).parent
SCHEMA = 'osr-rustgis-city/1'
LAYERS = ('routes', 'stations', 'platforms', 'original_access_markers',
          'interchanges', 'civil_segments', 'access_connectors', 'unlocated_requirements')
INDEX = '_osr_source_index'
COLOURS = {'earth': '#f2ecdd', 'landuse': '#e2ebd8', 'buildings': '#d8d4cc',
           'boundaries': '#b3aea2', 'roads': '#cbbba2', 'places': '#7b7770', 'water': '#bbdce8'}


def lock_record():
    return json.loads((PACKAGE/'backend.json').read_bytes())


def executable():
    value = lock_record()
    path = shutil.which('rustgis-cli')
    if not path:
        path = str(Path.home()/'.local/bin/rustgis-cli')
    p = Path(path).resolve()
    if not p.is_file():
        raise ValueError('Pinned RustGIS CLI missing/different; run ./osr gis install')
    stat = p.stat()
    _binary_digest(str(p), (stat.st_size, stat.st_mtime_ns, stat.st_ctime_ns, stat.st_ino),
                   value['executables_sha256']['rustgis-cli'])
    return p


@lru_cache(maxsize=4)
def _binary_digest(path, signature, expected):
    if digest(path) != expected:
        raise ValueError('Pinned RustGIS executable checksum differs')
    stat = Path(path).stat()
    if signature != (stat.st_size, stat.st_mtime_ns, stat.st_ctime_ns, stat.st_ino):
        raise ValueError('RustGIS changed while being checked')


def source_hashes(root=ROOT):
    root = Path(root)
    return {p.relative_to(root).as_posix(): digest(p) for p in sorted((root/'engineering/rustgis').iterdir())
            if p.suffix in ('.py', '.json')}


def cache_root():
    return Path(os.environ.get('XDG_CACHE_HOME', str(Path.home()/'.cache')))/'opensourcerail/rustgis'


def prune_cache(budget=256*1024**2, keep=()):
    """Evict reproducible successful ZIPs only; preserve receipts, logs and failures."""
    root = cache_root();root.mkdir(parents=True, exist_ok=True)
    keep = {Path(p).resolve() for p in keep}
    with (root/'pruning.lock').open('a+') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        files = [p for p in root.glob('*/*/*.zip') if not p.is_symlink() and (p.parent/'manifest.json').is_file()]
        total = sum(p.stat().st_size for p in files);removed = []
        for p in sorted(files, key=lambda p:p.stat().st_mtime_ns):
            if total <= budget:break
            if p.parent.resolve() in keep:continue
            with (p.parent/'coordinator.lock').open('a+') as active:
                try:fcntl.flock(active, fcntl.LOCK_EX|fcntl.LOCK_NB)
                except BlockingIOError:continue
                r = json.loads((p.parent/'manifest.json').read_bytes())
                if r.get('schema') != SCHEMA+'/cache' or digest(p) != r['archive_sha256']:
                    continue
                size = p.stat().st_size
                event = dict(schema=SCHEMA+'/eviction', manifest_id=r['manifest']['manifest_id'],
                    archive_sha256=r['archive_sha256'], bytes=size,
                    reason='Reproducible successful export evicted from bounded 256 MiB cache; canonical inputs and logs retained')
                (p.parent/('evicted-'+event['manifest_id']+'.json')).write_bytes(encoded(event))
                p.unlink();total -= size;removed.append(event)
        return dict(retained_archive_bytes=total, evicted=len(removed), budget_bytes=budget)


def _sealed(value, key):
    if value.get(key) != identity({k: v for k, v in value.items() if k != key}):
        raise ValueError('Changed GIS identity: '+key)


def _local(root, name):
    p = Path(name)
    if p.is_absolute() or '..' in p.parts or (Path(root)/p).resolve() != Path(root)/p:
        raise ValueError('Ordinary relative GIS source required')
    return Path(root)/p


def inputs(root=ROOT):
    from engineering.city_reports import publication
    root = Path(root).resolve()
    manifest = publication._manifest(root)
    am, cm, rows = publication._inputs(root)
    if manifest['atlas_manifest_id'] != am['manifest_id'] or manifest['outline_manifest_id'] != cm['manifest_id']:
        raise ValueError('GIS and outline publication epochs differ')
    return root, manifest, am, cm, rows


def city_input(slug, context):
    from engineering.city_reports import publication
    root, parent, am, cm, rows = context
    if not re.fullmatch('[a-z0-9]+(?:-[a-z0-9]+)*', slug) or slug not in rows:
        raise ValueError('Known city slug required')
    row = rows[slug]
    folder = _local(root, row['path']+'/engineering/outline')
    m = json.loads((folder/'manifest.json').read_bytes())
    _sealed(m, 'manifest_id')
    key = row['path']+'/engineering/outline/manifest.json'
    if parent['files_sha256'].get(key) != digest(folder/'manifest.json'):
        raise ValueError('Unbound city dossier manifest')
    if m.get('city_slug') != slug or m.get('source_sha256') != parent['source_sha256']:
        raise ValueError('Mixed city GIS sources')
    packet, detail, geography, background, ap, dp = publication._city_inputs(root, row, am, cm)
    _sealed(packet, 'packet_id')
    if m['atlas_packet_id'] != packet['packet_id']:
        raise ValueError('Mixed GIS and city packet')
    files = {}
    for name, h in m['files_sha256'].items():
        p = _local(folder, name)
        if digest(p) != h:
            raise ValueError('City GIS/table changed: '+name)
        # Preserve all original tables and GIS, not duplicate the SVG/delivery model.
        if name.endswith('.csv') or name == 'summary.json' or name.startswith('gis/'):
            files['sources/'+name] = p.read_bytes()
    files['sources/atlas.json.gz'] = ap.read_bytes()
    if packet.get('map_context'):
        files['sources/map-context.json.gz'] = _local(root, packet['map_context']['path']).read_bytes()
    layers = {}
    for name in LAYERS:
        layers[name] = json.loads(gzip.decompress(files['sources/gis/'+name+'.geojson.gz']))
        if layers[name].get('packet_id') != packet['packet_id']:
            raise ValueError('GIS layer packet differs: '+name)
    return packet, background, files, layers, m


def prepared(value):
    """Keep original IDs separately from RustGIS's numeric local feature IDs."""
    out = deepcopy(value)
    for i, feature in enumerate(out['features']):
        props = feature.setdefault('properties', {})
        if INDEX in props:
            raise ValueError('Reserved GIS correspondence key already present')
        props[INDEX] = i
    return out


def context_layers(context):
    """Never close a water line into an area; keep polygon rings/holes together."""
    out = {}
    for name in ('earth', 'landuse', 'buildings', 'boundaries', 'water', 'roads', 'places'):
        groups = {}
        for f in (context or {}).get('layers', {}).get(name, []):
            t = (f.get('geometry') or {}).get('type')
            kind = {'Point': 'points', 'MultiPoint': 'points', 'LineString': 'lines',
                    'MultiLineString': 'lines', 'Polygon': 'areas', 'MultiPolygon': 'areas'}.get(t)
            if not kind:
                raise ValueError('Unsupported context geometry: '+str(t))
            groups.setdefault(kind, []).append(f)
        for kind, fs in groups.items():
            out['context_'+name+'_'+kind] = dict(type='FeatureCollection', features=deepcopy(fs))
    return out


def native(args, directory, label):
    """No shell, AI, saved secrets, plugins, external tiles or implicit services."""
    directory = Path(directory)
    started = time.monotonic()
    limiter = shutil.which('prlimit')
    if not limiter:
        raise ValueError('prlimit is required for bounded native GIS workers')
    cmd = [limiter, '--cpu=60', '--as='+str(2*1024**3), '--', str(executable()), *args]
    failure = None;code = None
    try:
        with (directory/(label+'.stdout')).open('wb') as out, (directory/(label+'.stderr')).open('wb') as err:
            proc = subprocess.run(cmd, cwd=directory, stdout=out, stderr=err,
                                  timeout=75, start_new_session=True)
            code = proc.returncode
    except (subprocess.TimeoutExpired, OSError) as exc:
        failure = exc
    result = dict(arguments=args, exit_code=code, wall_s=time.monotonic()-started,
                  failure=str(failure) if failure else None,
                  stdout_sha256=digest(directory/(label+'.stdout')),
                  stderr_sha256=digest(directory/(label+'.stderr')))
    (directory/(label+'.execution.json')).write_bytes(encoded(result))
    if failure or code:
        raise ValueError('RustGIS '+label+' failed; retained logs: '+str(directory))
    return result


def _cmd(command_id, **params):
    return ['--cmd', command_id+'='+json.dumps(params, separators=(',', ':'), allow_nan=False)]


def commands(layer_files, packet):
    args = ['run', '--no-plugins', *_cmd('map.basemap', name='blank')]
    for name in layer_files:
        args += _cmd('layer.addData', path='layers/'+name+'.geojson', name=name)
        if not any(f.get('geometry') is not None for f in layer_files[name]['features']):
            # Native RustGIS correctly imports all-null/empty geometry as a table.
            continue
        if name.startswith('context_'):
            color = COLOURS[name.split('_')[1]]
            args += _cmd('layer.color', layer=name, color=color)
            args += _cmd('layer.outline', layer=name, color=color, width=.5)
            # Separate line-only datasets have no polygon fill in the native renderer.
            if name.endswith('_points'):
                args += _cmd('layer.marker', layer=name, size=2)
        elif name == 'routes':
            args += _cmd('layer.symbolBy', layer=name, stroke='colour', strokeWidth='2.5')
        elif name in ('stations', 'interchanges'):
            args += _cmd('layer.color', layer=name, color='#ffffff')
            args += _cmd('layer.outline', layer=name, color='#233c48', width=1)
            args += _cmd('layer.marker', layer=name, size=5 if name == 'stations' else 7)
            if name == 'stations':
                args += _cmd('labels.field', layer=name, field='label')
                args += _cmd('labels.style', layer=name, size=8, halo=True)
                args += _cmd('labels.enable', layer=name, on=True)
        elif name == 'platforms':
            args += _cmd('layer.color', layer=name, color='#41444d')
            args += _cmd('layer.outline', layer=name, width=3)
        else:
            args += _cmd('layer.visibility', layer=name, visible=False)
    # Last imported is topmost. Keep station labels above platforms and routes.
    for name in ('routes', 'platforms', 'stations', 'interchanges'):
        if any(f.get('geometry') is not None for f in layer_files[name]['features']):
            args += _cmd('layer.move', layer=name, to=0)
    args += _cmd('layer.zoomTo', layer='routes')
    return args


def _geometry(value):
    """RustGIS normalizes single/multipart geometry; compare equivalent topology."""
    if value is None:
        return None
    t, c = value['type'], value['coordinates']
    return ({'Point':'MultiPoint', 'LineString':'MultiLineString', 'Polygon':'MultiPolygon'}.get(t, t),
            [c] if t in ('Point', 'LineString', 'Polygon') else c)


def _same_numbers(a, b):
    if isinstance(a, bool) or isinstance(b, bool):
        return type(a) is type(b) and a == b
    if isinstance(a, (int, float)) and not isinstance(a, bool) and isinstance(b, (int, float)):
        return abs(a-b) <= 1e-12
    if isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)):
        return len(a) == len(b) and all(_same_numbers(x, y) for x, y in zip(a, b))
    if isinstance(a, dict) and isinstance(b, dict):
        return set(a) == set(b) and all(_same_numbers(a[k], b[k]) for k in a)
    return a == b


def check_roundtrip(source, exported):
    """Verify coordinates, null geometry and every attribute, including nested JSON."""
    actual = exported['features']
    expected = source['features']
    if len(actual) != len(expected):
        raise ValueError('Native GIS feature count changed')
    seen = set()
    for f in actual:
        props = dict(f['properties']);i = props.pop(INDEX)
        if type(i) is not int or i in seen or not 0 <= i < len(expected):
            raise ValueError('Native GIS feature correspondence changed')
        seen.add(i);e = expected[i]
        if not _same_numbers(_geometry(e['geometry']), _geometry(f['geometry'])):
            raise ValueError('Native GIS geometry changed')
        original = e.get('properties', {})
        # Native datasets have a shared schema, adding nulls for absent fields.
        if set(original)-set(props) or any(v is not None for k,v in props.items() if k not in original):
            raise ValueError('Native GIS attribute keys changed')
        for k,v in original.items():
            out = props[k]
            if isinstance(v, (dict, list)) and isinstance(out, str):
                out = json.loads(out)
            if not _same_numbers(v, out):
                raise ValueError('Native GIS attribute changed: '+k)
    return dict(features=len(expected), unlocated=sum(f['geometry'] is None for f in expected),
                coordinates_tolerance_degrees=1e-12, all_properties_checked=True)


def zip_bytes(files):
    data = io.BytesIO()
    with zipfile.ZipFile(data, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for name, raw in sorted(files.items()):
            info = zipfile.ZipInfo(name, date_time=(2026, 11, 7, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, raw)
    return data.getvalue()


def export(slug, *, root=ROOT, context=None, output=None, preview=False):
    context = inputs(root) if context is None else context
    root = context[0]
    packet, background, originals, source_layers, dossier = city_input(slug, context)
    expected_inputs = dict(packet_id=packet['packet_id'], city=packet['city'], identity=packet['identity'],
        dossier_manifest_id=dossier['manifest_id'],
        input_sha256={k:sha256(v).hexdigest() for k,v in originals.items()})
    tool = lock_record();sources = source_hashes(root)
    key = identity(dict(packet_id=packet['packet_id'], dossier=dossier['manifest_id'],
        sources=sources, tool=tool, original_sha256={k:sha256(v).hexdigest() for k,v in originals.items()}, preview=preview))
    folder = (cache_root() if output is None else Path(output).resolve())/slug/key
    folder.mkdir(parents=True, exist_ok=True)
    with (folder/'coordinator.lock').open('a+') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        if (folder/'manifest.json').exists() and (folder/(slug+'.zip')).exists():
            result = verify(folder, root=root, expected_inputs=expected_inputs)
            os.utime(folder/(slug+'.zip'), None)
            if output is None:prune_cache(keep=(folder,))
            return result
        if (folder/'manifest.json').exists():
            previous = json.loads((folder/'manifest.json').read_bytes())
            (folder/('previous-'+previous['manifest']['manifest_id']+'.json')).write_bytes(encoded(previous))
        # Keep failed/interrupted native executions in separate attempt directories.
        run = Path(tempfile.mkdtemp(prefix='attempt-', dir=folder))
        (run/'layers').mkdir();(run/'roundtrip').mkdir()
        all_layers = {**context_layers(background), **source_layers}
        for name, layer in all_layers.items():
            (run/'layers'/str(name+'.geojson')).write_bytes(encoded(prepared(layer)))
        project = slug+'.rgis'
        first = native([*commands(all_layers, packet), '--save', project], run, 'build')
        args = ['run', '--no-plugins', '--project', project]
        for name in all_layers:
            if any(f.get('geometry') is not None for f in all_layers[name]['features']):
                args += _cmd('share.exportLayer', layer=name, path='roundtrip/'+name+'.geojson')
            else:
                args += _cmd('share.exportTable', table=name, path='roundtrip/'+name+'.geojson')
        args += _cmd('info.project')
        if preview:
            args += _cmd('share.exportMap', path='preview.png', width=1600, height=1000, dpi=96)
        second = native(args, run, 'reopen')
        roundtrips = {name:check_roundtrip(layer, json.loads((run/'roundtrip'/str(name+'.geojson')).read_bytes()))
                      for name,layer in all_layers.items()}
        contents = {**originals, project:(run/project).read_bytes()}
        # Native project includes all geometry; relative source files make it editable and portable.
        contents.update({'layers/'+name+'.geojson':(run/'layers'/str(name+'.geojson')).read_bytes() for name in all_layers})
        notice = ('Open '+project+' in RustGIS '+tool['version']+'.\n'
            'Coordinates are WGS84 lon/lat. Display projection is Web Mercator; do not use map pixels for quantities.\n'
            'Sources and tables are the exact selected OSR outline. Nested attributes are JSON text in native tables.\n'
            'Unlocated requirements remain null geometry. No physical, procurement or operating approval.\n'
            'Cost/service changes require the OSR evaluator; editing the GIS project does not reprice the railway.\n')
        contents['READ-ME.txt'] = notice.encode()
        m = dict(schema=SCHEMA, city=packet['city'], packet_id=packet['packet_id'],
            identity=packet['identity'], dossier_manifest_id=dossier['manifest_id'],
            tool=tool, source_sha256=sources, input_sha256={k:sha256(v).hexdigest() for k,v in originals.items()},
            key=key, project=project, display_projection='EPSG:3857', data_crs='EPSG:4326',
            roundtrip=roundtrips, attribution=(background or {}).get('attribution', []),
            features=sum(len(l['features']) for l in source_layers.values()),
            background_features=sum(len(l['features']) for n,l in all_layers.items() if n.startswith('context_')),
            native_executions=[first,second], files_sha256={k:sha256(v).hexdigest() for k,v in contents.items()},
            railway_calculations_changed=False, selected_reference_changed=False, **FLAGS)
        m['manifest_id'] = identity(m)
        contents['manifest.json'] = encoded(m)
        raw = zip_bytes(contents)
        (folder/(slug+'.zip')).write_bytes(raw)
        receipt = dict(schema=SCHEMA+'/cache', manifest=m, archive_sha256=sha256(raw).hexdigest(),
            preview_sha256=digest(run/'preview.png') if preview else None)
        if preview:
            shutil.copyfile(run/'preview.png', folder/'preview.png')
        (folder/'manifest.json').write_bytes(encoded(receipt))
        # Only duplicated successful working files are disposable; native logs stay.
        shutil.rmtree(run/'layers');shutil.rmtree(run/'roundtrip');(run/project).unlink()
        result = verify(folder, root=root, expected_inputs=expected_inputs)
        if output is None:prune_cache(keep=(folder,))
        return result


def verify(folder, *, root=ROOT, expected_inputs=None):
    folder = Path(folder);r = json.loads((folder/'manifest.json').read_bytes());m = r['manifest']
    _sealed(m, 'manifest_id')
    if m['schema'] != SCHEMA or m['source_sha256'] != source_hashes(root) or m['tool'] != lock_record():
        raise ValueError('GIS adapter/tool changed; rebuild export')
    if (any(m.get(k) is not v for k,v in FLAGS.items()) or m.get('selected_reference_changed') is not False
            or m.get('railway_calculations_changed') is not False):
        raise ValueError('GIS export cannot grant release')
    if expected_inputs is None:
        packet, _, originals, _, dossier = city_input(m['city']['slug'], inputs(root))
        expected_inputs = dict(packet_id=packet['packet_id'], city=packet['city'], identity=packet['identity'],
            dossier_manifest_id=dossier['manifest_id'],
            input_sha256={k:sha256(v).hexdigest() for k,v in originals.items()})
    if any(m.get(k) != v for k,v in expected_inputs.items()):
        raise ValueError('GIS upstream city changed; rebuild export')
    if any(m['files_sha256'].get(n) != h for n,h in m['input_sha256'].items()):
        raise ValueError('GIS exact source member differs from authenticated input')
    expected_key = identity(dict(packet_id=m['packet_id'], dossier=m['dossier_manifest_id'],
        sources=m['source_sha256'], tool=m['tool'], original_sha256=m['input_sha256'],
        preview=r['preview_sha256'] is not None))
    if m.get('key') != expected_key or folder.name != expected_key:
        raise ValueError('GIS cache request identity differs')
    archive = folder/(m['city']['slug']+'.zip')
    if digest(archive) != r['archive_sha256']:
        raise ValueError('GIS archive changed')
    with zipfile.ZipFile(archive) as z:
        if set(z.namelist()) != set(m['files_sha256'])|{'manifest.json'} or len(z.namelist()) != len(set(z.namelist())):
            raise ValueError('GIS archive members differ')
        if z.read('manifest.json') != encoded(m):
            raise ValueError('GIS archive manifest differs')
        for name,h in m['files_sha256'].items():
            if sha256(z.read(name)).hexdigest() != h:
                raise ValueError('GIS archive member changed')
    if r['preview_sha256'] is not None and digest(folder/'preview.png') != r['preview_sha256']:
        raise ValueError('GIS preview changed')
    return dict(verified=True, city=m['city']['slug'], archive=str(archive), bytes=archive.stat().st_size,
        manifest_id=m['manifest_id'], packet_id=m['packet_id'], features=m['features'],
        background_features=m['background_features'], layers=len(m['roundtrip']),
        native_reopen_verified=True, **FLAGS)
