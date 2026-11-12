import hashlib
import json
from pathlib import Path

import pytest

from engineering.v06_design_closure import release_gate


ROOT = Path(__file__).resolve().parents[1]


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def test_open_engineering_gates_remain_visible_after_software_publication():
    report = release_gate.inspect(ROOT)
    assert report['required_gate_count'] == 7
    assert report['closed_gate_count'] == 0
    assert report['release_ready'] is False
    assert report['engineering_design_complete'] is False
    assert report['controls_software_publication'] is False
    assert report['published_software_release'] == 'v0.6.1'
    assert {item['id'] for item in report['open_gates']} == {
        'installed-vehicle', 'controlled-research-documents', 'mapped-corridor',
        'native-gis-return-path', 'candidate-business-lifecycle',
        'all-city-outline-reconciliation', 'unified-workbench',
    }
    with pytest.raises(ValueError, match='design closure remains incomplete'):
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


def test_false_publication_control_requires_explicit_supersession(tmp_path):
    root, campaign_path, status_path = _closed_fixture(tmp_path)
    path = root / campaign_path
    raw = path.read_bytes().replace(b'release_unpublished_until_required_work_closed = true',
                                  b'release_unpublished_until_required_work_closed = false')
    path.write_bytes(raw)
    status = json.loads((root / status_path).read_text())
    status['campaign_sha256'] = digest(raw)
    (root / status_path).write_text(json.dumps(status))
    with pytest.raises(ValueError, match='Superseded software-publication control'):
        release_gate.inspect(root, campaign_path=campaign_path, status_path=status_path)


def _retention_fixture(tmp_path):
    import subprocess
    root, campaign, status_path = _closed_fixture(tmp_path)
    def git(*args):
        return subprocess.check_output(['git', '-C', str(root), *args]).decode().strip()
    git('init', '-q')
    git('add', '.')
    git('-c', 'user.name=Synthetic test', '-c', 'user.email=test@example.invalid',
        'commit', '-qm', 'Synthetic historical source fixture')
    revision = git('rev-parse', 'HEAD')
    (root / 'docs/result.txt').write_text('new implementation, no new execution\n')
    return root, campaign, status_path, revision


def test_retention_preserves_historical_hashes_states_and_is_idempotent(tmp_path):
    from engineering.v06_design_closure.retain_sources import retain
    root, campaign, status_path, revision = _retention_fixture(tmp_path)
    before = json.loads((root / status_path).read_text())
    preview = retain(root, revision, status_path=status_path)
    assert preview['changed'] and not preview['written']
    assert not (root / 'docs/archives').exists()
    result = retain(root, revision, status_path=status_path, write=True)
    assert len(result['inventory']) == 2
    assert len(result['retained']) == 2
    after = json.loads((root / status_path).read_text())
    for name, gate in before['gates'].items():
        assert {k: v for k, v in gate.items() if k != 'evidence'} == {
            k: v for k, v in after['gates'][name].items() if k != 'evidence'}
        assert gate['evidence'][0]['sha256'] == after['gates'][name]['evidence'][0]['sha256']
    assert after['release_flags'] == before['release_flags']
    assert after['release_ready'] == before['release_ready']
    release_gate.inspect(root, campaign_path=campaign, status_path=status_path)
    assert retain(root, revision, status_path=status_path, write=True)['changed'] is False
    with pytest.raises(ValueError, match='different source revision'):
        retain(root, 'a' * 40, status_path=status_path, write=True)


def test_retention_authentication_refuses_before_writes(tmp_path):
    from engineering.v06_design_closure.retain_sources import retain
    root, _, status_path, revision = _retention_fixture(tmp_path)
    path = root / status_path
    status = json.loads(path.read_text())
    status['gates']['alpha']['evidence'][0]['sha256'] = 'a' * 64
    path.write_text(json.dumps(status))
    with pytest.raises(ValueError, match='not authenticated'):
        retain(root, revision, status_path=status_path, write=True)
    assert not (root / 'docs/archives').exists()


