from __future__ import annotations

import copy
import http.client
import importlib.util
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import subprocess
import sys
import threading

import pytest


ROOT = Path(__file__).resolve().parents[3]
SPEC = importlib.util.spec_from_file_location("review_ops", ROOT / "tools/automation/ops-core-server.py")
OPS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(OPS)
KEY = b"test-attestation-key-32-bytes-long"


def actor(role):
    return {"user_id": role, "display_name": role, "roles": [role], "city_scopes": ["test"]}


def test_private_backups_and_symlinks_are_not_served(tmp_path, monkeypatch):
    monkeypatch.setattr(OPS, "REPO_ROOT", tmp_path)
    for name in ("backups/ops-core.zip", "var/ops.sqlite3", "docs/operations-portal/app.js"):
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("synthetic fixture")
    (tmp_path / "docs/leaked.sqlite3").symlink_to(tmp_path / "var/ops.sqlite3")

    class Handler(OPS.OpsCoreHandler):
        user_store = {"configured": {}}
        private_paths = (tmp_path / "var/ops.sqlite3",)

        def log_message(self, *args):
            pass

    server = OPS.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        for method in ("GET", "HEAD"):
            for path in ("/backups/ops-core.zip", "/var/ops.sqlite3", "/docs/leaked.sqlite3", "/docs/"):
                client = http.client.HTTPConnection("127.0.0.1", server.server_port)
                client.request(method, path)
                response = client.getresponse()
                assert response.status == 404, (method, path)
                response.read()
                client.close()
        client = http.client.HTTPConnection("127.0.0.1", server.server_port)
        client.request("GET", "/docs/operations-portal/app.js")
        response = client.getresponse()
        assert response.status == 200
        assert response.read() == b"synthetic fixture"
        client.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


def test_workbench_rejects_network_bind_before_creating_files(tmp_path):
    db = tmp_path / "must-not-exist.sqlite3"
    result = subprocess.run(
        [sys.executable, str(ROOT / "tools/automation/workbench-server.py"),
         "--host", "0.0.0.0", "--db", str(db)],
        capture_output=True, text=True,
    )
    assert result.returncode == 2
    assert "loopback-only" in result.stderr
    assert not db.exists()


def test_http_stale_save_returns_conflict_and_preserves_first_write(tmp_path):
    class Handler(OPS.OpsCoreHandler):
        database_path = tmp_path / "ops.sqlite3"
        attestation_key = KEY

        def log_message(self, *args):
            pass

    server = OPS.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        def request(method, body=None):
            client = http.client.HTTPConnection("127.0.0.1", server.server_port)
            client.request(method, "/api/ops-core/test", json.dumps(body) if body is not None else None,
                           {"Content-Type": "application/json"})
            response = client.getresponse()
            status, payload = response.status, json.loads(response.read())
            client.close()
            return status, payload

        status, response = request("GET")
        assert status == 200
        state = response["state"]
        state["workOrders"] = [{"id": "WO-A", "status": "open"}]
        assert request("PUT", state)[0] == 200
        state["workOrders"] = [{"id": "WO-B", "status": "open"}]
        assert request("PUT", state)[0] == 409
        assert request("GET")[1]["state"]["workOrders"][0]["id"] == "WO-A"
        del state["_revision"]
        assert request("PUT", state)[0] == 400
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


def test_concurrent_snapshots_allow_exactly_one_writer(tmp_path):
    db = tmp_path / "ops.sqlite3"
    with OPS.connect(db) as con:
        OPS.init_db(con)
    barrier = threading.Barrier(2)

    def write(record_id):
        with OPS.connect(db) as con:
            state = OPS.load_state(con, "test")
            state["workOrders"] = [{"id": record_id, "title": record_id, "status": "open"}]
            barrier.wait()
            try:
                OPS.save_state(con, "test", state, actor=actor("planner"), signing_key=KEY)
                return record_id
            except OPS.StateConflict:
                return None

    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = list(pool.map(write, ["WO-A", "WO-B"]))
    assert outcomes.count(None) == 1
    with OPS.connect(db) as con:
        state = OPS.load_state(con, "test")
        assert state["_revision"] == 1
        assert [row["id"] for row in state["workOrders"]] == [item for item in outcomes if item]


def test_failed_reinspection_and_reordered_history_cannot_release(tmp_path):
    with OPS.connect(tmp_path / "ops.sqlite3") as con:
        OPS.init_db(con)

        def save(state, role):
            return OPS.save_state(con, "test", state, actor=actor(role), signing_key=KEY)

        state = OPS.empty_state()
        state["workOrders"] = [{"id": "WO", "status": "open", "title": "fixture"}]
        state = save(state, "planner")
        state["inspections"] = [{"id": "I1", "wo_id": "WO", "result": "pass"}]
        state = save(state, "inspector")
        state["approvals"] = [{"id": "A1", "wo_id": "WO", "inspection_id": "I1", "decision": "approved"}]
        state = save(state, "approver")
        state["inspections"].append({"id": "I2", "wo_id": "WO", "result": "fail", "server_sequence": -999})
        state["workOrders"][0]["status"] = "hold"
        state = save(state, "inspector")
        assert OPS.latest_record(state["inspections"], "WO")["id"] == "I2"
        rejected = copy.deepcopy(state)
        rejected["workOrders"][0]["status"] = "closed"
        with pytest.raises(ValueError, match="lacks passing inspection"):
            save(rejected, "approver")
        state["inspections"].insert(0, {"id": "I3", "wo_id": "WO", "result": "pass"})
        state = save(state, "inspector")
        state["approvals"].append({"id": "A2", "wo_id": "WO", "inspection_id": "I3", "decision": "rejected"})
        state = save(state, "approver")
        rejected = copy.deepcopy(state)
        rejected["workOrders"][0]["status"] = "closed"
        with pytest.raises(ValueError, match="lacks passing inspection"):
            save(rejected, "approver")
        state["approvals"].append({"id": "A3", "wo_id": "WO", "inspection_id": "I3", "decision": "approved"})
        state = save(state, "approver")
        state["inspections"].reverse()
        state["approvals"].reverse()
        state["workOrders"][0]["status"] = "closed"
        state = save(state, "approver")
        assert state["workOrders"][0]["status"] == "closed"


def test_legacy_database_gains_revision_without_losing_records(tmp_path):
    with OPS.connect(tmp_path / "legacy.sqlite3") as con:
        con.execute("CREATE TABLE city_state (city_slug TEXT PRIMARY KEY, updated_at TEXT NOT NULL)")
        con.execute("INSERT INTO city_state VALUES ('test', 'legacy')")
        con.commit()
        OPS.init_db(con)
        assert OPS.load_state(con, "test")["_revision"] == 0
        saved = OPS.save_state(con, "test", OPS.empty_state())
        assert saved["_revision"] == 1


@pytest.mark.parametrize("results", [("fail", "pass"), ("pass", "fail")])
def test_a_batch_cannot_choose_the_order_of_new_inspection_outcomes(tmp_path, results):
    with OPS.connect(tmp_path / "ops.sqlite3") as con:
        OPS.init_db(con)
        state = OPS.empty_state()
        state["workOrders"] = [{"id": "WO", "status": "open"}]
        state = OPS.save_state(con, "test", state, actor=actor("planner"), signing_key=KEY)
        state["inspections"] = [
            {"id": f"I{index}", "wo_id": "WO", "result": result}
            for index, result in enumerate(results)
        ]
        with pytest.raises(ValueError, match="save each inspections event"):
            OPS.save_state(con, "test", state, actor=actor("inspector"), signing_key=KEY)
        assert OPS.load_state(con, "test")["inspections"] == []
