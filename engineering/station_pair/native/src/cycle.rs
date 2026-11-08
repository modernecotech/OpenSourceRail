//! Conditional station-store sequence of one point-train with actual reversed
//! stop offsets retained. Ideal coordinated retarding-force sharing is
//! an explicit model hypothesis, not a spring/accumulator/contact force law.
use super::*;
use crate::cycle_release::ReleaseRuntime;
pub use crate::cycle_release::{ReleaseControl, ReleaseDiagnostics, ReleaseSample};

pub const REQUEST_SCHEMA: &str = "osr-station-cycle-request/1";
#[derive(Debug, Clone, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct Request {
    pub schema: String,
    pub cases: Vec<CycleCase>,
}
#[derive(Debug, Clone, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct Store {
    pub capacity_j: f64,
    pub capture_efficiency: f64,
    pub release_efficiency: f64,
    pub leakage_per_s: f64,
}
#[derive(Debug, Clone, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct Transfer {
    pub start_m: f64,
    pub end_m: f64,
    pub max_force_n: f64,
    pub max_power_w: f64,
}
#[derive(Debug, Clone, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct Reset {
    pub duration_s: f64,
    pub grid_energy_j: f64,
    pub grid_power_w: f64,
}
#[derive(Debug, Clone, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct Station {
    pub id: String,
    pub initial_energy_j: f64,
    pub store: Store,
    pub capture_stages: Vec<Transfer>,
    pub release: Transfer,
    pub reset: Reset,
}
#[derive(Debug, Clone, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct Leg {
    pub train_id: String,
    pub journey: Case,
    pub departure_station_id: String,
    pub arrival_station_id: String,
    pub departure_time_s: f64,
    pub departure_authorized: bool,
    pub capture_failed: bool,
    pub release_failed: bool,
    pub reset_failed: bool,
}
#[derive(Debug, Clone, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct CycleCase {
    pub id: String,
    pub candidate_id: String,
    pub stations: Vec<Station>,
    pub legs: Vec<Leg>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub release_control: Option<ReleaseControl>,
}
#[derive(Debug, Clone, Serialize)]
pub struct StationState {
    pub id: String,
    pub energy_j: f64,
    pub ready: bool,
    pub ready_at_s: f64,
    pub locked_until_s: f64,
}
#[derive(Debug, Clone, Serialize)]
pub struct CycleEvent {
    pub kind: String,
    pub station_id: String,
    pub time_s: f64,
}
#[derive(Debug, Clone, Serialize)]
pub struct RecoveryPoint {
    pub time_s: f64,
    pub position_m: f64,
    pub capture_n: f64,
    pub friction_n: f64,
    pub store_traction_n: f64,
    pub departure_store_j: f64,
    pub arrival_store_j: f64,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub release_control: Option<ReleaseSample>,
}
#[derive(Debug, Clone, Default, Serialize)]
pub struct LegEnergy {
    pub initial_store_j: f64,
    pub final_store_j: f64,
    pub storage_balance_residual_j: f64,
    pub capture_work_j: f64,
    pub stored_capture_j: f64,
    pub capture_loss_j: f64,
    pub bypassed_capture_work_j: f64,
    pub released_from_store_j: f64,
    pub delivered_launch_work_j: f64,
    pub release_loss_j: f64,
    pub leakage_j: f64,
    pub maximum_capture_force_n: f64,
    pub maximum_capture_power_w: f64,
    pub maximum_release_force_n: f64,
    pub maximum_release_power_w: f64,
    pub maximum_grid_force_n: f64,
    pub capture_stage_work_j: Vec<f64>,
    pub trace: Vec<RecoveryPoint>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub release_control: Option<ReleaseDiagnostics>,
}
#[derive(Debug, Clone, Default, Serialize)]
pub struct Ledger {
    pub initial_store_j: f64,
    pub final_store_j: f64,
    pub capture_work_j: f64,
    pub stored_capture_j: f64,
    pub capture_loss_j: f64,
    pub bypassed_capture_work_j: f64,
    pub released_from_store_j: f64,
    pub delivered_launch_work_j: f64,
    pub release_loss_j: f64,
    pub storage_leakage_j: f64,
    pub reset_grid_energy_j: f64,
    pub unperformed_reset_grid_energy_j: f64,
    pub grid_traction_energy_j: f64,
    pub drive_conversion_loss_j: f64,
    pub train_traction_work_j: f64,
    pub friction_brake_heat_j: f64,
    pub resistance_work_j: f64,
    pub external_resistance_work_j: f64,
    pub grade_work_j: f64,
    pub detached_reset_kinetic_energy_j: f64,
    pub final_train_kinetic_energy_j: f64,
    pub auxiliary_load_energy_j: f64,
    pub storage_balance_residual_j: f64,
    pub train_and_storage_balance_residual_j: f64,
}
#[derive(Debug, Clone, Serialize)]
pub struct LegResult {
    pub train_id: String,
    pub departure_station_id: String,
    pub arrival_station_id: String,
    pub departure_time_s: f64,
    pub initial_position_m: f64,
    pub end_time_s: f64,
    pub state: String,
    pub hold_reason: Option<String>,
    pub journey: Option<ResultRow>,
    pub energy: LegEnergy,
    pub events: Vec<CycleEvent>,
    pub station_states: Vec<StationState>,
}
#[derive(Debug, Clone, Serialize)]
pub struct CycleResult {
    pub id: String,
    pub candidate_id: String,
    pub state: String,
    pub scheduled_legs: usize,
    pub executed_legs: usize,
    pub arrived_legs: usize,
    pub legs: Vec<LegResult>,
    pub station_states: Vec<StationState>,
    pub ledger: Ledger,
    pub conditional: bool,
    pub physical_accepted: bool,
    pub engineering_accepted: bool,
    pub operating_release: bool,
    pub admitted_operating_map: bool,
    pub same_train_circulation_verified: bool,
    pub limitations: Vec<String>,
}
#[derive(Debug, Clone, Serialize)]
pub struct BatchResult {
    pub schema: &'static str,
    pub cases: Vec<CycleResult>,
}

