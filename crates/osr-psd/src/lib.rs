//! OpenSourceRail Platform Screen Door (PSD) controller.
//!
//! Station-side counterpart to [`osr_door_control`]. A modern metro
//! platform runs a line of PSD panels — typically 8–16 panels per
//! train-length of platform — that open and close in synchrony with
//! the train's saloon doors. This crate arbitrates when those
//! panels may open and handles per-panel actuation including
//! obstruction detection and fault latching.
//!
//! Phase 2e crate 1 of [RFC 0005 §4.7](../../../docs/rfcs/0005-sbc-software-architecture.md).
//! SIL-2 — failure-to-open is a service failure; failure-to-close in
//! the presence of a passenger is an injury risk, but that interlock
//! lives in the hardware-level light curtain (per RFC 0005 §4.7);
//! this crate handles the coordination logic.
//!
//! # Decision rules
//!
//! A PSD panel may be driven `Open` only when **all** the following
//! hold (the 2oo2 `train_at_platform && train_interlock_ok` pair is
//! the safety-critical input — a mistaken "train here" signal would
//! open panels onto live track):
//!
//! - `train_at_platform == true`
//! - `train_interlock_ok == true` (train has reported all its saloon
//!   doors closed-and-locked during approach, and is now stopped at
//!   the platform edge)
//! - `train_doors_open_or_opening == true` (the train has
//!   affirmatively commanded open — we don't open on pure proximity)
//! - `!emergency_stop`
//! - `occ_commanded == PsdCommand::Open`
//!
//! A panel is driven `Close` when the OCC commands so AND the train
//! doors are no longer open — or unconditionally on `emergency_stop`
//! (the emergency-stop mode actually opens panels for evacuation,
//! handled separately below).
//!
//! ## Emergency-stop behaviour
//!
//! Under `emergency_stop = true` panels are commanded **Open** —
//! this is a station-evacuation mode, not a "lock passengers in"
//! mode. Matches the train-side `osr-door-control` `emergency_unlock`
//! semantic.
//!
//! # Properties (proptest-verified)
//!
//! - **PSD1 determinism.**
//! - **PSD2 no open without train-at-platform.**
//! - **PSD3 no open without train-interlock.**
//! - **PSD4 obstruction stops close.**
//! - **PSD5 emergency-stop opens all panels.**
//! - **PSD6 all-closed-signal is AND-reduction:** `all_closed` iff
//!   every panel reports `closed_limit`.

#![forbid(unsafe_code)]

use serde::{Deserialize, Serialize};

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

#[derive(Copy, Clone, Debug, PartialEq, Eq, Hash, Default, Serialize, Deserialize)]
pub enum PsdCommand {
    #[default]
    Hold,
    Open,
    Close,
}

#[derive(Copy, Clone, Debug, PartialEq, Eq, Hash, Default, Serialize, Deserialize)]
pub enum PsdMotorCommand {
    #[default]
    Stop,
    DriveOpen,
    DriveClose,
}

#[derive(Copy, Clone, Debug, PartialEq, Eq, Hash, Default, Serialize, Deserialize)]
pub enum PsdPanelStatus {
    #[default]
    Closed,
    Opening,
    Open,
    Closing,
    /// Close command interrupted by obstruction; motor stopped.
    Obstructed,
    /// Motor timeout or persistent fault; latched.
    Faulted,
    Unknown,
}

/// Per-panel sensor package. Simpler than the train-side `osr-door-control`
/// because a station panel doesn't need a separate lock sensor — the
/// end-of-travel switch *is* the lock.
#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct PsdSensors {
    pub closed_limit: bool,
    pub open_limit: bool,
    pub motor_current_ma: u32,
    pub obstruction_detected: bool,
}

// ---------------------------------------------------------------------------
// Inputs / params
// ---------------------------------------------------------------------------

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct PsdInputs<'a> {
    pub now_ns: u64,
    pub train_at_platform: bool,
    pub train_interlock_ok: bool,
    pub train_doors_open_or_opening: bool,
    pub occ_commanded: PsdCommand,
    pub emergency_stop: bool,
    pub panels: &'a [PsdSensors],
}

#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct PsdParams {
    pub obstruction_current_trip_ma: u32,
    pub motor_timeout_ms: u32,
    pub fault_cooldown_ms: u32,
}

impl PsdParams {
    #[must_use]
    pub fn default_station() -> Self {
        Self {
            obstruction_current_trip_ma: 4_000,
            motor_timeout_ms: 6_000,
            fault_cooldown_ms: 5_000,
        }
    }
}

// ---------------------------------------------------------------------------
// Per-panel state + output
// ---------------------------------------------------------------------------

