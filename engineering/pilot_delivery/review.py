"""Compile actual controlled research documents into a same-candidate ERP review pack.

No business API is contacted. Document coverage is never hardware qualification.
"""
from copy import deepcopy
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import shutil
from xml.etree import ElementTree

from engineering.station_rail.common import identity, encoded, digest
from . import ROOT
from .model import validate_proposal

CONTRACT='deployment/erpnext/apps/osr_erpnext/osr_erpnext/candidate_delivery_contract.py'
_spec=importlib.util.spec_from_file_location('osr_wheel_delivery_contract',ROOT/CONTRACT)
contract=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(contract)
FLAGS=contract.FLAGS


def ordinary(root, relative, *, maximum=contract.MAX_ARTIFACT_BYTES):
    root=Path(root).absolute();relative=contract.safe_path(relative);path=root/relative
    if any(p.is_symlink() for p in (path,*path.parents)) or not path.is_file() or not path.resolve().is_relative_to(root.resolve()):
        raise ValueError('Ordinary in-root controlled artifact required: '+relative)
    if not 0<path.stat().st_size<=maximum:raise ValueError('Empty or oversized controlled artifact: '+relative)
    return path


def _payload(root, row, definition):
    path=ordinary(root,row['path'])
    if path.stat().st_size!=row['bytes'] or digest(path)!=row['sha256']:raise ValueError('Controlled payload bytes changed: '+row['path'])
    raw=path.read_bytes();kind=definition['document_type'];media=row['media_type']
    if kind=='drawing':
        if media=='image/svg+xml':
            tree=ElementTree.fromstring(raw)
            if tree.tag.rsplit('}',1)[-1]!='svg' or not any(e.tag.rsplit('}',1)[-1] in {'path','line','rect','circle','ellipse','polyline','polygon'} for e in tree.iter()):
                raise ValueError('A real nonempty SVG drawing is required')
        elif media=='application/pdf':
            if not raw.startswith(b'%PDF-') or b'%%EOF' not in raw[-2048:]:raise ValueError('A complete PDF drawing is required')
        elif media in {'model/step','application/step'}:
            if b'ISO-10303-21;' not in raw[:100] or b'END-ISO-10303-21;' not in raw[-200:]:raise ValueError('A complete STEP payload is required')
        else:raise ValueError('Supported drawing media type required')
    elif media=='application/json':
        value=json.loads(raw)
        expected='osr-controlled-research-'+('inspection' if kind=='inspection' else 'route')+'/1'
        field='characteristics' if kind=='inspection' else 'operations'
        if (value.get('schema')!=expected or value.get('identities')!=definition['identities'] or
                value.get('part_id')!=definition['part_id'] or value.get(field)!=definition[field]):
            raise ValueError('Inspection/routing payload differs from its controlled definition')
    else:raise ValueError('Machine-readable inspection/routing JSON required')
    return dict(row)


def source_assemblies(proposal, groups):
    """Derive logical research kits from existing source routes, never client BOMs.

    Grouping is a trusted compiler selection, not installed mating/placement
    evidence or an asserted hash of the separate door-module compiler output.
    """
    if not isinstance(groups,list) or not 1<=len(groups)<=contract.MAX_ASSEMBLIES:raise ValueError('Bounded source assembly group selection required')
    routes={r['id']:r for r in proposal['assembly_routes']};parts={p['id']:p for p in proposal['items']}
    nodes={};binding=proposal['identities'];group_ids=set()
    def node(name,quantity,occ,children,refs):
        value=dict(id=name,identities=deepcopy(binding),quantity_per_train=quantity,occurrence_ids=deepcopy(occ),children=children,
            source_reference=dict(proposal_id=proposal['proposal_id'],scope='source-authoritative-proposal-reference-only',physical_module_id=None,**refs),
            research_holds=['Logical counted research kit; installed mating, placement, assembly process cost and physical qualification remain unresolved'])
        value['definition_id']=identity(value);return value
    for group in groups:
        if not isinstance(group,dict) or set(group)!={'id','assembly_ids'}:raise ValueError('Select existing source assembly routes only')
        name=contract.text(group['id'],'group id',150);ids=group['assembly_ids']
        if name in group_ids or name in routes or name in parts:raise ValueError('Duplicate source assembly group')
        group_ids.add(name)
        if not isinstance(ids,list) or not ids or len(set(ids))!=len(ids) or any(i not in routes for i in ids):raise ValueError('Unique known source assembly routes required')
        quantities={routes[i]['occurrences_per_train'] for i in ids}
        if len(quantities)!=1:raise ValueError('Grouped source assemblies require matched per-train occurrence counts')
        count=next(iter(quantities))
        if type(count) is not int or not 1<=count<=100000:raise ValueError('Bounded positive source assembly count required')
        for rid in ids:
            occ=routes[rid]['assembly_occurrence_ids']
            if not isinstance(occ,list) or len(occ)!=count or len(set(occ))!=count:raise ValueError('Exact source assembly occurrence inventory required')
            for item in occ:contract.text(item,'source assembly occurrence',500)
        for rid in ids:
            route=routes[rid];children=[]
            for part_id in route['component_type_ids']:
                part=parts[part_id];q=part['quantity_per_train']/count
                if type(part['quantity_per_train']) is not int or not q.is_integer():raise ValueError('Integral source pieces per assembly required')
                children.append(dict(kind='part',id=part_id,quantity=int(q)))
            value=node(rid,count,route['assembly_occurrence_ids'],children,dict(source_route_sha256=identity(route)))
            if rid in nodes:raise ValueError('Source assembly cannot belong to two groups')
            nodes[rid]=value
        occurrences=['research-kit-'+identity(dict(group=name,source_occurrences=[routes[i]['assembly_occurrence_ids'][j] for i in ids])) for j in range(count)]
        nodes[name]=node(name,count,occurrences,[dict(kind='assembly',id=i,quantity=1) for i in ids],dict(source_routes={i:identity(routes[i]) for i in ids}))
    contract.validate_assemblies(list(nodes.values()),parts,binding,proposal['proposal_id'])
    return nodes


