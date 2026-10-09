"""Add connected residential rail lines to controlled corridor inventories.

Immutable pre-expansion design bytes preserve the baseline. Population counts
select neighbourhoods; routing costs never become prices. Native station/fleet/
civil/service/finance generation must follow, with actual coverage audited again.
"""
from __future__ import annotations

from copy import deepcopy
import gzip
import hashlib
import io
import importlib.util
import json
import math
from pathlib import Path
import subprocess
import tomllib

import numpy as np
from scipy.spatial import cKDTree
from shapely.geometry import LineString
from skimage.graph import MCP_Geometric

from city_access import EARTH_RADIUS_M, xyz

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / 'design/network-planning/residential-expansion.json'
BACKTRACK_VALIDATOR=ROOT/'tools/automation/validate-ring-interchanges.py'
_spec=importlib.util.spec_from_file_location('residential_alignment_guard',BACKTRACK_VALIDATOR)
_guard=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(_guard)


def encoded(value):
    return (json.dumps(value, indent=2, sort_keys=True, allow_nan=False)+'\n').encode()


def packed(raw):
    data = bytearray(gzip.compress(raw, mtime=0)); data[9] = 255
    return bytes(data)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def baseline(path, check=False):
    archive = path.parent/'engineering/alignment/network-expansion-baseline.json.gz'
    if not archive.exists():
        if check:
            raise ValueError('Missing immutable expansion baseline: '+str(path))
        raw = path.read_bytes()
        value = dict(design_toml=raw.decode(), design_sha256=hashlib.sha256(raw).hexdigest(),
                     capture_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip())
        archive.write_bytes(packed(encoded(value)))
    value = json.loads(gzip.decompress(archive.read_bytes()))
    if hashlib.sha256(value['design_toml'].encode()).hexdigest()!=value['design_sha256']:
        raise ValueError('Expansion baseline bytes changed: '+str(archive))
    return tomllib.loads(value['design_toml']), archive


def cell_lonlat(cells, grid):
    cells = np.asarray(cells, dtype=float)
    return np.column_stack((grid['bbox_west']+(cells[:,1]+.5)*grid['cell_m']/grid['m_per_deg_lon'],
                            grid['bbox_north']-(cells[:,0]+.5)*grid['cell_m']/grid['m_per_deg_lat']))


def lonlat_cell(lon, lat, grid):
    return (round((grid['bbox_north']-lat)*grid['m_per_deg_lat']/grid['cell_m']-.5),
            round((lon-grid['bbox_west'])*grid['m_per_deg_lon']/grid['cell_m']-.5))


def dry_point(cell, mask, buildable, cell_m, radius_m=400):
    radius = math.ceil(radius_m/cell_m); r,c = cell
    candidates=[]
    for row in range(max(0,r-radius),min(mask.shape[0],r+radius+1)):
        for col in range(max(0,c-radius),min(mask.shape[1],c+radius+1)):
            distance = math.dist(cell,(row,col))*cell_m
            if distance<=radius_m and mask[row,col]==0 and buildable[row,col]:
                candidates.append((distance,row,col))
    if not candidates:
        return None
    _,r,c=min(candidates)
    return (r,c)


def route_between(start, end, mask, buildable, cfg, cell_m):
    """Bounded raster investigation route; short wet runs stay bridge scopes."""
    margin=math.ceil(cfg['route_search_margin_m']/cell_m)
    r0=max(0,min(start[0],end[0])-margin); r1=min(mask.shape[0],max(start[0],end[0])+margin+1)
    c0=max(0,min(start[1],end[1])-margin); c1=min(mask.shape[1],max(start[1],end[1])+margin+1)
    wet=mask[r0:r1,c0:c1]; blocked=(~buildable[r0:r1,c0:c1])|(wet==255)
    costs=np.where(blocked,np.inf,np.where(wet>0,100.,1.))
    a=(start[0]-r0,start[1]-c0); b=(end[0]-r0,end[1]-c0)
    for diagonal in [True,False]:
        solver=MCP_Geometric(costs,fully_connected=diagonal)
        distances,_=solver.find_costs([a],[b])
        if not np.isfinite(distances[b]):
            raise ValueError('No route within the bounded water/buildability search')
        local=solver.traceback(b)
        if any(x[0]!=y[0] and x[1]!=y[1] and (blocked[x[0],y[1]] or blocked[y[0],x[1]])
               for x,y in zip(local,local[1:])):
            continue
        length=0.; longest=0.
        for x,y in zip(local,local[1:]):
            if wet[x]>0 or wet[y]>0:
                length+=math.dist(x,y)*cell_m; longest=max(longest,length)
            else:
                length=0.
        if longest>cfg['maximum_water_crossing_m']:
            raise ValueError('Route requires a separately approved long water crossing')
        return [(r+r0,c+c0) for r,c in local]
    raise ValueError('Route cuts a forbidden buildability corner')


