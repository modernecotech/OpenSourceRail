"""Regenerate every STEP artifact under `catalog/`.

This is the CLI entry point (`osr-mech-export`). It walks a fixed list
of component × parameter combinations and writes one STEP per entry.
The set is kept deliberately small — just the canonical sizes from the
RFCs plus a couple of Samawah-specific instantiations. Extending the
set is a one-line addition below.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from build123d import export_step

from .accessibility import add_prm_zones_to_car, platform_tactile_path
from .civil.platform_l_unit import platform_l_unit
from .civil.ugirder import u_girder
from .clearance import reference_envelope, swept_envelope_part
from .common import ConsistFamily, GeometryPreset, RailProfile, StationArchetype
from .depot import DepotArchetype, depot_layout
from .rolling_stock.bogie import bogie_assembly
from .rolling_stock.car_body import car_body
from .rolling_stock.cots_equipment import fit_out_car_body
from .rolling_stock.sensor_cowl import sensor_cowl
from .rolling_stock.trainset import trainset
from .station.canopy import station_canopy
from .station.portal import portal_frame
from .station.solar_roof import solar_roof_panel
from .track.fastener import fastener_assembly
from .track.panel import track_panel
from .track.rail import rail_bar, rail_section
from .track.sleeper import mono_block_sleeper
from .track.turnout import TurnoutTangent, turnout


def _out(root: Path, *parts: str) -> Path:
    p = root.joinpath(*parts)
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def _export(obj, path: Path) -> None:
    export_step(obj, str(path))
    print(f"wrote {path}")


def export_all(root: Path) -> None:
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
    _export(car_body(), _out(root, "rolling_stock", "car-body-22m.step"))
    _export(bogie_assembly(), _out(root, "rolling_stock", "bogie-2axle.step"))
    _export(
        fit_out_car_body(),
        _out(root, "rolling_stock", "car-body-22m-cots-fit-out.step"),
    )
    for family in (
        ConsistFamily.TRAM_2CAR,
        ConsistFamily.LIGHT_METRO_3CAR,
        ConsistFamily.METRO_4CAR,
        ConsistFamily.METRO_6CAR,
    ):
        _export(
            trainset(family=family),
            _out(root, "rolling_stock", f"trainset-{family.value}.step"),
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


def main() -> None:
    ap = argparse.ArgumentParser(description="Export every OSR mechanical artifact to STEP.")
    ap.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).resolve().parent.parent.parent / "catalog",
        help="output directory root (default: mechanical-py/catalog)",
    )
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    export_all(args.out)


if __name__ == "__main__":
    main()
