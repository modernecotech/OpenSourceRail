"""Simulation cache reuses only identical executed inputs and intact outputs."""
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location("cached_city_validation", ROOT / "tools/automation/validate-city-simulation.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_cache_binds_binary_scenario_duration_and_output(tmp_path, monkeypatch):
    monkeypatch.setattr(module, "REPO_ROOT", tmp_path)
    monkeypatch.setenv("OSR_SIM_CACHE", "1")
    binary = tmp_path / "target/release/osr-sim"
    binary.parent.mkdir(parents=True)
    binary.write_text("binary v1")
    scenario = tmp_path / "city.toml"
    scenario.write_text("configuration v1")
    output = tmp_path / "result.json"
    calls = []

    def execute(command, **kwargs):
        calls.append(command)
        Path(command[command.index("--json-out")+1]).write_text(json.dumps({"run": len(calls)}))

    monkeypatch.setattr(module.subprocess, "run", execute)
    first = module.run_sim(scenario, 100, output)
    assert len(calls) == 1 and not first["execution_receipt"]["cache_reused"]
    second = module.run_sim(scenario, 100, output)
    assert len(calls) == 1 and second["execution_receipt"]["cache_reused"]
    cache_file = tmp_path / ".cache/osr-pipeline/native-runs" / (second["execution_receipt"]["cache_key"]+".json")
    cache_file.write_text('{"run": 999}')
    module.run_sim(scenario, 100, output)
    assert len(calls) == 2
    scenario.write_text("configuration v2")
    module.run_sim(scenario, 100, output)
    assert len(calls) == 3
    binary.write_text("binary v2")
    module.run_sim(scenario, 100, output)
    assert len(calls) == 4
    module.run_sim(scenario, 200, output)
    assert len(calls) == 5
    monkeypatch.setenv("OSR_SIM_CACHE", "0")
    module.run_sim(scenario, 200, output)
    assert len(calls) == 6
