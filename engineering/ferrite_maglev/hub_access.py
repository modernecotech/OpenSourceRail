"""Physical access-kit alternatives for unselected Baghdad interchange studies.

Located reference walkways, stock sections and deterministic queues close
calculation gaps. They do not approve routes, foundations, lifts or a hub merge.
"""
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
import heapq
from itertools import combinations
from pathlib import Path
import gzip
import io
import json
import math
import tomllib

from . import interchange_hubs as hubs

ROOT=Path(__file__).resolve().parents[2]
INPUT=Path(__file__).with_name('hub-access.toml')
OUTPUT=ROOT/'docs/design-engine/ferrite-maglev/hub-access'
TEST=ROOT/'engineering/analysis/tests/test_ferrite_maglev_hub_access.py'
FLAGS=dict(design_complete=False,engineering_accepted=False,physical_validation=False,
    manufacturing_release=False,physical_release=False)
SCHEMA='osr-hub-access-design-study/1'
FILES={'study.json.gz','geometry.json','overview.svg','assembly.svg','README.md'}
MAX_RAW=24*1024*1024
MAX_COMPRESSED=4*1024*1024


def encoded(value):return json.dumps(value,sort_keys=True,allow_nan=False,separators=(',',':')).encode()
def digest(path):return sha256(Path(path).read_bytes()).hexdigest()


def number(value,name,*,zero=False):
    if type(value) not in (int,float) or not math.isfinite(value) or (value<0 if zero else value<=0):
        raise ValueError('finite '+('nonnegative ' if zero else 'positive ')+name+' required')
    return value


def load():
    a=tomllib.loads(INPUT.read_text())
    if a['schema']!=SCHEMA or a['city']!='Baghdad' or a['selected_hub'] is not False or a['costs_are_quotes'] is not False:
        raise ValueError('unselected Baghdad access study required')
    if any(v is not False for v in a['validation'].values()):raise ValueError('external acceptance remains open')
    for group in (a,a['reference_loads'],a['concrete'],a['steel'],a['access'],a['flow'],a['cost_sensitivities']):
        for key,value in group.items():
            if type(value) in (int,float):number(value,key)
            elif isinstance(value,list) and value and type(value[0]) in (int,float):
                if len(value)>12:raise ValueError('bounded alternatives required')
                for entry in value:number(entry,key,zero=key=='lift_outages')
    if not 1<=a['maximum_source_variants']<=40 or not 5<=a['maximum_support_spacing_m']<=25:
        raise ValueError('bounded source/support search required')
    if not all(2.2<=v<=8 for v in a['clear_widths_m']):raise ValueError('bounded clear walkway width required')
    ac=a['access'];f=a['flow'];s=a['steel'];c=a['concrete']
    if ac['gradient_denominator']<20 or ac['maximum_rise_between_landings_m']>.5 or a['rest_interval_m']>50:
        raise ValueError('accessible reference geometry exceeds adopted benchmark')
    if ac['ramp_lane_pitch_m']<max(a['clear_widths_m'][0],ac['stair_clear_width_m']) or ac['landing_length_m']<a['clear_widths_m'][0]:
        raise ValueError('ramp runs or landings overlap clear space')
    if ac['lift_internal_width_m']<1.6 or ac['lift_internal_depth_m']<1.5 or ac['lift_clear_door_m']<1.1:
        raise ValueError('lift reference clear space insufficient')
    if not all(type(v) is int and 1<=v<=4 for v in ac['lift_counts_per_core']):raise ValueError('bounded lift counts required')
    if not all(type(v) is int and 0<=v<=4 for v in ac['lift_outages']):raise ValueError('integer outage counts required')
    if not 1<=f['repeat_pulses']<=8 or f['time_step_s']!=1 or f['pulse_duration_s']>min(f['headways_s']):
        raise ValueError('bounded nonoverlapping pulse simulation required')
    if not 0<ac['mobility_party_fraction_of_total_people']<=1 or f['edge_allowance_m']>=min(a['clear_widths_m']):
        raise ValueError('bounded demand/edge assumptions required')
    if ac['mobility_party_fraction_of_total_people']*ac['people_per_wheelchair_party']>1:
        raise ValueError('wheelchair parties and companions exceed total pulse')
    if 2*s['rhs_wall_m']>=min(s['rhs_depth_m'],s['rhs_width_m']) or 2*c['girder_flange_m']>=c['girder_depth_m']:
        raise ValueError('hollow section dimensions invalid')
    return a


def source_paths():
    return sorted(set([Path(__file__),INPUT,TEST,*hubs.source_paths(),
        *(hubs.OUTPUT/name for name in hubs.FILES|{'manifest.json'})]))


def sources():return {p.relative_to(ROOT).as_posix():digest(p) for p in source_paths()}


def polyline(points):
    clean=[]
    for p in points:
        if len(p)!=3 or any(type(x) not in (int,float) or not math.isfinite(x) for x in p):raise ValueError('finite xyz required')
        if not clean or math.dist(clean[-1],p)>1e-7:clean.append(list(p))
    if len(clean)<2:raise ValueError('nonzero physical route required')
    distances=[0.]
    for p,q in zip(clean,clean[1:]):distances.append(distances[-1]+math.dist(p,q))
    return clean,distances


def at(points,chainages,s):
    if not -1e-8<=s<=chainages[-1]+1e-8:raise ValueError('point outside route')
    for i,(lo,hi) in enumerate(zip(chainages,chainages[1:])):
        if s<=hi+1e-8:
            t=max(0.,min(1.,(s-lo)/(hi-lo)))
            return [p+t*(q-p) for p,q in zip(points[i],points[i+1])]
    return list(points[-1])


def canonical_intervals(components):
    """Union repeated intervals only on the same declared physical alignment."""
    groups={};identities=set()
    for row in components:
        if row['id'] in identities:raise ValueError('duplicate component identity')
        identities.add(row['id'])
        if len(row['interval_m'])!=2:raise ValueError('interval endpoints required')
        for value in row['interval_m']:number(value,'interval',zero=True)
        groups.setdefault(row['alignment_id'],[]).append(row['interval_m'])
    return [dict(id=key+'-'+str(i+1),alignment_id=key,interval_m=value,length_m=value[1]-value[0])
        for key,values in sorted(groups.items()) for i,value in enumerate(hubs.interval_union(values))]


