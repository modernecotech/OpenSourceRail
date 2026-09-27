"""Deterministic governance for multi-model executive recommendations.

Models supply recommendations.  This module supplies the authority boundary:
quorum, independence, dissent, delegation and an operator-owned attestation.
It deliberately contains no model client and grants no SCADA authority.
"""
import hashlib
import hmac
import json
import math
from datetime import datetime

from .config import identifier


PERSPECTIVES = {'strategy', 'finance', 'operations', 'risk'}
VERDICTS = {'endorse', 'reject', 'abstain'}
OFFICES = {
    'ai-chief-executive', 'ai-finance-manager', 'ai-operations-manager',
    'ai-maintenance-manager', 'ai-procurement-manager', 'ai-workforce-planner',
}
DELEGATABLE_ERP_DRAFTS = {
    'erp.draft-budget-scenario',
    'erp.draft-maintenance-plan',
    'erp.draft-material-request',
    'erp.draft-work-order',
}

COMPONENT_DRAFTS = {
    'erp.draft-budget-scenario', 'erp.draft-maintenance-plan', 'erp.draft-work-order',
}


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)


def sha256(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def _text(value, field, maximum, minimum=1):
    if not isinstance(value, str) or not minimum <= len(value.strip()) <= maximum:
        raise ValueError(f'{field} must contain {minimum} to {maximum} characters')
    return value.strip()


def _instant(value, field):
    if not isinstance(value, str):
        raise ValueError(f'{field} must be an ISO 8601 timestamp with timezone')
    parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if parsed.tzinfo is None:
        raise ValueError(f'{field} timezone required')
    return parsed.timestamp()


def validate_policy(policy):
    if not isinstance(policy, dict):
        raise ValueError('Executive council policy is not configured')
    required = set(policy.get('required_perspectives', []))
    if not required or not required <= PERSPECTIVES:
        raise ValueError('Council required perspectives are invalid')
    quorum = policy.get('quorum')
    providers = policy.get('minimum_providers')
    families = policy.get('minimum_model_families')
    ratio = policy.get('approval_ratio')
    if type(quorum) is not int or not 3 <= quorum <= 12:
        raise ValueError('Council quorum must be between 3 and 12')
    if len(required) > quorum:
        raise ValueError('Council quorum cannot satisfy its required perspectives')
    if type(providers) is not int or not 2 <= providers <= quorum:
        raise ValueError('Council requires at least two independent providers')
    if type(families) is not int or not 2 <= families <= quorum:
        raise ValueError('Council requires at least two independent model families')
    if isinstance(ratio, bool) or not isinstance(ratio, (int, float)) or not math.isfinite(ratio) or not .67 <= ratio <= 1:
        raise ValueError('Council approval ratio must be between 0.67 and 1')
    allowed = set(policy.get('delegated_erp_drafts', []))
    if not allowed <= DELEGATABLE_ERP_DRAFTS:
        raise ValueError('Policy attempts to delegate a prohibited action')
    _text(policy.get('policy_id'), 'policy_id', 160)
    _text(policy.get('version'), 'policy version', 80)
    return {
        'policy_id': policy['policy_id'], 'version': policy['version'],
        'quorum': quorum, 'required_perspectives': sorted(required),
        'minimum_providers': providers, 'minimum_model_families': families,
        'approval_ratio': float(ratio), 'delegated_erp_drafts': sorted(allowed),
    }


def validate_proposal(value, now):
    if not isinstance(value, dict):
        raise ValueError('Executive proposal must be an object')
    created = _instant(value.get('created_at'), 'created_at')
    expires = _instant(value.get('expires_at'), 'expires_at')
    if created > now + 300 or expires <= now or expires <= created or expires - created > 30 * 86400:
        raise ValueError('Executive proposal timestamps or lifetime are invalid')
    authority = value.get('requested_authority')
    if authority not in ('advisory', 'delegated-erp-draft'):
        raise ValueError('Requested authority must be advisory or delegated-erp-draft')
    office = value.get('office')
    if office not in OFFICES:
        raise ValueError('Unknown AI executive office')
    action = identifier(value.get('action_type'))
    parameters = value.get('parameters')
    if not isinstance(parameters, dict):
        raise ValueError('Proposal parameters must be an object')
    # Force JSON validation, finite numbers and a bounded durable record.
    if len(canonical(parameters).encode()) > 100_000:
        raise ValueError('Proposal parameters exceed 100 kB')
    if authority == 'delegated-erp-draft' and action in COMPONENT_DRAFTS:
        if set(parameters) != {'project', 'key', 'inputs'} or not isinstance(parameters['inputs'], dict):
            raise ValueError('Component draft parameters must contain only project, key and inputs')
        _text(parameters['project'], 'ERP project', 140)
        identifier(parameters['key'])
    if authority == 'delegated-erp-draft' and action == 'erp.draft-material-request':
        required = {'project', 'task', 'requirement_id', 'item_code', 'quantity', 'schedule_date', 'warehouse'}
        if set(parameters) != required:
            raise ValueError('Material-request parameters do not match the ERP draft contract')
        for field in required - {'quantity'}:
            _text(parameters[field], field, 240)
    evidence = value.get('evidence', [])
    if not isinstance(evidence, list) or len(evidence) > 50:
        raise ValueError('Proposal evidence must be a list of at most 50 references')
    clean_evidence = []
    for row in evidence:
        if not isinstance(row, dict):
            raise ValueError('Proposal evidence entry must be an object')
        digest = row.get('sha256')
        if not isinstance(digest, str) or len(digest) != 64 or any(c not in '0123456789abcdef' for c in digest):
            raise ValueError('Proposal evidence must have a lowercase SHA-256')
        clean_evidence.append({'kind': identifier(row.get('kind')), 'sha256': digest,
                               'reference': _text(row.get('reference'), 'evidence reference', 2048)})
    return {
        'id': identifier(value.get('id')), 'city': identifier(value.get('city')),
        'environment': identifier(value.get('environment')), 'office': office,
        'action_type': action, 'requested_authority': authority,
        'summary': _text(value.get('summary'), 'summary', 500),
        'rationale': _text(value.get('rationale'), 'rationale', 4000),
        'parameters': parameters, 'evidence': clean_evidence,
        'created_at': value['created_at'], 'expires_at': value['expires_at'],
    }


def validate_ballot(value, identity, context_sha256):
    if not isinstance(value, dict):
        raise ValueError('Council ballot must be an object')
    for field in ('model_id', 'model_family', 'provider', 'perspective'):
        identifier(identity.get(field))
    if identity['perspective'] not in PERSPECTIVES:
        raise ValueError('Unknown council perspective')
    expected = value.get('expected_identity')
    if expected is not None and (not isinstance(expected, dict) or
            set(expected) != {'model_id', 'perspective'} or
            expected['model_id'] != identity['model_id'] or expected['perspective'] != identity['perspective']):
        raise ValueError('Runner identity does not match its authenticated model principal')
    verdict = value.get('verdict')
    if verdict not in VERDICTS:
        raise ValueError('Ballot verdict must be endorse, reject or abstain')
    if value.get('context_sha256') != context_sha256:
        raise ValueError('Ballot does not cite the proposal operational context')
    claims = value.get('claims', [])
    if not isinstance(claims, list) or len(claims) > 20 or any(
            not isinstance(row, str) or not row.strip() or len(row) > 500 for row in claims):
        raise ValueError('Ballot claims must be a list of at most 20 bounded statements')
    artifact_hashes = {}
    for field in ('prompt_sha256', 'response_sha256'):
        artifact = value.get(field)
        if not isinstance(artifact, str) or len(artifact) != 64 or any(c not in '0123456789abcdef' for c in artifact):
            raise ValueError(f'{field} must be a lowercase SHA-256')
        artifact_hashes[field] = artifact
    return {
        'id': identifier(value.get('id')), 'model_id': identity['model_id'],
        'model_family': identity['model_family'], 'provider': identity['provider'],
        'perspective': identity['perspective'], 'verdict': verdict,
        'rationale': _text(value.get('rationale'), 'ballot rationale', 4000),
        'claims': [row.strip() for row in claims], 'context_sha256': context_sha256,
        **artifact_hashes,
    }


def decide(proposal, ballots, policy, now):
    """Return a deterministic decision; never execute or contact a model."""
    policy = validate_policy(policy)
    perspectives = {b['perspective'] for b in ballots}
    providers = {b['provider'] for b in ballots}
    families = {b['model_family'] for b in ballots}
    endorsements = sum(b['verdict'] == 'endorse' for b in ballots)
    rejections = sum(b['verdict'] == 'reject' for b in ballots)
    reasons = []
    if len(ballots) < policy['quorum']:
        reasons.append('quorum-not-met')
    if not set(policy['required_perspectives']) <= perspectives:
        reasons.append('required-perspective-missing')
    if len(providers) < policy['minimum_providers']:
        reasons.append('provider-independence-not-met')
    if len(families) < policy['minimum_model_families']:
        reasons.append('model-family-independence-not-met')
    expired = _instant(proposal['expires_at'], 'expires_at') <= now
    if expired:
        reasons.append('proposal-expired')

    eligible = not reasons
    ratio = endorsements / len(ballots) if ballots else 0
    if expired:
        outcome = 'expired-unverified'
    elif not eligible:
        outcome = 'insufficient-verification'
    elif rejections:
        outcome = 'disputed-human-review-required'
        reasons.append('recorded-dissent')
    elif ratio < policy['approval_ratio']:
        outcome = 'not-endorsed'
        reasons.append('approval-threshold-not-met')
    elif proposal['requested_authority'] == 'advisory':
        outcome = 'advisory-endorsed'
    elif proposal['action_type'] in policy['delegated_erp_drafts']:
        outcome = 'delegated-erp-draft-authorized'
    else:
        outcome = 'human-approval-required'
        reasons.append('action-outside-delegation')

    return {
        'outcome': outcome, 'reasons': reasons,
        'counts': {'ballots': len(ballots), 'endorse': endorsements,
                   'reject': rejections, 'abstain': len(ballots) - endorsements - rejections,
                   'providers': len(providers), 'model_families': len(families)},
        'perspectives': sorted(perspectives), 'approval_ratio': ratio,
        'policy': policy,
        'authority': ('Authority derives from the operator-approved delegation policy and attestation key, '
                      'not from a model. No outcome grants SCADA, movement, safety, employment, payment or legal authority.'),
    }


def attest(decision, key, key_id):
    if not isinstance(key, str) or len(key) < 32:
        raise ValueError('Executive attestation key must contain at least 32 characters')
    identifier(key_id)
    digest = sha256(decision)
    signature = hmac.new(key.encode(), digest.encode(), hashlib.sha256).hexdigest()
    return digest, {'algorithm': 'HMAC-SHA256', 'key_id': key_id, 'signature': signature}
