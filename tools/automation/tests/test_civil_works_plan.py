"""Civil planning checks cover disconnected scope and unqualified resource claims."""
import importlib.util
import json
import tomllib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location('civil_works_plan', ROOT / 'tools/automation/civil-works-plan.py')
plan = importlib.util.module_from_spec(spec)
spec.loader.exec_module(plan)


def span(key, start, end, run=1, variant='OSR-Pi25'):
    special = variant is None
    return dict(id=key, line='line-a', run=run, start_chainage_m=start, end_chainage_m=end, length_m=end-start,
                classification='special-design-required' if special else 'catalogue-planning-span',
                beam_variant=variant, quantity=None if special else 2,
                component_ids=[] if special else [key+'-track-1', key+'-track-2'],
                pier_a=f'support-{start}', pier_b=f'support-{end}')


def test_disconnected_supports_and_specials_do_not_become_rounded_orders():
    rows = [span('one', 0, 25), span('closure', 25, 29.7, variant=None), span('two', 100, 125, run=2)]
    q = plan.span_quantities(rows)
    assert q['running_alignment_m'] == 54.7
    assert q['catalogue_beams'] == 4
    assert q['special_spans'] == 1
    assert q['unique_proposed_supports'] == 5  # Shared in one run; separate endpoints in the other.
    assert q['disconnected_runs'] == 2


def test_wrong_length_or_special_order_cannot_issue_catalogue_quantity():
    with pytest.raises(ValueError, match='complete identified'):
        plan.span_quantities([span('short', 0, 23.3)])
    row = span('special', 0, 23.3, variant=None)
    row['component_ids'] = ['fake-order']
    with pytest.raises(ValueError, match='unresolved special'):
        plan.span_quantities([row])


def test_rejected_casts_complete_return_cycle_and_buffer_are_in_capacity_requirement():
    cfg = json.loads((ROOT / plan.CONFIG).read_text())['planning']
    row = plan.logistics_requirements(cfg, 18, 1, dict(manufactured_study_mass_kg=85507.241, concrete_m3=32.34055))
    assert row['accepted_beams_erection_day'] == 36
    assert row['gross_cast_beams_erection_day'] == 40
    assert row['one_beam_mould_positions_peak_daily'] == 80
    assert row['required_vehicles_daily'] == 36  # 12h window cannot fit two complete 8h cycles.
    assert row['buffer_accepted_beams'] == [360, 540]
    assert row['available_productive_erection_hours_launcher_day'] == 5.4
    assert row['maximum_serial_cycle_hours_required_for_rate'] == 5.4
    assert row['actual_available_supplier_beams_day'] is None
    assert row['achieved_daily_rate'] is None
    cfg['haulage_window_hours'] = 4
    impossible = plan.logistics_requirements(cfg, 18, 1, dict(manufactured_study_mass_kg=85507.241, concrete_m3=32.34055))
    assert impossible['required_vehicles_daily'] is None
    assert impossible['route_cycle_fits_window'] is False


def test_impossible_working_clock_and_negative_return_leg_are_rejected():
    cfg = json.loads((ROOT / plan.CONFIG).read_text())['planning']
    cfg['production_calendar_hours_day'] = 48
    with pytest.raises(ValueError, match='24 hours'):
        plan.logistics_requirements(cfg, 18, 1, dict(manufactured_study_mass_kg=85000, concrete_m3=32))
    cfg['production_calendar_hours_day'] = 24
    cfg['complete_vehicle_cycle_breakdown_hours']['return'] = -2
    with pytest.raises(ValueError, match='cycle leg'):
        plan.logistics_requirements(cfg, 18, 1, dict(manufactured_study_mass_kg=85000, concrete_m3=32))


def test_dependency_cycle_and_authoring_acceptance_are_rejected():
    packages = [dict(id='A', finish_predecessors=['B'], accountable_role='designer', method='method',
                     duration_working_days=None, installed_price_usd=None, accepted_release_record=None),
                dict(id='B', finish_predecessors=['A'], accountable_role='designer', method='method',
                     duration_working_days=None, installed_price_usd=None, accepted_release_record=None)]
    with pytest.raises(ValueError, match='cyclic'):
        plan.validate_packages(packages)
    packages[0]['finish_predecessors'] = []
    plan.validate_packages(packages)
    packages[0]['accepted_release_record'] = 'authoring-is-not-release'
    with pytest.raises(ValueError, match='reviewed import'):
        plan.validate_packages(packages)


def test_current_scope_reconciles_all_civil_classes_and_keeps_external_gates_open():
    outputs = plan.build()
    summary = json.loads(outputs['summary.json'])
    assert summary['route_length_m'] == pytest.approx(sum(summary['civil_lengths_m'].values()))
    assert summary['civil_lengths_m']['elevated'] == pytest.approx(
        summary['running_quantities']['running_alignment_m'] + summary['elevated_station_transition_m'])
    assert summary['complete_project_concrete_m3'] is None
    assert summary['complete_opening_date'] is None
    assert summary['construction_released'] is False
    dependencies = json.loads(outputs['package-dependencies.json'])
    design=tomllib.loads((ROOT/plan.CITY/'design.toml').read_text())
    assert len(dependencies['nodes']) == len(design['lines']) * 14
    assert {node['line'] for node in dependencies['nodes']} == {line['name'] for line in design['lines']}
    assert summary['initial_candidate_launchers'] == 18
    assert summary['candidate_workfronts'] == 2 * len(design['lines'])
    assert all(node['finish_date'] is None and node['accepted'] is False for node in dependencies['nodes'])
    opening = json.loads((ROOT / plan.CITY / 'engineering/coupled-programme/line-opening-milestones.json').read_text())
    for row in opening['rows']:
        assert set(dependencies['opening_package_links']) == set(row['packages']) | set(row['missing_dates'])
    resource = json.loads(outputs['resource-and-logistics.json'])
    assert [row['single_shift_rate_fits_reference_serial_cycle'] for row in resource['cases']] == [True, False, False]
