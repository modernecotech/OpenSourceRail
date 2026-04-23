"""OSR-ALN validator hard-gate + soft-gate tests.

Each hard gate H1–H8 from the format-spec §"Validator semantics"
gets a dedicated test: a minimal good document + a mutation that
should make the gate fire.
"""

from __future__ import annotations

import copy
import tomllib
from pathlib import Path

from osr_aln.validate import PRESETS, validate, validate_file

SAMPLES = Path(__file__).resolve().parent.parent / "samples"
SAMAWAH_ALN = (
    Path(__file__).resolve().parent.parent.parent.parent
    / "designs/middle-east/iraq/samawah/samawah-line1.aln.toml"
)
SAMAWAH_DESIGN = (
    Path(__file__).resolve().parent.parent.parent.parent
    / "designs/middle-east/iraq/samawah/design.toml"
)


def _minimal_good() -> dict:
    """Smallest OSR-ALN document that passes every hard gate."""
    return {
        "meta": {
            "schema_version": "1.0",
            "line_id": "test-line",
            "design_date": "2026-04-23",
            "surveyor": "unit test",
            "preset": "standard-urban",
            "consist": "light-metro-3car",
            "crs": "EPSG:32638",
            "units": "metric",
            "is_ring": False,
        },
        "horizontal": [
            {
                "station_m": 0.0,
                "easting_m": 477500.0,
                "northing_m": 3467100.0,
                "bearing_in_deg": 128.7,
                "bearing_out_deg": 128.7,
                "curve_radius_m": 0.0,
                "transition_length_m": 0.0,
            },
            {
                "station_m": 1000.0,
                "easting_m": 478280.0,
                "northing_m": 3466475.0,
                "bearing_in_deg": 128.7,
                "bearing_out_deg": 128.7,
                "curve_radius_m": 0.0,
                "transition_length_m": 0.0,
            },
        ],
        "vertical": [
            {"station_m": 0.0, "elevation_m": 6.0, "vc_radius_m": 0.0},
            {"station_m": 1000.0, "elevation_m": 6.0, "vc_radius_m": 0.0},
        ],
        "civil": [
            {"from_station_m": 0.0, "to_station_m": 1000.0, "class": "at-grade"},
        ],
        "station": [
            {"id": "s-a", "station_m": 0.0, "platform_length_m": 75.0},
            {"id": "s-b", "station_m": 1000.0, "platform_length_m": 75.0},
        ],
    }


def test_minimal_good_passes() -> None:
    r = validate(_minimal_good(), known_station_ids={"s-a", "s-b"})
    assert r.ok, r.format_text()
    assert r.errors == []


def test_h1_unknown_preset_fails() -> None:
    doc = _minimal_good()
    doc["meta"]["preset"] = "nonsense-preset"
    r = validate(doc)
    assert not r.ok
    assert any("H1" in e for e in r.errors)


def test_h2_incompatible_consist_fails() -> None:
    doc = _minimal_good()
    # tram-2car is not compatible with standard-urban.
    doc["meta"]["consist"] = "tram-2car"
    r = validate(doc, known_station_ids={"s-a", "s-b"})
    assert not r.ok
    assert any("H2" in e for e in r.errors)


def test_h3_gap_in_civil_spans_fails() -> None:
    doc = _minimal_good()
    doc["civil"] = [
        {"from_station_m": 0.0, "to_station_m": 500.0, "class": "at-grade"},
        # gap 500..700
        {"from_station_m": 700.0, "to_station_m": 1000.0, "class": "at-grade"},
    ]
    r = validate(doc, known_station_ids={"s-a", "s-b"})
    assert not r.ok
    assert any("H3" in e for e in r.errors)


def test_h4_tunnel_class_fails() -> None:
    doc = _minimal_good()
    doc["civil"] = [
        {"from_station_m": 0.0, "to_station_m": 1000.0, "class": "tunnel"},
    ]
    r = validate(doc, known_station_ids={"s-a", "s-b"})
    assert not r.ok
    assert any("H4" in e for e in r.errors)


def test_h5_unknown_station_id_fails() -> None:
    doc = _minimal_good()
    # "s-c" is not in the design.toml set.
    doc["station"].append(
        {"id": "s-c", "station_m": 500.0, "platform_length_m": 75.0}
    )
    r = validate(doc, known_station_ids={"s-a", "s-b"})
    assert not r.ok
    assert any("H5" in e for e in r.errors)


def test_h5_skipped_when_design_toml_not_provided() -> None:
    doc = _minimal_good()
    r = validate(doc)
    # H5 skipped — gate fires as a warning, not an error.
    assert r.ok
    assert any("H5 skipped" in w for w in r.warnings)


