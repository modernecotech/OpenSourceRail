//! OpenSourceRail station SCADA.
//!
//! Supervises the station's fixed building systems —  escalators,
//! lifts, lighting zones, HVAC, CCTV NVR — and rolls them up into
//! a station-level health signal. Most of these subsystems are
//! vendor equipment with their own internal controllers; this crate
//! is primarily a *monitor* that watches status flags and issues
//! permissive commands (start/stop, call-floor, setpoint).
//!
//! Phase 2e crate of [RFC 0005 §4.7](../../../docs/rfcs/0005-sbc-software-architecture.md).
//! SIL-2: a bad command from here can trap passengers in a lift or
//! stop an escalator unexpectedly; safety interlocks live in the
//! vendor equipment. This crate enforces the commanded-only-when-
//! safe-to-command discipline and rolls faults up.
//!
//! # Subsystems modelled
//!
//! - **Escalators** — array. Per unit: run direction, faulted,
//!   overload, emergency-stop.
//! - **Lifts** — array. Per unit: current floor, requested floor,
//!   faulted, door open.
//! - **Lighting zones** — array of on/off + dim setpoint.
//! - **Station HVAC** — simple setpoint + fault flag.
//! - **CCTV NVR** — online + free-storage gauge.
//!
//! # Properties (proptest-verified)
//!
//! - **SC1 determinism.**
//! - **SC2 emergency-stop cascade:** an `emergency_stop` input
//!   forces every escalator `Run` command to `Stop`, all lifts to
//!   hold at current floor, station HVAC to off.
//! - **SC3 any-fault downgrade:** if any subsystem reports a
//!   fault, `station_health != Nominal`.
//! - **SC4 CCTV storage alarm:** when NVR storage < threshold,
//!   alarm is at least `Warning`.

#![forbid(unsafe_code)]

use serde::{Deserialize, Serialize};

// ---------------------------------------------------------------------------
// Subsystem types
// ---------------------------------------------------------------------------

#[derive(Copy, Clone, Debug, PartialEq, Eq, Hash, Default, Serialize, Deserialize)]
pub enum EscalatorDirection {
    #[default]
    Stop,
    Up,
    Down,
}

#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct EscalatorStatus {
    pub commanded: EscalatorDirection,
    pub running: EscalatorDirection,
    pub faulted: bool,
    pub overload: bool,
    pub estop: bool,
}

#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct LiftStatus {
    pub current_floor: i8,
    pub requested_floor: i8,
    pub door_open: bool,
    pub faulted: bool,
}

#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct LightingZoneStatus {
    pub enabled: bool,
    pub dim_ppt: u16,
    pub faulted: bool,
}

#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct StationHvacStatus {
    pub setpoint_dc: i16,
    pub faulted: bool,
}

#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct CctvNvrStatus {
    pub online: bool,
    /// Free storage as ppt of total capacity.
    pub free_storage_ppt: u16,
    pub channels_offline: u8,
}

// ---------------------------------------------------------------------------
// Inputs
// ---------------------------------------------------------------------------

#[derive(Clone, Debug)]
pub struct StationScadaInputs<'a> {
    pub now_ns: u64,
    pub emergency_stop: bool,
    pub escalators: &'a [EscalatorStatus],
    pub lifts: &'a [LiftStatus],
    pub lighting_zones: &'a [LightingZoneStatus],
    pub hvac: StationHvacStatus,
    pub cctv: CctvNvrStatus,
    /// Operator-commanded escalator directions (parallel to
    /// `escalators`). `None` at any index leaves the existing command.
    pub escalator_commands: &'a [Option<EscalatorDirection>],
    /// Operator-commanded lift floor calls (parallel to `lifts`).
    pub lift_calls: &'a [Option<i8>],
}

#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct StationScadaParams {
    pub min_free_storage_ppt: u16,
    pub hvac_off_setpoint_dc: i16,
}

impl StationScadaParams {
    #[must_use]
    pub fn default_metro() -> Self {
        Self {
            min_free_storage_ppt: 100, // 10 % free
            hvac_off_setpoint_dc: 0,
        }
    }
}

// ---------------------------------------------------------------------------
// Output
// ---------------------------------------------------------------------------

