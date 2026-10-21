"""Bounded unselected interchange/access studies on unchanged train guideways."""
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
from itertools import combinations, product
import gzip
import io
import json
import math
from pathlib import Path
import tomllib

ROOT=Path(__file__).resolve().parents[2]
from engineering.ferrite_maglev import model,cities,operating_plan as op,manufacturing

INPUT=Path(__file__).with_name('interchange-hubs.toml')
OUTPUT=ROOT/'docs/design-engine/ferrite-maglev/interchange-hubs'
CITY_ROOT=ROOT/'cities/catalogue/west-asia/Iraq/Baghdad'
TEST=ROOT/'engineering/analysis/tests/test_ferrite_maglev_interchange_hubs.py'
MAX_RAW=20*1024*1024
MAX_COMPRESSED=4*1024*1024
FILES={'study.json.gz','overview.svg','README.md'}
FLAGS={**model.FLAGS,'engineering_accepted':False}
COMPONENTS=('repeat_fleet_allowance_usd','ordinary_elevated_allowance_usd','terminal_civil_allowance_usd',
    'station_electrical_allowance_usd','conditional_foundation_increment_usd','booster_electrical_allowance_usd',
    'booster_mount_allowance_usd','rescue_kit_allowance_usd')


def load():
    a=tomllib.loads(INPUT.read_text())
    if a['schema']!='osr-interchange-hub-investigation/1' or a['guideway_rerouting_allowed'] is not False:
        raise ValueError('fixed-guideway study required')
    if not 500<=a['minimum_pair_spacing_m']<a['maximum_pair_spacing_m']<=1500:
        raise ValueError('bounded pair search required')
    if (type(a['maximum_network_alternatives']) is not int or type(a['maximum_pair_variants']) is not int
            or not 1<=a['maximum_network_alternatives']<=32 or not 1<=a['maximum_pair_variants']<=40):
        raise ValueError('bounded scenario count required')
    if any(a[k] is not False for k in ('site_approval','costs_are_quotes')):raise ValueError('unapproved study required')
    if a['city']!='Baghdad' or a['original_crossline_boarding_platforms_preserved'] is not True:raise ValueError('retained Baghdad boarding records required')
    bounds={'maximum_merged_component_extent_m':(100,2000),'compact_site_extent_m':(1,200),'long_walk_warning_m':(100,1500),
        'connector_clear_width_m':(2.2,15),'connector_span_m':(5,50),'rest_interval_m':(5,50)}
    for key,(lo,hi) in bounds.items():
        if type(a[key]) not in (int,float) or not math.isfinite(a[key]) or not lo<=a[key]<=hi:raise ValueError('bounded '+key+' required')
    if not isinstance(a['walk_speeds_m_s'],list) or not 1<=len(a['walk_speeds_m_s'])<=4:raise ValueError('bounded walking sensitivities required')
    for speed in a['walk_speeds_m_s']:
        if type(speed) not in (int,float) or not math.isfinite(speed) or not .3<=speed<=2:raise ValueError('bounded walking speed required')
    return a


def encoded(value):return json.dumps(value,sort_keys=True,allow_nan=False,separators=(',',':')).encode()
def digest(path):return sha256(Path(path).read_bytes()).hexdigest()


def source_snapshot(city_root):
    paths={*cities.calculation_dependencies(),Path(cities.__file__),cities.ASSUMPTIONS,model.INPUT,model.POLICY,
        Path(model.__file__),manufacturing.INPUT,Path(manufacturing.__file__),ROOT/'VERSION',INPUT,Path(__file__),
        city_root/'city.json',city_root/'baghdad.corridor.geojson',TEST,
        city_root/'engineering/maglev/summary.json',city_root/'engineering/maglev/manufacturing.json'}
    return {str(p.relative_to(ROOT)):digest(p) for p in sorted(paths)}


def source_paths():
    return [ROOT/name for name in source_snapshot(CITY_ROOT)]


def interval_union(intervals):
    result=[]
    for lo,hi in sorted((min(x),max(x)) for x in intervals):
        if hi-lo<1e-8:continue
        if result and lo<=result[-1][1]+1e-8:result[-1][1]=max(hi,result[-1][1])
        else:result.append([lo,hi])
    return result


def bridge_quantities(length,a):
    if not math.isfinite(length) or length<0:raise ValueError('finite nonnegative connector length required')
    spans=math.ceil(max(0.,length-1e-9)/a['connector_span_m'])
    return dict(reference_horizontal_length_m=length,assumed_clear_width_m=a['connector_clear_width_m'],
        deck_area_m2=length*a['connector_clear_width_m'],shade_roof_area_m2=length*a['connector_clear_width_m'],
        span_modules=spans,independent_support_positions=spans+1 if spans else 0,
        parapet_length_m=2*length,interior_rest_positions=max(0,math.ceil(length/a['rest_interval_m'])-1),
        foundations_selected=False,actual_level_changes_m=None,actual_approved_accessible_length_m=None,
        passenger_capacity_qualified=False,capex_usd=None,**FLAGS)


def connector_quantities(components,a):
    """Count separate bridge components without joining their end supports."""
    values=[];ids=set()
    for component in components:
        if component['id'] in ids:raise ValueError('duplicate connector component identity')
        ids.add(component['id']);quantity=bridge_quantities(component['length_m'],a)
        if component['length_m']>1e-8:values.append(dict(component,quantity_screen=quantity))
    result=bridge_quantities(0.,a)
    fields=('reference_horizontal_length_m','deck_area_m2','shade_roof_area_m2','span_modules',
        'independent_support_positions','parapet_length_m','interior_rest_positions')
    for field in fields:result[field]=sum(component['quantity_screen'][field] for component in values)
    return dict(result,components=values,shared_end_support_or_foundation_credit=False,
        counting_basis='Each merged trunk interval on each line and each unique nonzero lateral branch is counted independently; intersection support duplication is conservative until physical joints/foundations are designed')


def walking_times(length,a):
    return {str(v):length/v/60 for v in a['walk_speeds_m_s']}


