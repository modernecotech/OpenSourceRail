"""Execute bounded engineering searches and retain a whole-scope closure ledger.

Human-facing agent roles are allocated in the scope manifest. The deterministic
runner executes their controlled engineering evaluators, not simulated LLM agents.
"""

from __future__ import annotations

from copy import deepcopy
import json
import os
from pathlib import Path
import platform
import shutil
import time

from .coverage import (
    ROOT,
    SCOPE,
    audit,
    ledger,
    local,
    sha,
    validate_ledger,
    work_queue,
)

GENERATED = {"mechanical-cleat", "civil-steel-beam"}


def write(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True, allow_nan=False) + "\n")


def scope():
    value = json.loads(SCOPE.read_text())
    audit(value)
    return value


def common_problems(value):
    return sorted(
        {p for w in value["work_packages"] for p in w["mapped_common_problems"]}
    )


def sources(value):
    from engineering.design_engine.registry import dependencies, get

    names = {
        p.relative_to(ROOT).as_posix() for p in Path(__file__).parent.rglob("*.py")
    }
    names.update(
        p.relative_to(ROOT).as_posix()
        for p in Path(__file__).with_name("data").glob("*.json")
    )
    names.update(["tools/automation/generative-design-campaign.py", "osr"])
    names.update(s["path"] for s in value["source_inventory"])
    names.update(
        s["path"] for p in value["work_packages"] for s in p["authoritative_sources"]
    )
    result = {name: sha(local(name)) for name in sorted(names)}
    for problem in common_problems(value):
        result.update(dependencies(get(problem)["adapter"]))
    return dict(sorted(result.items()))


def environment(native):
    import numpy
    import scipy
    import numpy._core._multiarray_umath as numpy_core
    import numpy.linalg._umath_linalg as numpy_linalg
    import scipy.linalg._fblas as scipy_blas

    result = dict(
        python=platform.python_version(),
        numpy=numpy.__version__,
        scipy=scipy.__version__,
    )
    result["numerical_binaries"] = {
        m.__name__: dict(path=m.__file__, sha256=sha(m.__file__))
        for m in (numpy_core, numpy_linalg, scipy_blas)
    }
    result["thread_environment"] = {
        k: os.environ.get(k)
        for k in ("OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "OMP_NUM_THREADS")
    }
    if native:
        from engineering.design_engine.factory import toolchain

        result["factory_native"] = toolchain()
    return result


def variations(charter, count=4):
    """Declared baseline plus one-coordinate alternatives; no changed function."""
    from engineering.design_engine.generated_parts import defaults

    if type(count) is not int or not 1 <= count <= 32:
        raise ValueError("screen candidate count must be in 1..32")
    specs = charter["variables"]
    base = (
        defaults(charter["adapter"])
        if charter["adapter"] in GENERATED
        else {
            k: (v["choices"][0] if v["kind"] == "choice" else v["bounds"][0])
            for k, v in specs.items()
        }
    )
    rows = [base]
    for name, spec in specs.items():
        values = spec["choices"] if spec["kind"] == "choice" else [spec["bounds"][1]]
        for v in values:
            row = {**base, name: v}
            if row not in rows:
                rows.append(row)
    return rows[:count]


def plan():
    value = scope()
    return dict(
        schema="osr-multi-agent-design-plan/1",
        inventory=audit(value),
        roles=sorted({p["owner_agent_role"] for p in value["work_packages"]}),
        common_problems=common_problems(value),
        work_packages=value["work_packages"],
        execution="Civil/mechanical feedback searches, bed-force propagation, bounded common variations, native holdouts, interface critique, evidence closure",
        stopping="Research-screen frontier, exhausted finite domain or explicit resource limit; unresolved packages remain queued, never promoted by a search pass",
        all_systems_design_complete=False,
        physical_release=False,
    )


def validate_common_request(req):
    from engineering.design_engine.registry import get, dependencies
    from engineering.design_engine.contracts import problem_fingerprint
    from engineering.design_engine.runtime import toolchain

    charter = req["problem"]
    if problem_fingerprint(charter) != problem_fingerprint(get(charter["id"])):
        raise ValueError("imported common function/charter differs")
    if req["dependencies"] != dependencies(charter["adapter"]) or req[
        "toolchain"
    ] != toolchain(charter["adapter"]):
        raise ValueError("imported common source/toolchain is stale")


def collect_common(store, identifier, destination):
    from engineering.design_engine.runtime import comparison

    job = store.verify_request(identifier)
    validate_common_request(job["request"])
    if not job["active_attempt"]:
        raise ValueError("common job has no execution attempt")
    manifest = store.verify_attempt(identifier, job["active_attempt"])
    report = (
        comparison(store, identifier)
        if job["status"] == "completed"
        else dict(candidates=[], evaluations_spent=None, recursive_search=None)
    )
    problem = job["request"]["problem"]["id"]
    folder = store.root / "runs" / identifier / f'attempt-{job["active_attempt"]:04d}'
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=False)
    for name, source in [
        ("request.json", folder.parent / "request.json"),
        ("comparison.json", folder / "comparison.json"),
        ("manifest.json", folder / "manifest.json"),
    ]:
        if source.is_file():
            shutil.copyfile(source, destination / name)
    recursive = report.get("recursive_search")
    native_files = []
    # Compact projections retain actual native CAD and the candidate's numerical
    # receipt; full meshes, decks and solver logs remain in the sealed parent job.
    if recursive:
        for candidate in report["candidates"]:
            parent = folder / "recursive-native" / candidate["id"]
            if not parent.is_dir():
                continue
            target = destination / "native" / candidate["id"]
            for source in sorted(parent.rglob("*")):
                if source.is_file() and (
                    source.suffix == ".FCStd"
                    or source.name
                    in {
                        "native.json",
                        "definition.json",
                        "summary.json",
                        "native-cad.json",
                        "native-result.json",
                    }
                ):
                    artifact = target / source.relative_to(parent)
                    artifact.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(source, artifact)
                    native_files.append(artifact.relative_to(destination).as_posix())
    record = dict(
        problem=problem,
        job=identifier,
        status=job["status"],
        error=job.get("error"),
        parent_store=store.root.relative_to(ROOT).as_posix(),
        attempt=job["active_attempt"],
        request_sha256=sha(destination / "request.json"),
        comparison_sha256=(
            sha(destination / "comparison.json")
            if (destination / "comparison.json").exists()
            else None
        ),
        manifest_sha256=sha(destination / "manifest.json"),
        parent_artifact_count=len(manifest["artifacts"]),
        parent_verified_at_collection=True,
        candidate_count=len(report["candidates"]),
        evaluations_spent=report["evaluations_spent"],
        verified_frontier=report.get("verified_frontier", []),
        recursive_termination=(
            recursive.get("termination_reason") if recursive else None
        ),
        finite_domain_complete=(
            recursive.get("finite_domain_complete") if recursive else False
        ),
        native_domain_complete=(
            recursive.get("native_domain_complete") if recursive else False
        ),
        compact_native_files=native_files,
        physical_release=False,
    )
    write(destination / "evidence.json", record)
    return record


