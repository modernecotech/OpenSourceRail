//! Topology traversal helpers.
//!
//! The MA computer needs to enumerate sections in the direction of travel
//! from a given start position. The `Network` type in osr-core describes
//! lines as ordered `Vec<SectionId>`; these helpers turn that description
//! into "walk forward from here" queries.
//!
//! All lookups are O(n) in section count — acceptable for a region of
//! <100 sections. The MA computer is called at most once per train per MA
//! refresh period (~500 ms), and total sections across a region are in the
//! low hundreds, so a full linear scan is well within budget.

use osr_core::{Direction, Line, Network, SectionId, TrackRef};

/// Locate a section within the network's lines.
///
/// Returns `(line_index, section_index_in_array, which_array)` where
/// `which_array` indicates whether the section is in the line's
/// `forward_sections` or `reverse_sections`. Returns `None` if the section
/// is not on any line.
pub fn locate_section(
    network: &Network,
    section: SectionId,
) -> Option<(usize, usize, SectionArray)> {
    for (li, line) in network.lines.iter().enumerate() {
        if let Some(si) = line.forward_sections.iter().position(|s| *s == section) {
            return Some((li, si, SectionArray::Forward));
        }
        if let Some(si) = line.reverse_sections.iter().position(|s| *s == section) {
            return Some((li, si, SectionArray::Reverse));
        }
    }
    None
}

#[derive(Copy, Clone, Debug, PartialEq, Eq)]
pub enum SectionArray {
    Forward,
    Reverse,
}

impl SectionArray {
    fn array_of<'a>(self, line: &'a Line) -> &'a [SectionId] {
        match self {
            SectionArray::Forward => &line.forward_sections,
            SectionArray::Reverse => &line.reverse_sections,
        }
    }
}

/// Enumerate section IDs that the train will traverse travelling forward
/// from `start`, going no further than `max_distance_mm` of additional
/// track. The starting section is always included as the first element.
///
/// `start.direction` matters: `Forward` means we follow the section's own
/// orientation (and thus the array it lives in); `Reverse` means we would
/// walk the _opposite_ direction array, but since the section IDs differ
/// between the forward and reverse parallel tracks in our model, a reverse
/// direction should be a section from the corresponding reverse array in
/// the first place. In other words: the natural model is that
/// `start.direction == Forward` when `start.section` is in
/// `line.forward_sections`, and symmetrically for Reverse. We validate that
/// and return an empty chain otherwise, which is the fail-restrictive
/// response.
pub fn forward_chain(network: &Network, start: TrackRef, max_distance_mm: i64) -> Vec<SectionId> {
    let Some((line_idx, start_idx, which)) = locate_section(network, start.section) else {
        return Vec::new();
    };

    // The train's direction must match the array orientation for this to
    // be a sensible forward chain. Anything else is a data inconsistency
    // and we respond fail-restrictively.
    let direction_matches = match (start.direction, which) {
        (Direction::Forward, SectionArray::Forward) => true,
        (Direction::Reverse, SectionArray::Reverse) => true,
        _ => false,
    };
    if !direction_matches {
        return Vec::new();
    }

    let line = &network.lines[line_idx];
    let array = which.array_of(line);
    let n = array.len();
    if n == 0 {
        return Vec::new();
    }

    // The first section: we only count the remaining distance within it
    // (section length minus train's current offset).
    let first_section = network.section(array[start_idx]);
    let mut result = vec![first_section.id];
    let mut consumed_mm: i64 = (first_section.length_mm as i64).saturating_sub(start.offset_mm);
    if consumed_mm < 0 {
        consumed_mm = 0;
    }

    let mut idx = start_idx;
    loop {
        let next_idx = idx + 1;
        let next_idx = if next_idx >= n {
            if line.is_ring {
                0
            } else {
                break; // linear line: terminated at the end
            }
        } else {
            next_idx
        };
        // Avoid infinite loop on rings: stop if we've come back to where we started.
        if next_idx == start_idx {
            break;
        }
        let sec = network.section(array[next_idx]);
        let would_consume = consumed_mm.saturating_add(sec.length_mm as i64);
        if would_consume > max_distance_mm {
            // Adding this section would exceed the MA budget. Stop at the
            // previous section's boundary — this is the fail-restrictive
            // choice and produces MAs that always end at station boundaries.
            break;
        }
        result.push(sec.id);
        consumed_mm = would_consume;
        idx = next_idx;
    }

    result
}

