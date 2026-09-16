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


def load_supervision():
    spec = importlib.util.spec_from_file_location(
        "supervision", ROOT / "tools/automation/supervision.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def expected_private_transfer(compose, *paths, environment):
    prefix = compose + ["exec", "-T", "--user", "root", "backend"]
    return [
        (prefix + ["chown", "frappe:frappe", *paths], {"check": True, "env": environment}),
        (prefix + ["chmod", "600", *paths], {"check": True, "env": environment}),
    ]


def test_container_transfer_is_private_and_independent_of_host_uid(monkeypatch) -> None:
    platform = load_platform()
    calls = []
    monkeypatch.setattr(
        platform.subprocess, "run", lambda command, **kwargs: calls.append((command, kwargs))
    )
    compose = ["docker", "compose", "-f", "compose.yaml"]
    environment = {"PATH": "/usr/bin"}

    platform.secure_container_files(
        compose, "/tmp/osr-input.json", env=environment
    )

    assert calls == expected_private_transfer(
        compose, "/tmp/osr-input.json", environment=environment
    )


def test_supervision_uses_the_same_private_erp_transfer(monkeypatch) -> None:
    supervision = load_supervision()
    calls = []
    monkeypatch.setattr(
        supervision.subprocess, "run", lambda command, **kwargs: calls.append((command, kwargs))
    )
    compose = ["docker", "compose", "-f", "compose.yaml"]
    environment = {"PATH": "/usr/bin"}

    supervision.secure_erp_transfer(
        compose, "/tmp/osr-supervision.json", env=environment
    )

    assert calls == expected_private_transfer(
        compose, "/tmp/osr-supervision.json", environment=environment
    )


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
