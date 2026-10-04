"""Read-only administrative eligibility preview from controlled native records.

No assignment, work start, permit, competence or railway release is granted.
Use this same preview again at task start; actual authority remains human-owned.
"""
import json
from datetime import datetime, timezone
from osr_erpnext.workforce_rules import assignment_eligibility

def administration_readiness():
    """Read local schemas/permissions only; none of these proves authorisation."""
    import frappe
    if not set(frappe.get_roles()).intersection({'HR Manager','System Manager'}):
        frappe.throw('HR Manager or System Manager role required')
    types=['Staffing Plan','Job Requisition','Job Opening','Job Applicant','Interview','Job Offer','Employee','Employee Onboarding',
        'Training Program','Training Event','Training Result','Employee Skill Map','Shift Assignment','Work Order','Job Card','Asset Maintenance','Asset Repair','Task','File']
    rows=[]
    for name in types:
        exists=bool(frappe.db.exists('DocType',name))
        rows.append(dict(doctype=name,schema_exists=exists,caller_can_read=bool(exists and frappe.has_permission(name,'read'))))
    return dict(record_types=rows,read_only=True,appointments_verified=False,authorisations_verified=False,operational_release=False)

def preview_assignment(project, task, employee, authorisation_file, at_time=None):
    """Bench-callable observation pilot; no public unauthenticated endpoint."""
    import frappe
    if not set(frappe.get_roles()).intersection({'HR Manager','System Manager'}):
        frappe.throw('HR Manager or System Manager role required for eligibility preview')
    def read(kind,name):
        doc=frappe.get_doc(kind,name)
        doc.check_permission('read')
        return doc
    p=read('Project',project);t=read('Task',task);person=read('Employee',employee)
    record=read('File',authorisation_file)
    if not p.custom_osr_package_sha256 or t.project!=p.name or person.company!=p.company or t.status in {'Cancelled','Completed'}:
        frappe.throw('Task, active employee and controlled baseline must belong to this project/company')
    if person.status!='Active' or not record.is_private or record.attached_to_doctype!='Employee' or record.attached_to_name!=person.name:
        frappe.throw('Use an active employee and their private controlled authorisation attachment')
    packet=json.loads(record.get_content())
    if packet.get('project_revision')!=p.custom_osr_package_sha256 or packet.get('task_reference')!=t.name or packet.get('worker',{}).get('native_employee')!=person.name:
        frappe.throw('Authorisation packet does not match this baseline, task and employee')
    when=at_time or datetime.now(timezone.utc).isoformat()
    result=assignment_eligibility(packet['worker'],packet['task'],packet['resources'],when)
    result.update(project=p.name,task=t.name,record=record.name,read_only=True,
        actual_assignment_created=False,live_start_check=at_time is None,
        boundary='Administrative evidence preview; human work/permit/release authority still required')
    return result
