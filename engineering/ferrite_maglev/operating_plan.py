"""Located provisional operating stops and finite station/top-up motion studies.

Retained geography/demand remain inputs. Proposed station locations, curve
geometry and flat motion screens do not constitute survey or route approval.
"""
from bisect import bisect_right
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
import json
import math
from pathlib import Path
import tomllib

from . import model,station,configuration

INPUT=Path(__file__).with_name('operating-plan.toml')
SCHEMA='osr-provisional-operating-plan/1'
EARTH_M=6371000.


def load():
    a=tomllib.loads(INPUT.read_text())
    if a['schema']!=SCHEMA:raise ValueError('operating plan schema required')
    for key in ('physical_route_approval','curve_phase_and_guidance_validated','station_sites_approved','costs_are_quotes'):
        if a.get(key) is not False:raise ValueError('unqualified operating plan cannot assert '+key)
    for key,value in a.items():
        if type(value) in (int,float) and not key.endswith('winding_start_m'):model.positive(value,key)
    if not 1500<=a['minimum_mainline_spacing_m']<=a['target_mainline_spacing_m']<=a['maximum_mainline_spacing_m']<=5000:
        raise ValueError('bounded station spacing required')
    if not 4000<=a['suburban_minimum_spacing_m']<=a['suburban_target_spacing_m']<=a['suburban_maximum_spacing_m']<=6000:
        raise ValueError('bounded suburban spacing required')
    if a['default_service_class']!='urban' or a['suburban_classification_required'] is not True:
        raise ValueError('suburban classification must be explicit')
    if a['junction_policy']!='preserve-transfers-and-flag-spacing-conflicts':raise ValueError('declared fixed-line passenger-transfer policy required')
    for name in ('charger_alternatives_kw_per_car','battery_alternatives_kwh_per_car'):
        if not isinstance(a[name],list) or not 1<=len(a[name])<=6:raise ValueError('bounded alternatives required')
        for value in a[name]:model.positive(value,name)
    if not 20<=a['minimum_runtime_s']<=a['maximum_runtime_s']<=180 or a['runtime_step_s']<1:
        raise ValueError('bounded runtime search required')
    if not 1<=len(a['acceleration_alternatives_m_s2'])<=4:raise ValueError('bounded acceleration alternatives required')
    for value in a['acceleration_alternatives_m_s2']:
        if type(value) not in (int,float) or not .5<=value<=1.2:raise ValueError('bounded acceleration study alternative required')
    if type(a['terminal_sections']) is not int or not 2<=a['terminal_sections']<=6:
        raise ValueError('bounded terminal section count required')
    if type(a['maximum_stations_per_line']) is not int or not 2<=a['maximum_stations_per_line']<=2000:
        raise ValueError('bounded station count required')
    # Signed coordinates are deliberately outside the generic positive loop.
    if not -500<=a['mainline_winding_start_m']<0<a['mainline_winding_end_m']<=500:
        raise ValueError('mainline winding coordinates required')
    if not -500<=a['terminal_winding_start_m']<0<a['terminal_winding_end_m']<=500:
        raise ValueError('terminal winding coordinates required')
    if not 0<a['minimum_assumed_force_reserve_fraction']<1:
        raise ValueError('finite force reserve target required')
    if not 0<a['charger_conversion_efficiency_study']<=1:
        raise ValueError('bounded charger conversion efficiency required')
    if a['minimum_headway_s']>a['preferred_headway_s'] or a['preferred_headway_s']>a['maximum_headway_s']:
        raise ValueError('ordered headway search bounds required')
    return a


def source_paths():
    from . import corridor,booster_kit
    return [Path(__file__),INPUT,Path(corridor.__file__),corridor.INPUT,*booster_kit.source_paths()]


def validate_strategy(c,a):
    strategy=c['operating_strategy']
    pairs={'urban_minimum_stop_spacing_m':'minimum_mainline_spacing_m','urban_target_stop_spacing_m':'target_mainline_spacing_m',
        'suburban_minimum_stop_spacing_m':'suburban_minimum_spacing_m','suburban_maximum_stop_spacing_m':'suburban_maximum_spacing_m'}
    if any(strategy[key]!=a[value] for key,value in pairs.items()):raise ValueError('primary and city stop-spacing strategies differ')
    if (strategy['junction_operation']!='passenger-transfer-between-fixed-lines' or strategy['longer_leg_boosters_enabled'] is not True
            or strategy['short_interchange_spacing_policy']!='retain-and-flag-exception'):
        raise ValueError('fixed-line passenger-transfer and declared booster strategy required')


def distance(a,b):
    x,y=math.radians(a[1]),math.radians(b[1])
    value=math.sin((y-x)/2)**2+math.cos(x)*math.cos(y)*math.sin(math.radians(b[0]-a[0])/2)**2
    return 2*EARTH_M*math.atan2(math.sqrt(max(0.,value)),math.sqrt(max(0.,1-value)))


def route_path(features,line):
    model.positive(line['length_m'],'retained route length')
    matches=[f for f in features if f.get('properties',{}).get('name')==line['name'] and
             f.get('geometry',{}).get('type')=='LineString']
    if len(matches)!=1:raise ValueError('exact retained geographic line required: '+line['name'])
    points=matches[0]['geometry']['coordinates']
    if len(points)<2 or len(points)>100000:raise ValueError('bounded route coordinates required')
    for p in points:
        if len(p)<2 or any(type(v) not in (float,int) or not math.isfinite(v) for v in p[:2]) or not -180<=p[0]<=180 or not -90<=p[1]<=90:
            raise ValueError('finite longitude/latitude required')
    lengths=[0.]
    for first,last in zip(points,points[1:]):lengths.append(lengths[-1]+distance(first,last))
    if lengths[-1]<=0:raise ValueError('positive retained geographic length required')
    return dict(points=points,cumulative_m=lengths,length_m=lengths[-1],retained_length_m=line['length_m'])


