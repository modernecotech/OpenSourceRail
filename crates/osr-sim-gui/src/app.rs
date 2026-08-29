//! Shared sim-GUI application state + rendering — works under
//! native (eframe) and WASM (same crate, same `App`).
//!
//! The UI runs the sim synchronously at load time and builds a
//! [`SimTimeline`] (1 Hz per-train snapshot array) that the
//! playback loop animates against. This avoids the complexity of
//! stepping `osr-sim` on a worker thread and makes the WASM story
//! trivial: load → run → play back locally.

use std::collections::HashSet;

use eframe::egui::{
    self, CentralPanel, Color32, Context, FontId, Pos2, Rect, RichText, ScrollArea, SidePanel,
    Slider, TopBottomPanel,
};
use osr_core::TrainId;
use osr_gui_shared::{draw_network, NetworkLayout, Palette};
use osr_sim::scenario_file::{canonical_samawah_scenario, load_scenario_from_path};
use osr_sim::sim::{run, EventKind, RuntimeConfig, ScenarioConfig, SimResult};
use osr_sim::timeline::SimTimeline;

#[allow(missing_debug_implementations)] // ScenarioConfig carries nested non-Debug types.
pub struct SimApp {
    /// Loaded scenario.
    scenario: ScenarioConfig,
    scenario_label: String,
    /// Completed sim result + derived timeline.
    result: Option<SimResult>,
    timeline: Option<SimTimeline>,
    /// Playback state.
    playing: bool,
    playback_t_s: f32,
    speed: f32,
    /// Requested sim duration for the next run.
    duration_s: u32,
    /// UI bookkeeping.
    palette: Palette,
    selected_train: Option<TrainId>,
    event_filter: EventFilter,
}

#[derive(Clone, Copy, Debug, Default)]
pub struct RunStateSummary {
    pub duration_s: u32,
    pub events: usize,
    pub trains: usize,
    pub controller_ticks: u64,
    pub embedded_ticks: u64,
    pub t2g_transmissions: u64,
    pub station_ticks: u64,
    pub wayside_ticks: u64,
    pub backend_samples: u64,
    pub analytics_metrics: u32,
    pub ptp_ticks: u64,
    pub habd_passages: u64,
    pub habd_warnings: u64,
    pub habd_restriction_ticks: u64,
    pub balise_fixes: u64,
    pub balise_audit_findings: u64,
    pub fare_gate_grants: u64,
    pub fare_gate_denials: u64,
    pub occ_reports: u64,
    pub occ_active_holds: u32,
    pub energy_site_evaluations: u64,
    pub regen_arbiter_ticks: u64,
    pub proto_frames: u64,
    pub switch_ticks: u64,
    pub crossing_count: u32,
    pub selftest_passes: u32,
    pub tcms_movement_inhibits: u64,
    pub invariant_violations: usize,
}

#[derive(Default)]
struct EventFilter {
    show_dispatched: bool,
    show_arrive: bool,
    show_depart: bool,
    show_charging: bool,
    show_turnaround: bool,
    show_soc_warning: bool,
}

impl EventFilter {
    fn all_on() -> Self {
        Self {
            show_dispatched: true,
            show_arrive: true,
            show_depart: true,
            show_charging: false,
            show_turnaround: true,
            show_soc_warning: true,
        }
    }

    fn passes(&self, kind: &EventKind) -> bool {
        match kind {
            EventKind::Dispatched => self.show_dispatched,
            EventKind::ArriveStation { .. } => self.show_arrive,
            EventKind::DepartStation => self.show_depart,
            EventKind::ChargingTick { .. } => self.show_charging,
            EventKind::Turnaround => self.show_turnaround,
            EventKind::DepotServiceStart { .. } | EventKind::DepotServiceComplete => true,
            EventKind::SocWarning { .. } => self.show_soc_warning,
        }
    }
}

