"""FreeCAD/CalculiX screening FEA for rolling-stock structures.

This is a first-pass engineering screen, not a certification model. It
uses axis-aligned B31 beam/space-frame idealisations to check gross load
paths and generate solver-result PNGs for:

- the low-floor chassis supported at bogie interfaces,
- low-floor chassis AW3 proof and asymmetric twist cases,
- the bogie H-frame supported at axlebox/primary-suspension points,
- bogie longitudinal brake/traction reaction,
- the full car body frame supported at bogie locations,
- full body lateral sway/racking.

The script runs inside FreeCADCmd so the FEM workbench and bundled
CalculiX/Gmsh tools from the FreeCAD runtime are discoverable.
"""

from __future__ import annotations

import argparse
import importlib
import json
import math
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path


try:
    import FreeCAD as App  # type: ignore[import-not-found]
    import Part  # type: ignore[import-not-found]
except Exception as exc:  # pragma: no cover - only exercised outside FreeCAD.
    App = None  # type: ignore[assignment]
    Part = None  # type: ignore[assignment]
    _FREECAD_IMPORT_ERROR = exc
else:
    _FREECAD_IMPORT_ERROR = None

from osr_mech.rolling_stock.baseline import PROMOTED_LIGHT_METRO_CAR_LENGTH_MM


E_STEEL_MPA = 210_000.0
NU_STEEL = 0.30
S355_YIELD_MPA = 355.0
ALLOWABLE_SERVICE_MPA = 0.60 * S355_YIELD_MPA
HALF_CAR_LENGTH_MM = PROMOTED_LIGHT_METRO_CAR_LENGTH_MM / 2.0
BOGIE_CENTRE_X_MM = HALF_CAR_LENGTH_MM - 2_100.0
BOGIE_AUXILIARY_X_MM = HALF_CAR_LENGTH_MM - 900.0


@dataclass(frozen=True)
class Node:
    id: int
    x: float
    y: float
    z: float


@dataclass(frozen=True)
class Element:
    id: int
    n1: int
    n2: int
    section: str


@dataclass(frozen=True)
class BeamSection:
    name: str
    width_mm: float
    height_mm: float
    orientation: tuple[float, float, float] = (0.0, 0.0, -1.0)


@dataclass(frozen=True)
class Boundary:
    node: int
    first_dof: int
    last_dof: int
    value: float = 0.0


@dataclass(frozen=True)
class Load:
    node: int
    dof: int
    value_n: float
    label: str


@dataclass
class Study:
    slug: str
    title: str
    load_case: str
    nodes: list[Node]
    elements: list[Element]
    sections: dict[str, BeamSection]
    boundaries: list[Boundary]
    loads: list[Load]
    deflection_limit_mm: float
    plot_view: str = "xz"
    notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class StudyResult:
    slug: str
    title: str
    nodes: int
    elements: int
    total_applied_load_n: float
    total_vertical_load_n: float
    max_displacement_mm: float
    deflection_limit_mm: float
    max_von_mises_mpa: float
    safety_factor_to_yield: float
    solver_ok: bool
    result_png: str | None = None
    docs_result_png: str | None = None
    issue: str | None = None


@dataclass(frozen=True)
class SolverFields:
    displacements: dict[int, tuple[float, float, float]]
    element_von_mises_mpa: dict[int, float]


class ModelBuilder:
    def __init__(self) -> None:
        self._nodes: dict[tuple[float, float, float], int] = {}
        self.nodes: list[Node] = []
        self.elements: list[Element] = []

    def node(self, x: float, y: float, z: float) -> int:
        key = (round(x, 6), round(y, 6), round(z, 6))
        existing = self._nodes.get(key)
        if existing is not None:
            return existing
        node_id = len(self.nodes) + 1
        self._nodes[key] = node_id
        self.nodes.append(Node(node_id, x, y, z))
        return node_id

    def beam(self, p1: tuple[float, float, float], p2: tuple[float, float, float], section: str) -> None:
        if p1 == p2:
            return
        self.elements.append(
            Element(
                id=len(self.elements) + 1,
                n1=self.node(*p1),
                n2=self.node(*p2),
                section=section,
            )
        )

    def node_id(self, p: tuple[float, float, float]) -> int:
        return self.node(*p)


def _require_freecad() -> None:
    if App is None or Part is None:
        raise SystemExit(
            "FreeCAD Python modules are not importable. Run this with FreeCADCmd "
            "or mechanical-py/scripts/freecad_fea.sh.\n"
            f"Import error was: {_FREECAD_IMPORT_ERROR!r}"
        )


def _catalog_root() -> Path:
    return Path(__file__).resolve().parents[2] / "catalog"


def _safe_name(name: str) -> str:
    return "".join(ch if ch.isalnum() else "_" for ch in name).strip("_")


def _chunks(values: list[int], size: int = 12) -> list[list[int]]:
    return [values[i : i + size] for i in range(0, len(values), size)]


def chassis_bogie_study() -> Study:
    b = ModelBuilder()
    sections = {
        "SIDE_TORSION_BOX": BeamSection("SIDE_TORSION_BOX", 240.0, 430.0),
        "STRINGER": BeamSection("STRINGER", 165.0, 260.0),
        "KEEL_BOX": BeamSection("KEEL_BOX", 150.0, 250.0),
        "UPPER_CHORD": BeamSection("UPPER_CHORD", 90.0, 145.0),
        "CROSS_BEARER": BeamSection("CROSS_BEARER", 125.0, 220.0),
        "TORSION_TIE": BeamSection("TORSION_TIE", 165.0, 180.0),
        "BOLSTER": BeamSection("BOLSTER", 260.0, 280.0),
    }
    xs = [
        -HALF_CAR_LENGTH_MM,
        -BOGIE_AUXILIARY_X_MM,
        -BOGIE_CENTRE_X_MM,
        -4_200.0,
        -2_000.0,
        0.0,
        2_000.0,
        4_200.0,
        BOGIE_CENTRE_X_MM,
        BOGIE_AUXILIARY_X_MM,
        HALF_CAR_LENGTH_MM,
    ]
    ys = [-1_250.0, -700.0, -430.0, 0.0, 430.0, 700.0, 1_250.0]
    z = 350.0
    for y in (-1_250.0, 1_250.0):
        for a, c in zip(xs, xs[1:]):
            b.beam((a, y, z), (c, y, z), "SIDE_TORSION_BOX")
    for y in (-700.0, 700.0):
        for a, c in zip(xs[1:-1], xs[2:]):
            b.beam((a, y, z), (c, y, z), "STRINGER")
    for y in (-430.0, 430.0):
        for a, c in zip(xs[1:-1], xs[2:]):
            b.beam((a, y, z - 20.0), (c, y, z - 20.0), "KEEL_BOX")
    for y in (-730.0, 730.0):
        for a, c in zip(xs[1:-1], xs[2:]):
            b.beam((a, y, z + 165.0), (c, y, z + 165.0), "UPPER_CHORD")
    for x in xs:
        for a, c in zip(ys, ys[1:]):
            b.beam((x, a, z), (x, c, z), "CROSS_BEARER")
        if abs(x) <= 4_200.0:
            b.beam((x, -610.0, z + 140.0), (x, 610.0, z + 140.0), "TORSION_TIE")
    for x in (-BOGIE_CENTRE_X_MM, BOGIE_CENTRE_X_MM):
        for y in (-1_250.0, -700.0, 700.0, 1_250.0):
            b.beam((x - 520.0, y, z + 160.0), (x + 520.0, y, z + 160.0), "BOLSTER")
        b.beam((x, -1_250.0, z + 160.0), (x, 1_250.0, z + 160.0), "BOLSTER")
        for y in (-700.0, 700.0):
            b.beam((x - math.copysign(1_480.0, x), y, z - 20.0), (x, y, z + 160.0), "BOLSTER")
    supports = [
        b.node_id((-BOGIE_CENTRE_X_MM, -700.0, z)),
        b.node_id((-BOGIE_CENTRE_X_MM, 700.0, z)),
        b.node_id((BOGIE_CENTRE_X_MM, -700.0, z)),
        b.node_id((BOGIE_CENTRE_X_MM, 700.0, z)),
    ]
    load_nodes = [b.node_id((x, y, z)) for x in xs[1:-1] for y in (-700.0, 0.0, 700.0)]
    total_load_n = -360_000.0
    load_each = total_load_n / len(load_nodes)
    boundaries = [
        Boundary(supports[0], 1, 6),
        Boundary(supports[1], 2, 3),
        Boundary(supports[2], 3, 3),
        Boundary(supports[3], 3, 3),
    ]
    loads = [Load(node, 3, load_each, "distributed chassis/body/payload gravity") for node in load_nodes]
    return Study(
        slug="chassis-bogie-screen",
        title="Low-floor chassis supported at bogie connectors",
        load_case="360 kN vertical service load distributed over low-floor and high-floor bearer grid",
        nodes=b.nodes,
        elements=b.elements,
        sections=sections,
        boundaries=boundaries,
        loads=loads,
        deflection_limit_mm=25.0,
        plot_view="xz",
        notes=[
            "Bogie support points represent four secondary-air-spring/chassis interface pads.",
            "Reworked chassis uses deep side torsion boxes, twin keel beams, upper battery-zone chords, and stiffer cross-bearers.",
        ],
    )


