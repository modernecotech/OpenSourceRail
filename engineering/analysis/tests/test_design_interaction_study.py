"""Factorial effects use actual paired evaluations; failures cannot become zeros."""

from copy import deepcopy
import json

import pytest

from engineering.design_engine.interaction_study import interaction_study


def run(evaluate, **changes):
    arguments = dict(
        candidates={"A": {"offset": 1}, "B": {"offset": 4}},
        factors={"load": [0, 2], "softening": [0, 3]},
        evaluate=evaluate,
        seed=21,
        max_evaluations=8,
        wall_seconds=30,
    )
    arguments.update(changes)
    return interaction_study(**arguments)


def actual_formula(candidate, scenario):
    x, y = scenario["load"], scenario["softening"]
    return dict(
        state="completed",
        metrics={"response": candidate["offset"] + 2 * x + 3 * y + 5 * x * y},
    )


def test_paired_full_factorial_detects_known_interaction_and_preserves_inputs(tmp_path):
    candidates = {"A": {"offset": 1}, "B": {"offset": 4}}
    original = deepcopy(candidates)
    report = run(actual_formula, candidates=candidates, output=tmp_path / "study")
    assert report["evaluator_calls"] == report["requested_cases"] == 8
    assert report["all_cases_completed"]
    assert report["probability_model"] is None and report["robust_qualified"] is False
    for row in report["candidate_summaries"]:
        assert row["pair_interactions"][0]["difference_in_differences"] == 30
        assert row["scenario_ranges"]["response"]["complete_explicit_scenario_envelope"]
    assert all(row["right_minus_left"] == 3 for row in report["paired_comparisons"])
    assert candidates == original
    assert len(list((tmp_path / "study/cases").glob("*.json"))) == 8
    with pytest.raises(FileExistsError):
        run(actual_formula, output=tmp_path / "study")


def test_budget_counts_all_actual_calls_and_keeps_unexecuted_scenarios():
    calls = []

    def evaluate(candidate, scenario):
        calls.append((candidate, scenario))
        return actual_formula(candidate, scenario)

    report = run(evaluate, max_evaluations=3)
    assert len(calls) == report["evaluator_calls"] == 3
    assert len(report["rows"]) == 8
    assert sum(row["state"] == "not-run" for row in report["rows"]) == 5
    assert report["all_cases_executed"] is False
    assert all(
        row["pair_interactions"][0]["difference_in_differences"] is None
        for row in report["candidate_summaries"]
    )


@pytest.mark.parametrize(
    "failure",
    [
        "failed",
        "unknown",
        "outside-domain",
        "unavailable",
        "timeout",
        "nan",
        "invalid-metrics",
    ],
)
def test_failed_or_unknown_corner_cannot_establish_an_interaction(failure):
    def evaluate(candidate, scenario):
        if scenario["load"] == 2 and scenario["softening"] == 3:
            if failure == "timeout":
                raise TimeoutError("actual evaluator timeout fixture")
            if failure == "nan":
                return dict(state="completed", metrics={"response": float("nan")})
            if failure == "invalid-metrics":
                return dict(state="completed", metrics={"response": object()})
            return dict(state=failure, metrics={"response": None})
        return actual_formula(candidate, scenario)

    report = run(evaluate)
    assert report["evaluator_calls"] == 8
    assert report["all_cases_completed"] is False
    assert all(
        row["pair_interactions"][0]["state"] == "unknown"
        for row in report["candidate_summaries"]
    )
    assert any(row["right_minus_left"] is None for row in report["paired_comparisons"])


def test_seed_reproduces_paired_scenarios_without_inventing_a_distribution():
    first, second = run(actual_formula), run(actual_formula)
    assert [row["scenario"] for row in first["rows"]] == [
        row["scenario"] for row in second["rows"]
    ]
    assert first["candidate_summaries"] == second["candidate_summaries"]
    assert (
        run(actual_formula, seed=22)["rows"][0]["scenario"]
        != first["rows"][0]["scenario"]
    )


@pytest.mark.parametrize("interrupt", ["operator-cancel", "job-evaluation-budget"])
def test_job_cancellation_and_budget_stop_paired_study_without_reclassifying_as_candidate_failure(
    tmp_path, interrupt
):
    from engineering.design_engine.runtime import (
        Budget,
        BudgetExceeded,
        Cancelled,
        request,
    )
    from engineering.design_engine.store import Store

    scope = dict(
        schema="osr-design-identity/1",
        city="samawah",
        project="interaction-fixture",
        environment="simulation",
        configuration_revision="fixture-revision",
        baseline_sha256="a" * 64,
        run_id=None,
        asset_id=None,
        part_id=None,
    )
    store = Store(tmp_path / "store")
    job = store.create(request("clipped-side-bay", scope))
    budget = Budget(
        store,
        job["id"],
        dict(
            wall_seconds=30,
            evaluations=1 if interrupt == "job-evaluation-budget" else 8,
        ),
    )
    calls = []

    def evaluate(candidate, scenario):
        calls.append(scenario)
        budget.charge(1, "paired-factorial-actual-evaluation")
        if interrupt == "operator-cancel":
            store.cancel(job["id"])
        return actual_formula(candidate, scenario)

    output = tmp_path / "paired-study"
    exception = Cancelled if interrupt == "operator-cancel" else BudgetExceeded
    with pytest.raises(exception):
        run(evaluate, output=output)
    assert len(calls) == 2
    assert budget.spent == 1
    retained = list((output / "cases").glob("*.json"))
    assert len(retained) == 1
    completed = json.loads(retained[0].read_text())
    assert completed["state"] == "completed"
    assert completed["evaluator_called"]
    assert "response" in completed["metrics"]
    assert not (output / "report.json").exists()
    assert (output / "request.json").is_file()


def test_real_civil_compiler_can_be_used_as_the_paired_evaluator():
    from engineering.design_engine.design_alternatives import compile_civil

    def evaluate(candidate, scenario):
        data = compile_civil({**candidate, **scenario})
        return dict(
            state="completed",
            metrics={
                "defined_mass_kg": data["correspondence"]["mass_kg"],
                "installed_study_mass_kg": data["quantities"][
                    "installed_study_mass_kg"
                ],
            },
        )

    report = interaction_study(
        {
            "reference": {"pier_family": "solid"},
            "hollow": {"pier_family": "hollow-tapered"},
        },
        {"material": ["normal", "lightweight"], "deck_family": ["pi", "hollow-box"]},
        evaluate,
        seed=21,
        max_evaluations=8,
        wall_seconds=60,
    )
    assert report["evaluator_calls"] == 8 and report["all_cases_completed"]
    assert all(row["state"] == "completed" for row in report["paired_comparisons"])
    assert any(
        row["difference_in_differences"] != 0
        for summary in report["candidate_summaries"]
        for row in summary["pair_interactions"]
    )


@pytest.mark.parametrize(
    "changes",
    [
        {"factors": {"load": [0, 0], "softening": [0, 1]}},
        {"factors": {"load": [0, 1]}},
        {"max_evaluations": 0},
        {"wall_seconds": float("inf")},
        {"seed": True},
    ],
)
def test_implicit_factor_levels_or_unbounded_study_are_rejected(changes):
    with pytest.raises(ValueError):
        run(actual_formula, **changes)
