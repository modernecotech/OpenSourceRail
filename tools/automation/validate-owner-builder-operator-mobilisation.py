#!/usr/bin/env python3
"""Validate and publish the fail-closed owner-builder-operator mobilisation state."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import tomllib


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "lib/templates/owner-builder-operator-mobilisation.toml"
STATUS_JSON = ROOT / "docs/owner-builder-operator-mobilisation-status.json"
STATUS_MD = ROOT / "docs/owner-builder-operator-mobilisation-status.md"


def _unique(rows: list[dict], field: str, label: str) -> set[str]:
    values = [str(row.get(field, "")) for row in rows]
    if any(not value for value in values) or len(values) != len(set(values)):
        raise ValueError(f"{label} IDs must be present and unique")
    return set(values)


def build_status(source: Path = SOURCE) -> dict:
    data = tomllib.loads(source.read_text(encoding="utf-8"))
    entity_fields = data.get("entity_model", {}).get("required_fields")
    if not isinstance(entity_fields, list) or not all(isinstance(value, str) and value.strip() for value in entity_fields):
        raise ValueError("declare entity_model.required_fields explicitly; use an empty list when none apply to the selected scope")
    roles = list(data.get("role", []))
    parties = list(data.get("independent_party", []))
    gates = list(data.get("gate", []))
    work_packages = list(data.get("work_package", []))
    management_systems = list(data.get("management_system", []))
    role_ids = _unique(roles, "id", "role")
    party_ids = _unique(parties, "id", "independent-party")
    gate_ids = _unique(gates, "id", "gate")
    work_package_ids = _unique(work_packages, "id", "work-package")
    management_system_ids = _unique(management_systems, "id", "management-system")
    if not role_ids or not gate_ids or not work_package_ids:
        raise ValueError("declare accountable roles, gates and work packages for the selected scope")
    if not str(data.get("deployment_scope", "")).strip():
        raise ValueError("declare the deployment scope before validating its requirements")
    if any(not row.get("accountable_for") for row in roles):
        raise ValueError("every role requires accountable scope")
    for system in management_systems:
        if system.get("accountable_role_id") not in role_ids or system.get("required_by_gate_id") not in gate_ids:
            raise ValueError(f"{system['id']} has unresolved role or gate")
        if not system.get("required_documents"):
            raise ValueError(f"{system['id']} has insufficient controlled documents")
        if system.get("status") not in {"not-established", "in-development", "established", "suspended"}:
            raise ValueError(f"{system['id']} has invalid status")
    for gate in gates:
        accountable = set(gate.get("accountable_role_ids", []))
        if not accountable or not accountable <= role_ids:
            raise ValueError(f"{gate['id']} has invalid accountable roles")
        if not gate.get("required_evidence"):
            raise ValueError(f"{gate['id']} has insufficient exit evidence")
        if gate.get("decision") not in {"open", "accepted", "rejected", "paused"}:
            raise ValueError(f"{gate['id']} has invalid decision")

    work_by_id = {row["id"]: row for row in work_packages}
    for row in work_packages:
        dependencies = set(row.get("depends_on", []))
        if not dependencies <= work_package_ids or row["id"] in dependencies:
            raise ValueError(f"{row['id']} has invalid dependencies")
        if row.get("accountable_role_id") not in role_ids or row.get("gate_id") not in gate_ids:
            raise ValueError(f"{row['id']} has unresolved role or gate")
        start, end = float(row.get("start_month", -1)), float(row.get("end_month", -1))
        if not (math.isfinite(start) and math.isfinite(end) and 0 <= start < end):
            raise ValueError(f"{row['id']} has invalid month range")
        fte_min, fte_max = float(row.get("fte_min", 0)), float(row.get("fte_max", 0))
        if not (math.isfinite(fte_min) and math.isfinite(fte_max) and 0 < fte_min <= fte_max):
            raise ValueError(f"{row['id']} has invalid FTE range")
        if not row.get("deliverables"):
            raise ValueError(f"{row['id']} has insufficient deliverables")
        if row.get("status") not in {"not-started", "in-progress", "complete", "blocked", "cancelled"}:
            raise ValueError(f"{row['id']} has invalid status")

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(work_id: str) -> None:
        if work_id in visiting:
            raise ValueError(f"mobilisation dependency cycle at {work_id}")
        if work_id in visited:
            return
        visiting.add(work_id)
        for dependency in work_by_id[work_id].get("depends_on", []):
            visit(dependency)
        visiting.remove(work_id)
        visited.add(work_id)

    for work_id in work_package_ids:
        visit(work_id)

    role_rows = []
    for role in roles:
        ready = (
            role.get("status") == "appointed"
            and bool(role.get("appointment_ref"))
            and bool(role.get("competence_ref"))
        )
        role_rows.append({**role, "ready": ready})

    party_rows = []
    for party in parties:
        ready = (
            party.get("status") == "appointed"
            and all(party.get(field) for field in ("organisation", "appointment_ref", "conflict_check_ref", "scope_ref"))
        )
        party_rows.append({**party, "ready": ready})

    gate_rows = []
    for gate in gates:
        evidence_refs = [ref for ref in gate.get("evidence_refs", []) if isinstance(ref, str) and ref.strip()]
        accepted = (
            gate.get("decision") == "accepted"
            and len(evidence_refs) >= len(gate["required_evidence"])
            and bool(gate.get("decided_by"))
            and bool(gate.get("decided_at"))
        )
        gate_rows.append(
            {
                **gate,
                "accepted": accepted,
                "evidence_count": len(evidence_refs),
                "required_evidence_count": len(gate["required_evidence"]),
            }
        )

    completed: dict[str, bool] = {}

    def work_complete(work_id: str) -> bool:
        if work_id not in completed:
            row = work_by_id[work_id]
            refs = [ref for ref in row.get("evidence_refs", []) if isinstance(ref, str) and ref.strip()]
            completed[work_id] = (
                row.get("status") == "complete"
                and len(refs) >= len(row["deliverables"])
                and all(work_complete(dependency) for dependency in row.get("depends_on", []))
            )
        return completed[work_id]

    work_rows = []
    for row in sorted(work_packages, key=lambda value: (value["start_month"], value["id"])):
        evidence_refs = [ref for ref in row.get("evidence_refs", []) if isinstance(ref, str) and ref.strip()]
        complete = work_complete(row["id"])
        work_rows.append(
            {
                **row,
                "duration_months": row["end_month"] - row["start_month"],
                "deliverable_count": len(row["deliverables"]),
                "evidence_count": len(evidence_refs),
                "complete": complete,
            }
        )

    management_system_rows = []
    for row in sorted(management_systems, key=lambda value: value["id"]):
        evidence_refs = [ref for ref in row.get("evidence_refs", []) if isinstance(ref, str) and ref.strip()]
        ready = (
            row.get("status") == "established"
            and len(evidence_refs) >= len(row["required_documents"])
            and bool(row.get("approved_by"))
            and bool(row.get("approved_at"))
        )
        management_system_rows.append(
            {
                **row,
                "required_document_count": len(row["required_documents"]),
                "evidence_count": len(evidence_refs),
                "ready": ready,
            }
        )

    project = dict(data.get("project", {}))
    entity = dict(data.get("entity_model", {}))
    entity_ready = all(entity.get(field) for field in entity_fields)
    result = {
        "schema": "org.opensourcerail.owner-builder-operator-mobilisation-status.v2",
        "source": str(source.resolve().relative_to(ROOT)) if source.resolve().is_relative_to(ROOT) else str(source.resolve()),
        "deployment_scope": data["deployment_scope"],
        "source_schema_version": data.get("schema_version"),
        "template_revision": data.get("template_revision"),
        "template_status": data.get("template_status"),
        "authority_boundary": data.get("authority_boundary"),
        "project": project,
        "entity_model": entity | {"ready": entity_ready},
        "summary": {
            "roles_ready": sum(row["ready"] for row in role_rows),
            "roles_total": len(role_rows),
            "independent_parties_ready": sum(row["ready"] for row in party_rows),
            "independent_parties_total": len(party_rows),
            "gates_accepted": sum(row["accepted"] for row in gate_rows),
            "gates_total": len(gate_rows),
            "work_packages_complete": sum(row["complete"] for row in work_rows),
            "work_packages_total": len(work_rows),
            "management_systems_ready": sum(row["ready"] for row in management_system_rows),
            "management_systems_total": len(management_system_rows),
            "default_programme_start_month": min(row["start_month"] for row in work_rows),
            "default_programme_end_month": max(row["end_month"] for row in work_rows),
            "mobilisation_ready": entity_ready and all(row["ready"] for row in role_rows) and all(row["ready"] for row in party_rows) and all(row["ready"] for row in management_system_rows) and all(row["complete"] for row in work_rows) and all(row["accepted"] for row in gate_rows),
        },
        "roles": role_rows,
        "independent_parties": party_rows,
        "management_systems": management_system_rows,
        "gates": sorted(gate_rows, key=lambda row: row["id"]),
        "work_packages": work_rows,
        "validation": {
            "declared_roles_valid": True,
            "declared_independent_parties_valid": True,
            "declared_gates_valid": True,
            "all_gate_accountabilities_resolve": True,
            "all_gates_have_exit_evidence": True,
            "reference_schema_is_not_a_deployment_mandate": True,
            "declared_work_packages_valid": True,
            "work_package_dependencies_acyclic": True,
            "all_work_package_roles_and_gates_resolve": True,
            "declared_management_systems_valid": True,
            "all_management_system_roles_and_gates_resolve": True,
            "all_management_system_document_sets_defined": True,
        },
    }
    return result


def render_status(status: dict) -> str:
    summary = status["summary"]
    project_id = status["project"].get("project_id") or "unassigned template"
    lines = [
        "# Owner–Builder–Operator Mobilisation Status",
        "",
        f"> Status: **{status.get('template_status') or 'deployment evidence record'} — not legal, spending, construction, safety or operating authority**.",
        "",
        f"Project: `{project_id}`",
        "",
        f"Scope: {status['deployment_scope']}",
        "",
        "The reference organisation and programme are editable. Validate the selected responsibilities, evidence and dependencies; job titles, committee structures and document counts are not universal requirements.",
        "",
        f"Entity model complete: **{'yes' if status['entity_model']['ready'] else 'no'}** · Roles ready: **{summary['roles_ready']}/{summary['roles_total']}** · Independent parties ready: **{summary['independent_parties_ready']}/{summary['independent_parties_total']}** · Management systems ready: **{summary['management_systems_ready']}/{summary['management_systems_total']}** · Work packages complete: **{summary['work_packages_complete']}/{summary['work_packages_total']}** · Gates accepted: **{summary['gates_accepted']}/{summary['gates_total']}**",
        "",
        status.get("authority_boundary") or "Evidence status for the declared scope; not operating authority.",
        "",
        "## Accountable Roles",
        "",
        "| ID | Role | Appointment | Competence | Ready |",
        "|---|---|---|---|---|",
    ]
    for role in status["roles"]:
        lines.append(
            f"| `{role['id']}` | {role['title']} | {role.get('appointment_ref') or 'open'} | "
            f"{role.get('competence_ref') or 'open'} | {'yes' if role['ready'] else 'no'} |"
        )
    lines += [
        "",
        "## Independent Parties",
        "",
        "| ID | Party | Organisation / appointment | Ready |",
        "|---|---|---|---|",
    ]
    for party in status["independent_parties"]:
        reference = " / ".join(value for value in (party.get("organisation"), party.get("appointment_ref")) if value) or "open"
        lines.append(f"| `{party['id']}` | {party['title']} | {reference} | {'yes' if party['ready'] else 'no'} |")
    lines += [
        "",
        "## Management-System Readiness",
        "",
        "| ID | System | Accountable | Required by | Evidence | Status | Ready |",
        "|---|---|---|---|---:|---|---|",
    ]
    for system in status["management_systems"]:
        lines.append(
            f"| `{system['id']}` | {system['title']} | `{system['accountable_role_id']}` | "
            f"`{system['required_by_gate_id']}` | {system['evidence_count']}/{system['required_document_count']} | "
            f"`{system['status']}` | {'yes' if system['ready'] else 'no'} |"
        )
    lines += [
        "",
        "## Mobilisation Gates",
        "",
        "| Gate | Window | Accountable roles | Evidence | Decision | Accepted |",
        "|---|---|---|---:|---|---|",
    ]
    for gate in status["gates"]:
        accountable = ", ".join(f"`{value}`" for value in gate["accountable_role_ids"])
        lines.append(
            f"| `{gate['id']}` — {gate.get('title', gate['id'])} | {gate.get('indicative_window', '')} | {accountable} | "
            f"{gate['evidence_count']}/{gate['required_evidence_count']} | `{gate['decision']}` | {'yes' if gate['accepted'] else 'no'} |"
        )
    lines += [
        "",
        "## Default Mobilisation Work Programme",
        "",
        f"Planning horizon: month **{summary['default_programme_start_month']}–{summary['default_programme_end_month']}**. Overlap is intentional; local approvals, procurement and construction determine the actual baseline.",
        "",
        "| Work package | Months | Planning FTE | Accountable | Depends on | Gate | Evidence | Status |",
        "|---|---:|---:|---|---|---|---:|---|",
    ]
    for row in status["work_packages"]:
        dependencies = ", ".join(f"`{value}`" for value in row.get("depends_on", [])) or "start"
        lines.append(
            f"| `{row['id']}` — {row.get('title', row['id'])} | {row['start_month']}–{row['end_month']} | "
            f"{row['fte_min']}–{row['fte_max']} | `{row['accountable_role_id']}` | {dependencies} | "
            f"`{row['gate_id']}` | {row['evidence_count']}/{row['deliverable_count']} | `{row['status']}` |"
        )
    lines += [
        "",
        "Use the [setup plan](owner-builder-operator-setup.md) to mobilise the organisation.",
        "Copy [`owner-builder-operator-mobilisation.toml`](../lib/templates/owner-builder-operator-mobilisation.toml)",
        "into a controlled deployment workspace, fill it with evidence references, and retain this repository file as the blank default.",
        "A gate is accepted only when its decision, decision-maker/date and at least one reference for every required evidence item are recorded.",
        "",
    ]
    return "\n".join(lines)


def write_outputs(status: dict, json_path: Path = STATUS_JSON, md_path: Path = STATUS_MD) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(status, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path.write_text(render_status(status), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if tracked status outputs are stale")
    parser.add_argument("--source", type=Path, default=SOURCE, help="Tailored deployment TOML; reference is the default")
    parser.add_argument("--output-dir", type=Path, help="Directory for the tailored status JSON and Markdown")
    args = parser.parse_args()
    if args.source.resolve() != SOURCE.resolve() and not args.output_dir:
        parser.error("--output-dir is required for a tailored source so the repository reference is preserved")
    json_path = args.output_dir / STATUS_JSON.name if args.output_dir else STATUS_JSON
    md_path = args.output_dir / STATUS_MD.name if args.output_dir else STATUS_MD
    status = build_status(args.source)
    expected_json = json.dumps(status, indent=2, sort_keys=True) + "\n"
    expected_md = render_status(status)
    if args.check:
        stale = []
        if not json_path.is_file() or json_path.read_text(encoding="utf-8") != expected_json:
            stale.append(str(json_path))
        if not md_path.is_file() or md_path.read_text(encoding="utf-8") != expected_md:
            stale.append(str(md_path))
        if stale:
            raise SystemExit("stale owner-builder-operator status: " + ", ".join(stale))
    else:
        write_outputs(status, json_path, md_path)
    summary = status["summary"]
    print(
        "owner-builder-operator mobilisation: "
        f"{summary['roles_ready']}/{summary['roles_total']} roles, "
        f"{summary['management_systems_ready']}/{summary['management_systems_total']} management systems, "
        f"{summary['work_packages_complete']}/{summary['work_packages_total']} work packages, "
        f"{summary['gates_accepted']}/{summary['gates_total']} gates accepted"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
