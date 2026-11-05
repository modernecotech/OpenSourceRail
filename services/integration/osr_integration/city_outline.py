"""Immutable LOCAL review drafts; never connects to or writes a business site.

ERPNext/HRMS v15 standard field names guide these payloads. They are not schema
validated against a target site, and required site/date mappings remain open.
Non-submittable masters without a standard disabled field are held by the local
manifest rather than receiving invented site fields. No importer is provided.
"""
from copy import deepcopy
from hashlib import sha256
import json
from math import ceil, isfinite
from pathlib import Path
import re

PRODUCER = 'services/integration/osr_integration/city_outline.py'
SCHEMA = 'osr-city-outline-delivery-drafts/1'
DOCTYPES = ('Item', 'BOM', 'Operation', 'Routing', 'Workstation', 'Project',
            'Task', 'Work Order', 'Shift Type', 'Staffing Plan')
FIELDS = {
    'Item': {'item_code','item_name','stock_uom','disabled','is_stock_item'},
    'BOM': {'item','quantity','uom','is_active','is_default','currency','items','routing','with_operations'},
    'Operation': {'workstation'}, 'Routing': {'routing_name','disabled','operations'},
    'Workstation': {'workstation_name'}, 'Project': {'project_name','status'},
    'Task': {'subject','project','status','depends_on'},
    'Work Order': {'status','production_item','bom_no','qty','project'},
    'Shift Type': {'start_time','end_time','enable_auto_attendance'},
    'Staffing Plan': {'staffing_details'},
}
FLAGS = dict(external_transactions_performed=False, business_records_submitted=False,
    physical_accepted=False, engineering_accepted=False, manufacturing_release=False,
    operating_release=False, procurement_approved=False, movement_authority=False,
    active_orders_mutated=False, target_site_schema_validation_performed=False)
MAX_BYTES = 64 * 1024**2
REFERENCES = {
    'work_order': 'https://raw.githubusercontent.com/frappe/erpnext/version-15/erpnext/manufacturing/doctype/work_order/work_order.json',
    'routing': 'https://raw.githubusercontent.com/frappe/erpnext/version-15/erpnext/manufacturing/doctype/routing/routing.json',
    'staffing_plan': 'https://raw.githubusercontent.com/frappe/hrms/version-15/hrms/hr/doctype/staffing_plan/staffing_plan.json',
    'staffing_detail': 'https://raw.githubusercontent.com/frappe/hrms/version-15/hrms/hr/doctype/staffing_plan_detail/staffing_plan_detail.json',
    'shift_type': 'https://docs.frappe.io/hr/shift-type',
}


def encoded(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)+'\n').encode()


def identity(value):
    return sha256(encoded(value)).hexdigest()


def _seal(value, key):
    value[key] = identity(value)
    return value


def _sealed(value, key):
    if value.get(key) != identity({k:v for k,v in value.items() if k != key}):
        raise ValueError('Immutable '+key+' identity differs')


def _number(value, name, zero=False):
    if type(value) not in (int, float) or not isfinite(value) or value < 0 or (not zero and value == 0):
        raise ValueError('Positive finite '+name+' required')
    return value


def _unique(rows, key):
    result = {}
    for row in rows:
        name = row.get(key)
        if not isinstance(name, str) or not name or name in result:
            raise ValueError('Unique '+key+' required')
        result[name] = row
    return result


def _acyclic(graph, label):
    pending, done = set(), set()
    def visit(node):
        if node in pending: raise ValueError(label+' cycle')
        if node in done: return
        pending.add(node)
        for child in graph[node]:
            if child not in graph: raise ValueError('Unknown '+label+' reference')
            visit(child)
        pending.remove(node); done.add(node)
    for node in graph: visit(node)


def _ordinary(path):
    path = Path(path).absolute()
    if any(p.is_symlink() for p in (path, *path.parents)):
        raise ValueError('Ordinary local paths required')
    return path


def _sources(sources, root):
    for name, digest in sources.items():
        if (not isinstance(name, str) or Path(name).is_absolute() or '..' in Path(name).parts
                or not isinstance(digest, str) or not re.fullmatch('[a-f0-9]{64}', digest)):
            raise ValueError('Relative source path and SHA256 required')
        if root is not None and sha256(_ordinary(Path(root)/name).read_bytes()).hexdigest() != digest:
            raise ValueError('Source differs: '+name)


