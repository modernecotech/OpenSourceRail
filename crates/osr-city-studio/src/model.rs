use std::collections::BTreeMap;

use serde::{Deserialize, Serialize};

#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct ProjectFile {
    pub project: ProjectIdentity,
    pub inputs: ProjectInputs,
    pub planning: PlanningAssumptions,
    #[serde(default)]
    pub routing: Option<RoutingSettings>,
    pub revision: RevisionPolicy,
}

#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct ProjectIdentity {
    pub schema_version: u32,
    pub id: String,
    pub slug: String,
    pub name: String,
    pub country: String,
    pub default_branch: String,
}

#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct ProjectInputs {
    pub base_design: String,
    pub corridor_geojson: String,
    pub simulator_scenario: String,
    pub network_overrides: String,
    pub service_plan: String,
    pub source_lock: String,
}

#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct PlanningAssumptions {
    pub passenger_capacity_per_train: u32,
    pub average_speed_kmh: f64,
    pub station_dwell_min: f64,
    pub terminal_turnaround_min: f64,
    pub geometry_regeneration_radius_m: f64,
}

#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct RoutingSettings {
    pub sidecar: String,
    pub slug: String,
    pub source_ids: Vec<String>,
    #[serde(default = "default_demand_weight")]
    pub demand_weight: f32,
    #[serde(default = "default_route_margin_m")]
    pub search_margin_m: f64,
    #[serde(default = "default_endpoint_snap_m")]
    pub endpoint_snap_m: f64,
}

fn default_demand_weight() -> f32 {
    5.0
}

fn default_route_margin_m() -> f64 {
    2_500.0
}

fn default_endpoint_snap_m() -> f64 {
    500.0
}

#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct RevisionPolicy {
    pub policy: String,
    pub tag_prefix: String,
    pub require_clean_source_locks: bool,
    pub require_passing_validation: bool,
}

#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct BaseDesign {
    pub city: BaseCity,
    pub lines: Vec<BaseLine>,
    pub stations: Vec<BaseStation>,
}

#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct BaseCity {
    pub slug: String,
    pub country: String,
    pub population: u64,
    pub centroid_lat: f64,
    pub centroid_lon: f64,
}

#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct BaseLine {
    pub name: String,
    pub shape: String,
    pub length_m: f64,
}

#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct BaseStation {
    pub id: String,
    pub line: String,
    pub lat: f64,
    pub lon: f64,
    pub s_m: f64,
    #[serde(default)]
    pub anchor_name: Option<String>,
    #[serde(default)]
    pub archetype: Option<String>,
}

#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct OverrideFile {
    pub schema_version: u32,
    #[serde(default)]
    pub manual_lines: Vec<ManualLine>,
    #[serde(default)]
    pub stations: Vec<StationOverride>,
    #[serde(default)]
    pub manual_stations: Vec<ManualStation>,
    #[serde(default)]
    pub line_control_points: Vec<LineControlPoint>,
}

#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct ManualLine {
    pub id: String,
    pub name: String,
    pub state: IntentState,
    pub shape: String,
    pub points: Vec<GeoPoint>,
    #[serde(default = "direct_routing_method")]
    pub routing_method: String,
    #[serde(default)]
    pub routing_source_ids: Vec<String>,
    #[serde(default)]
    pub demand_weight: Option<f32>,
    #[serde(default)]
    pub reason: String,
}

fn direct_routing_method() -> String {
    "direct".to_string()
}

#[derive(Clone, Copy, Debug, Deserialize, Serialize)]
pub struct GeoPoint {
    pub lat: f64,
    pub lon: f64,
}

#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct StationOverride {
    pub id: String,
    pub state: IntentState,
    #[serde(default)]
    pub lat: Option<f64>,
    #[serde(default)]
    pub lon: Option<f64>,
    #[serde(default)]
    pub reason: String,
}

#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct ManualStation {
    pub id: String,
    pub name: String,
    pub line: String,
    pub state: IntentState,
    pub source_lat: f64,
    pub source_lon: f64,
    pub source_s_m: f64,
    pub lat: f64,
    pub lon: f64,
    pub archetype: String,
    #[serde(default)]
    pub reason: String,
}

#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct LineControlPoint {
    pub id: String,
    pub line: String,
    pub state: IntentState,
    pub source_lat: f64,
    pub source_lon: f64,
    pub lat: f64,
    pub lon: f64,
    pub influence_m: f64,
    #[serde(default)]
    pub reason: String,
}

