use std::path::{Path, PathBuf};
use std::sync::Arc;

use anyhow::{bail, Context, Result};
use axum::extract::{DefaultBodyLimit, Path as AxumPath, State};
use axum::http::StatusCode;
use axum::response::{Html, IntoResponse};
use axum::routing::{get, post, put};
use axum::{Json, Router};
use serde::Serialize;
use sha2::{Digest, Sha256};
use tokio::sync::Mutex;

use crate::jobs::JobManager;
use crate::model::{
    ApprovalCreate, CivilConstructionSettings, ControlPointCreate, ControlPointEdit,
    CoordinationCreate, CoordinationEdit, DemandFlowCreate, DemandFlowEdit, GisLayerDescriptor,
    GisManifest, JobRequest, LineCreate, LineEdit, LineServicePlan, ProjectView,
    ServiceHeadwayBulkEdit, StationCreate, StationEdit,
};
use crate::CityProject;

#[derive(Clone, Debug)]
struct AppState {
    project_root: PathBuf,
    repository_root: PathBuf,
    write_lock: Arc<Mutex<()>>,
    jobs: JobManager,
}

#[derive(Debug)]
struct ApiError(anyhow::Error);

#[derive(Debug, Serialize)]
struct ApiErrorBody {
    error: String,
}

impl<E> From<E> for ApiError
where
    E: Into<anyhow::Error>,
{
    fn from(error: E) -> Self {
        Self(error.into())
    }
}

impl IntoResponse for ApiError {
    fn into_response(self) -> axum::response::Response {
        (
            StatusCode::BAD_REQUEST,
            Json(ApiErrorBody {
                error: format!("{:#}", self.0),
            }),
        )
            .into_response()
    }
}

pub async fn serve(project_root: impl AsRef<Path>, host: &str, port: u16) -> Result<()> {
    let project_root = project_root.as_ref().to_path_buf();
    let project = CityProject::load(&project_root)?;
    let repository_root = project
        .git_state()
        .repository_root
        .map(PathBuf::from)
        .unwrap_or_else(|| project_root.clone());
    let write_lock = Arc::new(Mutex::new(()));
    let jobs = JobManager::new(
        project_root.clone(),
        repository_root.clone(),
        project.config().project.slug.clone(),
        write_lock.clone(),
    )?;
    let state = AppState {
        project_root,
        repository_root,
        write_lock,
        jobs,
    };
    let app = Router::new()
        .route("/", get(index))
        .route("/app.js", get(javascript))
        .route("/app.css", get(stylesheet))
        .route("/api/project", get(get_project))
        .route("/api/gis/manifest", get(get_gis_manifest))
        .route("/api/gis/layers/:id", get(get_gis_layer))
        .route("/api/civil", put(put_civil))
        .route("/api/stations/:id", put(put_station).delete(delete_station))
        .route("/api/lines", post(post_line))
        .route("/api/lines/:id", put(put_line).delete(delete_line))
        .route("/api/lines/:line/stations", post(post_station))
        .route("/api/lines/:line/control-points", post(post_control_point))
        .route("/api/control-points/:id", put(put_control_point))
        .route("/api/services/bulk", put(put_bulk_service))
        .route("/api/services/:line/:day_type", put(put_service))
        .route("/api/coordination", post(post_coordination_issue))
        .route("/api/coordination/:id", put(put_coordination_issue))
        .route("/api/approvals", post(post_approval))
        .route("/api/demand/flows", post(post_demand_flow))
        .route(
            "/api/demand/flows/:id",
            put(put_demand_flow).delete(delete_demand_flow),
        )
        .route("/api/compile", post(compile_project))
        .route("/api/jobs", get(get_jobs))
        .route("/api/jobs/:id", get(get_job).post(start_job))
        .route("/api/jobs/:id/artifacts/:index", get(get_job_artifact))
        .route(
            "/api/revisions",
            get(get_revisions).post(materialize_revision),
        )
        .route("/api/revisions/:id/compare", get(compare_revision))
        .route("/api/git", get(get_git))
        .layer(DefaultBodyLimit::max(1_000_000))
        .with_state(state);
    let address = format!("{host}:{port}");
    let listener = tokio::net::TcpListener::bind(&address)
        .await
        .with_context(|| format!("binding City Studio to {address}"))?;
    eprintln!("OSR City Studio: http://{address}/");
    eprintln!("project: {}", project.root().display());
    eprintln!("working changes remain uncommitted until materialized and reviewed");
    axum::serve(listener, app)
        .with_graceful_shutdown(shutdown_signal())
        .await
        .context("serving City Studio")?;
    Ok(())
}

