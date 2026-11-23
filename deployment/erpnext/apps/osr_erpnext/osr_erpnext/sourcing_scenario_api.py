"""Buyer-only opening cost sensitivity using a current, attributed ERP quotation."""
import frappe

from osr_erpnext.sourcing import compare_rfq, get_estimate
from osr_erpnext.sourcing_scenario import opening_scenario


@frappe.whitelist(methods=["GET"])
def price_scenario(project, rfq, quotation):
    report = compare_rfq(rfq)
    if report["project"] != project:
        frappe.throw("The RFQ must belong to the requested Project")
    estimate = get_estimate(project, report["comparison"]["estimate_evaluation_id"])
    try:
        return opening_scenario(estimate, [(report, quotation)])
    except ValueError as error:
        frappe.throw(str(error))
