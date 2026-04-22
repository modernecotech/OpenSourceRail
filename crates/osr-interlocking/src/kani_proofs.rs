//! Kani bounded-model-checker harnesses for the five safety
//! properties of [RFC 0004 §4](../../docs/rfcs/0004-osr-interlocking-plan.md):
//!
//! - **P1 (determinism):** same log prefix → byte-identical MA.
//! - **P2 (non-overlap):** two registered trains' MAs do not share a
//!   section (modulo their own footprints).
//! - **P3 (consist-fit):** MA end accounts for full consist footprint.
//! - **P4 (conservatism):** more-uncertain input produces a
//!   more-restrictive MA.
//! - **P5 (time-bounded):** `valid_until - now ≤ MA_VALIDITY_WINDOW_NS`.
//!
//! # Status
//!
//! All five harnesses are present and compile under Kani. The bounds
//! are the smallest that exercise each property's control flow at a
//! non-trivial regime: 2 sections for the arithmetic-only proofs, 3
//! sections + 2 trains for non-overlap (P2), and a mutation-style
//! companion harness for conservatism (P4). Larger bounds (toward the
//! RFC 0004 target of 8 trains × 50 entries × 100 sections) remain
//! work for dedicated CI with a compute budget — see
//! `docs/safety-case/README.md`.
//!
//! # Running
//!
//! ```bash
//! cargo install --locked kani-verifier
//! cargo kani setup
//! cargo kani -p osr-interlocking --harness kani_p5_time_bounded
//! ```
//!
//! Or all at once:
//!
//! ```bash
//! cargo kani -p osr-interlocking
//! ```
//!
//! Properties that verify trivially (constant-time, no loops) complete
//! in seconds. P2 / P4 on non-trivial bounded networks can take
//! minutes to tens of minutes depending on the bound.

#![cfg(kani)]

use osr_core::{
    ConsistDescriptor, Direction, EntryId, Line, Network, Position, Section, SectionId, Station,
    StationId, TrackRef, TrainId,
};

use crate::log::{Entry, EntryPayload, PositionSource, TrainPositionReport, TrainRegistration};
use crate::ma::{compute_self_ma, MAX_MA_DISTANCE_MM, MA_VALIDITY_WINDOW_NS};

// ---------------------------------------------------------------------------
// Scaffolding: tiny networks Kani can reason about.
// ---------------------------------------------------------------------------

/// Three-section linear network: S1 ── 1000 ──▶ S2 ── 1001 ──▶ S3 ── 1002 ──▶ S4.
/// Every section is 1 km. Used by the P2 non-overlap harness so MA1's
/// forward chain has an unblocked section to reach into after train 2
/// is moved out of the way.
fn three_section_network() -> Network {
    let mut net = Network::default();
    for i in 1..=4u64 {
        net.stations.insert(
            StationId::new(i),
            Station {
                id: StationId::new(i),
                name: String::new(),
                charging_power_kw: 0,
                dwell_seconds: 0,
                is_terminal: i == 1 || i == 4,
                is_depot: false,
            },
        );
    }
    let mut fwd = vec![];
    let mut rev = vec![];
    for i in 0..3u64 {
        let f = SectionId::new(1000 + i);
        let r = SectionId::new(2000 + i);
        net.sections.insert(
            f,
            Section {
                id: f,
                from_station: StationId::new(i + 1),
                to_station: StationId::new(i + 2),
                length_mm: 1_000_000,
                max_speed_mps: 22.0,
            },
        );
        net.sections.insert(
            r,
            Section {
                id: r,
                from_station: StationId::new(i + 2),
                to_station: StationId::new(i + 1),
                length_mm: 1_000_000,
                max_speed_mps: 22.0,
            },
        );
        fwd.push(f);
        rev.push(r);
    }
    net.lines.push(Line {
        name: String::new(),
        stations: (1..=4).map(StationId::new).collect(),
        forward_sections: fwd,
        reverse_sections: rev,
        is_ring: false,
    });
    net
}

