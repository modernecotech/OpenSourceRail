"""Compare urban and Airport standalone openings on an equal, all-day service offer."""
from collections import defaultdict
from hashlib import sha256
from math import ceil, isclose
from pathlib import Path
import tomllib

from cities.Baghdad import airport_opening as opening, airport_service
from engineering.outline import baghdad_diagrams as diagrams, baghdad_system as system
from engineering.outline import baghdad_power, baghdad_viaduct


def interchange_scores(groups):
    """Count distinct other corridors sharing named stops, including terminal stops."""
    memberships = defaultdict(set)
    for name, group in groups.items():
        for stop in group['outward_stops']:
            memberships[stop['interchange_hint']].add(name)
    scores = {}
    for name, group in groups.items():
        if name == 'Airport':
            continue
        shared = {s['interchange_hint']: sorted(memberships[s['interchange_hint']] - {name})
                  for s in group['outward_stops'] if len(memberships[s['interchange_hint']]) > 1}
        others = {line for names in shared.values() for line in names}
        scores[name] = {'other_corridors': sorted(others), 'number_of_other_corridors': len(others),
                        'shared_named_stops': shared, 'route_km': group['one_way_km']}
    return scores


def _price_corridor(cfg, group_name, reference, parent, receipt_usd, empty_share):
    route = reference['one_way_km']
    headway = 3600 // airport_service.OPENING_TPH
    v = {**cfg['vehicle'], 'peak_headway_s': headway}
    hourly = [airport_service.OPENING_TPH] * v['service_hours_per_day']
    plan = {**cfg['service_plan'], 'departures_per_hour_direction': hourly}
    group, _, _ = diagrams.group_diagram(group_name, reference['outward_stops'], route,
                                         dict(cfg, vehicle=v, service_plan=plan))
    stops, active = group['outward_stops'], group['diagrammed_sets']
    fleet = active + 3  # one workshop, one inspection, one ready spare
    supply_sites = 1 + ceil(route / 6)  # End feeds; intermediate feed allowance at up to 6 km spacing.
    days = v['service_days_per_year']
    passenger_km_train = group['scheduled_trips'] * route * days
    annual_km = passenger_km_train * (1 + empty_share)
    bundle = {'parent': parent, 'service_group': group_name, 'route_km': route,
              'stops': [stop['id'] for stop in stops], 'formation_cars': v['cars_per_train'],
              'fleet_sets': fleet, 'depots': 1, 'control_centres': 1, 'grid_sites': supply_sites,
              'supply': 'protected_conductor', 'span_m': cfg['selected_span_m'],
              'pier_family': cfg['selected_pier_family'], 'track_count': cfg['track_count']}
    network = baghdad_power.PowerNetwork(
        candidate_id=system._id(bundle), route_km=route, station_count=len(stops), line_count=1,
        normal_places_per_train=v['normal_places_per_train'], active_trainsets=active, fleet_trainsets=fleet,
        annual_train_km=annual_km, grid_site_count=supply_sites,
        train_mass_t=v['crowd_mass_t_per_train_before_supply'],
        train_energy_kwh_per_km=v['energy_kwh_per_train_km_overhead_comparator'],
        peak_headway_s=headway, dwell_s=v['dwell_s'], speed_cap_m_s=v['speed_cap_kmh']/3.6,
        service_hours_per_day=v['service_hours_per_day'], service_days_per_year=days)
    power = baghdad_power.compare_power(network, baghdad_power.PowerAssumptions(**cfg['power_assumptions']))['protected_conductor']
    civil = baghdad_viaduct.evaluate({group_name: route}, span_m=bundle['span_m'],
        common_pier=False, physical_candidate_id=power['physical_candidate_id'],
        rates=baghdad_viaduct.PlanningRates(**cfg['civil_rates']), train_crowd_mass_t=power['vehicle']['mass_t'],
        target_years=2, civil_start_year=1)
    direct, opex, _ = opening.common_opening_cost(cfg, civil, power, route, fleet, len(stops), supply_sites, annual_km)
    scopes = opening.allowances(direct, cfg['capital_rates_usd_m'])
    annual = sum(opex.values())
    capacity = v['normal_places_per_train'] * airport_service.OPENING_TPH
    break_even = annual * 1e6 / (days * receipt_usd)
    result = {'group_name': group_name, 'candidate_id': network.candidate_id, 'bundle': bundle,
              'power_evaluation_id': power['evaluation_id'], 'civil_evaluation_id': civil['evaluation_id'],
              'plan': group, 'hourly_departures_per_direction': hourly, 'scheduled_trips_day': group['scheduled_trips'],
              'route_km': route, 'station_count': len(stops), 'active_sets': active, 'fleet_sets': fleet,
              'annual_passenger_service_train_km': passenger_km_train,
              'annual_empty_train_km_allowance': passenger_km_train * empty_share, 'grid_sites': supply_sites,
              'annual_place_km': passenger_km_train * v['normal_places_per_train'],
              'normal_places_hour_direction': capacity, 'annual_grid_gwh': power['energy']['annual_grid_gwh'],
              'capital_usd_m': sum(scopes.values()), 'common_capital_scopes_usd_m': scopes,
              'capital_usd_per_place_hour_direction': sum(scopes.values()) * 1e6 / capacity,
              'annual_opex_usd_m': annual, 'annual_opex_rows_usd_m': opex,
              'paid_journeys_day_to_cover_common_opex': break_even,
              'paid_journeys_per_train_to_cover_common_opex': break_even / group['scheduled_trips'],
              'observed_paid_journeys_day': None, 'observed_peak_directional_load': None,
              'complete_opening_capital_usd_m': None, 'physical_accepted': False}
    result['evaluation_id'] = system._id(result)
    return result