/// Compute the TrackRef at the far end of a section in the given travel
/// direction.
pub fn far_end_of(network: &Network, section: SectionId, direction: Direction) -> TrackRef {
    let sec = network.section(section);
    TrackRef {
        section,
        offset_mm: sec.length_mm as i64,
        direction,
    }
}

/// Compute the sections the train currently occupies, given the head
/// position and total consist length. Returns the head's section and any
/// preceding sections that the consist's tail reaches into.
///
/// Simplification (v1): walks backward through the line's section array,
/// matching the head's direction. Works for both linear and ring lines.
/// Formal verification in M3 will bound this to at most 2 sections for a
/// 51 m reference consist on >= 200 m sections.
pub fn footprint_from(network: &Network, head: TrackRef, consist_length_mm: u32) -> Vec<SectionId> {
    let Some((line_idx, head_idx, which)) = locate_section(network, head.section) else {
        return Vec::new();
    };

    // Sanity: if the head's direction doesn't match the array orientation,
    // we can't walk backward sensibly. Fail-restrictive: return just the
    // head section, so the MA computer treats it as the full footprint.
    let direction_matches = match (head.direction, which) {
        (Direction::Forward, SectionArray::Forward) => true,
        (Direction::Reverse, SectionArray::Reverse) => true,
        _ => false,
    };
    if !direction_matches {
        return vec![head.section];
    }

    let line = &network.lines[line_idx];
    let array = which.array_of(line);
    let n = array.len();

    let mut result = vec![head.section];
    // How much tail length remains after covering the head's section interior?
    let remaining_tail_mm: i64 = (consist_length_mm as i64).saturating_sub(head.offset_mm);
    if remaining_tail_mm <= 0 {
        return result; // tail fits within the head's section
    }

    let mut tail_left = remaining_tail_mm;
    let mut idx = head_idx;
    while tail_left > 0 {
        let prev_idx = if idx == 0 {
            if line.is_ring {
                n - 1
            } else {
                break; // reached the head of the line
            }
        } else {
            idx - 1
        };
        // Loop guard for rings
        if prev_idx == head_idx {
            break;
        }
        idx = prev_idx;
        let sec = network.section(array[idx]);
        result.push(sec.id);
        tail_left = tail_left.saturating_sub(sec.length_mm as i64);
    }

    result
}

#[cfg(test)]
mod tests {
    use super::*;
    use osr_core::{Line, Network, Section, SectionId, Station, StationId, TrackRef};

    fn simple_linear_network() -> Network {
        let mut net = Network::default();
        for i in 1..=4 {
            net.stations.insert(
                StationId::new(i),
                Station {
                    id: StationId::new(i),
                    name: format!("S{i}"),
                    charging_power_kw: 0,
                    dwell_seconds: 0,
                    is_terminal: i == 1 || i == 4,
                    is_depot: false,
                },
            );
        }
        let mut fwd = vec![];
        let mut rev = vec![];
        for i in 0..3 {
            let f = SectionId::new(1000 + i);
            let r = SectionId::new(2000 + i);
            net.sections.insert(
                f,
                Section {
                    id: f,
                    from_station: StationId::new((i as u64) + 1),
                    to_station: StationId::new((i as u64) + 2),
                    length_mm: 1_000_000, // 1 km
                    max_speed_mps: 22.0,
                },
            );
            net.sections.insert(
                r,
                Section {
                    id: r,
                    from_station: StationId::new((i as u64) + 2),
                    to_station: StationId::new((i as u64) + 1),
                    length_mm: 1_000_000,
                    max_speed_mps: 22.0,
                },
            );
            fwd.push(f);
            rev.push(r);
        }
        net.lines.push(Line {
            name: "L".into(),
            stations: (1..=4).map(StationId::new).collect(),
            forward_sections: fwd,
            reverse_sections: rev,
            is_ring: false,
        });
        net
    }

