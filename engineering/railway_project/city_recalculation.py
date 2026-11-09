"""Bind Samawah's five-line outline to the exact package-07 detailed body.

This is a bounded held definition, not an adapter that relabels the earlier
outline vehicle or invents a completed journey. Geometry and declared planning
controls are recomputed; unsupported service, installed quantities and costs
remain explicit. The old publication is read as geographic ancestry only.
"""
from copy import deepcopy
from math import ceil, floor, fsum, isclose, isfinite, sqrt
from pathlib import Path
import argparse
import gzip
import json

from engineering.compact_drive.common import validate as validate_body
from engineering.design_search.model_cost import SCOPES
from engineering.outline import city_inputs, planning_geometry
from engineering.station_rail import ROOT
from engineering.station_rail.common import digest, encoded, identity

PRODUCER = 'engineering/railway_project/city_recalculation.py'
POLICY = 'engineering/railway_project/city-recalculation-policy.json'
BODY_FILE = 'docs/design-engine/v06-design-closure/compact-drive-corridor/body.json.gz'
BODY = '75075df9247dfff7082a78eadc273d3a99f37e5486450621536c43b1bfa2f797'
BODY_EVALUATION = 'fdac4907a6a867f0b4f27e0876a772d1b54d526ec323beb3b6d9a155e0e00b21'
PARENT = '9f6d223074b3438a546d5b3d71cd9b970807387ef0542023bed79bef46dbdeba'
CASES = ('low', 'base', 'high')
FLAGS = dict(physical_accepted=False, engineering_accepted=False,
    manufacturing_release=False, operating_release=False,
    selected_reference_changed=False, movement_authority=False)
UNKNOWN_INPUTS = ('grade_profile', 'available_force_map', 'independent_braking_map',
                  'ground_profile', 'site_utilities', 'local_price_profile')


def _number(v, name, *, zero=False):
    if type(v) not in (float, int) or not isfinite(v) or (v < 0 if zero else v <= 0):
        raise ValueError('Explicit finite '+('nonnegative ' if zero else 'positive ')+name+' required')
    return v


def _sources(root, *maps):
    root = Path(root).resolve(); result = {}
    for mapping in maps:
        for name, want in mapping.items():
            path = Path(name)
            if (path.is_absolute() or '..' in path.parts or path.as_posix() != name or
                    not (root/path).resolve().is_relative_to(root)):
                raise ValueError('Ordinary in-root source path required')
            if name in result and result[name] != want:
                raise ValueError('Mixed city/body source epochs: '+name)
            if digest(root/path) != want:
                raise ValueError('City/body source changed: '+name)
            result[name] = want
    for name in (PRODUCER, POLICY, 'engineering/station_rail/common.py',
                 'engineering/compact_drive/common.py', 'engineering/design_search/model_cost.py',
                 'engineering/outline/city_inputs.py', 'engineering/outline/planning_geometry.py'):
        want = digest(root/name)
        if name in result and result[name] != want:
            raise ValueError('Mixed adapter source epochs: '+name)
        result[name] = want
    return dict(sorted(result.items()))


