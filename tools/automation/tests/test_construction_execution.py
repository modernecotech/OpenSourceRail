"""Execution gates reject stale authority, overlapping crews and lifecycle gaps."""
from copy import deepcopy
from pathlib import Path
import sys
import pytest

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'deployment/erpnext/apps/osr_erpnext'))
from osr_erpnext.construction_execution import check_packet


def fixture():
    allocation=dict(task='task',department='Civil',unit='line',front='front',crew='crew',shift=1,equipment='launcher',
        workers=['employee'],required_roles=['operator'],start_at='2027-01-05T08:00:00+03:00',finish_at='2027-01-05T16:00:00+03:00')
    life=dict(commissioned=True,commissioning_record='bench',inspection_record='bench',configuration_accepted=True,
        released_project='project',released_front='front',transfer_required=False,
        inspection_valid_until='2028-01-01T00:00:00+03:00',maintenance_due_at='2028-01-01T00:00:00+03:00')
    worker=dict(id='employee',role='operator',crew='crew',shift=1,equipment='launcher',
        commissioning_supervised=True,equipment_assessment_passed=True,competency_expires='2028-01-01',
        assessment_record='test-assessment',assessor='test-assessor',authority_record='auth',revoked=False)
    packet=dict(schema='osr-construction-allocation/1',project='project',project_revision='revision',allocation=allocation,
        workers=[worker],asset_lifecycle=life,handover_record='test-handover',relief_coverage_record='test-relief',
        calendar=dict(weekdays=list(range(7)),holidays=[],maximum_shift_hours=8,minimum_rest_hours=12,
            day_start_hour=6,day_finish_hour=22,timezone='Asia/Baghdad'))
    employee=dict(status='Active',company='company',department='Civil',shift_covers_allocation=True,
        authorisations=[dict(record_id='auth',accepted=True,revoked=False,equipment='launcher',role='operator',
            assessment_record='test-assessment',assessor='test-assessor',valid_from='2027-01-01T00:00:00+03:00',expires_at='2028-01-01T00:00:00+03:00')])
    return packet,dict(name='project',company='company',revision='revision'),dict(name='task',**{k:allocation[k] for k in ('department','unit','front','crew','shift','equipment','workers')}),dict(name='launcher',company='company',docstatus=1,status='Submitted',controlled_lifecycle=deepcopy(life)),{'employee':employee},[]


def test_reviewed_native_allocation_can_pass_without_claiming_railway_release():
    values=fixture()
    assert check_packet(*values)==values[0]['allocation']


@pytest.mark.parametrize('failure',['revoked','leave','shift','maintenance','revision','relief','holiday','night'])
def test_current_record_and_calendar_failures_block_execution(failure):
    p,project,task,asset,employees,others=fixture()
    if failure=='revoked':employees['employee']['authorisations'][0]['revoked']=True
    elif failure=='leave':employees['employee']['on_leave']=True
    elif failure=='shift':employees['employee']['shift_covers_allocation']=False
    elif failure=='maintenance':asset['open_repairs']=['repair']
    elif failure=='revision':project['revision']='other-revision'
    elif failure=='relief':p['relief_coverage_record']=None
    elif failure=='holiday':p['calendar']['holidays']=['2027-01-05']
    elif failure=='night':p['calendar']['day_finish_hour']=15
    with pytest.raises(ValueError):check_packet(p,project,task,asset,employees,others)


def test_completed_shift_still_requires_rest_before_the_next_assignment():
    values=list(fixture());previous=deepcopy(values[0]['allocation'])
    previous.update(task='previous-task',equipment='other-launcher',start_at='2027-01-05T01:00:00+03:00',finish_at='2027-01-05T05:00:00+03:00')
    values[-1]=[previous]
    with pytest.raises(ValueError,match='rest'):check_packet(*values)
    previous['finish_at']='2027-01-04T19:00:00+03:00'
    assert check_packet(*values)


def test_hooks_cover_native_tasks_assignments_and_controlled_resource_changes():
    import runpy
    hooks=runpy.run_path(str(ROOT/'deployment/erpnext/apps/osr_erpnext/osr_erpnext/hooks.py'))['doc_events']
    assert hooks['Task']['validate'].endswith('validate_task')
    assert hooks['ToDo']['validate'].endswith('validate_assignment')
    assert 'OSR Construction Release' in hooks
    assert hooks['Employee']['validate'].endswith('validate_controlled_evidence')


def test_native_work_transition_rejects_a_draft_or_cancelled_review(monkeypatch):
    from types import SimpleNamespace
    from osr_erpnext.construction_execution import validate_task
    class Doc(dict):
        def __getattr__(self,name):return self.get(name)
        def get_doc_before_save(self):return None
    doc=Doc(name='task',status='Working',project='project',custom_osr_construction_equipment='launcher',custom_osr_construction_release='release')
    release=SimpleNamespace(docstatus=0,accepted=1,task='task',project='project',check_permission=lambda action:None)
    def throw(message):raise ValueError(message)
    monkeypatch.setitem(sys.modules,'frappe',SimpleNamespace(get_doc=lambda *args:release,throw=throw))
    with pytest.raises(ValueError,match='revoked'):validate_task(doc)
    release.docstatus=2
    with pytest.raises(ValueError,match='revoked'):validate_task(doc)


def test_asset_transfer_requires_matching_destination_and_recommissioning():
    values=list(fixture());values[0]['asset_lifecycle']['transfer_required']=True
    values[3]['controlled_lifecycle']=deepcopy(values[0]['asset_lifecycle'])
    with pytest.raises(ValueError,match='transfer'):check_packet(*values)
    for key in ('transfer_record','compatibility_record','recommissioning_record'):
        values[0]['asset_lifecycle'][key]='test-only'
    values[3]['controlled_lifecycle']=deepcopy(values[0]['asset_lifecycle'])
    assert check_packet(*values)
    values[0]['asset_lifecycle']['released_front']='another-front'
    values[3]['controlled_lifecycle']=deepcopy(values[0]['asset_lifecycle'])
    with pytest.raises(ValueError,match='project/front'):check_packet(*values)


