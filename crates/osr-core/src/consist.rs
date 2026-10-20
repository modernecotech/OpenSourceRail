//! Rolling-stock description: consist, braking curve, train class.

use serde::{Deserialize, Serialize};

#[derive(Copy, Clone, Debug, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum TrainClass {
    UrbanMaglev,
    Engineering,
    Yard,
    // Urban passenger and maintenance service classes only.
}

/// Piecewise-linear deceleration profile keyed by speed (m/s).
#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct BrakingCurve {
    pub service: Vec<(f32, f32)>,   // (speed_mps, decel_mps2) — nominal
    pub emergency: Vec<(f32, f32)>, // (speed_mps, decel_mps2) — guaranteed
    pub reaction_time_ms: u32,
}

impl BrakingCurve {
    /// Synthetic curve for arithmetic regression fixtures; not a qualified vehicle curve.
    pub fn synthetic_analysis_fixture() -> Self {
        Self {
            service: vec![(0.0, 1.1), (20.0, 1.0), (28.0, 0.9)],
            emergency: vec![(0.0, 1.5), (20.0, 1.4), (28.0, 1.2)],
            reaction_time_ms: 400,
        }
    }
}

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct ConsistDescriptor {
    pub train_class: TrainClass,
    pub car_count: u32,
    pub length_mm: u32,
    pub mass_kg: u32,
    pub max_speed_mps: f32,
    pub braking: BrakingCurve,
    /// Service-brake acceleration (m/s²). Used with the braking curve to
    /// compute kinematic travel times.
    pub service_accel_mps2: f32,
    pub battery_capacity_wh: u32,
}

impl ConsistDescriptor {
    /// Synthetic two-car fixture for generic protocol and protection arithmetic.
    /// Never use this as an operating or engineering vehicle configuration.
    pub fn synthetic_analysis_fixture() -> Self {
        Self {
            train_class: TrainClass::UrbanMaglev,
            car_count: 2,
            length_mm: 40_000,
            mass_kg: 40_000,
            max_speed_mps: 22.0, // ≈ 80 km/h
            braking: BrakingCurve::synthetic_analysis_fixture(),
            service_accel_mps2: 1.0, // synthetic kinematic parameter
            battery_capacity_wh: 100_000,
        }
    }

    /// Effective low-speed service deceleration derived from the braking
    /// curve. Used by the sim engine for travel-time calculations.
    pub fn service_decel_mps2(&self) -> f32 {
        self.braking.service.first().map_or(1.0, |(_, d)| *d)
    }
}