#[derive(Clone, Copy, Debug, Deserialize, Serialize, PartialEq, Eq)]
#[serde(rename_all = "kebab-case")]
pub enum IntentState {
    Generated,
    Preferred,
    Locked,
    Manual,
    Retired,
}

#[derive(Clone, Debug, Deserialize, Serialize, PartialEq)]
pub struct ServicePlan {
    pub schema_version: u32,
    pub calendar: ServiceCalendar,
    pub day_types: Vec<DayType>,
    pub line_plans: Vec<LineServicePlan>,
}

#[derive(Clone, Debug, Deserialize, Serialize, PartialEq)]
pub struct ServiceCalendar {
    pub monday: String,
    pub tuesday: String,
    pub wednesday: String,
    pub thursday: String,
    pub friday: String,
    pub saturday: String,
    pub sunday: String,
}

impl ServiceCalendar {
    pub fn day_type_counts(&self) -> BTreeMap<String, u32> {
        let mut counts = BTreeMap::new();
        for day_type in [
            &self.monday,
            &self.tuesday,
            &self.wednesday,
            &self.thursday,
            &self.friday,
            &self.saturday,
            &self.sunday,
        ] {
            *counts.entry(day_type.clone()).or_insert(0) += 1;
        }
        counts
    }
}

#[derive(Clone, Debug, Deserialize, Serialize, PartialEq)]
pub struct DayType {
    pub id: String,
    pub name: String,
}

#[derive(Clone, Debug, Deserialize, Serialize, PartialEq)]
pub struct LineServicePlan {
    pub line: String,
    pub day_type: String,
    pub service_start: String,
    pub service_end: String,
    pub windows: Vec<ServiceWindow>,
}

#[derive(Clone, Debug, Deserialize, Serialize, PartialEq)]
pub struct ServiceWindow {
    pub from: String,
    pub to: String,
    pub headway_min: u32,
}

#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct SourceLock {
    pub schema_version: u32,
    pub sources: Vec<LockedSource>,
}

#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct LockedSource {
    pub id: String,
    pub kind: String,
    pub path: String,
    pub sha256: String,
}

#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct CompiledSnapshot {
    pub schema_version: u32,
    pub compiler_version: String,
    pub compiler_source_sha256: String,
    pub revision_id: String,
    pub content_sha256: String,
    pub input_sha256: String,
    pub parent_git_commit: Option<String>,
    pub project: ProjectIdentity,
    pub sources: Vec<ResolvedSource>,
    pub lines: Vec<CompiledLine>,
    pub stations: Vec<CompiledStation>,
    pub line_control_points: Vec<CompiledControlPoint>,
    #[serde(default)]
    pub service_plan: Option<ServicePlan>,
    pub service_metrics: Vec<ServiceMetric>,
    pub summary: SnapshotSummary,
    pub changes: Vec<StationChange>,
    pub findings: Vec<ValidationFinding>,
}

#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct ResolvedSource {
    pub id: String,
    pub kind: String,
    pub path: String,
    pub expected_sha256: String,
    pub actual_sha256: String,
    pub matches_lock: bool,
}

#[derive(Clone, Debug, Deserialize, Serialize, PartialEq)]
pub struct CompiledLine {
    pub id: String,
    #[serde(default)]
    pub name: String,
    pub shape: String,
    pub length_m: f64,
    pub station_count: usize,
    #[serde(default)]
    pub routing_method: String,
    #[serde(default)]
    pub routing_source_ids: Vec<String>,
    #[serde(default)]
    pub demand_weight: Option<f32>,
    #[serde(default = "generated_intent_state")]
    pub state: IntentState,
    #[serde(default)]
    pub reason: String,
}

fn generated_intent_state() -> IntentState {
    IntentState::Generated
}

#[derive(Clone, Debug, Deserialize, Serialize, PartialEq)]
pub struct CompiledStation {
    pub id: String,
    pub name: String,
    pub line: String,
    pub lat: f64,
    pub lon: f64,
    pub s_m: f64,
    pub archetype: String,
    pub state: IntentState,
    pub reason: String,
}

#[derive(Clone, Debug, Deserialize, Serialize, PartialEq)]
pub struct CompiledControlPoint {
    pub id: String,
    pub line: String,
    pub state: IntentState,
    pub source_lat: f64,
    pub source_lon: f64,
    pub lat: f64,
    pub lon: f64,
    pub influence_m: f64,
    pub distance_m: f64,
    pub reason: String,
}