impl SimApp {
    pub fn new(scenario_path: Option<&str>, duration_s: u32) -> Self {
        Self::with_auto_run(scenario_path, duration_s, false)
    }

    /// Construct + optionally run the sim immediately at startup.
    /// Used for screenshots / demos so the default view is already
    /// populated.
    pub fn with_auto_run(scenario_path: Option<&str>, duration_s: u32, auto_run: bool) -> Self {
        let (scenario, label) = match scenario_path {
            Some(path) => match load_scenario_from_path(std::path::Path::new(path)) {
                Ok(s) => (s, path.to_string()),
                Err(e) => {
                    eprintln!("failed to load {path}: {e}");
                    (
                        canonical_samawah_scenario(),
                        "Samawah (bundled; fallback)".into(),
                    )
                }
            },
            // No explicit path given: prefer the on-disk
            // designs/west-asia/Iraq/Samawah/samawah.toml; fall back
            // to the bundled snapshot if it isn't there.
            None => _default_scenario(),
        };
        let mut app = Self {
            scenario,
            scenario_label: label,
            result: None,
            timeline: None,
            playing: false,
            playback_t_s: 0.0,
            speed: 10.0,
            duration_s,
            palette: Palette::dark(),
            selected_train: None,
            event_filter: EventFilter::all_on(),
        };
        if auto_run {
            app.run_sim();
            // Advance playback into the middle of the run so trains
            // are mid-journey and the event log has content.
            app.playback_t_s = (duration_s as f32 * 0.25).max(60.0);
            app.playing = false; // paused on a populated frame
        }
        app
    }

    /// Compact proof that the browser-visible run is populated and that the
    /// integrated vehicle controllers executed.
    pub fn run_state_summary(&self) -> RunStateSummary {
        self.result
            .as_ref()
            .map_or_else(RunStateSummary::default, |result| RunStateSummary {
                duration_s: result.sim_duration_s,
                events: result.events.len(),
                trains: result.per_train_final_soc.len(),
                controller_ticks: result.vehicle_systems.controller_ticks,
                embedded_ticks: result.embedded.controller_ticks,
                t2g_transmissions: result.embedded.t2g_transmissions,
                station_ticks: result.infrastructure_systems.stations.controller_ticks,
                wayside_ticks: result.infrastructure_systems.wayside.detector_ticks,
                backend_samples: result.backend_systems.cbm_samples_received,
                analytics_metrics: result.backend_systems.analytics_metrics_evaluated,
                ptp_ticks: result.time_sync.controller_ticks,
                habd_passages: result.habd_systems.passages_evaluated,
                habd_warnings: result.habd_systems.warning_passages,
                habd_restriction_ticks: result.habd_systems.speed_restriction_ticks,
                balise_fixes: result.balise_systems.fixes_applied,
                balise_audit_findings: result.balise_systems.missed_sightings
                    + result.balise_systems.position_mismatches
                    + result.balise_systems.unknown_sightings
                    + result.balise_systems.stale_findings,
                fare_gate_grants: result.fare_systems.gate_grants,
                fare_gate_denials: result.fare_systems.gate_denials,
                occ_reports: result.occ_systems.telemetry_reports_processed,
                occ_active_holds: result.occ_systems.final_active_dispatch_holds,
                energy_site_evaluations: result
                    .energy_sites
                    .iter()
                    .map(|site| site.controller_evaluations)
                    .sum(),
                regen_arbiter_ticks: result.onboard.total_regen_arbiter_ticks,
                proto_frames: result.proto_systems.frames_decoded,
                switch_ticks: result.wayside_asset_systems.switch_controller_ticks,
                crossing_count: result.wayside_asset_systems.crossing_count,
                selftest_passes: result.selftest_systems.checks_passed,
                tcms_movement_inhibits: result.embedded.tcms_departure_inhibit_ticks
                    + result.embedded.tcms_travel_hold_ticks,
                invariant_violations: result.invariant_violations.len(),
            })
    }

