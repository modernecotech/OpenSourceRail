//! Explicit hypothetical five-mode rigid plant for offline checks, not a magnetic
//! field map. Forces apply instantly: no electrical/thermal dynamics, delay,
//! flexible bodies, rail movement, wind, flux saturation or current conversion.
use crate::array::{Forces, Frame, Station, Wrench, MODULES};

#[derive(Debug, Clone, Copy, PartialEq)]
pub struct IdealPlant {
    /// down (m), roll (rad), pitch (rad), left (m), yaw (rad).
    pub modes: [f64; 5],
    pub velocity: [f64; 5],
    pub mass_kg: f64,
    pub inertia_kg_m2: [f64; 3],
    pub gravity_m_s2: f64,
}
impl IdealPlant {
    /// Exact integration for constant wrench during this interval under the
    /// small-angle, diagonal-inertia hypothesis. Returns false without mutation
    /// for invalid input. External disturbances belong in the supplied wrench.
    pub fn step(&mut self, wrench: Wrench, dt_s: f64) -> bool {
        let finite = self
            .modes
            .iter()
            .chain(self.velocity.iter())
            .chain(self.inertia_kg_m2.iter())
            .chain(wrench.force_n.iter())
            .chain(wrench.moment_nm.iter())
            .all(|v| v.is_finite() && v.abs() <= 1e12);
        if !finite
            || wrench.force_n[0] != 0.0
            || !self.mass_kg.is_finite()
            || self.mass_kg < 1e-6
            || self.mass_kg > 1e9
            || self.inertia_kg_m2.iter().any(|v| *v < 1e-6)
            || !self.gravity_m_s2.is_finite()
            || !(0.0..=100.0).contains(&self.gravity_m_s2)
            || !dt_s.is_finite()
            || dt_s <= 0.0
            || dt_s > 1.0
        {
            return false;
        }
        let acceleration = [
            self.gravity_m_s2 - wrench.force_n[2] / self.mass_kg,
            wrench.moment_nm[0] / self.inertia_kg_m2[0],
            wrench.moment_nm[1] / self.inertia_kg_m2[1],
            wrench.force_n[1] / self.mass_kg,
            wrench.moment_nm[2] / self.inertia_kg_m2[2],
        ];
        for (i, a) in acceleration.into_iter().enumerate() {
            self.modes[i] += self.velocity[i] * dt_s + 0.5 * a * dt_s * dt_s;
            self.velocity[i] += a * dt_s;
        }
        true
    }
    /// Construct identical ideal sensor channels; this establishes no hardware
    /// redundancy or independently measured state. Each station sees rigid tilt.
    pub fn observe(&self, frame: &mut Frame, stations: &[Station; MODULES], target_gap_m: f64) {
        for (sample, s) in frame.samples.iter_mut().zip(stations) {
            let [x, y, z] = s.position_m;
            let gap = target_gap_m + self.modes[0] - y * self.modes[1] + x * self.modes[2];
            let lateral = self.modes[3] + x * self.modes[4] - z * self.modes[1];
            sample.gap_m = [gap; 2];
            sample.lateral_m = [lateral; 2];
        }
    }
    /// Kinetic energy plus gravitational potential relative to zero down.
    pub fn mechanical_energy_j(&self) -> f64 {
        0.5 * self.mass_kg
            * (self.velocity[0] * self.velocity[0] + self.velocity[3] * self.velocity[3])
            + 0.5
                * (self.inertia_kg_m2[0] * self.velocity[1] * self.velocity[1]
                    + self.inertia_kg_m2[1] * self.velocity[2] * self.velocity[2]
                    + self.inertia_kg_m2[2] * self.velocity[4] * self.velocity[4])
            - self.mass_kg * self.gravity_m_s2 * self.modes[0]
    }
}

/// Mechanical interface power at the rigid attachment points in W. Linearised
/// angular kinematics match the five-mode plant; positive means into the car.
/// This is mechanical power only and cannot establish electrical coil losses.
pub fn interface_power_w(
    stations: &[Station; MODULES],
    forces: &[Forces; MODULES],
    velocity: [f64; 5],
) -> f64 {
    stations
        .iter()
        .zip(forces)
        .map(|(s, f)| {
            let [x, y, z] = s.position_m;
            let up_velocity = -velocity[0] + y * velocity[1] - x * velocity[2];
            let left_velocity = velocity[3] + x * velocity[4] - z * velocity[1];
            f.upward_n * up_velocity + f.leftward_n * left_velocity
        })
        .sum()
}