def reference_path(path,start,end):
    lo,hi=sorted((start,end));first=op.point_at(path,lo);last=op.point_at(path,hi)
    coordinates=[[first['lon'],first['lat']],*[p[:2] for s,p in zip(path['cumulative_m'],path['points']) if lo<s<hi],
        [last['lon'],last['lat']]]
    return coordinates if start<=end else list(reversed(coordinates))


def disjoint_sets(edges):
    """Complete finite matching enumeration; no source interchange used twice."""
    choices=[]
    for count in range(len(edges)+1):
        for subset in combinations(edges,count):
            ids=[hub for edge in subset for hub in edge['hub_ids']]
            if len(set(ids))==len(ids):choices.append([edge['id'] for edge in subset])
    return sorted(choices,key=lambda row:(-len(row),row))


def pair_edges(context):
    a=context['a'];pairs={};terminal=[]
    for name,entry in context['lines'].items():
        for conflict in entry['plan']['spacing_conflicts']:
            first=[x for x in conflict['from_nodes'] if x.startswith('interchange-')]
            last=[x for x in conflict['to_nodes'] if x.startswith('interchange-')]
            if len(first)!=1 or len(last)!=1:
                terminal.append(dict(line=name,kind='terminal-transfer-spacing',conflict=conflict,
                    connector_capex_usd=None,terminal_loop_datum_may_not_move_without_new_geometry=True,**FLAGS));continue
            if not a['minimum_pair_spacing_m']<=conflict['distance_m']<=a['maximum_pair_spacing_m']:continue
            key=tuple(sorted((first[0],last[0])));identity='pair-'+key[0].split('-')[-1]+'-'+key[1].split('-')[-1]
            edge=pairs.setdefault(key,dict(id=identity,hub_ids=list(key),shared_line_adjacencies=[],
                source_hubs=[deepcopy(context['hubs'][h]) for h in key]))
            edge['shared_line_adjacencies'].append(dict(line=name,from_hub=first[0],to_hub=last[0],
                along_line_distance_m=conflict['distance_m']))
    return sorted(pairs.values(),key=lambda x:x['id']),terminal


def geometry_variant(context,edge,adjacency,placement):
    a=context['a'];name=adjacency['line'];entry=context['lines'][name];path=entry['path']
    projections={h['id']:h for h in entry['plan']['transfer_hubs']}
    sa=projections[adjacency['from_hub']]['s_m'];sb=projections[adjacency['to_hub']]['s_m']
    if sb<sa:sb+=path['length_m']
    centre={'midpoint':(sa+sb)/2,'endpoint-a':sa,'endpoint-b':sb}[placement]%path['length_m']
    point=op.point_at(path,centre);connectors=[];intervals=[];branches={}
    source_platforms=[deepcopy(context['stations'][pid]) for h in edge['source_hubs'] for pid in h['platforms']]
    for platform in source_platforms:
        if platform['line']==name:continue
        projected=op.project_crossing(path,platform['lon'],platform['lat']);s=projected['s_m']
        # All retained candidate pairs lie away from the ring wrap. Refuse to
        # disguise a wrap crossing with a long unwrapped straight connector.
        if abs(s-centre)>path['length_m']/2 and entry['line']['shape']=='ring':
            raise ValueError('connector ring wrap needs an explicit geographic path')
        along=abs(s-centre);lateral=projected['crossing_projection_offset_m'];length=along+lateral
        intervals.append([s,centre]);coordinates=reference_path(path,centre,s)
        coordinates.append([platform['lon'],platform['lat']])
        direct=op.distance([point['lon'],point['lat']],[platform['lon'],platform['lat']])
        if direct>length+.1:raise ValueError('reference connector shorter than geodesic lower bound')
        branch=(round(s,6),round(platform['lon'],9),round(platform['lat'],9));branches[branch]=lateral
        connectors.append(dict(id=edge['id']+'-'+name+'-'+placement+'-'+platform['id'],
            source_platform_id=platform['id'],source_platform_line=platform['line'],
            source_coordinate=[platform['lon'],platform['lat']],proposed_shared_line_stop_coordinate=[point['lon'],point['lat']],
            retained_guideway_reference_coordinates=coordinates,reference_horizontal_route_length_m=length,
            along_shared_line_m=along,lateral_reference_branch_m=lateral,geodesic_lower_bound_m=direct,
            free_flow_walk_minutes=walking_times(length,a),excludes_vertical_queues_rests_heat_and_service_wait=True,
            original_crossline_boarding_platform_retained=True,accessible_path_approved=False,obstacles_accepted=False,
            bridge_quantity_screen=bridge_quantities(length,a),capex_usd=None,**FLAGS))
    merged_intervals=interval_union(intervals);trunk=sum(hi-lo for lo,hi in merged_intervals);lateral=sum(branches.values())
    components=[dict(id=f'{name}-trunk-{i+1}',kind='merged-shared-line-trunk',line=name,
        interval_m=[lo,hi],length_m=hi-lo) for i,(lo,hi) in enumerate(merged_intervals)]
    components.extend(dict(id=f'{name}-lateral-{i+1}',kind='independent-lateral-branch',line=name,
        projected_s_m=key[0],source_coordinate=list(key[1:]),length_m=value) for i,(key,value) in enumerate(sorted(branches.items())) if value>1e-8)
    maximum=max((v['reference_horizontal_route_length_m'] for v in connectors),default=0.)
    diameter=max(op.distance([p['lon'],p['lat']],[q['lon'],q['lat']]) for p in source_platforms for q in source_platforms)
    return dict(id=edge['id']+'/'+name+'/'+placement,kind='extended-transfer-complex-investigation',pair_id=edge['id'],
        hub_ids=edge['hub_ids'],shared_line=name,placement=placement,new_shared_line_stop_s_m=centre,
        new_shared_line_stop_coordinate=[point['lon'],point['lat']],source_platform_records=source_platforms,
        original_crossline_boarding_platforms_preserved=True,original_shared_line_platform_ids_retained_as_access_records=True,
        train_guideways_changed=False,train_routing_switches=0,source_platform_geodesic_diameter_m=diameter,
        true_compact_hub_geometry_demonstrated=diameter<=a['compact_site_extent_m'],
        merge_component_extent_m=max(sb-sa,diameter),component_extent_screen_pass=max(sb-sa,diameter)<=a['maximum_merged_component_extent_m'],
        maximum_reference_access_arm_m=maximum,long_walk_penalty=maximum>a['long_walk_warning_m'],
        maximum_reference_access_minutes=walking_times(maximum,a),connectors=connectors,
        maximum_crossline_platform_to_platform_via_hub_reference_walk_m=max((p['reference_horizontal_route_length_m']+q['reference_horizontal_route_length_m']
            for i,p in enumerate(connectors) for q in connectors[i+1:]),default=0.),
        connector_trunk_intervals_m=merged_intervals,connector_lateral_branches_m=lateral,
        independently_counted_unique_connector_length_m=trunk+lateral,
        connector_unique_quantity_screen=connector_quantities(components,a),
        crossline_to_crossline_walk_requires_both_arms=True,original_hub_ids_and_access_records_preserved=True,
        network_route_approved=False,passenger_transfer_demand_known=False,complete_delta_cost_usd=None,**FLAGS)


