"""Adverse experiment adoption and actual hierarchy/physics pilot checks."""

from copy import deepcopy
from pathlib import Path
import math
import subprocess

import pytest

from engineering.generative_design import hierarchical_experiments as h


def records():
    context = h.comparison_context(
        "bracket", "carry same support force", ["elastic fit"], ["normal", "adverse"]
    )
    baseline = dict(
        id="old",
        comparison_context=context,
        objectives={
            "mass": dict(
                value=10.0,
                uncertainty=0.01,
                units="kg",
                state="computed",
                basis="Declared fixture exact unit mass",
                evidence_ref="baseline-calculation.json",
            )
        },
    )
    candidate = dict(
        id="new",
        comparison_context=deepcopy(context),
        objectives={
            "mass": dict(
                value=9.0,
                uncertainty=0.01,
                units="kg",
                state="computed",
                basis="Same declared fixture exact unit mass",
                evidence_ref="candidate-calculation.json",
            )
        },
        producer="designer",
        changed_paths=["part.py"],
    )
    policy = dict(
        mandatory_checks=["local"],
        independent_checks=["reference"],
        parent_checks=["assembly"],
        objective_axes=["mass"],
        protected_paths=["tests/", "policy/"],
    )
    evidence = [
        h.evaluation(
            candidate,
            worker=worker,
            checks=[dict(id=check, state="pass", evidence_ref="sha256:" + "a" * 64)],
        )
        for check, worker in [
            ("local", "designer"),
            ("reference", "verifier"),
            ("assembly", "integrator"),
        ]
    ]
    return baseline, candidate, policy, evidence


def promote(baseline, candidate, policy, evidence):
    return h.evaluate_promotion(baseline, candidate, policy, evidence=evidence)


def test_exact_scope_and_every_typed_item_is_evaluated_or_precisely_held():
    value = h.plan()
    assert value["work_package_count"] == 63
    assert value["controlled_component_count"] > 280
    assert h.validate_plan(value)
    assert all(
        item["evaluators"] or item["missing_capability_ids"] for item in value["items"]
    )
    requests = {r["id"]: r for r in value["missing_capabilities"]}
    for item in value["items"]:
        for identity in item["missing_capability_ids"]:
            assert requests[identity]["item_id"] == item["id"]
            assert requests[identity]["missing_inputs"]
            assert requests[identity]["acceptance"]
    assert (
        sum(
            bool(i["evaluators"]) for i in value["items"] if i["kind"] == "work-package"
        )
        == 6
    )


def test_missing_package_or_cyclic_hierarchy_cannot_claim_full_coverage():
    value = h.plan()
    value["items"] = [i for i in value["items"] if i["id"] != "CIV-FRP-100"]
    with pytest.raises(ValueError):
        h.validate_plan(value)
    value = h.plan()
    value["items"][-1]["parents"] = [value["items"][-1]["id"]]
    with pytest.raises(ValueError, match="cyclic"):
        h.validate_plan(value)


def test_experimental_promotion_retains_policy_evidence_ancestry_and_no_release():
    baseline, candidate, policy, evidence = records()
    decision = promote(baseline, candidate, policy, evidence)
    assert decision["disposition"] == "ADOPT-EXPERIMENTAL"
    revision = decision["experimental_revision"]
    assert revision["policy_sha256"] == h.digest(policy)
    assert revision["evidence_sha256"] == h.digest(evidence)
    assert revision["state"] == "experimental-computational-baseline"
    for flag in h.FLAGS:
        assert decision[flag] is revision[flag] is False
    revised_baseline = dict(candidate, revision_id=revision["id"])
    next_candidate = deepcopy(candidate)
    next_candidate["id"] = "third"
    next_candidate["objectives"]["mass"]["value"] = 8.0
    current_evidence = [
        h.evaluation(next_candidate, worker=row["worker"], checks=row["checks"])
        for row in evidence
    ]
    successor = h.evaluate_promotion(
        revised_baseline,
        next_candidate,
        policy,
        evidence=current_evidence,
        history=[revision],
    )
    assert successor["experimental_revision"]["parents"] == [revision["id"]]


@pytest.mark.parametrize(
    "category", ["mandatory_checks", "independent_checks", "parent_checks"]
)
def test_every_required_evidence_class_is_mandatory(category):
    baseline, candidate, policy, evidence = records()
    identity = policy[category][0]
    evidence = [row for row in evidence if row["checks"][0]["id"] != identity]
    decision = promote(baseline, candidate, policy, evidence)
    assert decision["disposition"] == "HOLD"
    assert any(identity in reason for reason in decision["reasons"])


def test_locally_passing_parent_harm_is_rejected():
    baseline, candidate, policy, evidence = records()
    evidence[-1]["checks"][0]["state"] = "fail"
    decision = promote(baseline, candidate, policy, evidence)
    assert decision["disposition"] == "REJECT"
    assert decision["experimental_revision"] is None


