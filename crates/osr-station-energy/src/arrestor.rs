//! Nominal flat-track point-mass requirements for a staged station arrestor.
//! Contact, load transfer, installed assemblies and physical acceptance remain unknown.
use serde::{Deserialize, Serialize};
use std::collections::HashSet;

pub const REQUEST_SCHEMA: &str = "osr-multistage-arrestor-request/1";
pub const RESULT_SCHEMA: &str = "osr-multistage-arrestor-result/1";
pub const MAX_INPUT_BYTES: usize = 8 * 1024 * 1024;
pub const MAX_CASES: usize = 1000;

#[derive(Debug, Clone, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct Request {
    pub schema: String,
    pub cases: Vec<Case>,
}
#[derive(Debug, Clone, Copy, Deserialize, Serialize, PartialEq, Eq)]
#[serde(rename_all = "kebab-case")]
pub enum Handover {
    ContinuousTotalForce,
    IndependentStagePulses,
}
#[derive(Debug, Clone, Copy, Deserialize, Serialize)]
#[serde(rename_all = "kebab-case")]
pub enum StressMode {
    Axial,
    Torsional,
}
#[derive(Debug, Clone, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct Stage {
    pub exit_speed_m_s: f64,
    pub max_deceleration_m_s2: f64,
    pub max_jerk_m_s3: f64,
    pub available_stroke_m: f64,
    pub force_limit_n: Option<f64>,
    pub displacement_ratio: f64,
}
#[derive(Debug, Clone, Deserialize, Serialize)]
#[serde(tag = "kind", rename_all = "kebab-case", deny_unknown_fields)]
pub enum StorageDesign {
    Elastic {
        stress_mode: StressMode,
        density_kg_m3: f64,
        modulus_pa: f64,
        allowable_stress_pa: f64,
        utilisation: f64,
        packing_fraction: f64,
    },
    Hydraulic {
        precharge_pressure_pa: f64,
        min_pressure_pa: f64,
        max_pressure_pa: f64,
        return_pressure_pa: f64,
        polytropic_exponent: f64,
        vessel_mass_kg_per_m3: f64,
        packing_fraction: f64,
    },
    Flywheel {
        density_kg_m3: f64,
        allowable_stress_pa: f64,
        utilisation: f64,
        min_max_speed_ratio: f64,
        radius_m: f64,
        packing_fraction: f64,
    },
    DeclaredSpecificEnergy {
        specific_energy_j_kg: f64,
        density_kg_m3: f64,
        packing_fraction: f64,
    },
}
#[derive(Debug, Clone, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct Store {
    pub capacity_j: f64,
    pub initial_j: f64,
    pub reserve_j: f64,
    pub efficiency_capture: f64,
    pub efficiency_store: f64,
    pub efficiency_release: f64,
    pub standing_loss_w: f64,
    pub dwell_s: f64,
    pub isolated_during_dwell: bool,
    pub controlled_forward_transfer: bool,
    pub departure_authorized: bool,
    pub design: StorageDesign,
}
#[derive(Debug, Clone, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct Launch {
    pub target_speed_m_s: f64,
    pub max_acceleration_m_s2: f64,
    pub max_jerk_m_s3: f64,
    pub available_stroke_m: f64,
    pub force_limit_n: Option<f64>,
    pub mass_fractions: Vec<f64>,
    pub force_fractions: Vec<f64>,
}
#[derive(Debug, Clone, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct Booster {
    pub target_speed_m_s: f64,
    pub max_acceleration_m_s2: f64,
    pub max_jerk_m_s3: f64,
    pub efficiency: f64,
    pub available_stroke_m: f64,
    pub force_limit_n: Option<f64>,
    pub source_power_limit_w: Option<f64>,
}
#[derive(Debug, Clone, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct Case {
    pub id: String,
    pub effective_mass_kg: f64,
    pub capture_entry_speed_m_s: f64,
    pub grade_fraction: f64,
    pub resistance_n: f64,
    pub handover: Handover,
    pub stages: Vec<Stage>,
    pub storage: Store,
    pub launch: Launch,
    pub booster: Booster,
    pub reset_s: f64,
    pub headway_s: f64,
}
#[derive(Debug, Clone, Serialize)]
pub struct BatchResult {
    pub schema: &'static str,
    pub cases: Vec<Envelope>,
}
#[derive(Debug, Clone, Serialize)]
pub struct Sizing {
    pub kind: &'static str,
    pub capacity_j: f64,
    pub active_mass_kg: f64,
    pub active_material_volume_m3: Option<f64>,
    pub internal_volume_m3: Option<f64>,
    pub envelope_volume_m3: f64,
    pub specific_energy_j_kg: Option<f64>,
    pub specific_work_j_m3: Option<f64>,
    pub tip_speed_m_s: Option<f64>,
    pub max_rpm: Option<f64>,
    pub mass_basis: &'static str,
    pub complete_installed_mass: bool,
}
#[derive(Debug, Clone, Serialize)]
pub struct StageResult {
    pub index: usize,
    pub entry_speed_m_s: f64,
    pub exit_speed_m_s: f64,
    pub time_s: f64,
    pub distance_m: f64,
    pub start_x_m: f64,
    pub end_x_m: f64,
    pub peak_deceleration_m_s2: f64,
    pub peak_jerk_m_s3: f64,
    pub required_peak_force_n: f64,
    pub store_travel_m: f64,
    pub store_force_upper_bound_n: f64,
    pub kinetic_drop_j: f64,
    pub credited_capture_j: f64,
    pub unrecovered_braking_j: f64,
    pub capture_loss_j: f64,
    pub store_loss_j: f64,
    pub accepted_j: f64,
    pub overflow_j: f64,
    pub bound_failures: Vec<String>,
}
#[derive(Debug, Clone, Serialize)]
pub struct Capture {
    pub entry_kinetic_energy_j: f64,
    pub total_time_s: Option<f64>,
    pub total_distance_m: Option<f64>,
    pub required_peak_force_n: Option<f64>,
    pub stages: Option<Vec<StageResult>>,
}
#[derive(Debug, Clone, Serialize)]
pub struct Storage {
    pub initial_j: f64,
    pub accepted_j: f64,
    pub capture_conversion_loss_j: f64,
    pub store_conversion_loss_j: f64,
    pub overflow_j: f64,
    pub unrecovered_braking_j: f64,
    pub unresolved_capture_j: f64,
    pub standing_loss_j: f64,
    pub withdrawn_j: f64,
    pub release_loss_j: f64,
    pub delivered_j: f64,
    pub delivered_from_initial_j: f64,
    pub delivered_from_new_capture_j: f64,
    pub request_shortfall_j: f64,
    pub end_j: f64,
    pub balance_residual_j: f64,
    pub departure_state: &'static str,
    /// All transfers are nominal requirements, never observed hardware behavior.
    pub nominal_transfer_only: bool,
}
#[derive(Debug, Clone, Serialize)]
pub struct Point {
    pub time_s: f64,
    pub x_m: f64,
    pub speed_m_s: f64,
    pub acceleration_m_s2: f64,
}
#[derive(Debug, Clone, Serialize)]
pub struct Motion {
    pub entry_speed_m_s: f64,
    pub exit_speed_m_s: f64,
    pub time_s: f64,
    pub distance_m: f64,
    pub origin_x_m: f64,
    pub peak_acceleration_m_s2: f64,
    pub peak_jerk_m_s3: f64,
    pub required_peak_force_n: f64,
    pub peak_mechanical_power_w: f64,
    pub coupler_tension_n: Vec<f64>,
    pub phase_knots: Vec<Point>,
}
#[derive(Debug, Clone, Serialize)]
pub struct BoosterResult {
    #[serde(flatten)]
    pub motion: Motion,
    pub source_energy_j: f64,
    pub peak_source_power_w: f64,
}
#[derive(Debug, Clone, Serialize)]
pub struct Resource {
    pub occupation_s: Option<f64>,
    pub headway_margin_s: Option<f64>,
}
#[derive(Debug, Clone, Serialize)]
pub struct Envelope {
    pub id: String,
    pub execution: &'static str,
    pub necessary_bounds: &'static str,
    pub failures: Vec<String>,
    pub unknowns: Vec<String>,
    pub capture: Capture,
    pub storage: Storage,
    pub sizing: Sizing,
    pub launch: Option<Motion>,
    pub booster: Option<BoosterResult>,
    pub resource: Resource,
    pub energy_residual_j: f64,
    pub physical_accepted: bool,
    pub engineering_accepted: bool,
    pub manufacturing_release: bool,
    pub operating_release: bool,
    pub selected_reference_changed: bool,
    pub movement_authority: bool,
}
fn positive(values: &[f64]) -> Result<(), String> {
    super::finite(values)?;
    if values.iter().any(|v| *v <= 0.0) {
        return Err("Positive finite SI quantity required".into());
    }
    Ok(())
}
fn fraction(value: f64) -> Result<(), String> {
    super::finite(&[value])?;
    if !(0.0..=1.0).contains(&value) {
        return Err("Fraction outside [0,1]".into());
    }
    Ok(())
}
fn positive_fraction(value: f64) -> Result<(), String> {
    fraction(value)?;
    positive(&[value])
}
fn limit(value: Option<f64>) -> Result<(), String> {
    if let Some(v) = value {
        super::nonnegative(&[v])?;
    }
    Ok(())
}
fn validate(c: &Case) -> Result<(), String> {
    if c.id.trim().is_empty() || c.id.len() > 128 {
        return Err("Nonempty id of at most 128 UTF-8 bytes required".into());
    }
    positive(&[c.effective_mass_kg, c.headway_s])?;
    super::finite(&[c.grade_fraction])?;
    super::nonnegative(&[
        c.capture_entry_speed_m_s,
        c.resistance_n,
        c.reset_s,
        c.storage.capacity_j,
        c.storage.initial_j,
        c.storage.reserve_j,
        c.storage.standing_loss_w,
        c.storage.dwell_s,
        c.launch.target_speed_m_s,
        c.launch.available_stroke_m,
        c.booster.target_speed_m_s,
        c.booster.available_stroke_m,
    ])?;
    positive(&[
        c.launch.max_acceleration_m_s2,
        c.launch.max_jerk_m_s3,
        c.booster.max_acceleration_m_s2,
        c.booster.max_jerk_m_s3,
        c.booster.efficiency,
    ])?;
    for f in [
        c.storage.efficiency_capture,
        c.storage.efficiency_store,
        c.storage.efficiency_release,
        c.booster.efficiency,
    ] {
        fraction(f)?;
    }
    if c.storage.initial_j > c.storage.capacity_j || c.storage.reserve_j > c.storage.capacity_j {
        return Err("Store state/reserve exceeds capacity".into());
    }
    if c.stages.len() > 64 {
        return Err("At most 64 capture stages permitted".into());
    }
    if (c.capture_entry_speed_m_s == 0.0) != c.stages.is_empty() {
        return Err(
            "Positive entry speed needs stages; zero entry speed needs no capture stages".into(),
        );
    }
    let mut speed = c.capture_entry_speed_m_s;
    for s in &c.stages {
        super::nonnegative(&[s.exit_speed_m_s, s.available_stroke_m])?;
        positive(&[
            s.max_deceleration_m_s2,
            s.max_jerk_m_s3,
            s.displacement_ratio,
        ])?;
        limit(s.force_limit_n)?;
        if s.exit_speed_m_s >= speed {
            return Err("Stage exit speeds must strictly decrease".into());
        }
        speed = s.exit_speed_m_s;
    }
    if !c.stages.is_empty() && speed != 0.0 {
        return Err("Final stage must stop the nominal train".into());
    }
    limit(c.launch.force_limit_n)?;
    limit(c.booster.force_limit_n)?;
    limit(c.booster.source_power_limit_w)?;
    if c.launch.mass_fractions.is_empty()
        || c.launch.mass_fractions.len() > 64
        || c.launch.mass_fractions.len() != c.launch.force_fractions.len()
    {
        return Err("Matching 1-64 car mass and launch-force fractions required".into());
    }
    for f in &c.launch.mass_fractions {
        positive_fraction(*f)?;
    }
    for f in &c.launch.force_fractions {
        fraction(*f)?;
    }
    for sum in [
        c.launch.mass_fractions.iter().sum::<f64>(),
        c.launch.force_fractions.iter().sum::<f64>(),
    ] {
        if (sum - 1.0).abs() > 1e-9 {
            return Err("Car fractions must sum to one".into());
        }
    }
    Ok(())
}

