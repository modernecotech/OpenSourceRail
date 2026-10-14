"""Operation setup and actual worker-bounded paired-variable execution."""

import json
import subprocess

import pytest

from engineering.analysis.tests.test_design_engine import scope
from engineering.design_engine import runtime
from engineering.design_engine.registry import get
from engineering.design_engine import adapters


def test_native_confirmation_and_cad_have_separate_setup_requirements(monkeypatch):
    tools = dict(
        numpy="present",
        scipy="present",
        pymoo=None,
        calculix_sha256=None,
        openseespy=None,
    )
    monkeypatch.setattr(runtime, "toolchain", lambda adapter: tools)
    monkeypatch.setattr(runtime.shutil, "which", lambda name: None)
    panel = get("clipped-side-bay")
    assert runtime.preflight(panel)["available"]
    assert runtime.preflight(panel, operation="confirm")["missing"] == ["CalculiX"]
    assert runtime.preflight(panel, operation="optimise")["missing"] == ["pymoo"]
    assert runtime.preflight(panel, operation="cad-export")["missing"] == ["FreeCAD"]
    civil = get("civil-system-alternatives")
    assert runtime.preflight(civil)["available"]
    assert runtime.preflight(civil, operation="confirm")["missing"] == ["OpenSeesPy"]


def test_hung_cad_package_probe_reports_missing_setup(monkeypatch):
    monkeypatch.setattr(
        runtime.shutil,
        "which",
        lambda name: "/fake/flatpak" if name == "flatpak" else None,
    )

    def timeout(*args, **kwargs):
        raise subprocess.TimeoutExpired(args[0], kwargs["timeout"])

    monkeypatch.setattr(runtime.subprocess, "run", timeout)
    assert (
        "FreeCAD"
        in runtime.preflight(get("clipped-side-bay"), operation="cad-export")["missing"]
    )


def test_actual_worker_retains_all_factorial_corners_and_unknown_economics(tmp_path):
    manager = runtime.Manager(tmp_path)
    values = dict(support_span_m=1.0, grade_density=80, core_m=0.0246, skin_m=0.0015)
    req = runtime.request(
        "clipped-side-bay",
        scope(),
        [values],
        interactions=dict(
            factors=dict(support_span_m=[1.0, 0.5], core_m=[0.02, 0.0246]),
            evaluations=4,
        ),
        budget=dict(evaluations=16, wall_seconds=120),
    )
    job = manager.start(req)
    import time

    deadline = time.monotonic() + 150
    while time.monotonic() < deadline:
        job = manager.store.get(job["id"])
        if job["status"] in runtime.TERMINAL:
            break
        time.sleep(0.1)
    assert job["status"] == "completed", job
    folder = tmp_path / "runs" / job["id"] / "attempt-0001"
    manager.store.verify_attempt(job["id"], 1)
    report = json.loads((folder / "interaction-study/report.json").read_text())
    cases = [
        json.loads(p.read_text())
        for p in (folder / "interaction-study/cases").glob("*.json")
    ]
    assert len(cases) == 4
    assert all(row["evaluator_called"] for row in cases)
    assert len({tuple(sorted(row["scenario"]["values"].items())) for row in cases}) == 4
    assert all(
        row["metrics"]["installed_cost"] is None and row["metrics"]["carbon"] is None
        for row in cases
    )
    assert all(row["result"]["engineering_state"] != "passed" for row in cases)
    assert report["physical_release"] is False
    with manager.store.connect() as con:
        events = [
            json.loads(row[0])
            for row in con.execute(
                "SELECT payload FROM events WHERE job=?", (job["id"],)
            )
        ]
    assert (
        len([e for e in events if e.get("phase") == "paired-variable-interaction"]) == 4
    )


@pytest.mark.parametrize("levels", [[1.0, 1.0], [1.0, 1000]])
def test_interaction_variables_cannot_bypass_the_controlled_domain(levels):
    with pytest.raises(ValueError):
        runtime.request(
            "clipped-side-bay",
            scope(),
            interactions=dict(
                factors=dict(support_span_m=levels, core_m=[0.02, 0.0246]),
                evaluations=4,
            ),
        )


def test_native_passage_uses_the_remaining_campaign_budget_and_retains_failures(
    tmp_path,
):
    charter = get("full-train")
    candidate = adapters.compile_candidate(charter, scope(), {"family": "metro-6car"})
    adapters.refine(
        charter,
        candidate,
        lambda count, phase: None,
        tmp_path,
        remaining_seconds=lambda: 0.1,
    )
    cases = candidate["definition"]["coupled_cases"]
    assert len(cases) == 8
    executed = [row for row in cases.values() if "allocated_wall_seconds" in row]
    assert executed
    assert all(row["allocated_wall_seconds"] == 0.001 for row in executed)
    assert all(row["state"] == "budget-exceeded" for row in executed)
    assert all(row["full_passage_coverage"] is False for row in executed)
    assert candidate["checks"]["service"]["state"] == "failed"
    assert len(list(tmp_path.glob("*/input.json"))) == len(executed)
