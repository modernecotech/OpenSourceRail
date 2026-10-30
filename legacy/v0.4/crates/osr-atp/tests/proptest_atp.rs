//! Property-based tests for the ATP.
//!
//! Exercises the crate-level safety properties A1–A7 over random
//! inputs. A subset of these are candidates for future Kani harnesses
//! once the SIL-4 partition migrates to bounded formal verification
//! (RFC 0005 §11, Phase 2a harnessing work).

use osr_atp::{
    atp_evaluate, max_safe_speed_mmps, AtpOutcome, BrakeCommand, DecelTable, TrainState,
    TriggerReason, OVERSPEED_EMERGENCY_MARGIN_MMPS, SERVICE_BRAKE_MARGIN_MMPS,
};
use osr_core::{
    ConsistDescriptor, Direction, Line, Network, Section, SectionId, Station, StationId, TrackRef,
    TrainId,
};
use osr_interlocking::{MovementAuthority, MA_VALIDITY_WINDOW_NS};
use proptest::prelude::*;

fn net() -> Network {
    let mut net = Network::default();
    for i in 1..=4 {
        net.stations.insert(
            StationId::new(i),
            Station {
                id: StationId::new(i),
                name: format!("S{i}"),
                charging_power_kw: 0,
                dwell_seconds: 0,
                is_terminal: false,
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
        name: "L".into(),
        stations: (1..=4).map(StationId::new).collect(),
        forward_sections: fwd,
        reverse_sections: rev,
        is_ring: false,
    });
    net
}

fn consist() -> ConsistDescriptor {
    ConsistDescriptor::reference_3car()
}

fn state_in_sec0(offset_mm: i64, speed_mmps: i32, speed_unc: u32, pos_unc: u32) -> TrainState {
    TrainState {
        train_id: TrainId::new(7),
        head: TrackRef {
            section: SectionId::new(1000),
            offset_mm,
            direction: Direction::Forward,
        },
        speed_mmps,
        speed_uncertainty_mmps: speed_unc,
        position_uncertainty_mm: pos_unc,
    }
}

fn ma_at(end_section: u64, end_offset: i64, now_ns: u64) -> MovementAuthority {
    MovementAuthority {
        train_id: TrainId::new(7),
        end: TrackRef {
            section: SectionId::new(end_section),
            offset_mm: end_offset,
            direction: Direction::Forward,
        },
        applicable_restrictions: vec![],
        valid_until_ns: now_ns + MA_VALIDITY_WINDOW_NS,
        derived_from_entry_id: None,
        has_known_position: true,
    }
}

// ---------------------------------------------------------------------------
// A1: determinism. Identical inputs produce identical outputs.
// ---------------------------------------------------------------------------

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, .. ProptestConfig::default() })]

    #[test]
    fn a1_determinism(
        head_offset in 0i64..1_000_000,
        speed_mmps in 0i32..25_000,
        speed_unc in 0u32..1_000,
        pos_unc in 0u32..5_000,
        ma_end_section in prop_oneof![Just(1000u64), Just(1001u64), Just(1002u64)],
        ma_end_offset in 0i64..1_000_000,
        now_ns in 0u64..1_000_000_000,
    ) {
        let net = net();
        let consist = consist();
        let state = state_in_sec0(head_offset, speed_mmps, speed_unc, pos_unc);
        let ma = ma_at(ma_end_section, ma_end_offset, now_ns);

        let a = atp_evaluate(&state, &ma, &consist, &net, now_ns);
        let b = atp_evaluate(&state, &ma, &consist, &net, now_ns);
        prop_assert_eq!(a, b);
    }
}

// ---------------------------------------------------------------------------
// A2: any `now_ns >= ma.valid_until_ns` → Emergency, regardless of
//     everything else about the state.
// ---------------------------------------------------------------------------

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, .. ProptestConfig::default() })]

    #[test]
    fn a2_expired_ma_always_emergency(
        head_offset in 0i64..1_000_000,
        speed_mmps in 0i32..25_000,
        delta in 0u64..10_000_000_000, // 0..10s past valid_until
    ) {
        let net = net();
        let consist = consist();
        let state = state_in_sec0(head_offset, speed_mmps, 0, 0);
        let ma = ma_at(1002, 500_000, 0);
        let now_ns = ma.valid_until_ns + delta;
        let out = atp_evaluate(&state, &ma, &consist, &net, now_ns);
        prop_assert!(out.is_emergency());
        prop_assert_eq!(out.reason, TriggerReason::MaExpired);
    }
}

// ---------------------------------------------------------------------------
// A3: !has_known_position → Emergency.
// ---------------------------------------------------------------------------

proptest! {
    #![proptest_config(ProptestConfig { cases: 128, .. ProptestConfig::default() })]

    #[test]
    fn a3_no_known_position_always_emergency(
        head_offset in 0i64..1_000_000,
        speed_mmps in 0i32..25_000,
    ) {
        let net = net();
        let consist = consist();
        let state = state_in_sec0(head_offset, speed_mmps, 0, 0);
        let mut ma = ma_at(1002, 500_000, 0);
        ma.has_known_position = false;
        let out = atp_evaluate(&state, &ma, &consist, &net, 0);
        prop_assert!(out.is_emergency());
        prop_assert_eq!(out.reason, TriggerReason::NoKnownPosition);
    }
}

