"""Recalculate every city using the explicit comfort development selection.

The retained city and maglev files provide geography, stop chainages and terminal
timing only. Their former formation, mass, power, cost and capacity are never
used as current results. Nothing here establishes a physical operating railway.
"""
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import gzip
import json
import math
import os
import tomllib

from engineering.comfort_design import service
from . import ROOT, FLAGS
from . import selection

SCHEMA = 'osr-current-city/1'
INDEX = 'docs/design-engine/current/cities.json'
INDEX_MANIFEST = 'docs/design-engine/current/city-catalogue-manifest.json'
PACKAGE = 'engineering/current'
LEGACY_REVISION = '578ee3950b872bf30fbf9e4207b2bda85951bdd7'
CODE = 'engineering/development_baseline/cities.py'


def _bytes(value):
    return selection.encoded(value)


def _digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def _write(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + '.tmp-' + str(os.getpid()))
    temporary.write_bytes(data)
    temporary.replace(path)


def catalogue(root=ROOT):
    """Geographic inventory, not a fallback to historical engineering results."""
    root = Path(root).resolve()
    rows = []
    for path in sorted((root / 'cities/catalogue').glob('*/*/*/city.json')):
        city = json.loads(path.read_bytes())
        rel = path.parent.relative_to(root).as_posix()
        rows.append(dict(slug=city['city']['slug'], name=city['name'],
                         country=city['city']['country'], path=rel,
                         summary_path=rel + '/' + PACKAGE + '/summary.json'))
    slugs = [row['slug'] for row in rows]
    if len(slugs) != len(set(slugs)):
        raise ValueError('Unique city slugs are required')
    return rows


def find_city(citypath_or_slug, root=ROOT):
    root = Path(root).resolve()
    path = Path(citypath_or_slug)
    candidate = path if path.is_absolute() else root / path
    if candidate.is_dir():
        candidate /= 'city.json'
    if candidate.is_file() and candidate.name == 'city.json':
        candidate = candidate.resolve()
        candidate.relative_to(root / 'cities/catalogue')
        return candidate
    found = [row for row in catalogue(root) if row['slug'].casefold() == str(citypath_or_slug).casefold()]
    if len(found) != 1:
        raise ValueError('Unknown city slug: ' + str(citypath_or_slug))
    return root / found[0]['path'] / 'city.json'


def read_catalogue(root=ROOT):
    """Read published current data; missing data stays an explicit hold."""
    path = Path(root) / INDEX
    if not path.is_file():
        raise FileNotFoundError('Current city catalogue has not been generated: ' + INDEX)
    value = json.loads(path.read_bytes())
    if value.get('schema') != 'osr-current-city-catalogue/1':
        raise ValueError('Current city catalogue schema differs')
    return value


def _baseline(record, root):
    record = selection.load(root) if record is None else record
    # The evaluator shape has no selection table; obtain the table from the
    # explicit selector and require its identities to match that evaluator.
    selected = record if 'selection' in record else selection.load(root)
    if record.get('selection_id') != selected['selection_id']:
        raise ValueError('City and evaluator selection identities differ')
    spec = selected['selection']
    if selected['selection_id'] != selection.identity(spec):
        raise ValueError('Selected service/vehicle definition identity differs')
    if selected['selection_id'] != selection.identity(tomllib.loads((root/'engineering/development-baseline.toml').read_text())):
        raise ValueError('City input is not the current explicitly selected default')
    vehicle = record['vehicle']
    for key, spec_key in (('candidate_id', 'vehicle_candidate_id'),
                          ('body_candidate_id', 'body_candidate_id'),
                          ('magnet_component_id', 'magnet_component_id')):
        if vehicle[key] != spec[spec_key]:
            raise ValueError('City vehicle component identity differs: ' + key)
    # Reject altered defaults instead of silently applying frozen six-car helper
    # arithmetic to a different formation or passenger payload.
    v = spec['vehicle']; s = spec['service']
    if (v['cars'], v['normal_passengers_per_car'], v['passenger_mass_kg_hypothesis'],
        v['fixed_seats_per_car'], v['wheelchair_places_per_car'], v['standing_passengers_per_car']) != (6, 46, 75., 44, 2, 0):
        raise ValueError('Current city adapter requires selected six-car 46-person comfort configuration')
    if (s['headway_s'], s['retain_existing_stops'], s['grade_fraction_hypothesis']) != (120., True, 0.):
        raise ValueError('Current city adapter requires explicit 120s retained-stop flat-route hypothesis')
    tare, loaded = service._vehicle(vehicle)
    if vehicle.get('installed_mass_complete') is not False:
        raise ValueError('Accounted material stock cannot be promoted to installed mass')
    if vehicle.get('evaluation_id') != selection.identity({k: val for k, val in vehicle.items() if k != 'evaluation_id'}):
        raise ValueError('Vehicle evaluation identity differs')
    if selection.identity(vehicle['physical_definition']) != vehicle['candidate_id']:
        raise ValueError('Vehicle physical identity differs')
    if not math.isclose(math.fsum(r['mass_kg'] for r in vehicle['inventory']), tare, abs_tol=1e-6):
        raise ValueError('Accounted vehicle inventory mass differs')
    return selected, vehicle, tare, loaded


