//! Shadow-mode onboard stack: runs `osr-odometry`, `osr-atp`, and
//! `osr-brake` in parallel with the simulator's countdown-based train
//! motion model, every tick, for every Traveling train.
//!
//! This is **integration evidence** for the Phase 2a SBC crates
//! (RFC 0005 §11). The sim's own kinematic model is not replaced —
//! the shadow runs alongside, exercises the real onboard decision
//! code with real scenario inputs, and produces a summary that's
//! folded into [`SimResult`].
//!
//! # What the shadow does each tick
//!
//! For each train in [`TrainPhase::Traveling`]:
//!
//! 1. Integrate a simple kinematic model (accel → cruise → decel)
//!    forward by `dt` seconds. Track head-offset-in-section and
//!    signed speed.
//! 2. Build a synthetic [`SensorTick`] from the integration step
//!    (wheel pulses derived from distance moved) and run
//!    [`odom_step`].
//! 3. Build a **local MA** whose end is at the far end of the
//!    current section. Because the sim's occupancy map already
//!    enforces the no-two-trains-in-one-section invariant globally,
//!    any ATP trip under this MA is a genuine bug in ATP or the
//!    kinematic model — not an interlocking mis-coordination. The
//!    full wayside-MA chain is exercised separately by the periodic
//!    [`crate::ma_check`] integration.
//! 4. Run [`atp_evaluate`] with that MA.
//! 5. Run [`brake_evaluate`] with the ATP command and all-false
//!    emergency sources (sim-driven faults like fire or derailment
//!    are not yet wired into the shadow; see §13 of RFC 0005
//!    for the future path).
//! 6. Record per-train tick statistics.
//!
//! On transition out of `Traveling` (section boundary crossed), the
//! shadow's kinematic state resets. On transition into `Traveling`
//! it re-seeds from the section geometry and consist.
//!
//! # What the shadow does NOT do
//!
//! - Override or influence the sim's own motion — the sim continues
//!   to teleport trains using its countdown model. This keeps the
//!   integration low-risk and backwards-compatible with every
//!   existing sim test.
//! - Talk to the consensus log. Local MAs are built directly from
//!   the network topology.
//! - Simulate wheel slip. `wheel_speed_mmps = measured_speed_mmps`
//!   always; WSP is exercised by its own proptests in `osr-brake`.

use osr_atp::{atp_evaluate, AtpOutcome, BrakeCommand, TriggerReason};
use osr_brake::{brake_evaluate, BrakeInputs, BrakeOutput, BrakeParams};
use osr_core::{ConsistDescriptor, Direction, Network, SectionId, TrackRef, TrainId};
use osr_interlocking::{far_end_of, forward_chain, MovementAuthority, MAX_MA_DISTANCE_MM, MA_VALIDITY_WINDOW_NS};
use osr_odometry::{odom_step, BaliseId, OdomCalibration, OdomState, SensorTick};
use serde::{Deserialize, Serialize};

use crate::train::{Heading, Train, TrainPhase};

// ---------------------------------------------------------------------------
// Shadow state
// ---------------------------------------------------------------------------

/// Per-train shadow state — kinematics + odometer + counters.
#[derive(Clone, Debug)]
pub struct OnboardShadow {
    pub train_id: TrainId,
    pub odom: OdomState,
    pub odom_cal: OdomCalibration,
    pub brake_params: BrakeParams,
    /// Kinematic state: meaningful only during Traveling. Reset to
    /// zero at section boundaries.
    pub kin: KinematicShadow,
    /// Rolling statistics across the full run.
    pub stats: OnboardStats,
    /// Last wall-time tick when this shadow was advanced. Used to
    /// compute `dt_ns` in the [`SensorTick`].
    pub last_t_ns: u64,
}

