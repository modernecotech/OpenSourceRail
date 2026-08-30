"""Build FreeCAD trainset review assemblies from parametric source geometry.

Run this with ``FreeCADCmd`` to create a compact ``.FCStd`` document with
named subassemblies, placements, and visual colours. The Python source
remains the design authority; FreeCAD is the tracked review format.
"""

from __future__ import annotations

import argparse
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

from osr_mech.freecad_occ_bridge import SourceGeometry, freecad_shape_from_source, safe_name


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
from osr_mech.rolling_stock.bogie import WHEELBASE_MM

CAR_LENGTH_MM = PROMOTED_LIGHT_METRO_CAR_LENGTH_MM
COWL_LENGTH_MM = 1_800.0
# The bogie pivot datum is one bogie wheelbase inboard from each car end.
# Keep this tied to the detailed bogie model rather than duplicating a
# placement value here; this prevents the body/chassis and assembly views
# drifting apart.
BOGIE_INSET_MM = WHEELBASE_MM
# Body/chassis secondary-seat datum minus the detailed motor-bogie top
# envelope. This is the vertical marriage position used by the chassis
# assembly review, so the trainset and single-car documents share one
# body-to-bogie interface.
BOGIE_SEAT_Z_MM = 740.0 - 1_072.5
COUPLING_GAP_MM = 0.0

FAMILY_CAR_COUNT = {
    "urban-shuttle-1car": 1,
    "tram-2car": 2,
    "light-metro-3car": 3,
    "metro-4car": 4,
    "metro-6car": 6,
}

COLOURS = {
    "body": (0.88, 0.91, 0.92, 0.0),
    "nose": (0.08, 0.12, 0.16, 0.0),
    "bogie": (0.12, 0.12, 0.12, 0.0),
    "systems": (0.18, 0.39, 0.68, 0.0),
    "door": (0.05, 0.45, 0.66, 0.0),
    "interface": (0.95, 0.68, 0.18, 0.0),
    "mechanical": (0.60, 0.62, 0.66, 0.0),
}

CAR_INTERFACE_SOURCES = (
    ("bogie-to-chassis-connector", "bogie-to-chassis connectors"),
    ("low-floor-chassis", "low-floor chassis"),
    ("side-body-frame-attachments", "side body frame attachments"),
    ("composite-body-roof-attachments", "composite body and roof attachments"),
    ("window-installations", "window installations"),
    ("door-mounts", "door mounts"),
    ("door-design", "door leaf designs"),
    ("door-installations", "door installations"),
    ("door-to-body-installations", "door-to-body installations"),
    ("cabin-flooring", "cabin flooring"),
    ("battery-installations", "battery installations"),
    ("bench-on-battery-installations", "bench installations on batteries"),
    ("internal-lighting-installation", "internal lighting installation"),
    ("hvac-roof-ducting-installation", "HVAC roof and ducting installation"),
    ("screen-speaker-mountings", "screen and speaker mountings"),
    ("external-lighting-lidar-system", "external lighting and lidar systems"),
    ("train-connector-mount-pair", "train connector mounts"),
)


@dataclass(frozen=True)
class GeometryItem:
    source: SourceGeometry
    name: str
    group: str
    x_mm: float = 0.0
    y_mm: float = 0.0
    z_mm: float = 0.0
    yaw_deg: float = 0.0
    colour: tuple[float, float, float, float] | None = None


def _require_freecad() -> None:
    if App is None or Part is None:
        raise SystemExit(
            "FreeCAD Python modules are not importable. Run this with FreeCADCmd, for example:\n"
            "  FreeCADCmd design/component-catalogue/src/osr_mech/freecad_trainset.py --family light-metro-3car\n"
            "or use design/component-catalogue/scripts/freecad_trainset.sh from the repository root.\n"
            f"Import error was: {_FREECAD_IMPORT_ERROR!r}"
        )


def _artifact_root() -> Path:
    return Path(__file__).resolve().parents[2] / "models" / "cad"


def _source(key: str) -> SourceGeometry:
    return SourceGeometry(key=key)


def _interface_source(key: str) -> SourceGeometry:
    return _source(key)


