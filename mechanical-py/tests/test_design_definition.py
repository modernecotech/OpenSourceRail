from __future__ import annotations

from osr_mech.common import ConsistFamily
from osr_mech.design_definition import (
    EXTERNAL_COMPONENTS,
    FABRICATED_PARTS,
    FINAL_ASSEMBLIES,
    REQUIREMENTS,
    SUBASSEMBLIES,
    CandidateParameters,
    evaluate_candidate,
    iterate_design_space,
    render_markdown,
)
from osr_mech.rolling_stock.baseline import (
    PROMOTED_CANDIDATE_ID,
    PROMOTED_LIGHT_METRO_CAR_LENGTH_M,
    PROMOTED_OPTIMIZER_MASS_SUBTOTAL_KG,
)


def test_design_hierarchy_has_required_layers() -> None:
    assert REQUIREMENTS
    assert any(item.role == "traction motor" for item in EXTERNAL_COMPONENTS)
    assert any(item.role.startswith("primary car body") for item in FABRICATED_PARTS)
    assert any(item.id == "sub-car-module" for item in SUBASSEMBLIES)
    assert any(item.id == "final-light-metro-trainset" for item in FINAL_ASSEMBLIES)


def test_promoted_reference_candidate_is_feasible() -> None:
    candidate = evaluate_candidate(
        CandidateParameters(
            family=ConsistFamily.LIGHT_METRO_3CAR,
            car_length_m=PROMOTED_LIGHT_METRO_CAR_LENGTH_M,
            structure_gauge="reference",
            bogie_frame_gauge="reference",
            motor_id="motor-350kw-hm47-class",
            battery_id="battery-225kwh-lfp-800v",
            hvac_id="hvac-24kw-direct-hv-dc",
            pv_modules_per_car=12,
        )
    )
    assert candidate.id == PROMOTED_CANDIDATE_ID
    assert candidate.feasible, candidate.violations
    assert candidate.metrics["platform_margin_m"] >= 1.0
    assert candidate.metrics["offwire_range_km"] >= 50.0
    assert candidate.metrics["traction_margin"] >= 1.0
    assert round(sum(candidate.mass_breakdown_kg.values())) == PROMOTED_OPTIMIZER_MASS_SUBTOTAL_KG


def test_iteration_returns_best_feasible_candidate_and_markdown() -> None:
    run = iterate_design_space(ConsistFamily.LIGHT_METRO_3CAR)
    assert run.iterations >= 80
    assert run.optimum.feasible
    assert run.optimum.id == PROMOTED_CANDIDATE_ID
    assert run.optimum.mass_breakdown_kg
    assert run.optimum in run.trace
    markdown = render_markdown(run)
    assert "Rolling-stock design iteration summary" in markdown
    assert run.optimum.id in markdown
    assert "Best-candidate modeled mass breakdown" in markdown
