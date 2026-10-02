"""Soil/access classified foundation selection and quantity functions."""

from __future__ import annotations

import math
import tomllib
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

CATALOG_PATH = Path(__file__).resolve().parents[5] / "lib/templates/foundation-catalog.toml"


@dataclass(frozen=True)
class FoundationSelection:
    id: str
    interface: str
    project_length_required: bool
    deep_element_count: int
    candidate_ids: tuple[str, ...] = ()
    selection_state: str = "planning-preference-only"
    selected_id: str | None = None


@dataclass(frozen=True)
class FoundationInstalledRecord:
    support_id: str
    foundation_id: str
    actual_length_m: float | None
    actual_element_count: int
    concrete_m3: float
    actual_reinforcement_kg: float
    installation_hours: float
    actual_installed_cost_usd: float
    test_result: str


@dataclass(frozen=True)
class GroundImprovementSelection:
    id: str
    interface: str
    design_measurement: str
    project_design_required: bool = True
    selection_state: str = "planning-candidate-only"


@dataclass(frozen=True)
class GeotechnicalSystemSelection:
    kind: str
    id: str
    interface: str
    selection_state: str = "planning-preference-only"
    selected_id: str | None = None


@lru_cache(maxsize=1)
def foundation_catalog() -> dict[str, Any]:
    with CATALOG_PATH.open("rb") as handle:
        return tomllib.load(handle)


def foundation_type(foundation_id: str) -> dict[str, Any]:
    for item in foundation_catalog()["foundation_types"]:
        if item["id"] == foundation_id:
            return item
    raise ValueError(f"unknown foundation type {foundation_id!r}")


def ground_improvement_type(product_id: str) -> dict[str, Any]:
    for item in foundation_catalog()["ground_improvement_types"]:
        if item["id"] == product_id:
            return item
    raise ValueError(f"unknown ground-improvement type {product_id!r}")


def finite_positive(value: float, name: str) -> float:
    if type(value) not in (int, float) or not math.isfinite(value) or value <= 0:
        raise ValueError(f"{name} must be finite and positive")
    return float(value)


def element_count(item: dict, value: int | None) -> int:
    count = int(item["deep_element_count"]) if value is None else value
    minimum = 1 if item["project_length_required"] else 0
    if type(count) is not int or count < minimum:
        raise ValueError("actual element count must be a positive integer for deep foundations; zero only denotes no deep elements")
    if not item["project_length_required"] and count != 0:
        raise ValueError("shallow foundation does not use deep elements")
    return count


def foundation_candidates(ground_class: str, *, vibration_restricted: bool = False,
                          clear_access: bool = True, high_lateral_load: bool = False) -> dict:
    """Screen methods for comparison; ground categories never select a design."""
    if ground_class not in {value for row in foundation_catalog()["foundation_types"] for value in row["ground_classes"]}:
        raise ValueError("ground/access condition requires project-specific foundation selection")
    candidates = ["bored-shaft", "pile-group"]
    if ground_class in {"rock", "dense-gravel", "strong-cemented-soil"} and not high_lateral_load:
        candidates.insert(0,"shallow-spread")
    if clear_access and not vibration_restricted:
        candidates.append("driven-pile-bent")
    if ground_class in {"viaduct-end", "low-embankment"} and not high_lateral_load:
        candidates.append("reinforced-soil-abutment")
    return {"candidate_ids":candidates,"selected_id":None,"state":"site-comparison-required",
            "required_inputs":["bearing/axial/lateral actions and resistance", "total/differential settlement", "groundwater and chemistry",
                               "liquefaction and scour where applicable", "access, utilities and installation trials", "independent geotechnical review"]}


def select_foundation(
    ground_class: str,
    *,
    vibration_restricted: bool = False,
    clear_access: bool = True,
    high_lateral_load: bool = False,
) -> FoundationSelection:
    """Legacy planning preference; use candidate_ids for site comparison, never release."""

    if high_lateral_load or ground_class in {"weak-liquefiable", "high-lateral-load"}:
        selected = "pile-group"
    elif vibration_restricted or ground_class in {"urban-alluvium", "vibration-restricted"}:
        selected = "bored-shaft"
    elif ground_class == "uniform-soft-ground" and clear_access:
        selected = "driven-pile-bent"
    elif ground_class in {"dense-gravel", "rock", "strong-cemented-soil"}:
        selected = "shallow-spread"
    elif ground_class in {"viaduct-end", "low-embankment"}:
        selected = "reinforced-soil-abutment"
    else:
        raise ValueError("ground/access condition requires project-specific foundation selection")
    item = foundation_type(selected)
    return FoundationSelection(
        id=selected,
        interface=str(item["interface"]),
        project_length_required=bool(item["project_length_required"]),
        deep_element_count=int(item["deep_element_count"]),
        candidate_ids=tuple(foundation_candidates(ground_class,vibration_restricted=vibration_restricted,
                             clear_access=clear_access,high_lateral_load=high_lateral_load)["candidate_ids"]),
    )


