"""Read native GIS edits as bounded data and return canonical planning requests.

Never execute a project, task, workspace, plugin, URI or saved command. The
server reconstructs the original export/base; a client hash is not authority.
"""
from copy import deepcopy
from hashlib import sha256
from math import cos, isfinite, pi
from pathlib import Path
import fcntl
import gzip
import json
import re
import time
import zipfile
from uuid import uuid4

from engineering.station_rail import ROOT, FLAGS as BASE_FLAGS
from engineering.station_rail.common import encoded, identity, digest
from engineering.development_baseline import planning
from engineering.outline import planning_adapter, planning_geometry
from . import adapter

SCHEMA='osr-rustgis-revision/1'
FLAGS=dict(BASE_FLAGS,selected_reference_changed=False,movement_authority=False)
MAX_PROJECT=32*1024**2
MAX_FEATURES=100000
MAX_VERTICES=500000
MAX_STORE=256*1024**2
MAX_PROJECTIONS=5_000_000
OFF_ROUTE_M=.02
CONTEXT='_osr_export_context'
STYLE={'label','colour','color'}
PROXIES={'lon','lat','chainage_m'}
FORBIDDEN={'physical_accepted','engineering_accepted','manufacturing_release','operating_release',
    'movement_authority','selected_reference_changed','price','cost','costs'}


class RetainedImportError(ValueError):
    def __init__(self,message,import_id):
        super().__init__(message);self.import_id=import_id


def read_json(raw):
    if not isinstance(raw,bytes) or not 0<len(raw)<=MAX_PROJECT:raise ValueError('Bounded native JSON project required')
    def pairs(rows):
        v={}
        for k,x in rows:
            if k in v:raise ValueError('Duplicate native project JSON key')
            v[k]=x
        return v
    try:return json.loads(raw,object_pairs_hook=pairs,
        parse_constant=lambda _:(_ for _ in ()).throw(ValueError('Finite native values required')))
    except (RecursionError,UnicodeError) as exc:raise ValueError('Invalid bounded native project') from exc


def _number(v):
    if type(v) not in (int,float) or not isfinite(v):raise ValueError('Finite native coordinate/value required')
    return v


def _point(v,budget):
    if not isinstance(v,dict) or set(v)!={'x','y'}:raise ValueError('Two-dimensional native coordinates required')
    x,y=_number(v['x']),_number(v['y'])
    if not -180<=x<=180 or not -90<=y<=90:raise ValueError('WGS84 longitude/latitude required, not map metres')
    budget[0]+=1
    if budget[0]>MAX_VERTICES:raise ValueError('Native coordinate budget exceeded')
    return [x,y]


def _geometry(v,budget):
    if v is None:return None
    if not isinstance(v,dict) or len(v)!=1:raise ValueError('Tagged native geometry required')
    kind,data=next(iter(v.items()))
    if kind=='Point':return dict(type='Point',coordinates=_point(data,budget))
    if kind in ('MultiPoint','Points'):
        return dict(type='MultiPoint',coordinates=[_point(p,budget) for p in data])
    if kind=='Line':
        if not isinstance(data,list) or not data:raise ValueError('Native line parts required')
        parts=[[_point(p,budget) for p in part] for part in data]
        if any(len(p)<2 for p in parts):raise ValueError('Native line needs at least two vertices')
        return dict(type='LineString' if len(parts)==1 else 'MultiLineString',coordinates=parts[0] if len(parts)==1 else parts)
    if kind=='Polygon':
        polygons=[[[_point(p,budget) for p in ring] for ring in polygon] for polygon in data]
        if not polygons or any(not poly or any(len(r)<4 or r[0]!=r[-1] for r in poly) for poly in polygons):
            raise ValueError('Closed native polygon rings required')
        return dict(type='Polygon' if len(polygons)==1 else 'MultiPolygon',coordinates=polygons[0] if len(polygons)==1 else polygons)
    raise ValueError('Unsupported native geometry: '+str(kind))


