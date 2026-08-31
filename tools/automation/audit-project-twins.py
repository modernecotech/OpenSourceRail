#!/usr/bin/env python3
"""Audit city twins against mechanical, civil, finance and source records."""

from __future__ import annotations

import argparse
import hashlib
import json
import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--city", help="audit one city slug instead of the catalogue")
    parser.add_argument("--output", type=Path, default=ROOT / "build/project-twin-audit.json")
    args = parser.parse_args()
    findings: list[str] = []
    rows: list[dict] = []

    for design_path in sorted((ROOT / "cities/catalogue").glob("*/*/*/design.toml")):
        design = tomllib.loads(design_path.read_text(encoding="utf-8"))
        slug = str(design.get("city", {}).get("slug", design_path.parent.name.lower()))
        if args.city and slug != args.city:
            continue
        summary_path = design_path.parent / "engineering/project-twin/summary.json"
        finance_path = design_path.parent / "engineering/finance/summary.json"
        prefix = f"{slug}:"
        if not summary_path.is_file() or not finance_path.is_file():
            findings.append(f"{prefix} missing project-twin or finance summary")
            continue
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        finance = json.loads(finance_path.read_text(encoding="utf-8"))
        family_set = {
            str(line["rolling_stock"])
            for line in design.get("lines", [])
            if line.get("rolling_stock")
        }
        family = next(iter(family_set)) if len(family_set) == 1 else "review-required"
        if summary.get("product_scope", {}).get("rolling_stock_family") != family:
            findings.append(f"{prefix} rolling-stock scope does not match design family {family}")
        capex = round(float(finance.get("capex_usd", {}).get("reconciled_project_total", 0.0)), 2)
        twin_capex = round(float(summary.get("totals", {}).get("planned_capex_usd", 0.0)), 2)
        cash = round(float(summary.get("cashflow", {}).get("total_planned_requirement_usd", 0.0)), 2)
        if capex != twin_capex or capex != cash:
            findings.append(f"{prefix} finance/twin/cashflow mismatch {capex}/{twin_capex}/{cash}")
        expected_buckets = {
            str(row["bucket"]): round(float(row.get("total_usd", 0.0)), 2)
            for row in finance.get("capex_usd", {}).get("procurement_origin_buckets", [])
        }
        actual_buckets = {
            str(key): round(float(value.get("budget_usd", 0.0)), 2)
            for key, value in summary.get("budget_by_bucket", {}).items()
        }
        if expected_buckets != actual_buckets:
            findings.append(f"{prefix} budget work packages do not reconcile by CAPEX bucket")
        for source_name, source in summary.get("sources", {}).items():
            source_path = ROOT / str(source.get("path", ""))
            if not source_path.is_file():
                findings.append(f"{prefix} missing source {source_name}: {source.get('path')}")
            elif source.get("sha256") != sha256(source_path):
                findings.append(f"{prefix} stale source hash for {source_name}")
        totals = summary.get("totals", {})
        if not all(int(totals.get(key, 0)) > 0 for key in ("assets", "work_packages", "programme_working_days", "planned_purchase_orders", "cashflow_months")):
            findings.append(f"{prefix} project-controls totals are incomplete")
        rows.append({
            "city": slug,
            "rolling_stock_family": family,
            "planned_capex_usd": capex,
            "work_packages": int(totals.get("work_packages", 0)),
            "programme_working_days": int(totals.get("programme_working_days", 0)),
            "planned_purchase_orders": int(totals.get("planned_purchase_orders", 0)),
        })

    mechanical = audit_mechanical(findings)
    civil = audit_civil(findings)
    payload = {
        "schema": "org.opensourcerail.project-twin-audit.v1",
        "passed": not findings,
        "catalogue_cities_audited": len(rows),
        "mechanical_reference": mechanical,
        "civil_reference": civil,
        "findings": findings,
        "cities": rows,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"project-twin audit: {'passed' if not findings else f'{len(findings)} finding(s)'} ({len(rows)} cities)")
    print(f"wrote {args.output}")
    return 0 if not findings else 1


def audit_mechanical(findings: list[str]) -> dict:
    root = ROOT / "design/component-catalogue/catalog/buildable-trainset"
    manifest = json.loads((root / "buildable-trainset-manifest.json").read_text())
    anchors = json.loads((root / "supplier-anchors.json").read_text())
    candidates = json.loads((root / "cots-candidates.json").read_text())
    cost = json.loads((root / "trainset-build-cost.json").read_text())
    critical = json.loads((root / "critical-path.json").read_text())
    if anchors.get("coverage", {}).get("uncovered_product_ids"):
        findings.append("mechanical: external supplier-anchor coverage is incomplete")
    if candidates.get("coverage", {}).get("uncovered_product_ids"):
        findings.append("mechanical: external COTS/RFQ candidate coverage is incomplete")
    if manifest.get("family") != "light-metro-3car" or cost.get("family") != manifest.get("family"):
        findings.append("mechanical: reference family is inconsistent")
    return {
        "family": manifest.get("family"),
        "product_rows": len(manifest.get("product_items", [])),
        "assembly_nodes": len(manifest.get("assemblies", [])),
        "supplier_anchor_families": len(anchors.get("anchor", [])),
        "external_products_covered": anchors.get("coverage", {}).get("covered_external_product_rows", 0),
        "cots_candidate_families": len(candidates.get("candidate", [])),
        "cots_external_products_covered": candidates.get("coverage", {}).get("covered_external_product_rows", 0),
        "rows_with_exact_catalogue_component": candidates.get("coverage", {}).get("rows_with_exact_catalogue_component", 0),
        "build_cost_usd": cost.get("total_build_cost_usd", 0),
        "first_article_working_days": critical.get("project_duration_days", 0),
        "release_status": cost.get("release_status", ""),
    }


def audit_civil(findings: list[str]) -> dict:
    root = ROOT / "engineering/models/bim/reference"
    index = json.loads((root / "civil-coordination.index.json").read_text())
    sequence = json.loads((root / "civil-construction-sequence.json").read_text())
    validation = json.loads((root / "civil-coordination.validation.json").read_text())
    if not validation.get("passed"):
        findings.append("civil: IFC/IDS/BCF validation is not passing")
    if index.get("ifc_sha256") != sha256(root / "civil-coordination.ifc"):
        findings.append("civil: IFC hash does not match its coordination index")
    return {
        "ifc_schema": index.get("ifc_schema"),
        "coordinated_objects": len(index.get("objects", [])),
        "construction_tasks": len(sequence.get("tasks", [])),
        "validation_checks": len(validation.get("checks", [])),
        "validation_passed": bool(validation.get("passed")),
        "limitations": index.get("limitations", []),
    }


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


if __name__ == "__main__":
    raise SystemExit(main())