def _check_plan(plan, root):
    _sealed(plan, 'plan_id')
    if plan.get('schema') != 'osr-city-outline-delivery-plan/1':
        raise ValueError('City delivery plan required')
    for flag in FLAGS:
        if plan.get(flag, False) is not False: raise ValueError('Plan cannot grant release')
    for key in ('city_record_evaluation_id','city_input_id','cost_evaluation_id',
                'research_configuration_id','selection_id','planning_revision_id'):
        if not isinstance(plan.get(key), str) or not plan[key]: raise ValueError('Missing '+key)
    if not plan.get('reference_candidate_ids'): raise ValueError('Reference candidate identities required')
    _sources(plan['source_sha256'], root)
    items = _unique(plan['items'], 'item_code')
    boms = _unique(plan['boms'], 'item_code')
    resources = _unique(plan['resources'], 'resource_id')
    tasks = _unique(plan['tasks'], 'task_id')
    graph = {key:[] for key in items}
    for key, item in items.items():
        _number(item['quantity'], 'item quantity')
        if not isinstance(item.get('uom'), str) or not item['uom']: raise ValueError('Explicit item UOM required')
        for field in ('budget_usd','unit_cost_usd'):
            if field in item:
                for x in ('low','base','high'): _number(item[field][x],field)
                if not item[field]['low'] <= item[field]['base'] <= item[field]['high']:
                    raise ValueError('Ordered item cost cases required')
    for key, bom in boms.items():
        if key not in items or bom['uom'] != items[key]['uom']: raise ValueError('BOM output item/UOM differs')
        _number(bom['output_quantity'], 'BOM output quantity')
        if not bom['items']: raise ValueError('BOM requires actual component rows')
        for child in bom['items']:
            code = child['item_code']
            if code not in items or child['uom'] != items[code]['uom']: raise ValueError('BOM component item/UOM differs')
            _number(child['qty'], 'BOM quantity'); graph[key].append(code)
    _acyclic(graph, 'BOM')
    _acyclic({k:v['predecessors'] for k,v in tasks.items()}, 'task')
    groups = _unique(plan['production_groups'], 'group_id')
    group_items = [g['item_code'] for g in groups.values() if g['operations']]
    if len(group_items) != len(set(group_items)):
        raise ValueError('One unambiguous routing per output item required')
    operations = []
    for group in groups.values():
        if group['item_code'] not in items or group['route'] not in ('make','buy','receive-fit'):
            raise ValueError('Production group item/route differs')
        _number(group['output_quantity'], 'production quantity')
        if group['uom'] != items[group['item_code']]['uom']: raise ValueError('Production UOM differs')
        if group['route'] == 'make' and group['item_code'] not in boms:
            raise ValueError('Make route requires an explicit BOM')
        sequence = []
        for op in group['operations']:
            if op['resource_id'] not in resources: raise ValueError('Unknown operation resource')
            for x in ('low','base','high'): _number(op['hours_per_unit'][x], 'operation hours')
            sequence.append(_number(op['sequence'], 'operation sequence'))
            operations.append(op)
        if len(sequence) != len(set(sequence)): raise ValueError('Unique operation sequence required')
    _unique(operations, 'operation_id')
    for case in ('low','base','high'):
        schedule = plan['schedule']['cases'][case]
        if schedule.get('capacity_pass') is not True: raise ValueError('Capacity-feasible outline schedule required')
        rows = _unique(schedule['tasks'], 'task_id')
        if set(rows) != set(tasks): raise ValueError('Schedule task coverage differs')
        for key, row in rows.items():
            start = _number(row['start_workday'], 'start workday', True)
            finish = _number(row['finish_workday'], 'finish workday', True)
            if finish < start: raise ValueError('Negative task duration')
            if any(rows[p]['finish_workday'] > start + 1e-8 for p in tasks[key]['predecessors']):
                raise ValueError('Task precedence differs')
    return items, boms, resources, tasks, groups


