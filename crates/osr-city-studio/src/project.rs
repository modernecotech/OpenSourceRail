use std::collections::{BTreeMap, BTreeSet};
use std::fs;
use std::path::{Path, PathBuf};
use std::process::Command;

use anyhow::{anyhow, bail, Context, Result};
use osr_routing::{solve_path_in_bbox, DemandWeight, Grid, GridRef};
use serde::Serialize;
use sha2::{Digest, Sha256};

use crate::model::{
    BaseDesign, BuildArtifact, BuildManifest, CompiledControlPoint, CompiledLine, CompiledSnapshot,
    CompiledStation, ControlPointCreate, ControlPointEdit, CoordinationCreate, CoordinationEdit,
    CoordinationFile, CoordinationIssue, CoordinationStatus, FindingSeverity, GeoPoint, GitState,
    IntentState, LineControlPoint, LineCreate, LineEdit, LineRoutingPreference, LineServicePlan,
    ManualLine, ManualStation, OverrideFile, ProjectFile, ResolvedSource, RevisionComparison,
    RevisionControlDiff, RevisionCoordinationDiff, RevisionLineDiff, RevisionListItem,
    RevisionMaterialized, RevisionServiceDiff, RevisionStationDiff, RevisionSummaryDiff,
    RoutingSettings, ServiceMetric, ServicePlan, SnapshotSummary, SourceLock, StationChange,
    StationCreate, StationEdit, StationOverride, StudioArtifact, ValidationFinding,
};

const SNAPSHOT_SCHEMA_VERSION: u32 = 1;
const CIVIL_COORDINATION_ISSUE_IDS: [&str; 3] = [
    "alignment-survey-authority",
    "station-deck-release",
    "viaduct-design-release",
];

#[derive(Debug)]
pub struct CityProject {
    root: PathBuf,
    config: ProjectFile,
    base: BaseDesign,
    overrides: OverrideFile,
    service_plan: ServicePlan,
    source_lock: SourceLock,
    corridor: serde_json::Value,
    coordination: CoordinationFile,
}

#[derive(Serialize)]
struct SnapshotContent<'a> {
    schema_version: u32,
    compiler_version: &'static str,
    compiler_source_sha256: &'a str,
    input_sha256: &'a str,
    project: &'a crate::model::ProjectIdentity,
    sources: &'a [ResolvedSource],
    lines: &'a [CompiledLine],
    stations: &'a [CompiledStation],
    line_control_points: &'a [CompiledControlPoint],
    service_plan: &'a ServicePlan,
    service_metrics: &'a [ServiceMetric],
    summary: &'a SnapshotSummary,
    changes: &'a [StationChange],
    findings: &'a [ValidationFinding],
    coordination: &'a CoordinationFile,
}

#[derive(Debug)]
struct LineGeometry {
    source: Vec<[f64; 2]>,
    effective: Vec<[f64; 2]>,
}

#[derive(Debug)]
struct RoutedLine {
    points: Vec<GeoPoint>,
    method: String,
    source_ids: Vec<String>,
    demand_weight: Option<f32>,
}

#[derive(Debug)]
struct GeometryControl {
    index: usize,
    chainage_m: f64,
    delta_lon: f64,
    delta_lat: f64,
    target_lon: f64,
    target_lat: f64,
    influence_m: f64,
}

impl CityProject {
    pub fn load(root: impl AsRef<Path>) -> Result<Self> {
        let root = root.as_ref().to_path_buf();
        let config: ProjectFile = read_toml(&root.join("project.osr.toml"))?;
        if config.project.schema_version != 1 {
            bail!(
                "unsupported city project schema {}; expected 1",
                config.project.schema_version
            );
        }
        let base: BaseDesign = read_toml(&root.join(&config.inputs.base_design))?;
        let overrides: OverrideFile = read_toml(&root.join(&config.inputs.network_overrides))?;
        let service_plan: ServicePlan = read_toml(&root.join(&config.inputs.service_plan))?;
        let source_lock: SourceLock = read_json(&root.join(&config.inputs.source_lock))?;
        let corridor: serde_json::Value = read_json(&root.join(&config.inputs.corridor_geojson))?;
        let coordination = if let Some(path) = &config.inputs.coordination {
            read_toml(&root.join(path))?
        } else {
            CoordinationFile {
                schema_version: 1,
                issues: Vec::new(),
            }
        };
        Ok(Self {
            root,
            config,
            base,
            overrides,
            service_plan,
            source_lock,
            corridor,
            coordination,
        })
    }

    pub fn root(&self) -> &Path {
        &self.root
    }

    pub fn config(&self) -> &ProjectFile {
        &self.config
    }

    pub fn service_plan(&self) -> &ServicePlan {
        &self.service_plan
    }

    pub fn coordination(&self) -> &CoordinationFile {
        &self.coordination
    }

    fn is_active_line(&self, id: &str) -> bool {
        self.base.lines.iter().any(|line| line.name == id)
            || self
                .overrides
                .manual_lines
                .iter()
                .any(|line| line.id == id && line.state != IntentState::Retired)
    }

    pub fn corridor(&self) -> &serde_json::Value {
        &self.corridor
    }

    pub fn compile(&self) -> Result<CompiledSnapshot> {
        let sources = self.resolve_sources()?;
        let mut findings = self.validate(&sources);
        let override_by_id: BTreeMap<&str, &StationOverride> = self
            .overrides
            .stations
            .iter()
            .map(|item| (item.id.as_str(), item))
            .collect();

        let mut stations =
            Vec::with_capacity(self.base.stations.len() + self.overrides.manual_stations.len());
        let mut changes = Vec::new();
        for station in &self.base.stations {
            let item = override_by_id.get(station.id.as_str()).copied();
            let state = item.map_or(IntentState::Generated, |value| value.state);
            if state == IntentState::Retired {
                continue;
            }
            let lat = item.and_then(|value| value.lat).unwrap_or(station.lat);
            let lon = item.and_then(|value| value.lon).unwrap_or(station.lon);
            let distance_m = haversine_m(station.lat, station.lon, lat, lon);
            if distance_m > 0.01 {
                changes.push(StationChange {
                    id: station.id.clone(),
                    line: station.line.clone(),
                    from_lat: station.lat,
                    from_lon: station.lon,
                    to_lat: lat,
                    to_lon: lon,
                    distance_m,
                });
                let (severity, code) = if distance_m > 5_000.0 {
                    (FindingSeverity::Error, "STATION_MOVE_TOO_LARGE")
                } else if distance_m > 1_000.0 {
                    (FindingSeverity::Warning, "STATION_MOVE_REVIEW")
                } else {
                    (FindingSeverity::Info, "STATION_MOVED")
                };
                findings.push(ValidationFinding {
                    severity,
                    code: code.to_string(),
                    message: format!("station moved {distance_m:.1} m from the generated baseline"),
                    object_id: Some(station.id.clone()),
                });
            }
            stations.push(CompiledStation {
                id: station.id.clone(),
                name: station
                    .anchor_name
                    .clone()
                    .unwrap_or_else(|| station.id.clone()),
                line: station.line.clone(),
                lat,
                lon,
                s_m: station.s_m,
                archetype: station
                    .archetype
                    .clone()
                    .unwrap_or_else(|| "standard".to_string()),
                state,
                reason: item.map_or_else(String::new, |value| value.reason.clone()),
            });
        }
        for station in self
            .overrides
            .manual_stations
            .iter()
            .filter(|station| station.state != IntentState::Retired)
        {
            let distance_m = haversine_m(
                station.source_lat,
                station.source_lon,
                station.lat,
                station.lon,
            );
            if distance_m > 0.01 {
                changes.push(StationChange {
                    id: station.id.clone(),
                    line: station.line.clone(),
                    from_lat: station.source_lat,
                    from_lon: station.source_lon,
                    to_lat: station.lat,
                    to_lon: station.lon,
                    distance_m,
                });
            }
            findings.push(ValidationFinding {
                severity: FindingSeverity::Info,
                code: "MANUAL_STATION_ADDED".to_string(),
                message: "designer-created station is included in the candidate network"
                    .to_string(),
                object_id: Some(station.id.clone()),
            });
            stations.push(CompiledStation {
                id: station.id.clone(),
                name: station.name.clone(),
                line: station.line.clone(),
                lat: station.lat,
                lon: station.lon,
                s_m: station.source_s_m,
                archetype: station.archetype.clone(),
                state: IntentState::Manual,
                reason: station.reason.clone(),
            });
        }
        stations.sort_by(|a, b| {
            a.line
                .cmp(&b.line)
                .then_with(|| a.s_m.total_cmp(&b.s_m))
                .then_with(|| a.id.cmp(&b.id))
        });
        changes.sort_by(|a, b| a.id.cmp(&b.id));
        findings.extend(self.validate_effective_stations(&stations));
        let mut line_control_points = self
            .overrides
            .line_control_points
            .iter()
            .filter(|control| control.state != IntentState::Retired)
            .map(|control| CompiledControlPoint {
                id: control.id.clone(),
                line: control.line.clone(),
                state: control.state,
                source_lat: control.source_lat,
                source_lon: control.source_lon,
                lat: control.lat,
                lon: control.lon,
                influence_m: control.influence_m,
                distance_m: haversine_m(
                    control.source_lat,
                    control.source_lon,
                    control.lat,
                    control.lon,
                ),
                reason: control.reason.clone(),
            })
            .collect::<Vec<_>>();
        line_control_points.sort_by(|left, right| left.id.cmp(&right.id));
        for control in &line_control_points {
            if control.distance_m > 0.01 {
                findings.push(ValidationFinding {
                    severity: FindingSeverity::Info,
                    code: "LINE_CONTROL_POINT_MOVED".to_string(),
                    message: format!(
                        "alignment control point moved {:.1} m with a {:.0} m influence radius",
                        control.distance_m, control.influence_m
                    ),
                    object_id: Some(control.id.clone()),
                });
            }
        }
        let mut changed_lines: BTreeSet<String> =
            changes.iter().map(|change| change.line.clone()).collect();
        changed_lines.extend(
            self.overrides
                .manual_stations
                .iter()
                .filter(|station| station.state != IntentState::Retired)
                .map(|station| station.line.clone()),
        );
        changed_lines.extend(
            self.overrides
                .manual_lines
                .iter()
                .filter(|line| line.state != IntentState::Retired)
                .map(|line| line.id.clone()),
        );
        changed_lines.extend(
            self.overrides
                .stations
                .iter()
                .filter(|station| station.state == IntentState::Retired)
                .filter_map(|station| {
                    self.base
                        .stations
                        .iter()
                        .find(|base| base.id == station.id)
                        .map(|base| base.line.clone())
                }),
        );
        changed_lines.extend(
            line_control_points
                .iter()
                .filter(|control| control.distance_m > 0.01)
                .map(|control| control.line.clone()),
        );
        let geometries = self.regenerated_line_geometries(&stations)?;

        let station_counts = stations
            .iter()
            .fold(BTreeMap::new(), |mut counts, station| {
                *counts.entry(station.line.clone()).or_insert(0_usize) += 1;
                counts
            });
        let mut lines: Vec<CompiledLine> = self
            .base
            .lines
            .iter()
            .map(|line| {
                let length_m = geometries
                    .get(&line.name)
                    .map_or(line.length_m, |geometry| {
                        if changed_lines.contains(&line.name) {
                            (line.length_m + polyline_length_m(&geometry.effective)
                                - polyline_length_m(&geometry.source))
                            .max(1.0)
                        } else {
                            line.length_m
                        }
                    });
                CompiledLine {
                    id: line.name.clone(),
                    name: line.name.clone(),
                    shape: line.shape.clone(),
                    length_m,
                    station_count: station_counts.get(&line.name).copied().unwrap_or(0),
                    routing_method: "generated-source".to_string(),
                    routing_source_ids: Vec::new(),
                    demand_weight: None,
                    state: IntentState::Generated,
                    reason: String::new(),
                }
            })
            .collect();
        lines.extend(
            self.overrides
                .manual_lines
                .iter()
                .filter(|line| line.state != IntentState::Retired)
                .map(|line| {
                    let geometry = geometries
                        .get(&line.id)
                        .ok_or_else(|| anyhow!("no geometry for manual line {}", line.id))?;
                    Ok(CompiledLine {
                        id: line.id.clone(),
                        name: line.name.clone(),
                        shape: line.shape.clone(),
                        length_m: polyline_length_m(&geometry.effective),
                        station_count: station_counts.get(&line.id).copied().unwrap_or(0),
                        routing_method: line.routing_method.clone(),
                        routing_source_ids: line.routing_source_ids.clone(),
                        demand_weight: line.demand_weight,
                        state: IntentState::Manual,
                        reason: line.reason.clone(),
                    })
                })
                .collect::<Result<Vec<_>>>()?,
        );
        lines.sort_by(|a, b| a.id.cmp(&b.id));

        let mut service_metrics = self.compute_service_metrics(&lines)?;
        service_metrics.sort_by(|a, b| {
            a.line
                .cmp(&b.line)
                .then_with(|| a.day_type.cmp(&b.day_type))
        });
        let day_counts = self.service_plan.calendar.day_type_counts();
        let weekly_service_km = service_metrics
            .iter()
            .map(|metric| {
                metric.daily_service_km
                    * f64::from(day_counts.get(&metric.day_type).copied().unwrap_or(0))
            })
            .sum();
        let summary = SnapshotSummary {
            route_km: lines.iter().map(|line| line.length_m).sum::<f64>() / 1_000.0,
            station_count: stations.len(),
            locked_station_count: stations
                .iter()
                .filter(|station| station.state == IntentState::Locked)
                .count(),
            manual_station_count: stations
                .iter()
                .filter(|station| station.state == IntentState::Manual)
                .count(),
            manual_line_count: lines
                .iter()
                .filter(|line| line.state == IntentState::Manual)
                .count(),
            moved_station_count: changes.len(),
            edited_line_count: changed_lines.len(),
            peak_fleet: service_metrics
                .iter()
                .map(|metric| metric.peak_fleet)
                .max()
                .unwrap_or(0),
            weekly_service_km,
            validation_errors: findings
                .iter()
                .filter(|finding| finding.severity == FindingSeverity::Error)
                .count(),
            validation_warnings: findings
                .iter()
                .filter(|finding| finding.severity == FindingSeverity::Warning)
                .count(),
        };

        let input_sha256 = self.project_input_hash()?;
        let compiler_source_sha256 = compiler_source_hash();
        let content = SnapshotContent {
            schema_version: SNAPSHOT_SCHEMA_VERSION,
            compiler_version: env!("CARGO_PKG_VERSION"),
            compiler_source_sha256: &compiler_source_sha256,
            input_sha256: &input_sha256,
            project: &self.config.project,
            sources: &sources,
            lines: &lines,
            stations: &stations,
            line_control_points: &line_control_points,
            service_plan: &self.service_plan,
            service_metrics: &service_metrics,
            summary: &summary,
            changes: &changes,
            findings: &findings,
            coordination: &self.coordination,
        };
        let content_sha256 = sha256_bytes(&serde_json::to_vec(&content)?);
        let revision_id = format!("osr-{}", &content_sha256[..16]);
        let parent_git_commit = self.git_state().head;
        Ok(CompiledSnapshot {
            schema_version: SNAPSHOT_SCHEMA_VERSION,
            compiler_version: env!("CARGO_PKG_VERSION").to_string(),
            compiler_source_sha256,
            revision_id,
            content_sha256,
            input_sha256,
            parent_git_commit,
            project: self.config.project.clone(),
            sources,
            lines,
            stations,
            line_control_points,
            service_plan: Some(self.service_plan.clone()),
            service_metrics,
            summary,
            changes,
            findings,
            coordination: self.coordination.clone(),
        })
    }

    pub fn update_coordination_issue(&mut self, id: &str, edit: CoordinationEdit) -> Result<()> {
        validate_coordination_decision(edit.status, &edit.resolution, &edit.reviewed_by)?;
        let issue = self
            .coordination
            .issues
            .iter_mut()
            .find(|issue| issue.id == id)
            .ok_or_else(|| anyhow!("unknown coordination issue {id:?}"))?;
        issue.status = edit.status;
        issue.assignee = edit.assignee.trim().to_string();
        issue.resolution = edit.resolution.trim().to_string();
        issue.reviewed_by = edit.reviewed_by.trim().to_string();
        self.coordination
            .issues
            .sort_by(|left, right| left.id.cmp(&right.id));
        let path = self
            .config
            .inputs
            .coordination
            .as_ref()
            .ok_or_else(|| anyhow!("project does not declare a coordination intent file"))?;
        write_toml_atomic(&self.root.join(path), &self.coordination)
    }

