"""Convert explicit operator mappings into native, unsubmitted Material Requests."""
import html
import json

import frappe
from osr_erpnext.automation_rules import procurement_input
from osr_erpnext.planning import digest


def source_task(name, write=False):
    task = frappe.get_doc('Task', name)
    task.check_permission('read')
    if task.custom_osr_kind != 'procurement' or not task.project:
        frappe.throw('Select an OSR procurement task')
    project = frappe.get_doc('Project', task.project)
    project.check_permission('write' if write else 'read')
    if not project.custom_osr_package_sha256 or task.custom_osr_city != project.custom_osr_city:
        frappe.throw('Task must belong to an applied city operating baseline')
    source = json.loads(task.custom_osr_source_record)
    if digest(source) != task.custom_osr_source_sha256:
        frappe.throw('Procurement source evidence has changed')
    return task, project, source['requirements']


@frappe.whitelist(methods=['GET'])
def candidates(task, search='', offset=0):
    _, project, rows = source_task(task)
    query = str(search).strip().casefold()
    rows = [r for r in rows if query in ' '.join(str(r.get(k, '')) for k in
            ['purchase_order_id', 'description', 'asset_id', 'bom_ref']).casefold()]
    start = max(0, int(offset))
    keys = ['purchase_order_id', 'description', 'asset_id', 'quantity_basis', 'required_by_day']
    warehouses = frappe.get_list('Warehouse', filters={'company': project.company,
        'disabled': 0, 'is_group': 0, 'custom_osr_master_key': ['in', city_warehouse_keys(project)]},
        pluck='name', limit_page_length=0) if frappe.has_permission('Warehouse', 'read') else []
    return dict(total=len(rows), offset=start, warehouses=warehouses,
                requirements=[{k: r.get(k) for k in keys} for r in rows[start:start+50]])


def city_warehouse_keys(project):
    config = json.loads(project.custom_osr_config)
    return [digest([project.company, project.custom_osr_city, 'Warehouse', label])
            for label in config['organisation']['warehouses']]


@frappe.whitelist(methods=['POST'])
def create_material_request(task, requirement_id, item_code, quantity, schedule_date, warehouse):
    mapping = procurement_input(requirement_id, item_code, quantity, schedule_date, warehouse)
    task, project, requirements = source_task(task, write=True)
    frappe.has_permission('Material Request', 'create', throw=True)
    matches = [r for r in requirements if r['purchase_order_id'] == requirement_id]
    if len(matches) != 1:
        frappe.throw('Requirement must identify exactly one row in this procurement task')
    requirement = matches[0]
    key = digest([project.name, task.custom_osr_source_key, requirement_id])
    fingerprint = digest(dict(mapping=mapping, source=digest(requirement)))
    existing = frappe.db.get_value('Material Request', {'custom_osr_request_key': key}, 'name')
    if existing:
        doc = frappe.get_doc('Material Request', existing)
        doc.check_permission('read')
        if doc.custom_osr_request_sha256 != fingerprint:
            frappe.throw('This requirement already has a request with different inputs. Review the existing request.')
        return dict(name=doc.name, created=False, docstatus=doc.docstatus)
    item = frappe.get_doc('Item', item_code)
    item.check_permission('read')
    if item.disabled or not item.is_purchase_item:
        frappe.throw('Select an active purchasable Item')
    store = frappe.get_doc('Warehouse', warehouse)
    store.check_permission('read')
    allowed = city_warehouse_keys(project)
    if store.company != project.company or store.is_group or store.disabled or store.custom_osr_master_key not in allowed:
        frappe.throw('Select an enabled warehouse configured for this city and company')
    if frappe.utils.getdate(schedule_date) < frappe.utils.getdate():
        frappe.throw('Required date cannot be in the past')
    doc = frappe.get_doc(dict(doctype='Material Request', material_request_type='Purchase',
        company=project.company, transaction_date=frappe.utils.today(), schedule_date=schedule_date,
        custom_osr_request_key=key, custom_osr_request_sha256=fingerprint,
        custom_osr_procurement_task=task.name, custom_osr_requirement_id=requirement_id,
        custom_osr_requirement_source=json.dumps(requirement, sort_keys=True),
        items=[dict(item_code=item.name, item_name=item.item_name,
            description=html.escape(item.description or item.item_name),
            qty=mapping['quantity'], uom=item.stock_uom, stock_uom=item.stock_uom,
            conversion_factor=1, warehouse=warehouse, schedule_date=schedule_date,
            project=project.name, cost_center=project.cost_center)]))
    doc.insert()
    # Native validation, workflows and subsequent submission remain in ERPNext.
    return dict(name=doc.name, created=True, docstatus=doc.docstatus)
