"""Revisioned owner/builder planning, independent of the physical train family.

Edits are proposals. Resource schedules, ERP imports and field observations do
not confer construction release, movement authority or physical acceptance.
"""
from copy import deepcopy
from bisect import bisect_right
from hashlib import sha256
import heapq
import gzip
import io
import json
import math
from pathlib import Path
import re
import sqlite3

from . import model, operating_plan, delivery_schedule

ROOT=model.ROOT
SCHEMA='osr-owner-builder-plan/1'
LAYERS=(('alignments','Fixed-line alignments'),('operating-stops','Proposed passenger stops'),
    ('retained-access','Original access records'),('transfers','Passenger transfer junctions'),
    ('power-zones','Station launch/receive extents'),('boosters','Located accelerators'),
    ('terminal-zones','Terminal service positions'),('civil-workfronts','Civil workfronts'),
    ('walking-streets','Open-map pedestrian streets'),('population-worldpop','WorldPop population'),
    ('population-ghsl','GHSL population'),('soil-samples','Open soil sample locations'),
    ('destinations','Open-map destinations'),('catchments','Indicative station access radii'),
    ('site-context','Site investigation context'),('revision-changes','Proposed revision changes'))
FLAGS={**model.FLAGS,'engineering_accepted':False,'movement_authority':False,'procurement_released':False}

def encoded(value):return (json.dumps(value,sort_keys=True,indent=2,allow_nan=False)+'\n').encode()
def digest(value):return sha256(encoded(value)).hexdigest()
def finite(value,*,minimum=0.,maximum=1e12):
    if type(value) not in (int,float) or not math.isfinite(value) or not minimum<=value<=maximum:
        raise ValueError('bounded finite planning quantity required')
    return float(value)

def seal(value):
    value=deepcopy(value);value.pop('revision_sha256',None);value['revision_sha256']=digest(value);return value

def city_folder(path):
    path=Path(path).resolve()
    if not path.is_relative_to(ROOT/'cities/catalogue') or not (path/'city.json').is_file():
        raise ValueError('catalogue city directory required')
    return path

def baseline(path):
    """Use each city's current operating stops, never inherited patronage claims."""
    path=city_folder(path);raw=path/'city.json';network=next(iter(sorted(path.glob('*.corridor.geojson'))),None)
    if network is None:raise ValueError('retained mapped alignment required')
    summary=path/'engineering/maglev/summary.json'
    city=json.loads(raw.read_bytes());features=json.loads(network.read_bytes())['features'];current=json.loads(summary.read_bytes())
    lines=[]
    for row in current['lines']:
        route=operating_plan.route_path(features,next(r for r in city['lines'] if r['name']==row['line']))
        stops=[dict(id=s['id'],chainage_m=s['s_m'],lat=s['lat'],lon=s['lon'],
            mandatory_junction_ids=s.get('mandatory_junction_ids',[]),dwell_s=60.) for s in row['operating_plan']['stations']]
        lines.append(dict(id=row['line'],coordinates=route['points'],length_m=route['length_m'],stops=stops,
            headway_s=row['selected_peak_headway_seconds'],planning_minimum_headway_s=row['planning_minimum_headway_seconds'],
            headway_is_accepted=False,cars=row['formation']['cars'] if isinstance(row['formation'],dict) else int(row['formation']),
            transport_family='fixed-zone-ferrite-maglev',alignment_accepted=False))
    value=dict(schema=SCHEMA,city=city['city']['slug'],revision=1,parent_revision_sha256=None,actor='catalogue-import',
        source_sha256={p.relative_to(ROOT).as_posix():sha256(p.read_bytes()).hexdigest() for p in (raw,network,summary)},
        lines=lines,interchanges=city.get('interchanges',[]),od=[],changes=[],environment='planning',**FLAGS)
    return seal(value)

