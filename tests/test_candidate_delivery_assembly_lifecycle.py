"""Synthetic one-child assembly API tests; no ERP/native/door qualification."""
from copy import deepcopy
from hashlib import sha256
import importlib,importlib.util,json,sys
from pathlib import Path
from types import SimpleNamespace as Row
import pytest
from engineering.pilot_delivery import review
from engineering.station_rail.common import identity,encoded
c=review.contract


def helper(name):
    spec=importlib.util.spec_from_file_location('fixture_'+name,Path(__file__).with_name(name+'.py'))
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m


def inputs(folder):
    h=helper('test_pilot_delivery_review');proposal=h.synthetic_proposal()
    part=proposal['items'][0];old=part['assembly_id'];part['assembly_id']='synthetic/source-one-piece-assembly'
    for route in proposal['assembly_routes']:
        if route['id']==old:
            route['component_type_ids'].remove(part['id'])
            for op in route['operations']:op['part_ids']=[p for p in op['part_ids'] if p!=part['id']]
    proposal['assembly_routes'].append(dict(id=part['assembly_id'],identities=proposal['identities'],
        occurrences_per_train=part['quantity_per_train'],assembly_occurrence_ids=['TEST-'+str(i) for i in range(part['quantity_per_train'])],
        component_type_ids=[part['id']],operations=[]))
    proposal['proposal_id']=identity({k:v for k,v in proposal.items() if k!='proposal_id'})
    groups=[dict(id='synthetic/research-kit',assembly_ids=[part['assembly_id']])]
    docs,conversion=h.documents(folder,proposal)
    node=review.source_assemblies(proposal,groups)[part['assembly_id']]
    mapping={'assembly_id':node['id']};(folder/'assembly').mkdir()
    for kind in sorted(c.DOCUMENT_TYPES):
        definition=json.loads((folder/docs['components'][0][kind]).read_text())
        definition.update(schema='osr-controlled-research-assembly-document/1',assembly_id=node['id'],
            assembly_definition_id=node['definition_id'],source_assembly_sha256=identity(node))
        for key in ('part_id','component_definition_id','source_part_sha256'):definition.pop(key)
        payload=deepcopy(definition['payloads'][0]);oldpayload=folder/payload['path'];payload['path']='assembly/'+payload['path']
        if kind=='drawing':raw=oldpayload.read_bytes()
        else:
            value=json.loads(oldpayload.read_text());value['assembly_id']=node['id'];value.pop('part_id');raw=encoded(value)
        (folder/payload['path']).write_bytes(raw);payload.update(bytes=len(raw),sha256=sha256(raw).hexdigest());definition['payloads']=[payload]
        name='assembly/'+kind+'-metadata.json';(folder/name).write_bytes(encoded(definition));mapping[kind]=name
    docs['assemblies']=[mapping]
    pack=review.compile_review_pack(proposal,docs,conversion,artifact_root=folder,city='baghdad',assembly_groups=groups)
    context=review.source_context(proposal,city='baghdad',project='P',company='C',assembly_groups=groups,assembly_documents=pack['assembly_documents'])
    return pack,context,node