#[derive(Clone, Debug)]
pub struct KinematicShadow {
    /// Head offset within the current section in millimetres. Zero
    /// when the train is at the start of a section.
    pub head_offset_mm: i64,
    /// Signed speed in the heading direction, mm/s.
    pub speed_mmps: i32,
    /// Section the train is currently on. `None` when the train is
    /// not in Traveling phase.
    pub current_section: Option<SectionId>,
    /// Section length in mm (cached from network at section entry).
    pub section_length_mm: i64,
    /// V_max for this section in mm/s (min of consist max and section
    /// permanent speed).
    pub v_max_mmps: i32,
    /// Service accel in mm/s².
    pub accel_mmps2: i32,
    /// Emergency decel in mm/s² — used by the shadow to keep its
    /// trajectory at or below the ATP envelope (which also uses
    /// emergency decel).
    pub decel_mmps2: i32,
    /// Envelope-matching reaction time in ms. Added to the decel
    /// trigger so the shadow starts braking early enough to stay
    /// below the envelope, which has its own `d·t_react` offset.
    pub reaction_time_ms: u32,
    /// Current heading direction (forward/reverse in the line's array).
    pub heading_direction: Direction,
}

impl KinematicShadow {
    pub fn reset() -> Self {
        Self {
            head_offset_mm: 0,
            speed_mmps: 0,
            current_section: None,
            section_length_mm: 0,
            v_max_mmps: 0,
            accel_mmps2: 0,
            decel_mmps2: 0,
            reaction_time_ms: 0,
            heading_direction: Direction::Forward,
        }
    }
}

/// Cumulative per-train and per-event statistics.
#[derive(Clone, Debug, Default, Serialize, Deserialize)]
pub struct OnboardStats {
    pub ticks_release: u32,
    pub ticks_service: u32,
    pub ticks_emergency: u32,
    /// Peak friction effort commanded on any tick (ppt).
    pub peak_friction_ppt: u16,
    /// Peak regen request across the run (ppt).
    pub peak_regen_ppt: u16,
    /// Number of ticks where the ATP reason was Overspeed.
    pub overspeed_ticks: u32,
    /// Number of ticks where the ATP reason was EnvelopeApproach.
    pub approach_ticks: u32,
    /// First recorded Emergency trip, if any.
    pub first_emergency: Option<EmergencyRecord>,
    /// Total distance covered by the shadow kinematic model, mm.
    pub shadow_distance_mm: u64,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct EmergencyRecord {
    pub sim_time_s: u32,
    pub train: String,
    pub reason: String,
    pub speed_mmps: i32,
    pub envelope_mmps: Option<i32>,
    pub distance_to_end_mm: Option<i64>,
}

/// Fleet-wide summary folded into [`crate::sim::SimResult`].
#[derive(Clone, Debug, Default, Serialize, Deserialize)]
pub struct OnboardSummary {
    pub ticks_evaluated: u64,
    pub total_release_ticks: u64,
    pub total_service_ticks: u64,
    pub total_emergency_ticks: u64,
    pub total_overspeed_ticks: u64,
    pub total_approach_ticks: u64,
    pub per_train: Vec<PerTrainOnboard>,
    pub emergencies: Vec<EmergencyRecord>,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct PerTrainOnboard {
    pub train: String,
    pub ticks_release: u32,
    pub ticks_service: u32,
    pub ticks_emergency: u32,
    pub peak_friction_ppt: u16,
    pub peak_regen_ppt: u16,
    pub shadow_distance_km: f64,
}

// ---------------------------------------------------------------------------
// Construction and phase-change hooks
// ---------------------------------------------------------------------------

impl OnboardShadow {
    /// Build a fresh shadow for a newly initialised train.
    pub fn new(train: &Train) -> Self {
        let head = TrackRef {
            section: SectionId::new(0),
            offset_mm: 0,
            direction: Direction::Forward,
        };
        let odom_cal = OdomCalibration::light_metro_default();
        Self {
            train_id: train.id,
            odom: OdomState::new_at(train.id, head, odom_cal.min_uncertainty_mm, 0),
            odom_cal,
            brake_params: BrakeParams::light_metro_default(),
            kin: KinematicShadow::reset(),
            stats: OnboardStats::default(),
            last_t_ns: 0,
        }
    }