    pub fn create_coordination_issue(&mut self, create: CoordinationCreate) -> Result<String> {
        let title = create.title.trim().to_string();
        let description = create.description.trim().to_string();
        let assignee = create.assignee.trim().to_string();
        let mut asset_ids = create
            .asset_ids
            .into_iter()
            .map(|value| value.trim().to_string())
            .collect::<Vec<_>>();
        asset_ids.sort();
        asset_ids.dedup();
        validate_custom_coordination_issue(&title, &description, &asset_ids)?;
        let identity = serde_json::to_vec(&serde_json::json!({
            "title": title,
            "description": description,
            "asset_ids": asset_ids,
        }))?;
        let id = format!("custom-{}", &sha256_bytes(&identity)[..16]);
        if self.coordination.issues.iter().any(|issue| issue.id == id) {
            bail!("an identical coordination issue already exists as {id}");
        }
        self.coordination.issues.push(CoordinationIssue {
            id: id.clone(),
            title,
            description,
            asset_ids,
            status: CoordinationStatus::Open,
            assignee,
            resolution: String::new(),
            reviewed_by: String::new(),
        });
        self.coordination
            .issues
            .sort_by(|left, right| left.id.cmp(&right.id));
        let path = self
            .config
            .inputs
            .coordination
            .as_ref()
            .ok_or_else(|| anyhow!("project does not declare a coordination intent file"))?;
        write_toml_atomic(&self.root.join(path), &self.coordination)?;
        Ok(id)
    }

    pub fn update_station(&mut self, id: &str, edit: StationEdit) -> Result<()> {
        validate_coordinates(edit.lat, edit.lon)?;
        if self.base.stations.iter().any(|station| station.id == id) {
            if edit.state == IntentState::Manual {
                bail!("manual state is reserved for designer-created stations");
            }
            if edit.name.is_some() || edit.archetype.is_some() {
                bail!(
                    "generated station names and archetypes remain controlled by the design source"
                );
            }
            if let Some(existing) = self
                .overrides
                .stations
                .iter_mut()
                .find(|item| item.id == id)
            {
                existing.state = edit.state;
                existing.lat = edit.lat;
                existing.lon = edit.lon;
                existing.reason = edit.reason;
            } else {
                self.overrides.stations.push(StationOverride {
                    id: id.to_string(),
                    state: edit.state,
                    lat: edit.lat,
                    lon: edit.lon,
                    reason: edit.reason,
                });
            }
            self.overrides
                .stations
                .sort_by(|left, right| left.id.cmp(&right.id));
        } else if let Some(station) = self
            .overrides
            .manual_stations
            .iter_mut()
            .find(|station| station.id == id)
        {
            if edit.state != IntentState::Manual && edit.state != IntentState::Retired {
                bail!("designer-created stations must remain manual or be retired");
            }
            let name = edit.name.unwrap_or_else(|| station.name.clone());
            validate_station_name(&name)?;
            let archetype = edit.archetype.unwrap_or_else(|| station.archetype.clone());
            validate_manual_archetype(&archetype)?;
            station.name = name.trim().to_string();
            station.archetype = archetype;
            station.state = edit.state;
            if let (Some(lat), Some(lon)) = (edit.lat, edit.lon) {
                station.lat = lat;
                station.lon = lon;
            }
            station.reason = edit.reason;
        } else {
            bail!("unknown station id {id:?}");
        }
        let path = self.root.join(&self.config.inputs.network_overrides);
        write_toml_atomic(&path, &self.overrides)
    }

    pub fn create_station(&mut self, line: &str, create: StationCreate) -> Result<String> {
        if !self.is_active_line(line) {
            bail!("unknown line {line:?}");
        }
        validate_station_name(&create.name)?;
        validate_manual_archetype(&create.archetype)?;
        validate_coordinates(Some(create.lat), Some(create.lon))?;
        let source = self
            .source_line_geometries()?
            .remove(line)
            .ok_or_else(|| anyhow!("corridor has no geometry for line {line}"))?;
        let source_index = nearest_coordinate_index(&source, create.lon, create.lat);
        let [source_lon, source_lat] = source[source_index];
        let offset_m = haversine_m(create.lat, create.lon, source_lat, source_lon);
        if offset_m > self.config.planning.geometry_regeneration_radius_m {
            bail!(
                "new station is {offset_m:.0} m from {line}; place it within the {:.0} m regeneration radius",
                self.config.planning.geometry_regeneration_radius_m
            );
        }
        if self.base.stations.iter().any(|station| {
            station.line == line
                && haversine_m(station.lat, station.lon, create.lat, create.lon) < 25.0
        }) || self.overrides.manual_stations.iter().any(|station| {
            station.line == line
                && station.state != IntentState::Retired
                && haversine_m(station.lat, station.lon, create.lat, create.lon) < 25.0
        }) {
            bail!("a station already exists within 25 m on {line}");
        }
        let source_s_m = cumulative_polyline_m(&source)[source_index];
        let seed = format!("{line}:{source_lat:.7}:{source_lon:.7}");
        let id = format!("manual-{line}-{}", &sha256_bytes(seed.as_bytes())[..12]);
        if self
            .overrides
            .manual_stations
            .iter()
            .any(|station| station.id == id)
        {
            bail!("a manual station already exists at this line location");
        }
        self.overrides.manual_stations.push(ManualStation {
            id: id.clone(),
            name: create.name.trim().to_string(),
            line: line.to_string(),
            state: IntentState::Manual,
            source_lat,
            source_lon,
            source_s_m,
            lat: create.lat,
            lon: create.lon,
            archetype: create.archetype,
            reason: create.reason,
        });
        self.overrides
            .manual_stations
            .sort_by(|left, right| left.id.cmp(&right.id));
        let path = self.root.join(&self.config.inputs.network_overrides);
        write_toml_atomic(&path, &self.overrides)?;
        Ok(id)
    }

    pub fn retire_manual_station(&mut self, id: &str) -> Result<()> {
        let station = self
            .overrides
            .manual_stations
            .iter_mut()
            .find(|station| station.id == id)
            .ok_or_else(|| anyhow!("only designer-created stations can be deleted here"))?;
        station.state = IntentState::Retired;
        if station.reason.trim().is_empty() {
            station.reason = "Retired through City Studio".to_string();
        }
        let path = self.root.join(&self.config.inputs.network_overrides);
        write_toml_atomic(&path, &self.overrides)
    }

    pub fn create_line(&mut self, create: LineCreate) -> Result<String> {
        validate_station_name(&create.name)?;
        validate_coordinates(Some(create.start_lat), Some(create.start_lon))?;
        validate_coordinates(Some(create.end_lat), Some(create.end_lon))?;
        let length_m = haversine_m(
            create.start_lat,
            create.start_lon,
            create.end_lat,
            create.end_lon,
        );
        if !(500.0..=100_000.0).contains(&length_m) {
            bail!("manual line endpoints must be between 500 m and 100 km apart");
        }
        let RoutedLine {
            points,
            method: routing_method,
            source_ids: routing_source_ids,
            demand_weight,
        } = self.route_manual_line(&create)?;
        let seed = format!(
            "{:.7}:{:.7}:{:.7}:{:.7}:{routing_method}",
            create.start_lat, create.start_lon, create.end_lat, create.end_lon
        );
        let id = format!("manual-line-{}", &sha256_bytes(seed.as_bytes())[..12]);
        if self.base.lines.iter().any(|line| line.name == id)
            || self.overrides.manual_lines.iter().any(|line| line.id == id)
        {
            bail!("a line already exists for these endpoints");
        }
        let route_length_m = polyline_length_m(
            &points
                .iter()
                .map(|point| [point.lon, point.lat])
                .collect::<Vec<_>>(),
        );
        let route_start = *points.first().expect("manual route has a start point");
        let route_end = *points.last().expect("manual route has an end point");
        self.overrides.manual_lines.push(ManualLine {
            id: id.clone(),
            name: create.name.trim().to_string(),
            state: IntentState::Manual,
            shape: "radial".to_string(),
            points,
            routing_method,
            routing_source_ids,
            demand_weight,
            reason: create.reason.clone(),
        });
        for (suffix, name_suffix, lat, lon, chainage) in [
            ("terminal-a", "A", route_start.lat, route_start.lon, 0.0),
            (
                "terminal-b",
                "B",
                route_end.lat,
                route_end.lon,
                route_length_m,
            ),
        ] {
            self.overrides.manual_stations.push(ManualStation {
                id: format!("{id}-{suffix}"),
                name: format!("{} {name_suffix}", create.name.trim()),
                line: id.clone(),
                state: IntentState::Manual,
                source_lat: lat,
                source_lon: lon,
                source_s_m: chainage,
                lat,
                lon,
                archetype: "terminal".to_string(),
                reason: "Terminal created with manual line".to_string(),
            });
        }
        let day_types = self
            .service_plan
            .day_types
            .iter()
            .map(|day| day.id.clone())
            .collect::<Vec<_>>();
        for day_type in day_types {
            let mut template = self
                .service_plan
                .line_plans
                .iter()
                .find(|plan| plan.day_type == day_type)
                .cloned()
                .ok_or_else(|| anyhow!("no service template for day type {day_type}"))?;
            template.line = id.clone();
            self.service_plan.line_plans.push(template);
        }
        self.overrides
            .manual_lines
            .sort_by(|left, right| left.id.cmp(&right.id));
        self.overrides
            .manual_stations
            .sort_by(|left, right| left.id.cmp(&right.id));
        self.service_plan.line_plans.sort_by(|left, right| {
            left.line
                .cmp(&right.line)
                .then_with(|| left.day_type.cmp(&right.day_type))
        });
        let overrides_path = self.root.join(&self.config.inputs.network_overrides);
        let service_path = self.root.join(&self.config.inputs.service_plan);
        write_toml_atomic(&overrides_path, &self.overrides)?;
        write_toml_atomic(&service_path, &self.service_plan)?;
        Ok(id)
    }

    fn route_manual_line(&self, create: &LineCreate) -> Result<RoutedLine> {
        let demand_aware = match create.routing {
            LineRoutingPreference::Auto => self.config.routing.is_some(),
            LineRoutingPreference::DemandAware => true,
            LineRoutingPreference::Direct => false,
        };
        if !demand_aware {
            return Ok(RoutedLine {
                points: interpolate_line_points(
                    create.start_lat,
                    create.start_lon,
                    create.end_lat,
                    create.end_lon,
                    50.0,
                ),
                method: "direct".to_string(),
                source_ids: Vec::new(),
                demand_weight: None,
            });
        }

        let settings = self.config.routing.as_ref().ok_or_else(|| {
            anyhow!("this project has no source-locked routing bundle; select direct routing")
        })?;
        validate_routing_settings(settings)?;
        let sources = self.resolve_sources()?;
        for source_id in &settings.source_ids {
            let source = sources
                .iter()
                .find(|source| &source.id == source_id)
                .ok_or_else(|| anyhow!("routing source {source_id:?} is not source-locked"))?;
            if !source.matches_lock {
                bail!(
                    "routing source {} does not match its SHA-256 lock",
                    source.path
                );
            }
        }
        let sidecar = self.root.join(&settings.sidecar);
        let bundle = osr_routing::raster::load_bundle(&sidecar, &settings.slug)
            .with_context(|| format!("loading routing bundle {}", sidecar.display()))?;
        let start = snapped_route_cell(
            &bundle.grid,
            create.start_lat,
            create.start_lon,
            settings.endpoint_snap_m,
        )?;
        let goal = snapped_route_cell(
            &bundle.grid,
            create.end_lat,
            create.end_lon,
            settings.endpoint_snap_m,
        )?;
        if start == goal {
            bail!("manual line endpoints snap to the same routing cell");
        }
        let margin_cells =
            (settings.search_margin_m / bundle.grid.reference.cell_m).ceil() as usize;
        let bbox = route_bbox(&bundle.grid, start, goal, margin_cells);
        let cells = solve_path_in_bbox(
            &bundle.grid,
            start,
            goal,
            DemandWeight(settings.demand_weight),
            None,
            Some(bbox),
        )
        .context("demand-aware route search found no buildable path")?;
        let points = cells
            .into_iter()
            .map(|(row, col)| {
                let (lat, lon) = bundle.grid.reference.rc_to_latlon(row, col);
                GeoPoint { lat, lon }
            })
            .collect::<Vec<_>>();
        Ok(RoutedLine {
            points,
            method: "demand-aware".to_string(),
            source_ids: settings.source_ids.clone(),
            demand_weight: Some(settings.demand_weight),
        })
    }

    pub fn update_manual_line(&mut self, id: &str, edit: LineEdit) -> Result<()> {
        validate_station_name(&edit.name)?;
        if edit.state != IntentState::Manual {
            bail!("manual lines remain manual; use the retire action to remove one");
        }
        let line = self
            .overrides
            .manual_lines
            .iter_mut()
            .find(|line| line.id == id && line.state != IntentState::Retired)
            .ok_or_else(|| anyhow!("unknown active manual line {id:?}"))?;
        line.name = edit.name.trim().to_string();
        line.reason = edit.reason;
        let path = self.root.join(&self.config.inputs.network_overrides);
        write_toml_atomic(&path, &self.overrides)
    }

    pub fn retire_manual_line(&mut self, id: &str) -> Result<()> {
        let line = self
            .overrides
            .manual_lines
            .iter_mut()
            .find(|line| line.id == id && line.state != IntentState::Retired)
            .ok_or_else(|| anyhow!("only active manual lines can be retired"))?;
        line.state = IntentState::Retired;
        if line.reason.trim().is_empty() {
            line.reason = "Retired through City Studio".to_string();
        }
        for station in self
            .overrides
            .manual_stations
            .iter_mut()
            .filter(|station| station.line == id)
        {
            station.state = IntentState::Retired;
        }
        for control in self
            .overrides
            .line_control_points
            .iter_mut()
            .filter(|control| control.line == id)
        {
            control.state = IntentState::Retired;
        }
        self.service_plan.line_plans.retain(|plan| plan.line != id);
        let overrides_path = self.root.join(&self.config.inputs.network_overrides);
        let service_path = self.root.join(&self.config.inputs.service_plan);
        write_toml_atomic(&overrides_path, &self.overrides)?;
        write_toml_atomic(&service_path, &self.service_plan)
    }

    pub fn create_control_point(
        &mut self,
        line: &str,
        create: ControlPointCreate,
    ) -> Result<String> {
        if !self.is_active_line(line) {
            bail!("unknown line {line:?}");
        }
        validate_coordinates(Some(create.source_lat), Some(create.source_lon))?;
        let seed = format!("{}:{:.7}:{:.7}", line, create.source_lat, create.source_lon);
        let id = format!("cp-{}-{}", line, &sha256_bytes(seed.as_bytes())[..12]);
        if self
            .overrides
            .line_control_points
            .iter()
            .any(|control| control.id == id)
        {
            bail!("a control point already exists at this line location");
        }
        self.overrides.line_control_points.push(LineControlPoint {
            id: id.clone(),
            line: line.to_string(),
            state: IntentState::Preferred,
            source_lat: create.source_lat,
            source_lon: create.source_lon,
            lat: create.source_lat,
            lon: create.source_lon,
            influence_m: self.config.planning.geometry_regeneration_radius_m,
            reason: create.reason,
        });
        self.overrides
            .line_control_points
            .sort_by(|left, right| left.id.cmp(&right.id));
        let path = self.root.join(&self.config.inputs.network_overrides);
        write_toml_atomic(&path, &self.overrides)?;
        Ok(id)
    }

