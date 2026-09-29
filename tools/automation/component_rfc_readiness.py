#!/usr/bin/env python3
"""Validate and render promoted component RFC implementation readiness."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tempfile
import tomllib
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "lib/templates/component-rfc-packages.toml"
REPORT_JSON = ROOT / "docs/component-rfc-readiness.json"
REPORT_MD = ROOT / "docs/component-rfc-readiness.md"
HAZARDS = ROOT / "docs/certification/hazard-log.md"
INVENTORIES = (
    ROOT / "design/component-catalogue/catalog/buildable-trainset/buildable-trainset-manifest.json",
    ROOT / "design/component-catalogue/catalog/buildable-stations/station-kit-manifest.json",
    ROOT / "design/component-catalogue/catalog/buildable-civil/reusable-type-release-register.json",
)
LIST_FIELDS = (
    "requirement_ids",
    "interface_ids",
    "hazard_ids",
    "part_ids",
    "drawing_ids",
    "assembly_steps",
    "analysis_evidence",
    "test_evidence_required",
    "unresolved_assumptions",
    "release_blockers",
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _atomic(path: Path, value: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as handle:
        handle.write(value)
        handle.flush()
        os.fsync(handle.fileno())
        temporary = Path(handle.name)
    os.replace(temporary, path)


def _collect_ids(value: Any, output: set[str]) -> None:
    if isinstance(value, dict):
        for field in ("id", "engineering_id", "type_id"):
            if isinstance(value.get(field), str):
                output.add(value[field])
        for child in value.values():
            _collect_ids(child, output)
    elif isinstance(value, list):
        for child in value:
            _collect_ids(child, output)


def compile_readiness(source: dict[str, Any] | None = None) -> dict[str, Any]:
    source = source or tomllib.loads(SOURCE.read_text(encoding="utf-8"))
    meta = source.get("meta", {})
    packages = source.get("packages", [])
    required = set(meta.get("required_rfc_ids", []))
    ids = [row.get("id") for row in packages]
    rfc_ids = [row.get("rfc_id") for row in packages]
    if len(ids) != len(set(ids)) or len(rfc_ids) != len(set(rfc_ids)):
        raise ValueError("component RFC package and RFC IDs must be unique")
    if set(rfc_ids) != required:
        raise ValueError(f"component RFC coverage mismatch: expected {sorted(required)}, got {sorted(rfc_ids)}")

    controlled_ids: set[str] = set()
    for path in INVENTORIES:
        _collect_ids(json.loads(path.read_text(encoding="utf-8")), controlled_ids)
    hazard_text = HAZARDS.read_text(encoding="utf-8")
    evidence_hashes: dict[str, str] = {}
    compiled = []
    for row in packages:
        for field in ("id", "rfc_id", "title", "rfc_path", "owner_role", "status", "acceptance_status"):
            if not isinstance(row.get(field), str) or not row[field].strip():
                raise ValueError(f"{row.get('id', '<unknown>')} requires {field}")
        if row["status"] != "implementation-package":
            raise ValueError(f"{row['id']} must be an implementation-package")
        if "open" not in row["acceptance_status"]:
            raise ValueError(f"{row['id']} may not imply physical acceptance")
        for field in LIST_FIELDS:
            values = row.get(field)
            if not isinstance(values, list) or not values or any(not isinstance(value, str) or not value.strip() for value in values):
                raise ValueError(f"{row['id']} requires non-empty {field}")
            if len(values) != len(set(values)):
                raise ValueError(f"{row['id']} has duplicate {field}")
        if any(part_id not in controlled_ids for part_id in row["part_ids"]):
            missing = sorted(set(row["part_ids"]) - controlled_ids)
            raise ValueError(f"{row['id']} references uncontrolled parts: {missing}")
        for hazard in row["hazard_ids"]:
            if not re.search(rf"^### {re.escape(hazard)}\b", hazard_text, flags=re.MULTILINE):
                raise ValueError(f"{row['id']} references unknown hazard {hazard}")
        paths = [row["rfc_path"], *row["analysis_evidence"]]
        for relative in paths:
            path = (ROOT / relative).resolve()
            try:
                path.relative_to(ROOT)
            except ValueError as error:
                raise ValueError(f"repository-relative evidence required: {relative}") from error
            if not path.is_file():
                raise ValueError(f"{row['id']} missing evidence {relative}")
            evidence_hashes[relative] = _sha(path)
        compiled.append({**row, "digital_completeness": "pass", "release_ready": False})
    return {
        "schema": meta["schema"],
        "authority_boundary": meta["authority_boundary"],
        "passed": True,
        "package_count": len(compiled),
        "release_ready_count": 0,
        "packages": compiled,
        "source_sha256": _sha(SOURCE),
        "inventory_hashes": {str(path.relative_to(ROOT)): _sha(path) for path in INVENTORIES},
        "evidence_hashes": dict(sorted(evidence_hashes.items())),
    }


def markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Component RFC Implementation Readiness",
        "",
        "> Machine-checked implementation/procurement completeness only. It is not supplier freeze, manufacturing release, certification, or permission to operate.",
        "",
        f"- Digital completeness: **{'PASS' if report['passed'] else 'FAIL'}**",
        f"- RFC packages checked: **{report['package_count']}**",
        f"- Physically release-ready: **{report['release_ready_count']}**",
        "",
        "| Package | Scope | Owner | Digital package | Physical release | Open blockers |",
        "|---|---|---|---|---|---:|",
    ]
    for row in report["packages"]:
        lines.append(
            f"| `{row['id']}` | [{row['title']}]({row['rfc_path'].removeprefix('docs/')}) | "
            f"{row['owner_role']} | **PASS** | **BLOCKED** | {len(row['release_blockers'])} |"
        )
    lines.extend(
        [
            "",
            "Every package names requirements, ICDs, hazards, controlled product/BOM IDs, drawings, assembly steps, analysis inputs, required tests, assumptions, accountable role and explicit blockers. Evidence hashes are retained in the JSON report.",
            "",
            report["authority_boundary"],
            "",
        ]
    )
    return "\n".join(lines)


def outputs() -> tuple[bytes, bytes]:
    report = compile_readiness()
    return (
        (json.dumps(report, indent=2, sort_keys=True) + "\n").encode(),
        markdown(report).encode(),
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    json_value, markdown_value = outputs()
    if args.check:
        for path, expected in ((REPORT_JSON, json_value), (REPORT_MD, markdown_value)):
            if not path.is_file() or path.read_bytes() != expected:
                raise SystemExit(f"stale component RFC readiness report: {path.relative_to(ROOT)}")
    else:
        _atomic(REPORT_JSON, json_value)
        _atomic(REPORT_MD, markdown_value)
    report = json.loads(json_value)
    print(f"component RFC readiness: PASS ({report['package_count']} packages; physical release BLOCKED)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
