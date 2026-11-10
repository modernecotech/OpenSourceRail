"""Read-only workspace performance and storage inventory commands."""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path
import shutil
import subprocess

from engineering.station_rail import ROOT

GIB = 1024 ** 3
DEFAULT_MINIMUM_FREE_GIB = 20.0
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


def main(argv=None, *, root=ROOT) -> int:
    parser = argparse.ArgumentParser(prog="./osr perf")
    commands = parser.add_subparsers(dest="action", required=True)
    storage = commands.add_parser("storage", help="Read-only disk and worktree inventory")
    storage.add_argument("--minimum-free-gib", type=float,
                         default=DEFAULT_MINIMUM_FREE_GIB)
    args = parser.parse_args(argv)
    try:
        print(json.dumps(storage_report(root, minimum_free_gib=args.minimum_free_gib),
                         indent=2, sort_keys=True, allow_nan=False))
        return 0
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        print(json.dumps({"schema": "osr-performance-storage-inventory/1",
                          "execution": "held", "reason": str(error)},
                         indent=2, sort_keys=True))
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
