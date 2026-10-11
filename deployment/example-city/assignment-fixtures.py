"""Native simulation-only allocation records for rolled-back assignment checks."""
import hashlib
from datetime import datetime,timedelta,timezone
from pathlib import Path


def maintenance_assignment_fixture(project,company,users,key,file_paths):
    import frappe,json
    def create(dt,**values):return frappe.get_doc(dict(doctype=dt,**values)).insert()
    def private_record(kind,name,value):
        raw=json.dumps(dict(value,fixture_key=key,physical_validation=False,evidence_basis='simulation-only native workflow test'),sort_keys=True).encode()
        doc=create('File',file_name='FLOWS-ALLOC-'+key+'-'+str(len(file_paths))+'.json',is_private=1,attached_to_doctype=kind,attached_to_name=name,content=raw)
        file_paths.append(doc.get_full_path())
        return dict(evidence_file=doc.name,evidence_sha256=hashlib.sha256(raw).hexdigest())
    today=datetime.now(timezone.utc).date();expiry=datetime.combine(today+timedelta(days=30),datetime.max.time(),tzinfo=timezone.utc)
    department=create('Department',department_name='FLOWS maintenance '+key,company=company)
    holiday=create('Holiday List',holiday_list_name='FLOWS allocation '+key,from_date=str(today),to_date=str(today+timedelta(days=30)))
    shift=create('Shift Type',name='FLOWS shift '+key,start_time='06:00:00',end_time='18:00:00',holiday_list=holiday.name)
    # The source asset stays in its native company; all temporary metadata rolls back.
    source=INPUT['source'];asset=frappe.get_doc('Asset',source['asset']);front='FLOWS front '+key;method='FLOWS-MAINT-'+key
    life=dict(commissioned=True,commissioning_record='simulation-only commission '+key,inspection_record='simulation-only inspection '+key,
        configuration_accepted=True,released_project=project,released_front=front,transfer_required=False,
        inspection_valid_until=expiry.isoformat(),maintenance_due_at=expiry.isoformat(),maintenance_isolation_accepted=True,
        maintenance_isolation_record='simulation-only isolation '+key,maintenance_isolation_valid_until=expiry.isoformat())
    life.update(private_record('Asset',asset.name,life));asset.custom_osr_fleet_lifecycle=json.dumps(life);asset.save()
    employees=[];workers=[]
    for i,user in enumerate(users):
        e=create('Employee',first_name='FLOWS allocation '+key+' '+str(i),user_id=user,gender=frappe.db.get_value('Gender',{},'name'),
            date_of_birth='1990-01-01',date_of_joining='2020-01-01',status='Active',company=company,department=department.name,holiday_list=holiday.name)
        assignment=create('Shift Assignment',employee=e.name,company=company,shift_type=shift.name,start_date=str(today),end_date=str(today+timedelta(days=30)),status='Active');assignment.submit()
        authority=dict(record_id='FLOWS authority '+key+' '+str(i),accepted=True,revoked=False,equipment=asset.name,role='maintainer',
            assessment_record='simulation-only assessment '+key+' '+str(i),assessor='simulation-only assessor',valid_from=datetime.combine(today,datetime.min.time(),tzinfo=timezone.utc).isoformat(),expires_at=expiry.isoformat(),task_kind='maintenance',method_revision=method)
        authority.update(private_record('Employee',e.name,authority));e.custom_osr_construction_authorisations=json.dumps([authority]);e.save();employees.append(e.name)
        workers.append(dict(id=e.name,role='maintainer',crew='FLOWS crew '+key,shift=1,equipment=asset.name,commissioning_supervised=True,
            equipment_assessment_passed=True,competency_expires=str(expiry.date()),assessment_record=authority['assessment_record'],assessor=authority['assessor'],authority_record=authority['record_id'],revoked=False,shift_type=shift.name))
    def attach(task,day):
        # Assignment permits remain administrative simulation records, never rail release.
        task.custom_osr_construction_work_method_revision=method;task.save()
        start=datetime.combine(today+timedelta(days=day),datetime.min.time(),tzinfo=timezone.utc)+timedelta(hours=8)
        allocation=dict(task=task.name,department=department.name,unit='FLOWS unit '+key,front=front,crew='FLOWS crew '+key,shift=1,equipment=asset.name,
            workers=employees,required_roles=['maintainer'],required_role_quantities={'maintainer':2},start_at=start.isoformat(),finish_at=(start+timedelta(hours=8)).isoformat())
        packet=dict(schema='osr-construction-allocation/1',task_kind='maintenance',method_revision=method,project=project,
            project_revision=frappe.db.get_value('Project',project,'custom_osr_package_sha256'),allocation=allocation,workers=workers,asset_lifecycle=life,
            handover_record='simulation-only handover '+key,relief_coverage_record='simulation-only relief '+key,
            calendar=dict(timezone='UTC',holiday_list=holiday.name,weekdays=list(range(7)),holidays=[],maximum_shift_hours=8,minimum_rest_hours=12,day_start_hour=6,day_finish_hour=22))
        evidence=private_record('Task',task.name,packet)
        review=create('OSR Construction Release',project=project,task=task.name,evidence_file=evidence['evidence_file'],accepted=1);review.submit();task.reload()
        return review
    return attach


def remove_fixture_files(file_paths):
    import frappe
    base=Path(frappe.get_site_path('private','files')).resolve()
    for name in file_paths:
        p=Path(name).resolve()
        if not p.is_relative_to(base) or not p.name.startswith('FLOWS-ALLOC-'):raise ValueError('fixture cleanup path outside owned private files')
        p.unlink(missing_ok=True)
