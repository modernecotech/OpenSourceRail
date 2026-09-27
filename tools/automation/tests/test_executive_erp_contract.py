"""ERP independently verifies that a draft packet is the council-endorsed action."""
import copy
import hashlib
import hmac
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'deployment/erpnext/apps/osr_erpnext'))
from osr_erpnext.executive_contract import digest, verify


KEY = 'erp-contract-test-key-01234567890123456789'
CONFIG = {'keys': {'council-key-1': KEY}}


def packet():
    proposal = {'id': 'D1', 'city': 'samawah', 'environment': 'simulation',
        'office': 'ai-chief-executive', 'action_type': 'erp.draft-work-order',
        'requested_authority': 'delegated-erp-draft', 'summary': 'Draft work',
        'rationale': 'Bounded action', 'created_at': '2026-01-01T00:00:00+00:00',
        'expires_at': '2026-01-02T00:00:00+00:00', 'evidence': [],
        'parameters': {'project': 'PROJ-1', 'key': 'decision-d1',
                       'inputs': {'bom': 'BOM-1', 'quantity': 1}}}
    decision = {'schema': 'osr-executive-decision/1', 'proposal_id': 'D1',
        'proposal_sha256': digest(proposal), 'operational_context_sha256': '1' * 64,
        'ballot_sha256s': ['2' * 64, '3' * 64, '4' * 64, '5' * 64],
        'result': {'outcome': 'delegated-erp-draft-authorized',
                   'policy': {'delegated_erp_drafts': ['erp.draft-work-order']}},
        'finalized_at': 1}
    decision_sha = digest(decision)
    signature = hmac.new(KEY.encode(), decision_sha.encode(), hashlib.sha256).hexdigest()
    return {'schema': 'osr-erp-executive-draft/1', 'id': 'executive-D1',
        'city': 'samawah', 'environment': 'simulation',
        'action_type': proposal['action_type'], 'parameters': proposal['parameters'],
        'proposal': proposal, 'decision': decision, 'decision_sha256': decision_sha,
        'attestation': {'algorithm': 'HMAC-SHA256', 'key_id': 'council-key-1', 'signature': signature},
        'authority': 'Create or update a draft only; submission and all railway authority remain external.'}


def test_valid_packet_binds_decision_proposal_and_erp_action():
    value = packet(); result = verify(value, CONFIG)
    assert result['component'] == 'manufacturing'
    assert result['packet_sha256'] == digest(value)


@pytest.mark.parametrize('mutation', [
    lambda value: value['parameters'].__setitem__('key', 'substituted'),
    lambda value: value.__setitem__('action_type', 'erp.draft-budget-scenario'),
    lambda value: value['proposal']['parameters'].__setitem__('key', 'substituted'),
    lambda value: value['decision']['result'].__setitem__('outcome', 'advisory-endorsed'),
    lambda value: value['attestation'].__setitem__('signature', '0' * 64),
])
def test_any_post_decision_mutation_is_rejected(mutation):
    value = copy.deepcopy(packet()); mutation(value)
    with pytest.raises(ValueError):
        verify(value, CONFIG)


def test_unknown_key_and_non_allowlisted_action_fail_closed():
    with pytest.raises(ValueError, match='unavailable'):
        verify(packet(), {'keys': {}})
    value = packet()
    value['proposal']['action_type'] = value['action_type'] = 'scada.set-point'
    value['decision']['proposal_sha256'] = digest(value['proposal'])
    value['decision_sha256'] = digest(value['decision'])
    value['attestation']['signature'] = hmac.new(KEY.encode(), value['decision_sha256'].encode(), hashlib.sha256).hexdigest()
    with pytest.raises(ValueError, match='outside'):
        verify(value, CONFIG)