def segment_distance(p,q,r,s):
    """Plan distance, including a real zero for intersecting segments."""
    def cross(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
    def point_segment(a,b,c):
        d=[c[i]-b[i] for i in (0,1)];norm=sum(v*v for v in d)
        t=max(0.,min(1.,sum((a[i]-b[i])*d[i] for i in (0,1))/norm)) if norm else 0.
        return math.hypot(*(a[i]-b[i]-t*d[i] for i in (0,1)))
    if (cross(p,q,r)*cross(p,q,s)<0 and cross(r,s,p)*cross(r,s,q)<0):return 0.
    return min(point_segment(p,r,s),point_segment(q,r,s),point_segment(r,p,q),point_segment(s,p,q))


def clearance(routes,width,a):
    corridors=[r for r in routes if r.get('kind')=='offset-corridor']
    reference=[(p,q) for row in corridors for p,q in zip(row['source_guideway_reference_xyz_m'],row['source_guideway_reference_xyz_m'][1:])]
    distances=[segment_distance(p,q,r,s) for row in corridors for p,q in zip(row['points_xyz_m'],row['points_xyz_m'][1:]) for r,s in reference]
    minimum=min(distances);required=width/2+a['reference_guideway_envelope_half_width_m']+a['reference_guideway_separation_m']
    return dict(minimum_corridor_to_source_guideway_centreline_m=minimum,required_separation_m=required,
        assumed_plan_separation_screen_pass=minimum>=required,actual_vehicle_guideway_swept_envelope_qualified=False,
        station_interface_spurs_excluded_from_mainline_screen=True,
        station_interfaces_require_approved_side_platform_and_level_geometry=True,site_obstacles_checked=False)


def physical_routes(variant,a):
    """Use retained geographical polylines; never replace their length by a chord."""
    lon0,lat0=variant['new_shared_line_stop_coordinate'];scale=math.cos(math.radians(lat0));routes=[]
    for connector in variant['connectors']:
        points=[[math.radians(p[0]-lon0)*hubs.op.EARTH_M*scale,
            math.radians(p[1]-lat0)*hubs.op.EARTH_M,a['deck_level_m']]
            for p in connector['retained_guideway_reference_coordinates']]
        original,distances=polyline(points)
        points=[[p[0]+a['walkway_offset_east_m'],p[1],p[2]] for p in original]
        routes.append(dict(id=connector['source_platform_id'],kind='offset-corridor',points_xyz_m=points,chainages_m=distances,
            length_m=distances[-1],upstream_reference_length_m=connector['reference_horizontal_route_length_m'],
            source_guideway_reference_xyz_m=original,source_coordinate=connector['source_coordinate'],source_line=connector['source_platform_line']))
    # Shared arms are prohibited here: this focused two-arm kit has disjoint
    # interiors. Generic interval union is separately executable and tested.
    for i,p in enumerate(routes):
        for q in routes[i+1:]:
            for x in p['points_xyz_m'][1:]:
                if any(math.dist(x,y)<1e-5 for y in q['points_xyz_m'][1:]):
                    raise ValueError('overlapping arms need explicit shared topology, not duplicate modules')
    interfaces={}
    for row in routes:
        for index in (0,-1):
            p=row['source_guideway_reference_xyz_m'][index];q=row['points_xyz_m'][index]
            key=tuple(round(v,5) for v in p)
            interfaces.setdefault(key,dict(id='platform-interface-'+str(len(interfaces)+1),kind='platform-interface-spur',
                points_xyz_m=[p,q],chainages_m=[0.,a['walkway_offset_east_m']],length_m=a['walkway_offset_east_m'],
                source_line=row['source_line'] if index==-1 else variant['shared_line'],
                platform_level_and_train_clearance_qualified=False))
    return routes+list(interfaces.values()),dict(lon=lon0,lat=lat0,
        projection='local equirectangular; measured survey not available',offset_east_m=a['walkway_offset_east_m'],
        placement='Independent translated walkway plus counted station-interface spurs; no shared train-beam deck credit')


def kit_geometry(routes,width,a):
    supports={};units=[];rests=[];bearing_seats=0;identities=set();edges=set()
    for route in routes:
        if route['id'] in identities:raise ValueError('duplicate physical route identity')
        identities.add(route['id'])
        points=route['points_xyz_m'];distances=route['chainages_m'];length=distances[-1]
        if abs(route['length_m']-length)>1e-7:raise ValueError('physical route length differs from geometry')
        # Every polyline bend receives a support. Omitting bends would silently
        # turn the retained path into unsupported kinked spans.
        marks={round(v,8) for v in distances}
        for lo,hi in zip(distances,distances[1:]):
            count=max(1,math.ceil((hi-lo)/a['maximum_support_spacing_m']))
            marks.update(round(lo+(hi-lo)*i/count,8) for i in range(count+1))
        ordered=sorted(marks)
        for s in ordered:
            point=at(points,distances,s);key=tuple(round(v,5) for v in point)
            supports.setdefault(key,dict(id='support-'+str(len(supports)+1),coordinate_xyz_m=point,
                bearing_seats=0,foundation_accepted=False))
        for i,(lo,hi) in enumerate(zip(ordered,ordered[1:])):
            if hi-lo<1e-6:continue
            start=at(points,distances,lo);end=at(points,distances,hi)
            edge=tuple(sorted(tuple(round(v,5) for v in point) for point in (start,end)))
            if edge in edges:raise ValueError('overlapping duplicate physical span')
            edges.add(edge)
            ids=[]
            for point in (start,end):
                support=supports[tuple(round(v,5) for v in point)];support['bearing_seats']+=1;ids.append(support['id'])
            bearing_seats+=2
            units.append(dict(id=route['id']+'-deck-'+str(i+1),route_id=route['id'],kind='simply-supported-deck-bay',
                endpoints_xyz_m=[start,end],length_m=hi-lo,clear_width_m=width,support_ids=ids,
                connections=['fixed bearing at start','guided bearing at end','bolted accessible joint cover'],
                installation_tolerance_m=None,qualified_lifting_points=None,manufacturing_release=False))
        for i in range(1,math.ceil(length/a['rest_interval_m'])):
            s=min(i*a['rest_interval_m'],length);point=at(points,distances,s)
            rests.append(dict(id=route['id']+'-rest-'+str(i),coordinate_xyz_m=point,
                additional_deck_area_m2=a['rest_bay_length_m']*a['rest_bay_additional_width_m'],
                clear_route_obstructed=False,seat_and_backrest_qualified=False))
    for unit in units:
        unit['revision']=sha256(encoded(unit)).hexdigest()
        unit['qa_traveller']=dict(unit_id=unit['id'],unit_revision=unit['revision'],serial=None,
            required=['approved section and joint drawings','material trace','dimensions','weld/reinforcement inspection',
                'lifting/transport inspection','bearing/joint locking','installed survey','independent acceptance'],
            records=[],status='unexecuted',manufacturing_release=False)
    # Two 50 m arm patterns leave a 100 m gap across a three-way junction.
    # Count an actual recessed rest bay at each branching support as well.
    for support in supports.values():
        if support['bearing_seats']>=3:
            rests.append(dict(id=support['id']+'-junction-rest',coordinate_xyz_m=support['coordinate_xyz_m'],
                additional_deck_area_m2=a['rest_bay_length_m']*a['rest_bay_additional_width_m'],
                clear_route_obstructed=False,seat_and_backrest_qualified=False,junction_rest_bay=True))
    length=sum(r['length_m'] for r in routes);rest_area=sum(r['additional_deck_area_m2'] for r in rests)
    return dict(routes=routes,units=units,supports=list(supports.values()),rest_bays=rests,
        horizontal_length_m=length,clear_width_m=width,main_deck_area_m2=length*width,
        rest_bay_additional_area_m2=rest_area,total_deck_area_m2=length*width+rest_area,
        canopy_area_m2=length*width+rest_area,parapet_length_m=2*length,
        deck_bays=len(units),unique_support_positions=len(supports),independent_bearing_seats=bearing_seats,
        shared_foundation_cost_credit=False,foundations_counted_as_qualified=False,
        bend_supports_counted=True,common_node_bearing_group_requires_design=True,**FLAGS)


def walking_matrix(geometry,a):
    """Shortest physical walks between all proposed platform interfaces.

    Graph edges are the exact placed deck units. A route may use a common
    junction without traversing the separate middle-platform access spur.
    """
    graph={p['id']:[] for p in geometry['supports']};units={u['id']:u for u in geometry['units']}
    lookup={support['id']:support['coordinate_xyz_m'] for support in geometry['supports']}
    support_points={tuple(round(v,5) for v in p['coordinate_xyz_m']):p['id'] for p in geometry['supports']}
    route_kind={r['id']:r.get('kind') for r in geometry['routes']};platforms=[]
    for unit in geometry['units']:
        if len(unit['support_ids'])!=2 or unit['support_ids'][0]==unit['support_ids'][1]:raise ValueError('physical graph edge requires two distinct supports')
        number(unit['length_m'],'physical graph edge')
        for first,last in (unit['support_ids'],list(reversed(unit['support_ids']))):
            graph[first].append((last,unit['length_m'],unit['id']))
    for route in geometry['routes']:
        if route.get('kind')!='platform-interface-spur':continue
        point=route['points_xyz_m'][0];key=tuple(round(v,5) for v in point)
        platforms.append(dict(id=route['id'],line=route['source_line'],coordinate_xyz_m=point,support_id=support_points[key]))
    if len(platforms)<2 or len({v['support_id'] for v in platforms})!=len(platforms):raise ValueError('distinct physical platform interfaces required')
    pairs=[]
    for first,last in combinations(sorted(platforms,key=lambda x:x['id']),2):
        distances={first['support_id']:0.};previous={};todo=[(0.,first['support_id'])]
        while todo:
            distance,node=heapq.heappop(todo)
            if distance!=distances.get(node):continue
            if node==last['support_id']:break
            for next_node,length,identity in sorted(graph[node]):
                candidate=distance+length
                if candidate<distances.get(next_node,float('inf')):
                    distances[next_node]=candidate;previous[next_node]=(node,identity);heapq.heappush(todo,(candidate,next_node))
        if last['support_id'] not in distances:raise ValueError('disconnected proposed transfer graph')
        nodes=[last['support_id']];path=[]
        while nodes[-1]!=first['support_id']:
            node,identity=previous[nodes[-1]];path.append(identity);nodes.append(node)
        path.reverse();nodes.reverse();total=sum(units[key]['length_m'] for key in path)
        if len(set(path))!=len(path):raise ValueError('shortest path double-counts a physical unit')
        # Locate resting bays on exact path edges. Include endpoint rests only
        # once even when adjacent members share the physical junction.
        rest_positions={};prefix=0.
        for i,key in enumerate(path):
            unit=units[key]
            p,q=lookup[nodes[i]],lookup[nodes[i+1]];delta=[q[j]-p[j] for j in range(3)];norm=sum(v*v for v in delta)
            for rest in geometry['rest_bays']:
                point=rest['coordinate_xyz_m'];t=sum((point[j]-p[j])*delta[j] for j in range(3))/norm
                nearest=[p[j]+max(0.,min(1.,t))*delta[j] for j in range(3)]
                if -1e-7<=t<=1+1e-7 and math.dist(point,nearest)<1e-4:
                    rest_positions[rest['id']]=prefix+max(0.,min(1.,t))*unit['length_m']
            prefix+=unit['length_m']
        ordered=sorted(set([0.,total,*rest_positions.values()]));maximum_gap=max(q-p for p,q in zip(ordered,ordered[1:]))
        corridor=sum(units[key]['length_m'] for key in path if route_kind[units[key]['route_id']]=='offset-corridor')
        spur=sum(units[key]['length_m'] for key in path if route_kind[units[key]['route_id']]=='platform-interface-spur')
        pairs.append(dict(from_platform=first['id'],to_platform=last['id'],from_line=first['line'],to_line=last['line'],
            horizontal_walk_m=total,reference_corridor_edges_m=corridor,platform_interface_spurs_m=spur,
            physical_support_path=nodes,physical_unit_path=path,each_physical_unit_counted_once=True,
            platform_spurs_used=sorted({units[key]['route_id'] for key in path if route_kind[units[key]['route_id']]=='platform-interface-spur'}),
            walk_minutes={str(v):total/v/60 for v in a['walking_speeds_m_s']},
            rest_bay_ids=sorted(rest_positions,key=lambda key:(rest_positions[key],key)),rest_bays_on_path=len(rest_positions),
            maximum_distance_between_rest_or_endpoint_m=maximum_gap,
            adopted_rest_spacing_screen_pass=maximum_gap<=a['rest_interval_m']+1e-6,
            extra_rest_minutes_sensitivity=len(rest_positions)*a['flow']['rest_s_per_stop_sensitivity']/60,
            vertical_movements_lifts_queues_heat_and_service_wait_included=False,
            measured_grade_and_approved_platform_interfaces=False,accessible_route_accepted=False))
    return dict(platforms=platforms,pairs=pairs,platform_pair_count=len(pairs),
        minimum_horizontal_walk_m=min(row['horizontal_walk_m'] for row in pairs),
        maximum_horizontal_walk_m=max(row['horizontal_walk_m'] for row in pairs),
        all_pairs_rest_spacing_screen_pass=all(row['adopted_rest_spacing_screen_pass'] for row in pairs),
        geometry_scope='Shortest paths over proposed deck-unit/support graph at assumed common +8 m level; actual station interfaces and vertical access remain unqualified',**FLAGS)


def section(kind,width,a):
    r=a['reference_loads']
    if kind=='steel-twin-rhs':
        s=a['steel'];h=s['rhs_depth_m'];b=s['rhs_width_m'];t=s['rhs_wall_m'];n=s['girder_count']
        area=n*(b*h-(b-2*t)*(h-2*t))+width*s['deck_plate_m']
        inertia=n*(b*h**3-(b-2*t)*(h-2*t)**3)/12 # Noncomposite plate gets no flexural credit.
        return dict(kind=kind,stock_area_m2=area,gross_inertia_m4=inertia,section_modulus_m3=inertia/(h/2),
            structural_mass_kg_m=area*r['steel_density_kg_m3'],elastic_modulus_pa=r['steel_modulus_gpa']*1e9,
            stress_limit_pa=r['steel_yield_assumption_mpa']*1e6*r['steel_elastic_stress_fraction'],
            reinforcement_stock_kg_m=0.,section_verified=False)
    if kind!='concrete-twin-i':raise ValueError('declared section required')
    c=a['concrete'];h=c['girder_depth_m'];b=c['girder_flange_width_m'];f=c['girder_flange_m'];w=c['girder_web_m'];n=c['girder_count']
    girder_area=2*b*f+w*(h-2*f);slab_area=width*c['slab_m'];area=n*girder_area+slab_area
    # Explicit parallel-axis centroid recovery, rather than crediting full box depth.
    pieces=[(slab_area,h+c['slab_m']/2,width*c['slab_m']**3/12)]
    for _ in range(n):
        pieces.extend([(b*f,f/2,b*f**3/12),(w*(h-2*f),h/2,w*(h-2*f)**3/12),(b*f,h-f/2,b*f**3/12)])
    centroid=sum(area_i*y for area_i,y,_ in pieces)/area
    inertia=sum(i+area_i*(y-centroid)**2 for area_i,y,i in pieces)
    return dict(kind=kind,stock_area_m2=area,gross_inertia_m4=inertia,centroid_above_bottom_m=centroid,
        section_modulus_m3=inertia/max(centroid,h+c['slab_m']-centroid),
        structural_mass_kg_m=area*r['concrete_density_kg_m3'],elastic_modulus_pa=r['concrete_gross_modulus_gpa']*1e9,
        stress_limit_pa=None,reinforcement_stock_kg_m=area*c['reinforcement_stock_kg_m3'],
        cracked_stiffness_and_reinforcement_design_open=True,section_verified=False)


def structure(geometry,kind,a):
    width=geometry['clear_width_m'];s=section(kind,width,a);r=a['reference_loads'];g=r['gravity_m_s2'];rows=[]
    dead=s['structural_mass_kg_m']*g/1000+(r['canopy_dead_kpa']+r['wear_services_dead_kpa'])*width+2*r['parapet_dead_kn_m_per_side']
    live=r['pedestrian_udl_kpa']*width;wind=r['wind_pressure_kpa']*(2*r['parapet_height_m']+width)
    for unit in geometry['units']:
        length=unit['length_m'];udl=(dead+live)*1000;moment=udl*length**2/8
        deflection=5*udl*length**4/(384*s['elastic_modulus_pa']*s['gross_inertia_m4'])
        rows.append(dict(unit_id=unit['id'],span_m=length,dead_load_kn_m=dead,pedestrian_load_kn_m=live,
            unfactored_moment_kn_m=moment/1000,unfactored_shear_kn=udl*length/2000,
            elastic_gross_deflection_mm=deflection*1000,reference_deflection_limit_mm=length/r['deflection_span_divisor']*1000,
            gross_elastic_deflection_screen_pass=deflection<=length/r['deflection_span_divisor'],
            gross_elastic_stress_mpa=moment/s['section_modulus_m3']/1e6,
            steel_reference_elastic_stress_screen_pass=moment/s['section_modulus_m3']<=s['stress_limit_pa'] if s['stress_limit_pa'] else None,
            wind_horizontal_kn=wind*length,canopy_uplift_kn=r['wind_pressure_kpa']*width*length,
            handling_selfweight_moment_kn_m=s['structural_mass_kg_m']*g/1000*length**2/8*r['handling_dynamic_factor'],
            handling_and_erection_verified=False))
    # Bays are installed as complete spans in this alternative. A midspan
    # transport splice would require its own moment connection, so no fictitious
    # half-module lifting credit is taken.
    length=geometry['horizontal_length_m'];stock=s['structural_mass_kg_m']*length
    largest=max((u['length_m'] for u in geometry['units']),default=0.)
    return dict(kind=kind,section=s,bays=rows,total_structural_stock_kg=stock,
        reinforcement_stock_kg=s['reinforcement_stock_kg_m']*length,
        largest_complete_span_stock_lift_kg=largest*s['structural_mass_kg_m'],
        rest_bay_structure_stock_unquantified=True,canopy_parapet_connections_stock_unquantified=True,
        unfactored_dead_total_kn=dead*length,unfactored_pedestrian_total_kn=live*length,
        reference_wind_total_kn=wind*length,reference_canopy_uplift_total_kn=r['wind_pressure_kpa']*width*length,
        reference_load_combinations_implemented=False,rest_bay_cantilevers_analysed=False,
        fatigue_vibration_crowd_dynamics_seismic_soil_and_joints_analysed=False,**FLAGS)


def ramp(height,width,a):
    number(height,'rise');number(width,'ramp width');ac=a['access'];count=math.ceil(height/ac['maximum_rise_between_landings_m']);rise=height/count
    run=rise*ac['gradient_denominator'];points=[[0.,0.,0.]];units=[]
    for i in range(count):
        y=i*ac['ramp_lane_pitch_m'];start=[0. if i%2==0 else run,y,i*rise];end=[run if i%2==0 else 0.,y,(i+1)*rise]
        if i:points.append(start)
        points.append(end);units.append(dict(id='ramp-run-'+str(i+1),endpoints_xyz_m=[start,end],width_m=width,
            rise_m=rise,horizontal_run_m=run,gradient=rise/run))
    horizontal=count*run+(count-1)*ac['ramp_lane_pitch_m']+2*ac['end_landing_length_m']
    surface=count*math.hypot(run,rise)+(count-1)*ac['ramp_lane_pitch_m']+2*ac['end_landing_length_m']
    # Each parallel run occupies a separate lane; no same-height crossing or
    # headroom credit from stacked short flights is assumed.
    return dict(height_m=height,runs=units,centreline_xyz_m=points,intermediate_landings=count-1,
        end_landings=2,landing_clear_width_m=width,landing_length_m=ac['landing_length_m'],
        gradient_denominator=ac['gradient_denominator'],horizontal_length_m=horizontal,surface_length_m=surface,
        deck_area_m2=surface*width,footprint_bounds_xy_m=[[-ac['end_landing_length_m'],-width/2],
            [run+ac['end_landing_length_m'],(count-1)*ac['ramp_lane_pitch_m']+width/2]],
        footprint_area_m2=(run+2*ac['end_landing_length_m'])*((count-1)*ac['ramp_lane_pitch_m']+width),
        parallel_lanes_do_not_overlap=ac['ramp_lane_pitch_m']>=width,
        obstacles_and_ground_levels_accepted=False,independent_step_free_route_after_total_lift_power_loss=True,**FLAGS)


def queue(pulse_people,width,headway_s,a):
    """Conservative shared two-way fluid bottleneck; no hidden demand reduction."""
    for value,name in ((pulse_people,'pulse people'),(width,'clear width'),(headway_s,'headway')):number(value,name)
    f=a['flow'];capacity=max(0.,width-f['edge_allowance_m'])*f['two_way_flow_person_min_per_effective_m']/60
    repeats=f['repeat_pulses'];duration=f['pulse_duration_s'];horizon=int(repeats*headway_s);q=0.;arrivals=0.;served=0.;maximum=0.;boundaries=[];samples=[]
    for t in range(horizon):
        arrival=pulse_people/duration if (t%headway_s)<duration else 0.
        arrivals+=arrival;q+=arrival;maximum=max(maximum,q)
        out=min(q,capacity);q-=out;served+=out
        if (t+1)%int(headway_s)==0:boundaries.append(q)
        if t%10==0:samples.append(dict(time_s=t+1,queue_people=q,cumulative_arrivals=arrivals,cumulative_departures=served))
    residual=arrivals-served-q
    return dict(pulse_people=pulse_people,pulse_duration_s=duration,headway_s=headway_s,repeated_pulses=repeats,
        clear_width_m=width,shared_two_way_capacity_people_s=capacity,arrivals_people=arrivals,departures_people=served,
        final_queue_people=q,maximum_queue_people=maximum,before_next_pulse_queues_people=boundaries,
        maximum_queue_delay_bound_s=maximum/capacity if capacity else None,
        separate_waiting_area_m2=maximum*f['waiting_area_m2_per_person'],queue_area_includes_unobstructed_circulation=False,
        clears_each_headway=all(value<1e-6 for value in boundaries),conservation_residual_people=residual,
        observed_od_demand=False,pedestrian_microsimulation=False,samples=samples)


def lift_queue(pulse_people,height,count,outage,headway_s,a,*,total_power_loss=False):
    """FIFO wheelchair-party jobs; one batch per round trip on each lift."""
    for value,name in ((pulse_people,'pulse'),(height,'lift height'),(headway_s,'headway')):number(value,name)
    if type(count) is not int or type(outage) is not int or not 1<=count<=8 or not 0<=outage<=count:raise ValueError('bounded integer lift inventory/outage required')
    ac=a['access'];f=a['flow'];available=0 if total_power_loss else count-outage
    parties=math.ceil(pulse_people*ac['mobility_party_fraction_of_total_people'])
    cycle=2*height/ac['lift_speed_m_s']+ac['lift_round_trip_door_and_loading_s'];per_trip=ac['assumed_wheelchair_parties_per_trip']
    demand=[k*headway_s+i*f['pulse_duration_s']/parties for k in range(f['repeat_pulses']) for i in range(parties)]
    pending=list(demand);servers=[0.]*available;records=[]
    while pending and servers:
        server=min(range(available),key=lambda i:(servers[i],i));start=max(servers[server],pending[0]);ready=[v for v in pending if v<=start+1e-9]
        batch=min(per_trip,len(ready));members=pending[:batch];del pending[:batch]
        arrival_destination=start+cycle/2;servers[server]=start+cycle
        records.extend(dict(arrival_s=value,boarding_s=start,destination_s=arrival_destination,lift=server+1) for value in members)
    horizon=f['repeat_pulses']*headway_s;final=sum(row['destination_s']>horizon for row in records)+len(pending)
    maximum_wait=max((row['destination_s']-row['arrival_s'] for row in records),default=None)
    maximum_queue=max((sum(row['arrival_s']<=t<row['boarding_s'] for row in records)+sum(v<=t for v in pending) for t in demand),default=0)
    boundaries=[sum(row['arrival_s']<t<row['destination_s'] for row in records)+sum(v<t for v in pending)
        for t in [headway_s*k for k in range(1,f['repeat_pulses']+1)]]
    return dict(lifts_installed=count,lifts_available=available,lifts_failed=outage,total_power_loss=total_power_loss,
        wheelchair_parties_per_pulse=parties,people_per_party=ac['people_per_wheelchair_party'],
        wheelchair_parties_per_trip_assumption=per_trip,round_trip_s=cycle,total_parties=len(demand),
        served_or_scheduled_parties=len(records),unserved_or_after_horizon_parties=final,
        maximum_arrival_to_destination_s=maximum_wait,
        maximum_waiting_parties=maximum_queue,maximum_waiting_people=maximum_queue*ac['people_per_wheelchair_party'],
        separate_lift_waiting_area_m2=maximum_queue*ac['people_per_wheelchair_party']*f['waiting_area_m2_per_person'],
        parties_not_at_destination_before_next_pulse=boundaries,clears_each_headway=available>0 and not any(boundaries),
        assumed_step_free_route_available=available>0,clears_before_repeated_service_horizon=available>0 and final==0,
        independent_fire_evacuation_route=False,car_loading_and_rescue_qualified=False,
        common_power_fire_control_and_maintenance_failures_qualified=False,records=records)


def access_cores(routes,a):
    nodes={}
    for row in routes:
        if row.get('kind')!='offset-corridor':continue
        for point in (row['points_xyz_m'][0],row['points_xyz_m'][-1]):nodes.setdefault(tuple(round(v,5) for v in point),point)
    ac=a['access'];cores=[]
    for i,point in enumerate(nodes.values()):
        cores.append(dict(id='access-core-'+str(i+1),platform_interface_xyz_m=point,
            lift_shaft_bounds_xyz_m=[[point[0]+4.,point[1],0.],
                [point[0]+4.+ac['lift_shaft_width_m'],point[1]+ac['lift_shaft_depth_m'],point[2]]],
            lift_cabin_internal_m=[ac['lift_internal_width_m'],ac['lift_internal_depth_m']],
            lift_clear_door_m=ac['lift_clear_door_m'],independent_stair_width_m=ac['stair_clear_width_m'],
            stair_risers=math.ceil(point[2]/ac['stair_riser_m']),
            stair_tread_run_m=math.ceil(point[2]/ac['stair_riser_m'])*ac['stair_tread_m'],
            ramp_alternative=ramp(point[2],a['clear_widths_m'][0],a),lift_arrangement_qualified=False,
            stairs_alone_are_accessible=False,**FLAGS))
    return cores


def shared_site(concept,a):
    """Dimension an independent concourse and interfaces, not train tangents."""
    ac=a['access'];gallery_z=a['deck_level_m'];interfaces=[]
    for i,name in enumerate(concept['involved_lines']):
        # Explicit separate platform levels are assumptions; train clearances,
        # station tangents and live route profiles are not inherited.
        point=[-10.+i*10.,12.,gallery_z+6.*(i+1)];gallery=[point[0],0.,gallery_z]
        interfaces.append(dict(line=name,platform_interface_xyz_m=point,concourse_interface_xyz_m=gallery,
            horizontal_spur_m=12.,level_change_m=point[2]-gallery_z,through_lift_cabin_m=[1.6,2.1],
            independent_stairs_width_m=ac['stair_clear_width_m'],train_tangent_fitted=False))
    walks=[]
    for i,p in enumerate(interfaces):
        for q in interfaces[i+1:]:
            walks.append(dict(from_line=p['line'],to_line=q['line'],horizontal_walk_m=24.+abs(p['platform_interface_xyz_m'][0]-q['platform_interface_xyz_m'][0]),
                lift_height_up_m=q['level_change_m'],lift_height_down_m=p['level_change_m'],
                lift_wait_s=None,passenger_time_qualified=False))
    return dict(id=concept['id']+'-circulation-kit',source_concept_id=concept['id'],shared_hub_coordinate=concept['shared_hub_coordinate'],
        concourse_bounds_xyz_m=[[-20.,-8.,gallery_z],[max(20.,len(interfaces)*10.),8.,gallery_z]],
        gallery_area_m2=(max(20.,len(interfaces)*10.)+20.)*16.,interfaces=interfaces,
        computed_internal_walks=walks,compact_walk_is_now_geometric_but_assumed_interfaces=True,
        existing_platform_access_preserved=False,source_reference_guideways_reused=False,
        train_levels_tangents_curves_and_collision_clearances_qualified=False,selected=False,**FLAGS)


def schedule(geometry,a):
    bays=geometry['deck_bays'];supports=geometry['unique_support_positions']
    phases=[('survey','site/utility/ground/level survey',0.,None,['approved survey and ground records']),
        ('detail','connections, structural/access/fire details',0.,None,['reviewed calculations and drawings']),
        ('factory','fabrication / casting and dimensional QA',10.,'detail',['material trace, coupons, dimensional inspection']),
        ('strength','concrete reference strength development or weld NDT',28.,'factory',['measured strength or qualified weld inspection']),
        ('supports','independent support and foundation installations',math.ceil(supports/2),'survey',['ground design, setting-out, connection QA']),
        ('deliver','bounded delivery at six full spans/day',math.ceil(bays/6),'strength',['route, axle loads, lift points and transport survey']),
        ('erect','crane placement at four full spans/day',math.ceil(bays/4),'deliver',['crane-at-radius, wind and ground bearing checks']),
        ('connect','bearings, joints, parapets, shade and access cores',math.ceil(bays/4),'erect',['temporary stability and complete locked connections']),
        ('accept','survey, access, proof and functional tests',3.,'connect',['independent acceptance; all measurements unexecuted'])]
    return dict(phases=[dict(id=key,description=description,assumed_days=days,depends_on=[dep] if dep else [],
        hold_points=holds,executed=False) for key,description,days,dep,holds in phases],
        basis='Illustrative resources and strength age, not a contractor programme. Foundations and access cores have no accepted duration.',
        lifts=bays,complete_programme_days=None,manufacturing_release=False)


def costs(geometry,core_count,credit,a):
    rates=a['cost_sensitivities'];result=[]
    for tier in range(3):
        deck=geometry['total_deck_area_m2']*rates['deck_and_canopy_usd_m2'][tier]
        support=geometry['unique_support_positions']*rates['support_and_foundation_usd_position'][tier]
        for lift_count in a['access']['lift_counts_per_core']:
            lift=core_count*lift_count*rates['lift_installed_usd_each'][tier]
            flow_wait=queue(240,geometry['clear_width_m'],360.,a)['separate_waiting_area_m2']
            lift_wait=lift_queue(240,a['deck_level_m'],lift_count,1,360.,a)['separate_lift_waiting_area_m2']
            gallery_area=flow_wait+core_count*lift_wait;gallery=gallery_area*rates['queue_gallery_usd_m2']
            total=deck+support+lift+gallery
            result.append(dict(rate_tier=tier+1,lifts_per_core=lift_count,deck_canopy_target_usd=deck,
                support_foundation_target_usd=support,lift_target_usd=lift,partial_scope_target_usd=total,
                additional_queue_gallery_m2=gallery_area,queue_gallery_target_usd=gallery,
                queue_gallery_basis='240-person pulse / 360 s; full wheelchair-party pulse at every core; one lift unavailable; four pulses. A finite gallery does not repair a failed accessible route.',
                station_electrical_credit_usd=credit,partial_target_less_electrical_credit_usd=total-credit,
                savings_proved=False,complete_capex_usd=None))
    return dict(scenarios=result,rates_are_quotes=False,baseline_station_civil_removal_credit_usd=None,
        excludes=['rest-bay structural premium','lifted core and queue-gallery connection details','ramps and stairs','land/relocation and utilities',
            'ground-specific foundations and seismic design','power, backup, lighting, drainage and security','construction access and disruption',
            'fire strategy, approved evacuation, maintenance and renewals','passenger time, traffic/ridership and financing'],complete_cost_comparison=False)


@lru_cache(maxsize=2)
def _study(identity):
    before=json.loads(identity);a=load();hubs.verify();upstream=hubs.study()
    if len(upstream['variants'])>a['maximum_source_variants']:raise ValueError('upstream alternative bound exceeded')
    focus=next(row for row in upstream['variants'] if row['id']==a['focused_variant']);routes,datum=physical_routes(focus,a)
    cores=access_cores(routes,a);credit=focus['operating_and_cost_comparison']['gross_station_electrical_target_credit_usd']
    geometries=[kit_geometry(routes,width,a) for width in a['clear_widths_m']]
    transfer_walks=walking_matrix(geometries[0],a)
    flow=[queue(pulse,width,headway,a) for width in a['clear_widths_m'] for pulse in a['flow']['pulse_people'] for headway in a['flow']['headways_s']]
    lifts=[lift_queue(pulse,a['deck_level_m'],count,outage,headway,a) for count in a['access']['lift_counts_per_core']
        for outage in a['access']['lift_outages'] if outage<=count for pulse in a['flow']['pulse_people'] for headway in a['flow']['headways_s']]
    power=lift_queue(240,a['deck_level_m'],4,0,360.,a,total_power_loss=True)
    distances=[dict(route_id=row['id'],reference_horizontal_length_m=row['length_m'],
        physical_platform_to_platform_horizontal_length_m=row['length_m']+2*a['walkway_offset_east_m'],
        walk_minutes={str(v):(row['length_m']+2*a['walkway_offset_east_m'])/v/60 for v in a['walking_speeds_m_s']},
        rest_stops=max(0,math.ceil(row['length_m']/a['rest_interval_m'])-1),
        extra_rest_minutes_sensitivity=max(0,math.ceil(row['length_m']/a['rest_interval_m'])-1)*a['flow']['rest_s_per_stop_sensitivity']/60,
        heat_vertical_lift_queue_and_service_wait_included=False) for row in routes if row['kind']=='offset-corridor']
    result=dict(schema=SCHEMA,source_sha256=before,upstream_content_sha256=upstream['content_sha256'],assumptions=a,
        focused_variant_id=focus['id'],geographic_datum=datum,reference_walks=distances,
        platform_transfer_walk_matrix=transfer_walks,
        upstream_unique_reference_length_m=focus['independently_counted_unique_connector_length_m'],
        physical_local_projection_length_m=sum(r['length_m'] for r in routes if r['kind']=='offset-corridor'),
        additional_counted_platform_interface_length_m=sum(r['length_m'] for r in routes if r['kind']=='platform-interface-spur'),
        complete_access_horizontal_length_m=sum(r['length_m'] for r in routes),core_count=len(cores),access_cores=cores,
        alternatives=[dict(id='width-'+str(g['clear_width_m']),geometry=g,guideway_clearance=clearance(routes,g['clear_width_m'],a),
            structure_alternatives=[structure(g,k,a) for k in ('concrete-twin-i','steel-twin-rhs')],
            schedule=schedule(g,a),cost_sensitivities=costs(g,len(cores),credit,a),selected=False) for g in geometries],
        flow_scenarios=flow,lift_scenarios=lifts,total_lift_power_loss_negative_control=power,
        shared_site_circulation_alternatives=[shared_site(row,a) for row in upstream['coordinated_realignment_concepts']],
        decisions=dict(hub_merge_selected=False,default_city_modified=False,complete_cost_savings_proved=False,
            research_geometry_and_conservation_checks_complete=True,engineering_closure_complete=False),
        external_gates=['measured site/ground/levels, obstructions and land','observed OD pulses and reduced-mobility mix',
            'train tangents, vertical/horizontal profiles and guideway collisions at shared sites',
            'factored structural combinations, prestress/reinforcement, steel stability, vibration and fatigue',
            'actual cranes, transport, lifting inserts, bearings, joints and erection-stage stability',
            'certified lift performance, power/common-mode resilience and assisted rescue',
            'independently accepted fire/evacuation and accessible route','supplier quotes and complete economic comparison'],**FLAGS)
    if abs(result['physical_local_projection_length_m']-result['upstream_unique_reference_length_m'])>.1:
        raise ValueError('physical route takeoff differs from upstream reference')
    if before!=sources():raise ValueError('hub access sources changed during calculation')
    result['content_sha256']=sha256(encoded(result)).hexdigest();return encoded(result)


def study():return json.loads(_study(encoded(sources()).decode()))


def geometry_document(result):
    return dict(schema=SCHEMA,source_sha256=result['source_sha256'],geographic_datum=result['geographic_datum'],
        alternatives=[dict(id=row['id'],guideway_clearance=row['guideway_clearance'],**row['geometry']) for row in result['alternatives']],access_cores=result['access_cores'],
        platform_transfer_walk_matrix=result['platform_transfer_walk_matrix'],
        shared_site_circulation_alternatives=result['shared_site_circulation_alternatives'],**FLAGS)


def overview(result):
    g=result['alternatives'][0]['geometry'];points=[p for r in g['routes'] for p in r['points_xyz_m']]
    x0=min(p[0] for p in points);x1=max(p[0] for p in points);y0=min(p[1] for p in points);y1=max(p[1] for p in points)
    scale=min(600/max(x1-x0,1),610/max(y1-y0,1))
    def xy(p):return 55+(p[0]-x0)*scale,110+(y1-p[1])*scale
    rows=['<svg xmlns="http://www.w3.org/2000/svg" width="1300" height="850" viewBox="0 0 1300 850">',
        '<rect width="1300" height="850" fill="#f8fafc"/><g font-family="sans-serif" fill="#102030">',
        '<text x="30" y="36" font-size="25">Baghdad 031–040: manufactured access-kit alternatives</text>',
        '<text x="30" y="66" font-size="16">Located reference walkway geometry; no merged hub, site or structural approval.</text>']
    for route in g['routes']:
        if route.get('kind')=='offset-corridor':
            source=' '.join(f'{x:.2f},{y:.2f}' for x,y in map(xy,route['source_guideway_reference_xyz_m']))
            rows.append(f'<polyline points="{source}" fill="none" stroke="#94a3b8" stroke-width="2" stroke-dasharray="5 4"/>')
        coords=' '.join(f'{x:.2f},{y:.2f}' for x,y in map(xy,route['points_xyz_m']))
        rows.append(f'<polyline points="{coords}" fill="none" stroke="#0f766e" stroke-width="9"/>')
        x,y=xy(route['points_xyz_m'][-1]);rows.append(f'<text x="{x+10:.2f}" y="{y:.2f}" font-size="13">{route["source_line"]}</text>')
    for p in g['supports']:
        x,y=xy(p['coordinate_xyz_m']);rows.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="3.2" fill="#a16207"/>')
    for core in result['access_cores']:
        x,y=xy(core['platform_interface_xyz_m']);rows.append(f'<rect x="{x-6:.2f}" y="{y-6:.2f}" width="12" height="12" fill="#7c3aed"/>')
    matrix=result['platform_transfer_walk_matrix'];longest=matrix['maximum_horizontal_walk_m']
    text=[f'942 m corridor plus 36 m station-interface spurs',f'{g["deck_bays"]} deck bays; {g["unique_support_positions"]} unique support positions',
        f'{g["independent_bearing_seats"]} independently counted bearing seats',f'{len(g["rest_bays"])} recessed resting bays; clear route retained',
        f'{result["core_count"]} proposed access cores; datum +8 m assumed',
        'Three widths: 3.0 / 4.2 / 6.6 m; two stock sections',
        'All retained route bends receive support positions.',
        '12 m east offset; three counted platform spurs.',
        f'All platform pairs: {matrix["minimum_horizontal_walk_m"]:,.0f} to {longest:,.0f} m.',
        f'Longest: {longest/60:.2f} min at 1 m/s; {longest/.6/60:.2f} min at 0.6 m/s.',
        'Outer-to-outer path skips the middle-platform spur.',
        'Ramp alternative: sixteen separated 1:20 runs.',
        'Twin lifts are not automatically outage-resilient.',
        'Four-lift case still fails total common power loss.',
        'Crowd pulses and waiting areas are explicit assumptions.',
        'New shared-site circulation kits do not fit train tangents.',
        'Loads are unfactored UK-informed research benchmarks.',
        'Foundations, connections and fire strategy remain open.']
    for i,line in enumerate(text):rows.append(f'<text x="670" y="{125+i*36}" font-size="16">{line}</text>')
    rows.append('<text x="30" y="815" font-size="14">Grey: source guideway. Green: translated access deck and spurs. Amber: preliminary supports. Purple: access cores.</text></g></svg>')
    return '\n'.join(rows)+'\n'


def assembly_svg(result):
    phases=result['alternatives'][0]['schedule']['phases'];rows=['<svg xmlns="http://www.w3.org/2000/svg" width="1300" height="700" viewBox="0 0 1300 700">',
        '<rect width="1300" height="700" fill="#f8fafc"/><g font-family="sans-serif" fill="#102030">',
        '<text x="35" y="38" font-size="24">Access-kit erection sequence and unexecuted hold points</text>',
        '<text x="35" y="67" font-size="16">Planning illustration only; no construction or proof test has been performed.</text>']
    for i,phase in enumerate(phases):
        y=100+i*60;rows.extend([f'<rect x="35" y="{y}" width="260" height="43" rx="5" fill="#cceae2"/>',
            f'<text x="48" y="{y+26}" font-size="16">{i+1}. {phase["id"]} · assumed {phase["assumed_days"]:g} days</text>',
            f'<text x="315" y="{y+19}" font-size="15">{phase["description"]}</text>',
            f'<text x="315" y="{y+39}" font-size="13">HOLD: {phase["hold_points"][0]}</text>'])
    rows.append('</g></svg>');return '\n'.join(rows)+'\n'


def readme(result):
    g=result['alternatives'][0]['geometry'];r=result['access_cores'][0]['ramp_alternative']
    rows=['# Baghdad physical interchange access-kit study','',
        '![Located walkways and access cores](overview.svg)','',
        f'The 031–040 / line 9 midpoint alternative retains {result["physical_local_projection_length_m"]:,.2f} m of geographically defined reference corridor. Its two reference arms remain approximately 471 m each. An independent deck is translated 12 m east of that train alignment, and three counted 12 m platform-interface spurs add 36 m: {g["horizontal_length_m"]:,.2f} m total. The middle-to-outer walks are approximately 495 m, while the outer-to-outer walk is approximately 966 m before vertical movement. The latter uses both corridor arms and two outer spurs; it skips the middle-platform spur rather than adding the two advertised arm walks. The guideway-separation screen uses an assumed envelope; the spurs still require approved side-platform/level geometry and the site is unchecked. {g["deck_bays"]} preliminary deck bays, {g["unique_support_positions"]} support positions and {g["independent_bearing_seats"]} bearing seats are explicitly placed. Every retained bend receives a support. The common central bearing group has no qualified foundation or cost credit. No hub is selected and the current city reference is unchanged.','',
        'All three platform-pair shortest paths are solved over the placed deck-unit/support graph. The longest transfer is about 16.10 minutes at 1 m/s or 26.83 minutes at 0.6 m/s, before rests, vertical access, queues, heat or service waiting. One additional recessed resting bay is counted at the central junction so that the two independent 50 m arm patterns do not leave a 100 m rest gap. Rest-spacing calculations include every path and its counted interface spurs; they do not establish an accepted accessible route.','',
        '| Platform pair | Shortest physical walk m | At 1 m/s min | At 0.6 m/s min | Rest bays on path | Maximum rest/endpoint gap m |',
        '|---|---:|---:|---:|---:|---:|']
    for pair in result['platform_transfer_walk_matrix']['pairs']:
        rows.append(f'| {pair["from_line"]} ↔ {pair["to_line"]} | {pair["horizontal_walk_m"]:,.2f} | {pair["walk_minutes"]["1.0"]:.2f} | {pair["walk_minutes"]["0.6"]:.2f} | {pair["rest_bays_on_path"]} | {pair["maximum_distance_between_rest_or_endpoint_m"]:.2f} |')
    rows += ['',
        'Three clear widths and concrete twin-I / steel twin-RHS stock sections are compared. Quantities include clear deck, recessed resting bays, shade, parapets, stock mass and full-span lifting weights. Gross elastic demand, wind/uplift and handling reference loads are calculated. Concrete cracking/reinforcement/prestress, steel local buckling, crowd vibration, fatigue, seismic, joints, foundations, lifting and erection stability require separate acceptance. A gross section result does not close these gates.','',
        f'Three separate ground/platform access cores use an assumed +8 m datum. A 1:20 ramp is physically laid out as {len(r["runs"])} separate parallel runs with landings: approximately {r["surface_length_m"]:,.1f} m surface length and {r["footprint_area_m2"]:,.1f} m² bounding footprint per core. Land and obstructions have not been checked. Lift alternatives have one, two or four cars per core plus independent stairs. Stairs alone do not provide a step-free route. An operating lift is not presumed to be an evacuation lift.','',
        'Deterministic queues retain 120/240/480-person, 60-second transfer pulses, repeated at 180/360-second headways. Shared two-way capacity is a declared benchmark, not an observed Baghdad demand. Waiting-area quantities are additional to unobstructed circulation. FIFO wheelchair-party lift scenarios include one-car outage and complete common power loss. A second lift does not guarantee that the surviving car clears a burst; the complete power-loss case is inaccessible without an independent route. These tests are fluid/queue calculations, not agent-based crowd or fire simulations.','',
        '| Clear width m | Deck including rest bays m² | Support positions | Lowest partial target USD | Highest partial target USD |',
        '|---:|---:|---:|---:|---:|']
    for row in result['alternatives']:
        geo=row['geometry'];values=[s['partial_scope_target_usd'] for s in row['cost_sensitivities']['scenarios']]
        rows.append(f'| {geo["clear_width_m"]:g} | {geo["total_deck_area_m2"]:,.1f} | {geo["unique_support_positions"]} | {min(values):,.0f} | {max(values):,.0f} |')
    rows+=['','Every rate is an unquoted sensitivity. The $3,075,000 station-electrical target credit is kept separate. Additional queue-gallery area is priced for a stated 240-person/360-second, one-lift-outage scenario at every core; four finite bursts do not prove long-term stability or repair an inaccessible route. Removed station civil, ramps/stairs, actual core/gallery connections, land, actual foundations, utilities, fire/power systems, construction access, renewals, passenger time and financing remain outside the partial total. A negative partial delta does not establish savings.','',
        'Seven shared-site concepts now have explicit concourse bounds, level-separated platform interfaces, lift/stair interfaces and computed internal horizontal walks. These are independent circulation layouts with assumed levels. They do not fit the required 350 m train tangents, preserve former boarding access, qualify train clearances or inherit old guideway civil prices.','',
        '![Factory and erection planning with hold points](assembly.svg)','',
        '[Complete calculations](study.json.gz) · [Physical geometry units](geometry.json) · [Source/payload receipt](manifest.json)','',
        'UK primary references inform research assumptions only; Iraqi accessibility, structural and fire acceptance remains open:','']
    rows += ['- ['+v['title']+']('+v['url']+'): '+v['use'] for v in result['assumptions']['external_guidance']]
    return '\n'.join(rows)+'\n'


def publish(output=OUTPUT):
    result=study();output=Path(output)
    if output.exists() and any(p.is_symlink() or p.name not in FILES|{'manifest.json'} for p in output.iterdir()):
        raise ValueError('unowned or linked access packet file')
    raw=encoded(result);compressed=gzip.compress(raw,mtime=0)
    if len(raw)>MAX_RAW or len(compressed)>MAX_COMPRESSED:raise ValueError('bounded access payload exceeded')
    if result['source_sha256']!=sources():raise ValueError('access sources changed before publication')
    output.mkdir(parents=True,exist_ok=True)
    (output/'study.json.gz').write_bytes(compressed);(output/'geometry.json').write_text(json.dumps(geometry_document(result),sort_keys=True,indent=2)+'\n')
    (output/'overview.svg').write_text(overview(result));(output/'assembly.svg').write_text(assembly_svg(result));(output/'README.md').write_text(readme(result))
    manifest=dict(schema=SCHEMA,source_sha256=result['source_sha256'],content_sha256=result['content_sha256'],
        files_sha256={name:digest(output/name) for name in sorted(FILES)},raw_bytes=len(raw),compressed_bytes=len(compressed),**FLAGS)
    (output/'manifest.json').write_text(json.dumps(manifest,sort_keys=True,indent=2)+'\n');verify(output);return manifest


def verify(output=OUTPUT):
    output=Path(output)
    if set(p.name for p in output.iterdir())!=FILES|{'manifest.json'} or any(p.is_symlink() for p in output.iterdir()):raise ValueError('access packet inventory differs')
    manifest=json.loads((output/'manifest.json').read_bytes())
    if manifest['schema']!=SCHEMA or any(manifest.get(k) is not False for k in FLAGS):raise ValueError('access packet may not claim release')
    if set(manifest['files_sha256'])!=FILES or any(digest(output/name)!=value for name,value in manifest['files_sha256'].items()):raise ValueError('access payload checksum differs')
    if manifest['source_sha256']!=sources():raise ValueError('access source receipt is stale')
    compressed=(output/'study.json.gz').read_bytes()
    if len(compressed)>MAX_COMPRESSED:raise ValueError('compressed access budget exceeded')
    with gzip.GzipFile(fileobj=io.BytesIO(compressed)) as stream:raw=stream.read(MAX_RAW+1)
    if len(raw)>MAX_RAW or len(raw)!=manifest['raw_bytes'] or len(compressed)!=manifest['compressed_bytes']:raise ValueError('raw access budget/size differs')
    expected=study()
    if raw!=encoded(expected) or manifest['content_sha256']!=expected['content_sha256']:raise ValueError('access recalculated content differs')
    if (json.loads((output/'geometry.json').read_bytes())!=geometry_document(expected) or (output/'overview.svg').read_text()!=overview(expected)
            or (output/'assembly.svg').read_text()!=assembly_svg(expected) or (output/'README.md').read_text()!=readme(expected)):
        raise ValueError('access presentation differs from exact calculations')
    return manifest


def read_summary(output=OUTPUT):
    verify(output);result=study();g=result['alternatives'][0]['geometry']
    return dict(schema=SCHEMA,focused_variant_id=result['focused_variant_id'],physical_reference_length_m=g['horizontal_length_m'],
        platform_pair_count=result['platform_transfer_walk_matrix']['platform_pair_count'],
        maximum_platform_transfer_walk_m=result['platform_transfer_walk_matrix']['maximum_horizontal_walk_m'],
        minimum_platform_transfer_walk_m=result['platform_transfer_walk_matrix']['minimum_horizontal_walk_m'],
        deck_bays=g['deck_bays'],unique_support_positions=g['unique_support_positions'],bearing_seats=g['independent_bearing_seats'],
        access_cores=result['core_count'],width_alternatives=len(result['alternatives']),stock_sections=2,
        flow_scenarios=len(result['flow_scenarios']),lift_scenarios=len(result['lift_scenarios']),
        shared_site_circulation_alternatives=len(result['shared_site_circulation_alternatives']),hub_selected=False,**FLAGS)
