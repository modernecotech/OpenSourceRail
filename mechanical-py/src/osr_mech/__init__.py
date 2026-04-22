"""OSR parametric mechanical catalogue — see package README for scope."""

from . import civil, station, track  # noqa: F401
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
    "station",
    "track",
]
