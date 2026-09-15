"""Typed native adapters with city scope, read-only previews and repeat-safe apply."""
import html
import json

import frappe
from osr_erpnext.component_catalogue import CATALOGUE, instance_key, validate_inputs
from osr_erpnext.planning import digest
from osr_erpnext.procurement import city_warehouse_keys

META_TYPES = ['Work Order', 'Quality Inspection', 'Asset Maintenance', 'Training Program', 'Budget', 'Issue', 'Assignment Rule', 'Item Reorder']


def project_doc(name, write=False):
    doc = frappe.get_doc('Project', name)
    doc.check_permission('write' if write else 'read')
    if not doc.custom_osr_package_sha256:
        frappe.throw('Select an applied city operating baseline')
    return doc


def read(doctype, name, project, write=False):
    doc = frappe.get_doc(doctype, name)
    doc.check_permission('write' if write else 'read')
    if doc.get('company') and doc.company != project.company:
        frappe.throw(f'{doctype} belongs to another company')
    if doc.get('disabled') or doc.docstatus == 2:
        frappe.throw(f'{doctype} is disabled or cancelled')
    return doc


def warehouse(name, project):
    doc = read('Warehouse', name, project)
    if doc.is_group or doc.custom_osr_master_key not in city_warehouse_keys(project):
        frappe.throw('Warehouse must be configured for this city')
    return doc.name


def user(name, project):
    doc = read('User', name, project)
    if not doc.enabled or doc.name == 'Guest' or doc.user_type != 'System User':
        frappe.throw('Select an enabled ERP system user')
    if not frappe.has_permission('Project', 'read', doc=project, user=name):
        frappe.throw('Selected user cannot access this city project')
    return doc.name


def build(project, kind, values):
    """Read native prerequisites; do not insert, save, submit or run event hooks."""
    v = values
    if kind == 'replenishment':
        item = read('Item', v['item'], project, write=True)
        if not item.is_stock_item or not item.is_purchase_item:
            frappe.throw('Replenishment requires a purchasable stock Item')
        return dict(doctype='Item Reorder', parent=item.name, parenttype='Item', parentfield='reorder_levels',
            warehouse=warehouse(v['warehouse'], project), material_request_type='Purchase',
            warehouse_reorder_level=v['level'], warehouse_reorder_qty=v['quantity'])
    if kind == 'manufacturing':
        bom = read('BOM', v['bom'], project)
        if bom.docstatus != 1 or not bom.is_active:
            frappe.throw('Production requires an active submitted BOM')
        item = read('Item', bom.item, project)
        if not item.is_stock_item:
            frappe.throw('Production requires a stock Item')
        return dict(doctype='Work Order', company=project.company, project=project.name,
            production_item=bom.item, bom_no=bom.name, qty=v['quantity'], planned_start_date=v['start'],
            source_warehouse=warehouse(v['source_warehouse'], project),
            wip_warehouse=warehouse(v['wip_warehouse'], project), fg_warehouse=warehouse(v['fg_warehouse'], project))
    if kind == 'quality':
        reference = read(v['reference_type'], v['reference'], project, write=True)
        rows = [row for row in reference.items if row.name == v['line']]
        if len(rows) != 1 or (rows[0].project or reference.project) != project.name:
            frappe.throw('Inspection row must belong to this city project')
        row = rows[0]
        read('Item', row.item_code, project)
        template = read('Quality Inspection Template', v['template'], project)
        if not template.item_quality_inspection_parameter:
            frappe.throw('Inspection template needs approved parameters')
        return dict(doctype='Quality Inspection', company=project.company, inspection_type='Incoming',
            reference_type=v['reference_type'], reference_name=reference.name, child_row_reference=row.name,
            item_code=row.item_code, quality_inspection_template=template.name, sample_size=v['sample_size'],
            inspected_by=user(v['inspector'], project), report_date=v['report_date'],
            remarks='Prepared from the city operating component. Measurements and submission remain with the inspector.')
    if kind == 'maintenance':
        asset = read('Asset', v['asset'], project)
        if asset.docstatus != 1 or asset.status in {'Sold', 'Scrapped', 'Capitalized'} or not asset.available_for_use_date or frappe.utils.getdate(asset.available_for_use_date) > frappe.utils.getdate():
            frappe.throw('Maintenance requires a commissioned, submitted Asset')
        if not asset.custom_osr_asset_id or not frappe.get_list('Task', filters={'project': project.name,
                'custom_osr_asset_id': asset.custom_osr_asset_id}, pluck='name', limit_page_length=1):
            frappe.throw('Asset must reference an asset in this city baseline')
        team = read('Asset Maintenance Team', v['team'], project)
        assignee = user(v['assignee'], project)
        if frappe.db.get_value('User', assignee, 'email') != assignee:
            frappe.throw('Maintenance assignment requires an email-based ERP user account')
        if assignee not in [r.team_member for r in team.maintenance_team_members]:
            frappe.throw('Assignee must belong to the maintenance team')
        from erpnext.assets.doctype.asset_maintenance.asset_maintenance import calculate_next_due_date
        due = calculate_next_due_date(v['periodicity'], start_date=v['start'])
        return dict(doctype='Asset Maintenance', company=project.company, asset_name=asset.name,
            item_code=asset.item_code, item_name=asset.item_name, maintenance_team=team.name,
            asset_maintenance_tasks=[dict(maintenance_task=v['title'], maintenance_type='Preventive Maintenance',
                maintenance_status='Planned', periodicity=v['periodicity'], start_date=v['start'],
                next_due_date=due, assign_to=assignee, description=html.escape(v['description']))])
    if kind == 'training':
        return dict(doctype='Training Program', company=project.company,
            training_program=f'{v["title"][:90]} · {project.custom_osr_city} · {project.name}',
            description=html.escape(v['description']), status='Scheduled')
    if kind == 'budget':
        year = read('Fiscal Year', v['fiscal_year'], project)
        companies = [r.company for r in year.companies]
        if companies and project.company not in companies:
            frappe.throw('Fiscal year is unavailable for this company')
        seen = set()
        for row in v['accounts']:
            account = read('Account', row['account'], project)
            if account.company != project.company or account.root_type != 'Expense' or account.is_group or account.name in seen:
                frappe.throw('Select unique expense accounts in this company')
            seen.add(account.name)
        return dict(doctype='Budget', company=project.company, budget_against='Project', project=project.name,
            fiscal_year=year.name, accounts=[dict(account=r['account'], budget_amount=r['amount']) for r in v['accounts']],
            applicable_on_material_request=1, applicable_on_purchase_order=1, applicable_on_booking_actual_expenses=1,
            action_if_annual_budget_exceeded_on_mr=v['action'], action_if_annual_budget_exceeded_on_po=v['action'],
            action_if_annual_budget_exceeded=v['action'])
    if kind == 'service':
        read('Issue Priority', v['priority'], project)
        if v.get('sla'):
            agreement = read('Service Level Agreement', v['sla'], project)
            if not agreement.enabled:
                frappe.throw('Select an enabled service agreement')
        return dict(doctype='Issue', company=project.company, project=project.name, subject=v['subject'],
            description=html.escape(v['description']), priority=v['priority'], service_level_agreement=v.get('sla'), status='Open')
    if kind == 'assignment':
        names = [user(row['user'], project) for row in v['users']]
        if len(set(names)) != len(names):
            frappe.throw('Assignment users must be unique')
        calendar = json.loads(project.custom_osr_config)['calendar']
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        return dict(doctype='Assignment Rule', document_type='Task', rule=v['strategy'], disabled=1,
            description=f'City work allocation: {project.custom_osr_city}',
            assign_condition=f'project == {project.name!r} and custom_osr_kind == {v["category"]!r} and status not in ("Completed", "Cancelled")',
            close_condition='status in ("Completed", "Cancelled")', due_date_based_on='exp_end_date',
            assignment_days=[dict(day=days[d]) for d in calendar['working_weekdays']], users=[dict(user=n) for n in names])
    raise ValueError('Unknown component')


