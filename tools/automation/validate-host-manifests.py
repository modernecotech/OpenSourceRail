#!/usr/bin/env python3
"""Validate deployable host compositions against the Cargo workspace."""

from __future__ import annotations

from pathlib import Path
import argparse
import sys
import tomllib


ROOT = Path(__file__).resolve().parents[2]
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
    """Read the complete workspace package inventory without invoking Cargo.

    The Python/generated-artifact CI job should not depend on an undeclared
    Rust toolchain.  The dedicated Rust job validates Cargo itself; this check
    only needs the package names declared by the same workspace manifests.
    """

    workspace = load_toml("Cargo.toml").get("workspace", {})
    member_patterns = workspace.get("members", [])
    excluded = {
        path.resolve()
        for pattern in workspace.get("exclude", [])
        for path in ROOT.glob(str(pattern))
    }
    manifests: list[Path] = []
    for pattern in member_patterns:
        matches = sorted(ROOT.glob(str(pattern)))
        if not matches:
            raise ValueError(f"Cargo workspace member pattern has no matches: {pattern}")
        manifests.extend(
            path / "Cargo.toml"
            for path in matches
            if path.resolve() not in excluded
        )

    names: list[str] = []
    for manifest in manifests:
        if not manifest.is_file():
            raise ValueError(f"Cargo workspace member manifest is missing: {manifest}")
        with manifest.open("rb") as handle:
            package = tomllib.load(handle).get("package", {})
        name = package.get("name")
        if not name:
            raise ValueError(f"Cargo workspace member has no package.name: {manifest}")
        names.append(str(name))
    if len(names) != len(set(names)):
        duplicates = sorted({name for name in names if names.count(name) > 1})
        raise ValueError(f"duplicate Cargo workspace package names: {duplicates}")
    return set(names)


def validate_legacy() -> list[str]:
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


def validate_primary(document=None) -> list[str]:
    """Validate the offline primary profile without inheriting old host acceptance."""
    errors = []
    profile = load_toml('deployment/maglev.toml') if document is None else document
    if not isinstance(profile, dict) or any(not isinstance(profile.get(section),dict) for section in ('runtime','io','release')):
        return ['primary profile requires runtime, io and release tables']
    policy = load_toml('lib/templates/infrastructure.toml')
    if (profile.get('schema') != 'osr-maglev-development-host/1'
            or profile.get('family') != policy['development']['primary_family']
            or profile.get('role') != 'maglev-study-sbc'):
        errors.append('primary maglev profile identity differs')
    if profile.get('reference_host_images_adopted') is not False:
        errors.append('primary maglev profile cannot inherit comparator host images')
    for field in ('design_complete', 'physical_validation', 'manufacturing_release', 'physical_release'):
        if profile.get('release', {}).get(field) is not False:
            errors.append('primary development profile cannot claim '+field)
    runtime = profile.get('runtime', {})
    for field, expected in dict(language='Rust', preferred_host='off-the-shelf-SBC',
        core_package='osr-maglev-control', mode='offline-replay-only', target_sku_frozen=False,
        target_timing_measured=False).items():
        if runtime.get(field) != expected or type(runtime.get(field)) is not type(expected):
            errors.append('primary runtime.'+field+' differs')
    if profile.get('services') != ['osr-maglev-control']:
        errors.append('primary services must use the implemented offline maglev core only')
    if profile.get('retired_wheel_specific') != ['osr-hot-axle','osr-hot-axle-wayside','osr-wayside-points']:
        errors.append('wheel-specific retirement inventory differs')
    revalidate = profile.get('interface_revalidation_required')
    if not isinstance(revalidate,list) or not all(isinstance(name,str) for name in revalidate):
        errors.append('primary interface revalidation inventory required')
    elif not {'osr-traction','osr-brake','osr-odometry','osr-derailment','osr-atp','osr-bms','osr-door-control','osr-fire-safety'} <= set(revalidate):
        errors.append('primary support/brake/protection interfaces require revalidation')
    expected_examples = {'sbc_replay', 'multimodule_replay', 'egress_replay', 'coupled_bridge'}
    examples = runtime.get('examples', [])
    if not isinstance(examples, list) or any(not isinstance(name,str) for name in examples):
        errors.append('primary example inventory must be a string list')
    elif set(examples) != expected_examples or len(examples)!=len(expected_examples):
        errors.append('primary example inventory differs')
    for name in expected_examples:
        if not (ROOT/'crates/osr-maglev-control/examples'/f'{name}.rs').is_file():
            errors.append('missing actual primary Rust example: '+name)
    io = profile.get('io', {})
    if (io.get('physical_outputs_enabled') is not False or io.get('physical_adapter')!='unimplemented'
            or io.get('hardware_addresses')!=[]):
        errors.append('primary development profile cannot bind physical outputs')
    if io.get('requirements')!=['isolated-sensing-and-output','qualified-current-drive-and-cooling',
            'independent-protection-and-watchdog','support-preserving-traction-stop','measured-deadlines-and-power-loss-response']:
        errors.append('primary physical interface qualification requirements differ')
    legacy = load_toml('deployment/hosts.toml').get('architecture', {})
    if legacy.get('family')!='wheel-rail-reference' or legacy.get('primary') is not False or legacy.get('acceptance_transfers_to_maglev') is not False:
        errors.append('retained five-host scope must remain an explicit comparator')
    components = load_toml('deployment/components.toml').get('component', [])
    core = [row for row in components if row.get('name')=='osr-maglev-control']
    if len(core)!=1 or core[0].get('hosts')!=['maglev-study-sbc'] or core[0].get('disposition')!='shared-library':
        errors.append('maglev core must have an explicit development-library disposition')
    return errors


def validate() -> list[str]:
    return validate_primary()+validate_legacy()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--legacy', action='store_true', help='Check the explicit retained five-host comparator only.')
    args = parser.parse_args()
    try:
        errors = validate_legacy() if args.legacy else validate()
    except (OSError, ValueError, tomllib.TOMLDecodeError) as exc:
        print(f"host manifest validation failed: {exc}", file=sys.stderr)
        return 2
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print('host manifests: OK ('+('retained five-host comparator' if args.legacy else 'primary offline maglev profile; retained five-host comparator')+'; complete Cargo inventory; no maglev physical image released)')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
