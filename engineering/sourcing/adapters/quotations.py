"""Import supplier quotation leads without authenticating their own assertions."""
import csv
from io import StringIO
import json

from ..model import decimal_text, record, validate_record
from .tenders import _text
from ._source import checked_source


def _quotation_rows(rows, source):
    validate_record(source, "source")
    if source["source_kind"] != "supplier_quotation":
        raise ValueError("Supplier quotation source required")
    if not isinstance(rows, list) or not rows or len(rows) > 10000:
        raise ValueError("Bounded supplier quotation rows required")
    result = []
    claims = []
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("Supplier quotation row object required")
        fields = {k: row.get(k) for k in ("product_key", "manufacturer", "part_number", "category", "description")}
        specifications = row.get("specifications") or {}
        if isinstance(specifications, str):
            specifications = json.loads(specifications)
        if not isinstance(specifications, dict):
            raise ValueError("Quotation specification observations must be an object")
        specifications = dict(specifications)
        specifications.update(quotation_admission="held-unverified-document",
                              sourcing_holds=["quotation-authentication-and-scope-review-required"],
                              technical_compatibility="pending")
        result.append(record("product", **fields, specifications=specifications,
                             source_ids=[source["record_id"]]))
        claims.append(dict(product_id=result[-1]["record_id"],
            claimed_source_class=row.get("source_class"),
            observed_unit_price=None if row.get("unit_price") in (None, "") else decimal_text(row["unit_price"]),
            currency=row.get("currency"), quantity_unit=row.get("quantity_unit"),
            quoted_quantity=None if row.get("quantity") in (None, "") else decimal_text(row["quantity"], positive=True),
            price_date=row.get("price_date"), valid_until=row.get("valid_until"),
            claimed_authentication_ignored=any(row.get(key) in (True, 1, "true", "True", "1")
                                               for key in ("authenticated", "procurement_approved"))))
    result.append(record("run", adapter="supplier-quotation", source_id=source["record_id"],
                         status="held", reason="independent-quotation-authentication-required",
                         claims=claims, price_offers_created=0))
    return result


def parse_quotation_json(raw, source):
    checked_source(source, "supplier_quotation", raw)
    value = json.loads(_text(raw)) if isinstance(raw, (str, bytes)) else raw
    rows = value.get("items") if isinstance(value, dict) else value
    return _quotation_rows(rows, source)


def parse_quotation_csv(raw, source):
    checked_source(source, "supplier_quotation", raw)
    return _quotation_rows(list(csv.DictReader(StringIO(_text(raw)))), source)
