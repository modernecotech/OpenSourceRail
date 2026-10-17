"""A proposal/measurement loop, not an autonomous engineering approval authority.

AI providers return data, never executable acceptance logic. Existing native CAD,
IFC and solver adapters perform the checks. All railway work orders remain open
until a separate, authenticated engineering acceptance integration exists.
"""
from __future__ import annotations

from copy import deepcopy
import fcntl
import gzip
import hashlib
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
PACKET = ROOT / "docs/design-engine/baghdad-digital-twin-2026-10-17"
FLAGS = dict(design_complete=False, physical_validation=False,
             manufacturing_release=False, physical_release=False)
KINDS = ("mechanical-cleat", "civil-steel-beam", "vehicle-interface", "civil-bay", "software-precharge", "controlled-assembly")
MAX_JSON = 2_000_000


def encoded(value):
    return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + "\n").encode()


def digest(value):
    return hashlib.sha256(encoded(value)).hexdigest()


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read(path, *, maximum=MAX_JSON):
    path = Path(path)
    if path.stat().st_size > maximum:
        raise ValueError("JSON input exceeds configured byte limit")
    def reject(value):
        raise ValueError("non-finite JSON: " + value)
    def pairs(rows):
        result = {}
        for key, value in rows:
            if key in result:
                raise ValueError("duplicate JSON key: " + key)
            result[key] = value
        return result
    return json.loads(path.read_text(), parse_constant=reject, object_pairs_hook=pairs)


def write(path, value, *, exclusive=False):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if exclusive:
        with path.open("xb") as stream:
            stream.write(encoded(value))
    else:
        temp = path.with_suffix(path.suffix + ".tmp")
        temp.write_bytes(encoded(value))
        temp.replace(path)


def sources():
    # Includes source-qualified baseline, all solver/geometry dependencies and
    # controller/acceptance code. New inputs require a new immutable workspace.
    from engineering.generative_design import digital_thread as dt
    result = dt.freeze_sources(dt.design_scenario.plan())
    paths = list((ROOT / "engineering/twin_workflow").glob("*.py"))
    paths += list((ROOT / "engineering/design_consistency").glob("*.py"))
    paths += [ROOT / "tools/automation/twin-completion.py"]
    paths += list((PACKET).glob("*.gz")) + [PACKET / "manifest.json", PACKET / "summary.json"]
    for path in paths:
        result[path.relative_to(ROOT).as_posix()] = sha(path)
    return result


def current(state):
    if digest(state["source_sha256"]) != state["baseline_sha256"]:
        raise ValueError("baseline/source digest mismatch")
    changed = [p for p, expected in state["source_sha256"].items()
               if not (ROOT / p).is_file() or sha(ROOT / p) != expected]
    if changed:
        raise ValueError("stale workflow sources; initialise a fresh workspace: " + ", ".join(changed[:6]))


def work_orders(graph, requests):
    orders = []
    for item in graph["items"]:
        orders.append(dict(id=item["id"], catalogue_id=item["catalogue_id"],
            title=item["title"], package_ids=item["package_ids"], source=item["source"],
            source_sha256=item["source_sha256"],
            source_pointers=[r["pointer"] for r in item["source_records"]],
            required_detail_sections=item["required_detail_sections"],
            relationships=[r for r in graph["relationships"] if item["id"] in (r["parent_id"], r["child_id"])],
            stages={k: "open" for k in ("requirements", "parts_and_assembly", "manufacturing",
                "independent_simulation", "system_integration", "physical_correlation", "authenticated_acceptance")},
            state="open", **FLAGS))
    return dict(schema="osr-twin-work-orders/1", packages=graph["packages"], items=orders,
                requests=requests, count_semantics="Controlled source items; not an exhaustive physical BOM", **FLAGS)


