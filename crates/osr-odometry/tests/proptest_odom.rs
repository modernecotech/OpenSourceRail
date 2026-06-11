//! Property-based tests for `osr-odometry`.
//!
//! Exercises the crate-level safety properties O1–O5 over random
//! inputs. Candidates for future Kani harnesses once the SIL-4
//! partition migrates to bounded formal verification.

use osr_core::{
    Direction, Line, Network, Section, SectionId, Station, StationId, TrackRef, TrainId,
};
use osr_odometry::{
    odom_step, BaliseFix, BaliseId, GnssFix, OdomCalibration, OdomState, PositionSource, SensorTick,
};
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
                length_mm: 1_000_000,
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

fn cal() -> OdomCalibration {
    OdomCalibration::light_metro_default()
}

fn init_at_offset(offset_mm: i64) -> OdomState {
    OdomState::new_at(
        TrainId::new(7),
        TrackRef {
            section: SectionId::new(1000),
            offset_mm,
            direction: Direction::Forward,
        },
        50,
        0,
    )
}

/// Linearise a TrackRef along the forward line sections 1000→1001→1002
/// into a single scalar "distance from the start of section 1000" (mm).
/// Sections are 1 km each, so 1001@500_000 linearises to 1_500_000.
fn linear_position_mm(t: TrackRef) -> i64 {
    let sec_offset = match t.section.0 {
        1000 => 0,
        1001 => 1_000_000,
        1002 => 2_000_000,
        _ => panic!("unexpected section {:?}", t.section),
    };
    sec_offset + t.offset_mm
}

// ---------------------------------------------------------------------------
// O1: determinism. Identical inputs produce identical outputs.
// ---------------------------------------------------------------------------

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, .. ProptestConfig::default() })]

    #[test]
    fn o1_determinism(
        start_offset in 0i64..1_000_000,
        pulses in -2_000i32..2_000,
        dt_ns in 1_000_000u64..1_000_000_000,
        gnss_unc in 0u32..20_000,
        with_gnss in any::<bool>(),
        with_balise in any::<bool>(),
    ) {
        let n = net();
        let c = cal();
        let prev = init_at_offset(start_offset);
        let sensors = SensorTick {
            timestamp_ns: prev.last_timestamp_ns + dt_ns,
            wheel_pulses: pulses,
            gnss: if with_gnss {
                Some(GnssFix {
                    projected: TrackRef {
                        section: SectionId::new(1000),
                        offset_mm: start_offset / 2,
                        direction: Direction::Forward,
                    },
                    uncertainty_mm: gnss_unc,
                })
            } else { None },
            balise: if with_balise {
                Some(BaliseFix {
                    balise_id: BaliseId::new(1),
                    position: TrackRef {
                        section: SectionId::new(1001),
                        offset_mm: 500_000,
                        direction: Direction::Forward,
                    },
                    uncertainty_mm: 80,
                })
            } else { None },
        };
        let a = odom_step(&prev, &c, &sensors, &n);
        let b = odom_step(&prev, &c, &sensors, &n);
        prop_assert_eq!(a, b);
    }
}

// ---------------------------------------------------------------------------
// O2: forward non-regression — non-negative pulses, no balise/GNSS,
// same direction → head does not move backward on the linearised axis.
// ---------------------------------------------------------------------------

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, .. ProptestConfig::default() })]

    #[test]
    fn o2_forward_pulses_never_regress(
        start_offset in 0i64..1_500_000,
        pulses in 0i32..5_000,
        dt_ns in 1_000_000u64..1_000_000_000,
    ) {
        let n = net();
        let c = cal();
        // Place the prev state at linear position = start_offset,
        // which could be in section 1000 or 1001.
        let prev = if start_offset < 1_000_000 {
            init_at_offset(start_offset)
        } else {
            OdomState::new_at(
                TrainId::new(7),
                TrackRef {
                    section: SectionId::new(1001),
                    offset_mm: start_offset - 1_000_000,
                    direction: Direction::Forward,
                },
                50,
                0,
            )
        };
        let sensors = SensorTick {
            timestamp_ns: prev.last_timestamp_ns + dt_ns,
            wheel_pulses: pulses,
            gnss: None,
            balise: None,
        };
        let next = odom_step(&prev, &c, &sensors, &n);
        let lp_prev = linear_position_mm(prev.head);
        let lp_next = linear_position_mm(next.head);
        prop_assert!(lp_next >= lp_prev, "regression: {lp_prev} → {lp_next}");
    }
}