async fn get_gis_manifest(State(state): State<AppState>) -> Result<Json<GisManifest>, ApiError> {
    let project = CityProject::load(&state.project_root)?;
    Ok(Json(gis_manifest(&project)?))
}

async fn get_gis_layer(
    State(state): State<AppState>,
    AxumPath(id): AxumPath<String>,
) -> Result<Json<serde_json::Value>, ApiError> {
    let project = CityProject::load(&state.project_root)?;
    Ok(Json(gis_layer(&project, &id)?))
}

async fn index() -> Html<&'static str> {
    Html(include_str!("../web/index.html"))
}

async fn javascript() -> ([(&'static str, &'static str); 1], &'static str) {
    (
        [("content-type", "text/javascript; charset=utf-8")],
        include_str!("../web/app.js"),
    )
}

async fn stylesheet() -> ([(&'static str, &'static str); 1], &'static str) {
    (
        [("content-type", "text/css; charset=utf-8")],
        include_str!("../web/app.css"),
    )
}

const GIS_LAYER_IDS: [&str; 16] = [
    "routing-demand",
    "routing-cost",
    "routing-buildability",
    "context-buildings",
    "context-water",
    "context-protected",
    "context-roads",
    "context-existing-rail",
    "context-anchors",
    "engineering-civil",
    "engineering-energy",
    "engineering-depots",
    "engineering-interchanges",
    "engineering-issues",
    "published-network",
    "candidate-network",
];

