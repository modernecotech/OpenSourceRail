"""Feedback-directed design iterations, bounded independently of acceptance.

Role workers are deterministic engineering adapters. The cooperating agents that
develop them are distinct from this reproducible numerical execution protocol.
"""

from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
from html import escape
import json
import math
from pathlib import Path

from . import campaign, coverage, evidence_store

FLAGS = (
    "design_complete",
    "engineering_design_complete",
    "manufacturing_release",
    "physical_release",
)
SCHEMA = "osr-generative-design-iteration/1"


def fingerprint(value):
    return sha256(evidence_store.compact(value)).hexdigest()


def validate_candidate(candidate):
    """Reject incomplete evaluations and release claims before selecting anything."""
    if not isinstance(candidate.get("id"), str) or not candidate["id"]:
        raise ValueError("candidate identity required")
    if not isinstance(candidate.get("variables"), dict):
        raise ValueError("explicit candidate variables required")
    checks = candidate.get("checks")
    if not isinstance(checks, list) or not checks:
        raise ValueError("actual evaluated checks required")
    ids = []
    for check in checks:
        ids.append(check["id"])
        if check.get("state") not in {"pass", "fail", "unknown"}:
            raise ValueError("check must retain pass/fail/unknown state")
        for name in ("value", "limit"):
            value = check.get(name)
            if isinstance(value, float) and not math.isfinite(value):
                raise ValueError("finite check quantities or explicit null required")
    if len(ids) != len(set(ids)):
        raise ValueError("unique candidate check identities required")
    if any(candidate.get(flag, False) is not False for flag in FLAGS):
        raise ValueError("computational candidate cannot claim design release")
    if not any(c["state"] == "unknown" for c in checks):
        raise ValueError(
            "unaccepted configuration and physical qualification remain unknown"
        )
    return candidate


def numerical_status(candidate):
    checks = candidate["checks"]
    if any(c["state"] == "fail" for c in checks):
        return "known-check-failure"
    if any(c["state"] == "pass" for c in checks):
        return "known-checks-pass-with-open-gates"
    return "no-evaluated-numerical-check"


def critique(candidate, *, producer, reviewer="independent-critic"):
    """Independent role challenge; computational review is never design approval."""
    if producer == reviewer:
        raise ValueError("producer cannot critique their own candidate")
    validate_candidate(candidate)
    failures = [c["id"] for c in candidate["checks"] if c["state"] == "fail"]
    unknowns = [c["id"] for c in candidate["checks"] if c["state"] == "unknown"]
    missing = [
        field
        for field in ("geometry", "materials", "connections", "manufacturing")
        if not candidate.get(field)
    ]
    return dict(
        schema="osr-design-candidate-critique/1",
        candidate_id=candidate["id"],
        producer_role=producer,
        reviewer_role=reviewer,
        review_kind="automated-contract-and-open-check-challenge",
        independent_engineering_review_performed=False,
        failed_check_ids=failures,
        unknown_check_ids=unknowns,
        missing_definition_fields=missing,
        disposition=(
            "reject-known-failures"
            if failures
            else (
                "hold-missing-definition"
                if missing
                else "provisional-research-only-awaiting-qualified-review"
            )
        ),
        engineering_design_complete=False,
        manufacturing_release=False,
        physical_release=False,
    )


