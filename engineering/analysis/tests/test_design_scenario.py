"""Scenario coverage and computational/physical acceptance boundaries."""

from copy import deepcopy
import json

import pytest

from engineering.generative_design import coverage, design_scenario as scenario


@pytest.fixture(scope="module")
def current_plan():
    return scenario.plan()


def raw_candidate():
    return {
        "id": "adapter-beam-1",
        "work_package_ids": ["CIV-FRP-100"],
        "component_ids": ["OSR-TYPE-D36A7871D9B7"],
        "variables": {"depth_mm": 1600, "web_mm": 160},
        "geometry": {"detail": "end block and two webs"},
        "materials": {"concrete": "unaccepted planning material"},
        "connections": {"bearing": "proposal"},
        "manufacturing": {"route": "precast-prestressed"},
        "objectives": {"concrete_m3": 27.4},
        "checks": [
            {
                "id": "stress",
                "state": "pass",
                "value": 8.0,
                "limit": 12.0,
                "units": "MPa",
            },
            {
                "id": "supplier-anchorage",
                "state": "unknown",
                "reason": "Actual anchorage configuration absent",
            },
        ],
        "engineering_design_complete": False,
        "manufacturing_release": False,
        "physical_release": False,
    }


def normalized(raw=None):
    return scenario.exchange_candidate(
        raw or raw_candidate(),
        context={"configuration_id": "six-car-provisional"},
        iteration=0,
        parent_candidate_ids=[],
        source_hashes={
            "engineering/generative_design/data/design-scenario.json": coverage.sha(
                scenario.CONTRACT
            )
        },
        producer_agent="civil-detail-worker",
        package_ids={"CIV-FRP-100"},
    )


def test_exact_source_qualified_inventory_and_dependencies(current_plan):
    scope = json.loads(coverage.SCOPE.read_text())
    original = {p["id"]: p for p in scope["work_packages"]}
    rows = current_plan["work_packages"]
    assert len(rows) == len(original) == 63
    assert {p["id"] for p in rows} == set(original)
    for row in rows:
        prior = original[row["id"]]
        assert row["authoritative_sources"] == prior["authoritative_sources"]
        assert row["dependencies"] == prior["dependencies"]
        assert row["required_gates"] == prior["required_gates"]
        assert row["original_completion_predicate"] == prior["completion_predicate"]
        assert {(r["source"], r["id"]) for r in row["components"]} == {
            (r["path"], identifier)
            for r in prior["authoritative_sources"]
            for identifier in r["ids"]
        }
        assert row["generate"] and row["evaluate"] and row["external_actions"]
        assert row["completion_artifacts"] and row["next_action"]
        assert row["owner_role"] != row["critic_role"]
        assert row["status"] == "open"
        assert all(
            row[k] is False
            for k in ("design_complete", "physical_release", "manufacturing_release")
        )
    assert current_plan["counts"]["completed_packages"] == 0
    assert current_plan["inventory_audit"]["inventory_coverage_verified"] is True


def test_actual_manufacturing_and_inspection_work_is_exhaustively_allocated(
    current_plan,
):
    rows = current_plan["work_packages"]
    audit = current_plan["manufacturing_audit"]
    counts = audit["counts"]
    assert (
        counts["required_production_artifacts"]
        == counts["missing_or_unissued_production_artifacts"]
        == 472
    )
    assert counts["inspection_characteristics"] == 416
    assert counts["actual_inspection_result_records"] == 0
    assert counts["drawing_definitions"] == 47
    assert counts["issued_drawing_references"] == 0
    assert {
        r["artifact_id"] for p in rows for r in p["production_artifact_requests"]
    } == {r["id"] for r in audit["artifact_requests"]}
    assert {r["id"] for p in rows for r in p["inspection_characteristics"]} == {
        r["id"] for r in audit["inspection_characteristics"]
    }
    assert {
        r["product_id"] for p in rows for r in p["supplier_configuration_requests"]
    } == {r["product_id"] for r in audit["supplier_configuration_requests"]}
    assert not current_plan["unallocated_artifact_ids"]
    assert not current_plan["unallocated_inspection_ids"]
    definitions = {
        d.get("drawing_id", d.get("id")) for p in rows for d in p["drawing_definitions"]
    }
    assert {d["drawing_id"] for d in audit["drawings"]} <= definitions
    assert (
        len(definitions) > 47
    )  # Includes the separately controlled civil definitions.


