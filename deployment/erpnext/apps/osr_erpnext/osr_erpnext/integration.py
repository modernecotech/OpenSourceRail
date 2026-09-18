"""Scoped condition-event ingress and permission-filtered execution feedback."""
import json
import math
from collections import defaultdict
from html import escape

import frappe
from osr_erpnext.planning import digest


def _scope(city, environment, project, company):
    # Provisioned by an administrator in private site_config, never supplied by caller.
    policy = (frappe.conf.get('osr_integration_users') or {}).get(frappe.session.user)
    if not policy or city not in policy['cities'] or environment not in policy['environments']:
        frappe.throw('Integration user scope does not permit this city/environment', frappe.PermissionError)
    doc = frappe.get_doc('Project', project)
    doc.check_permission('read')
    if doc.custom_osr_city != city or doc.company != company or project not in policy['projects']:
        frappe.throw('Condition event project/company mismatch', frappe.PermissionError)
    return doc


@frappe.whitelist(methods=['POST'])
def condition_event(event):
    event = frappe.parse_json(event)
    required = ['event_id', 'incident_id', 'city', 'environment', 'company', 'project', 'asset_id', 'rule', 'condition', 'occurrence']
    if not isinstance(event, dict) or any(not event.get(k) for k in required):
        frappe.throw('Incomplete condition event')
    _scope(event['city'], event['environment'], event['project'], event['company'])
    if event['condition'] not in ('active', 'cleared') or type(event['occurrence']) is not int or event['occurrence'] < 1:
        frappe.throw('Invalid condition occurrence')
    priority = event.get('priority', 'medium')
    if not isinstance(priority, str) or priority not in {'low', 'medium', 'high'}:
        frappe.throw('Condition priority must be low, medium or high')
    if event.get('erp_asset_id'):
        # The narrowly scoped gateway account need not receive broad Asset-module
        # access merely to attach an already reviewed identity to its event.
        asset = frappe.get_doc('Asset', event['erp_asset_id'])
        if asset.company != event['company'] or asset.custom_osr_asset_id != event['asset_id']:
            frappe.throw('ERP Asset identity does not match condition event')
    key = digest([event['company'], event['city'], event['environment'], event['asset_id'], event['rule'], event['incident_id']])
    names = frappe.db.sql('SELECT name FROM `tabIssue` WHERE custom_osr_incident_key=%s FOR UPDATE', (key,))
    if names:
        issue = frappe.get_doc('Issue', names[0][0]); issue.check_permission('write')
    else:
        issue = frappe.new_doc('Issue')
        issue.subject = f"[OSR {event['environment']}] {event['asset_id']} · {event['rule']}"
        issue.priority = priority.title()  # Initial triage only; preserve subsequent native operator changes.
        issue.description = '<p>' + escape(event.get('response', 'Condition requires triage')) + '</p>'
        issue.custom_osr_incident_key = key
        issue.custom_osr_environment = event['environment']
        issue.custom_osr_city = event['city']
        issue.custom_osr_asset_id = event['asset_id']
        issue.custom_osr_erp_asset = event.get('erp_asset_id', '')
        issue.project = event['project']
        issue.custom_osr_condition_history = '[]'
    history = frappe.parse_json(issue.custom_osr_condition_history or '[]')
    known = next((r for r in history if r['event_id'] == event['event_id']), None)
    if known and known['hash'] != digest(event):
        frappe.throw('Event identity reused with changed data')
    if not known:
        history.append({'event_id': event['event_id'], 'hash': digest(event), 'condition': event['condition'],
                        'occurrence': event['occurrence'], 'observed_at': event.get('observed_at')})
        issue.custom_osr_condition_history = json.dumps(history)
        issue.custom_osr_condition = event['condition']
        issue.custom_osr_evidence_path = '/docs/lifecycle/?city=' + event['city'] + '&asset=' + event['asset_id'] + '&environment=' + event['environment']
        issue.save()  # Native permissions, assignment and audit remain active.
    return {'issue': issue.name, 'status': issue.status, 'duplicate': bool(known)}


