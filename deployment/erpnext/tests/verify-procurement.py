import os,json,uuid
from datetime import date,timedelta
import frappe
os.chdir('/home/frappe/frappe-bench/sites');frappe.init(site='osr.localhost');frappe.connect()
from osr_erpnext.procurement import candidates,create_material_request
from osr_erpnext.city_runtime import city_status
try:
    task=frappe.get_list('Task',filters={'custom_osr_city':'samawah','custom_osr_kind':'procurement'},fields=['name','project'],limit_page_length=1)[0]
    found=candidates(task.name)
    assert len(found['requirements'])<=50 and found['total']>0
    requirement=found['requirements'][0]['purchase_order_id']
    assert candidates(task.name,search=requirement)['requirements'][0]['purchase_order_id']==requirement
    project=frappe.get_doc('Project',task.project)
    warehouse=frappe.db.get_value('Warehouse',{'warehouse_name':'OSR samawah Main Stores'},'name')
    other=frappe.db.get_value('Warehouse',{'warehouse_name':'OSR mosul Main Stores'},'name')
    item=frappe.get_doc(dict(doctype='Item',item_code='OSR-AUTOMATION-CHECK-'+uuid.uuid4().hex[:10],
        item_name='Temporary automation validation item',item_group=frappe.db.get_value('Item Group',{'is_group':0},'name'),
        stock_uom='Nos',is_stock_item=0,is_purchase_item=1)).insert()
    args=dict(task=task.name,requirement_id=requirement,item_code=item.name,quantity=1,
              schedule_date=(date.today()+timedelta(days=30)).isoformat(),warehouse=warehouse)
    before=city_status(project.name)['business_documents']['Material Request']['draft']
    first=create_material_request(**args)
    assert first['created'] and first['docstatus']==0
    mr=frappe.get_doc('Material Request',first['name'])
    assert mr.items[0].project==project.name and mr.items[0].cost_center==project.cost_center
    assert city_status(project.name)['business_documents']['Material Request']['draft']==before+1
    mr.items[0].qty=3;mr.save()
    assert create_material_request(**args)['created'] is False
    assert frappe.get_doc('Material Request',mr.name).items[0].qty==3
    try:
        create_material_request(**dict(args,quantity=2))
        raise AssertionError('Changed input accepted')
    except frappe.ValidationError:
        pass
    second=found['requirements'][1]['purchase_order_id']
    try:
        create_material_request(**dict(args,requirement_id=second,warehouse=other))
        raise AssertionError('Wrong-city warehouse accepted')
    except frappe.ValidationError:
        pass
    frappe.set_user('Guest')
    try:
        candidates(task.name)
        raise AssertionError('Guest read accepted')
    except frappe.PermissionError:
        pass
    frappe.set_user('Administrator')
    readiness=city_status(project.name)['readiness']
    assert readiness['undated']>0 and readiness['overdue']==0
    print(json.dumps(dict(native_draft=True,line_project_feedback=True,repeat_preserves_edits=True,
                         changed_inputs_rejected=True,wrong_city_rejected=True,guest_denied=True,
                         readiness=readiness,fixture_rolled_back=True)))
finally:
    frappe.db.rollback();frappe.destroy()
