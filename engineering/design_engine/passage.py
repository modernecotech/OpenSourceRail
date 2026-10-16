"""One bounded native passage case per process; no alternative model on failure."""

import json
import gzip
import hashlib
import importlib.metadata
import platform
from pathlib import Path
import subprocess
import sys
import time

from .contracts import canonical, load
from .registry import ROOT
from .publication import digest, safe


def solver_toolchain():
    """Identity of the interpreter and numerical packages actually executing."""
    return dict(
        python=sys.version,
        implementation=platform.python_implementation(),
        platform=platform.platform(),
        executable_sha256=digest(Path(sys.executable).resolve()),
        **{name: importlib.metadata.version(name) for name in ("numpy", "scipy")},
    )


def seal_case(folder):
    """Bind the retained input, native result and all original case artifacts."""
    folder = Path(folder)
    result = load(folder / "result.json")
    manifest = dict(
        schema="osr-native-passage-manifest/1",
        files={
            p.relative_to(folder).as_posix(): digest(p)
            for p in sorted(folder.rglob("*"))
            if p.is_file() and p != folder / "case-manifest.json"
        },
        source_sha256=result.get("source_sha256"),
        solver_toolchain=result.get("solver_toolchain"),
        physical_validation=False,
    )
    target = folder / "case-manifest.json"
    with target.open("xb") as stream:
        stream.write(canonical(manifest) + b"\n")
    return {
        **result,
        "retained_manifest": dict(path=target.name, sha256=digest(target)),
    }


def verify_case(folder, result, *, model, configuration, parameters):
    """Verify retained bytes and exact inputs before using any native metrics.

    These are local integrity records, not independent solver attestations.
    In-memory annotations cannot replace a retained result or missing history.
    """
    from osr_mech.engineering_definition import fingerprint as native_hash

    folder = Path(folder)
    reference = result.get("retained_manifest", {})
    manifest_path = folder / "case-manifest.json"
    if reference.get("path") != manifest_path.name or not manifest_path.is_file():
        raise ValueError("retained passage manifest required")
    if digest(manifest_path) != reference.get("sha256"):
        raise ValueError("retained passage manifest changed")
    manifest = load(manifest_path)
    if manifest.get("schema") != "osr-native-passage-manifest/1":
        raise ValueError("unsupported passage manifest")
    files = manifest.get("files", {})
    if not {"input.json", "result.json", "solver.log"} <= files.keys():
        raise ValueError("passage manifest omits required artifacts")
    actual = set()
    for path in folder.rglob("*"):
        if path.is_symlink():
            raise ValueError("symlinked passage artifact")
        if path.is_file() and path != manifest_path:
            actual.add(path.relative_to(folder).as_posix())
    if actual != set(files):
        raise ValueError("passage artifact closure changed")
    for name, expected in files.items():
        target = safe(folder, name)
        if not target.is_file() or digest(target) != expected:
            raise ValueError("retained passage artifact changed: " + name)
    inputs = load(folder / "input.json")
    if inputs != dict(model=model, configuration=configuration, parameters=parameters):
        raise ValueError("retained passage inputs do not match comparison")
    retained = load(folder / "result.json")
    annotations = {
        "retained_manifest",
        "allocated_wall_seconds",
        "passage_plan",
        "full_passage_coverage",
    }
    if {k: v for k, v in result.items() if k not in annotations} != retained:
        raise ValueError("comparison result differs from retained passage result")
    if retained.get("input_sha256") != files["input.json"]:
        raise ValueError("native passage input hash differs")
    sources = retained.get("source_sha256")
    tools = retained.get("solver_toolchain")
    if (
        not isinstance(sources, dict)
        or not sources
        or any(
            not isinstance(v, str)
            or len(v) != 64
            or any(c not in "0123456789abcdef" for c in v)
            for v in sources.values()
        )
        or not isinstance(tools, dict)
        or not all(
            tools.get(k) for k in ("python", "numpy", "scipy", "executable_sha256")
        )
        or manifest.get("source_sha256") != sources
        or manifest.get("solver_toolchain") != tools
    ):
        raise ValueError("complete passage source and toolchain identities required")
    if (
        retained.get("source_unchanged") is not True
        or retained.get("toolchain_unchanged") is not True
    ):
        raise ValueError("passage source/toolchain changed during execution")
    if retained.get("state") == "completed":
        if (
            retained.get("configuration_sha256") != native_hash(configuration)
            or retained.get("hardware_definition_sha256") != native_hash(model)
            or retained.get("requested_parameters") != parameters
        ):
            raise ValueError("native passage scope differs from retained inputs")
        history = retained.get("history_artifact", {})
        if history.get("path") not in files or history.get("sha256") != files.get(
            history.get("path")
        ):
            raise ValueError("retained native history required")
    return retained


