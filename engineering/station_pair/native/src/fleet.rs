//! Causal shared-store dispatch research under independently available grid
//! traction. Terminal motion and route clearance are explicit assumed budgets.
use super::*;
use crate::cycle::{Ledger, LegEnergy, ReleaseControl, Station, StationState};

pub const REQUEST_SCHEMA: &str = "osr-station-fleet-request/1";
#[derive(Debug, Clone, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct Request {
    pub schema: String,
    pub cases: Vec<FleetCase>,
}
#[derive(Debug, Clone, Deserialize, Serialize, PartialEq, Eq)]
#[serde(rename_all = "kebab-case")]
pub enum TrainRole {
    Active,
    Spare,
}
#[derive(Debug, Clone, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct Train {
    pub id: String,
    pub initial_station_id: String,
    pub initial_position_m: f64,
    pub ready_at_s: f64,
    pub role: TrainRole,
    pub initial_drive_temperature_c: Option<f64>,
}
#[derive(Debug, Clone, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct Departure {
    pub id: String,
    pub journey: Case,
    pub departure_station_id: String,
    pub arrival_station_id: String,
    pub departure_time_s: f64,
    pub departure_authorized: bool,
    pub capture_failed: bool,
    pub release_failed: bool,
    pub reset_failed: bool,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub requested_train_id: Option<String>,
}
#[derive(Debug, Clone, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct FleetCase {
    pub id: String,
    pub candidate_id: String,
    pub stations: Vec<Station>,
    pub release_control: ReleaseControl,
    pub trains: Vec<Train>,
    pub departures: Vec<Departure>,
    pub turnaround_s: f64,
    pub clearance_s: f64,
}
#[derive(Debug, Clone, Serialize)]
pub struct TrainState {
    pub id: String,
    pub role: TrainRole,
    pub station_id: Option<String>,
    pub initial_position_m: f64,
    pub ready_at_s: f64,
    pub in_transit: bool,
    pub pending_rescue: bool,
    pub drive_temperature_c: Option<f64>,
    pub temperature_time_s: f64,
}
#[derive(Debug, Clone, Serialize)]
pub struct RouteState {
    pub departure_station_id: String,
    pub arrival_station_id: String,
    pub occupied_until_s: f64,
    pub pending_rescue: bool,
}
#[derive(Debug, Clone, Serialize)]
pub struct FleetEvent {
    pub time_s: f64,
    pub kind: String,
    pub departure_id: Option<String>,
    pub train_id: Option<String>,
    pub station_id: Option<String>,
    pub reason: Option<String>,
    pub store_before_j: Option<f64>,
    pub store_after_j: Option<f64>,
}
#[derive(Debug, Clone, Serialize)]
pub struct DepartureResult {
    pub id: String,
    pub train_id: Option<String>,
    pub state: String,
    pub hold_reason: Option<String>,
    pub departure_station_id: String,
    pub arrival_station_id: String,
    pub departure_time_s: f64,
    pub arrival_time_s: Option<f64>,
    pub initial_position_m: Option<f64>,
    pub initial_drive_temperature_c: Option<f64>,
    pub actual_applied_case: Option<Case>,
    pub source_domain: Option<FeedbackDiagnostics>,
    pub journey: Option<ResultRow>,
    pub energy: LegEnergy,
    pub release_bypassed: bool,
    pub capture_bypassed: bool,
    pub recovery_reasons: Vec<String>,
    pub mechanical_steps: usize,
    pub thermal_result_basis: String,
}
#[derive(Debug, Clone, Serialize)]
pub struct FleetResult {
    pub id: String,
    pub candidate_id: String,
    pub state: String,
    pub requested_departures: usize,
    pub dispatched_departures: usize,
    pub normal_arrivals: usize,
    pub blocked_departures: usize,
    pub active_trains: usize,
    pub spare_trains: usize,
    pub departures: Vec<DepartureResult>,
    pub station_states: Vec<StationState>,
    pub train_states: Vec<TrainState>,
    pub route_states: Vec<RouteState>,
    pub ledger: Ledger,
    pub events: Vec<FleetEvent>,
    pub simulation_end_time_s: f64,
    pub maximum_thermal_proxy_temperature_c: Option<f64>,
    pub numerical_thermal_limits_met: bool,
    pub schedule_numerical_complete: bool,
    pub terminal_dynamics_supported: bool,
    pub route_separation_qualified: bool,
    pub thermal_duty_verified: bool,
    pub auxiliary_duty_complete: bool,
    pub conditional: bool,
    pub physical_accepted: bool,
    pub engineering_accepted: bool,
    pub operating_release: bool,
    pub admitted_operating_map: bool,
    pub limitations: Vec<String>,
}
#[derive(Debug, Clone, Serialize)]
pub struct BatchResult {
    pub schema: &'static str,
    pub cases: Vec<FleetResult>,
}

