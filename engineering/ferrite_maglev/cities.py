"""Compile retained geography/demand into separate, unqualified v0.5 city plans.

The outputs are planning quantities. Their straight, level, independent-car duty
screen cannot qualify a route, terminal loop, supplier price or operating fleet.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
import json
import math
import os
from pathlib import Path
import tomllib

from . import model,optimisation,evacuation

ROOT = model.ROOT
ASSUMPTIONS = Path(__file__).with_name('city-planning.toml')
INDEX = Path(__file__).with_name('city-index.json')
NOTICE_START=b'<!-- osr-maglev-primary:start -->\n'
NOTICE_END=b'<!-- osr-maglev-primary:end -->\n\n'


def promote_city_readme(city_dir):
    """Prepend a controlled entry notice, preserving every legacy body byte."""
    path=Path(city_dir)/'README.md'
    original=path.read_bytes() if path.is_file() else b''
    body=original
    if body.startswith(NOTICE_START):
        if NOTICE_END not in body:
            raise ValueError('incomplete controlled primary notice: '+str(path))
        body=body.split(NOTICE_END,1)[1]
    notice=(NOTICE_START+b'> **Primary v0.5 ferrite-maglev planning:** [Open the current city planning package](engineering/maglev/README.md). '
            b'Formation, duty, fleet, charging, depot quantities and partial cost allowances are recomputed; physical acceptance remains open.\n>\n'
            b'> The material below this notice is the retained v0.4 wheel/rail comparator. Its costs, fleet, geometry and acceptance do not transfer to maglev.\n'+NOTICE_END)
    replacement=notice+body
    if replacement!=original:
        path.write_bytes(replacement)
    return path


def digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()


@lru_cache(maxsize=2048)
def _cached_city_slug(path, size, mtime_ns, ctime_ns):
    # Catalogue metadata is the first city table. Read only that table for this
    # inventory operation; full compilation still parses the complete design.
    block=[]
    with Path(path).open() as stream:
        for line in stream:
            if line.strip()=='[city]':
                block.append(line)
            elif block:
                if line.lstrip().startswith('['):
                    break
                block.append(line)
    document=tomllib.loads(''.join(block)) if block else tomllib.loads(Path(path).read_text())
    slug=document['city']['slug']
    if not isinstance(slug,str) or not slug:
        raise ValueError('nonempty city slug required: '+path)
    return slug


def city_slug(path):
    path=Path(path).resolve()
    stat=path.stat()
    return _cached_city_slug(str(path),stat.st_size,stat.st_mtime_ns,stat.st_ctime_ns)


def count(value, name):
    if type(value) is not int or value <= 0:
        raise ValueError('positive integer required: ' + name)
    return value


def formation(c, source_consist, profiles):
    """Match both declared passenger loads, including line-specific profiles."""
    v = c['vehicle']
    aw2 = max([count(source_consist['passenger_capacity'], 'AW2')] +
              [count(p['passenger_capacity'], 'profile AW2') for p in profiles])
    aw3 = max([count(source_consist['crush_capacity'], 'AW3')] +
              [count(p['crush_capacity'], 'profile AW3') for p in profiles])
    cars = max(math.ceil(aw2 / v['aw2_passengers_per_car']),
               math.ceil(aw3 / v['aw3_passengers_per_car']))
    m = model.mass(c, c['mass']['ferrite_base'], c['power']['gross_battery_matched_kwh_per_car'])
    return dict(cars=cars, retained_aw2_required=aw2, retained_aw3_required=aw3,
                aw2_passengers=cars*v['aw2_passengers_per_car'], aw3_passengers=cars*v['aw3_passengers_per_car'],
                nominal_body_length_m=cars*v['nominal_car_length_m'], overall_length_m=None,
                length_basis='Sum of nominal 17 m bodies; coupling pitch and overhang unresolved.',
                tare_mass_kg=cars*m['tare_kg'], aw2_mass_kg=cars*m['aw2_kg'], aw3_mass_kg=cars*m['aw3_kg'],
                gross_storage_kwh=cars*c['power']['gross_battery_matched_kwh_per_car'],
                eol_capacity_kwh=cars*c['power']['gross_battery_matched_kwh_per_car']*c['power']['eol_capacity_fraction'],
                normal_soc_low=c['power']['normal_soc_low'], normal_soc_high=c['power']['normal_soc_high'],
                eol_normal_window_kwh=cars*m['eol_window_kwh'], protected_emergency_energy_kwh=None,
                cabin_width_m=v['nominal_car_width_m'], full_running_gear_envelope_width_m=None,
                envelope_basis='Cabin width does not bound magnetic lifting faces, guidance arms or below-floor gear. Revalidate full route/platform swept envelope against native geometry.',
                measured_mass=False, formation_qualified=False)


def station_legs(line, stations):
    """Use retained chainages, reconciling a complete ring with its total length."""
    length = model.positive(line['length_m'], 'route length')
    ordered = sorted(stations, key=lambda s: s['s_m'])
    if len(ordered) < 2 or len({s['id'] for s in ordered}) != len(ordered):
        raise ValueError('at least two unique stations required: '+line['name'])
    chainages = [model.positive(s['s_m'], 'chainage', zero=True) for s in ordered]
    if chainages[-1] > length + 1:
        raise ValueError('station beyond retained route length: '+line['name'])
    legs = [b-a for a, b in zip(chainages, chainages[1:])]
    if any(d <= 0 for d in legs):
        raise ValueError('distinct increasing station chainages required')
    if line['shape'] == 'ring':
        closure = length - sum(legs)
        model.positive(closure, 'ring closure')
        legs.append(closure)
    elif line['shape'] == 'radial':
        # Retain unserved ends explicitly; charge/duty uses the full declared route.
        legs[0] += chainages[0]
        legs[-1] += max(0, length-chainages[-1])
        closure = None
    else:
        raise ValueError('unsupported retained topology: '+line['shape'])
    return ordered, legs, closure


def duty_evaluator(c):
    """Cache only within this exact input configuration."""
    mass = model.mass(c, c['mass']['ferrite_base'], c['power']['gross_battery_matched_kwh_per_car'])

    @lru_cache(maxsize=None)
    def evaluate(distance, hot=False, regen=True, speed=80.0):
        configuration = deepcopy(c)
        configuration['power']['station_spacing_study_m'] = distance
        r = model.cycle(configuration, mass['aw3_kg' if hot else 'aw2_kg'], hot=hot, regen=regen, speed_kmh=speed)
        hotel = configuration['power']['hot_hotel_kw_per_car' if hot else 'normal_hotel_kw_per_car']
        return dict(moving_seconds=r['moving_seconds'], moving_energy_kwh=r['cycle_kwh']-
                    hotel*configuration['power']['station_dwell_seconds']/3600,
                    achieved_speed_kmh=r['achieved_speed_kmh'], hotel_kw=hotel)
    return evaluate


def line_plan(c, a, f, line, stations, source_fleet, evaluate):
    ordered, distances, closure = station_legs(line, stations)
    schedule = source_fleet.get('schedule', [])
    if not schedule:
        raise ValueError('retained service schedule required: '+line['name'])
    headway = min(model.positive(s['headway_min'], 'headway') for s in schedule)*60
    normal = [evaluate(round(d, 6)) for d in distances]
    hot = [evaluate(round(d, 6), True, False) for d in distances]
    hot_regen = [evaluate(round(d, 6), True, True) for d in distances]
    p = a['charging']; charger = model.positive(p['candidate_kw_per_car'], 'charger')
    hotel = c['power']['hot_hotel_kw_per_car']
    if charger <= hotel:
        raise ValueError('charger must exceed stationary services')
    # Charge at each station; dwell covers the worst incoming hot/no-regen leg.
    effective = max((r['moving_energy_kwh']*3600 + hotel*p['connection_overhead_seconds']) /
                    (charger-hotel) for r in hot)
    dwell = max(p['minimum_dwell_seconds'], math.ceil(effective+p['connection_overhead_seconds']))
    ring = line['shape'] == 'ring'
    loop_distance = 0.0
    loop_time = 0.0
    loop_energy = 0.0
    loop_regen_energy = 0.0
    if not ring:
        radius = a['topology']['terminal_loop_radius_screen_m']
        loop_distance = a['topology']['terminal_loop_circumferences_per_roundtrip']*2*math.pi*radius
        speed = a['topology']['terminal_loop_speed_screen_kmh']
        lateral = (speed/3.6)**2/radius
        if lateral > a['topology']['terminal_loop_lateral_acceleration_limit_screen_m_s2']:
            raise ValueError('loop speed exceeds declared lateral acceleration screen')
        loop_duty = evaluate(round(loop_distance/2, 6), True, False, speed)
        loop_time = 2*loop_duty['moving_seconds']
        loop_energy = 2*loop_duty['moving_energy_kwh']
        loop_regen_energy = 2*evaluate(round(loop_distance/2, 6), True, True, speed)['moving_energy_kwh']
        # End loops also consume energy between platform charging events.
        extra = loop_energy/2
        effective = (max(r['moving_energy_kwh'] for r in hot)*3600+extra*3600+
                     hotel*p['connection_overhead_seconds'])/(charger-hotel)
        dwell = max(dwell, math.ceil(effective+p['connection_overhead_seconds']))
    cycle_distance = sum(distances)*(1 if ring else 2)+loop_distance
    cycle_seconds = sum(r['moving_seconds'] for r in hot)*(1 if ring else 2)+loop_time
    # Radials include both terminal stops once per round trip; rings once/lap.
    stops = len(ordered) if ring else 2*len(ordered)-2
    cycle_seconds += stops*dwell
    per_direction = math.ceil(cycle_seconds/headway)
    peak = 2*per_direction if ring else per_direction
    spare = math.ceil(peak*a['formation']['spare_fraction'])
    total = peak+spare+a['formation']['cold_reserve_per_line']
    nominal_slot = f['nominal_body_length_m']+a['formation']['platform_end_allowance_m']
    hot_cycle = sum(r['moving_energy_kwh'] for r in hot)*(1 if ring else 2)+loop_energy+hotel*stops*dwell/3600
    normal_cycle = sum(r['moving_energy_kwh'] for r in normal)*(1 if ring else 2)
    normal_cycle += c['power']['normal_hotel_kw_per_car']*stops*dwell/3600
    # Normal loop calculation must use the normal load and hotel assumptions.
    if not ring:
        normal_cycle += 2*evaluate(round(loop_distance/2, 6), False, True,
                                 a['topology']['terminal_loop_speed_screen_kmh'])['moving_energy_kwh']
    source_wrap = line.get('ring_wrap_length_m')
    stations_out = [dict(id=s['id'], lat=s['lat'], lon=s['lon'], retained_platform_length_m=s.get('platform_length_m'),
                         provisional_platform_body_plus_allowance_m=nominal_slot,
                         length_shortfall_screen_m=max(0, nominal_slot-s.get('platform_length_m', 0))) for s in ordered]
    charging = dict(candidate_kw_per_car=charger, candidate_kw_per_train=charger*f['cars'],
                    dwell_seconds=dwell, effective_charge_seconds=dwell-p['connection_overhead_seconds'],
                    minimum_screen_passed=dwell <= p['maximum_dwell_screen_seconds'],
                    dwell_exceeds_peak_headway=dwell > headway,
                    minimum_parallel_platform_berths_per_direction=math.ceil(dwell/headway),
                    station_count=len(ordered), all_sites_simultaneous_dc_upper_bound_kw=len(ordered)*2*charger*f['cars'],
                    diversity_applied=False, grid_pv_storage_sizing_accepted=False,
                    conversion_losses_and_taper_included=False, rating_selected=False)
    topology = dict(selected=a['topology']['ring' if ring else 'radial'], mainline_switches=0,
                    terminal_loop_count=0 if ring else 2, added_single_direction_loop_beam_m=loop_distance,
                    loop_radius_screen_m=None if ring else a['topology']['terminal_loop_radius_screen_m'],
                    loop_speed_screen_kmh=None if ring else a['topology']['terminal_loop_speed_screen_kmh'],
                    loop_lateral_acceleration_screen_m_s2=None if ring else lateral,
                    loop_lateral_acceleration_limit_screen_m_s2=a['topology']['terminal_loop_lateral_acceleration_limit_screen_m_s2'],
                    loop_land_and_swept_envelope_accepted=False, depot_access_accepted=False,
                    source_ring_wrap_m=source_wrap, complete_ring_closure_m=closure,
                    ring_wrap_discrepancy_m=None if closure is None or source_wrap is None else closure-source_wrap,
                    exclusive_shuttle_alternative=None if ring else dict(
                        minimum_independent_lanes=math.ceil((cycle_seconds-loop_time)/headway),
                        reversal_allowance_seconds=0,
                        rule='One train per isolated bidirectional lane; no passing or crossover. This lane count is a capacity screen, not a selected civil plan.'),
                    loop_length_basis='Two full-circumference budgeting allowances per radial roundtrip; connection geometry and actual added length unresolved.')
    depot = dict(storage_slots=total, minimum_total_storage_track_m=total*nominal_slot,
                 storage_lanes_screen=math.ceil(total/a['depot']['trains_per_storage_lane_screen']),
                 inspection_bays_screen=math.ceil(total*a['depot']['inspection_bay_fraction_screen']),
                 simultaneous_depot_charge_kw_upper_bound=total*charger*f['cars'],
                 switch_policy=a['depot']['switches'], placement_accepted=False,
                 entry_exit_without_mainline_points_qualified=False, depot_cost_usd=None,
                 access='A moving transfer device or engineered depot-only connection is required; no old wheel/rail turnout is inherited.')
    arrivals=[]
    sequence=[(i,i+1) for i in range(len(ordered)-1)]
    if ring:
        sequence.append((len(ordered)-1,0))
    else:
        sequence += [(i,i-1) for i in range(len(ordered)-1,0,-1)]
    for origin,destination in sequence:
        leg_index=origin if ring else min(origin,destination)
        terminal_loop=not ring and destination in (0,len(ordered)-1)
        arrivals.append(dict(origin_station=ordered[origin]['id'], destination_station=ordered[destination]['id'],
                             distance_m=distances[leg_index]+(loop_distance/2 if terminal_loop else 0),
                             moving_seconds=hot[leg_index]['moving_seconds']+(loop_time/2 if terminal_loop else 0),
                             hot_no_regen_motion_kwh=(hot[leg_index]['moving_energy_kwh']+(loop_energy/2 if terminal_loop else 0))*f['cars'],
                             hot_regen_motion_kwh=(hot_regen[leg_index]['moving_energy_kwh']+(loop_regen_energy/2 if terminal_loop else 0))*f['cars'],
                             terminal_loop_allowance=terminal_loop))
    return dict(line=line['name'], retained_shape=line['shape'], retained_length_m=line['length_m'],
                retained_schedule=schedule, retained_peak_headway_seconds=headway,
                aw2_capacity_per_direction_hour=f['aw2_passengers']*3600/headway,
                formation=f, topology=topology, stations=stations_out,
                duty=dict(cycle_distance_m=cycle_distance, conservative_cycle_seconds=cycle_seconds,
                          moving_seconds=sum(r['moving_seconds'] for r in hot)*(1 if ring else 2)+loop_time,
                          normal_aw2_regen_cycle_kwh=normal_cycle*f['cars'],
                          hot_aw3_no_regen_cycle_kwh=hot_cycle*f['cars'],
                          largest_leg_m=max(distances), minimum_leg_m=min(distances),
                          worst_incoming_leg_hot_no_regen_kwh=max(r['moving_energy_kwh'] for r in hot)*f['cars'],
                          hot_hotel_kw=hotel*f['cars'], arrival_events_per_circuit=arrivals,
                          eol_window_divided_by_cycle_energy=f['eol_normal_window_kwh']/(hot_cycle*f['cars']),
                          route_acceptance=False,
                          exclusions=['grade/curves/wind', 'jerk and coupled dynamics', 'shared-train aerodynamic effects',
                                      'loop lateral force and physical geometry', 'emergency reserve', 'missed charge',
                                      'full SOC and low voltage', 'charger taper/grid and battery internal losses']),
                fleet=dict(peak=peak, spare=spare, cold_reserve=a['formation']['cold_reserve_per_line'], total=total,
                           retained_comparator_trainsets=source_fleet['trainset_count'],
                           source_fleet_inherited=False, conflict_and_recovery_validated=False,
                           rule='ceil(hot/no-regen circuit time / retained peak headway), two directions for rings, 10% spare rounded up plus one cold reserve/line'),
                charging=charging, depot=depot)


GATES = [
    ('retained-geography', 'Survey, utilities, land, water crossings, terrain, ground investigation and alignment reconciliation; retained mapping is geographic evidence only.'),
    ('formation-platform', 'Close coupling pitch, full magnetic lifting-face/guidance-arm/below-floor swept envelope, door/egress layouts, actual mass and equal AW2/AW3 qualification. The 2.65 m cabin width does not bound running gear or platform clearance.'),
    ('field-control', 'Obtain force/loss maps and rig correlation, six-axis stability, target timing and independent support/capture/braking protection.'),
    ('terminal-topology', 'Locate fixed loops/ring closure, qualify curvature, clearance and land, and provide switch-free failure recovery.'),
    ('elevated-alignment', 'Locate the predominantly elevated straight-tangent proposal and verify buildings/air rights, road/utility clearance, wildlife/water passage, piers, station/egress and construction access; no zero-impact claim from elevation alone.'),
    ('civil-release', 'Redesign guidebeam/passive rail, supports/foundations, joints/tolerances, movement, gap dynamics, evacuation and erection.'),
    ('route-duty', 'Run approved grade, curve, wind, hot, low-voltage, full-SOC, no-regen, missed-charge, failed-channel and rescue duty.'),
    ('fleet-timetable', 'Validate headway/conflicts, station berth throughput, dispatch, maintenance rotation, degraded service and reserve.'),
    ('charging-microgrid', 'Place charging interfaces and prove taper, power quality, PV/storage/backup sizing and adverse-weather replenishment.'),
    ('depot-access', 'Locate line-local storage/workshops and qualify depot-only connection/transfer, isolation, inspection, towing and recovery.'),
    ('programme-cost', 'Price all station/land/loop/bridge/at-grade/depot/energy/control/production/QA/NRE/spares/OPEX scope, origin-trace MBOM and apply EPC once.'),
    ('physical-release', 'Close G0–G5 through authenticated independent physical acceptance; planning arithmetic is insufficient.'),
]


def generate(city_dir, context=None, output_dir=None, *, assumptions=None, evaluate=None):
    city_dir = Path(city_dir).resolve()
    _, c, costs = context or model.load()
    a = assumptions or tomllib.loads(ASSUMPTIONS.read_text())
    if a['schema']['family'] != c['metadata']['family'] or a['topology']['loop_geometry_accepted'] is not False:
        raise ValueError('unqualified maglev planning assumptions required')
    if a['topology']['radial'] != 'fixed-terminal-loops' or a['topology']['ring'] != 'two-independent-directed-circuits':
        raise ValueError('unsupported city topology requires its own adapter')
    if a['topology']['terminal_loop_circumferences_per_roundtrip'] != 2:
        raise ValueError('two terminal loop allowances required')
    for group in ('formation', 'topology', 'charging', 'depot'):
        for name, value in a[group].items():
            if type(value) in (int, float):
                model.positive(value, group+'.'+name)
    design_path = city_dir/'design.toml'
    design = tomllib.loads(design_path.read_text())
    slug = design['city']['slug']
    scenario_path = city_dir/(slug+'.toml')
    scenario = tomllib.loads(scenario_path.read_text())
    profiles_path = ROOT/'lib/templates/rolling-stock.toml'
    profiles = tomllib.loads(profiles_path.read_text())['profiles']
    evaluate = evaluate or duty_evaluator(c)
    fleets = {s['line']: s for s in scenario['fleets']}
    lines = []
    for line in design['lines']:
        f = formation(c, scenario['consist'], [profiles[line['rolling_stock']]])
        stations = [s for s in design['stations'] if s['line'] == line['name']]
        lines.append(line_plan(c, a, f, line, stations, fleets[line['name']], evaluate))
    source_paths = [design_path, scenario_path, profiles_path, ASSUMPTIONS, Path(__file__),
                    model.INPUT, model.POLICY, Path(model.__file__), ROOT/'engineering/ferrite_maglev/workbook.py',
                    ROOT/c['cost']['cost_input_file'], ROOT/'VERSION']
    source_paths += [ROOT/'design/component-catalogue/catalog/buildable-trainset/trainset-build-cost.json',
                     ROOT/'lib/templates/civil-cost-model.toml',Path(optimisation.__file__),optimisation.INPUT,Path(evacuation.__file__),evacuation.INPUT]
    for name in ('corridors.json', slug+'.stations.json', slug+'.corridor.geojson', 'alignment-policy.toml'):
        path = city_dir/name
        if path.is_file(): source_paths.append(path)
    sources = {p.relative_to(ROOT).as_posix(): digest(p) for p in source_paths}
    station_input = city_dir/(slug+'.stations.json')
    retained_stations = json.loads(station_input.read_text()) if station_input.is_file() else design['stations']
    corridor_path = city_dir/'corridors.json'
    corridor = json.loads(corridor_path.read_text()) if corridor_path.is_file() else {}
    records = dict(city=design['city'], climate=design['climate'], retained_station_demand_records=retained_stations,
                   retained_station_design_records=design['stations'], retained_interchanges=design.get('interchanges', []),
                   retained_lines=design['lines'], retained_service_schedules=scenario['fleets'],
                   retained_demand_metadata={k:v for k,v in corridor.items() if k != 'lines'},
                   full_route_geometry_sources=[p for p in sources if p.endswith(('.corridor.geojson', '/corridors.json'))],
                   use='Retained geography and demand only. No physical geometry, fleet, costs, soil or supplier acceptance transfers.')
    fleet = sum(l['fleet']['total'] for l in lines)
    cars = sum(l['fleet']['total']*l['formation']['cars'] for l in lines)
    by_class = {}
    for s in design['civil_segments']:
        by_class[s['class']] = by_class.get(s['class'], 0)+s['to_station_m']-s['from_station_m']
    strategy=optimisation.route_strategy(design,corridor)
    elevated=strategy['ordinary_viaduct_proposal_length_m']/1000
    cost_rows = []
    for name in ('low', 'base', 'high', 'target-90000', 'target-60000'):
        target = int(name.split('-')[1]) if name.startswith('target-') else None
        case = model.cost_case(c, costs, 'base' if target else name, c['mass']['ferrite_base'],
                               c['power']['gross_battery_matched_kwh_per_car'], hardware_target=target)
        trains = case['train_usd']*cars/c['vehicle']['cars_per_train']
        civil = case['civil_usd_dual_km']*elevated
        cost_rows.append(dict(scenario=name, repeat_fleet_allowance_usd=trains,
                              ordinary_elevated_allowance_usd=civil, priced_scope_subtotal_usd=trains+civil,
                              complete_city_programme_usd=None, epc_included=False, nre_included=False,
                              supplier_quotes=False, fleet_scaling_basis='Linear per-car extrapolation of supplied three-car allowance; formation engineering and economies of scale unpriced.',
                              ordinary_viaduct_proposal_km=elevated,
                              civil_basis='All ordinary mainline sections proposed elevated, including retained at-grade lengths; special crossings stay separately unpriced. New indexed rate; old curve multipliers/products and costs are not inherited.'))
    search=optimisation.study(c,costs)
    candidate=search['minimum_indexed_allowance_candidate']
    if candidate is not None:
        unit=candidate['civil']['indexed_allowance_usd_dual_km']
        trains=candidate['vehicle']['repeat_three_car_train_allowance_usd']*cars/c['vehicle']['cars_per_train']
        cost_rows.append(dict(scenario='indexed-joint-optimisation-target',repeat_fleet_allowance_usd=trains,
            ordinary_elevated_allowance_usd=unit*elevated,priced_scope_subtotal_usd=trains+unit*elevated,
            ordinary_viaduct_proposal_km=elevated,ordinary_viaduct_unit_allowance_usd_dual_km=unit,
            candidate_id=candidate['id'],complete_city_programme_usd=None,epc_included=False,nre_included=False,supplier_quotes=False,
            fleet_scaling_basis='Baseline conservative fleet quantities retained; lighter mass and hardware costs are unqualified targets. No fleet reduction credited.',
            civil_basis='Provisional lowest indexed civil allowance passing gross stiffness/lift screens; all ordinary sections proposed elevated. No engineering acceptance or full project price.'))
    evac=evacuation.load();bare=search['beam_only_minimum_gross_allowance_candidate']
    packs=cars*evac['train']['doors_per_side_per_car_screen']*evac['train']['sides']
    beam_only=dict(target=evac['architecture']['target'],walkway_removal_approved=False,
        onboard_pack_count_hypothesis=packs,door_configuration_approved=False,
        added_vehicle_mass_kg=None,procurement_and_lifetime_cost_usd=None,net_system_saving_usd=None,
        gross_avoided_viaduct_scope_allowance_usd=bare['gross_avoided_scope_usd_dual_km']*elevated if bare else None,
        minimum_gross_only_candidate_id=bare['id'] if bare else None,
        selection_state='hold; landing at every stop position, accessible alternatives, fire/weather/fault/rescue and supplier acceptance unproved')
    report = dict(schema='osr-maglev-city-planning/1', architecture=c['metadata']['family'], version='0.5',
                  city=slug, name=scenario['scenario']['name'], status='provisional-planning; physical-acceptance-open',
                  source_sha256=sources, planning_assumptions=a, routing_strategy=strategy, retained_records_file='retained-records.json', lines=lines,
                  diagnostics=dict(ring_closure_discrepancies=[dict(line=l['line'], discrepancy_m=l['topology']['ring_wrap_discrepancy_m'])
                                    for l in lines if l['topology']['ring_wrap_discrepancy_m'] not in (None, 0)],
                                   platform_body_allowance_shortfalls=sum(s['length_shortfall_screen_m']>0 for l in lines for s in l['stations']),
                                   dwell_headway_conflicts=[l['line'] for l in lines if l['charging']['dwell_exceeds_peak_headway']],
                                   excessive_charging_dwell=[l['line'] for l in lines if not l['charging']['minimum_screen_passed']]),
                  totals=dict(lines=len(lines), station_records=sum(len(l['stations']) for l in lines),
                              trainsets=fleet, cars=cars, gross_onboard_storage_kwh=cars*c['power']['gross_battery_matched_kwh_per_car'],
                              retained_route_length_m=sum(l['length_m'] for l in design['lines']),
                              added_single_direction_loop_beam_m=sum(l['topology']['added_single_direction_loop_beam_m'] for l in lines),
                              retained_civil_class_length_m=by_class),
                  costs=dict(scenarios=cost_rows, city_total_usd=None, beam_only_conditional_option=beam_only,
                             unpriced=['site-specific elevated conversion and clearance premiums', 'bridges and special structures', 'curve/site premiums', 'terminal loops and land',
                                       'stations/platform alterations', 'depot/transfer/recovery equipment', 'charging/PV/storage/grid',
                                       'signalling/control/supervision', 'surveys/design/qualification', 'national production plant',
                                       'NRE and first article', 'EPC', 'initial spares/warranty/renewals/OPEX'],
                             old_city_costs_inherited=False, pilot_and_repeat_fleet_automatically_added=False),
                  gates=[dict(id=k, state='open', accepted=False, closure=v) for k,v in GATES],
                  design_complete=False, physical_validation=False, manufacturing_release=False, physical_release=False)
    output = Path(output_dir) if output_dir else city_dir/'engineering/maglev'
    output.mkdir(parents=True, exist_ok=True)
    (output/'retained-records.json').write_text(json.dumps(records, ensure_ascii=False, sort_keys=True, indent=2)+'\n')
    report['retained_records_sha256'] = digest(output/'retained-records.json')
    (output/'summary.json').write_text(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2)+'\n')
    write_readme(output, report)
    if output_dir is None:
        promote_city_readme(city_dir)
    return report


def write_readme(output, report):
    t = report['totals']
    rows = [f"# {report['name']} — v0.5 maglev city planning", '',
            'Provisional planning from retained geography, station demand and service schedules. All physical and manufacturing release flags remain false.', '',
            f"{t['lines']} lines; {t['trainsets']} provisional trainsets / {t['cars']} cars; {t['gross_onboard_storage_kwh']:,.0f} kWh gross onboard storage.", '',
            '| Line | Cars | AW2 / AW3 | Body length m | Topology | Peak / total trains | Dwell s |',
            '|---|---:|---:|---:|---|---:|---:|']
    for l in report['lines']:
        f=l['formation']
        rows.append(f"| {l['line']} | {f['cars']} | {f['aw2_passengers']} / {f['aw3_passengers']} | {f['nominal_body_length_m']:g} | {l['topology']['selected']} | {l['fleet']['peak']} / {l['fleet']['total']} | {l['charging']['dwell_seconds']:g} |")
    diagnostics=report['diagnostics']
    if diagnostics['ring_closure_discrepancies']:
        rows += ['', 'Retained ring wrap distances do not close the complete geographic route. Recomputed closure adds the following distances to the old wrap values; actual closure alignment remains open: '+
                 '; '.join(f"{r['line']} {r['discrepancy_m']:,.1f} m" for r in diagnostics['ring_closure_discrepancies'])+'.']
    if diagnostics['platform_body_allowance_shortfalls']:
        rows += ['', f"{diagnostics['platform_body_allowance_shortfalls']} retained station platforms are shorter than the new body-length-plus-10 m screen. Final coupling/overhang and platform design remain open."]
    option=report['costs']['beam_only_conditional_option']
    rows += ['', '**Integrated-beam/no-walkway target:** door-mounted evacuation is a study candidate. Continuous walkway removal is not approved. Necessary iron reaction faces, supports/foundations, joints and protection remain. '+str(option['onboard_pack_count_hypothesis'])+' onboard packs are a provisional door-count hypothesis; new mass, lifetime cost and net savings are unknown. Landing space, accessible alternatives, fire/weather/fault conditions and rescue/maintenance access must be proved along the complete route.', '']
    route=report['routing_strategy']
    rows += ['', f"**Predominantly elevated strategy:** {100*route['target_elevated_mainline_fraction']:g}% mainline elevation target; all ordinary sections proposed elevated. Ordinary viaduct planning length {route['ordinary_viaduct_proposal_length_m']/1000:,.3f} km includes {route['proposed_conversion_from_at_grade_m']/1000:,.3f} km converted from retained at-grade scope. Special crossings remain separate and unpriced.", '',
             'Straight tangents are preferred between demand anchors. Existing geographic alignments have not been rerouted or proved clear. Buildings/air rights, road and utility clearances, piers/foundations, wildlife/water passage, station access and construction access require evidence. Elevation does not establish zero displacement or zero environmental impact.', '']
    rows += ['', 'Formation matches both retained AW2/AW3 loads. Body lengths exclude unresolved couplings/overhang; platform allowance is a planning screen. Fleet is recomputed from hot AW3, no-regen straight/level duty and retained peak headways, with 10% spares rounded up and one cold reserve per line.', '',
             'Radials use unlocated fixed terminal loop allowances; rings use two independent directed circuits. A 100 m radius / 20 km/h loop allowance is not approved geometry. Depot-only switches or transfer devices require separate hardware, access and recovery qualification.', '',
             'Station charging is screened at 600 kW per car, with dwell extended to cover the worst incoming hot/no-regen leg and terminal loop. Multiple berths implied by dwell/headway require a conflict-free physical layout. Losses, taper, grade, curve forces, emergency reserve and missed charging remain open. No grid/PV/storage or site release is asserted.', '',
             '| Scenario | Repeat fleet allowance USD | Ordinary elevated allowance USD | Partial subtotal USD |',
             '|---|---:|---:|---:|']
    for c in report['costs']['scenarios']:
        rows.append(f"| {c['scenario']} | {c['repeat_fleet_allowance_usd']:,.0f} | {c['ordinary_elevated_allowance_usd']:,.0f} | {c['priced_scope_subtotal_usd']:,.0f} |")
    rows += ['', '**Complete city programme cost remains unknown.** Partial allowances extrapolate the supplied three-car cost per car and ordinary elevated route km. They exclude site-specific conversion/clearance premiums, terminal loops, special/bridge works, stations, depots, energy, controls, land, NRE/plant, EPC and other scope listed in the structured report. The joint optimisation row uses unqualified mass/hardware targets and indexed civil quantities; it retains conservative baseline fleet counts. Targets are unquoted hypotheses; old city totals are not reused.', '',
             'Open acceptance work:', '']
    rows += ['- '+g['id']+': '+g['closure'] for g in report['gates']]
    rows += ['', '[Structured plan](summary.json) · [Preserved geography/demand records](retained-records.json)', '',
             'The structured plan binds source bytes with SHA-256. Retained old designs remain separate wheel/rail comparators.', '',
             '[Primary planning method]('+Path(os.path.relpath(ROOT/'engineering/ferrite_maglev/README.md',output)).as_posix().replace(' ','%20')+')', '',
             '<!-- Generated by engineering.ferrite_maglev.cities; primary planning only. -->', '']
    (output/'README.md').write_text('\n'.join(rows))


def generate_all(output_root=None):
    context = model.load()
    assumptions = tomllib.loads(ASSUMPTIONS.read_text())
    evaluate = duty_evaluator(context[1])
    designs = sorted((ROOT/'cities/catalogue').glob('*/*/*/design.toml'))
    if not designs:
        raise ValueError('retained catalogue is empty')
    rows = []
    for design in designs:
        output = None if output_root is None else Path(output_root)/design.parent.relative_to(ROOT/'cities/catalogue')
        report = generate(design.parent, context, output, assumptions=assumptions, evaluate=evaluate)
        package = output or design.parent/'engineering/maglev'
        rows.append(dict(city=report['city'], name=report['name'], catalogue_path=design.parent.relative_to(ROOT).as_posix(),
                         package_path=package.relative_to(ROOT).as_posix() if package.is_relative_to(ROOT) else str(package),
                         summary_sha256=digest(package/'summary.json'), retained_records_sha256=report['retained_records_sha256'],
                         readme_sha256=digest(package/'README.md'), diagnostics=report['diagnostics'],
                         trainsets=report['totals']['trainsets'], cars=report['totals']['cars'],
                         open_gate_count=len(report['gates']), complete_city_programme_usd=None, physical_release=False))
    index = dict(schema='osr-maglev-city-index/1', architecture=context[1]['metadata']['family'],
                 city_count=len(rows), catalogue_design_paths=[p.relative_to(ROOT).as_posix() for p in designs],
                 catalogue_complete=True, cities=rows, physical_release=False,
                 source_sha256={str(p.relative_to(ROOT)):digest(p) for p in (Path(__file__),ASSUMPTIONS,model.INPUT,model.POLICY)})
    destination = INDEX if output_root is None else Path(output_root)/'city-index.json'
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(index, ensure_ascii=False, sort_keys=True, indent=2)+'\n')
    md=['# v0.5 maglev catalogue planning index', '',
        f'{len(rows)} retained cities have separate provisional maglev packages. Geography and demand are preserved; formation, duty, fleet, charging, depot quantities and partial costs are recomputed. Every physical acceptance gate remains open. Complete city costs remain unknown.', '',
        '| City | Cars | Trainsets | Ring closure discrepancies | Open gates | Planning package |', '|---|---:|---:|---:|---:|---|']
    for row in rows:
        package = ROOT/row['package_path']
        link=Path(os.path.relpath(package/'README.md', destination.parent)).as_posix().replace(' ', '%20')
        md.append(f"| {row['name']} | {row['cars']} | {row['trainsets']} | {len(row['diagnostics']['ring_closure_discrepancies'])} | {row['open_gate_count']} | [plan]({link}) |")
    destination.with_suffix('.md').write_text('\n'.join(md)+'\n')
    return index


def source_paths():
    """Unique city compiler input/output paths for an enclosing source snapshot.

    Reading this list neither regenerates packages nor edits entry notices.
    Missing generated output is reported by verify_index(), not manufactured.
    """
    paths={Path(__file__),ASSUMPTIONS,model.POLICY,model.INPUT,Path(model.__file__),
           ROOT/'engineering/ferrite_maglev/workbook.py',Path(optimisation.__file__),optimisation.INPUT,Path(evacuation.__file__),evacuation.INPUT,ROOT/'VERSION',
           ROOT/'OpenSourceRail_Ferrite_Maglev_Cost_Model.xlsx',ROOT/'lib/templates/rolling-stock.toml',
           ROOT/'lib/templates/civil-cost-model.toml',
           ROOT/'design/component-catalogue/catalog/buildable-trainset/trainset-build-cost.json'}
    for design in sorted((ROOT/'cities/catalogue').glob('*/*/*/design.toml')):
        directory=design.parent
        slug=city_slug(design)
        paths.update((design,directory/(slug+'.toml'),directory/'README.md'))
        for name in ('corridors.json',slug+'.stations.json',slug+'.corridor.geojson','alignment-policy.toml',
                     'engineering/maglev/summary.json','engineering/maglev/retained-records.json','engineering/maglev/README.md'):
            candidate=directory/name
            if candidate.is_file():
                paths.add(candidate)
    paths.update(p for p in (INDEX,INDEX.with_suffix('.md')) if p.is_file())
    return sorted(paths)


def verify_index(index_path=INDEX):
    """Read-only coverage, input freshness, output integrity and notice preflight."""
    errors=[]; cache={}; checked_outputs=0

    def read_json(path):
        try:
            result=json.loads(Path(path).read_text())
            if not isinstance(result,dict):
                raise ValueError('JSON object required')
            return result
        except (OSError,ValueError) as exc:
            errors.append(f'{path}: {type(exc).__name__}')
            return {}

    def check_hash(path,expected,label):
        path=Path(path)
        if path not in cache:
            cache[path]=digest(path) if path.is_file() else None
        if cache[path] is None:
            errors.append(label+': missing '+str(path))
        elif cache[path]!=expected:
            errors.append(label+': SHA-256 differs: '+str(path))

    def check_sources(mapping,label):
        if not isinstance(mapping,dict) or not mapping:
            errors.append(label+': source bindings missing')
            return
        for relative,expected in mapping.items():
            path=(ROOT/relative).resolve()
            if not path.is_relative_to(ROOT):
                errors.append(label+': source path outside repository')
            else:
                check_hash(path,expected,label)

    index=read_json(index_path)
    designs=sorted(p.relative_to(ROOT).as_posix() for p in (ROOT/'cities/catalogue').glob('*/*/*/design.toml'))
    entries=index.get('cities',[])
    if not isinstance(entries,list) or any(not isinstance(r,dict) for r in entries):
        errors.append('city entry objects missing')
        entries=[]
    if index.get('schema')!='osr-maglev-city-index/1' or index.get('physical_release') is not False:
        errors.append('index schema/release boundary differs')
    if index.get('catalogue_design_paths')!=designs or index.get('city_count')!=len(designs) or len(entries)!=len(designs):
        errors.append('index does not cover the exact current catalogue design-path set')
    expected_directories={str(Path(p).parent) for p in designs}
    entry_directories=[r.get('catalogue_path') for r in entries]
    if len(set(entry_directories))!=len(entries) or set(entry_directories)!=expected_directories:
        errors.append('city entries have missing, extra or duplicate catalogue paths')
    check_sources(index.get('source_sha256',{}),'index')
    for row in entries:
        label=row.get('city','unknown city')
        package=ROOT/row.get('package_path','missing-package')
        if not package.resolve().is_relative_to(ROOT):
            errors.append(label+': output package outside repository')
            continue
        for filename,key in (('summary.json','summary_sha256'),('retained-records.json','retained_records_sha256'),('README.md','readme_sha256')):
            check_hash(package/filename,row.get(key),label)
            checked_outputs+=1
        report=read_json(package/'summary.json')
        if report.get('schema')!='osr-maglev-city-planning/1' or report.get('city')!=row.get('city'):
            errors.append(label+': compiled city identity/schema differs')
        if any(report.get(k) is not False for k in model.FLAGS):
            errors.append(label+': unqualified city release flags differ')
        check_sources(report.get('source_sha256',{}),label)
        check_hash(package/'retained-records.json',report.get('retained_records_sha256'),label+' retained records')
        entry=ROOT/row.get('catalogue_path','missing-city')/'README.md'
        try:
            body=entry.read_bytes()
            if not body.startswith(NOTICE_START) or NOTICE_END not in body or b'engineering/maglev/README.md' not in body.split(NOTICE_END,1)[0]:
                errors.append(label+': primary entry notice missing or incomplete')
        except OSError:
            errors.append(label+': city entry README missing')
    return dict(current=not errors,errors=errors,city_count=len(entries),
                expected_city_count=len(designs),checked_outputs=checked_outputs,physical_release=False)


def replay_city(report, *, cycles=2, start_soc=None, charger_efficiency=0.90,
                regen_available=False, missed_charge_events=(1,)):
    """Replay representative trains through compiled hot duty and charging events.

    Event numbers are one-based per line and continue across circuits. Charging
    efficiency is an explicit DC supply-to-pack allowance; train motion remains
    the declared unqualified duty model. This is an offline energy ledger, not
    a traffic, protection-reserve or physical route acceptance simulation.
    """
    count(cycles, 'replay cycles')
    if cycles>100:
        raise ValueError('at most 100 replay circuits required')
    model.positive(charger_efficiency, 'charger efficiency')
    if charger_efficiency>1 or type(regen_available) is not bool:
        raise ValueError('bounded efficiency and explicit regeneration state required')
    missed=set(missed_charge_events)
    for event in missed:
        count(event, 'missed charge event')
    if report.get('schema')!='osr-maglev-city-planning/1' or report.get('physical_release') is not False:
        raise ValueError('unqualified compiled city plan required')
    source_current=all((ROOT/p).is_file() and digest(ROOT/p)==h for p,h in report['source_sha256'].items())
    if not source_current:
        raise ValueError('compiled city sources changed; regenerate before replay')
    lines=[]
    for line in report['lines']:
        f=line['formation']; duty=line['duty']; charge=line['charging']
        soc=f['normal_soc_high'] if start_soc is None else start_soc
        if type(soc) not in (int,float) or not math.isfinite(soc) or not 0<=soc<=1:
            raise ValueError('initial SOC in [0,1] required')
        capacity=model.positive(f['eol_capacity_kwh'],'EOL storage')
        lower=capacity*f['normal_soc_low']; upper=capacity*f['normal_soc_high']
        energy=capacity*soc
        initial=energy; elapsed=0.0; trace=[]; breaches=[]
        totals=dict(motion_kwh=0.0, stationary_services_kwh=0.0, supply_dc_kwh=0.0,
                    available_dc_kwh=0.0, curtailed_dc_kwh=0.0,
                    stored_charge_kwh=0.0, charger_loss_kwh=0.0, curtailed_pack_energy_kwh=0.0)
        if not lower<=energy<=upper:
            breaches.append(dict(event=0, reason='initial SOC outside normal window', energy_kwh=energy))
        for circuit in range(cycles):
            for arrival in duty['arrival_events_per_circuit']:
                event=len(trace)+1
                motion=arrival['hot_regen_motion_kwh' if regen_available else 'hot_no_regen_motion_kwh']
                energy-=motion; elapsed+=arrival['moving_seconds']
                arrival_energy=energy
                dwell=charge['dwell_seconds']; effective=charge['effective_charge_seconds']
                overhead=dwell-effective
                hotel=duty['hot_hotel_kw']; services=hotel*dwell/3600
                skipped=event in missed
                available=0.0 if skipped else charge['candidate_kw_per_train']*effective/3600
                offered=available*charger_efficiency
                # No energy is silently created/clipped at the lower bound. A
                # negative ledger is retained as an infeasibility diagnostic.
                before_charging=energy-hotel*overhead/3600
                stored=min(offered,max(0.0,upper-(energy-services)))
                curtailed=offered-stored
                supply=stored/charger_efficiency
                energy=energy-services+stored
                minimum=min(arrival_energy,before_charging,energy)
                if minimum<lower:
                    breaches.append(dict(event=event, reason='below normal SOC floor', minimum_energy_kwh=minimum,
                                         shortfall_kwh=lower-minimum))
                elapsed+=dwell
                totals['motion_kwh']+=motion; totals['stationary_services_kwh']+=services
                totals['supply_dc_kwh']+=supply; totals['stored_charge_kwh']+=stored
                totals['available_dc_kwh']+=available; totals['curtailed_dc_kwh']+=available-supply
                totals['charger_loss_kwh']+=supply-stored; totals['curtailed_pack_energy_kwh']+=curtailed
                trace.append(dict(event=event,circuit=circuit+1,station=arrival['destination_station'],
                                  elapsed_seconds=elapsed, motion_kwh=motion, arrival_energy_kwh=arrival_energy,
                                  stationary_services_kwh=services, missed_charge=skipped,
                                  available_dc_kwh=available, supply_dc_kwh=supply, charger_loss_kwh=supply-stored,
                                  curtailed_dc_kwh=available-supply,
                                  stored_charge_kwh=stored, curtailed_pack_energy_kwh=curtailed,
                                  departure_energy_kwh=energy, departure_soc=energy/capacity,
                                  minimum_event_energy_kwh=minimum, normal_window_passed=minimum>=lower))
        balance=initial-totals['motion_kwh']-totals['stationary_services_kwh']+totals['stored_charge_kwh']
        lines.append(dict(line=line['line'], representative_trains_replayed=1,
                          compiled_fleet_total=line['fleet']['total'], retained_headway_seconds=line['retained_peak_headway_seconds'],
                          initial_energy_kwh=initial, final_energy_kwh=energy, minimum_normal_energy_kwh=lower,
                          eol_capacity_kwh=capacity, elapsed_seconds=elapsed, cycles=cycles,
                          energy_ledger_residual_kwh=energy-balance, energy_totals=totals,
                          normal_window_passed=not breaches, breaches=breaches, events=trace,
                          missed_charge_events_requested=sorted(missed),
                          missed_charge_events_outside_replay=sorted(missed-set(range(1,len(trace)+1))),
                          protected_emergency_energy_kwh=None, emergency_reserve_passed=None,
                          route_acceptance=False, force_acceptance=False))
    return dict(schema='osr-maglev-city-replay/1', city=report['city'],
                compiled_plan_sha256=sha256(json.dumps(report,sort_keys=True,ensure_ascii=False).encode()).hexdigest(),
                source_sha256=report['source_sha256'], replay_generator_sha256=digest(__file__),
                source_current=True, charger_efficiency=charger_efficiency,
                regeneration_available=regen_available, load='AW3; hot assumed efficiencies', lines=lines,
                normal_window_passed=all(l['normal_window_passed'] for l in lines),
                protected_emergency_energy_kwh=None, emergency_reserve_passed=None,
                physical_release=False, route_acceptance=False, force_acceptance=False,
                exclusions=['fleet traffic/conflicts and charging simultaneity', 'grade/curves/wind/jerk',
                            'battery voltage/thermal/taper and internal losses', 'physical force/control/protection',
                            'grid/PV/storage availability', 'protected emergency reserve'])


def find_city(slug):
    matches=[]
    for path in sorted((ROOT/'cities/catalogue').glob('*/*/*/design.toml')):
        if city_slug(path)==slug:
            matches.append(path.parent)
    if len(matches)!=1:
        raise ValueError('expected one retained city for '+slug+f'; found {len(matches)}')
    return matches[0]


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('city',nargs='?',help='retained catalogue city slug')
    mode=parser.add_mutually_exclusive_group()
    mode.add_argument('--all', action='store_true')
    mode.add_argument('--design', type=Path)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--simulate',action='store_true',help='write offline hot AW3 SOC replay with a missed first charge')
    parser.add_argument('--cycles',type=int,default=2)
    parser.add_argument('--charger-efficiency',type=float,default=.9)
    parser.add_argument('--missed-charge',type=int,action='append',help='one-based event number per line; default 1')
    parser.add_argument('--regen',action='store_true')
    args=parser.parse_args(argv)
    if sum((bool(args.city),bool(args.all),bool(args.design)))!=1:
        parser.error('choose exactly one city slug, --design or --all')
    if args.simulate and args.all:
        parser.error('choose a single city for representative-train replay')
    try:
        city_dir=None if args.all else (args.design.parent if args.design else find_city(args.city))
        result=generate_all(args.output) if args.all else generate(city_dir, output_dir=args.output)
        if args.simulate:
            replay=replay_city(result,cycles=args.cycles,charger_efficiency=args.charger_efficiency,
                               regen_available=args.regen,missed_charge_events=args.missed_charge or (1,))
            output=args.output or city_dir/'engineering/maglev'
            (output/'replay.json').write_text(json.dumps(replay,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
            print(f"{result['city']}: representative-train offline SOC replay; normal window passed={replay['normal_window_passed']}; emergency reserve unknown; route acceptance=false")
            return 0
    except (ValueError,FileNotFoundError) as exc:
        parser.exit(2,f'{parser.prog}: error: {exc}\n')
    print(f"{result['city_count']} provisional city packages" if args.all else f"{result['city']}: provisional city package")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