def _attribute(v):
    if v=='Null':return None
    if not isinstance(v,dict) or len(v)!=1:raise ValueError('Tagged native attribute required')
    kind,value=next(iter(v.items()))
    if kind=='Text' and isinstance(value,str):return value
    if kind=='Bool' and type(value) is bool:return value
    if kind=='Int' and type(value) is int:return value
    if kind=='Float':return _number(value)
    raise ValueError('Unsupported native attribute tag')


def decode(raw,*,data_crs):
    if data_crs!='EPSG:4326':raise ValueError('Explicit EPSG:4326 data coordinates required')
    v=read_json(raw)
    if not isinstance(v,dict) or v.get('format')!=1 or type(v.get('format')) is not int:
        raise ValueError('Supported native RustGIS format:1 project required')
    if FORBIDDEN&set(v):raise ValueError('Native project cannot supply engineering approval or prices')
    maps=v.get('maps');tables=v.get('tables',[])
    if not isinstance(maps,list) or not 1<=len(maps)<=4 or not isinstance(tables,list):raise ValueError('Bounded native maps/tables required')
    datasets=[]
    for m in maps:
        if not isinstance(m,dict):raise ValueError('Native map object required')
        layers=m.get('layers')
        if not isinstance(layers,list):raise ValueError('Embedded native layers required')
        for layer in layers:
            if not isinstance(layer,dict) or 'dataset' not in layer:raise ValueError('Embedded ordinary datasets required')
            datasets.append((layer.get('name'),layer['dataset']))
    if any(not isinstance(d,dict) for d in tables):raise ValueError('Native table objects required')
    datasets.extend((d.get('name'),d) for d in tables)
    if len(datasets)>100:raise ValueError('Native layer budget exceeded')
    out={};count=0;budget=[0]
    for name,d in datasets:
        if not isinstance(name,str) or not re.fullmatch('[a-zA-Z0-9_-]{1,100}',name) or name in out:
            raise ValueError('Unique supported native layer names required')
        if not isinstance(d,dict) or d.get('crs','EPSG:4326') not in ('EPSG:4326','WGS84'):
            raise ValueError('Unsupported native data CRS')
        fields=d.get('fields');features=d.get('features')
        if not isinstance(fields,list) or not 1<=len(fields)<=256 or not isinstance(features,list):
            raise ValueError('Bounded native field schema required')
        keys=[f.get('name') if isinstance(f,dict) else None for f in fields]
        if any(not isinstance(k,str) or not k or len(k)>150 for k in keys) or len(set(keys))!=len(keys):
            raise ValueError('Unique native field names required')
        if FORBIDDEN&set(keys):raise ValueError('Native fields cannot inject prices or acceptance')
        count+=len(features)
        if count>MAX_FEATURES:raise ValueError('Native feature budget exceeded')
        result=[];ids=set()
        for feature in features:
            if not isinstance(feature,dict) or type(feature.get('id')) is not int or feature['id'] in ids:
                raise ValueError('Unique native local feature identifiers required')
            ids.add(feature['id']);attrs=feature.get('attrs')
            if not isinstance(attrs,list) or len(attrs)!=len(keys):raise ValueError('Native attribute vector differs from fields')
            result.append(dict(type='Feature',id=feature['id'],geometry=_geometry(feature.get('geometry'),budget),
                properties={k:_attribute(a) for k,a in zip(keys,attrs)}))
        out[name]=dict(type='FeatureCollection',features=result)
    return out


def _value_equal(old,new):
    if isinstance(old,(dict,list)) and isinstance(new,str):
        try:new=read_json(new.encode())
        except ValueError:return False
    return adapter._same_numbers(old,new)


def _mapped(layer,*,new_stations=False):
    found={};new=[]
    for feature in layer['features']:
        at=feature['properties'].get(adapter.INDEX)
        if at is None and new_stations:new.append(feature);continue
        if type(at) is not int or at<0 or at in found:raise ValueError('Native source correspondence changed or duplicated')
        found[at]=feature
    return found,new


def _properties(old,new,*,allowed=()):
    allowed=set(allowed)|STYLE|{adapter.INDEX}
    if set(old)-set(new):raise ValueError('Native source field removed')
    for k,value in new.items():
        if k in allowed:continue
        if k not in old:
            if value is not None:raise ValueError('Unsupported native field edit: '+k)
        elif not _value_equal(old[k],value):raise ValueError('Unsupported source/engineering attribute edit: '+k)