def initialise(workspace, seeds=None):
    from engineering.generative_design import digital_thread as dt
    dt.verify(PACKET)
    graph = json.loads(gzip.decompress((PACKET / "specifications.json.gz").read_bytes()))
    requests = json.loads(gzip.decompress((PACKET / "open-requests.json.gz").read_bytes()))
    inputs = sources()
    workspace = Path(workspace).resolve()
    workspace.mkdir(parents=True, exist_ok=False)
    orders = work_orders(graph, requests)
    write(workspace / "work-orders.json", orders, exclusive=True)
    state = dict(schema="osr-twin-completion-controller/1", source_sha256=inputs,
        baseline_sha256=digest(inputs), work_orders_sha256=sha(workspace / "work-orders.json"),
        proposals=[], receipts=[], provider_calls=[], stop_reason="ready", **FLAGS)
    write(workspace / "state.json", state, exclusive=True)
    if seeds is not None:
        submit(workspace, seeds)
    return status(workspace)


def validate(proposal, baseline):
    if not isinstance(proposal, dict) or set(proposal) != {
        "schema", "id", "baseline_sha256", "kind", "parameters", "rationale", "sources", "expected_tests"
    }:
        raise ValueError("proposal requires exact typed contract; no approval fields, scripts or changed test limits")
    if proposal["schema"] != "osr-twin-proposal/1" or proposal["baseline_sha256"] != baseline:
        raise ValueError("proposal schema/baseline mismatch")
    if not isinstance(proposal["id"], str) or not 1 <= len(proposal["id"]) <= 100:
        raise ValueError("bounded proposal identity required")
    if not isinstance(proposal["rationale"], str) or not 1 <= len(proposal["rationale"]) <= 8000:
        raise ValueError("bounded design rationale required")
    if not isinstance(proposal["sources"], list) or len(proposal["sources"]) > 20 or any(
        not isinstance(s, str) or len(s) > 2048 for s in proposal["sources"]
    ):
        raise ValueError("bounded source references required; citations are hints, not accepted inputs")
    if not isinstance(proposal["expected_tests"], list) or not proposal["expected_tests"] or any(
        not isinstance(s, str) or len(s) > 200 for s in proposal["expected_tests"]
    ) or len(proposal["expected_tests"]) > 20:
        raise ValueError("expected tests describe intent, not acceptance commands")
    kind, params = proposal["kind"], proposal["parameters"]
    if kind not in KINDS or not isinstance(params, dict):
        raise ValueError("adapter missing; issue an adapter-development work order")
    if kind in ("mechanical-cleat", "civil-steel-beam"):
        from engineering.design_engine.generated_parts import compile_definition
        compile_definition(kind, params)
    elif kind == "civil-bay":
        choices = dict(length=[20., 25.], pier_height=[6., 8.], pile_length=[12., 15.], pile_spacing=[2., 2.5])
        if set(params) != set(choices) or any(type(v) not in (int, float) or v not in choices[k] for k, v in params.items()):
            raise ValueError("civil bay parameters must be within declared research domain")
    elif kind == "software-precharge":
        if set(params) != {"policy"} or params["policy"] not in ("ratio-only", "interlocks-only", "guarded"):
            raise ValueError("unregistered software policy; new source needs isolated patch/review workflow")
    elif kind == "controlled-assembly":
        if set(params) != {"contract"}:
            raise ValueError("controlled-assembly requires one pure-data contract")
        from engineering.design_consistency.contracts import validate as assembly_validate
        contract = params["contract"]
        if not isinstance(contract, dict) or not 1 <= len(contract.get("parts", [])) <= 128:
            raise ValueError("assembly requires 1..128 parts per candidate")
        if len(encoded(contract)) > 500_000:
            raise ValueError("assembly contract exceeds 500 kB")
        for part in contract["parts"]:
            # No uploaded scripts, macros, external evidence paths or FCStd objects.
            if part.get("evidence") or len(part["manufacturing"]["primitives"]) > 32:
                raise ValueError("proposal evidence stays in source hints; at most 32 primitives per part")
        assembly_validate(contract)
    elif params:
        raise ValueError("vehicle interface pilot has a fixed dimensional recipe")
    return digest(dict(kind=kind, parameters=params, baseline_sha256=baseline))


