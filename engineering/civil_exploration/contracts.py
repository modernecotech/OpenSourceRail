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


from osr_mech.schema_validation import validate


def validate_study(value):
    validate(value, load(HERE/'schemas/study.json'))
    if len({c['name'] for c in value['candidates']}) != len(value['candidates']):
        raise ValueError('duplicate candidate names')
    if len({s['name'] for s in value['ground_scenarios']}) != len(value['ground_scenarios']):
        raise ValueError('duplicate ground scenarios')
    if 'concrete' in value.get('material_records',{}):
        raise ValueError('reference concrete belongs in material, not a second record')
    evidence=value.get('evidence_refs',{})
    claims=[('foundation',value['foundation']['site_verified']),('train',value['train']['supplier_verified']),
            ('material',value['material']['measured'])]
    claims += [('ground:'+g['name'],g['calibrated']) for g in value['ground_scenarios']]
    claims += [('material:'+name,m['measured']) for name,m in value.get('material_records',{}).items()]
    claims += [(role,value[role]['measured']) for role in ('support_material','foundation_material') if role in value]
    for role,claimed in claims:
        if claimed and role not in evidence:raise ValueError('measured/calibrated claim needs controlled evidence: '+role)
    for role,receipt in evidence.items():
        path=(ROOT/receipt['source']).resolve()
        if Path(receipt['source']).is_absolute() or not path.is_relative_to(ROOT) or not path.is_file() or sha(path)!=receipt['sha256']:
            raise ValueError('measured evidence source missing/stale: '+role)
    for candidate in value['candidates']:
        ratio = value['route_length_m']/candidate['deck']['span_m']
        if not math.isclose(ratio, round(ratio), abs_tol=1e-10):
            raise ValueError('common route length must contain whole spans')
        if candidate['deck']['family'] == 'pi' and candidate['deck']['parameters']:
            raise ValueError('canonical Pi section parameters cannot be overridden')
        if candidate['pier']['family'] == 'solid' and candidate['pier']['parameters']:
            raise ValueError('canonical solid pier parameters cannot be overridden')
        if candidate['deck']['family'] in ('uhpc-ribbed','hybrid-shell','frp-composite-I','steel-composite-I'):
            role={'uhpc-ribbed':'uhpc','steel-composite-I':'steel'}.get(candidate['deck']['family'],'frp')
            if role not in value.get('material_records',{}):
                raise ValueError('research family requires explicit material record: '+role)
        if candidate['pier']['family']=='double-skin-hybrid' and 'frp' not in value.get('material_records',{}):
            raise ValueError('hybrid pier requires explicit FRP material record')
    from osr_mech.civil.exploration import foundation_geometry
    foundation_geometry(value['foundation'])
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
    paths = list(HERE.rglob('*.py'))+list((HERE/'schemas').glob('*.json'))+list((HERE/'config').glob('*.json'))
    paths += list((ROOT/'design/component-catalogue/src/osr_mech/civil').glob('*.py'))
    paths += [ROOT/'design/component-catalogue/src/osr_mech'/name for name in ('cad.py', 'common.py', 'provenance.py', 'schema_validation.py', 'family_definition.py')]
    paths += [ROOT/'engineering/analysis/benchmarks/civil/exploration.py', ROOT/'tools/automation/civil-study.py']
    paths += [ROOT/name for name in ('tools/automation/project_twin.py', 'tools/automation/civil_reference.py', 'engineering/analysis/benchmarks/civil_reference.py',
                                    'engineering/analysis/drainage_ground_design.py', 'engineering/analysis/solver_results.py',
                                    'lib/templates/foundation-catalog.toml')]
    reference = ROOT/'engineering/assurance/civil-reference'
    paths += [p for p in reference.rglob('*') if p.is_file()]
    return {p.relative_to(ROOT).as_posix(): sha(p) for p in sorted(paths)}
