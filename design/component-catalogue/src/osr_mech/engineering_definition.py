"""Instance engineering data extending the existing product tree.

Design studies, supplier declarations and build measurements occupy separate
slots. An envelope never supplies mass through its volume. Content fingerprints
invalidate dependent calculations and inspection results without erasing history.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

from .family_definition import ROOT, family_definition
from .vehicle_mass_properties import mass_properties, inertia_tensor
from .schema_validation import validate as validate_schema

SCHEMA = "osr-shared-engineering/1"
STATES = {"as-designed", "as-built", "as-maintained"}
SOURCES = {"design", "supplier", "measured"}


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def load_definition(path):
    def pairs(values):
        result={}
        for key,value in values:
            if key in result:raise ValueError('duplicate engineering JSON field: '+key)
            result[key]=value
        return result
    def constant(value):raise ValueError('nonfinite engineering JSON value: '+value)
    return json.loads(Path(path).read_text(),object_pairs_hook=pairs,parse_constant=constant)


def number(value, name, *, minimum=None):
    if type(value) not in (int, float) or not math.isfinite(value) or (minimum is not None and value < minimum):
        raise ValueError(f"invalid {name}")
    return value


def _keys(value, required, optional=()):
    if not isinstance(value, dict) or set(value)-set(required)-set(optional) or set(required)-set(value):
        raise ValueError('engineering fields missing or unknown: ' + ', '.join(required))


def evidence(record, root=ROOT):
    _keys(record, ('path', 'sha256', 'kind'))
    if record['kind'] not in ('supplier', 'measurement', 'calibration', 'design'):
        raise ValueError('unknown evidence kind')
    path = Path(record['path'])
    base = Path(root).resolve(); source = (base/path).resolve()
    if path.is_absolute() or '..' in path.parts or not source.is_relative_to(base) or not source.is_file():
        raise ValueError('evidence must be a retained file inside its controlled root')
    if hashlib.sha256(source.read_bytes()).hexdigest() != record['sha256']:
        raise ValueError('stale engineering evidence: ' + str(path))


def _transform(value):
    import numpy as np
    _keys(value, ('translation_m', 'rotation'))
    if len(value['translation_m']) != 3:
        raise ValueError('three translation coordinates required')
    for x in value['translation_m']: number(x, 'translation')
    r = np.asarray(value['rotation'])
    if (r.shape != (3, 3) or r.dtype.kind not in 'if' or not np.isfinite(r).all() or
        not np.allclose(r.T @ r, np.eye(3), atol=1e-10) or not np.isclose(np.linalg.det(r), 1., atol=1e-10)):
        raise ValueError('proper orthonormal engineering transform required')


def catalogue_template(design):
    """Unfilled physical slots use existing product IDs, quantities and parents.

    Non-counted area/length quantities remain a single unresolved allocation;
    production must split kits/areas into physical parts before mass closure.
    """
    slots = []
    for product in design.product_items:
        quantity = product.quantity_per_trainset
        if quantity <= 0: continue
        count = int(quantity) if float(quantity).is_integer() and product.unit not in ('m', 'm2', 'kg') else 1
        for position in range(count):
            slots.append(dict(id=f'{product.id}/slot-{position + 1}', part_id=product.id,
                revision='A-DRAFT', serial=None, batch=None, parent=product.parent,
                quantity=1 if count > 1 else quantity, unit=product.unit,
                geometry=dict(kind=product.maturity.value, source=list(product.source_refs),
                              material_regions=[], thickness_m=None, process=None),
                transform=None, datums={}, body=None, bogie=None, axle=None,
                scope=[f'{product.id}/slot-{position + 1}'], property_source='design',
                properties=dict(design=None, supplier=None, measured=None),
                requirements=list(product.acceptance), inspections=[]))
    return dict(schema=SCHEMA, revision='A-DRAFT', state='as-designed', asset_id=None,
                family=design.family.value, family_definition=family_definition(design.family.value), instances=slots, joints=[], bridge=None,
                requirements=[], inspections=[],
                notes='Unfilled instance allocation from the existing EBOM; manufacturing dimensions and mass remain open.')


def validate(model, *, root=ROOT, catalogue_ids=None):
    schema=load_definition(ROOT/'design/component-catalogue/schemas/shared-engineering-model.json')
    validate_schema(model,schema)
    _keys(model, ('schema', 'revision', 'state', 'asset_id', 'family', 'family_definition', 'instances', 'joints', 'bridge', 'requirements', 'inspections'), ('notes',))
    if model['schema'] != SCHEMA or model['state'] not in STATES or not model['revision']:
        raise ValueError('invalid engineering revision/configuration')
    definition = model['family_definition']
    current = family_definition(model['family'])
    if definition.get('schema') != current['schema'] or definition.get('family') != model['family']:
        raise ValueError('frozen family definition belongs to another schema/family')
    if model['state']=='as-designed' and definition != current:
        raise ValueError('as-designed family definition is stale; regenerate from the authoritative profile')
    if (type(definition['car_count']) is not int or definition['car_count'] != len(definition['cars']) or
        definition['car_count'] != definition['profile']['cars'] or
        not math.isclose(sum(c['length_m'] for c in definition['cars']),definition['length_m']) or
        not math.isclose(definition['profile']['length_m'],definition['length_m'])):
        raise ValueError('frozen family dimensions do not reconcile')
    if model['state'] != 'as-designed' and not model['asset_id']:
        raise ValueError('built and maintained configurations need an individual asset')
    if catalogue_ids is None:
        from .buildable_trainset import buildable_trainset_design
        from .common import ConsistFamily
        design = buildable_trainset_design(ConsistFamily(model['family']))
        catalogue_ids = {p.id for p in design.product_items} | {p.id for p in design.assemblies}
    ids = set(); body_ids = {r['id'] for r in definition['cars']}; bogie_ids = {r['id'] for r in definition['bogies']}
    if len(body_ids)!=len(definition['cars']) or len(bogie_ids)!=len(definition['bogies']):
        raise ValueError('frozen family body/bogie identities overlap')
    for body in definition['cars']:
        if len(body['supports'])!=2 or len(set(body['supports']))!=2 or not set(body['supports'])<=bogie_ids:
            raise ValueError('frozen body needs two known distinct bogie supports')
    for row in model['instances']:
        _keys(row, ('id', 'part_id', 'revision', 'serial', 'batch', 'parent', 'quantity', 'unit', 'geometry', 'transform', 'datums', 'body', 'bogie', 'axle', 'scope', 'property_source', 'properties', 'requirements', 'inspections'))
        if not row['id'] or row['id'] in ids or row['part_id'] not in catalogue_ids or not row['revision']:
            raise ValueError('duplicate/unknown component instance or product revision')
        ids.add(row['id']); number(row['quantity'], 'instance quantity', minimum=0)
        if row['property_source'] not in SOURCES or set(row['properties']) != SOURCES:
            raise ValueError('separate design/supplier/measured property slots required')
        if row['body'] is not None and row['body'] not in body_ids:
            raise ValueError('unknown body attachment')
        if row['bogie'] is not None and row['bogie'] not in bogie_ids:
            raise ValueError('unknown bogie attachment')
        if row['axle'] is not None and (type(row['axle']) is not int or row['axle'] not in (1, 2) or row['bogie'] is None):
            raise ValueError('wheelset needs an identified bogie and axle')
        _keys(row['geometry'], ('kind', 'source', 'material_regions', 'thickness_m', 'process'))
        if row['geometry']['kind']=='osr-parametric-reference':
            from .automated_geometry import from_source
            from_source(row['geometry'])
        for reference in row['geometry']['source']:
            if isinstance(reference, dict):evidence(reference, root)
            elif not isinstance(reference, str) or not reference:raise ValueError('geometry source identity required')
        if row['geometry']['kind'] in ('released-solid','supplier-installation') and (len(row['geometry']['source'])!=1 or not isinstance(row['geometry']['source'][0],dict)):
            raise ValueError('released/supplier installation geometry needs one retained geometry source')
        if row['geometry']['thickness_m'] is not None:
            number(row['geometry']['thickness_m'], 'material thickness', minimum=0)
        if row['transform'] is not None: _transform(row['transform'])
        for transform in row['datums'].values(): _transform(transform)
        for source, props in row['properties'].items():
            if props is None: continue
            _keys(props, ('mass_kg', 'cg_m', 'inertia_tensor_kg_m2', 'uncertainty_kg', 'position_uncertainty_m', 'inertia_uncertainty_kg_m2', 'basis', 'evidence'))
            for key in ('mass_kg', 'uncertainty_kg', 'position_uncertainty_m', 'inertia_uncertainty_kg_m2'):
                if props[key] is not None:number(props[key], key, minimum=0)
            if (props['cg_m'] is not None and len(props['cg_m']) != 3) or not props['basis'] or (props['uncertainty_kg'] is not None and props['mass_kg'] is not None and props['uncertainty_kg'] > props['mass_kg']):
                raise ValueError('property basis, CG and nonnegative uncertainty required')
            if props['cg_m'] is not None:
                for x in props['cg_m']: number(x, 'CG')
            if props['inertia_tensor_kg_m2'] is not None:inertia_tensor(props['inertia_tensor_kg_m2'])
            if source != 'design':
                if not props['evidence'] or props['evidence']['kind'] != ('supplier' if source == 'supplier' else 'measurement'):
                    raise ValueError('supplier/measured values require matching retained evidence')
            if props['evidence'] is not None: evidence(props['evidence'], root)
        if model['state'] != 'as-designed' and not (row['serial'] or row['batch']):
            raise ValueError('physical configuration needs serial or batch identity')
    joints = set()
    instances = {r['id']: r for r in model['instances']}
    for row in model['instances']:
        if row['parent'] not in ids | catalogue_ids | body_ids:
            raise ValueError('unknown parent assembly')
        visited={row['id']};parent=row['parent']
        while parent in instances:
            if parent in visited:raise ValueError('cyclic parent assembly')
            visited.add(parent);parent=instances[parent]['parent']
    physical_serials=[(r['part_id'],r['serial']) for r in model['instances'] if r['serial']]
    if len(physical_serials)!=len(set(physical_serials)):
        raise ValueError('duplicate part/serial physical identity')
    for joint in model['joints']:
        _keys(joint, ('id', 'revision', 'connection', 'type', 'endpoints', 'permitted_motion', 'property_source', 'properties', 'definition', 'requirements', 'inspections'))
        if not joint['id'] or joint['id'] in joints or not joint['revision']:
            raise ValueError('duplicate or unrevisioned physical joint')
        joints.add(joint['id'])
        if joint['type'] not in ('fixed', 'revolute', 'slider', 'bolted', 'welded', 'bonded', 'suspension', 'articulation'):
            raise ValueError('unknown physical joint type')
        if len(joint['endpoints']) != 2 or joint['endpoints'][0]['instance'] == joint['endpoints'][1]['instance']:
            raise ValueError('two different joint endpoint instances required')
        for endpoint in joint['endpoints']:
            _keys(endpoint, ('instance', 'datum'))
            instance = instances.get(endpoint['instance'])
            if instance is None or endpoint['datum'] not in instance['datums']:
                raise ValueError('joint references an unknown instance datum')
        if set(joint['properties']) != SOURCES or joint['property_source'] not in SOURCES:
            raise ValueError('joint design/supplier/measured slots required')
        for source, props in joint['properties'].items():
            if props is None: continue
            _keys(props, ('stiffness_n_m', 'damping_ns_m', 'friction_coefficient', 'lower_stop_m', 'upper_stop_m', 'basis', 'evidence'))
            for key in ('stiffness_n_m', 'damping_ns_m', 'friction_coefficient'):
                number(props[key], key, minimum=0)
            for key in ('lower_stop_m', 'upper_stop_m'):
                if props[key] is not None: number(props[key], key)
            if (props['lower_stop_m'] is not None and props['upper_stop_m'] is not None and props['lower_stop_m'] >= props['upper_stop_m']) or not props['basis']:
                raise ValueError('ordered joint stops and property basis required')
            if source != 'design' and (props['evidence'] is None or props['evidence']['kind'] != ('supplier' if source == 'supplier' else 'measurement')):
                raise ValueError('joint supplier/measured properties need evidence')
            if props['evidence'] is not None: evidence(props['evidence'], root)
    # Scope IDs identify physical coverage independently of aggregate mass rows.
    scopes = [item for r in model['instances'] for item in r['scope']]
    if len(scopes) != len(set(scopes)) or any(not r['scope'] for r in model['instances']):
        raise ValueError('component scopes overlap or are empty')
    for inspection in model['inspections']:
        _keys(inspection, ('id', 'instance', 'characteristic', 'unit', 'minimum', 'maximum', 'dependencies'))
        if inspection['instance'] not in ids:
            raise ValueError('inspection targets an unknown instance')
        for key in ('minimum', 'maximum'):
            if inspection[key] is not None: number(inspection[key], 'inspection bound')
        if inspection['minimum'] is not None and inspection['maximum'] is not None and inspection['minimum'] > inspection['maximum']:
            raise ValueError('unordered inspection limits')
    if len({i['id'] for i in model['inspections']}) != len(model['inspections']):
        raise ValueError('duplicate inspection characteristic')
    fingerprint(model)  # Reject nonfinite values anywhere, including unconsumed metadata.
    return definition


def component_mass_records(model):
    import numpy as np
    records = []
    for row in model['instances']:
        props = row['properties'][row['property_source']]
        record = dict(id=row['id'], included_items=row['scope'], body=row['body'], bogie=row['bogie'])
        if props is None or row['transform'] is None or any(props[k] is None for k in ('mass_kg','cg_m','uncertainty_kg')):
            record.update(evidence_record=None, mass_kg=None, uncertainty_kg=None, x_m=None, y_m=None, z_m=None)
        else:
            t = row['transform']; location = np.asarray(t['translation_m']) + np.asarray(t['rotation']) @ props['cg_m']
            record.update(mass_kg=props['mass_kg'], uncertainty_kg=props['uncertainty_kg'],
                          x_m=float(location[0]), y_m=float(location[1]), z_m=float(location[2]),
                          position_uncertainty_m=props['position_uncertainty_m'], rotation_matrix=t['rotation'],
                          inertia_tensor_kg_m2=props['inertia_tensor_kg_m2'], inertia_uncertainty_kg_m2=props['inertia_uncertainty_kg_m2'],
                          evidence_record=props['evidence'] or {'kind': 'design', 'basis': props['basis']})
        records.append(record)
    return records


def model_mass_properties(model, *, root=ROOT):
    definition = validate(model, root=root)
    records = component_mass_records(model)
    bodies = [r for r in definition['cars'] if any(c['body'] == r['id'] for c in model['instances'])]
    active = {s for b in bodies for s in b['supports']} | {r['bogie'] for r in model['instances'] if r['bogie']}
    bogies = [r for r in definition['bogies'] if r['id'] in active]
    result = mass_properties(records, [s for r in model['instances'] for s in r['scope']], bodies, bogies)
    result['configuration_sha256'] = fingerprint(model)
    result['property_sources'] = {r['id']: r['property_source'] for r in model['instances']}
    return result


def verification_register(model, previous=None, *, root=ROOT, implementation_hashes=None):
    definition = validate(model, root=root)
    nodes = {'family': fingerprint(definition), 'bridge': fingerprint(model['bridge']),
             'requirements': fingerprint(model['requirements']), 'configuration': fingerprint([model['revision'], model['state'], model['asset_id']]),
             'implementation': fingerprint(implementation_hashes or {})}
    dependencies = {}
    for row in model['instances']:
        nodes['instance:' + row['id']] = fingerprint(row)
    for joint in model['joints']:
        key = 'joint:' + joint['id']; nodes[key] = fingerprint(joint)
        dependencies[key] = ['instance:' + e['instance'] for e in joint['endpoints']]
    dependencies['mass-properties'] = ['family', 'configuration', 'implementation'] + ['instance:' + r['id'] for r in model['instances']]
    dependencies['vehicle-model'] = ['mass-properties', 'implementation'] + ['joint:' + j['id'] for j in model['joints']]
    dependencies['vehicle-dynamics'] = ['vehicle-model', 'bridge', 'requirements']
    dependencies['bridge-demand'] = ['vehicle-dynamics', 'bridge', 'requirements']
    dependencies['cost'] = ['mass-properties', 'bridge'] + ['joint:' + j['id'] for j in model['joints']]
    for row in model['instances']:
        dependencies['drawing:' + row['id']] = ['instance:' + row['id'], 'family', 'implementation']
    for inspection in model['inspections']:
        key = 'inspection:' + inspection['id']; nodes[key] = fingerprint(inspection)
        dependencies[key] = ['instance:' + inspection['instance'], 'configuration', 'requirements', *inspection['dependencies']]
    resolved = set(); visiting = set()
    def resolve(key):
        if key in visiting: raise ValueError('cyclic verification dependencies')
        if key in resolved: return nodes[key]
        if key not in nodes and key not in dependencies: raise ValueError('unknown verification dependency: ' + key)
        visiting.add(key)
        if key in dependencies:
            nodes[key] = fingerprint([nodes.get(key), [(d, resolve(d)) for d in dependencies[key]]])
        visiting.remove(key); resolved.add(key)
        return nodes[key]
    for key in list(dependencies): resolve(key)
    old = (previous or {}).get('nodes', {})
    return dict(schema='osr-verification-dependencies/1', configuration_sha256=fingerprint(model),
        nodes=nodes, dependencies=dependencies, invalidated=sorted(k for k, v in nodes.items() if k in old and old[k] != v),
        removed=sorted(set(old)-set(nodes)), pending=sorted(k for k in nodes if k not in old),
        engineering_released=False, inspections_reaccepted=False)


def evaluate_inspection(model, record, *, root=ROOT):
    """Compare a revision/serial-bound measurement; leave authority release separate."""
    validate(model, root=root)
    _keys(record, ('inspection_id', 'configuration_sha256', 'instance', 'serial', 'batch', 'unit', 'value', 'calibration', 'evidence'))
    inspection = next((i for i in model['inspections'] if i['id'] == record['inspection_id']), None)
    row = next((i for i in model['instances'] if i['id'] == record['instance']), None)
    if inspection is None or row is None or inspection['instance'] != record['instance']:
        raise ValueError('unknown measurement instance/characteristic')
    if model['state'] == 'as-designed' or record['configuration_sha256'] != fingerprint(model):
        raise ValueError('measurement requires the exact physical configuration revision')
    if (record['serial'], record['batch']) != (row['serial'], row['batch']) or record['unit'] != inspection['unit']:
        raise ValueError('measurement serial/batch/unit mismatch')
    if record['calibration']['kind'] != 'calibration' or record['evidence']['kind'] != 'measurement':
        raise ValueError('measurement and calibration evidence required')
    evidence(record['calibration'], root); evidence(record['evidence'], root)
    value = number(record['value'], 'measured value')
    limits = [inspection['minimum'], inspection['maximum']]
    passed = None if all(x is None for x in limits) else ((limits[0] is None or value >= limits[0]) and (limits[1] is None or value <= limits[1]))
    return dict(inspection_id=inspection['id'], within_defined_limits=passed, accepted=False,
                result_sha256=fingerprint(record), configuration_sha256=fingerprint(model),
                design_revision=model['revision'], part_revision=row['revision'], asset_id=model['asset_id'],
                serial=row['serial'], batch=row['batch'], measurement_evidence=record['evidence'], calibration_evidence=record['calibration'])


def engineering_identity(model, *, root=ROOT):
    """Portable characteristic map for an ERP execution proposal/source package."""
    validate(model, root=root)
    instances={r['id']:r for r in model['instances']}
    rows=[]
    for inspection in model['inspections']:
        r=instances[inspection['instance']]
        rows.append(dict(inspection_id=inspection['id'],instance_id=r['id'],part_id=r['part_id'],part_revision=r['revision'],
            serial=r['serial'],batch=r['batch'],characteristic=inspection['characteristic'],unit=inspection['unit'],
            minimum=inspection['minimum'],maximum=inspection['maximum'],
            joint_ids=[j['id'] for j in model['joints'] if any(e['instance']==r['id'] for e in j['endpoints'])]))
    payload=dict(schema='osr-engineering-qa-map/1',configuration_sha256=fingerprint(model),design_revision=model['revision'],
                 state=model['state'],asset_id=model['asset_id'],characteristics=rows)
    payload['sha256']=fingerprint(payload)
    return payload
