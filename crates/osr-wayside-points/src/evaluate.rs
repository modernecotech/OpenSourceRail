//! Pure evaluator — the single entry point of the crate.

use crate::inputs::{SwitchInputs, SwitchParams};
use crate::output::{FaultReason, SwitchOutput, SwitchState};
use crate::types::{CommandedPosition, DetectedPosition, MotorCommand, RawSensor};

/// Run one tick of the points controller.
///
/// Pure function of `(prev, inputs, params)`. Caller applies
/// `output.motor` to the motor drive and, if `output.publish_observation`
/// is `Some`, proposes a `SwitchObservation` entry to the consensus
/// cluster (Category::Advisory — the committed log serves as the
/// authoritative detection ground truth for the interlocking).
#[must_use]
pub fn switch_evaluate(
    prev: &SwitchState,
    inputs: &SwitchInputs,
    params: &SwitchParams,
) -> SwitchOutput {
    // --- 1. Fuse sensors (W2: fail-restrictive) -------------------------
    let detected = fuse_sensors(inputs.sensor_a, inputs.sensor_b);

    // --- 2. Merge commanded — hold the most recent command. ------------
    let commanded = inputs.commanded.or(prev.commanded);

    // --- 3. Fault handling ----------------------------------------------
    // New faults trump everything: over-temp, drive fault, and motor
    // timeout all latch a cooldown.
    let mut fault_until_ns = prev.fault_until_ns;
    let mut fault_reason = prev.fault_reason;

    if inputs.motor_over_temp && fault_reason != Some(FaultReason::OverTemperature) {
        fault_reason = Some(FaultReason::OverTemperature);
        fault_until_ns = Some(
            inputs
                .now_ns
                .saturating_add(u64::from(params.motor_cooldown_ms) * 1_000_000),
        );
    } else if inputs.motor_drive_fault && fault_reason != Some(FaultReason::DriveFault) {
        fault_reason = Some(FaultReason::DriveFault);
        fault_until_ns = Some(
            inputs
                .now_ns
                .saturating_add(u64::from(params.motor_cooldown_ms) * 1_000_000),
        );
    }

    // Cooldown expires when now_ns exceeds fault_until_ns.
    if let Some(until) = fault_until_ns {
        if inputs.now_ns >= until {
            fault_until_ns = None;
            fault_reason = None;
        }
    }

    let in_fault = fault_until_ns.is_some();

    // --- 4. Motor-timeout detection (W4) --------------------------------
    let motor_running = !matches!(prev.motor, MotorCommand::Stop);
    let mut motor_timeout_tripped = false;
    if motor_running {
        if let Some(started) = prev.motor_started_ns {
            let run_ms = inputs.now_ns.saturating_sub(started) / 1_000_000;
            if run_ms > u64::from(params.motor_timeout_ms) {
                motor_timeout_tripped = true;
                fault_reason = Some(FaultReason::MotorTimeout);
                fault_until_ns = Some(
                    inputs
                        .now_ns
                        .saturating_add(u64::from(params.motor_cooldown_ms) * 1_000_000),
                );
            }
        }
    }
    let in_fault = in_fault || motor_timeout_tripped;

    // --- 5. Decide motor command ---------------------------------------
    // Rules:
    //   - In fault: Stop (W4).
    //   - If commanded is None: Stop.
    //   - If detected matches commanded: Stop (W3).
    //   - If detected == opposite of commanded OR Unknown: drive.
    //     (Never drive "away" — if detected already matches, we're
    //     done. If detected is Unknown, drive toward target; W5 holds
    //     because we never drive *opposite* to commanded.)
    let motor = if in_fault {
        MotorCommand::Stop
    } else if let Some(cmd) = commanded {
        if detected.matches(cmd) {
            MotorCommand::Stop
        } else {
            match cmd {
                CommandedPosition::Normal => MotorCommand::DriveToNormal,
                CommandedPosition::Reverse => MotorCommand::DriveToReverse,
            }
        }
    } else {
        MotorCommand::Stop
    };

    // --- 6. Track motor start time --------------------------------------
    // If motor was stopped and is now starting, stamp. If motor was
    // running and is now stopping, clear. If still running same
    // direction, carry forward. Direction changes re-stamp.
    let motor_started_ns = match (prev.motor, motor) {
        (_, MotorCommand::Stop) => None,
        (MotorCommand::Stop, _) => Some(inputs.now_ns),
        (prev_m, new_m) if prev_m == new_m => prev.motor_started_ns,
        // Direction change: re-stamp.
        (_, _) => Some(inputs.now_ns),
    };

    // --- 7. Decide whether to publish an observation --------------------
    let publish_observation = if detected != prev.last_emitted_detected {
        Some(detected)
    } else {
        None
    };

    let last_emitted_detected = publish_observation.unwrap_or(prev.last_emitted_detected);

    let state = SwitchState {
        detected,
        commanded,
        motor,
        motor_started_ns,
        fault_until_ns,
        fault_reason,
        last_emitted_detected,
    };

    SwitchOutput {
        state,
        motor,
        publish_observation,
    }
}