def execute_common(value, output, mode, store_path, imported, revision):
    from engineering.design_engine.runtime import Manager, request, TERMINAL
    from engineering.design_engine.contracts import identity, SCHEMA
    from engineering.design_engine.registry import get

    if mode not in {"none", "screen", "native"}:
        raise ValueError("common execution mode must be none/screen/native")
    if mode == "none":
        if imported:
            raise ValueError("cannot import jobs when common execution is disabled")
        return {}
    if not Path(store_path).resolve().is_relative_to(ROOT):
        raise ValueError("common store must remain in the repository workspace")
    manager = Manager(store_path)
    imported_by_problem = {}
    for identifier in imported:
        job = manager.store.verify_request(identifier)
        validate_common_request(job["request"])
        problem = job["request"]["problem"]["id"]
        context = job["request"]["identity"]
        if problem in imported_by_problem or problem not in common_problems(value):
            raise ValueError("duplicate or unrelated imported common problem")
        if (
            context["city"] != "baghdad"
            or context["project"] != "baghdad"
            or context["environment"] != "simulation"
            or context["configuration_revision"] != revision
        ):
            raise ValueError("imported job refers to another campaign scope")
        if job["status"] not in TERMINAL:
            raise ValueError("import requires a terminal sealed common execution")
        if (
            mode == "native"
            and problem in GENERATED
            and not job["request"].get("recursive")
        ):
            raise ValueError(
                "native part campaign requires actual recursive confirmation"
            )
        imported_by_problem[problem] = identifier
    context = identity(
        dict(
            schema=SCHEMA,
            city="baghdad",
            project="baghdad",
            environment="simulation",
            configuration_revision=revision,
            baseline_sha256=None,
            run_id=None,
            asset_id=None,
            part_id=None,
        )
    )
    results = {}
    for problem in common_problems(value):
        if problem in imported_by_problem:
            identifier = imported_by_problem[problem]
        else:
            kwargs = {}
            if mode == "native" and problem in GENERATED:
                kwargs.update(
                    budget=dict(evaluations=24, wall_seconds=360),
                    recursive=dict(
                        evaluations=12,
                        confirmations=6,
                        iterations=32,
                        finite_exhaustive=True,
                    ),
                )
            else:
                kwargs.update(
                    candidates=variations(get(problem)),
                    budget=dict(evaluations=16, wall_seconds=180),
                )
            req = request(problem, context, **kwargs)
            identifier = manager.start(req)["id"]
            deadline = time.monotonic() + req["problem"]["budget"]["wall_seconds"] + 30
            while manager.store.get(identifier)["status"] not in TERMINAL:
                if time.monotonic() > deadline:
                    manager.store.cancel(identifier)
                    raise RuntimeError("common campaign watchdog: " + identifier)
                time.sleep(0.2)
        results[problem] = collect_common(
            manager.store, identifier, output / "common" / problem
        )
        print(
            f'Common {problem}: {results[problem]["status"]}, {results[problem]["candidate_count"]} candidates',
            flush=True,
        )
    return results


