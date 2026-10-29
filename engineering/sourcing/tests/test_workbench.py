"""Read-only HTTP projections for the local sourcing Workbench."""
from contextlib import contextmanager
import json
from pathlib import Path
import threading
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from engineering.sourcing.model import identity, record
from engineering.sourcing.database import Store
from engineering.sourcing.publication import execute
from engineering.sourcing.workbench import build_server, WEB


@contextmanager
def live_server(database):
    server = build_server(database, port=0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield "http://127.0.0.1:%s" % server.server_address[1]
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def product_records(count=37, *, vendor="Ordinary Components"):
    source = record("source", publisher="Vendor directory", url="https://vendor.example/catalogue",
        retrieved_at="2026-10-29", access="public", source_kind="manufacturer_catalogue")
    values = [source]
    for index in range(count):
        values.append(record("product", product_key="PART-%03d" % index,
            manufacturer=vendor if index == 0 else "Vendor %03d" % index,
            part_number="P-%03d" % index, category="running-gear",
            description="Catalogue part %03d" % index, source_ids=[source["record_id"]],
            specifications={"mass": {"value": "2.5", "unit": "kg"}},
            supply_scope="component"))
    return values


def declared_input(candidate="a" * 64):
    requirement = record("requirement", candidate_id=candidate, input_id="b" * 64,
        namespace="fixture-vehicle", requirement_key="unresolved-bogie-account",
        description="Bogie assembly account without a located occurrence",
        category="running-gear", priority=4, quantity=None, quantity_unit=None,
        occurrence_ids=[], physical_scopes=[], procurement_scope="complete-bogie",
        identifiers={}, constraints=[])
    payload = dict(schema="osr-sourcing-declared-requirements/1",
                   candidate_id=candidate, requirements=[requirement])
    return dict(schema="osr-sourcing-twin-input/1", payload=payload,
                payload_id=identity(payload), origin={"fixture": True})


def make_run(database):
    with Store(database) as store:
        result = execute(store, declared_input(), {"as_of": "2026-10-29"})
        return result


def fetch_json(base, path):
    with urlopen(base + path, timeout=3) as response:
        return response.status, response.headers, json.loads(response.read())


def test_ui_is_read_only_and_never_interpolates_vendor_text_as_markup(tmp_path):
    database = tmp_path / "sourcing.sqlite3"
    with Store(database) as store:
        store.insert_many(product_records(count=1, vendor='<svg onload="alert(1)">Vendor & Co</svg>'))
    before = database.read_bytes()
    with live_server(database) as base:
        status, _, page = fetch_json(base, "/api/status")
        assert status == 200 and page["database_available"] is True
        with urlopen(base + "/", timeout=3) as response:
            html = response.read().decode()
        with urlopen(base + "/assets/app.js", timeout=3) as response:
            script = response.read().decode()
        status, _, products = fetch_json(base, "/api/records?kind=product&limit=1&offset=0")
        assert status == 200
        assert products["items"][0]["manufacturer"] == '<svg onload="alert(1)">Vendor & Co</svg>'
        with urlopen(base + "/api/records?kind=product&limit=1&offset=0") as response:
            raw = response.read()
        assert b"\\u003csvg" in raw and b"<svg" not in raw
    assert "Read only" in html
    assert "RFQ drafts are disabled" in html
    assert "textContent" in script
    assert ".innerHTML" not in script
    assert database.read_bytes() == before


def test_http_write_methods_return_405(tmp_path):
    database = tmp_path / "sourcing.sqlite3"
    with Store(database):
        pass
    with live_server(database) as base:
        for method in ("POST", "PUT", "PATCH", "DELETE"):
            request = Request(base + "/api/status", data=b"{}", method=method)
            try:
                urlopen(request, timeout=3)
            except HTTPError as error:
                assert error.code == 405
                assert error.headers["Allow"] == "GET, HEAD"
                body = json.loads(error.read())
                assert body["writes_disabled"] is True
            else:
                raise AssertionError(method + " unexpectedly succeeded")


def test_record_api_paginates_and_returns_a_small_projection(tmp_path):
    database = tmp_path / "sourcing.sqlite3"
    with Store(database) as store:
        store.insert_many(product_records())
    with live_server(database) as base:
        status, _, first = fetch_json(base, "/api/records?kind=product&limit=10&offset=0")
        assert status == 200
        assert first["total"] == 37 and len(first["items"]) == 10
        assert first["next_offset"] == 10
        status, _, second = fetch_json(base, "/api/records?kind=product&limit=10&offset=10")
        assert status == 200
        assert second["offset"] == 10 and len(second["items"]) == 10
        assert not set(item["record_id"] for item in first["items"]) & set(item["record_id"] for item in second["items"])
        assert "specification_count" in first["items"][0]
        assert "specifications" in first["items"][0]
        assert "source_ids" not in first["items"][0]


def test_offer_projection_keeps_quantity_packaging_and_price_breaks(tmp_path):
    database = tmp_path / "sourcing.sqlite3"
    source, product = product_records(count=1)
    offer = record("offer", product_id=product["record_id"], source_id=source["record_id"],
        price_date="2026-10-29", valid_until=None, currency="GBP", quantity_unit="m",
        source_class="B", tax_basis="excluded", tax_rate=None,
        minimum_order_quantity="100", order_multiple="10",
        packaging={"roll_length_m": "100", "note": "one roll"},
        tiers=[{"minimum_quantity": "0", "maximum_quantity": "10", "unit_price": "4.05"}],
        market="public catalogue")
    with Store(database) as store:
        store.insert_many([source, product, offer])
    with live_server(database) as base:
        status, _, page = fetch_json(base, "/api/records?kind=offer&limit=10&offset=0")
    assert status == 200 and page["total"] == 1
    row = page["items"][0]
    assert row["quantity_unit"] == "m"
    assert row["packaging"]["roll_length_m"] == "100"
    assert row["tiers"][0]["unit_price"] == "4.05"
    assert row["minimum_order_quantity"] == "100"


def test_requirement_projection_exposes_selected_product_and_bounded_configuration(tmp_path):
    database = tmp_path / "sourcing.sqlite3"
    requirement = record("requirement", candidate_id="a" * 64, input_id="b" * 64,
        namespace="manufacturing-study", requirement_key="core-20mm",
        description="M80 core material takeoff", category="body-materials", priority=3,
        quantity="18.8889", quantity_unit="kg", occurrence_ids=[], physical_scopes=["study/core"],
        procurement_scope="raw-material", identifiers={"manufacturer": "Gurit", "part_number": "Corecell M80"},
        constraints=[], selected_product_record_id="c" * 64,
        product_configuration={"reference_area_m2": "10", "target_thickness_mm": "20", "sheet_count": None})
    with Store(database) as store:
        store.put(requirement)
    with live_server(database) as base:
        status, _, page = fetch_json(base, "/api/records?kind=requirement&limit=1&offset=0")
    assert status == 200
    assert page["items"][0]["selected_product_record_id"] == "c" * 64
    assert page["items"][0]["product_configuration"]["target_thickness_mm"] == "20"
    assert page["items"][0]["product_configuration"]["sheet_count"] is None


def test_status_and_run_evidence_apis_report_coverage_and_paginate(tmp_path):
    database = tmp_path / "sourcing.sqlite3"
    result = make_run(database)
    with live_server(database) as base:
        status, _, state = fetch_json(base, "/api/status")
        assert status == 200
        assert state["counts"]["run"] == 1
        assert state["recent_runs"][0]["summary"]["unknown_quantity_requirements"] == 1
        status, _, run_page = fetch_json(base, "/api/runs?limit=1&offset=0")
        assert status == 200 and run_page["total"] == 1
        assert run_page["items"][0]["run_id"] == result["record_id"]
        path = "/api/runs/%s/items?section=requirements&limit=1&offset=0" % result["record_id"]
        status, _, evidence = fetch_json(base, path)
        assert status == 200
        assert evidence["total"] == 1
        assert evidence["items"][0]["quantity"] is None
        assert "vehicle-only input does not cover" in state["note"].lower()


def test_workbench_only_binds_loopback_and_uses_local_assets():
    try:
        build_server(Path("/tmp/unused"), host="0.0.0.0", port=8774)
    except ValueError as error:
        assert "127.0.0.1" in str(error)
    else:
        raise AssertionError("non-loopback bind unexpectedly accepted")
    assert (WEB / "index.html").is_file()
    assert (WEB / "styles.css").is_file()
    assert (WEB / "app.js").is_file()