def test_unknown_and_timeout_are_inconclusive_even_if_other_checks_pass():
    baseline, candidate, policy, evidence = records()
    evidence[-1]["execution_status"] = "timeout"
    decision = promote(baseline, candidate, policy, evidence)
    assert decision["disposition"] == "HOLD"
    evidence[-1]["execution_status"] = "completed"
    evidence[-1]["checks"][0]["state"] = "unknown"
    assert promote(baseline, candidate, policy, evidence)["disposition"] == "HOLD"


def test_source_and_context_tampering_rejected():
    baseline, candidate, policy, evidence = records()
    candidate["objectives"]["mass"]["value"] = 8.0
    with pytest.raises(ValueError, match="different candidate"):
        promote(baseline, candidate, policy, evidence)


@pytest.mark.parametrize("field", ["function", "requirements", "scenarios"])
def test_comparisons_require_same_function_requirements_and_scenarios(field):
    baseline, candidate, policy, evidence = records()
    candidate["comparison_context"][field] = "changed acceptance scope"
    evidence = [
        h.evaluation(candidate, worker=row["worker"], checks=row["checks"])
        for row in evidence
    ]
    assert promote(baseline, candidate, policy, evidence)["disposition"] == "HOLD"


def test_self_review_or_contributor_review_cannot_adopt():
    baseline, candidate, policy, evidence = records()
    evidence[1]["worker"] = candidate["producer"]
    assert promote(baseline, candidate, policy, evidence)["disposition"] == "HOLD"
    candidate["contributors"] = ["verifier"]
    evidence = [
        h.evaluation(candidate, worker=worker, checks=row["checks"])
        for worker, row in zip(["designer", "verifier", "integrator"], evidence)
    ]
    assert promote(baseline, candidate, policy, evidence)["disposition"] == "HOLD"


def test_uncertainty_unknown_cost_and_objective_regression_cannot_adopt():
    baseline, candidate, policy, evidence = records()
    for value in [9.99, 12.0, None, math.nan]:
        candidate["objectives"]["mass"]["value"] = value
        if isinstance(value, float) and math.isnan(value):
            with pytest.raises(ValueError):
                h.evaluation(candidate, worker="worker", checks=[])
            continue
        current = [
            h.evaluation(candidate, worker=row["worker"], checks=row["checks"])
            for row in evidence
        ]
        assert promote(baseline, candidate, policy, current)["disposition"] == "HOLD"


@pytest.mark.parametrize("path", ["tests/reference.py", "policy/limits.json"])
def test_acceptance_machinery_edits_need_own_review(path):
    baseline, candidate, policy, evidence = records()
    candidate["changed_paths"] = [path]
    evidence = [
        h.evaluation(candidate, worker=row["worker"], checks=row["checks"])
        for row in evidence
    ]
    decision = promote(baseline, candidate, policy, evidence)
    assert decision["disposition"] == "HOLD"
    assert "own independent review" in decision["reasons"][0]


def test_revision_graph_cannot_be_cyclic_or_reference_unknown_parent():
    baseline, candidate, policy, evidence = records()
    for history in [
        [dict(id="a", parents=["b"]), dict(id="b", parents=["a"])],
        [dict(id="a", parents=["absent"])],
    ]:
        with pytest.raises(ValueError):
            h.evaluate_promotion(
                baseline, candidate, policy, evidence=evidence, history=history
            )


def test_empty_evidence_check_classes_duplicate_check_or_missing_reference_rejected():
    baseline, candidate, policy, evidence = records()
    evidence.append(deepcopy(evidence[0]))
    with pytest.raises(ValueError, match="unique"):
        promote(baseline, candidate, policy, evidence)
    evidence.pop()
    evidence[0]["checks"][0].pop("evidence_ref")
    with pytest.raises(ValueError, match="actual check evidence"):
        promote(baseline, candidate, policy, evidence)
    policy["independent_checks"] = []
    with pytest.raises(ValueError):
        promote(baseline, candidate, policy, [])


def step(state):
    return dict(
        state={"mass": state["mass"] / 2},
        checks=[dict(id="balance", state="pass", evidence_ref="calculation.json")],
    )


def test_coupled_loop_converges_with_explicit_units_scales_and_residuals():
    result = h.coupled_iteration(
        {"mass": 1.0}, step, scales={"mass": 1.0}, tolerance=0.01, max_iterations=8
    )
    assert result["status"] == "converged-declared-interfaces"
    assert len(result["trace"]) == 7
    assert result["trace"][-1]["normalized_residual"] <= 0.01
    assert result["physical_convergence_established"] is False


