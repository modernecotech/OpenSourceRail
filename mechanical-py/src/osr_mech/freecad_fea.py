"""FreeCAD/CalculiX screening FEA for rolling-stock structures.

This is a first-pass engineering screen, not a certification model. It
uses axis-aligned B31 beam/space-frame idealisations to check gross load
paths for:

- the low-floor chassis supported at bogie interfaces,
- the bogie H-frame supported at axlebox/primary-suspension points,
- the full car body frame supported at bogie locations.

The script runs inside FreeCADCmd so the FEM workbench and bundled
CalculiX/Gmsh tools from the FreeCAD runtime are discoverable.
"""

from __future__ import annotations

import argparse
import importlib
import json
import math
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


E_STEEL_MPA = 210_000.0
NU_STEEL = 0.30
S355_YIELD_MPA = 355.0
ALLOWABLE_SERVICE_MPA = 0.60 * S355_YIELD_MPA


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
    notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class StudyResult:
    slug: str
    title: str
    nodes: int
    elements: int
    total_vertical_load_n: float
    max_displacement_mm: float
    deflection_limit_mm: float
    max_von_mises_mpa: float
    safety_factor_to_yield: float
    solver_ok: bool
    issue: str | None = None


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
    xs = [-8_500.0, -7_600.0, -6_400.0, -4_200.0, -2_000.0, 0.0, 2_000.0, 4_200.0, 6_400.0, 7_600.0, 8_500.0]
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
    for x in (-6_400.0, 6_400.0):
        for y in (-1_250.0, -700.0, 700.0, 1_250.0):
            b.beam((x - 520.0, y, z + 160.0), (x + 520.0, y, z + 160.0), "BOLSTER")
        b.beam((x, -1_250.0, z + 160.0), (x, 1_250.0, z + 160.0), "BOLSTER")
        for y in (-700.0, 700.0):
            b.beam((x - math.copysign(1_480.0, x), y, z - 20.0), (x, y, z + 160.0), "BOLSTER")
    supports = [
        b.node_id((-6_400.0, -700.0, z)),
        b.node_id((-6_400.0, 700.0, z)),
        b.node_id((6_400.0, -700.0, z)),
        b.node_id((6_400.0, 700.0, z)),
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
        notes=[
            "Bogie support points represent four secondary-air-spring/chassis interface pads.",
            "Reworked chassis uses deep side torsion boxes, twin keel beams, upper battery-zone chords, and stiffer cross-bearers.",
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
        notes=[
            "Axlebox/primary-suspension support nodes constrain vertical displacement.",
            "Motor reaction brackets are not included in this load case; use the motor connector CAD for interface review.",
        ],
    )


def full_body_frame_study() -> Study:
    b = ModelBuilder()
    sections = {
        "SIDE_SILL": BeamSection("SIDE_SILL", 170.0, 300.0),
        "WAIST_RAIL": BeamSection("WAIST_RAIL", 120.0, 105.0),
        "CANT_RAIL": BeamSection("CANT_RAIL", 135.0, 170.0),
        "ROOF_RAIL": BeamSection("ROOF_RAIL", 115.0, 115.0),
        "POST": BeamSection("POST", 120.0, 120.0, orientation=(1.0, 0.0, 0.0)),
        "CROSS_TIE": BeamSection("CROSS_TIE", 95.0, 135.0),
    }
    xs = [-8_500.0, -6_400.0, -4_200.0, -2_100.0, 0.0, 2_100.0, 4_200.0, 6_400.0, 8_500.0]
    ys = [-1_350.0, 1_350.0]
    levels = [350.0, 1_500.0, 2_800.0, 3_450.0]
    for y in ys:
        for z, section in ((350.0, "SIDE_SILL"), (1_500.0, "WAIST_RAIL"), (2_800.0, "CANT_RAIL"), (3_450.0, "ROOF_RAIL")):
            for a, c in zip(xs, xs[1:]):
                b.beam((a, y, z), (c, y, z), section)
        for x in xs:
            for a, c in zip(levels, levels[1:]):
                b.beam((x, y, a), (x, y, c), "POST")
    for x in xs:
        for z in (350.0, 3_450.0):
            b.beam((x, -1_350.0, z), (x, 1_350.0, z), "CROSS_TIE")
    supports = [
        b.node_id((-6_400.0, -1_350.0, 350.0)),
        b.node_id((-6_400.0, 1_350.0, 350.0)),
        b.node_id((6_400.0, -1_350.0, 350.0)),
        b.node_id((6_400.0, 1_350.0, 350.0)),
    ]
    floor_nodes = [b.node_id((x, y, 350.0)) for x in xs[1:-1] for y in ys]
    body_payload_load_n = -420_000.0
    loads = [
        Load(node, 3, body_payload_load_n / len(floor_nodes), "distributed body/interior/passenger gravity")
        for node in floor_nodes
    ]
    roof_load_nodes = [b.node_id((x, y, 3_450.0)) for x in (-6_400.0, 6_400.0) for y in ys]
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
        load_case="420 kN distributed body/payload gravity plus 30 kN roof equipment allowance",
        nodes=b.nodes,
        elements=b.elements,
        sections=sections,
        boundaries=boundaries,
        loads=loads,
        deflection_limit_mm=15.0,
        notes=[
            "Side posts, side sills, waist rails, cant rails, and roof bows are idealised as S355 beams.",
            "Composite panels and glazing are treated as non-structural for this screening pass.",
        ],
    )


def all_studies() -> list[Study]:
    return [chassis_bogie_study(), bogie_frame_study(), full_body_frame_study()]


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


