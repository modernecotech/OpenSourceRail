//! Core fusion step and track-advancement helper.
//!
//! See the crate-level docs for the fusion priority and safety
//! properties.

use osr_core::{Network, TrackRef};
use osr_interlocking::forward_chain;

use crate::sensors::{GnssFix, OdomCalibration, PositionSource, SensorTick};
use crate::state::OdomState;

/// Advance `from` forward along the track graph by `dist_mm`.
///
/// - `dist_mm > 0`: walk in `from.direction` using the forward-chain
///   helper, summing section lengths until the distance is consumed.
///   At a terminal (end of a non-ring line), clips at the last
///   section's far end — callers detect "clipped" by observing that
///   the returned [`TrackRef`] matches the terminal and the caller's
///   tracked distance was not fully consumed.
/// - `dist_mm == 0`: returns `from` unchanged.
/// - `dist_mm < 0`: simple backward roll *within the current section*
///   only. If the roll-back would cross the section boundary, the
///   result is clipped to `offset_mm = 0`. Full cross-section
///   backward walks are a v2 feature; in v1 deliberate reversing is
///   handled at a higher level by flipping `from.direction` before
///   rolling.
#[must_use]
pub fn advance_along_track(network: &Network, from: TrackRef, dist_mm: i64) -> TrackRef {
    if dist_mm == 0 {
        return from;
    }
    if dist_mm < 0 {
        let back = -dist_mm;
        let new_offset = from.offset_mm.saturating_sub(back);
        return TrackRef {
            section: from.section,
            offset_mm: new_offset.max(0),
            direction: from.direction,
        };
    }

    // Forward walk: use forward_chain to enumerate the reachable sections.
    // Budget: dist_mm itself is enough — forward_chain returns sections
    // whose cumulative length is <= budget, so we may need one more
    // section beyond that to find the section the distance lands in.
    // Pad the budget by the largest plausible section length (1 km)
    // to capture the landing section.
    let budget = dist_mm.saturating_add(10_000_000); // 10 km slack
    let chain = forward_chain(network, from, budget);
    if chain.is_empty() {
        return from;
    }

    let mut remaining = dist_mm;
    let first_sec = network.section(chain[0]);
    let first_len = first_sec.length_mm as i64;
    let first_avail = first_len.saturating_sub(from.offset_mm).max(0);

    if remaining <= first_avail {
        return TrackRef {
            section: chain[0],
            offset_mm: from.offset_mm + remaining,
            direction: from.direction,
        };
    }
    remaining -= first_avail;
    let mut last_section = chain[0];

    for sid in chain.iter().skip(1).copied() {
        let sec = network.section(sid);
        let sec_len = sec.length_mm as i64;
        if remaining <= sec_len {
            return TrackRef {
                section: sid,
                offset_mm: remaining,
                direction: from.direction,
            };
        }
        remaining -= sec_len;
        last_section = sid;
    }

    // Ran off the end (terminal) — clip at the far end of the last section.
    let last_len = network.section(last_section).length_mm as i64;
    TrackRef {
        section: last_section,
        offset_mm: last_len,
        direction: from.direction,
    }
}