def altered_line(context,name,variants):
    entry=context['lines'][name];plan=deepcopy(entry['plan']);line=entry['line'];path=entry['path'];f=entry['formation'];c=context['c']
    stops=plan['stations'];seen=set()
    for v in variants:
        hub_ids=set(v['hub_ids'])
        if seen&hub_ids:raise ValueError('overlapping interchange merges are forbidden')
        seen|=hub_ids
        matched=[s for s in stops if hub_ids&set(s['mandatory_junction_ids'])]
        if len(matched)!=2:raise ValueError('two distinct current boarding stops required for pair consolidation')
        source_ids={s['id'] for s in matched};remaining=[s for s in stops if s['id'] not in source_ids]
        centre=v['new_shared_line_stop_s_m'];node=dict(id='proposal-'+v['id'].replace('/','-'),line=name,s_m=centre,**op.point_at(path,centre),
            passenger_stop=True,mandatory_junction_ids=sorted(hub_ids),retained_access_station_ids=[],
            site_approved=False,platform_length_m=f['overall_length_assumption_m']+10.,platform_is_proposed=True)
        remaining.append(node);stops=sorted(remaining,key=lambda row:row['s_m'])
    for s in stops:
        s['retained_access_station_ids']=[]
        for key in ('power_winding_length_m','power_winding_start_m','power_winding_end_m'):s.pop(key,None)
    assignments=[];length=path['length_m'];ratio=length/line['length_m']
    for retained in entry['retained']:
        position=retained['s_m']*ratio
        def separation(stop):
            delta=abs(stop['s_m']-position)
            return min(delta,length-delta) if line['shape']=='ring' else delta
        target=min(stops,key=separation);offset=separation(target);target['retained_access_station_ids'].append(retained['id'])
        assignments.append(dict(retained_station_id=retained['id'],operating_station_id=target['id'],retained_station=deepcopy(retained),
            along_route_access_offset_m=offset,catchment_connection_designed=False,retained_location_served_exactly=offset<.01))
    gaps=[q['s_m']-p['s_m'] for p,q in zip(stops,stops[1:])]
    if line['shape']=='ring':gaps.append(length-stops[-1]['s_m']+stops[0]['s_m'])
    trips=[op.wide_trip(c,f,value,service_class='urban') for value in gaps]
    conflicts=[dict(kind='proposed-layout-spacing-conflict',leg=i+1,distance_m=value,
        minimum_m=plan['minimum_passenger_spacing_m'],maximum_m=plan['policy']['maximum_mainline_spacing_m'],**FLAGS)
        for i,value in enumerate(gaps) if not plan['minimum_passenger_spacing_m']<=value<=plan['policy']['maximum_mainline_spacing_m']]
    plan.update(stations=stops,trips=trips,retained_station_assignments=assignments,operating_station_count=len(stops),
        spacing_conflicts=conflicts,passenger_spacing_screen_pass=not conflicts,
        flat_mainline_screen_pass=all(v['kinematic_screen_pass'] for v in trips),
        proposed_interchange_consolidations=[v['id'] for v in variants],
        average_passenger_spacing_m=sum(gaps)/len(gaps),**op.physical_installations(c,f,line,path,stops,trips))
    result=cities.operating_line_plan(c,context['city_assumptions'],f,line,line['service'],plan)
    if {r['retained_station_id'] for r in assignments}!={r['id'] for r in entry['retained']}:raise ValueError('access record lost')
    return result


def base_bill(context,lines,route_km=0.):
    return next(r for r in manufacturing.city_programme(context['c'],context['costs'],lines,route_km)['scenarios'] if r['scenario']=='base')


def line_screen(result):
    plan=result['operating_plan'];trips=plan['trips']
    return dict(line=result['line'],operating_stops=len(result['stations']),flat_all_load_motion_rating_pass=not result['kinematic_holds'],
        kinematic_holds=result['kinematic_holds'],spacing_conflicts=plan['spacing_conflicts'],
        protected_headway_s=result['selected_peak_headway_seconds'],source_target_headway_s=result['retained_peak_headway_seconds'],
        aw2_capacity_per_direction_hour=result['aw2_capacity_per_direction_hour'],source_aw2_capacity_per_direction_hour=result['source_aw2_capacity_per_direction_hour'],
        capacity_target_met=result['retained_capacity_target_met'],trainsets=result['fleet']['total'],dwell_s=result['charging']['dwell_seconds'],
        service_energy_screen_pass=all(t['service_energy_screen_pass'] for t in trips),
        maximum_leg_m=max(t['distance_m'] for t in trips),leg_distances_m=[t['distance_m'] for t in trips],
        leg_duties=[dict(distance_m=t['distance_m'],runtime_s=t['runtime_s'],propulsion_topology=t['propulsion_topology'],
            all_load_motion_rating_pass=t['kinematic_screen_pass'],services_reserve_and_replenishment_pass=t['service_energy_screen_pass']) for t in trips],
        booster_zones=[dict(id=z['id'],length_m_per_direction=z['length_m_per_direction'],s_m=z['s_m'],directions=z['directions']) for z in plan['powered_top_up_zones']],
        qualified_operating_design=None,**FLAGS)


