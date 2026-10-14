"""One bounded native passage case per process; no alternative model on failure."""

import json
from pathlib import Path
import subprocess
import sys

from .contracts import canonical, load
from .registry import ROOT


def case(model, configuration, parameters, folder, *, timeout=45):
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=False)
    inputs = folder / "input.json"
    inputs.write_bytes(
        canonical(dict(model=model, configuration=configuration, parameters=parameters))
        + b"\n"
    )
    output = folder / "result.json"
    with (folder / "solver.log").open("wb") as log:
        try:
            proc = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "engineering.design_engine.passage",
                    str(inputs),
                    str(output),
                ],
                cwd=ROOT,
                stdout=log,
                stderr=subprocess.STDOUT,
                timeout=timeout,
            )
            if proc.returncode != 0 or not output.is_file():
                result = dict(
                    state="failed",
                    basis="native process failed before producing a complete result",
                    exit_code=proc.returncode,
                )
            else:
                return load(output)
        except subprocess.TimeoutExpired:
            result = dict(
                state="budget-exceeded",
                basis="per-case wall-clock limit exhausted; original inputs and log retained",
                wall_seconds=timeout,
            )
    result.update(requested_parameters=parameters, physical_release=False)
    output.write_bytes(canonical(result) + b"\n")
    return result


def main():
    from engineering.civil_exploration.spatial_vehicle import run_spatial

    data = load(sys.argv[1])
    try:
        result = run_spatial(data["model"], data["configuration"], **data["parameters"])
    except (RuntimeError, ValueError) as error:
        result = dict(
            state="outside-domain",
            error=str(error),
            requested_parameters=data["parameters"],
            physical_release=False,
        )
    Path(sys.argv[2]).write_bytes(canonical(result) + b"\n")


if __name__ == "__main__":
    main()
