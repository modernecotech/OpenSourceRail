"""Controlled LM3 product-level mass closure and lightweighting evidence.

The optimizer carries nine planning categories, while manufacturing is controlled
through individual product rows.  This module joins those two views without
inventing masses from the deliberately simplified product-envelope geometry.
"""

from __future__ import annotations

from collections import Counter
from typing import Protocol, Sequence

from osr_mech.common import ConsistFamily
from osr_mech.design_definition import DesignCandidate, iterate_design_space
from osr_mech.maintenance_interface import lm3_field_recovery_datum

from .baseline import (
    PROMOTED_ENGINEERING_MASS_RESERVE_KG,
    PROMOTED_LIGHT_METRO_TRAINSET_MASS_KG,
    PROMOTED_OPTIMIZER_MASS_SUBTOTAL_KG,
)
from .recovery import LM3_CAR_COUNT, field_recovery_load_cases, recovery_mass_scenarios


CARBODY = "carbody primary structure"
BOGIES = "bogie frames, wheelsets, brakes, and suspension"
TRACTION = "traction motors, gearboxes, and controllers"
BATTERIES = "traction batteries"
HVAC = "roof HVAC"
PV = "roof PV"
AUXILIARIES = "doors, glazing, interior, and auxiliaries"
ENDS = "end cowls and interfaces"
ARTICULATION = "inter-car articulation"

MASS_CATEGORIES = (
    CARBODY,
    BOGIES,
    TRACTION,
    BATTERIES,
    HVAC,
    PV,
    AUXILIARIES,
    ENDS,
    ARTICULATION,
)


class ProductRow(Protocol):
    id: str
    title: str
    route: object
    maturity: object
    quantity_per_trainset: float
    unit: str
    parent: str


def _enum_value(value: object) -> str:
    return str(getattr(value, "value", value))


def mass_responsibility_category(product_id: str) -> str:
    """Map one manifest row to its optimizer mass-responsibility category.

    This is a responsibility map, not a per-product estimate.  Mass may only be
    entered against a row after released CAD, supplier or weighing evidence exists.
    """

    if product_id.startswith("LM3-BDY-"):
        return CARBODY
    if product_id.startswith("LM3-BOG-"):
        return BOGIES
    if product_id in {"LM3-TRC-P010", "LM3-TRC-P020", "LM3-TRC-P030"}:
        return TRACTION
    if product_id == "LM3-TRC-P040" or product_id.startswith("LM3-HV-"):
        return BATTERIES
    if product_id in {"LM3-EXT-P040", "LM3-ROOF-P010", "LM3-ROOF-P030", "LM3-INT-P010"}:
        return HVAC
    if product_id in {"LM3-EXT-P050", "LM3-ROOF-P020", "LM3-ROOF-P040"}:
        return PV
    if product_id.startswith(("LM3-END-", "LM3-CWL-", "LM3-FAS-")):
        return ENDS
    if product_id.startswith("LM3-ART-"):
        return ARTICULATION
    if product_id.startswith(
        ("LM3-EXT-", "LM3-FIX-", "LM3-WIN-", "LM3-DOOR-", "LM3-LGT-", "LM3-FIN-", "LM3-INT-", "LM3-TRC-", "LM3-SAF-", "LM3-AUX-", "LM3-CTRL-")
    ):
        return AUXILIARIES
    raise ValueError(f"no mass-responsibility category for {product_id}")


def _evidence_route(route: str) -> tuple[list[str], str]:
    if route == "MAKE":
        return (
            [
                "released production-solid CAD mass-property report with material, thickness and finish density",
                "first-article calibrated component or completed-subassembly weigh record",
            ],
            "mass-properties engineer + manufacturing quality + design authority",
        )
    return (
        [
            "selected exact supplier configuration mass declaration or certificate with included/excluded scope",
            "calibrated receipt weigh or accepted installed-system reconciliation",
        ],
        "supplier/subsystem engineer + incoming quality + mass-properties engineer",
    )


