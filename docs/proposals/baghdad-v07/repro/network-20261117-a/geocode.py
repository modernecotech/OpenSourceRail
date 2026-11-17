"""Fetch Baghdad RFI place-name candidates from OSM Nominatim with 1 r/s pacing."""
import json,time,urllib.parse,urllib.request
from pathlib import Path
HERE=Path(__file__).resolve().parent
names=[
 'Al Allawi','Al Mansour','Al Nusour Square','Al Yarmouk','Al Bayaa',
 'Al Eelam','Al Saydiyya','Doura','Adan Square','Al Kadhimiya',
 'Al Adhamiya','Antar Square','Al Mustansiriya','Qanat Al Jaish',
 'Maisaloun Square','Al Shaab','Al Waziriya','Al Jamhouriya Street',
 'Al Khallani Square','Al Tayaran Square','Al Andalus',
 'Uqba Bin Nafi Square','Al Zuafaraniya','Hamza Square','55 Square',
 '83 Square','Nadi Al Naft Intersection','Ur','Al Baladiyat',
 'Al Hasanin Square','Al Chadriya Square','Hay Al Jamiaa',
 'Al Shulah','Al Gazaliya','Al Khadhraa','Al Amiriya',
 'Hay Al Aamil','Um Al Tubol','Al Qadisiya',
]
out={}
for i,name in enumerate(names):
 q=name+', Baghdad, Iraq'
 params={'q':q,'format':'jsonv2','limit':3,'addressdetails':1,
         'viewbox':'44.2,33.5,44.75,33.05','bounded':1}
 url='https://nominatim.openstreetmap.org/search?'+urllib.parse.urlencode(params)
 req=urllib.request.Request(url,headers={'User-Agent':'OpenSourceRail research contact github.com/modernecotech/OpenSourceRail'})
 try:
  rows=json.load(urllib.request.urlopen(req,timeout=15))
  out[name]={'query':q,'url':url,'results':[
   {'lat':r['lat'],'lon':r['lon'],'osm_type':r['osm_type'],'osm_id':r['osm_id'],
    'type':r['type'],'category':r.get('category'),'display_name':r['display_name'],
    'boundingbox':r.get('boundingbox')} for r in rows]}
 except Exception as e:
  out[name]={'query':q,'url':url,'error':type(e).__name__+': '+str(e),'results':[]}
 (HERE/'rfi-geocode-raw.json').write_text(json.dumps(out,sort_keys=True,ensure_ascii=False,separators=(',',':')))
 print(i+1,len(names),name,len(out[name]['results']),flush=True)
 if i<len(names)-1:time.sleep(1.05)
