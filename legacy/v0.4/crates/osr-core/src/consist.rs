//! Rolling-stock description: consist, braking curve, train class.

use serde::{Deserialize, Serialize};

#[derive(Copy, Clone, Debug, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum TrainClass {
    LightMetro,
    Metro,
    Engineering,
    Yard,
    // Intercity and freight are deliberately omitted; see ARCHITECTURE.md §1.
}

/// Piecewise-linear deceleration profile keyed by speed (m/s).
#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct BrakingCurve {
    pub service: Vec<(f32, f32)>,   // (speed_mps, decel_mps2) — nominal
    pub emergency: Vec<(f32, f32)>, // (speed_mps, decel_mps2) — guaranteed
    pub reaction_time_ms: u32,
}

impl BrakingCurve {
    /// Reasonable defaults for a light-metro trainset.
    pub fn light_metro_default() -> Self {
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
    pub has_pantograph: bool,
    pub battery_capacity_wh: u32,
}

impl ConsistDescriptor {
    /// Reference 3-car light-metro consist per RFC 0008 §1.
    pub fn reference_3car() -> Self {
        Self {
            train_class: TrainClass::LightMetro,
            car_count: 3,
            length_mm: 49_500,
            mass_kg: 78_750,
            max_speed_mps: 22.0, // ≈ 80 km/h
            braking: BrakingCurve::light_metro_default(),
            service_accel_mps2: 1.0, // typical light metro service accel
            has_pantograph: false,   // side-pin is the default station charger
            // 675 kWh nameplate provides the documented 540 kWh usable
            // energy after retaining the 20% operating reserve.
            battery_capacity_wh: 675_000,
        }
    }

    /// Effective low-speed service deceleration derived from the braking
    /// curve. Used by the sim engine for travel-time calculations.
    pub fn service_decel_mps2(&self) -> f32 {
        self.braking.service.first().map_or(1.0, |(_, d)| *d)
    }
}
