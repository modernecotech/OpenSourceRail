"""Actual compilation/screens with labelled policy-only confirmation callbacks."""

from copy import deepcopy

import pytest

from engineering.analysis.tests.test_design_engine import scope
from engineering.design_engine import adapters, runtime
from engineering.design_engine.recursive_workflow import execute
from engineering.design_engine.store import Store


def run_policy(tmp_path, problem, values, *, confirm_state="passed", service_test_double=False):
    req = runtime.request(problem, scope(), [values], recursive=dict(evaluations=2, confirmations=1))
    store = Store(tmp_path / "store")
    job = store.create(req)
    budget = runtime.Budget(store, job["id"], req["problem"]["budget"])
    confirmed = []
    screened = []
    folder = tmp_path / "attempt"

    def evaluate(values, charge):
        row = adapters.compile_candidate(req["problem"], req["identity"], values)
        row = adapters.screen(req["problem"], row, charge, folder)
        screened.append(deepcopy(row))
        if service_test_double:
            # The existing fixed deck fails its real 20mm service limit. This
            # deliberate, labelled substitution tests queue transport only.
            row["checks"]["service"] = dict(state="passed",
                basis="Policy queue test double; actual fixed-deck service screen failed")
        return row

    def confirm(row):
        confirmed.append(row["id"])
        for key in req["recursive"]["native_checks"]:
            row["checks"][key] = dict(state=confirm_state,
                basis="Policy transport test double only; no native solver or physical validation")
        return row

    return req, execute(req, evaluate, budget, folder, confirm=confirm), screened, confirmed


def test_actual_roof_thermal_failure_vetoes_native_queue_and_recommendations(tmp_path):
    # This actual roof strip screen passes nominal deflection but the known
    # 85degC/core-datum conflict is independently mandatory and must dominate.
    values = dict(support_span_m=.2, grade_density=100, core_m=.03, skin_m=.002)
    req, result, screened, confirmed = run_policy(tmp_path, "clipped-roof-bay", values)
    first = screened[0]
    assert first["checks"]["nominal_deflection"]["state"] == "passed"
    assert first["checks"]["hot_wet_properties"]["state"] == "failed"
    assert first["checks"]["geometry"]["state"] == "passed"
    assert not confirmed and result["confirmations"] == 0
    assert result["incumbent_id"] is None
    assert result["verified_frontier"] == result["conditional_screen_frontier"] == []
    assert not result["best_verified_in_tested_domain_claimed"]
    assert "hot_wet_properties" in result["outcomes"][first["id"]]["mandatory_failed_checks"]


@pytest.mark.parametrize("problem,values", [
    ("viaduct-bay", dict(pier_height_m=8, pile_length_m=15, pile_spacing_m=2.0)),
    ("foundation-site", dict(pile_length_m=15, pile_spacing_m=2.0)),
])
@pytest.mark.parametrize("confirm_state", ["passed", "failed", "unknown"])
def test_civil_actual_compile_and_screen_with_labelled_service_double_reaches_confirmation(tmp_path, problem, values, confirm_state):
    req, result, screened, confirmed = run_policy(tmp_path, problem, values,
        confirm_state=confirm_state, service_test_double=True)
    settings = req["recursive"]
    assert settings["screening_checks"] == ["geometry", "mass_inertia", "service"]
    assert settings["native_checks"] == ["refinement"]
    assert {"interfaces", "degraded_service"} <= set(settings["physical_checks"])
    assert len(confirmed) == 1
    for key in ("geometry", "mass_inertia"):
        assert screened[0]["checks"][key]["state"] == "passed", screened[0]["checks"][key]
    assert screened[0]["checks"]["service"]["state"] == "failed"
    assert screened[0]["checks"]["refinement"]["state"] == "not-run"
    row = result["candidates"][0]
    assert row["checks"]["interfaces"]["state"] == row["checks"]["degraded_service"]["state"] == "not-run"
    assert row["checks"]["refinement"]["state"] == confirm_state
    assert bool(result["incumbent_id"]) == (confirm_state == "passed")
    assert bool(result["verified_frontier"]) == (confirm_state == "passed")
    assert not result["physical_release"] and not row["physical_release"]
    assert not result["best_verified_in_tested_domain_claimed"]  # only one tested candidate


@pytest.mark.parametrize("problem,values", [
    ("viaduct-bay", dict(pier_height_m=8, pile_length_m=15, pile_spacing_m=2.0)),
    ("foundation-site", dict(pile_length_m=15, pile_spacing_m=2.0)),
])
def test_actual_fixed_civil_service_failure_is_retained_and_never_confirmed_or_recommended(tmp_path, problem, values):
    req, result, screened, confirmed = run_policy(tmp_path, problem, values)
    assert all(row["checks"]["service"]["state"] == "failed" for row in screened)
    assert screened[0]["definition"]["stages"]["service"]["maximum_deflection_m"] > .020
    assert not confirmed and result["confirmations"] == 0
    assert result["incumbent_id"] is None
    assert result["verified_frontier"] == result["conditional_screen_frontier"] == []
    assert not result["native_domain_complete"] and not result["best_verified_in_tested_domain_claimed"]
    assert not result["physical_release"]
