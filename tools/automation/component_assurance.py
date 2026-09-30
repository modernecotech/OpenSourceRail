#!/usr/bin/env python3
"""Build the deterministic all-component assurance and authorization register."""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
import tomllib


ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "lib/templates/component-assurance.toml"
OUTPUT_MARKDOWN = ROOT / "docs/certification/component-assurance-register.md"
OUTPUT_JSON = ROOT / "docs/certification/component-assurance-register.json"
DIGITAL_ASSURANCE = ROOT / "tools/automation/digital-assurance.py"


def _load_digital_assurance():
    spec = importlib.util.spec_from_file_location("osr_digital_assurance", DIGITAL_ASSURANCE)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load digital-assurance compiler")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _unique(rows: list[dict], label: str) -> None:
    ids = [row.get("id") for row in rows]
    if any(not isinstance(value, str) or not value for value in ids):
        raise ValueError(f"{label} requires non-empty IDs")
    if len(ids) != len(set(ids)):
        raise ValueError(f"duplicate {label} IDs")


def _source(root: Path, value: str) -> Path:
    path = (root / value).resolve()
    try:
        path.relative_to(root.resolve())
    except ValueError as error:
        raise ValueError(f"repository-relative component source required: {value}") from error
    if not path.is_file():
        raise ValueError(f"missing component source: {value}")
    return path


