"""Independent step/restriction-filtered OSM walk sensitivity for the infill map."""
import gc,gzip,hashlib,io,json,math,shutil,time
from pathlib import Path
import numpy as np
from scipy.spatial import cKDTree
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import dijkstra

T0=time.monotonic();H=Path(__file__).resolve().parent;R=H.parents[2]
B=R/'cities/catalogue/west-asia/Iraq/Baghdad';M=B/'engineering/mapping';P=H.parent/'network-20261117-a'
RR=6371008.8
def can(x):return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ident(x):return hashlib.sha256(can(x)).hexdigest()
def xyz(a,o):
 a=np.deg2rad(a);o=np.deg2rad(o);return np.column_stack((np.cos(a)*np.cos(o),np.cos(a)*np.sin(o),np.sin(a)))
def chord(m):return 2*math.sin(m/(2*RR))
def metres(ch):return 2*RR*np.arcsin(np.minimum(1,ch/2))
def npz(p):return np.load(io.BytesIO(gzip.decompress(p.read_bytes())),allow_pickle=False)

if shutil.disk_usage(H).free<20*1024**3+100*1024**2:raise RuntimeError('20 GiB free floor')
inp=json.loads((H/'input.json').read_text());prior=json.loads((H/'result.json').read_text())
geojson=json.loads((H/'schematic.geojson').read_text())
proposed=[{'lat':f['properties']['lat'],'lon':f['properties']['lon'],'route_id':f['properties']['route_id']} for f in geojson['features'] if f['properties'].get('kind')=='proposed_stop_anchor']
base=json.loads((B/'baghdad.stations.json').read_text())
correction=[{'lat':q['planning_lat_lon'][0],'lon':q['planning_lat_lon'][1]} for q in json.loads((P/'concept-b-2035-delta.json').read_text())['proposed_anchor_edits']]
popz=npz(M/'worldpop-2026-pixels.npz.gz');lat=popz['lat'];lon=popz['lon'];count=popz['counts'].astype(float)
valid=popz['valid']&np.isfinite(count)&(count>0);V=xyz(lat,lon)
g=npz(M/'walking-graph.npz.gz');N=xyz(g['lat'],g['lon']);tree=cKDTree(N)

# Match the repository's tagged-way exclusion policy without duplicating its
# memory-heavy allowed-edge set. Every retained graph edge originates in OSM.
street=json.loads((M/'street-source.json').read_text())
if sha(M/'walking-graph.npz.gz')!=street['graph_sha256'] or sha(M/'walking-streets.geojson.gz')!=street['geometry_sha256']:
 raise RuntimeError('OSM source hash mismatch')
waygeo=json.loads(gzip.decompress((M/'walking-streets.geojson.gz').read_bytes()))
blocked=set();tagged=0
def point(p):return (round(p[0],7),round(p[1],7))
for f in waygeo['features']:
 t=f['properties'];h=t.get('highway')
 deny=h in {'steps','motorway','motorway_link','construction','proposed','raceway','no'} or t.get('foot') in {'no','private'} or t.get('access') in {'no','private'}
 if h in {'trunk','trunk_link'} and t.get('foot') not in {'yes','designated','permissive'}:deny=True
 if not deny:continue
 tagged+=1
 coords=f['geometry']['coordinates']
 for a,b in zip(coords,coords[1:]):blocked.add(tuple(sorted((point(a),point(b)))))
del waygeo;gc.collect()
coords=[(round(float(o),7),round(float(a),7)) for a,o in zip(g['lat'],g['lon'])]
keep=np.fromiter((tuple(sorted((coords[i],coords[j]))) not in blocked for i,j in zip(g['first'],g['second'])),dtype=bool,count=len(g['first']))
del coords,blocked;gc.collect()
f=g['first'][keep];s=g['second'][keep];length=g['length_m'][keep]
n=len(g['lat']);pixel_ch,pixel_node=tree.query(V);pixel_snap=metres(pixel_ch)