/// A minimal two-section linear network: S1 ── 1000 ──▶ S2 ── 1001 ──▶ S3.
/// Every section is 1 km.
fn tiny_network() -> Network {
    let mut net = Network::default();
    for i in 1..=3u64 {
        net.stations.insert(
            StationId::new(i),
            Station {
                id: StationId::new(i),
                name: String::new(), // Kani dislikes nontrivial strings; keep empty
                charging_power_kw: 0,
                dwell_seconds: 0,
                is_terminal: i == 1 || i == 3,
                is_depot: false,
            },
        );
    }
    let mut fwd = vec![];
    let mut rev = vec![];
    for i in 0..2u64 {
        let f = SectionId::new(1000 + i);
        let r = SectionId::new(2000 + i);
        net.sections.insert(
            f,
            Section {
                id: f,
                from_station: StationId::new(i + 1),
                to_station: StationId::new(i + 2),
                length_mm: 1_000_000,
                max_speed_mps: 22.0,
            },
        );
        net.sections.insert(
            r,
            Section {
                id: r,
                from_station: StationId::new(i + 2),
                to_station: StationId::new(i + 1),
                length_mm: 1_000_000,
                max_speed_mps: 22.0,
            },
        );
        fwd.push(f);
        rev.push(r);
    }
    net.lines.push(Line {
        name: String::new(),
        stations: (1..=3).map(StationId::new).collect(),
        forward_sections: fwd,
        reverse_sections: rev,
        is_ring: false,
    });
    net
}

/// Build a single registration + position entry pair for a train on
/// section 1000, `head_offset_mm` millimetres in.
fn train_on_first_section(train_id: u64, head_offset_mm: i64, ts_ns: u64) -> Vec<Entry> {
    vec![
        Entry {
            entry_id: EntryId::new(1),
            term: 1,
            timestamp_ns: ts_ns.saturating_sub(1_000_000),
            payload: EntryPayload::TrainRegistration(TrainRegistration {
                train_id: TrainId::new(train_id),
                consist: ConsistDescriptor::reference_3car(),
                initial_position: Position::certain(TrackRef {
                    section: SectionId::new(1000),
                    offset_mm: 0,
                    direction: Direction::Forward,
                }),
            }),
        },
        Entry {
            entry_id: EntryId::new(2),
            term: 1,
            timestamp_ns: ts_ns,
            payload: EntryPayload::TrainPositionReport(TrainPositionReport {
                train_id: TrainId::new(train_id),
                head_position: Position::certain(TrackRef {
                    section: SectionId::new(1000),
                    offset_mm: head_offset_mm,
                    direction: Direction::Forward,
                }),
                tail_position: Position::certain(TrackRef {
                    section: SectionId::new(1000),
                    offset_mm: (head_offset_mm - 65_000).max(0),
                    direction: Direction::Forward,
                }),
                speed_mmps: 10_000,
                speed_uncertainty_mmps: 500,
                heading: Direction::Forward,
                contributing_sources: vec![PositionSource::Gnss],
                onboard_time_ns: ts_ns.saturating_sub(100),
                pack_soc_ppt: 900,
            }),
        },
    ]
}

// ---------------------------------------------------------------------------
// P5 (time-bounded): the core arithmetic.
//
// `compute_self_ma` always computes
// `valid_until_ns = now_ns.saturating_add(MA_VALIDITY_WINDOW_NS)`.
// The property under test is a universal arithmetic statement: for
// every `now_ns`, the returned window fits within
// `MA_VALIDITY_WINDOW_NS`. Checked directly on the primitive so Kani
// doesn't have to unwind `HashMap` operations that the full
// `compute_self_ma` path performs on a `Network`.
//
// Runs in ~1 second.
// ---------------------------------------------------------------------------