    fn simple_ring_network() -> Network {
        let mut net = Network::default();
        for i in 1..=4 {
            net.stations.insert(
                StationId::new(i),
                Station {
                    id: StationId::new(i),
                    name: format!("R{i}"),
                    charging_power_kw: 0,
                    dwell_seconds: 0,
                    is_terminal: false,
                    is_depot: false,
                },
            );
        }
        let mut fwd = vec![];
        let mut rev = vec![];
        for i in 0..4 {
            let f = SectionId::new(3000 + i);
            let r = SectionId::new(4000 + i);
            let from_idx = (i as u64) + 1;
            let to_idx = ((i as u64) % 4) + 2;
            let to_idx = if to_idx > 4 { 1 } else { to_idx };
            net.sections.insert(
                f,
                Section {
                    id: f,
                    from_station: StationId::new(from_idx),
                    to_station: StationId::new(to_idx),
                    length_mm: 1_000_000,
                    max_speed_mps: 22.0,
                },
            );
            net.sections.insert(
                r,
                Section {
                    id: r,
                    from_station: StationId::new(to_idx),
                    to_station: StationId::new(from_idx),
                    length_mm: 1_000_000,
                    max_speed_mps: 22.0,
                },
            );
            fwd.push(f);
            rev.push(r);
        }
        net.lines.push(Line {
            name: "Ring".into(),
            stations: (1..=4).map(StationId::new).collect(),
            forward_sections: fwd,
            reverse_sections: rev,
            is_ring: true,
        });
        net
    }

    #[test]
    fn forward_chain_linear_basic() {
        let net = simple_linear_network();
        // Start at mid of first section, Forward direction, walking up to 1500 m
        let start = TrackRef {
            section: SectionId::new(1000),
            offset_mm: 500_000,
            direction: Direction::Forward,
        };
        let chain = forward_chain(&net, start, 1_500_000);
        // Should include first section + 1 more (500 m remaining + 1 km = 1.5 km)
        assert_eq!(chain, vec![SectionId::new(1000), SectionId::new(1001)]);
    }

    #[test]
    fn forward_chain_linear_terminates_at_end() {
        let net = simple_linear_network();
        // Start at mid of last forward section (1002), walking 5 km forward.
        let start = TrackRef {
            section: SectionId::new(1002),
            offset_mm: 0,
            direction: Direction::Forward,
        };
        let chain = forward_chain(&net, start, 5_000_000);
        // Only one section available before hitting terminal.
        assert_eq!(chain, vec![SectionId::new(1002)]);
    }

    #[test]
    fn forward_chain_ring_wraps() {
        let net = simple_ring_network();
        let start = TrackRef {
            section: SectionId::new(3003), // last fwd section (station 4 -> station 1)
            offset_mm: 0,
            direction: Direction::Forward,
        };
        let chain = forward_chain(&net, start, 2_500_000);
        // Budget 2.5 km; section 3003 covers 1 km from offset 0; next section
        // 3000 wraps and fits (1 km + 1 km = 2 km); next would exceed.
        assert_eq!(chain, vec![SectionId::new(3003), SectionId::new(3000)]);
    }

    #[test]
    fn forward_chain_stops_at_budget_section_boundary() {
        let net = simple_linear_network();
        // Head at 100m into section 1000. Budget 2km.
        // Remaining in 1000: 900m. Section 1001: 1km (900+1000=1900 ≤ 2000). Include.
        // Section 1002: would add 1km to 1900 = 2900 > 2000. Exclude.
        let start = TrackRef {
            section: SectionId::new(1000),
            offset_mm: 100_000,
            direction: Direction::Forward,
        };
        let chain = forward_chain(&net, start, 2_000_000);
        assert_eq!(chain, vec![SectionId::new(1000), SectionId::new(1001)]);
    }

    #[test]
    fn footprint_single_section() {
        let net = simple_linear_network();
        // Reference consist length 51 m; head at offset 100 m on section 1001
        // → tail also on 1001.
        let head = TrackRef {
            section: SectionId::new(1001),
            offset_mm: 100_000,
            direction: Direction::Forward,
        };
        let footprint = footprint_from(&net, head, 51_000);
        assert_eq!(footprint, vec![SectionId::new(1001)]);
    }

    #[test]
    fn footprint_crosses_section_boundary() {
        let net = simple_linear_network();
        // Head at offset 20 m on section 1001; reference consist length 51 m
        // → tail on 1000.
        let head = TrackRef {
            section: SectionId::new(1001),
            offset_mm: 20_000,
            direction: Direction::Forward,
        };
        let footprint = footprint_from(&net, head, 51_000);
        assert_eq!(footprint, vec![SectionId::new(1001), SectionId::new(1000)]);
    }
}
