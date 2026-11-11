#!/usr/bin/env python3
"""Expand a blob-filtered clone to exact inputs for the v0.6 release demo."""

from __future__ import annotations

import json
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess


BASE_PATTERNS = (
    "/.gitignore",
    "/.github/release-smoke-tests.txt",
    "/engineering/development_baseline/**",
    "/tests/test_v06_software_release_gate.py",
    "/tests/test_city_recalculation.py",
    "/tests/test_outline_city_jobs.py",
    "/tests/test_outline_completion_cli_admission.py",
    "/cities/catalogue/west-asia/Iraq/Samawah/**",
    "/docs/design-engine/current/**",
    "/docs/design-engine/v06-software-release/**",
    "/docs/design-engine/v06-design-closure/compact-drive-source-replay-01/compact-737-h100/**",
    "/docs/design-engine/powered-bogie-detail/body.json.gz",
    "/docs/design-engine/outline-completion/**",
    "/docs/design-engine/city-atlas/**",
    "/docs/design-engine/demand-outline/**",
    "/docs/design-engine/supply-economics/**",
    "/docs/design-engine/breadth-first-shape-portfolio/**",
    "/docs/design-engine/civil-shape-portfolio/**",
    "/docs/design-engine/coupled-railway/**",
    "/docs/design-engine/ferrite-maglev/comfort-design/**",
    "/docs/workbench/city-atlas-assets.json",
    "/docs/workbench/current/**",
    "/docs/releases/v0.6.0/**",
    "/tools/automation/default-design-workbench.py",
    "/tools/automation/osr-python",
    "/tools/automation/prepare-v06-release-checkout.py",
    "/tools/automation/tests/browser-launch.mjs",
    "/tools/automation/tests/verify-development-baseline.mjs",
    "/tools/automation/tests/verify-v06-software-journey-a.mjs",
    "/package.json",
    "/package-lock.json",
)
MIN_FREE_BYTES = 8 * 1024**3
MIN_POST_EXPANSION_FREE_BYTES = 6 * 1024**3
SEED_MANIFESTS = (
    "docs/design-engine/outline-completion/manifest.json",
    "docs/design-engine/city-atlas/manifest.json",
    "docs/design-engine/coupled-railway/manifest.json",
    "docs/workbench/city-atlas-assets.json",
)


def allocated_bytes(root: Path) -> int:
    total = 0
    pending = [root]
    while pending:
        directory = pending.pop()
        with os.scandir(directory) as entries:
            for entry in entries:
                if entry.is_dir(follow_symlinks=False):
                    pending.append(Path(entry.path))
                elif entry.is_file(follow_symlinks=False):
                    metadata = entry.stat(follow_symlinks=False)
                    total += getattr(metadata, "st_blocks", 0) * 512 or metadata.st_size
    return total
SOURCE_FIELDS = ("source_sha256", "calculation_sha256", "presentation_sha256")


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    dirty = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=all"],
        cwd=root, check=True, capture_output=True, text=True,
    ).stdout
    if dirty:
        raise RuntimeError("release source expansion requires a clean checkout")
    available_before = shutil.disk_usage(root).free
    if available_before < MIN_FREE_BYTES:
        raise RuntimeError(
            f"release source expansion requires {MIN_FREE_BYTES} free bytes; "
            f"found {available_before}"
        )

    patterns = set(BASE_PATTERNS)
    manifests = []
    for relative in SEED_MANIFESTS:
        value = json.loads((root / relative).read_bytes())
        manifests.append((relative, value.get("manifest_id")))
        for field in SOURCE_FIELDS:
            sources = value.get(field, {})
            if not isinstance(sources, dict):
                continue
            for source in sources:
                path = PurePosixPath(source)
                if (not source or path.is_absolute() or ".." in path.parts
                        or path.as_posix() != source or "\\" in source
                        or any(char in source for char in "*?[]\n\r")):
                    raise ValueError(f"unsafe source path in {relative}: {source!r}")
                patterns.add("/" + source)

    subprocess.run(
        ["git", "sparse-checkout", "set", "--no-cone", "--stdin"],
        cwd=root, input="\n".join(sorted(patterns)) + "\n", text=True, check=True,
    )
    subprocess.run(["git", "read-tree", "-mu", "HEAD"], cwd=root, check=True)
    dirty_after = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=all"],
        cwd=root, check=True, capture_output=True, text=True,
    ).stdout
    if dirty_after:
        raise RuntimeError("manifest source expansion changed the checkout: " + dirty_after)

    available_after = shutil.disk_usage(root).free
    if available_after < MIN_POST_EXPANSION_FREE_BYTES:
        raise RuntimeError(
            "release source expansion left less than the 6 GiB setup reserve: "
            f"{available_after} bytes remain"
        )
    print(json.dumps({
        "checkout": "v0.6-software-release-evaluation",
        "seed_manifests": manifests,
        "exact_source_paths_added": len(patterns) - len(BASE_PATTERNS),
        "sparse_patterns": len(patterns),
        "expanded_checkout_allocated_bytes": allocated_bytes(root),
        "available_disk_bytes_after_expansion": available_after,
        "minimum_free_disk_bytes": MIN_FREE_BYTES,
        "minimum_post_expansion_free_disk_bytes": MIN_POST_EXPANSION_FREE_BYTES,
        "native_solver_packages_included": False,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
