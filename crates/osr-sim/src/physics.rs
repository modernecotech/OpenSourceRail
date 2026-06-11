//! Service-run physics helpers.
//!
//! The simulator still schedules trains as section-to-section movements,
//! but this module exposes the continuous rest-to-rest profile inside each
//! section so CSV traces can show position, speed, acceleration, braking
//! power, and energy-rate estimates.

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum MotionPhase {
    Idle,
    Accelerating,
    Cruising,
    Braking,
    Arrived,
}

impl MotionPhase {
    pub fn as_str(self) -> &'static str {
        match self {
            Self::Idle => "idle",
            Self::Accelerating => "accelerating",
            Self::Cruising => "cruising",
            Self::Braking => "braking",
            Self::Arrived => "arrived",
        }
    }
}

#[derive(Clone, Copy, Debug)]
pub struct KinematicProfile {
    pub length_m: f32,
    pub accel_mps2: f32,
    pub decel_mps2: f32,
    pub v_peak_mps: f32,
    pub accel_s: f32,
    pub cruise_s: f32,
    pub decel_s: f32,
    pub accel_dist_m: f32,
    pub cruise_dist_m: f32,
    pub total_s: f32,
}

#[derive(Clone, Copy, Debug)]
pub struct MotionSample {
    pub position_m: f32,
    pub speed_mps: f32,
    pub accel_mps2: f32,
    pub traction_power_kw: f32,
    pub brake_power_kw: f32,
    pub phase: MotionPhase,
}

/// Build a rest-to-rest profile for one section.
///
/// If the section is too short to reach `v_max_mps`, the profile becomes
/// triangular and `v_peak_mps` falls below `v_max_mps`.
pub fn kinematic_profile(
    length_m: f32,
    v_max_mps: f32,
    accel_mps2: f32,
    decel_mps2: f32,
) -> KinematicProfile {
    let length_m = length_m.max(0.0);
    let v_max_mps = v_max_mps.max(0.01);
    let accel_mps2 = accel_mps2.max(0.01);
    let decel_mps2 = decel_mps2.max(0.01);

    let accel_dist_m = (v_max_mps * v_max_mps) / (2.0 * accel_mps2);
    let decel_dist_m = (v_max_mps * v_max_mps) / (2.0 * decel_mps2);

    if accel_dist_m + decel_dist_m >= length_m {
        let v_peak_mps =
            ((2.0 * length_m * accel_mps2 * decel_mps2) / (accel_mps2 + decel_mps2)).sqrt();
        let accel_s = v_peak_mps / accel_mps2;
        let decel_s = v_peak_mps / decel_mps2;
        KinematicProfile {
            length_m,
            accel_mps2,
            decel_mps2,
            v_peak_mps,
            accel_s,
            cruise_s: 0.0,
            decel_s,
            accel_dist_m: (v_peak_mps * v_peak_mps) / (2.0 * accel_mps2),
            cruise_dist_m: 0.0,
            total_s: accel_s + decel_s,
        }
    } else {
        let cruise_dist_m = length_m - accel_dist_m - decel_dist_m;
        let cruise_s = cruise_dist_m / v_max_mps;
        let accel_s = v_max_mps / accel_mps2;
        let decel_s = v_max_mps / decel_mps2;
        KinematicProfile {
            length_m,
            accel_mps2,
            decel_mps2,
            v_peak_mps: v_max_mps,
            accel_s,
            cruise_s,
            decel_s,
            accel_dist_m,
            cruise_dist_m,
            total_s: accel_s + cruise_s + decel_s,
        }
    }
}

