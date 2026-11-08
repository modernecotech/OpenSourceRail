"""Controlled business review contracts; synthetic documents are not CAD evidence."""
from copy import deepcopy
import gzip
import json
from pathlib import Path
import pytest

from engineering.pilot_delivery import review
from engineering.station_rail.common import identity, encoded

c=review.contract


@pytest.fixture(scope='module')
def proposal():
    return json.loads(gzip.decompress((review.ROOT/'docs/design-engine/reconciled-pilot-bogie-detail/delivery/proposal.json.gz').read_bytes()))


def documents(tmp_path, proposal):
    part=proposal['items'][0];binding=proposal['identities'];refs={'part_id':part['id']}
    chars=[dict(id='stock-length',name='Declared stock length',unit='m',minimum=.259,maximum=.261,
        method='Synthetic dimensional-reading test; no real physical observation',evidence_maturity='calculated-research-limit')]
    ops=[dict(sequence=1,operation='Inspect counted stock',workstation='Research inspection bench',
        tools=['Dimensional gauge'],setup_minutes=2.,run_minutes_per_unit=3.,time_basis='Explicit synthetic planning test',inspection_ids=['stock-length'])]
    for kind in sorted(c.DOCUMENT_TYPES):
        suffix='.svg' if kind=='drawing' else '.json';name=kind+suffix;path=tmp_path/name
        if kind=='drawing':path.write_text('<svg xmlns="http://www.w3.org/2000/svg"><rect width="260" height="240"/></svg>')
        else:path.write_bytes(encoded(dict(schema='osr-controlled-research-'+('inspection' if kind=='inspection' else 'route')+'/1',
            identities=binding,part_id=part['id'],**({'characteristics':chars} if kind=='inspection' else {'operations':ops}))))
        doc=dict(schema='osr-controlled-research-document/1',document_type=kind,identities=binding,
            part_id=part['id'],component_definition_id=part['component_definition_id'],source_part_sha256=identity(part),
            revision='TEST-1',maturity='controlled-research-draft',research_holds=['Synthetic unit fixture, no manufacturing or physical release'],
            payloads=[dict(path=name,sha256=review.digest(path),bytes=path.stat().st_size,
                media_type='image/svg+xml' if kind=='drawing' else 'application/json')],**c.FLAGS)
        if kind=='inspection':doc['characteristics']=chars
        if kind=='routing':doc['operations']=ops
        sidecar=kind+'-metadata.json';(tmp_path/sidecar).write_bytes(encoded(doc));refs[kind]=sidecar
    index=dict(schema='osr-controlled-research-documents/1',identities=binding,components=[refs])
    conversion={part['id']:dict(valuation_mode='source-priced-workpiece',source_part_sha256=identity(part),stock_inputs=[],direct_process_allowance_usd=None)}
    return index,conversion


def pack(tmp_path,proposal):
    docs,conversions=documents(tmp_path,proposal)
    return review.compile_review_pack(proposal,docs,conversions,artifact_root=tmp_path,city='baghdad')


def test_real_source_part_cost_quantity_and_partial_coverage_retained(tmp_path,proposal):
    p=pack(tmp_path,proposal);part=proposal['items'][0]
    assert c.validate_pack(p)==p and review.verify_artifacts(p,tmp_path)
    assert p['coverage']['complete'] is False and len(p['coverage']['uncovered_part_ids'])==len(proposal['items'])-1
    row=p['components'][0];stock=row['stock_lines'][0]
    assert row['source_part']==part and row['source_part_sha256']==identity(part)
    assert stock['engineering_unit_rate_usd']==part['counted_direct_parts_process_usd_per_train']['base']/part['quantity_per_train']
    assert stock['quantity']==1 and stock['uom']=='Nos' and stock['rate']!=1
    assert all(p[k] is False for k in c.FLAGS)


@pytest.mark.parametrize('fault',['drawing-byte','missing-document','wrong-candidate','wrong-part','empty-drawing','routing-inspection','source-price-zero','duplicate-component','source-part-hash'])
def test_compiler_rejects_mixed_or_placeholder_evidence(tmp_path,proposal,fault):
    docs,conversion=documents(tmp_path,proposal)
    kind='routing' if fault=='routing-inspection' else 'drawing';path=tmp_path/docs['components'][0][kind]
    definition=json.loads(path.read_bytes())
    if fault=='drawing-byte':(tmp_path/'drawing.svg').write_text('changed')
    elif fault=='missing-document':docs['components'][0].pop('inspection')
    elif fault=='wrong-candidate':definition['identities']=dict(definition['identities'],candidate_id='0'*64)
    elif fault=='wrong-part':definition['component_definition_id']='0'*64
    elif fault=='empty-drawing':
        payload=tmp_path/'drawing.svg';payload.write_text('<svg xmlns="http://www.w3.org/2000/svg"/>')
        definition['payloads'][0].update(sha256=review.digest(payload),bytes=payload.stat().st_size)
    elif fault=='routing-inspection':definition['operations'][0]['inspection_ids']=['unknown']
    elif fault=='source-price-zero':
        altered=deepcopy(proposal['items'][0]);altered['counted_direct_parts_process_usd_per_train']['base']=0
        with pytest.raises(ValueError):c.stock_lines(next(iter(conversion.values())),altered)
        return
    elif fault=='duplicate-component':docs['components'].append(deepcopy(docs['components'][0]))
    else:next(iter(conversion.values()))['source_part_sha256']='0'*64
    path.write_bytes(encoded(definition))
    with pytest.raises((ValueError,KeyError)):
        review.compile_review_pack(proposal,docs,conversion,artifact_root=tmp_path,city='baghdad')