def walk(points):
 S=xyz([q['lat'] for q in points],[q['lon'] for q in points]);ch,idx=tree.query(S);snap=metres(ch)
 ok=snap<=150;idx=idx[ok];snap=snap[ok]
 # Super-source records each hypothetical station-to-road connector distance.
 row=np.r_[f,s,np.full(len(idx),n,dtype=int),idx]
 col=np.r_[s,f,idx,np.full(len(idx),n,dtype=int)]
 dat=np.r_[length,length,snap,snap]
 matrix=coo_matrix((dat,(row,col)),shape=(n+1,n+1)).tocsr()
 dist=dijkstra(matrix,directed=False,indices=n,limit=1000)
 cover=valid&(pixel_snap<=150)&((dist[pixel_node]+pixel_snap)<=1000)
 return {'graph_1km_population':round(float(count[cover].sum())),
         'accepted_station_snaps':int(ok.sum()),'rejected_station_snaps':int((~ok).sum()),
         'maximum_station_snap_m':round(float(np.max(metres(ch))),1),
         'reachable_populated_pixels':int(cover.sum())}

def radial(points):
 S=xyz([q['lat'] for q in points],[q['lon'] for q in points]);cover=cKDTree(S).query(V)[0]<=chord(1000)
 return round(float(count[valid&cover].sum()))

states=[('existing',base),('corrected',base+correction),('infill',base+correction+proposed)]
screen={k:{'radial_1km_population':radial(points),'filtered_osm_graph_1km_population':walk(points)} for k,points in states}
cumulative=base+correction;route_gains=[]
for r in prior['corridors']:
 before=radial(cumulative);add=[p for p in proposed if p['route_id']==r['route_id']];cumulative+=add;after=radial(cumulative)
 route_gains.append({'route_id':r['route_id'],'schematic_chord_km':r['schematic_chord_km'],
                     'proposed_stop_anchors':len(add),'incremental_worldpop_radial_1km':after-before})
sources={'input.json':sha(H/'input.json'),'result.json':sha(H/'result.json'),'schematic.geojson':sha(H/'schematic.geojson'),
         'walking-graph.npz.gz':sha(M/'walking-graph.npz.gz'),'walking-streets.geojson.gz':sha(M/'walking-streets.geojson.gz'),
         'street-source.json':sha(M/'street-source.json'),'worldpop-2026-pixels.npz.gz':sha(M/'worldpop-2026-pixels.npz.gz')}
out={'schema':'osr-baghdad-2035-filtered-walk-evaluation/1','candidate_id':prior['candidate_id'],'prior_evaluation_id':prior['evaluation_id'],
     'sources_sha256':sources,'screen':screen,'incremental_route_gains_ordered':route_gains,
     'graph_filter':{'removed_edges':int((~keep).sum()),'retained_edges':int(keep.sum()),'tagged_restricted_ways':tagged,
                     'policy':'exclude tagged steps, motorway, construction, proposed, private/no foot/access and trunk without explicit foot permission'},
     'limits':['Station and population pixel snap links up to 150m are straight hypothetical connectors; walls, river, gates, crossings and wheelchair accessibility unverified.',
               'OSM roads may lack sidewalks, safe crossings, width, surface and grade; route length is walking graph only, not verified accessible travel.',
               'Modelled residential population is not measured demand, mode share, jobs or 2035 projection.'],
     'physical_accepted':False,'execution':{'wall_s':round(time.monotonic()-T0,3),'free_bytes':shutil.disk_usage(H).free}}
out['evaluation_id']=ident(out)
(H/'filtered-result.json').write_bytes(can(out)+b'\n')
rec={'schema':'osr-baghdad-2035-filtered-receipt/1','candidate_id':prior['candidate_id'],'evaluation_id':out['evaluation_id'],
     'files_sha256':{x:sha(H/x) for x in ('input.json','result.json','schematic.geojson','filtered.py','filtered-result.json')},'physical_accepted':False}
rec['receipt_id']=ident(rec);(H/'filtered-receipt.json').write_bytes(can(rec)+b'\n')
print(can({'candidate_id':out['candidate_id'],'evaluation_id':out['evaluation_id'],'receipt_id':rec['receipt_id'],
           'screen':screen,'route_gains':route_gains,'wall_s':out['execution']['wall_s']}).decode())