@pytest.fixture
def native(tmp_path,monkeypatch):
    h=helper('test_candidate_delivery_adapter');b=h.Backend(tmp_path/'site');monkeypatch.setitem(sys.modules,'frappe',b)
    monkeypatch.syspath_prepend(str(review.ROOT/'deployment/erpnext/apps/osr_erpnext'))
    name='osr_erpnext.candidate_delivery';monkeypatch.delitem(sys.modules,name,raising=False);m=importlib.import_module(name)
    b.add('Company','C',default_currency='USD');b.add('Project','P',company='C',custom_osr_city='baghdad');b.add('Item Group','Products',is_group=0)
    folder=tmp_path/'artifacts';folder.mkdir();pack,context,node=inputs(folder)
    m.provision_project('P',context);files={}
    for i,r in enumerate(pack['artifacts']):
        name='File-'+str(i);b.add('File',name,attached_to_doctype='Project',attached_to_name='P',is_private=1,content=(folder/r['path']).read_bytes());files[r['path']]=name
    b.session.user='engineer';m.register_pack('P',pack,files);preview=m.preview('P',pack['sha256'],'Products')
    b.session.user='reviewer';r=m.review('P',pack['sha256'],'Products',preview['fingerprint']);b.session.user='engineer'
    applied=m.apply('P',pack['sha256'],r['review_id'])['applied'];part=applied['components'][0]
    assembly=next(a for a in applied['assemblies'] if a['assembly_id']==node['id'])
    for x in (part,assembly):b.get_doc('BOM',x['bom']).docstatus=1
    def bundle(name,item,serial,direction,stock,line):
        b.add('Serial and Batch Bundle',name,company='C',docstatus=1,item_code=item,is_cancelled=False,type_of_transaction=direction,entries=[Row(serial_no=serial,qty=-1 if direction=='Outward' else 1)],voucher_type='Stock Entry',voucher_no=stock,voucher_detail_no=line)
    def make(serial):
        child='CHILD-'+serial
        for sn,source in [(child,part),(serial,assembly)]:
            item=source['finished_item'];b.add('Serial No',sn,company='C',item_code=item)
            b.add('Work Order','WO-'+sn,company='C',project='P',docstatus=1,production_item=item,bom_no=source['bom'],produced_qty=1)
            for direct,kind in [('Inward','MADE'),('Outward','INSTALL')]:
                bn='B-'+kind+'-'+sn;bundle(bn,item,sn,direct,kind+'-'+sn,'row-'+sn)
                rows=[Row(name='row-'+sn,item_code=item,project='P',qty=1,serial_and_batch_bundle=bn,is_finished_item=True)]
                if sn==serial and kind=='MADE':
                    cb='CONSUME-'+sn;bundle(cb,part['finished_item'],child,'Outward','MADE-'+sn,'child-'+sn)
                    rows.append(Row(name='child-'+sn,item_code=part['finished_item'],project='P',qty=1,serial_and_batch_bundle=cb,is_finished_item=False))
                b.add('Stock Entry',kind+'-'+sn,company='C',docstatus=1,work_order='WO-'+sn,stock_entry_type='Manufacture' if kind=='MADE' else 'Material Issue',items=rows)
            b.add('Quality Inspection','QA-'+sn,company='C',reference_type='Stock Entry',reference_name='MADE-'+sn,item_code=item,
                child_row_reference='row-'+sn,status='Accepted',docstatus=1,creation='001',inspected_by='inspector')
        return [dict(kind='part',id=part['part_id'],units=[dict(serial=child,work_order='WO-'+child,manufacture_stock='MADE-'+child,children=[])])]
    pattern=next(k for k,v in context['assembly_patterns'].items() if v['assembly_id']==node['id'])
    position=c.digest(dict(context_sha256=context['sha256'],source_kind='assembly',source_id=node['id'],definition_id=node['definition_id'],source_pattern_id=pattern,ordinal=0,train_index=0))
    b.add('Asset','ASSET',company='C',docstatus=1,custom_osr_asset_id='SIM-WD-'+position[:24])
    args=dict(project='P',pack_sha256=pack['sha256'],assembly_id=node['id'],asset='ASSET',source_pattern_id=pattern,ordinal=0,train_index=0,
        work_order='WO-OLD',manufacture_stock='MADE-OLD',installation_stock='INSTALL-OLD',child_provenance=make('OLD'))
    yield b,m,pack,context,part,assembly,args,make
    monkeypatch.delitem(sys.modules,name,raising=False)


def return_stock(b,name,item,serial):
    bundle='B-'+name
    b.add('Serial and Batch Bundle',bundle,company='C',item_code=item,is_cancelled=False,type_of_transaction='Inward',entries=[Row(serial_no=serial)],voucher_type='Stock Entry',voucher_no=name,voucher_detail_no='returned')
    b.add('Stock Entry',name,company='C',docstatus=1,stock_entry_type='Material Receipt',items=[Row(name='returned',item_code=item,project='P',qty=1,serial_and_batch_bundle=bundle)])


