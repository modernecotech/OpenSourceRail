"""Readiness cannot inherit ideal-force motion or credit rejected currents."""
from copy import deepcopy
import gzip
import json
import math
from pathlib import Path
import tomllib

import pytest

from engineering.maglev_research import dynamics_readiness as d

ROOT = Path(__file__).resolve().parents[3]


@pytest.fixture(scope='module')
def evidence():
    value = json.loads(gzip.decompress((ROOT/d.PACKET/'study.json.gz').read_bytes()))
    assumptions = tomllib.loads((ROOT/'engineering/ferrite_maglev/full-dynamics.toml').read_text())
    return value, assumptions


def test_actual_current_attempts_do_not_earn_executed_motion(evidence):
    value, assumptions = evidence
    result = d.audit_runs(value, assumptions)
    assert result['terminal_counts'] == {
        'hold-initial-support-current-or-field-capacity': 12,
        'hold-initial-curve-or-gap-geometry': 2,
    }
    assert result['meaningful_motion_cases'] == 0
    assert result['continued_post_fault_cases'] == 0
    assert not result['full_trip_executed']
    row = result['rows'][0]
    assert row['executed_peak_current_a'] == 0
    assert row['attempted_initial_inverse']['peak_current_a'] == 270
    assert row['attempted_initial_inverse']['current_limit_ratio'] == 2.25
    assert row['attempted_initial_inverse']['invalid_modules'] == 144
    assert not row['attempted_initial_inverse']['admissible']


@pytest.mark.parametrize('change', ['legacy', 'mixed-candidate', 'promoted', 'out-of-limit-equilibrium', 'fake-trip', 'missing-cases', 'fake-post-fault'])
def test_readiness_refuses_unearned_evidence(evidence, change):
    value, assumptions = deepcopy(evidence)
    if change == 'legacy':
        value['schema'] = 'osr-moving-train/1'
    elif change == 'mixed-candidate':
        value['runs'][0]['configuration_sha256'] = 'f'*64
    elif change == 'promoted':
        value['runs'][0]['study_pass'] = True
    elif change == 'out-of-limit-equilibrium':
        value['runs'][0]['screens']['initial_equilibrium'] = True
    elif change == 'fake-trip':
        value['full_line_attempt']['full_trip_executed'] = True
    elif change == 'missing-cases':
        value['runs'].pop()
    elif change == 'fake-post-fault':
        value['runs'][1]['post_fault_steps'] = 1
    with pytest.raises(ValueError):
        d.audit_runs(value, assumptions)


@pytest.mark.parametrize('bad', [float('nan'), float('inf'), True])
def test_attempted_current_must_be_finite_numeric(evidence, bad):
    value, assumptions = deepcopy(evidence)
    value['runs'][0]['initial_inverse']['current_a'][0][0] = bad
    with pytest.raises(ValueError, match='attempted current'):
        d.audit_runs(value, assumptions)


@pytest.mark.parametrize('change', ['post-current-only', 'fault-tick-only', 'initial-hold-frame',
                                  'zero-microsteps', 'nonboolean-screen', 'nonboolean-duration'])
def test_audit_rejects_invented_execution_and_nonboolean_screens(evidence, change):
    value, assumptions = deepcopy(evidence)
    run = value['runs'][1]
    if change == 'post-current-only':
        run['executed_current_frames'] = 1
        run['executed_current_microsteps'] = 20
        run['post_fault_current_frames'] = 1
    elif change == 'fault-tick-only':
        run['fault_tick'] = 0
    elif change == 'initial-hold-frame':
        run['executed_current_frames'] = 1
        run['executed_current_microsteps'] = 20
    elif change == 'zero-microsteps':
        assumptions['mechanical_step_s'] = 1e-13
    elif change == 'nonboolean-screen':
        run['screens']['initial_equilibrium'] = 0
    elif change == 'nonboolean-duration':
        run['executed_s'] = False
    with pytest.raises(ValueError):
        d.audit_runs(value, assumptions)


