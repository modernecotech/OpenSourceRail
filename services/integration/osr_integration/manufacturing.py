"""Validated read-only factory supervision derived from LM3 manufacturing methods."""
import copy
import hashlib
import json
import math
from pathlib import Path
import re


METHOD_SCHEMA = 'org.opensourcerail.trainset-manufacturing-methods.v1'
FACTORY_METHOD_SCHEMA = 'osr-manufacturing-method/1'
DEFAULT_SIMULATION_METHOD = 'LM3-MFG-020'


def _identity(value, label='identity'):
    if not isinstance(value, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.:-]{0,159}', value):
        raise ValueError(f'Invalid {label}')
    return value


def _nonempty(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f'{label} is required')
    return value


def _identity_list(value, label):
    if not isinstance(value, list) or not value:
        raise ValueError(f'{label} must be a non-empty list')
    rows = [_identity(item, label) for item in value]
    if len(rows) != len(set(rows)):
        raise ValueError(f'{label} contains duplicate identities')
    return rows


def validate_method_document(document):
    """Reject incomplete or internally inconsistent generated method coverage."""
    if not isinstance(document, dict) or document.get('schema') != METHOD_SCHEMA:
        raise ValueError('Manufacturing-method schema mismatch')
    methods = document.get('method')
    coverage = document.get('coverage')
    if not isinstance(methods, list) or not methods or not isinstance(coverage, dict):
        raise ValueError('Manufacturing methods and coverage are required')
    method_ids, product_ids, tooling_ids = set(), set(), set()
    for method in methods:
        if not isinstance(method, dict):
            raise ValueError('Manufacturing method must be an object')
        method_id = _identity(method.get('id'), 'manufacturing method identity')
        if method_id in method_ids:
            raise ValueError('Duplicate manufacturing method identity')
        method_ids.add(method_id)
        _nonempty(method.get('title'), 'Manufacturing method title')
        _nonempty(method.get('work_center'), 'Manufacturing work center')
        _nonempty(method.get('release_gate'), 'Manufacturing release gate')
        crew = method.get('crew_size')
        cycle = method.get('planning_cycle_minutes')
        if type(crew) is not int or crew < 1 or type(cycle) is not int or cycle < 1:
            raise ValueError('Manufacturing crew and planning cycle must be positive integers')
        products = _identity_list(method.get('product_ids'), 'manufactured product identity')
        # A product can legitimately pass through more than one method (for
        # example fabrication followed by integration); coverage is the union.
        product_ids.update(products)
        tooling_ids.update(_identity_list(method.get('tooling_ids'), 'manufacturing tooling identity'))
        _identity_list(method.get('source_ids'), 'manufacturing source identity')
        steps = method.get('steps')
        if not isinstance(steps, list) or not steps:
            raise ValueError('Manufacturing steps are required')
        sequences, planned = set(), 0
        for step in steps:
            if not isinstance(step, dict) or type(step.get('hold_point')) is not bool:
                raise ValueError('Manufacturing step and hold-point flag are required')
            sequence = step.get('sequence')
            minutes = step.get('planning_minutes')
            if type(sequence) is not int or sequence < 1 or sequence in sequences:
                raise ValueError('Manufacturing step sequence must be a unique positive integer')
            if type(minutes) is not int or minutes < 1:
                raise ValueError('Manufacturing step duration must be a positive integer')
            sequences.add(sequence); planned += minutes
            _nonempty(step.get('name'), 'Manufacturing step name')
            _nonempty(step.get('instruction'), 'Manufacturing step instruction')
        if planned != cycle:
            raise ValueError('Manufacturing step durations must equal the planning cycle')
    if coverage.get('method_count') != len(methods):
        raise ValueError('Manufacturing method coverage count mismatch')
    if coverage.get('product_rows') != len(product_ids) or coverage.get('covered_product_rows') != len(product_ids):
        raise ValueError('Manufactured product coverage count mismatch')
    if coverage.get('tooling_count') != len(tooling_ids) or coverage.get('uncovered_product_ids') != []:
        raise ValueError('Manufacturing tooling or uncovered-product count mismatch')
    _nonempty(document.get('revision'), 'Manufacturing revision')
    _nonempty(document.get('status'), 'Manufacturing status')
    _nonempty(document.get('release_boundary'), 'Manufacturing release boundary')
    for path_field, hash_field in (('source_file', 'source_sha256'),
                                   ('product_manifest', 'product_manifest_sha256')):
        _nonempty(document.get(path_field), 'Manufacturing source path')
        if not isinstance(document.get(hash_field), str) or not re.fullmatch(r'[0-9a-f]{64}', document[hash_field]):
            raise ValueError('Manufacturing source checksum is required')
    return document


