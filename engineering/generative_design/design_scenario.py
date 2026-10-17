"""Audited multi-agent design contracts; computational progress is not release.

The plan joins the current controlled inventory and actual production/inspection
registers. It deliberately does not fabricate discipline solvers for the many
systems still awaiting accepted inputs or validated engineering models.
"""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
import hashlib
import json
from pathlib import Path

from . import coverage, manufacturing

CONTRACT = Path(__file__).with_name("data") / "design-scenario.json"
SCHEMA = "osr-design-iteration-candidate/1"
STATES = {
    "generated",
    "computationally-rejected",
    "provisional-detailed",
    "computational-solution",
    "held-external-input",
    "bounded-search-exhausted",
    "stagnated",
}
CHECK_STATES = {"pass", "fail", "unknown"}
TRANSITIONS = {
    "generated": {
        "computationally-rejected",
        "provisional-detailed",
        "computational-solution",
        "held-external-input",
    },
    "provisional-detailed": {
        "computationally-rejected",
        "computational-solution",
        "held-external-input",
        "bounded-search-exhausted",
        "stagnated",
    },
    "computational-solution": {"held-external-input"},
    "computationally-rejected": {"bounded-search-exhausted", "stagnated"},
    "held-external-input": set(),
    "bounded-search-exhausted": set(),
    "stagnated": set(),
}


def _read(name):
    return json.loads((coverage.ROOT / name).read_text())


def _hash(value):
    return hashlib.sha256(
        json.dumps(
            value, sort_keys=True, separators=(",", ":"), allow_nan=False
        ).encode()
    ).hexdigest()


def candidate_id(candidate):
    """Identity excludes iteration/evaluation labels, preventing false progress."""
    return (
        "detail-"
        + _hash(
            {
                key: candidate[key]
                for key in (
                    "work_package_ids",
                    "configuration_id",
                    "parameters",
                    "source_hashes",
                )
            }
        )[:20]
    )


def exchange_candidate(
    raw,
    *,
    context,
    iteration,
    parent_candidate_ids,
    source_hashes,
    producer_agent,
    package_ids=None,
):
    """Normalize an actual adapter response without expanding its scope.

    ``adapter_raw`` retains geometry, materials, connections, objectives, model
    limitations and original check details byte-for-value in the JSON exchange.
    Internal evidence pointers identify the retained calculation, not a measured
    test or an approved document. Role worker names identify reproducible code;
    they do not claim a new LLM or an appointed independent engineer was run.
    """
    if any(
        raw.get(key, False) is not False
        for key in (
            "design_complete",
            "engineering_design_complete",
            "manufacturing_release",
            "physical_release",
        )
    ):
        raise ValueError("adapter cannot claim engineering or manufacturing release")
    if not isinstance(raw.get("work_package_ids"), list) or not isinstance(
        raw.get("component_ids"), list
    ):
        raise ValueError("adapter must declare actual package and component coverage")
    if len(raw["component_ids"]) != len(set(raw["component_ids"])):
        raise ValueError("duplicate adapter component coverage")
    configuration_id = raw.get("configuration_id") or context.get("configuration_id")
    if not configuration_id:
        raise ValueError("explicit configuration identity required")
    parameters = raw.get("parameters", raw.get("variables"))
    if not isinstance(parameters, dict):
        raise ValueError("adapter must retain explicit varied parameters")
    checks = []
    for index, row in enumerate(raw.get("checks", [])):
        check = deepcopy(row)
        check.setdefault("mandatory", True)
        if check.get("state") == "unknown":
            check.setdefault(
                "reason",
                check.get("basis")
                or "Accepted input, validated model or qualification evidence is absent.",
            )
        else:
            check.setdefault("evidence_ref", f"#/adapter_raw/checks/{index}")
        checks.append(check)
    failures = [c for c in checks if c.get("mandatory") and c.get("state") == "fail"]
    unknowns = [c["id"] for c in checks if c.get("state") == "unknown"]
    manufacturing_raw = deepcopy(raw.get("manufacturing", {}))
    manufacturing_state = {
        "route": manufacturing_raw.get("route")
        or "proposed-route-requires-process-validation",
        "material_state": "unaccepted",
        "process_state": "unqualified",
        "drawing_state": "proposal-unissued",
        "inspection_state": "not-performed",
        "adapter_proposal": manufacturing_raw,
    }
    result = {
        "schema": SCHEMA,
        "work_package_ids": sorted(raw["work_package_ids"]),
        "component_ids": sorted(raw["component_ids"]),
        "configuration_id": configuration_id,
        "iteration": iteration,
        "parent_candidate_ids": list(parent_candidate_ids),
        "producer_agent": producer_agent,
        "contributing_agents": deepcopy(raw.get("contributing_agents", [])),
        "source_hashes": deepcopy(source_hashes),
        "parameters": deepcopy(parameters),
        "checks": checks,
        "interfaces": deepcopy(raw.get("interfaces", [])),
        "manufacturing": manufacturing_state,
        "artifact_refs": deepcopy(raw.get("artifact_refs", [])),
        "unknowns": unknowns,
        "next_actions": deepcopy(
            raw.get(
                "next_actions",
                [
                    "Resolve controlling unknown checks with accepted inputs, qualified processes and actual physical evidence."
                ],
            )
        ),
        "state": (
            "computationally-rejected"
            if failures
            else "held-external-input" if unknowns else "provisional-detailed"
        ),
        "context": deepcopy(context),
        "adapter_raw": deepcopy(raw),
        "design_complete": False,
        "manufacturing_release": False,
        "physical_release": False,
    }
    result["id"] = candidate_id(result)
    validate_candidate(result, package_ids=package_ids)
    return result


