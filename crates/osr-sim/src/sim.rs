//! Time-stepped simulation engine.
//!
//! Service-level model (v1):
//! - Trains teleport between adjacent stations over a computed travel time
//!   derived from section length and a constant cruise speed.
//! - Energy is debited on arrival (equal to section_length_km × kWh_per_km)
//!   and credited during dwells at charging-equipped stations.
//! - An occupancy map enforces the "no two trains in the same section"
//!   invariant; violations are logged.
//! - Lines can be linear or ring. Linear lines flip heading at terminals;
//!   rings wrap around.
//!
//! Later iterations will add kinematic integration, proper interlocking,
//! trackside storage + PV, and the time-of-day service plan.

use osr_core::topology::OccupancyMap;
use osr_core::{ConsistDescriptor, Line, Network, SectionId, StationId, TrainId};
use serde::{Deserialize, Serialize};

use crate::energy::{EnergySiteConfig, EnergySiteSummary, EnergySystem};
use crate::fault::{Fault, FaultEngine, FaultLogEntry};
use crate::ma_check::{self, MaCheckSummary, SimulatedLog};
use crate::schedule::{DispatchThrottle, LineSchedule};
use crate::train::{Heading, Train, TrainPhase};

// --------------------------------------------------------------------------
// Configuration
// --------------------------------------------------------------------------

#[derive(Clone, Debug)]
pub struct ScenarioConfig {
    pub name: String,
    pub network: Network,
    /// Per-line fleet configuration. One entry per line.
    pub fleets: Vec<LineFleet>,
    /// Shared reference consist used by every trainset in every line.
    pub consist: ConsistDescriptor,
    pub climate: ClimateModel,
    /// Sim-clock start time in seconds since midnight. Used for status display
    /// and dispatch-gate timing.
    pub start_time_s_after_midnight: u32,
    /// Trackside energy sites (PV + storage + grid tie). Optional; scenarios
    /// without any sites run in "unlimited free charging" mode.
    pub energy_sites: Vec<EnergySiteConfig>,
    /// Declared fault events (dust, grid outages, charging pad outages).
    /// Optional.
    pub faults: Vec<Fault>,
}

#[derive(Clone, Debug)]
pub struct LineFleet {
    pub line_index: usize,
    /// Stations from which trains dispatch, paired with their initial heading.
    /// Trains are distributed round-robin across this list.
    pub dispatch_points: Vec<(StationId, Heading)>,
    pub trainset_count: u32,
    /// Time-of-day schedule. Headway varies by window per RFC 0003 §4.1.
    pub schedule: LineSchedule,
}

#[derive(Clone, Debug)]
pub struct ClimateModel {
    pub ambient_c: f32,
    pub peak_sun_hours: f32,
    pub hvac_uplift_frac: f32,
}

#[derive(Clone, Debug)]
pub struct RuntimeConfig {
    pub duration_s: u32,
    pub time_step_s: u32,
    pub status_every_s: u32,
    /// Optional path to write per-train CSV snapshots. When set, the
    /// simulator opens the file and writes one row per train per
    /// `csv_every_s` seconds of sim time.
    pub csv_out: Option<std::path::PathBuf>,
    /// Interval between CSV rows, in sim seconds. Defaults to 60.
    pub csv_every_s: u32,
    /// Interval between MA consistency checks, in sim seconds. 0 disables
    /// the MA computer integration entirely. Defaults to 30.
    pub ma_check_every_s: u32,
}

impl Default for RuntimeConfig {
    fn default() -> Self {
        Self {
            duration_s: 3600,
            time_step_s: 1,
            status_every_s: 60,
            csv_out: None,
            csv_every_s: 60,
            ma_check_every_s: 30,
        }
    }
}

// --------------------------------------------------------------------------
// Events and result
// --------------------------------------------------------------------------

