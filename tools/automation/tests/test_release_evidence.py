import importlib.util
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[3]
SPEC = importlib.util.spec_from_file_location('release_evidence', ROOT / 'tools/automation/release-evidence.py')
RELEASE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RELEASE)


def rows(commit='revision', conclusion='success'):
    return [dict(workflowName=name, headSha=commit, createdAt='2026-09-17T10:00:00Z',
                 databaseId=n, status='completed', conclusion=conclusion)
            for n, name in enumerate(sorted(RELEASE.WORKFLOWS))]


def test_release_requires_all_four_workflows_on_exact_commit():
    assert len(RELEASE.successful_runs(rows(), 'revision')) == 4
    for invalid in [rows('old-revision'), rows()[:-1], rows(conclusion='failure')]:
        with pytest.raises(ValueError, match='incomplete'):
            RELEASE.successful_runs(invalid, 'revision')


def test_new_failed_or_running_workflow_cannot_be_hidden_by_old_success():
    for status, conclusion in [('completed','failure'), ('in_progress',None)]:
        retry = {**rows()[0], 'databaseId':100, 'createdAt':'2026-09-17T11:00:00Z',
                 'status':status, 'conclusion':conclusion}
        with pytest.raises(ValueError, match='incomplete'):
            RELEASE.successful_runs([*rows(),retry], 'revision')


def test_missing_local_gates_fail_without_contacting_github(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT / 'tools/automation'))
    monkeypatch.setattr(RELEASE, 'run', lambda *args: pytest.fail('GitHub must not be called by local packaging'))
    with pytest.raises(ValueError, match='incomplete'):
        with RELEASE.release_inputs('local', [], 'revision'): pytest.fail('missing gates accepted')


def test_local_release_inputs_use_validated_directories_without_network(tmp_path, monkeypatch):
    import json
    monkeypatch.syspath_prepend(str(ROOT / 'tools/automation'))
    import local_validation
    folders = []
    receipts = {}
    for name in RELEASE.WORKFLOWS:
        folder = tmp_path / name; folder.mkdir()
        receipts[name] = dict(profile=name, source=dict(commit='revision'))
        (folder / 'receipt.json').write_text(json.dumps(receipts[name]))
        folders.append(folder)
    def checked(values, commit):
        assert values == folders and commit == 'revision'
        return receipts
    monkeypatch.setattr(local_validation, 'release_receipts', checked)
    monkeypatch.setattr(RELEASE, 'run', lambda *args: pytest.fail('GitHub was contacted'))
    with RELEASE.release_inputs('local', folders, 'revision') as (checks, city, kani, city_id, kani_id):
        assert {row['profile'] for row in checks} == RELEASE.WORKFLOWS
        assert all(row['execution_location'] == 'local' for row in checks)
        assert city == tmp_path / 'example-city/city' and kani == tmp_path / 'kani'
        assert city_id is None and kani_id is None
