"""Native ERPNext RFQs and attributable Supplier Quotations for one priced lot."""

import base64
from contextlib import contextmanager
from datetime import date, timedelta
from html import escape
import json

import frappe
from frappe.utils import getdate, today

from osr_erpnext.sourcing_contract import (
    amount_usd,
    calendar_date,
    canonical,
    corrected_enquiry_reference,
    decimal_value,
    digest,
    estimate_payload,
    exact_text,
    offer_payload,
    one_lot,
)

_RFQ = "Request for Quotation"
_QUOTE = "Supplier Quotation"
_RFQ_PREFIX = "OSR-RFQ-"
_QUOTE_PREFIX = "OSR-SQ-"
_RECORD_PREFIX = "OSR-SRC-"
_WRITE_TOKEN = object()


def _input(check, *args, **kwargs):
    try:
        return check(*args, **kwargs)
    except (ValueError, ArithmeticError) as exc:
        frappe.throw(str(exc))


@contextmanager
def _atomic(operation):
    frappe.db.savepoint(operation)
    try:
        yield
    except Exception:
        frappe.db.rollback(save_point=operation)
        raise


def _desk_project(project, write=False):
    if frappe.session.user == "Guest" or "Desk User" not in frappe.get_roles():
        frappe.throw("Sourcing buyer access required", frappe.PermissionError)
    doc = frappe.get_doc("Project", project)
    doc.check_permission("write" if write else "read")
    frappe.has_permission(_RFQ, ptype="create" if write else "read", throw=True)
    if not doc.company:
        frappe.throw("Select a Project with a buying company")
    return doc


def _record_name(kind, key):
    return _RECORD_PREFIX + digest([kind, key])


def _record_title(kind, project=None):
    return f"OSR sourcing {kind}" + (f" {digest(project)}" if project else "")


def _decode_record(note, kind, project=None):
    try:
        wrapper = json.loads(base64.b64decode(note.content, validate=True))
        if note.public or note.owner != "Administrator" or note.title != _record_title(kind, project):
            raise ValueError
        if wrapper["kind"] != kind or wrapper["sha256"] != digest(wrapper["value"]):
            raise ValueError
        return wrapper["value"]
    except (ValueError, TypeError, KeyError):
        frappe.throw("Stored sourcing evidence failed its integrity check")


def _read_record(kind, key, *, lock=False):
    note = frappe.db.get_value("Note", _record_name(kind, key),
                               ["title", "public", "owner", "content"], as_dict=True,
                               for_update=lock, cache=False)
    if note is None:
        return None
    return _decode_record(note, kind, key[0] if kind == "estimate" else None)


def _save_record(kind, key, value):
    content = dict(kind=kind, value=value, sha256=digest(value))
    note = frappe.get_doc(dict(
        doctype="Note", title=_record_title(kind, key[0] if kind == "estimate" else None), public=0,
        content=base64.b64encode(canonical(content).encode()).decode(),
    ))
    note.flags.osr_sourcing_token = _WRITE_TOKEN
    note.insert(ignore_permissions=True, set_name=_record_name(kind, key))


def protect_sourcing_note(doc, method=None):
    if not (doc.name or "").startswith(_RECORD_PREFIX):
        return
    if doc.flags.osr_sourcing_token is not _WRITE_TOKEN or not doc.is_new() or doc.public:
        frappe.throw("Sourcing evidence is an immutable private receipt", frappe.PermissionError)
    doc.owner = "Administrator"


def protect_sourcing_share(doc, method=None):
    prefix = {
        "Note": _RECORD_PREFIX,
        _RFQ: _RFQ_PREFIX,
        _QUOTE: _QUOTE_PREFIX,
    }.get(doc.share_doctype)
    if prefix and (doc.share_name or "").startswith(prefix):
        frappe.throw("Use the sourcing access workflow for this record", frappe.PermissionError)


