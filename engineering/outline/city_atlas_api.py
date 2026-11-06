"""Read-only, source-checked city map dossiers and separately bound UI assets."""
from pathlib import Path
from hashlib import sha256
import gzip
import json
import re
from urllib.parse import unquote,urlsplit

from engineering.station_rail.common import digest,encoded,identity
from engineering.trip_dynamics.interactive import _loopback

ASSET_RECEIPT='docs/workbench/city-atlas-assets.json'
ASSETS=('city-atlas.js','city-atlas.css','city-journeys.js')
PRODUCER='engineering/outline/city_atlas_api.py'


def publish_assets(root):
    root=Path(root);sources={};files={}
    for name in ASSETS:
        source='engineering/development_baseline/web/'+name
        target='docs/workbench/current/'+name
        raw=(root/source).read_bytes();sources[source]=sha256(raw).hexdigest()
        (root/target).write_bytes(raw);files[target]=sha256(raw).hexdigest()
    sources[PRODUCER]=digest(root/PRODUCER)
    value=dict(schema='osr-city-atlas-ui/1',source_sha256=sources,files_sha256=files,
        physical_accepted=False,manufacturing_release=False,operating_release=False)
    value['manifest_id']=identity(value)
    (root/ASSET_RECEIPT).write_bytes(encoded(value))
    return value


def verify_asset(root,name,target):
    root=Path(root)
    if name not in ASSETS:raise ValueError('Known city atlas UI asset required')
    m=json.loads((root/ASSET_RECEIPT).read_bytes())
    if m.get('schema')!='osr-city-atlas-ui/1' or m.get('manifest_id')!=identity({k:v for k,v in m.items() if k!='manifest_id'}):
        raise ValueError('City atlas UI manifest differs')
    for n,h in m['source_sha256'].items():
        if digest(root/n)!=h:raise ValueError('City atlas UI source changed: '+n)
    key='docs/workbench/current/'+name
    if Path(target)!=root/key or m['files_sha256'].get(key)!=digest(target):
        raise ValueError('City atlas UI asset differs')


def published(root,slug=None):
    from . import city_atlas,publication_cache
    root=Path(root);folder=root/city_atlas.PUBLICATION
    m=json.loads((folder/'manifest.json').read_bytes())
    if m.get('schema')!=city_atlas.SCHEMA+'/manifest' or m.get('manifest_id')!=identity({k:v for k,v in m.items() if k!='manifest_id'}):
        raise ValueError('City atlas manifest differs')
    if any(m.get(k) is not False for k in city_atlas.FLAGS):raise ValueError('City atlas cannot grant qualification')
    upstream,_=publication_cache.verified(root)
    if m.get('publication_manifest_id')!=upstream['manifest_id']:
        raise ValueError('City calculations changed; regenerate city atlas')
    if m.get('presentation_sha256')!=city_atlas._presentation_sources():
        raise ValueError('City atlas compiler changed; regenerate presentation')
    name='summary.json' if slug is None else 'cities/'+slug+'.json.gz'
    if name not in m['files_sha256']:raise ValueError('Unknown calculated city dossier')
    raw=(folder/name).read_bytes()
    if sha256(raw).hexdigest()!=m['files_sha256'][name]:raise ValueError('City atlas payload changed')
    if name.endswith('.gz'):
        import io
        with gzip.GzipFile(fileobj=io.BytesIO(raw)) as stream:raw=stream.read(16*1024**2+1)
    if len(raw)>16*1024**2:raise ValueError('City map presentation exceeds byte budget')
    value=json.loads(raw)
    if slug is not None:
        if value.get('city',{}).get('slug')!=slug or value.get('packet_id')!=identity({k:v for k,v in value.items() if k!='packet_id'}):
            raise ValueError('City atlas identity differs')
    for key in city_atlas.FLAGS:
        if value.get(key) is not False:raise ValueError('City map cannot grant qualification')
    return value


def handle_api(handler):
    path=unquote(urlsplit(handler.path).path)
    if path!='/api/city-atlas' and not path.startswith('/api/city-atlas/'):return False
    if handler.command not in ('GET','HEAD'):
        handler.respond(405,{'error':'City atlas is read-only'});return True
    if not _loopback(handler,post=False):
        handler.respond(403,{'error':'Matching loopback Host required'});return True
    try:
        if path.startswith('/api/city-atlas/study/'):
            job_id=path.removeprefix('/api/city-atlas/study/')
            if not re.fullmatch('[a-f0-9]{32}',job_id):raise ValueError('Known completed city study required')
            service=getattr(handler.server,'city_studies',None)
            if service is None:raise ValueError('Local city study service unavailable')
            # The study service refuses pending, failed, stale or changed artifacts.
            raw=service.artifact(job_id,'result.json')
            from . import city_atlas
            workflow=json.loads(raw)
            value=city_atlas.from_study(workflow)
            value['evidence']['outline_acceptance']=workflow['outline_acceptance']
            selected=next(c for c in workflow['cases'] if c['alignment_id']==workflow['examined_alignment_id'])
            value['evidence']['functional_screen']=selected['functional_screen']
            delivery=workflow['delivery_plan']
            value['delivery']=dict(plan_id=delivery['plan_id'],task_count=len(delivery['tasks']),
                schedule_cases=delivery['schedule']['cases'],workforce=delivery['workforce'],
                cost_reconciliation=delivery['cost_reconciliation'])
            value['sources']['presentation_sha256'][PRODUCER]=digest(Path(handler.root)/PRODUCER)
            value.pop('packet_id');value['packet_id']=identity(value)
        else:
            slug=None if path=='/api/city-atlas' else path.removeprefix('/api/city-atlas/')
            if slug is not None and not re.fullmatch('[a-z0-9]+(?:-[a-z0-9]+)*',slug):raise ValueError('Known city slug required')
            value=published(handler.root,slug)
        handler.respond(200,value)
    except (ValueError,KeyError,TypeError,OSError) as exc:
        handler.respond(503,{'error':str(exc),'physical_accepted':False})
    return True