def _variant(
    base: Study,
    *,
    slug: str,
    title: str,
    load_case: str,
    loads: list[Load],
    deflection_limit_mm: float,
    plot_view: str,
    notes: list[str],
) -> Study:
    return Study(
        slug=slug,
        title=title,
        load_case=load_case,
        nodes=base.nodes,
        elements=base.elements,
        sections=base.sections,
        boundaries=base.boundaries,
        loads=loads,
        deflection_limit_mm=deflection_limit_mm,
        plot_view=plot_view,
        notes=notes,
    )


def chassis_aw3_proof_study() -> Study:
    base = chassis_bogie_study()
    return _variant(
        base,
        slug="chassis-aw3-proof-screen",
        title="Low-floor chassis AW3 vertical proof-load screen",
        load_case="540 kN vertical proof load: 1.5 x the baseline 360 kN service gravity case",
        loads=[
            Load(load.node, load.dof, load.value_n * 1.5, "1.5 x distributed AW3 proof gravity")
            for load in base.loads
        ],
        deflection_limit_mm=35.0,
        plot_view="xz",
        notes=[
            "Uses the same bogie support pads as the service screen with a 1.5 x vertical load multiplier.",
            "This is a static proof-load screen only; fatigue and local weld toe stresses remain v2 work.",
        ],
    )


def chassis_track_twist_study() -> Study:
    base = chassis_bogie_study()
    node_by_id = {node.id: node for node in base.nodes}
    loads: list[Load] = []
    for load in base.loads:
        node = node_by_id[load.node]
        if node.y < -100.0:
            factor = 1.25
        elif node.y > 100.0:
            factor = 0.65
        else:
            factor = 1.10
        loads.append(Load(load.node, load.dof, load.value_n * factor, "track-twist asymmetric gravity"))
    roof_anchor_nodes = [
        base.nodes[min(range(len(base.nodes)), key=lambda i: (base.nodes[i].x - x) ** 2 + (base.nodes[i].y - y) ** 2)].id
        for x, y in ((-2_000.0, -700.0), (2_000.0, -700.0))
    ]
    loads.extend(Load(node, 3, -12_500.0, "diagonal roof/equipment offset allowance") for node in roof_anchor_nodes)
    return _variant(
        base,
        slug="chassis-track-twist-screen",
        title="Low-floor chassis asymmetric track-twist screen",
        load_case="Asymmetric 65/110/125% side load bias plus 25 kN diagonal equipment offset",
        loads=loads,
        deflection_limit_mm=30.0,
        plot_view="xz",
        notes=[
            "Represents uneven passenger/load distribution during a track-twist or low-speed ramp transition.",
            "The diagonal equipment allowance biases the roof-side service mass onto one chassis side.",
        ],
    )


def bogie_frame_study() -> Study:
    b = ModelBuilder()
    sections = {
        "SIDE_BEAM": BeamSection("SIDE_BEAM", 160.0, 280.0),
        "CROSS_MEMBER": BeamSection("CROSS_MEMBER", 180.0, 220.0),
        "BOLSTER": BeamSection("BOLSTER", 220.0, 260.0),
        "LINK": BeamSection("LINK", 90.0, 110.0, orientation=(1.0, 0.0, 0.0)),
    }
    xs = [-1_750.0, -1_050.0, 0.0, 1_050.0, 1_750.0]
    y_side = (-1_100.0, 1_100.0)
    z = 620.0
    for y in y_side:
        for a, c in zip(xs, xs[1:]):
            b.beam((a, y, z), (c, y, z), "SIDE_BEAM")
    for x in (-1_500.0, 0.0, 1_500.0):
        for a, c in zip([-1_100.0, -750.0, 0.0, 750.0, 1_100.0], [-750.0, 0.0, 750.0, 1_100.0]):
            b.beam((x, a, z), (x, c, z), "CROSS_MEMBER")
    for y in (-750.0, 750.0):
        b.beam((-360.0, y, z + 120.0), (360.0, y, z + 120.0), "BOLSTER")
        b.beam((0.0, y, z), (0.0, y, z + 120.0), "LINK")
    supports = [
        b.node_id((-1_050.0, -1_100.0, z)),
        b.node_id((-1_050.0, 1_100.0, z)),
        b.node_id((1_050.0, -1_100.0, z)),
        b.node_id((1_050.0, 1_100.0, z)),
    ]
    load_nodes = [b.node_id((0.0, -750.0, z + 120.0)), b.node_id((0.0, 750.0, z + 120.0))]
    boundaries = [
        Boundary(supports[0], 1, 6),
        Boundary(supports[1], 2, 3),
        Boundary(supports[2], 3, 3),
        Boundary(supports[3], 3, 3),
    ]
    loads = [Load(node, 3, -80_000.0, "secondary air-spring vertical load") for node in load_nodes]
    return Study(
        slug="bogie-frame-screen",
        title="Motor/trailer bogie H-frame screening model",
        load_case="160 kN bogie vertical load applied through two secondary-air-spring seats",
        nodes=b.nodes,
        elements=b.elements,
        sections=sections,
        boundaries=boundaries,
        loads=loads,
        deflection_limit_mm=5.0,
        plot_view="xz",
        notes=[
            "Axlebox/primary-suspension support nodes constrain vertical displacement.",
            "Motor reaction brackets are not included in this load case; use the motor connector CAD for interface review.",
        ],
    )