def iterate(
    adapter,
    context,
    *,
    budget=64,
    previous=None,
    producer="discipline-designer",
    checkpoint=None,
):
    """Evaluate fresh proposals, retaining parents, failures and resume frontier."""
    if type(budget) is not int or not 1 <= budget <= 512:
        raise ValueError("finite evaluation budget in 1..512 required")
    context_hash = fingerprint(context)
    if previous is not None and previous["context_sha256"] != context_hash:
        raise ValueError("changed context requires a fresh trace and descendant review")
    candidates = deepcopy(previous["candidates"]) if previous else []
    if len(candidates) > budget:
        raise ValueError("resume budget cannot be smaller than retained evaluations")
    for candidate in candidates:
        validate_candidate(candidate)
    visited = {fingerprint(c["variables"]) for c in candidates}
    if len(visited) != len(candidates):
        raise ValueError("duplicate retained candidate genotype")
    frontier = (
        deepcopy(previous["frontier"])
        if previous
        else [
            dict(
                variables=adapter.seed(context),
                parent=None,
                generation=0,
                reasons=["seed"],
            )
        ]
    )
    queued = {fingerprint(row["variables"]) for row in frontier}
    known_ids = {c["id"] for c in candidates}
    adverse_counts = {
        c["id"]: sum(x["state"] == "fail" for x in c["checks"]) for c in candidates
    }
    selected = next(
        (
            c
            for c in candidates
            if numerical_status(c) == "known-checks-pass-with-open-gates"
        ),
        None,
    )
    evaluations = 0
    while frontier and len(candidates) < budget and selected is None:
        # Explore repairs of the least-adverse evaluated parent first. Unknown
        # cost/material/qualification never improves this numerical priority.
        frontier.sort(
            key=lambda p: (adverse_counts.get(p["parent"], 0), p["generation"])
        )
        proposal = frontier.pop(0)
        genotype = fingerprint(proposal["variables"])
        queued.discard(genotype)
        if genotype in visited:
            continue
        if proposal["parent"] is not None and proposal["parent"] not in known_ids:
            raise ValueError("proposal parent must be retained in the same trace")
        try:
            candidate = deepcopy(adapter.assess(proposal["variables"], context))
        except Exception as error:
            if checkpoint:
                checkpoint(
                    dict(
                        id="evaluation-failure-" + genotype,
                        variables=proposal["variables"],
                        error=f"{type(error).__name__}: {error}",
                        parent_candidate_id=proposal["parent"],
                        physical_release=False,
                    )
                )
            raise
        validate_candidate(candidate)
        if (
            candidate["variables"] != proposal["variables"]
            or candidate["id"] in known_ids
        ):
            raise ValueError("adapter altered proposal or reused a candidate identity")
        candidate["iteration_provenance"] = dict(
            generation=proposal["generation"],
            parent_candidate_ids=[proposal["parent"]] if proposal["parent"] else [],
            repair_reasons=proposal["reasons"],
            producer_role=producer,
            context_sha256=context_hash,
        )
        candidates.append(candidate)
        if checkpoint:
            checkpoint(candidate)
        visited.add(genotype)
        known_ids.add(candidate["id"])
        adverse_counts[candidate["id"]] = sum(
            c["state"] == "fail" for c in candidate["checks"]
        )
        evaluations += 1
        if numerical_status(candidate) == "known-checks-pass-with-open-gates":
            selected = candidate
            break
        reasons = [c["id"] for c in candidate["checks"] if c["state"] == "fail"]
        for variables in adapter.propose(candidate, context):
            key = fingerprint(variables)
            if key in visited or key in queued:
                continue
            if not reasons or variables == candidate["variables"]:
                raise ValueError(
                    "new variant requires actual adverse feedback and a change"
                )
            frontier.append(
                dict(
                    variables=deepcopy(variables),
                    parent=candidate["id"],
                    generation=proposal["generation"] + 1,
                    reasons=reasons,
                )
            )
            queued.add(key)
    status = (
        "provisional-solution-held-for-qualification"
        if selected
        else "budget-exhausted" if frontier else "no-solution-in-declared-repair-domain"
    )
    best = selected or min(
        candidates,
        key=lambda c: (sum(x["state"] == "fail" for x in c["checks"]), c["id"]),
        default=None,
    )
    return dict(
        schema="osr-design-feedback-trace/1",
        proposal_policy="fewest-known-adverse-parent-checks-then-generation",
        context=deepcopy(context),
        context_sha256=context_hash,
        candidates=candidates,
        frontier=frontier,
        evaluation_budget=budget,
        new_evaluations=evaluations,
        selected_candidate_id=selected["id"] if selected else None,
        diagnostic_candidate_id=best["id"] if best else None,
        termination=status,
        critique=critique(best, producer=producer) if best else None,
        engineering_design_complete=False,
        manufacturing_release=False,
        physical_release=False,
    )


def _read(path):
    return evidence_store.read_json(path)


def _checkpoint(output, lane, context):
    folder = output / "attempts" / lane / fingerprint(context)[:16]

    def capture(candidate):
        path = folder / (fingerprint(candidate["id"])[:20] + ".json")
        if path.exists() and _read(path) != candidate:
            raise ValueError("retained attempt bytes cannot be replaced")
        if not path.exists():
            campaign.write(path, candidate)

    return capture


def _files(folder):
    result = {}
    for path in sorted(folder.rglob("*")):
        if path.is_symlink():
            raise ValueError("design artifacts cannot be symbolic links")
        if path.is_file() and path != folder / "receipt.json":
            result[path.relative_to(folder).as_posix()] = coverage.sha(path)
    return result