/// Material or parametric active-element sizing only; installed auxiliaries stay separate.
pub fn size_store(capacity: f64, design: &StorageDesign) -> Result<Sizing, String> {
    super::nonnegative(&[capacity])?;
    let mut out = Sizing {
        kind: "",
        capacity_j: capacity,
        active_mass_kg: 0.0,
        active_material_volume_m3: None,
        internal_volume_m3: None,
        envelope_volume_m3: 0.0,
        specific_energy_j_kg: None,
        specific_work_j_m3: None,
        tip_speed_m_s: None,
        max_rpm: None,
        mass_basis: "",
        complete_installed_mass: false,
    };
    match *design {
        StorageDesign::Elastic {
            stress_mode: _,
            density_kg_m3,
            modulus_pa,
            allowable_stress_pa,
            utilisation,
            packing_fraction,
        } => {
            positive(&[density_kg_m3, modulus_pa, allowable_stress_pa])?;
            positive_fraction(utilisation)?;
            positive_fraction(packing_fraction)?;
            let specific = allowable_stress_pa / modulus_pa * allowable_stress_pa
                / (2.0 * density_kg_m3)
                * utilisation;
            positive(&[specific])?;
            let mass = capacity / specific;
            let volume = mass / density_kg_m3;
            out.kind = "elastic";
            out.active_mass_kg = mass;
            out.active_material_volume_m3 = Some(volume);
            out.envelope_volume_m3 = volume / packing_fraction;
            out.specific_energy_j_kg = Some(specific);
            out.mass_basis =
                "declared-elastic-material-stress-modulus-and-utilisation; fatigue-unverified";
        }
        StorageDesign::DeclaredSpecificEnergy {
            specific_energy_j_kg,
            density_kg_m3,
            packing_fraction,
        } => {
            positive(&[specific_energy_j_kg, density_kg_m3])?;
            positive_fraction(packing_fraction)?;
            let mass = capacity / specific_energy_j_kg;
            let volume = mass / density_kg_m3;
            out.kind = "declared-specific-energy";
            out.active_mass_kg = mass;
            out.active_material_volume_m3 = Some(volume);
            out.envelope_volume_m3 = volume / packing_fraction;
            out.specific_energy_j_kg = Some(specific_energy_j_kg);
            out.mass_basis =
                "explicit-specific-energy-sensitivity; not-a-universal-material-property";
        }
        StorageDesign::Hydraulic {
            precharge_pressure_pa,
            min_pressure_pa,
            max_pressure_pa,
            return_pressure_pa,
            polytropic_exponent,
            vessel_mass_kg_per_m3,
            packing_fraction,
        } => {
            positive(&[
                precharge_pressure_pa,
                min_pressure_pa,
                max_pressure_pa,
                polytropic_exponent,
                vessel_mass_kg_per_m3,
            ])?;
            super::nonnegative(&[return_pressure_pa])?;
            positive_fraction(packing_fraction)?;
            if precharge_pressure_pa > min_pressure_pa
                || min_pressure_pa >= max_pressure_pa
                || return_pressure_pa >= min_pressure_pa
            {
                return Err(
                    "Absolute hydraulic pressures must satisfy 0<p0<=pmin<pmax and return<pmin"
                        .into(),
                );
            }
            let log_ratio = (max_pressure_pa / min_pressure_pa).ln();
            let vmin = (precharge_pressure_pa / min_pressure_pa).powf(1.0 / polytropic_exponent);
            let vmax = vmin * (-log_ratio / polytropic_exponent).exp();
            let z = (polytropic_exponent - 1.0) / polytropic_exponent * log_ratio;
            let gas_work = if polytropic_exponent == 1.0 {
                precharge_pressure_pa * log_ratio
            } else {
                min_pressure_pa * vmin * z.exp_m1() / (polytropic_exponent - 1.0)
            };
            let specific = gas_work - return_pressure_pa * (vmin - vmax);
            positive(&[specific])?;
            let volume = capacity / specific;
            out.kind = "hydraulic";
            out.active_mass_kg = volume * vessel_mass_kg_per_m3;
            out.internal_volume_m3 = Some(volume);
            out.envelope_volume_m3 = volume / packing_fraction;
            out.specific_work_j_m3 = Some(specific);
            out.mass_basis =
                "assumed-vessel-package-mass-per-precharge-volume; pressure-design-unverified";
        }
        StorageDesign::Flywheel {
            density_kg_m3,
            allowable_stress_pa,
            utilisation,
            min_max_speed_ratio,
            radius_m,
            packing_fraction,
        } => {
            positive(&[density_kg_m3, allowable_stress_pa, radius_m])?;
            positive_fraction(utilisation)?;
            fraction(min_max_speed_ratio)?;
            positive_fraction(packing_fraction)?;
            if min_max_speed_ratio >= 1.0 {
                return Err("Flywheel minimum speed must be below maximum speed".into());
            }
            let specific = 0.5 * allowable_stress_pa / density_kg_m3
                * utilisation
                * (1.0 - min_max_speed_ratio * min_max_speed_ratio);
            positive(&[specific])?;
            let mass = capacity / specific;
            let volume = mass / density_kg_m3;
            let tip = (allowable_stress_pa / density_kg_m3).sqrt();
            out.kind = "flywheel";
            out.active_mass_kg = mass;
            out.active_material_volume_m3 = Some(volume);
            out.envelope_volume_m3 = volume / packing_fraction;
            out.specific_energy_j_kg = Some(specific);
            out.tip_speed_m_s = Some(tip);
            out.max_rpm = Some(tip / radius_m * 60.0 / (2.0 * std::f64::consts::PI));
            out.mass_basis =
                "usable-thin-rim-energy-bound; hub-bearing-containment-and-fatigue-unverified";
        }
    }
    super::finite(&[out.active_mass_kg, out.envelope_volume_m3])?;
    if capacity > 0.0 && (out.active_mass_kg <= 0.0 || out.envelope_volume_m3 <= 0.0) {
        return Err("Storage sizing underflow outside representable numerical domain".into());
    }
    for n in [
        out.active_material_volume_m3,
        out.internal_volume_m3,
        out.specific_energy_j_kg,
        out.specific_work_j_m3,
        out.tip_speed_m_s,
        out.max_rpm,
    ]
    .into_iter()
    .flatten()
    {
        super::finite(&[n])?;
    }
    Ok(out)
}

