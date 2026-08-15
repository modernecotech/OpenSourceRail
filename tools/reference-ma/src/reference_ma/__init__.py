"""Python reference interpreter for osr-interlocking.

Independent implementation of the Movement Authority state machine
that the Rust crate produces. Intended for differential testing: a
divergence between this and `osr_interlocking::compute_self_ma`
indicates a bug in at least one of the two.

Public surface is narrow on purpose — the only thing a caller should
ever need is `compute_self_ma` and the types it consumes.
"""

from .types import (
    Direction,
    TrackRef,
    Position,
    BrakingCurve,
    ConsistDescriptor,
    Station,
    Section,
    Line,
    Network,
)
from .log import (
    Entry,
    EntryPayload,
    TrainRegistration,
    TrainPositionReport,
    TrainDeparture,
    SwitchObservation,
    SwitchCommand,
    RouteRequest,
    RouteGrant,
    RouteRelease,
    SpeedRestriction,
    SectionIntrusion,
    MaintenanceOverride,
    Heartbeat,
    FormatVersion,
    SwitchPosition,
    Confidence,
    PositionSource,
    HealthStatus,
    RestrictionReason,
    IntrusionState,
)
from .state import DerivedState, derive_state
from .ma import (
    MovementAuthority,
    compute_self_ma,
    compute_self_ma_from_state,
    section_available_to,
    MAX_MA_DISTANCE_MM,
    MA_VALIDITY_WINDOW_NS,
)
from .topology import forward_chain, footprint_from, far_end_of, locate_section

__all__ = [
    "Direction",
    "TrackRef",
    "Position",
    "BrakingCurve",
    "ConsistDescriptor",
    "Station",
    "Section",
    "Line",
    "Network",
    "Entry",
    "EntryPayload",
    "TrainRegistration",
    "TrainPositionReport",
    "TrainDeparture",
    "SwitchObservation",
    "SwitchCommand",
    "RouteRequest",
    "RouteGrant",
    "RouteRelease",
    "SpeedRestriction",
    "SectionIntrusion",
    "MaintenanceOverride",
    "Heartbeat",
    "FormatVersion",
    "SwitchPosition",
    "Confidence",
    "PositionSource",
    "HealthStatus",
    "RestrictionReason",
    "IntrusionState",
    "DerivedState",
    "derive_state",
    "MovementAuthority",
    "compute_self_ma",
    "compute_self_ma_from_state",
    "section_available_to",
    "MAX_MA_DISTANCE_MM",
    "MA_VALIDITY_WINDOW_NS",
    "forward_chain",
    "footprint_from",
    "far_end_of",
    "locate_section",
]