def urban_comparison(cfg, report):
    """Select one urban survey priority and price both corridors at common input rates."""
    if (cfg['candidate_id'] != report['candidate_id'] or cfg['selected_span_m'] != 10
            or cfg['selected_pier_family'] != 'separate-track' or cfg['preferred_supply'] != 'protected-conductor'
            or cfg['track_count'] != 2 or cfg['vehicle']['cars_per_train'] != 6):
        raise ValueError('Urban opening needs the matching six-car protected-conductor first network')
    first = report['networks']['first']
    groups = first['groups']
    if ({name: group['one_way_km'] for name, group in groups.items()} != cfg['networks']['first']['lines_km']
            or any(not all(stop['id'].startswith(name + '-') for stop in group['outward_stops'])
                   for name, group in groups.items())):
        raise ValueError('Urban opening groups differ from named first-network routes')
    scores = interchange_scores(groups)
    # A transfer opportunity counts even at a terminal. Opening in isolation earns no transfer journeys here.
    name = min(scores, key=lambda g: (-scores[g]['number_of_other_corridors'],
                                     -len(scores[g]['shared_named_stops']), scores[g]['route_km'], g))
    market = tomllib.loads(opening.MARKET_INPUT.read_text())
    receipt = market['fare']['posted_iqd'][1] * market['fare']['receipt_fraction'][1] / market['currency']['iqd_per_usd']
    empty_share = tomllib.loads(opening.SITE_INPUT.read_text())['operations']['non_revenue_distance_share'][1]
    airport, urban = [_price_corridor(cfg, g, groups[g], first['selected_candidate_id'], receipt, empty_share)
                      for g in ('Airport', name)]
    if not isclose(urban['normal_places_hour_direction'], airport['normal_places_hour_direction']):
        raise ValueError('Demand comparison requires equal offered capacity')
    result = {'group_name': name, 'proxy_scores': scores, 'airport': airport, 'urban': urban,
              'timetable_parent_id': report['evaluation_id'],
              'selection_purpose': 'Urban demand survey priority based on the largest number of other corridors sharing named stops. Ties use more shared stops, then shorter distance and name.',
              'comparator_basis': 'Identical six-car service, three spares, two tracks, one depot and control centre per opening, endpoint and intermediate feeds at up to 6 km spacing. Generic 2026 USD costs before local site, feeder upgrades, staffing adjustments, financing and renewals.',
              'empty_mileage_share_for_both': empty_share, 'net_receipt_usd_per_paid_journey': receipt,
              'extra_paid_journeys_day_to_match_airport_operating_support':
                  urban['paid_journeys_day_to_cover_common_opex'] - airport['paid_journeys_day_to_cover_common_opex'],
              'required_observations': ['Origin–destination counts by hour and direction including fare-paying share, walking access, maximum loads and peak crowding.',
                                        'Terminal, depot and empty-stock paths, surveyed chainages, ground, land, utilities and construction bids for the urban alignment.',
                                        'Route-specific feed, isolation, thermal, protection and fault cases matched to the urban train positions.',
                                        'Observed road trip times, diversion by mode and value of time before valuing congestion relief.'],
              'rankable': False, 'source_sha256': {str(p.relative_to(system.ROOT)): sha256(p.read_bytes()).hexdigest()
                  for p in (Path(__file__).resolve(), opening.MARKET_INPUT, opening.SITE_INPUT,
                            *(Path(mod.__file__).resolve() for mod in (opening, airport_service, diagrams, system, baghdad_power, baghdad_viaduct)))}}
    result['evaluation_id'] = system._id(result)
    return result