def compile_review_pack(proposal, documents, conversions, *, artifact_root, city,
                        source_root=ROOT, selected_part_ids=None, assembly_groups=None):
    """Pure bounded compiler API consumed by drawing producers and business adapters.

    documents: osr-controlled-research-documents/1 {identities, components:[
      {part_id, drawing:<sidecar.json>, inspection:<sidecar.json>, routing:<sidecar.json>}]}.
    conversions: keyed by part ID, with valuation_mode, source_part_sha256 and
    explicit stock/process decomposition when quantified-source-stock is chosen.
    """
    validate_proposal(proposal);contract.text(city,'city',100)
    root=Path(source_root)
    for name,want in proposal['source_sha256'].items():
        if digest(ordinary(root,name,maximum=64*1024**2))!=want:raise ValueError('Proposal source changed: '+name)
    if (documents.get('schema')!='osr-controlled-research-documents/1' or documents.get('identities')!=proposal['identities']):
        raise ValueError('Same-candidate controlled document index required')
    rows=documents.get('components')
    if not isinstance(rows,list) or len(rows)>contract.MAX_COMPONENTS:raise ValueError('Bounded component document index required')
    by_id={r['part_id']:r for r in rows}
    if len(by_id)!=len(rows):raise ValueError('Duplicate component document mapping')
    parts={p['id']:p for p in proposal['items']}
    if not set(by_id)<=set(parts) or not set(conversions)<=set(parts):raise ValueError('Unknown source component in review mapping')
    selected=sorted(set(selected_part_ids if selected_part_ids is not None else by_id))
    if not selected or not set(selected)<=set(by_id):raise ValueError('Explicit nonempty documented component scope required')
    if set(conversions)!=set(selected):raise ValueError('Exactly one reviewed conversion per selected component required')
    components=[];artifacts={}
    for part_id in selected:
        part=parts[part_id];mapping=by_id[part_id]
        if set(mapping)!={'part_id',*contract.DOCUMENT_TYPES}:raise ValueError('Every covered part needs drawing/inspection/routing sidecars')
        owned={}
        for kind in sorted(contract.DOCUMENT_TYPES):
            name=contract.safe_path(mapping[kind]);path=ordinary(artifact_root,name,maximum=2*1024**2)
            definition=json.loads(path.read_bytes());contract.validate_document(definition,part,proposal['identities'])
            if definition['document_type']!=kind:raise ValueError('Sidecar document type differs')
            entry=dict(path=name,sha256=digest(path),bytes=path.stat().st_size,definition=definition)
            owned[kind]=entry
            artifacts[name]=dict(path=name,sha256=digest(path),bytes=path.stat().st_size,media_type='application/json',role='controlled-'+kind+'-metadata')
            for row in definition['payloads']:
                item=_payload(artifact_root,row,definition)
                if item['path'] in artifacts and any(artifacts[item['path']][k]!=item[k] for k in ('sha256','bytes','media_type')):
                    raise ValueError('Conflicting controlled artifact definitions')
                artifacts[item['path']]=dict(item,role=kind+'-payload')
        conversion=deepcopy(conversions[part_id])
        if conversion.get('source_part_sha256')!=identity(part):raise ValueError('Conversion source part changed')
        stocks=contract.stock_lines(conversion,part)
        components.append(dict(source_part=deepcopy(part),source_part_sha256=identity(part),documents=owned,
            conversion=conversion,stock_lines=stocks,native_orders_released=False,physical_manufacture_validated=False))
    extra={}
    if assembly_groups is not None:
        nodes=source_assemblies(proposal,assembly_groups)
        contract.validate_assemblies(list(nodes.values()),{r['source_part']['id']:r['source_part'] for r in components},proposal['identities'],proposal['proposal_id'])
        extra['assemblies']=list(nodes.values())
    result=contract.seal(dict(schema='osr-wheel-delivery-review-pack/1',environment='simulation',city=city,
        identities=deepcopy(proposal['identities']),proposal_id=proposal['proposal_id'],proposal_sha256=identity(proposal),
        components=components,artifacts=[artifacts[k] for k in sorted(artifacts)],
        coverage=dict(source_part_ids=sorted(parts),covered_part_ids=selected,uncovered_part_ids=sorted(set(parts)-set(selected)),complete=set(selected)==set(parts)),
        source_sha256={**proposal['source_sha256'],CONTRACT:digest(ROOT/CONTRACT),
            'engineering/pilot_delivery/review.py':digest(__file__)},
        scope='Controlled research-document and quantified business-conversion review only; no manufacturing, engineering or operating acceptance',
        cost_scope='Existing source direct part/process account is retained once; this is not an additive project cost ledger',**extra,**FLAGS))
    contract.validate_pack(result)
    return result


