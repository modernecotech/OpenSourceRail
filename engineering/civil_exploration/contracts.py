"""Strict JSON contracts, content identities and input provenance."""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent


def encoded(value) -> bytes:
    return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False)+'\n').encode()


def identity(value) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('duplicate JSON key: '+key)
            result[key] = value
        return result
    return json.loads(path.read_text(), object_pairs_hook=unique,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError('nonfinite JSON: '+value)))


def validate(value, schema, location='$'):
    """Validate the bounded JSON Schema vocabulary used by our contracts."""
    types = schema.get('type', [])
    types = [types] if isinstance(types, str) else types
    matches = {'object': type(value) is dict, 'array': type(value) is list,
               'string': type(value) is str, 'number': type(value) in (int, float),
               'integer': type(value) is int, 'boolean': type(value) is bool, 'null': value is None}
    if types and not any(matches[t] for t in types):
        raise ValueError(location+': wrong type')
    if 'enum' in schema and value not in schema['enum']:
        raise ValueError(location+': unregistered value')
    if type(value) in (int, float):
        if not math.isfinite(value):
            raise ValueError(location+': nonfinite number')
        for key, failed in (('minimum', value < schema.get('minimum', -math.inf)),
                            ('maximum', value > schema.get('maximum', math.inf)),
                            ('exclusiveMinimum', value <= schema.get('exclusiveMinimum', -math.inf))):
            if failed:
                raise ValueError(location+': '+key)
    if type(value) is str and len(value) < schema.get('minLength', 0):
        raise ValueError(location+': empty string')
    if type(value) is dict:
        properties = schema.get('properties', {})
        if set(schema.get('required', []))-value.keys():
            raise ValueError(location+': missing required fields')
        if schema.get('additionalProperties') is False and value.keys()-properties.keys():
            raise ValueError(location+': unknown fields '+str(sorted(value.keys()-properties.keys())))
        for key, item in value.items():
            if key in properties:
                validate(item, properties[key], location+'.'+key)
            elif isinstance(schema.get('additionalProperties'), dict):
                validate(item, schema['additionalProperties'], location+'.'+key)
    if type(value) is list:
        if not schema.get('minItems', 0) <= len(value) <= schema.get('maxItems', math.inf):
            raise ValueError(location+': invalid array length')
        if schema.get('uniqueItems') and len({identity(v) for v in value}) != len(value):
            raise ValueError(location+': duplicate array entries')
        for i, item in enumerate(value):
            validate(item, schema.get('items', {}), location+f'[{i}]')


def validate_study(value):
    validate(value, load(HERE/'schemas/study.json'))
    if len({c['name'] for c in value['candidates']}) != len(value['candidates']):
        raise ValueError('duplicate candidate names')
    if len({s['name'] for s in value['ground_scenarios']}) != len(value['ground_scenarios']):
        raise ValueError('duplicate ground scenarios')
    for candidate in value['candidates']:
        ratio = value['route_length_m']/candidate['deck']['span_m']
        if not math.isclose(ratio, round(ratio), abs_tol=1e-10):
            raise ValueError('common route length must contain whole spans')
        if candidate['deck']['family'] == 'pi' and candidate['deck']['parameters']:
            raise ValueError('canonical Pi section parameters cannot be overridden')
        if candidate['pier']['family'] == 'solid' and candidate['pier']['parameters']:
            raise ValueError('canonical solid pier parameters cannot be overridden')
    train = value['train']
    if len(train['axle_offsets_m']) != len(train['axle_loads_kn']):
        raise ValueError('axle positions and loads differ in count')
    if train['axle_offsets_m'] != sorted(set(train['axle_offsets_m'])) or train['axle_offsets_m'][0] != 0:
        raise ValueError('axle offsets must be unique, sorted and start at zero')
    if value['analysis']['meshes'] != sorted(set(value['analysis']['meshes'])):
        raise ValueError('meshes must be distinct increasing refinement levels')
    for source, digest in value['sources_sha256'].items():
        path = (ROOT/source).resolve()
        if Path(source).is_absolute() or not path.is_relative_to(ROOT) or sha(path) != digest:
            raise ValueError('stale or uncontrolled study source: '+source)


def dependencies():
    paths = list(HERE.rglob('*.py'))+list((HERE/'schemas').glob('*.json'))
    paths += list((ROOT/'design/component-catalogue/src/osr_mech/civil').glob('*.py'))
    paths += [ROOT/'design/component-catalogue/src/osr_mech'/name for name in ('cad.py', 'common.py', 'provenance.py')]
    paths += [ROOT/'engineering/analysis/benchmarks/civil/exploration.py', ROOT/'tools/automation/civil-study.py']
    paths += [ROOT/name for name in ('tools/automation/civil_reference.py', 'engineering/analysis/benchmarks/civil_reference.py',
                                    'engineering/analysis/drainage_ground_design.py', 'engineering/analysis/solver_results.py')]
    reference = ROOT/'engineering/assurance/civil-reference'
    paths += [p for p in reference.rglob('*') if p.is_file()]
    return {p.relative_to(ROOT).as_posix(): sha(p) for p in sorted(paths)}
