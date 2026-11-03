"""Physics-aware parent opportunities without qualification or unknown-as-zero."""
from copy import deepcopy

import pytest

from engineering.design_search import (design_grammar as g, design_portfolio, model_cost,
    native_refinement, native_search, search_feedback as f)
from engineering.station_rail.common import digest, identity


class NoNative:
    def archive(self, *args, **kwargs):
        raise AssertionError("Small feedback cohorts must not invoke a native process")


def reseal(value, key):
    value[key] = identity({k: v for k, v in value.items() if k != key})
    return value


@pytest.fixture(scope="module")
def evidence():
    assumptions = model_cost.assumptions()
    candidates, rows, assessments = [], [], []
    for wall, braced in ((0.006, True), (0.010, True), (0.006, False)):
        candidate = g.build(dict(g.parameters(), chord_wall_m=wall, braced=braced))
        candidates.append(candidate)
        assessment = native_refinement.assess(candidate)
        assessments.append(assessment)
        cost = design_portfolio._factory_gate_stock_estimate(candidate, assumptions, g.ROOT if hasattr(g, "ROOT") else native_search.ROOT)
        sources = design_portfolio.sources()
        request = dict(candidate_id=candidate["candidate_id"], definition_id=candidate["definition_id"],
            fidelity=0, requirements=candidate["requirement_revision"], assumption_id=assumptions["assumption_id"], evaluator_sources=sources)
        rows.append(reseal(dict(candidate_id=candidate["candidate_id"], definition_id=candidate["definition_id"], request=request,
            descriptor=dict(family=candidate["parameters"]["family"], topology="reference"),
            metrics=dict(nominal_stock_kg=sum(p["mass_kg"] for p in candidate["parts"]),
                factory_gate_base_iqd=cost["scenarios_iqd"]["base"], factory_process_hours=cost["process_hours"]["base"]),
            cost_estimate=cost, execution="completed", fidelity=0, engineering_screen="unknown",
            complete_installed_mass_kg=None, complete_installed_cost_iqd=None,
            **{k: False for k in ("physical_accepted", "engineering_accepted", "configuration_adopted", "manufacturing_release",
                "operating_release", "physical_journey_completed", "selected_reference_changed")}), "evaluation_id"))
    epoch = dict(design_portfolio.sources())
    for assessment in assessments:
        epoch.update(assessment["source_sha256"])
    epoch.update(f.LOADED)
    observations = [dict(candidate_id=row["candidate_id"], parent_evaluation_id=row["evaluation_id"],
        comparison_context_id=identity(dict(policy="normal46-own-accounted-sprung-mass")), assessment=assessment)
        for row, assessment in zip(rows, assessments)]
    return candidates, rows, observations, epoch


def make(evidence, **options):
    _, rows, observations, epoch = deepcopy(evidence)
    return f.plan(NoNative(), rows, observations, source_sha256=epoch, **options)


def test_cost_dominated_but_stiffer_supported_candidate_still_receives_parent_priority(evidence):
    _, rows, observations, _ = evidence
    result = make(evidence)
    thin, thick, held = rows
    assert thick["metrics"]["nominal_stock_kg"] > thin["metrics"]["nominal_stock_kg"]
    assert thick["metrics"]["factory_gate_base_iqd"] > thin["metrics"]["factory_gate_base_iqd"]
    assert observations[0]["assessment"]["axial_status"] == observations[1]["assessment"]["axial_status"] == f.SUPPORTED
    assert observations[2]["assessment"]["axial_status"] == "graph-mechanism-model-only"
    assert thick["candidate_id"] not in result["cost_archive"]["retained_candidate_ids"]
    assert thick["candidate_id"] in result["axial_archives"][0]["archive"]["retained_candidate_ids"]
    weights = {p["candidate_id"]: p["weight"] for p in result["parents"]}
    assert weights[thick["candidate_id"]] >= 3
    assert weights[held["candidate_id"]] >= 1
    assert len(weights) == 3 and all(1 <= w <= 4 for w in weights.values())
    assert result["coverage"]["held_candidate_ids"] == [held["candidate_id"]]
    assert all(result[k] == v for k, v in f.FLAGS.items())
    assert result["feedback_id"] == identity({k:v for k,v in result.items() if k != "feedback_id"})


def test_unknown_and_unassessed_are_not_zero_displacement_or_whole_body_rejections(evidence):
    _, rows, observations, epoch = deepcopy(evidence)
    observations[1]["assessment"] = None
    result = f.plan(NoNative(), rows, observations[:2], source_sha256=epoch)
    ids = {rows[1]["candidate_id"], rows[2]["candidate_id"]}
    assert set(result["coverage"]["unassessed_candidate_ids"]) == ids
    assert all(p["weight"] >= 1 for p in result["parents"])
    physics_ids = {cid for entry in result["axial_archives"] for cid in entry["archive"]["retained_candidate_ids"]}
    assert not ids & physics_ids
    assert result["coverage"]["held_candidate_ids"] == []
    assert {task["candidate_id"] for task in result["model_tasks"] if task["kind"] == "axial-model-assessment"} == ids


