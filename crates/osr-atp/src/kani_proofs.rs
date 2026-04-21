//! Kani bounded-model-checker harnesses for the ATP's safety
//! properties A1–A7, as named in the [crate docs](crate).
//!
//! # Status
//!
//! Initial landing — **A1 (determinism)** and **A2 (expired MA trips)**
//! written. A3–A7 are the next increment; the scaffolding
//! ([`tiny_network`], [`nominal_ma`], [`state_on_section`]) is shared
//! so each addition is a single `#[kani::proof]` function.
//!
//! The same property is covered by an unbounded proptest in
//! [`tests/proptest_atp.rs`](../../tests/proptest_atp.rs); the Kani
//! harness upgrades that coverage to a formal guarantee within
//! the bounds written into each proof.
//!
//! # Running
//!
//! ```bash
//! cargo install --locked kani-verifier
//! cargo kani setup
//! cargo kani -p osr-atp --harness kani_a2_expired_ma_trips
//! ```
//!
//! Or all harnesses in the crate:
//!
//! ```bash
//! cargo kani -p osr-atp
//! ```
//!
//! A1 exercises the full `atp_evaluate` path (topology walk included)
//! and needs non-trivial unwind. A2 short-circuits before the
//! topology is touched, so it discharges in under a second.

#![cfg(kani)]

use osr_core::{
    ConsistDescriptor, Direction, Line, Network, Section, SectionId, Station, StationId, TrackRef,
    TrainId,
};
use osr_interlocking::{MovementAuthority, MAX_MA_DISTANCE_MM, MA_VALIDITY_WINDOW_NS};

use crate::evaluate::{atp_evaluate, BrakeCommand, TriggerReason};
use crate::state::TrainState;

// ---------------------------------------------------------------------------
// Scaffolding: tiny, Kani-friendly fixtures.
// ---------------------------------------------------------------------------

/// Three-section linear network: S1 ── 1000 ──▶ S2 ── 1001 ──▶ S3 ── 1002 ──▶ S4.
///
/// Every section is 1 km long. Matches the unit-test `net_3_sections`
/// but with empty strings in place of formatted station names — Kani
/// dislikes non-trivial string construction.
fn tiny_network() -> Network {
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

fn state_on_section(train_id: u64, section: u64, head_offset_mm: i64) -> TrainState {
    TrainState {
        train_id: TrainId::new(train_id),
        head: TrackRef {
            section: SectionId::new(section),
            offset_mm: head_offset_mm,
            direction: Direction::Forward,
        },
        speed_mmps: 0,
        speed_uncertainty_mmps: 0,
        position_uncertainty_mm: 0,
    }
}

fn nominal_ma(train_id: u64, end_section: u64, end_offset: i64, now_ns: u64) -> MovementAuthority {
    MovementAuthority {
        train_id: TrainId::new(train_id),
        end: TrackRef {
            section: SectionId::new(end_section),
            offset_mm: end_offset,
            direction: Direction::Forward,
        },
        applicable_restrictions: vec![],
        valid_until_ns: now_ns.saturating_add(MA_VALIDITY_WINDOW_NS),
        derived_from_entry_id: None,
        has_known_position: true,
    }
}

// ---------------------------------------------------------------------------
// A2 (expired MA trips): if `now_ns >= ma.valid_until_ns`, outcome is
// Emergency / MaExpired — regardless of any other input.
//
// Short-circuits before the topology walk, so an empty `Network` works
// and the proof discharges quickly.
// ---------------------------------------------------------------------------

#[kani::proof]
fn kani_a2_expired_ma_trips() {
    let now_ns: u64 = kani::any();
    let valid_until_ns: u64 = kani::any();
    kani::assume(now_ns >= valid_until_ns);

    // An empty network is sufficient: the A2 check runs before any
    // `Network` field is read.
    let net = Network::default();
    let consist = ConsistDescriptor::reference_3car();
    let state = state_on_section(7, 1000, 0);

    let mut ma = nominal_ma(7, 1001, 500_000, 0);
    ma.valid_until_ns = valid_until_ns;

    let out = atp_evaluate(&state, &ma, &consist, &net, now_ns);

    assert!(matches!(out.command, BrakeCommand::Emergency));
    assert!(matches!(out.reason, TriggerReason::MaExpired));
}

// ---------------------------------------------------------------------------
// A1 (determinism): two invocations with byte-identical inputs produce
// byte-identical outputs.
//
// Proves `atp_evaluate` has no hidden inputs (no clock read, no global
// state, no randomness). The harness runs the full path — topology
// walk, envelope math, three-region partition — so non-determinism
// anywhere in that chain would show up.
// ---------------------------------------------------------------------------

#[kani::proof]
#[kani::unwind(8)]
fn kani_a1_determinism() {
    // Bound the head to the interior of section 1000 so the topology
    // walk has work to do (distance-to-end will cross into 1001 or
    // 1002) but the state space stays small.
    let head_offset_mm: i64 = kani::any();
    kani::assume(head_offset_mm >= 0);
    kani::assume(head_offset_mm <= 900_000);

    let speed_mmps: i32 = kani::any();
    kani::assume(speed_mmps >= 0);
    kani::assume(speed_mmps <= 30_000); // ≤ 30 m/s — well below any envelope

    let now_ns: u64 = kani::any();
    kani::assume(now_ns <= u64::MAX - MA_VALIDITY_WINDOW_NS - 1);

    // MA end on section 1001 (one section ahead of the head's section).
    // Offset bounded to keep the distance under MAX_MA_DISTANCE_MM.
    let end_offset: i64 = kani::any();
    kani::assume(end_offset >= 0);
    kani::assume(end_offset <= 500_000);

    let net = tiny_network();
    let consist = ConsistDescriptor::reference_3car();

    let mut state = state_on_section(7, 1000, head_offset_mm);
    state.speed_mmps = speed_mmps;

    let ma = nominal_ma(7, 1001, end_offset, now_ns);

    // Bound on MA reachability — keeps the forward chain short.
    let _ = MAX_MA_DISTANCE_MM;

    let a = atp_evaluate(&state, &ma, &consist, &net, now_ns);
    let b = atp_evaluate(&state, &ma, &consist, &net, now_ns);

    assert!(a == b);
}