def compare(context,variants,identity):
    by_line={}
    used=[]
    for variant in variants:
        used.extend(variant['hub_ids']);by_line.setdefault(variant['shared_line'],[]).append(variant)
    if len(used)!=len(set(used)):raise ValueError('network alternative double-counts a merged interchange')
    changes=[];delta={key:0. for key in COMPONENTS};residual_stop_count=0
    for name,proposals in sorted(by_line.items()):
        result=altered_line(context,name,proposals);before=context['lines'][name]['compiled'];old=base_bill(context,[before]);new=base_bill(context,[result])
        component_delta={key:new[key]-old[key] for key in COMPONENTS}
        for key,value in component_delta.items():delta[key]+=value
        residual_stop_count+=len(result['stations'])-len(before['stations'])
        changes.append(dict(line=name,before=line_screen(before),after=line_screen(result),priced_component_delta_usd=component_delta,
            retained_access_ids_preserved=True,unaffected_lines_and_original_crossline_platforms_unchanged=True,
            fixed_guideway_and_terminal_loop_geometry_changed=False))
    referenced=[x for v in variants for x in v['connectors']];trunks={};laterals={}
    for v in variants:
        trunks.setdefault(v['shared_line'],[]).extend(v['connector_trunk_intervals_m'])
        for connector in v['connectors']:
            key=(v['shared_line'],tuple(connector['source_coordinate']))
            laterals[key]=connector['lateral_reference_branch_m']
    connector_length=sum(sum(hi-lo for lo,hi in interval_union(values)) for values in trunks.values())+sum(laterals.values())
    components=[dict(id=f'{name}-trunk-{i+1}',kind='merged-shared-line-trunk',line=name,interval_m=[lo,hi],length_m=hi-lo)
        for name,values in sorted(trunks.items()) for i,(lo,hi) in enumerate(interval_union(values))]
    components.extend(dict(id=f'{key[0]}-lateral-{i+1}',kind='independent-lateral-branch',line=key[0],
        source_coordinate=list(key[1]),length_m=value) for i,(key,value) in enumerate(sorted(laterals.items())) if value>1e-8)
    capacity_not_lower=all(change['after']['aw2_capacity_per_direction_hour']>=change['before']['aw2_capacity_per_direction_hour'] for change in changes)
    subtotal_delta=sum(delta.values());max_arm=max((c['reference_horizontal_route_length_m'] for c in referenced),default=0.)
    baseline_conflicts=sum(len(entry['plan']['spacing_conflicts']) for entry in context['lines'].values())
    old_affected=sum(len(context['lines'][name]['plan']['spacing_conflicts']) for name in by_line)
    new_affected=sum(len(change['after']['spacing_conflicts']) for change in changes)
    gross_credit=max(0.,-delta['station_electrical_allowance_usd'])
    new_booster=max(0.,delta['booster_electrical_allowance_usd'])+max(0.,delta['booster_mount_allowance_usd'])
    available=gross_credit-new_booster
    return dict(id=identity,variant_ids=[v['id'] for v in variants],merged_interchange_ids=sorted(used),
        disjoint_original_interchanges=True,source_interchange_ids_preserved=sorted(context['hubs']),
        source_access_platform_ids_preserved=sorted(context['stations']),train_routing_switches=0,
        passenger_stop_delta=residual_stop_count,new_passenger_stop_count=context['baseline_station_count']+residual_stop_count,
        network_spacing_conflicts_before=baseline_conflicts,network_spacing_conflicts_after=baseline_conflicts-old_affected+new_affected,
        affected_lines=changes,priced_component_delta_usd=delta,priced_scope_subtotal_delta_usd=subtotal_delta,
        connector_reference_horizontal_length_m=connector_length,connector_quantity_screen=connector_quantities(components,context['a']),
        maximum_transfer_access_arm_m=max_arm,maximum_free_flow_access_minutes=walking_times(max_arm,context['a']),
        connector_complete_capex_usd=None,passenger_od_weighted_time_or_economic_benefit=None,
        equal_or_greater_affected_line_capacity_screen=capacity_not_lower,
        component_extent_screen_pass=all(v['component_extent_screen_pass'] for v in variants),
        gross_station_electrical_target_credit_usd=gross_credit,new_booster_and_mount_target_increment_usd=new_booster,
        priced_scope_connector_allowance_usd=available,
        priced_scope_connector_allowance_usd_per_reference_m=available/connector_length if connector_length else None,
        priced_scope_connector_allowance_usd_per_assumed_deck_m2=available/(connector_length*context['a']['connector_clear_width_m']) if connector_length else None,
        connector_allowance_scope='Unquoted station-electrical target credit less new booster/mount target increments only; removed station civil, connectors, passenger time and other complete economic effects are unpriced. This is not complete economic break-even.',
        cost_savings_proved=False,complete_net_cost_delta_usd=None,selected=False,
        eligibility='hold; located access/flow/ground/level changes, exact profiles, hardware, capacity and quotations require qualification',**FLAGS)


def connected_components(edges):
    graph={}
    for edge in edges:
        x,y=edge['hub_ids'];graph.setdefault(x,set()).add(y);graph.setdefault(y,set()).add(x)
    result=[];seen=set()
    for node in sorted(graph):
        if node in seen:continue
        todo=[node];component=[]
        while todo:
            item=todo.pop()
            if item in seen:continue
            seen.add(item);component.append(item);todo.extend(graph[item]-seen)
        result.append(sorted(component))
    return result


