//! Inputs and parameters to the BMS evaluator.

use serde::{Deserialize, Serialize};

use crate::types::Chemistry;

/// Per-tick BMS inputs.
///
/// Cell slices are borrowed from the caller to avoid allocation on
/// the SIL-4 hot path. `cell_voltages_mv` and `cell_temps_dc` must
/// have the same length; mismatched lengths trip
/// [`crate::FaultReason::SensorMismatch`].
#[derive(Copy, Clone, Debug, PartialEq, Eq)]
pub struct BmsInputs<'a> {
    pub now_ns: u64,
    /// Cell voltages, millivolts. One entry per cell.
    pub cell_voltages_mv: &'a [u16],
    /// Cell temperatures in tenths of °C. Signed to carry sub-freezing
    /// readings. One entry per cell (parallel to `cell_voltages_mv`).
    pub cell_temps_dc: &'a [i16],
    /// Pack current, milliamps. Positive = charge, negative = discharge.
    pub pack_current_ma: i32,
    /// Pack terminal voltage, millivolts. Used for cross-checks only.
    pub pack_voltage_mv: u32,
    /// External contactor command from the vehicle controller.
    pub external_command: ContactorCommand,
    /// Nanoseconds since the previous tick. Used for Coulomb counting.
    pub dt_ns: u64,
}

/// Vehicle controller's request about contactor state.
#[derive(Copy, Clone, Debug, PartialEq, Eq, Hash, Default, Serialize, Deserialize)]
pub enum ContactorCommand {
    #[default]
    RequestOpen,
    RequestClose,
    /// Clear a latched fault (only effective after cooldown has
    /// elapsed — the BMS will not close the contactor during an
    /// active fault window).
    ClearFault,
}

/// Static BMS calibration. Loaded at commissioning; never changes.
#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct BmsParams {
    pub chemistry: Chemistry,
    /// Nominal cell count (used for alarm-level checks and for
    /// cross-check of the input slices).
    pub cell_count: u16,
    /// Per-cell nominal capacity in milliamp-hours.
    pub cell_capacity_mah: u32,

    // --- Voltage limits (mV) -------------------------------------------
    /// Hard trip (over-voltage): any cell at or above → fault.
    pub v_trip_max_mv: u16,
    /// Warning threshold; derate charge when any cell crosses.
    pub v_warn_max_mv: u16,
    /// Warning threshold; derate discharge when any cell crosses.
    pub v_warn_min_mv: u16,
    /// Hard trip (under-voltage): any cell at or below → fault.
    pub v_trip_min_mv: u16,

    // --- Temperature limits (tenths of °C) -----------------------------
    pub t_trip_max_dc: i16,
    pub t_warn_max_dc: i16,
    pub t_warn_min_dc: i16,
    pub t_trip_min_dc: i16,

    // --- Balance and current ------------------------------------------
    /// Cell voltage spread above which [`crate::FaultReason::Imbalance`]
    /// trips.
    pub imbalance_trip_mv: u16,
    /// Absolute pack current limit, milliamps. Exceeding in either
    /// direction trips OverCurrent.
    pub current_trip_ma: u32,
    /// Pack-level maximum charge rate (mA) under fully nominal
    /// conditions. Actual limit is derated from this.
    pub max_charge_ma: u32,
    /// Pack-level maximum discharge rate (mA) nominal.
    pub max_discharge_ma: u32,

    // --- Timing --------------------------------------------------------
    /// Cooldown after any fault before the contactor can be re-closed.
    pub fault_cooldown_ms: u32,
}

impl BmsParams {
    /// Reasonable defaults for a Na-ion pack on a light-metro trainset
    /// (per [RFC 0003 §4.3](../../../docs/rfcs/0003-samawah-reference-deployment.md)
    /// the reference 3-car carries 360 kWh; at ~3.2 V/cell average
    /// that is thousands of cells in series-parallel — the numbers
    /// here describe a representative cell, not the whole pack).
    #[must_use]
    pub fn sodium_ion_default(cell_count: u16, cell_capacity_mah: u32) -> Self {
        Self {
            chemistry: Chemistry::SodiumIon,
            cell_count,
            cell_capacity_mah,
            v_trip_max_mv: 3_950,
            v_warn_max_mv: 3_850,
            v_warn_min_mv: 2_200,
            v_trip_min_mv: 2_000,
            t_trip_max_dc: 650,  // 65 °C
            t_warn_max_dc: 550,  // 55 °C
            t_warn_min_dc: -150, // −15 °C
            t_trip_min_dc: -250, // −25 °C
            imbalance_trip_mv: 150,
            current_trip_ma: 1_500_000,  // 1500 A
            max_charge_ma: 1_000_000,    // 1000 A
            max_discharge_ma: 1_200_000, // 1200 A
            fault_cooldown_ms: 10_000,
        }
    }

    /// Reasonable defaults for an LFP pack. Tighter voltage window,
    /// restricts charging below 0 °C.
    #[must_use]
    pub fn lfp_default(cell_count: u16, cell_capacity_mah: u32) -> Self {
        Self {
            chemistry: Chemistry::Lfp,
            cell_count,
            cell_capacity_mah,
            v_trip_max_mv: 3_700,
            v_warn_max_mv: 3_600,
            v_warn_min_mv: 2_700,
            v_trip_min_mv: 2_500,
            t_trip_max_dc: 600,
            t_warn_max_dc: 500,
            t_warn_min_dc: 50, // +5 °C — charge derate starts
            t_trip_min_dc: -100,
            imbalance_trip_mv: 100,
            current_trip_ma: 1_500_000,
            max_charge_ma: 800_000,
            max_discharge_ma: 1_000_000,
            fault_cooldown_ms: 10_000,
        }
    }
}