def compile_register(root: Path = ROOT, config: dict | None = None) -> dict:
    config = config or tomllib.loads((root / CONFIG.relative_to(ROOT)).read_text(encoding="utf-8"))
    gates = config.get("gates", [])
    routes = config.get("routes", [])
    platform_components = config.get("platform_components", [])
    _unique(gates, "gate")
    _unique(routes, "route")
    _unique(platform_components, "platform component")
    if [row["id"] for row in gates] != ["G0", "G1", "G2", "G3", "G4"]:
        raise ValueError("component assurance gates must be exactly G0 through G4 in order")

    scope_routes: dict[str, dict] = {}
    for route in routes:
        if not route.get("candidate_standards") or not route.get("qualification_focus"):
            raise ValueError(f"route {route['id']} requires standards candidates and qualification focus")
        for scope in route.get("scopes", []):
            if scope in scope_routes:
                raise ValueError(f"component scope has multiple routes: {scope}")
            scope_routes[scope] = route

    digital = _load_digital_assurance().compile_assurance(root)
    inventory = digital["inventory_coverage"]
    inventory_scopes = {row["scope"] for row in inventory}
    if inventory_scopes - set(scope_routes):
        raise ValueError(f"unrouted inventory scopes: {sorted(inventory_scopes - set(scope_routes))}")
    if "platform-service" not in scope_routes:
        raise ValueError("platform-service assurance route is required")

    passports: list[dict] = []

    def add_passport(
        *,
        controlled_id: str,
        title: str,
        scope: str,
        domain: str,
        source: str,
        controls: list[str],
        boundary: str,
    ) -> None:
        source_path = _source(root, source)
        route = scope_routes[scope]
        passports.append(
            {
                "assurance_id": f"CA:{scope}:{controlled_id}",
                "controlled_id": controlled_id,
                "title": title,
                "scope": scope,
                "domain": domain,
                "route_id": route["id"],
                "source": source,
                "source_sha256": _digest(source_path),
                "intended_use_boundary": boundary,
                "safety_classification": "deployment-classification-open",
                "standards_applicability": "candidate-list-requires-jurisdiction-review",
                "existing_controls": list(controls),
                "gate_status": {gate["id"]: gate["repository_state"] for gate in gates},
                "gate_evidence": {"G0": [source]},
                "release_state": "blocked-after-g0",
                "permitted_claim": "identity-and-source-baseline-recorded-only",
            }
        )

    for row in inventory:
        add_passport(
            controlled_id=row["item_id"],
            title=row["item"],
            scope=row["scope"],
            domain=row["domain"],
            source=row["evidence"],
            controls=row["existing_controls"],
            boundary="Reference engineering inventory item; exact deployment use, safety classification and jurisdiction remain G1 decisions.",
        )
    for row in platform_components:
        add_passport(
            controlled_id=row["id"],
            title=row["title"],
            scope="platform-service",
            domain="business-supervision",
            source=row["source"],
            controls=[row["boundary"]],
            boundary=row["boundary"],
        )

    assurance_ids = [row["assurance_id"] for row in passports]
    if len(assurance_ids) != len(set(assurance_ids)):
        raise ValueError("duplicate component assurance passport IDs")
    if any(row["release_state"] != "blocked-after-g0" for row in passports):
        raise ValueError("component register cannot claim unsupported release")
    if any(row["gate_status"]["G0"] != "pass-baseline-recorded" for row in passports):
        raise ValueError("every controlled item must have a G0 baseline")
    if any(any(row["gate_status"][gate].startswith("pass") for gate in ("G1", "G2", "G3", "G4")) for row in passports):
        raise ValueError("G1-G4 cannot pass without deployment evidence")

    scope_counts = Counter(row["scope"] for row in passports)
    route_counts = Counter(row["route_id"] for row in passports)
    domain_counts = Counter(row["domain"] for row in passports)
    source_paths = sorted(
        {row["source"] for row in passports}
        | {
            str(CONFIG.relative_to(root)),
            str(DIGITAL_ASSURANCE.relative_to(root)),
            "tools/automation/component_assurance.py",
        }
    )
    return {
        "schema": config["meta"]["schema"],
        "status": config["meta"]["status"],
        "authority_boundary": config["authority_boundary"],
        "model": {
            "principle": "one passport per controlled item, five gates, route-specific evidence, one system acceptance",
            "gates": gates,
            "routes": routes,
            "change_rule": "A changed identity, use, requirement, implementation, interface, environment or acceptance condition reopens the affected gate and every dependent later gate.",
            "roll_up_rule": "Component evidence may support a subsystem or system case, but no parent can pass a gate while a safety-significant child or interface remains open or stale.",
        },
        "summary": {
            "controlled_items": len(passports),
            "engineering_inventory_items": len(inventory),
            "platform_services": len(platform_components),
            "scopes": dict(sorted(scope_counts.items())),
            "routes": dict(sorted(route_counts.items())),
            "domains": dict(sorted(domain_counts.items())),
            "g0_baselined": len(passports),
            "g1_item_plans_open": len(passports),
            "g2_qualification_open": len(passports),
            "g3_integration_open": len(passports),
            "g4_acceptance_open": len(passports),
            "released_items": 0,
        },
        "source_hashes": {value: _digest(_source(root, value)) for value in source_paths},
        "passports": sorted(passports, key=lambda row: row["assurance_id"]),
        "validation": {
            "passed": True,
            "unique_passports": True,
            "complete_engineering_inventory_coverage": len(inventory) == 279,
            "platform_boundary_coverage": len(platform_components) > 0,
            "all_routes_assigned": True,
            "all_release_blocked_after_g0": True,
        },
    }


