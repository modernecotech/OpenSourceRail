"""Shared parameters for rolling-stock CAD template parts."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TemplateParams:
    """Default envelope dimensions in millimetres."""

    gauge_mm: float = 1435.0
    car_length_mm: float = 20_000.0
    car_width_mm: float = 2850.0
    low_floor_height_mm: float = 350.0
    frame_beam_width_mm: float = 200.0
    frame_beam_height_mm: float = 100.0
    frame_beam_thickness_mm: float = 8.0
    cross_spacing_mm: float = 1000.0
    panel_width_mm: float = 1200.0
    panel_height_mm: float = 3000.0
    panel_thickness_mm: float = 40.0
    skin_thickness_mm: float = 1.8
    door_width_mm: float = 1200.0
    door_height_mm: float = 2200.0
    door_thickness_mm: float = 40.0
    door_skin_thickness_mm: float = 1.5
    battery_module_width_mm: float = 420.0
    battery_module_height_mm: float = 220.0
    battery_module_length_mm: float = 320.0


DEFAULT_PARAMS = TemplateParams()
