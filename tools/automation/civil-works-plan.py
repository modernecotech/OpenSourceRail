#!/usr/bin/env python3
"""Compile asset-bound civil methods, scope, dependencies and logistics requirements."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import io
import json
import math
from pathlib import Path
import tomllib

ROOT = Path(__file__).resolve().parents[2]
CITY = Path('cities/catalogue/west-asia/Iraq/Baghdad')
OUT = CITY / 'engineering/civil-works'
CONFIG = Path('design/programme/civil-works-plan.json')


def encoded(value):
    return (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n').encode()


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def csv_bytes(rows, fields):
    stream = io.StringIO(newline='')
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode()


def span_quantities(spans):
    """Count only identified catalogue orders; unique supports include specials."""
    if len({s['id'] for s in spans}) != len(spans):
        raise ValueError('duplicate span identity')
    catalogue = []
    special = []
    for span in spans:
        if span['length_m'] <= 0 or not math.isclose(
                span['end_chainage_m'] - span['start_chainage_m'], span['length_m'], abs_tol=.001):
            raise ValueError('span length and chainage disagree')
        if span['classification'] == 'catalogue-planning-span':
            expected = {'OSR-Pi20': 20, 'OSR-Pi25': 25}.get(span['beam_variant'])
            if expected != span['length_m'] or span['quantity'] != 2 or len(span['component_ids']) != 2:
                raise ValueError('catalogue order is not a complete identified two-beam bay')
            catalogue.append(span)
        elif span['classification'] == 'special-design-required':
            if span['component_ids'] or span['beam_variant'] is not None or span['quantity'] is not None:
                raise ValueError('unresolved special cannot have a catalogue beam order')
            special.append(span)
        else:
            raise ValueError('unknown span classification')
    component_ids = [key for span in catalogue for key in span['component_ids']]
    if len(set(component_ids)) != len(component_ids):
        raise ValueError('catalogue component identity is duplicated')
    variants = Counter(s['beam_variant'] for s in catalogue)
    metres = math.fsum(s['length_m'] for s in spans)
    return dict(running_alignment_m=round(metres, 3), catalogue_bays=len(catalogue),
                catalogue_alignment_m=round(math.fsum(s['length_m'] for s in catalogue), 3),
                pi20_beams=2 * variants['OSR-Pi20'], pi25_beams=2 * variants['OSR-Pi25'],
                catalogue_beams=len(component_ids), special_spans=len(special),
                special_alignment_m=round(math.fsum(s['length_m'] for s in special), 3),
                unique_proposed_supports=len({s[k] for s in spans for k in ('pier_a', 'pier_b')}),
                disconnected_runs=len({(s['line'], s['run']) for s in spans}),
                identified_average_span_m=round(metres / len(spans), 6) if spans else None)


def logistics_requirements(planning, launchers, rate, beam):
    """Required capacity under explicit assumptions, never available capacity."""
    values = [launchers, rate, planning['production_cycle_hours'], planning['production_calendar_hours_day'],
              planning['complete_vehicle_cycle_hours'], planning['haulage_window_hours'], planning['beams_per_trip'],
              planning['average_span_m'], beam['manufactured_study_mass_kg'], beam['concrete_m3']]
    if any(not math.isfinite(v) or v <= 0 for v in values):
        raise ValueError('positive finite resource assumptions required')
    if int(launchers) != launchers or int(planning['beams_per_trip']) != planning['beams_per_trip']:
        raise ValueError('equipment and complete cargo quantities must be integers')
    if any(not 0 < planning[k] <= 24 for k in ('erection_shift_hours', 'production_calendar_hours_day', 'haulage_window_hours')):
        raise ValueError('daily clock windows cannot exceed 24 hours')
    if not 0 < planning['erection_productive_fraction'] <= 1:
        raise ValueError('productive fraction must be in (0, 1]')
    if any(not math.isfinite(v) or v < 0 for v in planning['complete_vehicle_cycle_breakdown_hours'].values()):
        raise ValueError('negative/nonfinite vehicle cycle leg')
    yield_fraction = planning['first_pass_yield']
    if not 0 < yield_fraction <= 1:
        raise ValueError('first-pass yield must be in (0, 1]')
    if not 1 <= planning['erection_days_week'] <= 7 or not 1 <= planning['production_days_week'] <= 7:
        raise ValueError('invalid working week')
    if any(int(planning[k]) != planning[k] for k in ('erection_days_week', 'production_days_week')):
        raise ValueError('working days per week must be integers')
    if not math.isclose(math.fsum(planning['complete_vehicle_cycle_breakdown_hours'].values()),
                        planning['complete_vehicle_cycle_hours']):
        raise ValueError('complete vehicle cycle must include all declared legs and allowances')
    bays = launchers * rate
    beams = 2 * bays
    gross = beams / yield_fraction
    cycles = math.floor(planning['haulage_window_hours'] / planning['complete_vehicle_cycle_hours'])
    trips = math.ceil(beams / planning['beams_per_trip'])
    buffers = planning['beam_buffer_bays_per_front']
    if len(buffers) != 2 or buffers[0] <= 0 or buffers[1] < buffers[0]:
        raise ValueError('invalid buffer interval')
    positions_factor = planning['production_cycle_hours'] / planning['production_calendar_hours_day']
    handover = planning['erection_handover_hours_shift']
    maintenance = planning['erection_maintenance_hours_day']
    if any(not math.isfinite(v) or v < 0 for v in (handover, maintenance)):
        raise ValueError('negative/nonfinite shift allowance')
    productive = planning['erection_shift_hours'] * planning['erection_productive_fraction'] - handover - maintenance
    if productive <= 0:
        raise ValueError('no productive erection time after allowances')
    return dict(launchers=launchers, accepted_bays_launcher_working_day=rate,
                available_productive_erection_hours_launcher_day=round(productive, 6),
                maximum_serial_cycle_hours_required_for_rate=round(productive / rate, 6),
                accepted_bays_erection_day=bays, equivalent_route_m_erection_day=bays * planning['average_span_m'],
                accepted_beams_erection_day=beams, gross_cast_beams_erection_day=round(gross, 6),
                accepted_beams_erection_week=beams * planning['erection_days_week'],
                one_beam_mould_positions_peak_daily=math.ceil(gross * positions_factor),
                one_beam_mould_positions_weekly_smoothed=math.ceil(gross * planning['erection_days_week'] /
                                                                  planning['production_days_week'] * positions_factor),
                cargo_only_t_erection_day=round(beams * beam['manufactured_study_mass_kg'] / 1000, 6),
                pi25_only_gross_cast_concrete_m3_day=round(gross * beam['concrete_m3'], 6),
                loaded_beam_trips_day=trips, complete_trips_vehicle_day=cycles,
                required_vehicles_daily=math.ceil(trips / cycles) if cycles else None,
                route_cycle_fits_window=cycles > 0,
                buffer_accepted_beams=[2 * launchers * v for v in buffers],
                buffer_applies_only_to_sufficiently_long_released_runs=True,
                actual_available_supplier_beams_day=None, actual_available_haulage_trips_day=None,
                plant_and_route_qualified=False, achieved_daily_rate=None)


def validate_packages(packages):
    ids = {p['id'] for p in packages}
    if len(ids) != len(packages):
        raise ValueError('duplicate work package')
    pending = {p['id']: set(p['finish_predecessors']) for p in packages}
    for package in packages:
        if not package['accountable_role'] or not package['method']:
            raise ValueError('package needs responsible role and method')
        if not pending[package['id']] <= ids:
            raise ValueError('unknown predecessor')
        # This authoring tool cannot manufacture an acceptance or a quotation.
        if any(package[k] is not None for k in ('duration_working_days', 'installed_price_usd', 'accepted_release_record')):
            raise ValueError('external priced/accepted schedule requires a reviewed import contract')
    resolved = set()
    while pending:
        ready = {key for key, deps in pending.items() if deps <= resolved}
        if not ready:
            raise ValueError('cyclic civil package graph')
        resolved.update(ready)
        pending = {key: deps for key, deps in pending.items() if key not in ready}


def build(root=ROOT):
    source_paths = [CONFIG, CITY / 'design.toml', CITY / 'engineering/connected-build/span-layout.json',
                    CITY / 'engineering/connected-build/civil.json', CITY / 'engineering/connected-build/stations.json',
                    CITY / 'engineering/connected-build/logistics.json', CITY / 'engineering/depot-scope/summary.json',
                    CITY / 'engineering/coupled-programme/line-opening-milestones.json',
                    Path('lib/templates/precast-suppliers.json'), Path('lib/templates/precast-logistics.json'),
                    Path('tools/automation/civil-works-plan.py')]
    def read(path):
        return json.loads((root / path).read_text())
    cfg = read(CONFIG)
    if cfg['schema'] != 'osr-civil-works-plan/1' or cfg['construction_released']:
        raise ValueError('only unaccepted civil method planning is supported')
    if any(cfg['site_evidence'].values()):
        raise ValueError('site evidence needs reviewed import/acceptance before it can replace missing inputs')
    validate_packages(cfg['packages'])
    if not {f'CW-{i:02d}' for i in range(1, 15)} <= {p['id'] for p in cfg['packages']}:
        raise ValueError('a required complete-civil scope package is missing')
    source_paths += [Path(s) for s in cfg['method_documents']]
    design = tomllib.loads((root / CITY / 'design.toml').read_text())
    layout = read(CITY / 'engineering/connected-build/span-layout.json')
    civil = read(CITY / 'engineering/connected-build/civil.json')
    stations = read(CITY / 'engineering/connected-build/stations.json')
    logistics = read(CITY / 'engineering/connected-build/logistics.json')
    depot = read(CITY / 'engineering/depot-scope/summary.json')
    opening = read(CITY / 'engineering/coupled-programme/line-opening-milestones.json')
    totals = span_quantities(layout['spans'])
    if totals['catalogue_bays'] != layout['quantities']['catalogue_bays'] or totals['unique_proposed_supports'] != layout['quantities']['proposed_supports']:
        raise ValueError('identified quantities differ from connected layout')
    station_ids = {s['id'] for s in stations}
    if len(station_ids) != len(stations) or station_ids != {s['id'] for s in design['stations']}:
        raise ValueError('station scope does not reconcile')
    line_rows = []
    run_rows = []
    runs = defaultdict(list)
    for s in layout['spans']:
        runs[(s['line'], s['run'])].append(s)
    for (line, run), spans in sorted(runs.items()):
        ordered = sorted(spans, key=lambda s: s['start_chainage_m'])
        if any(not math.isclose(a['end_chainage_m'], b['start_chainage_m'], abs_tol=.001)
               for a, b in zip(ordered, ordered[1:])):
            raise ValueError('one continuous run has an unrepresented gap/overlap')
        q = span_quantities(spans)
        run_rows.append(dict(package=f'{line}-run-{run:04d}', line=line, run=run,
                             from_m=ordered[0]['start_chainage_m'], to_m=ordered[-1]['end_chainage_m'],
                             catalogue_bays=q['catalogue_bays'], pi20_beams=q['pi20_beams'], pi25_beams=q['pi25_beams'],
                             special_spans=q['special_spans'], unique_supports=q['unique_proposed_supports'],
                             launcher_boundary_review='required', support_release='missing', route_release='missing'))
    segment_rows = []
    for index, segment in enumerate(design['civil_segments'], 1):
        segment_rows.append(dict(id=f'civil-segment-{index:04d}', line=segment['line'], civil_class=segment['class'],
                                 from_m=segment['from_station_m'], to_m=segment['to_station_m'],
                                 length_m=round(segment['to_station_m'] - segment['from_station_m'], 3)))
    for line in design['lines']:
        key = line['name']
        quantities = span_quantities([s for s in layout['spans'] if s['line'] == key])
        lengths = {kind: round(math.fsum(s['length_m'] for s in segment_rows if s['line'] == key and s['civil_class'] == kind), 3)
                   for kind in ('at-grade', 'elevated', 'bridge')}
        connected = next(r for r in civil['lines'] if r['line'] == key)
        excluded = round(connected['station_and_transition_elevated_m'], 3)
        if not math.isclose(lengths['elevated'], quantities['running_alignment_m'] + excluded, abs_tol=.002):
            raise ValueError('running plus station/transition scope differs from elevated alignment')
        if not math.isclose(math.fsum(lengths.values()), line['length_m'], abs_tol=.002):
            raise ValueError('civil classes do not reconcile to route length')
        selected = [s for s in stations if s['line'] == key]
        counts = Counter()
        for s in selected:
            counts.update(s['layout']['quantities'])
        line_rows.append(dict(line=key, route_length_m=line['length_m'], civil_lengths_m=lengths,
                              **quantities, elevated_station_transition_m=excluded,
                              stations=len(selected), elevated_stations=sum(s['layout']['elevation'] == 'elevated' for s in selected),
                              station_equipment_and_platform_quantities=dict(counts),
                              station_structure_takeoff=None, foundation_count_and_depth_accepted=None,
                              complete_opening_date=None, complete_installed_price_usd=None))
    station_rows = []
    for s in stations:
        q = s['layout']['quantities']
        station_rows.append(dict(id=s['id'], line=s['line'], chainage_m=s['s_m'], elevation=s['layout']['elevation'],
                                 layout=s['layout']['layout'], product_variant=s['product_variant'],
                                 platforms=q['platform_count'], boarding_faces=q['boarding_face_count'], lifts=q['lift_count'],
                                 shafts=q['shaft_count'], stairs=q['staircase_count'], escalators=q['escalator_count'],
                                 method='station-construction-method', structure_design='missing', access_approval='missing'))
    planning = cfg['planning']
    launchers = len(line_rows) * planning['initial_launchers_per_line']
    pi25 = next(b for b in civil['beams'] if b['id'] == 'OSR-Pi25')
    cases = [logistics_requirements(planning, launchers, rate, pi25) for rate in planning['illustrative_bays_launcher_working_day']]
    reference_cycle = civil['conditional_scenarios']['initial-accelerated']['cycle']
    serial_hours = 2 * (reference_cycle['placement_hours_beam'] + reference_cycle['securing_hours_beam']) + reference_cycle['advance_hours_bay']
    for case in cases:
        case['connected_reference_serial_bay_cycle_hours'] = serial_hours
        case['single_shift_rate_fits_reference_serial_cycle'] = serial_hours <= case['maximum_serial_cycle_hours_required_for_rate']
        case['serial_cycle_is_unmeasured_reference_not_qualified'] = True
        days = math.ceil(totals['catalogue_bays'] / case['accepted_bays_erection_day'])
        week = planning['erection_days_week']
        case['catalogue_only_aggregate_working_day_lower_bound'] = days
        case['catalogue_only_elapsed_day_lower_bound_monday_start_no_losses'] = (days - 1) // week * 7 + (days - 1) % week + 1
        case['lower_bound_excludes'] = ['mobilisation', 'unequal fronts', 'closures and relocation', 'station structures',
                                       'special crossings', 'ground and release delays', 'holidays/weather', 'track/systems/testing/approval']
    beams = {b['id']: b for b in civil['beams']}
    accepted_concrete = math.fsum(totals[k] * beams[v]['concrete_m3'] for k, v in
                                  [('pi20_beams', 'OSR-Pi20'), ('pi25_beams', 'OSR-Pi25')])
    buffers = sorted({r['buffer_beams'] for case in logistics['conditional_cases'].values() for r in case['routes']})
    nodes = []
    for line in line_rows:
        for package in cfg['packages']:
            nodes.append(dict(id=f"{line['line']}:{package['id']}", line=line['line'],
                              package=package['id'], title=package['title'], method=package['method'],
                              accountable_role=package['accountable_role'], appointed_person=None,
                              finish_predecessors=[f"{line['line']}:{p}" for p in package['finish_predecessors']],
                              start_date=None, finish_date=None, duration_working_days=None,
                              complete_installed_price_usd=None, accepted=False,
                              evidence_required=['configuration-bound design/method', 'resource and permit release',
                                                 'measured installed quantities', 'ITP/NCR closure', 'signed handover']))
    opening_map = {'running_structures': ['CW-04', 'CW-06'], 'stations': ['CW-07'], 'specials_and_transitions': ['CW-09'],
                   'track': ['CW-08'], 'energy': ['CW-12'], 'depots': ['CW-11'], 'fleet': [], 'testing': ['CW-14'], 'approvals': ['CW-14']}
    if {row['line'] for row in opening['rows']} != {line['line'] for line in line_rows}:
        raise ValueError('complete-opening lines differ from civil scope')
    for row in opening['rows']:
        if set(row['packages']) | set(row['missing_dates']) != set(opening_map):
            raise ValueError('civil interfaces differ from the coupled complete-opening package contract')
    review = [
        dict(id='CR-01', finding='Civil classes and running/station partition reconcile', state='repository-check-passed', independent_acceptance=False),
        dict(id='CR-02', finding='25 m average is a sizing basis; individual orders retain actual variants/closures', state='repository-check-passed', independent_acceptance=False),
        dict(id='CR-03', finding='Support locations, site foundations and temporary-stage designs require release', state='open-external-evidence'),
        dict(id='CR-04', finding='No qualified supplier capacity or surveyed haulage route is entered', state='open-external-evidence'),
        dict(id='CR-05', finding='Illustrative route buffers need reconciliation with 10–15 bay policy', state='open-planning-interface',
             recorded_conditional_buffer_beams=buffers, recorded_conditional_equivalent_bays=[v / 2 for v in buffers],
             required_policy_bays=planning['beam_buffer_bays_per_front']),
        dict(id='CR-06', finding='Station/transition structures and bridge/special take-offs are not released', state='open-external-evidence'),
        dict(id='CR-07', finding='Declared depot stalls do not close physical distributed stabling for the whole fleet', state='open-external-evidence'),
        dict(id='CR-08', finding='Foundation, station, spoil and other concrete/material volumes remain design-specific', state='open-quantity-scope'),
        dict(id='CR-09', finding='Actual rates, relief, traffic/holiday/weather/maintenance calendars and permissions missing', state='open-external-evidence'),
        dict(id='CR-10', finding='Complete installed costs and milestone dates unknown; finance/opening adoption withheld', state='open-external-evidence'),
        dict(id='CR-11', finding='One-shift rate targets must fit productive hours after handover/maintenance; higher targets need measured improvements or additional authorised shifts',
             state='open-cycle-and-resource-qualification', reference_serial_cycle_hours=serial_hours,
             one_shift_productive_hours=cases[0]['available_productive_erection_hours_launcher_day'])]
    station_counts = Counter()
    for s in stations:
        station_counts.update(s['layout']['quantities'])
    summary = dict(schema='osr-civil-works-summary/1', revision_date=cfg['revision_date'],
                   status=cfg['status'], construction_released=False, planning_average_span_m=planning['average_span_m'],
                   route_length_m=round(math.fsum(r['route_length_m'] for r in line_rows), 3),
                   civil_lengths_m={k: round(math.fsum(r['civil_lengths_m'][k] for r in line_rows), 3) for k in ('at-grade', 'elevated', 'bridge')},
                   elevated_station_transition_m=round(math.fsum(r['elevated_station_transition_m'] for r in line_rows), 3),
                   running_quantities=totals, station_count=len(stations), station_quantities=dict(station_counts),
                   elevated_station_count=sum(r['elevated_stations'] for r in line_rows),
                   declared_depots=len(design['depots']), declared_depot_stalls=sum(r['fleet_stalls'] for r in design['depots']),
                   controlled_fleet_trainsets=depot['fleet_trainsets'], verified_overnight_storage_slots=None,
                   catalogue_beam_only_study_concrete_m3=round(accepted_concrete, 6), complete_project_concrete_m3=None,
                   initial_candidate_launchers=launchers, complete_installed_capital_usd=None, complete_opening_date=None,
                   method_documents=cfg['method_documents'], complete_civil_package_types=len(cfg['packages']))
    outputs = {
        'summary.json': encoded(summary), 'line-quantities.json': encoded(line_rows),
        'workfront-register.csv': csv_bytes(run_rows, list(run_rows[0])),
        'station-work-packages.csv': csv_bytes(station_rows, list(station_rows[0])),
        'civil-segments.csv': csv_bytes(segment_rows, list(segment_rows[0])),
        'resource-and-logistics.json': encoded(dict(assumptions=planning, cases=cases,
             illustrative_capacity_only=True, evidence_backed_daily_capacity=None,
             complete_beam_mass_basis='connected manufactured study, not weighed supplier member',
             foundation_station_special_and_other_material_deliveries_additional=True)),
        'package-dependencies.json': encoded(dict(nodes=nodes, opening_package_links=opening_map,
             link_is_civil_interface_not_complete_system_acceptance=True,
             repeated_local_workfaces_can_overlap_under_released_location_time_programme=True,
             finish_predecessors_are_completion_logic_not_blanket_start_gates=True,
             full_line_opening_source=(CITY / 'engineering/coupled-programme/line-opening-milestones.json').as_posix(),
             complete_opening_date=None, opening_accepted=False)),
        'review-register.json': encoded(dict(authoring_review=True, independent_acceptance=False, findings=review)),
        'technical-references.json': encoded(cfg['technical_references']),
    }
    lines = ['# Baghdad detailed civil works plan', '',
             '**Proposed planning methods; construction and complete opening remain unreleased.**', '',
             '[Master plan](../../../../../../../docs/civil/civil-works-master-plan.md) connects detailed viaduct, station, other works, logistics, programme and inspection methods.', '',
             f"The 25 m average sizing basis reconciles to {totals['catalogue_bays']:,} identified catalogue bays, {totals['special_spans']:,} unresolved specials/closures and {totals['identified_average_span_m']:.2f} m actual running-span average. Orders retain span/track IDs and actual products.", '',
             '| Line | At grade km | Elevated km | Bridge km | Catalogue bays | Special spans | Stations |',
             '|---|---:|---:|---:|---:|---:|---:|']
    for r in line_rows:
        lengths = r['civil_lengths_m']
        lines.append(f"| {r['line']} | {lengths['at-grade']/1000:.3f} | {lengths['elevated']/1000:.3f} | {lengths['bridge']/1000:.3f} | {r['catalogue_bays']} | {r['special_spans']} | {r['stations']} |")
    lines += ['', '[Line quantities](line-quantities.json) separate running structures from elevated station/transition scope. [Run register](workfront-register.csv) retains 548 disconnected access/launcher boundary packages. [Station packages](station-work-packages.csv) retain individual layouts and equipment; [civil segments](civil-segments.csv) retain every class/chainage.', '',
              '[Resources and logistics](resource-and-logistics.json) calculates required production positions, accepted/gross supply, concrete, cargo, complete transport cycles, vehicles, 10–15-bay buffers and six-day calendar lower bounds. These are illustrative requirements, not available supplier/route capacity or a completion forecast.', '',
              '[Package dependencies](package-dependencies.json) connects fourteen civil scopes per line to complete opening interfaces. Unprovided durations, installed prices and accepted dates stay unknown. Fleet, systems qualification, testing and authority approvals remain additional requirements.', '',
              '[Review register](review-register.json) preserves open support/structure, capacity, buffer, station/special, stabling, quantity, calendar and cost findings. [References](technical-references.json) are international method-development guidance; local adoption and actual site evidence are required.', '',
              'Run `python tools/automation/civil-works-plan.py`; `--check` verifies deterministic bytes and source locks on a clean checkout. [Manifest](manifest.json) records content provenance independent of the containing commit.', '']
    outputs['README.md'] = '\n'.join(lines).encode()
    sources = {p.as_posix(): digest((root / p).read_bytes()) for p in sorted(set(source_paths))}
    outputs['manifest.json'] = encoded(dict(schema='osr-civil-works-manifest/1',
                                            source_revision=digest(encoded(sources)), sources_sha256=sources,
                                            outputs_sha256={k: digest(v) for k, v in sorted(outputs.items())},
                                            construction_released=False))
    return outputs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    outputs = build()
    if args.check:
        stale = [name for name, raw in outputs.items() if not (ROOT / OUT / name).is_file() or (ROOT / OUT / name).read_bytes() != raw]
        if stale:
            raise SystemExit('stale civil works planning outputs: ' + ', '.join(stale))
        print('Civil works quantities, methods, logistics and package dependencies current; construction release open')
    else:
        (ROOT / OUT).mkdir(parents=True, exist_ok=True)
        for name, raw in outputs.items():
            (ROOT / OUT / name).write_bytes(raw)
        print(f'Published {len(outputs)} asset-bound civil planning artifacts')


if __name__ == '__main__':
    main()
