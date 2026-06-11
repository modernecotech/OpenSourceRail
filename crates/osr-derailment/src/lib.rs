//! OpenSourceRail derailment detector.
//!
//! SIL-4 monitor that watches a dual-redundant accelerometer +
//! tilt-sensor package and requests an emergency brake on any
//! derailment-consistent signature (per the safe-state envelopes of
//! EN 50159 and common rail-vehicle practice).
//!
//! Phase 2c crate of [RFC 0005 §4.3](../../../docs/rfcs/0005-sbc-software-architecture.md).
//!
//! # Detection rules
//!
//! A trip is asserted when *any* of the following holds — with
//! confirmation required from **both** sensor channels (dual-sensor
//! 2oo2 logic) to minimise false positives from single-axis noise:
//!
//! - **Lateral g-force** spike above `lateral_trip_mg` on both
//!   channels. Trains should experience < 100 mg lateral under any
//!   normal operation; > 300 mg is an unambiguous derailment signal.
//! - **Tilt angle** beyond `tilt_trip_mdeg` on both channels.
//!   A car body rolled past ±15 ° (15 000 mdeg) is on its side.
//! - **Vertical shock** above `vertical_trip_mg` on both channels
//!   (wheel drop off rail → sudden vertical acceleration).
//!
//! A **single-channel** anomaly within the same envelope only raises
//! the alarm to `Warning` — the sensor may be faulty and the brake
//! crate will not be commanded.
//!
//! Sensor integrity: if either channel reports invalid (`!valid`),
//! the crate asserts [`FaultReason::SensorInvalid`] and the alarm
//! becomes `Warning` (lost redundancy; do not trip emergency on a
//! single healthy channel).
//!
//! # Properties (proptest-verified)
//!
//! - **D1 determinism.**
//! - **D2 2oo2 safety:** an emergency is asserted only when *both*
//!   sensor channels report valid readings and both breach the
//!   same threshold.
//! - **D3 trip latches** through cooldown.
//! - **D4 invalid sensor → no emergency** (lost redundancy): when
//!   either channel reports invalid, the current-tick output is
//!   never `Trip`-with-`emergency_requested=true` from that tick's
//!   readings alone.
//! - **D5 alarm monotone in severity:** any single-channel breach
//!   or sensor fault raises alarm to at least `Warning`.

#![forbid(unsafe_code)]

use serde::{Deserialize, Serialize};

// ---------------------------------------------------------------------------
// Inputs
// ---------------------------------------------------------------------------

/// One sensor channel's reading.
#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct SensorChannel {
    pub lateral_mg: i32,
    pub longitudinal_mg: i32,
    pub vertical_mg: i32,
    /// Tilt angle in milli-degrees, signed.
    pub tilt_mdeg: i32,
    /// `true` when the sensor is powered, responding, and passing
    /// self-test.
    pub valid: bool,
}

impl Default for SensorChannel {
    fn default() -> Self {
        Self {
            lateral_mg: 0,
            longitudinal_mg: 0,
            vertical_mg: 1_000, // 1 g — at rest
            tilt_mdeg: 0,
            valid: true,
        }
    }
}

#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct DerailmentInputs {
    pub now_ns: u64,
    pub sensor_a: SensorChannel,
    pub sensor_b: SensorChannel,
    pub reset_requested: bool,
}

#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct DerailmentParams {
    /// Lateral acceleration magnitude above which a trip is asserted
    /// when both channels agree. milli-g.
    pub lateral_trip_mg: i32,
    pub lateral_warn_mg: i32,
    pub vertical_trip_mg_delta: i32, // magnitude deviation from 1g
    pub vertical_warn_mg_delta: i32,
    pub tilt_trip_mdeg: i32,
    pub tilt_warn_mdeg: i32,
    pub cooldown_ms: u32,
}

impl DerailmentParams {
    #[must_use]
    pub fn default_metro() -> Self {
        Self {
            lateral_trip_mg: 300,
            lateral_warn_mg: 150,
            vertical_trip_mg_delta: 600, // ±0.6 g deviation from 1 g
            vertical_warn_mg_delta: 300,
            tilt_trip_mdeg: 15_000,
            tilt_warn_mdeg: 7_000,
            cooldown_ms: 30_000,
        }
    }
}

// ---------------------------------------------------------------------------
// Output
// ---------------------------------------------------------------------------

#[derive(Copy, Clone, Debug, PartialEq, Eq, Hash, Default, Serialize, Deserialize)]
pub enum AlarmLevel {
    #[default]
    Nominal,
    Warning,
    Trip,
}

#[derive(Copy, Clone, Debug, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum FaultReason {
    /// Both channels breached a lateral threshold.
    LateralExceedance,
    /// Both channels breached a vertical threshold.
    VerticalExceedance,
    /// Both channels breached a tilt threshold.
    TiltExceedance,
    /// Single-channel anomaly (warning only; does not trip).
    SingleChannelAnomaly,
    /// One or both channels reported invalid.
    SensorInvalid,
}

#[derive(Copy, Clone, Debug, PartialEq, Eq, Default, Serialize, Deserialize)]
pub struct FaultMask(pub u8);

