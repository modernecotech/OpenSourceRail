use std::collections::BTreeMap;
use std::fs;
use std::path::{Path, PathBuf};
use std::sync::atomic::{AtomicU64, Ordering};
use std::sync::Arc;
use std::time::{SystemTime, UNIX_EPOCH};

use anyhow::{anyhow, bail, Context, Result};
use sha2::{Digest, Sha256};
use tokio::process::Command;
use tokio::sync::Mutex;

use crate::model::{
    JobAdapterInfo, JobArtifact, JobArtifactPreview, JobRecord, JobRequest, JobStatus,
};
use crate::CityProject;

const LOG_TAIL_CHARS: usize = 12_000;
const MAX_PREVIEW_BYTES: u64 = 4_000_000;

#[derive(Clone, Copy, Debug)]
enum Adapter {
    GisExport,
    FieldEvidence,
    Simulation,
    AlignmentExchange,
    CivilBim,
}

impl Adapter {
    fn parse(id: &str) -> Result<Self> {
        match id {
            "gis-export" => Ok(Self::GisExport),
            "field-evidence" => Ok(Self::FieldEvidence),
            "simulation" => Ok(Self::Simulation),
            "alignment-exchange" => Ok(Self::AlignmentExchange),
            "civil-bim" => Ok(Self::CivilBim),
            _ => bail!("unknown job adapter {id:?}"),
        }
    }

    fn id(self) -> &'static str {
        match self {
            Self::GisExport => "gis-export",
            Self::FieldEvidence => "field-evidence",
            Self::Simulation => "simulation",
            Self::AlignmentExchange => "alignment-exchange",
            Self::CivilBim => "civil-bim",
        }
    }

    fn label(self) -> &'static str {
        match self {
            Self::GisExport => "Compile GIS package",
            Self::FieldEvidence => "Issue field-evidence brief",
            Self::Simulation => "Run network simulation",
            Self::AlignmentExchange => "Export LandXML and railML",
            Self::CivilBim => "Generate Bonsai civil IFC4.3",
        }
    }
}

#[derive(Clone, Debug)]
pub struct JobManager {
    project_root: PathBuf,
    repository_root: PathBuf,
    slug: String,
    records: Arc<Mutex<BTreeMap<String, JobRecord>>>,
    run_lock: Arc<Mutex<()>>,
    counter: Arc<AtomicU64>,
}

impl JobManager {
    pub fn new(
        project_root: PathBuf,
        repository_root: PathBuf,
        slug: String,
        run_lock: Arc<Mutex<()>>,
    ) -> Result<Self> {
        let records = load_records(&repository_root, &slug)?;
        Ok(Self {
            project_root,
            repository_root,
            slug,
            records: Arc::new(Mutex::new(records)),
            run_lock,
            counter: Arc::new(AtomicU64::new(0)),
        })
    }

    pub fn catalog() -> Vec<JobAdapterInfo> {
        vec![
            JobAdapterInfo {
                id: "gis-export".to_string(),
                category: "GIS".to_string(),
                label: "Compile GIS package".to_string(),
                description:
                    "Compile the candidate network, day-type scenarios, and hash manifest."
                        .to_string(),
            },
            JobAdapterInfo {
                id: "field-evidence".to_string(),
                category: "Survey / site evidence".to_string(),
                label: "Issue field-evidence brief".to_string(),
                description:
                    "Generate revision-locked field requirements, an empty receipt, and explicit survey-control and ground-model readiness gates."
                        .to_string(),
            },
            JobAdapterInfo {
                id: "civil-bim".to_string(),
                category: "Civil BIM / 4D".to_string(),
                label: "Generate Bonsai civil IFC4.3".to_string(),
                description:
                    "Federate the selected line with deterministic civil detail, quantities, provenance, IDS audit, BCF issues, and a construction sequence."
                        .to_string(),
            },
            JobAdapterInfo {
                id: "simulation".to_string(),
                category: "Simulation".to_string(),
                label: "Run network simulation".to_string(),
                description:
                    "Run a fixed one-hour compact osr-sim scenario for the selected day type."
                        .to_string(),
            },
            JobAdapterInfo {
                id: "alignment-exchange".to_string(),
                category: "CAD / alignment".to_string(),
                label: "Export LandXML and railML".to_string(),
                description:
                    "Fit the selected line and emit review JSON, stakeout CSV, LandXML, and railML."
                        .to_string(),
            },
        ]
    }

    pub async fn list(&self) -> Vec<JobRecord> {
        let mut records = self
            .records
            .lock()
            .await
            .values()
            .cloned()
            .collect::<Vec<_>>();
        records.sort_by(|left, right| {
            right
                .created_unix_ms
                .cmp(&left.created_unix_ms)
                .then_with(|| right.id.cmp(&left.id))
        });
        records
    }

    pub async fn get(&self, id: &str) -> Result<JobRecord> {
        self.records
            .lock()
            .await
            .get(id)
            .cloned()
            .ok_or_else(|| anyhow!("unknown job {id:?}"))
    }

