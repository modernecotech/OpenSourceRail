//! Trackside energy system: PV generation, battery storage, grid tie.
//!
//! Each `EnergySite` is co-located with a station and provides the energy
//! that the station's charging pads deliver to trains. A site has three
//! flows: PV generation (free), battery storage (buffer), and grid tie
//! (import/export). In each sim tick:
//!
//!   1. `tick_pv` runs: PV generated at this time of day is stored in the
//!      battery, with overflow exported to grid (if available) or curtailed.
//!   2. Trains dwelling at stations call `draw_at_station` to request
//!      charging energy. The site delivers from battery first, then from
//!      grid import if the battery is empty or rate-limited.
//!
//! A station not present in `[[sites]]` supplies no charging energy.

use osr_core::StationId;
use serde::{Deserialize, Serialize};
use std::collections::BTreeMap;

// ---------------------------------------------------------------------------
// PV curve
// ---------------------------------------------------------------------------

/// Simple sinusoidal PV output at a given clock time (seconds since midnight).
/// Sunrise is assumed at 06:00, sunset at 18:00 (12 h daylight window).
///
/// The curve is scaled so that its integral over the day equals
/// `peak_sun_hours × nameplate_kw` kWh. The peak (at solar noon) is
/// therefore `nameplate_kw × PSH / (12/π · 2)` ≈ `nameplate_kw × PSH / 7.64`.
/// For PSH = 6 this gives ≈ 78.5 % of nameplate at peak — realistic for
/// a well-designed PV system with typical losses.
pub fn pv_output_kw(nameplate_kw: f32, clock_s: u32, peak_sun_hours: f32) -> f32 {
    let hours_since_sunrise = (clock_s as f32 / 3600.0) - 6.0;
    if !(0.0..=12.0).contains(&hours_since_sunrise) {
        return 0.0;
    }
    let normalized = (std::f32::consts::PI * hours_since_sunrise / 12.0).sin();
    // Integral of sin(πx/12) from 0 to 12 is 12 × 2/π ≈ 7.639.
    const DAILY_SIN_INTEGRAL: f32 = 7.639_437;
    let scale = peak_sun_hours / DAILY_SIN_INTEGRAL;
    nameplate_kw * normalized * scale
}

// ---------------------------------------------------------------------------
// Site config + state
// ---------------------------------------------------------------------------

#[derive(Clone, Debug)]
pub struct EnergySiteConfig {
    pub station: StationId,
    pub pv_nameplate_kw: f32,
    pub storage_capacity_kwh: f32,
    pub storage_max_charge_kw: f32,
    pub storage_max_discharge_kw: f32,
    pub storage_initial_soc: f32,
    pub grid_import_kw: f32,
    pub grid_export_kw: f32,
    pub storage_module_kwh: f32,
    pub charger_max_kw: f32,
    pub charger_max_current_a: f32,
    pub charger_bus_voltage_v: f32,
    pub charger_efficiency: f32,
    pub charger_contact_count: u8,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct EnergySiteSummary {
    pub station_id: String,
    pub station_name: String,
    pub storage_final_soc: f32,
    pub pv_generated_kwh: f64,
    pub grid_imported_kwh: f64,
    pub grid_exported_kwh: f64,
    pub curtailed_kwh: f64,
    pub delivered_to_trains_kwh: f64,
}

#[derive(Clone, Debug)]
pub struct EnergySite {
    pub config: EnergySiteConfig,
    pub storage_soc: f32,
    pub pv_generated_kwh: f64,
    pub grid_imported_kwh: f64,
    pub grid_exported_kwh: f64,
    pub curtailed_kwh: f64,
    pub delivered_to_trains_kwh: f64,
    /// Shared train-side cabinet energy remaining in the current tick.
    charger_budget_kwh: f32,
}

impl EnergySite {
    pub fn new(config: EnergySiteConfig) -> Self {
        let soc = config.storage_initial_soc.clamp(0.0, 1.0);
        Self {
            config,
            storage_soc: soc,
            pv_generated_kwh: 0.0,
            grid_imported_kwh: 0.0,
            grid_exported_kwh: 0.0,
            curtailed_kwh: 0.0,
            delivered_to_trains_kwh: 0.0,
            charger_budget_kwh: f32::INFINITY,
        }
    }