def delivery_drafts(plan, active_orders=(), root=None):
    """Convert a sealed plan into held local payloads, with no invented dates."""
    items, boms, resources, tasks, groups = _check_plan(plan, root)
    prefix = 'OSR-'+plan['plan_id'][:16]+'-'
    def name(kind, key): return prefix+kind+'-'+identity(key)[:16]
    docs = {kind:[] for kind in DOCTYPES}; metadata = {}
    def add(kind, key, fields, **extra):
        n = name(kind.replace(' ', ''), key)
        doc = dict(doctype=kind, name=n, docstatus=0, **fields)
        docs[kind].append(doc)
        metadata[n] = dict(local_disabled=True, export_only=True, site_insert_permitted=False,
            source_plan_id=plan['plan_id'], **extra)
        return n
    item_names = {}
    for key, item in items.items():
        code = name('Item', key); item_names[key] = code
        add('Item', key, dict(item_code=code, item_name=item['name'], stock_uom=item['uom'],
            disabled=1, is_stock_item=0 if item.get('kind') == 'service' else 1),
            source_item_id=item['item_id'], original_item_code=key, quantity=item['quantity'],
            source_line_ids=item.get('source_line_ids', []), budget_usd=item.get('budget_usd'),
            unit_cost_usd=item.get('unit_cost_usd'), cost_status='bounded-plan-budget' if item.get('budget_usd') else 'not-an-individual-priced-line-see-cost-reconciliation',
            unresolved_site_fields=['item_group', 'UOM mapping'])
    project = add('Project', plan['plan_id'], dict(project_name=plan['city']['name']+' calculated outline', status='Open'),
        unresolved_site_fields=['company', 'calendar start date'], budget=deepcopy(plan.get('cost_reconciliation', {})))
    resource_names = {key:add('Workstation', key, dict(workstation_name=name('Cell', key)),
        resource=deepcopy(row), capacity_semantics='Outline resource; site workstation/capacity mapping required')
        for key, row in resources.items()}
    route_names = {}; op_names = {}
    for key, group in groups.items():
        route_ops = []
        for op in sorted(group['operations'], key=lambda z:z['sequence']):
            op_name = add('Operation', op['operation_id'], dict(workstation=resource_names[op['resource_id']]),
                operation_name=op['name'], source_operation=deepcopy(op))
            op_names[op['operation_id']] = op_name
            route_ops.append(dict(doctype='BOM Operation',docstatus=0,operation=op_name,
                workstation=resource_names[op['resource_id']],time_in_mins=op['hours_per_unit']['base']*60,
                sequence_id=op['sequence']))
        if route_ops:
            route_names[group['item_code']] = add('Routing', key,
                dict(routing_name=name('Routing', key), disabled=1, operations=route_ops),
                group_id=key, route=group['route'], output_quantity=group['output_quantity'],
                operation_times_basis='Per output unit; low/base/high retained in operation metadata')
    bom_names = {}
    for key, bom in boms.items():
        fields = dict(item=item_names[key], quantity=bom['output_quantity'],uom=bom['uom'],
            is_active=0,is_default=0,currency='USD',items=[dict(doctype='BOM Item',docstatus=0,
                item_code=item_names[z['item_code']],qty=z['qty'],uom=z['uom']) for z in bom['items']])
        if key in route_names: fields.update(routing=route_names[key],with_operations=1)
        bom_names[key] = add('BOM', key, fields, source_bom_id=bom['bom_id'],
            unresolved_site_fields=['company', 'warehouse', 'BOM costing validation'])
    task_names = {key:name('Task',key) for key in tasks}
    for key, task in tasks.items():
        sched = {c:next(r for r in plan['schedule']['cases'][c]['tasks'] if r['task_id']==key)
            for c in ('low','base','high')}
        add('Task', key, dict(subject=task['name'],project=project,status='Open',
            depends_on=[dict(doctype='Task Depends On',docstatus=0,task=task_names[p]) for p in task['predecessors']]),
            source_task=deepcopy(task), relative_schedule=sched, calendar_dates_assigned=False)
    for key, group in groups.items():
        if group['route'] == 'make':
            add('Work Order', key, dict(status='Draft',production_item=item_names[group['item_code']],
                bom_no=bom_names[group['item_code']],qty=group['output_quantity'],project=project),
                group_id=key, unresolved_site_fields=['company','source_warehouse','wip_warehouse',
                    'fg_warehouse','planned_start_date','naming_series'], calendar_dates_assigned=False)
    for shift in plan['workforce']['shift_patterns']:
        count = shift['shifts_per_day']; hours = shift['hours_per_shift']
        if type(count) is not int or not 1 <= count <= 3 or not 0 < hours <= 12 or count*hours > 24:
            raise ValueError('Bounded nonoverlapping shift pattern required')
        for i in range(count):
            def clock(h):
                minutes = round(h*60)%1440
                return f'{minutes//60:02d}:{minutes%60:02d}:00'
            add('Shift Type', [shift['shift_id'],i], dict(start_time=clock(i*hours),
                end_time=clock((i+1)*hours),enable_auto_attendance=0),
                shift_pattern=deepcopy(shift), shift_number=i+1,
                clock_origin_is_provisional=True, named_workers_assigned=False)
        positions = shift['positions_by_case']
        for x in ('low','base','high'): _number(positions[x], 'staffing positions', True)
        add('Staffing Plan', shift['shift_id'], dict(staffing_details=[dict(
            doctype='Staffing Plan Detail',docstatus=0,vacancies=ceil(positions['base'])*count)]),
            workforce=deepcopy(shift), vacancies_by_case=deepcopy(shift['positions_by_case']),
            vacancies_basis='Ceiling of base simultaneous positions times daily shifts; no named workers. Days-off/leave relief remains a separate HR calculation',
            unresolved_site_fields=['company','from_date','to_date','designation','department','employment-cost budget'],
            staffing_details_status='Calculated unnamed vacancies; required designation and employment costs remain unmapped')
    orders = deepcopy(list(active_orders)); reviews = []
    for order in orders:
        if not all(order.get(k) for k in ('order_id','candidate_id','released_revision_id')):
            raise ValueError('Active orders require immutable released bindings')
        reviews.append(dict(order_id=order['order_id'],released_candidate_id=order['candidate_id'],
            released_revision_id=order['released_revision_id'],proposed_plan_id=plan['plan_id'],
            action='human-change-control-review',active_order_mutated=False))
    source = dict(plan['source_sha256']); source[PRODUCER] = sha256(Path(__file__).read_bytes()).hexdigest()
    value = dict(schema=SCHEMA, source_plan_id=plan['plan_id'], city=deepcopy(plan['city']),
        identities={k:deepcopy(plan[k]) for k in ('city_record_evaluation_id','city_input_id','cost_evaluation_id',
            'research_configuration_id','reference_candidate_ids','selection_id','planning_revision_id')},
        documents=docs, document_metadata=metadata, active_orders_preserved=orders,
        active_orders_sha256=identity(orders),change_reviews=reviews,source_sha256=source,
        standard_field_references=REFERENCES, target_schema_basis='ERPNext/HRMS v15 source guidance; not target-site validation',
        unresolved_handoffs=['Company, warehouses, UOMs, item groups and HR designations',
            'Calendar origin, working/holiday calendars and employee relief rosters',
            'Approved drawings/BOM/routes, QA and independent procurement/manufacturing release'],
        **FLAGS)
    return _seal(value, 'draft_id')


