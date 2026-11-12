"""Native adapter logic against an in-memory Frappe double, not native evidence."""
from copy import deepcopy
import gzip
import importlib
import importlib.util
import json
from pathlib import Path
import sys
import types
import pytest

from engineering.pilot_delivery import review


class Denied(Exception):pass


class Doc:
    def __init__(self, backend, values):
        self._backend=backend;self.__dict__.update(deepcopy(values))
        self.docstatus=values.get('docstatus',0)
    def get(self,key,default=None):return self.__dict__.get(key,default)
    def check_permission(self,kind):
        if self._backend.session.user=='Guest':raise Denied('Guest')
        if self.doctype=='Project' and self.name not in self._backend.allowed_projects.get(self._backend.session.user,[]):raise Denied('Project')
    def get_content(self):return self.content
    def insert(self):
        b=self._backend;b.has_permission(self.doctype,'create',throw=True)
        if self.doctype=='BOM':
            for row in self.items:
                if row.get('bom_no') and b.get_doc('BOM',row['bom_no']).docstatus!=1:
                    raise ValueError('ERPNext requires submitted child BOM')
                row['rate']=b.get_doc('Item',row['item_code']).get('valuation_rate',0)
        name=self.get('name') or self.get('item_code') or self.get('workstation_name') or self.get('routing_name') or self.doctype+'-'+str(len(b.documents)+1)
        self.name=name;self.owner=b.session.user;self.modified_by=b.session.user;self.modified='time-'+str(len(b.documents)+1)
        if (self.doctype,name) in b.documents:raise ValueError('duplicate native record')
        b.documents[self.doctype,name]=self;return self


class Backend(types.ModuleType):
    def __init__(self,root):
        super().__init__('frappe');self.root=root;self.documents={};self.session=types.SimpleNamespace(user='Administrator')
        self.roles={'Administrator':['Manufacturing Manager','Projects Manager','Asset Manager'],'engineer':['Manufacturing Manager','Asset Manager'],
            'reviewer':['Projects Manager'],'reader':['Projects User'],'outsider':['Manufacturing Manager']}
        self.allowed_projects={name:['P'] for name in self.roles};self.allowed_projects['outsider']=['P']
        self.conf={'osr_integration_users':{name:dict(cities=['other' if name=='outsider' else 'baghdad'],environments=['simulation'],projects=['P']) for name in self.roles}}
        self.PermissionError=Denied;self.db=types.SimpleNamespace(exists=lambda dt,name:(dt,name) in self.documents,sql=lambda *args:[])
        self.whitelist=lambda **kwargs:lambda fn:fn
        self.parse_json=lambda value:json.loads(value) if isinstance(value,str) else value
        self.get_roles=lambda:self.roles.get(self.session.user,[])
        self.get_site_path=lambda *parts:str(self.root.joinpath(*parts))
        self.get_meta=lambda dt:types.SimpleNamespace(has_field=lambda key:True)
    def throw(self,message,exception=ValueError):raise exception(message)
    def has_permission(self,doctype,permission,throw=False):
        allowed=permission=='read' or self.session.user=='Administrator' or ('Manufacturing Manager' in self.get_roles() and doctype!='Task') or ('Projects Manager' in self.get_roles() and doctype=='Task')
        if not allowed and throw:raise Denied(doctype+'/'+permission)
        return allowed
    def get_doc(self,doctype,name=None):
        if isinstance(doctype,dict):return Doc(self,doctype)
        return self.documents[doctype,name]
    def add(self,doctype,name,**values):
        doc=Doc(self,dict(doctype=doctype,name=name,owner='Administrator',modified_by='Administrator',modified='initial',**values));self.documents[doctype,name]=doc;return doc
    def get_all(self,doctype,filters,pluck,order_by,limit_page_length):
        assert order_by=='creation desc, name desc'
        docs=[d for (dt,_),d in self.documents.items() if dt==doctype and all(d.get(k)==v for k,v in filters.items())]
        docs.sort(key=lambda d:(d.get('creation',''),d.name),reverse=True)
        return [d.get(pluck) for d in docs[:limit_page_length]]


