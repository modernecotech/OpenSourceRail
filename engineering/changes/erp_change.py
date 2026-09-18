"""Real ERPNext change rehearsal in an isolated simulation project.

INPUT contains verified quantities and hashes, never passwords. New records are
committed together; a failure rolls this run back. Software reviewer identities
exercise separation of duties and do not represent engineering acceptance.
"""
import os,json,hashlib
from datetime import date,timedelta
import frappe
os.chdir('/home/frappe/frappe-bench/sites');frappe.init(site=INPUT['site']);frappe.connect();frappe.flags.mute_emails=True

def insert(dt,**values):return frappe.get_doc(dict(doctype=dt,**values)).insert()
def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
checks=[]
def check(name,condition):
    checks.append(dict(name=name,passed=bool(condition)))
    if not condition:raise AssertionError(name)

try:
    from osr_erpnext.integration import preview_execution,apply_execution,execution_feedback
    from osr_erpnext import disposition,disposition_execution as outcome
    from erpnext.manufacturing.doctype.work_order.work_order import make_stock_entry,stop_unstop
    reference=frappe.get_doc('Project',INPUT['reference_project'])
    assert reference.custom_osr_city==INPUT['city']
    company=reference.company;key=INPUT['run'];title='OSR simulation CAD change '+key
    if frappe.db.exists('Project',{'project_name':title}):raise ValueError('Run already exists; inspect retained results')
    project=insert('Project',project_name=title,company=company,custom_osr_city=INPUT['city'])
    warehouse=insert('Warehouse',warehouse_name='CAD simulation '+key,company=company).name
    group=frappe.db.get_value('Item Group',{'is_group':0},'name')
    assert frappe.db.exists('UOM','Kg')
    raw=insert('Item',item_code='CAD-RAW-'+key,item_name='Simulation gross steel equivalent',item_group=group,stock_uom='Kg',is_stock_item=1,is_purchase_item=1,valuation_rate=1)
    member=insert('Item',item_code='CAD-MEMBER-'+key,item_name='Screening cross bearer '+INPUT['component'],item_group=group,stock_uom='Nos',is_stock_item=1)
    kit=insert('Item',item_code='CAD-KIT-'+key,item_name='Screening underframe kit '+INPUT['component'],item_group=group,stock_uom='Nos',is_stock_item=1)
    boms={};maps={};orders={}
    def revision(name):
        q=INPUT['quantities'][name]
        child=insert('BOM',item=member.name,company=company,quantity=1,currency='USD',items=[dict(item_code=raw.name,qty=q['member_purchase_kg'],rate=1)]);child.submit()
        parent=insert('BOM',item=kit.name,company=company,quantity=1,currency='USD',items=[dict(item_code=member.name,qty=1,bom_no=child.name),dict(item_code=raw.name,qty=q['other_purchase_kg'],rate=1)]);parent.submit()
        boms[name]=dict(member=child.name,kit=parent.name,member_kg=child.items[0].qty,total_kg=q['member_purchase_kg']+q['other_purchase_kg'])
        package=dict(schema='osr-execution-proposal/1',city=INPUT['city'],asset_id=INPUT['asset_id'],
            engineering_revision=key+'-'+name,engineering_sha256=INPUT['manifest_sha256'],
            mapping=dict(review_reference='software-scenario:'+key,items=[dict(component_type_id=INPUT['component']+'-screen-'+key,
                erp_item_code=kit.name,uom='Nos',production_bom=parent.name,
                conversion_rule='Native solid volumes x assumed density x '+str(1+INPUT['purchase_allowance'])+' purchase allowance; one changed member plus unchanged kit solids. Simulation only.',
                inspection_reference='screening-not-accepted:'+key,drawing_reference=INPUT['cad_sha256'][name])]))
        package['sha256']=digest(package);preview=preview_execution(project.name,package)
        maps[name]=apply_execution(project.name,package,preview['fingerprint'])['mappings'][0]
        order=insert('Work Order',company=company,project=project.name,production_item=kit.name,bom_no=parent.name,
            qty=2 if name=='baseline' else 1,use_multi_level_bom=1,source_warehouse=warehouse,
            wip_warehouse=warehouse,fg_warehouse=warehouse,planned_start_date=str(date.today())+' 09:00:00',skip_transfer=1)
        for row in order.required_items:row.source_warehouse=warehouse
        order.save();order.submit();orders[name]=order
        check(name+' exploded material follows measured CAD quantity',len(order.required_items)==1 and order.required_items[0].item_code==raw.name and abs(order.required_items[0].required_qty-order.qty*boms[name]['total_kg'])<1e-5)
    revision('baseline');revision('candidate')
    check('Revised BOM changes purchased member quantity',abs(boms['candidate']['member_kg']-boms['baseline']['member_kg'])>1e-6)
    original=orders['baseline'];original_qty=original.required_items[0].required_qty
    feedback=execution_feedback(project.name)
    exposure=next(r for r in feedback['revision_reviews'] if r['mapping']['name']==maps['baseline'])
    check('Nested dependencies expose old parent production',len(exposure['bom_dependencies'])==2 and any(r['name']==original.name for r in exposure['work_orders']))
    request=dict(key='cad-stop-'+key,mapping=maps['baseline'],target=dict(kind='work-order',document=original.name),action='Request production stop',responsible='Administrator',due_date=str(date.today()+timedelta(days=7)),rationale='Native CAD depth and dependent material/solver results changed. Hold old simulation production for review.',references=['bundle:'+INPUT['manifest_sha256'],'cad:'+INPUT['cad_sha256']['candidate']])
    plan=disposition.preview(project.name,request);saved=disposition.record(project.name,request,plan['fingerprint'])
    roles=['Projects Manager','Manufacturing Manager','Manufacturing User','Purchase Manager','Stock Manager','Stock User','Quality Manager']
    reviewer=insert('User',email='cad-review-'+key+'@example.invalid',first_name='Software scenario reviewer',send_welcome_email=0,roles=[dict(role=r) for r in roles])
    frappe.share.add('Project',project.name,reviewer.name,read=1,write=1,notify=0)
    decision=dict(outcome='Endorse plan',rationale='Software role-separation check only; no independent engineering approval.',references=['simulation:'+key])
    try:disposition.preview_decision(saved['name'],decision)
    except frappe.ValidationError:check('Self endorsement rejected',True)
    else:raise AssertionError('Self endorsement accepted')
    frappe.set_user(reviewer.name);review=disposition.preview_decision(saved['name'],decision);disposition.record_decision(saved['name'],decision,review['fingerprint'])
    verify=dict(key='cad-stop-check-'+key,rationale='Observed actual stopped native work order.',references=['simulation:'+key])
    try:outcome.preview(saved['name'],verify)
    except frappe.ValidationError:check('Unperformed production stop rejected',True)
    else:raise AssertionError('Unperformed stop accepted')
    frappe.set_user('Administrator');stop_unstop(original.name,'Stopped');original.reload()
    frappe.set_user(reviewer.name);observed=outcome.preview(saved['name'],verify);verified=outcome.record(saved['name'],verify,observed['fingerprint'])
    check('Old production stopped and separately verified',observed['observation']['native']['status']=='Stopped')
    frappe.set_user('Administrator');original.reload()
    check('Original BOM and quantities remain unchanged',original.bom_no==boms['baseline']['kit'] and original.required_items[0].required_qty==original_qty)
    receipt=insert('Stock Entry',stock_entry_type='Material Receipt',company=company,project=project.name,set_posting_time=1,posting_date=str(date.today()-timedelta(days=1)),posting_time='12:00:00',items=[dict(item_code=raw.name,qty=2*boms['candidate']['total_kg'],t_warehouse=warehouse,basic_rate=1)]);receipt.submit()
    new=orders['candidate'];stock=frappe.get_doc(make_stock_entry(new.name,'Manufacture',1));stock.insert();stock.submit();new.reload();stock.reload()
    consumed=sum(row.transfer_qty for row in stock.items if row.item_code==raw.name and row.s_warehouse)
    material_rows=[row for row in stock.items if row.item_code==raw.name and row.s_warehouse]
    rounding_tolerance=sum(.5*10**-min(row.precision('qty'),row.precision('transfer_qty')) for row in material_rows)
    check('Candidate native production consumes revised material',new.produced_qty==1 and all(row.s_warehouse==warehouse for row in material_rows) and abs(consumed-boms['candidate']['total_kg'])<=rounding_tolerance+1e-9)
    check('Candidate production retains exact revised BOM',new.bom_no==boms['candidate']['kit'])
    check('Old mapping remains immutable',frappe.get_doc('OSR Execution Mapping',maps['baseline']).engineering_revision==key+'-baseline')
    result=dict(schema='osr-engineering-change-erp/1',passed=True,checks=checks,project=project.name,company=company,warehouse=warehouse,
        city=INPUT['city'],run=key,manifest_sha256=INPUT['manifest_sha256'],boms=boms,mappings=maps,
        work_orders={name:doc.name for name,doc in orders.items()},disposition=saved['name'],verification=verified['name'],
        stock_entry=stock.name,receipt=receipt.name,consumed_kg=consumed,quantity_rounding_tolerance_kg=rounding_tolerance,quantity_difference_kg=consumed-boms['candidate']['total_kg'],reviewer_kind='software-test-identity',physical_release=False,engineering_acceptance=False)
    frappe.db.commit();print('OSR_CHANGE_RESULT:'+json.dumps(result),flush=True)
except BaseException:frappe.db.rollback();raise
finally:frappe.destroy()