    pub fn update_control_point(&mut self, id: &str, edit: ControlPointEdit) -> Result<()> {
        validate_coordinates(Some(edit.lat), Some(edit.lon))?;
        if !(100.0..=20_000.0).contains(&edit.influence_m) {
            bail!("control-point influence must be between 100 m and 20 km");
        }
        if edit.state == IntentState::Generated || edit.state == IntentState::Manual {
            bail!("alignment control points must be preferred, locked, or retired");
        }
        let control = self
            .overrides
            .line_control_points
            .iter_mut()
            .find(|control| control.id == id)
            .ok_or_else(|| anyhow!("unknown control point {id:?}"))?;
        control.state = edit.state;
        control.lat = edit.lat;
        control.lon = edit.lon;
        control.influence_m = edit.influence_m;
        control.reason = edit.reason;
        let path = self.root.join(&self.config.inputs.network_overrides);
        write_toml_atomic(&path, &self.overrides)
    }

    pub fn update_service_plan(&mut self, replacement: LineServicePlan) -> Result<()> {
        if !self
            .base
            .lines
            .iter()
            .any(|line| line.name == replacement.line)
        {
            bail!("unknown line {:?}", replacement.line);
        }
        if !self
            .service_plan
            .day_types
            .iter()
            .any(|day| day.id == replacement.day_type)
        {
            bail!("unknown day type {:?}", replacement.day_type);
        }
        validate_line_plan(&replacement)?;
        if let Some(existing) = self
            .service_plan
            .line_plans
            .iter_mut()
            .find(|plan| plan.line == replacement.line && plan.day_type == replacement.day_type)
        {
            *existing = replacement;
        } else {
            self.service_plan.line_plans.push(replacement);
        }
        self.service_plan.line_plans.sort_by(|left, right| {
            left.line
                .cmp(&right.line)
                .then_with(|| left.day_type.cmp(&right.day_type))
        });
        let path = self.root.join(&self.config.inputs.service_plan);
        write_toml_atomic(&path, &self.service_plan)
    }

    pub fn write_build_snapshot(&self, repo_root: &Path) -> Result<PathBuf> {
        let snapshot = self.compile()?;
        let output_dir = repo_root
            .join("build/city-studio")
            .join(&self.config.project.slug);
        let snapshot_path = output_dir.join("snapshot.json");
        write_json_atomic(&snapshot_path, &snapshot)?;

        let network_path = output_dir.join("candidate-network.geojson");
        write_json_atomic(&network_path, &self.candidate_network_geojson(&snapshot)?)?;

        let scenario_dir = output_dir.join("scenarios");
        let mut day_types: Vec<&str> = self
            .service_plan
            .day_types
            .iter()
            .map(|day| day.id.as_str())
            .collect();
        day_types.sort_unstable();
        let mut scenario_paths = Vec::new();
        for day_type in day_types {
            let scenario_path = scenario_dir.join(format!("{day_type}.toml"));
            let scenario = self.scenario_for_day_type(day_type, &snapshot)?;
            write_atomic(&scenario_path, scenario.as_bytes())?;
            scenario_paths.push(scenario_path);
        }

        let mut artifact_paths = vec![
            ("snapshot", snapshot_path.clone()),
            ("gis-network", network_path),
        ];
        artifact_paths.extend(
            scenario_paths
                .into_iter()
                .map(|path| ("simulator-scenario", path)),
        );
        let mut artifacts = Vec::with_capacity(artifact_paths.len());
        for (kind, path) in artifact_paths {
            artifacts.push(BuildArtifact {
                kind: kind.to_string(),
                path: path
                    .strip_prefix(repo_root)
                    .unwrap_or(&path)
                    .display()
                    .to_string(),
                sha256: sha256_file(&path)?,
            });
        }
        artifacts.sort_by(|left, right| left.path.cmp(&right.path));
        let manifest = BuildManifest {
            schema_version: 1,
            compiler_version: env!("CARGO_PKG_VERSION").to_string(),
            compiler_source_sha256: snapshot.compiler_source_sha256.clone(),
            revision_id: snapshot.revision_id.clone(),
            content_sha256: snapshot.content_sha256.clone(),
            input_sha256: snapshot.input_sha256.clone(),
            artifacts,
        };
        write_json_atomic(&output_dir.join("manifest.json"), &manifest)?;
        Ok(snapshot_path)
    }

    pub fn materialize_revision(&self) -> Result<RevisionMaterialized> {
        let snapshot = self.compile()?;
        if self.config.revision.require_passing_validation && snapshot.summary.validation_errors > 0
        {
            bail!(
                "revision has {} validation error(s); materialization refused",
                snapshot.summary.validation_errors
            );
        }
        let revisions = self.root.join("revisions");
        let output = revisions.join(format!("{}.json", snapshot.revision_id));
        write_json_atomic(&output, &snapshot)?;
        Ok(RevisionMaterialized {
            revision_id: snapshot.revision_id.clone(),
            path: output.display().to_string(),
            suggested_branch: format!("city/{}/{}", self.config.project.slug, snapshot.revision_id),
            suggested_tag: format!(
                "{}{}",
                self.config.revision.tag_prefix, snapshot.revision_id
            ),
        })
    }

    pub fn revisions(&self) -> Result<Vec<RevisionListItem>> {
        let current = self.compile()?;
        let directory = self.root.join("revisions");
        let mut revisions = Vec::new();
        if !directory.exists() {
            return Ok(revisions);
        }
        for entry in
            fs::read_dir(&directory).with_context(|| format!("reading {}", directory.display()))?
        {
            let path = entry?.path();
            if path.extension().and_then(|value| value.to_str()) != Some("json") {
                continue;
            }
            let snapshot: CompiledSnapshot = read_json(&path)?;
            revisions.push(RevisionListItem {
                revision_id: snapshot.revision_id.clone(),
                parent_git_commit: snapshot.parent_git_commit,
                compiler_version: snapshot.compiler_version,
                content_sha256: snapshot.content_sha256,
                route_km: snapshot.summary.route_km,
                station_count: snapshot.summary.station_count,
                peak_fleet: snapshot.summary.peak_fleet,
                weekly_service_km: snapshot.summary.weekly_service_km,
                is_current: snapshot.revision_id == current.revision_id,
            });
        }
        revisions.sort_by(|left, right| left.revision_id.cmp(&right.revision_id));
        Ok(revisions)
    }

    pub fn compare_revision(&self, revision_id: &str) -> Result<RevisionComparison> {
        validate_revision_id(revision_id)?;
        let path = self
            .root
            .join("revisions")
            .join(format!("{revision_id}.json"));
        let base: CompiledSnapshot =
            read_json(&path).with_context(|| format!("loading base revision {revision_id}"))?;
        let candidate = self.compile()?;
        Ok(compare_snapshots(&base, &candidate))
    }

    pub fn git_state(&self) -> GitState {
        let repository_root = git_output(&self.root, &["rev-parse", "--show-toplevel"]);
        let branch =
            git_output(&self.root, &["branch", "--show-current"]).filter(|value| !value.is_empty());
        let head = git_output(&self.root, &["rev-parse", "HEAD"]);
        let changed_paths = git_output(&self.root, &["status", "--porcelain"])
            .map(|output| {
                output
                    .lines()
                    .filter_map(|line| line.get(3..))
                    .map(str::to_string)
                    .collect::<Vec<_>>()
            })
            .unwrap_or_default();
        GitState {
            repository_root,
            branch,
            head,
            dirty: !changed_paths.is_empty(),
            changed_paths,
        }
    }

    pub fn artifacts(&self) -> Vec<StudioArtifact> {
        let design = self.root.join(&self.config.inputs.base_design);
        let city_dir = design.parent().unwrap_or(&self.root).to_path_buf();
        let repository_root = self
            .git_state()
            .repository_root
            .map(PathBuf::from)
            .unwrap_or_else(|| self.root.clone());
        let build_dir = repository_root
            .join("build/city-studio")
            .join(&self.config.project.slug);
        let candidates = [
            ("Design", "Generated design", design),
            (
                "GIS",
                "Corridor GeoJSON",
                self.root.join(&self.config.inputs.corridor_geojson),
            ),
            (
                "Simulation",
                "Simulator scenario",
                self.root.join(&self.config.inputs.simulator_scenario),
            ),
            (
                "GIS",
                "Network map",
                city_dir.join(format!("{}-network-map.png", self.config.project.slug)),
            ),
            (
                "Engineering",
                "Station product map",
                city_dir.join("engineering/station-product-map.json"),
            ),
            (
                "Operations",
                "Operations manifest",
                city_dir.join(format!(
                    "operations/{}-operations-manifest.json",
                    self.config.project.slug
                )),
            ),
            (
                "Release",
                "City package manifest",
                city_dir.join("package-manifest.json"),
            ),
            (
                "Studio",
                "Candidate artifact manifest",
                build_dir.join("manifest.json"),
            ),
            (
                "Studio",
                "Candidate GIS network",
                build_dir.join("candidate-network.geojson"),
            ),
        ];
        candidates
            .into_iter()
            .map(|(category, label, path)| StudioArtifact {
                category: category.to_string(),
                label: label.to_string(),
                path: path.display().to_string(),
                exists: path.exists(),
            })
            .collect()
    }

    pub fn candidate_network(&self) -> Result<serde_json::Value> {
        let snapshot = self.compile()?;
        self.candidate_network_geojson(&snapshot)
    }

    fn resolve_sources(&self) -> Result<Vec<ResolvedSource>> {
        let mut resolved = Vec::with_capacity(self.source_lock.sources.len());
        for source in &self.source_lock.sources {
            let path = self.root.join(&source.path);
            let actual = if path.exists() {
                sha256_file(&path)?
            } else {
                String::new()
            };
            resolved.push(ResolvedSource {
                id: source.id.clone(),
                kind: source.kind.clone(),
                path: source.path.clone(),
                expected_sha256: source.sha256.clone(),
                matches_lock: actual == source.sha256,
                actual_sha256: actual,
            });
        }
        resolved.sort_by(|a, b| a.id.cmp(&b.id));
        Ok(resolved)
    }

    fn project_input_hash(&self) -> Result<String> {
        let mut paths = vec![
            PathBuf::from("project.osr.toml"),
            PathBuf::from(&self.config.inputs.network_overrides),
            PathBuf::from(&self.config.inputs.service_plan),
            PathBuf::from(&self.config.inputs.source_lock),
        ];
        if let Some(path) = &self.config.inputs.coordination {
            paths.push(PathBuf::from(path));
        }
        let mut hasher = Sha256::new();
        for relative in paths {
            let bytes = fs::read(self.root.join(&relative))
                .with_context(|| format!("hashing project input {}", relative.display()))?;
            hasher.update(relative.to_string_lossy().as_bytes());
            hasher.update([0]);
            hasher.update(&bytes);
            hasher.update([0]);
        }
        Ok(hex::encode(hasher.finalize()))
    }

