//! OpenSourceRail door controller.
//!
//! Per-door SIL-4 evaluator enforcing the safety-critical interlock:
//! **no door may be driven open above a low-speed threshold**
//! (typically 5 km/h ≈ 1 400 mm/s). Opening at speed is the single
//! highest-risk failure mode of a passenger rail vehicle; the
//! controller makes it structurally impossible under the
//! `commanded = Open` path.
//!
//! Phase 2c crate 1 of [RFC 0005 §4.2](../../../docs/rfcs/0005-sbc-software-architecture.md).
//!
//! # What the controller decides each tick
//!
//! Given a commanded action (Open / Close / Hold), speed, at-station
//! flag, per-door sensors, and an emergency-unlock input:
//!
//! - **Open path:** permitted only when
//!   `speed ≤ stop_speed_threshold_mmps` AND `at_station`, *or* when
//!   `emergency_unlock == true` (egress during incidents; the
//!   speed / platform gate is waived). Emergency unlock never
//!   commands `DriveClose` — the intent is always "let passengers
//!   out."
//! - **Close path:** motor drives closed unless obstruction is
//!   detected (obstruction sensor OR motor-current above trip),
//!   in which case the motor stops and the `Obstructed` state
//!   is latched for upstream retry logic.
//! - **Interlock signal:** `interlock_ok` is `true` iff the door
//!   reports closed-limit AND lock-sensor (2oo2). Traction is
//!   permitted to produce torque only when every door's
//!   `interlock_ok` is true (enforced by the consist-level
//!   aggregator, not this crate).
//! - **Motor timeout:** the motor is stopped and the door enters
//!   `Faulted` (with cooldown latch) if it has run in the same
//!   direction for longer than `motor_timeout_ms`.
//!
//! # Safety properties (proptest-verified)
//!
//! - **D1 determinism.**
//! - **D2 no-open-above-threshold:** if
//!   `speed_mmps > stop_speed_threshold_mmps` AND
//!   `!emergency_unlock`, motor is never `DriveOpen`.
//! - **D3 at-station-gates-open:** if `!at_station` AND
//!   `!emergency_unlock`, motor is never `DriveOpen`.
//! - **D4 obstruction-stops-close:** if
//!   `obstruction_detected || motor_current ≥ trip`, motor is
//!   never `DriveClose`.
//! - **D5 emergency-unlock overrides:** `emergency_unlock == true`
//!   → motor ∈ { `Stop`, `DriveOpen` } (never `DriveClose`).
//! - **D6 interlock is 2oo2:** `interlock_ok` iff
//!   `closed_limit && lock_sensor`.
//! - **D7 motor timeout latches Faulted:** motor running beyond
//!   `motor_timeout_ms` → `Faulted` + cooldown; within cooldown
//!   motor is `Stop`.
//! - **D8 fault blocks motor:** while `Faulted`, motor is `Stop`.

#![forbid(unsafe_code)]

use serde::{Deserialize, Serialize};

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

/// Top-level action the vehicle controller wants.
#[derive(Copy, Clone, Debug, PartialEq, Eq, Hash, Default, Serialize, Deserialize)]
pub enum DoorAction {
    /// Keep current state. Motor stops.
    #[default]
    Hold,
    Open,
    Close,
}

/// Low-level motor command emitted by the evaluator.
#[derive(Copy, Clone, Debug, PartialEq, Eq, Hash, Default, Serialize, Deserialize)]
pub enum MotorCommand {
    #[default]
    Stop,
    DriveOpen,
    DriveClose,
}

