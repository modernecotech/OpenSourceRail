import hashlib
import json
from pathlib import Path
import gzip
import subprocess

import pytest

from engineering.railway_project import city_acceleration_sensitivity as study
from engineering.station_rail.common import identity


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / 'docs/design-engine/v06-design-closure/samawah-acceleration-sensitivity'
ORIGINAL = ROOT / 'docs/design-engine/v06-design-closure/samawah-city-recalculation'


def sha256(raw):
    return hashlib.sha256(raw).hexdigest()


def load(packet, name):
    return json.loads((packet / name).read_text(encoding='utf-8'))


def historical_source_sha256(commit, paths):
    recorded = {}
    for relative in paths:
        raw = subprocess.run(['git', 'show', f'{commit}:{relative}'], cwd=ROOT,
            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout
        recorded[relative] = sha256(raw)
    return recorded


def test_acceleration_packet_bytes_and_sealed_identities():
    manifest_raw = (PACKET / 'manifest.json').read_bytes()
    manifest = json.loads(manifest_raw)
    assert manifest['schema'] == 'osr-bounded-city-acceleration-run/1'
    assert manifest['packet_id'] == identity({k: v for k, v in manifest.items() if k != 'packet_id'})
    assert sha256(manifest_raw) == 'eccd7048f1452d6ca2c1a75dd05a186c8f239e17f92815448a430fd056ead96d'
    assert manifest['packet_id'] == '19b3fa755578cb982f0100e589b4500dc1b0fec753cfba37cf43b3d70d684985'
    assert manifest['source_commit'] == '615f50fd6a6a73db32a0dffa4682a86d83920224'
    for relative, expected in manifest['files'].items():
        raw = (PACKET / relative).read_bytes()
        assert len(raw) == expected['bytes'], relative
        assert sha256(raw) == expected['sha256'], relative

    request = load(PACKET, 'request.json')
    result = load(PACKET, 'result.json')
    receipt = load(PACKET, 'receipt.json')
    assert request['request_id'] == identity({k: v for k, v in request.items() if k != 'request_id'})
    assert receipt['receipt_id'] == identity({k: v for k, v in receipt.items() if k != 'receipt_id'})
    assert result['evaluation_id'] == identity({k: v for k, v in result.items() if k != 'evaluation_id'})
    assert manifest['source_commit'] == request['source_commit']
    assert result['source_sha256'] == historical_source_sha256(
        request['source_commit'], result['source_sha256'])
    assert request['request_id'] == receipt['request_id'] == manifest['request_id']
    assert result['evaluation_id'] == receipt['evaluation_id'] == '7c45c16f5d147935f58643aad22b7092d00244eae9738a174172067af6f255e8'
    assert receipt['retained_original_unchanged'] is True
    assert receipt['native_execution'] is False
    body_raw = (PACKET / 'inputs/body.json.gz').read_bytes()
    body = json.loads(gzip.decompress(body_raw))
    city = load(PACKET, 'inputs/city.json')
    assert request['retained_file_sha256']['inputs/body.json.gz'] == sha256(body_raw)
    assert request['retained_file_sha256']['inputs/city.json'] == sha256(
        (PACKET / 'inputs/city.json').read_bytes())
    assert (result['body_candidate_id'], result['body_evaluation_id']) == (
        body['candidate_id'], body['evaluation_id'])
    assert result['source_city_input_id'] == city['input_id'] == request['source_city_input_id']
    assert all(result['source_sha256'].get(name) == digest
               for name, digest in city['source_sha256'].items())
    assert study.verify(result)


def test_control_packet_reference_and_acceleration_sensitivity_are_not_promoted():
    original_manifest_raw = (ORIGINAL / 'manifest.json').read_bytes()
    original_manifest = json.loads(original_manifest_raw)
    result = load(PACKET, 'result.json')
    assert sha256(original_manifest_raw) == study.REFERENCE_MANIFEST_SHA256
    assert original_manifest['packet_id'] == study.REFERENCE_PACKET
    assert result['retained_control_reference']['packet_id'] == original_manifest['packet_id']
    assert result['retained_control_reference']['manifest_sha256'] == sha256(original_manifest_raw)
    assert result['cases'][0]['source_outline_evaluation_id'] == study.REFERENCE_EVALUATION
    assert result['acceleration_hypotheses_m_s2'] == [0.4, 0.6, 0.8]
    assert [sum(row['scenarios']['base']['total_trainsets'] for row in case['kinematic_lines'])
            for case in result['cases']] == [59, 59, 56]
    assert all(result[key] is False for key in study.FLAGS)

    normal_base = [next(row for row in case['inertia_only_lower_bound_components']
                        if row['mass_scenario'] == 'normal-base') for case in result['cases']]
    assert [row['translational_inertia_force_N'] for row in normal_base] == pytest.approx(
        [60127.008833166925, 90190.51324975038, 120254.01766633385])
    assert [row['mechanical_power_at_declared_speed_cap_W'] for row in normal_base] == pytest.approx(
        [1202540.1766633384, 1803810.2649950075, 2405080.353326677])
    assert all(row['installed_mass_verified'] is False for row in normal_base)
    assert result['inertia_component_basis']['excluded_effects'] == list(study.EXCLUDED)
    assert all(case['definition_failures'][0]['kind'] == 'overlapping-standard-platform-envelope'
               for case in result['cases'])


def test_historical_sensitivity_verifier_binds_cases_to_embedded_body():
    result = load(PACKET, 'result.json')
    assert study.verify(result)
    changed = json.loads(json.dumps(result))
    changed['body_candidate_id'] = 'a'*64
    changed['evaluation_id'] = identity({k: v for k, v in changed.items() if k != 'evaluation_id'})
    with pytest.raises(ValueError, match='body identities'):
        study.verify(changed)
