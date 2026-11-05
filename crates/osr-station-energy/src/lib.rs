//! Ideal energy/motion requirements, not a contact simulator or hardware proof.
//! Every input uses the SI unit suffix in its field name. No reference train,
//! operating speed, launcher length, equipment capacity or efficiency is supplied
//! by this library. Calculations never grant engineering or operating approval.

pub mod arrestor;

use serde::{Deserialize, Serialize};
use std::collections::HashSet;

pub const MAX_INPUT_BYTES: usize = 8 * 1024 * 1024;
pub const MAX_CASES: usize = 10_000;
pub const REQUEST_SCHEMA: &str = "osr-station-energy-request/1";
pub const RESULT_SCHEMA: &str = "osr-station-energy-result/1";

#[derive(Debug, Clone, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct Request {
    pub schema: String,
    pub cases: Vec<Case>,
}

#[derive(Debug, Clone, Copy, Deserialize, Serialize, PartialEq, Eq)]
#[serde(rename_all = "kebab-case")]
pub enum CaptureProfile {
    ControlledConstant,
    UnpreloadedSpring,
}

#[derive(Debug, Clone, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct Case {
    pub id: String,
    pub effective_mass_kg: f64,
    pub physical_mass_kg: f64,
    pub capture_speed_m_s: f64,
    pub capture_deceleration_m_s2: f64,
    pub capture_stroke_m: f64,
    pub capture_profile: CaptureProfile,
    pub forward_transfer: bool,
    pub efficiency_capture: f64,
    pub efficiency_store: f64,
    pub efficiency_release: f64,
    pub store_capacity_j: f64,
    pub store_initial_j: f64,
    pub store_reserve_j: f64,
    pub standing_loss_w: f64,
    pub dwell_s: f64,
    pub launch_request_j: f64,
    pub release_duration_s: f64,
    pub booster_offset_m: f64,
    pub booster_length_m: f64,
    pub target_speed_m_s: f64,
    pub resistance_n: f64,
    pub grade_fraction: f64,
    pub booster_efficiency: f64,
    pub reset_s: f64,
    pub headway_s: f64,
    pub capture_force_limit_n: Option<f64>,
    pub max_booster_acceleration_m_s2: Option<f64>,
    pub available_booster_force_n: Option<f64>,
    pub source_power_limit_w: Option<f64>,
    pub independent_brake_deceleration_m_s2: Option<f64>,
}

#[derive(Debug, Clone, Serialize)]
pub struct BatchResult {
    pub schema: &'static str,
    pub cases: Vec<Envelope>,
}

#[derive(Debug, Clone, Serialize)]
pub struct Capture {
    pub kinetic_energy_j: f64,
    pub required_stroke_m: Option<f64>,
    pub time_s: Option<f64>,
    pub required_peak_force_n: Option<f64>,
    pub opposing_work_j: f64,
    pub drive_work_needed_j: f64,
    pub available_braking_work_j: f64,
    pub credited_mechanical_capture_j: f64,
    pub unrecovered_braking_j: f64,
    pub unresolved_work_j: f64,
}

#[derive(Debug, Clone, Serialize)]
pub struct Storage {
    pub initial_j: f64,
    pub accepted_j: f64,
    pub capture_conversion_loss_j: f64,
    pub store_conversion_loss_j: f64,
    pub overflow_j: f64,
    pub standing_loss_j: f64,
    pub withdrawn_j: f64,
    pub release_loss_j: f64,
    pub delivered_j: f64,
    pub delivered_from_initial_j: f64,
    pub delivered_from_new_capture_j: f64,
    pub request_shortfall_j: f64,
    pub end_j: f64,
    pub balance_residual_j: f64,
}

#[derive(Debug, Clone, Serialize)]
pub struct Motion {
    pub ideal_launch_speed_m_s: f64,
    pub booster_reached: bool,
    pub coast_distance_travelled_m: f64,
    pub coast_time_s: Option<f64>,
    pub booster_entry_speed_m_s: Option<f64>,
    pub coast_opposing_work_j: f64,
}

