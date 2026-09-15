"""Scoped condition-event ingress and permission-filtered execution feedback."""
import json
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
    if event.get('erp_asset_id'):
        asset = frappe.get_doc('Asset', event['erp_asset_id']); asset.check_permission('read')
        if asset.company != event['company'] or asset.custom_osr_asset_id != event['asset_id']:
            frappe.throw('ERP Asset identity does not match condition event')
    key = digest([event['company'], event['city'], event['environment'], event['asset_id'], event['rule'], event['incident_id']])
    names = frappe.db.sql('SELECT name FROM `tabIssue` WHERE custom_osr_incident_key=%s FOR UPDATE', (key,))
    if names:
        issue = frappe.get_doc('Issue', names[0][0]); issue.check_permission('write')
    else:
        issue = frappe.new_doc('Issue')
        issue.subject = f"[OSR {event['environment']}] {event['asset_id']} · {event['rule']}"
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


def execution_feedback(project):
    """Actual transaction lines, keeping quantities, currency and release separate."""
    p = frappe.get_doc('Project', project); p.check_permission('read')
    result = {'purchase_orders': [], 'receipts': [], 'invoices': [], 'production': [], 'repairs': [], 'visibility': {},
              'engineering_accepted_quantity': None, 'installed_quantity': None,
              'authority': 'Native business transactions; installation and engineering acceptance require OSR evidence'}
    for dt, output in [('Purchase Order', 'purchase_orders'), ('Purchase Receipt', 'receipts'), ('Purchase Invoice', 'invoices'), ('Work Order', 'production'), ('Asset Repair', 'repairs')]:
        if not frappe.has_permission(dt, 'read'):
            result['visibility'][dt] = 'permission-denied'; continue
        meta = frappe.get_meta(dt)
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