def preserve_sourcing_record(doc, method=None, **kwargs):
    if (doc.name or "").startswith((_RFQ_PREFIX, _QUOTE_PREFIX, _RECORD_PREFIX)):
        frappe.throw("Keep the original sourcing record for review", frappe.PermissionError)


def _require_protection():
    hooks = frappe.get_doc_hooks()
    for doctype, handler in (
        ("Note", "protect_sourcing_note"),
        (_RFQ, "validate_rfq"),
        (_QUOTE, "validate_quotation"),
        ("DocShare", "protect_sourcing_share"),
    ):
        if f"osr_erpnext.sourcing.{handler}" not in hooks.get(doctype, {}).get("validate", []):
            frappe.throw("Load the current OSR app hooks before registering sourcing records")
    if (frappe.override_whitelisted_method("frappe.www.list.get_list_data") !=
            "osr_erpnext.sourcing.website_list_data"):
        frappe.throw("Load the current OSR app hooks before registering sourcing records")


@frappe.whitelist(methods=["POST"])
def stage_estimate(project, packet):
    buyer_project = _desk_project(project, write=True)
    _require_protection()
    packet = _input(estimate_payload, packet)
    key = [buyer_project.name, packet["evaluation_id"]]
    if len(canonical(packet).encode()) > 1024 * 1024:
        frappe.throw("The native sourcing estimate snapshot exceeds 1 MiB")
    frappe.db.get_value("Project", buyer_project.name, "name", for_update=True)
    existing = _read_record("estimate", key, lock=True)
    created = existing is None
    if existing and digest(existing) != digest(packet):
        frappe.throw("That evaluation already has different staged evidence")
    if created:
        _save_record("estimate", key, packet)
    return dict(project=buyer_project.name, candidate_id=packet["candidate_id"],
                evaluation_id=packet["evaluation_id"], receipt=_record_name("estimate", key),
                packet_sha256=digest(packet), created=created)


@frappe.whitelist(methods=["GET"])
def get_estimate(project, evaluation_id):
    _desk_project(project)
    return _staged_estimate(project, evaluation_id)


@frappe.whitelist(methods=["GET"])
def list_estimates(project, offset=0):
    _desk_project(project)
    offset = int(_input(decimal_value, offset, "offset", places=0))
    notes = frappe.get_all("Note", filters={"title": _record_title("estimate", project)},
                           fields=["name", "title", "public", "owner", "content"],
                           limit_start=offset, limit_page_length=50, order_by="creation desc, name desc")
    rows = []
    for note in notes:
        packet = _decode_record(note, "estimate", project)
        if note.name != _record_name("estimate", [project, packet["evaluation_id"]]):
            frappe.throw("Stored estimate failed its Project binding check")
        rows.append({key: packet[key] for key in ("candidate_id", "evaluation_id")})
    return rows


def _staged_estimate(project, evaluation_id, *, lock=False):
    packet = _read_record("estimate", [project, evaluation_id], lock=lock)
    if packet is None:
        frappe.throw("Stage the exact engineering estimate for this Project and evaluation first")
    return packet


def _scope(packet, lot):
    # Supplier-facing scope excludes budget allowances and comparison evidence.
    technical = (
        "design_id", "design_documents", "published_scope", "outgoing_circuits", "midpoint_ties",
        "protected_track_km", "branch_disconnect_and_test_points", "operating_year", "stop_ids",
        "fleet_cars", "opening_installed_tare_kg", "supports", "bearing_units", "lifts",
        "peak_dc_mw", "site_peak_dc_mw_proxy",
    )
    return dict(
        candidate_id=packet["candidate_id"], evaluation_id=packet["evaluation_id"],
        lot_id=lot["lot_id"], description=lot["description"], quantity=lot["quantity"], unit=lot["unit"],
        currency="USD", price_period=lot.get("price_period", "one-time"),
        deliverables=lot.get("deliverables", []), exclusions=lot.get("exclusions", []),
        technical_scope={key: lot[key] for key in technical if key in lot},
        price_basis=lot.get("price_basis", "constant 2026 USD"),
        commercial_scope=("Include the requested deliverables and all applicable charges for that scope "
                          "in the lot rate. Specify any exclusions, differences, or unconfirmed coverage."),
    )


