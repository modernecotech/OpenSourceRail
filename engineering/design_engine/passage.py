"""One bounded native passage case per process; no alternative model on failure."""

import json
import gzip
from pathlib import Path
import subprocess
import sys
import time

from .contracts import canonical, load
from .registry import ROOT


def retained_history(folder):
    """Read the complete journal prefix after a killed writer; keep raw bytes."""
    history, warnings = [], []
    path = Path(folder) / "converged-joints.jsonl"
    if not path.is_file():
        return history, warnings
    with path.open("rb") as stream:
        for line_number, raw in enumerate(stream, 1):
            try:
                row = json.loads(raw)
            except (UnicodeDecodeError, json.JSONDecodeError):
                warnings.append(
                    dict(
                        path=path.name,
                        line=line_number,
                        basis="incomplete or invalid journal suffix retained; only preceding complete samples used",
                    )
                )
                break
            history.append(row)
    return history, warnings


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
    progress = folder / "progress.json"
    if progress.is_file():
        result["numerical_progress"] = load(progress)
    journal = folder / "converged-joints.jsonl"
    if journal.is_file():
        from .vehicle_confirmation import joint_cycles

        history, warnings = retained_history(folder)
        result["joint_resultant_cycles"] = joint_cycles(history, complete=False)
        result["journal_warnings"] = warnings
    output.write_bytes(canonical(result) + b"\n")
    return result


def main():
    from engineering.civil_exploration.spatial_vehicle import (
        run_spatial,
        SpatialDomainError,
        SpatialConvergenceError,
    )
    from .vehicle_confirmation import joint_cycles
    from .publication import digest

    data = load(sys.argv[1])
    folder = Path(sys.argv[2]).parent
    started = time.monotonic()
    samples = 0

    def checkpoint(sample):
        nonlocal samples
        samples += 1
        with (folder / "converged-joints.jsonl").open("a") as journal:
            journal.write(
                json.dumps(
                    dict(time_s=sample["time_s"], joints=sample["joints"]),
                    allow_nan=False,
                )
                + "\n"
            )
        progress = dict(
            state="incomplete",
            converged_steps=samples,
            last_converged_time_s=sample["time_s"],
            requested_duration_s=data["parameters"]["duration_s"],
            wall_seconds=time.monotonic() - started,
            last_newton_residual_n=sample["newton_residual_n"],
            last_newton_iterations=sample["newton_iterations"],
            physical_validation=False,
        )
        temporary = folder / "progress.pending.json"
        temporary.write_bytes(canonical(progress) + b"\n")
        temporary.replace(folder / "progress.json")

    try:
        result = run_spatial(
            data["model"],
            data["configuration"],
            sample_callback=checkpoint,
            **data["parameters"]
        )
        history = result.pop("history")
        result["joint_resultant_cycles"] = joint_cycles(history, complete=True)
        # Preserve the full native history once, compressed. Parent result
        # manifests reference this artifact rather than duplicating its bytes.
        artifact = folder / "native-history.json.gz"
        with gzip.open(artifact, "wt", encoding="utf-8") as stream:
            json.dump(history, stream, allow_nan=False, separators=(",", ":"))
        result["history_artifact"] = dict(
            path=artifact.name, sha256=digest(artifact), samples=len(history)
        )
        result["state"] = "completed"
    except SpatialDomainError as error:
        result = dict(
            state="outside-domain",
            error=str(error),
            time_s=error.time_s,
            violations=error.violations,
            details=error.details,
            physical_release=False,
        )
    except SpatialConvergenceError as error:
        result = dict(
            state="failed",
            error=str(error),
            time_s=error.time_s,
            residual_n=error.residual_n,
            iterations=error.iterations,
            trial_domain_exceedances=error.trial_domain_exceedances,
            physical_release=False,
        )
    except RuntimeError as error:
        result = dict(state="failed", error=str(error), physical_release=False)
    except ValueError as error:
        result = dict(
            state="outside-domain",
            error=str(error),
            requested_parameters=data["parameters"],
            physical_release=False,
        )
    result["requested_parameters"] = data["parameters"]
    if (folder / "progress.json").is_file():
        result["numerical_progress"] = load(folder / "progress.json")
        if result["state"] != "completed":
            history, warnings = retained_history(folder)
            result["joint_resultant_cycles"] = joint_cycles(history, complete=False)
            result["journal_warnings"] = warnings
    Path(sys.argv[2]).write_bytes(canonical(result) + b"\n")


if __name__ == "__main__":
    main()