def sources():
    from . import design_scenario

    result = campaign.sources(campaign.scope())
    result.update(design_scenario.plan()["source_hashes"])
    result["tools/automation/design-iteration.py"] = coverage.sha(
        coverage.ROOT / "tools/automation/design-iteration.py"
    )
    return dict(sorted(result.items()))


def _adapters():
    from . import civil_detail, mechanical_detail

    return {"mechanical": mechanical_detail, "civil": civil_detail}


def _representative(trace):
    return next(
        c for c in trace["candidates"] if c["id"] == trace["diagnostic_candidate_id"]
    )


def _architecture(context):
    value = context.get(
        "architecture_id",
        context.get("architecture", context.get("configuration_id", "")),
    )
    if value not in {"LM3", "metro-6car-planning"}:
        raise ValueError("explicit recognised architecture required")
    return value


def _civil_contexts(adapter, mechanical_traces):
    """Gross addition is an explicit sensitivity; removed frame mass is unknown."""
    by_architecture = {_architecture(t["context"]): t for t in mechanical_traces}
    if len(by_architecture) != len(mechanical_traces) or set(by_architecture) != {
        "LM3",
        "metro-6car-planning",
    }:
        raise ValueError("one mechanical context per declared architecture required")
    contexts, transfers = [], []
    for original in adapter.contexts():
        architecture = _architecture(original)
        mechanical = by_architecture[architecture]
        candidate = _representative(mechanical)
        mass = candidate["objectives"]["mass_kg"]
        if type(mass) not in (int, float) or not math.isfinite(mass) or mass <= 0:
            raise ValueError(
                "known positive detailed assembly mass required for coupling"
            )
        cars = 3 if architecture == "LM3" else 6
        gross = cars * mass
        context = adapter.coupled_context(original, gross)
        contexts.append(context)
        transfers.append(
            dict(
                mechanical_candidate_id=candidate["id"],
                architecture_id=architecture,
                civil_context_sha256=fingerprint(context),
                modeled_steel_mass_per_car_kg=mass,
                complete_assembly_mass_per_car_kg=None,
                unmodeled_accessory_mass_kg=None,
                cars=cars,
                gross_added_train_mass_kg=gross,
                removed_existing_frame_mass_kg=None,
                net_mass_change_kg=None,
                assumption="Known modelled steel added without credit for removed frame; missing fastener/weld/paint mass remains unknown. Proportional axle-force sensitivity retains source CG distribution. No total-mass bound, mass saving or accepted new axle allocation.",
                source_candidate_has_known_failures=numerical_status(candidate)
                == "known-check-failure",
                adopted=False,
                engineering_design_complete=False,
                manufacturing_release=False,
                physical_release=False,
            )
        )
    return contexts, transfers


def _native(output, lane, trace, adapter):
    from engineering.factory_examples import native

    candidate = _representative(trace)
    folder = output / "models" / lane / trace["context_sha256"][:16]
    folder.mkdir(parents=True)
    model = adapter.model_definition(candidate)
    campaign.write(folder / "model.json", model)
    record = dict(
        case_id=trace["context"]["id"],
        context_sha256=trace["context_sha256"],
        lane=lane,
        candidate_id=candidate["id"],
        model=(folder / "model.json").relative_to(output).as_posix(),
        receipt=(folder / "native-cad.json").relative_to(output).as_posix(),
        role=(
            "provisional-shortlist"
            if trace["selected_candidate_id"]
            else "failed-design-diagnostic"
        ),
        physical_release=False,
    )
    try:
        proof = native.generate(folder / "model.json", folder, coverage.ROOT)
        record.update(status="passed", part_count=proof["part_count"])
    except Exception as error:
        record.update(status="failed", error=f"{type(error).__name__}: {error}")
        campaign.write(folder / "failure.json", record)
    # Retain native diagnostics alongside the result, including failed attempts.
    import shutil

    work = coverage.ROOT / "build/factory-examples-native" / folder.name
    for name in ("generate.py", "freecad.log", "completed"):
        source = work / name
        if source.is_file():
            shutil.copyfile(source, folder / name)
    return record