@frappe.whitelist(methods=['GET'])
def case_status(issue):
    doc = frappe.get_doc('Issue', issue); doc.check_permission('read')
    project = frappe.get_doc('Project', doc.project)
    _scope(doc.custom_osr_city, doc.custom_osr_environment, project.name, project.company)
    return {'issue': doc.name, 'status': doc.status, 'condition': doc.custom_osr_condition, 'assignments': doc.get('_assign')}


def _normalise_repair_proposal(proposal):
    proposal = frappe.parse_json(proposal)
    required = {'schema', 'key', 'failure_date', 'expected_downtime_hours', 'technician',
                'description', 'parts', 'evidence_references'}
    if not isinstance(proposal, dict) or set(proposal) != required or proposal.get('schema') != 'osr-condition-repair/1':
        frappe.throw('Invalid condition repair proposal')
    from osr_erpnext.component_catalogue import instance_key
    key = instance_key(proposal['key'])
    if not isinstance(proposal['failure_date'], str) or not proposal['failure_date'].strip():
        frappe.throw('Repair failure date is required')
    try:
        failure_date = str(frappe.utils.get_datetime(proposal['failure_date']))
        downtime = float(proposal['expected_downtime_hours'])
    except (TypeError, ValueError):
        frappe.throw('Invalid repair date or expected downtime')
    if not math.isfinite(downtime) or downtime <= 0 or downtime > 8760:
        frappe.throw('Expected downtime must be more than zero and no more than one year')
    if not isinstance(proposal['description'], str) or not proposal['description'].strip() or len(proposal['description']) > 10000:
        frappe.throw('Repair description is required and must not exceed 10,000 characters')
    if not isinstance(proposal['technician'], str) or not proposal['technician'].strip():
        frappe.throw('A technician is required')
    references = proposal['evidence_references']
    if (not isinstance(references, list) or len(references) > 100 or
            any(not isinstance(row, str) or not row.strip() or len(row) > 500 for row in references)):
        frappe.throw('Evidence references must be a list of up to 100 non-empty references')
    parts = proposal['parts']
    if not isinstance(parts, list) or len(parts) > 100:
        frappe.throw('Repair parts must be a list of no more than 100 rows')
    cleaned_parts = []
    for row in parts:
        allowed = {'item', 'warehouse', 'quantity', 'serial_and_batch_bundle'}
        if not isinstance(row, dict) or not {'item', 'warehouse', 'quantity'} <= set(row) or set(row) - allowed:
            frappe.throw('Invalid repair part row')
        try:
            quantity = float(row['quantity'])
        except (TypeError, ValueError):
            frappe.throw('Repair part quantity must be a number')
        if not math.isfinite(quantity) or quantity <= 0 or quantity > 1e12:
            frappe.throw('Repair part quantity must be finite and positive')
        cleaned_parts.append(dict(item=str(row['item']), warehouse=str(row['warehouse']), quantity=quantity,
            **({'serial_and_batch_bundle': str(row['serial_and_batch_bundle'])}
               if row.get('serial_and_batch_bundle') else {})))
    return dict(schema=proposal['schema'], key=key, failure_date=failure_date,
        expected_downtime_hours=downtime, technician=proposal['technician'].strip(),
        description=proposal['description'].strip(), parts=cleaned_parts,
        evidence_references=[row.strip() for row in references])


def _repair_identity(issue, proposal):
    return digest([issue.name, proposal['key']])


