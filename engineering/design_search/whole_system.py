"""Bounded equal-service fleet/winding tradeoffs, not a priced railway selection.

The selected six-car geometry is retained. Increased occupancy is explicitly a
load/layout hypothesis, not a silently recertified comfort car. All force and
power values are requirements; no available propulsion or safe headway is assumed.
"""
from collections import Counter
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import argparse
import gzip
import itertools
import json
import math
import subprocess

from engineering.development_baseline import selection
from engineering.comfort_design import service, system_tradeoff

ROOT=Path(__file__).resolve().parents[2]
CODE='engineering/design_search/whole_system.py'
FLAGS=dict(physical_accepted=False,engineering_accepted=False,operating_release=False,
           manufacturing_release=False,complete_installed_mass=False,economic_superiority_demonstrated=False)
LIBRARY=(350.,450.,600.,800.,900.,1000.)


def _finite(x,name):
    if type(x) not in (int,float) or not math.isfinite(x) or x<=0:raise ValueError('Positive finite '+name+' required')
    return float(x)


def capacity(cars,people,headway):
    return _finite(cars,'cars')*_finite(people,'people')*3600/_finite(headway,'headway')


@lru_cache(maxsize=8192)
def profile(distance,speed,mass):
    return service.motion_profile(distance,speed,.4,.6,mass,1000.,1.8)


@lru_cache(maxsize=32768)
def zone(distance,speed,mass,dwell,length):
    p=profile(distance,speed,mass)
    if p['runtime_s'] is None:return None
    z=service.motor_zone(p,length,104.5,dwell)
    keys=('length_m','start_m','end_m','station_id','geometry_full_engagement',
          'no_powered_overlap_during_required_force','minimum_nominal_resource_interval_s',
          'required_peak_train_mechanical_kW','full_engagement_bound_m')
    return {k:z[k] for k in keys}


def choose_zone(distance,speed,mass,dwell,headway,maximum):
    # motor_zone exposes a120s comparison too. Use its actual resource interval
    # for the requested headway; never reuse that hardcoded screen at90/180s.
    for length in LIBRARY:
        if length>maximum:continue
        z=zone(distance,speed,mass,dwell,length)
        if (z is not None and z['geometry_full_engagement']
            and not z['no_powered_overlap_during_required_force']
            and z['minimum_nominal_resource_interval_s']<=headway+1e-9):return z
    return None


def continuous_traction_lower_bound(distance,speed=20.):
    """Ideal kinematics only: same acceleration/dwell, continuous supplied force."""
    distance=_finite(distance,'distance');speed=_finite(speed,'speed')
    v=min(speed,math.sqrt(2*distance/(1/.4+1/.6)))
    return v/.4+v/.6+max(0.,distance-v*v/(2*.4)-v*v/(2*.6))/v