@lru_cache(maxsize=16384)
def _profile(distance, speed, a, b, mass, C, Q):
    return service.motion_profile(distance, speed, a, b, mass, C, Q)


@lru_cache(maxsize=16384)
def _zone(distance, speed, a, b, mass, C, Q, train_length, dwell, library):
    profile = _profile(distance, speed, a, b, mass, C, Q)
    if profile['runtime_s'] is None:
        return None
    for length in library:
        value = service.motor_zone(profile, length, train_length, dwell)
        if value['geometry_full_engagement'] and value['nominal_resource_screen'] == 'pass':
            # Retain the physical definition and requirements without duplicating
            # numerical traces and addressed section arrays at every city stop.
            return {k: v for k, v in value.items() if k not in
                    ('force_samples', 'addressed_sections', 'exclusive_control_physical_definition')}
    return None


def _union(intervals, lo, hi):
    clipped = sorted((max(lo, a), min(hi, b)) for a, b in intervals if b > lo and a < hi)
    total = overlap_m = 0.; end = None; overlaps = 0
    for a, b in clipped:
        if end is None or a >= end:
            total += b - a; end = b
        else:
            overlaps += 1; overlap_m += max(0., min(end, b) - a)
            if b > end:
                total += b - end; end = b
    return dict(union_m=total, overlap_pairs=overlaps, overlap_m=overlap_m)


