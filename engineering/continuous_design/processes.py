"""Mandatory process profiles and geometric production-effort measurements.

Limits are declared research hypotheses unless an existing source is named.
Unknown shop, tooling, cure and inspection evidence never becomes acceptance.
"""
from collections import defaultdict
import math

from engineering.twin_workflow import core
from . import operation_graph

PROFILES={
    'purchased-equipment':dict(source='source-bound equipment mass/envelope only',unknown=['supplier manufacturing and internal detail','mount/harness/connector interfaces','incoming inspection and commissioning']),
    'purchased-section-fastener':dict(source='modeled stock/hardware envelope',unknown=['offered section/fastener geometry and origin','stock certificates','preload, threads, finish and inspection']),
    'sheet-duct':dict(source='0.7mm steel duct research envelope; formed corners unmodeled',unknown=['seam and flange geometry','bends, stiffening and sealing','leak/pressure/fire tests']),
    'pultrusion-bond':dict(source='existing synthetic FRP material card',unknown=['die, fibre/resin processing and cure','qualified bond/interface slip','fire, fatigue and damage']),
    'profile-cut-weld':dict(minimum_wall_m=.003,stock_m=[4.,2.],maximum_plate_m=.032,
        source='engineering/generative_design/data/mechanical-detail-space.json#swift-cut-xp4000',
        unknown=['weld access and distortion','splice fatigue','finished datums and NDT','actual shop capability']),
    'machined-cut':dict(minimum_wall_m=.003,stock_m=[4.,2.],maximum_plate_m=.032,
        source='declared machining research profile; machine configuration unaccepted',
        unknown=['cutting forces','reach and clamping','surface finish','burr removal and actual setups']),
    'folded-bolted':dict(minimum_wall_m=.003,stock_m=[4.,2.],maximum_plate_m=.032,
        source='declared cold-folding research hypothesis; 2t inside radius and K=0.4, not a qualified bend procedure',
        unknown=['springback and bend coupon','press brake tooling/capacity','bolt preload and locking','fatigue and inspection access']),
    'vacuum-laminate':dict(minimum_ply_m=.00015,source='existing development material and coupled core cards',
        unknown=['resin/fibre qualification','drapability and ply drops','resin flow and cure','voids, fire and hot/wet ageing','insert and edge-closure qualification']),
    'precast-reusable':dict(cell_withdrawal_m=6.,split_core_segment_m=4.,lifting_hypothesis_kg=125000.,
        source='existing 125t research handling envelope; withdrawal distances are unaccepted layout hypotheses',
        unknown=['cage congestion and concrete access','curing and transfer strength','stressing/anchorage and erection stability','actual crane chart and site foundation']),
}


def nesting(rectangles,stock=(4.,2.),kerf=.003):
    """Conservative shelf packing; full rectangular blank area, grouped by gauge."""
    groups=defaultdict(list);placements=[];sheets=0;blank_area=0.
    for rectangle in rectangles:
        length,width,thickness=rectangle['size_m']
        if min(length,width,thickness)<=0 or not all(math.isfinite(v) for v in (length,width,thickness)):
            raise ValueError('positive finite stock rectangle required')
        groups[thickness].append(rectangle)
    failures=[]
    for thickness,items in sorted(groups.items()):
        bins=[]
        for item in sorted(items,key=lambda p:(-max(p['size_m'][:2]),p['id'])):
            length,width,_=item['size_m']
            orientations=[(length,width),(width,length)]
            feasible=[(a,b) for a,b in orientations if a<=stock[0] and b<=stock[1]]
            if not feasible:
                failures.append(item['id']);continue
            length,width=min(feasible,key=lambda pair:pair[1])
            blank_area+=length*width
            chosen=None
            for index,sheet in enumerate(bins):
                if sheet['x']+length<=stock[0] and sheet['y']+width<=stock[1] and width<=sheet['row_height']+1e-12:
                    chosen=(index,sheet);break
                if sheet['y']+sheet['row_height']+kerf+width<=stock[1]:
                    sheet.update(x=0.,y=sheet['y']+sheet['row_height']+kerf,row_height=width)
                    chosen=(index,sheet);break
            if chosen is None:
                bins.append(dict(x=0.,y=0.,row_height=width));chosen=(len(bins)-1,bins[-1])
            index,sheet=chosen
            placements.append(dict(part=item['id'],sheet=sheets+index,x_m=sheet['x'],y_m=sheet['y'],
                size_m=[length,width],thickness_m=thickness))
            sheet['x']+=length+kerf
        sheets+=len(bins)
    return dict(passed=not failures,unplaced_part_ids=failures,placements=placements,
        sheet_count=sheets,blank_area_m2=blank_area,stock_area_m2=sheets*math.prod(stock),
        rectangular_scrap_m2=sheets*math.prod(stock)-blank_area,
        kerf_m=kerf,exact_contour_nesting=False)


def physical_parts(contract):
    from engineering.design_engine.manufacturing_rules import part_bounds
    return [dict(id=p['id'],bounds_m=part_bounds(p),mass_kg=p['properties']['mass_kg']) for p in contract['parts']]