def validate_candidate(candidate, *, package_ids=None):
    """Validate exchanges and reject fabricated engineering closure claims.

    ``computational-solution`` describes only the declared computational checks.
    Every supported output remains provisional for physical manufacture.
    """
    if candidate.get("schema") != SCHEMA:
        raise ValueError("unsupported design candidate schema")
    required = (
        "id",
        "work_package_ids",
        "component_ids",
        "configuration_id",
        "iteration",
        "parent_candidate_ids",
        "producer_agent",
        "source_hashes",
        "parameters",
        "checks",
        "interfaces",
        "manufacturing",
        "artifact_refs",
        "unknowns",
        "next_actions",
        "state",
        "design_complete",
        "manufacturing_release",
        "physical_release",
    )
    if any(key not in candidate for key in required):
        raise ValueError("incomplete candidate exchange")
    ids = candidate["work_package_ids"]
    if (
        not isinstance(ids, list)
        or not ids
        or any(not isinstance(x, str) or not x for x in ids)
        or len(ids) != len(set(ids))
        or (package_ids is not None and set(ids) - set(package_ids))
    ):
        raise ValueError("known unique work package IDs required")
    if candidate["state"] not in STATES or any(
        candidate[key] is not False
        for key in ("design_complete", "manufacturing_release", "physical_release")
    ):
        raise ValueError("automated candidates cannot grant engineering release")
    if candidate["id"] != candidate_id(candidate):
        raise ValueError("candidate identity differs from configuration and parameters")
    if (
        not candidate["configuration_id"]
        or not candidate["producer_agent"]
        or not isinstance(candidate["iteration"], int)
        or isinstance(candidate["iteration"], bool)
        or candidate["iteration"] < 0
        or not candidate["source_hashes"]
    ):
        raise ValueError(
            "configuration, producer, iteration and source bindings required"
        )
    for path, digest in candidate["source_hashes"].items():
        coverage.local(path)
        if not isinstance(digest, str) or len(digest) != 64:
            raise ValueError("SHA256 source binding required")
        try:
            int(digest, 16)
        except ValueError as exc:
            raise ValueError("SHA256 source binding required") from exc
    checks = candidate["checks"]
    if not checks or len({check["id"] for check in checks}) != len(checks):
        raise ValueError("nonempty unique check identities required")
    for check in checks:
        if check.get("state") not in CHECK_STATES or not check.get("id"):
            raise ValueError("checks require explicit pass, fail or unknown")
        if "mandatory" not in check or not isinstance(check["mandatory"], bool):
            raise ValueError("check mandatory status required")
        if check["state"] == "unknown" and not check.get("reason"):
            raise ValueError("unknown checks require a missing-input or model reason")
        if check["state"] != "unknown" and not check.get("evidence_ref"):
            raise ValueError("evaluated checks require an evidence reference")
    mandatory = [check for check in checks if check["mandatory"]]
    if candidate["state"] == "computational-solution" and (
        not mandatory or any(check["state"] != "pass" for check in mandatory)
    ):
        raise ValueError(
            "unknown or failed mandatory checks cannot be a computational solution"
        )
    if candidate["state"] == "computationally-rejected" and not any(
        check["state"] == "fail" and check["mandatory"] for check in checks
    ):
        raise ValueError("a rejected candidate must retain its failed mandatory check")
    manufacturing_state = candidate["manufacturing"]
    for key in (
        "route",
        "material_state",
        "process_state",
        "drawing_state",
        "inspection_state",
    ):
        if not manufacturing_state.get(key):
            raise ValueError("explicit manufacturing readiness fields required")
    if any(
        manufacturing_state[key] in {"accepted", "approved", "issued", "performed"}
        for key in (
            "material_state",
            "process_state",
            "drawing_state",
            "inspection_state",
        )
    ):
        raise ValueError(
            "candidate proposals cannot authenticate physical evidence or signoff"
        )
    for interface in candidate["interfaces"]:
        if not interface.get("id") or interface.get("state") not in CHECK_STATES:
            raise ValueError("explicit interface identities and states required")
        if interface["state"] == "pass" and not interface.get("evidence_ref"):
            raise ValueError("interface pass requires revision-bound evidence")
    _hash(candidate)  # Reject non-finite or non-serializable numerical outputs.
    return True


