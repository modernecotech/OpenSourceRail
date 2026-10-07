"""Native Task/ToDo execution gates backed by submitted allocation evidence.

No draft, attachment or successful planning check grants an allocation. A
submitted review remains revocable; live employee, asset and competing task
records are resolved on transitions under database locks.
"""
from datetime import datetime, timedelta, timezone
import hashlib
import json
from zoneinfo import ZoneInfo
from .construction_fleet import validate_crew_task
from .workforce_rules import moment

RELEASE='OSR Construction Release'
ACTIVE={'Working','Pending Review','Completed'}
RESERVED={'Open','Overdue','Working','Pending Review'}


def check_packet(packet, project, task, asset, employees, other_tasks):
    if packet.get('schema')!='osr-construction-allocation/1':
        raise ValueError('unknown construction allocation evidence')
    allocation=packet['allocation'];start=moment(allocation['start_at']);end=moment(allocation['finish_at'])
    if end<=start or packet['project']!=project['name'] or allocation['task']!=task['name']:
        raise ValueError('allocation does not match project, task and time window')
    if not project.get('revision') or packet['project_revision']!=project['revision']:
        raise ValueError('allocation review belongs to another project revision')
    for field in ('department','unit','front','crew','shift','equipment'):
        if allocation[field]!=task[field]:
            raise ValueError('reviewed allocation differs from current '+field)
    if asset['name']!=allocation['equipment'] or asset['company']!=project['company'] or asset['docstatus']!=1 or asset['status'] in {None,'Work In Progress','Capitalized','Cancelled','Sold','Scrapped','Out of Order'}:
        raise ValueError('construction asset is unavailable or belongs to another company')
    lifecycle=packet['asset_lifecycle']
    if lifecycle!=asset.get('controlled_lifecycle'):
        raise ValueError('asset lifecycle review differs from current authoritative record')
    if lifecycle.get('released_project')!=project['name'] or lifecycle.get('released_front')!=allocation['front']:
        raise ValueError('asset lifecycle is not released for this project/front')
    if lifecycle.get('transfer_required') and not all(lifecycle.get(k) for k in ('transfer_record','compatibility_record','recommissioning_record')):
        raise ValueError('asset transfer, compatibility and recommissioning evidence required')
    if lifecycle.get('commissioned') is not True or not lifecycle.get('commissioning_record') or not lifecycle.get('inspection_record') or lifecycle.get('configuration_accepted') is not True:
        raise ValueError('asset commissioning, configuration and inspection evidence required')
    if moment(lifecycle['inspection_valid_until'])<end or moment(lifecycle['maintenance_due_at'])<end or asset.get('open_repairs'):
        raise ValueError('asset inspection/maintenance does not cover this allocation')
    workers=packet['workers'];ids=allocation['workers']
    if not ids or len(set(ids))!=len(ids) or set(ids)!=set(task['workers']):
        raise ValueError('reviewed, distinct qualified workers required')
    validate_crew_task({**allocation,'finish':end.date().isoformat()},workers)
    for worker in workers:
        if worker['id'] not in ids:
            continue
        employee=employees[worker['id']]
        if employee['status']!='Active' or employee['company']!=project['company'] or employee['department']!=allocation['department'] or employee.get('on_leave') or employee.get('holiday_closed') or employee.get('shift_covers_allocation') is not True:
            raise ValueError('employee is inactive or outside this department/company')
        if not worker.get('assessment_record') or not worker.get('assessor') or not worker.get('authority_record') or worker.get('revoked') is not False:
            raise ValueError('current assessed worker authority required')
        auth=next((r for r in employee.get('authorisations',[]) if r.get('record_id')==worker['authority_record']),{})
        if auth.get('accepted') is not True or auth.get('revoked') is not False or auth.get('equipment')!=allocation['equipment'] or auth.get('role')!=worker['role'] or auth.get('assessment_record')!=worker['assessment_record'] or not auth.get('assessor'):
            raise ValueError('worker authority is missing, revoked or outside this equipment/role')
        if not moment(auth['valid_from'])<=start<end<=moment(auth['expires_at']):
            raise ValueError('worker authorisation does not cover this shift')
    calendar=packet['calendar'];hours=(end-start).total_seconds()/3600
    start_local=start.astimezone(ZoneInfo(calendar['timezone']));end_local=end.astimezone(ZoneInfo(calendar['timezone']))
    if not 0<calendar['maximum_shift_hours']<=24 or not 0<=calendar['minimum_rest_hours']<=168 or hours>calendar['maximum_shift_hours']:
        raise ValueError('shift duration exceeds reviewed calendar')
    cursor=start_local
    while cursor<end_local:
        if cursor.weekday() not in calendar['weekdays'] or cursor.date().isoformat() in calendar['holidays']:
            raise ValueError('allocation falls on a closed calendar day')
        cursor+=timedelta(minutes=1)
    if (start_local.hour+start_local.minute/60<calendar['day_start_hour'] or end_local.hour+end_local.minute/60>calendar['day_finish_hour'] or start_local.date()!=end_local.date()) and not calendar.get('night_work_permission'):
        raise ValueError('reviewed night-work permission required')
    if not packet.get('handover_record') or not packet.get('relief_coverage_record'):
        raise ValueError('handover and relief coverage evidence required')
    rest=timedelta(hours=calendar['minimum_rest_hours'])
    for other in other_tasks:
        if other['task']==allocation['task']:
            continue
        a=moment(other['start_at']);b=moment(other['finish_at'])
        if other['equipment']==allocation['equipment'] and start<b and a<end:
            raise ValueError('asset is allocated to another task')
        if set(other['workers'])&set(ids) and start<b+rest and a<end+rest:
            raise ValueError('worker assignments overlap or breach reviewed rest')
    return allocation


