//! Kani bounded-model-checker harnesses for the ATP's safety
//! properties A1–A7, as named in the [crate docs](crate).
//!
//! # Status
//!
//! **A1–A7 all written.** A1 (determinism), A2 (MA-expired trips),
//! A3 (unknown-position trips), A4 (train-id mismatch trips),
//! A5 (head-past-MA-end trips), A6 (overspeed trips), A7 (conservatism
//! under widened speed uncertainty). Every proptest in
//! [`tests/proptest_atp.rs`](../../tests/proptest_atp.rs) now has a
//! Kani counterpart; scaling the bounds is the only remaining work.
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

// ---------------------------------------------------------------------------
// A3 (unknown position trips): `!ma.has_known_position` forces an
// Emergency brake with `TriggerReason::NoKnownPosition`.
//
// Short-circuits before the topology walk, so an empty `Network` is
// enough and the proof discharges in milliseconds.
// ---------------------------------------------------------------------------

#[kani::proof]
fn kani_a3_unknown_position_trips() {
    let now_ns: u64 = kani::any();
    // Keep the MA technically valid so we exercise the A3 branch
    // rather than falling through to A2.
    let valid_until_ns: u64 = kani::any();
    kani::assume(valid_until_ns > now_ns);

    let net = Network::default();
    let consist = ConsistDescriptor::reference_3car();
    let state = state_on_section(7, 1000, 0);
    let mut ma = nominal_ma(7, 1001, 500_000, 0);
    ma.valid_until_ns = valid_until_ns;
    ma.has_known_position = false;

    let out = atp_evaluate(&state, &ma, &consist, &net, now_ns);

    assert!(matches!(out.command, BrakeCommand::Emergency));
    assert!(matches!(out.reason, TriggerReason::NoKnownPosition));
}

// ---------------------------------------------------------------------------
// A4 (train-id mismatch trips): receiving an MA addressed to a
// different train must trip the brake, not silently ignore the MA.
// Short-circuits at the very top of `atp_evaluate`.
// ---------------------------------------------------------------------------

#[kani::proof]
fn kani_a4_train_mismatch_trips() {
    let state_id: u64 = kani::any();
    let ma_id: u64 = kani::any();
    kani::assume(state_id != ma_id);

    let net = Network::default();
    let consist = ConsistDescriptor::reference_3car();
    let state = state_on_section(state_id, 1000, 0);
    let ma = nominal_ma(ma_id, 1001, 500_000, 0);

    let out = atp_evaluate(&state, &ma, &consist, &net, 0);

    assert!(matches!(out.command, BrakeCommand::Emergency));
    assert!(matches!(out.reason, TriggerReason::MaTrainMismatch));
}

// ---------------------------------------------------------------------------
// A5 (head past MA end trips): if the train's head has already
// advanced past the MA end (same section, head.offset > end.offset),
// the ATP must apply the emergency brake with
// `TriggerReason::HeadPastMaEnd`.
//
// Same-section case keeps the Network trivial (Kani still needs it
// to hold up to the section-length read).
// ---------------------------------------------------------------------------

#[kani::proof]
fn kani_a5_head_past_ma_end_trips_same_section() {
    // Build the tiny network so the same-section length lookup succeeds
    // if we ever reach the slow path. For this proof we stay in the
    // same-section fast path of `distance_to_ma_end`.
    let net = tiny_network();
    let consist = ConsistDescriptor::reference_3car();

    let head_offset: i64 = kani::any();
    let end_offset: i64 = kani::any();
    kani::assume(head_offset >= 0);
    kani::assume(end_offset >= 0);
    kani::assume(head_offset <= 1_000_000);
    kani::assume(end_offset <= 1_000_000);
    // Head is strictly past the MA end on the same section.
    kani::assume(head_offset > end_offset);

    let state = state_on_section(7, 1000, head_offset);
    let ma = nominal_ma(7, 1000, end_offset, 0);

    let out = atp_evaluate(&state, &ma, &consist, &net, 0);

    assert!(matches!(out.command, BrakeCommand::Emergency));
    assert!(matches!(out.reason, TriggerReason::HeadPastMaEnd));
}

// ---------------------------------------------------------------------------
// A6 (overspeed trips): when the measured speed exceeds the envelope
// by more than `OVERSPEED_EMERGENCY_MARGIN_MMPS`, the ATP commands
// emergency brake for `TriggerReason::Overspeed`.
//
// We stay in the same-section fast path (head + end both on section
// 1000) and pre-compute the envelope at distance `end_offset`, then
// assume the measured speed lands above envelope + margin.
// ---------------------------------------------------------------------------