def _line(line, spec, mass):
    """Only retained chainages/events/timing enter; no old equipment values."""
    s = spec['service']; v = spec['vehicle']; headway = s['headway_s']; dwell = s['dwell_s']
    train_length = v['cars'] * v['body_length_m'] + (v['cars'] - 1) * .5
    args = (s['launch_speed_cap_m_s'], s['acceleration_m_s2_hypothesis'],
            s['deceleration_m_s2_hypothesis'], mass,
            s['constant_drag_N_per_car_hypothesis'], s['quadratic_drag_N_per_car_per_m_s_squared_hypothesis'])
    library = tuple(s['station_winding_library_m'])
    stations = {r['id']: r['s_m'] for r in line['stations']}
    if len(stations) < 2:
        raise ValueError('At least two explicit station chainages required')
    limits = (min(stations.values()), max(stations.values()))
    intervals = {-1: [], 1: []}; layouts = []; failures = []; zone_failures = []; cases = {}
    quantities = {str(int(w)): 0 for w in library}
    moving = main_moving = terminal_moving = launch = recovery = coast = 0.
    main_events = terminals = 0; maximum_power = 0.; margin = None
    for event in line['duty']['arrival_events_per_circuit']:
        if event['terminal_loop_allowance']:
            duration = event['moving_seconds']
            if not isinstance(duration, (int, float)) or not math.isfinite(duration) or duration < 0:
                raise ValueError('Finite nonnegative retained terminal timing required')
            terminal_moving += duration; moving += duration; terminals += 1
            continue
        distance = event['distance_m']; profile = _profile(distance, *args)
        case_id = selection.identity(profile)
        cases[case_id] = profile
        main_events += 1
        if profile['runtime_s'] is None:
            failures.append(dict(origin=event['origin_station'], destination=event['destination_station'],
                                 distance_m=distance, reason=profile['failure'],
                                 shortfall_m=profile['shortfall_m'], profile_id=case_id))
            continue
        moving += profile['runtime_s']; main_moving += profile['runtime_s']
        launch += profile['launch_mechanical_kWh_per_train']
        recovery += profile['theoretically_recoverable_mechanical_kWh_per_train']
        coast += profile['coast_drag_work_kWh_per_train']
        zone = _zone(distance, *args, train_length, dwell, library)
        if zone is None:
            zone_failures.append(dict(distance_m=distance, origin=event['origin_station'],
                                     destination=event['destination_station'], profile_id=case_id,
                                     reason='No full-engagement 120-second station-library survivor'))
            continue
        origin = event['origin_station'].removesuffix('-outgoing')
        destination = event['destination_station'].removesuffix('-outgoing')
        if origin not in stations or destination not in stations:
            raise ValueError('Explicit mainline chainage required')
        direction = 1 if stations[destination] > stations[origin] else -1
        at = stations[destination]
        ends = (at + direction * zone['start_m'], at + direction * zone['end_m'])
        start, end = min(ends), max(ends)
        intervals[direction].append((start, end))
        quantities[str(int(zone['length_m']))] += 1
        maximum_power = max(maximum_power, zone['required_peak_train_mechanical_kW'])
        margin = zone['nominal_120_s_margin_s'] if margin is None else min(margin, zone['nominal_120_s_margin_s'])
        layouts.append(dict(direction=direction, station_id=destination, station_chainage_m=at,
                            start_chainage_m=start, end_chainage_m=end,
                            station_component_id=zone['station_id'], profile_id=case_id,
                            length_m=zone['length_m'], sections=zone['sections_per_direction'],
                            minimum_phase_current_branches=2,
                            full_engagement_bound_m=zone['full_engagement_bound_m'],
                            required_peak_train_mechanical_kW=zone['required_peak_train_mechanical_kW'],
                            nominal120s_margin_s=zone['nominal_120_s_margin_s']))
    reachable = not failures; adequate = reachable and not zone_failures
    dwell_total = dwell * (main_events + terminals)
    cycle = moving + dwell_total if reachable else None
    peak = math.ceil(cycle / headway) if reachable else None
    spare = math.ceil(.12 * peak) if peak is not None else None
    unions = [_union(intervals[d], *limits) for d in (-1, 1)]
    station_rows = [dict(id=r['id'], lat=r['lat'], lon=r['lon'], s_m=r['s_m'],
                         minimum_body_plus_allowance_platform_length_m=train_length + 10.,
                         actual_platform_length_m=None, site_approved=False,
                         single_side_door_platform_interface_qualified=False)
                    for r in line['stations']]
    return dict(line=line['line'], retained_length_m=line['retained_length_m'],
                stations=station_rows, coast_failures=failures, station_library_failures=zone_failures,
                all_mainline_events_reachable=reachable, all_station_library_screens_pass=adequate,
                peak_trainsets=peak, spare_trainsets=spare, cold_reserve_trainsets=1,
                total_trainsets=peak + spare + 1 if peak is not None else None,
                moving_s=moving if reachable else None, mainline_moving_s=main_moving if reachable else None,
                terminal_moving_s_retained_hypothesis=terminal_moving, terminal_events_per_circuit=terminals,
                dwell_s_per_circuit=dwell_total, circuit_s=cycle,
                terminal_motion_energy_and_capacity_qualified=False,
                mainline_arrivals_per_circuit=main_events, additional_line_stop_sites=0,
                station_library_counts=quantities,
                direction_winding_m=sum(float(k)*n for k, n in quantities.items()) if adequate else None,
                evaluated_direction_winding_lower_bound_m=sum(float(k)*n for k, n in quantities.items()),
                addressed_direction_sections=sum(r['sections'] for r in layouts) if adequate else None,
                mainline_mechanical_launch_kWh_per_circuit=launch if reachable else None,
                mainline_mechanical_recoverable_kWh_per_circuit=recovery if reachable else None,
                mainline_coast_drag_kWh_per_circuit=coast if reachable else None,
                peak_required_train_mechanical_kW=maximum_power if adequate else None,
                minimum_nominal120s_margin_s=margin if adequate else None,
                directional_mainline_length_m=2*(limits[1]-limits[0]),
                motor_union_on_mainline_m=sum(r['union_m'] for r in unions),
                motor_interval_overlap_count=sum(r['overlap_pairs'] for r in unions),
                motor_overlap_m=sum(r['overlap_m'] for r in unions),
                directional_winding_intervals=sorted(layouts, key=lambda r:(r['direction'], r['station_chainage_m'])),
                profile_cases=cases, chainage_interval_design_qualified=False)


@lru_cache(maxsize=2)
def _source_civil(root_name, source_name, expected_sha):
    path = Path(root_name) / source_name
    if _digest(path) != expected_sha:
        raise ValueError('Selected source civil packet differs')
    return json.loads(gzip.decompress(path.read_bytes()))['interfaces']['civil']


