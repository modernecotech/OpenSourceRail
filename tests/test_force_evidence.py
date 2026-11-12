"""Thin integration coverage; force maps and brake equations retain their tests."""
from copy import deepcopy
import importlib.util
from pathlib import Path

import pytest

from engineering.station_rail import ROOT
import engineering.station_rail
from engineering.station_rail.common import digest, identity
from engineering.development_baseline.selection import load
from engineering.trip_dynamics import magnetic_maps

# A sparse source worker reuses the coordinator's frozen runtime, not a second
# multi-GiB checkout. Normal full-checkout discovery follows the same import.
SOURCE = Path(__file__).resolve().parents[1]/'engineering/station_rail'
engineering.station_rail.__path__.insert(0, str(SOURCE))
from engineering.station_rail import force_evidence as f


@pytest.fixture(scope='module')
def vehicle():
    return load(ROOT)['vehicle']


def test_missing_system_data_stays_unknown_and_loadings_separate(vehicle):
    result = f.audit(vehicle, f.controls())
    assert result['engineering_screen'] == 'held'
    assert result['actual_installed_force_available_N'] is None
    assert result['available_data_domain'] is None
    assert result['accounted_mass']['installed_tare_kg_per_car'] is None
    normal, crowd = result['scenarios']
    assert normal['people_per_car'] == 46 and crowd['people_per_car'] == 160
    assert crowd['requirement']['inputs']['mass_kg_per_car'] - normal['requirement']['inputs']['mass_kg_per_car'] == 114*75
    for row in result['scenarios']:
        assert row['actual_installed_force_available_N'] is None
        assert row['requirement']['peak_launch_force_N_per_car'] > 0
        assert row['missing_evidence']['installed_force_speed_current_envelope']
        assert not row['independent_stopping_requirement']['brake_supplier_curve_and_WSP_verified']
    assert not result['physical_journey_completed']


def test_tampered_and_resealed_mixed_candidate_refused(vehicle):
    bad = deepcopy(vehicle)
    bad['mass']['accounted_tare_kg_per_car'] += 1
    with pytest.raises(ValueError, match='seal'):
        f.audit(bad, f.controls())
    bad = deepcopy(vehicle)
    bad['candidate_id'] = 'a'*64
    bad.pop('evaluation_id')
    bad['evaluation_id'] = identity(bad)
    with pytest.raises(ValueError, match='candidate'):
        f.audit(bad, f.controls())
    bad = deepcopy(vehicle)
    bad['mass']['accounted_tare_kg_per_car'] += 1
    bad.pop('evaluation_id')
    bad['evaluation_id'] = identity(bad)
    with pytest.raises(ValueError, match='reference evaluation'):
        f.audit(bad, f.controls())


def request(vehicle):
    path = ROOT/'engineering/trip_dynamics/tests/test_magnetic_maps.py'
    spec = importlib.util.spec_from_file_location('retained_map_fixture', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    value = module.fixture()
    value.pop('map_id')
    value['identity']['candidate_id'] = vehicle['candidate_id']
    for row in value['rows']:
        row['identity']['candidate_id'] = vehicle['candidate_id']
    name = 'engineering/trip_dynamics/tests/test_magnetic_maps.py'
    value['source_sha256'] = {name: digest(ROOT/name)}
    value = magnetic_maps.seal_force_map(value)
    return dict(map=value, expected_identity=deepcopy(value['identity']), queries=[module.query()])


def test_valid_synthetic_map_never_becomes_installed_force(vehicle):
    result = f.audit(vehicle, f.controls(), map_request=request(vehicle))
    assert result['model_force_samples'][0]['force_N'] == pytest.approx([10., 0., 9050.])
    assert result['force_map_metadata']['evidence_kind'] == 'synthetic-test'
    assert result['actual_installed_force_available_N'] is None
    assert not result['model_samples_establish_installed_force']
    assert result['engineering_screen'] == 'held'


def test_map_identity_tamper_domain_and_source_rejected(vehicle):
    r = request(vehicle)
    r['expected_identity']['candidate_id'] = 'e'*64
    with pytest.raises(ValueError, match='identities'):
        f.audit(vehicle, f.controls(), map_request=r)
    r = request(vehicle)
    r['map']['rows'][0]['force_N'][0] += 1
    with pytest.raises(magnetic_maps.MapError):
        f.audit(vehicle, f.controls(), map_request=r)
    r = request(vehicle)
    r['queries'][0]['v_m_s'] = 1.
    with pytest.raises(magnetic_maps.MapDomainError):
        f.audit(vehicle, f.controls(), map_request=r)
    r = request(vehicle)
    r['map'].pop('map_id')
    r['map']['source_sha256'] = {'engineering/station_rail/operations.py': 'f'*64}
    r['map'] = magnetic_maps.seal_force_map(r['map'])
    with pytest.raises(ValueError, match='source differs'):
        f.audit(vehicle, f.controls(), map_request=r)


def test_failed_stopping_and_coast_controls_preserved(vehicle):
    scenario = f.controls()[0]
    scenario['distance_m'] = 100000.
    scenario['stopping'].update(adhesion_coefficient=.03, downhill_grade_fraction=.04)
    result = f.audit(vehicle, [scenario])['scenarios'][0]
    assert not result['requirement']['reachable']
    assert result['requirement']['reason'] == 'coast_stops_before_receiving_zone'
    assert result['independent_stopping_requirement']['stopping_distance_m'] is None
    assert result['independent_stopping_requirement']['necessary_stop_screen'] == 'fail'


@pytest.mark.parametrize('value', [float('nan'), float('inf'), True, -1.])
def test_invalid_stopping_controls_refused(vehicle, value):
    scenario = f.controls()[0]
    scenario['stopping']['reaction_s'] = value
    with pytest.raises(ValueError):
        f.audit(vehicle, [scenario])


def test_bound_mass_cannot_be_overridden(vehicle):
    scenario = f.controls()[0]
    scenario['profile']['mass_kg_per_car'] = 1.
    with pytest.raises(ValueError, match='candidate-bound'):
        f.audit(vehicle, [scenario])