def run(output, *, budget=256, native=False, baseline=True, resume=None):
    from . import design_scenario, queue_campaign

    output = Path(output).resolve()
    if output.exists():
        raise ValueError("a fresh output directory preserves prior design attempts")
    if type(budget) is not int or not 1 <= budget <= 512:
        raise ValueError("finite budget in 1..512 required")
    prior = None
    if resume is not None:
        verify(resume, current=True)
        prior = _read(Path(resume) / "report.json")
    plan = design_scenario.plan()
    source_hashes = sources()
    output.mkdir(parents=True)
    campaign.write(
        output / "request.json",
        dict(
            schema=SCHEMA,
            source_sha256=source_hashes,
            evaluation_budget_per_context=budget,
            native_requested=bool(native),
            baseline_requested=bool(baseline),
            numerical_environment=campaign.environment(False),
            parent_receipt_sha256=(
                sha256(
                    evidence_store.read_bytes(Path(resume) / "receipt.json")
                ).hexdigest()
                if resume
                else None
            ),
            engineering_design_complete=False,
            manufacturing_release=False,
            physical_release=False,
        ),
    )
    adapters = _adapters()
    previous = (
        {(t["lane"], t["context_sha256"]): t for t in prior["traces"]} if prior else {}
    )
    traces = []
    for context in adapters["mechanical"].contexts():
        trace = iterate(
            adapters["mechanical"],
            context,
            budget=budget,
            previous=previous.get(("mechanical", fingerprint(context))),
            producer="mechanical-designer",
            checkpoint=_checkpoint(output, "mechanical", context),
        )
        trace["lane"] = "mechanical"
        traces.append(trace)
        print(
            f"mechanical {context['id']}: {len(trace['candidates'])} evaluations; {trace['termination']}",
            flush=True,
        )
    contexts, transfers = _civil_contexts(adapters["civil"], traces)
    for context in contexts:
        trace = iterate(
            adapters["civil"],
            context,
            budget=budget,
            previous=previous.get(("civil", fingerprint(context))),
            producer="civil-designer",
            checkpoint=_checkpoint(output, "civil", context),
        )
        trace["lane"] = "civil"
        traces.append(trace)
        print(
            f"civil {context['id']}: {len(trace['candidates'])} evaluations; {trace['termination']}",
            flush=True,
        )
    package_ids = {p["id"] for p in plan["work_packages"]}
    exchanges = []
    for trace in traces:
        translated = {}
        for raw in trace["candidates"]:
            _checkpoint(output, trace["lane"], trace["context"])(raw)
            provenance = raw["iteration_provenance"]
            parents = [translated[p] for p in provenance["parent_candidate_ids"]]
            exchange = design_scenario.exchange_candidate(
                raw,
                context=trace["context"],
                iteration=provenance["generation"],
                parent_candidate_ids=parents,
                source_hashes=source_hashes,
                producer_agent=provenance["producer_role"],
                package_ids=package_ids,
            )
            translated[raw["id"]] = exchange["id"]
            exchanges.append(exchange)
    native_records = (
        [_native(output, t["lane"], t, adapters[t["lane"]]) for t in traces]
        if native
        else []
    )
    baseline_record = None
    if baseline:
        baseline_record = queue_campaign.run(
            output / "preliminary-packages", native=False
        )
    packages = []
    for package in plan["work_packages"]:
        responses = [c for c in exchanges if package["id"] in c["work_package_ids"]]
        packages.append(
            dict(
                id=package["id"],
                title=package["title"],
                owner_role=package["owner_role"],
                component_ids=package["component_ids"],
                dependencies=package["dependencies"],
                actual_detail_candidate_ids=[c["id"] for c in responses],
                proposed_detail_component_ids=sorted(
                    {i for c in responses for i in c["component_ids"]}
                ),
                status=(
                    "provisional-detail-investigated"
                    if responses
                    else "awaiting-qualified-detail-adapter-and-inputs"
                ),
                next_action=package["next_action"],
                required_gates=package["required_gates"],
                production_artifact_ids=[
                    r["artifact_id"] for r in package["production_artifact_requests"]
                ],
                inspection_characteristic_ids=[
                    r["id"] for r in package["inspection_characteristics"]
                ],
                design_complete=False,
                manufacturing_release=False,
                physical_release=False,
            )
        )
    report = dict(
        schema=SCHEMA,
        scenario=plan,
        traces=traces,
        exchanges=exchanges,
        mechanical_to_civil_transfers=transfers,
        packages=packages,
        native_geometry=native_records,
        baseline_execution=baseline_record,
        counts=dict(
            packages=len(packages),
            detail_contexts=len(traces),
            evaluated_variations=sum(len(t["candidates"]) for t in traces),
            new_evaluations=sum(t["new_evaluations"] for t in traces),
            provisional_local_solutions=sum(
                t["selected_candidate_id"] is not None for t in traces
            ),
            detailed_packages=sum(
                bool(p["actual_detail_candidate_ids"]) for p in packages
            ),
            completed_packages=0,
        ),
        interpretation="Role workers execute engineering code, not simulated LLM conversations. Research check convergence is separate from complete component design and physical production acceptance.",
        engineering_design_complete=False,
        manufacturing_release=False,
        physical_release=False,
    )
    campaign.write(output / "report.json", report)
    (output / "index.html").write_text(render(report))
    campaign.write(
        output / "receipt.json",
        dict(
            schema=SCHEMA,
            source_sha256=source_hashes,
            files_sha256=_files(output),
            native_requested=bool(native),
            baseline_requested=bool(baseline),
            engineering_design_complete=False,
            manufacturing_release=False,
            physical_release=False,
        ),
    )
    return verify(output, require_native=native)