fn gis_manifest(project: &CityProject) -> Result<GisManifest> {
    let mut layers = Vec::with_capacity(GIS_LAYER_IDS.len());
    for id in GIS_LAYER_IDS {
        let data = gis_layer(project, id)?;
        let features = data
            .get("features")
            .and_then(serde_json::Value::as_array)
            .map_or(0, Vec::len);
        let (label, category, geometry, source_kind, visible, opacity) = match id {
            "routing-demand" => (
                "Demand intensity",
                "Planning surfaces",
                "Polygon",
                "source-locked-raster",
                true,
                0.30,
            ),
            "routing-cost" => (
                "Construction cost",
                "Planning surfaces",
                "Polygon",
                "source-locked-raster",
                false,
                0.32,
            ),
            "routing-buildability" => (
                "Buildability constraints",
                "Planning surfaces",
                "Polygon",
                "source-locked-raster",
                true,
                0.42,
            ),
            "context-buildings" => (
                "Buildings",
                "Local context",
                "Polygon",
                "source-locked-osm",
                true,
                0.18,
            ),
            "context-water" => (
                "Water",
                "Local context",
                "Mixed",
                "source-locked-osm",
                true,
                0.55,
            ),
            "context-protected" => (
                "Protected land",
                "Local context",
                "Polygon",
                "source-locked-osm",
                true,
                0.35,
            ),
            "context-roads" => (
                "Roads",
                "Local context",
                "LineString",
                "source-locked-osm",
                true,
                0.32,
            ),
            "context-existing-rail" => (
                "Existing rail",
                "Local context",
                "LineString",
                "source-locked-osm",
                true,
                0.58,
            ),
            "context-anchors" => (
                "Places and destinations",
                "Local context",
                "Point",
                "source-locked-index",
                true,
                0.90,
            ),
            "engineering-civil" => (
                "Civil classifications",
                "Engineering",
                "LineString",
                "generated-gis",
                false,
                0.78,
            ),
            "engineering-energy" => (
                "Energy sites",
                "Engineering",
                "Point",
                "generated-gis",
                false,
                0.90,
            ),
            "engineering-depots" => (
                "Depots",
                "Engineering",
                "Point",
                "generated-gis",
                true,
                0.95,
            ),
            "engineering-interchanges" => (
                "Interchanges",
                "Engineering",
                "Point",
                "generated-gis",
                true,
                0.95,
            ),
            "engineering-issues" => (
                "GIS input issues",
                "Assurance",
                "Point",
                "generated-gis",
                true,
                1.0,
            ),
            "published-network" => (
                "Published GIS network",
                "Reference",
                "Mixed",
                "generated-gis",
                false,
                0.45,
            ),
            "candidate-network" => (
                "Working candidate",
                "Design intent",
                "Mixed",
                "live-project",
                true,
                1.0,
            ),
            _ => unreachable!(),
        };
        let encoded = serde_json::to_vec(&data)?;
        layers.push(GisLayerDescriptor {
            id: id.to_string(),
            label: label.to_string(),
            category: category.to_string(),
            geometry: geometry.to_string(),
            feature_count: features,
            sha256: hex::encode(Sha256::digest(&encoded)),
            source_kind: source_kind.to_string(),
            default_visible: visible,
            default_opacity: opacity,
        });
    }
    let bounds = project
        .config()
        .routing
        .as_ref()
        .and_then(|settings| {
            osr_routing::raster::load_bundle(project.root().join(&settings.sidecar), &settings.slug)
                .ok()
        })
        .map(|bundle| {
            let grid = bundle.grid.reference;
            [
                grid.bbox_west,
                grid.bbox_south,
                grid.bbox_east,
                grid.bbox_north,
            ]
        })
        .unwrap_or_else(|| geojson_bounds(&project.candidate_network().unwrap_or_default()));
    Ok(GisManifest {
        schema_version: 1,
        coordinate_reference_system: "EPSG:4326".to_string(),
        bounds,
        deterministic: true,
        attribution: vec![
            "OpenSourceRail source-locked project inputs".to_string(),
            "© OpenStreetMap contributors · ODbL 1.0".to_string(),
            "Context anchors derived from the locked routing bundle; verify survey data before engineering release".to_string(),
        ],
        layers,
    })
}

fn gis_layer(project: &CityProject, id: &str) -> Result<serde_json::Value> {
    match id {
        "candidate-network" => project.candidate_network(),
        "published-network" => {
            let directory = engineering_gis_layers(project)?;
            merge_feature_collections(&[
                read_geojson(&directory.join("corridors.geojson"))?,
                read_geojson(&directory.join("stations.geojson"))?,
            ])
        }
        "engineering-civil" => read_engineering_layer(project, "civil_segments.geojson"),
        "engineering-energy" => read_engineering_layer(project, "energy_sites.geojson"),
        "engineering-depots" => read_engineering_layer(project, "depots.geojson"),
        "engineering-interchanges" => read_engineering_layer(project, "interchanges.geojson"),
        "engineering-issues" => read_engineering_layer(project, "input_issues.geojson"),
        "context-buildings" => read_geojson(&project.root().join("gis/context-buildings.geojson")),
        "context-water" => read_geojson(&project.root().join("gis/context-water.geojson")),
        "context-protected" => read_geojson(&project.root().join("gis/context-protected.geojson")),
        "context-roads" => read_geojson(&project.root().join("gis/context-roads.geojson")),
        "context-existing-rail" => {
            read_geojson(&project.root().join("gis/context-existing-rail.geojson"))
        }
        "context-anchors" => routing_anchors_geojson(project),
        "routing-demand" | "routing-cost" | "routing-buildability" => {
            routing_surface_geojson(project, id)
        }
        _ => bail!("unknown GIS layer {id:?}"),
    }
}

