"""Depot inventory must follow the operating tier, not a smaller legacy kit."""

import json
import shutil
from pathlib import Path

import pytest

from osr_mech.depot.energy import TEMPLATES, depot_energy_scope
from osr_mech.depot.layout import DepotArchetype, depot_footprint


def test_main_depot_inventory_and_space_balance():
    scope = depot_energy_scope("main-heavy")
    assert scope["pv_nameplate_kw"] == 5000
    assert scope["storage_module_count"] == 80
    assert scope["storage_capacity_kwh"] == 80 * 500
    assert scope["required_pv_module_area_m2"] == pytest.approx(5000 / 0.15)
    assert scope["additional_pv_module_area_m2"] == pytest.approx(5000 / 0.15 - 4000)
    assert scope["additional_storage_kwh"] == 38000
    assert scope["storage_compound_area_m2"] is None
    assert scope["deployment_release_ready"] is False


@pytest.mark.parametrize("archetype,modules,size", [("secondary-medium", 10, 500), ("layup-minimal", 1, 150)])
def test_other_archetypes_use_whole_modules(archetype, modules, size):
    scope = depot_energy_scope(archetype)
    assert scope["storage_module_count"] == modules
    assert scope["storage_module_kwh"] == size


def test_layout_and_station_bom_use_the_same_inventory():
    scope = depot_footprint(DepotArchetype.MAIN_HEAVY, stalls=6).energy_requirements
    path = TEMPLATES.parents[1] / "design/component-catalogue/catalog/buildable-stations/station-kit-manifest.json"
    report = json.loads(path.read_text())
    variant = next(v for v in report["variants"] if v["archetype"] == "depot-terminal")
    assert variant["parameters"]["depot_pv_nameplate_kw"] == scope["pv_nameplate_kw"]
    assert variant["parameters"]["depot_storage_capacity_kwh"] == scope["storage_capacity_kwh"]
    assert variant["parameters"]["depot_storage_module_count"] == scope["storage_module_count"]
    item = next(item for item in variant["product_items"] if item["id"] == "STN-DEP-P050")
    assert "80 x 500 kWh = 40000 kWh" in item["quantity_basis"]
    assert "placement and cost closure pending" in item["quantity_basis"]


def test_changing_canonical_tier_changes_quantities_and_area(tmp_path):
    for name in ("depots.toml", "energy-sites.toml"):
        shutil.copy2(TEMPLATES / name, tmp_path / name)
    path = tmp_path / "energy-sites.toml"
    path.write_text(path.read_text().replace("pv_nameplate_kw          = 5000", "pv_nameplate_kw          = 6000").replace("storage_capacity_kwh     = 40000", "storage_capacity_kwh     = 45000"))
    scope = depot_energy_scope("main-heavy", templates_root=tmp_path)
    assert scope["storage_module_count"] == 90
    assert scope["required_pv_module_area_m2"] == 40000


@pytest.mark.parametrize("site", [
    {"tier": "depot-main", "storage_capacity_kwh": 40001},
    {"tier": "depot-main", "pv_nameplate_kw": float("nan")},
    {"tier": "depot-main", "storage_module_kwh": 0},
    {"tier": "standard"},
])
def test_conflicting_or_nonphysical_site_quantities_are_rejected(site):
    with pytest.raises(ValueError):
        depot_energy_scope("main-heavy", site=site)
