"""Local, read-only HTTP Workbench for bounded sourcing review."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import sqlite3
from urllib.parse import parse_qs, urlsplit

from . import publication
from .database import Store

WEB = Path(__file__).with_name("web")
KINDS = {"source", "product", "offer", "fx", "benchmark", "process",
         "requirement", "assessment", "rfq", "overlay", "run", "redesign"}
SECTIONS = {
    "requirements": "requirement_ids",
    "technical_assessments": "technical_assessment_ids",
    "price_assessments": "price_assessment_ids",
    "RFQ_drafts": "rfq_ids",
    "redesign_tasks": "redesign_ids",
}
MAX_PAGE_SIZE = 100


def _json_bytes(value):
    # Keep JSON valid while preventing a reflected value from terminating an
    # accidental script or markup context at a caller's rendering boundary.
    value = json.dumps(value, ensure_ascii=False, allow_nan=False,
                       separators=(",", ":"))
    return (value.replace("&", "\\u0026").replace("<", "\\u003c")
            .replace(">", "\\u003e").replace("\u2028", "\\u2028")
            .replace("\u2029", "\\u2029")).encode("utf-8")


def _text(value, maximum=1600):
    if value is None:
        return None
    if isinstance(value, str) and len(value) > maximum:
        return value[:maximum] + "…"
    return value


def _bounded_value(value, *, depth=0):
    """Project typed facts with strict depth, key, item and text limits."""
    if value is None or isinstance(value, (bool, int, float)):
        return value
    if isinstance(value, str):
        return _text(value, 240)
    if depth >= 3:
        return "nested value omitted"
    if isinstance(value, list):
        result = [_bounded_value(item, depth=depth + 1) for item in value[:10]]
        if len(value) > 10:
            result.append("… (%s more)" % (len(value) - 10))
        return result
    if isinstance(value, dict):
        keys = sorted(value, key=str)
        result = {str(key)[:80]: _bounded_value(value[key], depth=depth + 1)
                  for key in keys[:16]}
        if len(keys) > 16:
            result["_omitted_key_count"] = len(keys) - 16
        return result
    return _text(str(value), 240)


def _project(value):
    kind = value["kind"]
    common = {"record_id": value["record_id"], "kind": kind}
    fields = {
        "source": ("publisher", "source_kind", "retrieved_at", "access"),
        "product": ("product_key", "manufacturer", "part_number", "category",
                    "description", "supply_scope"),
        "offer": ("product_id", "source_id", "price_date", "currency", "source_class",
                  "tax_basis", "quantity_unit", "minimum_order_quantity", "order_multiple",
                  "packaging"),
        "fx": ("base_currency", "quote_currency", "rate_date", "rate", "source_id"),
        "benchmark": ("benchmark_key", "observation_date", "quantity_unit", "currency",
                      "unit_price", "geographic_scope", "cost_scope", "source_id"),
        "process": ("process_key", "process_name", "material_family", "estimate_key",
                    "candidate_id", "currency", "estimated_unit_cost", "output_unit",
                    "candidate_takeoff_mapped", "source_ids"),
        "requirement": ("candidate_id", "namespace", "requirement_key", "description",
                        "category", "priority", "quantity", "quantity_unit", "scope_kind",
                        "procurement_scope", "selected_product_record_id",
                        "source_manufacturing_group_id", "engineering_occurrence_count",
                        "procurement_unit_status", "system", "material", "stock_scope"),
        "assessment": ("candidate_id", "requirement_id", "product_id", "product_key",
                       "status", "holds", "suitability_scope", "assessment_type",
                       "estimate_date", "target_currency", "source_price_date",
                       "comparable_order_subtotal", "comparable_listed_extension"),
        "rfq": ("candidate_id", "category", "submission_allowed", "send_supplier_emails",
                "purchase_authorized"),
        "overlay": ("candidate_id", "estimate_date", "currency", "known_catalogue_subtotal",
                    "known_listed_extension_subtotal", "coverage", "complete_installed_total",
                    "complete_whole_life_total"),
        "redesign": ("candidate_id", "requirement_id", "product_id", "task_type", "status", "reason"),
    }
    for key in fields.get(kind, ()):
        if key in value:
            common[key] = _text(value[key])
    if kind == "product":
        common["source_count"] = len(value.get("source_ids", []))
        specifications = value.get("specifications", {})
        keys = sorted(specifications, key=str)
        common["specification_count"] = len(keys)
        common["specifications"] = {str(key)[:80]: _bounded_value(specifications[key])
                                     for key in keys[:24]}
        if len(keys) > 24:
            common["specifications_omitted_key_count"] = len(keys) - 24
    elif kind == "requirement" and value.get("product_configuration") is not None:
        common["product_configuration"] = _bounded_value(value["product_configuration"])
    elif kind == "offer":
        tiers = value.get("tiers", [])
        common["tiers"] = [_bounded_value(tier) for tier in tiers[:32]]
        common["tier_count"] = len(tiers)
        if len(tiers) > 32:
            common["tiers_omitted_count"] = len(tiers) - 32
    elif kind == "process":
        common["source_count"] = len(value.get("source_ids", []))
    elif kind == "assessment":
        holds = value.get("holds", [])
        common["holds"] = [_text(item, 240) for item in holds[:20]]
        common["hold_count"] = len(holds)
    elif kind == "requirement":
        common["occurrence_count"] = len(value.get("occurrence_ids", []))
        common["identifiers"] = {key: _text(item, 500) for key, item in value.get("identifiers", {}).items()}
        common["source_gross_stock_mass_kg"] = value.get("accounted_mass_kg")
        if value.get("decision_sensitivity") is not None:
            common["decision_sensitivity"] = _bounded_value(value["decision_sensitivity"])
        if value.get("source_manufacturing_group") is not None:
            common["source_manufacturing_group"] = _bounded_value(value["source_manufacturing_group"])
    elif kind == "rfq":
        common["requirement_count"] = len(value.get("requirement_ids", []))
        common["requested_item_count"] = len(value.get("requested_items", []))
    return common


def _page_args(query):
    try:
        limit = int(query.get("limit", ["25"])[0])
        offset = int(query.get("offset", ["0"])[0])
    except (TypeError, ValueError):
        raise ValueError("Integer offset and limit required") from None
    if not 1 <= limit <= MAX_PAGE_SIZE or not 0 <= offset <= 10_000_000:
        raise ValueError("Page size must be 1–100 and offset must be nonnegative")
    return limit, offset


def _records(store, kind, limit, offset):
    if kind not in KINDS:
        raise ValueError("Unsupported record kind")
    if kind == "run":
        return _run_page(store, limit, offset)
    total = store.connection.execute("SELECT COUNT(*) FROM records WHERE kind=?", (kind,)).fetchone()[0]
    ids = [row[0] for row in store.connection.execute(
        "SELECT record_id FROM records WHERE kind=? ORDER BY record_id LIMIT ? OFFSET ?",
        (kind, limit, offset))]
    items = [(publication.summary(store, store.get(record_id, "run")) if kind == "run"
              else _project(store.get(record_id, kind))) for record_id in ids]
    return dict(schema="osr-sourcing-record-page/1", kind=kind, total=total,
                limit=limit, offset=offset, next_offset=offset + len(ids) if offset + len(ids) < total else None,
                items=items)


def _run_page(store, limit, offset):
    where = "kind='run' AND json_extract(payload, '$.input_payload_id') IS NOT NULL"
    total = store.connection.execute("SELECT COUNT(*) FROM records WHERE " + where).fetchone()[0]
    ids = [row[0] for row in store.connection.execute(
        "SELECT record_id FROM records WHERE " + where + " ORDER BY rowid DESC LIMIT ? OFFSET ?",
        (limit, offset))]
    return dict(schema="osr-sourcing-run-page/1", total=total, limit=limit, offset=offset,
                next_offset=offset + len(ids) if offset + len(ids) < total else None,
                items=[publication.summary(store, store.get(record_id, "run")) for record_id in ids])


def _detail_page(store, run, section, limit, offset):
    field = SECTIONS[section]
    ids = run[field]
    page_ids = ids[offset:offset + limit]
    items = [_project(store.get(record_id)) for record_id in page_ids]
    return dict(schema="osr-sourcing-run-evidence-page/1", run_id=run["record_id"],
                section=section, total=len(ids), limit=limit, offset=offset,
                next_offset=offset + len(page_ids) if offset + len(page_ids) < len(ids) else None,
                items=items)


def _status(database):
    if not Path(database).is_file():
        return dict(schema="osr-sourcing-workbench-status/1", database_available=False,
                    counts={kind: 0 for kind in sorted(KINDS)}, recent_runs=[],
                    complete_installed_cost=None, complete_whole_life_cost=None,
                    physical_qualification=None, supplier_communications_sent=0,
                    note="Initialize the local database, then seed or evaluate a typed input.")
    with Store(database, readonly=True) as store:
        counts = {kind: 0 for kind in KINDS}
        counts.update({row[0]: row[1] for row in store.connection.execute(
            "SELECT kind, COUNT(*) FROM records GROUP BY kind")})
        counts["run"] = store.connection.execute(
            "SELECT COUNT(*) FROM records WHERE kind='run' AND json_extract(payload, '$.input_payload_id') IS NOT NULL").fetchone()[0]
        ids = [row[0] for row in store.connection.execute(
            "SELECT record_id FROM records WHERE kind='run' AND json_extract(payload, '$.input_payload_id') IS NOT NULL ORDER BY rowid DESC LIMIT 5")]
        recent = [publication.summary(store, store.get(record_id, "run")) for record_id in ids]
        return dict(schema="osr-sourcing-workbench-status/1", database_available=True,
                    counts=counts, recent_runs=recent,
                    complete_installed_cost=None, complete_whole_life_cost=None,
                    physical_qualification=None, supplier_communications_sent=0,
                    note="Coverage reflects supplied typed inputs; a vehicle-only input does not cover infrastructure or whole-life scope.")


def build_server(database, *, host="127.0.0.1", port=8774):
    if host != "127.0.0.1":
        raise ValueError("The sourcing Workbench may bind only to 127.0.0.1")
    if type(port) is not int or not 0 <= port <= 65535:
        raise ValueError("Valid local TCP port required")
    database = Path(database).expanduser().resolve()

    class Handler(BaseHTTPRequestHandler):
        server_version = "OSRSourcingWorkbench/1"
        sys_version = ""

        def log_message(self, fmt, *args):
            # Avoid logging untrusted query strings into shared terminal logs.
            return

        def __getattr__(self, name):
            # BaseHTTPRequestHandler otherwise returns 501 for extension verbs.
            # Unknown methods are denied in the same way as known write verbs.
            if name.startswith("do_"):
                return self._method_not_allowed
            raise AttributeError(name)

        def _send(self, status, body=b"", content_type="application/json; charset=utf-8"):
            if isinstance(body, str):
                body = body.encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'")
            self.send_header("Referrer-Policy", "no-referrer")
            if status == 405:
                self.send_header("Allow", "GET, HEAD")
            self.end_headers()
            if self.command != "HEAD" and body:
                self.wfile.write(body)

        def _reply_json(self, value, status=200):
            self._send(status, _json_bytes(value))

        def _method_not_allowed(self):
            self._reply_json(dict(error="method-not-allowed", writes_disabled=True), 405)

        def do_GET(self):
            parsed = urlsplit(self.path)
            path = parsed.path
            query = parse_qs(parsed.query, keep_blank_values=True)
            try:
                if path == "/" or path == "/index.html":
                    self._send(200, (WEB / "index.html").read_bytes(), "text/html; charset=utf-8")
                elif path == "/assets/app.js":
                    self._send(200, (WEB / "app.js").read_bytes(), "text/javascript; charset=utf-8")
                elif path == "/assets/styles.css":
                    self._send(200, (WEB / "styles.css").read_bytes(), "text/css; charset=utf-8")
                elif path == "/api/status":
                    self._reply_json(_status(database))
                elif path == "/api/runs":
                    limit, offset = _page_args(query)
                    if not database.is_file():
                        self._reply_json(dict(schema="osr-sourcing-run-page/1", total=0,
                                              limit=limit, offset=offset, next_offset=None, items=[]))
                        return
                    with Store(database, readonly=True) as store:
                        self._reply_json(_run_page(store, limit, offset))
                elif path == "/api/records":
                    kinds = query.get("kind", [])
                    if len(kinds) != 1:
                        raise ValueError("Exactly one record kind is required")
                    limit, offset = _page_args(query)
                    if not database.is_file():
                        if kinds[0] not in KINDS:
                            raise ValueError("Unsupported record kind")
                        self._reply_json(dict(schema="osr-sourcing-record-page/1", kind=kinds[0],
                                              total=0, limit=limit, offset=offset,
                                              next_offset=None, items=[]))
                        return
                    with Store(database, readonly=True) as store:
                        self._reply_json(_records(store, kinds[0], limit, offset))
                elif path.startswith("/api/runs/"):
                    parts = path.strip("/").split("/")
                    if len(parts) == 4 and parts[0:2] == ["api", "runs"] and parts[3] == "items":
                        run_id = parts[2]
                        section_values = query.get("section", [])
                        if len(section_values) != 1 or section_values[0] not in SECTIONS:
                            raise ValueError("A supported evidence section is required")
                        limit, offset = _page_args(query)
                        with Store(database, readonly=True) as store:
                            run = store.get(run_id, "run")
                            self._reply_json(_detail_page(store, run, section_values[0], limit, offset))
                    elif len(parts) == 4 and parts[0:2] == ["api", "runs"] and parts[3] == "summary":
                        run_id = parts[2]
                        with Store(database, readonly=True) as store:
                            self._reply_json(publication.summary(store, store.get(run_id, "run")))
                    else:
                        self._reply_json(dict(error="not-found"), 404)
                else:
                    self._reply_json(dict(error="not-found"), 404)
            except (ValueError, KeyError, sqlite3.Error, OSError) as error:
                self._reply_json(dict(error="bad-request", message=str(error)), 400)

        def do_HEAD(self):
            # `_send` suppresses the body for HEAD while preserving GET headers.
            self.do_GET()

        def do_POST(self): self._method_not_allowed()
        def do_PUT(self): self._method_not_allowed()
        def do_PATCH(self): self._method_not_allowed()
        def do_DELETE(self): self._method_not_allowed()
        def do_OPTIONS(self): self._method_not_allowed()
        def do_TRACE(self): self._method_not_allowed()
        def do_CONNECT(self): self._method_not_allowed()

    return ThreadingHTTPServer((host, port), Handler)


def serve(database, *, port=8774):
    server = build_server(database, port=port)
    print(f"Sourcing Workbench: http://127.0.0.1:{server.server_address[1]}/", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
