"""Render buying or supplier views using the same permissions as the sourcing API."""
import frappe
from osr_erpnext import sourcing

no_cache = 1


def get_context(context):
    context.no_cache = 1
    if frappe.session.user == "Guest":
        frappe.throw("Sign in to the Airport sourcing portal", frappe.PermissionError)
    context.actor = frappe.session.user
    query = frappe.form_dict
    offset = max(0, frappe.utils.cint(query.get("offset")))
    context.offset = offset
    context.rfq = query.get("rfq") or ""
    context.buyer = "Desk User" in frappe.get_roles()
    if not context.buyer:
        context.requests = sourcing.list_requests(offset=offset)
        if context.rfq:
            context.enquiry = sourcing.get_request(context.rfq)
        return

    frappe.has_permission("Request for Quotation", "read", throw=True)
    project = query.get("project")
    if not project:
        matches = frappe.get_list("Project", filters={"project_name": "Baghdad Airport opening procurement"},
                                  pluck="name", limit_page_length=2)
        project = matches[0] if len(matches) == 1 else ""
    context.project = project
    if not project:
        return
    context.editions = sourcing.list_estimates(project)
    context.requests = sourcing.list_buyer_requests(project, offset=offset)
    edition = query.get("evaluation_id") or (context.editions[0]["evaluation_id"] if context.editions else "")
    context.edition = edition
    if edition:
        from osr_erpnext.sourcing_prices import lot_item_code

        packet = sourcing.get_estimate(project, edition)
        context.candidate_id = packet["candidate_id"]
        context.lots = packet["lots"]
        lot_id = query.get("lot") or context.lots[0]["lot_id"]
        context.lot = next((r for r in context.lots if r["lot_id"] == lot_id), None)
        if not context.lot:
            frappe.throw("Select a lot on this estimate edition")
        context.item_code = lot_item_code(project, edition, lot_id)
    if context.rfq:
        context.review = sourcing.compare_rfq(context.rfq)
        if context.review["project"] != project:
            frappe.throw("Select a competition staged on this Project")
        estimate_id = context.review["comparison"]["estimate_evaluation_id"]
        selected_packet = packet if edition and edition == estimate_id else sourcing.get_estimate(project, estimate_id)
        review_lot = next(r for r in selected_packet["lots"] if r["lot_id"] == context.review["lot_id"])
        context.replacement_available = review_lot["inclusion_group"] == "opening-direct"
        if query.get("quotation"):
            from osr_erpnext.sourcing_scenario_api import price_scenario
            context.scenario = price_scenario(project, context.rfq, query.get("quotation"))