    fn validate(&self, sources: &[ResolvedSource]) -> Vec<ValidationFinding> {
        let mut findings = Vec::new();
        if self.config.inputs.coordination.is_some() {
            if self.coordination.schema_version != 1 {
                findings.push(ValidationFinding {
                    severity: FindingSeverity::Error,
                    code: "COORDINATION_SCHEMA".to_string(),
                    message: "coordination intent schema_version must be 1".to_string(),
                    object_id: Some("coordination".to_string()),
                });
            }
            let mut seen = BTreeSet::new();
            for issue in &self.coordination.issues {
                if !seen.insert(issue.id.as_str()) {
                    findings.push(ValidationFinding {
                        severity: FindingSeverity::Error,
                        code: "DUPLICATE_COORDINATION_ISSUE".to_string(),
                        message: format!("coordination issue {} is duplicated", issue.id),
                        object_id: Some(issue.id.clone()),
                    });
                }
                if !CIVIL_COORDINATION_ISSUE_IDS.contains(&issue.id.as_str()) {
                    if !is_custom_coordination_id(&issue.id) {
                        findings.push(ValidationFinding {
                            severity: FindingSeverity::Error,
                            code: "UNKNOWN_COORDINATION_ISSUE".to_string(),
                            message: format!(
                                "coordination issue {} has an invalid custom id",
                                issue.id
                            ),
                            object_id: Some(issue.id.clone()),
                        });
                    }
                    if let Err(error) = validate_custom_coordination_issue(
                        &issue.title,
                        &issue.description,
                        &issue.asset_ids,
                    ) {
                        findings.push(ValidationFinding {
                            severity: FindingSeverity::Error,
                            code: "INVALID_CUSTOM_COORDINATION_ISSUE".to_string(),
                            message: error.to_string(),
                            object_id: Some(issue.id.clone()),
                        });
                    }
                }
                if let Err(error) = validate_coordination_decision(
                    issue.status,
                    &issue.resolution,
                    &issue.reviewed_by,
                ) {
                    findings.push(ValidationFinding {
                        severity: FindingSeverity::Error,
                        code: "INVALID_COORDINATION_DECISION".to_string(),
                        message: error.to_string(),
                        object_id: Some(issue.id.clone()),
                    });
                }
            }
            for expected in CIVIL_COORDINATION_ISSUE_IDS {
                if !seen.contains(expected) {
                    findings.push(ValidationFinding {
                        severity: FindingSeverity::Error,
                        code: "MISSING_COORDINATION_ISSUE".to_string(),
                        message: format!("coordination issue {expected} is missing"),
                        object_id: Some(expected.to_string()),
                    });
                }
            }
        }
        for source in sources {
            if !source.matches_lock {
                findings.push(ValidationFinding {
                    severity: FindingSeverity::Error,
                    code: "SOURCE_LOCK_MISMATCH".to_string(),
                    message: format!(
                        "source {} does not match its committed SHA-256 lock",
                        source.path
                    ),
                    object_id: Some(source.id.clone()),
                });
            }
        }
        if let Some(settings) = &self.config.routing {
            if let Err(error) = validate_routing_settings(settings) {
                findings.push(ValidationFinding {
                    severity: FindingSeverity::Error,
                    code: "INVALID_ROUTING_SETTINGS".to_string(),
                    message: error.to_string(),
                    object_id: Some("routing".to_string()),
                });
            }
            let locked_ids = self
                .source_lock
                .sources
                .iter()
                .map(|source| source.id.as_str())
                .collect::<BTreeSet<_>>();
            for source_id in &settings.source_ids {
                if !locked_ids.contains(source_id.as_str()) {
                    findings.push(ValidationFinding {
                        severity: FindingSeverity::Error,
                        code: "UNLOCKED_ROUTING_SOURCE".to_string(),
                        message: "routing bundle refers to a source without a SHA-256 lock"
                            .to_string(),
                        object_id: Some(source_id.clone()),
                    });
                }
            }
        }

        let station_ids: BTreeSet<&str> = self
            .base
            .stations
            .iter()
            .map(|station| station.id.as_str())
            .collect();
        let mut seen_overrides = BTreeSet::new();
        for item in &self.overrides.stations {
            if !station_ids.contains(item.id.as_str()) {
                findings.push(ValidationFinding {
                    severity: FindingSeverity::Error,
                    code: "UNKNOWN_STATION_OVERRIDE".to_string(),
                    message: "station override does not exist in the source design".to_string(),
                    object_id: Some(item.id.clone()),
                });
            }
            if !seen_overrides.insert(item.id.as_str()) {
                findings.push(ValidationFinding {
                    severity: FindingSeverity::Error,
                    code: "DUPLICATE_STATION_OVERRIDE".to_string(),
                    message: "station has more than one intent override".to_string(),
                    object_id: Some(item.id.clone()),
                });
            }
            if let Err(error) = validate_coordinates(item.lat, item.lon) {
                findings.push(ValidationFinding {
                    severity: FindingSeverity::Error,
                    code: "INVALID_STATION_COORDINATE".to_string(),
                    message: error.to_string(),
                    object_id: Some(item.id.clone()),
                });
            }
        }

        let mut all_station_ids = station_ids.clone();
        for station in &self.overrides.manual_stations {
            if !all_station_ids.insert(station.id.as_str()) {
                findings.push(ValidationFinding {
                    severity: FindingSeverity::Error,
                    code: "DUPLICATE_STATION_ID".to_string(),
                    message: "manual station id duplicates another station".to_string(),
                    object_id: Some(station.id.clone()),
                });
            }
            if station.state != IntentState::Manual && station.state != IntentState::Retired {
                findings.push(ValidationFinding {
                    severity: FindingSeverity::Error,
                    code: "INVALID_MANUAL_STATION_STATE".to_string(),
                    message: "designer-created station must be manual or retired".to_string(),
                    object_id: Some(station.id.clone()),
                });
            }
            let station_validation = validate_station_name(&station.name)
                .and_then(|()| validate_manual_archetype(&station.archetype))
                .and_then(|()| {
                    validate_coordinates(Some(station.source_lat), Some(station.source_lon))
                })
                .and_then(|()| validate_coordinates(Some(station.lat), Some(station.lon)));
            if let Err(error) = station_validation {
                findings.push(ValidationFinding {
                    severity: FindingSeverity::Error,
                    code: "INVALID_MANUAL_STATION".to_string(),
                    message: error.to_string(),
                    object_id: Some(station.id.clone()),
                });
            }
            if station.source_s_m < 0.0 || !station.source_s_m.is_finite() {
                findings.push(ValidationFinding {
                    severity: FindingSeverity::Error,
                    code: "INVALID_MANUAL_STATION_CHAINAGE".to_string(),
                    message: "manual station source chainage must be finite and non-negative"
                        .to_string(),
                    object_id: Some(station.id.clone()),
                });
            }
        }

        let mut line_ids: BTreeSet<&str> = self
            .base
            .lines
            .iter()
            .map(|line| line.name.as_str())
            .collect();
        let mut active_line_ids = line_ids.clone();
        for line in &self.overrides.manual_lines {
            if !line_ids.insert(line.id.as_str()) {
                findings.push(ValidationFinding {
                    severity: FindingSeverity::Error,
                    code: "DUPLICATE_LINE_ID".to_string(),
                    message: "manual line id duplicates another line".to_string(),
                    object_id: Some(line.id.clone()),
                });
            }
            if line.state != IntentState::Manual && line.state != IntentState::Retired {
                findings.push(ValidationFinding {
                    severity: FindingSeverity::Error,
                    code: "INVALID_MANUAL_LINE_STATE".to_string(),
                    message: "designer-created line must be manual or retired".to_string(),
                    object_id: Some(line.id.clone()),
                });
            }
            if line.state != IntentState::Retired {
                active_line_ids.insert(line.id.as_str());
            }
            if line.shape != "radial" || line.points.len() < 2 {
                findings.push(ValidationFinding {
                    severity: FindingSeverity::Error,
                    code: "INVALID_MANUAL_LINE_GEOMETRY".to_string(),
                    message: "manual line must be a radial with at least two points".to_string(),
                    object_id: Some(line.id.clone()),
                });
            }
            match line.routing_method.as_str() {
                "direct" => {
                    if !line.routing_source_ids.is_empty() || line.demand_weight.is_some() {
                        findings.push(ValidationFinding {
                            severity: FindingSeverity::Error,
                            code: "INVALID_DIRECT_ROUTE_PROVENANCE".to_string(),
                            message: "direct routes must not claim raster sources or demand weight"
                                .to_string(),
                            object_id: Some(line.id.clone()),
                        });
                    }
                }
                "demand-aware" => {
                    if line.routing_source_ids.is_empty() || line.demand_weight.is_none() {
                        findings.push(ValidationFinding {
                            severity: FindingSeverity::Error,
                            code: "MISSING_ROUTE_PROVENANCE".to_string(),
                            message: "demand-aware route must record source ids and demand weight"
                                .to_string(),
                            object_id: Some(line.id.clone()),
                        });
                    }
                }
                _ => findings.push(ValidationFinding {
                    severity: FindingSeverity::Error,
                    code: "UNKNOWN_ROUTING_METHOD".to_string(),
                    message: "manual line has an unknown routing method".to_string(),
                    object_id: Some(line.id.clone()),
                }),
            }
            for point in &line.points {
                if let Err(error) = validate_coordinates(Some(point.lat), Some(point.lon)) {
                    findings.push(ValidationFinding {
                        severity: FindingSeverity::Error,
                        code: "INVALID_MANUAL_LINE_COORDINATE".to_string(),
                        message: error.to_string(),
                        object_id: Some(line.id.clone()),
                    });
                    break;
                }
            }
        }
        for station in &self.overrides.manual_stations {
            if !line_ids.contains(station.line.as_str()) {
                findings.push(ValidationFinding {
                    severity: FindingSeverity::Error,
                    code: "UNKNOWN_MANUAL_STATION_LINE".to_string(),
                    message: "manual station refers to an unknown line".to_string(),
                    object_id: Some(station.id.clone()),
                });
            }
        }
        let mut seen_control_points = BTreeSet::new();
        for control in &self.overrides.line_control_points {
            if !line_ids.contains(control.line.as_str()) {
                findings.push(ValidationFinding {
                    severity: FindingSeverity::Error,
                    code: "UNKNOWN_CONTROL_POINT_LINE".to_string(),
                    message: "alignment control point refers to an unknown line".to_string(),
                    object_id: Some(control.id.clone()),
                });
            }
            if !seen_control_points.insert(control.id.as_str()) {
                findings.push(ValidationFinding {
                    severity: FindingSeverity::Error,
                    code: "DUPLICATE_CONTROL_POINT".to_string(),
                    message: "alignment control point id is duplicated".to_string(),
                    object_id: Some(control.id.clone()),
                });
            }
            if let Err(error) =
                validate_coordinates(Some(control.source_lat), Some(control.source_lon))
                    .and_then(|()| validate_coordinates(Some(control.lat), Some(control.lon)))
            {
                findings.push(ValidationFinding {
                    severity: FindingSeverity::Error,
                    code: "INVALID_CONTROL_POINT_COORDINATE".to_string(),
                    message: error.to_string(),
                    object_id: Some(control.id.clone()),
                });
            }
            if !(100.0..=20_000.0).contains(&control.influence_m) {
                findings.push(ValidationFinding {
                    severity: FindingSeverity::Error,
                    code: "INVALID_CONTROL_POINT_INFLUENCE".to_string(),
                    message: "control-point influence must be between 100 m and 20 km".to_string(),
                    object_id: Some(control.id.clone()),
                });
            }
        }
        let day_type_ids: BTreeSet<&str> = self
            .service_plan
            .day_types
            .iter()
            .map(|day| day.id.as_str())
            .collect();
        let mut seen_plans = BTreeSet::new();
        for plan in &self.service_plan.line_plans {
            if !line_ids.contains(plan.line.as_str()) {
                findings.push(service_finding(
                    FindingSeverity::Error,
                    "UNKNOWN_SERVICE_LINE",
                    "service plan refers to an unknown line",
                    plan,
                ));
            }
            if !day_type_ids.contains(plan.day_type.as_str()) {
                findings.push(service_finding(
                    FindingSeverity::Error,
                    "UNKNOWN_DAY_TYPE",
                    "service plan refers to an unknown day type",
                    plan,
                ));
            }
            if !seen_plans.insert((plan.line.as_str(), plan.day_type.as_str())) {
                findings.push(service_finding(
                    FindingSeverity::Error,
                    "DUPLICATE_SERVICE_PLAN",
                    "line and day type have more than one service plan",
                    plan,
                ));
            }
            if let Err(error) = validate_line_plan(plan) {
                findings.push(service_finding(
                    FindingSeverity::Error,
                    "INVALID_SERVICE_WINDOWS",
                    &error.to_string(),
                    plan,
                ));
            }
        }
        for line in active_line_ids {
            for day_type in &self.service_plan.day_types {
                if !seen_plans.contains(&(line, day_type.id.as_str())) {
                    findings.push(ValidationFinding {
                        severity: FindingSeverity::Error,
                        code: "MISSING_SERVICE_PLAN".to_string(),
                        message: format!(
                            "line {} has no service plan for day type {}",
                            line, day_type.id
                        ),
                        object_id: Some(line.to_string()),
                    });
                }
            }
        }
        for (_, day_type) in calendar_days(&self.service_plan) {
            if !day_type_ids.contains(day_type) {
                findings.push(ValidationFinding {
                    severity: FindingSeverity::Error,
                    code: "UNKNOWN_CALENDAR_DAY_TYPE".to_string(),
                    message: format!("calendar refers to unknown day type {day_type}"),
                    object_id: Some(day_type.to_string()),
                });
            }
        }
        findings
    }

    fn validate_effective_stations(&self, stations: &[CompiledStation]) -> Vec<ValidationFinding> {
        let mut findings = Vec::new();
        let active_ids: BTreeSet<&str> =
            stations.iter().map(|station| station.id.as_str()).collect();
        let mut active_lines: BTreeSet<&str> = self
            .base
            .lines
            .iter()
            .map(|line| line.name.as_str())
            .collect();
        active_lines.extend(
            self.overrides
                .manual_lines
                .iter()
                .filter(|line| line.state != IntentState::Retired)
                .map(|line| line.id.as_str()),
        );
        for line in active_lines {
            let count = stations
                .iter()
                .filter(|station| station.line == line)
                .count();
            if count < 2 {
                findings.push(ValidationFinding {
                    severity: FindingSeverity::Error,
                    code: "LINE_HAS_TOO_FEW_STATIONS".to_string(),
                    message: format!("line {line} requires at least two active stations"),
                    object_id: Some(line.to_string()),
                });
            }
        }
        let path = self.root.join(&self.config.inputs.simulator_scenario);
        match read_toml::<toml::Value>(&path) {
            Ok(scenario) => {
                for dispatch in scenario
                    .get("fleets")
                    .and_then(toml::Value::as_array)
                    .into_iter()
                    .flatten()
                    .flat_map(|fleet| {
                        fleet
                            .get("dispatch_points")
                            .and_then(toml::Value::as_array)
                            .into_iter()
                            .flatten()
                    })
                {
                    if let Some(id) = dispatch.get("station").and_then(toml::Value::as_str) {
                        if !active_ids.contains(id) {
                            findings.push(ValidationFinding {
                                severity: FindingSeverity::Error,
                                code: "RETIRED_DISPATCH_STATION".to_string(),
                                message:
                                    "a fleet dispatch point cannot reference a retired station"
                                        .to_string(),
                                object_id: Some(id.to_string()),
                            });
                        }
                    }
                }
            }
            Err(error) => findings.push(ValidationFinding {
                severity: FindingSeverity::Error,
                code: "INVALID_SIMULATOR_SOURCE".to_string(),
                message: error.to_string(),
                object_id: None,
            }),
        }
        findings
    }

    fn compute_service_metrics(&self, lines: &[CompiledLine]) -> Result<Vec<ServiceMetric>> {
        let lines_by_id: BTreeMap<&str, &CompiledLine> =
            lines.iter().map(|line| (line.id.as_str(), line)).collect();
        let assumptions = &self.config.planning;
        let mut metrics = Vec::with_capacity(self.service_plan.line_plans.len());
        for plan in &self.service_plan.line_plans {
            let line = lines_by_id
                .get(plan.line.as_str())
                .ok_or_else(|| anyhow!("unknown service line {:?}", plan.line))?;
            let one_way_min = (line.length_m / 1_000.0) / assumptions.average_speed_kmh * 60.0
                + line.station_count.saturating_sub(1) as f64 * assumptions.station_dwell_min;
            let cycle_time_min = if line.shape == "ring" {
                one_way_min + assumptions.terminal_turnaround_min
            } else {
                2.0 * (one_way_min + assumptions.terminal_turnaround_min)
            };
            let minimum_headway = plan
                .windows
                .iter()
                .map(|window| window.headway_min)
                .min()
                .unwrap_or(1);
            let peak_fleet = (cycle_time_min / f64::from(minimum_headway)).ceil() as u32;
            let peak_capacity_pphpd =
                assumptions.passenger_capacity_per_train * 60 / minimum_headway.max(1);
            let mut daily_service_km = 0.0;
            for window in &plan.windows {
                let (from, to) = normalized_interval(
                    &window.from,
                    &window.to,
                    parse_minutes(&plan.service_start)?,
                )?;
                let departures_per_direction =
                    (f64::from(to - from) / f64::from(window.headway_min)).ceil();
                daily_service_km += departures_per_direction * 2.0 * line.length_m / 1_000.0;
            }
            metrics.push(ServiceMetric {
                line: plan.line.clone(),
                day_type: plan.day_type.clone(),
                cycle_time_min,
                peak_fleet,
                peak_capacity_pphpd,
                daily_service_km,
            });
        }
        Ok(metrics)
    }