fn engineering_gis_layers(project: &CityProject) -> Result<PathBuf> {
    let base = project.root().join(&project.config().inputs.base_design);
    let city = base
        .parent()
        .context("base design input has no city directory")?;
    Ok(city.join("engineering/gis/layers"))
}

fn read_engineering_layer(project: &CityProject, file: &str) -> Result<serde_json::Value> {
    read_geojson(&engineering_gis_layers(project)?.join(file))
}

fn read_geojson(path: &Path) -> Result<serde_json::Value> {
    let bytes =
        std::fs::read(path).with_context(|| format!("reading GIS layer {}", path.display()))?;
    let value = serde_json::from_slice(&bytes)
        .with_context(|| format!("parsing GIS layer {}", path.display()))?;
    Ok(value)
}

fn merge_feature_collections(values: &[serde_json::Value]) -> Result<serde_json::Value> {
    let mut features = Vec::new();
    for value in values {
        let items = value
            .get("features")
            .and_then(serde_json::Value::as_array)
            .context("GIS layer is not a GeoJSON FeatureCollection")?;
        features.extend(items.iter().cloned());
    }
    Ok(serde_json::json!({ "type": "FeatureCollection", "features": features }))
}

fn routing_bundle(project: &CityProject) -> Result<osr_routing::RasterBundle> {
    let settings = project
        .config()
        .routing
        .as_ref()
        .context("project has no source-locked routing bundle")?;
    osr_routing::raster::load_bundle(project.root().join(&settings.sidecar), &settings.slug)
        .context("loading GIS planning surfaces")
}

fn routing_anchors_geojson(project: &CityProject) -> Result<serde_json::Value> {
    let bundle = routing_bundle(project)?;
    let features = bundle
        .anchors
        .into_iter()
        .map(|anchor| {
            serde_json::json!({
                "type": "Feature",
                "geometry": { "type": "Point", "coordinates": [anchor.lon, anchor.lat] },
                "properties": {
                    "id": anchor.id,
                    "kind": anchor.kind,
                    "name": anchor.name,
                    "weight": anchor.weight,
                }
            })
        })
        .collect::<Vec<_>>();
    Ok(serde_json::json!({ "type": "FeatureCollection", "features": features }))
}

fn routing_surface_geojson(project: &CityProject, layer: &str) -> Result<serde_json::Value> {
    let bundle = routing_bundle(project)?;
    let grid = &bundle.grid;
    let reference = &grid.reference;
    const STRIDE: usize = 5;
    let mut features = Vec::new();
    let finite_costs = grid
        .cost
        .iter()
        .copied()
        .filter(|value| value.is_finite())
        .collect::<Vec<_>>();
    let cost_min = finite_costs.iter().copied().fold(f32::INFINITY, f32::min);
    let cost_max = finite_costs
        .iter()
        .copied()
        .fold(f32::NEG_INFINITY, f32::max);
    for row in (0..reference.height).step_by(STRIDE) {
        for col in (0..reference.width).step_by(STRIDE) {
            let row_end = (row + STRIDE).min(reference.height);
            let col_end = (col + STRIDE).min(reference.width);
            let mut demand = 0.0_f32;
            let mut cost = f32::INFINITY;
            let mut buildable = 0_usize;
            let mut total = 0_usize;
            for sample_row in row..row_end {
                for sample_col in col..col_end {
                    demand = demand.max(grid.demand_at(sample_row, sample_col));
                    if grid.is_buildable(sample_row, sample_col) {
                        buildable += 1;
                        cost = cost.min(grid.cost_at(sample_row, sample_col));
                    }
                    total += 1;
                }
            }
            let value = match layer {
                "routing-demand" if demand >= 0.05 => demand.clamp(0.0, 1.0),
                "routing-cost" if cost.is_finite() => {
                    ((cost - cost_min) / (cost_max - cost_min).max(f32::EPSILON)).clamp(0.0, 1.0)
                }
                "routing-buildability" if buildable < total => {
                    1.0 - buildable as f32 / total as f32
                }
                _ => continue,
            };
            let west =
                reference.bbox_west + col as f64 * reference.cell_m / reference.m_per_deg_lon;
            let east =
                reference.bbox_west + col_end as f64 * reference.cell_m / reference.m_per_deg_lon;
            let north =
                reference.bbox_north - row as f64 * reference.cell_m / reference.m_per_deg_lat;
            let south =
                reference.bbox_north - row_end as f64 * reference.cell_m / reference.m_per_deg_lat;
            features.push(serde_json::json!({
                "type": "Feature",
                "geometry": { "type": "Polygon", "coordinates": [[
                    [west, south], [east, south], [east, north], [west, north], [west, south]
                ]] },
                "properties": { "value": (value * 10_000.0).round() / 10_000.0 }
            }));
        }
    }
    Ok(serde_json::json!({ "type": "FeatureCollection", "features": features }))
}

