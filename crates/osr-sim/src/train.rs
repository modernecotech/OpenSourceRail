//! Train state machine and energy model.

use osr_core::{ConsistDescriptor, SectionId, StationId, TrainId};
use serde::{Deserialize, Serialize};

/// Direction of travel along a line, expressed relative to the line's own
/// station ordering. On Line 1 (linear, west → east) Forward is eastbound;
/// on Line 2 (ring) Forward is counterclockwise.
#[derive(Copy, Clone, Debug, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum Heading {
    Forward,
    Reverse,
}

impl Heading {
    pub fn flip(self) -> Self {
        match self {
            Heading::Forward => Heading::Reverse,
            Heading::Reverse => Heading::Forward,
        }
    }
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub enum TrainPhase {
    /// Train is at a station.
    Dwelling {
        station: StationId,
        remaining_s: f32,
        /// kWh added to the pack so far in this dwell (for reporting).
        energy_added_kwh: f32,
    },
    /// Train is in a section, in transit.
    Traveling {
        section: SectionId,
        from_station: StationId,
        to_station: StationId,
        total_travel_s: f32,
        remaining_s: f32,
    },
    /// Awaiting dispatch from a dispatch point — either pre-service-start or
    /// because the dispatch throttle (schedule) is holding the train.
    AwaitingDispatch { station: StationId },
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Train {
    pub id: TrainId,
    /// Index into `Network.lines` for the line this train operates on.
    pub line_index: usize,
    pub consist: ConsistDescriptor,
    pub heading: Heading,
    pub phase: TrainPhase,
    /// State of charge, 0.0..1.0
    pub soc: f32,
    /// Cumulative odometer in km since sim start.
    pub odometer_km: f64,
    /// Cumulative energy consumed in kWh.
    pub energy_consumed_kwh: f64,
    /// Cumulative energy received from charging in kWh.
    pub energy_charged_kwh: f64,
    /// Cumulative energy received from onboard roof PV in kWh.
    pub energy_roof_pv_kwh: f64,
    /// Minimum SoC observed so far (for end-of-run reporting).
    pub min_soc_seen: f32,
}

impl Train {
    pub fn battery_capacity_kwh(&self) -> f32 {
        self.consist.battery_capacity_wh as f32 / 1000.0
    }

    /// Energy intensity on a given section, in kWh/km, including HVAC uplift.
    pub fn kwh_per_km(&self, hvac_uplift_frac: f32) -> f32 {
        // Baseline 4 kWh/car-km per RFC 0002 §4.1, scaled by cars.
        let baseline_per_car_km = 4.0_f32;
        let per_car_km = baseline_per_car_km * (1.0 + hvac_uplift_frac);
        per_car_km * self.consist.car_count as f32
    }

    /// Add energy (positive = charging, negative = consuming). Clamps to
    /// [0.0, 1.0] SoC and returns the actually-applied delta.
    pub fn apply_energy_kwh(&mut self, delta_kwh: f32) -> f32 {
        let cap = self.battery_capacity_kwh();
        let current_kwh = self.soc * cap;
        let new_kwh = (current_kwh + delta_kwh).clamp(0.0, cap);
        let applied = new_kwh - current_kwh;
        self.soc = new_kwh / cap;
        if self.soc < self.min_soc_seen {
            self.min_soc_seen = self.soc;
        }
        applied
    }
}
