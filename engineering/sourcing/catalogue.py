"""Offline catalogue seeds with explicit source/product dependency resolution.

Only observation metadata and narrowly scoped facts are seeded. Catalogue hashes
bind retrieved bytes; neither a hash nor a catalogue record authenticates a
supplier or releases the physical design. Network retrieval belongs to adapters.
"""
from collections import Counter
from copy import deepcopy
import json
from pathlib import Path

from .model import encoded, record, text, validate_record, is_id

DATA = Path(__file__).resolve().parent / "data"
DEFAULT_PATHS = (DATA / "supplier-catalogue.json", DATA / "public-feeds.json",
                 DATA / "iraq-domestic-2026-july.json")
GROUPS = ("products", "offers", "fx", "benchmarks", "processes")
MAX_SEED_BYTES = 16 * 1024 ** 2
MAX_SEED_RECORDS = 10000


def _rows(seed, key):
    rows = seed.get(key, [])
    if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
        raise ValueError("Catalogue " + key + " must be a list of objects")
    return rows


def _fields(body):
    if {"schema", "kind", "record_id"} & set(body):
        raise ValueError("Seed record identity and kind are computed")
    return deepcopy(body)


def _references(body, sources, *, plural=False):
    """Resolve aliases, rejecting caller-supplied canonical reference IDs."""
    if "source_id" in body or "source_ids" in body:
        raise ValueError("Seed sources must use declared aliases")
    if plural:
        if "source_key" in body and "source_keys" in body:
            raise ValueError("Ambiguous source aliases")
        aliases = body.pop("source_keys", None)
        if aliases is None and "source_key" in body:
            aliases = [body.pop("source_key")]
        if not isinstance(aliases, list) or not aliases or len(aliases) != len(set(aliases)):
            raise ValueError("Distinct declared source aliases required")
    else:
        if "source_keys" in body:
            raise ValueError("Exactly one source alias required")
        aliases = [body.pop("source_key", None)]
    for alias in aliases:
        text(alias, "source alias")
        if alias not in sources:
            raise ValueError("Unknown catalogue source alias: " + alias)
    return [sources[alias]["record_id"] for alias in aliases]


def load_catalogue(paths=None):
    """Return canonical independent copies; never fetch network data or select parts.

    Identical aliases may be shared between input files. Conflicting definitions
    under one source alias or product key are rejected, rather than arbitrarily
    choosing whichever file was read last. Offers must cite a source attached to
    their exact product definition.
    """
    paths = DEFAULT_PATHS if paths is None else tuple(paths)
    if not paths or len(paths) > 32:
        raise ValueError("Explicit bounded seed paths required")
    seeds = []
    for path in paths:
        path = Path(path)
        if not path.is_file() or path.is_symlink() or path.stat().st_size > MAX_SEED_BYTES:
            raise ValueError("Bounded regular catalogue seed required: " + str(path))
        seed = json.loads(path.read_text(), parse_float=str)
        if not isinstance(seed, dict) or seed.get("schema") != "osr-sourcing-seed/1":
            raise ValueError("Catalogue seed schema differs")
        if set(seed) - {"schema", "sources", "notes", "research_package_id", *GROUPS}:
            raise ValueError("Unknown catalogue seed collection")
        if "notes" in seed and (not isinstance(seed["notes"], list) or any(not isinstance(note, str) for note in seed["notes"])):
            raise ValueError("Seed notes must be explicit provenance text")
        if "research_package_id" in seed and not is_id(seed["research_package_id"]):
            raise ValueError("Exact research package identity required")
        if not isinstance(seed.get("sources"), dict):
            raise ValueError("Explicit source alias mapping required")
        seeds.append(seed)
    sources, products, values = {}, {}, {}

    def retain(value):
        validate_record(value)
        key = value["record_id"]
        if key in values and encoded(values[key]) != encoded(value):
            raise ValueError("Conflicting canonical observation")
        values[key] = value
        if len(values) > MAX_SEED_RECORDS:
            raise ValueError("Catalogue record budget exceeded")

    for seed in seeds:
        for alias, fields in seed["sources"].items():
            text(alias, "source alias")
            if not isinstance(fields, dict) or "source_key" in fields:
                raise ValueError("Source alias body differs")
            body = _fields(fields)
            if "notes" in seed or "research_package_id" in seed:
                body["seed_provenance"] = {key: deepcopy(seed[key]) for key in ("notes", "research_package_id") if key in seed}
            value = record("source", source_key=alias, **body)
            if alias in sources and value != sources[alias]:
                raise ValueError("Conflicting source alias: " + alias)
            sources[alias] = value
            retain(value)
    for seed in seeds:
        for fields in _rows(seed, "products"):
            body = _fields(fields)
            body["source_ids"] = _references(body, sources, plural=True)
            value = record("product", **body)
            key = value["product_key"]
            if key in products and value != products[key]:
                raise ValueError("Conflicting product key: " + key)
            products[key] = value
            retain(value)
    for seed in seeds:
        for fields in _rows(seed, "offers"):
            body = _fields(fields)
            if "product_id" in body:
                raise ValueError("Seed offers must use a product key")
            key = body.pop("product_key", None)
            if key not in products:
                raise ValueError("Unknown offer product key: " + str(key))
            product = products[key]
            for field in ("manufacturer", "part_number"):
                if field in body and body[field] != product[field]:
                    raise ValueError("Offer/product identity mismatch: " + field)
            source_id = _references(body, sources)[0]
            if source_id not in product["source_ids"]:
                raise ValueError("Offer source does not identify the exact product")
            source = next(value for value in sources.values() if value["record_id"] == source_id)
            if source["source_kind"] not in {"manufacturer_catalogue", "distributor_catalogue", "supplier_quotation", "factory_catalogue", "engineering_estimate"}:
                raise ValueError("Commodity/tender benchmarks cannot become product offers")
            retain(record("offer", product_id=product["record_id"], source_id=source_id, **body))
        for group, kind in (("fx", "fx"), ("benchmarks", "benchmark"), ("processes", "process")):
            for fields in _rows(seed, group):
                body = _fields(fields)
                ids = _references(body, sources, plural=kind == "process")
                if kind == "fx" and not any(value["record_id"] == ids[0] and value["source_kind"] == "exchange_rate" for value in sources.values()):
                    raise ValueError("FX requires an exchange-rate source")
                body["source_ids" if kind == "process" else "source_id"] = ids if kind == "process" else ids[0]
                retain(record(kind, **body))
    return deepcopy(sorted(values.values(), key=lambda value: (value["kind"], value["record_id"])))


def seed(store, paths=None):
    """Atomically append validated observations; repeated seeding is idempotent."""
    values = load_catalogue(paths)
    added = store.insert_many(values)
    return dict(schema="osr-sourcing-seed-result/1", record_count=len(values),
                added_count=len(added), counts=dict(sorted(Counter(v["kind"] for v in values).items())),
                record_ids=[v["record_id"] for v in values], added_record_ids=sorted(added),
                source_ids={v["source_key"]: v["record_id"] for v in values if v["kind"] == "source"},
                product_ids={v["product_key"]: v["record_id"] for v in values if v["kind"] == "product"},
                physical_qualification=None, selected_reference_changed=False)
