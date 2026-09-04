from __future__ import annotations

from osr_mech.freecad_sources import SOURCE_BUILDERS
from osr_mech.rolling_stock.exterior_finish import (
    exterior_finish_review_assembly,
    finish_process,
    finish_process_payload,
    finish_zones,
)
from osr_mech.rolling_stock.product_geometry import flatten_geometry


def test_finish_zones_keep_decorative_film_separate_from_protection() -> None:
    zones = {zone.id: zone for zone in finish_zones()}
    assert set(zones) == {"LM3-FIN-Z01", "LM3-FIN-Z02", "LM3-FIN-Z03"}
    assert "corrosion primer" in zones["LM3-FIN-Z01"].mandatory_base_system
    assert "graphic film" in zones["LM3-FIN-Z02"].simplified_finish
    assert "gelcoat" in zones["LM3-FIN-Z02"].mandatory_base_system
    assert "PV active area and clamps" in zones["LM3-FIN-Z03"].prohibited_coverage
    assert "one-car thermal and maintenance trial" in zones["LM3-FIN-Z03"].release_evidence


def test_radiative_values_are_screening_targets_and_process_has_hold_points() -> None:
    payload = finish_process_payload()
    targets = payload["radiative_research_targets"]
    assert targets["initial_solar_reflectance"] == 0.955
    assert targets["initial_sky_window_emissivity"] == 0.94
    assert "research screening" in targets["use"]
    assert len(finish_process()) == 6
    assert all(step.hold_point for step in finish_process())


def test_finish_review_geometry_and_source_registration() -> None:
    leaves = flatten_geometry(exterior_finish_review_assembly())
    labels = {leaf.label for leaf in leaves}
    assert "replaceable pre-cut livery film band" in labels
    assert "candidate CaCO3 radiative finish on exposed roof only" in labels
    assert {"HVAC keep-out", "PV keep-out", "antenna/service keep-out"} <= labels
    assert "lm3-exterior-finish-review" in SOURCE_BUILDERS
