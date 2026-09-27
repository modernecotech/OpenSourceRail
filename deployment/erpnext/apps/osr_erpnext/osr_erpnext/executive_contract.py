"""Pure verification of an attested executive-to-ERP draft packet."""
import hashlib
import hmac
import json
import re


SAFE_ACTIONS = {
    'erp.draft-budget-scenario': 'budget',
    'erp.draft-maintenance-plan': 'maintenance',
    'erp.draft-material-request': 'material-request',
    'erp.draft-work-order': 'manufacturing',
}


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def _identity(value, field):
    if not isinstance(value, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.:-]{0,159}', value):
        raise ValueError(f'Invalid {field}')
    return value


def _sha(value, field):
    if not isinstance(value, str) or not re.fullmatch(r'[0-9a-f]{64}', value):
        raise ValueError(f'Invalid {field}')
    return value


def verify(packet, configuration):
    """Verify authority and content binding without importing Frappe."""
    if not isinstance(packet, dict) or set(packet) != {
            'schema', 'id', 'city', 'environment', 'action_type', 'parameters',
            'proposal', 'decision', 'decision_sha256', 'attestation', 'authority'}:
        raise ValueError('Invalid executive draft packet')
    if packet['schema'] != 'osr-erp-executive-draft/1':
        raise ValueError('Unknown executive draft schema')
    proposal, decision, attestation = packet['proposal'], packet['decision'], packet['attestation']
    if not isinstance(proposal, dict) or not isinstance(decision, dict) or not isinstance(attestation, dict):
        raise ValueError('Executive packet records must be objects')
    decision_sha = _sha(packet['decision_sha256'], 'decision checksum')
    if digest(decision) != decision_sha:
        raise ValueError('Executive decision checksum mismatch')
    if set(attestation) != {'algorithm', 'key_id', 'signature'} or attestation['algorithm'] != 'HMAC-SHA256':
        raise ValueError('Unknown executive attestation')
    key_id = _identity(attestation['key_id'], 'attestation key identity')
    keys = configuration.get('keys', {}) if isinstance(configuration, dict) else {}
    key = keys.get(key_id)
    if not isinstance(key, str) or len(key) < 32:
        raise ValueError('Executive attestation key is unavailable')
    expected = hmac.new(key.encode(), decision_sha.encode(), hashlib.sha256).hexdigest()
    if not isinstance(attestation['signature'], str) or not hmac.compare_digest(attestation['signature'], expected):
        raise ValueError('Executive decision attestation is invalid')

    result = decision.get('result', {})
    policy = result.get('policy', {}) if isinstance(result, dict) else {}
    action = packet['action_type']
    if (decision.get('schema') != 'osr-executive-decision/1' or
            result.get('outcome') != 'delegated-erp-draft-authorized'):
        raise ValueError('Decision does not authorize an ERP draft')
    if action not in SAFE_ACTIONS or action not in policy.get('delegated_erp_drafts', []):
        raise ValueError('Action is outside the ERP draft delegation')
    if decision.get('proposal_id') != proposal.get('id') or decision.get('proposal_sha256') != digest(proposal):
        raise ValueError('Decision is not bound to this proposal')
    if packet['id'] != 'executive-' + _identity(proposal.get('id'), 'proposal identity'):
        raise ValueError('Executive action identity mismatch')
    if (packet['city'] != proposal.get('city') or packet['environment'] != proposal.get('environment') or
            action != proposal.get('action_type') or packet['parameters'] != proposal.get('parameters') or
            proposal.get('requested_authority') != 'delegated-erp-draft'):
        raise ValueError('Executive packet differs from its signed proposal')
    _identity(packet['city'], 'city')
    _identity(packet['environment'], 'environment')
    if not isinstance(packet['parameters'], dict):
        raise ValueError('Executive draft parameters must be an object')
    return {'proposal': proposal, 'decision': decision, 'decision_sha256': decision_sha,
            'action_type': action, 'component': SAFE_ACTIONS[action],
            'packet_sha256': digest(packet), 'key_id': key_id}