    fn charger_power_limit_kw(&self) -> f32 {
        let current_limited_kw =
            self.config.charger_max_current_a * self.config.charger_bus_voltage_v / 1000.0;
        self.config.charger_max_kw.min(current_limited_kw).max(0.0)
    }

    pub fn storage_stored_kwh(&self) -> f32 {
        self.storage_soc * self.config.storage_capacity_kwh
    }

    /// Advance this site's internal energy flows for one time step:
    /// generate PV, store what we can, export/curtail the rest.
    /// `pv_factor` is 1.0 under normal operation; a dust event would set it
    /// below 1.0. `grid_disabled` blocks both import and export at this site.
    pub fn tick_pv(
        &mut self,
        clock_s: u32,
        dt_s: f32,
        peak_sun_hours: f32,
        pv_factor: f32,
        grid_disabled: bool,
    ) {
        self.charger_budget_kwh = self.charger_power_limit_kw() * dt_s / 3600.0;
        let pv_kw = pv_output_kw(self.config.pv_nameplate_kw, clock_s, peak_sun_hours) * pv_factor;
        let pv_kwh = pv_kw * dt_s / 3600.0;
        self.pv_generated_kwh += f64::from(pv_kwh);

        if pv_kwh <= 0.0 {
            return;
        }

        // Try to store in the battery.
        let remaining_capacity = (1.0 - self.storage_soc) * self.config.storage_capacity_kwh;
        let max_store_kwh = self.config.storage_max_charge_kw * dt_s / 3600.0;
        let stored = pv_kwh.min(remaining_capacity).min(max_store_kwh).max(0.0);
        if self.config.storage_capacity_kwh > 0.0 {
            self.storage_soc += stored / self.config.storage_capacity_kwh;
        }

        // Handle excess: export if possible and grid is up, otherwise curtail.
        let excess = pv_kwh - stored;
        if excess > 0.0 {
            let export_cap_kw = if grid_disabled {
                0.0
            } else {
                self.config.grid_export_kw
            };
            let max_export_kwh = export_cap_kw * dt_s / 3600.0;
            let exported = excess.min(max_export_kwh).max(0.0);
            self.grid_exported_kwh += f64::from(exported);
            self.curtailed_kwh += f64::from(excess - exported);
        }
    }

    /// Deliver up to `max_kwh` from this site to a charging train.
    /// Storage is drawn first, then grid import (unless `grid_disabled`).
    /// Returns the actual energy delivered.
    pub fn draw(&mut self, max_kwh: f32, dt_s: f32, grid_disabled: bool) -> f32 {
        if max_kwh <= 0.0 {
            return 0.0;
        }
        if self.charger_budget_kwh.is_infinite() {
            self.charger_budget_kwh = self.charger_power_limit_kw() * dt_s / 3600.0;
        }
        let requested_delivered = max_kwh.min(self.charger_budget_kwh).max(0.0);
        let efficiency = self.config.charger_efficiency.clamp(0.01, 1.0);
        let mut remaining = requested_delivered / efficiency;

        // 1. Draw from storage, subject to discharge-rate and available energy.
        let max_discharge_kwh = self.config.storage_max_discharge_kw * dt_s / 3600.0;
        let stored = self.storage_stored_kwh();
        let from_storage = remaining.min(max_discharge_kwh).min(stored).max(0.0);
        if self.config.storage_capacity_kwh > 0.0 {
            self.storage_soc -= from_storage / self.config.storage_capacity_kwh;
            self.storage_soc = self.storage_soc.max(0.0);
        }
        remaining -= from_storage;

        // 2. Cover any shortfall via grid import (if the grid is up).
        if remaining > 0.0 && !grid_disabled {
            let max_import_kwh = self.config.grid_import_kw * dt_s / 3600.0;
            let imported = remaining.min(max_import_kwh).max(0.0);
            self.grid_imported_kwh += f64::from(imported);
            remaining -= imported;
        }

        let source_energy = requested_delivered / efficiency - remaining;
        let delivered = source_energy * efficiency;
        self.charger_budget_kwh = (self.charger_budget_kwh - delivered).max(0.0);
        self.delivered_to_trains_kwh += f64::from(delivered);
        delivered
    }

