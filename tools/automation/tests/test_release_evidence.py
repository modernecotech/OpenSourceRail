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


def test_release_requires_all_three_workflows_on_exact_commit():
    assert len(RELEASE.successful_runs(rows(), 'revision')) == 3
    for invalid in [rows('old-revision'), rows()[:-1], rows(conclusion='failure')]:
        with pytest.raises(ValueError, match='incomplete'):
            RELEASE.successful_runs(invalid, 'revision')


def test_new_failed_or_running_workflow_cannot_be_hidden_by_old_success():
    for status, conclusion in [('completed','failure'), ('in_progress',None)]:
        retry = {**rows()[0], 'databaseId':100, 'createdAt':'2026-09-17T11:00:00Z',
                 'status':status, 'conclusion':conclusion}
        with pytest.raises(ValueError, match='incomplete'):
            RELEASE.successful_runs([*rows(),retry], 'revision')
