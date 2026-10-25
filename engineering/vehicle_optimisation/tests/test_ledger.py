from copy import deepcopy
import pytest
from engineering.vehicle_optimisation import ledger


def change(name,old,new,parts=None,alloc=None):
    return dict(id=name,removal_kind='counted-stock' if parts else 'inherited-allocation',
                removed_part_ids=parts or [],removed_allocation_ids=alloc or [],
                removed_kg_per_car=old,added_known_kg_per_car=new,
                basis='Test ledger fixture; no material performance credit',
                source_bindings={'input.json':'a'*64},unknown_installed_inventory=['mounts'])


def test_named_components_not_whole_body_budget_and_payload_preserved():
    result=ledger.compose(25000,[change('support',10000,3000,['oldsupport']),
        change('HVAC',800,450,alloc=['hvac-allowance'])])
    assert result['comparison_empty_kg_per_car']==17650
    assert result['comparison_aw3_kg_per_car']==29650
    assert result['comparison_train_aw3_kg']==177900
    assert result['installed_aw3_kg_per_car'] is None
    assert result['service']['normal_pphpd']==6*120*3600/180


def test_overlap_and_negative_stock_are_rejected():
    with pytest.raises(ValueError,match='overlapping'):
        ledger.compose(25000,[change('a',1000,900,['frame']),change('b',1000,500,['frame'])])
    with pytest.raises(ValueError,match='overlapping'):
        ledger.compose(25000,[change('a',500,450,alloc=['doors']),change('b',500,400,alloc=['doors'])])
    with pytest.raises(ValueError):ledger.compose(25000,[change('a',800,-5,['a'])])
    with pytest.raises(ValueError,match='AW3 payload'):ledger.compose(25000,[],payload_kg=0.)


def test_unresolved_material_does_not_create_screen_pass_and_mass_feedback_matters():
    light=ledger.compose(25000,[change('support',10000,3000,['old'])])
    heavy=ledger.compose(25000,[change('support',10000,9000,['old'])])
    a=ledger.support_screen(18000,light,quality_usable=True)
    b=ledger.support_screen(18000,heavy,quality_usable=True)
    assert a['force_ratio']>b['force_ratio']
    assert ledger.support_screen(100000,light,quality_usable=False)['state']=='unknown'
    assert a['physical_accepted'] is False and a['coupled_control_and_thermal_pass'] is False
    nominal=ledger.support_screen(18000,light,quality_usable=True)
    assert ledger.support_screen(nominal['required_N_per_module']+1,light,
        quality_usable=True,numerical_variation_N=100)['state']=='unknown'
