"""Byte-identical round-trip against the sample LandXML input.

Demonstrates that the converter is deterministic: given the same
input, it always produces the same output. Protects against
accidental non-deterministic ordering (dict iteration, float
formatting drift).
"""

from __future__ import annotations

from pathlib import Path

from osr_aln.landxml_to_osr_aln import Meta, convert

SAMPLES = Path(__file__).resolve().parent.parent / "samples"


def _meta() -> Meta:
    return Meta(
        line_id="samawah-line1",
        preset="standard-urban",
        consist="light-metro-3car",
        crs="EPSG:32638",
        surveyor="Samawah Civil Associates",
        design_date="2026-04-23",
    )


def test_round_trip_is_byte_identical() -> None:
    xml_path = SAMPLES / "samawah-line1.xml"
    golden_path = SAMPLES / "samawah-line1.aln.toml"
    assert xml_path.exists(), "sample LandXML missing"
    assert golden_path.exists(), "golden OSR-ALN missing"

    produced = convert(xml_path, _meta())
    expected = golden_path.read_text()

    # Byte-identical comparison — any drift in the converter's output
    # (float rounding, ordering) shows up as a diff the reviewer can
    # examine.
    assert produced == expected, (
        "converter output drifted from golden — inspect the diff "
        "and either update the converter or regenerate the golden "
        "with `landxml-to-osr-aln --input samples/samawah-line1.xml ...`"
    )


def test_every_horizontal_element_appears() -> None:
    """Sanity: the sample LandXML has 1 Line + 1 Curve + 1 Spiral +
    1 Line = 4 declared segments. The converter emits at least one
    [[horizontal]] block per segment (tangent lines emit 2 — start +
    end anchors)."""
    xml_path = SAMPLES / "samawah-line1.xml"
    produced = convert(xml_path, _meta())
    horizontal_count = produced.count("[[horizontal]]")
    assert horizontal_count >= 4, (
        f"expected ≥ 4 horizontal rows, got {horizontal_count}"
    )


def test_every_pvi_appears() -> None:
    """Sanity: 5 PVIs in the sample should produce at least 5
    [[vertical]] rows."""
    xml_path = SAMPLES / "samawah-line1.xml"
    produced = convert(xml_path, _meta())
    vertical_count = produced.count("[[vertical]]")
    assert vertical_count >= 5, f"expected ≥ 5 vertical rows, got {vertical_count}"


def test_every_station_appears() -> None:
    """Sanity: 3 stations in the sample."""
    xml_path = SAMPLES / "samawah-line1.xml"
    produced = convert(xml_path, _meta())
    station_count = produced.count("[[station]]")
    assert station_count == 3, f"expected exactly 3 station rows, got {station_count}"
    assert produced.count("platform_length_m = 61.000") == 3


def test_station_platform_default_can_be_overridden() -> None:
    """Civil packages may safeguard a longer local platform."""
    xml_path = SAMPLES / "samawah-line1.xml"
    produced = convert(xml_path, _meta(), platform_length_default_m=75.0)
    assert produced.count("platform_length_m = 75.000") == 3


def test_civil_placeholder_covers_full_length() -> None:
    """The converter emits an at-grade civil placeholder covering
    the full alignment length. The sample is 3000 m."""
    xml_path = SAMPLES / "samawah-line1.xml"
    produced = convert(xml_path, _meta())
    assert "to_station_m   = 3000.000" in produced
    assert 'class          = "at-grade"' in produced