def _rfq_description(scope):
    return escape(scope["description"])


def _rfq_native_matches(rfq, binding):
    if (rfq.company != binding["company"] or str(rfq.schedule_date) != binding["required_on"]
            or rfq.subject != binding["subject"] or rfq.message_for_supplier != binding["message"]
            or rfq.send_attached_files or rfq.send_document_print or rfq.email_template
            or rfq.get("amended_from") or len(rfq.items) != 1):
        return False
    suppliers = sorted(row.supplier for row in rfq.suppliers)
    if suppliers != binding["suppliers"] or any(row.send_email for row in rfq.suppliers):
        return False
    row = rfq.items[0]
    scope = binding["scope"]
    return (
        row.item_code == binding["item_code"] and row.uom == scope["unit"]
        and row.stock_uom == scope["unit"] and row.conversion_factor == 1
        and decimal_value(row.qty, "native RFQ quantity") == decimal_value(scope["quantity"], "lot quantity")
        and str(row.schedule_date) == binding["required_on"] and row.project_name == binding["project"]
        and row.description == _rfq_description(scope) and not row.material_request
    )


def validate_rfq(doc, method=None):
    if not (doc.name or "").startswith(_RFQ_PREFIX):
        return
    binding = _read_record("rfq", doc.name)
    if (not binding or not _rfq_native_matches(doc, binding)
            or (doc.is_new() and doc.flags.osr_sourcing_token is not _WRITE_TOKEN)):
        frappe.throw("Native RFQ differs from its staged sourcing scope")


def _supplier_list(value):
    if isinstance(value, str):
        value = json.loads(value)
    if not isinstance(value, list) or not 1 <= len(value) <= 50:
        raise ValueError("Select between 1 and 50 Supplier records")
    codes = [exact_text(supplier, "Supplier") for supplier in value]
    if len(codes) != len(set(codes)):
        raise ValueError("Select distinct Supplier records")
    return sorted(codes)


@frappe.whitelist(methods=["POST"])
def create_rfq(project, evaluation_id, lot_id, item_code, suppliers, required_on, round_no=1):
    buyer_project = _desk_project(project, write=True)
    _require_protection()
    supplier_codes = _input(_supplier_list, suppliers)
    need = _input(calendar_date, required_on)
    round_no = int(_input(decimal_value, round_no, "sourcing round", places=0, positive=True))
    frappe.db.get_value("Project", buyer_project.name, "name", for_update=True)
    packet = _staged_estimate(project, evaluation_id, lock=True)
    lot = _input(one_lot, packet, lot_id)
    name = _RFQ_PREFIX + digest([project, packet["candidate_id"], lot_id, round_no])
    scope = dict(_scope(packet, lot), rfq=name, round_no=round_no, required_on=need.isoformat(),
                 buyer_company=buyer_project.company)
    quantity = _input(decimal_value, scope["quantity"], "quantity", positive=True)
    binding = dict(
        project=project, company=buyer_project.company, item_code=item_code, suppliers=supplier_codes,
        scope=scope, estimate_sha256=digest(packet), required_on=need.isoformat(), round_no=round_no,
        subject=f"OSR sourcing {lot_id} round {round_no}",
        message=f"Supply the complete {escape(lot_id)} lot in USD. Use the OSR supplier offer page.",
    )
    existing = _read_record("rfq", name, lock=True)
    if existing:
        rfq = frappe.get_doc(_RFQ, name, for_update=True)
        rfq.check_permission("read")
        if digest(existing) != digest(binding) or not _rfq_native_matches(rfq, binding):
            frappe.throw("That sourcing round already has different inputs or requires integrity review")
        return dict(name=rfq.name, docstatus=rfq.docstatus, created=False)
    if need < getdate(today()):
        frappe.throw("Required delivery date cannot be in the past")

    item = frappe.get_doc("Item", item_code)
    item.check_permission("read")
    if item.disabled or not item.is_purchase_item or item.stock_uom != scope["unit"]:
        frappe.throw(f"Select an enabled purchase Item with the exact {escape(scope['unit'])} stock UOM")
    for supplier in supplier_codes:
        supplier_doc = frappe.get_doc("Supplier", supplier)
        supplier_doc.check_permission("read")
        if (supplier_doc.name != supplier or supplier_doc.disabled or supplier_doc.get("on_hold")
                or supplier_doc.prevent_rfqs):
            frappe.throw("Select enabled Supplier records eligible for RFQs")

    rfq = frappe.get_doc(dict(
        doctype=_RFQ, company=binding["company"], subject=binding["subject"],
        message_for_supplier=binding["message"], schedule_date=need,
        send_attached_files=0, send_document_print=0,
        suppliers=[dict(supplier=supplier, send_email=0) for supplier in supplier_codes],
        items=[dict(
            item_code=item.name, item_name=item.item_name, description=_rfq_description(scope),
            qty=float(quantity), uom=item.stock_uom,
            stock_uom=item.stock_uom, conversion_factor=1, schedule_date=need,
            project_name=project,
        )],
    ))
    rfq.flags.osr_sourcing_token = _WRITE_TOKEN
    with _atomic("osr_sourcing_rfq"):
        _save_record("rfq", name, binding)
        rfq.insert(set_name=name)
        if not _rfq_native_matches(frappe.get_doc(_RFQ, name), binding):
            frappe.throw("Native RFQ changed the lot or its unit precision")
    return dict(name=rfq.name, docstatus=rfq.docstatus, created=True)


