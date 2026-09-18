"""Bounded native outcome checks against the complete reviewed exposure."""
from copy import deepcopy
from datetime import datetime
import hashlib
import json
import re
from osr_erpnext.disposition_contract import text, evidence

from osr_erpnext import outcome_checks as checks

# One registry drives the authenticated UI and strict native evidence selection.
VERIFIERS = {
    'Request cancellation': dict(doctype='Purchase Order', fields=[], description='Cancelled native order; unchanged reviewed quantities.'),
    'Request production stop': dict(doctype='Work Order', fields=[], description='Stopped native Work Order; unchanged quantities and materials.'),
    'Request amendment': dict(doctype='Purchase Order', fields=[dict(key='purchase_order', label='Submitted amended Purchase Order', doctype='Purchase Order')],
        description='Direct submitted amendment, same Items/units and project. Review all replacement quantities, prices and dates.'),
    'Request rework': dict(doctype='Work Order', fields=[dict(key='job_card', label='Completed corrective Job Card', doctype='Job Card'),
        dict(key='quality_inspections', label='Accepted corrective Quality Inspection', doctype='Quality Inspection', multiple=True)],
        description='Completed corrective Job Card and its accepted inspection. Verifies only the displayed corrective quantity and inspection sample.'),
    'Request inspection': dict(doctype='Stock Entry', fields=[dict(key='quality_inspections', label='Submitted Quality Inspections (one per stock line)', doctype='Quality Inspection', multiple=True)],
        description='Performed native readings for every reviewed stock line. Rejected results remain rejected.'),
    'Request material trace': dict(doctype='Stock Entry', fields=[],
        description='Reconcile this movement with native ledger and serial/batch bundles. Does not establish current stock or installed identity.'),
    'Retain for review': dict(doctype=None, fields=[], description='Record independent retention review while the complete exposure is unchanged. No hold or release is imposed.'),
}
SUPPORTED = {action: row['doctype'] for action, row in VERIFIERS.items()}


def selected_records(action, value):
    fields = VERIFIERS[action]['fields']
    if not isinstance(value, dict) or set(value) != {f['key'] for f in fields}:
        raise ValueError('Provide exactly the native records required by this action')
    result = {}
    for field in fields:
        row = value[field['key']]
        if field.get('multiple'):
            if not isinstance(row, list) or not 1 <= len(row) <= 100:
                raise ValueError('Provide 1–100 native inspection names')
            row = sorted(text(n, 'native document', 140) for n in row)
            if len(set(row)) != len(row):
                raise ValueError('Duplicate native inspection')
        else:
            row = text(row, 'native document', 140)
        result[field['key']] = row
    return result


def request(value):
    if not isinstance(value, dict) or set(value) not in ({'key', 'rationale', 'references'}, {'key', 'rationale', 'references', 'records'}):
        raise ValueError('Invalid outcome verification fields')
    key = text(value['key'], 'verification key', 64)
    if not re.fullmatch(r'[A-Za-z0-9_-]+', key):
        raise ValueError('Invalid verification key')
    result = dict(key=key, rationale=text(value['rationale'], 'verification rationale', 4000),
                  references=evidence(value['references']))
    if 'records' in value:
        if not isinstance(value['records'], dict):
            raise ValueError('Native records must be an object')
        result['records'] = value['records']
    return result


def _body(review):
    if not isinstance(review, dict) or 'sha256' not in review:
        raise ValueError('Proposal has no complete exposure snapshot; create a new reviewed proposal')
    result = deepcopy(review); checksum = result.pop('sha256')
    expected = hashlib.sha256(json.dumps(result, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()
    if checksum != expected:
        raise ValueError('Exposure snapshot checksum mismatch')
    if result['warnings']:
        raise ValueError('Exposure coverage is incomplete')
    return result


def verify(baseline, current, proposal, native, endorsed_at, evidence=None):
    before, after = _body(baseline), _body(current)
    action, target = proposal['action'], proposal['target']
    if action not in SUPPORTED:
        raise ValueError('This action has no native outcome verifier')
    expected_type = SUPPORTED[action] or {'purchase-line': 'Purchase Order', 'work-order': 'Work Order'}[target['kind']]
    if native['doctype'] != expected_type or native['name'] != target['document']:
        raise ValueError('Native outcome belongs to another record')
    if (native['company'] != before['scope']['company'] or
            native['project'] != before['scope']['project']):
        raise ValueError('Native outcome scope mismatch')
    if action in {'Request cancellation', 'Request production stop'} and datetime.fromisoformat(native['modified']) <= datetime.fromisoformat(endorsed_at):
        raise ValueError('Native outcome must be observed after endorsement')
    status = 'Native outcome verified'
    if action == 'Request amendment':
        status = checks.amendment(before, after, target, native, evidence, endorsed_at)
    elif action == 'Request rework':
        status = checks.rework(before, after, target, native, evidence, endorsed_at)
    elif action == 'Request inspection':
        status = checks.inspect_stock(before, after, target, native, evidence, endorsed_at)
    elif action == 'Request material trace':
        status = checks.material_trace(before, target, native, evidence)
    elif action == 'Retain for review':
        group = 'purchase_orders' if target['kind'] == 'purchase-line' else 'work_orders'
        row = next((r for r in after[group] if (r.get('document') or r.get('name')) == target['document'] and
                    (target['kind'] != 'purchase-line' or r['line'] == target['line'])), None)
        checks.require(row and all(row[k] == native[k] for k in ['docstatus', 'status', 'modified']),
                       'Retained native record changed during observation')
        status = 'Retention review recorded'
    elif action == 'Request cancellation':
        if target['kind'] != 'purchase-line' or native['docstatus'] != 2:
            raise ValueError('Purchase Order has not been cancelled')
        affected = [r for r in before['purchase_orders'] if r['document'] == target['document']]
        if not any(r['line'] == target['line'] and r['docstatus'] == 1 for r in affected):
            raise ValueError('Reviewed submitted purchase line is missing')
        # A cancelled document is excluded from the live exposure. Verify its
        # original visible lines directly before removing only that document.
        for row in affected:
            line = next((r for r in native['lines'] if r['line'] == row['line']), None)
            if not line or any(line[k] != row[k] for k in ['item', 'qty', 'received_qty', 'uom']):
                raise ValueError('Cancelled purchase lines differ from the endorsed plan')
        before['purchase_orders'] = [r for r in before['purchase_orders'] if r['document'] != target['document']]
    else:
        original = next((r for r in before['work_orders'] if r['name'] == target['document']), None)
        observed = next((r for r in after['work_orders'] if r['name'] == target['document']), None)
        if (target['kind'] != 'work-order' or not original or not observed or
                original['docstatus'] != 1 or original['status'] == 'Stopped' or
                native['docstatus'] != 1 or native['status'] != 'Stopped' or observed['status'] != 'Stopped'):
            raise ValueError('The reviewed submitted Work Order has not changed to Stopped')
        if observed['modified'] != native['modified']:
            raise ValueError('Native Work Order changed during observation')
        for field in ['status', 'modified', 'actionable']:
            observed[field] = original[field]
    if before != after:
        raise ValueError('Other revision exposure changed; a fresh disposition review is required')
    return status
