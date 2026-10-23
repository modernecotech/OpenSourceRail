"""Disposable, authenticated current-maglev pilot over native ERPNext records.

Explicit simulator execution submits ERP business fixtures. It cannot commission
equipment, approve engineering, send motion commands or release a railway.
"""
from copy import deepcopy
from datetime import date, timedelta, datetime
from pathlib import Path
import json
import re
import frappe
from osr_erpnext import maglev_lifecycle_contract as contract


def _root():
    p=Path(frappe.get_site_path('private','files','osr-maglev-pilot'));p.mkdir(parents=True,exist_ok=True);return p

def _context(write=False):
    if frappe.session.user=='Guest':frappe.throw('Sign in to the pilot workspace',frappe.PermissionError)
    root=_root();pointer=json.loads((root/'current.json').read_text());run=pointer['run']
    if not re.fullmatch('[A-Za-z0-9-]{1,50}',run):frappe.throw('Invalid pilot run')
    folder=root/run;package=contract.validate_package(json.loads((folder/'package.json').read_text()))
    project=frappe.get_doc('Project',pointer['project']);project.check_permission('write' if write else 'read')
    if project.custom_osr_package_sha256!=package['sha256']:frappe.throw('Controlled pilot project/package changed')
    return folder,package,project,contract.Ledger(folder/'lifecycle.sqlite',package)


@frappe.whitelist(methods=['GET'])
def snapshot():
    folder,package,project,ledger=_context();result=json.loads((folder/'result.json').read_text())
    return dict(package=package,project=project.name,result=result,journal=ledger.snapshot(),actor=frappe.session.user,
        allowed_actions=['test-pass','test-fail'] if 'Quality Manager' in frappe.get_roles() else [],
        reviewer='Projects Manager' in frappe.get_roles(),**contract.FLAGS)


def _quality(reference_type,reference,item,line,value,parameter,company,remarks='Explicit software fixture; no physical test',actor=None):
    previous=frappe.session.user
    if actor:frappe.set_user(actor)
    try:return _quality_record(reference_type,reference,item,line,value,parameter,company,remarks)
    finally:frappe.set_user(previous)

def _quality_record(reference_type,reference,item,line,value,parameter,company,remarks):
    qa=frappe.get_doc(dict(doctype='Quality Inspection',company=company,inspection_type='Incoming' if reference_type=='Purchase Receipt' else 'In Process',reference_type=reference_type,
        reference_name=reference,item_code=item,child_row_reference=line,sample_size=1,inspected_by=frappe.session.user,remarks=remarks,
        readings=[dict(specification=parameter,numeric=0,value='Pass',reading_value=value)])).insert();qa.submit();return qa