def select_ground_improvement(
    ground_class: str,
    *,
    strict_settlement_limit: bool = True,
    embankment_or_at_grade: bool = True,
    calcium_treatment_compatibility_review: str | None = None,
) -> GroundImprovementSelection:
    """Return a planning candidate for a non-pier zone, subject to site review."""

    if not embankment_or_at_grade:
        raise ValueError("ground improvement catalogue applies to at-grade or embankment zones")
    if ground_class in {"uniform-soft-ground", "compressible-alluvium"}:
        selected = "rigid-inclusion-platform" if strict_settlement_limit else "deep-soil-mixing"
    elif ground_class in {"very-soft-clay", "organic-soft-soil"}:
        selected = "deep-soil-mixing"
    elif ground_class in {"loose-granular", "soft-granular"} and not strict_settlement_limit:
        selected = "stone-columns"
    elif ground_class in {"marginal-fill", "lightweight-approach-zone"}:
        selected = "lightweight-fill"
    elif ground_class in {"weak-formation", "moisture-sensitive-formation"}:
        if not calcium_treatment_compatibility_review:
            raise ValueError("lime/cement candidate requires reviewed soil chemistry and treatment compatibility")
        selected = "lime-cement-stabilisation"
    else:
        raise ValueError("ground condition requires project-specific improvement selection")
    item = ground_improvement_type(selected)
    return GroundImprovementSelection(
        id=selected,
        interface=str(item["interface"]),
        design_measurement=str(item["design_measurement"]),
    )


def select_geotechnical_system(
    ground_class: str,
    *,
    structure: str,
    vibration_restricted: bool = False,
    clear_access: bool = True,
    high_lateral_load: bool = False,
    strict_settlement_limit: bool = True,
) -> GeotechnicalSystemSelection:
    """Select a foundation for a pier or an improvement for ground-supported work."""

    if structure in {"at-grade", "embankment", "approach"}:
        selected = select_ground_improvement(
            ground_class,
            strict_settlement_limit=strict_settlement_limit,
        )
        return GeotechnicalSystemSelection("ground-improvement", selected.id, selected.interface)
    if structure in {"pier", "abutment"}:
        selected = select_foundation(
            ground_class,
            vibration_restricted=vibration_restricted,
            clear_access=clear_access,
            high_lateral_load=high_lateral_load,
        )
        return GeotechnicalSystemSelection("foundation", selected.id, selected.interface)
    raise ValueError("structure must be pier, abutment, at-grade, embankment, or approach")


def foundation_concrete_m3(
    foundation_id: str,
    *,
    actual_length_m: float | None = None,
    actual_element_count: int | None = None,
) -> float:
    """Calculate concrete from selected type and actual deep-element length.

    Deep foundations intentionally have no default length: supplying the site
    value is mandatory and prevents the former six-metre CAD placeholder from
    leaking into cost quantities.
    """

    item = foundation_type(foundation_id)
    interface = (
        float(item["interface_width_m"])
        * float(item["interface_length_m"])
        * float(item["interface_depth_m"])
    )
    count = element_count(item, actual_element_count)
    if bool(item["project_length_required"]):
        if actual_length_m is None:
            raise ValueError(f"{foundation_id} requires actual pile/shaft length")
        actual_length_m = finite_positive(actual_length_m,"actual pile/shaft length")
        if "deep_element_diameter_m" in item:
            area = math.pi * (float(item["deep_element_diameter_m"]) / 2.0) ** 2
        elif "deep_element_width_m" in item:
            area = float(item["deep_element_width_m"]) ** 2
        else:
            area = math.pi * (float(item["interface_width_m"]) / 2.0) ** 2
            interface = 0.0  # integral bored shaft: do not double-count a cap
        return finite_positive(interface + count * area * actual_length_m,"foundation concrete quantity")
    if actual_length_m is not None:
        raise ValueError(f"{foundation_id} does not use a deep-element length")
    return interface


def foundation_installed_record(
    support_id: str,
    foundation_id: str,
    *,
    actual_installed_cost_usd: float,
    actual_reinforcement_kg: float,
    installation_hours: float,
    test_result: str,
    actual_length_m: float | None = None,
    actual_element_count: int | None = None,
) -> FoundationInstalledRecord:
    """Create the per-support quantity, time, test and actual-cost record."""

    if not support_id.strip():
        raise ValueError("support id is required")
    finite_positive(actual_installed_cost_usd,"actual installed cost")
    finite_positive(actual_reinforcement_kg,"reinforcement")
    finite_positive(installation_hours,"installation hours")
    if not test_result.strip():
        raise ValueError("foundation test result is required")
    item = foundation_type(foundation_id)
    count = element_count(item, actual_element_count)
    concrete = foundation_concrete_m3(
        foundation_id,
        actual_length_m=actual_length_m,
        actual_element_count=actual_element_count,
    )
    return FoundationInstalledRecord(
        support_id=support_id,
        foundation_id=foundation_id,
        actual_length_m=actual_length_m,
        actual_element_count=count,
        concrete_m3=round(concrete, 3),
        actual_reinforcement_kg=actual_reinforcement_kg,
        installation_hours=installation_hours,
        actual_installed_cost_usd=actual_installed_cost_usd,
        test_result=test_result.strip(),
    )


__all__ = [
    "FoundationSelection",
    "FoundationInstalledRecord",
    "GeotechnicalSystemSelection",
    "GroundImprovementSelection",
    "foundation_catalog",
    "foundation_candidates",
    "foundation_concrete_m3",
    "foundation_installed_record",
    "foundation_type",
    "ground_improvement_type",
    "select_foundation",
    "select_geotechnical_system",
    "select_ground_improvement",
]