def source_context(proposal, *, city, project, company, assembly_groups=None):
    """Trusted administrator provisioning input; not a client-selected candidate."""
    validate_proposal(proposal)
    extra={}
    if assembly_groups is not None:
        nodes=source_assemblies(proposal,assembly_groups)
        extra=dict(source_assemblies=nodes,assembly_patterns=contract.assembly_patterns(nodes))
    result=contract.seal(dict(schema='osr-wheel-delivery-project/1',environment='simulation',city=city,
        project=project,company=company,identities=deepcopy(proposal['identities']),proposal_id=proposal['proposal_id'],
        proposal_sha256=identity(proposal),source_parts={p['id']:identity(p) for p in proposal['items']},
        project_trainsets=proposal['summary']['project_trainsets'],
        source_patterns={p['id']:dict(part_id=p['part_id'],count_per_train=p['count_per_train'],
            assembly_occurrence_id=p['assembly_occurrence_id']) for p in proposal['occurrence_patterns']},**extra,**FLAGS))
    contract.validate_context(result);return result


def verify_artifacts(pack, root):
    contract.validate_pack(pack)
    for row in pack['artifacts']:
        path=ordinary(root,row['path'])
        if path.stat().st_size!=row['bytes'] or digest(path)!=row['sha256']:raise ValueError('Review artifact changed: '+row['path'])
    for component in pack['components']:
        for entry in component['documents'].values():
            definition=json.loads(ordinary(root,entry['path']).read_bytes())
            if definition!=entry['definition']:raise ValueError('Controlled sidecar definition differs')
            for row in definition['payloads']:_payload(root,row,definition)
    return True


def export_review_pack(pack, artifact_root, output):
    verify_artifacts(pack,artifact_root);out=Path(output)
    out.mkdir(parents=True,exist_ok=False)
    (out/'review-pack.json').write_bytes(encoded(pack))
    for row in pack['artifacts']:
        target=out/row['path'];target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ordinary(artifact_root,row['path']),target)
    verify_artifacts(pack,out)
    return dict(pack_sha256=pack['sha256'],components=len(pack['components']),
        complete_document_coverage=pack['coverage']['complete'],output=str(out),**FLAGS)


def main():
    import argparse
    from .export import load
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--proposal',required=True);p.add_argument('--documents',required=True)
    p.add_argument('--conversions',required=True);p.add_argument('--artifact-root',required=True)
    p.add_argument('--city',required=True);p.add_argument('--output',required=True)
    a=p.parse_args()
    value=compile_review_pack(load(a.proposal),load(a.documents),load(a.conversions),artifact_root=a.artifact_root,city=a.city)
    print(json.dumps(export_review_pack(value,a.artifact_root,a.output),sort_keys=True))


if __name__=='__main__':main()
