"""Entry schema — mirror of osr-interlocking::log.

Rust's `EntryPayload` is an externally-tagged enum, so serde produces
`{"TrainRegistration": {...}}`, `{"TrainPositionReport": {...}}`, etc.
We round-trip the same shape here.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from .types import (
    ConsistDescriptor,
    Direction,
    EntityId,
    EntryId,
    Position,
    RegionId,
    RouteId,
    SectionId,
    StationId,
    SwitchId,
    TrackRef,
    TrainId,
)


class PositionSource(str, Enum):
    Gnss = "Gnss"
    Imu = "Imu"
    Odometry = "Odometry"
    Beacon = "Beacon"


class IntrusionState(str, Enum):
    Clear = "Clear"
    Unknown = "Unknown"
    Present = "Present"


class SwitchPosition(str, Enum):
    Normal = "Normal"
    Reverse = "Reverse"
    Transitioning = "Transitioning"
    Unknown = "Unknown"


class Confidence(str, Enum):
    Locked = "Locked"
    Observed = "Observed"
    Transitioning = "Transitioning"
    Unknown = "Unknown"


class HealthStatus(str, Enum):
    Ok = "Ok"
    Degraded = "Degraded"
    Failing = "Failing"


class RestrictionReason(str, Enum):
    Permanent = "Permanent"
    Temporary = "Temporary"
    Emergency = "Emergency"
    Weather = "Weather"
    InfrastructureFault = "InfrastructureFault"


# ---------------------------------------------------------------------------
# Payload variants
# ---------------------------------------------------------------------------


@dataclass
class TrainPositionReport:
    train_id: TrainId
    head_position: Position
    tail_position: Position
    speed_mmps: int
    speed_uncertainty_mmps: int
    heading: Direction
    contributing_sources: List[PositionSource]
    onboard_time_ns: int
    pack_soc_ppt: int

    @classmethod
    def from_json(cls, d: Dict[str, Any]) -> "TrainPositionReport":
        return cls(
            train_id=d["train_id"],
            head_position=Position.from_json(d["head_position"]),
            tail_position=Position.from_json(d["tail_position"]),
            speed_mmps=int(d["speed_mmps"]),
            speed_uncertainty_mmps=int(d["speed_uncertainty_mmps"]),
            heading=Direction(d["heading"]),
            contributing_sources=[PositionSource(s) for s in d["contributing_sources"]],
            onboard_time_ns=int(d["onboard_time_ns"]),
            pack_soc_ppt=int(d["pack_soc_ppt"]),
        )


@dataclass
class SwitchCommand:
    switch_id: SwitchId
    requested_position: SwitchPosition
    requested_by: EntityId
    lock_until: Optional[EntryId]

    @classmethod
    def from_json(cls, d: Dict[str, Any]) -> "SwitchCommand":
        return cls(
            switch_id=d["switch_id"],
            requested_position=SwitchPosition(d["requested_position"]),
            requested_by=d["requested_by"],
            lock_until=d.get("lock_until"),
        )


@dataclass
class SwitchObservation:
    switch_id: SwitchId
    observed_position: SwitchPosition
    confidence: Confidence
    observed_at_ns: int

    @classmethod
    def from_json(cls, d: Dict[str, Any]) -> "SwitchObservation":
        return cls(
            switch_id=d["switch_id"],
            observed_position=SwitchPosition(d["observed_position"]),
            confidence=Confidence(d["confidence"]),
            observed_at_ns=int(d["observed_at_ns"]),
        )


@dataclass
class RouteRequest:
    route_id: RouteId
    requested_by: EntityId
    entry_point: TrackRef
    exit_point: TrackRef
    train_id: Optional[TrainId]

    @classmethod
    def from_json(cls, d: Dict[str, Any]) -> "RouteRequest":
        return cls(
            route_id=d["route_id"],
            requested_by=d["requested_by"],
            entry_point=TrackRef.from_json(d["entry_point"]),
            exit_point=TrackRef.from_json(d["exit_point"]),
            train_id=d.get("train_id"),
        )


@dataclass
class RouteGrant:
    route_id: RouteId
    train_id: TrainId
    locked_switches: List[SwitchId]
    locked_sections: List[SectionId]
    expires_at_ns: int

    @classmethod
    def from_json(cls, d: Dict[str, Any]) -> "RouteGrant":
        return cls(
            route_id=d["route_id"],
            train_id=d["train_id"],
            locked_switches=list(d["locked_switches"]),
            locked_sections=list(d["locked_sections"]),
            expires_at_ns=int(d["expires_at_ns"]),
        )


@dataclass
class RouteRelease:
    route_id: RouteId
    reason: str

    @classmethod
    def from_json(cls, d: Dict[str, Any]) -> "RouteRelease":
        return cls(route_id=d["route_id"], reason=d["reason"])


@dataclass
class SpeedRestriction:
    section: SectionId
    from_offset_mm: int
    to_offset_mm: int
    max_speed_mmps: int
    reason: RestrictionReason
    effective_from_ns: int
    effective_until_ns: Optional[int]
    issued_by: EntityId

    @classmethod
    def from_json(cls, d: Dict[str, Any]) -> "SpeedRestriction":
        return cls(
            section=d["section"],
            from_offset_mm=int(d["from_offset_mm"]),
            to_offset_mm=int(d["to_offset_mm"]),
            max_speed_mmps=int(d["max_speed_mmps"]),
            reason=RestrictionReason(d["reason"]),
            effective_from_ns=int(d["effective_from_ns"]),
            effective_until_ns=(
                int(d["effective_until_ns"])
                if d.get("effective_until_ns") is not None
                else None
            ),
            issued_by=d["issued_by"],
        )


@dataclass
class SectionIntrusion:
    section: SectionId
    state: IntrusionState
    issued_by: EntityId
    observed_at_ns: int

    @classmethod
    def from_json(cls, d: Dict[str, Any]) -> "SectionIntrusion":
        return cls(
            section=d["section"],
            state=IntrusionState(d["state"]),
            issued_by=d["issued_by"],
            observed_at_ns=int(d["observed_at_ns"]),
        )


@dataclass
class TrainRegistration:
    train_id: TrainId
    consist: ConsistDescriptor
    initial_position: Position

    @classmethod
    def from_json(cls, d: Dict[str, Any]) -> "TrainRegistration":
        return cls(
            train_id=d["train_id"],
            consist=ConsistDescriptor.from_json(d["consist"]),
            initial_position=Position.from_json(d["initial_position"]),
        )


@dataclass
class TrainDeparture:
    train_id: TrainId
    handed_off_to: Optional[RegionId]
    handoff_time_ns: int

    @classmethod
    def from_json(cls, d: Dict[str, Any]) -> "TrainDeparture":
        return cls(
            train_id=d["train_id"],
            handed_off_to=d.get("handed_off_to"),
            handoff_time_ns=int(d["handoff_time_ns"]),
        )


@dataclass
class Heartbeat:
    from_entity: EntityId
    health: HealthStatus
    monotonic_seq: int

    @classmethod
    def from_json(cls, d: Dict[str, Any]) -> "Heartbeat":
        return cls(
            from_entity=d["from_entity"],
            health=HealthStatus(d["health"]),
            monotonic_seq=int(d["monotonic_seq"]),
        )


@dataclass
class MaintenanceOverride:
    section: SectionId
    from_offset_mm: int
    to_offset_mm: int
    granted_to: EntityId
    granted_until_ns: int
    rationale: str

    @classmethod
    def from_json(cls, d: Dict[str, Any]) -> "MaintenanceOverride":
        return cls(
            section=d["section"],
            from_offset_mm=int(d["from_offset_mm"]),
            to_offset_mm=int(d["to_offset_mm"]),
            granted_to=d["granted_to"],
            granted_until_ns=int(d["granted_until_ns"]),
            rationale=d["rationale"],
        )


@dataclass
class FormatVersion:
    current: int
    min_compatible: int
    schema_sha256_hex: str

    @classmethod
    def from_json(cls, d: Dict[str, Any]) -> "FormatVersion":
        return cls(
            current=int(d["current"]),
            min_compatible=int(d["min_compatible"]),
            schema_sha256_hex=d["schema_sha256_hex"],
        )


# Union type for an EntryPayload. Kept as a plain tuple `(tag, value)`
# after decoding — one variant per tag.
EntryPayload = Union[
    TrainPositionReport,
    SwitchCommand,
    SwitchObservation,
    RouteRequest,
    RouteGrant,
    RouteRelease,
    SpeedRestriction,
    SectionIntrusion,
    TrainRegistration,
    TrainDeparture,
    Heartbeat,
    MaintenanceOverride,
    FormatVersion,
]


_PAYLOAD_DECODERS = {
    "TrainPositionReport": TrainPositionReport.from_json,
    "SwitchCommand": SwitchCommand.from_json,
    "SwitchObservation": SwitchObservation.from_json,
    "RouteRequest": RouteRequest.from_json,
    "RouteGrant": RouteGrant.from_json,
    "RouteRelease": RouteRelease.from_json,
    "SpeedRestriction": SpeedRestriction.from_json,
    "SectionIntrusion": SectionIntrusion.from_json,
    "TrainRegistration": TrainRegistration.from_json,
    "TrainDeparture": TrainDeparture.from_json,
    "Heartbeat": Heartbeat.from_json,
    "MaintenanceOverride": MaintenanceOverride.from_json,
    "FormatVersion": FormatVersion.from_json,
}


def _decode_payload(obj: Dict[str, Any]) -> EntryPayload:
    if len(obj) != 1:
        raise ValueError(
            f"expected externally-tagged enum with one key, got {list(obj)}"
        )
    tag, inner = next(iter(obj.items()))
    decoder = _PAYLOAD_DECODERS.get(tag)
    if decoder is None:
        raise ValueError(f"unknown EntryPayload variant {tag!r}")
    return decoder(inner)


@dataclass
class Entry:
    entry_id: EntryId
    term: int
    timestamp_ns: int
    payload: EntryPayload

    @classmethod
    def from_json(cls, d: Dict[str, Any]) -> "Entry":
        return cls(
            entry_id=d["entry_id"],
            term=int(d["term"]),
            timestamp_ns=int(d["timestamp_ns"]),
            payload=_decode_payload(d["payload"]),
        )
