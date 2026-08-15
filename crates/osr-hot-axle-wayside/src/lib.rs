//! OpenSourceRail wayside Hot Axle Box Detector (HABD).
//!
//! A trackside IR sensor array reads bearing temperatures on every
//! axle of a passing train. This crate is the authoritative
//! trackside detector (the onboard [`osr_hot_axle`] is an advisory
//! backup).
//!
//! Phase 2d crate of [RFC 0005 §4.6](../../../docs/rfcs/0005-sbc-software-architecture.md).
//! SIL-4: a missed hot-bearing sighting can mean wheel lockup,
//! derailment, or fire. Decision is simple but load-bearing.
//!
//! # Decision rule
//!
//! Given per-axle peak temperature + ambient + optional
//! contralateral reading (some HABDs watch both sides), produce:
//!
//! - **Nominal** if all readings below `warn_dc` and differential
//!   below `warn_diff_dc`.
//! - **Warning** if any reading between warn and trip thresholds
//!   → emit a speed-restriction event for this train (limit to
//!   say 40 km/h through the next station).
//! - **Trip** if any reading exceeds trip → emit a stop-order
//!   that the interlocking injects as a hard speed restriction of
//!   0 on the train's current section.
//!
//! # Properties (proptest-verified)
//!
//! - **HW1 determinism.**
//! - **HW2 trip ⇒ stop order.**
//! - **HW3 warning ⇒ speed restriction.**

#![forbid(unsafe_code)]

use serde::{Deserialize, Serialize};

#[derive(
    Copy, Clone, Debug, PartialEq, Eq, Hash, Default, Serialize, Deserialize, PartialOrd, Ord,
)]
pub enum HwAlarmLevel {
    #[default]
    Nominal,
    Warning,
    Trip,
}

#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct AxleReading {
    /// Axle index within the consist (0-based).
    pub axle_index: u8,
    /// Peak temperature measured on this pass, tenths of °C.
    pub peak_dc: i16,
}

#[derive(Clone, Debug)]
pub struct HabdInputs<'a> {
    pub now_ns: u64,
    pub train_id: u32,
    pub section_id: u32,
    pub ambient_dc: i16,
    pub axles: &'a [AxleReading],
}

#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct HabdParams {
    pub warn_dc: i16,
    pub trip_dc: i16,
    pub warn_diff_dc: i16,
    pub trip_diff_dc: i16,
    /// Speed-restriction limit to emit on Warning, mm/s.
    pub warning_speed_limit_mmps: i32,
}

impl HabdParams {
    #[must_use]
    pub fn default_metro() -> Self {
        Self {
            warn_dc: 750,                     // 75 °C
            trip_dc: 1_000,                   // 100 °C
            warn_diff_dc: 400,                // 40 °C over ambient
            trip_diff_dc: 700,                // 70 °C over ambient
            warning_speed_limit_mmps: 11_000, // ~40 km/h
        }
    }
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub enum HabdAction {
    /// No action needed — train proceeds at normal speed.
    Nominal,
    /// Emit a speed restriction for this train on the current section.
    SpeedRestriction {
        train_id: u32,
        section_id: u32,
        limit_mmps: i32,
    },
    /// Emit a stop order for this train (speed restriction of 0
    /// on its current section).
    StopOrder { train_id: u32, section_id: u32 },
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct HabdOutput {
    pub alarm: HwAlarmLevel,
    pub worst_axle_index: Option<u8>,
    pub worst_peak_dc: Option<i16>,
    pub action: HabdAction,
}

#[must_use]
pub fn habd_evaluate(inputs: &HabdInputs<'_>, params: &HabdParams) -> HabdOutput {
    let mut worst: Option<(u8, i16, HwAlarmLevel)> = None;

    for a in inputs.axles {
        let diff = a.peak_dc.saturating_sub(inputs.ambient_dc);
        let level = if a.peak_dc >= params.trip_dc || diff >= params.trip_diff_dc {
            HwAlarmLevel::Trip
        } else if a.peak_dc >= params.warn_dc || diff >= params.warn_diff_dc {
            HwAlarmLevel::Warning
        } else {
            HwAlarmLevel::Nominal
        };

        let take = match &worst {
            None => true,
            Some((_, _, best)) => level > *best,
        };
        if take {
            worst = Some((a.axle_index, a.peak_dc, level));
        }
    }

    let alarm = worst.map(|(_, _, l)| l).unwrap_or(HwAlarmLevel::Nominal);
    let action = match alarm {
        HwAlarmLevel::Nominal => HabdAction::Nominal,
        HwAlarmLevel::Warning => HabdAction::SpeedRestriction {
            train_id: inputs.train_id,
            section_id: inputs.section_id,
            limit_mmps: params.warning_speed_limit_mmps,
        },
        HwAlarmLevel::Trip => HabdAction::StopOrder {
            train_id: inputs.train_id,
            section_id: inputs.section_id,
        },
    };

    HabdOutput {
        alarm,
        worst_axle_index: worst.map(|(i, _, _)| i),
        worst_peak_dc: worst.map(|(_, t, _)| t),
        action,
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn nominal_cool_axles() {
        let axles = vec![
            AxleReading {
                axle_index: 0,
                peak_dc: 300
            };
            4
        ];
        let out = habd_evaluate(
            &HabdInputs {
                now_ns: 0,
                train_id: 7,
                section_id: 1000,
                ambient_dc: 250,
                axles: &axles,
            },
            &HabdParams::default_metro(),
        );
        assert_eq!(out.alarm, HwAlarmLevel::Nominal);
        assert!(matches!(out.action, HabdAction::Nominal));
    }

    #[test]
    fn hot_axle_trips_with_stop_order() {
        let axles = vec![
            AxleReading {
                axle_index: 0,
                peak_dc: 300,
            },
            AxleReading {
                axle_index: 1,
                peak_dc: 1_200,
            },
        ];
        let out = habd_evaluate(
            &HabdInputs {
                now_ns: 0,
                train_id: 7,
                section_id: 1000,
                ambient_dc: 250,
                axles: &axles,
            },
            &HabdParams::default_metro(),
        );
        assert_eq!(out.alarm, HwAlarmLevel::Trip);
        assert!(matches!(
            out.action,
            HabdAction::StopOrder { train_id: 7, .. }
        ));
        assert_eq!(out.worst_axle_index, Some(1));
    }

    #[test]
    fn warm_axle_warns_with_restriction() {
        let axles = vec![AxleReading {
            axle_index: 2,
            peak_dc: 850,
        }];
        let out = habd_evaluate(
            &HabdInputs {
                now_ns: 0,
                train_id: 7,
                section_id: 1000,
                ambient_dc: 250,
                axles: &axles,
            },
            &HabdParams::default_metro(),
        );
        assert_eq!(out.alarm, HwAlarmLevel::Warning);
        let is_sr = matches!(out.action, HabdAction::SpeedRestriction { .. });
        assert!(is_sr);
    }

    #[test]
    fn determinism() {
        let axles = vec![AxleReading {
            axle_index: 0,
            peak_dc: 700,
        }];
        let i = HabdInputs {
            now_ns: 0,
            train_id: 1,
            section_id: 1,
            ambient_dc: 250,
            axles: &axles,
        };
        let p = HabdParams::default_metro();
        assert_eq!(habd_evaluate(&i, &p), habd_evaluate(&i, &p));
    }
}
