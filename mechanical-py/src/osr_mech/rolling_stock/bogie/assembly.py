"""Bogie assembly — frame + wheelsets + suspensions + (for motor
bogies) drivetrain + brakes.

Two variants share the same frame + wheelsets + suspension SKUs:

- [`motor_bogie`]: full drivetrain (motor + gearbox) on each axle,
  plus a brake unit per axle.
- [`trailer_bogie`]: same frame + wheelsets + suspension as the
  motor bogie, minus the drivetrain. Brakes still fitted.

The legacy `bogie_assembly()` alias returns a motor bogie — every
existing caller was built around the earlier block-geometry bogie,
which was motor by default.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from build123d import Axis, Compound, Location, Part

from ...common import STANDARD_GAUGE_MM
from .brake import brake_unit
from .frame import (
    FRAME_HEIGHT_MM,
    FRAME_LENGTH_MM,
    FRAME_WIDTH_MM,
    PIVOT_BOSS_DIAMETER_MM,
    PIVOT_BOSS_HEIGHT_MM,
    SIDE_BEAM_WIDTH_MM,
    bogie_frame,
)
from .gearbox import GEARBOX_HOUSING_HEIGHT_MM, GEARBOX_HOUSING_LENGTH_MM, gearbox
from .motor import (
    MOTOR_BODY_DIAMETER_MM,
    MOTOR_BODY_LENGTH_MM,
    MOTOR_ENDBELL_LENGTH_MM,
    traction_motor,
)
from .suspension import (
    AIR_SPRING_HEIGHT_MM,
    CHEVRON_HEIGHT_MM,
    primary_suspension,
    secondary_suspension,
)
from .wheelset import (
    BEARING_HOUSING_LENGTH_MM,
    WHEEL_DIAMETER_NEW_MM,
    WHEEL_DIAMETER_WORN_MM,
    wheelset,
)

# Re-exported top-level dimensions (backwards-compatible with old
# `bogie.py`).
WHEELBASE_MM = 2_100.0
WHEEL_DIAMETER_MM = WHEEL_DIAMETER_NEW_MM
BOGIE_FRAME_HEIGHT_MM = FRAME_HEIGHT_MM
BOGIE_FRAME_LENGTH_MM = FRAME_LENGTH_MM
BOGIE_FRAME_WIDTH_MM = FRAME_WIDTH_MM
PIVOT_HEIGHT_MM = 580.0  # above rail head


class BogieVariant(str, Enum):
    """Which drivetrain variant to emit."""

    MOTOR = "motor"
    TRAILER = "trailer"


@dataclass(frozen=True)
class _MountPoints:
    """Geometric anchors where components go."""

    wheelset_y_center_z: float
    frame_z: float
    secondary_z: float


def _mount_points() -> _MountPoints:
    """Resolve vertical mounting positions.

    Z = 0 is rail-head. Wheelset axis is at wheel-radius. Frame sits
    above the primary suspension. Air spring sits on top of the frame."""
    wheelset_axle_z = WHEEL_DIAMETER_NEW_MM / 2.0  # 380 mm
    # Primary chevron pack: compressed height between axle-box top
    # and frame underside. Assume ~50 mm axle-box above wheelset axis +
    # chevron height + frame starting above.
    frame_bottom_z = wheelset_axle_z + 50.0 + CHEVRON_HEIGHT_MM  # 380 + 50 + 110 = 540
    # Frame centroid (since frame origin is at frame geometric centre).
    frame_centroid_z = frame_bottom_z + FRAME_HEIGHT_MM / 2.0
    # Secondary air spring sits on top of the frame + pivot boss.
    secondary_bottom_z = frame_bottom_z + FRAME_HEIGHT_MM
    return _MountPoints(
        wheelset_y_center_z=wheelset_axle_z,
        frame_z=frame_centroid_z,
        secondary_z=secondary_bottom_z,
    )


def _place_wheelsets() -> list[Compound]:
    """Two wheelsets on the bogie centreline at ±wheelbase/2."""
    mp = _mount_points()
    out: list[Compound] = []
    for x_sign in (-1.0, 1.0):
        w = wheelset()
        w = w.locate(
            Location(
                (x_sign * WHEELBASE_MM / 2.0, 0.0, mp.wheelset_y_center_z)
            )
        )
        # label update, preserving the original "Wheelset" prefix
        w.label = f"Wheelset {'+X' if x_sign > 0 else '-X'}"
        out.append(w)
    return out


def _place_primary_suspension() -> list[Compound]:
    """Eight chevron packs: two axles × two bearing housings × two
    packs each. Simplified to four packs at the corners of the
    frame (one per axle × side), which is the dominant load path."""
    mp = _mount_points()
    out: list[Compound] = []
    z = mp.wheelset_y_center_z + CHEVRON_HEIGHT_MM / 2.0 + 40.0
    for x_sign in (-1.0, 1.0):
        for y_sign in (-1.0, 1.0):
            p = primary_suspension()
            p = p.locate(
                Location(
                    (
                        x_sign * WHEELBASE_MM / 2.0,
                        y_sign * (STANDARD_GAUGE_MM / 2.0 + 80.0),
                        z,
                    )
                )
            )
            p.label = f"Primary suspension {'+X' if x_sign > 0 else '-X'}{'+Y' if y_sign > 0 else '-Y'}"
            out.append(p)
    return out


def _place_secondary_suspension() -> list[Compound]:
    """Two air springs on the central bolster — one per side."""
    mp = _mount_points()
    out: list[Compound] = []
    # Air springs sit on top of the bolster, near the side edges.
    y_offset = FRAME_WIDTH_MM / 2.0 - 420.0
    for y_sign in (-1.0, 1.0):
        s = secondary_suspension()
        s = s.locate(Location((0.0, y_sign * y_offset, mp.secondary_z)))
        s.label = f"Secondary suspension {'+Y' if y_sign > 0 else '-Y'}"
        out.append(s)
    return out


def _place_drivetrain() -> list[Compound]:
    """One motor-gearbox pair per wheelset — two per motor bogie.
    Motor hangs off the axle via the gearbox; both pieces sit
    inboard of the wheel on one side (typical axle-hung layout
    where the motor extends past the axle centre)."""
    out: list[Compound] = []
    mp = _mount_points()
    for x_sign in (-1.0, 1.0):
        x0 = x_sign * WHEELBASE_MM / 2.0
        # Gearbox sits centred on the axle.
        gb = gearbox()
        gb = gb.locate(Location((x0, 0.0, mp.wheelset_y_center_z)))
        gb.label = f"Gearbox {'+X' if x_sign > 0 else '-X'}"
        out.append(gb)
        # Motor is cantilevered from the gearbox on the +Y side.
        m = traction_motor()
        # Motor centre X = gearbox centre X; Y = gearbox edge + motor half-length.
        motor_y = GEARBOX_HOUSING_LENGTH_MM / 2.0 + MOTOR_BODY_LENGTH_MM / 2.0 + 80.0
        m = m.locate(
            Location((x0, motor_y, mp.wheelset_y_center_z + 180.0))
        )
        m.label = f"PMSM traction motor {'+X' if x_sign > 0 else '-X'}"
        out.append(m)
    return out


def _place_brakes() -> list[Compound]:
    """One brake unit per axle — at the disc location."""
    out: list[Compound] = []
    mp = _mount_points()
    for x_sign in (-1.0, 1.0):
        b = brake_unit()
        b = b.locate(
            Location(
                (
                    x_sign * WHEELBASE_MM / 2.0,
                    -150.0,
                    mp.wheelset_y_center_z,
                )
            )
        )
        b.label = f"Brake unit {'+X' if x_sign > 0 else '-X'}"
        out.append(b)
    return out


def _assemble(variant: BogieVariant) -> Compound:
    parts: list[Part | Compound] = []

    # Frame centred on the bogie geometric centre.
    mp = _mount_points()
    frame = bogie_frame().locate(Location((0.0, 0.0, mp.frame_z - FRAME_HEIGHT_MM / 2.0)))
    frame.label = "Bogie frame"
    parts.append(frame)

    parts.extend(_place_wheelsets())
    parts.extend(_place_primary_suspension())
    parts.extend(_place_secondary_suspension())
    parts.extend(_place_brakes())
    if variant == BogieVariant.MOTOR:
        parts.extend(_place_drivetrain())

    tag = "motor (Bo-Bo)" if variant == BogieVariant.MOTOR else "trailer"
    return Compound(
        label=f"Bogie — {tag} (RFC 0022)",
        children=parts,
    )


def motor_bogie() -> Compound:
    """Full motor bogie — every axle is driven by a PMSM + gearbox."""
    return _assemble(BogieVariant.MOTOR)


def trailer_bogie() -> Compound:
    """Trailer bogie — same frame + suspension + wheelsets, no
    drivetrain."""
    return _assemble(BogieVariant.TRAILER)


def bogie(variant: BogieVariant = BogieVariant.MOTOR) -> Compound:
    """Either-variant entry point."""
    return _assemble(variant)


def bogie_assembly() -> Compound:
    """Historical alias — returns a motor bogie. Kept so callers that
    predate the motor/trailer split continue to work."""
    return motor_bogie()


def bogie_footprint_length_mm() -> float:
    return FRAME_LENGTH_MM
