"""Pinned planning-water evidence; opt-in civil hypotheses, never site approval."""
from collections import defaultdict
from copy import deepcopy
import gzip
from hashlib import sha1, sha256
import io
import json
import math
import os
from pathlib import Path
import subprocess
import tempfile

from engineering.station_rail import ROOT
from engineering.station_rail.common import digest, identity

PRODUCER = 'engineering/outline/civil_evidence.py'
PINNED_REVISION = 'a0389044828f661fe74ff314aed7fbe26748638a'
MAX_MASK_BYTES = 64 * 1024 * 1024
FLAGS = dict(physical_accepted=False, engineering_accepted=False, manufacturing_release=False,
             operating_release=False, selected_reference_changed=False, movement_authority=False)
LIMITATIONS = [
    'WorldCover 2021/retained OSM is historical planning evidence, not a current shoreline or site survey.',
    'Twenty-metre cells do not resolve narrow streams, flooding, wetlands, scour, foundations or clearances.',
    'Dry legacy bridges may represent unverified obstructions: retain a nonzero priced reserve or a hold.',
    'Water mapping does not design a bridge or establish physical acceptance.',
]


def _git(root, *args):
    return subprocess.check_output(['git', '-C', str(root),
        '-c', 'core.deltaBaseCacheLimit=8m', '-c', 'core.packedGitWindowSize=8m',
        '-c', 'core.packedGitLimit=64m', *args])


def _blob(root, obj, cache):
    if obj['size'] > MAX_MASK_BYTES:
        raise ValueError('Historical blob exceeds evidence resource budget')
    path = cache / obj['oid']
    if not path.exists():
        data = _git(root, 'cat-file', 'blob', obj['oid'])
        with tempfile.NamedTemporaryFile(dir=cache, delete=False) as stream:
            stream.write(data); temporary = Path(stream.name)
        try:
            temporary.chmod(0o444)
            try: os.link(temporary, path)
            except FileExistsError: pass
        finally: temporary.unlink(missing_ok=True)
    data = path.read_bytes()
    if len(data) != obj['size'] or sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest() != obj['oid']:
        raise ValueError('Immutable historical cache object differs')
    return data


def prepare(root=ROOT, cache=None):
    """Index retained Git objects without downloads; cache is a private run folder.

    Only one city mask is loaded per evaluation; cache location is not identity.
    Historical source files are never restored into the active checkout.
    """
    if cache is None: raise ValueError('Explicit private evidence cache required')
    root, cache = Path(root).resolve(), Path(cache).resolve(); cache.mkdir(parents=True, exist_ok=True)
    revision = _git(root, 'rev-parse', PINNED_REVISION + '^{commit}').decode().strip()
    if revision != PINNED_REVISION: raise ValueError('Historical revision differs')
    entries = {}
    for row in _git(root, 'ls-tree', '-rl', revision, '--', 'cities/catalogue').decode().splitlines():
        header, path = row.split('\t', 1); _, kind, oid, size = header.split()
        if kind == 'blob' and '/engineering/alignment/' in path: entries[path] = dict(oid=oid, size=int(size))
    cities = {}
    for path in sorted(entries):
        if not path.endswith('/engineering/alignment/water-source-receipt.json'): continue
        directory = path.rsplit('/', 1)[0]
        names = {k: directory + '/' + n for k, n in [('receipt', 'water-source-receipt.json'),
            ('grid', 'planning-grid.json'), ('mask', 'planning-water-mask.bin.gz')]}
        if any(n not in entries for n in names.values()): raise ValueError('Incomplete historical evidence triplet')
        payload = {k: _blob(root, entries[n], cache) for k, n in names.items() if k != 'mask'}
        receipt, grid = json.loads(payload['receipt']), json.loads(payload['grid'])
        if receipt.get('schema_version') != 2: raise ValueError('Unsupported historical receipt')
        if receipt.get('sources_sha256', {}).get(names['grid']) != sha256(payload['grid']).hexdigest():
            raise ValueError('Historical grid receipt hash differs')
        if any(grid[k] <= 0 for k in ('width', 'height', 'cell_m', 'm_per_deg_lat', 'm_per_deg_lon')):
            raise ValueError('Positive explicit historical projection required')
        if grid['width'] * grid['height'] > MAX_MASK_BYTES: raise ValueError('Historical mask exceeds per-city budget')
        slug = receipt['city']
        if slug in cities: raise ValueError('Duplicate historical city slug')
        cities[slug] = dict(paths=names, objects={k: entries[n] for k, n in names.items()}, grid=grid,
            receipt=receipt, sha256={k: sha256(v).hexdigest() for k, v in payload.items()})
    if not cities: raise ValueError('No retained historical city evidence')
    sources = {PRODUCER: digest(__file__)}
    context_id = identity(dict(revision=revision, cities={s: z['objects'] for s, z in cities.items()}, sources=sources))
    return dict(root=str(root), cache=str(cache), revision=revision, cities=cities,
                source_sha256=sources, context_id=context_id)


