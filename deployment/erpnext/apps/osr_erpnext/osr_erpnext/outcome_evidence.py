"""Permission-checked native evidence for the reusable disposition verifiers."""
import frappe


def read(doctype, name):
    doc = frappe.get_doc(doctype, name)
    doc.check_permission('read')
    return doc


def identity(doc):
    return dict(doctype=doc.doctype, name=doc.name, company=doc.company,
                docstatus=doc.docstatus, modified=str(doc.modified), modified_by=doc.modified_by)


def purchase(doc):
    return dict(**identity(doc), amended_from=doc.amended_from, supplier=doc.supplier,
        currency=doc.currency, grand_total=doc.grand_total,
        lines=[dict(line=r.name, item=r.item_code, project=r.project or doc.project,
            qty=r.qty, received_qty=r.received_qty, uom=r.uom, rate=r.rate,
            schedule_date=str(r.schedule_date), warehouse=r.warehouse) for r in doc.items])


def inspection(name):
    doc = read('Quality Inspection', name)
    result = dict(**identity(doc), reference_type=doc.reference_type, reference_name=doc.reference_name,
        line=doc.child_row_reference, item=doc.item_code, sample_size=doc.sample_size,
        inspected_by=doc.inspected_by, status=doc.status, template=doc.quality_inspection_template,
        serial_no=doc.item_serial_no, batch_no=doc.batch_no,
        readings=[{k: r.get(k) for k in ['specification', 'status', 'numeric', 'manual_inspection',
            'value', 'min_value', 'max_value', 'reading_value', 'formula_based_criteria',
            'acceptance_formula', *['reading_' + str(i) for i in range(1, 11)]]} for r in doc.readings])
    return result


def job(name):
    doc = read('Job Card', name)
    return dict(**identity(doc), project=doc.project, work_order=doc.work_order,
        bom=doc.bom_no, item=doc.production_item, corrective=bool(doc.is_corrective_job_card),
        for_job_card=doc.for_job_card, for_operation=doc.for_operation, operation=doc.operation,
        qty=doc.for_quantity, completed_qty=doc.total_completed_qty, process_loss_qty=doc.process_loss_qty,
        status=doc.status, quality_inspection=doc.quality_inspection,
        time_logs=[dict(from_time=str(r.from_time), to_time=str(r.to_time),
            minutes=r.time_in_mins, completed_qty=r.completed_qty, employee=r.employee) for r in doc.time_logs])


def stock(doc, project):
    # Mixed-project stock documents cannot receive a whole-document verification.
    if any((r.project or doc.project or project) != project for r in doc.items):
        raise ValueError('Stock Entry contains another project; review it separately')
    work = read('Work Order', doc.work_order)
    if work.project != project or work.company != doc.company:
        raise ValueError('Stock Entry Work Order scope mismatch')
    return dict(**identity(doc), project=project, work_order=doc.work_order, status='Submitted' if doc.docstatus == 1 else 'Unsubmitted',
        lines=[dict(line=r.name, item=r.item_code, qty=r.transfer_qty, uom=r.stock_uom,
            source_warehouse=r.s_warehouse, target_warehouse=r.t_warehouse,
            serial_and_batch_bundle=r.serial_and_batch_bundle,
            quality_inspection=r.quality_inspection) for r in doc.items])


def trace(doc, native):
    if not frappe.has_permission('Stock Ledger Entry', 'read'):
        frappe.throw('Stock Ledger Entry read permission required', frappe.PermissionError)
    ledger = []
    for row in frappe.get_list('Stock Ledger Entry', filters={'voucher_type': 'Stock Entry',
            'voucher_no': doc.name, 'is_cancelled': 0}, fields=['name'], order_by='name', limit_page_length=0):
        record = read('Stock Ledger Entry', row.name)
        ledger.append(dict(name=record.name, company=record.company, line=record.voucher_detail_no,
            item=record.item_code, warehouse=record.warehouse, qty=record.actual_qty,
            serial_and_batch_bundle=record.serial_and_batch_bundle, modified=str(record.modified)))
    bundles = []
    for name in sorted({r['serial_and_batch_bundle'] for r in [*native['lines'], *ledger] if r['serial_and_batch_bundle']}):
        record = read('Serial and Batch Bundle', name)
        bundles.append(dict(**identity(record), item=record.item_code, voucher_type=record.voucher_type,
            voucher_no=record.voucher_no, line=record.voucher_detail_no, cancelled=bool(record.is_cancelled),
            warehouse=record.warehouse, qty=record.total_qty,
            entries=[dict(serial_no=r.serial_no, batch_no=r.batch_no, qty=r.qty,
                          warehouse=r.warehouse) for r in record.entries]))
    items = []
    for name in sorted({r['item'] for r in native['lines']}):
        item = read('Item', name)
        items.append(dict(name=item.name, has_serial_no=bool(item.has_serial_no),
                          has_batch_no=bool(item.has_batch_no), stock_uom=item.stock_uom))
    return dict(ledger=ledger, bundles=bundles, items=items)


def collect(action, doc, native, records):
    if action == 'Request amendment':
        return dict(original=purchase(doc), replacement=purchase(read('Purchase Order', records['purchase_order'])))
    if action == 'Request rework':
        corrective = job(records['job_card'])
        if not corrective['for_job_card']:
            raise ValueError('A corrective Job Card must identify its original Job Card')
        return dict(job_card=corrective, original_job=job(corrective['for_job_card']),
                    inspections=[inspection(n) for n in records['quality_inspections']])
    if action == 'Request inspection':
        return dict(inspections=[inspection(n) for n in records['quality_inspections']])
    if action == 'Request material trace':
        return trace(doc, native)
    return {}
