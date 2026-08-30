"""Anchored rolled-steel plinths for fare and ticket equipment."""

from __future__ import annotations

from osr_mech.cad import Box, Color, Compound, Location, Part


PLINTH_HEIGHT_MM = 240.0


def _plinth(length_mm: float, depth_mm: float, label: str) -> Compound:
    steel = Color(0.38, 0.42, 0.46)
    top = Box(length_mm, depth_mm, 12.0).locate(Location((length_mm / 2, 0, PLINTH_HEIGHT_MM)))
    top.label = f"{label} folded top plate"
    top.color = steel
    curb = Box(length_mm, depth_mm, PLINTH_HEIGHT_MM).locate(Location((length_mm / 2, 0, PLINTH_HEIGHT_MM / 2)))
    curb.label = f"{label} rolled-steel curb and cable void"
    curb.color = steel
    return Compound(label=label, children=[curb, top])


def fare_lane_plinth() -> Compound:
    return _plinth(1_200.0, 750.0, "Fare lane / validator plinth")


def tvm_plinth() -> Compound:
    return _plinth(1_000.0, 900.0, "Ticket-vending-machine plinth")


__all__ = ["PLINTH_HEIGHT_MM", "fare_lane_plinth", "tvm_plinth"]
