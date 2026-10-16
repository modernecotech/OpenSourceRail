"""Factory candidates share common scope, jobs, budgets and inventories."""

from copy import deepcopy
from pathlib import Path

import pytest

from engineering.design_engine import adapters, factory, runtime
from engineering.design_engine.bom import review_bill
from engineering.design_engine.contracts import identity, SCHEMA
from engineering.design_engine.registry import get, dependencies


def scope():
    return identity(
        dict(
            schema=SCHEMA,
            city="baghdad",
            project="baghdad",
            environment="simulation",
            configuration_revision="test-1",
            baseline_sha256=None,
            run_id=None,
            asset_id=None,
            part_id=None,
        )
    )


def candidate(kind="factory-precast", **changes):
    charter = get(kind)
    values = {k: v["choices"][0] for k, v in charter["variables"].items()}
    row = adapters.compile_candidate(charter, scope(), {**values, **changes})
    return adapters.screen(charter, row, lambda *args: None, Path("."))


@pytest.mark.parametrize("kind", sorted(factory.ADAPTERS))
def test_factory_problem_provenance_and_common_bom(kind):
    row = candidate(kind)
    bill = review_bill(row, adapter=kind)
    assert bill["physical_instance_count"] in (32, 63)
    assert bill["defined_mass_kg"] is None  # purchased/envelope masses remain unknown
    assert row["metrics"]["represented_steel_mass_kg"] > 0
    assert any(p["defined_mass_kg"] is None for p in bill["parts"])
    assert bill["complete_installed_kit"] is False
    sources = dependencies(kind)
    for name in (
        "models.py",
        "development.py",
        "connections.py",
        "native.py",
        "reproduction.py",
        "data/equipment.json",
        "data/production.json",
    ):
        assert "engineering/factory_examples/" + name in sources
    for check in (
        "physical_correlation",
        "independent_acceptance",
        "foundation_connections",
        "local_resistance",
    ):
        assert row["checks"][check]["state"] == "unknown"


def test_both_buckling_planes_are_independent():
    lateral = candidate(lateral_spring_n_m=0)
    vertical = candidate(vertical_spring_n_m=0)
    assert lateral["checks"]["lateral_stability"]["state"] == "failed"
    assert lateral["checks"]["vertical_stability"]["state"] == "passed"
    assert vertical["checks"]["vertical_stability"]["state"] == "failed"
    assert vertical["checks"]["lateral_stability"]["state"] == "passed"


def test_prestress_changes_handling_and_bed_force_without_closing_railway_checks():
    low, balanced = candidate(prestress_id="low-40"), candidate()
    assert low["checks"]["dead_load_prestress"]["state"] == "failed"
    assert (
        low["metrics"]["initial_bed_force_n"]
        < balanced["metrics"]["initial_bed_force_n"]
    )
    assert (
        low["metrics"]["beam_mass_lower_bound_kg"]
        < balanced["metrics"]["beam_mass_lower_bound_kg"]
    )
    assert balanced["metrics"]["handling_equivalent_lower_bound_kg"] == pytest.approx(
        104687.71875
    )
    assert balanced["checks"]["handling_lower_bound"]["state"] == "unknown"
    small = candidate(rated_lift_kg=100000)
    assert small["checks"]["handling_lower_bound"]["state"] == "failed"
    assert (
        small["definition"]["runway"]["near_wheel_n"]
        < balanced["definition"]["runway"]["near_wheel_n"]
    )


def test_more_beds_do_not_invent_other_resource_capacity():
    pilot, larger = candidate(), candidate(casting_positions=134)
    assert pilot["checks"]["production_flow"]["state"] == "failed"
    assert larger["checks"]["production_flow"]["state"] == "unknown"
    assert (
        larger["definition"]["production"]["all_resource_upper_bound_per_day"] is None
    )
    assert larger["installed_cost"] is None
    assert len(larger["definition"]["production"]["unresolved_resources"]) == 8


def test_known_resource_bottleneck_and_missing_resource_rejection():
    a, _, _, _, prod = factory.inputs()
    prod["resources"][0].update(units=2, working_days_per_attempt=0.5, availability=0.8)
    report = factory.production(a, 134, prod)
    assert report["known_resource_upper_bound_per_day"] == pytest.approx(3.04)
    assert report["resources"][1]["units_required_at_programme"] == 36
    assert report["demonstrated_accepted_output_per_day"] is None
    prod["resources"].pop()
    with pytest.raises(ValueError, match="complete unique"):
        factory.production(a, 134, prod)


def test_payload_preload_candidates_and_exhausted_native_budget(tmp_path, monkeypatch):
    row = candidate("factory-fixture", payload_kg=250, clamp_preload_n=250)
    assert row["metrics"]["payload_demand_n"] == pytest.approx(250 * 9.80665 * 1.5)
    monkeypatch.setattr(
        factory.subprocess,
        "Popen",
        lambda *a, **k: pytest.fail("exhausted budget launched native process"),
    )
    with pytest.raises(runtime.BudgetExceeded):
        factory.confirm(row, lambda *args: None, tmp_path, lambda: 0)


def test_common_job_rejects_undeclared_domain_and_physical_scope():
    with pytest.raises(ValueError):
        runtime.request("factory-precast", {**scope(), "environment": "physical"})
    charter = get("factory-fixture")
    values = {k: v["choices"][0] for k, v in charter["variables"].items()}
    with pytest.raises(ValueError):
        adapters.compile_candidate(charter, scope(), {**values, "payload_kg": 1e9})


def test_missing_factory_tool_is_an_unavailable_confirmation(monkeypatch):
    original = runtime.toolchain
    monkeypatch.setattr(
        runtime,
        "toolchain",
        lambda adapter: {
            **original(adapter),
            "factory_native": {"available": False, "missing": ["FreeCAD"]},
        },
    )
    result = runtime.preflight(get("factory-precast"), operation="confirm")
    assert result["available"] is False and "FreeCAD" in result["missing"]