def render_markdown(report: dict) -> str:
    summary = report["summary"]
    gates = report["model"]["gates"]
    routes = report["model"]["routes"]
    lines = [
        "# All-component assurance register",
        "",
        "> Generated by `python3 tools/automation/component_assurance.py`. Do not edit this file or its JSON partner by hand.",
        "",
        report["authority_boundary"]["statement"],
        "",
        f"The register contains **{summary['controlled_items']} assurance passports**: {summary['engineering_inventory_items']} engineering inventory items and {summary['platform_services']} owner/operator platform services. Every item has a locked identity/source baseline at G0. All item-specific design, qualification, integration and independent-acceptance gates remain open; **zero items are represented as certified or released**.",
        "",
        "## One lifecycle",
        "",
        "| Gate | Decision question | Current repository state | Decision owner |",
        "|---|---|---|---|",
    ]
    for gate in gates:
        lines.append(f"| **{gate['id']} — {gate['name']}** | {gate['question']} | `{gate['repository_state']}` | {gate['decision_owner']} |")
    lines += [
        "",
        "A pass applies only to the named item, configuration, intended use and evidence revision. " + report["model"]["change_rule"],
        "",
        "## Assurance routes",
        "",
        "| Route | Items | Scope | Qualification emphasis | Final decision |",
        "|---|---:|---|---|---|",
    ]
    for route in routes:
        count = summary["routes"].get(route["id"], 0)
        lines.append(f"| `{route['id']}` | {count} | {route['title']} | {', '.join(route['qualification_focus'])} | {route['final_decision']} |")
    lines += [
        "",
        "Standards in each passport are **candidate applicability prompts**, not declarations of conformity. The deployment must freeze jurisdiction, intended use, safety classification, editions, national adoptions, contractual rules and assessment bodies at G1.",
        "",
        "## Current gate position",
        "",
        "| Gate | Baselined/passed | Open | Meaning |",
        "|---|---:|---:|---|",
        f"| G0 — Define | {summary['g0_baselined']} | 0 | Identity and source are recorded. |",
        f"| G1 — Assure design | 0 | {summary['g1_item_plans_open']} | Item applicability, classification and assurance plan remain deployment work. |",
        f"| G2 — Qualify implementation | 0 | {summary['g2_qualification_open']} | Supplier, build, target, test and physical evidence remain open. |",
        f"| G3 — Validate integration | 0 | {summary['g3_integration_open']} | HIL/FAT/SAT/site/commissioning evidence remains open. |",
        f"| G4 — Accept and authorize | 0 | {summary['g4_acceptance_open']} | Independent acceptance and legal/contractual authorization remain open. |",
        "",
        "## What each passport contains",
        "",
        "Each JSON passport carries a stable assurance ID, controlled item ID, scope/domain, route, source/hash reference, intended-use boundary, open safety classification, existing controls, five gate states and a fail-closed release state. Route definitions hold the candidate standards and evidence focus; gate definitions hold the decision owners. The JSON is the complete item-level register; this page intentionally stays short.",
        "",
        "## How evidence rolls up",
        "",
        "1. Close a component gate only against its exact configuration and raw evidence.",
        "2. Check every child, interface and common-cause dependency before closing the parent subsystem gate.",
        "3. Validate the integrated train, station, corridor and operating organization in their real environment.",
        "4. Keep product conformity, project acceptance, safety assessment and legal authorization as separate decisions.",
        "5. Reopen affected gates after change, incident, expiry or adverse field evidence; retain the superseded decision and conditions of use.",
        "",
        "The full deterministic register is [`component-assurance-register.json`](component-assurance-register.json). The [certification front door](README.md) explains how to use it with the safety case, release gaps and deployment dossier.",
        "",
    ]
    return "\n".join(lines)


def serialise(report: dict) -> str:
    return json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def outputs(root: Path = ROOT) -> tuple[str, str]:
    report = compile_register(root)
    return render_markdown(report), serialise(report)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if tracked outputs are stale")
    args = parser.parse_args()
    markdown, data = outputs(ROOT)
    targets = ((OUTPUT_MARKDOWN, markdown), (OUTPUT_JSON, data))
    stale = [path for path, value in targets if not path.is_file() or path.read_text(encoding="utf-8") != value]
    if args.check:
        if stale:
            raise SystemExit("stale component assurance register: " + ", ".join(str(path.relative_to(ROOT)) for path in stale))
    else:
        for path, value in targets:
            path.write_text(value, encoding="utf-8")
    report = json.loads(data)
    print(
        f"Component assurance: {report['summary']['controlled_items']} passports, "
        f"G0 {report['summary']['g0_baselined']}, released {report['summary']['released_items']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
