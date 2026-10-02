#!/usr/bin/env python3
"""Compile configuration-bound engineering relationships and conservative change impact."""
from __future__ import annotations

import argparse
from collections import defaultdict, deque
from datetime import date
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
CONFIG = "lib/templates/connected-engineering.json"
MANIFEST = "design/component-catalogue/catalog/buildable-trainset/buildable-trainset-manifest.json"
OUTPUT = "docs/certification/connected-engineering-report"
EXECUTION = "engineering/assurance/battery-cooling/controller-execution.json"
COLLECTIONS = ("design_items", "functions", "interfaces", "configurations", "occurrences",
               "hazards", "requirements", "failure_modes", "models", "scenarios", "evidence",
               "production_records", "incidents", "decisions", "obligations")
CLASSES = {"automated-design-check", "engineering-analysis", "software-verification",
           "physical-qualification", "process-evidence", "authority-decision"}
GATES = ("G1", "G2", "G3", "G4")


def fingerprint(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def source(root: Path, value: str) -> Path:
    path = (root / value).resolve()
    if Path(value).is_absolute() or not path.is_relative_to(root.resolve()):
        raise ValueError(f"repository-relative path required: {value}")
    if not path.is_file():
        raise ValueError(f"missing engineering source: {value}")
    return path


def digest(root: Path, value: str) -> str:
    return hashlib.sha256(source(root, value).read_bytes()).hexdigest()


def import_items(root: Path) -> list[dict]:
    manifest = json.loads(source(root, MANIFEST).read_text())
    parents: dict[str, set[str]] = defaultdict(set)
    for row in manifest["assemblies"]:
        for child in row["children"]:
            parents[child].add(row["id"])
    items = []
    for row in [*manifest["product_items"], *manifest["assemblies"]]:
        if row.get("parent"):
            parents[row["id"]].add(row["parent"])
        paths = []
        for value in row.get("source_refs", []):
            if value.endswith(".py"):
                candidates = ["design/component-catalogue/src/osr_mech/" + value,
                              "design/component-catalogue/src/osr_mech/rolling_stock/" + value]
                resolved = next((path for path in candidates if (root / path).is_file()), None)
                if not resolved:
                    raise ValueError(f"missing controlled CAD source: {value}")
                paths.append(resolved)
        definition = {"manifest_definition": row, "cad_baseline": manifest["current_cad_baseline"],
                      "source_hashes": {value: digest(root, value) for value in paths}}
        items.append({"id": row["id"], "title": row["title"], "kind": "design_items",
                      "level": row["layer"], "revision": "sha256:" + fingerprint(definition),
                      "part_of": sorted(parents[row["id"]]), "source": MANIFEST,
                      "source_paths": sorted(paths),
                      "decomposition_rationale": "Manifest boundary; item-specific decomposition and supplier evidence remain open."})
    return items


def _require(row: dict, *fields: str) -> None:
    if any(field not in row or row[field] in (None, "", [], {}) for field in fields):
        raise ValueError(f"{row['id']} missing required fields: {', '.join(fields)}")


def execution_paths(nodes: list[dict]) -> set[str]:
    paths = {CONFIG, MANIFEST, "Cargo.toml", "Cargo.lock", "rust-toolchain.toml", "crates/osr-hvac/Cargo.toml",
             "crates/osr-hvac/src/lib.rs", "tools/automation/connected_assurance.py"}
    configured_items = {value for row in nodes if row["kind"] == "configurations" for value in row["item_revisions"]}
    paths.update(value for row in nodes if row["kind"] == "models" or row["id"] in configured_items
                 for value in row.get("source_paths", []))
    return paths


def compile_thread(root: Path = ROOT, config: dict | None = None, *, today: date | None = None,
                   config_source: str = CONFIG, import_catalog: bool = True, include_controller_execution: bool = True) -> dict:
    config = config if config is not None else json.loads(source(root, config_source).read_text())
    if config.get("schema") != "osr-connected-engineering/1":
        raise ValueError("unsupported connected engineering schema")
    today = today or date.today()
    nodes: dict[str, dict] = {}
    for kind in COLLECTIONS:
        rows = [*(import_items(root) if import_catalog else []), *config.get(kind, [])] if kind == "design_items" else config.get(kind, [])
        for row in rows:
            identifier = row.get("id")
            if not isinstance(identifier, str) or not identifier or identifier in nodes:
                raise ValueError(f"missing or duplicate engineering ID: {identifier}")
            nodes[identifier] = {**row, "kind": kind}
    edges: set[tuple[str, str, str]] = set()
    hashes = {config_source: digest(root, config_source),
              "tools/automation/connected_assurance.py": digest(root, "tools/automation/connected_assurance.py")}
    if import_catalog: hashes[MANIFEST] = digest(root, MANIFEST)

    def ref(identifier: str, kinds: str | tuple[str, ...]) -> dict:
        allowed = (kinds,) if isinstance(kinds, str) else kinds
        if identifier not in nodes or nodes[identifier]["kind"] not in allowed:
            raise ValueError(f"orphan or wrong-kind reference: {identifier}; expected {allowed}")
        return nodes[identifier]

    def link(origin: str, target: str, relation: str) -> None:
        edges.add((origin, target, relation))

    def references(row: dict, field: str, kinds: str | tuple[str, ...], *, reverse: bool = False) -> None:
        for identifier in row.get(field, []):
            ref(identifier, kinds)
            link(row["id"] if reverse else identifier, identifier if reverse else row["id"], field)

    for relationship in config.get("relationships", []):
        origin, target, relation = relationship["from"], relationship["to"], relationship["relation"]
        ref(origin, "design_items")
        ref(target, "functions" if relation == "implements_function" else "design_items")
        if relation not in {"part_of", "depends_on", "implements_function"}:
            raise ValueError(f"unsupported engineering relationship: {relation}")
        link(target, origin, relation) if relation == "depends_on" else link(origin, target, relation)

    for row in list(nodes.values()):
        kind = row["kind"]
        if kind == "design_items":
            _require(row, "title", "revision", "level", "decomposition_rationale")
            references(row, "part_of", "design_items", reverse=True)
            references(row, "depends_on", "design_items")
            references(row, "implements_function", "functions", reverse=True)
        elif kind == "functions":
            _require(row, "title", "owner")
        elif kind == "interfaces":
            _require(row, "endpoints", "parameters", "owner")
            if len(set(row["endpoints"])) < 2:
                raise ValueError(f"{row['id']} interface requires distinct endpoints")
            references(row, "endpoints", "design_items")
            # Interface changes and faults can cross either physical boundary.
            references(row, "endpoints", "design_items", reverse=True)
        elif kind == "configurations":
            _require(row, "deployment", "item_revisions", "initial_state", "status")
            for identifier, revision in row["item_revisions"].items():
                ref(identifier, "design_items")
                if not isinstance(revision, str) or not revision:
                    raise ValueError(f"{row['id']} requires explicit item revisions")
                link(identifier, row["id"], "configuration_applicability")
        elif kind == "occurrences":
            _require(row, "design_item", "design_revision", "configuration_id", "position", "serial_number",
                     "supplier_batch", "maintenance_history", "status")
            ref(row["design_item"], "design_items")
            ref(row["configuration_id"], "configurations")
            link(row["design_item"], row["id"], "installed_as")
            if row.get("part_of"):
                ref(row["part_of"], "occurrences")
                link(row["id"], row["part_of"], "occurrence_part_of")
        elif kind == "hazards":
            _require(row, "consequence", "owner")
        elif kind == "requirements":
            _require(row, "statement", "acceptance_criteria", "allocated_to", "owner", "review_state")
            if row["review_state"] not in {"open", "reviewed", "rejected", "superseded"}:
                raise ValueError(f"{row['id']} invalid requirement review state")
            if row["review_state"] == "reviewed":
                _require(row, "author", "reviewer", "review_reference")
                if row["author"] == row["reviewer"]:
                    raise ValueError(f"{row['id']} reviewer must be independent")
            references(row, "allocated_to", ("design_items", "functions", "interfaces"))
            references(row, "hazard_ids", "hazards", reverse=True)
        elif kind == "failure_modes":
            _require(row, "item_id", "item_revision", "configuration_ids", "function_id", "operating_modes",
                     "environment", "initiating_circumstances", "mode", "causes", "mechanisms", "local_effect",
                     "next_higher_effect", "system_effect", "detection", "mitigation", "risk", "ownership",
                     "requirement_ids", "scenario_ids")
            ref(row["item_id"], "design_items")
            ref(row["function_id"], "functions")
            link(row["item_id"], row["id"], "failure_of")
            link(row["function_id"], row["id"], "failure_of_function")
            references(row, "configuration_ids", "configurations")
            references(row, "affected_interfaces", "interfaces")
            references(row, "propagates_to", "failure_modes", reverse=True)
            references(row, "requirement_ids", "requirements", reverse=True)
            references(row, "scenario_ids", "scenarios", reverse=True)
            _require({"id": row["id"], **row["detection"]}, "mechanism", "coverage_evidence", "delay", "latent_exposure")
            _require({"id": row["id"], **row["mitigation"]}, "action", "response_time", "degraded_state", "recovery_conditions")
            _require({"id": row["id"], **row["ownership"]}, "responsible_role", "action", "deadline", "review_state", "residual_risk_decision")
            date.fromisoformat(row["ownership"]["deadline"])
            risk = row["risk"]
            _require({"id": row["id"], **risk}, "likelihood_basis", "uncertainty", "criticality", "hazard_id")
            if type(risk.get("severity")) is not int or not 1 <= risk["severity"] <= 5:
                raise ValueError(f"{row['id']} severity must be 1 to 5")
            occurrence = risk.get("occurrence")
            if occurrence != "unknown" and (type(occurrence) is not int or not 1 <= occurrence <= 5):
                raise ValueError(f"{row['id']} occurrence must be 1 to 5 or unknown")
            ref(risk["hazard_id"], "hazards")
            link(row["id"], risk["hazard_id"], "hazard_contribution")
            row["priority"] = "mandatory-safety-review" if risk["severity"] == 5 else "evidence-gap-review" if occurrence == "unknown" else "engineering-review"
        elif kind == "models":
            _require(row, "source_paths", "represents", "calibration", "validation_data", "valid_envelope", "limitations", "version")
        elif kind == "scenarios":
            _require(row, "configuration_id", "failure_mode_ids", "requirement_ids", "model_id", "initial_state",
                     "faults", "acceptance_criteria", "validation_relationship", "uncertainty", "status", "operating_mode")
            ref(row["configuration_id"], "configurations")
            ref(row["model_id"], "models")
            link(row["configuration_id"], row["id"], "scenario_configuration")
            link(row["model_id"], row["id"], "scenario_model")
            references(row, "failure_mode_ids", "failure_modes")
            references(row, "requirement_ids", "requirements")
            references(row, "requirement_ids", "requirements", reverse=True)
            expected = {}
            for identifier in row["requirement_ids"]:
                for key, value in nodes[identifier]["acceptance_criteria"].items():
                    if key in expected and expected[key] != value:
                        raise ValueError(f"{row['id']} contradictory requirement criteria")
                    expected[key] = value
            if row["acceptance_criteria"] != expected:
                raise ValueError(f"{row['id']} acceptance criteria must derive from requirements")
            for fault in row["faults"]:
                _require({"id": row["id"], **fault}, "location", "onset", "duration", "magnitude")
                ref(fault["location"], "design_items")
                if fault.get("input_changes") and not set(fault["input_changes"]) <= set(row["initial_state"]):
                    raise ValueError(f"{row['id']} fault input is absent from initial state")
                link(fault["location"], row["id"], "fault_location")
        elif kind == "evidence":
            _require(row, "configuration_id", "verification_class", "requirement_ids", "scenario_ids", "state", "limitations")
            ref(row["configuration_id"], "configurations")
            if row["verification_class"] not in CLASSES or row["state"] not in {"planned", "generated-unreviewed", "reviewed", "rejected", "superseded"}:
                raise ValueError(f"{row['id']} invalid evidence class/state")
            references(row, "scenario_ids", "scenarios")
            references(row, "requirement_ids", "requirements")
            if row["state"] == "reviewed":
                _require(row, "author", "reviewer", "review_reference", "valid_until", "input_hashes", "result_path", "result_sha256", "configuration_fingerprint")
                if row["author"] == row["reviewer"]:
                    raise ValueError(f"{row['id']} reviewer must be independent")
        elif kind == "production_records":
            _require(row, "item_ids", "occurrence_ids", "operation", "requirement_ids", "tool_calibration", "inspection_hold_point", "state")
            references(row, "item_ids", "design_items")
            references(row, "occurrence_ids", "occurrences")
            references(row, "requirement_ids", "requirements")
            references(row, "failure_mode_ids", "failure_modes")
        elif kind == "incidents":
            _require(row, "occurrence_id", "failure_mode_ids", "diagnosis", "corrective_action", "effectiveness_check", "work_order_state", "engineering_handback")
            ref(row["occurrence_id"], "occurrences")
            link(row["occurrence_id"], row["id"], "field_incident")
            references(row, "failure_mode_ids", "failure_modes")
        elif kind == "decisions":
            _require(row, "item_id", "configuration_id", "gate", "evidence_ids", "state", "owner", "integration_evidence_ids")
            ref(row["item_id"], "design_items")
            ref(row["configuration_id"], "configurations")
            if row["gate"] not in GATES or row["state"] not in {"open", "proposed", "rejected", "superseded"}:
                raise ValueError(f"{row['id']} cannot manufacture an accepted gate decision")
            link(row["item_id"], row["id"], "gate_subject")
            link(row["configuration_id"], row["id"], "decision_configuration")
            references(row, "evidence_ids", "evidence")
            references(row, "integration_evidence_ids", "evidence")
            if row["state"] == "proposed":
                _require(row, "author", "reviewer", "review_reference")
                if row["author"] == row["reviewer"]:
                    raise ValueError(f"{row['id']} reviewer must be independent")
        elif kind == "obligations":
            _require(row, "deployment_id", "standard_id", "clause_id", "applicability", "rationale", "verification_class", "requirement_ids", "decision_ids")
            if row["verification_class"] not in CLASSES:
                raise ValueError(f"{row['id']} invalid verification class")
            if row["applicability"] not in {"open", "applicable", "not-applicable-with-rationale", "informative", "superseded"}:
                raise ValueError(f"{row['id']} invalid applicability disposition")
            references(row, "requirement_ids", "requirements", reverse=True)
            references(row, "requirement_ids", "requirements")
            references(row, "decision_ids", "decisions", reverse=True)
        for value in row.get("source_paths", []):
            hashes[value] = digest(root, value)
        if row.get("source_paths"):
            row["source_hashes"] = {value: hashes[value] for value in row["source_paths"]}

    # Containment and failure propagation must be acyclic; shared dependencies may cycle.
    for relation in ("part_of", "occurrence_part_of", "propagates_to"):
        visiting, done = set(), set()
        successors: dict[str, list[str]] = defaultdict(list)
        for origin, target, name in edges:
            if name == relation:
                successors[origin].append(target)
        def visit(identifier: str) -> None:
            if identifier in visiting:
                raise ValueError(f"cycle in {relation}: {identifier}")
            if identifier in done:
                return
            visiting.add(identifier)
            for target in successors[identifier]:
                visit(target)
            visiting.remove(identifier)
            done.add(identifier)
        for identifier in list(successors):
            visit(identifier)

    gaps: dict[str, list[str]] = defaultdict(list)
    for row in nodes.values():
        kind = row["kind"]
        if kind == "configurations":
            for identifier, revision in row["item_revisions"].items():
                if revision != nodes[identifier]["revision"]:
                    gaps[row["id"]].append(f"stale design revision: {identifier}")
        elif kind == "occurrences":
            cfg = nodes[row["configuration_id"]]
            if cfg["item_revisions"].get(row["design_item"]) != row["design_revision"]:
                gaps[row["id"]].append("installed revision differs from configuration")
            if row["design_revision"] != nodes[row["design_item"]]["revision"]:
                gaps[row["id"]].append("design changed; installed applicability requires reassessment")
        elif kind == "failure_modes":
            if row["item_revision"] != nodes[row["item_id"]]["revision"]:
                gaps[row["id"]].append("failure analysis binds an earlier design revision")
            for cfg_id in row["configuration_ids"]:
                if nodes[cfg_id]["item_revisions"].get(row["item_id"]) != row["item_revision"]:
                    gaps[row["id"]].append(f"failure subject absent/different in configuration: {cfg_id}")
            if row["risk"]["occurrence"] == "unknown":
                gaps[row["id"]].append("occurrence evidence unknown")
            if row["ownership"]["review_state"] != "reviewed":
                gaps[row["id"]].append("failure analysis and residual risk unreviewed")
            if row["priority"] == "mandatory-safety-review":
                gaps[row["id"]].append("mandatory safety review requires a controlled decision")
            for identifier in row["requirement_ids"]:
                if not any(identifier in nodes[value]["requirement_ids"] for value in row["scenario_ids"]):
                    gaps[row["id"]].append(f"mitigation lacks a verification scenario: {identifier}")
            uncovered = set(row["operating_modes"]) - {nodes[value]["operating_mode"] for value in row["scenario_ids"]}
            if uncovered:
                gaps[row["id"]].append("operating context verification open: " + ", ".join(sorted(uncovered)))
        elif kind == "requirements" and row["review_state"] != "reviewed":
            gaps[row["id"]].append("acceptance criteria require independent engineering review")
        elif kind == "evidence":
            if row["state"] != "reviewed":
                gaps[row["id"]].append(f"evidence {row['state']}")
            else:
                if row["configuration_fingerprint"] != fingerprint(nodes[row["configuration_id"]]):
                    gaps[row["id"]].append("evidence binds a different configuration record")
                if today > date.fromisoformat(row["valid_until"]):
                    gaps[row["id"]].append("evidence expired")
                if row["configuration_id"] in gaps:
                    gaps[row["id"]].append("evidence configuration stale")
                for value, expected in row["input_hashes"].items():
                    hashes[value] = digest(root, value)
                    if hashes[value] != expected:
                        gaps[row["id"]].append(f"stale evidence input: {value}")
                hashes[row["result_path"]] = digest(root, row["result_path"])
                if hashes[row["result_path"]] != row["result_sha256"]:
                    gaps[row["id"]].append("stale result bytes")
                for identifier in row["requirement_ids"]:
                    if gaps.get(identifier):
                        gaps[row["id"]].append(f"requirement review open: {identifier}")
        elif kind == "incidents" and row["engineering_handback"] != "accepted":
            gaps[row["id"]].append("engineering handback and effectiveness review open")
        elif kind == "obligations" and row["applicability"] == "open":
            gaps[row["id"]].append("deployment applicability and clause selection open")

    # A local record is a review proposal, never an authenticated acceptance.
    decisions = [row for row in nodes.values() if row["kind"] == "decisions"]
    subjects = {(row["item_id"], row["configuration_id"], row["gate"]): row for row in decisions}
    if len(subjects) != len(decisions):
        raise ValueError("duplicate decision subject/configuration/gate")
    for row in decisions:
        blockers = ["controlled deployment acceptance is not authenticated"]
        if row["state"] != "proposed":
            blockers.append(f"decision {row['state']}")
        blockers.extend(gaps.get(row["configuration_id"], []))
        previous_gate = GATES.index(row["gate"]) - 1
        if previous_gate >= 0:
            previous = subjects.get((row["item_id"], row["configuration_id"], GATES[previous_gate]))
            blockers.append(f"prior gate decision open: {GATES[previous_gate]}")
            if previous:
                link(previous["id"], row["id"], "prior_gate")
        if row["item_id"] not in nodes[row["configuration_id"]]["item_revisions"]:
            blockers.append("decision subject missing from configuration")
        for subject in nodes.values():
            if (subject["kind"] == "failure_modes" and subject["item_id"] == row["item_id"]) or (
                subject["kind"] == "requirements" and row["item_id"] in subject["allocated_to"]
            ):
                blockers.extend(f"{subject['id']}: {gap}" for gap in gaps.get(subject["id"], []))
        for identifier in set(row["evidence_ids"] + row["integration_evidence_ids"]):
            evidence = nodes[identifier]
            if evidence["configuration_id"] != row["configuration_id"]:
                blockers.append(f"evidence configuration mismatch: {identifier}")
            blockers.extend(f"{identifier}: {gap}" for gap in gaps.get(identifier, []))
        children = {origin for origin, target, name in edges if target == row["item_id"] and name in {"part_of", "depends_on"}}
        for child in sorted(children):
            dependent = subjects.get((child, row["configuration_id"], row["gate"]))
            blockers.append(f"child/dependency decision open: {child}/{row['gate']}")
            if dependent:
                link(dependent["id"], row["id"], "dependent_gate")
            link(child, row["id"], "required_child_gate")
        if children and row["gate"] in {"G3", "G4"}:
            if not any(nodes[value]["verification_class"] == "physical-qualification" and not gaps.get(value)
                       for value in row["integration_evidence_ids"]):
                blockers.append("reviewed physical integration evidence missing")
        row["blockers"] = sorted(set(blockers))
        row["evaluated_state"] = "blocked"
        gaps[row["id"]].extend(row["blockers"])

    if include_controller_execution and (root / EXECUTION).is_file():
        execution = json.loads(source(root, EXECUTION).read_text())
        hashes[EXECUTION] = digest(root, EXECUTION)
        # Review and physical validation stay open even after a successful controller run.
        required_inputs = execution_paths(list(nodes.values()))
        stale = bool(required_inputs - set(execution["input_hashes"]))
        for value, expected in execution["input_hashes"].items():
            hashes[value] = digest(root, value)
            stale = stale or hashes[value] != expected
        raw_results = json.loads(execution["raw_stdout"])
        if execution.get("schema") != "osr-cooling-controller-execution/1" or len(raw_results) != len(execution["results"]):
            raise ValueError("invalid controller execution bundle")
        for result in execution["results"]:
            row = ref(result["scenario_id"], "scenarios")
            raw = next((value for value in raw_results if value["scenario_id"] == result["scenario_id"]), None)
            if not raw or raw["actual"] != result["actual"] or raw["inputs"] != result["inputs"]:
                raise ValueError("controller execution differs from raw output")
            initial = dict(row["initial_state"])
            for fault in row["faults"]:
                initial.update(fault.get("input_changes", {}))
            passed = initial == result["inputs"] and all(type(result["actual"].get(key)) is type(value) and result["actual"].get(key) == value
                                                        for key, value in row["acceptance_criteria"].items())
            row["controller_execution"] = "stale" if stale or gaps.get(row["configuration_id"]) else "passed-unreviewed" if passed else "failed"

    edge_rows = [{"from": a, "to": b, "relation": c} for a, b, c in sorted(edges)]
    node_rows = sorted(nodes.values(), key=lambda row: row["id"])
    node_hashes = {row["id"]: fingerprint(row) for row in node_rows}
    return {"schema": config["schema"], "scope": config["scope"], "release_ready": False,
            "nodes": node_rows, "edges": edge_rows, "node_hashes": node_hashes,
            "source_hashes": dict(sorted(hashes.items())), "gaps": dict(sorted(gaps.items())),
            "fingerprint": fingerprint({"nodes": node_hashes, "edges": edge_rows, "sources": hashes}),
            "counts": {kind: sum(row["kind"] == kind for row in node_rows) for kind in COLLECTIONS},
            "interpretation": "Relationship checks passed; reviewed physical evidence and controlled deployment decisions remain open."}


def change_impact(previous: dict, current: dict, seeds: list[str] | None = None) -> dict:
    """Traverse both baselines so removals cannot hide former dependants."""
    nodes = {row["id"]: row for row in [*previous["nodes"], *current["nodes"]]}
    changed = sorted(identifier for identifier in set(previous["node_hashes"]) | set(current["node_hashes"])
                     if previous["node_hashes"].get(identifier) != current["node_hashes"].get(identifier))
    old_edges = {fingerprint(row): row for row in previous["edges"]}
    new_edges = {fingerprint(row): row for row in current["edges"]}
    relationships = {"added": [new_edges[key] for key in sorted(new_edges.keys() - old_edges.keys())],
                     "removed": [old_edges[key] for key in sorted(old_edges.keys() - new_edges.keys())]}
    changed_sources = sorted(value for value in set(previous.get("source_hashes", {})) | set(current.get("source_hashes", {}))
                             if previous.get("source_hashes", {}).get(value) != current.get("source_hashes", {}).get(value))
    seed_reasons: dict[str, list[str]] = defaultdict(list)
    for identifier in changed:
        seed_reasons[identifier].append("record changed")
    for disposition, rows in relationships.items():
        for row in rows:
            for identifier in (row["from"], row["to"]):
                seed_reasons[identifier].append(f"relationship {disposition}: {row['from']} / {row['relation']} / {row['to']}")
    for value in changed_sources:
        bound = {row["id"] for row in [*previous["nodes"], *current["nodes"]]
                 if value == row.get("source") or value in row.get("source_paths", [])
                 or value in row.get("input_hashes", {}) or value == row.get("result_path")}
        # Compiler, build and execution sources may have no per-record path field.
        # Unknown source scope conservatively reopens every evidence-bearing record.
        if not bound:
            bound = {identifier for identifier, row in nodes.items()
                     if row["kind"] in {"configurations", "models", "scenarios", "evidence", "decisions"}}
        for identifier in bound:
            seed_reasons[identifier].append(f"controlled source changed: {value}")
    for identifier in seeds or []:
        seed_reasons[identifier].append("explicit impact seed")
    start = sorted(seed_reasons)
    if set(start) - set(nodes):
        raise ValueError("unknown impact seed: " + ", ".join(sorted(set(start) - set(nodes))))
    adjacency: dict[str, set[str]] = defaultdict(set)
    for edge in [*previous["edges"], *current["edges"]]:
        adjacency[edge["from"]].add(edge["to"])
    reasons = {identifier: [identifier] for identifier in start}
    queue = deque(sorted(start))
    while queue:
        identifier = queue.popleft()
        for target in sorted(adjacency[identifier]):
            if target not in reasons:
                reasons[target] = [*reasons[identifier], target]
                queue.append(target)
    impacted: dict[str, list[str]] = defaultdict(list)
    for identifier in sorted(reasons):
        impacted[nodes[identifier]["kind"]].append(identifier)
    return {"changed_records": changed, "changed_relationships": relationships, "changed_sources": changed_sources,
            "seed_reasons": {key: sorted(set(value)) for key, value in sorted(seed_reasons.items())},
            "seeds": sorted(start), "impacted": dict(sorted(impacted.items())),
            "trace_paths": dict(sorted(reasons.items())), "release_ready": False,
            "decision": "reassess-affected-evidence-assets-and-gates" if start else "no-record-change"}


def batch_impact(report: dict, batch: str) -> dict:
    occurrences = [row["id"] for row in report["nodes"] if row["kind"] == "occurrences" and row["supplier_batch"] == batch]
    if not occurrences:
        raise ValueError(f"unknown supplier batch: {batch}")
    return change_impact(report, report, occurrences)


def run_scenarios(root: Path, output: Path) -> dict:
    report = compile_thread(root)
    rows = [row for row in report["nodes"] if row["kind"] == "scenarios" and row["status"] == "controller-executable"]
    if not rows:
        raise ValueError("no executable controller scenarios")
    if any(report["gaps"].get(row["configuration_id"]) for row in rows):
        raise ValueError("cannot execute against stale configuration")
    paths = execution_paths(report["nodes"])
    inputs = {path: digest(root, path) for path in sorted(paths)}
    request = []
    for row in rows:
        initial = dict(row["initial_state"])
        for fault in row["faults"]:
            initial.update(fault.get("input_changes", {}))
        request.append({"scenario_id": row["id"], "inputs": initial})
    command = ["cargo", "run", "--locked", "--quiet", "-p", "osr-hvac", "--example", "cooling_fault_evidence"]
    completed = subprocess.run(command, cwd=root, input=json.dumps(request), capture_output=True, text=True, timeout=180)
    if completed.returncode:
        raise ValueError("controller scenario execution failed: " + completed.stderr[-2000:])
    results = json.loads(completed.stdout)
    if [row["scenario_id"] for row in results] != [row["id"] for row in rows]:
        raise ValueError("controller runner returned different scenario identities")
    for row, result in zip(rows, results):
        result["acceptance_criteria"] = row["acceptance_criteria"]
        result["passed"] = all(type(result["actual"].get(key)) is type(value) and result["actual"].get(key) == value
                               for key, value in row["acceptance_criteria"].items())
        result["configuration_id"] = row["configuration_id"]
    if any(digest(root, path) != expected for path, expected in inputs.items()):
        raise ValueError("inputs changed during execution")
    bundle = {"schema": "osr-cooling-controller-execution/1", "command": command,
              "tool_version": subprocess.check_output(["rustc", "--version"], cwd=root, text=True).strip(),
              "input_hashes": inputs, "results": results, "state": "generated-unreviewed",
              "limitations": "One controller evaluation per case. No flow sensor, transient heat transfer, timing, charging/recovery dynamics or physical validation.",
              "raw_stdout": completed.stdout, "raw_stderr": completed.stderr, "release_ready": False}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(bundle, indent=2, sort_keys=True) + "\n")
    if not all(row["passed"] for row in results):
        raise ValueError("controller criteria failed; raw execution retained at " + str(output))
    return bundle