    fn run_sim(&mut self) {
        let runtime = RuntimeConfig {
            duration_s: self.duration_s,
            ..Default::default()
        };
        let result = run(&self.scenario, &runtime);
        let timeline = SimTimeline::from_result(&result, &self.scenario.network);
        self.result = Some(result);
        self.timeline = Some(timeline);
        self.playback_t_s = 0.0;
        self.playing = true;
    }

    fn advance_playback(&mut self, ctx: &Context) {
        let Some(tl) = &self.timeline else { return };
        if !self.playing {
            return;
        }
        let dt = ctx.input(|i| i.stable_dt).min(1.0 / 20.0);
        self.playback_t_s = (self.playback_t_s + dt * self.speed).min(tl.duration_s as f32);
        if self.playback_t_s >= tl.duration_s as f32 {
            self.playing = false;
        }
        ctx.request_repaint();
    }
}

impl eframe::App for SimApp {
    fn update(&mut self, ctx: &Context, _frame: &mut eframe::Frame) {
        self.advance_playback(ctx);

        top_bar(self, ctx);
        left_sidebar(self, ctx);
        right_inspector(self, ctx);
        bottom_event_log(self, ctx);
        central_map(self, ctx);
    }
}

// ---------------------------------------------------------------------------
// Panels
// ---------------------------------------------------------------------------

fn top_bar(app: &mut SimApp, ctx: &Context) {
    TopBottomPanel::top("top").show(ctx, |ui| {
        ui.horizontal(|ui| {
            ui.heading("OSR Sim GUI");
            ui.separator();
            ui.label(format!("scenario: {}", app.scenario_label));
            ui.separator();
            ui.label(format!(
                "lines: {} · stations: {} · route km: {:.1}",
                app.scenario.network.lines.len(),
                app.scenario.network.stations.len(),
                app.scenario.network.total_route_length_km()
            ));
            if let Some(tl) = &app.timeline {
                ui.separator();
                ui.label(format!(
                    "t = {:>5.0} / {} s",
                    app.playback_t_s, tl.duration_s
                ));
            }
        });
    });
}

