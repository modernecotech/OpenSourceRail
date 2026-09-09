"""Physical AC connection limits must remain independent of transformer sizing."""

import importlib.util
import json
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = REPO_ROOT / "engineering/analysis/city_microgrid.py"
SPEC = importlib.util.spec_from_file_location("city_microgrid", MODULE_PATH)
microgrid = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(microgrid)


def site(import_kw=500.0, export_kw=0.0, pv_kw=0.0):
    return {"station": "test", "grid_import_kw": import_kw, "grid_export_kw": export_kw,
            "pv_nameplate_kw": pv_kw, "storage_max_discharge_kw": 0.0}


@pytest.mark.parametrize("import_kw,passes", [(500.0, False), (516.0, False), (550.0, True)])
def test_import_includes_converter_and_transformer_losses(tmp_path, import_kw, passes):
    network = microgrid.build_network([site(import_kw)], {"test": 500.0}, pv_factor=0, storage_factor=0)
    result = microgrid.run_case(network, tmp_path / "case.json")
    connection = result["site_connections"][0]

    assert result["converged"]
    assert result["overloaded_transformer_count"] == 0
    assert connection["grid_import_kw"] > 500.0 / 0.97
    assert connection["grid_export_kw"] == 0
    assert connection["passed"] is passes
    assert result["connection_limit_exceedance_count"] == int(not passes)


@pytest.mark.parametrize("export_kw,passes", [(0.0, False), (80.0, False), (100.0, True)])
def test_export_uses_its_own_limit_and_opposite_power_direction(tmp_path, export_kw, passes):
    network = microgrid.build_network([site(1000.0, export_kw, 100.0)], {"test": 0.0}, pv_factor=1, storage_factor=0)
    result = microgrid.run_case(network, tmp_path / "case.json")
    connection = result["site_connections"][0]

    assert result["converged"]
    assert connection["grid_import_kw"] == 0
    assert 90.0 < connection["grid_export_kw"] < 100.0 * 0.97
    assert connection["passed"] is passes


def test_solver_failure_cannot_be_reported_as_convergence(tmp_path, monkeypatch):
    network = microgrid.build_network([site()], {"test": 500.0}, pv_factor=0, storage_factor=0)
    def fail(*args, **kwargs):
        raise RuntimeError("test convergence failure")
    monkeypatch.setattr(microgrid.pp, "runpp", fail)
    result = microgrid.run_case(network, tmp_path / "case.json")
    assert result["converged"] is False
    assert "test convergence failure" in result["error"]


def test_city_generation_fails_design_despite_converged_solver(tmp_path, monkeypatch):
    design = REPO_ROOT / "cities/catalogue/west-asia/Iraq/Samawah/design.toml"
    monkeypatch.setattr(microgrid, "clear_sky_specific_yield", lambda *args: 2000.0)
    report = microgrid.generate(design, tmp_path)

    assert report["solver_passed"] is True
    assert report["passed"] is False
    assert report["deployment_release_ready"] is False
    findings = [row for row in report["design_findings"] if row["code"] == "site-grid-connection-limit-exceeded"]
    assert len(findings) == 7
    assert all(row["case"] == "peak_charge_grid_only" for row in findings)
    assert all(row["import_exceedance_kw"] > 500 / 0.97 - 500 for row in findings)
    assert json.loads((tmp_path / "summary.json").read_text())["passed"] is False


def test_catalogue_energy_summaries_are_current_and_fail_closed():
    paths = sorted((REPO_ROOT / "cities/catalogue").glob("*/*/*/engineering/energy/summary.json"))
    assert len(paths) == 266
    for path in paths:
        report = json.loads(path.read_text())
        assert report["generator_sha256"] == microgrid.source_hash(MODULE_PATH), path
        for name in ("design", "scenario", "climate"):
            assert report[f"{name}_sha256"] == microgrid.source_hash(REPO_ROOT / report[f"{name}_input"]), path
        assert report["passed"] == (report["solver_passed"] and not report["design_findings"]), path
        for case in report["cases"].values():
            assert len(case["site_connections"]) == report["site_count"], path
            assert case["connection_limit_exceedance_count"] == sum(not row["passed"] for row in case["site_connections"]), path


def test_catalogue_gis_and_plots_reference_current_inputs():
    for path in (REPO_ROOT / "cities/catalogue").glob("*/*/*/design.toml"):
        engineering = path.parent / "engineering"
        gis = json.loads((engineering / "gis/summary.json").read_text())
        assert gis["generator_sha256"] == microgrid.source_hash(REPO_ROOT / "engineering/analysis/city_package.py"), path
        for name in ("design", "scenario", "corridor"):
            assert gis[f"{name}_sha256"] == microgrid.source_hash(REPO_ROOT / gis[f"{name}_input"]), path
        manifest = json.loads((engineering / "screenshots/manifest.json").read_text())
        assert manifest["generator_sha256"] == microgrid.source_hash(REPO_ROOT / "tools/automation/render-city-engineering.py"), path
        for name in ("energy", "gis", "sumo"):
            assert manifest["sources"][f"{name}_summary_sha256"] == microgrid.source_hash(engineering / name / "summary.json"), path
        for record in manifest["screenshots"].values():
            assert record["sha256"] == microgrid.source_hash(engineering / "screenshots" / record["path"]), path