fn geojson_bounds(value: &serde_json::Value) -> [f64; 4] {
    fn visit(value: &serde_json::Value, bounds: &mut [f64; 4]) {
        if let Some(array) = value.as_array() {
            if array.len() >= 2 && array[0].is_number() && array[1].is_number() {
                if let (Some(lon), Some(lat)) = (array[0].as_f64(), array[1].as_f64()) {
                    bounds[0] = bounds[0].min(lon);
                    bounds[1] = bounds[1].min(lat);
                    bounds[2] = bounds[2].max(lon);
                    bounds[3] = bounds[3].max(lat);
                }
            } else {
                for item in array {
                    visit(item, bounds);
                }
            }
        } else if let Some(object) = value.as_object() {
            if let Some(coordinates) = object.get("coordinates") {
                visit(coordinates, bounds);
            }
            if let Some(features) = object.get("features") {
                visit(features, bounds);
            }
            if let Some(geometry) = object.get("geometry") {
                visit(geometry, bounds);
            }
        }
    }
    let mut bounds = [
        f64::INFINITY,
        f64::INFINITY,
        f64::NEG_INFINITY,
        f64::NEG_INFINITY,
    ];
    visit(value, &mut bounds);
    if bounds.iter().all(|number| number.is_finite()) {
        bounds
    } else {
        [-180.0, -90.0, 180.0, 90.0]
    }
}

async fn get_project(State(state): State<AppState>) -> Result<Json<ProjectView>, ApiError> {
    let project = CityProject::load(&state.project_root)?;
    let snapshot = project.compile()?;
    let corridor = project.candidate_network()?;
    Ok(Json(ProjectView {
        snapshot,
        corridor,
        service_plan: project.service_plan().clone(),
        git: project.git_state(),
        project_path: project.root().display().to_string(),
        artifacts: project.artifacts(),
        approvals: project.approvals().clone(),
    }))
}

async fn put_civil(
    State(state): State<AppState>,
    Json(settings): Json<CivilConstructionSettings>,
) -> Result<Json<ProjectView>, ApiError> {
    let _guard = state.write_lock.lock().await;
    let mut project = CityProject::load(&state.project_root)?;
    project.update_civil(settings)?;
    drop(project);
    drop(_guard);
    get_project(State(state)).await
}

async fn put_station(
    State(state): State<AppState>,
    AxumPath(id): AxumPath<String>,
    Json(edit): Json<StationEdit>,
) -> Result<Json<ProjectView>, ApiError> {
    let _guard = state.write_lock.lock().await;
    let mut project = CityProject::load(&state.project_root)?;
    project.update_station(&id, edit)?;
    drop(project);
    drop(_guard);
    get_project(State(state)).await
}