def point_at(path,chainage):
    value=min(path['length_m'],max(0.,chainage))
    index=min(len(path['points'])-2,max(0,bisect_right(path['cumulative_m'],value)-1))
    first,last=path['points'][index:index+2];lo,hi=path['cumulative_m'][index:index+2]
    fraction=(value-lo)/(hi-lo) if hi>lo else 0.
    return dict(lon=first[0]+fraction*(last[0]-first[0]),lat=first[1]+fraction*(last[1]-first[1]),
        source_segment_index=index,source_segment_fraction=fraction)


def _identity(c,f):
    a=load();validate_strategy(c,a)
    return json.dumps(dict(c=c,cars=f['cars'],policy=a),sort_keys=True,allow_nan=False)


def trip(c,f,length,*,terminal=False):
    """Cached bounded runtime/acceleration search, at AW0/AW2/AW3."""
    return deepcopy(_trip(_identity(c,f),round(length,6),terminal))


@lru_cache(maxsize=8192)
def _trip(identity,length,terminal):
    inputs=json.loads(identity);c=inputs['c'];cars=inputs['cars'];a=inputs['policy'];p=c['power'];v=c['vehicle']
    cfg=configuration.selected(c,city='operating-plan',cars=cars)
    start=a['terminal_winding_start_m'] if terminal else a['mainline_winding_start_m']
    end=a['terminal_winding_end_m'] if terminal else a['mainline_winding_end_m']
    speed=a['terminal_speed_limit_kmh'] if terminal else v['service_speed_study_kmh']
    target=max(a['minimum_runtime_s'],a['runtime_reference_s_per_km']*length/1000)
    step=a['runtime_step_s'];target=math.ceil(target/step)*step
    times=[a['minimum_runtime_s']+i*step for i in range(1+int((a['maximum_runtime_s']-a['minimum_runtime_s'])/step))]
    times.sort(key=lambda value:(abs(value-target),value))
    masses=model.mass(c,c['mass']['ferrite_base'],p['services_battery_kwh_per_car'])
    attempts=[];fallback=None
    for runtime in times:
        for accel in a['acceleration_alternatives_m_s2']:
            profiles=[];reason=None
            for load in ('tare_kg','aw2_kg','aw3_kg'):
                t=station.trajectory(distance_m=length,runtime_s=runtime,car_mass_kg=masses[load],cars=cars,
                    acceleration=accel,deceleration=v['service_deceleration_study_m_s2'],jerk=v['jerk_study_m_s3'],
                    speed_limit_kmh=speed,record_trace=False,motoring_efficiency=p['station_drive_efficiency'],
                    generating_efficiency=p['station_generating_efficiency'],
                    resistance_constant_n_per_car=p['passive_rail_drag_study_n_per_car'],
                    resistance_quadratic_n_per_car=.5*p['air_density_study_kg_m3']*p['drag_area_study_m2_per_car'])
                if not t['study_pass']:reason=load+': '+t['reason'];break
                z=model.station_zone_screen(c,t,cars=cars,winding_start_m=start,winding_end_m=end)
                if not z['study_pass']:reason=load+': '+z['reason'];break
                margin=min(z['minimum_force_reserve_fraction'].values())
                if margin<a['minimum_assumed_force_reserve_fraction']:
                    reason=load+': provisional overlap force reserve below search target';break
                clearance=station._time_at_position(t,cfg.formation.assumed_overall_length_m+end+a['downstream_overlap_beyond_winding_m'])
                if clearance is None:reason=load+': complete train cannot clear protected bundle before next stop';break
                profiles.append(dict(load=load,car_mass_kg=masses[load],trajectory=t,zone=z,tail_clearance_s=clearance))
            if reason:
                attempts.append(dict(runtime_s=runtime,acceleration_m_s2=accel,hold=reason));continue
            hotel=p['hot_hotel_kw_per_car'];overhead=p['station_dwell_seconds']-p['charger_effective_seconds']
            charger=p.get('candidate_station_charger_kw_per_car',240.)
            converted=charger*a['charger_conversion_efficiency_study']
            if converted<=hotel:raise ValueError('converted charger input must exceed live services')
            dwell=max(p['station_dwell_seconds'],math.ceil((hotel*runtime+hotel*overhead)/(converted-hotel)+overhead))
            clear=max(r['tail_clearance_s'] for r in profiles)
            bound=runtime+dwell+clear+a['release_allowance_s']
            candidate=dict(schema=SCHEMA,study_pass=True,distance_m=length,runtime_s=runtime,
                acceleration_m_s2=accel,deceleration_m_s2=v['service_deceleration_study_m_s2'],jerk_m_s3=v['jerk_study_m_s3'],
                speed_limit_kmh=speed,winding_start_m=start,winding_end_m=end,
                downstream_overlap_end_m=end+a['downstream_overlap_beyond_winding_m'],
                clearance_front_distance_m=cfg.formation.assumed_overall_length_m+end+a['downstream_overlap_beyond_winding_m'],
                tail_clearance_s=clear,dwell_s=dwell,resource_headway_lower_bound_s=bound,
                charger_input_kw_per_car=charger,charger_converted_output_kw_per_car=converted,
                charger_conversion_efficiency_study=a['charger_conversion_efficiency_study'],
                minimum_assumed_force_reserve_fraction=min(min(r['zone']['minimum_force_reserve_fraction'].values()) for r in profiles),
                profiles=profiles,rejected_attempts=attempts.copy(),terminal=terminal,
                physical_route_approved=False,curve_phase_and_guidance_validated=False,**model.FLAGS)
            if bound<=a['preferred_headway_s']:return candidate
            if bound<=a['maximum_headway_s'] and fallback is None:fallback=candidate
            attempts.append(dict(runtime_s=runtime,acceleration_m_s2=accel,hold='preferred headway not met',headway_lower_bound_s=bound))
    if fallback is not None:
        fallback['rejected_attempts']=attempts
        return fallback
    return dict(schema=SCHEMA,study_pass=False,distance_m=length,terminal=terminal,rejected_attempts=attempts,
        reason='No bounded station-only runtime/force/clearance candidate meets the declared headway ceiling',**model.FLAGS)