def _portal_supplier():
    user = frappe.session.user
    account = frappe.db.get_value("User", user, ["enabled", "user_type"], as_dict=True)
    if (not account or not account.enabled or account.user_type != "Website User"
            or "Supplier" not in frappe.get_roles()):
        frappe.throw("Enabled supplier portal access required", frappe.PermissionError)
    suppliers = set(frappe.get_all("Portal User", filters={
        "parenttype": "Supplier", "parentfield": "portal_users", "user": user,
    }, pluck="parent"))
    if len(suppliers) != 1:
        frappe.throw("Portal account must identify exactly one Supplier", frappe.PermissionError)
    supplier = suppliers.pop()
    if frappe.db.get_value("Supplier", supplier, "disabled") != 0:
        frappe.throw("Enabled supplier portal access required", frappe.PermissionError)
    return supplier


def protect_website_quotation(doc, ptype, user, verbose=False):
    if not doc:
        return False
    if not (doc.name or "").startswith(_QUOTE_PREFIX):
        return True
    if user != frappe.session.user:
        return False
    try:
        supplier = _portal_supplier()
    except frappe.PermissionError:
        return False
    receipt = _read_record("offer", doc.name)
    return bool(receipt and doc.supplier == supplier == receipt["supplier"])


def _website_prefix(doctype):
    if "Desk User" in frappe.get_roles():
        return None
    return {_RFQ.casefold(): _RFQ_PREFIX, _QUOTE.casefold(): _QUOTE_PREFIX}.get(doctype.casefold())


@frappe.whitelist(allow_guest=True, methods=["GET", "POST"])
def website_list_data(doctype, **kwargs):
    from frappe.www.list import get_list_data

    rows = get_list_data(doctype, **kwargs)
    prefix = _website_prefix(doctype)
    return [row for row in rows if not row.name.startswith(prefix)] if prefix else rows


@frappe.whitelist(allow_guest=True, methods=["GET", "POST"])
def website_list(doctype, **kwargs):
    from frappe.www.list import get

    listing = get(doctype, **kwargs)
    prefix = _website_prefix(doctype)
    if prefix and listing.get("raw_result"):
        # Frappe returns complete native records alongside the rendered rows.
        pairs = [pair for pair in zip(json.loads(listing["raw_result"]), listing["result"], strict=True)
                 if not pair[0]["name"].startswith(prefix)]
        listing["raw_result"] = json.dumps([row for row, _ in pairs])
        listing["result"] = [html for _, html in pairs]
    return listing