def run(
    output,
    *,
    civil_budget=128,
    mechanical_budget=128,
    native=False,
    common="native",
    common_store=None,
    import_jobs=(),
    revision="multi-agent-manufacturing-1",
):
    from . import civil, mechanical, coupling
    from engineering.factory_examples.native import generate

    if (
        type(civil_budget) is not int
        or not 1 <= civil_budget <= 2048
        or type(mechanical_budget) is not int
        or not 1 <= mechanical_budget <= 4096
    ):
        raise ValueError(
            "bounded lane budgets required: civil 1..2048, mechanical 1..4096"
        )
    output = Path(output).resolve()
    if output.exists() or not output.is_relative_to(ROOT / "build"):
        raise ValueError("immutable campaign needs a fresh directory under build/")
    value = scope()
    source = sources(value)
    tools = environment(native)
    output.mkdir(parents=True)
    write(output / "scope.json", value)
    write(output / "inventory-audit.json", audit(value))
    write(
        output / "request.json",
        dict(
            schema="osr-generative-campaign-request/1",
            revision=revision,
            civil_budget=civil_budget,
            mechanical_budget=mechanical_budget,
            native=native,
            common=common,
            source_sha256=source,
            environment=tools,
            physical_release=False,
        ),
    )
    try:
        lanes, native_records = {}, []
        for name, evaluator, budget in (
            ("civil", civil, civil_budget),
            ("mechanical", mechanical, mechanical_budget),
        ):
            report = evaluator.search(budget=budget)
            lanes[name] = report
            write(output / name / "search.json", report)
            models = evaluator.write_artifacts(report, output / name / "models")
            for item in models:
                model = Path(item["model"] if isinstance(item, dict) else item)
                if native:
                    try:
                        receipt = generate(Path(model), Path(model).parent, ROOT)
                        native_records.append(
                            dict(
                                lane=name,
                                model=Path(model).relative_to(output).as_posix(),
                                receipt=(Path(model).parent / "native-cad.json")
                                .relative_to(output)
                                .as_posix(),
                                status="passed",
                                part_count=receipt["part_count"],
                                physical_release=False,
                            )
                        )
                    except Exception as error:
                        native_records.append(
                            dict(
                                lane=name,
                                model=Path(model).relative_to(output).as_posix(),
                                status="failed",
                                error=str(error),
                                physical_release=False,
                            )
                        )
            print(
                f'{name}: {len(report["candidates"])} candidates, {len(report["selected_candidate_ids"])} selected local research alternatives',
                flush=True,
            )
        coupled = coupling.search(lanes["civil"])
        write(output / "bed-coupling.json", coupled)
        common_results = execute_common(
            value,
            output,
            common,
            common_store or output / "common-store",
            import_jobs,
            revision,
        )
        closure = ledger(value, lanes, common_results)
        write(output / "closure-ledger.json", closure)
        write(output / "work-queue.json", work_queue(value, closure))
        result = dict(
            schema="osr-generative-campaign/1",
            revision=revision,
            inventory_coverage_verified=True,
            work_package_count=len(value["work_packages"]),
            lane_summaries={
                name: dict(
                    candidate_count=len(r["candidates"]),
                    selected_candidate_ids=r["selected_candidate_ids"],
                    termination=r["termination"],
                )
                for name, r in lanes.items()
            },
            bed_coupling_candidate_count=len(coupled["candidates"]),
            native_geometry=native_records,
            common=common_results,
            closure_counts=closure["counts"],
            completed_packages=0,
            all_systems_design_complete=False,
            manufacturing_release=False,
            physical_release=False,
            known_gaps="Partial research evaluators do not cover full release packages. Unknown loads, materials, tolerances, complete process/tooling, supplier and physical evidence retain open completion gates.",
        )
        write(output / "summary.json", result)
        from .review import page

        (output / "index.html").write_text(page(result, closure, lanes, coupled))
        if sources(value) != source or environment(native) != tools:
            raise ValueError(
                "campaign sources or numerical environment changed during execution"
            )
        files = {
            p.relative_to(output).as_posix(): sha(p)
            for p in sorted(output.rglob("*"))
            if p.is_file() and not p.is_relative_to(output / "common-store")
        }
        write(
            output / "receipt.json",
            dict(
                schema="osr-generative-campaign-receipt/1",
                source_sha256=source,
                environment=tools,
                files_sha256=files,
                physical_release=False,
            ),
        )
        return verify(output)
    except Exception as error:
        write(
            output / "failure.json",
            dict(
                error=type(error).__name__, message=str(error), physical_release=False
            ),
        )
        raise