def independent_critique(candidate, *, critic_agent, checks, contributing_agents=()):
    """Record a distinct critic's numerical challenge without implying signoff."""
    validate_candidate(candidate)
    contributors = set(contributing_agents) | set(
        candidate.get("contributing_agents", [])
    )
    contributors.add(candidate["producer_agent"])
    if not critic_agent or critic_agent in contributors:
        raise ValueError(
            "independent critic must not produce or contribute to the candidate"
        )
    if not checks or any(
        check.get("state") not in CHECK_STATES
        or not check.get("id")
        or not check.get("evidence_ref")
        for check in checks
    ):
        raise ValueError(
            "independent challenge checks and evidence references required"
        )
    return {
        "schema": "osr-design-independent-critique/1",
        "candidate_id": candidate["id"],
        "candidate_sha256": _hash(candidate),
        "critic_agent": critic_agent,
        "producer_agent": candidate["producer_agent"],
        "checks": deepcopy(checks),
        "computational_challenge_passed": all(x["state"] == "pass" for x in checks),
        "review_kind": "reproducible-numerical-role-worker-challenge",
        "independent_engineering_review_performed": False,
        "authority_independently_verified": False,
        "design_complete": False,
        "manufacturing_release": False,
        "physical_release": False,
    }


def transition(candidate, state):
    """Advance one proposal; changed evidence/parameters require a new candidate.

    Terminal candidates stay immutable. A resumed run retains their history and
    derives new source-bound children rather than relabelling held work solved.
    """
    validate_candidate(candidate)
    if state not in TRANSITIONS[candidate["state"]]:
        raise ValueError("invalid design candidate state transition")
    result = deepcopy(candidate)
    result["state"] = state
    validate_candidate(result)
    return result


def _components(package, documents):
    """Keep IDs source qualified, including assembly/type/package identities."""
    result = []
    for source in package["authoritative_sources"]:
        document = documents.get(source["path"])
        by_id = {}

        def walk(value):
            if isinstance(value, dict):
                identifier = value.get(
                    "id", value.get("product_id", value.get("type_id"))
                )
                if isinstance(identifier, str):
                    by_id.setdefault(identifier, value)
                for child in value.values():
                    walk(child)
            elif isinstance(value, list):
                for child in value:
                    walk(child)

        walk(document)
        for identifier in source["ids"]:
            row = by_id.get(identifier, {})
            result.append(
                {
                    "id": identifier,
                    "source": source["path"],
                    "title": row.get("title", row.get("asset_class", identifier)),
                    "route": row.get("route"),
                    "parent": row.get("parent", row.get("parent_assembly")),
                    "design_reference_envelope_mm": row.get(
                        "design_reference_envelope_mm"
                    ),
                    "acceptance_requirements": row.get("acceptance", []),
                    "status": "open",
                }
            )
    return result


