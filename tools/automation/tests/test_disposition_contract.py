import copy
from pathlib import Path
import sys
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'deployment/erpnext/apps/osr_erpnext'))
from osr_erpnext import disposition_contract as contract


def proposal():
    return dict(key='review-1', mapping='M1', target=dict(kind='purchase-line', document='PO1', line='L1'),
                action='Request amendment', responsible='owner@example.invalid', due_date='2026-10-01',
                rationale='A revised connector is required.', references=['drawing:revision-2'])


def review():
    return dict(mapping=dict(name='M1'), sha256='a'*64, scope=dict(city='samawah', project='P1'),
                warnings=[], purchase_orders=[dict(document='PO1', line='L1', item='connector', qty=4)],
                work_orders=[], stock_movements=[])


def test_review_is_bound_to_exact_purchase_line_actor_and_exposure():
    request=contract.proposal(proposal()); source=review()
    result=contract.plan(source,request,'proposer')
    assert result['fingerprint']==contract.plan(source,request,'proposer')['fingerprint']
    assert result['fingerprint']!=contract.plan(source,request,'other')['fingerprint']
    assert not result['automatic_execution'] and not result['railway_release_authorised']
    source['sha256']='b'*64
    assert result['fingerprint']!=contract.plan(source,request,'proposer')['fingerprint']
    request['target']['line']='L2'
    with pytest.raises(ValueError,match='outside'): contract.plan(source,request,'proposer')


@pytest.mark.parametrize('change',[
    dict(approved=True), dict(references=[]), dict(due_date='2026-02-30'), dict(key='../record'),
    dict(action='Submit order'), dict(target=dict(kind='stock-entry',document='SE',line='L1')),
    dict(target=dict(kind='arbitrary-doctype',document='PO1')), dict(rationale=''),
])
def test_unknown_fields_actions_and_malformed_evidence_are_rejected(change):
    with pytest.raises(ValueError): contract.proposal({**proposal(),**change})


def test_requests_do_not_mutate_input_and_decisions_require_evidence():
    value=proposal(); before=copy.deepcopy(value)
    assert contract.proposal(value)==value and before==value
    with pytest.raises(ValueError): contract.decision(dict(outcome='Endorse plan',rationale='ok',references=[]))
    with pytest.raises(ValueError): contract.decision(dict(outcome='Execute',rationale='ok',references=['evidence']))
    assert contract.decision(dict(outcome='Reject plan',rationale='Wrong allocation',references=['review:R2']))['outcome']=='Reject plan'
