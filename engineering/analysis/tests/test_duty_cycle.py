import copy
from pathlib import Path

import pytest

from engineering.analysis.duty_cycle import DutyCycleError, load, project, verify_projection


ROOT = Path(__file__).resolve().parents[3]
FIXTURE = ROOT / "engineering/toolchain/fixtures/planning-duty-cycle.json"


def test_solver_projections_preserve_identity_time_and_power() -> None:
    duty = load(FIXTURE)
    projections = project(duty)
    verify_projection(duty, projections)
    assert not projections["acceptance_eligible"]
    assert [row["time_s"] for row in projections["pybamm"]] == [
        row["time_s"] for row in projections["sumo"]
    ]
    for source, battery in zip(duty["samples"], projections["pybamm"]):
        expected = source["traction_kw"] + source["auxiliary_kw"] - source["charge_kw"]
        assert battery["battery_power_kw"] == expected


@pytest.mark.parametrize(
    "mutation",
    [
        lambda d: d.update(schema="unknown"),
        lambda d: d["units"].update(power="W"),
        lambda d: d["samples"][1].update(time_s=0.0),
        lambda d: d["samples"][1].update(traction_kw=float("nan")),
        lambda d: d["samples"][1].update(charge_kw=10.0),
        lambda d: d["samples"][1].update(extra=1),
    ],
)
def test_invalid_or_ambiguous_duty_fails_closed(mutation) -> None:
    duty = load(FIXTURE)
    broken = copy.deepcopy(duty)
    mutation(broken)
    with pytest.raises(DutyCycleError):
        project(broken)


def test_projection_drift_fails_closed() -> None:
    duty = load(FIXTURE)
    projections = project(duty)
    projections["pandapower"][0]["charger_demand_mw"] = 99.0
    with pytest.raises(DutyCycleError, match="drifted"):
        verify_projection(duty, projections)
