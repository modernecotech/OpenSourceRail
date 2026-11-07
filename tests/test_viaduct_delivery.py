from copy import deepcopy
import pytest
from engineering.station_rail.common import identity
from engineering.design_search import civil_shape_geometry as geometry
from engineering.design_search.craft_backends import viaduct_delivery as delivery


@pytest.fixture(scope='module')
def context():return delivery.prepare()


def test_stock_reserves_and_owned_costs_reconcile_without_installed_claim(context):
    for family in geometry.FAMILIES:
        definition=geometry.generate(family)
        original=deepcopy(definition)
        result=delivery.build(definition,context)
        assert definition==original
        assert result['candidate_id']==definition['candidate_id']
        assert result['complete_installed_mass_kg'] is None
        assert result['complete_installed_cost_iqd'] is None
        assert result['business_draft']['disabled']==1
        assert result['business_draft']['executable_work_order'] is False
        assert result['cost']['additive_to_city_or_corridor_budget'] is False
        assert result['cost']['reprice_performed'] is False
        for case in result['mass_accounts']:
            assert case['accounted_delivery_mass_kg']>case['nominal_stock_kg']
            assert case['bearing_and_other_unlocated_hardware_mass_kg'] is None
        assert result['delivery_evaluation_id']==identity({k:v for k,v in result.items() if k!='delivery_evaluation_id'})
        assert all(result[k] is False for k in delivery.FLAGS)


def test_prism_regions_do_not_become_manufactured_components(context):
    result=delivery.build(geometry.generate('variable_depth_box'),context)
    assert result['source_prism_count']==80
    assert result['proposed_manufactured_groups']==[dict(id='integrated-precast-span',proposed_count=1)]
    assert result['formwork']['developed_mould_area_m2'] is None
    assert result['formwork']['production_capacity_verified'] is False


def test_resealed_other_candidate_quantities_and_cost_context_are_rejected(context):
    bad=deepcopy(context);candidate=geometry.generate('reference_box')
    bad['rows'][candidate['candidate_id']]['quantities']['total_nominal_stock_mass_kg']+=1
    bad['context_id']=identity({k:v for k,v in bad.items() if k!='context_id'})
    with pytest.raises(ValueError,match='exact nominal quantities'):delivery.build(candidate,bad)


def test_dated_rail_allowance_is_visible_and_counted_once(context):
    result=delivery.build(geometry.generate('reference_box'),context)
    base=result['cost']['cases']['base']
    assert base['owned_accounts_iqd']['rail-and-fastener-interface']==52084000.
    assert sum(base['owned_accounts_iqd'].values())==pytest.approx(base['scoped_installed_iqd'],abs=1.)
    assert 'not the newer China' in result['cost']['basis']


@pytest.mark.parametrize('reseal_row',[False,True])
def test_resealed_price_cannot_inherit_a_retained_cost_identity(context,reseal_row):
    bad=deepcopy(context);candidate=geometry.generate('reference_box')
    row=bad['rows'][candidate['candidate_id']]
    row['cost_estimate']['cases'][1]['factory_gate_iqd']+=1000000.
    if reseal_row:row['evaluation_id']=identity({k:v for k,v in row.items() if k!='evaluation_id'})
    bad['context_id']=identity({k:v for k,v in bad.items() if k!='context_id'})
    with pytest.raises(ValueError,match='cost-row evaluation|retained source evaluation'):
        delivery.build(candidate,bad)


def test_resealed_manufacturing_assumption_cannot_inherit_old_cost(context):
    bad=deepcopy(context);bad['specification']['rates']['form_reuses']=1
    bad['context_id']=identity({k:v for k,v in bad.items() if k!='context_id'})
    with pytest.raises(ValueError,match='retained source evaluation'):delivery.build(geometry.generate('reference_box'),bad)
