//! OpenSourceRail onboard Condition-Based Monitoring (CBM) sampler.
//!
//! Per-tick evaluator that takes sensor readings from the bogies and
//! traction chain and produces:
//!
//! 1. A typed [`CbmSample`] for the stream that `osr-cbm-backend`
//!    consumes over TRG.
//! 2. Per-component [`ComponentHealth`] flags (Nominal / Watch /
//!    Service) — an at-a-glance summary for the OCC console and a
//!    trigger for local de-rating decisions (e.g. reduce brake
//!    effort on a worn pad even before the back office sees it).
//!
//! Phase 2b crate of [RFC 0005 §4.4](../../../docs/rfcs/0005-sbc-software-architecture.md).
//! SIL-0: purely advisory; a missed sample just shows up as a gap in
//! the depot-side trend. Real maintenance decisions are the
//! back-office crate's job (`osr-cbm-backend`).
//!
//! # Covered components
//!
//! | Component | Sensor | Unit |
//! |---|---|---|
//! | Axle bearing | accel RMS | mm/s × 1000 (ppt-ish) |
//! | Traction motor | NTC / PT100 | tenths of °C |
//! | Brake pad | wear sensor | ppt remaining (1000 = new) |
//! | Wheel tread | accel-based profile / gauge | ppt remaining |
//!
//! # Properties (proptest-verified)
//!
//! - **CB1 determinism.**
//! - **CB2 health monotone in severity:** better sensor readings
//!   cannot produce a worse health flag.
//! - **CB3 Service iff any component exceeds its Service threshold.**

#![forbid(unsafe_code)]

use serde::{Deserialize, Serialize};

/// Per-axle / per-motor / per-car reading set for one tick.
#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct CbmInputs {
    pub now_ns: u64,
    pub train_id: u32,
    /// Bearing vibration per axle, mm/s × 1000 (i.e. thousandths of mm/s).
    pub bearing_vib_ppt: Vec<u32>,
    /// Traction-motor temperatures, tenths of °C.
    pub motor_temp_dc: Vec<i16>,
    /// Brake-pad wear per car, ppt remaining (0 = gone, 1000 = new).
    pub brake_pad_remaining_ppt: Vec<u16>,
    /// Wheel-tread remaining wear, ppt remaining per wheelset.
    pub wheel_tread_remaining_ppt: Vec<u16>,
}

#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct CbmParams {
    pub bearing_watch_ppt: u32,
    pub bearing_service_ppt: u32,
    pub motor_watch_dc: i16,
    pub motor_service_dc: i16,
    pub brake_pad_watch_ppt: u16,
    pub brake_pad_service_ppt: u16,
    pub wheel_watch_ppt: u16,
    pub wheel_service_ppt: u16,
}

impl CbmParams {
    #[must_use]
    pub fn default_metro() -> Self {
        Self {
            // Bearing RMS: ISO 10816 style. 4 mm/s = watch, 7 mm/s = service.
            bearing_watch_ppt: 4_000,
            bearing_service_ppt: 7_000,
            motor_watch_dc: 1_400,      // 140 °C
            motor_service_dc: 1_600,    // 160 °C
            brake_pad_watch_ppt: 300,   // 30 % remaining = watch
            brake_pad_service_ppt: 150, // 15 % remaining = service
            wheel_watch_ppt: 300,
            wheel_service_ppt: 150,
        }
    }
}

#[derive(
    Copy, Clone, Debug, PartialEq, Eq, Hash, Default, PartialOrd, Ord, Serialize, Deserialize,
)]
pub enum ComponentHealth {
    #[default]
    Nominal,
    Watch,
    Service,
}

#[derive(Copy, Clone, Debug, PartialEq, Eq, Hash, PartialOrd, Ord, Serialize, Deserialize)]
pub enum Component {
    Bearing,
    Motor,
    BrakePad,
    WheelTread,
}

#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct ComponentFlag {
    pub component: Component,
    pub index: u16,
    pub health: ComponentHealth,
}

/// Streamed to `osr-cbm-backend` — carries the raw readings plus the
/// worst-case health flag for quick filtering.
#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct CbmSample {
    pub now_ns: u64,
    pub train_id: u32,
    pub bearing_vib_ppt: Vec<u32>,
    pub motor_temp_dc: Vec<i16>,
    pub brake_pad_remaining_ppt: Vec<u16>,
    pub wheel_tread_remaining_ppt: Vec<u16>,
    pub worst_health: ComponentHealth,
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct CbmOutput {
    pub sample: CbmSample,
    pub flags: Vec<ComponentFlag>,
}

