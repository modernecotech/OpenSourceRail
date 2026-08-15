"""Canopy bay count, PV output, and steel mass regression."""

from __future__ import annotations

from pathlib import Path
import tomllib

import pytest

from osr_mech.common import (
    ConsistFamily,
    StationArchetype,
    archetype_platform_length_m,
    consist_length_m,
)
from osr_mech.station.canopy import (
    bay_count,
    canopy_kwp,
    canopy_steel_mass_kg,
    station_canopy,
)
from osr_mech.station.auxiliary_canopy import (
    AUX_MODULE_AREA_M2,
    auxiliary_canopy_kwp,
    auxiliary_canopy_row,
    auxiliary_foundation_count,
    auxiliary_frame_count,
    auxiliary_installed_area_m2,
    auxiliary_module_count,
)
from osr_mech.station.solar_roof import panel_kwp
from osr_mech.station.plinth import fare_lane_plinth, tvm_plinth
from osr_mech.civil.guideway_channel_edge import PLATFORM_TO_TOR_HEIGHT_MM, guideway_channel_edge_module


@pytest.mark.parametrize(
    "archetype, consist, expected_min_bays, expected_max_bays",
    [
        # Standard station × light-metro-3car = (49.5 + 10) m / 6 m = 10 bays.
        (StationArchetype.STANDARD, ConsistFamily.LIGHT_METRO_3CAR, 10, 10),
        # Major = standard + 2 waiting-area bays.
        (StationArchetype.MAJOR, ConsistFamily.LIGHT_METRO_3CAR, 12, 12),
        # Terminal = standard + 4 end-screen bays.
        (StationArchetype.TERMINAL, ConsistFamily.LIGHT_METRO_3CAR, 14, 14),
        # Metro-4car = 85 m / 6 m ≈ 15 bays.
        (StationArchetype.STANDARD, ConsistFamily.METRO_4CAR, 15, 15),
        # Halt still fits the consist: (49.5 + 6) m / 6 m = 10 bays.
        (StationArchetype.HALT, ConsistFamily.LIGHT_METRO_3CAR, 10, 10),
        # Elevated interchange is a controlled variant of interchange.
        (StationArchetype.INTERCHANGE_ELEVATED, ConsistFamily.LIGHT_METRO_3CAR, 10, 10),
    ],
)
def test_bay_counts(
    archetype: StationArchetype,
    consist: ConsistFamily,
    expected_min_bays: int,
    expected_max_bays: int,
) -> None:
    n = bay_count(archetype, consist)
    assert expected_min_bays <= n <= expected_max_bays, (
        f"{archetype.value}×{consist.value}: {n} bays outside [{expected_min_bays}, {expected_max_bays}]"
    )


def test_standard_canopy_generates_tens_of_kwp() -> None:
    # A 10-bay per-platform canopy at 6 m × 4.2 m per bay × 200 W/m²
    # × 0.85 pack factor ≈ 43 kWp.
    kwp = canopy_kwp(StationArchetype.STANDARD, ConsistFamily.LIGHT_METRO_3CAR)
    assert 40.0 <= kwp <= 70.0, f"standard canopy PV = {kwp:.1f} kWp, expected 40–70"


def test_platform_lengths_are_consist_plus_archetype_clearance() -> None:
    family = ConsistFamily.LIGHT_METRO_3CAR
    assert archetype_platform_length_m(StationArchetype.HALT, family) == pytest.approx(55.5)
    assert archetype_platform_length_m(StationArchetype.STANDARD, family) == pytest.approx(59.5)
    assert archetype_platform_length_m(StationArchetype.INTERCHANGE_ELEVATED, family) == pytest.approx(59.5)


def test_mechanical_station_catalogue_matches_the_canonical_template() -> None:
    root = Path(__file__).resolve().parents[2]
    template = tomllib.loads((root / "lib/templates/stations.toml").read_text())["archetypes"]
    assert set(template) == {archetype.value for archetype in StationArchetype}

    family = ConsistFamily.LIGHT_METRO_3CAR
    for archetype in StationArchetype:
        expected = consist_length_m(family) + float(template[archetype.value]["platform_clearance_m"])
        assert archetype_platform_length_m(archetype, family) == pytest.approx(expected)


def test_steel_mass_fits_two_lorries() -> None:
    # One articulated lorry can carry ~26 t of flat-pack steel. A
    # standard canopy should come in at <2 lorries — if it doesn't,
    # the bay design is too heavy and we need thinner sections.
    mass_kg = canopy_steel_mass_kg(
        StationArchetype.STANDARD, ConsistFamily.LIGHT_METRO_3CAR
    )
    assert mass_kg <= 52_000.0, f"{mass_kg / 1000:.1f} t exceeds 2-lorry budget"


def test_single_bay_panel_kwp_matches_spec() -> None:
    # 6 m × 3.5 m bay panel at 200 W/m² × 0.85 pack = 3.57 kWp.
    kwp = panel_kwp(6000.0, 3500.0)
    assert kwp == pytest.approx(3.57, abs=0.05)


def test_canopy_step_volume_nonzero() -> None:
    c = station_canopy(StationArchetype.STANDARD, ConsistFamily.LIGHT_METRO_3CAR)
    # The assembly is a Compound — volume is the sum across its children.
    # We just need to confirm CAD review sees non-trivial geometry.
    # Walk children and sum volumes.
    total = 0.0
    for ch in c.children:
        if hasattr(ch, "volume"):
            total += ch.volume
        if hasattr(ch, "children"):
            for sub in ch.children:
                if hasattr(sub, "volume"):
                    total += sub.volume
    assert total > 0.0


def test_auxiliary_canopy_quantises_area_without_underbuild() -> None:
    required_m2 = 1296.0
    modules = auxiliary_module_count(required_m2)
    assert AUX_MODULE_AREA_M2 == pytest.approx(187.0)
    assert modules == 7
    assert auxiliary_installed_area_m2(modules) >= required_m2
    assert auxiliary_frame_count(modules) == 8
    assert auxiliary_foundation_count(modules) == 16
    assert auxiliary_canopy_kwp(modules) == pytest.approx(222.53, abs=0.1)


def test_auxiliary_canopy_row_matches_shared_frame_product_rule() -> None:
    modules = 3
    canopy = auxiliary_canopy_row(modules)
    frames = [child for child in canopy.children if "transverse frame" in child.label]
    roofs = [child for child in canopy.children if "solar roof module" in child.label]
    assert len(frames) == modules + 1
    assert len(roofs) == modules
    assert canopy.volume > 0


def test_ground_level_station_edge_and_equipment_plinths_are_modelled() -> None:
    edge = guideway_channel_edge_module()
    assert PLATFORM_TO_TOR_HEIGHT_MM == 350
    assert edge.volume > 0
    assert {child.label for child in edge.children} >= {
        "Guideway edge beam",
        "Replaceable platform coping carrier",
        "Tactile and warning-strip carrier",
        "Guideway edge drain and service trough",
    }
    assert fare_lane_plinth().volume > 0
    assert tvm_plinth().volume > 0