def _line(g):
    if g is None or g['type']!='LineString':raise ValueError('One connected route LineString required')
    return g['coordinates']


def _station(g):
    if g is None or g['type']!='Point':raise ValueError('One located station Point required')
    return g['coordinates']


def chainage(point,coordinates,shape,*,chain=None):
    """Locate actual point on actual polyline; never infer engineering map units."""
    chain=planning_geometry.route(coordinates,shape) if chain is None else chain;hits=[]
    scale=cos(point[1]*pi/180.)
    for i,(a,b) in enumerate(zip(coordinates,coordinates[1:])):
        dx=(b[0]-a[0])*scale;dy=b[1]-a[1];den=dx*dx+dy*dy
        f=0. if den==0 else max(0.,min(1.,((point[0]-a[0])*scale*dx+(point[1]-a[1])*dy)/den))
        at=[a[k]+f*(b[k]-a[k]) for k in (0,1)]
        distance=planning._distance(point,at)
        if distance<=OFF_ROUTE_M:
            value=chain[i]+f*(chain[i+1]-chain[i])
            if shape=='ring' and abs(value-chain[-1])<=OFF_ROUTE_M:value=0.
            if not any(abs(value-x)<=OFF_ROUTE_M for x in hits):hits.append(value)
    if not hits:raise ValueError('Station is more than 20 mm off its declared route; move it explicitly')
    if len(hits)!=1:raise ValueError('Ambiguous station projection on route; revise the native geometry')
    value=hits[0]
    if abs(value)<=1e-8:value=0.
    if abs(value-chain[-1])<=1e-8:value=chain[-1]
    return value