@pytest.fixture()
def native(tmp_path,monkeypatch):
    backend=Backend(tmp_path/'site');monkeypatch.setitem(sys.modules,'frappe',backend)
    monkeypatch.syspath_prepend(str(review.ROOT/'deployment/erpnext/apps/osr_erpnext'))
    name='osr_erpnext.candidate_delivery';monkeypatch.delitem(sys.modules,name,raising=False)
    module=importlib.import_module(name)
    backend.add('Company','C',default_currency='USD')
    backend.add('Project','P',company='C',custom_osr_city='baghdad')
    backend.add('Item Group','Products',is_group=0)
    spec=importlib.util.spec_from_file_location('review_fixture_helpers',Path(__file__).with_name('test_pilot_delivery_review.py'))
    helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
    proposal=helper.synthetic_proposal()
    artifacts=tmp_path/'artifacts';artifacts.mkdir();pack=helper.pack(artifacts,proposal)
    context=review.source_context(proposal,city='baghdad',project='P',company='C')
    module.provision_project('P',context)
    files={}
    for i,row in enumerate(pack['artifacts']):
        name='File-'+str(i);backend.add('File',name,attached_to_doctype='Project',attached_to_name='P',is_private=1,content=(artifacts/row['path']).read_bytes());files[row['path']]=name
    backend.session.user='engineer';module.register_pack('P',pack,files)
    yield backend,module,pack,context,files
    monkeypatch.delitem(sys.modules,name,raising=False)


def approved(native):
    backend,module,pack,context,files=native
    backend.session.user='engineer';preview=module.preview('P',pack['sha256'],'Products')
    backend.session.user='reviewer';approved=module.review('P',pack['sha256'],'Products',preview['fingerprint'])
    return preview,approved


def test_authenticated_independent_review_creates_source_priced_drafts_and_idempotent_readback(native):
    b,m,p,context,_=native;preview,r=approved(native);b.session.user='engineer'
    out=m.apply('P',p['sha256'],r['review_id']);again=m.apply('P',p['sha256'],r['review_id'])
    assert out['created'] and not again['created'] and out['applied']==again['applied']
    assert all(x is False for k,x in out['applied'].items() if k in review.FLAGS)
    component=out['applied']['components'][0];bom=b.get_doc('BOM',component['bom'])
    assert bom.docstatus==0 and bom.items[0]['rate']==p['components'][0]['stock_lines'][0]['rate']
    assert component['source_direct_usd_per_unit']!=1 and component['quantity_per_train']==p['components'][0]['source_part']['quantity_per_train']
    assert len(bom.operations)>0 and m.status('P',p['sha256'])['state']=='reviewed-native-business-mapping'
    provenance=json.loads(b.get_doc('Item',component['finished_item']).description)
    assert provenance['maturity']=='controlled-research-draft' and provenance['research_holds']
    assert all(provenance[k] is False for k in review.FLAGS)


@pytest.mark.parametrize('actor',['Guest','reader','outsider'])
def test_roles_and_project_city_scope_are_native_not_client_strings(native,actor):
    b,m,p,_,_=native;b.session.user=actor
    with pytest.raises((Denied,ValueError)):m.preview('P',p['sha256'],'Products')


def test_proposer_cannot_self_review_and_unreviewed_apply_creates_nothing(native):
    b,m,p,_,_=native;b.roles['engineer'].append('Projects Manager');before=len(b.documents)
    preview=m.preview('P',p['sha256'],'Products')
    with pytest.raises(Denied):m.review('P',p['sha256'],'Products',preview['fingerprint'])
    with pytest.raises(FileNotFoundError):m.apply('P',p['sha256'],'0'*64)
    assert len(b.documents)==before


@pytest.mark.parametrize('fault',['drawing-content','drawing-revision','native-collision','review-task'])
def test_artifact_and_native_revision_changes_invalidate_conversion_review(native,fault):
    b,m,p,_,files=native;preview,r=approved(native)
    if fault=='drawing-content':b.get_doc('File',next(iter(files.values()))).content=b'changed'
    elif fault=='drawing-revision':b.get_doc('File',next(iter(files.values()))).modified='later'
    elif fault=='native-collision':
        item=preview['specifications']['items'][0];b.add('Item',item['item_code'],stock_uom='Nos')
    else:b.get_doc('Task',r['task']).description='rewritten review'
    b.session.user='engineer';before=len(b.documents)
    with pytest.raises(ValueError):m.apply('P',p['sha256'],r['review_id'])
    assert len(b.documents)==before


