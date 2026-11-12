"""Read-only performance/storage inventory contracts."""
import json
from pathlib import Path
import subprocess
from types import SimpleNamespace
from datetime import datetime, timezone
import hashlib
import os
import struct
import sys

import pytest

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
    review_ready = tmp_path / "merged clean worktree"
    ignored = tmp_path / "merged worktree with ignored data"
    (root / "build" / "sample").mkdir(parents=True)
    linked.mkdir()
    review_ready.mkdir()
    ignored.mkdir()
    (root / "build" / "sample" / "run.json").write_text("source-bound evidence")
    (linked / "README.md").write_text("local checkout")
    (review_ready / "README.md").write_text("merged source checkout")
    (ignored / "README.md").write_text("merged checkout with local evidence")
    original_run = subprocess.run

    def fake_run(command, **kwargs):
        if command[:4] == ["git", "-C", str(root), "worktree"]:
            stdout = (f"worktree {root}\nHEAD abc123\nbranch refs/heads/main\n\n"
                      f"worktree {linked}\nHEAD def456\nbranch refs/heads/feature\n\n"
                      f"worktree {review_ready}\nHEAD fedcba\nbranch refs/heads/merged\n\n"
                      f"worktree {ignored}\nHEAD 987654\nbranch refs/heads/merged-evidence\n")
            return subprocess.CompletedProcess(command, 0, stdout, "")
        if "merge-base" in command:
            return subprocess.CompletedProcess(command, 0, b"", b"")
        if "status" in command:
            dirty = (" M README.md\n!! build/\n" if str(linked) in command else
                     "!! build/\n" if str(ignored) in command else "")
            return subprocess.CompletedProcess(command, 0, dirty.encode(), b"")
        return original_run(command, **kwargs)

    monkeypatch.setattr(performance.subprocess, "run", fake_run)
    monkeypatch.setattr(performance.shutil, "disk_usage",
                        lambda path: SimpleNamespace(total=100, used=20, free=80))
    before = {(path, path.read_bytes()) for path in
              (root / "build" / "sample" / "run.json", linked / "README.md",
               review_ready / "README.md", ignored / "README.md")}
    report = performance.storage_report(root, minimum_free_gib=1)
    after = {(path, path.read_bytes()) for path in
             (root / "build" / "sample" / "run.json", linked / "README.md",
              review_ready / "README.md", ignored / "README.md")}

    assert report["filesystem"]["reserve_status"] == "below-reserve"
    assert report["registered_worktree_count"] == 4
    linked_row = next(row for row in report["registered_worktrees"] if row["path"] == str(linked))
    assert linked_row["branch"] == "feature"
    assert linked_row["status"] == "dirty"
    assert linked_row["dirty_file_count"] == 1
    assert linked_row["ignored_paths"] == ["build/"]
    review = report["cleanup_review"]
    assert review["deletion_performed"] is False
    by_path = {row["path"]: row for row in review["items"]}
    assert by_path[str(review_ready)]["disposition"] == "review-ready"
    assert by_path[str(review_ready)]["requires_user_approval"] is True
    assert by_path[str(ignored)]["disposition"] == "held-ignored-data-review"
    assert by_path[str(ignored)]["ignored_paths"] == ["build/"]
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


def test_disk_hold_record_preserves_action_resource_and_acceptance_dispositions(
        tmp_path, monkeypatch):
    admission = dict(schema="osr-performance-disk-admission/1", root=str(tmp_path),
        filesystem_free_bytes=1, minimum_free_reserve_bytes=20*performance.GIB,
        minimum_free_reserve_gib=20.0, admitted=False, execution="held",
        reason="below reserve", enforcement="shared reserve only")
    monkeypatch.setattr(performance, "disk_admission", lambda root: admission)
    record = performance.disk_hold_record(tmp_path, "example-run",
        {"physical_accepted": False, "selected_reference_changed": False})
    assert record == dict(schema="osr-performance-disk-admission/1",
        execution="held", requested_action="example-run", resource_admission=admission,
        physical_accepted=False, selected_reference_changed=False)


def test_disk_hold_record_returns_none_when_admitted(tmp_path, monkeypatch):
    monkeypatch.setattr(performance, "disk_admission",
        lambda root: dict(admitted=True, execution="ready"))
    assert performance.disk_hold_record(tmp_path, "example-run", {}) is None


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


def _git_pack_cleanup_fixture(root):
    root.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", "--quiet", "--object-format=sha1", str(root)],
                   check=True)
    return root / ".git" / "objects" / "pack"


