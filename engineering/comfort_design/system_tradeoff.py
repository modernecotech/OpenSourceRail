"""Six equal-headway network alternatives; no new native or price evidence.

This adjunct challenges the earlier shortest-winding prototype selection using
fleet, added stops, motor coverage and energy together. It leaves that source
and its executed native packet unchanged.
"""
from hashlib import sha256
from pathlib import Path
import json
import math

from . import ROOT,FLAGS
from . import service

LIBRARY=(350.,450.,600.,800.,900.,1000.)


def _encoded(v):return (json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()
def _id(v):return sha256(_encoded(v)).hexdigest()


def interval_union(intervals,lo,hi):
    """Union clipped to mainline chainage; overlap never creates free hardware."""
    clipped=sorted((max(lo,a),min(hi,b)) for a,b in intervals if b>lo and a<hi)
    total=0.;end=None;overlaps=0;overlap_m=0.
    for a,b in clipped:
        if end is None or a>=end:
            total+=b-a;end=b
        else:
            overlaps+=1;overlap_m+=max(0.,min(end,b)-a)
            if b>end:total+=b-end;end=b
    return dict(union_m=total,overlap_pairs=overlaps,overlap_m=overlap_m)


def evaluate(vehicle,root=ROOT):
    root=Path(root).resolve();tare,mass=service._vehicle(vehicle)
    city=json.loads((root/service.CITY).read_bytes())
    profiles={};zones={}
    def profile(speed,distance):
        key=(speed,distance)
        if key not in profiles:profiles[key]=service.motion_profile(distance,speed,.4,.6,mass,1000.)
        return profiles[key]
    def zone(speed,distance):
        key=(speed,distance)
        if key not in zones:
            p=profile(speed,distance);chosen=None
            if p['runtime_s'] is not None:
                for length in LIBRARY:
                    z=service.motor_zone(p,length,104.5,35.)
                    if z['geometry_full_engagement'] and z['nominal_resource_screen']=='pass':
                        chosen=z;break
            zones[key]=chosen
        return zones[key]
    proposals=[]
    for speed in (15.,20.):
        for maximum in (None,2000.,3000.):
            lines=[];quantities={str(int(w)):0 for w in LIBRARY};all_sites=0
            for line in city['lines']:
                stations={r['id']:r['s_m'] for r in line['stations']}
                limits=(min(stations.values()),max(stations.values()))
                track_intervals={-1:[],1:[]};new_sites=set();failures=[];zone_failures=[];layouts=[]
                moving=dwell=launch=recovery=0.;main_moving=0.;main_events=0;maximum_power=0.;resource_margin=None
                local_quantities={str(int(w)):0 for w in LIBRARY}
                for event in line['duty']['arrival_events_per_circuit']:
                    if event['terminal_loop_allowance']:
                        moving+=event['moving_seconds'];dwell+=35.;continue
                    pieces=1 if maximum is None else max(1,math.ceil(event['distance_m']/maximum))
                    distance=event['distance_m']/pieces;p=profile(speed,distance);z=zone(speed,distance)
                    origin=event['origin_station'].removesuffix('-outgoing')
                    destination=event['destination_station'].removesuffix('-outgoing')
                    if origin not in stations or destination not in stations:raise ValueError('explicit mainline chainage required')
                    s0,s1=stations[origin],stations[destination];direction=1 if s1>s0 else -1
                    for k in range(1,pieces):new_sites.add(round(s0+(s1-s0)*k/pieces,6))
                    main_events+=pieces
                    if p['runtime_s'] is None:
                        failures.append(dict(distance_m=distance,events=pieces,reason=p['failure']));continue
                    moving+=pieces*p['runtime_s'];dwell+=35.*pieces
                    main_moving+=pieces*p['runtime_s']
                    launch+=pieces*p['launch_mechanical_kWh_per_train']
                    recovery+=pieces*p['theoretically_recoverable_mechanical_kWh_per_train']
                    if z is None:
                        zone_failures.append(dict(distance_m=distance,events=pieces,reason='No full-engagement120-second station-library survivor'));continue
                    name=str(int(z['length_m']));local_quantities[name]+=pieces;quantities[name]+=pieces
                    maximum_power=max(maximum_power,z['required_peak_train_mechanical_kW'])
                    resource_margin=z['nominal_120_s_margin_s'] if resource_margin is None else min(resource_margin,z['nominal_120_s_margin_s'])
                    for k in range(1,pieces+1):
                        at=s0+(s1-s0)*k/pieces
                        ends=(at+direction*z['start_m'],at+direction*z['end_m'])
                        track_intervals[direction].append((min(ends),max(ends)))
                        layouts.append(dict(direction=direction,station_chainage_m=at,
                            start_chainage_m=min(ends),end_chainage_m=max(ends),
                            station_component_id=z['station_id'],length_m=z['length_m']))
                reach=not failures;valid=reach and not zone_failures
                peak=math.ceil((moving+dwell)/120.) if reach else None
                spare=math.ceil(.12*peak) if peak is not None else None
                union=[interval_union(track_intervals[d],*limits) for d in (-1,1)]
                all_sites+=len(new_sites)
                lines.append(dict(line=line['line'],coast_failures=failures,station_library_failures=zone_failures,
                    peak_trainsets=peak,spare_trainsets=spare,cold_reserve=1,
                    total_trainsets=peak+spare+1 if peak is not None else None,
                    circuit_s=moving+dwell if reach else None,moving_s=moving if reach else None,
                    mainline_moving_s=main_moving if reach else None,
                    additional_line_stop_sites=len(new_sites),mainline_arrivals_per_circuit=main_events,
                    station_library_counts=local_quantities,
                    direction_winding_m=sum(float(k)*n for k,n in local_quantities.items()) if valid else None,
                    mainline_mechanical_launch_kWh_per_circuit=launch if reach else None,
                    mainline_mechanical_recoverable_kWh_per_circuit=recovery if reach else None,
                    peak_required_train_mechanical_kW=maximum_power if valid else None,
                    minimum_nominal120s_margin_s=resource_margin if valid else None,
                    directional_mainline_length_m=2*(limits[1]-limits[0]),
                    motor_union_on_mainline_m=sum(r['union_m'] for r in union),
                    motor_interval_overlap_count=sum(r['overlap_pairs'] for r in union),
                    motor_overlap_m=sum(r['overlap_m'] for r in union),
                    directional_winding_intervals=sorted(layouts,key=lambda r:(r['direction'],r['station_chainage_m'])),
                    chainage_interval_design_qualified=False))
            reachable=all(not r['coast_failures'] for r in lines)
            adequate=reachable and all(not r['station_library_failures'] for r in lines)
            total=sum(r['total_trainsets'] for r in lines) if reachable else None
            active=sum(r['peak_trainsets'] for r in lines) if reachable else None
            wind=sum(r['direction_winding_m'] for r in lines) if adequate else None
            union=sum(r['motor_union_on_mainline_m'] for r in lines)
            mainline=sum(r['directional_mainline_length_m'] for r in lines)
            physical=dict(vehicle_candidate_id=vehicle['candidate_id'],launch_speed_m_s=speed,
                maximum_station_spacing_m=maximum,headway_s=120.,dwell_s=35.,
                acceleration_m_s2=.4,deceleration_m_s2=.6,drag_N_per_car=1000.,
                station_library_m=list(LIBRARY),actual_station_layouts_qualified=False)
            row=dict(proposal_id=_id(physical),physical_definition=physical,lines=lines,
                launch_speed_m_s=speed,maximum_station_spacing_m=maximum,
                all_mainline_events_reachable=reachable,all_station_library_screens_pass=adequate,
                lines_with_unreachable_events=sum(bool(r['coast_failures']) for r in lines),
                lines_with_station_library_failures=sum(bool(r['station_library_failures']) for r in lines),
                peak_active_trainsets=active,total_trainsets=total,additional_line_stop_sites=all_sites,
                network_cycle_seconds_sum=sum(r['circuit_s'] for r in lines) if reachable else None,
                mean_mainline_event_runtime_s=sum(r['mainline_moving_s'] for r in lines)/sum(r['mainline_arrivals_per_circuit'] for r in lines) if reachable else None,
                station_library_counts=quantities,total_direction_winding_m=wind,
                mainline_motor_union_m=union,directional_mainline_length_m=mainline,
                mainline_motor_coverage_fraction=union/mainline if adequate else None,
                evaluated_motor_coverage_lower_bound_fraction=union/mainline,
                station_library_quantities_complete=adequate,
                motor_overlap_count=sum(r['motor_interval_overlap_count'] for r in lines),
                motor_overlap_m=sum(r['motor_overlap_m'] for r in lines),
                overlapping_motor_hardware_or_phase_handoff_qualified=False,
                actual_complete_powered_length_m=None,terminal_winding_and_civil_scope_complete=False,
                required_mainline_launch_mechanical_kWh_per_peak_operating_hour=None if not reachable else 30*sum(r['mainline_mechanical_launch_kWh_per_circuit'] for r in lines),
                potentially_recoverable_mainline_mechanical_kWh_per_peak_operating_hour=None if not reachable else 30*sum(r['mainline_mechanical_recoverable_kWh_per_circuit'] for r in lines),
                hotel_kWh_per_peak_operating_hour_per_kW_per_car=None if active is None else 6*active,
                actual_hotel_kW_per_car=None,actual_traction_electrical_efficiency=None,actual_price_USD=None,
                scope='Equal120s/46-person-cap analytical network alternative; retained terminal times, flat routes and constant force drag are hypotheses',
                native_protection_or_dynamic_validation_for_this_alternative=False,**FLAGS)
            row['realized_network_id']=_id(dict(vehicle_candidate_id=vehicle['candidate_id'],
                winding_layouts_by_line=[dict(line=r['line'],layouts=r['directional_winding_intervals']) for r in lines],
                layouts_complete=adequate))
            proposals.append(row)
    feasible=[r for r in proposals if r['all_station_library_screens_pass']]
    pareto=[];realized_seen=set()
    for row in feasible:
        measures=lambda r:(r['total_trainsets'],r['additional_line_stop_sites'],r['total_direction_winding_m'],r['network_cycle_seconds_sum'])
        vals=measures(row)
        dominated=any(all(a<=b for a,b in zip(measures(other),vals)) and any(a<b for a,b in zip(measures(other),vals)) for other in feasible if other is not row)
        if not dominated and row['realized_network_id'] not in realized_seen:
            pareto.append(row['proposal_id']);realized_seen.add(row['realized_network_id'])
    baseline=next(r for r in proposals if r['launch_speed_m_s']==15 and r['maximum_station_spacing_m']==2000)
    costs=[];cost_seen=set()
    for row in feasible:
        if row is baseline or row['realized_network_id'] in cost_seen:continue
        cost_seen.add(row['realized_network_id'])
        extra=row['total_direction_winding_m']-baseline['total_direction_winding_m']
        saved=baseline['total_trainsets']-row['total_trainsets']
        site_saved=baseline['additional_line_stop_sites']-row['additional_line_stop_sites']
        hotel_saved=baseline['hotel_kWh_per_peak_operating_hour_per_kW_per_car']-row['hotel_kWh_per_peak_operating_hour_per_kW_per_car']
        costs.append(dict(proposal_id=row['proposal_id'],realized_network_id=row['realized_network_id'],baseline_proposal_id=baseline['proposal_id'],
            saved_trainsets=saved,saved_proposed_stop_sites=site_saved,additional_direction_winding_m=extra,
            hotel_saving_kWh_per_operating_hour_per_kW_per_car=hotel_saved,
            train_only_break_even_USD_per_m_per_USD_unit_trainset_price=None if extra<=0 else saved/extra,
            hypothetical_train_only_break_even_USD_per_direction_m=None if extra<=0 else [
                dict(hypothetical_trainset_unit_price_USD=price,break_even_USD_per_direction_m=saved*price/extra,
                     quoted_price=False,station_savings_excluded_not_valued_zero=True) for price in (250000.,500000.,1000000.)],
            capital_equation='additional_direction_m * winding_cost_per_direction_m = saved_trainsets * trainset_unit_price + saved_sites * station_unit_price - other_extra_capital',
            annual_hotel_equation='annual_hotel_saving_kWh = hotel_saving_coefficient * actual_hotel_kW_per_car * hours_at_this_service_per_year',
            hotel_lifetime_value_equation='annual_hotel_saving_kWh * electricity_price_USD_per_kWh * declared_present_value_year_factor',
            unknown_prices_are_zero=False,actual_complete_cost_difference_USD=None))
    p20=profile(20.,2000.);z800=service.motor_zone(p20,800.,104.5,35.)
    source={}
    for mapping in (vehicle.get('source_sha256',{}),service.sources(root)):
        for name,digest in mapping.items():
            if name in source and source[name]!=digest:raise ValueError('mixed tradeoff source revisions: '+name)
            source[name]=digest
    source['engineering/comfort_design/system_tradeoff.py']=sha256(Path(__file__).read_bytes()).hexdigest()
    value=dict(schema='osr-comfort-system-tradeoff/1',candidate_id=vehicle['candidate_id'],body_candidate_id=vehicle['body_candidate_id'],
        magnet_component_id=vehicle['magnet_component_id'],source_sha256=dict(sorted(source.items())),
        proposals=proposals,pareto_proposal_ids=pareto,capital_and_hotel_break_even=costs,
        two_km_20m_s_800m_diagnostic=dict(profile=p20,station=z800),
        comparison_basis=dict(cars=6,people_per_car=46,headway_s=120,capacity_pphpd=8280,dwell_s=35,price_quotes_available=False),
        budget=dict(analytic_network_proposals=6,native_runs=0,profile_states_evaluated=len(profiles),station_options_evaluated=len(zones)),
        policy='Retain non-dominated fleet/site/winding/cycle-time alternatives; do not select a whole-system cheapest design without prices and qualified interfaces.',
        earlier_450m_choice_scope='Shortest-winding next service prototype; not a whole-system cost optimum',
        terminal_motion_and_energy_qualified=False,complete_system_economics=False,**FLAGS)
    value['evaluation_id']=_id(value)
    return value


def summary(value):
    keys=('proposal_id','realized_network_id','launch_speed_m_s','maximum_station_spacing_m','all_mainline_events_reachable',
          'all_station_library_screens_pass','lines_with_unreachable_events','total_trainsets','additional_line_stop_sites',
          'station_library_counts','total_direction_winding_m','mainline_motor_coverage_fraction','motor_overlap_count',
          'network_cycle_seconds_sum','mean_mainline_event_runtime_s',
          'hotel_kWh_per_peak_operating_hour_per_kW_per_car','required_mainline_launch_mechanical_kWh_per_peak_operating_hour',
          'potentially_recoverable_mainline_mechanical_kWh_per_peak_operating_hour')
    return dict(candidate_id=value['candidate_id'],body_candidate_id=value['body_candidate_id'],magnet_component_id=value['magnet_component_id'],evaluation_id=value['evaluation_id'],
        proposals=[{k:r[k] for k in keys} for r in value['proposals']],pareto_proposal_ids=value['pareto_proposal_ids'],
        capital_and_hotel_break_even=value['capital_and_hotel_break_even'],comparison_basis=value['comparison_basis'],**FLAGS)


def markdown(value):
    diag=value['two_km_20m_s_800m_diagnostic'];p=diag['profile'];z=diag['station']
    lines=['### Whole-system alternatives to the shortest-winding prototype','',
        'The earlier 450 m/15 m/s selection is a next station/service prototype, not proof of the cheapest complete railway. This bounded comparison keeps the same vehicle, 46-person cap, six cars, 120-second departure target, 35-second dwell and retained drag hypothesis while changing launch speed, stop spacing and counted station windings. No new native protection or physical train simulation is credited to these alternatives.','',
        f"At 20 m/s (72 km/h), the 2 km analytical journey takes **{p['runtime_s']:.1f}s**, versus 218.7 s at 15 m/s. Arrival speed is {p['arrival_speed_before_braking_m_s']:.2f} m/s. The full-engagement station bound is {z['full_engagement_bound_m']:.1f} m, so the 800 m shared-winding diagnostic **{'passes' if z['geometry_full_engagement'] else 'fails'}** that necessary geometry screen. Required peak mechanical power is {z['required_peak_train_mechanical_kW']:.0f} kW per train; this is required power, not demonstrated motor capability.",'',
        '| Launch | Stop plan | Fleet | Additional proposed line-stop sites | Directional winding | Mainline motor coverage | Overlapping intervals | Result |',
        '|---|---|---:|---:|---:|---:|---:|---|']
    for row in value['proposals']:
        spacing='Retained stops' if row['maximum_station_spacing_m'] is None else f"≤{row['maximum_station_spacing_m']/1000:g} km"
        fleet='unknown' if row['total_trainsets'] is None else f"{row['total_trainsets']:,}"
        winding='unknown' if row['total_direction_winding_m'] is None else f"{row['total_direction_winding_m']/1000:,.1f} km"
        state='Conditional analytical survivor' if row['all_station_library_screens_pass'] else f"Hold: {row['lines_with_unreachable_events']} lines have unreachable events or station screens fail"
        coverage='unknown' if row['mainline_motor_coverage_fraction'] is None else f"{100*row['mainline_motor_coverage_fraction']:.1f}%"
        lines.append(f"| {row['launch_speed_m_s']*3.6:g} km/h | {spacing} | {fleet} | {row['additional_line_stop_sites']} | {winding} | {coverage} | {row['motor_overlap_count']} | {state} |")
    lines += ['',
        'Each reachable arrival selects the shortest full-engagement station option from 350/450/600/800/900/1,000 m. Directional winding quantities exclude terminal-loop windings and other unclosed scope. Mainline coverage is the union of winding intervals clipped to retained chainages; overlapping intervals do not become free shared hardware. New line-stop sites are chainage proposals, not approved locations. Ordinary passive-guideway length must not be described as though long station motors occupy no route.','',
        f"Across these proposals the interval calculation finds {sum(r['motor_overlap_count'] for r in value['proposals'])} adjacent motor-interval overlaps. Their phase/hardware sharing, attachment, electrical isolation and additional drag remain unqualified. Higher speed and longer powered sections also require new current, voltage, thermal and protection evidence; the old 20 m/s field point is not transferred as available thrust.",'',
        'The Pareto set retains alternatives that cannot improve fleet, added sites and directional winding together. Prices remain unknown. For any comparison with extra winding, the train-only break-even threshold is `saved trainsets × assumed unit trainset price / extra directional metres`; excluded station savings are unpriced, not assigned zero. The complete equations and explicitly hypothetical unit-price sensitivities are retained in the machine-readable record.','',
        '| Alternative versus 54 km/h, ≤2 km plan | Trainsets saved | Proposed sites avoided | Extra directional winding | Hotel saving coefficient |',
        '|---|---:|---:|---:|---:|']
    by_id={r['proposal_id']:r for r in value['proposals']}
    for c in value['capital_and_hotel_break_even']:
        r=by_id[c['proposal_id']];label=f"{r['launch_speed_m_s']*3.6:g} km/h, ≤{r['maximum_station_spacing_m']/1000:g} km" if r['maximum_station_spacing_m'] else f"{r['launch_speed_m_s']*3.6:g} km/h, retained stops"
        lines.append(f"| {label} | {c['saved_trainsets']} | {c['saved_proposed_stop_sites']} | {c['additional_direction_winding_m']/1000:,.1f} km | {c['hotel_saving_kWh_per_operating_hour_per_kW_per_car']:,.0f} |")
    lines += ['',
        'The hotel coefficient is kWh saved per operating hour for each 1 kW of actual per-car services load. Multiply by measured load and declared hours at this service; electricity tariff and lifetime present-value assumptions are additional parameters. Mechanical launch and potentially recoverable braking energy are reported separately from electrical energy, with terminal-loop energy still unknown. Faster service may reduce fleet and auxiliary energy while increasing stator quantities and mechanical/aerodynamic demand; no complete cost saving is established.','',
        f"Adjunct evaluation: `{value['evaluation_id']}`. All operating and physical acceptance flags remain false.",'']
    return '\n'.join(lines)
