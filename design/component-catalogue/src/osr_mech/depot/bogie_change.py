"""Coordinated civil/equipment envelope for the LM3 bogie-change bay."""

from __future__ import annotations

from osr_mech.cad import Box, Color, Compound, Cylinder, Location, Part
from osr_mech.maintenance_interface import LM3BogieChangeDatum, lm3_bogie_change_datum


CONCRETE = Color(0.70, 0.70, 0.66)
STEEL = Color(0.38, 0.43, 0.48)
SAFETY = Color(0.90, 0.48, 0.10)
SYSTEM = Color(0.18, 0.39, 0.68)
CLEARANCE = Color(0.25, 0.55, 0.80, 0.18)


def _part(shape: Part, label: str, colour: Color, at: tuple[float, float, float]) -> Part:
    shape.label = label
    shape.color = colour
    return shape.locate(Location(at))


def _box(
    size: tuple[float, float, float],
    label: str,
    colour: Color,
    at: tuple[float, float, float],
) -> Part:
    return _part(Box(*size), label, colour, at)


def depot_bogie_change_bay(
    datum: LM3BogieChangeDatum | None = None,
    *,
    top_of_rail_z_mm: float = 0.0,
) -> Compound:
    """Return the civil, lifting, access, and extraction coordination assembly.

    The lift heads land on the exact four points published by
    :class:`LM3BogieChangeDatum`. Column bodies remain outside the car envelope
    and use transverse reach arms, leaving the pit and bogie-drop path clear.
    """

    datum = datum or lm3_bogie_change_datum()
    parts: list[Part] = []
    pit_top = top_of_rail_z_mm - 190.0
    pit_floor_z = pit_top - datum.inspection_pit_depth_mm
    wall_offset = datum.inspection_pit_clear_width_mm / 2.0 + 130.0

    parts.append(
        _box(
            (datum.inspection_pit_length_mm, datum.inspection_pit_clear_width_mm, datum.inspection_pit_depth_mm),
            "Bogie-change pit guarded clear envelope",
            CLEARANCE,
            (0.0, 0.0, pit_top - datum.inspection_pit_depth_mm / 2.0),
        )
    )
    parts.append(
        _box(
            (datum.inspection_pit_length_mm + 800.0, datum.inspection_pit_clear_width_mm + 520.0, 220.0),
            "Bogie-change pit reinforced base slab",
            CONCRETE,
            (0.0, 0.0, pit_floor_z - 110.0),
        )
    )
    for side in (-1.0, 1.0):
        parts.append(
            _box(
                (datum.inspection_pit_length_mm + 400.0, 260.0, datum.inspection_pit_depth_mm),
                "Bogie-change pit wall and edge-beam",
                CONCRETE,
                (0.0, side * wall_offset, pit_top - datum.inspection_pit_depth_mm / 2.0),
            )
        )
        rail_y = side * datum.rail_gauge_mm / 2.0
        parts.append(
            _box(
                (datum.inspection_pit_length_mm + 2_000.0, 75.0, 172.0),
                "Bogie-change bay running rail",
                STEEL,
                (0.0, rail_y, top_of_rail_z_mm - 86.0),
            )
        )

    jack_by_sign = {
        (1 if x > 0 else -1, 1 if y > 0 else -1): (x, y)
        for x, y in datum.jack_positions_mm
    }
    for column_x, column_y in datum.lift_column_positions_mm:
        sign = (1 if column_x > 0 else -1, 1 if column_y > 0 else -1)
        jack_x, jack_y = jack_by_sign[sign]
        foundation_z = top_of_rail_z_mm - 340.0
        parts.extend(
            [
                _box(
                    (1_200.0, 1_200.0, 680.0),
                    "Synchronized lift-column foundation and anchor pocket",
                    CONCRETE,
                    (column_x, column_y, foundation_z),
                ),
                _box(
                    (420.0, 420.0, 3_200.0),
                    "Synchronized lifting column supplier envelope",
                    SYSTEM,
                    (column_x, column_y, top_of_rail_z_mm + 1_600.0),
                ),
                _box(
                    (520.0, abs(column_y - jack_y) + 260.0, 220.0),
                    "Retractable lift arm and mechanical lock envelope",
                    STEEL,
                    (jack_x, (column_y + jack_y) / 2.0, top_of_rail_z_mm + 120.0),
                ),
                _box(
                    (480.0, 420.0, 120.0),
                    "LM3 four-point lift head datum",
                    SAFETY,
                    (jack_x, jack_y, top_of_rail_z_mm + 250.0),
                ),
            ]
        )

    for bogie_x in datum.bogie_centres_x_mm:
        parts.extend(
            [
                _box(
                    (4_000.0, datum.bogie_extraction_clear_width_mm, 1_300.0),
                    "Transverse bogie extraction and transfer clear envelope",
                    CLEARANCE,
                    (bogie_x, datum.bogie_extraction_clear_width_mm / 2.0 + 850.0, pit_floor_z + 650.0),
                ),
                _box(
                    (240.0, datum.bogie_extraction_clear_width_mm, 180.0),
                    "Bogie transfer-table embedded guide rail",
                    STEEL,
                    (bogie_x - 650.0, datum.bogie_extraction_clear_width_mm / 2.0 + 850.0, pit_floor_z + 90.0),
                ),
                _box(
                    (240.0, datum.bogie_extraction_clear_width_mm, 180.0),
                    "Bogie transfer-table embedded guide rail",
                    STEEL,
                    (bogie_x + 650.0, datum.bogie_extraction_clear_width_mm / 2.0 + 850.0, pit_floor_z + 90.0),
                ),
            ]
        )

    parts.extend(
        [
            _box(
                (3_600.0, 2_800.0, 1_400.0),
                "Removed bogie parking and restraint envelope",
                CLEARANCE,
                (0.0, datum.bogie_extraction_clear_width_mm + 3_200.0, top_of_rail_z_mm + 700.0),
            ),
            _box(
                (900.0, 650.0, 1_500.0),
                "Synchronized lift local control and emergency-stop cabinet",
                SYSTEM,
                (-datum.car_length_mm / 2.0 + 900.0, -3_700.0, top_of_rail_z_mm + 750.0),
            ),
            _part(
                Cylinder(90.0, 1_100.0),
                "Bogie-change bay trapped-key isolation post",
                SAFETY,
                (-datum.car_length_mm / 2.0 + 2_100.0, -3_700.0, top_of_rail_z_mm + 550.0),
            ),
        ]
    )
    return Compound(label="LM3 synchronized lifting and bogie-change bay assembly", children=parts)


__all__ = ["depot_bogie_change_bay"]
