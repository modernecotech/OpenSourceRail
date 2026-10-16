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


@pytest.mark.parametrize(
    "changed",
    [
        "engineering/factory_examples/native.py",
        "engineering/factory_examples/data/equipment.json",
        "engineering/factory_examples/examples/strongback-end/model.FCStd",
        "engineering/design_engine/factory.py",
        "engineering/design_engine/factory_acceptance.py",
        "engineering/design_engine/factory_restraint.py",
        "engineering/design_engine/factory_schedule.py",
        "engineering/design_engine/factory_stages.py",
        "engineering/design_engine/factory_frame.py",
        "engineering/design_engine/factory_beam.py",
        "docs/design-engine/factory-beam-demands/model.FCStd",
        "engineering/generative_design/civil.py",
        "tools/automation/generative-design-campaign.py",
        "docs/design-engine/generative-campaign/snapshot.json",
        "docs/design-engine/factory-whole-bed/model.FCStd",
        "docs/design-engine/factory-buildout/handover.json",
        "docs/design-engine/factory-stages/model.FCStd",
        "engineering/design_engine/data/factory-restraint.json",
        "tools/automation/publish-factory-review.py",
        "docs/design-engine/factory-support/model.FCStd",
        "tools/automation/local_validation.py",
        "engineering/analysis/tests/test_factory_reproduction.py",
    ],
)
def test_factory_sources_and_native_evidence_require_factory_acceptance(changed):
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
    assert "factory-native" in plan["profiles"]
    if (
        changed.startswith("engineering/factory_examples/")
        and "/examples/" not in changed
    ):
        assert "problem:factory-fixture" in plan["affected"]
        assert "problem:factory-precast" in plan["affected"]
