//! OpenSourceRail onboard axle-bearing temperature monitor.
//!
//! Continuously watches the bearing temperature on each powered and
//! trailer axle, with a dual-sensor 2oo2 redundancy model like
//! [`osr_derailment`]. Not SIL-4 because the wayside HABD
//! ([`osr_hot_axle_wayside`] in RFC 0005 §4.6) provides the primary
//! trip signal; onboard detection is backup + maintenance-signalling.
//!
//! Phase 2c crate of [RFC 0005 §4.3](../../../docs/rfcs/0005-sbc-software-architecture.md).
//!
//! # Trip rules
//!
//! A per-axle `Trip` is asserted when **both** sensor channels are
//! valid AND either:
//! - any channel above `absolute_trip_dc` (tenths of °C), or
//! - channel temp − ambient > `differential_trip_dc`.
//!
//! A single-channel anomaly raises the axle to `Warning` only — the
//! sensor may be faulty.
//!
//! Sensor integrity: if either channel is `!valid`, the axle cannot
//! `Trip` from this tick's readings, and a `SensorInvalid` fault
//! bit is set in the axle's fault mask.
//!
//! # Properties
//!
//! - **HA1 determinism.**
//! - **HA2 trip is 2oo2:** `axle.state == Trip` ⇒ both channels
//!   `valid` and at least one breach condition on both channels.
//! - **HA3 invalid sensor blocks trip:** `!valid` on either channel
//!   ⇒ axle `state ∈ { Nominal, Warning }`.
//! - **HA4 any axle trip raises system-level emergency request
//!   to true** (advisory; wayside HABD is authoritative on the
//!   trip-to-emergency-brake path).
//! - **HA5 alarm monotone:** any fault raises axle alarm to at
//!   least `Warning`.

#![forbid(unsafe_code)]

use serde::{Deserialize, Serialize};

// ---------------------------------------------------------------------------
// Per-axle types
// ---------------------------------------------------------------------------

#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct AxleSensor {
    /// Temperature, tenths of °C.
    pub temp_dc: i16,
    /// `true` when the sensor is powered, responding, and passing
    /// self-test.
    pub valid: bool,
}

impl Default for AxleSensor {
    fn default() -> Self {
        Self {
            temp_dc: 250, // 25 °C
            valid: true,
        }
    }
}

#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct AxleReading {
    pub sensor_a: AxleSensor,
    pub sensor_b: AxleSensor,
}

impl Default for AxleReading {
    fn default() -> Self {
        Self {
            sensor_a: AxleSensor::default(),
            sensor_b: AxleSensor::default(),
        }
    }
}

#[derive(Copy, Clone, Debug, PartialEq, Eq, Hash, Default, Serialize, Deserialize)]
pub enum AxleAlarm {
    #[default]
    Nominal,
    Warning,
    Trip,
}

#[derive(Copy, Clone, Debug, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum AxleFault {
    AbsoluteExceedance = 0,
    DifferentialExceedance = 1,
    SingleChannelAnomaly = 2,
    SensorInvalid = 3,
}

#[derive(Copy, Clone, Debug, PartialEq, Eq, Default, Serialize, Deserialize)]
pub struct AxleFaultMask(pub u8);

impl AxleFaultMask {
    pub fn insert(&mut self, f: AxleFault) {
        self.0 |= 1u8 << (f as u8);
    }
    #[must_use]
    pub fn contains(self, f: AxleFault) -> bool {
        (self.0 >> (f as u8)) & 1 == 1
    }
    #[must_use]
    pub fn any(self) -> bool {
        self.0 != 0
    }
}

// ---------------------------------------------------------------------------
// Inputs / params / output
// ---------------------------------------------------------------------------

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct HotAxleInputs {
    pub now_ns: u64,
    pub ambient_dc: i16,
    pub axles: Vec<AxleReading>,
}

#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct HotAxleParams {
    /// Absolute bearing temperature at which a trip is asserted (dC).
    pub absolute_trip_dc: i16,
    pub absolute_warn_dc: i16,
    /// Differential over ambient for trip (dC).
    pub differential_trip_dc: i16,
    pub differential_warn_dc: i16,
}

