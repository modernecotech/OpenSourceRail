"""Unselected straight-station / continuous-transition Baghdad hub layouts.

Quintic transitions meet retained anchor tangents and the station straight with
zero endpoint curvature. Bernstein subdivision conservatively bounds curvature.
Neither a geometric fit nor reopened solids provide engineering/site acceptance.
"""
from functools import lru_cache
from copy import deepcopy
from hashlib import sha256
from itertools import combinations,product
from pathlib import Path
import gzip
import io
import json
import math
import shutil
import subprocess
import tomllib
import zipfile

from . import interchange_hubs as hubs,configuration,hub_access

ROOT=Path(__file__).resolve().parents[2]
INPUT=Path(__file__).with_name('shared-hub-layout.toml')
TEST=ROOT/'engineering/analysis/tests/test_ferrite_maglev_shared_hub_layout.py'
OUTPUT=ROOT/'docs/design-engine/ferrite-maglev/shared-hub-layout'
SCHEMA='osr-shared-hub-layout/1'
FLAGS=dict(design_complete=False,engineering_accepted=False,physical_validation=False,
    manufacturing_release=False,physical_release=False)
BASE_FILES={'study.json.gz','geometry.json','overview.svg','station-plan.svg','README.md'}
NATIVE_FILES={'model.FCStd','model.step.gz','native-cad.json','native-mesh.json.gz','overview.png','native-visual.json'}
MAX_RAW=32*1024*1024
MAX_FILE=32*1024*1024


def encoded(value):return json.dumps(value,sort_keys=True,allow_nan=False,separators=(',',':')).encode()
def digest(path):return sha256(Path(path).read_bytes()).hexdigest()
def add(p,q):return [x+y for x,y in zip(p,q)]
def sub(p,q):return [x-y for x,y in zip(p,q)]
def mul(p,k):return [x*k for x in p]
def dot(p,q):return sum(x*y for x,y in zip(p,q))
def unit(p):
    n=math.hypot(*p)
    if n<1e-9:raise ValueError('nonzero direction required')
    return mul(p,1/n)
def normal(p):return [-p[1],p[0]]
def rotate(p,degrees):
    t=math.radians(degrees);return [p[0]*math.cos(t)-p[1]*math.sin(t),p[0]*math.sin(t)+p[1]*math.cos(t)]


def load():
    a=tomllib.loads(INPUT.read_text())
    if a['schema']!=SCHEMA or any(a[key] is not False for key in ('hub_selected','land_accepted','engineering_accepted')):
        raise ValueError('unselected unaccepted hub layout required')
    positive=('minimum_station_tangent_m','maximum_transition_detour_ratio','maximum_transition_extent_from_chord_m',
        'maximum_anchor_projection_offset_m','maximum_grade_fraction','minimum_vertical_radius_m','anchor_beam_level_m',
        'platform_floor_above_beam_m','vehicle_envelope_above_beam_m','vehicle_envelope_half_width_m','minimum_structure_clearance_m',
        'maximum_guideway_bay_m','hall_floor_m','hall_headroom_m','hall_side_m','lift_shaft_width_m','lift_shaft_depth_m',
        'stair_flight_clear_width_m','stair_centre_gap_m','minimum_platform_side_passage_m','stair_riser_max_m','stair_tread_m')
    for key in positive:hub_access.number(a[key],key)
    for key in ('platform_widths_m','minimum_horizontal_radii_m','level_spacings_m','control_handle_fractions','portal_column_offsets_m'):
        if not 1<=len(a[key])<=4:raise ValueError('bounded layout alternatives required')
        for value in a[key]:hub_access.number(value,key)
    if a['minimum_station_tangent_m']<350 or a['maximum_guideway_bay_m']>25 or a['maximum_grade_fraction']>.06:
        raise ValueError('bounded station/bay/grade assumptions required')
    if (not 1<=a['maximum_variants']<=768 or not 1<=a['maximum_representatives']<=3
            or type(a['curvature_subdivision_depth']) is not int or not 4<=a['curvature_subdivision_depth']<=14):
        raise ValueError('bounded search/subdivision required')
    if any(not .05<=v<=.4 for v in a['control_handle_fractions']):raise ValueError('bounded transition handles required')
    for key in ('heading_adjustments_deg','shared_site_east_offsets_m','lift_positions_along_platform_m','forward_power_zone_m'):
        if not 1<=len(a[key])<=4 or any(type(v) not in (int,float) or not math.isfinite(v) or abs(v)>500 for v in a[key]):
            raise ValueError('finite bounded offsets required')
    if len(a['forward_power_zone_m'])!=2 or a['forward_power_zone_m'][1]-a['forward_power_zone_m'][0]<350:
        raise ValueError('350 m directional powered zone required')
    f=configuration.selected().formation
    if (a['stop_coordinate_convention']!='front-of-leading-car-at-H-in-both-directions'
            or not math.isclose(a['directional_beam_centre_offset_from_island_edge_m'],f.cabin_width_m/2+a['platform_door_gap_m'])
            or not math.isclose(a['vehicle_envelope_half_width_m'],f.arm_width_m/2+a['vehicle_swept_allowance_per_side_m'])):
        raise ValueError('stop, cabin/door and arm-envelope configuration differs')
    return a


def source_paths():
    return sorted(set([Path(__file__),INPUT,TEST,*hubs.source_paths(),*configuration.source_paths(),Path(hub_access.__file__),hub_access.INPUT,
        ROOT/'engineering/factory_examples/native.py',
        *(hubs.OUTPUT/name for name in hubs.FILES|{'manifest.json'})]))


def sources():return {p.relative_to(ROOT).as_posix():digest(p) for p in source_paths()}


def bezier(points,t):
    values=[list(p) for p in points]
    while len(values)>1:values=[add(mul(p,1-t),mul(q,t)) for p,q in zip(values,values[1:])]
    return values[0]


def derivative(points):return [mul(sub(q,p),len(points)-1) for p,q in zip(points,points[1:])]


def split(points):
    rows=[[list(p) for p in points]]
    while len(rows[-1])>1:rows.append([mul(add(p,q),.5) for p,q in zip(rows[-1],rows[-1][1:])])
    return [row[0] for row in rows],[row[-1] for row in reversed(rows)]


def curvature(points,t):
    v=bezier(derivative(points),t);acc=bezier(derivative(derivative(points)),t);speed=math.hypot(*v)
    return abs(v[0]*acc[1]-v[1]*acc[0])/speed**3 if speed>1e-10 else float('inf')


def curvature_bound(points):
    v=derivative(points);acc=derivative(v);degree=len(v)+len(acc)-2;cross=[]
    for k in range(degree+1):
        cross.append(sum(math.comb(len(v)-1,i)*math.comb(len(acc)-1,k-i)/math.comb(degree,k)
            *(v[i][0]*acc[k-i][1]-v[i][1]*acc[k-i][0])
            for i in range(len(v)) if 0<=k-i<len(acc)))
    minima=[]
    for j in (0,1):
        lo=min(p[j] for p in v);hi=max(p[j] for p in v);minima.append(0. if lo<=0<=hi else min(abs(lo),abs(hi)))
    speed_lower=math.hypot(*minima)
    return max(map(abs,cross))/speed_lower**3 if speed_lower>1e-12 else float('inf')


def certify_curvature(points,minimum_radius,max_depth=12):
    hub_access.number(minimum_radius,'minimum radius');limit=1/minimum_radius;stack=[(points,0)];largest=0.;leaves=0
    sampled=max(curvature(points,i/100) for i in range(101))
    if not math.isfinite(sampled) or sampled>limit*(1+1e-9):
        return dict(passed=False,reason='sampled curvature exceeds minimum radius or singular speed',sampled_minimum_radius_m=1/sampled if sampled and math.isfinite(sampled) else None,
            certified_minimum_radius_m=None,subdivision_leaves=0)
    while stack:
        values,depth=stack.pop();upper=curvature_bound(values)
        if upper<=limit*(1+1e-12):largest=max(largest,upper);leaves+=1
        elif depth>=max_depth:
            return dict(passed=False,reason='curvature/speed bound unresolved at subdivision limit',sampled_minimum_radius_m=1/sampled if sampled else None,
                certified_minimum_radius_m=None,subdivision_leaves=leaves)
        else:
            first,last=split(values);stack.extend([(first,depth+1),(last,depth+1)])
    return dict(passed=True,reason='Bernstein curvature upper bound and derivative-box speed lower bound',
        sampled_minimum_radius_m=1/sampled if sampled else None,certified_minimum_radius_m=1/largest if largest else None,subdivision_leaves=leaves)


def curve_length(points):
    d=derivative(points)
    chord=sub(points[-1],points[0]);length=math.hypot(*chord)
    if length>0:
        axis=unit(chord)
        if min(dot(v,axis) for v in d)>=0 and max(abs(dot(sub(p,points[0]),normal(axis))) for p in points)<=1e-10:
            return length,0.
    def simpson(n):return sum((1 if i in (0,n) else 4 if i%2 else 2)*math.hypot(*bezier(d,i/n)) for i in range(n+1))/(3*n)
    coarse=simpson(32);fine=simpson(64);n=64
    while abs(fine-coarse)/15>1e-5 and n<2048:
        coarse=fine;n*=2;fine=simpson(n)
    return fine,abs(fine-coarse)/15


def lateral_extent_bound(points,origin,direction,depth=5):
    values=[points]
    for _ in range(depth):values=[piece for curve in values for piece in split(curve)]
    return max(abs(dot(sub(p,origin),normal(direction))) for curve in values for p in curve)