def evaluate(profile_id,*,parts=None,rectangles=None,graph=None,observations=None,part_profiles=None,contract=None,output=None):
    if profile_id not in PROFILES:
        raise ValueError('an applicable registered manufacturing process profile is mandatory')
    profile=PROFILES[profile_id];checks={};metrics={};unknown=list(profile['unknown'])
    observations=observations or {}
    dimensional=None
    if contract:
        from engineering.design_engine.manufacturing_rules import evaluate as common_rules
        dimensional=common_rules(contract)
        for entry in dimensional['checks']:
            if entry['state'] in {'passed','failed'}:
                checks['dimensional/'+entry['id']]=entry['state']=='passed'
            else:
                unknown.append('dimensional/'+entry['id'])
    if parts:
        assignments=part_profiles or {p['id']:profile_id for p in parts}
        if set(assignments)!={p['id'] for p in parts} or any(p not in PROFILES for p in assignments.values()):
            raise ValueError('every represented part requires an applicable registered process profile')
        for name in set(assignments.values()):unknown.extend(PROFILES[name]['unknown'])
    else:assignments={}
    packed=None;replay=None
    if rectangles is not None and 'stock_m' in profile:
        packed=nesting(rectangles,profile['stock_m'])
        checks['all_blanks_nested']=packed['passed']
        checks['plate_thickness']=all(r['size_m'][2]<=profile['maximum_plate_m'] for r in rectangles)
        checks['minimum_plate_gauge']=all(r['size_m'][2]>=profile['minimum_wall_m'] for r in rectangles)
        metrics.update(sheet_count=packed['sheet_count'],rectangular_scrap_m2=packed['rectangular_scrap_m2'])
        metrics['profile_cut_length_m']=sum(2*sum(r['size_m'][:2]) for r in rectangles)
    elif 'stock_m' in profile:
        unknown.append('complete developed blank nesting')
    if profile_id=='folded-bolted':
        thickness=observations.get('wall_m');radius=observations.get('inside_bend_radius_m')
        checks['declared_bend_radius']=radius is not None and thickness is not None and radius>=2*thickness
        metrics['bend_count']=observations.get('bend_count')
    if profile_id=='vacuum-laminate':
        plies=observations.get('ply_thicknesses_m',[])
        checks['ply_gauge']=bool(plies) and min(plies)>=profile['minimum_ply_m']
        checks['core_service_temperature']=observations['core_temperature_c']<=observations['core_temperature_limit_c']
        metrics['ply_placement_count']=observations.get('ply_placement_count')
    if profile_id=='precast-reusable':
        stroke=observations.get('withdrawal_m')
        if stroke is not None:checks['mould_withdrawal_layout']=stroke<=profile['cell_withdrawal_m']
        mass=observations.get('suspended_mass_kg')
        if mass is not None:checks['declared_handling_envelope']=mass<=profile['lifting_hypothesis_kg']
    if graph:
        replay=operation_graph.evaluate(graph)
        checks.update({'operations/'+k:v for k,v in replay['checks'].items()})
        metrics.update(replay['metrics']);unknown.extend(replay['unknown'])
    else:
        unknown.append('complete executable assembly/removal sequence')
    if output is not None:
        if dimensional:core.write(output/'dimensional-manufacturing.json',dimensional,exclusive=True)
        if packed:core.write(output/'blank-nesting.json',packed,exclusive=True)
        if graph:core.write(output/'operation-graph.json',graph,exclusive=True)
        if replay:core.write(output/'operation-replay.json',replay,exclusive=True)
    return dict(schema='osr-process-profile-evaluation/1',profile_id=profile_id,profile_sha256=core.digest(profile),
        source=profile['source'],checks=checks,metrics=metrics,unknown=list(dict.fromkeys(unknown)),
        part_profiles=assignments,part_coverage='all represented regions assigned; actual manufacturing-unit aggregation and process qualification remain open' if parts else 'family profile; complete physical part allocation unavailable',
        scope='Declared dimensional/process screens and conservative operation replay; no qualified manufacturing process',
        measured_cycle_time_s=None,quoted_cost=None,manufacturing_release=False)


LEGACY={
    'mechanical-detail':'profile-cut-weld','mechanical-interface':'profile-cut-weld',
    'mechanical-cleat':'machined-cut','civil-steel-beam':'profile-cut-weld',
    'civil-detail':'precast-reusable','civil-bay':'precast-reusable',
}


def attach(value,result,output):
    """Physical candidates cannot opt out; absent measurements remain explicit."""
    kind=value['kind']
    if kind not in LEGACY:
        return result
    observations={};rectangles=None
    assessment=result.get('assessment',{})
    if kind=='mechanical-detail':
        geometry=assessment['geometry']['parts'];rectangles=[]
        for part in geometry:
            if part['kind']=='box':
                sizes=sorted(part['size_m'],reverse=True)
                rectangles.append(dict(id=part['id'],size_m=sizes))
    if kind=='civil-detail':
        observations['suspended_mass_kg']=assessment.get('metrics',{}).get('suspended_mass_kg')
    profile=evaluate(LEGACY[kind],rectangles=rectangles,observations=observations,output=output)
    result['manufacturing_process']=profile
    for name,passed in profile['checks'].items():
        result['checks']['manufacturing/'+name]=passed
        if not passed:
            result.setdefault('failed_checks',[]).append('manufacturing/'+name)
            result['study_pass']=False
    return result
