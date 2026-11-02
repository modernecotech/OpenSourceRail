from copy import deepcopy
import pytest
from engineering.station_rail.common import identity
from engineering.design_search import topology_geometry as g,topology_cost as c,model_cost


@pytest.fixture(scope='module')
def canonical():return model_cost.assumptions()


def package(canonical,spec=None):
    candidate=g.realize([[1,1,1],[1,0,1],[1,1,1]])
    spec=c.default_spec() if spec is None else spec
    q=g.quantities(candidate,reserves_kg=spec['reserve_mass_kg'],module_length_m=spec['module_length_m'])
    return candidate,q,c.estimate(candidate,q,spec,canonical)


def test_complete_positive_scoped_cost_breakdown_and_independent_plant(canonical):
    candidate,q,value=package(canonical)
    assert value['evaluation_id']==identity({k:v for k,v in value.items() if k!='evaluation_id'})
    assert value['candidate_id']==q['candidate_id']==candidate['candidate_id']
    for row in value['cases']:
        assert 0<row['factory_gate_iqd']<row['delivered_iqd']<row['scoped_installed_iqd']<row['lifecycle']['total_scoped_npv_iqd']
        assert row['factory_gate_iqd']==pytest.approx(sum(row['factory_line_items_iqd'].values())+row['factory_overhead_iqd'])
        assert row['steel_purchased_kg']>=q['quantities']['steel_full_stock_envelope_kg']
        assert row['offcut_credit_iqd']==0 and row['steel_scrap_or_offcut_kg']>0
        assert row['plant_and_tooling_in_per_piece_iqd'] is False and row['dedicated_plant_capital_iqd']>0
        assert row['schedule']['production_shifts_per_day']==row['schedule']['civil_shifts_per_day']==2
        assert row['schedule']['hours_per_shift']==8
        assert row['schedule']['precedence_and_tool_capacity_verified'] is False
    assert not value['scope']['rails_included'] and not value['scope']['complete_installed_cost']
    assert all(value[k] is False for k in g.FLAGS)


def test_plant_capital_change_does_not_double_charge_piece_cost(canonical):
    a,q,first=package(canonical);spec=c.default_spec();spec['dedicated_plant_capital_iqd']=[v*2 for v in spec['dedicated_plant_capital_iqd']]
    second=c.estimate(a,q,spec,canonical)
    assert first['evaluation_id']!=second['evaluation_id']
    for x,y in zip(first['cases'],second['cases']):
        assert x['scoped_installed_iqd']==y['scoped_installed_iqd']
        assert x['lifecycle']==y['lifecycle']
        assert y['dedicated_plant_capital_iqd']==2*x['dedicated_plant_capital_iqd']


def test_mixed_candidate_and_reserve_accounting_rejected(canonical):
    a,q,_=package(canonical);b=g.realize([[1]])
    with pytest.raises(ValueError,match='quantities differ'):c.estimate(b,q,c.default_spec(),canonical)
    spec=c.default_spec();spec['reserve_mass_kg']['bearings']=[1.,2.,3.]
    with pytest.raises(ValueError,match='quantities differ'):c.estimate(a,q,spec,canonical)


def test_unqualified_disconnected_geometry_can_be_costed_without_admission(canonical):
    a=g.realize([[1,0],[0,1]]);spec=c.default_spec();q=g.quantities(a);v=c.estimate(a,q,spec,canonical)
    assert v['scope']['physical_topology_screen']=='disconnected-or-corner-contact'
    assert v['physical_accepted'] is False and v['engineering_accepted'] is False


def test_rates_are_explicit_and_canonical_receipt_must_be_sealed(canonical):
    a=g.realize([[1]]);q=g.quantities(a);spec=c.default_spec();spec['cut_hours_per_m'][1]=float('nan')
    with pytest.raises(ValueError):c.estimate(a,q,spec,canonical)
    bad=deepcopy(canonical);bad['real_discount_rate']=.5
    with pytest.raises(ValueError,match='Sealed'):c.estimate(a,q,c.default_spec(),bad)


@pytest.mark.parametrize('key',['coating_renewal_years','bearing_renewal_years'])
@pytest.mark.parametrize('interval',[1e-100,.249,1001.,float('inf'),float('nan')])
def test_renewal_construction_domain_prevents_unbounded_event_allocation(canonical,key,interval):
    a=g.realize([[1]]);q=g.quantities(a);spec=c.default_spec();spec[key][0]=interval
    with pytest.raises(ValueError):c.estimate(a,q,spec,canonical)


def test_quarterly_boundary_remains_bounded_and_not_certified_life(canonical):
    a=g.realize([[1]]);q=g.quantities(a);spec=c.default_spec();spec['coating_renewal_years']=[.25,.25,.25];spec['bearing_renewal_years']=[.25,.25,.25]
    v=c.estimate(a,q,spec,canonical)
    assert all(len(row['lifecycle']['renewals'])==238 for row in v['cases'])
    assert all(row['lifecycle']['certified_asset_life'] is False for row in v['cases'])


def test_finite_input_rates_that_overflow_cost_arithmetic_fail_before_sealing(canonical):
    a=g.realize([[1]]);q=g.quantities(a);spec=c.default_spec();spec['coating_iqd_per_m2']=[1e308]*3
    with pytest.raises(ValueError,match='nonfinite'):c.estimate(a,q,spec,canonical)
