"""The city project twin connects CPM, orders, cashflow and persisted actuals."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sqlite3
import sys

import pytest


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools/automation"))

from project_twin import apply_resource_cpm, build_project_twin, compact_summary  # noqa: E402


def _task(uid: str, *, predecessor: str = "") -> dict:
    return {
        "manufacturing_uid": uid,
        "asset_id": uid.split(":")[0],
        "asset_type": "rolling-stock",
        "package_id": uid.split(":")[-1],
        "work_center": "test cell",
        "duration_days": 2,
        "predecessor_uids": predecessor,
        "external_predecessors": "",
        "work_order_title": uid,
    }


def test_resource_cpm_assigns_lanes_and_calculates_float() -> None:
    rows = [_task("a:p"), _task("b:p"), _task("c:q", predecessor="a:p")]
    result = apply_resource_cpm(rows, {"test cell": 1})

    assert result["programme_working_days"] == 6
    assert [row["planned_start_day"] for row in rows] == [0, 2, 4]
    assert rows[1]["resource_predecessor_uid"] == "a:p"
    assert rows[2]["resource_predecessor_uid"] == "b:p"
    assert all(row["total_float_days"] == 0 for row in rows)
    assert all(row["is_critical"] for row in rows)


def test_twin_reconciles_capex_deduplicates_orders_and_is_deterministic(tmp_path: Path) -> None:
    design = tmp_path / "design.toml"
    scenario = tmp_path / "city.toml"
    finance = tmp_path / "summary.json"
    for path, value in ((design, "[city]\nslug='test'\n"), (scenario, "[scenario]\n"), (finance, "{}\n")):
        path.write_text(value, encoding="utf-8")
    tasks = [_task("TRAIN-1:kit")]
    materials = [
        {
            "manufacturing_uid": "TRAIN-1:kit",
            "asset_id": "TRAIN-1",
            "bom_source": "rolling_stock_bom",
            "bom_ref": "T1",
            "description": "traction motor",
            "quantity_basis": "4",
            "make_buy_source": "BID",
            "base_usd": "25000",
            "supplier_anchor_id": "ANCHOR-MOTOR",
            "supplier_name": "reference supplier",
            "supplier_family": "motor family",
            "cots_candidate_ids": "OSR-COTS-MOTOR-001",
            "cots_candidate_models": "reference supplier motor 001",
            "cots_selection_states": "rfq-baseline",
            "cots_register_status": "controlled-design-input-not-order",
        },
        {
            "manufacturing_uid": "TRAIN-1:kit",
            "asset_id": "TRAIN-1",
            "bom_source": "rolling_stock_bom",
            "bom_ref": "T1",
            "description": "traction motor",
            "quantity_basis": "4",
            "make_buy_source": "BID",
            "base_usd": "25000",
        },
    ]
    kwargs = {
        "meta": {"city_slug": "test"},
        "assets": [{"asset_id": "TRAIN-1"}],
        "manufacturing_tasks": tasks,
        "manufacturing_materials": materials,
        "finance": {
            "capex_usd": {
                "reconciled_project_total": 100_000.0,
                "procurement_origin_buckets": [
                    {"bucket": "rolling_stock", "total_usd": 100_000.0, "local_share": 0.6, "imported_share": 0.4}
                ],
            }
        },
        "source_paths": {"design": design, "scenario": scenario, "finance": finance},
        "resource_capacity": {"test cell": 1},
    }
    first = build_project_twin(**kwargs)
    second = build_project_twin(**kwargs)

    assert first["revision_id"] == second["revision_id"]
    assert len(first["purchase_orders"]) == 1
    assert first["purchase_orders"][0]["order_by_day"] == -150
    assert first["purchase_orders"][0]["cots_candidate_ids"] == "OSR-COTS-MOTOR-001"
    assert first["purchase_orders"][0]["status"] == "planned-not-issued"
    summary = compact_summary(first)
    assert summary["procurement"]["manufacturer_candidate_linked_rows"] == 1
    assert summary["procurement"]["manufacturer_candidate_ids"] == ["OSR-COTS-MOTOR-001"]
    assert sum(row["budget_usd"] for row in first["budget_contracts"]) == 100_000.0
    assert sum(row["planned_requirement_usd"] for row in first["cashflow"]["monthly_requirements"]) == 100_000.0
    assert len(first["visualization_timeline"]) == 2


def test_charging_budget_is_allocated_to_energy_work() -> None:
    energy = _task("ENERGY-1:install")
    energy["asset_type"] = "energy"
    twin = build_project_twin(
        meta={"city_slug": "test", "rolling_stock_family": "light-metro-3car"},
        assets=[{"asset_id": "ENERGY-1"}],
        manufacturing_tasks=[energy],
        manufacturing_materials=[],
        finance={
            "capex_usd": {
                "reconciled_project_total": 30_000.0,
                "procurement_origin_buckets": [
                    {"bucket": "solar_plant", "total_usd": 20_000.0, "local_share": 0.5, "imported_share": 0.5},
                    {"bucket": "charging_microgrid", "total_usd": 10_000.0, "local_share": 0.6, "imported_share": 0.4},
                ],
            }
        },
        source_paths={},
    )
    assert {row["bucket"] for row in twin["budget_contracts"]} == {"solar_plant", "charging_microgrid"}
    assert {row["asset_id"] for row in twin["budget_contracts"]} == {"ENERGY-1"}


def test_ops_core_round_trips_project_actuals(tmp_path: Path) -> None:
    spec = importlib.util.spec_from_file_location(
        "ops_core_server", ROOT / "tools/automation/ops-core-server.py"
    )
    assert spec and spec.loader
    server = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(server)
    db = tmp_path / "ops.sqlite3"
    with sqlite3.connect(db) as raw:
        raw.row_factory = sqlite3.Row
        server.init_db(raw)
        state = server.empty_state()
        state["purchaseOrders"] = [
            {"id": "PO-00001", "status": "draft-not-issued", "effective_at": "2026-01-01T00:00:00Z"}
        ]
        state["invoices"] = [{"id": "INV-00001", "status": "received"}]
        state["progressUpdates"] = [{"id": "PROG-00001", "status": "reported", "percent": 25}]
        server.save_state(raw, "test", state)
        restored = server.load_state(raw, "test")

    assert restored["purchaseOrders"][0]["id"] == "PO-00001"
    assert restored["invoices"][0]["id"] == "INV-00001"
    assert restored["progressUpdates"][0]["percent"] == 25


def test_ops_core_enforces_authenticated_segregation_and_attests_records(tmp_path: Path) -> None:
    spec = importlib.util.spec_from_file_location(
        "ops_core_server_secure", ROOT / "tools/automation/ops-core-server.py"
    )
    assert spec and spec.loader
    server = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(server)
    users = server.load_users(ROOT / "tests/fixtures/ops-users.json")
    assert server.verify_password(users["inspector"], "Inspector-pass-123!")
    db = tmp_path / "ops.sqlite3"
    signing_key = b"x" * 32
    planner = server.actor_from_user(users["planner"])
    inspector = server.actor_from_user(users["inspector"])
    approver = server.actor_from_user(users["approver"])
    with sqlite3.connect(db) as raw:
        raw.row_factory = sqlite3.Row
        server.init_db(raw)
        state = server.empty_state()
        state["workOrders"] = [{"id": "WO-00001", "status": "open", "title": "test"}]
        server.save_state(raw, "samawah", state, actor=planner, signing_key=signing_key)

        state = server.load_state(raw, "samawah")
        state["workOrders"][0]["status"] = "ready_to_close"
        state["inspections"] = [{
            "id": "INSP-00001", "wo_id": "WO-00001", "result": "pass", "recorded_at": "2026-01-01T00:00:00Z"
        }]
        state = server.save_state(raw, "samawah", state, actor=inspector, signing_key=signing_key)
        inspection = state["inspections"][0]
        assert inspection["signed_by_user_id"] == "inspector-test"
        assert server._verify_attestation(inspection, signing_key)

        state["approvals"] = [{
            "id": "APR-00001", "wo_id": "WO-00001", "inspection_id": "INSP-00001", "decision": "approved"
        }]
        dual_role_inspector = {**inspector, "roles": ["inspector", "approver"]}
        with pytest.raises(PermissionError, match="different authenticated users"):
            server.save_state(raw, "samawah", state, actor=dual_role_inspector, signing_key=signing_key)
        state = server.save_state(raw, "samawah", state, actor=approver, signing_key=signing_key)
        assert state["approvals"][0]["signed_by_user_id"] == "approver-test"
        state["workOrders"][0]["status"] = "closed"
        closed = server.save_state(raw, "samawah", state, actor=approver, signing_key=signing_key)
        assert closed["workOrders"][0]["status"] == "closed"

        tampered = server.load_state(raw, "samawah")
        tampered["inspections"][0]["result"] = "fail"
        with pytest.raises(PermissionError, match="cannot be changed"):
            server.save_state(raw, "samawah", tampered, actor=approver, signing_key=signing_key)


def test_ops_core_backup_contains_verified_sqlite_and_evidence(tmp_path: Path) -> None:
    spec = importlib.util.spec_from_file_location(
        "ops_core_backup", ROOT / "tools/automation/ops-core-backup.py"
    )
    assert spec and spec.loader
    backup = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(backup)
    database = tmp_path / "ops.sqlite3"
    with sqlite3.connect(database) as connection:
        connection.execute("CREATE TABLE evidence (id TEXT PRIMARY KEY)")
        connection.execute("INSERT INTO evidence VALUES ('EVID-1')")
    evidence = tmp_path / "evidence/samawah/00"
    evidence.mkdir(parents=True)
    (evidence / "photo.txt").write_text("inspection photo fixture\n")
    archive = tmp_path / "ops-backup.zip"

    backup.create_backup(database, tmp_path / "evidence", archive)
    backup.verify_backup(archive)

    assert archive.is_file()
