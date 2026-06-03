"""Build FreeCAD review assemblies from the generated STEP catalogue.

The build123d source remains the design authority. This module is a
FreeCAD bridge: run it with ``FreeCADCmd`` to turn catalogue STEP files
into an ``.FCStd`` document with named subassemblies, placements, visual
colours, and optional STEP re-export for downstream CAD review.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path


try:
    import FreeCAD as App  # type: ignore[import-not-found]
    import Import  # type: ignore[import-not-found]
    import Part  # type: ignore[import-not-found]
except Exception as exc:  # pragma: no cover - only exercised outside FreeCAD.
    App = None  # type: ignore[assignment]
    Import = None  # type: ignore[assignment]
    Part = None  # type: ignore[assignment]
    _FREECAD_IMPORT_ERROR = exc
else:
    _FREECAD_IMPORT_ERROR = None


CAR_LENGTH_MM = 17_000.0
COWL_LENGTH_MM = 1_800.0
BOGIE_INSET_MM = 2_500.0
COUPLING_GAP_MM = 0.0

FAMILY_CAR_COUNT = {
    "urban-shuttle-1car": 1,
    "tram-2car": 2,
    "light-metro-3car": 3,
    "metro-4car": 4,
    "metro-6car": 6,
}

FAMILY_MOTORISED = {
    "urban-shuttle-1car": (True,),
    "tram-2car": (True, True),
    "light-metro-3car": (True, False, True),
    "metro-4car": (True, True, True, True),
    "metro-6car": (True, True, True, True, True, True),
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

CAR_INTERFACE_STEPS = (
    ("bogie-to-chassis-connector.step", "bogie-to-chassis connectors"),
    ("low-floor-chassis.step", "low-floor chassis"),
    ("side-body-frame-attachments.step", "side body frame attachments"),
    ("composite-body-roof-attachments.step", "composite body and roof attachments"),
    ("window-installations.step", "window installations"),
    ("door-mounts.step", "door mounts"),
    ("door-installations.step", "door installations"),
    ("door-to-body-installations.step", "door-to-body installations"),
    ("cabin-flooring.step", "cabin flooring"),
    ("battery-installations.step", "battery installations"),
    ("bench-on-battery-installations.step", "bench installations on batteries"),
    ("internal-lighting-installation.step", "internal lighting installation"),
    ("hvac-roof-ducting-installation.step", "HVAC roof and ducting installation"),
    ("screen-speaker-mountings.step", "screen and speaker mountings"),
)


@dataclass(frozen=True)
class StepItem:
    path: Path
    name: str
    group: str
    x_mm: float = 0.0
    y_mm: float = 0.0
    z_mm: float = 0.0
    yaw_deg: float = 0.0
    colour: tuple[float, float, float, float] | None = None


def _require_freecad() -> None:
    if App is None or Part is None or Import is None:
        raise SystemExit(
            "FreeCAD Python modules are not importable. Run this with FreeCADCmd, for example:\n"
            "  FreeCADCmd mechanical-py/src/osr_mech/freecad_trainset.py --family light-metro-3car\n"
            "or use mechanical-py/scripts/freecad_trainset.sh from the repository root.\n"
            f"Import error was: {_FREECAD_IMPORT_ERROR!r}"
        )


def _catalog_root() -> Path:
    return Path(__file__).resolve().parents[2] / "catalog"


def _safe_name(name: str) -> str:
    return "".join(ch if ch.isalnum() else "_" for ch in name).strip("_")


def _add_shape(doc, item: StepItem, groups: dict[str, object]):
    if not item.path.exists():
        raise FileNotFoundError(f"missing STEP input: {item.path}")

    shape = Part.Shape()
    shape.read(str(item.path))

    obj = doc.addObject("Part::Feature", _safe_name(item.name))
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
        group = doc.addObject("App::DocumentObjectGroup", _safe_name(item.group))
        group.Label = item.group
        groups[item.group] = group
    group.addObject(obj)
    return obj


def _trainset_items(catalog: Path, family: str) -> list[StepItem]:
    car_count = FAMILY_CAR_COUNT[family]
    motorised = FAMILY_MOTORISED[family]
    rolling = catalog / "rolling_stock"
    bogies = catalog / "bogie"
    interfaces = rolling / "interfaces"

    total_length = car_count * CAR_LENGTH_MM + (car_count - 1) * COUPLING_GAP_MM
    start_x = -total_length / 2.0
    items: list[StepItem] = []

    items.append(
        StepItem(
            rolling / "sensor-cowl.step",
            "A-end sensor cowl",
            "End Modules",
            x_mm=start_x + COWL_LENGTH_MM,
            yaw_deg=180.0,
            colour=COLOURS["nose"],
        )
    )
    items.append(
        StepItem(
            rolling / "sensor-cowl.step",
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
                StepItem(
                    rolling / "car-body-17m.step",
                    f"{car_label} body",
                    "Car Bodies",
                    x_mm=car_centre_x,
                    colour=COLOURS["body"],
                ),
                StepItem(
                    rolling / "door-system-pair.step",
                    f"{car_label} door system",
                    "Doors and Platform Interface",
                    x_mm=car_centre_x,
                    colour=COLOURS["door"],
                ),
                StepItem(
                    rolling / "battery-pack-set.step",
                    f"{car_label} battery pack set",
                    "Onboard Systems",
                    x_mm=car_centre_x,
                    colour=COLOURS["systems"],
                ),
                StepItem(
                    rolling / "car-systems.step",
                    f"{car_label} systems",
                    "Onboard Systems",
                    x_mm=car_centre_x,
                    colour=COLOURS["systems"],
                ),
            ]
        )
        for file_name, label in CAR_INTERFACE_STEPS:
            items.append(
                StepItem(
                    interfaces / file_name,
                    f"{car_label} {label}",
                    "Mechanical Interfaces",
                    x_mm=car_centre_x,
                    colour=COLOURS["mechanical"],
                )
            )

        bogie_files = (
            ("motor-bogie.step", "motor") if motorised[car_index] else ("trailer-bogie.step", "trailer"),
            ("trailer-bogie.step", "trailer"),
        )
        for end_name, sign, bogie_spec in (
            ("A", -1.0, bogie_files[0]),
            ("B", 1.0, bogie_files[1]),
        ):
            file_name, kind = bogie_spec
            items.append(
                StepItem(
                    bogies / file_name,
                    f"{car_label} {end_name}-end {kind} bogie",
                    "Bogies",
                    x_mm=car_centre_x + sign * (CAR_LENGTH_MM / 2.0 - BOGIE_INSET_MM),
                    colour=COLOURS["bogie"],
                )
            )
            if kind == "motor":
                items.append(
                    StepItem(
                        interfaces / "bogie-to-motor-connector.step",
                        f"{car_label} {end_name}-end bogie-to-motor connector",
                        "Mechanical Interfaces",
                        x_mm=car_centre_x + sign * (CAR_LENGTH_MM / 2.0 - BOGIE_INSET_MM),
                        colour=COLOURS["mechanical"],
                    )
                )

        if car_index + 1 < car_count:
            joint_x = car_centre_x + CAR_LENGTH_MM / 2.0 + COUPLING_GAP_MM / 2.0
            items.extend(
                [
                    StepItem(
                        rolling / "inter-car-articulation.step",
                        f"Articulation {car_index + 1}-{car_index + 2}",
                        "Couplers and Articulation",
                        x_mm=joint_x,
                        colour=COLOURS["interface"],
                    ),
                    StepItem(
                        rolling / "end-coupler.step",
                        f"Internal coupler {car_index + 1}-{car_index + 2}",
                        "Couplers and Articulation",
                        x_mm=joint_x,
                        colour=COLOURS["interface"],
                    ),
                ]
            )

    items.extend(
        [
            StepItem(
                rolling / "end-coupler.step",
                "A-end recovery coupler",
                "Couplers and Articulation",
                x_mm=start_x,
                yaw_deg=180.0,
                colour=COLOURS["interface"],
            ),
            StepItem(
                rolling / "end-coupler.step",
                "B-end recovery coupler",
                "Couplers and Articulation",
                x_mm=start_x + total_length,
                colour=COLOURS["interface"],
            ),
            StepItem(
                rolling / "platform-safety-interface.step",
                "Platform safety interface reference",
                "Doors and Platform Interface",
                y_mm=2_200.0,
                colour=COLOURS["interface"],
            ),
            StepItem(
                rolling / "kinematic-envelope.step",
                "Kinematic envelope reference",
                "Clearance References",
                colour=(0.75, 0.75, 0.75, 0.0),
            ),
        ]
    )
    return items


def build_trainset_document(
    *,
    family: str,
    catalog: Path,
    output: Path,
    export_step: Path | None = None,
) -> None:
    _require_freecad()

    doc = App.newDocument(_safe_name(f"OSR_{family}_review_assembly"))
    doc.Label = f"OSR {family} FreeCAD review assembly"

    groups: dict[str, object] = {}
    objects = []
    for item in _trainset_items(catalog, family):
        objects.append(_add_shape(doc, item, groups))

    doc.addObject("App::DocumentObjectGroup", "SourceNotes").Label = (
        "Generated from build123d STEP catalogue; build123d remains design authority"
    )
    doc.recompute()

    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        output.unlink()
    doc.saveAs(str(output))
    print(f"wrote {output}")

    if export_step is not None:
        export_step.parent.mkdir(parents=True, exist_ok=True)
        if export_step.exists():
            export_step.unlink()
        Import.export(objects, str(export_step))
        print(f"wrote {export_step}")

    App.closeDocument(doc.Name)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a FreeCAD FCStd trainset assembly from OSR catalogue STEP files.",
    )
    parser.add_argument(
        "--family",
        choices=sorted(FAMILY_CAR_COUNT),
        default="light-metro-3car",
        help="trainset family to assemble",
    )
    parser.add_argument(
        "--catalog",
        type=Path,
        default=_catalog_root(),
        help="STEP catalogue root, default: mechanical-py/catalog",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="FCStd output path, default: mechanical-py/catalog/freecad/trainset-<family>.FCStd",
    )
    parser.add_argument(
        "--export-step",
        type=Path,
        default=None,
        help="optional combined STEP export path",
    )
    return parser.parse_args(argv)


def _normalise_freecad_argv(argv: list[str]) -> list[str]:
    """Strip FreeCADCmd's script bookkeeping from ``sys.argv``.

    FreeCADCmd executes ``some_script.py`` with ``__name__`` set to the
    script stem, and keeps both the script path and optional ``--pass``
    marker in ``sys.argv``. Normal Python execution does neither.
    """
    args = list(argv)
    if args and Path(args[0]).name == "freecad_trainset.py":
        args = args[1:]
    if args and args[0] == "--pass":
        args = args[1:]
    return args


def main(argv: list[str] | None = None) -> None:
    args = parse_args(_normalise_freecad_argv(argv or []))
    output = args.out or args.catalog / "freecad" / f"trainset-{args.family}.FCStd"
    build_trainset_document(
        family=args.family,
        catalog=args.catalog,
        output=output,
        export_step=args.export_step,
    )


def _running_as_freecad_script() -> bool:
    return bool(sys.argv[1:2]) and Path(sys.argv[1]).name == "freecad_trainset.py"


if __name__ == "__main__" or _running_as_freecad_script():
    main(sys.argv[1:])
