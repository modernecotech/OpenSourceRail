#!/usr/bin/env python3
"""Replace forced core chords and connect the complete controlled line graph."""
import argparse
from copy import deepcopy
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import tomllib

import numpy as np
from shapely.geometry import LineString
from city_network_layout import connect_network,length,remove_small_knots,reverse_excursion
from residential_route_expansion import route_between,terrain_cost
from retained_city_demand import restore as restore_demand,GridRef

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('previous_city_alignment',ROOT/'tools/automation/rework-city-alignment.py')
legacy=importlib.util.module_from_spec(spec);spec.loader.exec_module(legacy)


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def encoded(value):return (json.dumps(value,sort_keys=True,indent=2,allow_nan=False)+'\n').encode()


def run(design_path,check=False):
    city=design_path.parent;design=tomllib.loads(design_path.read_text());slug=design['city']['slug']
    if slug=='baghdad':raise ValueError('Baghdad retains its separately controlled planner')
    out=city/'engineering/alignment';grid_path=out/'planning-grid.json';grid=json.loads(grid_path.read_text())
    source=out/'pre-network-correction.json.gz'
    if not source.exists():
        if check:raise ValueError('Missing immutable network correction input')
        source.write_bytes(gzip.compress((city/'corridors.json').read_bytes(),mtime=0))
    live=json.loads((city/'corridors.json').read_text())
    retained=json.loads(gzip.decompress(source.read_bytes()))
    previous=out/'network-correction.json'
    if live!=retained and (not previous.exists() or
        hashlib.sha256(encoded(live)).hexdigest()!=json.loads(previous.read_text())['candidate_sha256']):
        raise ValueError('Prior planner input changed; preserve the old correction and adopt a new controlled input revision')
    routes=json.loads(gzip.decompress(source.read_bytes()));cell=grid['cell_m']
    shape=(grid['height'],grid['width'])
    mask_path=out/'planning-water-mask.bin.gz';build_path=out/'planning-buildability-mask.bin.gz'
    mask=np.frombuffer(gzip.decompress(mask_path.read_bytes()),dtype=np.uint8).reshape(shape)
    receipt=json.loads((out/'water-source-receipt.json').read_text())
    if hashlib.sha256(mask.tobytes()).hexdigest()!=receipt['mask_sha256']:raise ValueError('Water evidence differs')
    buildable=np.frombuffer(gzip.decompress(build_path.read_bytes()),dtype=np.uint8).reshape(shape).astype(bool)
    terrain,terrain_paths=terrain_cost(city,grid,check=True)
    cache=ROOT/'.cache/osr-pipeline/rasters';cost_path=cache/(slug+'.cost.npy')
    # Retain routing costs so regeneration/checking never depends on a deleted
    # cache or silently substitutes a featureless cost plane.
    retained_cost=out/'network-routing-cost.f32.gz'
    if not retained_cost.exists():
        if check:raise ValueError('Missing retained network routing cost')
        retained_cost.write_bytes(gzip.compress(cost_path.read_bytes(),mtime=0))
    costs=np.frombuffer(gzip.decompress(retained_cost.read_bytes()),dtype='<f4').reshape(shape)
    routing_cost=terrain*np.maximum(costs,.05)
    cfg=json.loads((ROOT/'design/network-planning/residential-expansion.json').read_text())
    cfg['route_search_margin_m']=max(cfg['route_search_margin_m'],3000.)
    old_seed_path=out/'pre-rework-corridors.json.gz'
    old_seed=json.loads(gzip.decompress(old_seed_path.read_bytes()))
    expansion=json.loads((out/'residential-line-expansion.json').read_text())
    protected={row['line']:row['priority_cells'] for row in expansion.get('added_lines',[])}
    for name,cells in expansion.get('planned_stop_cells_by_line',{}).items():
        protected.setdefault(name,[]).extend(cells)
    priorities_path=out/'pre-network-priority-sites.json'
    priority_bytes=encoded(protected)
    if not priorities_path.exists():
        if check:raise ValueError('Missing controlled priority-site input')
        priorities_path.write_bytes(priority_bytes)
    elif priorities_path.read_bytes()!=priority_bytes:raise ValueError('Controlled residential priority sites changed')
    layout_policy_path=city/'network-layout-policy.toml';knot_limits={};layout_policy=None
    if layout_policy_path.exists():
        layout_policy=tomllib.loads(layout_policy_path.read_text())
        if set(layout_policy)!={'schema_version','knot_cleanup'} or layout_policy['schema_version']!=1:raise ValueError('Invalid bounded knot policy')
        for row in layout_policy['knot_cleanup']:
            if (set(row)!={'line','maximum_removed_route_m','basis'} or row['line'] not in {l['name'] for l in routes['lines']}
                    or row['line'] in knot_limits or not 200<=row['maximum_removed_route_m']<=500 or not row['basis'].strip()):
                raise ValueError('Knot scope needs a named line, 200–500 m bound and explicit site-planning basis')
            knot_limits[row['line']]=row['maximum_removed_route_m']
    config=tomllib.loads(legacy.CONFIG.read_text());config['core']=tomllib.loads((city/'alignment-policy.toml').read_text())['core']
    config['geometry'].update(simplification_tolerance_m=75.,maximum_simplification_tolerance_m=150.,preferred_fillet_radius_m=300.)
    bank_path=city/'station-bank-policy.toml'
    if bank_path.exists():config['water_crossings']['maximum_endpoint_trim_m']=tomllib.loads(bank_path.read_text()).get('route_ends',{}).get('maximum_crop_m',600.)
    water_path=city/'water-route-policy.toml'
    if water_path.exists():
        policy=tomllib.loads(water_path.read_text());config['terminal_scopes']=policy.get('terminal_scopes',[])
        if 'maximum_endpoint_relocation_m' in policy:config['water_crossings']['maximum_endpoint_relocation_m']=policy['maximum_endpoint_relocation_m']
    restored=[];restoration_holds=[];source_reroutes=[]
    for line in routes['lines']:
        original=next((l for l in old_seed['lines'] if l['name']==line['name'] and l['shape']=='Radial'),None)
        if original is None:continue
        deviation=LineString(original['cells']).hausdorff_distance(LineString(line['cells']))*cell
        if deviation<=200:continue
        # "Radial" is a topology label, not permission to replace the route
        # by a core chord. Use the existing contour/fillet branch and retain
        # unfit source geometry, with the same water/protected/terrain limits.
        seed=deepcopy(old_seed);seed['lines']=[deepcopy(original)];seed['lines'][0]['shape']='Corridor'
        revised,detail=legacy.rework(seed,grid,config,mask,buildable,terrain)
        cells=revised['lines'][0]['cells'];cells,_=legacy.remove_closed_retraces(cells)
        if not set(map(tuple,protected.get(line['name'],[])))<=set(map(tuple,cells)):continue
        excursion=reverse_excursion(cells,cell)
        if excursion>max(750.,reverse_excursion(line['cells'],cell)):
            hold=dict(line=line['name'],source_reverse_excursion_m=excursion,
                reason='Source restoration worsens the 750 m reversal screen; retain the prior controlled corridor and require another constrained alignment decision',
                engineering_release=False)
            # A shoreline detour in the old source can itself be a hairpin.
            # Try a real constrained route between the retained termini;
            # never substitute a straight drawn connector across the water.
            a,b=map(tuple,(line['cells'][0],line['cells'][-1]));delta=np.subtract(b,a)
            norm=float(np.linalg.norm(delta));candidate=None
            if norm:
                rr,cc=np.indices(shape)
                progress=((rr-a[0])*delta[0]+(cc-a[1])*delta[1])/norm*cell
                allowed=buildable&(progress>=-740.)&(progress<=norm*cell+740.)
                try:candidate=route_between(a,b,mask,allowed,cfg,cell,routing_cost)
                except ValueError as error:hold['reroute_failure']=str(error)
            if (candidate and LineString(candidate).is_simple
                    and reverse_excursion(candidate,cell)<=750.
                    and length(candidate,cell)<=length(line['cells'],cell)+5000.
                    and set(map(tuple,protected.get(line['name'],[])))<=set(map(tuple,candidate))):
                source_reroutes.append(dict(line=line['name'],prior_route_m=length(line['cells'],cell),
                    final_route_m=length(candidate,cell),reverse_excursion_m=reverse_excursion(candidate,cell),
                    basis='Retained termini, actual routing costs, terrain, protected land and bounded water crossings; 740 m endpoint-axis search envelope and 750 m final reversal screen',
                    engineering_release=False))
                line['cells']=candidate
                hold['disposition']='source rejected; constrained replacement routed and separately audited'
            else:hold['disposition']='source rejected; prior controlled corridor retained; downstream audits remain mandatory'
            restoration_holds.append(hold)
            continue
        line['cells']=cells
        restored.append(dict(line=line['name'],former_source_deviation_m=deviation,
                             original_route_m=length(original['cells'],cell),final_route_m=length(cells,cell),
                             basis='Retained source corridor, bounded contour fillets and water/protected/terrain constraints; no forced radial chord',
                             geometry_details=detail['lines'][0]))
    def route(a,b,blocked):
        allowed=buildable
        if blocked:
            allowed=buildable.copy()
            for c in blocked:allowed[tuple(c)]=False
        return route_between(tuple(a),tuple(b),mask,allowed,cfg,cell,routing_cost)
    knots=[]
    for line in routes['lines']:
        cells,changes=remove_small_knots(line['cells'],cell,mask,buildable,required_cells=protected.get(line['name'],[]),maximum_removed_m=knot_limits.get(line['name'],200.))
        line['cells']=cells
        if changes:knots.append(dict(line=line['name'],changes=changes))
    routes,connections=connect_network(routes,mask,buildable,cell,route,protected_by_line=protected)
    demand,demand_paths=restore_demand(city,GridRef(**grid),check)
    paths=[Path(__file__),Path(__file__).with_name('city_network_layout.py'),Path(legacy.__file__),
           Path(__file__).with_name('residential_route_expansion.py'),source,old_seed_path,grid_path,
           mask_path,out/'water-source-receipt.json',build_path,retained_cost,legacy.CONFIG,ROOT/'design/network-planning/residential-expansion.json',
           city/'alignment-policy.toml',priorities_path,*terrain_paths,*demand_paths]
    paths += [p for p in (bank_path,water_path) if p.exists()]
    if layout_policy_path.exists():paths.append(layout_policy_path)
    report=dict(schema='osr-city-network-correction/1',city=slug,restored_route_shapes=restored,demand_recovery=demand,
                source_restoration_holds=restoration_holds,
                constrained_source_reroutes=source_reroutes,
                bounded_knot_corrections=knots,
                bounded_knot_policy=layout_policy,
                connectivity=connections,final_line_count=len(routes['lines']),
                final_route_m=sum(length(l['cells'],cell) for l in routes['lines']),
                source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in paths},
                candidate_sha256=hashlib.sha256(encoded(routes)).hexdigest(),
                scope='Controlled planning correction. Regenerate native stations, civil, service, energy, access and costs; physical, property, transfer and engineering acceptance remain open.',
                engineering_release=False,physical_release=False)
    report_path=out/'network-correction.json'
    outputs={city/'corridors.json':encoded(routes),report_path:encoded(report)}
    # Bind the former core and expansion stages to their final postprocessed
    # geometry, clearing analytical controls superseded by this correction.
    for name in ('core-realignment.json','residential-line-expansion.json'):
        path=out/name;value=json.loads(path.read_text())
        # The original stage remains historical evidence. Its water/geometry
        # inputs must not be relabelled as current after a source correction.
        # Final quantities below are derived from this correction's inputs.
        value.setdefault('pre_network_sources_sha256',dict(value['sources_sha256']))
        value['sources_sha256']={}
        value['network_correction']=dict(report=report_path.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(outputs[report_path]).hexdigest())
        value['sources_sha256'][report_path.relative_to(ROOT).as_posix()]=hashlib.sha256(outputs[report_path]).hexdigest()
        if name=='core-realignment.json':
            by_name={l['name']:l for l in routes['lines']}
            for row in value['lines']:
                row['reworked_route_m']=length(by_name[row['line']]['cells'],cell)
                row['reworked_cells']=len(by_name[row['line']]['cells'])
                cells=by_name[row['line']]['cells'];core=config['core']
                def inside(c):
                    lat=grid['bbox_north']-(c[0]+.5)*cell/grid['m_per_deg_lat']
                    lon=grid['bbox_west']+(c[1]+.5)*cell/grid['m_per_deg_lon']
                    return core['south']<=lat<=core['north'] and core['west']<=lon<=core['east']
                row['final_core_route_m']=sum(np.linalg.norm(np.subtract(a,b))*cell for a,b in zip(cells,cells[1:]) if inside(np.mean([a,b],axis=0)))
                for run in row['core_runs']:
                    run['superseded_analytical_controls']=run.get('superseded_analytical_controls',run.get('controls',[]));run['controls']=[]
                    run['geometry_basis']='final-network-correction; see network-correction.json; geometry release open'
            value['core_final_route_length_m']=sum(row['final_core_route_m'] for row in value['lines'])
            value['final_route_quantity_basis']='Final complete line lengths in network-correction.json; former core analytical quantities superseded'
        outputs[path]=encoded(value)
    core_path=out/'core-realignment.json';expansion_path=out/'residential-line-expansion.json'
    core_value=json.loads(outputs[core_path]);expansion_value=json.loads(outputs[expansion_path])
    core_value['sources_sha256'][expansion_path.relative_to(ROOT).as_posix()]=hashlib.sha256(outputs[expansion_path]).hexdigest()
    core_value['residential_line_expansion']=expansion_value
    outputs[core_path]=encoded(core_value)
    for path,raw in outputs.items():
        if check:
            if path.read_bytes()!=raw:raise ValueError('Stale network correction: '+str(path))
        else:path.write_bytes(raw)
    return report


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--design',type=Path,required=True);parser.add_argument('--check',action='store_true');a=parser.parse_args()
    result=run(a.design.resolve(),a.check)
    print(json.dumps(dict(city=result['city'],restored_shapes=len(result['restored_route_shapes']),connections=len(result['connectivity']['changes']),components=len(result['connectivity']['final_components']))))