def realignment_concept(context,edge):
    """Counterfactual chords actually meet; no inherited alignment/cost approval."""
    first,last=edge['source_hubs'];h=[(first['lon']+last['lon'])/2,(first['lat']+last['lat'])/2]
    involved=sorted(set(first['lines'])|set(last['lines']));proposals=[]
    for name in involved:
        entry=context['lines'][name];path=entry['path'];length=path['length_m'];anchors=[];members=[]
        for hub in entry['plan']['transfer_hubs']:
            row=(hub['s_m'],hub['exact_crossing_coordinate'],hub['id'])
            if hub['id'] in edge['hub_ids']:members.append(row)
            else:anchors.append(row)
        if entry['line']['shape']=='radial':anchors.extend([(0.,path['points'][0][:2],'start'),(length,path['points'][-1][:2],'end')])
        if not members:raise ValueError('realignment line must serve a source hub')
        lo=min(row[0] for row in members);hi=max(row[0] for row in members);anchors.sort()
        if entry['line']['shape']=='ring':
            expanded=[(s+offset,p,i) for offset in (-length,0.,length) for s,p,i in anchors]
            before=max((row for row in expanded if row[0]<lo),key=lambda row:row[0]);after=min((row for row in expanded if row[0]>hi),key=lambda row:row[0])
        else:
            before=max((row for row in anchors if row[0]<=lo),key=lambda row:row[0]);after=min((row for row in anchors if row[0]>=hi),key=lambda row:row[0])
        coordinates=[before[1],h,after[1]];segments=[op.distance(p,q) for p,q in zip(coordinates,coordinates[1:])]
        scale=math.cos(math.radians(h[1]));incoming=[(h[0]-before[1][0])*scale,h[1]-before[1][1]]
        outgoing=[(after[1][0]-h[0])*scale,after[1][1]-h[1]];norm=math.hypot(*incoming)*math.hypot(*outgoing)
        turn=math.degrees(math.acos(max(-1.,min(1.,sum(x*y for x,y in zip(incoming,outgoing))/norm)))) if norm else None
        proposals.append(dict(line=name,previous_retained_anchor_id=before[2],next_retained_anchor_id=after[2],
            shared_hub_coordinate=h,local_chord_coordinates=coordinates,chord_lengths_m=segments,
            proposed_local_chord_length_m=sum(segments),retained_local_polyline_length_m=after[0]-before[0],
            turn_at_h_degrees=turn,required_station_tangent_m=350.,station_tangent_fitted=False,
            horizontal_curve_radii_m=None,vertical_geometry_m=None,operational_profile=None,
            original_platform_ids_retained_as_source_records=[p['id'] for p in context['stations'].values() if p['line']==name],
            old_platforms_still_operational=False,old_platform_relocation_and_access_solution_required=True,
            existing_civil_classification_reused=False,old_price_reused=False,proposed_civil_cost_usd=None,**FLAGS))
    return dict(id=edge['id']+'-coordinated-realignment-concept',pair_id=edge['id'],kind='counterfactual-shared-site-chords',
        shared_hub_coordinate=h,involved_lines=involved,line_proposals=proposals,
        fixed_line_guideways_physically_reach_common_h=True,train_routing_switches=0,selected=False,
        status='Geometric idea only; guideways change in this counterfactual and no route/design approval transfers',
        original_hub_and_platform_ids_preserved_as_source_records=True,original_platform_boarding_continuity_demonstrated=False,
        platform_levels_and_collision_clearances=None,actual_internal_transfer_walk_m=None,
        compact_walk_benchmark_assumption=dict(distance_m=100.,walk_minutes=walking_times(100.,context['a']),is_computed_layout=False),
        land_water_obstacles_utilities_grade_and_access_qualified=False,station_structure_cost_usd=None,complete_programme_cost_usd=None,**FLAGS)