def verify(output, *, current=True, require_native=False):
    from . import design_scenario, native_acceptance, queue_campaign

    output = Path(output).resolve()
    if evidence_store.is_projection(output):
        with evidence_store.materialized(output) as original:
            return verify(original, current=current, require_native=require_native)
    receipt = _read(output / "receipt.json")
    if receipt.get("schema") != SCHEMA or receipt.get("files_sha256") != _files(output):
        raise ValueError("design iteration receipt/artifact membership differs")
    if current and receipt["source_sha256"] != sources():
        raise ValueError(
            "design iteration sources changed; preserve history and rerun affected designs"
        )
    report = _read(output / "report.json")
    request = _read(output / "request.json")
    for item in (receipt, request, report):
        if any(item.get(k, False) is not False for k in FLAGS):
            raise ValueError(
                "design scenario cannot issue engineering or manufacturing release"
            )
    if receipt["source_sha256"] != request["source_sha256"]:
        raise ValueError("request sources differ")
    if any(
        receipt.get(k) != request.get(k)
        for k in ("native_requested", "baseline_requested")
    ):
        raise ValueError("execution request membership differs")
    plan = design_scenario.plan() if current else report["scenario"]
    if report["scenario"] != plan or {p["id"] for p in report["packages"]} != {
        p["id"] for p in plan["work_packages"]
    }:
        raise ValueError("exact audited component/package scope required")
    calculated = dict(
        packages=len(report["packages"]),
        detail_contexts=len(report["traces"]),
        evaluated_variations=sum(len(t["candidates"]) for t in report["traces"]),
        new_evaluations=sum(t["new_evaluations"] for t in report["traces"]),
        provisional_local_solutions=sum(
            t["selected_candidate_id"] is not None for t in report["traces"]
        ),
        detailed_packages=sum(
            bool(p["actual_detail_candidate_ids"]) for p in report["packages"]
        ),
        completed_packages=0,
    )
    if report["counts"] != calculated:
        raise ValueError("design iteration counts differ from retained records")
    for package in report["packages"]:
        if any(package.get(k, False) is not False for k in FLAGS):
            raise ValueError("partial detailed work cannot close a package")
    if not current:
        if require_native:
            raise ValueError(
                "fresh native acceptance requires current-source verification"
            )
        # A historical seal preserves past bytes. Current evaluators are never
        # substituted for a previous version to assert numerical applicability.
        return dict(
            integrity_verified=True,
            current_sources_checked=False,
            numerical_detail_calculations_recomputed=False,
            **calculated,
            native_geometry_passed=sum(
                r["status"] == "passed" for r in report["native_geometry"]
            ),
            engineering_design_complete=False,
            manufacturing_release=False,
            physical_release=False,
        )
    adapters = _adapters()
    mechanical = [t for t in report["traces"] if t["lane"] == "mechanical"]
    expected_contexts = {"mechanical": adapters["mechanical"].contexts()}
    expected_contexts["civil"], transfers = _civil_contexts(
        adapters["civil"], mechanical
    )
    if report["mechanical_to_civil_transfers"] != transfers:
        raise ValueError("mechanical mass to civil load transfer differs")
    expected = {
        (lane, fingerprint(c))
        for lane, contexts in expected_contexts.items()
        for c in contexts
    }
    actual = [(t["lane"], t["context_sha256"]) for t in report["traces"]]
    if len(actual) != len(set(actual)) or set(actual) != expected:
        raise ValueError("required detail context membership differs")
    expected_exchanges = []
    package_ids = {p["id"] for p in plan["work_packages"]}
    for trace in report["traces"]:
        context = trace["context"]
        if (
            fingerprint(context) != trace["context_sha256"]
            or context not in expected_contexts[trace["lane"]]
        ):
            raise ValueError("detail context differs")
        replayed = iterate(
            adapters[trace["lane"]],
            context,
            budget=trace["evaluation_budget"],
            producer=trace["lane"] + "-designer",
        )
        retained_trace = {
            k: v for k, v in trace.items() if k not in {"lane", "new_evaluations"}
        }
        replayed.pop("new_evaluations")
        if retained_trace != replayed or not 0 <= trace["new_evaluations"] <= len(
            trace["candidates"]
        ):
            raise ValueError(
                "feedback lineage/frontier/selection differs from reproducible iteration"
            )
        translated = {}
        for raw in trace["candidates"]:
            validate_candidate(raw)
            attempt = (
                output
                / "attempts"
                / trace["lane"]
                / trace["context_sha256"][:16]
                / (fingerprint(raw["id"])[:20] + ".json")
            )
            if _read(attempt) != raw:
                raise ValueError(
                    "retained individual attempt differs from campaign trace"
                )
            provenance = raw["iteration_provenance"]
            exchange = design_scenario.exchange_candidate(
                raw,
                context=context,
                iteration=provenance["generation"],
                parent_candidate_ids=[
                    translated[p] for p in provenance["parent_candidate_ids"]
                ],
                source_hashes=receipt["source_sha256"],
                producer_agent=provenance["producer_role"],
                package_ids=package_ids,
            )
            translated[raw["id"]] = exchange["id"]
            expected_exchanges.append(exchange)
    if report["exchanges"] != expected_exchanges:
        raise ValueError(
            "candidate exchange coverage/evidence differs from actual adapter responses"
        )
    for package in report["packages"]:
        original = next(p for p in plan["work_packages"] if p["id"] == package["id"])
        responses = [
            c for c in expected_exchanges if package["id"] in c["work_package_ids"]
        ]
        if (
            package["actual_detail_candidate_ids"] != [c["id"] for c in responses]
            or package["proposed_detail_component_ids"]
            != sorted({i for c in responses for i in c["component_ids"]})
            or any(
                package[k] != original[k]
                for k in (
                    "required_gates",
                    "dependencies",
                    "component_ids",
                    "next_action",
                )
            )
            or package["production_artifact_ids"]
            != [r["artifact_id"] for r in original["production_artifact_requests"]]
            or package["inspection_characteristic_ids"]
            != [r["id"] for r in original["inspection_characteristics"]]
        ):
            raise ValueError("package coverage and required gates differ")
    records = report["native_geometry"]
    if require_native or receipt.get("native_requested"):
        membership = [(r["lane"], r["context_sha256"]) for r in records]
        if len(membership) != len(set(membership)) or set(membership) != expected:
            raise ValueError(
                "every required detailed assembly needs fresh native proof"
            )
        for record in records:
            trace = next(
                t
                for t in report["traces"]
                if (t["lane"], t["context_sha256"])
                == (record["lane"], record["context_sha256"])
            )
            candidate = _representative(trace)
            native_acceptance.validate_model(
                output,
                record,
                candidate["id"],
                adapters[trace["lane"]].model_definition(candidate),
            )
    if receipt.get("baseline_requested"):
        queue_campaign.verify(output / "preliminary-packages", current=current)
    return dict(
        integrity_verified=True,
        current_sources_checked=current,
        numerical_detail_calculations_recomputed=True,
        **report["counts"],
        native_geometry_passed=sum(r["status"] == "passed" for r in records),
        engineering_design_complete=False,
        manufacturing_release=False,
        physical_release=False,
    )


