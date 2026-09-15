import copy
import importlib.util
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "deployment/erpnext/apps/osr_erpnext"))
from osr_erpnext.planning import make_plan, source_key, validate_plan


def bundle():
    return {"project_twin": {"city": "test", "revision_id": "twin-123"},
            "manufacturing_tasks": [{"manufacturing_uid": "test:a:build", "city": "test", "asset_id": "a"}],
            "maintenance_tasks": [{"task_uid": "test:a:daily", "city": "test", "cadence": "daily"}]}


def test_stable_keys_preserve_company_and_revision_boundaries():
    plan = make_plan(bundle())
    assert plan == make_plan(bundle())
    assert len(plan["records"]) == 2
    validate_plan(plan)
    key = source_key("Company A", plan, "maintenance", "test:a:daily")
    assert key != source_key("Company B", plan, "maintenance", "test:a:daily")
    assert key != source_key("Company A", dict(plan, revision="twin-456"), "maintenance", "test:a:daily")


def test_partial_plan_uses_same_full_bundle_fingerprint():
    full = make_plan(bundle())
    partial = make_plan(bundle(), ["maintenance"])
    assert len(partial["records"]) == 1
    assert full["source_sha256"] == partial["source_sha256"]


@pytest.mark.parametrize("fault", ["duplicate", "city", "identity", "kind", "hash"])
def test_reject_ambiguous_or_tampered_import(fault):
    plan = make_plan(bundle())
    if fault == "duplicate":
        plan["records"].append(copy.deepcopy(plan["records"][0]))
    elif fault == "city":
        plan["records"][0]["source"]["city"] = "another-city"
    elif fault == "identity":
        plan["records"][0]["uid"] = "different"
    elif fault == "kind":
        plan["records"][0]["kind"] = "Payment Entry"
    else:
        plan["source_sha256"] = "not-a-hash"
    with pytest.raises(ValueError):
        validate_plan(plan)


def test_source_changes_are_detectable():
    before = make_plan(bundle())
    changed = bundle()
    changed["maintenance_tasks"][0]["cadence"] = "weekly"
    assert make_plan(changed)["source_sha256"] != before["source_sha256"]


def test_business_records_read_only_but_railway_revisions_can_save(tmp_path):
    spec = importlib.util.spec_from_file_location("erp_ops_test", ROOT / "tools/automation/ops-core-server.py")
    ops = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ops)
    with ops.connect(tmp_path / "ops.sqlite3") as connection:
        ops.init_db(connection)
        for collection in ops.ERP_RECORD_KINDS:
            state = ops.empty_state()
            state[collection] = [{"id": "attempt", "status": "draft"}]
            with pytest.raises(ValueError, match="Use ERPNext"):
                ops.save_state(connection, "test", state)
            assert ops.load_state(connection, "test")["_revision"] == 0
        # Historic actuals can be read and preserved during a railway save.
        connection.execute("INSERT INTO project_records (city_slug, kind, id, position, status, effective_at, payload) VALUES (?, ?, ?, ?, ?, ?, ?)",
                           ("test", "purchase-order", "legacy", 0, "draft", "", '{"id":"legacy","status":"draft"}'))
        connection.commit()
        state = ops.load_state(connection, "test")
        saved = ops.save_state(connection, "test", state)
        assert saved["purchaseOrders"] == [{"id": "legacy", "status": "draft"}]
        assert saved["_revision"] == 1