    pub async fn preview(&self, id: &str, artifact_index: usize) -> Result<JobArtifactPreview> {
        let record = self.get(id).await?;
        let artifact = record
            .artifacts
            .get(artifact_index)
            .cloned()
            .ok_or_else(|| anyhow!("job {id:?} has no artifact at index {artifact_index}"))?;
        let relative_path = Path::new(&artifact.path);
        if relative_path.is_absolute() {
            bail!("job artifact path must be repository-relative");
        }
        let path = self.repository_root.join(relative_path);
        let canonical_path = path
            .canonicalize()
            .with_context(|| format!("opening job artifact {}", path.display()))?;
        let allowed_root = self
            .repository_root
            .join("build/city-studio")
            .join(&self.slug)
            .canonicalize()
            .context("opening City Studio build root")?;
        if !canonical_path.starts_with(&allowed_root) {
            bail!("job artifact is outside the City Studio build root");
        }
        let metadata = fs::metadata(&canonical_path)?;
        if !metadata.is_file() {
            bail!("job artifact is not a regular file");
        }
        if metadata.len() > MAX_PREVIEW_BYTES {
            bail!(
                "job artifact is {} bytes; browser previews are limited to {} bytes",
                metadata.len(),
                MAX_PREVIEW_BYTES
            );
        }
        let bytes = fs::read(&canonical_path)?;
        verify_sha256(&bytes, &artifact.sha256)?;
        let (format, media_type, content) = preview_content(&canonical_path, &bytes)?;
        Ok(JobArtifactPreview {
            schema_version: 1,
            job_id: id.to_string(),
            artifact_index,
            artifact,
            format: format.to_string(),
            media_type: media_type.to_string(),
            sha256_verified: true,
            content,
        })
    }

    pub async fn start(&self, adapter_id: &str, request: JobRequest) -> Result<JobRecord> {
        let adapter = Adapter::parse(adapter_id)?;
        let project = CityProject::load(&self.project_root)?;
        let snapshot = project.compile()?;
        let requested_day_type = match adapter {
            Adapter::Simulation => {
                let day_type = request.day_type.unwrap_or_else(|| "weekday".to_string());
                if !project
                    .service_plan()
                    .day_types
                    .iter()
                    .any(|day| day.id == day_type)
                {
                    bail!("unknown simulation day type {day_type:?}");
                }
                Some(day_type)
            }
            _ => None,
        };
        let requested_line = match adapter {
            Adapter::AlignmentExchange | Adapter::CivilBim => {
                let line = request
                    .line
                    .or_else(|| snapshot.lines.first().map(|line| line.id.clone()))
                    .ok_or_else(|| anyhow!("candidate network has no lines"))?;
                if !snapshot.lines.iter().any(|candidate| candidate.id == line) {
                    bail!("unknown alignment line {line:?}");
                }
                Some(line)
            }
            _ => None,
        };
        let created_unix_ms = unix_ms();
        let sequence = self.counter.fetch_add(1, Ordering::Relaxed);
        let id = format!("job-{created_unix_ms}-{sequence:03}");
        let job_dir = self.job_dir(&id);
        fs::create_dir_all(&job_dir)
            .with_context(|| format!("creating job directory {}", job_dir.display()))?;
        let log_path = job_dir.join("job.log");
        let record = JobRecord {
            schema_version: 1,
            id: id.clone(),
            adapter: adapter.id().to_string(),
            label: adapter.label().to_string(),
            revision_id: snapshot.revision_id,
            status: JobStatus::Queued,
            progress_percent: 0,
            phase: "Waiting for engineering job slot".to_string(),
            command: display_command(
                adapter,
                requested_day_type.as_deref(),
                requested_line.as_deref(),
            ),
            requested_day_type,
            requested_line,
            created_unix_ms,
            started_unix_ms: None,
            completed_unix_ms: None,
            exit_code: None,
            error: None,
            log_path: relative_display(&self.repository_root, &log_path),
            log_tail: String::new(),
            artifacts: Vec::new(),
        };
        self.save_record(record.clone()).await?;
        let manager = self.clone();
        tokio::spawn(async move {
            manager.run(id, adapter).await;
        });
        Ok(record)
    }

    async fn run(&self, id: String, adapter: Adapter) {
        let _guard = self.run_lock.lock().await;
        if let Err(error) = self
            .update(&id, |record| {
                record.status = JobStatus::Running;
                record.progress_percent = 5;
                record.phase = "Loading and validating candidate".to_string();
                record.started_unix_ms = Some(unix_ms());
            })
            .await
        {
            eprintln!("City Studio job {id} could not start: {error:#}");
            return;
        }
        let result = self.run_adapter(&id, adapter).await;
        match result {
            Ok((exit_code, log, mut artifacts)) => {
                if let Err(error) = self.write_log(&id, &log) {
                    eprintln!("City Studio job {id} log write failed: {error:#}");
                } else if let Ok(log_artifact) =
                    self.artifact("job-log", &self.job_dir(&id).join("job.log"))
                {
                    artifacts.push(log_artifact);
                }
                let tail = tail_chars(&log, LOG_TAIL_CHARS);
                if let Err(error) = self
                    .update(&id, |record| {
                        record.status = JobStatus::Succeeded;
                        record.progress_percent = 100;
                        record.phase = "Completed".to_string();
                        record.completed_unix_ms = Some(unix_ms());
                        record.exit_code = Some(exit_code);
                        record.log_tail = tail;
                        record.artifacts = artifacts;
                    })
                    .await
                {
                    eprintln!("City Studio job {id} completion write failed: {error:#}");
                }
            }
            Err(error) => {
                let message = format!("{error:#}");
                let _ = self.write_log(&id, &message);
                let _ = self
                    .update(&id, |record| {
                        record.status = JobStatus::Failed;
                        record.progress_percent = 100;
                        record.phase = "Failed".to_string();
                        record.completed_unix_ms = Some(unix_ms());
                        record.exit_code = Some(1);
                        record.error = Some(message.clone());
                        record.log_tail = message;
                    })
                    .await;
            }
        }
    }