async fn post_station(
    State(state): State<AppState>,
    AxumPath(line): AxumPath<String>,
    Json(create): Json<StationCreate>,
) -> Result<Json<serde_json::Value>, ApiError> {
    let guard = state.write_lock.lock().await;
    let mut project = CityProject::load(&state.project_root)?;
    let id = project.create_station(&line, create)?;
    drop(project);
    drop(guard);
    let project = get_project(State(state)).await?.0;
    Ok(Json(serde_json::json!({ "id": id, "project": project })))
}

async fn post_line(
    State(state): State<AppState>,
    Json(create): Json<LineCreate>,
) -> Result<Json<serde_json::Value>, ApiError> {
    let guard = state.write_lock.lock().await;
    let mut project = CityProject::load(&state.project_root)?;
    let id = project.create_line(create)?;
    drop(project);
    drop(guard);
    let project = get_project(State(state)).await?.0;
    Ok(Json(serde_json::json!({ "id": id, "project": project })))
}

async fn put_line(
    State(state): State<AppState>,
    AxumPath(id): AxumPath<String>,
    Json(edit): Json<LineEdit>,
) -> Result<Json<ProjectView>, ApiError> {
    let guard = state.write_lock.lock().await;
    let mut project = CityProject::load(&state.project_root)?;
    project.update_manual_line(&id, edit)?;
    drop(project);
    drop(guard);
    get_project(State(state)).await
}

async fn delete_line(
    State(state): State<AppState>,
    AxumPath(id): AxumPath<String>,
) -> Result<Json<ProjectView>, ApiError> {
    let guard = state.write_lock.lock().await;
    let mut project = CityProject::load(&state.project_root)?;
    project.retire_manual_line(&id)?;
    drop(project);
    drop(guard);
    get_project(State(state)).await
}

async fn delete_station(
    State(state): State<AppState>,
    AxumPath(id): AxumPath<String>,
) -> Result<Json<ProjectView>, ApiError> {
    let guard = state.write_lock.lock().await;
    let mut project = CityProject::load(&state.project_root)?;
    project.retire_manual_station(&id)?;
    drop(project);
    drop(guard);
    get_project(State(state)).await
}

async fn post_control_point(
    State(state): State<AppState>,
    AxumPath(line): AxumPath<String>,
    Json(create): Json<ControlPointCreate>,
) -> Result<Json<serde_json::Value>, ApiError> {
    let guard = state.write_lock.lock().await;
    let mut project = CityProject::load(&state.project_root)?;
    let id = project.create_control_point(&line, create)?;
    drop(project);
    drop(guard);
    let project = get_project(State(state)).await?.0;
    Ok(Json(serde_json::json!({ "id": id, "project": project })))
}

async fn put_control_point(
    State(state): State<AppState>,
    AxumPath(id): AxumPath<String>,
    Json(edit): Json<ControlPointEdit>,
) -> Result<Json<ProjectView>, ApiError> {
    let guard = state.write_lock.lock().await;
    let mut project = CityProject::load(&state.project_root)?;
    project.update_control_point(&id, edit)?;
    drop(project);
    drop(guard);
    get_project(State(state)).await
}

async fn put_service(
    State(state): State<AppState>,
    AxumPath((line, day_type)): AxumPath<(String, String)>,
    Json(plan): Json<LineServicePlan>,
) -> Result<Json<ProjectView>, ApiError> {
    if line != plan.line || day_type != plan.day_type {
        return Err(ApiError(anyhow::anyhow!(
            "route line/day type does not match the request body"
        )));
    }
    let _guard = state.write_lock.lock().await;
    let mut project = CityProject::load(&state.project_root)?;
    project.update_service_plan(plan)?;
    drop(project);
    drop(_guard);
    get_project(State(state)).await
}

async fn put_bulk_service(
    State(state): State<AppState>,
    Json(edit): Json<ServiceHeadwayBulkEdit>,
) -> Result<Json<serde_json::Value>, ApiError> {
    let guard = state.write_lock.lock().await;
    let mut project = CityProject::load(&state.project_root)?;
    let updated_line_plans = project.scale_service_headways(edit)?;
    drop(project);
    drop(guard);
    let project = get_project(State(state)).await?.0;
    Ok(Json(serde_json::json!({
        "updated_line_plans": updated_line_plans,
        "project": project,
    })))
}