def bogie_brake_traction_study() -> Study:
    base = bogie_frame_study()
    loads = list(base.loads)
    secondary_nodes = [load.node for load in base.loads]
    loads.extend(
        Load(node, 1, 30_000.0, "longitudinal brake/traction reaction at secondary seat")
        for node in secondary_nodes
    )
    return _variant(
        base,
        slug="bogie-brake-traction-screen",
        title="Bogie frame brake/traction longitudinal load screen",
        load_case="160 kN vertical bogie load plus 60 kN longitudinal brake/traction reaction",
        loads=loads,
        deflection_limit_mm=6.0,
        plot_view="xz",
        notes=[
            "Adds a longitudinal force path through the secondary-seat structure on top of the vertical bogie case.",
            "Gearbox, axle, and detailed motor-bracket local stresses are still outside this beam-model screen.",
        ],
    )


def full_body_frame_study() -> Study:
    b = ModelBuilder()
    sections = {
        # The first lateral-sway screen was 0.564 mm over target. The
        # revised body adds a light diagonal racking frame and modestly
        # increases the side/roof bearer sections.
        "SIDE_SILL": BeamSection("SIDE_SILL", 185.0, 330.0),
        "WAIST_RAIL": BeamSection("WAIST_RAIL", 135.0, 120.0),
        "CANT_RAIL": BeamSection("CANT_RAIL", 150.0, 190.0),
        "ROOF_RAIL": BeamSection("ROOF_RAIL", 130.0, 130.0),
        "POST": BeamSection("POST", 135.0, 135.0, orientation=(1.0, 0.0, 0.0)),
        "CROSS_TIE": BeamSection("CROSS_TIE", 95.0, 135.0),
        "RACK_DIAGONAL": BeamSection("RACK_DIAGONAL", 80.0, 120.0),
    }
    xs = [
        -HALF_CAR_LENGTH_MM,
        -BOGIE_CENTRE_X_MM,
        -4_200.0,
        -2_100.0,
        0.0,
        2_100.0,
        4_200.0,
        BOGIE_CENTRE_X_MM,
        HALF_CAR_LENGTH_MM,
    ]
    ys = [-1_350.0, 1_350.0]
    levels = [350.0, 1_500.0, 2_800.0, 3_450.0]
    for y in ys:
        for z, section in ((350.0, "SIDE_SILL"), (1_500.0, "WAIST_RAIL"), (2_800.0, "CANT_RAIL"), (3_450.0, "ROOF_RAIL")):
            for a, c in zip(xs, xs[1:]):
                b.beam((a, y, z), (c, y, z), section)
        for a, c in zip(xs, xs[1:]):
            b.beam((a, y, 1_500.0), (c, y, 2_800.0), "RACK_DIAGONAL")
            b.beam((a, y, 2_800.0), (c, y, 1_500.0), "RACK_DIAGONAL")
        for x in xs:
            for a, c in zip(levels, levels[1:]):
                b.beam((x, y, a), (x, y, c), "POST")
    for x in xs:
        for z in (350.0, 3_450.0):
            b.beam((x, -1_350.0, z), (x, 1_350.0, z), "CROSS_TIE")
    supports = [
        b.node_id((-BOGIE_CENTRE_X_MM, -1_350.0, 350.0)),
        b.node_id((-BOGIE_CENTRE_X_MM, 1_350.0, 350.0)),
        b.node_id((BOGIE_CENTRE_X_MM, -1_350.0, 350.0)),
        b.node_id((BOGIE_CENTRE_X_MM, 1_350.0, 350.0)),
    ]
    floor_nodes = [b.node_id((x, y, 350.0)) for x in xs[1:-1] for y in ys]
    body_payload_load_n = -420_000.0
    installed_systems_load_n = -60_000.0  # doors, seats, HVAC, lighting, screens, batteries, fixtures
    loads = [
        Load(node, 3, body_payload_load_n / len(floor_nodes), "distributed body/interior/passenger gravity")
        for node in floor_nodes
    ]
    loads.extend(
        Load(node, 3, installed_systems_load_n / len(floor_nodes), "installed doors/seats/HVAC/lighting/fixtures")
        for node in floor_nodes
    )
    roof_load_nodes = [b.node_id((x, y, 3_450.0)) for x in (-BOGIE_CENTRE_X_MM, BOGIE_CENTRE_X_MM) for y in ys]
    loads.extend(Load(node, 3, -7_500.0, "roof HVAC/PV concentrated allowance") for node in roof_load_nodes)
    boundaries = [
        Boundary(supports[0], 1, 6),
        Boundary(supports[1], 2, 3),
        Boundary(supports[2], 3, 3),
        Boundary(supports[3], 3, 3),
    ]
    return Study(
        slug="full-body-frame-screen",
        title="Full car body side/roof frame screening model",
        load_case="420 kN body/payload plus 60 kN installed systems and 30 kN roof equipment allowance",
        nodes=b.nodes,
        elements=b.elements,
        sections=sections,
        boundaries=boundaries,
        loads=loads,
        deflection_limit_mm=15.0,
        plot_view="xz",
        notes=[
            "Side posts, side sills, waist rails, cant rails, and roof bows are idealised as S355 beams.",
            "Revised body includes diagonal side-frame racking members added after the initial lateral-sway exceedance.",
            "Composite panels and glazing are treated as non-structural for this screening pass.",
        ],
    )


def full_body_lateral_sway_study() -> Study:
    base = full_body_frame_study()
    sway_nodes = [
        node.id
        for node in base.nodes
        if abs(node.y) > 1_000.0 and node.z >= 1_500.0 and abs(node.x) < HALF_CAR_LENGTH_MM
    ]
    lateral_total_n = 165_000.0  # body/interior plus installed systems at 0.15 g
    loads = [
        Load(node, 2, lateral_total_n / len(sway_nodes), "0.15 g body/interior lateral sway equivalent")
        for node in sway_nodes
    ]
    return _variant(
        base,
        slug="full-body-lateral-sway-screen",
        title="Full car body lateral sway screen",
        load_case="165 kN lateral body/interior/installed-systems equivalent load through side posts, waist rails, and cant rails",
        loads=loads,
        deflection_limit_mm=20.0,
        plot_view="xy",
        notes=[
            "Applies an approximate 0.15 g lateral inertial load through the occupied side-frame height.",
            "The current candidate includes diagonal side-frame racking members and enlarged side/roof bearers.",
            "This complements the vertical body frame case; it is not a modal, ride, or fatigue analysis.",
        ],
    )