@frappe.whitelist(methods=['POST'])
def action(asset_id,action,expected_head):
    """Small useful native UI: record simulated tests and independent review.

    Roles come from authenticated ERP users, not role strings in a browser.
    Native record is committed before journal dispatch; a dispatch retry uses
    its deterministic event key and cannot duplicate or revise the prior event.
    """
    folder,package,project,ledger=_context(write=True);state=ledger.snapshot()
    event_id=contract.digest(dict(asset=asset_id,action=action,head=expected_head,actor=frappe.session.user))
    previous=next((e for e in state['events'] if e['command']['id']=='ui-'+event_id),None)
    if previous:return dict(created=False,head_sha256=state['head_sha256'],physical_release=False,engineering_accepted=False)
    if state['head_sha256']!=expected_head:frappe.throw('Pilot changed; refresh before acting')
    pos=state['state']['positions'].get(asset_id)
    if not pos or not pos['serial']:frappe.throw('Current installed pilot serial required')
    position=next(p for p in package['positions'] if p['asset_id']==asset_id);serial=pos['serial']
    result=json.loads((folder/'result.json').read_text());native=next(x for x in result['products'] if x['asset_id']==asset_id)
    if action in {'test-pass','test-fail'}:
        if 'Quality Manager' not in frappe.get_roles():frappe.throw('Quality Manager required',frappe.PermissionError)
        value='Pass' if action=='test-pass' else 'Fail'
        old=frappe.db.get_value('Quality Inspection',{'remarks':'SIM-PILOT-EVENT:'+event_id},'name')
        qa=frappe.get_doc('Quality Inspection',old) if old else _quality('Stock Entry',native['stock_entries'][-1],native['finished_item'],native['finished_row'],value,native['qa_parameter'],project.company,'SIM-PILOT-EVENT:'+event_id)
        kind='test';data=dict(result='pass' if value=='Pass' else 'fail',test_record=qa.name);role='inspector';refs=dict(doctype='Quality Inspection',name=qa.name,status=qa.status)
    elif action=='review-business':
        if 'Projects Manager' not in frappe.get_roles():frappe.throw('Projects Manager required',frappe.PermissionError)
        if not pos['last_test']:frappe.throw('Exact latest test required')
        kind='handback';role='reviewer';data=dict(test_id=pos['last_test']['id'],review_record='native-user-review:'+event_id)
        refs=dict(user=frappe.session.user,latest_test=deepcopy(pos['last_test']),scope='Software-business review only')
    else:frappe.throw('Unsupported pilot action')
    product=next(p for p in package['products'] if p['product_id']==position['product_id'])
    cmd=dict(id='ui-'+event_id,kind=kind,asset_id=asset_id,serial=serial,batch=state['state']['articles'][serial]['batch'],
        configuration_sha256=package['configuration_sha256'],product_revision_sha256=product['product_revision_sha256'],actor=frappe.session.user,role=role,evidence=[contract.digest(refs)],data=data)
    contract.transition(state['state'],cmd,package) # refuse self/failed/stale review before committing
    frappe.db.commit()
    response=ledger.append(cmd,expected_head=expected_head)
    frappe.get_doc('Asset',native['asset']).add_comment('Info','Software pilot '+kind+' '+serial+' / '+cmd['evidence'][0]+'; physical handback remains required.')
    return dict(**response,physical_release=False,engineering_accepted=False)


