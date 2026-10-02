"""Civil option comparisons and actual-configuration mass checks."""
from __future__ import annotations

import math
import hashlib
import json

from .decked_pi import approx_mass_kg

DETAIL_MASSES = ("net_diaphragms", "reinforcement_adjustment", "prestress_steel",
                 "anchorages", "embedded_lifting_hardware", "curbs_and_attachments",
                 "retained_temporary_works")
RIGGING_MASSES = ("slings", "spreader", "hook_and_blocks")


def nonnegative(value, name):
    if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
        raise ValueError(f"{name} must be finite and non-negative")
    return float(value)


def lifting_budget(span_m: float, masses: dict, lift: dict, planning_target_kg=75_000.0, *, product_deviation: dict | None = None) -> dict:
    """No credit for unknown mass or nominal crane tonnage.

    The bare 2500 kg/m3 envelope already includes a bulk density allowance.
    Reinforcement_adjustment is the documented net adjustment to that basis;
    do not add the full steel mass while retaining displaced concrete mass.
    Diaphragms similarly use only additional volume outside the bare section.
    """
    bare = approx_mass_kg(span_m)
    target = nonnegative(planning_target_kg, "planning target")
    if target <= 0: raise ValueError("member weight target must be positive")
    missing = [k for k in (*DETAIL_MASSES, *RIGGING_MASSES) if masses.get(k) is None]
    known = {k: nonnegative(masses[k], k) for k in (*DETAIL_MASSES, *RIGGING_MASSES) if masses.get(k) is not None}
    required_lift = ("equipment_id", "chart_reference", "configuration", "radius_m", "capacity_at_radius_kg",
                     "dynamic_factor", "permitted_utilisation", "review_reference", "support_check_reference",
                     "stability_check_reference", "mass_basis_reference")
    missing += [f"lift.{k}" for k in required_lift if lift.get(k) is None or lift.get(k) == ""]
    minimum = bare + sum(known.get(k, 0) for k in DETAIL_MASSES)
    if not math.isfinite(minimum): raise ValueError("mass budget overflow")
    result = {"bare_mass_kg": bare, "known_member_mass_kg": minimum,
              "planning_target_kg": target, "bare_margin_kg": target - bare,
              "missing_inputs": missing, "complete_member_mass_kg": None,
              "lift_demand_kg": None, "permitted_capacity_kg": None, "lifting_check_passed": False,
              "member_target_met": None, "equipment_capacity_met": False,
              "product_envelope_accepted": False, "controlled_deviation_accepted": False, "overall_accepted": False,
              "status": "blocked-incomplete-mass-or-lift"}
    if missing: return result
    capacity = nonnegative(lift["capacity_at_radius_kg"], "capacity")
    radius = nonnegative(lift["radius_m"], "radius")
    factor = nonnegative(lift["dynamic_factor"], "dynamic factor")
    utilisation = nonnegative(lift["permitted_utilisation"], "permitted utilisation")
    if capacity <= 0 or radius <= 0 or factor < 1 or not 0 < utilisation <= 1:
        raise ValueError("invalid reviewed lifting configuration")
    demand = (minimum + sum(known[k] for k in RIGGING_MASSES)) * factor
    permitted = capacity * utilisation
    if not all(math.isfinite(v) for v in (minimum, demand, permitted)): raise ValueError("mass budget overflow")
    basis_hash = hashlib.sha256(json.dumps({"span_m":float(span_m),"target_kg":target,"masses_kg":known},sort_keys=True,separators=(",", ":")).encode()).hexdigest()
    member_met, capacity_met = minimum <= target, demand <= permitted
    deviation = product_deviation or {}
    reviewed = (deviation.get("decision") == "accepted" and all(deviation.get(k) for k in ("engineer","checker","signed_at","controlled_reference","rationale"))
                and deviation.get("engineer") != deviation.get("checker") and deviation.get("mass_budget_sha256") == basis_hash)
    product_accepted = member_met or reviewed
    overall = product_accepted and capacity_met
    result.update(complete_member_mass_kg=minimum, lift_demand_kg=demand, permitted_capacity_kg=permitted,
                  mass_budget_sha256=basis_hash, member_target_met=member_met, equipment_capacity_met=capacity_met,
                  product_envelope_accepted=product_accepted, controlled_deviation_accepted=reviewed,
                  overall_accepted=overall, lifting_check_passed=overall,
                  status="configuration-check-passed" if overall else "member-target-exceeded" if not product_accepted else "configuration-capacity-exceeded")
    return result


def compare_foundations(candidates: list[str], comparisons: list[dict], site: dict) -> dict:
    """Return feasible candidates only; an engineer's reviewed comparison selects."""
    required = ("groundwater", "chemistry", "liquefaction", "scour", "utilities", "construction_access",
                "axial_demand_kN", "lateral_demand_kN", "settlement_limit_mm", "differential_settlement_limit_mm")
    missing = [k for k in required if site.get(k) is None or site.get(k) == ""]
    result = {"selected_id": None, "feasible_candidates": [], "missing_site_inputs": missing,
              "state": "site-comparison-required"}
    if missing: return result
    actions = {k: nonnegative(site[k], k) for k in required if k.endswith(("_kN", "_mm"))}
    if {r.get("id") for r in comparisons} != set(candidates) or len(comparisons) != len(candidates):
        raise ValueError("compare every foundation candidate exactly once")
    for row in comparisons:
        values = {k: nonnegative(row[k], k) for k in ("axial_capacity_kN", "lateral_capacity_kN", "settlement_mm", "differential_settlement_mm")}
        if (values["axial_capacity_kN"] >= actions["axial_demand_kN"] and values["lateral_capacity_kN"] >= actions["lateral_demand_kN"]
            and values["settlement_mm"] <= actions["settlement_limit_mm"] and values["differential_settlement_mm"] <= actions["differential_settlement_limit_mm"]
            and all(row.get(k) is True for k in ("constructable", "chemistry_compatible", "liquefaction_checked", "scour_checked"))
            and row.get("calculation_reference")):
            result["feasible_candidates"].append(row["id"])
    selection = site.get("selection_review", {})
    if (selection.get("selected_id") in result["feasible_candidates"] and selection.get("decision") == "accepted"
        and all(selection.get(k) for k in ("engineer", "checker", "signed_at", "controlled_reference", "comparison_rationale"))
        and selection["engineer"] != selection["checker"]):
        result.update(selected_id=selection["selected_id"], state="reviewed-site-selection")
    return result
