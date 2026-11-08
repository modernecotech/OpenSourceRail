"""Explicit wheel-candidate software lifecycle in a new disposable native site.

This file is runnable only by the bounded native runner. Every inspection is
simulated, every drawing remains a controlled research draft, and every adapter
physical/release flag remains false. No hardware qualification is inferred.
"""
from datetime import timedelta
from pathlib import Path
import json
import os
import sys
sys.path.insert(0,'/tmp/osr-native-v06')
from candidate_contracts import validate_input,project_context
from contracts import digest,FLAGS
import frappe
from osr_erpnext import setup,planning,api,components,integration,candidate_delivery as delivery
from erpnext.manufacturing.doctype.work_order.work_order import make_stock_entry

BASE=Path('/tmp/osr-native-v06');STATE=BASE/'state.json'


def insert(dt,**values):return frappe.get_doc(dict(doctype=dt,**values)).insert()


def refuse(callback):
    try:callback()
    except (ValueError,frappe.ValidationError,frappe.PermissionError,FileNotFoundError):return
    raise AssertionError('Expected native permission/source refusal did not occur')


def as_user(state,role,callback):
    before=frappe.session.user;frappe.set_user(state['users'][role]['user'])
    try:return callback()
    finally:frappe.set_user(before)


def quality(state,reference_type,reference,item,line,*,passed=True,submit=True):
    """Use the actual controlled research limit, with explicitly simulated values."""
    rows=[]
    for i,c in enumerate(state['characteristics']):
        lower=c['minimum'];upper=c['maximum']
        sample=(lower+upper)/2 if lower is not None and upper is not None else (lower if lower is not None else upper)
        if not passed and i==0:sample=(upper+max(1,abs(upper)*.01) if upper is not None else lower-max(1,abs(lower)*.01))
        formula=' and '.join(x for x in ((f'reading_1 >= {lower!r}' if lower is not None else ''),(f'reading_1 <= {upper!r}' if upper is not None else '')) if x)
        rows.append(dict(specification=state['parameters'][i],numeric=1,formula_based_criteria=1,
            acceptance_formula=formula,reading_1=str(sample)))
    def make():
        qa=insert('Quality Inspection',company=state['company'],inspection_type='Incoming' if reference_type=='Purchase Receipt' else 'In Process',
            reference_type=reference_type,reference_name=reference,item_code=item,child_row_reference=line,
            sample_size=1,inspected_by=frappe.session.user,readings=rows,
            remarks=json.dumps(dict(scope='SIMULATION generated readings; no physical measurement, calibration or release',
                inspection_sidecar=state['inspection_document'],characteristics=state['characteristics'],**FLAGS)))
        if submit:qa.submit()
        return qa
    return as_user(state,'inspector',make)


def manufacture(state,serial):
    values=dict(bom=state['bom'],quantity=1,source_warehouse=state['warehouse'],wip_warehouse=state['warehouse'],
        fg_warehouse=state['warehouse'],start=frappe.utils.nowdate()+' 01:00:00')
    preview=components.preview(state['project'],'manufacturing',serial.lower(),values)
    wo=frappe.get_doc('Work Order',components.apply(state['project'],'manufacturing',serial.lower(),values,preview['fingerprint'])['name'])
    wo.skip_transfer=1;wo.save();wo.submit()
    stock=frappe.get_doc(make_stock_entry(wo.name,'Manufacture',1))
    for row in stock.items:
        row.project=state['project']
        if row.item_code==state['finished_item']:row.serial_no=serial;row.batch_no=state['batch'];row.use_serial_batch_fields=1
    stock.insert();stock.submit();stock.reload();wo.reload();assert wo.produced_qty==1
    finished=next(r for r in stock.items if r.item_code==state['finished_item'])
    installed=insert('Stock Entry',stock_entry_type='Material Issue',company=state['company'],items=[dict(
        item_code=state['finished_item'],qty=1,s_warehouse=state['warehouse'],serial_no=serial,batch_no=state['batch'],
        use_serial_batch_fields=1,project=state['project'])]);installed.submit()
    return dict(serial=serial,work_order=wo.name,stock_entry=stock.name,finished_row=finished.name,installation_record=installed.name)


