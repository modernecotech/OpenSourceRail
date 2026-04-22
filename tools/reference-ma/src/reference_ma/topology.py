"""Topology traversal helpers — mirror of osr-interlocking::topology.

Return-for-return identical to the Rust implementation so that
`forward_chain` / `footprint_from` / `far_end_of` / `locate_section`
never diverge on the same inputs.
"""

from __future__ import annotations

from enum import Enum
from typing import List, Optional, Tuple

from .types import Direction, Network, SectionId, TrackRef


class SectionArray(str, Enum):
    Forward = "Forward"
    Reverse = "Reverse"


def locate_section(
    network: Network, section: SectionId
) -> Optional[Tuple[int, int, SectionArray]]:
    """Return `(line_index, section_index, which_array)` for `section`,
    or `None` if the section isn't on any line."""
    for li, line in enumerate(network.lines):
        try:
            si = line.forward_sections.index(section)
            return li, si, SectionArray.Forward
        except ValueError:
            pass
        try:
            si = line.reverse_sections.index(section)
            return li, si, SectionArray.Reverse
        except ValueError:
            pass
    return None


def _array_of(line, which: SectionArray) -> List[SectionId]:
    return line.forward_sections if which == SectionArray.Forward else line.reverse_sections


def _direction_matches(direction: Direction, which: SectionArray) -> bool:
    return (direction == Direction.Forward and which == SectionArray.Forward) or (
        direction == Direction.Reverse and which == SectionArray.Reverse
    )


def forward_chain(
    network: Network, start: TrackRef, max_distance_mm: int
) -> List[SectionId]:
    """Enumerate sections the train traverses travelling forward from
    `start`, up to `max_distance_mm` of additional track. The starting
    section is always the first element. Empty chain on direction-vs-
    array mismatch (fail-restrictive)."""
    located = locate_section(network, start.section)
    if located is None:
        return []
    line_idx, start_idx, which = located
    if not _direction_matches(start.direction, which):
        return []

    line = network.lines[line_idx]
    array = _array_of(line, which)
    n = len(array)
    if n == 0:
        return []

    first_section = network.section(array[start_idx])
    result: List[SectionId] = [first_section.id]
    consumed_mm = first_section.length_mm - start.offset_mm
    if consumed_mm < 0:
        consumed_mm = 0

    idx = start_idx
    while True:
        next_idx = idx + 1
        if next_idx >= n:
            if line.is_ring:
                next_idx = 0
            else:
                break
        if next_idx == start_idx:
            break
        sec = network.section(array[next_idx])
        would_consume = consumed_mm + sec.length_mm
        if would_consume > max_distance_mm:
            break
        result.append(sec.id)
        consumed_mm = would_consume
        idx = next_idx

    return result


def far_end_of(network: Network, section: SectionId, direction: Direction) -> TrackRef:
    sec = network.section(section)
    return TrackRef(section=section, offset_mm=sec.length_mm, direction=direction)


def footprint_from(
    network: Network, head: TrackRef, consist_length_mm: int
) -> List[SectionId]:
    """Sections the train occupies given its head position and consist
    length — head's section plus any preceding section the tail reaches
    into."""
    located = locate_section(network, head.section)
    if located is None:
        return []
    line_idx, head_idx, which = located
    if not _direction_matches(head.direction, which):
        return [head.section]

    line = network.lines[line_idx]
    array = _array_of(line, which)
    n = len(array)

    result: List[SectionId] = [head.section]
    remaining_tail_mm = consist_length_mm - head.offset_mm
    if remaining_tail_mm <= 0:
        return result

    tail_left = remaining_tail_mm
    idx = head_idx
    while tail_left > 0:
        if idx == 0:
            if line.is_ring:
                prev_idx = n - 1
            else:
                break
        else:
            prev_idx = idx - 1
        if prev_idx == head_idx:
            break
        idx = prev_idx
        sec = network.section(array[idx])
        result.append(sec.id)
        tail_left -= sec.length_mm

    return result
