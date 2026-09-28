#!/usr/bin/env python3
"""Generate lifecycle-control coverage for mechanical, station, civil and Rust systems."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
import tomllib


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_JSON = ROOT / "engineering/assurance/subsystem-control-register.json"
OUTPUT_MARKDOWN = ROOT / "engineering/assurance/subsystem-control-register.md"
TRAINSET = ROOT / "design/component-catalogue/catalog/buildable-trainset/buildable-trainset-manifest.json"
STATIONS = ROOT / "design/component-catalogue/catalog/buildable-stations/station-product-reconciliation.json"
CIVIL = ROOT / "design/component-catalogue/catalog/buildable-civil/reusable-type-release-register.json"
GOVERNANCE = ROOT / "deployment/erpnext/config/lifecycle-governance.json"
GOVERNANCE_MODULE = ROOT / "deployment/erpnext/apps/osr_erpnext"
sys.path.insert(0, str(GOVERNANCE_MODULE))

from osr_erpnext.lifecycle_governance import validate_template  # noqa: E402


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def common_record(
    *,
    identifier: str,
    title: str,
    domain: str,
    kind: str,
    source: Path,
    source_status: str,
    profile: dict,
    physical: bool,
    details: dict | None = None,
) -> dict:
    return {
        "id": identifier,
        "title": title,
        "domain": domain,
        "kind": kind,
        "source": relative(source),
        "source_status": source_status,
        "required_records": list(profile["records"]),
        "release_evidence": list(profile["release_evidence"]),
        "physical_identity_eligible": physical,
        "identity_state": (
            "label-template-blocked-until-resolver-and-physical-binding"
            if physical
            else "source-version-artifact-provenance-only"
        ),
        "release_state": "evidence-open-not-released",
        "details": details or {},
    }


def rust_record(member: str, profile: dict) -> dict:
    crate_dir = ROOT / member
    manifest_path = crate_dir / "Cargo.toml"
    manifest = tomllib.loads(manifest_path.read_text(encoding="utf-8"))
    package = manifest["package"]
    name = str(package["name"])
    source_files = sorted((crate_dir / "src").glob("**/*.rs"))
    integration_tests = sorted((crate_dir / "tests").glob("**/*.rs"))
    unit_modules = sum(path.read_text(encoding="utf-8").count("#[cfg(test)]") for path in source_files)
    kani_harnesses = sum(path.read_text(encoding="utf-8").count("#[kani::proof]") for path in source_files + integration_tests)
    boundary = (
        "observation-only"
        if name == "osr-supervision-contract"
        else "lookup-only"
        if name == "osr-lifecycle-identity"
        else "no-deployment-authority-claimed"
    )
    return common_record(
        identifier=name,
        title=str(package.get("description", name)),
        domain="rust",
        kind="crate",
        source=manifest_path,
        source_status="software-development-evidence",
        profile=profile,
        physical=False,
        details={
            "member": member,
            "source_files": len(source_files),
            "integration_test_files": len(integration_tests),
            "unit_test_modules": unit_modules,
            "kani_harnesses": kani_harnesses,
            "authority_boundary": boundary,
            "workspace_version": "0.4.0",
        },
    )


def build_register() -> dict:
    trainset = load_json(TRAINSET)
    stations = load_json(STATIONS)
    civil = load_json(CIVIL)
    governance = validate_template(load_json(GOVERNANCE))
    profiles = governance["subsystem_profiles"]
    records: list[dict] = []

    for row in trainset["product_items"]:
        records.append(common_record(
            identifier=row["id"], title=row["title"], domain="mechanical",
            kind="product", source=TRAINSET, source_status=row["maturity"],
            profile=profiles["mechanical"], physical=True,
            details={"route": row["route"], "parent": row["parent"],
                     "acceptance": row["acceptance"]},
        ))
    for row in trainset["assemblies"]:
        records.append(common_record(
            identifier=row["id"], title=row["title"], domain="mechanical",
            kind="assembly", source=TRAINSET, source_status=row["maturity"],
            profile=profiles["mechanical"], physical=True,
            details={"build_cell": row["build_cell"], "children": row["children"],
                     "hold_points": row["hold_points"]},
        ))
    for row in stations["variants"]:
        records.append(common_record(
            identifier=f"station:{row['archetype']}", title=f"{row['archetype']} station variant",
            domain="station", kind="variant", source=STATIONS,
            source_status="coordinated-design-reference" if row["passed"] else "failed-reconciliation",
            profile=profiles["station"], physical=True,
            details={"products": row["product_count"], "assemblies": row["assembly_count"],
                     "connection_controls": row["connection_control_count"],
                     "definition_sheets": row["definition_sheet_count"]},
        ))
    for row in civil["type_register"]:
        records.append(common_record(
            identifier=row["type_id"], title=row["disposition"], domain="civil",
            kind="reusable-type", source=CIVIL, source_status=row["status"],
            profile=profiles["civil"], physical=True,
            details={"asset_class": row["asset_class"], "ifc_class": row["ifc_class"],
                     "package_id": row["package_id"], "authority": row["authority"]},
        ))

    workspace = tomllib.loads((ROOT / "Cargo.toml").read_text(encoding="utf-8"))
    for member in workspace["workspace"]["members"]:
        records.append(rust_record(member, profiles["rust"]))

    identifiers = [row["id"] for row in records]
    if len(identifiers) != len(set(identifiers)):
        duplicates = sorted(value for value in set(identifiers) if identifiers.count(value) > 1)
        raise ValueError(f"Duplicate subsystem identities: {duplicates}")
    counts: dict[str, int] = {}
    kinds: dict[str, int] = {}
    for row in records:
        counts[row["domain"]] = counts.get(row["domain"], 0) + 1
        key = f"{row['domain']}:{row['kind']}"
        kinds[key] = kinds.get(key, 0) + 1
    if counts != {"mechanical": 146, "station": 7, "civil": 19, "rust": len(workspace["workspace"]["members"])}:
        raise ValueError(f"Unexpected subsystem coverage: {counts}")
    if any(row["release_state"] != "evidence-open-not-released" for row in records):
        raise ValueError("Subsystem register claims unsupported release")

    sources = [TRAINSET, STATIONS, CIVIL, GOVERNANCE, ROOT / "Cargo.toml"]
    return {
        "schema": "osr-subsystem-control-register/1",
        "authority_boundary": governance["authority_boundary"],
        "summary": {
            "records": len(records),
            "domains": dict(sorted(counts.items())),
            "kinds": dict(sorted(kinds.items())),
            "role_templates": len(governance["role_templates"]),
            "record_templates": len(governance["record_templates"]),
            "workflow_templates": len(governance["workflow_templates"]),
            "management_cadences": len(governance["management_cadence"]),
            "physical_identity_templates": sum(row["physical_identity_eligible"] for row in records),
            "printable_qr_labels": 0,
        },
        "sources": {relative(path): digest(path) for path in sources},
        "best_practice_basis": governance["sources"],
        "records": records,
        "validation": {
            "passed": True,
            "unique_identity": True,
            "complete_source_coverage": True,
            "all_release_evidence_open": True,
            "qr_fail_closed": True,
        },
    }


def markdown(report: dict) -> str:
    summary = report["summary"]
    control_summary = (
        f"{summary['role_templates']} role templates, "
        f"{summary['record_templates']} record templates, "
        f"{summary['workflow_templates']} workflow templates and "
        f"{summary['management_cadences']} management cadences"
    )
    basis = "\n".join(
        f"| `{row['id']}` | [{row['title']}]({row['url']}) | {row['applied_as']} |"
        for row in report["best_practice_basis"]
    )
    return f"""# Subsystem lifecycle-control register

