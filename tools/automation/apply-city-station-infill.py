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
            previous_chainage=first['s_m']
            for i in range(1,bays):
                target=first['s_m']+gap*i/bays
                chosen=None
                for offset in [0,*[signed*delta for delta in range(20,401,20) for signed in [-1,1]]]:
                    chainage=target+offset
                    remaining=last['s_m']-chainage;future_bays=bays-i
                    if not minimum_gap_m<=chainage-previous_chainage<=maximum_gap_m or not future_bays*minimum_gap_m<=remaining<=future_bays*maximum_gap_m:continue
                    lat,lon=interpolate(geometry[line['name']],chainage,line['length_m'],grid)
                    row=math.floor((grid['bbox_north']-lat)*grid['m_per_deg_lat']/grid['cell_m'])
                    col=math.floor((lon-grid['bbox_west'])*grid['m_per_deg_lon']/grid['cell_m'])
                    if 0<=row<grid['height'] and 0<=col<grid['width'] and mask[row*grid['width']+col]==0:
                        chosen=(chainage,lat,lon);break
                if chosen is None:
                    raise ValueError('Infill platform requires a dry in-grid point and survey review')
                chainage,lat,lon=chosen;previous_chainage=chainage
                additions.append(dict(id=f"{line['name']}-planning-infill-s{round(chainage):06d}",line=line['name'],lat=lat,lon=lon,s_m=round(chainage,1),anchor_kind='planning:infill',anchor_name=f'Planning infill {i}',archetype='standard',platform_length_m=first['platform_length_m']))
    return additions

def transfer_groups(stations, previous, civil, lines=None):
    """Retain platforms on their own corridors and identify actual transfer legs."""
    stations=[dict(s) for s in stations];parent=list(range(len(stations)));terminals=set()
    for line in lines or []:
        if line['shape']=='ring':continue
        members=sorted((s for s in stations if s['line']==line['name']),key=lambda s:s['s_m'])
        if members:terminals.update([members[0]['id'],members[-1]['id']])
    def find(i):
        while parent[i]!=i:i=parent[i]
        return i
    def union(i,j):parent[find(j)]=find(i)
    for i,first in enumerate(stations):
        for j,second in enumerate(stations[:i]):
            if first['line']==second['line']:continue
            lat1,lat2=map(math.radians,[first['lat'],second['lat']]);dl=math.radians(first['lon']-second['lon'])
            distance=6371000*2*math.asin(min(1,math.sqrt(math.sin((lat1-lat2)/2)**2+math.cos(lat1)*math.cos(lat2)*math.sin(dl/2)**2)))
            if distance<=600 or first.get('junction_group') is not None and first.get('junction_group')==second.get('junction_group'):union(i,j)
    components={}
    for i,s in enumerate(stations):components.setdefault(find(i),[]).append(s)
    existing={g['junction_group']:g for g in previous};next_id=max(existing,default=-1)+1;groups=[]
    for members in components.values():
        if len({s['line'] for s in members})<2:continue
        old={s['junction_group'] for s in members if 'junction_group' in s};group=min(old) if old else next_id
        if not old:next_id+=1
        elevated=any(c['line']==s['line'] and c['from_station_m']<=s['s_m']<=c['to_station_m'] and c['class']=='elevated' for s in members for c in civil)
        for station in members:
            role=station['archetype'] if station['archetype'] in {'terminal','depot-terminal'} else 'terminal' if station['id'] in terminals else 'interchange-elevated' if elevated else 'interchange'
            station.update(junction_group=group,archetype=role)
        groups.append(dict(id=existing.get(group,{}).get('id',f'interchange-{group:03d}'),junction_group=group,lat=math.fsum(s['lat'] for s in members)/len(members),lon=math.fsum(s['lon'] for s in members)/len(members),lines=sorted({s['line'] for s in members}),platforms=sorted(s['id'] for s in members)))
    return stations,sorted(groups,key=lambda g:g['junction_group'])