#[derive(Clone, Debug, Serialize, Deserialize)]
pub enum EventKind {
    Dispatched,
    ArriveStation { soc: f32 },
    DepartStation,
    ChargingTick { power_kw: f32, energy_added_kwh: f32 },
    Turnaround,
    SocWarning { soc: f32 },
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Event {
    pub sim_time_s: u32,
    pub train: TrainId,
    pub line: String,
    pub station: Option<StationId>,
    pub station_name: Option<String>,
    pub kind: EventKind,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct InvariantViolation {
    pub sim_time_s: u32,
    pub description: String,
}

#[derive(Clone, Debug, Default, Serialize, Deserialize)]
pub struct SimResult {
    pub scenario_name: String,
    pub sim_duration_s: u32,
    pub total_train_km: f64,
    pub total_energy_consumed_kwh: f64,
    pub total_energy_charged_kwh: f64,
    /// Train-seconds held at dispatch points during service hours (fleet
    /// oversized for the headway). High values mean off-peak overstaffing.
    pub in_service_held_s: u64,
    /// Train-seconds spent parked at dispatch points outside service hours
    /// (overnight idle). Expected to be roughly `(fleet_size × night_hours)`.
    pub out_of_service_held_s: u64,
    pub per_train_final_soc: Vec<(String, String, f32, f32)>, // (train_id, line, final_soc, min_soc)
    pub per_line_km: Vec<(String, f64)>,
    pub events: Vec<Event>,
    pub invariant_violations: Vec<InvariantViolation>,
    /// Trackside energy system summary (empty if scenario has no sites).
    #[serde(default)]
    pub energy_sites: Vec<EnergySiteSummary>,
    #[serde(default)]
    pub total_pv_generated_kwh: f64,
    #[serde(default)]
    pub total_grid_imported_kwh: f64,
    #[serde(default)]
    pub total_grid_exported_kwh: f64,
    #[serde(default)]
    pub total_curtailed_kwh: f64,
    #[serde(default)]
    pub total_delivered_to_trains_kwh: f64,
    #[serde(default)]
    pub faults_fired: Vec<FaultSummary>,
    /// Summary of the osr-interlocking MA-computer integration
    /// (checks run, MAs computed, any consistency violations).
    #[serde(default = "default_ma_summary")]
    pub ma_check: MaCheckSummary,
}

fn default_ma_summary() -> MaCheckSummary {
    MaCheckSummary {
        checks_run: 0,
        total_mas_computed: 0,
        fail_restrictive_mas: 0,
        violations: Vec::new(),
    }
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct FaultSummary {
    pub name: String,
    pub started_at_sim_s: u32,
    pub duration_s: u32,
    pub description: String,
}

impl FaultSummary {
    fn from_log(entry: &FaultLogEntry) -> Self {
        Self {
            name: entry.name.clone(),
            started_at_sim_s: entry.started_at_sim_s,
            duration_s: entry.duration_s,
            description: entry.kind_description.clone(),
        }
    }
}

// --------------------------------------------------------------------------
// Engine
// --------------------------------------------------------------------------

const SOC_WARNING_THRESHOLD: f32 = 0.30;

/// Compute section travel time from rest-to-rest using a simple trapezoidal
/// velocity profile: accelerate at `a`, cruise at `v_max`, decelerate at `d`.
/// Falls back to a triangular profile when the section is too short to
/// reach `v_max`. All units in SI (m, m/s, m/s²).
pub fn kinematic_travel_time(length_m: f32, v_max: f32, a: f32, d: f32) -> f32 {
    let accel_dist = (v_max * v_max) / (2.0 * a);
    let decel_dist = (v_max * v_max) / (2.0 * d);

    if accel_dist + decel_dist >= length_m {
        // Triangular profile: peak velocity below v_max.
        // Peak v such that v²/(2a) + v²/(2d) = length → v = sqrt(2·L·a·d/(a+d))
        let v_peak = ((2.0 * length_m * a * d) / (a + d)).sqrt();
        v_peak / a + v_peak / d
    } else {
        let cruise_dist = length_m - accel_dist - decel_dist;
        let cruise_time = cruise_dist / v_max;
        v_max / a + cruise_time + v_max / d
    }
}

pub fn run(config: &ScenarioConfig, runtime: &RuntimeConfig) -> SimResult {
    use std::io::Write;

    let mut trains = init_fleet(config);
    let mut occupancy = OccupancyMap::default();
    let mut throttle = DispatchThrottle::new();
    let mut energy = EnergySystem::new(
        config.energy_sites.clone(),
        config.climate.peak_sun_hours,
    );
    let mut faults = FaultEngine::new(config.faults.clone());

    // MA-computer integration (RFC 0004 §M5). The sim maintains a log of
    // Entry objects as trains move; every `ma_check_every_s` sim seconds
    // we compute each train's MA and verify consistency.
    let mut ma_log = SimulatedLog::new();
    let mut ma_summary = default_ma_summary();
    let ma_check_interval = runtime.ma_check_every_s;
    let mut next_ma_check = if ma_check_interval > 0 { 0 } else { u32::MAX };

    // Optional CSV trace.
    let mut csv_writer: Option<std::io::BufWriter<std::fs::File>> = None;
    if let Some(path) = &runtime.csv_out {
        match std::fs::File::create(path) {
            Ok(f) => {
                let mut w = std::io::BufWriter::new(f);
                let _ = writeln!(
                    w,
                    "sim_time_s,clock_tod_hms,train_id,line,phase,station,soc,odometer_km,energy_consumed_kwh,energy_charged_kwh"
                );
                csv_writer = Some(w);
            }
            Err(e) => {
                eprintln!(
                    "warning: could not open CSV {}: {}; continuing without CSV",
                    path.display(),
                    e
                );
            }
        }
    }
    let csv_every = runtime.csv_every_s.max(1);
    let mut next_csv = if csv_writer.is_some() { 0 } else { u32::MAX };
    let mut events: Vec<Event> = Vec::new();
    let mut violations: Vec<InvariantViolation> = Vec::new();

    // Register throttle points from each line's dispatch configuration.
    for fleet in &config.fleets {
        for (station, heading) in &fleet.dispatch_points {
            throttle.register(
                (fleet.line_index, *station, *heading),
                fleet.schedule.service_start_s,
            );
        }
    }

    let dt = runtime.time_step_s as f32;
    let status_every = runtime.status_every_s;

    print_header(config, runtime, &trains);

    let mut t: u32 = 0;
    let mut next_status = if status_every > 0 { status_every } else { u32::MAX };
    let mut prev_day: u32 = 0;

    while t < runtime.duration_s {
        let clock_absolute = t + config.start_time_s_after_midnight;
        let day = clock_absolute / 86400;
        let clock_tod = clock_absolute % 86400;

        // Midnight crossing: re-arm all throttle points for the new day.
        if day > prev_day {
            let keys: Vec<_> = throttle.registered_keys().collect();
            for key in keys {
                let fleet = fleet_for_line(&config.fleets, key.0);
                throttle.reset(key, fleet.schedule.service_start_s);
            }
            prev_day = day;
        }

        // Update fault state for this tick.
        faults.tick(t);

        // PV generation, battery storage, grid export/curtail (time-of-day).
        energy.tick_pv(clock_tod, dt, &faults);

        for idx in 0..trains.len() {
            step_train(
                idx,
                &mut trains,
                &config.network,
                &config.climate,
                &config.fleets,
                clock_tod,
                &mut occupancy,
                &mut throttle,
                &mut energy,
                &faults,
                dt,
                t,
                &mut events,
                &mut violations,
            );
        }

        if status_every > 0 && t >= next_status {
            print_status_line(t, &trains, &config.network, config.start_time_s_after_midnight);
            next_status = t.saturating_add(status_every);
        }

        if let Some(w) = csv_writer.as_mut() {
            if t >= next_csv {
                write_csv_snapshot(w, t, clock_tod, &trains, &config.network);
                next_csv = t.saturating_add(csv_every);
            }
        }

        if ma_check_interval > 0 && t >= next_ma_check {
            // Emit position reports for all trains before the check, so the
            // MA computer sees the current state. Registration happens
            // automatically on first emission.
            for tr in &trains {
                if let Some(trackref) = ma_check::trackref_for(tr, &config.network) {
                    ma_log.ensure_registered(tr, trackref, t);
                    ma_log.emit_position(tr, trackref, None, t);
                }
            }
            ma_check::run_check(
                &trains,
                &ma_log,
                &config.network,
                &occupancy,
                t,
                &mut ma_summary,
            );
            next_ma_check = t.saturating_add(ma_check_interval);
        }

        t = t.saturating_add(runtime.time_step_s);
    }

    if let Some(mut w) = csv_writer.take() {
        let _ = std::io::Write::flush(&mut w);
        if let Some(path) = &runtime.csv_out {
            println!("CSV trace written to {}", path.display());
        }
    }

    if status_every > 0 {
        print_status_line(
            runtime.duration_s,
            &trains,
            &config.network,
            config.start_time_s_after_midnight,
        );
    }

    // Aggregate per-line km.
    let mut per_line_km: Vec<(String, f64)> = config
        .network
        .lines
        .iter()
        .map(|l| (l.name.clone(), 0.0))
        .collect();
    for tr in &trains {
        per_line_km[tr.line_index].1 += tr.odometer_km;
    }

    // Build per-site summaries.
    let energy_sites: Vec<EnergySiteSummary> = energy
        .sites
        .values()
        .map(|site| {
            let name = config.network.station(site.config.station).name.clone();
            site.summary(name)
        })
        .collect();

    SimResult {
        scenario_name: config.name.clone(),
        sim_duration_s: runtime.duration_s,
        total_train_km: trains.iter().map(|t| t.odometer_km).sum(),
        total_energy_consumed_kwh: trains.iter().map(|t| t.energy_consumed_kwh).sum(),
        total_energy_charged_kwh: trains.iter().map(|t| t.energy_charged_kwh).sum(),
        in_service_held_s: throttle.in_service_held_s,
        out_of_service_held_s: throttle.out_of_service_held_s,
        per_train_final_soc: trains
            .iter()
            .map(|t| {
                let line_name = config.network.lines[t.line_index].name.clone();
                (t.id.to_string(), line_name, t.soc, t.min_soc_seen)
            })
            .collect(),
        per_line_km,
        events,
        invariant_violations: violations,
        total_pv_generated_kwh: energy.total_pv_generated_kwh(),
        total_grid_imported_kwh: energy.total_grid_imported_kwh(),
        total_grid_exported_kwh: energy.total_grid_exported_kwh(),
        total_curtailed_kwh: energy.total_curtailed_kwh(),
        total_delivered_to_trains_kwh: energy.total_delivered_to_trains_kwh(),
        energy_sites,
        faults_fired: faults
            .fault_log
            .iter()
            .map(FaultSummary::from_log)
            .collect(),
        ma_check: ma_summary,
    }
}

fn print_header(config: &ScenarioConfig, runtime: &RuntimeConfig, trains: &[Train]) {
    println!("OpenSourceRail sim — scenario \"{}\"", config.name);
    println!("Network:");
    for (i, line) in config.network.lines.iter().enumerate() {
        let line_km: f64 = line
            .forward_sections
            .iter()
            .map(|sid| config.network.section(*sid).length_km())
            .sum();
        let kind = if line.is_ring { "ring" } else { "linear" };
        let train_count = trains.iter().filter(|t| t.line_index == i).count();
        let fleet_opt = config.fleets.iter().find(|f| f.line_index == i);
        if let Some(fleet) = fleet_opt {
            println!(
                "  {} ({}, {:.1} km, {} stations, {} trainsets) — headways {} over {}–{}",
                line.name,
                kind,
                line_km,
                line.stations.len(),
                train_count,
                fleet.schedule.headway_summary(),
                fmt_time_of_day(fleet.schedule.service_start_s),
                fmt_time_of_day(fleet.schedule.service_end_s),
            );
        } else {
            println!(
                "  {} ({}, {:.1} km, {} stations, no fleet assigned)",
                line.name,
                kind,
                line_km,
                line.stations.len(),
            );
        }
    }
    println!(
        "Climate: ambient {:.0}°C, PSH {:.1} h, HVAC uplift {:+.0}%",
        config.climate.ambient_c,
        config.climate.peak_sun_hours,
        config.climate.hvac_uplift_frac * 100.0
    );
    println!(
        "Rolling stock: {}-car consist, {} kWh per trainset",
        trains[0].consist.car_count,
        trains[0].consist.battery_capacity_wh / 1000
    );
    println!(
        "Running {} s ({}) at {}s step, start {}…\n",
        runtime.duration_s,
        fmt_duration(runtime.duration_s),
        runtime.time_step_s,
        fmt_time_of_day(config.start_time_s_after_midnight)
    );
}

fn init_fleet(config: &ScenarioConfig) -> Vec<Train> {
    let mut trains = Vec::new();
    let mut next_train_num: u64 = 1;

    for fleet in &config.fleets {
        assert!(
            !fleet.dispatch_points.is_empty(),
            "fleet for line {} has no dispatch points",
            fleet.line_index
        );
        for i in 0..fleet.trainset_count {
            let dp_idx = (i as usize) % fleet.dispatch_points.len();
            let (start_station, heading) = fleet.dispatch_points[dp_idx];

            trains.push(Train {
                id: TrainId::new(next_train_num),
                line_index: fleet.line_index,
                consist: config.consist.clone(),
                heading,
                phase: TrainPhase::AwaitingDispatch { station: start_station },
                soc: 0.95,
                odometer_km: 0.0,
                energy_consumed_kwh: 0.0,
                energy_charged_kwh: 0.0,
                min_soc_seen: 0.95,
            });
            next_train_num += 1;
        }
    }

    trains
}

fn fleet_for_line(fleets: &[LineFleet], line_index: usize) -> &LineFleet {
    fleets
        .iter()
        .find(|f| f.line_index == line_index)
        .unwrap_or_else(|| panic!("no fleet configured for line {line_index}"))
}

#[allow(clippy::too_many_arguments)]
fn step_train(
    idx: usize,
    trains: &mut [Train],
    network: &Network,
    climate: &ClimateModel,
    fleets: &[LineFleet],
    clock_tod: u32,
    occupancy: &mut OccupancyMap,
    throttle: &mut DispatchThrottle,
    energy: &mut EnergySystem,
    faults: &FaultEngine,
    dt: f32,
    t: u32,
    events: &mut Vec<Event>,
    violations: &mut Vec<InvariantViolation>,
) {
    let phase = trains[idx].phase.clone();
    let clock = clock_tod;

    match phase {
        TrainPhase::AwaitingDispatch { station } => {
            let line_idx = trains[idx].line_index;
            let heading = trains[idx].heading;
            let key = (line_idx, station, heading);
            let fleet = fleet_for_line(fleets, line_idx);

            match fleet.schedule.headway_at(clock) {
                Some(hw) if throttle.can_dispatch(&key, clock) => {
                    throttle.mark_dispatched(&key, clock, hw);
                    enter_first_section(idx, trains, network, t, occupancy, events, violations);
                }
                Some(_) => throttle.record_in_service_held(dt),
                None => throttle.record_out_of_service_held(dt),
            }
        }
        TrainPhase::Dwelling {
            station,
            mut remaining_s,
            mut energy_added_kwh,
        } => {
            let s = network.station(station);
            let pad_up = !faults.pad_disabled_at(station);
            if pad_up && s.charging_power_kw > 0 && trains[idx].soc < 1.0 {
                let pad_rate_kwh = (s.charging_power_kw as f32 / 3600.0) * dt;
                let headroom_kwh = (1.0 - trains[idx].soc)
                    * trains[idx].battery_capacity_kwh();
                let requested = pad_rate_kwh.min(headroom_kwh);
                if requested > 0.0 {
                    let delivered = energy.draw_at_station(station, requested, dt, faults);
                    let applied = trains[idx].apply_energy_kwh(delivered);
                    trains[idx].energy_charged_kwh += f64::from(applied);
                    energy_added_kwh += applied;
                }
            }
            remaining_s -= dt;

            if remaining_s > 0.0 {
                trains[idx].phase = TrainPhase::Dwelling {
                    station,
                    remaining_s,
                    energy_added_kwh,
                };
                return;
            }

            // Dwell expired. Check if this station + departure heading is a
            // throttle point; if so, honor the schedule.
            let line_idx = trains[idx].line_index;
            let line = &network.lines[line_idx];
            let terminal_flip = s.is_terminal && !line.is_ring;
            let departure_heading = if terminal_flip {
                trains[idx].heading.flip()
            } else {
                trains[idx].heading
            };
            let key = (line_idx, station, departure_heading);

            if throttle.is_throttle_point(&key) {
                let fleet = fleet_for_line(fleets, line_idx);
                let in_service = fleet.schedule.headway_at(clock);
                match in_service {
                    Some(hw) if throttle.can_dispatch(&key, clock) => {
                        throttle.mark_dispatched(&key, clock, hw);
                        // Fall through to departure logic below.
                    }
                    _ => {
                        trains[idx].phase = TrainPhase::Dwelling {
                            station,
                            remaining_s: dt,
                            energy_added_kwh,
                        };
                        if in_service.is_some() {
                            throttle.record_in_service_held(dt);
                        } else {
                            throttle.record_out_of_service_held(dt);
                        }
                        return;
                    }
                }
            }

            // Proceed with departure.
            if terminal_flip {
                trains[idx].heading = trains[idx].heading.flip();
                emit_event(
                    events,
                    Event {
                        sim_time_s: t,
                        train: trains[idx].id,
                        line: line.name.clone(),
                        station: Some(station),
                        station_name: Some(s.name.clone()),
                        kind: EventKind::Turnaround,
                    },
                );
            }
            if energy_added_kwh > 0.1 {
                emit_event(
                    events,
                    Event {
                        sim_time_s: t,
                        train: trains[idx].id,
                        line: line.name.clone(),
                        station: Some(station),
                        station_name: Some(s.name.clone()),
                        kind: EventKind::ChargingTick {
                            power_kw: s.charging_power_kw as f32,
                            energy_added_kwh,
                        },
                    },
                );
            }
            emit_event(
                events,
                Event {
                    sim_time_s: t,
                    train: trains[idx].id,
                    line: line.name.clone(),
                    station: Some(station),
                    station_name: Some(s.name.clone()),
                    kind: EventKind::DepartStation,
                },
            );
            enter_next_section(idx, trains, network, t, occupancy, events, violations);
        }
        TrainPhase::Traveling {
            section,
            from_station,
            to_station,
            total_travel_s,
            mut remaining_s,
        } => {
            remaining_s -= dt;
            if remaining_s <= 0.0 {
                let sec = network.section(section);
                let km = sec.length_km();
                let kwh_per_km = trains[idx].kwh_per_km(climate.hvac_uplift_frac);
                let consumed = kwh_per_km * km as f32;
                trains[idx].apply_energy_kwh(-consumed);
                trains[idx].energy_consumed_kwh += f64::from(consumed);
                trains[idx].odometer_km += km;

                occupancy.leave(section, trains[idx].id);

                let line = &network.lines[trains[idx].line_index];

                if trains[idx].soc < SOC_WARNING_THRESHOLD {
                    emit_event(
                        events,
                        Event {
                            sim_time_s: t,
                            train: trains[idx].id,
                            line: line.name.clone(),
                            station: Some(to_station),
                            station_name: Some(network.station(to_station).name.clone()),
                            kind: EventKind::SocWarning { soc: trains[idx].soc },
                        },
                    );
                }

                emit_event(
                    events,
                    Event {
                        sim_time_s: t,
                        train: trains[idx].id,
                        line: line.name.clone(),
                        station: Some(to_station),
                        station_name: Some(network.station(to_station).name.clone()),
                        kind: EventKind::ArriveStation { soc: trains[idx].soc },
                    },
                );

                let dst = network.station(to_station);
                trains[idx].phase = TrainPhase::Dwelling {
                    station: to_station,
                    remaining_s: dst.dwell_seconds as f32,
                    energy_added_kwh: 0.0,
                };

                let _ = (from_station, total_travel_s);
            } else {
                trains[idx].phase = TrainPhase::Traveling {
                    section,
                    from_station,
                    to_station,
                    total_travel_s,
                    remaining_s,
                };
            }
        }
    }
}

fn enter_first_section(
    idx: usize,
    trains: &mut [Train],
    network: &Network,
    t: u32,
    occupancy: &mut OccupancyMap,
    events: &mut Vec<Event>,
    violations: &mut Vec<InvariantViolation>,
) {
    let station = match trains[idx].phase {
        TrainPhase::AwaitingDispatch { station, .. } => station,
        _ => return,
    };
    let line_name = network.lines[trains[idx].line_index].name.clone();
    emit_event(
        events,
        Event {
            sim_time_s: t,
            train: trains[idx].id,
            line: line_name,
            station: Some(station),
            station_name: Some(network.station(station).name.clone()),
            kind: EventKind::Dispatched,
        },
    );
    enter_next_section(idx, trains, network, t, occupancy, events, violations);
}

fn enter_next_section(
    idx: usize,
    trains: &mut [Train],
    network: &Network,
    _t: u32,
    occupancy: &mut OccupancyMap,
    _events: &mut Vec<Event>,
    violations: &mut Vec<InvariantViolation>,
) {
    let line = &network.lines[trains[idx].line_index];
    let current_station = current_station(&trains[idx]);
    let next = next_station_for(&trains[idx], line, current_station);

    let Some((to_station, section_id)) = next else {
        // At a terminal on a non-ring line with no next station; stay here
        // until the dwell expires and heading flips. (This branch shouldn't
        // occur because terminal dwells flip heading before we call here.)
        trains[idx].phase = TrainPhase::Dwelling {
            station: current_station,
            remaining_s: network.station(current_station).dwell_seconds as f32,
            energy_added_kwh: 0.0,
        };
        return;
    };

    // Section occupancy: if busy, hold at station for one step and retry.
    if let Some(blocker) = occupancy.occupant(section_id) {
        if blocker != trains[idx].id {
            trains[idx].phase = TrainPhase::Dwelling {
                station: current_station,
                remaining_s: 1.0,
                energy_added_kwh: 0.0,
            };
            return;
        }
    }

    if let Err(existing) = occupancy.enter(section_id, trains[idx].id) {
        violations.push(InvariantViolation {
            sim_time_s: _t,
            description: format!(
                "occupancy conflict: train {} entering {} already held by {}",
                trains[idx].id, section_id, existing
            ),
        });
    }

    let sec = network.section(section_id);
    let length_m = sec.length_mm as f32 / 1_000.0;
    let consist = &trains[idx].consist;
    let v_max = sec.max_speed_mps.min(consist.max_speed_mps);
    let a = consist.service_accel_mps2;
    let d = consist.service_decel_mps2();
    let travel_s = kinematic_travel_time(length_m, v_max, a, d)
        + consist.braking.reaction_time_ms as f32 / 1000.0;

    trains[idx].phase = TrainPhase::Traveling {
        section: section_id,
        from_station: current_station,
        to_station,
        total_travel_s: travel_s,
        remaining_s: travel_s,
    };
}

fn current_station(train: &Train) -> StationId {
    match &train.phase {
        TrainPhase::Dwelling { station, .. }
        | TrainPhase::AwaitingDispatch { station, .. } => *station,
        TrainPhase::Traveling { to_station, .. } => *to_station,
    }
}

fn next_station_for(
    train: &Train,
    line: &Line,
    current: StationId,
) -> Option<(StationId, SectionId)> {
    let idx = line.stations.iter().position(|s| *s == current)?;
    let n = line.stations.len();
    match train.heading {
        Heading::Forward => {
            let next_idx = idx + 1;
            if next_idx >= n {
                if line.is_ring {
                    // Wrap: stations[N-1] -> stations[0] uses forward_sections[N-1].
                    Some((line.stations[0], line.forward_sections[n - 1]))
                } else {
                    None
                }
            } else {
                Some((line.stations[next_idx], line.forward_sections[idx]))
            }
        }
        Heading::Reverse => {
            if idx == 0 {
                if line.is_ring {
                    // Wrap: stations[0] -> stations[N-1] uses reverse_sections[N-1].
                    Some((line.stations[n - 1], line.reverse_sections[n - 1]))
                } else {
                    None
                }
            } else {
                Some((line.stations[idx - 1], line.reverse_sections[idx - 1]))
            }
        }
    }
}

fn emit_event(buf: &mut Vec<Event>, ev: Event) {
    buf.push(ev);
}

// --------------------------------------------------------------------------
// Display helpers
// --------------------------------------------------------------------------

fn print_status_line(t: u32, trains: &[Train], network: &Network, start_of_day_s: u32) {
    let clock = fmt_sim_clock(t, start_of_day_s);
    // Group by line so the status line stays readable as fleets grow.
    let mut by_line: Vec<Vec<String>> = vec![Vec::new(); network.lines.len()];
    for tr in trains {
        by_line[tr.line_index].push(format!(
            "{}={}·{:.2}",
            tr.id,
            abbrev_phase(tr, network),
            tr.soc
        ));
    }
    print!("[{clock}]");
    for (i, cells) in by_line.iter().enumerate() {
        if cells.is_empty() {
            continue;
        }
        let line_abbrev = short_line_name(&network.lines[i].name);
        print!("  {}:{}", line_abbrev, cells.join(" "));
    }
    println!();
}

fn short_line_name(name: &str) -> String {
    // "Line 1 Nahrain" → "L1". "Line 2 Halqa" → "L2".
    name.split_whitespace()
        .take(2)
        .map(|w| {
            if w.eq_ignore_ascii_case("line") {
                "L".to_string()
            } else {
                w.to_string()
            }
        })
        .collect()
}

fn abbrev_phase(train: &Train, network: &Network) -> String {
    match &train.phase {
        TrainPhase::Dwelling { station, .. } => {
            format!("@{}", abbrev_name(&network.station(*station).name))
        }
        TrainPhase::Traveling { to_station, .. } => {
            format!("→{}", abbrev_name(&network.station(*to_station).name))
        }
        TrainPhase::AwaitingDispatch { station, .. } => {
            format!("…{}", abbrev_name(&network.station(*station).name))
        }
    }
}

fn abbrev_name(s: &str) -> String {
    s.split(|c: char| !c.is_alphanumeric())
        .filter(|w| !w.is_empty())
        .map(|w| w.chars().next().unwrap_or(' ').to_ascii_uppercase())
        .collect()
}

pub fn fmt_time_of_day(total_s: u32) -> String {
    let tod = total_s % 86400;
    let h = tod / 3600;
    let m = (tod / 60) % 60;
    let s = tod % 60;
    format!("{h:02}:{m:02}:{s:02}")
}

/// Format sim clock including a day prefix once the sim crosses midnight.
/// On day 1 (no wrap), prints "HH:MM:SS"; from day 2 onward prints
/// "D2 HH:MM:SS" etc.
pub fn fmt_sim_clock(t: u32, start_of_day_s: u32) -> String {
    let total = t + start_of_day_s;
    let day = total / 86400;
    let tod = total % 86400;
    let h = tod / 3600;
    let m = (tod / 60) % 60;
    let s = tod % 60;
    if day == 0 {
        format!("{h:02}:{m:02}:{s:02}")
    } else {
        format!("D{} {h:02}:{m:02}:{s:02}", day + 1)
    }
}

pub fn fmt_clock(t: u32) -> String {
    fmt_time_of_day(t)
}

fn write_csv_snapshot<W: std::io::Write>(
    w: &mut W,
    t: u32,
    clock_tod: u32,
    trains: &[Train],
    network: &Network,
) {
    let tod = fmt_time_of_day(clock_tod);
    for tr in trains {
        let line_name = network.lines[tr.line_index].name.clone();
        let (phase, station) = match &tr.phase {
            TrainPhase::Dwelling { station, .. } => (
                "dwelling",
                network.station(*station).name.clone(),
            ),
            TrainPhase::Traveling { to_station, .. } => (
                "traveling",
                format!("→{}", network.station(*to_station).name),
            ),
            TrainPhase::AwaitingDispatch { station } => (
                "awaiting",
                network.station(*station).name.clone(),
            ),
        };
        let _ = writeln!(
            w,
            "{t},{tod},{id},{line},{phase},\"{station}\",{soc:.4},{odo:.3},{consumed:.2},{charged:.2}",
            id = tr.id,
            line = csv_escape(&line_name),
            station = csv_escape(&station),
            soc = tr.soc,
            odo = tr.odometer_km,
            consumed = tr.energy_consumed_kwh,
            charged = tr.energy_charged_kwh,
        );
    }
}

fn csv_escape(s: &str) -> String {
    s.replace('"', "\"\"")
}

pub fn fmt_duration(s: u32) -> String {
    let days = s / 86400;
    let rem = s % 86400;
    let h = rem / 3600;
    let m = (rem / 60) % 60;
    let s = rem % 60;
    if days > 0 {
        format!("{days}d {h:02}h {m:02}m {s:02}s")
    } else {
        format!("{h}h {m:02}m {s:02}s")
    }
}

#[cfg(test)]
mod tests {
    use super::kinematic_travel_time;

    /// Approximate equality for time comparisons (±0.1 s).
    fn approx(a: f32, b: f32) {
        assert!((a - b).abs() < 0.1, "expected {b:.3}, got {a:.3}");
    }

    #[test]
    fn trapezoidal_long_section() {
        // 2000 m section, v_max = 20, a = d = 1.
        // Accel: 0→20 at 1 m/s² → 20s, covers 200m. Same for decel.
        // Cruise: 1600m at 20 m/s → 80s. Total 120s.
        approx(kinematic_travel_time(2000.0, 20.0, 1.0, 1.0), 120.0);
    }

    #[test]
    fn triangular_short_section() {
        // 200m section, v_max = 20, a = d = 1. Can't reach v_max.
        // v_peak = sqrt(2 * 200 * 1 * 1 / 2) = sqrt(200) ≈ 14.142
        // time = v_peak / 1 + v_peak / 1 ≈ 28.28 s
        approx(kinematic_travel_time(200.0, 20.0, 1.0, 1.0), 28.28);
    }

    #[test]
    fn asymmetric_accel_decel() {
        // Accel stronger than brake: slightly longer decel phase.
        let t_sym = kinematic_travel_time(1000.0, 20.0, 1.0, 1.0);
        let t_stronger_accel = kinematic_travel_time(1000.0, 20.0, 1.5, 1.0);
        // Stronger accel shortens the accel phase, so total time is lower.
        assert!(t_stronger_accel < t_sym);
    }

    #[test]
    fn boundary_section_exactly_reaches_vmax() {
        // length = accel_dist + decel_dist exactly.
        // v_max = 20, a = d = 1 → 200 + 200 = 400m section.
        // Trapezoidal with zero cruise: 20 + 0 + 20 = 40s.
        approx(kinematic_travel_time(400.0, 20.0, 1.0, 1.0), 40.0);
    }
}