def validate(plan):
    if not isinstance(plan,dict) or plan.get('schema')!=SCHEMA or plan.get('environment')!='planning':raise ValueError('planning-only revision required')
    if plan.get('revision_sha256')!=digest({k:v for k,v in plan.items() if k!='revision_sha256'}):raise ValueError('planning revision digest differs')
    if any(plan.get(k) is not False for k in FLAGS):raise ValueError('planning cannot assert physical or operational release')
    if not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,80}',plan.get('city','')):raise ValueError('bounded city identity required')
    if type(plan.get('revision')) is not int or plan['revision']<1 or not isinstance(plan.get('actor'),str) or not plan['actor']:raise ValueError('revision and actor required')
    if not isinstance(plan.get('lines'),list) or not 1<=len(plan['lines'])<=100:raise ValueError('bounded line list required')
    if len({r['id'] for r in plan['lines']})!=len(plan['lines']):raise ValueError('duplicate line')
    stops=set()
    for line in plan['lines']:
        finite(line['length_m'],minimum=1,maximum=1e6);finite(line['headway_s'],minimum=10,maximum=86400)
        finite(line['planning_minimum_headway_s'],minimum=1,maximum=86400)
        points=line['coordinates']
        if not isinstance(points,list) or not 2<=len(points)<=10000:raise ValueError('bounded geographical path required')
        for lon,lat in points:finite(lon,minimum=-180,maximum=180);finite(lat,minimum=-90,maximum=90)
        expected=math.fsum(operating_plan.distance(a,b) for a,b in zip(points,points[1:]))
        if not math.isclose(expected,line['length_m'],abs_tol=.001):raise ValueError('alignment length differs from geography')
        previous=-1.;chain=_chainages(points)
        for stop in line['stops']:
            s=finite(stop['chainage_m'],maximum=line['length_m'])
            if s<=previous or stop['id'] in stops:raise ValueError('ordered unique station chainages required')
            previous=s;stops.add(stop['id']);finite(stop['dwell_s'],minimum=10,maximum=3600)
            route=dict(coordinates=points,length_m=line['length_m'])
            expected_point=_point(route,s,chain=chain)
            if operating_plan.distance(expected_point,[stop['lon'],stop['lat']])>.01:raise ValueError('station is off its alignment')
    if not isinstance(plan.get('od'),list) or len(plan['od'])>100000:raise ValueError('bounded OD rows required')
    seen=set()
    for row in plan['od']:
        pair=(row['origin'],row['destination'])
        if pair[0] not in stops or pair[1] not in stops or pair[0]==pair[1] or pair in seen:raise ValueError('unique distinct existing OD stations required')
        finite(row['trips_per_day'],maximum=1e8);seen.add(pair)
        if row.get('basis') not in {'synthetic','observed-unaccepted'}:raise ValueError('explicit unaccepted demand provenance required')
    return plan

def _chainages(points):
    out=[0.]
    for a,b in zip(points,points[1:]):out.append(out[-1]+operating_plan.distance(a,b))
    return out

def _point(route,s,*,chain=None):
    points=route['coordinates'];chain=_chainages(points) if chain is None else chain
    i=max(0,min(len(chain)-2,bisect_right(chain,s)-1));start,end=chain[i:i+2]
    t=(s-start)/(end-start) if end>start else 0.
    return [points[i][j]+t*(points[i+1][j]-points[i][j]) for j in range(2)]

def revise(plan,edits,*,expected_revision_sha256,actor):
    validate(plan)
    if expected_revision_sha256!=plan['revision_sha256']:raise ValueError('stale planning revision; merge/review required')
    if not isinstance(actor,str) or not actor.strip() or len(actor)>150:raise ValueError('named planning actor required')
    if not isinstance(edits,list) or not 1<=len(edits)<=1000:raise ValueError('bounded nonempty edits required')
    new=deepcopy(plan);by_id={r['id']:r for r in new['lines']}
    for edit in edits:
        kind=edit.get('kind')
        if kind=='set-od':new['od']=deepcopy(edit['rows'])
        else:
            line=by_id.get(edit.get('line'))
            if line is None:raise ValueError('unknown planning line')
            if kind=='move-stop':
                stop=next((s for s in line['stops'] if s['id']==edit.get('stop')),None)
                if stop is None:raise ValueError('unknown station')
                stop['chainage_m']=finite(edit['chainage_m'],maximum=line['length_m'])
                stop['lon'],stop['lat']=_point(line,stop['chainage_m']);stop['access_and_transfer_reassessment_required']=True
            elif kind=='set-service':
                line['headway_s']=finite(edit['headway_s'],minimum=10,maximum=86400)
                dwell=finite(edit['dwell_s'],minimum=10,maximum=3600)
                for s in line['stops']:s['dwell_s']=dwell
            elif kind=='straighten-line':
                old=line['length_m'];line['coordinates']=[line['coordinates'][0],line['coordinates'][-1]]
                line['length_m']=operating_plan.distance(*line['coordinates'])
                for s in line['stops']:
                    s['chainage_m']*=line['length_m']/old;s['lon'],s['lat']=_point(line,s['chainage_m'])
                    s['access_and_transfer_reassessment_required']=True
            else:raise ValueError('unknown planning edit')
    new.update(revision=plan['revision']+1,parent_revision_sha256=plan['revision_sha256'],actor=actor,
        changes=deepcopy(edits),requires_reassessment=['geography/access/demand','operating protection and power','BOM/structure/construction/cash','BIM/field coordination'])
    return validate(seal(new))

