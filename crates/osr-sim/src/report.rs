//! End-of-run summary printer.

use crate::sim::{EventKind, RuntimeConfig, ScenarioConfig, SimResult};

fn max_usize(a: usize, b: usize) -> usize {
    if a > b {
        a
    } else {
        b
    }
}

pub fn print_summary(_config: &ScenarioConfig, _runtime: &RuntimeConfig, r: &SimResult) {
    println!("\n────────── Summary ──────────");
    println!("Scenario           : {}", r.scenario_name);
    println!("Sim duration       : {} s", r.sim_duration_s);
    println!("Total train-km     : {:>10.2}", r.total_train_km);
    println!(
        "Energy consumed    : {:>10.2} kWh",
        r.total_energy_consumed_kwh
    );
    println!(
        "Energy charged     : {:>10.2} kWh",
        r.total_energy_charged_kwh
    );
    if r.total_roof_pv_charged_kwh > 0.0 {
        println!(
            "  of which roof PV : {:>10.2} kWh",
            r.total_roof_pv_charged_kwh
        );
    }
    println!(
        "Fleet battery net  : {:>10.2} kWh",
        r.total_energy_charged_kwh - r.total_energy_consumed_kwh
    );
    println!(
        "In-service held    : {:>10} train-s ({:.1} train-min)",
        r.in_service_held_s,
        r.in_service_held_s as f64 / 60.0
    );
    println!(
        "Out-of-service idle: {:>10} train-s ({:.1} train-min)",
        r.out_of_service_held_s,
        r.out_of_service_held_s as f64 / 60.0
    );
    if r.energy_adaptive_dispatches > 0 {
        println!(
            "Energy-adapted svc : {:>10} departures (+{:.1} headway-h, max {} min)",
            r.energy_adaptive_dispatches,
            r.energy_adaptive_headway_added_s as f64 / 3600.0,
            r.maximum_effective_headway_s / 60,
        );
    }
    println!();
    if !r.per_line_km.is_empty() {
        println!("\nPer-line km:");
        for (name, km) in &r.per_line_km {
            println!("  {name:<24}  {km:>8.2} km");
        }
    }

    println!("\nPer-train SoC (final, min):");
    for (id, line, soc, min_soc) in &r.per_train_final_soc {
        println!("  {id:<5}  {line:<20}  final={soc:.2}   min={min_soc:.2}");
    }

    // Event tallies by kind. Compact acceptance runs retain the aggregate
    // map while omitting their detailed trace.
    let mut counts = r.event_counts.clone();
    if counts.is_empty() {
        for e in &r.events {
            let key = match &e.kind {
                EventKind::Dispatched => "Dispatched",
                EventKind::ArriveStation { .. } => "ArriveStation",
                EventKind::DepartStation => "DepartStation",
                EventKind::ChargingTick { .. } => "ChargingTick",
                EventKind::Turnaround => "Turnaround",
                EventKind::DepotServiceStart { .. } => "DepotServiceStart",
                EventKind::DepotServiceComplete => "DepotServiceComplete",
                EventKind::SocWarning { .. } => "SocWarning",
            };
            *counts.entry(key.to_owned()).or_insert(0) += 1;
        }
    }
    println!("\nEvent counts:");
    for (k, v) in &counts {
        println!("  {k:<14}  {v}");
    }

    if !r.energy_sites.is_empty() {
        println!("\n────────── Energy system ──────────");
        println!(
            "PV generated       : {:>10.2} kWh",
            r.total_pv_generated_kwh
        );
        println!(
            "To train charging  : {:>10.2} kWh",
            r.total_delivered_to_trains_kwh
        );
        println!(
            "Grid imported      : {:>10.2} kWh",
            r.total_grid_imported_kwh
        );
        println!(
            "Grid exported      : {:>10.2} kWh",
            r.total_grid_exported_kwh
        );
        println!("Curtailed          : {:>10.2} kWh", r.total_curtailed_kwh);
        let pv_used = r.total_pv_generated_kwh - r.total_grid_exported_kwh - r.total_curtailed_kwh;
        if r.total_pv_generated_kwh > 0.0 {
            let self_consumption = pv_used / r.total_pv_generated_kwh * 100.0;
            println!("PV self-consumed   : {pv_used:>10.2} kWh ({self_consumption:.1}%)");
        }

        // Top 8 sites by any kind of activity, so output stays readable for
        // larger networks.
        let mut sorted = r.energy_sites.clone();
        sorted.sort_by(|a, b| {
            let score_a = a.pv_generated_kwh
                + a.delivered_to_trains_kwh
                + a.grid_imported_kwh
                + a.grid_exported_kwh;
            let score_b = b.pv_generated_kwh
                + b.delivered_to_trains_kwh
                + b.grid_imported_kwh
                + b.grid_exported_kwh;
            score_b
                .partial_cmp(&score_a)
                .unwrap_or(std::cmp::Ordering::Equal)
        });
        let shown = sorted.iter().take(8);
        let name_w = max_usize(
            10,
            sorted
                .iter()
                .take(8)
                .map(|s| s.station_name.len())
                .max()
                .unwrap_or(0),
        );
        println!("\nPer-site (top by activity):");
        println!(
            "  {:<width$}  {:>7}  {:>8}  {:>8}  {:>8}  {:>6}",
            "station",
            "PV kWh",
            "→trains",
            "grid←",
            "grid→",
            "SoC",
            width = name_w
        );
        for s in shown {
            println!(
                "  {:<width$}  {:>7.1}  {:>8.1}  {:>8.1}  {:>8.1}  {:>6.2}",
                s.station_name,
                s.pv_generated_kwh,
                s.delivered_to_trains_kwh,
                s.grid_imported_kwh,
                s.grid_exported_kwh,
                s.storage_final_soc,
                width = name_w
            );
        }
    }

    if !r.faults_fired.is_empty() {
        println!("\n────────── Faults ──────────");
        for f in &r.faults_fired {
            let start_h = f.started_at_sim_s / 3600;
            let start_m = (f.started_at_sim_s / 60) % 60;
            let dur_m = f.duration_s / 60;
            println!(
                "  {:<28}  from T+{start_h:02}:{start_m:02}  for {dur_m} min   {}",
                f.name, f.description,
            );
        }
    }

    if r.onboard.ticks_evaluated > 0 {
        println!("\n────────── Onboard shadow stack (SIL-4 monitors) ──────────");
        println!("Ticks evaluated    : {:>10}", r.onboard.ticks_evaluated);
        println!(
            "Release / service / emergency : {} / {} / {}",
            r.onboard.total_release_ticks,
            r.onboard.total_service_ticks,
            r.onboard.total_emergency_ticks,
        );
        println!(
            "Fire / derail trips: {} / {}",
            r.onboard.total_fire_trip_ticks, r.onboard.total_derailment_trip_ticks,
        );
        println!(
            "Obstacle-detect verdicts (RFC 0015): RestrictedSpeed={}  CrawlOnly={}  EmergencyBrake={}",
            r.onboard.total_obstacle_restricted_ticks,
            r.onboard.total_obstacle_crawl_ticks,
            r.onboard.total_obstacle_emergency_ticks,
        );
    }

    if r.embedded.controller_ticks > 0 {
        println!("\n────────── Embedded application stack ──────────");
        println!("TCMS ticks         : {:>10}", r.embedded.controller_ticks);
        println!(
            "Ready / trip ticks : {} / {}",
            r.embedded.tcms_ready_to_move_ticks, r.embedded.tcms_trip_ticks
        );
        println!(
            "TCMS movement holds: {} departure / {} travel",
            r.embedded.tcms_departure_inhibit_ticks, r.embedded.tcms_travel_hold_ticks
        );
        println!(
            "Event records      : {} written / {} retained / {} overwritten",
            r.embedded.event_records_written,
            r.embedded.event_records_retained,
            r.embedded.event_records_dropped
        );
        println!(
            "CBM samples/alerts : {} / {} watch / {} service",
            r.embedded.cbm_samples, r.embedded.cbm_watch_flags, r.embedded.cbm_service_flags
        );
        println!(
            "T2G tx/channels    : {} tx · {} primary · {} backup · {} offline · queue max {} · {} dropped",
            r.embedded.t2g_transmissions,
            r.embedded.t2g_primary_ticks,
            r.embedded.t2g_backup_ticks,
            r.embedded.t2g_offline_ticks,
            r.embedded.maximum_t2g_queue_depth,
            r.embedded.t2g_payloads_dropped
        );
    }

    if r.time_sync.controller_ticks > 0 {
        println!("\n────────── Shared time synchronization ──────────");
        println!("PTP ticks          : {:>10}", r.time_sync.controller_ticks);
        println!(
            "Lock state/ticks   : {} / {} locked · {} acquiring",
            r.time_sync.final_lock_state, r.time_sync.locked_ticks, r.time_sync.acquiring_ticks
        );
        println!(
            "Offset / path max  : {} ns / {} ns",
            r.time_sync.maximum_absolute_offset_ns, r.time_sync.maximum_path_delay_ns
        );
    }

    if r.infrastructure_systems.stations.controller_ticks > 0 {
        let stations = &r.infrastructure_systems.stations;
        let wayside = &r.infrastructure_systems.wayside;
        println!("\n────────── Station + wayside application stack ──────────");
        println!("Station ticks      : {:>10}", stations.controller_ticks);
        println!(
            "PSD open/obstructed: {} / {} ticks ({} panel evaluations)",
            stations.psd_open_ticks, stations.psd_obstruction_ticks, stations.psd_panel_evaluations
        );
        println!(
            "PIS entries / SCADA degraded: {} / {} ticks",
            stations.pis_board_entries, stations.scada_degraded_ticks
        );
        println!(
            "Wayside verdicts   : {} clear / {} unknown / {} present · {} transitions",
            wayside.clear_ticks,
            wayside.unknown_ticks,
            wayside.present_ticks,
            wayside.verdict_transitions
        );
    }

    if r.habd_systems.detector_count > 0 {
        println!("\n────────── Physical hot-axle detection ──────────");
        println!(
            "HABD sites/tracks  : {} / {}",
            r.habd_systems.detector_count, r.habd_systems.track_position_count
        );
        println!(
            "Passages N/W/T     : {} / {} / {}",
            r.habd_systems.nominal_passages,
            r.habd_systems.warning_passages,
            r.habd_systems.trip_passages
        );
        println!(
            "Restrictions I/C/A : {} / {} / {} · {} ticks · max {:.1} km/h",
            r.habd_systems.speed_restrictions_issued,
            r.habd_systems.speed_restrictions_cleared,
            r.habd_systems.active_speed_restrictions.len(),
            r.habd_systems.speed_restriction_ticks,
            r.habd_systems.maximum_restricted_speed_mmps as f32 * 0.0036
        );
        println!(
            "Stops/holds/active : {} / {} / {}",
            r.habd_systems.stop_orders_issued,
            r.habd_systems.stop_hold_ticks,
            r.habd_systems.active_stop_orders.len()
        );
        println!(
            "Inspection resets  : {} accepted / {} rejected",
            r.habd_systems.reset_actions_accepted, r.habd_systems.reset_actions_rejected
        );
    }

    if r.backend_systems.cbm_samples_received > 0 {
        let backend = &r.backend_systems;
        println!("\n────────── Depot data services ──────────");
        println!(
            "CBM rx / tracked   : {} payloads / {} components",
            backend.cbm_samples_received, backend.cbm_components_tracked
        );
        println!(
            "Historian          : {} samples across {} metrics",
            backend.historian_samples_ingested, backend.historian_metrics_retained
        );
        println!(
            "Analytics          : {} metrics / {} retained samples evaluated",
            backend.analytics_metrics_evaluated, backend.analytics_samples_evaluated
        );
        println!(
            "Work orders        : {} routine / {} urgent",
            backend.routine_work_orders, backend.urgent_work_orders
        );
    }

    if r.ma_check.checks_run > 0 {
        println!("\n────────── MA computer integration (osr-interlocking) ──────────");
        println!("Sweeps run         : {:>10}", r.ma_check.checks_run);
        println!(
            "MAs computed       : {:>10}  (fleet × sweeps)",
            r.ma_check.total_mas_computed
        );
        println!(
            "Fail-restrictive   : {:>10}  (train position unknown at sweep time)",
            r.ma_check.fail_restrictive_mas
        );
    }

    if !r.invariant_violations.is_empty() {
        println!("\n⚠ Invariant violations: {}", r.invariant_violations.len());
        for v in &r.invariant_violations {
            println!(
                "  [{}] {}",
                crate::sim::fmt_clock(v.sim_time_s),
                v.description
            );
        }
    } else {
        println!("\nInvariant violations: 0  ✓");
    }
}