#[derive(Debug, Clone, Copy)]
struct State {
    x: f64,
    v: f64,
    a: f64,
}
#[derive(Debug, Clone, Copy)]
struct Profile {
    vin: f64,
    vout: f64,
    sign: f64,
    a: f64,
    j: f64,
    ramp: f64,
    hold: f64,
    time: f64,
    distance: f64,
}
impl Profile {
    fn new(vin: f64, vout: f64, a_max: f64, j: f64) -> Result<Self, String> {
        let delta = (vout - vin).abs();
        let ramp = (a_max / j).min((delta / j).sqrt());
        let a = j * ramp;
        let hold = if a == 0.0 {
            0.0
        } else {
            (delta / a - ramp).max(0.0)
        };
        let time = 2.0 * ramp + hold;
        let distance = (vin + vout) * 0.5 * time;
        super::finite(&[ramp, a, hold, time, distance])?;
        if delta > 0.0 && (ramp == 0.0 || a == 0.0 || time == 0.0) {
            return Err("Nonzero velocity change has an unrepresentable motion profile".into());
        }
        Ok(Self {
            vin,
            vout,
            sign: if vout >= vin { 1.0 } else { -1.0 },
            a,
            j,
            ramp,
            hold,
            time,
            distance,
        })
    }
    fn state(self, t: f64) -> State {
        let t = t.clamp(0.0, self.time);
        if t == self.time {
            return State {
                x: self.distance,
                v: self.vout,
                a: 0.0,
            };
        }
        let r = self.ramp;
        let a = self.a;
        let j = self.j;
        let sign = self.sign;
        if t <= r {
            return State {
                x: self.vin * t + sign * j * t * t * t / 6.0,
                v: self.vin + sign * j * t * t / 2.0,
                a: sign * j * t,
            };
        }
        let v1 = self.vin + sign * a * r / 2.0;
        let x1 = self.vin * r + sign * j * r * r * r / 6.0;
        if t <= r + self.hold {
            let u = t - r;
            return State {
                x: x1 + v1 * u + sign * a * u * u / 2.0,
                v: v1 + sign * a * u,
                a: sign * a,
            };
        }
        let h = self.hold;
        let v2 = v1 + sign * a * h;
        let x2 = x1 + v1 * h + sign * a * h * h / 2.0;
        let u = t - r - h;
        State {
            x: x2 + v2 * u + sign * (a * u * u / 2.0 - j * u * u * u / 6.0),
            v: v2 + sign * (a * u - j * u * u / 2.0),
            a: sign * (a - j * u),
        }
    }
    fn at_speed(self, target: f64) -> f64 {
        if target == self.vin {
            return 0.0;
        }
        if target == self.vout {
            return self.time;
        }
        let (mut low, mut high) = (0.0, self.time);
        for _ in 0..80 {
            let mid = (low + high) * 0.5;
            let v = self.state(mid).v;
            if (self.sign > 0.0 && v < target) || (self.sign < 0.0 && v > target) {
                low = mid;
            } else {
                high = mid;
            }
        }
        (low + high) * 0.5
    }
    fn peak_a(self, start: f64, end: f64) -> f64 {
        let mut peak = self.state(start).a.abs().max(self.state(end).a.abs());
        for t in [self.ramp, self.ramp + self.hold] {
            if start <= t && t <= end {
                peak = peak.max(self.state(t).a.abs());
            }
        }
        peak
    }
    fn peak_j(self, start: f64, end: f64) -> f64 {
        if (start < self.ramp && end > 0.0) || (start < self.time && end > self.ramp + self.hold) {
            self.j
        } else {
            0.0
        }
    }
    fn peak_power(self, mass: f64) -> Result<f64, String> {
        if self.time == 0.0 {
            return Ok(0.0);
        }
        let mut times = vec![0.0, self.ramp, self.ramp + self.hold, self.time];
        for (start, duration, jerk) in [
            (0.0, self.ramp, self.sign * self.j),
            (self.ramp, self.hold, 0.0),
            (self.ramp + self.hold, self.ramp, -self.sign * self.j),
        ] {
            if duration == 0.0 || jerk == 0.0 {
                continue;
            }
            let state = self.state(start);
            let qa = 1.5 * jerk * jerk;
            let qb = 3.0 * state.a * jerk;
            let qc = state.a * state.a + jerk * state.v;
            let disc = qb * qb - 4.0 * qa * qc;
            super::finite(&[qa, qb, qc, disc])?;
            if disc >= 0.0 {
                for t in [
                    (-qb - disc.sqrt()) / (2.0 * qa),
                    (-qb + disc.sqrt()) / (2.0 * qa),
                ] {
                    if t > 0.0 && t < duration {
                        times.push(start + t);
                    }
                }
            }
        }
        let peak = times
            .into_iter()
            .map(|t| {
                let s = self.state(t);
                mass * s.a.abs() * s.v.max(0.0)
            })
            .fold(0.0, f64::max);
        super::finite(&[peak])?;
        Ok(peak)
    }
    fn motion(
        self,
        mass: f64,
        origin: f64,
        masses: &[f64],
        forces: &[f64],
    ) -> Result<Motion, String> {
        let peak_force = mass * self.a;
        let mut prefix_m = 0.0;
        let mut prefix_f = 0.0;
        let mut couplers = Vec::new();
        for i in 0..masses.len().saturating_sub(1) {
            prefix_m += masses[i];
            prefix_f += forces[i];
            couplers.push(peak_force * (prefix_f - prefix_m));
        }
        let mut times = vec![0.0, self.ramp, self.ramp + self.hold, self.time];
        times.dedup_by(|a, b| *a == *b);
        let knots = times
            .into_iter()
            .map(|t| {
                let s = self.state(t);
                Point {
                    time_s: t,
                    x_m: origin + s.x,
                    speed_m_s: s.v,
                    acceleration_m_s2: s.a,
                }
            })
            .collect();
        let power = self.peak_power(mass)?;
        super::finite(&[peak_force, origin + self.distance])?;
        for force in &couplers {
            super::finite(&[*force])?;
        }
        Ok(Motion {
            entry_speed_m_s: self.vin,
            exit_speed_m_s: self.vout,
            time_s: self.time,
            distance_m: self.distance,
            origin_x_m: origin,
            peak_acceleration_m_s2: self.a,
            peak_jerk_m_s3: if self.time > 0.0 { self.j } else { 0.0 },
            required_peak_force_n: peak_force,
            peak_mechanical_power_w: power,
            coupler_tension_n: couplers,
            phase_knots: knots,
        })
    }
}
fn push(items: &mut Vec<String>, s: &str) {
    items.push(s.to_string());
}

