"""Read-only workspace performance and storage inventory commands."""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
import json
import math
import os
from pathlib import Path
import shutil
import stat
import subprocess

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


def main(argv=None, *, root=ROOT) -> int:
    parser = argparse.ArgumentParser(prog="./osr perf")
    commands = parser.add_subparsers(dest="action", required=True)
    storage = commands.add_parser("storage", help="Read-only disk and worktree inventory")
    storage.add_argument("--minimum-free-gib", type=float,
                         default=DEFAULT_MINIMUM_FREE_GIB)
    cleanup = commands.add_parser("cleanup", help="Dry-run or remove stale source-tree bytecode caches")
    cleanup.add_argument("--minimum-age-days", type=float, default=DEFAULT_CACHE_AGE_DAYS)
    cleanup.add_argument("--apply", action="store_true", help="Remove only stale ordinary .pyc caches in the reported source roots")
    args = parser.parse_args(argv)
    try:
        if args.action == "storage":
            value = storage_report(root, minimum_free_gib=args.minimum_free_gib)
        else:
            value = cleanup_bytecode(root, minimum_age_days=args.minimum_age_days,
                                     apply=args.apply)
        print(json.dumps(value, indent=2, sort_keys=True, allow_nan=False))
        return 0
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        schema = "osr-performance-cleanup/1" if args.action == "cleanup" else "osr-performance-storage-inventory/1"
        print(json.dumps({"schema": schema,
                          "execution": "held", "reason": str(error)},
                         indent=2, sort_keys=True))
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
