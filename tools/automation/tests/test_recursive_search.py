"""Policy protocol tests use labelled artificial oracles; native integration is separate."""
from copy import deepcopy
import math
import random

import pytest

from engineering.design_engine.contracts import fingerprint, problem_fingerprint
from engineering.design_engine.recursive_search import RecursiveSearchStop, recursive_search, validate_policy
from engineering.design_engine.registry import charter, choice, real


def fixture(domains=None, *, axes=None, evaluations=32):
    problem = charter("recursive-policy-fixture", "policy-fixture", "Test policy, not physical qualification",
                      domains or {"x": choice("1", 1, 2, 3)},
                      checks=["geometry", "solver", "physical_correlation", "independent_acceptance"])
    problem["objectives"] = axes or ["mass", "cost"]
    problem["budget"]["evaluations"] = evaluations
    scope = dict(schema="osr-design-identity/1", city="samawah", project="policy/test", environment="simulation",
                 configuration_revision="test-1", baseline_sha256="a"*64, run_id=None, asset_id=None, part_id=None)
    context = dict(identity=scope, source_sha256={"fixture-oracle.py": "b"*64},
                   toolchain={"oracle": "labelled-policy-unit-fixture/1"}, request={"id": "fixture-request"})
    policy = dict(evaluations=evaluations, confirmations=evaluations//2,
                  screening_checks=["geometry"], native_checks=["solver"],
                  physical_checks=["physical_correlation", "independent_acceptance"])
    return problem, context, policy


def oracle(problem, context, *, score=None, screen=None, native=None, alter=None):
    calls = []
    def evaluate(values, phase, parent):
        calls.append((phase, deepcopy(values), parent))
        checks = {key: dict(state="unknown", basis="Policy-only synthetic fixture; no physical/native validation")
                  for key in problem["applicability"]["mandatory_checks"]}
        checks["geometry"]["state"] = "passed" if screen is None or screen(values) else "failed"
        return dict(id="candidate-"+fingerprint(values), variables=deepcopy(values), identity=deepcopy(context["identity"]),
                    problem_sha256=problem_fingerprint(problem), definition_sha256=fingerprint(["fixture-definition", values]),
                    definition={"label": "Policy-only artificial definition", "values": deepcopy(values)},
                    metrics=score(values) if score else dict(mass=values["x"], cost=4-values["x"]),
                    checks=checks, physical_release=False, independently_accepted=False)
    def confirm(candidate):
        calls.append(("confirm", deepcopy(candidate["variables"]), candidate["id"]))
        result = deepcopy(candidate)
        value = "passed" if native is None else native(candidate["variables"])
        result["checks"]["solver"].update(state=value, basis="Labelled policy fixture outcome, not an actual physics test")
        if alter:
            alter(result)
        return result
    return evaluate, confirm, calls


def test_exhaustive_native_failures_never_win_and_full_accounting_is_exact():
    p, ctx, settings = fixture({"x": choice("1", 1, 2)}, evaluations=4)
    settings["finite_exhaustive"] = True
    evaluate, confirm, calls = oracle(p, ctx, score=lambda v: dict(mass=3-v["x"]), native=lambda v: "failed" if v["x"]==2 else "passed")
    result = recursive_search(p, evaluate, confirm, context=ctx, policy=settings)
    assert result["evaluations"] == len(calls) == 4
    assert result["proposals"] == result["confirmations"] == 2
    assert result["termination_reason"] == "finite-space-exhausted"
    assert result["finite_domain_complete"] and result["native_domain_complete"]
    best = next(c for c in result["candidates"] if c["id"]==result["incumbent_id"])
    assert best["variables"] == {"x": 1}
    assert result["best_verified_in_tested_domain_claimed"]
    assert not result["global_optimum_claimed"] and not result["physical_release"]
    assert all(row["physical_correlation"]["state"]=="unknown" for row in result["physical_qualification"].values())