def test_typed_assembly_manufacture_install_replace_handback(native):
    b,m,p,context,part,assembly,args,make=native
    first=m.register_assembly_installation(**args)['installation']
    assert first['assembly_id']==args['assembly_id'] and 'part_id' not in first
    assert first['identities']==context['identities'] and not first['installation_accepted']
    assert not m.register_assembly_installation(**args)['created']
    b.add('Issue','ISSUE',project='P',custom_osr_erp_asset='ASSET',custom_osr_environment='simulation')
    b.add('Asset Repair','REPAIR',company='C',project='P',asset='ASSET',docstatus=1,custom_osr_issue='ISSUE',custom_osr_environment='simulation',repair_status='Completed',custom_osr_handback_required=1)
    return_stock(b,'RETURN',assembly['finished_item'],'OLD')
    replacement=dict(args,work_order='WO-NEW',manufacture_stock='MADE-NEW',installation_stock='INSTALL-NEW',child_provenance=make('NEW'),repair='REPAIR',removal_stock='RETURN')
    current=m.register_assembly_installation(**replacement)['installation'];assert current['previous_installation_sha256']==first['sha256']
    event=dict(project='P',company='C',city='baghdad',environment='simulation',erp_asset_id='ASSET',asset_id=b.get_doc('Asset','ASSET').custom_osr_asset_id,
        engineering_revision=context['identities']['engineering_revision'],physical_serial_id='NEW')
    assert m.guard_condition_event(event)
    for key,value in [('engineering_revision','0'*64),('physical_serial_id','OLD')]:
        with pytest.raises(ValueError):m.guard_condition_event(dict(event,**{key:value}))
    b.session.user='reviewer';out=m.review_handback('P',p['sha256'],'ASSET')
    assert not out['handback']['physical_accepted']
    assert m.lifecycle_status('P',p['sha256'],'ASSET')['state']=='simulation-business-reviewed'
    old=b.get_doc('Quality Inspection','QA-CHILD-NEW')
    b.add('Quality Inspection','QA-CHILD-NEW-2',company='C',reference_type='Stock Entry',reference_name='MADE-CHILD-NEW',item_code=part['finished_item'],
        child_row_reference='row-CHILD-NEW',status='Accepted',docstatus=1,creation='002',inspected_by='inspector')
    b.session.user='engineer'
    assert not m.register_assembly_installation(**replacement)['created']
    b.session.user='reviewer'
    assert m.lifecycle_status('P',p['sha256'],'ASSET')['state']=='business-handback-held'
    out=m.review_handback('P',p['sha256'],'ASSET')
    assert m.lifecycle_status('P',p['sha256'],'ASSET')['state']=='simulation-business-reviewed'
    qa=b.get_doc('Quality Inspection','QA-NEW');qa.docstatus=0
    assert m.lifecycle_status('P',p['sha256'],'ASSET')['state']=='business-handback-held'
    with pytest.raises(ValueError):m.review_handback('P',p['sha256'],'ASSET')
    qa.docstatus=1
    task=b.get_doc('Task',out['handback']['native_readback']['review_task']);task.description+='tampered'
    with pytest.raises(ValueError,match='Task changed'):m.lifecycle_status('P',p['sha256'],'ASSET')
    b.get_doc('Quality Inspection','QA-CHILD-NEW-2').status='Rejected'
    with pytest.raises(ValueError,match='child native QA'):m.guard_condition_event(event)
    with pytest.raises(ValueError,match='child native QA'):m.lifecycle_status('P',p['sha256'],'ASSET')