def _transition(first,last,heading_first,heading_last,minimum_radius,a):
    chord=sub(last,first);length=math.hypot(*chord)
    if length<50:return dict(passed=False,reason='insufficient transition extent',alternatives=[])
    direction=unit(chord);options=[]
    for fraction in a['control_handle_fractions']:
        handle=length*fraction
        poles=[first,add(first,mul(heading_first,handle)),add(first,mul(heading_first,2*handle)),
            sub(last,mul(heading_last,2*handle)),sub(last,mul(heading_last,handle)),last]
        # Forward control-polygon derivatives exclude loops/backtracking. This
        # conservative screen can reject a fit that a wider search could find.
        monotone=min(dot(v,direction) for v in derivative(poles))>=-1e-8
        lateral=lateral_extent_bound(poles,first,direction)
        bounds=certify_curvature(poles,minimum_radius,a['curvature_subdivision_depth']) if monotone else dict(passed=False,reason='nonmonotone transition control polygon',certified_minimum_radius_m=None)
        actual,error=curve_length(poles) if bounds['passed'] else (None,None)
        passed=bool(bounds['passed'] and lateral<=a['maximum_transition_extent_from_chord_m'] and actual<=length*a['maximum_transition_detour_ratio'])
        options.append(dict(handle_fraction=fraction,control_points_xy_m=poles,chord_m=length,length_m=actual,length_integration_error_estimate_m=error,
            control_hull_max_lateral_extent_m=lateral,forward_monotone=monotone,curvature=bounds,passed=passed))
    candidates=[v for v in options if v['passed']]
    return dict(passed=bool(candidates),reason='bounded tangent/zero-curvature transition fit' if candidates else 'no bounded handle/radius/extent fit',
        selected=min(candidates,key=lambda r:(r['length_m'],r['handle_fraction'])) if candidates else None,alternatives=options)


@lru_cache(maxsize=2048)
def _transition_cached(identity):return encoded(_transition(*json.loads(identity)))


def transition(first,last,heading_first,heading_last,minimum_radius,a):
    policy={key:a[key] for key in ('control_handle_fractions','curvature_subdivision_depth','maximum_transition_extent_from_chord_m','maximum_transition_detour_ratio')}
    return json.loads(_transition_cached(encoded([first,last,heading_first,heading_last,minimum_radius,policy]).decode()))


def project(point,origin):
    return [math.radians(point[0]-origin[0])*hubs.op.EARTH_M*math.cos(math.radians(origin[1])),math.radians(point[1]-origin[1])*hubs.op.EARTH_M]


def anchor_context(concept):
    design=json.loads((hubs.CITY_ROOT/'city.json').read_text());features=json.loads((hubs.CITY_ROOT/'baghdad.corridor.geojson').read_text())['features']
    lines={r['name']:r for r in design['lines']};values={}
    for proposal in concept['line_proposals']:
        path=hubs.op.route_path(features,lines[proposal['line']]);ends=[]
        for index,p in enumerate((proposal['local_chord_coordinates'][0],proposal['local_chord_coordinates'][-1])):
            projection=hubs.op.project_crossing(path,*p);s=projection['s_m'];ds=-20. if index==0 else 20.
            sample=max(0.,min(path['length_m'],s+ds));q=hubs.op.point_at(path,s);r=hubs.op.point_at(path,sample)
            if abs(sample-s)<1e-7:
                sample=max(0.,min(path['length_m'],s-ds));r=hubs.op.point_at(path,sample)
                vector=sub(project([r['lon'],r['lat']],p),project([q['lon'],q['lat']],p))
                if index==1:vector=mul(vector,-1.)
            else:
                vector=sub(project([q['lon'],q['lat']],p),project([r['lon'],r['lat']],p)) if index==0 else sub(project([r['lon'],r['lat']],p),project([q['lon'],q['lat']],p))
            ends.append(dict(coordinate=p,heading=unit(vector),projection_offset_m=projection['crossing_projection_offset_m'],
                projected_coordinate=[q['lon'],q['lat']],projected_chainage_m=s))
        values[proposal['line']]=ends
    return values


def projected_anchor_repair(concept,context,a):
    if not any(row['projection_offset_m']>a['maximum_anchor_projection_offset_m'] for rows in context.values() for row in rows):return None
    repaired=deepcopy(concept);repaired['id']=concept['id']+'/projected-anchors';repaired['anchor_mode']='projected-repair'
    changed_context=deepcopy(context);records=[]
    for proposal in repaired['line_proposals']:
        for index,slot in ((0,0),(1,-1)):
            original=context[proposal['line']][index];point=original['projected_coordinate'];old=proposal['local_chord_coordinates'][slot]
            proposal['local_chord_coordinates'][slot]=point
            records.append(dict(line=proposal['line'],end='before' if index==0 else 'after',original_coordinate=old,
                projected_coordinate=point,exact_retained_polyline_chainage_m=original['projected_chainage_m'],
                displacement_m=hubs.op.distance(old,point),source_projection_offset_m=original['projection_offset_m'],
                source_control_exceeded_5m_limit=original['projection_offset_m']>a['maximum_anchor_projection_offset_m'],
                connection_and_access_site_accepted=False))
            changed_context[proposal['line']][index].update(coordinate=point,projection_offset_m=0.,original_source_coordinate=old)
    repaired['anchor_repair_provenance']=dict(source_concept_id=concept['id'],records=records,
        rejected_original_retained=True,projection_limit_relaxed=False,old_civil_cost_reused=False,
        changed_connections_and_source_access_require_acceptance=True)
    return repaired,changed_context


def fit_line(proposal,anchors,origin,centre,heading_adjustment,radius,level,a):
    first,last=[project(p,origin) for p in (proposal['local_chord_coordinates'][0],proposal['local_chord_coordinates'][-1])]
    if math.dist(first,last)<1. or proposal['previous_retained_anchor_id']==proposal['next_retained_anchor_id']:
        return dict(line=proposal['line'],passed=False,reason='coincident before/after anchors; through-line would double back',source_anchor_ids=[proposal['previous_retained_anchor_id'],proposal['next_retained_anchor_id']])
    if max(row['projection_offset_m'] for row in anchors)>a['maximum_anchor_projection_offset_m']:
        return dict(line=proposal['line'],passed=False,reason='retained anchor lies outside allowed source alignment projection offset')
    try:heading=rotate(unit(add(unit(sub(centre,first)),unit(sub(last,centre)))),heading_adjustment)
    except ValueError:return dict(line=proposal['line'],passed=False,reason='opposed station approach chords')
    powered=a['forward_power_zone_m'];lo=min(powered[0],-powered[1],-a['minimum_station_tangent_m']/2);hi=max(powered[1],-powered[0],a['minimum_station_tangent_m']/2)
    start=add(centre,mul(heading,lo));end=add(centre,mul(heading,hi))
    if dot(sub(start,first),heading)<=0 or dot(sub(last,end),heading)<=0:return dict(line=proposal['line'],passed=False,reason='anchor extent cannot contain station straight without reversal')
    width=a['_variant_platform_width_m'];f=configuration.selected().formation
    station_offset=width/2+f.cabin_width_m/2+a['platform_door_gap_m'];ordinary_offset=a['ordinary_directional_beam_centres_m']/2
    beams=[];failures=[]
    for side in (-1,1):
        anchor_first=add(first,mul(normal(anchors[0]['heading']),side*ordinary_offset));anchor_last=add(last,mul(normal(anchors[1]['heading']),side*ordinary_offset))
        station_start=add(start,mul(normal(heading),side*station_offset));station_end=add(end,mul(normal(heading),side*station_offset))
        incoming=transition(anchor_first,station_start,anchors[0]['heading'],heading,radius,a)
        outgoing=transition(station_end,anchor_last,heading,anchors[1]['heading'],radius,a)
        if not incoming['passed'] or not outgoing['passed']:
            failures.append(dict(side=side,incoming=incoming,outgoing=outgoing));continue
        beams.append(dict(id=proposal['line']+'-beam-'+str(side),side=side,ordinary_offset_m=ordinary_offset,station_offset_m=station_offset,
            station_start_xy_m=station_start,station_end_xy_m=station_end,
            incoming=incoming['selected'],outgoing=outgoing['selected'],flared_transition_geometry_fitted=True,
            length_m=incoming['selected']['length_m']+outgoing['selected']['length_m']+hi-lo))
    if failures:return dict(line=proposal['line'],passed=False,reason='directional beam flaring / transition / radius / extent screen',beam_failures=failures)
    lengths=[beam[side]['length_m'] for beam in beams for side in ('incoming','outgoing')];delta=level-a['anchor_beam_level_m']
    grade=max(1.875*abs(delta)/length for length in lengths);vertical=max(5.773502691896258*abs(delta)/length**2 for length in lengths)
    passed=grade<=a['maximum_grade_fraction'] and vertical<=1/a['minimum_vertical_radius_m']
    return dict(line=proposal['line'],passed=passed,reason='fit research screens' if passed else 'vertical grade/radius screen',heading_xy=heading,
        station_centre_xy_m=centre,station_tangent_start_xy_m=start,station_tangent_end_xy_m=end,
        station_tangent_bounds_m=[lo,hi],station_tangent_length_m=hi-lo,beam_top_level_m=level,
        platform_floor_level_m=level+a['platform_floor_above_beam_m'],forward_power_zone_m=powered,reverse_power_zone_m=[-powered[1],-powered[0]],
        directional_beams=beams,station_beam_centres_m=2*station_offset,ordinary_beam_centres_m=2*ordinary_offset,
        platform_door_gap_m=a['platform_door_gap_m'],arm_envelope_half_width_m=f.arm_width_m/2,
        arm_under_platform_vertical_clearance_accepted=False,maximum_grade_bound=grade,
        vertical_curvature_upper_bound_m_inv=vertical,minimum_vertical_radius_bound_m=1/vertical if vertical else None,
        reference_anchor_beam_levels_are_assumed=True,
        vertical_profile=dict(parameter='horizontal arc length fraction u on each approach',smoothstep='10*u**3-15*u**4+6*u**5',
            incoming_levels_m=[a['anchor_beam_level_m'],level],outgoing_levels_m=[level,a['anchor_beam_level_m']],
            zero_endpoint_grade_and_vertical_curvature=True,profile_is_design_hypothesis=True),
        new_local_physical_beam_length_m=sum(beam['length_m'] for beam in beams),retained_local_route_m=proposal['retained_local_polyline_length_m'],
        inherited_civil_price_or_classification_reused=False,approved_operating_speed_m_s=None,
        reference_curve_speed_cap_m_s=math.sqrt(.7*radius),
        speed_scope='Assumed0.7m/s2 lateral acceleration; no coast/force/energy/comfort proof',**FLAGS)


