"""City project-twin jobs; extracted without changing the public launcher API."""

from pathlib import Path
import json, subprocess, sys, threading, tomllib, uuid, os, hashlib

from engineering.design_engine.store import process_ownership, process_start


class ProjectTwinManager:
    """Allowlisted, asynchronous generation for tracked catalogue cities."""

    def __init__(self, repository_root: Path):
        self.repository_root = repository_root
        self.output_root = repository_root / "build" / "workbench" / "project-twins"
        self.output_root.mkdir(parents=True, exist_ok=True)
        self._cities = self._discover()
        self._jobs: dict[str, dict] = {}
        self._lock = threading.Lock()
        self._record_root = self.output_root / "job-records"
        self._record_root.mkdir(exist_ok=True)
        for path in sorted(self._record_root.glob("twin-*.json")):
            job = json.loads(path.read_text())
            if job["city"] not in self._cities or path.stem != job["id"]:
                continue
            if job["status"] in {"queued", "running"}:
                if process_ownership(job.get("owner_pid"), job.get("owner_process_start")) is False:
                    job.update(
                        status="interrupted",
                        error="local server stopped; original request and partial output retained",
                    )
                    self._persist(job)
            self._jobs[job["id"]] = job

    def _persist(self, job):
        path = self._record_root / (job["id"] + ".json")
        temporary = path.with_suffix("." + uuid.uuid4().hex + ".tmp")
        with temporary.open("x") as stream:
            json.dump(job, stream, allow_nan=False)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)

    def jobs(self, city):
        with self._lock:
            return [dict(job) for job in self._jobs.values() if job["city"] == city]

    def _discover(self) -> dict[str, dict]:
        cities: dict[str, dict] = {}
        for design_path in sorted(
            (self.repository_root / "cities" / "catalogue").glob("*/*/*/design.toml")
        ):
            design = tomllib.loads(design_path.read_text(encoding="utf-8"))
            city = design.get("city", {})
            slug = str(city.get("slug", design_path.parent.name.lower()))
            families = sorted(
                {
                    str(line.get("rolling_stock"))
                    for line in design.get("lines", [])
                    if line.get("rolling_stock")
                }
            )
            finance_path = (
                design_path.parent / "engineering" / "finance" / "summary.json"
            )
            capex = 0.0
            if finance_path.is_file():
                finance = json.loads(finance_path.read_text(encoding="utf-8"))
                capex = float(
                    finance.get("capex_usd", {}).get("reconciled_project_total", 0.0)
                )
            cities[slug] = {
                "slug": slug,
                "name": str(
                    city.get("name") or design_path.parent.name.replace("-", " ")
                ),
                "country": str(city.get("country", design_path.parent.parent.name)),
                "rolling_stock_family": (
                    families[0] if len(families) == 1 else "review-required"
                ),
                "lines": len(design.get("lines", [])),
                "stations": len(design.get("stations", [])),
                "trainsets": sum(
                    int(row.get("trainset_count", 0))
                    for row in design.get("fleets", [])
                ),
                "planned_capex_usd": capex,
                "design_path": str(design_path),
                "operations_data": "/"
                + (design_path.parent / "operations" / f"{slug}-operations.json.gz")
                .relative_to(self.repository_root)
                .as_posix(),
            }
        return cities

    def catalogue(self) -> list[dict]:
        return [
            {key: value for key, value in row.items() if key != "design_path"}
            for row in sorted(
                self._cities.values(), key=lambda item: (item["country"], item["name"])
            )
        ]

    def start(self, slug: str) -> dict:
        if slug not in self._cities:
            raise ValueError("select a tracked catalogue city")
        with self._lock:
            active = next(
                (
                    job
                    for job in self._jobs.values()
                    if job["city"] == slug and job["status"] in {"queued", "running"}
                ),
                None,
            )
            if active:
                return dict(active)
            job_id = f"twin-{slug}-{uuid.uuid4().hex[:10]}"
            job = {
                "id": job_id,
                "city": slug,
                "status": "queued",
                "phase": "Queued deterministic city package generation",
                "progress_percent": 0,
                "error": None,
                "owner_pid": os.getpid(),
                "owner_process_start": process_start(os.getpid()),
                "design_sha256": hashlib.sha256(
                    Path(self._cities[slug]["design_path"]).read_bytes()
                ).hexdigest(),
                "physical_release": False,
            }
            self._jobs[job_id] = job
            self._persist(job)
        threading.Thread(target=self._run, args=(job_id,), daemon=True).start()
        return dict(job)

    def job(self, job_id: str) -> dict | None:
        with self._lock:
            job = self._jobs.get(job_id)
            return dict(job) if job else None

    def _update(self, job_id: str, **values) -> None:
        with self._lock:
            self._jobs[job_id].update(values)
            self._persist(self._jobs[job_id])

    def _run(self, job_id: str) -> None:
        job = self.job(job_id)
        if not job:
            return
        slug = job["city"]
        city = self._cities[slug]
        output_dir = self.output_root / job_id
        self._update(
            job_id,
            status="running",
            phase="Generating assets, assembly plan, CPM, orders, costs and cashflow",
            progress_percent=15,
        )
        command = [
            sys.executable,
            str(
                self.repository_root
                / "tools"
                / "automation"
                / "generate-qa-maintenance-data.py"
            ),
            "--design",
            city["design_path"],
            "--out-dir",
            str(output_dir),
        ]
        try:
            result = subprocess.run(
                command,
                cwd=self.repository_root,
                capture_output=True,
                text=True,
                timeout=300,
                check=False,
            )
            if result.returncode:
                raise RuntimeError(
                    (result.stderr or result.stdout or "generation failed")[-4000:]
                )
            summary_path = output_dir / "project-twin-summary.json"
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
            if (
                hashlib.sha256(Path(city["design_path"]).read_bytes()).hexdigest()
                != job["design_sha256"]
            ):
                raise ValueError(
                    "city definition changed during generation; partial artifacts retained"
                )
            self._update(
                job_id,
                status="completed",
                phase="Generated and reconciled",
                progress_percent=100,
                revision_id=summary["revision_id"],
                summary=summary,
                operations_data=f"/generated/project-twins/{job_id}/{slug}-operations.json.gz",
                artifact_root=f"/generated/project-twins/{job_id}/",
                log_tail=result.stdout[-4000:],
            )
        except Exception as error:
            self._update(
                job_id,
                status="failed",
                phase="Generation failed",
                progress_percent=100,
                error=str(error),
            )
