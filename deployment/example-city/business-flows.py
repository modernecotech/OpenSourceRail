"""Downstream native business workflows in a rolled-back evaluation transaction."""
import os,json,uuid
from datetime import date,timedelta
import frappe
os.chdir('/home/frappe/frappe-bench/sites');frappe.init(site=INPUT['site']);frappe.connect();frappe.flags.mute_emails=True
source=INPUT['source'];project=source['project'];company=source['company'];key=uuid.uuid4().hex[:10];checks=[];fixture_files=[]
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
    review_assignment=maintenance_assignment_fixture(project,company,users,key,fixture_files)
    for strategy in ['Round Robin','Load Balancing']:
        frappe.db.savepoint('assignment_flow')
        rule=component('assignment',dict(category='maintenance',strategy=strategy,users=[dict(user=u) for u in users]),'assignment-'+str(len(checks)))
        rule.disabled=1;rule.assignment_days=[]
        for day in ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']:rule.append('assignment_days',dict(day=day))
        rule.save();frappe.clear_cache()
        observed=[]
        for i in range(2):
            task=insert('Task',subject='Assignment flow '+key+' '+str(i),project=project,custom_osr_kind='maintenance',exp_end_date=str(date.today()+timedelta(days=2)))
            blocked=False
            try:insert('ToDo',reference_type='Task',reference_name=task.name,allocated_to=users[0],status='Open',description='Simulation unreviewed assignment')
            except frappe.ValidationError as error:
                if 'allocation review' not in str(error):raise
                blocked=True
            check('business.assignment.unreviewed-blocked.'+strategy+'.'+str(i),blocked)
            review_assignment(task,i+1)
            rule.disabled=0;rule.save();frappe.clear_cache()
            assign(task)
            targets=frappe.get_all('ToDo',filters={'reference_type':'Task','reference_name':task.name,'status':'Open'},pluck='allocated_to')
            check('business.assignment.'+strategy+'.'+str(i),len(targets)==1 and targets[0] in users,assigned=targets)
            observed+=targets
            rule.reload();rule.disabled=1;rule.save();frappe.clear_cache()
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
    # HRMS is installed in this native fixture. Test attendance/payroll arithmetic
    # with declared amounts only; no jurisdictional tax/benefit policy is inferred.
    from calendar import monthrange
    month_start=date.today().replace(day=1);month_end=date.today().replace(day=monthrange(date.today().year,date.today().month)[1])
    holidays=insert('Holiday List',holiday_list_name='FLOWS holidays '+key,from_date=str(month_start),to_date=str(month_end))
    employee.holiday_list=holidays.name;employee.save()
    frappe.db.set_single_value('Payroll Settings','payroll_based_on','Attendance')
    frappe.db.set_single_value('Payroll Settings','consider_unmarked_attendance_as','Present')
    frappe.db.set_single_value('Payroll Settings','email_salary_slip_to_employee',0)
    attendance=insert('Attendance',employee=employee.name,company=company,status='Present',attendance_date=str(date.today()));attendance.submit()
    duplicate=False
    try:insert('Attendance',employee=employee.name,company=company,status='Absent',attendance_date=str(date.today()))
    except frappe.ValidationError:duplicate=True
    check('business.attendance.duplicate-blocked',duplicate)
    currency=frappe.db.get_value('Company',company,'default_currency')
    earning=insert('Salary Component',salary_component='FLOWS earning '+key,salary_component_abbr='E'+key,type='Earning',depends_on_payment_days=0,is_tax_applicable=0)
    deduction=insert('Salary Component',salary_component='FLOWS deduction '+key,salary_component_abbr='D'+key,type='Deduction',depends_on_payment_days=0)
    structure=insert('Salary Structure',name='FLOWS salary '+key,company=company,currency=currency,is_active='Yes',payroll_frequency='Monthly',earnings=[dict(salary_component=earning.name,amount=1200)],deductions=[dict(salary_component=deduction.name,amount=120)]);structure.submit()
    assignment=insert('Salary Structure Assignment',employee=employee.name,company=company,currency=currency,salary_structure=structure.name,from_date=str(month_start));assignment.submit()
    slip=insert('Salary Slip',employee=employee.name,company=company,currency=currency,start_date=str(month_start),end_date=str(date.today()),posting_date=str(date.today()),salary_structure=structure.name);slip.submit();slip.reload()
    check('business.payroll.declared-arithmetic',slip.gross_pay==1200 and slip.total_deduction==120 and slip.net_pay==1080 and slip.docstatus==1,gross=slip.gross_pay,deductions=slip.total_deduction,net=slip.net_pay,currency=currency,policy='synthetic fixed non-prorated amounts; country statutory policy open')
    # Native purchase commitments must be caught before expense booking.
    frappe.db.savepoint('commitment_flow')
    budget=component('budget',dict(fiscal_year=year,action='Stop',accounts=[dict(account=expense,amount=100)]),'commitment-budget')
    budget.applicable_on_purchase_order=1;budget.action_if_annual_budget_exceeded_on_po='Stop';budget.submit()
    blocked=False
    try:
        order=insert('Purchase Order',company=company,supplier=source['supplier'],project=project,schedule_date=str(date.today()+timedelta(days=2)),items=[dict(item_code=service.name,qty=1,rate=101,schedule_date=str(date.today()+timedelta(days=2)),expense_account=expense,cost_center=center,project=project)]);order.submit()
    except frappe.ValidationError as error:
        if 'budget' not in str(error).lower():raise
        blocked=True
    check('business.procurement.over-budget-commitment-blocked',blocked)
    frappe.db.rollback(save_point='commitment_flow');frappe.clear_cache()
    # Asset value/depreciation use native schedules; booked journals are separate.
    asset_parent=frappe.db.get_value('Account',{'company':company,'root_type':'Asset','is_group':1},'name')
    fixed=insert('Account',account_name='FLOWS fixed '+key,parent_account=asset_parent,company=company,account_type='Fixed Asset')
    accumulated=insert('Account',account_name='FLOWS accumulated '+key,parent_account=asset_parent,company=company,account_type='Accumulated Depreciation')
    depreciation_expense=frappe.db.get_value('Account',{'company':company,'account_type':'Depreciation','is_group':0},'name')
    if not depreciation_expense:
        parent=frappe.db.get_value('Account',{'company':company,'root_type':'Expense','is_group':1},'name')
        depreciation_expense=insert('Account',account_name='FLOWS depreciation '+key,parent_account=parent,company=company,account_type='Depreciation').name
    category=insert('Asset Category',asset_category_name='FLOWS depreciable '+key,enable_cwip_accounting=0,accounts=[dict(company_name=company,fixed_asset_account=fixed.name,accumulated_depreciation_account=accumulated.name,depreciation_expense_account=depreciation_expense)],finance_books=[dict(depreciation_method='Straight Line',total_number_of_depreciations=4,frequency_of_depreciation=12,expected_value_after_useful_life=200)])
    item=insert('Item',item_code='FLOWS-ASSET-'+key,item_group=group,stock_uom='Nos',is_stock_item=0,is_fixed_asset=1,asset_category=category.name)
    location=frappe.db.get_value('Location',{},'name')
    if not location:location=insert('Location',location_name='FLOWS location '+key).name
    asset=insert('Asset',company=company,item_code=item.name,asset_name='FLOWS asset '+key,location=location,is_existing_asset=1,purchase_date=str(month_start),available_for_use_date=str(month_start),gross_purchase_amount=1000,opening_accumulated_depreciation=0,calculate_depreciation=1,finance_books=[dict(depreciation_method='Straight Line',total_number_of_depreciations=4,frequency_of_depreciation=12,depreciation_start_date=str(month_end),expected_value_after_useful_life=200)]);asset.submit()
    schedules=frappe.get_all('Asset Depreciation Schedule',filters={'asset':asset.name,'docstatus':1},pluck='name')
    values=[r.depreciation_amount for name in schedules for r in frappe.get_doc('Asset Depreciation Schedule',name).depreciation_schedule]
    # A partial first annual period adds a final balancing period. Verify the
    # full four-year amount and annual middle periods, rather than hiding those.
    check('business.asset.depreciation-schedule',len(values)==5 and all(abs(v-200)<.001 for v in values[1:-1]) and 0<values[0]<200 and abs(values[0]+values[-1]-200)<.001 and abs(sum(values)-800)<.001,asset_value=1000,residual_value=200,schedule=values,native_prorata_first_and_last_periods=True,capitalization_basis='declared existing-asset opening value; purchase/capitalization journals require separate test')
    # Existing-asset values require an actual opening journal. This test books
    # the declared fixture value, verifies native ledger rows, then rolls back.
    equity_parent=frappe.db.get_value('Account',{'company':company,'root_type':'Equity','is_group':1},'name')
    opening_contra=insert('Account',account_name='FLOWS opening '+key,parent_account=equity_parent,company=company)
    opening=insert('Journal Entry',voucher_type='Opening Entry',is_opening='Yes',company=company,posting_date=str(date.today()),user_remark='Simulation-only existing-asset opening balance',accounts=[dict(account=fixed.name,debit_in_account_currency=1000,cost_center=center),dict(account=opening_contra.name,credit_in_account_currency=1000,cost_center=center)]);opening.submit()
    ledger=frappe.get_all('GL Entry',filters={'voucher_type':'Journal Entry','voucher_no':opening.name,'is_cancelled':0},fields=['account','debit','credit'])
    check('business.asset.opening-journal-booked',sum(r.debit for r in ledger)==1000 and sum(r.credit for r in ledger)==1000 and any(r.account==fixed.name and r.debit==1000 for r in ledger),native_ledger_rows=len(ledger),value=1000,basis='simulation existing-asset opening journal; no supplier purchase claim')
    from erpnext.assets.doctype.asset.depreciation import make_depreciation_entry
    make_depreciation_entry(schedules[0],date=str(month_end))
    schedule=frappe.get_doc('Asset Depreciation Schedule',schedules[0]);entry=schedule.depreciation_schedule[0].journal_entry
    ledger=frappe.get_all('GL Entry',filters={'voucher_type':'Journal Entry','voucher_no':entry,'is_cancelled':0},fields=['account','debit','credit'])
    amount=values[0]
    check('business.asset.native-depreciation-booked',bool(entry) and abs(sum(r.debit for r in ledger)-amount)<.001 and abs(sum(r.credit for r in ledger)-amount)<.001 and any(r.account==depreciation_expense and abs(r.debit-amount)<.001 for r in ledger) and any(r.account==accumulated.name and abs(r.credit-amount)<.001 for r in ledger),amount=amount,native_ledger_rows=len(ledger))
    # Native SLA calendar/deadline calculation for a scoped simulation issue.
    frappe.db.set_single_value('Support Settings','track_service_level_agreement',1)
    priority=frappe.db.get_value('Issue Priority',{},'name') or insert('Issue Priority',name='FLOWS priority '+key).name
    sla=insert('Service Level Agreement',service_level='FLOWS SLA '+key,document_type='Issue',enabled=1,holiday_list=holidays.name,start_date=str(month_start),end_date=str(month_end),condition='doc.project == '+repr(project),priorities=[dict(priority=priority,default_priority=1,response_time=3600,resolution_time=14400)],sla_fulfilled_on=[dict(status='Closed')],support_and_resolution=[dict(workday=day,start_time='00:00:00',end_time='23:59:59') for day in ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']])
    issue=insert('Issue',subject='FLOWS SLA '+key,raised_by='fixture@example.invalid',project=project,priority=priority)
    check('business.sla.native-deadlines',issue.service_level_agreement==sla.name and issue.response_by is not None and issue.sla_resolution_by is not None,sla=issue.service_level_agreement,response_by=issue.response_by,resolution_by=issue.sla_resolution_by)
    result.update(passed=True)
except BaseException as error:result['error']=str(error);raise
finally:
    frappe.db.rollback();remove_fixture_files(fixture_files);frappe.clear_cache();frappe.destroy();print('OSR_BUSINESS:'+json.dumps(result,default=str),flush=True)
