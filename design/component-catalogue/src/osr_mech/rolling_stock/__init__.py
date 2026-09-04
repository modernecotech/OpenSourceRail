"""Rolling-stock parametric geometry — cabless per RFC 0015.

Every trainset in the OpenSourceRail default configuration ships as
GoA 4 (unattended) with no driver cab. The geometry reflects that:

- Both train ends are symmetrical multi-part fiberglass cowls with one
  large dark glass face: passengers can see through the driverless
  front/back, while the same heated RF-transparent glazing carries the
  T-OBS sensor sightline and LED headlamp / marker-light clusters per
  RFC 0015 §5.1.
- Passenger floor is stepped because all cars use standard bogies:
  high-floor end zones sit over the bogies, while the two centre door
  pairs and PRM zone stay at the 350 mm low-floor platform datum.
- Bogie spacing, door openings, and coupler faces follow the RFC 0008
  §3 reference-design dimensions for each consist family.

Scope for v0.1:

- `car_body`        — one parametric layered body assembly: primary
                       structure, exterior, interior, HVAC, electrical,
                       HV/PV, thermal, and fire-routing layers.
- `bogie`           — detailed 2-axle motor/trailer bogie assemblies.
- `sensor_cowl`     — identical A/B-end fiberglass cowl casts with
                       single driverless panoramic end glass, T-OBS
                       aperture, LED headlamps, marker lights, and
                       livery band.
- `systems`         — supplier-neutral envelopes for couplers,
                       detailed inter-car articulation/gangways, doors,
                       batteries, traction power, electronics cabinets,
                       charging, PRM/safety, T-OBS.
- `trainset`        — full consist assembly of N cars coupled together
                       with train-level systems.

Out of scope (reserved for v0.2 or later):

- Pantograph (catenary-free system — not present).
- Supplier-internal geometry and production tolerance stacks.

Interior fit-out (seats, poles, grab-handles, windows, HVAC, PIS
screens, lighting, intercom) lives in [`cots_equipment`](./cots_equipment.py)
as an envelope-reservation catalogue — not part of the structural
car body but sized + placed on it.
"""

from .bogie import motor_bogie, trailer_bogie
from .car_body import (
    car_body,
    car_body_exterior,
    car_body_interior,
    car_body_services,
    car_body_structure,
)
from .cots_equipment import (
    CATALOGUE,
    Category,
    CotsItem,
    bom_per_car,
    fit_out_car_body,
    locations_for,
    total_active_power_w,
    total_mass_kg,
)
from .mechanical_interfaces import (
    INTERFACE_BUILDERS,
    battery_installations,
    bench_on_battery_installations,
    bogie_to_chassis_connector,
    bogie_to_motor_connector,
    cabin_flooring,
    composite_body_roof_attachments,
    door_design,
    door_installations,
    door_mounts,
    door_to_body_installations,
    external_lighting_lidar_system,
    hvac_roof_ducting_installation,
    internal_lighting_installation,
    low_floor_chassis,
    mechanical_interface_package,
    screen_speaker_mountings,
    side_body_frame_attachments,
    train_connector_mount_pair,
    underframe_jacking_recovery_interface,
    window_installations,
)
from .sensor_cowl import sensor_cowl
from .recovery import (
    controlled_recovery_capacity_checks,
    field_recovery_load_cases,
    portable_field_rerailing_kit,
    recovery_mass_scenarios,
)
from .exterior_finish import (
    exterior_finish_review_assembly,
    finish_process,
    finish_process_payload,
    finish_zones,
)
from .small_components import (
    CONNECTOR_FAMILIES,
    FASTENER_FAMILIES,
    door_window_cassette_hardware,
    modular_lighting_cassettes,
    simplified_small_component_package,
    small_component_standard_payload,
    standard_fixture_adapters,
    universal_service_rail_installation,
)
from .systems import (
    battery_pack_set,
    car_systems,
    door_system_pair,
    electronics_cabinet,
    end_coupler,
    inter_car_articulation,
    roof_solar_system,
    tobs_sensor_pack,
    traction_power_rack,
    trainset_systems,
)
from .trainset import trainset

__all__ = [
    "CATALOGUE",
    "Category",
    "CotsItem",
    "INTERFACE_BUILDERS",
    "CONNECTOR_FAMILIES",
    "FASTENER_FAMILIES",
    "battery_installations",
    "bench_on_battery_installations",
    "bogie_to_chassis_connector",
    "bogie_to_motor_connector",
    "bom_per_car",
    "cabin_flooring",
    "car_body",
    "car_body_exterior",
    "car_body_interior",
    "car_body_services",
    "car_body_structure",
    "composite_body_roof_attachments",
    "door_design",
    "door_installations",
    "door_mounts",
    "door_to_body_installations",
    "external_lighting_lidar_system",
    "fit_out_car_body",
    "hvac_roof_ducting_installation",
    "internal_lighting_installation",
    "locations_for",
    "low_floor_chassis",
    "mechanical_interface_package",
    "motor_bogie",
    "screen_speaker_mountings",
    "sensor_cowl",
    "controlled_recovery_capacity_checks",
    "field_recovery_load_cases",
    "portable_field_rerailing_kit",
    "recovery_mass_scenarios",
    "exterior_finish_review_assembly",
    "finish_process",
    "finish_process_payload",
    "finish_zones",
    "battery_pack_set",
    "car_systems",
    "door_system_pair",
    "electronics_cabinet",
    "end_coupler",
    "inter_car_articulation",
    "roof_solar_system",
    "tobs_sensor_pack",
    "total_active_power_w",
    "total_mass_kg",
    "traction_power_rack",
    "side_body_frame_attachments",
    "train_connector_mount_pair",
    "underframe_jacking_recovery_interface",
    "trainset",
    "trainset_systems",
    "trailer_bogie",
    "window_installations",
    "door_window_cassette_hardware",
    "modular_lighting_cassettes",
    "simplified_small_component_package",
    "small_component_standard_payload",
    "standard_fixture_adapters",
    "universal_service_rail_installation",
]