    /// Seed the kinematic state on entry to a new section. Called by
    /// the sim once the train's phase transitions into Traveling.
    pub fn on_enter_section(
        &mut self,
        section: SectionId,
        network: &Network,
        consist: &ConsistDescriptor,
        heading: Heading,
        t_s: u32,
    ) {
        let sec = network.section(section);
        let section_length_mm = sec.length_mm as i64;
        // v_max: min of consist and section, converted to mm/s.
        let v_max_mps = sec.max_speed_mps.min(consist.max_speed_mps);
        let v_max_mmps = (v_max_mps * 1000.0) as i32;
        let accel_mmps2 = (consist.service_accel_mps2 * 1000.0) as i32;
        // Shadow uses the consist's *emergency* decel, not service,
        // so the shadow's kinematic trajectory stays at or below the
        // ATP envelope (which is also derived from the emergency
        // curve) across the entire approach-to-stop. Using service
        // decel would be more realistic for ride comfort but would
        // physically overshoot the envelope near MA end — a
        // shadow-integration artifact, not a real SIL-4 concern
        // (the brake crate's service→emergency transition is
        // exercised by its own unit and proptests).
        let min_e_decel = consist
            .braking
            .emergency
            .iter()
            .map(|(_, d)| *d)
            .fold(f32::INFINITY, f32::min);
        let decel_mmps2 = (min_e_decel * 1000.0).max(1.0) as i32;
        let reaction_time_ms = consist.braking.reaction_time_ms;

        let direction = direction_for_section(section, network, heading);
        self.kin = KinematicShadow {
            head_offset_mm: 0,
            speed_mmps: 0,
            current_section: Some(section),
            section_length_mm,
            v_max_mmps,
            accel_mmps2,
            decel_mmps2,
            reaction_time_ms,
            heading_direction: direction,
        };
        // Seed the odometer at the start of the section.
        let head = TrackRef {
            section,
            offset_mm: 0,
            direction,
        };
        self.odom = OdomState::new_at(
            self.train_id,
            head,
            self.odom_cal.min_uncertainty_mm,
            (t_s as u64).saturating_mul(1_000_000_000),
        );
        self.last_t_ns = self.odom.last_timestamp_ns;
    }

