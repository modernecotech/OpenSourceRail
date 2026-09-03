#!/usr/bin/env python3
"""Cross-check OSR reference timings against SUMO and gate operational release.

The automatic comparison is deliberately limited to facts both models expose.
Junction occupancy and final operations acceptance remain controlled external
evidence because the generated SUMO screening network does not model shared
junction conflicts independently.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import tomllib
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected a JSON object")
    return value


def display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def city_and_lines(design_path: Path) -> tuple[str, list[str]]:
    with design_path.open("rb") as handle:
        design = tomllib.load(handle)
    city = str(design.get("city", {}).get("slug", design_path.parent.name.lower()))
    return city, [str(line.get("id", line.get("name", ""))) for line in design.get("lines", [])]


def pairs(value: Any) -> dict[str, float]:
    result: dict[str, float] = {}
    if not isinstance(value, list):
        return result
    for row in value:
        if isinstance(row, list) and len(row) == 2:
            result[str(row[0])] = float(row[1])
    return result


def validate_bound_evidence(
    value: dict[str, Any],
    expected_hashes: dict[str, str],
    required_fields: tuple[str, ...],
    label: str,
) -> list[str]:
    findings = [f"{label} missing {field}" for field in required_fields if value.get(field) in (None, "", [], {})]
    if value.get("status") != "passed" and label == "junction evidence":
        findings.append("junction evidence status is not passed")
    for field, digest in expected_hashes.items():
        if value.get(field) != digest:
            findings.append(f"{label} {field} does not match the received input")
    return findings


def build_report(
    design_path: Path,
    sumo_path: Path,
    simulation_path: Path,
    *,
    relative_tolerance: float = 0.15,
    absolute_tolerance_s: float = 120.0,
    junction_evidence_path: Path | None = None,
    acceptance_record_path: Path | None = None,
) -> dict[str, Any]:
    city, design_lines = city_and_lines(design_path)
    sumo = read_json(sumo_path)
    simulation = read_json(simulation_path)
    runs = simulation.get("runs", [])
    full_run = runs[0] if isinstance(runs, list) and runs and isinstance(runs[0], dict) else {}
    osr_times = pairs(full_run.get("per_line_reference_trip_time_s"))
    sumo_times = {
        str(row.get("line")): float(row.get("mean_trip_duration_s", 0.0))
        for row in sumo.get("lines", [])
        if isinstance(row, dict) and row.get("line")
    }

    comparisons: list[dict[str, Any]] = []
    for line_id in design_lines:
        osr_s = osr_times.get(line_id)
        sumo_s = sumo_times.get(line_id)
        tolerance_s = max(absolute_tolerance_s, (osr_s or 0.0) * relative_tolerance)
        delta_s = None if osr_s is None or sumo_s is None else sumo_s - osr_s
        passed = delta_s is not None and abs(delta_s) <= tolerance_s
        comparisons.append(
            {
                "line_id": line_id,
                "osr_reference_trip_time_s": None if osr_s is None else round(osr_s, 3),
                "sumo_mean_trip_time_s": None if sumo_s is None else round(sumo_s, 3),
                "delta_s": None if delta_s is None else round(delta_s, 3),
                "delta_percent_of_osr": None if delta_s is None or not osr_s else round(delta_s / osr_s * 100.0, 3),
                "tolerance_s": round(tolerance_s, 3),
                "passed": passed,
            }
        )

    line_scope_matches = set(design_lines) == set(osr_times) == set(sumo_times)
    automatic_passed = bool(
        design_lines
        and line_scope_matches
        and sumo.get("passed") is True
        and simulation.get("passed") is True
        and all(row["passed"] for row in comparisons)
    )
    hashes = {
        "design_sha256": sha256(design_path),
        "sumo_summary_sha256": sha256(sumo_path),
        "simulation_summary_sha256": sha256(simulation_path),
    }

    junction_findings = ["independently reviewed junction-occupancy evidence not received"]
    junction_evidence_sha256 = None
    if junction_evidence_path is not None and junction_evidence_path.exists():
        junction = read_json(junction_evidence_path)
        junction_findings = validate_bound_evidence(
            junction,
            hashes,
            ("status", "reviewer", "organisation", "reviewed_at", "method", "line_results"),
            "junction evidence",
        )
        covered = {str(row.get("line_id")) for row in junction.get("line_results", []) if isinstance(row, dict)}
        if covered != set(design_lines):
            junction_findings.append("junction evidence does not cover every design line exactly")
        if any(row.get("occupancy_conflicts") != 0 for row in junction.get("line_results", []) if isinstance(row, dict)):
            junction_findings.append("junction evidence contains unresolved occupancy conflicts")
        junction_evidence_sha256 = sha256(junction_evidence_path)
    junction_passed = not junction_findings

    acceptance_expected = {**hashes}
    if junction_evidence_sha256:
        acceptance_expected["junction_evidence_sha256"] = junction_evidence_sha256
    acceptance_findings = ["signed operational acceptance record not received"]
    if acceptance_record_path is not None and acceptance_record_path.exists():
        acceptance = read_json(acceptance_record_path)
        acceptance_findings = validate_bound_evidence(
            acceptance,
            acceptance_expected,
            ("decision", "approver", "organisation", "approved_at"),
            "acceptance record",
        )
        if acceptance.get("decision") != "accepted":
            acceptance_findings.append("operational acceptance decision is not accepted")
    authority_accepted = bool(automatic_passed and junction_passed and not acceptance_findings)
    if not automatic_passed:
        status = "automatic-crosscheck-failed"
    elif not junction_passed:
        status = "running-time-screen-passed-awaiting-junction-evidence"
    elif not authority_accepted:
        status = "technical-screen-passed-awaiting-authority"
    else:
        status = "authority-accepted"

    return {
        "schema_version": "1.0",
        "analysis_id": f"OSR-OPERATIONS-CROSSCHECK:{city}",
        "city": city,
        "passed": automatic_passed,
        "status": status,
        "automatic_crosscheck_passed": automatic_passed,
        "line_scope_matches": line_scope_matches,
        "relative_tolerance": relative_tolerance,
        "absolute_tolerance_s": absolute_tolerance_s,
        "line_comparisons": comparisons,
        "junction_occupancy_passed": junction_passed,
        "junction_findings": junction_findings,
        "authority_accepted": authority_accepted,
        "acceptance_findings": acceptance_findings,
        "evidence_hashes": hashes,
        "junction_evidence_sha256": junction_evidence_sha256,
        "generator": display_path(Path(__file__)),
        "generator_sha256": sha256(Path(__file__)),
        "sources": {
            "design": display_path(design_path),
            "sumo_summary": display_path(sumo_path),
            "simulation_summary": display_path(simulation_path),
        },
        "technical_boundary": "The automatic result is a deterministic planning-model timing comparison, not proof of safe headways, signalling performance or junction capacity.",
        "acceptance_boundary": "Junction occupancy must be checked in an independently reviewed conflict-capable model and the operator or authority must sign the bound evidence before operational release.",
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        f"# {report['city'].title()} operations cross-check",
        "",
        f"- Status: **{report['status']}**",
        f"- Automatic running-time cross-check: **{'passed' if report['automatic_crosscheck_passed'] else 'failed'}**",
        f"- Junction occupancy evidence: **{'passed' if report['junction_occupancy_passed'] else 'pending'}**",
        f"- Authority accepted: **{'yes' if report['authority_accepted'] else 'no'}**",
        "",
        "| Line | OSR reference | SUMO mean | Difference | Tolerance | Result |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for row in report["line_comparisons"]:
        def seconds(value: Any) -> str:
            return "missing" if value is None else f"{float(value):.1f} s"
        lines.append(
            f"| {row['line_id']} | {seconds(row['osr_reference_trip_time_s'])} | {seconds(row['sumo_mean_trip_time_s'])} | {seconds(row['delta_s'])} | {seconds(row['tolerance_s'])} | {'pass' if row['passed'] else 'fail'} |"
        )
    lines.extend(["", "> " + report["technical_boundary"], "", "> " + report["acceptance_boundary"], ""])
    if report["junction_findings"]:
        lines.extend(["## Remaining junction gate", "", *[f"- {item}" for item in report["junction_findings"]], ""])
    if report["acceptance_findings"]:
        lines.extend(["## Remaining acceptance gate", "", *[f"- {item}" for item in report["acceptance_findings"]], ""])
    return "\n".join(lines)


def generate(**kwargs: Any) -> dict[str, Any]:
    output_dir = Path(kwargs.pop("output_dir"))
    output_dir.mkdir(parents=True, exist_ok=True)
    report = build_report(**kwargs)
    (output_dir / "operations-crosscheck.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    (output_dir / "operations-crosscheck.md").write_text(render_markdown(report), encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--design", type=Path, required=True)
    parser.add_argument("--sumo-summary", type=Path, required=True)
    parser.add_argument("--simulation-summary", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--junction-evidence", type=Path)
    parser.add_argument("--acceptance-record", type=Path)
    parser.add_argument("--relative-tolerance", type=float, default=0.15)
    parser.add_argument("--absolute-tolerance-s", type=float, default=120.0)
    args = parser.parse_args()
    report = generate(
        design_path=args.design.resolve(),
        sumo_path=args.sumo_summary.resolve(),
        simulation_path=args.simulation_summary.resolve(),
        output_dir=args.output_dir.resolve(),
        junction_evidence_path=args.junction_evidence.resolve() if args.junction_evidence else None,
        acceptance_record_path=args.acceptance_record.resolve() if args.acceptance_record else None,
        relative_tolerance=args.relative_tolerance,
        absolute_tolerance_s=args.absolute_tolerance_s,
    )
    print(json.dumps(report, indent=2))
    return 0 if report["automatic_crosscheck_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
