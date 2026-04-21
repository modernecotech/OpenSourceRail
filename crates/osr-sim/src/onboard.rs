//! Shadow-mode onboard stack: runs the full SIL-4 + SIL-2 onboard
//! software chain — [`osr-odometry`], [`osr-interlocking`] MA via
//! `forward_chain`, [`osr-atp`], [`osr-ato`], [`osr-bms`],
//! [`osr-traction`], [`osr-brake`] — in parallel with the
//! simulator's countdown-based train motion model, every tick, for
//! every Traveling train.
//!
//! This is **integration evidence** for the Phase 2a + 2b SBC
//! crates (RFC 0005 §11). The sim's own kinematic model is not
//! replaced — the shadow runs alongside, exercises the real onboard
//! decision code with real scenario inputs, and produces a summary
//! that's folded into [`SimResult`].
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
//! 3. Build a local MA via `forward_chain`, exactly as
//!    `osr-interlocking` would.
//! 4. Run [`atp_evaluate`] → safety envelope / brake command.
//! 5. Run [`ato_evaluate`] → torque setpoint + service-brake demand.
//! 6. Synthesize cell-level pack state from the BMS state's SoC and
//!    run [`bms_evaluate`] (using the prior tick's estimated current
//!    as the pack-current input — one-tick lag, fine for shadow
//!    purposes).
//! 7. Run [`traction_evaluate`] with ATO's torque and BMS's limits.
//! 8. Compose a [`BrakeInputs`] that *unions* the ATP command with
//!    ATO's service brake (ATP remains the hard bound; ATO drives
//!    normal braking inside it). Regen availability comes from the
//!    BMS charge limit. Run [`brake_evaluate`].
//! 9. Record per-train tick statistics.
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

use osr_ato::{ato_evaluate, AtoInputs, AtoMode, AtoParams, AtoState};
use osr_atp::{atp_evaluate, AtpOutcome, BrakeCommand, TriggerReason};
use osr_bms::{bms_evaluate, BmsInputs, BmsParams, BmsState, ContactorCommand, ContactorState};
use osr_brake::{brake_evaluate, BrakeInputs, BrakeOutput, BrakeParams};
use osr_core::{ConsistDescriptor, Direction, Network, SectionId, TrackRef, TrainId};
use osr_derailment::{
    derailment_evaluate, DerailmentInputs, DerailmentParams, DerailmentState,
    SensorChannel as DerailSensor,
};
use osr_fire_safety::{
    fire_evaluate, BaySensors, FireInputs, FireParams, FireState,
};
use osr_interlocking::{far_end_of, forward_chain, MovementAuthority, MAX_MA_DISTANCE_MM, MA_VALIDITY_WINDOW_NS};
use osr_odometry::{odom_step, BaliseId, OdomCalibration, OdomState, SensorTick};
use osr_traction::{traction_evaluate, InverterState, TractionInputs, TractionParams, TractionState};
use osr_vigilance::{
    vigilance_evaluate, VigilanceInputs, VigilanceOutput, VigilanceParams,
};
use serde::{Deserialize, Serialize};

use crate::train::{Heading, Train, TrainPhase};

// ---------------------------------------------------------------------------
// Shadow state
// ---------------------------------------------------------------------------

/// Per-train shadow state — kinematics + odometer + Phase 2b stack + counters.
#[derive(Clone, Debug)]
pub struct OnboardShadow {
    pub train_id: TrainId,
    pub odom: OdomState,
    pub odom_cal: OdomCalibration,
    pub brake_params: BrakeParams,
    /// Kinematic state: meaningful only during Traveling. Reset to
    /// zero at section boundaries.
    pub kin: KinematicShadow,

    // --- Phase 2b stack ------------------------------------------------
    pub ato_state: AtoState,
    pub ato_params: AtoParams,
    pub bms_state: BmsState,
    pub bms_params: BmsParams,
    pub traction_state: TractionState,
    pub traction_params: TractionParams,