def test_active_task_cannot_hide_its_allocation_by_reopening(monkeypatch):
    from types import SimpleNamespace
    from osr_erpnext.construction_execution import validate_task
    class Doc(dict):
        def __getattr__(self,name):return self.get(name)
        def get_doc_before_save(self):return Doc(status='Working',custom_osr_construction_equipment='launcher')
    def throw(message):raise ValueError(message)
    monkeypatch.setitem(sys.modules,'frappe',SimpleNamespace(throw=throw))
    with pytest.raises(ValueError,match='status reset'):
        validate_task(Doc(status='Open',custom_osr_construction_equipment='launcher'))


def test_future_reviewed_task_cannot_skip_resource_validation(monkeypatch):
    from types import SimpleNamespace
    from osr_erpnext.construction_execution import validate_task
    class Doc(dict):
        def __getattr__(self,name):return self.get(name)
        def get_doc_before_save(self):return None
    release=SimpleNamespace(docstatus=0,accepted=1,task='future-task',project='project',check_permission=lambda action:None)
    def throw(message):raise ValueError(message)
    monkeypatch.setitem(sys.modules,'frappe',SimpleNamespace(get_doc=lambda *args:release,throw=throw))
    with pytest.raises(ValueError,match='revoked'):
        validate_task(Doc(name='future-task',status='Open',project='project',
            custom_osr_construction_equipment='launcher',custom_osr_construction_release='review'))


def test_future_reviewed_allocation_blocks_asset_and_worker_double_booking():
    values=list(fixture());other=deepcopy(values[0]['allocation']);other['task']='future-open-task'
    values[-1]=[other]
    with pytest.raises(ValueError,match='asset is allocated'):check_packet(*values)
    other['equipment']='another-launcher'
    with pytest.raises(ValueError,match='worker assignments overlap'):check_packet(*values)
    other.update(start_at='2027-01-06T08:00:00+03:00',finish_at='2027-01-06T16:00:00+03:00')
    assert check_packet(*values)


@pytest.mark.parametrize('peer_status',['Open','Overdue','Completed','Completed-without-review'])
def test_native_future_booking_checks_reviewed_peers_and_retains_completed_history(monkeypatch,peer_status):
    """Exercise the native query and lock path, rather than just packet maths."""
    import hashlib
    import json
    from types import SimpleNamespace
    import osr_erpnext.construction_execution as execution
    class Doc(dict):
        def __getattr__(self,name):return self.get(name)
        def check_permission(self,action):pass
        def get_doc_before_save(self):return None
    packet,project,task,asset,employees,_=fixture()
    packet['workers'][0]['shift_type']='day'
    packet['calendar']['holiday_list']='holidays'
    peer_packet=deepcopy(packet);peer_packet['allocation']['task']='peer'
    packets={'review':packet,'peer-review':peer_packet}
    raw={name:json.dumps(value,sort_keys=True).encode() for name,value in packets.items()}
    documents={
        ('OSR Construction Release',name):Doc(docstatus=1,accepted=1,task=value['allocation']['task'],
            project='project',evidence_sha256=hashlib.sha256(raw[name]).hexdigest(),name=name)
        for name,value in packets.items()}
    documents.update({('Project','project'):Doc(**project,custom_osr_package_sha256='revision'),
        ('Asset','launcher'):Doc(**asset),('Employee','employee'):Doc(name='employee',**employees['employee']),
        ('Shift Type','day'):Doc(start_time='08:00:00',end_time='16:00:00',holiday_list='holidays'),
        ('Holiday List','holidays'):Doc(name='holidays',holidays=[]),
        ('Company','company'):Doc(default_holiday_list='holidays')})
    live_employee={**employees['employee'],
        'custom_osr_construction_authorisations':json.dumps(employees['employee']['authorisations']),
        'holiday_list':'holidays'}
    live_asset={**asset,'custom_osr_fleet_lifecycle':json.dumps(asset['controlled_lifecycle'])}
    def query(kind,**kwargs):
        if kind=='Task':
            assert 'Open' in kwargs['or_filters'][0][2] and 'Overdue' in kwargs['or_filters'][0][2]
            return [Doc(name='peer',status='Completed' if peer_status.startswith('Completed') else peer_status,
                custom_osr_construction_release=None if peer_status=='Completed-without-review' else 'peer-review')]
        return ['assignment'] if kind=='Shift Assignment' else []
    def sql(statement,parameters,**kwargs):
        return [live_asset if 'tabAsset' in statement else live_employee]
    def throw(message):raise ValueError(message)
    monkeypatch.setitem(sys.modules,'frappe',SimpleNamespace(get_doc=lambda *key:documents[key],
        get_all=query,db=SimpleNamespace(sql=sql),throw=throw))
    monkeypatch.setattr(execution,'_attachment',lambda release:(packets[release.name],raw[release.name]))
    monkeypatch.setattr(execution,'_resolve_evidence',lambda *args:None)
    allocation=packet['allocation']
    doc=Doc(name='task',status='Open',project='project',custom_osr_construction_release='review',
        custom_osr_construction_qualified_workers=json.dumps(allocation['workers']),
        **{'custom_osr_construction_'+key:allocation[key] for key in ('department','unit','front','crew','shift','equipment')})
    message='retained allocation review' if peer_status=='Completed-without-review' else 'asset is allocated'
    with pytest.raises(ValueError,match=message):execution.validate_task(doc)