def install(state,unit,**extra):
    return as_user(state,'engineer',lambda:delivery.register_installation(project=state['project'],pack_sha256=state['pack_sha256'],
        part_id=state['part_id'],asset=state['asset'],source_pattern_id=state['source_pattern_id'],ordinal=0,train_index=0,
        work_order=unit['work_order'],manufacture_stock=unit['stock_entry'],installation_stock=unit['installation_record'],**extra))


def bootstrap():
    source=INPUT['review_pack'];component=next(r for r in source['components'] if r['source_part']['id']==INPUT['component_id'])
    setup.create_evaluation_company();setup.install();run=os.environ['OSR_TEST_RUN'];company='OSR wheel SIM '+run
    insert('Company',company_name=company,abbr='W'+digest(run)[:7].upper(),default_currency='USD',country='Iraq',
        chart_of_accounts='Standard',create_chart_of_accounts_based_on='Standard Template')
    bundle=dict(project_twin=dict(city=INPUT['city'],revision_id='wheel-'+run),manufacturing_tasks=[dict(
        manufacturing_uid='wheel-source-manufacture',title='SIM source component manufacture',candidate_id=INPUT['identities']['candidate_id'])],maintenance_tasks=[])
    plan=planning.make_plan(bundle);made=api.import_plan(plan,company);assert api.import_plan(plan,company)['created']==0
    project=frappe.get_doc('Project',made['project']);label='SIM wheel stores '+run
    project.custom_osr_package_sha256=INPUT['input_id'];project.custom_osr_config_sha256=INPUT['identities']['candidate_id']
    project.custom_osr_config=json.dumps(dict(organisation=dict(warehouses=[label])));project.save()
    warehouse=insert('Warehouse',warehouse_name=label,company=company,custom_osr_master_key=planning.digest([company,INPUT['city'],'Warehouse',label])).name
    context=project_context(INPUT,project=project.name,company=company);delivery.provision_project(project.name,context)
    from frappe.utils.password import set_encrypted_password
    users={}
    roles={'engineer':['Projects Manager','Manufacturing Manager','Manufacturing User','Stock Manager','Stock User','Asset Manager'],
        'inspector':['Projects Manager','Quality Manager','Stock Manager','Stock User'],
        'reviewer':['Projects Manager','Manufacturing Manager','Quality Manager'],'observer':['Projects User','Support Team']}
    for kind,names in roles.items():
        user=insert('User',email='wheel-'+kind+'-'+run+'@example.invalid',first_name='SIM wheel '+kind,
            send_welcome_email=0,roles=[dict(role=r) for r in names]);key=frappe.generate_hash(length=20);secret=frappe.generate_hash(length=32)
        user.api_key=key;user.save();set_encrypted_password('User',user.name,secret,'api_secret')
        frappe.share.add('Project',project.name,user.name,read=1,write=kind!='observer',notify=0);users[kind]=dict(user=user.name,key=key,secret=secret)
    policy={u['user']:dict(cities=[INPUT['city']],environments=['simulation'],projects=[project.name]) for u in users.values()}
    from frappe.installer import update_site_config
    update_site_config('osr_integration_users',policy);frappe.conf.osr_integration_users=policy
    files={}
    from frappe.utils.file_manager import save_file
    for row in source['artifacts']:
        raw=(BASE/'artifacts'/row['path']).read_bytes();assert digest_bytes(raw)==row['sha256'] and len(raw)==row['bytes']
        file=save_file(Path(row['path']).name,raw,'Project',project.name,is_private=1);files[row['path']]=file.name
    state=dict(company=company,project=project.name,warehouse=warehouse,users=users,part_id=INPUT['component_id'],
        pack_sha256=source['sha256'],files=files,context=context,characteristics=component['documents']['inspection']['definition']['characteristics'],
        inspection_document=component['documents']['inspection']['sha256'])
    group=frappe.db.get_value('Item Group',{'is_group':0},'name')
    as_user(state,'engineer',lambda:delivery.register_pack(project.name,source,files))
    preview=as_user(state,'engineer',lambda:delivery.preview(project.name,source['sha256'],group))
    refuse(lambda:as_user(state,'engineer',lambda:delivery.review(project.name,source['sha256'],group,preview['fingerprint'])))
    refuse(lambda:as_user(state,'observer',lambda:delivery.apply(project.name,source['sha256'],'0'*64)))
    reviewed=as_user(state,'reviewer',lambda:delivery.review(project.name,source['sha256'],group,preview['fingerprint']))
    applied=as_user(state,'engineer',lambda:delivery.apply(project.name,source['sha256'],reviewed['review_id']))['applied']
    assert not as_user(state,'engineer',lambda:delivery.apply(project.name,source['sha256'],reviewed['review_id']))['created']
    mapped=next(r for r in applied['components'] if r['part_id']==INPUT['component_id'])
    for record in applied['records']:
        frappe.share.add(record['doctype'],record['name'],users['observer']['user'],read=1,write=0,notify=0)
    bom=frappe.get_doc('BOM',mapped['bom']);bom.submit()  # Explicit simulation transaction, never adapter auto-submit.
    source_price=component['source_part']['counted_direct_parts_process_usd_per_train']['base']/component['source_part']['quantity_per_train']
    assert mapped['source_direct_usd_per_unit']==source_price
    assert abs(sum(r.qty*r.rate for r in bom.items)-mapped['native_stock_usd_per_unit'])<.000001
    state.update(mapping=applied,bom=bom.name,raw=mapped['raw_items'][0],finished_item=mapped['finished_item'],review_task=reviewed['task'])
    state['batch']=insert('Batch',batch_id='SIM-WHEEL-BATCH-'+run,item=state['finished_item']).name
    state['parameters']=[insert('Quality Inspection Parameter',parameter='SIM '+run+' '+str(i)+' '+c['id']).name for i,c in enumerate(state['characteristics'])]
    supplier=insert('Supplier',supplier_name='SIM wheel supplier '+run,supplier_type='Company',supplier_group='All Supplier Groups')
    today=frappe.utils.nowdate();items=[dict(item_code=r.item_code,qty=4*r.qty,rate=r.rate,warehouse=warehouse,project=project.name) for r in bom.items]
    po=insert('Purchase Order',supplier=supplier.name,company=company,schedule_date=today,items=items);po.submit()
    receipt=insert('Purchase Receipt',supplier=supplier.name,company=company,items=[dict(row,
        purchase_order=po.name,purchase_order_item=native.name) for row,native in zip(items,po.items)])
    failed=quality(state,'Purchase Receipt',receipt.name,receipt.items[0].item_code,receipt.items[0].name,passed=False)
    receipt.items[0].quality_inspection=failed.name;receipt.save();refuse(receipt.submit);receipt.reload();assert receipt.docstatus==0
    ncr=insert('Issue',subject='SIM incoming research-limit hold '+run,project=project.name,description='Simulated rejected native QI '+failed.name)
    rework=insert('Task',subject='SIM corrective preparation '+run,project=project.name,status='Completed',description='No physical rework claimed; '+failed.name)
    for row in receipt.items:
        qa=quality(state,'Purchase Receipt',receipt.name,row.item_code,row.name);row.quality_inspection=qa.name
    receipt.save();receipt.submit();state.update(po=po.name,receipt=receipt.name,failed_qa=failed.name,incoming_ncr=ncr.name,rework_task=rework.name)
    state['old']=manufacture(state,'SIM-WHEEL-OLD-'+run)
    pattern=component['source_part']['serial_plan']['occurrence_pattern_ids'][0]
    position=digest(dict(context_sha256=context['sha256'],source_pattern_id=pattern,ordinal=0,train_index=0));asset_id='SIM-WD-'+position[:24]
    fixed=frappe.db.get_value('Account',{'company':company,'is_group':0,'account_type':'Fixed Asset'},'name')
    category=insert('Asset Category',asset_category_name='SIM wheel positions '+run,accounts=[dict(company_name=company,fixed_asset_account=fixed)])
    assetitem=insert('Item',item_code='SIM-WHEEL-POS-'+run,item_name='SIM counted research position',item_group=group,
        stock_uom='Nos',is_stock_item=0,is_fixed_asset=1,asset_category=category.name)
    location=insert('Location',location_name='SIM wheel '+run);yesterday=str(frappe.utils.getdate(today)-timedelta(days=1))
    asset=insert('Asset',company=company,item_code=assetitem.name,asset_name=asset_id,asset_category=category.name,location=location.name,
        purchase_date=yesterday,available_for_use_date=yesterday,is_existing_asset=1,gross_purchase_amount=source_price,
        calculate_depreciation=0,custom_osr_asset_id=asset_id);asset.submit()
    frappe.share.add('Asset',asset.name,users['observer']['user'],read=1,write=0,notify=0)
    state.update(asset=asset.name,asset_id=asset_id,source_pattern_id=pattern)
    state['initial_installation']=install(state,state['old'])['installation']
    # A gateway observer receives read access only to this installed custody
    # chain. Its role still cannot create a BOM or approve a source revision.
    refs=[('Work Order',state['old']['work_order']),('Serial No',state['old']['serial'])]
    for name in (state['old']['stock_entry'],state['old']['installation_record']):
        stock=frappe.get_doc('Stock Entry',name);refs.append(('Stock Entry',name))
        refs += [('Serial and Batch Bundle',r.serial_and_batch_bundle) for r in stock.items if r.serial_and_batch_bundle]
    for dt,name in refs:frappe.share.add(dt,name,users['observer']['user'],read=1,write=0,notify=0)
    assert 'hrms' in frappe.get_installed_apps()
    state['training_program']=insert('Training Program',training_program='SIM wheel induction '+run,company=company,
        description='Software-only draft training; no competency or physical authorisation claimed').name
    STATE.write_text(json.dumps(state));frappe.db.commit()