def _policy(value):
    p = deepcopy(value)
    if p.get('schema') != 'osr-detailed-city-outline-policy/1' or p.get('city_slug') != 'samawah':
        raise ValueError('Explicit bounded Samawah policy required')
    if p.get('line_ids') != ['line-1', 'line-2', 'line-3', 'line-4', 'line-5']:
        raise ValueError('Exact five-line policy coverage required')
    positive = ('normal_places_per_train', 'passenger_mass_kg', 'speed_cap_m_s', 'acceleration_m_s2',
        'deceleration_m_s2', 'dwell_s', 'turnback_s', 'planning_occupancy', 'planning_availability',
        'headway_quantum_s', 'maximum_headway_s', 'spare_fraction', 'operating_hours_per_day',
        'operating_days_per_year', 'design_life_years', 'shift_hours', 'production_shifts_per_day',
        'civil_shifts_per_day', 'initial_operating_shifts_per_day', 'extended_operating_shifts_per_day',
        'reference_span_m', 'reference_fastening_pitch_m', 'reference_platform_length_m',
        'hotel_kw_per_car_hypothesis', 'reserve_hotel_fraction_hypothesis', 'hotel_charge_efficiency_hypothesis')
    for key in positive: _number(p.get(key), key)
    _number(p.get('running_time_margin_fraction'), 'running time margin', zero=True)
    if (p['normal_places_per_train'] != 276 or p['passenger_mass_kg'] != 75 or
        p['operating_hours_per_day'] > 24 or p['operating_days_per_year'] > 366 or
        any(p[k] > 1 for k in ('planning_occupancy', 'planning_availability', 'spare_fraction',
                              'hotel_charge_efficiency_hypothesis'))):
        raise ValueError('Policy outside declared formation/calendar/fraction domain')
    if any(p.get(k) is not None for k in UNKNOWN_INPUTS):
        raise ValueError('This held adapter cannot admit new physical/site evidence through a policy value')
    if set(p.get('demand_pphpd_cases', {})) != set(CASES):
        raise ValueError('Three explicit demand sensitivity controls required')
    for c in CASES: _number(p['demand_pphpd_cases'][c], 'demand/'+c)
    return p


def _leg_time(distance, p):
    """Point-train kinematic request, without an available-force/braking claim."""
    a = p['acceleration_m_s2']; b = p['deceleration_m_s2']
    speed = min(p['speed_cap_m_s'], sqrt(2*distance/(1/a+1/b)))
    stroke = speed*speed/2*(1/a+1/b)
    return (speed/a+speed/b+max(0., distance-stroke)/speed)*(1+p['running_time_margin_fraction'])


def _city(city, trusted_input_id, p):
    if (city.get('schema') != 'osr-city-outline-input/1' or
        city.get('input_id') != trusted_input_id or
        trusted_input_id != identity({k:v for k,v in city.items() if k != 'input_id'})):
        raise ValueError('Exact caller-authenticated city input required')
    if city.get('city', {}).get('slug') != 'samawah':
        raise ValueError('Only the assigned Samawah outline is supported')
    lines = city.get('lines', [])
    if len(lines) != 5 or {r['line_id'] for r in lines} != set(p['line_ids']):
        raise ValueError('Exactly one of each existing five lines required')
    if any(city.get(k) is not False for k in FLAGS):
        raise ValueError('City inputs cannot grant acceptance')
    for line in lines:
        if line['shape'] != 'radial':
            raise ValueError('This bounded Samawah adapter covers its five radial lines only')
        route = planning_geometry.route(line['coordinates'], line['shape'])[-1]
        if not isclose(route, line['route_m'], abs_tol=1e-6):
            raise ValueError('Mapped geometry and route quantity disagree')
        stops = line['stops']
        if (len(stops) < 2 or len({r['id'] for r in stops}) != len(stops) or
            any(not 0 <= r['chainage_m'] <= route+1e-6 for r in stops) or
            any(a['chainage_m'] >= b['chainage_m'] for a,b in zip(stops, stops[1:]))):
            raise ValueError('Unique ordered mapped station markers required')
        expected = [(a['id'],b['id'],b['chainage_m']-a['chainage_m']) for a,b in zip(stops,stops[1:])]
        actual = [(r['from_stop'],r['to_stop'],r['distance_m']) for r in line['legs']]
        if expected != actual: raise ValueError('Mapped leg/stop quantities disagree')
    return lines


