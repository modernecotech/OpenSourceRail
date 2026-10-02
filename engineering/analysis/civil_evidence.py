"""Controlled civil layouts and numerical result exchanges shared by both gates.

The register is reviewed separately from the submitted schedule. Acceptance of
these exchanges establishes consistency with reviewed limits, not design safety.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path


def finite(value, *, minimum=None) -> float:
    if isinstance(value, bool):
        raise ValueError("boolean is not a measurement")
    number = float(value)
    if not math.isfinite(number) or (minimum is not None and number < minimum):
        raise ValueError("measurement must be finite and within range")
    return number


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def add_pending_roles(path: Path, requirements: dict) -> None:
    """Migrate receipt templates without replacing any received evidence rows."""
    with path.open(newline="") as stream:
        reader = csv.DictReader(stream)
        fields = reader.fieldnames or []
        roles = {r.get("file_role") for r in reader}
    if "file_role" not in fields or "acceptance_status" not in fields: return
    missing = [r["file_role"] for r in requirements["input"] if r["file_role"] not in roles]
    if not missing: return
    with path.open("a", newline="") as stream:
        if path.stat().st_size and not path.read_bytes().endswith(b"\n"): stream.write("\n")
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writerows({"file_role":r,"acceptance_status":"not-received"} for r in missing)


def controlled_path(root: Path, relative: str) -> Path:
    path = Path(relative)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError("output path must be relative to controlled evidence")
    resolved = (root / path).resolve()
    if not resolved.is_relative_to(root.resolve()) or not resolved.is_file():
        raise ValueError("output file missing or outside controlled evidence")
    return resolved


def inspect_register(value: dict, design_hash: str, line_ids: set[str], station_ids: set[str]) -> list[str]:
    findings = []
    if value.get("schema") != "osr-civil-assets/1" or value.get("design_sha256") != design_hash:
        findings.append("civil asset register schema/design hash does not match")
    review = value.get("review", {})
    if (review.get("decision") != "accepted" or not all(review.get(k) for k in
        ("producer", "checker", "signed_at", "controlled_reference")) or review.get("producer") == review.get("checker")):
        findings.append("civil asset register needs independent accepted layout review")
    assets, supports = value.get("assets", []), value.get("supports", [])
    for label, rows, key in (("asset", assets, "asset_id"), ("support", supports, "support_id")):
        ids = [row.get(key) for row in rows]
        if not ids or any(not i for i in ids) or len(set(ids)) != len(ids):
            findings.append(f"register {label} IDs empty or duplicated")
    support_ids = {row.get("support_id") for row in supports}
    support_map = {row.get("support_id"): row for row in supports}
    for asset in assets:
        try:
            start, end = finite(asset["from_station_m"], minimum=0), finite(asset["to_station_m"], minimum=0)
            if end < start or (asset["asset_type"] not in {"pier", "abutment", "foundation"} and end == start):
                raise ValueError("invalid range")
            if asset["line_id"] not in line_ids or not asset.get("support_ids") or not set(asset["support_ids"]) <= support_ids:
                raise ValueError("unknown line/support")
            if asset["asset_type"] in {"span", "at-grade-structure"}:
                locations = {finite(support_map[i]["chainage_m"]) for i in asset["support_ids"]}
                if not {start,end} <= locations: raise ValueError("endpoint supports missing")
        except (KeyError, TypeError, ValueError):
            findings.append(f"register asset {asset.get('asset_id')}: invalid chainage or supports")
    for support in supports:
        try:
            finite(support["chainage_m"], minimum=0)
            known = line_ids if support["scope_type"] == "line" else station_ids if support["scope_type"] == "station" else set()
            if support["scope_id"] not in known or not support.get("zone_id"):
                raise ValueError("scope/zone")
        except (KeyError, TypeError, ValueError):
            findings.append(f"register support {support.get('support_id')}: invalid location")
    intervals = value.get("coverage_intervals", [])
    if {row.get("line_id") for row in intervals} != line_ids:
        findings.append("register coverage intervals do not cover every line")
    groups = set()
    for interval in intervals:
        try:
            group = (interval["line_id"], interval["coverage_group"])
            if group in groups:
                raise ValueError("duplicate coverage group")
            groups.add(group)
            cursor = finite(interval["from_station_m"], minimum=0)
            finish = finite(interval["to_station_m"], minimum=0)
            if finish <= cursor: raise ValueError("invalid extent")
            ranges = sorted((finite(a["from_station_m"]), finite(a["to_station_m"])) for a in assets
                            if (a.get("line_id"), a.get("coverage_group")) == group)
            for start, end in ranges:
                if abs(start - cursor) > 1e-6 or end <= start: raise ValueError("gap/overlap")
                cursor = end
            if abs(cursor - finish) > 1e-6: raise ValueError("incomplete extent")
        except (KeyError, TypeError, ValueError):
            findings.append("register chainage coverage has gaps, overlaps or invalid ranges")
    for asset in assets:
        if asset.get("coverage_group") and (asset.get("line_id"), asset["coverage_group"]) not in groups:
            findings.append("register asset uses undefined coverage group")
    return findings


def reconcile(rows: list[dict], expected: list[dict], key: str, fields: tuple[str, ...]) -> list[str]:
    actual_ids = [r.get(key) for r in rows]
    expected_ids = [r.get(key) for r in expected]
    if set(actual_ids) != set(expected_ids) or len(actual_ids) != len(expected_ids):
        return [f"schedule does not contain exactly the expected {key} IDs"]
    indexed = {r[key]: r for r in expected}
    findings = []
    for row in rows:
        for field in fields:
            a, b = row.get(field), indexed[row[key]].get(field)
            try:
                same = abs(finite(a) - finite(b)) <= 1e-6 if field.endswith("_m") else a == b
            except (TypeError, ValueError):
                same = False
            if not same: findings.append(f"{row[key]}: {field} differs from reviewed register")
    return findings


def inspect_results(report: dict, root: Path, register: dict | None, solver: str | None, asset_ids: set[str] | None) -> list[str]:
    findings = []
    hashes = report.get("output_hashes", {})
    if not isinstance(hashes, dict) or not hashes:
        return ["solver needs actual output files and hashes"]
    for relative, digest in hashes.items():
        try:
            path = controlled_path(root, relative)
            if not path.stat().st_size or sha(path) != digest: raise ValueError("hash mismatch")
        except (ValueError, OSError, TypeError):
            findings.append(f"solver output {relative} missing or hash mismatch")
    results_path = report.get("numerical_results_path")
    if results_path not in hashes:
        findings.append("solver numerical results must be a hashed output file")
    native = report.get("native_output_paths", [])
    if not native or any(p not in hashes or p == results_path for p in native):
        findings.append("solver needs hashed native outputs alongside numerical exchange")
    if not register or not solver:
        return findings + ["solver needs reviewed load-case register and numerical acceptance criteria"]
    review = register.get("review", {})
    if (review.get("decision") != "accepted" or not review.get("controlled_reference") or not review.get("checker")
        or not review.get("producer") or review.get("checker") == review.get("producer") or not review.get("signed_at")):
        findings.append("load-case register requires independent accepted review")
    cases = register.get("required_load_cases", {}).get(solver, [])
    criteria = register.get("criteria", {}).get(solver, [])
    actual_cases = report.get("load_case_ids", [])
    if not cases or len(set(cases)) != len(cases) or len(actual_cases) != len(cases) or set(actual_cases) != set(cases):
        findings.append("solver required load-case coverage mismatch")
    expected = {(r.get("asset_id"), r.get("load_case_id"), r.get("metric")): r for r in criteria}
    if (not criteria or len(expected) != len(criteria) or {r.get("load_case_id") for r in criteria} != set(cases)
        or (asset_ids is not None and {r.get("asset_id") for r in criteria} != asset_ids)):
        findings.append("numerical criteria must cover every scheduled asset and required load case")
    if asset_ids is not None and {(r.get("asset_id"), r.get("load_case_id")) for r in criteria} != {(a,c) for a in asset_ids for c in cases}:
        findings.append("numerical criteria missing asset/load-case combinations")
    if not {"service", "construction"} <= {r.get("stage") for r in criteria}:
        findings.append("numerical criteria need service and construction stages")
    try:
        with controlled_path(root, results_path).open(newline="") as handle:
            rows = list(csv.DictReader(handle))
        keys = [(r["asset_id"], r["load_case_id"], r["metric"]) for r in rows]
        if set(keys) != set(expected) or len(keys) != len(expected):
            findings.append("numerical output coverage differs from required criteria")
        for row, key in zip(rows, keys):
            criterion = expected.get(key)
            if criterion is None: continue
            actual = finite(row["value"])
            limit = finite(criterion["limit"])
            op = criterion["operator"]
            passed = actual <= limit if op == "max" else actual >= limit if op == "min" else abs(actual) <= limit if op == "abs-max" else False
            if row["unit"] != criterion["unit"] or not passed:
                findings.append(f"numerical acceptance failed: {key}")
    except (KeyError, TypeError, ValueError, OSError):
        findings.append("numerical output or criteria missing, invalid or non-finite")
    return findings