> Generated by `python3 engineering/subsystem_control_register.py`. Do not edit this file or its JSON partner by hand.

This register joins every controlled mechanical product and assembly, station
variant, reusable civil type and Rust workspace crate to the same configuration,
quality, competence, management and identity controls. It routes evidence; it
does not claim fabrication, construction, software deployment or railway release.

## Coverage

| Domain | Controlled records |
|---|---:|
| LM3 mechanical products and assemblies | {summary['domains']['mechanical']} |
| Station variants | {summary['domains']['station']} |
| Reusable civil types | {summary['domains']['civil']} |
| Rust crates | {summary['domains']['rust']} |
| **Total** | **{summary['records']}** |

The common control system contains **{control_summary}**.
There are {summary['physical_identity_templates']} physical identity candidates.
There are deliberately **zero printable QR labels** until a deployment binds real
assets to an operator-controlled HTTPS resolver and checks the physical labels.

## Best-practice basis

| Basis | Authoritative source | Applied here as |
|---|---|---|
{basis}

These sources inform the templates; they do not certify OSR or replace the
contract, applicable law, national standards, competent engineers, operators or
independent assessors.

## Control model

- Mechanical and station records require configuration, inspection/test,
  calibration, nonconformance and asset-identity evidence.
- Civil records add survey/ground, temporary-works, concealed-work, as-built and
  handover evidence.
- Rust records require locked source/toolchain, peer review, all-feature tests
  and linting, vulnerability disposition, reproducible artifacts and an explicit
  deployment-authority boundary.
- The QR contract is lookup-only. It carries no personal data, credential,
  command, approval, isolation or movement authority.

The complete per-record controls, source paths, maturity states and evidence
requirements are in [subsystem-control-register.json](subsystem-control-register.json).
The editable governance source is
[`lifecycle-governance.json`](../../deployment/erpnext/config/lifecycle-governance.json).
"""


def serialise(report: dict) -> str:
    return json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def check(path: Path, expected: str) -> bool:
    if not path.is_file() or path.read_text(encoding="utf-8") != expected:
        print(f"stale subsystem control register: {relative(path)}", file=sys.stderr)
        return False
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    report = build_register()
    json_text = serialise(report)
    markdown_text = markdown(report)
    if args.check:
        return 0 if check(OUTPUT_JSON, json_text) and check(OUTPUT_MARKDOWN, markdown_text) else 1
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(json_text, encoding="utf-8")
    OUTPUT_MARKDOWN.write_text(markdown_text, encoding="utf-8")
    print(
        f"Subsystem controls: {report['summary']['records']} records, "
        f"{report['summary']['domains']['rust']} Rust crates"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
