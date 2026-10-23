"""Authenticated native pilot workspace; not an equipment commissioning page."""
import frappe
no_cache=1
def get_context(context):
    if frappe.session.user=='Guest':
        frappe.throw('Sign in to the current-maglev pilot workspace',frappe.PermissionError)
    from osr_erpnext.maglev_pilot import snapshot
    context.pilot=snapshot()
    context.no_cache=1