    async fn run_adapter(
        &self,
        id: &str,
        adapter: Adapter,
    ) -> Result<(i32, String, Vec<JobArtifact>)> {
        let record = self.get(id).await?;
        let candidate_revision = CityProject::load(&self.project_root)?
            .compile()?
            .revision_id;
        if candidate_revision != record.revision_id {
            bail!(
                "candidate changed from revision {} to {} while the job was queued; submit a new job",
                record.revision_id,
                candidate_revision
            );
        }
        match adapter {
            Adapter::GisExport => self.run_gis(id).await,
            Adapter::FieldEvidence => self.run_field_evidence(id).await,
            Adapter::Simulation => self.run_simulation(id).await,
            Adapter::AlignmentExchange => self.run_alignment(id).await,
            Adapter::CivilBim => self.run_civil_bim(id).await,
        }
    }

    async fn run_gis(&self, id: &str) -> Result<(i32, String, Vec<JobArtifact>)> {
        self.progress(id, 30, "Compiling deterministic GIS and scenario package")
            .await?;
        let project = CityProject::load(&self.project_root)?;
        let snapshot_path = project.write_build_snapshot(&self.repository_root)?;
        let output_dir = snapshot_path
            .parent()
            .ok_or_else(|| anyhow!("compiled snapshot has no output directory"))?;
        let published_paths = [
            (
                "snapshot",
                output_dir.join("snapshot.json"),
                "snapshot.json",
            ),
            (
                "gis-network",
                output_dir.join("candidate-network.geojson"),
                "candidate-network.geojson",
            ),
            (
                "manifest",
                output_dir.join("manifest.json"),
                "manifest.json",
            ),
        ];
        let job_dir = self.job_dir(id);
        let paths = published_paths
            .iter()
            .map(|(kind, published, filename)| {
                let evidence = job_dir.join(filename);
                fs::copy(published, &evidence).with_context(|| {
                    format!(
                        "copying published artifact {} to {}",
                        published.display(),
                        evidence.display()
                    )
                })?;
                Ok((*kind, evidence))
            })
            .collect::<Result<Vec<_>>>()?;
        let artifacts = paths
            .iter()
            .map(|(kind, path)| self.artifact(kind, path))
            .collect::<Result<Vec<_>>>()?;
        Ok((
            0,
            format!(
                "Compiled candidate {}\nPublished {} hash-addressed GIS/build artifacts\n",
                project.compile()?.revision_id,
                artifacts.len()
            ),
            artifacts,
        ))
    }