def _append(rows, a, b, status):
    if b <= a: return
    if rows and rows[-1]['status'] == status and abs(rows[-1]['to_m'] - a) < 1e-7: rows[-1]['to_m'] = b
    else: rows.append(dict(from_m=a, to_m=b, status=status))


def _intervals(line, grid, mask):
    coordinates, chain = line['coordinates'], line.get('coordinate_chainages_m')
    if not chain or len(chain) != len(coordinates) or len(chain) < 2:
        raise ValueError('Exact selected coordinates and matching chainages required')
    if any(not math.isfinite(float(x)) for x in chain) or abs(chain[0]) > 1e-7 or abs(chain[-1] - line['route_m']) > .02:
        raise ValueError('Selected chainages do not cover route')
    if any(b < a for a, b in zip(chain, chain[1:])): raise ValueError('Selected chainages must be ordered')
    def project(point):
        if len(point) < 2 or any(not math.isfinite(float(x)) for x in point[:2]): raise ValueError('Finite WGS84 required')
        lon, lat = point[:2]
        if not -180 <= lon <= 180 or not -90 <= lat <= 90: raise ValueError('WGS84 outside domain')
        return ((lon-grid['bbox_west'])*grid['m_per_deg_lon']/grid['cell_m'],
                (grid['bbox_north']-lat)*grid['m_per_deg_lat']/grid['cell_m'])
    rows = []
    for first, second, a, b in zip(coordinates, coordinates[1:], chain, chain[1:]):
        if b == a: continue
        x0, y0 = project(first); x1, y1 = project(second); cuts = {0., 1.}
        # Exact cell-boundary traversal, including long chords with dry endpoints.
        for v0, v1, limit in ((x0, x1, grid['width']), (y0, y1, grid['height'])):
            if v0 == v1: continue
            lo, hi = sorted((v0, v1))
            for edge in range(max(0, math.ceil(lo)), min(limit, math.floor(hi))+1):
                t = (edge-v0)/(v1-v0)
                if 0 < t < 1: cuts.add(t)
        cuts = sorted(cuts)
        for t0, t1 in zip(cuts, cuts[1:]):
            t = (t0+t1)/2; col, row = math.floor(x0+t*(x1-x0)), math.floor(y0+t*(y1-y0))
            if not 0 <= row < grid['height'] or not 0 <= col < grid['width']: status = 'out-of-domain'
            else:
                value = mask[row*grid['width']+col]
                status = 'unknown' if value == 255 else ('wet' if value else 'dry')
            _append(rows, a+t0*(b-a), a+t1*(b-a), status)
    if not rows or abs(rows[-1]['to_m']-line['route_m']) > .02: raise ValueError('Traversal did not cover selected route')
    return rows


def _legacy(line, city):
    rows = sorted((z for z in city.get('civil_segments', []) if z['line_id'] == line['line_id']), key=lambda z:z['from_m'])
    if not rows: rows = [dict(line_id=line['line_id'], **{'class':'elevated'}, from_m=0., to_m=line['route_m'], assumed=True)]
    prior = 0.
    for row in rows:
        if row['class'] not in ('bridge','elevated','at-grade','tunnel') or abs(row['from_m']-prior) > .02 or row['to_m'] <= row['from_m']:
            raise ValueError('Legacy civil intervals are not a complete typed control')
        prior = row['to_m']
    if abs(prior-line['route_m']) > .02: raise ValueError('Legacy civil control does not cover route')
    return rows