def _pack_checksum_consistent_empty():
    header = b"PACK" + struct.pack(">II", 2, 0)
    return header + hashlib.sha1(header).digest()


def test_git_temp_pack_cleanup_dry_run_holds_recent_and_checksum_consistent(
        tmp_path, monkeypatch):
    now = datetime(2026, 11, 11, 12, tzinfo=timezone.utc)
    pack_dir = _git_pack_cleanup_fixture(tmp_path / "repo")
    old_invalid = pack_dir / "tmp_pack_old"
    old_invalid.write_bytes(b"PACK" + struct.pack(">II", 2, 1) + b"x" * 64)
    old_valid_checksum = pack_dir / "tmp_pack_valid"
    old_valid_checksum.write_bytes(_pack_checksum_consistent_empty())
    recent_invalid = pack_dir / "tmp_pack_recent"
    recent_invalid.write_bytes(b"incomplete")
    old_time = now.timestamp() - 48 * 3600
    for path in (old_invalid, old_valid_checksum):
        os.utime(path, (old_time, old_time))
    monkeypatch.setattr(performance, "_active_git_processes", lambda: [])

    report = performance.cleanup_git_temp_packs(
        tmp_path / "repo", minimum_age_hours=24, now=now,
    )

    assert report["mode"] == "dry-run"
    assert report["mutation_performed"] is False
    rows = {Path(row["path"]).name: row for row in report["candidates"]}
    assert rows["tmp_pack_old"]["status"] == "eligible"
    assert rows["tmp_pack_old"]["validation"] == "checksum-mismatch"
    assert rows["tmp_pack_valid"]["status"] == "held"
    assert rows["tmp_pack_valid"]["validation"] == "checksum-consistent"
    assert rows["tmp_pack_recent"]["status"] == "held"
    assert old_invalid.exists() and old_valid_checksum.exists() and recent_invalid.exists()


def test_git_temp_pack_cleanup_apply_removes_only_stale_invalid_fragments(
        tmp_path, monkeypatch):
    now = datetime(2026, 11, 11, 12, tzinfo=timezone.utc)
    root = tmp_path / "repo"
    pack_dir = _git_pack_cleanup_fixture(root)
    invalid = pack_dir / "tmp_pack_interrupted"
    invalid.write_bytes(b"PACK" + struct.pack(">II", 2, 2) + b"partial" * 20)
    empty = pack_dir / "tmp_pack_empty"
    empty.touch()
    complete_checksum = pack_dir / "tmp_pack_complete"
    complete_checksum.write_bytes(_pack_checksum_consistent_empty())
    old_time = now.timestamp() - 48 * 3600
    for path in (invalid, empty, complete_checksum):
        os.utime(path, (old_time, old_time))
    monkeypatch.setattr(performance, "_active_git_processes", lambda: [])

    report = performance.cleanup_git_temp_packs(
        root, minimum_age_hours=24, apply=True, now=now,
    )

    rows = {Path(row["path"]).name: row for row in report["candidates"]}
    assert report["removed_count"] == 2
    assert report["mutation_performed"] is True
    assert rows["tmp_pack_interrupted"]["status"] == "removed"
    assert rows["tmp_pack_empty"]["status"] == "removed"
    assert rows["tmp_pack_complete"]["status"] == "held"
    assert not invalid.exists() and not empty.exists() and complete_checksum.exists()


def test_git_temp_pack_cleanup_holds_all_candidates_while_git_is_active(
        tmp_path, monkeypatch):
    now = datetime(2026, 11, 11, 12, tzinfo=timezone.utc)
    root = tmp_path / "repo"
    pack_dir = _git_pack_cleanup_fixture(root)
    candidate = pack_dir / "tmp_pack_old"
    candidate.write_bytes(b"truncated")
    os.utime(candidate, (now.timestamp() - 48 * 3600,) * 2)
    monkeypatch.setattr(performance, "_active_git_processes",
                        lambda: ["123:git-fetch"])

    report = performance.cleanup_git_temp_packs(
        root, minimum_age_hours=24, apply=True, now=now,
    )

    assert report["removed_count"] == 0
    assert report["mutation_performed"] is False
    assert report["candidates"][0]["status"] == "held"
    assert candidate.exists()


def test_git_temp_pack_cleanup_cli_defaults_to_dry_run(tmp_path, monkeypatch, capsys):
    _git_pack_cleanup_fixture(tmp_path)
    monkeypatch.setattr(performance, "_active_git_processes", lambda: [])

    assert performance.main(["cleanup-git-packs"], root=tmp_path) == 0
    report = __import__("json").loads(capsys.readouterr().out)

    assert report["schema"] == "osr-performance-git-temp-pack-cleanup/1"
    assert report["mode"] == "dry-run"
    assert report["mutation_performed"] is False