/// Sample the continuous rest-to-rest profile at `elapsed_s`.
pub fn sample_profile(profile: &KinematicProfile, elapsed_s: f32, mass_kg: f32) -> MotionSample {
    let t = elapsed_s.max(0.0);

    let (position_m, speed_mps, accel_mps2, phase) = if profile.length_m <= 0.0 {
        (0.0, 0.0, 0.0, MotionPhase::Arrived)
    } else if t == 0.0 {
        (0.0, 0.0, profile.accel_mps2, MotionPhase::Accelerating)
    } else if t < profile.accel_s {
        let v = profile.accel_mps2 * t;
        let x = 0.5 * profile.accel_mps2 * t * t;
        (x, v, profile.accel_mps2, MotionPhase::Accelerating)
    } else if t < profile.accel_s + profile.cruise_s {
        let tau = t - profile.accel_s;
        let x = profile.accel_dist_m + profile.v_peak_mps * tau;
        (x, profile.v_peak_mps, 0.0, MotionPhase::Cruising)
    } else if t < profile.total_s {
        let tau = t - profile.accel_s - profile.cruise_s;
        let v = (profile.v_peak_mps - profile.decel_mps2 * tau).max(0.0);
        let x = profile.accel_dist_m + profile.cruise_dist_m + profile.v_peak_mps * tau
            - 0.5 * profile.decel_mps2 * tau * tau;
        (x, v, -profile.decel_mps2, MotionPhase::Braking)
    } else {
        (profile.length_m, 0.0, 0.0, MotionPhase::Arrived)
    };

    let traction_power_kw = if accel_mps2 > 0.0 {
        mass_kg.max(0.0) * accel_mps2 * speed_mps / 1000.0
    } else {
        0.0
    };
    let brake_power_kw = if accel_mps2 < 0.0 {
        mass_kg.max(0.0) * -accel_mps2 * speed_mps / 1000.0
    } else {
        0.0
    };

    MotionSample {
        position_m: position_m.clamp(0.0, profile.length_m),
        speed_mps: speed_mps.max(0.0),
        accel_mps2,
        traction_power_kw,
        brake_power_kw,
        phase,
    }
}

pub fn sample_kinematic_profile(
    length_m: f32,
    v_max_mps: f32,
    accel_mps2: f32,
    decel_mps2: f32,
    elapsed_s: f32,
    mass_kg: f32,
) -> MotionSample {
    let profile = kinematic_profile(length_m, v_max_mps, accel_mps2, decel_mps2);
    sample_profile(&profile, elapsed_s, mass_kg)
}

#[cfg(test)]
mod tests {
    use super::*;

    fn approx(a: f32, b: f32, tol: f32) {
        assert!((a - b).abs() <= tol, "expected {b:.3} ± {tol}, got {a:.3}");
    }

    #[test]
    fn trapezoid_samples_accel_cruise_brake_arrival() {
        let p = kinematic_profile(2_000.0, 20.0, 1.0, 1.0);
        approx(p.total_s, 120.0, 0.01);

        let a = sample_profile(&p, 10.0, 100_000.0);
        approx(a.position_m, 50.0, 0.01);
        approx(a.speed_mps, 10.0, 0.01);
        assert_eq!(a.phase, MotionPhase::Accelerating);

        let c = sample_profile(&p, 60.0, 100_000.0);
        approx(c.speed_mps, 20.0, 0.01);
        assert_eq!(c.phase, MotionPhase::Cruising);

        let b = sample_profile(&p, 110.0, 100_000.0);
        approx(b.speed_mps, 10.0, 0.01);
        assert_eq!(b.phase, MotionPhase::Braking);

        let z = sample_profile(&p, 120.0, 100_000.0);
        approx(z.position_m, 2_000.0, 0.01);
        approx(z.speed_mps, 0.0, 0.01);
        assert_eq!(z.phase, MotionPhase::Arrived);
    }

    #[test]
    fn short_section_is_triangular() {
        let p = kinematic_profile(200.0, 20.0, 1.0, 1.0);
        approx(p.total_s, 28.284, 0.01);
        approx(p.v_peak_mps, 14.142, 0.01);
        assert_eq!(p.cruise_s, 0.0);
    }
}
