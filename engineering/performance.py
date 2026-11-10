"""Read-only workspace performance and storage inventory commands."""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
import json
import math
import os
import platform
from pathlib import Path
import shutil
import stat
import subprocess
import tempfile
import time
import sys

from engineering.station_rail import ROOT

GIB = 1024 ** 3
DEFAULT_MINIMUM_FREE_GIB = 20.0
DEFAULT_CACHE_AGE_DAYS = 7
CACHE_SOURCE_ROOTS = (".venv", "engineering", "tools", "tests", "services", "scripts")
MAX_STATUS_WORKERS = 8
MAX_STATUS_SECONDS = 20


def _parse_worktrees(raw: str) -> list[dict]:
    rows: list[dict] = []
    current: dict | None = None
    for line in raw.splitlines() + [""]:
        if not line:
            if current is not None:
                rows.append(current)
                current = None
            continue
        if line.startswith("worktree "):
            if current is not None:
                rows.append(current)
            current = {"path": line[len("worktree "):], "head": None,
                       "branch": None, "detached": False,
                       "locked": False, "prunable": False}
        elif current is not None and line.startswith("HEAD "):
            current["head"] = line[5:]
        elif current is not None and line.startswith("branch "):
            branch = line[len("branch "):]
            current["branch"] = branch.removeprefix("refs/heads/")
        elif current is not None and line == "detached":
            current["detached"] = True
        elif current is not None and (line == "locked" or line.startswith("locked ")):
            current["locked"] = True
        elif current is not None and (line == "prunable" or line.startswith("prunable ")):
            current["prunable"] = True
    return rows


def _worktrees(root: Path) -> list[dict]:
    result = subprocess.run(
        ["git", "-C", str(root), "worktree", "list", "--porcelain"],
        check=True, capture_output=True, text=True, timeout=30,
    )
    return _parse_worktrees(result.stdout)


