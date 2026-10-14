"""Bounded local design jobs, durable attempts and source-qualified refinement."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import importlib.metadata
import json
import math
import os
from pathlib import Path
import resource
import shutil
import signal
import subprocess
import sys
import threading
import time
import fcntl

from . import adapters
from .contracts import (
    identity,
    problem,
    variables,
    fingerprint,
    comparable,
    checks_status,
    canonical,
    problem_fingerprint,
)
from .publication import digest
from .registry import ROOT, get, dependencies
from .store import Store, write_new

TERMINAL = {
    "completed",
    "failed",
    "cancelled",
    "timeout",
    "budget-exceeded",
    "outside-domain",
    "unavailable",
    "interrupted",
}


class BudgetExceeded(RuntimeError):
    pass


class Cancelled(RuntimeError):
    pass


def toolchain(adapter):
    result = dict(python=sys.version.split()[0])
    for name in ("numpy", "scipy", "pymoo", "openseespy", "ifcopenshell"):
        try:
            result[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            result[name] = None
    ccx = shutil.which("ccx")
    result["calculix_sha256"] = digest(Path(ccx)) if ccx else None
    result["adapter"] = adapter
    return result


def preflight(charter):
    adapter = charter["adapter"]
    tools = toolchain(adapter)
    missing = []
    for name in ("numpy", "scipy"):
        if not tools[name]:
            missing.append(name)
    if adapter in {"panel", "roof"} and not tools["calculix_sha256"]:
        missing.append("CalculiX")
    if adapter == "civil" and not tools["openseespy"]:
        missing.append("OpenSeesPy")
    return dict(
        available=not missing, missing=missing, toolchain=tools, physical_release=False
    )


def request(
    problem_id,
    scope,
    candidates=None,
    *,
    refine=False,
    shortlist=3,
    budget=None,
    seed=11,
    search=None,
):
    charter = get(problem_id)
    identity(scope)
    if scope["environment"] not in charter["applicability"]["environment"]:
        raise ValueError("problem does not apply to the selected environment")
    if budget:
        charter["budget"].update(budget)
        problem(charter)
    if type(seed) is not int or not 0 <= seed <= 2**32 - 1:
        raise ValueError("bounded integer random seed required")
    if type(shortlist) is not int or not 1 <= shortlist <= 16:
        raise ValueError("bounded diverse shortlist required")
    if candidates is None:
        candidates = [
            {
                k: (v["choices"][0] if v["kind"] == "choice" else v["bounds"][0])
                for k, v in charter["variables"].items()
            }
        ]
    if not isinstance(candidates, list) or not 1 <= len(candidates) <= 128:
        raise ValueError("bounded candidate list required")
    values = [variables(charter, c) for c in candidates]
    if len({fingerprint(v) for v in values}) != len(values):
        raise ValueError("duplicate candidates do not create free evaluations")
    if type(refine) is not bool:
        raise ValueError("refinement must be an explicit boolean")
    if search is not None:
        if not isinstance(search, dict) or set(search) != {"seeds", "evaluations"}:
            raise ValueError("bounded search seeds/proposal budget required")
        seeds = search["seeds"]
        count = search["evaluations"]
        if (
            not isinstance(seeds, list)
            or not 2 <= len(seeds) <= 8
            or len(set(seeds)) != len(seeds)
            or any(type(s) is not int or not 0 <= s <= 2**32 - 1 for s in seeds)
        ):
            raise ValueError("distinct bounded search seeds required")
        if type(count) is not int or not 4 <= count <= 128:
            raise ValueError("bounded search proposal budget required")
    return dict(
        schema="osr-design-request/1",
        problem=charter,
        identity=scope,
        candidates=values,
        refine=bool(refine),
        shortlist=shortlist,
        seed=seed,
        search=search,
        dependencies=dependencies(charter["adapter"]),
        toolchain=toolchain(charter["adapter"]),
    )


class Budget:
    def __init__(self, store, identifier, limits):
        self.store = store
        self.id = identifier
        self.limits = limits
        self.started = time.monotonic()
        self.spent = 0

    def charge(self, count, phase):
        if self.store.cancelled(self.id):
            raise Cancelled("operator cancelled the local experiment")
        if time.monotonic() - self.started > self.limits["wall_seconds"]:
            raise BudgetExceeded("wall-clock budget exhausted")
        if self.spent + count > self.limits["evaluations"]:
            raise BudgetExceeded(
                "evaluation budget exhausted; failed and completed attempts retained"
            )
        self.spent += count
        self.store.update(
            self.id, phase, min(95, 100 * self.spent / self.limits["evaluations"])
        )
        self.store.event(
            self.id,
            dict(
                kind="budget",
                phase=phase,
                evaluations=self.spent,
                limit=self.limits["evaluations"],
            ),
        )


def diverse_shortlist(rows, limit):
    eligible = [
        r
        for r in rows
        if not any(
            c["state"]
            in {"failed", "outside-domain", "unavailable", "budget-exceeded", "stale"}
            for c in r["checks"].values()
        )
    ]
    ordered = sorted(
        eligible,
        key=lambda r: (r["metrics"].get("defined_mass_kg", float("inf")), r["id"]),
    )
    chosen = []
    seen = set()
    # Preserve distinct supports/materials before selecting another design with
    # the same arrangement; low nominal mass is not the only shortlist signal.
    for row in ordered:
        signature = tuple(
            (k, str(v))
            for k, v in row["variables"].items()
            if k
            in {"support_span_m", "grade_density", "parallel_strings", "pier_height_m"}
        )
        if signature not in seen:
            chosen.append(row)
            seen.add(signature)
        if len(chosen) == limit:
            break
    for row in ordered:
        if len(chosen) == limit:
            break
        if row not in chosen:
            chosen.append(row)
    return chosen


def worker(store_root, identifier):
    store = Store(store_root)
    job = store.verify_request(identifier)
    req = job["request"]
    charter = req["problem"]
    problem(charter)
    identity(req["identity"])
    folder = store.begin(identifier, os.getpid())
    limits = charter["budget"]
    budget = Budget(store, identifier, limits)
    rows = []
    state = "completed"
    error = None
    resource.setrlimit(
        resource.RLIMIT_AS,
        (limits["memory_mib"] * 1024**2, limits["memory_mib"] * 1024**2),
    )
    cpu = max(1, math.ceil(limits["wall_seconds"]))
    resource.setrlimit(resource.RLIMIT_CPU, (cpu, cpu + 1))
    try:
        if req["dependencies"] != dependencies(charter["adapter"]) or req[
            "toolchain"
        ] != toolchain(charter["adapter"]):
            raise ValueError(
                "stale source/material/solver environment before execution"
            )
        check = preflight(charter)
        write_new(folder / "preflight.json", check)
        if not check["available"]:
            raise adapters.Unavailable(
                "missing local tools: " + ", ".join(check["missing"])
            )
        budget.charge(0, "preflight")
        if charter["adapter"] in {"panel", "roof"} and req["refine"]:
            from engineering.panel_response.verification import native

            budget.charge(1, "independent-formulation-benchmark")
            benchmark = native(folder / "native-benchmark")
            if not benchmark["numerical_screen_passed"]:
                raise RuntimeError("independent plate formulation benchmark failed")

        def evaluate(values, charge):
            budget.charge(0, "compile")
            try:
                row = adapters.compile_candidate(charter, req["identity"], values)
                row = adapters.screen(charter, row, charge, folder)
            except (ValueError, adapters.OutsideDomain) as failure:
                row = dict(
                    schema="osr-design-candidate/1",
                    id="candidate-" + fingerprint(values),
                    variables=values,
                    identity=req["identity"],
                    problem_sha256=problem_fingerprint(charter),
                    definition_sha256=None,
                    metrics={},
                    checks=adapters.checks(charter),
                    evidence_state="outside-domain",
                    error=str(failure),
                    physical_release=False,
                    independently_accepted=False,
                )
                for item in row["checks"].values():
                    item.update(
                        state="not-run",
                        basis="candidate compilation outside the declared physical model domain",
                    )
                row["checks"]["geometry"].update(
                    state="outside-domain", basis=str(failure)
                )
            return row

        search_result = None
        if req.get("search"):
            from .optimization import paired

            def oracle(value, seed, arm, cached):
                budget.charge(1, "search-" + arm + "-" + str(seed))
                if cached:
                    return None
                return evaluate(value, lambda count, phase: budget.charge(0, phase))

            search_result = paired(
                charter,
                oracle,
                seeds=req["search"]["seeds"],
                evaluations=req["search"]["evaluations"],
            )
            rows = search_result["candidates"]
            write_new(folder / "search.json", search_result)
        else:
            for values in req["candidates"]:
                rows.append(evaluate(values, budget.charge))
        shortlist = diverse_shortlist(rows, req["shortlist"]) if req["refine"] else []
        # An explicitly selected single candidate may be refined diagnostically
        # even when a screening constraint fails. It stays ineligible for ranking.
        if req["refine"] and len(rows) == 1 and rows[0].get("definition"):
            shortlist = rows
        for row in shortlist:
            try:
                adapters.refine(charter, row, budget.charge, folder / row["id"])
            except adapters.OutsideDomain as failure:
                row["evidence_state"] = "outside-domain"
                row["error"] = str(failure)
                for name in ("mesh_refinement", "refinement"):
                    if name in row["checks"]:
                        adapters.set_check(row, name, "outside-domain", str(failure))
            row["refinement_requested"] = True
        if dependencies(charter["adapter"]) != req["dependencies"]:
            raise ValueError("source changed during execution; evidence is stale")
        screening = sorted(
            (r for r in rows if "defined_mass_kg" in r["metrics"]),
            key=lambda r: r["metrics"]["defined_mass_kg"],
        )
        detailed = sorted(
            (r for r in rows if "detailed_deflection_m" in r["metrics"]),
            key=lambda r: r["metrics"]["detailed_deflection_m"],
        )
        summary = dict(
            schema="osr-design-comparison/1",
            identity=req["identity"],
            problem_sha256=problem_fingerprint(charter),
            candidates=rows,
            screen_mass_ranking=[r["id"] for r in screening],
            screen_deflection_ranking=[
                r["id"]
                for r in sorted(
                    (r for r in rows if "screen_deflection_m" in r["metrics"]),
                    key=lambda r: r["metrics"]["screen_deflection_m"],
                )
            ],
            detailed_deflection_ranking=[r["id"] for r in detailed],
            ranking_axes_differ=True,
            conditional_shortlist=[r["id"] for r in shortlist],
            verified_frontier=[],
            unknown_objectives=[
                "complete installed/lifecycle cost",
                "production/disruption/imported scope",
                "physical material/connection/measurement evidence",
            ],
            evaluations_spent=budget.spent,
            cache_hits=search_result["cache_hits"] if search_result else 0,
            optimisation_trials=search_result["trials"] if search_result else [],
            elapsed_seconds=time.monotonic() - budget.started,
            physical_release=False,
            independently_accepted=False,
            global_optimum_claimed=False,
        )
        write_new(folder / "comparison.json", summary)
        write_new(folder / "review-package.json", review_package(req, summary))
    except Cancelled as failure:
        state, error = "cancelled", str(failure)
    except BudgetExceeded as failure:
        state, error = "budget-exceeded", str(failure)
    except adapters.Unavailable as failure:
        state, error = "unavailable", str(failure)
    except adapters.OutsideDomain as failure:
        state, error = "outside-domain", str(failure)
    except MemoryError:
        state, error = "budget-exceeded", "memory budget exhausted"
    except Exception as failure:
        state, error = "failed", type(failure).__name__ + ": " + str(failure)
    if error:
        write_new(
            folder / "failure.json",
            dict(
                state=state,
                error=error,
                completed_candidates=rows,
                evaluations_spent=budget.spent,
                physical_release=False,
            ),
        )
    size = sum(p.stat().st_size for p in folder.rglob("*") if p.is_file())
    if size > limits["artifact_mib"] * 1024**2:
        state, error = (
            "budget-exceeded",
            "artifact budget exceeded; partial attempt retained",
        )
    manifest = dict(
        schema="osr-design-attempt/1",
        job=identifier,
        request_sha256=fingerprint(req),
        state=state,
        error=error,
        dependency_hashes=req["dependencies"],
        toolchain=req["toolchain"],
        artifacts={
            p.relative_to(folder).as_posix(): digest(p)
            for p in sorted(folder.rglob("*"))
            if p.is_file()
        },
        numerical_only=True,
        runner="local-unattested",
        physical_release=False,
        independently_accepted=False,
    )
    write_new(folder / "manifest.json", manifest)
    store.finish(identifier, state, error, manifest)
    return 0 if state == "completed" else 1


def review_package(req, summary):
    candidates = summary["candidates"]
    return dict(
        schema="osr-design-review-package/1",
        identity=req["identity"],
        problem=req["problem"],
        candidate_ids=[r["id"] for r in candidates],
        source_dependencies=req["dependencies"],
        drawings_status="unissued; native CAD/BIM exports and authored drawings retain separate evidence",
        bill=[
            dict(
                candidate=r["id"],
                parts=r.get("definition", {}).get("contract", {}).get("parts", []),
                incomplete_installed_inventory=True,
            )
            for r in candidates
        ],
        rfq_required=[
            "supplier grade/batch",
            "complete joint/retention/seal quantities",
            "local supply and manufacturing rights",
            "installed tooling/QA/rejects/transport/replacement scope",
            "place/date/currency/binding quotation",
        ],
        test_matrix=req["problem"]["applicability"]["mandatory_checks"],
        accountable_roles=dict(
            design_authority=None, test_executor=None, independent_reviewer=None
        ),
        erp_handoff=dict(
            state="draft-only",
            native_record_created=False,
            baseline_overwrite_permitted=False,
        ),
        physical_release=False,
        independently_accepted=False,
    )


class Manager:
    def __init__(self, root, *, recover_pending=True):
        self.store = Store(root)
        self.store.recover()
        self._slots = threading.BoundedSemaphore(2)
        if recover_pending:
            for identifier in self.store.pending():
                threading.Thread(
                    target=self._launch, args=(identifier,), daemon=True
                ).start()

    def start(self, req):
        job = self.store.create(req)
        threading.Thread(target=self._launch, args=(job["id"],), daemon=True).start()
        return job

    def resume(self, identifier):
        job = self.store.get(identifier)
        adapter = job["request"]["problem"]["adapter"]
        self.store.resume(identifier, dependencies(adapter), toolchain(adapter))
        threading.Thread(target=self._launch, args=(identifier,), daemon=True).start()
        return self.store.get(identifier)

    def _launch(self, identifier):
        if not self.store.claim_dispatch(identifier):
            return
        with self._slots:
            locks = self.store.root / "worker-slots"
            locks.mkdir(exist_ok=True)
            lease = None
            while lease is None:
                if self.store.cancelled(identifier):
                    self.store.finish(
                        identifier,
                        "cancelled",
                        "cancelled while queued; request and events retained",
                    )
                    return
                for slot in range(2):
                    candidate = (locks / str(slot)).open("a+b")
                    try:
                        fcntl.flock(candidate.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                        lease = candidate
                        break
                    except BlockingIOError:
                        candidate.close()
                if lease is None:
                    time.sleep(0.2)
            try:
                self._execute(identifier, lease.fileno())
            except (OSError, ValueError, RuntimeError) as error:
                if self.store.get(identifier)["status"] not in TERMINAL:
                    self.store.finish(
                        identifier, "failed", "local dispatcher failed: " + str(error)
                    )
            finally:
                lease.close()

    def _execute(self, identifier, lease_fd):
        req = self.store.get(identifier)["request"]
        limit = req["problem"]["budget"]["wall_seconds"]
        logs = self.store.root / "runs" / identifier / "logs"
        logs.mkdir(exist_ok=True)
        attempt = self.store.get(identifier)["active_attempt"] + 1
        started = time.monotonic()
        env = {
            **os.environ,
            "OPENBLAS_NUM_THREADS": "1",
            "OMP_NUM_THREADS": "1",
            "MKL_NUM_THREADS": "1",
            "PYTHONPATH": os.pathsep.join(
                [str(ROOT), str(ROOT / "design/component-catalogue/src")]
            ),
        }
        for key in list(env):
            if key.startswith("GITHUB_"):
                env.pop(key)
        with (logs / f"attempt-{attempt:04d}.log").open("wb") as log:
            proc = subprocess.Popen(
                [
                    sys.executable,
                    str(ROOT / "tools/automation/design-engine.py"),
                    "_worker",
                    "--store",
                    str(self.store.root),
                    "--job",
                    identifier,
                ],
                cwd=ROOT,
                env=env,
                stdout=log,
                stderr=subprocess.STDOUT,
                start_new_session=True,
                pass_fds=(lease_fd,),
            )
            reason = None
            while proc.poll() is None:
                if self.store.cancelled(identifier):
                    reason = "cancelled"
                    break
                if time.monotonic() - started > limit:
                    reason = "timeout"
                    break
                time.sleep(0.2)
            if reason:
                try:
                    os.killpg(proc.pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    os.killpg(proc.pid, signal.SIGKILL)
                    proc.wait()
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            current = self.store.get(identifier)
            if current["status"] not in TERMINAL:
                if reason is None and proc.returncode == -signal.SIGXCPU:
                    reason = "budget-exceeded"
                self.store.finish(
                    identifier,
                    reason or "failed",
                    "worker terminated before sealing; partial artifacts and logs retained",
                )


def comparison(store, identifier):
    job = store.verify_request(identifier)
    if job["status"] != "completed":
        raise ValueError(
            "only completed execution has a sealed comparison; failed attempts remain available"
        )
    number = job["active_attempt"]
    store.verify_attempt(identifier, number)
    return json.loads(
        (
            store.root
            / "runs"
            / identifier
            / f"attempt-{number:04d}"
            / "comparison.json"
        ).read_text()
    )


def compare(store, identifiers):
    reports = [comparison(store, i) for i in identifiers]
    for report in reports[1:]:
        comparable(reports[0], report)
    return dict(
        schema="osr-design-run-comparison/1",
        runs=identifiers,
        reports=reports,
        physical_release=False,
    )
