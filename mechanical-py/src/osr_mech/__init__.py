"""OSR parametric mechanical catalogue — see package README for scope."""

from . import accessibility, civil, clearance, crashworthiness, depot, rolling_stock, station, track  # noqa: F401
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
    "civil",
    "clearance",
    "consist_platform_length_m",
    "crashworthiness",
    "depot",
    "rolling_stock",
    "station",
    "track",
]