def publish(output, destination):
    output, destination = Path(output).resolve(), Path(destination).resolve()
    verify(output)
    if destination.exists() or not destination.is_relative_to(
        coverage.ROOT / "docs/design-engine"
    ):
        raise ValueError("fresh design review publication directory required")
    files = {name: output / name for name in _files(output)}
    files["receipt.json"] = output / "receipt.json"
    evidence_store.publish_files(files, destination, original_seal="receipt.json")
    return verify(destination)


def render(report):
    """Small human review; full immutable calculations remain separate artifacts."""

    def e(value):
        return escape(str(value), quote=True)

    counts = report["counts"]
    trace_blocks = []
    for trace in report["traces"]:
        rows = []
        for c in trace["candidates"]:
            failed = [x["id"] for x in c["checks"] if x["state"] == "fail"]
            rows.append(
                "<tr><td>"
                + e(c["id"])
                + "<br>Generation "
                + str(c["iteration_provenance"]["generation"])
                + "</td><td>"
                + e(json.dumps(c["variables"], sort_keys=True))
                + "</td><td>"
                + e(", ".join(failed) or "Known checks pass; qualification unknown")
                + "</td><td>"
                + e(c.get("objectives", {}).get("mass_kg", "unknown"))
                + "</td></tr>"
            )
        best = _representative(trace)
        critique_record = trace["critique"]
        native = next(
            (
                r
                for r in report["native_geometry"]
                if r["context_sha256"] == trace["context_sha256"]
            ),
            None,
        )
        links = ""
        if native:
            folder = Path(native["model"]).parent.as_posix()
            links = f'<p><a href="{e(folder)}/model.FCStd">FreeCAD assembly</a> · <a href="{e(folder)}/model.step">STEP assembly</a> · Native status: {e(native["status"])}</p>'
        checks = "".join(
            f'<li><strong>{e(c["state"])}</strong> {e(c["id"])}: {e(c.get("value"))} {e(c.get("units",""))}; limit {e(c.get("limit"))}. {e(c.get("basis",""))}</li>'
            for c in best["checks"]
        )
        definitions = {
            k: best.get(k)
            for k in (
                "geometry",
                "controlled_target_mappings",
                "basis",
                "load_case_responses",
                "materials",
                "connections",
                "manufacturing",
                "next_actions",
            )
        }
        trace_blocks.append(
            f'<article><h3>{e(trace["lane"])} · {e(trace["context"]["id"])}</h3><p>{e(trace["termination"])}. {len(trace["candidates"])} retained evaluations; {trace["new_evaluations"]} newly computed. Diagnostic/shortlist: {e(best["id"])}.</p>{links}<p>Critic disposition: {e(critique_record["disposition"])}. This is an automated contract challenge; qualified independent engineering review remains required.</p><details><summary>Best retained calculation and unresolved checks</summary><ul>{checks}</ul><pre>{e(json.dumps(definitions,indent=2))}</pre></details><details><summary>All variations and failed attempts</summary><div class="scroll"><table><thead><tr><th>Attempt/parent generation</th><th>Varied dimensions (SI units)</th><th>Known adverse results</th><th>Mass objective (kg; scope in definition)</th></tr></thead><tbody>{"".join(rows)}</tbody></table></div></details></article>'
        )
    package_rows = []
    for p in report["packages"]:
        content = json.dumps(
            dict(
                required_gates=p["required_gates"],
                production_artifact_ids=p["production_artifact_ids"],
                inspection_characteristic_ids=p["inspection_characteristic_ids"],
            ),
            indent=2,
        )
        package_rows.append(
            f'<tr><td>{e(p["id"])}<br>{e(p["title"])}</td><td>{e(p["owner_role"])}<br>{len(p["component_ids"])} assigned inventory IDs</td><td>{e(p["status"])}<br>{len(p["actual_detail_candidate_ids"])} detail responses<br><details><summary>Assigned controlled catalogue IDs</summary><pre>{e(json.dumps(p["component_ids"],indent=2))}</pre></details><details><summary>Proposed research subassembly IDs</summary><pre>{e(json.dumps(p["proposed_detail_component_ids"],indent=2))}</pre></details></td><td>{e(p["next_action"])}<details><summary>Mandatory evidence and actual records still required</summary><pre>{e(content)}</pre></details></td></tr>'
        )
    transfers = "".join(
        f'<li>{e(r["architecture_id"])}: {r["modeled_steel_mass_per_car_kg"]:.1f} kg modelled steel/car × {r["cars"]} cars = {r["gross_added_train_mass_kg"]:.1f} kg added sensitivity. Net mass change unknown; removed frame has no credited mass. Candidate has known failed checks: {e(r["source_candidate_has_known_failures"])}.</li>'
        for r in report["mechanical_to_civil_transfers"]
    )
    audits = report["scenario"]["manufacturing_audit"]["counts"]
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Generative civil and mechanical design team</title><style>body{{margin:0;background:#f4f3ed;color:#17313e;font:16px/1.5 system-ui,sans-serif}}main{{max-width:1300px;margin:auto;padding:24px}}article,details,.notice{{background:white;border:1px solid #ccd4d1;border-radius:6px;padding:16px;margin:14px 0}}.notice{{border-left:5px solid #9a4d30}}nav{{display:flex;flex-wrap:wrap;gap:18px}}a{{color:#176b79;overflow-wrap:anywhere}}pre{{white-space:pre-wrap;overflow-wrap:anywhere;font-size:12px}}summary{{cursor:pointer}}li{{overflow-wrap:anywhere}}.scroll{{overflow:auto;max-width:100%}}table{{border-collapse:collapse;width:100%;min-width:850px}}th,td{{padding:12px;text-align:left;border:1px solid #ccd4d1;vertical-align:top;max-width:380px;overflow-wrap:anywhere}}h1,h2,h3{{line-height:1.2;overflow-wrap:anywhere}}@media(max-width:650px){{main{{padding:14px}}article{{padding:12px}}}}</style></head><body><main>
<h1>Generative civil and mechanical design team</h1>
<p class="notice">Executed provisional design development. {counts['evaluated_variations']} detailed variations across {counts['detail_contexts']} contexts; {counts['provisional_local_solutions']} contexts have passing known checks. All {counts['packages']} packages remain open for integrated engineering and manufacturing acceptance. An unsolved design is retained as unsolved.</p>
<nav><a href="#team">Team and iteration</a><a href="#coupling">Civil/mechanical propagation</a><a href="#results">Design variations</a><a href="#packages">All components and packages</a><a href="../campaign-review/index.html">Earlier campaign review</a></nav>
<h2 id="team">Team and iteration</h2><p>Configuration coordinator → civil and mechanical designers → manufacturing integrator → separate critic → changed-variable proposal. The reproducible runner executes engineering adapters built by the collaborating agents. It does not simulate new LLM conversations or appoint a design authority.</p><p>Each attempt retains variables, units, materials, connection assumptions, load context, manufacturing route, check results and parent/repair reasons. A failed check proposes bounded changes. A local solution stops for qualification; an exhausted domain records that no solution was found. Identical inputs are not repeated to manufacture evidence. A fresh source-bound run is required after a changed model or accepted basis.</p>
<h2 id="coupling">Civil/mechanical propagation</h2><ul>{transfers}</ul><p>Repeated transfer entries distinguish 20 m and 25 m spans. Proportional axle scaling is an explicit sensitivity, not an approved axle/CG allocation. LM3 and six-car planning inputs remain separate. Civil width changes recalculate section properties, self-weight and prestress responses before cage, pad and footing screening.</p>
<h2 id="results">Detailed variations and retained failures</h2>{''.join(trace_blocks)}
<h2 id="packages">All component and system work</h2><p>The audited scenario covers {report['scenario']['counts']['component_ids']} distinct controlled IDs in {counts['packages']} work packages. There are {counts['detailed_packages']} packages with a new partial detail response. Other systems have explicit discipline, input, manufacturing and qualification work; coverage is not completion. Existing preliminary models {'were freshly executed for all packages' if report['baseline_execution'] else 'were not rerun in this detail-only acceptance run'}.</p><p>Manufacturing audit: {audits["missing_or_unissued_production_artifacts"]} missing/unissued production artifacts; {audits["actual_inspection_result_records"]} measured result records for {audits["inspection_characteristics"]} planned characteristics; {audits["issued_drawing_references"]} issued drawing references among {audits["drawing_definitions"]} definitions. Planned drawings, inspections and supplier requests cannot replace issued documents or measured first articles. British manufacture remains the equipment priority; exact offered configurations and capacities require supplier evidence. Enquiries remain unsent.</p><div class="scroll"><table><thead><tr><th>Package</th><th>Owner / allocation</th><th>Actual detail coverage</th><th>Next action / open evidence</th></tr></thead><tbody>{''.join(package_rows)}</tbody></table></div>
<p><a href="report.json">Immutable full evidence reference</a> · <a href="receipt.json">Execution seal reference</a>. Read archived JSON with <code>evidence_store.read_json</code>. Native geometry verification does not establish reinforcement, joints, fatigue, material durability, foundation acceptance or production capability.</p></main></body></html>"""
