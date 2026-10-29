"""Historical awarded pay items and unpriced BOQs retain distinct meanings."""
import csv
from datetime import datetime
from html.parser import HTMLParser
from io import StringIO
import re

from ..model import UNITS, day, decimal, decimal_text, record, validate_record
from ._source import checked_source

MAX_DOCUMENT = 20 * 1024**2


def _text(raw):
    if isinstance(raw, bytes):
        if len(raw) > MAX_DOCUMENT:
            raise ValueError("Tender document budget exceeded")
        return raw.decode("utf-8-sig")
    if isinstance(raw, str) and len(raw.encode()) <= MAX_DOCUMENT:
        return raw
    raise ValueError("Bounded tender text required")


class _Table(HTMLParser):
    def __init__(self):
        super().__init__()
        self.rows = []
        self.row = None
        self.cell = None
        self.text = []

    def handle_starttag(self, tag, attrs):
        if tag == "tr":
            self.row = []
        elif tag in ("td", "th") and self.row is not None:
            self.cell = []

    def handle_data(self, data):
        self.text.append(data)
        if self.cell is not None:
            self.cell.append(data)

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self.cell is not None:
            self.row.append(" ".join("".join(self.cell).split()))
            self.cell = None
        elif tag == "tr" and self.row is not None:
            self.rows.append(self.row)
            self.row = None


def _awarded(row, source):
    validate_record(source, "source")
    if source["source_kind"] != "awarded_bid":
        raise ValueError("Awarded-bid source required")
    if row.get("quantity_unit") not in UNITS:
        raise ValueError("Pay-item unit unsupported; lump sums are not unit rates")
    if not row.get("contract") or not row.get("item_code"):
        raise ValueError("Exact contract and item identity required")
    quantity = decimal(row.get("quantity"), "awarded quantity", positive=True)
    price = decimal(row.get("unit_price"), "awarded unit price")
    total = row.get("line_total")
    if total is not None and abs(quantity * price - decimal(total)) > decimal("0.01"):
        raise ValueError("Pay-item quantity/price/total do not reconcile")
    day(row.get("bid_open_date"))
    currency = row.get("currency")
    if not isinstance(currency, str) or not re.fullmatch("[A-Z]{3}", currency):
        raise ValueError("Explicit pay-item currency required")
    return record("benchmark", source_id=source["record_id"],
        benchmark_key="caltrans:" + row["contract"] + ":" + row["item_code"] + ":" + row["bid_open_date"],
        observation_date=row["bid_open_date"], unit_price=price,
        currency=currency, quantity_unit=row["quantity_unit"],
        reference_quantity=decimal_text(quantity), contract=row["contract"],
        item_code=row["item_code"], description=row.get("description"),
        district=row.get("district"), source_line_total=None if total is None else decimal_text(total),
        adjusted_unit_price=None if row.get("adjusted_unit_price") is None else decimal_text(row["adjusted_unit_price"]),
        adjustment_basis="Caltrans CHCCI; source vintage required",
        location="California, USA", cost_scope="historical-awarded-pay-item",
        scope_documents_required=True, mobilization_and_TRO_not_imported=True,
        target_Iraq_unit_rate=False, is_manufactured_product_price=False,
        delivered_or_installed_target_cost_complete=False)


def parse_caltrans_html(raw, source):
    checked_source(source, "awarded_bid", raw)
    parser = _Table()
    parser.feed(_text(raw))
    document = " ".join(" ".join(parser.text).split())
    if not re.search(r"Bidders\s*=\s*Awarded Only", document, re.I):
        raise ValueError("Actual Awarded Only query marker required")
    results = []
    for cells in parser.rows:
        if len(cells) != 13 or not re.match(r"^[0-9]{6}\s*-", cells[1]):
            continue
        code, description = cells[1].split("-", 1)
        def money(value):
            if not re.fullmatch(r"\$[0-9,]+(?:\.[0-9]+)?", value):
                raise ValueError("Actual Caltrans dollar value required")
            return value[1:].replace(",", "")
        row = dict(item_code=code.strip(), description=description.strip(),
                   quantity_unit=cells[2], district=cells[3], quantity=cells[4].replace(",", ""),
                   unit_price=money(cells[5]), adjusted_unit_price=money(cells[6]),
                   line_total=money(cells[7]), currency="USD", contract=cells[9],
                   bid_open_date=datetime.strptime(cells[8], "%m-%d-%Y").date().isoformat())
        results.append(_awarded(row, source))
    if not results:
        raise ValueError("No supported awarded pay-item rows found")
    if len({r["benchmark_key"] for r in results}) != len(results):
        raise ValueError("Duplicate awarded pay-item rows")
    return results


def parse_caltrans_csv(raw, source):
    checked_source(source, "awarded_bid", raw)
    rows = list(csv.DictReader(StringIO(_text(raw))))
    if not rows or len(rows) > 10000:
        raise ValueError("Bounded awarded CSV rows required")
    result = []
    for row in rows:
        if row.get("awarded", "").strip().lower() not in {"true", "yes", "1"}:
            raise ValueError("Explicit awarded status required for every row")
        for key in ("line_total", "adjusted_unit_price"):
            if not row.get(key):
                row[key] = None
        result.append(_awarded(row, source))
    if len({r["benchmark_key"] for r in result}) != len(result):
        raise ValueError("Duplicate awarded CSV pay items")
    return result


def parse_boq_csv(raw, source):
    checked_source(source, "tender_notice", raw)
    rows = list(csv.DictReader(StringIO(_text(raw))))
    if not rows or len(rows) > 10000:
        raise ValueError("Bounded BOQ rows required")
    normalized = []
    for index, row in enumerate(rows, 1):
        if not row.get("description"):
            raise ValueError("BOQ description required")
        quantity = None if not row.get("quantity") else decimal_text(row["quantity"])
        price = None if not row.get("unit_price") else decimal_text(row["unit_price"])
        normalized.append(dict(line_id=row.get("line_id") or str(index),
            description=row["description"], quantity=quantity,
            quantity_unit=row.get("quantity_unit") or None,
            observed_unit_price=price, currency=row.get("currency") or None,
            rate_state="unpriced" if price is None else "unverified-document-value",
            pricing_admitted=False))
    return [record("run", adapter="tender-boq", source_id=source["record_id"],
        status="held", reason="BOQ-quantities-do-not-establish-awarded-unit-rates",
        rows=normalized, price_offers_created=0)]