def issues(plan):
    validate(plan);rows=[]
    for line in plan['lines']:
        if line['headway_s']<line['planning_minimum_headway_s']:
            rows.append(dict(id=line['id']+'/headway',state='hold',reason='Requested headway below current planning/protection basis'))
        for a,b in zip(line['stops'],line['stops'][1:]):
            if b['chainage_m']-a['chainage_m']<1500:
                rows.append(dict(id=a['id']+'/'+b['id'],state='spacing-exception' if a['mandatory_junction_ids'] or b['mandatory_junction_ids'] else 'hold',reason='Passenger stops less than1500m apart'))
    rows.extend(dict(id='revision/'+str(i),state='reassessment-required',reason='Edited design is an unadopted proposal') for i,_ in enumerate(plan.get('changes',[])))
    return rows

class RevisionStore:
    """Immutable local planning revisions with optimistic concurrency."""
    def __init__(self,path):
        self.path=Path(path);self.path.parent.mkdir(parents=True,exist_ok=True)
        with sqlite3.connect(self.path) as db:
            db.executescript('CREATE TABLE IF NOT EXISTS revisions(city TEXT, revision INTEGER, digest TEXT UNIQUE, parent TEXT, body TEXT, PRIMARY KEY(city,revision)); CREATE TRIGGER IF NOT EXISTS immutable_revision_update BEFORE UPDATE ON revisions BEGIN SELECT RAISE(ABORT,"immutable planning revision"); END; CREATE TRIGGER IF NOT EXISTS immutable_revision_delete BEFORE DELETE ON revisions BEGIN SELECT RAISE(ABORT,"immutable planning revision"); END;')
    def append(self,plan):
        validate(plan)
        with sqlite3.connect(self.path,timeout=10) as db:
            db.execute('BEGIN IMMEDIATE')
            prior=db.execute('SELECT digest,revision FROM revisions WHERE city=? ORDER BY revision DESC LIMIT 1',(plan['city'],)).fetchone()
            old=db.execute('SELECT body FROM revisions WHERE digest=?',(plan['revision_sha256'],)).fetchone()
            if old:
                if json.loads(old[0])!=plan:raise ValueError('revision identity reused')
                return False
            if prior and (plan['parent_revision_sha256']!=prior[0] or plan['revision']!=prior[1]+1):raise ValueError('stale planning revision; no overwrite')
            if not prior and (plan['revision']!=1 or plan['parent_revision_sha256'] is not None):raise ValueError('initial baseline required')
            db.execute('INSERT INTO revisions VALUES(?,?,?,?,?)',(plan['city'],plan['revision'],plan['revision_sha256'],plan['parent_revision_sha256'],encoded(plan).decode()))
        return True
    def latest(self,city):
        with sqlite3.connect(self.path) as db:row=db.execute('SELECT body FROM revisions WHERE city=? ORDER BY revision DESC LIMIT 1',(city,)).fetchone()
        return validate(json.loads(row[0])) if row else None

