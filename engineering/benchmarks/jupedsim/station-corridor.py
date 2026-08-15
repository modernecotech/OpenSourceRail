#!/usr/bin/env python3
"""Run deterministic normal and constrained station-corridor flow cases."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from importlib.metadata import version
from pathlib import Path

import jupedsim as jps


REPO_ROOT = Path(__file__).resolve().parents[3]
MANIFEST = REPO_ROOT / "mechanical-py/catalog/buildable-stations/station-kit-manifest.json"


def run_case(length_m: float, width_m: float, rows: int, columns: int) -> dict[str, float | int | bool]:
    simulation = jps.Simulation(
        model=jps.CollisionFreeSpeedModel(),
        geometry=[(0.0, 0.0), (length_m, 0.0), (length_m, width_m), (0.0, width_m)],
        dt=0.05,
    )
    exit_id = simulation.add_exit_stage(
        [(length_m - 1.0, 0.1), (length_m - 0.1, 0.1), (length_m - 0.1, width_m - 0.1), (length_m - 1.0, width_m - 0.1)]
    )
    journey_id = simulation.add_journey(jps.JourneyDescription([exit_id]))

    for row in range(rows):
        y = 0.45 + row * (width_m - 0.9) / (rows - 1)
        for column in range(columns):
            simulation.add_agent(
                jps.CollisionFreeSpeedModelAgentParameters(
                    position=(1.0 + column * 0.55, y),
                    journey_id=journey_id,
                    stage_id=exit_id,
                    desired_speed=1.2,
                    radius=0.2,
                )
            )

    initial_agents = simulation.agent_count()
    while simulation.agent_count() and simulation.elapsed_time() < 150.0:
        simulation.iterate()

    return {
        "clear": simulation.agent_count() == 0,
        "clearance_time_s": simulation.elapsed_time(),
        "initial_agents": initial_agents,
        "iterations": simulation.iteration_count(),
        "length_m": length_m,
        "remaining_agents": simulation.agent_count(),
        "width_m": width_m,
    }


def atomic_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", dir=path.parent, delete=False, encoding="utf-8") as handle:
        json.dump(value, handle, indent=2, sort_keys=True)
        handle.write("\n")
        temporary = Path(handle.name)
    os.replace(temporary, path)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("build/engineering/benchmarks/jupedsim/station-corridor.json"),
    )
    args = parser.parse_args()

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    standard = next(variant for variant in manifest["variants"] if variant["archetype"] == "standard")
    platform_length_m = float(standard["parameters"]["platform_length_m"])
    normal = run_case(platform_length_m, 6.0, 8, 10)
    constrained = run_case(platform_length_m, 2.4, 4, 20)
    passed = bool(
        normal["clear"]
        and constrained["clear"]
        and normal["clearance_time_s"] <= 90.0
        and constrained["clearance_time_s"] <= 120.0
        and constrained["clearance_time_s"] >= normal["clearance_time_s"]
    )
    report = {
        "analysis_id": "OSR-AN-STN-PED-001",
        "acceptance": {
            "constrained_clearance_time_max_s": 120.0,
            "normal_clearance_time_max_s": 90.0,
            "ordering": "constrained clearance must not be faster than normal",
        },
        "canonical_input": str(MANIFEST.relative_to(REPO_ROOT)),
        "input_sha256": hashlib.sha256(Path(__file__).read_bytes() + MANIFEST.read_bytes()).hexdigest(),
        "manifest_sha256": hashlib.sha256(MANIFEST.read_bytes()).hexdigest(),
        "model_scope": "standard station platform circulation corridor; screening geometry only",
        "passed": passed,
        "source_assembly_ids": ["STN-PAX-SA500", "STN-ACC-SA600"],
        "scenarios": {"constrained": constrained, "normal": normal},
        "tool": {"name": "jupedsim", "version": version("jupedsim")},
    }
    atomic_json(args.output, report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