def test_native_feedback_changes_next_recursive_neighbour_not_just_final_ranking():
    p, ctx, settings = fixture({"x": dict(kind="integer", unit="1", bounds=[0, 8])}, evaluations=8)
    settings["refinements"] = 2
    sequences = []
    for failing in (False, True):
        evaluate, confirm, calls = oracle(p, ctx, score=lambda v: dict(mass=v["x"]),
            native=lambda v: "failed" if failing and v["x"]<=4 else "passed")
        result = recursive_search(p, evaluate, confirm, context=ctx, initial=[{"x": 4}], policy=settings)
        sequences.append([values["x"] for phase, values, _ in calls if phase=="screen"])
        assert [values for phase, values, _ in calls if phase=="screen"] == [values for phase, values, _ in calls if phase=="confirm"]
        assert result["evaluations"]==8
    assert sequences == [[4, 0, 8, 2], [4, 0, 8, 6]]


def test_finite_exhaustive_coverage_still_uses_native_feedback_for_next_anchor():
    p, ctx, settings = fixture({"x": choice("1", 1, 2), "y": choice("1", 1, 2, 3)}, evaluations=12)
    settings["finite_exhaustive"] = True
    sequences = []
    for failing in (False, True):
        evaluate, confirm, calls = oracle(p, ctx, score=lambda v: dict(mass=v["x"]+v["y"]),
            native=lambda v: "failed" if failing and v=={"x": 1, "y": 1} else "passed")
        result = recursive_search(p, evaluate, confirm, context=ctx, policy=settings)
        sequences.append([values for phase, values, _ in calls if phase=="screen"])
        assert result["finite_domain_complete"] and result["native_domain_complete"]
        assert result["completed_unique_candidates"]==6
    assert sequences[0][:3] == [{"x": 1, "y": 1}, {"x": 2, "y": 1}, {"x": 1, "y": 2}]
    assert sequences[1][:3] == [{"x": 1, "y": 1}, {"x": 2, "y": 1}, {"x": 2, "y": 2}]


def test_compile_callback_failure_retains_explicit_common_scope_without_inventory():
    p, ctx, settings = fixture({"x": choice("1", 1)}, evaluations=2)
    def failed(*args):
        raise RuntimeError("actual compiler rejected geometry")
    result = recursive_search(p, failed, failed, context=ctx, policy=settings)
    row = result["candidates"][0]
    assert row["schema"] == "osr-design-candidate/1"
    assert row["identity"] == ctx["identity"] and row["problem_sha256"] == problem_fingerprint(p)
    assert row["definition_sha256"] is None and row["evidence_state"] == "failed"
    assert row["error"] == "actual compiler rejected geometry"
    assert result["incumbent_id"] is None


def test_failed_initial_geometry_does_not_trap_search_and_confirmation_is_fair():
    p, ctx, settings = fixture({"x": dict(kind="integer", unit="1", bounds=[0, 6])}, evaluations=12)
    evaluate, confirm, calls = oracle(p, ctx, screen=lambda v: v["x"]>=3)
    result = recursive_search(p, evaluate, confirm, context=ctx, initial=[{"x": 0}], policy=settings)
    assert result["incumbent_id"]
    best = next(c for c in result["candidates"] if c["id"]==result["incumbent_id"])
    assert best["variables"]["x"] >= 3
    assert any(phase=="confirm" for phase, _, _ in calls)
    assert calls[0][1]=={"x": 0}


@pytest.mark.parametrize("state", ["failed", "unknown", "not-run", "outside-domain", "unavailable", "stale"])
def test_unconfirmed_or_bad_native_evidence_cannot_be_best(state):
    p, ctx, settings = fixture({"x": choice("1", 1)}, evaluations=2)
    evaluate, confirm, _ = oracle(p, ctx, native=lambda _: state)
    result = recursive_search(p, evaluate, confirm, context=ctx, policy=settings)
    assert result["incumbent_id"] is None and result["verified_frontier"]==[]
    assert result["conditional_screen_frontier"]==[]
    assert not result["best_verified_in_tested_domain_claimed"]
    assert result["candidates"][0]["definition"]["label"].startswith("Policy-only")


def test_unknown_objective_never_becomes_zero_or_domain_best():
    p, ctx, settings = fixture(evaluations=8)
    settings.update(objective_axes=["mass", "cost"], finite_exhaustive=True)
    evaluate, confirm, _ = oracle(p, ctx, score=lambda v: dict(mass=v["x"], cost=None if v["x"]==2 else 4-v["x"]))
    result = recursive_search(p, evaluate, confirm, context=ctx, policy=settings)
    assert len(result["verified_frontier"])==2
    assert not result["native_domain_complete"] and not result["best_verified_in_tested_domain_claimed"]
    assert next(c for c in result["candidates"] if c["variables"]["x"]==2)["metrics"]["cost"] is None


