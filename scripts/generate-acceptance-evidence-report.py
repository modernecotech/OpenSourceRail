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
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BUNDLE = REPO_ROOT / "docs/operations-portal/data/samawah-operations.json"
DEFAULT_REPORT = REPO_ROOT / "docs/operations-portal/acceptance-evidence-report.md"
DEFAULT_MATRIX = REPO_ROOT / "docs/operations-portal/data/samawah-acceptance-evidence-matrix.csv"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate acceptance/accreditation evidence-basis reports."
    )
    parser.add_argument("--bundle", type=Path, default=DEFAULT_BUNDLE)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--matrix", type=Path, default=DEFAULT_MATRIX)
    args = parser.parse_args()

    data = json.loads(args.bundle.read_text())
    matrix = build_matrix(data)
    write_csv(args.matrix, matrix)
    args.report.write_text(render_report(data, matrix, args.bundle, args.matrix))
    print(f"wrote {args.report}")
    print(f"wrote {args.matrix}")
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

    out = [
        "# Samawah Acceptance And Accreditation Evidence Basis",
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
        "## Review Artifacts",
        "",
        f"- Operations bundle: [`{rel(bundle_path)}`](../../{rel(bundle_path)})",
        f"- Evidence matrix CSV: [`{rel(matrix_path)}`](../../{rel(matrix_path)})",
        "- Manufacturing schedule CSV: [`docs/operations-portal/data/samawah-manufacturing-schedule.csv`](data/samawah-manufacturing-schedule.csv)",
        "- Manufacturing materials CSV: [`docs/operations-portal/data/samawah-manufacturing-materials.csv`](data/samawah-manufacturing-materials.csv)",
        "- Manufacturing verification CSV: [`docs/operations-portal/data/samawah-manufacturing-verification.csv`](data/samawah-manufacturing-verification.csv)",
        "- QA register CSV: [`docs/operations-portal/data/samawah-qa-register.csv`](data/samawah-qa-register.csv)",
        "- Maintenance schedule CSV: [`docs/operations-portal/data/samawah-maintenance-schedule.csv`](data/samawah-maintenance-schedule.csv)",
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
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
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
