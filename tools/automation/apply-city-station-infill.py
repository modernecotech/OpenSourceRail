#!/usr/bin/env python3
"""Apply explicit planning infill along current corridors, with dry platform points."""
import argparse
import gzip
import hashlib
import json
import math
from pathlib import Path
import re
import tomllib

ROOT=Path(__file__).resolve().parents[2]

def interpolate(coordinates, chainage, line_length, grid):
    lengths=[math.hypot((b[0]-a[0])*grid['m_per_deg_lon'],(b[1]-a[1])*grid['m_per_deg_lat']) for a,b in zip(coordinates,coordinates[1:])]
    total=math.fsum(lengths)
    if total<=0 or not 0<=chainage<=line_length:raise ValueError('Invalid corridor length/chainage')
    remaining=chainage/line_length*total
    for a,b,length in zip(coordinates,coordinates[1:],lengths):
        if remaining<=length and length>0:
            t=remaining/length
            return a[1]+t*(b[1]-a[1]),a[0]+t*(b[0]-a[0])
        remaining-=length
    return coordinates[-1][1],coordinates[-1][0]

def infill(stations, lines, geometry, grid, mask, maximum_gap_m, minimum_gap_m):
    if not 1200<=minimum_gap_m<=maximum_gap_m<=2000:raise ValueError('Infill spacing requires 1200–2000 m bounds')
    if len(mask)!=grid['width']*grid['height']:raise ValueError('Water mask shape mismatch')
    additions=[]
    for line in lines:
        current=sorted((s for s in stations if s['line']==line['name']),key=lambda s:s['s_m'])
        for first,last in zip(current,current[1:]):
            gap=last['s_m']-first['s_m'];bays=math.ceil(gap/maximum_gap_m)
            if bays<=1:continue
            if gap/bays<minimum_gap_m:raise ValueError('No compliant station spacing within controlled gap')
            for i in range(1,bays):
                chainage=first['s_m']+gap*i/bays
                lat,lon=interpolate(geometry[line['name']],chainage,line['length_m'],grid)
                row=math.floor((grid['bbox_north']-lat)*grid['m_per_deg_lat']/grid['cell_m'])
                col=math.floor((lon-grid['bbox_west'])*grid['m_per_deg_lon']/grid['cell_m'])
                if not 0<=row<grid['height'] or not 0<=col<grid['width'] or mask[row*grid['width']+col]>=50:
                    raise ValueError('Infill platform requires a dry in-grid point and survey review')
                additions.append(dict(id=f"{line['name']}-planning-infill-s{round(chainage):06d}",line=line['name'],lat=lat,lon=lon,s_m=round(chainage,1),anchor_kind='planning:infill',anchor_name=f'Planning infill {i}',archetype='standard',platform_length_m=first['platform_length_m']))
    return additions

def apply(path):
    policy_path=path.with_name('station-infill-policy.toml')
    if not policy_path.exists():return False
    policy=tomllib.loads(policy_path.read_text())
    if set(policy)!={'maximum_gap_m','minimum_gap_m','basis'} or not str(policy['basis']).strip():raise ValueError('Infill policy requires bounded spacing and a planning basis')
    text=path.read_text();d=tomllib.loads(text);slug=d['city']['slug'];city=path.parent;out=city/'engineering/alignment'
    corridor=city/(slug+'.corridor.geojson');grid_path=out/'planning-grid.json';mask_path=out/'planning-water-mask.bin.gz'
    geometry={f['properties']['name']:f['geometry']['coordinates'] for f in json.loads(corridor.read_text())['features'] if f['properties'].get('kind')=='line'}
    additions=infill(d['stations'],d['lines'],geometry,json.loads(grid_path.read_text()),gzip.decompress(mask_path.read_bytes()),policy['maximum_gap_m'],policy['minimum_gap_m'])
    existing=[s for s in d['stations'] if s.get('anchor_kind')=='planning:infill']
    if existing:
        expected=infill([s for s in d['stations'] if s.get('anchor_kind')!='planning:infill'],d['lines'],geometry,json.loads(grid_path.read_text()),gzip.decompress(mask_path.read_bytes()),policy['maximum_gap_m'],policy['minimum_gap_m'])
        if sorted(existing,key=lambda s:s['id'])!=sorted(expected,key=lambda s:s['id']):raise ValueError('Planning infill differs from controlled corridor/policy')
    capex_path=ROOT/'lib/templates/capex-costs.toml';capex=tomllib.loads(capex_path.read_text())
    if additions:
        all_stations=sorted(d['stations']+additions,key=lambda s:(s['line'],s['s_m'],s['id']))
        blocks='\n'.join('[[stations]]\n'+''.join(k+' = '+json.dumps(v)+'\n' for k,v in station.items()) for station in all_stations)+'\n'
        text=re.sub(r'(?ms)^\[\[stations\]\].*?(?=^# \[\[depots\]\]|^\[\[depots\]\])',lambda _:blocks,text,count=1)
        station_cost=round(sum(capex['station_unit_usd'][s['archetype']] for s in all_stations))
        charging=round(sum(capex['charging_microgrid_unit_usd'][s['archetype']] for s in all_stations)*d['costs']['technology_basis']['station_charging_cabinet_count'])
        net=d['costs']['total_usd']-d['costs']['epc_overhead_usd']-d['costs']['stations_usd']-d['costs']['charging_microgrid_usd']+station_cost+charging
        epc=round(net*capex['overhead']['epc_fraction'])
        for key,value in [('stations_usd',station_cost),('charging_microgrid_usd',charging),('epc_overhead_usd',epc),('total_usd',round(net+epc))]:
            for name,amount in [(key,value),(key.replace('_usd','_eur'),round(value*capex['schema']['usd_to_eur']))]:
                text,n=re.subn(r'^('+name+r'\s*=\s*)[^\s#]+',lambda m:m[1]+str(amount),text,count=1,flags=re.M)
                if n!=1:raise ValueError('Missing priced infill field '+name)
        current=tomllib.loads(text)
        for key in d.keys()-{'stations','costs'}:
            if current[key]!=d[key]:raise ValueError('Infill changed another controlled inventory: '+key)
        path.write_text(text);d=current
        points_path=city/(slug+'.stations.json');points=json.loads(points_path.read_text());points.extend({k:v for k,v in a.items() if k not in {'archetype','platform_length_m'}}|{'demand':0.0,'demand_basis':'Uncalibrated planning infill; no observed ridership claimed'} for a in additions)
        points.sort(key=lambda s:(s['line'],s['s_m'],s['id']));points_path.write_text(json.dumps(points,indent=2)+'\n')
    report=dict(city=slug,physical_release=False,policy=policy,planning_infill_stations=[s for s in d['stations'] if s.get('anchor_kind')=='planning:infill'],sources_sha256={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in [path,policy_path,corridor,grid_path,mask_path,capex_path,Path(__file__)]},limitations=['Planning point locations only; footprints, land, structure, utilities, access and ridership require independent project evidence.','Existing fleet is retained conservatively; complete nominal/degraded service and current energy, depot and finance regeneration remain required.'])
    (out/'station-infill.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    return bool(additions)

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--design',type=Path,required=True);args=parser.parse_args();print('Planning station infill: '+str(apply(args.design.resolve())))