def _add(state, proposals):
    if not isinstance(proposals, list) or len(proposals) > 32:
        raise ValueError("at most 32 proposals per submission")
    pending = deepcopy(state["proposals"])
    count = 0
    for value in proposals:
        key = validate(value, state["baseline_sha256"])
        if any(p["design_sha256"] == key for p in pending):
            continue
        if len(pending) >= 256:
            raise ValueError("workspace proposal budget reached; archive before continuing")
        if any(p["proposal"]["id"] == value["id"] for p in pending):
            raise ValueError("proposal identity already used for different design")
        pending.append(dict(design_sha256=key, proposal=value))
        count += 1
    if len(encoded(pending)) > 1_000_000:
        raise ValueError("candidate pool exceeds 1 MB; use a fresh bounded workspace")
    state["proposals"] = pending
    return count


def _lock(workspace):
    handle = (Path(workspace) / ".lock").open("a")
    try:
        fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        handle.close()
        raise ValueError("workspace is already being updated")
    return handle


def submit(workspace, proposals):
    workspace = Path(workspace)
    with _lock(workspace):
        state = read(workspace / "state.json")
        current(state)
        count = _add(state, proposals)
        if count:
            state["stop_reason"] = "ready"
        write(workspace / "state.json", state)
    return dict(added=count, **FLAGS)


def status(workspace, *, check_current=True):
    workspace = Path(workspace)
    state = read(workspace / "state.json")
    if check_current:
        current(state)
    if sha(workspace / "work-orders.json") != state["work_orders_sha256"]:
        raise ValueError("work orders were modified outside controlled baseline")
    orders = read(workspace / "work-orders.json", maximum=10_000_000)
    done = {r["design_sha256"] for r in state["receipts"]}
    return dict(schema=state["schema"], baseline_sha256=state["baseline_sha256"],
        work_packages=len(orders["packages"]), controlled_items=len(orders["items"]),
        open_baseline_requests=len(orders["requests"]),
        evaluated_candidates=len(done), queued_candidates=sum(p["design_sha256"] not in done for p in state["proposals"]),
        study_pass_candidates=sum(r["study_pass"] for r in state["receipts"]),
        completed_specifications=0, provider_calls=len(state["provider_calls"]),
        stop_reason=state["stop_reason"], **FLAGS)


def _size(workspace):
    return sum(p.stat().st_size for p in Path(workspace).rglob("*") if p.is_file())


def _process(argv, folder, stdin, timeout, workspace, max_bytes, reserve_bytes):
    """Fixed local adapters or an explicitly supplied operator command, no shell.

    This provides timeout/output limits, not a security sandbox for provider code.
    """
    log = folder / "process.log"
    input_path = folder / "input.json"
    input_path.write_bytes(stdin or b"")
    with log.open("wb") as out, (folder / "process.stderr.log").open("wb") as err, input_path.open("rb") as incoming:
        process = subprocess.Popen(argv, stdin=incoming,
            stdout=out, stderr=err, cwd=ROOT, start_new_session=True)
        try:
            deadline = time.monotonic() + timeout
            while process.poll() is None:
                if time.monotonic() >= deadline:
                    raise TimeoutError("workflow wall-time budget reached")
                if _size(workspace) > max_bytes or shutil.disk_usage(workspace).free < reserve_bytes:
                    raise RuntimeError("workflow output/disk budget reached")
                time.sleep(.25)
            if process.returncode:
                raise RuntimeError("adapter/provider failed; inspect " + str(log))
            if _size(workspace) > max_bytes:
                raise RuntimeError("workflow output budget exceeded")
        finally:
            if process.poll() is None:
                from engineering.design_engine.generated_parts_native import _stop_owned_descendants
                _stop_owned_descendants(process)
    return log


