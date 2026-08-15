"""Focused tests for repository-level network quality validators."""

from __future__ import annotations

import importlib.util
import textwrap
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def _load_script(relative: str):
    path = REPO_ROOT / relative
    spec = importlib.util.spec_from_file_location(path.stem.replace("-", "_"), path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_station_validator_uses_light_metro_spacing_and_centre_consolidation(
    tmp_path: Path,
) -> None:
    validator = _load_script("scripts/validate-station-clusters.py")
    design = tmp_path / "design.toml"
    design.write_text(
        textwrap.dedent(
            """
            [city]
            slug = "validator-fixture"
            bbox = { south = 0.0, west = 0.0, north = 0.1, east = 0.1 }

            [[stations]]
            id = "a"
            line = "line-1"
            lat = 0.0500
            lon = 0.0500
            s_m = 0.0

            [[stations]]
            id = "b"
            line = "line-1"
            lat = 0.0500
            lon = 0.0600
            s_m = 1200.0

            [[stations]]
            id = "c"
            line = "line-2"
            lat = 0.0500
            lon = 0.0640
            s_m = 0.0
            """
        ).strip()
        + "\n",
        encoding="utf-8",
    )

    result = validator.validate(design)
    codes = {failure["code"] for failure in result["failures"]}
    review_codes = {finding["code"] for finding in result["review_findings"]}
    assert result["minimum_inline_chainage_m"] == 1_180.0
    assert result["preferred_inline_chainage_m"] == 1_200.0
    assert "same-line-stations-too-close" not in review_codes
    assert "nearby-cross-line-stations-not-one-interchange" in codes
    assert "same-line-stations-too-close" not in codes


def test_ring_validator_flags_material_radial_backtracking() -> None:
    validator = _load_script("scripts/validate-ring-interchanges.py")
    finding = validator.backtracking_finding(
        "line-1",
        [
            [0.000, 0.000],
            [0.030, 0.000],
            [0.015, 0.000],
            [0.060, 0.000],
        ],
    )
    assert finding is not None
    assert finding["code"] == "radial-corridor-turns-back-on-itself"
    assert finding["maximum_reverse_excursion_m"] > 750.0


def test_ring_validator_allows_small_accumulated_street_wiggles() -> None:
    validator = _load_script("scripts/validate-ring-interchanges.py")
    finding = validator.backtracking_finding(
        "line-1",
        [
            [0.000, 0.000],
            [0.012, 0.000],
            [0.008, 0.000],
            [0.020, 0.000],
            [0.016, 0.000],
            [0.040, 0.000],
        ],
    )
    assert finding is None