def station_samples(cells, mask, spacing_m, cell_m):
    lengths=np.r_[0.,np.cumsum([math.dist(a,b)*cell_m for a,b in zip(cells,cells[1:])])]
    targets=sorted(set([0.,float(lengths[-1]),*np.arange(spacing_m/2,lengths[-1],spacing_m)]))
    samples=[]
    for target in targets:
        nearby=sorted(range(len(cells)),key=lambda i:(abs(lengths[i]-target),i))
        for i in nearby:
            if abs(lengths[i]-target)>400:
                break
            if mask[tuple(cells[i])]==0:
                samples.append(cells[i]);break
    return samples


def connect_nearby_rings(cells, priority_cells, rings, route, cell_m, envelope_m=600., allow_proposed_terminal_crop=False, maximum_terminal_crop_m=600.):
    """Give a near-ring line a real common cell while preserving priority sites.

    A short continuous diversion replaces a route interval; no out-and-back
    branch or fictitious walking/grouping link is inserted.
    """
    result=list(map(tuple,cells));priority=set(map(tuple,priority_cells))
    def valid_extension(extension,previous,endpoint,revised):
        if LineString([(c,r) for r,c in revised]).is_simple:return True
        if not allow_proposed_terminal_crop:return False
        new=LineString([(c,r) for r,c in extension]);old=LineString([(c,r) for r,c in previous])
        intersection=new.intersection(old)
        return new.is_simple and intersection.geom_type=='Point' and tuple(intersection.coords[0])==(endpoint[1],endpoint[0])
    for ring in rings:
        ring_cells=list(map(tuple,ring['cells'])); ring_set=set(ring_cells)
        tree=cKDTree(ring_cells)
        for at_start in [True,False]:
            endpoint=result[0] if at_start else result[-1]
            if endpoint in ring_set:continue
            distance,index=tree.query(endpoint)
            if float(distance)*cell_m>envelope_m:continue
            target=ring_cells[int(index)]
            extension=route(target,endpoint) if at_start else route(endpoint,target)
            revised=extension[:-1]+result if at_start else result+extension[1:]
            if not valid_extension(extension,result,endpoint,revised):
                alternatives=sorted((math.dist(endpoint,ring_cells[i]),ring_cells[i])
                    for i in tree.query_ball_point(endpoint,envelope_m/cell_m)
                    if ring_cells[i] not in set(result))
                selected=[]
                for _,alternative in alternatives:
                    if any(math.dist(alternative,other)*cell_m<60 for other in selected):continue
                    selected.append(alternative)
                    try:
                        extension=route(alternative,endpoint) if at_start else route(endpoint,alternative)
                    except ValueError:continue
                    trial=extension[:-1]+result if at_start else result+extension[1:]
                    if valid_extension(extension,result,endpoint,trial):
                        revised=trial;break
                    if len(selected)>=16:break
            if not valid_extension(extension,result,endpoint,revised):
                contacts=[i for i,cell in enumerate(result) if cell in ring_set]
                if allow_proposed_terminal_crop and contacts:
                    stop=contacts[0] if at_start else contacts[-1]
                    tail=result[:stop+1] if at_start else result[stop:]
                    removed=math.fsum(math.dist(a,b)*cell_m for a,b in zip(tail,tail[1:]))
                    if removed<=maximum_terminal_crop_m:
                        revised=result[stop:] if at_start else result[:stop+1]
                        priority&=set(revised)
                    else:raise ValueError('Ring terminal retrace would exceed the controlled crop envelope')
                else:raise ValueError('Ring terminal connection would retrace the line; choose another corridor')
            result=revised
        if ring_set.intersection(result):continue
        distances,indices=tree.query(result)
        index=int(np.argmin(distances));distance=float(distances[index])*cell_m
        if distance>envelope_m:continue
        target=ring_cells[int(indices[index])]
        chain=np.r_[0.,np.cumsum([math.dist(a,b)*cell_m for a,b in zip(result,result[1:])])]
        first=max(0,int(np.searchsorted(chain,chain[index]-1600)))
        last=min(len(result)-1,int(np.searchsorted(chain,chain[index]+1600)))
        if first==last:raise ValueError('Near-ring connector has no continuous route interval')
        preserved=[c for c in result[first+1:last] if c in priority]
        possibilities=[]
        for slot in range(len(preserved)+1):
            waypoints=[result[first],*preserved[:slot],target,*preserved[slot:],result[last]]
            proposed=[]
            try:
                for a,b in zip(waypoints,waypoints[1:]):
                    piece=route(a,b)
                    proposed.extend(piece if not proposed else piece[1:])
            except ValueError:
                continue
            revised=result[:first]+proposed+result[last+1:]
            if len(revised)<2 or not priority<=set(revised):continue
            if not LineString([(c,r) for r,c in revised]).is_simple:continue
            length=math.fsum(math.dist(a,b)*cell_m for a,b in zip(revised,revised[1:]))
            possibilities.append((round(length,3),slot,revised))
        if not possibilities:raise ValueError('No simple protected/water-compliant continuous ring connection preserves priority sites')
        result=min(possibilities,key=lambda item:(item[0],item[1]))[2]
    return result