def _civil_quantities(context, spec, vehicle, record, root, civil, source_sha256):
    source = spec['source_design']
    expected = _source_civil(str(root), source, source_sha256[source])
    if civil is None:
        civil = record.get('interfaces', {}).get('civil')
    if civil is None:
        civil = expected
    if civil.get('civil_interface_id') != expected['civil_interface_id']:
        raise ValueError('City civil interface differs from the explicitly selected physical bundle')
    if civil.get('civil_interface_id') != selection.identity({k:v for k,v in civil.items() if k!='civil_interface_id'}):
        raise ValueError('City civil interface identity differs')
    if civil.get('plain_guideway_has_powered_equipment') is not False:
        raise ValueError('Ordinary guideway must remain concrete with passive steel facings')
    span = civil['span_m']; direction_m = 2 * sum(r['retained_length_m'] for r in context['lines'])
    equivalent = direction_m / span
    steel = civil['complete_counted_steel_stock_kg_per_span'] * equivalent
    concrete = civil['reference_prismatic_concrete_volume_m3'] * equivalent
    return dict(civil_interface_id=civil['civil_interface_id'], candidate_id=vehicle['candidate_id'],
                body_candidate_id=vehicle['body_candidate_id'], magnet_component_id=vehicle['magnet_component_id'],
                scope='Prototype section rate extrapolated over both retained mainline directions; not an optimised or installed civil design',
                retained_mainline_direction_m=direction_m, reference_span_m=span,
                mainline_reference_span_equivalents=equivalent,
                counted_steel_stock_kg_per_reference_span=civil['complete_counted_steel_stock_kg_per_span'],
                facing_only_kg_per_reference_span=civil['facing_only_kg_per_span'],
                reference_prismatic_concrete_m3_per_span=civil['reference_prismatic_concrete_volume_m3'],
                counted_steel_stock_tonnes_per_direction_km=civil['complete_counted_steel_stock_kg_per_span']/span,
                mainline_counted_steel_stock_kg=steel,
                mainline_reference_prismatic_concrete_m3=concrete,
                mainline_counted_concrete_plus_steel_kg=2500*concrete+steel,
                mainline_reference_anchor_stock_count_coefficient=equivalent*civil['anchors_per_span'],
                mainline_reference_crossmember_count_coefficient=equivalent*civil['crossmembers_per_span'],
                actual_span_count_and_endblock_layout_known=False,
                retained_terminal_loop_geometry_direction_m=context['totals']['added_single_direction_loop_beam_m'],
                terminal_loop_quantity_and_structure_for_selected_train_known=False,
                reinforcement_prestress_endblocks_bearings_mass_kg=None,
                piers_foundations_and_station_structures_quantities=None,
                facing_magnetic_shadow_joints_anchor_capacity_and_alignment_qualified=False,
                whole_installed_civil_mass_kg=None, installed_cost_USD=None,
                guideway_permanent_magnets=0, ordinary_guideway_powered_suspension=False,
                **FLAGS)


