//! OCC dispatcher-console application state + rendering.
//!
//! v1 scope (per RFC 0018 §7):
//! - Load the Samawah network (same as sim GUI).
//! - Render the network with live-style section-state overlays.
//! - Section-state panel with intrusion verdicts per section.
//! - Train panel with per-train phase + SoC (from a pre-recorded
//!   sim run so the "live" feel is deterministic for demonstration).
//! - Alert feed with category filtering.
//! - Action modals with input validation (v1 logs; v3 emits signed
//!   RFC 0017 envelopes).
//!
//! v2 (deferred): live consensus-log attach, streaming events,
//! audit-log display.

use std::collections::HashMap;

use eframe::egui::{
    self, CentralPanel, Color32, Context, Pos2, RichText, ScrollArea, SidePanel, TopBottomPanel,
};
use osr_core::{Network, SectionId};
use osr_gui_shared::{draw_network, draw_section_state, NetworkLayout, Palette};
use osr_interlocking::IntrusionState;
use osr_sim::scenario_file::{canonical_samawah_scenario, load_scenario_from_path};
use osr_sim::sim::{run, EventKind, RuntimeConfig, ScenarioConfig, SimResult};
use osr_sim::timeline::SimTimeline;

#[allow(missing_debug_implementations)]
pub struct OccApp {
    scenario: ScenarioConfig,
    network: Network,
    result: Option<SimResult>,
    timeline: Option<SimTimeline>,
    operator: String,
    palette: Palette,
    /// Per-section intrusion verdicts — v1 populated from faults.
    intrusions: HashMap<SectionId, IntrusionState>,
    alerts: Vec<Alert>,
    /// Playback cursor for the "live" feel.
    t_s: f32,
    running: bool,
    speed: f32,
    show_route_grant_modal: bool,
    show_override_modal: bool,
    show_habd_reset_modal: bool,
    show_degraded_mode_modal: bool,
    route_grant_buffer: RouteGrantBuffer,
    override_buffer: OverrideBuffer,
    habd_reset_buffer: HabdResetBuffer,
    degraded_mode: DegradedMode,
    alert_filter: AlertFilter,
}

#[derive(Clone, Copy, Debug, Default)]
pub struct RecordedStateSummary {
    pub duration_s: u32,
    pub recorded_events: usize,
    pub trains: usize,
    pub alerts: usize,
    pub intrusions: usize,
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
}

#[derive(Default)]
struct RouteGrantBuffer {
    train_id: String,
    section_ids: String,
}

#[derive(Default)]
struct OverrideBuffer {
    section_id: String,
    crew_id: String,
    expires_min: u32,
}

#[derive(Default)]
struct HabdResetBuffer {
    train_id: String,
    authorised_by: String,
    inspection_reference: String,
    inspection_complete: bool,
}

#[derive(Clone, Copy, PartialEq, Eq)]
enum DegradedMode {
    Normal,
    ManualOnMa,
    RestrictedService,
    Evacuation,
}

#[derive(Default)]
struct AlertFilter {
    show_info: bool,
    show_warn: bool,
    show_crit: bool,
}

impl AlertFilter {
    fn all() -> Self {
        Self {
            show_info: true,
            show_warn: true,
            show_crit: true,
        }
    }
}

#[derive(Clone, Debug)]
pub struct Alert {
    pub level: AlertLevel,
    pub category: String,
    pub text: String,
    pub sim_time_s: u32,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum AlertLevel {
    Info,
    Warn,
    Crit,
}

impl OccApp {
    pub fn new(operator: String) -> Self {
        Self::with_auto_attach(operator, false)
    }

    /// Construct + optionally pre-attach a recorded sim run and
    /// seed a Present intrusion on SEC1001 so the default view is
    /// populated. Used for screenshots / demos.
    pub fn with_auto_attach(operator: String, auto_attach: bool) -> Self {
        Self::with_auto_attach_duration(operator, auto_attach, 3600)
    }

