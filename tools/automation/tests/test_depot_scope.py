"""Depot scope reporting must expose quantities and unallocated physical work."""

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SPEC = importlib.util.spec_from_file_location("depot_scope", ROOT / "tools/automation/generate-depot-scope.py")
scope = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(scope)


def test_samawah_inventory_cost_sensitivity_and_dispatch_requirements():
    report = scope.build_report(ROOT / "cities/catalogue/west-asia/Iraq/Samawah/design.toml")
    assert report["quantities_reconciled"] is True
    assert report["overnight_stabling_policy"]["enabled"] is True
    assert report["overnight_stabling_policy"]["morning_start_policy"] == "simultaneous-from-stabled-stations"
    assert report["workshop_bays_are_fleet_parking"] is False
    assert report["passed"] is False
    assert report["deployment_release_ready"] is False
    assert len(report["depots"]) == 1  # shared passenger/depot site is counted once
    cost = report["depots"][0]["cost_reconciliation"]
    assert cost["additional_equipment_reference_usd"] == 4400 * 700 + 38000 * 75
    assert not cost["applied_to_city_capex"]
    assert not cost["included_in_existing_allowance_verified"]
    rows = report["initial_dispatch_requirements"]
    assert report["fleet_trainsets"] == 108
    assert sorted(r["initial_trainset_count"] for r in rows if r["line"] == "line-1") == [26, 27]
    largest = max(rows, key=lambda r: r["initial_trainset_count"])
    assert largest["train_body_length_m"] == 27 * 49.5
    assert largest["minimum_slot_length_with_clearance_m"] == 27 * (49.5 + 10)
    assert all(r["verified_stabling_slots"] is None for r in rows)


def test_dispatch_requirements_aggregate_duplicate_start_stations():
    design = {"lines": [{"name": "L", "rolling_stock": "test"}]}
    scenario = {"fleets": [{"line": "L", "trainset_count": 5, "dispatch_points": [{"station": "A"}, {"station": "B"}, {"station": "A"}]}]}
    rows = scope.stabling_requirements(design, scenario, {"test": {"length_m": 21}})
    assert {r["station"]: r["initial_trainset_count"] for r in rows} == {"A": 3, "B": 2}


def test_catalogue_depot_scope_is_current_and_does_not_claim_release():
    paths = sorted((ROOT / "cities/catalogue").glob("*/*/*/design.toml"))
    assert len(paths) == 266
    for path in paths:
        output = path.parent / "engineering/depot-scope/summary.json"
        report = json.loads(output.read_text())
        assert report == scope.build_report(path), path
        assert report["passed"] is False
        assert report["quantities_reconciled"] is True
        assert (output.parent / "README.md").read_text() == scope.render_markdown(report)
