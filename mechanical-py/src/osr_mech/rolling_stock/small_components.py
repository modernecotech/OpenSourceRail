"""Standardised small components for simple trainset assembly and service.

The train previously modelled most brackets and fixtures individually.  This
module deliberately reduces that variety to a small, supplier-neutral system:

* one slotted service-rail datum for ceiling, waist and seat-zone equipment;
* four controlled fastener families, selected by load and service frequency;
* two keyed rail-qualified connector families; and
* modular light, door-carrier and window-pressure-frame installation kits.

The geometry is an interface model, not a released fastener calculation.  In
particular, passenger-restraint fixtures, doors and glazing still require the
loads, preload, vibration, fire and supplier evidence named in the generated
small-component standard.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass

from osr_mech.cad import Box, Color, Compound, Cylinder, Location, Part

from .car_body import (
    DOOR_HEIGHT_MM,
    DOOR_SILL_HEIGHT_MM,
    DOOR_WIDTH_MM,
    WINDOW_HEIGHT_MM,
    WINDOW_MARGIN_MM,
    WINDOW_SILL_MM,
    CarDimensions,
)


SERVICE_RAIL_WIDTH_MM = 42.0
SERVICE_RAIL_DEPTH_MM = 18.0
SERVICE_RAIL_DATUM_PITCH_MM = 50.0
LIGHT_MODULE_LENGTH_MM = 1_200.0
LIGHT_MODULES_PER_CAR = 22
EMERGENCY_LIGHT_MODULES_PER_CAR = 4
DOOR_THRESHOLD_LIGHTS_PER_CAR = 4

COLOR_RAIL = Color(0.62, 0.65, 0.68)
COLOR_FASTENER = Color(0.78, 0.78, 0.75)
COLOR_ADAPTER = Color(0.94, 0.67, 0.16)
COLOR_SEAL = Color(0.04, 0.04, 0.045)
COLOR_LIGHT = Color(1.0, 0.94, 0.66)
COLOR_EMERGENCY = Color(0.34, 0.95, 0.48)
COLOR_CONNECTOR = Color(0.08, 0.22, 0.52)


@dataclass(frozen=True)
class FastenerFamily:
    id: str
    nominal: str
    retained_element: str
    intended_uses: tuple[str, ...]
    prohibited_uses: tuple[str, ...]
    installation_control: str
    release_authority: str


@dataclass(frozen=True)
class ConnectorFamily:
    id: str
    service: str
    interface: str
    keying: str
    release_evidence: tuple[str, ...]


FASTENER_FAMILIES: tuple[FastenerFamily, ...] = (
    FastenerFamily(
        "OSR-FST-M6-CAPTIVE",
        "M6 captive flanged screw into floating service-rail nut",
        "captive screw and retained sliding nut",
        ("light cassettes", "trim and service panels", "small PIS and cable supports"),
        ("seat or handhold primary load paths", "door primary retention", "glazing retention"),
        "positive seating, released torque table, witness mark and visual captive-part check",
        "small-component standard plus accepted fastener batch and calibrated-tool procedure",
    ),
    FastenerFamily(
        "OSR-FST-M8-FLOAT",
        "M8 flanged bolt into floating nutplate or qualified blind-rivet nut",
        "captive/floating female thread with anti-rotation feature",
        ("calculated seat and handrail adapters", "door/window secondary carriers", "PIS equipment trays"),
        ("uncalculated passenger-restraint joints", "primary crash structure", "bogie or coupler joints"),
        "joint-specific load/preload calculation, released torque, locking feature and witness mark",
        "released interface calculation and drawing plus accepted fastener batch",
    ),
    FastenerFamily(
        "OSR-FST-QT-CAPTIVE",
        "tool-operated captive quarter-turn stud and receptacle",
        "stud retained in removable panel; receptacle retained on rail adapter",
        ("frequently opened trim", "lighting diffuser", "inspection and access covers"),
        ("structural retention", "passenger handholds", "door or glazing retention"),
        "supplier grip-range gauge, closed-position indication and pull-check sampling",
        "accepted supplier part and receptacle/grip schedule",
    ),
    FastenerFamily(
        "OSR-FST-M10-SEAL",
        "M10 isolating flanged bolt into sealed floating nutplate",
        "sealed captive nutplate, isolation washer and replaceable environmental seal",
        ("external cassette carriers", "removable exterior equipment adapters"),
        ("direct glass clamping", "unsealed wet cavities", "primary crash joints without calculation"),
        "interface calculation, seal compression gauge, released torque and water-ingress test",
        "released cassette interface drawing and calculation plus supplier installation manual",
    ),
)


CONNECTOR_FAMILIES: tuple[ConnectorFamily, ...] = (
    ConnectorFamily(
        "OSR-CON-LV4",
        "24 V/48 V main and emergency lighting",
        "touch-safe keyed four-pole plug with retained strain relief",
        "main and emergency feeds use mechanically incompatible keys",
        ("rail fire/smoke evidence", "shock/vibration evidence", "pinout and polarity test", "connector retention test"),
    ),
    ConnectorFamily(
        "OSR-CON-LVDATA12",
        "door, PIS, CCTV and local low-voltage/data services",
        "keyed twelve-position plug family with blanking cap and fixed body-side bracket",
        "different voltage/data duties use unique shell keys and labels",
        ("rail fire/smoke evidence", "shock/vibration evidence", "EMC-compatible termination", "100% continuity test"),
    ),
)


AUTHORITATIVE_REFERENCES: tuple[dict[str, str], ...] = (
    {
        "title": "EU LOC&PAS TSI, Commission Regulation (EU) No 1302/2014",
        "url": "https://eur-lex.europa.eu/legal-content/en/TXT/?uri=CELEX%3A32014R1302",
        "use": "interior fixture retention, glazing, passenger doors and fire-safety release gates",
    },
    {
        "title": "ERA guide for the PRM TSI",
        "url": "https://www.era.europa.eu/system/files/2023-12/PRM_TSI_Guide.pdf",
        "use": "emergency-lighting and evacuation-visibility intent",
    },
    {
        "title": "Knorr-Bremse IFE entrance systems",
        "url": "https://rail.knorr-bremse.com/en/us/portfolio/products-and-systems/entrance-systems/",
        "use": "complete supplier-owned modular door system boundary",
    },
    {
        "title": "AGC glass with framing system",
        "url": "https://www.agc-automotive.com/en/products-and-solutions/glass-with-framing-system",
        "use": "supplier-bonded framed glazing and rapid cassette replacement",
    },
    {
        "title": "Bollhoff RIVNUT blind-rivet nuts",
        "url": "https://www.boellhoff.com/us-en/products/special-fasteners/rivnut-blind-rivet-nuts-and-rivstud-blind-rivet-studs/",
        "use": "controlled one-side thread installation in thin sections",
    },
    {
        "title": "Southco DZUS quarter-turn fasteners",
        "url": "https://southco.com/en_in_int/fasteners/emdzusemreg-quarter-turn-fasteners",
        "use": "captive, vibration-resistant repeated-access panel retention",
    },
    {
        "title": "HARTING compact railway connectors",
        "url": "https://www.harting.com/en-GB/space-saving-industrial-connectors-for-railway-vehicles",
        "use": "compact rail-qualified plug interfaces for lights, doors and displays",
    },
)


def small_component_standard_payload() -> dict[str, object]:
    """Machine-readable design and release boundary for the common system."""

    return {
        "document_revision": "A-DRAFT",
        "release_status": "design-reference-not-released",
        "principle": (
            "Use one datum rail and the smallest qualified fastener/connector family that "
            "matches load and service frequency; preserve supplier ownership of doors, "
            "glazing and safety-critical internal mechanisms."
        ),
        "service_rail": {
            "id": "OSR-RAIL-42",
            "nominal_section_mm": [SERVICE_RAIL_WIDTH_MM, SERVICE_RAIL_DEPTH_MM],
            "datum_pitch_mm": SERVICE_RAIL_DATUM_PITCH_MM,
            "material": "extruded aluminium rail with electrically isolated body attachments where required",
            "functions": [
                "repeatable mounting datum",
                "floating-nut capture",
                "cable and connector bracket attachment",
                "trim edge alignment",
            ],
            "release_evidence": [
                "fixture-specific load path calculation",
                "rail pull-out and slip test",
                "shock/vibration evidence",
                "galvanic-isolation and fire-material review",
            ],
        },
        "fastener_families": [asdict(item) for item in FASTENER_FAMILIES],
        "connector_families": [asdict(item) for item in CONNECTOR_FAMILIES],
        "lighting": {
            "main_modules_per_car": LIGHT_MODULES_PER_CAR,
            "module_length_mm": LIGHT_MODULE_LENGTH_MM,
            "emergency_modules_per_car": EMERGENCY_LIGHT_MODULES_PER_CAR,
            "door_threshold_modules_per_car": DOOR_THRESHOLD_LIGHTS_PER_CAR,
            "replacement_rule": "one module, two captive screws and one keyed plug; no field-cut strip or loose wire termination",
        },
        "door_interface": {
            "boundary": "complete certified supplier cassette including leaf, operator, lock, seals and controller",
            "osr_interface": "four adjustable carrier shoes, two datum pins, dry perimeter seal and one keyed service bracket",
            "release_gate": "supplier freeze, structural interface calculation and all applicable door safety tests",
        },
        "window_interface": {
            "boundary": "glass remains bonded to its supplier aluminium frame",
            "osr_interface": "replaceable pressure frame, dry outer seal, drain path and captive secondary retention",
            "replacement_rule": "remove internal pressure frame and withdraw cassette; do not cut adhesive at the carbody",
            "release_gate": "glazing certificate, retention calculation, seal compression and water-ingress test",
        },
        "authoritative_references": list(AUTHORITATIVE_REFERENCES),
    }


def _part(part: Part, label: str, color: Color) -> Part:
    part.label = label
    part.color = color
    return part


def _box(
    length: float,
    width: float,
    height: float,
    loc: tuple[float, float, float],
    label: str,
    color: Color,
) -> Part:
    return _part(Box(length, width, height).locate(Location(loc)), label, color)


def _cyl(
    radius: float,
    height: float,
    loc: tuple[float, float, float],
    label: str,
    color: Color,
) -> Part:
    return _part(Cylinder(radius=radius, height=height).locate(Location(loc)), label, color)


def _door_centres_x(dims: CarDimensions) -> list[float]:
    spacing = dims.body_length_mm / (dims.doors_per_side + 1)
    return [-dims.body_length_mm / 2.0 + (index + 1) * spacing for index in range(dims.doors_per_side)]


def _window_zones(dims: CarDimensions) -> list[tuple[float, float]]:
    doors = _door_centres_x(dims)
    half_length = dims.body_length_mm / 2.0
    half_door = DOOR_WIDTH_MM / 2.0
    edges = [-half_length] + doors + [half_length]
    zones: list[tuple[float, float]] = []
    for index in range(len(edges) - 1):
        left = edges[index] + (half_door if index > 0 else 0.0)
        right = edges[index + 1] - (half_door if index + 1 < len(edges) - 1 else 0.0)
        width = max(0.0, right - left - 2.0 * WINDOW_MARGIN_MM)
        if width >= 400.0:
            zones.append(((left + right) / 2.0, width))
    return zones


def universal_service_rail_installation(dims: CarDimensions = CarDimensions()) -> Compound:
    """Common ceiling, waist and seat-zone datum rails with splice markers."""

    parts: list[Part] = []
    usable_length = dims.body_length_mm - 3_000.0
    for y_sign in (-1.0, 1.0):
        for y, z, role in (
            (y_sign * 545.0, 2_900.0, "ceiling lighting and service"),
            (y_sign * (dims.body_width_mm / 2.0 - 155.0), 2_480.0, "upper fixture"),
            (y_sign * (dims.body_width_mm / 2.0 - 165.0), 1_080.0, "waist and passenger fixture"),
            (y_sign * (dims.body_width_mm / 2.0 - 410.0), 545.0, "seat and equipment"),
        ):
            parts.append(
                _box(
                    usable_length,
                    SERVICE_RAIL_WIDTH_MM,
                    SERVICE_RAIL_DEPTH_MM,
                    (0.0, y, z),
                    f"OSR-RAIL-42 {role} rail",
                    COLOR_RAIL,
                )
            )
            for x in range(-6_000, 6_001, 1_000):
                parts.append(
                    _box(
                        22.0,
                        SERVICE_RAIL_WIDTH_MM + 8.0,
                        SERVICE_RAIL_DEPTH_MM + 5.0,
                        (float(x), y, z),
                        "OSR-RAIL-42 one-metre inspection datum marker",
                        COLOR_ADAPTER,
                    )
                )
    return Compound(label="Universal OSR-RAIL-42 service rail installation", children=parts)


def modular_lighting_cassettes(dims: CarDimensions = CarDimensions()) -> Compound:
    """Twenty-two identical main lights plus emergency and doorway modules."""

    parts: list[Part] = []
    x_positions = [(-6_000.0 + index * LIGHT_MODULE_LENGTH_MM) for index in range(11)]
    for y_sign in (-1.0, 1.0):
        y = y_sign * 545.0
        for index, x in enumerate(x_positions, start=1):
            parts.extend(
                [
                    _box(
                        LIGHT_MODULE_LENGTH_MM - 18.0,
                        94.0,
                        42.0,
                        (x, y, 2_920.0),
                        f"1.2 m plug-in main lighting cassette {index}",
                        COLOR_LIGHT,
                    ),
                    _box(
                        56.0,
                        28.0,
                        28.0,
                        (x + LIGHT_MODULE_LENGTH_MM / 2.0 - 65.0, y + y_sign * 62.0, 2_900.0),
                        "OSR-CON-LV4 keyed lighting plug and strain relief",
                        COLOR_CONNECTOR,
                    ),
                ]
            )
            for fastener_x in (-LIGHT_MODULE_LENGTH_MM / 2.0 + 58.0, LIGHT_MODULE_LENGTH_MM / 2.0 - 58.0):
                parts.append(
                    _cyl(
                        7.0,
                        12.0,
                        (x + fastener_x, y, 2_945.0),
                        "OSR-FST-M6-CAPTIVE lighting cassette screw",
                        COLOR_FASTENER,
                    )
                )
    for x in (-4_800.0, -1_600.0, 1_600.0, 4_800.0):
        parts.append(
            _box(360.0, 150.0, 54.0, (x, 0.0, 2_930.0), "Independent-feed emergency light cassette", COLOR_EMERGENCY)
        )
    for x in _door_centres_x(dims):
        for y_sign in (-1.0, 1.0):
            parts.append(
                _box(
                    560.0,
                    54.0,
                    42.0,
                    (x, y_sign * (dims.body_width_mm / 2.0 - 390.0), 2_435.0),
                    "Door-threshold illumination cassette",
                    COLOR_EMERGENCY,
                )
            )
    return Compound(label="Modular main, emergency, and doorway lighting installation", children=parts)


def standard_fixture_adapters(dims: CarDimensions = CarDimensions()) -> Compound:
    """Repeatable rail adapters for seats, handholds, screens and cable trays."""

    parts: list[Part] = []
    for y_sign in (-1.0, 1.0):
        y = y_sign * (dims.body_width_mm / 2.0 - 360.0)
        for x in (-5_800.0, -4_200.0, -2_600.0, 2_600.0, 4_200.0, 5_800.0):
            parts.extend(
                [
                    _box(180.0, 120.0, 220.0, (x, y, 720.0), "Universal seat/handrail saddle adapter", COLOR_ADAPTER),
                    _box(96.0, 58.0, 34.0, (x, y_sign * (dims.body_width_mm / 2.0 - 170.0), 1_080.0), "Floating M8 rail-nut carrier", COLOR_FASTENER),
                ]
            )
            for offset in (-48.0, 48.0):
                parts.append(
                    _cyl(9.0, 18.0, (x + offset, y, 842.0), "OSR-FST-M8-FLOAT calculated fixture bolt", COLOR_FASTENER)
                )
    for x in _door_centres_x(dims):
        for y_sign in (-1.0, 1.0):
            parts.append(
                _box(
                    260.0,
                    86.0,
                    160.0,
                    (x, y_sign * (dims.body_width_mm / 2.0 - 195.0), 2_485.0),
                    "Common PIS/CCTV/door-service adapter",
                    COLOR_ADAPTER,
                )
            )
    return Compound(label="Standard passenger fixture and equipment adapter kit", children=parts)


def door_window_cassette_hardware(dims: CarDimensions = CarDimensions()) -> Compound:
    """Adjustable door carriers and dry-serviceable window pressure frames."""

    parts: list[Part] = []
    for x in _door_centres_x(dims):
        for y_sign in (-1.0, 1.0):
            y = y_sign * (dims.body_width_mm / 2.0 - 94.0)
            for x_offset in (-DOOR_WIDTH_MM / 2.0 - 155.0, DOOR_WIDTH_MM / 2.0 + 155.0):
                for z in (DOOR_SILL_HEIGHT_MM + 125.0, DOOR_SILL_HEIGHT_MM + DOOR_HEIGHT_MM + 125.0):
                    parts.extend(
                        [
                            _box(150.0, 72.0, 110.0, (x + x_offset, y, z), "Door cassette adjustable four-point carrier shoe", COLOR_ADAPTER),
                            _cyl(10.0, 22.0, (x + x_offset, y, z), "OSR-FST-M8-FLOAT door carrier bolt", COLOR_FASTENER),
                        ]
                    )
            parts.append(
                _box(
                    110.0,
                    82.0,
                    130.0,
                    (x - DOOR_WIDTH_MM / 2.0 - 310.0, y, 2_295.0),
                    "Keyed door power/data connector fixed bracket",
                    COLOR_CONNECTOR,
                )
            )
    for y_sign in (-1.0, 1.0):
        for x, width in _window_zones(dims):
            y = y_sign * (dims.body_width_mm / 2.0 - 46.0)
            centre_z = WINDOW_SILL_MM + WINDOW_HEIGHT_MM / 2.0
            frame_width = width + 210.0
            frame_height = WINDOW_HEIGHT_MM + 190.0
            parts.extend(
                [
                    _box(frame_width, 28.0, 48.0, (x, y, centre_z + frame_height / 2.0), "Replaceable window cassette pressure frame", COLOR_RAIL),
                    _box(frame_width, 28.0, 48.0, (x, y, centre_z - frame_height / 2.0), "Window pressure-frame lower rail", COLOR_RAIL),
                    _box(48.0, 28.0, frame_height, (x - frame_width / 2.0, y, centre_z), "Window pressure-frame left stile", COLOR_RAIL),
                    _box(48.0, 28.0, frame_height, (x + frame_width / 2.0, y, centre_z), "Window pressure-frame right stile", COLOR_RAIL),
                    _box(width + 155.0, 14.0, 24.0, (x, y_sign * (dims.body_width_mm / 2.0 - 28.0), centre_z + (WINDOW_HEIGHT_MM + 145.0) / 2.0), "Dry EPDM window cassette compression seal", COLOR_SEAL),
                    _box(width + 155.0, 14.0, 24.0, (x, y_sign * (dims.body_width_mm / 2.0 - 28.0), centre_z - (WINDOW_HEIGHT_MM + 145.0) / 2.0), "Dry EPDM window cassette lower seal", COLOR_SEAL),
                    _box(24.0, 14.0, WINDOW_HEIGHT_MM + 145.0, (x - (width + 155.0) / 2.0, y_sign * (dims.body_width_mm / 2.0 - 28.0), centre_z), "Dry EPDM window cassette left seal", COLOR_SEAL),
                    _box(24.0, 14.0, WINDOW_HEIGHT_MM + 145.0, (x + (width + 155.0) / 2.0, y_sign * (dims.body_width_mm / 2.0 - 28.0), centre_z), "Dry EPDM window cassette right seal", COLOR_SEAL),
                    _box(width + 245.0, 38.0, 42.0, (x, y, WINDOW_SILL_MM - 74.0), "Replaceable window drain and weep rail", COLOR_RAIL),
                ]
            )
            for x_fraction in (-0.4, -0.13, 0.13, 0.4):
                parts.append(
                    _cyl(8.0, 16.0, (x + x_fraction * width, y, WINDOW_SILL_MM + WINDOW_HEIGHT_MM + 105.0), "Captive M8 window pressure-frame fastener", COLOR_FASTENER)
                )
    return Compound(label="Simplified door and window cassette interface hardware", children=parts)


def simplified_small_component_package(dims: CarDimensions = CarDimensions()) -> Compound:
    """Complete common small-component package for one car."""

    return Compound(
        label="Simplified modular small-component package for one car",
        children=[
            universal_service_rail_installation(dims),
            modular_lighting_cassettes(dims),
            standard_fixture_adapters(dims),
            door_window_cassette_hardware(dims),
        ],
    )


__all__ = [
    "AUTHORITATIVE_REFERENCES",
    "CONNECTOR_FAMILIES",
    "DOOR_THRESHOLD_LIGHTS_PER_CAR",
    "EMERGENCY_LIGHT_MODULES_PER_CAR",
    "FASTENER_FAMILIES",
    "LIGHT_MODULE_LENGTH_MM",
    "LIGHT_MODULES_PER_CAR",
    "SERVICE_RAIL_DATUM_PITCH_MM",
    "SERVICE_RAIL_DEPTH_MM",
    "SERVICE_RAIL_WIDTH_MM",
    "ConnectorFamily",
    "FastenerFamily",
    "door_window_cassette_hardware",
    "modular_lighting_cassettes",
    "simplified_small_component_package",
    "small_component_standard_payload",
    "standard_fixture_adapters",
    "universal_service_rail_installation",
]