    pub fn summary(&self, station_name: String) -> EnergySiteSummary {
        EnergySiteSummary {
            station_id: self.config.station.to_string(),
            station_name,
            storage_final_soc: self.storage_soc,
            pv_generated_kwh: self.pv_generated_kwh,
            grid_imported_kwh: self.grid_imported_kwh,
            grid_exported_kwh: self.grid_exported_kwh,
            curtailed_kwh: self.curtailed_kwh,
            delivered_to_trains_kwh: self.delivered_to_trains_kwh,
        }
    }
}

// ---------------------------------------------------------------------------
// System aggregate
// ---------------------------------------------------------------------------

#[derive(Clone, Debug, Default)]
pub struct EnergySystem {
    /// Station-ID ordering is intentional: tick order, serialized summaries,
    /// and floating-point aggregate sums must be identical across processes.
    pub sites: BTreeMap<StationId, EnergySite>,
    pub peak_sun_hours: f32,
}

impl EnergySystem {
    pub fn new(configs: Vec<EnergySiteConfig>, peak_sun_hours: f32) -> Self {
        let sites = configs
            .into_iter()
            .map(|c| (c.station, EnergySite::new(c)))
            .collect();
        Self {
            sites,
            peak_sun_hours,
        }
    }

    pub fn tick_pv(&mut self, clock_s: u32, dt_s: f32, faults: &crate::fault::FaultEngine) {
        for (station, site) in self.sites.iter_mut() {
            let pv_factor = faults.pv_factor_for(*station);
            let grid_disabled = faults.grid_disabled_at(*station);
            site.tick_pv(clock_s, dt_s, self.peak_sun_hours, pv_factor, grid_disabled);
        }
    }

    /// Request charging energy at a station. A station omitted from the
    /// configured energy network cannot supply charging energy.
    pub fn draw_at_station(
        &mut self,
        station: StationId,
        max_kwh: f32,
        dt_s: f32,
        faults: &crate::fault::FaultEngine,
    ) -> f32 {
        match self.sites.get_mut(&station) {
            Some(site) => site.draw(max_kwh, dt_s, faults.grid_disabled_at(station)),
            None => 0.0,
        }
    }

    #[allow(dead_code)]
    pub fn is_empty(&self) -> bool {
        self.sites.is_empty()
    }

    pub fn total_pv_generated_kwh(&self) -> f64 {
        self.sites.values().map(|s| s.pv_generated_kwh).sum()
    }
    pub fn total_grid_imported_kwh(&self) -> f64 {
        self.sites.values().map(|s| s.grid_imported_kwh).sum()
    }
    pub fn total_grid_exported_kwh(&self) -> f64 {
        self.sites.values().map(|s| s.grid_exported_kwh).sum()
    }
    pub fn total_curtailed_kwh(&self) -> f64 {
        self.sites.values().map(|s| s.curtailed_kwh).sum()
    }
    pub fn total_delivered_to_trains_kwh(&self) -> f64 {
        self.sites.values().map(|s| s.delivered_to_trains_kwh).sum()
    }
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;
    use osr_core::StationId;

    fn approx(a: f32, b: f32, tol: f32) {
        assert!((a - b).abs() < tol, "expected {b:.4} ± {tol}, got {a:.4}");
    }

    #[test]
    fn pv_zero_at_night() {
        // 01:00 → before sunrise.
        assert_eq!(pv_output_kw(1000.0, 3600, 6.0), 0.0);
        // 23:00 → after sunset.
        assert_eq!(pv_output_kw(1000.0, 23 * 3600, 6.0), 0.0);
    }

    #[test]
    fn pv_peaks_at_solar_noon() {
        let peak_sun_hours = 6.0;
        let nameplate = 1000.0_f32;
        let noon = pv_output_kw(nameplate, 12 * 3600, peak_sun_hours);
        let expected_peak = nameplate * peak_sun_hours / 7.639_437;
        approx(noon, expected_peak, 1.0);
    }