def test_reviewed_item_quantity_or_route_mutation_cannot_be_reused(native):
    b,m,p,_,_=native;_,r=approved(native);b.session.user='engineer'
    out=m.apply('P',p['sha256'],r['review_id']);bom=b.get_doc('BOM',out['applied']['components'][0]['bom']);bom.items[0]['qty']=2
    with pytest.raises(ValueError,match='fields changed'):m.apply('P',p['sha256'],r['review_id'])


def test_native_default_cannot_silently_replace_reviewed_rate(native,monkeypatch):
    b,m,p,_,_=native;_,r=approved(native);b.session.user='engineer';original=Doc.insert
    def altered(doc):
        if doc.doctype=='BOM':b.get_doc('Item',doc.items[0]['item_code']).valuation_rate=1.
        return original(doc)
    monkeypatch.setattr(Doc,'insert',altered)
    with pytest.raises(ValueError,match='Native defaults changed'):m.apply('P',p['sha256'],r['review_id'])


def test_project_binding_cannot_be_replaced_by_another_candidate(native):
    b,m,p,context,_=native;b.session.user='Administrator';changed=deepcopy(context)
    changed['identities']=dict(changed['identities'],candidate_id='0'*64);changed=review.contract.seal({k:v for k,v in changed.items() if k!='sha256'})
    with pytest.raises(ValueError,match='immutable'):m.provision_project('P',changed)


def test_gateway_request_builder_never_forwards_actor_or_controller_fields(monkeypatch):
    monkeypatch.syspath_prepend(str(review.ROOT/'services/integration'))
    from osr_integration.pilot_delivery import request
    value=dict(project='P',pack_sha256='a'*64,item_group='Products')
    assert request('preview',value)['method']=='osr_erpnext.candidate_delivery.preview'
    for extra in ('actor','role','movement_authority','commands','reviewer'):
        with pytest.raises(ValueError):request('preview',dict(value,**{extra:'forged'}))
    with pytest.raises(ValueError):request('movement_authority',value)


def test_gateway_outbox_preserves_legacy_bytes_and_only_carries_explicit_serial(monkeypatch):
    monkeypatch.syspath_prepend(str(review.ROOT/'services/integration'))
    from osr_integration.store import Store
    class Capture:
        def execute(self,query,args):self.args=args
    db=Capture();store=object.__new__(Store)
    asset=dict(city='baghdad',environment='simulation',company_id='C',erp_project='P',asset_id='A',erp_asset_id='ASSET',engineering_revision='a'*64)
    rule=dict(id='R',response='simulation')
    store._enqueue(db,asset,rule,'I',1,'active',123.);legacy=db.args
    store._enqueue(db,dict(asset,physical_serial_id=''),rule,'I',1,'active',123.)
    assert db.args==legacy and 'physical_serial_id' not in json.loads(legacy[2])
    store._enqueue(db,dict(asset,physical_serial_id='SERIAL-1'),rule,'I',1,'active',123.)
    assert json.loads(db.args[2])==dict(json.loads(legacy[2]),physical_serial_id='SERIAL-1')


