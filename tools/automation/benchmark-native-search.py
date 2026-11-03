#!/usr/bin/env python3
"""Bounded deterministic archive/proposal benchmarks; no physical solver calls."""
import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import platform
import resource
import statistics
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from engineering.design_search import native_search, quality_diversity
from engineering.station_rail.common import digest, encoded, identity


def synthetic(count, dimensions, kind):
    state = 0x123456789ABCDEF
    rows = []
    for index in range(count):
        values = [float(index), float(count-index)] + [1.0] * (dimensions-2)
        if kind == "random":
            values = []
            for _ in range(dimensions):
                state = (state * 6364136223846793005 + 1442695040888963407) % 2**64
                values.append(float((state >> 32) % 100_003))
        rows.append(dict(candidate_id=f"{index:064x}", descriptor=dict(family="synthetic"),
                         metrics={f"objective_{i}": value for i, value in enumerate(values)}))
    return rows, tuple(f"objective_{i}" for i in range(dimensions)), ("family",)


def timed(function, repetitions):
    values, result = [], None
    for _ in range(repetitions):
        start = time.perf_counter()
        result = function()
        values.append(time.perf_counter()-start)
    return values, result


def parity(reference, native):
    assert reference["retained_candidate_ids"] == native["retained_candidate_ids"]
    assert reference["cross_cell_partial_quantity_pareto_candidate_ids"] == native["global_front"]
    expected = {c["cell_id"]: c["retained_pareto_candidate_ids"] for c in reference["cells"]}
    assert expected == {c["cell_id"]: c["retained_candidate_ids"] for c in native["cells"]}


def portfolio(folder, objectives, descriptors):
    base = ROOT / "docs/design-engine" / folder
    manifest = json.loads((base / "manifest.json").read_bytes())
    assert manifest["manifest_id"] == identity({k: v for k, v in manifest.items() if k != "manifest_id"})
    assert all(digest(base / path) == value for path, value in manifest["files_sha256"].items())
    assert all(digest(ROOT / path) == value for path, value in manifest["source_sha256"].items())
    value = json.loads((base / "result.json").read_bytes())
    return value["evaluations"], objectives, descriptors, {
        str((base / path).relative_to(ROOT)): digest(base / path) for path in ("manifest.json", "result.json")}


