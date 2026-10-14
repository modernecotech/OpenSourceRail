"""Actual model execution, budgets, adverse neighbourhoods and independent runs."""

from copy import deepcopy

import pytest

from engineering.design_engine import contracts as c
from engineering.design_engine.adapters import compile_candidate, screen
from engineering.design_engine.registry import get
from engineering.design_engine.runtime import BudgetExceeded, Cancelled
from engineering.design_engine.uncertainty import sensitivity


def scope():
    return c.identity(
        dict(
            schema=c.SCHEMA,
            city="samawah",
            project="samawah",
            environment="simulation",
            configuration_revision="sensitivity-fixture",
            baseline_sha256=None,
            run_id=None,
            asset_id=None,
            part_id=None,
        )
    )


def charter():
    p = get("clipped-side-bay")
    p["variables"] = dict(
        x=dict(kind="real", bounds=[0, 2], unit="m"),
        y=dict(kind="choice", choices=[1, 2, 2.0], unit="1"),
    )
    return p


def evaluator(p, s):
    def execute(values, case):
        result = dict(
            id="candidate-" + c.fingerprint(values),
            variables=values,
            problem_sha256=c.problem_fingerprint(p),
            identity=deepcopy(s),
            metrics=dict(defined_mass_kg=10 + values["x"] * 2 + values["y"]),
            installed_cost=None,
            carbon=None,
            checks={
                k: dict(state="unknown", basis="independent synthetic test fixture")
                for k in p["applicability"]["mandatory_checks"]
            },
            physical_release=False,
            production_released=False,
            independently_accepted=False,
        )
        if values["x"] == 2:
            result["checks"]["nominal_deflection"] = dict(
                state="failed", basis="adverse boundary fixture"
            )
        return result

    return execute


def test_every_duplicate_proposal_charged_and_failed_low_cost_cannot_be_hidden():
    p, s = charter(), scope()
    calls = []
    result = sensitivity(
        p, s, dict(x=1, y=1), evaluator(p, s), lambda n, phase: calls.append((n, phase))
    )
    assert result["requested_cases"] == result["proposals_charged"] == len(calls) == 5
    assert result["cache_hits"] == 1
    assert result["oracle_calls"] == 4
    assert any(
        r["state"] == "failed" and r["candidate"]["variables"]["x"] == 2
        for r in result["cases"]
    )
    assert all(r["objectives"]["installed_cost"] is None for r in result["cases"])
    assert all(r["delta_from_baseline"]["carbon"] is None for r in result["cases"])
    assert result["verified_frontier"] == []
    assert not result["physical_robustness_accepted"]


def test_supplied_interval_holdouts_execute_separately_and_never_cache_baseline():
    p, s = charter(), scope()
    calls, holdout_calls, charges = [], [], []
    base = evaluator(p, s)

    def execute(values, case):
        calls.append(deepcopy(values))
        return base(values, case)

    def holdout(values, case):
        holdout_calls.append(deepcopy(values))
        return base(values, case)

    result = sensitivity(
        p,
        s,
        dict(x=1, y=1),
        execute,
        lambda n, phase: charges.append(phase),
        uncertainty_intervals=[
            dict(
                variable="x",
                lower=1,
                upper=2,
                unit="m",
                basis_reference="declared tolerance report",
            )
        ],
        holdout_evaluator=holdout,
    )
    assert len(holdout_calls) == 2
    assert holdout_calls[0] == dict(x=1, y=1)
    assert len(calls) == 4
    assert len(charges) == result["proposals_charged"] == 7
    assert [r["state"] for r in result["cases"] if r["case"]["arm"] == "holdout"] == [
        "unknown",
        "failed",
    ]
    assert not result["source_references_verified"]
    assert not result["measured_holdout_available"]