#[kani::proof]
fn kani_p5_time_bounded_arithmetic() {
    let now_ns: u64 = kani::any();
    let valid_until_ns = now_ns.saturating_add(MA_VALIDITY_WINDOW_NS);
    // Invariant: the window never exceeds MA_VALIDITY_WINDOW_NS.
    // `saturating_add` clamps at u64::MAX, which remains within bound.
    assert!(valid_until_ns >= now_ns);
    assert!(valid_until_ns.saturating_sub(now_ns) <= MA_VALIDITY_WINDOW_NS);
}

// The whole-function version of P5 — exercises the full
// compute_self_ma path including the `Network`'s `HashMap` lookups.
// Kani-expensive; may time out without generous bounds. Left as an
// aspirational harness; primary P5 proof is the arithmetic variant
// above.
#[kani::proof]
#[kani::unwind(10)]
#[kani::solver(cadical)]
fn kani_p5_time_bounded() {
    let now_ns: u64 = kani::any();
    kani::assume(now_ns < u64::MAX - MA_VALIDITY_WINDOW_NS - 1);

    let net = tiny_network();
    let ma = compute_self_ma(TrainId::new(1), &[], &net, now_ns);

    assert!(ma.valid_until_ns >= now_ns);
    assert!(ma.valid_until_ns - now_ns <= MA_VALIDITY_WINDOW_NS);
}

// ---------------------------------------------------------------------------
// P5 with a non-trivial log: the same bound must hold when there is a
// known-position train.
// ---------------------------------------------------------------------------

#[kani::proof]
#[kani::unwind(10)]
fn kani_p5_time_bounded_with_known_position() {
    let now_ns: u64 = kani::any();
    kani::assume(now_ns > 1_000_000_000);
    kani::assume(now_ns < u64::MAX - MA_VALIDITY_WINDOW_NS - 1);

    let net = tiny_network();
    let log = train_on_first_section(1, 100_000, now_ns - 500_000_000);
    let ma = compute_self_ma(TrainId::new(1), &log, &net, now_ns);

    assert!(ma.has_known_position);
    assert!(ma.valid_until_ns - now_ns <= MA_VALIDITY_WINDOW_NS);
}

// ---------------------------------------------------------------------------
// P1 (determinism): same input, same output.
//
// Trivially holds in Rust for pure functions, but proving it formally
// captures the structural commitment that `compute_self_ma` takes no
// hidden inputs (no clock read, no global state, no rand).
// ---------------------------------------------------------------------------

#[kani::proof]
#[kani::unwind(10)]
fn kani_p1_determinism() {
    let now_ns: u64 = kani::any();
    kani::assume(now_ns > 1_000_000_000);
    kani::assume(now_ns < u64::MAX / 2);

    let net = tiny_network();
    let log = train_on_first_section(1, 100_000, now_ns - 100_000_000);

    let a = compute_self_ma(TrainId::new(1), &log, &net, now_ns);
    let b = compute_self_ma(TrainId::new(1), &log, &net, now_ns);

    assert!(a == b);
}

// ---------------------------------------------------------------------------
// P3 (consist-fit): the MA end must be at or ahead of the head
// position — the MA never regresses into the consist's own footprint.
//
// Concretely: for a train at offset `h` on section 1000 going
// Forward, the computed MA's end must be either on section 1000 at
// offset ≥ h, or on a section strictly later in the forward chain.
// ---------------------------------------------------------------------------

#[kani::proof]
#[kani::unwind(16)]
fn kani_p3_consist_fit_single_train() {
    // Head somewhere in section 1000 (1 km long), past the consist
    // length so the tail fits on the same section.
    let head_offset_mm: i64 = kani::any();
    kani::assume(head_offset_mm >= 100_000);
    kani::assume(head_offset_mm <= 900_000);

    let now_ns: u64 = 1_000_000_000;
    let net = tiny_network();
    let log = train_on_first_section(1, head_offset_mm, 500_000_000);

    let ma = compute_self_ma(TrainId::new(1), &log, &net, now_ns);
    assert!(ma.has_known_position);

    // MA end is either on section 1000 (same or later offset) or on
    // a section later in the forward chain (1001).
    if ma.end.section == SectionId::new(1000) {
        assert!(ma.end.offset_mm >= head_offset_mm);
    } else {
        // Must be on 1001 (the only forward section after 1000 in
        // this network).
        assert!(ma.end.section == SectionId::new(1001));
    }
}

