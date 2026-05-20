"""OSR parametric mechanical catalogue — see package README for scope."""

from . import (  # noqa: F401
    accessibility,
    cad_templates,
    civil,
    clearance,
    crashworthiness,
    depot,
    rolling_stock,
    station,
    track,
)
from .common import (
    ConsistFamily,
    GeometryPreset,
    RailProfile,
    StationArchetype,
    consist_platform_length_m,
)

__all__ = [
    "ConsistFamily",
    "GeometryPreset",
    "RailProfile",
    "StationArchetype",
    "accessibility",
    "cad_templates",
    "civil",
    "clearance",
    "consist_platform_length_m",
    "crashworthiness",
    "depot",
    "rolling_stock",
    "station",
    "track",
]