def build_request(raw,original,base,binding,*,actor,reason,data_crs='EPSG:4326'):
    """Create only typed edits over a caller-authenticated server planning base."""
    if not isinstance(actor,str) or not actor.strip() or len(actor)>150:raise ValueError('Named bounded planning author required')
    if not isinstance(reason,str) or not reason.strip() or len(reason)>1000:raise ValueError('Named bounded revision reason required')
    expected=decode(original,data_crs='EPSG:4326');edited=decode(raw,data_crs=data_crs)
    if set(expected)!=set(edited):raise ValueError('Native layer set changed; only declared routes/stations can be revised')
    if CONTEXT not in edited:raise ValueError('Re-export the current native project to include its OSR base binding')
    oldctx=expected[CONTEXT]['features'];newctx=edited[CONTEXT]['features']
    if (len(oldctx)!=1 or len(newctx)!=1 or oldctx[0]['properties']!=newctx[0]['properties'] or
            oldctx[0]['geometry']!=newctx[0]['geometry']):
        raise ValueError('Native export context changed; reload the authoritative project')
    context=read_json(newctx[0]['properties']['binding_json'].encode())
    if context!=binding or newctx[0]['properties']['data_crs']!='EPSG:4326':raise ValueError('Native export belongs to another base/candidate')
    if binding['city_slug']!=base['city'] or binding['reference_candidate_ids']!=base['outline_context']['seed']['reference_candidate_ids']:
        raise ValueError('Mixed native city or physical reference')
    for name in set(expected)-{'routes','stations',CONTEXT}:
        a,_=_mapped(expected[name]);b,_=_mapped(edited[name])
        if set(a)!=set(b):raise ValueError('Derived/source layer feature set changed: '+name)
        for i,f in a.items():
            _properties(f['properties'],b[i]['properties'])
            if not adapter._same_numbers(adapter._geometry(f['geometry']),adapter._geometry(b[i]['geometry'])):
                raise ValueError('Derived/source layer geometry edited: '+name)
    routes,_=_mapped(expected['routes']);newroutes,_=_mapped(edited['routes'])
    if set(routes)!=set(newroutes):raise ValueError('Existing route identities must be preserved')
    station_old,_=_mapped(expected['stations']);station_new,added=_mapped(edited['stations'],new_stations=True)
    old_by_id={s['properties']['id']:s['properties'] for s in station_old.values()}
    if set(station_new)-set(station_old):raise ValueError('Unknown source station index')
    by_id={line['id']:line for line in base['lines']};new_by_line={k:[] for k in by_id}
    seen_stops=set();station_changed=set()
    for index,f in station_new.items():
        old=station_old[index];props=f['properties'];_properties(old['properties'],props,allowed=PROXIES|{'dwell_s'})
        lid=props['line_id'];sid=props['id']
        if lid!=old['properties']['line_id'] or sid!=old['properties']['id']:raise ValueError('Station source identity changed')
        new_by_line[lid].append(f)
        if not adapter._same_numbers(old['geometry'],f['geometry']) or props.get('dwell_s')!=old['properties'].get('dwell_s'):
            station_changed.add(lid)
    for index in set(station_old)-set(station_new):station_changed.add(station_old[index]['properties']['line_id'])
    for f in added:
        props=f['properties'];lid=props.get('line_id');sid=props.get('id')
        if lid not in by_id or not isinstance(sid,str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.:-]{0,149}',sid):
            raise ValueError('New station needs a unique OSR string id and existing line_id')
        if any(props.get(k) is not None for k in set(props)-{adapter.INDEX,'id','line_id','dwell_s','lon','lat','chainage_m','label','colour','packet_id'}):
            raise ValueError('New station cannot inject source/engineering attributes')
        if props.get('packet_id') not in (None,binding['packet_id']):raise ValueError('New station packet differs')
        if sid in old_by_id:raise ValueError('New station reuses an existing source id')
        new_by_line[lid].append(f);station_changed.add(lid)
    edits=[];projections=0
    for index,f in routes.items():
        current=newroutes[index];_properties(f['properties'],current['properties'],allowed={'shape','headway_s','design_speed_cap_m_s'})
        lid=current['properties']['line_id']
        if lid not in by_id or f['properties']['line_id']!=lid:raise ValueError('Unknown route identity')
        line=by_id[lid];coords=_line(current['geometry'])
        props=current['properties'];shape=props.get('shape',line['shape'])
        cap=props.get('design_speed_cap_m_s',line['design_speed_cap_m_s'])
        headway=props.get('headway_s',line['headway_s'])
        planning_geometry.number(cap,'native route speed cap',.1,80.)
        planning_geometry.number(headway,'native headway',10.,86400.)
        changed=(not adapter._same_numbers(_line(f['geometry']),coords) or shape!=line['shape'] or cap!=line['design_speed_cap_m_s'])
        route_chain=planning_geometry.route(coords,shape)
        projections+=len(coords)*len(new_by_line[lid])
        if projections>MAX_PROJECTIONS:raise ValueError('Native station/route projection work exceeds this bounded import; split the revision')
        stops=[]
        for station in new_by_line[lid]:
            props=station['properties'];sid=props['id']
            if sid in seen_stops:raise ValueError('Duplicate OSR station identity')
            seen_stops.add(sid)
            point=_station(station['geometry']);at=chainage(point,coords,shape,chain=route_chain)
            source=old_by_id.get(sid,{})
            for field,want in [('lon',point[0]),('lat',point[1]),('chainage_m',at)]:
                actual=props.get(field)
                if actual is not None and actual!=source.get(field) and (type(actual) not in (int,float) or abs(actual-want)>(.02 if field=='chainage_m' else 1e-10)):
                    raise ValueError('Changed station coordinate proxy disagrees with actual geometry: '+field)
            dwell=props.get('dwell_s')
            if type(dwell) not in (int,float) or not isfinite(dwell) or not 10<=dwell<=3600:raise ValueError('Explicit bounded station dwell required')
            stops.append(dict(id=sid,chainage_m=at,dwell_s=dwell))
        stops.sort(key=lambda s:s['chainage_m'])
        if headway!=line['headway_s']:
            edits.append(dict(kind='set-service',line=lid,headway_s=headway,dwell_s=stops[0]['dwell_s'] if stops else 35.))
        if changed or lid in station_changed or headway!=line['headway_s']:
            edits.append(dict(kind='replace-line-geometry',line=lid,coordinates=coords,shape=shape,
                design_speed_cap_m_s=cap,stops=stops,reason=reason.strip()))
    bundle=dict(schema=planning_adapter.EDIT_SCHEMA,city=base['city'],base_revision_sha256=base['revision_sha256'],
        seed_id=base['outline_context']['seed']['seed_id'],source_outline_evaluation_id=base['source_outline_evaluation_id'],
        actor=actor.strip(),edits=edits)
    request=dict(schema='osr-city-workflow-request/1',city_slug=base['city'],
        expected_outline_evaluation_id=binding['source_outline_evaluation_id'],edit_bundle=bundle)
    request['base_study_id' if binding['kind']=='study' else 'base_seed_id']=binding.get('base_study_id',binding.get('base_seed_id'))
    from engineering.outline.city_workflow import normalize
    request=normalize(request)
    # The existing evaluator checks stop order, OD/access, civil and demand
    # consequences; it remains the only source of quantities and prices.
    return request,dict(changed_lines=list(dict.fromkeys(e['line'] for e in edits)),no_op=not edits,
        project_sha256=sha256(raw).hexdigest(),original_project_sha256=sha256(original).hexdigest(),
        base_revision_sha256=base['revision_sha256'],data_crs=data_crs,**FLAGS)


