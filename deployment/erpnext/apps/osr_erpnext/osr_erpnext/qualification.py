"""Reconcile the reviewed Baghdad qualification drafts into ordinary ERPNext Tasks.

Run with bench execute osr_erpnext.qualification.import_tasks. Preview is default;
apply is a local authorized import, never evidence acceptance or owner assignment.
"""
from pathlib import Path
import json


def reconcile_tasks(frappe, payload, apply=False):
    if payload.get('doctype')!='Task' or payload.get('status')!='draft-import-package-not-live-records':
        raise ValueError('Unknown qualification import schema')
    results=[]
    for row in payload['tasks']:
        if row['status']!='Open' or not row['subject'].startswith('BAG-EVID-'):
            raise ValueError('Qualification imports must be open evidence drafts')
        existing=frappe.get_all('Task',filters={'subject':row['subject']},pluck='name')
        if len(existing)>1:
            raise ValueError('Duplicate qualification subjects require manual reconciliation')
        action='update-description' if existing else 'create-open-task'
        name=existing[0] if existing else None
        if apply:
            if existing:
                doc=frappe.get_doc('Task',name)
                # Keep assignment, project, dates, priority and operator-managed
                # status. Neither refresh nor accepted evidence completes Task.
                doc.description=row['description'];doc.save()
            else:
                doc=frappe.get_doc(dict(doctype='Task',**row));doc.insert();name=doc.name
        results.append(dict(subject=row['subject'],task=name,action=action,applied=apply))
    return dict(tasks=results,applied=apply,evidence_accepted=False,operational_release=False)


def import_tasks(package_path=None, apply=False):
    import frappe
    if package_path is None:
        package_path=frappe.conf.get('osr_repo_path')
        if not package_path:
            raise ValueError('Supply package_path or configure osr_repo_path')
        package_path=Path(package_path)/'cities/catalogue/west-asia/Iraq/Baghdad/engineering/qualification/erpnext-tasks.json'
    # Bench passes booleans through kwargs; never treat the string "false" as true.
    if not isinstance(apply,bool):
        raise ValueError('apply must be a boolean')
    result=reconcile_tasks(frappe,json.loads(Path(package_path).read_text()),apply)
    if apply:frappe.db.commit()
    return result
