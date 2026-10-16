"""Campaign scheduling/provenance protocol fixtures; not native physics."""

from copy import deepcopy
import json

import pytest

from engineering.design_engine import vehicle_campaign as campaign
from engineering.design_engine.runtime import BudgetExceeded
from engineering.analysis.tests.test_design_vehicle_confirmation import (
    simple_model,
    motion,
    retained_fixture_case,
)


@pytest.fixture
def protocol(monkeypatch):
    from engineering.civil_exploration import spatial_demo

    monkeypatch.setattr(
        spatial_demo, "scenarios", lambda model: {"fixture-straight": motion()}
    )
    monkeypatch.setattr(
        campaign,
        "assembly_diagnostics",
        lambda data, mode_count: dict(
            equipment_mount_laws={},
            flexible_vehicle_parameters=dict(
                mode_count=mode_count, ei_nm2=3e8, damping_ratio=0.02
            ),
        ),
    )

    def retained(model, configuration, parameters, folder, timeout):
        # Plans must be on disk before any native execution could start.
        assert (folder.parent / "refinement-plan.json").is_file()
        return retained_fixture_case(folder, model, configuration, parameters)

    monkeypatch.setattr(campaign, "case", retained)
    return dict(model=simple_model())


def test_campaign_executes_every_declared_axis_with_shared_budget(protocol, tmp_path):
    charges = []
    report = campaign.run(
        protocol,
        tmp_path,
        lambda count, phase: charges.append((count, phase)),
        remaining_seconds=lambda: 102.0,
    )
    row = report["fixture-straight"]
    assert row["planned"] == row["executed"] == 5
    assert row["validated"] == 4 and row["state"] == "validated"
    assert sum(count for count, _ in charges) == 7
    assert [phase.rsplit("-", 1)[-1] for _, phase in charges[1:]] == [
        "baseline",
        "time",
        "deck",
        "rail",
        "modal",
    ]
    assert row["cases"]["baseline"]["allocated_wall_seconds"] == 18.4
    assert row["cases"]["modal"]["allocated_wall_seconds"] == 92.0
    baseline = json.loads(
        (tmp_path / "fixture-straight/baseline/input.json").read_text()
    )
    for axis in ("time", "deck", "rail"):
        inputs = json.loads(
            (tmp_path / "fixture-straight" / axis / "input.json").read_text()
        )
        assert inputs["model"] == baseline["model"]
        assert inputs["configuration"] == baseline["configuration"]
        assert (
            sum(v != baseline["parameters"][k] for k, v in inputs["parameters"].items())
            == 1
        )
    modal = json.loads((tmp_path / "fixture-straight/modal/input.json").read_text())
    expected = deepcopy(baseline)
    expected["configuration"]["flexible_vehicle"]["mode_count"] = 4
    assert modal == expected
    assert not row["physical_validation"]


def test_budget_exception_retains_plans_and_does_not_validate_unexecuted_cases(
    protocol, tmp_path
):
    spent = 0

    def charge(count, phase):
        nonlocal spent
        if spent + count > 3:
            raise BudgetExceeded("labelled evaluation budget")
        spent += count

    with pytest.raises(BudgetExceeded, match="evaluation budget"):
        campaign.run(protocol, tmp_path, charge)
    report = json.loads((tmp_path / "passage-progress.json").read_text())
    row = report["campaigns"]["fixture-straight"]
    assert row["planned"] == 5 and row["executed"] == 1 and row["validated"] == 0
    assert row["cases"]["time"]["state"] == "not-run"
    assert row["comparison"]["state"] == "unknown"
    assert not (tmp_path / "fixture-straight/time/input.json").exists()


def test_finalization_reserve_does_not_launch_new_cases(
    protocol, tmp_path, monkeypatch
):
    def unexpected(*args, **kwargs):
        raise AssertionError("No case may start in the finalization reserve")

    monkeypatch.setattr(campaign, "case", unexpected)
    report = campaign.run(
        protocol, tmp_path, lambda *args: None, remaining_seconds=lambda: 0.1
    )
    row = report["fixture-straight"]
    assert row["planned"] == 5 and row["executed"] == row["validated"] == 0
    assert row["comparison"]["state"] == "unknown"
    assert not list(tmp_path.glob("*/*/input.json"))