    // --- SIL-4 monitors -----------------------------------------------
    pub fire_state: FireState,
    pub fire_params: FireParams,
    pub derailment_state: DerailmentState,
    pub derailment_params: DerailmentParams,
    pub vigilance_out: VigilanceOutput,
    pub vigilance_params: VigilanceParams,

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

    // --- Phase 2b telemetry -------------------------------------------
    pub ato_ticks_accelerating: u32,
    pub ato_ticks_cruising: u32,
    pub ato_ticks_coasting: u32,
    pub ato_ticks_braking: u32,
    pub ato_ticks_station_approach: u32,
    pub ato_ticks_stopped: u32,
    /// Peak positive torque commanded by ATO, mN·m.
    pub peak_torque_mnm: i32,
    /// Peak negative torque (regen) commanded, mN·m (negative value).
    pub min_torque_mnm: i32,
    /// Peak pack discharge current, mA.
    pub peak_discharge_ma: i32,
    /// Peak pack charge (regen) current, mA (negative value).
    pub min_charge_ma: i32,
    /// Ticks where the traction crate asserted anti-slip.
    pub anti_slip_ticks: u32,
    /// Final SoC observed (ppt).
    pub final_soc_ppt: u16,
    /// Minimum SoC observed (ppt). Useful for battery-sizing studies.
    pub min_soc_ppt: u16,
    /// BMS fault ticks (any latched fault active).
    pub bms_fault_ticks: u32,
    /// Traction fault ticks.
    pub traction_fault_ticks: u32,

    // --- SIL-4 monitor trip counters ---------------------------------
    pub fire_trip_ticks: u32,
    pub derailment_trip_ticks: u32,
    pub vigilance_trip_ticks: u32,
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
    pub total_anti_slip_ticks: u64,
    pub total_bms_fault_ticks: u64,
    pub total_traction_fault_ticks: u64,
    pub total_fire_trip_ticks: u64,
    pub total_derailment_trip_ticks: u64,
    pub total_vigilance_trip_ticks: u64,
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

