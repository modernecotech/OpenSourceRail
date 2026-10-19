"""Manifest coverage gate vetoes missing, edited and source-stale inventories."""
import importlib.util
import json
from pathlib import Path
import shutil

import pytest

ROOT = Path(__file__).resolve().parents[3]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def package(tmp_path, monkeypatch):
    tool = tmp_path / "tools/automation/generate-city-design-status.py"
    tool.parent.mkdir(parents=True)
    shutil.copyfile(ROOT / "tools/automation/generate-city-design-status.py", tool)
    city = tmp_path / "cities/example"
    city.mkdir(parents=True)
    (city / "design.toml").write_text('[city]\nslug="example"\ncountry="XX"\n[[lines]]\nrolling_stock="tram-small"\nlength_m=1000\n')
    inventory = load("fixture_inventory", tool)
    manifest = load("fixture_city_manifest", ROOT / "tools/automation/generate-city-package-manifest.py")
    monkeypatch.setattr(manifest, "REPO_ROOT", tmp_path)
    return city, inventory, manifest


def test_manifest_requires_generated_current_inventory(package):
    city, inventory, manifest = package
    assert not manifest.current_design_inventory(city)
    inventory.generate(city / "design.toml", manifest.REPO_ROOT)
    assert manifest.current_design_inventory(city)
    (city / "design.toml").write_text((city / "design.toml").read_text().replace("1000", "2000"))
    assert not manifest.current_design_inventory(city)


@pytest.mark.parametrize("target", ["summary.json", "index.html"])
def test_manifest_rejects_edited_design_coverage(package, target):
    city, inventory, manifest = package
    inventory.generate(city / "design.toml", manifest.REPO_ROOT)
    output = city / "engineering/design-system" / target
    output.write_text("altered publication")
    assert not manifest.current_design_inventory(city)


def test_manifest_rejects_fabricated_release_claim(package):
    city, inventory, manifest = package
    inventory.generate(city / "design.toml", manifest.REPO_ROOT)
    output = city / "engineering/design-system/summary.json"
    report = json.loads(output.read_text())
    report["manufacturing_release"] = True
    output.write_bytes(inventory.encoded(report))
    assert not manifest.current_design_inventory(city)


def test_manifest_holds_when_an_upstream_design_receipt_is_stale(package):
    city, inventory, manifest = package
    path = city/'engineering/energy/summary.json'
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps({'design_sha256': '0'*64, 'passed': True}))
    report = inventory.generate(city/'design.toml', manifest.REPO_ROOT)
    assert report['counts']['stale_system_domains'] > 0
    assert not manifest.current_design_inventory(city)