def test_plan_binds_inputs_and_has_finite_stop_resume_contract(current_plan):
    for path, digest in current_plan["source_hashes"].items():
        assert coverage.sha(coverage.local(path)) == digest
    contract = current_plan["contract"]
    assert contract["maximum_future_orchestration_review_passes"] == 4
    assert contract["feedback_evaluation_budget_per_context"] == {
        "default": 256,
        "minimum": 1,
        "maximum": 512,
    }
    assert set(contract["execution_bounds"]) == {
        "current_execution",
        "future_pass",
        "feedback_generation",
        "resume",
        "standalone_adapters",
    }
    assert set(contract["stopping"]) == {
        "computationally_rejected",
        "held_external_input",
        "bounded_search_exhausted",
        "stagnated",
        "resume",
        "physical_release",
    }
    assert contract["schedule"]["maximum_concurrent_agents"] == 4
    assert all(r["may_approve_own_work"] is False for r in contract["roles"].values())


def test_exchange_preserves_actual_scope_geometry_and_unknowns():
    raw = raw_candidate()
    candidate = normalized(raw)
    assert candidate["adapter_raw"] == raw
    assert candidate["component_ids"] == raw["component_ids"]
    assert candidate["work_package_ids"] == raw["work_package_ids"]
    assert candidate["state"] == "held-external-input"
    assert candidate["unknowns"] == ["supplier-anchorage"]
    assert candidate["manufacturing"]["drawing_state"] == "proposal-unissued"
    assert candidate["checks"][0]["evidence_ref"] == "#/adapter_raw/checks/0"
    changed = deepcopy(candidate)
    changed["iteration"] = 3
    assert scenario.candidate_id(changed) == candidate["id"]
    changed["parameters"]["depth_mm"] += 1
    assert scenario.candidate_id(changed) != candidate["id"]


@pytest.mark.parametrize(
    "field",
    ["engineering_design_complete", "manufacturing_release", "physical_release"],
)
def test_adapter_cannot_smuggle_release(field):
    raw = raw_candidate()
    raw[field] = True
    with pytest.raises(ValueError, match="cannot claim"):
        normalized(raw)


def test_exchange_never_invents_missing_coverage_or_configuration():
    raw = raw_candidate()
    del raw["component_ids"]
    with pytest.raises(ValueError, match="actual package and component"):
        normalized(raw)
    raw = raw_candidate()
    raw["work_package_ids"] = ["UNCONTROLLED-PACKAGE"]
    with pytest.raises(ValueError, match="known unique"):
        normalized(raw)


def test_unknowns_cannot_be_promoted_to_computational_solution_or_physical_signoff():
    candidate = normalized()
    candidate["state"] = "computational-solution"
    with pytest.raises(ValueError, match="unknown or failed"):
        scenario.validate_candidate(candidate)
    candidate = normalized()
    candidate["manufacturing"]["inspection_state"] = "performed"
    with pytest.raises(ValueError, match="cannot authenticate"):
        scenario.validate_candidate(candidate)


def test_failure_and_its_evidence_are_retained():
    raw = raw_candidate()
    raw["checks"][0]["state"] = "fail"
    candidate = normalized(raw)
    assert candidate["state"] == "computationally-rejected"
    assert candidate["checks"][0]["value"] == 8.0
    result = scenario.transition(candidate, "bounded-search-exhausted")
    assert result["checks"] == candidate["checks"]
    with pytest.raises(ValueError, match="invalid design candidate"):
        scenario.transition(result, "generated")


def test_independent_critic_cannot_be_producer_or_prior_contributor():
    candidate = normalized()
    checks = [
        {
            "id": "independent-unit-balance",
            "state": "pass",
            "evidence_ref": "#/independent/unit-balance",
        }
    ]
    with pytest.raises(ValueError, match="must not produce"):
        scenario.independent_critique(
            candidate, critic_agent=candidate["producer_agent"], checks=checks
        )
    with pytest.raises(ValueError, match="must not produce"):
        scenario.independent_critique(
            candidate,
            critic_agent="prior-helper",
            checks=checks,
            contributing_agents=["prior-helper"],
        )
    review = scenario.independent_critique(
        candidate, critic_agent="independent-numerical-worker", checks=checks
    )
    assert review["computational_challenge_passed"] is True
    assert review["independent_engineering_review_performed"] is False
    assert review["physical_release"] is False
    changed = deepcopy(candidate)
    changed["checks"][0]["value"] = 7.5
    other = scenario.independent_critique(
        changed, critic_agent="independent-numerical-worker", checks=checks
    )
    assert other["candidate_sha256"] != review["candidate_sha256"]


def test_nonfinite_numerical_claim_is_rejected():
    raw = raw_candidate()
    raw["checks"][0]["value"] = float("nan")
    with pytest.raises(ValueError):
        normalized(raw)
