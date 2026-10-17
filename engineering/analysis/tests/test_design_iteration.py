"""Actual feedback, retained adverse results, resume and untrusted evidence guards."""

from copy import deepcopy
from types import SimpleNamespace

import pytest

from engineering.generative_design import design_iteration as d


def adapter():
    def assess(v, context):
        return dict(
            id=f"trial-{context['id']}-{v['depth']}",
            variables=dict(v),
            checks=[
                dict(
                    id="resistance",
                    state="pass" if v["depth"] >= 3 else "fail",
                    value=v["depth"],
                    limit=3,
                ),
                dict(
                    id="material-qualification", state="unknown", value=None, limit=None
                ),
            ],
            geometry={"depth": v["depth"]},
            materials={"accepted": False},
            connections={"qualified": False},
            manufacturing={"issued": False},
            physical_release=False,
        )

    return SimpleNamespace(
        seed=lambda c: dict(depth=1),
        assess=assess,
        propose=lambda candidate, c: [
            dict(depth=candidate["variables"]["depth"] + 1),
            dict(candidate["variables"]),
        ],
    )


def test_feedback_changes_failed_dimension_and_preserves_parents_and_unknowns():
    trace = d.iterate(adapter(), dict(id="beam"), budget=8)
    assert len(trace["candidates"]) == 3
    assert trace["termination"] == "provisional-solution-held-for-qualification"
    assert trace["selected_candidate_id"] == "trial-beam-3"
    assert trace["candidates"][0]["checks"][0]["state"] == "fail"
    assert trace["candidates"][1]["iteration_provenance"]["parent_candidate_ids"] == [
        "trial-beam-1"
    ]
    assert trace["candidates"][1]["iteration_provenance"]["repair_reasons"] == [
        "resistance"
    ]
    assert trace["critique"]["unknown_check_ids"] == ["material-qualification"]
    assert (
        not trace["physical_release"]
        and not trace["critique"]["independent_engineering_review_performed"]
    )


def test_resume_uses_frontier_without_repeating_completed_evaluations():
    first = d.iterate(adapter(), dict(id="beam"), budget=1)
    assert first["termination"] == "budget-exhausted"
    resumed = d.iterate(adapter(), dict(id="beam"), budget=5, previous=first)
    assert resumed["new_evaluations"] == 2
    assert (
        resumed["candidates"]
        == d.iterate(adapter(), dict(id="beam"), budget=5)["candidates"]
    )
    unchanged = d.iterate(adapter(), dict(id="beam"), budget=5, previous=resumed)
    assert unchanged["new_evaluations"] == 0
    with pytest.raises(ValueError, match="changed context"):
        d.iterate(adapter(), dict(id="other"), budget=5, previous=first)


def test_unknown_only_evaluation_never_becomes_numerical_solution():
    a = adapter()
    original = a.assess

    def unknown(v, c):
        row = original(v, c)
        row["checks"][0]["state"] = "unknown"
        return row

    a.assess = unknown
    a.propose = lambda r, c: []
    trace = d.iterate(a, dict(id="beam"))
    assert trace["selected_candidate_id"] is None
    assert trace["termination"] == "no-solution-in-declared-repair-domain"


@pytest.mark.parametrize("flag", d.FLAGS)
def test_no_adapter_can_claim_release(flag):
    row = adapter().assess(dict(depth=3), dict(id="beam"))
    row[flag] = True
    with pytest.raises(ValueError, match="release"):
        d.validate_candidate(row)


def test_separate_critic_and_missing_assembly_definition():
    row = adapter().assess(dict(depth=3), dict(id="beam"))
    with pytest.raises(ValueError, match="own candidate"):
        d.critique(row, producer="same", reviewer="same")
    row.pop("connections")
    result = d.critique(row, producer="designer")
    assert result["missing_definition_fields"] == ["connections"]
    assert result["disposition"] == "hold-missing-definition"


