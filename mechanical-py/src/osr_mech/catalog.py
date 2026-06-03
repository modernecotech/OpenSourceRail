"""Regenerate STEP handoff artifacts under `catalog/`.

This is the CLI entry point (`osr-mech-export`). It walks a fixed list
of component × parameter combinations and writes one STEP per entry.
The set is kept deliberately small — just the canonical sizes from the
RFCs plus a couple of Samawah-specific instantiations. Extending the
set is a one-line addition below.

Whole-train STEP assemblies are intentionally opt-in because detailed
trainset exports quickly exceed GitHub's file-size limits. The tracked
full-assembly review format is FreeCAD FCStd, built by
`scripts/freecad_trainset.sh` from the smaller component STEP catalogue.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from build123d import export_step

from .accessibility import add_prm_zones_to_car, platform_tactile_path
from .cad_templates import FIXTURE_BUILDERS, ROLLING_STOCK_TEMPLATE_BUILDERS
from .civil.platform_l_unit import platform_l_unit
from .civil.ugirder import u_girder
from .clearance import reference_envelope, swept_envelope_part
from .common import ConsistFamily, GeometryPreset, RailProfile, StationArchetype
from .depot import DepotArchetype, depot_layout
from .rolling_stock.bogie import (
    bogie_frame,
    bogie_assembly,
    brake_unit,
    gearbox,
    motor_bogie,
    primary_suspension,
    secondary_suspension,
    traction_motor,
    trailer_bogie,
    wheelset,
)
from .rolling_stock.car_body import (
    car_body,
    car_body_exterior,
    car_body_interior,
    car_body_services,
    car_body_structure,
)
from .rolling_stock.cots_equipment import fit_out_car_body
from .rolling_stock.mechanical_interfaces import INTERFACE_BUILDERS
from .rolling_stock.sensor_cowl import sensor_cowl
from .rolling_stock.systems import (
    battery_pack_set,
    car_systems,
    door_system_pair,
    electronics_cabinet,
    end_coupler,
    inter_car_articulation,
    platform_safety_interface,
    tobs_sensor_pack,
    traction_power_rack,
)
from .rolling_stock.trainset import trainset
from .station.canopy import station_canopy
from .station.portal import portal_frame
from .station.solar_roof import solar_roof_panel
from .track.fastener import fastener_assembly
from .track.panel import track_panel
from .track.rail import rail_bar, rail_section
from .track.sleeper import mono_block_sleeper
from .track.turnout import TurnoutTangent, turnout


GENERATED_STEP_DIRS = (
    "track",
    "civil",
    "station",
    "rolling_stock",
    "bogie",
    "depot",
    "fixtures",
)

TRAINSET_STEP_FAMILIES = (
    ConsistFamily.URBAN_SHUTTLE_1CAR,
    ConsistFamily.TRAM_2CAR,
    ConsistFamily.LIGHT_METRO_3CAR,
    ConsistFamily.METRO_4CAR,
    ConsistFamily.METRO_6CAR,
)


def _out(root: Path, *parts: str) -> Path:
    p = root.joinpath(*parts)
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def _export(obj, path: Path) -> None:
    export_step(obj, str(path))
    print(f"wrote {path}")


def _refresh_latest_outputs(root: Path) -> None:
    for folder in GENERATED_STEP_DIRS:
        directory = root / folder
        if not directory.exists():
            continue
        for path in directory.rglob("*.step"):
            path.unlink()
            print(f"removed old STEP artifact {path}")


def export_all(root: Path, *, include_trainset_step: bool = False) -> None:
    _refresh_latest_outputs(root)

    # Track: one rail per profile, one sleeper, one fastener, one panel.
    _export(rail_section(RailProfile.UIC_54E1), _out(root, "track", "rail-54E1-1m.step"))
    _export(rail_section(RailProfile.UIC_60E1), _out(root, "track", "rail-60E1-1m.step"))
    _export(mono_block_sleeper(), _out(root, "track", "sleeper-B70.step"))
    _export(fastener_assembly(), _out(root, "track", "fastener-pandrol.step"))
    _export(
        track_panel(length_mm=6500.0, preset=GeometryPreset.STANDARD_URBAN),
        _out(root, "track", "panel-6500mm-standard-urban.step"),
    )

    # Civil: three U-girder spans + one platform L-unit.
    for span in (20.0, 25.0, 30.0):
        _export(u_girder(span_m=span), _out(root, "civil", f"u-girder-{int(span)}m.step"))
    _export(platform_l_unit(), _out(root, "civil", "platform-l-unit-3m.step"))

    # Station: one portal, one solar panel, the four non-halt archetypes.
    _export(portal_frame(), _out(root, "station", "portal-bay-6m.step"))
    _export(solar_roof_panel(), _out(root, "station", "solar-roof-6x3p5.step"))

    canopy_matrix = [
        (StationArchetype.STANDARD, ConsistFamily.URBAN_SHUTTLE_1CAR),
        (StationArchetype.STANDARD, ConsistFamily.LIGHT_METRO_3CAR),
        (StationArchetype.MAJOR, ConsistFamily.LIGHT_METRO_3CAR),
        (StationArchetype.INTERCHANGE, ConsistFamily.LIGHT_METRO_3CAR),
        (StationArchetype.TERMINAL, ConsistFamily.LIGHT_METRO_3CAR),
        (StationArchetype.STANDARD, ConsistFamily.METRO_4CAR),
    ]
    for arch, consist in canopy_matrix:
        c = station_canopy(archetype=arch, consist=consist)
        _export(
            c,
            _out(
                root,
                "station",
                f"canopy-{arch.value}-{consist.value}.step",
            ),
        )

    # Rolling stock (RFC 0015 cabless).
    _export(sensor_cowl(), _out(root, "rolling_stock", "sensor-cowl.step"))
    _export(car_body(), _out(root, "rolling_stock", "car-body-17m.step"))
    _export(
        car_body_structure(),
        _out(root, "rolling_stock", "car-body-structure.step"),
    )
    _export(
        car_body_exterior(),
        _out(root, "rolling_stock", "car-body-exterior.step"),
    )
    _export(
        car_body_interior(),
        _out(root, "rolling_stock", "car-body-interior.step"),
    )
    _export(
        car_body_services(),
        _out(root, "rolling_stock", "car-body-services.step"),
    )
    _export(
        fit_out_car_body(),
        _out(root, "rolling_stock", "car-body-17m-cots-fit-out.step"),
    )
    _export(door_system_pair(), _out(root, "rolling_stock", "door-system-pair.step"))
    _export(platform_safety_interface(), _out(root, "rolling_stock", "platform-safety-interface.step"))
    _export(battery_pack_set(), _out(root, "rolling_stock", "battery-pack-set.step"))
    _export(traction_power_rack(), _out(root, "rolling_stock", "traction-power-rack.step"))
    _export(electronics_cabinet(), _out(root, "rolling_stock", "electronics-cabinet.step"))
    _export(car_systems(), _out(root, "rolling_stock", "car-systems.step"))
    _export(end_coupler(), _out(root, "rolling_stock", "end-coupler.step"))
    _export(inter_car_articulation(), _out(root, "rolling_stock", "inter-car-articulation.step"))
    _export(tobs_sensor_pack(), _out(root, "rolling_stock", "tobs-sensor-pack.step"))
    for slug, builder in INTERFACE_BUILDERS.items():
        _export(
            builder(),
            _out(root, "rolling_stock", "interfaces", f"{slug}.step"),
        )

    # Bogie components (RFC 0022).
    _export(wheelset(), _out(root, "bogie", "wheelset.step"))
    _export(traction_motor(), _out(root, "bogie", "motor-pmsm.step"))
    _export(gearbox(), _out(root, "bogie", "gearbox.step"))
    _export(primary_suspension(), _out(root, "bogie", "primary-suspension.step"))
    _export(
        secondary_suspension(),
        _out(root, "bogie", "secondary-suspension.step"),
    )
    _export(brake_unit(), _out(root, "bogie", "brake-unit.step"))
    _export(bogie_frame(), _out(root, "bogie", "frame.step"))

    # Bogie assemblies (motor + trailer).
    _export(motor_bogie(), _out(root, "bogie", "motor-bogie.step"))
    _export(trailer_bogie(), _out(root, "bogie", "trailer-bogie.step"))
    # Legacy name — identical to motor-bogie.
    _export(bogie_assembly(), _out(root, "rolling_stock", "bogie-2axle.step"))
    if include_trainset_step:
        for family in TRAINSET_STEP_FAMILIES:
            _export(
                trainset(family=family),
                _out(root, "rolling_stock", f"trainset-{family.value}.step"),
            )
    else:
        print(
            "skipped whole-train STEP assemblies; use "
            "--include-trainset-step for local neutral-format exports"
        )

    # Accessibility (PRM zones) — RFC 0010 + EN 16584.
    _export(
        add_prm_zones_to_car(),
        _out(root, "rolling_stock", "car-prm-zones.step"),
    )
    _export(
        platform_tactile_path(75.0),
        _out(root, "station", "platform-tactile-path-75m.step"),
    )

    # Turnouts — RFC 0012.
    for t in TurnoutTangent:
        slug = t.value.replace(":", "to").replace(".", "p")
        _export(turnout(t), _out(root, "track", f"turnout-{slug}.step"))

    # Depot archetypes — RFC 0014.
    for a in DepotArchetype:
        _export(
            depot_layout(archetype=a),
            _out(root, "depot", f"depot-{a.value}.step"),
        )

    # Kinematic envelope — EN 15273 gauge-clearance visualisation.
    _export(
        swept_envelope_part(reference_envelope()),
        _out(root, "rolling_stock", "kinematic-envelope.step"),
    )

    # Early fabrication templates and COTS fixture envelopes.
    for slug, builder in ROLLING_STOCK_TEMPLATE_BUILDERS.items():
        _export(builder(), _out(root, "rolling_stock", "templates", f"{slug}.step"))
    for slug, builder in FIXTURE_BUILDERS.items():
        _export(builder(), _out(root, "fixtures", f"{slug}.step"))


def main() -> None:
    ap = argparse.ArgumentParser(description="Export every OSR mechanical artifact to STEP.")
    ap.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).resolve().parent.parent.parent / "catalog",
        help="output directory root (default: mechanical-py/catalog)",
    )
    ap.add_argument(
        "--include-trainset-step",
        action="store_true",
        help=(
            "also emit very large whole-train STEP assemblies; by default "
            "full assemblies are kept as tracked FreeCAD FCStd documents"
        ),
    )
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    export_all(args.out, include_trainset_step=args.include_trainset_step)


if __name__ == "__main__":
    main()
