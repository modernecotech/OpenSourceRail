"""Required native acceptance follows the actual part dependency closure."""

import json
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[3]


@pytest.mark.parametrize(
    "changed",
    [
        "engineering/design_engine/generated_parts_native.py",
        "./engineering/design_engine/generated_parts.py",
        "engineering/design_engine/contracts.py",
        "design/component-catalogue/src/osr_mech/vehicle_mass_properties.py",
        "design/component-catalogue/schemas/shared-engineering-model.json",
        "engineering/analysis/tests/test_generated_parts_native.py",
        "tools/automation/local_validation.py",
        "tools/automation/check.py",
    ],
)
def test_native_pipeline_and_acceptance_dependencies_require_native_profile(changed):
    result = subprocess.run(
        [
            sys.executable,
            "tools/automation/check.py",
            "--scope",
            "impact",
            "--changed",
            changed,
            "--plan",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    plan = json.loads(result.stdout)
    assert "native-design" in plan["profiles"]
    assert plan["profiles"].count("python") == 1
    assert plan["execution_location"] == "local"


def test_unrelated_prose_does_not_require_native_execution():
    result = subprocess.run(
        [
            sys.executable,
            "tools/automation/check.py",
            "--scope",
            "impact",
            "--changed",
            "docs/commercial/supplier-technical-support-package.md",
            "--plan",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    assert json.loads(result.stdout)["profiles"] == ["quick"]