    fn candidate_network_geojson(&self, snapshot: &CompiledSnapshot) -> Result<serde_json::Value> {
        let geometries = self.regenerated_line_geometries(&snapshot.stations)?;
        let mut features = Vec::new();
        for feature in self
            .corridor
            .get("features")
            .and_then(serde_json::Value::as_array)
            .into_iter()
            .flatten()
            .filter(|feature| {
                feature
                    .get("geometry")
                    .and_then(|geometry| geometry.get("type"))
                    .and_then(serde_json::Value::as_str)
                    == Some("LineString")
            })
        {
            let line = feature
                .get("properties")
                .and_then(|properties| properties.get("name"))
                .and_then(serde_json::Value::as_str)
                .ok_or_else(|| anyhow!("corridor line feature has no name"))?;
            let geometry = geometries
                .get(line)
                .ok_or_else(|| anyhow!("no regenerated geometry for line {line}"))?;
            let mut candidate = feature.clone();
            candidate["geometry"]["coordinates"] = serde_json::to_value(&geometry.effective)?;
            candidate["properties"]["revision_id"] =
                serde_json::Value::String(snapshot.revision_id.clone());
            features.push(candidate);
        }
        for line in snapshot
            .lines
            .iter()
            .filter(|line| line.state == IntentState::Manual)
        {
            let geometry = geometries
                .get(&line.id)
                .ok_or_else(|| anyhow!("no regenerated geometry for line {}", line.id))?;
            features.push(serde_json::json!({
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": geometry.effective,
                },
                "properties": {
                    "kind": "manual-line",
                    "name": line.id,
                    "label": line.name,
                    "shape": line.shape,
                    "routing_method": line.routing_method,
                    "routing_source_ids": line.routing_source_ids,
                    "demand_weight": line.demand_weight,
                    "intent_state": line.state,
                    "reason": line.reason,
                    "revision_id": snapshot.revision_id,
                },
            }));
        }
        features.extend(snapshot.stations.iter().map(|station| {
            serde_json::json!({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [station.lon, station.lat],
                },
                "properties": {
                    "kind": "station",
                    "id": station.id,
                    "name": station.name,
                    "line": station.line,
                    "s_m": station.s_m,
                    "archetype": station.archetype,
                    "intent_state": station.state,
                    "revision_id": snapshot.revision_id,
                },
            })
        }));
        features.extend(snapshot.line_control_points.iter().map(|control| {
            serde_json::json!({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [control.lon, control.lat],
                },
                "properties": {
                    "kind": "line-control-point",
                    "id": control.id,
                    "line": control.line,
                    "source_lat": control.source_lat,
                    "source_lon": control.source_lon,
                    "influence_m": control.influence_m,
                    "distance_m": control.distance_m,
                    "intent_state": control.state,
                    "reason": control.reason,
                    "revision_id": snapshot.revision_id,
                },
            })
        }));
        Ok(serde_json::json!({
            "type": "FeatureCollection",
            "osr_schema_version": 1,
            "osr_revision_id": snapshot.revision_id,
            "features": features,
        }))
    }

    fn source_line_geometries(&self) -> Result<BTreeMap<String, Vec<[f64; 2]>>> {
        let mut geometries = BTreeMap::new();
        for feature in self
            .corridor
            .get("features")
            .and_then(serde_json::Value::as_array)
            .into_iter()
            .flatten()
            .filter(|feature| feature["geometry"]["type"].as_str() == Some("LineString"))
        {
            let line = feature["properties"]["name"]
                .as_str()
                .ok_or_else(|| anyhow!("corridor line feature has no name"))?;
            geometries.insert(line.to_string(), geojson_coordinates(feature)?);
        }
        for line in self
            .overrides
            .manual_lines
            .iter()
            .filter(|line| line.state != IntentState::Retired)
        {
            geometries.insert(
                line.id.clone(),
                line.points
                    .iter()
                    .map(|point| [point.lon, point.lat])
                    .collect(),
            );
        }
        Ok(geometries)
    }

    fn regenerated_line_geometries(
        &self,
        effective_stations: &[CompiledStation],
    ) -> Result<BTreeMap<String, LineGeometry>> {
        let effective_by_id: BTreeMap<&str, &CompiledStation> = effective_stations
            .iter()
            .map(|station| (station.id.as_str(), station))
            .collect();
        let mut output = BTreeMap::new();
        for (line, source) in self.source_line_geometries()? {
            let line = line.as_str();
            let moved_on_line = self.base.stations.iter().any(|station| {
                station.line == line
                    && effective_by_id
                        .get(station.id.as_str())
                        .is_some_and(|effective| {
                            haversine_m(station.lat, station.lon, effective.lat, effective.lon)
                                > 0.01
                        })
            }) || self.overrides.manual_stations.iter().any(|station| {
                station.line == line
                    && station.state != IntentState::Retired
                    && haversine_m(
                        station.source_lat,
                        station.source_lon,
                        station.lat,
                        station.lon,
                    ) > 0.01
            }) || self.overrides.line_control_points.iter().any(|control| {
                control.line == line
                    && control.state != IntentState::Retired
                    && haversine_m(
                        control.source_lat,
                        control.source_lon,
                        control.lat,
                        control.lon,
                    ) > 0.01
            });
            if !moved_on_line {
                output.insert(
                    line.to_string(),
                    LineGeometry {
                        effective: source.clone(),
                        source,
                    },
                );
                continue;
            }
            let cumulative = cumulative_polyline_m(&source);
            let mut controls = Vec::new();
            for station in self.base.stations.iter().filter(|station| {
                station.line == line
                    && effective_by_id
                        .get(station.id.as_str())
                        .is_some_and(|effective| {
                            effective.state == IntentState::Locked
                                || haversine_m(
                                    station.lat,
                                    station.lon,
                                    effective.lat,
                                    effective.lon,
                                ) > 0.01
                        })
            }) {
                let effective = effective_by_id[station.id.as_str()];
                let index = nearest_coordinate_index(&source, station.lon, station.lat);
                controls.push(GeometryControl {
                    index,
                    chainage_m: cumulative[index],
                    delta_lon: effective.lon - station.lon,
                    delta_lat: effective.lat - station.lat,
                    target_lon: effective.lon,
                    target_lat: effective.lat,
                    influence_m: self.config.planning.geometry_regeneration_radius_m.max(1.0),
                });
            }
            for control in self
                .overrides
                .line_control_points
                .iter()
                .filter(|control| control.line == line && control.state != IntentState::Retired)
            {
                let index =
                    nearest_coordinate_index(&source, control.source_lon, control.source_lat);
                controls.push(GeometryControl {
                    index,
                    chainage_m: cumulative[index],
                    delta_lon: control.lon - control.source_lon,
                    delta_lat: control.lat - control.source_lat,
                    target_lon: control.lon,
                    target_lat: control.lat,
                    influence_m: control.influence_m.max(1.0),
                });
            }
            for station in self.overrides.manual_stations.iter().filter(|station| {
                station.line == line
                    && station.state != IntentState::Retired
                    && haversine_m(
                        station.source_lat,
                        station.source_lon,
                        station.lat,
                        station.lon,
                    ) > 0.01
            }) {
                let index =
                    nearest_coordinate_index(&source, station.source_lon, station.source_lat);
                controls.push(GeometryControl {
                    index,
                    chainage_m: cumulative[index],
                    delta_lon: station.lon - station.source_lon,
                    delta_lat: station.lat - station.source_lat,
                    target_lon: station.lon,
                    target_lat: station.lat,
                    influence_m: self.config.planning.geometry_regeneration_radius_m.max(1.0),
                });
            }
            let mut effective = source.clone();
            for (index, coordinate) in effective.iter_mut().enumerate() {
                let mut longitude_offset = 0.0;
                let mut latitude_offset = 0.0;
                let mut total_weight = 0.0;
                for control in &controls {
                    let distance = (cumulative[index] - control.chainage_m).abs();
                    let weight = (1.0 - distance / control.influence_m).max(0.0);
                    longitude_offset += control.delta_lon * weight;
                    latitude_offset += control.delta_lat * weight;
                    total_weight += weight;
                }
                if total_weight > 0.0 {
                    let blend = total_weight.min(1.0);
                    coordinate[0] += longitude_offset / total_weight * blend;
                    coordinate[1] += latitude_offset / total_weight * blend;
                }
            }
            for control in controls {
                effective[control.index] = [control.target_lon, control.target_lat];
            }
            output.insert(line.to_string(), LineGeometry { source, effective });
        }
        Ok(output)
    }

    fn scenario_for_day_type(&self, day_type: &str, snapshot: &CompiledSnapshot) -> Result<String> {
        let path = self.root.join(&self.config.inputs.simulator_scenario);
        let text =
            fs::read_to_string(&path).with_context(|| format!("reading {}", path.display()))?;
        let mut scenario: toml::Value =
            toml::from_str(&text).with_context(|| format!("parsing {}", path.display()))?;
        self.apply_scenario_geometry(&mut scenario, snapshot)?;
        let fleets = scenario
            .get_mut("fleets")
            .and_then(toml::Value::as_array_mut)
            .ok_or_else(|| anyhow!("simulator scenario has no [[fleets]] array"))?;
        let existing_fleet_lines: BTreeSet<String> = fleets
            .iter()
            .filter_map(|fleet| fleet.get("line").and_then(toml::Value::as_str))
            .map(str::to_string)
            .collect();
        for fleet in fleets.iter_mut() {
            let line = fleet
                .get("line")
                .and_then(toml::Value::as_str)
                .ok_or_else(|| anyhow!("simulator fleet has no line id"))?
                .to_string();
            let plan = self
                .service_plan
                .line_plans
                .iter()
                .find(|plan| plan.line == line && plan.day_type == day_type)
                .ok_or_else(|| anyhow!("no {day_type} service plan for simulator fleet {line}"))?;
            let fleet_table = fleet
                .as_table_mut()
                .ok_or_else(|| anyhow!("simulator fleet is not a TOML table"))?;
            fleet_table.insert(
                "service_start".to_string(),
                toml::Value::String(plan.service_start.clone()),
            );
            fleet_table.insert(
                "service_end".to_string(),
                toml::Value::String(plan.service_end.clone()),
            );
            let fleet_count = snapshot
                .service_metrics
                .iter()
                .find(|metric| metric.line == line && metric.day_type == day_type)
                .map(|metric| metric.peak_fleet)
                .ok_or_else(|| anyhow!("no compiled fleet metric for {line}:{day_type}"))?;
            fleet_table.insert(
                "trainset_count".to_string(),
                toml::Value::Integer(i64::from(fleet_count)),
            );
            let windows = plan
                .windows
                .iter()
                .map(|window| {
                    let mut table = toml::map::Map::new();
                    table.insert("from".to_string(), toml::Value::String(window.from.clone()));
                    table.insert("to".to_string(), toml::Value::String(window.to.clone()));
                    table.insert(
                        "headway_min".to_string(),
                        toml::Value::Integer(i64::from(window.headway_min)),
                    );
                    toml::Value::Table(table)
                })
                .collect();
            fleet_table.insert("schedule".to_string(), toml::Value::Array(windows));
        }
        for line in snapshot.lines.iter().filter(|line| {
            line.state == IntentState::Manual && !existing_fleet_lines.contains(&line.id)
        }) {
            let plan = self
                .service_plan
                .line_plans
                .iter()
                .find(|plan| plan.line == line.id && plan.day_type == day_type)
                .ok_or_else(|| anyhow!("no {day_type} service plan for {}", line.id))?;
            let fleet_count = snapshot
                .service_metrics
                .iter()
                .find(|metric| metric.line == line.id && metric.day_type == day_type)
                .map(|metric| metric.peak_fleet)
                .ok_or_else(|| anyhow!("no compiled fleet metric for {}:{day_type}", line.id))?;
            let mut stations = snapshot
                .stations
                .iter()
                .filter(|station| station.line == line.id)
                .collect::<Vec<_>>();
            stations.sort_by(|left, right| left.s_m.total_cmp(&right.s_m));
            let first = stations
                .first()
                .ok_or_else(|| anyhow!("manual line {} has no first station", line.id))?;
            let last = stations
                .last()
                .ok_or_else(|| anyhow!("manual line {} has no last station", line.id))?;
            let dispatch_points = [
                (first.id.as_str(), "forward"),
                (last.id.as_str(), "reverse"),
            ]
            .into_iter()
            .map(|(station, heading)| {
                let mut point = toml::map::Map::new();
                point.insert(
                    "station".to_string(),
                    toml::Value::String(station.to_string()),
                );
                point.insert(
                    "heading".to_string(),
                    toml::Value::String(heading.to_string()),
                );
                toml::Value::Table(point)
            })
            .collect();
            let windows = plan
                .windows
                .iter()
                .map(|window| {
                    let mut table = toml::map::Map::new();
                    table.insert("from".to_string(), toml::Value::String(window.from.clone()));
                    table.insert("to".to_string(), toml::Value::String(window.to.clone()));
                    table.insert(
                        "headway_min".to_string(),
                        toml::Value::Integer(i64::from(window.headway_min)),
                    );
                    toml::Value::Table(table)
                })
                .collect();
            let mut fleet = toml::map::Map::new();
            fleet.insert("line".to_string(), toml::Value::String(line.id.clone()));
            fleet.insert(
                "trainset_count".to_string(),
                toml::Value::Integer(i64::from(fleet_count)),
            );
            fleet.insert(
                "dispatch_points".to_string(),
                toml::Value::Array(dispatch_points),
            );
            fleet.insert(
                "service_start".to_string(),
                toml::Value::String(plan.service_start.clone()),
            );
            fleet.insert(
                "service_end".to_string(),
                toml::Value::String(plan.service_end.clone()),
            );
            fleet.insert("schedule".to_string(), toml::Value::Array(windows));
            fleets.push(toml::Value::Table(fleet));
        }
        let body = toml::to_string_pretty(&scenario).context("serializing scenario")?;
        let mut output = format!(
            "# Generated by OSR City Studio for project {} and day type {}.\n# Source service plan: {}\n\n{}",
            self.config.project.id, day_type, self.config.inputs.service_plan, body
        );
        output.push('\n');
        Ok(output)
    }

    fn apply_scenario_geometry(
        &self,
        scenario: &mut toml::Value,
        snapshot: &CompiledSnapshot,
    ) -> Result<()> {
        let geometries = self.regenerated_line_geometries(&snapshot.stations)?;
        let mut changed_lines: BTreeSet<&str> = snapshot
            .changes
            .iter()
            .map(|change| change.line.as_str())
            .collect();
        changed_lines.extend(
            snapshot
                .line_control_points
                .iter()
                .filter(|control| control.distance_m > 0.01)
                .map(|control| control.line.as_str()),
        );
        changed_lines.extend(
            snapshot
                .lines
                .iter()
                .filter(|line| line.state == IntentState::Manual)
                .map(|line| line.id.as_str()),
        );
        for line in &self.base.lines {
            let source_ids: BTreeSet<&str> = self
                .base
                .stations
                .iter()
                .filter(|station| station.line == line.name)
                .map(|station| station.id.as_str())
                .collect();
            let candidate_ids: BTreeSet<&str> = snapshot
                .stations
                .iter()
                .filter(|station| station.line == line.name)
                .map(|station| station.id.as_str())
                .collect();
            if source_ids != candidate_ids {
                changed_lines.insert(line.name.as_str());
            }
        }

        let station_definitions = scenario
            .get_mut("stations")
            .and_then(toml::Value::as_array_mut)
            .ok_or_else(|| anyhow!("simulator scenario has no [[stations]] array"))?;
        let mut existing_definitions: BTreeMap<String, toml::Value> =
            std::mem::take(station_definitions)
                .into_iter()
                .filter_map(|definition| {
                    let id = definition
                        .get("id")
                        .and_then(toml::Value::as_str)
                        .map(str::to_string)?;
                    Some((id, definition))
                })
                .collect();
        for station in &snapshot.stations {
            if let Some(definition) = existing_definitions.remove(&station.id) {
                station_definitions.push(definition);
            } else {
                let mut definition = toml::map::Map::new();
                definition.insert("id".to_string(), toml::Value::String(station.id.clone()));
                definition.insert(
                    "name".to_string(),
                    toml::Value::String(station.name.clone()),
                );
                definition.insert("charging_power_kw".to_string(), toml::Value::Integer(0));
                definition.insert(
                    "dwell_seconds".to_string(),
                    toml::Value::Integer(
                        (self.config.planning.station_dwell_min * 60.0).round() as i64
                    ),
                );
                if station.archetype == "terminal" {
                    definition.insert("is_terminal".to_string(), toml::Value::Boolean(true));
                }
                station_definitions.push(toml::Value::Table(definition));
            }
        }

        let lines = scenario
            .get_mut("lines")
            .and_then(toml::Value::as_array_mut)
            .ok_or_else(|| anyhow!("simulator scenario has no [[lines]] array"))?;
        let existing_line_ids: BTreeSet<String> = lines
            .iter()
            .filter_map(|line| line.get("id").and_then(toml::Value::as_str))
            .map(str::to_string)
            .collect();
        for line in lines.iter_mut() {
            let line_id = line
                .get("id")
                .and_then(toml::Value::as_str)
                .ok_or_else(|| anyhow!("simulator line has no id"))?
                .to_string();
            if !changed_lines.contains(line_id.as_str()) {
                continue;
            }
            let geometry = geometries
                .get(&line_id)
                .ok_or_else(|| anyhow!("no effective geometry for simulator line {line_id}"))?;
            let cumulative = cumulative_polyline_m(&geometry.effective);
            let total_length = cumulative.last().copied().unwrap_or(0.0);
            let is_ring = line
                .get("is_ring")
                .and_then(toml::Value::as_bool)
                .unwrap_or(false);
            let line_table = line
                .as_table_mut()
                .ok_or_else(|| anyhow!("simulator line is not a table"))?;
            let mut ordered_stations = snapshot
                .stations
                .iter()
                .filter(|station| station.line == line_id)
                .map(|station| {
                    let index =
                        nearest_coordinate_index(&geometry.effective, station.lon, station.lat);
                    (cumulative[index], station)
                })
                .collect::<Vec<_>>();
            ordered_stations.sort_by(|left, right| {
                left.0
                    .total_cmp(&right.0)
                    .then_with(|| left.1.id.cmp(&right.1.id))
            });
            let mut station_refs = Vec::with_capacity(ordered_stations.len());
            let mut previous_chainage = 0.0;
            for (position, (chainage, station)) in ordered_stations.iter().enumerate() {
                if position > 0 && *chainage <= previous_chainage {
                    bail!(
                        "effective geometry places station {} at the same or an earlier chainage on {line_id}",
                        station.id
                    );
                }
                let distance = if position == 0 {
                    0
                } else {
                    (*chainage - previous_chainage).round().max(1.0) as i64
                };
                let mut station_ref = toml::map::Map::new();
                station_ref.insert("id".to_string(), toml::Value::String(station.id.clone()));
                station_ref.insert(
                    "distance_from_prev_m".to_string(),
                    toml::Value::Integer(distance),
                );
                station_refs.push(toml::Value::Table(station_ref));
                previous_chainage = *chainage;
            }
            line_table.insert("stations".to_string(), toml::Value::Array(station_refs));
            if is_ring {
                let wrap = (total_length - previous_chainage).round().max(1.0) as i64;
                line_table.insert("ring_wrap_length_m".to_string(), toml::Value::Integer(wrap));
            }
        }
        for compiled in snapshot.lines.iter().filter(|line| {
            line.state == IntentState::Manual && !existing_line_ids.contains(&line.id)
        }) {
            let geometry = geometries.get(&compiled.id).ok_or_else(|| {
                anyhow!("no effective geometry for simulator line {}", compiled.id)
            })?;
            let station_refs = scenario_station_refs(&compiled.id, geometry, snapshot)?;
            let mut line = toml::map::Map::new();
            line.insert("id".to_string(), toml::Value::String(compiled.id.clone()));
            line.insert(
                "name".to_string(),
                toml::Value::String(compiled.name.clone()),
            );
            line.insert("is_ring".to_string(), toml::Value::Boolean(false));
            line.insert("stations".to_string(), toml::Value::Array(station_refs));
            lines.push(toml::Value::Table(line));
        }
        Ok(())
    }
}