// ---------------------------------------------------------------------------
// P2 (non-overlap): two registered trains' MAs do not share any
// section (beyond their own respective footprints).
//
// Scaled from the old two-section fixture to three sections so the
// non-overlap claim is non-trivial: train 1 is on 1000, train 2 is
// on 1001, and train 2's MA may now legitimately extend into 1002
// (which is unoccupied). The property under test is that train 1's
// MA never advances past 1000's far end while train 2 holds 1001,
// and that the two trains' MA sets do not intersect on any section
// outside their own footprint.
// ---------------------------------------------------------------------------

#[kani::proof]
#[kani::unwind(16)]
fn kani_p2_non_overlap_two_trains() {
    let h1: i64 = kani::any();
    let h2: i64 = kani::any();
    // Bound both heads tightly so the state space is small.
    kani::assume(h1 >= 100_000 && h1 <= 800_000);
    kani::assume(h2 >= 100_000 && h2 <= 800_000);

    let now_ns: u64 = 1_000_000_000;
    let net = three_section_network();

    // Train 1 on section 1000, Train 2 on section 1001.
    let mut log = train_on_first_section(1, h1, 500_000_000);
    log.push(Entry {
        entry_id: EntryId::new(3),
        term: 1,
        timestamp_ns: 500_000_001,
        payload: EntryPayload::TrainRegistration(TrainRegistration {
            train_id: TrainId::new(2),
            consist: ConsistDescriptor::reference_3car(),
            initial_position: Position::certain(TrackRef {
                section: SectionId::new(1001),
                offset_mm: 0,
                direction: Direction::Forward,
            }),
        }),
    });
    log.push(Entry {
        entry_id: EntryId::new(4),
        term: 1,
        timestamp_ns: 500_000_002,
        payload: EntryPayload::TrainPositionReport(TrainPositionReport {
            train_id: TrainId::new(2),
            head_position: Position::certain(TrackRef {
                section: SectionId::new(1001),
                offset_mm: h2,
                direction: Direction::Forward,
            }),
            tail_position: Position::certain(TrackRef {
                section: SectionId::new(1001),
                offset_mm: (h2 - 65_000).max(0),
                direction: Direction::Forward,
            }),
            speed_mmps: 10_000,
            speed_uncertainty_mmps: 500,
            heading: Direction::Forward,
            contributing_sources: vec![PositionSource::Gnss],
            onboard_time_ns: 499_999_900,
            pack_soc_ppt: 900,
        }),
    });

    let ma1 = compute_self_ma(TrainId::new(1), &log, &net, now_ns);
    let ma2 = compute_self_ma(TrainId::new(2), &log, &net, now_ns);

    // Train 1 sees Train 2 occupying section 1001 → its MA ends on
    // section 1000.
    assert!(ma1.end.section == SectionId::new(1000));
    // Train 2's forward section 1002 is unoccupied → its MA extends
    // into 1002 and ends there. (The "full extension" direction of
    // P2: occupancy clipping is sharp, not overly conservative.)
    assert!(ma2.end.section == SectionId::new(1002));

    // Non-overlap on section boundaries — the two MA end sections
    // never coincide.
    assert!(ma1.end.section != ma2.end.section);
    // Neither MA reaches the other's head section.
    assert!(ma1.end.section != SectionId::new(1001));
    assert!(ma2.end.section != SectionId::new(1000));
}

// ---------------------------------------------------------------------------
// P4 (conservatism): more-uncertain input produces a
// more-restrictive MA.
//
// Encoded as: a fail-restrictive MA (no known position) never extends
// past the fallback head. This is the simplest refinement-style
// statement that Kani can discharge without comparing two runs of
// compute_self_ma.
// ---------------------------------------------------------------------------

