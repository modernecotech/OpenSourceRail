//! Kani bounded-model-checker harnesses for O1–O5.
//!
//! `odom_step` is a pure function but the wheel-dead-reckoning path
//! touches the network topology, so each harness uses a fixed
//! 3-section linear fixture (matching the style used by
//! `osr-atp::kani_proofs::tiny_network`) and a bounded unwind.
//!
//! Run with:
//!
//! ```bash
//! cargo kani -p osr-odometry
//! ```

#![cfg(kani)]

use osr_core::{
    Direction, Line, Network, Section, SectionId, Station, StationId, TrackRef, TrainId,
};

use crate::fusion::odom_step;
use crate::sensors::{BaliseFix, BaliseId, GnssFix, OdomCalibration, PositionSource, SensorTick};
use crate::state::OdomState;

// ---------------------------------------------------------------------------
// Scaffolding
// ---------------------------------------------------------------------------

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

fn fixed_cal() -> OdomCalibration {
    OdomCalibration {
        pulses_per_meter: 410,
        wheel_slip_ppm: 5_000,
        uncertainty_floor_per_tick_mm: 2,
        min_uncertainty_mm: 50,
        max_uncertainty_mm: 50_000,
    }
}

fn arb_prev() -> OdomState {
    let offset_mm: i64 = kani::any();
    kani::assume(offset_mm >= 0);
    kani::assume(offset_mm <= 900_000);
    let prev_unc: u32 = kani::any();
    kani::assume(prev_unc <= 10_000);
    OdomState {
        train_id: TrainId::new(7),
        head: TrackRef {
            section: SectionId::new(1000),
            offset_mm,
            direction: Direction::Forward,
        },
        speed_mmps: 0,
        position_uncertainty_mm: prev_unc,
        speed_uncertainty_mmps: 0,
        contributing_source: PositionSource::WheelTachometer,
        last_balise_id: None,
        last_timestamp_ns: 0,
    }
}

fn arb_tick_no_fix() -> SensorTick {
    let pulses: i32 = kani::any();
    // Bound to ~ ±2 m per tick (≈ ±820 pulses) to keep forward-chain
    // walks short.
    kani::assume(pulses.abs() <= 820);
    let ts: u64 = kani::any();
    kani::assume(ts <= 10_000_000_000);
    SensorTick {
        timestamp_ns: ts,
        wheel_pulses: pulses,
        gnss: None,
        balise: None,
    }
}

// ---------------------------------------------------------------------------
// O1 (determinism)
// ---------------------------------------------------------------------------

#[kani::proof]
#[kani::unwind(6)]
fn kani_o1_determinism() {
    let prev = arb_prev();
    let cal = fixed_cal();
    let sensors = arb_tick_no_fix();
    let net = tiny_network();

    let a = odom_step(&prev, &cal, &sensors, &net);
    let b = odom_step(&prev, &cal, &sensors, &net);
    assert!(a == b);
}

// ---------------------------------------------------------------------------
// O3 (uncertainty monotone without fix): no balise, no tightening
// GNSS → new uncertainty is at least `min_uncertainty_mm` and never
// strictly less than the previous uncertainty (up to the per-tick
// floor add and the `max_uncertainty_mm` cap).
// ---------------------------------------------------------------------------

#[kani::proof]
#[kani::unwind(6)]
fn kani_o3_uncertainty_monotone_without_fix() {
    let prev = arb_prev();
    let cal = fixed_cal();
    let sensors = arb_tick_no_fix();
    let net = tiny_network();

    let next = odom_step(&prev, &cal, &sensors, &net);

    // Minimum floor the output can't go below.
    let floor = cal.min_uncertainty_mm.max(0);
    assert!(next.position_uncertainty_mm >= floor);

    // Without a fix, uncertainty only grows (subject to the max cap).
    // So either next.uncertainty >= prev.uncertainty, or the cap
    // clipped it down to `max_uncertainty_mm`.
    let prev_unc = prev.position_uncertainty_mm.min(cal.max_uncertainty_mm);
    assert!(
        next.position_uncertainty_mm >= prev_unc
            || next.position_uncertainty_mm == cal.max_uncertainty_mm
    );
}

// ---------------------------------------------------------------------------
// O4 (balise resets uncertainty)
// ---------------------------------------------------------------------------