fn left_sidebar(app: &mut SimApp, ctx: &Context) {
    SidePanel::left("sidebar").show(ctx, |ui| {
        ui.heading("Run + playback");
        ui.separator();
        ui.add(Slider::new(&mut app.duration_s, 60..=86_400).text("duration (s)"));
        if ui.button("Run sim").clicked() {
            app.run_sim();
        }
        if let Some(tl) = &app.timeline {
            ui.separator();
            ui.horizontal(|ui| {
                if ui
                    .button(if app.playing { "⏸ Pause" } else { "▶ Play" })
                    .clicked()
                {
                    app.playing = !app.playing;
                }
                if ui.button("⏹ Reset").clicked() {
                    app.playing = false;
                    app.playback_t_s = 0.0;
                }
            });
            ui.horizontal(|ui| {
                ui.label("speed:");
                for (label, v) in [("0.5×", 0.5), ("1×", 1.0), ("10×", 10.0), ("60×", 60.0)] {
                    if ui.selectable_label(app.speed == v, label).clicked() {
                        app.speed = v;
                    }
                }
            });
            ui.add(Slider::new(&mut app.playback_t_s, 0.0..=(tl.duration_s as f32)).text("t (s)"));
        }

        ui.separator();
        ui.heading("Fleet");
        for fleet in &app.scenario.fleets {
            let name = app
                .scenario
                .network
                .lines
                .get(fleet.line_index)
                .map(|l| l.name.as_str())
                .unwrap_or("?");
            ui.label(format!("  {name}: {} trainsets", fleet.trainset_count));
        }

        if let Some(r) = &app.result {
            ui.separator();
            ui.heading("Run summary");
            ui.label(format!("total train-km: {:.2}", r.total_train_km));
            ui.label(format!(
                "energy consumed: {:.2} kWh",
                r.total_energy_consumed_kwh
            ));
            ui.label(format!(
                "energy charged: {:.2} kWh",
                r.total_energy_charged_kwh
            ));
            let violations = r.invariant_violations.len();
            let colour = if violations == 0 {
                Color32::from_rgb(120, 220, 120)
            } else {
                Color32::from_rgb(230, 80, 80)
            };
            ui.colored_label(colour, format!("invariant violations: {violations}"));
            ui.separator();
            ui.heading("Vehicle systems");
            ui.label(format!(
                "controller ticks: {}",
                r.vehicle_systems.controller_ticks
            ));
            ui.label(format!(
                "door evaluations: {}",
                r.vehicle_systems.door_controller_evaluations
            ));
            let door_violations = r.vehicle_systems.door_interlock_violations;
            let door_colour = if door_violations == 0 {
                Color32::from_rgb(120, 220, 120)
            } else {
                Color32::from_rgb(230, 80, 80)
            };
            ui.colored_label(
                door_colour,
                format!("door interlock violations: {door_violations}"),
            );
            ui.label(format!(
                "PIS announcements: {}",
                r.vehicle_systems.pis_announcements
            ));
            ui.separator();
            ui.heading("Embedded software");
            ui.label(format!("TCMS ticks: {}", r.embedded.controller_ticks));
            ui.label(format!(
                "TCMS departure / travel holds: {} / {}",
                r.embedded.tcms_departure_inhibit_ticks, r.embedded.tcms_travel_hold_ticks
            ));
            ui.label(format!(
                "PTP: {} · {} locked ticks",
                r.time_sync.final_lock_state, r.time_sync.locked_ticks
            ));
            ui.label(format!(
                "event records: {}",
                r.embedded.event_records_written
            ));
            ui.label(format!("CBM samples: {}", r.embedded.cbm_samples));
            ui.label(format!(
                "T2G tx / backup / offline / dropped: {} / {} / {} / {}",
                r.embedded.t2g_transmissions,
                r.embedded.t2g_backup_ticks,
                r.embedded.t2g_offline_ticks,
                r.embedded.t2g_payloads_dropped
            ));
            let embedded_trips = r.embedded.hot_axle_trip_ticks + r.embedded.tcms_trip_ticks;
            let embedded_colour = if embedded_trips == 0 {
                Color32::from_rgb(120, 220, 120)
            } else {
                Color32::from_rgb(230, 180, 60)
            };
            ui.colored_label(
                embedded_colour,
                format!("embedded alert ticks: {embedded_trips}"),
            );
            ui.label(format!(
                "HABD passages / warnings / trips / active stops: {} / {} / {} / {}",
                r.habd_systems.passages_evaluated,
                r.habd_systems.warning_passages,
                r.habd_systems.trip_passages,
                r.habd_systems.active_stop_orders.len()
            ));
            ui.label(format!(
                "HABD restrictions issued / cleared / active / ticks: {} / {} / {} / {}",
                r.habd_systems.speed_restrictions_issued,
                r.habd_systems.speed_restrictions_cleared,
                r.habd_systems.active_speed_restrictions.len(),
                r.habd_systems.speed_restriction_ticks
            ));
            ui.label(format!(
                "Balises registry / fixes / missed / mismatch: {} / {} / {} / {}",
                r.balise_systems.registry_count,
                r.balise_systems.fixes_applied,
                r.balise_systems.missed_sightings,
                r.balise_systems.position_mismatches
            ));
            ui.label(format!(
                "Fare TVM issued / gate grants / denies / settled: {} / {} / {} / {} cents",
                r.fare_systems.tickets_issued,
                r.fare_systems.gate_grants,
                r.fare_systems.gate_denials,
                r.fare_systems.settled_fare_cents
            ));
            ui.label(format!(
                "OCC roster / reports / incidents / holds: {} / {} / {} / {}",
                r.occ_systems.final_roster_count,
                r.occ_systems.telemetry_reports_processed,
                r.occ_systems.final_active_incidents,
                r.occ_systems.final_active_dispatch_holds
            ));
            ui.label(format!(
                "Energy-site calls / conservation errors: {} / {}",
                r.energy_sites
                    .iter()
                    .map(|site| site.controller_evaluations)
                    .sum::<u64>(),
                r.energy_sites
                    .iter()
                    .map(|site| site.conservation_errors)
                    .sum::<u64>()
            ));
            ui.label(format!(
                "Regen arbiter ticks / requests / refused mA-ticks: {} / {} / {}",
                r.onboard.total_regen_arbiter_ticks,
                r.onboard.total_regen_request_ticks,
                r.onboard.total_regen_refused_ma
            ));
            ui.label(format!(
                "Wire frames / decode failures / semantic drift: {} / {} / {}",
                r.proto_systems.frames_decoded,
                r.proto_systems.decode_failures,
                r.proto_systems.semantic_mismatches
            ));
            ui.label(format!(
                "Switches / ticks / faults · crossings / ticks / faults: {} / {} / {} · {} / {} / {}",
                r.wayside_asset_systems.switch_count,
                r.wayside_asset_systems.switch_controller_ticks,
                r.wayside_asset_systems.switch_fault_ticks,
                r.wayside_asset_systems.crossing_count,
                r.wayside_asset_systems.crossing_controller_ticks,
                r.wayside_asset_systems.crossing_fault_ticks
            ));
            ui.label(format!(
                "Role preflight pass / fail / skip: {} / {} / {}",
                r.selftest_systems.checks_passed,
                r.selftest_systems.checks_failed,
                r.selftest_systems.checks_skipped
            ));
            ui.separator();
            ui.heading("Station + wayside");
            ui.label(format!(
                "station controller ticks: {}",
                r.infrastructure_systems.stations.controller_ticks
            ));
            ui.label(format!(
                "PSD open / obstructed: {} / {}",
                r.infrastructure_systems.stations.psd_open_ticks,
                r.infrastructure_systems.stations.psd_obstruction_ticks
            ));
            ui.label(format!(
                "wayside clear / unknown / present: {} / {} / {}",
                r.infrastructure_systems.wayside.clear_ticks,
                r.infrastructure_systems.wayside.unknown_ticks,
                r.infrastructure_systems.wayside.present_ticks
            ));
            ui.separator();
            ui.heading("Depot data services");
            ui.label(format!(
                "CBM payloads received: {}",
                r.backend_systems.cbm_samples_received
            ));
            ui.label(format!(
                "historian samples / metrics: {} / {}",
                r.backend_systems.historian_samples_ingested,
                r.backend_systems.historian_metrics_retained
            ));
            ui.label(format!(
                "routine / urgent work orders: {} / {}",
                r.backend_systems.routine_work_orders, r.backend_systems.urgent_work_orders
            ));
            if !r.faults_fired.is_empty() {
                ui.separator();
                ui.heading("Faults fired");
                for f in &r.faults_fired {
                    ui.label(format!("  · {}: {}", f.name, f.description));
                }
            }
        }
    });
}

