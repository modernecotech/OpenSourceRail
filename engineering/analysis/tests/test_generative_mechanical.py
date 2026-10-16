"""Independent fit, beam and traceability controls for generated workholding."""

from copy import deepcopy
import json
import math

import pytest

from engineering.generative_design import mechanical as m
from engineering.factory_examples.models import volume


def selected():
    r = m.search()
    return r, [c for c in r["candidates"] if c["id"] in r["selected_candidate_ids"]]


def test_feedback_retains_rejected_seed_and_descendant_lineage():
    report, choices = selected()
    seed = report["candidates"][0]
    failures = {c["id"] for c in seed["checks"] if c["status"] == "failed"}
    assert {"locator_fit", "underside_access", "machine_workpiece_envelope"} <= failures
    by_id = {c["id"]: c for c in report["candidates"]}
    assert len(by_id) == 128
    assert len(choices) == 2
    for c in choices:
        assert c["generation"] >= 3
        assert c["conditional_screen_feasible"]
        current = c
        while current["parent_ids"]:
            parent = by_id[current["parent_ids"][0]]
            assert parent["generation"] + 1 == current["generation"]
            assert parent["variables"] != current["variables"]
            current = parent
        assert current["id"] == seed["id"]


def test_retained_worst_case_pin_fit_and_interference():
    _, choices = selected()
    c = choices[0]
    assert c["metrics"]["minimum_diametral_clearance_m"] == pytest.approx(6e-6)
    assert c["metrics"]["maximum_diametral_clearance_m"] == pytest.approx(14e-6)
    variables = dict(c["variables"], stem_diameter_m=0.020)
    bad = m.evaluate(variables)
    assert (
        next(x for x in bad["checks"] if x["id"] == "locator_fit")["status"] == "failed"
    )
    assert bad["metrics"]["minimum_diametral_clearance_m"] == pytest.approx(-4e-6)


def test_strip_stress_deflection_and_cube_scaling():
    _, choices = selected()
    c = choices[0]
    v = c["variables"]
    span = v["pitch_x_m"] + 0.04
    z = v["length_m"] * v["plate_m"] ** 2 / 6
    assert c["metrics"]["nominal_strip_stress_pa"] == pytest.approx(1500 * span / 4 / z)
    thick = m.evaluate(dict(v, plate_m=2 * v["plate_m"]))
    assert thick["metrics"]["nominal_strip_deflection_m"] == pytest.approx(
        c["metrics"]["nominal_strip_deflection_m"] / 8
    )
    assert c["metrics"]["strip_span_m"] > c["metrics"]["underside_gap_m"]


def test_machine_circle_contains_blank_and_workholding_corners():
    _, choices = selected()
    for c in choices:
        v = c["variables"]
        diameter = math.hypot(v["width_m"] + 0.064, v["length_m"] + 0.064)
        assert c["metrics"]["machining_setup_diameter_m"] == pytest.approx(diameter)
        assert diameter < 0.5
        assert c["metrics"]["machining_setup_mass_kg"] < 200
        assert c["metrics"]["machining_setup_height_m"] < 0.32


def test_selected_geometry_matches_dimensions_holes_and_support_access():
    _, choices = selected()
    for c in choices:
        result = m.model(c)
        parts = result["parts"]
        plate = parts[0]
        assert plate["size_m"] == [
            c["variables"][k] for k in ["width_m", "length_m", "plate_m"]
        ]
        assert len(plate["holes"]) == 5
        assert len(parts) == 12
        assert all(volume(p) > 0 for p in parts)
        rails = parts[1:3]
        inner_gap = rails[1]["at_m"][0] - (rails[0]["at_m"][0] + rails[0]["size_m"][0])
        assert inner_gap == pytest.approx(c["metrics"]["underside_gap_m"])
        pin = parts[3]
        assert pin["steps"][0]["diameter_m"] == c["variables"]["stem_diameter_m"]
        assert pin["steps"][0]["length_m"] == c["variables"]["plate_m"]
        assert not result["manufacturing_released"]


def test_no_unknown_is_promoted_by_conditional_selection(tmp_path):
    report, choices = selected()
    assert not report["design_complete"] and not report["physical_release"]
    assert not report["termination"]["complete_solution_found"]
    assert report["termination"]["reason"] == "budget_exhausted"
    for c in choices:
        assert {x["status"] for x in c["checks"]} == {"passed", "unknown"}
        assert not c["design_complete"] and not c["physical_release"]
    paths = m.write_artifacts(report, tmp_path)
    assert len(paths) == 2
    assert all(json.loads(p.read_text())["parts"] for p in paths)


def test_search_is_deterministic_and_small_budget_cannot_fabricate_a_solution():
    assert m.search(budget=16) == m.search(budget=16)
    tiny = m.search(budget=1)
    assert len(tiny["candidates"]) == 1
    assert tiny["selected_candidate_ids"] == []
    assert tiny["termination"]["reason"] == "budget_exhausted"


def test_search_proposals_stay_in_choices_while_independent_assessor_is_continuous():
    cfg = json.loads(m.SPACE.read_text())
    report = m.search(budget=32)
    assert all(
        row["variables"][k] in values
        for row in report["candidates"]
        for k, values in cfg["choices"].items()
    )
    # The continuous assessor also supports independent analytical controls;
    # such a value is not automatically a member of the finite search domain.
    row = m.evaluate(dict(cfg["seed"], width_m=0.219))
    assert row["variables"]["width_m"] == 0.219


@pytest.mark.parametrize("budget", [0, True, 4097, 1.5])
def test_invalid_search_budget(budget):
    with pytest.raises(ValueError):
        m.search(budget=budget)


def test_non_finite_geometry_rejected():
    cfg = json.loads(m.SPACE.read_text())
    v = deepcopy(cfg["seed"])
    v["plate_m"] = float("nan")
    with pytest.raises(ValueError, match="finite"):
        m.evaluate(v)