@pytest.mark.parametrize('fault',[None,'pending-receipt','wrong-receipt-row','wrong-batch','pending-qa','rejected-qa','wrong-origin','duplicate-serial'])
def test_purchased_child_receipt_and_lot_custody(native,fault):
    b,m,p,context,part,assembly,args,make=native
    original=m._pack
    def purchased_pack(*a,**kw):
        d,ctx,folder,reg=original(*a,**kw)
        reg=deepcopy(reg);reg['pack']['components'][0]['source_part']['make_buy']='buy-qualified'
        return d,ctx,folder,reg
    m._pack=purchased_pack
    serial='BOUGHT-OLD';batch='LOT-OLD';item=part['finished_item']
    b.add('Serial No',serial,company='C',item_code=item)
    b.add('Batch',batch,company='C',item=item)
    outward=b.get_doc('Serial and Batch Bundle','CONSUME-OLD')
    outward.entries=[Row(serial_no=serial,batch_no=batch,qty=-1)]
    row=Row(name='RECEIPT-ROW',item_code=item,project='P',qty=1,serial_and_batch_bundle='RECEIPT-BUNDLE')
    receipt=b.add('Purchase Receipt','RECEIPT',company='C',docstatus=1,items=[row])
    incoming=b.add('Serial and Batch Bundle','RECEIPT-BUNDLE',company='C',docstatus=1,item_code=item,
        is_cancelled=False,type_of_transaction='Inward',voucher_type='Purchase Receipt',voucher_no='RECEIPT',
        voucher_detail_no=row.name,entries=[Row(serial_no=serial,batch_no=batch,qty=1)])
    qa=b.add('Quality Inspection','INCOMING-QA',company='C',inspection_type='Incoming',reference_type='Purchase Receipt',
        reference_name=receipt.name,item_code=item,child_row_reference=row.name,status='Accepted',docstatus=1,
        creation='001',inspected_by='inspector')
    args['child_provenance']=[dict(kind='part',id=part['part_id'],units=[dict(
        serial=serial,batch=batch,purchase_receipt=receipt.name,receipt_row=row.name,children=[])])]
    if fault=='pending-receipt':receipt.docstatus=0
    elif fault=='wrong-receipt-row':args['child_provenance'][0]['units'][0]['receipt_row']='OTHER'
    elif fault=='wrong-batch':incoming.entries[0].batch_no='OTHER'
    elif fault=='pending-qa':qa.docstatus=0
    elif fault=='rejected-qa':qa.status='Rejected'
    elif fault=='wrong-origin':incoming.voucher_type='Stock Entry'
    elif fault=='duplicate-serial':incoming.entries.append(Row(serial_no=serial,batch_no=batch,qty=1))
    if fault:
        with pytest.raises(ValueError):m.register_assembly_installation(**args)
    else:
        result=m.register_assembly_installation(**args)['installation']
        assert not result['installation_accepted']
        assert result['child_provenance'][0]['units'][0]['batch']==batch


@pytest.mark.parametrize('fault',['quantity','kind','serial','work-order','stock','child-qa','assembly-definition','unsubmitted-child','wrong-revision','purchased','lot-only','voucher'])
def test_assembly_refuses_wrong_native_custody_or_source(native,fault):
    b,m,p,context,part,assembly,args,make=native
    if fault=='quantity':args['child_provenance'][0]['units']=[]
    elif fault=='kind':args['child_provenance'][0]['kind']='assembly'
    elif fault=='serial':args['child_provenance'][0]['units'][0]['serial']='OTHER'
    elif fault=='work-order':b.get_doc('Work Order','WO-CHILD-OLD').production_item='OTHER'
    elif fault=='stock':b.get_doc('Stock Entry','MADE-OLD').items[1].qty=2
    elif fault=='child-qa':b.get_doc('Quality Inspection','QA-CHILD-OLD').docstatus=0
    elif fault=='unsubmitted-child':b.get_doc('BOM',part['bom']).docstatus=0
    elif fault=='wrong-revision':args['pack_sha256']='0'*64
    elif fault=='voucher':b.get_doc('Serial and Batch Bundle','CONSUME-OLD').voucher_no='OTHER-STOCK'
    elif fault=='lot-only':b.get_doc('Serial and Batch Bundle','B-MADE-CHILD-OLD').entries=[Row(serial_no=None,batch_no='LOT-ONLY')]
    elif fault=='assembly-definition':
        doc=b.get_doc('Item',assembly['finished_item']);doc.description+='changed'
    else:
        # Resolve guard in isolation: source hash/review/file binding refusals
        # would precede this explicit unsupported-domain branch in production.
        original=m._pack
        def pack(*a,**kw):
            d,ctx,folder,reg=original(*a,**kw);reg=deepcopy(reg);reg['pack']['components'][0]['source_part']['make_buy']='buy-standard';return d,ctx,folder,reg
        m._pack=pack
    before=len(b.documents)
    with pytest.raises((ValueError,FileNotFoundError)):m.register_assembly_installation(**args)
    assert len(b.documents)==before