def _prepare_repair(issue_name, proposal):
    proposal = _normalise_repair_proposal(proposal)
    issue = frappe.get_doc('Issue', issue_name); issue.check_permission('write')
    if not issue.project or not issue.custom_osr_incident_key or not issue.custom_osr_erp_asset:
        frappe.throw('Issue must be a condition case linked to a city project and ERP Asset')
    if issue.status in {'Closed', 'Resolved'}:
        frappe.throw('Reopen the Issue before preparing a repair')
    project = frappe.get_doc('Project', issue.project); project.check_permission('read')
    asset = frappe.get_doc('Asset', issue.custom_osr_erp_asset); asset.check_permission('read')
    if (asset.docstatus != 1 or asset.status in {'Sold', 'Scrapped', 'Capitalized'} or
            asset.company != project.company or asset.custom_osr_asset_id != issue.custom_osr_asset_id or
            project.custom_osr_city != issue.custom_osr_city):
        frappe.throw('Issue, project and commissioned Asset identities do not match')
    frappe.has_permission('Asset Repair', 'create', throw=True)
    from osr_erpnext.components import read, user, warehouse
    technician = user(proposal['technician'], project)
    stock_items, availability = [], []
    for row in proposal['parts']:
        item = read('Item', row['item'], project)
        if not item.is_stock_item:
            frappe.throw('Repair consumption requires stock Items')
        store = warehouse(row['warehouse'], project)
        bin_values = frappe.db.get_value('Bin', {'item_code': item.name, 'warehouse': store},
            ['actual_qty', 'valuation_rate'], as_dict=True) or frappe._dict(actual_qty=0, valuation_rate=0)
        bundle_name = row.get('serial_and_batch_bundle')
        if bundle_name:
            bundle = read('Serial and Batch Bundle', bundle_name, project)
            if (bundle.item_code != item.name or bundle.company != project.company or
                    bundle.warehouse not in (None, '', store) or bundle.is_cancelled or
                    bundle.type_of_transaction != 'Outward' or bundle.voucher_no):
                frappe.throw('Serial/batch selection does not match the repair Item and warehouse')
        stock_items.append(dict(item_code=item.name, warehouse=store,
            consumed_quantity=row['quantity'], valuation_rate=bin_values.valuation_rate or 0,
            serial_and_batch_bundle=bundle_name))
        availability.append(dict(item=item.name, warehouse=store, required_qty=row['quantity'],
            available_qty=bin_values.actual_qty or 0,
            shortage_qty=max(0, row['quantity'] - (bin_values.actual_qty or 0))))
    references = list(proposal['evidence_references'])
    if issue.custom_osr_evidence_path and issue.custom_osr_evidence_path not in references:
        references.append(issue.custom_osr_evidence_path)
    evidence = dict(issue=issue.name, incident=issue.custom_osr_incident_key,
        observed_condition=issue.custom_osr_condition,
        condition_history=frappe.parse_json(issue.custom_osr_condition_history or '[]'),
        references=references, serial_history_authority=issue.custom_osr_evidence_path)
    request_json = json.dumps(proposal, sort_keys=True, separators=(',', ':'))
    identity = _repair_identity(issue, proposal)
    document = dict(doctype='Asset Repair', asset=asset.name, company=project.company,
        project=project.name, failure_date=proposal['failure_date'], repair_status='Pending',
        description='<p>' + escape(proposal['description']).replace('\n', '<br>') + '</p>',
        stock_consumption=bool(stock_items), stock_items=stock_items,
        custom_osr_repair_key=identity, custom_osr_repair_request=request_json,
        custom_osr_issue=issue.name, custom_osr_environment=issue.custom_osr_environment,
        custom_osr_city=issue.custom_osr_city, custom_osr_asset_id=issue.custom_osr_asset_id,
        custom_osr_expected_downtime_hours=proposal['expected_downtime_hours'],
        custom_osr_configuration_evidence=json.dumps(evidence, sort_keys=True),
        custom_osr_handback_required=1)
    fingerprint = digest(dict(request=proposal, issue_modified=str(issue.modified),
        asset=asset.name, asset_item=asset.item_code, project=project.name,
        technician=technician, document=document, availability=availability))
    document['custom_osr_repair_sha256'] = fingerprint
    return dict(issue=issue, project=project, asset=asset, proposal=proposal,
        identity=identity, fingerprint=fingerprint, technician=technician,
        document=document, availability=availability)