def _study(identity):
    a=load();city_root=CITY_ROOT;before=source_snapshot(city_root)
    if before!=json.loads(identity):raise ValueError('study source identity changed before execution')
    design=json.loads((city_root/'city.json').read_text());features=json.loads((city_root/'baghdad.corridor.geojson').read_text())['features']
    _,c,costs=model.load();city_assumptions=tomllib.loads(cities.ASSUMPTIONS.read_text())
    context=dict(a=a,c=c,costs=costs,city_assumptions=city_assumptions,hubs={h['id']:h for h in design['interchanges']},
        stations={s['id']:s for s in design['stations']},lines={})
    for line in design['lines']:
        f=cities.formation(c,line['capacity'],[]);retained=[s for s in design['stations'] if s['line']==line['name']]
        plan=op.plan_line(c,f,line,retained,features,interchanges=design['interchanges']);compiled=cities.operating_line_plan(c,city_assumptions,f,line,line['service'],plan)
        context['lines'][line['name']]=dict(line=line,path=op.route_path(features,line),retained=retained,formation=f,plan=plan,compiled=compiled)
    context['baseline_station_count']=sum(len(row['plan']['stations']) for row in context['lines'].values())
    published=json.loads((city_root/'engineering/maglev/summary.json').read_text())
    for name,value in published['source_sha256'].items():
        path=Path(name)
        if path.is_absolute() or '..' in path.parts or digest(ROOT/path)!=value:raise ValueError('current canonical Baghdad packet required')
    if (published['city']!='baghdad' or published['totals']['station_records']!=context['baseline_station_count']
            or published['manufacturing_sha256']!=digest(city_root/'engineering/maglev/manufacturing.json')):
        raise ValueError('canonical Baghdad evidence differs from calculated reference')
    for line in published['lines']:
        baseline=context['lines'][line['line']]['compiled']
        if (line['selected_peak_headway_seconds']!=baseline['selected_peak_headway_seconds']
                or len(line['stations'])!=len(baseline['stations'])
                or line['aw2_capacity_per_direction_hour']!=baseline['aw2_capacity_per_direction_hour']):
            raise ValueError('canonical Baghdad operational reference differs')
    edges,terminal=pair_edges(context);variants=[]
    for edge in edges:
        for adjacency in edge['shared_line_adjacencies']:
            for placement in ('midpoint','endpoint-a','endpoint-b'):
                variant=geometry_variant(context,edge,adjacency,placement)
                variant['operating_and_cost_comparison']=compare(context,[variant],variant['id'])
                variants.append(variant)
    if len(variants)>a['maximum_pair_variants']:raise ValueError('variant count exceeds policy')
    sets=disjoint_sets(edges);lookup={edge['id']:edge for edge in edges};network=[]
    maximal=[row for row in sets if len(row)==len(sets[0])]
    for matching in maximal:
        choices=[[v for v in variants if v['pair_id']==edge_id and v['placement']=='midpoint'] for edge_id in matching]
        for combination in product(*choices):
            if len(network)>=a['maximum_network_alternatives']:break
            network.append(compare(context,list(combination),'disjoint-midpoint-network-'+str(len(network)+1)))
    # Endpoint alternatives use the same disjoint pair sets; no additive delta
    # shortcut: each affected line is rebuilt once for the whole combination.
    for matching in maximal:
        for placement in ('endpoint-a','endpoint-b'):
            if len(network)>=a['maximum_network_alternatives']:break
            choice=[next(v for v in variants if v['pair_id']==edge_id and v['placement']==placement) for edge_id in matching]
            network.append(compare(context,choice,'disjoint-'+placement+'-network-'+str(len(network)+1)))
    bounded_seen=set()
    for matching in maximal:
        choice=[next((v for v in variants if v['pair_id']==edge_id and v['placement']=='midpoint' and v['component_extent_screen_pass']),None) for edge_id in matching]
        choice=[v for v in choice if v is not None];key=tuple(v['id'] for v in choice)
        if key in bounded_seen or len(network)>=a['maximum_network_alternatives']:continue
        bounded_seen.add(key);network.append(compare(context,choice,'bounded-component-midpoint-network-'+str(len(network)+1)))
    components=[]
    for nodes in connected_components(edges):
        hubs=[context['hubs'][x] for x in nodes]
        diameter=max(op.distance([p['lon'],p['lat']],[q['lon'],q['lat']]) for p in hubs for q in hubs)
        components.append(dict(hub_ids=nodes,geodesic_diameter_m=diameter,
            component_extent_screen_pass=diameter<=a['maximum_merged_component_extent_m'],
            all_edges_may_be_merged_independently=len(nodes)==2,
            triple_merge_implemented=False if len(nodes)>2 else None,
            warning='Shared interchange cannot belong to two independently counted pair merges' if len(nodes)>2 else None))
    after=source_snapshot(city_root)
    if after!=before:raise ValueError('calculation sources changed during read-only investigation')
    result=dict(schema=a['schema'],role='read-only-unselected-interchange-hub-investigation',city='Baghdad',source_sha256=before,
        assumptions=a,baseline=dict(operating_station_count=context['baseline_station_count'],source_interchanges=len(design['interchanges']),
            canonical_city_summary_sha256=digest(city_root/'engineering/maglev/summary.json'),canonical_city_summary_current=True,
            source_access_platform_records=len(design['stations']),source_guideway_geometries_changed=False,
            line_screens=[line_screen(row['compiled']) for row in context['lines'].values()]),
        unique_pair_count=len(edges),shared_line_adjacency_count=sum(len(e['shared_line_adjacencies']) for e in edges),
        pair_edges=edges,connected_components=components,terminal_spacing_cases=terminal,variants=variants,
        coordinated_realignment_concepts=[realignment_concept(context,edge) for edge in edges],
        matching_enumeration=dict(disjoint_pair_sets_including_empty=len(sets),maximum_pair_count=len(sets[0]),
            enumerated_sets=sets,calculated_network_alternatives=len(network),maximum_calculated=a['maximum_network_alternatives'],
            other_matching_sets_not_operationally_replayed=True),network_alternatives=network,
        source_access_platform_ids_preserved=sorted(context['stations']),source_interchange_ids_preserved=sorted(context['hubs']),
        true_compact_candidate_count=sum(v['true_compact_hub_geometry_demonstrated'] for v in variants),
        external_guidance=[dict(title='Network Rail Station Capacity Planning NR/GN/CIV/100/03, December2021',
            url='https://www.networkrail.co.uk/wp-content/uploads/2022/02/Station-Capacity-Planning-Design-Manual-NRGNCIV10003.pdf',
            use='Nonlocal preliminary passage-flow, peak-minute pulse, circulation/runoff and resting-place benchmarks; no Iraq approval'),
            dict(title='DfT Inclusive Mobility, January2022',url='https://www.gov.uk/government/publications/inclusive-mobility-making-transport-accessible-for-passengers-and-pedestrians',
                use='Accessible-route best practice; moving-walkway options require a parallel ordinary route, additional width and equipment scope')],
        passage_flow_screen=dict(assumed_clear_width_m=a['connector_clear_width_m'],benchmark_capacity_persons_per_minute=(a['connector_clear_width_m']-.6)*40,
            formula='width_m=max(2.2,peak_two_way_persons_per_minute/40+0.6)',
            hypothetical_peak_minute_requirements=[dict(persons_per_minute=q,width_m=max(2.2,q/40+.6)) for q in (96,120,240)],
            actual_transfer_pulses_known=False,approved_connector_width_m=None),
        connector_unpriced_scope=['deck/roof, piers/foundations, parapets and shade','land/obstacles/utilities and actual level changes',
            'lifts/stairs, queue/runoff/resting areas and accessible lift resilience','optional two-way travelators plus parallel ordinary walkway, power and maintenance',
            'fire/evacuation, passenger flow, cleaning, security and lifetime renewals'],
        recommendation='Keep current junction stops as the reference. All candidate merges are extended transfer complexes, not proved compact hubs. Investigate midpoint geometry locally only where its walking, pulse-flow, capacity and complete connector cost can beat the retained short-spacing exception; do not automatically select an all-merge network.',
        complete_engineering_release=False,**FLAGS)
    result['content_sha256']=sha256(encoded(result)).hexdigest()
    return result


@lru_cache(maxsize=2)
def _study_cached(identity):
    return encoded(_study(identity))


def study():
    """Reproduce bounded alternatives against the current exact Baghdad packet."""
    return json.loads(_study_cached(encoded(source_snapshot(CITY_ROOT)).decode()))


