"""Scenario capacities have one depot tier source and reject shadow quantities."""

import tomllib
from pathlib import Path

import pytest

from osr_scenario.generator import GeneratorError, ScenarioGenerator, generate_from_path, generate_scenario

ROOT = Path(__file__).resolve().parents[3]
TEMPLATES = ROOT / "lib/templates"
SAMAWAH = ROOT / "cities/catalogue/west-asia/Iraq/Samawah/design.toml"


def test_missing_depot_tier_cannot_silently_fall_back(tmp_path):
    generator = ScenarioGenerator({}, tmp_path / "design.toml", tmp_path)
    with pytest.raises(GeneratorError, match="no fallback"):
        generator.site_defaults("depot-main")


def test_legacy_depot_quantities_cannot_disagree_with_operating_site():
    design = tomllib.loads(SAMAWAH.read_text())
    design["depots"][0]["battery_kwh"] = 2000
    with pytest.raises(GeneratorError, match="battery_kwh conflicts"):
        generate_scenario(design, SAMAWAH, TEMPLATES)


def test_explicit_passenger_tier_cannot_replace_depot_equipment():
    design = tomllib.loads(SAMAWAH.read_text())
    design["sites"] = [{"station": design["depots"][0]["station"], "tier": "standard"}]
    with pytest.raises(GeneratorError, match="expected tier 'depot-main'"):
        generate_scenario(design, SAMAWAH, TEMPLATES)


def test_existing_catalogue_depot_pv_and_storage_are_preserved():
    paths = sorted((ROOT / "cities/catalogue").glob("*/*/*/design.toml"))
    assert len(paths) == 266
    for path in paths:
        slug = tomllib.loads(path.read_text())["city"]["slug"]
        generated = tomllib.loads(generate_from_path(path))
        retained = tomllib.loads(path.with_name(f"{slug}.toml").read_text())
        # Some retained cities have separate charging/grid scaling. This contract
        # covers the depot PV and storage inventory, not that existing drift.
        old_sites = {site["station"]: site for site in retained["sites"]}
        for site in generated["sites"]:
            if site["tier"].startswith("depot-"):
                for key in ("pv_nameplate_kw", "storage_capacity_kwh", "storage_module_kwh"):
                    assert site[key] == old_sites[site["station"]][key], (path, key)