@frappe.whitelist(methods=["GET", "POST"])
def desk_rfq_lookup(doctype, txt, searchfield, start, page_len, filters):
    from erpnext.buying.doctype.request_for_quotation.request_for_quotation import get_rfq_containing_supplier

    if "Desk User" not in frappe.get_roles():
        frappe.throw("Use the authenticated supplier offer page", frappe.PermissionError)
    frappe.has_permission(_RFQ, ptype="read", throw=True)
    return get_rfq_containing_supplier(doctype, txt, searchfield, start, page_len, filters)


def _portal_request(name, supplier, *, lock=False):
    if (not isinstance(name, str) or not name.startswith(_RFQ_PREFIX)
            or frappe.db.get_value(_RFQ, name, "docstatus", for_update=lock) != 1):
        frappe.throw("Sourcing request unavailable", frappe.PermissionError)
    binding = _read_record("rfq", name, lock=lock)
    if not binding or supplier not in binding["suppliers"]:
        frappe.throw("Sourcing request unavailable", frappe.PermissionError)
    rfq = frappe.get_doc(_RFQ, name, for_update=lock)
    if not _rfq_native_matches(rfq, binding):
        frappe.throw("Sourcing request unavailable", frappe.PermissionError)
    return rfq, binding


@frappe.whitelist(methods=["GET"])
def list_requests(offset=0):
    supplier = _portal_supplier()
    offset = int(_input(decimal_value, offset, "offset", places=0))
    eligible = frappe.get_all("Request for Quotation Supplier", filters={
        "parenttype": _RFQ, "parentfield": "suppliers", "supplier": supplier,
        "parent": ["like", _RFQ_PREFIX + "%"], "docstatus": 1,
    }, pluck="parent", limit_start=offset, limit_page_length=50, order_by="creation desc, name desc")
    return [dict(rfq=name, url=f"/airport-sourcing?rfq={name}") for name in eligible]


@frappe.whitelist(methods=["GET"])
def list_buyer_requests(project, offset=0):
    _desk_project(project)
    offset = int(_input(decimal_value, offset, "offset", places=0))
    rows = frappe.get_list(_RFQ, filters=[[_RFQ, "name", "like", _RFQ_PREFIX + "%"],
                                         ["Request for Quotation Item", "project_name", "=", project]],
                           fields=["name", "docstatus", "creation"], start=offset, page_length=50,
                           order_by="`tabRequest for Quotation`.creation desc, `tabRequest for Quotation`.name desc",
                           distinct=True)
    requests = []
    for row in rows:
        binding = _read_record("rfq", row.name)
        if binding and binding["project"] == project:
            scope = binding["scope"]
            requests.append(dict(rfq=row.name, docstatus=row.docstatus, lot_id=scope["lot_id"],
                                 evaluation_id=scope["evaluation_id"], round_no=binding["round_no"],
                                 required_on=binding["required_on"]))
    return requests


def _quote_name(rfq, supplier):
    return _QUOTE_PREFIX + digest([rfq, supplier])


@frappe.whitelist(methods=["GET"])
def get_request(rfq):
    supplier = _portal_supplier()
    request, binding = _portal_request(rfq, supplier)
    scope = binding["scope"]
    quote_name = _quote_name(rfq, supplier)
    receipt = _read_record("offer", quote_name)
    prior = None
    if receipt:
        native = frappe.get_doc(_QUOTE, quote_name)
        if not _quote_native_matches(native, request, binding, receipt):
            frappe.throw("This offer requires integrity review")
        prior = dict(quotation=native.name, docstatus=native.docstatus, status=native.status,
                     offer=receipt["offer"])
    result = dict(rfq=rfq, round_no=binding["round_no"], required_on=binding["required_on"],
                  scope=scope, scope_sha256=digest(scope), previous=prior)
    packet = _staged_estimate(binding["project"], scope["evaluation_id"])
    if digest(packet) != binding["estimate_sha256"]:
        frappe.throw("RFQ estimate requires integrity review")
    lot = _input(one_lot, packet, scope["lot_id"])
    reference = _input(corrected_enquiry_reference, packet, lot)
    if reference is not None:
        result["enquiry_reference"] = reference
    return result


