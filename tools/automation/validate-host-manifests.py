#!/usr/bin/env python3
"""Validate deployable host compositions against the Cargo workspace."""

from __future__ import annotations

from pathlib import Path
import argparse
import sys
import tomllib


ROOT = Path(__file__).resolve().parents[2]

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


def validate_primary(document=None) -> list[str]:
    """Validate an offline development profile; physical adapters remain unimplemented."""
    errors = []
    profile = load_toml('deployment/maglev.toml') if document is None else document
    if not isinstance(profile, dict) or any(not isinstance(profile.get(section),dict) for section in ('runtime','io','release')):
        return ['primary profile requires runtime, io and release tables']
    policy = load_toml('lib/templates/infrastructure.toml')
    if (profile.get('schema') != 'osr-maglev-development-host/1'
            or profile.get('family') != policy['development']['primary_family']
            or profile.get('role') != 'maglev-study-sbc'):
        errors.append('primary maglev profile identity differs')
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
    interfaces = profile.get('interface_qualification_required')
    if interfaces != ['levitation-and-guidance','linear-propulsion','support-and-braking',
            'independent-protection','battery-and-power','doors-and-egress','thermal-and-fire']:
        errors.append('primary physical interface qualification inventory differs')
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
    hosts = load_toml('deployment/hosts.toml')
    expected_host = dict(id='maglev-study-sbc', config='deployment/maglev.toml',
        services=['osr-maglev-control'], mode='offline-replay-only', physical_outputs_enabled=False)
    if hosts.get('schema') != 'osr-development-hosts/1' or hosts.get('host') != [expected_host]:
        errors.append('host inventory must contain only the offline maglev study host')
    components = load_toml('deployment/components.toml')
    expected_component = dict(name='osr-maglev-control',hosts=['maglev-study-sbc'],
        disposition='research-library',physical_release=False)
    if (components.get('schema') != 'osr-development-components/1'
            or components.get('default_disposition') != 'unqualified-research-software'
            or components.get('component') != [expected_component]):
        errors.append('component inventory must distinguish the offline core from unqualified shared software')
    packages = workspace_packages()
    if 'osr-maglev-control' not in packages:
        errors.append('maglev core is absent from the Cargo workspace')
    return errors


def validate() -> list[str]:
    return validate_primary()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    try:
        errors = validate()
    except (OSError, ValueError, tomllib.TOMLDecodeError) as exc:
        print(f"host manifest validation failed: {exc}", file=sys.stderr)
        return 2
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f'host manifests: OK (offline maglev study; {len(workspace_packages())} Cargo packages classified; physical outputs disabled)')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