def population_inputs(city, design):
    pixels=city/'engineering/access/population-pixels.npz.gz'
    receipt=city/'engineering/access/population-source.json'
    if not pixels.exists() or not receipt.exists():
        return None,[], 'No retained native population counts; additional-line targeting remains unavailable.'
    source=json.loads(receipt.read_text())
    if sha(pixels)!=source['retained_sha256'] or source['bbox']!=design['city']['bbox']:
        raise ValueError('Altered or wrong-bbox expansion population evidence')
    access=json.loads((city/'engineering/access/summary.json').read_text())
    if access['population']['status']!='available':
        return None,[pixels,receipt], 'Retained population is unavailable under the controlled jurisdiction/source finding.'
    with np.load(io.BytesIO(gzip.decompress(pixels.read_bytes())),allow_pickle=False) as values:
        keep=values['valid']&(values['counts']>0)
        data={k:values[k][keep].copy() for k in ('lat','lon','counts')}
    return data,[pixels,receipt],None


def plan(routes, stations, grid, mask, buildable, population, cfg):
    """Greedy bounded line addition, with native-pixel union accounting."""
    result=deepcopy(routes); cell_m=grid['cell_m']
    lat,lon,counts=(population[k] for k in ('lat','lon','counts'))
    total=math.fsum(map(float,counts))
    if total<=0:
        raise ValueError('No positive retained population')
    tree=cKDTree(xyz(lat,lon))
    radius=2*math.sin(cfg['station_radius_m']/(2*EARTH_RADIUS_M))
    def members(cells):
        if not cells:
            return np.array([],dtype=int)
        positions=cell_lonlat(cells,grid)
        groups=tree.query_ball_point(xyz(positions[:,1],positions[:,0]),radius)
        return np.unique(np.concatenate([np.asarray(g,dtype=int) for g in groups]))
    covered=np.zeros(len(counts),dtype=bool)
    if stations:
        groups=tree.query_ball_point(xyz([s['lat'] for s in stations],[s['lon'] for s in stations]),radius)
        covered[np.unique(np.concatenate([np.asarray(g,dtype=int) for g in groups]))]=True
    baseline_fraction=math.fsum(map(float,counts[covered]))/total
    baseline_covered=covered.copy()
    for line in routes['lines']:
        covered[members(station_samples(line['cells'],mask,cfg['maximum_ordinary_station_gap_m'],cell_m))]=True
    infill_fraction=math.fsum(map(float,counts[covered]))/total
    # Selection credits retained baseline stops and explicit priority sites.
    # Spacing/consolidation can remove ordinary sampled sites, so their larger
    # catchment screen is never used to declare the line-addition target met.
    covered=baseline_covered.copy()
    rows=(grid['bbox_north']-lat)*grid['m_per_deg_lat']/cell_m-.5
    cols=(lon-grid['bbox_west'])*grid['m_per_deg_lon']/cell_m-.5
    bin_cells=cfg['priority_bin_m']/cell_m
    keys=np.column_stack((np.floor(rows/bin_cells),np.floor(cols/bin_cells))).astype(int)
    bins={}
    for i in np.flatnonzero(~covered):
        key=tuple(keys[i]); bins.setdefault(key,[]).append(int(i))
    areas=[]
    for key,indices in bins.items():
        indices=np.asarray(indices,dtype=int); weights=counts[indices].astype(float)
        if weights.sum()<=0:
            continue
        centre=(float(np.average(rows[indices],weights=weights)),float(np.average(cols[indices],weights=weights)))
        dry=dry_point(tuple(round(v) for v in centre),mask,buildable,cell_m)
        if dry is None:
            continue
        indices=members([dry]); gain=round(math.fsum(map(float,counts[indices[~covered[indices]]])),3)
        areas.append(dict(bin=list(map(int,key)),cell=dry,initial_unserved_residents=gain))
    selected=[]
    for area in ([] if baseline_fraction>=cfg['target_station_radial_fraction'] else sorted(areas,key=lambda a:(-a['initial_unserved_residents'],a['bin']))):
        if len(selected)>=cfg['maximum_priority_areas']:
            break
        if any(math.dist(area['cell'],a['cell'])*cell_m<cfg['minimum_priority_separation_m'] for a in selected):
            continue
        selected.append(area)
    base_vertices=[]
    for line in routes['lines']:
        base_vertices.extend((tuple(c),line['name']) for c in line['cells'] if mask[tuple(c)]==0 and buildable[tuple(c)])
    if not base_vertices:
        raise ValueError('No dry existing corridor connection')
    base_vertices=sorted(set(base_vertices)); base_tree=cKDTree([v[0] for v in base_vertices])
    candidates=[]; rejected=[]
    def length(cells):
        return math.fsum(math.dist(a,b)*cell_m for a,b in zip(cells,cells[1:]))
    original_length=math.fsum(length(l['cells']) for l in routes['lines'])
    minimum_line=min(6000.,max(cfg['minimum_line_m'],original_length*.02))
    route_cache={}
    rings=[line for line in routes['lines'] if line['shape']=='Ring']
    def cached_route(first,last):
        key=tuple(sorted((tuple(first),tuple(last))))
        if key not in route_cache:
            try:
                route_cache[key]=route_between(key[0],key[1],mask,buildable,cfg,cell_m)
            except ValueError as error:
                route_cache[key]=str(error)
        value=route_cache[key]
        if isinstance(value,str):raise ValueError(value)
        return value if tuple(first)==key[0] else list(reversed(value))
    for area in selected:
        _,index=base_tree.query(area['cell']); connection,line_name=base_vertices[int(index)]
        try:
            path=cached_route(connection,area['cell'])
            choices=[(path,[area])]
            outward=np.subtract(area['cell'],connection)
            extensions=sorted((a for a in selected if a is not area and
                               1500<=math.dist(a['cell'],area['cell'])*cell_m<=8000 and
                               np.dot(outward,np.subtract(a['cell'],area['cell']))>=0),
                              key=lambda a:(-a['initial_unserved_residents'],a['bin']))
            for other in extensions[:3]:
                try:
                    extra=cached_route(area['cell'],other['cell'])
                    joined=path+extra[1:]
                    choices.append((joined,[area,other]))
                    onward=np.subtract(other['cell'],area['cell'])
                    further=sorted((a for a in selected if a is not area and a is not other and
                                    1500<=math.dist(a['cell'],other['cell'])*cell_m<=8000 and
                                    np.dot(onward,np.subtract(a['cell'],other['cell']))>=0),
                                   key=lambda a:(-a['initial_unserved_residents'],a['bin']))
                    for third in further[:2]:
                        try:
                            tail=cached_route(other['cell'],third['cell'])
                            choices.append((joined+tail[1:],[area,other,third]))
                        except ValueError:
                            continue
                except ValueError:
                    continue
            # Connect useful through-lines at both ends where a different
            # retained corridor is available. This is an identified geometric
            # interface, never an inferred rail switch or accepted interchange.
            through=[]
            for cells,served_areas in choices:
                end=cells[-1]
                connections=sorted((math.dist(end,c),c,name) for c,name in base_vertices
                    if name!=line_name and math.dist(c,connection)*cell_m>=1500)
                if connections and connections[0][0]*cell_m<=8000:
                    _,last,last_line=connections[0]
                    try:
                        tail=cached_route(end,last)
                        through.append((cells+tail[1:],served_areas,last_line,last))
                    except ValueError:
                        pass
            choices=[(cells,areas,None,None) for cells,areas in choices]+through
            for cells,served_areas,end_line,end_cell in choices:
                priority_cells=[a['cell'] for a in served_areas]
                try:
                    cells=connect_nearby_rings(cells,priority_cells,rings,cached_route,cell_m)
                except ValueError:
                    continue
                distance=length(cells)
                if not minimum_line<=distance<=cfg['maximum_line_m']:
                    continue
                if not LineString([(c,r) for r,c in cells]).is_simple:
                    continue
                if _guard.backtracking_finding('candidate',cell_lonlat(cells,grid).tolist()) is not None:
                    continue
                indices=members([cells[0],cells[-1],*priority_cells])
                candidates.append(dict(cells=cells,connection_line=line_name,connection_cell=connection,
                                       end_connection_line=end_line,end_connection_cell=end_cell,
                                       priority_areas=[a['bin'] for a in served_areas],priority_cells=priority_cells,
                                       length_m=distance,members=indices))
        except ValueError as error:
            rejected.append(dict(priority_bin=area['bin'],reason=str(error)))
    route_limit=min(cfg['maximum_added_route_m'],original_length*cfg['maximum_added_route_fraction'])
    added=[]; route_m=0.
    next_number=max((int(l['name'].split('-')[-1]) for l in result['lines']),default=0)+1
    minimum_gain=max(cfg['minimum_incremental_population'],total*cfg['minimum_population_fraction_per_line'])
    while candidates and len(added)<cfg['maximum_added_lines']:
        if math.fsum(map(float,counts[covered]))/total>=cfg['target_station_radial_fraction']:
            break
        ranked=[]
        for i,candidate in enumerate(candidates):
            if route_m+candidate['length_m']>route_limit:
                continue
            indices=candidate['members']; gain=math.fsum(map(float,counts[indices[~covered[indices]]]))
            density=gain/(candidate['length_m']/1000)
            if gain>=minimum_gain and density>=cfg['minimum_incremental_residents_per_km']:
                ranked.append((round(gain/math.sqrt(candidate['length_m']/1000),3),round(gain,3),i))
        if not ranked:
            break
        _,gain,index=min(ranked,key=lambda a:(-a[0],-a[1],a[2]))
        candidate=candidates.pop(index); name=f'line-{next_number}'; next_number+=1
        result['lines'].append(dict(name=name,shape='Radial',anchor_ids=[],cells=[list(c) for c in candidate['cells']]))
        covered[candidate['members']]=True; route_m+=candidate['length_m']
        added.append({k:v for k,v in candidate.items() if k not in ('cells','members')} |
                     dict(line=name,incremental_residents_2020=round(gain,3),
                          connection_kind='actual common corridor cell; mandatory native platform pair and civil junction design required',
                          geometry_basis='bounded water/buildability raster investigation route',
                          property_curve_vertical_profile_and_structural_release=False))
    fraction=math.fsum(map(float,counts[covered]))/total
    report=dict(population_year=2020,bbox_population_2020=round(total,3),
                original_line_count=len(routes['lines']),added_line_count=len(added),final_line_count=len(result['lines']),
                original_route_m=round(original_length,3),added_route_m=round(route_m,3),
                added_route_limit_m=round(route_limit,3),target_radial_fraction=cfg['target_station_radial_fraction'],
                baseline_actual_station_radial_fraction=round(baseline_fraction,8),
                baseline_with_sampled_infill_radial_fraction=round(infill_fraction,8),
                proposed_station_sample_radial_fraction=round(fraction,8),
                planned_stop_cells_by_line={line['name']:station_samples(line['cells'],mask,cfg['maximum_ordinary_station_gap_m'],cell_m)
                                           for line in result['lines']},
                target_met_in_proposed_station_sample=fraction>=cfg['target_station_radial_fraction'],
                actual_regenerated_station_coverage=None,added_lines=added,rejected_priority_areas=rejected,
                outcome='target reached in station-sample screen' if fraction>=cfg['target_station_radial_fraction'] else
                        'bounded candidates exhausted; remaining residential gaps require further route/source/site investigation')
    return result,report