def provider_request(state, orders):
    from engineering.design_engine.generated_parts import variables
    return dict(schema="osr-twin-agent-request/1", baseline_sha256=state["baseline_sha256"],
        instructions="Return JSON {proposals:[...]}. Generate a distinct design using feedback. "
        "Never alter checks, loads or limits. URLs are design hints only. If no supported improvement exists return proposals:[]. "
        "No approval fields or executable code. Unavailable model families need a reviewed adapter, not a fabricated completion.",
        prototype=dict(schema="osr-twin-proposal/1", id="distinct-design-name",
            baseline_sha256=state["baseline_sha256"], kind="mechanical-cleat",
            parameters={}, rationale="Explain proposed improvement and tradeoffs", sources=[], expected_tests=["native geometry", "elastic response"]),
        domains={**{k: variables(k) for k in KINDS[:2]},
            "vehicle-interface": {"parameters": {}},
            "civil-bay": dict(length=[20., 25.], pier_height=[6., 8.], pile_length=[12., 15.], pile_spacing=[2., 2.5]),
            "software-precharge": dict(policy=["ratio-only", "interlocks-only", "guarded"])},
        previous_designs=state["proposals"], feedback=state["receipts"],
        work_orders_sha256=state["work_orders_sha256"],
        open_item_count=len(orders["items"]), open_request_count=len(orders["requests"]),
        capability_scope="Five research recipes plus pure-data assembly authoring (128 parts). "
        "For controlled-assembly use engineering.design_consistency.contracts schema, with empty evidence arrays. "
        "A passing example does not close any railway item", **FLAGS)


def run(workspace, *, steps=8, wall_seconds=900, max_output_mib=512,
        reserve_gib=5, provider_argv=None):
    workspace = Path(workspace).resolve()
    if type(steps) is not int or not 1 <= steps <= 32:
        raise ValueError("step budget must be 1..32")
    for value, low, high in ((wall_seconds, 1, 7200), (max_output_mib, 1, 4096), (reserve_gib, .1, 100)):
        if type(value) not in (int, float) or not math.isfinite(value) or not low <= value <= high:
            raise ValueError("invalid workflow resource budget")
    if provider_argv is not None and (not isinstance(provider_argv, list) or not provider_argv or
        any(not isinstance(p, str) or not p or len(p) > 4096 for p in provider_argv)):
        raise ValueError("provider command must be an operator-supplied argv list")
    with _lock(workspace):
        state = read(workspace / "state.json")
        status(workspace)
        orders = read(workspace / "work-orders.json", maximum=10_000_000)
        deadline = time.monotonic() + wall_seconds
        max_bytes, reserve = max_output_mib * 1024**2, reserve_gib * 1024**3
        from engineering.design_engine.generated_parts_native import toolchain
        environment = toolchain()
        for _ in range(steps):
            current(state)
            if _size(workspace) >= max_bytes or shutil.disk_usage(workspace).free < reserve:
                state["stop_reason"] = "disk-budget"
                break
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                state["stop_reason"] = "wall-time-budget"
                break
            done = {r["design_sha256"] for r in state["receipts"]}
            candidate = next((p for p in state["proposals"] if p["design_sha256"] not in done), None)
            if candidate is None:
                if provider_argv is None:
                    state["stop_reason"] = "needs-new-proposals-or-evidence"
                    break
                request = provider_request(state, orders)
                request_hash = digest(request)
                command_hash = digest(provider_argv)
                if any(c["request_sha256"] == request_hash and c["command_sha256"] == command_hash for c in state["provider_calls"]):
                    state["stop_reason"] = "provider-no-progress"
                    break
                folder = workspace / "provider" / f"{len(state['provider_calls']):04d}"
                folder.mkdir(parents=True, exist_ok=False)
                write(folder / "request.json", request, exclusive=True)
                try:
                    log = _process(provider_argv, folder, encoded(request), min(remaining, 60), workspace,
                                   min(max_bytes, _size(workspace) + MAX_JSON), reserve)
                    response = read(log)
                    if not isinstance(response, dict) or set(response) != {"proposals"}:
                        raise ValueError("provider must return only {proposals:[...]}")
                    added = _add(state, response["proposals"])
                    error = None
                except (ValueError, OSError, RuntimeError, TimeoutError) as exc:
                    added, error = 0, str(exc)
                state["provider_calls"].append(dict(request_sha256=request_hash, command_sha256=command_hash,
                    artifacts_sha256={p.relative_to(workspace).as_posix(): sha(p) for p in folder.iterdir() if p.is_file()},
                    added=added, error=error))
                write(workspace / "state.json", state)
                if not added:
                    state["stop_reason"] = "provider-error" if error else "provider-no-progress"
                    break
                continue
            key = candidate["design_sha256"]
            validate(candidate["proposal"], state["baseline_sha256"])
            folder = workspace / "runs" / key
            if folder.exists():
                state["stop_reason"] = "interrupted-attempt-needs-review"
                break
            folder.mkdir(parents=True)
            write(folder / "proposal.json", candidate["proposal"], exclusive=True)
            try:
                argv = [sys.executable, str(ROOT / "tools/automation/twin-completion.py"),
                        "evaluate", "--proposal", str(folder / "proposal.json"), "--output", str(folder / "artifacts")]
                _process(argv, folder, None, remaining, workspace, max_bytes, reserve)
                result = read(folder / "artifacts/result.json")
            except (ValueError, OSError, RuntimeError, TimeoutError) as exc:
                result = dict(study_pass=False, error=str(exc), checks={}, **FLAGS)
            current(state)
            receipt = dict(design_sha256=key, kind=candidate["proposal"]["kind"],
                study_pass=result["study_pass"], result=result, toolchain=environment,
                artifacts_sha256={p.relative_to(workspace).as_posix(): sha(p) for p in sorted(folder.rglob("*")) if p.is_file()},
                scope="Research example only; zero railway specification acceptance credit", **FLAGS)
            state["receipts"].append(receipt)
            state["stop_reason"] = "step-budget"
            write(workspace / "state.json", state)
        write(workspace / "state.json", state)
    return status(workspace)


