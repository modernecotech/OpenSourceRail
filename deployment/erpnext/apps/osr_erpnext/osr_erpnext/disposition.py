"""Append-only, independently reviewed disposition plans; no business execution side effects."""
from contextlib import contextmanager
import json
import frappe
from osr_erpnext import disposition_contract as contract
from osr_erpnext.planning import digest

PROPOSAL = 'OSR Revision Disposition'
DECISION = 'OSR Disposition Decision'


def _parse(parser, value):
    try:
        return parser(frappe.parse_json(value))
    except (ValueError, TypeError) as error:
        frappe.throw(str(error))


def _project(name):
    doc = frappe.get_doc('Project', name)
    doc.check_permission('read')
    if not doc.custom_osr_city:
        frappe.throw('An OSR city project is required')
    return doc


def _permission(doctype, action):
    if not frappe.has_permission(doctype, action):
        frappe.throw('Disposition permission required', frappe.PermissionError)


def _reviews(project):
    from osr_erpnext.integration import execution_feedback
    return execution_feedback(project)['revision_reviews']


def _current(project, mapping, required=True):
    row = next((r for r in _reviews(project) if r['mapping']['name'] == mapping), None)
    if not row and required:
        frappe.throw('Reviewed execution mapping is unavailable in this project')
    return row


@contextmanager
def _insert(doctype):
    previous = frappe.flags.get('osr_disposition_insert')
    frappe.flags.osr_disposition_insert = doctype
    try:
        yield
    finally:
        frappe.flags.osr_disposition_insert = previous


def validate(doc, method=None):
    if not doc.is_new() or frappe.flags.get('osr_disposition_insert') != doc.doctype:
        frappe.throw('Disposition records are append-only; use the reviewed project workflow')


def prevent_delete(doc, method=None):
    frappe.throw('Disposition history cannot be deleted')


@frappe.whitelist(methods=['GET'])
def catalogue(project):
    p = _project(project)
    _permission(PROPOSAL, 'read')
    reviews = _reviews(p.name)
    return dict(actions=contract.ACTIONS, reviews=[dict(mapping=r['mapping'], sha256=r['sha256'],
        warnings=r['warnings'], targets=contract.targets(r)) for r in reviews],
        dispositions=feedback(p, reviews), can_propose=bool(frappe.has_permission(PROPOSAL, 'create')),
        can_review=bool(frappe.has_permission(DECISION, 'create')))


@frappe.whitelist(methods=['POST'])
def preview(project, proposal):
    _permission(PROPOSAL, 'create')
    p = _project(project)
    request = _parse(contract.proposal, proposal)
    user = frappe.get_doc('User', request['responsible'])
    if (not user.enabled or user.user_type != 'System User' or
            not frappe.has_permission('Project', 'read', doc=p, user=user.name) or
            not frappe.has_permission(PROPOSAL, 'read', user=user.name)):
        frappe.throw('Responsible person must be an enabled ERP user with project and disposition access')
    try:
        return contract.plan(_current(p.name, request['mapping']), request, frappe.session.user)
    except ValueError as error:
        frappe.throw(str(error))


@frappe.whitelist(methods=['POST'])
def record(project, proposal, fingerprint):
    _permission(PROPOSAL, 'create')
    p = _project(project)
    request = _parse(contract.proposal, proposal)
    key = digest([p.name, request['key']])
    request_hash = digest(dict(proposal=request, proposer=frappe.session.user))
    # Serialises repeat submissions in this project; it does not lock native production.
    frappe.db.sql('SELECT name FROM `tabProject` WHERE name=%s FOR UPDATE', p.name)
    if frappe.db.get_value(PROPOSAL, key, 'name', for_update=True):
        existing = frappe.get_doc(PROPOSAL, key, for_update=True); existing.check_permission('read')
        if existing.request_sha256 != request_hash:
            frappe.throw('Proposal key already used with different content or proposer')
        return dict(name=existing.name, created=False, automatic_execution=False)
    reviewed = preview(project, request)
    if reviewed['fingerprint'] != fingerprint:
        frappe.throw('ERP exposure or proposal changed after preview; review again')
    with _insert(PROPOSAL):
        doc = frappe.get_doc(dict(doctype=PROPOSAL, disposition_key=key, project=p.name,
            company=p.company, city=p.custom_osr_city, execution_mapping=request['mapping'],
            responsible=request['responsible'], due_date=request['due_date'], proposer=frappe.session.user,
            exposure_sha256=reviewed['exposure_sha256'], request_sha256=request_hash,
            proposal=json.dumps(request, sort_keys=True), reviewed_plan=json.dumps(reviewed, sort_keys=True))).insert()
    from frappe.desk.form.assign_to import add
    add(dict(doctype=PROPOSAL, name=doc.name, assign_to=[request['responsible']],
             date=request['due_date'], description='Review disposition plan; native business execution remains separate.'))
    return dict(name=doc.name, created=True, automatic_execution=False)


