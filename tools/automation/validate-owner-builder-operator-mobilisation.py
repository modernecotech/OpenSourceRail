#!/usr/bin/env python3
"""Validate and publish the fail-closed owner-builder-operator mobilisation state."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import tomllib


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "lib/templates/owner-builder-operator-mobilisation.toml"
STATUS_JSON = ROOT / "docs/owner-builder-operator-mobilisation-status.json"
STATUS_MD = ROOT / "docs/owner-builder-operator-mobilisation-status.md"
EXPECTED_ROLES = {
    "ROLE-OWNER", "ROLE-CEO", "ROLE-PROGRAMME", "ROLE-ENGINEERING",
    "ROLE-SAFETY", "ROLE-OPERATIONS", "ROLE-ASSET", "ROLE-MANUFACTURING",
    "ROLE-INFRASTRUCTURE", "ROLE-COMMERCIAL", "ROLE-FINANCE", "ROLE-PEOPLE",
    "ROLE-DIGITAL",
}
EXPECTED_GATES = {f"G{number}" for number in range(8)}
EXPECTED_INDEPENDENT = {"IND-ASSESSOR", "IND-CHECKER", "IND-AUDITOR"}
EXPECTED_WORK_PACKAGES = {f"MOB-{number:03d}" for number in range(10, 181, 10)}
EXPECTED_MANAGEMENT_SYSTEMS = {
    "MS-GOV", "MS-ENG", "MS-SAF", "MS-COMP", "MS-COM", "MS-PC",
    "MS-QUA", "MS-ASSET", "MS-ENV", "MS-FIN", "MS-DIG",
}


def _unique(rows: list[dict], field: str, label: str) -> set[str]:
    values = [str(row.get(field, "")) for row in rows]
    if any(not value for value in values) or len(values) != len(set(values)):
        raise ValueError(f"{label} IDs must be present and unique")
    return set(values)


def build_status(source: Path = SOURCE) -> dict:
    data = tomllib.loads(source.read_text(encoding="utf-8"))
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
    if role_ids != EXPECTED_ROLES:
        raise ValueError(f"role set changed: missing={sorted(EXPECTED_ROLES-role_ids)}, new={sorted(role_ids-EXPECTED_ROLES)}")
    if party_ids != EXPECTED_INDEPENDENT:
        raise ValueError("independent-party set changed")
    if gate_ids != EXPECTED_GATES:
        raise ValueError("G0-G7 mobilisation gates must all be present")
    if work_package_ids != EXPECTED_WORK_PACKAGES:
        raise ValueError("MOB-010 through MOB-180 work packages must all be present")
    if management_system_ids != EXPECTED_MANAGEMENT_SYSTEMS:
        raise ValueError("owner-builder-operator management-system set changed")
    if len(data.get("governance", {}).get("independence_rules", [])) < 5:
        raise ValueError("governance independence rules are incomplete")
    if any(not row.get("accountable_for") for row in roles):
        raise ValueError("every role requires accountable scope")
    for system in management_systems:
        if system.get("accountable_role_id") not in role_ids or system.get("required_by_gate_id") not in gate_ids:
            raise ValueError(f"{system['id']} has unresolved role or gate")
        if len(system.get("required_documents", [])) < 4:
            raise ValueError(f"{system['id']} has insufficient controlled documents")
        if system.get("status") not in {"not-established", "in-development", "established", "suspended"}:
            raise ValueError(f"{system['id']} has invalid status")
    for gate in gates:
        accountable = set(gate.get("accountable_role_ids", []))
        if not accountable or not accountable <= role_ids:
            raise ValueError(f"{gate['id']} has invalid accountable roles")
        if len(gate.get("required_evidence", [])) < 4:
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
        if not (0 <= int(row.get("start_month", -1)) < int(row.get("end_month", -1)) <= 120):
            raise ValueError(f"{row['id']} has invalid month range")
        if not (0 < int(row.get("fte_min", 0)) <= int(row.get("fte_max", 0))):
            raise ValueError(f"{row['id']} has invalid FTE range")
        if len(row.get("deliverables", [])) < 4:
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
        evidence_refs = list(gate.get("evidence_refs", []))
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

    work_rows = []
    for row in sorted(work_packages, key=lambda value: (value["start_month"], value["id"])):
        evidence_refs = list(row.get("evidence_refs", []))
        complete = (
            row.get("status") == "complete"
            and len(evidence_refs) >= len(row["deliverables"])
            and all(work_by_id[dependency].get("status") == "complete" for dependency in row.get("depends_on", []))
        )
        work_rows.append(
            {
                **row,
                "duration_months": int(row["end_month"]) - int(row["start_month"]),
                "deliverable_count": len(row["deliverables"]),
                "evidence_count": len(evidence_refs),
                "complete": complete,
            }
        )

    management_system_rows = []
    for row in sorted(management_systems, key=lambda value: value["id"]):
        evidence_refs = list(row.get("evidence_refs", []))
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
    entity_ready = all(
        entity.get(field)
        for field in (
            "selected_model", "selection_evidence_ref", "legal_advice_ref",
            "statutory_duties_register_ref", "reserved_matters_ref", "delegations_ref",
            "open_design_and_data_rights_ref",
        )
    )
    result = {
        "schema": "org.opensourcerail.owner-builder-operator-mobilisation-status.v2",
        "source": str(source.relative_to(ROOT)),
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
            "role_set_complete": True,
            "independent_parties_complete": True,
            "gates_g0_through_g7_complete": True,
            "all_gate_accountabilities_resolve": True,
            "all_gates_have_exit_evidence": True,
            "independence_rules_present": True,
            "work_package_set_complete": True,
            "work_package_dependencies_acyclic": True,
            "all_work_package_roles_and_gates_resolve": True,
            "management_system_set_complete": True,
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
        "> Status: **unfilled template — not legal, spending, construction, safety or operating authority**.",
        "",
        f"Project: `{project_id}`",
        "",
        f"Entity model complete: **{'yes' if status['entity_model']['ready'] else 'no'}** · Roles ready: **{summary['roles_ready']}/{summary['roles_total']}** · Independent parties ready: **{summary['independent_parties_ready']}/{summary['independent_parties_total']}** · Management systems ready: **{summary['management_systems_ready']}/{summary['management_systems_total']}** · Work packages complete: **{summary['work_packages_complete']}/{summary['work_packages_total']}** · Gates accepted: **{summary['gates_accepted']}/{summary['gates_total']}**",
        "",
        status["authority_boundary"],
        "",
        "## Accountable Roles",
        "",
        "| ID | Role | Appointment | Competence | Ready |",
        "|---|---|---|---|---|",
    ]
    for role in status["roles"]:
        lines.append(
            f"| `{role['id']}` | {role['title']} | {role['appointment_ref'] or 'open'} | "
            f"{role['competence_ref'] or 'open'} | {'yes' if role['ready'] else 'no'} |"
        )
    lines += [
        "",
        "## Independent Parties",
        "",
        "| ID | Party | Organisation / appointment | Ready |",
        "|---|---|---|---|",
    ]
    for party in status["independent_parties"]:
        reference = " / ".join(value for value in (party["organisation"], party["appointment_ref"]) if value) or "open"
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
            f"| `{gate['id']}` — {gate['title']} | {gate['indicative_window']} | {accountable} | "
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
        dependencies = ", ".join(f"`{value}`" for value in row["depends_on"]) or "start"
        lines.append(
            f"| `{row['id']}` — {row['title']} | {row['start_month']}–{row['end_month']} | "
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


def write_outputs(status: dict) -> None:
    STATUS_JSON.write_text(json.dumps(status, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    STATUS_MD.write_text(render_status(status), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if tracked status outputs are stale")
    args = parser.parse_args()
    status = build_status()
    expected_json = json.dumps(status, indent=2, sort_keys=True) + "\n"
    expected_md = render_status(status)
    if args.check:
        stale = []
        if not STATUS_JSON.is_file() or STATUS_JSON.read_text(encoding="utf-8") != expected_json:
            stale.append(str(STATUS_JSON.relative_to(ROOT)))
        if not STATUS_MD.is_file() or STATUS_MD.read_text(encoding="utf-8") != expected_md:
            stale.append(str(STATUS_MD.relative_to(ROOT)))
        if stale:
            raise SystemExit("stale owner-builder-operator status: " + ", ".join(stale))
    else:
        write_outputs(status)
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
