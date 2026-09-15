"""Local evaluation check: eight native adapters, all fixtures rolled back."""
import os,json,uuid
from datetime import date,timedelta
import frappe
os.chdir('/home/frappe/frappe-bench/sites');frappe.init(site='osr.localhost');frappe.connect()
frappe.flags.mute_emails=True
from osr_erpnext.components import preview,apply,feedback
suffix=uuid.uuid4().hex[:8]
project=frappe.get_doc('Project','PROJ-0001')
company=project.company
store=frappe.db.get_value('Warehouse',{'warehouse_name':'OSR samawah Main Stores'},'name')
wip=frappe.db.get_value('Warehouse',{'warehouse_name':'OSR samawah Workshop Spares'},'name')
fg=frappe.db.get_value('Warehouse',{'warehouse_name':'OSR samawah Receiving Inspection'},'name')
other=frappe.db.get_value('Warehouse',{'warehouse_name':'OSR mosul Main Stores'},'name')
group=frappe.db.get_value('Item Group',{'is_group':0},'name')
results={}
def insert(dt,**kwargs):return frappe.get_doc(dict(doctype=dt,**kwargs)).insert()
def run(kind,inputs):
    key='check-'+suffix
    before=frappe.db.count('Item Reorder' if kind=='replenishment' else __import__('osr_erpnext.component_catalogue',fromlist=['CATALOGUE']).CATALOGUE[kind]['doctype'])
    p=preview(project.name,kind,key,inputs)
    dt=p['document']['doctype']
    assert frappe.db.count(dt)==before, 'Preview wrote records'
    r=apply(project.name,kind,key,inputs,p['fingerprint'])
    assert r['created']
    assert apply(project.name,kind,key,inputs,p['fingerprint'])['created'] is False
    results[kind]=r['doctype']
    print('PASS',kind,flush=True)
    return frappe.get_doc(r['doctype'],r['name'])
