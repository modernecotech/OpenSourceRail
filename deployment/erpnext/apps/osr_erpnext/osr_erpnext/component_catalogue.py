"""Versioned schemas shared by the ERP forms, API and city package compiler."""
from copy import deepcopy
from datetime import date, datetime
import math
import re


def field(name, label, kind='Data', options=None, required=True, **extra):
    return dict(fieldname=name, label=label, fieldtype=kind, options=options, reqd=int(required), **extra)


def link(name, label, doctype, **extra):
    return field(name, label, 'Link', doctype, **extra)


def component(label, doctype, effect, fields):
    return dict(label=label, doctype=doctype, version=1, effect=effect, fields=fields)


CATALOGUE = {
 'replenishment': component('Stock replenishment', 'Item Reorder',
    'Adds a live reorder rule to an existing Item. Native stock settings and the scheduler control request generation.', [
    link('item', 'Stock Item', 'Item'), link('warehouse', 'City warehouse', 'Warehouse'),
    field('level', 'Reorder level in stock units', 'Float', minimum=0),
    field('quantity', 'Reorder quantity in stock units', 'Float', minimum=0.000001)]),
 'manufacturing': component('Production order', 'Work Order',
    'Creates an unsubmitted Work Order from an approved BOM. Native submission creates the production workflow.', [
    link('bom', 'Submitted production BOM', 'BOM'), field('quantity', 'Production quantity', 'Float', minimum=0.000001),
    link('source_warehouse', 'Source city warehouse', 'Warehouse'), link('wip_warehouse', 'Work in progress warehouse', 'Warehouse'),
    link('fg_warehouse', 'Finished goods warehouse', 'Warehouse'), field('start', 'Planned start', 'Datetime')]),
 'quality': component('Incoming quality inspection', 'Quality Inspection',
    'Creates a draft inspection for one project-linked receipt/invoice line. Inspectors record measurements and submit it in ERPNext.', [
    field('reference_type', 'Reference type', 'Select', 'Purchase Receipt\nPurchase Invoice'),
    link('reference', 'Receipt or invoice', 'Purchase Receipt'), field('line', 'Reference item row ID'),
    link('template', 'Inspection template', 'Quality Inspection Template'), field('sample_size', 'Sample size', 'Float', minimum=0.000001),
    field('report_date', 'Inspection date', 'Date'),
    link('inspector', 'Inspector', 'User')]),
 'maintenance': component('Asset servicing', 'Asset Maintenance',
    'Creates a native maintenance schedule, maintenance log and assignment to the selected team member on save.', [
    link('asset', 'Commissioned city asset', 'Asset'), link('team', 'Maintenance team', 'Asset Maintenance Team'),
    link('assignee', 'Team member', 'User'), field('title', 'Maintenance task'),
    field('periodicity', 'Approved interval', 'Select', 'Daily\nWeekly\nMonthly\nQuarterly\nHalf-yearly\nYearly\n2 Yearly\n3 Yearly'),
    field('start', 'Schedule start', 'Date'), field('description', 'Service instructions', 'Small Text')]),
 'training': component('Training programme', 'Training Program',
    'Creates a native training programme. Events, attendance, results and competence decisions remain separate records.', [
    field('title', 'Programme title'), field('description', 'Objectives and required learning', 'Small Text')]),
 'budget': component('Project budget', 'Budget',
    'Creates an unsubmitted project budget in company currency. Native budget controls take effect after submission.', [
    link('fiscal_year', 'Fiscal year', 'Fiscal Year'), field('action', 'Annual overspend action', 'Select', 'Stop\nWarn'),
    field('accounts', 'Account allocations in company currency', 'Table', fields=[
        link('account', 'Expense account', 'Account', in_list_view=1),
        field('amount', 'Budget amount', 'Currency', minimum=0.000001, in_list_view=1)])]),
 'service': component('Facility service issue', 'Issue',
    'Creates an open business service issue. The selected SLA supplies response deadlines through native ERP rules.', [
    field('subject', 'Issue subject'), field('description', 'Description', 'Small Text'),
    link('priority', 'Priority', 'Issue Priority'), link('sla', 'Service level agreement', 'Service Level Agreement', required=False)]),
 'assignment': component('City task assignment', 'Assignment Rule',
    'Creates a disabled native assignment rule scoped to this project and work category. Review users and enable it in ERPNext.', [
    field('category', 'Work category', 'Select', 'manufacturing\nmaintenance\nqa\nprocurement\nprogramme'),
    field('strategy', 'Assignment strategy', 'Select', 'Round Robin\nLoad Balancing'),
    field('users', 'Responsible users', 'Table', fields=[link('user', 'User', 'User', in_list_view=1)])]),
}


