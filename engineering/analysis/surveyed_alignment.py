#!/usr/bin/env python3
"""Gate surveyed per-line OSR-ALN, LandXML and civil-interface evidence."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
import tomllib
from pathlib import Path, PurePosixPath
from typing import Any

try:
    from engineering.analysis import survey_control
except ModuleNotFoundError:
    import survey_control  # type: ignore[no-redef]


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REQUIREMENTS = REPO_ROOT / "lib/templates/surveyed-alignment-processing.toml"
CONVERTER_SRC = REPO_ROOT / "tools/osr-aln-convert/src"
if str(CONVERTER_SRC) not in sys.path:
    sys.path.insert(0, str(CONVERTER_SRC))

from osr_aln.landxml_to_osr_aln import Meta, convert  # noqa: E402
from osr_aln.validate import validate  # noqa: E402


FIELDS = [
    "line_id", "file_role", "package_revision", "file_path", "sha256",
    "capture_date", "coordinate_system", "vertical_datum", "producer",
    "checker", "acceptance_status",
]


def load_design(path: Path) -> tuple[str, list[dict[str, Any]], list[dict[str, Any]]]:
    data = json.loads(path.read_text()) if path.suffix.lower() == ".json" else tomllib.loads(path.read_text())
    snapshot = "project" in data
    city = data.get("project", {}) if snapshot else data.get("city", {})
    slug = str(city.get("slug", "")).strip()
    lines = list(data.get("lines", []))
    stations = list(data.get("stations", []))
    if not slug or not lines or not stations:
        raise ValueError(f"{path}: design must contain city/project slug, lines and stations")
    normalised_lines = [
        {
            "id": str(line.get("id" if snapshot else "name", "")),
            "preset": str(line.get("geometry", "standard-urban")),
            "consist": str(line.get("rolling_stock", "light-metro-3car")),
        }
        for line in lines
    ]
    if any(not line["id"] for line in normalised_lines):
        raise ValueError(f"{path}: line id/name is missing")
    return slug, normalised_lines, stations


def read_requirements(path: Path = DEFAULT_REQUIREMENTS) -> dict[str, Any]:
    return tomllib.loads(path.read_text(encoding="utf-8"))


def expected_keys(lines: list[dict[str, Any]], requirements: dict[str, Any]) -> list[tuple[str, str]]:
    keys = [("*", str(item["file_role"])) for item in requirements["global_input"]]
    keys.extend(
        (line["id"], str(item["file_role"]))
        for line in lines
        for item in requirements["line_input"]
    )
    return keys


def write_placeholder_manifest(path: Path, lines: list[dict[str, Any]], requirements: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        for line_id, role in expected_keys(lines, requirements):
            writer.writerow({"line_id": line_id, "file_role": role, "acceptance_status": "not-received"})


def _specifications(requirements: dict[str, Any]) -> dict[tuple[str, str], dict[str, Any]]:
    result = {("*", str(item["file_role"])): item for item in requirements["global_input"]}
    result.update({("line", str(item["file_role"])): item for item in requirements["line_input"]})
    return result


def validate_receipt(
    manifest_path: Path,
    evidence_root: Path,
    lines: list[dict[str, Any]],
    requirements: dict[str, Any],
) -> tuple[dict[tuple[str, str], list[dict[str, str]]], list[str]]:
    expected = expected_keys(lines, requirements)
    received = {key: [] for key in expected}
    line_ids = {line["id"] for line in lines}
    specs = _specifications(requirements)
    findings: list[str] = []
    root = evidence_root.resolve()
    required_metadata = set(requirements["receipt"]["required_metadata_fields"])
    allowed_statuses = set(requirements["receipt"]["allowed_acceptance_statuses"])
    with manifest_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        required_columns = {"line_id", "file_role", *required_metadata}
        missing_columns = sorted(required_columns - set(reader.fieldnames or []))
        if missing_columns:
            return received, [f"manifest missing columns: {', '.join(missing_columns)}"]
        for number, row in enumerate(reader, start=2):
            line_id = row.get("line_id", "").strip()
            role = row.get("file_role", "").strip()
            path_value = row.get("file_path", "").strip()
            key = (line_id, role)
            if not path_value and key in received:
                continue
            specification = specs.get(("*", role) if line_id == "*" else ("line", role))
            if specification is None or (line_id != "*" and line_id not in line_ids):
                findings.append(f"manifest row {number}: unexpected line/role {line_id!r}/{role!r}")
                continue
            if key not in received:
                findings.append(f"manifest row {number}: unexpected global or per-line role")
                continue
            label = f"manifest row {number}"
            try:
                relative = survey_control.safe_relative_path(path_value)
            except ValueError as exc:
                findings.append(f"{label}: {exc}")
                continue
            if relative is None:
                findings.append(f"{label}: file_path is required")
                continue
            suffixes = tuple(str(item).lower() for item in specification["extensions"])
            if not relative.as_posix().lower().endswith(suffixes):
                findings.append(f"{label}: {role} has an unsupported extension")
            digest = row.get("sha256", "").strip().lower()
            if not survey_control.SHA256_RE.fullmatch(digest):
                findings.append(f"{label}: sha256 must contain 64 lowercase hexadecimal characters")
            absent = sorted(field for field in required_metadata if not row.get(field, "").strip())
            if absent:
                findings.append(f"{label}: missing metadata: {', '.join(absent)}")
            if row.get("acceptance_status", "").strip() not in allowed_statuses:
                findings.append(f"{label}: unsupported acceptance_status")
            source = root.joinpath(*relative.parts).resolve(strict=False)
            if not source.is_relative_to(root):
                findings.append(f"{label}: received file resolves outside the evidence root")
            elif not source.is_file():
                findings.append(f"{label}: received file is missing from controlled storage")
            elif survey_control.SHA256_RE.fullmatch(digest) and survey_control.sha256(source) != digest:
                findings.append(f"{label}: sha256 does not match received file")
            received[key].append({**row, "file_path": relative.as_posix(), "sha256": digest})
    return received, findings


def _path(rows: dict[tuple[str, str], list[dict[str, str]]], key: tuple[str, str], root: Path) -> Path:
    relative = PurePosixPath(rows[key][0]["file_path"])
    return root.joinpath(*relative.parts)


def inspect_alignment(
    path: Path,
    line: dict[str, Any],
    stations: list[dict[str, Any]],
    receipt_row: dict[str, str],
    known_line_ids: set[str],
) -> tuple[dict[str, Any], list[str]]:
    doc = tomllib.loads(path.read_text(encoding="utf-8"))
    expected_stations = {str(item["id"]) for item in stations if item.get("line") == line["id"]}
    validation = validate(doc, known_station_ids=expected_stations, known_line_ids=known_line_ids)
    meta = doc.get("meta", {})
    findings = list(validation.errors)
    source_status = str(meta.get("source_status", "")).lower()
    if "survey" not in source_status or "planning" in source_status or "unsurveyed" in source_status:
        findings.append("meta.source_status does not identify accepted survey-fitted geometry")
    if str(meta.get("surveyor", "")).lower() in {"", "unknown", "unsurveyed"} or "unsurveyed" in str(meta.get("surveyor", "")).lower():
        findings.append("meta.surveyor does not identify the survey producer")
    if meta.get("crs") != receipt_row.get("coordinate_system"):
        findings.append("OSR-ALN CRS does not match receipt")
    horizontal = list(doc.get("horizontal", []))
    vertical = list(doc.get("vertical", []))
    cant = list(doc.get("cant", []))
    if len(horizontal) < 2:
        findings.append("horizontal alignment has fewer than two elements")
    if len(vertical) < 2:
        findings.append("vertical profile has fewer than two elements")
    if not cant:
        findings.append("cant schedule is absent")
    for name, elements in (("horizontal", horizontal), ("vertical", vertical), ("cant", cant)):
        chainages = [float(item.get("station_m", item.get("from_station_m", -1))) for item in elements]
        if chainages != sorted(chainages) or any(value < 0 for value in chainages):
            findings.append(f"{name} chainage is negative or not monotonic")
    actual_stations = {str(item.get("id", "")) for item in doc.get("station", [])}
    if actual_stations != expected_stations:
        findings.append("OSR-ALN station set does not exactly match the selected design line")
    return {
        "horizontal_element_count": len(horizontal),
        "vertical_element_count": len(vertical),
        "cant_element_count": len(cant),
        "station_count": len(actual_stations),
        "warnings": validation.warnings,
    }, findings


def inspect_roundtrip(
    report_path: Path,
    xml_path: Path,
    alignment_path: Path,
    line: dict[str, Any],
    requirements: dict[str, Any],
) -> tuple[dict[str, Any], list[str]]:
    value = json.loads(report_path.read_text(encoding="utf-8"))
    required = requirements["roundtrip_report"]["required_fields"]
    findings = [f"round-trip report missing {field}" for field in required if value.get(field) in (None, "")]
    if value.get("status") != requirements["roundtrip_report"]["accepted_status"]:
        findings.append("round-trip report status is not passed")
    source_doc = tomllib.loads(alignment_path.read_text(encoding="utf-8"))
    meta = source_doc.get("meta", {})
    emitted = convert(
        xml_path,
        Meta(
            line_id=line["id"], preset=str(meta.get("preset", line["preset"])),
            consist=str(meta.get("consist", line["consist"])), crs=str(meta.get("crs", "")),
            surveyor=str(meta.get("surveyor", "unknown")), design_date=str(meta.get("design_date", "1970-01-01")),
            is_ring=bool(meta.get("is_ring", False)),
        ),
    )
    expected_hashes = {
        "source_osr_aln_sha256": survey_control.sha256(alignment_path),
        "landxml_sha256": survey_control.sha256(xml_path),
        "reimported_osr_aln_sha256": hashlib.sha256(emitted.encode()).hexdigest(),
    }
    for field, digest in expected_hashes.items():
        if value.get(field) != digest:
            findings.append(f"round-trip report {field} does not match inspected content")
    limits = requirements["technical_screen"]
    for field, limit_key in (
        ("maximum_horizontal_delta_m", "maximum_horizontal_roundtrip_delta_m"),
        ("maximum_vertical_delta_m", "maximum_vertical_roundtrip_delta_m"),
        ("maximum_chainage_delta_m", "maximum_chainage_roundtrip_delta_m"),
    ):
        try:
            if float(value[field]) > float(limits[limit_key]):
                findings.append(f"{field} exceeds the provisional limit")
        except (KeyError, TypeError, ValueError):
            findings.append(f"{field} is not numeric")
    for field in ("station_count_match", "element_count_match"):
        if value.get(field) is not True:
            findings.append(f"{field} is not true")
    return {field: value.get(field) for field in required}, findings


def inspect_interfaces(
    path: Path,
    lines: list[dict[str, Any]],
    stations: list[dict[str, Any]],
    alignment_hashes: dict[str, str],
    crs: str,
    vertical_datum: str,
    requirements: dict[str, Any],
) -> list[str]:
    value = json.loads(path.read_text(encoding="utf-8"))
    findings: list[str] = []
    for field in requirements["interface_report"]["required_fields"]:
        if value.get(field) in (None, "", [], {}):
            findings.append(f"interface report missing {field}")
    if value.get("status") != requirements["interface_report"]["accepted_status"]:
        findings.append("interface report status is not passed")
    if value.get("coordinate_system") != crs or value.get("vertical_datum") != vertical_datum:
        findings.append("interface report CRS or vertical datum does not match the receipt")
    if value.get("alignment_hashes") != alignment_hashes:
        findings.append("interface report alignment hashes do not match received OSR-ALN files")
    expected_lines = {line["id"] for line in lines}
    interfaces = {str(item.get("line_id", "")): item for item in value.get("line_interfaces", [])}
    if set(interfaces) != expected_lines:
        findings.append("interface report does not contain exactly one row per design line")
    expected_stations = {line_id: {str(s["id"]) for s in stations if s.get("line") == line_id} for line_id in expected_lines}
    limits = requirements["technical_screen"]
    for line_id, item in interfaces.items():
        for status_field in ("yard_interface_status", "turnout_interface_status", "clearance_status"):
            if item.get(status_field) != "passed":
                findings.append(f"{line_id}: {status_field} is not passed")
        platforms = item.get("platforms", [])
        if {str(platform.get("station_id", "")) for platform in platforms} != expected_stations.get(line_id, set()):
            findings.append(f"{line_id}: platform interfaces do not match design stations")
        for platform in platforms:
            try:
                if abs(float(platform["horizontal_offset_m"])) > float(limits["maximum_platform_horizontal_offset_m"]):
                    findings.append(f"{line_id}/{platform.get('station_id')}: platform horizontal offset exceeds limit")
                if abs(float(platform["vertical_offset_m"])) > float(limits["maximum_platform_vertical_offset_m"]):
                    findings.append(f"{line_id}/{platform.get('station_id')}: platform vertical offset exceeds limit")
            except (KeyError, TypeError, ValueError):
                findings.append(f"{line_id}/{platform.get('station_id')}: platform offsets are not numeric")
    return findings


def build_report(
    design_path: Path,
    manifest_path: Path,
    evidence_root: Path,
    requirements_path: Path = DEFAULT_REQUIREMENTS,
    inspect: bool = False,
) -> dict[str, Any]:
    city, lines, stations = load_design(design_path)
    requirements = read_requirements(requirements_path)
    received, receipt_findings = validate_receipt(manifest_path, evidence_root, lines, requirements)
    missing = [f"{line_id}:{role}" for (line_id, role), rows in received.items() if not rows and role != "alignment_acceptance_record"]
    duplicates = [f"{line_id}:{role}" for (line_id, role), rows in received.items() if len(rows) > 1]
    unreviewed = [f"{line_id}:{role}" for (line_id, role), rows in received.items() if rows and role != "alignment_acceptance_record" and rows[0].get("acceptance_status") not in {"checked", "accepted"}]
    inspection: dict[str, Any] = {}
    findings: list[str] = []
    technical_keys = [key for key in received if key[1] != "alignment_acceptance_record"]
    can_inspect = inspect and not receipt_findings and not missing and not duplicates
    alignment_hashes: dict[str, str] = {}
    crs_values = {received[key][0]["coordinate_system"] for key in technical_keys if received[key]}
    datum_values = {received[key][0]["vertical_datum"] for key in technical_keys if received[key]}
    if can_inspect:
        if unreviewed:
            findings.append("technical inputs are not checked or accepted: " + ", ".join(unreviewed))
        if len(crs_values) != 1 or len(datum_values) != 1:
            findings.append("technical inputs do not share one CRS and vertical datum")
        ground = json.loads(_path(received, ("*", "ground_model_readiness"), evidence_root).read_text())
        if ground.get("authority_accepted") is not True:
            findings.append("surveyed ground model is not authority accepted")
        for line in lines:
            line_id = line["id"]
            aln_path = _path(received, (line_id, "surveyed_osr_aln"), evidence_root)
            alignment_hashes[line_id] = survey_control.sha256(aln_path)
            summary, line_findings = inspect_alignment(
                aln_path, line, stations, received[(line_id, "surveyed_osr_aln")][0], {item["id"] for item in lines}
            )
            roundtrip, roundtrip_findings = inspect_roundtrip(
                _path(received, (line_id, "landxml_roundtrip_report"), evidence_root),
                _path(received, (line_id, "landxml_export"), evidence_root),
                aln_path, line, requirements,
            )
            inspection[line_id] = {"alignment": summary, "roundtrip": roundtrip}
            findings.extend(f"{line_id}: {item}" for item in line_findings + roundtrip_findings)
        if len(crs_values) == 1 and len(datum_values) == 1:
            findings.extend(inspect_interfaces(
                _path(received, ("*", "interface_verification_report"), evidence_root),
                lines, stations, alignment_hashes, next(iter(crs_values)), next(iter(datum_values)), requirements,
            ))
    technical_passed = bool(can_inspect and not findings)
    authority_findings = ["alignment acceptance record not received"]
    acceptance_rows = received[("*", "alignment_acceptance_record")]
    if acceptance_rows and not receipt_findings:
        value = json.loads(_path(received, ("*", "alignment_acceptance_record"), evidence_root).read_text())
        authority_findings = [f"alignment acceptance record missing {field}" for field in requirements["authority_record"]["required_fields"] if value.get(field) in (None, "", {})]
        if value.get("decision") != requirements["authority_record"]["accepted_decision"]:
            authority_findings.append("alignment acceptance decision is not accepted")
        if acceptance_rows[0].get("acceptance_status") != "accepted":
            authority_findings.append("alignment acceptance manifest row is not accepted")
        if technical_passed and value.get("approved_alignment_hashes") != alignment_hashes:
            authority_findings.append("approved alignment hashes do not match inspected files")
        if len(crs_values) == 1 and value.get("approved_horizontal_crs") != next(iter(crs_values)):
            authority_findings.append("approved CRS does not match inspected files")
        if len(datum_values) == 1 and value.get("approved_vertical_datum") != next(iter(datum_values)):
            authority_findings.append("approved vertical datum does not match inspected files")
    authority_accepted = bool(technical_passed and not authority_findings)
    if receipt_findings:
        status = "blocked-invalid-receipt"
    elif missing:
        status = "awaiting-surveyed-alignments"
    elif duplicates:
        status = "blocked-duplicate-role"
    elif not inspect:
        status = "ready-for-inspection"
    elif findings:
        status = "technical-screen-failed"
    elif not authority_accepted:
        status = "technical-screen-passed-awaiting-authority"
    else:
        status = "authority-accepted"
    return {
        "schema_version": "1.0", "analysis_id": f"OSR-SURVEYED-ALIGNMENT:{city}", "city": city,
        "status": status, "report_valid": not receipt_findings, "line_ids": [line["id"] for line in lines],
        "receipt_findings": receipt_findings, "missing_technical_roles": missing, "duplicate_roles": duplicates,
        "unreviewed_technical_roles": unreviewed, "inspection_requested": inspect,
        "inspection_completed": can_inspect, "inspection": inspection, "inspection_findings": findings,
        "technical_screen_passed": technical_passed, "authority_record_findings": authority_findings,
        "authority_accepted": authority_accepted, "alignment_hashes": alignment_hashes,
        "requirements_source": survey_control.display_path(requirements_path),
        "requirements_sha256": survey_control.sha256(requirements_path),
        "design_source": survey_control.display_path(design_path), "design_sha256": survey_control.sha256(design_path),
        "receipt_manifest_sha256": survey_control.sha256(manifest_path),
        "osr_aln_validator_sha256": survey_control.sha256(CONVERTER_SRC / "osr_aln/validate.py"),
        "landxml_converter_sha256": survey_control.sha256(CONVERTER_SRC / "osr_aln/landxml_to_osr_aln.py"),
        "generator_sha256": survey_control.sha256(Path(__file__)),
        "controlled_storage_policy": requirements["controlled_storage_policy"],
        "technical_boundary": requirements["technical_boundary"], "acceptance_boundary": requirements["acceptance_boundary"],
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        f"# {report['city'].title()} surveyed-alignment gate", "",
        f"- Status: **{report['status']}**",
        f"- Lines expected: {', '.join(report['line_ids'])}",
        f"- Technical screen passed: **{'yes' if report['technical_screen_passed'] else 'no'}**",
        f"- Authority accepted: **{'yes' if report['authority_accepted'] else 'no'}**", "",
        "> " + report["technical_boundary"], "", "> " + report["acceptance_boundary"], "",
        "## Current gates", "",
        f"- Missing technical roles: {', '.join(report['missing_technical_roles']) or 'none'}",
        f"- Duplicate roles: {', '.join(report['duplicate_roles']) or 'none'}",
    ]
    for title, values in (("Receipt findings", report["receipt_findings"]), ("Inspection findings", report["inspection_findings"]), ("Authority findings", report["authority_record_findings"])):
        if values:
            lines.extend([f"- {title}:", *[f"  - {item}" for item in values]])
    lines.extend(["", "## Controlled workflow", "", report["controlled_storage_policy"], "",
        "1. Accept survey control and the surveyed ground model.",
        "2. Fit each line in the confirmed CRS/datum; explicitly issue horizontal, vertical and cant schedules.",
        "3. Export one OSR-ALN and LandXML file per line and record the deterministic re-import hash and comparison tolerances.",
        "4. Reconcile every platform and record yard, turnout and clearance dispositions per line.",
        "5. Run this inspection and obtain the controlled multi-discipline acceptance record.", ""])
    return "\n".join(lines)


def generate(design_path: Path, manifest_path: Path, evidence_root: Path, output_dir: Path, requirements_path: Path = DEFAULT_REQUIREMENTS, inspect: bool = False) -> dict[str, Any]:
    report = build_report(design_path.resolve(), manifest_path.resolve(), evidence_root.resolve(), requirements_path.resolve(), inspect)
    output_dir.mkdir(parents=True, exist_ok=True)
    survey_control.atomic_json(output_dir / "surveyed-alignment-readiness.json", report)
    (output_dir / "surveyed-alignment-readiness.md").write_text(render_markdown(report), encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--design", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--evidence-root", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--requirements", type=Path, default=DEFAULT_REQUIREMENTS)
    parser.add_argument("--write-placeholder-manifest", action="store_true")
    parser.add_argument("--inspect", action="store_true")
    parser.add_argument("--require-technical-screen", action="store_true")
    args = parser.parse_args()
    _, lines, _ = load_design(args.design)
    if args.write_placeholder_manifest:
        write_placeholder_manifest(args.manifest, lines, read_requirements(args.requirements))
    report = generate(args.design, args.manifest, args.evidence_root, args.output_dir, args.requirements, args.inspect)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 1 if not report["report_valid"] or (args.require_technical_screen and not report["technical_screen_passed"]) else 0


if __name__ == "__main__":
    raise SystemExit(main())