    /// Called when the train leaves Traveling phase (e.g. section
    /// arrival or a phase flip). Clears the kinematic shadow so the
    /// next tick in Traveling re-seeds cleanly.
    pub fn on_leave_section(&mut self) {
        self.kin = KinematicShadow::reset();
    }
}

// ---------------------------------------------------------------------------
// Tick
// ---------------------------------------------------------------------------

/// One tick of the shadow onboard stack. Safe to call only when the
/// train is in [`TrainPhase::Traveling`]; otherwise returns `None`.
#[must_use]
pub fn onboard_tick(
    shadow: &mut OnboardShadow,
    train: &Train,
    network: &Network,
    t_s: u32,
    dt_s: f32,
) -> Option<TickReport> {
    let section = match train.phase {
        TrainPhase::Traveling { section, .. } => section,
        _ => return None,
    };

    // Lazy re-seed if the shadow doesn't yet know about this section.
    if shadow.kin.current_section != Some(section) {
        shadow.on_enter_section(section, network, &train.consist, train.heading, t_s);
    }

    let now_ns = (t_s as u64).saturating_mul(1_000_000_000);

    // 1. Kinematic integration (very simple: accel → cruise → decel).
    advance_kinematic(&mut shadow.kin, dt_s);

    // If the shadow has arrived at (or past) the section end,
    // we are waiting for the sim to transition Traveling→Dwelling.
    // The shadow integrates with emergency decel while the sim uses
    // service decel + reaction time, so the shadow typically
    // arrives a few ticks ahead. In that window, head = MA end and
    // distance_to_end = 0 would spuriously trip HeadPastMaEnd.
    // Skip ATP evaluation until the sim catches up and resets us,
    // but first sync the odometer view to the at-rest-at-end state.
    if shadow.kin.head_offset_mm >= shadow.kin.section_length_mm {
        shadow.odom.head.offset_mm = shadow.kin.section_length_mm;
        shadow.odom.speed_mmps = 0;
        shadow.odom.speed_uncertainty_mmps = 0;
        shadow.odom.position_uncertainty_mm = 0;
        shadow.last_t_ns = now_ns;
        return None;
    }

    // Distance moved on this tick.
    let prev_offset = shadow.odom.head.offset_mm;
    let new_offset = shadow.kin.head_offset_mm.min(shadow.kin.section_length_mm);
    let distance_mm = (new_offset - prev_offset).max(0);
    shadow.stats.shadow_distance_mm = shadow
        .stats
        .shadow_distance_mm
        .saturating_add(distance_mm as u64);

    // 2. Build synthetic sensors.
    let wheel_pulses =
        ((distance_mm as i64) * i64::from(shadow.odom_cal.pulses_per_meter) / 1_000) as i32;
    let sensors = SensorTick {
        timestamp_ns: now_ns,
        wheel_pulses,
        gnss: None,
        balise: None,
    };

    // 3. Odometry.
    shadow.odom = odom_step(&shadow.odom, &shadow.odom_cal, &sensors, network);
    // In the shadow we have perfect kinematic ground truth, so we
    // override the sensor-fusion uncertainties to zero and sync
    // position+speed to the integrator exactly. Sensor-noise
    // handling is exercised by osr-odometry's own tests; here the
    // focus is ATP+brake integration.
    shadow.odom.head.offset_mm = new_offset;
    shadow.odom.speed_mmps = shadow.kin.speed_mmps;
    shadow.odom.speed_uncertainty_mmps = 0;
    shadow.odom.position_uncertainty_mm = 0;
    shadow.last_t_ns = now_ns;
    let _ = BaliseId::new(0); // silence "unused import" if balises aren't exercised

    // 4. Build a local MA: walk forward_chain from the current head
    //    up to MAX_MA_DISTANCE_MM, exactly as osr-interlocking would.
    //    This ensures the MA end is several sections ahead when the
    //    train is at a section boundary, so a train arriving at a
    //    station doesn't trip on position-uncertainty alone.
    let ma = local_movement_authority(train.id, shadow.odom.head, network, now_ns);

    // 5. ATP.
    let atp_out = atp_evaluate(
        &shadow.odom.to_train_state(),
        &ma,
        &train.consist,
        network,
        now_ns,
    );

    // 6. Brake.
    let brake_inputs = BrakeInputs {
        atp_command: atp_out.command,
        vigilance_emergency: false,
        fire_emergency: false,
        derailment_emergency: false,
        driver_emergency: false,
        park_requested: false,
        measured_speed_mmps: shadow.odom.speed_mmps,
        wheel_speed_mmps: shadow.odom.speed_mmps,
        regen_available_ppt: 800, // placeholder: 80 % availability
        now_ns,
    };
    let brake_out = brake_evaluate(&brake_inputs, &shadow.brake_params);

    // 7. Stats.
    record_tick(
        &mut shadow.stats,
        t_s,
        train.id,
        &atp_out,
        &brake_out,
        shadow.odom.speed_mmps,
    );

    Some(TickReport {
        atp: atp_out,
        brake: brake_out,
    })
}

#[derive(Clone, Debug)]
pub struct TickReport {
    pub atp: AtpOutcome,
    pub brake: BrakeOutput,
}

// ---------------------------------------------------------------------------
// Kinematic integrator
// ---------------------------------------------------------------------------

/// Advance the kinematic model by `dt_s` seconds.
///
/// Sub-stepped at 100 ms resolution internally: with a 1 s tick that
/// is 10 sub-steps. This makes the discrete trajectory converge on
/// the continuous envelope math used by ATP, so the shadow doesn't
/// exceed the envelope through coarse-time integration error.
fn advance_kinematic(k: &mut KinematicShadow, dt_s: f32) {
    if dt_s <= 0.0 {
        return;
    }
    let total_ms = (dt_s * 1000.0) as i32;
    if total_ms <= 0 {
        return;
    }
    const SUB_MS: i32 = 100;
    let mut remaining_ms = total_ms;
    while remaining_ms > 0 {
        let step_ms = remaining_ms.min(SUB_MS);
        advance_kinematic_substep(k, step_ms);
        remaining_ms -= step_ms;
        if k.head_offset_mm >= k.section_length_mm {
            break;
        }
    }
}

fn advance_kinematic_substep(k: &mut KinematicShadow, dt_ms: i32) {
    // Decide phase: decel if braking distance + reaction-time margin ≥
    // remaining, accel if below v_max, else cruise.
    //
    // The reaction margin has two components:
    // 1. `sub_step_margin_mm = v · dt` — one sub-step of cruise that
    //    would otherwise occur between the trigger firing and decel
    //    engaging.
    // 2. `envelope_reaction_mm = v · t_react` — matches the `d·t`
    //    subtracted term in the ATP envelope. Without this, a
    //    continuous emergency-decel trajectory exceeds the envelope
    //    by `d·t_react ≈ 480 mm/s`, which is too close to the
    //    OVERSPEED_EMERGENCY_MARGIN and trips Emergency under
    //    small discretization noise.
    let remaining = (k.section_length_mm - k.head_offset_mm).max(0);
    let v = i64::from(k.speed_mmps.max(0));
    let d = i64::from(k.decel_mmps2.max(1));
    let braking_distance_mm = (v.saturating_mul(v)) / (2 * d);
    let sub_step_margin_mm = v.saturating_mul(i64::from(dt_ms)) / 1000;
    let envelope_reaction_mm = v.saturating_mul(i64::from(k.reaction_time_ms)) / 1000;
    let decel_trigger_distance = braking_distance_mm
        .saturating_add(sub_step_margin_mm)
        .saturating_add(envelope_reaction_mm);

    let accel_mmps2 = if decel_trigger_distance >= remaining {
        -k.decel_mmps2
    } else if k.speed_mmps < k.v_max_mmps {
        k.accel_mmps2
    } else {
        0
    };

    let dv = (i64::from(accel_mmps2) * i64::from(dt_ms)) / 1000;
    let new_speed = (i64::from(k.speed_mmps) + dv).max(0);
    let avg_speed = (i64::from(k.speed_mmps) + new_speed) / 2;
    let dx = (avg_speed * i64::from(dt_ms)) / 1000;
    k.speed_mmps = new_speed.min(i64::from(k.v_max_mmps)).max(0) as i32;
    k.head_offset_mm = (k.head_offset_mm + dx).min(k.section_length_mm);
    if k.head_offset_mm >= k.section_length_mm {
        k.speed_mmps = 0;
    }
}

// ---------------------------------------------------------------------------
// Local MA
// ---------------------------------------------------------------------------

fn local_movement_authority(
    train_id: TrainId,
    head: TrackRef,
    network: &Network,
    now_ns: u64,
) -> MovementAuthority {
    let chain = forward_chain(network, head, MAX_MA_DISTANCE_MM);
    let end_section = chain.last().copied().unwrap_or(head.section);
    let end = far_end_of(network, end_section, head.direction);
    MovementAuthority {
        train_id,
        end,
        applicable_restrictions: vec![],
        valid_until_ns: now_ns.saturating_add(MA_VALIDITY_WINDOW_NS),
        derived_from_entry_id: None,
        has_known_position: true,
    }
}

// ---------------------------------------------------------------------------
// Direction mapping
// ---------------------------------------------------------------------------

fn direction_for_section(section: SectionId, network: &Network, heading: Heading) -> Direction {
    // `heading` is Forward/Reverse relative to the line. If the section
    // is in `forward_sections`, a Forward heading means the track
    // Direction is Forward. We scan the owning line to decide.
    for line in &network.lines {
        if line.forward_sections.contains(&section) {
            return match heading {
                Heading::Forward => Direction::Forward,
                Heading::Reverse => Direction::Reverse,
            };
        }
        if line.reverse_sections.contains(&section) {
            return match heading {
                Heading::Forward => Direction::Reverse,
                Heading::Reverse => Direction::Forward,
            };
        }
    }
    Direction::Forward
}

// ---------------------------------------------------------------------------
// Stat recording
// ---------------------------------------------------------------------------

fn record_tick(
    stats: &mut OnboardStats,
    t_s: u32,
    train_id: TrainId,
    atp_out: &AtpOutcome,
    brake_out: &BrakeOutput,
    speed_mmps: i32,
) {
    match brake_out.command {
        BrakeCommand::Release => stats.ticks_release = stats.ticks_release.saturating_add(1),
        BrakeCommand::Service(_) => stats.ticks_service = stats.ticks_service.saturating_add(1),
        BrakeCommand::Emergency => stats.ticks_emergency = stats.ticks_emergency.saturating_add(1),
    }
    if brake_out.friction_effort_ppt > stats.peak_friction_ppt {
        stats.peak_friction_ppt = brake_out.friction_effort_ppt;
    }
    if brake_out.regen_request_ppt > stats.peak_regen_ppt {
        stats.peak_regen_ppt = brake_out.regen_request_ppt;
    }
    match atp_out.reason {
        TriggerReason::Overspeed => {
            stats.overspeed_ticks = stats.overspeed_ticks.saturating_add(1);
        }
        TriggerReason::EnvelopeApproach => {
            stats.approach_ticks = stats.approach_ticks.saturating_add(1);
        }
        _ => {}
    }
    if matches!(brake_out.command, BrakeCommand::Emergency) && stats.first_emergency.is_none() {
        stats.first_emergency = Some(EmergencyRecord {
            sim_time_s: t_s,
            train: train_id.to_string(),
            reason: format!("{:?}", atp_out.reason),
            speed_mmps,
            envelope_mmps: atp_out.envelope_mmps,
            distance_to_end_mm: atp_out.distance_to_end_mm,
        });
    }
}

// ---------------------------------------------------------------------------
// Summary
// ---------------------------------------------------------------------------

pub fn summarise(shadows: &[OnboardShadow], trains: &[Train]) -> OnboardSummary {
    let mut summary = OnboardSummary::default();
    for (sh, tr) in shadows.iter().zip(trains.iter()) {
        summary.ticks_evaluated = summary.ticks_evaluated.saturating_add(
            u64::from(sh.stats.ticks_release)
                + u64::from(sh.stats.ticks_service)
                + u64::from(sh.stats.ticks_emergency),
        );
        summary.total_release_ticks = summary
            .total_release_ticks
            .saturating_add(u64::from(sh.stats.ticks_release));
        summary.total_service_ticks = summary
            .total_service_ticks
            .saturating_add(u64::from(sh.stats.ticks_service));
        summary.total_emergency_ticks = summary
            .total_emergency_ticks
            .saturating_add(u64::from(sh.stats.ticks_emergency));
        summary.total_overspeed_ticks = summary
            .total_overspeed_ticks
            .saturating_add(u64::from(sh.stats.overspeed_ticks));
        summary.total_approach_ticks = summary
            .total_approach_ticks
            .saturating_add(u64::from(sh.stats.approach_ticks));
        if let Some(e) = sh.stats.first_emergency.clone() {
            summary.emergencies.push(e);
        }
        summary.per_train.push(PerTrainOnboard {
            train: tr.id.to_string(),
            ticks_release: sh.stats.ticks_release,
            ticks_service: sh.stats.ticks_service,
            ticks_emergency: sh.stats.ticks_emergency,
            peak_friction_ppt: sh.stats.peak_friction_ppt,
            peak_regen_ppt: sh.stats.peak_regen_ppt,
            shadow_distance_km: sh.stats.shadow_distance_mm as f64 / 1_000_000.0,
        });
    }
    summary
}

#[cfg(test)]
mod tests {
    use super::*;
    use osr_core::{Line, Section, Station, StationId};