def digest_bytes(raw):
    from hashlib import sha256
    return sha256(raw).hexdigest()


def repair():
    state=json.loads(STATE.read_text());event=json.loads((BASE/'event.json').read_text());issue=frappe.get_doc('Issue',event['issue'])
    assert issue.project==state['project'] and issue.custom_osr_erp_asset==state['asset']
    assert as_user(state,'observer',lambda:integration.condition_event(event['body']))['duplicate']
    for key,value in [('engineering_revision','0'*64),('physical_serial_id','wrong-serial'),('project','wrong-project')]:
        count=frappe.db.count('Issue')
        refuse(lambda:as_user(state,'observer',lambda:integration.condition_event(dict(event['body'],**{key:value}))))
        assert frappe.db.count('Issue')==count
    bom=frappe.get_doc('BOM',state['bom']);raw=bom.items[0]
    proposal=dict(schema='osr-condition-repair/1',key='wheel-repair',failure_date=frappe.utils.nowdate()+' 01:00:00',
        expected_downtime_hours=1,technician='Administrator',description='SIM source component serial replacement',
        parts=[dict(item=state['raw'],warehouse=state['warehouse'],quantity=raw.qty)],
        evidence_references=['removed-serial:'+state['old']['serial'],'review-pack:'+state['pack_sha256']])
    preview=integration.preview_repair(issue.name,proposal);made=integration.apply_repair(issue.name,proposal,preview['fingerprint'])
    doc=frappe.get_doc('Asset Repair',made['name']);doc.actions_performed='SIM software replacement; physical handback still required'
    doc.repair_status='Completed';doc.completion_date=frappe.utils.nowdate()+' 02:00:00';doc.save();doc.submit()
    assert frappe.db.exists('Stock Entry',{'asset_repair':doc.name,'docstatus':1})
    replacement=manufacture(state,'SIM-WHEEL-NEW-'+os.environ['OSR_TEST_RUN']);state['replacement']=replacement
    refuse(lambda:install(state,replacement,repair=doc.name))
    returned=insert('Stock Entry',stock_entry_type='Material Receipt',company=state['company'],items=[dict(item_code=state['finished_item'],qty=1,
        t_warehouse=state['warehouse'],serial_no=state['old']['serial'],batch_no=state['batch'],use_serial_batch_fields=1,project=state['project'],basic_rate=next(r['source_direct_usd_per_unit'] for r in state['mapping']['components'] if r['part_id']==state['part_id']))]);returned.submit()
    state['replacement_installation']=install(state,replacement,repair=doc.name,removal_stock=returned.name)['installation']
    quality(state,'Stock Entry',replacement['stock_entry'],state['finished_item'],replacement['finished_row'])
    failed=quality(state,'Stock Entry',replacement['stock_entry'],state['finished_item'],replacement['finished_row'],passed=False)
    refuse(lambda:as_user(state,'reviewer',lambda:delivery.review_handback(state['project'],state['pack_sha256'],state['asset'])))
    latest=quality(state,'Stock Entry',replacement['stock_entry'],state['finished_item'],replacement['finished_row'])
    refuse(lambda:as_user(state,'engineer',lambda:delivery.review_handback(state['project'],state['pack_sha256'],state['asset'])))
    handback=as_user(state,'reviewer',lambda:delivery.review_handback(state['project'],state['pack_sha256'],state['asset']))['handback']
    pending=quality(state,'Stock Entry',replacement['stock_entry'],state['finished_item'],replacement['finished_row'],passed=False,submit=False)
    assert delivery.lifecycle_status(state['project'],state['pack_sha256'],state['asset'])['state']=='business-handback-held'
    refuse(lambda:as_user(state,'reviewer',lambda:delivery.review_handback(state['project'],state['pack_sha256'],state['asset'])))
    latest=quality(state,'Stock Entry',replacement['stock_entry'],state['finished_item'],replacement['finished_row'])
    handback=as_user(state,'reviewer',lambda:delivery.review_handback(state['project'],state['pack_sha256'],state['asset']))['handback']
    state.update(issue=issue.name,repair=doc.name,removal=returned.name,latest_test=latest.name,late_failed_test=failed.name,
        pending_test=pending.name,handback=handback,review_task=handback['native_readback']['review_task'])
    STATE.write_text(json.dumps(state));frappe.db.commit()