    async fn run_field_evidence(&self, id: &str) -> Result<(i32, String, Vec<JobArtifact>)> {
        self.progress(id, 25, "Compiling the current city revision")
            .await?;
        let project = CityProject::load(&self.project_root)?;
        let snapshot_path = project.write_build_snapshot(&self.repository_root)?;
        let output_dir = self.job_dir(id).join("field-evidence");
        fs::create_dir_all(&output_dir)?;
        self.progress(id, 55, "Generating survey and site-evidence requirements")
            .await?;
        let python = self.repository_root.join("tools/automation/osr-python");
        let generator = self
            .repository_root
            .join("engineering/analysis/survey_package.py");
        let output = Command::new(&python)
            .arg(&generator)
            .arg("--design")
            .arg(&snapshot_path)
            .arg("--output-dir")
            .arg(&output_dir)
            .current_dir(&self.repository_root)
            .kill_on_drop(true)
            .output()
            .await
            .with_context(|| {
                format!(
                    "running allowlisted field-evidence generator {}",
                    generator.display()
                )
            })?;
        let mut log = command_log(&output);
        if !output.status.success() {
            bail!("field-evidence generator exited unsuccessfully\n{log}");
        }
        self.progress(
            id,
            70,
            "Generating control, ground-model and alignment readiness gates",
        )
        .await?;
        for (name, script) in [
            ("survey-control", "engineering/analysis/survey_control.py"),
            ("ground-model", "engineering/analysis/ground_model.py"),
        ] {
            let program = self.repository_root.join(script);
            let gate_output = Command::new(&python)
                .arg(&program)
                .arg("--city")
                .arg(&self.slug)
                .arg("--manifest")
                .arg(output_dir.join("survey-input-manifest.csv"))
                .arg("--evidence-root")
                .arg(&output_dir)
                .arg("--output-dir")
                .arg(&output_dir)
                .current_dir(&self.repository_root)
                .kill_on_drop(true)
                .output()
                .await
                .with_context(|| format!("running allowlisted {name} readiness generator"))?;
            let gate_log = command_log(&gate_output);
            log.push_str(&gate_log);
            if !gate_output.status.success() {
                bail!("{name} readiness generator exited unsuccessfully\n{gate_log}");
            }
        }
        let alignment_program = self
            .repository_root
            .join("engineering/analysis/surveyed_alignment.py");
        let alignment_output = Command::new(&python)
            .arg(&alignment_program)
            .arg("--design")
            .arg(&snapshot_path)
            .arg("--manifest")
            .arg(output_dir.join("surveyed-alignment-input-manifest.csv"))
            .arg("--evidence-root")
            .arg(&output_dir)
            .arg("--output-dir")
            .arg(&output_dir)
            .arg("--write-placeholder-manifest")
            .current_dir(&self.repository_root)
            .kill_on_drop(true)
            .output()
            .await
            .context("running allowlisted surveyed-alignment readiness generator")?;
        let alignment_log = command_log(&alignment_output);
        log.push_str(&alignment_log);
        if !alignment_output.status.success() {
            bail!("surveyed-alignment readiness generator exited unsuccessfully\n{alignment_log}");
        }
        let route_fit_program = self
            .repository_root
            .join("engineering/analysis/route_station_fit.py");
        let route_fit_output = Command::new(&python)
            .arg(&route_fit_program)
            .arg("--design")
            .arg(&snapshot_path)
            .arg("--manifest")
            .arg(output_dir.join("route-station-fit-input-manifest.csv"))
            .arg("--evidence-root")
            .arg(&output_dir)
            .arg("--output-dir")
            .arg(&output_dir)
            .arg("--write-placeholder-manifest")
            .current_dir(&self.repository_root)
            .kill_on_drop(true)
            .output()
            .await
            .context("running allowlisted route/station-fit readiness generator")?;
        let route_fit_log = command_log(&route_fit_output);
        log.push_str(&route_fit_log);
        if !route_fit_output.status.success() {
            bail!("route/station-fit readiness generator exited unsuccessfully\n{route_fit_log}");
        }
        let drainage_ground_program = self
            .repository_root
            .join("engineering/analysis/drainage_ground_design.py");
        let drainage_ground_output = Command::new(&python)
            .arg(&drainage_ground_program)
            .arg("--design")
            .arg(&snapshot_path)
            .arg("--manifest")
            .arg(output_dir.join("drainage-ground-input-manifest.csv"))
            .arg("--evidence-root")
            .arg(&output_dir)
            .arg("--output-dir")
            .arg(&output_dir)
            .arg("--write-placeholder-manifest")
            .current_dir(&self.repository_root)
            .kill_on_drop(true)
            .output()
            .await
            .context("running allowlisted drainage/ground readiness generator")?;
        let drainage_ground_log = command_log(&drainage_ground_output);
        log.push_str(&drainage_ground_log);
        if !drainage_ground_output.status.success() {
            bail!(
                "drainage/ground readiness generator exited unsuccessfully\n{drainage_ground_log}"
            );
        }
        let artifacts = vec![
            self.artifact(
                "field-evidence-brief",
                &output_dir.join("field-evidence-brief.json"),
            )?,
            self.artifact(
                "field-evidence-readable",
                &output_dir.join("field-evidence-brief.md"),
            )?,
            self.artifact(
                "survey-receipt-manifest",
                &output_dir.join("survey-input-manifest.csv"),
            )?,
            self.artifact(
                "survey-control-readiness",
                &output_dir.join("control-processing-readiness.json"),
            )?,
            self.artifact(
                "survey-control-readable",
                &output_dir.join("control-processing-readiness.md"),
            )?,
            self.artifact(
                "ground-model-readiness",
                &output_dir.join("ground-model-readiness.json"),
            )?,
            self.artifact(
                "ground-model-readable",
                &output_dir.join("ground-model-readiness.md"),
            )?,
            self.artifact(
                "surveyed-alignment-manifest",
                &output_dir.join("surveyed-alignment-input-manifest.csv"),
            )?,
            self.artifact(
                "surveyed-alignment-readiness",
                &output_dir.join("surveyed-alignment-readiness.json"),
            )?,
            self.artifact(
                "surveyed-alignment-readable",
                &output_dir.join("surveyed-alignment-readiness.md"),
            )?,
            self.artifact(
                "route-station-fit-manifest",
                &output_dir.join("route-station-fit-input-manifest.csv"),
            )?,
            self.artifact(
                "route-station-fit-readiness",
                &output_dir.join("route-station-fit-readiness.json"),
            )?,
            self.artifact(
                "route-station-fit-readable",
                &output_dir.join("route-station-fit-readiness.md"),
            )?,
            self.artifact(
                "drainage-ground-manifest",
                &output_dir.join("drainage-ground-input-manifest.csv"),
            )?,
            self.artifact(
                "drainage-ground-readiness",
                &output_dir.join("drainage-ground-readiness.json"),
            )?,
            self.artifact(
                "drainage-ground-readable",
                &output_dir.join("drainage-ground-readiness.md"),
            )?,
        ];
        Ok((output.status.code().unwrap_or(0), log, artifacts))
    }