def resource_schedule(tasks,capacities,*,shift_hours=8.):
    """Feasible deterministic list schedule; no global-optimum claim."""
    if any(type(n) is not int or n<1 for n in capacities.values()):raise ValueError('positive resource capacity required')
    by={t['id']:deepcopy(t) for t in tasks}
    if len(by)!=len(tasks):raise ValueError('duplicate task')
    downstream={i:[] for i in by};remaining={};ready=[]
    for uid,t in by.items():
        finite(t['hours'],minimum=.001,maximum=1e7);remaining[uid]=len(t['depends'])
        for dep in t['depends']:
            if dep not in by:raise ValueError('unknown task predecessor')
            downstream[dep].append(uid)
        if not remaining[uid]:heapq.heappush(ready,uid)
    slots={r:[0.]*n for r,n in capacities.items()};done={}
    while ready:
        uid=heapq.heappop(ready);t=by[uid];begin=max((done[d]['end_h'] for d in t['depends']),default=0.)
        resource=t.get('resource');unit=None
        if resource is not None:
            if resource not in slots:raise ValueError('undefined task resource')
            unit=min(range(len(slots[resource])),key=lambda j:slots[resource][j]);begin=max(begin,slots[resource][unit])
        start,end=delivery_schedule.work_window(begin,t['hours'],shift=shift_hours,continuous=t.get('continuous',False))
        done[uid]=dict(t,start_h=start,end_h=end,resource_unit=unit)
        if resource is not None:slots[resource][unit]=end
        for child in downstream[uid]:
            remaining[child]-=1
            if not remaining[child]:heapq.heappush(ready,child)
    if len(done)!=len(by):raise ValueError('cyclic task graph')
    result=sorted(done.values(),key=lambda t:(t['start_h'],t['id']));delivery_schedule.verify_schedule(result,capacities);return result

def project_twin(plan,*,configuration_sha256,unit_costs=None,workfront_m=100.,resources=None):
    """Any-city revision -> quantities, tasks, procurement, monthly planned cash.

    Unpriced scope is explicit and prevents a complete-cost assertion. Qualified
    engineering and observed actuals are inputs, never inferred from a schedule.
    """
    validate(plan)
    if not re.fullmatch('[0-9a-f]{64}',configuration_sha256):raise ValueError('controlled engineering candidate required')
    finite(workfront_m,minimum=25,maximum=1000);rates=unit_costs or {}
    resources=resources or dict(design=2,ground=2,foundation=4,casting=4,transport=2,crane=2,installation=2,inspection=2)
    tasks=[];quantities=[];procurement=[]
    stages=[('investigate',8,'ground',False),('foundations',24,'foundation',False),('cast',16,'casting',False),('cure',168,None,True),('transport',8,'transport',False),('erect',16,'crane',False),('interfaces',16,'installation',False),('survey-and-test',8,'inspection',False)]
    for line in plan['lines']:
        bays=math.ceil(line['length_m']/25);beams=2*bays;supports=bays+1
        quantities.extend([dict(id=line['id']+'/beam',product='guidebeam',quantity=beams,unit='unit'),dict(id=line['id']+'/support',product='support',quantity=supports,unit='unit'),dict(id=line['id']+'/station',product='station',quantity=len(line['stops']),unit='unit')])
        release=line['id']+'/controlled-design'
        tasks.append(dict(id=release,hours=40.,resource='design',depends=[],engineering_release=False,planned_only=True,cost_usd=0.))
        n=math.ceil(line['length_m']/workfront_m)
        for i in range(n):
            previous=release;length=min(workfront_m,line['length_m']-i*workfront_m)
            for stage,hours,res,continuous in stages:
                uid=f'{line["id"]}/workfront-{i:04d}/{stage}'
                tasks.append(dict(id=uid,line=line['id'],chainage_m=i*workfront_m,length_m=length,hours=hours*length/workfront_m if not continuous else hours,
                    resource=res,depends=[previous],continuous=continuous,engineering_release=False,planned_only=True,cost_usd=0.));previous=uid
    scheduled=resource_schedule(tasks,resources);by={t['id']:t for t in scheduled};monthly={};missing=[]
    for q in quantities:
        rate=rates.get(q['product']);q['unit_rate_usd']=rate;q['unquoted']=True;q['cost_usd']=None if rate is None else q['quantity']*finite(rate)
        line=q['id'].split('/')[0];completion=max(t['end_h'] for t in scheduled if t['id'].startswith(line+'/'))/24
        lead={'guidebeam':90.,'support':60.,'station':180.}[q['product']]
        row=dict(id=q['id'],product=q['product'],quantity=q['quantity'],unit=q['unit'],need_by_day=completion,lead_days=lead,order_by_day=max(0.,completion-lead),cost_usd=q['cost_usd'],supplier_qualified=False)
        procurement.append(row)
        if rate is None:missing.append(q['id']);continue
        for day,fraction in ((row['order_by_day'],.3),(completion,.6),(completion+90,.1)):
            month=math.floor(day/30)+1;monthly[month]=monthly.get(month,0.)+q['cost_usd']*fraction
    manufacturing_tasks=[dict(manufacturing_uid=q['id'],title='Draft '+q['product']+' delivery',asset_id=q['id'],quantity=q['quantity'],unit=q['unit'],configuration_sha256=configuration_sha256) for q in quantities]
    bundle=dict(project_twin=dict(city=plan['city'],revision_id=plan['revision_sha256']),manufacturing_tasks=manufacturing_tasks,
        maintenance_tasks=[dict(task_uid=q['id']+'/inspection',title='Independent inspection and serial maintenance',asset_id=q['id'],configuration_sha256=configuration_sha256) for q in quantities])
    from .pilot_lifecycle import planning
    planning.validate_plan(planning.make_plan(bundle))
    total=math.fsum(q['cost_usd'] for q in quantities if q['cost_usd'] is not None)
    if not math.isclose(total,math.fsum(monthly.values()),abs_tol=1e-6):raise ValueError('planned procurement cash does not reconcile')
    return dict(schema='osr-owner-builder-delivery-twin/1',city=plan['city'],planning_revision_sha256=plan['revision_sha256'],configuration_sha256=configuration_sha256,
        quantities=quantities,tasks=scheduled,resources=resources,procurement=procurement,monthly_cash=[dict(month=k,cash_usd=v) for k,v in sorted(monthly.items())],
        priced_subtotal_usd=total,unpriced_scope=missing,registered_scope_priced=not missing,complete_cost_known=False,
        excluded_scope=['qualified site/utility/land works','complete station/depot/factory/vehicle scope','grid/evacuation/assurance/finance actuals'],completion_calendar_days=max(t['end_h'] for t in scheduled)/24,
        planning_bundle=bundle,actual_records=[],physical_releases=0,scope='Generic any-city planned workfronts and constrained resources; geometric/site/method/price acceptance and native actual transactions remain separate.',**FLAGS)

