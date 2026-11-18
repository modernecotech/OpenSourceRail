"""Baghdad two-track precast viaduct quantity and planning-cost comparison.

The 10 m selected v0.7 beam is a source diagnostic, not an accepted Baghdad
structure. Longer beams and common piers are new physical candidates. This
model keeps their material/handling extrapolation and pricing assumptions
visible so a route-level system model can compare them without claiming FEM,
ground, crosshead, or erection approval.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
from math import ceil, isfinite
import json
from typing import Mapping


SCHEMA = "osr-baghdad-viaduct-comparison/1"
SUPPORTED_SPANS_M = (10, 20, 25, 30)
PARENT_BEAM_PHYSICAL_ID = "34161ebcca2e35599cc5896a23b763cc35d3809107dd6b0c9f2ff98516a68160"
PARENT_NATIVE_EVALUATION_ID = "e8856048364ad54e5c8ba214567c5a21c457c47293cccda219a8df5fe1ac6cee"
PARENT_NATIVE_RESULT_SHA256 = "ffe1bc03bdad9245bb8e7754455f9a4cdcacfef066cf883df009e95c4656c363"
PARENT_BARE_BEAM_T = 29.964382
PARENT_HOOK_WITH_ALLOWANCE_T = 37.4554775
BAGHDAD_COMPARATOR_CROWD_TRAIN_T = 201.732


@dataclass(frozen=True)
class PlanningRates:
    """Declared USD allowances; none is a Baghdad supplier quotation."""

    current_elevated_usd_per_route_km: float = 9_000_000
    selected_10m_beam_usd: float = 14_240
    independent_pier_foundation_usd: float = 8_000
    common_pier_crosshead_foundation_usd: float = 20_000
    selected_10m_lift_usd: float = 5_000
    beam_length_price_exponent: float = 1.0
    lift_length_price_exponent: float = 1.0
    factory_beams_per_workday_per_yard: float = 8.0
    erection_lifts_per_workday_per_front: float = 8.0
    workdays_per_year: int = 250


def _identity(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    return sha256(raw).hexdigest()


def _positive(value: object, name: str) -> float:
    if type(value) not in (int, float) or not isfinite(value) or value <= 0:
        raise ValueError(f"Finite positive {name} required")
    return float(value)


def _quantities(lines_km: Mapping[str, float], span_m: int, common_pier: bool) -> dict:
    if not lines_km or len(lines_km) != len(set(lines_km)):
        raise ValueError("Named route lines required")
    rows = []
    for name, km in sorted(lines_km.items()):
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Nonempty line name required")
        km = _positive(km, f"{name} length")
        bays = ceil(km * 1000 / span_m)
        rows.append({"line": name, "route_km": km, "bays": bays,
                     "last_bay_at_most_span_m": span_m,
                     "beams_and_lifts": 2 * bays,
                     "support_nodes": bays + 1,
                     "pier_foundations": bays + 1 if common_pier else 2 * (bays + 1)})
    return {"lines": rows, "route_km": sum(row["route_km"] for row in rows),
            "beam_count": sum(row["beams_and_lifts"] for row in rows),
            "lift_count": sum(row["beams_and_lifts"] for row in rows),
            "support_node_count": sum(row["support_nodes"] for row in rows),
            "pier_foundation_count": sum(row["pier_foundations"] for row in rows),
            "bearing_unit_allowance": 4 * sum(row["beams_and_lifts"] for row in rows)}


def evaluate(
    lines_km: Mapping[str, float], *, span_m: int, common_pier: bool,
    physical_candidate_id: str, rates: PlanningRates = PlanningRates(),
    target_years: float = 5.0,
    civil_start_year: int = 2028,
    first_year_productivity_fraction: float = 0.8,
    later_year_availability_fraction: float = 0.9,
    train_crowd_mass_t: float = BAGHDAD_COMPARATOR_CROWD_TRAIN_T,
) -> dict:
    """Return one source-labelled civil option for an unchanged route/service.

    Every option is costed against the *same* published elevated scope. A
    longer-span beam price and lift price are explicit length-scaling planning
    scenarios, never an inferred structural takeoff or verified saving.
    """
    if span_m not in SUPPORTED_SPANS_M or type(span_m) is not int:
        raise ValueError("Span must be one of 10, 20, 25 or 30 m")
    if type(common_pier) is not bool:
        raise ValueError("common_pier must be Boolean")
    if not physical_candidate_id or not isinstance(physical_candidate_id, str):
        raise ValueError("Explicit physical candidate ID required")
    _positive(target_years, "target years")
    if not float(target_years).is_integer() or type(civil_start_year) is not int:
        raise ValueError("Integral civil window years and start year required")
    _positive(train_crowd_mass_t, "crowd train mass")
    for key, value in asdict(rates).items():
        _positive(value, key)
    _positive(first_year_productivity_fraction, "first year productivity fraction")
    _positive(later_year_availability_fraction, "later year availability fraction")
    if (first_year_productivity_fraction > 1
            or later_year_availability_fraction > 1):
        raise ValueError("Productivity and availability fractions cannot exceed one")
    q = _quantities(lines_km, span_m, common_pier)
    baseline = _quantities(lines_km, 10, False)
    scale = span_m / 10
    # This priced load sensitivity is an explicit planning surrogate. Its
    # proportional scaling does not replace load combinations or a beam design.
    load_ratio = train_crowd_mass_t / BAGHDAD_COMPARATOR_CROWD_TRAIN_T
    beam_price = rates.selected_10m_beam_usd * scale**rates.beam_length_price_exponent * load_ratio
    lift_price = rates.selected_10m_lift_usd * scale**rates.lift_length_price_exponent * load_ratio
    pier_price = ((rates.common_pier_crosshead_foundation_usd if common_pier
                   else rates.independent_pier_foundation_usd) * load_ratio)
    baseline_itemised = (baseline["beam_count"] * rates.selected_10m_beam_usd
                         + baseline["pier_foundation_count"] * rates.independent_pier_foundation_usd
                         + baseline["lift_count"] * rates.selected_10m_lift_usd)
    option_itemised = (q["beam_count"] * beam_price
                       + q["pier_foundation_count"] * pier_price
                       + q["lift_count"] * lift_price)
    published_elevated_scope = q["route_km"] * rates.current_elevated_usd_per_route_km
    direct_civil = published_elevated_scope + option_itemised - baseline_itemised
    if direct_civil <= 0:
        raise ValueError("Planning civil price must remain positive")
    nominal_workdays = target_years * rates.workdays_per_year
    yearly_capacity = [
        {"year": civil_start_year + index,
         "productive_workdays_per_yard_or_front": rates.workdays_per_year * (
             first_year_productivity_fraction if index == 0
             else later_year_availability_fraction)}
        for index in range(int(target_years))
    ]
    effective_workdays = sum(row["productive_workdays_per_yard_or_front"]
                             for row in yearly_capacity)
    factory_beams_per_day = q["beam_count"] / nominal_workdays
    erection_lifts_per_day = q["lift_count"] / nominal_workdays
    factory_yards_without_margin = ceil(q["beam_count"] /
                                       (nominal_workdays * rates.factory_beams_per_workday_per_yard))
    fronts_without_margin = ceil(q["lift_count"] /
                                 (nominal_workdays * rates.erection_lifts_per_workday_per_front))
    factory_yards_with_margin = ceil(q["beam_count"] /
                                    (effective_workdays * rates.factory_beams_per_workday_per_yard))
    fronts_with_margin = ceil(q["lift_count"] /
                              (effective_workdays * rates.erection_lifts_per_workday_per_front))
    same_section_bare_t = PARENT_BARE_BEAM_T * scale * load_ratio
    same_section_hook_t = PARENT_HOOK_WITH_ALLOWANCE_T * scale * load_ratio
    physical = {
        "selected_10m_source_beam_id": PARENT_BEAM_PHYSICAL_ID,
        "selected_10m_native_evaluation_id": PARENT_NATIVE_EVALUATION_ID,
        "selected_10m_native_result_sha256": PARENT_NATIVE_RESULT_SHA256,
        "baghdad_comparator_crowd_train_t": BAGHDAD_COMPARATOR_CROWD_TRAIN_T,
        "candidate_crowd_train_t": train_crowd_mass_t,
        "crowd_load_ratio_planning_surrogate": load_ratio,
        "length_and_load_scaled_material_surrogate_bare_t_per_beam": same_section_bare_t,
        "length_and_load_scaled_hook_surrogate_t_per_beam": same_section_hook_t,
        "same_section_uniform_load_bending_demand_ratio_to_10m": scale**2 * load_ratio,
        "same_section_uniform_load_deflection_demand_ratio_to_10m": scale**4 * load_ratio,
        "uniform_load_ratios_are_preliminary_not_a_train_load_case": True,
        "longer_span_section_and_prestress_redesign_required": span_m > 10,
        "reference_crane_chart_t_at_12m": 60.0,
        "surrogate_hook_below_reference_crane_chart": same_section_hook_t <= 60.0,
        "surrogate_is_a_structural_or_lift_design": False,
        "gross_10m_native_midspan_deflection_m": 0.001576498 if span_m == 10 else None,
        "gross_10m_native_one_rail_twist_rad": 7.043999988349704e-5 if span_m == 10 else None,
        "gross_10m_native_revised_end_reactions_N": [514_683.846, 603_781.846] if span_m == 10 else None,
        "gross_10m_native_service_tension_MPa": -0.106 if span_m == 10 else None,
        "gross_10m_native_transfer_tension_MPa": -0.760 if span_m == 10 else None,
        "gross_10m_native_result_applies_to_baghdad_700_place_train": False,
        "baghdad_moving_load_stress_envelope_verified": False,
        "torsion_and_local_seat_verified": False,
        "prestress_transfer_and_anchorage_verified": False,
        "handling_insert_and_temporary_stability_verified": False,
        "pier_crosshead_and_foundation_verified": False,
        "crane_at_actual_radius_verified": False,
        "road_clearance_and_pier_footprint_mapped": False,
        "site_soil_capacity_kpa": None,
    }
    option_physical_id = _identity({"parent_system_physical_candidate_id": physical_candidate_id,
                                    "span_m": span_m, "common_pier": common_pier,
                                    "train_crowd_mass_t": train_crowd_mass_t})
    result = {
        "schema": SCHEMA,
        "parent_system_physical_candidate_id": physical_candidate_id,
        "civil_option_physical_id": option_physical_id,
        "parent_selected_10m_beam_physical_id": PARENT_BEAM_PHYSICAL_ID,
        "span_m": span_m,
        "common_pier": common_pier,
        "train_crowd_mass_t": train_crowd_mass_t,
        "zero_tunnels": True,
        "zero_underground_stations": True,
        "two_tracks": True,
        "quantities": q,
        "prices": {"basis": "2026 USD planning allowances, not supplier quotations",
                   "rates": asdict(rates), "beam_usd_each": beam_price,
                   "lift_usd_each": lift_price, "pier_foundation_usd_each": pier_price,
                   "published_10m_separate_pier_scope_usd": published_elevated_scope,
                   "baseline_itemised_usd": baseline_itemised,
                   "option_itemised_usd": option_itemised,
                   "changed_elevated_scope_usd": direct_civil,
                   "delta_from_published_elevated_scope_usd": direct_civil - published_elevated_scope,
                   "unchanged_urban_access_drainage_allowance_retained": True,
                   "structural_redesign_and_actual_ground_quote_missing": True},
        "delivery": {"target_years": target_years,
                     "civil_start_year": civil_start_year,
                     "civil_finish_year": civil_start_year + int(target_years) - 1,
                     "first_year_productivity_fraction": first_year_productivity_fraction,
                     "later_year_availability_fraction": later_year_availability_fraction,
                     "nominal_workdays_per_yard_or_front": nominal_workdays,
                     "effective_workdays_per_yard_or_front": effective_workdays,
                     "yearly_capacity": yearly_capacity,
                     "factory_beams_per_workday_needed": factory_beams_per_day,
                     "erection_lifts_per_workday_needed": erection_lifts_per_day,
                     "factory_yards_without_ramp_or_downtime": factory_yards_without_margin,
                     "erection_fronts_without_ramp_or_downtime": fronts_without_margin,
                     "factory_yards_needed_at_declared_rate": factory_yards_with_margin,
                     "erection_fronts_needed_at_declared_rate": fronts_with_margin,
                     "single_yard_workdays": ceil(q["beam_count"] / rates.factory_beams_per_workday_per_yard),
                     "single_erection_front_workdays": ceil(q["lift_count"] / rates.erection_lifts_per_workday_per_front),
                     "additional_yard_and_front_cost_usd": None,
                     "ramp_and_availability_are_planning_assumptions": True,
                     "road_closure_days": None,
                     "factory_shifts_and_crane_availability_verified": False},
        "physical_screen": physical,
        "cost_is_a_structurally_qualified_bid": False,
        "construction_release": False,
    }
    result["evaluation_id"] = _identity(result)
    return result
