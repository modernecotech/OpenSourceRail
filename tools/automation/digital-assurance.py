#!/usr/bin/env python3
"""Validate and deterministically render the cross-domain pre-build gate."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import tomllib

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "lib/templates/digital-assurance.toml"
FMEA = ROOT / "lib/templates/system-fmea.toml"
INVENTORY_SOURCES = (
    "design/component-catalogue/catalog/buildable-trainset/buildable-trainset-manifest.json",
    "design/component-catalogue/catalog/buildable-stations/station-kit-manifest.json",
    "design/component-catalogue/catalog/buildable-civil/reusable-type-release-register.json",
    "Cargo.toml",
)


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


def _unique(rows: list[dict], label: str) -> None:
    ids = [row.get("id") for row in rows]
    if any(not isinstance(value, str) or not value for value in ids):
        raise ValueError(f"{label} requires non-empty IDs")
    if len(ids) != len(set(ids)):
        raise ValueError(f"duplicate {label} IDs")


def _inventory_domain(item_id: str, title: str, scope: str) -> str:
    """Assign a conservative primary discipline for the preliminary screen."""
    if scope == "software-crate":
        return "embedded-software"
    if scope == "civil-type":
        return "civil"
    text = f"{item_id} {title}".lower()
    thermal_words = ("thermal", "coolant", "cooling", "hvac", "chiller", "refriger", "air-condition")
    if any(word in text for word in thermal_words):
        return "thermal"
    if scope.startswith("station"):
        if any(token in item_id for token in ("-CIV-", "-PLT-", "-CNP-", "-ACC-", "-TRK-", "-DEP-")):
            return "civil"
        return "electrical"
    electrical_words = (
        "battery", "electrical", "cable", "inverter", "motor", "lighting", "charger",
        "converter", "sensor", "control", "electronic", "wiring", "antenna", "radio",
    )
    if any(word in text for word in electrical_words) or any(
        token in item_id for token in ("-AUX-", "-CTRL-", "-HV-", "-LGT-", "-TRC-")
    ):
        return "electrical"
    return "mechanical"


def _inventory_coverage(root: Path) -> list[dict]:
    """Expand every controlled physical item and Rust crate into an FMEA seed.

    These rows prove inventory coverage, not item-specific FMEDA completion.
    Their intentionally open review state prevents a generic family screen from
    being mistaken for production or safety release evidence.
    """
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
        rows.append(
            {
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
            }
        )

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
        normalized = {
            **item,
            "id": item["type_id"],
            "title": item.get("asset_class", item["type_id"]),
            "verification": [
                "project-specific design release",
                "independent engineering check",
                "inspection and test plan",
            ],
        }
        add("civil-type", "component", normalized, INVENTORY_SOURCES[2])

    for member in cargo.get("workspace", {}).get("members", []):
        crate_path = root / member / "Cargo.toml"
        crate = tomllib.loads(crate_path.read_text(encoding="utf-8"))
        package = crate.get("package", {})
        add(
            "software-crate",
            "component",
            {"id": package.get("name", Path(member).name), "title": package.get("description", Path(member).name)},
            str(crate_path.relative_to(root)),
        )

    _unique([{"id": row["inventory_id"]} for row in rows], "inventory coverage")
    if not rows or any(not row["existing_controls"] and row["scope"] != "software-crate" for row in rows):
        raise ValueError("physical inventory rows require existing acceptance or hold-point controls")
    return sorted(rows, key=lambda row: row["inventory_id"])


def compile_assurance(root: Path = ROOT, config: dict | None = None, fmea: dict | None = None) -> dict:
    config = config or _read(root / CONFIG.relative_to(ROOT))
    fmea = fmea or _read(root / FMEA.relative_to(ROOT))
    standards = config.get("standards", [])
    checks = config.get("checks", [])
    modes = fmea.get("failure_modes", [])
    if tuple(fmea.get("meta", {}).get("inventory_sources", [])) != INVENTORY_SOURCES:
        raise ValueError("FMEA inventory sources must enumerate the controlled train, station, civil and software inventories")
    inventory = _inventory_coverage(root)
    _unique(standards, "standard")
    _unique(checks, "digital check")
    _unique(modes, "failure mode")

    standard_ids = {row["id"] for row in standards}
    required_domains = set(fmea.get("meta", {}).get("required_domains", []))
    required_levels = set(fmea.get("meta", {}).get("required_levels", []))
    if not required_domains or not required_levels:
        raise ValueError("FMEA required domains and levels must be declared")

    evidence_hashes: dict[str, str] = {}
    compiled_checks = []
    for row in checks:
        unknown = set(row.get("standard_ids", [])) - standard_ids
        if unknown:
            raise ValueError(f"{row['id']} references unknown standards: {sorted(unknown)}")
        if not row.get("required_digital"):
            raise ValueError(f"{row['id']} must be fail-closed as required_digital")
        paths = row.get("evidence", [])
        if not paths:
            raise ValueError(f"{row['id']} has no evidence")
        for value in paths:
            path = _repo_path(root, value)
            evidence_hashes[value] = hashlib.sha256(path.read_bytes()).hexdigest()
        compiled_checks.append({**row, "status": "pass"})

    matrix = {(domain, level): 0 for domain in required_domains for level in required_levels}
    compiled_modes = []
    high_risk = int(fmea.get("meta", {}).get("high_risk_rpn", 40))
    for row in modes:
        domain, level = row.get("domain"), row.get("level")
        if (domain, level) not in matrix:
            raise ValueError(f"{row['id']} has unsupported domain/level {domain}/{level}")
        if not re.fullmatch(r"FMEA-[A-Z]+-[A-Z]\d{2}", row["id"]):
            raise ValueError(f"invalid failure-mode ID: {row['id']}")
        for field in ("item", "function", "mode", "local_effect", "system_effect", "cause", "detection"):
            if not row.get(field):
                raise ValueError(f"{row['id']} missing {field}")
        ratings = [row.get(name) for name in ("severity", "occurrence", "detection_rating")]
        if any(not isinstance(value, int) or not 1 <= value <= 5 for value in ratings):
            raise ValueError(f"{row['id']} ratings must be integers from 1 to 5")
        if not row.get("controls") or not row.get("evidence"):
            raise ValueError(f"{row['id']} requires controls and evidence")
        if row["severity"] == 5 and not row.get("physical_evidence_required"):
            raise ValueError(f"{row['id']} catastrophic mode cannot waive physical evidence")
        for value in row["evidence"]:
            path = _repo_path(root, value)
            evidence_hashes[value] = hashlib.sha256(path.read_bytes()).hexdigest()
        rpn = ratings[0] * ratings[1] * ratings[2]
        compiled_modes.append({**row, "rpn": rpn, "priority": "high" if rpn >= high_risk else "managed"})
        matrix[(domain, level)] += 1
    missing = [f"{domain}/{level}" for (domain, level), count in sorted(matrix.items()) if count == 0]
    if missing:
        raise ValueError(f"FMEA coverage gaps: {', '.join(missing)}")

    source_hashes = {}
    for relative in ("lib/templates/digital-assurance.toml", "lib/templates/system-fmea.toml", "lib/templates/corridor-resilience.toml", *INVENTORY_SOURCES):
        path = _repo_path(root, relative)
        source_hashes[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
    fingerprint_payload = json.dumps({"sources": source_hashes, "evidence": evidence_hashes}, sort_keys=True, separators=(",", ":"))
    fingerprint = hashlib.sha256(fingerprint_payload.encode()).hexdigest()
    return {
        "schema": config["meta"]["schema"],
        "status": config["meta"]["status"],
        "design_fingerprint_sha256": fingerprint,
        "digital_gate_passed": True,
        "release_ready": False,
        "authority_boundary": config["authority_boundary"],
        "counts": {"standards": len(standards), "digital_checks": len(checks), "failure_modes": len(modes), "inventory_items_screened": len(inventory), "inventory_item_reviews_open": sum(row["release_blocking"] for row in inventory), "physical_evidence_open": sum(bool(row.get("physical_evidence_required")) for row in modes)},
        "standards": standards,
        "checks": compiled_checks,
        "fmea_coverage": [{"domain": domain, "level": level, "count": matrix[(domain, level)]} for domain, level in sorted(matrix)],
        "failure_modes": sorted(compiled_modes, key=lambda row: row["id"]),
        "inventory_coverage": inventory,
        "source_hashes": source_hashes,
        "evidence_hashes": dict(sorted(evidence_hashes.items())),
        "interpretation": "The deterministic design gate passed. Physical tests, site evidence, independent assessment and regulatory acceptance remain open and cannot be replaced by this report.",
    }


def render_markdown(report: dict) -> str:
    lines = [
        "# Deterministic Digital Assurance Report", "",
        "> Design-screening evidence only. This is not certification, permission to manufacture, or permission to operate.", "",
        f"- Design fingerprint: `{report['design_fingerprint_sha256']}`",
        f"- Digital pre-build gate: **{'PASS' if report['digital_gate_passed'] else 'FAIL'}**",
        f"- Physical/revenue release: **{'READY' if report['release_ready'] else 'BLOCKED'}**",
        f"- Scope: {report['counts']['standards']} standards records, {report['counts']['digital_checks']} deterministic checks, {report['counts']['failure_modes']} system failure modes",
        f"- Controlled inventory screened: **{report['counts']['inventory_items_screened']} items**; item-specific reviews open: **{report['counts']['inventory_item_reviews_open']}**",
        f"- Open physical-evidence rows: **{report['counts']['physical_evidence_open']}**", "",
        "## Authority Boundary", "", report["authority_boundary"]["statement"], "",
        "Route selection never grants movement authority. Simulation and analysis reduce redesign risk; they do not waive mandatory physical or independent evidence.", "",
        "## Deterministic Checks", "", "| ID | Check | Standards | Result |", "|---|---|---|---|",
    ]
    for row in report["checks"]:
        lines.append(f"| `{row['id']}` | {row['title']} | {', '.join(row['standard_ids'])} | **{row['status'].upper()}** |")
    lines += ["", "## FMEA Coverage", "", "| Domain | Component | Subsystem | System |", "|---|---:|---:|---:|"]
    coverage = {(row["domain"], row["level"]): row["count"] for row in report["fmea_coverage"]}
    for domain in sorted({row["domain"] for row in report["fmea_coverage"]}):
        lines.append(f"| {domain} | {coverage[(domain, 'component')]} | {coverage[(domain, 'subsystem')]} | {coverage[(domain, 'system')]} |")
    lines += ["", "## Controlled Inventory Screen", "", "Every train product/assembly, station product/assembly, reusable civil type and Rust workspace crate is deterministically included below the JSON report's `inventory_coverage` key. These are preliminary family screens with item-specific analysis and accountable acceptance deliberately open.", "", "| Scope | Items | Open item reviews |", "|---|---:|---:|"]
    inventory_scopes = sorted({row["scope"] for row in report["inventory_coverage"]})
    for scope in inventory_scopes:
        scoped = [row for row in report["inventory_coverage"] if row["scope"] == scope]
        lines.append(f"| {scope} | {len(scoped)} | {sum(row['release_blocking'] for row in scoped)} |")
    lines += ["", "## Failure Modes", "", "| ID | Domain / level | Item | Failure mode | S/O/D | RPN | Physical evidence |", "|---|---|---|---|---:|---:|---|"]
    for row in report["failure_modes"]:
        physical = "open — required" if row["physical_evidence_required"] else "not required"
        lines.append(f"| `{row['id']}` | {row['domain']} / {row['level']} | {row['item']} | {row['mode']} | {row['severity']}/{row['occurrence']}/{row['detection_rating']} | {row['rpn']} | {physical} |")
    lines += ["", "## Standards Profile", "", "| Standard | Digital use | Physical evidence retained |", "|---|---|---|"]
    for row in report["standards"]:
        lines.append(f"| [{row['id']}]({row['source_url']}) | {row['digital_use']} | {', '.join(row['physical_evidence'])} |")
    lines += ["", "## Interpretation", "", report["interpretation"], ""]
    return "\n".join(lines)


def outputs(root: Path = ROOT) -> tuple[str, str]:
    report = compile_assurance(root)
    return render_markdown(report), json.dumps(report, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if tracked reports are stale")
    args = parser.parse_args()
    markdown, data = outputs(ROOT)
    targets = [(ROOT / "docs/certification/digital-assurance-report.md", markdown), (ROOT / "docs/certification/digital-assurance-report.json", data)]
    stale = [path for path, value in targets if not path.is_file() or path.read_text(encoding="utf-8") != value]
    if args.check:
        if stale:
            raise SystemExit("stale digital assurance reports: " + ", ".join(str(path.relative_to(ROOT)) for path in stale))
    else:
        for path, value in targets:
            path.write_text(value, encoding="utf-8")
    report = json.loads(data)
    print(
        "Digital assurance: PASS "
        f"({report['counts']['digital_checks']} checks, "
        f"{report['counts']['failure_modes']} system FMEA rows, "
        f"{report['counts']['inventory_items_screened']} inventory items; "
        "physical release BLOCKED)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
