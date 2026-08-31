#!/usr/bin/env python3
"""Run and evaluate the deterministic CalculiX thermal-block benchmark."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[4]
INPUT_DECK = Path(__file__).with_name("thermal-block.inp")
DEFAULT_OUTPUT_DIR = REPO_ROOT / "build/engineering/analysis/benchmarks/calculix/thermal-block"
JOB_NAME = "thermal-block"
EXPECTED_MIDDLE_TEMPERATURE_C = 40.0
EXPECTED_LONGITUDINAL_FLUX_W_M2 = -80.0
TEMPERATURE_TOLERANCE_C = 1.0e-6
FLUX_TOLERANCE_W_M2 = 1.0e-5
TRANSVERSE_FLUX_TOLERANCE_W_M2 = 1.0e-10


def parse_dat(text: str) -> tuple[dict[int, float], list[tuple[int, int, float, float, float]]]:
    """Extract final-step nodal temperatures and integration-point heat fluxes."""

    temperatures: dict[int, float] = {}
    fluxes: list[tuple[int, int, float, float, float]] = []
    section: str | None = None
    temperature_pattern = re.compile(r"^\s*(\d+)\s+([-+0-9.Ee]+)\s*$")
    flux_pattern = re.compile(
        r"^\s*(\d+)\s+(\d+)\s+([-+0-9.Ee]+)\s+([-+0-9.Ee]+)\s+([-+0-9.Ee]+)\s*$"
    )

    for line in text.splitlines():
        lowered = line.lower()
        if "temperatures for set nall" in lowered:
            section = "temperature"
            temperatures = {}
            continue
        if "heat flux (elem, integ.pnt.,qx,qy,qz) for set eall" in lowered:
            section = "flux"
            fluxes = []
            continue
        if not line.strip():
            continue
        if section == "temperature" and (match := temperature_pattern.match(line)):
            temperatures[int(match.group(1))] = float(match.group(2))
        elif section == "flux" and (match := flux_pattern.match(line)):
            fluxes.append(
                (
                    int(match.group(1)),
                    int(match.group(2)),
                    float(match.group(3)),
                    float(match.group(4)),
                    float(match.group(5)),
                )
            )

    if set(temperatures) != set(range(1, 13)):
        raise ValueError(f"expected temperatures for nodes 1..12, got {sorted(temperatures)}")
    if len(fluxes) != 16:
        raise ValueError(f"expected 16 heat-flux integration points, got {len(fluxes)}")
    return temperatures, fluxes


def solver_command() -> list[str]:
    """Select native CalculiX or the CalculiX bundled with the FreeCAD Flatpak."""

    if executable := shutil.which("ccx"):
        return [executable, JOB_NAME]
    if shutil.which("flatpak"):
        for scope in ("--user", "--system"):
            available = subprocess.run(
                ["flatpak", "info", scope, "org.freecad.FreeCAD"],
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            if available.returncode == 0:
                return [
                    "flatpak",
                    "run",
                    scope,
                    f"--filesystem={REPO_ROOT}",
                    "--command=/app/bin/ccx",
                    "org.freecad.FreeCAD",
                    JOB_NAME,
                ]
    raise RuntimeError("CalculiX not found; run ./install.sh and accept the engineering applications")


def atomic_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", dir=path.parent, delete=False, encoding="utf-8") as handle:
        json.dump(value, handle, indent=2, sort_keys=True)
        handle.write("\n")
        temporary = Path(handle.name)
    os.replace(temporary, path)


def evaluate(dat_text: str, solver_output: str, input_sha256: str) -> dict[str, object]:
    temperatures, fluxes = parse_dat(dat_text)
    middle_temperatures = [temperatures[node] for node in range(5, 9)]
    longitudinal_fluxes = [flux[2] for flux in fluxes]
    transverse_fluxes = [component for flux in fluxes for component in flux[3:]]
    middle_error = max(abs(value - EXPECTED_MIDDLE_TEMPERATURE_C) for value in middle_temperatures)
    longitudinal_error = max(abs(value - EXPECTED_LONGITUDINAL_FLUX_W_M2) for value in longitudinal_fluxes)
    transverse_max = max(abs(value) for value in transverse_fluxes)
    passed = (
        middle_error <= TEMPERATURE_TOLERANCE_C
        and longitudinal_error <= FLUX_TOLERANCE_W_M2
        and transverse_max <= TRANSVERSE_FLUX_TOLERANCE_W_M2
    )
    version_match = re.search(r"CalculiX Version\s+([0-9]+(?:\.[0-9]+)*)", solver_output, flags=re.IGNORECASE)
    return {
        "analysis_id": "OSR-AN-CIV-THERM-001",
        "acceptance": {
            "longitudinal_flux_tolerance_w_m2": FLUX_TOLERANCE_W_M2,
            "middle_temperature_tolerance_c": TEMPERATURE_TOLERANCE_C,
            "transverse_flux_tolerance_w_m2": TRANSVERSE_FLUX_TOLERANCE_W_M2,
        },
        "analytical_solution": {
            "boundary_temperatures_c": [20.0, 60.0],
            "conductivity_w_mk": 2.0,
            "longitudinal_flux_w_m2": EXPECTED_LONGITUDINAL_FLUX_W_M2,
            "middle_temperature_c": EXPECTED_MIDDLE_TEMPERATURE_C,
        },
        "input_sha256": input_sha256,
        "mesh": {"elements": 2, "integration_points": len(fluxes), "nodes": len(temperatures)},
        "passed": passed,
        "results": {
            "longitudinal_flux_error_max_w_m2": longitudinal_error,
            "longitudinal_flux_range_w_m2": [min(longitudinal_fluxes), max(longitudinal_fluxes)],
            "middle_temperature_error_max_c": middle_error,
            "middle_temperature_range_c": [min(middle_temperatures), max(middle_temperatures)],
            "transverse_flux_abs_max_w_m2": transverse_max,
        },
        "scope": "steady-state conduction solver benchmark; not a civil-assembly thermal model",
        "tool": {"name": "CalculiX", "version": version_match.group(1) if version_match else "unknown"},
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    output_deck = output_dir / INPUT_DECK.name
    shutil.copyfile(INPUT_DECK, output_deck)

    completed = subprocess.run(
        solver_command(),
        cwd=output_dir,
        check=False,
        capture_output=True,
        text=True,
    )
    solver_output = completed.stdout + completed.stderr
    if completed.returncode != 0:
        raise RuntimeError(f"CalculiX failed with exit code {completed.returncode}:\n{solver_output}")
    dat_path = output_dir / f"{JOB_NAME}.dat"
    if not dat_path.is_file():
        raise RuntimeError(f"CalculiX did not create {dat_path}")

    report = evaluate(
        dat_path.read_text(encoding="utf-8"),
        solver_output,
        hashlib.sha256(INPUT_DECK.read_bytes()).hexdigest(),
    )
    atomic_json(output_dir / "summary.json", report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
