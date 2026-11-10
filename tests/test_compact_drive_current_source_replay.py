"""The Samawah adapter's compact-drive body is a current-source campaign child."""
import gzip
import json
from pathlib import Path

from engineering.compact_drive.common import validate
from engineering.railway_project import city_recalculation
from engineering.station_rail.common import digest, identity


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / 'docs/design-engine/v06-design-closure/compact-drive-source-replay-01'


def test_bounded_source_replay_is_intact_and_selected_body_is_exact():
    manifest = json.loads((PACKET / 'manifest.json').read_bytes())
    assert isinstance(manifest.get('files_sha256'), dict)
    assert manifest.get('evaluation_id')
    for relative, expected in manifest['files_sha256'].items():
        assert digest(PACKET / relative) == expected, relative

    request = json.loads((PACKET / 'request.json').read_bytes())
    summary = json.loads((PACKET / 'summary.json').read_bytes())
    assert request['maximum_trials'] == 3
    assert request['native_jobs'] == 0
    assert summary['source_unchanged'] is True
    assert summary['evaluation_id'] == manifest['evaluation_id']

    trials = {row['config_id']: row for row in summary['trials']}
    selected = trials['compact-737-h100']
    assert selected['execution'] == 'completed'
    assert selected['candidate_id'] == city_recalculation.BODY
    assert selected['body_evaluation_id'] == city_recalculation.BODY_EVALUATION
    assert selected['known_geometry_screen_pass'] is False
    assert selected['physical_accepted'] is False
    assert selected['engineering_accepted'] is False
    assert selected['source_before'] == selected['source_after']

    body = json.loads(gzip.decompress((PACKET / 'compact-737-h100/body.json.gz').read_bytes()))
    assert validate(body) is None
    assert body['candidate_id'] == selected['candidate_id']
    assert body['evaluation_id'] == selected['body_evaluation_id']
    assert body['source_sha256'] == request['source_sha256']

    # Nearby parameter variants are distinct physical candidates and are not
    # accidentally substituted into the Samawah city calculation.
    assert trials['compact-737-h150']['candidate_id'] != selected['candidate_id']
    assert trials['compact-980-h150']['candidate_id'] != selected['candidate_id']