def authoritative(slug,packet_id,*,root=ROOT,study_id=None,service=None,output=None):
    """Resolve base and original project from server-owned records, not uploads."""
    root=Path(root).resolve()
    if study_id is not None:
        packet,_,_,_,_,binding=adapter.study_input(study_id,root=root,service=service)
        folder=root/'build/city-studies'/study_id/'artifacts'
        base=json.loads((folder/'planning.json').read_bytes())
        result=adapter.export_study(study_id,root=root,service=service,output=output)
    else:
        context=adapter.inputs(root);packet,*_=adapter.city_input(slug,context)
        from engineering.outline import publication_cache
        seed=publication_cache.json_member('cities/'+slug+'.json.gz',root)['planning_seed']
        base=planning_adapter.export_plan(seed,root=root)
        binding=adapter.published_binding(slug,packet,root)
        result=adapter.export(slug,root=root,context=context,output=output)
    if packet['city']['slug']!=slug or packet['packet_id']!=packet_id:raise ValueError('Displayed native GIS base changed; reload before editing')
    with zipfile.ZipFile(result['archive']) as archive:
        manifest=read_json(archive.read('manifest.json'));original=archive.read(manifest['project'])
    if manifest['revision_binding']!=binding:raise ValueError('Authoritative GIS export/base differ')
    return base,binding,original,manifest