#[derive(Debug, Clone, Serialize, Default)]
pub struct Booster {
    pub net_acceleration_m_s2: Option<f64>,
    pub required_force_n: Option<f64>,
    pub mechanical_work_j: Option<f64>,
    pub peak_mechanical_power_w: Option<f64>,
    pub source_energy_j: Option<f64>,
    pub peak_source_power_w: Option<f64>,
    pub time_s: Option<f64>,
}

#[derive(Debug, Clone, Serialize)]
pub struct Braking {
    pub assumed_net_deceleration_m_s2: Option<f64>,
    pub capture_failure_stopping_distance_m: Option<f64>,
    pub physical_capability_verified: bool,
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
    pub motion: Motion,
    pub booster: Booster,
    pub braking: Braking,
    pub resource: Resource,
    /// Balance of capture and storage, including explicitly unresolved work.
    /// Booster purchased energy and coast work are reported separately.
    pub energy_residual_j: f64,
    pub physical_accepted: bool,
    pub engineering_accepted: bool,
    pub operating_release: bool,
    pub selected_reference_changed: bool,
}

fn finite(values: &[f64]) -> Result<(), String> {
    if values.iter().any(|v| !v.is_finite()) {
        return Err("Non-finite input or derived overflow".into());
    }
    Ok(())
}

fn nonnegative(values: &[f64]) -> Result<(), String> {
    finite(values)?;
    if values.iter().any(|v| *v < 0.0) {
        return Err("Nonnegative SI quantity required".into());
    }
    Ok(())
}

fn validate(c: &Case) -> Result<(), String> {
    if c.id.trim().is_empty() || c.id.len() > 128 {
        return Err("Nonempty case id of at most 128 UTF-8 bytes required".into());
    }
    nonnegative(&[
        c.effective_mass_kg,
        c.physical_mass_kg,
        c.capture_speed_m_s,
        c.capture_deceleration_m_s2,
        c.capture_stroke_m,
        c.store_capacity_j,
        c.store_initial_j,
        c.store_reserve_j,
        c.standing_loss_w,
        c.dwell_s,
        c.launch_request_j,
        c.release_duration_s,
        c.booster_offset_m,
        c.booster_length_m,
        c.target_speed_m_s,
        c.resistance_n,
        c.reset_s,
        c.headway_s,
    ])?;
    finite(&[c.grade_fraction])?;
    if c.physical_mass_kg == 0.0
        || c.effective_mass_kg < c.physical_mass_kg
        || c.capture_deceleration_m_s2 == 0.0
        || c.target_speed_m_s == 0.0
        || c.headway_s == 0.0
    {
        return Err("Positive masses/deceleration/target speed/headway; effective mass >= physical mass required".into());
    }
    for eta in [
        c.efficiency_capture,
        c.efficiency_store,
        c.efficiency_release,
        c.booster_efficiency,
    ] {
        finite(&[eta])?;
        if !(0.0..=1.0).contains(&eta) {
            return Err("Efficiency outside [0,1]".into());
        }
    }
    if c.booster_efficiency == 0.0 {
        return Err("Positive booster efficiency required".into());
    }
    if c.store_initial_j > c.store_capacity_j || c.store_reserve_j > c.store_capacity_j {
        return Err("Storage initial/reserve energy exceeds capacity".into());
    }
    for v in [
        c.capture_force_limit_n,
        c.max_booster_acceleration_m_s2,
        c.available_booster_force_n,
        c.source_power_limit_w,
        c.independent_brake_deceleration_m_s2,
    ]
    .into_iter()
    .flatten()
    {
        nonnegative(&[v])?;
    }
    if c.independent_brake_deceleration_m_s2 == Some(0.0) {
        return Err("Positive assumed independent net braking deceleration required".into());
    }
    Ok(())
}

fn tag(list: &mut Vec<String>, value: &str) {
    list.push(value.into());
}