def wide_trip(c,f,length,*,service_class='urban'):
    return deepcopy(_wide_trip(_identity(c,f),round(length,6),service_class))


@lru_cache(maxsize=4096)
def _wide_trip(identity,length,service_class):
    from . import corridor
    inputs=json.loads(identity);c=inputs['c'];cars=inputs['cars'];a=inputs['policy'];p=c['power'];ca=corridor.load()
    battery=p['services_battery_kwh_per_car'];masses=model.mass(c,c['mass']['ferrite_base'],battery)
    def all_loads(mode):
        rows=[]
        for label,key in [('AW0','tare_kg'),('AW2','aw2_kg'),('AW3','aw3_kg')]:
            value=corridor.evaluate(c,distance_m=length,cars=cars,car_mass_kg=masses[key],load_case=label,mode=mode,
                battery_kwh=battery,charger_kw=400.,dwell_s=60.,record_trace=False)
            rows.append(dict(load=key,car_mass_kg=masses[key],corridor=value,trajectory=value['longitudinal_profile']))
        return rows
    propulsion_mode=service_class;profiles=all_loads(propulsion_mode);topology_comparisons=[]
    if service_class=='urban' and not all(r['corridor']['motion_screen_pass'] and r['corridor']['rating_screen_pass'] for r in profiles):
        # The evaluator's suburban mechanism is one finite midpoint top-up; it
        # does not classify this retained urban corridor as suburban land use.
        alternative=all_loads('suburban')
        passed=all(r['corridor']['motion_screen_pass'] and r['corridor']['rating_screen_pass'] for r in alternative)
        topology_comparisons.append(dict(kind='unpowered-interstation-coast',all_load_motion_rating_pass=False,
            runtime_s=profiles[-1]['corridor']['runtime_s'],holds=[r['corridor']['holds'] for r in profiles]))
        topology_comparisons.append(dict(kind='one-located-midpoint-top-up',all_load_motion_rating_pass=passed,
            runtime_s=alternative[-1]['corridor']['runtime_s'],selected_for_numerical_plan=passed))
        if passed:propulsion_mode='suburban';profiles=alternative
    lower_motors=[corridor.evaluate(c,distance_m=length,cars=cars,car_mass_kg=masses[key],load_case=label,mode=propulsion_mode,
        battery_kwh=battery,charger_kw=400.,dwell_s=60.,motor_option='lower-force-constant',record_trace=False)
        for label,key in [('AW0','tare_kg'),('AW2','aw2_kg'),('AW3','aw3_kg')]]
    lower_motor=lower_motors[-1]
    runtime=profiles[-1]['corridor']['runtime_s'];fraction=ca['connected_fraction'];eta=ca['charger_efficiency'];hotel=ca['hot_services_kw_per_car']
    moving=all(v['corridor']['motion_screen_pass'] for v in profiles);rated=all(v['corridor']['rating_screen_pass'] for v in profiles)
    clearance=max((v['corridor'].get('full_tail_clearance_time_after_next_departure_s') or 0.) for v in profiles)
    cases=[]
    for pack in a['battery_alternatives_kwh_per_car']:
        for charger in a['charger_alternatives_kw_per_car']:
            denominator=charger*eta*fraction-hotel
            balance_dwell=max(60.,float(math.ceil(hotel*runtime/denominator))) if denominator>0 else 300.
            for dwell in sorted({balance_dwell,96.,240.}):
                connected=dwell*fraction;replacement=hotel*(runtime+dwell-connected)/3600
                replenishment=(charger*eta-hotel)*connected/3600;reserve=hotel*ca['protected_services_reserve_minutes']/60
                usable=pack*p['eol_capacity_fraction']*(p['normal_soc_high']-p['normal_soc_low'])
                service=usable>=replacement+reserve and replenishment>=replacement
                exact_mass=pack==battery
                headway=runtime+dwell+clearance+ca['release_allowance_s'] if clearance>0 else None
                capacity=headway is not None and headway<=ca['requested_headway_s']
                case_holds=[]
                if not moving:case_holds.append('Motion/installed-zone overlap screen fails')
                if not rated:case_holds.append('Equivalent motor rating screen fails')
                if not service:case_holds.append('Protected services reserve or repeated charge replenishment fails')
                if not exact_mass:case_holds.append('Changed services pack mass requires a new exact formation and trajectory confirmation')
                if not capacity:case_holds.append('Existing exclusive whole-leg protection cannot meet retained180s target')
                case_holds.append('Recovery, section handover and installed hardware qualification remain open')
                cases.append(dict(battery_kwh_per_car=pack,charger_input_kw_per_car=charger,charger_converted_kw_per_car=charger*eta,
                    dwell_s=dwell,connected_s=connected,charger_efficiency=eta,services_replacement_kwh_per_car=replacement,
                    replenished_kwh_per_car=replenishment,protected_reserve_kwh_per_car=reserve,usable_kwh_per_car=usable,
                    battery_mass_change_kg_per_car=(pack-battery)*1000/p['installed_pack_specific_energy_wh_kg'],
                    exact_installed_pack_configuration=exact_mass,motion_rating_confirmed=exact_mass and moving and rated,
                    service_energy_screen_pass=service,headway_lower_bound_s=headway,capacity_screen_pass=capacity,
                    charger_interface_target_factor=charger/200.,eligible=False,holds=case_holds,engineering_accepted=False))
    current=[case for case in cases if case['exact_installed_pack_configuration']]
    research=min(current,key=lambda r:(not (r['motion_rating_confirmed'] and r['service_energy_screen_pass']),
        r['headway_lower_bound_s'] if r['headway_lower_bound_s'] is not None else float('inf'),r['charger_input_kw_per_car']))
    # No changed pack, unimplemented protection or hardware claim is promoted.
    combined={}
    for row in profiles:
        for zone in row['corridor']['installed_zones']:
            if zone['id'] not in combined:combined[zone['id']]=deepcopy(zone)
            else:
                item=combined[zone['id']];item['start_m']=min(item['start_m'],zone['start_m']);item['end_m']=max(item['end_m'],zone['end_m'])
    zones=list(combined.values())
    for zone in zones:
        zone['length_m']=zone['end_m']-zone['start_m'];zone['electrical_sections']=math.ceil(zone['length_m']/zone['electrical_section_m'])
        zone['coverage_basis']='Union of explicitly sampled AW0/AW2/AW3 installed-zone envelopes; exact physical field and curved alignment unqualified'
    holds=list(dict.fromkeys([*research['holds'],*[h for row in profiles for h in row['corridor']['holds']]]))
    return dict(schema=SCHEMA,kind='sparse-fixed-powered-corridor',study_pass=False,
        motion_screen_pass=moving,rating_screen_pass=rated,kinematic_screen_pass=moving and rated,
        service_energy_screen_pass=research['service_energy_screen_pass'],distance_m=length,runtime_s=runtime,
        service_class=service_class,propulsion_topology='one-located-midpoint-top-up' if propulsion_mode=='suburban' else 'unpowered-interstation-coast',
        corridor_evaluator_mechanism=propulsion_mode,land_use_classification_inferred_from_propulsion=False,
        topology_comparisons=topology_comparisons,profiles=profiles,installed_zones=zones,alternatives=cases,
        selected_eligible_alternative=None,research_comparison_candidate=research,
        selection_scope='Research comparison only; no alternative is eligible while protection/recovery/hardware gates remain open',
        equivalent_motor_alternatives=[dict(option='higher-voltage',rating=profiles[-1]['corridor'].get('equivalent_motor'),
                all_loads_confirmed=moving and rated,qualified=False,configured_price_usd=None),
            dict(option='lower-force-constant',rating=lower_motor.get('equivalent_motor'),
                aw3_motion_pass=lower_motor['motion_screen_pass'],aw3_rating_pass=lower_motor['rating_screen_pass'],
                all_loads_confirmed=all(row['motion_screen_pass'] and row['rating_screen_pass'] for row in lower_motors),
                qualified=False,configured_price_usd=None)],
        motor_selection_qualified=False,motor_price_comparison_proved=False,
        dwell_s=research['dwell_s'],charger_input_kw_per_car=research['charger_input_kw_per_car'],
        charger_conversion_efficiency_study=eta,connected_fraction=fraction,
        tail_clearance_s=clearance or None,resource_headway_lower_bound_s=research['headway_lower_bound_s'],
        minimum_assumed_force_reserve_fraction=min(v['corridor'].get('minimum_force_reserve_fraction',-1.) for v in profiles),
        holds=holds,physical_route_approved=False,curve_phase_and_guidance_validated=False,**model.FLAGS)