def station_portals(lines,width,a):
    """Place actual columns outside every lower station envelope."""
    result=[];rejects=[];searches=[];margin=a['portal_column_width_m']/2+a['minimum_structure_clearance_m'];depth=configuration.selected().civil.depth_m
    for i,line in enumerate(lines):
        heading=line['heading_xy'];n=normal(heading);centre=line['station_centre_xy_m'];lo,hi=line['station_tangent_bounds_m']
        count=math.ceil((hi-lo)/(a['maximum_guideway_bay_m']/5));marks=[lo+(hi-lo)*k/count for k in range(count+1)];feasible={}
        for k,s in enumerate(marks):
            axis=add(centre,mul(heading,s));columns=[]
            for side in (-1,1):
                found=None
                for offset in a['portal_column_offsets_m']:
                    point=add(axis,mul(n,side*offset));clear=True
                    own_half=width/2+a['directional_beam_centre_offset_from_island_edge_m']+a['vehicle_envelope_half_width_m']
                    if offset<own_half+margin:continue
                    for lower in lines[:i]:
                        d=sub(point,lower['station_centre_xy_m']);x=dot(d,lower['heading_xy']);y=dot(d,normal(lower['heading_xy']))
                        track=width/2+a['directional_beam_centre_offset_from_island_edge_m']
                        if lower['station_tangent_bounds_m'][0]-margin<=x<=lower['station_tangent_bounds_m'][1]+margin and min(abs(y-track),abs(y+track))<=a['vehicle_envelope_half_width_m']+margin:clear=False;break
                    for previous in result:
                        p,q=[v['xy_m'] for v in previous['column_points']];cap_centre=mul(add(p,q),.5);delta=sub(point,cap_centre)
                        if abs(dot(delta,previous['heading_xy']))<=a['portal_cap_width_m']/2+margin and abs(dot(delta,normal(previous['heading_xy'])))<=previous['cap_span_m']/2+margin:
                            clear=False;break
                    if clear:found=dict(xy_m=point,side=side,offset_m=offset);break
                if found is None:continue
                columns.append(found)
            if len(columns)==2:feasible[s]=dict(id=line['line']+'-portal-grid-'+str(k+1),line=line['line'],s_m=s,heading_xy=heading,
                centre_xy_m=axis,column_points=columns,column_top_level_m=line['beam_top_level_m']-depth-a['portal_cap_depth_m'],
                cap_top_level_m=line['beam_top_level_m']-depth,
                cap_span_m=sum(row['offset_m'] for row in columns),structural_capacity_accepted=False)
        costs={lo:0} if lo in feasible else {};previous={}
        for s in sorted(feasible):
            options=[p for p in costs if 1e-7<s-p<=a['maximum_guideway_bay_m']+1e-7]
            if options:
                p=min(options,key=lambda x:(costs[x],x));costs[s]=costs[p]+1;previous[s]=p
        searches.append(dict(line=line['line'],grid_points=len(marks),feasible_points=len(feasible),maximum_span_m=a['maximum_guideway_bay_m']))
        if hi not in costs:
            rejects.append(dict(line=line['line'],reason='no complete portal support path within25m bays and bounded column offsets',
                infeasible_chainages_m=[s for s in marks if s not in feasible]));continue
        chosen=[hi]
        while chosen[-1]!=lo:chosen.append(previous[chosen[-1]])
        result.extend(feasible[s] for s in reversed(chosen))
    return dict(portals=result,rejections=rejects,support_grid_searches=searches,passed=not rejects,
        columns_checked_against_lower_moving_train_bands_and_caps=True,
        lower_platform_column_obstacles_must_be_routed_and_cut=True,transition_pier_interference_qualified=False)


def body_and_doors(line,width,a):
    f=configuration.selected().formation;heading=line['heading_xy'];n=normal(heading);centre=line['station_centre_xy_m'];bodies=[];doors=[]
    for direction in (1,-1):
        for car in range(f.cars):
            along=-f.body_length_m/2-car*(f.body_length_m+f.coupling_gap_assumption_m)
            bodies.append(dict(direction=direction,car=car+1,body_centre_along_m=direction*along,
                body_extent_along_m=sorted([direction*(along-f.body_length_m/2),direction*(along+f.body_length_m/2)])))
            for j,offset in enumerate(f.doors_per_side_x_m):
                s=direction*(along+offset);point=add(add(centre,mul(heading,s)),mul(n,direction*width/2))
                doors.append(dict(id=line['line']+f'-d{direction}-car{car+1}-door{j+1}',direction=direction,car=car+1,
                    body_local_door_m=offset,along_m=s,platform_edge_xyz_m=[*point,line['platform_floor_level_m']]))
    return dict(stop_coordinate_convention=a['stop_coordinate_convention'],front_stop_along_m=0.,formation_length_m=f.assumed_overall_length_m,
        body_intervals=bodies,doors=doors,platform_bounds_along_m=[-f.assumed_overall_length_m-a['platform_stopping_allowance_m']/2,
            f.assumed_overall_length_m+a['platform_stopping_allowance_m']/2],platform_length_m=2*f.assumed_overall_length_m+a['platform_stopping_allowance_m'])


def rect_segment_clear(p,q,rectangle):
    """Allow boundary tangencies, reject a positive-length open-interior crossing."""
    low,high=rectangle;lo=0.;hi=1.
    for j in (0,1):
        delta=q[j]-p[j]
        if abs(delta)<1e-12:
            if not low[j]+1e-8<p[j]<high[j]-1e-8:return True
            continue
        first=(low[j]+1e-8-p[j])/delta;last=(high[j]-1e-8-p[j])/delta
        lo=max(lo,min(first,last));hi=min(hi,max(first,last))
    return not lo<hi-1e-10


def visibility_path(first,last,obstacles,inside):
    if not inside(first) or not inside(last):return None
    vertices=[first,last]
    for low,high in obstacles:
        vertices.extend(p for p in ([low[0],low[1]],[low[0],high[1]],[high[0],low[1]],[high[0],high[1]]) if inside(p))
    vertices=[list(p) for p in dict.fromkeys(tuple(p) for p in vertices)]
    graph={i:[] for i in range(len(vertices))}
    for i,j in combinations(range(len(vertices)),2):
        if all(rect_segment_clear(vertices[i],vertices[j],rect) for rect in obstacles):
            length=math.dist(vertices[i],vertices[j]);graph[i].append((j,length));graph[j].append((i,length))
    import heapq
    distances={0:0.};previous={};todo=[(0.,0)]
    while todo:
        distance,node=heapq.heappop(todo)
        if distance!=distances.get(node):continue
        if node==1:break
        for target,length in graph[node]:
            value=distance+length
            if value<distances.get(target,float('inf')):distances[target]=value;previous[target]=node;heapq.heappush(todo,(value,target))
    if 1 not in distances:return None
    indices=[1]
    while indices[-1]!=0:indices.append(previous[indices[-1]])
    return dict(points_xy_m=[vertices[i] for i in reversed(indices)],length_m=distances[1])


def rectangle_platform_overlap_area(rectangle,centre,heading,length,width):
    low,high=rectangle;n=normal(heading)
    points=[[dot(sub([x,y],centre),heading),dot(sub([x,y],centre),n)] for x,y in
        [(low[0],low[1]),(high[0],low[1]),(high[0],high[1]),(low[0],high[1])]]
    for axis,bound,sign in ((0,-length/2,1),(0,length/2,-1),(1,-width/2,1),(1,width/2,-1)):
        result=[]
        for first,last in zip(points,points[1:]+points[:1]):
            inside_first=(first[axis]-bound)*sign>=0;inside_last=(last[axis]-bound)*sign>=0
            if inside_first:result.append(first)
            if inside_first!=inside_last:
                t=(bound-first[axis])/(last[axis]-first[axis]);result.append(add(first,mul(sub(last,first),t)))
        points=result
        if not points:return 0.
    return abs(sum(p[0]*q[1]-p[1]*q[0] for p,q in zip(points,points[1:]+points[:1])))/2


def stair_geometry(flights,a,centre):
    """Connected tread/landing stock and a traversable stepped centreline."""
    maximum_run=max(flight['run_m'] for flight in flights);width=a['stair_flight_clear_width_m'];gap=a['stair_centre_gap_m']
    total_width=2*width+gap;pieces=[];paths=[]
    for i,flight in enumerate(flights):
        sign=1 if i%2==0 else -1;y=centre[1]-total_width+(width/2 if i%2==0 else width+gap+width/2)
        start=centre[0]-sign*maximum_run/2;end=start+sign*flight['run_m'];path=[[start,y,flight['from_level_m']]];treads=[]
        for j in range(flight['treads']):
            x0=start+sign*j*a['stair_tread_m'];x1=x0+sign*a['stair_tread_m'];top=flight['from_level_m']+(j+1)*flight['riser_m']
            identity=f'stair-flight-{i+1}-tread-{j+1}';treads.append(identity)
            pieces.append(dict(id=identity,size_m=[a['stair_tread_m'],width,.15],xy_m=[(x0+x1)/2,y],bottom_m=top-.15,top_m=top,kind='tread'))
            path.extend([[x0,y,top],[x1,y,top]])
        path.append([end,y,flight['to_level_m']])
        outer=centre[0]+sign*(maximum_run/2+a['stair_landing_length_m']);boundary=centre[0]+sign*maximum_run/2
        landing=dict(id='stair-flight-'+str(i+1)+'-landing',size_m=[abs(outer-end),total_width,.15],xy_m=[(outer+end)/2,centre[1]-total_width/2],
            bottom_m=flight['to_level_m']-.15,top_m=flight['to_level_m'],kind='landing',extra_connection_length_m=max(0.,maximum_run-flight['run_m']))
        pieces.append(landing)
        next_y=centre[1]-total_width+(width+gap+width/2 if i%2==0 else width/2)
        path.extend([[boundary,y,flight['to_level_m']],[boundary,next_y,flight['to_level_m']]])
        if i==len(flights)-1:path.append([outer,next_y,flight['to_level_m']])
        paths.append(dict(flight=i+1,tread_ids=treads,landing_id=landing['id'],walking_path_xyz_m=path,
            platform_landing_exit_xyz_m=[outer,y,flight['to_level_m']],actual_run_m=flight['run_m'],landing_extra_length_m=landing['extra_connection_length_m']))
    connected=all(math.dist(p['walking_path_xyz_m'][-1],q['walking_path_xyz_m'][0])<1e-8 for p,q in zip(paths,paths[1:]))
    return dict(units=pieces,flights=paths,maximum_run_m=maximum_run,total_width_m=total_width,
        total_concrete_stock_m3=sum(math.prod(p['size_m']) for p in pieces),
        all_flights_have_connected_landings=connected,structural_connections_and_headroom_accepted=False)


