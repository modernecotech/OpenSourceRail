import hashlib
import json
from pathlib import Path

import pytest

from engineering.v06_design_closure import release_gate


ROOT = Path(__file__).resolve().parents[1]


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def test_current_v06_release_is_withheld_by_all_required_open_gates():
    report = release_gate.inspect(ROOT)
    assert report['required_gate_count'] == 7
    assert report['closed_gate_count'] == 0
    assert report['release_ready'] is False
    assert {item['id'] for item in report['open_gates']} == {
        'installed-vehicle', 'controlled-research-documents', 'mapped-corridor',
        'native-gis-return-path', 'candidate-business-lifecycle',
        'all-city-outline-reconciliation', 'unified-workbench',
    }
    with pytest.raises(ValueError, match='remains withheld'):
        release_gate.require_ready(ROOT)


def _closed_fixture(tmp_path):
    root = tmp_path
    root.mkdir(parents=True, exist_ok=True)
    (root / 'campaigns').mkdir()
    (root / 'docs').mkdir()
    campaign_path = 'campaigns/gates.toml'
    campaign_bytes = (
        'schema = "osr-design-integration-closure-program/1"\n'
        'release_unpublished_until_required_work_closed = true\n'
        '[[work]]\nid = "alpha"\nrequired = true\n'
        '[[work]]\nid = "beta"\nrequired = true\n'
    ).encode()
    (root / campaign_path).write_bytes(campaign_bytes)
    payload = b'reproduced result\n'
    review = b'independent review\n'
    final_review = b'release review\n'
    (root / 'docs/result.txt').write_bytes(payload)
    (root / 'docs/review.txt').write_bytes(review)
    (root / 'docs/release-review.txt').write_bytes(final_review)
    file_row = lambda path, data: {'path': path, 'sha256': digest(data)}
    status = {
        'schema': release_gate.STATUS_SCHEMA,
        'campaign_path': campaign_path,
        'campaign_sha256': digest(campaign_bytes),
        'release_ready': True,
        'gates': {
            name: {
                'state': 'closed',
                'evidence': [file_row('docs/result.txt', payload)],
                'independent_review': {
                    'state': 'accepted', 'reviewer': 'independent-reviewer',
                    **file_row('docs/review.txt', review),
                },
            }
            for name in ('alpha', 'beta')
        },
        'release_review': {
            'state': 'accepted', 'reviewer': 'release-reviewer',
            **file_row('docs/release-review.txt', final_review),
        },
        'release_flags': {key: False for key in release_gate.RELEASE_FLAGS},
    }
    status_path = 'docs/status.json'
    (root / status_path).write_text(json.dumps(status), encoding='utf-8')
    return root, campaign_path, status_path


def test_closed_digital_gates_require_source_hashes_and_independent_reviews(tmp_path):
    root, campaign_path, status_path = _closed_fixture(tmp_path)
    report = release_gate.inspect(root, campaign_path=campaign_path, status_path=status_path)
    assert report['release_ready'] is True


def test_changed_evidence_or_physical_release_claim_fails_closed(tmp_path):
    root, campaign_path, status_path = _closed_fixture(tmp_path)
    (root / 'docs/result.txt').write_text('changed evidence', encoding='utf-8')
    with pytest.raises(ValueError, match='content hash mismatch'):
        release_gate.inspect(root, campaign_path=campaign_path, status_path=status_path)

    root, campaign_path, status_path = _closed_fixture(tmp_path / 'second')
    path = root / status_path
    status = json.loads(path.read_text(encoding='utf-8'))
    status['release_flags']['physical_accepted'] = True
    path.write_text(json.dumps(status), encoding='utf-8')
    with pytest.raises(ValueError, match='cannot assert physical'):
        release_gate.inspect(root, campaign_path=campaign_path, status_path=status_path)
