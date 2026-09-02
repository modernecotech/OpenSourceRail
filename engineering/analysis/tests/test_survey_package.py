"""Tests for deterministic city field-evidence briefs."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from engineering.analysis import survey_package


REPO_ROOT = Path(__file__).resolve().parents[3]
SAMAWAH = REPO_ROOT / "cities/catalogue/west-asia/Iraq/Samawah/design.toml"


def test_samawah_brief_is_complete_but_does_not_claim_field_acceptance() -> None:
    report = survey_package.build_report(SAMAWAH)

    assert report["city"] == "samawah"
    assert report["dataset_count"] == 11
    assert report["candidate_horizontal_crs"].startswith("EPSG:32638")
    assert report["vertical_datum"] == "authority-to-confirm-before-mobilisation"
    assert report["brief_findings"] == []
    assert report["brief_ready_for_approval"] is True
    assert report["mobilisation_authorized"] is False
    assert report["field_evidence_accepted"] is False
    assert report["requirements_sha256"] == survey_package.sha256(
        survey_package.DEFAULT_REQUIREMENTS
    )
    assert report["project_input_kind"] == "catalogue-design"


def test_generated_brief_and_empty_receipt_manifest_are_deterministic(tmp_path: Path) -> None:
    first = survey_package.generate(SAMAWAH, tmp_path / "first")
    second = survey_package.generate(SAMAWAH, tmp_path / "second")

    for name in ("field-evidence-brief.json", "field-evidence-brief.md", "survey-input-manifest.csv"):
        assert (tmp_path / "first" / name).read_bytes() == (tmp_path / "second" / name).read_bytes()
    persisted = json.loads((tmp_path / "first/field-evidence-brief.json").read_text())
    assert persisted == first == second
    with (tmp_path / "first/survey-input-manifest.csv").open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == first["dataset_count"]
    assert {row["dataset_id"] for row in rows} == {
        dataset["id"] for dataset in first["datasets"]
    }
    assert all(row["acceptance_status"] == "not-received" for row in rows)
    assert all(not row["sha256"] and not row["file_path"] for row in rows)


def test_compiled_city_studio_snapshot_uses_current_station_centroid(tmp_path: Path) -> None:
    snapshot = {
        "project": {"slug": "changed-city", "country": "IQ"},
        "stations": [
            {"lat": 31.30, "lon": 45.20},
            {"lat": 31.32, "lon": 45.40},
        ],
    }
    path = tmp_path / "snapshot.json"
    path.write_text(json.dumps(snapshot), encoding="utf-8")
    report = survey_package.build_report(path)

    assert report["city"] == "changed-city"
    assert report["project_input_kind"] == "compiled-city-studio-snapshot"
    assert report["candidate_horizontal_crs"].startswith("EPSG:32638")
