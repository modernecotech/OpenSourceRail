#!/usr/bin/env python3
"""Serve the integrated OSR Workbench, Ops Core, WASM GUIs, and City Studio."""

from __future__ import annotations

import argparse
import http.client
import importlib.util
import json
import shutil
import signal
import subprocess
import sys
import threading
import time
import tomllib
import uuid
from pathlib import Path
from urllib.parse import unquote, urlsplit


REPO_ROOT = Path(__file__).resolve().parents[2]


def load_ops_core():
    path = REPO_ROOT / "tools/automation" / "ops-core-server.py"
    spec = importlib.util.spec_from_file_location("osr_ops_core_server", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


OPS = load_ops_core()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8090)
    parser.add_argument("--city-port", type=int, default=8091)
    parser.add_argument("--project", type=Path, default=REPO_ROOT / "cities/workspaces" / "samawah")
    parser.add_argument("--isolated-project", type=Path)
    parser.add_argument("--db", type=Path, default=REPO_ROOT / "var" / "ops-core.sqlite3")
    parser.add_argument("--reset-db", action="store_true")
    args = parser.parse_args()

    for required in [
        REPO_ROOT / "build" / "frontend" / "sim" / "index.html",
        REPO_ROOT / "build" / "frontend" / "occ" / "index.html",
        REPO_ROOT / "target" / "debug" / "osr-city-studio",
    ]:
        if not required.exists():
            raise SystemExit(f"missing {required.relative_to(REPO_ROOT)}; run npm run frontend:build")

    fixture = None
    project = args.project.resolve()
    if args.isolated_project:
        source = args.isolated_project.resolve()
        fixture = REPO_ROOT / "build" / "playwright" / f"workbench-project-{args.port}"
        if fixture.exists():
            shutil.rmtree(fixture)
        shutil.copytree(source, fixture)
        external_prefix = str((REPO_ROOT / "cities/catalogue").resolve())
        for relative in ["project.osr.toml", "sources.lock.json"]:
            path = fixture / relative
            path.write_text(path.read_text().replace("../../catalogue", external_prefix))
        project = fixture

    project_config = tomllib.loads((project / "project.osr.toml").read_text())
    city_slug = project_config["project"]["slug"]
    design_path = (project / project_config["inputs"]["base_design"]).resolve()
    operations_path = design_path.parent / "operations" / f"{city_slug}-operations.json.gz"
    operations_url = "/" + operations_path.relative_to(REPO_ROOT).as_posix()

    db_path = args.db.resolve()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if args.reset_db and db_path.exists():
        db_path.unlink()
    with OPS.connect(db_path) as connection:
        OPS.init_db(connection)
    evidence_path = db_path.parent / "ops-evidence"
    evidence_path.mkdir(parents=True, exist_ok=True)
    signing_key_path = db_path.with_suffix(".signing-key")

    twin_manager = ProjectTwinManager(REPO_ROOT)

    city_process = subprocess.Popen(
        [
            str(REPO_ROOT / "target" / "debug" / "osr-city-studio"),
            "--project", str(project), "serve", "--host", "127.0.0.1",
            "--port", str(args.city_port),
        ],
        cwd=REPO_ROOT,
    )
    wait_for_city(args.city_port, city_process)

    class Handler(WorkbenchHandler):
        database_path = db_path
        evidence_root = evidence_path
        user_store = None
        attestation_key = OPS.load_or_create_signing_key(signing_key_path)
        sessions = {}
        private_paths = (db_path, evidence_path, signing_key_path)
        city_port = args.city_port
        bootstrap = {"city": city_slug, "operations_data": operations_url}
        project_twins = twin_manager

    server = OPS.ThreadingHTTPServer((args.host, args.port), Handler)
    signal.signal(signal.SIGTERM, stop_server)
    print(f"OSR Workbench: http://{args.host}:{args.port}/")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        city_process.terminate()
        try:
            city_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            city_process.kill()
            city_process.wait()
        if fixture:
            shutil.rmtree(fixture, ignore_errors=True)
    return 0