fn transfer_valid(t: &Transfer, distance: f64) -> bool {
    nonneg(t.start_m)
        && pos(t.end_m)
        && t.end_m > t.start_m
        && t.end_m <= distance
        && nonneg(t.max_force_n)
        && nonneg(t.max_power_w)
}
fn validate(c: &CycleCase) -> Result<(), String> {
    if c.id.is_empty()
        || c.candidate_id.len() != 64
        || !c.candidate_id.bytes().all(|x| x.is_ascii_hexdigit())
        || c.stations.len() != 2
        || c.legs.is_empty()
        || c.legs.len() > 32
    {
        return Err("Cycle requires explicit candidate, exactly2stations and1..32serial point-train movements".into());
    }
    if c.stations[0].id.is_empty() || c.stations[0].id == c.stations[1].id {
        return Err("Distinct named station stores required".into());
    }
    if let Some(p) = &c.release_control {
        p.validate()?;
    }
    let mut ids = HashSet::new();
    let train = &c.legs[0].train_id;
    let distance = c.legs[0].journey.distance_m;
    for s in &c.stations {
        if s.id.is_empty()
            || !nonneg(s.store.capacity_j)
            || !nonneg(s.initial_energy_j)
            || s.initial_energy_j > s.store.capacity_j
            || !pos(s.store.capture_efficiency)
            || s.store.capture_efficiency > 1.
            || !pos(s.store.release_efficiency)
            || s.store.release_efficiency > 1.
            || !nonneg(s.store.leakage_per_s)
            || !nonneg(s.reset.duration_s)
            || !nonneg(s.reset.grid_energy_j)
            || !nonneg(s.reset.grid_power_w)
            || s.capture_stages.is_empty()
            || s.capture_stages.len() > 16
            || s.capture_stages
                .iter()
                .any(|t| !transfer_valid(t, distance))
            || !transfer_valid(&s.release, distance)
            || s.capture_stages
                .windows(2)
                .any(|p| p[0].end_m > p[1].start_m)
            || s.store.capacity_j == 0.
                && (s.initial_energy_j != 0.
                    || s.release.max_force_n != 0.
                    || s.capture_stages.iter().any(|q| q.max_force_n != 0.))
        {
            return Err(
                "Invalid finite explicit station transfer, store or reset specification".into(),
            );
        }
    }
    for (i, l) in c.legs.iter().enumerate() {
        valid(&l.journey)?;
        if l.train_id.is_empty() || &l.train_id != train {
            return Err(
                "One explicit point-train identity required for the serial alternating circulation"
                    .into(),
            );
        }
        if !ids.insert(l.journey.id.clone())
            || l.journey.candidate_id != c.candidate_id
            || l.journey.control.is_none()
            || l.journey.distance_m != distance
            || !nonneg(l.departure_time_s)
            || l.departure_time_s > 172800.
            || l.departure_station_id == l.arrival_station_id
            || !c.stations.iter().any(|s| s.id == l.departure_station_id)
            || !c.stations.iter().any(|s| s.id == l.arrival_station_id)
            || i > 0
                && (l.departure_time_s < c.legs[i - 1].departure_time_s
                    || l.departure_station_id != c.legs[i - 1].arrival_station_id)
        {
            return Err("Same-candidate bounded-feedback journeys, unique IDs, common distance and alternating monotone station schedule required".into());
        }
    }
    Ok(())
}
fn age(states: &mut [StationState], specs: &[Station], dt: f64) -> f64 {
    let mut loss = 0.;
    for (s, p) in states.iter_mut().zip(specs) {
        let end = s.energy_j * (-p.store.leakage_per_s * dt).exp();
        loss += s.energy_j - end;
        s.energy_j = end;
    }
    loss
}
#[derive(Debug, Clone)]
pub(crate) struct MechanicalStep {
    pub start_s: f64,
    pub h: f64,
    pub x: f64,
    pub v0: f64,
    pub v1: f64,
    pub dx: f64,
    pub traction_n: f64,
    pub brake_n: f64,
    pub fault: bool,
    pub acceleration: f64,
    pub previous_acceleration: f64,
    pub previous_h: f64,
}
pub(crate) struct RecordedMotion {
    pub journey: ResultRow,
    pub steps: Vec<MechanicalStep>,
    pub arrival_temperature_c: Option<f64>,
}
/// Runtime hook is absent from all retained ordinary journey evaluations.
pub(super) struct Runtime<'a> {
    pub states: &'a mut [StationState],
    pub specs: &'a [Station],
    pub leg: &'a Leg,
    pub dep: usize,
    pub arr: usize,
    pub energy: LegEnergy,
    pub events: Vec<CycleEvent>,
    pub initial_position_m: f64,
    next_trace_s: f64,
    release_runtime: Option<ReleaseRuntime>,
    pub recorded_steps: Option<Vec<MechanicalStep>>,
    pub moving_final_temperature_c: Option<f64>,
    inactive_recording: bool,
}
fn controlled_recording_feedback(legacy_allocator: bool, inactive: bool, v2: bool) -> bool {
    if inactive { !v2 } else { legacy_allocator }
}
impl<'a> Runtime<'a> {
    pub fn record_step(&mut self, step: MechanicalStep) {
        if let Some(v) = self.recorded_steps.as_mut() {
            v.push(step);
        }
    }
    #[allow(clippy::too_many_arguments)]
    pub fn observe_motion(
        &mut self,
        t: f64,
        x: f64,
        v0: f64,
        v1: f64,
        h: f64,
        ph: f64,
        pa: f64,
        a: f64,
        force: f64,
        brake: f64,
    ) {
        if let Some(q) = self.release_runtime.as_mut() {
            q.observe_motion(t, x, v0, v1, h, ph, pa, a, force, brake);
            self.energy.release_control = Some(q.diagnostics.clone());
        }
    }
    pub fn controlled_feedback(&self) -> bool {
        controlled_recording_feedback(
            self.release_runtime.is_some(),
            self.inactive_recording,
            self.leg
                .journey
                .control
                .as_ref()
                .is_some_and(|p| p.research_v2.is_some()),
        )
    }
    pub fn inactive_recording(&self) -> bool {
        self.inactive_recording && self.release_runtime.is_none()
    }
    pub fn controlled_grid_peak_power_w(&self) -> Option<f64> {
        self.release_runtime
            .as_ref()
            .map(|q| q.last_grid_peak_power_w)
    }
    pub fn boundaries(&self) -> Vec<f64> {
        if self.release_runtime.is_some() {
            return vec![];
        }
        let mut v = vec![];
        if !self.leg.release_failed
            && self.states[self.dep].energy_j > 0.
            && self.specs[self.dep].release.max_force_n > 0.
        {
            v.extend([
                self.specs[self.dep].release.start_m,
                self.specs[self.dep].release.end_m,
            ]);
        }
        v
    }
    pub fn release_cap(&self, x: f64, v: f64, h: f64, fault: bool) -> f64 {
        if self.release_runtime.is_some() {
            return 0.;
        }
        let s = &self.specs[self.dep];
        let q = &s.release;
        if fault
            || self.leg.release_failed
            || !self.leg.departure_authorized
            || x < q.start_m - 1e-9
            || x >= q.end_m - 1e-9
        {
            return 0.;
        }
        // Reserve this step's worst storage leakage before making an energy offer.
        let budget = self.states[self.dep].energy_j
            * (-s.store.leakage_per_s * h).exp()
            * s.store.release_efficiency;
        q.max_force_n
            .min(q.max_power_w / v.max(1e-12))
            .min(budget / (v * h).max(1e-12))
    }
    // Capture shares an already-applied total brake force. Integrate its exact
    // spatial overlap inside the accepted plant step: capture-only boundaries
    // must not change controller sampling or the mechanical stopping trace.
    fn capture_plan(
        &self,
        x: f64,
        dx: f64,
        v_upper: f64,
        h: f64,
        brake: f64,
        time_s: f64,
    ) -> Vec<(usize, f64, f64, f64)> {
        if dx <= 0. || brake <= 0. {
            return vec![];
        }
        let s = &self.specs[self.arr];
        let after_leak = self.states[self.arr].energy_j * (-s.store.leakage_per_s * h).exp();
        let mut room = (s.store.capacity_j - after_leak).max(0.);
        let ready = !self.leg.capture_failed
            && self.states[self.arr].ready
            && self.leg.departure_time_s + time_s - h >= self.states[self.arr].ready_at_s
            && self.leg.departure_time_s + time_s - h >= self.states[self.arr].locked_until_s;
        let mut plan = vec![];
        for (i, q) in s.capture_stages.iter().enumerate() {
            let overlap = ((x + dx).min(q.end_m) - x.max(q.start_m)).max(0.);
            if overlap <= 0. {
                continue;
            }
            let potential = brake
                .min(q.max_force_n)
                .min(q.max_power_w / v_upper.max(1e-12));
            let force = if ready {
                potential.min(room / (s.store.capture_efficiency * overlap).max(1e-12))
            } else {
                0.
            };
            room = (room - force * overlap * s.store.capture_efficiency).max(0.);
            plan.push((i, force, potential, overlap));
        }
        plan
    }
    pub fn commit(
        &mut self,
        x: f64,
        v: f64,
        v_upper: f64,
        v0: f64,
        v1: f64,
        dx: f64,
        h: f64,
        time_s: f64,
        traction: f64,
        brake: f64,
        fault: bool,
    ) -> Result<(f64, f64), String> {
        let allocation = if let Some(q) = self.release_runtime.as_mut() {
            Some(q.allocate(
                &self.specs[self.dep],
                self.leg,
                self.states[self.dep].energy_j,
                time_s - h,
                x,
                v0,
                v1,
                dx,
                h,
                traction,
                fault,
            ))
        } else {
            None
        };
        let release = allocation.as_ref().map_or_else(
            || traction.min(self.release_cap(x, v, h, fault)),
            |a| a.equivalent_force_n,
        );
        let plan = self.capture_plan(x, dx, v_upper, h, brake, time_s);
        let capture_work: f64 = plan.iter().map(|(_, f, _, overlap)| f * overlap).sum();
        let capture = if dx > 0. { capture_work / dx } else { 0. };
        let launch = allocation
            .as_ref()
            .map_or_else(|| release * dx.max(0.), |a| a.work_j);
        let draw = launch / self.specs[self.dep].store.release_efficiency;
        let stored = capture_work * self.specs[self.arr].store.capture_efficiency;
        self.energy.leakage_j += age(self.states, self.specs, h);
        if draw > self.states[self.dep].energy_j + 1e-6
            || stored + self.states[self.arr].energy_j
                > self.specs[self.arr].store.capacity_j + 1e-6
        {
            return Err("Accepted step violates exact storage energy/capacity budget".into());
        }
        self.states[self.dep].energy_j = (self.states[self.dep].energy_j - draw).max(0.);
        self.states[self.arr].energy_j += stored;
        self.energy.capture_work_j += capture_work;
        self.energy.stored_capture_j += stored;
        self.energy.capture_loss_j += capture_work - stored;
        self.energy.bypassed_capture_work_j +=
            plan.iter().map(|(_, f, p, d)| (p - f) * d).sum::<f64>();
        self.energy.released_from_store_j += draw;
        self.energy.delivered_launch_work_j += launch;
        self.energy.release_loss_j += draw - launch;
        self.energy.maximum_release_force_n = self
            .energy
            .maximum_release_force_n
            .max(allocation.as_ref().map_or(release, |a| a.peak_force_n));
        self.energy.maximum_release_power_w = self
            .energy
            .maximum_release_power_w
            .max(allocation.as_ref().map_or(release * v, |a| a.peak_power_w));
        self.energy.maximum_grid_force_n = self.energy.maximum_grid_force_n.max(traction - release);
        for (stage, force, _, distance) in plan {
            self.energy.capture_stage_work_j[stage] += force * distance;
            self.energy.maximum_capture_force_n = self.energy.maximum_capture_force_n.max(force);
            self.energy.maximum_capture_power_w =
                self.energy.maximum_capture_power_w.max(force * v_upper);
            if force * distance > 0.
                && !self.events.iter().any(|e| {
                    e.kind == "capture-stage-active"
                        && e.station_id == format!("{}:{stage}", self.specs[self.arr].id)
                })
            {
                self.events.push(CycleEvent {
                    kind: "capture-stage-active".into(),
                    station_id: format!("{}:{stage}", self.specs[self.arr].id),
                    time_s: self.leg.departure_time_s + time_s,
                });
            }
        }
        if launch > 0.
            && !self
                .events
                .iter()
                .any(|e| e.kind == "authorized-forward-release")
        {
            self.events.push(CycleEvent {
                kind: "authorized-forward-release".into(),
                station_id: self.specs[self.dep].id.clone(),
                time_s: self.leg.departure_time_s + time_s,
            });
        }
        if time_s >= self.next_trace_s {
            self.energy.trace.push(RecoveryPoint {
                time_s,
                position_m: x + dx,
                capture_n: capture,
                friction_n: brake - capture,
                store_traction_n: release,
                departure_store_j: self.states[self.dep].energy_j,
                arrival_store_j: self.states[self.arr].energy_j,
                release_control: self
                    .release_runtime
                    .as_ref()
                    .and_then(|q| q.last_sample.clone()),
            });
            self.next_trace_s = time_s + 1.;
        }
        self.energy.release_control = self.release_runtime.as_ref().map(|q| q.diagnostics.clone());
        Ok((launch, capture_work))
    }
}

