"""Read an Airport estimate on stdin and verify the native price book inside one rolled-back ERP transaction."""

from decimal import Decimal, ROUND_HALF_UP
import json
import os
import sys
from uuid import uuid4

import frappe

from osr_erpnext.sourcing import stage_estimate
from osr_erpnext.sourcing_prices import publish_price_lists

os.chdir("/home/frappe/frappe-bench/sites")
frappe.init(site=os.environ["OSR_TEST_SITE"])
frappe.connect()
try:
    frappe.set_user("Administrator")
    packet = json.load(sys.stdin)
    tracked = ("Request for Quotation", "Supplier Quotation", "Purchase Order", "GL Entry")
    counts = {doctype: frappe.db.count(doctype) for doctype in tracked}
    default_list = frappe.db.get_single_value("Buying Settings", "buying_price_list")
    project = frappe.get_doc(
        dict(
            doctype="Project",
            company=os.environ["OSR_TEST_COMPANY"],
            project_name=f"OSR sourcing price test {uuid4().hex}",
        )
    ).insert()
    stage_estimate(project.name, packet)
    group = frappe.db.get_value("Item Group", {"is_group": 0}, "name")

    def publish():
        return publish_price_lists(project.name, packet["evaluation_id"], group)

    result = publish()
    assert publish() == result
    assert result["evaluation_id"] == packet["evaluation_id"]
    assert len(result["lots"]) == len(packet["lots"])
    priced = 0
    for data, row in zip(packet["lots"], result["lots"], strict=True):
        assert data["lot_id"] == row["lot_id"] and data["quantity"] == row["quantity"]
        item = frappe.get_doc("Item", row["item_code"])
        assert item.is_purchase_item and not item.is_stock_item and item.stock_uom == data["unit"]
        for band, rate in row["rates"].items():
            if data[band + "_usd"] is None:
                assert rate is None
                continue
            priced += 1
            entry = frappe.get_doc("Item Price", rate["item_price"])
            assert entry.price_list == result["price_lists"][band] and entry.currency == "USD"
            total = Decimal(str(data[band + "_usd"]))
            qty = Decimal(str(data.get("scenario_quantities", {}).get(band, data["quantity"])))
            unit_rate = (total / qty).quantize(
                Decimal(1).scaleb(-entry.precision("price_list_rate")), rounding=ROUND_HALF_UP
            )
            assert Decimal(str(entry.price_list_rate)) == unit_rate
            assert Decimal(rate["enquiry_at_unit_rate_usd"]) == unit_rate * Decimal(
                str(data["quantity"])
            )
            assert Decimal(rate["extended_rounding_difference_usd"]) == unit_rate * qty - total
    assert frappe.db.get_single_value("Buying Settings", "buying_price_list") == default_list
    assert {doctype: frappe.db.count(doctype) for doctype in tracked} == counts
    first = next(row["rates"]["base"] for row in result["lots"] if row["rates"]["base"])
    frappe.db.set_value("Item Price", first["item_price"], "price_list_rate", -5)
    try:
        publish()
    except frappe.ValidationError as exc:
        assert "Item Price differs" in str(exc)
    else:
        raise AssertionError("An existing changed Item Price was silently reused")
    frappe.set_user("Guest")
    try:
        publish()
    except frappe.PermissionError:
        pass
    else:
        raise AssertionError("Guest could access the buyer's estimate")
    print(
        json.dumps(
            dict(
                lots=len(result["lots"]),
                item_prices=priced,
                repeat_same=True,
                tampering_rejected=True,
                guest_denied=True,
                rolled_back=True,
            )
        )
    )
finally:
    frappe.db.rollback()
    frappe.destroy()
