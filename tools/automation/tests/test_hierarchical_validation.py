"""Impact selection requires fresh hierarchy jobs and sealed adoption evidence."""

import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools/automation"))
from local_validation import artifact_hashes, plan

import pytest


def test_profile_requires_both_actual_execution_and_verification(tmp_path):
    commands = plan("hierarchical-design", tmp_path)
    assert len(commands) == 2
    assert "run" in commands[0]["argv"]
    assert "verify" in commands[1]["argv"]
    with pytest.raises(FileNotFoundError):
        artifact_hashes("hierarchical-design", tmp_path)


@pytest.mark.parametrize(
    "path",
    [
        "engineering/generative_design/agent_execution.py",
        "engineering/generative_design/hierarchical_controller.py",
        "tools/automation/hierarchical-design.py",
        "tools/automation/fixtures/section-independent-acceptance.py",
        "engineering/analysis/tests/test_hierarchical_experiments.py",
    ],
)
def test_impact_requires_hierarchy_acceptance(path):
    r = subprocess.run(
        [
            sys.executable,
            "tools/automation/check.py",
            "--scope",
            "impact",
            "--changed",
            path,
            "--plan",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert "hierarchical-design" in json.loads(r.stdout)["profiles"]