@pytest.mark.parametrize("metric", [None, float("nan"), float("inf"), {"value": 0, "state": "unknown"}])
def test_absent_nonfinite_and_unknown_objectives_are_ineligible(metric):
    p, ctx, settings = fixture({"x": choice("1", 1)}, evaluations=2)
    evaluate, confirm, _ = oracle(p, ctx, score=lambda _: dict(mass=metric))
    result = recursive_search(p, evaluate, confirm, context=ctx, policy=settings)
    assert result["incumbent_id"] is None
    assert not result["verified_frontier"]
    assert result["confirmations"]==0


def test_real_quantization_and_integer_refinement_are_deterministic_full_maps():
    p, ctx, settings = fixture({"x": real("m", 0, 1), "n": dict(kind="integer", unit="ea", bounds=[1, 7])}, evaluations=20)
    settings.update(real_intervals=2, refinements=2)
    transcripts = []
    for seed in (1, 999):
        random.seed(seed)
        evaluate, confirm, calls = oracle(p, ctx, score=lambda v: dict(mass=(v["x"]-.5)**2+v["n"]))
        result = recursive_search(p, evaluate, confirm, context=ctx, initial=[{"n": 1, "x": .3}, {"x": .31, "n": 1}], policy=settings)
        transcripts.append(result)
        assert result["deduplicated_initial_values"]==1
        assert calls[0][1]=={"n": 1, "x": .25}
        assert all(set(v)=={"x", "n"} and type(v["n"]) is int and v["x"]*8==int(v["x"]*8) for _, v, _ in calls)
        assert not result["global_optimum_claimed"] and result["finite_domain_size"] is None
    assert transcripts[0]==transcripts[1]


def test_cache_reuses_only_exact_context_and_still_charges_policy_budget():
    p, ctx, settings = fixture(evaluations=6)
    cache = {}
    evaluate, confirm, calls = oracle(p, ctx)
    first = recursive_search(p, evaluate, confirm, context=ctx, policy=settings, cache=cache)
    calls.clear()
    second = recursive_search(p, evaluate, confirm, context=ctx, policy=settings, cache=cache)
    assert not calls and second["oracle_calls"]==0 and second["cache_hits"]==first["evaluations"]
    assert first["evaluations"]==second["evaluations"]==6
    assert first["candidates"]==second["candidates"]
    for field in ("identity", "source_sha256", "toolchain", "request"):
        changed = deepcopy(ctx)
        if field=="identity": changed[field]["project"]="different/exact-project"
        elif field=="source_sha256": changed[field]["fixture-oracle.py"]="c"*64
        elif field=="toolchain": changed[field]["oracle"]="different-tool-version"
        else: changed[field]["id"]="different-request"
        fresh_evaluate, fresh_confirm, fresh_calls = oracle(p, changed)
        result = recursive_search(p, fresh_evaluate, fresh_confirm, context=changed, policy=settings, cache=cache)
        assert fresh_calls and result["cache_hits"]==0
        assert result["cache_namespace_sha256"]!=first["cache_namespace_sha256"]


@pytest.mark.parametrize("field", ["identity", "problem_sha256", "definition_sha256"])
def test_missing_explicit_evidence_scope_never_enters_verified_ranking(field):
    p, ctx, settings = fixture({"x": choice("1", 1)}, evaluations=2)
    evaluate, confirm, _ = oracle(p, ctx)
    def broken(values, phase, parent):
        candidate=evaluate(values, phase, parent);candidate.pop(field);return candidate
    result = recursive_search(p, broken, confirm, context=ctx, policy=settings)
    assert result["incumbent_id"] is None and result["confirmations"]==0
    assert result["lineage"][0]["error"]


def test_failed_confirmation_keeps_actual_definition_and_bom_and_rejects_identity_change():
    p, ctx, settings = fixture({"x": choice("1", 1)}, evaluations=2)
    evaluate, _, _ = oracle(p, ctx)
    def broken(candidate):
        candidate["definition_sha256"]="f"*64
        return candidate
    result = recursive_search(p, evaluate, broken, context=ctx, policy=settings)
    row=result["candidates"][0]
    assert row["definition_sha256"]==fingerprint(["fixture-definition", {"x": 1}])
    assert row["definition"]["values"]=={"x": 1}
    assert row["checks"]["solver"]["state"]=="failed" and result["incumbent_id"] is None


