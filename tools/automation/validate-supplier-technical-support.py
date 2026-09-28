#!/usr/bin/env python3
"""Validate and publish the fail-closed LM3 supplier-support readiness record."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import tomllib
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "lib/templates/supplier-technical-support-readiness.toml"
STATUS_JSON = ROOT / "docs/commercial/supplier-technical-support-readiness.json"
STATUS_MD = ROOT / "docs/commercial/supplier-technical-support-readiness.md"
RFQ_TEMPLATE = ROOT / "design/component-catalogue/catalog/buildable-trainset/evidence/rfq-response-template.json"


def _unique(rows: list[dict], label: str) -> set[str]:
    values = [str(row.get("id", "")).strip() for row in rows]
    if any(not value for value in values) or len(values) != len(set(values)):
        raise ValueError(f"{label} IDs must be present and unique")
    return set(values)


def _strings(row: dict, field: str, *, required: bool = True) -> list[str]:
    values = row.get(field, [])
    if not isinstance(values, list) or not all(
        isinstance(value, str) and value.strip() for value in values
    ):
        raise ValueError(f"{row.get('id', 'record')} {field} must contain strings")
    cleaned = [value.strip() for value in values]
    if required and not cleaned:
        raise ValueError(f"{row.get('id', 'record')} requires non-empty {field}")
    if len(cleaned) != len(set(cleaned)):
        raise ValueError(f"{row.get('id', 'record')} {field} must not contain duplicates")
    return cleaned


def _check_local_ref(value: str, label: str) -> None:
    path = Path(value)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"{label} must be a repository-relative path")
    if not (ROOT / path).exists():
        raise ValueError(f"{label} does not exist: {value}")


def _check_public_source(value: str, label: str) -> None:
    parsed = urlparse(value)
    if parsed.scheme in {"https", "http"} and parsed.netloc:
        return
    _check_local_ref(value, label)


def _all_text(row: dict, fields: tuple[str, ...]) -> bool:
    return all(str(row.get(field, "")).strip() for field in fields)


def _validate_rfq_contract(cost_ids: set[str]) -> dict:
    data = json.loads(RFQ_TEMPLATE.read_text(encoding="utf-8"))
    if data.get("schema_version") != "2.0":
        raise ValueError("supplier RFQ response contract must use schema 2.0")
    required_top = {
        "engagement_id",
        "commercial_candidate_id",
        "osr_baseline",
        "supplier",
        "offered_work_package_ids",
        "exact_order_codes",
        "separated_costs",
        "interface_packages",
        "controlled_documents",
        "local_capability_offer",
        "lifecycle_import",
        "responsibility",
        "design_authority_review",
    }
    missing = required_top - set(data)
    if missing:
        raise ValueError(f"supplier RFQ response contract misses: {sorted(missing)}")
    supplier_fields = {
        "legal_name",
        "authority_to_offer_ref",
        "manufacturer_legal_name",
        "manufacturer_authorization_ref",
        "named_engineering_owner",
        "conflict_disclosure_ref",
    }
    if supplier_fields - set(data["supplier"]):
        raise ValueError("supplier RFQ response contract misses authority fields")
    baseline_fields = {
        "configuration_id",
        "commit",
        "freeze_record_ref",
        "duty_cycle_ref",
        "route_environment_ref",
    }
    if baseline_fields - set(data["osr_baseline"]):
        raise ValueError("supplier RFQ response contract misses baseline fields")
    response_cost_ids = [str(row.get("id", "")) for row in data["separated_costs"]]
    if len(response_cost_ids) != len(set(response_cost_ids)) or set(response_cost_ids) != cost_ids:
        raise ValueError("supplier RFQ response cost buckets must match the readiness register")
    return {
        "path": str(RFQ_TEMPLATE.relative_to(ROOT)),
        "schema_version": data["schema_version"],
        "authority_fields_present": True,
        "baseline_fields_present": True,
        "separated_cost_bucket_count": len(response_cost_ids),
        "lifecycle_import_present": bool(data["lifecycle_import"]),
        "responsibility_record_present": bool(data["responsibility"]),
    }


def build_status(source: Path = SOURCE) -> dict:
    data = tomllib.loads(source.read_text(encoding="utf-8"))
    engagement = dict(data.get("engagement", {}))
    baseline = dict(data.get("baseline", {}))
    leads = list(data.get("catalogue_lead", []))
    work_packages = list(data.get("work_package", []))
    interfaces = list(data.get("interface_package", []))
    costs = list(data.get("cost_bucket", []))
    gates = list(data.get("gate", []))
    claims = dict(data.get("claim_controls", {}))

    lead_ids = _unique(leads, "catalogue-lead")
    work_ids = _unique(work_packages, "work-package")
    interface_ids = _unique(interfaces, "interface-package")
    cost_ids = _unique(costs, "cost-bucket")
    gate_ids = _unique(gates, "gate")
    if not all((lead_ids, work_ids, interface_ids, cost_ids, gate_ids)):
        raise ValueError("declare leads, work packages, interfaces, costs and gates")
    rfq_contract = _validate_rfq_contract(cost_ids)

    if engagement.get("status") not in {
        "screening",
        "definition",
        "contracted",
        "active",
        "closed",
        "cancelled",
    }:
        raise ValueError("invalid engagement status")
    if baseline.get("status") not in {"not-frozen", "candidate-frozen", "accepted"}:
        raise ValueError("invalid baseline status")
    for field in (
        "train_requirement_ref",
        "interface_requirement_ref",
        "product_tree_ref",
        "loading_and_mass_ref",
        "localisation_objective_ref",
    ):
        value = str(baseline.get(field, "")).strip()
        if not value:
            raise ValueError(f"baseline requires {field}")
        _check_local_ref(value, f"baseline {field}")
    baseline_frozen = baseline.get("status") in {"candidate-frozen", "accepted"} and _all_text(
        baseline,
        ("configuration_id", "osr_commit", "freeze_record_ref", "duty_cycle_ref", "route_environment_ref"),
    )

    lead_rows = []
    for row in leads:
        status = row.get("status")
        if status not in {"screening-source-only", "contacted", "qualified", "withdrawn"}:
            raise ValueError(f"{row['id']} has invalid status")
        if not _all_text(
            row,
            ("display_name", "public_source", "published_scope", "possible_use", "limitations"),
        ):
            raise ValueError(f"{row['id']} requires its public screening description")
        _check_public_source(str(row["public_source"]), f"{row['id']} public_source")
        evidence = _strings(row, "evidence_refs", required=False)
        qualified = status == "qualified" and _all_text(
            row, ("legal_entity", "authority_chain_ref", "controlled_offer_ref")
        ) and len(evidence) >= 3
        lead_rows.append({**row, "evidence_count": len(evidence), "qualified": qualified})

    work_rows = []
    for row in work_packages:
        if row.get("status") not in {"proposed", "contracted", "in-progress", "submitted", "accepted", "rejected"}:
            raise ValueError(f"{row['id']} has invalid status")
        inputs = _strings(row, "osr_input_refs")
        outputs = _strings(row, "required_outputs")
        for value in inputs:
            _check_local_ref(value, f"{row['id']} input")
        evidence = _strings(row, "evidence_refs", required=False)
        accepted = row.get("status") == "accepted" and _all_text(
            row, ("supplier_owner", "osr_owner", "independent_reviewer")
        ) and len(evidence) >= len(outputs)
        work_rows.append(
            {
                **row,
                "input_count": len(inputs),
                "required_output_count": len(outputs),
                "evidence_count": len(evidence),
                "accepted_and_evidenced": accepted,
            }
        )

    interface_rows = []
    for row in interfaces:
        if row.get("status") not in {"open", "in-review", "accepted", "rejected"}:
            raise ValueError(f"{row['id']} has invalid status")
        related = _strings(row, "related_work_packages")
        unknown = set(related) - work_ids
        if unknown:
            raise ValueError(f"{row['id']} references unknown work packages: {sorted(unknown)}")
        required_fields = _strings(row, "required_fields")
        evidence = _strings(row, "evidence_refs", required=False)
        accepted = row.get("status") == "accepted" and _all_text(
            row, ("responsible_party", "accepted_configuration_ref")
        ) and len(evidence) >= len(required_fields)
        interface_rows.append(
            {
                **row,
                "required_field_count": len(required_fields),
                "evidence_count": len(evidence),
                "accepted_and_evidenced": accepted,
            }
        )

    cost_rows = []
    for row in costs:
        if row.get("status") not in {"unquoted", "budgetary", "firm", "accepted", "withdrawn"}:
            raise ValueError(f"{row['id']} has invalid status")
        amount = row.get("amount")
        if not isinstance(amount, (int, float)) or isinstance(amount, bool) or not math.isfinite(amount) or amount < 0:
            raise ValueError(f"{row['id']} amount must be a finite non-negative number")
        inclusions = _strings(row, "inclusions", required=False)
        exclusions = _strings(row, "exclusions", required=False)
        priced = row.get("status") in {"budgetary", "firm", "accepted"} and amount > 0 and _all_text(
            row, ("currency", "price_basis", "quote_ref", "valid_until")
        ) and bool(inclusions) and bool(exclusions)
        accepted = row.get("status") == "accepted" and priced
        cost_rows.append(
            {
                **row,
                "inclusion_count": len(inclusions),
                "exclusion_count": len(exclusions),
                "priced_and_scoped": priced,
                "accepted_and_scoped": accepted,
            }
        )

    gate_rows = []
    for row in gates:
        if row.get("decision") not in {"open", "pass", "hold", "reject"}:
            raise ValueError(f"{row['id']} has invalid decision")
        required = _strings(row, "required_evidence")
        evidence = _strings(row, "evidence_refs", required=False)
        passed = row.get("decision") == "pass" and _all_text(
            row, ("decided_by", "decided_at")
        ) and len(evidence) >= len(required)
        gate_rows.append(
            {
                **row,
                "required_evidence_count": len(required),
                "evidence_count": len(evidence),
                "passed_and_evidenced": passed,
            }
        )

    claim_rules = {
        "supplier_support_committed": ({"unverified", "committed", "withdrawn"}, "committed", "supplier_support_ref"),
        "manufacturer_access_authorized": ({"unverified", "authorized", "withdrawn"}, "authorized", "manufacturer_access_ref"),
        "lm3_configuration_compatible": ({"unproven", "demonstrated", "rejected"}, "demonstrated", "lm3_configuration_ref"),
        "first_article_authorized": ({"not-authorized", "authorized", "withdrawn"}, "authorized", "first_article_ref"),
        "local_manufacture_transferred": ({"unproven", "demonstrated", "rejected"}, "demonstrated", "local_manufacture_ref"),
        "all_in_repeat_cost": ({"unproven", "evidenced", "withdrawn"}, "evidenced", "all_in_repeat_cost_ref"),
        "railway_acceptance": ({"not-granted", "granted", "withdrawn"}, "granted", "railway_acceptance_ref"),
    }
    claim_rows = []
    for claim, (allowed, positive, ref_field) in claim_rules.items():
        if claim not in claims or ref_field not in claims:
            raise ValueError(f"claim controls require {claim} and {ref_field}")
        value = str(claims[claim]).strip()
        ref = str(claims[ref_field]).strip()
        if value not in allowed:
            raise ValueError(f"{claim} has invalid status")
        evidenced = value == positive and bool(ref)
        if value == positive and not ref:
            raise ValueError(f"{claim} cannot be {positive} without {ref_field}")
        claim_rows.append(
            {"claim": claim, "status": value, "required_positive": positive, "evidence_ref": ref, "evidenced": evidenced}
        )

    engagement_defined = engagement.get("status") in {"contracted", "active", "closed"} and _all_text(
        engagement,
        (
            "engagement_id",
            "commercial_candidate_id",
            "engagement_owner",
            "customer_or_sponsor",
            "procurement_route_ref",
            "conflict_review_ref",
            "controlled_workspace_ref",
        ),
    )
    summary = {
        "catalogue_leads": len(lead_rows),
        "qualified_leads": sum(row["qualified"] for row in lead_rows),
        "work_packages": len(work_rows),
        "accepted_work_packages": sum(row["accepted_and_evidenced"] for row in work_rows),
        "interfaces": len(interface_rows),
        "accepted_interfaces": sum(row["accepted_and_evidenced"] for row in interface_rows),
        "cost_buckets": len(cost_rows),
        "priced_cost_buckets": sum(row["priced_and_scoped"] for row in cost_rows),
        "accepted_cost_buckets": sum(row["accepted_and_scoped"] for row in cost_rows),
        "gates": len(gate_rows),
        "passed_gates": sum(row["passed_and_evidenced"] for row in gate_rows),
        "claims": len(claim_rows),
        "evidenced_claims": sum(row["evidenced"] for row in claim_rows),
        "technical_claims_evidenced": sum(
            row["evidenced"] for row in claim_rows if row["claim"] != "railway_acceptance"
        ),
        "railway_acceptance_granted": next(
            row["evidenced"] for row in claim_rows if row["claim"] == "railway_acceptance"
        ),
        "engagement_defined": engagement_defined,
        "baseline_frozen": baseline_frozen,
    }
    summary["technical_support_ready"] = bool(
        engagement_defined
        and baseline_frozen
        and summary["qualified_leads"] > 0
        and summary["accepted_work_packages"] == summary["work_packages"]
        and summary["accepted_interfaces"] == summary["interfaces"]
        and summary["accepted_cost_buckets"] == summary["cost_buckets"]
        and summary["passed_gates"] == summary["gates"]
        and summary["technical_claims_evidenced"] == summary["claims"] - 1
    )

    return {
        "schema_version": "opensource-rail-supplier-technical-support-readiness-v1",
        "source": str(source.relative_to(ROOT)) if source.is_relative_to(ROOT) else str(source),
        "template_schema_version": data.get("schema_version"),
        "template_revision": data.get("template_revision"),
        "template_status": data.get("template_status"),
        "authority_boundary": data.get("authority_boundary"),
        "engagement": engagement,
        "baseline": {**baseline, "frozen_and_evidenced": baseline_frozen},
        "catalogue_leads": lead_rows,
        "work_packages": work_rows,
        "interface_packages": interface_rows,
        "cost_buckets": cost_rows,
        "gates": gate_rows,
        "claim_controls": claim_rows,
        "rfq_intake_contract": rfq_contract,
        "summary": summary,
    }


def _mark(value: bool) -> str:
    return "yes" if value else "no"


def render_markdown(status: dict) -> str:
    summary = status["summary"]
    lines = [
        "# Supplier Technical-Support Readiness",
        "",
        "> Generated from `lib/templates/supplier-technical-support-readiness.toml`; do not edit this report directly.",
        "",
        f"> **Authority boundary:** {status['authority_boundary']}",
        "",
        "## Current Decision",
        "",
        f"**Technical-support ready: {_mark(summary['technical_support_ready']).upper()}.** "
        f"The baseline is {'frozen' if summary['baseline_frozen'] else 'not frozen'}, "
        f"{summary['qualified_leads']}/{summary['catalogue_leads']} catalogue leads are qualified, "
        f"{summary['accepted_work_packages']}/{summary['work_packages']} work packages and "
        f"{summary['accepted_interfaces']}/{summary['interfaces']} interfaces are accepted, "
        f"{summary['accepted_cost_buckets']}/{summary['cost_buckets']} cost buckets are accepted, and "
        f"{summary['passed_gates']}/{summary['gates']} gates have passed.",
        "",
        "Public supplier pages are useful discovery inputs. They do not count as a commitment, controlled configuration, manufacturer authorization or LM3 evidence. A controlled opportunity copy must carry confidential offers and acceptance records.",
        "",
        "## Baseline",
        "",
        "| Field | Value |",
        "|---|---|",
    ]
    for field in (
        "configuration_id",
        "osr_commit",
        "freeze_record_ref",
        "duty_cycle_ref",
        "route_environment_ref",
        "status",
    ):
        lines.append(f"| `{field}` | {status['baseline'].get(field) or '—'} |")

    lines.extend(["", "## Catalogue Leads", "", "| Lead | Published scope | Status | Qualified |", "|---|---|---|---|"])
    for row in status["catalogue_leads"]:
        lines.append(
            f"| `{row['id']}` — {row['display_name']} | {row['published_scope']} | {row['status']} | {_mark(row['qualified'])} |"
        )

    lines.extend(["", "## Technical Work Packages", "", "| Package | Discipline | Existing OSR inputs | Evidence / required | Accepted |", "|---|---|---:|---:|---|"])
    for row in status["work_packages"]:
        lines.append(
            f"| `{row['id']}` — {row['title']} | {row['discipline']} | {row['input_count']} | "
            f"{row['evidence_count']} / {row['required_output_count']} | {_mark(row['accepted_and_evidenced'])} |"
        )

    lines.extend(["", "## Cross-Supplier Interfaces", "", "| Interface | Work packages | Evidence / fields | Accepted |", "|---|---|---:|---|"])
    for row in status["interface_packages"]:
        lines.append(
            f"| `{row['id']}` — {row['title']} | {', '.join(f'`{value}`' for value in row['related_work_packages'])} | "
            f"{row['evidence_count']} / {row['required_field_count']} | {_mark(row['accepted_and_evidenced'])} |"
        )

    lines.extend(["", "## Separated Cost Statement", "", "| Bucket | Status | Amount | Scoped | Accepted |", "|---|---|---:|---|---|"])
    for row in status["cost_buckets"]:
        amount = f"{row['amount']:,.2f} {row['currency']}" if row["amount"] else "—"
        lines.append(
            f"| `{row['id']}` — {row['title']} | {row['status']} | {amount} | "
            f"{_mark(row['priced_and_scoped'])} | {_mark(row['accepted_and_scoped'])} |"
        )

    lines.extend(["", "## Decision Gates", "", "| Gate | Decision | Evidence / required | Passed |", "|---|---|---:|---|"])
    for row in status["gates"]:
        lines.append(
            f"| `{row['id']}` — {row['title']} | {row['decision']} | {row['evidence_count']} / "
            f"{row['required_evidence_count']} | {_mark(row['passed_and_evidenced'])} |"
        )

    lines.extend(["", "## Controlled Claims", "", "| Claim | Recorded status | Evidence | Claim evidenced |", "|---|---|---|---|"])
    for row in status["claim_controls"]:
        lines.append(
            f"| `{row['claim']}` | {row['status']} | {row['evidence_ref'] or '—'} | {_mark(row['evidenced'])} |"
        )

    lines.extend(
        [
            "",
            "## How This Uses The Existing Platform",
            "",
            "The eight work packages consume the existing LM3 requirements, product tree, supplier anchors, RFQ candidates, mechanical interface register, first-article gates, manufacturing controls, city duty-cycle evidence and ERP/lifecycle identities. Accepted supplier data should update those sources through configuration-controlled changes; it must not be copied into a detached supplier spreadsheet and treated as a second design baseline.",
            f"The supplier intake contract is `{status['rfq_intake_contract']['path']}` schema {status['rfq_intake_contract']['schema_version']}; it carries authority, frozen-baseline, separated-cost, interface-responsibility, local-capability and lifecycle-import fields.",
            "",
            "Use `python3 tools/automation/validate-supplier-technical-support.py --check` to reject stale output or invalid references.",
            "",
        ]
    )
    return "\n".join(lines)


def _json_text(status: dict) -> str:
    return json.dumps(status, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail if generated reports are stale")
    args = parser.parse_args()
    status = build_status()
    expected_json = _json_text(status)
    expected_md = render_markdown(status)
    if args.check:
        stale = []
        if not STATUS_JSON.exists() or STATUS_JSON.read_text(encoding="utf-8") != expected_json:
            stale.append(str(STATUS_JSON.relative_to(ROOT)))
        if not STATUS_MD.exists() or STATUS_MD.read_text(encoding="utf-8") != expected_md:
            stale.append(str(STATUS_MD.relative_to(ROOT)))
        if stale:
            raise SystemExit("stale supplier technical-support output: " + ", ".join(stale))
    else:
        STATUS_JSON.parent.mkdir(parents=True, exist_ok=True)
        STATUS_JSON.write_text(expected_json, encoding="utf-8")
        STATUS_MD.write_text(expected_md, encoding="utf-8")
    summary = status["summary"]
    print(
        "supplier technical support: "
        f"{summary['qualified_leads']}/{summary['catalogue_leads']} leads, "
        f"{summary['accepted_work_packages']}/{summary['work_packages']} work packages, "
        f"{summary['accepted_interfaces']}/{summary['interfaces']} interfaces, "
        f"{summary['passed_gates']}/{summary['gates']} gates accepted"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
