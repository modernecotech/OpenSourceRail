"""The AI executive layer is quorum-bound, transparent and unable to command SCADA."""
from datetime import datetime, timezone
import hashlib
import hmac
import json
from pathlib import Path
import sys
import threading
import time
from http.server import ThreadingHTTPServer
from urllib.error import HTTPError

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'services/integration'))
from osr_integration.config import build_package
from osr_integration.server import Handler, deliver_executive_actions, request_json
from osr_integration.store import Store


KEY = 'test-only-executive-attestation-key-0123456789'
POLICY = {
    'enabled': True, 'policy_id': 'test-delegation', 'version': '1', 'quorum': 4,
    'required_perspectives': ['strategy', 'finance', 'operations', 'risk'],
    'minimum_providers': 2, 'minimum_model_families': 3, 'approval_ratio': .75,
    'delegated_erp_drafts': ['erp.draft-work-order'],
    'attestation_key_id': 'test-key-1', 'attestation_key': KEY,
}


@pytest.fixture
def store(tmp_path):
    result = Store(tmp_path / 'gateway.sqlite')
    generic = json.loads((ROOT / 'deployment/supervision/config/generic.json').read_text())
    package = build_package(generic, {'city': 'samawah', 'company': 'Test Company',
        'erp_project': 'TEST-PROJECT'}, [
        {'asset_type': 'station', 'asset_id': 'samawah-station', 'name': 'Station'}], 'r1')
    result.apply(package, 'engineer')
    return result


def iso(value):
    return datetime.fromtimestamp(value, timezone.utc).isoformat()


def proposal(identity='P1', action='erp.draft-work-order', authority='delegated-erp-draft'):
    parameters = ({'project': 'TEST-PROJECT', 'key': identity.lower(),
                   'inputs': {'bom': 'BOM-1', 'quantity': 1}}
                  if action == 'erp.draft-work-order' else
                  {'project': 'TEST-PROJECT', 'subject': 'Human review required'})
    return {'id': identity, 'city': 'samawah', 'environment': 'simulation',
            'office': 'ai-chief-executive', 'action_type': action,
            'requested_authority': authority, 'summary': 'Prepare a maintenance work-order draft',
            'rationale': 'A reviewed draft can reduce administration without bypassing submission approval.',
            'parameters': parameters,
            'evidence': [], 'created_at': iso(1000), 'expires_at': iso(2000)}


IDENTITIES = [
    {'subject': 'model-strategy', 'model_id': 'strategy-1', 'model_family': 'family-a', 'provider': 'provider-a', 'perspective': 'strategy'},
    {'subject': 'model-finance', 'model_id': 'finance-1', 'model_family': 'family-b', 'provider': 'provider-b', 'perspective': 'finance'},
    {'subject': 'model-operations', 'model_id': 'operations-1', 'model_family': 'family-c', 'provider': 'provider-c', 'perspective': 'operations'},
    {'subject': 'model-risk', 'model_id': 'risk-1', 'model_family': 'family-d', 'provider': 'provider-a', 'perspective': 'risk'},
]


def vote(store, record, identity, verdict='endorse'):
    ballot = {'id': record['id'] + '-' + identity['perspective'], 'verdict': verdict,
              'rationale': 'The cited operational context supports this bounded recommendation.',
              'claims': ['The requested output remains an unsubmitted ERP draft.'],
              'context_sha256': record['operational_context_sha256'],
              'prompt_sha256': hashlib.sha256(('prompt-' + identity['subject']).encode()).hexdigest(),
              'response_sha256': hashlib.sha256(('response-' + verdict + identity['subject']).encode()).hexdigest()}
    return store.add_executive_ballot(record['id'], ballot, identity, now=1100)


def test_no_single_shot_and_independent_quorum_creates_attested_erp_draft(store):
    record = store.create_executive_proposal(proposal(), 'secretary', now=1000)
    assert record['created'] and record['operational_context']['assets']
    vote(store, record, IDENTITIES[0])
    pending = store.finalize_executive_proposal('P1', 'auditor', POLICY, now=1100)
    assert pending['state'] == 'collecting'
    assert pending['pending_decision']['result']['outcome'] == 'insufficient-verification'
    assert 'quorum-not-met' in pending['pending_decision']['result']['reasons']

    for identity in IDENTITIES[1:]:
        vote(store, record, identity)
    final = store.finalize_executive_proposal('P1', 'auditor', POLICY, now=1100)
    assert final['state'] == 'sealed'
    assert final['decision']['result']['outcome'] == 'delegated-erp-draft-authorized'
    assert final['erp_action']['state'] == 'pending'
    assert final['erp_action']['body']['authority'].startswith('Create or update a draft only')
    expected = hmac.new(KEY.encode(), final['decision_sha256'].encode(), hashlib.sha256).hexdigest()
    assert hmac.compare_digest(final['attestation']['signature'], expected)
    assert len(final['ballots']) == 4
    sys.path.insert(0, str(ROOT / 'deployment/erpnext/apps/osr_erpnext'))
    from osr_erpnext.executive_contract import verify
    received = verify(final['erp_action']['body'], {'keys': {'test-key-1': KEY}})
    assert received['component'] == 'manufacturing'