class WorkbenchHandler(OPS.OpsCoreHandler):
    city_port: int
    bootstrap: dict[str, str]
    project_twins: "ProjectTwinManager"

    def do_GET(self) -> None:
        path = urlsplit(self.path).path
        if path == "/api/workbench":
            self._send_json(200, self.bootstrap)
            return
        if path == "/api/twins/catalogue":
            self._send_json(200, {"cities": self.project_twins.catalogue()})
            return
        if path.startswith("/api/twins/jobs/"):
            job = self.project_twins.job(unquote(path.removeprefix("/api/twins/jobs/")))
            self._send_json(200 if job else 404, job or {"error": "unknown project-twin job"})
            return
        if self._is_city_request():
            self._proxy_city("GET")
            return
        super().do_GET()

    def do_POST(self) -> None:
        path = urlsplit(self.path).path
        if path.startswith("/api/ops-auth/") or path.startswith("/api/ops-core/"):
            super().do_POST()
            return
        if path.startswith("/api/twins/generate/"):
            slug = unquote(path.removeprefix("/api/twins/generate/")).strip("/")
            try:
                self._send_json(202, self.project_twins.start(slug))
            except ValueError as error:
                self._send_json(400, {"error": str(error)})
            return
        self._proxy_city("POST")

    def do_PUT(self) -> None:
        if self._api_city() is not None:
            super().do_PUT()
            return
        self._proxy_city("PUT")

    def do_DELETE(self) -> None:
        self._proxy_city("DELETE")

    def translate_path(self, request_path: str) -> str:
        path = unquote(urlsplit(request_path).path)
        mappings = [
            ("/workbench/", REPO_ROOT / "docs" / "workbench"),
            ("/simulator/", REPO_ROOT / "build" / "frontend" / "sim"),
            ("/occ/", REPO_ROOT / "build" / "frontend" / "occ"),
            ("/operations/", REPO_ROOT / "docs" / "operations-portal"),
            ("/generated/project-twins/", REPO_ROOT / "build" / "workbench" / "project-twins"),
        ]
        if path == "/":
            return str(REPO_ROOT / "docs" / "workbench" / "index.html")
        for prefix, root in mappings:
            if path.startswith(prefix):
                relative = path[len(prefix):] or "index.html"
                candidate = (root / relative).resolve()
                if root.resolve() not in candidate.parents and candidate != root.resolve():
                    return str(root / "__invalid__")
                return str(candidate)
        return super().translate_path(request_path)

    def _is_city_request(self) -> bool:
        path = urlsplit(self.path).path
        return path == "/studio" or path.startswith("/studio/") or (
            path.startswith("/api/")
            and not path.startswith("/api/ops-core/")
            and not path.startswith("/api/ops-auth/")
            and not path.startswith("/api/twins/")
            and path != "/api/workbench"
        )

    def _proxy_city(self, method: str) -> None:
        parsed = urlsplit(self.path)
        target = parsed.path
        if target == "/studio":
            target = "/"
        elif target.startswith("/studio/"):
            target = target[len("/studio"):]
        if parsed.query:
            target += f"?{parsed.query}"
        length = int(self.headers.get("Content-Length", "0") or "0")
        body = self.rfile.read(length) if length else None
        headers = {
            key: value for key, value in self.headers.items()
            if key.lower() in {"accept", "content-type"}
        }
        connection = http.client.HTTPConnection("127.0.0.1", self.city_port, timeout=60)
        try:
            connection.request(method, target, body=body, headers=headers)
            response = connection.getresponse()
            payload = response.read()
            self.send_response(response.status)
            for key, value in response.getheaders():
                if key.lower() not in {"connection", "content-length", "transfer-encoding"}:
                    self.send_header(key, value)
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
        except OSError as error:
            self._send_json(502, {"error": f"City Studio unavailable: {error}"})
        finally:
            connection.close()


def wait_for_city(port: int, process: subprocess.Popen, timeout: float = 30.0) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError(f"City Studio exited with status {process.returncode}")
        connection = http.client.HTTPConnection("127.0.0.1", port, timeout=1)
        try:
            connection.request("GET", "/api/project")
            if connection.getresponse().status == 200:
                return
        except OSError:
            time.sleep(0.1)
        finally:
            connection.close()
    raise TimeoutError("City Studio did not become ready")