use crate::cycle::{Leg, MechanicalStep, record_grid_motion};
use crate::cycle_release::ReleaseRuntime;
use std::cmp::Ordering;
use std::collections::BinaryHeap;
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
enum ResourceKind {
    Release,
    Capture,
    Reset,
}
#[derive(Debug, Clone, Copy)]
struct Owner {
    leg: usize,
    kind: ResourceKind,
}
struct Bank {
    state: StationState,
    owner: Option<Owner>,
    generation: u64,
}
#[derive(Debug, Clone)]
enum Action {
    Departure(usize),
    StepStart(usize, usize),
    StepEnd(usize, usize),
    Arrival(usize),
    ReleaseExit(usize),
    ResetDone(usize, u64),
    RouteClear(usize),
}
#[derive(Debug, Clone)]
struct Scheduled {
    time: f64,
    priority: u8,
    order: u64,
    action: Action,
}
impl PartialEq for Scheduled {
    fn eq(&self, other: &Self) -> bool {
        self.time == other.time && self.priority == other.priority && self.order == other.order
    }
}
impl Eq for Scheduled {}
impl Ord for Scheduled {
    fn cmp(&self, other: &Self) -> Ordering {
        other
            .time
            .total_cmp(&self.time)
            .then_with(|| other.priority.cmp(&self.priority))
            .then_with(|| other.order.cmp(&self.order))
    }
}
impl PartialOrd for Scheduled {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}
#[derive(Default)]
struct TransferStep {
    launch_j: f64,
    draw_j: f64,
    capture_j: f64,
    stored_j: f64,
    bypass_j: f64,
    stage_j: Vec<f64>,
    release_peak_n: f64,
    release_peak_w: f64,
    capture_peak_n: f64,
    capture_peak_w: f64,
    grid_peak_w: f64,
}
struct LiveLeg {
    result_index: usize,
    train: usize,
    dep: usize,
    arr: usize,
    leg: Leg,
    steps: Vec<MechanicalStep>,
    arrival_temperature: Option<f64>,
    allocator: ReleaseRuntime,
    pending: Option<TransferStep>,
    release_decided: bool,
    capture_decided: bool,
    release_owned: bool,
    capture_owned: bool,
    grid_j: f64,
    grid_loss_j: f64,
    grid_peak_w: f64,
    next_trace: f64,
}
struct Engine<'a> {
    input: &'a FleetCase,
    now: f64,
    queue: BinaryHeap<Scheduled>,
    serial: u64,
    banks: Vec<Bank>,
    trains: Vec<TrainState>,
    routes: Vec<RouteState>,
    results: Vec<DepartureResult>,
    live: Vec<LiveLeg>,
    events: Vec<FleetEvent>,
    ledger: Ledger,
    thermal_model: Option<Thermal>,
    maximum_temperature: Option<f64>,
}
fn station_valid(s: &Station, distance: f64) -> bool {
    let transfer = |q: &crate::cycle::Transfer| {
        nonneg(q.start_m)
            && pos(q.end_m)
            && q.end_m > q.start_m
            && q.end_m <= distance
            && nonneg(q.max_force_n)
            && nonneg(q.max_power_w)
    };
    !s.id.is_empty()
        && nonneg(s.initial_energy_j)
        && nonneg(s.store.capacity_j)
        && s.initial_energy_j <= s.store.capacity_j
        && pos(s.store.capture_efficiency)
        && s.store.capture_efficiency <= 1.
        && pos(s.store.release_efficiency)
        && s.store.release_efficiency <= 1.
        && nonneg(s.store.leakage_per_s)
        && transfer(&s.release)
        && !s.capture_stages.is_empty()
        && s.capture_stages.len() <= 16
        && s.capture_stages.iter().all(transfer)
        && s.capture_stages
            .windows(2)
            .all(|p| p[0].end_m <= p[1].start_m)
        && nonneg(s.reset.duration_s)
        && nonneg(s.reset.grid_energy_j)
        && nonneg(s.reset.grid_power_w)
        && (s.store.capacity_j > 0.
            || s.initial_energy_j == 0.
                && s.release.max_force_n == 0.
                && s.capture_stages.iter().all(|q| q.max_force_n == 0.))
}
fn thermal_same(a: &Option<Thermal>, b: &Option<Thermal>) -> bool {
    match (a, b) {
        (None, None) => true,
        (Some(a), Some(b)) => {
            a.capacity_j_k == b.capacity_j_k
                && a.heat_rejection_w_k == b.heat_rejection_w_k
                && a.ambient_c == b.ambient_c
                && a.maximum_c == b.maximum_c
        }
        _ => false,
    }
}
fn validate(c: &FleetCase) -> Result<(), String> {
    c.release_control.validate()?;
    if c.id.is_empty()
        || c.candidate_id.len() != 64
        || !c.candidate_id.bytes().all(|x| x.is_ascii_hexdigit())
        || c.stations.len() != 2
        || c.trains.is_empty()
        || c.trains.len() > 16
        || c.departures.is_empty()
        || c.departures.len() > 64
        || !nonneg(c.turnaround_s)
        || !pos(c.clearance_s)
    {
        return Err("Explicit same-candidate two-station fleet,1..16trains,1..64departures, turn and positive clearance budgets required".into());
    }
    let distance = c.departures[0].journey.distance_m;
    if c.stations[0].id == c.stations[1].id
        || c.stations.iter().any(|s| !station_valid(s, distance))
    {
        return Err("Distinct valid explicit station stores and transfer domains required".into());
    }
    let mut ids = HashSet::new();
    for t in &c.trains {
        if t.id.is_empty()
            || !ids.insert(t.id.clone())
            || !c.stations.iter().any(|s| s.id == t.initial_station_id)
            || !nonneg(t.initial_position_m)
            || t.initial_position_m > c.departures[0].journey.berth_tolerance_m
            || !nonneg(t.ready_at_s)
            || t.initial_drive_temperature_c
                .is_some_and(|v| !v.is_finite() || v < -273.15)
        {
            return Err("Unique explicitly located initial train states required".into());
        }
    }
    ids.clear();
    for d in &c.departures {
        valid(&d.journey)?;
        if d.id.is_empty()
            || !ids.insert(d.id.clone())
            || d.journey.candidate_id != c.candidate_id
            || d.journey.distance_m != distance
            || d.journey.control.is_none()
            || !nonneg(d.departure_time_s)
            || d.departure_time_s > 172800.
            || d.departure_station_id == d.arrival_station_id
            || !c.stations.iter().any(|s| s.id == d.departure_station_id)
            || !c.stations.iter().any(|s| s.id == d.arrival_station_id)
            || !thermal_same(&d.journey.thermal, &c.departures[0].journey.thermal)
            || d.requested_train_id
                .as_ref()
                .is_some_and(|id| !c.trains.iter().any(|t| &t.id == id))
        {
            return Err("Unique same-candidate bounded-feedback departures, common thermal/route domain and explicit time/station IDs required".into());
        }
    }
    Ok(())
}
impl<'a> Engine<'a> {
    fn push(&mut self, time: f64, priority: u8, action: Action) {
        self.serial += 1;
        self.queue.push(Scheduled {
            time,
            priority,
            order: self.serial,
            action,
        });
    }
    fn log(
        &mut self,
        time: f64,
        kind: &str,
        leg: Option<usize>,
        station: Option<usize>,
        reason: Option<String>,
        before: Option<f64>,
        after: Option<f64>,
    ) {
        let (dep, train) = leg.map_or((None, None), |i| {
            (
                Some(self.input.departures[self.live[i].result_index].id.clone()),
                Some(self.trains[self.live[i].train].id.clone()),
            )
        });
        self.events.push(FleetEvent {
            time_s: time,
            kind: kind.into(),
            departure_id: dep,
            train_id: train,
            station_id: station.map(|i| self.input.stations[i].id.clone()),
            reason,
            store_before_j: before,
            store_after_j: after,
        });
    }
    fn age_to(&mut self, time: f64) -> Result<(), String> {
        if time < self.now - 1e-8 {
            return Err("Fleet event time moved backwards".into());
        }
        let dt = (time - self.now).max(0.);
        for (bank, spec) in self.banks.iter_mut().zip(&self.input.stations) {
            let end = bank.state.energy_j * (-spec.store.leakage_per_s * dt).exp();
            self.ledger.storage_leakage_j += bank.state.energy_j - end;
            bank.state.energy_j = end;
        }
        self.now = time;
        Ok(())
    }
    fn train_temperature_at(&self, index: usize, time: f64) -> Option<f64> {
        let state = &self.trains[index];
        match (state.drive_temperature_c, self.thermal_model.as_ref()) {
            (Some(t), Some(model)) => Some(temperature(
                t,
                (time - state.temperature_time_s).max(0.),
                0.,
                model,
            )),
            (t, _) => t,
        }
    }
    fn dispatch(&mut self, index: usize) -> Result<(), String> {
        let d = &self.input.departures[index];
        let dep = self
            .input
            .stations
            .iter()
            .position(|s| s.id == d.departure_station_id)
            .unwrap();
        let arr = 1 - dep;
        let route = &self.routes[dep];
        let eligible = |i: usize| {
            let t = &self.trains[i];
            t.role == TrainRole::Active
                && !t.in_transit
                && !t.pending_rescue
                && t.station_id.as_ref() == Some(&d.departure_station_id)
                && t.ready_at_s <= self.now + 1e-9
        };
        let selected = if let Some(id) = &d.requested_train_id {
            self.trains
                .iter()
                .position(|t| &t.id == id)
                .filter(|i| eligible(*i))
        } else {
            (0..self.trains.len())
                .filter(|i| eligible(*i))
                .min_by(|a, b| {
                    self.trains[*a]
                        .ready_at_s
                        .total_cmp(&self.trains[*b].ready_at_s)
                        .then_with(|| self.trains[*a].id.cmp(&self.trains[*b].id))
                })
        };
        let reason = if !d.departure_authorized {
            Some("No positive departure authorization")
        } else if route.pending_rescue {
            Some("Dedicated route remains occupied by failed movement pending rescue")
        } else if route.occupied_until_s > self.now + 1e-9 {
            Some("Dedicated route arrival/clearance budget is still occupied")
        } else if selected.is_none() {
            Some(
                "No eligible active train at the station after arrival, dwell and turn budgets; spares are excluded",
            )
        } else {
            None
        };
        let mut result=DepartureResult{id:d.id.clone(),train_id:selected.map(|i|self.trains[i].id.clone()),state:"departure-held".into(),hold_reason:reason.map(str::to_string),departure_station_id:d.departure_station_id.clone(),arrival_station_id:d.arrival_station_id.clone(),departure_time_s:self.now,arrival_time_s:None,initial_position_m:None,initial_drive_temperature_c:None,actual_applied_case:None,source_domain:None,journey:None,energy:LegEnergy::default(),release_bypassed:false,capture_bypassed:false,recovery_reasons:vec![],mechanical_steps:0,thermal_result_basis:"Conservative full-grid drive-loss RC proxy; actual allocation losses separate; hardware calibration and store thermal limits unverified".into()};
        if reason.is_some() {
            self.results[index] = result;
            return Ok(());
        }
        let train = selected.unwrap();
        let initial_x = self.trains[train].initial_position_m;
        let initial_temp = self.train_temperature_at(train, self.now);
        result.initial_position_m = Some(initial_x);
        result.initial_drive_temperature_c = initial_temp;
        let mut applied = d.journey.clone();
        applied.id = format!("{}/{}", d.id, self.trains[train].id);
        if let Some(t) = applied.thermal.as_mut() {
            let Some(initial) = initial_temp else {
                result.hold_reason = Some(
                    "Initial train drive temperature unknown under the declared thermal model"
                        .into(),
                );
                self.results[index] = result;
                return Ok(());
            };
            t.initial_c = initial;
        }
        result.actual_applied_case = Some(applied.clone());
        let domain = feedback::domain_screen(&applied, applied.control.as_ref().unwrap())?;
        result.source_domain = Some(domain.clone());
        if !domain.bounds_valid || applied.drive.is_none() {
            result.hold_reason = Some(if applied.drive.is_none() {
                "Available source drive profile absent".into()
            } else {
                domain.bound_violations.join("; ")
            });
            self.results[index] = result;
            return Ok(());
        }
        let motion = record_grid_motion(&applied, initial_x, &self.input.release_control)?;
        if motion
            .journey
            .control
            .as_ref()
            .is_none_or(|p| !p.bounds_valid || p.departure_held)
            || motion.steps.is_empty()
        {
            result.hold_reason = Some(motion.journey.hold_reason.clone().unwrap_or(
                "Declared source/controller/thermal domain does not support departure".into(),
            ));
            result.journey = Some(motion.journey);
            self.results[index] = result;
            return Ok(());
        }
        result.state = "dispatched".into();
        result.hold_reason = None;
        result.arrival_time_s = Some(self.now + motion.journey.elapsed_s);
        result.mechanical_steps = motion.steps.len();
        result.energy.capture_stage_work_j =
            vec![0.; self.input.stations[arr].capture_stages.len()];
        result.journey = Some(motion.journey);
        self.results[index] = result;
        self.trains[train].in_transit = true;
        self.trains[train].station_id = None;
        self.trains[train].drive_temperature_c = initial_temp;
        self.trains[train].temperature_time_s = self.now;
        self.routes[dep].occupied_until_s = self.now
            + self.results[index].journey.as_ref().unwrap().elapsed_s
            + self.input.clearance_s;
        let leg = Leg {
            train_id: self.trains[train].id.clone(),
            journey: applied,
            departure_station_id: d.departure_station_id.clone(),
            arrival_station_id: d.arrival_station_id.clone(),
            departure_time_s: self.now,
            departure_authorized: true,
            capture_failed: d.capture_failed,
            release_failed: d.release_failed,
            reset_failed: d.reset_failed,
        };
        let live_index = self.live.len();
        let arrival_time = self.results[index].arrival_time_s.unwrap();
        let steps = motion.steps;
        let release_end = self.input.stations[dep].release.end_m;
        let mut release_exit = None;
        for (i, s) in steps.iter().enumerate() {
            self.push(self.now + s.start_s, 5, Action::StepStart(live_index, i));
            self.push(
                self.now + (s.start_s + s.h),
                0,
                Action::StepEnd(live_index, i),
            );
            if release_exit.is_none() && s.x < release_end && s.x + s.dx >= release_end {
                let a = (s.v1 - s.v0) / s.h;
                let gap = release_end - s.x;
                let within =
                    2. * gap / (s.v0 + (s.v0 * s.v0 + 2. * a * gap).max(0.).sqrt()).max(1e-12);
                release_exit = Some(self.now + s.start_s + within.min(s.h));
            }
        }
        self.live.push(LiveLeg {
            result_index: index,
            train,
            dep,
            arr,
            leg,
            steps,
            arrival_temperature: motion.arrival_temperature_c,
            allocator: ReleaseRuntime::new(self.input.release_control.clone()),
            pending: None,
            release_decided: false,
            capture_decided: false,
            release_owned: false,
            capture_owned: false,
            grid_j: 0.,
            grid_loss_j: 0.,
            grid_peak_w: 0.,
            next_trace: 0.,
        });
        // Exit ownership is released at the first accepted step endpoint after
        // the crossing, so its final transaction commits before any other owner.
        if let Some(time) = release_exit {
            let endpoint = self.live[live_index]
                .steps
                .iter()
                .find(|s| {
                    self.live[live_index].leg.departure_time_s + (s.start_s + s.h) >= time - 1e-9
                })
                .map(|s| self.live[live_index].leg.departure_time_s + (s.start_s + s.h))
                .unwrap_or(time);
            self.push(endpoint, 1, Action::ReleaseExit(live_index));
        }
        self.push(arrival_time, 2, Action::Arrival(live_index));
        self.log(
            self.now,
            "departure-dispatched",
            Some(live_index),
            Some(dep),
            None,
            None,
            None,
        );
        Ok(())
    }
    fn acquire(&mut self, leg_index: usize, station: usize, kind: ResourceKind) -> bool {
        let bank = &self.banks[station];
        let available = bank.owner.is_none()
            && bank.state.ready
            && bank.state.ready_at_s <= self.now + 1e-9
            && bank.state.locked_until_s <= self.now + 1e-9;
        if available {
            self.banks[station].owner = Some(Owner {
                leg: leg_index,
                kind,
            });
            self.banks[station].state.ready = false;
            self.log(
                self.now,
                if kind == ResourceKind::Release {
                    "launch-resource-acquired"
                } else {
                    "capture-resource-acquired"
                },
                Some(leg_index),
                Some(station),
                None,
                None,
                None,
            );
        }
        available
    }
    fn start_step(&mut self, li: usize, si: usize) -> Result<(), String> {
        let (dep, arr, result_index) = {
            let l = &self.live[li];
            (l.dep, l.arr, l.result_index)
        };
        let step = self.live[li].steps[si].clone();
        let release = &self.input.stations[dep].release;
        let release_attempt = !self.live[li].release_decided
            && step.x + step.dx > release.start_m
            && step.x < release.end_m;
        if release_attempt {
            let requested = !self.live[li].leg.release_failed
                && !step.fault
                && release.max_force_n > 0.
                && self.banks[dep].state.energy_j > 0.;
            let owned = requested && self.acquire(li, dep, ResourceKind::Release);
            self.live[li].release_decided = true;
            self.live[li].release_owned = owned;
            if !owned {
                self.results[result_index].release_bypassed = true;
                self.results[result_index].recovery_reasons.push("Departure store absent, empty, failed, locked or busy; independently rated grid drive supplies the requested motion".into());
            }
        }
        let capture_attempt = !self.live[li].capture_decided
            && step.brake_n > 0.
            && self.input.stations[arr]
                .capture_stages
                .iter()
                .any(|q| step.x + step.dx > q.start_m && step.x < q.end_m);
        if capture_attempt {
            let requested =
                !self.live[li].leg.capture_failed && self.input.stations[arr].store.capacity_j > 0.;
            let owned = requested && self.acquire(li, arr, ResourceKind::Capture);
            self.live[li].capture_decided = true;
            self.live[li].capture_owned = owned;
            if !owned {
                self.results[result_index].capture_bypassed = true;
                self.results[result_index].recovery_reasons.push("Receiving module absent, failed, locked or busy; actual independent friction braking retains the full retarding demand".into());
            }
        }
        let live = &mut self.live[li];
        let mut allocation_leg = live.leg.clone();
        allocation_leg.release_failed |= !live.release_owned;
        let allocation = live.allocator.allocate(
            &self.input.stations[dep],
            &allocation_leg,
            self.banks[dep].state.energy_j,
            step.x,
            step.v0,
            step.v1,
            step.dx,
            step.h,
            step.traction_n,
            step.fault,
        );
        let mut pending = TransferStep {
            launch_j: allocation.work_j,
            draw_j: allocation.work_j / self.input.stations[dep].store.release_efficiency,
            release_peak_n: allocation.peak_force_n,
            release_peak_w: allocation.peak_power_w,
            grid_peak_w: live.allocator.last_grid_peak_power_w,
            stage_j: vec![0.; self.input.stations[arr].capture_stages.len()],
            ..Default::default()
        };
        let spec = &self.input.stations[arr];
        let mut room = (spec.store.capacity_j
            - self.banks[arr].state.energy_j * (-spec.store.leakage_per_s * step.h).exp())
        .max(0.);
        for (i, q) in spec.capture_stages.iter().enumerate() {
            let overlap = ((step.x + step.dx).min(q.end_m) - step.x.max(q.start_m)).max(0.);
            let potential = step
                .brake_n
                .min(q.max_force_n)
                .min(q.max_power_w / step.v0.max(step.v1).max(1e-12));
            let captured = if live.capture_owned {
                potential.min(room / (spec.store.capture_efficiency * overlap).max(1e-12)) * overlap
            } else {
                0.
            };
            pending.stage_j[i] = captured;
            pending.capture_j += captured;
            pending.bypass_j += potential * overlap - captured;
            let force = if overlap > 0. { captured / overlap } else { 0. };
            pending.capture_peak_n = pending.capture_peak_n.max(force);
            pending.capture_peak_w = pending.capture_peak_w.max(force * step.v0.max(step.v1));
            room = (room - captured * spec.store.capture_efficiency).max(0.);
        }
        pending.stored_j = pending.capture_j * spec.store.capture_efficiency;
        live.pending = Some(pending);
        Ok(())
    }
    fn end_step(&mut self, li: usize, si: usize) -> Result<(), String> {
        let live = &mut self.live[li];
        let step = &live.steps[si];
        let p = live
            .pending
            .take()
            .ok_or("A fleet transfer step ended without its causal start")?;
        let dep = live.dep;
        let arr = live.arr;
        let row = &mut self.results[live.result_index];
        if p.draw_j > self.banks[dep].state.energy_j + 1e-5
            || self.banks[arr].state.energy_j + p.stored_j
                > self.input.stations[arr].store.capacity_j + 1e-5
        {
            return Err("Causal shared-store step exceeded actual energy/capacity".into());
        }
        self.banks[dep].state.energy_j = (self.banks[dep].state.energy_j - p.draw_j).max(0.);
        self.banks[arr].state.energy_j += p.stored_j;
        let e = &mut row.energy;
        e.capture_work_j += p.capture_j;
        e.stored_capture_j += p.stored_j;
        e.capture_loss_j += p.capture_j - p.stored_j;
        e.bypassed_capture_work_j += p.bypass_j;
        e.released_from_store_j += p.draw_j;
        e.delivered_launch_work_j += p.launch_j;
        e.release_loss_j += p.draw_j - p.launch_j;
        for (a, b) in e.capture_stage_work_j.iter_mut().zip(&p.stage_j) {
            *a += b;
        }
        e.maximum_release_force_n = e.maximum_release_force_n.max(p.release_peak_n);
        e.maximum_release_power_w = e.maximum_release_power_w.max(p.release_peak_w);
        e.maximum_capture_force_n = e.maximum_capture_force_n.max(p.capture_peak_n);
        e.maximum_capture_power_w = e.maximum_capture_power_w.max(p.capture_peak_w);
        let efficiency = live
            .leg
            .journey
            .drive
            .as_ref()
            .unwrap()
            .electrical_efficiency;
        let work = step.traction_n * step.dx;
        let grid = (work - p.launch_j) / efficiency;
        live.grid_j += grid;
        live.grid_loss_j += grid - (work - p.launch_j);
        live.grid_peak_w = live.grid_peak_w.max(p.grid_peak_w / efficiency);
        live.allocator.observe_motion(
            step.start_s + step.h,
            step.x,
            step.v0,
            step.v1,
            step.h,
            step.previous_h,
            step.previous_acceleration,
            step.acceleration,
            step.traction_n,
            step.brake_n,
        );
        e.release_control = Some(live.allocator.diagnostics.clone());
        let emit_trace = step.start_s + step.h >= live.next_trace;
        if emit_trace {
            e.trace.push(crate::cycle::RecoveryPoint {
                time_s: step.start_s + step.h,
                position_m: step.x + step.dx,
                capture_n: if step.dx > 0. {
                    p.capture_j / step.dx
                } else {
                    0.
                },
                friction_n: step.brake_n
                    - if step.dx > 0. {
                        p.capture_j / step.dx
                    } else {
                        0.
                    },
                store_traction_n: if step.dx > 0. {
                    p.launch_j / step.dx
                } else {
                    0.
                },
                departure_store_j: self.banks[dep].state.energy_j,
                arrival_store_j: self.banks[arr].state.energy_j,
                release_control: live.allocator.last_sample.clone(),
            });
            live.next_trace = step.start_s + step.h + 1.;
        }
        if emit_trace && p.capture_j > 0. {
            self.log(
                self.now,
                "capture-work-committed",
                Some(li),
                Some(arr),
                None,
                Some(self.banks[arr].state.energy_j - p.stored_j),
                Some(self.banks[arr].state.energy_j),
            );
        }
        if emit_trace && p.draw_j > 0. {
            self.log(
                self.now,
                "stored-launch-work-committed",
                Some(li),
                Some(dep),
                None,
                Some(self.banks[dep].state.energy_j + p.draw_j),
                Some(self.banks[dep].state.energy_j),
            );
        }
        Ok(())
    }
    fn reset(&mut self, li: usize, station: usize, lock_until: f64) -> Result<(), String> {
        let spec = &self.input.stations[station];
        let failed = self.live[li].leg.reset_failed
            || spec.reset.grid_energy_j > spec.reset.duration_s * spec.reset.grid_power_w + 1e-8;
        self.banks[station].state.locked_until_s = lock_until;
        self.banks[station].state.ready_at_s = (self.now + spec.reset.duration_s).max(lock_until);
        self.banks[station].generation += 1;
        let generation = self.banks[station].generation;
        if failed {
            self.ledger.unperformed_reset_grid_energy_j += spec.reset.grid_energy_j;
            self.banks[station].state.ready = false;
            self.banks[station].owner = None;
            self.log(
                self.now,
                "recovery-reset-failed-grid-service-remains-independent",
                Some(li),
                Some(station),
                None,
                None,
                None,
            );
        } else {
            self.banks[station].owner = Some(Owner {
                leg: li,
                kind: ResourceKind::Reset,
            });
            self.push(
                self.banks[station].state.ready_at_s,
                1,
                Action::ResetDone(station, generation),
            );
        }
        Ok(())
    }
    fn release_exit(&mut self, li: usize) -> Result<(), String> {
        let dep = self.live[li].dep;
        if self.banks[dep]
            .owner
            .is_some_and(|o| o.leg == li && o.kind == ResourceKind::Release)
        {
            if self.results[self.live[li].result_index]
                .energy
                .delivered_launch_work_j
                > 0.
            {
                self.reset(li, dep, self.now)?;
            } else {
                self.banks[dep].owner = None;
                self.banks[dep].state.ready = true;
            }
            self.live[li].release_owned = false;
        }
        Ok(())
    }
    fn arrival(&mut self, li: usize) -> Result<(), String> {
        let (result_index, train, dep, arr) = {
            let l = &self.live[li];
            (l.result_index, l.train, l.dep, l.arr)
        };
        let live = &mut self.live[li];
        let row = &mut self.results[result_index];
        let j = row.journey.as_mut().unwrap();
        j.grid_energy_j = live.grid_j;
        j.drive_loss_j = live.grid_loss_j;
        j.maximum_grid_power_w = live.grid_peak_w;
        j.brake_heat_j -= row.energy.capture_work_j;
        j.energy_residual_j = j.traction_work_j + j.grade_work_j
            - j.resistance_work_j
            - j.external_resistance_work_j
            - j.brake_heat_j
            - row.energy.capture_work_j
            - j.detached_reset_kinetic_energy_j
            - j.final_kinetic_energy_j;
        j.limitations.push("Fleet thermal state uses the conservative full-grid loss RC proxy, while reported grid energy/loss uses actual store substitution. No hardware thermal qualification".into());
        self.ledger.grid_traction_energy_j += j.grid_energy_j;
        self.ledger.drive_conversion_loss_j += j.drive_loss_j;
        self.ledger.train_traction_work_j += j.traction_work_j;
        self.ledger.friction_brake_heat_j += j.brake_heat_j;
        self.ledger.resistance_work_j += j.resistance_work_j;
        self.ledger.external_resistance_work_j += j.external_resistance_work_j;
        self.ledger.grade_work_j += j.grade_work_j;
        self.ledger.detached_reset_kinetic_energy_j += j.detached_reset_kinetic_energy_j;
        self.ledger.final_train_kinetic_energy_j += j.final_kinetic_energy_j;
        self.ledger.auxiliary_load_energy_j += j.auxiliary_energy_j;
        self.ledger.capture_work_j += row.energy.capture_work_j;
        self.ledger.stored_capture_j += row.energy.stored_capture_j;
        self.ledger.capture_loss_j += row.energy.capture_loss_j;
        self.ledger.bypassed_capture_work_j += row.energy.bypassed_capture_work_j;
        self.ledger.released_from_store_j += row.energy.released_from_store_j;
        self.ledger.delivered_launch_work_j += row.energy.delivered_launch_work_j;
        self.ledger.release_loss_j += row.energy.release_loss_j;
        self.maximum_temperature = match (self.maximum_temperature, j.maximum_temperature_c) {
            (Some(a), Some(b)) => Some(a.max(b)),
            (a, b) => a.or(b),
        };
        self.trains[train].drive_temperature_c = live.arrival_temperature;
        self.trains[train].temperature_time_s = self.now;
        self.trains[train].in_transit = false;
        if j.normal_numerical_arrival {
            row.state = "arrived".into();
            self.trains[train].station_id = Some(self.input.stations[arr].id.clone());
            self.trains[train].initial_position_m =
                (live.leg.journey.distance_m - j.final_position_m).max(0.);
            self.trains[train].ready_at_s =
                self.now + live.leg.journey.dwell_s + self.input.turnaround_s;
            self.routes[dep].occupied_until_s = self.now + self.input.clearance_s;
            self.push(
                self.routes[dep].occupied_until_s,
                1,
                Action::RouteClear(dep),
            );
            if self.banks[arr]
                .owner
                .is_some_and(|o| o.leg == li && o.kind == ResourceKind::Capture)
            {
                self.reset(li, arr, self.now + self.live[li].leg.journey.dwell_s)?;
                self.live[li].capture_owned = false;
            }
            self.log(
                self.now,
                "normal-arrival-awaiting-dwell-and-terminal-budget",
                Some(li),
                Some(arr),
                None,
                None,
                None,
            );
        } else {
            row.state = "journey-held".into();
            row.hold_reason=Some("Actual motion failed its declared arrival; dedicated route stays occupied pending rescue".into());
            self.trains[train].pending_rescue = true;
            self.trains[train].station_id = None;
            self.routes[dep].pending_rescue = true;
            for station in [dep, arr] {
                if self.banks[station].owner.is_some_and(|o| o.leg == li) {
                    self.ledger.unperformed_reset_grid_energy_j +=
                        self.input.stations[station].reset.grid_energy_j;
                    self.banks[station].state.ready = false;
                }
            }
            self.log(
                self.now,
                "failed-movement-route-retained-pending-rescue",
                Some(li),
                None,
                None,
                None,
                None,
            );
        }
        self.live[li].steps.clear();
        Ok(())
    }
    fn run(mut self) -> Result<FleetResult, String> {
        while let Some(event) = self.queue.pop() {
            self.age_to(event.time)?;
            match event.action {
                Action::Departure(i) => self.dispatch(i)?,
                Action::StepStart(l, s) => self.start_step(l, s)?,
                Action::StepEnd(l, s) => self.end_step(l, s)?,
                Action::Arrival(l) => self.arrival(l)?,
                Action::ReleaseExit(l) => self.release_exit(l)?,
                Action::ResetDone(s, g) => {
                    if self.banks[s].generation == g
                        && self.banks[s]
                            .owner
                            .is_some_and(|o| o.kind == ResourceKind::Reset)
                    {
                        let li = self.banks[s].owner.unwrap().leg;
                        self.ledger.reset_grid_energy_j +=
                            self.input.stations[s].reset.grid_energy_j;
                        self.banks[s].owner = None;
                        self.banks[s].state.ready = true;
                        self.log(
                            self.now,
                            "recovery-reset-complete",
                            Some(li),
                            Some(s),
                            None,
                            None,
                            None,
                        );
                    }
                }
                Action::RouteClear(s) => {
                    if !self.routes[s].pending_rescue
                        && self.routes[s].occupied_until_s <= self.now + 1e-9
                    {
                        self.log(
                            self.now,
                            "dedicated-route-clearance-budget-complete",
                            None,
                            Some(s),
                            None,
                            None,
                            None,
                        );
                    }
                }
            }
        }
        for i in 0..self.trains.len() {
            let t = self.train_temperature_at(i, self.now);
            self.trains[i].drive_temperature_c = t;
            self.trains[i].temperature_time_s = self.now;
        }
        self.ledger.final_store_j = self.banks.iter().map(|b| b.state.energy_j).sum();
        self.ledger.storage_balance_residual_j = self.ledger.initial_store_j
            + self.ledger.stored_capture_j
            - self.ledger.released_from_store_j
            - self.ledger.storage_leakage_j
            - self.ledger.final_store_j;
        let l = &self.ledger;
        self.ledger.train_and_storage_balance_residual_j =
            l.initial_store_j + l.grid_traction_energy_j + l.grade_work_j
                - l.final_store_j
                - l.drive_conversion_loss_j
                - l.capture_loss_j
                - l.release_loss_j
                - l.storage_leakage_j
                - l.friction_brake_heat_j
                - l.resistance_work_j
                - l.external_resistance_work_j
                - l.detached_reset_kinetic_energy_j
                - l.final_train_kinetic_energy_j;
        let dispatched = self
            .results
            .iter()
            .filter(|r| r.state != "departure-held")
            .count();
        let arrivals = self.results.iter().filter(|r| r.state == "arrived").count();
        let scale = self
            .ledger
            .grid_traction_energy_j
            .max(self.ledger.initial_store_j)
            .max(self.ledger.grade_work_j.abs())
            .max(1.);
        let energy_valid = self.ledger.storage_balance_residual_j.abs() <= 1e-6 * scale
            && self.ledger.train_and_storage_balance_residual_j.abs() <= 1e-6 * scale;
        let complete = arrivals == self.input.departures.len() && energy_valid;
        let thermal = self
            .thermal_model
            .as_ref()
            .is_some_and(|m| self.maximum_temperature.is_some_and(|t| t <= m.maximum_c));
        Ok(FleetResult{id:self.input.id.clone(),candidate_id:self.input.candidate_id.clone(),state:if !energy_valid{"numerical-energy-held"}else if complete{"schedule-numerically-complete"}else{"schedule-held"}.into(),requested_departures:self.input.departures.len(),dispatched_departures:dispatched,normal_arrivals:arrivals,blocked_departures:self.input.departures.len()-dispatched,active_trains:self.trains.iter().filter(|t|t.role==TrainRole::Active).count(),spare_trains:self.trains.iter().filter(|t|t.role==TrainRole::Spare).count(),departures:self.results,station_states:self.banks.into_iter().map(|b|b.state).collect(),train_states:self.trains,route_states:self.routes,ledger:self.ledger,events:self.events,simulation_end_time_s:self.now,maximum_thermal_proxy_temperature_c:self.maximum_temperature,numerical_thermal_limits_met:thermal,schedule_numerical_complete:complete,terminal_dynamics_supported:false,route_separation_qualified:false,thermal_duty_verified:false,auxiliary_duty_complete:false,conditional:true,physical_accepted:false,engineering_accepted:false,operating_release:false,admitted_operating_map:false,limitations:vec![
            "Shared-bank transactions commit at accepted mechanical-step endpoints under exclusive resource ownership. Capture cannot credit an earlier launch; ready/locked/busy recovery bypasses to independent grid/friction".into(),
            "Only grid-substitution mode is supported; exact mechanical steps are generated under independently available grid ratings and conservative full-grid thermal losses before shared-store accounting".into(),
            "Terminal turn/staging and dedicated-route clearance are explicit time budgets, not verified finite-train geometry, interlocking, passenger dwell, manoeuvre dynamics or operating protection".into(),
            "Actual stop offsets are carried to the next reverse departure. Initially staged trains/positions are a dispatch abstraction, not demonstrated simultaneous platform/CAD placements; spares never supply nominal automatic service".into(),
            "Per-train drive RC state carries with passive idle cooling and conservative full-grid losses. Real current/voltage, contact, cooling, station-store temperatures and continuous thermal duty remain unverified".into(),
            "Auxiliary energy is the supplied journey/dwell subtotal only; spare/depot/terminal conditioning and service-battery charging remain separate required accounts, not zero".into(),
        ]})
    }
}
pub fn evaluate(c: &FleetCase) -> Result<FleetResult, String> {
    validate(c)?;
    let stations = c
        .stations
        .iter()
        .map(|s| Bank {
            state: StationState {
                id: s.id.clone(),
                energy_j: s.initial_energy_j,
                ready: true,
                ready_at_s: 0.,
                locked_until_s: 0.,
            },
            owner: None,
            generation: 0,
        })
        .collect();
    let trains = c
        .trains
        .iter()
        .map(|t| TrainState {
            id: t.id.clone(),
            role: t.role.clone(),
            station_id: Some(t.initial_station_id.clone()),
            initial_position_m: t.initial_position_m,
            ready_at_s: t.ready_at_s,
            in_transit: false,
            pending_rescue: false,
            drive_temperature_c: t.initial_drive_temperature_c,
            temperature_time_s: 0.,
        })
        .collect();
    let mut engine = Engine {
        input: c,
        now: 0.,
        queue: BinaryHeap::new(),
        serial: 0,
        banks: stations,
        trains,
        routes: vec![
            RouteState {
                departure_station_id: c.stations[0].id.clone(),
                arrival_station_id: c.stations[1].id.clone(),
                occupied_until_s: 0.,
                pending_rescue: false,
            },
            RouteState {
                departure_station_id: c.stations[1].id.clone(),
                arrival_station_id: c.stations[0].id.clone(),
                occupied_until_s: 0.,
                pending_rescue: false,
            },
        ],
        results: vec![],
        live: vec![],
        events: vec![],
        ledger: Ledger {
            initial_store_j: c.stations.iter().map(|s| s.initial_energy_j).sum(),
            ..Default::default()
        },
        thermal_model: c.departures[0].journey.thermal.clone(),
        maximum_temperature: c
            .trains
            .iter()
            .filter_map(|t| t.initial_drive_temperature_c)
            .reduce(f64::max),
    };
    engine.results = (0..c.departures.len())
        .map(|i| DepartureResult {
            id: c.departures[i].id.clone(),
            train_id: None,
            state: "pending".into(),
            hold_reason: None,
            departure_station_id: c.departures[i].departure_station_id.clone(),
            arrival_station_id: c.departures[i].arrival_station_id.clone(),
            departure_time_s: c.departures[i].departure_time_s,
            arrival_time_s: None,
            initial_position_m: None,
            initial_drive_temperature_c: None,
            actual_applied_case: None,
            source_domain: None,
            journey: None,
            energy: LegEnergy::default(),
            release_bypassed: false,
            capture_bypassed: false,
            recovery_reasons: vec![],
            mechanical_steps: 0,
            thermal_result_basis: "Not executed".into(),
        })
        .collect();
    for (i, d) in c.departures.iter().enumerate() {
        engine.push(d.departure_time_s, 4, Action::Departure(i));
    }
    engine.run()
}
pub fn execute(q: Request) -> Result<BatchResult, String> {
    if q.schema != REQUEST_SCHEMA || q.cases.is_empty() || q.cases.len() > 64 {
        return Err("Explicit fleet schema and1..64cases required".into());
    }
    let mut ids = HashSet::new();
    let mut cases = vec![];
    for c in q.cases {
        if !ids.insert(c.id.clone()) {
            return Err("Duplicate fleet case ID".into());
        }
        cases.push(evaluate(&c)?);
    }
    Ok(BatchResult {
        schema: "osr-station-fleet-result/1",
        cases,
    })
}
