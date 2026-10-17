"""Independent acceptance checks for offline controls, physics and procurement."""
from copy import deepcopy
import hashlib
import json
import math
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / 'design/component-catalogue/src')]
from engineering.generative_design.twin_software_factory import (
    GUARDS, build, fault_suite, origin_screen, replay_precharge,
)


@pytest.fixture(scope='module')
def packet():
    return build()


def _system(packet, identifier):
    return next(row for row in packet['systems'] if row['id'] == identifier)


def test_packet_is_deterministic_serializable_and_source_bound(packet):
    assert packet['schema'] == 'osr-domain-design-twin/1'
    assert json.dumps(packet, sort_keys=True, allow_nan=False) == json.dumps(build(), sort_keys=True, allow_nan=False)
    for name, expected in packet['source_files'].items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == expected
    assert not packet['telemetry_contract']['installed_asset_connection']
    assert packet['telemetry_contract']['calibration_state'] == 'unmeasured'


def test_unique_complete_part_tree_and_open_evidence_gates(packet):
    ids = []
    for system in packet['systems']:
        for variant in system['variants']:
            local = {p['id'] for p in variant['parts']}
            assert len(local) == len(variant['parts'])
            ids.extend(local)
            assert all(p['parent_id'] is None or p['parent_id'] in local for p in variant['parts'])
            assert all(set(('specifications', 'material', 'manufacturing', 'inspection')) <= p.keys() for p in variant['parts'])
            assert not variant['production_released']
            assert variant['selection_state'] != 'study-admissible'
    assert len(ids) == len(set(ids))
    assert any(r['id'] == 'SF-subcomponent-closure' for r in packet['open_requests'])
    assert any(r['id'] == 'SF-factory-production' and not r['throughput_established'] for r in packet['open_requests'])


@pytest.mark.parametrize('guard', GUARDS)
def test_each_critical_guard_fails_closed_and_latches(guard):
    frame = deepcopy(fault_suite()[0]['frames'][0])
    frame['signals'][guard] = False
    healthy = deepcopy(fault_suite()[0]['frames'][0])
    healthy.update(sequence=2, observed_s=3.6, received_s=3.62)
    result = replay_precharge([frame, healthy])
    assert all(not row['request_main_close'] for row in result['rows'])
    assert result['final_state'] == 'LOCKOUT'
    assert not result['physical_control_implemented']


@pytest.mark.parametrize('key,value', [('sequence', True), ('observed_s', float('nan')), ('received_s', float('inf'))])
def test_invalid_transport_fields_cannot_close(key, value):
    frame = deepcopy(fault_suite()[0]['frames'][0]); frame[key] = value
    assert not replay_precharge([frame])['rows'][0]['request_main_close']


def test_safe_policy_passes_exact_same_adverse_suite_weak_candidates_fail(packet):
    variants = {row['id']: row for row in _system(packet, 'software-precharge-control')['variants']}
    assert variants['control-guarded']['objectives']['failed_fault_cases'] == 0
    assert variants['control-guarded']['selection_state'] == 'conditional'
    for name in ('control-ratio-only', 'control-interlocks-only'):
        assert variants[name]['objectives']['failed_fault_cases'] > 0
        assert variants[name]['selection_state'] == 'rejected'
    counts = {len(e['results']) for e in packet['experiments'] if e['id'].startswith('fault-replay-')}
    assert len(counts) == 1 and counts.pop() >= 15


def test_rc_closed_form_and_joule_balance_have_independent_reference(packet):
    result = next(e['result'] for e in packet['experiments'] if e['id'] == 'rc-150')
    assert result['nominal_ready_time_s'] == pytest.approx(-150 * .006 * math.log(.05))
    assert result['required_resistor_pulse_energy_j'] == pytest.approx(.5 * .006 * 1.1 * 900**2 * 1.5)
    for row in result['samples']:
        assert row['source_energy_j'] == pytest.approx(row['capacitor_energy_j'] + row['resistor_energy_j'], abs=1e-7)
    variants = {row['id']: row for row in _system(packet, 'electrical-precharge')['variants']}
    assert variants['precharge-600-ohm']['selection_state'] == 'rejected'
    assert variants['precharge-150-ohm']['selection_state'] == 'conditional'