def _terms(offer):
    lines = [
        f"Supplier reference: {escape(offer['supplier_reference'])}",
        f"Delivery lead time: {offer['lead_time_days']} days",
        f"Warranty: {escape(offer['warranty'])}",
        "Scope SHA-256: " + offer["scope_sha256"],
    ]
    upkeep = offer["annual_upkeep_usd"]
    renewals = offer["renewals_usd"]
    exclusions = offer["exclusions"]
    lines += [
        "Separate annual upkeep: " + ("Unquoted" if upkeep is None else f"USD {upkeep:,.2f}"),
        "Renewals: " + ("Unquoted" if renewals is None else ", ".join(
            f"year {year}, USD {amount:,.2f}" for year, amount in sorted(renewals.items(), key=lambda row: int(row[0]))
        ) or "None declared"),
        "Coverage: " + ("Unconfirmed" if exclusions is None else ", ".join(map(escape, exclusions)) or "Full declared scope"),
    ]
    return "<p>" + "</p><p>".join(lines) + "</p>"


def _quote_native_matches(doc, rfq, binding, receipt):
    offer = receipt["offer"]
    if (receipt["rfq"] != rfq.name or doc.name != _quote_name(rfq.name, receipt["supplier"])
            or (doc.company, doc.supplier, doc.currency, doc.owner) !=
            (rfq.company, receipt["supplier"], "USD", receipt["account"])
            or doc.conversion_rate != receipt["conversion_rate"]
            or doc.project != binding["project"] or doc.quotation_number != offer["supplier_reference"]
            or str(doc.valid_till) != offer["valid_until"] or str(doc.transaction_date) != receipt["recorded_on"]
            or doc.terms != _terms(offer) or doc.taxes or doc.discount_amount or doc.additional_discount_percentage
            or len(doc.items) != 1):
        return False
    row = doc.items[0]
    rate = decimal_value(offer["rate_usd"], "USD unit rate")
    qty = decimal_value(offer["quantity"], "quantity", positive=True)
    expected_total = amount_usd(rate, qty)
    return (
        row.request_for_quotation == rfq.name and row.request_for_quotation_item == rfq.items[0].name
        and row.item_code == rfq.items[0].item_code and row.uom == row.stock_uom == offer["unit"]
        and row.conversion_factor == 1 and row.project == binding["project"]
        and decimal_value(row.qty, "native quote quantity") == qty
        and decimal_value(row.rate, "native quote USD rate") == rate
        and decimal_value(row.amount, "native quote USD amount") == expected_total
        and decimal_value(doc.grand_total, "native quote USD total") == expected_total
    )


def validate_quotation(doc, method=None):
    managed = (doc.name or "").startswith(_QUOTE_PREFIX)
    linked = any(
        (row.request_for_quotation or "").startswith(_RFQ_PREFIX)
        or (row.request_for_quotation_item and
            (frappe.db.get_value("Request for Quotation Item", row.request_for_quotation_item, "parent") or "")
            .startswith(_RFQ_PREFIX))
        for row in doc.items
    )
    if not managed and not linked:
        return
    if doc.is_new() and doc.flags.osr_sourcing_token is _WRITE_TOKEN:
        return
    if not managed or doc.is_new():
        frappe.throw("Submit this lot through the authenticated OSR supplier offer page", frappe.PermissionError)
    receipt = _read_record("offer", doc.name)
    if receipt:
        binding = _read_record("rfq", receipt["rfq"])
        rfq = frappe.get_doc(_RFQ, receipt["rfq"])
        if binding and _quote_native_matches(doc, rfq, binding, receipt):
            return
    frappe.throw("Native quotation differs from its recorded supplier offer")