    async fn run_simulation(&self, id: &str) -> Result<(i32, String, Vec<JobArtifact>)> {
        let record = self.get(id).await?;
        let day_type = record
            .requested_day_type
            .as_deref()
            .ok_or_else(|| anyhow!("simulation job has no day type"))?;
        self.progress(id, 20, "Compiling selected day-type scenario")
            .await?;
        let project = CityProject::load(&self.project_root)?;
        project.write_build_snapshot(&self.repository_root)?;
        self.progress(id, 45, "Running fixed one-hour compact simulation")
            .await?;
        let output_path = self.job_dir(id).join(format!("simulation-{day_type}.json"));
        let scenario_path = self
            .repository_root
            .join("build/city-studio")
            .join(&self.slug)
            .join("scenarios")
            .join(format!("{day_type}.toml"));
        let arguments = vec![
            "--config".to_string(),
            scenario_path.display().to_string(),
            "--duration".to_string(),
            "3600".to_string(),
            "--status-every".to_string(),
            "300".to_string(),
            "--compact-json".to_string(),
            "--json-out".to_string(),
            output_path.display().to_string(),
        ];
        let output =
            run_rust_binary(&self.repository_root, "osr-sim", "osr-sim", &arguments).await?;
        let log = command_log(&output);
        if !output.status.success() {
            bail!("osr-sim exited unsuccessfully\n{log}");
        }
        let result: serde_json::Value = serde_json::from_slice(&fs::read(&output_path)?)?;
        let violations = result
            .get("invariant_violations")
            .and_then(serde_json::Value::as_array)
            .map_or(usize::MAX, Vec::len);
        if violations != 0 {
            bail!("simulation reported {violations} invariant violation(s)\n{log}");
        }
        Ok((
            output.status.code().unwrap_or(0),
            log,
            vec![self.artifact("simulation-result", &output_path)?],
        ))
    }

    async fn run_alignment(&self, id: &str) -> Result<(i32, String, Vec<JobArtifact>)> {
        let record = self.get(id).await?;
        let line_id = record
            .requested_line
            .as_deref()
            .ok_or_else(|| anyhow!("alignment job has no selected line"))?;
        self.progress(id, 20, "Compiling candidate line geometry")
            .await?;
        let project = CityProject::load(&self.project_root)?;
        project.write_build_snapshot(&self.repository_root)?;
        let candidate = project.candidate_network()?;
        let points = line_coordinates(&candidate, line_id)?;
        let local_points = geographic_to_local_xyz(&points)?;
        let safe_line = safe_component(line_id)?;
        let input_path = self.job_dir(id).join(format!("{safe_line}.input.json"));
        fs::write(
            &input_path,
            serde_json::to_vec_pretty(&serde_json::json!({
                "line_slug": safe_line,
                "design_speed_kmh": 80.0,
                "points": local_points,
            }))?,
        )?;
        let output_dir = self.job_dir(id).join("alignment");
        fs::create_dir_all(&output_dir)?;
        self.progress(id, 50, "Fitting alignment and writing exchange formats")
            .await?;
        let arguments = vec![
            "--input".to_string(),
            input_path.display().to_string(),
            "--out".to_string(),
            output_dir.display().to_string(),
        ];
        let output = run_rust_binary(
            &self.repository_root,
            "osr-alignment",
            "osr-alignment-export",
            &arguments,
        )
        .await?;
        let log = command_log(&output);
        if !output.status.success() {
            bail!("alignment exporter exited unsuccessfully\n{log}");
        }
        let mut paths = fs::read_dir(&output_dir)?
            .filter_map(|entry| entry.ok().map(|entry| entry.path()))
            .filter(|path| path.is_file())
            .collect::<Vec<_>>();
        paths.sort();
        let mut artifacts = vec![self.artifact("alignment-input", &input_path)?];
        for path in paths {
            let kind = match path.extension().and_then(|value| value.to_str()) {
                Some("landxml") => "landxml",
                Some("railml") => "railml",
                Some("csv") => "stakeout",
                _ => "alignment-review",
            };
            artifacts.push(self.artifact(kind, &path)?);
        }
        Ok((output.status.code().unwrap_or(0), log, artifacts))
    }

