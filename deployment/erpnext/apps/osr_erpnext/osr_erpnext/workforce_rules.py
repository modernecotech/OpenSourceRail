"""Validate controlled resource snapshots; never grant live work or railway release."""
from datetime import datetime
import math

SCOPE = ('task_kind', 'asset_family', 'location', 'method_revision')
RESOURCE_SCOPE = ('task_id', 'asset_id', 'location', 'method_revision')

def moment(value):
    result = datetime.fromisoformat(value)
    if result.tzinfo is None:
        raise ValueError('Use timezone-aware timestamps')
    return result

def finite(value):
    return not isinstance(value, bool) and isinstance(value, (int, float)) and math.isfinite(value)

def current(record, now):
    try:
        return (record.get('accepted') is True and bool(record.get('record_id'))
                and record.get('revoked') is False
                and moment(record['valid_from']) <= now < moment(record['expires_at']))
    except (KeyError, TypeError, ValueError):
        return False

def person_reasons(worker, task, now, idle_limit, responsibility):
    reasons = []
    if not all(worker.get(k) for k in ('worker_id', 'native_employee', 'evidence_revision')):
        reasons.append('missing-controlled-worker-record')
    if worker.get('available') is not True or worker.get('suspended') is not False:
        reasons.append('worker-unavailable-or-suspended')
    if worker.get('rest_checked') is not True or worker.get('rest_compliant') is not True:
        reasons.append('rest-unverified-or-failed')
    if worker.get('location') != task.get('location'):
        reasons.append('wrong-location')
    matched = False
    for auth in worker.get('authorisations', []):
        scope = all(auth.get(k) == task.get(k) and task.get(k) for k in SCOPE)
        evidence = (all(auth.get(k) for k in ('assessment_record', 'assessor', 'authority_record', 'issued_by'))
                    and auth.get('accepted') is True and auth.get('responsibility') == responsibility)
        try:
            idle = (now - moment(auth['last_practical_use'])).total_seconds() / 86400
            valid = moment(auth['valid_from']) <= now < moment(auth['expires_at']) and 0 <= idle < idle_limit
        except (KeyError, TypeError, ValueError):
            valid = False
        if scope and evidence and valid and auth.get('suspended') is False and auth.get('revoked') is False:
            matched = True
    if not matched:
        reasons.append('no-current-assessed-task-authorisation')
    return reasons

def assignment_eligibility(worker, task, resources, at_time):
    now = moment(at_time)
    reasons = []
    idle_limit = task.get('maximum_skill_idle_days')
    if not finite(idle_limit) or idle_limit <= 0:
        reasons.append('invalid-skill-idle-policy')
        idle_limit = 0
    if task.get('independent_verification_required') not in (True, False) or not isinstance(task.get('independent_verification_required'), bool):
        reasons.append('unverified-independent-verification-policy')
    if not all(isinstance(task.get(k), str) and task[k].strip() for k in (*SCOPE, 'task_id', 'asset_id', 'isolation_scope')):
        reasons.append('missing-controlled-task-scope')
    reasons.extend(person_reasons(worker, task, now, idle_limit, 'perform'))
    required = ['access', 'permit', 'tools', 'materials', 'supervisor']
    if task.get('independent_verification_required'):
        required.append('verifier')
    for item in required:
        record = resources.get(item, {})
        if not current(record, now):
            reasons.append('missing-or-expired-' + item)
        keys = (*RESOURCE_SCOPE, 'asset_family', 'isolation_scope') if item in ('access', 'permit') else RESOURCE_SCOPE
        if not all(record.get(k) == task.get(k) and task.get(k) for k in keys):
            reasons.append('wrong-resource-scope-' + item)
        if item in ('supervisor', 'verifier'):
            role = 'supervise' if item == 'supervisor' else 'verify'
            if record.get('qualified') is not True or person_reasons(record, task, now, idle_limit, role):
                reasons.append('unavailable-or-unauthorised-' + item)
    if task.get('independent_verification_required'):
        verifier = resources.get('verifier', {})
        if (verifier.get('independent') is not True or not verifier.get('independence_record')
                or verifier.get('worker_id') in (None, worker.get('worker_id'), resources.get('supervisor', {}).get('worker_id'))
                or verifier.get('native_employee') in (None, worker.get('native_employee'), resources.get('supervisor', {}).get('native_employee'))):
            reasons.append('independent-verifier-unavailable')
    tools = task.get('required_tools')
    if not isinstance(tools, list):
        reasons.append('unverified-tool-requirements')
    else:
        for need in tools:
            if not all(need.get(k) for k in ('tool_type', 'unit')) or not all(finite(need.get(k)) for k in ('range_min', 'range_max')) or need['range_min'] > need['range_max']:
                reasons.append('invalid-tool-requirement')
                continue
            matched = False
            for tool in resources.get('tools', {}).get('items', []):
                try:
                    calibrated = (tool.get('calibration_record') and tool.get('calibration_revoked') is False
                        and moment(tool['calibration_valid_from']) <= now < moment(tool['calibration_expires_at']))
                except (KeyError, TypeError, ValueError):
                    calibrated = False
                if (tool.get('tool_type') == need['tool_type'] and tool.get('unit') == need['unit']
                        and tool.get('serial_number') and tool.get('accepted') is True and tool.get('revoked') is False
                        and all(finite(tool.get(k)) for k in ('range_min', 'range_max'))
                        and tool['range_min'] <= need['range_min'] <= need['range_max'] <= tool['range_max'] and calibrated):
                    matched = True
            if not matched:
                reasons.append('missing-correct-calibrated-tool')
    materials = task.get('required_materials')
    if not isinstance(materials, list):
        reasons.append('unverified-material-requirements')
    else:
        lots=resources.get('materials', {}).get('items', [])
        lot_ids=[part.get('stock_record') for part in lots]
        if any(not item for item in lot_ids) or len(set(lot_ids))!=len(lot_ids):
            reasons.append('missing-or-duplicate-material-stock-record')
        required_parts=[tuple(part.get(k) for k in ('part_id','revision','unit')) for part in materials]
        if len(set(required_parts))!=len(required_parts):
            reasons.append('duplicate-material-requirement')
        for need in materials:
            if not all(need.get(k) for k in ('part_id', 'revision', 'unit')) or not finite(need.get('quantity')) or need['quantity'] <= 0:
                reasons.append('invalid-material-requirement')
                continue
            # Released matching lots may jointly cover the required quantity.
            quantity = sum(part['available_quantity'] for part in resources.get('materials', {}).get('items', [])
                if all(part.get(k) == need[k] for k in ('part_id', 'revision', 'unit'))
                and part.get('release_status') == 'Released' and part.get('release_record')
                and part.get('accepted') is True and part.get('stock_record')
                and part.get('revoked') is False and finite(part.get('available_quantity')) and part['available_quantity'] >= 0)
            if quantity < need['quantity']:
                reasons.append('missing-released-material-quantity')
    return dict(eligible=not reasons, reasons=list(dict.fromkeys(reasons)), checked_at=at_time,
        worker_id=worker.get('worker_id'), method_revision=task.get('method_revision'),
        evidence_revision=worker.get('evidence_revision'), evidence_scope='controlled-attached-snapshot',
        authoritative_revocation_resolved=False, creates_assignment=False, operational_release=False)
