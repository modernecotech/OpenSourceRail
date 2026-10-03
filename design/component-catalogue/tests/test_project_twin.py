"""The city project twin connects CPM, orders, cashflow and persisted actuals."""

from __future__ import annotations

import importlib.util
import json
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


def test_ops_core_rejects_business_writes_and_preserves_historic_actuals(tmp_path: Path) -> None:
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
        with pytest.raises(ValueError, match="Use ERPNext"):
            server.save_state(raw, "test", state)
        assert server.load_state(raw, "test")["_revision"] == 0

        # Pre-migration business history remains readable and survives later
        # railway-evidence writes, but OSR cannot mutate it.
        historic = {
            "purchase-order": state["purchaseOrders"][0],
            "invoice": state["invoices"][0],
            "progress-update": state["progressUpdates"][0],
        }
        raw.executemany(
            "INSERT INTO project_records "
            "(city_slug, kind, id, position, status, effective_at, payload) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            [
                (
                    "test",
                    kind,
                    row["id"],
                    0,
                    row["status"],
                    row.get("effective_at", ""),
                    json.dumps(row),
                )
                for kind, row in historic.items()
            ],
        )
        raw.commit()
        railway_state = server.load_state(raw, "test")
        railway_state["projectRevisions"] = [{"id": "REV-00001", "status": "reviewed"}]
        server.save_state(raw, "test", railway_state)
        restored = server.load_state(raw, "test")

    assert restored["purchaseOrders"][0]["id"] == "PO-00001"
    assert restored["invoices"][0]["id"] == "INV-00001"
    assert restored["progressUpdates"][0]["percent"] == 25
    assert restored["projectRevisions"] == [{"id": "REV-00001", "status": "reviewed"}]


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


def test_resource_cpm_pipelines_ready_train_stages_and_respects_plant_availability() -> None:
    rows = []
    for asset in ('A', 'B', 'C'):
        kit = _task(f'{asset}:kit')
        body = _task(f'{asset}:body', predecessor=f'{asset}:kit')
        kit['sequence'], body['sequence'] = 10, 20
        rows.extend((kit, body))
    result = apply_resource_cpm(rows, {'test cell': 1}, {'test cell': 5})
    by_uid = {row['manufacturing_uid']: row for row in rows}
    assert by_uid['A:kit']['planned_start_day'] == 5
    assert by_uid['A:body']['planned_finish_day'] < by_uid['B:kit']['planned_start_day']
    assert result['programme_working_days'] == 17
    ordered = sorted(rows, key=lambda row: row['planned_start_day'])
    assert all(a['planned_finish_day'] < b['planned_start_day'] for a, b in zip(ordered, ordered[1:]))
    rerun = [dict(row) for row in reversed(rows)]
    apply_resource_cpm(rerun, {'test cell': 1}, {'test cell': 5})
    assert {row['manufacturing_uid']: row['planned_start_day'] for row in rerun} == {uid: row['planned_start_day'] for uid, row in by_uid.items()}


def test_resource_cpm_rejects_cycles_before_dispatch() -> None:
    with pytest.raises(ValueError, match='cycle'):
        apply_resource_cpm([_task('a:kit', predecessor='b:kit'), _task('b:kit', predecessor='a:kit')])


def test_epc_overhead_follows_direct_works_instead_of_baseline_freeze() -> None:
    from project_twin import build_budget_contracts
    freeze, early, late = _task('SYS:freeze'), _task('TRAIN-1:kit'), _task('TRAIN-2:kit')
    freeze['asset_type'] = 'system'
    freeze['phase'] = 'program-control'
    for task, start in ((freeze, 0), (early, 10), (late, 500)):
        task['planned_start_day'] = start
        task['planned_finish_day'] = start+1
    contracts = build_budget_contracts([freeze, early, late], {'buckets': [
        {'bucket': 'rolling_stock', 'total_usd': 100, 'local_share': .6, 'imported_share': .4},
        {'bucket': 'epc_overhead', 'total_usd': 7, 'local_share': .85, 'imported_share': .15}]})
    epc = [row for row in contracts if row['bucket'] == 'epc_overhead']
    assert sum(row['budget_usd'] for row in epc) == 7
    assert {row['planned_start_day'] for row in epc} == {10, 500}
    assert all(row['asset_id'] != 'SYS' for row in epc)
    assert sum(row['budget_usd'] for row in contracts) == 107
    assert early['budget_bucket'] == late['budget_bucket'] == 'rolling_stock'
    assert sum(task['epc_overhead_usd'] for task in (freeze, early, late)) == 7