def assign_supplier_owner(doc, method=None):
    if doc.flags.osr_sourcing_token is _WRITE_TOKEN:
        doc.owner = doc.modified_by = doc.flags.osr_supplier_account
        for item in doc.items:
            item.owner = item.modified_by = doc.owner


def _conversion_rate(company, on):
    currency = frappe.db.get_value("Company", company, "default_currency")
    if currency == "USD":
        return 1
    rates = frappe.get_all("Currency Exchange", filters={
        "from_currency": "USD", "to_currency": currency, "date": ["<=", on], "for_buying": 1,
    }, fields=["exchange_rate"], order_by="date desc, creation desc", limit_page_length=1)
    if not rates or not rates[0].exchange_rate:
        frappe.throw("Configure a dated USD buying exchange rate for the company's native books")
    return rates[0].exchange_rate


@frappe.whitelist(methods=["POST"])
def submit_offer(rfq, offer):
    supplier = _portal_supplier()
    _require_protection()
    request, binding = _portal_request(rfq, supplier, lock=True)
    offer = _input(offer_payload, offer, binding)
    name = _quote_name(rfq, supplier)
    receipt = _read_record("offer", name, lock=True)
    if receipt:
        native = frappe.get_doc(_QUOTE, name, for_update=True)
        if digest(receipt["offer"]) != digest(offer) or not _quote_native_matches(native, request, binding, receipt):
            frappe.throw("This supplier already offered different terms or the quotation requires integrity review")
        return dict(quotation=name, docstatus=native.docstatus, created=False)
    on = today()
    if offer["valid_until"] < on:
        frappe.throw("Offer validity must include the submission date")

    buyer_row = request.items[0]
    conversion_rate = _conversion_rate(request.company, on)
    quote = frappe.get_doc(dict(
        doctype=_QUOTE, supplier=supplier, company=request.company, project=binding["project"],
        currency="USD", conversion_rate=conversion_rate,
        transaction_date=on, valid_till=offer["valid_until"], ignore_pricing_rule=1,
        disable_rounded_total=1, quotation_number=offer["supplier_reference"], terms=_terms(offer),
        items=[dict(
            item_code=buyer_row.item_code, item_name=buyer_row.item_name, description=buyer_row.description,
            qty=float(offer["quantity"]), rate=float(offer["rate_usd"]), stock_uom=buyer_row.stock_uom,
            uom=buyer_row.uom, conversion_factor=1, request_for_quotation=rfq,
            request_for_quotation_item=buyer_row.name, project=binding["project"],
        )],
    ))
    quote.flags.osr_sourcing_token = _WRITE_TOKEN
    account = frappe.session.user
    quote.flags.osr_supplier_account = account
    with _atomic("osr_sourcing_offer"):
        # Core ERP validation reads Item, Account and company settings reserved to
        # Desk users. Validate only this server-built record under a scoped user.
        user_perms = frappe.local.user_perms
        try:
            frappe.session.user = "Administrator"
            frappe.local.user_perms = None
            quote.insert(set_name=name)
        finally:
            frappe.session.user = account
            frappe.local.user_perms = user_perms
        receipt = dict(rfq=rfq, supplier=supplier, account=account, offer=offer, recorded_on=on,
                       conversion_rate=conversion_rate)
        if not _quote_native_matches(frappe.get_doc(_QUOTE, name), request, binding, receipt):
            frappe.throw("Native quotation changed the quoted quantity, price or currency precision")
        _save_record("offer", name, receipt)
    return dict(quotation=name, docstatus=quote.docstatus, created=True)


