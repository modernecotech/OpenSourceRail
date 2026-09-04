"""Cross-domain civil geometry for LM3 field recovery access.

This source sits outside the civil quantity-model tree because the optional
selected-node envelope is not included in route-kilometre planning rates.
Project deployment decides the number, construction and cost of recovery nodes.
"""

from __future__ import annotations

from osr_mech.cad import Box, Color, Compound, Location, Part
from osr_mech.maintenance_interface import lm3_field_recovery_datum


STEEL = Color(0.30, 0.35, 0.39)
CONCRETE = Color(0.68, 0.68, 0.65)
RECOVERY = Color(0.94, 0.55, 0.08)
CLEARANCE = Color(0.95, 0.34, 0.12, 0.18)


def _box(
    size: tuple[float, float, float],
    location: tuple[float, float, float],
    label: str,
    color: Color,
) -> Part:
    item = Box(*size).locate(Location(location))
    item.label = label
    item.color = color
    return item


def wayside_rerailing_access_interface() -> Compound:
    """Optional civil envelope at selected road-accessible recovery nodes.

    This does not prescribe a foundation capacity. It preserves a level
    bearing/staging zone and a cross-track equipment path so a site-specific
    geotechnical design can support the released portable rerailing method.
    """

    datum = lm3_field_recovery_datum()
    hardstanding_y = (
        datum.car_width_mm / 2.0
        + 700.0
        + datum.recovery_hardstanding_width_mm / 2.0
    )
    staging_y = hardstanding_y + (
        datum.recovery_hardstanding_width_mm
        + datum.equipment_staging_width_mm
    ) / 2.0
    parts: list[Part] = [
        _box(
            (datum.recovery_hardstanding_length_mm, datum.recovery_hardstanding_width_mm, 260.0),
            (0.0, hardstanding_y, -130.0),
            "Selected-node rerailing hardstanding ground-bearing interface",
            CONCRETE,
        ),
        _box(
            (datum.equipment_staging_length_mm, datum.equipment_staging_width_mm, 180.0),
            (0.0, staging_y, -90.0),
            "Recovery vehicle offload and hydraulic-equipment staging interface",
            CONCRETE,
        ),
        _box(
            (datum.exclusion_zone_length_mm, datum.exclusion_zone_width_mm, 2_500.0),
            (0.0, 0.0, 1_250.0),
            "Temporary incident exclusion and controlled-access zone",
            CLEARANCE,
        ),
        _box(
            (datum.car_length_mm + 2_000.0, datum.car_width_mm + 1_400.0, 350.0),
            (0.0, 0.0, -350.0),
            "Track formation subject to incident ground-bearing verification",
            CONCRETE,
        ),
    ]
    for rail_y in (-datum.rail_gauge_mm / 2.0, datum.rail_gauge_mm / 2.0):
        parts.append(
            _box(
                (datum.car_length_mm + 2_000.0, 75.0, 172.0),
                (0.0, rail_y, -86.0),
                "Recovery-node running rail",
                STEEL,
            )
        )
    half_x = datum.jack_longitudinal_spacing_mm / 2.0
    for x in (-half_x, half_x):
        parts.extend(
            [
                _box(
                    (1_400.0, datum.transverse_rerailing_bridge_length_mm + 800.0, 120.0),
                    (x, 0.0, -60.0),
                    "Field rerailing bridge placement and bearing zone",
                    RECOVERY,
                ),
                _box(
                    (1_600.0, hardstanding_y, 900.0),
                    (x, hardstanding_y / 2.0, 450.0),
                    "Unobstructed cross-track equipment handling route",
                    CLEARANCE,
                ),
            ]
        )
    return Compound(label="LM3 selected-node wayside rerailing access interface", children=parts)


__all__ = ["wayside_rerailing_access_interface"]