async fn put_coordination_issue(
    State(state): State<AppState>,
    AxumPath(id): AxumPath<String>,
    Json(edit): Json<CoordinationEdit>,
) -> Result<Json<ProjectView>, ApiError> {
    let _guard = state.write_lock.lock().await;
    let mut project = CityProject::load(&state.project_root)?;
    project.update_coordination_issue(&id, edit)?;
    drop(project);
    drop(_guard);
    get_project(State(state)).await
}

async fn post_coordination_issue(
    State(state): State<AppState>,
    Json(create): Json<CoordinationCreate>,
) -> Result<Json<serde_json::Value>, ApiError> {
    let guard = state.write_lock.lock().await;
    let mut project = CityProject::load(&state.project_root)?;
    let id = project.create_coordination_issue(create)?;
    drop(project);
    drop(guard);
    let project = get_project(State(state)).await?.0;
    Ok(Json(serde_json::json!({ "id": id, "project": project })))
}

async fn post_approval(
    State(state): State<AppState>,
    Json(create): Json<ApprovalCreate>,
) -> Result<Json<serde_json::Value>, ApiError> {
    let guard = state.write_lock.lock().await;
    let mut project = CityProject::load(&state.project_root)?;
    let id = project.create_approval(create)?;
    drop(project);
    drop(guard);
    let project = get_project(State(state)).await?.0;
    Ok(Json(serde_json::json!({ "id": id, "project": project })))
}

async fn post_demand_flow(
    State(state): State<AppState>,
    Json(create): Json<DemandFlowCreate>,
) -> Result<Json<serde_json::Value>, ApiError> {
    let guard = state.write_lock.lock().await;
    let mut project = CityProject::load(&state.project_root)?;
    let id = project.create_demand_flow(create)?;
    drop(project);
    drop(guard);
    let project = get_project(State(state)).await?.0;
    Ok(Json(serde_json::json!({ "id": id, "project": project })))
}

async fn put_demand_flow(
    State(state): State<AppState>,
    AxumPath(id): AxumPath<String>,
    Json(edit): Json<DemandFlowEdit>,
) -> Result<Json<ProjectView>, ApiError> {
    let guard = state.write_lock.lock().await;
    let mut project = CityProject::load(&state.project_root)?;
    project.update_demand_flow(&id, edit)?;
    drop(project);
    drop(guard);
    get_project(State(state)).await
}

async fn delete_demand_flow(
    State(state): State<AppState>,
    AxumPath(id): AxumPath<String>,
) -> Result<Json<ProjectView>, ApiError> {
    let guard = state.write_lock.lock().await;
    let mut project = CityProject::load(&state.project_root)?;
    project.delete_demand_flow(&id)?;
    drop(project);
    drop(guard);
    get_project(State(state)).await
}

async fn compile_project(
    State(state): State<AppState>,
) -> Result<Json<serde_json::Value>, ApiError> {
    let _guard = state.write_lock.lock().await;
    let project = CityProject::load(&state.project_root)?;
    let output = project.write_build_snapshot(&state.repository_root)?;
    Ok(Json(serde_json::json!({
        "status": "compiled",
        "path": output.display().to_string(),
        "snapshot": project.compile()?,
    })))
}

async fn get_jobs(State(state): State<AppState>) -> Json<serde_json::Value> {
    Json(serde_json::json!({
        "adapters": JobManager::catalog(),
        "jobs": state.jobs.list().await,
    }))
}

async fn get_job(
    State(state): State<AppState>,
    AxumPath(id): AxumPath<String>,
) -> Result<Json<crate::model::JobRecord>, ApiError> {
    Ok(Json(state.jobs.get(&id).await?))
}