def duty(c,result,*,hot=False):
    hotel=c['power']['hot_hotel_kw_per_car' if hot else 'normal_hotel_kw_per_car']
    if result.get('kind')=='sparse-fixed-powered-corridor':
        profile=next(row for row in result['profiles'] if row['load']==('aw3_kg' if hot else 'aw2_kg'))['corridor']
        return dict(moving_seconds=result['runtime_s'],moving_energy_kwh=hotel*result['runtime_s']/3600,
            achieved_speed_kmh=profile['peak_speed_kmh'],hotel_kw=hotel,
            station_traction_input_kwh=None if profile['propulsion_input_kwh'] is None else profile['propulsion_input_kwh']/profile['cars'],
            pure_trajectory_screen_pass=profile['longitudinal_profile']['study_pass'],station_zone_screen_pass=profile['motion_screen_pass'],
            kinematic_screen_pass=result['kinematic_screen_pass'],kinematic_hold=None if result['kinematic_screen_pass'] else '; '.join(result['holds']),
            tail_clearance_s=result['tail_clearance_s'])
    if result['study_pass']:
        profile=next(r for r in result['profiles'] if r['load']==('aw3_kg' if hot else 'aw2_kg'))
        t=profile['trajectory'];cars=t['inputs']['cars'];runtime=result['runtime_s']
        return dict(moving_seconds=runtime,moving_energy_kwh=hotel*runtime/3600,
            achieved_speed_kmh=t['peak_speed_kmh'],hotel_kw=hotel,
            station_traction_input_kwh=t['station_positive_input_kwh']/cars,
            pure_trajectory_screen_pass=True,station_zone_screen_pass=True,station_zone=profile['zone'],
            kinematic_screen_pass=True,kinematic_hold=None,tail_clearance_s=result['tail_clearance_s'])
    runtime=load()['maximum_runtime_s']
    return dict(moving_seconds=runtime,moving_energy_kwh=hotel*runtime/3600,achieved_speed_kmh=None,hotel_kw=hotel,
        station_traction_input_kwh=None,pure_trajectory_screen_pass=False,station_zone_screen_pass=False,
        kinematic_screen_pass=False,kinematic_hold=result['reason'],tail_clearance_s=None)