def test_authoritative_project_binding_and_coverage_cannot_be_resealed(tmp_path,proposal):
    p=pack(tmp_path,proposal);context=review.source_context(proposal,city='baghdad',project='P',company='C')
    assert c.bind_pack(p,context)
    forged=deepcopy(p);forged['coverage']['source_part_ids']=forged['coverage']['covered_part_ids'];forged['coverage']['uncovered_part_ids']=[];forged['coverage']['complete']=True
    forged=c.seal({k:v for k,v in forged.items() if k!='sha256'})
    with pytest.raises(ValueError,match='source coverage'):c.bind_pack(forged,context)
    forged=deepcopy(p);forged['identities']=dict(forged['identities'],candidate_id='0'*64)
    forged=c.seal({k:v for k,v in forged.items() if k!='sha256'})
    with pytest.raises(ValueError):c.bind_pack(forged,context)


def test_review_export_copies_actual_artifacts_and_refuses_overwrite(tmp_path,proposal):
    p=pack(tmp_path,proposal);out=tmp_path/'export'
    result=review.export_review_pack(p,tmp_path,out)
    assert not result['complete_document_coverage'] and review.verify_artifacts(p,out)
    with pytest.raises(FileExistsError):review.export_review_pack(p,tmp_path,out)
    (out/'drawing.svg').write_text('tampered')
    with pytest.raises(ValueError):review.verify_artifacts(p,out)


def test_quantity_yield_and_cost_decomposition_require_explicit_balance(proposal):
    source=proposal['items'][0];rate=source['counted_direct_parts_process_usd_per_train']['base']/source['quantity_per_train']
    mapping=dict(valuation_mode='quantified-source-stock',source_part_sha256=identity(source),
        stock_inputs=[dict(id='stock',uom='Kg',net_quantity=9.,gross_quantity=10.,waste_fraction=.1,
            unit_rate_usd=rate/20.,source_sha256='a'*64,basis='Synthetic test price, no supplier observation')],direct_process_allowance_usd=rate/2.)
    assert c.stock_lines(mapping,source)[0]['quantity']==10
    mapping['stock_inputs'][0]['net_quantity']=10
    with pytest.raises(ValueError,match='yield'):c.stock_lines(mapping,source)


def test_unsafe_or_symlink_artifacts_refused(tmp_path,proposal):
    docs,conversion=documents(tmp_path,proposal);path=tmp_path/'drawing.svg';outside=tmp_path/'outside.svg'
    path.rename(outside);path.symlink_to(outside)
    with pytest.raises(ValueError,match='Ordinary'):review.compile_review_pack(proposal,docs,conversion,artifact_root=tmp_path,city='baghdad')
    with pytest.raises(ValueError):c.safe_path('../escape')


def test_business_handback_uses_latest_native_state_and_independent_authenticated_actor(proposal):
    context=review.source_context(proposal,city='baghdad',project='P',company='C')
    observed=dict(project='P',company='C',identities=proposal['identities'],reviewer='reviewer',inspector='inspector',proposer='engineer',
        latest_qa_docstatus=1,latest_qa_status='Accepted',repair_docstatus=1,repair_status='Completed',installation_docstatus=1,
        installed_serial='NEW',manufactured_serial='NEW',physical_handback_required=True,latest_qa='QI',installation_record='SE',repair='AR',review_task='T')
    assert c.business_handback(context,observed,actor='reviewer')['business_state']=='simulation-business-reviewed'
    for key,value in [('latest_qa_status','Rejected'),('latest_qa_docstatus',0),('installed_serial','OLD'),('physical_handback_required',False),('reviewer','inspector')]:
        altered=deepcopy(observed);altered[key]=value
        with pytest.raises(ValueError):c.business_handback(context,altered,actor=altered['reviewer'])
    with pytest.raises(ValueError):c.business_handback(context,observed,actor='forged-client-role')