/// Fuse two sensor readings into a single `DetectedPosition`.
///
/// W2: any disagreement, any non-end-of-travel reading, or any
/// dead-sensor reading collapses to [`DetectedPosition::Unknown`].
fn fuse_sensors(a: RawSensor, b: RawSensor) -> DetectedPosition {
    match (a, b) {
        (RawSensor::ReadNormal, RawSensor::ReadNormal) => DetectedPosition::Normal,
        (RawSensor::ReadReverse, RawSensor::ReadReverse) => DetectedPosition::Reverse,
        _ => DetectedPosition::Unknown,
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn nominal_inputs(now_ns: u64) -> SwitchInputs {
        SwitchInputs {
            now_ns,
            sensor_a: RawSensor::ReadNormal,
            sensor_b: RawSensor::ReadNormal,
            commanded: Some(CommandedPosition::Normal),
            motor_over_temp: false,
            motor_drive_fault: false,
        }
    }

    #[test]
    fn at_rest_at_target_motor_stops() {
        let prev = SwitchState::default();
        let p = SwitchParams::typical();
        let out = switch_evaluate(&prev, &nominal_inputs(1_000_000), &p);
        assert_eq!(out.motor, MotorCommand::Stop);
        assert_eq!(out.state.detected, DetectedPosition::Normal);
    }

    #[test]
    fn mismatch_drives_toward_command() {
        let prev = SwitchState::default();
        let p = SwitchParams::typical();
        let mut i = nominal_inputs(0);
        i.commanded = Some(CommandedPosition::Reverse);
        // Detected Normal, commanded Reverse → drive to Reverse.
        let out = switch_evaluate(&prev, &i, &p);
        assert_eq!(out.motor, MotorCommand::DriveToReverse);
    }

    #[test]
    fn sensor_disagreement_yields_unknown() {
        let prev = SwitchState::default();
        let p = SwitchParams::typical();
        let mut i = nominal_inputs(0);
        i.sensor_b = RawSensor::ReadReverse;
        let out = switch_evaluate(&prev, &i, &p);
        assert_eq!(out.state.detected, DetectedPosition::Unknown);
    }

    #[test]
    fn dead_sensor_yields_unknown() {
        let prev = SwitchState::default();
        let p = SwitchParams::typical();
        let mut i = nominal_inputs(0);
        i.sensor_a = RawSensor::Dead;
        let out = switch_evaluate(&prev, &i, &p);
        assert_eq!(out.state.detected, DetectedPosition::Unknown);
    }

    #[test]
    fn motor_timeout_latches_fault() {
        let p = SwitchParams::typical();
        // Start with motor running toward Reverse, started at t=0.
        let prev = SwitchState {
            motor: MotorCommand::DriveToReverse,
            motor_started_ns: Some(0),
            commanded: Some(CommandedPosition::Reverse),
            detected: DetectedPosition::Unknown,
            last_emitted_detected: DetectedPosition::Unknown,
            ..Default::default()
        };
        let mut i = nominal_inputs(6_000_000_000); // 6s > 5s timeout
        i.sensor_a = RawSensor::InTransit;
        i.sensor_b = RawSensor::InTransit;
        i.commanded = Some(CommandedPosition::Reverse);
        let out = switch_evaluate(&prev, &i, &p);
        assert_eq!(out.motor, MotorCommand::Stop);
        assert_eq!(out.state.fault_reason, Some(FaultReason::MotorTimeout));
        assert!(out.state.fault_until_ns.is_some());
    }

    #[test]
    fn over_temp_immediately_stops_motor() {
        let prev = SwitchState {
            motor: MotorCommand::DriveToReverse,
            motor_started_ns: Some(1_000_000_000),
            commanded: Some(CommandedPosition::Reverse),
            detected: DetectedPosition::Unknown,
            ..Default::default()
        };
        let p = SwitchParams::typical();
        let mut i = nominal_inputs(2_000_000_000);
        i.motor_over_temp = true;
        i.sensor_a = RawSensor::InTransit;
        i.sensor_b = RawSensor::InTransit;
        i.commanded = Some(CommandedPosition::Reverse);
        let out = switch_evaluate(&prev, &i, &p);
        assert_eq!(out.motor, MotorCommand::Stop);
        assert_eq!(out.state.fault_reason, Some(FaultReason::OverTemperature));
    }

    #[test]
    fn observation_published_only_on_change() {
        let prev = SwitchState {
            detected: DetectedPosition::Normal,
            last_emitted_detected: DetectedPosition::Normal,
            ..Default::default()
        };
        let p = SwitchParams::typical();
        // No change.
        let out = switch_evaluate(&prev, &nominal_inputs(0), &p);
        assert_eq!(out.publish_observation, None);
        // Change.
        let mut i = nominal_inputs(0);
        i.sensor_a = RawSensor::ReadReverse;
        i.sensor_b = RawSensor::ReadReverse;
        let out = switch_evaluate(&prev, &i, &p);
        assert_eq!(out.publish_observation, Some(DetectedPosition::Reverse));
    }

    #[test]
    fn determinism() {
        let prev = SwitchState::default();
        let p = SwitchParams::typical();
        let i = nominal_inputs(1_234_567);
        let a = switch_evaluate(&prev, &i, &p);
        let b = switch_evaluate(&prev, &i, &p);
        assert_eq!(a, b);
    }

    #[test]
    fn no_command_motor_stops() {
        let prev = SwitchState {
            detected: DetectedPosition::Unknown,
            ..Default::default()
        };
        let p = SwitchParams::typical();
        let i = SwitchInputs {
            now_ns: 0,
            sensor_a: RawSensor::InTransit,
            sensor_b: RawSensor::InTransit,
            commanded: None,
            motor_over_temp: false,
            motor_drive_fault: false,
        };
        let out = switch_evaluate(&prev, &i, &p);
        assert_eq!(out.motor, MotorCommand::Stop);
    }

    #[test]
    fn motor_does_not_drive_away_from_commanded() {
        // Already at Normal, commanded Normal → never drive to Reverse.
        let prev = SwitchState {
            detected: DetectedPosition::Normal,
            commanded: Some(CommandedPosition::Normal),
            ..Default::default()
        };
        let p = SwitchParams::typical();
        let out = switch_evaluate(&prev, &nominal_inputs(0), &p);
        assert_eq!(out.motor, MotorCommand::Stop);
        assert_ne!(out.motor, MotorCommand::DriveToReverse);
    }

    #[test]
    fn cooldown_blocks_motor_until_elapsed() {
        let prev = SwitchState {
            fault_until_ns: Some(10_000_000_000),
            fault_reason: Some(FaultReason::MotorTimeout),
            commanded: Some(CommandedPosition::Reverse),
            detected: DetectedPosition::Normal,
            ..Default::default()
        };
        let p = SwitchParams::typical();
        // Before fault cleared:
        let mut i = nominal_inputs(5_000_000_000);
        i.commanded = Some(CommandedPosition::Reverse);
        let out = switch_evaluate(&prev, &i, &p);
        assert_eq!(out.motor, MotorCommand::Stop);
        assert!(out.state.fault_until_ns.is_some());

        // After fault cleared:
        let mut i = nominal_inputs(11_000_000_000);
        i.commanded = Some(CommandedPosition::Reverse);
        let out = switch_evaluate(&prev, &i, &p);
        assert_eq!(out.motor, MotorCommand::DriveToReverse);
        assert!(out.state.fault_until_ns.is_none());
    }
}
