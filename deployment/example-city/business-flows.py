"""Downstream native business workflows in a rolled-back evaluation transaction."""
import os,json,uuid
from datetime import date,timedelta
import frappe
os.chdir('/home/frappe/frappe-bench/sites');frappe.init(site=INPUT['site']);frappe.connect();frappe.flags.mute_emails=True
source=INPUT['source'];project=source['project'];company=source['company'];key=uuid.uuid4().hex[:10];checks=[]
from osr_erpnext.components import preview,apply

def check(identity,condition,**after):
    checks.append(dict(id=identity,name=identity,passed=bool(condition),after=after,level='native-erp-rollback'))
    if not condition:raise AssertionError(identity)
    print('PASS '+identity,flush=True)
def insert(dt,**values):return frappe.get_doc(dict(doctype=dt,**values)).insert()
def component(kind,values,variant):
    identity='flows-'+key+'-'+variant;p=preview(project,kind,identity,values);r=apply(project,kind,identity,values,p['fingerprint']);return frappe.get_doc(r['doctype'],r['name'])
result=dict(passed=False,checks=checks,fixtures_rolled_back=True)
try:
    from erpnext.accounts.utils import get_fiscal_year
    year=get_fiscal_year(date.today(),company=company)[0]
    group=frappe.db.get_value('Item Group',{'is_group':0},'name')
    expense=frappe.db.get_value('Account',{'company':company,'root_type':'Expense','is_group':0,'account_type':'Expense Account'},'name') or frappe.db.get_value('Account',{'company':company,'root_type':'Expense','is_group':0},'name')
    center=frappe.db.get_value('Company',company,'cost_center')
    service=insert('Item',item_code='FLOWS-SERVICE-'+key,item_group=group,stock_uom='Nos',is_stock_item=0,is_purchase_item=1)
    for action in ['Stop','Warn']:
        frappe.db.savepoint('budget_flow')
        budget=component('budget',dict(fiscal_year=year,action=action,accounts=[dict(account=expense,amount=100)]),'budget-'+action.lower());budget.submit()
        for amount,total in [(50,50),(50,100),(1,101)]:
            frappe.db.savepoint('budget_invoice')
            invoice=frappe.get_doc(dict(doctype='Purchase Invoice',company=company,supplier=source['supplier'],project=project,items=[dict(item_code=service.name,qty=1,rate=amount,expense_account=expense,cost_center=center,project=project)]))
            blocked=False
            try:invoice.insert();invoice.submit()
            except frappe.ValidationError as error:
                if 'budget' not in str(error).lower():raise
                blocked=True;frappe.db.rollback(save_point='budget_invoice')
            check('business.budget.'+action+'.'+str(total),blocked==(action=='Stop' and total>100),budget=100,attempted_total=total,blocked=blocked)
        frappe.db.rollback(save_point='budget_flow');frappe.clear_cache()
    # Actual enabled native assignment, including changes in strategy and work category.
    users=[]
    for i in range(2):
        email='flows-'+key+'-'+str(i)+'@example.invalid'
        insert('User',email=email,first_name='Assignment fixture',enabled=1,send_welcome_email=0,user_type='System User',roles=[dict(role='Projects Manager')]);frappe.share.add('Project',project,email,read=1,write=1,notify=0);users.append(email)
    from frappe.automation.doctype.assignment_rule.assignment_rule import apply as assign
    for strategy in ['Round Robin','Load Balancing']:
        frappe.db.savepoint('assignment_flow')
        rule=component('assignment',dict(category='maintenance',strategy=strategy,users=[dict(user=u) for u in users]),'assignment-'+str(len(checks)))
        rule.disabled=0;rule.assignment_days=[]
        for day in ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']:rule.append('assignment_days',dict(day=day))
        rule.save();frappe.clear_cache()
        observed=[]
        for i in range(2):
            task=insert('Task',subject='Assignment flow '+key+' '+str(i),project=project,custom_osr_kind='maintenance',exp_end_date=str(date.today()+timedelta(days=2)))
            assign(task)
            targets=frappe.get_all('ToDo',filters={'reference_type':'Task','reference_name':task.name,'status':'Open'},pluck='allocated_to')
            check('business.assignment.'+strategy+'.'+str(i),len(targets)==1 and targets[0] in users,assigned=targets)
            observed+=targets
        check('business.assignment.distribution.'+strategy,set(observed)==set(users),users=observed)
        frappe.db.rollback(save_point='assignment_flow');frappe.clear_cache()
    # Native reorder scheduler with stock just above, at and below the threshold.
    from erpnext.stock.reorder_item import reorder_item
    frappe.db.set_single_value('Stock Settings','auto_indent',1)
    for quantity in [3,2,1]:
        frappe.db.savepoint('reorder_flow')
        item=insert('Item',item_code='FLOWS-REORDER-'+key+'-'+str(quantity),item_group=group,stock_uom='Nos',is_stock_item=1,is_purchase_item=1)
        component('replenishment',dict(item=item.name,warehouse=source['warehouse'],level=2,quantity=5),'reorder-'+str(quantity))
        stock=insert('Stock Entry',stock_entry_type='Material Receipt',company=company,items=[dict(item_code=item.name,qty=quantity,t_warehouse=source['warehouse'],basic_rate=10,expense_account=expense,cost_center=center)]);stock.submit()
        reorder_item()
        requests=frappe.get_all('Material Request Item',filters={'item_code':item.name},fields=['parent','warehouse','project','qty'])
        check('business.replenishment.threshold.'+str(quantity),len(requests)==(0 if quantity>2 else 1),stock=quantity,threshold=2,requests=requests)
        if requests:check('business.replenishment.quantity.'+str(quantity),requests[0].qty==5 and requests[0].warehouse==source['warehouse'] and requests[0].project==project,quantity=requests[0].qty,warehouse=requests[0].warehouse,project=requests[0].project)
        if quantity==1:
            from osr_erpnext.replenishment import assign_city_scope
            def request(explicit=None):return frappe.get_doc(dict(doctype='Material Request',material_request_type='Purchase',company=company,items=[dict(item_code=item.name,warehouse=source['warehouse'],project=explicit)]))
            explicit=request(project);assign_city_scope(explicit)
            check('business.replenishment.explicit-project',explicit.items[0].project==project)
            frappe.db.savepoint('stale_reorder')
            frappe.db.set_value('Warehouse',source['warehouse'],'custom_osr_master_key','foreign-warehouse')
            blocked=False
            try:assign_city_scope(request())
            except frappe.ValidationError:blocked=True
            check('business.replenishment.stale-warehouse',blocked)
            frappe.db.rollback(save_point='stale_reorder')
            # Simulate a stale conflicting stored rule, bypassing configuration validation.
            original=frappe.get_doc('Item',item.name).reorder_levels[0].as_dict()
            original.update(name='ambiguous-'+key,custom_osr_component_key='ambiguous-'+key,custom_osr_component_project='conflicting-project')
            frappe.get_doc(original).db_insert()
            blocked=False
            try:assign_city_scope(request())
            except frappe.ValidationError:blocked=True
            check('business.replenishment.ambiguous-project',blocked)
        frappe.db.rollback(save_point='reorder_flow');frappe.clear_cache()
    # Submitted native training, attendance and graded results; competence remains separate.
    employee=insert('Employee',first_name='Example training fixture',gender=frappe.db.get_value('Gender',{},'name'),date_of_birth='1990-01-01',date_of_joining='2020-01-01',status='Active',company=company)
    programme=component('training',dict(title='Maintenance assessment '+key,description='Simulation assessment; no operational competence authorization'),'training')
    for grade,attendance in [('Fail','Absent'),('Pass','Present')]:
        event=insert('Training Event',event_name='Assessment '+key+' '+grade,event_status='Scheduled',type='Exam',location='Example city simulator',start_time='2026-10-05 09:00:00',end_time='2026-10-05 10:00:00',introduction='Test-only training workflow',training_program=programme.name,company=company,employees=[dict(employee=employee.name,attendance=attendance,is_mandatory=1)])
        event.submit()
        assessment=insert('Training Result',training_event=event.name,employees=[dict(employee=employee.name,hours=1,grade=grade,comments='Simulated assessment')]);assessment.submit()
        event.reload();assessment.reload()
        check('business.training.'+grade,assessment.docstatus==1 and assessment.employees[0].grade==grade and event.employees[0].attendance==attendance,grade=assessment.employees[0].grade,attendance=event.employees[0].attendance)
    blocked=False
    try:insert('Training Event',event_name='Invalid period '+key,event_status='Scheduled',type='Exam',location='Simulator',start_time='2026-10-05 10:00:00',end_time='2026-10-05 09:00:00',introduction='Invalid test period')
    except frappe.ValidationError:blocked=True
    check('business.training.invalid-period',blocked)
    result.update(passed=True)
except BaseException as error:result['error']=str(error);raise
finally:
    frappe.db.rollback();frappe.destroy();print('OSR_BUSINESS:'+json.dumps(result,default=str),flush=True)