def terminal_geometry(point,tangent,*,at_start=False):
    """Tangent R-L-R loop between opposing parallel beams; open land envelope."""
    a=load();r=a['terminal_radius_m'];spacing=a['terminal_beam_centres_m'];cy=r+spacing/2
    if cy>=2*r:raise ValueError('terminal track spacing exceeds tangent loop construction')
    x=math.sqrt(4*r*r-cy*cy);theta=math.acos(cy/(2*r))
    arcs=[dict(centre_m=[0.,-cy],start_angle_rad=math.pi/2,turn_angle_rad=-theta),
          dict(centre_m=[x,0.],start_angle_rad=-math.pi/2-theta,turn_angle_rad=math.pi+2*theta),
          dict(centre_m=[0.,cy],start_angle_rad=-math.pi/2+theta,turn_angle_rad=-theta)]
    local=[];chain=[];s=0.
    for arc in arcs:
        angle=arc['turn_angle_rad'];n=max(1,math.ceil(abs(angle)*r/a['curve_sample_interval_m']))
        for i in range(n+1):
            if local and i==0:continue
            q=arc['start_angle_rad']+angle*i/n
            local.append([arc['centre_m'][0]+r*math.cos(q),arc['centre_m'][1]+r*math.sin(q)])
            chain.append(s+abs(angle)*r*i/n)
        s+=abs(angle)*r
    # End loops point outwards, away from the retained line endpoint.
    dx,dy=tangent
    if at_start:dx,dy=-dx,-dy
    norm=math.hypot(dx,dy)
    if norm<=0:raise ValueError('terminal tangent required')
    dx,dy=dx/norm,dy/norm
    coslat=math.cos(math.radians(point['lat']));coordinates=[]
    for u,w in local:
        east=u*dx-w*dy;north=u*dy+w*dx
        coordinates.append([point['lon']+math.degrees(east/(EARTH_M*coslat)),point['lat']+math.degrees(north/EARTH_M)])
    return dict(radius_m=r,beam_centres_m=spacing,arcs=arcs,length_m=s,
        local_coordinates_m=local,coordinates=coordinates,chainages_m=chain,
        longitudinal_curve_model='Flat arclength; lateral acceleration screen only, no curve-phase/guidance/flexible-train validation',
        land_and_clearance_approved=False,curve_phase_and_guidance_validated=False,
        lateral_acceleration_screen_m_s2=(a['terminal_speed_limit_kmh']/3.6)**2/r,
        lateral_screen_pass=(a['terminal_speed_limit_kmh']/3.6)**2/r<=a['terminal_lateral_acceleration_screen_m_s2'],
        **model.FLAGS)


def _curve_point(curve,value):
    i=min(len(curve['chainages_m'])-2,max(0,bisect_right(curve['chainages_m'],value)-1))
    lo,hi=curve['chainages_m'][i:i+2];fraction=(value-lo)/(hi-lo)
    p,q=curve['coordinates'][i:i+2]
    return dict(lon=p[0]+fraction*(q[0]-p[0]),lat=p[1]+fraction*(q[1]-p[1]))


def project_crossing(path,lon,lat):
    """Project one retained crossing onto its fixed geographic line."""
    best=None;scale=math.cos(math.radians(lat))
    for i,(p,q) in enumerate(zip(path['points'],path['points'][1:])):
        ax=(p[0]-lon)*scale;ay=p[1]-lat;dx=(q[0]-p[0])*scale;dy=q[1]-p[1]
        fraction=max(0.,min(1.,-(ax*dx+ay*dy)/(dx*dx+dy*dy))) if dx*dx+dy*dy else 0.
        point=[p[0]+fraction*(q[0]-p[0]),p[1]+fraction*(q[1]-p[1])]
        error=distance([lon,lat],point)
        candidate=(error,i,fraction)
        if best is None or candidate<best:best=candidate
    error,index,fraction=best
    return dict(s_m=path['cumulative_m'][index]+fraction*(path['cumulative_m'][index+1]-path['cumulative_m'][index]),
        source_segment_index=index,source_segment_fraction=fraction,crossing_projection_offset_m=error,
        method='Local longitude/latitude segment projection onto retained fixed line; not a survey')