def import_project(raw,slug,packet_id,*,actor,reason,data_crs,root=ROOT,study_id=None,service=None):
    """Retain original input/failure, then submit only canonical typed changes."""
    root=Path(root).resolve();store=root/'build/rustgis-imports';adapter._local(root,'build/rustgis-imports')
    store.mkdir(parents=True,exist_ok=True)
    with (store/'coordinator.lock').open('a+') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        paths=list(store.rglob('*'))
        if len(paths)>15000 or any(p.is_symlink() for p in paths):raise ValueError('Bounded ordinary native import store required')
        size=sum(p.stat().st_size for p in paths if p.is_file())
        if not isinstance(raw,bytes) or not 0<len(raw)<=MAX_PROJECT:raise ValueError('Bounded native project upload required')
        if size+len(raw)+2*1024**2>MAX_STORE:raise ValueError('Native import evidence store is full; export/preserve runs before cleanup')
        import_id=uuid4().hex;folder=store/import_id;folder.mkdir()
        (folder/'project.rgis').write_bytes(raw)
        start=time.monotonic()
        try:
            base,binding,original,manifest=authoritative(slug,packet_id,root=root,study_id=study_id,service=service)
            base_raw=encoded(base)
            if len(original)>MAX_PROJECT or len(base_raw)>MAX_PROJECT or size+len(raw)+len(original)+len(base_raw)+2*1024**2>MAX_STORE:
                raise ValueError('Native import evidence exceeds its retained storage budget')
            (folder/'original.rgis').write_bytes(original)
            (folder/'planning-base.json').write_bytes(base_raw)
            (folder/'original-export-manifest.json').write_bytes(encoded(manifest))
            request,comparison=build_request(raw,original,base,binding,actor=actor,reason=reason,data_crs=data_crs)
            (folder/'canonical-request.json').write_bytes(encoded(request))
            (folder/'export-binding.json').write_bytes(encoded(binding))
            (folder/'comparison.json').write_bytes(encoded(comparison))
            job=None
            if not comparison['no_op']:
                if service is None:raise ValueError('Typed city study service required for repricing')
                job=service.submit(request)
                if job.get('busy'):raise ValueError('Another city calculation is active; retry this retained import after completion')
            record=dict(schema=SCHEMA,import_id=import_id,execution='no-op' if comparison['no_op'] else 'submitted',
                actor=actor.strip(),reason=reason.strip(),
                project_sha256=sha256(raw).hexdigest(),original_project_sha256=sha256(original).hexdigest(),
                export_manifest_id=manifest['manifest_id'],binding=binding,comparison=comparison,
                canonical_request_id=identity(request),job=job,wall_s=time.monotonic()-start,
                source_sha256={p.relative_to(root).as_posix():digest(p) for p in
                    [root/'engineering/rustgis/revision.py',root/'engineering/rustgis/adapter.py',root/'engineering/outline/city_workflow.py']},
                files_sha256={p.name:digest(p) for p in folder.iterdir() if p.is_file()},**FLAGS)
            record['evaluation_id']=identity(record);(folder/'manifest.json').write_bytes(encoded(record))
            return record
        except Exception as exc:
            failure=dict(schema=SCHEMA+'/failure',import_id=import_id,project_sha256=sha256(raw).hexdigest(),
                error=type(exc).__name__+': '+str(exc),raw_input_retained=True,wall_s=time.monotonic()-start,**FLAGS)
            failure['evaluation_id']=identity(failure);(folder/'failure.json').write_bytes(encoded(failure))
            raise RetainedImportError(str(exc),import_id) from exc


def verify_import(folder,*,root=ROOT):
    """Check retained custody and typed translation; no solver or transaction."""
    folder=Path(folder).resolve();m=read_json((folder/'manifest.json').read_bytes())
    if m.get('evaluation_id')!=identity({k:v for k,v in m.items() if k!='evaluation_id'}) or m.get('schema')!=SCHEMA:
        raise ValueError('Native import manifest changed')
    if any(m.get(k) is not v for k,v in FLAGS.items()):raise ValueError('Native import cannot grant release')
    actual={p.name:digest(p) for p in folder.iterdir() if p.is_file() and p.name!='manifest.json'}
    if any(p.is_symlink() or not p.is_file() for p in folder.iterdir()) or actual!=m['files_sha256']:
        raise ValueError('Native import artifact inventory changed')
    for name,want in m['source_sha256'].items():
        if digest(adapter._local(Path(root).resolve(),name))!=want:raise ValueError('Native import producer source changed')
    raw=(folder/'project.rgis').read_bytes();old=(folder/'original.rgis').read_bytes()
    base=read_json((folder/'planning-base.json').read_bytes());request=read_json((folder/'canonical-request.json').read_bytes())
    binding=read_json((folder/'export-binding.json').read_bytes());comparison=read_json((folder/'comparison.json').read_bytes())
    rebuilt,check=build_request(raw,old,base,binding,actor=m['actor'],reason=m['reason'],data_crs=comparison['data_crs'])
    # A no-op's reason is deliberately not part of any physical/evaluation request.
    if rebuilt!=request or check!=comparison or identity(request)!=m['canonical_request_id']:
        raise ValueError('Native import does not reproduce its typed request')
    if m['project_sha256']!=sha256(raw).hexdigest() or m['original_project_sha256']!=sha256(old).hexdigest():
        raise ValueError('Native import source bytes changed')
    return dict(verified=True,import_id=m['import_id'],execution=m['execution'],
        canonical_request_id=m['canonical_request_id'],job=m['job'],**FLAGS)
