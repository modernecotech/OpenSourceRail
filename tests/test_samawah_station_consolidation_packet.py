import gzip
import hashlib
import json
from pathlib import Path

from engineering.station_rail.common import identity


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / 'docs/design-engine/v06-design-closure/samawah-station-consolidation'


def load(name):
    return json.loads((PACKET / name).read_bytes())


def test_station_consolidation_packet_is_sealed_and_candidate_bound():
    manifest = load('manifest.json')
    assert manifest['schema'] == 'osr-private-samawah-station-consolidation-run/1'
    assert manifest['packet_id'] == identity({k: v for k, v in manifest.items() if k != 'packet_id'})
    assert manifest['source_commit'] == '90d07f045bfc4d8860c04a984ba84a867ed997e9'
    assert manifest['packet_id'] == '856609798cbe717713a6833f96484081d23dc183c79246aadf05fa6be6267bb6'
    for relative, expected in manifest['files'].items():
        raw = (PACKET / relative).read_bytes()
        assert len(raw) == expected['bytes'], relative
        assert hashlib.sha256(raw).hexdigest() == expected['sha256'], relative

    request, receipt = load('request.json'), load('receipt.json')
    result, comparison = load('result.json'), load('comparison.json')
    derivation = load('derivation.json')
    assert request['request_id'] == identity({k: v for k, v in request.items() if k != 'request_id'})
    assert receipt['receipt_id'] == identity({k: v for k, v in receipt.items() if k != 'receipt_id'})
    assert result['evaluation_id'] == identity({k: v for k, v in result.items() if k != 'evaluation_id'})
    assert comparison['evaluation_id'] == identity({k: v for k, v in comparison.items() if k != 'evaluation_id'})
    derivation_fields = ('schema', 'source_city_input_id', 'line_id', 'source_stop_ids',
        'source_stops', 'midpoint_chainage_m', 'midpoint_longitude_latitude', 'method')
    assert derivation['derivation_id'] == identity({k: derivation[k] for k in derivation_fields})
    assert request['request_id'] == receipt['request_id'] == manifest['request_id']
    assert result['evaluation_id'] == comparison['midpoint_scenario']['evaluation_id']
    assert comparison['derivation_id'] == derivation['derivation_id']
    assert comparison['control_reproduced'] is True
    assert comparison['source_polyline_unchanged'] is True
    assert comparison['all_other_lines_unchanged'] is True
    assert comparison['body_and_policy_unchanged'] is True
    assert comparison['gate_closed'] is False
    assert manifest['gate_closed'] is False and manifest['physical_accepted'] is False
    assert receipt['native_execution'] is False and receipt['physical_accepted'] is False
    assert comparison['baseline']['station_markers'] == 26
    assert comparison['midpoint_scenario']['station_markers'] == 25
    assert comparison['midpoint_scenario']['boarding_faces'] == 50
    assert comparison['cost_complete'] is False and comparison['service_complete'] is False

    body = json.loads(gzip.decompress((PACKET / 'inputs/body.json.gz').read_bytes()))
    assert body['candidate_id'] == result['body_candidate_id']
    assert body['evaluation_id'] == result['body_evaluation_id']
    assert result['candidate_id'] == 'f3e6532304d2a5f56d44e77ab32b523f4ab3a20850bed633741b68eb33861ea2'
    assert result['quantities']['station_markers'] == 25
    assert result['definition_failures'] == []
    assert result['scope_totals_usd']['rolling-stock'] == {'low': None, 'base': None, 'high': None}
    assert result['whole_life_NPV_usd'] == {'low': None, 'base': None, 'high': None}

    city = load('derived-city.json')
    assert city['input_id'] == result['source_city_input_id']
    assert len(city['lines']) == 5
    interchange = next(row for row in city['interchanges'] if row['id'] == 'interchange-001')
    assert interchange['platforms'].count(derivation['new_station_id']) == 1
    assert 'line-1-0485-0464-s009300' not in interchange['platforms']
    assert 'line-1-0487-0466-s009380' not in interchange['platforms']