def evaluate_city(citypath_or_slug, baseline=None, root=ROOT, civil=None):
    root = Path(root).resolve(); citypath = find_city(citypath_or_slug, root)
    selected, vehicle, tare, loaded = _baseline(baseline, root)
    spec = selected['selection']; s = spec['service']; v = spec['vehicle']
    path = citypath.parent; context_path = path / 'engineering/maglev/summary.json'
    geographic = json.loads(citypath.read_bytes()); context = json.loads(context_path.read_bytes())
    lines = [_line(line, spec, loaded) for line in context['lines']]
    reachable = all(r['all_mainline_events_reachable'] for r in lines)
    adequate = all(r['all_station_library_screens_pass'] for r in lines)
    active = sum(r['peak_trainsets'] for r in lines) if reachable else None
    total = sum(r['total_trainsets'] for r in lines) if reachable else None
    quantities = {str(int(w)):sum(r['station_library_counts'][str(int(w))] for r in lines)
                  for w in s['station_winding_library_m']}
    direction_winding = sum(r['direction_winding_m'] for r in lines) if adequate else None
    mainline = sum(r['directional_mainline_length_m'] for r in lines)
    union = sum(r['motor_union_on_mainline_m'] for r in lines)
    source = dict(selected['source_sha256'])
    source.update({citypath.relative_to(root).as_posix():_digest(citypath),
                   context_path.relative_to(root).as_posix():_digest(context_path),
                   CODE:_digest(__file__),
                   'engineering/comfort_design/service.py':_digest(service.__file__)})
    ids = {key:vehicle[key] for key in ('candidate_id','body_candidate_id','magnet_component_id')}
    capacity = v['cars']*v['normal_passengers_per_car']*3600/s['headway_s']
    result = dict(schema=SCHEMA, **ids, selection_id=selected['selection_id'],
        development_default=True, source_sha256=dict(sorted(source.items())),
        city=dict(slug=geographic['city']['slug'],name=geographic['name'],
                  country=geographic['city']['country'],population=geographic['city']['population']),
        city_path=path.relative_to(root).as_posix(), lines=lines,
        geography=dict(city_json_sha256=_digest(citypath),retained_route_context_sha256=_digest(context_path),
                       retained_source_revision=spec['source_revision'],
                       source_route_geometry_changed=False, basemaps_regenerated=False,
                       map_path=path.relative_to(root).as_posix()+'/engineering/maglev/network.svg',
                       route_and_sites_qualified=False),
        vehicle=dict(**ids,cars=v['cars'],body_length_m=v['body_length_m'],
                     train_length_m=6*v['body_length_m']+5*.5,
                     fixed_seats_per_car=v['fixed_seats_per_car'],wheelchair_places_per_car=v['wheelchair_places_per_car'],
                     standing_passengers_per_car=0,normal_passengers_per_car=v['normal_passengers_per_car'],
                     normal_people_per_train=6*v['normal_passengers_per_car'],passenger_mass_kg_hypothesis=75.,
                     passenger_doors_total_per_car=v['passenger_doors_total_per_car'],passenger_door_sides=1,
                     accounted_tare_kg_per_car=tare,accounted_cap_loaded_kg_per_car=loaded,
                     accounted_tare_kg_per_train=6*tare,accounted_cap_loaded_kg_per_train=6*loaded,
                     installed_tare_kg_per_car=None, installed_CG_and_inertia=None, **FLAGS),
        service=dict(s,normal_capacity_pphpd_arithmetic=capacity,
                     retained_14400_pphpd_comparison_met=capacity>=14400,
                     maximum_station_spacing_m=None,additional_line_stop_sites=0,
                     timetable_safe_headway_and_protected_braking_qualified=False,
                     actual_passenger_dwell_distribution_known=False,
                     terminal_timing='Retained context timing hypothesis only; terminal motion, motor length and energy remain open',
                     physical_force_maps_used=False, native_dynamic_train_runs=0),
        totals=dict(lines=len(lines),retained_route_length_m=sum(r['retained_length_m'] for r in lines),
                    station_records=sum(len(r['stations']) for r in lines),
                    peak_active_trainsets=active,spare_trainsets=sum(r['spare_trainsets'] for r in lines) if reachable else None,
                    cold_reserve_trainsets=len(lines),total_trainsets=total,
                    cars=None if total is None else 6*total,additional_line_stop_sites=0,
                    all_mainline_events_reachable=reachable,all_station_library_screens_pass=adequate,
                    lines_with_unreachable_events=sum(bool(r['coast_failures']) for r in lines),
                    lines_with_station_library_failures=sum(bool(r['station_library_failures']) for r in lines),
                    unreachable_mainline_events=sum(len(r['coast_failures']) for r in lines),
                    station_library_counts=quantities,total_direction_winding_m=direction_winding,
                    evaluated_direction_winding_lower_bound_m=sum(r['evaluated_direction_winding_lower_bound_m'] for r in lines),
                    addressed_direction_sections=sum(r['addressed_direction_sections'] for r in lines) if adequate else None,
                    directional_mainline_length_m=mainline,mainline_motor_union_m=union,
                    mainline_motor_coverage_fraction=union/mainline if adequate and mainline else None,
                    motor_overlap_count=sum(r['motor_interval_overlap_count'] for r in lines),
                    motor_overlap_m=sum(r['motor_overlap_m'] for r in lines),
                    network_cycle_seconds_sum=sum(r['circuit_s'] for r in lines) if reachable else None,
                    mean_mainline_event_runtime_s=sum(r['mainline_moving_s'] for r in lines)/sum(r['mainline_arrivals_per_circuit'] for r in lines) if reachable else None),
        energy=dict(required_mainline_launch_mechanical_kWh_per_peak_operating_hour=
                    3600/s['headway_s']*sum(r['mainline_mechanical_launch_kWh_per_circuit'] for r in lines) if reachable else None,
                    potentially_recoverable_mainline_mechanical_kWh_per_peak_operating_hour=
                    3600/s['headway_s']*sum(r['mainline_mechanical_recoverable_kWh_per_circuit'] for r in lines) if reachable else None,
                    mainline_coast_drag_kWh_per_peak_operating_hour=
                    3600/s['headway_s']*sum(r['mainline_coast_drag_kWh_per_circuit'] for r in lines) if reachable else None,
                    hotel_kWh_per_peak_operating_hour_per_kW_per_car=None if active is None else 6*active,
                    actual_hotel_kW_per_car=None,actual_station_electrical_efficiency=None,
                    terminal_energy_kWh=None,actual_operating_energy_kWh=None,
                    energy_scope='Mainline mechanical requirements under flat-route C+Qv² drag hypothesis; auxiliaries, converters, losses, terminal movement and faults are not closed'),
        quantities=_civil_quantities(context,spec,vehicle,baseline or selected,root,civil,selected['source_sha256']),
        costs=dict(prices_quoted=False,complete_priced_BOM=False,price_quote_coverage_fraction=None,
                   complete_CAPEX_USD=None,annual_OPEX_USD=None,annual_debt_service_USD=None,
                   imported_content_fraction=None,actual_origin_records_available=False,
                   capital_equation='trainsets * trainset_price + direction_winding_m * winding_price_per_direction_m + concrete_m3 * concrete_installed_rate + steel_kg * steel_installed_rate + unpriced_station_terminal_depot_power_protection_pier_foundation_and_other_scope',
                   annual_energy_equation='hours_at_this_service * (mainline_launch_mechanical_kWh_per_hour / launch_efficiency - recovered_mechanical_kWh_per_hour * receiving_efficiency + hotel_coefficient * measured_hotel_kW_per_car + unclosed_terminal_and_other_electrical_energy)',
                   annual_whole_life_equation='annual_energy_kWh * electricity_price + priced_maintenance_staffing_insurance_renewals_and_financing',
                   unknown_prices_are_zero=False,older_ferrite_costs_transferred=False),
        gates=dict(execution='completed',numerical_validity='valid-analytical-hypothesis',
                   engineering_screen='conditional-analytical-survivor' if adequate else 'fail',
                   evidence_maturity='analytical-estimate',selection_purpose='development-default',
                   physical_acceptance='unqualified',complete_equipped_vehicle=False,
                   multiaxis_stable_hover=False,actual_station_electrical_thermal_envelope=False,
                   matched_civil_installed_design=False,protected_120s_headway=False,
                   same_candidate_complete_economics=False),
        limitations=['Accounted mass is a material subtotal; installed mass, CG, inertia, hardware and margins remain open.',
                     'The unpowered coast ODE uses declared drag and zero grade; no measured magnetic drag or levitated train trajectory is claimed.',
                     'Per-arrival station envelopes need compatible departure layouts, terminal designs, independent phase branches, grid/electrical/thermal sizing and surveyed sites.',
                     'Adjacent winding intervals may overlap. Motor isolation, handoff and physical sharing are unqualified; overlapping length is not free hardware.',
                     'Two-minute capacity is arithmetic; safe braking, availability, dwell, passenger control and receiving-power loss require independent qualification.',
                     'Prototype civil quantities are very heavy and unoptimised; reinforcement, foundations and complete installed costs remain unknown.'],
        budget=dict(native_solver_runs=0,physical_tests=0,ordinary_numerical_worker=True),**FLAGS)
    result['evaluation_id'] = selection.identity(result)
    return result


