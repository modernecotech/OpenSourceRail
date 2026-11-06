"""Executed only inside the freshly created disposable Frappe site.

This is a synthetic native business acceptance fixture, never physical release.
No production endpoint, permission bypass or engineering-input mutation is added.
"""
from datetime import timedelta
from pathlib import Path
import json
import os
import sys
sys.path.insert(0, '/tmp/osr-native-v06')
from contracts import validate_input, handback_guard, digest, FLAGS
import frappe
from osr_erpnext import setup, planning, api, components, integration, engineering_identity
from erpnext.manufacturing.doctype.work_order.work_order import make_stock_entry

BASE = Path('/tmp/osr-native-v06')
INPUT = validate_input(json.loads((BASE/'input.json').read_text()))
STATE = BASE/'state.json'


def insert(dt, **kw):
    return frappe.get_doc(dict(doctype=dt, **kw)).insert()


def refuse(callback):
    try:
        callback()
    except (ValueError, frappe.ValidationError, frappe.PermissionError):
        return
    raise AssertionError('Expected native/identity refusal did not occur')


def quality(state, reference_type, reference, item, line, value):
    previous = frappe.session.user
    frappe.set_user(state['users']['inspector']['user'])
    try:
        qa = insert('Quality Inspection', company=state['company'],
            inspection_type='Incoming' if reference_type == 'Purchase Receipt' else 'In Process',
            reference_type=reference_type, reference_name=reference, item_code=item,
            child_row_reference=line, sample_size=1, inspected_by=frappe.session.user,
            remarks='SIMULATION software record only; no physical measurement or calibration',
            readings=[dict(specification=state['parameter'], numeric=0, value='Pass', reading_value=value)])
        qa.submit()
        return qa
    finally:
        frappe.set_user(previous)


def manufacture(state, serial):
    values = dict(bom=state['bom'], quantity=1, source_warehouse=state['warehouse'],
                  wip_warehouse=state['warehouse'], fg_warehouse=state['warehouse'],
                  start=frappe.utils.nowdate()+' 01:00:00')
    p = components.preview(state['project'], 'manufacturing', serial.lower(), values)
    wo = frappe.get_doc('Work Order', components.apply(state['project'], 'manufacturing', serial.lower(), values, p['fingerprint'])['name'])
    wo.skip_transfer=1; wo.save(); wo.submit()
    stock = frappe.get_doc(make_stock_entry(wo.name, 'Manufacture', 1))
    for row in stock.items:
        row.project=state['project']
        if row.item_code == state['finished_item']:
            row.serial_no=serial; row.batch_no=state['batch']; row.use_serial_batch_fields=1
    stock.insert(); stock.submit(); stock.reload(); wo.reload()
    assert wo.produced_qty == 1 and frappe.db.exists('Serial No', serial)
    line=next(r.name for r in stock.items if r.item_code == state['finished_item'])
    issued=insert('Stock Entry', stock_entry_type='Material Issue', company=state['company'],
        items=[dict(item_code=state['finished_item'], qty=1, s_warehouse=state['warehouse'], serial_no=serial,
                    batch_no=state['batch'], use_serial_batch_fields=1, project=state['project'])])
    issued.submit()
    return dict(serial=serial, work_order=wo.name, stock_entry=stock.name, finished_row=line,
                installation_record=issued.name)