// ---------------------------------------------------------------------------
// O3: uncertainty monotone without fix. Without balise or tightening
// GNSS, position uncertainty never decreases.
// ---------------------------------------------------------------------------

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, .. ProptestConfig::default() })]

    #[test]
    fn o3_uncertainty_monotone_without_fix(
        start_offset in 0i64..900_000,
        pulses in 0i32..5_000,
        prev_unc in 50u32..10_000,
        dt_ns in 1_000_000u64..1_000_000_000,
    ) {
        let n = net();
        let c = cal();
        let mut prev = init_at_offset(start_offset);
        prev.position_uncertainty_mm = prev_unc;
        let sensors = SensorTick {
            timestamp_ns: prev.last_timestamp_ns + dt_ns,
            wheel_pulses: pulses,
            gnss: None,
            balise: None,
        };
        let next = odom_step(&prev, &c, &sensors, &n);
        prop_assert!(
            next.position_uncertainty_mm >= prev.position_uncertainty_mm
                || next.position_uncertainty_mm == c.max_uncertainty_mm,
            "uncertainty decreased: {} → {}",
            prev.position_uncertainty_mm, next.position_uncertainty_mm
        );
    }
}

// ---------------------------------------------------------------------------
// O4: a valid balise fix resets uncertainty to max(fix, min_floor),
// regardless of prior uncertainty.
// ---------------------------------------------------------------------------

proptest! {
    #![proptest_config(ProptestConfig { cases: 128, .. ProptestConfig::default() })]

    #[test]
    fn o4_balise_resets_uncertainty(
        prev_unc in 0u32..50_000,
        fix_unc in 0u32..500,
    ) {
        let n = net();
        let c = cal();
        let mut prev = init_at_offset(100_000);
        prev.position_uncertainty_mm = prev_unc;
        let sensors = SensorTick {
            timestamp_ns: prev.last_timestamp_ns + 1_000_000_000,
            wheel_pulses: 0,
            gnss: None,
            balise: Some(BaliseFix {
                balise_id: BaliseId::new(5),
                position: TrackRef {
                    section: SectionId::new(1001),
                    offset_mm: 100_000,
                    direction: Direction::Forward,
                },
                uncertainty_mm: fix_unc,
            }),
        };
        let next = odom_step(&prev, &c, &sensors, &n);
        prop_assert_eq!(next.position_uncertainty_mm, fix_unc.max(c.min_uncertainty_mm));
        prop_assert_eq!(next.contributing_source, PositionSource::Balise);
        prop_assert_eq!(
            next.head,
            TrackRef {
                section: SectionId::new(1001),
                offset_mm: 100_000,
                direction: Direction::Forward,
            }
        );
    }
}

