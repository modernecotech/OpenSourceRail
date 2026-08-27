use std::path::{Path, PathBuf};
use std::sync::Arc;

use anyhow::{Context, Result};
use axum::extract::{DefaultBodyLimit, Path as AxumPath, State};
use axum::http::StatusCode;
use axum::response::{Html, IntoResponse};
use axum::routing::{get, post, put};
use axum::{Json, Router};
use serde::Serialize;
use tokio::sync::Mutex;

use crate::jobs::JobManager;
use crate::model::{
    ControlPointCreate, ControlPointEdit, JobRequest, LineCreate, LineEdit, LineServicePlan,
    ProjectView, StationCreate, StationEdit,
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
        .route("/api/stations/:id", put(put_station).delete(delete_station))
        .route("/api/lines", post(post_line))
        .route("/api/lines/:id", put(put_line).delete(delete_line))
        .route("/api/lines/:line/stations", post(post_station))
        .route("/api/lines/:line/control-points", post(post_control_point))
        .route("/api/control-points/:id", put(put_control_point))
        .route("/api/services/:line/:day_type", put(put_service))
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
    }))
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