def plan():
    """Build exact current work and evidence coverage, with no orchestration."""
    contract = json.loads(CONTRACT.read_text())
    if contract.get("schema") != "osr-design-scenario-contract/1":
        raise ValueError("controlled design scenario contract required")
    scope = json.loads(coverage.SCOPE.read_text())
    audit = coverage.audit(scope)
    production = manufacturing.run()
    documents = {
        row["path"]: _read(row["path"])
        for row in scope["source_inventory"]
        if row["path"].endswith(".json")
    }
    release_sources = (
        (
            "design/component-catalogue/catalog/buildable-trainset/factory-release-work-packages.json",
            "packages",
        ),
        (
            "design/component-catalogue/catalog/buildable-stations/factory-release-work-packages.json",
            "packages",
        ),
        (
            "design/component-catalogue/catalog/buildable-civil/reusable-type-release-register.json",
            "release_packages",
        ),
    )
    release = {
        row["id"]: row
        for path, collection in release_sources
        for row in documents[path][collection]
    }
    details = documents["engineering/models/bim/design-detail-register.json"]
    interfaces = details["mechanical_interfaces"]
    civil_document = documents[
        "design/component-catalogue/catalog/buildable-civil/reusable-type-release-register.json"
    ]
    drawing_definitions = {
        row["id"]: row for row in civil_document["drawing_definitions"]
    }
    for row in production["drawings"]:
        drawing_definitions[row["drawing_id"]] = _read(row["source"])
    products = production["products"]
    requests = production["artifact_requests"]
    package_rows = []
    for package in scope["work_packages"]:
        identifier = package["id"]
        components = _components(package, documents)
        component_ids = sorted({row["id"] for row in components})
        declared = release.get(identifier, {})
        drawings = set(declared.get("drawing_ids", []))
        package_products = [row for row in products if identifier in row["package_ids"]]
        artifact_rows = [
            dict(row, artifact_id=row["id"])
            for row in requests
            if identifier in row["package_ids"]
        ]
        inspection_rows = [
            row
            for row in production["inspection_characteristics"]
            if row["package_id"] == identifier
        ]
        supplier_rows = [
            row
            for row in production["supplier_configuration_requests"]
            if row["product_id"] in component_ids
        ]
        interface_rows = [
            deepcopy(row)
            for row in interfaces
            if row["id"] in component_ids
            or set(row["source_product_ids"]) & set(component_ids)
        ]
        workflow = contract["domain_workflows"][package["domain"]]
        if identifier in {
            "CIV-FRP-100",
            "CIV-FRP-110",
            "CIV-FRP-120",
            "CIV-FRP-130",
            "CIV-INT-200",
            "CIV-INT-210",
        } or identifier.startswith("STN-FRP-"):
            adapter = "civil_detail.run"
        elif identifier.startswith("LM3-FRP-") or identifier.startswith("BUY-LM3-"):
            adapter = "mechanical_detail.run"
        else:
            adapter = None
        # These are work requests to adapters, never a claim that an adapter
        # implements every assigned package. Actual response coverage is audited.
        owner = {
            "civil": "civil-designer",
            "station": "civil-designer",
            "mechanical": "mechanical-designer",
            "factory": "manufacturing-integrator",
            "integration": "configuration-integrator",
        }[package["domain"]]
        if identifier == "SYSTEM-ASSURANCE":
            owner = "configuration-integrator"
        package_rows.append(
            {
                "id": identifier,
                "title": package["title"],
                "domain": package["domain"],
                "owner_role": owner,
                "critic_role": "independent-critic",
                "dependencies": deepcopy(package["dependencies"]),
                "dependency_rule": "Provisional inputs may support research; integrated completion requires accepted exact revisions of every dependency.",
                "authoritative_sources": deepcopy(package["authoritative_sources"]),
                "component_ids": component_ids,
                "components": components,
                "adapter_request": adapter,
                "adapter_coverage": "Only explicitly returned package/component/check IDs count as evaluated; all unreturned work remains open.",
                "variables": deepcopy(package["generative_variables"]),
                "generate": deepcopy(workflow["generate"]),
                "evaluate": deepcopy(workflow["evaluate"]),
                "frozen_inputs": deepcopy(declared.get("frozen_inputs", [])),
                "required_gates": deepcopy(package["required_gates"]),
                "original_completion_predicate": deepcopy(
                    package["completion_predicate"]
                ),
                "interfaces": interface_rows,
                "interface_rule": "Match both parent/child datums, accepted reactions, service/removal envelopes and exact revisions. Missing interface allocation is unknown, never pass.",
                "drawing_ids": sorted(drawings),
                "drawing_definitions": [
                    deepcopy(drawing_definitions[drawing_id])
                    for drawing_id in sorted(drawings)
                ],
                "tooling_ids": deepcopy(declared.get("tooling_ids", [])),
                "reference_control_ids": deepcopy(
                    declared.get("reference_control_ids", [])
                ),
                "declared_controlled_outputs": deepcopy(
                    declared.get("controlled_outputs", [])
                ),
                "declared_verification": deepcopy(declared.get("verification", [])),
                "declared_hold_points": deepcopy(declared.get("hold_points", [])),
                "completion_artifacts": deepcopy(workflow["completion_artifacts"]),
                "local_product_manufacturing_requirements": [
                    {
                        "product_id": row["product_id"],
                        "planning_route": row["planning_route"],
                        "design_reference_envelope_mm": row[
                            "design_reference_envelope_mm"
                        ],
                        "requirements": row["production_data_requirements"],
                        "artifact_ids": [a["artifact_id"] for a in row["artifacts"]],
                    }
                    for row in package_products
                ],
                "production_artifact_requests": deepcopy(artifact_rows),
                "inspection_characteristics": deepcopy(inspection_rows),
                "supplier_configuration_requests": deepcopy(supplier_rows),
                "external_actions": deepcopy(workflow["external_actions"]),
                "next_action": (
                    "Generate provisional detail variants and report actual coverage through "
                    + adapter
                    if adapter
                    else "Commission the configuration-specific model/input or supplier evidence; preserve existing research as provisional."
                ),
                "status": "open",
                "design_complete": False,
                "manufacturing_release": False,
                "physical_release": False,
            }
        )
    # Preserve *all* requests, including actual future issued claims and planned
    # inspections: summaries never substitute for source evidence or authority.
    source_hashes = {row["path"]: row["sha256"] for row in scope["source_inventory"]}
    source_hashes.update(production["sources_sha256"])
    for path in (
        CONTRACT,
        coverage.SCOPE,
        Path(__file__),
        Path(manufacturing.__file__),
        Path(coverage.__file__),
    ):
        source_hashes[path.relative_to(coverage.ROOT).as_posix()] = coverage.sha(path)
    result = {
        "schema": "osr-multi-agent-design-scenario/1",
        "scenario_id": "design-scenario-" + _hash(source_hashes)[:20],
        "source_hashes": dict(sorted(source_hashes.items())),
        "contract": contract,
        "architecture_boundary": deepcopy(scope["architecture_boundary"]),
        "inventory_audit": audit,
        "work_packages": package_rows,
        "manufacturing_audit": production,
        "unallocated_artifact_ids": sorted(
            {r["id"] if "id" in r else r["artifact_id"] for r in requests}
            - {
                r["artifact_id"]
                for p in package_rows
                for r in p["production_artifact_requests"]
            }
        ),
        "unallocated_inspection_ids": sorted(
            {r["id"] for r in production["inspection_characteristics"]}
            - {r["id"] for p in package_rows for r in p["inspection_characteristics"]}
        ),
        "counts": {
            "work_packages": len(package_rows),
            "domains": dict(Counter(p["domain"] for p in package_rows)),
            "source_qualified_component_assignments": sum(
                len(p["components"]) for p in package_rows
            ),
            "component_ids": len({i for p in package_rows for i in p["component_ids"]}),
            "open_packages": len(package_rows),
            "completed_packages": 0,
        },
        "design_complete": False,
        "manufacturing_release": False,
        "physical_release": False,
    }
    if result["unallocated_artifact_ids"] or result["unallocated_inspection_ids"]:
        raise ValueError("unallocated actual production or inspection work")
    return result