def test_h6_sub_minimum_radius_fails() -> None:
    doc = _minimal_good()
    # standard-urban minimum is 200 m.
    doc["horizontal"][1]["curve_radius_m"] = 150.0
    r = validate(doc, known_station_ids={"s-a", "s-b"})
    assert not r.ok
    assert any("H6" in e for e in r.errors)


def test_h7_grade_over_preset_fails() -> None:
    doc = _minimal_good()
    # standard-urban maximum is 40 ‰. A drop of 50 m over 1 km = 50 ‰.
    doc["vertical"][1]["elevation_m"] = -44.0  # Δz=-50, Δx=1000 → 50 ‰
    r = validate(doc, known_station_ids={"s-a", "s-b"})
    assert not r.ok
    assert any("H7" in e for e in r.errors)


def test_h8_cant_over_preset_fails() -> None:
    doc = _minimal_good()
    doc["cant"] = [
        {
            "from_station_m": 0.0,
            "to_station_m": 1000.0,
            "max_cant_mm": 200,  # > standard-urban's 150 mm
            "transition_in_m": 50.0,
            "transition_out_m": 50.0,
        }
    ]
    r = validate(doc, known_station_ids={"s-a", "s-b"})
    assert not r.ok
    assert any("H8" in e for e in r.errors)


def test_s1_elevated_share_over_30pc_warns() -> None:
    doc = _minimal_good()
    # 50% elevated over 1000 m total.
    doc["civil"] = [
        {"from_station_m": 0.0, "to_station_m": 500.0, "class": "at-grade"},
        {"from_station_m": 500.0, "to_station_m": 1000.0, "class": "elevated"},
    ]
    r = validate(doc, known_station_ids={"s-a", "s-b"})
    assert r.ok
    assert any("S1" in w for w in r.warnings)


def test_s2_radius_near_preset_min_warns() -> None:
    doc = _minimal_good()
    # 300 m is > 200 m (min) but < 2 × 200 = 400 m.
    doc["horizontal"][1]["curve_radius_m"] = 300.0
    r = validate(doc, known_station_ids={"s-a", "s-b"})
    assert r.ok
    assert any("S2" in w for w in r.warnings)


def test_s3_grade_near_preset_max_warns() -> None:
    doc = _minimal_good()
    # 35 ‰ is > 0.8 × 40 (= 32) but ≤ 40.
    doc["vertical"][1]["elevation_m"] = 41.0  # 35 ‰ over 1000 m
    r = validate(doc, known_station_ids={"s-a", "s-b"})
    assert r.ok
    assert any("S3" in w for w in r.warnings)


def test_samawah_line1_passes_with_design_toml() -> None:
    """The hand-authored Samawah Line 1 alignment must pass every
    hard gate against the deployment's design.toml."""
    if not SAMAWAH_ALN.exists() or not SAMAWAH_DESIGN.exists():
        return  # skip if files are absent (e.g., during stand-alone tool install)
    with SAMAWAH_DESIGN.open("rb") as f:
        design = tomllib.load(f)
    ids = {s.get("id") for s in design.get("stations", []) if s.get("id")}
    report = validate_file(SAMAWAH_ALN, known_station_ids=ids)
    assert report.ok, report.format_text()


SAMAWAH_LINE2_ALN = (
    Path(__file__).resolve().parent.parent.parent.parent
    / "designs/middle-east/iraq/samawah/samawah-line2.aln.toml"
)


def test_samawah_line2_ring_passes_with_design_toml() -> None:
    """The hand-authored Samawah Line 2 ring alignment must pass
    every hard gate against the deployment's design.toml. Line 2
    exercises the is_ring = true path and 4 cant sections."""
    if not SAMAWAH_LINE2_ALN.exists() or not SAMAWAH_DESIGN.exists():
        return
    with SAMAWAH_DESIGN.open("rb") as f:
        design = tomllib.load(f)
    ids = {s.get("id") for s in design.get("stations", []) if s.get("id")}
    report = validate_file(SAMAWAH_LINE2_ALN, known_station_ids=ids)
    assert report.ok, report.format_text()

    # Sanity: Line 2 declares is_ring = true.
    with SAMAWAH_LINE2_ALN.open("rb") as f:
        doc = tomllib.load(f)
    assert doc["meta"].get("is_ring") is True, "Line 2 must be a ring"


def test_preset_table_has_all_four_rfc0009_presets() -> None:
    assert set(PRESETS) == {
        "heritage-tram",
        "standard-urban",
        "standard-metro",
        "mainline-mixed",
    }