def install():
    import frappe
    if frappe.db.exists('DocType',RELEASE):
        return
    fields=[dict(fieldname=n,label=label,fieldtype=kind,reqd=0 if extra.get('read_only') or kind=='Check' else 1,**extra) for n,label,kind,extra in (
        ('project','Project','Link',{'options':'Project'}),('task','Task','Link',{'options':'Task'}),
        ('evidence_file','Private allocation evidence','Link',{'options':'File'}),
        ('accepted','Review accepted','Check',{}),
        ('evidence_sha256','Evidence SHA-256','Data',{'read_only':1}),
        ('reviewed_by','Reviewing authority','Link',{'options':'User','read_only':1}))]
    frappe.get_doc(dict(doctype='DocType',name=RELEASE,module='OpenSourceRail',custom=1,is_submittable=1,
        autoname='hash',track_changes=1,fields=fields,
        permissions=[*[dict(role=r,read=1,write=1,create=1,submit=1,cancel=1) for r in ('HR Manager','Projects Manager')],dict(role='Projects User',read=1)])).insert()


def submit_review(doc,method=None):
    import frappe
    if not {'HR Manager','Projects Manager'}.issubset(set(frappe.get_roles())) or doc.accepted!=1:
        frappe.throw('Accepted construction review requires HR and project authority roles')
    packet,raw=_attachment(doc)
    if packet['project']!=doc.project or packet['allocation']['task']!=doc.task:
        frappe.throw('Evidence does not match review project/task')
    doc.evidence_sha256=hashlib.sha256(raw).hexdigest();doc.reviewed_by=frappe.session.user


def _attachment(release):
    import frappe
    attachment=frappe.get_doc('File',release.evidence_file);attachment.check_permission('read')
    if not attachment.is_private or attachment.attached_to_doctype!='Task' or attachment.attached_to_name!=release.task:
        frappe.throw('Use private evidence attached to the reviewed Task')
    raw=attachment.get_content()
    if isinstance(raw,str):raw=raw.encode()
    return json.loads(raw),raw


def validate_controlled_evidence(doc,method=None):
    import frappe
    field='custom_osr_construction_authorisations' if doc.doctype=='Employee' else 'custom_osr_fleet_lifecycle'
    role='HR Manager' if doc.doctype=='Employee' else 'Projects Manager'
    old=doc.get_doc_before_save()
    if doc.get(field)!=(old.get(field) if old else None) and role not in set(frappe.get_roles()):
        frappe.throw('Controlled construction evidence requires '+role)


def _resolve_evidence(record,kind,name):
    import frappe
    source=frappe.get_doc('File',record['evidence_file']);source.check_permission('read')
    if not source.is_private or source.attached_to_doctype!=kind or source.attached_to_name!=name:
        frappe.throw('Controlled evidence must be private and attached to its native resource')
    raw=source.get_content()
    if isinstance(raw,str):raw=raw.encode()
    if hashlib.sha256(raw).hexdigest()!=record['evidence_sha256']:
        frappe.throw('Authoritative construction resource evidence has changed')


def _guarded(doc):
    return bool(doc.get('custom_osr_construction_equipment') or doc.get('custom_osr_construction_unit') or doc.get('custom_osr_kind') in {'construction','erection','civil'})


