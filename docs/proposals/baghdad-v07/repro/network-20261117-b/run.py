"""Baghdad 2035 schematic infill screen; never a surveyed alignment."""
import gzip,hashlib,io,json,math,shutil,time
from pathlib import Path
import numpy as np
from scipy.spatial import cKDTree
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import dijkstra

H=Path(__file__).resolve().parent
R=H.parents[2]
B=R/'cities/catalogue/west-asia/Iraq/Baghdad'
M=B/'engineering/mapping'
PREV=H.parent/'network-20261117-a'
RADIUS=6371008.8
T0=time.monotonic()
def can(x):return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ident(x):return hashlib.sha256(can(x)).hexdigest()
def xyz(a,o):
 a=np.deg2rad(a);o=np.deg2rad(o)
 return np.column_stack((np.cos(a)*np.cos(o),np.cos(a)*np.sin(o),np.sin(a)))
def chord(m):return 2*math.sin(m/(2*RADIUS))
def arc(a,b):
 d=np.linalg.norm(xyz([a[0]],[a[1]])[0]-xyz([b[0]],[b[1]])[0])
 return 2*RADIUS*math.asin(min(1,d/2))
def npz(p):return np.load(io.BytesIO(gzip.decompress(p.read_bytes())),allow_pickle=False)

if shutil.disk_usage(H).free<20*1024**3+100*1024**2:raise RuntimeError('20 GiB free floor plus 100 MiB projection not met')
routes=[
 ('B-I01','Sadr east-west',[(33.389,44.400),(33.386,44.440),(33.389,44.490),(33.389,44.530)],'Central and eastern Sadr infill; transfer fit to base lines 9/10/11 and roads/land to survey.'),
 ('B-I02','Sadr north-south',[(33.345,44.460),(33.370,44.460),(33.400,44.455),(33.435,44.450)],'Sadr cross-link; intersections with B-I01, base ring and lines 10/14 require station/track design.'),
 ('B-I03','East inner arc',[(33.270,44.410),(33.300,44.430),(33.330,44.460),(33.345,44.500),(33.350,44.540)],'Jadriya/Karrada east-bank approach; land, arterial crossings and heritage/utilities to survey.'),
 ('B-I04','Karkh north-south',[(33.230,44.310),(33.280,44.310),(33.330,44.320),(33.380,44.340),(33.420,44.350)],'West-bank inner infill; road footprint, existing line conflicts and safe transfers to survey.'),
 ('B-I05','Southwest cross-city',[(33.225,44.290),(33.245,44.340),(33.265,44.380),(33.280,44.410)],'Southwest to Jadriya approach; Tigris crossing and property/utility rights are a major hold.'),
 ('B-I06','Northern cross-city',[(33.420,44.310),(33.420,44.370),(33.420,44.430),(33.420,44.490)],'West/east north connector; Tigris crossing and interchanges are a major hold.'),
]
sources={
 'cities/catalogue/west-asia/Iraq/Baghdad/city.json':sha(B/'city.json'),
 'cities/catalogue/west-asia/Iraq/Baghdad/baghdad.corridor.geojson':sha(B/'baghdad.corridor.geojson'),
 'cities/catalogue/west-asia/Iraq/Baghdad/baghdad.stations.json':sha(B/'baghdad.stations.json'),
 'cities/catalogue/west-asia/Iraq/Baghdad/site-context.json':sha(B/'site-context.json'),
 'cities/catalogue/west-asia/Iraq/Baghdad/engineering/mapping/worldpop-2026-pixels.npz.gz':sha(M/'worldpop-2026-pixels.npz.gz'),
 'cities/catalogue/west-asia/Iraq/Baghdad/engineering/mapping/walking-graph.npz.gz':sha(M/'walking-graph.npz.gz'),
 'build/v07-baghdad/network-20261117-a/concept-b-2035-delta.json':sha(PREV/'concept-b-2035-delta.json'),
}
inp={'schema':'osr-baghdad-2035-infill-input/1','parent_candidate_id':'aad29169384d4201eff98da1e7090ca43b7cb3fc37fd51159224901762a408aa',
     'fixed_reference_vehicle':'six 17 m cars; 276 normal places; two wheelchair places/car; 72 km/h retained-stop launch cap, not a service proof',
     'source_sha256':sources,'corridor_control_vertices':routes,
     'stop_interval_target_m':1700,'radial_access_m':1000,'walking_graph_path_budget_m':1000,
     'walking_graph_snap_limit_m':150,'walking_graph_policy':'raw graph topology upper-bound sensitivity; not filtered for steps/private/trunk crossings, therefore no accessible-service claim'}