fn right_inspector(app: &mut SimApp, ctx: &Context) {
    SidePanel::right("inspector").show(ctx, |ui| {
        ui.heading("Inspector");
        ui.separator();
        let Some(tl) = &app.timeline else {
            ui.label("(run a sim to populate)");
            return;
        };
        let frame_idx = (app.playback_t_s as u32).min(tl.duration_s);
        let Some(frame) = tl.frame_at(frame_idx) else {
            return;
        };
        if frame.trains.is_empty() {
            ui.label("(no trains in frame)");
            return;
        }
        let train_ids: Vec<TrainId> = frame.trains.iter().map(|t| t.train).collect();
        ui.label("Trains:");
        for tid in &train_ids {
            let selected = app.selected_train == Some(*tid);
            if ui.selectable_label(selected, tid.to_string()).clicked() {
                app.selected_train = Some(*tid);
            }
        }
        ui.separator();
        if let Some(sel) = app.selected_train {
            if let Some(tf) = frame.trains.iter().find(|t| t.train == sel) {
                ui.strong(tf.train.to_string());
                ui.label(format!("line: {}", tf.line_index));
                ui.label(format!("phase: {}", tf.phase));
                ui.label(format!("station_m: {:.1}", tf.station_m));
                let soc_colour = if tf.soc < 0.2 {
                    Color32::from_rgb(230, 80, 80)
                } else if tf.soc < 0.4 {
                    Color32::from_rgb(230, 180, 60)
                } else {
                    Color32::from_rgb(120, 220, 120)
                };
                ui.colored_label(soc_colour, format!("SoC: {:.2}", tf.soc));
                if let Some(e) = &tf.last_event {
                    ui.separator();
                    ui.label(RichText::new("last event:").monospace());
                    ui.label(RichText::new(e).small());
                }
            }
        } else {
            ui.label("(click a train id above)");
        }
    });
}