def _add_shape(
    doc,
    item: GeometryItem,
    groups: dict[str, object],
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

    group = groups.get(item.group)
    if group is None:
        group = doc.addObject("App::DocumentObjectGroup", safe_name(item.group))
        group.Label = item.group
        groups[item.group] = group
    group.addObject(obj)
    return obj


def _trainset_items(family: str) -> list[GeometryItem]:
    car_count = FAMILY_CAR_COUNT[family]

    total_length = car_count * CAR_LENGTH_MM + (car_count - 1) * COUPLING_GAP_MM
    start_x = -total_length / 2.0
    items: list[GeometryItem] = []

    items.append(
        GeometryItem(
            _source("sensor-cowl"),
            "A-end sensor cowl",
            "End Modules",
            x_mm=start_x + COWL_LENGTH_MM,
            yaw_deg=180.0,
            colour=COLOURS["nose"],
        )
    )
    items.append(
        GeometryItem(
            _source("sensor-cowl"),
            "B-end sensor cowl",
            "End Modules",
            x_mm=start_x + total_length - COWL_LENGTH_MM,
            colour=COLOURS["nose"],
        )
    )

    for car_index in range(car_count):
        car_centre_x = start_x + car_index * (CAR_LENGTH_MM + COUPLING_GAP_MM) + CAR_LENGTH_MM / 2.0
        car_label = f"Car {car_index + 1}"
        items.extend(
            [
                GeometryItem(
                    _source("car-body-17m"),
                    f"{car_label} body",
                    "Car Bodies",
                    x_mm=car_centre_x,
                    colour=COLOURS["body"],
                ),
                GeometryItem(
                    _source("door-system-pair"),
                    f"{car_label} door system",
                    "Doors and Platform Interface",
                    x_mm=car_centre_x,
                    colour=COLOURS["door"],
                ),
                GeometryItem(
                    _source("battery-pack-set"),
                    f"{car_label} battery pack set",
                    "Onboard Systems",
                    x_mm=car_centre_x,
                    colour=COLOURS["systems"],
                ),
                GeometryItem(
                    _source("car-systems"),
                    f"{car_label} systems",
                    "Onboard Systems",
                    x_mm=car_centre_x,
                    colour=COLOURS["systems"],
                ),
            ]
        )
        for key, label in CAR_INTERFACE_SOURCES:
            items.append(
                GeometryItem(
                    _interface_source(key),
                    f"{car_label} {label}",
                    "Mechanical Interfaces",
                    x_mm=car_centre_x,
                    colour=COLOURS["mechanical"],
                )
            )

        bogie_specs = (
            (_source("motor-bogie"), "motor"),
            (_source("trailer-bogie"), "trailer"),
        )
        for end_name, sign, bogie_spec in (
            ("A", -1.0, bogie_specs[0]),
            ("B", 1.0, bogie_specs[1]),
        ):
            source, kind = bogie_spec
            items.append(
                GeometryItem(
                    source,
                    f"{car_label} {end_name}-end {kind} bogie",
                    "Bogies",
                    x_mm=car_centre_x + sign * (CAR_LENGTH_MM / 2.0 - BOGIE_INSET_MM),
                    z_mm=BOGIE_SEAT_Z_MM,
                    colour=COLOURS["bogie"],
                )
            )
            if kind == "motor":
                items.append(
                    GeometryItem(
                        _interface_source("bogie-to-motor-connector"),
                        f"{car_label} {end_name}-end bogie-to-motor connector",
                        "Mechanical Interfaces",
                        x_mm=car_centre_x + sign * (CAR_LENGTH_MM / 2.0 - BOGIE_INSET_MM),
                        z_mm=BOGIE_SEAT_Z_MM,
                        colour=COLOURS["mechanical"],
                    )
                )

        if car_index + 1 < car_count:
            joint_x = car_centre_x + CAR_LENGTH_MM / 2.0 + COUPLING_GAP_MM / 2.0
            items.extend(
                [
                    GeometryItem(
                        _source("inter-car-articulation"),
                        f"Articulation {car_index + 1}-{car_index + 2}",
                        "Couplers and Articulation",
                        x_mm=joint_x,
                        colour=COLOURS["interface"],
                    ),
                    GeometryItem(
                        _source("end-coupler"),
                        f"Internal coupler {car_index + 1}-{car_index + 2}",
                        "Couplers and Articulation",
                        x_mm=joint_x,
                        colour=COLOURS["interface"],
                    ),
                ]
            )

    items.extend(
        [
            GeometryItem(
                _source("end-coupler"),
                "A-end recovery coupler",
                "Couplers and Articulation",
                x_mm=start_x,
                yaw_deg=180.0,
                colour=COLOURS["interface"],
            ),
            GeometryItem(
                _source("end-coupler"),
                "B-end recovery coupler",
                "Couplers and Articulation",
                x_mm=start_x + total_length,
                colour=COLOURS["interface"],
            ),
            GeometryItem(
                _source("platform-safety-interface"),
                "Platform safety interface reference",
                "Doors and Platform Interface",
                y_mm=2_200.0,
                colour=COLOURS["interface"],
            ),
            GeometryItem(
                _source("kinematic-envelope"),
                "Kinematic envelope reference",
                "Clearance References",
                colour=(0.75, 0.75, 0.75, 0.0),
            ),
        ]
    )
    return items


def build_trainset_document(*, family: str, output: Path) -> None:
    _require_freecad()

    doc = App.newDocument(safe_name(f"OSR_{family}_review_assembly"))
    doc.Label = f"OSR {family} FreeCAD review assembly"

    groups: dict[str, object] = {}
    shape_cache: dict[str, object] = {}
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="osr-freecad-brep-", dir=output.parent) as tmp:
        temp_dir = Path(tmp)
        for item in _trainset_items(family):
            _add_shape(doc, item, groups, shape_cache, temp_dir)

    doc.addObject("App::DocumentObjectGroup", "SourceNotes").Label = (
        "Generated directly from parametric source geometry; Python source remains design authority"
    )
    doc.recompute()

    if output.exists():
        output.unlink()
    doc.saveAs(str(output))
    print(f"wrote {output}")

    App.closeDocument(doc.Name)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a FreeCAD FCStd trainset assembly from OSR source geometry.",
    )
    parser.add_argument(
        "--family",
        choices=sorted(FAMILY_CAR_COUNT),
        default="light-metro-3car",
        help="trainset family to assemble",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="FCStd output path, default: design/component-catalogue/models/cad/trainset-<family>.FCStd",
    )
    return parser.parse_args(argv)


def _normalise_freecad_argv(argv: list[str]) -> list[str]:
    """Strip FreeCADCmd's script bookkeeping from ``sys.argv``."""
    args = list(argv)
    if args and Path(args[0]).name == "freecad_trainset.py":
        args = args[1:]
    if args and args[0] == "--pass":
        args = args[1:]
    return args


def main(argv: list[str] | None = None) -> None:
    args = parse_args(_normalise_freecad_argv(argv or []))
    output = args.out or _artifact_root() / f"trainset-{args.family}.FCStd"
    build_trainset_document(family=args.family, output=output)


def _running_as_freecad_script() -> bool:
    return bool(sys.argv[1:2]) and Path(sys.argv[1]).name == "freecad_trainset.py"


if __name__ == "__main__" or _running_as_freecad_script():
    main(sys.argv[1:])
