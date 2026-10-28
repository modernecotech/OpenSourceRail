from copy import deepcopy
import pytest
from services.integration.osr_integration.reference_cell import delivery_drafts


def report():
    return dict(candidate_id='a'*64,body_candidate_id='b'*64,bundle=dict(candidate_id='a'*64,mass_registry_revision_id='c'*64),
        civil=dict(construction_sequence=[dict(asset_id='span/1')]),manufacturing=dict(candidate_id='a'*64,
        ERPNext=dict(items=[dict(disabled=1)],external_transactions_performed=False,production_orders=[])))


def test_new_candidate_does_not_mutate_released_orders_or_issue_purchase():
    v=report();orders=[dict(order_id='WO-001',candidate_id='d'*64,released_revision_id='e'*64)];before=deepcopy(orders)
    result=delivery_drafts(v,active_orders=orders)
    assert orders==before and not result['active_orders_mutated'] and not result['assets_activated']
    assert result['change_reviews'][0]['released_candidate_id']=='d'*64
    assert not result['live_movement_authority'] and result['drafts']['items'][0]['disabled']==1


@pytest.mark.parametrize('change',[
 lambda r:r['bundle'].update(candidate_id='f'*64),
 lambda r:r['manufacturing'].update(candidate_id='f'*64),
 lambda r:r['manufacturing']['ERPNext']['items'][0].update(disabled=0),
 lambda r:r['manufacturing']['ERPNext'].update(external_transactions_performed=True),
 lambda r:r['manufacturing']['ERPNext'].update(production_orders=[dict(order='WO-002')])])
def test_draft_bridge_refuses_mixed_or_activated_records(change):
    r=report();change(r)
    with pytest.raises(ValueError):delivery_drafts(r)
