"""Exercise native intake orchestration and independent live-state revalidation."""
import copy
import importlib.util
import json
import sys
import types
from pathlib import Path

import pytest

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'deployment/erpnext/apps/osr_erpnext'))
from osr_erpnext.field_contract import digest


class Doc(types.SimpleNamespace):
    def get(self,key,default=None):return getattr(self,key,default)
    def check_permission(self,permission):self.permissions.append(permission)
    def add_comment(self,*args):self.comments.append(args)
    def load_doc_before_save(self, **kwargs):self.before_save_loaded=True
    def is_new(self):return self.new
    def insert(self,*args,**kwargs):
        self.inserted=True
        if self.doctype=='OSR Field Execution':self.name='EXEC-1'
        return self


@pytest.fixture
def native(monkeypatch):
    project=Doc(name='PROJ',company='COMP')
    task=Doc(name='TASK',project='PROJ',status='Working',modified='2026-10-12 06:00:00',
        custom_osr_asset_id='A:charger',custom_osr_revision='v1',custom_osr_construction_work_method_revision='METHOD',permissions=[],comments=[])
    asset=Doc(name='ASSET',company='COMP',custom_osr_asset_id='A:charger',docstatus=1,status='Submitted',permissions=[])
    employee=Doc(name='EMP',company='COMP',status='Active',user_id='tech@example.invalid',permissions=[])
    records={('Task','TASK'):task,('Asset','ASSET'):asset,('Employee','EMP'):employee}
    created=[];state={'assigned':True,'prior':None,'gate_revoked':False,'gate_calls':0}
    def get_doc(kind,name=None):
        if isinstance(kind,dict):
            d=Doc(**kind,name='new',permissions=[],new=True);created.append(d);return d
        if kind=='OSR Field Execution':return Doc(name=name,permissions=[])
        return records[(kind,name)]
    def throw(message,*args):raise ValueError(message)
    frappe=types.ModuleType('frappe');frappe.get_doc=get_doc;frappe.throw=throw
    frappe.parse_json=lambda value:json.loads(value)if isinstance(value,str)else value
    frappe.whitelist=lambda **kwargs:lambda f:f
    frappe.flags=types.SimpleNamespace();frappe.PermissionError=PermissionError
    frappe.conf={'osr_field_technicians':{'tech':{'employee':'EMP','user':'tech@example.invalid'}}}
    frappe.db=types.SimpleNamespace(sql=lambda *args:[],get_value=lambda *args,**kwargs:state['prior'],exists=lambda *args,**kwargs:state['assigned'])
    integration=types.ModuleType('osr_erpnext.integration');integration._scope=lambda *args:project
    execution=types.ModuleType('osr_erpnext.construction_execution')
    def gate(doc):
        assert doc.before_save_loaded is True
        state['gate_calls']+=1
        if state['gate_revoked']:raise ValueError('Native allocation revoked')
    execution.validate_task=gate
    monkeypatch.setitem(sys.modules,'frappe',frappe)
    monkeypatch.setitem(sys.modules,'osr_erpnext.integration',integration)
    monkeypatch.setitem(sys.modules,'osr_erpnext.construction_execution',execution)
    spec=importlib.util.spec_from_file_location('field_native_under_test',ROOT/'deployment/erpnext/apps/osr_erpnext/osr_erpnext/field_operations.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    work=dict(id='W1',city='samawah',environment='simulation',asset_id='A:charger',assigned_to='tech',method_revision='METHOD',erp_task='TASK',erp_asset='ASSET',
        native_modified=str(task.modified),engineering_revision='v1',expires_at='2099-01-01T00:00:00Z',physical_serial='',requires_photo=False,readings=[],operational_release=False)
    work['sha256']=digest(work)
    event=dict(id='E1',device_id='D1',work_id='W1',status='performed-awaiting-inspection',readings={},photos=[],notes='')
    packet=dict(schema='osr-field-completion/1',city='samawah',environment='simulation',work=work,event=event,actor='tech',company='COMP',project='PROJ',operational_release=False)
    packet['idempotency_sha256']=digest(dict(event=event,actor='tech',scope='samawah|simulation'))
    return module,packet,state,task,asset,employee,created,frappe


def test_native_intake_uses_permissions_revalidates_allocation_and_preserves_work_state(native):
    module,packet,state,task,asset,employee,created,frappe=native
    result=module.ingest(packet)
    assert result['execution']=='EXEC-1' and not result['operational_release']
    assert state['gate_calls']==1 and task.status=='Working' and task.comments
    assert task.permissions==['write'] and asset.permissions==employee.permissions==['read']
    assert created[0].status=='performed-awaiting-inspection' and not frappe.flags.osr_field_intake


@pytest.mark.parametrize('mutation', ['task-revision','method','engineering','assignment','employee','asset','revocation'])
def test_native_intake_rejects_stale_or_revoked_records(native,mutation):
    module,packet,state,task,asset,employee,created,_=native
    if mutation=='task-revision':task.modified='changed'
    elif mutation=='method':task.custom_osr_construction_work_method_revision='changed'
    elif mutation=='engineering':task.custom_osr_revision='changed'
    elif mutation=='assignment':state['assigned']=False
    elif mutation=='employee':employee.status='Left'
    elif mutation=='asset':asset.custom_osr_asset_id='other'
    else:state['gate_revoked']=True
    with pytest.raises(ValueError):module.ingest(packet)
    assert not created


def test_native_lost_reply_is_idempotent_and_generic_writes_are_blocked(native):
    module,packet,state,_,_,_,created,frappe=native
    state['prior']=types.SimpleNamespace(name='EXEC-1',event_sha256=packet['idempotency_sha256'])
    assert module.ingest(packet)['duplicate'] and not created
    with pytest.raises(ValueError):module.validate_receipt(Doc(new=True))
    frappe.flags.osr_field_intake=True
    with pytest.raises(ValueError):module.validate_receipt(Doc(new=False))
