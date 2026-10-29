"""Append-only logical records in SQLite, with checked dependency identities.

The database is not an OS security boundary. Every read rechecks payload hashes;
portable publications use canonical JSON rather than SQLite file-byte identity.
"""
from contextlib import contextmanager
from pathlib import Path
import json
import sqlite3
from .model import encoded, identity, validate_record

MAX_RECORD_BYTES = 8 * 1024 ** 2


def references(value):
    kind = value["kind"]
    refs = []
    if kind == "product":
        refs += value["source_ids"]
    elif kind == "offer":
        refs += [value["source_id"], value["product_id"]]
    elif kind in ("fx", "benchmark"):
        refs += [value["source_id"]]
    elif kind == "process":
        refs += value.get("source_ids", [])
    # Candidate/registry/part hashes belong to typed twin inputs, not to the
    # observation table. Domain overlay adapters validate those exact bindings.
    return sorted(set(refs))


def reference_types(value):
    kind = value["kind"]
    if kind == "product":
        return [(key, "source") for key in value["source_ids"]]
    if kind == "offer":
        return [(value["source_id"], "source"), (value["product_id"], "product")]
    if kind in ("fx", "benchmark"):
        return [(value["source_id"], "source")]
    if kind == "process":
        return [(key, "source") for key in value.get("source_ids", [])]
    return []


class Store:
    def __init__(self, path, *, readonly=False):
        self.path = Path(path).resolve()
        self.readonly = readonly
        if readonly:
            self.connection = sqlite3.connect(self.path.as_uri() + "?mode=ro", uri=True)
        else:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.connection = sqlite3.connect(self.path)
        self.connection.execute("PRAGMA foreign_keys=ON")
        version = self.connection.execute("PRAGMA user_version").fetchone()[0]
        if version not in (0, 1) or readonly and version != 1:
            self.connection.close()
            raise ValueError("Unsupported sourcing database revision")
        if not readonly:
            with self.connection:
                self.connection.executescript("""
                CREATE TABLE IF NOT EXISTS records(
                    record_id TEXT PRIMARY KEY, kind TEXT NOT NULL,
                    payload BLOB NOT NULL
                );
                CREATE INDEX IF NOT EXISTS records_kind ON records(kind);
                CREATE TABLE IF NOT EXISTS record_links(
                    record_id TEXT NOT NULL REFERENCES records(record_id),
                    parent_id TEXT NOT NULL REFERENCES records(record_id),
                    PRIMARY KEY(record_id,parent_id)
                );
                CREATE TRIGGER IF NOT EXISTS records_no_update BEFORE UPDATE ON records
                    BEGIN SELECT RAISE(ABORT,'Sourcing records are append-only'); END;
                CREATE TRIGGER IF NOT EXISTS records_no_delete BEFORE DELETE ON records
                    BEGIN SELECT RAISE(ABORT,'Sourcing records are append-only'); END;
                PRAGMA user_version=1;
                """)

    def close(self):
        self.connection.close()

    def __enter__(self):
        return self

    def __exit__(self, *unused):
        self.close()

    def get(self, record_id, kind=None):
        row = self.connection.execute("SELECT kind,payload FROM records WHERE record_id=?", (record_id,)).fetchone()
        if row is None:
            raise KeyError(record_id)
        value = json.loads(row[1])
        validate_record(value, kind)
        if row[0] != value["kind"] or value["record_id"] != record_id:
            raise ValueError("Database record index differs from payload")
        return value

    def all(self, kind=None, *, limit=100000):
        if type(limit) is not int or not 1 <= limit <= 200000:
            raise ValueError("Explicit bounded record query required")
        query = "SELECT record_id FROM records"
        params = []
        if kind is not None:
            query += " WHERE kind=?"
            params.append(kind)
        query += " ORDER BY record_id LIMIT ?"
        params.append(limit + 1)
        rows = self.connection.execute(query, params).fetchall()
        if len(rows) > limit:
            raise ValueError("Database query exceeds declared record budget")
        return [self.get(row[0], kind) for row in rows]

    def insert_many(self, values):
        if self.readonly:
            raise ValueError("Read-only sourcing database")
        prepared = {}
        for value in values:
            validate_record(value)
            raw = encoded(value)
            if len(raw) > MAX_RECORD_BYTES:
                raise ValueError("Sourcing observation exceeds record budget")
            key = value["record_id"]
            if key in prepared and prepared[key][1] != raw:
                raise ValueError("Conflicting record identity")
            prepared[key] = (value, raw)
        added = []
        with self.connection:
            pending = dict(prepared)
            while pending:
                progressed = False
                for key, (value, raw) in list(pending.items()):
                    refs = references(value)
                    if any(self.connection.execute("SELECT 1 FROM records WHERE record_id=?", (ref,)).fetchone() is None for ref in refs):
                        continue
                    for parent_id, expected_kind in reference_types(value):
                        parent = self.get(parent_id, expected_kind)
                        if value["kind"] == "fx" and parent["source_kind"] != "exchange_rate":
                            raise ValueError("FX requires its actual exchange-rate source")
                        if value["kind"] == "offer" and expected_kind == "source" and parent["source_kind"] not in {
                            "manufacturer_catalogue", "distributor_catalogue", "supplier_quotation",
                            "factory_catalogue", "engineering_estimate"
                        }:
                            raise ValueError("Commodity/tender benchmarks cannot become supplier product offers")
                        if value["kind"] == "offer" and expected_kind == "source" and value["source_class"] == "A" and parent["source_kind"] != "supplier_quotation":
                            raise ValueError("A public catalogue cannot self-promote to an actual quotation")
                    old = self.connection.execute("SELECT payload FROM records WHERE record_id=?", (key,)).fetchone()
                    if old is not None and old[0] != raw:
                        raise ValueError("Stored immutable observation differs")
                    if old is None:
                        self.connection.execute("INSERT INTO records VALUES(?,?,?)", (key, value["kind"], raw))
                        self.connection.executemany("INSERT INTO record_links VALUES(?,?)", [(key, ref) for ref in refs])
                        added.append(key)
                    del pending[key]
                    progressed = True
                if not progressed:
                    raise ValueError("Missing or cyclic source/product dependencies")
        return added

    def put(self, value):
        self.insert_many([value])
        return value["record_id"]

    def snapshot(self):
        values = self.all()
        result = dict(schema="osr-sourcing-database-snapshot/1", records=values,
                      record_count=len(values), physical_qualification=None,
                      immutable_records_are_not_supplier_authentication=True)
        result["snapshot_id"] = identity(result)
        return result