impl HotAxleParams {
    #[must_use]
    pub fn default_metro() -> Self {
        Self {
            absolute_trip_dc: 1_000,   // 100 °C
            absolute_warn_dc: 750,     // 75 °C
            differential_trip_dc: 700, // 70 °C over ambient
            differential_warn_dc: 400, // 40 °C over ambient
        }
    }
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct HotAxleOutput {
    /// Per-axle alarm level, parallel to the input `axles` vec.
    pub axle_alarms: Vec<AxleAlarm>,
    /// Per-axle fault bitmasks, parallel to the input.
    pub axle_faults: Vec<AxleFaultMask>,
    /// Advisory emergency request (some axle tripped). Forwarded to
    /// the vehicle controller as a maintenance alarm; wayside HABD
    /// is the authoritative source for the brake-apply union.
    pub emergency_advisory: bool,
    /// Worst per-axle alarm level (nominal < warning < trip).
    pub worst_alarm: AxleAlarm,
}

// ---------------------------------------------------------------------------
// Evaluator
// ---------------------------------------------------------------------------

fn evaluate_axle(
    reading: &AxleReading,
    ambient_dc: i16,
    p: &HotAxleParams,
) -> (AxleAlarm, AxleFaultMask) {
    let mut faults = AxleFaultMask::default();

    let a_valid = reading.sensor_a.valid;
    let b_valid = reading.sensor_b.valid;
    let both_valid = a_valid && b_valid;

    if !both_valid {
        faults.insert(AxleFault::SensorInvalid);
    }

    let a_t = reading.sensor_a.temp_dc;
    let b_t = reading.sensor_b.temp_dc;

    let a_abs_trip = a_t >= p.absolute_trip_dc;
    let b_abs_trip = b_t >= p.absolute_trip_dc;
    let a_abs_warn = a_t >= p.absolute_warn_dc;
    let b_abs_warn = b_t >= p.absolute_warn_dc;

    let a_diff_trip = a_t.saturating_sub(ambient_dc) >= p.differential_trip_dc;
    let b_diff_trip = b_t.saturating_sub(ambient_dc) >= p.differential_trip_dc;
    let a_diff_warn = a_t.saturating_sub(ambient_dc) >= p.differential_warn_dc;
    let b_diff_warn = b_t.saturating_sub(ambient_dc) >= p.differential_warn_dc;

    let mut trip = false;
    if both_valid {
        if a_abs_trip && b_abs_trip {
            faults.insert(AxleFault::AbsoluteExceedance);
            trip = true;
        }
        if a_diff_trip && b_diff_trip {
            faults.insert(AxleFault::DifferentialExceedance);
            trip = true;
        }
    }

    // Single-channel anomaly (one above trip, the other not).
    let any_single_trip = (a_abs_trip ^ b_abs_trip) || (a_diff_trip ^ b_diff_trip);
    if any_single_trip && !trip {
        faults.insert(AxleFault::SingleChannelAnomaly);
    }

    // Warning-level rollup: any warn threshold crossed on either
    // channel (single-channel warn is still a warning).
    let any_warn = a_abs_warn || b_abs_warn || a_diff_warn || b_diff_warn;

    let alarm = if trip {
        AxleAlarm::Trip
    } else if any_warn || faults.any() {
        AxleAlarm::Warning
    } else {
        AxleAlarm::Nominal
    };

    (alarm, faults)
}

/// Evaluate one tick across all axles. Pure.
#[must_use]
pub fn hot_axle_evaluate(inputs: &HotAxleInputs, params: &HotAxleParams) -> HotAxleOutput {
    let mut alarms = Vec::with_capacity(inputs.axles.len());
    let mut faults = Vec::with_capacity(inputs.axles.len());
    let mut worst = AxleAlarm::Nominal;
    let mut any_trip = false;

    for r in &inputs.axles {
        let (alarm, fmask) = evaluate_axle(r, inputs.ambient_dc, params);
        if alarm == AxleAlarm::Trip {
            any_trip = true;
            worst = AxleAlarm::Trip;
        } else if alarm == AxleAlarm::Warning && worst == AxleAlarm::Nominal {
            worst = AxleAlarm::Warning;
        }
        alarms.push(alarm);
        faults.push(fmask);
    }

    HotAxleOutput {
        axle_alarms: alarms,
        axle_faults: faults,
        emergency_advisory: any_trip,
        worst_alarm: worst,
    }
}

// ---------------------------------------------------------------------------
// Unit tests
// ---------------------------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;