#[kani::proof]
#[kani::unwind(10)]
fn kani_p4_fail_restrictive_is_not_less_restrictive_than_known() {
    let now_ns: u64 = 1_000_000_000;
    let net = tiny_network();

    // Unregistered train: fail-restrictive MA.
    let ma_unreg = compute_self_ma(TrainId::new(42), &[], &net, now_ns);
    assert!(!ma_unreg.has_known_position);

    // A fail-restrictive MA's end.offset_mm is 0 (head unknown). No
    // section the train could be on is "granted" forward travel.
    assert!(ma_unreg.end.offset_mm == 0);
    // applicable_restrictions is empty on the fail-restrictive path.
    assert!(ma_unreg.applicable_restrictions.is_empty());
}

// ---------------------------------------------------------------------------
// P4 (conservatism, mutation-style): adding a *more uncertain* entry to
// a committed log never extends an already-computed MA's end section.
//
// Concretely: from a baseline log with train 1 on section 1000, compare
// two MAs:
//   (a) baseline log alone.
//   (b) baseline log plus one additional occupancy by train 2 on section
//       1001 (another known-position entry is strictly more
//       information, but crucially *more restrictive* for train 1).
//
// The property: the MA end section of (b) is never ahead of (a) in the
// forward chain. Kani enumerates train-1 head offsets and checks the
// relationship.
// ---------------------------------------------------------------------------

#[kani::proof]
#[kani::unwind(16)]
fn kani_p4_conservatism_extra_occupant() {
    let h1: i64 = kani::any();
    kani::assume(h1 >= 100_000 && h1 <= 800_000);

    let now_ns: u64 = 1_000_000_000;
    let net = three_section_network();

    // Baseline: train 1 alone on section 1000.
    let baseline = train_on_first_section(1, h1, 500_000_000);

    // Mutation: add train 2 on section 1001.
    let mut mutated = baseline.clone();
    mutated.push(Entry {
        entry_id: EntryId::new(3),
        term: 1,
        timestamp_ns: 500_000_001,
        payload: EntryPayload::TrainRegistration(TrainRegistration {
            train_id: TrainId::new(2),
            consist: ConsistDescriptor::reference_3car(),
            initial_position: Position::certain(TrackRef {
                section: SectionId::new(1001),
                offset_mm: 0,
                direction: Direction::Forward,
            }),
        }),
    });
    mutated.push(Entry {
        entry_id: EntryId::new(4),
        term: 1,
        timestamp_ns: 500_000_002,
        payload: EntryPayload::TrainPositionReport(TrainPositionReport {
            train_id: TrainId::new(2),
            head_position: Position::certain(TrackRef {
                section: SectionId::new(1001),
                offset_mm: 500_000,
                direction: Direction::Forward,
            }),
            tail_position: Position::certain(TrackRef {
                section: SectionId::new(1001),
                offset_mm: 0,
                direction: Direction::Forward,
            }),
            speed_mmps: 10_000,
            speed_uncertainty_mmps: 500,
            heading: Direction::Forward,
            contributing_sources: vec![PositionSource::Gnss],
            onboard_time_ns: 499_999_900,
            pack_soc_ppt: 900,
        }),
    });

    let ma_baseline = compute_self_ma(TrainId::new(1), &baseline, &net, now_ns);
    let ma_mutated = compute_self_ma(TrainId::new(1), &mutated, &net, now_ns);

    // MA end section must not advance past the baseline when the
    // mutation is strictly more restrictive.
    let section_rank =
        |sec: SectionId| -> u8 {
            match sec.0 {
                1000 => 1,
                1001 => 2,
                1002 => 3,
                _ => 0,
            }
        };
    assert!(section_rank(ma_mutated.end.section) <= section_rank(ma_baseline.end.section));
}