def test_stopped_native_attempt_retains_partial_lineage_pending_queue_and_checkpoints():
    p, ctx, settings = fixture(evaluations=6)
    evaluate, _, _ = oracle(p, ctx)
    checkpoints=[]
    def stop(candidate): raise RecursiveSearchStop("budget", "actual solver case budget")
    result = recursive_search(p, evaluate, stop, context=ctx, policy=settings, checkpoint=lambda r: checkpoints.append(r))
    assert result["termination_reason"]=="budget" and result["stop"]["message"]=="actual solver case budget"
    assert result["proposals"]==result["confirmations"]==1 and result["evaluations"]==2
    assert len(result["lineage"])==2 and result["lineage"][-1]["stopped"]
    assert result["unconfirmed_candidate_ids"]==[result["candidates"][0]["id"]]
    assert any(r["in_flight_attempt"] and r["in_flight_attempt"]["phase"]=="confirm" for r in checkpoints)
    assert not result["replay_complete"] and result["incumbent_id"] is None
    checkpoints[-1]["candidates"][0]["variables"]["x"]=999
    assert result["candidates"][0]["variables"]["x"]==1


def test_external_budget_and_cancel_exceptions_are_retained_not_swallowed_as_solver_failure():
    class BudgetExceeded(RuntimeError): pass
    class Cancelled(RuntimeError): pass
    p, ctx, settings = fixture(evaluations=6)
    for error, reason in ((BudgetExceeded, "budget"), (Cancelled, "cancelled")):
        def evaluate(*args): raise error("external stop")
        result = recursive_search(p, evaluate, lambda c:c, context=ctx, policy=settings, stop_exceptions=(BudgetExceeded, Cancelled))
        assert result["termination_reason"]==reason
        assert result["proposals"]==1 and result["evaluations"]==1 and result["candidates"]==[]
        assert result["stop"]["type"]==error.__name__ and not result["replay_complete"]


def test_stall_and_iteration_limits_are_reported_without_false_global_claim():
    p, ctx, settings = fixture({"x": dict(kind="integer", unit="1", bounds=[0, 100])}, evaluations=20)
    evaluate, confirm, _ = oracle(p, ctx, score=lambda _: dict(mass=None))
    result=recursive_search(p, evaluate, confirm, context=ctx, policy={**settings, "stall_rounds": 2})
    assert result["termination_reason"]=="stall" and result["evaluations"]<20
    result=recursive_search(p, evaluate, confirm, context=ctx, policy={**settings, "iterations": 1})
    assert result["termination_reason"]=="budget" and result["stop"]["type"]=="iteration-limit"
    assert result["iterations"]==1 and not result["global_optimum_claimed"]


@pytest.mark.parametrize("change", [
    {"native_checks": ["solver", "geometry"]}, {"physical_checks": []},
    {"screening_checks": ["geometry", "physical_correlation"], "physical_checks": ["independent_acceptance"]},
    {"evaluations": True}, {"evaluations": 1000}, {"objective_axes": ["unpriced"]},
    {"seed": -1}, {"finite_exhaustive": "yes"}, {"allow_physical_acceptance": True},
])
def test_policy_validation_rejects_waivers_unknown_axes_and_unbounded_controls(change):
    p, _, settings = fixture()
    with pytest.raises(ValueError): validate_policy(p, {**settings, **change})


def test_exhaustive_mode_is_optional_and_bounded_before_any_oracle_call():
    p, ctx, settings = fixture({"x": real("m", 0, 1)})
    with pytest.raises(ValueError, match="all-choice"):
        recursive_search(p, lambda *a:pytest.fail("must not evaluate"), lambda *a:None, context=ctx,
                         policy={**settings, "finite_exhaustive": True})
    p, ctx, settings = fixture({"x": choice("1", 1, 2, 3)})
    with pytest.raises(ValueError, match="bounded"):
        recursive_search(p, lambda *a:pytest.fail("must not evaluate"), lambda *a:None, context=ctx,
                         policy={**settings, "finite_exhaustive": True, "max_space": 2})
