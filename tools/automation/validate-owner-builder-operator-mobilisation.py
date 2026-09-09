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
    role_ids = _unique(roles, "id", "role")
    party_ids = _unique(parties, "id", "independent-party")
    gate_ids = _unique(gates, "id", "gate")
    if role_ids != EXPECTED_ROLES:
        raise ValueError(f"role set changed: missing={sorted(EXPECTED_ROLES-role_ids)}, new={sorted(role_ids-EXPECTED_ROLES)}")
    if party_ids != EXPECTED_INDEPENDENT:
        raise ValueError("independent-party set changed")
    if gate_ids != EXPECTED_GATES:
        raise ValueError("G0-G7 mobilisation gates must all be present")
    if len(data.get("governance", {}).get("independence_rules", [])) < 5:
        raise ValueError("governance independence rules are incomplete")
    if any(not row.get("accountable_for") for row in roles):
        raise ValueError("every role requires accountable scope")
    for gate in gates:
        accountable = set(gate.get("accountable_role_ids", []))
        if not accountable or not accountable <= role_ids:
            raise ValueError(f"{gate['id']} has invalid accountable roles")
        if len(gate.get("required_evidence", [])) < 4:
            raise ValueError(f"{gate['id']} has insufficient exit evidence")
        if gate.get("decision") not in {"open", "accepted", "rejected", "paused"}:
            raise ValueError(f"{gate['id']} has invalid decision")

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
        "schema": "org.opensourcerail.owner-builder-operator-mobilisation-status.v1",
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
            "mobilisation_ready": entity_ready and all(row["ready"] for row in role_rows) and all(row["ready"] for row in party_rows) and all(row["accepted"] for row in gate_rows),
        },
        "roles": role_rows,
        "independent_parties": party_rows,
        "gates": sorted(gate_rows, key=lambda row: row["id"]),
        "validation": {
            "role_set_complete": True,
            "independent_parties_complete": True,
            "gates_g0_through_g7_complete": True,
            "all_gate_accountabilities_resolve": True,
            "all_gates_have_exit_evidence": True,
            "independence_rules_present": True,
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
        f"Entity model complete: **{'yes' if status['entity_model']['ready'] else 'no'}** · Roles ready: **{summary['roles_ready']}/{summary['roles_total']}** · Independent parties ready: **{summary['independent_parties_ready']}/{summary['independent_parties_total']}** · Gates accepted: **{summary['gates_accepted']}/{summary['gates_total']}**",
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
        f"{summary['gates_accepted']}/{summary['gates_total']} gates accepted"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