def circulation(lines,width,a,*,door_details=False,portals=None):
    centre=lines[0]['station_centre_xy_m'];half=a['hall_side_m']/2;passage=a['minimum_platform_side_passage_m'];clearance=passage/2
    levels=[a['hall_floor_m'],*[line['platform_floor_level_m'] for line in lines]];stairs=[];z=levels[0]
    for top in levels[1:]:
        rise=top-z;risers=math.ceil(rise/a['stair_riser_max_m']);flights=math.ceil(risers/a['maximum_risers_per_flight']);riser=rise/risers
        for i in range(flights):
            count=risers//flights+(i<risers%flights);stairs.append(dict(from_level_m=z,to_level_m=z+count*riser,risers=count,
                riser_m=riser,treads=count-1,run_m=(count-1)*a['stair_tread_m'],clear_width_m=a['stair_flight_clear_width_m']))
            z+=count*riser
    stair_length=max(row['run_m'] for row in stairs)+2*a['stair_landing_length_m'];stair_width=2*a['stair_flight_clear_width_m']+a['stair_centre_gap_m']
    stair_rect=[[-stair_length/2,-stair_width],[stair_length/2,0.]]
    lift_rects=[[[x-1.5,2.45],[x+1.5,5.05]] for x in (-1.75,1.75)]
    rectangles=[stair_rect,*lift_rects];obstacles=[[[centre[j]+lo[j]-clearance for j in (0,1)],
        [centre[j]+hi[j]+clearance for j in (0,1)]] for lo,hi in rectangles]
    entries={}
    for i,(lo,hi) in enumerate(lift_rects):
        entries['shared-lift-'+str(i+1)]=[[centre[0]+(lo[0]+hi[0])/2,centre[1]+y] for y in (lo[1]-clearance,hi[1]+clearance)]
    interfaces=[];route_lookup={};all_routed=True;minimum_side=float('inf');column_rects={}
    for line in lines:
        record=body_and_doors(line,width,a);heading=line['heading_xy'];n=normal(heading);lo,hi=record['platform_bounds_along_m']
        projection=max(abs(dot(sub([x,y],centre),n)) for low,high in obstacles for x,y in product((low[0],high[0]),(low[1],high[1])))
        minimum_side=min(minimum_side,width/2-projection+clearance)
        def inside(p):
            d=sub(p,centre);return lo+clearance-1e-8<=dot(d,heading)<=hi-clearance+1e-8 and abs(dot(d,n))<=width/2-clearance+1e-8
        columns=[]
        for portal in (portals or []):
            if portal['column_top_level_m']<=line['platform_floor_level_m']:continue
            for column in portal['column_points']:
                point=column['xy_m'];half_column=a['portal_column_width_m']/2
                rect=[[point[j]-half_column for j in (0,1)],[point[j]+half_column for j in (0,1)]]
                if rectangle_platform_overlap_area(rect,centre,heading,hi-lo,width)>1e-8:columns.append(rect)
        column_rects[line['line']]=columns
        floor_obstacles=obstacles+[[[low[j]-clearance for j in (0,1)],[high[j]+clearance for j in (0,1)]] for low,high in columns]
        for door in record['doors']:
            edge=door['platform_edge_xyz_m'][:2];start=sub(edge,mul(n,door['direction']*clearance));options={}
            for lift,points in entries.items():
                candidates=[v for end in points if (v:=visibility_path(start,end,floor_obstacles,inside)) is not None]
                if candidates:
                    best=min(candidates,key=lambda row:(row['length_m'],row['points_xy_m']));options[lift]=dict(best,
                        length_m=best['length_m']+2*clearance,door_edge_ingress_m=clearance,lift_entry_ingress_m=clearance,
                        physical_entry_xy_m=best['points_xy_m'][-1])
            route_lookup[door['id']]=options;all_routed=all_routed and bool(options)
        interfaces.append(dict(line=line['line'],heading_xy=heading,platform_level_m=line['platform_floor_level_m'],**record))
    pairs=[]
    for first,last in combinations(interfaces,2):
        rows=[]
        for door_a,door_b in product(first['doors'],last['doors']):
            candidates=[]
            for lift in sorted(set(route_lookup[door_a['id']])&set(route_lookup[door_b['id']])):
                p=route_lookup[door_a['id']][lift];q=route_lookup[door_b['id']][lift]
                candidates.append(dict(lift=lift,horizontal_walk_m=p['length_m']+q['length_m'],
                    vertical_lift_travel_m=abs(first['platform_level_m']-last['platform_level_m']),
                    from_floor_path=p,to_floor_path=q))
            if not candidates:all_routed=False;continue
            best=min(candidates,key=lambda row:(row['horizontal_walk_m'],row['lift']));rows.append(dict(from_door=door_a['id'],to_door=door_b['id'],**best))
        minimum=min(rows,key=lambda row:(row['horizontal_walk_m'],row['from_door'],row['to_door'])) if rows else None
        maximum=max(rows,key=lambda row:(row['horizontal_walk_m'],row['from_door'],row['to_door'])) if rows else None
        pairs.append(dict(from_line=first['line'],to_line=last['line'],required_door_pairs=len(first['doors'])*len(last['doors']),routed_door_pairs=len(rows),
            minimum_horizontal_walk_m=minimum['horizontal_walk_m'] if minimum else None,maximum_horizontal_walk_m=maximum['horizontal_walk_m'] if maximum else None,
            shortest_door_route=minimum,longest_door_route=maximum,door_pair_routes=rows if door_details else None,
            lift_time_at_assumed_1m_s=abs(first['platform_level_m']-last['platform_level_m']),lift_queues_door_opening_and_service_wait_s=None,
            stair_vertical_rise_m=abs(first['platform_level_m']-last['platform_level_m']),
            via_ground_hall_vertical_lift_travel_m=first['platform_level_m']+last['platform_level_m']-2*a['hall_floor_m'],
            accessible_route_accepted=False))
    core_corners=[[centre[0]+x,centre[1]+y] for lo,hi in rectangles for x,y in product((lo[0],hi[0]),(lo[1],hi[1]))]
    return dict(platform_interfaces=interfaces,platform_pair_walks=pairs,shared_lifts=2,lift_stop_levels_m=levels,
        stair_geometry=stair_geometry(stairs,a,centre),
        common_core_rectangles_xy_m=[[[centre[j]+value[j] for j in (0,1)] for value in rect] for rect in rectangles],
        floor_column_obstacles_by_line=column_rects,
        shaft_and_stair_obstacles_inflated_for_half_passage_m=clearance,minimum_side_passage_m=minimum_side,
        platform_bypass_screen_pass=minimum_side>=passage-1e-8,all_boarding_door_pairs_routed=all_routed,
        stair_flights=stairs,stair_core_length_m=stair_length,stair_core_width_m=stair_width,
        minimum_repeated_flight_headroom_reference_m=min(row['to_level_m']-row['from_level_m'] for row in stairs)*2-a['platform_slab_m'],
        stair_headroom_accepted=False,hall_bounds_xyz_m=[[centre[0]-half,centre[1]-half,a['hall_floor_m']],
            [centre[0]+half,centre[1]+half,a['hall_floor_m']+a['hall_headroom_m']]],hall_deck_area_m2=a['hall_side_m']**2,
        core_within_hall_screen_pass=all(abs(p[j]-centre[j])<=half-clearance for p in core_corners for j in (0,1)),
        floor_path_scope='Visibility paths inside oriented platform boundaries, avoiding inflated shared lift/stair footprints; finite passage and door ingress included. Direct shared multi-stop lift routes; hall descent is a separately stated alternative.',
        common_lift_capacity_outage_fire_power_and_platform_interfaces_accepted=False,**FLAGS)


def layout(concept,anchors,heading,offset,radius,gap,width,a,*,details=False):
    origin=concept['shared_hub_coordinate'];centre=[offset,0.];values=[];settings=dict(a,_variant_platform_width_m=width)
    for i,proposal in enumerate(concept['line_proposals']):
        values.append(fit_line(proposal,anchors[proposal['line']],origin,centre,heading,radius,a['anchor_beam_level_m']+i*gap,settings))
    holds=[row['line']+': '+row['reason'] for row in values if not row['passed']]
    mode=concept.get('anchor_mode','source-exact')
    identity=f'{concept["pair_id"]}/anchors-{mode}/heading{heading:g}/east{offset:g}/radius{radius:g}/gap{gap:g}/island{width:g}'
    result=dict(id=identity,pair_id=concept['pair_id'],source_concept_id=concept['id'],source_hub_coordinate=origin,
        heading_adjustment_deg=heading,shared_site_east_offset_m=offset,minimum_directional_beam_radius_m=radius,
        anchor_mode=mode,anchor_repair_provenance=concept.get('anchor_repair_provenance'),
        level_spacing_m=gap,platform_island_width_m=width,lines=values,selected=False,geometry_holds=holds,
        terminal_extension_and_unswitched_return_loop_implemented=False,train_routing_switches=0,
        source_platform_records_preserved=True,source_platform_boarding_continuity_preserved=False,**FLAGS)
    if holds:
        result.update(geometric_research_screen_pass=False,screen='rejected-or-unimplemented-through-layout');return result
    cv=configuration.selected().civil
    clearance=gap-cv.depth_m-a['portal_cap_depth_m']-a['vehicle_envelope_above_beam_m']
    if clearance<a['minimum_structure_clearance_m']:holds.append('upper portal cap / lower vehicle envelope vertical clearance')
    hall_clearance=a['anchor_beam_level_m']-cv.depth_m-(a['hall_floor_m']+a['hall_headroom_m'])
    if hall_clearance<a['minimum_structure_clearance_m']:holds.append('lower beam underside / hall headroom clearance')
    portal=station_portals(values,width,a)
    if not portal['passed']:holds.append('bounded portal column placement interferes with lower station envelopes')
    access=circulation(values,width,a,door_details=details,portals=portal['portals']) if width>=10 else None
    if access is None or not access['platform_bypass_screen_pass']:holds.append('platform width cannot contain common core with adopted side passage')
    if access and not access['all_boarding_door_pairs_routed']:holds.append('not all exact boarding-door pairs have a clear floor/lift route')
    if access and not access['core_within_hall_screen_pass']:holds.append('common core exceeds hall bounds')
    platform_length=2*configuration.selected().formation.assumed_overall_length_m+a['platform_stopping_allowance_m']
    station_bays=sum(max(0,len([p for p in portal['portals'] if p['line']==line['line']])-1)*2 for line in values)
    whole_beam_bays=sum(math.ceil(beam['length_m']/a['maximum_guideway_bay_m']) for line in values for beam in line['directional_beams'])
    quantities=dict(new_physical_directional_guideway_m=sum(line['new_local_physical_beam_length_m'] for line in values),
        station_straight_directional_beam_m=sum(line['station_tangent_length_m']*2 for line in values),
        station_guideway_bays=station_bays,whole_local_route_beam_bay_lower_bound=whole_beam_bays,
        transition_supports_individually_located=False,curved_and_graded_beam_detail_accepted=False,
        platform_count=len(values),platform_length_m=platform_length,platform_area_m2=len(values)*platform_length*width,
        platform_concrete_m3=len(values)*platform_length*width*a['platform_slab_m'],
        station_portals=len(portal['portals']),station_columns=2*len(portal['portals']),
        portal_cap_concrete_m3=sum(row['cap_span_m']*a['portal_cap_depth_m']*a['portal_cap_width_m'] for row in portal['portals']),
        station_column_concrete_m3=sum(2*row['column_top_level_m']*a['portal_column_width_m']**2 for row in portal['portals']),
        hall_deck_m2=a['hall_side_m']**2,hall_concrete_m3=a['hall_side_m']**2*a['hall_slab_m'],
        shared_multistop_lifts=2,shared_stair_core=1,
        old_civil_price_or_foundation_credit_usd=0.,complete_installed_cost_usd=None,
        material_mass_complete=False,ground_foundations_and_earthquake_design_accepted=False)
    if access:
        void_area=sum((hi[0]-lo[0])*(hi[1]-lo[1]) for lo,hi in access['common_core_rectangles_xy_m'])
        column_void=sum(rectangle_platform_overlap_area(rect,line['station_centre_xy_m'],line['heading_xy'],platform_length,width)
            for line in values for rect in access['floor_column_obstacles_by_line'][line['line']])
        quantities.update(platform_core_openings_area_m2=len(values)*void_area,
            platform_column_openings_area_m2=column_void,
            platform_net_slab_concrete_m3=(len(values)*(platform_length*width-void_area)-column_void)*a['platform_slab_m'],
            platform_slab_gross_quantity_is_not_net_material=True)
        quantities['stair_tread_and_landing_concrete_m3']=access['stair_geometry']['total_concrete_stock_m3']
    result.update(station_vertical_cap_to_lower_vehicle_clearance_m=clearance,hall_to_lower_beam_clearance_m=hall_clearance,
        portal_layout=portal,circulation=access,quantities=quantities,geometric_research_screen_pass=not holds,
        screen='bounded-geometric-fit; external and detailed engineering gates open' if not holds else 'rejected geometric/access screen',
        route_dynamic_clearance_outside_station_not_qualified=True,
        complete_cost_and_passenger_capacity_unqualified=True)
    return result