def _lightest_feasible_candidate(family: ConsistFamily) -> DesignCandidate:
    feasible = (candidate for candidate in iterate_design_space(family).trace if candidate.feasible)
    return min(feasible, key=lambda candidate: (sum(candidate.mass_breakdown_kg.values()), candidate.id))


def _recovery_scenario(scenario_id: str, status: str, train_mass_kg: float) -> dict[str, object]:
    capacity_kn = lm3_field_recovery_datum().portable_cylinder_min_capacity_kn
    car_mass_kg = train_mass_kg / LM3_CAR_COUNT
    cases = []
    for load_case in field_recovery_load_cases():
        reaction_kn = load_case.maximum_point_reaction_kn(car_mass_kg)
        cases.append(
            {
                "load_case_id": load_case.id,
                "required_point_capacity_kn": round(reaction_kn, 2),
                "available_point_capacity_kn": capacity_kn,
                "capacity_margin_kn": round(capacity_kn - reaction_kn, 2),
                "passes_planning_envelope": reaction_kn <= capacity_kn,
            }
        )
    return {
        "id": scenario_id,
        "status": status,
        "train_mass_kg": round(train_mass_kg, 2),
        "mean_car_mass_kg": round(car_mass_kg, 2),
        "load_cases": cases,
    }


def mass_closure_payload(
    candidate: DesignCandidate,
    products: Sequence[ProductRow],
    family: ConsistFamily = ConsistFamily.LIGHT_METRO_3CAR,
) -> dict[str, object]:
    """Build the controlled mass ledger for every product-manifest row."""

    modeled_exact_kg = round(sum(candidate.mass_breakdown_kg.values()), 2)
    if round(modeled_exact_kg) != PROMOTED_OPTIMIZER_MASS_SUBTOTAL_KG:
        raise ValueError("candidate no longer reconciles with the promoted mass subtotal")
    if set(candidate.mass_breakdown_kg) != set(MASS_CATEGORIES):
        raise ValueError("optimizer and mass-responsibility categories have diverged")

    rows: list[dict[str, object]] = []
    for product in products:
        route = _enum_value(product.route)
        evidence_required, authority = _evidence_route(route)
        active = product.quantity_per_trainset > 0
        rows.append(
            {
                "product_id": product.id,
                "title": product.title,
                "route": route,
                "maturity": _enum_value(product.maturity),
                "quantity_per_trainset": product.quantity_per_trainset,
                "unit": product.unit,
                "parent_assembly": product.parent,
                "active_in_reference_configuration": active,
                "mass_responsibility_category": mass_responsibility_category(product.id),
                "mass_evidence_status": "unclosed-evidence-required" if active else "inactive-option-not-weighed",
                "closed_mass_kg": None,
                "evidence_required": evidence_required,
                "closure_authority": authority,
                "closed": False,
            }
        )

    category_counts = Counter(str(row["mass_responsibility_category"]) for row in rows)
    active_counts = Counter(
        str(row["mass_responsibility_category"])
        for row in rows
        if row["active_in_reference_configuration"]
    )
    categories = [
        {
            "category": category,
            "modeled_planning_budget_kg": candidate.mass_breakdown_kg[category],
            "product_row_count": category_counts[category],
            "active_product_row_count": active_counts[category],
            "closed_active_product_row_count": 0,
            "status": "open-product-mass-evidence",
        }
        for category in MASS_CATEGORIES
    ]

    lightest = _lightest_feasible_candidate(family)
    lightest_modeled_kg = round(sum(lightest.mass_breakdown_kg.values()), 2)
    modeled_saving_kg = round(modeled_exact_kg - lightest_modeled_kg, 2)
    lightest_same_reserve_kg = round(lightest_modeled_kg + PROMOTED_ENGINEERING_MASS_RESERVE_KG, 2)
    sensitivity = recovery_mass_scenarios(PROMOTED_LIGHT_METRO_TRAINSET_MASS_KG)
    recovery_scenarios = [
        _recovery_scenario(
            "controlled-planning-tare",
            "controlled design basis; product mass evidence open",
            PROMOTED_LIGHT_METRO_TRAINSET_MASS_KG,
        ),
        _recovery_scenario(
            "lightest-existing-feasible-design-space-with-same-reserve",
            "unpromoted candidate; structural, dynamic, manufacturing and mass closure required",
            lightest_same_reserve_kg,
        ),
        *[
            _recovery_scenario(
                row.id,
                "sensitivity only; no corresponding closed design candidate",
                row.train_mass_kg,
            )
            for row in sensitivity[1:]
        ],
    ]

    return {
        "schema": "org.opensourcerail.lm3-mass-closure.v1",
        "document_revision": "A-DRAFT",
        "release_status": "planning-control-mass-evidence-open",
        "candidate": candidate.id,
        "mass_basis": {
            "modeled_exact_subtotal_kg": modeled_exact_kg,
            "controlled_modeled_subtotal_kg": PROMOTED_OPTIMIZER_MASS_SUBTOTAL_KG,
            "engineering_reserve_kg": PROMOTED_ENGINEERING_MASS_RESERVE_KG,
            "controlled_planning_tare_kg": PROMOTED_LIGHT_METRO_TRAINSET_MASS_KG,
            "product_geometry_mass_use": "prohibited until production solids have released materials, thicknesses and included-scope fidelity",
        },
        "coverage": {
            "product_rows": len(rows),
            "active_product_rows": sum(bool(row["active_in_reference_configuration"]) for row in rows),
            "mapped_product_rows": len(rows),
            "closed_active_product_rows": 0,
            "category_count": len(categories),
            "categories_reconciled_to_controlled_subtotal": round(sum(float(row["modeled_planning_budget_kg"]) for row in categories)) == PROMOTED_OPTIMIZER_MASS_SUBTOTAL_KG,
        },
        "categories": categories,
        "product_rows": rows,
        "lightweighting": {
            "selected_modeled_mass_kg": modeled_exact_kg,
            "lightest_existing_feasible_candidate": lightest.id,
            "lightest_existing_feasible_modeled_mass_kg": lightest_modeled_kg,
            "modeled_saving_kg": modeled_saving_kg,
            "modeled_saving_percent": round(100.0 * modeled_saving_kg / modeled_exact_kg, 2),
            "lightest_candidate_with_unchanged_reserve_kg": lightest_same_reserve_kg,
            "controlled_tare_comparison_saving_kg": round(PROMOTED_LIGHT_METRO_TRAINSET_MASS_KG - lightest_same_reserve_kg, 2),
            "candidate_parameters": {
                "car_length_m": lightest.parameters.car_length_m,
                "structure_gauge": lightest.parameters.structure_gauge,
                "bogie_frame_gauge": lightest.parameters.bogie_frame_gauge,
                "motor_id": lightest.parameters.motor_id,
                "battery_id": lightest.parameters.battery_id,
                "hvac_id": lightest.parameters.hvac_id,
                "pv_modules_per_car": lightest.parameters.pv_modules_per_car,
            },
            "decision": "retain the 78,750 kg controlled planning tare; the lighter candidate is a study option, not achieved mass",
            "promotion_gates": [
                "close every active product row with accepted CAD, supplier and/or calibrated weigh evidence",
                "reconcile individual-car and complete-train weights, axle loads and longitudinal/vertical centre of gravity",
                "repeat structural, crash, fatigue, dynamics, braking, thermal and manufacturability substantiation for changed gauges",
                "approve reserve drawdown and configuration change through the design authority",
            ],
        },
        "recovery_load_case_link": {
            "portable_cylinder_envelope_kn_per_point": lm3_field_recovery_datum().portable_cylinder_min_capacity_kn,
            "scenarios": recovery_scenarios,
            "interpretation": "Lower mass reduces calculated reactions, but it does not authorise scissor jacks, unilateral lifting or a reduced-capacity recovery kit.",
        },
        "closure_rule": "Do not reduce controlled tare until all active row evidence is accepted and a signed trainset weight-and-balance report closes category totals, individual-car weights, axle loads and centre of gravity.",
    }


