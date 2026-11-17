"""Seal a long-network planning delta; all new connections are schematic."""
import hashlib, json, math
from pathlib import Path

H=Path(__file__).resolve().parent
R=H.parents[2]
B=R/'cities/catalogue/west-asia/Iraq/Baghdad'

def canon(x):return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
def digest(x):return hashlib.sha256(canon(x)).hexdigest()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def gc(a,b):
 la1,lo1=map(math.radians,a);la2,lo2=map(math.radians,b)
 return 2*6371008.8*math.asin(min(1,math.sqrt(math.sin((la2-la1)/2)**2+math.cos(la1)*math.cos(la2)*math.sin((lo2-lo1)/2)**2)))

city=json.loads((B/'city.json').read_text())
features=json.loads((B/'baghdad.corridor.geojson').read_text())['features']
lines={f['properties']['name']:f['geometry']['coordinates'] for f in features if f['geometry']['type']=='LineString'}
stations=json.loads((B/'baghdad.stations.json').read_text())
source={p:sha(B/p) for p in ('city.json','baghdad.corridor.geojson','baghdad.stations.json','site-context.json')}
source.update({'screen_result.json':sha(H/'result.json'),'rfi-waypoints.json':sha(H/'rfi-waypoints.json')})
anchors=[
 ('airport-terminal','line-5',33.2676806,44.2289243,'OSM passenger terminal way/28647537 centroid; landside entrance and property access unverified','required passenger terminal service'),
 ('sadr-south','line-10',33.368,44.451,'WorldPop 2026 1 km radial model; off-line distance is not station fit','new station or local alignment variation'),
 ('sadr-central','line-10',33.383,44.446,'WorldPop 2026 1 km radial model; off-line distance is not station fit','new station or local alignment variation'),
 ('sadr-east','line-9',33.393,44.486,'WorldPop 2026 1 km radial model; ring stop integration unverified','new ring station'),
 ('jadriya-west','line-1',33.281,44.383,'WorldPop 2026 1 km radial model; Tigris/road crossing access unverified','new station or walking connection'),
 ('jadriya-east','line-2',33.286,44.403,'WorldPop 2026 1 km radial model; line 2 deviation and transfer unverified','new station on deviation or verified feeder'),
]
rows=[];geo=[]
for aid,line,lat,lon,basis,action in anchors:
 p=(lat,lon)
 coords=lines[line]
 i=min(range(len(coords)),key=lambda j:gc(p,(coords[j][1],coords[j][0])))
 near=(coords[i][1],coords[i][0]); d=gc(p,near)
 rec={'anchor_id':aid,'assigned_existing_line':line,'planning_lat_lon':[lat,lon],
      'nearest_existing_line_vertex_lat_lon':[round(near[0],7),round(near[1],7)],
      'straight_distance_to_line_m':round(d), 'action':action,'basis':basis,
      'alignment_surveyed':False,'station_feasibility_verified':False}
 rows.append(rec)
 geo.append({'type':'Feature','properties':{'kind':'proposed_anchor',**rec},'geometry':{'type':'Point','coordinates':[lon,lat]}})
 geo.append({'type':'Feature','properties':{'kind':'straight_lower_bound_connector','anchor_id':aid,'schematic_only':True,'surveyed_alignment':False},
             'geometry':{'type':'LineString','coordinates':[[near[1],near[0]],[lon,lat]]}})
original_km=round(sum(x['length_m'] for x in city['lines'])/1000,3)
short=[x for x in city['lines'] if int(x['name'].split('-')[1])>=10]
airport_lb_km=next(r['straight_distance_to_line_m'] for r in rows if r['anchor_id']=='airport-terminal')/1000
out={'schema':'osr-baghdad-2035-research-network-delta/1',
     'identity_scope':'separate physical-planning topology; fixed reference vehicle; no selection or physical acceptance',
     'planning_horizon':'2035 scenario; >12m residents is user planning assumption, not validated projection',
     'input_sha256':source,
     'source_declared_14_line_km':original_km,'source_declared_station_markers':len(stations),
     'source_declared_short_lines_10_14_km':round(sum(x['length_m'] for x in short)/1000,3),
     'source_declared_short_lines_10_14_retained':True,
     'proposed_anchor_edits':rows,
     'airport_line_5_extension_straight_lower_bound_km':round(airport_lb_km,3),
     'network_length_after_airport_extension_straight_lower_bound_km':round(original_km+airport_lb_km,3),
     'length_reporting':'Source city.json length includes declared lines; proposed anchor connectors are straight lower bounds only. No route length or 500–800 km engineering acceptance is claimed.',
     'regional_coverage':'Current 1 km radial WorldPop screen covers 2,583,183 of 8,597,980 modelled residents (30.04%); targeted Sadr/Jadriya anchors improve local radial coverage only if physically sited.',
     'retain_or_consolidate':'Retain all five short lines pending through-running or verified replacement; their stops are not redundant by access screen. Cost/fleet savings cannot be booked.',
     'holds':['Line-5 airport land/security/accessible terminal entrance and surveyed horizontal/vertical alignment.',
              'Sadr station footprint, track divergence, access, evacuation and interchange on lines 9/10.',
              'Jadriya river/road crossings, land/utility interfaces and whether line-1/2 can form through connector.',
              'Complete station count, platforms, powered zones, grid, depots, fleet, rescue and normal-service timetable.',
              'Installed vehicle mass and grade/braking/full-tail/charging/reserve evidence.',
              'Population scenario, measured demand, origin-destination and walking network coverage.',
              'One source-backed installed and whole-life cost; candidate not bankable or owner-approved.'],
     'physical_accepted':False,'selected':False}
out['candidate_id']=digest(out)
(H/'concept-b-2035-delta.json').write_bytes(canon(out)+b'\n')
(H/'concept-b-2035-schematic.geojson').write_bytes(canon({'type':'FeatureCollection','properties':{'candidate_id':out['candidate_id'],'schematic_only':True},'features':geo})+b'\n')
print(out['candidate_id'],original_km,round(airport_lb_km,3),len(rows))
