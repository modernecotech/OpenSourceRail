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

use crate::model::{JobAdapterInfo, JobArtifact, JobRecord, JobRequest, JobStatus};
use crate::CityProject;

const LOG_TAIL_CHARS: usize = 12_000;

#[derive(Clone, Copy, Debug)]
enum Adapter {
    GisExport,
    Simulation,
    AlignmentExchange,
}

impl Adapter {
    fn parse(id: &str) -> Result<Self> {
        match id {
            "gis-export" => Ok(Self::GisExport),
            "simulation" => Ok(Self::Simulation),
            "alignment-exchange" => Ok(Self::AlignmentExchange),
            _ => bail!("unknown job adapter {id:?}"),
        }
    }

    fn id(self) -> &'static str {
        match self {
            Self::GisExport => "gis-export",
            Self::Simulation => "simulation",
            Self::AlignmentExchange => "alignment-exchange",
        }
    }

    fn label(self) -> &'static str {
        match self {
            Self::GisExport => "Compile GIS package",
            Self::Simulation => "Run network simulation",
            Self::AlignmentExchange => "Export LandXML and railML",
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
            Adapter::AlignmentExchange => {
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
            Adapter::Simulation => self.run_simulation(id).await,
            Adapter::AlignmentExchange => self.run_alignment(id).await,
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
        let paths = [
            ("snapshot", output_dir.join("snapshot.json")),
            ("gis-network", output_dir.join("candidate-network.geojson")),
            ("manifest", output_dir.join("manifest.json")),
        ];
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
    use super::{safe_component, tail_chars, Adapter};

    #[test]
    fn adapter_allowlist_rejects_shell_input() {
        assert!(Adapter::parse("simulation").is_ok());
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
}
