"""OSR-ALN validator hard-gate + soft-gate tests.

Each hard gate H1–H8 from the format-spec §"Validator semantics"
gets a dedicated test: a minimal good document + a mutation that
should make the gate fire.
"""

from __future__ import annotations

import copy
from osr_aln.validate import PRESETS, validate


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
            {"id": "s-a", "station_m": 0.0, "platform_length_m": 61.0},
            {"id": "s-b", "station_m": 1000.0, "platform_length_m": 61.0},
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
    # Full metro stock is not compatible with the street-integrated preset.
    doc["meta"]["consist"] = "metro-4car"
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


def test_h3_civil_spans_must_reach_alignment_end() -> None:
    doc = _minimal_good()
    doc["civil"][0]["to_station_m"] = 900.0
    r = validate(doc, known_station_ids={"s-a", "s-b"})
    assert not r.ok
    assert any("coverage ends" in e for e in r.errors)


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
        {"id": "s-c", "station_m": 500.0, "platform_length_m": 61.0}
    )
    r = validate(doc, known_station_ids={"s-a", "s-b"})
    assert not r.ok
    assert any("H5" in e for e in r.errors)


def test_h5_unknown_line_id_fails() -> None:
    doc = _minimal_good()
    r = validate(
        doc,
        known_station_ids={"s-a", "s-b"},
        known_line_ids={"another-line"},
    )
    assert not r.ok
    assert any("meta.line_id" in e for e in r.errors)


def test_h5_skipped_when_design_toml_not_provided() -> None:
    doc = _minimal_good()
    r = validate(doc)
    # H5 skipped — gate fires as a warning, not an error.
    assert r.ok
    assert any("H5 skipped" in w for w in r.warnings)


def test_h6_sub_minimum_radius_fails() -> None:
    doc = _minimal_good()
    # standard-urban minimum is 90 m.
    doc["horizontal"][1]["curve_radius_m"] = 80.0
    r = validate(doc, known_station_ids={"s-a", "s-b"})
    assert not r.ok
    assert any("H6" in e for e in r.errors)


def test_h7_grade_over_preset_fails() -> None:
    doc = _minimal_good()
    # standard-urban maximum is 50 per mille.
    doc["vertical"][1]["elevation_m"] = -49.0  # dz=-55, dx=1000 -> 55 per mille
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
    # 120 m is above 90 m (min) but below twice that minimum.
    doc["horizontal"][1]["curve_radius_m"] = 120.0
    r = validate(doc, known_station_ids={"s-a", "s-b"})
    assert r.ok
    assert any("S2" in w for w in r.warnings)


def test_s3_grade_near_preset_max_warns() -> None:
    doc = _minimal_good()
    # 45 per mille is above 0.8 x 50 but within the 50 per mille limit.
    doc["vertical"][1]["elevation_m"] = 51.0
    r = validate(doc, known_station_ids={"s-a", "s-b"})
    assert r.ok
    assert any("S3" in w for w in r.warnings)


def test_preset_table_has_all_rfc0009_presets() -> None:
    assert set(PRESETS) == {
        "standard-urban",
        "standard-metro",
        "mainline-mixed",
    }