def line_result(line,mass,speed,headway,maximum,dwell=35.):
    stations={r['id']:r['s_m'] for r in line['stations']};limits=min(stations.values()),max(stations.values())
    moving=continuous=launch=net=wind=peak_power=0.;margin=None
    coast_fail=[];zone_fail=[];intervals={-1:[],1:[]};counts=Counter();events=0;terminals=0
    for event in line['duty']['arrival_events_per_circuit']:
        if event['terminal_loop_allowance']:
            moving+=event['moving_seconds'];continuous+=event['moving_seconds'];terminals+=1;continue
        events+=1;D=event['distance_m'];p=profile(D,speed,mass)
        continuous+=continuous_traction_lower_bound(D,speed)
        if p['runtime_s'] is None:
            coast_fail.append(dict(distance_m=D,reason=p['failure']));continue
        moving+=p['runtime_s'];launch+=p['launch_mechanical_kWh_per_train'];net+=p['net_station_work_kWh_per_train']
        z=choose_zone(D,speed,mass,dwell,headway,maximum)
        if z is None:
            zone_fail.append(dict(distance_m=D,reason='No full-engagement option within length/headway bounds'));continue
        wind+=z['length_m'];counts[str(int(z['length_m']))]+=1
        peak_power=max(peak_power,z['required_peak_train_mechanical_kW'])
        value=headway-z['minimum_nominal_resource_interval_s'];margin=value if margin is None else min(margin,value)
        origin=event['origin_station'].removesuffix('-outgoing');destination=event['destination_station'].removesuffix('-outgoing')
        direction=1 if stations[destination]>stations[origin] else -1;at=stations[destination]
        ends=(at+direction*z['start_m'],at+direction*z['end_m']);intervals[direction].append((min(ends),max(ends)))
    cycle=moving+dwell*(events+terminals) if not coast_fail else None
    def fleet(cycle):
        active=math.ceil(cycle/headway);return dict(active=active,spare=math.ceil(.12*active),cold=1,total=active+math.ceil(.12*active)+1)
    unions=[system_tradeoff.interval_union(intervals[d],*limits) for d in (-1,1)]
    return dict(line=line['line'],coast_failures=coast_fail,station_library_failures=zone_fail,
        circuit_s=cycle,fleet=None if cycle is None else fleet(cycle),
        direction_winding_m=wind if not coast_fail and not zone_fail else None,
        counted_winding_lower_bound_m=wind,station_library_counts=dict(sorted(counts.items())),
        minimum_resource_margin_s=margin,required_peak_train_mechanical_kW=peak_power if not coast_fail and not zone_fail else None,
        mainline_launch_mechanical_kWh_per_circuit=launch if not coast_fail else None,
        net_mechanical_station_work_kWh_per_circuit=net if not coast_fail else None,
        motor_interval_overlap_count=sum(r['overlap_pairs'] for r in unions),
        motor_union_m=sum(r['union_m'] for r in unions),directional_mainline_length_m=2*(limits[1]-limits[0]),
        continuous_traction_kinematic_fleet_lower_bound=fleet(continuous+dwell*(events+terminals)),
        continuous_traction_actual_vehicle_mass_price_power_and_braking=None)


def _sources(root,selected):
    result=dict(selected['source_sha256'])
    for name in (CODE,'engineering/comfort_design/service.py','engineering/comfort_design/system_tradeoff.py',service.CITY):
        path=Path(__file__) if name==CODE else root/name
        result[name]=sha256(path.read_bytes()).hexdigest()
    return dict(sorted(result.items()))


def pareto(rows):
    names=('trainsets','direction_winding_m','required_peak_train_mechanical_kW','net_mechanical_kWh_per_peak_hour')
    result=[]
    for row in rows:
        if any(row.get(k) is None for k in names):continue
        dominated=any(other is not row and all(other[k]<=row[k] for k in names)
                      and any(other[k]<row[k] for k in names) for other in rows)
        if not dominated:result.append(row['scenario_id'])
    return sorted(result)


def quoted_cost(row,quotes):
    """Unknown quotes never become zero; all declared scope terms are required."""
    required=('trainset_USD','direction_winding_USD_per_m','guideway_USD_per_direction_m',
              'other_station_CAPEX_USD','depot_CAPEX_USD','present_value_OPEX_renewals_USD')
    if any(quotes.get(k) is None for k in required):return None
    if any(type(quotes[k]) not in (int,float) or not math.isfinite(quotes[k]) or quotes[k]<0 for k in required):
        raise ValueError('Finite nonnegative explicitly quoted cost terms required')
    if row['trainsets'] is None or row['direction_winding_m'] is None:return None
    return (row['trainsets']*quotes['trainset_USD']+row['direction_winding_m']*quotes['direction_winding_USD_per_m']
            +row['directional_mainline_length_m']*quotes['guideway_USD_per_direction_m']
            +sum(quotes[k] for k in required[3:]))


