"""Versioned reference values and architecture-specific requirement allocations."""
import gzip
import json
from pathlib import Path

from engineering.twin_workflow import core
from engineering.continuous_design import service

DATA=Path(__file__).parent/'data/baseline.json'
REFERENCE=core.ROOT/'engineering/data/baghdad-reference-parts.json'


def sources():
    result=service.source_snapshot()
    paths=[*Path(__file__).parent.glob('*.py'),*DATA.parent.glob('*.json'),REFERENCE,
        core.ROOT/'tools/automation/design-assemblies.py',core.ROOT/'engineering/analysis/tests/test_assembly_design.py',
        core.ROOT/'engineering/integration_programme/joints.py',core.ROOT/'engineering/design_delivery/pipeline.py',core.ROOT/'engineering/design_delivery/visuals.py',core.ROOT/'tools/automation/design-progress.py',core.ROOT/'tools/automation/design-progress-mesh.py']
    paths += list((core.ROOT/'engineering/analysis/tests').glob('test_closure_*.py'))
    paths += [*list((core.ROOT/'engineering/panel_materials').glob('*.py')),
              *list((core.ROOT/'engineering/panel_materials/config').glob('*')),
              core.ROOT/'engineering/analysis/tests/test_panel_materials.py',core.ROOT/'tools/automation/panel-material-study.py']
    paths += [core.ROOT/'OpenSourceRail_Full_Design_Closure_Plan_2026-10-19.pdf',
              core.ROOT/'lib/templates/rolling-stock.toml',core.ROOT/'lib/templates/track-geometry.toml',
              core.ROOT/'design/component-catalogue/src/osr_mech/rolling_stock/trainset.py']
    from . import site_bundle
    paths += [core.ROOT/name for name in site_bundle.paths()]
    graph=json.loads(gzip.decompress((core.PACKET/'specifications.json.gz').read_bytes()))
    paths += [core.ROOT/i['source'] for i in graph['items']]
    paths += [core.ROOT/p['source'] for p in core.read(REFERENCE)['parts'] if (core.ROOT/p['source']).is_file()]
    for path in paths:result[path.relative_to(core.ROOT).as_posix()]=core.sha(path)
    return result


def validate(policy):
    if policy['architecture']!='baghdad-six-car' or any(policy.get(k) is not False for k in core.FLAGS):raise ValueError('provisional Baghdad baseline required')
    ids=set()
    for fact in policy['facts']:
        if fact['id'] in ids:raise ValueError('duplicate baseline fact')
        ids.add(fact['id'])
        if fact['approved'] is not False or fact['value'] is None or not fact['unit'] or not fact['locator'] or not fact['applicability']:raise ValueError('sourced non-approved typed fact required')
        source=fact['source']
        if source not in policy['sources'] and (not source.startswith('engineering/') or '..' in Path(source).parts or not (core.ROOT/source).is_file()):raise ValueError('unbound baseline source')
        if fact['status'] not in {'published-reference','repository-provisional'}:raise ValueError('unknown evidence status')
    parts={p['id'] for p in core.read(REFERENCE)['parts']}
    for pilot in policy['pilots'].values():
        if any(i.removeprefix('baghdad:') not in parts for i in pilot['requirement_ids']):raise ValueError('pilot references missing authoritative Baghdad part')
        if not pilot['holds']:raise ValueError('pilot qualification holds required')
    return policy


def facts(policy):return {r['id']:r['value'] for r in policy['facts']}


def inventory(policy):
    graph=json.loads(gzip.decompress((core.PACKET/'specifications.json.gz').read_bytes()));items=[]
    for item in graph['items']:
        # Preserve the existing identity and data, with no inferred adoption of
        # the six-car inputs into LM3 or unreconciled station/product definitions.
        items.append(dict(id=item['id'],catalogue_id=item['catalogue_id'],title=item['title'],
            architecture='legacy-lm3' if item['catalogue_id'].startswith('LM3-') else 'reference-unreconciled',
            source=item['source'],source_sha256=item['source_sha256'],source_records=item['source_records'],
            required_detail_sections=item['required_detail_sections'],adopted_fact_ids=[],pilot=None,state='reference-preserved; architecture adoption open'))
    all_fact_ids=[f['id'] for f in policy['facts']]
    allocations={'ME-10':[i for i in all_fact_ids if i.startswith('connector.')],
        'ME-11':['climate.ambient','climate.baghdad_mean_july_max','climate.iraq_summer_max_context'],
        'ME-01':['train.mass_cases','train.car_length','steel.elastic_modulus','steel.density','steel.yield_by_thickness'],
        'CI-01':['train.mass_cases','train.car_length','bearing.uk_manufacture','bearing.reference_temperature','steel.yield_by_thickness']}
    for p in core.read(REFERENCE)['parts']:
        identity='baghdad:'+p['id'];pilot=next((k for k,v in policy['pilots'].items() if identity in v['requirement_ids']),None)
        items.append(dict(id=identity,catalogue_id=p['id'],title=p['title'],architecture='baghdad-six-car',
            source=REFERENCE.relative_to(core.ROOT).as_posix(),source_sha256=core.sha(REFERENCE),source_records=[dict(pointer='/parts/id='+p['id'],record=p)],
            required_detail_sections=graph['items'][0]['required_detail_sections'],adopted_fact_ids=allocations.get(p['id'],[]),pilot=pilot,
            state='source requirements enriched for provisional design' if allocations.get(p['id']) else 'source requirements retained; numeric component specification open'))
    return dict(schema='osr-assembly-requirements/1',items=items,existing_items=len(graph['items']),baghdad_reference_items=len(items)-len(graph['items']),
        packages=graph['packages'],identity_policy='Source identities retained; 69 Baghdad records are additional scoped records, not 69 newly designed components',**core.FLAGS)


def build():
    from . import closure,closure_evidence,contracts,cassette_system,families,integration,site_bundle
    policy=validate(core.read(DATA));inv=inventory(policy)
    return dict(policy=policy,inventory=inv,prototype=contracts.prototype_configuration(),
        completion_evidence=core.read(closure_evidence.DATA/'closure-evidence.json'),
        completion_trust=core.read(closure_evidence.DATA/'closure-trust.json'),
        family_crosswalk=contracts.crosswalk(inv),closure_plan=closure.plan(),
        registers=dict(sources=contracts.baseline_source_cards(policy)+cassette_system.SOURCE_CARDS,
            standards=contracts.standards_register(),families=families.registry(policy)),
        integration=integration.snapshot(policy),site=site_bundle.snapshot(),source_sha256=sources(),**core.FLAGS)
