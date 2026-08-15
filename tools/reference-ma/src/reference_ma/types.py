"""Value types — mirrors of osr-core.

Every field's JSON shape matches serde's default for the Rust type of
the same name. ID newtypes in Rust carry `#[serde(transparent)]`, so
they arrive here as bare ints; no wrapper class is needed.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, NewType, Optional

# Identifier type aliases (for documentation; they are plain ints on the wire).
TrainId = NewType("TrainId", int)
StationId = NewType("StationId", int)
SectionId = NewType("SectionId", int)
SwitchId = NewType("SwitchId", int)
RouteId = NewType("RouteId", int)
EntityId = NewType("EntityId", int)
EntryId = NewType("EntryId", int)
RegionId = NewType("RegionId", int)


class Direction(str, Enum):
    Forward = "Forward"
    Reverse = "Reverse"


@dataclass(frozen=True)
class TrackRef:
    section: SectionId
    offset_mm: int
    direction: Direction

    @classmethod
    def from_json(cls, d: Dict[str, Any]) -> "TrackRef":
        return cls(d["section"], int(d["offset_mm"]), Direction(d["direction"]))


@dataclass(frozen=True)
class Position:
    track_ref: TrackRef
    uncertainty_mm: int

    @classmethod
    def from_json(cls, d: Dict[str, Any]) -> "Position":
        return cls(TrackRef.from_json(d["track_ref"]), int(d["uncertainty_mm"]))


@dataclass
class BrakingCurve:
    service: List[tuple]
    emergency: List[tuple]
    reaction_time_ms: int

    @classmethod
    def from_json(cls, d: Dict[str, Any]) -> "BrakingCurve":
        # Rust serde serialises `Vec<(f32, f32)>` as list-of-lists.
        return cls(
            service=[tuple(pair) for pair in d["service"]],
            emergency=[tuple(pair) for pair in d["emergency"]],
            reaction_time_ms=int(d["reaction_time_ms"]),
        )


@dataclass
class ConsistDescriptor:
    train_class: str  # "LightMetro" | "Metro" | "Engineering" | "Yard"
    car_count: int
    length_mm: int
    mass_kg: int
    max_speed_mps: float
    braking: BrakingCurve
    service_accel_mps2: float
    has_pantograph: bool
    battery_capacity_wh: int

    @classmethod
    def from_json(cls, d: Dict[str, Any]) -> "ConsistDescriptor":
        return cls(
            train_class=d["train_class"],
            car_count=int(d["car_count"]),
            length_mm=int(d["length_mm"]),
            mass_kg=int(d["mass_kg"]),
            max_speed_mps=float(d["max_speed_mps"]),
            braking=BrakingCurve.from_json(d["braking"]),
            service_accel_mps2=float(d["service_accel_mps2"]),
            has_pantograph=bool(d["has_pantograph"]),
            battery_capacity_wh=int(d["battery_capacity_wh"]),
        )

    @staticmethod
    def reference_3car() -> "ConsistDescriptor":
        """Mirror of osr-core `ConsistDescriptor::reference_3car`. Used by
        `apply_position` when a position report arrives before a
        registration (the fallback record)."""
        return ConsistDescriptor(
            train_class="LightMetro",
            car_count=3,
            length_mm=51_000,
            mass_kg=195_000,
            max_speed_mps=22.0,
            braking=BrakingCurve(
                service=[(0.0, 1.1), (20.0, 1.0), (28.0, 0.9)],
                emergency=[(0.0, 1.5), (20.0, 1.4), (28.0, 1.2)],
                reaction_time_ms=400,
            ),
            service_accel_mps2=1.0,
            has_pantograph=False,
            battery_capacity_wh=900_000,
        )


# ---------------------------------------------------------------------------
# Network — static track topology.
# ---------------------------------------------------------------------------


@dataclass
class Station:
    id: StationId
    name: str
    charging_power_kw: int
    dwell_seconds: int
    is_terminal: bool
    is_depot: bool

    @classmethod
    def from_json(cls, d: Dict[str, Any]) -> "Station":
        return cls(
            id=d["id"],
            name=d["name"],
            charging_power_kw=int(d["charging_power_kw"]),
            dwell_seconds=int(d["dwell_seconds"]),
            is_terminal=bool(d["is_terminal"]),
            is_depot=bool(d["is_depot"]),
        )


@dataclass
class Section:
    id: SectionId
    from_station: StationId
    to_station: StationId
    length_mm: int
    max_speed_mps: float

    @classmethod
    def from_json(cls, d: Dict[str, Any]) -> "Section":
        return cls(
            id=d["id"],
            from_station=d["from_station"],
            to_station=d["to_station"],
            length_mm=int(d["length_mm"]),
            max_speed_mps=float(d["max_speed_mps"]),
        )


@dataclass
class Line:
    name: str
    stations: List[StationId]
    forward_sections: List[SectionId]
    reverse_sections: List[SectionId]
    is_ring: bool

    @classmethod
    def from_json(cls, d: Dict[str, Any]) -> "Line":
        return cls(
            name=d["name"],
            stations=list(d["stations"]),
            forward_sections=list(d["forward_sections"]),
            reverse_sections=list(d["reverse_sections"]),
            is_ring=bool(d["is_ring"]),
        )


@dataclass
class Network:
    stations: Dict[StationId, Station] = field(default_factory=dict)
    sections: Dict[SectionId, Section] = field(default_factory=dict)
    lines: List[Line] = field(default_factory=list)

    @classmethod
    def from_json(cls, d: Dict[str, Any]) -> "Network":
        # Rust `BTreeMap<SectionId, Section>` serialises as an *object*
        # whose keys are stringified ints. Decode both halves.
        stations_raw = d.get("stations", {}) or {}
        sections_raw = d.get("sections", {}) or {}
        stations = {int(k): Station.from_json(v) for k, v in stations_raw.items()}
        sections = {int(k): Section.from_json(v) for k, v in sections_raw.items()}
        lines = [Line.from_json(l) for l in d.get("lines", [])]
        return cls(stations=stations, sections=sections, lines=lines)

    def station(self, sid: StationId) -> Station:
        return self.stations[sid]

    def section(self, sec: SectionId) -> Section:
        return self.sections[sec]