def validate(value, root=None):
    _sealed(value, 'draft_id')
    if value.get('schema') != SCHEMA or any(value.get(k) is not False for k in FLAGS):
        raise ValueError('Held local draft disposition required')
    _sources(value['source_sha256'], root)
    if value['source_sha256'].get(PRODUCER) != sha256(Path(__file__).read_bytes()).hexdigest():
        raise ValueError('Loaded draft adapter source differs')
    if set(value['documents']) != set(DOCTYPES): raise ValueError('Doctype coverage differs')
    all_docs = [d for rows in value['documents'].values() for d in rows]
    names = _unique(all_docs, 'name')
    if set(names) != set(value['document_metadata']): raise ValueError('Document metadata coverage differs')
    for kind, rows in value['documents'].items():
        for doc in rows:
            if doc['doctype'] != kind or doc.get('docstatus') != 0: raise ValueError('Draft docstatus required')
            if set(doc)-FIELDS[kind]-{'doctype','name','docstatus'}:
                raise ValueError('Unsupported site field in '+kind)
            if kind in ('Item','Routing') and doc.get('disabled') != 1: raise ValueError('Disabled master required')
            if kind == 'BOM' and (doc.get('is_active') != 0 or doc.get('is_default') != 0):
                raise ValueError('Inactive non-default BOM required')
            meta = value['document_metadata'][doc['name']]
            if meta.get('local_disabled') is not True or meta.get('site_insert_permitted') is not False or meta['source_plan_id'] != value['source_plan_id']:
                raise ValueError('Local hold metadata required')
            for field in ('items','operations','depends_on','staffing_details'):
                for child in doc.get(field,[]):
                    if child.get('docstatus') != 0: raise ValueError('Draft child docstatus required')
            if kind == 'Shift Type' and doc.get('enable_auto_attendance') != 0:
                raise ValueError('Automatic attendance remains disabled')
    def refs(kind): return {d['name']:d for d in value['documents'][kind]}
    items = {d['item_code']:d for d in value['documents']['Item']}
    boms, resources, operations, routes, projects, tasks = [refs(k) for k in
        ('BOM','Workstation','Operation','Routing','Project','Task')]
    graph = {key:[] for key in items}
    for bom in boms.values():
        if bom['item'] not in items or bom['uom'] != items[bom['item']]['stock_uom']:
            raise ValueError('BOM output reference/UOM differs')
        _number(bom['quantity'], 'BOM output quantity')
        for child in bom['items']:
            code = child['item_code']
            if code not in items or child['uom'] != items[code]['stock_uom']:
                raise ValueError('BOM child reference/UOM differs')
            _number(child['qty'], 'BOM quantity'); graph[bom['item']].append(code)
        if 'routing' in bom and bom['routing'] not in routes: raise ValueError('Unknown BOM routing')
    _acyclic(graph,'BOM')
    for op in operations.values():
        if op['workstation'] not in resources: raise ValueError('Unknown operation workstation')
    for route in routes.values():
        for op in route['operations']:
            if op['operation'] not in operations or op['workstation'] not in resources:
                raise ValueError('Unknown routing operation/workstation')
            _number(op['time_in_mins'], 'routing time')
    for doc in value['documents']['Work Order']:
        if (doc['production_item'] not in items or doc['bom_no'] not in boms
                or boms[doc['bom_no']]['item'] != doc['production_item']
                or doc['project'] not in projects or doc['status'] != 'Draft'):
            raise ValueError('Work Order references/status differ')
        _number(doc['qty'],'Work Order quantity')
    task_graph = {}
    for key, task in tasks.items():
        if task['project'] not in projects: raise ValueError('Unknown task project')
        task_graph[key] = [r['task'] for r in task['depends_on']]
        for case,row in value['document_metadata'][key]['relative_schedule'].items():
            if case not in ('low','base','high') or row['finish_workday'] < row['start_workday']:
                raise ValueError('Relative schedule differs')
    _acyclic(task_graph,'task')
    if identity(value['active_orders_preserved']) != value['active_orders_sha256']:
        raise ValueError('Preserved active order identity differs')
    return value


