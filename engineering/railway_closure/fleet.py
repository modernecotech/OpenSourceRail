"""Counted service plans → native causal station-store fleet requests."""
from copy import deepcopy
from pathlib import Path
from math import fsum
import json
from engineering.station_cycle import coordinator as cycle,design
from engineering.station_rail.common import identity
from engineering.station_pair import coordinator as pair
from . import ROOT,FLAGS
from .motion import case
from .electrical import supply_screen
from . import service as service_model


class EnergyDomainHold(ValueError):
    """Completed fleet model exceeds a declared electrical/thermal hypothesis."""


def request(installed,bundle,service,*,enabled=True,experiment='nominal',dt=.05,root=ROOT):
    if (service['candidate_id']!=bundle['candidate_id']
        or service['evaluation_id']!=identity({k:v for k,v in service.items() if k!='evaluation_id'})):
        raise ValueError('Exact canonical timetable required')
    p=design.policy(root);stations=cycle.stations(installed['recovery_design'],p)
    if experiment=='initially-full':
        for s in stations:s['initial_energy_j']=s['store']['capacity_j']
    if experiment=='slow-reset':
        for s in stations:s['reset']['duration_s']=600.
    if experiment=='storage-leakage':
        for s in stations:s['store']['leakage_per_s']=.001
    kwargs={}
    if experiment in ('wet','power-loss','half-drive','emergency-stop'):
        kwargs['fault']=experiment
        if experiment=='half-drive':kwargs['drive_fault_observed']=True
    if experiment=='high-mass':kwargs['mass_case']='high'
    if experiment=='high-mass-low-force':kwargs.update(mass_case='high',force_case='low')
    if experiment=='half-drive-unobserved':kwargs['fault']='half-drive'
    if experiment=='low-mass':kwargs['mass_case']='low'
    if experiment=='up-2pct':kwargs['grade']=.02
    if experiment=='down-2pct':kwargs['grade']=-.02
    if experiment=='headwind':kwargs['wind']=15.
    if experiment=='tailwind-unsupported':kwargs['wind']=-15.
    if experiment=='outside-grade-bound':kwargs.update(grade=-.025,grade_observation=-.02)
    if experiment=='outside-position-bound':kwargs['sensor_biases']=dict(position_bias_m=-2.)
    if experiment=='compound-downhill-boundary':
        from engineering.station_pair import control_policy
        cp=json.loads((Path(root)/control_policy.POLICY).read_bytes())
        kwargs.update(mass_case='high',grade=-.02-cp['grade_error_bound'],grade_observation=-.02,
                      sensor_biases=dict(position_bias_m=-cp['position_error_bound_m'],
                         speed_bias_m_s=-cp['speed_error_bound_m_s'],acceleration_bias_m_s2=-cp['acceleration_error_bound_m_s2']))
    if experiment=='hot-hotel':kwargs['hotel_W_per_car']=50000.
    base=case(installed,candidate_bundle=bundle,dt=dt,root=root,**kwargs)
    base['headway_s']=service['headway_s']
    if experiment=='compound-downhill-boundary':
        base['brake_force_cap_n']*=cp['brake_force_lower_fraction']
        base['brake_latency_s']=cp['reaction_time_bound_s'];base['brake_rise_s']=cp['brake_rise_time_bound_s']
    if experiment=='outside-brake-bound':base['brake_force_cap_n']*=.7
    if experiment=='outside-response-bound':base['brake_latency_s']=2.;base['brake_rise_s']=2.
    base.pop('id');base['id']=identity(base)
    trains=[dict(t,initial_drive_temperature_c=base['thermal']['ambient_c']) for t in service['counted_initial_trains']]
    for i in range(service['spare_trainsets']):
        trains.append(dict(id='reserve-'+str(i),initial_station_id='A',initial_position_m=0.,ready_at_s=0.,
                           role='spare',initial_drive_temperature_c=base['thermal']['ambient_c']))
    departures=[]
    for i,slot in enumerate(service['departures']):
        q=deepcopy(base);station=slot['departure_station_id'];other='B' if station=='A' else 'A'
        if station=='B':q['grade_fraction']*=-1;q['control']['grade_estimate_fraction']*=-1
        q.pop('id');q['id']=identity(q)
        at=slot.get('departure_time_s',slot.get('time_s'))
        row=dict(id=slot['slot_id'],journey=q,departure_station_id=station,arrival_station_id=other,
                 departure_time_s=at,departure_authorized=not(experiment=='no-authority' and i==1),
                 capture_failed=not enabled or experiment=='capture-failed',
                 release_failed=not enabled or experiment=='release-failed',
                 reset_failed=experiment=='reset-failed' and i==0)
        if slot.get('train_id'):row['requested_train_id']=slot['train_id']
        departures.append(row)
    req=dict(candidate_id=bundle['candidate_id'],stations=stations,trains=trains,departures=departures,
             release_control=dict(mode='grid-substitution-slew/1',force_slew_n_s=10000.,maximum_traction_share=.8,reserve_factor=2.),
             turnaround_s=service['hypotheses']['turnaround_maneuver_s'],
             clearance_s=service['hypotheses']['route_release_allowance_s'])
    req['id']=identity(req);return req