@frappe.whitelist(methods=['POST'])
def preview_repair(issue, proposal):
    """Review a condition case transition without creating or submitting repair work."""
    plan = _prepare_repair(issue, proposal)
    return dict(issue=plan['issue'].name, project=plan['project'].name,
        fingerprint=plan['fingerprint'], document=plan['document'],
        availability=plan['availability'], automatic_submission=False,
        automatic_issue_closure=False, automatic_handback=False)


@frappe.whitelist(methods=['POST'])
def apply_repair(issue, proposal, fingerprint):
    """Create one review-bound draft Asset Repair and native technician assignment."""
    normalised = _normalise_repair_proposal(proposal)
    source_issue = frappe.get_doc('Issue', issue); source_issue.check_permission('write')
    identity = _repair_identity(source_issue, normalised)
    frappe.db.get_value('Issue', source_issue.name, 'name', for_update=True)
    existing = frappe.db.get_value('Asset Repair', {'custom_osr_repair_key': identity}, 'name')
    request_json = json.dumps(normalised, sort_keys=True, separators=(',', ':'))
    if existing:
        record = frappe.get_doc('Asset Repair', existing); record.check_permission('read')
        if record.custom_osr_repair_request != request_json or record.custom_osr_repair_sha256 != fingerprint:
            frappe.throw('This Issue repair already exists with different reviewed inputs')
        return dict(doctype=record.doctype, name=record.name, created=False,
            automatic_submission=False, automatic_issue_closure=False, automatic_handback=False)
    plan = _prepare_repair(issue, normalised)
    if plan['fingerprint'] != fingerprint:
        frappe.throw('Issue, Asset, stock or repair inputs changed after preview. Preview again.')
    record = frappe.get_doc(plan['document']).insert()
    from frappe.desk.form.assign_to import add
    add(dict(assign_to=[plan['technician']], doctype=record.doctype, name=record.name,
        description='Condition-driven repair for ' + source_issue.name))
    source_issue.add_comment('Info', 'Reviewed Asset Repair {0} created; railway handback remains independent.'.format(record.name))
    return dict(doctype=record.doctype, name=record.name, created=True,
        automatic_submission=False, automatic_issue_closure=False, automatic_handback=False)


@frappe.whitelist(methods=['GET'])
def repairs_for_issue(issue):
    source = frappe.get_doc('Issue', issue); source.check_permission('read')
    if not frappe.has_permission('Asset Repair', 'read'):
        return []
    return frappe.get_list('Asset Repair', filters={'custom_osr_issue': source.name, 'docstatus': ['!=', 2]},
        fields=['name', 'repair_status', 'docstatus', 'modified'], order_by='modified desc', limit_page_length=0)