def _full_set_spine_model() -> tuple[ModelBuilder, dict[str, BeamSection], list[float], list[float]]:
    b = ModelBuilder()
    sections = {
        "LONGITUDINAL_SILL": BeamSection("LONGITUDINAL_SILL", 260.0, 430.0),
        "CENTRE_SPINE": BeamSection("CENTRE_SPINE", 220.0, 360.0),
        "CROSS_TIE": BeamSection("CROSS_TIE", 150.0, 240.0),
        "TRAIN_TO_TRAIN_LINK": BeamSection("TRAIN_TO_TRAIN_LINK", 240.0, 300.0),
        "UPPER_GANGWAY_LINK": BeamSection("UPPER_GANGWAY_LINK", 120.0, 160.0),
    }
    total_length = 9 * PROMOTED_LIGHT_METRO_CAR_LENGTH_MM
    start_x = -total_length / 2.0
    car_ends = [start_x + i * PROMOTED_LIGHT_METRO_CAR_LENGTH_MM for i in range(10)]
    xs = sorted(
        set(
            car_ends
            + [start_x + i * PROMOTED_LIGHT_METRO_CAR_LENGTH_MM + offset for i in range(9) for offset in (2_100.0, 8_250.0, 14_400.0)]
        )
    )
    ys = [-1_150.0, 0.0, 1_150.0]
    z = 720.0
    roof_z = 2_850.0
    for y in (-1_150.0, 1_150.0):
        for a, c in zip(xs, xs[1:]):
            section = "TRAIN_TO_TRAIN_LINK" if any(a < boundary < c for boundary in (car_ends[3], car_ends[6])) else "LONGITUDINAL_SILL"
            b.beam((a, y, z), (c, y, z), section)
    for a, c in zip(xs, xs[1:]):
        b.beam((a, 0.0, z - 70.0), (c, 0.0, z - 70.0), "CENTRE_SPINE")
    for x in xs:
        b.beam((x, -1_150.0, z), (x, 1_150.0, z), "CROSS_TIE")
    for boundary in (car_ends[3], car_ends[6]):
        for y in (-760.0, 760.0):
            b.beam((boundary - 620.0, y, roof_z), (boundary + 620.0, y, roof_z), "UPPER_GANGWAY_LINK")
            b.beam((boundary - 620.0, y, z), (boundary + 620.0, y, z), "TRAIN_TO_TRAIN_LINK")
        b.beam((boundary, -1_150.0, z), (boundary, 1_150.0, z), "TRAIN_TO_TRAIN_LINK")
    return b, sections, xs, car_ends


def full_set_longitudinal_buff_study() -> Study:
    b, sections, _xs, car_ends = _full_set_spine_model()
    z = 720.0
    fixed_nodes = [
        b.node_id((car_ends[0], -1_150.0, z)),
        b.node_id((car_ends[0], 0.0, z - 70.0)),
        b.node_id((car_ends[0], 1_150.0, z)),
    ]
    load_nodes = [
        b.node_id((car_ends[-1], -1_150.0, z)),
        b.node_id((car_ends[-1], 0.0, z - 70.0)),
        b.node_id((car_ends[-1], 1_150.0, z)),
    ]
    boundaries = [Boundary(fixed_nodes[0], 1, 6), Boundary(fixed_nodes[1], 1, 3), Boundary(fixed_nodes[2], 1, 3)]
    loads = [Load(node, 1, -180_000.0 / len(load_nodes), "full-set longitudinal buff/draft load") for node in load_nodes]
    return Study(
        slug="full-set-longitudinal-buff-screen",
        title="Three-train full-set longitudinal buff/draft screen",
        load_case="180 kN longitudinal buff/draft load through the 148.5 m full-set spine and two open train-to-train joints",
        nodes=b.nodes,
        elements=b.elements,
        sections=sections,
        boundaries=boundaries,
        loads=loads,
        deflection_limit_mm=35.0,
        plot_view="xz",
        notes=[
            "Models three LM3 modules as one 148.5 m spine with two train-to-train open joints.",
            "The load is a gross service/recovery screen, not an EN 15227 crash case.",
        ],
    )


def full_set_vertical_service_study() -> Study:
    b, sections, xs, car_ends = _full_set_spine_model()
    z = 720.0
    support_xs = [
        car_ends[i] + PROMOTED_LIGHT_METRO_CAR_LENGTH_MM / 2.0 + sign * BOGIE_CENTRE_X_MM
        for i in range(9)
        for sign in (-1.0, 1.0)
    ]
    supports = [
        b.node_id((support_x, y, z))
        for support_x in support_xs
        for y in (-1_150.0, 1_150.0)
    ]
    boundaries = [Boundary(supports[0], 1, 6)]
    boundaries.extend(Boundary(node, 3, 3) for node in supports[1:])
    load_nodes = [b.node_id((x, y, z)) for x in xs[1:-1] for y in (-1_150.0, 0.0, 1_150.0)]
    total_load_n = -1_080_000.0
    loads = [Load(node, 3, total_load_n / len(load_nodes), "nine-car distributed service gravity") for node in load_nodes]
    for boundary in (car_ends[3], car_ends[6]):
        loads.append(Load(b.node_id((boundary, 0.0, z)), 3, -35_000.0, "train-to-train joint vertical allowance"))
    return Study(
        slug="full-set-vertical-service-screen",
        title="Three-train full-set vertical service screen",
        load_case="1,080 kN distributed nine-car service gravity plus 70 kN across two open train-to-train joints",
        nodes=b.nodes,
        elements=b.elements,
        sections=sections,
        boundaries=boundaries,
        loads=loads,
        deflection_limit_mm=45.0,
        plot_view="xz",
        notes=[
            "Supports represent all 18 bogies in the full-set example.",
            "The two open train-to-train joints receive explicit vertical allowances for gangway, threshold, and passenger transfer loads.",
        ],
    )


def _train_to_train_joint_model() -> tuple[ModelBuilder, dict[str, BeamSection], list[int], list[int]]:
    b = ModelBuilder()
    oblique_orientation = (1.0, 1.0, 1.0)
    sections = {
        "END_RING": BeamSection("END_RING", 240.0, 360.0, oblique_orientation),
        "LOWER_DRAWBAR": BeamSection("LOWER_DRAWBAR", 320.0, 420.0, oblique_orientation),
        "THRESHOLD_BRIDGE": BeamSection("THRESHOLD_BRIDGE", 240.0, 240.0, oblique_orientation),
        "UPPER_LINK": BeamSection("UPPER_LINK", 160.0, 220.0, oblique_orientation),
        "PORTAL_TIE": BeamSection("PORTAL_TIE", 160.0, 260.0, oblique_orientation),
    }
    left_x = -720.0
    right_x = 720.0
    ys = [-1_080.0, -760.0, 0.0, 760.0, 1_080.0]
    levels = [720.0, 760.0, 1_500.0, 2_850.0]
    for x in (left_x, right_x):
        for y in (-1_080.0, 1_080.0):
            for a, c in zip(levels, levels[1:]):
                b.beam((x, y, a), (x, y, c), "END_RING")
        for z in levels:
            for a, c in zip(ys, ys[1:]):
                b.beam((x, a, z), (x, c, z), "PORTAL_TIE")
    for y in (-760.0, 0.0, 760.0):
        b.beam((left_x, y, 760.0), (right_x, y, 760.0), "THRESHOLD_BRIDGE")
    for y in (-520.0, 520.0):
        b.beam((left_x, y, 720.0), (right_x, y, 720.0), "LOWER_DRAWBAR")
        b.beam((left_x, y, 2_850.0), (right_x, y, 2_850.0), "UPPER_LINK")
    left_supports = [b.node_id((left_x, y, z)) for y in ys for z in levels]
    right_load_nodes = [b.node_id((right_x, y, z)) for y in (-760.0, 0.0, 760.0) for z in (760.0, 1_500.0, 2_850.0)]
    return b, sections, left_supports, right_load_nodes


