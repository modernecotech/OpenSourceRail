"""Native ERP variable matrix and payment lifecycle; every mutation rolls back."""
import os,json,uuid
from datetime import date,timedelta
import frappe
os.chdir('/home/frappe/frappe-bench/sites');frappe.init(site=INPUT['site']);frappe.connect()
frappe.flags.mute_emails=True
from osr_erpnext.components import preview,apply,feedback
from osr_erpnext.component_catalogue import CATALOGUE
source=INPUT['source'];project=source['project'];company=source['company'];key=uuid.uuid4().hex[:10]
checks=[]
def check(identity,condition,**observed):
    checks.append(dict(id=identity,name=identity,passed=bool(condition),before=None,after=observed,level='native-erp-rollback'))
    if not condition:raise AssertionError(identity)
def insert(dt,**values):return frappe.get_doc(dict(doctype=dt,**values)).insert()
def component(kind,values,variant):
    identity='matrix-'+key+'-'+variant
    plan=preview(project,kind,identity,values)
    result=apply(project,kind,identity,values,plan['fingerprint'])
    assert apply(project,kind,identity,values,plan['fingerprint'])['created'] is False
    return frappe.get_doc(result['doctype'],result['name'])
try:
    for amount in [1,2,5]:
        doc=component('manufacturing',dict(bom=source['bom'],quantity=amount,source_warehouse=source['warehouse'],wip_warehouse=source['warehouse'],fg_warehouse=source['warehouse'],start='2026-11-04 09:00:00'),'production-'+str(amount))
        check('erp.manufacturing.quantity.'+str(amount),doc.qty==amount and doc.required_items[0].required_qty==2*amount,quantity=doc.qty,raw_required=doc.required_items[0].required_qty,docstatus=doc.docstatus)
    group=frappe.db.get_value('Item Group',{'is_group':0},'name')
    for level,quantity in [(0,1),(2,5),(10,20)]:
        item=insert('Item',item_code='MATRIX-'+key+'-'+str(level),item_group=group,stock_uom='Nos',is_stock_item=1,is_purchase_item=1)
        doc=component('replenishment',dict(item=item.name,warehouse=source['warehouse'],level=level,quantity=quantity),'reorder-'+str(level))
        row=doc.reorder_levels[0]
        check('erp.replenishment.'+str(level),row.warehouse_reorder_level==level and row.warehouse_reorder_qty==quantity,level=row.warehouse_reorder_level,quantity=row.warehouse_reorder_qty)
    for strategy in CATALOGUE['assignment']['fields'][1]['options'].split('\n'):
        for category in CATALOGUE['assignment']['fields'][0]['options'].split('\n'):
            doc=component('assignment',dict(strategy=strategy,category=category,users=[dict(user='Administrator')]),'allocation-'+str(len(checks)))
            check('erp.assignment.'+strategy+'.'+category,doc.disabled==1 and doc.rule==strategy and repr(category) in doc.assign_condition,strategy=doc.rule,category=category,disabled=doc.disabled)
    for priority in ['Low','Medium','High']:
        doc=component('service',dict(subject='Matrix '+key+' '+priority,description='<b>Inspection</b>',priority=priority),'issue-'+priority.lower())
        check('erp.service.priority.'+priority,doc.priority==priority and doc.status=='Open' and '&lt;b&gt;' in doc.description,priority=doc.priority,status=doc.status,escaped_description=doc.description)
    for i,title in enumerate(['Operator induction','Maintainer refresher']):
        doc=component('training',dict(title=title,description='Objectives '+str(i)),'training-'+str(i))
        check('erp.training.'+str(i),title in doc.training_program and doc.description=='Objectives '+str(i),title=doc.training_program,status=doc.status)
    member=insert('User',email='matrix-'+key+'@example.invalid',first_name='Matrix fixture',enabled=1,send_welcome_email=0,user_type='System User',roles=[dict(role='System Manager')])
    frappe.share.add('Project',project,member.name,read=1,notify=0)
    asset=frappe.copy_doc(frappe.get_doc('Asset',source['asset']));asset.asset_name='Matrix '+key
    asset.custom_osr_asset_id=frappe.get_list('Task',filters={'project':project,'custom_osr_kind':'maintenance'},fields=['custom_osr_asset_id'],limit_page_length=1)[0].custom_osr_asset_id
    asset.insert();asset.submit()
    team=insert('Asset Maintenance Team',maintenance_team_name='Matrix '+key,company=company,maintenance_manager=member.name,maintenance_team_members=[dict(team_member=member.name,maintenance_role='System Manager')])
    periods=next(f['options'].split('\n') for f in CATALOGUE['maintenance']['fields'] if f['fieldname']=='periodicity')
    for i,period in enumerate(periods):
        # One schedule per asset: use a savepoint so each interval starts from the same asset.
        frappe.db.savepoint('maintenance_variant')
        doc=component('maintenance',dict(asset=asset.name,team=team.name,assignee=member.name,title='Matrix interval '+period,periodicity=period,start='2026-10-05',description='Fixture interval'),'interval-'+str(i))
        row=doc.asset_maintenance_tasks[0]
        expected=['2026-10-06','2026-10-12','2026-11-05','2027-01-05','2027-04-05','2027-10-05','2028-10-05','2029-10-05'][i]
        check('erp.maintenance.'+period,str(row.next_due_date)==expected and frappe.db.count('Asset Maintenance Log',{'asset_maintenance':doc.name})==1,periodicity=period,next_due=str(row.next_due_date),expected=expected)
        frappe.db.rollback(save_point='maintenance_variant')
    raw=frappe.get_doc('Item',source['raw']);raw.inspection_required_before_purchase=1;raw.save()
    parameter=insert('Quality Inspection Parameter',parameter='Matrix temperature '+key)
    template=insert('Quality Inspection Template',quality_inspection_template_name='Matrix '+key,item_quality_inspection_parameter=[dict(specification=parameter.name,numeric=1,min_value=30,max_value=45)])
    for kind,reference in [('Purchase Receipt',source['receipt']),('Purchase Invoice',source['invoice'])]:
        line=frappe.get_doc(kind,reference).items[0]
        for sample_size,reading in [(1,35),(2,99)]:
            doc=component('quality',dict(reference_type=kind,reference=reference,line=line.name,template=template.name,sample_size=sample_size,inspector='Administrator',report_date=date.today().isoformat()),'inspection-'+str(len(checks)))
            doc.readings[0].reading_1=str(reading);doc.save();doc.submit()
            expected='Accepted' if reading==35 else 'Rejected'
            check('erp.quality.'+kind+'.'+str(reading),doc.status==expected and doc.docstatus==1 and doc.sample_size==sample_size,reference=kind,reading=reading,sample_size=sample_size,status=doc.status)
    from erpnext.accounts.utils import get_fiscal_year
    year=get_fiscal_year(date.today(),company=company)[0]
    expense=frappe.db.get_value('Account',{'company':company,'root_type':'Expense','is_group':0},'name')
    for action,amount in [('Stop',100),('Warn',200)]:
        frappe.db.savepoint('budget_variant')
        doc=component('budget',dict(fiscal_year=year,action=action,accounts=[dict(account=expense,amount=amount)]),'budget-'+action.lower());doc.submit()
        check('erp.budget.'+action,doc.docstatus==1 and doc.action_if_annual_budget_exceeded==action and doc.accounts[0].budget_amount==amount,action=action,amount=amount,submitted=True)
        frappe.db.rollback(save_point='budget_variant')
    # Native partial payment, settlement and cancellation against the retained example invoice.
    from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry
    invoice=frappe.get_doc('Purchase Invoice',source['invoice']);original=invoice.outstanding_amount
    assert original==60, 'Expected untouched example invoice'
    bank=frappe.db.get_value('Account',{'company':company,'account_type':'Cash','is_group':0},'name')
    payments=[]
    for amount,remaining in [(20,40),(40,0)]:
        payment=get_payment_entry('Purchase Invoice',invoice.name,bank_account=bank,bank_amount=amount)
        payment.paid_amount=amount;payment.received_amount=amount
        for ref in payment.references:ref.allocated_amount=amount
        payment.reference_no='matrix-'+key;payment.reference_date=date.today();payment.insert();payment.submit();payments.append(payment)
        invoice.reload()
        ledger=frappe.get_all('GL Entry',filters={'voucher_type':'Payment Entry','voucher_no':payment.name,'is_cancelled':0},fields=['debit','credit'])
        check('erp.payment.remaining.'+str(remaining),invoice.outstanding_amount==remaining and len(ledger)>=2 and abs(sum(r.debit-r.credit for r in ledger))<0.000001,paid=amount,outstanding=invoice.outstanding_amount,ledger_rows=len(ledger),balanced=True)
    for payment,remaining in zip(reversed(payments),[40,60]):
        payment.cancel();invoice.reload()
        check('erp.payment.cancel.'+str(remaining),invoice.outstanding_amount==remaining,outstanding=invoice.outstanding_amount,cancelled_payment=payment.name)
    result=dict(passed=True,checks=checks,fixtures_rolled_back=True)
except BaseException as error:
    result=dict(passed=False,checks=checks,error=str(error),fixtures_rolled_back=True)
    raise
finally:
    frappe.db.rollback();frappe.destroy()
    print('OSR_EXPANSION:'+json.dumps(result,default=str),flush=True)