@pytest.mark.parametrize('tamper', ['bytes', 'revision', 'original_path'])
def test_retained_source_tamper_or_origin_change_is_rejected(tmp_path, tamper):
    from engineering.v06_design_closure.retain_sources import retain
    root, campaign, status_path, revision = _retention_fixture(tmp_path)
    retain(root, revision, status_path=status_path, write=True)
    path = root / status_path
    status = json.loads(path.read_text())
    row = status['gates']['alpha']['evidence'][0]
    if tamper == 'bytes':
        (root / row['path']).write_text('tampered')
    else:
        row['source_revision' if tamper == 'revision' else 'original_path'] = (
            'a' * 40 if tamper == 'revision' else 'other/source.py')
        path.write_text(json.dumps(status))
    with pytest.raises(ValueError, match='hash mismatch|identity mismatch'):
        release_gate.inspect(root, campaign_path=campaign, status_path=status_path)


def test_current_retention_keeps_all_original_engineering_findings():
    status = json.loads((ROOT / release_gate.STATUS).read_text())
    manifest = json.loads((ROOT / status['source_retention']['path']).read_text())
    original = json.loads((ROOT / manifest['original_ledger']['path']).read_text())
    assert len(manifest['inventory']) == 199
    assert len(manifest['retained_sources']) == 5
    assert manifest['source_revision'] == '5cfe89488a64549b37d4a7fd3ea9e3d3a8923aea'
    model_rows = [row for row in manifest['retained_sources']
                  if row['original_path'] == 'engineering/vehicle_installation/model.py']
    assert {row['gate'] for row in model_rows} == {
        'installed-vehicle', 'controlled-research-documents'}
    assert {row['sha256'] for row in model_rows} == {
        'a68c6a14f3094c037413021305d929099762cc095cbd36349216b3f909d12340'}
    for name, record in original['gates'].items():
        assert {k: v for k, v in record.items() if k != 'evidence'} == {
            k: v for k, v in status['gates'][name].items() if k != 'evidence'}
    for key in ('release_flags', 'release_ready', 'release_review', 'record_note'):
        assert status[key] == original[key]


@pytest.mark.parametrize('kind', ['file-symlink', 'parent-symlink', 'oversized'])
def test_retention_status_cannot_escape_root_or_exceed_read_budget(tmp_path, kind):
    from engineering.v06_design_closure.retain_sources import retain, MAX_FILE
    root, _, status_path, revision = _retention_fixture(tmp_path / 'repo')
    status = root / status_path
    outside = tmp_path / 'outside.json'
    outside.write_bytes(status.read_bytes())
    original = outside.read_bytes()
    if kind == 'file-symlink':
        status.unlink()
        status.symlink_to(outside)
    elif kind == 'parent-symlink':
        linked = root / 'linked'
        linked.symlink_to(tmp_path, target_is_directory=True)
        status_path = 'linked/outside.json'
    else:
        with status.open('wb') as stream:
            stream.truncate(MAX_FILE + 1)
    with pytest.raises(ValueError, match='ordinary|bounded|bound'):
        retain(root, revision, status_path=status_path, write=True)
    assert outside.read_bytes() == original
    assert not (root / 'docs/archives').exists()


def test_retention_uses_original_git_objects_not_replacement_refs(tmp_path):
    import subprocess
    from engineering.v06_design_closure.retain_sources import retain
    root, _, status_path, revision = _retention_fixture(tmp_path)
    expected = json.loads((root / status_path).read_bytes())['gates']['alpha']['evidence'][0]['sha256']
    subprocess.run(['git', '-C', str(root), 'add', '.'], check=True)
    subprocess.run(['git', '-C', str(root), '-c', 'user.name=Synthetic test', '-c',
        'user.email=test@example.invalid', 'commit', '-qm', 'Synthetic replacement'], check=True)
    replacement = subprocess.check_output(['git', '-C', str(root), 'rev-parse', 'HEAD'], text=True).strip()
    subprocess.run(['git', '-C', str(root), 'replace', revision, replacement], check=True)
    result = retain(root, revision, status_path=status_path, write=True)
    assert result['retained'][0]['sha256'] == expected
    assert digest((root / result['retained'][0]['path']).read_bytes()) == expected
