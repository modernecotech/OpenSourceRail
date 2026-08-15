"""OSR parametric mechanical catalogue — see package README for scope."""

from __future__ import annotations

import importlib

from .common import (
    ConsistFamily,
    GeometryPreset,
    RailProfile,
    StationArchetype,
    consist_length_m,
    consist_platform_length_m,
)

_SUBMODULES = {
    "accessibility",
    "cad_templates",
    "civil",
    "clearance",
    "crashworthiness",
    "depot",
    "rolling_stock",
    "station",
    "track",
}

__all__ = [
    "ConsistFamily",
    "GeometryPreset",
    "RailProfile",
    "StationArchetype",
    "accessibility",
    "cad_templates",
    "civil",
    "clearance",
    "consist_length_m",
    "consist_platform_length_m",
    "crashworthiness",
    "depot",
    "rolling_stock",
    "station",
    "track",
]


def __getattr__(name: str):
    if name in _SUBMODULES:
        module = importlib.import_module(f"{__name__}.{name}")
        globals()[name] = module
        return module
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