def passenger_layout(path,line,retained,interchanges=(),*,service_class='urban'):
    """Junctions are passenger transfers; no train routing or switch is inferred."""
    a=load();length=path['length_m'];raw=sorted(deepcopy(retained),key=lambda r:r['s_m']);by_id={s['id']:s for s in raw}
    if service_class not in ('urban','suburban'):raise ValueError('explicit urban/suburban service class required')
    minimum=a['minimum_mainline_spacing_m'] if service_class=='urban' else a['suburban_minimum_spacing_m']
    target=a['target_mainline_spacing_m'] if service_class=='urban' else a['suburban_target_spacing_m']
    maximum=a['maximum_mainline_spacing_m'] if service_class=='urban' else a['suburban_maximum_spacing_m']
    nodes=[];crossings=[];terminal_access=[]
    for hub in interchanges:
        platforms=[s for s in hub.get('platforms',[]) if s in by_id]
        if line['name'] not in hub.get('lines',[]) and not platforms:continue
        projection=project_crossing(path,hub['lon'],hub['lat'])
        node=dict(id=hub['id'],kind='fixed-line-passenger-transfer',**projection,
            source_crossing=deepcopy(hub),source_platform_ids=platforms,
            exact_crossing_coordinate=[hub['lon'],hub['lat']],train_routing=False,access_qualified=False)
        operating_s=projection['s_m']
        if line['shape']=='radial' and .5<=min(operating_s,length-operating_s)<350.:
            # Keep the terminal and its loop datum. A nearby crossing becomes
            # a compact passenger-access proposal, never a49m train journey.
            endpoint=0. if operating_s<=length/2 else length
            spread=abs(operating_s-endpoint);lo,hi=sorted((operating_s,endpoint))
            coordinates=[[point_at(path,lo)['lon'],point_at(path,lo)['lat']],
                *[p[:2] for s,p in zip(path['cumulative_m'],path['points']) if lo<s<hi],
                [point_at(path,hi)['lon'],point_at(path,hi)['lat']]]
            connector=dict(id=hub['id']+'-terminal-access-proposal',kind='compact-terminal-passenger-transfer-access',
                crossing_id=hub['id'],terminal_s_m=endpoint,source_crossing_s_m=operating_s,
                retained_route_separation_m=spread,reference_coordinates=coordinates,
                accessible_path_length_m=None,capex_usd=None,access_and_land_qualified=False,
                route_alignment_changed=False,terminal_loop_datum_changed=False,train_routing=False)
            terminal_access.append(connector);node.update(operating_station_s_m=endpoint,terminal_access_proposal=connector)
            operating_s=endpoint
        crossings.append(node);nodes.append(dict(s_m=operating_s,node_ids=[hub['id']],junction_ids=[hub['id']]))
    if line['shape']=='radial':nodes.extend([dict(s_m=0.,node_ids=['start'],junction_ids=[]),dict(s_m=length,node_ids=['end'],junction_ids=[])])
    elif line['shape']!='ring':raise ValueError('supported radial/ring topology required')
    if not nodes:nodes=[dict(s_m=0.,node_ids=['ring-reference'],junction_ids=[])]
    nodes.sort(key=lambda row:row['s_m']);anchors=[]
    for node in nodes:
        if anchors and abs(node['s_m']-anchors[-1]['s_m'])<.5:
            anchors[-1]['node_ids'].extend(node['node_ids']);anchors[-1]['junction_ids'].extend(node['junction_ids'])
        else:anchors.append(deepcopy(node))
    edges=[(anchors[i],anchors[i+1],anchors[i+1]['s_m']) for i in range(len(anchors)-1)]
    if line['shape']=='ring':edges.append((anchors[-1],anchors[0],anchors[0]['s_m']+length))
    positions=[];conflicts=[]
    for first,last,end in edges:
        span=end-first['s_m'];lower=max(1,math.ceil(span/maximum-1e-10));upper=math.floor(span/minimum+1e-10)
        count=max(1,min(max(1,upper),max(lower,math.floor(span/target+.5))))
        if upper<lower:
            conflicts.append(dict(kind='passenger-stop-spacing-conflict',from_nodes=first['node_ids'],to_nodes=last['node_ids'],
                distance_m=span,minimum_m=minimum,maximum_m=maximum,service_class=service_class,
                retained_crossings_preserved=True,engineering_accepted=False,
                alternatives=[dict(kind='accessible-consolidated-transfer-hub',minimum_shared_line_transfer_walk_m=span,
                    actual_accessible_path_m=None,guideways_moved=False,capex_usd=None,access_and_cost_qualified=False),
                    dict(kind='separately-assessed-fixed-line-geometry-or-terminal-lead',geometry_changed=False,capex_usd=None,accepted=False)]))
        for i in range(count):positions.append((first['s_m']+span*i/count)%length)
    if line['shape']=='radial':positions.append(length)
    positions=sorted(positions)
    if len(positions)>a['maximum_stations_per_line']:raise ValueError('operating station count exceeds bounded policy')
    stops=[]
    for i,s in enumerate(positions):
        junction_ids=[j for anchor in anchors if abs(anchor['s_m']-s)<.5 for j in anchor['junction_ids']]
        stops.append(dict(id=f"{line['name']}-operating-{i+1:04d}",line=line['name'],s_m=s,**point_at(path,s),
            passenger_stop=True,mandatory_junction_ids=junction_ids,retained_access_station_ids=[],site_approved=False))
    assignments=[];ratio=length/line['length_m']
    for raw_stop in raw:
        s=raw_stop['s_m']*ratio
        def separation(stop):
            gap=abs(stop['s_m']-s)
            return min(gap,length-gap) if line['shape']=='ring' else gap
        chosen=min(stops,key=separation);offset=separation(chosen)
        chosen['retained_access_station_ids'].append(raw_stop['id'])
        assignments.append(dict(retained_station_id=raw_stop['id'],operating_station_id=chosen['id'],retained_station=raw_stop,
            along_route_access_offset_m=offset,catchment_connection_designed=False,retained_location_served_exactly=offset<.01))
    return dict(stations=stops,retained_station_assignments=assignments,transfer_hubs=crossings,spacing_conflicts=conflicts,
        terminal_transfer_access_proposals=terminal_access,
        service_class=service_class,minimum_spacing_m=minimum,target_spacing_m=target,maximum_spacing_m=maximum,
        classification='explicit suburban scenario' if service_class=='suburban' else 'default urban planning assumption; no suburban land-use inference',
        physical_switches_proposed=0,fixed_line_alignments_preserved=True,straight_corridors_demonstrated=None)