def bootstrap():
    setup.create_evaluation_company(); setup.install()
    run=os.environ['OSR_TEST_RUN']; company='OSR v06 simulation '+run
    insert('Company', company_name=company, abbr='V'+digest(run)[:7].upper(), default_currency='USD', country='Iraq',
           chart_of_accounts='Standard', create_chart_of_accounts_based_on='Standard Template')
    bundle=dict(project_twin=dict(city=INPUT['city'], revision_id='v06-'+run),
        manufacturing_tasks=[dict(manufacturing_uid='v06-manufacture', title='SIM current occurrence manufacture',
            asset_id='SIM-V06-HVAC', candidate_id=INPUT['identities']['candidate_id'], fixture_input_id=INPUT['input_id'])],
        maintenance_tasks=[dict(task_uid='v06-maintain', title='SIM inspect and repair', asset_id='SIM-V06-HVAC')])
    plan=planning.make_plan(bundle); imported=api.import_plan(plan, company)
    assert api.import_plan(plan, company)['created'] == 0
    project=frappe.get_doc('Project', imported['project'])
    label='SIM v06 fixture stores'
    project.custom_osr_package_sha256=INPUT['input_id']
    project.custom_osr_config_sha256=INPUT['identities']['candidate_id']
    project.custom_osr_config=json.dumps(dict(organisation=dict(warehouses=[label]))); project.save()
    warehouse=insert('Warehouse', warehouse_name=label, company=company,
        custom_osr_master_key=planning.digest([company,INPUT['city'],'Warehouse',label])).name
    group=frappe.db.get_value('Item Group', {'is_group':0}, 'name')
    supplier=insert('Supplier', supplier_name='SIM v06 supplier '+run, supplier_type='Company', supplier_group='All Supplier Groups')
    users={}
    from frappe.utils.password import set_encrypted_password
    for kind, roles in [('inspector',['Projects Manager','Quality Manager','Stock Manager','Stock User','Manufacturing Manager','Manufacturing User']), ('reviewer',['Projects Manager']), ('observer',['Projects User','Support Team'])]:
        email='v06-'+kind+'-'+run+'@example.invalid'
        user=insert('User', email=email, first_name='SIM v06 '+kind, send_welcome_email=0,
                    roles=[dict(role=r) for r in roles])
        key=frappe.generate_hash(length=20); secret=frappe.generate_hash(length=32)
        user.api_key=key; user.save(); set_encrypted_password('User', user.name, secret, 'api_secret')
        frappe.share.add('Project', project.name, user.name, read=1, write=kind!='observer', notify=0)
        users[kind]=dict(user=user.name,key=key,secret=secret)
    from frappe.installer import update_site_config
    policy={users['observer']['user']:dict(cities=[INPUT['city']], environments=['simulation'], projects=[project.name])}
    update_site_config('osr_integration_users',policy); frappe.conf.osr_integration_users=policy
    raw=insert('Item', item_code='SIM-V06-RAW-'+run, item_name='Synthetic kit for '+INPUT['source_occurrence']['id'],
        item_group=group, stock_uom='Nos', is_stock_item=1, is_purchase_item=1, inspection_required_before_purchase=1,
        description=json.dumps(dict(source=INPUT['source_occurrence'], sha256=INPUT['source_occurrence_sha256'], conversion=INPUT['conversion'])))
    fg=insert('Item', item_code='SIM-V06-FG-'+run, item_name='SIM v06 HVAC fixture', item_group=group, stock_uom='Nos',
              is_stock_item=1, has_serial_no=1, has_batch_no=1)
    batch=insert('Batch', batch_id='SIM-V06-BATCH-'+run, item=fg.name)
    bom=insert('BOM', item=fg.name, company=company, quantity=1, currency='USD',
               items=[dict(item_code=raw.name, qty=1, rate=1)]); bom.submit()
    mapping=dict(schema='osr-execution-proposal/1', city=INPUT['city'], asset_id='SIM-V06-HVAC',
        engineering_revision=INPUT['identities']['candidate_id'], engineering_sha256=INPUT['input_id'],
        identities=INPUT['identities'], fixture_input_id=INPUT['input_id'],
        mapping=dict(review_reference='SIM source-bound conversion '+INPUT['input_id'], items=[dict(
            component_type_id=INPUT['source_occurrence']['id'], erp_item_code=fg.name, uom='Nos', production_bom=bom.name,
            conversion_rule=INPUT['conversion']['basis'], inspection_reference='SIM no physical qualification',
            drawing_reference='source-occurrence:'+INPUT['source_occurrence_sha256'])]))
    mapping['sha256']=digest(mapping)
    preview=integration.preview_execution(project.name,mapping)
    made=integration.apply_execution(project.name,mapping,preview['fingerprint'])
    assert integration.apply_execution(project.name,mapping,preview['fingerprint']) == made
    state=dict(company=company, project=project.name, warehouse=warehouse, raw=raw.name, finished_item=fg.name,
        bom=bom.name, batch=batch.name, mapping=made['mappings'][0], users=users,
        parameter=insert('Quality Inspection Parameter', parameter='SIM v06 record code '+run).name)
    today=frappe.utils.nowdate()
    po=insert('Purchase Order',supplier=supplier.name,company=company,schedule_date=today,
              items=[dict(item_code=raw.name,qty=4,rate=1,warehouse=warehouse,project=project.name)]);po.submit()
    receipt=insert('Purchase Receipt',supplier=supplier.name,company=company,
        items=[dict(item_code=raw.name,qty=4,rate=1,warehouse=warehouse,project=project.name,
                    purchase_order=po.name,purchase_order_item=po.items[0].name)])
    failed=quality(state,'Purchase Receipt',receipt.name,raw.name,receipt.items[0].name,'Fail')
    receipt.reload();receipt.items[0].quality_inspection=failed.name;receipt.save()
    refuse(receipt.submit);receipt.reload();assert receipt.docstatus==0
    ncr=insert('Issue',subject='SIM incoming nonconformance '+run,project=project.name,description='Rejected native QI '+failed.name)
    rework=insert('Task',subject='SIM software rework '+run,project=project.name,description='Explicit synthetic corrective preparation for '+failed.name)
    rework.status='Completed';rework.save()
    passed=quality(state,'Purchase Receipt',receipt.name,raw.name,receipt.items[0].name,'Pass')
    receipt.reload();receipt.items[0].quality_inspection=passed.name;receipt.save();receipt.submit()
    state.update(po=po.name,receipt=receipt.name,failed_qa=failed.name,passed_qa=passed.name,incoming_ncr=ncr.name,rework_task=rework.name)
    old=manufacture(state,'SIM-V06-OLD-'+run);state['old']=old
    fixed=frappe.db.get_value('Account',{'company':company,'is_group':0,'account_type':'Fixed Asset'},'name')
    category=insert('Asset Category',asset_category_name='SIM v06 positions '+run,accounts=[dict(company_name=company,fixed_asset_account=fixed)])
    assetitem=insert('Item',item_code='SIM-V06-POS-'+run,item_name='SIM position',item_group=group,stock_uom='Nos',is_stock_item=0,is_fixed_asset=1,asset_category=category.name)
    location=insert('Location',location_name='SIM v06 '+run)
    yesterday=str(frappe.utils.getdate(today)-timedelta(days=1));asset_id='SIM-V06-HVAC:'+run
    asset=insert('Asset',company=company,item_code=assetitem.name,asset_name=asset_id,asset_category=category.name,
        location=location.name,purchase_date=yesterday,available_for_use_date=yesterday,is_existing_asset=1,
        gross_purchase_amount=1,calculate_depreciation=0,custom_osr_asset_id=asset_id);asset.submit()
    state.update(asset=asset.name,asset_id=asset_id)
    # Actual installed HRMS app and native HR record, not a capability declaration.
    assert 'hrms' in frappe.get_installed_apps()
    state['training_program']=insert('Training Program',training_program='SIM v06 induction '+run,
        company=company,description='Software-only training record; no competency or authorisation claimed').name
    STATE.write_text(json.dumps(state));frappe.db.commit()


