"""Native evidence checks; statuses describe business evidence, never railway release."""
from datetime import datetime
from math import isclose, isfinite


def require(condition, message):
    if not condition:
        raise ValueError(message)


def later(record, endorsed_at):
    require(datetime.fromisoformat(record['modified']) > datetime.fromisoformat(endorsed_at),
            'Native evidence must be updated after endorsement')


def same_scope(record, scope):
    require(record['company'] == scope['company'], 'Evidence company mismatch')


def equal_qty(a, b):
    return isfinite(a) and isfinite(b) and isclose(a, b, rel_tol=1e-9, abs_tol=1e-9)


def inspection(record, reference_type, reference, item, scope, endorsed_at):
    same_scope(record, scope)
    require(record['docstatus'] == 1 and record['reference_type'] == reference_type and
            record['reference_name'] == reference and record['item'] == item,
            'Submitted inspection must reference the exact native record and Item')
    later(record, endorsed_at)
    require(record['sample_size'] > 0 and record['inspected_by'] and record['readings'],
            'Inspection requires a sample, inspector and performed readings')
    for row in record['readings']:
        require(row['specification'] and row['status'] in {'Accepted', 'Rejected'}, 'Incomplete inspection readings')
        fields = ['reading_' + str(i) for i in range(1, 11)] if row['numeric'] else ['reading_value']
        require(any(row.get(k) is not None and str(row[k]).strip() != '' for k in fields),
                'Inspection contains no measured reading')
    require(record['status'] in {'Accepted', 'Rejected'}, 'Inspection has no result')
    if record['status'] == 'Accepted':
        require(all(r['status'] == 'Accepted' for r in record['readings']), 'Accepted inspection has rejected readings')


def amendment(before, after, target, native, evidence, endorsed_at):
    original, replacement = evidence['original'], evidence['replacement']
    same_scope(replacement, before['scope'])
    require(native['docstatus'] == original['docstatus'] == 2 and replacement['docstatus'] == 1 and
            replacement['amended_from'] == target['document'], 'A submitted direct amendment of the cancelled order is required')
    later(replacement, endorsed_at)
    later(original, endorsed_at)
    for doc in [original, replacement]:
        require(doc['lines'] and all(r['project'] == before['scope']['project'] for r in doc['lines']),
                'Amendment verification requires all order lines in the selected project')
    exposed = [r for r in before['purchase_orders'] if r['document'] == target['document']]
    require(any(r['line'] == target['line'] and r['docstatus'] == 1 for r in exposed), 'Reviewed submitted purchase line is missing')
    for row in exposed:
        actual = next((r for r in original['lines'] if r['line'] == row['line']), None)
        require(actual and all(actual[k] == row[k] for k in ['item', 'qty', 'received_qty', 'uom']),
                'Original purchase line changed since endorsement')
    # Substitution needs a new engineering mapping, not an inferred item equivalence.
    require(sorted((r['item'], r['uom']) for r in original['lines']) ==
            sorted((r['item'], r['uom']) for r in replacement['lines']), 'Item substitution requires a new engineering review')
    require(all(r['qty'] > 0 and r['received_qty'] == 0 for r in replacement['lines']),
            'Amendment must precede receiving')
    require(not any(r['document'] == replacement['name'] for r in before['purchase_orders']),
            'Replacement order already existed in the endorsed exposure')
    replacement_rows = [r for r in after['purchase_orders'] if r['document'] == replacement['name']]
    require(replacement_rows, 'Replacement order is not visible in current exposure')
    for row in replacement_rows:
        actual = next((r for r in replacement['lines'] if r['line'] == row['line']), None)
        require(actual and all(actual[k] == row[k] for k in ['item', 'qty', 'received_qty', 'uom']) and
                row['docstatus'] == 1 and row['modified'] == replacement['modified'], 'Amended order changed during observation')
    before['purchase_orders'] = [r for r in before['purchase_orders'] if r['document'] != target['document']]
    after['purchase_orders'] = [r for r in after['purchase_orders'] if r['document'] != replacement['name']]
    return 'Native amendment verified'


def rework(before, after, target, native, evidence, endorsed_at):
    original = next((r for r in before['work_orders'] if r['name'] == target['document']), None)
    observed = next((r for r in after['work_orders'] if r['name'] == target['document']), None)
    require(original and observed and original['docstatus'] == native['docstatus'] == 1,
            'Rework requires the reviewed submitted Work Order')
    card, source = evidence['job_card'], evidence['original_job']
    for row in [card, source]:
        same_scope(row, before['scope'])
        require(row['work_order'] == target['document'] and row['bom'] == original['bom'] and
                row['item'] == original['item'] and row['project'] == before['scope']['project'],
                'Job Card does not match the reviewed project, Work Order and BOM')
    require(source['docstatus'] == 1 and card['for_job_card'] == source['name'] and card['corrective'] and
            card['for_operation'] == source['operation'], 'Rework must be a native corrective Job Card linked to the original operation')
    require(card['docstatus'] == 1 and card['status'] == 'Completed' and card['qty'] > 0 and
            equal_qty(card['completed_qty'], card['qty']) and card['process_loss_qty'] == 0,
            'Corrective work is not fully completed without process loss')
    require(card['qty'] <= original['planned_qty'] and card['time_logs'] and
            all(r['minutes'] > 0 and r['from_time'] not in ('', 'None') and r['to_time'] not in ('', 'None') for r in card['time_logs']),
            'Corrective work requires performed time logs and a bounded quantity')
    later(card, endorsed_at)
    require(len(evidence['inspections']) == 1, 'Select the corrective Job Card inspection')
    qa = evidence['inspections'][0]
    inspection(qa, 'Job Card', card['name'], card['item'], before['scope'], endorsed_at)
    require(qa['status'] == 'Accepted' and card['quality_inspection'] == qa['name'],
            'Corrective work requires its linked accepted native inspection')
    # Job Card costing may update the WO timestamp. Quantities/materials must be unchanged.
    observed['modified'] = original['modified']
    return 'Corrective work and inspection verified'