#[derive(Clone, Debug, Deserialize, Serialize, PartialEq)]
pub struct ServiceMetric {
    pub line: String,
    pub day_type: String,
    pub cycle_time_min: f64,
    pub peak_fleet: u32,
    pub peak_capacity_pphpd: u32,
    pub daily_service_km: f64,
}

#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct SnapshotSummary {
    pub route_km: f64,
    pub station_count: usize,
    pub locked_station_count: usize,
    #[serde(default)]
    pub manual_station_count: usize,
    #[serde(default)]
    pub manual_line_count: usize,
    pub moved_station_count: usize,
    pub edited_line_count: usize,
    pub peak_fleet: u32,
    pub weekly_service_km: f64,
    pub validation_errors: usize,
    pub validation_warnings: usize,
}

#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct StationChange {
    pub id: String,
    pub line: String,
    pub from_lat: f64,
    pub from_lon: f64,
    pub to_lat: f64,
    pub to_lon: f64,
    pub distance_m: f64,
}

#[derive(Clone, Copy, Debug, Deserialize, Serialize, PartialEq, Eq)]
#[serde(rename_all = "lowercase")]
pub enum FindingSeverity {
    Error,
    Warning,
    Info,
}

#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct ValidationFinding {
    pub severity: FindingSeverity,
    pub code: String,
    pub message: String,
    pub object_id: Option<String>,
}

#[derive(Clone, Debug, Serialize)]
pub struct GitState {
    pub repository_root: Option<String>,
    pub branch: Option<String>,
    pub head: Option<String>,
    pub dirty: bool,
    pub changed_paths: Vec<String>,
}

#[derive(Clone, Debug, Serialize)]
pub struct ProjectView {
    pub snapshot: CompiledSnapshot,
    pub corridor: serde_json::Value,
    pub service_plan: ServicePlan,
    pub git: GitState,
    pub project_path: String,
    pub artifacts: Vec<StudioArtifact>,
}

#[derive(Clone, Debug, Serialize)]
pub struct StudioArtifact {
    pub category: String,
    pub label: String,
    pub path: String,
    pub exists: bool,
}

#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct JobRequest {
    #[serde(default)]
    pub day_type: Option<String>,
    #[serde(default)]
    pub line: Option<String>,
}

#[derive(Clone, Debug, Serialize)]
pub struct JobAdapterInfo {
    pub id: String,
    pub category: String,
    pub label: String,
    pub description: String,
}

#[derive(Clone, Debug, Deserialize, Serialize, PartialEq, Eq)]
#[serde(rename_all = "kebab-case")]
pub enum JobStatus {
    Queued,
    Running,
    Succeeded,
    Failed,
}

#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct JobArtifact {
    pub kind: String,
    pub path: String,
    pub sha256: String,
    pub size_bytes: u64,
}

#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct JobRecord {
    pub schema_version: u32,
    pub id: String,
    pub adapter: String,
    pub label: String,
    pub revision_id: String,
    pub status: JobStatus,
    pub progress_percent: u8,
    pub phase: String,
    pub command: Vec<String>,
    pub requested_day_type: Option<String>,
    pub requested_line: Option<String>,
    pub created_unix_ms: u128,
    #[serde(default)]
    pub started_unix_ms: Option<u128>,
    #[serde(default)]
    pub completed_unix_ms: Option<u128>,
    #[serde(default)]
    pub exit_code: Option<i32>,
    #[serde(default)]
    pub error: Option<String>,
    pub log_path: String,
    #[serde(default)]
    pub log_tail: String,
    #[serde(default)]
    pub artifacts: Vec<JobArtifact>,
}

#[derive(Clone, Debug, Deserialize)]
pub struct StationEdit {
    pub state: IntentState,
    pub lat: Option<f64>,
    pub lon: Option<f64>,
    #[serde(default)]
    pub name: Option<String>,
    #[serde(default)]
    pub archetype: Option<String>,
    #[serde(default)]
    pub reason: String,
}

#[derive(Clone, Debug, Deserialize)]
pub struct StationCreate {
    pub name: String,
    pub lat: f64,
    pub lon: f64,
    #[serde(default = "default_station_archetype")]
    pub archetype: String,
    #[serde(default)]
    pub reason: String,
}