def validate_method_sources(document, root):
    """Bind generated method coverage to its tracked source and product manifest."""
    validate_method_document(document)
    root = Path(root).resolve()
    resolved = {}
    for path_field, hash_field in (('source_file', 'source_sha256'),
                                   ('product_manifest', 'product_manifest_sha256')):
        path = (root / document[path_field]).resolve()
        if root not in path.parents or not path.is_file():
            raise ValueError('Manufacturing source path escapes or is missing')
        if hashlib.sha256(path.read_bytes()).hexdigest() != document[hash_field]:
            raise ValueError('Manufacturing source changed; regenerate method coverage')
        resolved[path_field] = path
    manifest = json.loads(resolved['product_manifest'].read_text())
    manifest_ids = {row.get('id') for row in manifest.get('product_items', [])
                    if isinstance(row, dict) and row.get('id')}
    method_ids = {item for method in document['method'] for item in method['product_ids']}
    if not manifest_ids or method_ids != manifest_ids:
        raise ValueError('Manufacturing methods do not cover the bound product manifest')
    return document


def validate_method_metadata(method):
    """Validate the compact method definition carried by a supervisory package."""
    if not isinstance(method, dict) or method.get('schema') != FACTORY_METHOD_SCHEMA:
        raise ValueError('Factory equipment requires manufacturing method metadata')
    _identity(method.get('method_id'), 'manufacturing method identity')
    _nonempty(method.get('title'), 'Manufacturing method title')
    _nonempty(method.get('work_center'), 'Manufacturing work center')
    _nonempty(method.get('release_gate'), 'Manufacturing release gate')
    _nonempty(method.get('release_boundary'), 'Manufacturing release boundary')
    _nonempty(method.get('document_revision'), 'Manufacturing document revision')
    _nonempty(method.get('document_status'), 'Manufacturing document status')
    _nonempty(method.get('source_file'), 'Manufacturing source file')
    _nonempty(method.get('product_manifest'), 'Manufacturing product manifest')
    for field in ('source_sha256', 'product_manifest_sha256'):
        if not isinstance(method.get(field), str) or not re.fullmatch(r'[0-9a-f]{64}', method[field]):
            raise ValueError('Manufacturing source checksum is required')
    if type(method.get('crew_size')) is not int or method['crew_size'] < 1:
        raise ValueError('Manufacturing crew size must be a positive integer')
    if type(method.get('planning_cycle_minutes')) is not int or method['planning_cycle_minutes'] < 1:
        raise ValueError('Manufacturing planning cycle must be a positive integer')
    _identity_list(method.get('product_ids'), 'manufactured product identity')
    _identity_list(method.get('tooling_ids'), 'manufacturing tooling identity')
    _identity_list(method.get('source_ids'), 'manufacturing source identity')
    steps = method.get('steps')
    if not isinstance(steps, list) or not steps:
        raise ValueError('Manufacturing step summaries are required')
    sequences, planned = set(), 0
    for step in steps:
        if not isinstance(step, dict):
            raise ValueError('Invalid manufacturing step summary')
        sequence, minutes = step.get('sequence'), step.get('planning_minutes')
        if (type(step.get('hold_point')) is not bool or
                type(sequence) is not int or sequence < 1 or sequence in sequences or
                type(minutes) is not int or minutes < 1 or
                not isinstance(step.get('name'), str) or not step['name'].strip()):
            raise ValueError('Invalid manufacturing step summary')
        sequences.add(sequence); planned += minutes
    if planned != method['planning_cycle_minutes']:
        raise ValueError('Manufacturing step summaries must equal the planning cycle')
    return method


