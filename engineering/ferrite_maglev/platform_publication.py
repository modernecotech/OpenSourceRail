"""Portable planning workspace and any-city owner/builder delivery compiler."""
from hashlib import sha256
from pathlib import Path
import argparse
import gzip
import json
import re
from threading import RLock
from . import model, delivery_platform as platform

ROOT=model.ROOT
OUTPUT=ROOT/'docs/design-engine/ferrite-maglev/planning-platform'
SCHEMA='osr-owner-builder-publication/1'
UI=ROOT/'docs/workbench/planning'
_PAYLOAD_CACHE=None
_PAYLOAD_CACHE_LOCK=RLock()

def folders():
    index=json.loads((Path(__file__).parent/'city-index.json').read_bytes())
    return [platform.city_folder((ROOT/p).parent) for p in index['catalogue_design_paths']]

def source_paths():
    paths={Path(__file__),Path(platform.__file__),Path(platform.operating_plan.__file__),Path(platform.delivery_schedule.__file__),
        ROOT/'engineering/analysis/tests/test_ferrite_maglev_delivery_platform.py',
        ROOT/'tools/automation/planning-workspace.py',ROOT/'tools/automation/tests/verify-planning-workspace.mjs',ROOT/'tools/automation/tests/browser-launch.mjs',
        Path(__file__).parent/'city-index.json',*[p for p in UI.glob('*') if p.is_file()]}
    for folder in folders():
        paths.update([folder/'city.json',folder/'engineering/maglev/summary.json',*folder.glob('*.corridor.geojson')])
        paths.update(p for p in (folder/'site-context.json',folder/'engineering/mapping/walking-streets.geojson.gz',
            folder/'engineering/mapping/worldpop-2026-pixels.npz.gz',folder/'engineering/mapping/ghsl-2025-pixels.npz.gz',folder/'engineering/soil/sample-locations.geojson') if p.exists())
    paths.add(Path(__file__).parent/'data/pilot-destinations.json')
    return sorted(paths)

def sources():return {p.relative_to(ROOT).as_posix():sha256(p.read_bytes()).hexdigest() for p in source_paths()}

def _generate_payload():
    files={};rows=[]
    for folder in folders():
        p=platform.baseline(folder);platform.validate(p);layers=platform.planning_layers(p,folder);slug=p['city']
        plan_name='cities/'+slug+'.json.gz';layer_name='layers/'+slug+'.json.gz'
        files[plan_name]=gzip.compress(platform.encoded(p),compresslevel=6,mtime=0);files[layer_name]=gzip.compress(platform.encoded(layers),compresslevel=6,mtime=0)
        city=json.loads((folder/'city.json').read_bytes())
        rows.append(dict(city=slug,label=city.get('name',slug),folder=folder.relative_to(ROOT).as_posix(),plan=plan_name,layers=layer_name,
            revision_sha256=p['revision_sha256'],lines=len(p['lines']),stops=sum(len(l['stops']) for l in p['lines']),
            available_layers=sum(l['available'] for l in layers['layers']),planning_holds=len(platform.issues(p))))
    index=dict(schema=SCHEMA,cities=sorted(rows,key=lambda r:r['label']),layer_count=len(platform.LAYERS),
        workspaces=[dict(name='Owner: project and commercial records',url='http://127.0.0.1:18088/app/project',action='Open authenticated project workspace',scope='Native ERP projects, tasks and commercial records; actual permissions apply.'),
            dict(name='Builder: manufacturing and purchasing',url='http://127.0.0.1:18088/app/work-order',action='Open manufacturing workspace',scope='Native BOMs, material requests, purchasing, work orders and inspection.'),
            dict(name='Operator: assets and maintenance',url='http://127.0.0.1:18088/maglev-pilot',action='Open current serial lifecycle',scope='Exact draft candidate, failed inspection/rework, serial installation, maintenance and independent simulated business review.'),
            dict(name='People and competence',url='http://127.0.0.1:18088/app/employee',action='Open workforce records',scope='Native employee/competence records where installed and permitted; a link does not install an HR module.'),
            dict(name='Operations observation',url='http://127.0.0.1:1888/home',action='Open authenticated FUXA',scope='Observation and alarms. No motion commands or physical handback.')],**platform.FLAGS)
    files['index.json']=platform.encoded(index)
    files['README.md']=('\n'.join(['# Owner/builder planning and delivery platform','',
        f'{len(rows)} current city revisions,16 named GIS layers, alignment/station/service/OD edit proposals, immutable local revisions and a generic resource/procurement/monthly-cash adapter.','',
        'Missing source layers are disabled. Streets and soil display samples are labelled;1km population aggregation preserves source population totals. Radial circles are display aids, not a walking catchment calculation. Editing a station invalidates access, demand, engineering and delivery assumptions until those are rerun.','',
        'The generic compiler executes the retained ERP planning adapter. It generates draft quantities and constrained workfront tasks for any retained city. Registered missing rates stay unknown; neither a priced subtotal nor a schedule is a complete project or released design. Native records and independent physical field acceptance remain separate.','',
        'Open the [planning workspace](../../../workbench/planning/index.html). Export edits, then run `./osr plan compile edits.json --output build/my-plan`. A stale base revision or changed station order is refused. Local revision storage is append-only and recoverable.','',
        'Native owner, builder, operator, workforce and observation links use the isolated loopback stack and its existing authentication. The people link requires the relevant ERP module. This does not claim full OCC/HR federation or deployment permissions.','',
        'Primary geography and population sources remain in each city input receipt. All design, physical and procurement release flags remain false.',''])).encode()
    return files