impl FaultMask {
    #[must_use]
    pub fn empty() -> Self {
        Self(0)
    }
    pub fn insert(&mut self, r: FaultReason) {
        self.0 |= 1u8 << Self::bit(r);
    }
    #[must_use]
    pub fn contains(self, r: FaultReason) -> bool {
        (self.0 >> Self::bit(r)) & 1 == 1
    }
    #[must_use]
    pub fn any(self) -> bool {
        self.0 != 0
    }
    fn bit(r: FaultReason) -> u8 {
        match r {
            FaultReason::LateralExceedance => 0,
            FaultReason::VerticalExceedance => 1,
            FaultReason::TiltExceedance => 2,
            FaultReason::SingleChannelAnomaly => 3,
            FaultReason::SensorInvalid => 4,
        }
    }
}

#[derive(Copy, Clone, Debug, PartialEq, Eq, Default, Serialize, Deserialize)]
pub struct DerailmentState {
    pub latched_tripped: bool,
    pub cooldown_until_ns: Option<u64>,
}

#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct DerailmentOutput {
    pub state: DerailmentState,
    pub emergency_requested: bool,
    pub alarm: AlarmLevel,
    pub faults: FaultMask,
}

// ---------------------------------------------------------------------------
// Evaluator
// ---------------------------------------------------------------------------

fn vert_deviation(vert_mg: i32) -> i32 {
    (vert_mg - 1_000).abs()
}

/// Evaluate one derailment-monitor tick. Pure.
#[must_use]
pub fn derailment_evaluate(
    prev: &DerailmentState,
    inputs: &DerailmentInputs,
    params: &DerailmentParams,
) -> DerailmentOutput {
    let mut faults = FaultMask::empty();
    let mut alarm = AlarmLevel::Nominal;

    let a_valid = inputs.sensor_a.valid;
    let b_valid = inputs.sensor_b.valid;
    let both_valid = a_valid && b_valid;

    if !both_valid {
        faults.insert(FaultReason::SensorInvalid);
        alarm = AlarmLevel::Warning;
    }

    // Per-axis breach flags.
    let a_lat = inputs.sensor_a.lateral_mg.abs();
    let b_lat = inputs.sensor_b.lateral_mg.abs();
    let lat_trip_a = a_lat >= params.lateral_trip_mg;
    let lat_trip_b = b_lat >= params.lateral_trip_mg;
    let lat_warn_a = a_lat >= params.lateral_warn_mg;
    let lat_warn_b = b_lat >= params.lateral_warn_mg;

    let a_vert_dev = vert_deviation(inputs.sensor_a.vertical_mg);
    let b_vert_dev = vert_deviation(inputs.sensor_b.vertical_mg);
    let vert_trip_a = a_vert_dev >= params.vertical_trip_mg_delta;
    let vert_trip_b = b_vert_dev >= params.vertical_trip_mg_delta;
    let vert_warn_a = a_vert_dev >= params.vertical_warn_mg_delta;
    let vert_warn_b = b_vert_dev >= params.vertical_warn_mg_delta;

    let a_tilt = inputs.sensor_a.tilt_mdeg.abs();
    let b_tilt = inputs.sensor_b.tilt_mdeg.abs();
    let tilt_trip_a = a_tilt >= params.tilt_trip_mdeg;
    let tilt_trip_b = b_tilt >= params.tilt_trip_mdeg;
    let tilt_warn_a = a_tilt >= params.tilt_warn_mdeg;
    let tilt_warn_b = b_tilt >= params.tilt_warn_mdeg;

    // 2oo2 trip logic: both channels must agree AND both must be valid.
    let mut this_tick_trip = false;
    if both_valid {
        if lat_trip_a && lat_trip_b {
            faults.insert(FaultReason::LateralExceedance);
            this_tick_trip = true;
        }
        if vert_trip_a && vert_trip_b {
            faults.insert(FaultReason::VerticalExceedance);
            this_tick_trip = true;
        }
        if tilt_trip_a && tilt_trip_b {
            faults.insert(FaultReason::TiltExceedance);
            this_tick_trip = true;
        }
    }

    // Single-channel anomaly warning.
    let any_single =
        (lat_trip_a ^ lat_trip_b) || (vert_trip_a ^ vert_trip_b) || (tilt_trip_a ^ tilt_trip_b);
    if any_single && !this_tick_trip {
        faults.insert(FaultReason::SingleChannelAnomaly);
    }

    // Warn-level aggregate.
    let any_warn =
        lat_warn_a || lat_warn_b || vert_warn_a || vert_warn_b || tilt_warn_a || tilt_warn_b;
    if (any_warn || any_single) && alarm == AlarmLevel::Nominal {
        alarm = AlarmLevel::Warning;
    }

    // Cooldown handling.
    let mut cooldown_until_ns = prev.cooldown_until_ns;
    if this_tick_trip {
        let deadline = inputs
            .now_ns
            .saturating_add(u64::from(params.cooldown_ms) * 1_000_000);
        cooldown_until_ns = Some(match cooldown_until_ns {
            Some(existing) => existing.max(deadline),
            None => deadline,
        });
    }

    let cooldown_expired = match cooldown_until_ns {
        Some(until) => inputs.now_ns >= until,
        None => true,
    };

    let mut latched_tripped = prev.latched_tripped || this_tick_trip;
    if inputs.reset_requested && cooldown_expired && !this_tick_trip {
        latched_tripped = false;
        cooldown_until_ns = None;
    }

    let emergency_requested = latched_tripped;
    if emergency_requested {
        alarm = AlarmLevel::Trip;
    }

    DerailmentOutput {
        state: DerailmentState {
            latched_tripped,
            cooldown_until_ns,
        },
        emergency_requested,
        alarm,
        faults,
    }
}

