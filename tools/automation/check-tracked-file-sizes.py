#!/usr/bin/env python3
"""Fail when a Git-tracked artifact exceeds the repository's 50 MiB limit."""

from __future__ import annotations

import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MAX_BYTES = 50 * 1024 * 1024


def main() -> int:
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
    )
    oversized: list[tuple[int, Path]] = []
    tracked = [item for item in result.stdout.split(b"\0") if item]
    for raw in tracked:
        relative = Path(raw.decode("utf-8", errors="surrogateescape"))
        path = REPO_ROOT / relative
        if path.is_file() and path.stat().st_size > MAX_BYTES:
            oversized.append((path.stat().st_size, relative))

    if oversized:
        print("Tracked files exceed the 50 MiB repository artifact limit:")
        for size, path in sorted(oversized, reverse=True):
            print(f"- {path}: {size / 1024 / 1024:.1f} MiB")
        return 1

    largest = max(
        ((REPO_ROOT / Path(raw.decode("utf-8", errors="surrogateescape"))).stat().st_size
         for raw in tracked
         if (REPO_ROOT / Path(raw.decode("utf-8", errors="surrogateescape"))).is_file()),
        default=0,
    )
    print(
        f"tracked artifact size: pass ({len(tracked)} files; "
        f"largest {largest / 1024 / 1024:.1f} MiB; limit 50.0 MiB)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
