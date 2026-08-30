#!/usr/bin/env python3
"""Validate every committed OSR City Studio project through the Rust compiler."""

from __future__ import annotations

import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
PROJECTS_ROOT = REPO_ROOT / "cities/workspaces"


def main() -> int:
    projects = sorted(path.parent for path in PROJECTS_ROOT.glob("*/project.osr.toml"))
    if not projects:
        raise SystemExit("no City Studio projects found")
    for project in projects:
        relative = project.relative_to(REPO_ROOT)
        print(f"validating City Studio project: {relative}")
        subprocess.run(
            [
                "cargo",
                "run",
                "--quiet",
                "-p",
                "osr-city-studio",
                "--",
                "--project",
                str(relative),
                "validate",
            ],
            cwd=REPO_ROOT,
            stdout=subprocess.DEVNULL,
            check=True,
        )
    print(f"validated {len(projects)} City Studio project(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
