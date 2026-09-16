"""Native lifecycle acceptance; transactional business fixtures are rolled back."""
import os,json,uuid,hashlib
from datetime import date,timedelta
import frappe
os.chdir('/home/frappe/frappe-bench/sites');frappe.init(site='osr.localhost');frappe.connect()
frappe.flags.mute_emails=True
from osr_erpnext.integration import (condition_event,execution_feedback,preview_execution,apply_execution,
    preview_repair,apply_repair,repairs_for_issue)
suffix=uuid.uuid4().hex[:8]
project=frappe.get_doc('Project','PROJ-0001');company=project.company
store=frappe.db.get_value('Warehouse',{'warehouse_name':'OSR samawah Main Stores'},'name')
group=frappe.db.get_value('Item Group',{'is_group':0},'name')
def insert(dt,**kwargs):return frappe.get_doc(dict(doctype=dt,**kwargs)).insert()
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
try:
    raw=insert('Item',item_code='OSR-LIFE-RAW-'+suffix,item_name='Lifecycle raw',item_group=group,stock_uom='Nos',is_stock_item=1,is_purchase_item=1)
    fg=insert('Item',item_code='OSR-LIFE-FG-'+suffix,item_name='Lifecycle assembly',item_group=group,stock_uom='Nos',is_stock_item=1)
    bom=insert('BOM',item=fg.name,company=company,quantity=1,currency='USD',items=[dict(item_code=raw.name,qty=2,rate=10)]);bom.submit()
    package=dict(schema='osr-execution-proposal/1',city='samawah',asset_id='SAM-ST-001:charger',engineering_revision='test-'+suffix,engineering_sha256='e'*64,
        mapping=dict(review_reference='native-test-review',items=[dict(component_type_id='charger-fixture',erp_item_code=fg.name,uom='Nos',production_bom=bom.name,conversion_rule='2 raw Nos per finished Nos',inspection_reference='test-inspection',drawing_reference='test-drawing')]))
    package['sha256']=digest(package)
    before=frappe.db.count('OSR Execution Mapping');plan=preview_execution(project.name,package)
    assert frappe.db.count('OSR Execution Mapping')==before
    mapped=apply_execution(project.name,package,plan['fingerprint'])
    assert apply_execution(project.name,package,plan['fingerprint'])==mapped
    immutable=frappe.get_doc('OSR Execution Mapping',mapped['mappings'][0]);immutable.source_package='{}'
    try: immutable.save();raise AssertionError('Revision mapping was mutable')
    except frappe.ValidationError:pass
    supplier=insert('Supplier',supplier_name='OSR lifecycle supplier '+suffix,supplier_type='Company',supplier_group='All Supplier Groups')
    order=insert('Purchase Order',supplier=supplier.name,company=company,schedule_date=(date.today()+timedelta(days=5)).isoformat(),
        items=[dict(item_code=raw.name,qty=10,rate=10,warehouse=store,project=project.name)])
    order.submit()
    receipt=insert('Purchase Receipt',supplier=supplier.name,company=company,
        items=[dict(item_code=raw.name,qty=4,rate=10,warehouse=store,project=project.name,purchase_order=order.name,purchase_order_item=order.items[0].name)])
    receipt.submit()
    feedback=execution_feedback(project.name)
    mapping_feedback=next(r for r in feedback['execution_mappings'] if r['name']==mapped['mappings'][0])
    assert mapping_feedback['component_type_id']=='charger-fixture' and mapping_feedback['erp_item_code']==fg.name
    assert mapping_feedback['production_bom']==bom.name and mapping_feedback['review_reference']=='native-test-review'
    line=next(r for r in feedback['purchase_orders'] if r['document']==order.name)
    assert line['received_qty']==4 and line['outstanding_qty']==6
    assert any(r['document']==receipt.name and r['qty']==4 for r in feedback['receipts'])
    # Complete manufacture using the existing native OSR component adapter.
    from osr_erpnext.components import preview,apply
    inputs=dict(bom=bom.name,quantity=1,source_warehouse=store,wip_warehouse=store,fg_warehouse=store,start=str(date.today())+' 09:00:00')
    previewed=preview(project.name,'manufacturing','life-'+suffix,inputs)
    work=frappe.get_doc('Work Order',apply(project.name,'manufacturing','life-'+suffix,inputs,previewed['fingerprint'])['name'])
    work.skip_transfer=1;work.save();work.submit()
    from erpnext.manufacturing.doctype.work_order.work_order import make_stock_entry
    stock=frappe.get_doc(make_stock_entry(work.name,'Manufacture',1));stock.insert();stock.submit()
    work.reload();assert work.produced_qty==1
    assert any(r['name']==work.name and r['produced_qty']==1 for r in execution_feedback(project.name)['production'])
    print('PASS reviewed item/BOM mapping, partial delivery, outstanding quantity, native manufacture and actuals',flush=True)
    fixed=frappe.db.get_value('Account',{'company':company,'is_group':0,'account_type':'Fixed Asset'},'name')
    category=insert('Asset Category',asset_category_name='OSR lifecycle assets '+suffix,
        accounts=[dict(company_name=company,fixed_asset_account=fixed)])
    assetitem=insert('Item',item_code='OSR-LIFE-ASSET-'+suffix,item_name='Lifecycle asset',item_group=group,
        stock_uom='Nos',is_stock_item=0,is_fixed_asset=1,asset_category=category.name)
    location=insert('Location',location_name='OSR lifecycle location '+suffix)
    rail_id='SAM-ST-001:charger:'+suffix
    yesterday=(date.today()-timedelta(days=1)).isoformat()
    asset=insert('Asset',company=company,item_code=assetitem.name,asset_name='Lifecycle charger '+suffix,
        asset_category=category.name,location=location.name,purchase_date=yesterday,
        available_for_use_date=yesterday,is_existing_asset=1,gross_purchase_amount=1000,
        calculate_depreciation=0,custom_osr_asset_id=rail_id)
    asset.submit()
    frappe.set_user('osr-supervision@example.invalid')
    event=dict(event_id='event-'+suffix,incident_id='incident-'+suffix,city='samawah',environment='simulation',
        company=company,project=project.name,asset_id=rail_id,erp_asset_id=asset.name,
        rule='cooling',condition='active',occurrence=1,response='Inspect cooling fan and replace the failed module')
    created=condition_event(event);assert condition_event(event)['issue']==created['issue'];assert condition_event(event)['duplicate']
    for change in [dict(environment='physical'),dict(city='mosul'),dict(project='PROJ-0002')]:
        try: condition_event({**event,**change});raise AssertionError('Cross-scope event accepted')
        except frappe.PermissionError:pass
    print('PASS event duplicate prevention and city/environment authorization',flush=True)
    frappe.set_user('Administrator')
    proposal=dict(schema='osr-condition-repair/1',key='primary',
        failure_date=str(date.today())+' 08:00:00',expected_downtime_hours=2,technician='Administrator',
        description='Replace the failed cooling module and retain configuration evidence.',
        parts=[dict(item=raw.name,warehouse=store,quantity=1)],
        evidence_references=['simulation-fault:'+event['event_id'],'removed-serial:SIM-CHARGER-001'])
    before=frappe.db.count('Asset Repair');repair_plan=preview_repair(created['issue'],proposal)
    assert frappe.db.count('Asset Repair')==before and repair_plan['availability'][0]['available_qty']>=1
    made=apply_repair(created['issue'],proposal,repair_plan['fingerprint']);assert made['created']
    repair=frappe.get_doc('Asset Repair',made['name'])
    assert repair.docstatus==0 and repair.repair_status=='Pending' and float(repair.stock_items[0].consumed_quantity)==1
    assert frappe.db.count('ToDo',{'reference_type':'Asset Repair','reference_name':repair.name,
        'allocated_to':'Administrator','status':'Open'})==1
    issue=frappe.get_doc('Issue',created['issue']);issue.status='Closed';issue.save()
    asset.reload();assert asset.status=='Out of Order' and repair.custom_osr_handback_required
    repair.actions_performed='Cooling module replaced; OSR inspection and handback still required.'
    repair.repair_status='Completed';repair.completion_date=str(date.today())+' 10:00:00';repair.save();repair.submit()
    assert frappe.db.exists('Stock Entry',{'asset_repair':repair.name,'docstatus':1})
    repeated=apply_repair(created['issue'],proposal,repair_plan['fingerprint'])
    assert repeated['name']==repair.name and not repeated['created'] and not repeated['automatic_handback']
    assert repairs_for_issue(created['issue'])[0].name==repair.name
    repair_feedback=next(r for r in execution_feedback(project.name)['repairs'] if r['name']==repair.name)
    assert repair_feedback['status']=='Completed' and repair_feedback['parts'][0]['consumed_qty']==1
    assert repair_feedback['railway_handback']=='required-in-osr' and not repair_feedback['railway_handback_authorised']
    assert 'removed-serial:SIM-CHARGER-001' in repair_feedback['configuration_evidence']['references']
    print('PASS reviewed condition repair, part consumption, assignment, evidence and independent handback',flush=True)
finally:
    frappe.set_user('Administrator');frappe.db.rollback();frappe.destroy()