def test_assembly_docs_must_be_independently_authoritative_and_real(tmp_path):
    p,context,node=inputs(tmp_path)
    assert review.verify_artifacts(p,tmp_path)
    forged=deepcopy(context);forged.pop('assembly_document_hashes');forged=c.seal({k:v for k,v in forged.items() if k!='sha256'})
    with pytest.raises(ValueError,match='authoritative'):c.bind_pack(p,forged)
    (tmp_path/'assembly/drawing.svg').write_text('tampered')
    with pytest.raises(ValueError,match='artifact changed'):review.verify_artifacts(p,tmp_path)


def test_part_assembly_collision_and_replacement_old_serial_refused(native):
    b,m,p,context,part,assembly,args,make=native
    wrong=dict(args);wrong['assembly_id']=part['part_id']
    with pytest.raises(ValueError,match='authoritative assembly'):m.register_assembly_installation(**wrong)
    flat={k:v for k,v in args.items() if k not in ('assembly_id','child_provenance')};flat['part_id']=args['assembly_id']
    with pytest.raises(ValueError,match='reviewed part'):m.register_installation(**flat)
    m.register_assembly_installation(**args)
    replacement=dict(args,work_order='WO-NEW',manufacture_stock='MADE-NEW',installation_stock='INSTALL-NEW',child_provenance=make('NEW'))
    with pytest.raises(ValueError,match='removal'):m.register_assembly_installation(**replacement)
    b.add('Asset Repair','R',company='C',project='P',asset='ASSET',docstatus=1,custom_osr_environment='simulation',repair_status='Completed',custom_osr_handback_required=1)
    return_stock(b,'WRONG-RETURN',assembly['finished_item'],'NEW')
    with pytest.raises(ValueError,match='previously installed serial'):
        m.register_assembly_installation(**dict(replacement,repair='R',removal_stock='WRONG-RETURN'))


def test_flat_native_fixture_does_not_qualify_new_assembly_api():
    sys.path.insert(0,str(review.ROOT/'tools/automation/native-v06'))
    import candidate_contracts
    with pytest.raises(ValueError,match='part only'):
        candidate_contracts.validate_input({'source_kind':'assembly'})


def test_child_serial_cannot_be_consumed_twice(native):
    b,m,p,context,part,assembly,args,make=native
    m.register_assembly_installation(**args)
    provenance=make('NEW')
    provenance[0]['units'][0]=deepcopy(args['child_provenance'][0]['units'][0])
    b.get_doc('Serial and Batch Bundle','CONSUME-NEW').entries=[Row(serial_no='CHILD-OLD',qty=-1)]
    b.add('Asset Repair','R',company='C',project='P',asset='ASSET',docstatus=1,custom_osr_environment='simulation',repair_status='Completed',custom_osr_handback_required=1)
    return_stock(b,'RETURN',assembly['finished_item'],'OLD')
    with pytest.raises(ValueError,match='already consumed'):
        m.register_assembly_installation(**dict(args,work_order='WO-NEW',manufacture_stock='MADE-NEW',installation_stock='INSTALL-NEW',child_provenance=provenance,repair='R',removal_stock='RETURN'))


@pytest.mark.parametrize('legacy',['part_id','component_definition_id','source_part_sha256'])
def test_assembly_document_cannot_hide_legacy_part_identity(legacy):
    with pytest.raises(ValueError,match='Mixed part and assembly'):
        c.validate_assembly_document(dict(schema='osr-controlled-research-assembly-document/1',**{legacy:'legacy'}),{}, {})
