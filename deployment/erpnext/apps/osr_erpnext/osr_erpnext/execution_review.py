"""Native ERP reader for repeatable, project-scoped revision exposure snapshots."""
import frappe
from osr_erpnext.execution_impact import revision_review


def execution_reviews(project, mappings):
    if not mappings:
        return []
    visibility, cache = {}, {}

    def readable(doctype):
        allowed = frappe.has_permission(doctype, 'read')
        visibility[doctype] = 'visible-to-current-user' if allowed else 'permission-denied'
        return allowed

    bom_allowed = readable('BOM')

    def bom(name):
        if name not in cache:
            cache[name] = None
            if bom_allowed:
                try:
                    doc = frappe.get_doc('BOM', name)
                    doc.check_permission('read')
                    if doc.company == project.company:
                        cache[name] = dict(name=doc.name, item=doc.item, modified=str(doc.modified),
                            docstatus=doc.docstatus, is_active=doc.is_active, quantity=doc.quantity,
                            uom=doc.uom, items=[dict(item=r.item_code, bom=r.bom_no,
                                qty=r.qty, uom=r.uom, stock_qty=r.stock_qty, stock_uom=r.stock_uom,
                                do_not_explode=bool(r.do_not_explode)) for r in doc.items])
                except (frappe.PermissionError, frappe.DoesNotExistError):
                    pass
        return cache[name]

    orders, work, stock = [], [], []
    if readable('Purchase Order'):
        names = {}
        base = [['Purchase Order', 'company', '=', project.company],
                ['Purchase Order', 'docstatus', '!=', 2]]
        # A parent project is inherited only by lines without their own project.
        queries = [[['Purchase Order Item', 'project', '=', project.name]]]
        if frappe.get_meta('Purchase Order').has_field('project'):
            queries.append([['Purchase Order', 'project', '=', project.name]])
        for query in queries:
            names.update({r.name: r for r in frappe.get_list('Purchase Order', filters=base + query,
                fields=['name'], distinct=True, order_by='name', limit_page_length=0)})
        for name in sorted(names):
            doc = frappe.get_doc('Purchase Order', name)
            doc.check_permission('read')
            for row in doc.items:
                if (row.get('project') or doc.get('project')) != project.name:
                    continue
                orders.append(dict(document=doc.name, line=row.name, item=row.item_code,
                    docstatus=doc.docstatus, status=doc.status, modified=str(doc.modified),
                    qty=row.qty, received_qty=row.received_qty, uom=row.uom,
                    unreceived_qty=max(0, row.qty - row.received_qty),
                    actionable=doc.docstatus == 0 or doc.status not in ('Closed', 'Completed')))
    if readable('Work Order'):
        for row in frappe.get_list('Work Order', filters={'company': project.company,
                'project': project.name, 'docstatus': ['!=', 2]}, fields=['name'],
                order_by='name', limit_page_length=0):
            doc = frappe.get_doc('Work Order', row.name)
            doc.check_permission('read')
            work.append(dict(name=doc.name, item=doc.production_item, bom=doc.bom_no,
                docstatus=doc.docstatus, status=doc.status, modified=str(doc.modified),
                planned_qty=doc.qty, produced_qty=doc.produced_qty, uom=doc.stock_uom,
                remaining_qty=max(0, doc.qty - doc.produced_qty),
                actionable=doc.docstatus == 0 or doc.status not in ('Completed', 'Stopped', 'Closed'),
                materials=[dict(item=r.item_code, required_qty=r.required_qty,
                    transferred_qty=r.transferred_qty, consumed_qty=r.consumed_qty,
                    returned_qty=r.returned_qty, uom=r.stock_uom) for r in doc.required_items]))
    if readable('Stock Entry') and work:
        for row in frappe.get_list('Stock Entry', filters={'company': project.company,
                'work_order': ['in', [r['name'] for r in work]], 'docstatus': 1},
                fields=['name'], order_by='name', limit_page_length=0):
            doc = frappe.get_doc('Stock Entry', row.name)
            doc.check_permission('read')
            if doc.project and doc.project != project.name:
                continue
            stock.append(dict(name=doc.name, work_order=doc.work_order, purpose=doc.purpose,
                modified=str(doc.modified), posting_date=str(doc.posting_date),
                lines=[dict(line=r.name, item=r.item_code, qty=r.transfer_qty, uom=r.stock_uom,
                    source_warehouse=r.s_warehouse, target_warehouse=r.t_warehouse,
                    serial_and_batch_bundle=r.serial_and_batch_bundle,
                    quality_inspection=r.quality_inspection) for r in doc.items
                    if (r.project or doc.project or project.name) == project.name]))
    scope = dict(project=project.name, city=project.custom_osr_city, company=project.company)
    return [revision_review(mapping, bom, orders, work, stock, visibility, scope)
            for mapping in sorted(mappings, key=lambda r: r['name'])]