#[kani::proof]
#[kani::unwind(6)]
fn kani_o4_balise_resets_uncertainty() {
    let prev = arb_prev();
    let cal = fixed_cal();
    let net = tiny_network();

    let fix_uncertainty: u32 = kani::any();
    kani::assume(fix_uncertainty <= 10_000);

    let balise_section: u64 = kani::any();
    kani::assume(balise_section >= 1000 && balise_section <= 1002);
    let balise_offset: i64 = kani::any();
    kani::assume(balise_offset >= 0);
    kani::assume(balise_offset <= 1_000_000);

    let sensors = SensorTick {
        timestamp_ns: 1_000,
        wheel_pulses: 0,
        gnss: None,
        balise: Some(BaliseFix {
            balise_id: BaliseId::new(42),
            position: TrackRef {
                section: SectionId::new(balise_section),
                offset_mm: balise_offset,
                direction: Direction::Forward,
            },
            uncertainty_mm: fix_uncertainty,
        }),
    };

    let next = odom_step(&prev, &cal, &sensors, &net);

    // Uncertainty should be max(fix.uncertainty, min_unc), capped by max_unc.
    let expected = fix_uncertainty
        .max(cal.min_uncertainty_mm)
        .min(cal.max_uncertainty_mm);
    assert!(next.position_uncertainty_mm == expected);
    assert!(matches!(next.contributing_source, PositionSource::Balise));
    assert!(next.last_balise_id == Some(BaliseId::new(42)));
}

// ---------------------------------------------------------------------------
// O5 (GNSS soft-correction is conservative): a GNSS fix whose
// reported uncertainty is ≥ the current dead-reckoned uncertainty
// must be ignored — the head is unchanged (matching the wheel-
// advanced position) and `contributing_source` is WheelTachometer.
// ---------------------------------------------------------------------------

#[kani::proof]
#[kani::unwind(6)]
fn kani_o5_gnss_does_not_loosen() {
    let prev = arb_prev();
    let cal = fixed_cal();
    let net = tiny_network();

    // Wheel-only dead-reckoning reference: no GNSS, no balise, same
    // wheel input.
    let pulses: i32 = kani::any();
    kani::assume(pulses.abs() <= 820);
    let ts: u64 = kani::any();
    kani::assume(ts <= 10_000_000_000);

    let dr_sensors = SensorTick {
        timestamp_ns: ts,
        wheel_pulses: pulses,
        gnss: None,
        balise: None,
    };
    let dr_next = odom_step(&prev, &cal, &dr_sensors, &net);

    // Now construct a GNSS tick with uncertainty ≥ dr_next's
    // uncertainty — by O5 it should be ignored.
    let gnss_unc: u32 = kani::any();
    kani::assume(gnss_unc >= dr_next.position_uncertainty_mm);
    kani::assume(gnss_unc <= 50_000);

    let gnss_offset: i64 = kani::any();
    kani::assume(gnss_offset >= 0);
    kani::assume(gnss_offset <= 1_000_000);

    let gnss_sensors = SensorTick {
        timestamp_ns: ts,
        wheel_pulses: pulses,
        gnss: Some(GnssFix {
            projected: TrackRef {
                section: SectionId::new(1002),
                offset_mm: gnss_offset,
                direction: Direction::Forward,
            },
            uncertainty_mm: gnss_unc,
        }),
        balise: None,
    };
    let gnss_next = odom_step(&prev, &cal, &gnss_sensors, &net);

    // GNSS ignored: head/uncertainty/source match the wheel-only step.
    assert!(gnss_next.head == dr_next.head);
    assert!(gnss_next.position_uncertainty_mm == dr_next.position_uncertainty_mm);
    assert!(matches!(
        gnss_next.contributing_source,
        PositionSource::WheelTachometer
    ));
}

// ---------------------------------------------------------------------------
// O2 (forward non-regression, bounded form): with non-negative wheel
// pulses, no balise, no tightening GNSS, starting in the interior of
// section 1000, the resulting head is either (a) still in 1000 at an
// offset ≥ prev.offset, or (b) in section 1001 or 1002 (further
// along the forward chain). Bounded: 2 m/tick keeps the walk short.
// ---------------------------------------------------------------------------

#[kani::proof]
#[kani::unwind(6)]
fn kani_o2_forward_non_regression() {
    let prev = arb_prev();
    let cal = fixed_cal();
    let net = tiny_network();

    let pulses: i32 = kani::any();
    kani::assume(pulses >= 0);
    kani::assume(pulses <= 820);
    let ts: u64 = kani::any();
    kani::assume(ts <= 10_000_000_000);

    let sensors = SensorTick {
        timestamp_ns: ts,
        wheel_pulses: pulses,
        gnss: None,
        balise: None,
    };
    let next = odom_step(&prev, &cal, &sensors, &net);

    // The head must stay on one of the three forward sections.
    let sec = next.head.section.0;
    assert!(sec == 1000 || sec == 1001 || sec == 1002);

    // Same-section case: offset must not have regressed.
    if next.head.section == prev.head.section {
        assert!(next.head.offset_mm >= prev.head.offset_mm);
    }
    // Cross-section case: section id must be strictly after 1000.
    if next.head.section != prev.head.section {
        assert!(next.head.section.0 > prev.head.section.0);
    }
}