def test_bounded_plan_retains_unexecuted_cases_and_absent_holdouts():
    p, s = charter(), scope()
    result = sensitivity(
        p, s, dict(x=1, y=1), evaluator(p, s), lambda *args: None, max_proposals=2
    )
    assert result["proposals_charged"] == 2
    assert len(result["cases"]) == 5
    assert sum(r["state"] == "not-run" for r in result["cases"]) == 3
    result = sensitivity(
        p,
        s,
        dict(x=1, y=1),
        evaluator(p, s),
        lambda *args: None,
        uncertainty_intervals=[
            dict(
                variable="x",
                lower=0.5,
                upper=1.5,
                unit="m",
                basis_reference="future source",
            )
        ],
    )
    assert all(
        r["state"] == "not-run"
        for r in result["cases"]
        if r["case"]["arm"] == "holdout"
    )


@pytest.mark.parametrize("change", ["unit", "source", "domain", "baseline"])
def test_uncertainty_does_not_relax_domain_or_invent_a_source(change):
    p, s = charter(), scope()
    interval = dict(
        variable="x", lower=0.5, upper=1.5, unit="m", basis_reference="source"
    )
    if change == "unit":
        interval["unit"] = "kg"
    elif change == "source":
        interval["basis_reference"] = ""
    elif change == "domain":
        interval["upper"] = 3
    else:
        interval["lower"] = 1.1
    with pytest.raises(ValueError):
        sensitivity(
            p,
            s,
            dict(x=1, y=1),
            evaluator(p, s),
            lambda *args: None,
            uncertainty_intervals=[interval],
        )


def test_scoped_evaluator_errors_are_retained_without_cross_city_recommendation():
    p, s = charter(), scope()
    good = evaluator(p, s)

    def changed(values, case):
        row = good(values, case)
        row["identity"]["city"] = "mosul"
        return row

    result = sensitivity(p, s, dict(x=1, y=1), changed, lambda *args: None)
    assert all(
        r["state"] == "failed" and r["candidate"] is None for r in result["cases"]
    )
    assert all("scoped identity" in r["error"] for r in result["cases"])


def test_common_budget_failure_stops_and_retains_remaining_plan():
    p, s = charter(), scope()

    def charge(*args):
        raise BudgetExceeded("external execution budget exhausted")

    result = sensitivity(p, s, dict(x=1, y=1), evaluator(p, s), charge)
    assert result["cases"][0]["state"] == "budget-exceeded"
    assert all(r["state"] == "not-run" for r in result["cases"][1:])
    assert result["oracle_calls"] == result["proposals_charged"] == 0


@pytest.mark.parametrize("cancel_in", ["budget", "evaluator"])
def test_cancellation_escapes_campaign_without_running_next_neighbour(cancel_in):
    p, s = charter(), scope()
    calls = []

    def charge(*args):
        calls.append("charge")
        if cancel_in == "budget":
            raise Cancelled("job cancellation requested")

    def execute(values, case):
        calls.append("evaluator")
        raise Cancelled("job cancellation requested")

    with pytest.raises(Cancelled, match="cancellation requested"):
        sensitivity(p, s, dict(x=1, y=1), execute, charge)
    assert calls == (["charge"] if cancel_in == "budget" else ["charge", "evaluator"])


def test_actual_compiler_screen_finite_neighbourhood_preserves_geometry_scope(tmp_path):
    p, s = get("clipped-side-bay"), scope()
    baseline = dict(support_span_m=1.0, grade_density=80, core_m=0.0246, skin_m=0.0015)
    for name, spec in p["variables"].items():
        spec["choices"] = [baseline[name]]
    p["variables"]["support_span_m"]["choices"].append(0.5)
    charges = []

    def charge(n, phase):
        charges.append((n, phase))

    def execute(values, case):
        candidate = compile_candidate(p, s, values)
        screen(p, candidate, charge, tmp_path)
        return candidate

    result = sensitivity(p, s, baseline, execute, charge)
    assert result["oracle_calls"] == result["proposals_charged"] == 2
    assert result["cases"][1]["delta_from_baseline"]["metrics.defined_mass_kg"] > 0
    assert (
        result["cases"][1]["candidate"]["metrics"]["screen_deflection_m"]
        < result["cases"][0]["candidate"]["metrics"]["screen_deflection_m"]
    )
    assert result["cases"][1]["objectives"]["installed_cost"] is None
    assert all(
        r["candidate"]["problem_sha256"] == c.problem_fingerprint(p)
        for r in result["cases"]
    )