def payload():
    """Fresh-source, one-snapshot process cache; retained output is never input."""
    global _PAYLOAD_CACHE
    with _PAYLOAD_CACHE_LOCK:
        before=dict(sources());key=tuple(sorted(before.items()))
        cached=_PAYLOAD_CACHE
        if cached is None or cached[0]!=key:
            files=_generate_payload()
            if any(not isinstance(name,str) or not isinstance(raw,bytes) for name,raw in files.items()):
                raise ValueError('immutable planning payload bytes required')
            snapshot=tuple(files.items())
            if sources()!=before:raise ValueError('planning source changed during generation')
            cached=(key,snapshot)
        # A cache hit still checks the live full source mapping, while the
        # cached tuple/bytes and copied return mapping cannot be caller-poisoned.
        if sources()!=before:raise ValueError('planning source changed during payload retrieval')
        _PAYLOAD_CACHE=cached
        return dict(cached[1])

def publish(output=OUTPUT):
    before=sources();files=payload()
    if sources()!=before:raise ValueError('planning source changed during generation')
    output=Path(output)
    if output.exists() and any(output.iterdir()) and not (output/'manifest.json').is_file():raise ValueError('owned planning publication required')
    output.mkdir(parents=True,exist_ok=True)
    for name,data in files.items():
        p=output/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
    manifest=dict(schema=SCHEMA,source_sha256=before,files_sha256={n:sha256(b).hexdigest() for n,b in files.items()},**platform.FLAGS)
    (output/'manifest.json').write_bytes(platform.encoded(manifest));return manifest

def verify(output=OUTPUT,*,recompute=True):
    output=Path(output);m=json.loads((output/'manifest.json').read_bytes())
    if m.get('schema')!=SCHEMA or m.get('source_sha256')!=sources() or any(m.get(k) is not False for k in platform.FLAGS):raise ValueError('planning publication stale or invalid')
    actual={p.relative_to(output).as_posix() for p in output.rglob('*') if p.is_file()}
    if actual!=set(m['files_sha256'])|{'manifest.json'} or any(p.is_symlink() for p in output.rglob('*')):raise ValueError('planning inventory differs')
    for n,h in m['files_sha256'].items():
        if sha256((output/n).read_bytes()).hexdigest()!=h:raise ValueError('planning bytes differ')
    if recompute:
        expected=payload()
        if any((output/n).read_bytes()!=b for n,b in expected.items()) or set(expected)!=set(m['files_sha256']):raise ValueError('planning derived data differs')
    return dict(verified=True,cities=len(folders()),layer_count=16,**platform.FLAGS)

def compile_edits(bundle,output,*,configuration_sha256,unit_costs=None):
    if bundle.get('schema')!='osr-planning-edit-bundle/1' or not re.fullmatch('[a-z0-9-]{1,81}',bundle.get('city','')):raise ValueError('typed planning edit bundle required')
    candidates=[p for p in folders() if json.loads((p/'city.json').read_bytes())['city']['slug']==bundle['city']]
    if len(candidates)!=1:raise ValueError('unique current city required')
    baseline=platform.baseline(candidates[0]);plan=platform.revise(baseline,bundle['edits'],expected_revision_sha256=bundle['base_revision_sha256'],actor=bundle['actor'])
    twin=platform.project_twin(plan,configuration_sha256=configuration_sha256,unit_costs=unit_costs)
    output=Path(output)
    if output.exists() and any(output.iterdir()) and not (output/'compile-manifest.json').exists():raise ValueError('owned planning output required')
    output.mkdir(parents=True,exist_ok=True);store=platform.RevisionStore(output/'revisions.sqlite')
    if store.latest(plan['city']) is None:store.append(baseline)
    store.append(plan)
    files={'plan.json':platform.encoded(plan),'project-twin.json':platform.encoded(twin),'planning-bundle.json':platform.encoded(twin['planning_bundle']),
        'issues.json':platform.encoded(platform.issues(plan))}
    for n,b in files.items():(output/n).write_bytes(b)
    receipt=dict(schema='osr-owner-builder-compile/1',planning_revision_sha256=plan['revision_sha256'],configuration_sha256=configuration_sha256,
        source_sha256=sources(),files_sha256={n:sha256(b).hexdigest() for n,b in files.items()},**platform.FLAGS)
    (output/'compile-manifest.json').write_bytes(platform.encoded(receipt));return receipt
