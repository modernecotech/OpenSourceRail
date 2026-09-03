"""Shared rolling-stock/depot maintenance-interface datum contract.

The vehicle and depot models deliberately consume the same immutable values.
They are coordination dimensions for design review, not certified lifting
loads, foundation reactions, or supplier equipment selections.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache


@dataclass(frozen=True)
class LM3BogieChangeDatum:
    """Controlled geometry for one LM3 car in a bogie-change bay."""

    car_length_mm: float
    car_width_mm: float
    bogie_centre_spacing_mm: float
    rail_gauge_mm: float = 1_435.0
    jack_longitudinal_spacing_mm: float = 11_200.0
    jack_transverse_spacing_mm: float = 2_360.0
    lift_column_transverse_spacing_mm: float = 4_400.0
    inspection_pit_length_mm: float = 16_000.0
    inspection_pit_clear_width_mm: float = 1_400.0
    inspection_pit_depth_mm: float = 1_500.0
    bogie_extraction_clear_width_mm: float = 5_000.0
    nominal_lift_stroke_mm: float = 1_500.0

    @property
    def bogie_centres_x_mm(self) -> tuple[float, float]:
        half = self.bogie_centre_spacing_mm / 2.0
        return (-half, half)

    @property
    def jack_positions_mm(self) -> tuple[tuple[float, float], ...]:
        half_x = self.jack_longitudinal_spacing_mm / 2.0
        half_y = self.jack_transverse_spacing_mm / 2.0
        return tuple((x, y) for x in (-half_x, half_x) for y in (-half_y, half_y))

    @property
    def lift_column_positions_mm(self) -> tuple[tuple[float, float], ...]:
        half_x = self.jack_longitudinal_spacing_mm / 2.0
        half_y = self.lift_column_transverse_spacing_mm / 2.0
        return tuple((x, y) for x in (-half_x, half_x) for y in (-half_y, half_y))


@lru_cache(maxsize=1)
def lm3_bogie_change_datum() -> LM3BogieChangeDatum:
    """Build the contract from the promoted train baseline without import cycles."""

    from osr_mech.rolling_stock.baseline import (
        PROMOTED_LIGHT_METRO_BOGIE_CENTRE_SPACING_MM,
        PROMOTED_LIGHT_METRO_CAR_LENGTH_MM,
        PROMOTED_LIGHT_METRO_CAR_WIDTH_MM,
    )

    return LM3BogieChangeDatum(
        car_length_mm=PROMOTED_LIGHT_METRO_CAR_LENGTH_MM,
        car_width_mm=PROMOTED_LIGHT_METRO_CAR_WIDTH_MM,
        bogie_centre_spacing_mm=PROMOTED_LIGHT_METRO_BOGIE_CENTRE_SPACING_MM,
    )


__all__ = ["LM3BogieChangeDatum", "lm3_bogie_change_datum"]