def evaluate(city_input, prepared):
    """Return sealed water intervals and legacy corroboration on actual geometry."""
    if city_input.get('input_id') != identity({k:v for k,v in city_input.items() if k!='input_id'}): raise ValueError('Sealed city input required')
    if prepared['source_sha256'] != {PRODUCER:digest(__file__)}: raise ValueError('Evaluator source changed')
    slug = city_input['city']['slug']
    if slug not in prepared['cities']: raise ValueError('City absent from pinned historical evidence')
    entry = prepared['cities'][slug]; grid = entry['grid']; receipt = entry['receipt']
    for key, record in [('grid', grid), ('receipt', receipt)]:
        if json.loads(_blob(prepared['root'], entry['objects'][key], Path(prepared['cache']))) != record:
            raise ValueError('Prepared historical '+key+' differs from immutable evidence')
    compressed = _blob(prepared['root'], entry['objects']['mask'], Path(prepared['cache']))
    with gzip.GzipFile(fileobj=io.BytesIO(compressed)) as stream: mask = stream.read(MAX_MASK_BYTES+1)
    if len(mask) != grid['width']*grid['height'] or sha256(mask).hexdigest() != receipt['mask_sha256']:
        raise ValueError('Historical mask dimensions or receipt hash differs')
    if set(mask)-{0,25,50,75,100,255}: raise ValueError('Unsupported mask coverage value')
    line_ids=[z['line_id'] for z in city_input['lines']]
    if not line_ids or len(line_ids)!=len(set(line_ids)): raise ValueError('Unique nonempty selected city lines required')
    lines=[]; totals=defaultdict(float); overlaps_total=defaultdict(float)
    for line in city_input['lines']:
        water = _intervals(line, grid, mask); legacy = _legacy(line, city_input); overlaps=[]; j=0
        for row in water:
            totals[row['status']] += row['to_m']-row['from_m']
            while j<len(legacy) and legacy[j]['to_m']<=row['from_m']+1e-8: j+=1
            k=j
            while k<len(legacy) and legacy[k]['from_m']<row['to_m']-1e-8:
                a,b=max(row['from_m'],legacy[k]['from_m']),min(row['to_m'],legacy[k]['to_m'])
                if b>a:
                    overlaps.append(dict(from_m=a,to_m=b,status=row['status'],legacy_class=legacy[k]['class']))
                    overlaps_total[legacy[k]['class']+':'+row['status']] += b-a
                k+=1
        lines.append(dict(line_id=line['line_id'],route_m=line['route_m'],water_intervals=water,legacy_overlap_intervals=overlaps))
    historical = {k:dict(path=entry['paths'][k],git_blob=entry['objects'][k]['oid'],
        sha256=sha256(compressed).hexdigest() if k=='mask' else entry['sha256'][k]) for k in ('grid','receipt','mask')}
    value=dict(schema='osr-city-civil-water-evidence/1',city_input_id=city_input['input_id'],city_slug=slug,
        context_id=prepared['context_id'],historical_revision=prepared['revision'],historical_sources=historical,
        mask_raw_sha256=receipt['mask_sha256'],source_description=receipt['source'],grid=deepcopy(grid),
        source_attribution=receipt.get('attribution'),source_license=receipt.get('license'),
        method='Exact WGS84 segment/grid-boundary traversal; any positive planning-cell coverage is wet.',
        geometry_unchanged=True,lines=lines,route_m_by_water_status=dict(totals),
        legacy_class_water_overlap_m=dict(sorted(overlaps_total.items())),
        dry_bridge_reclassified_m=overlaps_total.get('bridge:dry',0.),
        limitations=LIMITATIONS+receipt.get('limitations',[]),source_sha256=prepared['source_sha256'],**FLAGS)
    value['evaluation_id']=identity(value); return value


def revise(city_input, report):
    """Opt-in research input; mandatory civil interfaces and reserve holds persist."""
    if report.get('evaluation_id') != identity({k:v for k,v in report.items() if k!='evaluation_id'}) or report['city_input_id']!=city_input.get('input_id'):
        raise ValueError('Matching immutable water report and city input required')
    if city_input.get('input_id') != identity({k:v for k,v in city_input.items() if k!='input_id'}): raise ValueError('Sealed city input required')
    segments=[]; holds=[]; reserve=0.
    for line in report['lines']:
        for row in line['legacy_overlap_intervals']:
            kind,status=row['legacy_class'],row['status']
            if status=='wet' and kind not in ('tunnel','at-grade'): kind='bridge'
            elif status=='dry' and kind=='bridge': kind='elevated'; reserve+=row['to_m']-row['from_m']
            if status in ('unknown','out-of-domain') or (status=='wet' and kind in ('tunnel','at-grade')):
                holds.append(dict(line_id=line['line_id'],**row,reason='Unavailable evidence or conflict with preserved mandatory civil interface'))
            segments.append(dict(line_id=line['line_id'],**{'class':kind},from_m=row['from_m'],to_m=row['to_m'],assumed=True,
                water_evidence_status=status,legacy_class=row['legacy_class'],
                unverified_obstruction_reserve_required=status=='dry' and row['legacy_class']=='bridge'))
    value=deepcopy(city_input); value.pop('input_id')
    value.update(civil_segments=segments,ancestry=dict(parent_input_id=city_input['input_id'],
        revision_operator='historical-water-corroborated-civil-research',water_evaluation_id=report['evaluation_id']),
        civil_evidence_hypothesis=dict(kind='historical-water-corroborated-civil-research',legacy_control_input_id=city_input['input_id'],
            water_evaluation_id=report['evaluation_id'],historical_revision=report['historical_revision'],historical_sources=report['historical_sources'],
            geometry_unchanged=True,outline_selection_status='conditional-research-hypothesis',
            dry_legacy_bridge_obstruction_reserve_route_m=reserve,nonzero_obstruction_reserve_or_hold_required=reserve>0,
            interface_holds=holds,limitations=deepcopy(report['limitations'])),**FLAGS)
    value['civil_evidence']=dict(report_id=report['evaluation_id'],dry_bridge_reclassified_m=reserve,
        route_m_by_water_status=deepcopy(report['route_m_by_water_status']),
        historical_revision=report['historical_revision'],nonzero_obstruction_reserve_or_hold_required=reserve>0,
        interface_hold_count=len(holds),comparison_only=True,geometry_unchanged=True)
    value['source_sha256']={**value.get('source_sha256',{}),**report['source_sha256']}
    value['civil_hypothesis_id']=identity(value['civil_evidence_hypothesis'])
    value['input_id']=identity(value); return value
