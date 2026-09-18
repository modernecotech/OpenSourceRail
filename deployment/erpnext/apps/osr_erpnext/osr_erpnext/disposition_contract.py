"""Typed business-disposition proposals. A recorded plan never executes an ERP action."""
from datetime import date
import re
from osr_erpnext.planning import digest

ACTIONS = {
    'purchase-line': ['Retain for review', 'Request amendment', 'Request cancellation'],
    'work-order': ['Retain for review', 'Request production stop', 'Request rework'],
    'stock-entry': ['Request inspection', 'Request material trace'],
}


def text(value, label, maximum=1000):
    if not isinstance(value, str) or not value.strip() or len(value) > maximum:
        raise ValueError('Invalid ' + label)
    return value.strip()


def evidence(value):
    if not isinstance(value, list) or not 1 <= len(value) <= 20:
        raise ValueError('Provide 1–20 versioned evidence references')
    return [text(row, 'evidence reference') for row in value]


def proposal(value):
    required = {'key', 'mapping', 'target', 'action', 'responsible', 'due_date', 'rationale', 'references'}
    if not isinstance(value, dict) or set(value) != required:
        raise ValueError('Invalid disposition proposal fields')
    result = {k: text(value[k], k, 4000 if k == 'rationale' else 140)
              for k in required - {'target', 'references'}}
    if not re.fullmatch(r'[A-Za-z0-9_-]{1,64}', result['key']):
        raise ValueError('Invalid proposal key')
    if date.fromisoformat(result['due_date']).isoformat() != result['due_date']:
        raise ValueError('Invalid due date')
    target = value['target']
    if not isinstance(target, dict) or target.get('kind') not in ACTIONS:
        raise ValueError('Unsupported disposition target')
    fields = {'kind', 'document'} | ({'line'} if target['kind'] == 'purchase-line' else set())
    if set(target) != fields:
        raise ValueError('Invalid target identity')
    result['target'] = {k: text(target[k], k, 140) for k in fields}
    if result['action'] not in ACTIONS[target['kind']]:
        raise ValueError('Action is not applicable to this record type')
    result['references'] = evidence(value['references'])
    return result


def targets(review):
    result = []
    for row in review['purchase_orders']:
        result.append(dict(target=dict(kind='purchase-line', document=row['document'], line=row['line']), record=row))
    for group, kind in [('work_orders', 'work-order'), ('stock_movements', 'stock-entry')]:
        result.extend(dict(target=dict(kind=kind, document=row['name']), record=row) for row in review[group])
    return result


def plan(review, request, actor):
    if review['mapping']['name'] != request['mapping']:
        raise ValueError('Execution mapping mismatch')
    selected = next((row for row in targets(review) if row['target'] == request['target']), None)
    if not selected:
        raise ValueError('Target is outside the current visible revision exposure')
    result = dict(proposal=request, proposer=actor, scope=review['scope'],
                  exposure_sha256=review['sha256'], target_record=selected['record'],
                  warnings=review['warnings'], automatic_execution=False, railway_release_authorised=False)
    result['fingerprint'] = digest(result)
    return result


def decision(value):
    if not isinstance(value, dict) or set(value) != {'outcome', 'rationale', 'references'}:
        raise ValueError('Invalid decision fields')
    if value['outcome'] not in {'Endorse plan', 'Reject plan'}:
        raise ValueError('Unsupported disposition decision')
    return dict(outcome=value['outcome'], rationale=text(value['rationale'], 'rationale', 4000),
                references=evidence(value['references']))
