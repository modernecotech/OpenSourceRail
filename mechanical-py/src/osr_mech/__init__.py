"""OSR parametric mechanical catalogue — see package README for scope."""

from . import civil, rolling_stock, station, track  # noqa: F401
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
    "civil",
    "consist_platform_length_m",
    "rolling_stock",
    "station",
    "track",
]