def render_mass_closure(payload: dict[str, object]) -> str:
    """Render the controlled mass ledger as a reviewable Markdown report."""

    basis = dict(payload["mass_basis"])  # type: ignore[arg-type]
    coverage = dict(payload["coverage"])  # type: ignore[arg-type]
    light = dict(payload["lightweighting"])  # type: ignore[arg-type]
    recovery = dict(payload["recovery_load_case_link"])  # type: ignore[arg-type]
    lines = [
        "# LM3 product-level mass closure and lightweighting ledger",
        "",
        "This ledger assigns every product row to one controlled planning category. It",
        "does **not** divide the category allowance into invented part masses: the current",
        "product geometry is an envelope/representation set, not production-solid mass evidence.",
        "",
        f"- Controlled planning tare: **{float(basis['controlled_planning_tare_kg']):,.0f} kg**",
        f"- Modeled exact subtotal: **{float(basis['modeled_exact_subtotal_kg']):,.2f} kg**",
        f"- Engineering reserve: **{float(basis['engineering_reserve_kg']):,.0f} kg**",
        f"- Coverage: **{coverage['mapped_product_rows']}/{coverage['product_rows']}** rows mapped; **{coverage['closed_active_product_rows']}/{coverage['active_product_rows']}** active rows mass-closed",
        "",
        "## Category responsibility",
        "",
        "| Planning category | Budget (kg) | Rows | Active | Closed active | Status |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for category in payload["categories"]:  # type: ignore[union-attr]
        row = dict(category)
        lines.append(
            f"| {row['category']} | {float(row['modeled_planning_budget_kg']):,.2f} | "
            f"{row['product_row_count']} | {row['active_product_row_count']} | "
            f"{row['closed_active_product_row_count']} | `{row['status']}` |"
        )
    lines.extend(
        [
            "",
            "## Lightweighting decision",
            "",
            f"The lightest feasible candidate already present in the declared design space is `{light['lightest_existing_feasible_candidate']}` at **{float(light['lightest_existing_feasible_modeled_mass_kg']):,.2f} kg** before reserve. It saves **{float(light['modeled_saving_kg']):,.2f} kg ({light['modeled_saving_percent']}%)** against the selected modeled candidate. Keeping the reserve unchanged gives **{float(light['lightest_candidate_with_unchanged_reserve_kg']):,.2f} kg**, not a closed new tare.",
            "",
            f"Decision: **{light['decision']}**.",
            "",
            "Promotion gates:",
            "",
            *[f"- {gate}" for gate in light["promotion_gates"]],
            "",
            "## Recovery reaction link",
            "",
            f"All cases retain the **{float(recovery['portable_cylinder_envelope_kn_per_point']):,.0f} kN/point** rail-rated portable-cylinder envelope.",
            "",
            "| Mass scenario | Status | Train (kg) | Full car, 4-point (kN/point) | One end, 2-point (kN/point) |",
            "|---|---|---:|---:|---:|",
        ]
    )
    for scenario in recovery["scenarios"]:
        row = dict(scenario)
        cases = {case["load_case_id"]: case for case in row["load_cases"]}
        lines.append(
            f"| `{row['id']}` | {row['status']} | {float(row['train_mass_kg']):,.2f} | "
            f"{float(cases['full-car-four-point']['required_point_capacity_kn']):,.2f} | "
            f"{float(cases['one-end-two-point']['required_point_capacity_kn']):,.2f} |"
        )
    lines.extend(
        [
            "",
            str(recovery["interpretation"]),
            "",
            "## Product closure rows",
            "",
            "| Product | Route | Qty | Mass responsibility | Evidence state | Minimum evidence |",
            "|---|---|---:|---|---|---|",
        ]
    )
    for product in payload["product_rows"]:  # type: ignore[union-attr]
        row = dict(product)
        evidence = "; ".join(row["evidence_required"])
        lines.append(
            f"| `{row['product_id']}` — {row['title']} | `{row['route']}` | "
            f"{float(row['quantity_per_trainset']):g} {row['unit']} | {row['mass_responsibility_category']} | "
            f"`{row['mass_evidence_status']}` | {evidence} |"
        )
    lines.extend(["", "## Closure rule", "", str(payload["closure_rule"]), ""])
    return "\n".join(lines)