    /// Construct a replay with an explicit deterministic duration.
    pub fn with_auto_attach_duration(operator: String, auto_attach: bool, duration_s: u32) -> Self {
        let mut app = Self::new_internal(operator);
        if auto_attach {
            app.load_recorded_run(duration_s);
            app.running = false;
            app.t_s = duration_s as f32 * 0.25;
            app.intrusions
                .insert(SectionId::new(1001), IntrusionState::Present);
            app.alerts.push(Alert {
                level: AlertLevel::Crit,
                category: "S7.1".into(),
                text: "SEC1001 — Present; dispatch track-patrol.".into(),
                sim_time_s: (duration_s as f32 * 0.25) as u32,
            });
        }
        app
    }

    /// Compact proof that the browser console attached a populated recording.
    pub fn recorded_state_summary(&self) -> RecordedStateSummary {
        let Some(result) = self.result.as_ref() else {
            return RecordedStateSummary {
                alerts: self.alerts.len(),
                intrusions: self.intrusions.len(),
                ..RecordedStateSummary::default()
            };
        };
        RecordedStateSummary {
            duration_s: result.sim_duration_s,
            recorded_events: result.events.len(),
            trains: result.per_train_final_soc.len(),
            alerts: self.alerts.len(),
            intrusions: self.intrusions.len(),
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
        }
    }

    fn new_internal(operator: String) -> Self {
        let (scenario, _label) = _default_scenario();
        let network = scenario.network.clone();
        let seeded_alerts = vec![
            Alert {
                level: AlertLevel::Info,
                category: "C2.1".into(),
                text: "OCC console — awaiting live consensus attach (v2).".into(),
                sim_time_s: 0,
            },
            Alert {
                level: AlertLevel::Warn,
                category: "S4".into(),
                text: "Climate alert: PM10 > 350 forecast 14:00.".into(),
                sim_time_s: 0,
            },
        ];
        Self {
            scenario,
            network,
            result: None,
            timeline: None,
            operator,
            palette: Palette::dark(),
            intrusions: HashMap::new(),
            alerts: seeded_alerts,
            t_s: 0.0,
            running: false,
            speed: 10.0,
            show_route_grant_modal: false,
            show_override_modal: false,
            show_habd_reset_modal: false,
            show_degraded_mode_modal: false,
            route_grant_buffer: RouteGrantBuffer::default(),
            override_buffer: OverrideBuffer {
                expires_min: 60,
                ..Default::default()
            },
            habd_reset_buffer: HabdResetBuffer::default(),
            degraded_mode: DegradedMode::Normal,
            alert_filter: AlertFilter::all(),
        }
    }

    fn load_recorded_run(&mut self, duration_s: u32) {
        let runtime = RuntimeConfig {
            duration_s,
            ..Default::default()
        };
        let result = run(&self.scenario, &runtime);
        let timeline = SimTimeline::from_result(&result, &self.network);
        // Seed alerts from the recorded events.
        for e in &result.events {
            if let EventKind::SocWarning { soc } = &e.kind {
                self.alerts.push(Alert {
                    level: AlertLevel::Warn,
                    category: "SoC".into(),
                    text: format!("{} low SoC {:.2}", e.train, soc),
                    sim_time_s: e.sim_time_s,
                });
            }
        }
        self.result = Some(result);
        self.timeline = Some(timeline);
        self.running = true;
        self.t_s = 0.0;
    }

    fn advance(&mut self, ctx: &Context) {
        let Some(tl) = &self.timeline else { return };
        if !self.running {
            return;
        }
        let dt = ctx.input(|i| i.stable_dt).min(1.0 / 20.0);
        self.t_s = (self.t_s + dt * self.speed).min(tl.duration_s as f32);
        ctx.request_repaint();
    }