def _source(name):
    doc = frappe.get_doc(PROPOSAL, name); doc.check_permission('read')
    _project(doc.project)
    return doc


@frappe.whitelist(methods=['POST'])
def preview_decision(disposition, decision):
    _permission(DECISION, 'create')
    doc = _source(disposition)
    request = _parse(contract.decision, decision)
    if frappe.session.user in {doc.proposer, doc.responsible}:
        frappe.throw('Reviewer must differ from proposer and responsible person')
    current = _current(doc.project, doc.execution_mapping, required=request['outcome'] == 'Endorse plan')
    if request['outcome'] == 'Endorse plan' and (current['sha256'] != doc.exposure_sha256 or current['warnings']):
        frappe.throw('Exposure is stale or incomplete; create and review a fresh proposal')
    result = dict(disposition=doc.name, proposal_sha256=doc.request_sha256, decision=request,
        reviewer=frappe.session.user, current_exposure_sha256=current['sha256'] if current else None,
        original_target=frappe.parse_json(doc.reviewed_plan)['target_record'],
        original_exposure_sha256=doc.exposure_sha256, automatic_execution=False,
        railway_release_authorised=False)
    result['fingerprint'] = digest(result)
    return result


@frappe.whitelist(methods=['POST'])
def record_decision(disposition, decision, fingerprint):
    _permission(DECISION, 'create')
    doc = _source(disposition)
    request = _parse(contract.decision, decision)
    request_hash = digest(dict(decision=request, reviewer=frappe.session.user))
    frappe.db.sql('SELECT name FROM `tabOSR Revision Disposition` WHERE name=%s FOR UPDATE', doc.name)
    if frappe.db.get_value(DECISION, doc.name, 'name', for_update=True):
        existing = frappe.get_doc(DECISION, doc.name, for_update=True); existing.check_permission('read')
        if existing.request_sha256 != request_hash:
            frappe.throw('An immutable decision already exists for this proposal')
        return dict(name=existing.name, created=False, automatic_execution=False)
    reviewed = preview_decision(disposition, request)
    if reviewed['fingerprint'] != fingerprint:
        frappe.throw('Decision or ERP exposure changed after preview; review again')
    with _insert(DECISION):
        result = frappe.get_doc(dict(doctype=DECISION, disposition=doc.name, project=doc.project,
            company=doc.company, city=doc.city, reviewer=frappe.session.user, outcome=request['outcome'],
            request_sha256=request_hash, reviewed_decision=json.dumps(reviewed, sort_keys=True))).insert()
    return dict(name=result.name, created=True, automatic_execution=False)


def feedback(project, reviews):
    if not frappe.db.exists('DocType', PROPOSAL) or not frappe.has_permission(PROPOSAL, 'read'):
        return []
    current = {r['mapping']['name']: r['sha256'] for r in reviews}
    decisions = {}
    if frappe.has_permission(DECISION, 'read'):
        for row in frappe.get_list(DECISION, filters={'project': project.name, 'company': project.company},
                                  fields=['name'], limit_page_length=0):
            doc = frappe.get_doc(DECISION, row.name); doc.check_permission('read')
            decisions[doc.disposition] = dict(name=doc.name, outcome=doc.outcome,
                reviewer=doc.reviewer, created=str(doc.creation),
                review=frappe.parse_json(doc.reviewed_decision))
    result = []
    for row in frappe.get_list(PROPOSAL, filters={'project': project.name, 'company': project.company},
                              fields=['name'], order_by='creation desc', limit_page_length=0):
        doc = frappe.get_doc(PROPOSAL, row.name); doc.check_permission('read')
        result.append(dict(name=doc.name, project=doc.project, company=doc.company, city=doc.city,
            mapping=doc.execution_mapping, proposal=frappe.parse_json(doc.proposal),
            proposer=doc.proposer, responsible=doc.responsible, due_date=str(doc.due_date),
            created=str(doc.creation), exposure_sha256=doc.exposure_sha256,
            current=current.get(doc.execution_mapping) == doc.exposure_sha256,
            decision=decisions.get(doc.name), automatic_execution=False, execution_verified=False))
    return result
