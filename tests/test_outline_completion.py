"""Integration boundaries for complete, resumable city outline campaigns."""
from copy import deepcopy
import json
from pathlib import Path

import pytest

from engineering.outline import completion, city_inputs, city_service, city_project_cost, coordinator
from engineering.station_rail.common import encoded, identity
from engineering.design_search.model_cost import SCOPES


@pytest.fixture(scope='module')
def city_value():
    context = coordinator.prepare()
    inputs = city_inputs.load('samawah')
    rules = completion.policy()
    services = city_service.evaluate(inputs,rules,context['spec']['design'],context['vehicle'])
    cost = city_project_cost.evaluate_city_cost(inputs,services['line_services'],context,policy=rules)
    return completion._assemble_city(inputs,services,cost,context,rules)


def test_complete_city_carries_same_configuration_into_delivery_and_prices(city_value):
    value = city_value
    assert value['outline_complete']
    assert value['delivery_draft']['research_configuration_id']==value['research_configuration_id']
    assert value['cost']['city_input_id']==value['input_id']
    assert value['service_evaluation']['city_input_id']==value['input_id']
    assert set(value['cost']['scope_totals_usd'])==set(SCOPES)
    assert value['delivery_draft']['ERPNext']['draft_BOM_items']
    assert len(value['delivery_draft']['procurement_packages'])==len(value['cost']['capital_lines'])
    assert value['delivery_draft']['ERPNext']['disabled']==1
    assert value['delivery_draft']['ERPNext']['external_transactions_performed'] is False
    assert all(value[k] is False for k in completion.FLAGS)


def test_scope_total_cannot_conceal_a_different_capital_ledger(city_value):
    bad = deepcopy(city_value['cost'])
    bad['capital_lines'][0]['costs_usd']['base']+=500
    with pytest.raises(ValueError,match='ledger differs'):
        completion._check_costs(bad)


def test_every_lifecycle_scope_must_be_accounted_for(city_value):
    bad = deepcopy(city_value['cost'])
    bad['scope_totals_usd'].pop('disposal')
    with pytest.raises(ValueError,match='fourteen'):
        completion._check_costs(bad)


def test_stored_other_city_cannot_satisfy_requested_slug(city_value,tmp_path):
    request={'policy':city_value['policy'],'source_sha256':city_value['source_sha256']}
    path=tmp_path/'result.json';path.write_bytes(encoded(city_value))
    assert completion._checked_city(path,request,'samawah')['input_id']==city_value['input_id']
    with pytest.raises(ValueError,match='requested identity'):
        completion._checked_city(path,request,'baghdad')


def test_stored_city_rejects_changed_policy_or_source_epoch(city_value,tmp_path):
    path=tmp_path/'result.json';path.write_bytes(encoded(city_value))
    request={'policy':city_value['policy'],'source_sha256':dict(city_value['source_sha256'])}
    request['source_sha256'][next(iter(request['source_sha256']))]='0'*64
    with pytest.raises(ValueError,match='source epoch'):
        completion._checked_city(path,request,'samawah')
    request['policy']={}
    with pytest.raises(ValueError,match='policy differs'):
        completion._checked_city(path,request,'samawah')


def test_child_output_and_lock_symlinks_are_refused(tmp_path):
    outside=tmp_path/'outside';outside.mkdir()
    state=tmp_path/'state';state.mkdir();(state/'cities').symlink_to(outside,target_is_directory=True)
    with pytest.raises(ValueError,match='Linked'):
        completion._write(state/'cities'/'samawah'/'result.json',{})
    (state/'coordinator.lock').symlink_to(outside/'lock')
    with pytest.raises(ValueError,match='Linked'):
        with completion._locked(state):pass


def test_only_one_coordinator_may_write_an_execution_state(tmp_path):
    with completion._locked(tmp_path/'state'):
        with pytest.raises(ValueError,match='Another completion coordinator'):
            with completion._locked(tmp_path/'state'):pass


def test_source_names_cannot_escape_repository(tmp_path):
    with pytest.raises(ValueError,match='Repository-relative'):
        completion._check_sources(tmp_path,{'../outside':'0'*64})


def test_bounded_worker_and_invocation_budgets_are_validated(tmp_path):
    with pytest.raises(ValueError,match='workers'):
        completion.run(tmp_path/'run',workers=8)
    with pytest.raises(ValueError,match='city budget'):
        completion.run(tmp_path/'run',maximum_cities=0)