@frappe.whitelist(methods=['GET'])
def catalogue(project):
    doc = project_doc(project)
    profile = json.loads(doc.custom_osr_component_profile or '{}')
    return dict(components=CATALOGUE, defaults=profile.get('defaults', {}), city=doc.custom_osr_city,
                warehouses=frappe.get_list('Warehouse', filters={'custom_osr_master_key': ['in', city_warehouse_keys(doc)],
                    'company': doc.company, 'disabled': 0, 'is_group': 0}, pluck='name', limit_page_length=0)
                    if frappe.has_permission('Warehouse', 'read') else [],
                company=doc.company, currency=frappe.db.get_value('Company', doc.company, 'default_currency'))


@frappe.whitelist(methods=['GET'])
def inspection_lines(project, reference_type, reference):
    if reference_type not in {'Purchase Receipt', 'Purchase Invoice'}:
        frappe.throw('Unsupported inspection reference')
    doc = project_doc(project)
    source = read(reference_type, reference, doc)
    return [dict(value=row.name, label=f'{row.idx}: {row.item_code} · {row.qty} {row.uom}')
            for row in source.items if (row.project or source.project) == doc.name]


def prepare(project, component, key, inputs):
    doc = project_doc(project, write=True)
    key = instance_key(key)
    values = validate_inputs(component, json.loads(inputs) if isinstance(inputs, str) else inputs)
    target = CATALOGUE[component]['doctype']
    if target != 'Item Reorder':
        frappe.has_permission(target, 'create', throw=True)
    plan = build(doc, component, values)
    identity = digest([doc.name, component, key])
    if target == 'Assignment Rule':
        plan['name'] = f'OSR {doc.custom_osr_city[:30]} {key[:48]} {identity[:10]}'
    if target == 'Training Program':
        plan['training_program'] = f'{values["title"][:70]} · {doc.custom_osr_city[:30]} · {identity[:10]}'
    fingerprint = digest(dict(component=component, version=CATALOGUE[component]['version'],
        project=doc.name, baseline=doc.custom_osr_package_sha256, key=key, inputs=values, document=plan))
    return doc, identity, fingerprint, plan


