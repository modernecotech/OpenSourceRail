"""Bogie — detailed component + assembly CAD.

Per [RFC 0022](../../../../docs/rfcs/0022-bogie-traction-drive.md):

- 2-axle pivoting, Bo-Bo when powered, trailer when not.
- Axle-hung PMSM traction motors + single-stage parallel gearbox.
- Chevron rubber primary suspension; air-spring secondary.
- 760 mm / 680 mm wheels, 2 100 mm wheelbase, 1 435 mm gauge.

**Components** (each is a separate CAD builder function):

- `wheelset`      — axle + 2 wheels + bearings + brake disc
- `motor`         — PMSM axle-hung
- `gearbox`       — single-stage parallel spur
- `suspension`    — chevron primary + air secondary
- `brake`         — electromagnetic caliper actuator
- `frame`         — the H-frame that holds everything

**Assemblies** (compose components):

- `motor_bogie`   — frame + 2 wheelsets + primary + secondary +
                    2 motor-gearbox drivetrains + 2 brakes
- `trailer_bogie` — same, minus the motor-gearbox drivetrains

Exports keep `bogie_assembly` as the historical entry point
(alias for `motor_bogie`) so existing callers don't break.
"""

from .assembly import (
    BogieVariant,
    BOGIE_FRAME_HEIGHT_MM,
    BOGIE_FRAME_LENGTH_MM,
    BOGIE_FRAME_WIDTH_MM,
    PIVOT_HEIGHT_MM,
    WHEEL_DIAMETER_MM,
    WHEEL_DIAMETER_WORN_MM,
    WHEELBASE_MM,
    bogie,
    bogie_assembly,
    motor_bogie,
    trailer_bogie,
)
from .brake import brake_unit
from .frame import bogie_frame
from .gearbox import gearbox
from .motor import traction_motor
from .suspension import primary_suspension, secondary_suspension
from .wheelset import wheelset

__all__ = [
    "BOGIE_FRAME_HEIGHT_MM",
    "BOGIE_FRAME_LENGTH_MM",
    "BOGIE_FRAME_WIDTH_MM",
    "BogieVariant",
    "PIVOT_HEIGHT_MM",
    "WHEELBASE_MM",
    "WHEEL_DIAMETER_MM",
    "WHEEL_DIAMETER_WORN_MM",
    "bogie",
    "bogie_assembly",
    "bogie_frame",
    "brake_unit",
    "gearbox",
    "motor_bogie",
    "primary_suspension",
    "secondary_suspension",
    "traction_motor",
    "trailer_bogie",
    "wheelset",
]