def dense_benchmark_station_count(path,line,retained):
    """Reproduce the previous350m-anchor/1km-fill layout as a named comparison."""
    length=path['length_m'];scale=length/line['length_m'];positions=sorted(s['s_m']*scale for s in retained)
    if line['shape']=='radial':positions=sorted(set([0.,length,*positions]))
    anchors=[]
    for s in positions:
        if not anchors or s-anchors[-1]>=350.:anchors.append(s)
    if line['shape']=='radial':
        while len(anchors)>1 and length-anchors[-1]<350.:anchors.pop()
        if not anchors or anchors[-1]!=length:anchors.append(length)
    else:
        while len(anchors)>1 and length-anchors[-1]+anchors[0]<350.:anchors.pop()
    if len(anchors)<2:anchors=sorted([positions[0],(positions[0]+length/2)%length])
    gaps=[q-p for p,q in zip(anchors,anchors[1:])]
    if line['shape']=='ring':gaps.append(length-anchors[-1]+anchors[0])
    return sum(max(1,math.ceil(gap/1000.)) for gap in gaps)+(line['shape']=='radial')


def straight_alignment_candidate(path,line,transfer_hubs):
    """Unselected fixed-node chord geometry; source civil classes do not transfer."""
    nodes=[(row['s_m'],row['exact_crossing_coordinate'],row['id']) for row in transfer_hubs]
    if line['shape']=='radial':nodes.extend([(0.,path['points'][0][:2],'start'),(path['length_m'],path['points'][-1][:2],'end')])
    elif len(nodes)<3:
        for i in range(3):
            p=point_at(path,path['length_m']*i/3);nodes.append((path['length_m']*i/3,[p['lon'],p['lat']],f'proposed-ring-bend-{i}'))
    nodes.sort();filtered=[]
    for node in nodes:
        if filtered and distance(filtered[-1][1],node[1])<.1:continue
        filtered.append(node)
    coordinates=[node[1] for node in filtered]
    if line['shape']=='ring' and coordinates:coordinates.append(coordinates[0])
    length=sum(distance(p,q) for p,q in zip(coordinates,coordinates[1:]))
    return dict(id=line['name']+'-straight-fixed-node-alternative',coordinates=coordinates,
        node_ids=[node[2] for node in filtered],proposed_length_m=length,retained_polyline_length_m=path['length_m'],
        selected=False,source_transfer_crossings_preserved=True,train_switches=0,
        geometry_scope='Straight geographic chords between retained passenger-transfer/terminal nodes; bends, grades and clearances unqualified',
        existing_civil_classification_reused=False,ordinary_civil_price_usd=None,special_structure_price_usd=None,
        obstacle_water_land_utilities_ground_and_new_civil_classification_accepted=False,engineering_accepted=False)


def physical_installations(c,f,line,path,stops,trips):
    from . import booster_kit
    length=path['length_m'];boosters=[]
    for i,motion in enumerate(trips):
        destination=(i+1)%len(stops)
        for zone in motion.get('installed_zones',[]):
            if zone['id'] in ('departure','arrival'):
                stop=stops[i if zone['id']=='departure' else destination]
                relative_start=zone['start_m']-(motion['distance_m'] if zone['id']=='arrival' else 0.)
                relative_end=zone['end_m']-(motion['distance_m'] if zone['id']=='arrival' else 0.)
                stop['power_winding_length_m']=max(stop.get('power_winding_length_m',0.),zone['length_m'])
                stop['power_winding_start_m']=min(stop.get('power_winding_start_m',relative_start),relative_start)
                stop['power_winding_end_m']=max(stop.get('power_winding_end_m',relative_end),relative_end)
                stop['power_coordinate_basis']='Each direction has its own winding about the berthing datum; no shared converter/field qualification'
            else:
                centre=(stops[i]['s_m']+(zone['start_m']+zone['end_m'])/2)%length
                boosters.append(dict(id=f"{line['name']}-leg-{i+1}-{zone['id']}",leg=i+1,
                    kind='fixed-nonpassenger-top-up',passenger=False,s_m=centre,**point_at(path,centre),
                    forward_start_s_m=stops[i]['s_m']+zone['start_m'],forward_end_s_m=stops[i]['s_m']+zone['end_m'],
                    reverse_start_s_m=stops[i]['s_m']+motion['distance_m']-zone['end_m'],
                    reverse_end_s_m=stops[i]['s_m']+motion['distance_m']-zone['start_m'],
                    directions=2,length_m_per_direction=zone['length_m'],electrical_sections_per_direction=zone['electrical_sections'],
                    converter_rating=zone['converter_rating'],mechanical_takeoff=booster_kit.takeoff(zone['length_m'],2),
                    protected_resources_required=True,independent_grid_braking_heat_and_qa_required=True,
                    services_charger=False,site_approved=False,hardware_qualified=False))
    for stop in stops:
        if 'power_winding_length_m' not in stop:
            stop.update(power_winding_length_m=350.,power_winding_start_m=-150.,power_winding_end_m=200.,
                power_geometry_scope='Unconfirmed fallback allocation for held adjacent motion; not selected hardware')
    intervals=max(1,math.ceil(length/1000.));count=intervals if line['shape']=='ring' else intervals+1
    nodes=[dict(id=f"{line['name']}-rescue-{i+1:04d}",s_m=length*i/intervals,**point_at(path,length*i/intervals),
        one_way_kits=2,access_approved=False,station_booster_colocation_credit=False) for i in range(count)]
    reference=booster_kit.recovery(c,cars=f['cars'],distance_m=min(length,5000.),runtime_s=max(t.get('runtime_s',100.) for t in trips),
        post_spacing_m=min(1000.,length),pack_kwh=c['power']['services_battery_kwh_per_car'],
        dwell_s=max(t.get('dwell_s',60.) for t in trips),connected_fraction=min((t.get('connected_fraction',.75) for t in trips),default=.75))
    return dict(powered_top_up_zones=boosters,rescue_nodes=nodes,rescue_kit_reference=reference,
        rescue_kit_count=sum(node['one_way_kits'] for node in nodes),rescue_placement_accepted=False,
        rescue_scope='Independent one-way kits at located nodes no more than1km apart, including line ends; no colocation or ordinary-foundation credit. Terminal curved cable paths remain unqualified')