    // Phase 2b
    pub peak_torque_mnm: i32,
    pub min_torque_mnm: i32,
    pub peak_discharge_ma: i32,
    pub min_charge_ma: i32,
    pub anti_slip_ticks: u32,
    pub final_soc_ppt: u16,
    pub min_soc_ppt: u16,
    pub ato_ticks_accelerating: u32,
    pub ato_ticks_cruising: u32,
    pub ato_ticks_braking: u32,
    pub ato_ticks_station_approach: u32,
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
        // Pack capacity (mAh) = Wh × 1000 / nominal_voltage_V.
        // Assume ~300 V nominal across the pack.
        let pack_capacity_mah = ((u64::from(train.consist.battery_capacity_wh) * 1000) / 300) as u32;
        let bms_params = BmsParams::sodium_ion_default(8, pack_capacity_mah.max(1));
        // Initial SoC assumed 80 % — matches the sim's default start.
        let bms_state = BmsState::initial((train.soc.clamp(0.0, 1.0) * 1000.0) as u16);
        let mut stats = OnboardStats::default();
        stats.min_soc_ppt = bms_state.soc_ppt;
        stats.final_soc_ppt = bms_state.soc_ppt;
        Self {
            train_id: train.id,
            odom: OdomState::new_at(train.id, head, odom_cal.min_uncertainty_mm, 0),
            odom_cal,
            brake_params: BrakeParams::light_metro_default(),
            kin: KinematicShadow::reset(),
            ato_state: AtoState::default(),
            ato_params: AtoParams::light_metro_default(),
            bms_state,
            bms_params,
            traction_state: TractionState::default(),
            traction_params: TractionParams::light_metro_default(),
            fire_state: FireState::default(),
            fire_params: FireParams::default_metro(),
            derailment_state: DerailmentState::default(),
            derailment_params: DerailmentParams::default_metro(),
            vigilance_out: VigilanceOutput::default(),
            vigilance_params: VigilanceParams::light_metro_default(),
            stats,
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

    // 6. ATO — controller inside the envelope. Target is the
    //    section's permanent max speed; station approach engages
    //    using remaining-distance-to-section-end.
    let envelope_mmps = atp_out
        .envelope_mmps
        .unwrap_or(shadow.kin.v_max_mmps);
    let distance_to_stop_mm = Some(
        (shadow.kin.section_length_mm - shadow.kin.head_offset_mm).max(0),
    );
    let dt_ns = (dt_s.max(0.0) * 1_000_000_000.0) as u64;
    let ato_in = AtoInputs {
        now_ns,
        dt_ns,
        current_speed_mmps: shadow.odom.speed_mmps,
        envelope_mmps,
        cruise_target_mmps: shadow.kin.v_max_mmps,
        distance_to_stop_mm,
        at_station: false,
        dwell_remaining_ms: 0,
        ato_engaged: true,
    };
    let ato_out = ato_evaluate(&shadow.ato_state, &ato_in, &shadow.ato_params);
    shadow.ato_state = ato_out.state;

    // 7. BMS — synthesize cell voltages/temps from current SoC.
    let cells = 8_usize;
    let v_low = shadow.bms_params.v_trip_min_mv as u32 + 100;
    let v_high = shadow.bms_params.v_trip_max_mv as u32 - 100;
    let soc_frac_pptp1 = u32::from(shadow.bms_state.soc_ppt).min(1000);
    let v_cell_mv = (v_low + (v_high - v_low) * soc_frac_pptp1 / 1000) as u16;
    let cell_voltages: Vec<u16> = vec![v_cell_mv; cells];
    // Constant 25 °C for v1 — thermal model is out of scope.
    let cell_temps: Vec<i16> = vec![250_i16; cells];
    // Sign convention swap: osr-traction uses "+ = discharge
    // (motoring)", osr-bms uses "+ = charge (into pack)". Negate
    // across the seam. This is the single sign-convention
    // disagreement in the onboard stack; a future refactor could
    // pick one convention crate-wide.
    let pack_current_ma = shadow.traction_state.estimated_current_ma.saturating_neg();
    let bms_in = BmsInputs {
        now_ns,
        cell_voltages_mv: &cell_voltages,
        cell_temps_dc: &cell_temps,
        pack_current_ma,
        pack_voltage_mv: 300_000,
        external_command: ContactorCommand::RequestClose,
        dt_ns,
    };
    let bms_out = bms_evaluate(&shadow.bms_state, &bms_in, &shadow.bms_params);
    shadow.bms_state = bms_out.state;

    // 8. Traction — ATO torque clamped by BMS limits. The BMS and
    //    traction crates use the same sign convention: `discharge`
    //    = current out of the pack (motoring), `charge` = current
    //    into the pack (regen).
    let traction_in = TractionInputs {
        now_ns,
        torque_setpoint_mnm: ato_out.torque_setpoint_mnm,
        enable_requested: true,
        bms_contactor_closed: matches!(bms_out.contactor, ContactorState::Closed),
        bms_discharge_limit_ma: bms_out.discharge_limit_ma,
        bms_charge_limit_ma: bms_out.charge_limit_ma,
        pack_voltage_mv: 300_000,
        reference_speed_mmps: shadow.odom.speed_mmps,
        wheel_speed_mmps: shadow.odom.speed_mmps,
        inverter_over_temp: false,
        inverter_drive_fault: false,
    };
    let traction_out =
        traction_evaluate(&shadow.traction_state, &traction_in, &shadow.traction_params);
    shadow.traction_state = traction_out.state;

    // 9. SIL-4 monitors — fire, derailment, vigilance. In the shadow
    //    we feed clean synthetic sensor readings (no smoke, no
    //    lateral g, auto-acknowledge vigilance). A real deployment
    //    would plumb real sensor samples here. Any trip from these
    //    crates flows into the brake inputs as an emergency source.
    let fire_in = FireInputs {
        now_ns,
        battery: BaySensors { smoke_ppm: 0, temp_dc: 250, agent_available: true },
        traction: BaySensors { smoke_ppm: 0, temp_dc: 250, agent_available: true },
        hvac: BaySensors { smoke_ppm: 0, temp_dc: 250, agent_available: true },
        ambient_temp_dc: 250,
        reset_requested: false,
    };
    let fire_out = fire_evaluate(&shadow.fire_state, &fire_in, &shadow.fire_params);
    shadow.fire_state = fire_out.state;

    let derail_in = DerailmentInputs {
        now_ns,
        sensor_a: DerailSensor::default(),
        sensor_b: DerailSensor::default(),
        reset_requested: false,
    };
    let derail_out =
        derailment_evaluate(&shadow.derailment_state, &derail_in, &shadow.derailment_params);
    shadow.derailment_state = derail_out.state;

    // Vigilance: auto-acknowledge every tick (synthetic alert driver).
    // A real shadow-mode driver model could decay acks to exercise
    // the timeout; kept simple for now.
    let vig_in = VigilanceInputs {
        now_ns,
        speed_mmps: shadow.odom.speed_mmps,
        ack_received_this_tick: true,
    };
    let vig_out = vigilance_evaluate(&shadow.vigilance_out, &vig_in, &shadow.vigilance_params);
    shadow.vigilance_out = vig_out;

    // 10. Brake — combine ATP command with ATO's service brake. ATP
    // wins on Emergency; otherwise the service level is the max of
    // the two. The SIL-4 monitor outputs all feed in as separate
    // emergency-source flags on `BrakeInputs`.
    let effective_atp_command = match atp_out.command {
        BrakeCommand::Emergency => BrakeCommand::Emergency,
        BrakeCommand::Service(p) => BrakeCommand::Service(p.max(ato_out.service_brake_ppt)),
        BrakeCommand::Release => {
            if ato_out.service_brake_ppt > 0 {
                BrakeCommand::Service(ato_out.service_brake_ppt)
            } else {
                BrakeCommand::Release
            }
        }
    };
    // Regen availability in ppt = charge_limit / max_charge.
    let regen_available_ppt = if shadow.bms_params.max_charge_ma == 0 {
        0_u16
    } else {
        let v = u64::from(bms_out.charge_limit_ma).saturating_mul(1_000)
            / u64::from(shadow.bms_params.max_charge_ma);
        v.min(1_000) as u16
    };
    let brake_inputs = BrakeInputs {
        atp_command: effective_atp_command,
        vigilance_emergency: vig_out.emergency_requested,
        fire_emergency: fire_out.emergency_requested,
        derailment_emergency: derail_out.emergency_requested,
        driver_emergency: false,
        park_requested: false,
        measured_speed_mmps: shadow.odom.speed_mmps,
        wheel_speed_mmps: shadow.odom.speed_mmps,
        regen_available_ppt,
        now_ns,
    };
    let brake_out = brake_evaluate(&brake_inputs, &shadow.brake_params);

    // 11. Stats — monitor trip counters.
    if fire_out.emergency_requested {
        shadow.stats.fire_trip_ticks = shadow.stats.fire_trip_ticks.saturating_add(1);
    }
    if derail_out.emergency_requested {
        shadow.stats.derailment_trip_ticks =
            shadow.stats.derailment_trip_ticks.saturating_add(1);
    }
    if vig_out.emergency_requested {
        shadow.stats.vigilance_trip_ticks =
            shadow.stats.vigilance_trip_ticks.saturating_add(1);
    }

    // 12. Stats.
    record_tick(
        &mut shadow.stats,
        t_s,
        train.id,
        &atp_out,
        &brake_out,
        shadow.odom.speed_mmps,
    );
    record_phase2b_tick(
        &mut shadow.stats,
        &ato_out.mode,
        &traction_out,
        &bms_out,
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

fn record_phase2b_tick(
    stats: &mut OnboardStats,
    ato_mode: &AtoMode,
    traction_out: &osr_traction::TractionOutput,
    bms_out: &osr_bms::BmsOutput,
) {
    // ATO mode counters.
    match ato_mode {
        AtoMode::Accelerating => {
            stats.ato_ticks_accelerating = stats.ato_ticks_accelerating.saturating_add(1);
        }
        AtoMode::Cruising => {
            stats.ato_ticks_cruising = stats.ato_ticks_cruising.saturating_add(1);
        }
        AtoMode::Coasting => {
            stats.ato_ticks_coasting = stats.ato_ticks_coasting.saturating_add(1);
        }
        AtoMode::Braking => {
            stats.ato_ticks_braking = stats.ato_ticks_braking.saturating_add(1);
        }
        AtoMode::StationApproach => {
            stats.ato_ticks_station_approach =
                stats.ato_ticks_station_approach.saturating_add(1);
        }
        AtoMode::Stopped | AtoMode::Dwelling => {
            stats.ato_ticks_stopped = stats.ato_ticks_stopped.saturating_add(1);
        }
        AtoMode::Off => {}
    }
    // Torque peaks (signed).
    if traction_out.commanded_torque_mnm > stats.peak_torque_mnm {
        stats.peak_torque_mnm = traction_out.commanded_torque_mnm;
    }
    if traction_out.commanded_torque_mnm < stats.min_torque_mnm {
        stats.min_torque_mnm = traction_out.commanded_torque_mnm;
    }
    // Current peaks.
    if traction_out.estimated_current_ma > stats.peak_discharge_ma {
        stats.peak_discharge_ma = traction_out.estimated_current_ma;
    }
    if traction_out.estimated_current_ma < stats.min_charge_ma {
        stats.min_charge_ma = traction_out.estimated_current_ma;
    }
    // Anti-slip.
    if traction_out.anti_slip_active {
        stats.anti_slip_ticks = stats.anti_slip_ticks.saturating_add(1);
    }
    // SoC tracking.
    stats.final_soc_ppt = bms_out.state.soc_ppt;
    if stats.min_soc_ppt == 0 || bms_out.state.soc_ppt < stats.min_soc_ppt {
        stats.min_soc_ppt = bms_out.state.soc_ppt;
    }
    // Fault counters.
    if bms_out.state.faults.any() {
        stats.bms_fault_ticks = stats.bms_fault_ticks.saturating_add(1);
    }
    if !matches!(traction_out.state.inverter, InverterState::Disabled | InverterState::Running) {
        stats.traction_fault_ticks = stats.traction_fault_ticks.saturating_add(1);
    }
}

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
        summary.total_anti_slip_ticks = summary
            .total_anti_slip_ticks
            .saturating_add(u64::from(sh.stats.anti_slip_ticks));
        summary.total_bms_fault_ticks = summary
            .total_bms_fault_ticks
            .saturating_add(u64::from(sh.stats.bms_fault_ticks));
        summary.total_traction_fault_ticks = summary
            .total_traction_fault_ticks
            .saturating_add(u64::from(sh.stats.traction_fault_ticks));
        summary.total_fire_trip_ticks = summary
            .total_fire_trip_ticks
            .saturating_add(u64::from(sh.stats.fire_trip_ticks));
        summary.total_derailment_trip_ticks = summary
            .total_derailment_trip_ticks
            .saturating_add(u64::from(sh.stats.derailment_trip_ticks));
        summary.total_vigilance_trip_ticks = summary
            .total_vigilance_trip_ticks
            .saturating_add(u64::from(sh.stats.vigilance_trip_ticks));
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
            peak_torque_mnm: sh.stats.peak_torque_mnm,
            min_torque_mnm: sh.stats.min_torque_mnm,
            peak_discharge_ma: sh.stats.peak_discharge_ma,
            min_charge_ma: sh.stats.min_charge_ma,
            anti_slip_ticks: sh.stats.anti_slip_ticks,
            final_soc_ppt: sh.stats.final_soc_ppt,
            min_soc_ppt: sh.stats.min_soc_ppt,
            ato_ticks_accelerating: sh.stats.ato_ticks_accelerating,
            ato_ticks_cruising: sh.stats.ato_ticks_cruising,
            ato_ticks_braking: sh.stats.ato_ticks_braking,
            ato_ticks_station_approach: sh.stats.ato_ticks_station_approach,
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
