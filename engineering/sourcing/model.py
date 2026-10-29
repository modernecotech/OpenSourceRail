"""Immutable commercial observations, separate from physical part identity.

Decimal quantities are serialized as strings. A record hash binds the observation
bytes; it does not authenticate a supplier, approve a material or qualify a train.
"""
from copy import deepcopy
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
import hashlib
import json
import re
from urllib.parse import urlsplit, parse_qsl

SCHEMA = "osr-sourcing-record/1"
FLAGS = dict(engineering_accepted=False, engineering_approved=False,
             procurement_approved=False, physical_accepted=False,
             manufacturing_release=False, operating_release=False,
             selected_reference_changed=False, unknown_is_zero=False)
KINDS = {"source", "product", "offer", "fx", "benchmark", "process",
         "requirement", "assessment", "rfq", "overlay", "run", "redesign"}
UNITS = {"each", "kg", "g", "t", "m", "mm", "m2", "m3", "CY", "h",
         "kWh", "W", "kW", "V", "A", "Pa", "MPa", "degC", "fraction"}
SOURCE_KINDS = {"manufacturer_catalogue", "distributor_catalogue",
                "commodity_benchmark", "exchange_rate", "tender_notice",
                "awarded_bid", "supplier_quotation", "factory_catalogue",
                "published_test", "engineering_estimate", "national_statistic",
                "marketplace_benchmark"}


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode("utf-8")


def identity(value):
    return hashlib.sha256(encoded(value)).hexdigest()


def is_id(value):
    return isinstance(value, str) and re.fullmatch("[0-9a-f]{64}", value) is not None


def text(value, name):
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Nonempty " + name + " required")
    return value


def decimal(value, name="quantity", *, positive=False, nonnegative=True):
    if isinstance(value, bool) or value is None:
        raise ValueError("Explicit decimal " + name + " required")
    try:
        number = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise ValueError("Finite decimal " + name + " required") from None
    if not number.is_finite() or positive and number <= 0 or nonnegative and number < 0:
        raise ValueError("Out-of-domain " + name)
    return number


def decimal_text(value, name="quantity", **kwargs):
    number = decimal(value, name, **kwargs)
    if len(number.as_tuple().digits) > 10000 or abs(number.as_tuple().exponent) > 10000:
        raise ValueError("Decimal observation exceeds explicit storage budget")
    if number.is_zero():
        return "0"
    result = format(number, "f")
    return result.rstrip("0").rstrip(".") if "." in result else result


def day(value, name="date"):
    try:
        parsed = date.fromisoformat(value)
    except (ValueError, TypeError):
        raise ValueError("ISO calendar " + name + " required") from None
    if parsed.isoformat() != value:
        raise ValueError("Canonical ISO " + name + " required")
    return parsed


def _id(value, name):
    if not is_id(value):
        raise ValueError("Exact " + name + " identity required")


def _source_ids(value):
    if not isinstance(value, list) or not value or len(value) != len(set(value)):
        raise ValueError("Distinct source identities required")
    for source in value:
        _id(source, "source")


