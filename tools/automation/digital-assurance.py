#!/usr/bin/env python3
"""Compile the deterministic, fail-closed digital standards thread."""
from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import date
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import tomllib

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "lib/templates/digital-assurance.toml"
FMEA = ROOT / "lib/templates/system-fmea.toml"
OUTPUT_MARKDOWN = ROOT / "docs/certification/digital-assurance-report.md"
OUTPUT_JSON = ROOT / "docs/certification/digital-assurance-report.json"
OUTPUT_BASELINE = ROOT / "docs/certification/standards-baseline.md"
INVENTORY_SOURCES = (
    "design/component-catalogue/catalog/buildable-trainset/buildable-trainset-manifest.json",
    "design/component-catalogue/catalog/buildable-stations/station-kit-manifest.json",
    "design/component-catalogue/catalog/buildable-civil/reusable-type-release-register.json",
    "Cargo.toml",
)


def _connected_assurance():
    spec = importlib.util.spec_from_file_location("osr_connected_assurance", ROOT / "tools/automation/connected_assurance.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _subsystem_qualification():
    spec = importlib.util.spec_from_file_location("osr_subsystem_qualification", ROOT / "tools/automation/subsystem_qualification.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _civil_reference():
    spec = importlib.util.spec_from_file_location("osr_civil_reference", ROOT / "tools/automation/civil_reference.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _tacs_assurance():
    spec = importlib.util.spec_from_file_location("osr_tacs_assurance", ROOT / "tools/automation/tacs_assurance.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _read(path: Path) -> dict:
    return tomllib.loads(path.read_text(encoding="utf-8"))


def _repo_path(root: Path, value: str) -> Path:
    path = (root / value).resolve()
    try:
        path.relative_to(root.resolve())
    except ValueError as error:
        raise ValueError(f"repository-relative path required: {value}") from error
    if not path.is_file():
        raise ValueError(f"missing evidence file: {value}")
    return path


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _unique(rows: list[dict], label: str) -> None:
    ids = [row.get("id") for row in rows]
    if any(not isinstance(value, str) or not value for value in ids):
        raise ValueError(f"{label} requires non-empty IDs")
    if len(ids) != len(set(ids)):
        raise ValueError(f"duplicate {label} IDs")


def _iso_date(value: object, label: str) -> date:
    if not isinstance(value, str):
        raise ValueError(f"{label} must be an ISO date string")
    try:
        return date.fromisoformat(value)
    except ValueError as error:
        raise ValueError(f"{label} must be YYYY-MM-DD") from error


def _inventory_domain(item_id: str, title: str, scope: str) -> str:
    if scope == "software-crate":
        return "embedded-software"
    if scope == "civil-type":
        return "civil"
    text = f"{item_id} {title}".lower()
    if any(word in text for word in ("thermal", "coolant", "cooling", "hvac", "chiller", "refriger", "air-condition")):
        return "thermal"
    if scope.startswith("station"):
        if any(token in item_id for token in ("-CIV-", "-PLT-", "-CNP-", "-ACC-", "-TRK-", "-DEP-")):
            return "civil"
        return "electrical"
    electrical = (
        "battery", "electrical", "cable", "inverter", "motor", "lighting", "charger",
        "converter", "sensor", "control", "electronic", "wiring", "antenna", "radio",
    )
    if any(word in text for word in electrical) or any(
        token in item_id for token in ("-AUX-", "-CTRL-", "-HV-", "-LGT-", "-TRC-")
    ):
        return "electrical"
    return "mechanical"


def _inventory_coverage(root: Path) -> list[dict]:
    """Expand every controlled physical item and Rust crate into an open FMEA seed."""
    train_path, station_path, civil_path, cargo_path = [root / value for value in INVENTORY_SOURCES]
    train = json.loads(train_path.read_text(encoding="utf-8"))
    station = json.loads(station_path.read_text(encoding="utf-8"))
    civil = json.loads(civil_path.read_text(encoding="utf-8"))
    cargo = tomllib.loads(cargo_path.read_text(encoding="utf-8"))
    rows: list[dict] = []

    def add(scope: str, level: str, item: dict, evidence: str) -> None:
        item_id = str(item["id"])
        title = str(item.get("title") or item.get("asset_class") or item_id)
        controls = item.get("acceptance") or item.get("hold_points") or item.get("verification") or []
        rows.append({
            "inventory_id": f"{scope}:{item_id}",
            "item_id": item_id,
            "item": title,
            "scope": scope,
            "level": level,
            "domain": _inventory_domain(item_id, title, scope),
            "preliminary_failure_mode": "loss, degradation, incorrect output or unintended operation",
            "preliminary_effect": "loss or degradation of the parent function; item-specific local and end effects require accountable review",
            "existing_controls": list(controls),
            "evidence": evidence,
            "review_status": "preliminary-family-screen-item-analysis-open",
            "release_blocking": True,
        })

    for item in train.get("product_items", []):
        add("train-product", "component", item, INVENTORY_SOURCES[0])
    for item in train.get("assemblies", []):
        add("train-assembly", "subsystem", item, INVENTORY_SOURCES[0])
    station_products: dict[str, dict] = {}
    station_assemblies: dict[str, dict] = {}
    for variant in station.get("variants", []):
        station_products.update({str(item["id"]): item for item in variant.get("product_items", [])})
        station_assemblies.update({str(item["id"]): item for item in variant.get("assemblies", [])})
    for item in station_products.values():
        add("station-product", "component", item, INVENTORY_SOURCES[1])
    for item in station_assemblies.values():
        add("station-assembly", "subsystem", item, INVENTORY_SOURCES[1])
    for item in civil.get("type_register", []):
        add(
            "civil-type",
            "component",
            {**item, "id": item["type_id"], "title": item.get("asset_class", item["type_id"]),
             "verification": ["project-specific design release", "independent engineering check", "inspection and test plan"]},
            INVENTORY_SOURCES[2],
        )
    for member in cargo.get("workspace", {}).get("members", []):
        crate_path = root / member / "Cargo.toml"
        package = tomllib.loads(crate_path.read_text(encoding="utf-8")).get("package", {})
        add(
            "software-crate", "component",
            {"id": package.get("name", Path(member).name), "title": package.get("description", Path(member).name)},
            str(crate_path.relative_to(root)),
        )
    _unique([{"id": row["inventory_id"]} for row in rows], "inventory coverage")
    if not rows or any(not row["existing_controls"] and row["scope"] != "software-crate" for row in rows):
        raise ValueError("physical inventory rows require existing acceptance or hold-point controls")
    return sorted(rows, key=lambda row: row["inventory_id"])


def _validate_registry(config: dict, today: date) -> dict:
    meta = config.get("meta", {})
    standards = config.get("standards", [])
    profiles = config.get("profiles", [])
    controls = config.get("controls", [])
    applicability = config.get("applicability_inputs", [])
    for rows, label in ((standards, "standard"), (profiles, "profile"), (controls, "control"), (applicability, "applicability input")):
        _unique(rows, label)
    standard_ids = {row["id"] for row in standards}
    control_ids = {row["id"] for row in controls}
    required_domains = set(meta.get("required_domains", []))
    required_stages = set(meta.get("required_lifecycle_stages", []))
    registry_due = _iso_date(meta.get("next_registry_review_due"), "meta.next_registry_review_due")
    if meta.get("standards_review_enforced") and today > registry_due:
        raise ValueError(f"standards registry review overdue since {registry_due.isoformat()}")
    standard_due_dates: list[date] = []
    for row in standards:
        required = (
            "title", "publisher", "edition", "status_on_review_date", "jurisdiction", "domains",
            "lifecycle_stages", "source_url", "source_reviewed_on", "next_review_due", "digital_use",
            "physical_evidence", "licensed_text_required",
        )
        missing = [field for field in required if field not in row or row[field] in ("", [])]
        if missing:
            raise ValueError(f"standard {row['id']} missing {missing}")
        if not str(row["source_url"]).startswith("https://"):
            raise ValueError(f"standard {row['id']} requires an authoritative HTTPS source")
        reviewed = _iso_date(row["source_reviewed_on"], f"{row['id']}.source_reviewed_on")
        due = _iso_date(row["next_review_due"], f"{row['id']}.next_review_due")
        if due <= reviewed:
            raise ValueError(f"standard {row['id']} next review must follow source review")
        if meta.get("standards_review_enforced") and today > due:
            raise ValueError(f"standard metadata review overdue: {row['id']} ({due.isoformat()})")
        standard_due_dates.append(due)
    profile_refs = set()
    for row in profiles:
        unknown = set(row.get("standard_ids", [])) - standard_ids
        if unknown or not row.get("decision"):
            raise ValueError(f"profile {row['id']} invalid standards/decision: {sorted(unknown)}")
        profile_refs.update(row["standard_ids"])
    domain_coverage: set[str] = set()
    stage_coverage: set[str] = set()
    control_refs: set[str] = set()
    for row in controls:
        unknown = set(row.get("standard_ids", [])) - standard_ids
        if unknown:
            raise ValueError(f"control {row['id']} references unknown standards: {sorted(unknown)}")
        if row.get("decision_gate") not in {"G1", "G2", "G3", "G4"}:
            raise ValueError(f"control {row['id']} requires a G1-G4 decision gate")
        if not row.get("verification"):
            raise ValueError(f"control {row['id']} requires verification methods")
        domain_coverage.update(row.get("domains", []))
        stage_coverage.update(row.get("lifecycle_stages", []))
        control_refs.update(row["standard_ids"])
    if standard_ids - profile_refs or standard_ids - control_refs:
        raise ValueError(
            "unmapped standards; profiles=" + str(sorted(standard_ids - profile_refs))
            + ", controls=" + str(sorted(standard_ids - control_refs))
        )
    if required_domains - domain_coverage or required_stages - stage_coverage:
        raise ValueError(
            "standards control coverage gaps; domains=" + str(sorted(required_domains - domain_coverage))
            + ", lifecycle=" + str(sorted(required_stages - stage_coverage))
        )
    if any(not row.get("required") or row.get("state") != "deployment-input-open" for row in applicability):
        raise ValueError("all applicability inputs must fail closed as open deployment inputs")
    return {
        "standard_ids": standard_ids,
        "control_ids": control_ids,
        "registry_reviewed_on": meta["standards_reviewed_on"],
        "next_review_due": min([registry_due, *standard_due_dates]).isoformat(),
        "registry_current": True,
    }


def compile_assurance(
    root: Path = ROOT,
    config: dict | None = None,
    fmea: dict | None = None,
    *,
    today: date | None = None,
) -> dict:
    config = config or _read(root / CONFIG.relative_to(ROOT))
    fmea = fmea or _read(root / FMEA.relative_to(ROOT))
    today = today or date.today()
    registry = _validate_registry(config, today)
    standards = config.get("standards", [])
    profiles = config.get("profiles", [])
    controls = config.get("controls", [])
    checks = config.get("checks", [])
    modes = fmea.get("failure_modes", [])
    if tuple(fmea.get("meta", {}).get("inventory_sources", [])) != INVENTORY_SOURCES:
        raise ValueError("FMEA inventory sources must enumerate the controlled train, station, civil and software inventories")
    inventory = _inventory_coverage(root)
    _unique(checks, "digital check")
    _unique(modes, "failure mode")

    evidence_hashes: dict[str, str] = {}
    evidence_manifest: dict[str, dict] = {}
    impact: dict[str, dict[str, set[str]]] = defaultdict(lambda: {"checks": set(), "controls": set(), "standards": set(), "failure_modes": set()})
    compiled_checks = []
    controls_by_id = {row["id"]: row for row in controls}
    for row in checks:
        unknown_standards = set(row.get("standard_ids", [])) - registry["standard_ids"]
        unknown_controls = set(row.get("control_ids", [])) - registry["control_ids"]
        if unknown_standards or unknown_controls:
            raise ValueError(f"{row['id']} unknown standards={sorted(unknown_standards)} controls={sorted(unknown_controls)}")
        if not row.get("required_digital") or not row.get("evidence"):
            raise ValueError(f"{row['id']} must be required and carry evidence")
        mapped_standards = {value for control_id in row["control_ids"] for value in controls_by_id[control_id]["standard_ids"]}
        if set(row["standard_ids"]) - mapped_standards:
            raise ValueError(f"{row['id']} standards are not covered by its controls")
        for value in row["evidence"]:
            path = _repo_path(root, value)
            digest = _digest(path)
            evidence_hashes[value] = digest
            evidence_manifest[value] = {"sha256": digest, "size_bytes": path.stat().st_size, "state": "generated-unreviewed"}
            impact[value]["checks"].add(row["id"])
            impact[value]["controls"].update(row["control_ids"])
            impact[value]["standards"].update(row["standard_ids"])
        compiled_checks.append({
            **row,
            "machine_status": "evidence-linked-and-hashed",
            "conformity_status": "not-assessed",
        })

    required_domains = set(fmea.get("meta", {}).get("required_domains", []))
    required_levels = set(fmea.get("meta", {}).get("required_levels", []))
    if not required_domains or not required_levels:
        raise ValueError("FMEA required domains and levels must be declared")
    matrix = {(domain, level): 0 for domain in required_domains for level in required_levels}
    compiled_modes = []
    high_risk = int(fmea.get("meta", {}).get("high_risk_rpn", 40))
    for row in modes:
        domain, level = row.get("domain"), row.get("level")
        if (domain, level) not in matrix:
            raise ValueError(f"{row['id']} has unsupported domain/level {domain}/{level}")
        if not re.fullmatch(r"FMEA-[A-Z]+-[A-Z]\d{2}", row["id"]):
            raise ValueError(f"invalid failure-mode ID: {row['id']}")
        required = ("item", "function", "mode", "local_effect", "system_effect", "cause", "detection")
        if any(not row.get(field) for field in required):
            raise ValueError(f"{row['id']} missing required descriptive field")
        ratings = [row.get(name) for name in ("severity", "occurrence", "detection_rating")]
        if any(type(value) is not int or not 1 <= value <= 5 for value in (ratings[0], ratings[2])):
            raise ValueError(f"{row['id']} severity/detection ratings must be integers from 1 to 5")
        if ratings[1] != "unknown" and (type(ratings[1]) is not int or not 1 <= ratings[1] <= 5):
            raise ValueError(f"{row['id']} occurrence must be 1 to 5 or unknown")
        if not row.get("controls") or not row.get("evidence"):
            raise ValueError(f"{row['id']} requires controls and evidence")
        if row["severity"] == 5 and not row.get("physical_evidence_required"):
            raise ValueError(f"{row['id']} catastrophic mode cannot waive physical evidence")
        for value in row["evidence"]:
            path = _repo_path(root, value)
            digest = _digest(path)
            evidence_hashes[value] = digest
            evidence_manifest[value] = {"sha256": digest, "size_bytes": path.stat().st_size, "state": "generated-unreviewed"}
            impact[value]["failure_modes"].add(row["id"])
            impact[value]["controls"].add("STD-CTRL-003")
            impact[value]["standards"].add("IEC-60812-2018")
        rpn = None if ratings[1] == "unknown" else ratings[0] * ratings[1] * ratings[2]
        priority = ("mandatory-safety-review" if ratings[0] == 5 else
                    "evidence-gap-review" if rpn is None else
                    "high" if rpn >= high_risk else "managed")
        compiled_modes.append({**row, "rpn": rpn, "priority": priority,
                               "occurrence_evidence_gap": ratings[1] == "unknown" or not row.get("occurrence_basis"),
                               "safety_review_required": ratings[0] == 5})
        matrix[(domain, level)] += 1
    missing = [f"{domain}/{level}" for (domain, level), count in sorted(matrix.items()) if count == 0]
    if missing:
        raise ValueError(f"FMEA coverage gaps: {', '.join(missing)}")

    source_hashes = {}
    source_paths = ("lib/templates/digital-assurance.toml", "lib/templates/system-fmea.toml", "lib/templates/corridor-resilience.toml", *INVENTORY_SOURCES)
    for relative in source_paths:
        path = _repo_path(root, relative)
        source_hashes[relative] = _digest(path)
        impact[relative]["controls"].update({"STD-CTRL-001", "STD-CTRL-003", "STD-CTRL-016"})
    connected = _connected_assurance().compile_thread(root, today=today)
    source_hashes.update(connected["source_hashes"])
    qualification = _subsystem_qualification().compile_package(root,today=today)
    source_hashes.update(qualification["source_hashes"])
    civil = _civil_reference().compile_package(root)
    source_hashes.update(civil["source_hashes"])
    for relative in civil["source_hashes"]:
        impact[relative]["controls"].update({"STD-CTRL-003", "STD-CTRL-016"})
    tacs = _tacs_assurance().compile_package(root)
    source_hashes.update(tacs["source_hashes"])
    for relative in tacs["source_hashes"]:
        impact[relative]["controls"].update({"STD-CTRL-003", "STD-CTRL-016"})
    fingerprint_payload = json.dumps({"sources": source_hashes, "evidence": evidence_hashes,
                                     "engineering": connected["fingerprint"]}, sort_keys=True, separators=(",", ":"))
    fingerprint = hashlib.sha256(fingerprint_payload.encode()).hexdigest()
    impact_index = {
        path: {key: sorted(values) for key, values in dimensions.items() if values}
        for path, dimensions in sorted(impact.items())
    }
    return {
        "schema": config["meta"]["schema"],
        "status": config["meta"]["status"],
        "design_fingerprint_sha256": fingerprint,
        "digital_gate_passed": True,
        "digital_coherence_gate": "pass",
        "conformity_state": "not-assessed",
        "release_ready": False,
        "authority_boundary": config["authority_boundary"],
        "evidence_policy": config["evidence_policy"],
        "standards_registry": {**registry, "standard_ids": sorted(registry["standard_ids"]), "control_ids": sorted(registry["control_ids"])},
        "counts": {
            "standards": len(standards), "profiles": len(profiles), "control_objectives": len(controls),
            "applicability_inputs_open": len(config["applicability_inputs"]), "digital_checks": len(checks),
            "failure_modes": len(modes), "inventory_items_screened": len(inventory),
            "inventory_item_reviews_open": sum(row["release_blocking"] for row in inventory),
            "physical_evidence_open": sum(bool(row.get("physical_evidence_required")) for row in modes),
        },
        "applicability_inputs": config["applicability_inputs"],
        "standards": standards,
        "profiles": profiles,
        "controls": [{**row, "repository_state": "mapped-not-assessed", "decision_state": "open"} for row in controls],
        "checks": compiled_checks,
        "fmea_coverage": [{"domain": domain, "level": level, "count": matrix[(domain, level)]} for domain, level in sorted(matrix)],
        "failure_modes": sorted(compiled_modes, key=lambda row: row["id"]),
        "inventory_coverage": inventory,
        "connected_engineering": connected,
        "subsystem_qualification": qualification,
        "civil_reference": civil,
        "tacs": tacs,
        "source_hashes": source_hashes,
        "evidence_hashes": dict(sorted(evidence_hashes.items())),
        "evidence_manifest": dict(sorted(evidence_manifest.items())),
        "change_impact_index": impact_index,
        "interpretation": "The deterministic evidence-coherence gate passed. Standards applicability, clause-level assessment, physical tests, site evidence, independent assessment and regulatory acceptance remain open.",
    }


def change_impact(previous: dict, current: dict) -> dict:
    """Return controls and decisions invalidated by changed hashed inputs."""
    before = {**previous.get("source_hashes", {}), **previous.get("evidence_hashes", {})}
    after = {**current.get("source_hashes", {}), **current.get("evidence_hashes", {})}
    changed = sorted(path for path in set(before) | set(after) if before.get(path) != after.get(path))
    dimensions: dict[str, set[str]] = defaultdict(set)
    index = current.get("change_impact_index", {})
    old_index = previous.get("change_impact_index", {})
    for path in changed:
        for source_index in (index, old_index):
            for key, values in source_index.get(path, {}).items():
                dimensions[key].update(values)
    engineering_impact = None
    if previous.get("connected_engineering") and current.get("connected_engineering"):
        engineering_impact = _connected_assurance().change_impact(previous["connected_engineering"], current["connected_engineering"])
        for key, values in engineering_impact["impacted"].items():
            dimensions[key].update(values)
    civil_impact = None
    if previous.get("civil_reference") and current.get("civil_reference"):
        civil_impact = _connected_assurance().change_impact(previous["civil_reference"]["graph"], current["civil_reference"]["graph"])
        for key, values in civil_impact["impacted"].items():
            dimensions[key].update(values)
    tacs_impact = None
    if previous.get("tacs") and current.get("tacs"):
        tacs_impact = _connected_assurance().change_impact(previous["tacs"]["graph"], current["tacs"]["graph"])
        for key, values in tacs_impact["impacted"].items():
            dimensions[key].update(values)
    return {
        "baseline_fingerprint": previous.get("design_fingerprint_sha256"),
        "current_fingerprint": current.get("design_fingerprint_sha256"),
        "changed_paths": changed,
        "impacted": {key: sorted(values) for key, values in sorted(dimensions.items())},
        "engineering_impact": engineering_impact,
        "civil_impact": civil_impact,
        "tacs_impact": tacs_impact,
        "decision": "reopen-affected-controls-and-dependent-gates" if changed or (engineering_impact and engineering_impact["seeds"]) or (civil_impact and civil_impact["seeds"]) or (tacs_impact and tacs_impact["seeds"]) else "no-hashed-input-change",
        "release_ready": False,
    }


def render_markdown(report: dict) -> str:
    counts = report["counts"]
    lines = [
        "# Digital standards-adherence report", "",
        "> Deterministic evidence-coherence result—not certification, conformity, construction release or permission to operate.", "",
        f"- Design fingerprint: `{report['design_fingerprint_sha256']}`",
        f"- Digital evidence-coherence gate: **{report['digital_coherence_gate'].upper()}**",
        f"- Standards conformity: **{report['conformity_state'].upper()}**",
        f"- Physical/revenue release: **{'READY' if report['release_ready'] else 'BLOCKED'}**",
        f"- Scope: **{counts['standards']}** publisher records, **{counts['profiles']}** assurance profiles, **{counts['control_objectives']}** control objectives and **{counts['digital_checks']}** repository checks",
        f"- Inventory: **{counts['inventory_items_screened']}** engineering items screened; **{counts['inventory_item_reviews_open']}** item reviews remain open",
        f"- Registry reviewed: {report['standards_registry']['registry_reviewed_on']}; next mandatory review: **{report['standards_registry']['next_review_due']}**", "",
        "## What the result means", "", report["authority_boundary"]["statement"], "",
        "The compiler validates identities, mappings, coverage, evidence paths, hashes, review dates and fail-closed states. It deliberately leaves deployment applicability, licensed clause assessment, physical evidence and every competent decision open.", "",
        "## Digital thread", "",
        "```text", "publisher record + deployment law + intended use", "  → applicability decision and licensed clauses", "    → OSR control objective", "      → requirement / hazard / design item", "        → method + acceptance criterion + configuration", "          → raw evidence + hash + reviewer + validity", "            → G1–G4 decision and conditions of use", "              → change impact / expiry / field feedback", "```", "",
        "## Open applicability inputs", "", "| ID | Deployment input | State |", "|---|---|---|",
    ]
    for row in report["applicability_inputs"]:
        lines.append(f"| `{row['id']}` | {row['title']} | `{row['state']}` |")
    lines += ["", "## Assurance profiles", "", "| Profile | Standards | Decision boundary |", "|---|---:|---|"]
    for row in report["profiles"]:
        lines.append(f"| `{row['id']}` — {row['title']} | {len(row['standard_ids'])} | {row['decision']} |")
    lines += ["", "## Control objectives", "", "| Control | Gate | Domains | Physical evidence | State |", "|---|---|---|---|---|"]
    for row in report["controls"]:
        physical = "required" if row["physical_evidence_required"] else "depends on child evidence"
        lines.append(f"| `{row['id']}` — {row['title']} | {row['decision_gate']} | {', '.join(row['domains'])} | {physical} | `{row['repository_state']}` |")
    lines += ["", "## Repository evidence checks", "", "| ID | Check | Controls | Machine result | Conformity |", "|---|---|---|---|---|"]
    for row in report["checks"]:
        lines.append(f"| `{row['id']}` | {row['title']} | {', '.join(row['control_ids'])} | `{row['machine_status']}` | `{row['conformity_status']}` |")
    lines += ["", "## Standards registry", "", "| Record | Publisher / edition | Status at review | Jurisdiction | Next review |", "|---|---|---|---|---|"]
    for row in report["standards"]:
        lines.append(f"| [`{row['id']}`]({row['source_url']}) | {row['publisher']} / {row['edition']} | {row['status_on_review_date']} | {row['jurisdiction']} | {row['next_review_due']} |")
    lines += ["", "## FMEA coverage", "", "| Domain | Component | Subsystem | System |", "|---|---:|---:|---:|"]
    coverage = {(row["domain"], row["level"]): row["count"] for row in report["fmea_coverage"]}
    for domain in sorted({row["domain"] for row in report["fmea_coverage"]}):
        lines.append(f"| {domain} | {coverage[(domain, 'component')]} | {coverage[(domain, 'subsystem')]} | {coverage[(domain, 'system')]} |")
    lines += [
        "", "## Evidence and change control", "",
        f"Every evidence object must carry {len(report['evidence_policy']['required_metadata'])} metadata fields. Current repository links are machine state `{report['evidence_policy']['repository_machine_state']}`; no link is silently promoted to reviewed or accepted.", "",
        f"The JSON report contains a path-level `change_impact_index` for {len(report['change_impact_index'])} hashed inputs. Comparing reports identifies changed paths and reopens mapped controls rather than averaging them into a green parent score.", "",
        "## Interpretation", "", report["interpretation"], "",
        "## Connected engineering", "",
        "The [connected engineering example](connected-engineering.md) and [generated report](connected-engineering-report.md) bind battery-cooling failure propagation, requirement criteria, controller scenarios, planned physical tests, synthetic production records and installed occurrences to exact design revisions. The JSON includes dependency traversal and explicit blocked deployment decisions.", "",
        "The [subsystem qualification workflow](subsystem-qualification.md) adds quantitative RAMS screens, controlled rig measurements, model correlation, manufacturing equivalence and six separate decision-readiness states. Physical evidence and deployment decisions remain open.", "",
        "The [civil reference demonstration](../../engineering/assurance/civil-reference/README.md) adds 20/25 m double-track bays, connection and erection controls, measured-result release interfaces and a connected construction/service FMEA. Its graph and controlled source hashes are included in this report and change-impact traversal; site inputs, physical qualification and independent release remain pending.", "",
        "The [train-centred prototype](../../engineering/assurance/tacs/README.md) adds the actual process reference around existing interlocking/ATP/ATO/brake, bounded formal protocol and shared sensor-to-separation/interaction FMEA. Model and firmware changes invalidate execution evidence and traverse procedures and blocked release decisions; physical and operational qualification remain pending.", "",
    ]
    return "\n".join(lines)


def render_baseline(report: dict) -> str:
    lines = [
        "# Current standards applicability baseline", "",
        "> Generated from `lib/templates/digital-assurance.toml`; do not edit by hand.", "",
        "This registry records current publisher metadata and how OpenSourceRail routes evidence. It does **not** reproduce normative clauses or claim applicability or conformity. A deployment must obtain licensed text where required and freeze law, jurisdiction, national adoptions, editions, contracts, intended use and assessment bodies.", "",
        f"Metadata was reviewed on **{report['standards_registry']['registry_reviewed_on']}**. The next fail-closed review is due **{report['standards_registry']['next_review_due']}**.", "",
        "## Publisher records", "", "| Record | Scope used by OSR | Evidence that remains outside the digital gate |", "|---|---|---|",
    ]
    for row in report["standards"]:
        lines.append(f"| [`{row['id']}`]({row['source_url']}) | {row['digital_use']} | {', '.join(row['physical_evidence'])} |")
    lines += [
        "", "## Transition notes", "",
        "- ISO 9001:2026 is the current ISO quality-management edition as of the review date and replaces ISO 9001:2015.",
        "- ISO 22163:2023 with Amendment 1:2024 remains the current railway QMS publisher record and still names ISO 9001:2015; deployments must agree and record the transition basis rather than silently rewriting its normative reference.",
        "- EN 50716:2023 is the current OSR European software baseline; legacy EN 50128/EN 50657 mappings require a recorded national or contractual reason during the transition.",
        "- EN 1990 is deliberately edition-neutral here because the deployment must select its national adoption and National Annex.",
        "- EU Regulation 402/2013 is included only as an EU/contractually adopted example; it is not automatically applicable outside that jurisdiction.", "",
        "## Machine-readable controls", "",
        f"The generated [digital standards report](digital-assurance-report.md) maps {report['counts']['standards']} records through {report['counts']['control_objectives']} control objectives to {report['counts']['digital_checks']} hashed repository checks. Its result is evidence coherence only. The [all-component assurance register](component-assurance-register.md) carries the resulting G0–G4 decision boundary to each controlled item.", "",
    ]
    return "\n".join(lines)


def outputs(root: Path = ROOT) -> tuple[str, str, str]:
    report = compile_assurance(root)
    return render_markdown(report), json.dumps(report, indent=2, sort_keys=True) + "\n", render_baseline(report)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if tracked reports are stale")
    parser.add_argument("--impact-from", type=Path, help="compare a previous JSON report with the current sources")
    args = parser.parse_args()
    markdown, data, baseline = outputs(ROOT)
    report = json.loads(data)
    if args.impact_from:
        previous = json.loads(args.impact_from.read_text(encoding="utf-8"))
        print(json.dumps(change_impact(previous, report), indent=2, sort_keys=True))
        return 0
    targets = [(OUTPUT_MARKDOWN, markdown), (OUTPUT_JSON, data), (OUTPUT_BASELINE, baseline)]
    stale = [path for path, value in targets if not path.is_file() or path.read_text(encoding="utf-8") != value]
    if args.check:
        if stale:
            raise SystemExit("stale digital standards reports: " + ", ".join(str(path.relative_to(ROOT)) for path in stale))
    else:
        for path, value in targets:
            path.write_text(value, encoding="utf-8")
    print(
        "Digital standards thread: COHERENT "
        f"({report['counts']['standards']} records, {report['counts']['control_objectives']} controls, "
        f"{report['counts']['digital_checks']} checks, {report['counts']['inventory_items_screened']} inventory items; "
        "conformity NOT ASSESSED; physical release BLOCKED)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