def screen(result,service,*,maximum_journey_s=210.,maximum_moving_jerk=.5):
    journeys=[d['journey'] for d in result['departures'] if d['journey'] is not None]
    criteria=dict(counted_schedule=bool(result['schedule_numerical_complete']),
        planning_requirements=service['planned_service_complete'],
        journey_time=bool(journeys) and all(j['elapsed_s']<=maximum_journey_s for j in journeys),
        moving_jerk=bool(journeys) and all(j['maximum_absolute_jerk_m_s3']<=maximum_moving_jerk*1.01 for j in journeys),
        stopping_domain=bool(journeys) and all(j['control']['bounds_valid'] and not j['control']['end_of_authority_violated'] for j in journeys),
        terminal_calendar=terminal_check(result,service)['calendar_screen'],
        repeated_thermal_proxy=bool(result['numerical_thermal_limits_met']))
    return dict(tests=criteria,nominal_model_screen=all(criteria.values()),
                terminal_jerk_qualified=False,protected_service_qualified=False,**FLAGS)


def terminal_check(result,service):
    """Replay actual arrivals against the same counted terminal resource."""
    if result['candidate_id']!=service['candidate_id']:raise ValueError('Mixed terminal timetable')
    duration=service['hypotheses']['turnaround_maneuver_s'];dwell=service['hypotheses']['dwell_s']
    clear=service['hypotheses']['departure_terminal_clearance_s']
    bookings={s:[] for s in ('A','B')};ready={};events=[];sequence=0;rows=[]
    parked={s:0 for s in bookings}
    from heapq import heappush,heappop
    for train in service['counted_initial_trains']:
        ready[train['id']]=(train['initial_station_id'],train['ready_at_s'])
        parked[train['initial_station_id']]+=1
        if train['ready_at_s']>0:bookings[train['initial_station_id']].append((train['ready_at_s']-duration,train['ready_at_s']))
    for slot in service['departures']:
        t=slot.get('departure_time_s',slot.get('time_s'));s=slot['departure_station_id']
        bookings[s].append((t,t+clear))
    for row in result['departures']:
        if row['train_id'] is None:continue
        sequence+=1;heappush(events,(row['departure_time_s'],1,sequence,'departure',row))
        if row['arrival_time_s'] is not None:
            sequence+=1;heappush(events,(row['arrival_time_s'],0,sequence,'arrival',row))
    complete=True;peak_parked=dict(parked)
    while events:
        now,_,__,kind,row=heappop(events);tid=row['train_id']
        if kind=='arrival':
            station=row['arrival_station_id'];start=service_model._gap(now+dwell,duration,bookings[station])
            parked[station]+=1;peak_parked[station]=max(peak_parked[station],parked[station])
            bookings[station].append((start,start+duration));ready[tid]=(station,start+duration)
        else:
            prior=ready.pop(tid,None)
            valid=prior is not None and prior[0]==row['departure_station_id'] and prior[1]<=now+1e-8
            complete&=valid
            if row['journey'] is not None:parked[row['departure_station_id']]-=1
            rows.append(dict(departure_id=row['id'],train_id=tid,departure_s=now,
                             terminal_ready_at_s=None if prior is None else prior[1],resource_ready=valid))
    return dict(calendar_screen=bool(complete) and max(peak_parked.values())<=3,
                peak_parked_active_trainsets=peak_parked,departures=rows,
                assumptions='Same45s finite-jerk necessary-time-screened shared maneuver and30s departure reservations; no physical interlocking proof',
                spare_location='Counted reserve held in separately priced depot; native station label is a dispatch anchor, not a platform pose',
                terminal_geometry_verified=False,operating_release=False)


