"""Native, permission-checked field evidence receipt; Task/release state is unchanged."""
import base64
import json
import time
from datetime import datetime
from html import escape

import frappe
from osr_erpnext.field_contract import digest, verify


def install():
    if frappe.db.exists('DocType', 'OSR Field Execution'): return
    frappe.get_doc(dict(doctype='DocType', name='OSR Field Execution', module='OpenSourceRail', custom=1,
        autoname='field:event_key', track_changes=1,
        fields=[dict(fieldname=name, label=label, fieldtype=kind, options=options, reqd=1,
                     read_only=1, unique=1 if name == 'event_key' else 0)
                for name, label, kind, options in [
                    ('event_key', 'Event identity', 'Data', None), ('event_sha256', 'Event checksum', 'Data', None),
                    ('task', 'Task', 'Link', 'Task'), ('asset', 'Asset', 'Link', 'Asset'),
                    ('employee', 'Technician', 'Link', 'Employee'), ('project', 'Project', 'Link', 'Project'), ('company', 'Company', 'Link', 'Company'),
                    ('status', 'Evidence state', 'Data', None), ('packet', 'Controlled evidence', 'Code', 'JSON')]],
        permissions=[dict(role='System Manager', read=1, create=1), dict(role='Projects User', read=1, create=1)]
    )).insert(ignore_permissions=True)


@frappe.whitelist(methods=['POST'])
def ingest(packet):
    packet = frappe.parse_json(packet)
    try: verify(packet)
    except (ValueError, TypeError, KeyError) as exc: frappe.throw('Invalid field evidence: ' + str(exc))
    from osr_erpnext.integration import _scope
    project = _scope(packet['city'], packet['environment'], packet['project'], packet['company'])
    work = packet['work']; key = digest([packet['city'], packet['environment'], packet['event']['id']])
    # Serialize retries and competing evidence on this work's native Task.
    frappe.db.sql('SELECT name FROM `tabTask` WHERE name=%s FOR UPDATE', (work['erp_task'],))
    prior = frappe.db.get_value('OSR Field Execution', {'event_key': key}, ['name', 'event_sha256'], as_dict=True)
    if prior:
        doc = frappe.get_doc('OSR Field Execution', prior.name); doc.check_permission('read')
        if prior.event_sha256 != packet['idempotency_sha256']: frappe.throw('Event identity reused with changed evidence')
        return dict(execution=prior.name, duplicate=True, status='performed-awaiting-inspection', operational_release=False)
    task = frappe.get_doc('Task', work['erp_task']); task.check_permission('write')
    asset = frappe.get_doc('Asset', work['erp_asset']); asset.check_permission('read')
    if task.project != project.name or task.status != 'Working' or str(task.modified) != work['native_modified']:
        frappe.throw('Task revision, project or active execution changed while device was offline')
    if asset.company != project.company or asset.custom_osr_asset_id != work['asset_id'] or asset.docstatus != 1 or asset.status in {'Sold', 'Scrapped', 'Capitalized'}:
        frappe.throw('Current native Asset binding is not available for field work')
    if task.custom_osr_asset_id != work['asset_id']:
        frappe.throw('Task does not target this railway asset')
    if task.get('custom_osr_construction_work_method_revision') != work['method_revision']:
        frappe.throw('Current native method revision differs from offline pack')
    expiry = datetime.fromisoformat(work['expires_at'].replace('Z', '+00:00'))
    if expiry.tzinfo is None or expiry.timestamp() <= time.time(): frappe.throw('Offline work pack has expired')
    if task.custom_osr_revision != work['engineering_revision']:
        frappe.throw('Native engineering revision differs from offline pack')
    technician = (frappe.conf.get('osr_field_technicians') or {}).get(packet['actor'])
    if not technician: frappe.throw('Technician identity is not provisioned', frappe.PermissionError)
    employee = frappe.get_doc('Employee', technician['employee']); employee.check_permission('read')
    if employee.status != 'Active' or employee.company != project.company or employee.user_id != technician['user']:
        frappe.throw('Technician native employment/user binding changed')
    if not frappe.db.exists('ToDo', {'reference_type': 'Task', 'reference_name': task.name, 'allocated_to': technician['user'], 'status': 'Open'}):
        frappe.throw('Technician is no longer assigned to this Task')
    if work['physical_serial'] and asset.get('serial_no') != work['physical_serial']:
        frappe.throw('Installed serial changed while device was offline')
    from osr_erpnext.construction_execution import validate_task
    task.load_doc_before_save(raise_exception=True)  # Current native history, not a fabricated work-start transition.
    validate_task(task)  # Re-resolve native allocation, people, permits and resource revocation.
    doc = frappe.get_doc(dict(doctype='OSR Field Execution', event_key=key,
        event_sha256=packet['idempotency_sha256'], task=task.name, asset=asset.name,
        employee=employee.name, project=project.name, company=project.company, status='performed-awaiting-inspection',
        packet=json.dumps(packet, sort_keys=True, allow_nan=False)))
    previous_flag = getattr(frappe.flags, 'osr_field_intake', False)
    try:
        frappe.flags.osr_field_intake = True
        doc.insert()
    finally:
        frappe.flags.osr_field_intake = previous_flag
    for photo in packet['event'].get('photos', []):
        suffix = '.png' if photo['mime'] == 'image/png' else '.jpg'
        frappe.get_doc(dict(doctype='File', file_name=photo['sha256'] + suffix, is_private=1,
            attached_to_doctype=doc.doctype, attached_to_name=doc.name,
            content=base64.b64decode(photo['base64'], validate=True))).insert()
    task.add_comment('Comment', 'Offline field evidence received: ' + escape(doc.name) + '; independent inspection and handback required.')
    return dict(execution=doc.name, duplicate=False, status=doc.status,
                task_status=task.status, operational_release=False)


def validate_receipt(doc, method=None):
    """Generic REST/Desk writes cannot forge or alter an intake receipt."""
    if not getattr(frappe.flags, 'osr_field_intake', False) or not doc.is_new():
        frappe.throw('Field receipts are immutable and created only through controlled intake', frappe.PermissionError)
