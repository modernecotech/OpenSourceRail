"""Match-cast segmental U/box planning family for constrained corridors."""

from __future__ import annotations

from osr_mech.cad import Box, Color, Compound, Location, Part

from .ugirder import EXTERNAL_HEIGHT_MM, EXTERNAL_WIDTH_MM, u_girder_envelope

MIN_SEGMENT_LENGTH_M = 2.5
MAX_SEGMENT_LENGTH_M = 3.0


def segmental_u_envelope(
    span_m: float = 25.0,
    segment_length_m: float = 2.5,
) -> Compound:
    """Show match-cast joints and post-tensioning zones on a span envelope.

    This straight coordination model does not generate the final curved
    match-cast geometry. Each deployment must provide surveyed segment
    coordinates, tendon profiles, epoxy joints, grouting, and launcher loads.
    """

    if not MIN_SEGMENT_LENGTH_M <= segment_length_m <= MAX_SEGMENT_LENGTH_M:
        raise ValueError("match-cast segment length must be 2.5 m .. 3.0 m")
    count = round(span_m / segment_length_m)
    if count < 2 or abs(count * segment_length_m - span_m) > 1e-6:
        raise ValueError("span must divide into equal match-cast segments")

    parts: list[Part] = [u_girder_envelope(span_m)]
    marker = Color(0.25, 0.45, 0.62, 0.70)
    for index in range(1, count):
        joint = Box(EXTERNAL_WIDTH_MM, EXTERNAL_HEIGHT_MM, 20.0).locate(
            Location((0.0, EXTERNAL_HEIGHT_MM / 2.0, index * segment_length_m * 1000.0))
        )
        joint.label = "Match-cast epoxy joint and shear-key design plane"
        joint.color = marker
        parts.append(joint)
    tendon = Box(400.0, 200.0, span_m * 1000.0).locate(
        Location((0.0, 350.0, span_m * 500.0))
    )
    tendon.label = "Post-tensioning tendon and grout QA corridor"
    tendon.color = marker
    parts.append(tendon)
    return Compound(
        label=f"OSR-US segmental U/box coordination envelope ({count} segments)",
        children=parts,
    )


__all__ = ["MAX_SEGMENT_LENGTH_M", "MIN_SEGMENT_LENGTH_M", "segmental_u_envelope"]