    async fn run_civil_bim(&self, id: &str) -> Result<(i32, String, Vec<JobArtifact>)> {
        let record = self.get(id).await?;
        let line_id = record
            .requested_line
            .as_deref()
            .ok_or_else(|| anyhow!("civil BIM job has no selected line"))?;
        self.progress(id, 20, "Compiling selected line reference axis")
            .await?;
        let project = CityProject::load(&self.project_root)?;
        project.write_build_snapshot(&self.repository_root)?;
        let candidate = project.candidate_network()?;
        let points = line_coordinates(&candidate, line_id)?;
        let local_points = geographic_to_local_xyz(&points)?;
        let safe_line = safe_component(line_id)?;
        let georeferencing = project
            .civil()
            .ifc_georeferencing
            .iter()
            .find(|settings| settings.line == line_id)
            .map(|settings| {
                serde_json::json!({
                    "crs_name": settings.crs_name,
                    "eastings": settings.eastings,
                    "northings": settings.northings,
                    "orthogonal_height": settings.orthogonal_height,
                    "x_axis_abscissa": settings.x_axis_abscissa,
                    "x_axis_ordinate": settings.x_axis_ordinate,
                    "scale": settings.scale,
                    "source": settings.source,
                })
            });
        let input_path = self
            .job_dir(id)
            .join(format!("{safe_line}.civil-input.json"));
        fs::write(
            &input_path,
            serde_json::to_vec_pretty(&serde_json::json!({
                "line_slug": safe_line,
                "design_speed_kmh": 80.0,
                "points": local_points,
                "coordination_issues": &project.coordination().issues,
                "georeferencing": georeferencing,
            }))?,
        )?;
        let output_dir = self.job_dir(id).join("civil-bim");
        fs::create_dir_all(&output_dir)?;
        self.progress(id, 48, "Writing deterministic IFC4.3 rail federation")
            .await?;
        let python = self.repository_root.join("tools/automation/osr-python");
        let exporter = self
            .repository_root
            .join("engineering/interchange/civil_bonsai_ifc.py");
        let output = Command::new(&python)
            .arg(&exporter)
            .arg("--out-dir")
            .arg(&output_dir)
            .arg("--alignment-input")
            .arg(&input_path)
            .arg("--revision-id")
            .arg(&record.revision_id)
            .current_dir(&self.repository_root)
            .kill_on_drop(true)
            .output()
            .await
            .with_context(|| {
                format!(
                    "running allowlisted civil IFC exporter {}",
                    exporter.display()
                )
            })?;
        let log = command_log(&output);
        if !output.status.success() {
            bail!("civil IFC exporter exited unsuccessfully\n{log}");
        }
        self.progress(
            id,
            90,
            "Auditing IFC with IDS and linking BCF review issues",
        )
        .await?;
        let artifacts = vec![
            self.artifact("civil-bim-input", &input_path)?,
            self.artifact(
                "civil-bim-index",
                &output_dir.join("civil-coordination.index.json"),
            )?,
            self.artifact("civil-ifc4x3", &output_dir.join("civil-coordination.ifc"))?,
            self.artifact(
                "civil-4d-sequence",
                &output_dir.join("civil-construction-sequence.json"),
            )?,
            self.artifact(
                "civil-bim-validation",
                &output_dir.join("civil-coordination.validation.json"),
            )?,
            self.artifact(
                "civil-ids-requirements",
                &output_dir.join("civil-information-requirements.ids"),
            )?,
            self.artifact(
                "civil-ids-report",
                &output_dir.join("civil-information-requirements.report.json"),
            )?,
            self.artifact(
                "civil-bcf3-issues",
                &output_dir.join("civil-coordination-issues.bcf"),
            )?,
            self.artifact(
                "civil-bcf3-index",
                &output_dir.join("civil-coordination-issues.index.json"),
            )?,
        ];
        Ok((output.status.code().unwrap_or(0), log, artifacts))
    }

    async fn progress(&self, id: &str, percent: u8, phase: &str) -> Result<()> {
        self.update(id, |record| {
            record.progress_percent = percent;
            record.phase = phase.to_string();
        })
        .await
    }

    async fn update(&self, id: &str, mutate: impl FnOnce(&mut JobRecord)) -> Result<()> {
        let mut records = self.records.lock().await;
        let record = records
            .get_mut(id)
            .ok_or_else(|| anyhow!("unknown job {id:?}"))?;
        mutate(record);
        write_record(&self.job_dir(id), record)
    }

    async fn save_record(&self, record: JobRecord) -> Result<()> {
        write_record(&self.job_dir(&record.id), &record)?;
        self.records.lock().await.insert(record.id.clone(), record);
        Ok(())
    }

    fn write_log(&self, id: &str, log: &str) -> Result<()> {
        fs::write(self.job_dir(id).join("job.log"), log)
            .with_context(|| format!("writing log for job {id}"))
    }

    fn artifact(&self, kind: &str, path: &Path) -> Result<JobArtifact> {
        let bytes =
            fs::read(path).with_context(|| format!("hashing job artifact {}", path.display()))?;
        Ok(JobArtifact {
            kind: kind.to_string(),
            path: relative_display(&self.repository_root, path),
            sha256: hex::encode(Sha256::digest(&bytes)),
            size_bytes: bytes.len() as u64,
        })
    }

    fn job_dir(&self, id: &str) -> PathBuf {
        self.repository_root
            .join("build/city-studio")
            .join(&self.slug)
            .join("jobs")
            .join(id)
    }
}

async fn run_rust_binary(
    repository_root: &Path,
    package: &str,
    binary: &str,
    arguments: &[String],
) -> Result<std::process::Output> {
    let executable = repository_root.join("target/debug").join(binary);
    let mut command = if executable.is_file() {
        Command::new(executable)
    } else {
        let mut command = Command::new("cargo");
        command.args(["run", "-q", "-p", package, "--bin", binary, "--"]);
        command
    };
    command
        .args(arguments)
        .current_dir(repository_root)
        .kill_on_drop(true)
        .output()
        .await
        .with_context(|| format!("running allowlisted adapter binary {binary}"))
}

