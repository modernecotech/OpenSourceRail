"""Attested, idempotent and draft-only ERP intake for the AI executive council."""
import json

import frappe

from osr_erpnext.executive_contract import verify


def _create_draft(project, decision_id, action, component, parameters):
    if parameters.get('project') != project.name:
        frappe.throw('Executive draft targets another ERP project', frappe.PermissionError)
    if component == 'material-request':
        from osr_erpnext.procurement import create_material_request, source_task
        _, source_project, _ = source_task(parameters['task'])
        if source_project.name != project.name:
            frappe.throw('Procurement task belongs to another ERP project', frappe.PermissionError)
        values = {key: parameters[key] for key in
                  ('task', 'requirement_id', 'item_code', 'quantity', 'schedule_date', 'warehouse')}
        return {'doctype': 'Material Request', **create_material_request(**values)}
    if set(parameters) != {'project', 'key', 'inputs'} or not isinstance(parameters['inputs'], dict):
        frappe.throw('Executive component draft parameters are invalid')
    from osr_erpnext.components import preview, apply
    plan = preview(project.name, component, parameters['key'], parameters['inputs'])
    result = apply(project.name, component, parameters['key'], parameters['inputs'], plan['fingerprint'])
    return {**result, 'fingerprint': plan['fingerprint']}


@frappe.whitelist(methods=['POST'])
def ingest_draft(packet):
    """Verify a council decision and create exactly one unsubmitted native draft."""
    packet = frappe.parse_json(packet)
    try:
        verified = verify(packet, frappe.conf.get('osr_executive_attestation') or {})
    except (TypeError, ValueError) as exc:
        frappe.throw(str(exc), frappe.PermissionError)
    proposal, parameters = verified['proposal'], packet['parameters']
    project_name = parameters.get('project') if isinstance(parameters, dict) else None
    if not isinstance(project_name, str):
        frappe.throw('Executive draft requires an ERP project')
    project = frappe.get_doc('Project', project_name)
    from osr_erpnext.integration import _scope
    _scope(packet['city'], packet['environment'], project.name, project.company)
    project.check_permission('write')

    # Lock an existing identity before reading it. Native adapters use their own
    # stable identities too, so a lost response cannot create a second draft.
    frappe.db.get_value('OSR Executive Decision', proposal['id'], 'name', for_update=True)
    if frappe.db.exists('OSR Executive Decision', proposal['id']):
        record = frappe.get_doc('OSR Executive Decision', proposal['id']); record.check_permission('read')
        if record.packet_sha256 != verified['packet_sha256']:
            frappe.throw('Executive decision identity was already used with different content')
        target = frappe.get_doc(record.target_doctype, record.target_name); target.check_permission('read')
        return {'decision': record.name, 'doctype': record.target_doctype,
                'name': record.target_name, 'created': False, 'docstatus': target.docstatus,
                'automatic_submission': False}

    target = _create_draft(project, proposal['id'], verified['action_type'],
                           verified['component'], parameters)
    document = frappe.get_doc(target['doctype'], target['name']); document.check_permission('read')
    if document.docstatus != 0:
        frappe.throw('Executive integration may create or reuse only an unsubmitted draft')
    record = frappe.get_doc(dict(doctype='OSR Executive Decision', decision_id=proposal['id'],
        project=project.name, company=project.company, city=packet['city'],
        environment=packet['environment'], action_type=verified['action_type'],
        decision_sha256=verified['decision_sha256'], packet_sha256=verified['packet_sha256'],
        attestation_key_id=verified['key_id'], packet=json.dumps(packet, sort_keys=True),
        target_doctype=document.doctype, target_name=document.name)).insert()
    return {'decision': record.name, 'doctype': document.doctype, 'name': document.name,
            'created': bool(target.get('created')), 'docstatus': document.docstatus,
            'automatic_submission': False}