def _number(value, places=0):
    return 'unknown' if value is None else f'{value:,.{places}f}'


def city_readme(value, detailed=False):
    name=value['city']['name']; t=value['totals']; v=value['vehicle']; s=value['service']; q=value['quantities']
    maplink='../../maglev/network.svg' if detailed else 'engineering/maglev/network.svg'
    # The package is city/engineering/current, so its historical sibling is
    # ../maglev; the frontdoor uses the complete city-relative path.
    if detailed: maplink='../maglev/network.svg'
    legacy='../maglev/README.md' if detailed else 'engineering/maglev/README.md'
    summary='summary.json' if detailed else 'engineering/current/summary.json'
    intro=(f'# {name} — comfort-first OpenSourceRail development design\n\n'
           'OpenSourceRail seeks simple, affordable, locally maintainable transport: repeated lightweight trains, '
           'concrete beams with passive steel facings, onboard permanent magnets and suspension controls, '
           'and powered launch/receiving zones at stations. The current development default gives passengers '
           'four-abreast seating and a controlled low standing load. Transfers connect fixed lines.\n\n'
           '**Selected for development; physical operation is not yet established.** This city uses the same '
           'six-car comfort candidate as the system default. Existing geographic corridors and stops are retained.\n\n'
           f'![Retained city geography and network context]({maplink})\n\n'
           'The retained map preserves its underlying city detail. Its older engineering annotations are historical; '
           'the current vehicle and service calculations below supersede those annotations. Route and station sites remain proposals.\n\n')
    rows=[intro,'| Current development basis | Result |','|---|---:|',
          '| Formation | 6 × 17 m cars |','| Per-car accommodation | 44 seats + 2 wheelchair places; no planned standing |',
          '| Passenger doors | Two doors on one side per car |',
          f"| Accounted tare / cap-loaded material mass per car | {v['accounted_tare_kg_per_car']/1000:.3f} / {v['accounted_cap_loaded_kg_per_car']/1000:.3f} t |",
          '| Complete installed mass, CG and inertia | Unknown |',
          f"| Launch-speed cap / target headway / dwell | {s['launch_speed_cap_m_s']*3.6:g} km/h / {s['headway_s']:g} s / {s['dwell_s']:g} s |",
          f"| Arithmetic normal capacity | {s['normal_capacity_pphpd_arithmetic']:,.0f} passengers/hour/direction |",
          '| Retained 14,400 pphpd comparison | Not met by this comfort capacity |',
          f"| Lines / retained route / proposed stops | {t['lines']} / {t['retained_route_length_m']/1000:,.1f} km / {t['station_records']} |",
          f"| Peak active + spare + cold reserve trainsets | {_number(t['peak_active_trainsets'])} + {_number(t['spare_trainsets'])} + {_number(t['cold_reserve_trainsets'])} |",
          f"| Total trainsets / cars | {_number(t['total_trainsets'])} / {_number(t['cars'])} |",
          '| Additional stops imposed by this default | 0 |',
          f"| Counted mainline station winding, directional | {_number(None if t['total_direction_winding_m'] is None else t['total_direction_winding_m']/1000,1)} km |",
          f"| Mainline powered coverage / overlapping intervals | {_number(None if t['mainline_motor_coverage_fraction'] is None else 100*t['mainline_motor_coverage_fraction'],1)}% / {t['motor_overlap_count']} |",'',
          'Fleet is recalculated from each actual coast/brake leg, retained terminal-time hypotheses, 35-second dwell, '
          'a 120-second target interval, 12% rounded-up spares and one cold reserve per line. '
          'Every reachable arrival selects the shortest full-engagement option from 350/450/600/800/900/1,000 m. '
          'These motors occupy substantial route length; each direction needs at least two independently routed train phase/current branches. '
          'Terminal motors and safe operational headway remain unqualified.','',
          f"Analytical result: **{value['gates']['engineering_screen']}**; {t['lines_with_unreachable_events']} lines have unreachable coasting legs and "
          f"{t['lines_with_station_library_failures']} lines have station-library failures. Failed cases stay in the data; their complete fleet/quantity totals remain unknown.",'',
          f"The selected prototype civil interface counts **{q['counted_steel_stock_tonnes_per_direction_km']:,.1f} tonnes of steel per directional kilometre**, "
          'before unclosed reinforcement, prestress, end blocks, bearings, piers and foundations. '
          'This heavy extrapolation is a redesign input, not an optimised viaduct or an installed bill. '
          'All current CAPEX, OPEX, debt service, imported-content and price-coverage totals remain unknown pending matched designs and quotations.','',
          'Stable multiaxis hover, a complete equipped vehicle, actual station thrust/electrical/thermal limits, '
          'fault stopping, civil acceptance and safe two-minute operation remain open. The mass ledger, energy requirements, '
          'winding layout, source hashes and failures are retained in the machine-readable record.','',
          f"[Current calculation and source identities]({summary}) · [Historical ferrite planning package]({legacy}) · "
          f"[Historical city front page at the pinned source](https://github.com/modernecotech/OpenSourceRail/blob/{LEGACY_REVISION}/{value['city_path']}/README.md)", '',
          f"Candidate `{value['candidate_id']}`  ",f"Body `{value['body_candidate_id']}`  ",
          f"Magnet `{value['magnet_component_id']}`  ",f"Selection `{value['selection_id']}`  ",
          f"Evaluation `{value['evaluation_id']}`",'']
    if detailed:
        rows += ['| Line | Fleet | Circuit minutes | Directional winding km | Coast failures |',
                 '|---|---:|---:|---:|---:|']
        for line in value['lines']:
            rows.append(f"| {line['line']} | {_number(line['total_trainsets'])} | {_number(None if line['circuit_s'] is None else line['circuit_s']/60,1)} | {_number(None if line['direction_winding_m'] is None else line['direction_winding_m']/1000,1)} | {len(line['coast_failures'])} |")
        rows += ['','Hotel-energy coefficient: **'+_number(value['energy']['hotel_kWh_per_peak_operating_hour_per_kW_per_car'])+
                 ' kWh per peak operating hour per actual kW/car**. Actual auxiliary load, conversion efficiency, terminal energy and complete operating energy remain unknown.','']
    return '\n'.join(rows)


