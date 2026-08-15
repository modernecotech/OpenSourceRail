"""Current generated-network → OSR-ALN export and drift tests."""

from __future__ import annotations

import tomllib
from pathlib import Path

import pytest

from osr_aln.current_network import _wgs84_to_utm, export_network, render_network
from osr_aln.validate import validate


REPO_ROOT = Path(__file__).resolve().parents[3]
SAMAWAH = REPO_ROOT / "designs/west-asia/Iraq/Samawah"
DESIGN = SAMAWAH / "design.toml"
GEOJSON = SAMAWAH / "samawah.corridor.geojson"
OUTPUT = SAMAWAH / "engineering/alignment"
DESIGN_DATE = "2026-08-12"


def _design() -> dict:
    with DESIGN.open("rb") as handle:
        return tomllib.load(handle)


def test_wgs84_projection_places_samawah_in_utm_zone_38n() -> None:
    easting, northing = _wgs84_to_utm(31.31, 45.28, 38)
    assert easting == pytest.approx(526_650, abs=250)
    assert northing == pytest.approx(3_464_000, abs=500)


def test_rendered_network_matches_every_design_line_station_and_civil_span() -> None:
    design = _design()
    rendered = render_network(DESIGN, GEOJSON, design_date=DESIGN_DATE)
    assert set(rendered) == {
        "samawah-line1.aln.toml",
        "samawah-line2.aln.toml",
        "samawah-line3.aln.toml",
    }

    known_stations = {station["id"] for station in design["stations"]}
    known_lines = {line["name"] for line in design["lines"]}
    seen_stations: set[str] = set()
    for content in rendered.values():
        doc = tomllib.loads(content)
        line_id = doc["meta"]["line_id"]
        assert line_id in known_lines
        assert doc["meta"]["source_status"].startswith("planning-only")
        assert doc["meta"]["vertical_status"].startswith("zero-datum")
        assert doc["meta"]["cant_status"].startswith("not designed")
        assert len(doc["horizontal"]) >= 2
        assert doc["horizontal"][-1]["station_m"] == pytest.approx(
            next(line["length_m"] for line in design["lines"] if line["name"] == line_id)
        )
        assert doc["civil"][0]["from_station_m"] == 0.0
        assert doc["civil"][-1]["to_station_m"] == doc["horizontal"][-1]["station_m"]
        report = validate(
            doc,
            known_station_ids=known_stations,
            known_line_ids=known_lines,
        )
        assert report.ok, report.format_text()
        seen_stations.update(station["id"] for station in doc["station"])
    assert seen_stations == known_stations


def test_checked_in_current_network_has_no_generator_drift() -> None:
    paths = export_network(
        DESIGN,
        GEOJSON,
        OUTPUT,
        design_date=DESIGN_DATE,
        check=True,
    )
    assert len(paths) == 4


def test_check_detects_drift(tmp_path: Path) -> None:
    export_network(DESIGN, GEOJSON, tmp_path, design_date=DESIGN_DATE)
    (tmp_path / "samawah-line2.aln.toml").write_text("stale\n")
    with pytest.raises(ValueError, match="drift"):
        export_network(
            DESIGN,
            GEOJSON,
            tmp_path,
            design_date=DESIGN_DATE,
            check=True,
        )
