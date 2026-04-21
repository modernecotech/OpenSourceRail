//! OpenSourceRail Train Control & Management System (TCMS).
//!
//! Central state aggregator for the onboard app layer. TCMS consumes
//! health rollups from every other crate (ATP / brake / BMS /
//! traction / ATO / doors / SIL-4 monitors / HVAC / lighting / PIS)
//! and produces a single [`ConsistStatus`] blob that downstream
//! consumers ([`osr_dmi`], [`osr_pis_onboard`], [`osr_t2g`],
//! [`osr_event_recorder`]) read from.
//!
//! Phase 2c crate 8 of [RFC 0005 §4.1](../../../docs/rfcs/0005-sbc-software-architecture.md).
//! SIL-2: failure here degrades coordination and DMI accuracy but
//! does not directly endanger passengers — the SIL-4 partition
//! runs independently.
//!
//! # Design: inputs are small flat structs
//!
//! To avoid a tangled dependency graph (TCMS depending on every
//! crate), the caller's glue code translates each producer's
//! output into a corresponding small struct here. That keeps TCMS
//! testable in isolation and keeps each other crate's type surface
//! from leaking into the rest of the workspace.
//!
//! # Properties (proptest-verified)
//!
//! - **TCMS1 determinism.**
//! - **TCMS2 ready-to-move is a conjunction:** `ready_to_move == true`
//!   requires all SIL-4 partitions green (no emergencies, interlock
//!   ok, no latched faults).
//! - **TCMS3 worst-alarm is monotone in any input:** raising any
//!   input alarm level never lowers the output.
//! - **TCMS4 any emergency → Trip alarm:** if any of the 5 emergency
//!   sources is active, the output `worst_alarm == Trip`.

#![forbid(unsafe_code)]

use serde::{Deserialize, Serialize};

// ---------------------------------------------------------------------------
// Shared alarm level (mirrors the per-crate levels)
// ---------------------------------------------------------------------------

#[derive(Copy, Clone, Debug, PartialEq, Eq, Hash, Ord, PartialOrd, Default, Serialize, Deserialize)]
pub enum AlarmLevel {
    #[default]
    Nominal = 0,
    Warning = 1,
    Trip = 2,
}

// ---------------------------------------------------------------------------
// Flat input struct
// ---------------------------------------------------------------------------

#[derive(Copy, Clone, Debug, PartialEq, Eq, Default, Serialize, Deserialize)]
pub struct TcmsInputs {
    pub now_ns: u64,

    // Kinematic summary.
    pub speed_mmps: i32,
    pub section_id: Option<u32>,
    pub at_station: bool,

    // SIL-4 emergency sources (bool = active).
    pub atp_emergency: bool,
    pub vigilance_emergency: bool,
    pub fire_emergency: bool,
    pub derailment_emergency: bool,
    pub driver_emergency: bool,

    // Interlock + traction readiness.
    pub doors_interlock_ok: bool,
    pub bms_contactor_closed: bool,
    pub traction_inverter_enabled: bool,

    // Health / alarm signals from subsystems.
    pub bms_alarm: AlarmLevel,
    pub traction_alarm: AlarmLevel,
    pub fire_alarm: AlarmLevel,
    pub derailment_alarm: AlarmLevel,
    pub hot_axle_alarm: AlarmLevel,
    pub hvac_alarm: AlarmLevel,
    pub comfort_alarm: AlarmLevel,
    pub door_alarm: AlarmLevel,

    // Pack / rail rollup.
    pub soc_ppt: u16,
    pub v24_rail_enabled: bool,
    pub v110_rail_enabled: bool,
    pub v400_rail_enabled: bool,
}

// ---------------------------------------------------------------------------
// Output
// ---------------------------------------------------------------------------

/// Emergency-source bitmask, mirrors the 5 O4-topic sources.
#[derive(Copy, Clone, Debug, PartialEq, Eq, Default, Serialize, Deserialize)]
pub struct EmergencySources {
    pub atp: bool,
    pub vigilance: bool,
    pub fire: bool,
    pub derailment: bool,
    pub driver: bool,
}

impl EmergencySources {
    #[must_use]
    pub fn any(&self) -> bool {
        self.atp || self.vigilance || self.fire || self.derailment || self.driver
    }
    #[must_use]
    pub fn count(&self) -> u8 {
        u8::from(self.atp)
            + u8::from(self.vigilance)
            + u8::from(self.fire)
            + u8::from(self.derailment)
            + u8::from(self.driver)
    }
}

/// Consolidated consist status.
#[derive(Copy, Clone, Debug, PartialEq, Eq, Default, Serialize, Deserialize)]
pub struct ConsistStatus {
    pub now_ns: u64,
    pub speed_mmps: i32,
    pub section_id: Option<u32>,
    pub at_station: bool,

    pub worst_alarm: AlarmLevel,
    pub emergency_sources: EmergencySources,
    pub any_emergency: bool,

    /// True iff all SIL-4 partitions are green AND interlocks hold.
    pub ready_to_move: bool,