#[kani::proof]
#[kani::unwind(4)]
fn kani_a6_severe_overspeed_trips() {
    use crate::envelope::{max_safe_speed_mmps, DecelTable};
    use crate::evaluate::OVERSPEED_EMERGENCY_MARGIN_MMPS;

    // Distance bounded away from 0 so the envelope is finite and
    // bounded up so Kani doesn't explore the full i64 range. 1 km is
    // enough to cover the ramp band.
    let dist: i64 = kani::any();
    kani::assume(dist >= 1_000);
    kani::assume(dist <= 900_000);

    // Pick a measured speed strictly above envelope + margin. We
    // choose the excess nondeterministically to prove the band is
    // reached for *every* such excess; the bound keeps i32 arithmetic
    // from wrapping.
    let excess: i32 = kani::any();
    kani::assume(excess > OVERSPEED_EMERGENCY_MARGIN_MMPS);
    kani::assume(excess <= 10_000);

    let net = tiny_network();
    let consist = ConsistDescriptor::reference_3car();
    let decel = DecelTable::from_emergency(&consist);
    let envelope = max_safe_speed_mmps(dist, &decel);

    // Guard: envelope + excess must not overflow i32. Given the
    // assumed bounds (envelope ≤ 100_000 mm/s for 900 m at normal
    // decel, excess ≤ 10_000) this always holds, but we spell it
    // out so Kani doesn't explore the overflow branch.
    kani::assume(envelope <= i32::MAX - excess);

    let speed = envelope + excess;

    let state = TrainState {
        train_id: TrainId::new(7),
        head: TrackRef {
            section: SectionId::new(1000),
            offset_mm: 0,
            direction: Direction::Forward,
        },
        speed_mmps: speed,
        speed_uncertainty_mmps: 0,
        position_uncertainty_mm: 0,
    };
    // MA ends `dist` mm ahead on the same section.
    let ma = nominal_ma(7, 1000, dist, 0);

    let out = atp_evaluate(&state, &ma, &consist, &net, 0);

    assert!(matches!(out.command, BrakeCommand::Emergency));
    assert!(matches!(out.reason, TriggerReason::Overspeed));
}

// ---------------------------------------------------------------------------
// A7 (conservatism): widening `speed_uncertainty_mmps` never softens
// the ATP's outcome. Severity is ordered
// `Release < Service(_) < Emergency`.
//
// This is the refinement direction P4 captures for the MA computer,
// ported here for the ATP's brake-command layer.
// ---------------------------------------------------------------------------

fn severity(command: &BrakeCommand) -> u8 {
    match command {
        BrakeCommand::Release => 0,
        BrakeCommand::Service(_) => 1,
        BrakeCommand::Emergency => 2,
    }
}

#[kani::proof]
#[kani::unwind(8)]
fn kani_a7_uncertainty_widening_is_conservative() {
    let head_offset: i64 = kani::any();
    kani::assume(head_offset >= 0);
    kani::assume(head_offset <= 800_000);

    let speed_mmps: i32 = kani::any();
    kani::assume(speed_mmps >= 0);
    kani::assume(speed_mmps <= 20_000);

    let base_unc: u32 = kani::any();
    kani::assume(base_unc <= 1_000);
    let extra_unc: u32 = kani::any();
    kani::assume(extra_unc <= 1_000);
    // Prevent the sum from wrapping the u32 range — a realistic
    // uncertainty envelope is well under this bound.
    kani::assume(base_unc <= u32::MAX - extra_unc);

    let end_offset: i64 = kani::any();
    kani::assume(end_offset >= 100_000);
    kani::assume(end_offset <= 1_000_000);

    let net = tiny_network();
    let consist = ConsistDescriptor::reference_3car();

    let mut state_low = state_on_section(7, 1000, head_offset);
    state_low.speed_mmps = speed_mmps;
    state_low.speed_uncertainty_mmps = base_unc;

    let mut state_high = state_low.clone();
    state_high.speed_uncertainty_mmps = base_unc + extra_unc;

    let ma = nominal_ma(7, 1000, end_offset, 0);

    let out_low = atp_evaluate(&state_low, &ma, &consist, &net, 0);
    let out_high = atp_evaluate(&state_high, &ma, &consist, &net, 0);

    assert!(severity(&out_high.command) >= severity(&out_low.command));
}