fn scenario_station_refs(
    line_id: &str,
    geometry: &LineGeometry,
    snapshot: &CompiledSnapshot,
) -> Result<Vec<toml::Value>> {
    let cumulative = cumulative_polyline_m(&geometry.effective);
    let mut ordered_stations = snapshot
        .stations
        .iter()
        .filter(|station| station.line == line_id)
        .map(|station| {
            let index = nearest_coordinate_index(&geometry.effective, station.lon, station.lat);
            (cumulative[index], station)
        })
        .collect::<Vec<_>>();
    ordered_stations.sort_by(|left, right| {
        left.0
            .total_cmp(&right.0)
            .then_with(|| left.1.id.cmp(&right.1.id))
    });
    let mut refs = Vec::with_capacity(ordered_stations.len());
    let mut previous_chainage = 0.0;
    for (position, (chainage, station)) in ordered_stations.iter().enumerate() {
        if position > 0 && *chainage <= previous_chainage {
            bail!(
                "effective geometry places station {} at the same or an earlier chainage on {line_id}",
                station.id
            );
        }
        let distance = if position == 0 {
            0
        } else {
            (*chainage - previous_chainage).round().max(1.0) as i64
        };
        let mut station_ref = toml::map::Map::new();
        station_ref.insert("id".to_string(), toml::Value::String(station.id.clone()));
        station_ref.insert(
            "distance_from_prev_m".to_string(),
            toml::Value::Integer(distance),
        );
        refs.push(toml::Value::Table(station_ref));
        previous_chainage = *chainage;
    }
    Ok(refs)
}

fn compare_snapshots(base: &CompiledSnapshot, candidate: &CompiledSnapshot) -> RevisionComparison {
    let base_stations: BTreeMap<&str, &CompiledStation> = base
        .stations
        .iter()
        .map(|station| (station.id.as_str(), station))
        .collect();
    let candidate_stations: BTreeMap<&str, &CompiledStation> = candidate
        .stations
        .iter()
        .map(|station| (station.id.as_str(), station))
        .collect();
    let station_ids: BTreeSet<&str> = base_stations
        .keys()
        .chain(candidate_stations.keys())
        .copied()
        .collect();
    let mut stations = Vec::new();
    for id in station_ids {
        let before = base_stations.get(id).copied();
        let after = candidate_stations.get(id).copied();
        let (kind, movement_m) = match (before, after) {
            (None, Some(_)) => ("added", None),
            (Some(_), None) => ("removed", None),
            (Some(before), Some(after)) if !stations_semantically_equal(before, after) => {
                let movement = haversine_m(before.lat, before.lon, after.lat, after.lon);
                if movement > 0.01 {
                    ("moved", Some(movement))
                } else {
                    ("modified", None)
                }
            }
            _ => continue,
        };
        stations.push(RevisionStationDiff {
            id: id.to_string(),
            kind: kind.to_string(),
            before: before.cloned(),
            after: after.cloned(),
            movement_m,
        });
    }

    let base_controls: BTreeMap<&str, &CompiledControlPoint> = base
        .line_control_points
        .iter()
        .map(|control| (control.id.as_str(), control))
        .collect();
    let candidate_controls: BTreeMap<&str, &CompiledControlPoint> = candidate
        .line_control_points
        .iter()
        .map(|control| (control.id.as_str(), control))
        .collect();
    let control_ids: BTreeSet<&str> = base_controls
        .keys()
        .chain(candidate_controls.keys())
        .copied()
        .collect();
    let mut controls = Vec::new();
    for id in control_ids {
        let before = base_controls.get(id).copied();
        let after = candidate_controls.get(id).copied();
        let (kind, movement_m) = match (before, after) {
            (None, Some(_)) => ("added", None),
            (Some(_), None) => ("removed", None),
            (Some(before), Some(after)) if !controls_semantically_equal(before, after) => {
                let movement = haversine_m(before.lat, before.lon, after.lat, after.lon);
                if movement > 0.01 {
                    ("moved", Some(movement))
                } else {
                    ("modified", None)
                }
            }
            _ => continue,
        };
        controls.push(RevisionControlDiff {
            id: id.to_string(),
            kind: kind.to_string(),
            before: before.cloned(),
            after: after.cloned(),
            movement_m,
        });
    }

    let base_lines: BTreeMap<&str, &CompiledLine> = base
        .lines
        .iter()
        .map(|line| (line.id.as_str(), line))
        .collect();
    let candidate_lines: BTreeMap<&str, &CompiledLine> = candidate
        .lines
        .iter()
        .map(|line| (line.id.as_str(), line))
        .collect();
    let line_ids: BTreeSet<&str> = base_lines
        .keys()
        .chain(candidate_lines.keys())
        .copied()
        .collect();
    let mut lines = Vec::new();
    for id in line_ids {
        let before = base_lines.get(id).copied();
        let after = candidate_lines.get(id).copied();
        if match (before, after) {
            (Some(before), Some(after)) => lines_semantically_equal(before, after),
            (None, None) => true,
            _ => false,
        } {
            continue;
        }
        lines.push(RevisionLineDiff {
            id: id.to_string(),
            before: before.cloned(),
            after: after.cloned(),
            before_length_m: before.map(|line| line.length_m),
            after_length_m: after.map(|line| line.length_m),
            length_delta_m: after.map_or(0.0, |line| line.length_m)
                - before.map_or(0.0, |line| line.length_m),
            station_delta: after.map_or(0, |line| line.station_count as i64)
                - before.map_or(0, |line| line.station_count as i64),
        });
    }

    let base_services: BTreeMap<(&str, &str), &ServiceMetric> = base
        .service_metrics
        .iter()
        .map(|metric| ((metric.line.as_str(), metric.day_type.as_str()), metric))
        .collect();
    let candidate_services: BTreeMap<(&str, &str), &ServiceMetric> = candidate
        .service_metrics
        .iter()
        .map(|metric| ((metric.line.as_str(), metric.day_type.as_str()), metric))
        .collect();
    let compare_plans = base.service_plan.is_some() && candidate.service_plan.is_some();
    let base_plans: BTreeMap<(&str, &str), &LineServicePlan> = base
        .service_plan
        .as_ref()
        .into_iter()
        .flat_map(|plan| &plan.line_plans)
        .map(|plan| ((plan.line.as_str(), plan.day_type.as_str()), plan))
        .collect();
    let candidate_plans: BTreeMap<(&str, &str), &LineServicePlan> = candidate
        .service_plan
        .as_ref()
        .into_iter()
        .flat_map(|plan| &plan.line_plans)
        .map(|plan| ((plan.line.as_str(), plan.day_type.as_str()), plan))
        .collect();
    let service_ids: BTreeSet<(&str, &str)> = base_services
        .keys()
        .chain(candidate_services.keys())
        .chain(base_plans.keys())
        .chain(candidate_plans.keys())
        .copied()
        .collect();
    let mut services = Vec::new();
    for (line, day_type) in service_ids {
        let before = base_services.get(&(line, day_type)).copied();
        let after = candidate_services.get(&(line, day_type)).copied();
        let metrics_equal = match (before, after) {
            (Some(before), Some(after)) => services_semantically_equal(before, after),
            (None, None) => true,
            _ => false,
        };
        let before_plan = compare_plans
            .then(|| base_plans.get(&(line, day_type)).copied())
            .flatten();
        let after_plan = compare_plans
            .then(|| candidate_plans.get(&(line, day_type)).copied())
            .flatten();
        let plans_equal = !compare_plans || before_plan == after_plan;
        if metrics_equal && plans_equal {
            continue;
        }
        let kind = match (before_plan, after_plan, before, after) {
            (None, Some(_), _, _) | (_, _, None, Some(_)) => "added",
            (Some(_), None, _, _) | (_, _, Some(_), None) => "removed",
            _ => "modified",
        };
        services.push(RevisionServiceDiff {
            line: line.to_string(),
            day_type: day_type.to_string(),
            kind: kind.to_string(),
            before: before_plan.cloned(),
            after: after_plan.cloned(),
            peak_fleet_delta: after.map_or(0, |metric| i64::from(metric.peak_fleet))
                - before.map_or(0, |metric| i64::from(metric.peak_fleet)),
            capacity_delta_pphpd: after.map_or(0, |metric| i64::from(metric.peak_capacity_pphpd))
                - before.map_or(0, |metric| i64::from(metric.peak_capacity_pphpd)),
            daily_service_km_delta: after.map_or(0.0, |metric| metric.daily_service_km)
                - before.map_or(0.0, |metric| metric.daily_service_km),
        });
    }

    let base_coordination: BTreeMap<&str, &CoordinationIssue> = base
        .coordination
        .issues
        .iter()
        .map(|issue| (issue.id.as_str(), issue))
        .collect();
    let candidate_coordination: BTreeMap<&str, &CoordinationIssue> = candidate
        .coordination
        .issues
        .iter()
        .map(|issue| (issue.id.as_str(), issue))
        .collect();
    let coordination_ids: BTreeSet<&str> = base_coordination
        .keys()
        .chain(candidate_coordination.keys())
        .copied()
        .collect();
    let mut coordination = Vec::new();
    for id in coordination_ids {
        let before = base_coordination.get(id).copied();
        let after = candidate_coordination.get(id).copied();
        if before == after {
            continue;
        }
        coordination.push(RevisionCoordinationDiff {
            id: id.to_string(),
            kind: match (before, after) {
                (None, Some(_)) => "added",
                (Some(_), None) => "removed",
                _ => "modified",
            }
            .to_string(),
            before: before.cloned(),
            after: after.cloned(),
        });
    }

    RevisionComparison {
        base_revision_id: base.revision_id.clone(),
        candidate_revision_id: candidate.revision_id.clone(),
        summary: RevisionSummaryDiff {
            route_km: candidate.summary.route_km - base.summary.route_km,
            station_count: candidate.summary.station_count as i64
                - base.summary.station_count as i64,
            manual_station_count: candidate.summary.manual_station_count as i64
                - base.summary.manual_station_count as i64,
            manual_line_count: candidate.summary.manual_line_count as i64
                - base.summary.manual_line_count as i64,
            peak_fleet: i64::from(candidate.summary.peak_fleet)
                - i64::from(base.summary.peak_fleet),
            weekly_service_km: candidate.summary.weekly_service_km - base.summary.weekly_service_km,
        },
        stations,
        controls,
        lines,
        services,
        coordination,
    }
}

fn stations_semantically_equal(left: &CompiledStation, right: &CompiledStation) -> bool {
    left.id == right.id
        && left.name == right.name
        && left.line == right.line
        && haversine_m(left.lat, left.lon, right.lat, right.lon) <= 0.01
        && (left.s_m - right.s_m).abs() <= 0.001
        && left.archetype == right.archetype
        && left.state == right.state
        && left.reason == right.reason
}

fn controls_semantically_equal(left: &CompiledControlPoint, right: &CompiledControlPoint) -> bool {
    left.id == right.id
        && left.line == right.line
        && left.state == right.state
        && haversine_m(
            left.source_lat,
            left.source_lon,
            right.source_lat,
            right.source_lon,
        ) <= 0.01
        && haversine_m(left.lat, left.lon, right.lat, right.lon) <= 0.01
        && (left.influence_m - right.influence_m).abs() <= 0.001
        && left.reason == right.reason
}

fn lines_semantically_equal(left: &CompiledLine, right: &CompiledLine) -> bool {
    let left_name = if left.name.is_empty() {
        &left.id
    } else {
        &left.name
    };
    let right_name = if right.name.is_empty() {
        &right.id
    } else {
        &right.name
    };
    left.id == right.id
        && left_name == right_name
        && left.shape == right.shape
        && (left.length_m - right.length_m).abs() <= 0.001
        && left.station_count == right.station_count
        && normalized_routing_method(left) == normalized_routing_method(right)
        && left.routing_source_ids == right.routing_source_ids
        && optional_f32_equal(left.demand_weight, right.demand_weight)
        && left.state == right.state
        && left.reason == right.reason
}

fn normalized_routing_method(line: &CompiledLine) -> &str {
    if line.routing_method.is_empty() {
        if line.state == IntentState::Generated {
            "generated-source"
        } else {
            "direct"
        }
    } else {
        line.routing_method.as_str()
    }
}

fn optional_f32_equal(left: Option<f32>, right: Option<f32>) -> bool {
    match (left, right) {
        (Some(left), Some(right)) => (left - right).abs() <= 0.000_001,
        (None, None) => true,
        _ => false,
    }
}

fn services_semantically_equal(left: &ServiceMetric, right: &ServiceMetric) -> bool {
    left.line == right.line
        && left.day_type == right.day_type
        && (left.cycle_time_min - right.cycle_time_min).abs() <= 0.000_001
        && left.peak_fleet == right.peak_fleet
        && left.peak_capacity_pphpd == right.peak_capacity_pphpd
        && (left.daily_service_km - right.daily_service_km).abs() <= 0.000_001
}

fn validate_revision_id(revision_id: &str) -> Result<()> {
    if revision_id.len() != 20
        || !revision_id.starts_with("osr-")
        || !revision_id[4..]
            .bytes()
            .all(|byte| byte.is_ascii_hexdigit())
    {
        bail!("invalid revision id {revision_id:?}");
    }
    Ok(())
}

fn validate_coordination_decision(
    status: CoordinationStatus,
    resolution: &str,
    reviewed_by: &str,
) -> Result<()> {
    if matches!(
        status,
        CoordinationStatus::Resolved | CoordinationStatus::Closed
    ) {
        if resolution.trim().len() < 12 {
            bail!("resolved or closed coordination issues require a substantive resolution");
        }
        if reviewed_by.trim().is_empty() {
            bail!("resolved or closed coordination issues require a reviewer");
        }
    }
    Ok(())
}

fn is_custom_coordination_id(id: &str) -> bool {
    id.len() == 23
        && id.starts_with("custom-")
        && id[7..]
            .bytes()
            .all(|byte| byte.is_ascii_digit() || (b'a'..=b'f').contains(&byte))
}

fn validate_custom_coordination_issue(
    title: &str,
    description: &str,
    asset_ids: &[String],
) -> Result<()> {
    if !(4..=160).contains(&title.trim().len()) {
        bail!("custom coordination issue title must contain 4 to 160 characters");
    }
    if !(12..=2_000).contains(&description.trim().len()) {
        bail!("custom coordination issue description must contain 12 to 2000 characters");
    }
    if asset_ids.is_empty() || asset_ids.len() > 50 {
        bail!("custom coordination issue must select 1 to 50 IFC assets");
    }
    let mut unique = BTreeSet::new();
    for asset_id in asset_ids {
        if !asset_id.starts_with("OSR-DT-")
            || !asset_id
                .bytes()
                .all(|byte| byte.is_ascii_uppercase() || byte.is_ascii_digit() || byte == b'-')
        {
            bail!("custom coordination issue contains invalid asset id {asset_id:?}");
        }
        if !unique.insert(asset_id) {
            bail!("custom coordination issue repeats asset id {asset_id:?}");
        }
    }
    Ok(())
}

fn geojson_coordinates(feature: &serde_json::Value) -> Result<Vec<[f64; 2]>> {
    feature
        .get("geometry")
        .and_then(|geometry| geometry.get("coordinates"))
        .and_then(serde_json::Value::as_array)
        .ok_or_else(|| anyhow!("line feature has no coordinate array"))?
        .iter()
        .map(|coordinate| {
            let values = coordinate
                .as_array()
                .ok_or_else(|| anyhow!("line coordinate is not an array"))?;
            if values.len() < 2 {
                bail!("line coordinate has fewer than two values");
            }
            let lon = values[0]
                .as_f64()
                .ok_or_else(|| anyhow!("line longitude is not numeric"))?;
            let lat = values[1]
                .as_f64()
                .ok_or_else(|| anyhow!("line latitude is not numeric"))?;
            Ok([lon, lat])
        })
        .collect()
}

