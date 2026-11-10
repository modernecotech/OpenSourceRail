"""Read-only performance/storage inventory contracts."""
from pathlib import Path
import subprocess
from types import SimpleNamespace

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