def overview(result):
    geography=json.loads((CITY_ROOT/'baghdad.corridor.geojson').read_text())
    paths=[f['geometry']['coordinates'] for f in geography['features'] if f.get('geometry',{}).get('type')=='LineString']
    points=[p for path in paths for p in path];lon0=min(p[0] for p in points);lon1=max(p[0] for p in points)
    lat0=min(p[1] for p in points);lat1=max(p[1] for p in points)
    def xy(point):return 45+(point[0]-lon0)/(lon1-lon0)*750,95+(lat1-point[1])/(lat1-lat0)*650
    rows=['<svg xmlns="http://www.w3.org/2000/svg" width="1300" height="820" viewBox="0 0 1300 820">',
        '<rect width="1300" height="820" fill="#f8fafc"/>',
        '<g font-family="sans-serif" fill="#102030"><text x="35" y="35" font-size="25">Baghdad: bounded extended passenger-transfer alternatives</text>',
        '<text x="35" y="62" font-size="16">Unchanged train guideways; source crossings retained. Connectors are provisional and unpriced.</text>']
    for path in paths:
        coordinates=' '.join(f'{x:.2f},{y:.2f}' for x,y in map(xy,path));rows.append(f'<polyline points="{coordinates}" fill="none" stroke="#94a3b8" stroke-width="1.4"/>')
    for edge in result['pair_edges']:
        color='#00896b' if edge['id']=='pair-031-040' else '#db7c15'
        variant=next(v for v in result['variants'] if v['pair_id']==edge['id'] and v['placement']=='midpoint')
        for connector in variant['connectors']:
            coordinates=' '.join(f'{x:.2f},{y:.2f}' for x,y in map(xy,connector['retained_guideway_reference_coordinates']))
            rows.append(f'<polyline points="{coordinates}" fill="none" stroke="{color}" stroke-width="4"/>')
        x,y=xy(variant['new_shared_line_stop_coordinate']);label=edge['id'].replace('pair-','')
        rows.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="5" fill="{color}"/><text x="{x+7:.2f}" y="{y-7:.2f}" font-size="12">{label}</text>')
    concept=next(c for c in result['coordinated_realignment_concepts'] if c['pair_id']=='pair-031-040')
    for line in concept['line_proposals']:
        coordinates=' '.join(f'{x:.2f},{y:.2f}' for x,y in map(xy,line['local_chord_coordinates']))
        rows.append(f'<polyline points="{coordinates}" fill="none" stroke="#8b50b5" stroke-width="2" stroke-dasharray="6 5"/>')
    text=[f"{result['unique_pair_count']} pairs; {result['shared_line_adjacency_count']} shared-line gaps; {len(result['variants'])} placements",
        f"{result['matching_enumeration']['disjoint_pair_sets_including_empty']} disjoint pair sets enumerated",
        f"{len(result['network_alternatives'])} bounded network scenarios calculated",
        'No compact hub geometry demonstrated.',
        'Green: 031–040 midpoint for local investigation;',
        'about 471 m maximum reference access arm.',
        'Long arms at 024–025 are retained explicitly;',
        'raw platform spread exceeds 1,500 m.',
        'Shared 000–036–001 cannot count two merges',
        'independently. Triple merge is unimplemented.',
        'All source access/platform IDs are preserved.',
        'No train routing switches are introduced.',
        'Walking excludes lifts, queues, heat and rests.',
        'Guideway curves/land/obstacles are unapproved.',
        'Purple: counterfactual 031–040 shared-site chords;',
        '350 m tangents/levels/internal walk not designed.',
        'Source-bound comparisons remain unselected.']
    for i,line in enumerate(text):rows.append(f'<text x="830" y="{120+i*34}" font-size="16">{line}</text>')
    rows.append('<text x="35" y="785" font-size="15">Geographic overview of retained raw corridors and candidate reference connector paths; no access/structural approval.</text></g></svg>')
    return '\n'.join(rows)+'\n'


def readme(result):
    best=next(v for v in result['variants'] if v['id']=='pair-031-040/line-9/midpoint')
    comparison=best['operating_and_cost_comparison'];line=comparison['affected_lines'][0]
    width=result['assumptions']['connector_clear_width_m']
    rows=['# Baghdad interchange-hub investigation','',
        '![Unchanged guideways and candidate connector paths](overview.svg)','',
        f"The current {result['baseline']['operating_station_count']}-stop Baghdad reference is retained. {result['unique_pair_count']} interchange pairs create {result['shared_line_adjacency_count']} shared-line short-spacing cases. {len(result['variants'])} midpoint/endpoint placements and {len(result['network_alternatives'])} disjoint network scenarios are compared. No variant is selected; every engineering and physical acceptance gate remains open.",'',
        'These are extended transfer complexes. Grouping IDs does not bring fixed train lines to one site. Original cross-line boarding platforms, raw crossing coordinates and every retained access ID stay recorded. The study relocates proposed stops only on the selected shared line and recomputes its exact leg, booster, services, fleet and protected-resource quantities. It introduces no train-routing switches.','',
        '| Pair / shared line / placement | Maximum reference access arm m | Unique reference connector m | Headway before → after s | Services reserve | Partial allowance delta USD | Connector allowance USD/m |',
        '|---|---:|---:|---:|---|---:|---:|']
    for v in result['variants']:
        comparison=v['operating_and_cost_comparison'];line=comparison['affected_lines'][0]
        rows.append(f"| {v['id']} | {v['maximum_reference_access_arm_m']:,.1f} | {comparison['connector_reference_horizontal_length_m']:,.1f} | {line['before']['protected_headway_s']:g} → {line['after']['protected_headway_s']:g} | {'screen pass' if line['after']['service_energy_screen_pass'] else 'hold'} | {comparison['priced_scope_subtotal_delta_usd']:,.0f} | {comparison['priced_scope_connector_allowance_usd_per_reference_m']:,.0f} |")
    comparison=best['operating_and_cost_comparison'];line=comparison['affected_lines'][0]
    rows += ['',
        f'The connector allowance is the unquoted station-electrical target credit less new booster/mount target increments, divided by unique reference connector length or its assumed {width:g} m deck area. It is not complete economic break-even. Removed station civil itself, all passenger-connector works and ridership-weighted time remain unpriced. Fleet differences can accompany lower capacity and do not prove equal-service savings.','',
        f"031–040 on line 9 is a local midpoint case to investigate first: {best['maximum_reference_access_arm_m']:,.1f} m maximum reference access arm, {comparison['connector_reference_horizontal_length_m']:,.1f} m connector, protected headway {line['before']['protected_headway_s']:g} → {line['after']['protected_headway_s']:g} s and services {'screen pass' if line['after']['service_energy_screen_pass'] else 'hold'}. Its station-electrical target credit is ${comparison['gross_station_electrical_target_credit_usd']:,.0f} before connector works; the declared connector allowance is ${comparison['priced_scope_connector_allowance_usd_per_reference_m']:,.0f}/reference-m or ${comparison['priced_scope_connector_allowance_usd_per_assumed_deck_m2']:,.0f}/assumed-deck-m². This is a comparison threshold, not a supplier price or approval.",'',
        'The 000–036–001 component contains overlapping pairs. Disjoint sets never count the shared 036 interchange twice. 024–025 is investigated separately on each shared line; retaining the other line’s boarding platforms produces much longer actual access arms than hub-centroid separation alone suggests. Component-extent failures remain visible as rejected controls.','',
        'Seven separate coordinated-realignment concepts physically draw each involved train line through a shared site using chords from adjacent retained transfer anchors. These change guideway geometry and therefore inherit no old civil classifications or prices. The 350 m station tangent, curves, grades, platform levels, collisions, land/water/utilities and accessible circulation remain undesigned. The 100 m compact walk is a sensitivity assumption, not a computed internal layout. Purple dashed lines illustrate the 031–040 concept only.','',
        f"Walking sensitivities use {', '.join(str(v) for v in result['assumptions']['walk_speeds_m_s'])} m/s, before level changes, queues, rests, Baghdad heat or waiting for service. The {width:g} m assumed passage is only a preliminary quantity width; its peak-minute two-way flow benchmark gives {result['passage_flow_screen']['benchmark_capacity_persons_per_minute']:g} people/min, and 120/240 people/min would imply 3.6/6.6 m. Actual transfer pulses and lift resilience must be studied.",'',
        '[Network Rail station-capacity guidance](https://www.networkrail.co.uk/wp-content/uploads/2022/02/Station-Capacity-Planning-Design-Manual-NRGNCIV10003.pdf) and [DfT Inclusive Mobility](https://www.gov.uk/government/publications/inclusive-mobility-making-transport-accessible-for-passengers-and-pedestrians) inform provisional access/flow benchmarks. They do not establish Iraq approval. Moving-walkway options retain a parallel ordinary route and require equipment, power, maintenance and additional width.','',
        '[Complete bounded data](study.json.gz) · [Source and payload receipt](manifest.json)','']
    return '\n'.join(rows)