// ---------------------------------------------------------------------------
// O5: GNSS correction is conservative. A GNSS fix whose reported
// uncertainty >= current uncertainty never changes position, never
// loosens uncertainty, and does not mark the source as Gnss.
// ---------------------------------------------------------------------------

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, .. ProptestConfig::default() })]

    #[test]
    fn o5_loose_gnss_ignored(
        start_offset in 0i64..900_000,
        prev_unc in 500u32..5_000,
        // Start from 50 mm: wider than the per-tick dead-reckoning
        // uncertainty growth (≈ `uncertainty_floor_per_tick_mm`),
        // so a fix with `prev_unc + extra` is unambiguously ≥
        // `dr_uncertainty_mm` after one tick of growth.
        gnss_unc_extra in 50u32..10_000,
    ) {
        let n = net();
        let c = cal();
        let mut prev = init_at_offset(start_offset);
        prev.position_uncertainty_mm = prev_unc;
        let sensors = SensorTick {
            timestamp_ns: prev.last_timestamp_ns + 1_000_000_000,
            wheel_pulses: 0,
            gnss: Some(GnssFix {
                projected: TrackRef {
                    section: SectionId::new(1001), // jumps forward
                    offset_mm: 900_000,
                    direction: Direction::Forward,
                },
                uncertainty_mm: prev_unc + gnss_unc_extra, // >= current
            }),
            balise: None,
        };
        let next = odom_step(&prev, &c, &sensors, &n);
        // Head stays near previous (wheel pulses = 0).
        prop_assert_eq!(next.head.section, SectionId::new(1000));
        prop_assert_eq!(next.contributing_source, PositionSource::WheelTachometer);
    }
}

// ---------------------------------------------------------------------------
// O5 continued: GNSS with strictly-tighter uncertainty is applied and
// tightens the reported uncertainty (never loosens).
// ---------------------------------------------------------------------------

proptest! {
    #![proptest_config(ProptestConfig { cases: 128, .. ProptestConfig::default() })]

    #[test]
    fn o5_tight_gnss_applies(
        start_offset in 0i64..900_000,
        prev_unc in 5_000u32..20_000,
        gnss_unc in 100u32..4_000,
    ) {
        let n = net();
        let c = cal();
        let mut prev = init_at_offset(start_offset);
        prev.position_uncertainty_mm = prev_unc;
        let sensors = SensorTick {
            timestamp_ns: prev.last_timestamp_ns + 1_000_000_000,
            wheel_pulses: 0,
            gnss: Some(GnssFix {
                projected: TrackRef {
                    section: SectionId::new(1000),
                    offset_mm: 500_000,
                    direction: Direction::Forward,
                },
                uncertainty_mm: gnss_unc,
            }),
            balise: None,
        };
        let next = odom_step(&prev, &c, &sensors, &n);
        prop_assert_eq!(next.head.offset_mm, 500_000);
        prop_assert_eq!(next.contributing_source, PositionSource::Gnss);
        prop_assert!(next.position_uncertainty_mm <= prev_unc);
    }
}

// ---------------------------------------------------------------------------
// Cross-crate smoke: the TrainState produced by odom_step can drive
// osr-atp to produce a sensible outcome. Useful as a regression
// against silent shape drift.
// ---------------------------------------------------------------------------

#[test]
fn cross_crate_odom_feeds_atp() {
    use osr_atp::atp_evaluate;
    use osr_core::ConsistDescriptor;
    use osr_interlocking::{MovementAuthority, MA_VALIDITY_WINDOW_NS};

    let n = net();
    let c = cal();
    let prev = init_at_offset(0);
    // 5 m/s for 1 s → 5 m along the track.
    let pulses = (c.pulses_per_meter as i32) * 5;
    let sensors = SensorTick {
        timestamp_ns: 1_000_000_000,
        wheel_pulses: pulses,
        gnss: None,
        balise: None,
    };
    let odom = odom_step(&prev, &c, &sensors, &n);
    let state = odom.to_train_state();
    let consist = ConsistDescriptor::reference_3car();
    let ma = MovementAuthority {
        train_id: TrainId::new(7),
        end: TrackRef {
            section: SectionId::new(1001),
            offset_mm: 1_000_000,
            direction: Direction::Forward,
        },
        applicable_restrictions: vec![],
        valid_until_ns: 1_000_000_000 + MA_VALIDITY_WINDOW_NS,
        derived_from_entry_id: None,
        has_known_position: true,
    };
    let out = atp_evaluate(&state, &ma, &consist, &n, 1_000_000_000);
    // 5 m/s well within envelope for ~2 km ahead.
    assert!(out.is_release(), "{out:?}");
}