def energy(result,request,service,*,root=ROOT):
    """Conditional service-energy estimate; no store energy credited in advance.

    Observed finite-run traction/reset work is annualized per completed scheduled
    movement. Cold starts and residual stored energy remain explicitly visible.
    Hotel loads cover every active train over paid service hours, including idle,
    rather than only the brief movements. Spare/depot loads belong to lifecycle.
    """
    if (result['native_input_id']!=identity(request) or result['candidate_id']!=service['candidate_id']
        or not screen(result,service)['nominal_model_screen']):
        raise ValueError('Only exact, fulfilled causal fleet service can annualize energy')
    brief=pair.variants(root)[0]
    policy=json.loads((Path(root)/'engineering/railway_closure/supply-policy.json').read_bytes())
    rows=result['departures'];journeys=[d['journey'] for d in rows if d['journey'] is not None]
    peak=max(j['maximum_grid_power_w'] for j in journeys)
    grid=supply_screen(peak,service['active_trainsets'],service['headway_s'],root=root)
    if not all(r['voltage_hypothesis_screen'] for r in grid['rows']):raise EnergyDomainHold('Voltage hypothesis fails; service energy remains held')
    L=result['ledger'];n=result['requested_departures']
    bank_heat=L['capture_loss_j']+L['release_loss_j']+L['storage_leakage_j']+L['reset_grid_energy_j']
    whole_heat_mean=bank_heat/max(1.,result['simulation_end_time_s'])
    if whole_heat_mean>policy['station_bank_cooling_capacity_W']:
        raise EnergyDomainHold('Even mean whole-system loss heat exceeds one declared bank cooler; per-bank hot duty unresolved')
    hours=brief['operation_hours_day']*brief['operation_days_year']
    departures=2*3600/service['headway_s']*hours
    mean=(L['grid_traction_energy_j']+L['reset_grid_energy_j'])/n/3.6e6
    powers={d['journey']['auxiliary_power_w'] for d in request['departures']}
    if len(powers)!=1:raise ValueError('Mixed auxiliary duties require explicit piecewise integration')
    hotel=powers.pop()/1000
    annual={};breakdown={}
    # Explicit finite cooler capacity is priced/retained; full-capacity operation
    # is a conservative electrical allowance, not a solved fluid/chiller model.
    bank_cooling_kw=2*policy['station_bank_cooling_capacity_W']/policy['station_bank_cooling_COP']/1000
    for i,c in enumerate(('low','base','high')):
        traction=departures*mean
        active_hotel=service['active_trainsets']*hotel*hours/policy['auxiliary_feed_efficiency_cases'][i]
        idle=service['active_trainsets']*policy['drive_idle_electronics_W_per_active_train_cases'][i]/1000*hours
        line_loss=(traction+active_hotel+idle)*grid['rows'][i]['line_loss_fraction_of_delivered_power']
        stations=2*json.loads((Path(root)/'engineering/station_pair/cost-policy.json').read_bytes())['station_auxiliary_W_each'][i]/1000*hours
        cooling=bank_cooling_kw*hours if any(s['store']['capacity_j']>0 for s in request['stations']) else 0.
        annual[c]=traction+active_hotel+line_loss+idle+stations+cooling
        breakdown[c]=dict(traction_and_reset_kwh=traction,all_active_hotel_kwh=active_hotel,
                          bounded_line_loss_kwh=line_loss,idle_drive_electronics_kwh=idle,
                          station_auxiliary_kwh=stations,bank_cooling_kwh=cooling)
    v=dict(schema='osr-railway-closure-service-energy/1',candidate_id=service['candidate_id'],
        service_evaluation_id=service['evaluation_id'],native_fleet_evaluation_id=result['evaluation_id'],
        native_fleet_receipt_id=result['native_receipt_id'],native_fleet_input_id=result['native_input_id'],
        service_fulfilled=True,annual_grid_kwh=annual,breakdown=breakdown,
        finite_run_initial_store_j=L['initial_store_j'],finite_run_final_store_j=L['final_store_j'],
        bank_heat_mean_upper_per_station_W=whole_heat_mean,
        bank_local_transients_verified=False,
        maximum_train_drive_grid_W=peak,supply_screen=grid,
        basis='Conditional model estimate from exact counted timetable/fleet work; all active train hotel/idle and positive grid/cooling allowances. No unspent store credit, no physical operating or electricity guarantee.',
        uncertainties=['Unmeasured drive/store hot efficiencies and current/flow curves',
                       'Finite-run mean extrapolation, not a proven daily storage steady state',
                       'Line voltage/loss model is conservative midpoint hypothesis; thermal/protection and detailed network unsolved',
                       'Availability, standby and renewal costs remain separate bounded assumptions'],**FLAGS)
    v['evaluation_id']=identity(v);return v
