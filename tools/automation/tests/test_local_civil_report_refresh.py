"""Evidence refresh must leave controlled design and cost changes for review."""
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location(
    "civil_report_refresh", ROOT / "tools/automation/refresh-local-civil-costs.py"
)
refresh = importlib.util.module_from_spec(spec)
spec.loader.exec_module(refresh)


def prepare(tmp_path, monkeypatch, *, multiplier=1.0):
    design = tmp_path / "design.toml"
    design.write_text('''[city]
slug = "example"
[costs]
total_usd = 100
[[lines]]
name = "line-1"
length_m = 20.0
[[civil_segments]]
line = "line-1"
class = "elevated"
from_station_m = 0.0
to_station_m = 20.0
elevated_cost_multiplier = 1.0
''')
    (tmp_path / "example.toml").write_text("# controlled scenario\n")
    def native(command, **kwargs):
        output = Path(command[command.index("--civil-register-out") + 1])
        output.write_text(json.dumps({"compiled_sources": {}, "segments": [{
            "line": "line-1", "class": "elevated", "from_station_m": 0.0,
            "to_station_m": 20.0, "elevated_cost_multiplier": multiplier,
        }]}))
    monkeypatch.setattr(refresh.subprocess, "run", native)
    return design


def test_report_refresh_refuses_changed_native_product_cost_without_writing(tmp_path, monkeypatch):
    design = prepare(tmp_path, monkeypatch, multiplier=1.5)
    original = design.read_bytes()
    with pytest.raises(ValueError, match="Native civil register differs"):
        refresh.refresh(design, report_only=True)
    assert design.read_bytes() == original
    assert not (tmp_path / "engineering/local-civil-costs/summary.json").exists()


def test_report_refresh_refuses_recalculated_budget_without_writing(tmp_path, monkeypatch):
    design = prepare(tmp_path, monkeypatch)
    original = design.read_bytes()
    def changed_budget(candidate):
        candidate.write_text(candidate.read_text().replace("total_usd = 100", "total_usd = 200"))
    monkeypatch.setattr(refresh.capex, "recalculate", changed_budget)
    with pytest.raises(ValueError, match="Civil budget changed"):
        refresh.refresh(design, report_only=True)
    assert design.read_bytes() == original
    assert not (tmp_path / "engineering/local-civil-costs/summary.json").exists()
