"""Bounded, read-only Baghdad network and native population screen."""
from __future__ import annotations
import gzip, hashlib, io, json, math, shutil, time
from pathlib import Path
import numpy as np
from scipy.spatial import cKDTree
from shapely.geometry import shape, Point
from shapely.ops import unary_union
from shapely import contains_xy

ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
B=ROOT/'cities/catalogue/west-asia/Iraq/Baghdad'
R=6371008.8
def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
def identity(x):return hashlib.sha256(canonical(x)).hexdigest()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def xyz(lat,lon):
 a=np.deg2rad(lat);o=np.deg2rad(lon)
 return np.column_stack((np.cos(a)*np.cos(o),np.cos(a)*np.sin(o),np.sin(a)))
def chord(m):return 2*math.sin(m/(2*R))
def great_circle(a,b):
 x=xyz(np.array([a[0]]),np.array([a[1]]))[0]
 y=xyz(np.array([b[0]]),np.array([b[1]]))[0]
 return 2*R*math.asin(min(1.,np.linalg.norm(x-y)/2))

start=time.monotonic()
if shutil.disk_usage(HERE).free < 20*1024**3+20*1024**2:
 raise RuntimeError('20 GiB free floor plus 20 MiB projection not met')
source_paths=[
 'AGENTS.md',
 'cities/catalogue/west-asia/Iraq/Baghdad/README.md',
 'cities/catalogue/west-asia/Iraq/Baghdad/city.json',
 'cities/catalogue/west-asia/Iraq/Baghdad/baghdad.corridor.geojson',
 'cities/catalogue/west-asia/Iraq/Baghdad/baghdad.stations.json',
 'cities/catalogue/west-asia/Iraq/Baghdad/site-context.json',
 'cities/catalogue/west-asia/Iraq/Baghdad/engineering/mapping/worldpop-2026-source.json',
 'cities/catalogue/west-asia/Iraq/Baghdad/engineering/mapping/worldpop-2026-pixels.npz.gz',
]
sources={p:sha(ROOT/p) for p in source_paths}
sources['osm-lookup.json']=sha(HERE/'osm-lookup.json')
osm=json.loads((HERE/'osm-lookup.json').read_text())
by_id={(r['osm_type'],r['osm_id']):r for r in osm}
airport=by_id[('way',28647537)];jad=by_id[('node',12044401990)]
sadr=unary_union([shape(by_id[('relation',i)]['geojson']) for i in (2964419,11085948)])
stations=json.loads((B/'baghdad.stations.json').read_text())
city=json.loads((B/'city.json').read_text())
geo=json.loads((B/'baghdad.corridor.geojson').read_text())
route={f['properties']['name']:f['geometry']['coordinates'] for f in geo['features'] if f['geometry']['type']=='LineString'}
px=np.load(io.BytesIO(gzip.open(B/'engineering/mapping/worldpop-2026-pixels.npz.gz','rb').read()))
lat=px['lat'];lon=px['lon'];pop=px['counts'].astype(float)
valid=px['valid']&np.isfinite(pop)&(pop>0)
V=xyz(lat,lon)
S=xyz(np.array([r['lat'] for r in stations]),np.array([r['lon'] for r in stations]))
old=cKDTree(S).query(V)[0]<=chord(1000)
focus={
 'sadr_osm_first_second_district_union':contains_xy(sadr,lon,lat)&valid,
 'jadriya_2km_centroid_screen':(np.linalg.norm(V-xyz(np.array([float(jad['lat'])]),np.array([float(jad['lon'])]))[0],axis=1)<=chord(2000))&valid,
}

def greedy(mask,maximum):
 # Deterministic 0.005-degree candidate lattice; 1 km radial, 1.3 km spacing.
 aa=np.arange(round(float(lat[mask].min()),3),float(lat[mask].max())+.005,.005)
 oo=np.arange(round(float(lon[mask].min()),3),float(lon[mask].max())+.005,.005)
 candidates=[]
 for a in aa:
  for o in oo:
   if mask is focus['sadr_osm_first_second_district_union'] and not sadr.contains(Point(o,a)):continue
   p=xyz(np.array([a]),np.array([o]))[0]
   if mask is focus['jadriya_2km_centroid_screen'] and np.linalg.norm(p-xyz(np.array([float(jad['lat'])]),np.array([float(jad['lon'])]))[0])>chord(2000):continue
   if cKDTree(S).query(p)[0]<chord(600):continue
   candidates.append((round(float(a),6),round(float(o),6),p))
 covered=old.copy();selected=[]
 for _ in range(maximum):
  best=None
  for a,o,p in candidates:
   if any(np.linalg.norm(p-q['xyz'])<chord(1300) for q in selected):continue
   hit=(np.linalg.norm(V-p,axis=1)<=chord(1000))&mask&(~covered)
   gain=float(pop[hit].sum())
   if best is None or gain>best[0]:best=(gain,a,o,p,hit)
  if best is None:break
  gain,a,o,p,hit=best;selected.append({'lat':a,'lon':o,'incremental_modelled_population_1km':round(gain),'xyz':p})
  covered|=hit
 return [{k:v for k,v in q.items() if k!='xyz'} for q in selected],round(float(pop[mask&covered].sum()))

