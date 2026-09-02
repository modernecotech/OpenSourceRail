"""Tests for the surveyed-alignment receipt, interchange and authority gate."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

from engineering.analysis import surveyed_alignment
from osr_aln.landxml_to_osr_aln import Meta, convert


SAMPLE_DIR = surveyed_alignment.REPO_ROOT / "tools/osr-aln-convert/samples"


def design(path: Path) -> None:
    path.write_text(
        "[city]\nslug = \"test-city\"\n\n[[lines]]\nname = \"line-1\"\n"
        "geometry = \"standard-urban\"\nrolling_stock = \"light-metro-3car\"\n\n"
        "[[stations]]\nid = \"samawah-rws\"\nline = \"line-1\"\n\n"
        "[[stations]]\nid = \"north-gate\"\nline = \"line-1\"\n\n"
        "[[stations]]\nid = \"central-plaza\"\nline = \"line-1\"\n",
        encoding="utf-8",
    )


def add_file(row: dict[str, str], path: Path, root: Path, crs: str = "EPSG:32638") -> dict[str, str]:
    return {
        **row,
        "package_revision": "A",
        "file_path": path.relative_to(root).as_posix(),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "capture_date": "2026-09-02",
        "coordinate_system": crs,
        "vertical_datum": "test-project-datum",
        "producer": "test producer",
        "checker": "independent test checker",
        "acceptance_status": "checked",
    }


def write_rows(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=surveyed_alignment.FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def test_placeholder_manifest_is_deterministic_and_pending(tmp_path: Path) -> None:
    design_path = tmp_path / "design.toml"
    manifest = tmp_path / "manifest.csv"
    design(design_path)
    _, lines, _ = surveyed_alignment.load_design(design_path)
    requirements = surveyed_alignment.read_requirements()
    surveyed_alignment.write_placeholder_manifest(manifest, lines, requirements)
    first = manifest.read_bytes()
    surveyed_alignment.write_placeholder_manifest(manifest, lines, requirements)

    report = surveyed_alignment.build_report(design_path, manifest, tmp_path)

    assert manifest.read_bytes() == first
    assert report["status"] == "awaiting-surveyed-alignments"
    assert report["missing_technical_roles"] == [
        "*:ground_model_readiness", "*:interface_verification_report",
        "line-1:surveyed_osr_aln", "line-1:landxml_export", "line-1:landxml_roundtrip_report",
    ]
    assert report["technical_screen_passed"] is False
    assert report["authority_accepted"] is False


def test_complete_fixture_passes_only_with_explicit_authority_record(tmp_path: Path) -> None:
    design_path = tmp_path / "design.toml"
    design(design_path)
    xml_path = tmp_path / "line-1.landxml"
    xml_path.write_bytes((SAMPLE_DIR / "samawah-line1.xml").read_bytes())
    source = (SAMPLE_DIR / "samawah-line1.aln.toml").read_text()
    source = source.replace('line_id        = "samawah-line1"', 'line_id        = "line-1"')
    source = source.replace('surveyor       = "Samawah Civil Associates"', 'surveyor       = "Test Survey Partnership"')
    source = source.replace("[meta]\n", '[meta]\nsource_status  = "survey-fitted and checked"\n')
    source += "\n[[cant]]\nfrom_station_m = 0.0\nto_station_m = 3000.0\nmax_cant_mm = 0.0\ntransition_in_m = 0.0\ntransition_out_m = 0.0\n"
    aln_path = tmp_path / "line-1.aln.toml"
    aln_path.write_text(source)
    doc = __import__("tomllib").loads(source)
    meta = doc["meta"]
    reimported = convert(xml_path, Meta(
        line_id="line-1", preset=meta["preset"], consist=meta["consist"], crs=meta["crs"],
        surveyor=meta["surveyor"], design_date=meta["design_date"], is_ring=meta["is_ring"],
    ))
    roundtrip_path = tmp_path / "roundtrip.json"
    roundtrip_path.write_text(json.dumps({
        "status": "passed", "tool": "test comparison", "version": "1",
        "source_osr_aln_sha256": hashlib.sha256(aln_path.read_bytes()).hexdigest(),
        "landxml_sha256": hashlib.sha256(xml_path.read_bytes()).hexdigest(),
        "reimported_osr_aln_sha256": hashlib.sha256(reimported.encode()).hexdigest(),
        "maximum_horizontal_delta_m": 0.001, "maximum_vertical_delta_m": 0.001,
        "maximum_chainage_delta_m": 0.001, "station_count_match": True, "element_count_match": True,
    }))
    ground_path = tmp_path / "ground.json"
    ground_path.write_text(json.dumps({"authority_accepted": True}))
    aln_hash = hashlib.sha256(aln_path.read_bytes()).hexdigest()
    interface_path = tmp_path / "interfaces.json"
    interface_path.write_text(json.dumps({
        "status": "passed", "coordinate_system": "EPSG:32638", "vertical_datum": "test-project-datum",
        "alignment_hashes": {"line-1": aln_hash},
        "line_interfaces": [{
            "line_id": "line-1", "yard_interface_status": "passed", "turnout_interface_status": "passed",
            "clearance_status": "passed", "platforms": [
                {"station_id": station, "horizontal_offset_m": 0.005, "vertical_offset_m": 0.003}
                for station in ("samawah-rws", "north-gate", "central-plaza")
            ],
        }],
    }))
    acceptance_path = tmp_path / "acceptance.json"
    acceptance_path.write_text(json.dumps({
        "decision": "accepted", "alignment_designer": "test designer", "survey_authority": "test authority",
        "track_engineer": "test track engineer", "information_manager": "test manager",
        "signed_at": "2026-09-02T12:00:00Z", "document_revision": "A",
        "approved_horizontal_crs": "EPSG:32638", "approved_vertical_datum": "test-project-datum",
        "controlled_record_reference": "TEST-ONLY", "approved_alignment_hashes": {"line-1": aln_hash},
    }))
    rows = [
        add_file({"line_id": "*", "file_role": "ground_model_readiness"}, ground_path, tmp_path),
        add_file({"line_id": "*", "file_role": "interface_verification_report"}, interface_path, tmp_path),
        add_file({"line_id": "line-1", "file_role": "surveyed_osr_aln"}, aln_path, tmp_path),
        add_file({"line_id": "line-1", "file_role": "landxml_export"}, xml_path, tmp_path),
        add_file({"line_id": "line-1", "file_role": "landxml_roundtrip_report"}, roundtrip_path, tmp_path),
    ]
    manifest = tmp_path / "manifest.csv"
    write_rows(manifest, rows)
    pending = surveyed_alignment.build_report(design_path, manifest, tmp_path, inspect=True)
    assert pending["technical_screen_passed"] is True
    assert pending["status"] == "technical-screen-passed-awaiting-authority"
    acceptance_row = add_file({"line_id": "*", "file_role": "alignment_acceptance_record"}, acceptance_path, tmp_path)
    acceptance_row["acceptance_status"] = "accepted"
    write_rows(manifest, [*rows, acceptance_row])

    accepted = surveyed_alignment.build_report(design_path, manifest, tmp_path, inspect=True)

    assert accepted["inspection_findings"] == []
    assert accepted["technical_screen_passed"] is True
    assert accepted["authority_record_findings"] == []
    assert accepted["authority_accepted"] is True
    assert accepted["status"] == "authority-accepted"


def test_bad_hash_and_path_escape_fail_closed(tmp_path: Path) -> None:
    design_path = tmp_path / "design.toml"
    design(design_path)
    root = tmp_path / "controlled"
    root.mkdir()
    outside = tmp_path / "outside.json"
    outside.write_text("{}")
    link = root / "ground.json"
    link.symlink_to(outside)
    row = add_file({"line_id": "*", "file_role": "ground_model_readiness"}, link, root)
    row["sha256"] = "0" * 64
    manifest = tmp_path / "manifest.csv"
    write_rows(manifest, [row])

    report = surveyed_alignment.build_report(design_path, manifest, root)

    assert report["status"] == "blocked-invalid-receipt"
    assert any("outside the evidence root" in item for item in report["receipt_findings"])
