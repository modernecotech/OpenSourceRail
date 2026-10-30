//! Inputs and parameters to the BMS evaluator.

use serde::{Deserialize, Serialize};

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
    /// Qualified battery-compartment off-gas detector trip.
    pub off_gas_detected: bool,
    /// Independent fire-controller request to isolate this car pack.
    pub external_fire_trip: bool,
    /// Diagnostic identity only. Isolation remains pack/string scoped unless
    /// the commissioned topology proves an individual-module bypass.
    pub hazard_module_id: Option<u8>,
    pub hazard_string_id: Option<u8>,
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

    // --- State of health ----------------------------------------------
    /// Capacity fade in parts-per-million per equivalent full cycle.
    /// A value of 200 models 20% fade after 1,000 nominal cycles.
    pub cycle_fade_ppm_per_efc: u32,
    /// Cell temperature at which cycle throughput receives the hot-cycle
    /// acceleration multiplier.
    pub hot_cycle_threshold_dc: i16,
    /// Multiplier applied to degradation throughput at/above the threshold.
    pub hot_cycle_multiplier: u16,

    // --- Timing --------------------------------------------------------
    /// Cooldown after any fault before the contactor can be re-closed.
    pub fault_cooldown_ms: u32,
}

impl BmsParams {
    /// Reference LFP calibration. Charging is derated below 5 °C and the
    /// evaluator force-opens the pack contactor at the hard limits.
    #[must_use]
    pub fn lfp_default(cell_count: u16, cell_capacity_mah: u32) -> Self {
        Self {
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
            cycle_fade_ppm_per_efc: 200,
            hot_cycle_threshold_dc: 400,
            hot_cycle_multiplier: 2,
            fault_cooldown_ms: 10_000,
        }
    }
}
