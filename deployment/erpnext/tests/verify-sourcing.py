"""Verify native RFQ and supplier replies in one rolled-back ERPNext v15 transaction.

Pass the published estimator JSON packet on stdin.
"""

from datetime import date, timedelta
import json
import os
import sys
from uuid import uuid4

import frappe
from frappe import share
from frappe.handler import execute_cmd
from frappe.website.page_renderers.template_page import TemplatePage
from werkzeug.test import EnvironBuilder
from werkzeug.wrappers import Request

from osr_erpnext.sourcing import (
    _QUOTE,
    _RFQ,
    _record_name,
    compare_rfq,
    create_rfq,
    get_estimate,
    get_request,
    list_buyer_requests,
    list_estimates,
    list_requests,
    stage_estimate,
    submit_offer,
)
from osr_erpnext.sourcing_contract import digest
from osr_erpnext.sourcing_scenario import opening_scenario
from osr_erpnext.sourcing_scenario_api import price_scenario


def rejected(function, error, *args, **kwargs):
    try:
        function(*args, **kwargs)
    except error:
        return
    raise AssertionError(f"{function.__name__} accepted a rejected action")


def insert(doctype, **values):
    return frappe.get_doc(dict(doctype=doctype, **values)).insert()


packet = json.load(sys.stdin)
os.chdir("/home/frappe/frappe-bench/sites")
frappe.init(site=os.environ.get("OSR_TEST_SITE", "osr-maglev-pilot.localhost"))
frappe.connect()
existing_rfq = frappe.db.count(_RFQ)
existing_quote = frappe.db.count(_QUOTE)
existing_email = frappe.db.count("Email Queue")
fixture = "OSR sourcing fixture " + uuid4().hex[:12]
all_docs = []
try:
    company = frappe.db.get_value("Company", {"default_currency": "USD"}, "name")
    project = insert("Project", project_name=fixture, company=company).name
    all_docs.append(("Project", project))
    other_project = insert("Project", project_name=fixture + " other project", company=company).name
    all_docs.append(("Project", other_project))
    lot = next(row for row in packet["lots"] if row["lot_id"] == "fleet")
    unit = lot["unit"]
    if not frappe.db.exists("UOM", unit):
        all_docs.append(("UOM", insert("UOM", uom_name=unit, must_be_whole_number=1).name))
    item = insert(
        "Item", item_code=fixture, item_name=fixture,
        item_group=frappe.db.get_value("Item Group", {"is_group": 0}, "name"),
        stock_uom=unit, is_stock_item=0, is_purchase_item=1, is_sales_item=0,
    ).name
    all_docs.append(("Item", item))
    wrong_item = insert(
        "Item", item_code=fixture+" wrong UOM", item_name=fixture,
        item_group=frappe.db.get_value("Item Group", {"is_group": 0}, "name"),
        stock_uom="Nos", is_stock_item=0, is_purchase_item=1, is_sales_item=0,
    ).name
    all_docs.append(("Item", wrong_item))
    suppliers, users = [], []
    for letter in "abc":
        email = f"{fixture.replace(' ', '-').lower()}-{letter}@example.invalid"
        user = insert("User", email=email, first_name=f"{fixture} {letter}", enabled=1,
                      send_welcome_email=0, user_type="Website User", roles=[dict(role="Supplier")]).name
        supplier = insert("Supplier", supplier_name=f"{fixture} {letter}", supplier_type="Company",
                          supplier_group=frappe.db.get_value("Supplier Group", {"is_group": 0}, "name"),
                          portal_users=[dict(user=user)]).name
        users.append(user)
        suppliers.append(supplier)
        all_docs.extend([("User", user), ("Supplier", supplier)])

    staged = stage_estimate(project, packet)
    assert staged["created"] and staged["packet_sha256"] == digest(packet)
    assert not stage_estimate(project, packet)["created"]
    assert get_estimate(project, packet["evaluation_id"]) == packet
    assert list_estimates(project)[0]["evaluation_id"] == packet["evaluation_id"]
    all_docs.append(("Note", staged["receipt"]))
    other_estimate = stage_estimate(other_project, packet)
    all_docs.append(("Note", other_estimate["receipt"]))
    changed_packet = dict(packet, candidate_id="f" * 64)
    rejected(stage_estimate, frappe.ValidationError, project, changed_packet)
    rejected(share.add, frappe.PermissionError, "Note", staged["receipt"], user=users[0])

    due = (date.today() + timedelta(days=90)).isoformat()
    args = dict(project=project, evaluation_id=packet["evaluation_id"], lot_id=lot["lot_id"],
                item_code=item, suppliers=suppliers[:2], required_on=due)
    rejected(create_rfq, frappe.ValidationError, **dict(args, item_code=wrong_item))
    rejected(create_rfq, frappe.ValidationError, **dict(args, suppliers=[]))
    rejected(create_rfq, frappe.ValidationError, **dict(args, suppliers=[suppliers[0], suppliers[0]]))
    first = create_rfq(**args)
    rfq = first["name"]
    all_docs.extend([(_RFQ, rfq), ("Note", _record_name("rfq", rfq))])
    assert first == dict(name=rfq, created=True, docstatus=0)
    assert create_rfq(**dict(args, suppliers=suppliers[1::-1])) == dict(name=rfq, created=False, docstatus=0)
    rejected(create_rfq, frappe.ValidationError, **dict(args, suppliers=suppliers))
    assert list_buyer_requests(project)[0]["rfq"] == rfq

    frappe.set_user(users[0])
    assert [request for request in list_requests() if request["rfq"] == rfq] == []
    rejected(get_request, frappe.PermissionError, rfq)
    rejected(get_estimate, frappe.PermissionError, project, packet["evaluation_id"])
    rejected(compare_rfq, frappe.PermissionError, rfq)
    rejected(frappe.get_doc("Note", staged["receipt"]).check_permission, frappe.PermissionError, "read")
    rejected(frappe.get_doc(_RFQ, rfq).check_permission, frappe.PermissionError, "read")
    frappe.set_user("Administrator")
    native = frappe.get_doc(_RFQ, rfq)
    assert all(not supplier.send_email for supplier in native.suppliers)
    native.submit()
    assert frappe.db.count("Email Queue") == existing_email

    quotes = []
    for user, rate in zip(users[:2], ["18000000", "20000000"], strict=True):
        frappe.set_user(user)
        assert {request["rfq"] for request in list_requests()} == {rfq}
        request = get_request(rfq)
        assert request["previous"] is None
        assert "suppliers" not in request and not {"low_usd", "high_usd", "sources"} & request["scope"].keys()
        frappe.form_dict.rfq = rfq
        frappe.local.request = Request(EnvironBuilder(path="/airport-sourcing").get_environ())
        rendered = TemplatePage("airport-sourcing").get_html()
        assert rfq in rendered and all(supplier not in rendered for supplier in suppliers)
        frappe.local.form_dict = frappe._dict(doctype=_RFQ)
        rows = execute_cmd("frappe.www.list.get_list_data")
        assert all(row.name != rfq for row in rows)
        assert rfq not in execute_cmd("frappe.www.list.get").get("raw_result", "")
        scope = request["scope"]
        offer = {key: scope[key] for key in ("candidate_id", "evaluation_id", "lot_id", "quantity", "unit", "currency")}
        offer.update(
            scope_sha256=request["scope_sha256"], rate_usd=rate, supplier_reference=f"FIXTURE-{rate}",
            valid_until=(date.today() + timedelta(days=45)).isoformat(), lead_time_days=70,
            annual_upkeep_usd="250000", renewals_usd={"15": "1200000"}, exclusions=[], warranty="Fixture only",
        )
        if quotes:
            other = frappe.get_doc(_QUOTE, quotes[0])
            assert not frappe.has_website_permission(other, "read", user)
            rejected(other.check_permission, frappe.PermissionError, "read")
        rejected(submit_offer, frappe.ValidationError, rfq, dict(offer, currency="EUR"))
        rejected(submit_offer, frappe.ValidationError, rfq, dict(offer, quantity=1))
        rejected(submit_offer, frappe.ValidationError, rfq, dict(offer, scope_sha256="f" * 64))
        quote = submit_offer(rfq, offer)
        assert quote["docstatus"] == 0 and quote["created"]
        quotes.append(quote["quotation"])
        all_docs.extend([(_QUOTE, quotes[-1]), ("Note", _record_name("offer", quotes[-1]))])
        assert get_request(rfq)["previous"]["quotation"] == quotes[-1]
        assert frappe.has_website_permission(frappe.get_doc(_QUOTE, quotes[-1]), "read", user)
        assert not submit_offer(rfq, dict(offer, rate_usd=rate+".00"))["created"]
        rejected(submit_offer, frappe.ValidationError, rfq, dict(offer, rate_usd=rate+"1"))

    frappe.set_user(users[2])
    assert list_requests() == []
    rejected(get_request, frappe.PermissionError, rfq)
    rejected(submit_offer, frappe.PermissionError, rfq, offer)
    rejected(price_scenario, frappe.PermissionError, project, rfq, quotes[0])
    frappe.set_user("Guest")
    rejected(list_requests, frappe.PermissionError)
    rejected(list_estimates, frappe.PermissionError, project)
    frappe.set_user("Administrator")
    comparison = compare_rfq(rfq)
    assert {row["status"] for row in comparison["suppliers"]} == {"received"}
    rows = comparison["comparison"]["offers"]
    assert sorted(row["direct_usd"] for row in rows) == [108_000_000, 120_000_000]
    assert all(row["pv_30y_4pct_usd"] > row["direct_usd"] for row in rows)
    assert comparison["comparison"]["direct_spread_usd"] == 12_000_000
    expired = compare_rfq(rfq, (date.today() + timedelta(days=50)).isoformat())
    assert not expired["comparison"]["offers"]
    rejected(opening_scenario, ValueError, packet, [(expired, quotes[0])])
    rejected(price_scenario, frappe.ValidationError, other_project, rfq, quotes[0])
    rejected(price_scenario, frappe.ValidationError, project, rfq, "NOT-A-QUOTATION")
    before_scenario = [frappe.db.get_value(_QUOTE, quote, "modified") for quote in quotes]
    scenario = price_scenario(project, rfq, quotes[0])
    assert scenario["replacements"][0]["displaced_central_direct_usd"] == 50_880_000
    assert scenario["replacements"][0]["quoted_direct_usd"] == 108_000_000
    assert scenario["direct_delta_usd"] == 57_120_000 and scenario["opening_delta_usd"] == 75_741_120
    assert not scenario["procurement_authorized"] and scenario["physical_acceptance"] == "open"
    assert [frappe.db.get_value(_QUOTE, quote, "modified") for quote in quotes] == before_scenario
    changed = frappe.get_doc(_QUOTE, quotes[0])
    changed.items[0].rate += 100
    rejected(changed.save, frappe.ValidationError)

    single_args = dict(args, round_no=2, suppliers=[suppliers[2]])
    single = create_rfq(**single_args)
    single_rfq = single["name"]
    all_docs.extend([(_RFQ, single_rfq), ("Note", _record_name("rfq", single_rfq))])
    assert single["created"] and single_rfq != rfq
    single_request = frappe.get_doc(_RFQ, single_rfq)
    assert [row.supplier for row in single_request.suppliers] == [suppliers[2]]
    single_request.submit()
    assert create_rfq(**single_args) == dict(name=single_rfq, created=False, docstatus=1)
    rejected(create_rfq, frappe.ValidationError, **dict(single_args, suppliers=suppliers[1:]))
    frappe.set_user(users[0])
    rejected(get_request, frappe.PermissionError, single_rfq)
    frappe.set_user(users[2])
    single_scope = get_request(single_rfq)
    single_quote = submit_offer(single_rfq, dict(offer, scope_sha256=single_scope["scope_sha256"]))["quotation"]
    all_docs.extend([(_QUOTE, single_quote), ("Note", _record_name("offer", single_quote))])
    frappe.set_user("Administrator")
    single_comparison = compare_rfq(single_rfq)["comparison"]
    assert single_comparison["scope_comparable_suppliers"] == 1
    assert single_comparison["direct_spread_usd"] is None and single_comparison["pv_spread_usd"] is None
    assert frappe.db.count(_RFQ) == existing_rfq + 2 and frappe.db.count(_QUOTE) == existing_quote + 3
    assert frappe.db.count("Email Queue") == existing_email
    print(json.dumps(dict(
        evidence_kind="software-fixture", authenticated_suppliers=2, uninvolved_supplier_denied=True,
        guest_denied=True, buyer_estimate_isolated=True, exact_immutable_estimate=True,
        distinct_competing_records=True, preserved_retries=True, changed_inputs_rejected=True,
        single_supplier_round=True, single_offer_spread_open=True, issued_invitation_set_immutable=True,
        native_quote_permission=True, expiry_excluded=True, no_email_queued=True,
        supplier_portal_rendered=True, managed_records_hidden_on_native_listing=True,
        scenario_bound_to_project_and_active_offer=True, scenario_read_only=True,
        scenario_id=scenario["scenario_id"], scenario_opening_delta_usd=scenario["opening_delta_usd"],
        comparison_id=comparison["comparison"]["comparison_id"],
        estimate_evaluation_id=packet["evaluation_id"], fixture_rolled_back=True,
    )))
finally:
    frappe.set_user("Administrator")
    frappe.db.rollback()
    for doctype, name in all_docs:
        assert not frappe.db.exists(doctype, name, cache=False), (doctype, name)
    frappe.db.rollback()
    frappe.destroy()