def installed(native):
    b,m,p,context,_=native;_,r=approved(native);b.session.user='engineer'
    applied=m.apply('P',p['sha256'],r['review_id'])['applied'];component=applied['components'][0]
    b.get_doc('BOM',component['bom']).docstatus=1
    source=next(row for row in p['components'] if row['source_part']['id']==component['part_id'])['source_part']
    pattern=source['serial_plan']['occurrence_pattern_ids'][0]
    position=review.contract.digest(dict(context_sha256=context['sha256'],source_pattern_id=pattern,ordinal=0,train_index=0))
    b.add('Asset','ASSET',company='C',docstatus=1,custom_osr_asset_id='SIM-WD-'+position[:24])
    def manufacture(serial):
        b.add('Serial No',serial,company='C',item_code=component['finished_item'])
        b.add('Work Order','WO-'+serial,company='C',project='P',docstatus=1,production_item=component['finished_item'],bom_no=component['bom'],produced_qty=1)
        for direction,kind in [('Inward','MADE'),('Outward','INSTALL')]:
            bundle='B-'+kind+'-'+serial
            b.add('Serial and Batch Bundle',bundle,company='C',item_code=component['finished_item'],is_cancelled=False,
                type_of_transaction=direction,entries=[types.SimpleNamespace(serial_no=serial)])
            b.add('Stock Entry',kind+'-'+serial,company='C',docstatus=1,work_order='WO-'+serial,
                stock_entry_type='Manufacture' if kind=='MADE' else 'Material Issue',
                items=[types.SimpleNamespace(name='row-'+serial,item_code=component['finished_item'],project='P',qty=1,serial_and_batch_bundle=bundle)])
    manufacture('OLD')
    args=dict(project='P',pack_sha256=p['sha256'],part_id=component['part_id'],asset='ASSET',source_pattern_id=pattern,
        ordinal=0,train_index=0,work_order='WO-OLD',manufacture_stock='MADE-OLD',installation_stock='INSTALL-OLD')
    result=m.register_installation(**args)
    return b,m,p,context,component,args,result,manufacture


def test_counted_occurrence_and_actual_serial_custody_are_required(native):
    b,m,p,context,component,args,result,manufacture=installed(native)
    assert result['created'] and not m.register_installation(**args)['created']
    assert not result['installation']['installation_accepted']
    for key,value in [('source_pattern_id','invented-position'),('train_index',context['project_trainsets']),('ordinal',True)]:
        with pytest.raises(ValueError):m.register_installation(**dict(args,**{key:value}))
    manufacture('NEW')
    replacement=dict(args,work_order='WO-NEW',manufacture_stock='MADE-NEW',installation_stock='INSTALL-NEW')
    with pytest.raises(ValueError,match='removal'):m.register_installation(**replacement)


def test_wrong_revision_or_serial_is_refused_before_generic_issue_creation(native,monkeypatch):
    b,m,p,context,component,args,result,manufacture=installed(native)
    event=dict(project='P',company='C',city='baghdad',environment='simulation',erp_asset_id='ASSET',
        asset_id=b.get_doc('Asset','ASSET').custom_osr_asset_id,engineering_revision=context['identities']['engineering_revision'],
        physical_serial_id='OLD',event_id='E',incident_id='I',rule='R',condition='active',occurrence=1)
    assert m.guard_condition_event(event)
    monkeypatch.delitem(sys.modules,'osr_erpnext.integration',raising=False)
    integration=importlib.import_module('osr_erpnext.integration')
    b.new_doc=lambda dt:(_ for _ in ()).throw(AssertionError('Issue creation reached before source guard'))
    b.add('Project','OTHER',company='C',custom_osr_city='baghdad')
    for key,value in [('engineering_revision','0'*64),('physical_serial_id','NEW'),('asset_id','other-position'),('environment','physical'),('project','OTHER')]:
        before=len(b.documents)
        with pytest.raises((ValueError,Denied)):integration.condition_event(dict(event,**{key:value}))
        assert len(b.documents)==before
    b.get_doc('Stock Entry','INSTALL-OLD').docstatus=2
    with pytest.raises(ValueError,match='Submitted'):integration.condition_event(event)