@frappe.whitelist(methods=['POST'])
def preview(project, component, key, inputs):
    doc, identity, fingerprint, plan = prepare(project, component, key, inputs)
    return dict(component=component, key=key, project=doc.name, city=doc.custom_osr_city,
                fingerprint=fingerprint, effect=CATALOGUE[component]['effect'], document=plan)


@frappe.whitelist(methods=['POST'])
def apply(project, component, key, inputs, fingerprint):
    doc, identity, expected, plan = prepare(project, component, key, inputs)
    if fingerprint != expected:
        frappe.throw('Component inputs or prerequisites changed. Preview again.')
    target = plan['doctype']
    if target == 'Item Reorder':
        # Serialize additions to a shared Item, across every city using it.
        frappe.db.get_value('Item', plan['parent'], 'name', for_update=True)
    existing = frappe.db.get_value(target, {'custom_osr_component_key': identity}, ['name', 'parent'] if target == 'Item Reorder' else ['name'], as_dict=True)
    if existing:
        previous = frappe.get_doc(target, existing.name)
        if target == 'Item Reorder':
            frappe.get_doc('Item', existing.parent).check_permission('read')
        else:
            previous.check_permission('read')
        if previous.custom_osr_component_sha256 != expected:
            frappe.throw('Component instance already exists with different inputs. Review its native record or use a new instance key.')
        return dict(doctype='Item' if target == 'Item Reorder' else target,
                    name=existing.parent if target == 'Item Reorder' else existing.name, created=False)
    metadata = dict(custom_osr_component_key=identity, custom_osr_component_sha256=expected,
        custom_osr_component=component, custom_osr_instance=key, custom_osr_component_project=doc.name)
    if target == 'Item Reorder':
        item = frappe.get_doc('Item', plan['parent'])
        item.check_permission('write')
        if any(row.warehouse == plan['warehouse'] for row in item.reorder_levels):
            frappe.throw('This Item already has a rule for the warehouse. Review it in ERPNext.')
        item.append('reorder_levels', {**plan, **metadata})
        item.save()
        return dict(doctype='Item', name=item.name, created=True)
    record = frappe.get_doc({**plan, **metadata})
    if target == 'Work Order':
        record.set_work_order_operations()
        record.set_required_items()
        for item in record.required_items:
            item.source_warehouse = record.source_warehouse
    record.insert()
    return dict(doctype=target, name=record.name, created=True)


def feedback(project):
    result = {}
    for kind, config in CATALOGUE.items():
        dt = config['doctype']
        parent = 'Item' if dt == 'Item Reorder' else dt
        if not frappe.has_permission(parent, 'read'):
            result[kind] = dict(available=False)
            continue
        filters = [[dt, 'custom_osr_component_project', '=', project]]
        fields = ['name'] if dt == 'Item Reorder' else ['name', 'docstatus']
        if dt == 'Assignment Rule':
            fields.append('disabled')
        if dt in {'Training Program', 'Issue', 'Work Order', 'Quality Inspection'}:
            fields.append('status')
        rows = frappe.get_list(parent, filters=filters, fields=fields, distinct=True, limit_page_length=0)
        states = {}
        for row in rows:
            state = ('Configured items' if dt == 'Item Reorder' else
                     'Disabled' if dt == 'Assignment Rule' and row.disabled else
                     'Enabled' if dt == 'Assignment Rule' else
                     row.status if dt in {'Training Program', 'Issue'} else
                     'Scheduled' if dt == 'Asset Maintenance' else
                     row.status if dt == 'Work Order' else
                     f'Submitted: {row.status}' if dt == 'Quality Inspection' and row.docstatus == 1 else
                     ['Draft', 'Submitted', 'Cancelled'][row.docstatus])
            states[state] = states.get(state, 0) + 1
        result[kind] = dict(available=True, records=len(rows), states=states, doctype=parent)
    return result


def apply_package(package, preview_only=False):
    from osr_erpnext.component_catalogue import validate_package
    validate_package(package)
    project = project_doc(package['project'], write=True)
    if project.custom_osr_city != package['city']:
        frappe.throw('Component package belongs to a different city')
    plans = [preview(project.name, r['component'], r['key'], r['inputs']) for r in package['instances']]
    if preview_only:
        return dict(project=project.name, plans=plans)
    records = [apply(project.name, r['component'], r['key'], r['inputs'], p['fingerprint'])
               for r, p in zip(package['instances'], plans)]
    project.custom_osr_component_profile = json.dumps(dict(defaults=package['defaults'], package_sha256=package['sha256']))
    project.save()
    return dict(project=project.name, records=records)


def apply_file(path, preview_only=False):
    with open(path, encoding='utf-8') as stream:
        result = apply_package(json.load(stream), preview_only=preview_only)
    if not preview_only:
        frappe.db.commit()
    return result