def evaluate(city, body, policy, *, trusted_city_input_id, root=ROOT):
    """Calculate a held outline from an authenticated city and package-07 body.

    The caller must authenticate ``trusted_city_input_id`` using its source
    manifest. Internal seals alone do not establish external authenticity.
    ``from_catalogue`` provides that source-bound production entry point.
    """
    validate_body(body)
    if (body.get('schema') != 'osr-vehicle-installation/1' or
        body.get('candidate_id') != BODY or body.get('evaluation_id') != BODY_EVALUATION or
        body.get('parent_candidate_id') != PARENT):
        raise ValueError('Exact package-07 body candidate and evaluation required')
    contract = body.get('compact_drive_contract', {})
    if (contract.get('candidate_id') != BODY or contract.get('contract_id') != identity(
        {k:v for k,v in contract.items() if k != 'contract_id'})):
        raise ValueError('Body and drive contract differ')
    ownership = contract.get('mass_ownership', {})
    if (ownership.get('all_new_drive_components_in_body_BOM') is not True or
        ownership.get('additional_external_drive_mass_kg') != 0):
        raise ValueError('Exact counted drive ownership required; no external drive addition')
    p = _policy(policy); lines = _city(city, trusted_city_input_id, p)
    sources = _sources(root, city['source_sha256'], body['source_sha256'])
    layout = body['policy']['layout']
    if layout['cars'] != 6 or layout['car_length_m'] != 17:
        raise ValueError('Explicit six17m formation required')
    train_length = layout['cars']*layout['car_length_m']+(layout['cars']-1)*layout['intercar_gap_m']
    if p['reference_platform_length_m'] < train_length:
        raise ValueError('Declared platform cannot contain the exact detailed formation')
    mass = {r['name']:r['train_mass_kg'] for r in body['mass_scenarios']}
    for c in CASES:
        for load in ('tare','normal','crowd-control'): _number(mass.get(load+'-'+c), load+' mass/'+c)
        if not isclose(mass['normal-'+c]-mass['tare-'+c], 276*p['passenger_mass_kg'], abs_tol=1e-7):
            raise ValueError('Declared passenger places and detailed mass scenarios differ')
    parts = body['parts']
    if len({r['id'] for r in parts}) != len(parts): raise ValueError('Duplicate counted part owner')
    direct = {c:fsum(r['quantity_per_train']*r['direct_cost_each_usd'][c] for r in parts) for c in CASES}
    if any(not isclose(direct[c],body['direct_parts_process_usd'][c],rel_tol=1e-10) for c in CASES):
        raise ValueError('Counted part/process subtotal differs')
    geometry = [dict(line_id=r['line_id'], shape=r['shape'], coordinates=deepcopy(r['coordinates']),
        stops=[{k:deepcopy(s[k]) for k in ('id','lon','lat','chainage_m')} for s in r['stops']])
        for r in sorted(lines,key=lambda r:r['line_id'])]
    physical = dict(schema='osr-detailed-city-outline-physical/1', body_candidate_id=BODY,
        mapped_lines=geometry, interchanges=deepcopy(city['interchanges']),
        civil_classification=deepcopy(city['civil_segments']))
    candidate = identity(physical); records = []; failures = []
    for line in sorted(lines,key=lambda r:r['line_id']):
        n = len(line['stops']); moving = fsum(_leg_time(r['distance_m'],p) for r in line['legs'])
        one_way = moving+(n-2)*p['dwell_s']; cycle = 2*(one_way+max(p['turnback_s'],p['dwell_s']))
        scenarios = {}
        for c in CASES:
            headway = floor(min(p['maximum_headway_s'],276*3600*p['planning_occupancy']*
                p['planning_availability']/p['demand_pphpd_cases'][c])/p['headway_quantum_s'])*p['headway_quantum_s']
            if headway <= 0: raise ValueError('Demand cannot fit a positive declared headway quantum')
            active = ceil(cycle/headway); spare = max(1,ceil(active*p['spare_fraction']))
            scenarios[c] = dict(peak_demand_pphpd=p['demand_pphpd_cases'][c],headway_s=headway,
                active_trainsets=active,spare_trainsets=spare,total_trainsets=active+spare,
                annual_train_km=2*line['route_m']/1000*3600/headway*p['operating_hours_per_day']*p['operating_days_per_year'],
                loaded_train_mass_kg_hypothesis=mass['normal-'+c],available_force_N=None,
                braking_distance_m=None,traction_grid_kwh=None)
        overlaps = [dict(from_stop=r['from_stop'],to_stop=r['to_stop'],distance_m=r['distance_m'])
                    for r in line['legs'] if r['distance_m'] < p['reference_platform_length_m']]
        if overlaps: failures.append(dict(line_id=line['line_id'],kind='overlapping-standard-platform-envelope',legs=overlaps))
        records.append(dict(line_id=line['line_id'],city_candidate_id=candidate,body_candidate_id=BODY,
            body_evaluation_id=BODY_EVALUATION,route_m=line['route_m'],station_markers=n,
            leg_count=len(line['legs']),normal_places_per_train=276,train_length_m=train_length,
            required_platform_length_m=p['reference_platform_length_m'],
            assumed_one_way_runtime_s=one_way,assumed_cycle_s=cycle,scenarios=scenarios,
            runtime_basis='Point-train kinematic allowance; no jerk, available force, braking, adhesion, charging or thermal verification',
            native_service_complete=False,service_evaluation_id=None))
    totals = {c:{k:sum(r['scenarios'][c][k] for r in records) for k in
        ('active_trainsets','spare_trainsets','total_trainsets','annual_train_km')} for c in CASES}
    auxiliary = {c:(totals[c]['active_trainsets']+totals[c]['spare_trainsets']*
        p['reserve_hotel_fraction_hypothesis'])*6*p['hotel_kw_per_car_hypothesis']*
        p['operating_hours_per_day']*p['operating_days_per_year']/p['hotel_charge_efficiency_hypothesis']
        for c in CASES}
    route_m = fsum(r['route_m'] for r in records); stations = sum(r['station_markers'] for r in records)
    bays = {r['line_id']:ceil(r['route_m']/p['reference_span_m']) for r in records}
    quantities = dict(route_m=route_m,lines=5,station_markers=stations,
        standard_bays_by_line=bays,standard_beams=2*sum(bays.values()),
        standard_shared_bents=sum(v+1 for v in bays.values()),running_rail_m=4*route_m,
        running_fastening_sets=sum(ceil(4*r['route_m']/p['reference_fastening_pitch_m']) for r in records),
        shared_factory_campaigns=1,shared_depot_provisions=1,shared_city_protection_systems=1,
        detailed_civil_load_evaluation_id=None,installed_quantities_complete=False)
    scope_quantities = {
        'rolling-stock':dict(active_trainsets={c:totals[c]['active_trainsets'] for c in CASES}),
        'fleet':dict(reserve_trainsets={c:totals[c]['spare_trainsets'] for c in CASES}),
        'guideway':dict(standard_beams=quantities['standard_beams'],rail_m=4*route_m,fastening_sets=quantities['running_fastening_sets'],new_load_check_required=True),
        'stations-power':dict(line_station_markers=stations,boarding_faces=2*stations,shared_city_protection_systems=1,installed_charger_and_grid_capacity=None),
        'construction':dict(standard_shared_bents=quantities['standard_shared_bents'],beam_erections=quantities['standard_beams'],foundation_design=None,terminal_and_station_spread_geometry=None),
        'factory-tooling':dict(shared_campaigns=1,production_shifts_per_day=p['production_shifts_per_day'],tooling_capacity=None),
        'land-utilities-depot':dict(shared_depot_provisions=1,land_area_m2=None,utility_quantities=None),
        'energy':dict(annual_train_km={c:totals[c]['annual_train_km'] for c in CASES},
            conditional_vehicle_auxiliary_grid_kwh_cases=auxiliary,traction_grid_kwh=None,
            station_depot_and_drive_cooling_kwh=None,complete_actual_grid_kwh=None,available_force_map=None),
        'operations':dict(annual_train_km={c:totals[c]['annual_train_km'] for c in CASES},staff_roster=None),
        'maintenance':dict(fleet={c:totals[c]['total_trainsets'] for c in CASES},service_intervals=None),
        'renewals':dict(accounting_years=p['design_life_years'],qualified_component_lives=None),
        'recovery':dict(lines_requiring_protected_recovery=5,rescue_equipment=None),
        'reliability':dict(planning_availability_hypothesis=p['planning_availability'],measured_availability=None),
        'disposal':dict(accounting_years=p['design_life_years'],removal_process=None)}
    scopes = []
    for scope in SCOPES:
        known = None
        if scope in ('rolling-stock','fleet'):
            key = 'active_trainsets' if scope == 'rolling-stock' else 'spare_trainsets'
            known = {c:totals[c][key]*direct[c] for c in CASES}
        row = dict(scope=scope,city_candidate_id=candidate,body_candidate_id=BODY,body_evaluation_id=BODY_EVALUATION,
            quantities=scope_quantities[scope],cost_usd={c:None for c in CASES},known_counted_BOM_process_subtotal_usd=known,
            cost_complete=False,source_class='calculated request; remaining costs unknown',
            basis='Disjoint city scope; counted BOM subtotal excludes delivered/installed completion and is not a complete train or project price')
        row['account_id'] = identity(row); scopes.append(row)
    minimum_shifts = ceil(p['operating_hours_per_day']/p['shift_hours'])
    shift_holds = []
    if minimum_shifts > p['initial_operating_shifts_per_day']:
        shift_holds.append('The declared '+str(p['operating_hours_per_day'])+
            '-hour service day exceeds '+str(p['initial_operating_shifts_per_day'])+
            ' shifts of '+str(p['shift_hours'])+' hours; extended coverage needs an explicit workforce/relief roster.')
    result = dict(schema='osr-detailed-city-recalculation/1',candidate_id=candidate,physical_definition=physical,
        body_candidate_id=BODY,body_evaluation_id=BODY_EVALUATION,
        source_city_input_id=city['input_id'],source_planning_revision_id=city['planning_revision_sha256'],
        historical_outline_reference_ids=deepcopy(city['reference_candidate_ids']),
        inherited_vehicle_service_cost_results=False,scalar_pilot_cost_per_km_used=False,
        policy=deepcopy(p),policy_id=identity(p),lines=records,quantities=quantities,fleet_request_cases=totals,
        scope_accounts=scopes,scope_totals_usd={s:{c:None for c in CASES} for s in SCOPES},
        known_counted_BOM_process_subtotal_usd={c:totals[c]['total_trainsets']*direct[c] for c in CASES},
        body_mass_scenarios_kg=mass,body_mass_uncertainty=deepcopy(body['mass_uncertainty']),
        installed_mass_complete=body['installed_mass_complete'],
        workforce_request=dict(production_shifts_per_day=p['production_shifts_per_day'],civil_shifts_per_day=p['civil_shifts_per_day'],
            initial_operating_shifts_per_day=p['initial_operating_shifts_per_day'],shift_hours=p['shift_hours'],
            minimum_operating_shifts_for_declared_calendar=minimum_shifts,
            initial_shift_coverage_complete=p['initial_operating_shifts_per_day']*p['shift_hours']>=p['operating_hours_per_day'],
            extended_shift_coverage_possible=p['extended_operating_shifts_per_day']>=minimum_shifts,staff_roster=None),
        unknown_inputs={k:None for k in UNKNOWN_INPUTS},definition_failures=failures,
        assumptions=['Demand cases are shared declared controls for each line, not a Samawah demand forecast.',
            'Kinematic running and fleet requests assume the requested acceleration/braking; available capability remains unknown.',
            'Existing body mass scenarios are retained as hypotheses with their original uncertainty; installed mass is incomplete.',
            'Twenty-metre span/rail counts are reference quantity requests only; exact-body civil loads, stations, terminals and site design need evaluation.',
            'Shared factory, depot and city protection requests occur once; five independent project prices are not summed.',
            'All raw station markers are retained. Close stations remain a definition failure; no automatic closure or access approval follows.'],
        holds=['Exact-body service and available force/braking/thermal/charging evidence absent.',
            'Exact-body mapped civil and station/terminal assemblies not evaluated.',
            'All fourteen complete scope prices and the complete whole-life NPV remain unknown.']+shift_holds,
        service_complete=False,cost_complete=False,simulation_complete=False,whole_life_NPV_usd={c:None for c in CASES},
        source_sha256=sources,**FLAGS)
    result['evaluation_id'] = identity(result)
    verify(result)
    return result