def test_incompatible_contexts_have_separate_axial_archives_and_no_cross_context_front(evidence):
    _, rows, observations, epoch = deepcopy(evidence)
    observations[1]["comparison_context_id"] = identity(dict(policy="another-route-context"))
    result = f.plan(NoNative(), rows, observations, source_sha256=epoch)
    assert len(result["axial_archives"]) == 2
    for group in result["axial_archives"]:
        assert len(group["archive"]["global_front"]) == 1
    assert "Global positive-weight" in result["policy"]["sampling"]


def test_reordered_inputs_reproduce_the_same_plan(evidence):
    _, rows, observations, epoch = deepcopy(evidence)
    a = f.plan(NoNative(), rows, observations, source_sha256=epoch)
    b = f.plan(NoNative(), list(reversed(rows)), list(reversed(observations)), source_sha256=epoch)
    assert a == b


@pytest.mark.parametrize("weight", [1, 2, 3, 4])
def test_weight_cap_is_explicit_and_all_valid_parents_survive(evidence, weight):
    result = make(evidence, maximum_weight=weight)
    assert len(result["parents"]) == 3
    assert all(type(p["weight"]) is int and 1 <= p["weight"] <= weight for p in result["parents"])


@pytest.mark.parametrize("weight", [0, 5, True, 1.5, None])
def test_invalid_weight_cap_rejected(evidence, weight):
    with pytest.raises(ValueError, match="maximum weight"):
        make(evidence, maximum_weight=weight)


@pytest.mark.parametrize("field", ["candidate_id", "definition_id", "requirement_revision"])
def test_consistently_resealed_mixed_assessment_identity_is_rejected(evidence, field):
    _, rows, observations, epoch = deepcopy(evidence)
    observations[0]["assessment"][field] = "0" * 64
    reseal(observations[0]["assessment"], "assessment_id")
    with pytest.raises(ValueError, match="binding differs"):
        f.plan(NoNative(), rows, observations, source_sha256=epoch)


def test_wrong_parent_evaluation_or_metric_is_rejected(evidence):
    _, rows, observations, epoch = deepcopy(evidence)
    observations[0]["parent_evaluation_id"] = "0" * 64
    with pytest.raises(ValueError, match="parent evaluation"):
        f.plan(NoNative(), rows, observations, source_sha256=epoch)
    _, rows, observations, epoch = deepcopy(evidence)
    rows[0]["metrics"]["factory_gate_base_iqd"] += 1
    reseal(rows[0], "evaluation_id")
    observations[0]["parent_evaluation_id"] = rows[0]["evaluation_id"]
    with pytest.raises(ValueError, match="cost metric"):
        f.plan(NoNative(), rows, observations, source_sha256=epoch)


@pytest.mark.parametrize("value", [None, True, float("nan"), -1, 0, 0.01])
def test_forged_or_out_of_domain_supported_ratio_cannot_gain_priority(evidence, value):
    _, rows, observations, epoch = deepcopy(evidence)
    assessment = observations[0]["assessment"]
    assessment["analytical_maximum_member_relative_displacement_to_length"] = value
    if value == value and value is not None:
        reseal(assessment, "assessment_id")
    with pytest.raises(ValueError):
        f.plan(NoNative(), rows, observations, source_sha256=epoch)


def test_stale_source_and_unsealed_assessment_are_rejected(evidence):
    _, rows, observations, epoch = deepcopy(evidence)
    epoch[f.PRODUCER] = "0" * 64
    with pytest.raises(ValueError, match="source"):
        f.plan(NoNative(), rows, observations, source_sha256=epoch)
    _, rows, observations, epoch = deepcopy(evidence)
    observations[0]["assessment"]["axial_reason"] = "changed without seal"
    with pytest.raises(ValueError, match="assessment identity"):
        f.plan(NoNative(), rows, observations, source_sha256=epoch)


def test_one_comparison_context_cannot_mix_normal_passenger_load_policies(evidence):
    _, rows, observations, epoch = deepcopy(evidence)
    observations[1]["assessment"]["load_basis"]["normal_people"] = 47
    reseal(observations[1]["assessment"], "assessment_id")
    with pytest.raises(ValueError, match="load policies"):
        f.plan(NoNative(), rows, observations, source_sha256=epoch)


def test_resealed_supported_diagnostic_cannot_claim_mechanisms_or_physical_acceptance(evidence):
    for field, value in (("mechanism_count", True), ("physical_accepted", True), ("necessary_rigidity_screen", "fail")):
        _, rows, observations, epoch = deepcopy(evidence)
        observations[0]["assessment"]["axial_diagnostic"][field] = value
        reseal(observations[0]["assessment"], "assessment_id")
        with pytest.raises(ValueError, match="graph or domain"):
            f.plan(NoNative(), rows, observations, source_sha256=epoch)