def execution_feedback(project):
    """Actual transaction lines, keeping quantities, currency and release separate."""
    p = frappe.get_doc('Project', project); p.check_permission('read')
    result = {'purchase_orders': [], 'receipts': [], 'invoices': [], 'production': [], 'repairs': [],
              'execution_mappings': [], 'visibility': {},
              'engineering_accepted_quantity': None, 'installed_quantity': None,
              'authority': 'Native business transactions; installation and engineering acceptance require OSR evidence'}
    if frappe.has_permission('OSR Execution Mapping', 'read'):
        result['visibility']['OSR Execution Mapping'] = 'visible-to-current-user'
        for row in frappe.get_list('OSR Execution Mapping',
                filters={'company': p.company, 'city': p.custom_osr_city},
                fields=['name', 'component_type', 'engineering_revision', 'engineering_sha256',
                        'erp_item', 'source_package'], order_by='modified desc', limit_page_length=0):
            source = frappe.parse_json(row.source_package)
            item = source.get('item', {}) if isinstance(source, dict) else {}
            result['execution_mappings'].append(dict(name=row.name,
                component_type_id=row.component_type, engineering_revision=row.engineering_revision,
                engineering_sha256=row.engineering_sha256, erp_item_code=row.erp_item,
                production_bom=item.get('production_bom'), uom=item.get('uom'),
                review_reference=(source.get('package', {}).get('mapping', {}).get('review_reference')
                                  if isinstance(source, dict) else None)))
    else:
        result['visibility']['OSR Execution Mapping'] = 'permission-denied'
    for dt, output in [('Purchase Order', 'purchase_orders'), ('Purchase Receipt', 'receipts'), ('Purchase Invoice', 'invoices'), ('Work Order', 'production'), ('Asset Repair', 'repairs')]:
        if not frappe.has_permission(dt, 'read'):
            result['visibility'][dt] = 'permission-denied'; continue
        meta = frappe.get_meta(dt)
        if dt == 'Asset Repair':
            result['visibility'][dt] = 'visible-to-current-user'
            names = frappe.get_list(dt, filters={'company': p.company, 'project': project,
                'docstatus': ['!=', 2]}, fields=['name'], limit_page_length=0)
            for row in names:
                doc = frappe.get_doc(dt, row.name); doc.check_permission('read')
                result[output].append(dict(name=doc.name, issue=doc.custom_osr_issue,
                    asset=doc.asset, osr_asset_id=doc.custom_osr_asset_id,
                    status=doc.repair_status, docstatus=doc.docstatus,
                    failure_date=str(doc.failure_date or ''), completion_date=str(doc.completion_date or ''),
                    expected_downtime_hours=doc.custom_osr_expected_downtime_hours,
                    actual_downtime=doc.downtime, total_repair_cost=doc.total_repair_cost,
                    assignments=frappe.parse_json(doc.get('_assign') or '[]'),
                    parts=[dict(item=item.item_code, warehouse=item.warehouse,
                        consumed_qty=frappe.utils.flt(item.consumed_quantity),
                        valuation_rate=frappe.utils.flt(item.valuation_rate),
                        serial_and_batch_bundle=item.serial_and_batch_bundle) for item in doc.stock_items],
                    configuration_evidence=frappe.parse_json(doc.custom_osr_configuration_evidence or '{}'),
                    railway_handback_authorised=False,
                    railway_handback='required-in-osr' if doc.custom_osr_handback_required else 'invalid'))
            continue
        child = meta.get_field('items')
        filters = [[dt, 'company', '=', p.company], [dt, 'docstatus', '=', 1]]
        names_by_id = {}
        project_filters = []
        if meta.has_field('project'):
            project_filters.append([dt, 'project', '=', project])
        if child and frappe.get_meta(child.options).has_field('project'):
            project_filters.append([child.options, 'project', '=', project])
        if not project_filters:
            result['visibility'][dt] = 'no-project-link'; continue
        for project_filter in project_filters:
            names_by_id.update({r.name: r for r in frappe.get_list(dt, filters=filters + [project_filter], fields=['name'], distinct=True, limit_page_length=0)})
        names = list(names_by_id.values())
        result['visibility'][dt] = 'visible-to-current-user'
        for row in names:
            doc = frappe.get_doc(dt, row.name); doc.check_permission('read')
            if dt == 'Work Order':
                result[output].append(dict(name=doc.name, item=doc.production_item, bom=doc.bom_no,
                    planned_qty=doc.qty, produced_qty=doc.produced_qty, status=doc.status,
                    uom=doc.stock_uom, engineering_accepted_qty=None))
                continue
            for item in doc.get('items') or []:
                if item.get('project') != project:
                    continue
                line = dict(document=doc.name, line=item.name, item=item.item_code, qty=item.qty,
                    uom=item.uom, stock_qty=item.get('stock_qty'), stock_uom=item.get('stock_uom'),
                    amount=item.amount, base_amount=item.base_amount, currency=doc.currency,
                    company_currency=frappe.db.get_value('Company', p.company, 'default_currency'),
                    schedule_date=str(item.get('schedule_date') or ''), supplier=doc.supplier,
                    purchase_order=item.get('purchase_order'), quality_inspection=item.get('quality_inspection'),
                    is_return=bool(doc.get('is_return')))
                if dt == 'Purchase Order':
                    line.update(received_qty=item.received_qty, outstanding_qty=max(0, item.qty-item.received_qty),
                                billed_amount=item.billed_amt, unbilled_order_amount=max(0, item.amount-item.billed_amt),
                                overdue=bool(item.schedule_date and str(item.schedule_date) < frappe.utils.today() and item.qty > item.received_qty))
                result[output].append(line)
    currencies = defaultdict(lambda: {'ordered': 0, 'unbilled_commitment': 0, 'invoiced': 0})
    for row in result['purchase_orders']:
        currencies[row['currency']]['ordered'] += row['amount']
        currencies[row['currency']]['unbilled_commitment'] += row['unbilled_order_amount']
    for row in result['invoices']:
        currencies[row['currency']]['invoiced'] += row['amount']
    result['by_currency'] = dict(currencies)
    result['localisation'] = {'domestic_value_added': None, 'reason': 'Manufacturing-origin and imported-content evidence required; supplier location and payment currency are separate facts'}
    from osr_erpnext.execution_review import execution_reviews
    result['revision_reviews'] = execution_reviews(p, result['execution_mappings'])
    from osr_erpnext.disposition import feedback as disposition_feedback
    result['dispositions'] = disposition_feedback(p, result['revision_reviews'])
    return result