def _validate_body(value):
    kind = value.get("kind")
    if not isinstance(kind, str) or kind not in KINDS:
        raise ValueError("Supported sourcing record kind required")
    if any(value.get(key) is not expected for key, expected in FLAGS.items()):
        raise ValueError("Sourcing observations cannot approve or release hardware")
    if kind == "source":
        for key in ("publisher", "url", "retrieved_at", "access"):
            text(value.get(key), key)
        parsed = urlsplit(value["url"])
        if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password or len(value["url"]) > 4096:
            raise ValueError("Explicit HTTPS source URL required")
        if any(key.lower() in {"token", "access_token", "refresh_token", "api_key", "apikey", "client_secret", "password", "authorization"}
               for key, unused in parse_qsl(parsed.query)):
            raise ValueError("Source URLs must not contain credentials")
        if value.get("source_kind") not in SOURCE_KINDS:
            raise ValueError("Explicit source category required")
        when = value["retrieved_at"]
        if len(when) == 10:
            day(when)
        else:
            try:
                stamp = datetime.fromisoformat(when.replace("Z", "+00:00"))
            except ValueError:
                raise ValueError("ISO retrieval timestamp required") from None
            if stamp.tzinfo is None:
                raise ValueError("Retrieval timezone required")
        digest = value.get("document_sha256")
        if digest is not None:
            _id(digest, "source document")
    elif kind == "product":
        for key in ("product_key", "manufacturer", "part_number", "category", "description"):
            text(value.get(key), key)
        _source_ids(value.get("source_ids"))
        if not isinstance(value.get("specifications"), dict):
            raise ValueError("Explicit specification observations required")
    elif kind == "offer":
        _id(value.get("product_id"), "product")
        _id(value.get("source_id"), "source")
        day(value.get("price_date"), "price date")
        until = value.get("valid_until")
        if until is not None and day(until) < day(value["price_date"]):
            raise ValueError("Offer validity precedes observation")
        if not isinstance(value.get("currency"), str) or re.fullmatch("[A-Z]{3}", value["currency"]) is None:
            raise ValueError("ISO currency code required")
        if value.get("quantity_unit") not in UNITS:
            raise ValueError("Unambiguous offer quantity unit required")
        if value.get("source_class") not in ("A", "B", "C"):
            raise ValueError("Explicit commercial evidence class required")
        if value.get("tax_basis") not in ("included", "excluded", "unknown"):
            raise ValueError("Explicit price tax scope required")
        if value.get("tax_rate") is not None and not 0 <= decimal(value["tax_rate"]) <= 1:
            raise ValueError("Tax fraction outside domain")
        for key in ("minimum_order_quantity", "order_multiple"):
            if value.get(key) is not None:
                decimal(value[key], key, positive=True)
        tiers = value.get("tiers")
        if not isinstance(tiers, list) or not tiers:
            raise ValueError("Actual price breaks required; an unpriced lead is not an offer")
        previous = None
        for index, row in enumerate(tiers):
            lower = decimal(row.get("minimum_quantity"), "tier minimum")
            upper = None if row.get("maximum_quantity") is None else decimal(row["maximum_quantity"])
            decimal(row.get("unit_price"), "unit price")
            # Canonical breaks are half-open [minimum, maximum), matching the
            # actual catalogue quantity contracts; None means no upper bound.
            if upper is not None and upper <= lower:
                raise ValueError("Invalid price break interval")
            if index and (previous is None or lower < previous):
                raise ValueError("Overlapping/unsorted price breaks")
            previous = upper
    elif kind == "fx":
        _id(value.get("source_id"), "FX source")
        day(value.get("rate_date"), "rate date")
        for key in ("base_currency", "quote_currency"):
            if not isinstance(value.get(key), str) or re.fullmatch("[A-Z]{3}", value[key]) is None:
                raise ValueError("ISO FX currencies required")
        if value["base_currency"] == value["quote_currency"]:
            raise ValueError("Do not invent same-currency FX observations")
        decimal(value.get("rate"), "FX rate", positive=True)
    elif kind == "benchmark":
        _id(value.get("source_id"), "benchmark source")
        text(value.get("benchmark_key"), "benchmark name")
        day(value.get("observation_date"), "benchmark observation date")
        if value.get("quantity_unit") not in UNITS:
            raise ValueError("Benchmark quantity unit required")
        if not isinstance(value.get("currency"), str) or re.fullmatch("[A-Z]{3}", value["currency"]) is None:
            raise ValueError("ISO benchmark currency required")
        decimal(value.get("unit_price"), "benchmark value")
        if value.get("is_manufactured_product_price") is not False:
            raise ValueError("A benchmark cannot become a manufactured product quote")
    elif kind == "requirement":
        for key in ("candidate_id", "input_id"):
            _id(value.get(key), key)
        text(value.get("namespace"), "typed BOM namespace")
        text(value.get("requirement_key"), "requirement key")
        if value.get("quantity") is not None:
            decimal(value["quantity"], "requirement quantity", positive=True)
            if value.get("quantity_unit") not in UNITS:
                raise ValueError("Requirement unit required")
        if not isinstance(value.get("occurrence_ids"), list):
            raise ValueError("Explicit occurrence inventory or empty unresolved account required")
        if len(value["occurrence_ids"]) != len(set(value["occurrence_ids"])):
            raise ValueError("Duplicate requirement occurrences")
    elif kind in {"assessment", "rfq", "overlay", "redesign"}:
        _id(value.get("candidate_id"), "candidate")
    # Remaining domain fields are checked by their typed adapters. Keeping their
    # namespace explicit prevents a scene account becoming a registry occurrence.
    encoded(value)


def record(kind, **fields):
    if {"record_id", "schema", "kind"} & set(fields):
        raise ValueError("Record type and identity are computed, never supplied")
    if any(key in fields and fields[key] is not expected for key, expected in FLAGS.items()):
        raise ValueError("Unsupported sourcing acceptance claim")
    value = dict(schema=SCHEMA, kind=kind, **deepcopy(fields))
    if kind == "offer":
        value.setdefault("minimum_order_quantity", None)
        value.setdefault("order_multiple", None)
        for key in ("minimum_order_quantity", "order_multiple", "tax_rate"):
            if value.get(key) is not None:
                value[key] = decimal_text(value[key], key)
        for tier in value.get("tiers", []):
            for key in ("minimum_quantity", "maximum_quantity", "unit_price"):
                if tier.get(key) is not None:
                    tier[key] = decimal_text(tier[key], key)
    elif kind in ("fx", "benchmark", "requirement"):
        key = {"fx": "rate", "benchmark": "unit_price", "requirement": "quantity"}[kind]
        if value.get(key) is not None:
            value[key] = decimal_text(value[key], key)
    value.update(FLAGS)
    _validate_body(value)
    value["record_id"] = identity(value)
    return value


def validate_record(value, kind=None):
    if not isinstance(value, dict) or value.get("schema") != SCHEMA:
        raise ValueError("Sourcing record schema differs")
    if kind is not None and value.get("kind") != kind:
        raise ValueError("Typed sourcing record differs")
    body = {key: item for key, item in value.items() if key != "record_id"}
    if not is_id(value.get("record_id")) or value["record_id"] != identity(body):
        raise ValueError("Sourcing record payload/identity differs")
    _validate_body(body)
    return value