def publish(output=OUTPUT):
    """Publish only this new owned packet; no city or infrastructure mutations."""
    result=study();output=Path(output)
    if output.exists() and any(p.is_symlink() or p.name not in FILES|{'manifest.json'} for p in output.iterdir()):
        raise ValueError('unowned or linked file in interchange packet')
    raw=encoded(result)
    if len(raw)>MAX_RAW:raise ValueError('interchange raw packet exceeds budget')
    compressed=gzip.compress(raw,mtime=0)
    if len(compressed)>MAX_COMPRESSED:raise ValueError('interchange compressed packet exceeds budget')
    if result['source_sha256']!=source_snapshot(CITY_ROOT):raise ValueError('interchange sources changed before publication')
    output.mkdir(parents=True,exist_ok=True)
    (output/'study.json.gz').write_bytes(compressed)
    (output/'overview.svg').write_text(overview(result));(output/'README.md').write_text(readme(result))
    manifest=dict(schema=result['schema'],source_sha256=result['source_sha256'],content_sha256=result['content_sha256'],
        files_sha256={name:digest(output/name) for name in sorted(FILES)},raw_bytes=len(raw),compressed_bytes=len(compressed),**FLAGS)
    (output/'manifest.json').write_text(json.dumps(manifest,sort_keys=True,indent=2)+'\n')
    verify(output)
    return manifest


def verify(output=OUTPUT):
    output=Path(output)
    if set(p.name for p in output.iterdir())!=FILES|{'manifest.json'} or any(p.is_symlink() for p in output.iterdir()):
        raise ValueError('interchange packet inventory differs')
    manifest=json.loads((output/'manifest.json').read_bytes())
    if manifest['schema']!='osr-interchange-hub-investigation/1' or any(manifest.get(k) is not False for k in FLAGS):raise ValueError('interchange packet may not claim release')
    if set(manifest['files_sha256'])!=FILES or any(digest(output/name)!=value for name,value in manifest['files_sha256'].items()):
        raise ValueError('interchange payload checksum differs')
    if manifest['source_sha256']!=source_snapshot(CITY_ROOT):raise ValueError('interchange source or canonical city receipt is stale')
    compressed=(output/'study.json.gz').read_bytes()
    if len(compressed)>MAX_COMPRESSED:raise ValueError('interchange compressed budget exceeded')
    with gzip.GzipFile(fileobj=io.BytesIO(compressed)) as stream:raw=stream.read(MAX_RAW+1)
    if len(raw)>MAX_RAW or len(raw)!=manifest['raw_bytes'] or len(compressed)!=manifest['compressed_bytes']:raise ValueError('interchange raw budget/size differs')
    result=json.loads(raw);expected=study()
    if encoded(result)!=encoded(expected) or manifest['content_sha256']!=expected['content_sha256']:
        raise ValueError('interchange recalculated content differs')
    if ((output/'overview.svg').read_text()!=overview(expected) or (output/'README.md').read_text()!=readme(expected)):
        raise ValueError('interchange presentation differs from exact study')
    return manifest


def read_summary(output=OUTPUT):
    verify(output);result=study()
    best=next(v for v in result['variants'] if v['id']=='pair-031-040/line-9/midpoint')
    return dict(schema=result['schema'],baseline_stops=result['baseline']['operating_station_count'],
        unique_pairs=result['unique_pair_count'],shared_line_adjacencies=result['shared_line_adjacency_count'],
        placement_variants=len(result['variants']),network_alternatives=len(result['network_alternatives']),
        compact_hubs_proved=result['true_compact_candidate_count'],
        focused_investigation=dict(id=best['id'],maximum_reference_access_arm_m=best['maximum_reference_access_arm_m'],
            unique_reference_connector_m=best['independently_counted_unique_connector_length_m'],
            price_scope_allowance_usd_per_reference_m=best['operating_and_cost_comparison']['priced_scope_connector_allowance_usd_per_reference_m']),
        selected_variant=None,**FLAGS)

