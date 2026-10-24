"""Exact candidate quantities reach the existing lifecycle contract."""
from copy import deepcopy
import pytest
from engineering.ferrite_maglev import candidate_lifecycle as c
from osr_erpnext.maglev_manufacturing import stock_lines


def test_new_candidate_is_not_rebinding_old_product_geometry():
    p=c.lifecycle_package();old=c.base.lifecycle_package()
    assert p['configuration_sha256']==c.manufacturing.magnetics.definition()['configuration_sha256']
    assert p['configuration_sha256']!=old['configuration_sha256']
    assert p['sha256']!=old['sha256']
    assert c.RAW!=c.base.RAW
    assert len(c.planning_bundle(p)['manufacturing_tasks'])==3
    assert all(x['quantity']*x['rate']!=1 for x in stock_lines(p['products'][0]))


def test_new_candidate_uses_same_revision_serial_failure_and_replay_contract():
    p=c.lifecycle_package();result=c.base.scenario(p)
    assert len(result['snapshot']['events'])==69 and len(result['controls'])==21
    assert not result['snapshot']['physical_release']
    assert all(x['revision_hold'] for x in result['snapshot']['state']['positions'].values())


def test_native_quantified_adapter_refuses_coherently_wrong_valuation():
    p=deepcopy(c.lifecycle_package()['products'][0]);p['bom'][0]['source']['extended_cost_usd']*=2
    with pytest.raises(ValueError,match='valuation'):stock_lines(p)
