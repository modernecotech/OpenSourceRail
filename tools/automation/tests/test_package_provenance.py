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


def test_historical_failures_and_staleness_do_not_block_selected_hybrid(tmp_path, monkeypatch):
    import sys
    (tmp_path / 'design.toml').write_text('[city]\nslug = "audit"\n')
    folder = tmp_path / 'engineering/stabling'
    folder.mkdir(parents=True)
    for name in (*manifest.STABLING_DIAGNOSTICS, 'hybrid-cycle-screen'):
        (folder / f'{name}.json').write_text('{"passed": false}')
        (folder / f'{name}.md').write_text('# Test evidence\n')
    monkeypatch.setattr(sys, 'argv', ['manifest', '--city-dir', str(tmp_path)])
    manifest.main()
    result = json.loads((tmp_path / 'package-manifest.json').read_text())
    assert 'engineering/stabling/hybrid-cycle-screen.json' in result['failed_summaries']
    assert any(r['artifact'].endswith('hybrid-cycle-screen.json') for r in result['stale_analysis_sources'])
    for name in manifest.STABLING_DIAGNOSTICS:
        relative = f'engineering/stabling/{name}.json'
        assert relative not in result['failed_summaries']
        assert all(r['artifact'] != relative for r in result['stale_analysis_sources'])
        assert result['diagnostic_artifacts'][relative]['passed'] is False
        assert result['diagnostic_artifacts'][relative]['sha256'] == manifest.sha256(folder / f'{name}.json')
        assert any(r['artifact'] == relative for r in result['diagnostic_stale_sources'])
