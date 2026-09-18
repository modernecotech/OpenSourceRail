"""Read native outcomes and append independent verification; never execute an ERP action."""
import json
import frappe
from osr_erpnext import disposition as plans, outcome_contract as contract, outcome_evidence as evidence
from osr_erpnext.planning import digest

DOCTYPE = 'OSR Disposition Execution'


def _decision(name):
    doc = frappe.get_doc(plans.DECISION, name); doc.check_permission('read')
    return dict(name=doc.name, outcome=doc.outcome, reviewer=doc.reviewer, created=str(doc.creation),
                request_sha256=doc.request_sha256)


def observation(source, current, decision, selection=None):
    proposal = frappe.parse_json(source.proposal)
    original = frappe.parse_json(source.reviewed_plan)
    if not decision or decision['outcome'] != 'Endorse plan':
        raise ValueError('An independently endorsed disposition plan is required')
    decision = {k: decision[k] for k in ['name', 'outcome', 'reviewer', 'created', 'request_sha256']}
    if not current:
        raise ValueError('Current revision exposure is unavailable')
    action = proposal['action']
    if action not in contract.SUPPORTED:
        raise ValueError('This action has no native outcome verifier')
    selection = contract.selected_records(action, selection or {})
    doctype = contract.SUPPORTED[action] or {'purchase-line': 'Purchase Order', 'work-order': 'Work Order'}[proposal['target']['kind']]
    doc = frappe.get_doc(doctype, proposal['target']['document']); doc.check_permission('read')
    project = plans._project(source.project)
    if project.company != source.company or project.custom_osr_city != source.city:
        raise ValueError('Project scope changed since the proposal')
    native = dict(doctype=doctype, name=doc.name, company=doc.company, project=doc.get('project'),
                  docstatus=doc.docstatus, status=doc.get('status'), modified=str(doc.modified), modified_by=doc.modified_by)
    if doctype == 'Purchase Order':
        selected = next((r for r in doc.items if r.name == proposal['target'].get('line')), None)
        if not selected or (selected.get('project') or doc.get('project')) != source.project:
            raise ValueError('Purchase line no longer belongs to this project')
        native['project'] = source.project
        native['lines'] = [dict(line=r.name, item=r.item_code, qty=r.qty, received_qty=r.received_qty, uom=r.uom)
                           for r in doc.items if (r.get('project') or doc.get('project')) == source.project]
    if doctype == 'Stock Entry':
        native = evidence.stock(doc, source.project)
    additional = evidence.collect(action, doc, native, selection)
    snapshot = original.get('exposure_snapshot')
    if not snapshot or snapshot.get('sha256') != source.exposure_sha256:
        raise ValueError('Proposal predates full exposure capture; create a new reviewed proposal')
    status = contract.verify(snapshot, current, proposal, native, decision['created'], additional)
    result = dict(disposition=source.name, proposal_sha256=source.request_sha256, decision=decision,
                  native=native, current_exposure_sha256=current['sha256'], status=status,
                  railway_release_authorised=False, automatic_execution=False)
    if additional:
        result['evidence'] = additional
    result['sha256'] = digest(result)
    return result


@frappe.whitelist(methods=['POST'])
def preview(disposition, verification):
    plans._permission(DOCTYPE, 'create')
    source = plans._source(disposition)
    request = plans._parse(contract.request, verification)
    decision = _decision(source.name)
    try:
        observed = observation(source, plans._current(source.project, source.execution_mapping), decision, request.get('records'))
    except ValueError as error:
        frappe.throw(str(error))
    contributors = {source.proposer, source.responsible, observed['native']['modified_by']}
    def collect_actors(value):
        if isinstance(value, dict):
            contributors.update(value.get(k) for k in ['modified_by', 'inspected_by'] if value.get(k))
            for row in value.values(): collect_actors(row)
        elif isinstance(value, list):
            for row in value: collect_actors(row)
    collect_actors(observed.get('evidence', {}))
    if frappe.session.user in contributors:
        frappe.throw('Verifier must differ from proposer, responsible person and native evidence contributors')
    result = dict(disposition=source.name, verification=request, verifier=frappe.session.user,
                  observation=observed, automatic_execution=False, railway_release_authorised=False)
    result['fingerprint'] = digest(result)
    return result


@frappe.whitelist(methods=['POST'])
def record(disposition, verification, fingerprint):
    plans._permission(DOCTYPE, 'create')
    source = plans._source(disposition)
    request = plans._parse(contract.request, verification)
    identity = digest([source.name, request['key']])
    request_hash = digest(dict(verification=request, verifier=frappe.session.user))
    frappe.db.sql('SELECT name FROM `tabOSR Revision Disposition` WHERE name=%s FOR UPDATE', source.name)
    if frappe.db.get_value(DOCTYPE, identity, 'name', for_update=True):
        existing = frappe.get_doc(DOCTYPE, identity, for_update=True); existing.check_permission('read')
        if existing.request_sha256 != request_hash:
            frappe.throw('Verification key already used with different content or verifier')
        return dict(name=existing.name, created=False, automatic_execution=False)
    checked = preview(disposition, request)
    if checked['fingerprint'] != fingerprint:
        frappe.throw('Native outcome or verification changed after preview; review again')
    with plans._insert(DOCTYPE):
        doc = frappe.get_doc(dict(doctype=DOCTYPE, verification_key=identity, disposition=source.name,
            project=source.project, company=source.company, city=source.city, verifier=frappe.session.user,
            request_sha256=request_hash, observation_sha256=checked['observation']['sha256'],
            reviewed_verification=json.dumps(checked, sort_keys=True))).insert()
    return dict(name=doc.name, created=True, automatic_execution=False)


def records(project):
    if not frappe.db.exists('DocType', DOCTYPE) or not frappe.has_permission(DOCTYPE, 'read'):
        return {}
    result = {}
    for row in frappe.get_list(DOCTYPE, filters={'project': project.name, 'company': project.company},
            fields=['name'], order_by='creation desc, name desc', limit_page_length=0):
        doc = frappe.get_doc(DOCTYPE, row.name); doc.check_permission('read')
        result.setdefault(doc.disposition, []).append(doc)
    return result


def feedback(source, current, decision, history):
    if not history:
        return None
    latest = history[0]
    result = dict(name=latest.name, verifier=latest.verifier, observed_at=str(latest.creation),
                  current=False, status='Verification stale', history=[dict(name=r.name,
                  verifier=r.verifier, observed_at=str(r.creation)) for r in history])
    try:
        if not decision or not current or current.get('warnings'):
            result['status'] = 'Verification unavailable'
            return result
        saved = frappe.parse_json(latest.reviewed_verification)
        observed = observation(source, current, decision, saved['verification'].get('records'))
        result['current'] = observed['sha256'] == latest.observation_sha256
        if result['current']:
            result['status'] = observed['status']
        result['recorded_status'] = saved['observation']['status']
    except (frappe.PermissionError, frappe.DoesNotExistError):
        result['status'] = 'Verification unavailable'
    except ValueError:
        pass
    return result
