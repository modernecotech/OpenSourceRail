"""Native lifecycle acceptance; transactional business fixtures are rolled back."""
import os,json,uuid,hashlib
from datetime import date,timedelta
import frappe
os.chdir('/home/frappe/frappe-bench/sites');frappe.init(site='osr.localhost');frappe.connect()
frappe.flags.mute_emails=True
from osr_erpnext.integration import condition_event,execution_feedback,preview_execution,apply_execution
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
    frappe.set_user('osr-supervision@example.invalid')
    event=dict(event_id='event-'+suffix,incident_id='incident-'+suffix,city='samawah',environment='simulation',company=company,project=project.name,asset_id='SAM-ST-001:charger',rule='cooling',condition='active',occurrence=1)
    created=condition_event(event);assert condition_event(event)['issue']==created['issue'];assert condition_event(event)['duplicate']
    for change in [dict(environment='physical'),dict(city='mosul'),dict(project='PROJ-0002')]:
        try: condition_event({**event,**change});raise AssertionError('Cross-scope event accepted')
        except frappe.PermissionError:pass
    print('PASS event duplicate prevention and city/environment authorization',flush=True)
finally:
    frappe.set_user('Administrator');frappe.db.rollback();frappe.destroy()
