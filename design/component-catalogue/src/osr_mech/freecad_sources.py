"""Source-geometry registry used by the FreeCAD document generators."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from osr_mech.cad import export_brep, to_freecad_shape

from osr_mech.clearance import reference_envelope, swept_envelope_part
from osr_mech.civil.platform_l_unit import platform_l_unit
from osr_mech.civil.guideway_channel_edge import guideway_channel_edge_module
from osr_mech.civil.decked_pi import decked_pi_structural_placeholder
from osr_mech.civil.slab import at_grade_slab_panel, elevated_deck_slab_panel
from osr_mech.civil.segmental import segmental_u_envelope
from osr_mech.civil.special_span import special_span_envelope
from osr_mech.civil.ugirder import u_girder_structural_placeholder
from osr_mech.civil.substructure import viaduct_abutment, viaduct_pier
from osr_mech.common import GeometryPreset, RailProfile
from osr_mech.depot.layout import DepotArchetype, depot_layout
from osr_mech.cad_templates.rolling_stock import (
    body_sheet_metal_kit,
    bogie_adapter,
    bolster,
    chassis_interface_assembly,
    door_leaf,
    main_frame,
    motor_cradle,
    sandwich_panel,
)
from osr_mech.rolling_stock.bogie import motor_bogie, trailer_bogie
from osr_mech.rolling_stock.car_body import (
    car_body,
    car_body_exterior,
    car_body_interior,
    car_body_services,
    car_body_structure,
)
from osr_mech.rolling_stock.mechanical_interfaces import INTERFACE_BUILDERS
from osr_mech.rolling_stock.sensor_cowl import sensor_cowl
from osr_mech.rolling_stock.systems import (
    battery_pack_set,
    car_systems,
    door_system_pair,
    end_coupler,
    inter_car_articulation,
    platform_safety_interface,
    train_to_train_articulation,
)
from osr_mech.station.canopy import station_canopy
from osr_mech.station.auxiliary_canopy import auxiliary_canopy_row
from osr_mech.station.portal import portal_frame
from osr_mech.station.plinth import fare_lane_plinth, tvm_plinth
from osr_mech.station.solar_roof import solar_roof_panel
from osr_mech.track.fastener import fastener_assembly
from osr_mech.track.panel import track_panel
from osr_mech.track.rail import rail_bar
from osr_mech.track.sleeper import mono_block_sleeper
from osr_mech.track.turnout import TurnoutTangent, turnout


def _kinematic_envelope():
    return swept_envelope_part(reference_envelope())


SOURCE_BUILDERS: dict[str, Callable[[], object]] = {
    "battery-pack-set": battery_pack_set,
    "car-body-17m": car_body,
    "car-body-exterior": car_body_exterior,
    "car-body-interior": car_body_interior,
    "car-body-services": car_body_services,
    "car-body-structure": car_body_structure,
    "car-systems": car_systems,
    "door-system-pair": door_system_pair,
    "end-coupler": end_coupler,
    "inter-car-articulation": inter_car_articulation,
    "kinematic-envelope": _kinematic_envelope,
    "motor-bogie": motor_bogie,
    "platform-l-unit": platform_l_unit,
    "station-guideway-channel-edge": guideway_channel_edge_module,
    "civil-at-grade-slab-panel": at_grade_slab_panel,
    "civil-elevated-deck-slab-panel": elevated_deck_slab_panel,
    "civil-decked-pi-25m": lambda: decked_pi_structural_placeholder(25.0),
    "civil-u-girder-25m": lambda: u_girder_structural_placeholder(25.0),
    "civil-segmental-u-25m": lambda: segmental_u_envelope(25.0, 2.5),
    "civil-special-span-40m": lambda: special_span_envelope(40.0),
    "civil-viaduct-pier-8m": lambda: viaduct_pier(8.0),
    "civil-viaduct-abutment": viaduct_abutment,
    "track-fastener-assembly": fastener_assembly,
    "track-mono-block-sleeper": mono_block_sleeper,
    "track-rail-60e1-6m": lambda: rail_bar(RailProfile.UIC_60E1, 6000.0),
    "track-panel-standard-urban": lambda: track_panel(6500.0, GeometryPreset.STANDARD_URBAN),
    "track-turnout-1-9": lambda: turnout(TurnoutTangent.T_1_9),
    "station-portal-frame": portal_frame,
    "station-solar-roof-panel": solar_roof_panel,
    "station-canopy-standard": station_canopy,
    "station-auxiliary-canopy-standard": lambda: auxiliary_canopy_row(7),
    "station-fare-lane-plinth": fare_lane_plinth,
    "station-tvm-plinth": tvm_plinth,
    "depot-main-heavy": lambda: depot_layout(DepotArchetype.MAIN_HEAVY, stalls=6, with_training_wing=True),
    "template-main-frame": main_frame,
    "template-sandwich-panel": sandwich_panel,
    "template-door-leaf": door_leaf,
    "template-body-sheet-metal-kit": body_sheet_metal_kit,
    "template-bogie-adapter": bogie_adapter,
    "template-bolster": bolster,
    "template-motor-cradle": motor_cradle,
    "template-chassis-interface-assembly": chassis_interface_assembly,
    "platform-safety-interface": platform_safety_interface,
    "sensor-cowl": sensor_cowl,
    "trailer-bogie": trailer_bogie,
    "train-to-train-articulation": train_to_train_articulation,
    **INTERFACE_BUILDERS,
}


def export_source_brep(key: str, path: str | Path) -> None:
    """Export a source shape as temporary BREP for compatibility tools."""

    ok = export_brep(source_object(key), str(path))
    if not ok:
        raise RuntimeError(f"could not export temporary BREP for {key}")


def source_object(key: str) -> object:
    try:
        builder = SOURCE_BUILDERS[key]
    except KeyError as exc:
        known = ", ".join(sorted(SOURCE_BUILDERS))
        raise KeyError(f"unknown FreeCAD source geometry {key!r}; known keys: {known}") from exc

    return builder()


def source_shape(key: str, *, clean: bool = False):
    """Build a catalogue item and return its native FreeCAD shape.

    Assembly review keeps the catalogue's separate part solids separate;
    callers that require a single boolean body may opt into ``clean=True``.
    """

    shape = to_freecad_shape(source_object(key), clean=clean)
    if shape is None:
        raise RuntimeError(
            f"could not build FreeCAD shape for {key!r}; run under FreeCADCmd or install FreeCAD modules"
        )
    return shape