def test_unretained_resume_parent_and_invalid_budgets_rejected():
    first = d.iterate(adapter(), dict(id="beam"), budget=1)
    first["frontier"][0]["parent"] = "invented"
    with pytest.raises(ValueError, match="parent"):
        d.iterate(adapter(), dict(id="beam"), budget=4, previous=first)
    for invalid in (0, 513, True):
        with pytest.raises(ValueError, match="budget"):
            d.iterate(adapter(), dict(id="beam"), budget=invalid)


def test_unknown_architecture_is_rejected_and_interrupted_attempts_are_retained():
    with pytest.raises(ValueError, match="architecture"):
        d._architecture(dict(configuration_id="unassigned-train"))
    a = adapter()
    original = a.assess
    captured = []

    def interrupted(v, c):
        if v["depth"] == 2:
            raise RuntimeError("declared solver failure")
        return original(v, c)

    a.assess = interrupted
    with pytest.raises(RuntimeError, match="solver failure"):
        d.iterate(a, dict(id="beam"), checkpoint=captured.append)
    assert captured[0]["checks"][0]["state"] == "fail"
    assert captured[1]["parent_candidate_id"] == captured[0]["id"]
    assert "solver failure" in captured[1]["error"]


@pytest.fixture(scope="module")
def actual_campaign(tmp_path_factory):
    folder = tmp_path_factory.mktemp("detail-campaign") / "actual"
    result = d.run(folder, budget=1, native=False, baseline=False)
    assert result["detail_contexts"] == 6 and result["packages"] == 63
    return folder


def test_real_campaign_recomputes_results_and_requires_all_native_contexts(
    actual_campaign,
):
    result = d.verify(actual_campaign)
    assert result["numerical_detail_calculations_recomputed"]
    assert not result["manufacturing_release"]
    with pytest.raises(ValueError, match="native proof"):
        d.verify(actual_campaign, require_native=True)
    with pytest.raises(ValueError, match="current-source"):
        d.verify(actual_campaign, current=False, require_native=True)


def test_real_unchanged_resume_performs_no_repeated_evaluations(
    actual_campaign, tmp_path
):
    result = d.run(
        tmp_path / "resume",
        budget=1,
        native=False,
        baseline=False,
        resume=actual_campaign,
    )
    assert result["new_evaluations"] == 0
    assert result["evaluated_variations"] == 6


@pytest.mark.parametrize(
    "mutation",
    ["exchange", "frontier", "package", "release", "production", "inspection"],
)
def test_resealing_cannot_invent_coverage_or_repair_results(
    actual_campaign, tmp_path, mutation
):
    import shutil
    from engineering.generative_design.campaign import write

    folder = tmp_path / "copy"
    shutil.copytree(actual_campaign, folder)
    report = d._read(folder / "report.json")
    if mutation == "exchange":
        report["exchanges"][0]["component_ids"].append("invented-completed-component")
    elif mutation == "frontier":
        report["traces"][0]["frontier"] = []
    elif mutation == "package":
        report["packages"][0]["required_gates"] = {}
    elif mutation == "release":
        report["packages"][0]["design_complete"] = True
    elif mutation == "production":
        report["packages"][0]["production_artifact_ids"].append(
            "fabricated-issued-drawing"
        )
    else:
        report["packages"][0]["inspection_characteristic_ids"].append(
            "fabricated-measurement"
        )
    write(folder / "report.json", report)
    receipt = d._read(folder / "receipt.json")
    receipt["files_sha256"] = d._files(folder)
    write(folder / "receipt.json", receipt)
    with pytest.raises(ValueError):
        d.verify(folder)


