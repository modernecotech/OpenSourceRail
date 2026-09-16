"""Portable container-transfer behaviour for the ERP launcher."""
from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


def load_platform():
    spec = importlib.util.spec_from_file_location(
        "erp_platform", ROOT / "tools/automation/erp-platform.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_container_transfer_cleanup_is_independent_of_host_uid(monkeypatch) -> None:
    platform = load_platform()
    calls = []

    def run(command, **kwargs):
        calls.append((command, kwargs))

    monkeypatch.setattr(platform.subprocess, "run", run)
    compose = ["docker", "compose", "-f", "compose.yaml"]
    environment = {"PATH": "/usr/bin"}
    platform.remove_container_files(
        compose, "/tmp/osr-input.json", "/tmp/osr-output.json", env=environment
    )

    assert calls == [
        (
            compose
            + [
                "exec",
                "-T",
                "--user",
                "root",
                "backend",
                "rm",
                "-f",
                "/tmp/osr-input.json",
                "/tmp/osr-output.json",
            ],
            {"check": True, "env": environment},
        )
    ]