def evaluate(root=ROOT):
    root=Path(root).resolve();selected=selection.load(root);vehicle=selected['vehicle']
    source=json.loads((root/service.CITY).read_bytes());tare=vehicle['mass']['accounted_tare_kg_per_car'];rows=[]
    for passengers,headway,speed,maximum in itertools.product((46,64,80,120),(60.,90.,120.,150.,180.,240.,360.),(15.,20.),(600.,800.,1000.)):
        mass=tare+75*passengers
        definition=dict(parent_candidate_id=vehicle['candidate_id'],cars=6,normal_people_per_car_hypothesis=passengers,
            headway_s=headway,launch_cap_m_s=speed,maximum_shared_station_winding_m=maximum,
            dwell_s=35.,accounted_tare_kg_per_car=tare,passenger_mass_kg=75.,acceleration_m_s2=.4,deceleration_m_s2=.6,
            constant_drag_N_per_car=1000.,quadratic_drag_N_per_car_per_m_s_squared=1.8,grade=0.,
            existing_routes_and_stops_retained=True,new_layout_and_mass_required=passengers!=46)
        lines=[line_result(line,mass,speed,headway,maximum) for line in source['lines']]
        reach=all(not r['coast_failures'] for r in lines);station=reach and all(not r['station_library_failures'] for r in lines)
        row=dict(scenario_id=selection.identity(definition),definition=definition,lines=lines,
            normal_capacity_pphpd=capacity(6,passengers,headway),nominal_wait_s=headway/2,
            fixed_seat_share_hypothesis=44/passengers,standing_or_new_seating_places_required=passengers-46,
            current_layout_supports_this_occupancy=passengers==46,
            trainsets=sum(r['fleet']['total'] for r in lines) if reach else None,
            active_trainsets=sum(r['fleet']['active'] for r in lines) if reach else None,
            direction_winding_m=sum(r['direction_winding_m'] for r in lines) if station else None,
            required_peak_train_mechanical_kW=max(r['required_peak_train_mechanical_kW'] for r in lines) if station else None,
            net_mechanical_kWh_per_peak_hour=3600/headway*sum(r['net_mechanical_station_work_kWh_per_circuit'] for r in lines) if reach else None,
            launch_mechanical_kWh_per_peak_hour=3600/headway*sum(r['mainline_launch_mechanical_kWh_per_circuit'] for r in lines) if reach else None,
            hotel_kWh_per_peak_hour_per_kW_per_car=6*sum(r['fleet']['active'] for r in lines) if reach else None,
            directional_mainline_length_m=sum(r['directional_mainline_length_m'] for r in lines),
            mainline_motor_coverage_fraction=sum(r['motor_union_m'] for r in lines)/sum(r['directional_mainline_length_m'] for r in lines) if station else None,
            motor_interval_overlaps=sum(r['motor_interval_overlap_count'] for r in lines),
            coast_failed_lines=sum(bool(r['coast_failures']) for r in lines),station_failed_lines=sum(bool(r['station_library_failures']) for r in lines),
            analytical_resource_screen='pass' if station else 'fail',actual_safe_headway_s=None,
            continuous_traction_ideal_fleet_lower_bound=sum(r['continuous_traction_kinematic_fleet_lower_bound']['total'] for r in lines),
            complete_whole_life_cost_USD=None,rankable_as_integrated_engineering_candidate=False,**FLAGS)
        rows.append(row)
    baseline=next(r for r in rows if (r['definition']['normal_people_per_car_hypothesis'],r['definition']['headway_s'],r['definition']['launch_cap_m_s'],r['definition']['maximum_shared_station_winding_m'])==(46,120.,20.,1000.))
    comparisons=[]
    for floor in (8280.,14400.):
        comparable=[r for r in rows if r['normal_capacity_pphpd']>=floor-1e-8 and r['definition']['headway_s']<=120 and r['analytical_resource_screen']=='pass']
        comparisons.append(dict(required_capacity_pphpd=floor,maximum_headway_s=120.,
            comparable_scenario_ids=[r['scenario_id'] for r in comparable],quantity_pareto_scenario_ids=pareto(comparable),
            comfort_layout_only_scenario_ids=[r['scenario_id'] for r in comparable if r['current_layout_supports_this_occupancy']],
            integrated_eligible_candidate_ids=[],economic_winner=None))
    coefficients=[]
    for row in rows:
        if row['analytical_resource_screen']!='pass' or row['definition']['normal_people_per_car_hypothesis']!=46 or row['definition']['headway_s']!=120:continue
        coefficients.append(dict(scenario_id=row['scenario_id'],saved_trainsets=baseline['trainsets']-row['trainsets'],
            extra_winding_m=row['direction_winding_m']-baseline['direction_winding_m'],
            comparison='Samecomfortcapacity8280pphpd and120s interval; allothercostdifferences remain explicit unknowns',
            break_even_equation='extra_winding_m * winding_USD_per_m = saved_trainsets * trainset_USD - other_extra_CAPEX_USD - PV_extra_OPEX_USD',
            actual_cost_difference_USD=None))
    result=dict(schema='osr-equal-service-whole-system-study/1',parent_selection_id=selected['selection_id'],
        parent_candidate_id=vehicle['candidate_id'],parent_body_candidate_id=vehicle['body_candidate_id'],
        parent_magnet_component_id=vehicle['magnet_component_id'],source_sha256=_sources(root,selected),
        scenarios=rows,current_default_scenario_id=baseline['scenario_id'],comparisons=comparisons,
        same_comfort_cost_coefficients=coefficients,
        wheel_rail_comparator=dict(scope='Continuous-traction ideal-kinematic fleet lower bound, not a designed or priced railvehicle',
            same_route_dwell_acceleration_and_spare_hypotheses=True,
            actual_equipped_rail_vehicle_mass_kg=None,actual_wheel_rail_CAPEX_USD=None,
            rail_braking_power_energy_and_grade_qualified=False,
            equal_service_cost_equation='DeltaPV = Fmag*Pmag - Frail*Prail + Ldir*(Gmag-Grail) + Wmag*Pwind - Ccontinuous_power + DeltaStationsDepots + PV_DeltaOPEXRenewals',
            omitted_cost_terms_are_zero=False,lowest_cost_architecture_demonstrated=False),
        selected_default_is_economic_winner=False,development_default_changed=False,
        physical_scope='Motion/resource requirements under flat-route C+Qv2 hypotheses; actual support, propulsion, thermal and brake maps unavailable',
        alternative_occupancy_scope='64/80/120-person rows require a different verified layout/admission and possiblyequipment mass. Tare is held as an explicit sensitivity, not a newinstalledbodyclaim.',
        budget=dict(scenarios=len(rows),cities=1,lines=len(source['lines']),native_physical_runs=0),**FLAGS)
    result['evaluation_id']=selection.identity(result);return result