inp['input_id']=ident(inp)
(H/'input.json').write_bytes(can(inp)+b'\n')

city=json.loads((B/'city.json').read_text());base=json.loads((B/'baghdad.stations.json').read_text())
prior=json.loads((PREV/'concept-b-2035-delta.json').read_text())
px=npz(M/'worldpop-2026-pixels.npz.gz');lat=px['lat'];lon=px['lon'];pop=px['counts'].astype(float)
valid=px['valid']&np.isfinite(pop)&(pop>0);P=xyz(lat,lon)
g=npz(M/'walking-graph.npz.gz');N=xyz(g['lat'],g['lon']);ntree=cKDTree(N)
edges=coo_matrix((np.r_[g['length_m'],g['length_m']],
   (np.r_[g['first'],g['second']],np.r_[g['second'],g['first']])),shape=(len(g['lat']),len(g['lat']))).tocsr()
pixchord,pixnode=ntree.query(P);pixsnap=2*RADIUS*np.arcsin(np.minimum(1,pixchord/2))

def densify(v,interval=1700):
 lengths=[arc(a,b) for a,b in zip(v,v[1:])];length=sum(lengths);n=math.ceil(length/interval)
 out=[]
 for k in range(n+1):
  target=length*k/n;cum=0
  for j,L in enumerate(lengths):
   if target<=cum+L or j==len(lengths)-1:
    t=min(1,max(0,(target-cum)/L));out.append([round(v[j][0]+t*(v[j+1][0]-v[j][0]),7),round(v[j][1]+t*(v[j+1][1]-v[j][1]),7)]);break
   cum+=L
 return length,out

route_rows=[];new=[];features=[]
for rid,name,vertices,hold in routes:
 length,stops=densify(vertices)
 row={'route_id':rid,'name':name,'control_vertices_lat_lon':vertices,'schematic_chord_km':round(length/1000,3),
      'proposed_stop_count':len(stops),'stop_spacing_chord_m':round(length/(len(stops)-1)),
      'interface_hold':hold,'river_crossing_verified':False,'land_and_alignment_surveyed':False}
 route_rows.append(row)
 features.append({'type':'Feature','properties':{'route_id':rid,'name':name,'kind':'schematic_control_polyline','not_surveyed':True},
                  'geometry':{'type':'LineString','coordinates':[[o,a] for a,o in vertices]}})
 for i,(a,o) in enumerate(stops):
  p={'id':f'{rid}-s{i:02d}','route_id':rid,'lat':a,'lon':o,'kind':'proposed_stop_anchor','not_surveyed':True}
  new.append(p)
  features.append({'type':'Feature','properties':p,'geometry':{'type':'Point','coordinates':[o,a]}})

def radial(points):
 S=xyz([p['lat'] for p in points],[p['lon'] for p in points]);return cKDTree(S).query(P)[0]<=chord(1000)
def walking(points):
 S=xyz([p['lat'] for p in points],[p['lon'] for p in points]);snap,idx=ntree.query(S)
 snap_m=2*RADIUS*np.arcsin(np.minimum(1,snap/2))
 # A station-to-OSM connector of 150 m is hypothetical; add a conservative
 # maximum snap penalty to the graph budget and count only connected pixels.
 accepted=idx[snap_m<=150]
 if len(accepted)==0:return np.zeros(len(P),dtype=bool),{'accepted':0,'rejected':len(points),'station_snap_m_max':None}
 dist=dijkstra(edges,directed=False,indices=np.unique(accepted),min_only=True,limit=1000)
 reached=valid&(pixsnap<=150)&(dist[pixnode]+pixsnap<=1000)
 return reached,{'accepted':len(accepted),'rejected':int(len(points)-len(accepted)),
                 'station_snap_m_max':round(float(np.max(snap_m)),1),'graph_reachable_pixels':int(reached.sum())}

