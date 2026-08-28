#!/usr/bin/env python3
"""Serve the integrated OSR Workbench, Ops Core, WASM GUIs, and City Studio."""

from __future__ import annotations

import argparse
import http.client
import importlib.util
import shutil
import signal
import subprocess
import sys
import time
import tomllib
from pathlib import Path
from urllib.parse import unquote, urlsplit


REPO_ROOT = Path(__file__).resolve().parents[1]


def load_ops_core():
    path = REPO_ROOT / "scripts" / "ops-core-server.py"
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
    parser.add_argument("--project", type=Path, default=REPO_ROOT / "projects" / "samawah")
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
        external_prefix = str((REPO_ROOT / "designs").resolve())
        for relative in ["project.osr.toml", "sources.lock.json"]:
            path = fixture / relative
            path.write_text(path.read_text().replace("../../designs", external_prefix))
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
        city_port = args.city_port
        bootstrap = {"city": city_slug, "operations_data": operations_url}

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

    def do_GET(self) -> None:
        if urlsplit(self.path).path == "/api/workbench":
            self._send_json(200, self.bootstrap)
            return
        if self._is_city_request():
            self._proxy_city("GET")
            return
        super().do_GET()

    def do_POST(self) -> None:
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


if __name__ == "__main__":
    raise SystemExit(main())
