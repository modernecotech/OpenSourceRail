"""Reusable railway/civil interface kits for coordination and maintainability.

The geometry fixes access, drainage and replacement envelopes at repeatable
datums.  Bearing, seal, restraint and anchorage selections remain project and
supplier calculations; these parts must not be interpreted as released details.
"""

from __future__ import annotations

from osr_mech.cad import Box, Color, Compound, Location, Part


STEEL = Color(0.30, 0.35, 0.39)
ELASTOMER = Color(0.12, 0.12, 0.12)
CONCRETE = Color(0.68, 0.68, 0.65)
SERVICE = Color(0.12, 0.52, 0.62)
CLEARANCE = Color(0.95, 0.34, 0.12, 0.18)


def _box(size: tuple[float, float, float], location: tuple[float, float, float], label: str, color: Color) -> Part:
    item = Box(*size).locate(Location(location))
    item.label = label
    item.color = color
    return item


def bearing_replacement_interface() -> Compound:
    """Paired bearing seats, jacking pads and a transverse extraction path."""

    parts: list[Part] = [
        _box((3_400, 2_900, 450), (0, 0, -225), "Pier-cap bearing interface zone", CONCRETE),
        _box((4_600, 3_600, 1_800), (0, 0, 900), "Temporary jacking and bearing extraction clearance", CLEARANCE),
    ]
    for side in (-1.0, 1.0):
        parts.extend([
            _box((650, 750, 90), (side * 850, 0, 45), "Replaceable bearing sole plate", STEEL),
            _box((500, 600, 180), (side * 850, 0, 180), "Supplier bearing coordination envelope", ELASTOMER),
            _box((420, 520, 80), (side * 850, 0, -40), "Grouted levelling plinth", CONCRETE),
            _box((520, 520, 100), (side * 850, 900, 50), "Permanent jacking pad", STEEL),
        ])
    return Compound(label="Bearing replacement and jacking interface", children=parts)


def deck_expansion_joint_interface() -> Compound:
    """Joint nosings, replaceable seal and below-deck collection tray."""

    return Compound(label="Deck expansion-joint maintenance interface", children=[
        _box((320, 3_400, 260), (-260, 0, 0), "Approach nosing and anchor zone", CONCRETE),
        _box((320, 3_400, 260), (260, 0, 0), "Departure nosing and anchor zone", CONCRETE),
        _box((180, 3_200, 100), (0, 0, 40), "Replaceable watertight joint seal envelope", ELASTOMER),
        _box((750, 3_000, 160), (0, 0, -260), "Removable drainage collection tray", SERVICE),
        _box((1_600, 4_200, 1_100), (0, 0, -150), "Joint inspection and replacement clearance", CLEARANCE),
    ])


def walkway_service_cassette() -> Compound:
    """Six-metre evacuation deck with segregated cable and drainage routes."""

    return Compound(label="Walkway, cable and drainage cassette", children=[
        _box((6_000, 1_050, 140), (3_000, 0, 70), "Replaceable anti-slip walkway slab", CONCRETE),
        _box((6_000, 110, 1_400), (3_000, 470, 700), "Barrier and screen socket rail", STEEL),
        _box((6_000, 260, 180), (3_000, -360, -100), "Covered LV/data cable trough", SERVICE),
        _box((6_000, 220, 180), (3_000, -80, -100), "Covered HV cable trough", STEEL),
        _box((6_000, 180, 160), (3_000, 260, -100), "Drainage channel and rodding route", SERVICE),
        _box((700, 1_450, 1_800), (5_650, 0, 600), "Cassette lifting and withdrawal clearance", CLEARANCE),
    ])


def approach_transition_interface() -> Compound:
    """Slab/structure transition zones with drainage and monitoring datums."""

    return Compound(label="At-grade to structure approach transition", children=[
        _box((12_000, 3_200, 420), (6_000, 0, -210), "Graded transition slab envelope", CONCRETE),
        _box((3_000, 3_200, 520), (10_500, 0, -260), "Structure-end sleeper/fastener transition zone", CONCRETE),
        _box((12_000, 240, 260), (6_000, 1_350, -340), "Accessible drainage and filter trench", SERVICE),
        _box((300, 300, 220), (2_000, -1_250, 110), "Settlement survey datum", STEEL),
        _box((300, 300, 220), (10_000, -1_250, 110), "Settlement survey datum", STEEL),
    ])


def railway_interface_kit() -> Compound:
    """Review sheet containing all four independent reusable interfaces."""

    return Compound(label="Reusable civil/railway interfaces", children=[
        bearing_replacement_interface().translate((0, 0, 0)),
        deck_expansion_joint_interface().translate((8_000, 0, 0)),
        walkway_service_cassette().translate((13_000, 0, 0)),
        approach_transition_interface().translate((21_000, 0, 0)),
    ])


__all__ = [
    "approach_transition_interface",
    "bearing_replacement_interface",
    "deck_expansion_joint_interface",
    "railway_interface_kit",
    "walkway_service_cassette",
]