def _publish(value, output, update_readme):
    city_root=Path(output)/value['city_path']; package=city_root/PACKAGE
    files={'summary.json':_bytes(value),'README.md':city_readme(value,True).encode()}
    manifest=dict(schema='osr-current-city-publication/1',selection_id=value['selection_id'],
                  development_default=True,
                  candidate_id=value['candidate_id'],body_candidate_id=value['body_candidate_id'],
                  magnet_component_id=value['magnet_component_id'],evaluation_id=value['evaluation_id'],
                  source_sha256=value['source_sha256'],files_sha256={k:sha256(v).hexdigest() for k,v in files.items()},
                  **FLAGS)
    if update_readme:
        front=city_readme(value).encode();_write(city_root/'README.md',front)
        manifest['city_frontdoor_sha256']=sha256(front).hexdigest()
    for name,raw in files.items(): _write(package/name,raw)
    _write(package/'manifest.json',_bytes(manifest))
    return manifest


def publish_city(citypath_or_slug, baseline=None, output=None, root=ROOT, civil=None, update_readme=False):
    value=evaluate_city(citypath_or_slug,baseline,root,civil)
    _publish(value,Path(root) if output is None else Path(output),update_readme)
    return value


def _index_row(value):
    return dict(**value['city'],path=value['city_path'],summary_path=value['city_path']+'/'+PACKAGE+'/summary.json',
                development_default=True,
                selection_id=value['selection_id'],candidate_id=value['candidate_id'],
                body_candidate_id=value['body_candidate_id'],magnet_component_id=value['magnet_component_id'],
                evaluation_id=value['evaluation_id'],totals=value['totals'],
                engineering_screen=value['gates']['engineering_screen'],**FLAGS)


