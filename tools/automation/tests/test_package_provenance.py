"""Retained solver passes must be bound to the inputs used for a package."""

import importlib.util
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
SPEC = importlib.util.spec_from_file_location(
    "package_manifest", REPO_ROOT / "tools/automation/generate-city-package-manifest.py"
)
manifest = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(manifest)


def test_changed_scenario_invalidates_passing_simulation_evidence(tmp_path):
    design, scenario = tmp_path / "design.toml", tmp_path / "test.toml"
    design.write_text("design input")
    scenario.write_text("original scenario")
    output = tmp_path / "engineering/simulation/validation-summary.json"
    output.parent.mkdir(parents=True)
    report = {
        "passed": True,
        "design_sha256": manifest.sha256(design),
        "scenario_sha256": manifest.sha256(scenario),
        "generator_sha256": manifest.sha256(REPO_ROOT / "tools/automation/validate-city-simulation.py"),
    }
    output.write_text(json.dumps(report))
    assert manifest.stale_analysis_sources(tmp_path, "test") == []

    scenario.write_text("changed charger capacity")
    findings = manifest.stale_analysis_sources(tmp_path, "test")
    assert len(findings) == 1
    assert findings[0]["source"] == "scenario_sha256"
    assert findings[0]["recorded_sha256"] == report["scenario_sha256"]
    assert findings[0]["expected_sha256"] == manifest.sha256(scenario)


def test_missing_provenance_is_not_accepted(tmp_path):
    output = tmp_path / "engineering/simulation/validation-summary.json"
    output.parent.mkdir(parents=True)
    output.write_text('{"passed": true}')
    findings = manifest.stale_analysis_sources(tmp_path, "test")
    assert {row["source"] for row in findings} == {"design_sha256", "scenario_sha256", "generator_sha256"}