/// Observable high-level door status — for DMI / PIS display and
/// for the interlock aggregator.
#[derive(Copy, Clone, Debug, PartialEq, Eq, Hash, Default, Serialize, Deserialize)]
pub enum DoorStatus {
    /// `closed_limit && lock_sensor` — interlock holds.
    #[default]
    Closed,
    /// Motor driving open; not yet at open-limit.
    Opening,
    /// `open_limit` asserted.
    Open,
    /// Motor driving closed; no obstruction.
    Closing,
    /// Close command was active but obstruction detected; motor
    /// stopped pending retry from a higher-level controller.
    Obstructed,
    /// Latched fault (motor timeout, sensor invalid, etc.); motor
    /// stops until cooldown expires AND a fresh command arrives.
    Faulted,
    /// Neither limit switch asserted and motor is Stop — transient
    /// state, shouldn't persist.
    Unknown,
}

/// Raw sensor package for one door pair.
#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct DoorSensors {
    /// End-of-travel switch asserting the door is fully closed.
    pub closed_limit: bool,
    /// Lock-pin engaged — the 2oo2 companion to `closed_limit`.
    pub lock_sensor: bool,
    /// End-of-travel switch asserting the door is fully open.
    pub open_limit: bool,
    /// Measured motor current, milliamps.
    pub motor_current_ma: u32,
    /// Dedicated obstruction-detection edge strip or light curtain.
    pub obstruction_detected: bool,
}

/// Per-tick inputs.
#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct DoorInputs {
    pub now_ns: u64,
    pub speed_mmps: i32,
    pub at_station: bool,
    pub commanded: DoorAction,
    /// `true` when emergency evacuation is in progress — waives the
    /// speed and station gates. Hardwired to the cab emergency
    /// control and to the fire-detection crate's trip.
    pub emergency_unlock: bool,
    pub sensors: DoorSensors,
}

/// Fixed calibration.
#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct DoorParams {
    /// Speed at or below which opening is permitted (mm/s).
    pub stop_speed_threshold_mmps: i32,
    /// Motor-current magnitude above which an obstruction is inferred.
    pub obstruction_current_trip_ma: u32,
    /// Maximum continuous motor-run time, milliseconds.
    pub motor_timeout_ms: u32,
    /// Rest period after a fault before the motor may be re-engaged.
    pub fault_cooldown_ms: u32,
}

impl DoorParams {
    #[must_use]
    pub fn light_metro_default() -> Self {
        Self {
            stop_speed_threshold_mmps: 1_400, // ≈ 5 km/h
            obstruction_current_trip_ma: 5_000,
            motor_timeout_ms: 8_000,
            fault_cooldown_ms: 5_000,
        }
    }
}

// ---------------------------------------------------------------------------
// State + Output
// ---------------------------------------------------------------------------

#[derive(Copy, Clone, Debug, PartialEq, Eq, Default, Serialize, Deserialize)]
pub struct DoorState {
    pub motor: MotorCommand,
    pub status: DoorStatus,
    /// Timestamp the motor most recently transitioned out of Stop.
    pub motor_started_ns: Option<u64>,
    /// When populated, the door is faulted until this wall-clock time.
    pub fault_until_ns: Option<u64>,
    /// Obstruction was detected on a recent Close attempt.
    pub obstruction_latched: bool,
}

#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct DoorOutput {
    pub state: DoorState,
    pub motor: MotorCommand,
    pub status: DoorStatus,
    /// `true` iff this door is closed AND locked (2oo2 of
    /// `closed_limit && lock_sensor`). The consist-level aggregator
    /// takes the AND across doors to produce the traction
    /// enable-to-move signal.
    pub interlock_ok: bool,
}

// ---------------------------------------------------------------------------
// Evaluator
// ---------------------------------------------------------------------------

