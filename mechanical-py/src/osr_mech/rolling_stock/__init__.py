"""Rolling-stock parametric geometry — cabless per RFC 0015.

Every trainset in the OpenSourceRail default configuration ships as
GoA 4 (unattended) with no driver cab. The geometry reflects that:

- Both car ends are symmetrical nose cowls holding the T-OBS sensor
  pack (ultrasonic × 4 + LIDAR + radar + stereo cameras) per
  RFC 0015 §5.1.
- Passenger floor extends end-to-end; the only non-passenger zone
  inside the lead and rear cars is the locked recovery-mode cabinet
  (RFC 0015 §8.2).
- Bogie spacing, door openings, and coupler faces follow the RFC 0008
  §3 reference-design dimensions for each consist family.

Scope for v0.1:

- `car_body`        — one parametric car shell (length, width, height,
                       door count, door openings, nose-cowl end caps).
- `bogie`           — simplified 2-axle bogie under the car.
- `sensor_cowl`     — nose cone with through-holes for sensors.
- `trainset`        — full consist assembly of N cars coupled together.

Out of scope (reserved for v0.2 or later):

- Interior layout (seats, poles, grab-handles).
- Pantograph (catenary-free system — not present).
- Wheels + axles (part of the bogie simplified as a block).
- Coupler mechanism (represented as a flat face only).
"""

from .bogie import bogie_assembly
from .car_body import car_body
from .sensor_cowl import sensor_cowl
from .trainset import trainset

__all__ = ["bogie_assembly", "car_body", "sensor_cowl", "trainset"]