#[derive(Clone, Debug, Deserialize)]
pub struct LineCreate {
    pub name: String,
    pub start_lat: f64,
    pub start_lon: f64,
    pub end_lat: f64,
    pub end_lon: f64,
    #[serde(default)]
    pub routing: LineRoutingPreference,
    #[serde(default)]
    pub reason: String,
}

#[derive(Clone, Copy, Debug, Default, Deserialize, Serialize, PartialEq, Eq)]
#[serde(rename_all = "kebab-case")]
pub enum LineRoutingPreference {
    #[default]
    Auto,
    DemandAware,
    Direct,
}

#[derive(Clone, Debug, Deserialize)]
pub struct LineEdit {
    pub name: String,
    pub state: IntentState,
    #[serde(default)]
    pub reason: String,
}

fn default_station_archetype() -> String {
    "standard".to_string()
}

#[derive(Clone, Debug, Deserialize)]
pub struct ControlPointCreate {
    pub source_lat: f64,
    pub source_lon: f64,
    #[serde(default)]
    pub reason: String,
}

#[derive(Clone, Debug, Deserialize)]
pub struct ControlPointEdit {
    pub state: IntentState,
    pub lat: f64,
    pub lon: f64,
    pub influence_m: f64,
    #[serde(default)]
    pub reason: String,
}

#[derive(Clone, Debug, Serialize)]
pub struct RevisionMaterialized {
    pub revision_id: String,
    pub path: String,
    pub suggested_branch: String,
    pub suggested_tag: String,
}

#[derive(Clone, Debug, Serialize)]
pub struct RevisionListItem {
    pub revision_id: String,
    pub parent_git_commit: Option<String>,
    pub compiler_version: String,
    pub content_sha256: String,
    pub route_km: f64,
    pub station_count: usize,
    pub peak_fleet: u32,
    pub weekly_service_km: f64,
    pub is_current: bool,
}

#[derive(Clone, Debug, Serialize)]
pub struct RevisionComparison {
    pub base_revision_id: String,
    pub candidate_revision_id: String,
    pub summary: RevisionSummaryDiff,
    pub stations: Vec<RevisionStationDiff>,
    pub controls: Vec<RevisionControlDiff>,
    pub lines: Vec<RevisionLineDiff>,
    pub services: Vec<RevisionServiceDiff>,
}

#[derive(Clone, Debug, Serialize)]
pub struct RevisionControlDiff {
    pub id: String,
    pub kind: String,
    pub before: Option<CompiledControlPoint>,
    pub after: Option<CompiledControlPoint>,
    pub movement_m: Option<f64>,
}

#[derive(Clone, Debug, Serialize)]
pub struct RevisionSummaryDiff {
    pub route_km: f64,
    pub station_count: i64,
    pub manual_station_count: i64,
    pub manual_line_count: i64,
    pub peak_fleet: i64,
    pub weekly_service_km: f64,
}

#[derive(Clone, Debug, Serialize)]
pub struct RevisionStationDiff {
    pub id: String,
    pub kind: String,
    pub before: Option<CompiledStation>,
    pub after: Option<CompiledStation>,
    pub movement_m: Option<f64>,
}

#[derive(Clone, Debug, Serialize)]
pub struct RevisionLineDiff {
    pub id: String,
    pub before: Option<CompiledLine>,
    pub after: Option<CompiledLine>,
    pub before_length_m: Option<f64>,
    pub after_length_m: Option<f64>,
    pub length_delta_m: f64,
    pub station_delta: i64,
}

#[derive(Clone, Debug, Serialize)]
pub struct RevisionServiceDiff {
    pub line: String,
    pub day_type: String,
    pub kind: String,
    pub before: Option<LineServicePlan>,
    pub after: Option<LineServicePlan>,
    pub peak_fleet_delta: i64,
    pub capacity_delta_pphpd: i64,
    pub daily_service_km_delta: f64,
}

#[derive(Clone, Debug, Serialize)]
pub struct BuildManifest {
    pub schema_version: u32,
    pub compiler_version: String,
    pub compiler_source_sha256: String,
    pub revision_id: String,
    pub content_sha256: String,
    pub input_sha256: String,
    pub artifacts: Vec<BuildArtifact>,
}

#[derive(Clone, Debug, Serialize)]
pub struct BuildArtifact {
    pub kind: String,
    pub path: String,
    pub sha256: String,
}
