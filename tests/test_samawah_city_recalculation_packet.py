import gzip
import hashlib
import json
from pathlib import Path

import pytest

from engineering.railway_project import city_recalculation
from engineering.station_rail.common import identity


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / 'docs/design-engine/v06-design-closure/samawah-city-recalculation'


def sha256(raw):
    return hashlib.sha256(raw).hexdigest()


def load(name):
    return json.loads((PACKET / name).read_text(encoding='utf-8'))


def test_run_packet_hashes_and_candidate_evaluations_are_reproducible():
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
    assert body['candidate_id'] == city_recalculation.BODY
    assert body['evaluation_id'] == city_recalculation.BODY_EVALUATION
    assert city_recalculation.verify(result)


def test_samawah_result_exposes_conditional_design_and_unresolved_costs():
    result = load('result.json')
    assert result['candidate_id'] == '9f37c5d864a34b56009030b07659abe0cc92d5dc97c5c1872384cc7b93a6b176'
    assert len(result['lines']) == 5
    assert result['quantities']['route_m'] == pytest.approx(57873.249527151514)
    assert result['quantities']['station_markers'] == 26
    assert result['fleet_request_cases']['base']['total_trainsets'] == 59
    assert result['known_counted_BOM_process_subtotal_usd']['base'] == pytest.approx(88678590.74607049)
    assert result['cost_complete'] is False and result['service_complete'] is False
    assert result['scope_totals_usd']['rolling-stock'] == {'low': None, 'base': None, 'high': None}
    assert result['whole_life_NPV_usd'] == {'low': None, 'base': None, 'high': None}
    assert result['definition_failures'][0]['kind'] == 'overlapping-standard-platform-envelope'
    assert result['unknown_inputs']['available_force_map'] is None
    assert result['unknown_inputs']['independent_braking_map'] is None
    assert all(result[k] is False for k in ('engineering_accepted', 'physical_accepted',
        'manufacturing_release', 'operating_release', 'movement_authority'))
