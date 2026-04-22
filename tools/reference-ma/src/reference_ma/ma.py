"""Movement-Authority computer — mirror of osr-interlocking::ma.

`compute_self_ma(train_id, entries, network, now_ns)` is a pure
function of its inputs. Byte-identical output to the Rust
`osr_interlocking::compute_self_ma` on the same inputs is the
correctness property (P1 determinism plus P2..P5 structural
equivalence).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Set

from .log import Entry, SpeedRestriction
from .state import DerivedState, derive_state
from .topology import far_end_of, footprint_from, forward_chain
from .types import (
    Direction,
    EntryId,
    Network,
    SectionId,
    TrackRef,
    TrainId,
)

# Constants — must match osr-interlocking::ma exactly.
MAX_MA_DISTANCE_MM: int = 2_000_000
MA_VALIDITY_WINDOW_NS: int = 3_000_000_000


@dataclass
class MovementAuthority:
    train_id: TrainId
    end: TrackRef
    applicable_restrictions: List[SpeedRestriction] = field(default_factory=list)
    valid_until_ns: int = 0
    derived_from_entry_id: Optional[EntryId] = None
    has_known_position: bool = False


def section_available_to(
    train_id: TrainId, section: SectionId, state: DerivedState
) -> bool:
    """P4's concrete enforcement point — a section is available iff no
    other train occupies it, no route grant locks it to another train,
    and no maintenance override covers it."""
    occupant = state.section_occupancy.get(section)
    if occupant is not None and occupant != train_id:
        return False

    for grant in state.active_routes.values():
        if section in grant.locked_sections and grant.train_id != train_id:
            return False

    for over in state.maintenance_overrides:
        if over.section == section:
            return False

    return True


def _saturating_add_u64(a: int, b: int) -> int:
    """Mirror of Rust `u64::saturating_add`."""
    total = a + b
    u64_max = (1 << 64) - 1
    return min(total, u64_max)


def _fail_restrictive(
    train_id: TrainId,
    head_if_any: Optional[TrackRef],
    valid_until_ns: int,
    derived_from_entry_id: Optional[EntryId],
) -> MovementAuthority:
    end = head_if_any or TrackRef(section=0, offset_mm=0, direction=Direction.Forward)
    return MovementAuthority(
        train_id=train_id,
        end=end,
        applicable_restrictions=[],
        valid_until_ns=valid_until_ns,
        derived_from_entry_id=derived_from_entry_id,
        has_known_position=head_if_any is not None,
    )


def _collect_applicable_restrictions(
    state: DerivedState,
    from_ref: TrackRef,
    to_ref: TrackRef,
    now_ns: int,
) -> List[SpeedRestriction]:
    out: List[SpeedRestriction] = []
    for sr in state.speed_restrictions:
        if sr.effective_from_ns > now_ns:
            continue
        if sr.effective_until_ns is not None and now_ns >= sr.effective_until_ns:
            continue
        # v1 heuristic (matches Rust): in-scope iff on either endpoint's section.
        if sr.section == from_ref.section or sr.section == to_ref.section:
            out.append(sr)
    return out


def compute_self_ma_from_state(
    train_id: TrainId,
    state: DerivedState,
    network: Network,
    now_ns: int,
    derived_from_entry_id: Optional[EntryId] = None,
) -> MovementAuthority:
    valid_until_ns = _saturating_add_u64(now_ns, MA_VALIDITY_WINDOW_NS)

    awareness = state.trains.get(train_id)
    if awareness is None:
        return _fail_restrictive(train_id, None, valid_until_ns, derived_from_entry_id)

    head = awareness.last_head_position
    if head is None:
        return _fail_restrictive(train_id, None, valid_until_ns, derived_from_entry_id)

    consist_length_mm = awareness.consist.length_mm
    footprint_sections: Set[SectionId] = set(
        footprint_from(network, head.track_ref, consist_length_mm)
    )

    chain = forward_chain(network, head.track_ref, MAX_MA_DISTANCE_MM)

    ma_end = head.track_ref
    reached_far_end_of_head = False
    for section_id in chain:
        if section_id in footprint_sections:
            ma_end = far_end_of(network, section_id, head.track_ref.direction)
            reached_far_end_of_head = True
            continue
        if not section_available_to(train_id, section_id, state):
            break
        ma_end = far_end_of(network, section_id, head.track_ref.direction)

    restrictions = _collect_applicable_restrictions(
        state, head.track_ref, ma_end, now_ns
    )

    return MovementAuthority(
        train_id=train_id,
        end=ma_end,
        applicable_restrictions=restrictions,
        valid_until_ns=valid_until_ns,
        derived_from_entry_id=derived_from_entry_id,
        has_known_position=True,
    )


def compute_self_ma(
    train_id: TrainId,
    log_prefix: List[Entry],
    network: Network,
    now_ns: int,
) -> MovementAuthority:
    state = derive_state(log_prefix)
    derived_from = log_prefix[-1].entry_id if log_prefix else None
    return compute_self_ma_from_state(train_id, state, network, now_ns, derived_from)