/// Evaluate one declared event. To model a later event sharing the store,
/// explicitly feed its predecessor's `storage.end_j` into `store_initial_j`.
pub fn evaluate(c: &Case) -> Result<Envelope, String> {
    validate(c)?;
    let mut failures = Vec::new();
    let mut unknowns = vec![
        "launch-speed-is-lossless-release-energy-upper-bound".into(),
        "release-stroke-contact-coupler-and-jerk-dynamics-unverified".into(),
        "storage-charge-discharge-power-and-repeated-thermal-duty-unverified".into(),
        "independent-braking-and-failed-capture-protection-unverified".into(),
    ];
    let m = c.effective_mass_kg;
    let v = c.capture_speed_m_s;
    let kinetic = 0.5 * m * v * v;
    let opposing_force =
        c.resistance_n + c.physical_mass_kg * 9.80665 * c.grade_fraction.atan().sin();
    finite(&[kinetic, opposing_force])?;
    let spring = c.capture_profile == CaptureProfile::UnpreloadedSpring;
    let unsupported_spring = spring && (c.grade_fraction != 0.0 || c.resistance_n != 0.0);
    let (stroke, capture_time, peak, opposing_work, drive_needed, brake_work, unresolved) =
        if unsupported_spring {
            tag(
                &mut unknowns,
                "spring-with-grade-or-resistance-outside-analytical-domain",
            );
            (None, None, None, 0.0, 0.0, 0.0, kinetic)
        } else {
            let distance = if spring {
                v * v / c.capture_deceleration_m_s2
            } else {
                v * v / (2.0 * c.capture_deceleration_m_s2)
            };
            let time = if spring {
                std::f64::consts::FRAC_PI_2 * v / c.capture_deceleration_m_s2
            } else {
                v / c.capture_deceleration_m_s2
            };
            let work = opposing_force * distance;
            let raw_brake = (kinetic - work).max(0.0);
            let drive = (work - kinetic).max(0.0);
            let force = if v == 0.0 {
                0.0
            } else if spring {
                m * c.capture_deceleration_m_s2
            } else {
                (m * c.capture_deceleration_m_s2 - opposing_force).max(0.0)
            };
            finite(&[distance, time, work, raw_brake, drive, force])?;
            (
                Some(distance),
                Some(time),
                Some(force),
                work,
                drive,
                raw_brake,
                0.0,
            )
        };
    let mut capture_possible = !unsupported_spring;
    if stroke.is_some_and(|s| s > c.capture_stroke_m) {
        tag(&mut failures, "insufficient-capture-stroke");
        capture_possible = false;
    }
    if drive_needed > 0.0 {
        tag(
            &mut failures,
            "capture-net-deceleration-requires-positive-drive",
        );
        capture_possible = false;
    }
    if let (Some(required), Some(limit)) = (peak, c.capture_force_limit_n) {
        if required > limit {
            tag(&mut failures, "capture-force-limit-exceeded");
            capture_possible = false;
        }
    } else if v > 0.0 {
        tag(&mut unknowns, "capture-force-capability-unspecified");
    }
    let credited = if capture_possible { brake_work } else { 0.0 };
    let unrecovered = brake_work - credited;
    let after_capture = credited * c.efficiency_capture;
    let after_store_conversion = after_capture * c.efficiency_store;
    let accepted = after_store_conversion.min(c.store_capacity_j - c.store_initial_j);
    let overflow = after_store_conversion - accepted;
    let requested_standing_loss = c.standing_loss_w * c.dwell_s;
    finite(&[
        after_capture,
        after_store_conversion,
        accepted,
        overflow,
        requested_standing_loss,
    ])?;
    let standing_loss = requested_standing_loss.min(c.store_initial_j + accepted);
    let before_release = c.store_initial_j + accepted - standing_loss;
    let available = (before_release - c.store_reserve_j).max(0.0);
    let transfer_allowed = c.forward_transfer && c.release_duration_s > 0.0;
    if c.launch_request_j > 0.0 && !c.forward_transfer {
        tag(&mut failures, "forward-energy-transfer-missing");
    }
    if c.launch_request_j > 0.0 && c.release_duration_s == 0.0 {
        tag(&mut failures, "positive-launch-work-needs-release-duration");
    }
    if before_release < c.store_reserve_j {
        tag(&mut failures, "store-below-declared-reserve");
    }
    let delivered = if transfer_allowed {
        c.launch_request_j.min(available * c.efficiency_release)
    } else {
        0.0
    };
    let withdrawn = if c.efficiency_release > 0.0 {
        (delivered / c.efficiency_release).min(available)
    } else {
        0.0
    };
    finite(&[before_release, available, delivered, withdrawn])?;
    let end = before_release - withdrawn;
    let initial_after_standing = (c.store_initial_j - standing_loss).max(0.0);
    let delivered_initial =
        (withdrawn.min(initial_after_standing) * c.efficiency_release).min(delivered);
    let delivered_new = delivered - delivered_initial;
    let shortfall = c.launch_request_j - delivered;
    if shortfall > 1e-9 * c.launch_request_j.max(1.0) {
        tag(&mut failures, "launch-energy-request-not-met");
    }
    let storage = Storage {
        initial_j: c.store_initial_j,
        accepted_j: accepted,
        capture_conversion_loss_j: credited - after_capture,
        store_conversion_loss_j: after_capture - after_store_conversion,
        overflow_j: overflow,
        standing_loss_j: standing_loss,
        withdrawn_j: withdrawn,
        release_loss_j: withdrawn - delivered,
        delivered_j: delivered,
        delivered_from_initial_j: delivered_initial,
        delivered_from_new_capture_j: delivered_new,
        request_shortfall_j: shortfall,
        end_j: end,
        balance_residual_j: c.store_initial_j + accepted - standing_loss - withdrawn - end,
    };
    let launch_speed = (2.0 * delivered / m).sqrt();
    let requested_coast_work = opposing_force * c.booster_offset_m;
    finite(&[launch_speed, requested_coast_work])?;
    let coast_end_energy = delivered - requested_coast_work;
    let stalled = c.booster_offset_m > 0.0
        && ((opposing_force > 0.0 && coast_end_energy < 0.0)
            || (delivered == 0.0 && opposing_force >= 0.0));
    let motion = if stalled {
        tag(&mut failures, "booster-offset-unreachable");
        let travelled = if opposing_force > 0.0 {
            (delivered / opposing_force).min(c.booster_offset_m)
        } else {
            0.0
        };
        let time = if launch_speed > 0.0 && opposing_force > 0.0 {
            Some(m * launch_speed / opposing_force)
        } else {
            None
        };
        Motion {
            ideal_launch_speed_m_s: launch_speed,
            booster_reached: false,
            coast_distance_travelled_m: travelled,
            coast_time_s: time,
            booster_entry_speed_m_s: None,
            coast_opposing_work_j: opposing_force * travelled,
        }
    } else {
        let entry = (2.0 * coast_end_energy.max(0.0) / m).sqrt();
        let time = if c.booster_offset_m == 0.0 {
            0.0
        } else {
            2.0 * c.booster_offset_m / (launch_speed + entry)
        };
        finite(&[entry, time])?;
        Motion {
            ideal_launch_speed_m_s: launch_speed,
            booster_reached: true,
            coast_distance_travelled_m: c.booster_offset_m,
            coast_time_s: Some(time),
            booster_entry_speed_m_s: Some(entry),
            coast_opposing_work_j: requested_coast_work,
        }
    };
    let mut booster = Booster::default();
    if let Some(entry) = motion.booster_entry_speed_m_s {
        if entry > c.target_speed_m_s {
            tag(
                &mut failures,
                "target-speed-below-coast-speed-requires-braking",
            );
        } else if c.booster_length_m == 0.0 && entry < c.target_speed_m_s {
            tag(
                &mut failures,
                "positive-speed-increase-needs-booster-length",
            );
        } else {
            let a = if c.booster_length_m == 0.0 {
                0.0
            } else {
                (c.target_speed_m_s * c.target_speed_m_s - entry * entry)
                    / (2.0 * c.booster_length_m)
            };
            let force = if c.booster_length_m == 0.0 {
                0.0
            } else {
                m * a + opposing_force
            };
            let work = force * c.booster_length_m;
            let time = 2.0 * c.booster_length_m / (entry + c.target_speed_m_s);
            finite(&[a, force, work, time])?;
            booster.net_acceleration_m_s2 = Some(a);
            booster.required_force_n = Some(force);
            booster.mechanical_work_j = Some(work);
            booster.time_s = Some(time);
            if force >= 0.0 {
                let peak_power = force * entry.max(c.target_speed_m_s);
                let source_energy = work / c.booster_efficiency;
                let source_power = peak_power / c.booster_efficiency;
                finite(&[peak_power, source_energy, source_power])?;
                booster.peak_mechanical_power_w = Some(peak_power);
                booster.source_energy_j = Some(source_energy);
                booster.peak_source_power_w = Some(source_power);
                if c.source_power_limit_w
                    .is_some_and(|limit| source_power > limit)
                {
                    tag(&mut failures, "booster-source-power-limit-exceeded");
                }
            } else {
                tag(
                    &mut unknowns,
                    "negative-drive-regeneration-outside-booster-domain",
                );
            }
            if c.max_booster_acceleration_m_s2
                .is_some_and(|limit| a > limit)
            {
                tag(&mut failures, "booster-net-acceleration-limit-exceeded");
            }
            if c.available_booster_force_n
                .is_some_and(|limit| force > limit)
            {
                tag(&mut failures, "booster-force-limit-exceeded");
            }
            if c.available_booster_force_n.is_none() {
                tag(&mut unknowns, "booster-available-force-unspecified");
            }
            if c.source_power_limit_w.is_none() {
                tag(&mut unknowns, "booster-available-source-power-unspecified");
            }
        }
    }
    let stopping_distance = c
        .independent_brake_deceleration_m_s2
        .map(|a| v * v / (2.0 * a));
    let occupation = capture_time.map(|time| time + c.dwell_s + c.release_duration_s + c.reset_s);
    let headway_margin = occupation.map(|time| c.headway_s - time);
    if headway_margin.is_some_and(|margin| margin < 0.0) {
        tag(
            &mut failures,
            "exclusive-capture-release-resource-exceeds-headway",
        );
    }
    let residual = kinetic + drive_needed + c.store_initial_j
        - opposing_work
        - unrecovered
        - unresolved
        - storage.capture_conversion_loss_j
        - storage.store_conversion_loss_j
        - storage.overflow_j
        - storage.standing_loss_j
        - storage.release_loss_j
        - delivered
        - end;
    finite(&[
        end,
        storage.balance_residual_j,
        delivered_initial,
        delivered_new,
        shortfall,
        residual,
        motion.coast_distance_travelled_m,
        motion.coast_opposing_work_j,
    ])?;
    for value in [
        stopping_distance,
        occupation,
        headway_margin,
        motion.coast_time_s,
    ]
    .into_iter()
    .flatten()
    {
        finite(&[value])?;
    }
    Ok(Envelope {
        id: c.id.clone(),
        execution: "complete",
        necessary_bounds: if !failures.is_empty() {
            "fail"
        } else if !unknowns.is_empty() {
            "unknown"
        } else {
            "pass"
        },
        failures,
        unknowns,
        capture: Capture {
            kinetic_energy_j: kinetic,
            required_stroke_m: stroke,
            time_s: capture_time,
            required_peak_force_n: peak,
            opposing_work_j: opposing_work,
            drive_work_needed_j: drive_needed,
            available_braking_work_j: brake_work,
            credited_mechanical_capture_j: credited,
            unrecovered_braking_j: unrecovered,
            unresolved_work_j: unresolved,
        },
        storage,
        motion,
        booster,
        braking: Braking {
            assumed_net_deceleration_m_s2: c.independent_brake_deceleration_m_s2,
            capture_failure_stopping_distance_m: stopping_distance,
            physical_capability_verified: false,
        },
        resource: Resource {
            occupation_s: occupation,
            headway_margin_s: headway_margin,
        },
        energy_residual_j: residual,
        physical_accepted: false,
        engineering_accepted: false,
        operating_release: false,
        selected_reference_changed: false,
    })
}

pub fn execute(request: Request) -> Result<BatchResult, String> {
    if request.schema != REQUEST_SCHEMA
        || request.cases.is_empty()
        || request.cases.len() > MAX_CASES
    {
        return Err("Exact request schema and 1..10000 cases required".into());
    }
    let mut ids = HashSet::new();
    let mut results = Vec::with_capacity(request.cases.len());
    for case in request.cases {
        if !ids.insert(case.id.clone()) {
            return Err("Duplicate case id".into());
        }
        results.push(evaluate(&case).map_err(|e| format!("{}: {e}", case.id))?);
    }
    Ok(BatchResult {
        schema: RESULT_SCHEMA,
        cases: results,
    })
}
