#!/usr/bin/env python3
"""Deterministic analytical and interchange assurance for engineering tools.

This fast gate complements live solver benchmarks.  Each analytical case uses
two independently expressed calculations and each interchange check verifies
identity, units, coordinate reference, or semantic conservation.  It is a
software/toolchain regression gate, not design approval.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
import tempfile
import tomllib
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
REPORT_JSON = ROOT / "engineering/toolchain/baseline-assurance.json"
REPORT_MD = ROOT / "engineering/toolchain/baseline-assurance.md"
ALIGNMENT_XML = ROOT / "tools/osr-aln-convert/samples/samawah-line1.xml"
ALIGNMENT_GOLDEN = ROOT / "tools/osr-aln-convert/samples/samawah-line1.aln.toml"
DUTY_FIXTURE = ROOT / "engineering/toolchain/fixtures/planning-duty-cycle.json"
CIVIL_INDEX = ROOT / "engineering/models/bim/reference/civil-coordination.index.json"
CIVIL_IFC = ROOT / "engineering/models/bim/reference/civil-coordination.ifc"

sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools/osr-aln-convert/src"))

from engineering.analysis.duty_cycle import load as load_duty  # noqa: E402
from engineering.analysis.duty_cycle import project, verify_projection  # noqa: E402
from osr_aln.landxml_to_osr_aln import Meta, convert  # noqa: E402


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_write(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as handle:
        handle.write(content)
        handle.flush()
        os.fsync(handle.fileno())
        temporary = Path(handle.name)
    os.replace(temporary, path)


def _solve(matrix: list[list[float]], vector: list[float]) -> list[float]:
    """Small deterministic Gaussian elimination with partial pivoting."""

    augmented = [row[:] + [rhs] for row, rhs in zip(matrix, vector)]
    size = len(augmented)
    for column in range(size):
        pivot = max(range(column, size), key=lambda row: abs(augmented[row][column]))
        if abs(augmented[pivot][column]) < 1.0e-15:
            raise ValueError("singular benchmark matrix")
        augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
        scale = augmented[column][column]
        augmented[column] = [value / scale for value in augmented[column]]
        for row in range(size):
            if row == column:
                continue
            factor = augmented[row][column]
            augmented[row] = [
                value - factor * reference
                for value, reference in zip(augmented[row], augmented[column])
            ]
    return [row[-1] for row in augmented]


def _case(identifier: str, title: str, expected: float, actual: float, tolerance: float, unit: str) -> dict[str, Any]:
    error = abs(actual - expected)
    return {
        "id": identifier,
        "title": title,
        "expected": expected,
        "actual": actual,
        "absolute_error": error,
        "tolerance": tolerance,
        "unit": unit,
        "passed": error <= tolerance,
    }


def analytical_cases() -> list[dict[str, Any]]:
    # Cantilever: Euler-Bernoulli closed form versus a one-element stiffness solve.
    force_n, length_m, modulus_pa, inertia_m4 = 12_000.0, 3.0, 210.0e9, 8.0e-6
    cantilever_expected = force_n * length_m**3 / (3.0 * modulus_pa * inertia_m4)
    beam_k = modulus_pa * inertia_m4 / length_m**3
    cantilever_actual = _solve(
        [[12 * beam_k, -6 * length_m * beam_k], [-6 * length_m * beam_k, 4 * length_m**2 * beam_k]],
        [force_n, 0.0],
    )[0]

    # Thermal block: resistance/flux form versus midpoint energy balance.
    left_c, right_c, conductivity, block_length = 20.0, 60.0, 2.0, 1.0
    thermal_expected = (left_c + right_c) / 2.0
    thermal_actual = _solve(
        [[2.0 * conductivity / (block_length / 2.0)]],
        [conductivity * left_c / (block_length / 2.0) + conductivity * right_c / (block_length / 2.0)],
    )[0]

    # Drainage: rainfall volume versus independently accumulated outlet volume.
    area_m2, intensity_m_s, duration_s, runoff_coefficient = 10_000.0, 25.0 / 1000.0 / 3600.0, 1_200.0, 0.4
    drainage_expected = area_m2 * intensity_m_s * duration_s * runoff_coefficient
    # ``sum`` changed its floating-point accumulation algorithm in Python 3.12.
    # Use fsum so tracked evidence is byte-identical on supported runtimes.
    drainage_actual = math.fsum(area_m2 * intensity_m_s * 60.0 * runoff_coefficient for _ in range(20))

    # One-zone steady state: heat balance versus converged implicit Euler RC steps.
    outdoor_c, internal_w, ua_w_k = 40.0, 10_000.0, 2_000.0
    zone_expected = outdoor_c + internal_w / ua_w_k
    capacitance_j_k, step_s = 4.0e6, 300.0
    zone_actual = outdoor_c
    for _ in range(2_000):
        zone_actual = (capacitance_j_k / step_s * zone_actual + ua_w_k * outdoor_c + internal_w) / (
            capacitance_j_k / step_s + ua_w_k
        )

    # Four-bus radial DC screen: downstream-flow voltage drops versus nodal solve.
    resistances = [0.02, 0.03, 0.025]
    loads_a = [50.0, 40.0, 30.0]
    source_v = 700.0
    downstream = [sum(loads_a[index:]) for index in range(3)]
    four_bus_expected = source_v - sum(r * current for r, current in zip(resistances, downstream))
    conductances = [1.0 / value for value in resistances]
    voltages = _solve(
        [
            [conductances[0] + conductances[1], -conductances[1], 0.0],
            [-conductances[1], conductances[1] + conductances[2], -conductances[2]],
            [0.0, -conductances[2], conductances[2]],
        ],
        [conductances[0] * source_v - loads_a[0], -loads_a[1], -loads_a[2]],
    )
    four_bus_actual = voltages[-1]

    # Corridor evacuation: exact batching versus capacity-duration expression.
    people, width_m, flow_people_m_s, walk_s = 120, 1.5, 1.3, 24.0
    evacuation_expected = walk_s + people / (width_m * flow_people_m_s)
    batches = 1_200
    evacuation_actual = walk_s + math.fsum(
        (people / batches) / (width_m * flow_people_m_s) for _ in range(batches)
    )

    # One-line timetable: recurrence versus closed-form run+dwell total.
    section_run_s = [180.0, 240.0, 210.0, 270.0]
    dwell_s = [45.0, 60.0, 45.0]
    timetable_expected = sum(section_run_s) + sum(dwell_s)
    clock = 0.0
    for index, run_s in enumerate(section_run_s):
        clock += run_s
        if index < len(dwell_s):
            clock += dwell_s[index]

    return [
        _case("BENCH-STRUCT-001", "cantilever tip displacement", cantilever_expected, cantilever_actual, 1.0e-12, "m"),
        _case("BENCH-THERM-001", "thermal block midpoint", thermal_expected, thermal_actual, 1.0e-12, "degC"),
        _case("BENCH-DRAIN-001", "simple drainage mass balance", drainage_expected, drainage_actual, 1.0e-12, "m3"),
        _case("BENCH-ENERGY-001", "one-zone steady-state temperature", zone_expected, zone_actual, 1.0e-9, "degC"),
        _case("BENCH-ELEC-001", "four-bus terminal voltage", four_bus_expected, four_bus_actual, 1.0e-9, "V"),
        _case("BENCH-EGRESS-001", "corridor evacuation clearance", evacuation_expected, evacuation_actual, 1.0e-9, "s"),
        _case("BENCH-TIME-001", "one-line timetable traversal", timetable_expected, clock, 1.0e-12, "s"),
    ]


def interchange_checks() -> list[dict[str, Any]]:
    produced = convert(
        ALIGNMENT_XML,
        Meta(
            line_id="samawah-line1",
            preset="standard-urban",
            consist="light-metro-3car",
            crs="EPSG:32638",
            surveyor="Samawah Civil Associates",
            design_date="2026-04-23",
        ),
    )
    golden = ALIGNMENT_GOLDEN.read_text(encoding="utf-8")
    alignment = tomllib.loads(produced)
    alignment_passed = produced == golden and alignment["meta"]["units"] == "metric" and alignment["meta"]["crs"] == "EPSG:32638"

    index = json.loads(CIVIL_INDEX.read_text(encoding="utf-8"))
    objects = index["objects"]
    ids = [row["asset_id"] for row in objects]
    guids = [row["ifc_guid"] for row in objects]
    boxes_valid = all(
        len(row.get("bbox_m", [])) == 6
        and all(isinstance(value, (int, float)) and math.isfinite(value) for value in row["bbox_m"])
        and all(row["bbox_m"][axis + 3] >= row["bbox_m"][axis] for axis in range(3))
        for row in objects
    )
    ifc_hash_matches = index.get("ifc_sha256") == sha256(CIVIL_IFC)
    ifc_passed = len(ids) == len(set(ids)) == len(set(guids)) and boxes_valid and ifc_hash_matches

    duty = load_duty(DUTY_FIXTURE)
    projections = project(duty)
    verify_projection(duty, projections)
    times = [[row["time_s"] for row in projections[name]] for name in ("pybamm", "pandapower", "sumo")]
    duty_passed = times[0] == times[1] == times[2] and not projections["acceptance_eligible"]

    return [
        {
            "id": "XCHG-ALN-001",
            "title": "LandXML to OSR-ALN units/CRS/golden round trip",
            "passed": alignment_passed,
            "source_sha256": sha256(ALIGNMENT_XML),
            "result_sha256": hashlib.sha256(produced.encode()).hexdigest(),
        },
        {
            "id": "XCHG-IFC-001",
            "title": "IFC asset identity and finite analysis envelope",
            "passed": ifc_passed,
            "object_count": len(objects),
            "source_sha256": sha256(CIVIL_IFC),
            "index_sha256": sha256(CIVIL_INDEX),
        },
        {
            "id": "XCHG-DUTY-001",
            "title": "Duty-cycle battery/grid/traffic semantic projection",
            "passed": duty_passed,
            "sample_count": len(duty["samples"]),
            "source_kind": duty["source_kind"],
            "acceptance_eligible": projections["acceptance_eligible"],
            "source_semantic_sha256": projections["source_semantic_sha256"],
        },
    ]


def build_report() -> dict[str, Any]:
    benchmarks = analytical_cases()
    interchange = interchange_checks()
    sources = [Path(__file__), ALIGNMENT_XML, ALIGNMENT_GOLDEN, DUTY_FIXTURE, CIVIL_INDEX, CIVIL_IFC]
    return {
        "schema": "org.opensourcerail.engineering-baseline-assurance.v1",
        "authority_boundary": "Deterministic software/toolchain regression evidence only; not physical validation, design approval, or authority acceptance.",
        "passed": all(row["passed"] for row in benchmarks + interchange),
        "benchmark_count": len(benchmarks),
        "interchange_check_count": len(interchange),
        "benchmarks": benchmarks,
        "interchange": interchange,
        "source_hashes": {str(path.relative_to(ROOT)): sha256(path) for path in sources},
    }


def markdown(report: dict[str, Any]) -> str:
    rows = [
        "# Engineering Baseline Assurance",
        "",
        "> Deterministic software/toolchain regression evidence only. This is not physical validation, design approval, certification, or authority acceptance.",
        "",
        f"- Overall result: **{'PASS' if report['passed'] else 'FAIL'}**",
        f"- Analytical benchmarks: **{report['benchmark_count']}**",
        f"- Interchange checks: **{report['interchange_check_count']}**",
        "",
        "## Analytical Benchmarks",
        "",
        "| ID | Case | Expected | Actual | Tolerance | Result |",
        "|---|---|---:|---:|---:|---|",
    ]
    for case in report["benchmarks"]:
        rows.append(
            f"| `{case['id']}` | {case['title']} | {case['expected']:.9g} {case['unit']} | "
            f"{case['actual']:.9g} {case['unit']} | {case['tolerance']:.3g} | "
            f"**{'PASS' if case['passed'] else 'FAIL'}** |"
        )
    rows.extend(
        [
            "",
            "## Interchange Drift",
            "",
            "| ID | Contract | Result |",
            "|---|---|---|",
        ]
    )
    for check in report["interchange"]:
        rows.append(f"| `{check['id']}` | {check['title']} | **{'PASS' if check['passed'] else 'FAIL'}** |")
    rows.extend(
        [
            "",
            "The duty fixture is deliberately marked planning-only. Conversion cannot make it acceptance-eligible; measured data still requires controlled instrumentation and source evidence.",
            "",
        ]
    )
    return "\n".join(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail if tracked reports differ")
    args = parser.parse_args()
    report = build_report()
    encoded = json.dumps(report, indent=2, sort_keys=True, allow_nan=False).encode() + b"\n"
    rendered = markdown(report).encode()
    if args.check:
        if not REPORT_JSON.is_file() or REPORT_JSON.read_bytes() != encoded:
            raise SystemExit(f"stale engineering assurance report: {REPORT_JSON}")
        if not REPORT_MD.is_file() or REPORT_MD.read_bytes() != rendered:
            raise SystemExit(f"stale engineering assurance report: {REPORT_MD}")
    else:
        atomic_write(REPORT_JSON, encoded)
        atomic_write(REPORT_MD, rendered)
    print(f"engineering baseline assurance: {'PASS' if report['passed'] else 'FAIL'} ({len(report['benchmarks'])} benchmarks, {len(report['interchange'])} interchange checks)")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
