"""Retain city identity when ERPNext's native scheduler creates purchase requests."""
import frappe
from osr_erpnext.procurement import city_warehouse_keys


def assign_city_scope(doc,method=None):
    if doc.material_request_type!='Purchase':return
    for row in doc.items:
        if row.project or not row.item_code or not row.warehouse:continue
        matches=frappe.get_all('Item Reorder',filters={'parent':row.item_code,'warehouse':row.warehouse,
            'custom_osr_component':'replenishment'},pluck='custom_osr_component_project')
        projects={p for p in matches if p}
        if not projects:continue
        if len(projects)!=1:frappe.throw('Ambiguous OSR city replenishment rules; review the Item and warehouse')
        project=frappe.get_doc('Project',next(iter(projects)));project.check_permission('read')
        warehouse_key=frappe.db.get_value('Warehouse',row.warehouse,'custom_osr_master_key')
        if project.company!=doc.company or warehouse_key not in city_warehouse_keys(project):
            frappe.throw('Replenishment rule no longer matches its city company/warehouse')
        row.project=project.name
