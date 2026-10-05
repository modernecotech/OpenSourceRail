"""Depot scope reporting must expose quantities and unallocated physical work."""

import importlib.util
import json
import math
import tomllib
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
    design=tomllib.loads((ROOT / "cities/catalogue/west-asia/Iraq/Samawah/design.toml").read_text())
    assert len(report["depots"]) == len(design["lines"])
    for depot in report["depots"]:
        cost=depot["cost_reconciliation"]
        assert cost["additional_equipment_reference_usd"] == 4400 * 700 + 38000 * 75
        assert cost["applied_to_city_capex"] and cost["full_depot_equipment_priced_in_depot_capital"]
        assert not cost["included_in_existing_allowance_verified"]
    rows = report["initial_dispatch_requirements"]
    assert report["fleet_trainsets"] == sum(f['trainset_count'] for f in design['fleets'])
    for row in rows:
        assert row['train_body_length_m']==row['initial_trainset_count']*49.5
        assert row['minimum_slot_length_with_clearance_m']==row['initial_trainset_count']*59.5
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
        assert publication_without_context((output.parent / "README.md").read_text()) == scope.render_markdown(report)


def publication_without_context(text):
    import re
    return re.sub(r'<!-- OSR CURRENT SCOPE CONTEXT -->.*?<!-- END OSR CURRENT SCOPE CONTEXT -->\n\n?', '', text, flags=re.S)
