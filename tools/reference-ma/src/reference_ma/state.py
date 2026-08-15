"""Derived-state fold — mirror of osr-interlocking::state.

`derive_state(entries)` is the pure fold over a committed log prefix.
Byte-identical to the Rust version on the same input is the correctness
property we care about; divergence = bug in one of the two.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .log import (
    Confidence,
    Entry,
    FormatVersion,
    Heartbeat,
    HealthStatus,
    MaintenanceOverride,
    Position,
    RouteGrant,
    RouteRelease,
    SectionIntrusion,
    SpeedRestriction,
    SwitchCommand,
    SwitchObservation,
    SwitchPosition,
    TrainDeparture,
    TrainPositionReport,
    TrainRegistration,
)
from .types import (
    ConsistDescriptor,
    EntityId,
    RouteId,
    SectionId,
    SwitchId,
    TrainId,
)


@dataclass
class SwitchState:
    position: SwitchPosition
    confidence: Confidence
    observed_at_ns: int


@dataclass
class TrainAwareness:
    consist: ConsistDescriptor
    last_head_position: Optional[Position]
    last_tail_position: Optional[Position]
    last_position_onboard_ns: int
    last_position_log_ns: int
    speed_mmps: int
    speed_uncertainty_mmps: int
    pack_soc_ppt: int

    @staticmethod
    def from_registration(reg: TrainRegistration, log_time_ns: int) -> "TrainAwareness":
        return TrainAwareness(
            consist=reg.consist,
            last_head_position=reg.initial_position,
            last_tail_position=None,
            last_position_onboard_ns=0,
            last_position_log_ns=log_time_ns,
            speed_mmps=0,
            speed_uncertainty_mmps=0,
            pack_soc_ppt=1000,
        )


@dataclass
class EntityLiveness:
    health: HealthStatus
    monotonic_seq: int
    last_entry_time_ns: int


@dataclass
class DerivedState:
    section_occupancy: Dict[SectionId, TrainId] = field(default_factory=dict)
    switches: Dict[SwitchId, SwitchState] = field(default_factory=dict)
    trains: Dict[TrainId, TrainAwareness] = field(default_factory=dict)
    active_routes: Dict[RouteId, RouteGrant] = field(default_factory=dict)
    speed_restrictions: List[SpeedRestriction] = field(default_factory=list)
    section_intrusions: Dict[SectionId, SectionIntrusion] = field(default_factory=dict)
    maintenance_overrides: List[MaintenanceOverride] = field(default_factory=list)
    entity_liveness: Dict[EntityId, EntityLiveness] = field(default_factory=dict)
    format_version: Optional[int] = None
    last_entry_time_ns: int = 0

    def apply(self, entry: Entry) -> None:
        _apply_entry(self, entry)


def derive_state(entries: List[Entry]) -> DerivedState:
    s = DerivedState()
    for e in entries:
        _apply_entry(s, e)
    return s


# ---------------------------------------------------------------------------
# apply helpers
# ---------------------------------------------------------------------------


def _apply_entry(s: DerivedState, entry: Entry) -> None:
    s.last_entry_time_ns = entry.timestamp_ns
    p = entry.payload

    if isinstance(p, TrainPositionReport):
        _apply_position(s, p, entry.timestamp_ns)
    elif isinstance(p, SwitchObservation):
        s.switches[p.switch_id] = SwitchState(
            position=p.observed_position,
            confidence=p.confidence,
            observed_at_ns=p.observed_at_ns,
        )
    elif isinstance(p, TrainRegistration):
        s.trains[p.train_id] = TrainAwareness.from_registration(p, entry.timestamp_ns)
    elif isinstance(p, TrainDeparture):
        _apply_departure(s, p)
    elif isinstance(p, RouteGrant):
        s.active_routes[p.route_id] = p
    elif isinstance(p, RouteRelease):
        s.active_routes.pop(p.route_id, None)
    elif isinstance(p, SpeedRestriction):
        s.speed_restrictions.append(p)
    elif isinstance(p, SectionIntrusion):
        s.section_intrusions[p.section] = p
    elif isinstance(p, MaintenanceOverride):
        s.maintenance_overrides.append(p)
    elif isinstance(p, Heartbeat):
        _apply_heartbeat(s, p, entry.timestamp_ns)
    elif isinstance(p, FormatVersion):
        s.format_version = p.current
    elif isinstance(p, (SwitchCommand,)):
        # Advisory — no state mutation until a subsequent Observation.
        pass
    else:
        # RouteRequest etc.: advisory. Intentionally unhandled.
        pass


def _apply_position(s: DerivedState, r: TrainPositionReport, log_time_ns: int) -> None:
    awareness = s.trains.get(r.train_id)
    if awareness is None:
        awareness = TrainAwareness(
            consist=ConsistDescriptor.reference_3car(),
            last_head_position=None,
            last_tail_position=None,
            last_position_onboard_ns=0,
            last_position_log_ns=0,
            speed_mmps=0,
            speed_uncertainty_mmps=0,
            pack_soc_ppt=1000,
        )
        s.trains[r.train_id] = awareness

    awareness.last_head_position = r.head_position
    awareness.last_tail_position = r.tail_position
    awareness.last_position_onboard_ns = r.onboard_time_ns
    awareness.last_position_log_ns = log_time_ns
    awareness.speed_mmps = r.speed_mmps
    awareness.speed_uncertainty_mmps = r.speed_uncertainty_mmps
    awareness.pack_soc_ppt = min(r.pack_soc_ppt, 1000)

    _clear_occupancy_by(s, r.train_id)
    s.section_occupancy[r.head_position.track_ref.section] = r.train_id
    if r.tail_position.track_ref.section != r.head_position.track_ref.section:
        s.section_occupancy[r.tail_position.track_ref.section] = r.train_id


def _apply_departure(s: DerivedState, dep: TrainDeparture) -> None:
    s.trains.pop(dep.train_id, None)
    _clear_occupancy_by(s, dep.train_id)
    s.active_routes = {
        rid: g for rid, g in s.active_routes.items() if g.train_id != dep.train_id
    }


def _clear_occupancy_by(s: DerivedState, train: TrainId) -> None:
    s.section_occupancy = {
        sec: tid for sec, tid in s.section_occupancy.items() if tid != train
    }


def _apply_heartbeat(s: DerivedState, hb: Heartbeat, log_time_ns: int) -> None:
    entry = s.entity_liveness.get(hb.from_entity)
    if entry is None:
        s.entity_liveness[hb.from_entity] = EntityLiveness(
            health=hb.health,
            monotonic_seq=hb.monotonic_seq,
            last_entry_time_ns=log_time_ns,
        )
        return
    if hb.monotonic_seq > entry.monotonic_seq:
        entry.health = hb.health
        entry.monotonic_seq = hb.monotonic_seq
        entry.last_entry_time_ns = log_time_ns
