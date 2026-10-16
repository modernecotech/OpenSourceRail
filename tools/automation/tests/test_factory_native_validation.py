"""Factory native acceptance is mandatory and retains all execution evidence."""

import importlib.util
from copy import deepcopy
from pathlib import Path

import pytest

from engineering.design_engine import factory_acceptance as fa
from engineering.design_engine.registry import get

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location(
    "factory_profile_validation", ROOT / "tools/automation/local_validation.py"
)
local = importlib.util.module_from_spec(spec)
spec.loader.exec_module(local)


def test_factory_profile_runs_actual_native_and_common_jobs(tmp_path):
    rows = local.plan("factory-native", tmp_path)
    assert len(rows) == 3
    for row, action in zip(rows, ("prerequisites", "run", "verify")):
        assert "engineering.design_engine.factory_acceptance" in row["argv"]
        assert action in row["argv"]
        assert "--output" in row["argv"]
    assert rows[1]["timeout_seconds"] == 900
    assert local.RELEASE_PROFILES == {"ci", "kani", "integrated-stack", "example-city"}


def test_missing_factory_tool_fails_and_retains_prerequisite_record(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(
        fa.factory, "toolchain", lambda: {"available": False, "missing": ["FreeCAD"]}
    )
    with pytest.raises(
        ValueError, match="Required factory native prerequisites unavailable"
    ):
        fa.prerequisites(tmp_path)
    assert "FreeCAD" in (tmp_path / "prerequisites.json").read_text()


def test_missing_factory_acceptance_cannot_produce_successful_artifact_set(tmp_path):
    (tmp_path / "factory-native").mkdir()
    with pytest.raises((ValueError, OSError)):
        local.artifact_hashes("factory-native", tmp_path)


@pytest.mark.parametrize("adapter", sorted(fa.factory.ADAPTERS))
def test_acceptance_budget_does_not_change_the_fixed_function(adapter):
    charter = get(adapter)
    charter["budget"] = deepcopy(fa.ACCEPTANCE_BUDGET)
    fa.validate_problem(adapter, charter)
    changed = deepcopy(charter)
    changed["applicability"]["function"] += " changed"
    with pytest.raises(ValueError, match="function or acceptance budget"):
        fa.validate_problem(adapter, changed)
    changed = deepcopy(charter)
    changed["budget"]["evaluations"] = 1
    with pytest.raises(ValueError, match="function or acceptance budget"):
        fa.validate_problem(adapter, changed)
