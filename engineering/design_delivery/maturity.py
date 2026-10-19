"""Exact research allocations, distinct from authenticated engineering acceptance."""
from hashlib import sha256
import json

from engineering.twin_workflow import core

# Explicit catalogue allocations; similar titles never create allocations.
# These identify representative research units, not a production substitution
# or closure of the catalogue item's detail/acceptance requirements.
CIVIL_ALLOCATIONS={
    'OSR-TYPE-FDB074324FD0':'walkway-parapet',
    'OSR-TYPE-99A11C1DC30D':'pier',
    'OSR-TYPE-3FD9673EF391':'pier-cap',
    'OSR-TYPE-C966BC7372EC':'bearing',
    'OSR-TYPE-D36A7871D9B7':'deck',
}


def annotate(graph,selected,load):
    units=[];links=[];allocations={i['id']:[] for i in graph['items']}
    for candidate in selected:
        if candidate['kind']!='civil-kit-study':continue
        raw=load(candidate,'output/civil-kit.json')
        if raw is None:continue
        kit=json.loads(raw);result=json.loads(load(candidate,'result.json'))
        proof_raw=load(candidate,'result.json',confirmation=True)
        proof=json.loads(proof_raw) if proof_raw else {}
        definition_raw=load(candidate,'output/physical-contract.json',confirmation=True)
        definition=json.loads(definition_raw) if definition_raw else {}
        native_ids={p['id'] for p in definition.get('parts',[])}
        native_ok=proof.get('study_pass') is True and proof.get('verification',{}).get('levels',{}).get('native_geometry',{}).get('state')=='passed'
        key=candidate.get('key',candidate.get('row',{}).get('key'))
        confirmation=candidate.get('confirmation_key') or (candidate.get('confirmation') or {}).get('key')
        joints=kit.get('operation_graph',{}).get('joints',[])
        for unit in kit['units']:
            uid=unit['id'];part_ids=unit.get('physical_part_ids',[])
            # Geometry counts only where explicit part definitions exist. Cages
            # represented solely by a mass allowance do not gain geometry credit.
            geometry=bool(part_ids) and all(p in native_ids for p in part_ids)
            checks={n:v for n,v in result.get('checks',{}).items() if n.startswith('handling/'+uid+'/')}
            numerical={n:v for n,v in proof.get('checks',{}).items() if n.startswith(uid+'/')}
            joint_ids=sorted(j['id'] for j in joints if uid in j.get('endpoints',[]))
            mapped=[i for i in graph['items'] if CIVIL_ALLOCATIONS.get(i.get('catalogue_id'))==unit['category']
                and (i.get('catalogue_id')!='OSR-TYPE-D36A7871D9B7' or kit['variables']['architecture']=='large-span')]
            evidence_id=key+'/'+uid
            entry=dict(id=evidence_id,candidate_key=key,unit_id=uid,unit_revision=unit['revision'],category=unit['category'],
                requirement_item_ids=[i['id'] for i in mapped],joint_ids=joint_ids,part_ids=part_ids,
                stages=dict(geometry_defined=geometry,analytically_screened=bool(checks) and all(v is True for v in checks.values()),
                    native_geometry_verified=geometry and native_ok,numerically_screened=bool(numerical) and all(v is True for v in numerical.values()),
                    manufacturing_qualified=False),
                analytical_checks=checks,numerical_checks=numerical,
                evidence=dict(unit_definition=dict(path=key+'/output/civil-kit.json',sha256=sha256(raw).hexdigest()),
                    analytical=dict(path=key+'/result.json',sha256=sha256(load(candidate,'result.json')).hexdigest()),
                    native=dict(path=confirmation+'/output/physical-contract.json',sha256=sha256(definition_raw).hexdigest()) if definition_raw else None,
                    confirmation=dict(path=confirmation+'/result.json',sha256=sha256(proof_raw).hexdigest()) if proof_raw else None),
                unresolved=unit.get('unresolved',[]),connection_resistance_qualified=False,accepted=False,
                scope='Representative research geometry and listed handling/beam screens only; no complete resistance, physical validation or manufacturing qualification')
            units.append(entry)
            for item in mapped:
                allocations[item['id']].append(evidence_id)
                for section in item['required_detail_sections']:
                    links.append(dict(requirement_id=item['id']+'/'+core.digest(section)[:16],requirement=section,
                        item_id=item['id'],unit_evidence_id=evidence_id,unit_revision=unit['revision'],joint_ids=joint_ids,
                        satisfied=False,scope='Research allocation only; section-specific accepted evidence remains required'))
    counts={stage:sum(u['stages'][stage] for u in units) for stage in (
        'geometry_defined','analytically_screened','native_geometry_verified','numerically_screened','manufacturing_qualified')}
    counts.update(representative_unit_revisions=len(units),allocated_authoritative_items=sum(bool(ids) for ids in allocations.values()))
    return dict(research_units=units,requirement_links=links,research_maturity_counts=counts,
        research_allocations=allocations,mapping_policy='Exact catalogue IDs and unit categories; research allocations are provisional and do not satisfy acceptance requirements')
