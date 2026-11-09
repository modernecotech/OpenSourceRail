import gzip
import hashlib
import json
from pathlib import Path

from engineering.station_rail.common import identity


ROOT = Path(__file__).resolve().parents[1]
CLOSURE = ROOT / 'docs/design-engine/v06-design-closure'


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def test_sealed_all_city_packet_and_erratum_are_consistent():
    packet = CLOSURE / 'all-city-baseline-audit'
    manifest = read_json(packet / 'manifest.json')
    assert manifest['source_commit'] == 'ebeb3b769a9b416180c64124debc1f23317ca277'
    assert manifest['packet_id'] == '5ea07b72c7b1cb7c90e4b7e4ef9754f2e6fad5beae76e383fccd0e4175d2cf48'
    for relative, expected in manifest['files'].items():
        raw = (packet / relative).read_bytes()
        assert len(raw) == expected['bytes'], relative
        assert sha256(raw) == expected['sha256'], relative

    summary = read_json(packet / 'audit-summary.json')
    expected_gates = {
        'installed-vehicle', 'controlled-research-documents', 'mapped-corridor',
        'native-gis-return-path', 'candidate-business-lifecycle',
        'all-city-outline-reconciliation', 'unified-workbench',
    }
    assert set(summary['gate_review']['committed_required_work_ids']) == expected_gates
    assert set(summary['gate_review']['working_required_work_ids']) == expected_gates
    errata = (CLOSURE / 'all-city-audit-errata.md').read_text(encoding='utf-8')
    assert 'only the original' in (packet / 'README.md').read_text(encoding='utf-8')
    assert 'seven' in errata and 'all-city-outline-reconciliation' in errata


def test_compact_corridor_package_is_hash_and_identity_consistent():
    packet = CLOSURE / 'compact-drive-corridor'
    request_bytes = (packet / 'request.json').read_bytes()
    request = json.loads(request_bytes)
    result_bytes = (packet / 'result.json').read_bytes()
    result = json.loads(result_bytes)
    manifest = read_json(packet / 'manifest.json')
    overlay_bytes = (packet / 'source-overlay-manifest.json').read_bytes()
    overlay = json.loads(overlay_bytes)

    assert request['request_id'] == identity({k: v for k, v in request.items() if k != 'request_id'})
    assert result['evaluation_id'] == identity({k: v for k, v in result.items() if k != 'evaluation_id'})
    assert manifest['manifest_id'] == identity({k: v for k, v in manifest.items() if k != 'manifest_id'})
    assert overlay['manifest_id'] == identity({k: v for k, v in overlay.items() if k != 'manifest_id'})
    assert sha256(request_bytes) == manifest['request_sha256']
    assert sha256(result_bytes) == manifest['result_sha256']
    assert request['request_id'] == manifest['request_id'] == result['request_id']
    assert result['evaluation_id'] == manifest['evaluation_id']
    assert overlay['manifest_id'] == manifest['source_overlay_manifest_id']
    assert sha256(overlay_bytes) == manifest['source_overlay_manifest_sha256']

    for relative, expected in manifest['artifact_sha256'].items():
        assert sha256((packet / relative).read_bytes()) == expected, relative
    body_bytes = (packet / 'body.json.gz').read_bytes()
    assert manifest['candidate_body_sha256'] == sha256(body_bytes)
    body = json.loads(gzip.decompress(body_bytes))
    assert body['candidate_id'] == manifest['body_candidate_id'] == result['candidate_identity']['body_candidate_id']
    assert body['evaluation_id'] == manifest['body_evaluation_id'] == result['candidate_identity']['body_evaluation_id']

    assert len(overlay['files_sha256']) == 103
    for source_path, expected in overlay['files_sha256'].items():
        assert result['source_sha256'][f'git-overlay/{source_path}'] == expected
    assert len(result['route_records']) == 2
    assert all(row['geometry_trial_count'] == 0 for row in result['route_records'])
    assert all(row['status'] == 'blocked-before-catalogue-route' for row in result['route_records'])
    assert result['stage_records'] == []
    assert result['body_definition_complete'] is True
    assert result['installed_mass_complete'] is False
    assert result['service']['service_complete'] is False
    assert result['costs']['complete'] is False
    assert result['costs']['scope_costs_USD'] is None
    assert result['selected_reference_changed'] is False
    for key in ('engineering_accepted', 'physical_accepted', 'manufacturing_release',
                'operating_release', 'movement_authority'):
        assert result[key] is False
