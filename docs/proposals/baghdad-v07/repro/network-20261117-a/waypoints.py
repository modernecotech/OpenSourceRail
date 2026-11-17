"""RFI names to vetted OSM planning points; never a surveyed alignment."""
import json,hashlib
from pathlib import Path
H=Path(__file__).resolve().parent
RFI='https://investpromo.gov.iq/wp-content/uploads/2024/03/3.-RFI-English-%D9%86%D8%A8%D8%B0%D8%A9-%D8%B9%D9%86-%D9%85%D8%AA%D8%B1%D9%88-%D8%A8%D8%BA%D8%AF%D8%A7%D8%AF-E-20.2.2024.pdf'
# OSM centroids are planning points. Exact square waypoints are still not station entrances.
# lat, lon, osm_type, osm_id, precision
v={
 'Al Mansour':(33.3174756,44.3390607,'relation',2964828,'area_centroid'),
 'Al Nusour Sq.':(33.3019833,44.3560678,'way',4077677,'square_road_centroid'),
 'Al Yarmouk':(33.3047065,44.3413213,'node',21661948,'named_square'),
 'Al Bayaa':(33.2696947,44.3454550,'relation',2964800,'area_centroid'),
 'Al Eelam':(33.2362709,44.3377970,'node',3718312982,'neighbourhood_centroid'),
 'Adan Sq.':(33.3618995,44.3353287,'way',1281239779,'square_road_centroid'),
 'Al Kadhimiya':(33.3774159,44.3312930,'node',12044401993,'suburb_centroid'),
 'Al Adhamiya':(33.4202176,44.4017953,'relation',2964144,'district_centroid_coarse'),
 'Maisaloun Sq.':(33.3183538,44.4690404,'way',1247146139,'square_road_centroid'),
 'Al Shaab':(33.4160876,44.4021197,'relation',17047853,'district_centroid_coarse'),
 'Al Waziriya':(33.3662160,44.3923831,'relation',2964400,'area_centroid'),
 'Al Khallani Sq.':(33.3326389,44.4052093,'way',839130755,'named_square'),
 'Al Tayaran Sq.':(33.3309180,44.4126796,'way',837367985,'named_square'),
 'Al Andalus':(33.3153532,44.4261660,'way',665424457,'square_road_centroid'),
 'Al Zuafaraniya':(33.2504645,44.4865607,'relation',15756058,'area_centroid'),
 'Hamza Sq.':(33.3590595,44.4599851,'way',4210529,'square_road_centroid'),
 '55 Sq.':(33.3740961,44.4407637,'way',1286845065,'named_square'),
 'Ur':(33.3997220,44.3938890,'node',2486265808,'neighbourhood_centroid'),
 'Al Baladiyat':(33.3479887,44.4810246,'node',12231874647,'suburb_centroid'),
 'Hay Al Jamiaa':(33.3236960,44.3259260,'node',2486263691,'neighbourhood_centroid'),
 'Al Shulah':(33.3640388,44.2842233,'node',2486307468,'quarter_centroid'),
 'Al Gazaliya':(33.3485980,44.2763614,'node',12044401989,'suburb_centroid'),
 'Al Khadhraa':(33.3199142,44.3082663,'relation',2964821,'area_centroid'),
 'Al Amiriya':(33.2975342,44.2902660,'node',12044401992,'suburb_centroid'),
 'Hay Al Aamil':(33.2785929,44.3274306,'relation',2964801,'area_centroid'),
 'Al Qadisiya':(33.2899389,44.3571234,'relation',2964829,'area_centroid'),
 'Baghdad Airport terminal':(33.2676806,44.2289243,'way',28647537,'passenger_terminal_way_centroid_not_entrance'),
}
lines=[
 ('Green',19,['Al Allawi','Al Mansour','Al Nusour Sq.','Al Yarmouk','Al Bayaa','Al Eelam','Al Saydiyya','Doura']),
 ('Red',27.7,['Al Allawi','Adan Sq.','Al Kadhimiya','Al Adhamiya','Antar Sq.','Al Mustansiriya','Qanat Al Jaish','Maisaloun Sq.']),
 ('Blue',22,['Al Shaab','Al Waziriya','Al Jamhouriya St.','Al Khallani Sq.','Al Tayaran Sq.','Al Andalus','Uqba Bin Nafi Sq.','Al Zuafaraniya']),
 ('Purple',14.5,['Al Tayaran Sq.','Hamza Sq.','55 Sq.','83 Sq.','Nadi Al Naft Int.','Ur','Al Shaab']),
 ('Yellow',30,['Al Baladiyat','Maisaloun Sq.','Uqba Bin Nafi Sq.','Al Hasanin Sq.','Al Chadriya Sq.','Al Bayaa','Hay Al Jamiaa','Adan Sq.']),
 ('White',23,['Al Kadhimiya','Al Shulah','Al Gazaliya','Al Khadhraa','Al Amiriya','Al Eelam','Al Bayaa']),
 ('Airport',12,['Baghdad Airport terminal','Al Amiriya','Hay Al Aamil','Al Bayaa','Um Al Tubol','Al Qadisiya']),
]
extra={
 'Purple':[(33.368,44.451,'Sadr south planning anchor'),(33.383,44.446,'Sadr central planning anchor'),(33.393,44.486,'Sadr east planning anchor')],
 'Yellow':[(33.281,44.383,'Jadriya west planning anchor'),(33.286,44.403,'Jadriya east planning anchor')],
}
rows=[];features=[]
for line,km,names in lines:
 located=[];unlocated=[]
 for order,name in enumerate(names):
  x=v.get(name)
  rec={'line':line,'order':order,'rfi_name':name,'kind':'rfi_named','lat':x[0] if x else None,
       'lon':x[1] if x else None,'osm_type':x[2] if x else None,'osm_id':x[3] if x else None,
       'coordinate_scope':x[4] if x else 'unlocated_name',
       'source_url':f'https://www.openstreetmap.org/{x[2]}/{x[3]}' if x else None,
       'route_clearance_or_station_fit_verified':False}
  rows.append(rec)
  if x:located.append([x[1],x[0]])
  else:unlocated.append(name)
 for a,o,name in extra.get(line,[]):
  rows.append({'line':line,'order':None,'rfi_name':None,'kind':'proposed_population_anchor',
               'planning_name':name,'lat':a,'lon':o,'osm_type':None,'osm_id':None,
               'coordinate_scope':'WorldPop radial_1km_greedy_lattice','source_url':None,
               'route_clearance_or_station_fit_verified':False})
 features.append({'type':'Feature','properties':{'line':line,'rfi_nominal_km':km,
      'schematic_only':True,'surveyed_alignment':False,'unlocated_rfi_names':unlocated,
      'proposed_anchor_count':len(extra.get(line,[]))},
      'geometry':{'type':'LineString','coordinates':located}})
 for r in rows:
  if r['line']==line and r['lat'] is not None:
   features.append({'type':'Feature','properties':{k:v for k,v in r.items() if k not in ('lat','lon')},
                    'geometry':{'type':'Point','coordinates':[r['lon'],r['lat']]}})
