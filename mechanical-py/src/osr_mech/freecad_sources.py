"""Source-geometry registry used by the FreeCAD document generators."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from osr_mech.cad import export_brep

from osr_mech.clearance import reference_envelope, swept_envelope_part
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
)


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
    "platform-safety-interface": platform_safety_interface,
    "sensor-cowl": sensor_cowl,
    "trailer-bogie": trailer_bogie,
    **INTERFACE_BUILDERS,
}


def export_source_brep(key: str, path: str | Path) -> None:
    try:
        builder = SOURCE_BUILDERS[key]
    except KeyError as exc:
        known = ", ".join(sorted(SOURCE_BUILDERS))
        raise KeyError(f"unknown FreeCAD source geometry {key!r}; known keys: {known}") from exc

    ok = export_brep(builder(), str(path))
    if not ok:
        raise RuntimeError(f"could not export temporary BREP for {key}")