def repair():
    state=json.loads(STATE.read_text());event=json.loads((BASE/'event.json').read_text())
    issue=frappe.get_doc('Issue',event['issue'])
    assert issue.project == state['project'] and issue.custom_osr_asset_id == state['asset_id']
    assert len([r for r in json.loads(issue.custom_osr_condition_history) if r['event_id']==event['event_id']]) == 1
    frappe.set_user(state['users']['observer']['user'])
    duplicate=integration.condition_event(event['body']);assert duplicate['duplicate'] and duplicate['issue']==issue.name
    refuse(lambda:integration.condition_event({**event['body'],'environment':'physical'}))
    frappe.set_user('Administrator')
    proposal=dict(schema='osr-condition-repair/1',key='v06-repair',failure_date=frappe.utils.nowdate()+' 01:00:00',
        expected_downtime_hours=1,technician='Administrator',description='SIM repair and serial replacement only',
        parts=[dict(item=state['raw'],warehouse=state['warehouse'],quantity=1)],
        evidence_references=['removed-serial:'+state['old']['serial'],'fixture-input:'+INPUT['input_id']])
    p=integration.preview_repair(issue.name,proposal)
    made=integration.apply_repair(issue.name,proposal,p['fingerprint'])
    doc=frappe.get_doc('Asset Repair',made['name']);doc.actions_performed='SIM only; physical inspection/handback remain required'
    doc.repair_status='Completed';doc.completion_date=frappe.utils.nowdate()+' 02:00:00';doc.save();doc.submit()
    assert frappe.db.exists('Stock Entry',{'asset_repair':doc.name,'docstatus':1})
    assert not integration.apply_repair(issue.name,proposal,p['fingerprint'])['automatic_handback']
    replacement=manufacture(state,'SIM-V06-NEW-'+os.environ['OSR_TEST_RUN']);state['replacement']=replacement
    # Latest native failure invalidates an earlier passing inspection.
    test=quality(state,'Stock Entry',replacement['stock_entry'],state['finished_item'],replacement['finished_row'],'Pass')
    late=quality(state,'Stock Entry',replacement['stock_entry'],state['finished_item'],replacement['finished_row'],'Fail')
    expected=dict(identities=INPUT['identities'],serial=replacement['serial'],latest_test=late.name,reviewer=state['users']['reviewer']['user'])
    observed=dict(**expected,test_status=late.status,inspector=state['users']['inspector']['user'],repair_status=doc.repair_status,handback_required=bool(doc.custom_osr_handback_required))
    refuse(lambda:handback_guard(expected,observed))
    latest=quality(state,'Stock Entry',replacement['stock_entry'],state['finished_item'],replacement['finished_row'],'Pass')
    expected['latest_test']=latest.name; observed.update(latest_test=latest.name,test_status=latest.status)
    refuse(lambda:handback_guard(expected,{**observed,'reviewer':observed['inspector']}))
    wrong=json.loads(json.dumps(observed));wrong['identities']['candidate_id']='f'*64
    refuse(lambda:handback_guard(expected,wrong))
    task=insert('Task',subject='SIM independent business handback '+os.environ['OSR_TEST_RUN'],project=state['project'],
        description=json.dumps(dict(expected=expected,asset=state['asset'],repair=doc.name,removed_serial=state['old']['serial'],
            installation_record=replacement['installation_record'],scope='Software-business review; physical handback remains open')))
    frappe.share.add('Task',task.name,state['users']['reviewer']['user'],read=1,write=1,notify=0)
    state.update(issue=issue.name,repair=doc.name,review_task=task.name,latest_test=latest.name,late_failed_test=late.name,
                 expected_handback=expected)
    STATE.write_text(json.dumps(state));frappe.db.commit()


