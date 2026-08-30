"""Create FreeCAD assembled/exploded review states and shape checks.

The review documents are generated directly from parametric source
geometry, then saved as compact FreeCAD documents. Assembled and
disassembled states are placement views for design review.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
import uuid
import zipfile
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from osr_mech.freecad_occ_bridge import SourceGeometry, freecad_shape_from_source, safe_name
from osr_mech.trainset_manufacturing_methods import load_and_validate


try:
    import FreeCAD as App  # type: ignore[import-not-found]
    import Part  # type: ignore[import-not-found]
except Exception as exc:  # pragma: no cover - exercised only outside FreeCAD.
    App = None  # type: ignore[assignment]
    Part = None  # type: ignore[assignment]
    _FREECAD_IMPORT_ERROR = exc
else:
    _FREECAD_IMPORT_ERROR = None


from osr_mech.rolling_stock.baseline import PROMOTED_LIGHT_METRO_CAR_LENGTH_MM

CAR_LENGTH_MM = PROMOTED_LIGHT_METRO_CAR_LENGTH_MM
BOGIE_X_MM = CAR_LENGTH_MM / 2.0 - 2_100.0
# The bogie source envelope tops out at 1,072.5 mm and the chassis
# interface datum is 740 mm.  This seats the bogie below the chassis
# instead of leaving it at the source origin above the floor structure.
BOGIE_SEAT_Z_MM = 740.0 - 1_072.5

COLOURS = {
    "structure": (0.52, 0.54, 0.56, 0.0),
    "body": (0.88, 0.91, 0.92, 0.0),
    "systems": (0.18, 0.39, 0.68, 0.0),
    "interface": (0.95, 0.68, 0.18, 0.0),
    "bogie": (0.12, 0.12, 0.12, 0.0),
}
FCSTD_NAMESPACE = uuid.UUID("f42effa5-2414-5f3f-a53c-1198e907e5e2")


@dataclass(frozen=True)
class ReviewItem:
    source: SourceGeometry
    name: str
    x_mm: float = 0.0
    y_mm: float = 0.0
    z_mm: float = 0.0
    yaw_deg: float = 0.0
    colour: tuple[float, float, float, float] | None = None
    metadata: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class ShapeCheck:
    name: str
    source_key: str
    valid: bool
    check_ok: bool
    solids_valid: bool
    solids: int
    volume_mm3: float
    bbox_mm: tuple[float, float, float]
    issue: str | None = None


def _source(key: str) -> SourceGeometry:
    return SourceGeometry(key=key)


def _interface_source(key: str) -> SourceGeometry:
    return _source(key)


def _summarise_occ_issue(exc: Exception) -> str:
    text = str(exc)
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    counter: Counter[str] = Counter()
    for line in lines:
        if "BOPAlgo" in line:
            counter[line] += 1
    if counter:
        common = ", ".join(f"{count}x {label}" for label, count in counter.most_common(4))
        return f"OCC compound check reported overlaps/self-intersections: {common}"
    return lines[0] if lines else repr(exc)


def _require_freecad() -> None:
    if App is None or Part is None:
        raise SystemExit(
            "FreeCAD Python modules are not importable. Run this with FreeCADCmd "
            "or design/component-catalogue/scripts/freecad_assembly_review.sh.\n"
            f"Import error was: {_FREECAD_IMPORT_ERROR!r}"
        )


def _artifact_root() -> Path:
    return Path(__file__).resolve().parents[2] / "models" / "cad"


def _canonicalise_fcstd(path: Path) -> None:
    """Remove FreeCAD save-time/UUID/ZIP metadata from a tracked review file."""

    with zipfile.ZipFile(path, "r") as source:
        entries = [(info, source.read(info.filename)) for info in source.infolist()]
        comment = source.comment
    canonical_entries: list[tuple[zipfile.ZipInfo, bytes]] = []
    document_uid = str(uuid.uuid5(FCSTD_NAMESPACE, path.name))
    for info, data in entries:
        if info.filename == "Document.xml":
            text = data.decode("utf-8")
            text = re.sub(
                r'(<Property name="(?:CreationDate|LastModifiedDate)"[^>]*>\s*<String value=")[^"]+',
                r"\g<1>2000-01-01T00:00:00Z",
                text,
            )
            text = re.sub(
                r'(<Property name="Uid"[^>]*>\s*<Uuid value=")[^"]+',
                rf"\g<1>{document_uid}",
                text,
            )
            object_id = 0

            def canonical_object_id(match: re.Match[str]) -> str:
                nonlocal object_id
                object_id += 1
                return f'{match.group(1)}{object_id}{match.group(2)}'

            text = re.sub(
                r'(<Object type="[^"]+" name="[^"]+" id=")\d+("\s*/>)',
                canonical_object_id,
                text,
            )
            data = text.encode("utf-8")
        canonical = zipfile.ZipInfo(info.filename, date_time=(2000, 1, 1, 0, 0, 0))
        canonical.compress_type = info.compress_type
        canonical.external_attr = info.external_attr
        canonical.internal_attr = info.internal_attr
        canonical.create_system = info.create_system
        canonical_entries.append((canonical, data))
    with tempfile.NamedTemporaryFile(
        "wb", dir=path.parent, prefix=f".{path.name}.", delete=False
    ) as handle:
        temporary = Path(handle.name)
    try:
        with zipfile.ZipFile(temporary, "w") as target:
            target.comment = comment
            for info, data in canonical_entries:
                target.writestr(info, data)
        temporary.replace(path)
    finally:
        if temporary.exists():
            temporary.unlink()


def _add_shape(
    doc,
    item: ReviewItem,
    group,
    shape_cache: dict[str, object],
    temp_dir: Path,
):
    shape = freecad_shape_from_source(
        item.source,
        part_module=Part,
        cache=shape_cache,
        temp_dir=temp_dir,
    )
    obj = doc.addObject("Part::Feature", safe_name(item.name))
    obj.Label = item.name
    obj.Shape = shape
    obj.Placement = App.Placement(
        App.Vector(item.x_mm, item.y_mm, item.z_mm),
        App.Rotation(App.Vector(0, 0, 1), item.yaw_deg),
    )
    view_object = getattr(obj, "ViewObject", None)
    if item.colour is not None and view_object is not None:
        view_object.ShapeColor = item.colour
    for key, value in item.metadata:
        property_name = safe_name(key)
        obj.addProperty("App::PropertyString", property_name, "OSR Manufacturing")
        setattr(obj, property_name, value)
    group.addObject(obj)
    return obj


def _state_group(doc, parent, item: ReviewItem, groups: dict[str, object]):
    """Keep floor architecture and running gear separate in the tree."""
    key = item.source.key
    if key in {"motor-bogie", "trailer-bogie"} or "bogie" in item.name.lower():
        label = "Running Gear / Bogies"
    elif key in {"low-floor-chassis", "bogie-to-chassis-connector"} or "chassis" in item.name.lower():
        label = "Floor Architecture / Chassis"
    elif key in {"window-installations", "door-window-cassette-hardware", "composite-body-roof-attachments"}:
        label = "Glazing and Exterior"
    elif key in {"door-design", "door-mounts", "door-installations", "door-to-body-installations"}:
        label = "Doors and Access"
    elif key in {"cabin-flooring", "bench-on-battery-installations", "universal-service-rail-installation", "standard-fixture-adapters"}:
        label = "Passenger Interior"
    elif key in {"hvac-roof-ducting-installation", "internal-lighting-installation", "modular-lighting-cassettes"}:
        label = "HVAC and Lighting"
    elif key in {"screen-speaker-mountings", "external-lighting-lidar-system"}:
        label = "Controls and Fixtures"
    else:
        label = "Body and Systems"
    group = groups.get(label)
    if group is None:
        group = doc.addObject("App::DocumentObjectGroup", safe_name(label))
        group.Label = label
        parent.addObject(group)
        groups[label] = group
    return group


def _check_shape(
    item: ReviewItem,
    shape_cache: dict[str, object],
    temp_dir: Path,
) -> ShapeCheck:
    try:
        shape = freecad_shape_from_source(
            item.source,
            part_module=Part,
            cache=shape_cache,
            temp_dir=temp_dir,
        )
        # Review assemblies intentionally contain separate contacting parts.
        # Checking the compound as one BOP body falsely reports those contacts
        # as self-intersections. Validate each manufacturable solid instead.
        check_ok = True
        issue = None
        for solid in shape.Solids:
            try:
                solid.check(True)
            except Exception as exc:  # FreeCAD returns detailed OCC text here.
                check_ok = False
                issue = _summarise_occ_issue(exc)
                break
        bbox = shape.BoundBox
        size = (bbox.XLength, bbox.YLength, bbox.ZLength)
        valid = bool(shape.isValid())
        solids_valid = all(solid.isValid() for solid in shape.Solids)
        if bbox.XLength <= 0.0 or bbox.YLength <= 0.0 or bbox.ZLength <= 0.0:
            valid = False
            issue = issue or "zero-size bounding box axis"
        return ShapeCheck(
            name=item.name,
            source_key=item.source.key,
            valid=valid,
            check_ok=check_ok,
            solids_valid=solids_valid,
            solids=len(shape.Solids),
            volume_mm3=float(shape.Volume),
            bbox_mm=size,
            issue=issue,
        )
    except Exception as exc:
        return ShapeCheck(
            name=item.name,
            source_key=item.source.key,
            valid=False,
            check_ok=False,
            solids_valid=False,
            solids=0,
            volume_mm3=0.0,
            bbox_mm=(0.0, 0.0, 0.0),
            issue=str(exc),
        )


def _chassis_bogie_items(*, exploded: bool) -> list[ReviewItem]:
    if not exploded:
        return [
            ReviewItem(
                _interface_source("low-floor-chassis"),
                "Low-floor centre chassis",
                colour=COLOURS["structure"],
                metadata=(("AssemblyId", "LM3-BDY-SA110"), ("ProductIds", "LM3-BDY-P010 | LM3-BDY-P020 | LM3-BDY-P030 | LM3-BDY-P120"), ("AssemblyChain", "parts > LM3-BDY-SA110 > LM3-BDY-SA120 > LM3-SHELL-A200 > LM3-CAR-A900 > LM3-TRAINSET-A000")),
            ),
            ReviewItem(
                _interface_source("bogie-to-chassis-connector"),
                "Bogie-to-chassis connector package",
                colour=COLOURS["interface"],
                metadata=(("ProductIds", "LM3-BOG-P046 | LM3-BOG-P047"), ("SupplierAnchors", "OSR-ANC-SUSPENSION-CONTI"), ("InterfaceControl", "air spring | emergency spring | centre pivot | yaw link | damper | anti-lift")),
            ),
            ReviewItem(
                _source("motor-bogie"),
                "A-end motor bogie",
                x_mm=-BOGIE_X_MM,
                z_mm=BOGIE_SEAT_Z_MM,
                colour=COLOURS["bogie"],
                metadata=(("AssemblyId", "LM3-BOG-SA610"), ("ChildAssemblies", "LM3-BOG-SA611 | LM3-TRC-SA615"), ("AssemblyChain", "running unit + bogie-mounted drive + body connection > powered bogie > car > trainset")),
            ),
            ReviewItem(
                _source("trailer-bogie"),
                "B-end trailer bogie",
                x_mm=BOGIE_X_MM,
                z_mm=BOGIE_SEAT_Z_MM,
                colour=COLOURS["bogie"],
                metadata=(("AssemblyId", "LM3-BOG-SA620"), ("ChildAssemblies", "LM3-BOG-SA621"), ("AssemblyChain", "running unit + body connection > trailer bogie > car > trainset")),
            ),
            ReviewItem(
                _interface_source("bogie-to-motor-connector"),
                "A-end bogie-to-motor connector",
                x_mm=-BOGIE_X_MM,
                colour=COLOURS["interface"],
                metadata=(("AssemblyId", "LM3-TRC-SA615"), ("ProductIds", "LM3-TRC-P010 | LM3-TRC-P020 | LM3-BOG-P050"), ("SupplierAnchors", "OSR-ANC-MOTOR-ABB-AMXM | OSR-ANC-GEAR-VOITH-SE")),
            ),
        ]
    return [
        ReviewItem(
            _interface_source("low-floor-chassis"),
            "Exploded low-floor centre chassis",
            z_mm=1_650.0,
            colour=COLOURS["structure"],
            metadata=(("AssemblyId", "LM3-BDY-SA110"), ("AssemblyChain", "chassis parts > underframe > body frame > shell > car > trainset")),
        ),
        ReviewItem(
            _interface_source("bogie-to-chassis-connector"),
            "Exploded bogie-to-chassis connector package",
            z_mm=850.0,
            colour=COLOURS["interface"],
            metadata=(("ProductIds", "LM3-BOG-P046 | LM3-BOG-P047"), ("SupplierAnchors", "OSR-ANC-SUSPENSION-CONTI")),
        ),
        ReviewItem(
            _source("motor-bogie"),
            "Exploded A-end motor bogie",
            x_mm=-BOGIE_X_MM,
            y_mm=-2_100.0,
            z_mm=BOGIE_SEAT_Z_MM - 650.0,
            colour=COLOURS["bogie"],
            metadata=(("AssemblyId", "LM3-BOG-SA610"), ("ChildAssemblies", "LM3-BOG-SA611 | LM3-TRC-SA615")),
        ),
        ReviewItem(
            _source("trailer-bogie"),
            "Exploded B-end trailer bogie",
            x_mm=BOGIE_X_MM,
            y_mm=2_100.0,
            z_mm=BOGIE_SEAT_Z_MM - 650.0,
            colour=COLOURS["bogie"],
            metadata=(("AssemblyId", "LM3-BOG-SA620"), ("ChildAssemblies", "LM3-BOG-SA621")),
        ),
        ReviewItem(
            _interface_source("bogie-to-motor-connector"),
            "Exploded A-end bogie-to-motor connector",
            x_mm=-BOGIE_X_MM,
            y_mm=-3_250.0,
            z_mm=180.0,
            colour=COLOURS["interface"],
            metadata=(("AssemblyId", "LM3-TRC-SA615"), ("ProductIds", "LM3-TRC-P010 | LM3-TRC-P020 | LM3-BOG-P050")),
        ),
    ]


def _full_body_items(*, exploded: bool) -> list[ReviewItem]:
    detail_sources = (
        ("window-installations", "Window cassettes and glazing installation"),
        ("door-design", "Door leaf design package"),
        ("door-mounts", "Door portal and mount package"),
        ("door-installations", "Door installation package"),
        ("door-to-body-installations", "Door-to-body seal and interlock package"),
        ("cabin-flooring", "Low-floor centre cabin flooring"),
        ("bench-on-battery-installations", "Passenger bench and battery-strake mounts"),
        ("hvac-roof-ducting-installation", "HVAC roof ducting and supply plenums"),
        ("internal-lighting-installation", "Interior lighting and emergency luminaires"),
        ("universal-service-rail-installation", "Universal ceiling, waist, and fixture rails"),
        ("standard-fixture-adapters", "Standard seat, handrail, and equipment adapters"),
        ("door-window-cassette-hardware", "Simplified door and window cassette hardware"),
        ("screen-speaker-mountings", "Passenger information screens and speakers"),
        ("external-lighting-lidar-system", "External lighting, lidar, radar, and cameras"),
        ("battery-installations", "Battery installation and contactor interfaces"),
        ("side-body-frame-attachments", "Side body frame and fixture attachments"),
        ("composite-body-roof-attachments", "Composite body and roof fixture attachments"),
    )
    if not exploded:
        items = [
            ReviewItem(_source("car-body-structure"), "Body primary structure", colour=COLOURS["structure"], metadata=(("AssemblyIds", "LM3-BDY-SA110 | LM3-BDY-SA120"), ("AssemblyChain", "chassis/body parts > underframe > body frame > shell > car > trainset"))),
            ReviewItem(_source("car-body-exterior"), "Body exterior layer", colour=COLOURS["body"], metadata=(("AssemblyId", "LM3-SHELL-A200"), ("ProductIds", "LM3-BDY-P130 | LM3-BDY-P140"))),
            ReviewItem(_source("car-body-interior"), "Body interior layer", colour=COLOURS["systems"]),
            ReviewItem(_source("car-body-services"), "Body service layers", colour=COLOURS["systems"]),
            ReviewItem(_source("car-systems"), "Car systems package", colour=COLOURS["systems"]),
            ReviewItem(
                _interface_source("mechanical-interface-package"),
                "Mechanical interface package",
                colour=COLOURS["interface"],
                metadata=(("AssemblyIds", "LM3-END-SA700 | LM3-ART-SA800"), ("ArticulationChildren", "LM3-ART-SA810 | LM3-ART-SA820 | LM3-ART-SA830"), ("SupplierRegister", "design/component-catalogue/catalog/buildable-trainset/supplier-anchors.md")),
            ),
        ]
        items.extend(ReviewItem(_interface_source(key), label, colour=COLOURS["systems"]) for key, label in detail_sources)
        return items
    items = [
        ReviewItem(
            _source("car-body-structure"),
            "Exploded body primary structure",
            colour=COLOURS["structure"],
        ),
        ReviewItem(
            _source("car-body-exterior"),
            "Exploded body exterior layer",
            y_mm=-4_200.0,
            colour=COLOURS["body"],
        ),
        ReviewItem(
            _source("car-body-interior"),
            "Exploded body interior layer",
            y_mm=4_200.0,
            colour=COLOURS["systems"],
        ),
        ReviewItem(
            _source("car-body-services"),
            "Exploded body service layers",
            z_mm=3_350.0,
            colour=COLOURS["systems"],
        ),
        ReviewItem(
            _source("car-systems"),
            "Exploded car systems package",
            z_mm=-1_650.0,
            colour=COLOURS["systems"],
        ),
        ReviewItem(
            _interface_source("mechanical-interface-package"),
            "Exploded mechanical interface package",
            y_mm=0.0,
            z_mm=1_900.0,
            colour=COLOURS["interface"],
        ),
    ]
    items.extend(
        ReviewItem(
            _interface_source(key),
            f"Exploded {label.lower()}",
            y_mm=-5_000.0,
            z_mm=2_000.0,
            colour=COLOURS["systems"],
        )
        for key, label in detail_sources
    )
    return items


def _tooling_items() -> list[tuple[str, ReviewItem]]:
    """Expose every controlled tooling family as a separately selectable object."""

    methods = load_and_validate()
    items: list[tuple[str, ReviewItem]] = []
    index = 0
    for method in methods["method"]:
        steps = json.dumps(
            [
                {
                    "sequence": step["sequence"],
                    "name": step["name"],
                    "planning_minutes": step["planning_minutes"],
                    "hold_point": step["hold_point"],
                    "instruction": step["instruction"],
                }
                for step in method["steps"]
            ],
            separators=(",", ":"),
        )
        for tool_id in method["tooling_ids"]:
            column = index % 3
            row = index // 3
            metadata = (
                ("OSRId", str(tool_id)),
                ("MethodId", str(method["id"])),
                ("DetailStatus", "design-reference-not-released"),
                ("LocalManufacture", "preferred where a qualified domestic toolmaker is available"),
                ("WorkCenter", str(method["work_center"])),
                ("PlanningCycleMinutes", str(method["planning_cycle_minutes"])),
                ("ProductIds", " | ".join(method["product_ids"])),
                ("JoiningParts", " | ".join(method["joining_parts"])),
                ("ReleaseGate", str(method["release_gate"])),
                ("StepInstructionsJson", steps),
                ("ControlledSource", "lib/templates/trainset-manufacturing-methods.toml"),
            )
            items.append(
                (
                    str(method["id"]),
                    ReviewItem(
                        _source(f"manufacturing-tool:{tool_id}"),
                        f"{tool_id} — {method['title']}",
                        x_mm=column * 24_000.0,
                        y_mm=row * 12_000.0,
                        colour=COLOURS["interface"],
                        metadata=metadata,
                    ),
                )
            )
            index += 1
    return items


def _write_tooling_doc(*, output: Path) -> list[ShapeCheck]:
    _require_freecad()
    title = "OSR LM3 manufacturing moulds, fixtures, gauges and assembly tooling"
    doc = App.newDocument(safe_name(title))
    doc.Label = title
    methods = load_and_validate()
    root = doc.addObject("App::DocumentObjectGroup", "Manufacturing_Methods")
    root.Label = "LM3 Manufacturing Methods and Tooling"
    groups: dict[str, object] = {}
    checks: list[ShapeCheck] = []
    shape_cache: dict[str, object] = {}
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="osr-freecad-tooling-", dir=output.parent) as tmp:
        temp_dir = Path(tmp)
        for method_id, item in _tooling_items():
            group = groups.get(method_id)
            if group is None:
                method = next(value for value in methods["method"] if value["id"] == method_id)
                group = doc.addObject("App::DocumentObjectGroup", safe_name(method_id))
                group.Label = f"{method_id} — {method['title']}"
                root.addObject(group)
                groups[method_id] = group
            _add_shape(doc, item, group, shape_cache, temp_dir)
            checks.append(_check_shape(item, shape_cache, temp_dir))

    notes = doc.addObject("App::FeaturePython", "ReleaseBoundary")
    notes.Label = "READ FIRST — tooling geometry is design-reference, not fabrication release"
    for name, value in (
        ("Status", methods["status"]),
        ("ReleaseBoundary", methods["release_boundary"]),
        ("MethodRegister", "design/component-catalogue/catalog/buildable-trainset/manufacturing-methods.md"),
        ("ControlledSource", methods["source_file"]),
        ("ControlledSourceSha256", methods["source_sha256"]),
    ):
        notes.addProperty("App::PropertyString", name, "OSR Manufacturing")
        setattr(notes, name, str(value))
    root.addObject(notes)
    doc.recompute()
    if output.exists():
        output.unlink()
    doc.saveAs(str(output))
    App.closeDocument(doc.Name)
    _canonicalise_fcstd(output)
    print(f"wrote {output}")
    return checks


def _write_review_doc(
    *,
    output: Path,
    title: str,
    assembled_items: list[ReviewItem],
    exploded_items: list[ReviewItem],
) -> list[ShapeCheck]:
    _require_freecad()
    doc = App.newDocument(safe_name(title))
    doc.Label = title
    assembled_group = doc.addObject("App::DocumentObjectGroup", "Assembled_State")
    assembled_group.Label = "Assembled State"
    exploded_group = doc.addObject("App::DocumentObjectGroup", "Disassembled_State")
    exploded_group.Label = "Disassembled / Exploded State"

    checks: list[ShapeCheck] = []
    shape_cache: dict[str, object] = {}
    output.parent.mkdir(parents=True, exist_ok=True)
    assembled_subgroups: dict[str, object] = {}
    exploded_subgroups: dict[str, object] = {}
    with tempfile.TemporaryDirectory(prefix="osr-freecad-brep-", dir=output.parent) as tmp:
        temp_dir = Path(tmp)
        for item in assembled_items:
            group = _state_group(doc, assembled_group, item, assembled_subgroups)
            _add_shape(doc, item, group, shape_cache, temp_dir)
            checks.append(_check_shape(item, shape_cache, temp_dir))
        for item in exploded_items:
            group = _state_group(doc, exploded_group, item, exploded_subgroups)
            _add_shape(doc, item, group, shape_cache, temp_dir)

    notes = doc.addObject("App::DocumentObjectGroup", "SourceNotes")
    notes.Label = "Generated directly from parametric source geometry; assembled and exploded states are placement views"
    doc.recompute()
    if output.exists():
        output.unlink()
    doc.saveAs(str(output))
    App.closeDocument(doc.Name)
    _canonicalise_fcstd(output)
    print(f"wrote {output}")
    return checks


def _write_report(path: Path, checks_by_doc: dict[str, list[ShapeCheck]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# FreeCAD Assembly Geometry Review",
        "",
        "Generated directly from parametric source geometry. The checks below use FreeCAD/OCC",
        "`Shape.isValid()`, `Shape.check(True)`, solid counts, volume, and bounding-box",
        "sanity checks on each assembled-state input.",
        "",
    ]
    issues = []
    for doc_name, checks in checks_by_doc.items():
        lines.extend(
            [
                f"## {doc_name}",
                "",
                "| Item | Source | Valid | OCC check | Solids | Volume mm^3 | Bounding box mm | Issue |",
                "|---|---|---:|---:|---:|---:|---|---|",
            ]
        )
        for check in checks:
            bbox = " x ".join(f"{v:.0f}" for v in check.bbox_mm)
            issue = check.issue or ""
            if issue or not check.valid or not check.check_ok:
                issues.append(f"{doc_name}: {check.name}: {issue or 'invalid shape'}")
            lines.append(
                f"| {check.name} | `{check.source_key}` | {check.valid and check.solids_valid} | {check.check_ok} | "
                f"{check.solids} | {check.volume_mm3:.0f} | {bbox} | {issue} |"
            )
        lines.append("")
    lines.extend(["## Geometry Issues", ""])
    if issues:
        lines.extend(f"- {issue}" for issue in issues)
        lines.append("")
        lines.append(
            "Note: review compounds are kept as separate part solids. A contact or overlap "
            "between independent interface envelopes is not automatically a self-intersection; "
            "the report validates each solid independently before FEM/contact setup."
        )
    else:
        lines.append("- No invalid source shapes or zero-size bounding boxes detected.")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {path}")


def build_review_documents(*, out_dir: Path) -> None:
    chassis_out = out_dir / "chassis-bogie-assembly-states.FCStd"
    body_out = out_dir / "full-body-assembly-states.FCStd"
    tooling_out = out_dir / "lm3-manufacturing-tooling.FCStd"
    checks_by_doc = {
        "Chassis + Bogie Assembly": _write_review_doc(
            output=chassis_out,
            title="OSR chassis and bogie assembly states",
            assembled_items=_chassis_bogie_items(exploded=False),
            exploded_items=_chassis_bogie_items(exploded=True),
        ),
        "Full Body Assembly": _write_review_doc(
            output=body_out,
            title="OSR full body assembly states",
            assembled_items=_full_body_items(exploded=False),
            exploded_items=_full_body_items(exploded=True),
        ),
        "LM3 Manufacturing Tooling": _write_tooling_doc(output=tooling_out),
    }
    _write_report(out_dir / "assembly-geometry-review.md", checks_by_doc)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build FreeCAD assembled/exploded review documents.")
    parser.add_argument("--out-dir", type=Path, default=_artifact_root())
    return parser.parse_args(argv)


def _normalise_freecad_argv(argv: list[str]) -> list[str]:
    args = list(argv)
    if args and Path(args[0]).name == "freecad_assembly_review.py":
        args = args[1:]
    if args and args[0] == "--pass":
        args = args[1:]
    return args


def main(argv: list[str] | None = None) -> None:
    args = parse_args(_normalise_freecad_argv(argv or []))
    build_review_documents(out_dir=args.out_dir)


def _running_as_freecad_script() -> bool:
    return bool(sys.argv[1:2]) and Path(sys.argv[1]).name == "freecad_assembly_review.py"


if __name__ == "__main__" or _running_as_freecad_script():
    main(sys.argv[1:])