def factory_templates(document):
    """Create one deterministic, read-only view per real manufacturing method."""
    validate_method_document(document)
    templates = {}
    for source in document['method']:
        method_id = source['id']
        key = 'factory-' + method_id.lower()
        metadata = dict(schema=FACTORY_METHOD_SCHEMA, method_id=method_id,
            title=source['title'], work_center=source['work_center'], crew_size=source['crew_size'],
            planning_cycle_minutes=source['planning_cycle_minutes'], product_ids=copy.deepcopy(source['product_ids']),
            tooling_ids=copy.deepcopy(source['tooling_ids']), source_ids=copy.deepcopy(source['source_ids']),
            steps=[{field: step[field] for field in ('sequence', 'name', 'planning_minutes', 'hold_point')}
                   for step in source['steps']],
            release_gate=source['release_gate'], release_boundary=document['release_boundary'],
            document_revision=document['revision'], document_status=document['status'],
            source_file=document['source_file'], source_sha256=document['source_sha256'],
            product_manifest=document['product_manifest'],
            product_manifest_sha256=document['product_manifest_sha256'])
        validate_method_metadata(metadata)
        templates[key] = dict(label=source['title'], component_type_id=method_id,
            asset_types=['depots-production'], source_crates=[], manufacturing_method=metadata,
            measurements={
                'cycle_progress_pct': {'unit': '%', 'min': 0, 'max': 100, 'stale_seconds': 10},
                'cell_unavailable': {'unit': 'bool', 'min': 0, 'max': 1, 'stale_seconds': 10},
                'quality_hold': {'unit': 'bool', 'min': 0, 'max': 1, 'stale_seconds': 10},
            }, alarms=[
                {'id': 'cell-unavailable', 'measurement': 'cell_unavailable', 'high': 1,
                 'clear_below': 0.5, 'delay_seconds': 4, 'repeat_seconds': 300, 'maintenance': True,
                 'response': 'Review the named method, work centre and tooling; reschedule native ERP work only after accountable production review.'},
                {'id': 'quality-hold', 'measurement': 'quality_hold', 'high': 1,
                 'clear_below': 0.5, 'delay_seconds': 4, 'repeat_seconds': 300, 'maintenance': True,
                 'response': 'Quarantine affected output and complete the method release gate and quality review; this signal does not accept, reject or release product.'},
            ], commands={})
    return templates


def factory_control_state(controls, method_ids):
    """Validate explicit simulation fixtures once for a city's deployed methods."""
    method_ids = set(method_ids)
    target = controls.get('factory_method', DEFAULT_SIMULATION_METHOD)
    _identity(target, 'factory simulation method')
    if target not in method_ids:
        raise ValueError('Factory simulation method is not deployed')
    result = {'factory_method': target}
    for name in ('factory_cell_unavailable', 'factory_process_excursion'):
        value = controls.get(name, False)
        if type(value) is not bool:
            raise ValueError('Boolean factory simulation fixture required')
        result[name] = value
    progress = controls.get('factory_cycle_progress_pct', 0)
    if isinstance(progress, bool) or not isinstance(progress, (int, float)) or not math.isfinite(progress) or not 0 <= progress <= 100:
        raise ValueError('Factory cycle progress fixture must be between 0 and 100')
    result['factory_cycle_progress_pct'] = progress
    return result


def factory_measurements(equipment, state):
    """Project validated simulation fixtures onto one method; never infer QA release."""
    method = validate_method_metadata(equipment.get('manufacturing_method'))
    selected = method['method_id'] == state['factory_method']
    return {
        (equipment['equipment_type'], 'cycle_progress_pct'): state['factory_cycle_progress_pct'] if selected else 0,
        (equipment['equipment_type'], 'cell_unavailable'): int(selected and state['factory_cell_unavailable']),
        (equipment['equipment_type'], 'quality_hold'): int(selected and state['factory_process_excursion']),
    }