    fn net() -> Network {
        let mut net = Network::default();
        for i in 1..=3 {
            net.stations.insert(
                StationId::new(i),
                Station {
                    id: StationId::new(i),
                    name: format!("S{i}"),
                    charging_power_kw: 0,
                    dwell_seconds: 30,
                    is_terminal: i == 1 || i == 3,
                    is_depot: false,
                },
            );
        }
        let mut fwd = vec![];
        let mut rev = vec![];
        for i in 0..2 {
            let f = SectionId::new(1000 + i);
            let r = SectionId::new(2000 + i);
            net.sections.insert(f, Section {
                id: f,
                from_station: StationId::new((i as u64) + 1),
                to_station: StationId::new((i as u64) + 2),
                length_mm: 1_000_000,
                max_speed_mps: 22.0,
            });
            net.sections.insert(r, Section {
                id: r,
                from_station: StationId::new((i as u64) + 2),
                to_station: StationId::new((i as u64) + 1),
                length_mm: 1_000_000,
                max_speed_mps: 22.0,
            });
            fwd.push(f);
            rev.push(r);
        }
        net.lines.push(Line {
            name: "L".into(),
            stations: (1..=3).map(StationId::new).collect(),
            forward_sections: fwd,
            reverse_sections: rev,
            is_ring: false,
        });
        net
    }