def brief(row):
    value={key:row[key] for key in ('id','pair_id','anchor_mode','anchor_repair_provenance','heading_adjustment_deg','shared_site_east_offset_m','minimum_directional_beam_radius_m',
        'level_spacing_m','platform_island_width_m','geometry_holds','geometric_research_screen_pass','selected','screen')}
    value['line_screens']=[dict(line=line['line'],passed=line['passed'],reason=line['reason']) for line in row['lines']]
    if row.get('quantities'):value['quantities']=row['quantities']
    if row.get('circulation'):
        value['transfer_walk_ranges']=[{key:p[key] for key in ('from_line','to_line','required_door_pairs','routed_door_pairs','minimum_horizontal_walk_m','maximum_horizontal_walk_m','lift_time_at_assumed_1m_s')} for p in row['circulation']['platform_pair_walks']]
    return value


@lru_cache(maxsize=2)
def _study(identity):
    a=load();before=json.loads(identity);hubs.verify();upstream=hubs.study();rows=[];representatives=[]
    concepts=upstream['coordinated_realignment_concepts'];cases=[]
    for concept in concepts:
        context=anchor_context(concept);cases.append((concept,context));repair=projected_anchor_repair(concept,context,a)
        if repair is not None:cases.append(repair)
    count=len(cases)*math.prod(len(a[key]) for key in ('heading_adjustments_deg','shared_site_east_offsets_m','minimum_horizontal_radii_m','level_spacings_m','platform_widths_m'))
    if count>a['maximum_variants']:raise ValueError('shared layout alternatives exceed bounded search')
    for concept,context in cases:
        best=None
        for heading,offset,radius,width,gap in product(a['heading_adjustments_deg'],a['shared_site_east_offsets_m'],a['minimum_horizontal_radii_m'],a['platform_widths_m'],a['level_spacings_m']):
            row=layout(concept,context,heading,offset,radius,gap,width,a);rows.append(brief(row))
            if row['geometric_research_screen_pass'] and (best is None or (row['quantities']['new_physical_directional_guideway_m'],row['id'])<(best['quantities']['new_physical_directional_guideway_m'],best['id'])):best=row
        if best is not None:representatives.append(best)
    representatives=sorted(representatives,key=lambda row:(row['quantities']['new_physical_directional_guideway_m'],row['id']))[:a['maximum_representatives']]
    # Retain every exact door-pair path for bounded representatives. Summaries
    # for the complete finite search carry only extrema and route counts.
    for row in representatives:
        row['circulation']=circulation(row['lines'],row['platform_island_width_m'],a,door_details=True,portals=row['portal_layout']['portals'])
    if before!=sources():raise ValueError('shared hub sources changed during bounded calculation')
    formation=configuration.selected().formation;zone=a['forward_power_zone_m']
    result=dict(schema=SCHEMA,source_sha256=before,upstream_content_sha256=upstream['content_sha256'],assumptions=a,
        stop_convention=dict(name=a['stop_coordinate_convention'],formation_length_m=formation.assumed_overall_length_m,
            body_length_m=formation.body_length_m,coupling_gap_m=formation.coupling_gap_assumption_m,body_local_door_offsets_m=formation.doors_per_side_x_m,
            forward_consist_extent_m=[-formation.assumed_overall_length_m,0.],reverse_consist_extent_m=[0.,formation.assumed_overall_length_m],
            directional_power_zones_m=[zone,[-zone[1],-zone[0]]],required_common_straight_m=max(zone[1],-zone[0])-min(zone[0],-zone[1]),
            common_platform_length_m=2*formation.assumed_overall_length_m+a['platform_stopping_allowance_m']),
        source_concepts=len(concepts),projected_anchor_repair_concepts=len(cases)-len(concepts),variant_count=len(rows),geometric_fit_count=sum(row['geometric_research_screen_pass'] for row in rows),
        alternatives=rows,representatives=representatives,representatives_are_unselected_research_examples=True,
        source_terminal_condition=dict(pair='pair-031-040',line='line-4',condition='Published before/after anchor is the same end endpoint; A–H–A is not a through-line',
            implies_entire_hub_impossible=False,explicit_terminal_extension_and_unswitched_turnback_loop_unimplemented=True),
        outstanding=['survey, land, utilities, hydrology, ground and all actual anchor levels','terminal/unswitched return-loop variant where source endpoint is duplicated',
            'actual grade/curve speed, thrust/coasting/energy and all-load moving-train response','transitions: every pier position, clashes and curved/graded beam manufacturing detail',
            'portal strength, bracing, foundations, bearings, joints, erection and seismic','car/arm/platform swept gap and vehicle floor interface',
            'shared multi-stop lift/stair throughput, outages, fire, headroom and acceptance','complete station/route cost and source catchment continuity'],
        hub_selected=False,city_geometry_or_price_replaced=False,**FLAGS)
    result['content_sha256']=sha256(encoded(result)).hexdigest();return encoded(result)


def study():return json.loads(_study(encoded(sources()).decode()))


def geometry_document(result):
    return dict(schema=SCHEMA,source_sha256=result['source_sha256'],stop_convention=result['stop_convention'],
        representatives=result['representatives'],source_terminal_condition=result['source_terminal_condition'],**FLAGS)


def overview(result):
    rows=['<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="900" viewBox="0 0 1400 900"><rect width="1400" height="900" fill="#f8fafc"/>',
        '<g font-family="sans-serif" fill="#102030"><text x="30" y="35" font-size="25">Shared Baghdad hubs: actual station straights and continuous approach fits</text>',
        '<text x="30" y="65" font-size="16">Unselected geometric research examples; no land, structural, operating or physical acceptance.</text>']
    if not result['representatives']:
        rows.append('<text x="40" y="150" font-size="21">No bounded complete geometric/access fit; all rejected cases retained.</text>')
    for i,row in enumerate(result['representatives']):
        xbase=35+i*450;points=[p for line in row['lines'] for beam in line['directional_beams'] for side in ('incoming','outgoing') for p in beam[side]['control_points_xy_m']]
        bounds=[min(p[j] for p in points) for j in (0,1)]+[max(p[j] for p in points) for j in (0,1)]
        scale=min(390/max(bounds[2]-bounds[0],1),500/max(bounds[3]-bounds[1],1))
        def xy(p):return xbase+10+(p[0]-bounds[0])*scale,130+(bounds[3]-p[1])*scale
        rows.append(f'<text x="{xbase}" y="105" font-size="17">{row["pair_id"]}; gap{row["level_spacing_m"]:g}m / island{row["platform_island_width_m"]:g}m</text>')
        for j,line in enumerate(row['lines']):
            color=['#0f766e','#7c3aed','#b45309'][j%3]
            for beam in line['directional_beams']:
                path=[*[bezier(beam['incoming']['control_points_xy_m'],k/50) for k in range(51)],beam['station_end_xy_m'],
                    *[bezier(beam['outgoing']['control_points_xy_m'],k/50) for k in range(1,51)]]
                coords=' '.join(f'{x:.2f},{y:.2f}' for x,y in map(xy,path));rows.append(f'<polyline points="{coords}" fill="none" stroke="{color}" stroke-width="2"/>')
            start,end=map(xy,[line['station_tangent_start_xy_m'],line['station_tangent_end_xy_m']]);rows.append(f'<path d="M{start[0]:.2f},{start[1]:.2f}L{end[0]:.2f},{end[1]:.2f}" stroke="{color}" stroke-width="7"/>')
        stats=[f'{row["quantities"]["new_physical_directional_guideway_m"]:,.0f} m of newly counted guideway',
            '400 m common straight / 350 m directional zones',f'{row["quantities"]["platform_length_m"]:g} m platforms; two opposed front stops at H',
            f'{row["quantities"]["station_columns"]} station columns; curved-route supports unresolved',
            'Exact flaring curves reach ordinary3.8m beam centres.']
        if row['circulation']:
            maximum=max(p['maximum_horizontal_walk_m'] for p in row['circulation']['platform_pair_walks'])
            stats.extend([f'Worst computed shortest door-pair walk: {maximum:.1f} m', 'Vertical lift travel and queues are separate.'])
        for k,text in enumerate(stats):rows.append(f'<text x="{xbase}" y="{670+k*26}" font-size="14">{text}</text>')
    rows.append(f'<text x="30" y="850" font-size="15">{result["variant_count"]} bounded variants; {result["geometric_fit_count"]} fit implemented geometric screens. No selection or engineering release.</text>')
    rows.append('<text x="30" y="877" font-size="15">031–040 line4 through-line is held: duplicated terminal anchor; an explicit terminal extension and return-loop variant remain unimplemented.</text></g></svg>')
    return '\n'.join(rows)+'\n'