out={'schema':'osr-baghdad-rfi-schematic-waypoints/1','official_rfi_url':RFI,
     'official_rfi_date':'2024-02-20','osm_lookup_date':'2026-11-17',
     'purpose':'Seven-line schematic for authority discussion; coordinates are OSM place centroids or WorldPop screen anchors, not surveyed track or approved stations.',
     'rfi_nominal_km':{line:km for line,km,_ in lines},
     'waypoints':rows,
     'holds':['No actual route alignment/grade/land/utility/river/airport access or owner approval.',
              'Several RFI names unlocated; schematic lines skip them and must not be measured as route length.',
              'Al Chadriya Sq. is not assumed to be Jadriya; proposed Jadriya anchors require owner confirmation.',
              'Sadr and Jadriya anchor paths require new route engineering; line connections are not physically proven.']}
out['waypoint_table_id']=hashlib.sha256(json.dumps(out,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
(H/'rfi-waypoints.json').write_text(json.dumps(out,sort_keys=True,indent=2,ensure_ascii=False)+'\n')
(H/'rfi-schematic.geojson').write_text(json.dumps({'type':'FeatureCollection','features':features},sort_keys=True,separators=(',',':'),ensure_ascii=False))
print(out['waypoint_table_id'],len(rows),sum(r['lat'] is None for r in rows))