def test_dissent_is_visible_and_forces_human_review(store):
    record = store.create_executive_proposal(proposal('P2'), 'secretary', now=1000)
    for identity in IDENTITIES:
        vote(store, record, identity, 'reject' if identity['perspective'] == 'risk' else 'endorse')
    final = store.finalize_executive_proposal('P2', 'auditor', POLICY, now=1100)
    assert final['decision']['result']['outcome'] == 'disputed-human-review-required'
    assert final['decision']['result']['counts']['reject'] == 1
    assert not final.get('erp_action')
    assert next(row for row in final['ballots'] if row['perspective'] == 'risk')['verdict'] == 'reject'


@pytest.mark.parametrize('action', ['scada.set-point', 'railway.issue-movement-authority',
                                    'hr.terminate-employee', 'finance.make-payment', 'legal.sign-contract'])
def test_non_delegated_domains_can_only_reach_human_approval(store, action):
    identity = 'P-' + action.split('.')[0]
    record = store.create_executive_proposal(proposal(identity, action), 'secretary', now=1000)
    for model in IDENTITIES:
        vote(store, record, model)
    final = store.finalize_executive_proposal(identity, 'auditor', POLICY, now=1100)
    assert final['decision']['result']['outcome'] == 'human-approval-required'
    assert final['decision']['result']['reasons'] == ['action-outside-delegation']
    assert 'SCADA' in final['decision']['result']['authority']
    assert not final.get('erp_action')


def test_identity_independence_and_context_binding_are_enforced(store):
    record = store.create_executive_proposal(proposal('P3'), 'secretary', now=1000)
    with pytest.raises(ValueError, match='operational context'):
        store.add_executive_ballot('P3', {'id': 'bad-context', 'verdict': 'endorse',
            'rationale': 'This response cites a different observation.', 'claims': [],
            'context_sha256': '0' * 64, 'prompt_sha256': '1' * 64,
            'response_sha256': '2' * 64}, IDENTITIES[0], now=1100)
    copies = []
    for index, perspective in enumerate(['strategy', 'finance', 'operations', 'risk']):
        copies.append({'subject': 'copy-' + perspective, 'model_id': 'copy-' + str(index),
            'model_family': 'same-family', 'provider': 'same-provider', 'perspective': perspective})
    for model in copies:
        vote(store, record, model)
    pending = store.finalize_executive_proposal('P3', 'auditor', POLICY, now=1100)
    assert pending['state'] == 'collecting'
    reasons = pending['pending_decision']['result']['reasons']
    assert 'provider-independence-not-met' in reasons
    assert 'model-family-independence-not-met' in reasons


def test_executive_erp_delivery_is_durable_and_retry_safe(store, monkeypatch):
    record = store.create_executive_proposal(proposal('P5'), 'secretary', now=1000)
    for model in IDENTITIES:
        vote(store, record, model)
    store.finalize_executive_proposal('P5', 'auditor', POLICY, now=1100)
    from osr_integration import server as gateway_server
    calls = []
    def unavailable(*args, **kwargs):
        calls.append(args)
        raise OSError('offline')
    monkeypatch.setattr(gateway_server, 'request_json', unavailable)
    erp = {'url': 'http://erp', 'key': 'key', 'secret': 'secret'}
    deliver_executive_actions(store, erp, now=1200)
    failed = store.executive_decision('P5')['erp_action']
    assert failed['state'] == 'pending' and failed['attempts'] == 1 and failed['next_try'] > 1200
    monkeypatch.setattr(gateway_server, 'request_json', lambda *a, **k: {
        'message': {'decision': 'P5', 'doctype': 'Work Order', 'name': 'WO-1',
                    'created': True, 'docstatus': 0, 'automatic_submission': False}})
    deliver_executive_actions(store, erp, now=failed['next_try'])
    delivered = store.executive_decision('P5')['erp_action']
    assert delivered['state'] == 'delivered'
    assert delivered['response']['automatic_submission'] is False
    assert len(calls) == 1


