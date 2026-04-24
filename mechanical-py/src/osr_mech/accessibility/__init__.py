"""Accessibility (PRM — Persons of Reduced Mobility) zone catalogue.

Jurisdictions mandate accessibility features that most commercial
rolling-stock vendors tuck behind proprietary options:

- **Wheelchair spaces** — clear floor area with securement points,
  adjacent to a powered door, within reach of a passenger-help
  button. EN 16585-1: ≥ 700 × 1 300 mm per space, ≥ 2 per car.
- **Priority seats** — folding or fixed seats adjacent to the
  wheelchair space, reserved by signage for passengers who need
  them. EN 16585-1: ≥ 10 % of seats. OSR targets 15 % per RFC 0008.
- **Tactile guidance paths** — raised stud pattern from platform
  entry to the nearest train door for visually-impaired passengers.
  EN 16584-3 defines the profile.
- **Audio-visual announcements** — covered by PIS screens + PA.
- **Platform-to-train gap** — ≤ 75 mm horizontal + ≤ 50 mm vertical
  per EN 16584-1. With PSDs + level boarding OSR hits this by design.

This module emits parametric geometry + a BOM for these features so
they're no longer invisible in the CAD model. Deployments that need
vendor-specific securement hardware (e.g. Q'Straint) substitute by
matching the envelope.
"""

from .prm import (
    ACCESSIBILITY_SPEC,
    AccessibilitySpec,
    PrmPlatformZone,
    WheelchairBay,
    add_prm_zones_to_car,
    platform_tactile_path,
)

__all__ = [
    "ACCESSIBILITY_SPEC",
    "AccessibilitySpec",
    "PrmPlatformZone",
    "WheelchairBay",
    "add_prm_zones_to_car",
    "platform_tactile_path",
]