    #[test]
    fn pv_daily_integral_matches_psh() {
        // Integrate in 60-second steps across the 6–18 window.
        let psh = 5.0_f32;
        let nameplate = 1000.0_f32;
        let mut total_kwh = 0.0_f32;
        let dt_s = 60.0;
        let mut t = 6 * 3600;
        while t <= 18 * 3600 {
            total_kwh += pv_output_kw(nameplate, t, psh) * dt_s / 3600.0;
            t += 60;
        }
        approx(total_kwh, psh * nameplate, 5.0); // within 5 kWh on ~5000 kWh — ok
    }

    #[test]
    fn site_stores_pv_up_to_capacity() {
        let mut site = EnergySite::new(EnergySiteConfig {
            station: StationId::new(1),
            pv_nameplate_kw: 1000.0,
            storage_capacity_kwh: 100.0,
            storage_max_charge_kw: 1000.0,
            storage_max_discharge_kw: 1000.0,
            storage_initial_soc: 0.0,
            grid_import_kw: 0.0,
            grid_export_kw: 0.0,
            storage_module_kwh: 500.0,
            charger_max_kw: 500.0,
            charger_max_current_a: 825.0,
            charger_bus_voltage_v: 650.0,
            charger_efficiency: 1.0,
            charger_contact_count: 2,
        });
        site.tick_pv(12 * 3600, 3600.0, 6.0, 1.0, false);
        assert!(site.storage_soc >= 0.99);
        assert!(site.curtailed_kwh > 600.0);
        assert_eq!(site.grid_exported_kwh, 0.0);
    }

    #[test]
    fn site_exports_excess_when_grid_tied() {
        let mut site = EnergySite::new(EnergySiteConfig {
            station: StationId::new(1),
            pv_nameplate_kw: 1000.0,
            storage_capacity_kwh: 100.0,
            storage_max_charge_kw: 1000.0,
            storage_max_discharge_kw: 1000.0,
            storage_initial_soc: 1.0,
            grid_import_kw: 0.0,
            grid_export_kw: 1000.0,
            storage_module_kwh: 500.0,
            charger_max_kw: 500.0,
            charger_max_current_a: 825.0,
            charger_bus_voltage_v: 650.0,
            charger_efficiency: 1.0,
            charger_contact_count: 2,
        });
        site.tick_pv(12 * 3600, 3600.0, 6.0, 1.0, false);
        assert!(site.grid_exported_kwh > 500.0);
        assert_eq!(site.curtailed_kwh, 0.0);
    }

    #[test]
    fn draw_prefers_storage_then_grid() {
        let mut site = EnergySite::new(EnergySiteConfig {
            station: StationId::new(1),
            pv_nameplate_kw: 0.0,
            storage_capacity_kwh: 50.0,
            storage_max_charge_kw: 100.0,
            storage_max_discharge_kw: 100.0,
            storage_initial_soc: 0.2,
            grid_import_kw: 200.0,
            grid_export_kw: 0.0,
            storage_module_kwh: 500.0,
            charger_max_kw: 500.0,
            charger_max_current_a: 825.0,
            charger_bus_voltage_v: 650.0,
            charger_efficiency: 1.0,
            charger_contact_count: 2,
        });
        let delivered = site.draw(20.0, 3600.0, false);
        approx(delivered, 20.0, 0.01);
        approx(site.storage_soc, 0.0, 0.001);
        approx(site.grid_imported_kwh as f32, 10.0, 0.01);
    }

    #[test]
    fn grid_outage_prevents_import() {
        let mut site = EnergySite::new(EnergySiteConfig {
            station: StationId::new(1),
            pv_nameplate_kw: 0.0,
            storage_capacity_kwh: 50.0,
            storage_max_charge_kw: 100.0,
            storage_max_discharge_kw: 100.0,
            storage_initial_soc: 0.2, // 10 kWh stored
            grid_import_kw: 200.0,
            grid_export_kw: 0.0,
            storage_module_kwh: 500.0,
            charger_max_kw: 500.0,
            charger_max_current_a: 825.0,
            charger_bus_voltage_v: 650.0,
            charger_efficiency: 1.0,
            charger_contact_count: 2,
        });
        // Request 20 kWh but grid is disabled: should get 10 kWh (storage only).
        let delivered = site.draw(20.0, 3600.0, true);
        approx(delivered, 10.0, 0.01);
        approx(site.grid_imported_kwh as f32, 0.0, 0.01);
    }