def expand(design_path,routes,grid,mask,buildable,check=False):
    cfg=json.loads(CONFIG.read_text()); design,archive=baseline(design_path,check)
    city=design_path.parent; data,inputs,reason=population_inputs(city,design)
    routes=deepcopy(routes)
    rings=[line for line in routes['lines'] if line['shape']=='Ring']
    base_junction_changes=[];base_junction_reviews=[]
    for line in routes['lines']:
        if line['shape']!='Radial':continue
        original=list(map(tuple,line['cells']));existing=set(original)
        protected_sites=[lonlat_cell(s['lon'],s['lat'],grid) for s in design['stations'] if s['line']==line['name']]
        protected_sites=[cell for cell in protected_sites if cell in existing]
        try:
            revised=connect_nearby_rings(original,protected_sites,rings,
                lambda a,b:route_between(a,b,mask,buildable,cfg,grid['cell_m']),grid['cell_m'],allow_proposed_terminal_crop=True,
                maximum_terminal_crop_m=cfg['maximum_proposed_terminal_route_crop_m'])
        except ValueError as error:
            # A retained near-ring line can use a bounded platform complex.
            # Keep the actual corridor if a continuous diversion is infeasible;
            # native mandatory crossing/terminal/group checks still must pass.
            revised=original
            base_junction_reviews.append(dict(line=line['name'],continuous_diversion_adopted=False,
                reason=str(error),bounded_platform_complex_must_pass_native_validation=True,
                site_profile_structure_and_walking_access_accepted=False))
        if revised!=original:
            line['cells']=[list(cell) for cell in revised]
            base_junction_changes.append(dict(line=line['name'],kind='continuous physical ring connection',
                original_route_m=round(math.fsum(math.dist(a,b)*grid['cell_m'] for a,b in zip(original,original[1:])),3),
                final_route_m=round(math.fsum(math.dist(a,b)*grid['cell_m'] for a,b in zip(revised,revised[1:])),3),
                original_station_cells_preserved=set(protected_sites)<=set(revised),
                relocated_original_proposed_station_cells=[list(c) for c in protected_sites if c not in set(revised)],
                profile_structure_and_site_release=False))
    if data is None:
        result=deepcopy(routes)
        report=dict(status='population-evidence-unavailable',reason=reason,original_line_count=len(routes['lines']),
                    added_line_count=0,final_line_count=len(routes['lines']),target_radial_fraction=cfg['target_station_radial_fraction'])
    else:
        result,report=plan(routes,design['stations'],grid,mask,buildable,data,cfg)
        report['status']='expanded-controlled-planning-layout'
        policy='\n'.join(['# Population-led planning spacing; field access and platform approval remain open.',
                           f'maximum_gap_m = {float(cfg["maximum_ordinary_station_gap_m"])}',
                           'basis = "Retained population-led network revision; ordinary stop spacing cap, no walkshed or operating acceptance."',''])
        policy_path=city/'station-spacing-policy.toml'
        if check:
            if not policy_path.exists() or policy_path.read_text()!=policy:
                raise ValueError('Stale population-led station-spacing policy')
        else:
            policy_path.write_text(policy)
        inputs.append(policy_path)
    report.update(schema=cfg['schema'],as_of=cfg['as_of'],city=design['city']['slug'],
                  base_line_junction_changes=base_junction_changes,
                  base_line_junction_reviews=base_junction_reviews,
                  physical_release=False,operating_release=False,
                  population_is_current_census=False,accessible_walking_coverage_accepted=False,
                target_interpretation='Native 2020 station-circle union; measured regenerated stations must be audited separately.',
                  design_stage='Controlled network planning adoption; structural/site and operating acceptance remain open')
    paths=[CONFIG,Path(__file__),archive,BACKTRACK_VALIDATOR,ROOT/'tools/automation/city_access.py',
           ROOT/'docs/data/city-population-source-overrides.json',*inputs]
    report['sources_sha256']={p.relative_to(ROOT).as_posix():sha(p) for p in paths}
    path=city/'engineering/alignment/residential-line-expansion.json'; raw=encoded(report)
    if check:
        if not path.exists() or path.read_bytes()!=raw:
            raise ValueError('Stale population-led line expansion: '+str(path))
    else:
        path.write_bytes(raw)
    return result,report,paths+[path]