#[derive(Copy, Clone, Debug, PartialEq, Eq, Default, Serialize, Deserialize)]
pub struct PsdPanelState {
    pub motor: PsdMotorCommand,
    pub status: PsdPanelStatus,
    pub motor_started_ns: Option<u64>,
    pub fault_until_ns: Option<u64>,
    pub obstruction_latched: bool,
}

#[derive(Clone, Debug, PartialEq, Eq, Default, Serialize, Deserialize)]
pub struct PsdState {
    pub panels: Vec<PsdPanelState>,
}

impl PsdState {
    #[must_use]
    pub fn initial(panel_count: usize) -> Self {
        Self {
            panels: vec![PsdPanelState::default(); panel_count],
        }
    }
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct PsdOutput {
    pub state: PsdState,
    pub panel_motors: Vec<PsdMotorCommand>,
    pub panel_statuses: Vec<PsdPanelStatus>,
    /// `true` when every panel reports `closed_limit`. This is the
    /// train-departure-enable signal sent back to the train.
    pub all_closed: bool,
    pub any_obstructed: bool,
    pub any_faulted: bool,
}

// ---------------------------------------------------------------------------
// Evaluator
// ---------------------------------------------------------------------------

/// One PSD tick. Pure.
#[must_use]
pub fn psd_evaluate(prev: &PsdState, inputs: &PsdInputs<'_>, params: &PsdParams) -> PsdOutput {
    let panel_count = inputs.panels.len();

    // Effective command per panel. Emergency stop opens for
    // evacuation (PSD5). Otherwise obey the OCC command gated by
    // train-side preconditions.
    let allowed_to_open =
        inputs.train_at_platform && inputs.train_interlock_ok && inputs.train_doors_open_or_opening;

    // Derive a single "this-panel-should-do-X" action to then
    // resolve per-panel with obstruction / fault handling.
    let effective_command = if inputs.emergency_stop {
        PsdCommand::Open
    } else {
        match inputs.occ_commanded {
            PsdCommand::Open if !allowed_to_open => PsdCommand::Hold,
            other => other,
        }
    };

    // Process each panel.
    let mut new_panels = Vec::with_capacity(panel_count);
    let mut panel_motors = Vec::with_capacity(panel_count);
    let mut panel_statuses = Vec::with_capacity(panel_count);
    let mut all_closed = panel_count > 0;
    let mut any_obstructed = false;
    let mut any_faulted = false;

    for (i, sensors) in inputs.panels.iter().enumerate() {
        let prev_panel = prev.panels.get(i).copied().unwrap_or_default();
        let (new_panel, motor, status) =
            evaluate_panel(&prev_panel, sensors, effective_command, inputs, params);
        if !sensors.closed_limit {
            all_closed = false;
        }
        if new_panel.obstruction_latched {
            any_obstructed = true;
        }
        if matches!(status, PsdPanelStatus::Faulted) {
            any_faulted = true;
        }
        new_panels.push(new_panel);
        panel_motors.push(motor);
        panel_statuses.push(status);
    }

    PsdOutput {
        state: PsdState { panels: new_panels },
        panel_motors,
        panel_statuses,
        all_closed,
        any_obstructed,
        any_faulted,
    }
}

// ---------------------------------------------------------------------------
// Per-panel helper
// ---------------------------------------------------------------------------

fn evaluate_panel(
    prev: &PsdPanelState,
    sensors: &PsdSensors,
    command: PsdCommand,
    inputs: &PsdInputs<'_>,
    params: &PsdParams,
) -> (PsdPanelState, PsdMotorCommand, PsdPanelStatus) {
    // Obstruction detection during close.
    let obstruction_while_closing = matches!(prev.motor, PsdMotorCommand::DriveClose)
        && (sensors.obstruction_detected
            || sensors.motor_current_ma >= params.obstruction_current_trip_ma);

    // Fault: motor timeout.
    let mut fault_until_ns = prev.fault_until_ns;
    if !matches!(prev.motor, PsdMotorCommand::Stop) {
        if let Some(started) = prev.motor_started_ns {
            let run_ms = inputs.now_ns.saturating_sub(started) / 1_000_000;
            if run_ms > u64::from(params.motor_timeout_ms) {
                let deadline = inputs
                    .now_ns
                    .saturating_add(u64::from(params.fault_cooldown_ms) * 1_000_000);
                fault_until_ns = Some(match fault_until_ns {
                    Some(existing) => existing.max(deadline),
                    None => deadline,
                });
            }
        }
    }
    if let Some(until) = fault_until_ns {
        if inputs.now_ns >= until {
            fault_until_ns = None;
        }
    }
    let in_fault = fault_until_ns.is_some();

    // Emergency-stop overrides fault for the open direction
    // (evacuation takes precedence over a drive-fault latch).
    if inputs.emergency_stop {
        let motor = if sensors.open_limit {
            PsdMotorCommand::Stop
        } else {
            PsdMotorCommand::DriveOpen
        };
        let motor_started_ns = start_timestamp(prev, motor, inputs.now_ns);
        let status = derive_status(motor, sensors, false);
        return (
            PsdPanelState {
                motor,
                status,
                motor_started_ns,
                fault_until_ns: None, // emergency clears fault latch
                obstruction_latched: false,
            },
            motor,
            status,
        );
    }

    // In fault → stop.
    if in_fault {
        return (
            PsdPanelState {
                motor: PsdMotorCommand::Stop,
                status: PsdPanelStatus::Faulted,
                motor_started_ns: None,
                fault_until_ns,
                obstruction_latched: prev.obstruction_latched,
            },
            PsdMotorCommand::Stop,
            PsdPanelStatus::Faulted,
        );
    }

    let mut obstruction_latched = prev.obstruction_latched;

    let motor = match command {
        PsdCommand::Hold => PsdMotorCommand::Stop,
        PsdCommand::Open => {
            if sensors.open_limit {
                PsdMotorCommand::Stop
            } else {
                PsdMotorCommand::DriveOpen
            }
        }
        PsdCommand::Close => {
            if sensors.closed_limit {
                PsdMotorCommand::Stop
            } else if obstruction_while_closing
                || sensors.obstruction_detected
                || sensors.motor_current_ma >= params.obstruction_current_trip_ma
            {
                obstruction_latched = true;
                PsdMotorCommand::Stop
            } else {
                PsdMotorCommand::DriveClose
            }
        }
    };

    // Clear the latch when not trying to close.
    if motor != PsdMotorCommand::DriveClose && command != PsdCommand::Close {
        obstruction_latched = false;
    }

    let motor_started_ns = start_timestamp(prev, motor, inputs.now_ns);
    let status = derive_status(motor, sensors, obstruction_latched);

    (
        PsdPanelState {
            motor,
            status,
            motor_started_ns,
            fault_until_ns,
            obstruction_latched,
        },
        motor,
        status,
    )
}

fn start_timestamp(prev: &PsdPanelState, new_motor: PsdMotorCommand, now_ns: u64) -> Option<u64> {
    match (prev.motor, new_motor) {
        (_, PsdMotorCommand::Stop) => None,
        (PsdMotorCommand::Stop, _) => Some(now_ns),
        (a, b) if a == b => prev.motor_started_ns,
        _ => Some(now_ns),
    }
}

fn derive_status(
    motor: PsdMotorCommand,
    sensors: &PsdSensors,
    obstruction_latched: bool,
) -> PsdPanelStatus {
    match motor {
        PsdMotorCommand::Stop => {
            if sensors.closed_limit {
                PsdPanelStatus::Closed
            } else if sensors.open_limit {
                PsdPanelStatus::Open
            } else if obstruction_latched {
                PsdPanelStatus::Obstructed
            } else {
                PsdPanelStatus::Unknown
            }
        }
        PsdMotorCommand::DriveOpen => PsdPanelStatus::Opening,
        PsdMotorCommand::DriveClose => PsdPanelStatus::Closing,
    }
}

// ---------------------------------------------------------------------------
// Unit tests
// ---------------------------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;