def inspect_stock(before, after, target, native, evidence, endorsed_at):
    original = next((r for r in before['stock_movements'] if r['name'] == target['document']), None)
    observed = next((r for r in after['stock_movements'] if r['name'] == target['document']), None)
    require(original and observed and native['docstatus'] == 1, 'Reviewed submitted Stock Entry is required')
    require(observed['lines'] == native['lines'] and observed['modified'] == native['modified'],
            'Stock Entry changed during inspection observation')
    inspections = evidence['inspections']
    require(len(inspections) == len(original['lines']), 'An inspection is required for every reviewed stock line')
    used = set()
    for line in original['lines']:
        matches = [q for q in inspections if q['line'] == line['line']]
        require(len(matches) == 1, 'Each stock line needs one exact-row inspection')
        qa = matches[0]; used.add(qa['name'])
        inspection(qa, 'Stock Entry', target['document'], line['item'], before['scope'], endorsed_at)
        current_line = next((r for r in observed['lines'] if r['line'] == line['line']), None)
        require(current_line and current_line['quality_inspection'] == qa['name'], 'Inspection is not linked on the exact stock line')
        current_line['quality_inspection'] = line['quality_inspection']
    require(len(used) == len(inspections), 'Duplicate inspection evidence')
    observed['modified'] = original['modified']
    return 'Inspection recorded: rejected' if any(q['status'] == 'Rejected' for q in inspections) else 'Inspection recorded: accepted'


def material_trace(before, target, native, evidence):
    original = next((r for r in before['stock_movements'] if r['name'] == target['document']), None)
    require(native['docstatus'] == 1 and original,
            'Reviewed submitted Stock Entry is required')
    require(original['lines'] == native['lines'] and original['modified'] == native['modified'],
            'Stock movement changed during trace observation')
    expected, actual = {}, {}
    for row in native['lines']:
        item = next((r for r in evidence['items'] if r['name'] == row['item']), None)
        require(item and item['stock_uom'] == row['uom'], 'Stock Item or unit is unavailable')
        for field, sign in [('source_warehouse', -1), ('target_warehouse', 1)]:
            if row[field]:
                key = (row['line'], row['item'], row[field])
                expected[key] = expected.get(key, 0) + sign * row['qty']
        if item['has_serial_no'] or item['has_batch_no']:
            require(row['serial_and_batch_bundle'], 'Serialized/batched movement has no bundle')
        if row['serial_and_batch_bundle']:
            bundle = next((b for b in evidence['bundles'] if b['name'] == row['serial_and_batch_bundle']), None)
            require(bundle and bundle['docstatus'] == 1 and not bundle['cancelled'] and
                    bundle['company'] == before['scope']['company'] and bundle['item'] == row['item'] and
                    bundle['voucher_type'] == 'Stock Entry' and bundle['voucher_no'] == native['name'] and
                    bundle['line'] == row['line'], 'Serial/batch bundle identity mismatch')
            require(bundle['entries'] and equal_qty(abs(sum(r['qty'] for r in bundle['entries'])), row['qty']),
                    'Serial/batch quantities do not reconcile')
            require(all(r['qty'] != 0 for r in bundle['entries']) and
                    equal_qty(sum(abs(r['qty']) for r in bundle['entries']), row['qty']),
                    'Serial/batch quantities have inconsistent signs')
            serials = [r['serial_no'] for r in bundle['entries'] if r['serial_no']]
            require(len(serials) == len(set(serials)), 'Duplicate serial identity in a movement')
            for entry in bundle['entries']:
                require((not item['has_serial_no'] or entry['serial_no']) and
                        (not item['has_batch_no'] or entry['batch_no']), 'Serial/batch identity is missing')
                require(not item['has_serial_no'] or equal_qty(abs(entry['qty']), 1), 'Serial quantities must be one per identity')
    for row in evidence['ledger']:
        same_scope(row, before['scope'])
        key = (row['line'], row['item'], row['warehouse'])
        actual[key] = actual.get(key, 0) + row['qty']
    require(expected and expected.keys() == actual.keys() and all(equal_qty(expected[k], actual[k]) for k in expected),
            'Permission-visible stock ledger does not reconcile with every movement line')
    for row in evidence['ledger']:
        if row.get('serial_and_batch_bundle'):
            bundle = next((b for b in evidence['bundles'] if b['name'] == row['serial_and_batch_bundle']), None)
            require(bundle and bundle['docstatus'] == 1 and not bundle['cancelled'] and
                    bundle['company'] == before['scope']['company'] and bundle['voucher_type'] == 'Stock Entry' and
                    bundle['voucher_no'] == native['name'] and bundle['line'] == row['line'] and
                    bundle['item'] == row['item'] and bundle['warehouse'] == row['warehouse'] and
                    equal_qty(bundle['qty'], row['qty']), 'Ledger serial/batch bundle does not reconcile')
    return 'Native movement trace verified'