def optimization_adapter():
    a = adapter()
    original = a.assess

    def assess(v, context):
        candidate = original(v, context)
        candidate["objectives"] = dict(mass=10 - v["depth"], pieces=v["depth"])
        return candidate

    source = "engineering/analysis/tests/test_design_iteration.py"
    a.assess = assess
    a.optimization_policy = lambda context: dict(
        domains=dict(depth=[1, 2, 3, 4, 5]),
        objective_axes=[
            dict(
                id=name,
                path=["objectives", name],
                units=unit,
                sense="minimize",
                basis="Explicit deterministic benchmark trade-off",
            )
            for name, unit in [("mass", "kg"), ("pieces", "count")]
        ],
        source_sha256={source: d.coverage.sha(d.coverage.ROOT / source)},
    )
    return a


def test_optimization_continues_after_feasibility_and_retains_reproducible_tradeoffs():
    a = optimization_adapter()
    repaired = d.iterate(a, dict(id="beam"), budget=8)
    optimized = d.iterate(a, dict(id="beam"), budget=8, mode="optimization")
    assert len(repaired["candidates"]) == 3
    assert len(optimized["candidates"]) == 5
    assert optimized["termination"] == "optimization-domain-exhausted"
    assert optimized["pareto_candidate_ids"] == [
        "trial-beam-3",
        "trial-beam-4",
        "trial-beam-5",
    ]
    assert optimized == d.iterate(a, dict(id="beam"), budget=8, mode="optimization")
    assert not optimized["manufacturing_release"]
    partial = d.iterate(a, dict(id="beam"), budget=3, mode="optimization")
    resumed = d.iterate(
        a, dict(id="beam"), budget=8, previous=partial, mode="optimization"
    )
    assert resumed["new_evaluations"] == 2
    assert resumed["candidates"] == optimized["candidates"]
    assert resumed["pareto_candidate_ids"] == optimized["pareto_candidate_ids"]
    with pytest.raises(ValueError, match="mode differs"):
        d.iterate(a, dict(id="beam"), previous=repaired, mode="optimization")


def test_unknown_costs_cannot_be_substituted_in_the_pareto_frontier():
    a = optimization_adapter()
    original = a.optimization_policy

    def policy(context):
        result = original(context)
        result["objective_axes"].append(
            dict(
                id="price",
                path=["objectives", "cost"],
                units="GBP",
                sense="minimize",
                basis="Unknown supplier quote",
            )
        )
        return result

    a.optimization_policy = policy
    trace = d.iterate(a, dict(id="beam"), budget=8, mode="optimization")
    assert trace["pareto_candidate_ids"] == []
    assert all(
        d._objective_values(c, trace["optimization_policy"]) is None
        for c in trace["candidates"]
    )
    a.optimization_policy = lambda c: dict(
        domains=dict(depth=[1]), objective_axes=[], source_sha256={}
    )
    with pytest.raises(ValueError, match="sourced objective"):
        d.iterate(a, dict(id="beam"), mode="optimization")


def test_atomic_state_write_preserves_previous_snapshot_when_replace_is_interrupted(
    tmp_path, monkeypatch
):
    path = tmp_path / "state.json"
    d._atomic_write(path, dict(committed=1))

    def interrupted(*args):
        raise OSError("simulated replacement interruption")

    monkeypatch.setattr(d.os, "replace", interrupted)
    with pytest.raises(OSError, match="interruption"):
        d._atomic_write(path, dict(committed=2))
    assert d._read(path) == dict(committed=1)
    assert sorted(p.name for p in tmp_path.iterdir()) == ["state.json"]