fn display_command(adapter: Adapter, day_type: Option<&str>, line: Option<&str>) -> Vec<String> {
    match adapter {
        Adapter::GisExport => vec![
            "internal:osr-city-studio".to_string(),
            "compile-gis".to_string(),
        ],
        Adapter::FieldEvidence => vec![
            "survey_package.py".to_string(),
            "--current-city-revision".to_string(),
        ],
        Adapter::Simulation => vec![
            "osr-sim".to_string(),
            "--day-type".to_string(),
            day_type.unwrap_or("weekday").to_string(),
            "--duration".to_string(),
            "3600".to_string(),
        ],
        Adapter::AlignmentExchange => vec![
            "osr-alignment-export".to_string(),
            "--line".to_string(),
            line.unwrap_or("line-1").to_string(),
        ],
        Adapter::CivilBim => vec![
            "civil_bonsai_ifc.py".to_string(),
            "--line".to_string(),
            line.unwrap_or("line-1").to_string(),
            "--schema".to_string(),
            "IFC4X3".to_string(),
        ],
    }
}

fn load_records(repository_root: &Path, slug: &str) -> Result<BTreeMap<String, JobRecord>> {
    let root = repository_root
        .join("build/city-studio")
        .join(slug)
        .join("jobs");
    if !root.is_dir() {
        return Ok(BTreeMap::new());
    }
    let mut records = BTreeMap::new();
    for entry in fs::read_dir(&root).with_context(|| format!("reading {}", root.display()))? {
        let path = entry?.path().join("record.json");
        if !path.is_file() {
            continue;
        }
        let mut record: JobRecord = serde_json::from_slice(&fs::read(&path)?)?;
        if matches!(record.status, JobStatus::Queued | JobStatus::Running) {
            record.status = JobStatus::Failed;
            record.progress_percent = 100;
            record.phase = "Interrupted by server restart".to_string();
            record.completed_unix_ms = Some(unix_ms());
            record.error =
                Some("job did not complete before the City Studio process stopped".to_string());
            write_record(path.parent().expect("record has parent"), &record)?;
        }
        records.insert(record.id.clone(), record);
    }
    Ok(records)
}

fn write_record(job_dir: &Path, record: &JobRecord) -> Result<()> {
    fs::create_dir_all(job_dir)?;
    let path = job_dir.join("record.json");
    let temporary = job_dir.join("record.json.tmp");
    let mut bytes = serde_json::to_vec_pretty(record)?;
    bytes.push(b'\n');
    fs::write(&temporary, bytes)?;
    fs::rename(&temporary, &path)?;
    Ok(())
}

fn line_coordinates(candidate: &serde_json::Value, line_id: &str) -> Result<Vec<[f64; 2]>> {
    let features = candidate
        .get("features")
        .and_then(serde_json::Value::as_array)
        .ok_or_else(|| anyhow!("candidate GIS has no features"))?;
    let feature = features
        .iter()
        .find(|feature| {
            feature
                .get("properties")
                .and_then(|properties| properties.get("name"))
                .and_then(serde_json::Value::as_str)
                == Some(line_id)
                && feature
                    .get("geometry")
                    .and_then(|geometry| geometry.get("type"))
                    .and_then(serde_json::Value::as_str)
                    == Some("LineString")
        })
        .ok_or_else(|| anyhow!("candidate GIS has no line geometry for {line_id}"))?;
    feature["geometry"]["coordinates"]
        .as_array()
        .ok_or_else(|| anyhow!("line geometry coordinates are not an array"))?
        .iter()
        .map(|coordinate| {
            let pair = coordinate
                .as_array()
                .ok_or_else(|| anyhow!("line coordinate is not an array"))?;
            let lon = pair
                .first()
                .and_then(serde_json::Value::as_f64)
                .ok_or_else(|| anyhow!("line longitude is not numeric"))?;
            let lat = pair
                .get(1)
                .and_then(serde_json::Value::as_f64)
                .ok_or_else(|| anyhow!("line latitude is not numeric"))?;
            Ok([lon, lat])
        })
        .collect()
}

fn geographic_to_local_xyz(points: &[[f64; 2]]) -> Result<Vec<[f64; 3]>> {
    let origin = points
        .first()
        .ok_or_else(|| anyhow!("line geometry is empty"))?;
    let metres_per_lon = 111_320.0 * origin[1].to_radians().cos();
    Ok(points
        .iter()
        .map(|point| {
            [
                (point[0] - origin[0]) * metres_per_lon,
                (point[1] - origin[1]) * 111_132.0,
                0.0,
            ]
        })
        .collect())
}

fn safe_component(value: &str) -> Result<String> {
    if value.is_empty()
        || !value
            .bytes()
            .all(|byte| byte.is_ascii_alphanumeric() || matches!(byte, b'-' | b'_'))
    {
        bail!("line id is not safe for an artifact filename");
    }
    Ok(value.to_string())
}

fn command_log(output: &std::process::Output) -> String {
    let mut log = String::from_utf8_lossy(&output.stdout).into_owned();
    if !output.stderr.is_empty() {
        if !log.ends_with('\n') && !log.is_empty() {
            log.push('\n');
        }
        log.push_str(&String::from_utf8_lossy(&output.stderr));
    }
    log
}

