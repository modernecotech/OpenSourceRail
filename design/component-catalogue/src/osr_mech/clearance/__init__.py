"""Gauge clearance — kinematic envelope sweep.

Given a rolling-stock reference profile + a track geometry (straight
tangent, curve radius, cant), sweep the kinematic envelope and check
it against infrastructure features (tunnel walls, platform edges,
adjacent-track centres, station canopies).

Produces:

- A `KinematicEnvelope` describing the peak lateral + vertical sway +
  throw of a body in motion.
- A `ClearanceReport` for each checked infrastructure feature:
  PASS with margin, or FAIL with interference distance.
- An optional visualisation Compound — the swept envelope as a
  translucent shell so a designer can see where the train "reaches"
  relative to fixed infra.
"""

from .envelope import (
    ClearanceReport,
    EN_15273_INFERRED,
    InfrastructureFeature,
    KinematicEnvelope,
    check_feature,
    envelope_swept_on_curve,
    reference_dynamic_width_mm,
    reference_envelope,
    swept_envelope_part,
)

__all__ = [
    "ClearanceReport",
    "EN_15273_INFERRED",
    "InfrastructureFeature",
    "KinematicEnvelope",
    "check_feature",
    "envelope_swept_on_curve",
    "reference_dynamic_width_mm",
    "reference_envelope",
    "swept_envelope_part",
]
