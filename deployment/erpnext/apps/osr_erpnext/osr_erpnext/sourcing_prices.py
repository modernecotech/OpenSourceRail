"""Materialise a project estimate as ERPNext buying rates for individual enquiry lots."""

from decimal import Decimal, ROUND_HALF_UP
from hashlib import sha256
from html import escape
import json

import frappe

BANDS = {"low": "Low", "base": "Central", "high": "High"}


def _number(value, field):
    if isinstance(value, bool) or not isinstance(value, (float, int, Decimal)):
        frappe.throw(f"Numeric {field} required")
    number = Decimal(str(value))
    if not number.is_finite() or number < 0:
        frappe.throw(f"Invalid {field}")
    return number


def _master(doctype, name, fields):
    if frappe.db.exists(doctype, name):
        doc = frappe.get_doc(doctype, name)
        doc.check_permission("read")
        for key, expected in fields.items():
            if doc.get(key) != expected:
                frappe.throw(f"{doctype} {name} differs in {key}. Review the existing master.")
        return doc
    return frappe.get_doc({"doctype": doctype, **fields}).insert()


def _scope(project, evaluation_id):
    return sha256(json.dumps([project, evaluation_id], separators=(",", ":")).encode()).hexdigest()[:20]


def lot_item_code(project, evaluation_id, lot_id):
    return f"OSR-BID-{_scope(project, evaluation_id)}-{sha256(lot_id.encode()).hexdigest()[:12]}"


@frappe.whitelist(methods=["POST"])
def publish_price_lists(project, evaluation_id, item_group):
    """Create project-specific Items and three USD buying price lists in the caller's transaction."""
    from osr_erpnext.sourcing import get_estimate

    packet = get_estimate(project, evaluation_id)
    project_doc = frappe.get_doc("Project", project)
    project_doc.check_permission("write")
    # Serialize materialisation of a whole price book, including retries.
    frappe.db.get_value("Project", project, "name", for_update=True)
    group = frappe.get_doc("Item Group", item_group)
    group.check_permission("read")
    if group.is_group:
        frappe.throw("Choose a leaf Item Group for purchasable packages")
    if not frappe.db.get_single_value("Buying Settings", "buying_price_list"):
        frappe.throw(
            "Set the company's ordinary buying price list first so the estimate cannot become the default"
        )

    scope = _scope(project, evaluation_id)
    lists = {key: f"OSR estimate {scope} {label}" for key, label in BANDS.items()}
    for name in lists.values():
        _master(
            "Price List",
            name,
            dict(price_list_name=name, currency="USD", enabled=1, buying=1, selling=0),
        )

    rows = []
    for lot in packet["lots"]:
        lot_id = lot["lot_id"]
        quantity = _number(lot["quantity"], "enquiry quantity")
        if not quantity:
            frappe.throw(f"{lot_id} needs a positive enquiry quantity")
        unit = lot["unit"]
        if not frappe.db.exists("UOM", unit):
            frappe.get_doc(dict(doctype="UOM", uom_name=unit)).insert()
        # ERPNext names can be case-insensitive, including custom units.
        unit_doc = frappe.get_doc("UOM", unit)
        if unit_doc.name != unit or not unit_doc.enabled:
            frappe.throw(f"The lot requires the exact active unit {unit}")
        item_code = lot_item_code(project, evaluation_id, lot_id)
        title = str(lot["description"])
        note = f"Estimate {evaluation_id} / {lot_id} / {lot['price_period']} / {lot['inclusion_group']}"
        item = _master(
            "Item",
            item_code,
            dict(
                item_code=item_code,
                item_name=title[:140],
                description=f"{escape(title)}<br>{escape(note)}",
                item_group=item_group,
                stock_uom=unit,
                is_stock_item=0,
                is_purchase_item=1,
                is_sales_item=0,
            ),
        )
        if item.disabled or item.has_variants:
            frappe.throw(f"Expected an active purchasable package for {lot_id}")

        rates = {}
        for band, name in lists.items():
            if lot[f"{band}_usd"] is None:
                if frappe.db.exists("Item Price", {"price_list": name, "item_code": item_code}):
                    frappe.throw(f"Unpriced {lot_id} has an unexpected {band} Item Price")
                rates[band] = None
                continue
            amount = _number(lot[f"{band}_usd"], f"{lot_id} {band} amount")
            price = frappe.new_doc("Item Price")
            precision = price.precision("price_list_rate")
            quantum = Decimal(1).scaleb(-precision)
            band_qty = _number(
                lot.get("scenario_quantities", {}).get(band, lot["quantity"]),
                f"{lot_id} {band} scenario quantity",
            )
            if not band_qty:
                if amount:
                    frappe.throw(f"{lot_id} has a nonzero amount for zero scenario quantity")
                rates[band] = None
                continue
            rate = (amount / band_qty).quantize(quantum, rounding=ROUND_HALF_UP)
            if amount and not rate:
                frappe.throw(f"ERP price precision would round a nonzero {lot_id} estimate to zero")
            existing = frappe.get_all(
                "Item Price", filters={"price_list": name, "item_code": item_code}, pluck="name", limit=2
            )
            if existing:
                price = frappe.get_doc("Item Price", existing[0])
                price.check_permission("read")
                if (
                    len(existing) != 1
                    or price.uom != unit
                    or price.supplier
                    or price.customer
                    or price.batch_no
                    or price.valid_upto
                    or str(price.valid_from) != packet["estimate_date"]
                    or price.currency != "USD"
                    or price.note != note
                    or Decimal(str(price.price_list_rate)) != rate
                ):
                    frappe.throw(f"Existing {band} Item Price differs for {lot_id}")
            else:
                price.update(
                    dict(
                        item_code=item_code,
                        uom=unit,
                        price_list=name,
                        price_list_rate=float(rate),
                        note=note,
                        valid_from=packet["estimate_date"],
                    )
                )
                price.insert()
            rates[band] = {
                "item_price": price.name,
                "unit_usd": str(rate),
                "full_scope_usd": str(amount),
                "scenario_quantity": str(band_qty),
                "enquiry_at_unit_rate_usd": str(rate * quantity),
                "extended_rounding_difference_usd": str(rate * band_qty - amount),
            }
        rows.append(
            {
                "lot_id": lot_id,
                "item_code": item.name,
                "unit": unit,
                "quantity": lot["quantity"],
                "rates": rates,
            }
        )
    return {
        "project": project,
        "candidate_id": packet["candidate_id"],
        "evaluation_id": evaluation_id,
        "currency": "USD",
        "price_lists": lists,
        "lots": rows,
    }
