"""Factory native acceptance is mandatory and retains all execution evidence."""

import importlib.util
from copy import deepcopy
from pathlib import Path
import subprocess
import sys

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
    assert len(rows) == 5
    for row, action in zip(rows[:3], ("prerequisites", "run", "verify")):
        assert "engineering.design_engine.factory_acceptance" in row["argv"]
        assert action in row["argv"]
        assert "--output" in row["argv"]
    assert rows[1]["timeout_seconds"] == 900
    for row, action in zip(rows[3:], ("run", "verify")):
        assert "engineering.generative_design.native_acceptance" in row["argv"]
        assert action in row["argv"]
        assert str(tmp_path / "factory-native/architecture") in row["argv"]
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


def test_old_factory_models_cannot_replace_required_architecture_evidence(
    tmp_path, monkeypatch
):
    from engineering.generative_design import native_acceptance as architecture

    native = tmp_path / "factory-native"
    native.mkdir()
    expected = dict(passed=True, physical_release=False)
    (native / "acceptance.json").write_text(local.encode(expected))
    monkeypatch.setattr(fa, "acceptance", lambda folder: expected)

    def missing(folder):
        assert folder == native / "architecture"
        raise ValueError("required architecture evidence missing")

    monkeypatch.setattr(architecture, "verify", missing)
    with pytest.raises(ValueError, match="required architecture evidence missing"):
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


def test_artifact_collector_imports_from_the_isolated_cli_path(tmp_path):
    (tmp_path / "factory-native").mkdir()
    script = (
        "import sys\nfrom pathlib import Path\n"
        + "sys.path.insert(0,"
        + repr(str(ROOT / "tools/automation"))
        + ")\n"
        + "from local_validation import artifact_hashes\n"
        + "try:\n artifact_hashes('factory-native',Path("
        + repr(str(tmp_path))
        + "))\n"
        + "except FileNotFoundError:\n print('acceptance collector import succeeded; evidence correctly missing')\n"
    )
    result = subprocess.run(
        [sys.executable, "-I", "-c", script],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=True,
    )
    assert "collector import succeeded" in result.stdout