def comparison_inputs(rfq, as_of=None):
    if not isinstance(rfq, str) or not rfq.startswith(_RFQ_PREFIX):
        frappe.throw("Select an OSR sourcing RFQ")
    request = frappe.get_doc(_RFQ, rfq)
    request.check_permission("read")
    frappe.has_permission(_QUOTE, ptype="read", throw=True)
    binding = _read_record("rfq", rfq)
    if not binding:
        frappe.throw("Select an OSR sourcing RFQ with its staged scope")
    _desk_project(binding["project"])
    if not _rfq_native_matches(request, binding):
        frappe.throw("Native RFQ requires integrity review")
    packet = _staged_estimate(binding["project"], binding["scope"]["evaluation_id"])
    if digest(packet) != binding["estimate_sha256"]:
        frappe.throw("RFQ estimate requires integrity review")
    on = _input(calendar_date, as_of) if as_of else date.fromisoformat(today())
    offers = []
    suppliers = []
    attributed = set()
    for supplier in binding["suppliers"]:
        name = _quote_name(rfq, supplier)
        receipt = _read_record("offer", name)
        trace = dict(supplier=supplier, status="pending" if request.docstatus == 1 else "unissued")
        if packet.get("schema") == "baghdad-airport-erpnext-estimate/1":
            trace.update(project=binding["project"], rfq=rfq, lot_id=binding["scope"]["lot_id"])
        suppliers.append(trace)
        if not receipt:
            continue
        attributed.add(name)
        quote = frappe.get_doc(_QUOTE, name)
        quote.check_permission("read")
        trace.update(quotation=name, recorded_on=receipt["recorded_on"])
        if not _input(_quote_native_matches, quote, request, binding, receipt):
            trace["status"] = "integrity-hold"
        elif request.docstatus != 1 or quote.docstatus == 2 or quote.status in ("Cancelled", "Stopped"):
            trace["status"] = "inactive"
        elif on < date.fromisoformat(receipt["recorded_on"]):
            trace["status"] = "not-yet-received"
        elif on > date.fromisoformat(receipt["offer"]["valid_until"]):
            trace["status"] = "expired"
        else:
            trace["status"] = "received"
            trace["valid_until"] = receipt["offer"]["valid_until"]
            trace["lead_time_days"] = receipt["offer"]["lead_time_days"]
            trace["warranty"] = receipt["offer"]["warranty"]
            earliest = date.fromisoformat(receipt["recorded_on"]) + timedelta(days=trace["lead_time_days"])
            trace["earliest_delivery_if_started_on_reply"] = earliest.isoformat()
            trace["required_on"] = binding["required_on"]
            offer = receipt["offer"]
            row = {key: offer[key] for key in (
                "candidate_id", "evaluation_id", "lot_id", "unit", "currency",
                "annual_upkeep_usd", "renewals_usd", "exclusions",
            )}
            row.update(supplier=supplier, quotation=name, evidence_kind="supplier-offer",
                       quantity=quote.items[0].qty, direct_usd=quote.items[0].amount)
            offers.append(row)
    linked = set(frappe.get_all("Supplier Quotation Item", filters={
        "request_for_quotation": rfq, "parenttype": _QUOTE, "parentfield": "items",
    }, pluck="parent"))
    unattributed = []
    for name in sorted(linked - attributed):
        doc = frappe.get_doc(_QUOTE, name)
        if doc.has_permission("read"):
            unattributed.append(dict(quotation=name, reason="No authenticated supplier offer receipt"))
    return dict(packet=packet, lot_id=binding["scope"]["lot_id"], offers=offers,
                suppliers=suppliers, unattributed_quotations=unattributed, as_of=on.isoformat(),
                rfq=rfq, rfq_docstatus=int(request.docstatus), project=binding["project"])


@frappe.whitelist(methods=["GET"])
def compare_rfq(rfq, as_of=None):
    from osr_erpnext.sourcing_comparison import compare_lot

    inputs = comparison_inputs(rfq, as_of)
    result = _input(compare_lot, inputs.pop("packet"), inputs["lot_id"], inputs.pop("offers"))
    return dict(inputs, comparison=result)