def _parse_dat(path: Path) -> tuple[float, float]:
    max_disp = 0.0
    max_vm = 0.0
    mode: str | None = None
    if not path.exists():
        return max_disp, max_vm
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
                float(parts[0])
                ux, uy, uz = (float(v) for v in parts[1:4])
                max_disp = max(max_disp, math.sqrt(ux * ux + uy * uy + uz * uz))
            elif mode == "s" and len(parts) == 8:
                float(parts[0])
                stresses = tuple(float(v) for v in parts[2:8])
                max_vm = max(max_vm, _von_mises(stresses))  # type: ignore[arg-type]
        except ValueError:
            continue
    return max_disp, max_vm


def _run_ccx(study: Study, out_dir: Path) -> StudyResult:
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
            total_vertical_load_n=sum(load.value_n for load in study.loads if load.dof == 3),
            max_displacement_mm=0.0,
            deflection_limit_mm=study.deflection_limit_mm,
            max_von_mises_mpa=0.0,
            safety_factor_to_yield=0.0,
            solver_ok=False,
            issue="CalculiX ccx executable not found in FreeCAD runtime",
        )
    base = out_dir / study.slug
    proc = subprocess.run(
        [ccx, str(base)],
        cwd=out_dir,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    (out_dir / f"{study.slug}.ccx.log").write_text(proc.stdout, encoding="utf-8")
    max_disp, max_vm = _parse_dat(out_dir / f"{study.slug}.dat")
    safety_factor = S355_YIELD_MPA / max_vm if max_vm > 0.0 else float("inf")
    issue = None
    if proc.returncode != 0:
        issue = f"CalculiX exited with code {proc.returncode}"
    elif max_disp > study.deflection_limit_mm:
        issue = f"screening deflection exceeds {study.deflection_limit_mm:.1f} mm target"
    elif max_vm > ALLOWABLE_SERVICE_MPA:
        issue = f"screening stress exceeds 0.6 x S355 yield ({ALLOWABLE_SERVICE_MPA:.0f} MPa)"
    return StudyResult(
        slug=study.slug,
        title=study.title,
        nodes=len(study.nodes),
        elements=len(study.elements),
        total_vertical_load_n=sum(load.value_n for load in study.loads if load.dof == 3),
        max_displacement_mm=max_disp,
        deflection_limit_mm=study.deflection_limit_mm,
        max_von_mises_mpa=max_vm,
        safety_factor_to_yield=safety_factor,
        solver_ok=proc.returncode == 0,
        issue=issue,
    )


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


def _add_visual_study(doc, study: Study, offset_y: float, result: StudyResult | None = None) -> None:
    group = doc.addObject("App::DocumentObjectGroup", _safe_name(study.slug))
    group.Label = study.title
    node_map = {node.id: Node(node.id, node.x, node.y + offset_y, node.z) for node in study.nodes}
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
    for offset_y, study in zip((-5_800.0, 0.0, 5_800.0), studies):
        _add_visual_study(doc, study, offset_y, result_by_slug.get(study.slug))
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
        "| Study | Load case | Nodes | Elements | Vertical load kN | Max displacement mm | Target mm | Max von Mises MPa | SF to S355 yield | Status |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    study_by_slug = {study.slug: study for study in studies}
    for result in results:
        study = study_by_slug[result.slug]
        status = "OK" if result.solver_ok and result.issue is None else f"Review: {result.issue}"
        sf = "inf" if math.isinf(result.safety_factor_to_yield) else f"{result.safety_factor_to_yield:.2f}"
        lines.append(
            f"| {result.title} | {study.load_case} | {result.nodes} | {result.elements} | "
            f"{abs(result.total_vertical_load_n) / 1000.0:.1f} | {result.max_displacement_mm:.3f} | "
            f"{result.deflection_limit_mm:.1f} | "
            f"{result.max_von_mises_mpa:.1f} | {sf} | {status} |"
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
            "- Loads are static gravity/service loads only; no crash, fatigue spectrum, modal, thermal, or derailment cases are included.",
            "- Any stress above the 0.6 x S355 yield service screen should trigger a detailed shell/solid mesh and local joint design.",
            "",
        ]
    )
    (out_dir / "screening-summary.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {summary_json}")
    print(f"wrote {out_dir / 'screening-summary.md'}")


def _refresh_latest_outputs(*, out_dir: Path, freecad_out: Path, studies: list[Study]) -> None:
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


def run_fea(*, out_dir: Path, freecad_out: Path) -> None:
    _require_freecad()
    studies = all_studies()
    _refresh_latest_outputs(out_dir=out_dir, freecad_out=freecad_out, studies=studies)
    dependency_report = _dependency_report()
    (out_dir / "dependency-check.json").write_text(
        json.dumps(dependency_report, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    print(f"wrote {out_dir / 'dependency-check.json'}")
    results = [_run_ccx(study, out_dir / study.slug) for study in studies]
    _write_summary(out_dir=out_dir, dependency_report=dependency_report, studies=studies, results=results)
    _write_freecad_visual_doc(studies, results, freecad_out)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run FreeCAD/CalculiX rolling-stock FEA screening models.")
    parser.add_argument("--out-dir", type=Path, default=_catalog_root() / "fea")
    parser.add_argument("--freecad-out", type=Path, default=_catalog_root() / "freecad" / "fea-screening-models.FCStd")
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
    run_fea(out_dir=args.out_dir, freecad_out=args.freecad_out)


def _running_as_freecad_script() -> bool:
    return bool(sys.argv[1:2]) and Path(sys.argv[1]).name == "freecad_fea.py"


if __name__ == "__main__" or _running_as_freecad_script():
    main(sys.argv[1:])