def test_thermal_one_unit_out_retains_failure_and_energy_conversion(packet):
    variants = {row['id']: row for row in _system(packet, 'thermal-control')['variants']}
    assert variants['hvac-3-modules']['selection_state'] == 'rejected'
    assert variants['hvac-4-modules']['selection_state'] == 'conditional'
    result = next(e['result'] for e in packet['experiments'] if e['id'] == 'one-unit-out-4')
    # Setpoint maintained: Q=9500 +500*(45-26)=19000 W;
    # half-hour / COP2.5 = 3.8 kWh independent of controller reporting.
    assert result['electrical_energy_kwh'] == pytest.approx(19000 / 2.5 * 1800 / 3600000)
    assert result['maximum_energy_residual_j'] < 1e-6
    assert not result['physical_validation']


def test_sustained_air_flow_applies_fad_units_duty_leak_and_reserve(packet):
    variants = _system(packet, 'factory/cmm-air-system')['variants']
    assert [v['selection_state'] for v in variants] == ['rejected', 'rejected', 'conditional']
    assert variants[0]['parameters']['required_l_min'] == pytest.approx(100 * 1.25 / .8)
    assert variants[1]['objectives']['continuous_average_capacity_l_min'] == pytest.approx(2 * 126 * .5)
    assert variants[2]['objectives']['continuous_average_capacity_l_min'] == pytest.approx(3 * 126 * .5)


def test_imported_machine_never_receives_british_manufacture_credit(packet):
    equipment = _system(packet, 'factory/prosaw-bomar-510')['variants'][0]
    assert equipment['parameters']['origin']['preference'] == 'imported-uk-supply-only'
    assert equipment['parameters']['origin']['exact_offered_origin'] is None
    assert any(c['id'] == 'offered-unit-origin' and c['state'] == 'unknown' for c in equipment['checks'])
    assert not equipment['parameters']['origin']['supplier_contacted']
    uk = _system(packet, 'factory/mazak-cv5-500')['variants'][0]
    assert uk['parameters']['origin']['preference'] == 'published-uk-manufacture-priority-offer-unconfirmed'
    assert uk['selection_state'] == 'conditional'
    assert origin_screen({'origin': 'UK integration of overseas machine'})['preference'] == 'uk-integration-or-assembly-origin-open'


def test_fresh_envelope_cannot_freeze_elapsed_time_or_reset_precharge_cycle():
    first = deepcopy(fault_suite()[0]['frames'][0])
    frozen = deepcopy(first); frozen.update(sequence=2, observed_s=10000., received_s=10000.02)
    result = replay_precharge([first, frozen])
    assert result['rows'][0]['request_main_close']
    assert not result['rows'][1]['request_main_close']
    assert result['final_state'] == 'LOCKOUT'
    assert 'elapsed-clock-inconsistency' in result['rows'][1]['faults']
    # A nonzero epoch works, but it belongs to the controller invocation.
    shifted = deepcopy(first); shifted.update(observed_s=103.5, received_s=103.52)
    assert replay_precharge([shifted], cycle_start_s=100.)['rows'][0]['request_main_close']
    assert not replay_precharge([shifted], cycle_start_s=101.)['rows'][0]['request_main_close']


def test_receipt_clock_cannot_move_backwards_despite_fresh_ordered_observations():
    first = deepcopy(fault_suite()[0]['frames'][0]); first['received_s'] = 3.58
    second = deepcopy(first); second.update(sequence=2, observed_s=3.52, received_s=3.55)
    second['signals']['elapsed_s'] = 3.52
    result = replay_precharge([first, second])
    assert result['rows'][0]['request_main_close']
    assert not result['rows'][1]['request_main_close']
    assert 'receipt-clock-backwards' in result['rows'][1]['faults']
    second['received_s'] = 3.6
    assert replay_precharge([first, second])['rows'][1]['request_main_close']