def run(engine):
    cases, packet_sources = [], {}
    for count in (100, 300, 600):
        rows, objectives, descriptors = synthetic(count, 2, "nondominated")
        old = lambda: quality_diversity.archive(rows, objectives, descriptors)
        new = lambda: engine.archive(rows, objectives, descriptors)
        parity(old(), new())  # one warmup per implementation
        old_times, reference = timed(old, 3)
        new_times, native = timed(new, 3)
        parity(reference, native)
        cases.append(dict(kind="synthetic-nondominated", count=count, dimensions=2,
            input_sha256=sha256(encoded(rows)).hexdigest(), legacy_wall_s=old_times,
            rust_bridge_wall_s=new_times, legacy_median_s=statistics.median(old_times),
            rust_bridge_median_s=statistics.median(new_times),
            median_speedup=statistics.median(old_times)/statistics.median(new_times),
            front_parity=True, rust_statistics=native["statistics"]))
    actual = (("civil-shape-portfolio", ("nominal_stock_mass_kg", "scoped_installed_base_iqd", "factory_hours_base"), ("family",)),
              ("breadth-first-shape-portfolio", ("known_gross_structure_stock_kg", "factory_gate_body_stock_base_iqd_per_car", "factory_process_hours_base_per_car", "manufacturing_occurrences"), ("frame", "shell", "ribs")))
    for folder, objectives, descriptors in actual:
        rows, objectives, descriptors, sources = portfolio(folder, objectives, descriptors)
        packet_sources.update(sources)
        old = lambda: quality_diversity.archive(rows, objectives, descriptors)
        new = lambda: engine.archive(rows, objectives, descriptors)
        parity(old(), new())
        old_times, reference = timed(old, 3)
        new_times, native = timed(new, 3)
        parity(reference, native)
        cases.append(dict(kind="stored-research-portfolio", folder=folder, count=len(rows),
            dimensions=len(objectives), input_sha256=sha256(encoded(rows)).hexdigest(),
            legacy_wall_s=old_times, rust_bridge_wall_s=new_times,
            legacy_median_s=statistics.median(old_times), rust_bridge_median_s=statistics.median(new_times),
            median_speedup=statistics.median(old_times)/statistics.median(new_times), front_parity=True))
    for dimensions in (3, 4):
        for kind in ("nondominated", "random"):
            rows, objectives, descriptors = synthetic(100_000, dimensions, kind)
            input_hash = sha256(encoded(rows)).hexdigest()
            times, native = timed(lambda: engine.archive(rows, objectives, descriptors), 1)
            points = [dict(candidate_id=r["candidate_id"], cell_id=identity(r["descriptor"]),
                           values=[r["metrics"][key] for key in objectives]) for r in rows]
            raw = encoded(dict(schema=native_search.REQUEST_SCHEMA, operation="pareto", points=points, max_work=100_000_000))
            engine._current()
            cli_times, result_raw = timed(lambda: native_search._run([str(engine.binary)], raw, timeout=60), 1)
            engine._current()
            direct = json.loads(result_raw)
            assert direct["global_front"] == native["global_front"]
            if kind == "nondominated":
                assert len(native["global_front"]) == len(rows)
            cases.append(dict(kind="synthetic-"+kind, count=len(rows), dimensions=dimensions,
                input_sha256=input_hash, kernel_request_sha256=sha256(raw).hexdigest(),
                kernel_request_bytes=len(raw), rust_bridge_wall_s=times, rust_cli_wall_s=cli_times,
                global_front_count=len(native["global_front"]), rust_statistics=direct["statistics"],
                cli_matches_bridge=True, legacy_not_run="100,000-point quadratic reference deliberately excluded"))
            del rows, points, raw, native, direct, result_raw
    parents = [dict(candidate_id=f"{i:064x}", genes=[i % 18] + [0]*7) for i in range(18)]
    request = dict(seed=20261103, generation=1, limit=10_000, max_attempts=100_000,
        axes=[dict(name="family", choices=18)] + [dict(name=f"axis_{i}", choices=11) for i in range(7)],
        family_axis=0, parents=parents, seen=[], weights=[50, 30, 20])
    times, result = timed(lambda: engine.propose(**request), 1)
    assert len(result["proposals"]) == len({tuple(p["genes"]) for p in result["proposals"]}) == 10_000
    proposals = dict(kind="synthetic-gene-programs-not-geometry", input_sha256=sha256(encoded(request)).hexdigest(),
        rust_bridge_wall_s=times, count=len(result["proposals"]), attempted=result["attempted"],
        allocation_counts=result["allocation_counts"], duplicates=result["duplicates"],
        exhausted=result["exhausted"], provenance=result["provenance"])
    return cases, proposals, packet_sources


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    fixed_sources = {"tools/automation/benchmark-native-search.py": digest(__file__),
        native_search.PRODUCER: digest(native_search.__file__),
        "engineering/design_search/quality_diversity.py": digest(quality_diversity.__file__)}
    engine = native_search.NativeSearch(ROOT)
    start = time.perf_counter()
    cases, proposals, packet_sources = run(engine)
    if any(digest(ROOT/name) != value for name, value in fixed_sources.items()):
        raise ValueError("Benchmark or bridge source changed during execution")
    report = dict(schema="osr-native-search-benchmark/1", elapsed_s=time.perf_counter()-start,
        python_version=platform.python_version(), platform=platform.platform(), cpu_count=os.cpu_count(),
        source_sha256={**packet_sources, **fixed_sources},
        kernel_receipt=engine.receipt, cases=cases, proposals=proposals,
        cumulative_self_maxrss_KiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        cumulative_children_maxrss_KiB=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
        address_space_rlimit_bytes=list(resource.getrlimit(resource.RLIMIT_AS)),
        method=dict(clock="time.perf_counter monotonic wall time", small_warmups=1, small_measured_repetitions=3,
            large_measured_repetitions=1, rss="Linux cumulative process/child high-water marks, not per-case peaks",
            bridge="normalization, canonical request/output hashes, receipt/source checks, subprocess pipes and output validation",
            cli="spawn, Rust JSON parse, native algorithm, JSON serialization and pipes; excludes Python normalization/hash/receipt checks",
            operating_system_limit="Set by the invoking shell if desired; script does not enforce an OS sandbox"),
        caveats=["Synthetic search timings are not geometry generation, solver or whole-railway throughput.",
            "No native engineering solver or physical test is dispatched.",
            "Compact Rust witnesses/fronts match reference fronts; the quadratic all-dominator output is intentionally absent.",
            "Actual 18/54 portfolios use stored provisional objectives; parity is not engineering acceptance."],
        physical_accepted=False, engineering_accepted=False, native_engineering_solver_dispatched=False)
    report["benchmark_id"] = identity(report)
    path = args.output / "report.json"
    path.write_bytes(encoded(report))
    print(json.dumps(dict(output=str(path), benchmark_id=report["benchmark_id"], report_sha256=digest(path), elapsed_s=report["elapsed_s"])))


if __name__ == "__main__":
    main()