prior_points=[{'lat':r['planning_lat_lon'][0],'lon':r['planning_lat_lon'][1]} for r in prior['proposed_anchor_edits']]
states=[('existing',base),('existing_plus_corrections',base+prior_points),('plus_infill',base+prior_points+new)]
access={}
for name,points in states:
 cover=radial(points);walk,wmeta=walking(points)
 access[name]={'station_markers':len(points),'radial_1km_modelled_population':round(float(pop[valid&cover].sum())),
               'raw_osm_graph_1km_modelled_population_upper_sensitivity':round(float(pop[walk].sum())),
               'raw_graph_screen':wmeta}

all_length=sum(r['schematic_chord_km'] for r in route_rows)
original=sum(x['length_m'] for x in city['lines'])/1000
airport=prior['airport_line_5_extension_straight_lower_bound_km']
result={'schema':'osr-baghdad-2035-infill-result/1','input_id':inp['input_id'],
 'candidate_scope':'separate 2035 research network; base 14 lines retained, line-5 airport extension and six prior focus anchors retained, six infill corridors added',
 'physical_accepted':False,'selected':False,'corridors':route_rows,
 'source_declared_base_km':round(original,3),'airport_extension_chord_lower_bound_km':airport,
 'infill_control_chord_km':round(all_length,3),'schematic_programme_total_km':round(original+airport+all_length,3),
 'new_infill_stop_anchors':len(new),'source_existing_station_markers':len(base),
 'access_screen':access,
 'access_change_from_base_to_full_radial_modelled_population':access['plus_infill']['radial_1km_modelled_population']-access['existing']['radial_1km_modelled_population'],
 'access_change_from_corrections_to_infill_radial_modelled_population':access['plus_infill']['radial_1km_modelled_population']-access['existing_plus_corrections']['radial_1km_modelled_population'],
 'worldpop_bbox_modelled_population':round(float(pop[valid].sum())),
 'population_is_not':'census, measured ridership, OD, construction viability or forecast 2035 >12m',
 'walking_screen_limit':'Raw OSM graph is an optimistic connectivity sensitivity; unfiltered steps/private/motorway edges and hypothetical 150 m connectors may overstate accessible walking. No approved entrances, crossings or wheelchair paths.',
 'service_and_construction_holds':['Track and station alignment, land and utilities, river/highway crossings and flood/ground surveys.',
   'Every station requires 102 m six-car full-tail platform plus clearance, evacuation and accessible entrance design.',
   'Count and locate powered zones, grid interfaces, substations, control boundaries, depots and recovery routes.',
   'Dwell, headway, formation, grade, charging, braking, reserve and fleet replay at measured OD demand.',
   'Installed vehicle and civil quantities, source-backed prices, delivery stages and whole-life financing.'],
 'execution':{'wall_s':round(time.monotonic()-T0,3),'free_bytes':shutil.disk_usage(H).free}}
result['candidate_id']=ident({'parent':inp['parent_candidate_id'],'routes':route_rows,'stops':new})
result['evaluation_id']=ident({'input_id':inp['input_id'],'result_without_evaluation':result})
(H/'result.json').write_bytes(can(result)+b'\n')
(H/'schematic.geojson').write_bytes(can({'type':'FeatureCollection','properties':{'candidate_id':result['candidate_id'],'not_surveyed':True},'features':features})+b'\n')
receipt={'schema':'osr-baghdad-2035-infill-receipt/1','input_id':inp['input_id'],'candidate_id':result['candidate_id'],'evaluation_id':result['evaluation_id'],
         'files_sha256':{p.name:sha(p) for p in sorted(H.iterdir()) if p.is_file() and p.name!='receipt.json'},'physical_accepted':False}
receipt['receipt_id']=ident(receipt)
(H/'receipt.json').write_bytes(can(receipt)+b'\n')
print(can({'candidate_id':result['candidate_id'],'receipt_id':receipt['receipt_id'],'infill_km':round(all_length,3),'stop_anchors':len(new),'access':access,'wall_s':result['execution']['wall_s']}).decode())