def planning_layers(plan,path):
    """Sixteen named GIS layers, with unavailable/sampled inputs explicit."""
    validate(plan);path=city_folder(path);city=json.loads((path/'city.json').read_bytes())
    summary=json.loads((path/'engineering/maglev/summary.json').read_bytes());by_line={r['line']:r for r in summary['lines']}
    rows={key:dict(id=key,name=name,features=[],available=True,source_sha256={},display_sampling=False) for key,name in LAYERS}
    def feature(key,uid,kind,coordinates,**properties):
        rows[key]['features'].append(dict(type='Feature',id=uid,geometry=dict(type=kind,coordinates=coordinates),properties=dict(id=uid,**properties)))
    chains={line['id']:_chainages(line['coordinates']) for line in plan['lines']}
    def point(line,s):return _point(line,s,chain=chains[line['id']])
    def source(key,p):rows[key]['source_sha256'][p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest()
    for line in plan['lines']:
        key=line['id'];feature('alignments',key,'LineString',line['coordinates'],line=key,accepted=False)
        for stop in line['stops']:
            feature('operating-stops',stop['id'],'Point',[stop['lon'],stop['lat']],line=key,chainage_m=stop['chainage_m'])
            feature('catchments',stop['id']+'/radius','Point',[stop['lon'],stop['lat']],radius_m=1000,basis='Illustrative radial distance; walking-network access is a separate calculation')
            begin=max(0.,stop['chainage_m']-150);end=min(line['length_m'],stop['chainage_m']+200)
            feature('power-zones',stop['id']+'/power','LineString',[point(line,begin),point(line,end)],line=key,nominal_length_m=350,extent_clipped_at_route_end=True)
        for i in range(math.ceil(line['length_m']/100)):
            feature('civil-workfronts',f'{key}/front-{i:04d}','Point',point(line,min(line['length_m'],i*100+50)),line=key,chainage_m=i*100,planned_only=True)
        for r in by_line[key]['operating_plan']['powered_top_up_zones']:
            if 'lon' in r and 'lat' in r:
                feature('boosters',r['id'],'Point',[r['lon'],r['lat']],line=key);continue
            if 'chainage_m' in r:s=r['chainage_m']
            elif 'start_m' in r and 'end_m' in r:s=(r['start_m']+r['end_m'])/2
            else:continue
            feature('boosters',r.get('id',key+'/'+str(s)),'Point',point(line,min(line['length_m'],max(0,s))),line=key)
        for r in by_line[key]['topology']['terminal_service_zones']:
            feature('terminal-zones',r['id'],'Point',[r['lon'],r['lat']],line=key,site_approved=False)
    for s in city['stations']:feature('retained-access',s['id'],'Point',[s['lon'],s['lat']],line=s['line'])
    for s in city.get('interchanges',[]):feature('transfers',s['id'],'Point',[s['lon'],s['lat']],lines=s['lines'])
    for key in ('alignments','operating-stops','retained-access','transfers','power-zones','boosters','terminal-zones','civil-workfronts','catchments'):
        source(key,path/'city.json');source(key,path/'engineering/maglev/summary.json')
    walking=path/'engineering/mapping/walking-streets.geojson.gz'
    if walking.exists():
        features=json.loads(gzip.decompress(walking.read_bytes()))['features'];stride=max(1,math.ceil(len(features)/2500))
        rows['walking-streets']['features']=features[::stride];rows['walking-streets'].update(display_sampling=True,source_feature_count=len(features),display_stride=stride);source('walking-streets',walking)
    else:rows['walking-streets']['available']=False
    for key,name in (('population-worldpop','worldpop-2026'),('population-ghsl','ghsl-2025')):
        p=path/'engineering/mapping'/(name+'-pixels.npz.gz')
        if not p.exists():rows[key]['available']=False;continue
        import numpy as np
        with np.load(io.BytesIO(gzip.decompress(p.read_bytes())),allow_pickle=False) as grid:
            lat=grid['lat'];lon=grid['lon'];counts=grid['counts'];valid=grid['valid'].astype(bool)&np.isfinite(counts)&(counts>=0)
            scale=111320*math.cos(math.radians(city['city']['centroid_lat']))
            cells=np.column_stack((np.floor(lon[valid].astype(np.float64)*scale/1000),np.floor(lat[valid].astype(np.float64)*111320/1000))).astype(np.int64)
            unique,inverse=np.unique(cells,axis=0,return_inverse=True);population=np.bincount(inverse,weights=counts[valid].astype(np.float64))
            for (x,y),n in zip(unique.tolist(),population.tolist()):feature(key,f'{name}/{x}/{y}','Point',[(x+.5)*1000/scale,(y+.5)*1000/111320],population=n,aggregation_cell_m=1000,boardings=False)
            rows[key].update(source_population_total=float(counts[valid].sum(dtype=np.float64)),aggregated_population_total=math.fsum(population),native_pixels=int(valid.sum()),display_sampling=False,aggregation_m=1000)
            if not math.isclose(rows[key]['source_population_total'],rows[key]['aggregated_population_total'],rel_tol=1e-10):raise ValueError('GIS aggregation lost population')
        source(key,p)
    p=path/'engineering/soil/sample-locations.geojson'
    if p.exists():
        data=json.loads(p.read_bytes())['features'];stride=max(1,math.ceil(len(data)/2500));rows['soil-samples'].update(features=data[::stride],display_sampling=stride>1,source_feature_count=len(data),display_stride=stride);source('soil-samples',p)
    else:rows['soil-samples']['available']=False
    p=Path(__file__).parent/'data/pilot-destinations.json'
    if plan['city']=='baghdad' and p.exists():
        data=json.loads(p.read_bytes());items=data.get('destinations',data.get('elements',data.get('features',[])))
        for i,r in enumerate(items):
            point=r if 'lat' in r and 'lon' in r else r.get('center',{})
            if 'lat' in point and 'lon' in point:feature('destinations',str(r.get('id',i)),'Point',[point['lon'],point['lat']],destination_type=r.get('tags',{}).get('amenity','destination'))
        source('destinations',p)
    else:rows['destinations']['available']=False
    p=path/'site-context.json'
    if p.exists():
        source('site-context',p);rows['site-context']['context']=json.loads(p.read_bytes());c=city['city'];feature('site-context',plan['city'],'Point',[c['centroid_lon'],c['centroid_lat']],ground_design_validated=False)
    else:rows['site-context']['available']=False
    for i,edit in enumerate(plan.get('changes',[])):
        line=next((l for l in plan['lines'] if l['id']==edit.get('line')),None)
        if line:feature('revision-changes',str(i),'LineString',line['coordinates'],edit=edit['kind'],adopted=False)
    return dict(schema='osr-planning-gis-layers/1',city=plan['city'],revision_sha256=plan['revision_sha256'],layers=list(rows.values()),
        scope='Planning visualisation and revision editing. Missing inputs are disabled; sampled streets/soil and1km population aggregation are explicit. No site/access/catchment acceptance.',**FLAGS)