def station_plan(result):
    rows=['<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="900" viewBox="0 0 1400 900"><rect width="1400" height="900" fill="#f8fafc"/><g font-family="sans-serif" fill="#102030">',
        '<text x="30" y="35" font-size="24">Computed shared-core station plan: bodies, doors, straights and floor routes</text>']
    if not result['representatives']:rows.append('<text x="40" y="100">No fitting bounded station plan.</text></g></svg>');return '\n'.join(rows)
    example=result['representatives'][0];scale=1.6;centre=[350.,450.]
    def xy(p):return centre[0]+(p[0]-example['shared_site_east_offset_m'])*scale,centre[1]-p[1]*scale
    for i,line in enumerate(example['lines']):
        color=['#0f766e','#7c3aed','#b45309'][i%3];n=normal(line['heading_xy']);c=line['station_centre_xy_m'];width=example['platform_island_width_m']
        platform=body_and_doors(line,width,result['assumptions']);lo,hi=platform['platform_bounds_along_m'];corners=[add(add(c,mul(line['heading_xy'],s)),mul(n,t)) for s,t in [(lo,-width/2),(hi,-width/2),(hi,width/2),(lo,width/2)]]
        coords=' '.join(f'{x:.2f},{y:.2f}' for x,y in map(xy,corners));rows.append(f'<polygon points="{coords}" fill="{color}" fill-opacity="0.16" stroke="{color}"/>')
        for beam in line['directional_beams']:
            p,q=map(xy,[beam['station_start_xy_m'],beam['station_end_xy_m']]);rows.append(f'<path d="M{p[0]:.2f},{p[1]:.2f}L{q[0]:.2f},{q[1]:.2f}" stroke="{color}" stroke-width="2"/>')
        for door in platform['doors']:
            x,y=xy(door['platform_edge_xyz_m']);rows.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="2.4" fill="{color}"/>')
    access=example['circulation']
    for rect in access['common_core_rectangles_xy_m']:
        p,q=map(xy,rect);rows.append(f'<rect x="{p[0]:.2f}" y="{q[1]:.2f}" width="{q[0]-p[0]:.2f}" height="{p[1]-q[1]:.2f}" fill="#475569"/>')
    y=100;rows.append(f'<text x="760" y="{y}" font-size="20">{example["pair_id"]}: computed floor paths</text>');y+=38
    for pair in access['platform_pair_walks']:
        text=f'{pair["from_line"]} ↔ {pair["to_line"]}: {pair["minimum_horizontal_walk_m"]:.1f}–{pair["maximum_horizontal_walk_m"]:.1f}m; lift {pair["lift_time_at_assumed_1m_s"]:.1f}m vertical'
        rows.append(f'<text x="760" y="{y}" font-size="16">{text}</text>');y+=36
        for name in ('shortest_door_route','longest_door_route'):
            for segment in ('from_floor_path','to_floor_path'):
                coords=' '.join(f'{x:.2f},{z:.2f}' for x,z in map(xy,pair[name][segment]['points_xy_m']));rows.append(f'<polyline points="{coords}" fill="none" stroke="#dc2626" stroke-width="1.8"/>')
    notes=['Plan overlays separate platform levels; it is not a same-level junction.', 'Dots: all twelve facing doors/train, both directions/line.', 'Front stops share H; bodies extend104.5m in opposite directions.', 'Platforms219m; powered-zone union400m is fitted explicitly.', 'Two common lifts serve hall and all platform levels.', 'Red: computed shortest/longest door-pair floor paths.', 'Paths avoid inflated core footprints; width is counted.', 'Vertical distances exclude motion profiles, doors and queues.', 'No old platform access or civil price transfers to this layout.', 'All structural, evacuation and site acceptance gates remain open.']
    for text in notes:rows.append(f'<text x="760" y="{y+50}" font-size="15">{text}</text>');y+=34
    rows.append('</g></svg>');return '\n'.join(rows)+'\n'


def readme(result,native_present=False):
    rows=['# Baghdad shared-hub station and approach geometry','', '![Bounded full approach fits](overview.svg)','',
        f'{result["variant_count"]} explicitly bounded alternatives fit continuous transitions, directional beam flaring, station straights, levels and circulation. These include seven original source concepts and {result["projected_anchor_repair_concepts"]} explicit projected-anchor repair concepts. {result["geometric_fit_count"]} pass the implemented geometric screens. The retained examples are research representatives; no hub is selected and no city geometry, inherited civil price or access approval is changed.','',
        'Off-line source anchors remain rejected against the5m projection limit. A separate repair family relocates each affected connection to the exact retained-polyline projection/chainage and records original/projected coordinates and displacement. Its directional approaches are fitted and counted afresh. The source controls, former access records and unaccepted connection/land implications remain visible; the projection limit is not relaxed.','',
        'H is the front stop of the leading car in both directions. Six17m bodies plus five0.5m coupling gaps give104.5m consists extending on opposite sides of H. Exact body-local door offsets are−4.5/+4.5m, giving twelve island-facing doors/train and twenty-four door locations per independent line. The two-direction platform envelope is219m, including10m stopping allowance. Forward powered limits[−150,+200] and reverse[−200,+150] require400m of common straight; a nominal350m centreline alone would omit part of the opposite powered zone.','',
        'Each physical directional beam has its own quintic approach/exit curves: tangent direction and zero endpoint curvature match the retained anchor and station straight. The station beam separation follows the actual2.65m cabin width,75mm assumed door gap and island width; curved approaches continuously flare from the separately declared3.8m ordinary beam centres. A conservative Bernstein-polynomial numerical screen bounds curvature over each retained transition; this is not a formally rounded interval certificate or engineering acceptance. Forward control-polygon, extent, detour, grade and vertical-radius screens reject sharp, looping or unbounded solutions. These are geometry limits, not a qualified maglev operating-speed or coasting result.','',
        'The common multi-level lift/stair core is represented by actual obstruction footprints. Visibility paths stay inside the oriented platform and avoid footprints inflated for the adopted passage width. Every exact boarding-door pair is evaluated, with representative routes retained in full. Reported horizontal min/max include door-edge and lift-entry ingress; lift vertical distance is separate. Shared lift throughput, queues, outages, fire operation, detailed stairs and physical platform interfaces remain unaccepted.','',
        '| Example | New physical beams m | Straight m/line | Island m | Platform m | Station columns | Door-pair horizontal range m |',
        '|---|---:|---:|---:|---:|---:|---|']
    for row in result['representatives']:
        walks=row['circulation']['platform_pair_walks'];lo=min(p['minimum_horizontal_walk_m'] for p in walks);hi=max(p['maximum_horizontal_walk_m'] for p in walks)
        rows.append(f'| {row["id"]} | {row["quantities"]["new_physical_directional_guideway_m"]:,.1f} | 400 | {row["platform_island_width_m"]:g} | {row["quantities"]["platform_length_m"]:g} | {row["quantities"]["station_columns"]} | {lo:.1f}–{hi:.1f} |')
    rows+=['','![Exact platform and door-route plan](station-plan.svg)','',
        'The031–040 source concept assigns line4 the same terminal endpoint before and after H. Its A–H–A construction is rejected as a through-line. This does not prove the entire shared hub impossible: an explicit terminal extension, paired arrival/return beams and a counted unswitched turnback loop still need their own fit. That alternative is unimplemented and receives no loop, land or cost credit.','',
        'Station columns are located outside every lower station envelope, and cap/vehicle and hall/beam vertical clearances are checked against stated assumptions. All approach lengths and flaring are counted afresh. Curved/graded beam fabrication, every transition-pier position and clash, station portal strength, foundations, erection, seismic and measured site constraints remain open. Raw quantity totals and native solids are partial geometry evidence. No complete installed cost or engineering release is claimed.','',
        '[Full bounded calculation](study.json.gz) · [Geometric definitions](geometry.json) · [Source/payload receipt](manifest.json)','']
    if native_present:rows+=['','![Reopened native station geometry](overview.png)','',
        '[Native FreeCAD station assembly](model.FCStd) · [Compressed STEP](model.step.gz) · [Native reopen receipt](native-cad.json). The export covers the bounded straight-station, portals, platforms and common core. Long curved approaches remain analytic geometric definitions, not released curved-beam fabrication.','']
    rows+=['- ['+v['title']+']('+v['url']+'): '+v['use'] for v in result['assumptions']['external_guidance']]
    return '\n'.join(rows)+'\n'


