"""Runs only inside the isolated example ERP site; INPUT is supplied through stdin."""
import os,json
import frappe
os.chdir('/home/frappe/frappe-bench/sites');frappe.init(site=INPUT['site']);frappe.connect()
frappe.flags.mute_emails=True
try:
    phase=INPUT['phase']
    if phase=='company':
        from osr_erpnext.setup import create_evaluation_company
        result=dict(company=create_evaluation_company())
        from frappe.installer import update_site_config
        update_site_config('osr_workbench_origins',['http://127.0.0.1:8190','http://localhost:8190'])
    elif phase=='import':
        from osr_erpnext.api import import_file
        result=import_file(INPUT['path'],INPUT['company'])
    elif phase=='provision':
        from osr_erpnext.integration import provision_service
        result=provision_service('/tmp/example-scope.json','/tmp/example-credentials.json')
    elif phase=='seed':
        from datetime import date,timedelta
        def insert(dt,**values):return frappe.get_doc(dict(doctype=dt,**values)).insert()
        project=frappe.get_doc('Project',INPUT['project']);company=project.company;key=INPUT['run']
        group=frappe.db.get_value('Item Group',{'is_group':0},'name')
        raw=insert('Item',item_code='EXAMPLE-PART-'+key,item_name='Example cooling module',item_group=group,stock_uom='Nos',is_stock_item=1,is_purchase_item=1)
        fg=insert('Item',item_code='EXAMPLE-CHARGER-'+key,item_name='Example charger assembly',item_group=group,stock_uom='Nos',is_stock_item=1,has_serial_no=1,serial_no_series='EXAMPLE-.#####')
        bom=insert('BOM',item=fg.name,company=company,quantity=1,currency='USD',items=[dict(item_code=raw.name,qty=INPUT['raw_per_unit'],rate=INPUT['rate'])]);bom.submit()
        supplier=insert('Supplier',supplier_name='Example supplier '+key,supplier_type='Company',supplier_group='All Supplier Groups')
        store=frappe.db.get_value('Warehouse',{'warehouse_name':'OSR samawah Main Stores'},'name')
        installed=insert('Warehouse',warehouse_name='OSR samawah Example Installed',company=company)
        returned=frappe.db.get_value('Warehouse',{'warehouse_name':'OSR samawah Workshop Spares'},'name')
        fixed=frappe.db.get_value('Account',{'company':company,'is_group':0,'account_type':'Fixed Asset'},'name')
        category=insert('Asset Category',asset_category_name='Example charger '+key,accounts=[dict(company_name=company,fixed_asset_account=fixed)])
        capital=insert('Item',item_code='EXAMPLE-CAPITAL-'+key,item_name='Example charger capital record',item_group=group,stock_uom='Nos',is_stock_item=0,is_fixed_asset=1,asset_category=category.name)
        location=insert('Location',location_name='Example Samawah station '+key)
        yesterday=str(date.today()-timedelta(days=1))
        asset=insert('Asset',company=company,item_code=capital.name,asset_name='Example SAM-ST-001 charger',asset_category=category.name,
            location=location.name,purchase_date=yesterday,available_for_use_date=yesterday,is_existing_asset=1,gross_purchase_amount=1000,
            calculate_depreciation=0,custom_osr_asset_id='SAM-ST-001:charger');asset.submit()
        result=dict(project=project.name,company=company,raw=raw.name,item=fg.name,bom=bom.name,supplier=supplier.name,warehouse=store,installed_warehouse=installed.name,return_warehouse=returned,asset=asset.name)
    elif phase=='mapping':
        from osr_erpnext.integration import preview_execution,apply_execution
        plan=preview_execution(INPUT['project'],INPUT['proposal'])
        result=apply_execution(INPUT['project'],INPUT['proposal'],plan['fingerprint'])
        assert apply_execution(INPUT['project'],INPUT['proposal'],plan['fingerprint'])==result
    elif phase=='procure':
        from datetime import date,timedelta
        source=INPUT['source']
        order=frappe.get_doc(dict(doctype='Purchase Order',company=source['company'],supplier=source['supplier'],
            schedule_date=str(date.today()+timedelta(days=7)),items=[dict(item_code=source['raw'],qty=INPUT['ordered'],rate=INPUT['rate'],warehouse=source['warehouse'],project=source['project'])])).insert();order.submit()
        receipt=frappe.get_doc(dict(doctype='Purchase Receipt',company=source['company'],supplier=source['supplier'],
            items=[dict(item_code=source['raw'],qty=INPUT['received'],rate=INPUT['rate'],warehouse=source['warehouse'],project=source['project'],purchase_order=order.name,purchase_order_item=order.items[0].name)])).insert();receipt.submit()
        from osr_erpnext.integration import execution_feedback
        observed=execution_feedback(source['project']);line=next(r for r in observed['purchase_orders'] if r['document']==order.name)
        assert line['outstanding_qty']==INPUT['ordered']-INPUT['received']
        from erpnext.stock.doctype.purchase_receipt.purchase_receipt import make_purchase_invoice
        invoice=make_purchase_invoice(receipt.name);invoice.insert();invoice.submit()
        result=dict(order=order.name,receipt=receipt.name,invoice=invoice.name,invoice_total=invoice.grand_total,outstanding_qty=line['outstanding_qty'])
    elif phase=='manufacture':
        from datetime import date
        source=INPUT['source']
        from osr_erpnext.components import preview,apply
        values=dict(bom=source['bom'],quantity=INPUT['planned'],source_warehouse=source['warehouse'],wip_warehouse=source['warehouse'],fg_warehouse=source['warehouse'],start=str(date.today())+' 09:00:00')
        plan=preview(source['project'],'manufacturing',INPUT['run'],values)
        made=apply(source['project'],'manufacturing',INPUT['run'],values,plan['fingerprint'])
        order=frappe.get_doc('Work Order',made['name']);assert order.required_items[0].required_qty==INPUT['planned']*INPUT['raw_per_unit']
        order.skip_transfer=1;order.save();order.submit()
        from erpnext.manufacturing.doctype.work_order.work_order import make_stock_entry
        stock=frappe.get_doc(make_stock_entry(order.name,'Manufacture',INPUT['produced']));stock.insert();stock.submit();stock.reload();order.reload()
        serials=[]
        for row in stock.items:
            if row.item_code==source['item'] and row.serial_and_batch_bundle:
                bundle=frappe.get_doc('Serial and Batch Bundle',row.serial_and_batch_bundle)
                serials += [r.serial_no for r in bundle.entries]
        assert len(serials)==INPUT['produced'] and order.produced_qty==INPUT['produced']
        parameter=frappe.get_doc(dict(doctype='Quality Inspection Parameter',parameter='Example cooling check '+INPUT['run'])).insert()
        line=next(r for r in stock.items if r.item_code==source['item'])
        qa=frappe.get_doc(dict(doctype='Quality Inspection',company=source['company'],inspection_type='In Process',reference_type='Stock Entry',reference_name=stock.name,
            child_row_reference=line.name,item_code=source['item'],sample_size=1,inspected_by='Administrator',
            readings=[dict(specification=parameter.name,numeric=1,min_value=30,max_value=45,reading_1='35')])).insert();qa.submit()
        assert qa.status=='Accepted'
        result=dict(work_order=order.name,stock_entry=stock.name,serials=serials,inspection=qa.name,produced=order.produced_qty,planned=order.qty)
    elif phase=='transfer':
        source=INPUT['source'];moves=INPUT['moves']
        stock=frappe.get_doc(dict(doctype='Stock Entry',stock_entry_type='Material Transfer',company=source['company'],
            project=source['project'],items=[dict(item_code=source['item'],qty=1,s_warehouse=m['from'],t_warehouse=m['to'],
                serial_no=m['serial'],use_serial_batch_fields=1,project=source['project']) for m in moves])).insert()
        stock.submit()
        observed={m['serial']:frappe.db.get_value('Serial No',m['serial'],'warehouse') for m in moves}
        assert all(observed[m['serial']]==m['to'] for m in moves)
        result=dict(stock_entry=stock.name,serial_warehouses=observed)
    elif phase=='repair':
        from datetime import date
        from osr_erpnext.integration import preview_repair,apply_repair,execution_feedback
        source=INPUT['source'];issue=frappe.get_doc('Issue',INPUT['issue'])
        assert issue.custom_osr_asset_id=='SAM-ST-001:charger' and issue.custom_osr_erp_asset==source['asset']
        proposal=dict(schema='osr-condition-repair/1',key=INPUT['run'],failure_date=str(date.today())+' 08:00:00',expected_downtime_hours=INPUT['downtime'],
            technician='Administrator',description='Example: replace cooling module after controller fault',
            parts=[dict(item=source['raw'],warehouse=source['warehouse'],quantity=INPUT['parts'])],evidence_references=[INPUT['evidence'], 'stock-entry:'+INPUT['stock_entry']])
        plan=preview_repair(issue.name,proposal);made=apply_repair(issue.name,proposal,plan['fingerprint'])
        repair=frappe.get_doc('Asset Repair',made['name']);repair.actions_performed='Example repair performed; independent simulation inspection follows.'
        repair.repair_status='Completed';repair.completion_date=str(date.today())+' 10:00:00';repair.save();repair.submit()
        assert frappe.db.exists('Stock Entry',{'asset_repair':repair.name,'docstatus':1})
        issue.status='Closed';issue.save()
        row=next(r for r in execution_feedback(source['project'])['repairs'] if r['name']==repair.name)
        assert row['parts'][0]['consumed_qty']==INPUT['parts'] and not row['railway_handback_authorised']
        result=dict(repair=repair.name,issue=issue.name,priority=issue.priority,consumed=row['parts'][0]['consumed_qty'],status=row['status'],railway_release=False)
    elif phase=='stock-audit':
        source=INPUT['source']
        def qty(item,warehouse):return frappe.db.get_value('Bin',{'item_code':item,'warehouse':warehouse},'actual_qty') or 0
        result=dict(raw_remaining=qty(source['raw'],source['warehouse']),
            finished_in_stores=qty(source['item'],source['warehouse']),installed=qty(source['item'],source['installed_warehouse']),
            returned=qty(source['item'],source['return_warehouse']))
    elif phase=='control-audit':
        from collections import Counter
        rows=frappe.get_list('Task',filters={'project':INPUT['project']},fields=['status'],limit_page_length=0)
        result=dict(tasks=dict(Counter(r.status for r in rows)),
            issues=frappe.db.count('Issue',{'project':INPUT['project']}),
            work_orders=frappe.db.count('Work Order',{'project':INPUT['project']}),
            stock_entries=frappe.db.count('Stock Entry',{'project':INPUT['project']}))
    elif phase=='case':
        issue=frappe.get_doc('Issue',INPUT['issue'])
        result=dict(issue=issue.name,priority=issue.priority,description=issue.description,project=issue.project)
    elif phase=='snapshot':
        from osr_erpnext.city_runtime import export_snapshots
        export_snapshots('/tmp/example-snapshot.json')
        with open('/tmp/example-snapshot.json') as f:result=json.load(f)
    elif phase=='task-change':
        from osr_erpnext.api import import_file
        project=frappe.get_doc('Project',INPUT['project'])
        row=frappe.get_list('Task',filters={'project':project.name},fields=['name'],limit_page_length=1)[0]
        task=frappe.get_doc('Task',row.name);task.progress=42;task.status='Working';task.save()
        imported=import_file(INPUT['path'],project.company);task.reload()
        assert task.progress==42 and task.status=='Working' and imported['project']==project.name
        result=dict(task=task.name,progress=task.progress,status=task.status,reimport_preserved=True)
    elif phase=='audit-plan':
        rows=frappe.get_list('Task',filters={'project':INPUT['project']},fields=['name','subject','exp_start_date','exp_end_date','department'],limit_page_length=0)
        row=next(r for r in rows if 'Example approved calendar check' in r.subject)
        result=dict(project=INPUT['project'],start=str(row.exp_start_date),end=str(row.exp_end_date),department=row.department,
            tasks=len(rows),warehouse=frappe.db.exists('Warehouse',{'warehouse_name':'OSR samawah Example Spares'}))
    elif phase=='expansion-audit':
        source=INPUT['source']
        types=['Item','Work Order','Quality Inspection','Asset Maintenance','Training Program','Training Event','Training Result','Employee','Budget','Issue','Assignment Rule','Payment Entry','GL Entry','Payment Ledger Entry','Material Request','Stock Entry','Stock Ledger Entry','Purchase Invoice','Task','ToDo','User','DocShare','Item Reorder']
        result=dict(counts={dt:frappe.db.count(dt) for dt in types},auto_indent=frappe.db.get_single_value('Stock Settings','auto_indent'),invoice_outstanding=frappe.db.get_value('Purchase Invoice',source['invoice'],'outstanding_amount'),inspection_required=frappe.db.get_value('Item',source['raw'],'inspection_required_before_purchase'))
    else:raise ValueError('Unknown example phase')
    frappe.db.commit()
    print('OSR_RESULT:'+json.dumps(result,default=str))
except BaseException:
    frappe.db.rollback();raise
finally:frappe.destroy()