def validate_inputs(component_id, values, partial=False):
    if component_id not in CATALOGUE or not isinstance(values, dict):
        raise ValueError('Unknown component or invalid inputs')
    def validate(fields, data):
        known = {f['fieldname']: f for f in fields}
        if data.keys() - known.keys():
            raise ValueError('Unknown component inputs: ' + ', '.join(sorted(data.keys() - known.keys())))
        clean = {}
        for name, f in known.items():
            value = data.get(name)
            if value is None or value == '':
                if f['reqd'] and not partial:
                    raise ValueError(f"{f['label']} is required")
                continue
            kind = f['fieldtype']
            if kind in {'Float', 'Currency'}:
                if isinstance(value, bool):
                    raise ValueError(f'{name} must be a number')
                try:
                    value = float(value)
                except (ValueError, TypeError):
                    raise ValueError(f'{name} must be a number') from None
                if not math.isfinite(value) or not f.get('minimum', 0) <= value <= 1e12:
                    raise ValueError(f'{name} is outside the permitted range')
            elif kind == 'Table':
                if not isinstance(value, list) or not 1 <= len(value) <= 100 or any(not isinstance(r, dict) for r in value):
                    raise ValueError(f'{name} needs 1..100 rows')
                value = [validate(f['fields'], row) for row in value]
            else:
                if not isinstance(value, str) or not value.strip() or len(value) > (10000 if kind == 'Small Text' else 140):
                    raise ValueError(f'Invalid {name}')
                if kind == 'Select' and value not in f['options'].split('\n'):
                    raise ValueError(f'Unknown {name}')
                if kind == 'Date':
                    value = date.fromisoformat(value).isoformat()
                if kind == 'Datetime':
                    parsed = datetime.fromisoformat(value)
                    if parsed.tzinfo:
                        raise ValueError('Use the ERP site timezone for timestamps')
                    value = parsed.isoformat(sep=' ')
            clean[name] = value
        return clean
    return validate(CATALOGUE[component_id]['fields'], values)


def instance_key(key):
    if not isinstance(key, str) or not re.fullmatch(r'[a-z0-9][a-z0-9_.-]{0,63}', key):
        raise ValueError('Instance key must be 1..64 lowercase letters, numbers, dots, underscores or hyphens')
    return key


def merge_profiles(generic, city):
    for value in [generic, city]:
        if not isinstance(value, dict) or set(value) - {'schema', 'city', 'defaults', 'instances'} or value.get('schema') != 'osr-components/1':
            raise ValueError('Invalid component profile')
    result = deepcopy(generic)
    result['city'] = city['city']
    result.setdefault('defaults', {})
    for kind, inputs in city.get('defaults', {}).items():
        result['defaults'][kind] = {**result['defaults'].get(kind, {}), **inputs}
    # Instance keys are component-local. City entries override shared entries explicitly.
    instances = {(r['component'], r['key']): r for r in generic.get('instances', [])}
    instances.update({(r['component'], r['key']): r for r in city.get('instances', [])})
    result['instances'] = list(instances.values())
    for kind, inputs in result['defaults'].items():
        validate_inputs(kind, inputs, partial=True)
    for source in [generic, city]:
        keys = [(r['component'], r['key']) for r in source.get('instances', [])]
        if len(set(keys)) != len(keys):
            raise ValueError('Duplicate component instance')
    for row in result['instances']:
        if set(row) - {'component', 'key', 'inputs', 'enabled'} or type(row.get('enabled', True)) is not bool:
            raise ValueError('Invalid component instance')
        instance_key(row['key'])
        values = {**result['defaults'].get(row['component'], {}), **row.get('inputs', {})}
        validate_inputs(row['component'], values, partial=not row.get('enabled', True))
    return result


def make_package(profile, project):
    from osr_erpnext.planning import digest
    if not isinstance(project, str) or not project.strip():
        raise ValueError('Target ERP project is required')
    profile = deepcopy(profile)
    def substitute(value):
        if isinstance(value, str):
            return value.replace('${city}', profile['city']).replace('${project}', project)
        if isinstance(value, dict):
            return {k: substitute(v) for k, v in value.items()}
        if isinstance(value, list):
            return [substitute(v) for v in value]
        return value
    profile['defaults'] = substitute(profile.get('defaults', {}))
    instances = []
    for row in profile['instances']:
        if row.get('enabled', True):
            values = substitute({**profile['defaults'].get(row['component'], {}), **row.get('inputs', {})})
            instances.append(dict(component=row['component'], key=row['key'], inputs=validate_inputs(row['component'], values)))
    package = dict(schema='osr-component-package/1', project=project, city=profile['city'],
                   defaults=profile['defaults'], instances=instances)
    package['sha256'] = digest(package)
    return package


def validate_package(package):
    from osr_erpnext.planning import digest
    if set(package) != {'schema', 'project', 'city', 'defaults', 'instances', 'sha256'} or package['schema'] != 'osr-component-package/1':
        raise ValueError('Invalid component package')
    if package['sha256'] != digest({k: v for k, v in package.items() if k != 'sha256'}):
        raise ValueError('Component package checksum mismatch')
    seen = set()
    for row in package['instances']:
        if set(row) != {'component', 'key', 'inputs'}:
            raise ValueError('Invalid component instance')
        identity = (row['component'], instance_key(row['key']))
        if identity in seen:
            raise ValueError('Duplicate component instance')
        seen.add(identity)
        validate_inputs(row['component'], row['inputs'])
    for kind, defaults in package['defaults'].items():
        validate_inputs(kind, defaults, partial=True)