def render_markdown(report: dict) -> str:
    lines = ["# Connected engineering assurance", "", "> Generated by `tools/automation/connected_assurance.py`.", "",
             report["scope"], "", report["interpretation"], "",
             f"Design fingerprint: `{report['fingerprint']}`. **Physical release: BLOCKED.**", "",
             "## Failure propagation", "", "| Failure | Subject/revision | Local → higher → system effect | Priority |", "|---|---|---|---|"]
    for row in report["nodes"]:
        if row["kind"] == "failure_modes":
            lines.append(f"| {row['id']} | {row['item_id']} / {row['item_revision']} | {row['local_effect']} → {row['next_higher_effect']} → {row['system_effect']} | {row['priority']} |")
    lines += ["", "## Verification scenarios", "", "| Scenario | Scope | Controller execution |", "|---|---|---|"]
    for row in report["nodes"]:
        if row["kind"] == "scenarios":
            lines.append(f"| {row['id']} | {row['status']} | {row.get('controller_execution', 'not-executed')} |")
    lines += ["", "## Unresolved evidence and decisions", "", "| Record | Blockers |", "|---|---|"]
    for identifier, gaps in report["gaps"].items():
        lines.append(f"| {identifier} | {'; '.join(gaps)} |")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--impact-from", type=Path)
    parser.add_argument("--changed-item", action="append")
    parser.add_argument("--batch")
    parser.add_argument("--run-scenarios", action="store_true")
    parser.add_argument("--execution-output", type=Path, default=ROOT / EXECUTION)
    args = parser.parse_args()
    if args.run_scenarios:
        result = run_scenarios(ROOT, args.execution_output)
        print(f"Controller cases: {len(result['results'])} passed; evidence generated-unreviewed: {args.execution_output}")
        return 0
    report = compile_thread()
    if args.impact_from or args.changed_item or args.batch:
        previous = json.loads(args.impact_from.read_text()) if args.impact_from else report
        result = batch_impact(report, args.batch) if args.batch else change_impact(previous, report, args.changed_item)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    targets = {ROOT / (OUTPUT + ".json"): json.dumps(report, indent=2, sort_keys=True) + "\n",
               ROOT / (OUTPUT + ".md"): render_markdown(report)}
    for path, value in targets.items():
        if args.check:
            if not path.is_file() or path.read_text() != value:
                raise SystemExit(f"stale connected engineering report: {path}")
        else:
            path.write_text(value)
    print(f"Connected engineering: {len(report['nodes'])} records, {len(report['edges'])} relationships; release BLOCKED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
