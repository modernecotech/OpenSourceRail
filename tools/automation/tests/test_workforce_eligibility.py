"""Attendance, identity, expired evidence and administrative tasks cannot release work."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import sys
from types import SimpleNamespace
import pytest

ROOT=Path(__file__).resolve().parents[3]
APP=ROOT/'deployment/erpnext/apps/osr_erpnext'
sys.path.insert(0,str(APP))
from osr_erpnext.workforce_rules import assignment_eligibility
from osr_erpnext.workforce import preview_assignment
NOW='2026-10-04T08:00:00+00:00'

@pytest.fixture
def packet():
    task=dict(task_kind='battery-inspection',asset_family='metro-6car',location='line-1',method_revision='A',maximum_skill_idle_days=90,independent_verification_required=True)
    auth=dict(**{k:task[k] for k in ['task_kind','asset_family','location','method_revision']},assessment_record='practical-assessment-fixture',assessor='assessor-fixture',authority_record='authority-fixture',issued_by='authority-fixture',accepted=True,suspended=False,valid_from='2026-10-01T00:00:00+00:00',expires_at='2026-10-04T09:00:00+00:00',last_practical_use='2026-10-03T08:00:00+00:00')
    worker=dict(worker_id='synthetic-worker',native_employee='EMP-FIXTURE',evidence_revision='fixture-only',available=True,suspended=False,rest_checked=True,rest_compliant=True,location='line-1',authorisations=[auth])
    resources={key:dict(record_id=key+'-fixture',accepted=True,valid_from='2026-10-04T07:00:00+00:00',expires_at='2026-10-04T12:00:00+00:00') for key in ['access','permit','tools','materials','supervisor','verifier']}
    resources['verifier']['worker_id']='independent-synthetic-verifier'
    return dict(worker=worker,task=task,resources=resources)

def evaluate(packet,now=NOW):return assignment_eligibility(packet['worker'],packet['task'],packet['resources'],now)

def test_eligible_synthetic_packet_grants_no_assignment_or_railway_authority(packet):
    result=evaluate(packet)
    assert result['eligible'] and not result['creates_assignment'] and not result['operational_release']
    spec=importlib.util.spec_from_file_location('shared',ROOT/'engineering/analysis/workforce_checks.py');shared=importlib.util.module_from_spec(spec);spec.loader.exec_module(shared)
    assert shared.assignment_eligibility(packet['worker'],packet['task'],packet['resources'],NOW)==result

@pytest.mark.parametrize('key,value',[('available',False),('suspended',True),('rest_checked',False),('rest_compliant',False),('native_employee',None),('location','line-2'),('available','true')])
def test_worker_unavailability_rest_identity_and_location_block(packet,key,value):
    packet['worker'][key]=value;assert not evaluate(packet)['eligible']

@pytest.mark.parametrize('key,value',[('assessment_record',None),('authority_record',None),('accepted',False),('accepted','true'),('suspended',True),('asset_family','light-metro-3car'),('method_revision','obsolete'),('last_practical_use','2026-01-01T00:00:00+00:00'),('last_practical_use','2026-10-05T00:00:00+00:00'),('expires_at','invalid')])
def test_attendance_does_not_replace_current_scoped_authorisation(packet,key,value):
    packet['worker']['authorisations'][0][key]=value;packet['worker']['attendance']=True
    assert not evaluate(packet)['eligible']

def test_task_start_recheck_blocks_later_expiry_and_independent_self_verification(packet):
    assert evaluate(packet)['eligible']
    assert not evaluate(packet,'2026-10-04T09:00:00+00:00')['eligible']
    packet['resources']['verifier']['worker_id']=packet['worker']['worker_id']
    assert not evaluate(packet)['eligible']

@pytest.mark.parametrize('resource',['access','permit','tools','materials','supervisor','verifier'])
def test_missing_or_expired_work_resources_block(packet,resource):
    packet['resources'][resource]['expires_at']='2026-10-04T08:00:00+00:00'
    assert not evaluate(packet)['eligible']

def test_missing_timestamp_zone_is_rejected(packet):
    with pytest.raises(ValueError):evaluate(packet,'2026-10-04T08:00:00')

@pytest.mark.parametrize('limit',[None,0,-1,float('inf'),float('nan'),True])
def test_missing_or_invalid_idle_policy_blocks(packet,limit):
    packet['task']['maximum_skill_idle_days']=limit
    assert not evaluate(packet)['eligible']

def test_verification_policy_must_be_explicit(packet):
    packet['task'].pop('independent_verification_required')
    assert not evaluate(packet)['eligible']

@pytest.fixture
def native(monkeypatch,packet):
    calls=[]
    def check(self,permission):
        calls.append((self.name,permission))
        if getattr(self,'deny',False):raise PermissionError('denied')
    def doc(**kw):
        value=SimpleNamespace(**kw);value.check_permission=lambda permission:check(value,permission);return value
    packet.update(project_revision='baseline-fixture',task_reference='TASK-FIXTURE')
    docs={('Project','P'):doc(name='P',company='C',custom_osr_package_sha256='baseline-fixture'),
        ('Task','T'):doc(name='TASK-FIXTURE',project='P',status='Open'),
        ('Employee','E'):doc(name='EMP-FIXTURE',company='C',status='Active'),
        ('File','F'):doc(name='F',is_private=True,attached_to_doctype='Employee',attached_to_name='EMP-FIXTURE',get_content=lambda:json.dumps(packet))}
    def throw(message):raise ValueError(message)
    monkeypatch.setitem(sys.modules,'frappe',SimpleNamespace(get_roles=lambda:['HR Manager'],get_doc=lambda kind,name:docs[(kind,name)],throw=throw))
    return docs,calls,packet

def test_native_observer_reads_permissions_but_never_assigns(native):
    docs,calls,packet=native;result=preview_assignment('P','T','E','F',NOW)
    assert result['eligible'] and result['read_only'] and not result['actual_assignment_created']
    assert calls==[('P','read'),('TASK-FIXTURE','read'),('EMP-FIXTURE','read'),('F','read')]

@pytest.mark.parametrize('kind,field,value',[('Task','project','other'),('Task','status','Completed'),('Employee','company','other'),('Employee','status','Left'),('File','is_private',False),('File','attached_to_name','other')])
def test_native_project_company_active_state_and_private_file_boundary(native,kind,field,value):
    docs,_,_=native;key={'Task':'T','Employee':'E','File':'F'}[kind];setattr(docs[(kind,key)],field,value)
    with pytest.raises(ValueError):preview_assignment('P','T','E','F',NOW)

def test_native_permissions_and_stale_baseline_packet_fail(native):
    docs,calls,packet=native;docs[('File','F')].deny=True
    with pytest.raises(PermissionError):preview_assignment('P','T','E','F',NOW)
    docs[('File','F')].deny=False;packet['project_revision']='obsolete'
    with pytest.raises(ValueError):preview_assignment('P','T','E','F',NOW)

def test_native_role_required(native):
    sys.modules['frappe'].get_roles=lambda:['Guest']
    with pytest.raises(ValueError):preview_assignment('P','T','E','F',NOW)

def test_native_readiness_distinguishes_schema_and_permissions(native):
    from osr_erpnext.workforce import administration_readiness
    f=sys.modules['frappe']
    f.db=SimpleNamespace(exists=lambda kind,name:name!='Training Result')
    f.has_permission=lambda name,permission:name!='File'
    result=administration_readiness()
    rows={r['doctype']:r for r in result['record_types']}
    assert rows['Employee']['caller_can_read']
    assert not rows['File']['caller_can_read']
    assert not rows['Training Result']['schema_exists']
    assert not result['appointments_verified'] and not result['operational_release']