def publish_all(output=None, baseline=None, root=ROOT, civil=None, update_readmes=True):
    """One bounded worker; output is a mirrored repository tree, never an archive rewrite."""
    root=Path(root).resolve();output=root if output is None else Path(output).resolve()
    selected,vehicle,_,_=_baseline(baseline,root)
    rows=[];payloads={};sources={};source_routes={}
    for descriptor in catalogue(root):
        value=evaluate_city(root/descriptor['path']/'city.json',baseline or selected,root,civil)
        _publish(value,output,update_readmes)
        rows.append(_index_row(value));sources.update(value['source_sha256'])
        source_routes[value['city_path']+'/city.json']=value['geography']['city_json_sha256']
        names=[value['city_path']+'/'+PACKAGE+'/'+n for n in ('summary.json','README.md','manifest.json')]
        if update_readmes:names.append(value['city_path']+'/README.md')
        payloads.update({name:_digest(output/name) for name in names})
    summary=dict(city_count=len(rows),line_count=sum(r['totals']['lines'] for r in rows),
                 cities_with_all_station_library_screens=sum(r['totals']['all_station_library_screens_pass'] for r in rows),
                 cities_with_unreachable_events=sum(bool(r['totals']['lines_with_unreachable_events']) for r in rows),
                 cities_with_station_library_failures=sum(bool(r['totals']['lines_with_station_library_failures']) for r in rows),
                 total_trainsets_if_all_reachable=None if any(r['totals']['total_trainsets'] is None for r in rows) else sum(r['totals']['total_trainsets'] for r in rows),
                 current_frontdoors_generated=update_readmes)
    index=dict(schema='osr-current-city-catalogue/1',city_count=len(rows),selection_id=selected['selection_id'],
               development_default=True,
               candidate_id=vehicle['candidate_id'],body_candidate_id=vehicle['body_candidate_id'],
               magnet_component_id=vehicle['magnet_component_id'],cities=rows,summary=summary,
               source_sha256=dict(sorted(sources.items())),source_city_json_sha256=source_routes,
               physical_train_journeys_executed=0,ordinary_numerical_workers=1,**FLAGS)
    index['evaluation_id']=selection.identity(index)
    _write(output/INDEX,_bytes(index));payloads[INDEX]=_digest(output/INDEX)
    receipt=dict(schema='osr-current-city-catalogue-publication/1',selection_id=selected['selection_id'],
                 development_default=True,
                 candidate_id=vehicle['candidate_id'],body_candidate_id=vehicle['body_candidate_id'],
                 magnet_component_id=vehicle['magnet_component_id'],evaluation_id=index['evaluation_id'],
                 files_sha256=dict(sorted(payloads.items())),summary=summary,**FLAGS)
    _write(output/INDEX_MANIFEST,_bytes(receipt))
    return index


def verify_all(output=None, baseline=None, root=ROOT, civil=None, replay=True):
    """Check source and payload integrity; optionally independently replay the analytics."""
    root=Path(root).resolve();output=root if output is None else Path(output).resolve()
    selected,vehicle,_,_=_baseline(baseline,root)
    index=read_catalogue(output);receipt=json.loads((output/INDEX_MANIFEST).read_bytes())
    if index['selection_id']!=selected['selection_id'] or index['candidate_id']!=vehicle['candidate_id']:
        raise ValueError('Published city selection differs')
    if index['evaluation_id']!=selection.identity({k:v for k,v in index.items() if k!='evaluation_id'}):
        raise ValueError('Catalogue evaluation identity differs')
    if any(receipt.get(k)!=index[k] for k in ('selection_id','candidate_id','body_candidate_id','magnet_component_id','evaluation_id')):
        raise ValueError('City catalogue receipt identity differs')
    for name,digest in receipt['files_sha256'].items():
        if Path(name).is_absolute() or '..' in Path(name).parts:
            raise ValueError('Ordinary relative city payload path required')
        if _digest(output/name)!=digest:raise ValueError('City payload differs: '+name)
    for name,digest in index['source_sha256'].items():
        actual=_digest(__file__) if name==CODE else _digest(service.__file__) if name=='engineering/comfort_design/service.py' else _digest(root/name)
        if actual!=digest:raise ValueError('City source differs: '+name)
    if {r['slug'] for r in index['cities']}!={r['slug'] for r in catalogue(root)}:
        raise ValueError('Current catalogue does not cover all geographic cities')
    for row in index['cities']:
        value=json.loads((output/row['summary_path']).read_bytes())
        if any(value.get(k)!=index[k] for k in ('selection_id','candidate_id','body_candidate_id','magnet_component_id')):
            raise ValueError('City physical/selection identity differs: '+row['slug'])
        if value['evaluation_id']!=selection.identity({k:v for k,v in value.items() if k!='evaluation_id'}):
            raise ValueError('City evaluation identity differs: '+row['slug'])
        if any(value.get(k) is not val for k,val in FLAGS.items()):
            raise ValueError('City qualification flag differs')
        if row!=_index_row(value):raise ValueError('Catalogue and city differ: '+row['slug'])
        if replay and value!=evaluate_city(root/row['path']/'city.json',baseline or selected,root,civil):
            raise ValueError('City replay differs: '+row['slug'])
    return dict(verified=True,replayed=replay,city_count=len(index['cities']),
                selection_id=selected['selection_id'],candidate_id=vehicle['candidate_id'],
                source_and_payload_integrity=True,physical_acceptance=False)