def test_later_failed_pending_or_cancelled_qa_invalidates_business_handback(native):
    b,m,p,context,component,args,first,manufacture=installed(native)
    b.add('Issue','ISSUE',project='P',custom_osr_erp_asset='ASSET',custom_osr_environment='simulation')
    b.add('Asset Repair','REPAIR',company='C',project='P',asset='ASSET',docstatus=1,
        custom_osr_issue='ISSUE',custom_osr_environment='simulation',repair_status='Completed',custom_osr_handback_required=1)
    b.add('Serial and Batch Bundle','RETURN-B',company='C',item_code=component['finished_item'],is_cancelled=False,
        type_of_transaction='Inward',entries=[types.SimpleNamespace(serial_no='OLD')])
    b.add('Stock Entry','RETURN',company='C',docstatus=1,stock_entry_type='Material Receipt',
        items=[types.SimpleNamespace(name='old-return',item_code=component['finished_item'],project='P',qty=1,serial_and_batch_bundle='RETURN-B')])
    manufacture('NEW')
    replacement=dict(args,work_order='WO-NEW',manufacture_stock='MADE-NEW',installation_stock='INSTALL-NEW',repair='REPAIR',removal_stock='RETURN')
    current=m.register_installation(**replacement)['installation']
    assert current['previous_installation_sha256']==first['installation']['sha256']
    assert not m.register_installation(**replacement)['created']
    def qa(name,status,docstatus,creation):
        return b.add('Quality Inspection',name,company='C',reference_type='Stock Entry',reference_name='MADE-NEW',
            item_code=component['finished_item'],child_row_reference='row-NEW',status=status,docstatus=docstatus,
            creation=creation,inspected_by='inspector')
    qa('PASS-1','Accepted',1,'001');qa('FAIL-2','Rejected',1,'002');b.session.user='reviewer'
    before=len(b.documents)
    with pytest.raises(ValueError):m.review_handback('P',p['sha256'],'ASSET')
    assert len(b.documents)==before
    qa('PASS-3','Accepted',1,'003')
    result=m.review_handback('P',p['sha256'],'ASSET')
    assert result['created'] and not m.review_handback('P',p['sha256'],'ASSET')['created']
    assert result['handback']['native_readback']['installed_serial']=='NEW'
    assert m.lifecycle_status('P',p['sha256'],'ASSET')['state']=='simulation-business-reviewed'
    # Exercise the receipt verifier with the in-memory double. This fabricated
    # unit-test receipt is never exported as evidence of native execution.
    monkey_path=str(review.ROOT/'tools/automation/native-v06')
    if monkey_path not in sys.path:sys.path.insert(0,monkey_path)
    import candidate_contracts as contract
    part=p['components'][0]
    value=dict(schema='osr-v06-platform-fixture/2',environment='simulation',city='baghdad',identities=p['identities'],
        review_pack=p,source_context=context,component_id=component['part_id'],source_occurrence=part['source_part'],
        source_occurrence_sha256=part['source_part_sha256'],artifact_inventory=p['artifacts'],proposal_file_sha256='a'*64,**review.FLAGS)
    value['input_id']=contract.digest(value)
    records=[]
    for (dt,name),doc in b.documents.items():
        fields={k:doc.get(k) for k in ('status','repair_status','produced_qty','production_item','bom_no','custom_osr_handback_required','inspected_by') if doc.get(k) is not None}
        if dt=='BOM':fields['items']=deepcopy(doc.items)
        records.append(dict(doctype=dt,name=name,docstatus=doc.docstatus,owner=doc.owner,modified_by=doc.modified_by,values=fields))
    records += [dict(doctype=dt,name='SIM-'+dt,docstatus=1,values={}) for dt in ('Purchase Order','Purchase Receipt','Training Program')]
    receipt=dict(schema='osr-v06-native-platform-result/2',execution='executed',input_id=value['input_id'],identities=p['identities'],
        source_sha256={},checks={k:True for k in sorted(contract.REQUIRED)},uncovered=[],cleanup={'verified':True},
        document_coverage=p['coverage'],candidate_mapping=m.status('P',p['sha256']),candidate_lifecycle=m.lifecycle_status('P',p['sha256'],'ASSET'),
        native_records=records,business_review=result['handback'],**review.FLAGS)
    assert contract.verify_result(receipt,value,{})==receipt
    changed=deepcopy(receipt);next(r for r in changed['native_records'] if r['doctype']=='BOM')['values']['items'][0]['rate']=1.
    with pytest.raises(ValueError,match='BOM price'):contract.verify_result(changed,value,{})
    qa('PENDING-4','Rejected',0,'004')
    assert m.lifecycle_status('P',p['sha256'],'ASSET')['state']=='business-handback-held'
    with pytest.raises(ValueError):m.review_handback('P',p['sha256'],'ASSET')