pub fn evaluate(c: &Case) -> Result<Envelope, String> {
    validate(c)?;
    let sizing = size_store(c.storage.capacity_j, &c.storage.design)?;
    let mut failures = Vec::new();
    let mut unknowns = vec![
        "contact-clutch-force-handover-and-forward-transmission-unverified".into(),
        "material-fatigue-storage-power-thermal-duty-and-containment-unverified".into(),
        "full-train-slack-coupler-buckling-and-independent-braking-unverified".into(),
        "swept-envelopes-attachments-retention-installation-removal-and-repair-unresolved".into(),
        "nominal-point-mass-jerk-is-not-measured-passenger-jerk".into(),
        "single-exclusive-resource-is-not-protected-station-throughput".into(),
    ];
    let domain = c.grade_fraction == 0.0 && c.resistance_n == 0.0;
    if !domain {
        push(
            &mut unknowns,
            "grade-or-resistance-outside-flat-capture-and-launch-domain",
        );
    }
    let kinetic = 0.5 * c.effective_mass_kg * c.capture_entry_speed_m_s * c.capture_entry_speed_m_s;
    super::finite(&[kinetic])?;
    let mut state = c.storage.initial_j;
    let mut rows = Vec::new();
    let (mut elapsed, mut distance, mut peak_force) = (0.0_f64, 0.0_f64, 0.0_f64);
    let (mut accepted, mut cap_loss, mut store_loss, mut overflow, mut unrecovered) =
        (0.0, 0.0, 0.0, 0.0, 0.0);
    if domain && !c.stages.is_empty() {
        let global = Profile::new(
            c.capture_entry_speed_m_s,
            0.0,
            c.stages
                .iter()
                .map(|s| s.max_deceleration_m_s2)
                .fold(f64::INFINITY, f64::min),
            c.stages
                .iter()
                .map(|s| s.max_jerk_m_s3)
                .fold(f64::INFINITY, f64::min),
        )?;
        let (mut vin, mut global_start) = (c.capture_entry_speed_m_s, 0.0);
        for (index, stage) in c.stages.iter().enumerate() {
            let (profile, start, end) = if c.handover == Handover::ContinuousTotalForce {
                let end = global.at_speed(stage.exit_speed_m_s);
                (global, global_start, end)
            } else {
                let p = Profile::new(
                    vin,
                    stage.exit_speed_m_s,
                    stage.max_deceleration_m_s2,
                    stage.max_jerk_m_s3,
                )?;
                (p, 0.0, p.time)
            };
            let time = end - start;
            let travel = profile.state(end).x - profile.state(start).x;
            let a = profile.peak_a(start, end);
            let j = profile.peak_j(start, end);
            let force = c.effective_mass_kg * a;
            let drop = 0.5
                * c.effective_mass_kg
                * (vin * vin - stage.exit_speed_m_s * stage.exit_speed_m_s);
            let mut stage_failures = Vec::new();
            if travel > stage.available_stroke_m + 1e-10 * travel.max(1.0) {
                push(&mut stage_failures, "capture-stage-stroke-exceeded");
            }
            if stage.force_limit_n.is_some_and(|limit| force > limit) {
                push(&mut stage_failures, "capture-stage-force-limit-exceeded");
            }
            if stage.force_limit_n.is_none() {
                push(
                    &mut unknowns,
                    &format!("capture-stage-{index}-force-capability-unspecified"),
                );
            }
            for failure in &stage_failures {
                failures.push(format!("stage-{index}:{failure}"));
            }
            let credit = if stage_failures.is_empty() { drop } else { 0.0 };
            let lost = drop - credit;
            let after_cap = credit * c.storage.efficiency_capture;
            let after_store = after_cap * c.storage.efficiency_store;
            let added = after_store.min((c.storage.capacity_j - state).max(0.0));
            let spill = after_store - added;
            state += added;
            accepted += added;
            cap_loss += credit - after_cap;
            store_loss += after_cap - after_store;
            overflow += spill;
            unrecovered += lost;
            let store_travel = travel / stage.displacement_ratio;
            let store_force = force * stage.displacement_ratio;
            super::finite(&[
                time,
                travel,
                a,
                j,
                force,
                drop,
                credit,
                lost,
                added,
                spill,
                state,
                store_travel,
                store_force,
            ])?;
            rows.push(StageResult {
                index,
                entry_speed_m_s: vin,
                exit_speed_m_s: stage.exit_speed_m_s,
                time_s: time,
                distance_m: travel,
                start_x_m: distance,
                end_x_m: distance + travel,
                peak_deceleration_m_s2: a,
                peak_jerk_m_s3: j,
                required_peak_force_n: force,
                store_travel_m: store_travel,
                store_force_upper_bound_n: store_force,
                kinetic_drop_j: drop,
                credited_capture_j: credit,
                unrecovered_braking_j: lost,
                capture_loss_j: credit - after_cap,
                store_loss_j: after_cap - after_store,
                accepted_j: added,
                overflow_j: spill,
                bound_failures: stage_failures,
            });
            elapsed += time;
            distance += travel;
            peak_force = peak_force.max(force);
            vin = stage.exit_speed_m_s;
            global_start = end;
        }
    }
    if c.handover == Handover::ContinuousTotalForce && !c.stages.is_empty() {
        push(
            &mut unknowns,
            "continuous-total-force-handover-is-assumed-not-proven",
        );
    }
    let capture = Capture {
        entry_kinetic_energy_j: kinetic,
        total_time_s: domain.then_some(elapsed),
        total_distance_m: domain.then_some(distance),
        required_peak_force_n: domain.then_some(peak_force),
        stages: if domain { Some(rows) } else { None },
    };
    let unresolved = if domain { 0.0 } else { kinetic };
    let wanted_standing = c.storage.standing_loss_w * c.storage.dwell_s;
    super::finite(&[wanted_standing])?;
    let standing = wanted_standing.min(state);
    state -= standing;
    if state < c.storage.reserve_j {
        push(&mut failures, "store-below-declared-reserve");
    }
    let requested =
        0.5 * c.effective_mass_kg * c.launch.target_speed_m_s * c.launch.target_speed_m_s;
    let mut release_allowed = domain && c.storage.departure_authorized;
    if c.storage.dwell_s > 0.0 && state > 0.0 && !c.storage.isolated_during_dwell {
        push(&mut failures, "energy-path-not-isolated-during-dwell");
        release_allowed = false;
    }
    if requested > 0.0 && !c.storage.controlled_forward_transfer {
        push(&mut failures, "controlled-forward-transfer-missing");
        release_allowed = false;
    }
    if c.launch.target_speed_m_s > c.booster.target_speed_m_s {
        push(&mut failures, "launch-target-exceeds-cruise-target");
        release_allowed = false;
    }
    let available = (state - c.storage.reserve_j).max(0.0);
    let delivered = if release_allowed {
        requested.min(available * c.storage.efficiency_release)
    } else {
        0.0
    };
    let withdrawn = if c.storage.efficiency_release > 0.0 {
        delivered / c.storage.efficiency_release
    } else {
        0.0
    };
    let withdrawn = withdrawn.min(available);
    let end_state = state - withdrawn;
    let initial_after_standing = (c.storage.initial_j - standing).max(0.0);
    let from_initial =
        (withdrawn.min(initial_after_standing) * c.storage.efficiency_release).min(delivered);
    let from_new = delivered - from_initial;
    let shortfall = if release_allowed {
        (requested - delivered).max(0.0)
    } else {
        0.0
    };
    if shortfall > 1e-9 * requested.max(1.0) {
        push(
            &mut failures,
            "requested-mechanical-launch-energy-not-available",
        );
    }
    let mut launch = None;
    let mut booster = None;
    if release_allowed {
        let speed = (2.0 * delivered / c.effective_mass_kg).sqrt();
        let p = Profile::new(
            0.0,
            speed,
            c.launch.max_acceleration_m_s2,
            c.launch.max_jerk_m_s3,
        )?;
        let motion = p.motion(
            c.effective_mass_kg,
            distance,
            &c.launch.mass_fractions,
            &c.launch.force_fractions,
        )?;
        if motion.distance_m > c.launch.available_stroke_m {
            push(&mut failures, "launch-stroke-exceeded");
        }
        if c.launch
            .force_limit_n
            .is_some_and(|limit| motion.required_peak_force_n > limit)
        {
            push(&mut failures, "launch-force-limit-exceeded");
        }
        if c.launch.force_limit_n.is_none() {
            push(&mut unknowns, "launcher-available-force-unspecified");
        }
        let b = Profile::new(
            speed,
            c.booster.target_speed_m_s,
            c.booster.max_acceleration_m_s2,
            c.booster.max_jerk_m_s3,
        )?;
        let bm = b.motion(c.effective_mass_kg, distance + motion.distance_m, &[], &[])?;
        let source_energy = 0.5
            * c.effective_mass_kg
            * (c.booster.target_speed_m_s * c.booster.target_speed_m_s - speed * speed)
            / c.booster.efficiency;
        let source_power = bm.peak_mechanical_power_w / c.booster.efficiency;
        if bm.distance_m > c.booster.available_stroke_m {
            push(
                &mut failures,
                "booster-acceleration-path-exceeds-declared-stroke",
            );
        }
        if c.booster
            .force_limit_n
            .is_some_and(|limit| bm.required_peak_force_n > limit)
        {
            push(&mut failures, "booster-force-limit-exceeded");
        }
        if c.booster
            .source_power_limit_w
            .is_some_and(|limit| source_power > limit)
        {
            push(&mut failures, "booster-source-power-limit-exceeded");
        }
        if c.booster.force_limit_n.is_none() {
            push(&mut unknowns, "booster-available-force-unspecified");
        }
        if c.booster.source_power_limit_w.is_none() {
            push(&mut unknowns, "booster-available-source-power-unspecified");
        }
        if bm.distance_m > 0.0 {
            push(
                &mut unknowns,
                "booster-force-distribution-and-coupler-loads-unresolved",
            );
            push(
                &mut unknowns,
                "booster-path-is-not-installed-hardware-length-or-force-map",
            );
        }
        booster = Some(BoosterResult {
            motion: bm,
            source_energy_j: source_energy,
            peak_source_power_w: source_power,
        });
        launch = Some(motion);
    }
    let occupation = launch
        .as_ref()
        .map(|l| elapsed + c.storage.dwell_s + l.time_s + c.reset_s);
    let margin = occupation.map(|t| c.headway_s - t);
    if margin.is_some_and(|m| m < 0.0) {
        push(&mut failures, "exclusive-resource-cycle-exceeds-headway");
    }
    if occupation.is_none() {
        push(
            &mut unknowns,
            "held-blocked-or-unsupported-departure-does-not-complete-resource-cycle",
        );
    }
    let departure = if !domain {
        "unsupported-motion-domain"
    } else if !c.storage.departure_authorized {
        "held-no-departure-authority"
    } else if !release_allowed {
        "blocked"
    } else {
        "nominal-transfer-only"
    };
    let storage = Storage {
        initial_j: c.storage.initial_j,
        accepted_j: accepted,
        capture_conversion_loss_j: cap_loss,
        store_conversion_loss_j: store_loss,
        overflow_j: overflow,
        unrecovered_braking_j: unrecovered,
        unresolved_capture_j: unresolved,
        standing_loss_j: standing,
        withdrawn_j: withdrawn,
        release_loss_j: withdrawn - delivered,
        delivered_j: delivered,
        delivered_from_initial_j: from_initial,
        delivered_from_new_capture_j: from_new,
        request_shortfall_j: shortfall,
        end_j: end_state,
        balance_residual_j: c.storage.initial_j + accepted - standing - withdrawn - end_state,
        departure_state: departure,
        nominal_transfer_only: true,
    };
    let residual = kinetic + c.storage.initial_j
        - cap_loss
        - store_loss
        - overflow
        - unrecovered
        - unresolved
        - standing
        - (withdrawn - delivered)
        - delivered
        - end_state;
    super::finite(&[
        requested,
        state,
        available,
        delivered,
        withdrawn,
        end_state,
        from_initial,
        from_new,
        shortfall,
        residual,
        storage.balance_residual_j,
    ])?;
    for n in [occupation, margin].into_iter().flatten() {
        super::finite(&[n])?;
    }
    if let Some(b) = &booster {
        super::finite(&[b.source_energy_j, b.peak_source_power_w])?;
    }
    Ok(Envelope {
        id: c.id.clone(),
        execution: "complete",
        necessary_bounds: if failures.is_empty() {
            "unknown"
        } else {
            "fail"
        },
        failures,
        unknowns,
        capture,
        storage,
        sizing,
        launch,
        booster,
        resource: Resource {
            occupation_s: occupation,
            headway_margin_s: margin,
        },
        energy_residual_j: residual,
        physical_accepted: false,
        engineering_accepted: false,
        manufacturing_release: false,
        operating_release: false,
        selected_reference_changed: false,
        movement_authority: false,
    })
}
pub fn execute(request: Request) -> Result<BatchResult, String> {
    if request.schema != REQUEST_SCHEMA {
        return Err("Unknown multistage arrestor schema".into());
    }
    if request.cases.is_empty() || request.cases.len() > MAX_CASES {
        return Err("1-1000 explicit cases required".into());
    }
    let mut ids = HashSet::new();
    let mut output = Vec::with_capacity(request.cases.len());
    for case in request.cases {
        if !ids.insert(case.id.clone()) {
            return Err("Duplicate case id".into());
        }
        output.push(evaluate(&case)?);
    }
    Ok(BatchResult {
        schema: RESULT_SCHEMA,
        cases: output,
    })
}
