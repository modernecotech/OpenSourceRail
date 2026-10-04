"""Planning eligibility checks; evidence inputs must come from controlled records.

This evaluator grants no railway authority, creates no assignment and does not
turn attendance into competence. Re-evaluate at both planning and task start.
"""
from datetime import datetime
import math

def moment(value):
    result = datetime.fromisoformat(value)
    if result.tzinfo is None:
        raise ValueError('Use timezone-aware timestamps')
    return result

def assignment_eligibility(worker, task, resources, at_time):
    now = moment(at_time)
    reasons = []
    idle_limit = task.get('maximum_skill_idle_days')
    if isinstance(idle_limit, bool) or not isinstance(idle_limit, (int, float)) or not math.isfinite(idle_limit) or idle_limit <= 0:
        reasons.append('invalid-skill-idle-policy')
        idle_limit = 0
    if task.get('independent_verification_required') is not True and task.get('independent_verification_required') is not False:
        reasons.append('unverified-independent-verification-policy')
    required = ('worker_id', 'native_employee', 'evidence_revision')
    if not all(worker.get(k) for k in required):
        reasons.append('missing-controlled-worker-record')
    if worker.get('available') is not True or worker.get('suspended') is not False:
        reasons.append('worker-unavailable-or-suspended')
    if worker.get('rest_checked') is not True or worker.get('rest_compliant') is not True:
        reasons.append('rest-unverified-or-failed')
    if worker.get('location') != task.get('location'):
        reasons.append('wrong-location')
    matching = []
    for authorisation in worker.get('authorisations', []):
        scope = all(authorisation.get(k) == task.get(k) and task.get(k) for k in ('task_kind', 'asset_family', 'location', 'method_revision'))
        evidence = all(authorisation.get(k) for k in ('assessment_record', 'assessor', 'authority_record', 'issued_by')) and authorisation.get('accepted') is True
        valid = False
        try:
            valid = moment(authorisation['valid_from']) <= now < moment(authorisation['expires_at'])
            idle = (now-moment(authorisation['last_practical_use'])).total_seconds()/86400
            valid = valid and 0 <= idle < idle_limit
        except (KeyError, TypeError, ValueError):
            valid = False
        if scope and evidence and valid and authorisation.get('suspended') is False:
            matching.append(authorisation)
    if not matching:
        reasons.append('no-current-assessed-task-authorisation')
    required_resources = ['access', 'permit', 'tools', 'materials', 'supervisor']
    if task.get('independent_verification_required'):
        required_resources.append('verifier')
    for item in required_resources:
        record = resources.get(item, {})
        try:
            valid = record.get('accepted') is True and record.get('record_id') and moment(record['valid_from']) <= now < moment(record['expires_at'])
        except (KeyError, TypeError, ValueError):
            valid = False
        if not valid:
            reasons.append('missing-or-expired-'+item)
    if task.get('independent_verification_required'):
        verifier = resources.get('verifier', {})
        if not verifier.get('worker_id') or verifier.get('worker_id') == worker.get('worker_id'):
            reasons.append('independent-verifier-unavailable')
    return {'eligible': not reasons, 'reasons': reasons, 'checked_at': at_time,
            'worker_id': worker.get('worker_id'), 'method_revision': task.get('method_revision'),
            'evidence_revision': worker.get('evidence_revision'), 'creates_assignment': False,
            'operational_release': False}
