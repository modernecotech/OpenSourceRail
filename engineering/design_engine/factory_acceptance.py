"""Mandatory factory native geometry execution and common-job acceptance.

Numerical geometry acceptance is separate from structural/production release.
Missing tools, omitted models, failed jobs or changed artifacts fail this gate.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import time
import uuid

from . import factory
from .contracts import SCHEMA, identity, problem_fingerprint, problem
from .export import export, verify_export
from .registry import ROOT, get, dependencies
from .runtime import Manager, request, comparison, TERMINAL
from engineering.factory_examples import build, reproduction
from engineering.factory_examples.native import generate, digest

ACCEPTANCE_BUDGET = dict(
    evaluations=4, wall_seconds=180, memory_mib=6144, artifact_mib=512
)


def validate_problem(adapter, charter):
    problem(charter)
    if (
        problem_fingerprint(charter) != problem_fingerprint(get(adapter))
        or charter["budget"] != ACCEPTANCE_BUDGET
    ):
        raise ValueError("factory common function or acceptance budget differs")


def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(build.json_text(data))


def prerequisites(folder):
    tools = factory.toolchain()
    write(Path(folder) / "prerequisites.json", tools)
    if not tools["available"]:
        raise ValueError(
            "Required factory native prerequisites unavailable: "
            + ", ".join(tools["missing"])
        )
    return tools


def execute(folder):
    folder = Path(folder).resolve()
    prerequisites(folder)
    outputs, models = build.make_outputs()
    report = reproduction.verify(build.DEFAULT, outputs, models, build.source_hashes())
    write(folder / "recomputation.json", report)
    model_records = {}
    for key, model in models.items():
        output = folder / "models" / key
        if output.exists():
            raise ValueError("factory native execution needs fresh model directories")
        write(output / "model.json", model)
        receipt = generate(output / "model.json", output, ROOT)
        # Keep the underlying exporter logs/bootstrap inside the sealed profile.
        work = ROOT / "build/factory-examples-native" / key
        for name in ("generate.py", "freecad.log"):
            shutil.copyfile(work / name, output / name)
        model_records[key] = digest(output / "native-cad.json")
        print(
            f"Factory native {key}: {receipt['part_count']} objects, FCStd/STEP reopened",
            flush=True,
        )
    context = identity(
        dict(
            schema=SCHEMA,
            city="baghdad",
            project="baghdad",
            environment="simulation",
            configuration_revision="factory-integration-1",
            baseline_sha256=None,
            run_id=None,
            asset_id=None,
            part_id=None,
        )
    )
    manager = Manager(ROOT / "build/factory-common-jobs" / uuid.uuid4().hex)
    jobs = {}
    for adapter in sorted(factory.ADAPTERS):
        job = manager.start(
            request(
                adapter,
                context,
                refine=True,
                budget=ACCEPTANCE_BUDGET,
            )
        )
        deadline = time.monotonic() + 200
        while manager.store.get(job["id"])["status"] not in TERMINAL:
            if time.monotonic() > deadline:
                manager.store.cancel(job["id"])
                raise ValueError("factory common job exceeded acceptance watchdog")
            time.sleep(0.2)
        result = comparison(manager.store, job["id"])
        if (
            len(result["candidates"]) != 1
            or result["candidates"][0]["checks"]["native_geometry"]["state"] != "passed"
        ):
            raise ValueError("factory common native confirmation did not pass")
        export(manager.store, job["id"], folder / "jobs" / adapter, native=True)
        jobs[adapter] = dict(
            job=job["id"],
            export_manifest_sha256=digest(folder / "jobs" / adapter / "manifest.json"),
        )
        print("Factory common job/export: " + adapter, flush=True)
    execution = dict(
        schema="osr-factory-native-execution/1",
        models=model_records,
        jobs=jobs,
        source_dependencies={
            adapter: dependencies(adapter) for adapter in sorted(factory.ADAPTERS)
        },
        physical_release=False,
    )
    write(folder / "execution.json", execution)
    write(folder / "acceptance.json", acceptance(folder))


def acceptance(folder):
    folder = Path(folder)
    tools = json.loads((folder / "prerequisites.json").read_text())
    if not tools["available"] or tools["missing"] or tools != factory.toolchain():
        raise ValueError("factory native tools unavailable or changed")
    execution = json.loads((folder / "execution.json").read_text())
    _, models = build.make_outputs()
    if (
        execution.get("schema") != "osr-factory-native-execution/1"
        or set(execution["models"]) != set(models)
        or set(execution["jobs"]) != factory.ADAPTERS
    ):
        raise ValueError("factory native mandatory model/job membership differs")
    if execution["source_dependencies"] != {
        adapter: dependencies(adapter) for adapter in sorted(factory.ADAPTERS)
    }:
        raise ValueError("factory native source/input binding differs")
    for key, model in models.items():
        output = folder / "models" / key
        receipt_path = output / "native-cad.json"
        receipt = json.loads(receipt_path.read_text())
        if (
            digest(receipt_path) != execution["models"][key]
            or json.loads((output / "model.json").read_text()) != model
        ):
            raise ValueError("changed factory native model/receipt: " + key)
        if (
            receipt.get("schema") != "osr-factory-native-cad/1"
            or receipt.get("part_count") != len(model["parts"])
            or not receipt.get("fcstd_reopened")
            or not receipt.get("step_reopened")
            or receipt.get("physical_release") is not False
        ):
            raise ValueError("incomplete factory native round trip: " + key)
        if (
            receipt["input_sha256"] != digest(output / "model.json")
            or receipt["exporter_sha256"] != digest(build.PACKAGE / "native.py")
            or receipt["geometry_helpers_sha256"] != digest(build.PACKAGE / "models.py")
        ):
            raise ValueError("factory native exporter/input binding differs: " + key)
        if set(receipt["files_sha256"]) != {"model.FCStd", "model.step"}:
            raise ValueError("factory native required CAD membership differs")
        for name, sha in receipt["files_sha256"].items():
            if digest(reproduction.safe_file(output, name)) != sha:
                raise ValueError("changed factory native artifact: " + key + "/" + name)
    for adapter, job in execution["jobs"].items():
        output = folder / "jobs" / adapter
        manifest = verify_export(output)
        if (
            digest(output / "manifest.json") != job["export_manifest_sha256"]
            or manifest["job"] != job["job"]
        ):
            raise ValueError("factory common export identity differs")
        req = json.loads((output / "request.json").read_text())
        result = json.loads((output / "executed-attempt/comparison.json").read_text())
        validate_problem(adapter, req["problem"])
        if (
            req["dependencies"] != dependencies(adapter)
            or len(result["candidates"]) != 1
        ):
            raise ValueError("factory common problem/source membership differs")
        checks = result["candidates"][0]["checks"]
        if (
            adapter == "factory-precast"
            and checks["spatial_native"]["state"] != "passed"
        ):
            raise ValueError("independent spatial confirmation did not pass")
        if (
            checks["native_geometry"]["state"] != "passed"
            or checks["physical_correlation"]["state"] != "unknown"
            or checks["independent_acceptance"]["state"] != "unknown"
        ):
            raise ValueError(
                "factory common native/physical acceptance boundary differs"
            )
    from .factory_review import verify_snapshot

    snapshot = verify_snapshot(ROOT / "docs/design-engine/factory-support")
    stage_snapshot = verify_snapshot(ROOT / "docs/design-engine/factory-stages")
    whole_snapshot = verify_snapshot(ROOT / "docs/design-engine/factory-whole-bed")
    beam_snapshot = verify_snapshot(ROOT / "docs/design-engine/factory-beam-demands")
    return dict(
        schema="osr-factory-native-acceptance/1",
        passed=True,
        model_count=len(models),
        common_jobs=sorted(factory.ADAPTERS),
        geometry_only=True,
        physical_release=False,
        independent_acceptance=False,
        retained_snapshot_integrity_verified=snapshot["integrity_verified"],
        retained_stage_snapshot_integrity_verified=stage_snapshot["integrity_verified"],
        retained_whole_snapshot_integrity_verified=whole_snapshot["integrity_verified"],
        retained_beam_snapshot_integrity_verified=beam_snapshot["integrity_verified"],
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("prerequisites", "run", "verify"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.action == "prerequisites":
        prerequisites(args.output)
    elif args.action == "run":
        execute(args.output)
    else:
        result = acceptance(args.output)
        if json.loads((args.output / "acceptance.json").read_text()) != result:
            raise ValueError("factory native acceptance report differs")
        print(build.json_text(result))


if __name__ == "__main__":
    main()