def test_coupled_unconverged_failure_and_unknown_do_not_pass():
    result = h.coupled_iteration(
        {"mass": 1.0}, step, scales={"mass": 1.0}, tolerance=1e-12, max_iterations=2
    )
    assert result["status"] == "budget-exhausted"
    for state, expected in [
        ("fail", "rejected-interface-failure"),
        ("unknown", "HOLD-missing-capability-or-input"),
    ]:
        result = h.coupled_iteration(
            {"mass": 1.0},
            lambda x: dict(
                state=x,
                checks=[dict(id="coupling", state=state, evidence_ref="actual")],
            ),
            scales={"mass": 1.0},
        )
        assert result["status"] == expected
    with pytest.raises(ValueError):
        h.coupled_iteration({"mass": 1.0}, step, scales={"force": 1.0})


def test_software_proposals_target_actual_existing_defect_and_no_acceptance_edits():
    rows = h.software_proposals(
        subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=h.ROOT, text=True
        ).strip()
    )
    assert len(rows) == 3
    assert rows[0]["patch"] == ""
    assert "+" in rows[1]["patch"]
    assert "type(v) in (int, float)" in rows[1]["patch"]
    assert "maximum_abs_deflection_m=0.0" in rows[2]["patch"]
    assert all(
        row["allowed_paths"] == ["engineering/generative_design/mechanical_detail.py"]
        for row in rows
    )
    assert all(row["claimed_performance_improvement"] is None for row in rows)


@pytest.fixture(scope="module")
def pilot():
    return h.engineering_pilot()


def test_actual_component_pass_cannot_hide_parent_frame_or_foundation_failures(pilot):
    assert pilot["mechanical"]["ordinary"]["failed_check_ids"] == []
    for case in pilot["adverse_cases"]:
        assert case["locally_passing"]
        assert case["disposition"] == "REJECT"
    assert "intersection_weld_nominal_shear" in " ".join(
        pilot["adverse_cases"][0]["parent_failed_check_ids"]
    )
    assert any(
        row["state"] == "fail" for row in pilot["adverse_cases"][1]["parent_checks"]
    )


def test_complete_bay_has_both_supports_and_explicit_missing_model_hold(pilot):
    bay = pilot["complete_bay"]
    assert len(bay["declared_supports"]) == len(bay["support_records"]) == 2
    assert bay["complete_bay_evaluator_executed"] is False
    assert bay["disposition"] == "HOLD"
    assert len(bay["missing_capabilities"]) >= 4
    assert pilot["civil"]["repaired"]["failed_checks"] == []
    assert pilot["coupling"]["status"] == "converged-declared-interfaces"
    assert pilot["coupling"]["physical_convergence_established"] is False


def test_adverse_check_cannot_be_omitted_from_policy_to_force_adoption():
    baseline, candidate, policy, evidence = records()
    evidence[0]["checks"].append(
        dict(id="omitted-danger", state="fail", evidence_ref="actual-calculation.json")
    )
    assert promote(baseline, candidate, policy, evidence)["disposition"] == "REJECT"


def test_objective_without_source_basis_creates_work_request():
    baseline, candidate, policy, evidence = records()
    candidate["objectives"]["mass"].pop("basis")
    evidence = [
        h.evaluation(candidate, worker=row["worker"], checks=row["checks"])
        for row in evidence
    ]
    result = promote(baseline, candidate, policy, evidence)
    assert result["disposition"] == "HOLD"
    assert result["work_requests"][0]["capability"] == "comparable objective mass"


def test_duplicate_policy_checks_and_blank_workers_rejected():
    baseline, candidate, policy, evidence = records()
    policy["parent_checks"].append("local")
    with pytest.raises(ValueError, match="distinct"):
        promote(baseline, candidate, policy, evidence)
    with pytest.raises(ValueError, match="worker identity"):
        h.evaluation(candidate, worker="", checks=[])


def test_unrelated_revision_history_cannot_become_baseline_ancestry():
    baseline, candidate, policy, evidence = records()
    revision = promote(baseline, candidate, policy, evidence)["experimental_revision"]
    result = h.evaluate_promotion(
        baseline, candidate, policy, evidence=evidence, history=[revision]
    )
    assert result["disposition"] == "HOLD"
    baseline["revision_id"] = revision["id"]
    with pytest.raises(ValueError, match="exact revision"):
        h.evaluate_promotion(
            baseline, candidate, policy, evidence=evidence, history=[revision]
        )


def test_software_proposals_reject_unknown_git_base_and_noncanonical_changes():
    with pytest.raises(ValueError, match="unavailable"):
        h.software_proposals("a" * 40)
    baseline, candidate, policy, evidence = records()
    candidate["changed_paths"] = ["./tests/bypass.py"]
    evidence = [
        h.evaluation(candidate, worker=row["worker"], checks=row["checks"])
        for row in evidence
    ]
    with pytest.raises(ValueError, match="canonical"):
        promote(baseline, candidate, policy, evidence)
