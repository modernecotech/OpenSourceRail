"""Model-based Class C costs complete declared scopes without closing gates."""
from copy import deepcopy

import pytest

from engineering.design_search import (
    design_grammar, model_cost, railway_bundle, railway_campaign,
    system_inventory, system_motion,
)
from engineering.station_rail import ROOT


def _evaluate(family):
    body = design_grammar.initial_candidates()[0]
    bundle = railway_bundle.materialize(body, family=family, root=ROOT)
    spec = railway_campaign.specification(ROOT)
    inventory = system_inventory.evaluate(
        body, bundle_id=bundle["candidate_id"], source_root=ROOT,
        comparison_context=spec["experiment"],
        component_substitutions=bundle["component_substitutions"],
        extra_equipment_tasks=bundle["unweighed_architecture_equipment"],
    )
    architecture = railway_bundle.assess_architecture(bundle)
    propulsion = railway_campaign.propulsion(bundle, architecture)
    motion = system_motion.evaluate(bundle, available_map=None)
    civil = railway_bundle.assess_civil(bundle)
    estimate = model_cost.evaluate(bundle, inventory, architecture, propulsion, motion, civil, root=ROOT)
    return bundle, inventory, estimate


def test_candidate_costs_quantify_all_scopes_and_keep_release_gates_open():
    bundle, inventory, estimate = _evaluate("P1")

    assert estimate["candidate_id"] == bundle["candidate_id"]
    assert estimate["model_cost_complete_for_declared_case"] is True
    assert estimate["model_cost_missing_scopes"] == []
    assert set(estimate["scope_totals_iqd"]) == set(model_cost.SCOPES)
    assert all(values[0] > 0 and values == sorted(values)
               for values in estimate["scope_totals_iqd"].values())
    assert estimate["currency"] == "IQD"
    assert estimate["estimate_class"] == "C"
    assert estimate["rate_evidence_summary"]["actual_supplier_quotes"] == 0
    assert estimate["model_based_installed_CAPEX_iqd"] == sorted(estimate["model_based_installed_CAPEX_iqd"])
    assert estimate["model_based_whole_life_NPV_iqd"] == sorted(estimate["model_based_whole_life_NPV_iqd"])
    assert estimate["annual_operations_iqd"][1] > 0
    assert estimate["production_plan"]["required_parallel_workcells"][1] > 0
    assert estimate["physical_mass_complete"] is False
    assert estimate["physical_journey_completed"] is False
    assert estimate["procurement_ready"] is False
    assert estimate["physical_or_safety_accepted"] is False
    assert all(line["candidate_id"] == bundle["candidate_id"] and line["source_ids"]
               for line in estimate["cost_line_items"])
    assert inventory["complete_installed_mass_kg"] is None


def test_wheel_traction_and_laminate_alternatives_are_costed_in_their_own_scopes():
    wheel_bundle, _, wheel = _evaluate("P6")
    lim_bundle, _, lim = _evaluate("P7")
    wheel_keys = {line["line_key"] for line in wheel["cost_line_items"]}
    lim_keys = {line["line_key"] for line in lim["cost_line_items"]}

    assert wheel_bundle["candidate_id"] != lim_bundle["candidate_id"]
    assert "unweighed-architecture-equipment-package" in wheel_keys
    assert "unlocated-wayside-propulsion-package" not in wheel_keys
    assert "traction-converter-capacity" not in wheel_keys
    assert "unlocated-wayside-propulsion-package" in lim_keys
    assert "unweighed-architecture-equipment-package" in lim_keys
    assert wheel["scope_totals_iqd"]["stations-power"][1] > 0
    assert lim["scope_totals_iqd"]["rolling-stock"][1] > 0


def test_cost_comparison_is_same_service_and_rejects_mixed_candidate_inputs():
    bundle, inventory, first = _evaluate("P1")
    _, _, second = _evaluate("P6")
    comparison = model_cost.compare([first, second])
    assert comparison["integrated_winner"] is None
    assert comparison["selected_reference_changed"] is False
    assert set(comparison["nondominated_candidate_ids"]) <= {
        first["candidate_id"], second["candidate_id"]
    }

    wrong_inventory = deepcopy(inventory)
    wrong_inventory["candidate_id"] = "f" * 64
    architecture = railway_bundle.assess_architecture(bundle)
    propulsion = railway_campaign.propulsion(bundle, architecture)
    motion = system_motion.evaluate(bundle, available_map=None)
    civil = railway_bundle.assess_civil(bundle)
    with pytest.raises(ValueError, match="Mixed candidate"):
        model_cost.evaluate(bundle, wrong_inventory, architecture, propulsion, motion, civil, root=ROOT)

    different_service = deepcopy(second)
    different_service["corridor_basis"]["offered_capacity_pphpd"] += 1
    different_service["evaluation_id"] = model_cost.identity(
        {key: value for key, value in different_service.items() if key != "evaluation_id"})
    with pytest.raises(ValueError, match="Equal currency, cost assumptions, route and nominal service"):
        model_cost.compare([first, different_service])