#[must_use]
pub fn cbm_evaluate(inputs: &CbmInputs, params: &CbmParams) -> CbmOutput {
    let mut flags: Vec<ComponentFlag> = Vec::new();

    for (i, &v) in inputs.bearing_vib_ppt.iter().enumerate() {
        let h = if v >= params.bearing_service_ppt {
            ComponentHealth::Service
        } else if v >= params.bearing_watch_ppt {
            ComponentHealth::Watch
        } else {
            ComponentHealth::Nominal
        };
        if h != ComponentHealth::Nominal {
            flags.push(ComponentFlag {
                component: Component::Bearing,
                index: i as u16,
                health: h,
            });
        }
    }
    for (i, &t) in inputs.motor_temp_dc.iter().enumerate() {
        let h = if t >= params.motor_service_dc {
            ComponentHealth::Service
        } else if t >= params.motor_watch_dc {
            ComponentHealth::Watch
        } else {
            ComponentHealth::Nominal
        };
        if h != ComponentHealth::Nominal {
            flags.push(ComponentFlag {
                component: Component::Motor,
                index: i as u16,
                health: h,
            });
        }
    }
    for (i, &w) in inputs.brake_pad_remaining_ppt.iter().enumerate() {
        // Thresholds are phrased as *remaining*, so lower = worse.
        let h = if w <= params.brake_pad_service_ppt {
            ComponentHealth::Service
        } else if w <= params.brake_pad_watch_ppt {
            ComponentHealth::Watch
        } else {
            ComponentHealth::Nominal
        };
        if h != ComponentHealth::Nominal {
            flags.push(ComponentFlag {
                component: Component::BrakePad,
                index: i as u16,
                health: h,
            });
        }
    }
    for (i, &w) in inputs.wheel_tread_remaining_ppt.iter().enumerate() {
        let h = if w <= params.wheel_service_ppt {
            ComponentHealth::Service
        } else if w <= params.wheel_watch_ppt {
            ComponentHealth::Watch
        } else {
            ComponentHealth::Nominal
        };
        if h != ComponentHealth::Nominal {
            flags.push(ComponentFlag {
                component: Component::WheelTread,
                index: i as u16,
                health: h,
            });
        }
    }

    let worst_health = flags
        .iter()
        .map(|f| f.health)
        .max()
        .unwrap_or(ComponentHealth::Nominal);

    let sample = CbmSample {
        now_ns: inputs.now_ns,
        train_id: inputs.train_id,
        bearing_vib_ppt: inputs.bearing_vib_ppt.clone(),
        motor_temp_dc: inputs.motor_temp_dc.clone(),
        brake_pad_remaining_ppt: inputs.brake_pad_remaining_ppt.clone(),
        wheel_tread_remaining_ppt: inputs.wheel_tread_remaining_ppt.clone(),
        worst_health,
    };

    CbmOutput { sample, flags }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn clean() -> CbmInputs {
        CbmInputs {
            now_ns: 0,
            train_id: 1,
            bearing_vib_ppt: vec![1_000; 4],
            motor_temp_dc: vec![800; 2],
            brake_pad_remaining_ppt: vec![900; 4],
            wheel_tread_remaining_ppt: vec![800; 4],
        }
    }

    #[test]
    fn nominal_has_no_flags() {
        let out = cbm_evaluate(&clean(), &CbmParams::default_metro());
        assert!(out.flags.is_empty());
        assert_eq!(out.sample.worst_health, ComponentHealth::Nominal);
    }

    #[test]
    fn hot_motor_flags_service() {
        let mut i = clean();
        i.motor_temp_dc[1] = 1_700;
        let out = cbm_evaluate(&i, &CbmParams::default_metro());
        assert_eq!(out.sample.worst_health, ComponentHealth::Service);
        assert!(out
            .flags
            .iter()
            .any(|f| f.component == Component::Motor && f.health == ComponentHealth::Service));
    }

    #[test]
    fn worn_brake_pad_flags_service() {
        let mut i = clean();
        i.brake_pad_remaining_ppt[2] = 100;
        let out = cbm_evaluate(&i, &CbmParams::default_metro());
        assert_eq!(out.sample.worst_health, ComponentHealth::Service);
    }

    #[test]
    fn watch_bearing_is_not_service() {
        let mut i = clean();
        i.bearing_vib_ppt[0] = 5_000; // above watch, below service
        let out = cbm_evaluate(&i, &CbmParams::default_metro());
        assert_eq!(out.sample.worst_health, ComponentHealth::Watch);
    }

    #[test]
    fn determinism() {
        let i = clean();
        let p = CbmParams::default_metro();
        assert_eq!(cbm_evaluate(&i, &p), cbm_evaluate(&i, &p));
    }
}