def native_definition(result):
    if not result['representatives']:return None
    row=result['representatives'][0];a=result['assumptions'];cv=configuration.selected().civil;parts=[]
    def box(identity,length,width,height,xy,bottom,angle=0.,role='concrete'):
        parts.append(dict(id=identity,kind='box',size_m=[length,width,height],xy_m=xy,bottom_m=bottom,
            angle_deg=angle,role=role,volume_m3=length*width*height,production_released=False))
    for line in row['lines']:
        theta=math.degrees(math.atan2(line['heading_xy'][1],line['heading_xy'][0]));heading=line['heading_xy']
        for beam in line['directional_beams']:
            marks=sorted(p['s_m'] for p in row['portal_layout']['portals'] if p['line']==line['line'])
            for i,(start,end) in enumerate(zip(marks,marks[1:])):
                span=end-start;point=add(beam['station_start_xy_m'],mul(heading,(start+end)/2-line['station_tangent_bounds_m'][0]));area=cv.width_m*cv.depth_m-(cv.width_m-2*cv.web_m)*(cv.depth_m-2*cv.flange_m)
                parts.append(dict(id=beam['id']+'-bay-'+str(i+1),kind='hollow-guidebeam',size_m=[span,cv.width_m,cv.depth_m],
                    web_m=cv.web_m,flange_m=cv.flange_m,xy_m=point,bottom_m=line['beam_top_level_m']-cv.depth_m,
                    angle_deg=theta,role=line['line'],volume_m3=area*span,production_released=False))
        length=2*configuration.selected().formation.assumed_overall_length_m+a['platform_stopping_allowance_m']
        box(line['line']+'-platform',length,row['platform_island_width_m'],a['platform_slab_m'],line['station_centre_xy_m'],line['platform_floor_level_m']-a['platform_slab_m'],theta,role=line['line'])
        parts[-1]['cutout_rectangles_xy_m']=[*row['circulation']['common_core_rectangles_xy_m'],*row['circulation']['floor_column_obstacles_by_line'][line['line']]]
        parts[-1]['volume_m3']-=sum(rectangle_platform_overlap_area(rect,line['station_centre_xy_m'],heading,length,row['platform_island_width_m'])*a['platform_slab_m'] for rect in parts[-1]['cutout_rectangles_xy_m'])
    for portal in row['portal_layout']['portals']:
        theta=math.degrees(math.atan2(portal['heading_xy'][1],portal['heading_xy'][0]));p,q=[v['xy_m'] for v in portal['column_points']]
        box(portal['id']+'-cap',a['portal_cap_width_m'],portal['cap_span_m'],a['portal_cap_depth_m'],mul(add(p,q),.5),portal['column_top_level_m'],theta)
        for i,point in enumerate((p,q)):box(portal['id']+'-column-'+str(i+1),a['portal_column_width_m'],a['portal_column_width_m'],portal['column_top_level_m'],point,0.)
    centre=row['lines'][0]['station_centre_xy_m'];box('common-hall-floor',a['hall_side_m'],a['hall_side_m'],a['hall_slab_m'],centre,a['hall_floor_m']-a['hall_slab_m'])
    hall=parts[-1];hall['cutout_rectangles_xy_m']=[];half=a['hall_side_m']/2;cw=a['portal_column_width_m']/2
    for portal in row['portal_layout']['portals']:
        for column in portal['column_points']:
            point=column['xy_m'];lo=[max(centre[j]-half,point[j]-cw) for j in (0,1)];hi=[min(centre[j]+half,point[j]+cw) for j in (0,1)]
            if all(hi[j]>lo[j] for j in (0,1)):
                hall['cutout_rectangles_xy_m'].append([lo,hi]);hall['volume_m3']-=(hi[0]-lo[0])*(hi[1]-lo[1])*a['hall_slab_m']
    for i,(lo,hi) in enumerate(row['circulation']['common_core_rectangles_xy_m'][1:]):
        box('lift-clearance-envelope-'+str(i+1),hi[0]-lo[0],hi[1]-lo[1],max(v['platform_floor_level_m'] for v in row['lines'])-a['hall_floor_m'],
            mul(add(lo,hi),.5),a['hall_floor_m'],role='clearance-envelope')
    # Explicit tread and landing stock is retained; stringer/connection/rebar
    # details and final stair headroom still require independent acceptance.
    for piece in row['circulation']['stair_geometry']['units']:
        box(piece['id'],*piece['size_m'],piece['xy_m'],piece['bottom_m'])
    return dict(schema=SCHEMA,layout_id=row['id'],parts=parts,scope='Straight station material regions, counted portals/platform cutouts/common stair treads; two separately identified lift clearance envelopes. Approach curves, foundations, joints, roof and structural acceptance remain outside native scope.',**FLAGS)


def native_export(definition_path,output):
    """Executed inside FreeCADCmd; actual solids and independent reopen checks."""
    import FreeCAD as App
    import Part
    definition_path=Path(definition_path);output=Path(output);value=json.loads(definition_path.read_text());doc=App.newDocument('SharedHub');objects=[];checks=[];mesh=[]
    for i,p in enumerate(value['parts']):
        length,width,height=[v*1000 for v in p['size_m']]
        shape=Part.makeBox(length,width,height,App.Vector(-length/2,-width/2,0.))
        if p['kind']=='hollow-guidebeam':
            web=p['web_m']*1000;flange=p['flange_m']*1000
            shape=shape.cut(Part.makeBox(length,width-2*web,height-2*flange,App.Vector(-length/2,-width/2+web,flange)))
        shape.rotate(App.Vector(0.,0.,0.),App.Vector(0.,0.,1.),p['angle_deg']);shape.translate(App.Vector(p['xy_m'][0]*1000,p['xy_m'][1]*1000,p['bottom_m']*1000))
        for lo,hi in p.get('cutout_rectangles_xy_m',[]):
            cutter=Part.makeBox((hi[0]-lo[0])*1000,(hi[1]-lo[1])*1000,height+200.,App.Vector(lo[0]*1000,lo[1]*1000,p['bottom_m']*1000-100.))
            shape=shape.cut(cutter)
        if not shape.isValid() or shape.Volume<=0 or not math.isclose(shape.Volume/1e9,p['volume_m3'],rel_tol=1e-7):raise ValueError('native solid/independent stock-volume mismatch: '+p['id'])
        obj=doc.addObject('PartDesign::Feature','Part'+str(i));obj.Label=p['id'];obj.Shape=shape;obj.addProperty('App::PropertyString','DesignId');obj.DesignId=p['id']
        obj.addProperty('App::PropertyBool','ProductionReleased');obj.ProductionReleased=False;objects.append(obj)
        b=shape.BoundBox;bounds=[v/1000 for v in (b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax)]
        checks.append(dict(id=p['id'],volume_m3=shape.Volume/1e9,bounds_m=bounds,valid=True,role=p['role']))
        vertices,faces=shape.tessellate(20.);mesh.append(dict(id=p['id'],role=p['role'],vertices_m=[[v.x/1000,v.y/1000,v.z/1000] for v in vertices],triangles=[list(f) for f in faces]))
    doc.recompute();path=output/'model.FCStd';doc.saveAs(str(path));Part.export(objects,str(output/'model.step'));App.closeDocument(doc.Name)
    restored=App.openDocument(str(path));found=[o for o in restored.Objects if 'DesignId' in o.PropertiesList]
    if len(found)!=len(checks) or {o.DesignId for o in found}!={p['id'] for p in checks} or any(not o.Shape.isValid() or o.ProductionReleased for o in found):raise ValueError('native reopen identity/solid mismatch')
    expected={p['id']:p['volume_m3'] for p in checks}
    if any(not math.isclose(o.Shape.Volume/1e9,expected[o.DesignId],rel_tol=1e-7) for o in found):raise ValueError('native reopen volume changed')
    App.closeDocument(restored.Name);step=Part.read(str(output/'model.step'))
    if not step.isValid() or not math.isclose(step.Volume/1e9,sum(p['volume_m3'] for p in checks),rel_tol=1e-7):raise ValueError('STEP reopen/volume mismatch')
    (output/'native-mesh.json.gz').write_bytes(gzip.compress(encoded(dict(schema=SCHEMA,definition_sha256=digest(definition_path),parts=mesh,**FLAGS)),mtime=0))
    (output/'native-cad.json').write_text(json.dumps(dict(schema=SCHEMA,definition_sha256=digest(definition_path),exporter_sha256=digest(__file__),
        fcstd_reopened=True,step_reopened=True,freecad_version=list(App.Version()),opencascade_version=Part.OCC_VERSION,
        part_count=len(checks),parts=checks,**FLAGS),sort_keys=True,indent=2)+'\n')


def native_render(output):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    value=json.loads(gzip.decompress((output/'native-mesh.json.gz').read_bytes()));fig=plt.figure(figsize=(14,9));ax=fig.add_subplot(111,projection='3d')
    colors={'line-1':'#0f766e','line-6':'#7c3aed','line-9':'#b45309','concrete':'#94a3b8'}
    all_points=[]
    for p in value['parts']:
        if p['role']=='clearance-envelope':continue
        vertices=p['vertices_m'];faces=[[vertices[i] for i in face] for face in p['triangles']];all_points.extend(vertices)
        ax.add_collection3d(Poly3DCollection(faces,facecolor=colors.get(p['role'],'#589294'),edgecolor='#475569',linewidths=.12,alpha=.9))
    ax.auto_scale_xyz([p[0] for p in all_points],[p[1] for p in all_points],[p[2] for p in all_points]);ranges=[max(p[j] for p in all_points)-min(p[j] for p in all_points) for j in range(3)]
    ax.set_box_aspect([ranges[0],ranges[1],ranges[2]*4]);ax.view_init(24,-55)
    ax.set_xlabel('East m');ax.set_ylabel('North m');ax.set_zlabel('Elevation m');ax.set_title('Reopened station native solids — vertical display×4; engineering/physical acceptance open',fontsize=12)
    fig.tight_layout();fig.savefig(output/'overview.png',dpi=110);plt.close(fig)
    (output/'native-visual.json').write_text(json.dumps(dict(schema=SCHEMA,renderer_sha256=digest(__file__),
        definition_sha256=value['definition_sha256'],mesh_sha256=digest(output/'native-mesh.json.gz'),
        image_sha256=digest(output/'overview.png'),parts=len(value['parts']),
        scope='Actual retained native tessellation; clearance envelopes omitted from material rendering',**FLAGS),sort_keys=True,indent=2)+'\n')