#[derive(Copy, Clone, Debug, PartialEq, Eq, Hash, Default, Serialize, Deserialize, PartialOrd, Ord)]
pub enum StationHealth {
    #[default]
    Nominal = 0,
    Warning = 1,
    Degraded = 2,
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct StationScadaOutput {
    pub health: StationHealth,
    /// Per-escalator commanded direction (after emergency gating).
    pub escalator_commands: Vec<EscalatorDirection>,
    /// Per-lift requested floor (after emergency gating — on e-stop,
    /// equal to current floor, meaning "hold").
    pub lift_requests: Vec<i8>,
    /// Per-zone effective enabled (emergency forces false for
    /// HVAC, not lighting — lighting stays on during evacuation).
    pub lighting_enabled: Vec<bool>,
    pub hvac_setpoint_dc: i16,
    pub cctv_recording: bool,
    pub fault_count: u32,
}

// ---------------------------------------------------------------------------
// Evaluator
// ---------------------------------------------------------------------------

#[must_use]
pub fn station_scada_evaluate(
    inputs: &StationScadaInputs<'_>,
    params: &StationScadaParams,
) -> StationScadaOutput {
    let mut fault_count: u32 = 0;
    let mut health = StationHealth::Nominal;

    // --- Escalators --------------------------------------------------
    let escalator_commands: Vec<EscalatorDirection> = inputs
        .escalators
        .iter()
        .enumerate()
        .map(|(i, esc)| {
            if esc.faulted || esc.overload || esc.estop {
                fault_count += 1;
            }
            if inputs.emergency_stop || esc.faulted || esc.overload || esc.estop {
                EscalatorDirection::Stop
            } else {
                match inputs.escalator_commands.get(i).and_then(|c| *c) {
                    Some(dir) => dir,
                    None => esc.commanded,
                }
            }
        })
        .collect();

    // --- Lifts --------------------------------------------------------
    let lift_requests: Vec<i8> = inputs
        .lifts
        .iter()
        .enumerate()
        .map(|(i, lift)| {
            if lift.faulted {
                fault_count += 1;
            }
            if inputs.emergency_stop || lift.faulted {
                lift.current_floor
            } else {
                match inputs.lift_calls.get(i).and_then(|c| *c) {
                    Some(f) => f,
                    None => lift.requested_floor,
                }
            }
        })
        .collect();

    // --- Lighting -----------------------------------------------------
    let lighting_enabled: Vec<bool> = inputs
        .lighting_zones
        .iter()
        .map(|z| {
            if z.faulted {
                fault_count += 1;
            }
            // Lighting stays on during emergency — evacuation requires visibility.
            if z.faulted { false } else { z.enabled }
        })
        .collect();

    // --- HVAC ---------------------------------------------------------
    if inputs.hvac.faulted {
        fault_count += 1;
    }
    let hvac_setpoint_dc = if inputs.emergency_stop || inputs.hvac.faulted {
        params.hvac_off_setpoint_dc
    } else {
        inputs.hvac.setpoint_dc
    };

    // --- CCTV ---------------------------------------------------------
    let cctv_recording = inputs.cctv.online;
    if !inputs.cctv.online {
        fault_count += 1;
    }
    if inputs.cctv.free_storage_ppt < params.min_free_storage_ppt && health == StationHealth::Nominal {
        health = StationHealth::Warning;
    }
    if inputs.cctv.channels_offline > 0 && health == StationHealth::Nominal {
        health = StationHealth::Warning;
    }

    // Rollup.
    if fault_count > 0 && health == StationHealth::Nominal {
        health = StationHealth::Warning;
    }
    if fault_count >= 3 {
        health = StationHealth::Degraded;
    }
    if inputs.emergency_stop {
        health = StationHealth::Degraded;
    }

    StationScadaOutput {
        health,
        escalator_commands,
        lift_requests,
        lighting_enabled,
        hvac_setpoint_dc,
        cctv_recording,
        fault_count,
    }
}

// ---------------------------------------------------------------------------
// Unit tests
// ---------------------------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;

    fn healthy_escalator() -> EscalatorStatus {
        EscalatorStatus {
            commanded: EscalatorDirection::Up,
            running: EscalatorDirection::Up,
            faulted: false,
            overload: false,
            estop: false,
        }
    }

    fn healthy_lift() -> LiftStatus {
        LiftStatus {
            current_floor: 0,
            requested_floor: 0,
            door_open: false,
            faulted: false,
        }
    }

    fn healthy_zone() -> LightingZoneStatus {
        LightingZoneStatus {
            enabled: true,
            dim_ppt: 1000,
            faulted: false,
        }
    }

    fn healthy_cctv() -> CctvNvrStatus {
        CctvNvrStatus {
            online: true,
            free_storage_ppt: 500,
            channels_offline: 0,
        }
    }

    fn healthy_hvac() -> StationHvacStatus {
        StationHvacStatus {
            setpoint_dc: 230,
            faulted: false,
        }
    }

    #[test]
    fn nominal_station_is_nominal() {
        let escalators = vec![healthy_escalator(); 2];
        let lifts = vec![healthy_lift(); 2];
        let zones = vec![healthy_zone(); 3];
        let esc_cmd = vec![None; 2];
        let lift_call = vec![None; 2];
        let out = station_scada_evaluate(
            &StationScadaInputs {
                now_ns: 0,
                emergency_stop: false,
                escalators: &escalators,
                lifts: &lifts,
                lighting_zones: &zones,
                hvac: healthy_hvac(),
                cctv: healthy_cctv(),
                escalator_commands: &esc_cmd,
                lift_calls: &lift_call,
            },
            &StationScadaParams::default_metro(),
        );
        assert_eq!(out.health, StationHealth::Nominal);
        assert_eq!(out.fault_count, 0);
    }