@frappe.whitelist(methods=['POST'])
def preview_execution(project, package):
    """Review native Item/BOM mapping without creating or releasing production."""
    package = frappe.parse_json(package)
    p = frappe.get_doc('Project', project); p.check_permission('read')
    if package.get('schema') != 'osr-execution-proposal/1' or package.get('city') != p.custom_osr_city:
        frappe.throw('Execution package belongs to another city or schema')
    # Same canonical checksum convention as the OSR engineering compiler.
    import hashlib
    calculated = hashlib.sha256(json.dumps({k: v for k, v in package.items() if k != 'sha256'}, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()
    if package.get('sha256') != calculated or not package['mapping'].get('review_reference'):
        frappe.throw('Reviewed execution package checksum required')
    mappings = []
    for entry in package['mapping']['items']:
        item = frappe.get_doc('Item', entry['erp_item_code']); item.check_permission('read')
        if item.disabled or item.stock_uom != entry['uom']:
            frappe.throw('Item disabled or production unit does not match')
        bom = None
        if entry.get('production_bom'):
            bom = frappe.get_doc('BOM', entry['production_bom']); bom.check_permission('read')
            if bom.docstatus != 1 or not bom.is_active or bom.item != item.name or bom.company != p.company or not entry.get('conversion_rule'):
                frappe.throw('Submitted active production BOM and reviewed conversion required')
        key = digest([p.company, p.custom_osr_city, entry['component_type_id'], package['engineering_revision']])
        mappings.append(dict(mapping_key=key, company=p.company, city=p.custom_osr_city,
            component_type=entry['component_type_id'], engineering_revision=package['engineering_revision'],
            engineering_sha256=package['engineering_sha256'], erp_item=item.name,
            source_package=json.dumps(dict(package=package, item=entry), sort_keys=True),
            native_item_modified=str(item.modified), native_bom_modified=str(bom.modified) if bom else None))
    return dict(mappings=mappings, fingerprint=digest(mappings), automatic_order_release=False)


@frappe.whitelist(methods=['POST'])
def apply_execution(project, package, fingerprint):
    preview = preview_execution(project, package)
    if preview['fingerprint'] != fingerprint:
        frappe.throw('Native item or BOM changed after preview')
    names = []
    for row in preview['mappings']:
        values = {k: v for k, v in row.items() if not k.startswith('native_')}
        if frappe.db.exists('OSR Execution Mapping', row['mapping_key']):
            doc = frappe.get_doc('OSR Execution Mapping', row['mapping_key']); doc.check_permission('read')
            if doc.source_package != row['source_package']:
                frappe.throw('Released revision mapping cannot be overwritten; create a new revision')
        else:
            doc = frappe.get_doc(dict(doctype='OSR Execution Mapping', **values)).insert()
        names.append(doc.name)
    return {'mappings': names, 'automatic_order_release': False}


def validate_execution_mapping(doc, method=None):
    previous = doc.get_doc_before_save()
    if previous and any(doc.get(field) != previous.get(field) for field in ['mapping_key', 'company', 'city', 'component_type', 'engineering_revision', 'engineering_sha256', 'erp_item', 'source_package']):
        frappe.throw('Execution mappings are immutable; create a reviewed new engineering revision')


def validate_condition_repair(doc, method=None):
    """Protect Issue/asset provenance while leaving native repair execution editable."""
    if not doc.get('custom_osr_repair_key'):
        return
    if not doc.custom_osr_handback_required:
        frappe.throw('OSR condition repairs always require independent railway handback')
    issue = frappe.get_doc('Issue', doc.custom_osr_issue)
    project = frappe.get_doc('Project', issue.project)
    asset = frappe.get_doc('Asset', issue.custom_osr_erp_asset)
    if (doc.asset != asset.name or doc.project != project.name or doc.company != project.company or
            doc.custom_osr_city != issue.custom_osr_city or
            doc.custom_osr_environment != issue.custom_osr_environment or
            doc.custom_osr_asset_id != issue.custom_osr_asset_id):
        frappe.throw('OSR repair provenance no longer matches its Issue, project and Asset')
    try:
        request = frappe.parse_json(doc.custom_osr_repair_request)
        if not isinstance(request, dict) or request.get('schema') != 'osr-condition-repair/1':
            raise ValueError
        frappe.parse_json(doc.custom_osr_configuration_evidence)
        expected = float(doc.custom_osr_expected_downtime_hours)
        if not math.isfinite(expected) or expected <= 0 or expected > 8760:
            raise ValueError
    except (AttributeError, TypeError, ValueError):
        frappe.throw('OSR repair provenance is invalid')
    previous = doc.get_doc_before_save()
    immutable = ['custom_osr_repair_key', 'custom_osr_repair_sha256', 'custom_osr_repair_request',
        'custom_osr_issue', 'custom_osr_environment', 'custom_osr_city', 'custom_osr_asset_id',
        'custom_osr_configuration_evidence', 'asset', 'company', 'project']
    if previous and any(doc.get(field) != previous.get(field) for field in immutable):
        frappe.throw('OSR repair provenance is immutable; create a separately reviewed repair')


def provision_service(path, output):
    """Bench-only provisioning from reviewed city/project scopes; never whitelisted."""
    import os
    import secrets
    from frappe.installer import update_site_config
    with open(path) as stream:
        requested = json.load(stream)
    projects, cities = [], []
    for row in requested:
        doc = frappe.get_doc('Project', row['project'])
        if doc.custom_osr_city != row['city']:
            frappe.throw('Provisioning city/project mismatch')
        projects.append(doc.name); cities.append(row['city'])
    email = 'osr-supervision@example.invalid'
    if not frappe.db.exists('User', email):
        frappe.get_doc(dict(doctype='User', email=email, first_name='OSR supervision integration',
            enabled=1, user_type='System User', send_welcome_email=0,
            roles=[dict(role='Support Team'), dict(role='Projects User')])).insert()
    user = frappe.get_doc('User', email)
    if not user.api_key:
        user.api_key = secrets.token_hex(16); user.api_secret = secrets.token_hex(24); user.save()
    policies = dict(frappe.conf.get('osr_integration_users') or {})
    previous = policies.get(email, {})
    policies[email] = dict(cities=sorted(set(cities + previous.get('cities', []))),
                          projects=sorted(set(projects + previous.get('projects', []))), environments=['simulation'])
    update_site_config('osr_integration_users', policies)
    for project in projects:
        frappe.share.add('Project', project, email, read=1, notify=0)
    frappe.db.commit()
    with open(output, 'w') as stream:
        json.dump(dict(url='http://frontend:8080', key=user.api_key, secret=user.get_password('api_secret')), stream)
    os.chmod(output, 0o600)
    return {'user': email, 'cities': policies[email]['cities'], 'environment': 'simulation'}
