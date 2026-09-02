"""Tests for the surveyed-ground-model receipt and inspection gate."""

from __future__ import annotations

import csv
import hashlib
import json
import sqlite3
from pathlib import Path

from engineering.analysis import ground_model


FIELDS = [
    "dataset_id",
    "file_role",
    "package_revision",
    "file_path",
    "sha256",
    "capture_date",
    "coordinate_system",
    "vertical_datum",
    "producer",
    "checker",
    "acceptance_status",
]


def write_manifest(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def manifest_row(dataset: str, role: str, path: Path, root: Path, status: str = "checked") -> dict[str, str]:
    return {
        "dataset_id": dataset,
        "file_role": role,
        "package_revision": "A",
        "file_path": path.relative_to(root).as_posix(),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "capture_date": "2026-09-02",
        "coordinate_system": "EPSG:32638",
        "vertical_datum": "Iraq-project-datum-test",
        "producer": "test survey team",
        "checker": "independent test checker",
        "acceptance_status": status,
    }


def create_geopackage(path: Path) -> None:
    connection = sqlite3.connect(path)
    connection.execute("PRAGMA application_id=1196444487")
    connection.execute(
        "CREATE TABLE gpkg_spatial_ref_sys (srs_name TEXT NOT NULL, srs_id INTEGER PRIMARY KEY, organization TEXT NOT NULL, organization_coordsys_id INTEGER NOT NULL, definition TEXT NOT NULL, description TEXT)"
    )
    connection.execute(
        "CREATE TABLE gpkg_contents (table_name TEXT PRIMARY KEY, data_type TEXT NOT NULL, identifier TEXT UNIQUE, description TEXT DEFAULT '', last_change DATETIME, min_x DOUBLE, min_y DOUBLE, max_x DOUBLE, max_y DOUBLE, srs_id INTEGER)"
    )
    connection.execute(
        "CREATE TABLE gpkg_geometry_columns (table_name TEXT NOT NULL, column_name TEXT NOT NULL, geometry_type_name TEXT NOT NULL, srs_id INTEGER NOT NULL, z TINYINT NOT NULL, m TINYINT NOT NULL)"
    )
    connection.execute(
        "INSERT INTO gpkg_spatial_ref_sys VALUES ('WGS 84 / UTM zone 38N',32638,'EPSG',32638,'test definition','test only')"
    )
    connection.execute("CREATE TABLE surveyed_features (fid INTEGER PRIMARY KEY)")
    connection.execute(
        "INSERT INTO gpkg_contents(table_name,data_type,identifier,srs_id) VALUES ('surveyed_features','features','surveyed_features',32638)"
    )
    connection.execute(
        "INSERT INTO gpkg_geometry_columns VALUES ('surveyed_features','geom','GEOMETRY',32638,1,0)"
    )
    connection.commit()
    connection.close()


def test_empty_shared_manifest_is_valid_and_awaits_ground_data(tmp_path: Path) -> None:
    manifest = tmp_path / "manifest.csv"
    write_manifest(manifest, [{"dataset_id": "SUR-TOPO", "acceptance_status": "not-received"}])

    report = ground_model.build_report("test-city", manifest, tmp_path)

    assert report["report_valid"] is True
    assert report["status"] == "awaiting-ground-model-data"
    assert report["technical_screen_passed"] is False
    assert report["authority_accepted"] is False
    assert len(report["missing_technical_roles"]) == 10


def test_complete_checked_fixture_passes_screen_and_explicit_acceptance(tmp_path: Path) -> None:
    requirements = ground_model.read_requirements()
    inputs = {(item["dataset_id"], item["file_role"]): item for item in requirements["input"]}
    files: dict[tuple[str, str], Path] = {}
    for key, specification in inputs.items():
        extension = specification["extensions"][0]
        path = tmp_path / f"{key[1]}{extension}"
        files[key] = path
        if extension == ".gpkg":
            create_geopackage(path)
        elif key[1] in {"terrain_dtm", "orthophoto"}:
            path.write_bytes(b"II*\x00" + b"test-geotiff")
        elif key[1] == "registered_point_cloud":
            path.write_bytes(b"ASTM-E57" + b"test-cloud")
        elif key[1] == "checkpoint_residuals":
            with path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.writer(handle, lineterminator="\n")
                writer.writerow(["point_id", "role", "horizontal_residual_m", "vertical_residual_m"])
                for index in range(10):
                    writer.writerow([f"CP-{index + 1:02d}", "independent-check", "0.010", "0.012"])
        elif key[1] in {"odm_processing_report", "cloudcompare_qa_report"}:
            path.write_text(
                json.dumps(
                    {
                        "status": "success",
                        "tool": "OpenDroneMap" if key[1].startswith("odm") else "CloudCompare",
                        "version": "test-version",
                        "capture_epoch": "2026-09-02",
                        "coordinate_system": "EPSG:32638",
                        "vertical_datum": "Iraq-project-datum-test",
                        "uncertainty_model": "test-only independent checkpoints",
                        "source_hashes": {"test": "a" * 64},
                        "settings": {"quality": "test"},
                        "output_hashes": {"test": "b" * 64},
                    }
                ),
                encoding="utf-8",
            )
        elif key[1] == "control_acceptance_report":
            path.write_text(json.dumps({"authority_accepted": True}), encoding="utf-8")
        elif key[1] == "ground_model_acceptance_record":
            path.write_text(
                json.dumps(
                    {
                        "decision": "accepted",
                        "authority_name": "test authority",
                        "authority_role": "appointed survey authority",
                        "information_manager": "test information manager",
                        "signed_at": "2026-09-02T12:00:00Z",
                        "document_revision": "A",
                        "approved_horizontal_crs": "EPSG:32638",
                        "approved_vertical_datum": "Iraq-project-datum-test",
                        "controlled_record_reference": "TEST-ONLY",
                    }
                ),
                encoding="utf-8",
            )
        else:
            path.write_text(
                "area_id,status,reason,design_impact,owner\nnone,closed,none,none,test\n",
                encoding="utf-8",
            )
    rows = [
        manifest_row(dataset, role, path, tmp_path, "accepted" if role == "ground_model_acceptance_record" else "checked")
        for (dataset, role), path in files.items()
    ]
    manifest = tmp_path / "manifest.csv"
    write_manifest(manifest, rows)

    report = ground_model.build_report("test-city", manifest, tmp_path, inspect=True)

    assert report["receipt_findings"] == []
    assert report["inspection_findings"] == []
    assert report["inspection"]["checkpoints"] == {
        "independent_checkpoint_count": 10,
        "horizontal_rmse_m": 0.01,
        "vertical_rmse_m": 0.012,
    }
    assert report["technical_screen_passed"] is True
    assert report["authority_accepted"] is True
    assert report["status"] == "authority-accepted"


def test_bad_hash_and_symlink_escape_fail_closed(tmp_path: Path) -> None:
    root = tmp_path / "controlled"
    root.mkdir()
    outside = tmp_path / "outside.gpkg"
    outside.write_bytes(b"not-a-package")
    linked = root / "topography.gpkg"
    linked.symlink_to(outside)
    row = manifest_row("SUR-TOPO", "topographic_features", linked, root)
    row["sha256"] = "0" * 64
    manifest = tmp_path / "manifest.csv"
    write_manifest(manifest, [row])

    report = ground_model.build_report("test-city", manifest, root)

    assert report["status"] == "blocked-invalid-receipt"
    assert any("outside the evidence root" in item for item in report["receipt_findings"])