def stop_server(_signum, _frame) -> None:
    raise KeyboardInterrupt


class ProjectTwinManager:
    """Allowlisted, asynchronous generation for tracked catalogue cities."""

    def __init__(self, repository_root: Path):
        self.repository_root = repository_root
        self.output_root = repository_root / "build" / "workbench" / "project-twins"
        self.output_root.mkdir(parents=True, exist_ok=True)
        self._cities = self._discover()
        self._jobs: dict[str, dict] = {}
        self._lock = threading.Lock()

    def _discover(self) -> dict[str, dict]:
        cities: dict[str, dict] = {}
        for design_path in sorted((self.repository_root / "cities" / "catalogue").glob("*/*/*/design.toml")):
            design = tomllib.loads(design_path.read_text(encoding="utf-8"))
            city = design.get("city", {})
            slug = str(city.get("slug", design_path.parent.name.lower()))
            families = sorted({
                str(line.get("rolling_stock"))
                for line in design.get("lines", [])
                if line.get("rolling_stock")
            })
            finance_path = design_path.parent / "engineering" / "finance" / "summary.json"
            capex = 0.0
            if finance_path.is_file():
                finance = json.loads(finance_path.read_text(encoding="utf-8"))
                capex = float(finance.get("capex_usd", {}).get("reconciled_project_total", 0.0))
            cities[slug] = {
                "slug": slug,
                "name": str(city.get("name") or design_path.parent.name.replace("-", " ")),
                "country": str(city.get("country", design_path.parent.parent.name)),
                "rolling_stock_family": families[0] if len(families) == 1 else "review-required",
                "lines": len(design.get("lines", [])),
                "stations": len(design.get("stations", [])),
                "trainsets": sum(int(row.get("trainset_count", 0)) for row in design.get("fleets", [])),
                "planned_capex_usd": capex,
                "design_path": str(design_path),
            }
        return cities

    def catalogue(self) -> list[dict]:
        return [
            {key: value for key, value in row.items() if key != "design_path"}
            for row in sorted(self._cities.values(), key=lambda item: (item["country"], item["name"]))
        ]

    def start(self, slug: str) -> dict:
        if slug not in self._cities:
            raise ValueError("select a tracked catalogue city")
        with self._lock:
            active = next(
                (job for job in self._jobs.values() if job["city"] == slug and job["status"] in {"queued", "running"}),
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
            }
            self._jobs[job_id] = job
        threading.Thread(target=self._run, args=(job_id,), daemon=True).start()
        return dict(job)

    def job(self, job_id: str) -> dict | None:
        with self._lock:
            job = self._jobs.get(job_id)
            return dict(job) if job else None

    def _update(self, job_id: str, **values) -> None:
        with self._lock:
            self._jobs[job_id].update(values)

    def _run(self, job_id: str) -> None:
        job = self.job(job_id)
        if not job:
            return
        slug = job["city"]
        city = self._cities[slug]
        output_dir = self.output_root / slug
        self._update(job_id, status="running", phase="Generating assets, assembly plan, CPM, orders, costs and cashflow", progress_percent=15)
        command = [
            sys.executable,
            str(self.repository_root / "tools" / "automation" / "generate-qa-maintenance-data.py"),
            "--design", city["design_path"],
            "--out-dir", str(output_dir),
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
                raise RuntimeError((result.stderr or result.stdout or "generation failed")[-4000:])
            summary_path = output_dir / "project-twin-summary.json"
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
            self._update(
                job_id,
                status="completed",
                phase="Generated and reconciled",
                progress_percent=100,
                revision_id=summary["revision_id"],
                summary=summary,
                operations_data=f"/generated/project-twins/{slug}/{slug}-operations.json.gz",
                artifact_root=f"/generated/project-twins/{slug}/",
                log_tail=result.stdout[-4000:],
            )
        except Exception as error:
            self._update(job_id, status="failed", phase="Generation failed", progress_percent=100, error=str(error))


if __name__ == "__main__":
    raise SystemExit(main())
