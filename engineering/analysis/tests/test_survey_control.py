"""Tests for the fail-closed survey-control processing gate."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

from engineering.analysis import survey_control


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


def row(role: str, path: Path, root: Path) -> dict[str, str]:
    return {
        "dataset_id": "SUR-CTRL",
        "file_role": role,
        "package_revision": "A",
        "file_path": path.relative_to(root).as_posix(),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "capture_date": "2026-09-02",
        "coordinate_system": "ITRF2020",
        "vertical_datum": "authority-review-pending",
        "producer": "test survey team",
        "checker": "independent test checker",
        "acceptance_status": "received",
    }


def test_empty_manifest_is_valid_but_awaiting_field_data(tmp_path: Path) -> None:
    manifest = tmp_path / "manifest.csv"
    write_manifest(
        manifest,
        [{"dataset_id": "SUR-CTRL", "acceptance_status": "not-received"}],
    )

    report = survey_control.build_report(
        "test-city", manifest, tmp_path, tmp_path / "output"
    )

    assert report["report_valid"] is True
    assert report["status"] == "awaiting-field-data"
    assert report["processing_completed"] is False
    assert report["solver_available"] is None
    assert report["technical_screen_passed"] is False
    assert report["authority_accepted"] is False
    assert set(report["missing_processing_roles"]) == {
        "rover_observation",
        "base_observation",
        "navigation",
        "rtklib_configuration",
    }


def test_receipt_rejects_path_traversal(tmp_path: Path) -> None:
    manifest = tmp_path / "manifest.csv"
    unsafe = {field: "value" for field in FIELDS}
    unsafe.update(
        dataset_id="SUR-CTRL",
        file_role="rover_observation",
        file_path="../outside.obs",
        sha256="0" * 64,
    )
    write_manifest(manifest, [unsafe])

    report = survey_control.build_report(
        "test-city", manifest, tmp_path, tmp_path / "output"
    )

    assert report["status"] == "blocked-invalid-receipt"
    assert any("relative to the evidence root" in item for item in report["receipt_findings"])


def test_receipt_detects_hash_mismatch(tmp_path: Path) -> None:
    observation = tmp_path / "rover.obs"
    observation.write_text("RINEX test fixture", encoding="utf-8")
    received = row("rover_observation", observation, tmp_path)
    received["sha256"] = "0" * 64
    manifest = tmp_path / "manifest.csv"
    write_manifest(manifest, [received])

    report = survey_control.build_report(
        "test-city", manifest, tmp_path, tmp_path / "output"
    )

    assert report["status"] == "blocked-invalid-receipt"
    assert any("sha256 does not match" in item for item in report["receipt_findings"])


def test_receipt_accepts_classic_rinex_suffix_and_rejects_symlink_escape(tmp_path: Path) -> None:
    requirements = survey_control.read_requirements()
    rover_role = next(
        item for item in requirements["file_role"] if item["id"] == "rover_observation"
    )
    assert survey_control.extension_supported("session/BASE1230.24o", rover_role)

    root = tmp_path / "controlled"
    root.mkdir()
    outside = tmp_path / "outside.obs"
    outside.write_text("outside", encoding="utf-8")
    linked = root / "linked.obs"
    linked.symlink_to(outside)
    manifest = tmp_path / "manifest.csv"
    write_manifest(manifest, [row("rover_observation", linked, root)])

    report = survey_control.build_report(
        "test-city", manifest, root, tmp_path / "output"
    )

    assert report["status"] == "blocked-invalid-receipt"
    assert any("outside the evidence root" in item for item in report["receipt_findings"])


def test_rtklib_solution_quality_is_parsed_and_screened(tmp_path: Path) -> None:
    root = tmp_path / "controlled"
    root.mkdir()
    files = {
        "rover_observation": root / "rover.obs",
        "base_observation": root / "base.obs",
        "navigation": root / "navigation.nav",
        "rtklib_configuration": root / "processing.conf",
    }
    for path in files.values():
        path.write_text("controlled test input\n", encoding="utf-8")
    files["rtklib_configuration"].write_text(
        "pos1-posmode=static\n"
        "pos1-soltype=combined\n"
        "out-solformat=llh\n"
        "out-timeform=hms\n"
        "out-degform=deg\n"
        "out-solstatic=all\n"
        "out-outstat=residual\n",
        encoding="utf-8",
    )
    manifest = tmp_path / "manifest.csv"
    write_manifest(manifest, [row(role, path, root) for role, path in files.items()])

    solver = tmp_path / "fake-rnx2rtkp"
    solver.write_text(
        "#!/bin/sh\n"
        "while [ \"$1\" != \"-o\" ]; do shift; done\n"
        "shift\n"
        "out=$1\n"
        "i=0\n"
        ": > \"$out\"\n"
        "while [ $i -lt 60 ]; do "
        "printf '2026/09/02 00:00:00.000 31.0 45.0 20.0 1 12 0.001 0.001 0.002\\n' >> \"$out\"; "
        "i=$((i+1)); done\n",
        encoding="utf-8",
    )
    solver.chmod(0o755)

    report = survey_control.build_report(
        "test-city",
        manifest,
        root,
        tmp_path / "output",
        solver_path=solver,
        execute=True,
    )

    assert report["processing_completed"] is True
    assert report["processing"]["metrics"]["epoch_count"] == 60
    assert report["processing"]["metrics"]["fixed_fraction"] == 1.0
    assert set(report["processing"]["controlled_run_artifacts"]) == {
        "control-solution.pos",
        "rnx2rtkp.log",
    }
    assert report["technical_screen_passed"] is True
    assert report["authority_accepted"] is False
    assert report["status"] == "technical-screen-passed-awaiting-authority"


def test_complete_receipt_with_unfrozen_config_is_blocked(tmp_path: Path) -> None:
    root = tmp_path / "controlled"
    root.mkdir()
    files = {
        "rover_observation": root / "rover.obs",
        "base_observation": root / "base.obs",
        "navigation": root / "navigation.nav",
        "rtklib_configuration": root / "processing.conf",
    }
    for path in files.values():
        path.write_text("not a frozen configuration\n", encoding="utf-8")
    manifest = tmp_path / "manifest.csv"
    write_manifest(manifest, [row(role, path, root) for role, path in files.items()])

    report = survey_control.build_report(
        "test-city",
        manifest,
        root,
        tmp_path / "output",
        solver_path=tmp_path / "missing-rnx2rtkp",
        execute=True,
    )

    assert report["status"] == "blocked-invalid-processing-configuration"
    assert report["solver_available"] is False
    assert report["processing_configuration_findings"]
    assert report["processing_completed"] is False


def test_acceptance_needs_explicit_authority_record_and_all_review_files(tmp_path: Path) -> None:
    position = tmp_path / "solution.pos"
    position.write_text(
        "% GPST latitude longitude height Q ns\n"
        + "\n".join(
            "2026/09/02 00:00:00.000 31.0 45.0 20.0 1 12" for _ in range(60)
        ),
        encoding="utf-8",
    )
    parsed = survey_control.parse_rtklib_solution(position)
    assert parsed["quality_code_counts"] == {"1": 60}
    assert parsed["malformed_data_rows"] == 0

    acceptance = tmp_path / "acceptance.json"
    acceptance.write_text(json.dumps({"decision": "accepted"}), encoding="utf-8")
    valid, findings = survey_control.authority_record_valid(
        [{"file_path": acceptance.name, "acceptance_status": "accepted"}],
        tmp_path,
        survey_control.read_requirements(),
    )
    assert valid is False
    assert findings and "missing" in findings[0]