def train_to_train_joint_vertical_study() -> Study:
    b, sections, supports, load_nodes = _train_to_train_joint_model()
    boundaries = [Boundary(supports[0], 1, 6)]
    boundaries.extend(Boundary(node, 3, 3) for node in supports[1:])
    loads = [Load(node, 3, -90_000.0 / len(load_nodes), "open-joint vertical passenger/gangway load") for node in load_nodes]
    return Study(
        slug="train-to-train-joint-vertical-screen",
        title="Train-to-train open joint vertical load screen",
        load_case="90 kN vertical load through open portal, threshold bridge, lower drawbar, and upper links",
        nodes=b.nodes,
        elements=b.elements,
        sections=sections,
        boundaries=boundaries,
        loads=loads,
        deflection_limit_mm=12.0,
        plot_view="xz",
        notes=[
            "Screens the local common end-interface carrier rings and open gangway cassette.",
            "The fixed-side ring is supported along its full moulded end-frame interface, matching the chassis/body pick-up concept.",
            "Passenger threshold bridge and gangway loads are included as vertical distributed loads.",
        ],
    )


def train_to_train_joint_lateral_sway_study() -> Study:
    b, sections, supports, load_nodes = _train_to_train_joint_model()
    boundaries = [Boundary(supports[0], 1, 6)]
    boundaries.extend(Boundary(node, 2, 2) for node in supports[1:])
    loads = [Load(node, 2, 55_000.0 / len(load_nodes), "open-joint lateral/racking load") for node in load_nodes]
    return Study(
        slug="train-to-train-joint-lateral-sway-screen",
        title="Train-to-train open joint lateral/racking screen",
        load_case="55 kN lateral load through open portal clamp frames, upper links, and threshold bridge",
        nodes=b.nodes,
        elements=b.elements,
        sections=sections,
        boundaries=boundaries,
        loads=loads,
        deflection_limit_mm=16.0,
        plot_view="xy",
        notes=[
            "Complements the full-set vertical and longitudinal screens with a local racking case.",
            "The fixed-side ring is supported laterally along its full moulded end-frame interface.",
            "Supplier bellows fabric, rubber fatigue, clamps, and fastener details still require supplier proof evidence.",
        ],
    )


def all_studies() -> list[Study]:
    return [
        chassis_bogie_study(),
        chassis_aw3_proof_study(),
        chassis_track_twist_study(),
        bogie_frame_study(),
        bogie_brake_traction_study(),
        full_body_frame_study(),
        full_body_lateral_sway_study(),
        full_set_longitudinal_buff_study(),
        full_set_vertical_service_study(),
        train_to_train_joint_vertical_study(),
        train_to_train_joint_lateral_sway_study(),
    ]