fn verify_sha256(bytes: &[u8], expected: &str) -> Result<()> {
    let actual = hex::encode(Sha256::digest(bytes));
    if actual != expected {
        bail!("job artifact hash mismatch: recorded {expected}, actual {actual}");
    }
    Ok(())
}

fn preview_content<'a>(
    path: &Path,
    bytes: &'a [u8],
) -> Result<(&'a str, &'a str, serde_json::Value)> {
    let extension = path
        .extension()
        .and_then(|value| value.to_str())
        .unwrap_or_default()
        .to_ascii_lowercase();
    match extension.as_str() {
        "geojson" => Ok((
            "geojson",
            "application/geo+json",
            serde_json::from_slice(bytes).context("parsing GeoJSON artifact")?,
        )),
        "json" => Ok((
            "json",
            "application/json",
            serde_json::from_slice(bytes).context("parsing JSON artifact")?,
        )),
        "landxml" => Ok((
            "landxml",
            "application/xml",
            serde_json::Value::String(String::from_utf8(bytes.to_vec())?),
        )),
        "railml" => Ok((
            "railml",
            "application/xml",
            serde_json::Value::String(String::from_utf8(bytes.to_vec())?),
        )),
        "csv" => Ok((
            "csv",
            "text/csv",
            serde_json::Value::String(String::from_utf8(bytes.to_vec())?),
        )),
        "md" => Ok((
            "markdown",
            "text/markdown",
            serde_json::Value::String(String::from_utf8(bytes.to_vec())?),
        )),
        "ifc" => Ok((
            "ifc",
            "model/ifc",
            serde_json::Value::String(String::from_utf8(bytes.to_vec())?),
        )),
        "ids" => Ok((
            "ids",
            "application/xml",
            serde_json::Value::String(String::from_utf8(bytes.to_vec())?),
        )),
        "bcf" => {
            if !bytes.starts_with(b"PK") {
                bail!("BCF artifact is not a ZIP container");
            }
            Ok((
                "bcf",
                "application/vnd.bcf+zip",
                serde_json::json!({
                    "container": "BCF 3.0 ZIP",
                    "size_bytes": bytes.len(),
                    "inspection": "Open the companion civil-bcf3-index artifact for topic and IFC selection details.",
                }),
            ))
        }
        "log" => Ok((
            "text",
            "text/plain",
            serde_json::Value::String(String::from_utf8(bytes.to_vec())?),
        )),
        _ => bail!("artifact type {extension:?} does not have a safe browser preview"),
    }
}

fn tail_chars(value: &str, maximum: usize) -> String {
    let count = value.chars().count();
    value.chars().skip(count.saturating_sub(maximum)).collect()
}

fn relative_display(root: &Path, path: &Path) -> String {
    path.strip_prefix(root)
        .unwrap_or(path)
        .display()
        .to_string()
}

fn unix_ms() -> u128 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or_default()
        .as_millis()
}

#[cfg(test)]
mod tests {
    use std::path::Path;

    use sha2::Digest;

    use super::{preview_content, safe_component, tail_chars, verify_sha256, Adapter};

    #[test]
    fn adapter_allowlist_rejects_shell_input() {
        assert!(Adapter::parse("simulation").is_ok());
        assert!(Adapter::parse("civil-bim").is_ok());
        assert!(Adapter::parse("field-evidence").is_ok());
        assert!(Adapter::parse("simulation; rm -rf").is_err());
    }

    #[test]
    fn artifact_components_are_restrictive() {
        assert_eq!(safe_component("manual-line_12").unwrap(), "manual-line_12");
        assert!(safe_component("../line").is_err());
    }

    #[test]
    fn log_tail_is_unicode_safe() {
        assert_eq!(tail_chars("abcdé", 3), "cdé");
    }

    #[test]
    fn preview_formats_are_explicitly_allowlisted() {
        let json = preview_content(
            Path::new("network.geojson"),
            br#"{"type":"FeatureCollection"}"#,
        )
        .unwrap();
        assert_eq!(json.0, "geojson");
        let ifc = preview_content(Path::new("civil.ifc"), b"ISO-10303-21;").unwrap();
        assert_eq!(ifc.0, "ifc");
        assert_eq!(ifc.1, "model/ifc");
        let ids = preview_content(Path::new("requirements.ids"), b"<ids/>").unwrap();
        assert_eq!(ids.0, "ids");
        let bcf = preview_content(Path::new("issues.bcf"), b"PK\x03\x04").unwrap();
        assert_eq!(bcf.0, "bcf");
        let markdown = preview_content(Path::new("brief.md"), b"# Brief").unwrap();
        assert_eq!(markdown.0, "markdown");
        assert!(preview_content(Path::new("issues.bcf"), b"not a zip").is_err());
        assert!(preview_content(Path::new("board.kicad_pcb"), b"board").is_err());
    }

    #[test]
    fn preview_rejects_changed_artifact_bytes() {
        assert!(
            verify_sha256(b"changed", &hex::encode(sha2::Sha256::digest(b"original"))).is_err()
        );
    }
}