/// Evaluate one door for one tick. Pure.
#[must_use]
pub fn door_evaluate(
    prev: &DoorState,
    inputs: &DoorInputs,
    params: &DoorParams,
) -> DoorOutput {
    let s = &inputs.sensors;

    // --- 1. Interlock signal (2oo2) ----------------------------------
    let interlock_ok = s.closed_limit && s.lock_sensor;

    // --- 2. Obstruction-during-close detection -----------------------
    // Either an explicit obstruction sensor or a motor-current spike
    // while driving closed constitutes obstruction.
    let obstruction_during_close = matches!(prev.motor, MotorCommand::DriveClose)
        && (s.obstruction_detected
            || s.motor_current_ma >= params.obstruction_current_trip_ma);

    // --- 3. Fault / cooldown handling --------------------------------
    let mut fault_until_ns = prev.fault_until_ns;

    // Motor-timeout trip.
    if !matches!(prev.motor, MotorCommand::Stop) {
        if let Some(started) = prev.motor_started_ns {
            let run_ms = inputs.now_ns.saturating_sub(started) / 1_000_000;
            if run_ms > u64::from(params.motor_timeout_ms) {
                let deadline =
                    inputs.now_ns.saturating_add(u64::from(params.fault_cooldown_ms) * 1_000_000);
                fault_until_ns = Some(match fault_until_ns {
                    Some(existing) => existing.max(deadline),
                    None => deadline,
                });
            }
        }
    }

    let cooldown_expired = match fault_until_ns {
        Some(until) => inputs.now_ns >= until,
        None => true,
    };
    if cooldown_expired {
        fault_until_ns = None;
    }
    let in_fault = fault_until_ns.is_some();

    // --- 4. Determine whether opening is permitted -------------------
    //
    // Open gate — rule (D2, D3, D5):
    //   allowed_to_open = emergency_unlock
    //       || (speed ≤ threshold AND at_station)
    let allowed_to_open = inputs.emergency_unlock
        || (inputs.speed_mmps <= params.stop_speed_threshold_mmps
            && inputs.at_station);

    // --- 5. Emergency-unlock override --------------------------------
    //
    // When emergency_unlock is active, the door is driven open
    // regardless of the `commanded` input — unless it's already open.
    if inputs.emergency_unlock && !in_fault {
        let motor = if s.open_limit {
            MotorCommand::Stop
        } else {
            MotorCommand::DriveOpen
        };
        let motor_started_ns = start_timestamp(prev, motor, inputs.now_ns);
        let status = derive_status(motor, s, false);
        return DoorOutput {
            state: DoorState {
                motor,
                status,
                motor_started_ns,
                fault_until_ns,
                obstruction_latched: false,
            },
            motor,
            status,
            interlock_ok,
        };
    }

    // --- 6. Fault → stop ----------------------------------------------
    if in_fault {
        return DoorOutput {
            state: DoorState {
                motor: MotorCommand::Stop,
                status: DoorStatus::Faulted,
                motor_started_ns: None,
                fault_until_ns,
                obstruction_latched: prev.obstruction_latched,
            },
            motor: MotorCommand::Stop,
            status: DoorStatus::Faulted,
            interlock_ok,
        };
    }

    // --- 7. Decide motor command based on commanded action -----------
    let mut obstruction_latched = prev.obstruction_latched;

    let motor = match inputs.commanded {
        DoorAction::Hold => MotorCommand::Stop,
        DoorAction::Open => {
            if allowed_to_open && !s.open_limit {
                MotorCommand::DriveOpen
            } else {
                MotorCommand::Stop
            }
        }
        DoorAction::Close => {
            if interlock_ok {
                // Already closed; nothing to do.
                MotorCommand::Stop
            } else if obstruction_during_close
                || s.obstruction_detected
                || s.motor_current_ma >= params.obstruction_current_trip_ma
            {
                obstruction_latched = true;
                MotorCommand::Stop
            } else {
                MotorCommand::DriveClose
            }
        }
    };

    // Clear obstruction latch once the door is no longer trying to close
    // (e.g., user re-opens it) — avoids sticky-state across an open-then-close.
    if motor != MotorCommand::DriveClose && inputs.commanded != DoorAction::Close {
        obstruction_latched = false;
    }

    let motor_started_ns = start_timestamp(prev, motor, inputs.now_ns);
    let status = derive_status(motor, s, obstruction_latched);

    DoorOutput {
        state: DoorState {
            motor,
            status,
            motor_started_ns,
            fault_until_ns,
            obstruction_latched,
        },
        motor,
        status,
        interlock_ok,
    }
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

fn start_timestamp(
    prev: &DoorState,
    new_motor: MotorCommand,
    now_ns: u64,
) -> Option<u64> {
    match (prev.motor, new_motor) {
        (_, MotorCommand::Stop) => None,
        (MotorCommand::Stop, _) => Some(now_ns),
        (a, b) if a == b => prev.motor_started_ns,
        // Direction change: re-stamp.
        _ => Some(now_ns),
    }
}

fn derive_status(
    motor: MotorCommand,
    sensors: &DoorSensors,
    obstruction_latched: bool,
) -> DoorStatus {
    let closed_and_locked = sensors.closed_limit && sensors.lock_sensor;
    match motor {
        MotorCommand::Stop => {
            if closed_and_locked {
                DoorStatus::Closed
            } else if sensors.open_limit {
                DoorStatus::Open
            } else if obstruction_latched {
                DoorStatus::Obstructed
            } else {
                DoorStatus::Unknown
            }
        }
        MotorCommand::DriveOpen => DoorStatus::Opening,
        MotorCommand::DriveClose => DoorStatus::Closing,
    }
}

// ---------------------------------------------------------------------------
// Consist-level helper
// ---------------------------------------------------------------------------

/// AND-reduction of per-door `interlock_ok`. Traction is permitted
/// to command torque only when this is `true`. Empty slice returns
/// `false` (fail-safe: a consist with no door reports is not
/// implicitly "all closed").
#[must_use]
pub fn consist_interlock_ok(outputs: &[DoorOutput]) -> bool {
    !outputs.is_empty() && outputs.iter().all(|o| o.interlock_ok)
}

// ---------------------------------------------------------------------------
// Unit tests
// ---------------------------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;

    fn closed_sensors() -> DoorSensors {
        DoorSensors {
            closed_limit: true,
            lock_sensor: true,
            open_limit: false,
            motor_current_ma: 0,
            obstruction_detected: false,
        }
    }

    fn open_sensors() -> DoorSensors {
        DoorSensors {
            closed_limit: false,
            lock_sensor: false,
            open_limit: true,
            motor_current_ma: 0,
            obstruction_detected: false,
        }
    }

    fn at_station_stopped(cmd: DoorAction, sensors: DoorSensors) -> DoorInputs {
        DoorInputs {
            now_ns: 0,
            speed_mmps: 0,
            at_station: true,
            commanded: cmd,
            emergency_unlock: false,
            sensors,
        }
    }

    #[test]
    fn closed_at_station_open_drives_open() {
        let p = DoorParams::light_metro_default();
        let out = door_evaluate(
            &DoorState::default(),
            &at_station_stopped(DoorAction::Open, closed_sensors()),
            &p,
        );
        assert_eq!(out.motor, MotorCommand::DriveOpen);
        assert_eq!(out.status, DoorStatus::Opening);
        assert!(out.interlock_ok);
    }

    #[test]
    fn open_above_threshold_refused() {
        let p = DoorParams::light_metro_default();
        let mut i = at_station_stopped(DoorAction::Open, closed_sensors());
        i.speed_mmps = 2_000; // > 1400 threshold
        let out = door_evaluate(&DoorState::default(), &i, &p);
        assert_eq!(out.motor, MotorCommand::Stop);
    }

    #[test]
    fn open_off_platform_refused() {
        let p = DoorParams::light_metro_default();
        let mut i = at_station_stopped(DoorAction::Open, closed_sensors());
        i.at_station = false;
        let out = door_evaluate(&DoorState::default(), &i, &p);
        assert_eq!(out.motor, MotorCommand::Stop);
    }

    #[test]
    fn emergency_unlock_opens_at_speed() {
        let p = DoorParams::light_metro_default();
        let mut i = at_station_stopped(DoorAction::Close, closed_sensors());
        i.speed_mmps = 15_000;
        i.at_station = false;
        i.emergency_unlock = true;
        let out = door_evaluate(&DoorState::default(), &i, &p);
        // Emergency-unlock overrides commanded=Close with DriveOpen.
        assert_eq!(out.motor, MotorCommand::DriveOpen);
    }

    #[test]
    fn close_when_open_drives_close() {
        let p = DoorParams::light_metro_default();
        let i = at_station_stopped(DoorAction::Close, open_sensors());
        let out = door_evaluate(&DoorState::default(), &i, &p);
        assert_eq!(out.motor, MotorCommand::DriveClose);
        assert_eq!(out.status, DoorStatus::Closing);
    }

    #[test]
    fn obstruction_stops_close() {
        let p = DoorParams::light_metro_default();
        let mut s = open_sensors();
        s.obstruction_detected = true;
        let i = at_station_stopped(DoorAction::Close, s);
        let out = door_evaluate(&DoorState::default(), &i, &p);
        assert_eq!(out.motor, MotorCommand::Stop);
        assert!(out.state.obstruction_latched);
    }

    #[test]
    fn high_motor_current_counts_as_obstruction() {
        let p = DoorParams::light_metro_default();
        let mut s = open_sensors();
        s.motor_current_ma = 6_000; // above 5_000 trip
        let i = at_station_stopped(DoorAction::Close, s);
        let out = door_evaluate(&DoorState::default(), &i, &p);
        assert_eq!(out.motor, MotorCommand::Stop);
        assert!(out.state.obstruction_latched);
    }

    #[test]
    fn interlock_is_2oo2() {
        let p = DoorParams::light_metro_default();
        let mut s = closed_sensors();
        s.lock_sensor = false; // limit OK but lock missing
        let i = at_station_stopped(DoorAction::Hold, s);
        let out = door_evaluate(&DoorState::default(), &i, &p);
        assert!(!out.interlock_ok);
    }

    #[test]
    fn motor_timeout_faults() {
        let p = DoorParams::light_metro_default();
        // Motor started at t=0, running open; still running at t=9s > 8s timeout.
        let prev = DoorState {
            motor: MotorCommand::DriveOpen,
            status: DoorStatus::Opening,
            motor_started_ns: Some(0),
            fault_until_ns: None,
            obstruction_latched: false,
        };
        let mut i = at_station_stopped(DoorAction::Open, open_sensors());
        i.now_ns = 9_000_000_000;
        i.sensors = DoorSensors {
            closed_limit: false,
            lock_sensor: false,
            open_limit: false, // stuck in transit
            motor_current_ma: 1_000,
            obstruction_detected: false,
        };
        let out = door_evaluate(&prev, &i, &p);
        assert_eq!(out.motor, MotorCommand::Stop);
        assert_eq!(out.status, DoorStatus::Faulted);
        assert!(out.state.fault_until_ns.is_some());
    }

    #[test]
    fn consist_interlock_and_reduction() {
        let p = DoorParams::light_metro_default();
        let closed = door_evaluate(
            &DoorState::default(),
            &at_station_stopped(DoorAction::Hold, closed_sensors()),
            &p,
        );
        let open = door_evaluate(
            &DoorState::default(),
            &at_station_stopped(DoorAction::Hold, open_sensors()),
            &p,
        );
        assert!(consist_interlock_ok(&[closed, closed]));
        assert!(!consist_interlock_ok(&[closed, open]));
        assert!(!consist_interlock_ok(&[]));
    }

    #[test]
    fn determinism() {
        let p = DoorParams::light_metro_default();
        let i = at_station_stopped(DoorAction::Open, closed_sensors());
        let a = door_evaluate(&DoorState::default(), &i, &p);
        let b = door_evaluate(&DoorState::default(), &i, &p);
        assert_eq!(a, b);
    }
}
