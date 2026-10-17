"""Actual isolated revisions, common-store attempts and adverse worker outcomes."""

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys

import pytest

from engineering.generative_design.agent_execution import (
    execute_proposals,
    verify_execution,
)


@pytest.fixture
def repo(tmp_path):
    root = tmp_path / "source"
    root.mkdir()
    for argv in (
        ["init", "-q"],
        ["config", "user.name", "Test"],
        ["config", "user.email", "test@example.invalid"],
    ):
        subprocess.run(["git", "-C", str(root), *argv], check=True)
    (root / "part.py").write_text("VALUE = 1\n")
    (root / "acceptance.py").write_text("assert True\n")
    subprocess.run(["git", "-C", str(root), "add", "."], check=True)
    subprocess.run(["git", "-C", str(root), "commit", "-qm", "baseline"], check=True)
    base = subprocess.check_output(
        ["git", "-C", str(root), "rev-parse", "HEAD"], text=True
    ).strip()
    policy = dict(
        checkout_paths=["part.py", "acceptance.py"],
        allowed_paths=["part.py"],
        acceptance_files={},
        toolchain=dict(python=sys.version),
        max_log_bytes=1024 * 1024,
        commands=[[sys.executable, "-c", "import part; assert part.VALUE == 2"]],
        timeout_seconds=3,
        max_candidates=4,
    )
    proposal = dict(
        id="repair",
        role="software-developer",
        base_commit=base,
        patch="--- a/part.py\n+++ b/part.py\n@@ -1 +1 @@\n-VALUE = 1\n+VALUE = 2\n",
        allowed_paths=["part.py"],
    )
    return root, policy, proposal


def test_actual_parallel_worktrees_and_store_attempts(repo, tmp_path):
    root, policy, proposal = repo
    other = dict(proposal, id="baseline", patch="")
    out = tmp_path / "run"
    report = execute_proposals(root, out, [proposal, other], policy)
    assert verify_execution(out)["jobs"] == 2
    assert [r["status"] for r in report["results"]] == ["completed", "failed"]
    assert (root / "part.py").read_text() == "VALUE = 1\n"
    for result in report["results"]:
        assert result["experimental_adoption"] is False
        folder = out / result["artifact_directory"]
        tool = result["tools"][0]
        assert (
            tool["log_sha256"]
            == sha256((folder / tool["log"]).read_bytes()).hexdigest()
        )
        assert (folder / "evaluation.json").is_file()
    worktrees = subprocess.check_output(
        ["git", "-C", str(root), "worktree", "list", "--porcelain"], text=True
    )
    assert worktrees.count("worktree ") == 1
    first = report["results"][0]
    (out / first["artifact_directory"] / first["tools"][0]["log"]).write_text("corrupt")
    with pytest.raises(ValueError, match="corrupt attempt artifact"):
        verify_execution(out)


def test_timeout_is_inconclusive_and_retained(repo, tmp_path):
    root, policy, proposal = repo
    policy["timeout_seconds"] = 1
    policy["commands"] = [[sys.executable, "-c", "import time; time.sleep(20)"]]
    result = execute_proposals(root, tmp_path / "run", [proposal], policy)["results"][0]
    assert result["status"] == "timeout"
    assert result["tools"][0]["state"] == "inconclusive-timeout"


def test_output_limit_stops_noisy_workers_and_seals_prefix(repo, tmp_path):
    root, policy, proposal = repo
    policy["max_log_bytes"] = 1024
    policy["commands"] = [[sys.executable, "-c", "print('x' * 2000000)"]]
    out = tmp_path / "run"
    result = execute_proposals(root, out, [proposal], policy)["results"][0]
    assert result["status"] == "budget-exceeded"
    assert result["tools"][0]["state"] == "inconclusive-output-limit"
    assert verify_execution(out)["verified"]


def test_evaluation_cannot_create_untracked_acceptance_or_helpers(repo, tmp_path):
    root, policy, proposal = repo
    policy["commands"] = [
        [sys.executable, "-c", "open('conftest.py', 'w').write('pass')"]
    ]
    result = execute_proposals(root, tmp_path / "run", [proposal], policy)["results"][0]
    assert result["status"] == "failed"
    assert "mutated" in result["error"]


def test_patch_cannot_edit_acceptance_or_hide_new_files(repo, tmp_path):
    root, policy, proposal = repo
    proposal["patch"] = "--- /dev/null\n+++ b/bypass.py\n@@ -0,0 +1 @@\n+pass\n"
    result = execute_proposals(root, tmp_path / "run", [proposal], policy)["results"][0]
    assert result["status"] == "failed"
    assert "protected files" in result["error"]
    assert not result["tools"]


def test_acceptance_file_hashes_are_checked_outside_candidate(repo, tmp_path):
    root, policy, proposal = repo
    fixture = tmp_path / "independent.py"
    fixture.write_text("pass\n")
    policy["acceptance_files"] = {
        str(fixture): sha256(fixture.read_bytes()).hexdigest()
    }
    fixture.write_text("raise RuntimeError\n")
    with pytest.raises(ValueError, match="acceptance file changed"):
        execute_proposals(root, tmp_path / "run", [proposal], policy)


@pytest.mark.parametrize(
    "change",
    [
        {"concurrency": 4},
        {"max_candidates": 0},
        {"timeout_seconds": 0},
        {"allowed_paths": ["../outside"]},
    ],
)
def test_limits_and_paths_are_controller_owned(repo, tmp_path, change):
    root, policy, proposal = repo
    concurrency = change.pop("concurrency", 2)
    policy.update(change)
    with pytest.raises(ValueError):
        execute_proposals(
            root, tmp_path / "run", [proposal], policy, concurrency=concurrency
        )


def test_proposal_cannot_widen_policy_or_duplicate_identity(repo, tmp_path):
    root, policy, proposal = repo
    widened = dict(proposal, allowed_paths=["acceptance.py"])
    with pytest.raises(ValueError, match="widen"):
        execute_proposals(root, tmp_path / "run", [widened], policy)
    with pytest.raises(ValueError, match="distinct safe"):
        execute_proposals(
            root, tmp_path / "other", [proposal, deepcopy(proposal)], policy
        )
