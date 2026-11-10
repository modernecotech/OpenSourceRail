import gzip
import hashlib
import json
from pathlib import Path

import pytest

from engineering.railway_project import city_recalculation
from engineering.station_rail.common import identity


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / 'docs/design-engine/v06-design-closure/samawah-city-recalculation'
CURRENT_PACKET = ROOT / 'docs/design-engine/v06-design-closure/samawah-city-recalculation-current-source'


def sha256(raw):
    return hashlib.sha256(raw).hexdigest()


def load(name):
    return json.loads((PACKET / name).read_text(encoding='utf-8'))


def test_historical_run_packet_remains_byte_verified_and_unmodified():
    manifest = load('manifest.json')
    assert manifest['schema'] == 'osr-bounded-city-adapter-run/1'
    assert manifest['packet_id'] == identity({k: v for k, v in manifest.items() if k != 'packet_id'})
    assert len(manifest['files']) == 9
    for relative, expected in manifest['files'].items():
        raw = (PACKET / relative).read_bytes()
        assert len(raw) == expected['bytes'], relative
        assert sha256(raw) == expected['sha256'], relative

    request = load('request.json')
    result = load('result.json')
    receipt = load('receipt.json')
    assert request['request_id'] == identity({k: v for k, v in request.items() if k != 'request_id'})
    assert receipt['receipt_id'] == identity({k: v for k, v in receipt.items() if k != 'receipt_id'})
    assert result['evaluation_id'] == identity({k: v for k, v in result.items() if k != 'evaluation_id'})
    assert result['evaluation_id'] == receipt['evaluation_id']
    assert request['request_id'] == receipt['request_id'] == manifest['request_id']
    assert result['body_candidate_id'] == request['body_candidate_id']
    assert result['body_evaluation_id'] == request['body_evaluation_id']
    assert receipt['native_execution'] is False and receipt['service_complete'] is False

    body = json.loads(gzip.decompress((PACKET / 'inputs/body.json.gz').read_bytes()))
    assert body['candidate_id'] == '75075df9247dfff7082a78eadc273d3a99f37e5486450621536c43b1bfa2f797'
    assert body['evaluation_id'] == 'fdac4907a6a867f0b4f27e0876a772d1b54d526ec323beb3b6d9a155e0e00b21'
    assert result['body_candidate_id'] == body['candidate_id']
    assert result['body_evaluation_id'] == body['evaluation_id']
    assert result['evaluation_id'] == identity({k: v for k, v in result.items() if k != 'evaluation_id'})


def test_samawah_result_exposes_conditional_design_and_unresolved_costs():
    result = json.loads((CURRENT_PACKET / 'result.json').read_bytes())
    assert result['candidate_id'] == '9f37c5d864a34b56009030b07659abe0cc92d5dc97c5c1872384cc7b93a6b176'
    assert len(result['lines']) == 5
    assert result['quantities']['route_m'] == pytest.approx(57873.249527151514)
    assert result['quantities']['station_markers'] == 26
    assert result['fleet_request_cases']['base']['total_trainsets'] == 59
    assert result['body_evaluation_id'] == city_recalculation.BODY_EVALUATION
    assert result['known_counted_BOM_process_subtotal_usd']['base'] == pytest.approx(
        sum(row['known_counted_BOM_process_subtotal_usd']['base'] or 0 for row in result['scope_accounts'])
    )
    assert result['cost_complete'] is False and result['service_complete'] is False
    assert result['scope_totals_usd']['rolling-stock'] == {'low': None, 'base': None, 'high': None}
    assert result['whole_life_NPV_usd'] == {'low': None, 'base': None, 'high': None}
    assert result['definition_failures'][0]['kind'] == 'overlapping-standard-platform-envelope'
    assert result['unknown_inputs']['available_force_map'] is None
    assert result['unknown_inputs']['independent_braking_map'] is None
    assert all(result[k] is False for k in ('engineering_accepted', 'physical_accepted',
        'manufacturing_release', 'operating_release', 'movement_authority'))


def test_current_source_city_packet_is_integrity_checked_and_verified():
    manifest = json.loads((CURRENT_PACKET / 'manifest.json').read_bytes())
    assert manifest['packet_id'] == identity({k: v for k, v in manifest.items() if k != 'packet_id'})
    for relative, expected in manifest['files'].items():
        raw = (CURRENT_PACKET / relative).read_bytes()
        assert len(raw) == expected['bytes'], relative
        assert sha256(raw) == expected['sha256'], relative
    request = json.loads((CURRENT_PACKET / 'request.json').read_bytes())
    receipt = json.loads((CURRENT_PACKET / 'receipt.json').read_bytes())
    result = json.loads((CURRENT_PACKET / 'result.json').read_bytes())
    assert request['body_candidate_id'] == city_recalculation.BODY
    assert request['body_evaluation_id'] == city_recalculation.BODY_EVALUATION
    assert result['evaluation_id'] == receipt['evaluation_id'] == identity(
        {k: v for k, v in result.items() if k != 'evaluation_id'})
    assert city_recalculation.verify(result)
    body = json.loads(gzip.decompress((CURRENT_PACKET / 'inputs/body.json.gz').read_bytes()))
    assert body['candidate_id'] == city_recalculation.BODY
    assert body['evaluation_id'] == city_recalculation.BODY_EVALUATION
