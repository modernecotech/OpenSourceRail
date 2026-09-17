#!/usr/bin/env python3
"""Audit every catalogue city's tracked ERP and supervision inputs."""

from __future__ import annotations

import argparse
from collections import Counter
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import subprocess
from functools import lru_cache
import tomllib


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_JSON = ROOT / "docs/operating/readiness.json"
DEFAULT_MARKDOWN = ROOT / "docs/operating/readiness.md"
sys.path.insert(0, str(ROOT / "deployment/erpnext/apps/osr_erpnext"))
sys.path.insert(0, str(ROOT / "services/integration"))

from osr_erpnext.city_config import make_city_plan, validate_city_plan  # noqa: E402
from osr_erpnext.component_catalogue import validate_package as validate_component_package  # noqa: E402


def load_script(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ERP_CITY = load_script("readiness_erp_city", ROOT / "tools/automation/erpnext-city.py")
ERP_COMPONENTS = load_script(
    "readiness_erp_components", ROOT / "tools/automation/erp-components.py"
)
SUPERVISION = load_script(
    "readiness_supervision", ROOT / "tools/automation/supervision.py"
)
# Both command modules load the same catalogue helper when run independently.
# Reuse one cache inside this audit so 266 large design files are parsed once.
ERP_COMPONENTS.cities = ERP_CITY
SUPERVISION.cities = ERP_CITY

COMPILER_INPUTS = [
    ROOT / "tools/automation/operating-readiness.py",
    ROOT / "tools/automation/erpnext-city.py",
    ROOT / "tools/automation/erp-components.py",
    ROOT / "tools/automation/supervision.py",
    ROOT / "deployment/erpnext/config/generic.toml",
    ROOT / "deployment/erpnext/config/components.json",
    ROOT / "deployment/erpnext/apps/osr_erpnext/osr_erpnext/city_config.py",
    ROOT / "deployment/erpnext/apps/osr_erpnext/osr_erpnext/component_catalogue.py",
    ROOT / "deployment/erpnext/apps/osr_erpnext/osr_erpnext/planning.py",
    ROOT / "deployment/supervision/config/generic.json",
    ROOT / "design/component-catalogue/catalog/buildable-trainset/manufacturing-methods.json",
    ROOT / "design/component-catalogue/catalog/buildable-trainset/buildable-trainset-manifest.json",
    ROOT / "lib/templates/trainset-manufacturing-methods.toml",
    ROOT / "services/integration/osr_integration/config.py",
    ROOT / "services/integration/osr_integration/manufacturing.py",
]


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def file_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@lru_cache(maxsize=1)
def tracked_bundles():
    # Reproducible checked-in evidence inventory, independent of local builds.
    names = subprocess.check_output(['git', 'ls-files', '-z', '--', '*-operations.json.gz'], cwd=ROOT)
    return set(names.decode().split('\0'))


def source_digest() -> str:
    paths = list(COMPILER_INPUTS)
    for city_dir in sorted(path.parent for path in
                           (ROOT / "cities/catalogue").glob("*/*/*/design.toml")):
        with (city_dir / "design.toml").open("rb") as handle:
            design = tomllib.load(handle)
        slug = design["city"]["slug"]
        paths.extend([
            city_dir / "design.toml",
            city_dir / f"{slug}.toml",
            city_dir / "operations/erpnext.toml",
            city_dir / "operations/erp-components.json",
            city_dir / "operations/supervision.json",
            city_dir / "operations" / f"{slug}-assets.csv",
            city_dir / "operations" / f"{slug}-operations-manifest.json",
            city_dir / "engineering/project-twin/summary.json",
        ])
        bundle = city_dir / "operations" / f"{slug}-operations.json.gz"
        if bundle.is_file() and relative(bundle) in tracked_bundles():
            paths.append(bundle)
    digest = hashlib.sha256()
    for path in sorted(set(paths)):
        require(path.is_file(), f"Missing readiness input: {relative(path)}")
        digest.update(relative(path).encode())
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def audit_city(slug: str) -> dict[str, object]:
    design_path, catalogue_city = ERP_CITY.catalogue()[slug]
    city_dir = design_path.parent
    operations = city_dir / "operations"
    scenario_path = city_dir / f"{slug}.toml"
    asset_path = operations / f"{slug}-assets.csv"
    manifest_path = operations / f"{slug}-operations-manifest.json"
    twin_path = city_dir / "engineering/project-twin/summary.json"
    bundle_path = operations / f"{slug}-operations.json.gz"

    require(scenario_path.is_file(), f"{slug}: missing scenario")
    design = tomllib.loads(design_path.read_text())
    require(design.get("city", {}).get("slug") == slug, f"{slug}: design identity mismatch")

    assets, revision = SUPERVISION.city_assets(slug)
    require(assets, f"{slug}: empty asset register")
    asset_ids = [row.get("asset_id", "") for row in assets]
    require(all(asset_ids), f"{slug}: blank asset identity")
    require(len(asset_ids) == len(set(asset_ids)), f"{slug}: duplicate asset identity")

    manifest = json.loads(manifest_path.read_text())
    twin = json.loads(twin_path.read_text())
    require(twin.get("totals", {}).get("assets") == len(assets),
            f"{slug}: project twin and asset register differ")

    erp_config = ERP_CITY.effective_config(slug)
    component_package = ERP_COMPONENTS.make_package(
        ERP_COMPONENTS.effective(slug), f"readiness-{slug}"
    )
    validate_component_package(component_package)
    supervision_package = SUPERVISION.city_package(slug)

    profile_path = operations / "supervision.json"
    supervision_profile = json.loads(profile_path.read_text())
    full_plan: dict[str, object] = {
        "status": "generate-on-demand",
        "records": None,
        "package_sha256": None,
    }
    if bundle_path.is_file() and relative(bundle_path) in tracked_bundles():
        compressed = bundle_path.read_bytes()
        require(
            hashlib.sha256(compressed).hexdigest() == manifest["compressed_sha256"],
            f"{slug}: compressed operations hash mismatch",
        )
        payload = gzip.decompress(compressed)
        require(
            hashlib.sha256(payload).hexdigest() == manifest["uncompressed_sha256"],
            f"{slug}: uncompressed operations hash mismatch",
        )
        bundle = json.loads(payload)
        require(bundle.get("project_twin", {}).get("city") == slug,
                f"{slug}: operations bundle identity mismatch")
        require(bundle.get("project_twin", {}).get("revision_id") == revision,
                f"{slug}: operations bundle revision mismatch")
        plan = make_city_plan(bundle, erp_config)
        validate_city_plan(plan)
        full_plan = {
            "status": "compiled",
            "records": len(plan["records"]),
            "package_sha256": plan["package_sha256"],
        }

    asset_counts = Counter(row["asset_type"] for row in assets)
    task_totals = {
        key: manifest.get("totals", {}).get(key)
        for key in (
            "manufacturing_tasks",
            "maintenance_tasks",
            "qa_actions",
            "planned_purchase_orders",
        )
    }
    return {
        "city": slug,
        "country_code": catalogue_city["country"],
        "paths": {
            "design": relative(design_path),
            "scenario": relative(scenario_path),
            "asset_register": relative(asset_path),
            "operations_manifest": relative(manifest_path),
            "project_twin": relative(twin_path),
            "operations_bundle": relative(bundle_path) if bundle_path.is_file() else None,
        },
        "revision": revision,
        "evidence": {
            "assets": len(assets),
            "asset_types": dict(sorted(asset_counts.items())),
            "task_totals": task_totals,
            "manifest_uncompressed_sha256": manifest["uncompressed_sha256"],
            "asset_register_sha256": file_digest(asset_path),
        },
        "compiled": {
            "erp_profile": "valid",
            "erp_full_plan": full_plan,
            "components": {
                "instances": len(component_package["instances"]),
                "package_sha256": component_package["sha256"],
            },
            "supervision": {
                "equipment": len(supervision_package["equipment"]),
                "package_sha256": supervision_package["sha256"],
            },
        },
        "deployment_inputs": {
            "company_configured": bool(erp_config["organisation"]["company"]),
            "calendar_start_configured": bool(erp_config["calendar"]["start_date"]),
            "timezone_configured": bool(erp_config["calendar"]["timezone"]),
            "erp_project_configured": bool(supervision_profile.get("erp_project")),
            "physical_bindings": len(supervision_profile.get("bindings", {})),
        },
    }


def build_report(slugs: list[str] | None = None) -> dict[str, object]:
    available = ERP_CITY.catalogue()
    selected = sorted(slugs or available)
    unknown = sorted(set(selected) - set(available))
    require(not unknown, "Unknown cities: " + ", ".join(unknown))
    cities = [audit_city(slug) for slug in selected]

    def count(predicate) -> int:
        return sum(bool(predicate(city)) for city in cities)

    totals = {
        "cities": len(cities),
        "asset_registers_validated": len(cities),
        "operations_manifests_validated": len(cities),
        "project_twins_validated": len(cities),
        "erp_profiles_validated": len(cities),
        "component_packages_compiled": len(cities),
        "supervision_packages_compiled": len(cities),
        "supervision_equipment": sum(
            city["compiled"]["supervision"]["equipment"] for city in cities
        ),
        "full_operations_bundles": count(
            lambda city: city["paths"]["operations_bundle"] is not None
        ),
        "full_erp_plans_compiled": count(
            lambda city: city["compiled"]["erp_full_plan"]["status"] == "compiled"
        ),
        "company_configured": count(
            lambda city: city["deployment_inputs"]["company_configured"]
        ),
        "calendar_start_configured": count(
            lambda city: city["deployment_inputs"]["calendar_start_configured"]
        ),
        "timezone_configured": count(
            lambda city: city["deployment_inputs"]["timezone_configured"]
        ),
        "erp_project_configured": count(
            lambda city: city["deployment_inputs"]["erp_project_configured"]
        ),
        "physical_bindings": sum(
            city["deployment_inputs"]["physical_bindings"] for city in cities
        ),
    }
    return {
        "schema": "osr-operating-readiness/1",
        "scope": "catalogue" if slugs is None else "selected-cities",
        "source_sha256": source_digest(),
        "totals": totals,
        "cities": cities,
    }


def markdown(report: dict[str, object]) -> str:
    totals = report["totals"]
    cities = report["cities"]
    complete = [city["city"] for city in cities
                if city["compiled"]["erp_full_plan"]["status"] == "compiled"]
    materialise = [city["city"] for city in cities
                   if city["compiled"]["erp_full_plan"]["status"] != "compiled"]
    rows = [
        ("Design, scenario, asset register, manifest and project twin", totals["asset_registers_validated"]),
        ("ERP city profile", totals["erp_profiles_validated"]),
        ("Reusable ERP component package", totals["component_packages_compiled"]),
        ("Real-asset simulation supervision package", totals["supervision_packages_compiled"]),
        ("Full ERP task plan from a local operations payload", totals["full_erp_plans_compiled"]),
    ]
    table = "\n".join(f"| {label} | {ready}/{totals['cities']} |" for label, ready in rows)
    complete_text = ", ".join(f"`{slug}`" for slug in complete) or "None"
    materialise_text = (
        f"{len(materialise)} cities" if len(materialise) > 12
        else ", ".join(f"`{slug}`" for slug in materialise) or "None"
    )
    return f"""# Operating platform readiness

> Generated by `./osr readiness`. Do not edit this file or `readiness.json` by hand.

This gate compiles the tracked ERP, reusable-component and supervision inputs
against each city's own engineering evidence. It separates repository-complete
work from information that only a real operator, supplier or commissioning team
can provide.

## Catalogue result

| Gate | Ready |
|---|---:|
{table}

The supervision result covers **{totals['supervision_equipment']:,} equipment records**
derived from the {totals['asset_registers_validated']} tracked city
asset registers. A compressed operations payload is no longer required to
prepare FUXA/gateway packages.

Full ERP task-plan compilation is exercised for {complete_text}. For the other
{materialise_text}, the tracked manifest, asset register and compact project twin
are validated here, while the large deterministic task payload is materialised
on demand with `./osr city <slug>` before ERP import. This is a storage/materialisation
boundary, not permission to substitute another city's tasks.

## Deployment-owned inputs

| Input recorded in tracked profiles | Configured |
|---|---:|
| Legal ERP company | {totals['company_configured']}/{totals['cities']} |
| Approved calendar start | {totals['calendar_start_configured']}/{totals['cities']} |
| Local timezone | {totals['timezone_configured']}/{totals['cities']} |
| ERP project link for supervision | {totals['erp_project_configured']}/{totals['cities']} |
| Physical equipment bindings | {totals['physical_bindings']} |

Blank deployment inputs are deliberate fail-closed states. This audit does not
invent companies, dates, holidays, employees, suppliers, ERP masters, serial
numbers, controller addresses, field results or approval evidence.

## Reproduce

```bash
./osr readiness
./osr readiness --check
./osr readiness --deep-check
./osr supervision validate
./osr erp city validate
./osr erp components validate
```

The machine-readable per-city paths, counts, revisions, package hashes and
deployment-input states are in [readiness.json](readiness.json).
"""


def serialise(report: dict[str, object]) -> str:
    return json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def check(path: Path, expected: str) -> bool:
    if not path.is_file() or path.read_text() != expected:
        display = relative(path) if path.is_relative_to(ROOT) else str(path)
        print(f"stale operating-readiness output: {display}", file=sys.stderr)
        return False
    return True


def check_tracked(json_path: Path, markdown_path: Path) -> bool:
    if not json_path.is_file():
        print(f"missing operating-readiness output: {json_path}", file=sys.stderr)
        return False
    try:
        report = json.loads(json_path.read_text())
    except (json.JSONDecodeError, OSError) as error:
        print(f"invalid operating-readiness output: {error}", file=sys.stderr)
        return False
    if report.get("schema") != "osr-operating-readiness/1":
        print("invalid operating-readiness schema", file=sys.stderr)
        return False
    if report.get("source_sha256") != source_digest():
        print("operating-readiness sources changed; run ./osr readiness", file=sys.stderr)
        return False
    return check(json_path, serialise(report)) and check(markdown_path, markdown(report))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="quickly fail unless tracked reports match their inputs")
    mode.add_argument("--deep-check", action="store_true", help="recompile every package and compare tracked reports")
    parser.add_argument("--json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--markdown", type=Path, default=DEFAULT_MARKDOWN)
    args = parser.parse_args()

    if args.check:
        return 0 if check_tracked(args.json, args.markdown) else 1
    report = build_report()
    json_text = serialise(report)
    markdown_text = markdown(report)
    if args.deep_check:
        return 0 if check(args.json, json_text) and check(args.markdown, markdown_text) else 1
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.markdown.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json_text)
    args.markdown.write_text(markdown_text)
    totals = report["totals"]
    print(
        f"Operating readiness: {totals['cities']} cities, "
        f"{totals['supervision_packages_compiled']} supervision packages, "
        f"{totals['full_erp_plans_compiled']} full ERP plans"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
