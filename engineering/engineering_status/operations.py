"""Explicit service and transfer constraints; retained planning is not a new train."""
from pathlib import Path
import json
import math
from hashlib import sha256
from . import ROOT,FLAGS
from .contracts import identity

CITY='cities/catalogue/west-asia/Iraq/Baghdad/engineering/maglev/summary.json'
ACCESS='docs/design-engine/ferrite-maglev/hub-access/geometry.json'
POLICY=dict(normal_passengers_per_car=120,cars=6,target_pphpd=14400,
    maximum_walking_time_s=300.,maximum_horizontal_transfer_m=300.,
    ordinary_walk_speed_m_s=1.,accessible_slow_walk_speed_m_s=.6,
    scope='New research comparison constraints; no city or station layout adoption',adopted=False)


def capacity(headway_s,passengers=720):
    if type(headway_s) not in (float,int) or not math.isfinite(headway_s) or headway_s<=0:raise ValueError('finite positive headway required')
    if type(passengers) is not int or passengers<=0:raise ValueError('positive explicit normal passenger count required')
    return passengers*3600/headway_s


def transfer(distance_m,speed_m_s):
    if any(type(v) not in (int,float) or not math.isfinite(v) for v in (distance_m,speed_m_s)) or distance_m<0 or speed_m_s<=0:
        raise ValueError('finite distance and positive walking speed required')
    seconds=distance_m/speed_m_s
    return dict(horizontal_walk_m=distance_m,assumed_speed_m_s=speed_m_s,walking_seconds=seconds,
        comparison_screen_pass=distance_m<=POLICY['maximum_horizontal_transfer_m'] and seconds<=POLICY['maximum_walking_time_s'],
        includes_vertical_lifts_queues_wait_weather=False,accessible_route_qualified=False)


def study(root=ROOT):
    root=Path(root);city=json.loads((root/CITY).read_bytes());access=json.loads((root/ACCESS).read_bytes())
    lines=[]
    for line in city['lines']:
        count=line['formation']['aw2_passengers'];headway=line['selected_peak_headway_seconds'];calculated=capacity(headway,count)
        if not math.isclose(calculated,line['aw2_capacity_per_direction_hour'],rel_tol=1e-10):raise ValueError('retained city capacity/headway accounting differs')
        lines.append(dict(line=line['line'],selected_headway_s=headway,normal_passengers_per_train=count,
            capacity_pphpd=calculated,required_headway_s=count*3600/POLICY['target_pphpd'],
            capacity_target_screen_pass=calculated>=POLICY['target_pphpd'],actual_new_candidate_compatible=False,
            actual_support_braking_protection_qualified=False))
    pairs=[]
    for p in access['platform_transfer_walk_matrix']['pairs']:
        pairs.append(dict(from_platform=p['from_platform'],to_platform=p['to_platform'],
            ordinary=transfer(p['horizontal_walk_m'],POLICY['ordinary_walk_speed_m_s']),
            accessible_slow_walk=transfer(p['horizontal_walk_m'],POLICY['accessible_slow_walk_speed_m_s'])))
    variants=[dict(headway_s=h,capacity_pphpd=capacity(h),capacity_target_screen_pass=capacity(h)>=POLICY['target_pphpd'],
        actual_safe_headway_qualified=False,changed_fleet_and_station_costs=None) for h in (180.,210.,240.,300.,360.)]
    value=dict(schema='osr-equal-service-transfer-constraints/1',policy=POLICY,retained_lines=lines,retained_transfer_pairs=pairs,
        headway_comparisons=variants,retained_city_totals=city['totals'],
        retained_lines_below_target=sum(not x['capacity_target_screen_pass'] for x in lines),
        maximum_retained_horizontal_transfer_m=max(p['ordinary']['horizontal_walk_m'] for p in pairs),
        source_sha256={name:sha256((root/name).read_bytes()).hexdigest() for name in (CITY,ACCESS)},
        scope='Retained planning inputs and explicit new service constraints; no new operating, site or cost acceptance',**FLAGS)
    value['evaluation_id']=identity(value);return value