def physics_snapshot():
    """Conservative native source closure, independent of common UI/registry edits."""
    paths = set()
    for directory in (
        "engineering/civil_exploration",
        "engineering/integration_programme",
        "design/component-catalogue/src/osr_mech",
    ):
        paths.update((ROOT / directory).rglob("*.py"))
    paths.update(
        ROOT / name
        for name in (
            "engineering/design_engine/passage.py",
            "engineering/design_engine/vehicle_confirmation.py",
            "engineering/design_engine/vehicle_campaign.py",
            "engineering/design_engine/contracts.py",
            "engineering/design_engine/publication.py",
            "engineering/industrialisation/common.py",
            "design/component-catalogue/schemas/shared-engineering-model.json",
        )
    )
    return {
        p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(paths)
        if p.is_file()
    }


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
    source_before = physics_snapshot()
    tools_before = solver_toolchain()
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
                result = load(output)
        except subprocess.TimeoutExpired:
            result = dict(
                state="budget-exceeded",
                basis="per-case wall-clock limit exhausted; original inputs and log retained",
                wall_seconds=timeout,
            )
    result.update(requested_parameters=parameters, physical_release=False)
    source_after = physics_snapshot()
    tools_after = solver_toolchain()
    unchanged = (
        source_before == source_after
        and result.get("source_sha256", source_before) == source_before
        and result.get("source_unchanged", True) is True
    )
    tools_unchanged = (
        tools_before == tools_after
        and result.get("solver_toolchain", tools_before) == tools_before
        and result.get("toolchain_unchanged", True) is True
    )
    result.update(
        source_sha256=source_before,
        source_unchanged=unchanged,
        solver_toolchain=tools_before,
        toolchain_unchanged=tools_unchanged,
        input_sha256=digest(inputs),
    )
    if not unchanged or not tools_unchanged:
        result.update(solver_state=result["state"], state="stale")
    progress = folder / "progress.json"
    if progress.is_file():
        result["numerical_progress"] = load(progress)
    journal = folder / "converged-joints.jsonl"
    if journal.is_file() and result.get("state") != "completed":
        from .vehicle_confirmation import joint_cycles

        history, warnings = retained_history(folder)
        result["joint_resultant_cycles"] = joint_cycles(history, complete=False)
        result["journal_warnings"] = warnings
    output.write_bytes(canonical(result) + b"\n")
    return seal_case(folder)


def main():
    from engineering.civil_exploration.spatial_vehicle import (
        run_spatial,
        SpatialDomainError,
        SpatialConvergenceError,
    )
    from .vehicle_confirmation import joint_cycles, incremental_demands
    from .publication import digest

    data = load(sys.argv[1])
    source_before = physics_snapshot()
    tools_before = solver_toolchain()
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
            **data["parameters"],
        )
        history = result.pop("history")
        result["joint_resultant_cycles"] = joint_cycles(history, complete=True)
        result.update(incremental_demands(history))
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
    source_after = physics_snapshot()
    result["source_sha256"] = source_before
    result["source_unchanged"] = source_before == source_after
    result["solver_toolchain"] = tools_before
    result["toolchain_unchanged"] = tools_before == solver_toolchain()
    result["input_sha256"] = hashlib.sha256(Path(sys.argv[1]).read_bytes()).hexdigest()
    if source_before != source_after or not result["toolchain_unchanged"]:
        result["solver_state"] = result["state"]
        result["state"] = "stale"
        result["basis"] = (
            "native physical source changed during execution; result cannot qualify refinement"
        )
        result["source_after_sha256"] = source_after
    if (folder / "progress.json").is_file():
        result["numerical_progress"] = load(folder / "progress.json")
        if result["state"] != "completed":
            history, warnings = retained_history(folder)
            result["joint_resultant_cycles"] = joint_cycles(history, complete=False)
            result["journal_warnings"] = warnings
    Path(sys.argv[2]).write_bytes(canonical(result) + b"\n")


if __name__ == "__main__":
    main()