    #[test]
    fn dust_factor_reduces_pv() {
        let mut site = EnergySite::new(EnergySiteConfig {
            station: StationId::new(1),
            pv_nameplate_kw: 1000.0,
            storage_capacity_kwh: 10000.0, // plenty of headroom
            storage_max_charge_kw: 10000.0,
            storage_max_discharge_kw: 10000.0,
            storage_initial_soc: 0.0,
            grid_import_kw: 0.0,
            grid_export_kw: 0.0,
            storage_module_kwh: 500.0,
            charger_max_kw: 500.0,
            charger_max_current_a: 825.0,
            charger_bus_voltage_v: 650.0,
            charger_efficiency: 1.0,
            charger_contact_count: 2,
        });
        // 0.5 dust factor over 1h at solar noon should halve PV.
        site.tick_pv(12 * 3600, 3600.0, 6.0, 0.5, false);
        let expected_pv = 0.5 * 6.0 / 7.639_437 * 1000.0;
        approx(site.pv_generated_kwh as f32, expected_pv, 5.0);
    }

    #[test]
    fn configured_network_does_not_charge_at_station_without_site() {
        let configured_station = StationId::new(1);
        let halt_without_site = StationId::new(2);
        let mut system = EnergySystem::new(
            vec![EnergySiteConfig {
                station: configured_station,
                pv_nameplate_kw: 0.0,
                storage_capacity_kwh: 10.0,
                storage_max_charge_kw: 10.0,
                storage_max_discharge_kw: 10.0,
                storage_initial_soc: 1.0,
                grid_import_kw: 0.0,
                grid_export_kw: 0.0,
                storage_module_kwh: 500.0,
                charger_max_kw: 500.0,
                charger_max_current_a: 825.0,
                charger_bus_voltage_v: 650.0,
                charger_efficiency: 1.0,
                charger_contact_count: 2,
            }],
            5.0,
        );

        assert_eq!(
            system.draw_at_station(
                halt_without_site,
                5.0,
                60.0,
                &crate::fault::FaultEngine::default(),
            ),
            0.0
        );
    }

    #[test]
    fn empty_network_supplies_no_charging_energy() {
        let mut system = EnergySystem::new(Vec::new(), 5.0);
        assert_eq!(
            system.draw_at_station(
                StationId::new(1),
                5.0,
                60.0,
                &crate::fault::FaultEngine::default(),
            ),
            0.0
        );
    }

    #[test]
    fn shared_cabinet_budget_caps_two_draws_in_one_tick() {
        let mut site = EnergySite::new(EnergySiteConfig {
            station: StationId::new(1),
            pv_nameplate_kw: 0.0,
            storage_capacity_kwh: 500.0,
            storage_max_charge_kw: 500.0,
            storage_max_discharge_kw: 1000.0,
            storage_initial_soc: 1.0,
            grid_import_kw: 0.0,
            grid_export_kw: 0.0,
            storage_module_kwh: 500.0,
            charger_max_kw: 500.0,
            charger_max_current_a: 825.0,
            charger_bus_voltage_v: 650.0,
            charger_efficiency: 1.0,
            charger_contact_count: 2,
        });
        site.tick_pv(0, 60.0, 5.0, 1.0, false);
        let first = site.draw(8.0, 60.0, false);
        let second = site.draw(8.0, 60.0, false);
        approx(first + second, 500.0 / 60.0, 0.01);
    }

    #[test]
    fn current_limit_can_bind_before_power_limit() {
        let mut site = EnergySite::new(EnergySiteConfig {
            station: StationId::new(1),
            pv_nameplate_kw: 0.0,
            storage_capacity_kwh: 500.0,
            storage_max_charge_kw: 500.0,
            storage_max_discharge_kw: 1000.0,
            storage_initial_soc: 1.0,
            grid_import_kw: 0.0,
            grid_export_kw: 0.0,
            storage_module_kwh: 500.0,
            charger_max_kw: 500.0,
            charger_max_current_a: 825.0,
            charger_bus_voltage_v: 500.0,
            charger_efficiency: 1.0,
            charger_contact_count: 2,
        });
        site.tick_pv(0, 60.0, 5.0, 1.0, false);
        let delivered = site.draw(20.0, 60.0, false);
        approx(delivered, 412.5 / 60.0, 0.01);
    }
}