def apply(path, report_only=False):
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
        fields=('id','line','lat','lon','s_m','anchor_kind','anchor_name','platform_length_m')
        if [{k:v[k] for k in fields} for v in sorted(existing,key=lambda s:s['id'])]!=[{k:v[k] for k in fields} for v in sorted(expected,key=lambda s:s['id'])]:raise ValueError('Planning infill differs from controlled corridor/policy')
    capex_path=ROOT/'lib/templates/capex-costs.toml';capex=tomllib.loads(capex_path.read_text())
    all_stations=sorted(d['stations']+additions,key=lambda s:(s['line'],s['s_m'],s['id']))
    all_stations,interchanges=transfer_groups(all_stations,d.get('interchanges',[]),d['civil_segments'],d['lines'])
    if report_only and (additions or all_stations!=d['stations'] or interchanges!=d.get('interchanges',[])):
        raise ValueError('Report-only infill differs from the controlled stations or transfers')
    if additions or all_stations!=d['stations'] or interchanges!=d.get('interchanges',[]):
        blocks='\n'.join('[[stations]]\n'+''.join(k+' = '+json.dumps(v)+'\n' for k,v in station.items()) for station in all_stations)+'\n'
        blocks+='\n'.join('[[interchanges]]\n'+''.join(k+' = '+json.dumps(v)+'\n' for k,v in group.items()) for group in interchanges)+'\n'
        text=re.sub(r'(?ms)^\[\[stations\]\].*?(?=^# \[\[depots\]\]|^\[\[depots\]\])',lambda _:blocks,text,count=1)
        station_cost=round(sum(capex['station_unit_usd'][s['archetype']] for s in all_stations))
        charging=round(sum(capex['charging_microgrid_unit_usd'][s['archetype']] for s in all_stations)*d['costs']['technology_basis']['station_charging_cabinet_count'])
        elevated_groups=sum(any(c['line']==s['line'] and c['from_station_m']<=s['s_m']<=c['to_station_m'] and c['class']=='elevated' for s in all_stations if s.get('junction_group')==g['junction_group'] for c in d['civil_segments']) for g in interchanges)
        premium=round(elevated_groups*capex['junctions']['elevated_interchange_premium_usd'])
        net=d['costs']['total_usd']-d['costs']['epc_overhead_usd']-d['costs']['stations_usd']-d['costs']['charging_microgrid_usd']-d['costs']['junction_premium_usd']+station_cost+charging+premium
        epc=round(net*capex['overhead']['epc_fraction'])
        for key,value in [('stations_usd',station_cost),('charging_microgrid_usd',charging),('junction_premium_usd',premium),('civil_subtotal_usd',round(d['costs']['civil_subtotal_usd']-d['costs']['junction_premium_usd']+premium)),('epc_overhead_usd',epc),('total_usd',round(net+epc))]:
            for name,amount in [(key,value),(key.replace('_usd','_eur'),round(value*capex['schema']['usd_to_eur']))]:
                text,n=re.subn(r'^('+name+r'\s*=\s*)[^\s#]+',lambda m:m[1]+str(amount),text,count=1,flags=re.M)
                if n!=1:raise ValueError('Missing priced infill field '+name)
        current=tomllib.loads(text)
        for key in d.keys()-{'stations','costs','interchanges'}:
            if current[key]!=d[key]:raise ValueError('Infill changed another controlled inventory: '+key)
        path.write_text(text);d=current
    points_path=city/(slug+'.stations.json');points=json.loads(points_path.read_text());by_id={s['id']:s for s in points}
    for station in d['stations']:
        fields={k:v for k,v in station.items() if k not in {'archetype','platform_length_m'}}
        if station['id'] in by_id:by_id[station['id']].update(fields)
        else:by_id[station['id']]={**fields,'demand':0.0,'demand_basis':'Uncalibrated planning infill; no observed ridership claimed'}
    points=sorted(by_id.values(),key=lambda s:(s['line'],s['s_m'],s['id']))
    if not report_only:points_path.write_text(json.dumps(points,indent=2)+'\n')
    quality_path=city/(slug+'.design-quality.yaml')
    if quality_path.exists() and not report_only:
        quality=quality_path.read_text();hit=sum(bool(s.get('anchor_kind')) and s.get('anchor_kind')!='planning:infill' for s in d['stations'])/len(d['stations'])
        quality=re.sub(r'(n_stations:\s*)\d+',lambda m:m[1]+str(len(d['stations'])),quality)
        quality=re.sub(r'(anchor_hit_rate:\s*)[\d.]+',lambda m:m[1]+f'{hit:.3f}',quality)
        quality_path.write_text(quality)
    report=dict(city=slug,physical_release=False,policy=policy,planning_infill_stations=[s for s in d['stations'] if s.get('anchor_kind')=='planning:infill'],sources_sha256={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in [path,policy_path,corridor,grid_path,mask_path,capex_path,Path(__file__)]},limitations=['Planning point locations only; footprints, land, structure, utilities, access and ridership require independent project evidence.','Existing fleet is retained conservatively; complete nominal/degraded service and current energy, depot and finance regeneration remain required.'])
    (out/'station-infill.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    return bool(additions)

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--design',type=Path,required=True)
    parser.add_argument('--report-only',action='store_true',help='verify retained controlled infill and recompute its report without changing design or map inputs')
    args=parser.parse_args();print('Planning station infill: '+str(apply(args.design.resolve(),args.report_only)))
