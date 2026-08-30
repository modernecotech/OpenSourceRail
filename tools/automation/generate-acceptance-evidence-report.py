#!/usr/bin/env python3
"""Generate acceptance/accreditation evidence-basis reports.

The report is not a certificate or approval. It is the traceability basis
that an owner engineer, ISA, or regulator can use to see what evidence must
exist before accepting manufactured trains and infrastructure into trial
running and operation.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_BUNDLE = REPO_ROOT / "build/generated-operations/samawah/samawah-operations.json.gz"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate acceptance/accreditation evidence-basis reports."
    )
    parser.add_argument("--bundle", type=Path, default=DEFAULT_BUNDLE)
    parser.add_argument(
        "--report",
        type=Path,
        default=None,
        help="report path (default: <bundle-folder>/acceptance-evidence-report.md)",
    )
    parser.add_argument(
        "--matrix",
        type=Path,
        default=None,
        help="matrix path (default: <bundle-folder>/<city>-acceptance-evidence-matrix.csv)",
    )
    args = parser.parse_args()

    if args.bundle.suffix == ".gz":
        with gzip.open(args.bundle, "rt", encoding="utf-8") as handle:
            data = json.load(handle)
    else:
        data = json.loads(args.bundle.read_text())
    fallback_slug = args.bundle.name.removesuffix("-operations.json.gz").removesuffix("-operations.json")
    slug = str(data.get("meta", {}).get("city_slug", fallback_slug))
    report_path = args.report or args.bundle.parent / "acceptance-evidence-report.md"
    matrix_path = args.matrix or args.bundle.parent / f"{slug}-acceptance-evidence-matrix.csv"
    matrix = build_matrix(data)
    write_csv(matrix_path, matrix)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(render_report(data, matrix, args.bundle, matrix_path))
    print(f"wrote {report_path}")
    print(f"wrote {matrix_path}")
    return 0


def build_matrix(data: dict[str, Any]) -> list[dict[str, Any]]:
    tasks = {
        str(row["manufacturing_uid"]): row
        for row in data.get("manufacturing_tasks", [])
    }
    materials_by_task: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in data.get("manufacturing_materials", []):
        materials_by_task[str(row["manufacturing_uid"])].append(row)

    rows: list[dict[str, Any]] = []
    for verification in data.get("manufacturing_verifications", []):
        uid = str(verification["manufacturing_uid"])
        task = tasks.get(uid, {})
        materials = materials_by_task.get(uid, [])
        material_sources = Counter(str(row["bom_source"]) for row in materials)
        rows.append({
            "evidence_id": verification["verification_uid"],
            "city": verification["city"],
            "asset_id": verification["asset_id"],
            "asset_name": verification["asset_name"],
            "asset_type": verification["asset_type"],
            "manufacturing_uid": uid,
            "package_id": verification["package_id"],
            "phase": verification["phase"],
            "qa_uid": verification["qa_uid"],
            "qa_gate_id": verification["qa_gate_id"],
            "qa_stage": verification["qa_stage"],
            "hold_point": verification["hold_point"],
            "required_result": verification["required_result"],
            "release_authority": verification["release_authority"],
            "evidence_required": verification["evidence_required"],
            "blocks_successors": verification["blocks_successors"],
            "predecessor_uids": task.get("predecessor_uids", ""),
            "material_count": len(materials),
            "material_sources": "; ".join(
                f"{source}:{count}" for source, count in sorted(material_sources.items())
            ),
            "acceptance_use": acceptance_use(verification),
        })
    return rows


def render_report(
    data: dict[str, Any],
    matrix: list[dict[str, Any]],
    bundle_path: Path,
    matrix_path: Path,
) -> str:
    totals = data.get("totals", {})
    tasks = data.get("manufacturing_tasks", [])
    materials = data.get("manufacturing_materials", [])
    verifications = data.get("manufacturing_verifications", [])
    qa_actions = data.get("qa_actions", [])
    maintenance_tasks = data.get("maintenance_tasks", [])

    task_count = len(tasks)
    all_materials = sum(1 for row in tasks if int(row.get("material_count") or 0) > 0)
    all_verifications = sum(1 for row in tasks if row.get("verification_uid"))
    all_qa_links = sum(1 for row in tasks if row.get("qa_uid"))
    external_pred = sum(1 for row in tasks if row.get("external_predecessors"))
    bom_sources = Counter(str(row.get("bom_source", "")) for row in materials)
    gates = Counter(str(row.get("qa_gate_id", "")) for row in verifications)
    meta = data.get("meta", {})
    city_name = str(meta.get("city_name", meta.get("city_slug", "City")))
    slug = str(meta.get("city_slug", "city"))

    out = [
        f"# {city_name} Acceptance And Accreditation Evidence Basis",
        "",
        "This report is the generated evidence basis for acceptance, trial-running",
        "readiness, and accreditation review. It is not itself an approval or",
        "certificate; it is the traceability index that shows which assets,",
        "manufacturing packages, BOM/material refs, QA hold points, evidence",
        "records, release authorities, and predecessor controls must be closed.",
        "",
        "## Summary",
        "",
        "| Item | Count / Status |",
        "|---|---:|",
        f"| Assets in register | {fmt(totals.get('assets', 0))} |",
        f"| Manufacturing schedule rows | {fmt(task_count)} |",
        f"| Manufacturing material/BOM rows | {fmt(len(materials))} |",
        f"| Manufacturing QA verification rows | {fmt(len(verifications))} |",
        f"| Construction QA action rows | {fmt(len(qa_actions))} |",
        f"| Maintenance handover schedule rows | {fmt(len(maintenance_tasks))} |",
        f"| Manufacturing rows with material refs | {fmt(all_materials)} / {fmt(task_count)} |",
        f"| Manufacturing rows with verification refs | {fmt(all_verifications)} / {fmt(task_count)} |",
        f"| Manufacturing rows linked to QA actions | {fmt(all_qa_links)} / {fmt(task_count)} |",
        f"| Unresolved external predecessors | {fmt(external_pred)} |",
        "",
        "## Material / BOM Basis",
        "",
        "| Source | Rows |",
        "|---|---:|",
    ]
    for source, count in sorted(bom_sources.items()):
        out.append(f"| `{source}` | {fmt(count)} |")
    out.extend([
        "",
        "Rolling-stock rows link to the generated rolling-stock BOM and COTS",
        "fit-out BOM. Infrastructure rows use controlled `project_kit:*` refs",
        "until detailed civil/station/energy BOMs are added.",
        "",
        "## QA Gate Coverage",
        "",
        "| QA gate | Verification rows |",
        "|---|---:|",
    ])
    for gate, count in sorted(gates.items()):
        out.append(f"| `{gate}` | {fmt(count)} |")
    out.extend([
        "",
        "## Acceptance Control Logic",
        "",
        "- Every manufacturing package has a controlled material/BOM row set.",
        "- Every manufacturing package has a QA verification row.",
        "- Every verification row links to a generated QA action by `qa_uid`.",
        "- Resolved predecessor ids are generated for schedule blocking.",
        "- The portal blocks successor manufacturing work until predecessor",
        "  work orders are closed with pass evidence.",
        "- The portal blocks manufacturing closeout until the selected work",
        "  order has pass evidence.",
        "- Failed evidence creates a defect/NCR and puts the work order on hold.",
        "- SQLite-backed Ops Core stores work orders, inspections, defects/NCR,",
        "  and audit records for handover.",
        "",
        "## Remaining External Release Gates",
        "",
        "This generated evidence basis organizes acceptance work, but it does",
        "not close release gates that require independent review, field data,",
        "hardware bring-up, supplier freeze, first-article tests, or authority",
        "acceptance. The open gates remain:",
        "",
        "| Gate family | Still required before accreditation / revenue release |",
        "|---|---|",
        "| Independent safety assessment and residual risk | Named ISA/assessor review, action log, residual-risk acceptance, and deployment-specific ALARP/tolerability decision. |",
        "| Formal safety integration | Consensus refinement proof from TLA+ to implementation behavior, plus signed safety-log integration tests for forged, replayed, stale, and unknown-issuer entries. |",
        "| Pilot hardware evidence | Exact COTS BOM freeze, wiring/harness maps, enclosure/mounting, power/thermal margins, SD image checksums, self-test logs, bench/safety evidence, and commissioning records for T-ECU/S, T-ECU/A, T-OBS, W-SBC, and S-SBC. |",
        "| Rolling-stock production release | Supplier envelope freeze, EN structural/FEA reports, weld/WPS/NDT packages, manufacturing drawings, flat patterns/NC output, harness routing, weight/balance, first-car build hold point, and first-article inspection. |",
        "| Field validation | Obstacle/intrusion sensor calibration and representative hot-weather, dust/soiling, night, and rain datasets with false-positive/false-negative analysis. |",
        "| Charging and site energy | Site-specific solar yield, grid interconnect, charger thermal study, protection settings, utility approval, and train charging interface tests. |",
        "| Operations validation | Operator workshops, translated/deployment rulebook where needed, competence records, emergency exercises, maintenance access trials, and trial-running records. |",
        "",
        "Those items are tracked in the",
        "[certification release gap register](../../../../../../docs/certification/release-gap-register.md),",
        "[control-electronics release checklist](../../../../../../control-electronics/release-checklist.md),",
        "and",
        "[rolling-stock v2 release checklist](../../../../../../docs/rolling-stock/light-metro-3car/v2-release-checklist.md).",
        "The acceptance matrix should be treated as the evidence index that",
        "collects those closures, not as the closure itself.",
        "",
        "## Review Artifacts",
        "",
        f"- Tracked compact asset register: [`{slug}-assets.csv`]({slug}-assets.csv)",
        f"- Tracked operations manifest: [`{slug}-operations-manifest.json`]({slug}-operations-manifest.json)",
        "",
        "The following high-volume files are regenerated in the local city",
        "package and intentionally excluded from Git. Their names are recorded",
        "for handover without presenting unavailable GitHub links:",
        "",
        f"- `{bundle_path.name}`",
        f"- `{matrix_path.name}`",
        f"- `{slug}-manufacturing-schedule.csv`",
        f"- `{slug}-manufacturing-materials.csv`",
        f"- `{slug}-manufacturing-verification.csv`",
        f"- `{slug}-qa-register.csv`",
        f"- `{slug}-maintenance-schedule.csv`",
        "",
        "## Accreditation Use",
        "",
        "The evidence matrix can be filtered by asset, package, QA gate, release",
        "authority, or material source. During acceptance, each row should be",
        "matched to completed Ops Core evidence, defects/NCR status, and the",
        "release authority signoff before the related asset is accepted into",
        "trial running or passenger operation.",
        "",
    ])
    return "\n".join(out)


def acceptance_use(row: dict[str, Any]) -> str:
    gate = str(row.get("qa_gate_id", ""))
    if gate.startswith("qa-1"):
        return "rolling-stock acceptance and trainset release"
    if gate in {"qa-20-survey-geotech", "qa-21-earthworks-drainage", "qa-22-trackform-rail", "qa-23-structures"}:
        return "civil, track, switch, and route-section acceptance"
    if gate == "qa-24-stations-depots-plant":
        return "station, depot, production plant, and public-opening acceptance"
    if gate == "qa-25-power-energy":
        return "energy, charging, earthing, protection, and interconnection acceptance"
    if gate == "qa-26-wayside-comms-safety":
        return "wayside, W-SBC, comms, sensors, and cyber acceptance"
    if gate == "qa-00-design-freeze":
        return "baseline design and ITP release"
    return "system acceptance evidence"


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("")
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=list(rows[0].keys()),
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


def fmt(value: Any) -> str:
    return f"{int(value):,}"


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
