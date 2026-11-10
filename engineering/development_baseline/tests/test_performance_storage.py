"""Read-only performance/storage inventory contracts."""
from pathlib import Path
import subprocess
from types import SimpleNamespace
from datetime import datetime, timezone
import os

from engineering import performance


def test_worktree_parser_retains_branch_detached_locked_and_prunable_state():
    raw = (
        "worktree /work/main\nHEAD abc123\nbranch refs/heads/main\n\n"
        "worktree /work/research branch\nHEAD def456\ndetached\nlocked held by review\n\n"
        "worktree /work/old\nHEAD 987654\nprunable gitdir file points to missing path\n"
    )
    rows = performance._parse_worktrees(raw)
    assert rows == [
        dict(path="/work/main", head="abc123", branch="main", detached=False,
             locked=False, prunable=False),
        dict(path="/work/research branch", head="def456", branch=None, detached=True,
             locked=True, prunable=False),
        dict(path="/work/old", head="987654", branch=None, detached=False,
             locked=False, prunable=True),
    ]


def test_storage_report_inventories_without_changing_worktree_files(tmp_path, monkeypatch):
    root = tmp_path / "repo"
    linked = tmp_path / "linked worktree"
    (root / "build" / "sample").mkdir(parents=True)
    linked.mkdir()
    (root / "build" / "sample" / "run.json").write_text("source-bound evidence")
    (linked / "README.md").write_text("local checkout")
    original_run = subprocess.run

    def fake_run(command, **kwargs):
        if command[:4] == ["git", "-C", str(root), "worktree"]:
            stdout = (f"worktree {root}\nHEAD abc123\nbranch refs/heads/main\n\n"
                      f"worktree {linked}\nHEAD def456\nbranch refs/heads/feature\n")
            return subprocess.CompletedProcess(command, 0, stdout, "")
        if "status" in command:
            dirty = " M README.md\n" if str(linked) in command else ""
            return subprocess.CompletedProcess(command, 0, dirty.encode(), b"")
        return original_run(command, **kwargs)

    monkeypatch.setattr(performance.subprocess, "run", fake_run)
    monkeypatch.setattr(performance.shutil, "disk_usage",
                        lambda path: SimpleNamespace(total=100, used=20, free=80))
    before = {(path, path.read_bytes()) for path in
              (root / "build" / "sample" / "run.json", linked / "README.md")}
    report = performance.storage_report(root, minimum_free_gib=1)
    after = {(path, path.read_bytes()) for path in
             (root / "build" / "sample" / "run.json", linked / "README.md")}

    assert report["filesystem"]["reserve_status"] == "below-reserve"
    assert report["registered_worktree_count"] == 2
    linked_row = next(row for row in report["registered_worktrees"] if row["path"] == str(linked))
    assert linked_row["branch"] == "feature"
    assert linked_row["status"] == "dirty"
    assert linked_row["dirty_file_count"] == 1
    assert report["measurement"]["deletion_performed"] is False
    assert before == after


def test_disk_admission_holds_below_reserve_and_disclaims_quota(tmp_path, monkeypatch):
    monkeypatch.setattr(performance.shutil, "disk_usage",
                        lambda path: SimpleNamespace(total=100 * performance.GIB,
                                                     used=81 * performance.GIB,
                                                     free=19 * performance.GIB))
    report = performance.disk_admission(tmp_path)
    assert report["execution"] == "held"
    assert report["admitted"] is False
    assert report["filesystem_free_bytes"] == 19 * performance.GIB
    assert "quota is not enforced" in report["enforcement"]


def test_bytecode_cleanup_is_dry_run_by_default_and_excludes_evidence_trees(tmp_path):
    now = datetime(2026, 11, 10, 12, tzinfo=timezone.utc)
    old = tmp_path / "engineering" / "pkg" / "__pycache__"
    fresh = tmp_path / "engineering" / "recent" / "__pycache__"
    excluded = tmp_path / "build" / "run" / "__pycache__"
    for cache in (old, fresh, excluded):
        cache.mkdir(parents=True)
    old_file = old / "old.cpython-313.pyc"
    fresh_file = fresh / "fresh.cpython-313.pyc"
    excluded_file = excluded / "evidence.pyc"
    old_file.write_bytes(b"old-bytecode")
    fresh_file.write_bytes(b"new-bytecode")
    excluded_file.write_bytes(b"keep-build-cache")
    os.utime(old_file, (now.timestamp() - 8 * 86400,) * 2)
    os.utime(fresh_file, (now.timestamp() - 2 * 86400,) * 2)
    os.utime(excluded_file, (now.timestamp() - 30 * 86400,) * 2)

    dry_run = performance.cleanup_bytecode(tmp_path, minimum_age_days=7, now=now)
    assert dry_run["mode"] == "dry-run"
    assert dry_run["eligible_directory_count"] == 1
    assert dry_run["mutation_performed"] is False
    assert old_file.exists() and fresh_file.exists() and excluded_file.exists()
    by_path = {row["path"]: row for row in dry_run["candidates"]}
    assert by_path["engineering/pkg/__pycache__"]["status"] == "eligible"
    assert by_path["engineering/recent/__pycache__"]["status"] == "held"
    assert "build/run/__pycache__" not in by_path

    applied = performance.cleanup_bytecode(tmp_path, minimum_age_days=7,
                                            apply=True, now=now)
    assert applied["removed_directory_count"] == 1
    assert applied["mutation_performed"] is True
    assert not old.exists()
    assert fresh_file.exists() and excluded_file.exists()


def test_cleanup_cli_defaults_to_dry_run(tmp_path, capsys):
    assert performance.main(["cleanup"], root=tmp_path) == 0
    report = __import__("json").loads(capsys.readouterr().out)
    assert report["mode"] == "dry-run"
    assert report["mutation_performed"] is False