    fn mock_train() -> Train {
        Train {
            id: TrainId::new(7),
            line_index: 0,
            consist: ConsistDescriptor::reference_3car(),
            heading: Heading::Forward,
            phase: TrainPhase::Traveling {
                section: SectionId::new(1000),
                from_station: StationId::new(1),
                to_station: StationId::new(2),
                total_travel_s: 60.0,
                remaining_s: 60.0,
            },
            soc: 0.9,
            odometer_km: 0.0,
            energy_consumed_kwh: 0.0,
            energy_charged_kwh: 0.0,
            min_soc_seen: 0.9,
        }
    }

    #[test]
    fn shadow_runs_and_records_release_at_start() {
        let n = net();
        let train = mock_train();
        let mut shadow = OnboardShadow::new(&train);
        let report = onboard_tick(&mut shadow, &train, &n, 1, 1.0).expect("is traveling");
        // First tick: speed very low, plenty of section ahead → Release.
        assert!(report.brake.is_release(), "{:?}", report);
        assert_eq!(shadow.stats.ticks_release, 1);
        assert_eq!(shadow.stats.ticks_emergency, 0);
    }

    #[test]
    fn shadow_accelerates_over_multiple_ticks() {
        let n = net();
        let train = mock_train();
        let mut shadow = OnboardShadow::new(&train);
        for t in 1..=10 {
            let _ = onboard_tick(&mut shadow, &train, &n, t, 1.0);
        }
        // Accel 1 m/s² → after 10 s shadow speed should be ~10 m/s (10_000 mm/s)
        // subject to v_max clamp.
        assert!(
            shadow.odom.speed_mmps > 5_000 && shadow.odom.speed_mmps <= 22_000,
            "speed {}",
            shadow.odom.speed_mmps
        );
        assert!(shadow.kin.head_offset_mm > 0);
        assert_eq!(shadow.stats.ticks_emergency, 0);
    }

    #[test]
    fn shadow_approaches_decel_near_end_of_section() {
        let n = net();
        let train = mock_train();
        let mut shadow = OnboardShadow::new(&train);
        // Run long enough to traverse the full 1 km section.
        for t in 1..=120 {
            let _ = onboard_tick(&mut shadow, &train, &n, t, 1.0);
        }
        // By the end, we should be clipped at section end with near-zero speed.
        assert_eq!(shadow.kin.head_offset_mm, 1_000_000);
        assert!(shadow.odom.speed_mmps.abs() < 2_000, "residual speed {}", shadow.odom.speed_mmps);
        assert_eq!(shadow.stats.ticks_emergency, 0);
    }

    #[test]
    fn non_traveling_phase_returns_none() {
        let n = net();
        let mut train = mock_train();
        train.phase = TrainPhase::Dwelling {
            station: StationId::new(1),
            remaining_s: 30.0,
            energy_added_kwh: 0.0,
        };
        let mut shadow = OnboardShadow::new(&train);
        assert!(onboard_tick(&mut shadow, &train, &n, 1, 1.0).is_none());
    }
}