// ---------------------------------------------------------------------------
// A6: severe overspeed → Emergency.
// A narrower version exists as a unit test; here we sweep over distance
// and speed to confirm the trip band is reached whenever measured
// speed exceeds envelope + OVERSPEED_EMERGENCY_MARGIN_MMPS.
// ---------------------------------------------------------------------------

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, .. ProptestConfig::default() })]

    #[test]
    fn a6_speed_above_envelope_plus_margin_trips(
        dist_raw in 1i64..1_500_000,
        excess in (OVERSPEED_EMERGENCY_MARGIN_MMPS + 100)..10_000i32,
    ) {
        let net = net();
        let consist = consist();
        let decel = DecelTable::from_emergency(&consist);
        // Construct a state with speed = envelope + excess.
        let envelope = max_safe_speed_mmps(dist_raw, &decel);
        let speed = envelope.saturating_add(excess);
        // Head at offset such that MA end is `dist_raw` ahead in section 1000.
        let end_offset = dist_raw;
        // Head must be at 0 in section 1000 so distance == end_offset.
        let state = state_in_sec0(0, speed, 0, 0);
        let ma = ma_at(1000, end_offset, 0);
        let out = atp_evaluate(&state, &ma, &consist, &net, 0);
        prop_assert!(out.is_emergency(), "state {:?} ma {:?} envelope {} speed {} out {:?}",
            state, ma, envelope, speed, out);
        prop_assert_eq!(out.reason, TriggerReason::Overspeed);
    }
}

// ---------------------------------------------------------------------------
// A7 (partial): conservatism — enlarging speed uncertainty never
//    produces a less-severe outcome.
//
// Severity order: Release < Service(*) < Emergency.
// ---------------------------------------------------------------------------

fn severity(o: &AtpOutcome) -> u8 {
    match o.command {
        BrakeCommand::Release => 0,
        BrakeCommand::Service(_) => 1,
        BrakeCommand::Emergency => 2,
    }
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, .. ProptestConfig::default() })]

    #[test]
    fn a7_speed_uncertainty_is_conservative(
        head_offset in 0i64..900_000,
        speed_mmps in 0i32..18_000,
        base_unc in 0u32..1_000,
        extra_unc in 0u32..2_000,
        ma_end_offset in 100_000i64..1_000_000,
    ) {
        let net = net();
        let consist = consist();
        let state_low = state_in_sec0(head_offset, speed_mmps, base_unc, 0);
        let state_high = state_in_sec0(head_offset, speed_mmps, base_unc + extra_unc, 0);
        let ma = ma_at(1000, ma_end_offset, 0);
        let out_low = atp_evaluate(&state_low, &ma, &consist, &net, 0);
        let out_high = atp_evaluate(&state_high, &ma, &consist, &net, 0);
        prop_assert!(
            severity(&out_high) >= severity(&out_low),
            "uncertainty widened but outcome softened: low={:?} high={:?}",
            out_low, out_high
        );
    }
}

// ---------------------------------------------------------------------------
// A7 (partial): shrinking the MA end (closer MA) never softens the
//    outcome. Specifically, moving the MA end backwards on the same
//    section should never turn Emergency→Service or Service→Release.
// ---------------------------------------------------------------------------

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, .. ProptestConfig::default() })]

    #[test]
    fn a7_shorter_ma_is_conservative(
        head_offset in 0i64..500_000,
        speed_mmps in 0i32..18_000,
        longer in 600_000i64..1_000_000,
        shorten_by in 100_000i64..500_000,
    ) {
        let net = net();
        let consist = consist();
        let state = state_in_sec0(head_offset, speed_mmps, 0, 0);
        let ma_longer = ma_at(1000, longer, 0);
        let ma_shorter = ma_at(1000, (longer - shorten_by).max(head_offset + 1), 0);
        let out_longer = atp_evaluate(&state, &ma_longer, &consist, &net, 0);
        let out_shorter = atp_evaluate(&state, &ma_shorter, &consist, &net, 0);
        prop_assert!(
            severity(&out_shorter) >= severity(&out_longer),
            "shorter MA produced softer outcome: longer={:?} shorter={:?}",
            out_longer, out_shorter
        );
    }
}

// ---------------------------------------------------------------------------
// Sanity: a stopped train with a valid forward MA never receives
// Emergency. (This is a "not-vacuous" check: earlier trips are gated
// on state validity, not merely on "something is wrong.")
// ---------------------------------------------------------------------------

proptest! {
    #![proptest_config(ProptestConfig { cases: 128, .. ProptestConfig::default() })]

    #[test]
    fn stopped_nominal_train_never_emergency(
        head_offset in 0i64..900_000,
        ma_end_offset in 950_000i64..1_000_000,
    ) {
        let net = net();
        let consist = consist();
        let state = state_in_sec0(head_offset, 0, 0, 0);
        let ma = ma_at(1000, ma_end_offset, 0);
        let out = atp_evaluate(&state, &ma, &consist, &net, 0);
        prop_assert!(!out.is_emergency(), "stopped train tripped: {out:?}");
    }
}

// A margin check used above: ensure our severity-partition band
// constants are internally consistent — the service band is positive
// and does not overlap the emergency-margin constant.
#[test]
fn margin_constants_well_ordered() {
    const { assert!(SERVICE_BRAKE_MARGIN_MMPS > 0) };
    const { assert!(OVERSPEED_EMERGENCY_MARGIN_MMPS > 0) };
    const { assert!(SERVICE_BRAKE_MARGIN_MMPS > OVERSPEED_EMERGENCY_MARGIN_MMPS) };
}