fn cumulative_polyline_m(coordinates: &[[f64; 2]]) -> Vec<f64> {
    let mut cumulative = Vec::with_capacity(coordinates.len());
    cumulative.push(0.0);
    for pair in coordinates.windows(2) {
        let distance = haversine_m(pair[0][1], pair[0][0], pair[1][1], pair[1][0]);
        cumulative.push(cumulative.last().copied().unwrap_or(0.0) + distance);
    }
    cumulative
}

fn polyline_length_m(coordinates: &[[f64; 2]]) -> f64 {
    cumulative_polyline_m(coordinates)
        .last()
        .copied()
        .unwrap_or(0.0)
}

fn validate_routing_settings(settings: &RoutingSettings) -> Result<()> {
    if settings.sidecar.trim().is_empty() || settings.slug.trim().is_empty() {
        bail!("routing sidecar and slug must not be empty");
    }
    if settings.source_ids.is_empty() {
        bail!("routing bundle must identify its locked sources");
    }
    if !settings.demand_weight.is_finite() || !(0.0..=100.0).contains(&settings.demand_weight) {
        bail!("routing demand weight must be finite and between 0 and 100");
    }
    if !settings.search_margin_m.is_finite()
        || !(100.0..=50_000.0).contains(&settings.search_margin_m)
    {
        bail!("routing search margin must be between 100 m and 50 km");
    }
    if !settings.endpoint_snap_m.is_finite() || !(0.0..=5_000.0).contains(&settings.endpoint_snap_m)
    {
        bail!("routing endpoint snap must be between 0 and 5 km");
    }
    Ok(())
}

fn latlon_to_cell(reference: &GridRef, lat: f64, lon: f64) -> Result<(usize, usize)> {
    if lat < reference.bbox_south
        || lat > reference.bbox_north
        || lon < reference.bbox_west
        || lon > reference.bbox_east
    {
        bail!("line endpoint lies outside the source-locked routing grid");
    }
    let row = (((reference.bbox_north - lat) * reference.m_per_deg_lat) / reference.cell_m)
        .floor()
        .max(0.0) as usize;
    let col = (((lon - reference.bbox_west) * reference.m_per_deg_lon) / reference.cell_m)
        .floor()
        .max(0.0) as usize;
    Ok((
        row.min(reference.height.saturating_sub(1)),
        col.min(reference.width.saturating_sub(1)),
    ))
}

fn snapped_route_cell(grid: &Grid, lat: f64, lon: f64, max_snap_m: f64) -> Result<(usize, usize)> {
    let origin = latlon_to_cell(&grid.reference, lat, lon)?;
    let radius = (max_snap_m / grid.reference.cell_m).ceil() as isize;
    let mut candidates = Vec::new();
    for dr in -radius..=radius {
        for dc in -radius..=radius {
            let row = origin.0 as isize + dr;
            let col = origin.1 as isize + dc;
            if !grid.in_bounds(row, col) {
                continue;
            }
            let row = row as usize;
            let col = col as usize;
            if !grid.is_buildable(row, col) || !grid.cost_at(row, col).is_finite() {
                continue;
            }
            let (candidate_lat, candidate_lon) = grid.reference.rc_to_latlon(row, col);
            let distance_m = haversine_m(lat, lon, candidate_lat, candidate_lon);
            if distance_m <= max_snap_m + 0.001 {
                candidates.push((distance_m, row, col));
            }
        }
    }
    candidates.sort_by(|left, right| {
        left.0
            .total_cmp(&right.0)
            .then_with(|| left.1.cmp(&right.1))
            .then_with(|| left.2.cmp(&right.2))
    });
    candidates
        .first()
        .map(|(_, row, col)| (*row, *col))
        .ok_or_else(|| {
            anyhow!("no buildable routing cell lies within {max_snap_m:.0} m of endpoint")
        })
}

fn route_bbox(
    grid: &Grid,
    start: (usize, usize),
    goal: (usize, usize),
    margin: usize,
) -> ((usize, usize), (usize, usize)) {
    let row_min = start.0.min(goal.0).saturating_sub(margin);
    let col_min = start.1.min(goal.1).saturating_sub(margin);
    let row_max = start
        .0
        .max(goal.0)
        .saturating_add(margin)
        .min(grid.reference.height.saturating_sub(1));
    let col_max = start
        .1
        .max(goal.1)
        .saturating_add(margin)
        .min(grid.reference.width.saturating_sub(1));
    ((row_min, col_min), (row_max, col_max))
}

fn interpolate_line_points(
    start_lat: f64,
    start_lon: f64,
    end_lat: f64,
    end_lon: f64,
    spacing_m: f64,
) -> Vec<GeoPoint> {
    let length_m = haversine_m(start_lat, start_lon, end_lat, end_lon);
    let segments = (length_m / spacing_m).ceil().clamp(1.0, 5_000.0) as usize;
    (0..=segments)
        .map(|index| {
            let fraction = index as f64 / segments as f64;
            GeoPoint {
                lat: start_lat + (end_lat - start_lat) * fraction,
                lon: start_lon + (end_lon - start_lon) * fraction,
            }
        })
        .collect()
}

fn nearest_coordinate_index(coordinates: &[[f64; 2]], lon: f64, lat: f64) -> usize {
    coordinates
        .iter()
        .enumerate()
        .min_by(|(_, left), (_, right)| {
            haversine_m(lat, lon, left[1], left[0])
                .total_cmp(&haversine_m(lat, lon, right[1], right[0]))
        })
        .map(|(index, _)| index)
        .unwrap_or(0)
}

fn read_toml<T: serde::de::DeserializeOwned>(path: &Path) -> Result<T> {
    let text = fs::read_to_string(path).with_context(|| format!("reading {}", path.display()))?;
    toml::from_str(&text).with_context(|| format!("parsing TOML {}", path.display()))
}

fn read_json<T: serde::de::DeserializeOwned>(path: &Path) -> Result<T> {
    let bytes = fs::read(path).with_context(|| format!("reading {}", path.display()))?;
    serde_json::from_slice(&bytes).with_context(|| format!("parsing JSON {}", path.display()))
}

fn write_toml_atomic<T: Serialize>(path: &Path, value: &T) -> Result<()> {
    let mut body = toml::to_string_pretty(value).context("serializing canonical TOML")?;
    body.push('\n');
    write_atomic(path, body.as_bytes())
}

fn write_json_atomic<T: Serialize>(path: &Path, value: &T) -> Result<()> {
    let mut body = serde_json::to_vec_pretty(value).context("serializing canonical JSON")?;
    body.push(b'\n');
    write_atomic(path, &body)
}

fn write_atomic(path: &Path, body: &[u8]) -> Result<()> {
    let parent = path
        .parent()
        .ok_or_else(|| anyhow!("{} has no parent directory", path.display()))?;
    fs::create_dir_all(parent).with_context(|| format!("creating {}", parent.display()))?;
    let temporary = path.with_extension("osr-studio-tmp");
    fs::write(&temporary, body)
        .with_context(|| format!("writing temporary file {}", temporary.display()))?;
    fs::rename(&temporary, path).with_context(|| format!("publishing {}", path.display()))?;
    Ok(())
}

fn sha256_file(path: &Path) -> Result<String> {
    let bytes = fs::read(path).with_context(|| format!("hashing {}", path.display()))?;
    Ok(sha256_bytes(&bytes))
}

fn compiler_source_hash() -> String {
    const SOURCES: &[(&str, &[u8])] = &[
        ("Cargo.toml", include_bytes!("../Cargo.toml")),
        ("src/lib.rs", include_bytes!("lib.rs")),
        ("src/jobs.rs", include_bytes!("jobs.rs")),
        ("src/main.rs", include_bytes!("main.rs")),
        ("src/model.rs", include_bytes!("model.rs")),
        ("src/project.rs", include_bytes!("project.rs")),
        ("src/server.rs", include_bytes!("server.rs")),
        ("web/app.css", include_bytes!("../web/app.css")),
        ("web/app.js", include_bytes!("../web/app.js")),
        ("web/index.html", include_bytes!("../web/index.html")),
    ];
    let mut hasher = Sha256::new();
    for (path, bytes) in SOURCES {
        hasher.update(path.as_bytes());
        hasher.update([0]);
        hasher.update(bytes);
        hasher.update([0]);
    }
    hex::encode(hasher.finalize())
}

fn sha256_bytes(bytes: &[u8]) -> String {
    let mut hasher = Sha256::new();
    hasher.update(bytes);
    hex::encode(hasher.finalize())
}

fn validate_coordinates(lat: Option<f64>, lon: Option<f64>) -> Result<()> {
    match (lat, lon) {
        (None, None) => Ok(()),
        (Some(latitude), Some(longitude))
            if (-90.0..=90.0).contains(&latitude) && (-180.0..=180.0).contains(&longitude) =>
        {
            Ok(())
        }
        (Some(_), Some(_)) => bail!("latitude or longitude is outside its valid range"),
        _ => bail!("latitude and longitude must be provided together"),
    }
}

fn validate_station_name(name: &str) -> Result<()> {
    let trimmed = name.trim();
    if trimmed.is_empty() {
        bail!("station name must not be empty");
    }
    if trimmed.chars().count() > 120 {
        bail!("station name must not exceed 120 characters");
    }
    Ok(())
}

fn validate_manual_archetype(archetype: &str) -> Result<()> {
    if !matches!(archetype, "standard" | "major" | "halt" | "terminal") {
        bail!("manual station archetype must be standard, major, halt, or terminal");
    }
    Ok(())
}

fn validate_line_plan(plan: &LineServicePlan) -> Result<()> {
    if plan.windows.is_empty() {
        bail!("service plan has no windows");
    }
    let service_start = parse_minutes(&plan.service_start)?;
    let (_, service_end) =
        normalized_interval(&plan.service_start, &plan.service_end, service_start)?;
    let mut expected = service_start;
    for window in &plan.windows {
        if !(1..=120).contains(&window.headway_min) {
            bail!("headway must be between 1 and 120 minutes");
        }
        let (from, to) = normalized_interval(&window.from, &window.to, service_start)?;
        if from != expected {
            bail!(
                "service windows are not contiguous at {} (expected minute {}, found {})",
                window.from,
                expected,
                from
            );
        }
        if to <= from {
            bail!("service window {}..{} is empty", window.from, window.to);
        }
        expected = to;
    }
    if expected != service_end {
        bail!("last service window ends at minute {expected}, but service ends at {service_end}");
    }
    Ok(())
}

fn parse_minutes(value: &str) -> Result<u32> {
    let (hours, minutes) = value
        .split_once(':')
        .ok_or_else(|| anyhow!("time {value:?} must use HH:MM"))?;
    let hours: u32 = hours
        .parse()
        .with_context(|| format!("invalid hour in {value:?}"))?;
    let minutes: u32 = minutes
        .parse()
        .with_context(|| format!("invalid minute in {value:?}"))?;
    if hours > 24 || minutes > 59 || (hours == 24 && minutes != 0) {
        bail!("time {value:?} is outside 00:00..24:00");
    }
    Ok(hours * 60 + minutes)
}

fn normalized_interval(from: &str, to: &str, service_start: u32) -> Result<(u32, u32)> {
    let mut from_min = parse_minutes(from)?;
    let mut to_min = parse_minutes(to)?;
    if from_min < service_start {
        from_min += 24 * 60;
    }
    if to_min <= from_min {
        to_min += 24 * 60;
    }
    Ok((from_min, to_min))
}

fn service_finding(
    severity: FindingSeverity,
    code: &str,
    message: &str,
    plan: &LineServicePlan,
) -> ValidationFinding {
    ValidationFinding {
        severity,
        code: code.to_string(),
        message: message.to_string(),
        object_id: Some(format!("{}:{}", plan.line, plan.day_type)),
    }
}

