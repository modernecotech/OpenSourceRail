import copy
import hashlib
import json
from pathlib import Path
import sys
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'deployment/erpnext/apps/osr_erpnext'))
from osr_erpnext.outcome_contract import verify, request


def signed(value):
    value=copy.deepcopy(value);value.pop('sha256',None)
    value['sha256']=hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return value


def fixture():
    baseline=signed(dict(scope=dict(company='OSR',project='P1'),warnings=[],mapping={'revision':'R1'},
        work_orders=[dict(name='WO1',item='ITEM',bom='BOM1',docstatus=1,status='In Process',modified='2026-01-01 08:00:00',
                         actionable=True,produced_qty=1,planned_qty=2)], purchase_orders=[],stock_movements=[]))
    current=copy.deepcopy(baseline);current['work_orders'][0].update(status='Stopped',modified='2026-01-01 10:00:00',actionable=False)
    native=dict(doctype='Work Order',name='WO1',company='OSR',project='P1',docstatus=1,status='Stopped',modified='2026-01-01 10:00:00')
    proposal=dict(action='Request production stop',target=dict(kind='work-order',document='WO1'))
    return baseline,signed(current),proposal,native,'2026-01-01 09:00:00'


def test_only_expected_stop_changes_are_accepted_without_mutating_sources():
    args=fixture();original=copy.deepcopy(args)
    assert verify(*args)=='Native outcome verified'
    assert args==original


@pytest.mark.parametrize('change', ['production','bom','stock','permission','other-order'])
def test_unrelated_changes_cannot_be_hidden_by_a_stop(change):
    before,after,proposal,native,time=fixture()
    if change=='production':after['work_orders'][0]['produced_qty']=2
    if change=='bom':after['work_orders'][0]['bom']='BOM2'
    if change=='stock':after['stock_movements'].append(dict(name='SE-new'))
    if change=='permission':after['warnings'].append('Purchase Order: permission-denied')
    if change=='other-order':after['work_orders'].append(dict(name='other'))
    with pytest.raises(ValueError):verify(before,signed(after),proposal,native,time)


@pytest.mark.parametrize('change',[dict(status='In Process'),dict(docstatus=2),dict(name='WO2'),dict(company='OTHER'),dict(project='P2'),dict(modified='2026-01-01 07:00:00')])
def test_wrong_or_earlier_native_outcomes_are_rejected(change):
    before,after,proposal,native,time=fixture()
    with pytest.raises(ValueError):verify(before,after,proposal,{**native,**change},time)


def test_cancelled_purchase_is_checked_directly_and_only_that_order_is_removed():
    before,_,_,_,time=fixture();before['work_orders']=[]
    line=dict(document='PO1',line='L1',item='RAW',qty=3,received_qty=0,uom='Nos',docstatus=1)
    other={**line,'document':'PO2','line':'L2'}
    before['purchase_orders']=[line,other]
    after=copy.deepcopy(before);after['purchase_orders']=[other]
    native=dict(doctype='Purchase Order',name='PO1',company='OSR',project='P1',docstatus=2,
                modified='2026-01-01 10:00:00',lines=[line])
    proposal=dict(action='Request cancellation',target=dict(kind='purchase-line',document='PO1',line='L1'))
    assert verify(signed(before),signed(after),proposal,native,time)=='Native outcome verified'
    native['lines']=[{**line,'qty':4}]
    with pytest.raises(ValueError,match='lines differ'):verify(signed(before),signed(after),proposal,native,time)


def test_legacy_and_corrupt_snapshots_and_unsupported_actions_are_not_certified():
    args=list(fixture())
    args[0]=None
    with pytest.raises(ValueError,match='complete exposure'):verify(*args)
    args=list(fixture());args[0]['sha256']='bad'
    with pytest.raises(ValueError,match='checksum'):verify(*args)
    args=list(fixture());args[2]['action']='Unsupported action'
    with pytest.raises(ValueError,match='no native outcome'):verify(*args)


def test_request_cannot_supply_outcome_actor_or_skip_evidence():
    good=dict(key='check-1',rationale='Verified native record.',references=['audit:record'])
    assert request(good)==good
    for change in [dict(verifier='Administrator'),dict(execution_verified=True),dict(references=[]),dict(key='../other')]:
        with pytest.raises(ValueError):request({**good,**change})