def _write_inp(study: Study, path: Path) -> None:
    section_elements: dict[str, list[Element]] = {name: [] for name in study.sections}
    for element in study.elements:
        section_elements[element.section].append(element)
    all_node_ids = [node.id for node in study.nodes]
    all_element_ids = [element.id for element in study.elements]

    lines: list[str] = [
        "*HEADING",
        study.title,
        "*NODE",
    ]
    lines.extend(f"{node.id},{node.x:.6f},{node.y:.6f},{node.z:.6f}" for node in study.nodes)
    lines.append("*NSET,NSET=ALLN")
    lines.extend(",".join(str(v) for v in chunk) for chunk in _chunks(all_node_ids))
    lines.append("*ELSET,ELSET=ALLE")
    lines.extend(",".join(str(v) for v in chunk) for chunk in _chunks(all_element_ids))
    for section_name, elements in section_elements.items():
        if not elements:
            continue
        lines.append(f"*ELEMENT,TYPE=B31,ELSET={section_name}")
        lines.extend(f"{element.id},{element.n1},{element.n2}" for element in elements)
    lines.extend(
        [
            "*MATERIAL,NAME=S355",
            "*ELASTIC",
            f"{E_STEEL_MPA:.1f},{NU_STEEL:.3f}",
        ]
    )
    for section in study.sections.values():
        lines.append(f"*BEAM SECTION,ELSET={section.name},MATERIAL=S355,SECTION=RECT")
        lines.append(f"{section.width_mm:.6f},{section.height_mm:.6f}")
        ox, oy, oz = section.orientation
        lines.append(f"{ox:.6f},{oy:.6f},{oz:.6f}")
    lines.append("*BOUNDARY")
    lines.extend(
        f"{bc.node},{bc.first_dof},{bc.last_dof},{bc.value:.6f}" for bc in study.boundaries
    )
    lines.extend(["*STEP", "*STATIC", "*CLOAD"])
    lines.extend(f"{load.node},{load.dof},{load.value_n:.6f}" for load in study.loads)
    lines.extend(
        [
            "*NODE PRINT,NSET=ALLN",
            "U",
            "*EL PRINT,ELSET=ALLE",
            "S",
            "*END STEP",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def _von_mises(vals: tuple[float, float, float, float, float, float]) -> float:
    sxx, syy, szz, sxy, sxz, syz = vals
    return math.sqrt(
        0.5 * ((sxx - syy) ** 2 + (syy - szz) ** 2 + (szz - sxx) ** 2)
        + 3.0 * (sxy**2 + sxz**2 + syz**2)
    )


def _parse_dat_fields(path: Path) -> SolverFields:
    displacements: dict[int, tuple[float, float, float]] = {}
    element_von_mises_mpa: dict[int, float] = {}
    mode: str | None = None
    if not path.exists():
        return SolverFields(displacements=displacements, element_von_mises_mpa=element_von_mises_mpa)
    for raw in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw.strip()
        lower = line.lower()
        if "displacements" in lower:
            mode = "u"
            continue
        if "stresses" in lower:
            mode = "s"
            continue
        if not line:
            continue
        parts = line.split()
        try:
            if mode == "u" and len(parts) == 4:
                node = int(float(parts[0]))
                ux, uy, uz = (float(v) for v in parts[1:4])
                displacements[node] = (ux, uy, uz)
            elif mode == "s" and len(parts) == 8:
                element = int(float(parts[0]))
                stresses = tuple(float(v) for v in parts[2:8])
                vm = _von_mises(stresses)  # type: ignore[arg-type]
                element_von_mises_mpa[element] = max(element_von_mises_mpa.get(element, 0.0), vm)
        except ValueError:
            continue
    return SolverFields(displacements=displacements, element_von_mises_mpa=element_von_mises_mpa)


def _result_maxima(fields: SolverFields) -> tuple[float, float]:
    max_disp = 0.0
    for ux, uy, uz in fields.displacements.values():
        max_disp = max(max_disp, math.sqrt(ux * ux + uy * uy + uz * uz))
    max_vm = max(fields.element_von_mises_mpa.values(), default=0.0)
    return max_disp, max_vm


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(_repo_root()))
    except ValueError:
        return str(path)


def _markdown_link_path(path_text: str, base_dir: Path) -> str:
    path = Path(path_text)
    if not path.is_absolute():
        path = _repo_root() / path
    return os.path.relpath(path, base_dir)


def _project_point(
    node: Node,
    displacement: tuple[float, float, float],
    *,
    scale: float,
    view: str,
) -> tuple[float, float]:
    x = node.x + displacement[0] * scale
    y = node.y + displacement[1] * scale
    z = node.z + displacement[2] * scale
    if view == "xy":
        return x, y
    if view == "yz":
        return y, z
    return x, z


def _view_labels(view: str) -> tuple[str, str]:
    if view == "xy":
        return "X mm", "Y mm"
    if view == "yz":
        return "Y mm", "Z mm"
    return "X mm", "Z mm"


def _load_components(loads: list[Load]) -> tuple[float, float, float]:
    fx = sum(load.value_n for load in loads if load.dof == 1)
    fy = sum(load.value_n for load in loads if load.dof == 2)
    fz = sum(load.value_n for load in loads if load.dof == 3)
    return fx, fy, fz


def _total_applied_load(loads: list[Load]) -> float:
    return sum(abs(load.value_n) for load in loads)


def _strip_trailing_whitespace(path: Path) -> None:
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8", errors="ignore")
    stripped = "\n".join(line.rstrip() for line in text.splitlines())
    if text.endswith("\n"):
        stripped += "\n"
    path.write_text(stripped, encoding="utf-8")


def _write_result_png(
    *,
    study: Study,
    result: StudyResult,
    fields: SolverFields,
    path: Path,
) -> None:
    if not fields.displacements:
        return
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.collections import LineCollection
    from matplotlib.colors import Normalize

    node_by_id = {node.id: node for node in study.nodes}
    max_disp = max(result.max_displacement_mm, 1e-9)
    xs = [node.x for node in study.nodes]
    ys = [node.y for node in study.nodes]
    zs = [node.z for node in study.nodes]
    span = max(max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs), 1.0)
    deformation_scale = min(max(span * 0.08 / max_disp, 1.0), 250.0)
    view = study.plot_view

    undeformed_segments: list[tuple[tuple[float, float], tuple[float, float]]] = []
    deformed_segments: list[tuple[tuple[float, float], tuple[float, float]]] = []
    values: list[float] = []
    for element in study.elements:
        n1 = node_by_id[element.n1]
        n2 = node_by_id[element.n2]
        zero = (0.0, 0.0, 0.0)
        undeformed_segments.append(
            (
                _project_point(n1, zero, scale=0.0, view=view),
                _project_point(n2, zero, scale=0.0, view=view),
            )
        )
        deformed_segments.append(
            (
                _project_point(n1, fields.displacements.get(n1.id, zero), scale=deformation_scale, view=view),
                _project_point(n2, fields.displacements.get(n2.id, zero), scale=deformation_scale, view=view),
            )
        )
        values.append(fields.element_von_mises_mpa.get(element.id, 0.0))

    path.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(12.5, 7.5), dpi=150)
    ax.set_facecolor("#f7f8fb")
    ax.add_collection(LineCollection(undeformed_segments, colors="#bcc4cc", linewidths=0.9, alpha=0.55))
    vmax = max(result.max_von_mises_mpa, 1.0)
    stress_lines = LineCollection(
        deformed_segments,
        array=values,
        cmap="turbo",
        norm=Normalize(vmin=0.0, vmax=vmax),
        linewidths=3.2,
    )
    ax.add_collection(stress_lines)
    cbar = fig.colorbar(stress_lines, ax=ax, fraction=0.036, pad=0.018)
    cbar.set_label("von Mises stress, MPa")

    support_nodes = sorted({bc.node for bc in study.boundaries})
    support_points = [
        _project_point(node_by_id[node_id], (0.0, 0.0, 0.0), scale=0.0, view=view)
        for node_id in support_nodes
        if node_id in node_by_id
    ]
    if support_points:
        ax.scatter(
            [p[0] for p in support_points],
            [p[1] for p in support_points],
            marker="s",
            s=32,
            c="#127333",
            label="supports",
            zorder=3,
        )
    load_points = [
        _project_point(node_by_id[load.node], (0.0, 0.0, 0.0), scale=0.0, view=view)
        for load in study.loads
        if load.node in node_by_id
    ]
    if load_points:
        ax.scatter(
            [p[0] for p in load_points],
            [p[1] for p in load_points],
            marker="v",
            s=22,
            c="#bc241d",
            label="load nodes",
            alpha=0.80,
            zorder=4,
        )

    all_points = [point for segment in undeformed_segments + deformed_segments for point in segment]
    min_x, max_x = min(p[0] for p in all_points), max(p[0] for p in all_points)
    min_y, max_y = min(p[1] for p in all_points), max(p[1] for p in all_points)
    pad_x = max((max_x - min_x) * 0.07, 500.0)
    pad_y = max((max_y - min_y) * 0.12, 350.0)
    ax.set_xlim(min_x - pad_x, max_x + pad_x)
    ax.set_ylim(min_y - pad_y, max_y + pad_y)
    ax.set_aspect("equal", adjustable="box")
    xlabel, ylabel = _view_labels(view)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    fx, fy, fz = _load_components(study.loads)
    status = "OK" if result.solver_ok and result.issue is None else f"Review: {result.issue}"
    sf = "inf" if math.isinf(result.safety_factor_to_yield) else f"{result.safety_factor_to_yield:.1f}"
    ax.set_title(f"{study.title}\n{study.load_case}", fontsize=12)
    ax.text(
        0.01,
        0.01,
        (
            f"Max displacement: {result.max_displacement_mm:.3f} mm "
            f"(limit {result.deflection_limit_mm:.1f} mm)\n"
            f"Max von Mises: {result.max_von_mises_mpa:.1f} MPa; "
            f"SF to S355 yield: {sf}; status: {status}\n"
            f"Resultant load components: Fx {fx/1000:.1f} kN, "
            f"Fy {fy/1000:.1f} kN, Fz {fz/1000:.1f} kN; "
            f"deformation amplified x{deformation_scale:.0f}"
        ),
        transform=ax.transAxes,
        fontsize=8.5,
        va="bottom",
        ha="left",
        bbox={"boxstyle": "round,pad=0.35", "facecolor": "white", "edgecolor": "#d4d8de", "alpha": 0.92},
    )
    ax.legend(loc="upper right", fontsize=8)
    ax.grid(color="#dfe3e8", linewidth=0.6, alpha=0.8)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def _ccx_deck_stem(study: Study) -> str:
    """Return the deck stem passed to ccx from inside the study folder."""

    return study.slug


