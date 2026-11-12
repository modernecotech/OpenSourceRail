"""Thin integration coverage; force maps and brake equations retain their tests."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path

import pytest

from engineering.station_rail import ROOT
from engineering.station_rail.common import digest, identity
from engineering.development_baseline.selection import load
from engineering.trip_dynamics import magnetic_maps

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


def test_cli_retains_exact_map_input_for_reproduction(vehicle, tmp_path):
    source = tmp_path/'map.json'
    raw = json.dumps(request(vehicle), indent=2).encode() + b'\n'
    source.write_bytes(raw)
    output = tmp_path/'packet'
    f.main(['--root', str(ROOT), '--map-request', str(source), '--output', str(output)])
    source.unlink()
    value = json.loads((output/'result.json').read_bytes())
    assert (output/'map-request.json').read_bytes() == raw
    assert value['retained_inputs']['map-request.json']['sha256'] == digest(output/'map-request.json')
    repeated = f.audit(vehicle, value['input_scenarios'], map_request=json.loads((output/'map-request.json').read_bytes()))
    assert repeated['model_force_samples'] == value['model_force_samples']
    assert '  map-request.json\n' in (output/'SHA256SUMS').read_text()


def test_loaded_source_epoch_and_requested_root_are_checked(vehicle, monkeypatch):
    original = f._LOADED_SHA.copy()
    monkeypatch.setitem(f._LOADED_SHA, f.DEPENDENCIES[0], '0'*64)
    with pytest.raises(ValueError, match='Loaded source changed'):
        f.audit(vehicle, f.controls())
    monkeypatch.setattr(f, '_LOADED_SHA', original)
    original_digest = f.digest
    monkeypatch.setattr(f, 'digest', lambda path: '0'*64 if Path(path) == ROOT/f.PRODUCER else original_digest(path))
    with pytest.raises(ValueError, match='Loaded source changed|Requested root differs'):
        f.audit(vehicle, f.controls())