def readback():
    state=json.loads(STATE.read_text());task=frappe.get_doc('Task',state['review_task'])
    assert task.status=='Completed' and task.modified_by==state['users']['reviewer']['user']
    # Read the immutable native mapping, chronological latest submitted QI,
    # and actual native serial/batch bundle instead of echoing fixture inputs.
    mapping=frappe.get_doc('OSR Execution Mapping',state['mapping'])
    native_package=json.loads(mapping.source_package)['package']
    assert native_package['identities']==INPUT['identities']
    assert mapping.engineering_revision==INPUT['identities']['candidate_id'] and mapping.engineering_sha256==INPUT['input_id']
    assert mapping.erp_item==state['finished_item']
    stock=frappe.get_doc('Stock Entry',state['replacement']['stock_entry'])
    finished=next(r for r in stock.items if r.name==state['replacement']['finished_row'] and r.item_code==mapping.erp_item)
    serial_bundle=frappe.get_doc('Serial and Batch Bundle',finished.serial_and_batch_bundle)
    native_serials=[r.serial_no for r in serial_bundle.entries if r.serial_no]
    assert len(native_serials)==1
    actual_serial=native_serials[0]
    installed=frappe.get_doc('Stock Entry',state['replacement']['installation_record'])
    installed_row=next(r for r in installed.items if r.item_code==mapping.erp_item)
    installed_bundle=frappe.get_doc('Serial and Batch Bundle',installed_row.serial_and_batch_bundle)
    assert installed.docstatus==1 and installed_row.s_warehouse and not installed_row.t_warehouse
    assert [r.serial_no for r in installed_bundle.entries if r.serial_no]==[actual_serial]
    latest=frappe.get_all('Quality Inspection',filters=dict(reference_type='Stock Entry',reference_name=stock.name,
        item_code=mapping.erp_item,child_row_reference=finished.name,docstatus=1),pluck='name',order_by='creation desc, name desc',limit_page_length=1)
    assert len(latest)==1
    qa=frappe.get_doc('Quality Inspection',latest[0]);repair_doc=frappe.get_doc('Asset Repair',state['repair'])
    observed=dict(identities=native_package['identities'],serial=actual_serial,latest_test=qa.name,test_status=qa.status,
        reviewer=task.modified_by,inspector=qa.inspected_by,repair_status=repair_doc.repair_status,
        handback_required=bool(repair_doc.custom_osr_handback_required))
    reviewed=handback_guard(state['expected_handback'],observed)
    identity=dict(schema='osr-engineering-qa-map/1',configuration_sha256=INPUT['input_id'],design_revision=INPUT['identities']['candidate_id'],
        state='as-maintained',asset_id=state['asset_id'],characteristics=[dict(inspection_id='SIM-record-code',instance_id=state['asset_id'],
        part_id=INPUT['source_occurrence']['id'],part_revision=INPUT['identities']['candidate_id'],serial=observed['serial'],batch=state['batch'],
        characteristic='Synthetic record code, no physical measurement',unit='simulation-code',minimum=None,maximum=None,joint_ids=[])])
    identity['sha256']=digest(identity)
    binding=engineering_identity.bind_quality_result(identity,dict(project=state['project'],company=state['company'],
        work_order=state['replacement']['work_order'],quality_inspection=qa.name,material_batch=state['batch'],nonconformance=state['issue'],
        calibration_record='SIM-NO-PHYSICAL-CALIBRATION'),dict(inspection_id='SIM-record-code',configuration_sha256=INPUT['input_id'],
        part_revision=INPUT['identities']['candidate_id'],serial=observed['serial'],batch=state['batch'],unit='simulation-code',value=1))
    refs=[('OSR Execution Mapping',state['mapping']),('Serial and Batch Bundle',serial_bundle.name),('Serial and Batch Bundle',installed_bundle.name),('BOM',state['bom']),('Purchase Order',state['po']),('Purchase Receipt',state['receipt']),('Quality Inspection',state['failed_qa']),
        ('Quality Inspection',qa.name),('Asset',state['asset']),('Issue',state['issue']),('Asset Repair',state['repair']),
        ('Task',task.name),('Training Program',state['training_program'])]
    for unit in (state['old'],state['replacement']):
        refs += [('Work Order',unit['work_order']),('Stock Entry',unit['stock_entry']),('Stock Entry',unit['installation_record']),('Serial No',unit['serial'])]
    records=[]
    for dt,name in refs:
        doc=frappe.get_doc(dt,name)
        records.append(dict(doctype=dt,name=name,docstatus=doc.docstatus,owner=doc.owner,modified_by=doc.modified_by,
            values={k:doc.get(k) for k in ('status','repair_status','produced_qty','custom_osr_handback_required','inspected_by','custom_osr_asset_id') if doc.meta.has_field(k)}))
    (BASE/'readback.json').write_text(json.dumps(dict(records=records,review=reviewed,binding=binding,review_context=dict(task=task.name,reviewer=task.modified_by,
        inspector=qa.inspected_by,quality_inspection=qa.name,current_serial=observed['serial'],native_mapping=state['mapping'],
        mapping_identities=native_package['identities'],native_inspection_order='creation desc, name desc',
        serial_bundle=serial_bundle.name,installation_bundle=installed_bundle.name)),default=str));frappe.db.commit()


os.chdir('/home/frappe/frappe-bench/sites');frappe.init(site=os.environ['OSR_TEST_SITE']);frappe.connect()
frappe.flags.mute_emails=True;frappe.set_user('Administrator')
try:
    {'bootstrap':bootstrap,'repair':repair,'readback':readback}[sys.argv[1]]()
    print('PASS native v06 fixture '+sys.argv[1])
finally:
    frappe.destroy()
