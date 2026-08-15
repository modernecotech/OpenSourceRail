"""Shared enums + parameter helpers for RFC-driven CAD models.

The enums mirror the RFC 0008 / 0009 / 0010 / 0011 catalogues exactly —
if an RFC changes, this file changes first, and every parametric
component picks up the new option automatically.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ConsistFamily(str, Enum):
    """RFC 0008 §1 rolling-stock families."""

    URBAN_SHUTTLE_1CAR = "urban-shuttle-1car"
    TRAM_2CAR = "tram-2car"
    LIGHT_METRO_3CAR = "light-metro-3car"
    METRO_4CAR = "metro-4car"
    METRO_6CAR = "metro-6car"


class GeometryPreset(str, Enum):
    """RFC 0009 §1 track-geometry presets."""

    STANDARD_URBAN = "standard-urban"
    STANDARD_METRO = "standard-metro"
    MAINLINE_MIXED = "mainline-mixed"


class StationArchetype(str, Enum):
    """RFC 0010 station shells: six bases plus one elevation variant."""

    HALT = "halt"
    STANDARD = "standard"
    MAJOR = "major"
    INTERCHANGE = "interchange"
    INTERCHANGE_ELEVATED = "interchange-elevated"
    TERMINAL = "terminal"
    DEPOT_TERMINAL = "depot-terminal"


class RailProfile(str, Enum):
    """Rail sections in scope — both UIC profiles in current use."""

    UIC_54E1 = "54E1"
    UIC_60E1 = "60E1"


@dataclass(frozen=True)
class RailGeometry:
    """Simplified UIC rail cross-section, for CAD review only.

    Real rolling-mill profiles include fillets and radiused transitions
    that do not affect clearance checks at 1:10 scale. The CAD extrusion
    uses a tapered polygon approximation of the UIC standard
    (head tapers inward at its crown, foot tapers inward at its
    underside edges) — this matches the published linear mass within
    ~2 %. Vendors supplying actual rail stock still roll to the full
    UIC fillet profile.
    """

    name: str
    height_mm: float
    head_width_mm: float        # crown width (top of head)
    head_base_width_mm: float   # head width where it meets the web fillet
    head_height_mm: float
    web_thickness_mm: float
    foot_width_mm: float        # maximum foot width (underside)
    foot_top_width_mm: float    # foot width where it meets the web fillet
    foot_height_mm: float
    linear_mass_kg_per_m: float


RAIL_GEOMETRY: dict[RailProfile, RailGeometry] = {
    RailProfile.UIC_54E1: RailGeometry(
        name="54E1",
        height_mm=159.0,
        head_width_mm=70.0,
        head_base_width_mm=53.0,
        head_height_mm=49.4,
        web_thickness_mm=16.0,
        foot_width_mm=140.0,
        foot_top_width_mm=37.0,
        foot_height_mm=31.5,
        linear_mass_kg_per_m=54.77,
    ),
    RailProfile.UIC_60E1: RailGeometry(
        name="60E1",
        height_mm=172.0,
        head_width_mm=72.0,
        head_base_width_mm=55.0,
        head_height_mm=51.0,
        web_thickness_mm=16.5,
        foot_width_mm=150.0,
        foot_top_width_mm=40.0,
        foot_height_mm=31.5,
        linear_mass_kg_per_m=60.21,
    ),
}


# RFC 0008 consist lengths. Station platforms add the RFC 0010 clearance
# instead of maintaining a second, independently edited length table.
_CONSIST_LENGTH_M: dict[ConsistFamily, float] = {
    ConsistFamily.URBAN_SHUTTLE_1CAR: 21.0,
    ConsistFamily.TRAM_2CAR: 39.0,
    ConsistFamily.LIGHT_METRO_3CAR: 49.5,
    ConsistFamily.METRO_4CAR: 75.0,
    ConsistFamily.METRO_6CAR: 111.0,
}


def consist_length_m(consist: ConsistFamily) -> float:
    """Published overall consist length from RFC 0008."""

    return _CONSIST_LENGTH_M[consist]


def consist_platform_length_m(consist: ConsistFamily) -> float:
    """Default non-halt platform length: consist plus 10 m clearance."""

    return consist_length_m(consist) + 10.0


# RFC 0009 §1 rail-profile-per-preset mapping.
_PRESET_RAIL_PROFILE: dict[GeometryPreset, RailProfile] = {
    GeometryPreset.STANDARD_URBAN: RailProfile.UIC_54E1,
    GeometryPreset.STANDARD_METRO: RailProfile.UIC_60E1,
    GeometryPreset.MAINLINE_MIXED: RailProfile.UIC_60E1,
}


def preset_rail_profile(preset: GeometryPreset) -> RailProfile:
    return _PRESET_RAIL_PROFILE[preset]


# Gauge for upstream urban-rail components.
STANDARD_GAUGE_MM: float = 1435.0


# Sleeper spacing per preset (RFC 0009 §4).
_PRESET_SLEEPER_SPACING_MM: dict[GeometryPreset, float] = {
    GeometryPreset.STANDARD_URBAN: 650.0,
    GeometryPreset.STANDARD_METRO: 600.0,
    GeometryPreset.MAINLINE_MIXED: 600.0,
}


def preset_sleeper_spacing_mm(preset: GeometryPreset) -> float:
    return _PRESET_SLEEPER_SPACING_MM[preset]


# RFC 0010 and lib/templates/stations.toml platform clearances. A halt is
# shorter only by its reduced stopping/door-control allowance; it still fits
# the complete consist and does not depend on selective door opening.
_ARCHETYPE_PLATFORM_CLEARANCE_M: dict[StationArchetype, float] = {
    StationArchetype.HALT: 6.0,
    StationArchetype.STANDARD: 10.0,
    StationArchetype.MAJOR: 10.0,
    StationArchetype.INTERCHANGE: 10.0,
    StationArchetype.INTERCHANGE_ELEVATED: 10.0,
    StationArchetype.TERMINAL: 10.0,
    StationArchetype.DEPOT_TERMINAL: 10.0,
}


def archetype_platform_length_m(
    archetype: StationArchetype, consist: ConsistFamily
) -> float:
    return consist_length_m(consist) + _ARCHETYPE_PLATFORM_CLEARANCE_M[archetype]
