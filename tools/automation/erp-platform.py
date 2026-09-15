#!/usr/bin/env python3
"""Build and operate the local ERPNext + Frappe HR deployment."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import secrets
import shutil
import subprocess
import uuid

ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = ROOT / "var/erpnext/local.env"


def init():
    ENV_FILE.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    if not ENV_FILE.exists():
        with open(ENV_FILE, "x", opener=lambda path, flags: os.open(path, flags, 0o600)) as f:
            f.write(f"DB_PASSWORD={secrets.token_hex(24)}\nADMIN_PASSWORD={secrets.token_hex(24)}\n"
                    "SITE_NAME=osr.localhost\nERP_PORT=8080\n")
    print(f"Private configuration: {ENV_FILE}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["init", "build", "up", "setup", "status", "stop", "logs", "backup", "bench", "import", "snapshot", "feedback", "component-preview", "component-apply"])
    parser.add_argument("args", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    if args.command == "init":
        init()
        return
    if args.command == "feedback":
        action = args.args[0] if len(args.args) == 1 else ""
        if action not in {"start", "stop", "status"}:
            parser.error("usage: osr erp feedback start|stop|status")
        name = "osr-erp-feedback"
        if action == "start":
            directory = Path.home() / ".config/systemd/user"
            directory.mkdir(parents=True, exist_ok=True)
            script = json.dumps(str(ROOT / "tools/automation/erp-platform.py").replace("%", "%%"))
            (directory / (name + ".service")).write_text(
                "# Managed by OpenSourceRail: ./osr erp feedback start\n"
                "[Unit]\nDescription=Refresh private OpenSourceRail ERP twin snapshots\n"
                "[Service]\nType=oneshot\nUMask=0077\n"
                f"ExecStart=/usr/bin/python3 {script} snapshot\n")
            (directory / (name + ".timer")).write_text(
                "# Managed by OpenSourceRail: ./osr erp feedback start\n"
                "[Unit]\nDescription=Refresh OpenSourceRail ERP feedback every five minutes\n"
                "[Timer]\nOnStartupSec=1min\nOnUnitActiveSec=5min\n"
                "[Install]\nWantedBy=timers.target\n")
            subprocess.run(["systemctl", "--user", "daemon-reload"], check=True)
            subprocess.run(["systemctl", "--user", "enable", "--now", name + ".timer"], check=True)
            subprocess.run(["systemctl", "--user", "start", name + ".service"], check=True)
        elif action == "stop":
            subprocess.run(["systemctl", "--user", "disable", "--now", name + ".timer"], check=True)
        else:
            subprocess.run(["systemctl", "--user", "status", "--no-pager", name + ".timer"], check=True)
        return
    docker = shutil.which("docker") or str(Path.home() / "bin/docker")
    if not Path(docker).is_file():
        parser.error("Docker is missing. Install Docker Engine with Compose, or Docker rootless mode.")
    if not ENV_FILE.exists():
        init()
    env = dict(os.environ)
    env["PATH"] = str(Path(docker).parent) + os.pathsep + env["PATH"]
    compose = [docker, "compose", "--env-file", str(ENV_FILE), "-f", str(ROOT / "deployment/erpnext/compose.yaml")]
    config = dict(line.split("=", 1) for line in ENV_FILE.read_text().splitlines() if line and not line.startswith("#"))
    if args.command in {"component-preview", "component-apply"}:
        if len(args.args) != 1:
            parser.error('A compiled component package path is required')
        selected = Path(args.args[0]).resolve()
        import sys
        sys.path.insert(0, str(ROOT / 'deployment/erpnext/apps/osr_erpnext'))
        from osr_erpnext.component_catalogue import validate_package
        validate_package(json.loads(selected.read_text()))
        remote = '/tmp/osr-components-' + uuid.uuid4().hex + '.json'
        subprocess.run(compose + ['cp', str(selected), 'backend:' + remote], check=True, env=env)
        try:
            subprocess.run(compose + ['exec', '-T', 'backend', 'bench', '--site', config['SITE_NAME'],
                'execute', 'osr_erpnext.components.apply_file', '--kwargs', json.dumps(dict(path=remote,
                preview_only=int(args.command == 'component-preview')))], check=True, env=env)
        finally:
            subprocess.run(compose + ['exec', '-T', 'backend', 'rm', '-f', remote], check=True, env=env)
        return
    if args.command == "import":
        importer = argparse.ArgumentParser(prog="osr erp import")
        importer.add_argument("plan", type=Path)
        importer.add_argument("--company", required=True)
        selected = importer.parse_args(args.args)
        from importlib import import_module
        import sys
        sys.path.insert(0, str(ROOT / "deployment/erpnext/apps/osr_erpnext"))
        plan = json.loads(selected.plan.read_text())
        if plan.get("schema") == "osr-erpnext-city/1":
            import_module("osr_erpnext.city_config").validate_city_plan(plan)
        else:
            import_module("osr_erpnext.planning").validate_plan(plan)
        remote = "/tmp/osr-plan-" + uuid.uuid4().hex + ".json"
        subprocess.run(compose + ["cp", str(selected.plan.resolve()), "backend:" + remote], check=True, env=env)
        try:
            subprocess.run(compose + ["exec", "-T", "backend", "bench", "--site", config["SITE_NAME"],
                "execute", "osr_erpnext.api.import_file", "--kwargs",
                json.dumps({"path": remote, "company": selected.company})], check=True, env=env)
        finally:
            subprocess.run(compose + ["exec", "-T", "backend", "rm", "-f", remote], check=True, env=env)
        return
    if args.command == "snapshot":
        if args.args:
            parser.error("snapshot takes no arguments; exports all OSR projects into private local storage")
        destination = ROOT / "var/erpnext/operating-twins.json"
        temporary = destination.with_name(destination.name + "." + uuid.uuid4().hex + ".pending")
        remote = "/tmp/osr-snapshot-" + uuid.uuid4().hex + ".json"
        try:
            subprocess.run(compose + ["exec", "-T", "backend", "bench", "--site", config["SITE_NAME"],
                "execute", "osr_erpnext.city_runtime.export_snapshots", "--kwargs", json.dumps({"path": remote})], check=True, env=env)
            subprocess.run(compose + ["cp", "backend:" + remote, str(temporary)], check=True, env=env)
            payload = json.loads(temporary.read_text())
            if payload.get("schema") != "osr-operating-portfolio/1":
                raise ValueError("Invalid ERP snapshot")
            temporary.chmod(0o600)
            temporary.replace(destination)
        finally:
            subprocess.run(compose + ["exec", "-T", "backend", "rm", "-f", remote], check=True, env=env)
            temporary.unlink(missing_ok=True)
        print(f"Refreshed private digital-twin feedback: {destination}")
        return
    commands = {
        "build": ["build", "backend"], "up": ["up", "-d"],
        "setup": ["run", "--rm", "create-site"], "status": ["ps", "--all"],
        "stop": ["stop"], "logs": ["logs", "--tail", "80"],
        "backup": ["exec", "-T", "backend", "bench", "--site", config["SITE_NAME"], "backup", "--with-files"],
        "bench": ["exec", "-T", "backend", "bench", "--site", config["SITE_NAME"]],
    }
    subprocess.run(compose + commands[args.command] + args.args, check=True, env=env)


if __name__ == "__main__":
    main()