focus_result={}
for name,mask in focus.items():
 chosen,after=greedy(mask,3 if name.startswith('sadr') else 2)
 focus_result[name]={
  'definition':'OSM first+second Al-Sadr administrative relation union' if name.startswith('sadr') else '2 km radial study circle around OSM Jadriya suburb node; not a district boundary',
  'modelled_population':round(float(pop[mask].sum())),
  'existing_1km_covered':round(float(pop[mask&old].sum())),
  'candidate_anchors':chosen,
  'after_1km_covered_if_all_anchors_built':after,
  'walking_access_verified':False,
 }

landmarks={
 'airport_terminal':(float(airport['lat']),float(airport['lon'])),
 'sadr_city_osm_suburb_approx':(33.3905897,44.4570662),
 'jadriya_osm_suburb':(float(jad['lat']),float(jad['lon'])),
}
nearest={}
for name,p in landmarks.items():
 station=sorted(((great_circle(p,(r['lat'],r['lon'])),r) for r in stations),key=lambda t:(t[0],t[1]['id']))[:3]
 line=[]
 for k,coords in route.items():
  d=min(great_circle(p,(q[1],q[0])) for q in coords)
  line.append((d,k))
 nearest[name]={
  'planning_point_lat_lon':[p[0],p[1]],
  'nearest_existing_stations':[{'distance_m':round(d),'line':r['line'],'station_id':r['id']} for d,r in station],
  'nearest_existing_line_geometry':[{'distance_m':round(d),'line':k} for d,k in sorted(line)[:3]],
 }

short=[]
long_stations=[r for r in stations if int(r['line'].split('-')[1])<=9]
for line in city['lines']:
 k=line['name'];n=int(k.split('-')[1])
 if n<10:continue
 own=[r for r in stations if r['line']==k]
 dist=[min(great_circle((r['lat'],r['lon']),(z['lat'],z['lon'])) for z in long_stations) for r in own]
 short.append({'line':k,'length_m':line['length_m'],'station_count':len(own),
               'station_nearest_long_line_station_m':[round(d) for d in dist]})