def _du(paths: list[str]) -> tuple[dict[str, int], list[str]]:
    if not paths:
        return {}, []
    try:
        result = subprocess.run(
            ["du", "--summarize", "--block-size=1", "--null", "--", *paths],
            capture_output=True, timeout=300,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        return {}, [f"du failed: {error}"]
    sizes: dict[str, int] = {}
    for record in result.stdout.split(b"\0"):
        if not record:
            continue
        try:
            size, path = record.split(b"\t", 1)
            sizes[os.fsdecode(path)] = int(size)
        except (ValueError, TypeError):
            continue
    errors = [line for line in result.stderr.decode(errors="replace").splitlines() if line]
    if result.returncode and not errors:
        errors.append(f"du exited with status {result.returncode}")
    return sizes, errors


def _worktree_status(row: dict) -> dict:
    path = Path(row["path"])
    if not path.is_dir():
        return {"status": "missing", "dirty_file_count": None, "dirty_paths": []}
    try:
        result = subprocess.run(
            ["git", "-C", str(path), "status", "--porcelain=v1", "--untracked-files=normal"],
            capture_output=True, timeout=MAX_STATUS_SECONDS,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        return {"status": "unavailable", "dirty_file_count": None,
                "dirty_paths": [], "status_error": str(error)}
    if result.returncode:
        return {"status": "unavailable", "dirty_file_count": None,
                "dirty_paths": [],
                "status_error": result.stderr.decode(errors="replace")[:500]}
    lines = result.stdout.decode(errors="replace").splitlines()
    return {"status": "dirty" if lines else "clean",
            "dirty_file_count": len(lines), "dirty_paths": lines[:20],
            "dirty_paths_truncated": len(lines) > 20}


def storage_report(root=ROOT, *, minimum_free_gib=DEFAULT_MINIMUM_FREE_GIB) -> dict:
    """Inventory disk use and registered worktrees without changing any files."""
    root = Path(root).resolve()
    if (isinstance(minimum_free_gib, bool)
            or not isinstance(minimum_free_gib, (int, float))
            or not math.isfinite(minimum_free_gib)
            or not 1 <= minimum_free_gib <= 1024):
        raise ValueError("minimum free-space threshold must be between 1 and 1024 GiB")

    usage = shutil.disk_usage(root)
    children = sorted(root.iterdir(), key=lambda path: path.name)
    root_sizes, root_errors = _du([str(path) for path in children])

    worktrees = _worktrees(root)
    status_rows: list[dict]
    with ThreadPoolExecutor(max_workers=MAX_STATUS_WORKERS) as pool:
        status_rows = list(pool.map(_worktree_status, worktrees))

    external_paths = [row["path"] for row in worktrees if Path(row["path"]).is_dir()]
    worktree_sizes, worktree_errors = _du(external_paths)
    for row, status in zip(worktrees, status_rows):
        row.update(status)
        row["path_exists"] = Path(row["path"]).is_dir()
        row["allocated_bytes"] = worktree_sizes.get(row["path"])
        try:
            owner = Path(row["path"]).stat()
            row["filesystem_owner_uid"] = owner.st_uid
            row["filesystem_owner_gid"] = owner.st_gid
        except OSError:
            row["filesystem_owner_uid"] = None
            row["filesystem_owner_gid"] = None

    directories = sorted(
        ({"path": str(path), "name": path.name,
          "allocated_bytes": root_sizes.get(str(path))}
         for path in children),
        key=lambda row: row["allocated_bytes"] or 0, reverse=True,
    )
    free_threshold = int(minimum_free_gib * GIB)
    direct_child_bytes = sum(row["allocated_bytes"] or 0 for row in directories)
    return {
        "schema": "osr-performance-storage-inventory/1",
        "collected_at_utc": datetime.now(timezone.utc).isoformat(),
        "root": str(root),
        "filesystem": {
            "total_bytes": usage.total,
            "used_bytes": usage.used,
            "free_bytes": usage.free,
            "minimum_free_reserve_bytes": free_threshold,
            "minimum_free_reserve_gib": minimum_free_gib,
            "reserve_status": "met" if usage.free >= free_threshold else "below-reserve",
            "utilization_fraction": usage.used / usage.total if usage.total else None,
        },
        "repository_top_level": directories,
        "repository_direct_child_allocated_bytes": direct_child_bytes,
        "registered_worktree_count": len(worktrees),
        "registered_worktrees": sorted(
            worktrees, key=lambda row: row["allocated_bytes"] or 0, reverse=True,
        ),
        "measurement": {
            "directory_sizes": "GNU du allocated-byte counts; reflink sharing may be counted per path",
            "uncommitted_status_scanned": True,
            "deletion_performed": False,
            "admission_enforced": False,
            "root_du_errors": root_errors,
            "worktree_du_errors": worktree_errors,
        },
    }


def disk_admission(root=ROOT, *, minimum_free_gib=DEFAULT_MINIMUM_FREE_GIB) -> dict:
    """Check the shared-filesystem reserve before dispatching native work.

    This is an admission check only. It does not impose an aggregate per-job
    output quota, and callers must report that distinction accurately.
    """
    if (isinstance(minimum_free_gib, bool)
            or not isinstance(minimum_free_gib, (int, float))
            or not math.isfinite(minimum_free_gib)
            or not 1 <= minimum_free_gib <= 1024):
        raise ValueError("minimum free-space threshold must be between 1 and 1024 GiB")
    root = Path(root).resolve()
    usage = shutil.disk_usage(root)
    required = int(minimum_free_gib * GIB)
    admitted = usage.free >= required
    return {
        "schema": "osr-performance-disk-admission/1",
        "root": str(root),
        "filesystem_free_bytes": usage.free,
        "minimum_free_reserve_bytes": required,
        "minimum_free_reserve_gib": minimum_free_gib,
        "admitted": admitted,
        "execution": "ready" if admitted else "held",
        "reason": None if admitted else "Free space is below the configured reserve",
        "enforcement": "Shared-filesystem free-space admission only; aggregate per-job disk quota is not enforced",
    }


def disk_hold_record(root, action: str, dispositions: dict) -> dict | None:
    """Return a CLI hold record when the shared free-space reserve is unmet."""
    admission = disk_admission(root)
    if admission["admitted"]:
        return None
    return {
        "schema": "osr-performance-disk-admission/1",
        "execution": "held",
        "requested_action": action,
        "resource_admission": admission,
        **dispositions,
    }


def cleanup_bytecode(root=ROOT, *, minimum_age_days=DEFAULT_CACHE_AGE_DAYS,
                     apply=False, now=None) -> dict:
    """Report or remove stale, ordinary Python bytecode caches in source roots.

    Research, build outputs, Git history, city data, general caches, virtual
    environments outside the checkout and all non-bytecode files are excluded.
    The default is a read-only dry run; deletion requires ``apply=True``.
    """
    if (isinstance(minimum_age_days, bool)
            or not isinstance(minimum_age_days, (int, float))
            or not math.isfinite(minimum_age_days)
            or not 0 <= minimum_age_days <= 3650):
        raise ValueError("cache age must be between 0 and 3650 days")
    if type(apply) is not bool:
        raise ValueError("explicit boolean cleanup mode required")
    root = Path(root).resolve()
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        raise ValueError("cleanup reference time must include a timezone")
    cutoff = now.timestamp() - minimum_age_days * 86400
    candidates = []
    errors = []
    for relative in CACHE_SOURCE_ROOTS:
        source = root / relative
        if source.is_symlink() or not source.is_dir():
            continue
        for directory, names, _ in os.walk(source, topdown=True, followlinks=False):
            for name in tuple(names):
                if name != "__pycache__":
                    continue
                names.remove(name)
                cache = Path(directory) / name
                try:
                    cache_info = cache.lstat()
                    if not stat.S_ISDIR(cache_info.st_mode):
                        continue
                    entries = list(cache.iterdir())
                    if not entries:
                        continue
                    file_rows = []
                    held_reason = None
                    for entry in entries:
                        info = entry.lstat()
                        if not stat.S_ISREG(info.st_mode) or entry.suffix != ".pyc":
                            held_reason = "cache contains a non-ordinary or non-bytecode entry"
                            break
                        if info.st_nlink != 1:
                            held_reason = "cache contains a multiply-linked bytecode file"
                            break
                        if info.st_mtime > cutoff:
                            held_reason = "cache contains recently used bytecode"
                            break
                        file_rows.append((entry, info))
                    relative_path = cache.relative_to(root).as_posix()
                    if held_reason:
                        candidates.append({"path": relative_path, "status": "held",
                                           "reason": held_reason, "file_count": len(entries),
                                           "reclaimable_bytes": 0})
                        continue
                    reclaimable = sum((info.st_blocks * 512) or info.st_size
                                       for _, info in file_rows)
                    row = {"path": relative_path, "status": "eligible",
                           "file_count": len(file_rows), "reclaimable_bytes": reclaimable}
                    if apply:
                        removed = 0
                        removed_bytes = 0
                        try:
                            for entry, original in file_rows:
                                current = entry.lstat()
                                if (not stat.S_ISREG(current.st_mode)
                                        or current.st_ino != original.st_ino
                                        or current.st_dev != original.st_dev
                                        or current.st_mtime_ns != original.st_mtime_ns
                                        or current.st_size != original.st_size):
                                    raise OSError("bytecode cache changed after inventory")
                                entry.unlink()
                                removed += 1
                                removed_bytes += (original.st_blocks * 512) or original.st_size
                            cache.rmdir()
                            row.update(status="removed", removed_file_count=removed,
                                       reclaimed_bytes=removed_bytes)
                        except OSError as error:
                            row.update(status="partial-or-held", removed_file_count=removed,
                                       reclaimed_bytes=removed_bytes, error=str(error))
                            errors.append(f"{relative_path}: {error}")
                    candidates.append(row)
                except OSError as error:
                    errors.append(f"{cache}: {error}")
                    candidates.append({"path": cache.relative_to(root).as_posix(),
                                       "status": "unavailable", "reason": str(error),
                                       "file_count": None, "reclaimable_bytes": 0})
    eligible = [row for row in candidates if row["status"] in ("eligible", "removed")]
    return {
        "schema": "osr-performance-cleanup/1",
        "root": str(root),
        "mode": "apply" if apply else "dry-run",
        "minimum_age_days": minimum_age_days,
        "candidate_directory_count": len(candidates),
        "eligible_directory_count": len(eligible),
        "eligible_bytes": sum(row["reclaimable_bytes"] for row in eligible),
        "removed_directory_count": sum(row["status"] == "removed" for row in candidates),
        "reclaimed_bytes": sum(row.get("reclaimed_bytes", 0) for row in candidates),
        "scope": list(CACHE_SOURCE_ROOTS),
        "excluded": [".git", "build", "var", "cities", "docs", ".cache", "node_modules", "all non-bytecode files"],
        "mutation_performed": apply and any(
            row["status"] == "removed" or row.get("removed_file_count", 0) > 0
            for row in candidates),
        "errors": errors,
        "candidates": candidates,
    }


def _git_snapshot(root):
    try:
        revision = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            capture_output=True, text=True, check=True, timeout=30,
        ).stdout.strip()
        status = subprocess.run(
            ["git", "-C", str(root), "status", "--porcelain=v1", "-z",
             "--untracked-files=normal"],
            capture_output=True, check=True, timeout=60,
        ).stdout
        return {"revision": revision, "dirty_path_count": status.count(b"\0")}
    except (OSError, subprocess.SubprocessError):
        return {"revision": None, "dirty_path_count": None}


def measure_command(command, *, workspace, report_path, root=ROOT) -> tuple[dict, int]:
    """Run one command under GNU time and retain comparable process metrics.

    The command is invoked as an argv vector, without a shell. Workspace sizes
    are before/after allocated-byte snapshots; peak workspace disk and cache
    or solver counts are not inferred from those snapshots.
    """
    if (not isinstance(command, (list, tuple)) or not command
            or any(not isinstance(arg, str) or not arg for arg in command)):
        raise ValueError("a nonempty command argument vector is required")
    workspace = Path(workspace).resolve()
    report_path = Path(report_path).resolve()
    root = Path(root).resolve()
    if report_path == workspace or workspace in report_path.parents:
        raise ValueError("performance report must be outside the measured workspace")
    if workspace.is_symlink():
        raise ValueError("measured workspace must not be a symlink")
    workspace.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    timer = Path("/usr/bin/time")
    if not timer.is_file():
        raise OSError("GNU /usr/bin/time is required for reproducible process metrics")

    before_disk = shutil.disk_usage(workspace)
    before_sizes, before_errors = _du([str(workspace)])
    before_size = before_sizes.get(str(workspace))
    source_before = _git_snapshot(root)
    format_string = (
        "elapsed_seconds=%e user_seconds=%U system_seconds=%S max_rss_kib=%M "
        "minor_page_faults=%R major_page_faults=%F "
        "filesystem_input_operations=%I filesystem_output_operations=%O exit_status=%x"
    )
    started_at = datetime.now(timezone.utc).isoformat()
    started = time.monotonic()
    with tempfile.TemporaryDirectory(prefix="osr-perf-measure-") as temp:
        metrics_path = Path(temp) / "time.txt"
        completed = subprocess.run(
            [str(timer), "-f", format_string, "-o", str(metrics_path), "--", *command],
            check=False,
        )
        elapsed = time.monotonic() - started
        raw_metrics = metrics_path.read_text(errors="replace") if metrics_path.exists() else ""
    after_disk = shutil.disk_usage(workspace)
    after_sizes, after_errors = _du([str(workspace)])
    after_size = after_sizes.get(str(workspace))
    source_after = _git_snapshot(root)
    metrics = {}
    for token in raw_metrics.split():
        if "=" not in token:
            continue
        key, value = token.split("=", 1)
        try:
            metrics[key] = float(value) if key.endswith(("seconds", "kib")) else int(value)
        except ValueError:
            metrics[key] = value
    result = {
        "schema": "osr-performance-measurement/1",
        "command": list(command),
        "workspace": str(workspace),
        "report_path": str(report_path),
        "started_at_utc": started_at,
        "wall_seconds_observed": elapsed,
        "command_exit_status": completed.returncode,
        "source_context": {
            "revision_before": source_before["revision"],
            "revision_after": source_after["revision"],
            "unchanged_during_measurement": (
                source_before["revision"] is not None
                and source_before["revision"] == source_after["revision"]
            ),
            "dirty_path_count_before": source_before["dirty_path_count"],
            "dirty_path_count_after": source_after["dirty_path_count"],
        },
        "environment": {
            "python_version": sys.version.split()[0],
            "platform": platform.platform(),
        },
        "process_metrics": metrics,
        "filesystem": {
            "total_bytes": after_disk.total,
            "free_bytes_before": before_disk.free,
            "free_bytes_after": after_disk.free,
            "workspace_allocated_bytes_before": before_size,
            "workspace_allocated_bytes_after": after_size,
            "workspace_allocated_bytes_delta": (
                after_size - before_size if before_size is not None and after_size is not None else None
            ),
            "workspace_du_errors": before_errors + after_errors,
        },
        "not_observed": [
            "peak temporary workspace bytes",
            "cache hits and misses",
            "native solver execution count",
            "retry count",
        ],
        "measurement_notes": [
            "GNU time reports CPU, sampled peak RSS and filesystem operation counts for the command process tree.",
            "Workspace size is an allocated-byte before/after snapshot, not a peak measurement.",
            "Filesystem free-space changes can include concurrent unrelated activity.",
        ],
    }
    fd, pending_name = tempfile.mkstemp(prefix="." + report_path.name + ".",
                                        suffix=".pending", dir=report_path.parent)
    pending = Path(pending_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as output:
            output.write(json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n")
            output.flush()
            os.fsync(output.fileno())
        pending.replace(report_path)
    except OSError:
        try:
            os.close(fd)
        except OSError:
            pass
        pending.unlink(missing_ok=True)
        raise
    return result, completed.returncode


def compare_measurements(before_path, after_path) -> dict:
    """Compare two compatible measurement reports without asserting a win."""
    def read(path):
        path = Path(path)
        info = path.lstat()
        if not stat.S_ISREG(info.st_mode) or info.st_size > 16 * 1024**2:
            raise ValueError("measurement input must be an ordinary JSON report below 16 MiB")
        value = json.loads(path.read_bytes())
        if value.get("schema") != "osr-performance-measurement/1":
            raise ValueError("performance measurement schema differs")
        return value

    before, after = read(before_path), read(after_path)
    fields = {
        "wall_seconds": ("wall_seconds_observed",),
        "user_seconds": ("process_metrics", "user_seconds"),
        "system_seconds": ("process_metrics", "system_seconds"),
        "max_rss_kib": ("process_metrics", "max_rss_kib"),
        "filesystem_input_operations": ("process_metrics", "filesystem_input_operations"),
        "filesystem_output_operations": ("process_metrics", "filesystem_output_operations"),
        "workspace_allocated_bytes_delta": ("filesystem", "workspace_allocated_bytes_delta"),
    }
    comparisons = {}
    for name, path in fields.items():
        left, right = before, after
        for key in path:
            left = left.get(key) if isinstance(left, dict) else None
            right = right.get(key) if isinstance(right, dict) else None
        if (not isinstance(left, (int, float)) or isinstance(left, bool)
                or not isinstance(right, (int, float)) or isinstance(right, bool)
                or not math.isfinite(left) or not math.isfinite(right)):
            comparisons[name] = {"before": left, "after": right,
                                 "delta": None, "relative_change_percent": None}
            continue
        delta = right - left
        comparisons[name] = {
            "before": left,
            "after": right,
            "delta": delta,
            "relative_change_percent": delta / abs(left) * 100 if left != 0 else None,
        }
    return {
        "schema": "osr-performance-comparison/1",
        "before_report": str(Path(before_path).resolve()),
        "after_report": str(Path(after_path).resolve()),
        "same_command": before.get("command") == after.get("command"),
        "same_source_revision": (
            before.get("source_context", {}).get("revision_before") is not None
            and before.get("source_context", {}).get("revision_before")
            == after.get("source_context", {}).get("revision_before")
        ),
        "same_environment": before.get("environment") == after.get("environment"),
        "before_command": before.get("command"),
        "after_command": after.get("command"),
        "comparisons": comparisons,
        "note": "Comparable command inputs, candidate identity and execution environment must be checked by the caller; this report does not assert engineering validity.",
    }


def main(argv=None, *, root=ROOT) -> int:
    parser = argparse.ArgumentParser(prog="./osr perf")
    commands = parser.add_subparsers(dest="action", required=True)
    storage = commands.add_parser("storage", help="Read-only disk and worktree inventory")
    storage.add_argument("--minimum-free-gib", type=float,
                         default=DEFAULT_MINIMUM_FREE_GIB)
    cleanup = commands.add_parser("cleanup", help="Dry-run or remove stale source-tree bytecode caches")
    cleanup.add_argument("--minimum-age-days", type=float, default=DEFAULT_CACHE_AGE_DAYS)
    cleanup.add_argument("--apply", action="store_true", help="Remove only stale ordinary .pyc caches in the reported source roots")
    measure = commands.add_parser("measure", help="Run an argv command and record process/resource metrics")
    measure.add_argument("--workspace", type=Path, required=True,
                         help="Dedicated job workspace whose allocated bytes are measured before and after")
    measure.add_argument("--report", type=Path, required=True,
                         help="JSON report path outside the measured workspace")
    measure.add_argument("command", nargs=argparse.REMAINDER)
    compare = commands.add_parser("compare", help="Compare two recorded process measurements")
    compare.add_argument("--before", type=Path, required=True)
    compare.add_argument("--after", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.action == "storage":
            value = storage_report(root, minimum_free_gib=args.minimum_free_gib)
            exit_code = 0
        elif args.action == "cleanup":
            value = cleanup_bytecode(root, minimum_age_days=args.minimum_age_days,
                                     apply=args.apply)
            exit_code = 0
        elif args.action == "measure":
            command = args.command[1:] if args.command[:1] == ["--"] else args.command
            value, exit_code = measure_command(command, workspace=args.workspace,
                                               report_path=args.report, root=root)
        else:
            value = compare_measurements(args.before, args.after)
            exit_code = 0
        print(json.dumps(value, indent=2, sort_keys=True, allow_nan=False))
        return exit_code
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        schema = {
            "storage": "osr-performance-storage-inventory/1",
            "cleanup": "osr-performance-cleanup/1",
            "measure": "osr-performance-measurement/1",
            "compare": "osr-performance-comparison/1",
        }[args.action]
        print(json.dumps({"schema": schema,
                          "execution": "held", "reason": str(error)},
                         indent=2, sort_keys=True))
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
