#!/usr/bin/env python3
"""Generate a deterministic pre-mobilisation field-evidence brief for a city."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import tempfile
import tomllib
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REQUIREMENTS = REPO_ROOT / "lib/templates/field-evidence.toml"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def atomic_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", dir=path.parent, delete=False, encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
        temporary = Path(handle.name)
    os.replace(temporary, path)


def candidate_projected_crs(longitude: float, latitude: float) -> str:
    zone = min(60, max(1, int((longitude + 180.0) // 6.0) + 1))
    epsg = (32600 if latitude >= 0 else 32700) + zone
    return f"EPSG:{epsg} candidate UTM zone {zone}{'N' if latitude >= 0 else 'S'}; survey authority to confirm or replace"


def build_report(design_path: Path, requirements_path: Path = DEFAULT_REQUIREMENTS) -> dict[str, Any]:
    design_path = design_path.resolve()
    requirements_path = requirements_path.resolve()
    if design_path.suffix.lower() == ".json":
        design = json.loads(design_path.read_text(encoding="utf-8"))
    else:
        design = tomllib.loads(design_path.read_text(encoding="utf-8"))
    requirements = tomllib.loads(requirements_path.read_text(encoding="utf-8"))
    is_snapshot = "project" in design and "stations" in design
    city = design.get("project", {}) if is_snapshot else design.get("city", {})
    slug = str(city.get("slug", "")).strip()
    if not slug:
        raise ValueError(f"{design_path}: missing city.slug")
    datasets = list(requirements.get("dataset", []))
    required_fields = {
        "id", "title", "owner_role", "delivery_format", "scope",
        "provisional_accuracy", "acceptance_evidence",
    }
    findings: list[str] = []
    ids: list[str] = []
    for index, dataset in enumerate(datasets, start=1):
        missing = sorted(required_fields - set(dataset))
        if missing:
            findings.append(f"dataset {index} missing: {', '.join(missing)}")
        dataset_id = str(dataset.get("id", ""))
        if dataset_id in ids:
            findings.append(f"duplicate dataset id: {dataset_id}")
        ids.append(dataset_id)
        if not dataset.get("acceptance_evidence"):
            findings.append(f"{dataset_id or index}: acceptance evidence is empty")
    if is_snapshot:
        stations = list(design.get("stations", []))
        if not stations:
            raise ValueError(f"{design_path}: compiled snapshot has no stations")
        longitude = sum(float(station["lon"]) for station in stations) / len(stations)
        latitude = sum(float(station["lat"]) for station in stations) / len(stations)
    else:
        longitude = float(city.get("centroid_lon", 0.0))
        latitude = float(city.get("centroid_lat", 0.0))
    return {
        "analysis_id": f"OSR-FIELD-EVIDENCE:{slug}",
        "city": slug,
        "country": city.get("country"),
        "candidate_horizontal_crs": candidate_projected_crs(longitude, latitude),
        "vertical_datum": "authority-to-confirm-before-mobilisation",
        "requirements_source": display_path(requirements_path),
        "requirements_sha256": sha256(requirements_path),
        "project_input_kind": "compiled-city-studio-snapshot" if is_snapshot else "catalogue-design",
        "project_input": display_path(design_path),
        "project_input_sha256": sha256(design_path),
        "generator_sha256": sha256(Path(__file__)),
        "dataset_count": len(datasets),
        "datasets": datasets,
        "brief_findings": findings,
        "brief_ready_for_approval": bool(datasets and not findings),
        "mobilisation_authorized": False,
        "field_evidence_accepted": False,
        "external_gate": requirements["mobilisation_gate"],
        "raw_data_policy": requirements["raw_data_policy"],
        "status": "brief-issued-awaiting-signatures" if datasets and not findings else "brief-incomplete",
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        f"# {report['city'].title()} field-evidence brief",
        "",
        "Deterministic pre-mobilisation requirements generated from the shared field-evidence template.",
        "It issues the information request; it does not claim that field data or approvals exist.",
        "",
        f"- Brief status: **{report['status']}**",
        f"- Mobilisation authorized: **{'yes' if report['mobilisation_authorized'] else 'no'}**",
        f"- Field evidence accepted: **{'yes' if report['field_evidence_accepted'] else 'no'}**",
        f"- Horizontal CRS: {report['candidate_horizontal_crs']}",
        f"- Vertical datum: `{report['vertical_datum']}`",
        f"- Canonical requirements: `{report['requirements_source']}`",
        "",
        "> " + report["external_gate"],
        "",
        "## Required packages",
        "",
        "| ID | Dataset | Owner role | Delivery |",
        "|---|---|---|---|",
    ]
    for dataset in report["datasets"]:
        lines.append(
            f"| `{dataset['id']}` | {dataset['title']} | {dataset['owner_role']} | {dataset['delivery_format']} |"
        )
    lines.extend(["", "## Scope and acceptance", ""])
    for dataset in report["datasets"]:
        lines.extend(
            [
                f"### `{dataset['id']}` — {dataset['title']}",
                "",
                dataset["scope"],
                "",
                f"**Provisional accuracy/quality requirement:** {dataset['provisional_accuracy']}",
                "",
                "Acceptance evidence:",
                "",
            ]
        )
        lines.extend(f"- {item}" for item in dataset["acceptance_evidence"])
        lines.append("")
    lines.extend(
        [
            "## Data handling and handoff",
            "",
            report["raw_data_policy"],
            "",
            "Complete [`survey-input-manifest.csv`](survey-input-manifest.csv) for every delivery.",
            "Each accepted row must name the producer/checker, CRS and vertical datum, capture",
            "date, controlled project-storage path, SHA-256 digest and acceptance state. RTKLIB",
            "processing configurations/status/residual outputs, QGIS/CloudCompare/ODM settings",
            "and signed review records accompany their respective source data.",
            "",
        ]
    )
    return "\n".join(lines)


def write_manifest(path: Path, datasets: list[dict[str, Any]]) -> None:
    fields = [
        "dataset_id", "file_role", "package_revision", "file_path", "sha256", "capture_date",
        "coordinate_system", "vertical_datum", "producer", "checker", "acceptance_status",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for dataset in datasets:
            writer.writerow({"dataset_id": dataset["id"], "acceptance_status": "not-received"})


def generate(design_path: Path, output: Path, requirements_path: Path = DEFAULT_REQUIREMENTS) -> dict[str, Any]:
    report = build_report(design_path, requirements_path)
    output.mkdir(parents=True, exist_ok=True)
    atomic_json(output / "field-evidence-brief.json", report)
    (output / "field-evidence-brief.md").write_text(render_markdown(report), encoding="utf-8")
    write_manifest(output / "survey-input-manifest.csv", report["datasets"])
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--design", required=True, type=Path)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--requirements", type=Path, default=DEFAULT_REQUIREMENTS)
    args = parser.parse_args()
    if args.design.suffix.lower() == ".json":
        design = json.loads(args.design.read_text(encoding="utf-8"))
        slug = str(design.get("project", {}).get("slug", "unknown"))
    else:
        design = tomllib.loads(args.design.read_text(encoding="utf-8"))
        slug = str(design.get("city", {}).get("slug", "unknown"))
    output = args.output_dir or args.design.resolve().parent / "engineering/survey"
    report = generate(args.design, output, args.requirements)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["brief_ready_for_approval"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
