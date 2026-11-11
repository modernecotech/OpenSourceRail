"""Sealed explicit-headway projection over unchanged city physical leg models."""
from copy import deepcopy
from math import ceil
from pathlib import Path

from engineering.station_rail import ROOT
from engineering.station_rail.common import identity,digest
from . import city_service,planning_adapter

PRODUCER='engineering/outline/revision_service.py'
_LOADED={PRODUCER:digest(__file__),city_service.PRODUCER:digest(city_service.__file__),
    planning_adapter.PRODUCER:digest(planning_adapter.__file__)}


def project(service,request,requirements):
    value=deepcopy(service)
    if service.get('evaluation_id')!=identity({k:v for k,v in service.items() if k!='evaluation_id'}):
        raise ValueError('Sealed base city service required')
    h=planning_adapter.geometry.number(request['headway_s'],'explicit headway',10,86400)
    old_h=service['requirements']['headway_s'];r=deepcopy(service['requirements']);r['headway_s']=h
    active=value['fleet_direction_multiplier']*ceil(value['round_trip_s']/h)
    spare=ceil(active*value['design']['reserve_fraction'])
    value.update(requirements=r,active_trainsets=active,spare_trainsets=spare,total_trainsets=active+spare,totalcars=6*(active+spare),
        capacity_pphpd=value['normal_places_per_train']*3600/h,
        planning_usable_capacity_pphpd=value['normal_places_per_train']*3600/h*requirements.get('planning_occupancy',.85)*requirements.get('planning_availability_assumption',.99))
    # An unchanged service is the identity projection. Multiplying then dividing
    # by the same headway can move a float by one ULP and alter cost subtotals.
    if h!=old_h:
        value.update(train_km_per_day=service['train_km_per_day']*old_h/h,
            departures_per_day=service['departures_per_day']*old_h/h)
    parallel=ceil(value['berth_resource_s']/h)
    positions=ceil((value['design']['terminal_turnback_s']+max(x['braking_time_s'] for x in request['legs'])+value['tail_clearance_s_jerk_bound'])/h) if value['baseline_budget_positions_per_end'] else 0
    value.update(minimum_parallel_berth_resources=parallel,additional_berth_edges=2*r['stations']*(parallel-1),
        berth_headway_necessary_screen='pass' if parallel==1 else 'parallel-protected-berths-required',
        minimum_turnback_positions_per_end=positions,terminal_additional_positions=2*max(0,positions-2))
    value.pop('evaluation_id');value['evaluation_id']=identity(value);return value


def _capacity_check(row,requirements):
    demand=row['requirements'].get('peak_demand_pphpd',requirements.get('peak_demand_pphpd'))
    if demand is None:raise ValueError('Explicit line or revision demand required')
    return dict(line_id=row['line_id'],capacity_pass=row['service']['planning_usable_capacity_pphpd']>=demand,
        headway_pass=row['requirements']['headway_s']<=requirements.get('maximum_headway_s',300.),
        demand_pphpd=demand,requested_headway_s=row['requirements']['headway_s'],actual_availability_proven=False)


def evaluate(revision,design,vehicle,root=ROOT):
    if revision.get('evaluation_id')!=identity({k:v for k,v in revision.items() if k!='evaluation_id'}):raise ValueError('Sealed planning revision required')
    sources=planning_adapter.merge_sources(revision['source_sha256'],_LOADED)
    planning_adapter._sources(root,sources)
    result=city_service.evaluate(revision['city_input'],revision['requirements'],{**design,**(revision.get('requested_design') or {})},vehicle,root=root)
    result=deepcopy(result);checks=[]
    for row in result['line_services']:
        requested=deepcopy(revision['service_requests'][row['line_id']]);requested['legs']=row['legs']
        row['service']=project(row['service'],requested,revision['requirements']);row['requirements']=deepcopy(row['service']['requirements'])
        row['requested_service']=deepcopy(revision['service_requests'][row['line_id']])
        row['dwell_adjustment']=dict(requested_minimum_dwell_s=requested['dwell_s'],
            calculated_stop_dwell_s=deepcopy(row['service'].get('stop_dwell_s',[])),
            automatic_adjustment_applied=any(x>requested['dwell_s'] for x in row['service'].get('stop_dwell_s',[])),
            basis='Explicit calculated amendment for declared reference and nominal hotel charging; not a validated timetable')
        checks.append(_capacity_check(row,revision['requirements']))
        row['source_sha256']=planning_adapter.merge_sources(row['source_sha256'],_LOADED)
        row.pop('evaluation_id');row['evaluation_id']=identity(row)
    result['summary'].update(total_trainsets=sum(r['service']['total_trainsets'] for r in result['line_services']),
        totalcars=sum(r['service']['totalcars'] for r in result['line_services']))
    result.update(functional_checks=checks,functional_pass=all(c['capacity_pass'] and c['headway_pass'] for c in checks) and revision['access_screen']['status']=='pass',
        explicit_service_requests=deepcopy(revision['service_requests']),planning_revision_id=revision['planning_revision_id'],
        source_sha256=planning_adapter.merge_sources(result['source_sha256'],_LOADED),provisional_costing_permitted=True)
    result.pop('evaluation_id');result['evaluation_id']=identity(result);return result