rfi={
 'source':'Government of Iraq, Prime Minister Office, Baghdad Metro RFI, 20 February 2024, pages 2–4',
 'url':'https://investpromo.gov.iq/wp-content/uploads/2024/03/3.-RFI-English-%D9%86%D8%A8%D8%B0%D8%A9-%D8%B9%D9%86-%D9%85%D8%AA%D8%B1%D9%88-%D8%A8%D8%BA%D8%AF%D8%A7%D8%AF-E-20.2.2024.pdf',
 'declared_total_km':148,
 'declared_station_count':64,
 'lines_km':{'Green':19,'Red':27.7,'Blue':22,'Purple':14.5,'Yellow':30,'White':23,'Airport':12},
 'sum_tabulated_km':148.2,
 'owner_approval_and_feasibility_can_revise':True,
 'airport_route_named':True,
 'jadriya_name_ambiguity':'RFI Yellow lists Al Chadriya Sq.; verify Arabic/local place identity before asserting Jadriya station.',
}
topology={
 'family':'seven government-RFI-named lines, separate from 494 km generated research map',
 'Airport':{'route':'Baghdad Airport passenger terminal → Al Amiriya → Hay Al Aamil → Al Bayaa → Um Al Tubol → Al Qadisiya',
            'terminal_planning_point_lat_lon':list(landmarks['airport_terminal']),
            'terminal_access':'landside passenger-terminal station and accessible path; exact entrance, security and property to survey'},
 'Purple_Blue_Sadr':{'route':'retain RFI Blue/Purple interchange family; require surveyed Sadr City stop sequence at the population anchors',
                     'anchors':focus_result['sadr_osm_first_second_district_union']['candidate_anchors'],
                     'legacy_corridors_to_replace_as_through_service':['line-10','line-11','line-14']},
 'Yellow_Jadriya':{'route':'resolve Al Chadriya name, then fit Jadriya stops on surveyed Yellow/Karrada connection',
                   'anchors':focus_result['jadriya_2km_centroid_screen']['candidate_anchors'],
                   'legacy_corridors_to_replace_as_through_service':['line-12','line-13']},
 'other_RFI_lines':['Green','Red','White'],
 'new_geometry_surveyed':False,
 'legacy_short_lines_retired_as_standalone_only_if_access_replaced':True,
}
request={
 'schema':'osr-baghdad-v07-network-screen-input/1',
 'fixed_reference_vehicle_candidate_id':'756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3',
 'selection_id':None,
 'source_sha256':sources,
 'rfi':rfi,
 'screen':{'radial_access_m':1000,'jadriya_focus_m':2000,'candidate_grid_degrees':.005,
           'candidate_existing_station_separation_m':600,'candidate_pair_separation_m':1300,
           'population_source':'WorldPop Global2 R2025A v1 constrained 100m 2026; model, not census',
           'coordinate_source':'OSM Nominatim lookup 2026-11-17, local response hash sealed'},
}
request['input_id']=identity(request)
(HERE/'input.json').write_bytes(canonical(request))
result={
 'schema':'osr-baghdad-v07-network-screen-result/1',
 'input_id':request['input_id'],
 'selected_reference_changed':False,
 'physical_accepted':False,
 'network_candidate_id':identity(topology),
 'topology':topology,
 'current_generated_map':{
  'lines':len(city['lines']),'route_km':round(sum(x['length_m'] for x in city['lines'])/1000,3),
  'station_markers':len(stations),'short_lines_10_14':short,
  'short_line_total_km':round(sum(x['length_m'] for x in short)/1000,3),
  'scope':'research map, not owner-approved government RFI route'},
 'nearest_landmarks':nearest,
 'population_screen':{
  'city_worldpop_modelled':round(float(pop[valid].sum())),
  'city_existing_1km_radial_covered':round(float(pop[valid&old].sum())),
  'focus':focus_result,
  'radial_not_walking':True,'demand_inference':False,
 },
 'service_screen':{'fixed_normal_places_per_train':276,'rfi_4minute_offered_pphpd_per_line':4140,
                   'planning_usable_pphpd_at_85pct_occupancy_99pct_availability':round(4140*.85*.99),
                   'headway_s_needed_for_4000_usable_pphpd':round(3600*276*.85*.99/4000,1),
                   'vehicle_formation_and_demand_need_separate_evaluation':True},
 'holds':['Government RFI is a negotiable seven-line concept, not surveyed civil/alignment/station permission.',
          'Airport terminal location is an OSM terminal-way centroid; landside entrance, security boundary and accessible route are unverified.',
          'Sadr and Jadriya WorldPop gains use 1 km radial circles and modelled counts, not walking network, census or ridership.',
          'Existing short-line corridors have unique access; standalone retirement requires replacement through route, transfer, fleet and timetable.',
          'River crossings, utilities, rights of way, airport property, speed/grade, platforms, powered zones, grid, depot and recovery are unverified.',
          'Seven-line lengths are RFI nominal; candidate aligned geometry, installed mass, cost and financing have not been evaluated.'],
 'execution':{'wall_s':round(time.monotonic()-start,3),'disk_free_bytes':shutil.disk_usage(HERE).free},
}
result['evaluation_id']=identity({k:v for k,v in result.items() if k!='execution'})
(HERE/'result.json').write_bytes(canonical(result))
receipt={'schema':'osr-baghdad-v07-network-screen-receipt/1','evaluation_id':result['evaluation_id'],
         'files_sha256':{n:sha(HERE/n) for n in ('osm-lookup.json','run.py','input.json','result.json')},
         'physical_accepted':False}
receipt['receipt_id']=identity(receipt)
(HERE/'receipt.json').write_bytes(canonical(receipt))
print(json.dumps({'input_id':request['input_id'],'evaluation_id':result['evaluation_id'],
                  'receipt_id':receipt['receipt_id'],'wall_s':result['execution']['wall_s'],
                  'network_candidate_id':result['network_candidate_id']},sort_keys=True))