def _run_ccx(study: Study, out_dir: Path, png_out_dir: Path | None = None) -> StudyResult:
    out_dir.mkdir(parents=True, exist_ok=True)
    inp = out_dir / f"{study.slug}.inp"
    _write_inp(study, inp)
    ccx = shutil.which("ccx")
    if ccx is None:
        return StudyResult(
            slug=study.slug,
            title=study.title,
            nodes=len(study.nodes),
            elements=len(study.elements),
            total_applied_load_n=_total_applied_load(study.loads),
            total_vertical_load_n=sum(load.value_n for load in study.loads if load.dof == 3),
            max_displacement_mm=0.0,
            deflection_limit_mm=study.deflection_limit_mm,
            max_von_mises_mpa=0.0,
            safety_factor_to_yield=0.0,
            solver_ok=False,
            issue="CalculiX ccx executable not found in FreeCAD runtime",
        )
    proc = subprocess.run(
        [ccx, _ccx_deck_stem(study)],
        cwd=out_dir,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    (out_dir / f"{study.slug}.ccx.log").write_text(proc.stdout, encoding="utf-8")
    _strip_trailing_whitespace(out_dir / f"{study.slug}.frd")
    fields = _parse_dat_fields(out_dir / f"{study.slug}.dat")
    max_disp, max_vm = _result_maxima(fields)
    safety_factor = S355_YIELD_MPA / max_vm if max_vm > 0.0 else float("inf")
    issue = None
    if proc.returncode != 0:
        issue = f"CalculiX exited with code {proc.returncode}"
    elif max_disp > study.deflection_limit_mm:
        issue = f"screening deflection exceeds {study.deflection_limit_mm:.1f} mm target"
    elif max_vm > ALLOWABLE_SERVICE_MPA:
        issue = f"screening stress exceeds 0.6 x S355 yield ({ALLOWABLE_SERVICE_MPA:.0f} MPa)"
    result_png: str | None = None
    docs_result_png: str | None = None
    result = StudyResult(
        slug=study.slug,
        title=study.title,
        nodes=len(study.nodes),
        elements=len(study.elements),
        total_applied_load_n=_total_applied_load(study.loads),
        total_vertical_load_n=sum(load.value_n for load in study.loads if load.dof == 3),
        max_displacement_mm=max_disp,
        deflection_limit_mm=study.deflection_limit_mm,
        max_von_mises_mpa=max_vm,
        safety_factor_to_yield=safety_factor,
        solver_ok=proc.returncode == 0,
        result_png=None,
        docs_result_png=None,
        issue=issue,
    )
    if proc.returncode == 0 and fields.displacements:
        local_png = out_dir / f"{study.slug}-result.png"
        _write_result_png(study=study, result=result, fields=fields, path=local_png)
        result_png = _display_path(local_png)
        if png_out_dir is not None:
            png_out_dir.mkdir(parents=True, exist_ok=True)
            docs_png = png_out_dir / f"freecad-fea-{study.slug}-result.png"
            shutil.copyfile(local_png, docs_png)
            docs_result_png = _display_path(docs_png)
        result = StudyResult(
            slug=result.slug,
            title=result.title,
            nodes=result.nodes,
            elements=result.elements,
            total_applied_load_n=result.total_applied_load_n,
            total_vertical_load_n=result.total_vertical_load_n,
            max_displacement_mm=result.max_displacement_mm,
            deflection_limit_mm=result.deflection_limit_mm,
            max_von_mises_mpa=result.max_von_mises_mpa,
            safety_factor_to_yield=result.safety_factor_to_yield,
            solver_ok=result.solver_ok,
            result_png=result_png,
            docs_result_png=docs_result_png,
            issue=result.issue,
        )
    return result


def _dependency_report() -> dict[str, object]:
    report: dict[str, object] = {
        "freecad_importable": App is not None,
        "freecad_version": App.Version() if App is not None else None,
        "modules": {},
        "executables": {},
    }
    modules: dict[str, bool] = {}
    for module in ("Fem", "femtools", "femmesh", "Assembly"):
        try:
            importlib.import_module(module)
        except Exception:
            modules[module] = False
        else:
            modules[module] = True
    report["modules"] = modules
    executables: dict[str, dict[str, object]] = {}
    for exe in ("ccx", "gmsh"):
        path = shutil.which(exe)
        version = None
        if path:
            proc = subprocess.run(
                [path, "-v" if exe == "ccx" else "--version"],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
            )
            version = proc.stdout.strip().splitlines()[:3]
        executables[exe] = {"path": path, "version": version}
    report["executables"] = executables
    return report


def _axis_box_shape(n1: Node, n2: Node, section: BeamSection):
    x1, y1, z1 = n1.x, n1.y, n1.z
    x2, y2, z2 = n2.x, n2.y, n2.z
    dx, dy, dz = abs(x2 - x1), abs(y2 - y1), abs(z2 - z1)
    w = section.width_mm
    h = section.height_mm
    if dx >= dy and dx >= dz:
        return Part.makeBox(dx, w, h, App.Vector(min(x1, x2), y1 - w / 2.0, z1 - h / 2.0))
    if dy >= dx and dy >= dz:
        return Part.makeBox(w, dy, h, App.Vector(x1 - w / 2.0, min(y1, y2), z1 - h / 2.0))
    return Part.makeBox(w, h, dz, App.Vector(x1 - w / 2.0, y1 - h / 2.0, min(z1, z2)))


def _add_visual_study(
    doc,
    study: Study,
    offset: tuple[float, float],
    result: StudyResult | None = None,
) -> None:
    group = doc.addObject("App::DocumentObjectGroup", _safe_name(study.slug))
    group.Label = study.title
    offset_x, offset_y = offset
    node_map = {
        node.id: Node(node.id, node.x + offset_x, node.y + offset_y, node.z)
        for node in study.nodes
    }
    for element in study.elements:
        n1 = node_map[element.n1]
        n2 = node_map[element.n2]
        section = study.sections[element.section]
        obj = doc.addObject("Part::Feature", f"{_safe_name(study.slug)}_E{element.id}")
        obj.Label = f"{study.slug} {element.section} element {element.id}"
        obj.Shape = _axis_box_shape(n1, n2, section)
        view_object = getattr(obj, "ViewObject", None)
        if view_object is not None:
            view_object.ShapeColor = (0.50, 0.52, 0.55, 0.0)
        group.addObject(obj)
    for load in study.loads:
        node = node_map[load.node]
        obj = doc.addObject("Part::Feature", f"{_safe_name(study.slug)}_load_{load.node}")
        obj.Label = f"{study.slug} load {load.label}"
        obj.Shape = Part.makeBox(90.0, 90.0, 260.0, App.Vector(node.x - 45.0, node.y - 45.0, node.z + 120.0))
        view_object = getattr(obj, "ViewObject", None)
        if view_object is not None:
            view_object.ShapeColor = (0.85, 0.18, 0.10, 0.0)
        group.addObject(obj)
    for bc in study.boundaries:
        node = node_map[bc.node]
        obj = doc.addObject("Part::Feature", f"{_safe_name(study.slug)}_support_{bc.node}")
        obj.Label = f"{study.slug} support node {bc.node}"
        obj.Shape = Part.makeBox(180.0, 180.0, 80.0, App.Vector(node.x - 90.0, node.y - 90.0, node.z - 140.0))
        view_object = getattr(obj, "ViewObject", None)
        if view_object is not None:
            view_object.ShapeColor = (0.10, 0.38, 0.18, 0.0)
        group.addObject(obj)
    if result is not None:
        note = doc.addObject("App::DocumentObjectGroup", f"{_safe_name(study.slug)}_result_note")
        note.Label = (
            f"Result: max displacement {result.max_displacement_mm:.3f} mm, "
            f"max von Mises {result.max_von_mises_mpa:.1f} MPa"
        )
        group.addObject(note)


def _write_freecad_visual_doc(studies: list[Study], results: list[StudyResult], path: Path) -> None:
    _require_freecad()
    doc = App.newDocument("OSR_FEA_screening_models")
    doc.Label = "OSR FEA screening beam models"
    result_by_slug = {result.slug: result for result in results}
    columns = 3
    rows = math.ceil(len(studies) / columns)
    for index, study in enumerate(studies):
        row, column = divmod(index, columns)
        offset = (
            (column - (columns - 1) / 2.0) * 24_000.0,
            (row - (rows - 1) / 2.0) * 6_400.0,
        )
        _add_visual_study(doc, study, offset, result_by_slug.get(study.slug))
    doc.recompute()
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        path.unlink()
    doc.saveAs(str(path))
    print(f"wrote {path}")
    App.closeDocument(doc.Name)


def _write_summary(
    *,
    out_dir: Path,
    dependency_report: dict[str, object],
    studies: list[Study],
    results: list[StudyResult],
) -> None:
    summary_json = out_dir / "screening-summary.json"
    summary_json.write_text(
        json.dumps(
            {
                "dependencies": dependency_report,
                "allowable_service_mpa": ALLOWABLE_SERVICE_MPA,
                "results": [result.__dict__ for result in results],
            },
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    lines = [
        "# Rolling-Stock FEA Screening Summary",
        "",
        "This is a first-pass FreeCAD/CalculiX beam-model screen for gross",
        "load paths. It is not a homologation, fatigue, crashworthiness, weld,",
        "shell-buckling, or supplier-final mesh.",
        "",
        "## FEA Stack",
        "",
        f"- FreeCAD importable: {dependency_report['freecad_importable']}",
        f"- FreeCAD version: {dependency_report['freecad_version']}",
        f"- Modules: {dependency_report['modules']}",
        f"- Executables: {dependency_report['executables']}",
        "",
        "## Results",
        "",
        "| Study | Load case | Nodes | Elements | Applied load kN | Vertical load kN | Max displacement mm | Target mm | Max von Mises MPa | SF to S355 yield | Result PNG | Status |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|",
    ]
    study_by_slug = {study.slug: study for study in studies}
    for result in results:
        study = study_by_slug[result.slug]
        status = "OK" if result.solver_ok and result.issue is None else f"Review: {result.issue}"
        sf = "inf" if math.isinf(result.safety_factor_to_yield) else f"{result.safety_factor_to_yield:.2f}"
        png = f"[PNG]({_markdown_link_path(result.result_png, out_dir)})" if result.result_png else "-"
        lines.append(
            f"| {result.title} | {study.load_case} | {result.nodes} | {result.elements} | "
            f"{result.total_applied_load_n / 1000.0:.1f} | "
            f"{abs(result.total_vertical_load_n) / 1000.0:.1f} | "
            f"{result.max_displacement_mm:.3f} | "
            f"{result.deflection_limit_mm:.1f} | "
            f"{result.max_von_mises_mpa:.1f} | {sf} | {png} | {status} |"
        )
    lines.extend(["", "## Study Notes", ""])
    for study in studies:
        lines.append(f"### {study.title}")
        lines.append("")
        lines.extend(f"- {note}" for note in study.notes)
        lines.append("")
    lines.extend(
        [
            "## Geometry/Model Caveats",
            "",
            "- Beam sections are conservative rectangular approximations of the CAD envelopes.",
            "- Composite body panels, glazing, adhesive lands, local brackets, bolt holes, weld toes, and notches are not meshed.",
            "- Loads are static screening loads only; no crash, fatigue spectrum, modal, thermal, or derailment cases are included.",
            "- Any stress above the 0.6 x S355 yield service screen should trigger a detailed shell/solid mesh and local joint design.",
            "",
        ]
    )
    (out_dir / "screening-summary.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {summary_json}")
    print(f"wrote {out_dir / 'screening-summary.md'}")


def _refresh_latest_outputs(
    *,
    out_dir: Path,
    freecad_out: Path,
    studies: list[Study],
    png_out_dir: Path | None = None,
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    for file_name in ("dependency-check.json", "screening-summary.json", "screening-summary.md"):
        path = out_dir / file_name
        if path.exists():
            path.unlink()
            print(f"removed old FEA summary artifact {path}")
    for study in studies:
        study_dir = out_dir / study.slug
        if study_dir.exists():
            shutil.rmtree(study_dir)
            print(f"removed old FEA solver output {study_dir}")
    if freecad_out.exists():
        freecad_out.unlink()
        print(f"removed old FEA FreeCAD visual document {freecad_out}")
    if png_out_dir is not None and png_out_dir.exists():
        for path in png_out_dir.glob("freecad-fea-*-result.png"):
            path.unlink()
            print(f"removed old FEA result PNG {path}")


def run_fea(*, out_dir: Path, freecad_out: Path, png_out_dir: Path | None) -> None:
    _require_freecad()
    studies = all_studies()
    _refresh_latest_outputs(
        out_dir=out_dir,
        freecad_out=freecad_out,
        studies=studies,
        png_out_dir=png_out_dir,
    )
    dependency_report = _dependency_report()
    (out_dir / "dependency-check.json").write_text(
        json.dumps(dependency_report, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    print(f"wrote {out_dir / 'dependency-check.json'}")
    results = [_run_ccx(study, out_dir / study.slug, png_out_dir) for study in studies]
    _write_summary(out_dir=out_dir, dependency_report=dependency_report, studies=studies, results=results)
    _write_freecad_visual_doc(studies, results, freecad_out)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run FreeCAD/CalculiX rolling-stock FEA screening models.")
    parser.add_argument("--out-dir", type=Path, default=_catalog_root() / "fea")
    parser.add_argument("--freecad-out", type=Path, default=_catalog_root() / "freecad" / "fea-screening-models.FCStd")
    parser.add_argument(
        "--png-out-dir",
        type=Path,
        default=_repo_root() / "docs" / "screenshots" / "freecad",
        help="directory for stable docs copies of solver-derived result PNGs",
    )
    parser.add_argument(
        "--no-doc-pngs",
        action="store_true",
        help="only write result PNGs inside each solver-output folder",
    )
    return parser.parse_args(argv)


def _normalise_freecad_argv(argv: list[str]) -> list[str]:
    args = list(argv)
    if args and Path(args[0]).name == "freecad_fea.py":
        args = args[1:]
    if args and args[0] == "--pass":
        args = args[1:]
    return args


def main(argv: list[str] | None = None) -> None:
    args = parse_args(_normalise_freecad_argv(argv or []))
    run_fea(
        out_dir=args.out_dir,
        freecad_out=args.freecad_out,
        png_out_dir=None if args.no_doc_pngs else args.png_out_dir,
    )


def _running_as_freecad_script() -> bool:
    return bool(sys.argv[1:2]) and Path(sys.argv[1]).name == "freecad_fea.py"


if __name__ == "__main__" or _running_as_freecad_script():
    main(sys.argv[1:])
