"""Keep complete selected-vehicle payloads stable across Python runtimes.

Available Python 3.11/3.12/3.13 executables are discovered on PATH. Additional
interpreters may be supplied through OSR_VEHICLE_REPRO_PYTHONS, separated by
os.pathsep; CI and local checks need no machine-specific path in this test.
"""
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tomllib

import pytest

from engineering.development_baseline import selection
from engineering.station_rail import ROOT
from engineering.station_rail.common import encoded, identity


def _interpreters():
    discovered = [sys.executable]
    discovered.extend(path for name in ("python3.11", "python3.12", "python3.13")
        if (path := shutil.which(name)) is not None)
    requested = os.environ.get("OSR_VEHICLE_REPRO_PYTHONS", "")
    for name in filter(None, requested.split(os.pathsep)):
        path = shutil.which(name) or str(Path(name).expanduser())
        if not Path(path).is_file() or not os.access(path, os.X_OK):
            raise ValueError("Requested vehicle-replay interpreter is unavailable: " + name)
        discovered.append(path)
    result = []
    seen = set()
    for path in discovered:
        resolved = Path(path).resolve()
        if resolved not in seen:
            seen.add(resolved)
            result.append(path)
    return result


@pytest.fixture(scope="module")
def selected_payload():
    selected = selection.load()
    return dict(vehicle=selected["vehicle"], selection_id=selected["selection_id"])


def test_vehicle_keeps_the_selected_definition_mass_and_acceptance_holds(selected_payload):
    config = tomllib.loads((ROOT/"engineering/development-baseline.toml").read_text())
    vehicle = selected_payload["vehicle"]
    assert vehicle["candidate_id"] == config["vehicle_candidate_id"]
    assert selected_payload["selection_id"] == identity(config)
    assert vehicle["mass"]["accounted_tare_kg_per_car"] == 19221.998134341986
    assert all(vehicle[key] is False for key in (
        "physical_accepted", "engineering_accepted", "installed_mass_complete",
        "manufacturing_release", "operating_release"))


@pytest.mark.parametrize("interpreter", _interpreters())
def test_entire_selected_vehicle_payload_matches_available_python_runtimes(interpreter, selected_payload):
    script = """
from engineering.development_baseline import selection
from engineering.station_rail.common import encoded
import sys
selected = selection.load()
sys.stdout.buffer.write(encoded(dict(vehicle=selected['vehicle'], selection_id=selected['selection_id'])))
"""
    actual = subprocess.run([interpreter, "-B", "-c", script], cwd=ROOT,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        capture_output=True, check=True, timeout=60).stdout
    assert actual == encoded(selected_payload), (
        "Complete vehicle/selection payload differs under " + interpreter)