    #[test]
    fn emergency_stops_escalators_and_hvac() {
        let escalators = vec![healthy_escalator(); 2];
        let lifts = vec![healthy_lift()];
        let zones = vec![healthy_zone()];
        let esc_cmd = vec![None; 2];
        let lift_call = vec![None; 1];
        let out = station_scada_evaluate(
            &StationScadaInputs {
                now_ns: 0,
                emergency_stop: true,
                escalators: &escalators,
                lifts: &lifts,
                lighting_zones: &zones,
                hvac: healthy_hvac(),
                cctv: healthy_cctv(),
                escalator_commands: &esc_cmd,
                lift_calls: &lift_call,
            },
            &StationScadaParams::default_metro(),
        );
        for d in &out.escalator_commands {
            assert_eq!(*d, EscalatorDirection::Stop);
        }
        assert_eq!(out.hvac_setpoint_dc, 0);
        assert_eq!(out.health, StationHealth::Degraded);
    }

    #[test]
    fn escalator_fault_stops_command() {
        let mut escalators = vec![healthy_escalator(); 2];
        escalators[0].faulted = true;
        let lifts = vec![healthy_lift()];
        let zones = vec![healthy_zone()];
        let esc_cmd = vec![Some(EscalatorDirection::Up), Some(EscalatorDirection::Up)];
        let lift_call = vec![None; 1];
        let out = station_scada_evaluate(
            &StationScadaInputs {
                now_ns: 0,
                emergency_stop: false,
                escalators: &escalators,
                lifts: &lifts,
                lighting_zones: &zones,
                hvac: healthy_hvac(),
                cctv: healthy_cctv(),
                escalator_commands: &esc_cmd,
                lift_calls: &lift_call,
            },
            &StationScadaParams::default_metro(),
        );
        assert_eq!(out.escalator_commands[0], EscalatorDirection::Stop);
        assert_eq!(out.escalator_commands[1], EscalatorDirection::Up);
        assert!(out.fault_count >= 1);
    }

    #[test]
    fn lift_fault_holds_at_current() {
        let escalators = vec![healthy_escalator()];
        let mut lifts = vec![healthy_lift()];
        lifts[0].current_floor = 3;
        lifts[0].faulted = true;
        let zones = vec![healthy_zone()];
        let esc_cmd = vec![None];
        let lift_call = vec![Some(5)];
        let out = station_scada_evaluate(
            &StationScadaInputs {
                now_ns: 0,
                emergency_stop: false,
                escalators: &escalators,
                lifts: &lifts,
                lighting_zones: &zones,
                hvac: healthy_hvac(),
                cctv: healthy_cctv(),
                escalator_commands: &esc_cmd,
                lift_calls: &lift_call,
            },
            &StationScadaParams::default_metro(),
        );
        assert_eq!(out.lift_requests[0], 3); // held at current floor
    }

    #[test]
    fn low_storage_is_warning() {
        let escalators = vec![healthy_escalator()];
        let lifts = vec![healthy_lift()];
        let zones = vec![healthy_zone()];
        let esc_cmd = vec![None];
        let lift_call = vec![None];
        let out = station_scada_evaluate(
            &StationScadaInputs {
                now_ns: 0,
                emergency_stop: false,
                escalators: &escalators,
                lifts: &lifts,
                lighting_zones: &zones,
                hvac: healthy_hvac(),
                cctv: CctvNvrStatus {
                    online: true,
                    free_storage_ppt: 50, // below 100 threshold
                    channels_offline: 0,
                },
                escalator_commands: &esc_cmd,
                lift_calls: &lift_call,
            },
            &StationScadaParams::default_metro(),
        );
        assert_eq!(out.health, StationHealth::Warning);
    }

    #[test]
    fn determinism() {
        let escalators = vec![healthy_escalator()];
        let lifts = vec![healthy_lift()];
        let zones = vec![healthy_zone()];
        let esc_cmd = vec![None];
        let lift_call = vec![None];
        let inputs = StationScadaInputs {
            now_ns: 0,
            emergency_stop: false,
            escalators: &escalators,
            lifts: &lifts,
            lighting_zones: &zones,
            hvac: healthy_hvac(),
            cctv: healthy_cctv(),
            escalator_commands: &esc_cmd,
            lift_calls: &lift_call,
        };
        let a = station_scada_evaluate(&inputs, &StationScadaParams::default_metro());
        let b = station_scada_evaluate(&inputs, &StationScadaParams::default_metro());
        assert_eq!(a, b);
    }
}