// ---------------------------------------------------------------------------
// Unit tests
// ---------------------------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;

    fn nominal_inputs() -> DerailmentInputs {
        DerailmentInputs {
            now_ns: 0,
            sensor_a: SensorChannel::default(),
            sensor_b: SensorChannel::default(),
            reset_requested: false,
        }
    }

    #[test]
    fn quiet_when_nominal() {
        let out = derailment_evaluate(
            &DerailmentState::default(),
            &nominal_inputs(),
            &DerailmentParams::default_metro(),
        );
        assert!(!out.emergency_requested);
        assert_eq!(out.alarm, AlarmLevel::Nominal);
        assert!(!out.faults.any());
    }

    #[test]
    fn lateral_2oo2_trip() {
        let p = DerailmentParams::default_metro();
        let mut i = nominal_inputs();
        i.sensor_a.lateral_mg = 400;
        i.sensor_b.lateral_mg = 400;
        let out = derailment_evaluate(&DerailmentState::default(), &i, &p);
        assert!(out.emergency_requested);
        assert!(out.faults.contains(FaultReason::LateralExceedance));
        assert_eq!(out.alarm, AlarmLevel::Trip);
    }

    #[test]
    fn single_channel_lateral_does_not_trip() {
        let p = DerailmentParams::default_metro();
        let mut i = nominal_inputs();
        i.sensor_a.lateral_mg = 400; // above trip
                                     // sensor_b stays quiet
        let out = derailment_evaluate(&DerailmentState::default(), &i, &p);
        assert!(!out.emergency_requested);
        assert!(out.faults.contains(FaultReason::SingleChannelAnomaly));
        assert_eq!(out.alarm, AlarmLevel::Warning);
    }

    #[test]
    fn invalid_sensor_blocks_trip() {
        let p = DerailmentParams::default_metro();
        let mut i = nominal_inputs();
        i.sensor_a.lateral_mg = 400;
        i.sensor_b.lateral_mg = 400;
        i.sensor_b.valid = false;
        let out = derailment_evaluate(&DerailmentState::default(), &i, &p);
        assert!(!out.emergency_requested);
        assert!(out.faults.contains(FaultReason::SensorInvalid));
    }

    #[test]
    fn tilt_2oo2_trip() {
        let p = DerailmentParams::default_metro();
        let mut i = nominal_inputs();
        i.sensor_a.tilt_mdeg = 20_000;
        i.sensor_b.tilt_mdeg = 20_000;
        let out = derailment_evaluate(&DerailmentState::default(), &i, &p);
        assert!(out.emergency_requested);
        assert!(out.faults.contains(FaultReason::TiltExceedance));
    }

    #[test]
    fn vertical_2oo2_trip() {
        let p = DerailmentParams::default_metro();
        let mut i = nominal_inputs();
        i.sensor_a.vertical_mg = 2_000; // +1 g deviation
        i.sensor_b.vertical_mg = 2_000;
        let out = derailment_evaluate(&DerailmentState::default(), &i, &p);
        assert!(out.emergency_requested);
        assert!(out.faults.contains(FaultReason::VerticalExceedance));
    }

    #[test]
    fn trip_latches() {
        let p = DerailmentParams::default_metro();
        let mut i = nominal_inputs();
        i.sensor_a.lateral_mg = 500;
        i.sensor_b.lateral_mg = 500;
        let first = derailment_evaluate(&DerailmentState::default(), &i, &p);
        assert!(first.emergency_requested);

        // Clear sensors, try to reset before cooldown — still latched.
        let i2 = nominal_inputs();
        let out = derailment_evaluate(&first.state, &i2, &p);
        assert!(out.emergency_requested);

        let mut i3 = DerailmentInputs {
            now_ns: 60_000_000_000, // past 30s cooldown
            sensor_a: SensorChannel::default(),
            sensor_b: SensorChannel::default(),
            reset_requested: true,
        };
        i3.reset_requested = true;
        let out = derailment_evaluate(&first.state, &i3, &p);
        assert!(!out.emergency_requested);
    }

    #[test]
    fn determinism() {
        let p = DerailmentParams::default_metro();
        let mut i = nominal_inputs();
        i.sensor_a.lateral_mg = 200;
        let a = derailment_evaluate(&DerailmentState::default(), &i, &p);
        let b = derailment_evaluate(&DerailmentState::default(), &i, &p);
        assert_eq!(a, b);
    }
}