def test_campaign_recovers_a_killed_worker_without_final_receipt(tmp_path):
    import os
    import signal
    import subprocess
    import sys

    interrupted = tmp_path / "killed"
    script = """import os, signal, sys
from engineering.generative_design import design_iteration as d, mechanical_detail as m
original = m.assess
calls = 0
def assess(v, c):
    global calls
    calls += 1
    if calls == 3:
        os.kill(os.getpid(), signal.SIGKILL)
    return original(v, c)
m.assess = assess
d.run(sys.argv[1], budget=3, native=False, baseline=False)
"""
    child = subprocess.run(
        [sys.executable, "-c", script, str(interrupted)],
        cwd=d.coverage.ROOT,
        env={**os.environ, "PYTHONPATH": str(d.coverage.ROOT)},
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert child.returncode == -signal.SIGKILL
    assert not (interrupted / "receipt.json").exists()
    state = d._read(interrupted / "execution-state.json")
    retained = state["active_trace"]["candidates"]
    assert len(retained) == 2
    assert state["active_trace"]["active_proposal"]
    resumed = tmp_path / "resumed"
    result = d.run(resumed, budget=3, native=False, baseline=False, resume=interrupted)
    report = d._read(resumed / "report.json")
    assert report["traces"][0]["candidates"][:2] == retained
    assert result["new_evaluations"] == result["evaluated_variations"] - 2
    assert result["numerical_detail_calculations_recomputed"]
    assert d._read(resumed / "request.json")["parent_interrupted_state_sha256"]
    assert not result["manufacturing_release"]
    # Recovery may inspect/recompute evidence, but the worker did not lose completed work.
    assert d._read(interrupted / "execution-state.json") == state


def test_interrupted_campaign_rejects_changed_source_options_and_corrupt_state(
    tmp_path, monkeypatch
):
    from engineering.generative_design import mechanical_detail

    original = mechanical_detail.assess
    calls = 0

    def stop(v, c):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise RuntimeError("interruption")
        return original(v, c)

    monkeypatch.setattr(mechanical_detail, "assess", stop)
    folder = tmp_path / "interrupted"
    with pytest.raises(RuntimeError, match="interruption"):
        d.run(folder, budget=2, native=False, baseline=False)
    monkeypatch.setattr(mechanical_detail, "assess", original)
    with pytest.raises(ValueError, match="options differ"):
        d.run(
            tmp_path / "wrong-options",
            budget=2,
            native=True,
            baseline=False,
            resume=folder,
        )
    source = d.sources()
    source["invented-source"] = "changed"
    monkeypatch.setattr(d, "sources", lambda: source)
    with pytest.raises(ValueError, match="sources/request/environment"):
        d.run(
            tmp_path / "wrong-source",
            budget=2,
            native=False,
            baseline=False,
            resume=folder,
        )
    monkeypatch.undo()
    state = d._read(folder / "execution-state.json")
    state["active_trace"]["frontier"] = []
    d.campaign.write(folder / "execution-state.json", state)
    with pytest.raises(ValueError, match="checksum"):
        d.run(
            tmp_path / "corrupt", budget=2, native=False, baseline=False, resume=folder
        )


def test_completed_attempt_between_atomic_snapshots_is_recovered_without_reevaluation():
    a = adapter()
    states, attempts = [], []

    def checkpoint(candidate):
        attempts.append(deepcopy(candidate))
        raise KeyboardInterrupt("kill after attempt flush before state commit")

    with pytest.raises(KeyboardInterrupt):
        d.iterate(
            a,
            dict(id="beam"),
            budget=1,
            checkpoint=checkpoint,
            state_checkpoint=lambda state: states.append(deepcopy(state)),
        )
    previous = states[-1]
    previous["frontier"].insert(0, previous.pop("active_proposal"))
    original = a.assess

    def unexpected(*args):
        raise AssertionError("completed assessment must not execute twice")

    a.assess = unexpected
    trace = d.iterate(
        a,
        dict(id="beam"),
        budget=1,
        previous=previous,
        recovered_attempts={d.fingerprint(attempts[0]["variables"]): attempts[0]},
    )
    assert trace["new_evaluations"] == 0
    assert trace["candidates"] == attempts
    a.assess = original
    assert trace["frontier"] == d.iterate(a, dict(id="beam"), budget=1)["frontier"]


def test_real_optimization_campaign_replays_sourced_quantity_frontiers(tmp_path):
    folder = tmp_path / "optimization"
    result = d.run(folder, budget=8, native=False, baseline=False, mode="optimization")
    report = d._read(folder / "report.json")
    assert result["evaluated_variations"] == 48
    assert result["numerical_detail_calculations_recomputed"]
    assert all(t["search_mode"] == "optimization" for t in report["traces"])
    for trace in report["traces"]:
        policy = trace["optimization_policy"]
        assert policy["source_sha256"]
        assert [a["units"] for a in policy["objective_axes"]] == ["kg", "count"]
        assert trace["pareto_candidate_ids"] == d._pareto(trace["candidates"], policy)
    assert not result["manufacturing_release"]


def test_optimization_retains_repair_prefix_before_exploring_objectives():
    a = optimization_adapter()
    original = a.assess

    def assess(v, context):
        candidate = original(v, context)
        candidate["checks"][0].update(
            state="pass" if v["depth"] >= 5 else "fail", limit=5
        )
        return candidate

    policy = a.optimization_policy
    a.optimization_policy = lambda context: dict(
        policy(context), domains=dict(depth=list(range(1, 8)))
    )
    a.assess = assess
    a.propose = lambda candidate, context: [
        dict(depth=candidate["variables"]["depth"] + 2)
    ]
    repair = d.iterate(a, dict(id="beam"), budget=8)
    optimization = d.iterate(a, dict(id="beam"), budget=8, mode="optimization")
    assert [c["variables"]["depth"] for c in repair["candidates"]] == [1, 3, 5]
    assert optimization["candidates"][:3] == repair["candidates"]
    assert len(optimization["candidates"]) > len(repair["candidates"])
    assert len(optimization["pareto_candidate_ids"]) > 1


def test_budget_extension_invalidates_civil_descendants_and_preserves_parent_evidence(
    actual_campaign, tmp_path
):
    from engineering.generative_design.campaign import write

    original_files = d._files(actual_campaign)
    original_report = d._read(actual_campaign / "report.json")
    folder = tmp_path / "expanded-budget"
    result = d.run(
        folder, budget=8, native=False, baseline=False, resume=actual_campaign
    )
    report = d._read(folder / "report.json")
    assert report["resume_parent_traces"] == original_report["traces"]
    assert report["superseded_parent_contexts"]
    assert result["numerical_detail_calculations_recomputed"]
    previous = {(t["lane"], t["context_sha256"]): t for t in original_report["traces"]}
    current = {(t["lane"], t["context_sha256"]): t for t in report["traces"]}
    for item in report["superseded_parent_contexts"]:
        old = previous[("civil", item["prior_context_sha256"])]
        new = current[("civil", item["replacement_context_sha256"])]
        assert item["prior_trace_sha256"] == d.fingerprint(old)
        assert new["context"] != old["context"]
        assert new["new_evaluations"] == len(new["candidates"])
        assert not item["physical_release"]
    assert d._files(actual_campaign) == original_files
    assert d._read(actual_campaign / "report.json") == original_report
    assert not result["manufacturing_release"]

    # Resealing cannot silently omit the old-to-new descendant relationship.
    report["superseded_parent_contexts"] = []
    write(folder / "report.json", report)
    receipt = d._read(folder / "receipt.json")
    receipt["files_sha256"] = d._files(folder)
    write(folder / "receipt.json", receipt)
    with pytest.raises(ValueError, match="superseded civil context"):
        d.verify(folder)


def test_resume_context_validation_rejects_invented_old_civil_loads(actual_campaign):
    traces = d._read(actual_campaign / "report.json")["traces"]
    civil = next(t for t in traces if t["lane"] == "civil")
    civil["context"]["span_m"] = 123
    civil["context_sha256"] = d.fingerprint(civil["context"])
    with pytest.raises(ValueError, match="source/context"):
        d._resume_records(traces, d._adapters())
