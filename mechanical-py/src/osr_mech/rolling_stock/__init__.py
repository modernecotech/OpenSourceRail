"""Rolling-stock parametric geometry — cabless per RFC 0015.

Every trainset in the OpenSourceRail default configuration ships as
GoA 4 (unattended) with no driver cab. The geometry reflects that:

- Both train ends are symmetrical open-glass nose cowls: passengers
  can see through the driverless front/back, while the same heated
  RF-transparent glass carries the T-OBS sensor sightline and LED
  headlamp / marker-light clusters per RFC 0015 §5.1.
- Passenger floor is stepped because all cars use standard bogies:
  high-floor end zones sit over the bogies, while the centre door and
  PRM zone stays at the 350 mm low-floor platform datum.
- Bogie spacing, door openings, and coupler faces follow the RFC 0008
  §3 reference-design dimensions for each consist family.

Scope for v0.1:

- `car_body`        — one parametric layered body assembly: primary
                       structure, exterior, interior, HVAC, electrical,
                       HV/PV, thermal, and fire-routing layers.
- `bogie`           — detailed 2-axle motor/trailer bogie assemblies.
- `sensor_cowl`     — open driverless glass end with T-OBS aperture,
                       LED headlamps, marker lights, and livery band.
- `systems`         — supplier-neutral envelopes for couplers,
                       articulation, doors, batteries, traction power,
                       electronics cabinets, charging, PRM/safety, T-OBS.
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

from .bogie import bogie_assembly
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
from .sensor_cowl import sensor_cowl
from .systems import (
    battery_pack_set,
    car_systems,
    door_system_pair,
    electronics_cabinet,
    end_coupler,
    inter_car_articulation,
    tobs_sensor_pack,
    traction_power_rack,
    trainset_systems,
)
from .trainset import trainset

__all__ = [
    "CATALOGUE",
    "Category",
    "CotsItem",
    "bogie_assembly",
    "bom_per_car",
    "car_body",
    "car_body_exterior",
    "car_body_interior",
    "car_body_services",
    "car_body_structure",
    "fit_out_car_body",
    "locations_for",
    "sensor_cowl",
    "battery_pack_set",
    "car_systems",
    "door_system_pair",
    "electronics_cabinet",
    "end_coupler",
    "inter_car_articulation",
    "tobs_sensor_pack",
    "total_active_power_w",
    "total_mass_kg",
    "traction_power_rack",
    "trainset",
    "trainset_systems",
]