def export_drafts(value, output, root=None):
    validate(value, root)
    if len(encoded(value)) > MAX_BYTES: raise ValueError('Bounded local export required')
    output = _ordinary(output)
    if root is not None:
        try: output.relative_to(_ordinary(Path(root)/'build'))
        except ValueError as exc: raise ValueError('Private repository build output required') from exc
    if output.exists(): raise ValueError('Fresh local draft output required')
    output.mkdir(parents=True)
    files = {}
    for kind in DOCTYPES:
        filename = kind.lower().replace(' ','-')+'.json'
        raw = encoded(value['documents'][kind]); (output/filename).write_bytes(raw)
        files[filename] = sha256(raw).hexdigest()
    raw = encoded(value); (output/'drafts.json').write_bytes(raw); files['drafts.json'] = sha256(raw).hexdigest()
    manifest = _seal(dict(schema='osr-city-outline-draft-export/1',draft_id=value['draft_id'],
        source_plan_id=value['source_plan_id'],identities=value['identities'],files_sha256=files,
        source_sha256=value['source_sha256'],**FLAGS), 'manifest_id')
    (output/'manifest.json').write_bytes(encoded(manifest))
    return manifest


def verify_export(output, root=None):
    output = _ordinary(output)
    def read(name):
        path = _ordinary(output/name)
        if path.stat().st_size>MAX_BYTES: raise ValueError('Bounded local artifact required')
        raw = path.read_bytes()
        if len(raw)>MAX_BYTES: raise ValueError('Bounded local artifact required')
        return raw
    manifest = json.loads(read('manifest.json')); _sealed(manifest, 'manifest_id')
    expected = {kind.lower().replace(' ','-')+'.json' for kind in DOCTYPES}|{'drafts.json'}
    if (manifest.get('schema') != 'osr-city-outline-draft-export/1'
            or any(manifest.get(k) is not False for k in FLAGS)
            or set(manifest['files_sha256']) != expected
            or {p.name for p in output.iterdir()} != expected|{'manifest.json'}):
        raise ValueError('Local export inventory/disposition differs')
    for name, digest in manifest['files_sha256'].items():
        if sha256(read(name)).hexdigest() != digest: raise ValueError('Artifact differs: '+name)
    value = validate(json.loads(read('drafts.json')), root)
    if any(manifest[k] != value[k] for k in ('draft_id','source_plan_id','identities','source_sha256')):
        raise ValueError('Export bindings differ')
    for kind in DOCTYPES:
        if json.loads(read(kind.lower().replace(' ','-')+'.json')) != value['documents'][kind]:
            raise ValueError('Export document payload differs')
    return manifest, value