try:
    member=insert('User',email='osr-components-'+suffix+'@example.invalid',first_name='Component fixture',
        enabled=1,send_welcome_email=0,user_type='System User',roles=[dict(role='System Manager')])
    frappe.share.add('Project',project.name,member.name,read=1,notify=0)
    raw=insert('Item',item_code='OSR-COMP-RAW-'+suffix,item_name='Component test raw',item_group=group,
        stock_uom='Nos',is_stock_item=1,is_purchase_item=1,inspection_required_before_purchase=1)
    product=insert('Item',item_code='OSR-COMP-FG-'+suffix,item_name='Component test output',item_group=group,stock_uom='Nos',is_stock_item=1)
    item=run('replenishment',dict(item=raw.name,warehouse=store,level=2,quantity=5))
    assert len(item.reorder_levels)==1
    try:
        preview(project.name,'replenishment','wrong-city',dict(item=raw.name,warehouse=other,level=2,quantity=5))
        raise AssertionError('Cross-city warehouse accepted')
    except frappe.ValidationError:pass
    bom=insert('BOM',item=product.name,company=company,quantity=1,currency='USD',items=[dict(item_code=raw.name,qty=1,rate=10)])
    bom.submit()
    work=run('manufacturing',dict(bom=bom.name,quantity=2,source_warehouse=store,wip_warehouse=wip,fg_warehouse=fg,start='2030-01-02 09:00:00'))
    assert work.docstatus==0 and work.required_items[0].required_qty==2
    supplier=insert('Supplier',supplier_name='OSR component supplier '+suffix,supplier_type='Company',supplier_group='All Supplier Groups')
    receipt=insert('Purchase Receipt',supplier=supplier.name,company=company,project=project.name,
        items=[dict(item_code=raw.name,qty=1,rate=10,warehouse=store,project=project.name)])
    parameter=insert('Quality Inspection Parameter',parameter='OSR fixture inspection '+suffix)
    template=insert('Quality Inspection Template',quality_inspection_template_name='OSR inspection '+suffix,
        item_quality_inspection_parameter=[dict(specification=parameter.name,numeric=0,value='Pass')])
    quality=run('quality',dict(reference_type='Purchase Receipt',reference=receipt.name,line=receipt.items[0].name,
        template=template.name,sample_size=1,inspector='Administrator',report_date=date.today().isoformat()))
    assert quality.docstatus==0 and quality.readings
    fixed=frappe.db.get_value('Account',{'company':company,'is_group':0,'account_type':'Fixed Asset'},'name')
    category=insert('Asset Category',asset_category_name='OSR component assets '+suffix,accounts=[dict(company_name=company,fixed_asset_account=fixed)])
    assetitem=insert('Item',item_code='OSR-COMP-ASSET-'+suffix,item_name='Component asset',item_group=group,stock_uom='Nos',
        is_stock_item=0,is_fixed_asset=1,asset_category=category.name)
    location=insert('Location',location_name='OSR component location '+suffix)
    rail_id=frappe.get_list('Task',filters={'project':project.name,'custom_osr_kind':'maintenance'},fields=['custom_osr_asset_id'],limit_page_length=1)[0].custom_osr_asset_id
    yesterday=(date.today()-timedelta(days=1)).isoformat()
    asset=insert('Asset',company=company,item_code=assetitem.name,asset_name='OSR component asset '+suffix,
        asset_category=category.name,location=location.name,purchase_date=yesterday,available_for_use_date=yesterday,
        is_existing_asset=1,gross_purchase_amount=1000,calculate_depreciation=0,custom_osr_asset_id=rail_id)
    asset.submit()
    team=insert('Asset Maintenance Team',maintenance_team_name='OSR component team '+suffix,company=company,
        maintenance_manager=member.name,maintenance_team_members=[dict(team_member=member.name,maintenance_role='System Manager')])
    service=run('maintenance',dict(asset=asset.name,team=team.name,assignee=member.name,title='Fixture monthly inspection',
        periodicity='Monthly',start=date.today().isoformat(),description='Fixture service instruction'))
    assert frappe.db.count('Asset Maintenance Log',{'asset_maintenance':service.name})==1
    assert frappe.db.count('ToDo',{'reference_type':'Asset Maintenance','reference_name':service.name})>=1
    original_status=asset.status
    asset.db_set('status','Sold')
    try:
        preview(project.name,'maintenance','disposed-asset',dict(asset=asset.name,team=team.name,assignee=member.name,
            title='Invalid servicing',periodicity='Monthly',start=date.today().isoformat(),description='Test'))
        raise AssertionError('Disposed asset accepted')
    except frappe.ValidationError:pass
    asset.db_set('status',original_status)
    training=run('training',dict(title='City induction fixture',description='Systems and business records'))
    assert training.company==company
    training.description='Operator revision';training.save()
    original=dict(title='City induction fixture',description='Systems and business records')
    again=preview(project.name,'training','check-'+suffix,original)
    apply(project.name,'training','check-'+suffix,original,again['fingerprint'])
    assert frappe.get_doc('Training Program',training.name).description=='Operator revision'
    changed=dict(original,title='Different programme')
    conflict=preview(project.name,'training','check-'+suffix,changed)
    try:
        apply(project.name,'training','check-'+suffix,changed,conflict['fingerprint'])
        raise AssertionError('Changed instance accepted')
    except frappe.ValidationError:pass
    try:
        apply(project.name,'training','bad-fingerprint',original,'not-the-preview')
        raise AssertionError('Invalid preview accepted')
    except frappe.ValidationError:pass
    year=frappe.db.get_value('Fiscal Year',{'disabled':0},'name')
    expense=frappe.db.get_value('Account',{'company':company,'root_type':'Expense','is_group':0},'name')
    budget=run('budget',dict(fiscal_year=year,action='Stop',accounts=[dict(account=expense,amount=100)]))
    assert budget.docstatus==0 and budget.applicable_on_material_request
    issue=run('service',dict(subject='Fixture facility issue',description='Test request',priority='Low'))
    assert issue.status=='Open' and issue.project==project.name
    rule=run('assignment',dict(category='maintenance',strategy='Round Robin',users=[dict(user='Administrator')]))
    assert rule.disabled and project.name in rule.assign_condition
    states=feedback(project.name)
    assert all(states[k]['records']>=1 for k in results)
    frappe.set_user('Guest')
    try:
        preview(project.name,'training','guest',original)
        raise AssertionError('Guest accepted')
    except frappe.PermissionError:pass
    frappe.set_user('Administrator')
    print(json.dumps(dict(components=results,preview_no_writes=True,repeated_apply_preserved=True,city_boundary=True,feedback=True,fixtures_rolled_back=True)),flush=True)
finally:
    frappe.db.rollback();frappe.destroy()
