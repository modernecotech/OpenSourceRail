#!/usr/bin/env python3
"""Expand a blob-filtered clone to exact inputs for the v0.6 release demo."""

from __future__ import annotations

import json
import gzip
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess


BASE_PATTERNS = (
    "/.gitignore",
    "/.github/repository-metadata.yml",
    "/.github/release-smoke-tests.txt",
    "/.github/workflows/development-baseline.yml",
    "/README.md",
    "/Cargo.lock",
    "/Cargo.toml",
    "/crates/**",
    "/campaigns/v06-design-integration-closure.toml",
    "/campaigns/v06-software-release.toml",
    "/campaigns/compact-affordable-launch.toml",
    "/campaigns/mass-reserve-sensitivity.toml",
    "/LICENSES/**",
    "/engineering/*.py",
    "/engineering/compact_drive/**",
    "/engineering/development_baseline/**",
    "/engineering/design_search/*.py",
    "/engineering/design_search/tests/test_compact_launch_source_epoch.py",
    "/engineering/design_search/tests/test_line_benchmark_source_epoch.py",
    "/engineering/maglev_research/readme_context.py",
    "/engineering/outline/**",
    "/engineering/railway_project/**",
    "/engineering/rustgis/**",
    "/engineering/station_rail/**",
    "/services/integration/osr_integration/__init__.py",
    "/services/integration/osr_integration/city_outline.py",
    "/engineering/v06_software_release/**",
    "/engineering/vehicle_optimisation/equipment.py",
    "/engineering/trip_dynamics/__init__.py",
    "/engineering/trip_dynamics/__main__.py",
    "/engineering/trip_dynamics/interactive.py",
    "/engineering/v06_design_closure/**",
    "/tests/test_v06_software_release_gate.py",
    "/tests/test_city_recalculation.py",
    "/tests/test_outline_city_jobs.py",
    "/tests/test_outline_completion_cli_admission.py",
    "/cities/catalogue/west-asia/Iraq/Samawah/**",
    "/docs/design-engine/current/**",
    "/docs/design-engine/mass-reconciliation/current/**",
    "/docs/archives/compact-launch-source-epochs/**",
    "/docs/archives/coupled-railway-source-epochs/**",
    "/docs/archives/line30-benchmark-source-epochs/**",
    "/docs/design-engine/compact-launch/**",
    "/docs/design-engine/line30-benchmark/**",
    "/docs/design-engine/v06-software-release/**",
    "/docs/design-engine/v06-design-closure/status.json",
    "/docs/capabilities/directory.md",
    "/docs/ARCHITECTURE.md",
    "/docs/first-adoptable-product.md",
    "/docs/open-source-rail-overview.md",
    "/docs/assets/v0.6/illustrations.json",
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
    "/docs/releases/v0.6.1/**",
    "/tools/automation/default-design-workbench.py",
    "/osr",
    "/tools/automation/osr-python",
    "/tools/automation/prepare-v06-release-checkout.py",
    "/tools/automation/tests/browser-launch.mjs",
    "/tools/automation/tests/verify-development-baseline.mjs",
    "/tools/automation/tests/verify-v06-release-workbench.mjs",
    "/tools/automation/tests/verify-v06-software-journey-a.mjs",
    "/tools/automation/tests/verify-v07-samawah-corridor.mjs",
    "/package.json",
    "/package-lock.json",
    "/rust-toolchain.toml",
    "/**/README*.md",
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


def _release_smoke_patterns(root: Path) -> set[str]:
    """Include every explicitly selected release test in the sparse checkout."""
    manifest = root / ".github/release-smoke-tests.txt"
    patterns = set()
    for line_number, line in enumerate(manifest.read_text(encoding="utf-8").splitlines(), 1):
        source = line.strip()
        if not source or source.startswith("#"):
            continue
        path = PurePosixPath(source)
        if (path.is_absolute() or ".." in path.parts or path.as_posix() != source
                or "\\" in source or any(char in source for char in "*?[]")):
            raise ValueError(f"unsafe release smoke path on line {line_number}")
        patterns.add("/" + source)
    return patterns


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
    patterns.update(_release_smoke_patterns(root))
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

    # Journey A binds a separate compressed body package rather than a city
    # manifest. Expand its declared producer inputs as part of the same exact
    # source checkout so local and CI evaluation runs do not fail on omissions.
    body_record = (
        "docs/design-engine/v06-design-closure/compact-drive-source-replay-01/"
        "compact-737-h100/body.json.gz"
    )
    body = json.loads(gzip.decompress((root / body_record).read_bytes()))
    body_sources = body.get("source_sha256", {})
    if not isinstance(body_sources, dict) or not body_sources:
        raise ValueError("Samawah body package requires an explicit source map")
    for source, expected in body_sources.items():
        path = PurePosixPath(source)
        if (not isinstance(source, str) or not isinstance(expected, str)
                or len(expected) != 64 or not source or path.is_absolute()
                or ".." in path.parts or path.as_posix() != source
                or "\\" in source or any(char in source for char in "*?[]\n\r")):
            raise ValueError(f"unsafe body source path: {source!r}")
        patterns.add("/" + source)
    manifests.append((body_record, body.get("candidate_id")))

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
