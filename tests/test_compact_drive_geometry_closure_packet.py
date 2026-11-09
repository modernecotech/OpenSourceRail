import hashlib
import json
from pathlib import Path

from engineering.compact_drive.common import read, sources, validate
from engineering.station_rail.common import identity


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / 'docs/design-engine/v06-design-closure/compact-drive-geometry-closure'
EXPECTED = {
    'compact-737-h100': ('75075df9247dfff7082a78eadc273d3a99f37e5486450621536c43b1bfa2f797', 5940, 3606),
    'compact-737-h150': ('5a3a6cd74fd33ab6d85e0a264afc899a5fff319e16e7fd94189637a6bfba44f3', 5790, 3498),
    'compact-980-h150': ('9af20e27cdb4f53568ad1408efd082b61ee56ecdad89a0fb4ccebd7dcb6024dc', 6060, 3474),
}


def sha256(raw):
    return hashlib.sha256(raw).hexdigest()


def load(name):
    return json.loads((PACKET / name).read_text(encoding='utf-8'))


def test_compact_drive_geometry_packet_hashes_and_source_bindings():
    manifest_raw = (PACKET / 'manifest.json').read_bytes()
    manifest = json.loads(manifest_raw)
    assert sha256(manifest_raw) == 'ef322685a479eb6f45b3dbba429d69c6ff7569841b152bd8309a9978584387ee'
    assert len(manifest['files_sha256']) == 23
    assert sum((PACKET / relative).stat().st_size for relative in manifest['files_sha256']) == 32716748
    for relative, expected in manifest['files_sha256'].items():
        assert sha256((PACKET / relative).read_bytes()) == expected, relative

    request = load('request.json')
    summary = load('summary.json')
    assert request['schema'] == 'osr-compact-drive-campaign-request/1'
    assert request['limits']['maximum_trials'] == 3
    assert request['limits']['CPU_s_each'] == 60
    assert request['limits']['memory_mib_each'] == 1024
    assert request['source_commit'] == '886ed155029a960eb62a99787c59c4bc1a842bbc'
    assert request['source_sha256'] == sources(ROOT)
    assert summary['schema'] == 'osr-compact-drive-campaign/1'
    assert summary['evaluation_id'] == identity({k: v for k, v in summary.items() if k != 'evaluation_id'})
    assert summary['source_unchanged'] is True
    assert summary['source_before'] == summary['source_after'] == request['source_sha256']
    assert summary['native_jobs'] == 0
    assert len(summary['trials']) == 3

    candidates = set()
    for trial in summary['trials']:
        config = trial['config_id']
        candidate, nominal_count, interface_count = EXPECTED[config]
        candidates.add(candidate)
        assert trial['execution'] == 'completed'
        assert trial['evaluation_id'] == identity({k: v for k, v in trial.items() if k != 'evaluation_id'})
        assert trial['candidate_id'] == candidate
        assert trial['source_unchanged'] is True
        assert trial['source_before'] == trial['source_after'] == request['source_sha256']
        assert trial['nominal_findings'] == nominal_count
        assert trial['continuous_interface_holds'] == interface_count
        assert trial['known_geometry_screen_pass'] is False
        assert all(trial[key] is False for key in (
            'engineering_accepted', 'physical_accepted', 'manufacturing_release',
            'operating_release', 'selected_reference_changed'))

        body = read(PACKET / config / 'body.json.gz')
        geometry = load(f'{config}/geometry.json')
        validate(body)
        assert body['candidate_id'] == candidate
        assert body['parent_candidate_id'] == '9f6d223074b3438a546d5b3d71cd9b970807387ef0542023bed79bef46dbdeba'
        assert body['evaluation_id'] == trial['body_evaluation_id']
        assert geometry['candidate_id'] == candidate
        assert geometry['evaluation_id'] == trial['geometry_evaluation_id']
        assert geometry['evaluation_id'] == identity({k: v for k, v in geometry.items() if k != 'evaluation_id'})
        assert geometry['known_geometry_screen_pass'] is False
        assert 'HOLD:' in geometry['geometry_screen']

    assert len(candidates) == 3
    assert all(manifest[key] is False for key in (
        'physical_accepted', 'engineering_accepted', 'manufacturing_release',
        'operating_release', 'selected_reference_changed'))