    fn four_axles_clean() -> HotAxleInputs {
        HotAxleInputs {
            now_ns: 0,
            ambient_dc: 250,
            axles: vec![AxleReading::default(); 4],
        }
    }

    #[test]
    fn all_cool_is_nominal() {
        let out = hot_axle_evaluate(&four_axles_clean(), &HotAxleParams::default_metro());
        assert_eq!(out.worst_alarm, AxleAlarm::Nominal);
        assert!(!out.emergency_advisory);
    }

    #[test]
    fn hot_axle_2oo2_trips() {
        let p = HotAxleParams::default_metro();
        let mut i = four_axles_clean();
        i.axles[2].sensor_a.temp_dc = 1_100;
        i.axles[2].sensor_b.temp_dc = 1_050;
        let out = hot_axle_evaluate(&i, &p);
        assert_eq!(out.axle_alarms[2], AxleAlarm::Trip);
        assert_eq!(out.worst_alarm, AxleAlarm::Trip);
        assert!(out.emergency_advisory);
        assert!(out.axle_faults[2].contains(AxleFault::AbsoluteExceedance));
    }

    #[test]
    fn single_channel_hot_warning_only() {
        let p = HotAxleParams::default_metro();
        let mut i = four_axles_clean();
        i.axles[1].sensor_a.temp_dc = 1_100;
        // sensor_b stays cool
        let out = hot_axle_evaluate(&i, &p);
        assert_eq!(out.axle_alarms[1], AxleAlarm::Warning);
        assert!(out.axle_faults[1].contains(AxleFault::SingleChannelAnomaly));
        assert!(!out.emergency_advisory);
    }

    #[test]
    fn invalid_sensor_blocks_trip() {
        let p = HotAxleParams::default_metro();
        let mut i = four_axles_clean();
        i.axles[0].sensor_a.temp_dc = 1_100;
        i.axles[0].sensor_b.temp_dc = 1_100;
        i.axles[0].sensor_b.valid = false;
        let out = hot_axle_evaluate(&i, &p);
        assert_ne!(out.axle_alarms[0], AxleAlarm::Trip);
        assert!(out.axle_faults[0].contains(AxleFault::SensorInvalid));
    }

    #[test]
    fn differential_2oo2_trips() {
        let p = HotAxleParams::default_metro();
        let mut i = four_axles_clean();
        i.ambient_dc = 200;
        // 90 °C > 70 °C differential trip
        i.axles[3].sensor_a.temp_dc = 1_100;
        i.axles[3].sensor_b.temp_dc = 1_100;
        let out = hot_axle_evaluate(&i, &p);
        assert_eq!(out.axle_alarms[3], AxleAlarm::Trip);
        assert!(out.axle_faults[3].contains(AxleFault::DifferentialExceedance));
    }

    #[test]
    fn warning_level() {
        let p = HotAxleParams::default_metro();
        let mut i = four_axles_clean();
        // 80 °C: above warn (75) but below trip (100)
        i.axles[0].sensor_a.temp_dc = 800;
        i.axles[0].sensor_b.temp_dc = 800;
        let out = hot_axle_evaluate(&i, &p);
        assert_eq!(out.axle_alarms[0], AxleAlarm::Warning);
    }

    #[test]
    fn worst_rolls_up() {
        let p = HotAxleParams::default_metro();
        let mut i = four_axles_clean();
        i.axles[0].sensor_a.temp_dc = 800; // Warning
        i.axles[0].sensor_b.temp_dc = 800;
        i.axles[3].sensor_a.temp_dc = 1_100; // Trip
        i.axles[3].sensor_b.temp_dc = 1_100;
        let out = hot_axle_evaluate(&i, &p);
        assert_eq!(out.worst_alarm, AxleAlarm::Trip);
    }

    #[test]
    fn determinism() {
        let p = HotAxleParams::default_metro();
        let mut i = four_axles_clean();
        i.axles[2].sensor_a.temp_dc = 700;
        let a = hot_axle_evaluate(&i, &p);
        let b = hot_axle_evaluate(&i, &p);
        assert_eq!(a, b);
    }
}