async fn get_job_artifact(
    State(state): State<AppState>,
    AxumPath((id, index)): AxumPath<(String, usize)>,
) -> Result<Json<crate::model::JobArtifactPreview>, ApiError> {
    Ok(Json(state.jobs.preview(&id, index).await?))
}

async fn start_job(
    State(state): State<AppState>,
    AxumPath(adapter): AxumPath<String>,
    Json(request): Json<JobRequest>,
) -> Result<(StatusCode, Json<crate::model::JobRecord>), ApiError> {
    let _guard = state.write_lock.lock().await;
    let record = state.jobs.start(&adapter, request).await?;
    Ok((StatusCode::ACCEPTED, Json(record)))
}

async fn materialize_revision(
    State(state): State<AppState>,
) -> Result<Json<serde_json::Value>, ApiError> {
    let _guard = state.write_lock.lock().await;
    let project = CityProject::load(&state.project_root)?;
    let revision = project.materialize_revision()?;
    Ok(Json(serde_json::json!({
        "status": "materialized",
        "revision": revision,
        "git": project.git_state(),
    })))
}

async fn get_revisions(State(state): State<AppState>) -> Result<Json<serde_json::Value>, ApiError> {
    let project = CityProject::load(&state.project_root)?;
    Ok(Json(serde_json::json!({
        "revisions": project.revisions()?,
        "candidate_revision_id": project.compile()?.revision_id,
    })))
}

async fn compare_revision(
    State(state): State<AppState>,
    AxumPath(id): AxumPath<String>,
) -> Result<Json<serde_json::Value>, ApiError> {
    let project = CityProject::load(&state.project_root)?;
    Ok(Json(serde_json::json!({
        "comparison": project.compare_revision(&id)?,
    })))
}

async fn get_git(State(state): State<AppState>) -> Result<Json<serde_json::Value>, ApiError> {
    let project = CityProject::load(&state.project_root)?;
    Ok(Json(serde_json::json!({ "git": project.git_state() })))
}

async fn shutdown_signal() {
    let _ = tokio::signal::ctrl_c().await;
}

#[cfg(test)]
mod tests {
    use super::*;

    fn samawah_project() -> CityProject {
        CityProject::load(
            Path::new(env!("CARGO_MANIFEST_DIR")).join("../../cities/workspaces/samawah"),
        )
        .expect("load Samawah project")
    }

    #[test]
    fn gis_manifest_is_complete_content_hashed_and_repeatable() {
        let project = samawah_project();
        let first = gis_manifest(&project).expect("first manifest");
        let second = gis_manifest(&project).expect("second manifest");
        assert_eq!(first.schema_version, 1);
        assert_eq!(first.coordinate_reference_system, "EPSG:4326");
        assert!(first.deterministic);
        assert_eq!(first.layers.len(), GIS_LAYER_IDS.len());
        assert_eq!(
            first
                .layers
                .iter()
                .map(|layer| (&layer.id, &layer.sha256, layer.feature_count))
                .collect::<Vec<_>>(),
            second
                .layers
                .iter()
                .map(|layer| (&layer.id, &layer.sha256, layer.feature_count))
                .collect::<Vec<_>>()
        );
        assert!(first.layers.iter().all(|layer| layer.sha256.len() == 64));
        assert!(first.bounds[0] < first.bounds[2]);
        assert!(first.bounds[1] < first.bounds[3]);
    }

    #[test]
    fn routing_surfaces_and_anchor_context_are_valid_geojson() {
        let project = samawah_project();
        for id in [
            "routing-demand",
            "routing-cost",
            "routing-buildability",
            "context-anchors",
            "context-roads",
            "context-buildings",
            "context-water",
            "context-protected",
            "context-existing-rail",
        ] {
            let layer = gis_layer(&project, id).expect("GIS layer");
            assert_eq!(layer["type"], "FeatureCollection");
            assert!(layer["features"]
                .as_array()
                .is_some_and(|items| !items.is_empty()));
        }
        assert!(gis_layer(&project, "../../project.osr.toml").is_err());
    }
}