    fn emit_action(&mut self, category: &str, text: String) {
        eprintln!("[OCC action] {category}: {text}");
        let t = self.t_s as u32;
        self.alerts.push(Alert {
            level: AlertLevel::Info,
            category: category.to_string(),
            text,
            sim_time_s: t,
        });
    }
}

impl eframe::App for OccApp {
    fn update(&mut self, ctx: &Context, _frame: &mut eframe::Frame) {
        self.advance(ctx);

        top_bar(self, ctx);
        left_actions(self, ctx);
        right_intrusions(self, ctx);
        bottom_alerts(self, ctx);
        central_map(self, ctx);

        // Modals
        modal_route_grant(self, ctx);
        modal_override(self, ctx);
        modal_habd_reset(self, ctx);
        modal_degraded_mode(self, ctx);
    }
}

fn top_bar(app: &mut OccApp, ctx: &Context) {
    TopBottomPanel::top("top").show(ctx, |ui| {
        ui.horizontal(|ui| {
            ui.heading("OSR OCC Console");
            ui.separator();
            ui.label(format!("operator: {}", app.operator));
            ui.separator();
            ui.label(format!(
                "network: {} lines · {} stations",
                app.network.lines.len(),
                app.network.stations.len()
            ));
            ui.separator();
            let mode_label = match app.degraded_mode {
                DegradedMode::Normal => RichText::new("NORMAL")
                    .color(Color32::from_rgb(120, 220, 120))
                    .strong(),
                DegradedMode::ManualOnMa => {
                    RichText::new("M1 Manual-on-MA").color(Color32::from_rgb(230, 180, 60))
                }
                DegradedMode::RestrictedService => {
                    RichText::new("M2 Restricted").color(Color32::from_rgb(230, 180, 60))
                }
                DegradedMode::Evacuation => {
                    RichText::new("M3 Evacuation").color(Color32::from_rgb(230, 80, 80))
                }
            };
            ui.label(mode_label);
            ui.separator();
            if let Some(tl) = &app.timeline {
                ui.label(format!("live t = {:>5.0} / {} s", app.t_s, tl.duration_s));
            } else {
                ui.colored_label(
                    Color32::from_rgb(230, 180, 60),
                    "(no timeline — click \"Attach recording\")",
                );
            }
        });
    });
}

fn left_actions(app: &mut OccApp, ctx: &Context) {
    SidePanel::left("actions").show(ctx, |ui| {
        ui.heading("Playback");
        if ui.button("Attach recording").clicked() {
            app.load_recorded_run(3600);
        }
        if app.timeline.is_some() {
            ui.horizontal(|ui| {
                if ui.button(if app.running { "⏸" } else { "▶" }).clicked() {
                    app.running = !app.running;
                }
                if ui.button("⏹").clicked() {
                    app.running = false;
                    app.t_s = 0.0;
                }
            });
            ui.horizontal(|ui| {
                for (label, v) in [("1×", 1.0), ("10×", 10.0), ("60×", 60.0)] {
                    if ui.selectable_label(app.speed == v, label).clicked() {
                        app.speed = v;
                    }
                }
            });
        }

        ui.separator();
        ui.heading("Dispatcher actions");
        if ui.button("Issue route grant (S2.1)…").clicked() {
            app.show_route_grant_modal = true;
        }
        if ui.button("Commit MaintenanceOverride (S5.1)…").clicked() {
            app.show_override_modal = true;
        }
        if ui.button("Release inspected HABD stop…").clicked() {
            app.show_habd_reset_modal = true;
        }
        if ui.button("Declare degraded mode…").clicked() {
            app.show_degraded_mode_modal = true;
        }

        ui.separator();
        ui.heading("Trains");
        if let Some(tl) = &app.timeline {
            let frame_idx = (app.t_s as u32).min(tl.duration_s);
            if let Some(frame) = tl.frame_at(frame_idx) {
                for tf in &frame.trains {
                    let colour = match tf.phase.as_str() {
                        "traveling" => app.palette.train_traveling,
                        "dwelling" => app.palette.train_dwelling,
                        "charging" => app.palette.train_charging,
                        "soc-warning" => app.palette.alert_fire,
                        _ => app.palette.train_idle,
                    };
                    ui.colored_label(
                        colour,
                        format!(
                            "{} · L{} · {} · SoC {:.2}",
                            tf.train, tf.line_index, tf.phase, tf.soc
                        ),
                    );
                }
            }
        } else {
            ui.label("(attach recording to populate)");
        }
        if let Some(result) = &app.result {
            ui.separator();
            ui.heading("Embedded telemetry");
            ui.label(format!("TCMS ticks: {}", result.embedded.controller_ticks));
            ui.label(format!(
                "TCMS departure / travel holds: {} / {}",
                result.embedded.tcms_departure_inhibit_ticks,
                result.embedded.tcms_travel_hold_ticks
            ));
            ui.label(format!(
                "PTP: {} · {} locked ticks",
                result.time_sync.final_lock_state, result.time_sync.locked_ticks
            ));
            ui.label(format!(
                "T2G tx / backup / offline / dropped: {} / {} / {} / {}",
                result.embedded.t2g_transmissions,
                result.embedded.t2g_backup_ticks,
                result.embedded.t2g_offline_ticks,
                result.embedded.t2g_payloads_dropped
            ));
            ui.label(format!(
                "CBM service flags: {}",
                result.embedded.cbm_service_flags
            ));
            ui.label(format!(
                "HABD passages / warnings / trips / active stops: {} / {} / {} / {}",
                result.habd_systems.passages_evaluated,
                result.habd_systems.warning_passages,
                result.habd_systems.trip_passages,
                result.habd_systems.active_stop_orders.len()
            ));
            ui.label(format!(
                "HABD restrictions issued / cleared / active / ticks: {} / {} / {} / {}",
                result.habd_systems.speed_restrictions_issued,
                result.habd_systems.speed_restrictions_cleared,
                result.habd_systems.active_speed_restrictions.len(),
                result.habd_systems.speed_restriction_ticks
            ));
            ui.label(format!(
                "Balises registry / fixes / missed / mismatch: {} / {} / {} / {}",
                result.balise_systems.registry_count,
                result.balise_systems.fixes_applied,
                result.balise_systems.missed_sightings,
                result.balise_systems.position_mismatches
            ));
            ui.label(format!(
                "Fare TVM issued / gate grants / denies / settled: {} / {} / {} / {} cents",
                result.fare_systems.tickets_issued,
                result.fare_systems.gate_grants,
                result.fare_systems.gate_denials,
                result.fare_systems.settled_fare_cents
            ));
            ui.label(format!(
                "OCC roster / reports / incidents / holds: {} / {} / {} / {}",
                result.occ_systems.final_roster_count,
                result.occ_systems.telemetry_reports_processed,
                result.occ_systems.final_active_incidents,
                result.occ_systems.final_active_dispatch_holds
            ));
            ui.label(format!(
                "Energy-site calls / conservation errors: {} / {}",
                result
                    .energy_sites
                    .iter()
                    .map(|site| site.controller_evaluations)
                    .sum::<u64>(),
                result
                    .energy_sites
                    .iter()
                    .map(|site| site.conservation_errors)
                    .sum::<u64>()
            ));
            ui.label(format!(
                "Regen arbiter ticks / requests / refused mA-ticks: {} / {} / {}",
                result.onboard.total_regen_arbiter_ticks,
                result.onboard.total_regen_request_ticks,
                result.onboard.total_regen_refused_ma
            ));
            ui.label(format!(
                "Wire frames / decode failures / semantic drift: {} / {} / {}",
                result.proto_systems.frames_decoded,
                result.proto_systems.decode_failures,
                result.proto_systems.semantic_mismatches
            ));
            ui.label(format!(
                "Switches / ticks / faults · crossings / ticks / faults: {} / {} / {} · {} / {} / {}",
                result.wayside_asset_systems.switch_count,
                result.wayside_asset_systems.switch_controller_ticks,
                result.wayside_asset_systems.switch_fault_ticks,
                result.wayside_asset_systems.crossing_count,
                result.wayside_asset_systems.crossing_controller_ticks,
                result.wayside_asset_systems.crossing_fault_ticks
            ));
            ui.label(format!(
                "Role preflight pass / fail / skip: {} / {} / {}",
                result.selftest_systems.checks_passed,
                result.selftest_systems.checks_failed,
                result.selftest_systems.checks_skipped
            ));
            ui.separator();
            ui.heading("Station + wayside");
            ui.label(format!(
                "Station controller ticks: {}",
                result.infrastructure_systems.stations.controller_ticks
            ));
            ui.label(format!(
                "PSD open / obstruction: {} / {}",
                result.infrastructure_systems.stations.psd_open_ticks,
                result.infrastructure_systems.stations.psd_obstruction_ticks
            ));
            ui.label(format!(
                "Wayside detector ticks / transitions: {} / {}",
                result.infrastructure_systems.wayside.detector_ticks,
                result.infrastructure_systems.wayside.verdict_transitions
            ));
            ui.separator();
            ui.heading("Depot data services");
            ui.label(format!(
                "CBM payloads / historian samples: {} / {}",
                result.backend_systems.cbm_samples_received,
                result.backend_systems.historian_samples_ingested
            ));
            ui.label(format!(
                "routine / urgent work orders: {} / {}",
                result.backend_systems.routine_work_orders,
                result.backend_systems.urgent_work_orders
            ));
        }
    });
}

fn right_intrusions(app: &mut OccApp, ctx: &Context) {
    SidePanel::right("intrusions").show(ctx, |ui| {
        ui.heading("Section state (RFC 0016)");
        ui.separator();
        ui.label("Intrusion verdicts, colour-coded per section.");
        ui.separator();
        ui.horizontal(|ui| {
            if ui.button("Simulate Present on SEC1001").clicked() {
                app.intrusions
                    .insert(SectionId::new(1001), IntrusionState::Present);
                app.alerts.push(Alert {
                    level: AlertLevel::Crit,
                    category: "S7.1".into(),
                    text: "SEC1001 — Present; dispatch track-patrol.".into(),
                    sim_time_s: app.t_s as u32,
                });
            }
            if ui.button("Clear SEC1001").clicked() {
                app.intrusions
                    .insert(SectionId::new(1001), IntrusionState::Clear);
            }
        });
        ui.separator();
        if app.intrusions.is_empty() {
            ui.label("(none on record)");
        }
        for (&sid, state) in &app.intrusions {
            let (colour, label) = match state {
                IntrusionState::Clear => (Color32::from_rgb(120, 220, 120), "Clear"),
                IntrusionState::Unknown => (app.palette.intrusion_unknown, "Unknown"),
                IntrusionState::Present => (app.palette.intrusion_present, "Present"),
            };
            ui.colored_label(colour, format!("{sid}: {label}"));
        }
    });
}

fn bottom_alerts(app: &mut OccApp, ctx: &Context) {
    TopBottomPanel::bottom("alerts")
        .default_height(150.0)
        .resizable(true)
        .show(ctx, |ui| {
            ui.horizontal(|ui| {
                ui.heading("Alerts");
                ui.separator();
                ui.checkbox(&mut app.alert_filter.show_info, "info");
                ui.checkbox(&mut app.alert_filter.show_warn, "warn");
                ui.checkbox(&mut app.alert_filter.show_crit, "crit");
            });
            ui.separator();
            let cutoff = app.t_s as u32;
            ScrollArea::vertical().stick_to_bottom(true).show(ui, |ui| {
                for a in app
                    .alerts
                    .iter()
                    .filter(|a| a.sim_time_s <= cutoff)
                    .filter(|a| match a.level {
                        AlertLevel::Info => app.alert_filter.show_info,
                        AlertLevel::Warn => app.alert_filter.show_warn,
                        AlertLevel::Crit => app.alert_filter.show_crit,
                    })
                {
                    let colour = match a.level {
                        AlertLevel::Info => Color32::LIGHT_GRAY,
                        AlertLevel::Warn => Color32::from_rgb(230, 180, 60),
                        AlertLevel::Crit => Color32::from_rgb(230, 80, 80),
                    };
                    ui.colored_label(
                        colour,
                        format!("[{:>5}s][{:<4}] {}", a.sim_time_s, a.category, a.text),
                    );
                }
            });
        });
}

fn central_map(app: &mut OccApp, ctx: &Context) {
    CentralPanel::default()
        .frame(egui::Frame::default().fill(app.palette.background))
        .show(ctx, |ui| {
            let rect = ui.available_rect_before_wrap();
            let painter = ui.painter_at(rect);
            let layout = NetworkLayout::build(&app.network, rect);
            draw_network(&painter, &layout, &app.network, &app.palette);

            // Section-state overlays.
            for (line_idx, line) in app.network.lines.iter().enumerate() {
                for (i, sec_id) in line.forward_sections.iter().enumerate() {
                    let Some(&from) = line.stations.get(i) else {
                        continue;
                    };
                    let Some(&to) = line.stations.get(i + 1) else {
                        continue;
                    };
                    let state = match app.intrusions.get(sec_id) {
                        Some(IntrusionState::Present) => app.palette.intrusion_present,
                        Some(IntrusionState::Unknown) => app.palette.intrusion_unknown,
                        _ => continue,
                    };
                    draw_section_state(&painter, &layout, line_idx, from, to, state);
                }
            }

            // Trains from the timeline.
            if let Some(tl) = &app.timeline {
                let frame_idx = (app.t_s as u32).min(tl.duration_s);
                if let Some(frame) = tl.frame_at(frame_idx) {
                    for tf in &frame.trains {
                        let colour = match tf.phase.as_str() {
                            "traveling" => app.palette.train_traveling,
                            "dwelling" => app.palette.train_dwelling,
                            "charging" => app.palette.train_charging,
                            "soc-warning" => app.palette.alert_fire,
                            _ => app.palette.train_idle,
                        };
                        osr_gui_shared::draw_train(
                            &painter,
                            &layout,
                            &app.network,
                            tf.line_index,
                            tf.station_m,
                            &tf.train.to_string(),
                            colour,
                        );
                    }
                }
            }

            // READ-ONLY watermark.
            painter.text(
                Pos2::new(rect.right() - 10.0, rect.bottom() - 10.0),
                egui::Align2::RIGHT_BOTTOM,
                "READ-ONLY v1 — actions are stubs",
                egui::FontId::proportional(10.0),
                Color32::from_rgba_premultiplied(230, 120, 120, 180),
            );
        });
}

// ---------------------------------------------------------------------------
// Modals
// ---------------------------------------------------------------------------

fn modal_route_grant(app: &mut OccApp, ctx: &Context) {
    if !app.show_route_grant_modal {
        return;
    }
    let mut open = app.show_route_grant_modal;
    egui::Window::new("Issue route grant (S2.1)")
        .open(&mut open)
        .show(ctx, |ui| {
            ui.label("Train id:");
            ui.text_edit_singleline(&mut app.route_grant_buffer.train_id);
            ui.label("Section ids (comma-separated numbers):");
            ui.text_edit_singleline(&mut app.route_grant_buffer.section_ids);
            let validation = validate_route_grant(&app.route_grant_buffer);
            ui.separator();
            match &validation {
                Ok(_) => ui.colored_label(
                    Color32::from_rgb(120, 220, 120),
                    "✓ valid — v3 will emit RFC 0017 signed envelope.",
                ),
                Err(e) => ui.colored_label(Color32::from_rgb(230, 80, 80), format!("✗ {e}")),
            };
            ui.separator();
            if ui
                .add_enabled(validation.is_ok(), egui::Button::new("Commit"))
                .clicked()
            {
                let msg = format!(
                    "train={} sections=[{}]",
                    app.route_grant_buffer.train_id, app.route_grant_buffer.section_ids
                );
                app.emit_action("S2.1", msg);
                app.show_route_grant_modal = false;
            }
            if ui.button("Cancel").clicked() {
                app.show_route_grant_modal = false;
            }
        });
    app.show_route_grant_modal = open && app.show_route_grant_modal;
}

fn modal_override(app: &mut OccApp, ctx: &Context) {
    if !app.show_override_modal {
        return;
    }
    let mut open = app.show_override_modal;
    egui::Window::new("Commit MaintenanceOverride (S5.1)")
        .open(&mut open)
        .show(ctx, |ui| {
            ui.label("Section id:");
            ui.text_edit_singleline(&mut app.override_buffer.section_id);
            ui.label("Crew id:");
            ui.text_edit_singleline(&mut app.override_buffer.crew_id);
            ui.add(
                egui::Slider::new(&mut app.override_buffer.expires_min, 15..=240)
                    .text("expires (min)"),
            );
            let validation = validate_override(&app.override_buffer);
            ui.separator();
            match &validation {
                Ok(_) => ui.colored_label(
                    Color32::from_rgb(120, 220, 120),
                    "✓ valid — v3 will emit RFC 0017 signed envelope.",
                ),
                Err(e) => ui.colored_label(Color32::from_rgb(230, 80, 80), format!("✗ {e}")),
            };
            ui.separator();
            if ui
                .add_enabled(validation.is_ok(), egui::Button::new("Commit"))
                .clicked()
            {
                let msg = format!(
                    "section={} crew={} expires_min={}",
                    app.override_buffer.section_id,
                    app.override_buffer.crew_id,
                    app.override_buffer.expires_min
                );
                app.emit_action("S5.1", msg);
                app.show_override_modal = false;
            }
            if ui.button("Cancel").clicked() {
                app.show_override_modal = false;
            }
        });
    app.show_override_modal = open && app.show_override_modal;
}

fn modal_habd_reset(app: &mut OccApp, ctx: &Context) {
    if !app.show_habd_reset_modal {
        return;
    }
    let mut open = app.show_habd_reset_modal;
    egui::Window::new("Release inspected HABD stop")
        .open(&mut open)
        .show(ctx, |ui| {
            ui.label("Train id:");
            ui.text_edit_singleline(&mut app.habd_reset_buffer.train_id);
            ui.label("Qualified authority:");
            ui.text_edit_singleline(&mut app.habd_reset_buffer.authorised_by);
            ui.label("Inspection reference:");
            ui.text_edit_singleline(&mut app.habd_reset_buffer.inspection_reference);
            ui.checkbox(
                &mut app.habd_reset_buffer.inspection_complete,
                "Affected vehicle examined and line confirmed clear",
            );
            let validation = validate_habd_reset(&app.habd_reset_buffer);
            ui.separator();
            match &validation {
                Ok(_) => ui.colored_label(
                    Color32::from_rgb(120, 220, 120),
                    "✓ valid inspected-release request",
                ),
                Err(error) => {
                    ui.colored_label(Color32::from_rgb(230, 80, 80), format!("✗ {error}"))
                }
            };
            ui.separator();
            if ui
                .add_enabled(validation.is_ok(), egui::Button::new("Commit"))
                .clicked()
            {
                app.emit_action(
                    "HABD.RESET",
                    format!(
                        "train={} authority={} inspection={}",
                        app.habd_reset_buffer.train_id,
                        app.habd_reset_buffer.authorised_by,
                        app.habd_reset_buffer.inspection_reference
                    ),
                );
                app.show_habd_reset_modal = false;
            }
            if ui.button("Cancel").clicked() {
                app.show_habd_reset_modal = false;
            }
        });
    app.show_habd_reset_modal = open && app.show_habd_reset_modal;
}

fn modal_degraded_mode(app: &mut OccApp, ctx: &Context) {
    if !app.show_degraded_mode_modal {
        return;
    }
    let mut open = app.show_degraded_mode_modal;
    let mut selected = app.degraded_mode;
    egui::Window::new("Declare degraded mode (RFC 0013 §5)")
        .open(&mut open)
        .show(ctx, |ui| {
            ui.selectable_value(&mut selected, DegradedMode::Normal, "Normal");
            ui.selectable_value(&mut selected, DegradedMode::ManualOnMa, "M1 Manual-on-MA");
            ui.selectable_value(
                &mut selected,
                DegradedMode::RestrictedService,
                "M2 Restricted service",
            );
            ui.selectable_value(&mut selected, DegradedMode::Evacuation, "M3 Evacuation");
            ui.separator();
            if ui.button("Apply").clicked() {
                let was = app.degraded_mode;
                app.degraded_mode = selected;
                if was != selected {
                    app.emit_action("S3", format!("degraded mode → {:?}", selected as u8));
                }
                app.show_degraded_mode_modal = false;
            }
            if ui.button("Cancel").clicked() {
                app.show_degraded_mode_modal = false;
            }
        });
    app.show_degraded_mode_modal = open && app.show_degraded_mode_modal;
}

// ---------------------------------------------------------------------------
// Validators — return Ok(()) or an error string for the user.
// ---------------------------------------------------------------------------

fn validate_route_grant(b: &RouteGrantBuffer) -> Result<(), String> {
    if b.train_id.trim().is_empty() {
        return Err("train id is required".into());
    }
    if !b.train_id.starts_with('T') || b.train_id[1..].parse::<u64>().is_err() {
        return Err("train id must be 'T<number>'".into());
    }
    if b.section_ids.trim().is_empty() {
        return Err("at least one section id is required".into());
    }
    for sid in b.section_ids.split(',') {
        if sid.trim().parse::<u64>().is_err() {
            return Err(format!("section id '{sid}' is not a number"));
        }
    }
    Ok(())
}

fn validate_override(b: &OverrideBuffer) -> Result<(), String> {
    if b.section_id.trim().parse::<u64>().is_err() {
        return Err("section id must be a number".into());
    }
    if b.crew_id.trim().is_empty() {
        return Err("crew id is required".into());
    }
    if b.expires_min < 15 || b.expires_min > 240 {
        return Err("expires must be 15..=240 minutes".into());
    }
    Ok(())
}

fn validate_habd_reset(buffer: &HabdResetBuffer) -> Result<(), String> {
    let digits = buffer
        .train_id
        .strip_prefix('T')
        .ok_or_else(|| "train id must be 'T<number>'".to_string())?;
    if digits
        .parse::<u64>()
        .ok()
        .filter(|number| *number > 0)
        .is_none()
    {
        return Err("train id must be 'T<number>'".into());
    }
    if buffer.authorised_by.trim().is_empty() {
        return Err("qualified authority is required".into());
    }
    if buffer.inspection_reference.trim().is_empty() {
        return Err("inspection reference is required".into());
    }
    if !buffer.inspection_complete {
        return Err("inspection and line-clear confirmation is required".into());
    }
    Ok(())
}

/// Prefer the on-disk `cities/catalogue/west-asia/Iraq/Samawah/samawah.toml`
/// (so a fresh `osr-design` regeneration shows up immediately);
/// fall back to the bundled snapshot when the binary is run from
/// outside the repo. Same logic as [`osr_sim_gui`'s `_default_scenario`].
fn _default_scenario() -> (ScenarioConfig, String) {
    let candidates = [
        "cities/catalogue/west-asia/Iraq/Samawah/samawah.toml",
        "../cities/catalogue/west-asia/Iraq/Samawah/samawah.toml",
        "../../cities/catalogue/west-asia/Iraq/Samawah/samawah.toml",
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
        "Samawah (bundled; cities/catalogue/west-asia/Iraq/Samawah/samawah.toml not on disk)"
            .into(),
    )
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn route_grant_validates_ok() {
        let b = RouteGrantBuffer {
            train_id: "T7".into(),
            section_ids: "1000,1001".into(),
        };
        assert!(validate_route_grant(&b).is_ok());
    }

    #[test]
    fn route_grant_rejects_bad_train_id() {
        let b = RouteGrantBuffer {
            train_id: "foo".into(),
            section_ids: "1000".into(),
        };
        assert!(validate_route_grant(&b).is_err());
    }

    #[test]
    fn route_grant_rejects_bad_section() {
        let b = RouteGrantBuffer {
            train_id: "T1".into(),
            section_ids: "1000, abc".into(),
        };
        assert!(validate_route_grant(&b).is_err());
    }

    #[test]
    fn override_validates_ok() {
        let b = OverrideBuffer {
            section_id: "1001".into(),
            crew_id: "crew-a".into(),
            expires_min: 60,
        };
        assert!(validate_override(&b).is_ok());
    }

    #[test]
    fn override_rejects_out_of_range_expiry() {
        let b = OverrideBuffer {
            section_id: "1001".into(),
            crew_id: "crew-a".into(),
            expires_min: 10,
        };
        assert!(validate_override(&b).is_err());
    }

    #[test]
    fn habd_reset_requires_inspection_and_named_authority() {
        let mut buffer = HabdResetBuffer {
            train_id: "T7".into(),
            authorised_by: "rolling-stock-technician".into(),
            inspection_reference: "inspection-42".into(),
            inspection_complete: false,
        };
        assert!(validate_habd_reset(&buffer).is_err());
        buffer.inspection_complete = true;
        assert!(validate_habd_reset(&buffer).is_ok());
    }
}