def plan_line(c,f,line,retained,features,*,interchanges=(),service_class='urban'):
    a=load();validate_strategy(c,a);path=route_path(features,line);length=path['length_m'];ratio=length/line['length_m']
    raw=sorted(deepcopy(retained),key=lambda row:row['s_m'])
    layout=passenger_layout(path,line,raw,interchanges,service_class=service_class)
    stops=layout['stations'];assignments=layout['retained_station_assignments'];minimum=layout['minimum_spacing_m']
    for stop in stops:
        stop.update(platform_length_m=f['overall_length_assumption_m']+10.,platform_is_proposed=True)
    distances=[q['s_m']-p['s_m'] for p,q in zip(stops,stops[1:])]
    if line['shape']=='ring':distances.append(length-stops[-1]['s_m']+stops[0]['s_m'])
    trips=[]
    for d in distances:
        if d<max(350.,f['overall_length_assumption_m']+275.):
            trips.append(dict(schema=SCHEMA,study_pass=False,distance_m=d,terminal=False,rejected_attempts=[],
                reason='Route is too short for separated station windings and complete protected-train clearance',**model.FLAGS))
        else:trips.append(wide_trip(c,f,d,service_class=service_class))
    loops=[]
    if line['shape']=='radial':
        for name,at_start in [('start',True),('end',False)]:
            endpoint=point_at(path,0. if at_start else length)
            pts=path['points'][:2] if at_start else path['points'][-2:]
            mean_lat=math.radians(endpoint['lat']);tangent=((pts[1][0]-pts[0][0])*math.cos(mean_lat),pts[1][1]-pts[0][1])
            curve=terminal_geometry(endpoint,tangent,at_start=at_start)
            section=curve['length_m']/a['terminal_sections'];motion=trip(c,f,section,terminal=True)
            zones=[dict(id=f"{line['name']}-{name}-service-{i}",chainage_m=section*i,
                winding_start_m=section*i+a['terminal_winding_start_m'],
                winding_end_m=section*i+a['terminal_winding_end_m'],**_curve_point(curve,section*i),
                passenger_platform=False,site_approved=False) for i in range(1,a['terminal_sections'])]
            loops.append(dict(id=line['name']+'-'+name,geometry=curve,sections=a['terminal_sections'],
                section_length_m=section,motion=motion,service_zones=zones,
                one_way_zone_cost_basis='Conservatively purchase a complete two-direction station electrical package per added service zone;150m winding case,unquoted',
                landing_curve_phase_guidance_and_land_accepted=False))
    installed=physical_installations(c,f,line,path,stops,trips)
    return dict(schema=SCHEMA,line=line['name'],policy=a,retained_station_count=len(raw),operating_station_count=len(stops),**installed,
        straight_alignment_alternative=straight_alignment_candidate(path,line,layout['transfer_hubs']),
        retained_dense_benchmark=dict(role='retained-1000m-component-benchmark',passenger_stops=dense_benchmark_station_count(path,line,raw),nominal_runtime_s=88.,target_spacing_m=1000.,not_current_operating_plan=True),
        added_operating_sites_without_exact_retained_stop=sum(not s['retained_access_station_ids'] for s in stops),
        consolidated_access_records=sum(not r['retained_location_served_exactly'] for r in assignments),
        measured_polyline_length_m=length,retained_chainage_length_m=line['length_m'],chainage_scale=ratio,
        chainage_mapping='Retained chainage fraction mapped to geodesic polyline arclength; no surveyed alignment assertion',
        stations=stops,retained_station_assignments=assignments,trips=trips,terminal_loops=loops,
        transfer_hubs=layout['transfer_hubs'],spacing_conflicts=layout['spacing_conflicts'],service_class=service_class,
        terminal_transfer_access_proposals=layout['terminal_transfer_access_proposals'],
        passenger_spacing_screen_pass=not layout['spacing_conflicts'],service_classification=layout['classification'],
        minimum_passenger_spacing_m=minimum,target_passenger_spacing_m=layout['target_spacing_m'],
        average_passenger_spacing_m=sum(distances)/len(distances),fixed_line_alignments_preserved=True,straight_corridors_demonstrated=None,physical_train_switches_proposed=0,
        flat_mainline_screen_pass=all(r.get('kinematic_screen_pass',r['study_pass']) for r in trips),
        terminal_longitudinal_screen_pass=all(loop['motion']['study_pass'] and loop['geometry']['lateral_screen_pass'] for loop in loops),
        route_site_approval=False,capacity_and_timetable_approved=False,
        missing_evidence=['survey/land/utilities and foundations for every proposed station and loop',
            'access/catchment connections for consolidated retained demand stations',
            'curved six-car magnetic phase,guidance and clearance tests',
            'station/current/voltage/thermal hardware qualification','network disturbance/berth/loop traffic assurance'],
        **model.FLAGS)