#[cfg(test)]
mod recorder_helper_tests {
    use super::controlled_recording_feedback;
    #[test]
    fn pure_recorder_controller_selection_keeps_v2_separate_and_legacy_unchanged() {
        assert!(controlled_recording_feedback(true, false, false));
        assert!(controlled_recording_feedback(true, false, true));
        assert!(controlled_recording_feedback(false, true, false));
        assert!(!controlled_recording_feedback(false, true, true));
        assert!(!controlled_recording_feedback(true, true, true));
        assert!(!controlled_recording_feedback(false, false, false));
    }
}

pub fn evaluate(c: &CycleCase) -> Result<CycleResult, String> {
    validate(c)?;
    let mut states: Vec<StationState> = c
        .stations
        .iter()
        .map(|s| StationState {
            id: s.id.clone(),
            energy_j: s.initial_energy_j,
            ready: true,
            ready_at_s: 0.,
            locked_until_s: 0.,
        })
        .collect();
    let mut ledger = Ledger {
        initial_store_j: states.iter().map(|s| s.energy_j).sum(),
        ..Default::default()
    };
    let mut rows = vec![];
    let mut now = 0.;
    let mut initial_x = 0.;
    let mut state = "sequence-complete".to_string();
    for l in &c.legs {
        let dep = c
            .stations
            .iter()
            .position(|s| s.id == l.departure_station_id)
            .unwrap();
        let arr = 1 - dep;
        let early = l.departure_time_s < now - 1e-8;
        if !early {
            ledger.storage_leakage_j += age(&mut states, &c.stations, l.departure_time_s - now);
            now = l.departure_time_s;
        }
        let hold = if early {
            Some("Schedule overlaps previous arrival/dwell/reset; concurrent movements unsupported")
        } else if !l.departure_authorized {
            Some("No positive departure authorization")
        } else if !states[dep].ready
            || l.departure_time_s < states[dep].ready_at_s - 1e-8
            || l.departure_time_s < states[dep].locked_until_s - 1e-8
        {
            Some("Departure station remains locked or reset is unavailable")
        } else {
            None
        };
        if let Some(reason) = hold {
            rows.push(LegResult {
                train_id: l.train_id.clone(),
                departure_station_id: l.departure_station_id.clone(),
                arrival_station_id: l.arrival_station_id.clone(),
                departure_time_s: l.departure_time_s,
                initial_position_m: initial_x,
                end_time_s: now,
                state: "departure-held".into(),
                hold_reason: Some(reason.into()),
                journey: None,
                energy: LegEnergy::default(),
                events: vec![],
                station_states: states.clone(),
            });
            state = "sequence-held".into();
            break;
        }
        let initial_store = states.iter().map(|s| s.energy_j).sum();
        let mut runtime = Runtime {
            states: &mut states,
            specs: &c.stations,
            leg: l,
            dep,
            arr,
            energy: LegEnergy {
                initial_store_j: initial_store,
                capture_stage_work_j: vec![0.; c.stations[arr].capture_stages.len()],
                ..Default::default()
            },
            events: vec![],
            initial_position_m: initial_x,
            next_trace_s: 0.,
            release_runtime: c.release_control.clone().map(ReleaseRuntime::new),
            recorded_steps: None,
            moving_final_temperature_c: None,
            inactive_recording: false,
        };
        let mut journey = feedback::evaluate_with_recovery(
            &l.journey,
            l.journey.control.as_ref().unwrap(),
            Some(&mut runtime),
        )?;
        let mut energy = runtime.energy;
        let mut events = runtime.events;
        now = l.departure_time_s + journey.elapsed_s;
        ledger.capture_work_j += energy.capture_work_j;
        ledger.stored_capture_j += energy.stored_capture_j;
        ledger.capture_loss_j += energy.capture_loss_j;
        ledger.bypassed_capture_work_j += energy.bypassed_capture_work_j;
        ledger.released_from_store_j += energy.released_from_store_j;
        ledger.delivered_launch_work_j += energy.delivered_launch_work_j;
        ledger.release_loss_j += energy.release_loss_j;
        ledger.storage_leakage_j += energy.leakage_j;
        ledger.grid_traction_energy_j += journey.grid_energy_j;
        ledger.drive_conversion_loss_j += journey.drive_loss_j;
        ledger.train_traction_work_j += journey.traction_work_j;
        ledger.friction_brake_heat_j += journey.brake_heat_j;
        ledger.resistance_work_j += journey.resistance_work_j;
        ledger.external_resistance_work_j += journey.external_resistance_work_j;
        ledger.grade_work_j += journey.grade_work_j;
        ledger.detached_reset_kinetic_energy_j += journey.detached_reset_kinetic_energy_j;
        ledger.final_train_kinetic_energy_j += journey.final_kinetic_energy_j;
        ledger.auxiliary_load_energy_j += journey.auxiliary_energy_j;
        let arrived = journey.normal_numerical_arrival;
        let reason = if arrived {
            None
        } else {
            Some(
                "Journey did not achieve its declared numerical arrival; onward sequence held"
                    .to_string(),
            )
        };
        if arrived {
            let mut wait = l.journey.dwell_s;
            states[arr].locked_until_s = now + l.journey.dwell_s;
            events.push(CycleEvent {
                kind: "arrival-store-locked-through-dwell".into(),
                station_id: c.stations[arr].id.clone(),
                time_s: now,
            });
            for (index, required, failed) in [
                (dep, energy.delivered_launch_work_j > 0., false),
                (
                    arr,
                    c.stations[arr]
                        .capture_stages
                        .iter()
                        .any(|q| q.max_force_n > 0.),
                    l.reset_failed,
                ),
            ] {
                if !required {
                    continue;
                }
                let reset = &c.stations[index].reset;
                let reset_ok =
                    !failed && reset.grid_energy_j <= reset.duration_s * reset.grid_power_w + 1e-8;
                wait = wait.max(reset.duration_s);
                states[index].ready_at_s = now + reset.duration_s;
                states[index].ready = reset_ok;
                if reset_ok {
                    ledger.reset_grid_energy_j += reset.grid_energy_j;
                    events.push(CycleEvent {
                        kind: if index == dep {
                            "launcher-reset-complete-assumed"
                        } else {
                            "capture-reset-complete-assumed"
                        }
                        .into(),
                        station_id: c.stations[index].id.clone(),
                        time_s: now + reset.duration_s,
                    });
                } else {
                    state = "reset-held".into();
                    ledger.unperformed_reset_grid_energy_j += reset.grid_energy_j;
                    events.push(CycleEvent {
                        kind: "reset-failed-or-power-budget-insufficient".into(),
                        station_id: c.stations[index].id.clone(),
                        time_s: now,
                    });
                }
            }
            let idle_leak = age(&mut states, &c.stations, wait);
            energy.leakage_j += idle_leak;
            ledger.storage_leakage_j += idle_leak;
            now += wait;
        } else {
            states[arr].ready = false;
            state = "journey-held".into();
            // Stored energy can remain after a failed arrival, but cannot justify
            // an invented onward vehicle movement or authorized release.
            journey.normal_numerical_arrival = false;
            if energy.delivered_launch_work_j > 0. {
                states[dep].ready = false;
                ledger.unperformed_reset_grid_energy_j += c.stations[dep].reset.grid_energy_j;
                events.push(CycleEvent {
                    kind: "launcher-reset-debt-after-failed-motion".into(),
                    station_id: c.stations[dep].id.clone(),
                    time_s: now,
                });
            }
            if energy.capture_work_j > 0. {
                ledger.unperformed_reset_grid_energy_j += c.stations[arr].reset.grid_energy_j;
                events.push(CycleEvent {
                    kind: "capture-reset-debt-after-failed-arrival".into(),
                    station_id: c.stations[arr].id.clone(),
                    time_s: now,
                });
            }
        }
        energy.final_store_j = states.iter().map(|s| s.energy_j).sum();
        energy.storage_balance_residual_j = energy.initial_store_j + energy.stored_capture_j
            - energy.released_from_store_j
            - energy.leakage_j
            - energy.final_store_j;
        rows.push(LegResult {
            train_id: l.train_id.clone(),
            departure_station_id: l.departure_station_id.clone(),
            arrival_station_id: l.arrival_station_id.clone(),
            departure_time_s: l.departure_time_s,
            initial_position_m: initial_x,
            end_time_s: now,
            state: if arrived {
                "arrived".into()
            } else {
                "journey-held".into()
            },
            hold_reason: reason,
            journey: Some(journey),
            energy,
            events,
            station_states: states.clone(),
        });
        if !arrived {
            break;
        }
        initial_x = (l.journey.distance_m
            - rows
                .last()
                .unwrap()
                .journey
                .as_ref()
                .unwrap()
                .final_position_m)
            .max(0.);
    }
    ledger.final_store_j = states.iter().map(|s| s.energy_j).sum();
    ledger.storage_balance_residual_j = ledger.initial_store_j + ledger.stored_capture_j
        - ledger.released_from_store_j
        - ledger.storage_leakage_j
        - ledger.final_store_j;
    ledger.train_and_storage_balance_residual_j =
        ledger.initial_store_j + ledger.grid_traction_energy_j + ledger.grade_work_j
            - ledger.final_store_j
            - ledger.drive_conversion_loss_j
            - ledger.capture_loss_j
            - ledger.release_loss_j
            - ledger.storage_leakage_j
            - ledger.friction_brake_heat_j
            - ledger.resistance_work_j
            - ledger.external_resistance_work_j
            - ledger.detached_reset_kinetic_energy_j
            - ledger.final_train_kinetic_energy_j;
    let scale = ledger
        .grid_traction_energy_j
        .max(ledger.initial_store_j)
        .max(ledger.grade_work_j.abs())
        .max(1.);
    if ledger.storage_balance_residual_j.abs() > 1e-6 * scale
        || ledger.train_and_storage_balance_residual_j.abs() > 1e-6 * scale
    {
        state = "numerical-energy-held".into();
    }
    let executed = rows.iter().filter(|r| r.journey.is_some()).count();
    let arrived = rows
        .iter()
        .filter(|r| {
            r.journey
                .as_ref()
                .is_some_and(|j| j.normal_numerical_arrival)
        })
        .count();
    Ok(CycleResult{id:c.id.clone(),candidate_id:c.candidate_id.clone(),state,scheduled_legs:c.legs.len(),executed_legs:executed,arrived_legs:arrived,
        legs:rows,station_states:states,ledger,conditional:true,physical_accepted:false,engineering_accepted:false,operating_release:false,
        admitted_operating_map:false,same_train_circulation_verified:false,limitations:vec![
            "Serial alternating point-train only; actual reversed departure coordinate is distance minus previous final position. No position reset. Real vehicle length, reverse cab/gear, turnback, staging, platform occupancy and circulation qualification remain unresolved".into(),
            "Capture is ideal coordinated retarding-force sharing within existing independent brake capability. Instantaneous bypass to friction under full/failed storage is assumed; real blending/contact/brake fallback response is unverified".into(),
            "Transfer force/power envelopes and storage efficiencies/leakage are explicit hypotheses. They are not spring force-extension, hydraulic pressure-flow, cable/contact or measured duty curves".into(),
            "No grid top-up of storage is provided. Initial energy is explicit; auxiliary load and reset grid energy are separately reported. Captured work excludes rolling, aerodynamic, grade and detached tug energy".into(),
            "Capture and actual launch release each require a separately charged station reset using the declared shared duration/energy/power budget; reset starts conservatively after motion and may overlap dwell. Moving return mechanisms, electrical standstill losses, containment and repeated thermal duty remain unverified".into(),
        ]})
}
pub fn execute(q: Request) -> Result<BatchResult, String> {
    if q.schema != REQUEST_SCHEMA || q.cases.is_empty() || q.cases.len() > 64 {
        return Err("Explicit cycle schema and1..64cases required".into());
    }
    let mut ids = HashSet::new();
    let mut cases = vec![];
    for c in q.cases {
        if !ids.insert(c.id.clone()) {
            return Err("Duplicate cycle case ID".into());
        }
        cases.push(evaluate(&c)?);
    }
    Ok(BatchResult {
        schema: "osr-station-cycle-result/1",
        cases,
    })
}