def verify(workspace, *, historical=False):
    workspace = Path(workspace)
    result = status(workspace, check_current=not historical)
    state = read(workspace / "state.json")
    if digest(state["source_sha256"]) != state["baseline_sha256"]:
        raise ValueError("baseline/source digest mismatch")
    seen = set()
    for candidate in state["proposals"]:
        key = validate(candidate["proposal"], state["baseline_sha256"])
        if key != candidate["design_sha256"] or key in seen:
            raise ValueError("changed/duplicate proposal")
        seen.add(key)
    for receipt in [*state["receipts"], *state["provider_calls"]]:
        if "design_sha256" in receipt and receipt["design_sha256"] not in seen:
            raise ValueError("unmapped result")
        for name, expected in receipt["artifacts_sha256"].items():
            path = (workspace / name).resolve()
            if not path.is_relative_to(workspace.resolve()) or sha(path) != expected:
                raise ValueError("changed execution artifact: " + name)
        if "design_sha256" in receipt:
            result_path = workspace / "runs" / receipt["design_sha256"] / "artifacts/result.json"
            if result_path.is_file() and read(result_path) != receipt["result"]:
                raise ValueError("receipt differs from actual adapter result")
            if receipt["study_pass"] is not receipt["result"]["study_pass"] or any(
                receipt.get(k) is not False or receipt["result"].get(k) is not False for k in FLAGS
            ):
                raise ValueError("receipt cannot assert independent or physical acceptance")
    if any(state.get(k) is not False for k in FLAGS):
        raise ValueError("controller cannot self-certify a physical twin")
    return dict(**result, integrity_verified=True, current_sources_required=not historical,
        assurance="Source/artifact integrity, not authenticated physical acceptance")