def test_permanent_erp_rejection_is_visible_and_not_retried(store, monkeypatch):
    record = store.create_executive_proposal(proposal('P6'), 'secretary', now=1000)
    for model in IDENTITIES:
        vote(store, record, model)
    store.finalize_executive_proposal('P6', 'auditor', POLICY, now=1100)
    from osr_integration import server as gateway_server
    def rejected(*args, **kwargs):
        raise HTTPError('http://erp', 403, 'denied', {}, None)
    monkeypatch.setattr(gateway_server, 'request_json', rejected)
    erp = {'url': 'http://erp', 'key': 'key', 'secret': 'secret'}
    deliver_executive_actions(store, erp, now=1200)
    action = store.executive_decision('P6')['erp_action']
    assert action['state'] == 'rejected' and action['attempts'] == 1
    deliver_executive_actions(store, erp, now=2000)
    assert store.executive_decision('P6')['erp_action']['attempts'] == 1


def test_ballots_and_proposals_are_immutable(store):
    record = store.create_executive_proposal(proposal('P4'), 'secretary', now=1000)
    assert not store.create_executive_proposal(proposal('P4'), 'secretary', now=1000)['created']
    with pytest.raises(ValueError, match='immutable'):
        store.create_executive_proposal(dict(proposal('P4'), summary='Changed after issue'), 'secretary', now=1000)
    assert vote(store, record, IDENTITIES[0])['created']
    assert not vote(store, record, IDENTITIES[0])['created']
    changed = {'id': 'P4-strategy', 'verdict': 'reject', 'rationale': 'Changed vote', 'claims': [],
               'context_sha256': record['operational_context_sha256'],
               'prompt_sha256': '1' * 64, 'response_sha256': '2' * 64}
    with pytest.raises(ValueError, match='cannot revise'):
        store.add_executive_ballot('P4', changed, IDENTITIES[0], now=1100)


def test_model_view_hides_other_models_ballots():
    ballots = [{'model_id': 'strategy-1'}, {'model_id': 'finance-1'}]
    result = Handler.executive_view(
        {'role': 'executive-model', 'model_id': 'strategy-1'},
        {'items': [{'id': 'P-redacted', 'ballots': list(ballots)}]},
    )
    assert result['items'][0]['ballots'] == [{'model_id': 'strategy-1'}]

    viewer_result = {'items': [{'id': 'P-visible', 'ballots': list(ballots)}]}
    assert Handler.executive_view({'role': 'viewer'}, viewer_result) == viewer_result
    assert len(viewer_result['items'][0]['ballots']) == 2


def test_http_roles_scope_and_configured_model_identity(store):
    principals = [
        {'token': 'secretary', 'role': 'executive-secretary', 'subject': 'secretary',
         'cities': ['samawah'], 'environments': ['simulation']},
        {'token': 'auditor', 'role': 'executive-auditor', 'subject': 'auditor',
         'cities': ['samawah'], 'environments': ['simulation']},
        {'token': 'viewer', 'role': 'viewer', 'subject': 'viewer',
         'cities': ['samawah'], 'environments': ['simulation']},
        {'token': 'model', 'role': 'executive-model', **IDENTITIES[0],
         'cities': ['samawah'], 'environments': ['simulation']},
    ]
    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    server.store, server.config = store, {'principals': principals, 'executive_council': POLICY}
    thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
    url = f'http://127.0.0.1:{server.server_port}'
    try:
        now = time.time()
        body = dict(proposal('HTTP1'), created_at=iso(now), expires_at=iso(now + 600))
        created = request_json(url + '/executive/proposals', body,
                               {'Authorization': 'Bearer secretary'})
        assert created['created']
        read = request_json(url + '/executive/decisions?id=HTTP1', headers={'Authorization': 'Bearer viewer'})
        ballot = {'id': 'HTTP1-strategy', 'verdict': 'endorse', 'rationale': 'Bounded draft is supported.',
                  'claims': [], 'context_sha256': read['operational_context_sha256'],
                  'prompt_sha256': '1' * 64, 'response_sha256': '2' * 64,
                  'model_id': 'attempted-body-spoof'}
        with pytest.raises(HTTPError) as error:
            request_json(url + '/executive/ballots', {'proposal_id': 'HTTP1', 'ballot': ballot},
                         {'Authorization': 'Bearer viewer'})
        assert error.value.code == 403
        result = request_json(url + '/executive/ballots', {'proposal_id': 'HTTP1', 'ballot': ballot},
                              {'Authorization': 'Bearer model'})
        assert result['created']
        stored = request_json(url + '/executive/decisions?id=HTTP1', headers={'Authorization': 'Bearer viewer'})
        assert stored['ballots'][0]['model_id'] == IDENTITIES[0]['model_id']
    finally:
        server.shutdown(); server.server_close(); thread.join()