    /// Rail availability rollup.
    pub v24_rail_enabled: bool,
    pub v110_rail_enabled: bool,
    pub v400_rail_enabled: bool,
    pub soc_ppt: u16,
}

// ---------------------------------------------------------------------------
// Evaluator
// ---------------------------------------------------------------------------

#[must_use]
pub fn tcms_evaluate(inputs: &TcmsInputs) -> ConsistStatus {
    let emergency_sources = EmergencySources {
        atp: inputs.atp_emergency,
        vigilance: inputs.vigilance_emergency,
        fire: inputs.fire_emergency,
        derailment: inputs.derailment_emergency,
        driver: inputs.driver_emergency,
    };
    let any_emergency = emergency_sources.any();

    // Worst-alarm rollup.
    let mut worst = AlarmLevel::Nominal;
    for a in [
        inputs.bms_alarm,
        inputs.traction_alarm,
        inputs.fire_alarm,
        inputs.derailment_alarm,
        inputs.hot_axle_alarm,
        inputs.hvac_alarm,
        inputs.comfort_alarm,
        inputs.door_alarm,
    ] {
        if a > worst {
            worst = a;
        }
    }
    if any_emergency && worst < AlarmLevel::Trip {
        worst = AlarmLevel::Trip;
    }

    // Ready-to-move: every gate green.
    let ready_to_move = !any_emergency
        && inputs.doors_interlock_ok
        && inputs.bms_contactor_closed
        && inputs.traction_inverter_enabled
        && matches!(inputs.bms_alarm, AlarmLevel::Nominal | AlarmLevel::Warning)
        && matches!(inputs.traction_alarm, AlarmLevel::Nominal | AlarmLevel::Warning)
        && matches!(inputs.fire_alarm, AlarmLevel::Nominal | AlarmLevel::Warning)
        && matches!(inputs.derailment_alarm, AlarmLevel::Nominal | AlarmLevel::Warning);

    ConsistStatus {
        now_ns: inputs.now_ns,
        speed_mmps: inputs.speed_mmps,
        section_id: inputs.section_id,
        at_station: inputs.at_station,
        worst_alarm: worst,
        emergency_sources,
        any_emergency,
        ready_to_move,
        v24_rail_enabled: inputs.v24_rail_enabled,
        v110_rail_enabled: inputs.v110_rail_enabled,
        v400_rail_enabled: inputs.v400_rail_enabled,
        soc_ppt: inputs.soc_ppt,
    }
}

// ---------------------------------------------------------------------------
// Unit tests
// ---------------------------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;

    fn clean_inputs() -> TcmsInputs {
        TcmsInputs {
            now_ns: 0,
            speed_mmps: 10_000,
            section_id: Some(1000),
            at_station: false,
            atp_emergency: false,
            vigilance_emergency: false,
            fire_emergency: false,
            derailment_emergency: false,
            driver_emergency: false,
            doors_interlock_ok: true,
            bms_contactor_closed: true,
            traction_inverter_enabled: true,
            bms_alarm: AlarmLevel::Nominal,
            traction_alarm: AlarmLevel::Nominal,
            fire_alarm: AlarmLevel::Nominal,
            derailment_alarm: AlarmLevel::Nominal,
            hot_axle_alarm: AlarmLevel::Nominal,
            hvac_alarm: AlarmLevel::Nominal,
            comfort_alarm: AlarmLevel::Nominal,
            door_alarm: AlarmLevel::Nominal,
            soc_ppt: 800,
            v24_rail_enabled: true,
            v110_rail_enabled: true,
            v400_rail_enabled: true,
        }
    }

    #[test]
    fn clean_is_ready() {
        let out = tcms_evaluate(&clean_inputs());
        assert!(out.ready_to_move);
        assert_eq!(out.worst_alarm, AlarmLevel::Nominal);
        assert!(!out.any_emergency);
    }

    #[test]
    fn any_emergency_sets_trip_and_blocks_move() {
        let mut i = clean_inputs();
        i.fire_emergency = true;
        let out = tcms_evaluate(&i);
        assert_eq!(out.worst_alarm, AlarmLevel::Trip);
        assert!(out.any_emergency);
        assert!(!out.ready_to_move);
        assert!(out.emergency_sources.fire);
    }

    #[test]
    fn door_open_blocks_move() {
        let mut i = clean_inputs();
        i.doors_interlock_ok = false;
        let out = tcms_evaluate(&i);
        assert!(!out.ready_to_move);
    }

    #[test]
    fn worst_alarm_takes_max() {
        let mut i = clean_inputs();
        i.bms_alarm = AlarmLevel::Warning;
        i.hvac_alarm = AlarmLevel::Warning;
        let out = tcms_evaluate(&i);
        assert_eq!(out.worst_alarm, AlarmLevel::Warning);

        i.fire_alarm = AlarmLevel::Trip;
        let out = tcms_evaluate(&i);
        assert_eq!(out.worst_alarm, AlarmLevel::Trip);
    }

    #[test]
    fn determinism() {
        let i = clean_inputs();
        assert_eq!(tcms_evaluate(&i), tcms_evaluate(&i));
    }
}