/// One step of the sensor fusion.
///
/// Pure function. See [`crate`] docs for the fusion rules and safety
/// properties O1–O5.
#[must_use]
pub fn odom_step(
    prev: &OdomState,
    cal: &OdomCalibration,
    sensors: &SensorTick,
    network: &Network,
) -> OdomState {
    // --- 1. Wheel dead reckoning --------------------------------------------
    let dist_mm = pulses_to_mm(sensors.wheel_pulses, cal);
    let dt_ns = sensors.timestamp_ns.saturating_sub(prev.last_timestamp_ns);

    let wheel_position = advance_along_track(network, prev.head, dist_mm);

    let (new_speed_mmps, new_speed_uncertainty_mmps) =
        derive_speed(prev, dist_mm, dt_ns, cal);

    // Uncertainty after dead-reckoning only.
    let dr_uncertainty_mm = grow_uncertainty(prev.position_uncertainty_mm, dist_mm.unsigned_abs(), cal);

    // --- 2. GNSS soft correction --------------------------------------------
    let (after_gnss_pos, after_gnss_uncertainty_mm, after_gnss_src) = match sensors.gnss {
        Some(fix) if fix_is_tightening(fix.uncertainty_mm, dr_uncertainty_mm) => (
            apply_gnss(wheel_position, fix),
            fix.uncertainty_mm.max(cal.min_uncertainty_mm),
            PositionSource::Gnss,
        ),
        _ => (wheel_position, dr_uncertainty_mm, PositionSource::WheelTachometer),
    };

    // --- 3. Balise absolute fix ---------------------------------------------
    let (final_pos, final_uncertainty_mm, final_src, balise_consumed) = match sensors.balise {
        Some(fix) => (
            // Balise snaps to its surveyed position, preserving the
            // train's heading direction (balises are direction-agnostic
            // on a double-track line, but we carry the heading through
            // to keep the TrackRef consistent).
            TrackRef {
                section: fix.position.section,
                offset_mm: fix.position.offset_mm,
                direction: after_gnss_pos.direction,
            },
            fix.uncertainty_mm.max(cal.min_uncertainty_mm),
            PositionSource::Balise,
            Some(fix.balise_id),
        ),
        None => (
            after_gnss_pos,
            after_gnss_uncertainty_mm,
            after_gnss_src,
            prev.last_balise_id,
        ),
    };

    // Cap uncertainty.
    let final_uncertainty_mm = final_uncertainty_mm.min(cal.max_uncertainty_mm);

    OdomState {
        train_id: prev.train_id,
        head: final_pos,
        speed_mmps: new_speed_mmps,
        position_uncertainty_mm: final_uncertainty_mm,
        speed_uncertainty_mmps: new_speed_uncertainty_mmps,
        contributing_source: final_src,
        last_balise_id: balise_consumed,
        last_timestamp_ns: sensors.timestamp_ns.max(prev.last_timestamp_ns),
    }
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/// Integer pulse → signed distance in mm.
fn pulses_to_mm(pulses: i32, cal: &OdomCalibration) -> i64 {
    let ppm = i64::from(cal.pulses_per_meter.max(1));
    // Round toward zero — conservative, matches the "distance per
    // pulse is slightly smaller than physical" direction set by
    // from_wheel_spec's ceil rounding.
    i64::from(pulses).saturating_mul(1000) / ppm
}

/// Derive the new speed from the signed distance and elapsed time.
///
/// Returns `(speed_mmps, speed_uncertainty_mmps)`. Uncertainty
/// accounts for the one-pulse quantisation: a pulse either has or
/// hasn't crossed the encoder threshold at the sample instant.
fn derive_speed(
    prev: &OdomState,
    dist_mm: i64,
    dt_ns: u64,
    cal: &OdomCalibration,
) -> (i32, u32) {
    if dt_ns == 0 {
        // No time elapsed — keep the previous speed. Uncertainty is
        // "no information" so we preserve the previous uncertainty.
        return (prev.speed_mmps, prev.speed_uncertainty_mmps);
    }
    // mm/s = (mm * 1e9) / ns. Be careful with overflow: a pulse-derived
    // distance up to a few metres per tick × 1e9 ≤ 1e13, well inside i64.
    let v_mmps_i64 = (dist_mm.saturating_mul(1_000_000_000))
        .checked_div(dt_ns as i64)
        .unwrap_or(0);
    let v_mmps = i32::try_from(v_mmps_i64.clamp(i32::MIN as i64, i32::MAX as i64))
        .unwrap_or(if v_mmps_i64 < 0 { i32::MIN } else { i32::MAX });

    // One-pulse quantisation in mm/s.
    let one_pulse_mm = (1_000_u64 + u64::from(cal.pulses_per_meter) - 1)
        / u64::from(cal.pulses_per_meter.max(1));
    let quant_mmps = ((one_pulse_mm.saturating_mul(1_000_000_000)) / dt_ns.max(1)) as u32;

    // Add the wheel-slip term scaled by current speed magnitude.
    let slip_term = ((v_mmps.unsigned_abs() as u64).saturating_mul(u64::from(cal.wheel_slip_ppm))
        / 1_000_000) as u32;

    (v_mmps, quant_mmps.saturating_add(slip_term))
}

/// Grow position uncertainty by the wheel-slip fraction of the
/// distance travelled plus the per-tick floor.
fn grow_uncertainty(prev: u32, dist_mm: u64, cal: &OdomCalibration) -> u32 {
    let growth_mm =
        dist_mm.saturating_mul(u64::from(cal.wheel_slip_ppm)) / 1_000_000;
    prev.saturating_add(growth_mm as u32)
        .saturating_add(cal.uncertainty_floor_per_tick_mm)
        .max(cal.min_uncertainty_mm)
}

/// Decide whether a GNSS fix should overwrite the wheel-derived
/// position. Strict inequality — equality is not a tightening.
fn fix_is_tightening(fix_uncertainty_mm: u32, current_uncertainty_mm: u32) -> bool {
    fix_uncertainty_mm < current_uncertainty_mm
}

fn apply_gnss(dead_reckoned: TrackRef, fix: GnssFix) -> TrackRef {
    // v1 strategy: fully replace with the GNSS projection, preserving
    // heading direction. Future Kalman would weight the two estimates.
    TrackRef {
        section: fix.projected.section,
        offset_mm: fix.projected.offset_mm,
        direction: dead_reckoned.direction,
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::sensors::{BaliseFix, BaliseId};
    use osr_core::{Direction, Line, Section, SectionId, Station, StationId, TrainId};

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
            net.sections.insert(f, Section {
                id: f,
                from_station: StationId::new((i as u64) + 1),
                to_station: StationId::new((i as u64) + 2),
                length_mm: 1_000_000,
                max_speed_mps: 22.0,
            });
            net.sections.insert(r, Section {
                id: r,
                from_station: StationId::new((i as u64) + 2),
                to_station: StationId::new((i as u64) + 1),
                length_mm: 1_000_000,
                max_speed_mps: 22.0,
            });
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

    fn sec(id: u64, offset: i64) -> TrackRef {
        TrackRef {
            section: SectionId::new(id),
            offset_mm: offset,
            direction: Direction::Forward,
        }
    }

    fn init() -> OdomState {
        OdomState::new_at(TrainId::new(7), sec(1000, 0), 50, 0)
    }

    #[test]
    fn advance_within_section() {
        let n = net();
        assert_eq!(advance_along_track(&n, sec(1000, 100_000), 50_000), sec(1000, 150_000));
    }

    #[test]
    fn advance_crosses_section_boundary() {
        let n = net();
        // 100 m into section 1000, advance 950 m → 50 m into section 1001.
        assert_eq!(advance_along_track(&n, sec(1000, 100_000), 950_000), sec(1001, 50_000));
    }

    #[test]
    fn advance_clips_at_terminal() {
        let n = net();
        // Start at 500 m into section 1002 (last forward section),
        // advance 5 km. Clip at far end of 1002 (offset = 1_000_000).
        assert_eq!(advance_along_track(&n, sec(1002, 500_000), 5_000_000), sec(1002, 1_000_000));
    }

    #[test]
    fn advance_negative_within_section() {
        let n = net();
        assert_eq!(advance_along_track(&n, sec(1000, 100_000), -40_000), sec(1000, 60_000));
    }

    #[test]
    fn advance_negative_clipped_at_section_start() {
        let n = net();
        assert_eq!(advance_along_track(&n, sec(1000, 20_000), -50_000), sec(1000, 0));
    }

    #[test]
    fn wheel_only_advances_head() {
        let n = net();
        let cal = OdomCalibration::light_metro_default();
        let prev = init();
        // pulses_per_meter = 410 → 410 pulses = 1 m.
        let sensors = SensorTick {
            timestamp_ns: 1_000_000_000, // 1 second after t=0
            wheel_pulses: 4_100, // ~10 m
            gnss: None,
            balise: None,
        };
        let next = odom_step(&prev, &cal, &sensors, &n);
        assert_eq!(next.head.section, SectionId::new(1000));
        // 4100 pulses / 410 ppm = 10000 mm. Due to ceil rounding in
        // pulses_to_mm (toward zero), distance = 4100*1000/410 = 10000.
        assert_eq!(next.head.offset_mm, 10_000);
        assert_eq!(next.contributing_source, PositionSource::WheelTachometer);
        // Uncertainty grew but is floored at min.
        assert!(next.position_uncertainty_mm >= cal.min_uncertainty_mm);
    }

    #[test]
    fn balise_snaps_and_resets_uncertainty() {
        let n = net();
        let cal = OdomCalibration::light_metro_default();
        let mut prev = init();
        prev.position_uncertainty_mm = 10_000; // 10 m before fix
        let balise = BaliseFix {
            balise_id: BaliseId::new(42),
            position: sec(1001, 500_000),
            uncertainty_mm: 80,
        };
        let sensors = SensorTick {
            timestamp_ns: 1_000_000_000,
            wheel_pulses: 0,
            gnss: None,
            balise: Some(balise),
        };
        let next = odom_step(&prev, &cal, &sensors, &n);
        assert_eq!(next.head, sec(1001, 500_000));
        assert_eq!(next.position_uncertainty_mm, 80.max(cal.min_uncertainty_mm));
        assert_eq!(next.contributing_source, PositionSource::Balise);
        assert_eq!(next.last_balise_id, Some(BaliseId::new(42)));
    }

    #[test]
    fn gnss_tighter_applies_loose_ignored() {
        let n = net();
        let cal = OdomCalibration::light_metro_default();
        let mut prev = init();
        prev.position_uncertainty_mm = 5_000;

        // Tight GNSS: 2 m uncertainty → applies.
        let tight = SensorTick {
            timestamp_ns: 1_000_000_000,
            wheel_pulses: 0,
            gnss: Some(GnssFix {
                projected: sec(1000, 200_000),
                uncertainty_mm: 2_000,
            }),
            balise: None,
        };
        let next = odom_step(&prev, &cal, &tight, &n);
        assert_eq!(next.head, sec(1000, 200_000));
        assert_eq!(next.contributing_source, PositionSource::Gnss);
        assert_eq!(next.position_uncertainty_mm, 2_000);

        // Loose GNSS: 20 m > current 5 m → ignored.
        let loose = SensorTick {
            timestamp_ns: 1_000_000_000,
            wheel_pulses: 0,
            gnss: Some(GnssFix {
                projected: sec(1000, 200_000),
                uncertainty_mm: 20_000,
            }),
            balise: None,
        };
        let next = odom_step(&prev, &cal, &loose, &n);
        assert_eq!(next.head, sec(1000, 0)); // unchanged
        assert_eq!(next.contributing_source, PositionSource::WheelTachometer);
    }

    #[test]
    fn speed_from_pulses() {
        let n = net();
        let cal = OdomCalibration::light_metro_default();
        let prev = init();
        // 4100 pulses in 1 second → 10 m/s = 10_000 mm/s.
        let sensors = SensorTick {
            timestamp_ns: 1_000_000_000,
            wheel_pulses: 4_100,
            gnss: None,
            balise: None,
        };
        let next = odom_step(&prev, &cal, &sensors, &n);
        // Allow ±20 mm/s for one-pulse quantisation at this rate.
        assert!((9_980..=10_020).contains(&next.speed_mmps), "speed={}", next.speed_mmps);
    }

    #[test]
    fn determinism() {
        let n = net();
        let cal = OdomCalibration::light_metro_default();
        let prev = init();
        let sensors = SensorTick {
            timestamp_ns: 1_000_000_000,
            wheel_pulses: 2_050,
            gnss: None,
            balise: None,
        };
        let a = odom_step(&prev, &cal, &sensors, &n);
        let b = odom_step(&prev, &cal, &sensors, &n);
        assert_eq!(a, b);
    }
}
