#!/usr/bin/env python3
"""Validate deployable host compositions against the Cargo workspace."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tomllib


ROOT = Path(__file__).resolve().parents[1]
HOST_IDS = {"t-ecu-s", "t-ecu-a", "t-obs", "w-sbc", "s-sbc"}
DISPOSITIONS = {
    "composed-service",
    "deployable-endpoint",
    "shared-library",
    "simulation",
    "tooling",
}


def load_toml(relative: str) -> dict:
    with (ROOT / relative).open("rb") as handle:
        return tomllib.load(handle)


def workspace_packages() -> set[str]:
    result = subprocess.run(
        ["cargo", "metadata", "--no-deps", "--format-version", "1"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    metadata = json.loads(result.stdout)
    return {package["name"] for package in metadata["packages"]}


def validate() -> list[str]:
    errors: list[str] = []
    hosts_doc = load_toml("deployment/hosts.toml")
    components_doc = load_toml("deployment/components.toml")
    hosts = hosts_doc.get("host", [])
    components = components_doc.get("component", [])

    if hosts_doc.get("schema_version") != 1:
        errors.append("deployment/hosts.toml: unsupported schema_version")
    defaults = hosts_doc.get("defaults", {})
    for field in (
        "log_format",
        "log_sink",
        "log_rotation_mib",
        "update_strategy",
        "signature_algorithm",
        "rollback_trigger",
        "rollback_timeout_seconds",
    ):
        if not defaults.get(field):
            errors.append(f"deployment/hosts.toml: defaults.{field} is required")

    ids = [host.get("id") for host in hosts]
    if set(ids) != HOST_IDS or len(ids) != len(HOST_IDS):
        errors.append(f"host IDs must be exactly {sorted(HOST_IDS)}, got {ids}")

    cargo_packages = workspace_packages()
    component_names = [item.get("name") for item in components]
    duplicate_components = sorted(
        {name for name in component_names if component_names.count(name) > 1}
    )
    if duplicate_components:
        errors.append(f"duplicate component dispositions: {duplicate_components}")
    classified = set(component_names)
    if cargo_packages != classified:
        errors.append(
            "component inventory differs from Cargo metadata; "
            f"missing={sorted(cargo_packages - classified)}, "
            f"unknown={sorted(classified - cargo_packages)}"
        )

    component_by_name = {item.get("name"): item for item in components}
    for item in components:
        name = item.get("name", "<missing>")
        if item.get("disposition") not in DISPOSITIONS:
            errors.append(f"component {name}: invalid disposition")
        if not item.get("hosts"):
            errors.append(f"component {name}: hosts must not be empty")

    for host in hosts:
        host_id = host.get("id", "<missing>")
        services = host.get("services", [])
        if len(services) != len(set(services)):
            errors.append(f"host {host_id}: duplicate services")
        unknown = sorted(set(services) - cargo_packages)
        if unknown:
            errors.append(f"host {host_id}: unknown Cargo packages {unknown}")
        ordered = [service for group in host.get("startup_order", []) for service in group]
        if ordered != list(dict.fromkeys(ordered)):
            errors.append(f"host {host_id}: startup order repeats services")
        if set(ordered) != set(services):
            errors.append(
                f"host {host_id}: startup order mismatch; "
                f"missing={sorted(set(services) - set(ordered))}, "
                f"extra={sorted(set(ordered) - set(services))}"
            )
        selftest = host.get("selftest", [])
        if selftest != ["osr-selftest", "--role", host_id, "--json"]:
            errors.append(f"host {host_id}: invalid commissioning self-test")

        config_path = ROOT / host.get("config", "")
        if not config_path.is_file():
            errors.append(f"host {host_id}: missing config {config_path}")
        else:
            with config_path.open("rb") as handle:
                config = tomllib.load(handle)
            if config.get("schema_version") != 1 or config.get("role") != host_id:
                errors.append(f"host {host_id}: config identity/schema mismatch")
            if config.get("identity_source") != "provisioned-trust-anchor":
                errors.append(f"host {host_id}: identity must come from provisioning")

        for service in services:
            disposition = component_by_name.get(service, {})
            declared_hosts = disposition.get("hosts", [])
            if "all" not in declared_hosts and host_id not in declared_hosts:
                errors.append(
                    f"host {host_id}: {service} disposition does not declare this host"
                )

    return errors


def main() -> int:
    try:
        errors = validate()
    except (OSError, subprocess.CalledProcessError, tomllib.TOMLDecodeError) as exc:
        print(f"host manifest validation failed: {exc}", file=sys.stderr)
        return 2
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("host manifests: OK (5 hosts; complete Cargo component inventory)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