def generate_native(result,output):
    value=native_definition(result)
    if value is None:return False
    work=ROOT/'build/shared-hub-layout-native';work.mkdir(parents=True,exist_ok=True);definition=work/'definition.json';definition.write_bytes(encoded(value))
    script=work/'export.py';complete=work/'completed';complete.unlink(missing_ok=True)
    script.write_text('import sys\nfrom pathlib import Path\nsys.path[:0]='+repr([str(ROOT)])+'\nfrom engineering.ferrite_maglev.shared_hub_layout import native_export\nnative_export('+repr(str(definition.resolve()))+','+repr(str(output.resolve()))+')\nPath('+repr(str(complete.resolve()))+').write_text("complete")\n')
    binary=shutil.which('FreeCADCmd') or shutil.which('freecadcmd');command=[binary] if binary else ['flatpak','run','--filesystem='+str(ROOT),'--command=FreeCADCmd','org.freecad.FreeCAD']
    with (work/'freecad.log').open('w') as log:subprocess.run([*command,str(script.resolve())],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,timeout=600,check=True)
    if not complete.is_file():raise ValueError('native shared-hub export incomplete')
    from engineering.factory_examples.native import _canonicalise_fcstd
    _canonicalise_fcstd(output/'model.FCStd')
    raw=(output/'model.step').read_bytes();(output/'model.step.gz').write_bytes(gzip.compress(raw,mtime=0));(output/'model.step').unlink();native_render(output)
    receipt=json.loads((output/'native-cad.json').read_text());receipt['files_sha256']={name:digest(output/name) for name in ('model.FCStd','model.step.gz','native-mesh.json.gz')}
    (output/'native-cad.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
    return True


def mesh_volume(part):
    vertices=part['vertices_m'];faces=part['triangles']
    if not 4<=len(vertices)<=100000 or not 4<=len(faces)<=200000:raise ValueError('bounded closed native mesh required')
    if any(len(p)!=3 or any(type(x) not in (int,float) or not math.isfinite(x) for x in p) for p in vertices):raise ValueError('finite native mesh vertices required')
    identities=[tuple(round(x,8) for x in p) for p in vertices];edges={};terms=[]
    for face in faces:
        if len(face)!=3 or len(set(face))!=3 or any(type(i) is not int or not 0<=i<len(vertices) for i in face):raise ValueError('native triangle indices differ')
        p,q,r=[vertices[i] for i in face]
        terms.append(p[0]*(q[1]*r[2]-q[2]*r[1])+p[1]*(q[2]*r[0]-q[0]*r[2])+p[2]*(q[0]*r[1]-q[1]*r[0]))
        for i,j in zip(face,face[1:]+face[:1]):
            first,last=identities[i],identities[j]
            if first==last:raise ValueError('collapsed native mesh edge')
            key=tuple(sorted((first,last)));count,balance=edges.get(key,(0,0));edges[key]=(count+1,balance+(1 if first<last else -1))
    if any(count!=2 or balance!=0 for count,balance in edges.values()):raise ValueError('native mesh is not a closed consistently oriented shell')
    return abs(math.fsum(terms))/6


def verify_stock_placement(mesh_part,definition_part):
    """Check position/orientation against source stock, independent of CAD claims."""
    angle=math.radians(definition_part['angle_deg']);c=math.cos(angle);s=math.sin(angle);xy=definition_part['xy_m'];bottom=definition_part['bottom_m']
    points=[]
    for x,y,z in mesh_part['vertices_m']:
        dx=x-xy[0];dy=y-xy[1];points.append([c*dx+s*dy,-s*dx+c*dy,z-bottom])
    actual=[min(p[j] for p in points) for j in range(3)]+[max(p[j] for p in points) for j in range(3)]
    length,width,height=definition_part['size_m'];expected=[-length/2,-width/2,0.,length/2,width/2,height]
    if any(abs(x-y)>1e-6 for x,y in zip(actual,expected)):raise ValueError('native mesh placement differs from source xy/angle/z stock definition')
    return actual


def publish(output=OUTPUT,*,native=True):
    result=study();output=Path(output);output.mkdir(parents=True,exist_ok=True)
    if output.is_symlink() or any(p.is_symlink() or p.name not in BASE_FILES|NATIVE_FILES|{'manifest.json'} for p in output.iterdir()):raise ValueError('unowned or linked shared-hub packet file')
    raw=encoded(result)
    if len(raw)>MAX_RAW:raise ValueError('bounded shared hub raw packet exceeded')
    (output/'study.json.gz').write_bytes(gzip.compress(raw,mtime=0));(output/'geometry.json').write_bytes(encoded(geometry_document(result)))
    (output/'overview.svg').write_text(overview(result));(output/'station-plan.svg').write_text(station_plan(result))
    native_present=generate_native(result,output) if native and result['assumptions']['native_enabled'] else False
    if not native_present:
        for name in NATIVE_FILES:(output/name).unlink(missing_ok=True)
    (output/'README.md').write_text(readme(result,native_present))
    if result['source_sha256']!=sources():raise ValueError('shared hub sources changed during publication')
    files=BASE_FILES|(NATIVE_FILES if native_present else set())
    manifest=dict(schema=SCHEMA,source_sha256=result['source_sha256'],content_sha256=result['content_sha256'],raw_bytes=len(raw),
        native_present=native_present,files_sha256={name:digest(output/name) for name in sorted(files)},**FLAGS)
    (output/'manifest.json').write_text(json.dumps(manifest,sort_keys=True,indent=2)+'\n');verify(output);return manifest


def verify(output=OUTPUT):
    output=Path(output)
    if output.is_symlink() or any(p.is_symlink() for p in output.iterdir()):raise ValueError('ordinary shared hub packet required')
    manifest=json.loads((output/'manifest.json').read_bytes());files=BASE_FILES|(NATIVE_FILES if manifest['native_present'] else set())
    if set(p.name for p in output.iterdir())!=files|{'manifest.json'} or set(manifest['files_sha256'])!=files:raise ValueError('shared hub inventory differs')
    if manifest['schema']!=SCHEMA or any(manifest.get(k) is not False for k in FLAGS):raise ValueError('shared hub packet may not claim release')
    if manifest['source_sha256']!=sources():raise ValueError('shared hub source receipt stale')
    for name in files:
        path=output/name
        if path.stat().st_size>MAX_FILE or digest(path)!=manifest['files_sha256'][name]:raise ValueError('shared hub bounded payload checksum differs')
    with gzip.GzipFile(fileobj=io.BytesIO((output/'study.json.gz').read_bytes())) as stream:raw=stream.read(MAX_RAW+1)
    expected=study()
    if len(raw)>MAX_RAW or len(raw)!=manifest['raw_bytes'] or raw!=encoded(expected) or manifest['content_sha256']!=expected['content_sha256']:raise ValueError('shared hub recalculated content differs')
    if ((output/'geometry.json').read_bytes()!=encoded(geometry_document(expected)) or (output/'overview.svg').read_text()!=overview(expected)
            or (output/'station-plan.svg').read_text()!=station_plan(expected) or (output/'README.md').read_text()!=readme(expected,manifest['native_present'])):
        raise ValueError('shared hub presentation differs from actual geometry')
    if manifest['native_present']:
        definition=native_definition(expected);receipt=json.loads((output/'native-cad.json').read_bytes())
        if not receipt['fcstd_reopened'] or not receipt['step_reopened'] or receipt['exporter_sha256']!=digest(__file__) or receipt['definition_sha256']!=sha256(encoded(definition)).hexdigest():raise ValueError('native shared hub source/reopen evidence differs')
        if receipt['part_count']!=len(definition['parts']) or [p['id'] for p in receipt['parts']]!=[p['id'] for p in definition['parts']]:raise ValueError('native shared hub part identity differs')
        for p,r in zip(definition['parts'],receipt['parts']):
            if not r['valid'] or not math.isclose(p['volume_m3'],r['volume_m3'],rel_tol=1e-7):raise ValueError('native shared hub stock-volume evidence differs')
        if set(receipt.get('files_sha256',{}))!={'model.FCStd','model.step.gz','native-mesh.json.gz'} or any(digest(output/name)!=value for name,value in receipt['files_sha256'].items()):raise ValueError('native CAD nested payload binding differs')
        with gzip.GzipFile(fileobj=io.BytesIO((output/'native-mesh.json.gz').read_bytes())) as stream:mesh_raw=stream.read(4*MAX_FILE+1)
        if len(mesh_raw)>4*MAX_FILE:raise ValueError('bounded native mesh expansion required')
        mesh=json.loads(mesh_raw);visual=json.loads((output/'native-visual.json').read_text());definition_sha=sha256(encoded(definition)).hexdigest()
        if (mesh.get('schema')!=SCHEMA or mesh.get('definition_sha256')!=definition_sha or visual.get('definition_sha256')!=definition_sha
                or visual.get('renderer_sha256')!=digest(__file__) or visual.get('mesh_sha256')!=digest(output/'native-mesh.json.gz')
                or visual.get('image_sha256')!=digest(output/'overview.png') or visual.get('parts')!=len(definition['parts'])
                or [p['id'] for p in mesh['parts']]!=[p['id'] for p in definition['parts']]
                or any(v.get(key) is not False for v in (receipt,mesh,visual) for key in FLAGS)):
            raise ValueError('native mesh/visual definition and source binding differs')
        for actual,expected_part,cad_part in zip(mesh['parts'],definition['parts'],receipt['parts']):
            if actual['role']!=expected_part['role'] or not math.isclose(mesh_volume(actual),expected_part['volume_m3'],rel_tol=1e-6,abs_tol=1e-7):raise ValueError('native mesh occupied volume differs')
            verify_stock_placement(actual,expected_part)
            bounds=[min(p[j] for p in actual['vertices_m']) for j in range(3)]+[max(p[j] for p in actual['vertices_m']) for j in range(3)]
            if any(abs(x-y)>1e-7 for x,y in zip(bounds,cad_part['bounds_m'])):raise ValueError('native mesh/CAD occupied bounds differ')
        from PIL import Image
        with Image.open(output/'overview.png') as picture:
            if picture.format!='PNG' or picture.width<1000 or picture.height<700:raise ValueError('native PNG dimensions/format differ')
        with zipfile.ZipFile(output/'model.FCStd') as archive:
            names=archive.namelist()
            if 'Document.xml' not in names or len(set(names))!=len(names) or sum(i.file_size for i in archive.infolist())>4*MAX_FILE or any(i.file_size>MAX_FILE or '..' in Path(i.filename).parts or Path(i.filename).is_absolute() for i in archive.infolist()):raise ValueError('bounded native shared hub archive required')
            if archive.testzip() is not None:raise ValueError('native shared hub archive CRC differs')
    return manifest


def read_summary(output=OUTPUT):
    receipt=verify(output);value=study();maximum=max((p['maximum_horizontal_walk_m'] for row in value['representatives'] for p in row['circulation']['platform_pair_walks']),default=None)
    return dict(schema=SCHEMA,source_concepts=value['source_concepts'],variant_count=value['variant_count'],geometric_fit_count=value['geometric_fit_count'],
        projected_anchor_repair_concepts=value['projected_anchor_repair_concepts'],
        representatives=len(value['representatives']),required_common_straight_m=value['stop_convention']['required_common_straight_m'],
        common_platform_length_m=value['stop_convention']['common_platform_length_m'],maximum_representative_door_walk_m=maximum,
        native_present=receipt['native_present'],hub_selected=False,**FLAGS)
