//! Deterministic integration of the real OCC state evaluator.
//!
//! Every embedded TCMS report is folded into the authoritative roster. A
//! line with any emergency source opens one critical incident and receives an
//! automatic wildcard dispatch hold; the incident and hold clear when every
//! train on that line reports clear. Movement already in a section is not
//! stopped by this service-level hold.

use std::collections::BTreeMap;

use osr_occ::{occ_evaluate, IncidentSeverity, NewIncident, OccInputs, OccState, TrainReport};
use serde::{Deserialize, Serialize};

#[derive(Clone, Debug, Default)]
pub struct OccSystemsShadow {
    state: OccState,
    active_incident_by_line: BTreeMap<u32, u64>,
    summary: OccSystemsSummary,
}

#[derive(Clone, Debug, Default, Serialize, Deserialize, PartialEq, Eq)]
pub struct OccSystemsSummary {
    pub controller_ticks: u64,
    pub telemetry_reports_processed: u64,
    pub final_roster_count: u32,
    pub incidents_opened: u64,
    pub incidents_closed: u64,
    pub dispatch_hold_ticks: u64,
    pub final_active_incidents: u32,
    pub final_active_dispatch_holds: u32,
}

impl OccSystemsShadow {
    #[must_use]
    pub fn line_dispatch_held(&self, line_index: usize) -> bool {
        let line_id = (line_index + 1).min(u32::MAX as usize) as u32;
        self.state
            .holds
            .keys()
            .any(|key| key.line_id == line_id && key.station_id == 0)
    }
}

pub fn occ_systems_tick(
    shadow: &mut OccSystemsShadow,
    reports: &[TrainReport],
    train_line_indices: &[usize],
    sim_time_s: u32,
) {
    let now_ns = u64::from(sim_time_s).saturating_mul(1_000_000_000);
    let mut emergency_by_line = BTreeMap::<u32, bool>::new();
    for (report, line_index) in reports.iter().zip(train_line_indices) {
        let line_id = (*line_index + 1).min(u32::MAX as usize) as u32;
        emergency_by_line
            .entry(line_id)
            .and_modify(|active| *active |= report.any_emergency)
            .or_insert(report.any_emergency);
    }

    let mut new_lines = Vec::new();
    let mut new_incidents = Vec::new();
    let mut close_incident_ids = Vec::new();
    for (line_id, emergency) in emergency_by_line {
        match (emergency, shadow.active_incident_by_line.get(&line_id)) {
            (true, None) => {
                new_lines.push(line_id);
                new_incidents.push(NewIncident {
                    severity: IncidentSeverity::Critical,
                    line_id,
                    description: "TCMS emergency source active".to_string(),
                });
            }
            (false, Some(incident_id)) => close_incident_ids.push(*incident_id),
            _ => {}
        }
    }

    let output = occ_evaluate(
        &shadow.state,
        &OccInputs {
            now_ns,
            train_reports: reports.to_vec(),
            new_incidents,
            close_incident_ids: close_incident_ids.clone(),
            ..OccInputs::default()
        },
    );
    for (line_id, incident_id) in new_lines.into_iter().zip(&output.opened_incident_ids) {
        shadow.active_incident_by_line.insert(line_id, *incident_id);
    }
    if !close_incident_ids.is_empty() {
        shadow
            .active_incident_by_line
            .retain(|_, id| !close_incident_ids.contains(id));
    }
    shadow.summary.controller_ticks = shadow.summary.controller_ticks.saturating_add(1);
    shadow.summary.telemetry_reports_processed = shadow
        .summary
        .telemetry_reports_processed
        .saturating_add(reports.len() as u64);
    shadow.summary.incidents_opened = shadow
        .summary
        .incidents_opened
        .saturating_add(output.opened_incident_ids.len() as u64);
    shadow.summary.incidents_closed = shadow
        .summary
        .incidents_closed
        .saturating_add(output.closed_incident_ids.len() as u64);
    if !output.state.holds.is_empty() {
        shadow.summary.dispatch_hold_ticks = shadow.summary.dispatch_hold_ticks.saturating_add(1);
    }
    shadow.state = output.state;
    shadow.summary.final_roster_count = shadow.state.roster.len().min(u32::MAX as usize) as u32;
    shadow.summary.final_active_incidents =
        shadow.active_incident_by_line.len().min(u32::MAX as usize) as u32;
    shadow.summary.final_active_dispatch_holds =
        shadow.state.holds.len().min(u32::MAX as usize) as u32;
}

#[must_use]
pub fn summarise(shadow: &OccSystemsShadow) -> OccSystemsSummary {
    shadow.summary.clone()
}

#[cfg(test)]
mod tests {
    use super::*;

    fn report(emergency: bool, now_ns: u64) -> TrainReport {
        TrainReport {
            train_id: 1,
            now_ns,
            position_section: Some(1000),
            speed_mmps: 10_000,
            any_emergency: emergency,
            worst_alarm: u8::from(emergency) * 2,
            soc_ppt: 800,
        }
    }

    #[test]
    fn emergency_opens_and_clear_closes_line_hold() {
        let mut shadow = OccSystemsShadow::default();
        occ_systems_tick(&mut shadow, &[report(true, 0)], &[0], 0);
        assert!(shadow.line_dispatch_held(0));
        occ_systems_tick(&mut shadow, &[report(false, 1_000_000_000)], &[0], 1);
        assert!(!shadow.line_dispatch_held(0));
        let summary = summarise(&shadow);
        assert_eq!(summary.incidents_opened, 1);
        assert_eq!(summary.incidents_closed, 1);
    }
}