def validate_task(doc,method=None,*,assigning_user=None,review_check=False):
    import frappe
    old=doc.get_doc_before_save()
    for field in ('custom_osr_construction_work_started_at','custom_osr_construction_work_closed_at'):
        if old and old.get(field) and doc.get(field)!=old.get(field):
            frappe.throw('Actual construction work history cannot be rewritten')
    if old and _guarded(old) and not _guarded(doc):
        frappe.throw('Construction execution scope cannot be removed to bypass allocation checks')
    if not _guarded(doc) and not (old and _guarded(old)):
        return
    was_active=old and old.status in {'Working','Pending Review'}
    if was_active and doc.status not in ACTIVE and doc.status!='Cancelled':
        frappe.throw('Active construction work requires reviewed handback before status reset')
    future_reservation=doc.status in {'Open','Overdue'} and doc.get('custom_osr_construction_release')
    if assigning_user is None and doc.status not in ACTIVE and not review_check and not was_active and not future_reservation:
        return
    release_name=doc.get('custom_osr_construction_release')
    if not release_name:
        frappe.throw('Submitted construction allocation review required before assignment/work')
    release=frappe.get_doc(RELEASE,release_name);release.check_permission('read')
    if release.docstatus!=1 or release.accepted!=1 or release.task!=doc.name or release.project!=doc.project:
        frappe.throw('Construction allocation review is missing, revoked or out of scope')
    packet,raw=_attachment(release)
    if hashlib.sha256(raw).hexdigest()!=release.evidence_sha256:
        frappe.throw('Reviewed allocation evidence has changed')
    project=frappe.get_doc('Project',doc.project);project.check_permission('read')
    allocation=packet['allocation'];asset=frappe.get_doc('Asset',allocation['equipment']);asset.check_permission('read')
    now=datetime.now(timezone.utc)
    if doc.status=='Working' and (old is None or old.status!='Working') and not moment(allocation['start_at'])<=now<moment(allocation['finish_at']):
        frappe.throw('Work start is outside the reviewed allocation window')
    if doc.status=='Completed' and (now<moment(allocation['finish_at']) or not packet.get('completion_record')):
        frappe.throw('Completion requires finished work and reviewed handover evidence')
    if was_active and doc.status=='Cancelled' and (not packet.get('suspension_handback_record') or 'Projects Manager' not in set(frappe.get_roles())):
        frappe.throw('Cancellation of active construction requires reviewed suspension/handback')
    # Serialize allocations sharing machinery or workers. Query again after locks.
    live_rows={}
    for kind,names in (('Asset',[asset.name]),('Employee',sorted(allocation['workers']))):
        for name in names:
            rows=frappe.db.sql(f'SELECT * FROM `tab{kind}` WHERE name=%s FOR UPDATE',(name,),as_dict=True)
            if not rows:frappe.throw('Construction resource was removed during allocation')
            live_rows[(kind,name)]=dict(rows[0])
    employees={}
    local_start=moment(allocation['start_at']).astimezone(ZoneInfo(packet['calendar']['timezone']))
    local_end=moment(allocation['finish_at']).astimezone(ZoneInfo(packet['calendar']['timezone']))
    worker_records={w['id']:w for w in packet['workers']}
    for name in allocation['workers']:
        employee=frappe.get_doc('Employee',name);employee.check_permission('read');employees[name]=live_rows[('Employee',name)]
        authorities=json.loads(employees[name].get('custom_osr_construction_authorisations') or '[]')
        authority=next((r for r in authorities if r.get('record_id')==worker_records[name].get('authority_record')),None)
        if authority is None:frappe.throw('Current native employee authorisation is missing')
        _resolve_evidence(authority,'Employee',name)
        employees[name]['authorisations']=authorities
        employees[name]['on_leave']=bool(frappe.get_all('Leave Application',filters={'employee':name,'docstatus':1,'status':'Approved',
            'from_date':['<=',local_end.date()],'to_date':['>=',local_start.date()]},pluck='name'))
        shift_name=worker_records[name].get('shift_type')
        assignments=frappe.get_all('Shift Assignment',filters={'employee':name,'shift_type':shift_name,
            'docstatus':1,'status':'Active','start_date':['<=',local_start.date()]},
            or_filters=[['end_date','>=',local_end.date()],['end_date','is','not set']],pluck='name') if shift_name else []
        employees[name]['shift_covers_allocation']=False
        employees[name]['holiday_closed']=True
        if assignments:
            shift=frappe.get_doc('Shift Type',shift_name);shift.check_permission('read')
            def seconds(value):
                if isinstance(value,timedelta):return value.total_seconds()
                parts=[float(x) for x in str(value).split(':')]
                return parts[0]*3600+parts[1]*60+(parts[2] if len(parts)>2 else 0)
            shift_start=seconds(shift.start_time);shift_end=seconds(shift.end_time)
            base=local_start.replace(hour=0,minute=0,second=0,microsecond=0)+timedelta(seconds=shift_start)
            if base>local_start:base-=timedelta(days=1)
            finish=base+timedelta(seconds=(shift_end-shift_start)%86400)
            employees[name]['shift_covers_allocation']=base<=local_start<local_end<=finish
            holidays=frappe.get_doc('Holiday List',packet['calendar']['holiday_list']);holidays.check_permission('read')
            company=frappe.get_doc('Company',project.company);company.check_permission('read')
            native_holidays=employees[name].get('holiday_list') or shift.get('holiday_list') or company.get('default_holiday_list')
            if native_holidays!=holidays.name:frappe.throw('Reviewed calendar differs from the employee/shift holiday list')
            closed={str(row.holiday_date) for row in holidays.holidays}
            employees[name]['holiday_closed']=any((local_start.date()+timedelta(days=d)).isoformat() in closed
                for d in range((local_end.date()-local_start.date()).days+1))
    if assigning_user is not None and assigning_user not in {e.get('user_id') for e in employees.values()}:
        frappe.throw('Assigned user is outside the reviewed construction crew')
    competitors=[]
    for row in frappe.get_all('Task',filters={'custom_osr_construction_equipment':['is','set']},
            or_filters=[['status','in',sorted(RESERVED|{'Completed'})],['custom_osr_construction_work_started_at','is','set']],
            fields=['name','status','custom_osr_construction_release','custom_osr_construction_work_started_at',
                    'custom_osr_construction_work_closed_at'],limit_page_length=0):
        if row.name==doc.name:continue
        started=row.get('custom_osr_construction_work_started_at')
        if not row.custom_osr_construction_release:
            if started or row.status in ACTIVE:
                frappe.throw('Competing construction work has no retained allocation review')
            continue  # An unreviewed planning draft does not reserve resources.
        other=frappe.get_doc(RELEASE,row.custom_osr_construction_release)
        if not started and row.status!='Completed' and (other.docstatus!=1 or other.accepted!=1):
            continue
        evidence,other_raw=_attachment(other)
        if other.task!=row.name or hashlib.sha256(other_raw).hexdigest()!=other.evidence_sha256:
            frappe.throw('Competing reviewed allocation evidence has changed')
        competing=dict(evidence['allocation'])
        if started:
            competing['start_at']=moment(started).isoformat()
            closed=row.get('custom_osr_construction_work_closed_at')
            competing['finish_at']=moment(closed).isoformat() if closed else max(now,moment(competing['finish_at'])).isoformat()
        competitors.append(competing)
    current=dict(name=doc.name,workers=json.loads(doc.get('custom_osr_construction_qualified_workers') or '[]'),
        **{f:doc.get('custom_osr_construction_'+f) for f in ('department','unit','front','crew','shift','equipment')})
    asset_data=live_rows[('Asset',asset.name)]
    asset_data['controlled_lifecycle']=json.loads(asset_data.get('custom_osr_fleet_lifecycle') or '{}')
    _resolve_evidence(asset_data['controlled_lifecycle'],'Asset',asset.name)
    asset_data['open_repairs']=frappe.get_all('Asset Repair',filters={'asset':asset.name,'docstatus':['!=',2],
        'repair_status':['!=','Completed']},pluck='name')
    try:
        check_packet(packet,dict(name=project.name,company=project.company,revision=project.get('custom_osr_package_sha256')),
            current,asset_data,employees,competitors)
    except (ValueError,KeyError,TypeError) as error:
        frappe.throw('Construction allocation blocked: '+str(error))
    if doc.status=='Working' and not doc.get('custom_osr_construction_work_started_at'):
        doc.set('custom_osr_construction_work_started_at',now.strftime('%Y-%m-%d %H:%M:%S'))
    if doc.status in {'Completed','Cancelled'} and was_active:
        doc.set('custom_osr_construction_work_closed_at',now.strftime('%Y-%m-%d %H:%M:%S'))


def validate_assignment(doc,method=None):
    if doc.reference_type=='Task' and doc.status=='Open':
        import frappe
        validate_task(frappe.get_doc('Task',doc.reference_name),assigning_user=doc.allocated_to)


def attach_review(doc,method=None):
    """Attach reviewed metadata; Task remains at its existing business status."""
    import frappe
    task=frappe.get_doc('Task',doc.task);task.check_permission('write')
    packet,_=_attachment(doc);allocation=packet['allocation']
    for field in ('department','unit','front','crew','shift','equipment'):
        task.set('custom_osr_construction_'+field,allocation[field])
    task.set('custom_osr_construction_qualified_workers',json.dumps(allocation['workers']))
    task.set('custom_osr_construction_release',doc.name)
    validate_task(task,review_check=True)
    task.save()
