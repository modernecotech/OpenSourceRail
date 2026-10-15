"""Common compilation and controlled integration; native physics runs are separate."""

from copy import deepcopy
from itertools import product
import json

import pytest

from engineering.analysis.tests.test_design_engine import scope
from engineering.design_engine import adapters, runtime
from engineering.design_engine.bom import candidate_bill, review_bill
from engineering.design_engine.contracts import fingerprint
from engineering.design_engine.recursive_workflow import execute, policy
from engineering.design_engine.registry import get
from engineering.design_engine.store import Store


@pytest.mark.parametrize("family", ["mechanical-cleat", "civil-steel-beam"])
def test_all_actual_solid_definitions_have_corresponding_inventory(family, tmp_path):
    charter = get(family)
    keys = list(charter["variables"])
    ids = set()
    for combination in product(*(charter["variables"][key]["choices"] for key in keys)):
        values = dict(zip(keys, combination))
        row = adapters.compile_candidate(charter, scope(), values)
        before = fingerprint(row["definition"]["model"])
        adapters.screen(charter, row, lambda *args: None, tmp_path)
        bill = candidate_bill(row, adapter=family)
        assert bill["physical_instance_count"] == 1
        assert bill["defined_mass_kg"] == pytest.approx(row["metrics"]["defined_mass_kg"])
        assert bill["parts"][0]["revision"] == "RESEARCH-1"
        assert fingerprint(row["definition"]["model"]) == before
        assert not bill["complete_installed_kit"] and not row["physical_release"]
        assert row["checks"]["physical_correlation"]["state"] == "unknown"
        assert row["checks"]["linear_service"]["state"] == "not-run"
        ids.add(row["id"])
    assert len(ids) == 6


@pytest.mark.parametrize("controls", [
    {"native_checks": []}, {"physical_checks": []}, {"screening_checks": ["geometry"]},
    {"evaluations": True}, {"objective_axes": ["invented-cost"]},
])
def test_clients_cannot_waive_checks_or_invent_objectives(controls):
    with pytest.raises(ValueError):
        policy(get("mechanical-cleat"), controls)


def test_generated_default_and_missing_native_preflight_are_explicit(monkeypatch):
    from engineering.design_engine.generated_parts import defaults

    req = runtime.request("mechanical-cleat", scope(), recursive={"evaluations": 12})
    assert req["candidates"] == [defaults("mechanical-cleat")]
    assert req["refine"] and req["recursive"]["native_checks"]
    tools = dict(numpy="present", scipy="present", pymoo=None,
                 generated_parts={"available": False, "missing": ["FreeCADCmd"]})
    monkeypatch.setattr(runtime, "toolchain", lambda adapter: tools)
    assert runtime.preflight(req["problem"], operation="iterate")["missing"] == ["FreeCADCmd"]
    assert runtime.preflight(req["problem"], operation="screen")["available"]


def test_recursive_and_paired_experiments_remain_separate():
    with pytest.raises(ValueError, match="separate experiments"):
        runtime.request("mechanical-cleat", scope(), recursive={},
                        search={"seeds": [11, 29], "evaluations": 4})


def test_failed_compilation_is_reviewable_but_missing_inventory_never_passes():
    row = dict(id="failed-test", definition_sha256=None, evidence_state="failed",
               error="controlled compilation failure")
    bill = review_bill(row, adapter="mechanical-cleat")
    assert bill["state"] == "not-compiled" and bill["physical_instance_count"] is None
    row["definition"] = {"model": {"parts": []}}
    with pytest.raises(ValueError):
        review_bill(row, adapter="mechanical-cleat")


def test_common_loop_charges_native_cases_and_keeps_replayable_checkpoints(tmp_path):
    """Real compilation, explicitly synthetic native outcome for workflow testing."""
    req = runtime.request("mechanical-cleat", scope(), recursive=dict(
        evaluations=12, confirmations=6, finite_exhaustive=True))
    store = Store(tmp_path / "store")
    job = store.create(req)
    budget = runtime.Budget(store, job["id"], req["problem"]["budget"])
    folder = tmp_path / "attempt"

    def evaluate(values, charge):
        row = adapters.compile_candidate(req["problem"], req["identity"], values)
        return adapters.screen(req["problem"], row, charge, folder)

    def confirm(row):
        budget.charge(3, "labelled-test-double-native-cases")
        for key in req["recursive"]["native_checks"]:
            row["checks"][key] = dict(state="passed", basis="Workflow test double; no native physics validation")
        return row

    result = execute(req, evaluate, budget, folder, confirm=confirm)
    assert len(result["candidates"]) == 6 and result["confirmations"] == 6
    assert result["common_evaluations_spent"] == 24  # six compiles + eighteen declared cases
    assert result["native_domain_complete"] and not result["global_optimum_claimed"]
    assert all(not row["physical_release"] for row in result["candidates"])
    frames = sorted((folder / "recursive-progress").glob("*.json"))
    assert len(frames) >= 12
    replay = {}
    for path in frames:
        frame = json.loads(path.read_text())
        assert frame["request_sha256"] == fingerprint(req)
        for row in frame["changed_candidates"]:
            replay[row["id"]] = row
    assert replay == {row["id"]: row for row in result["candidates"]}
    assert json.loads((folder / "recursive-search.json").read_text())["decision_trace_sha256"] == result["decision_trace_sha256"]