    fn closed() -> PsdSensors {
        PsdSensors {
            closed_limit: true,
            open_limit: false,
            motor_current_ma: 0,
            obstruction_detected: false,
        }
    }

    fn open() -> PsdSensors {
        PsdSensors {
            closed_limit: false,
            open_limit: true,
            motor_current_ma: 0,
            obstruction_detected: false,
        }
    }

    fn inputs_with(
        train_at: bool,
        interlock: bool,
        train_open: bool,
        cmd: PsdCommand,
        em: bool,
        panels: &[PsdSensors],
    ) -> PsdInputs<'_> {
        PsdInputs {
            now_ns: 0,
            train_at_platform: train_at,
            train_interlock_ok: interlock,
            train_doors_open_or_opening: train_open,
            occ_commanded: cmd,
            emergency_stop: em,
            panels,
        }
    }

    #[test]
    fn cannot_open_without_train_at_platform() {
        let p = PsdParams::default_station();
        let panels = vec![closed(); 4];
        let i = inputs_with(false, true, true, PsdCommand::Open, false, &panels);
        let out = psd_evaluate(&PsdState::initial(4), &i, &p);
        for m in &out.panel_motors {
            assert_eq!(*m, PsdMotorCommand::Stop);
        }
    }

    #[test]
    fn cannot_open_without_train_interlock() {
        let p = PsdParams::default_station();
        let panels = vec![closed(); 4];
        let i = inputs_with(true, false, true, PsdCommand::Open, false, &panels);
        let out = psd_evaluate(&PsdState::initial(4), &i, &p);
        for m in &out.panel_motors {
            assert_eq!(*m, PsdMotorCommand::Stop);
        }
    }

    #[test]
    fn cannot_open_without_train_doors_open() {
        let p = PsdParams::default_station();
        let panels = vec![closed(); 4];
        let i = inputs_with(true, true, false, PsdCommand::Open, false, &panels);
        let out = psd_evaluate(&PsdState::initial(4), &i, &p);
        for m in &out.panel_motors {
            assert_eq!(*m, PsdMotorCommand::Stop);
        }
    }

    #[test]
    fn happy_path_opens_panels() {
        let p = PsdParams::default_station();
        let panels = vec![closed(); 4];
        let i = inputs_with(true, true, true, PsdCommand::Open, false, &panels);
        let out = psd_evaluate(&PsdState::initial(4), &i, &p);
        for m in &out.panel_motors {
            assert_eq!(*m, PsdMotorCommand::DriveOpen);
        }
    }

    #[test]
    fn close_command_drives_close_from_open() {
        let p = PsdParams::default_station();
        let panels = vec![open(); 4];
        let i = inputs_with(true, true, false, PsdCommand::Close, false, &panels);
        let out = psd_evaluate(&PsdState::initial(4), &i, &p);
        for m in &out.panel_motors {
            assert_eq!(*m, PsdMotorCommand::DriveClose);
        }
    }

    #[test]
    fn obstruction_stops_close() {
        let p = PsdParams::default_station();
        let mut panels = vec![open(); 4];
        panels[1].obstruction_detected = true;
        let i = inputs_with(true, true, false, PsdCommand::Close, false, &panels);
        let out = psd_evaluate(&PsdState::initial(4), &i, &p);
        // Panel 1 should stop; others should drive close.
        assert_eq!(out.panel_motors[1], PsdMotorCommand::Stop);
        assert_eq!(out.panel_motors[0], PsdMotorCommand::DriveClose);
        assert!(out.any_obstructed);
    }

    #[test]
    fn emergency_stop_opens_all() {
        let p = PsdParams::default_station();
        let panels = vec![closed(); 4];
        let i = inputs_with(false, false, false, PsdCommand::Close, true, &panels);
        let out = psd_evaluate(&PsdState::initial(4), &i, &p);
        for m in &out.panel_motors {
            assert_eq!(*m, PsdMotorCommand::DriveOpen);
        }
    }

    #[test]
    fn all_closed_is_and_reduction() {
        let p = PsdParams::default_station();
        let mut panels = vec![closed(); 4];
        let i = inputs_with(true, true, false, PsdCommand::Hold, false, &panels);
        let out = psd_evaluate(&PsdState::initial(4), &i, &p);
        assert!(out.all_closed);
        panels[2] = open();
        let i = inputs_with(true, true, false, PsdCommand::Hold, false, &panels);
        let out = psd_evaluate(&PsdState::initial(4), &i, &p);
        assert!(!out.all_closed);
    }

    #[test]
    fn motor_timeout_faults_panel() {
        let p = PsdParams::default_station();
        let mut state = PsdState::initial(1);
        state.panels[0] = PsdPanelState {
            motor: PsdMotorCommand::DriveOpen,
            status: PsdPanelStatus::Opening,
            motor_started_ns: Some(0),
            fault_until_ns: None,
            obstruction_latched: false,
        };
        let panels = vec![PsdSensors {
            closed_limit: false,
            open_limit: false,
            motor_current_ma: 100,
            obstruction_detected: false,
        }];
        let mut i = inputs_with(true, true, true, PsdCommand::Open, false, &panels);
        i.now_ns = 7_000_000_000; // past 6 s timeout
        let out = psd_evaluate(&state, &i, &p);
        assert_eq!(out.panel_motors[0], PsdMotorCommand::Stop);
        assert_eq!(out.panel_statuses[0], PsdPanelStatus::Faulted);
    }

    #[test]
    fn determinism() {
        let p = PsdParams::default_station();
        let panels = vec![closed(); 3];
        let i = inputs_with(true, true, true, PsdCommand::Open, false, &panels);
        let a = psd_evaluate(&PsdState::initial(3), &i, &p);
        let b = psd_evaluate(&PsdState::initial(3), &i, &p);
        assert_eq!(a, b);
    }
}