def test_perf_measure_records_process_metrics_and_workspace_delta(tmp_path, capsys):
    import json
    workspace = tmp_path / "job-workspace"
    report_path = tmp_path / "measurement.json"
    output = workspace / "artifact.bin"
    code = "import pathlib,sys; pathlib.Path(sys.argv[1]).write_bytes(b'x'*4096)"
    assert performance.main(["measure", "--workspace", str(workspace),
                              "--report", str(report_path), "--sample-interval", "0.05",
                              "--", sys.executable,
                              "-c", code, str(output)], root=tmp_path) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["schema"] == "osr-performance-measurement/1"
    assert result["process_metrics"]["exit_status"] == 0
    assert result["process_metrics"]["max_rss_kib"] > 0
    assert result["filesystem"]["workspace_allocated_bytes_delta"] >= 4096
    assert (result["filesystem"]["workspace_allocated_bytes_peak_sampled"]
            >= result["filesystem"]["workspace_allocated_bytes_after"])
    assert result["filesystem"]["workspace_sample_interval_seconds"] == 0.05
    assert "peak disk use outside the measured workspace" in result["not_observed"]
    assert report_path.is_file()
    assert output.stat().st_size == 4096


def test_perf_compare_reports_deltas_without_claiming_compatibility(tmp_path, capsys):
    import json
    before = {
        "schema": "osr-performance-measurement/1",
        "command": ["python", "case.py"],
        "wall_seconds_observed": 100.0,
        "process_metrics": {"user_seconds": 20.0, "system_seconds": 10.0,
                            "max_rss_kib": 4096, "filesystem_input_operations": 9,
                            "filesystem_output_operations": 4},
        "filesystem": {"workspace_allocated_bytes_delta": 512,
                       "workspace_allocated_bytes_peak_sampled": 2048},
    }
    after = json.loads(json.dumps(before))
    after["wall_seconds_observed"] = 80.0
    after["process_metrics"]["user_seconds"] = 15.0
    after["filesystem"]["workspace_allocated_bytes_peak_sampled"] = 1024
    after_path = tmp_path / "after.json"
    before_path = tmp_path / "before.json"
    before_path.write_text(json.dumps(before))
    after_path.write_text(json.dumps(after))

    assert performance.main(["compare", "--before", str(before_path),
                             "--after", str(after_path)], root=tmp_path) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["same_command"] is True
    assert result["comparisons"]["wall_seconds"]["relative_change_percent"] == -20.0
    assert result["comparisons"]["user_seconds"]["relative_change_percent"] == -25.0
    assert (result["comparisons"]["workspace_allocated_bytes_peak_sampled"]["delta"]
            == -1024)
    assert "does not assert engineering validity" in result["note"]


def test_measure_command_records_sampled_peak_workspace_bytes(tmp_path):
    workspace = tmp_path / "job"
    report = tmp_path / "measurement.json"
    payload = workspace / "transient.bin"
    script = (
        "from pathlib import Path; import sys, time; "
        "p=Path(sys.argv[1]); p.parent.mkdir(parents=True, exist_ok=True); "
        "p.write_bytes(b'x' * (4 * 1024 * 1024)); time.sleep(0.8); p.unlink()"
    )

    result, exit_code = performance.measure_command(
        [sys.executable, "-c", script, str(payload)], workspace=workspace,
        report_path=report, root=tmp_path, sampling_interval_seconds=0.05,
    )

    assert exit_code == 0
    assert (result["filesystem"]["workspace_allocated_bytes_after"]
            == result["filesystem"]["workspace_allocated_bytes_before"])
    assert not payload.exists()
    assert result["filesystem"]["workspace_allocated_bytes_peak_sampled"] >= 4 * 1024**2
    assert result["filesystem"]["workspace_size_sample_count"] >= 3
    assert "peak disk use outside the measured workspace" in result["not_observed"]
    assert json.loads(report.read_text()) == result


def test_measure_command_rejects_invalid_workspace_sampling_interval(tmp_path):
    with pytest.raises(ValueError, match="sampling interval"):
        performance.measure_command(
            [sys.executable, "-c", "pass"], workspace=tmp_path / "job",
            report_path=tmp_path / "measurement.json", root=tmp_path,
            sampling_interval_seconds=0.01,
        )