def compact(value):
    excluded={'lines'}
    return dict(**{k:v for k,v in value.items() if k!='scenarios'},scenarios=[{k:v for k,v in r.items() if k not in excluded} for r in value['scenarios']])


def run(output,root=ROOT):
    output=Path(output);output.mkdir(parents=True,exist_ok=False);value=evaluate(root)
    (output/'results.json.gz').write_bytes(gzip.compress(selection.encoded(value),mtime=0))
    (output/'summary.json').write_bytes(selection.encoded(compact(value)))
    files={p.name:sha256(p.read_bytes()).hexdigest() for p in output.iterdir()}
    manifest=dict(schema='osr-equal-service-study-publication/1',evaluation_id=value['evaluation_id'],source_sha256=value['source_sha256'],files_sha256=files,**FLAGS)
    (output/'manifest.json').write_bytes(selection.encoded(manifest));return compact(value)


def verify(output,root=ROOT,replay=True):
    output=Path(output);m=json.loads((output/'manifest.json').read_bytes());v=json.loads(gzip.decompress((output/'results.json.gz').read_bytes()))
    for name,digest in m['files_sha256'].items():
        if Path(name).name!=name or sha256((output/name).read_bytes()).hexdigest()!=digest:raise ValueError('study payload differs')
    selected=selection.load(root)
    if v['source_sha256']!=_sources(Path(root),selected) or m['source_sha256']!=v['source_sha256']:raise ValueError('study sources differ')
    if v['evaluation_id']!=selection.identity({k:x for k,x in v.items() if k!='evaluation_id'}):raise ValueError('study identity differs')
    if replay and v!=evaluate(root):raise ValueError('equal-service calculation does not reproduce')
    if json.loads((output/'summary.json').read_bytes())!=compact(v):raise ValueError('study summary differs')
    return dict(verified=True,replayed=replay,scenarios=len(v['scenarios']),evaluation_id=v['evaluation_id'],**FLAGS)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('command',choices=('run','verify'));p.add_argument('--output',type=Path,required=True);p.add_argument('--root',type=Path,default=ROOT);a=p.parse_args()
    v=run(a.output,a.root) if a.command=='run' else verify(a.output,a.root)
    print(json.dumps({k:v[k] for k in ('evaluation_id','budget') if k in v},sort_keys=True))

if __name__=='__main__':main()