fn calendar_days(plan: &ServicePlan) -> [(&'static str, &str); 7] {
    [
        ("monday", &plan.calendar.monday),
        ("tuesday", &plan.calendar.tuesday),
        ("wednesday", &plan.calendar.wednesday),
        ("thursday", &plan.calendar.thursday),
        ("friday", &plan.calendar.friday),
        ("saturday", &plan.calendar.saturday),
        ("sunday", &plan.calendar.sunday),
    ]
}

fn haversine_m(lat_a: f64, lon_a: f64, lat_b: f64, lon_b: f64) -> f64 {
    let earth_radius_m = 6_371_000.0;
    let lat_a = lat_a.to_radians();
    let lat_b = lat_b.to_radians();
    let delta_lat = lat_b - lat_a;
    let delta_lon = (lon_b - lon_a).to_radians();
    let half = (delta_lat / 2.0).sin().powi(2)
        + lat_a.cos() * lat_b.cos() * (delta_lon / 2.0).sin().powi(2);
    2.0 * earth_radius_m * half.sqrt().asin()
}

fn git_output(cwd: &Path, args: &[&str]) -> Option<String> {
    let output = Command::new("git")
        .args(args)
        .current_dir(cwd)
        .output()
        .ok()?;
    if !output.status.success() {
        return None;
    }
    Some(String::from_utf8_lossy(&output.stdout).trim().to_string())
}

#[cfg(test)]
mod tests {
    use std::path::Path;

    use super::{
        haversine_m, is_custom_coordination_id, normalized_interval, parse_minutes,
        validate_coordination_decision, validate_custom_coordination_issue, validate_line_plan,
        CityProject,
    };
    use crate::model::{
        CoordinationStatus, IntentState, LineControlPoint, LineCreate, LineRoutingPreference,
        LineServicePlan, ManualStation, ServiceWindow, StationCreate, StationOverride,
    };

    #[test]
    fn parses_end_of_day() {
        assert_eq!(parse_minutes("24:00").unwrap(), 1_440);
        assert!(parse_minutes("24:01").is_err());
    }

    #[test]
    fn coordination_closure_requires_resolution_and_reviewer() {
        assert!(validate_coordination_decision(CoordinationStatus::Open, "", "").is_ok());
        assert!(validate_coordination_decision(
            CoordinationStatus::Resolved,
            "Engineer-released package accepted",
            "Civil authority",
        )
        .is_ok());
        assert!(
            validate_coordination_decision(CoordinationStatus::Closed, "too short", "").is_err()
        );
    }

    #[test]
    fn custom_coordination_topics_require_deterministic_ids_and_assets() {
        assert!(is_custom_coordination_id("custom-0123456789abcdef"));
        assert!(!is_custom_coordination_id("custom-not-a-hash"));
        assert!(validate_custom_coordination_issue(
            "Confirm rail fastening interface",
            "Confirm this interface against the released supplier assembly.",
            &["OSR-DT-416916837E".to_string()],
        )
        .is_ok());
        assert!(validate_custom_coordination_issue(
            "Bad",
            "Too short",
            &["not-an-asset".to_string()],
        )
        .is_err());
    }

    #[test]
    fn normalizes_overnight_interval() {
        assert_eq!(
            normalized_interval("23:30", "02:00", 330).unwrap(),
            (1_410, 1_560)
        );
    }

    #[test]
    fn rejects_schedule_gaps() {
        let plan = LineServicePlan {
            line: "line-1".to_string(),
            day_type: "weekday".to_string(),
            service_start: "06:00".to_string(),
            service_end: "10:00".to_string(),
            windows: vec![
                ServiceWindow {
                    from: "06:00".to_string(),
                    to: "07:00".to_string(),
                    headway_min: 10,
                },
                ServiceWindow {
                    from: "08:00".to_string(),
                    to: "10:00".to_string(),
                    headway_min: 10,
                },
            ],
        };
        assert!(validate_line_plan(&plan).is_err());
    }

    #[test]
    fn station_move_regenerates_its_line_and_day_scenario() {
        let root = Path::new(env!("CARGO_MANIFEST_DIR")).join("../../projects/samawah");
        let mut project = CityProject::load(root).expect("load Samawah project");
        let station_id = "line-1-0581-0418-s012247";
        let source = project
            .base
            .stations
            .iter()
            .find(|station| station.id == station_id)
            .expect("source station")
            .clone();
        let baseline_snapshot = project.compile().expect("compile baseline");
        let baseline_scenario = project
            .scenario_for_day_type("weekday", &baseline_snapshot)
            .expect("baseline weekday scenario");
        let baseline_parsed: toml::Value =
            toml::from_str(&baseline_scenario).expect("parse baseline scenario");
        let baseline_distance = baseline_parsed["lines"]
            .as_array()
            .expect("baseline lines")
            .iter()
            .find(|line| line["id"].as_str() == Some("line-1"))
            .expect("baseline line 1")["stations"]
            .as_array()
            .expect("baseline station refs")[5]["distance_from_prev_m"]
            .as_integer()
            .expect("baseline distance");
        project.overrides.stations.push(StationOverride {
            id: station_id.to_string(),
            state: IntentState::Preferred,
            lat: Some(source.lat + 0.002),
            lon: Some(source.lon + 0.001),
            reason: "test movement".to_string(),
        });
        let snapshot = project.compile().expect("compile moved station");
        assert_eq!(snapshot.changes.len(), 1);
        assert_ne!(snapshot.summary.route_km, 50.4235);

        let network = project
            .candidate_network_geojson(&snapshot)
            .expect("candidate network");
        let effective_station = network["features"]
            .as_array()
            .expect("features")
            .iter()
            .find(|feature| feature["properties"]["id"] == station_id)
            .expect("effective station feature");
        assert_eq!(
            effective_station["geometry"]["coordinates"][1],
            source.lat + 0.002
        );

        let scenario = project
            .scenario_for_day_type("weekday", &snapshot)
            .expect("weekday scenario");
        let parsed: toml::Value = toml::from_str(&scenario).expect("parse scenario");
        let line_one = parsed["lines"]
            .as_array()
            .expect("lines")
            .iter()
            .find(|line| line["id"].as_str() == Some("line-1"))
            .expect("line 1");
        let distances = line_one["stations"]
            .as_array()
            .expect("station refs")
            .iter()
            .map(|station| station["distance_from_prev_m"].as_integer().unwrap())
            .collect::<Vec<_>>();
        assert_ne!(distances[5], baseline_distance);
    }

    #[test]
    fn alignment_control_point_regenerates_line_geometry() {
        let root = Path::new(env!("CARGO_MANIFEST_DIR")).join("../../projects/samawah");
        let mut project = CityProject::load(root).expect("load Samawah project");
        project
            .overrides
            .line_control_points
            .push(LineControlPoint {
                id: "cp-test".to_string(),
                line: "line-2".to_string(),
                state: IntentState::Preferred,
                source_lat: 31.327923550372528,
                source_lon: 45.26779468621901,
                lat: 31.32992355037253,
                lon: 45.26879468621901,
                influence_m: 1_500.0,
                reason: "test line edit".to_string(),
            });
        let snapshot = project.compile().expect("compile line edit");
        assert_eq!(snapshot.summary.edited_line_count, 1);
        assert_eq!(snapshot.line_control_points.len(), 1);
        assert!(snapshot.line_control_points[0].distance_m > 200.0);
        let network = project
            .candidate_network_geojson(&snapshot)
            .expect("candidate network");
        let control = network["features"]
            .as_array()
            .expect("features")
            .iter()
            .find(|feature| feature["properties"]["id"] == "cp-test")
            .expect("control feature");
        assert_eq!(control["geometry"]["coordinates"][1], 31.32992355037253);
    }

    #[test]
    fn manual_station_updates_snapshot_and_simulator_topology() {
        let root = Path::new(env!("CARGO_MANIFEST_DIR")).join("../../projects/samawah");
        let mut project = CityProject::load(root).expect("load Samawah project");
        let line = project
            .corridor
            .get("features")
            .and_then(serde_json::Value::as_array)
            .expect("corridor features")
            .iter()
            .find(|feature| feature["properties"]["name"] == "line-2")
            .expect("line 2 geometry");
        let source = super::geojson_coordinates(line).expect("line coordinates");
        let coordinate = source[source.len() / 2];
        let chainage = super::cumulative_polyline_m(&source)[source.len() / 2];
        let id = "manual-line-2-test";
        project.overrides.manual_stations.push(ManualStation {
            id: id.to_string(),
            name: "Test infill".to_string(),
            line: "line-2".to_string(),
            state: IntentState::Manual,
            source_lat: coordinate[1],
            source_lon: coordinate[0],
            source_s_m: chainage,
            lat: coordinate[1],
            lon: coordinate[0],
            archetype: "standard".to_string(),
            reason: "topology test".to_string(),
        });

        let snapshot = project.compile().expect("compile manual station");
        assert_eq!(snapshot.summary.station_count, 22);
        assert_eq!(snapshot.summary.manual_station_count, 1);
        assert_eq!(snapshot.summary.edited_line_count, 1);
        assert_eq!(
            snapshot
                .lines
                .iter()
                .find(|line| line.id == "line-2")
                .expect("compiled line 2")
                .station_count,
            7
        );

        let scenario = project
            .scenario_for_day_type("weekday", &snapshot)
            .expect("manual-station scenario");
        let parsed: toml::Value = toml::from_str(&scenario).expect("parse scenario");
        assert!(parsed["stations"]
            .as_array()
            .expect("station definitions")
            .iter()
            .any(|station| station["id"].as_str() == Some(id)));
        let line_two = parsed["lines"]
            .as_array()
            .expect("scenario lines")
            .iter()
            .find(|line| line["id"].as_str() == Some("line-2"))
            .expect("scenario line 2");
        assert!(line_two["stations"]
            .as_array()
            .expect("line station refs")
            .iter()
            .any(|station| station["id"].as_str() == Some(id)));
    }

    #[test]
    fn retiring_generated_station_rebuilds_simulator_topology() {
        let root = Path::new(env!("CARGO_MANIFEST_DIR")).join("../../projects/samawah");
        let mut project = CityProject::load(root).expect("load Samawah project");
        let id = "line-2-0400-0417-s008456";
        project.overrides.stations.push(StationOverride {
            id: id.to_string(),
            state: IntentState::Retired,
            lat: None,
            lon: None,
            reason: "retirement test".to_string(),
        });
        let snapshot = project.compile().expect("compile retired station");
        assert_eq!(snapshot.summary.station_count, 20);
        assert_eq!(snapshot.summary.edited_line_count, 1);
        let scenario = project
            .scenario_for_day_type("weekday", &snapshot)
            .expect("retired-station scenario");
        let parsed: toml::Value = toml::from_str(&scenario).expect("parse scenario");
        assert!(!parsed["stations"]
            .as_array()
            .expect("station definitions")
            .iter()
            .any(|station| station["id"].as_str() == Some(id)));
        assert!(!parsed["lines"]
            .as_array()
            .expect("scenario lines")
            .iter()
            .find(|line| line["id"].as_str() == Some("line-2"))
            .expect("scenario line 2")["stations"]
            .as_array()
            .expect("line station refs")
            .iter()
            .any(|station| station["id"].as_str() == Some(id)));
    }

    #[test]
    fn station_creation_persists_deterministic_manual_intent() {
        let root = Path::new(env!("CARGO_MANIFEST_DIR")).join("../../projects/samawah");
        let mut project = CityProject::load(&root).expect("load Samawah project");
        let temporary = tempfile::tempdir().expect("temporary project root");
        std::fs::copy(
            root.join("network/overrides.toml"),
            temporary.path().join("overrides.toml"),
        )
        .expect("copy overrides");
        project.root = temporary.path().to_path_buf();
        project.config.inputs.network_overrides = "overrides.toml".to_string();
        let coordinate = project.corridor["features"]
            .as_array()
            .expect("features")
            .iter()
            .find(|feature| feature["properties"]["name"] == "line-3")
            .expect("line 3")["geometry"]["coordinates"]
            .as_array()
            .expect("coordinates")[250]
            .as_array()
            .expect("coordinate");
        let lon = coordinate[0].as_f64().expect("longitude");
        let lat = coordinate[1].as_f64().expect("latitude");
        let id = project
            .create_station(
                "line-3",
                StationCreate {
                    name: "Deterministic infill".to_string(),
                    lat,
                    lon,
                    archetype: "major".to_string(),
                    reason: "authoring test".to_string(),
                },
            )
            .expect("create manual station");
        assert!(id.starts_with("manual-line-3-"));
        let saved: crate::model::OverrideFile =
            super::read_toml(&temporary.path().join("overrides.toml"))
                .expect("read saved overrides");
        assert_eq!(saved.manual_stations.len(), 1);
        assert_eq!(saved.manual_stations[0].id, id);
        assert_eq!(saved.manual_stations[0].state, IntentState::Manual);
    }

    #[test]
    fn revision_comparison_includes_service_windows_and_alignment_controls() {
        let root = Path::new(env!("CARGO_MANIFEST_DIR")).join("../../projects/samawah");
        let project = CityProject::load(root).expect("load Samawah project");
        let base = project.compile().expect("compile base");
        let mut candidate = base.clone();
        candidate.revision_id = "osr-aaaaaaaaaaaaaaaa".to_string();
        let service_plan = candidate
            .service_plan
            .as_mut()
            .expect("embedded service plan");
        let service_key = (
            service_plan.line_plans[0].line.clone(),
            service_plan.line_plans[0].day_type.clone(),
        );
        service_plan.line_plans[0].windows[0].headway_min += 1;
        candidate
            .service_metrics
            .iter_mut()
            .find(|metric| metric.line == service_key.0 && metric.day_type == service_key.1)
            .expect("matching service metric")
            .peak_fleet += 1;
        candidate
            .line_control_points
            .push(crate::model::CompiledControlPoint {
                id: "cp-review".to_string(),
                line: "line-1".to_string(),
                state: IntentState::Preferred,
                source_lat: 31.3,
                source_lon: 45.2,
                lat: 31.301,
                lon: 45.201,
                influence_m: 2_000.0,
                distance_m: 146.0,
                reason: "review test".to_string(),
            });

        let comparison = super::compare_snapshots(&base, &candidate);
        assert_eq!(comparison.services.len(), 1);
        assert_eq!(comparison.services[0].kind, "modified");
        assert!(comparison.services[0].before.is_some());
        assert!(comparison.services[0].after.is_some());
        assert_eq!(comparison.controls.len(), 1);
        assert_eq!(comparison.controls[0].kind, "added");
    }

    #[test]
    fn manual_line_creation_populates_network_services_and_simulator() {
        let root = Path::new(env!("CARGO_MANIFEST_DIR")).join("../../projects/samawah");
        let mut project = CityProject::load(&root).expect("load Samawah project");
        let base = project.compile().expect("compile baseline");
        let temporary = tempfile::tempdir().expect("temporary project root");
        std::fs::copy(
            root.join("network/overrides.toml"),
            temporary.path().join("overrides.toml"),
        )
        .expect("copy overrides");
        std::fs::copy(
            root.join("services/service-plan.toml"),
            temporary.path().join("service-plan.toml"),
        )
        .expect("copy service plan");
        project.root = temporary.path().to_path_buf();
        project.config.inputs.network_overrides = "overrides.toml".to_string();
        project.config.inputs.service_plan = "service-plan.toml".to_string();
        let id = project
            .create_line(LineCreate {
                name: "Test orbital connector".to_string(),
                start_lat: 31.275,
                start_lon: 45.225,
                end_lat: 31.345,
                end_lon: 45.325,
                routing: LineRoutingPreference::Direct,
                reason: "manual line acceptance".to_string(),
            })
            .expect("create line");
        assert!(id.starts_with("manual-line-"));
        let saved_overrides: crate::model::OverrideFile =
            super::read_toml(&temporary.path().join("overrides.toml")).expect("saved overrides");
        let saved_services: crate::model::ServicePlan =
            super::read_toml(&temporary.path().join("service-plan.toml")).expect("saved services");
        assert_eq!(saved_overrides.manual_lines.len(), 1);
        assert_eq!(
            saved_overrides
                .manual_stations
                .iter()
                .filter(|station| station.line == id)
                .count(),
            2
        );
        assert_eq!(
            saved_services
                .line_plans
                .iter()
                .filter(|plan| plan.line == id)
                .count(),
            3
        );

        project.root = root;
        project.config.inputs.network_overrides = "network/overrides.toml".to_string();
        project.config.inputs.service_plan = "services/service-plan.toml".to_string();
        let snapshot = project.compile().expect("compile manual line");
        assert_eq!(snapshot.lines.len(), 4);
        assert_eq!(snapshot.summary.manual_line_count, 1);
        assert_eq!(snapshot.summary.station_count, 23);
        assert_eq!(snapshot.summary.manual_station_count, 2);
        assert_eq!(snapshot.service_metrics.len(), 12);
        assert_eq!(snapshot.summary.validation_errors, 0);
        let candidate_line = snapshot
            .lines
            .iter()
            .find(|line| line.id == id)
            .expect("compiled manual line");
        assert_eq!(candidate_line.state, IntentState::Manual);
        assert_eq!(candidate_line.station_count, 2);

        let scenario = project
            .scenario_for_day_type("weekday", &snapshot)
            .expect("manual-line scenario");
        let parsed: toml::Value = toml::from_str(&scenario).expect("parse scenario");
        assert!(parsed["lines"]
            .as_array()
            .expect("scenario lines")
            .iter()
            .any(|line| line["id"].as_str() == Some(id.as_str())));
        assert!(parsed["fleets"]
            .as_array()
            .expect("scenario fleets")
            .iter()
            .any(|fleet| fleet["line"].as_str() == Some(id.as_str())));

        let comparison = super::compare_snapshots(&base, &snapshot);
        assert_eq!(comparison.lines.len(), 1);
        assert_eq!(comparison.stations.len(), 2);
        assert_eq!(comparison.services.len(), 3);
        assert_eq!(comparison.summary.manual_line_count, 1);
    }

    #[test]
    fn demand_aware_line_uses_locked_rasters_deterministically() {
        let root = Path::new(env!("CARGO_MANIFEST_DIR")).join("../../projects/samawah");
        let mut project = CityProject::load(&root).expect("load Samawah project");
        let temporary = tempfile::tempdir().expect("temporary project root");
        std::fs::copy(
            root.join("network/overrides.toml"),
            temporary.path().join("overrides.toml"),
        )
        .expect("copy overrides");
        std::fs::copy(
            root.join("services/service-plan.toml"),
            temporary.path().join("service-plan.toml"),
        )
        .expect("copy service plan");
        let routing_sidecar = root
            .join("routing/samawah.grid.json")
            .canonicalize()
            .expect("canonical routing sidecar");
        project
            .config
            .routing
            .as_mut()
            .expect("routing settings")
            .sidecar = routing_sidecar.display().to_string();
        for source in &mut project.source_lock.sources {
            source.path = root
                .join(&source.path)
                .canonicalize()
                .expect("canonical locked source")
                .display()
                .to_string();
        }
        project.root = temporary.path().to_path_buf();
        project.config.inputs.network_overrides = "overrides.toml".to_string();
        project.config.inputs.service_plan = "service-plan.toml".to_string();
        let create = LineCreate {
            name: "Demand-aware connector".to_string(),
            start_lat: 31.275,
            start_lon: 45.225,
            end_lat: 31.345,
            end_lon: 45.325,
            routing: LineRoutingPreference::DemandAware,
            reason: "routing acceptance".to_string(),
        };
        let first = project
            .route_manual_line(&create)
            .expect("first demand-aware route");
        let second = project
            .route_manual_line(&create)
            .expect("second demand-aware route");
        assert_eq!(
            serde_json::to_vec(&first.points).expect("serialize first route"),
            serde_json::to_vec(&second.points).expect("serialize second route")
        );
        assert_eq!(first.method, "demand-aware");
        assert_eq!(first.source_ids.len(), 6);
        assert_eq!(first.demand_weight, Some(5.0));
        assert!(first.points.len() > 20);

        let id = project
            .create_line(create)
            .expect("create demand-aware line");
        let line = project
            .overrides
            .manual_lines
            .iter()
            .find(|line| line.id == id)
            .expect("saved demand-aware line");
        assert_eq!(line.routing_method, "demand-aware");
        assert_eq!(line.routing_source_ids.len(), 6);
        assert_eq!(line.demand_weight, Some(5.0));
        assert!(
            haversine_m(
                line.points.first().expect("route start").lat,
                line.points.first().expect("route start").lon,
                31.275,
                45.225
            ) <= 500.0
        );
        assert!(
            haversine_m(
                line.points.last().expect("route end").lat,
                line.points.last().expect("route end").lon,
                31.345,
                45.325
            ) <= 500.0
        );
    }
}