def readback():
    state=json.loads(STATE.read_text());mapping=delivery.status(state['project'],state['pack_sha256'])
    lifecycle=delivery.lifecycle_status(state['project'],state['pack_sha256'],state['asset']);assert lifecycle['state']=='simulation-business-reviewed'
    handback=as_user(state,'reviewer',lambda:delivery.review_handback(state['project'],state['pack_sha256'],state['asset']))['handback']
    refs=[(r['doctype'],r['name']) for r in state['mapping']['records']]+[('File',v) for v in state['files'].values()]
    refs += [('Purchase Order',state['po']),('Purchase Receipt',state['receipt']),('Quality Inspection',state['failed_qa']),
        ('Quality Inspection',state['latest_test']),('Asset',state['asset']),('Issue',state['issue']),('Asset Repair',state['repair']),
        ('Task',state['review_task']),('Training Program',state['training_program']),('Stock Entry',state['removal'])]
    for unit in (state['old'],state['replacement']):
        refs += [('Work Order',unit['work_order']),('Stock Entry',unit['stock_entry']),('Stock Entry',unit['installation_record']),('Serial No',unit['serial'])]
        for name in (unit['stock_entry'],unit['installation_record']):
            stock=frappe.get_doc('Stock Entry',name)
            refs += [('Serial and Batch Bundle',r.serial_and_batch_bundle) for r in stock.items if r.serial_and_batch_bundle]
    records=[]
    for dt,name in sorted(set(refs)):
        doc=frappe.get_doc(dt,name)
        records.append(dict(doctype=dt,name=name,docstatus=doc.docstatus,owner=doc.owner,modified_by=doc.modified_by,
            values={k:doc.get(k) for k in ('status','repair_status','produced_qty','production_item','bom_no',
                'custom_osr_handback_required','inspected_by','custom_osr_asset_id') if doc.meta.has_field(k)}))
        if dt=='BOM':records[-1]['values']['items']=[dict(item_code=r.item_code,qty=r.qty,rate=r.rate,uom=r.uom) for r in doc.items]
    (BASE/'readback.json').write_text(json.dumps(dict(records=records,review=handback,candidate_mapping=mapping,
        candidate_lifecycle=lifecycle,binding=dict(scope='Controlled research limits with simulated readings only',**FLAGS),
        review_context=handback['native_readback']),default=str));frappe.db.commit()


def main():
    global INPUT
    INPUT=validate_input(json.loads((BASE/'input.json').read_text()))
    os.chdir('/home/frappe/frappe-bench/sites');frappe.init(site=os.environ['OSR_TEST_SITE']);frappe.connect()
    frappe.flags.mute_emails=True;frappe.set_user('Administrator')
    try:
        {'bootstrap':bootstrap,'repair':repair,'readback':readback}[sys.argv[1]]()
        print('PASS native wheel-candidate fixture '+sys.argv[1])
    finally:frappe.destroy()


if __name__=='__main__':main()
