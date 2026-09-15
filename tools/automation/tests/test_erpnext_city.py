import copy
import importlib.util
import json
from pathlib import Path
import sys
import tomllib
import types

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "deployment/erpnext/apps/osr_erpnext"))
from osr_erpnext.city_config import make_city_plan, merge_config, validate_config, validate_city_plan, working_date
from osr_erpnext.planning import digest, source_key


def config():
    base = tomllib.loads((ROOT / "deployment/erpnext/config/generic.toml").read_text())
    return merge_config(base, {"city": {"slug": "test", "name": "Test", "country_code": "IQ"}})


def bundle():
    return {"project_twin": {"city": "test", "revision_id": "twin-123", "purchase_orders": []},
        "manufacturing_tasks": [
            dict(manufacturing_uid="test:build", city="test", planned_start_day=0, planned_finish_day=2, schedule_predecessor_uids=""),
            dict(manufacturing_uid="test:fit", city="test", planned_start_day=3, planned_finish_day=5, schedule_predecessor_uids="test:build"),
        ], "maintenance_tasks": [dict(task_uid="test:daily", city="test", asset_type="station")],
        "qa_actions": [dict(qa_uid="test:qa", city="test", stage="Review")], "totals": {"assets": 2}}


def test_shared_tables_merge_but_city_lists_replace_without_mutating_defaults():
    base = config()
    updated = merge_config(base, {"calendar": {"working_weekdays": [0, 2, 4]}})
    assert updated["calendar"]["working_weekdays"] == [0, 2, 4]
    assert base["calendar"]["working_weekdays"] == [0, 1, 2, 3, 4, 5]
    with pytest.raises(ValueError, match="Unknown configuration key"):
        merge_config(base, {"calender": {}})


def test_working_calendar_handles_holidays_negative_offsets_and_weekend_anchor():
    calendar = dict(start_date="2026-09-19", working_weekdays=[0, 1, 2, 3, 4], holidays=["2026-09-22"])
    assert working_date(calendar, 0) == "2026-09-21"
    assert working_date(calendar, -1) == "2026-09-18"
    assert working_date(calendar, 1) == "2026-09-23"


def test_deterministic_city_packages_enrich_native_work_and_keep_legacy_keys():
    c = config()
    p = make_city_plan(bundle(), c)
    assert p == make_city_plan(bundle(), c)
    validate_city_plan(p)
    second = next(r for r in p["records"] if r["uid"] == "test:fit")
    assert second["depends_on"] == ["manufacturing:test:build"]
    assert second["start_date"] is None
    maintenance = next(r for r in p["records"] if r["kind"] == "maintenance")
    assert maintenance["department"] == "Infrastructure Maintenance"
    assert source_key("A", p, "manufacturing", "test:fit") == source_key("A", {"city": "test", "revision": "twin-123"}, "manufacturing", "test:fit")
    assert source_key("A", dict(p, release="2"), "manufacturing", "test:fit") != source_key("A", p, "manufacturing", "test:fit")


@pytest.mark.parametrize("fault", ["cycle", "missing", "city", "weekday", "department"])
def test_reject_unreproducible_or_ambiguous_inputs(fault):
    c, b = config(), bundle()
    if fault == "cycle":
        b["manufacturing_tasks"][0]["schedule_predecessor_uids"] = "test:fit"
    elif fault == "missing":
        b["manufacturing_tasks"][0]["schedule_predecessor_uids"] = "test:missing"
    elif fault == "city":
        c["city"]["slug"] = "another"
    elif fault == "weekday":
        c["calendar"]["working_weekdays"] = []
    else:
        c["departments"]["manufacturing"] = "Unknown"
    with pytest.raises(ValueError):
        make_city_plan(b, c)


def test_dates_and_package_checksums_are_validated_at_import_boundary():
    c = config()
    c["calendar"]["start_date"] = "2026-09-21"
    plan = make_city_plan(bundle(), c)
    plan["records"][0]["start_date"] = "2027-01-01"
    with pytest.raises(ValueError, match="checksum"):
        validate_city_plan(plan)
    plan["package_sha256"] = digest({k: v for k, v in plan.items() if k != "package_sha256"})
    with pytest.raises(ValueError, match="dates"):
        validate_city_plan(plan)


def test_each_catalogue_city_has_a_valid_specific_profile():
    spec = importlib.util.spec_from_file_location("erp_city_cli", ROOT / "tools/automation/erpnext-city.py")
    cli = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cli)
    cities = cli.catalogue()
    assert len(cities) >= 266
    for slug in cities:
        validate_config(cli.effective_config(slug))


def test_large_procurement_tables_do_not_enter_rich_text_sanitizer(monkeypatch):
    fake_frappe = types.SimpleNamespace(whitelist=lambda **kwargs: lambda fn: fn)
    monkeypatch.setitem(sys.modules, "frappe", fake_frappe)
    spec = importlib.util.spec_from_file_location("city_import_description", ROOT / "deployment/erpnext/apps/osr_erpnext/osr_erpnext/api.py")
    api = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(api)
    row = dict(kind="procurement", source={"requirements": [{"description": "source detail"}] * 20000})
    description = api.task_description(row, "Review sourcing package")
    assert "20000 procurement requirements" in description
    assert len(description) < 1000
    assert "source detail" not in description
    assert len(row["source"]["requirements"]) == 20000