def verify(output, *, current=True):
    from engineering.design_engine.store import Store

    output = Path(output).resolve()
    receipt = json.loads((output / "receipt.json").read_text())
    if (
        receipt.get("schema") != "osr-generative-campaign-receipt/1"
        or receipt.get("physical_release") is not False
    ):
        raise ValueError("controlled unreleased campaign receipt required")
    expected = set(receipt["files_sha256"])
    actual = {
        p.relative_to(output).as_posix()
        for p in output.rglob("*")
        if p.is_file()
        and p != output / "receipt.json"
        and not p.is_relative_to(output / "common-store")
    }
    if expected != actual:
        raise ValueError("campaign artifact membership differs")
    for name, digest in receipt["files_sha256"].items():
        if sha(local(name, output)) != digest:
            raise ValueError("campaign artifact changed: " + name)
    value = json.loads((output / "scope.json").read_text())
    if current:
        audit(value)
        native = json.loads((output / "request.json").read_text())["native"]
        if (
            sources(value) != receipt["source_sha256"]
            or environment(native) != receipt["environment"]
        ):
            raise ValueError("campaign belongs to another source/toolchain revision")
    result = json.loads((output / "summary.json").read_text())
    closure = json.loads((output / "closure-ledger.json").read_text())
    validate_ledger(value, closure)
    if (
        result["all_systems_design_complete"] is not False
        or result["manufacturing_release"] is not False
        or result["physical_release"] is not False
    ):
        raise ValueError("research campaign cannot grant manufacturing/design release")
    if len(closure["work_packages"]) != len(value["work_packages"]) or any(
        p["design_complete"] or p["manufacturing_release"] or p["physical_release"]
        for p in closure["work_packages"]
    ):
        raise ValueError("research closure ledger cannot hide or promote work packages")
    for record in result["native_geometry"]:
        if record["status"] != "passed":
            continue
        model = output / record["model"]
        proof = json.loads((output / record["receipt"]).read_text())
        if (
            proof["input_sha256"] != sha(model)
            or not proof["fcstd_reopened"]
            or not proof["step_reopened"]
        ):
            raise ValueError("native geometry correspondence differs")
        for name, digest in proof["files_sha256"].items():
            if sha(model.parent / name) != digest:
                raise ValueError("native geometry artifact differs")
    for record in result["common"].values():
        store = Store(local(record["parent_store"]))
        job = store.verify_request(record["job"])
        if current:
            validate_common_request(job["request"])
        store.verify_attempt(record["job"], record["attempt"])
        parent = store.root / "runs" / record["job"]
        attempt = parent / f'attempt-{record["attempt"]:04d}'
        if (
            sha(parent / "request.json") != record["request_sha256"]
            or (
                sha(attempt / "comparison.json")
                if (attempt / "comparison.json").exists()
                else None
            )
            != record["comparison_sha256"]
            or sha(attempt / "manifest.json") != record["manifest_sha256"]
        ):
            raise ValueError("common parent evidence differs")
    return dict(
        integrity_verified=True,
        current_sources_checked=current,
        parent_common_attempts_verified=len(result["common"]),
        native_geometry_passed=sum(
            r["status"] == "passed" for r in result["native_geometry"]
        ),
        native_geometry_failed=sum(
            r["status"] != "passed" for r in result["native_geometry"]
        ),
        all_systems_design_complete=False,
        physical_release=False,
    )