/// Full-grid motion does not depend on the future store state in substitution
/// mode. Record every accepted mechanical step; the fleet engine alone applies
/// actual shared-store transactions in chronological order.
pub(crate) fn record_grid_motion(
    c: &Case,
    initial_position_m: f64,
    policy: &ReleaseControl,
) -> Result<RecordedMotion, String> {
    record_grid_motion_mode(c, initial_position_m, policy, false)
}
/// Only validated REAL outer zero-storage specs can issue this private permit.
/// The static exported Case is compared byte-for-byte, never rewritten here.
pub(crate) fn record_inactive_grid_motion(
    c: &Case,
    initial_position_m: f64,
    policy: &ReleaseControl,
    permit: &crate::fleet::InactiveRecordingPermit,
) -> Result<RecordedMotion, String> {
    if !permit.allows(c) || !nonneg(initial_position_m) || initial_position_m > c.distance_m {
        return Err("Inactive mechanical recording requires exact exported Case permission and a validated nonnegative native entry".into());
    }
    record_grid_motion_mode(c, initial_position_m, policy, true)
}
fn record_grid_motion_mode(
    c: &Case,
    initial_position_m: f64,
    policy: &ReleaseControl,
    inactive_recording: bool,
) -> Result<RecordedMotion, String> {
    valid(c)?;
    policy.validate()?;
    let p = c
        .control
        .as_ref()
        .ok_or("Fleet motion requires the bounded feedback policy")?;
    let station = |id: &str| Station {
        id: id.into(),
        initial_energy_j: 0.,
        store: Store {
            capacity_j: 0.,
            capture_efficiency: 1.,
            release_efficiency: 1.,
            leakage_per_s: 0.,
        },
        capture_stages: vec![Transfer {
            start_m: 0.,
            end_m: c.distance_m,
            max_force_n: 0.,
            max_power_w: 0.,
        }],
        release: Transfer {
            start_m: 0.,
            end_m: c.distance_m,
            max_force_n: 0.,
            max_power_w: 0.,
        },
        reset: Reset {
            duration_s: 0.,
            grid_energy_j: 0.,
            grid_power_w: 0.,
        },
    };
    let specs = vec![station("record-A"), station("record-B")];
    let mut states: Vec<StationState> = specs
        .iter()
        .map(|s| StationState {
            id: s.id.clone(),
            energy_j: 0.,
            ready: true,
            ready_at_s: 0.,
            locked_until_s: 0.,
        })
        .collect();
    let leg = Leg {
        train_id: "mechanical-recording".into(),
        journey: c.clone(),
        departure_station_id: specs[0].id.clone(),
        arrival_station_id: specs[1].id.clone(),
        departure_time_s: 0.,
        departure_authorized: true,
        capture_failed: true,
        release_failed: true,
        reset_failed: false,
    };
    let mut runtime = Runtime {
        states: &mut states,
        specs: &specs,
        leg: &leg,
        dep: 0,
        arr: 1,
        energy: LegEnergy {
            capture_stage_work_j: vec![0.],
            ..Default::default()
        },
        events: vec![],
        initial_position_m,
        next_trace_s: 0.,
        release_runtime: if inactive_recording {
            None
        } else {
            Some(ReleaseRuntime::new(policy.clone()))
        },
        recorded_steps: Some(vec![]),
        moving_final_temperature_c: None,
        inactive_recording,
    };
    let journey = feedback::evaluate_with_recovery(c, p, Some(&mut runtime))?;
    Ok(RecordedMotion {
        journey,
        steps: runtime.recorded_steps.unwrap(),
        arrival_temperature_c: runtime.moving_final_temperature_c,
    })
}