fn bottom_event_log(app: &mut SimApp, ctx: &Context) {
    TopBottomPanel::bottom("event_log")
        .default_height(160.0)
        .resizable(true)
        .show(ctx, |ui| {
            ui.horizontal(|ui| {
                ui.heading("Event log");
                ui.separator();
                ui.checkbox(&mut app.event_filter.show_dispatched, "dispatched");
                ui.checkbox(&mut app.event_filter.show_arrive, "arrive");
                ui.checkbox(&mut app.event_filter.show_depart, "depart");
                ui.checkbox(&mut app.event_filter.show_charging, "charging");
                ui.checkbox(&mut app.event_filter.show_turnaround, "turnaround");
                ui.checkbox(&mut app.event_filter.show_soc_warning, "soc-warning");
            });
            ui.separator();
            let Some(r) = &app.result else {
                ui.label("(run a sim to populate)");
                return;
            };
            let cutoff_s = app.playback_t_s as u32;
            ScrollArea::vertical().stick_to_bottom(true).show(ui, |ui| {
                for e in r
                    .events
                    .iter()
                    .filter(|e| e.sim_time_s <= cutoff_s && app.event_filter.passes(&e.kind))
                {
                    let colour = match &e.kind {
                        EventKind::SocWarning { .. } => Color32::from_rgb(230, 180, 60),
                        EventKind::DepartStation => Color32::from_rgb(90, 200, 120),
                        EventKind::ArriveStation { .. } => Color32::from_rgb(90, 160, 240),
                        EventKind::DepotServiceStart { .. } => Color32::from_rgb(155, 110, 220),
                        EventKind::DepotServiceComplete => Color32::from_rgb(90, 210, 185),
                        _ => Color32::LIGHT_GRAY,
                    };
                    let station = e.station_name.as_deref().unwrap_or("-");
                    ui.colored_label(
                        colour,
                        format!(
                            "{:>6.1}s  {:<5}  {:<18}  {:?}",
                            e.sim_time_s as f32,
                            e.train.to_string(),
                            station,
                            e.kind
                        ),
                    );
                }
            });
        });
}