def verify(value):
    if (value.get('schema') != 'osr-detailed-city-recalculation/1' or value.get('evaluation_id') !=
        identity({k:v for k,v in value.items() if k != 'evaluation_id'})):
        raise ValueError('Sealed detailed-city recalculation required')
    if (value.get('candidate_id') != identity(value.get('physical_definition')) or
        value.get('body_candidate_id') != BODY or value.get('body_evaluation_id') != BODY_EVALUATION or
        value['physical_definition'].get('body_candidate_id') != BODY):
        raise ValueError('Exact physical city/body identity required')
    if any(value.get(k) is not False for k in (*FLAGS,'service_complete','cost_complete','simulation_complete')):
        raise ValueError('Held outline cannot confer service/cost closure or acceptance')
    if value.get('scalar_pilot_cost_per_km_used') is not False or value.get('inherited_vehicle_service_cost_results') is not False:
        raise ValueError('No inherited economics or fixed cost/km scaling')
    p = _policy(value['policy'])
    if (value.get('policy_id') != identity(p) or value.get('installed_mass_complete') is not False or
        value.get('unknown_inputs') != dict.fromkeys(UNKNOWN_INPUTS) or
        value.get('whole_life_NPV_usd') != dict.fromkeys(CASES)):
        raise ValueError('Held body, policy and unknown evidence must remain explicit')
    lines = value.get('lines', [])
    physical_lines = value['physical_definition'].get('mapped_lines', [])
    wanted = set(p['line_ids'])
    if (len(lines) != 5 or len(physical_lines) != 5 or
        {r['line_id'] for r in lines} != wanted or {r['line_id'] for r in physical_lines} != wanted):
        raise ValueError('Exactly five distinct physical and evaluated city lines required')
    physical_by_id = {r['line_id']:r for r in physical_lines}
    for row in lines:
        geo = physical_by_id[row['line_id']]
        if (not isclose(row['route_m'], planning_geometry.route(geo['coordinates'], geo['shape'])[-1], abs_tol=1e-6) or
            row['station_markers'] != len(geo['stops']) or set(row['scenarios']) != set(CASES)):
            raise ValueError('Mapped physical and evaluated line quantities differ')
        if any(row['scenarios'][c].get(k) is not None for c in CASES for k in
               ('available_force_N','braking_distance_m','traction_grid_kwh')):
            raise ValueError('Held service cannot invent available force, braking or traction energy')
    rows = value.get('scope_accounts', [])
    if len(rows) != 14 or {r['scope'] for r in rows} != set(SCOPES) or set(value['scope_totals_usd']) != set(SCOPES):
        raise ValueError('All fourteen unique cost scopes required')
    if any(v != dict.fromkeys(CASES) for v in value['scope_totals_usd'].values()):
        raise ValueError('Incomplete scope totals must remain unknown')
    for r in rows:
        if (r.get('account_id') != identity({k:v for k,v in r.items() if k != 'account_id'}) or
            r.get('city_candidate_id') != value['candidate_id'] or r.get('body_candidate_id') != BODY or
            r.get('body_evaluation_id') != BODY_EVALUATION or r.get('cost_complete') is not False or
            r.get('cost_usd') != dict.fromkeys(CASES)):
            raise ValueError('Mixed or falsely completed cost scope')
    if any(r.get('city_candidate_id') != value['candidate_id'] or r.get('body_candidate_id') != BODY or
           r.get('body_evaluation_id') != BODY_EVALUATION or r.get('native_service_complete') is not False or
           r.get('service_evaluation_id') is not None for r in value['lines']):
        raise ValueError('Mixed or invented line service evaluation')
    return True


def from_catalogue(*, root=ROOT, body_path=None, policy=None):
    """Load authentic current geography; never modify the old city publication."""
    root = Path(root)
    path = root/BODY_FILE if body_path is None else Path(body_path)
    raw = path.read_bytes(); body = json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)
    city = city_inputs.load('samawah',root=root)
    p = json.loads((root/POLICY).read_bytes()) if policy is None else policy
    return evaluate(city,body,p,trusted_city_input_id=city['input_id'],root=root)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--body',type=Path); parser.add_argument('--output',type=Path,required=True)
    args = parser.parse_args(); result = from_catalogue(body_path=args.body)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open('xb') as stream: stream.write(encoded(result))
    print(json.dumps(dict(candidate_id=result['candidate_id'],evaluation_id=result['evaluation_id'],
        lines=len(result['lines']),scope_count=len(result['scope_accounts']),service_complete=False,cost_complete=False)))


if __name__ == '__main__': main()