def test_recentring_is_minimax_and_still_cannot_fit_terminal_or_urban_curve():
    positions = [-5.5+i for i in range(12)]
    for radius in (50., 300.):
        result = d.curve_fit(positions, radius, .008, .002, .03)
        assert not result['original_geometry_screen_pass']
        assert not result['recentered_geometry_screen_pass']
        assert result['optimal_maximum_mismatch_m'] < result['original_maximum_mismatch_m']
        half_span = result['continuous_recentered_rigid_span_limit_m']/2
        assert (radius-math.sqrt(radius*radius-half_span**2))/2 == pytest.approx(.006)
        offsets = [radius-math.sqrt(radius*radius-x*x) for x in positions]
        target = result['optimal_lateral_translation_m']
        optimum = result['optimal_maximum_mismatch_m']
        assert max(abs(y-target) for y in offsets) == pytest.approx(optimum)
        for change in (-.001, .001):
            assert max(abs(y-target-change) for y in offsets) > optimum
    assert not result['adopted']


def test_exact_curve_radius_bounds_match_analytical_fixed_centre():
    positions = [-5.5+i for i in range(12)]
    fixed = d.minimum_radius(positions, .008, .002, .03, recentered=False)
    shifted = d.minimum_radius(positions, .008, .002, .03, recentered=True)
    assert fixed == pytest.approx((5.5**2+.006**2)/(.012))
    assert 1200 < shifted < 1300
    assert shifted < fixed
    for recentered, radius in ((False,fixed), (True,shifted)):
        field = 'recentered_geometry_screen_pass' if recentered else 'original_geometry_screen_pass'
        assert d.curve_fit(positions, radius*1.00001, .008, .002, .03)[field]
        assert not d.curve_fit(positions, radius*.99999, .008, .002, .03)[field]


@pytest.mark.parametrize('positions,radius,gap', [([-1,2],100,[.008,.002,.03]), ([-1,1],.5,[.008,.002,.03]), ([-1,1],100,[.001,.002,.03])])
def test_invalid_geometry_does_not_earn_clearance(positions, radius, gap):
    with pytest.raises(ValueError):
        d.curve_fit(positions,radius,*gap)


def test_retained_payload_tamper_is_rejected(tmp_path):
    packet = tmp_path/d.PACKET
    packet.mkdir(parents=True)
    (packet/'study.json.gz').write_bytes(b'changed')
    manifest = dict(schema='osr-continued-full-dynamics/1', files_sha256={'study.json.gz':'0'*64},
                    source_sha256={}, raw_bytes=1, design_complete=False, physical_validation=False,
                    manufacturing_release=False, physical_release=False)
    (packet/'manifest.json').write_text(json.dumps(manifest))
    with pytest.raises(ValueError,match='payload differs'):
        d.retained(tmp_path)


def test_retained_source_drift_is_rejected(tmp_path):
    packet = tmp_path/d.PACKET
    packet.mkdir(parents=True)
    (packet/'study.json.gz').write_bytes(b'payload')
    (tmp_path/'solver.py').write_text('changed source')
    from hashlib import sha256
    manifest = dict(schema='osr-continued-full-dynamics/1',
                    files_sha256={'study.json.gz':sha256(b'payload').hexdigest()},
                    source_sha256={'solver.py':'0'*64}, raw_bytes=1,
                    design_complete=False, physical_validation=False,
                    manufacturing_release=False, physical_release=False)
    (packet/'manifest.json').write_text(json.dumps(manifest))
    with pytest.raises(ValueError,match='source differs'):
        d.retained(tmp_path)


def test_correct_subset_of_sources_cannot_remove_original_dependencies(tmp_path):
    from hashlib import sha256
    packet = tmp_path/d.PACKET
    packet.mkdir(parents=True)
    raw = b'{}'
    payload = gzip.compress(raw)
    (packet/'study.json.gz').write_bytes(payload)
    manifest = dict(schema='osr-continued-full-dynamics/1',
                    files_sha256={'study.json.gz':sha256(payload).hexdigest()},
                    source_sha256={}, raw_bytes=len(raw), design_complete=False,
                    physical_validation=False, manufacturing_release=False, physical_release=False)
    (packet/'manifest.json').write_text(json.dumps(manifest))
    with pytest.raises(ValueError,match='complete original dynamics source inventory'):
        d.retained(tmp_path)