fn central_map(app: &mut SimApp, ctx: &Context) {
    CentralPanel::default()
        .frame(egui::Frame::default().fill(app.palette.background))
        .show(ctx, |ui| {
            let rect = ui.available_rect_before_wrap();
            let painter = ui.painter_at(rect);
            let layout = NetworkLayout::build(&app.scenario.network, rect);
            draw_network(&painter, &layout, &app.scenario.network, &app.palette);

            // Fault badges on affected sections/stations.
            if let Some(r) = &app.result {
                draw_fault_badges(&painter, &rect, r, app);
            }

            // Draw trains from the current timeline frame.
            if let Some(tl) = &app.timeline {
                let frame_idx = (app.playback_t_s as u32).min(tl.duration_s);
                if let Some(frame) = tl.frame_at(frame_idx) {
                    for tf in &frame.trains {
                        let total = tl
                            .line_total_length_m
                            .get(tf.line_index)
                            .copied()
                            .unwrap_or(0.0);
                        let colour = phase_colour(app, &tf.phase);
                        let label = tf.train.to_string();
                        osr_gui_shared::draw_train(
                            &painter,
                            &layout,
                            &app.scenario.network,
                            tf.line_index,
                            if total > 0.0 {
                                tf.station_m * total / total
                            } else {
                                tf.station_m
                            },
                            &label,
                            colour,
                        );
                        // Highlight selection with a ring.
                        if app.selected_train == Some(tf.train) {
                            if let Some(strip) = layout.strips.get(tf.line_index) {
                                if let Some(x) =
                                    layout.station_m_to_x(tf.line_index, tf.station_m, total)
                                {
                                    painter.circle_stroke(
                                        Pos2::new(x, strip.y - 12.0),
                                        12.0,
                                        egui::Stroke::new(2.0, Color32::WHITE),
                                    );
                                }
                            }
                        }
                    }
                }
            }
        });
}

fn phase_colour(app: &SimApp, phase: &str) -> Color32 {
    match phase {
        "traveling" => app.palette.train_traveling,
        "dwelling" | "turnaround" => app.palette.train_dwelling,
        "charging" => app.palette.train_charging,
        "soc-warning" => app.palette.alert_fire,
        _ => app.palette.train_idle,
    }
}

fn draw_fault_badges(painter: &egui::Painter, rect: &Rect, result: &SimResult, app: &SimApp) {
    let cutoff_s = app.playback_t_s as u32;
    let active_now: HashSet<&String> = result
        .faults_fired
        .iter()
        .filter(|f| f.started_at_sim_s <= cutoff_s && cutoff_s < f.started_at_sim_s + f.duration_s)
        .map(|f| &f.name)
        .collect();
    if active_now.is_empty() {
        return;
    }
    let mut y = rect.top() + 24.0;
    for f in &result.faults_fired {
        if !active_now.contains(&f.name) {
            continue;
        }
        painter.rect_filled(
            Rect::from_min_size(Pos2::new(rect.right() - 260.0, y), egui::vec2(250.0, 20.0)),
            egui::Rounding::same(3.0),
            Color32::from_rgba_premultiplied(230, 120, 60, 220),
        );
        painter.text(
            Pos2::new(rect.right() - 250.0, y + 10.0),
            egui::Align2::LEFT_CENTER,
            format!("⚠ {}: {}", f.name, f.description),
            FontId::proportional(11.0),
            Color32::BLACK,
        );
        y += 24.0;
    }
}

/// Attempt to load `designs/west-asia/Iraq/Samawah/samawah.toml` from the
/// standard repo location; if the file isn't on disk the bundled
/// `canonical_samawah_scenario` snapshot is used instead.
fn _default_scenario() -> (ScenarioConfig, String) {
    let candidates = [
        "designs/west-asia/Iraq/Samawah/samawah.toml",
        "../designs/west-asia/Iraq/Samawah/samawah.toml",
        "../../designs/west-asia/Iraq/Samawah/samawah.toml",
    ];
    for c in candidates {
        let p = std::path::Path::new(c);
        if p.exists() {
            if let Ok(s) = load_scenario_from_path(p) {
                return (s, format!("{} (auto)", c));
            }
        }
    }
    (
        canonical_samawah_scenario(),
        "Samawah (bundled; designs/west-asia/Iraq/Samawah/samawah.toml not on disk)".into(),
    )
}