def run_fixture(package,bundle,run_id):
    """Explicit native development campaign, callable only by Administrator.

    The isolated runner supplies source-controlled product identity. Every
    native amount/rate is labelled a software fixture, never a supplier quote.
    """
    if frappe.session.user!='Administrator':frappe.throw('Explicit administrator fixture action required',frappe.PermissionError)
    contract.validate_package(package)
    if not re.fullmatch('[A-Za-z0-9-]{1,50}',run_id):raise ValueError('bounded isolated run required')
    from osr_erpnext import api,planning,setup,components,integration,disposition,engineering_identity
    from erpnext.manufacturing.doctype.work_order.work_order import make_stock_entry
    from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
    from frappe.utils import get_url_to_form
    frappe.flags.mute_emails=True
    setup.create_evaluation_company();setup.install()
    # Each explicit campaign has a distinct evaluation company. Native released
    # revision -> Item/BOM mappings are immutable and are never overwritten to
    # make a repeat campaign pass with different fixture Item codes.
    company='OpenSourceRail Pilot '+run_id
    frappe.get_doc(dict(doctype='Company',company_name=company,abbr='MP'+contract.digest(run_id)[:6].upper(),default_currency='USD',country='Iraq',
        chart_of_accounts='Standard',create_chart_of_accounts_based_on='Standard Template')).insert()
    plan=planning.make_plan(bundle);imported=api.import_plan(plan,company);project=frappe.get_doc('Project',imported['project'])
    if api.import_plan(plan,company)['created']!=0:raise AssertionError('planning retry duplicated tasks')
    project.custom_osr_package_sha256=package['sha256'];project.custom_osr_config_sha256=package['configuration_sha256']
    label='Maglev pilot fixture stores';project.custom_osr_config=json.dumps(dict(organisation=dict(warehouses=[label])));project.save()
    key=planning.digest([company,'baghdad','Warehouse',label]);warehouse=frappe.db.get_value('Warehouse',{'custom_osr_master_key':key},'name')
    def insert(dt,**kw):return frappe.get_doc(dict(doctype=dt,**kw)).insert()
    if not warehouse:warehouse=insert('Warehouse',warehouse_name=label,company=company,custom_osr_master_key=key).name
    group=frappe.db.get_value('Item Group',{'is_group':0},'name')
    supplier_name='SIM Maglev software fixture '+run_id
    supplier=insert('Supplier',supplier_name=supplier_name,supplier_type='Company',supplier_group='All Supplier Groups')
    users={}
    roles=['Projects Manager','Manufacturing Manager','Manufacturing User','Purchase Manager','Stock Manager','Stock User','Quality Manager','Asset Manager','Asset User','Support Team']
    available=[r for r in roles if frappe.db.exists('Role',r)]
    for name in ('inspector','reviewer','observer','reader'):
        email='maglev-pilot-'+name+'@example.invalid'
        desired=['Projects User'] if name=='reader' else ['Projects User','Support Team'] if name=='observer' else available
        if not frappe.db.exists('User',email):insert('User',email=email,first_name='Maglev pilot '+name,send_welcome_email=0,roles=[dict(role=r) for r in desired])
        else:
            user=frappe.get_doc('User',email)
            if user.first_name!='Maglev pilot '+name:frappe.throw('Reserved simulator user collides with an existing user')
            user.set('roles',[dict(role=r) for r in desired]);user.save()
        users[name]=email
    # Record roles and identity on server; clients cannot widen this policy.
    scopes={u:dict(cities=['baghdad'],environments=['simulation'],projects=[project.name]) for n,u in users.items() if n!='reader'}
    current=frappe.conf.get('osr_integration_users') or {};current.update(scopes)
    from frappe.installer import update_site_config
    update_site_config('osr_integration_users',current);frappe.conf.osr_integration_users=current
    create_custom_fields({'Asset':[dict(fieldname='custom_osr_pilot_current_serial',label='Simulation installed serial',fieldtype='Data',read_only=1),dict(fieldname='custom_osr_pilot_revision',label='Simulation product revision',fieldtype='Data',read_only=1)]})
    fixed=frappe.db.get_value('Account',{'company':company,'is_group':0,'account_type':'Fixed Asset'},'name')
    category_name='SIM Maglev positions '+run_id
    category=insert('Asset Category',asset_category_name=category_name,accounts=[dict(company_name=company,fixed_asset_account=fixed)])
    location=insert('Location',location_name='SIM Maglev fixture '+run_id)
    parameter=insert('Quality Inspection Parameter',parameter='SIM software record pass code '+run_id)
    root=_root()/run_id;root.mkdir(parents=True,exist_ok=False);(root/'package.json').write_text(json.dumps(package,sort_keys=True));ledger=contract.Ledger(root/'lifecycle.sqlite',package)
    products=[];negative=[];evidence_bodies=[]
    def event(position,serial,kind,data,actor='Administrator',refs=None):
        product=next(p for p in package['products'] if p['product_id']==position['product_id']);batch='SIM-BATCH-'+run_id+'-'+str(package['positions'].index(position))
        body=dict(environment='simulation',native_records=refs or data,physical_test=False)
        cmd=dict(id=run_id+'-'+str(len(ledger.snapshot()['events'])+1),kind=kind,asset_id=position['asset_id'],serial=serial,batch=batch,
            configuration_sha256=package['configuration_sha256'],product_revision_sha256=product['product_revision_sha256'],actor=actor,role=contract.ROLES[kind],evidence=[contract.digest(body)],data=data)
        ledger.append(cmd);assert not ledger.append(cmd)['created'];evidence_bodies.append(dict(sha256=contract.digest(body),body=body));return cmd
    def refused(label,callback,types=(ValueError,PermissionError,frappe.ValidationError,frappe.PermissionError)):
        try:callback()
        except types:negative.append(dict(id=label,passed=True));return
        raise AssertionError('Unsafe action accepted: '+label)
    for number,position in enumerate(package['positions']):
        product=next(p for p in package['products'] if p['product_id']==position['product_id']);short=str(number)+'-'+run_id
        raw=[]
        for i,line in enumerate(product['bom']):
            # Each stock kit represents one exact source engineering BOM row.
            # Quantified engineering values remain in its immutable description;
            # allocated/missing parts are explicit unqualified kit allowances.
            item=insert('Item',item_code='SIM-MAG-RAW-'+short+'-'+str(i),item_name=line['id'],item_group=group,stock_uom='Nos',is_stock_item=1,is_purchase_item=1,inspection_required_before_purchase=1 if i==0 else 0,
                description='SOFTWARE FIXTURE KIT; engineering source '+line['source_sha256']+' / '+json.dumps(line['source'],sort_keys=True))
            raw.append(item)
        fg=insert('Item',item_code='SIM-MAG-FG-'+short,item_name=product['product_id'],item_group=group,stock_uom='Nos',is_stock_item=1,has_serial_no=1,has_batch_no=1,
            description='SIMULATED current product '+product['product_revision_sha256']+' / no physical manufacturing release')
        batch=insert('Batch',batch_id='SIM-BATCH-'+run_id+'-'+str(number),item=fg.name)
        bom=insert('BOM',item=fg.name,company=company,quantity=1,currency='USD',items=[dict(item_code=x.name,qty=1,rate=1) for x in raw]);bom.submit()
        mapping=dict(schema='osr-execution-proposal/1',city='baghdad',asset_id=position['asset_id'],engineering_revision=product['product_revision_sha256'],engineering_sha256=package['configuration_sha256'],
            mapping=dict(review_reference='simulation-current-maglev-'+run_id,items=[dict(component_type_id=product['product_id'],erp_item_code=fg.name,uom='Nos',production_bom=bom.name,
            conversion_rule='One explicit software fixture kit per engineering BOM row; detailed quantities and qualification remain source-bound.',inspection_reference='qualification/physical-unexecuted',drawing_reference='product-geometry-sha256:'+product['geometry_sha256'])]))
        mapping['sha256']=planning.digest(mapping);preview=integration.preview_execution(project.name,mapping);mapped=integration.apply_execution(project.name,mapping,preview['fingerprint'])
        assert integration.apply_execution(project.name,mapping,preview['fingerprint'])==mapped
        mr=insert('Material Request',material_request_type='Purchase',company=company,schedule_date=str(date.today()),items=[dict(item_code=x.name,qty=4,warehouse=warehouse,project=project.name) for x in raw])
        po=insert('Purchase Order',supplier=supplier.name,company=company,schedule_date=str(date.today()),items=[dict(item_code=x.name,qty=4,rate=1,warehouse=warehouse,project=project.name) for x in raw])
        assert mr.docstatus==po.docstatus==0
        old='SIM-MAG-'+short+'-OLD';new='SIM-MAG-'+short+'-NEW'
        event(position,old,'purchase',dict(draft_material_request=mr.name,draft_purchase_order=po.name,bom_sha256=contract.digest(product['bom'])))
        # Explicit fixture execution, separate from the draft mapping/import.
        po.submit()
        receipt=insert('Purchase Receipt',supplier=supplier.name,company=company,items=[dict(item_code=r.item_code,qty=4,rate=1,warehouse=warehouse,project=project.name,purchase_order=po.name,purchase_order_item=r.name) for r in po.items])
        event(position,old,'receive',dict(receipt=receipt.name))
        failed=_quality('Purchase Receipt',receipt.name,raw[0].name,receipt.items[0].name,'Fail',parameter.name,company,actor=users['inspector'])
        event(position,old,'inspect',dict(result='fail',inspection=failed.name),users['inspector'])
        ncr=insert('Issue',subject='SIM nonconformance '+product['product_id'],project=project.name,description='Software fixture rejected inspection '+failed.name)
        rework=insert('Task',subject='SIM corrective preparation '+product['product_id'],project=project.name,description='Record rejected fixture '+failed.name+'; no physical rework claimed')
        event(position,old,'rework',dict(nonconformance=ncr.name,rework_order=rework.name))
        passed=_quality('Purchase Receipt',receipt.name,raw[0].name,receipt.items[0].name,'Pass',parameter.name,company,actor=users['inspector'])
        receipt.reload();receipt.items[0].quality_inspection=passed.name;receipt.save();receipt.submit()
        rework.status='Completed';rework.save();event(position,old,'inspect',dict(result='pass',inspection=passed.name),users['inspector'])
        asset_item=insert('Item',item_code='SIM-MAG-POS-'+short,item_name='SIM '+product['product_id']+' position',item_group=group,stock_uom='Nos',is_stock_item=0,is_fixed_asset=1,asset_category=category.name)
        # Position identity stays stable. An old serial is never renamed to free
        # a unique Asset key; the journal keeps every installation/removal.
        asset=insert('Asset',company=company,item_code=asset_item.name,asset_name='SIM '+position['asset_id'],asset_category=category.name,location=location.name,
            purchase_date=str(date.today()-timedelta(days=1)),available_for_use_date=str(date.today()-timedelta(days=1)),is_existing_asset=1,gross_purchase_amount=1,calculate_depreciation=0,
            custom_osr_asset_id=position['asset_id']+':'+run_id,custom_osr_pilot_revision=product['product_revision_sha256'])
        asset.submit();work_orders=[];stock_entries=[];finished_row=None;issue=None;repair=None
        for serial in (old,new):
            if serial==new:
                event(position,new,'purchase',dict(draft_material_request=mr.name,draft_purchase_order=po.name,bom_sha256=contract.digest(product['bom'])))
                event(position,new,'receive',dict(receipt=receipt.name));event(position,new,'inspect',dict(result='pass',inspection=passed.name),users['inspector'])
            values=dict(bom=bom.name,quantity=1,source_warehouse=warehouse,wip_warehouse=warehouse,fg_warehouse=warehouse,start=str(date.today())+' 01:00:00')
            prepared=components.preview(project.name,'manufacturing',serial.lower(),values)
            wo=frappe.get_doc('Work Order',components.apply(project.name,'manufacturing',serial.lower(),values,prepared['fingerprint'])['name']);wo.skip_transfer=1;wo.save();wo.submit()
            stock=frappe.get_doc(make_stock_entry(wo.name,'Manufacture',1))
            for row in stock.items:
                row.project=project.name
                if row.item_code==fg.name:row.serial_no=serial;row.batch_no=batch.name;row.use_serial_batch_fields=1
            stock.insert();stock.submit();stock.reload();finished_row=next(r.name for r in stock.items if r.item_code==fg.name)
            assert frappe.db.exists('Serial No',serial);wo.reload();assert wo.produced_qty==1
            work_orders.append(wo.name);stock_entries.append(stock.name)
            event(position,serial,'assemble',dict(work_order=wo.name,manufacture_entry=stock.name))
            # Native material issue records the exact finished serial leaving
            # stores for this simulated installation.
            issued=insert('Stock Entry',stock_entry_type='Material Issue',company=company,items=[dict(item_code=fg.name,qty=1,s_warehouse=warehouse,serial_no=serial,batch_no=batch.name,use_serial_batch_fields=1,project=project.name)]);issued.submit()
            event(position,serial,'install',dict(installation_record=issued.name,**(dict(replaces_serial=old) if serial==new else {})))
            asset.db_set('custom_osr_pilot_current_serial',serial)
            test=_quality('Stock Entry',stock.name,fg.name,finished_row,'Pass',parameter.name,company,actor=users['inspector'])
            last=event(position,serial,'test',dict(result='pass',test_record=test.name),users['inspector'])
            if serial==new:
                fail=_quality('Stock Entry',stock.name,fg.name,finished_row,'Fail',parameter.name,company,actor=users['inspector'])
                event(position,serial,'test',dict(result='fail',test_record=fail.name),users['inspector'])
                bad=deepcopy(last);bad.update(id=run_id+'-bad-'+str(number),kind='handback',actor=users['reviewer'],role='reviewer',data=dict(test_id=last['id'],review_record='stale-test'))
                refused('latest-failure-'+str(number),lambda:ledger.append(bad))
                retest=_quality('Stock Entry',stock.name,fg.name,finished_row,'Pass',parameter.name,company,actor=users['inspector'])
                last=event(position,serial,'test',dict(result='pass',test_record=retest.name),users['inspector'])
                bad.update(id=run_id+'-self-'+str(number),actor=users['inspector'],data=dict(test_id=last['id'],review_record='self'))
                refused('self-review-'+str(number),lambda:ledger.append(bad))
            event(position,serial,'handback',dict(test_id=last['id'],review_record='native-independent-user:'+users['reviewer']),users['reviewer'])
            if serial==old:
                frappe.set_user(users['observer'])
                alarm=dict(event_id='SIM-EVENT-'+short,incident_id='SIM-INCIDENT-'+short,city='baghdad',environment='simulation',company=company,project=project.name,
                    asset_id=asset.custom_osr_asset_id,erp_asset_id=asset.name,rule='software-fixture-fault',condition='active',occurrence=1,response='Simulated current maglev part replacement; no physical inference')
                made=integration.condition_event(alarm);assert integration.condition_event(alarm)['duplicate'];issue=made['issue']
                refused('physical-ingress-'+str(number),lambda:integration.condition_event({**alarm,'environment':'physical'}))
                frappe.set_user('Administrator');event(position,serial,'alarm',dict(incident_id=alarm['incident_id']),users['observer'])
                proposal=dict(schema='osr-condition-repair/1',key='current-maglev-'+short,failure_date=str(date.today())+' 01:00:00',expected_downtime_hours=2,technician='Administrator',
                    description='SIM replacement workflow; consume one explicit software fixture consumable; physical handback remains open.',parts=[dict(item=raw[0].name,warehouse=warehouse,quantity=1)],
                    evidence_references=['removed-serial:'+old,'product-revision:'+product['product_revision_sha256'],'SIM:no-physical-work'])
                prep=integration.preview_repair(issue,proposal);repair=integration.apply_repair(issue,proposal,prep['fingerprint'])['name']
                event(position,serial,'maintain',dict(maintenance_case=repair));event(position,serial,'remove',dict(removal_record=repair))
                doc=frappe.get_doc('Asset Repair',repair);doc.actions_performed='SIM business fixture replacement; physical QA and handback required.';doc.repair_status='Completed';doc.completion_date=str(date.today())+' 02:00:00';doc.save();doc.submit()
                assert doc.custom_osr_handback_required
                assert not integration.apply_repair(issue,proposal,prep['fingerprint'])['automatic_handback']
                frappe.db.commit();before=ledger.snapshot();ledger=contract.Ledger(root/'lifecycle.sqlite',package);assert before==ledger.snapshot()
        # A real independently reviewed revision disposition remains separate
        # from the plan, and never silently amends a purchase or product.
        draft=insert('Purchase Order',supplier=supplier.name,company=company,schedule_date=str(date.today()),items=[dict(item_code=raw[0].name,qty=1,rate=1,warehouse=warehouse,project=project.name)])
        request=dict(key='revision-'+short,mapping=mapped['mappings'][0],target=dict(kind='purchase-line',document=draft.name,line=draft.items[0].name),action='Request amendment',responsible='Administrator',due_date=str(date.today()+timedelta(days=5)),
            rationale='Proposed current maglev product revision requires independent review; no automatic BOM/serial migration.',references=['SIM:unadopted-revision:'+run_id])
        d=disposition.preview(project.name,request);record=disposition.record(project.name,request,d['fingerprint'])
        refused('disposition-self-review-'+str(number),lambda:disposition.preview_decision(record['name'],dict(outcome='Endorse plan',rationale='Independent review required',references=['SIM:review'])))
        frappe.set_user(users['reviewer']);decision=dict(outcome='Endorse plan',rationale='Reviewed as a simulated proposed amendment; execution and engineering acceptance remain separate.',references=['SIM:independent-review:'+run_id]);d=disposition.preview_decision(record['name'],decision);disposition.record_decision(record['name'],decision,d['fingerprint']);frappe.set_user('Administrator')
        assert frappe.get_doc('Purchase Order',draft.name).docstatus==0
        identity=dict(schema='osr-engineering-qa-map/1',configuration_sha256=package['configuration_sha256'],design_revision=product['product_revision_sha256'],state='as-maintained',asset_id=position['asset_id'],characteristics=[
            dict(inspection_id=position['asset_id']+'/software-code',instance_id=position['asset_id'],part_id=position['product_id'],part_revision=product['product_revision_sha256'],serial=new,batch=batch.name,
                 characteristic='Explicit simulated record code; no material/property result',unit='simulation-code',minimum=None,maximum=None,joint_ids=[])])
        identity['sha256']=engineering_identity.digest(identity)
        qa_binding=engineering_identity.bind_quality_result(identity,dict(project=project.name,company=company,work_order=work_orders[-1],quality_inspection=retest.name,material_batch=batch.name,
            nonconformance=ncr.name,calibration_record='SIM-SOFTWARE-CODE-NO-PHYSICAL-CALIBRATION'),dict(inspection_id=identity['characteristics'][0]['inspection_id'],configuration_sha256=package['configuration_sha256'],part_revision=product['product_revision_sha256'],serial=new,batch=batch.name,unit='simulation-code',value=1))
        products.append(dict(product_id=product['product_id'],product_revision_sha256=product['product_revision_sha256'],asset_id=position['asset_id'],asset=asset.name,finished_item=fg.name,finished_row=finished_row,qa_parameter=parameter.name,
            material_request=mr.name,purchase_order=po.name,receipt=receipt.name,failed_inspection=failed.name,rework_task=rework.name,work_orders=work_orders,stock_entries=stock_entries,issue=issue,asset_repair=repair,
            old_serial=old,current_serial=new,batch=batch.name,engineering_qa_identity=identity,engineering_qa_binding=qa_binding,serial_history=deepcopy(ledger.snapshot()['state']['positions'][position['asset_id']]),revision_disposition=record['name'],native_asset_identity=asset.custom_osr_asset_id,
            links={dt:get_url_to_form(dt,name) for dt,name in [('Asset',asset.name),('Purchase Order',po.name),('Quality Inspection',failed.name),('Work Order',work_orders[-1]),('Issue',issue),('Asset Repair',repair)]},physical_release=False))
    # Real permission refusal over the existing scoped native feedback API.
    frappe.set_user(users['reader']);refused('native-permission',lambda:components.preview(project.name,'manufacturing','forbidden',dict(bom=bom.name,quantity=1,source_warehouse=warehouse,wip_warehouse=warehouse,fg_warehouse=warehouse,start=str(date.today())+' 01:00:00')))
    frappe.set_user('Administrator')
    result=dict(schema='osr-maglev-native-business-result/1',environment='simulation',run=run_id,configuration_sha256=package['configuration_sha256'],project=project.name,company=company,products=products,negative_controls=negative,
        journal=ledger.snapshot(),evidence_bodies=evidence_bodies,users=users,physical_release=False,engineering_accepted=False,fixture_valuation='USD1 per software kit; not a product quote, financial forecast or real asset value')
    (root/'result.json').write_text(json.dumps(result,sort_keys=True,indent=2));(_root()/'current.json').write_text(json.dumps(dict(run=run_id,project=project.name)))
    frappe.db.commit();return result
