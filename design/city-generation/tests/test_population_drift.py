"""Population drift gate.

`lib/city-batches/world-sample.toml` is the **canonical source of
truth** for city population (see the file header for the policy).
Every design.toml under `cities/catalogue/` whose city slug appears in the
catalog must carry the catalog's population — passing the wrong
`--population` to `osr-design`, or hand-editing the design.toml,
silently shifts the rolling-stock family band (RFC 0008 §5), the
fleet sizing, and the entire CAPEX line. This test fails CI loudly
when that drift creeps in.

Resolution: re-emit the city via
    cargo run --release --bin osr-design -- --slug <slug> \
        --sidecar .cache/osr-pipeline/rasters/<slug>.grid.json \
        --out-dir cities/catalogue/.../<City>
With no `--population` flag: `osr-design` reads the catalog
automatically.
"""

from __future__ import annotations

import tomllib
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
CATALOG = REPO_ROOT / "lib/city-batches/world-sample.toml"
DESIGNS_ROOT = REPO_ROOT / "cities/catalogue"


def _load_catalog() -> dict[str, dict]:
    doc = tomllib.loads(CATALOG.read_text())
    return {c["slug"]: c for c in doc.get("cities", [])}


def _all_design_files() -> list[Path]:
    return sorted(DESIGNS_ROOT.rglob("design.toml"))


@pytest.mark.parametrize("design_path", _all_design_files(), ids=lambda p: p.parent.name)
def test_design_population_matches_catalog(design_path: Path) -> None:
    """Every committed design.toml whose slug is in the catalog must
    carry the catalog's population."""
    design = tomllib.loads(design_path.read_text())
    slug = design.get("city", {}).get("slug")
    if not slug:
        pytest.skip(f"{design_path} has no [city] slug — older schema")
    catalog = _load_catalog()
    if slug not in catalog:
        pytest.skip(
            f"slug {slug!r} not in {CATALOG} — add it there to make this "
            "design canonical, or accept that it is unverified"
        )
    expected = int(catalog[slug]["population"])
    actual = int(design["city"]["population"])
    assert expected == actual, (
        f"{design_path}: [city] population = {actual:,} but catalog "
        f"says {expected:,}. Re-emit with `cargo run --release --bin "
        f"osr-design -- --slug {slug} --sidecar .cache/.../{slug}.grid.json "
        f"--out-dir {design_path.parent}` (no --population flag — the "
        f"catalog provides it)."
    )


def test_catalog_has_required_metadata() -> None:
    """Every catalog entry must carry the population-policy fields so
    drift can be diagnosed (which year, which census/source)."""
    catalog = _load_catalog()
    assert catalog, f"empty catalog at {CATALOG}"
    required = ("country", "population", "population_source", "population_source_year")
    missing: list[str] = []
    for slug, entry in catalog.items():
        for k in required:
            if k not in entry:
                missing.append(f"{slug}: {k}")
    assert not missing, (
        "catalog entries missing required fields:\n  - "
        + "\n  - ".join(missing)
    )
