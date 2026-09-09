from __future__ import annotations

import json
from pathlib import Path
import runpy


ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "tools/automation/validate-owner-builder-operator-mobilisation.py"


def test_blank_mobilisation_baseline_is_complete_and_fail_closed() -> None:
    module = runpy.run_path(str(SCRIPT))
    status = module["build_status"]()
    assert status["summary"] == {
        "roles_ready": 0,
        "roles_total": 13,
        "independent_parties_ready": 0,
        "independent_parties_total": 3,
        "gates_accepted": 0,
        "gates_total": 8,
        "work_packages_complete": 0,
        "work_packages_total": 18,
        "default_programme_start_month": 0,
        "default_programme_end_month": 60,
        "mobilisation_ready": False,
    }
    assert all(status["validation"].values())
    assert {row["id"] for row in status["gates"]} == {f"G{number}" for number in range(8)}
    assert {row["id"] for row in status["work_packages"]} == {
        f"MOB-{number:03d}" for number in range(10, 181, 10)
    }
    assert all(row["status"] == "not-started" and not row["complete"] for row in status["work_packages"])


def test_tracked_mobilisation_outputs_match_source() -> None:
    module = runpy.run_path(str(SCRIPT))
    status = module["build_status"]()
    assert json.loads((ROOT / "docs/owner-builder-operator-mobilisation-status.json").read_text()) == status
    assert (ROOT / "docs/owner-builder-operator-mobilisation-status.md").read_text() == module["render_status"](status)
