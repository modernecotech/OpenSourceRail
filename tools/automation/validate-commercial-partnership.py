#!/usr/bin/env python3
"""Validate and publish fail-closed commercial-partnership readiness."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import tomllib


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "lib/templates/commercial-partnership-readiness.toml"
STATUS_JSON = ROOT / "docs/commercial/partnership-readiness.json"
STATUS_MD = ROOT / "docs/commercial/partnership-readiness.md"


def _unique(rows: list[dict], label: str) -> set[str]:
    values = [str(row.get("id", "")).strip() for row in rows]
    if any(not value for value in values) or len(values) != len(set(values)):
        raise ValueError(f"{label} IDs must be present and unique")
    return set(values)


def _refs(row: dict, field: str = "evidence_refs") -> list[str]:
    values = row.get(field, [])
    if not isinstance(values, list):
        raise ValueError(f"{field} must be a list")
    return [value.strip() for value in values if isinstance(value, str) and value.strip()]


def _evidenced(row: dict, required_field: str) -> tuple[int, int]:
    required = row.get(required_field, [])
    if not isinstance(required, list) or not required or not all(
        isinstance(value, str) and value.strip() for value in required
    ):
        raise ValueError(f"{row.get('id', 'record')} requires non-empty {required_field}")
    return len(_refs(row)), len(required)


def build_status(source: Path = SOURCE) -> dict:
    data = tomllib.loads(source.read_text(encoding="utf-8"))
    opportunity = dict(data.get("opportunity", {}))
    candidates = list(data.get("reference_candidate", []))
    funding = dict(data.get("funding", {}))
    exclusivity = dict(data.get("exclusivity", {}))
    claims = dict(data.get("claim_controls", {}))
    parties = list(data.get("party", []))
    contributions = list(data.get("contribution", []))
    ip_items = list(data.get("ip_item", []))
    controls = list(data.get("commercial_control", []))
    localisation = list(data.get("localisation_stage", []))
    gates = list(data.get("gate", []))

    party_ids = _unique(parties, "party")
    _unique(candidates, "reference-candidate")
    _unique(contributions, "contribution")
    _unique(ip_items, "IP-item")
    _unique(controls, "commercial-control")
    _unique(localisation, "localisation-stage")
    _unique(gates, "gate")
    if not all((candidates, parties, contributions, ip_items, controls, localisation, gates)):
        raise ValueError("declare reference candidates, parties, contributions, IP items, controls, localisation stages and gates")

    procurement_roles = {
        "undecided",
        "owner-adviser",
        "prospective-supplier",
        "integrated-contractor",
    }
    if opportunity.get("procurement_role") not in procurement_roles:
        raise ValueError("invalid procurement role")
    candidate_types = {
        "integrated-corridor",
        "owner-operator-workshop",
        "manufacturing-first-article",
        "supplier-neutral-integration",
        "other",
    }
    candidate_rows = []
    for row in candidates:
        if row.get("candidate_type") not in candidate_types:
            raise ValueError(f"{row['id']} has invalid candidate type")
        if row.get("status") not in {"screening", "shortlisted", "selected", "paused", "withdrawn"}:
            raise ValueError(f"{row['id']} has invalid status")
        evidence_count, required_count = _evidenced(row, "selection_criteria")
        selected = (
            row.get("status") == "selected"
            and evidence_count >= required_count
            and all(
                str(row.get(field, "")).strip()
                for field in (
                    "country",
                    "city_or_site",
                    "scope",
                    "source_ref",
                    "customer_legal_name",
                    "customer_need_ref",
                    "funded_scope_ref",
                    "site_evidence_ref",
                    "approval_route_ref",
                    "reuse_case",
                )
            )
        )
        candidate_rows.append(
            {
                **row,
                "selection_evidence_count": evidence_count,
                "selection_criteria_count": required_count,
                "selected_and_evidenced": selected,
            }
        )

    opportunity_ready = (
        all(
            str(opportunity.get(field, "")).strip()
            for field in (
                "opportunity_id",
                "portfolio_owner",
                "candidate_selection_method_ref",
                "procurement_conflict_review_ref",
            )
        )
        and opportunity.get("procurement_role") != "undecided"
        and any(row["selected_and_evidenced"] for row in candidate_rows)
    )

    party_rows = []
    allowed_party_status = {"unverified", "verified", "withdrawn"}
    for row in parties:
        if row.get("status") not in allowed_party_status:
            raise ValueError(f"{row['id']} has invalid status")
        ready = row.get("status") == "verified" and all(
            str(row.get(field, "")).strip()
            for field in (
                "legal_name",
                "registration_jurisdiction",
                "authority_to_commit_ref",
                "beneficial_ownership_ref",
                "conflict_disclosure_ref",
            )
        )
        party_rows.append({**row, "ready": ready})

    contribution_rows = []
    for row in contributions:
        if row.get("party_id") not in party_ids:
            raise ValueError(f"{row['id']} has unknown party")
        value = float(row.get("agreed_value", -1))
        if not math.isfinite(value) or value < 0:
            raise ValueError(f"{row['id']} has invalid agreed value")
        currency = str(row.get("currency", "")).strip()
        if value > 0 and (len(currency) != 3 or not currency.isalpha()):
            raise ValueError(f"{row['id']} requires a three-letter currency")
        evidence_count, required_count = _evidenced(row, "acceptance_criteria")
        if row.get("status") not in {"proposed", "committed", "accepted", "rejected", "withdrawn"}:
            raise ValueError(f"{row['id']} has invalid status")
        accepted = (
            row.get("status") == "accepted"
            and evidence_count >= required_count
            and bool(str(row.get("acceptance_owner", "")).strip())
        )
        contribution_rows.append(
            {
                **row,
                "evidence_count": evidence_count,
                "required_evidence_count": required_count,
                "accepted": accepted,
            }
        )

    ip_rows = []
    for row in ip_items:
        if row.get("status") not in {"unagreed", "agreed", "disputed", "not-applicable"}:
            raise ValueError(f"{row['id']} has invalid status")
        ready = row.get("status") == "not-applicable" or (
            row.get("status") == "agreed"
            and all(
                str(row.get(field, "")).strip()
                for field in ("owner_or_custodian", "rights_ref", "publication_policy_ref")
            )
        )
        ip_rows.append({**row, "ready": ready})

    control_rows = []
    for row in controls:
        evidence_count, required_count = _evidenced(row, "required_evidence")
        if row.get("status") not in {"open", "approved", "suspended", "not-applicable"}:
            raise ValueError(f"{row['id']} has invalid status")
        ready = row.get("status") == "not-applicable" or (
            row.get("status") == "approved"
            and evidence_count >= required_count
            and bool(str(row.get("approved_by", "")).strip())
            and bool(str(row.get("approved_at", "")).strip())
        )
        control_rows.append(
            {
                **row,
                "evidence_count": evidence_count,
                "required_evidence_count": required_count,
                "ready": ready,
            }
        )

    localisation_rows = []
    for row in localisation:
        evidence_count, required_count = _evidenced(row, "required_outputs")
        if row.get("status") not in {"not-started", "in-progress", "complete", "paused", "cancelled"}:
            raise ValueError(f"{row['id']} has invalid status")
        complete = (
            row.get("status") == "complete"
            and evidence_count >= required_count
            and bool(str(row.get("accepted_by", "")).strip())
            and bool(str(row.get("accepted_at", "")).strip())
        )
        localisation_rows.append(
            {
                **row,
                "evidence_count": evidence_count,
                "required_evidence_count": required_count,
                "complete": complete,
            }
        )

    gate_rows = []
    for row in gates:
        evidence_count, required_count = _evidenced(row, "required_evidence")
        if row.get("decision") not in {"open", "accepted", "rejected", "paused"}:
            raise ValueError(f"{row['id']} has invalid decision")
        accepted = (
            row.get("decision") == "accepted"
            and evidence_count >= required_count
            and bool(str(row.get("decided_by", "")).strip())
            and bool(str(row.get("decided_at", "")).strip())
        )
        gate_rows.append(
            {
                **row,
                "evidence_count": evidence_count,
                "required_evidence_count": required_count,
                "accepted": accepted,
            }
        )

    funding_ready = (
        funding.get("status") == "agreed"
        and funding.get("development_and_project_finance_separated") is True
        and all(
            str(funding.get(field, "")).strip()
            for field in (
                "development_capital_ref",
                "customer_funded_work_ref",
                "factory_investment_ref",
                "working_capital_ref",
                "railway_project_finance_ref",
                "approved_by",
                "approved_at",
            )
        )
    )
    if funding.get("status") not in {"unagreed", "in-review", "agreed", "withdrawn"}:
        raise ValueError("invalid funding status")

    if not isinstance(exclusivity.get("enabled"), bool):
        raise ValueError("exclusivity.enabled must be boolean")
    exclusivity_ready = not exclusivity["enabled"]
    if exclusivity["enabled"]:
        term = exclusivity.get("term_months")
        exclusivity_ready = (
            isinstance(term, int)
            and term > 0
            and bool(exclusivity.get("territories"))
            and bool(exclusivity.get("performance_conditions"))
            and bool(exclusivity.get("termination_rights"))
            and bool(str(exclusivity.get("approval_ref", "")).strip())
        )

    expected_claims = {
        "customer_order": {"absent", "evidenced"},
        "industrial_partner_commitment": {"unverified", "evidenced"},
        "manufacturer_authorization": {"unverified", "evidenced"},
        "all_in_cost_advantage": {"unproven", "independently-demonstrated"},
        "railway_acceptance": {"not-granted", "authority-evidenced"},
    }
    for field, allowed in expected_claims.items():
        if claims.get(field) not in allowed:
            raise ValueError(f"invalid claim control {field}")
    evidenced_claim_values = {
        "customer_order": "evidenced",
        "industrial_partner_commitment": "evidenced",
        "manufacturer_authorization": "evidenced",
        "all_in_cost_advantage": "independently-demonstrated",
        "railway_acceptance": "authority-evidenced",
    }
    claims_evidenced = all(
        claims[field] == value and bool(str(claims.get(f"{field}_ref", "")).strip())
        for field, value in evidenced_claim_values.items()
    )

    gate_by_id = {row["id"]: row for row in gate_rows}
    expected_gate_ids = {f"P{number}" for number in range(5)}
    if set(gate_by_id) != expected_gate_ids:
        raise ValueError("commercial partnership gates must be P0 through P4")
    core_ready = (
        opportunity_ready
        and all(row["ready"] for row in party_rows)
        and all(row["accepted"] for row in contribution_rows)
        and all(row["ready"] for row in ip_rows)
        and all(row["ready"] for row in control_rows)
        and funding_ready
        and exclusivity_ready
    )
    development_agreement_ready = core_ready and gate_by_id["P0"]["accepted"] and gate_by_id["P1"]["accepted"]
    equity_jv_ready = development_agreement_ready and gate_by_id["P2"]["accepted"]
    candidate_project_ready = development_agreement_ready and gate_by_id["P3"]["accepted"]
    replication_ready = (
        candidate_project_ready
        and all(row["complete"] for row in localisation_rows)
        and gate_by_id["P4"]["accepted"]
    )

    summary = {
        "opportunity_ready": opportunity_ready,
        "candidates_screened_or_active": sum(row["status"] not in {"withdrawn"} for row in candidate_rows),
        "candidates_total": len(candidate_rows),
        "candidates_shortlisted": sum(row["status"] == "shortlisted" for row in candidate_rows),
        "candidates_selected_and_evidenced": sum(row["selected_and_evidenced"] for row in candidate_rows),
        "parties_ready": sum(row["ready"] for row in party_rows),
        "parties_total": len(party_rows),
        "contributions_accepted": sum(row["accepted"] for row in contribution_rows),
        "contributions_total": len(contribution_rows),
        "ip_items_ready": sum(row["ready"] for row in ip_rows),
        "ip_items_total": len(ip_rows),
        "commercial_controls_ready": sum(row["ready"] for row in control_rows),
        "commercial_controls_total": len(control_rows),
        "localisation_stages_complete": sum(row["complete"] for row in localisation_rows),
        "localisation_stages_total": len(localisation_rows),
        "gates_accepted": sum(row["accepted"] for row in gate_rows),
        "gates_total": len(gate_rows),
        "funding_ready": funding_ready,
        "exclusivity_controlled": exclusivity_ready,
        "public_claims_evidenced": claims_evidenced,
        "development_agreement_ready": development_agreement_ready,
        "equity_jv_ready": equity_jv_ready,
        "candidate_project_ready": candidate_project_ready,
        "replication_ready": replication_ready,
    }
    summary["partnership_ready"] = equity_jv_ready

    source_value = str(source.resolve().relative_to(ROOT)) if source.resolve().is_relative_to(ROOT) else str(source.resolve())
    return {
        "schema": "org.opensourcerail.commercial-partnership-readiness.v2",
        "source": source_value,
        "source_schema_version": data.get("schema_version"),
        "template_revision": data.get("template_revision"),
        "template_status": data.get("template_status"),
        "authority_boundary": data.get("authority_boundary"),
        "opportunity": opportunity | {"ready": opportunity_ready},
        "reference_candidates": candidate_rows,
        "funding": funding | {"ready": funding_ready},
        "exclusivity": exclusivity | {"controlled": exclusivity_ready},
        "claim_controls": claims | {"all_evidenced": claims_evidenced},
        "summary": summary,
        "parties": party_rows,
        "contributions": contribution_rows,
        "ip_items": ip_rows,
        "commercial_controls": control_rows,
        "localisation_stages": localisation_rows,
        "gates": gate_rows,
        "validation": {
            "identifiers_unique": True,
            "candidate_portfolio_is_open_ended": True,
            "selected_candidates_require_customer_funding_site_and_approval_evidence": True,
            "contribution_parties_resolve": True,
            "evidence_requirements_declared": True,
            "procurement_role_explicit": True,
            "development_and_project_finance_separated_before_readiness": True,
            "exclusive_rights_finite_performance_based_and_terminable": True,
            "claims_fail_closed": True,
        },
    }


def render_status(status: dict) -> str:
    summary = status["summary"]
    lines = [
        "# Commercial Partnership Readiness",
        "",
        f"> Status: **{status.get('template_status') or 'commercial evidence record'} — no partnership, supplier backing, customer order, financing, certification or operating authority is implied**.",
        "",
        status.get("authority_boundary") or "Evidence status only.",
        "",
        f"Opportunity ready: **{'yes' if summary['opportunity_ready'] else 'no'}** · Parties: **{summary['parties_ready']}/{summary['parties_total']}** · Contributions: **{summary['contributions_accepted']}/{summary['contributions_total']}** · IP items: **{summary['ip_items_ready']}/{summary['ip_items_total']}** · Controls: **{summary['commercial_controls_ready']}/{summary['commercial_controls_total']}** · Localisation stages: **{summary['localisation_stages_complete']}/{summary['localisation_stages_total']}** · Gates: **{summary['gates_accepted']}/{summary['gates_total']}**",
        "",
        f"Reference candidates active: **{summary['candidates_screened_or_active']}/{summary['candidates_total']}** · Shortlisted: **{summary['candidates_shortlisted']}** · Selected and evidenced: **{summary['candidates_selected_and_evidenced']}**",
        "",
        f"Funding separated and agreed: **{'yes' if summary['funding_ready'] else 'no'}** · Exclusivity controlled: **{'yes' if summary['exclusivity_controlled'] else 'no'}** · Public claims evidenced: **{'yes' if summary['public_claims_evidenced'] else 'no'}**",
        "",
        f"Development agreement ready: **{'yes' if summary['development_agreement_ready'] else 'no'}** · Equity JV ready: **{'yes' if summary['equity_jv_ready'] else 'no'}** · Any candidate project ready: **{'yes' if summary['candidate_project_ready'] else 'no'}** · Replication ready: **{'yes' if summary['replication_ready'] else 'no'}**",
        "",
        "## Reference Candidate Portfolio",
        "",
        "The candidate array is open-ended. Screening status records a possible example, not customer interest, funding or authorization. Give every selected project its own controlled copy before adding confidential evidence.",
        "",
        "| Candidate | Type | Country / site | Selection evidence | Status | Selected |",
        "|---|---|---|---:|---|---|",
    ]
    for row in status["reference_candidates"]:
        place = " / ".join(filter(None, (row.get("country"), row.get("city_or_site"))))
        lines.append(
            f"| `{row['id']}` | {row['candidate_type']} | {place} | "
            f"{row['selection_evidence_count']}/{row['selection_criteria_count']} | `{row['status']}` | "
            f"{'yes' if row['selected_and_evidenced'] else 'no'} |"
        )
    lines += [
        "",
        "## Parties",
        "",
        "| Party | Role | Legal identity | Authority | Ready |",
        "|---|---|---|---|---|",
    ]
    for row in status["parties"]:
        lines.append(
            f"| `{row['id']}` | {row['role']} | {row.get('legal_name') or 'open'} | "
            f"{row.get('authority_to_commit_ref') or 'open'} | {'yes' if row['ready'] else 'no'} |"
        )
    lines += [
        "",
        "## Contributions",
        "",
        "| Contribution | Party | Milestone | Evidence | Status | Accepted |",
        "|---|---|---|---:|---|---|",
    ]
    for row in status["contributions"]:
        lines.append(
            f"| `{row['id']}` — {row['description']} | `{row['party_id']}` | {row['due_milestone']} | "
            f"{row['evidence_count']}/{row['required_evidence_count']} | `{row['status']}` | {'yes' if row['accepted'] else 'no'} |"
        )
    lines += [
        "",
        "## IP And Manufacturing Rights",
        "",
        "| Item | Material | Rights / publication evidence | Status | Ready |",
        "|---|---|---|---|---|",
    ]
    for row in status["ip_items"]:
        evidence = " / ".join(filter(None, (row.get("rights_ref"), row.get("publication_policy_ref")))) or "open"
        lines.append(f"| `{row['id']}` | {row['material']} | {evidence} | `{row['status']}` | {'yes' if row['ready'] else 'no'} |")
    lines += [
        "",
        "## Commercial Controls",
        "",
        "| Control | Evidence | Status | Ready |",
        "|---|---:|---|---|",
    ]
    for row in status["commercial_controls"]:
        lines.append(
            f"| `{row['id']}` — {row['title']} | {row['evidence_count']}/{row['required_evidence_count']} | "
            f"`{row['status']}` | {'yes' if row['ready'] else 'no'} |"
        )
    lines += [
        "",
        "## Localisation Capability",
        "",
        "| Stage | Outputs | Status | Complete |",
        "|---|---:|---|---|",
    ]
    for row in status["localisation_stages"]:
        lines.append(
            f"| `{row['id']}` — {row['title']} | {row['evidence_count']}/{row['required_evidence_count']} | "
            f"`{row['status']}` | {'yes' if row['complete'] else 'no'} |"
        )
    lines += [
        "",
        "## Decision Gates",
        "",
        "| Gate | Evidence | Decision | Accepted |",
        "|---|---:|---|---|",
    ]
    for row in status["gates"]:
        lines.append(
            f"| `{row['id']}` — {row['title']} | {row['evidence_count']}/{row['required_evidence_count']} | "
            f"`{row['decision']}` | {'yes' if row['accepted'] else 'no'} |"
        )
    lines += [
        "",
        "Use the [joint-development framework](joint-development-framework.md) before tailoring this record.",
        "Copy [`commercial-partnership-readiness.toml`](../../lib/templates/commercial-partnership-readiness.toml) into a controlled opportunity workspace; do not fill the public reference template with confidential negotiation material.",
        "An accepted status without the required evidence, named acceptance or date remains open.",
        "",
    ]
    return "\n".join(lines)


def write_outputs(status: dict, json_path: Path = STATUS_JSON, md_path: Path = STATUS_MD) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(status, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path.write_text(render_status(status), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail when tracked outputs are stale")
    parser.add_argument("--source", type=Path, default=SOURCE, help="tailored opportunity TOML")
    parser.add_argument("--output-dir", type=Path, help="output directory for a tailored record")
    args = parser.parse_args()
    if args.source.resolve() != SOURCE.resolve() and not args.output_dir:
        parser.error("--output-dir is required for a tailored source")
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
            raise SystemExit("stale commercial-partnership status: " + ", ".join(stale))
    else:
        write_outputs(status, json_path, md_path)
    print(
        "commercial partnership: "
        f"{status['summary']['parties_ready']}/{status['summary']['parties_total']} parties, "
        f"{status['summary']['contributions_accepted']}/{status['summary']['contributions_total']} contributions, "
        f"{status['summary']['gates_accepted']}/{status['summary']['gates_total']} gates accepted"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
