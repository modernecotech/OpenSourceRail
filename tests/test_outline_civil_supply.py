from copy import deepcopy
import json
from math import ceil, fsum
from pathlib import Path

import pytest

from engineering.outline import civil_supply
from engineering.station_rail.common import digest, identity

ROOT = Path(__file__).resolve().parents[1]
CASES = ('low','base','high')


@pytest.fixture
def inputs():
    value=json.loads((ROOT/'docs/design-engine/line30-benchmark/result.json').read_bytes())
    return value['civil'],value['specification']


def reseal(civil):
    civil['evaluation_id']=identity({k:v for k,v in civil.items() if k!='evaluation_id'})
    return civil


def item(result,name):
    return next(z for z in result['decisions'] if z['item']==name)


@pytest.mark.parametrize('scenario',['china-bulk-buy','project-make-buy'])
def test_supply_preserves_input_geometry_quantity_mass_and_all_scopes(inputs,scenario):
    civil,spec=inputs;before=deepcopy((civil,spec))
    result=civil_supply.revalue(civil,spec,scenario)
    assert (civil,spec)==before
    assert result['civil']['quantities']==civil['quantities']
    assert result['civil']['beam']==civil['beam']
    assert result['civil']['evaluation_vehicle_mass_hypothesis']==civil['evaluation_vehicle_mass_hypothesis']
    old={z['key'] for z in civil['capital_lines']}
    assert len(old)==len(result['civil']['capital_lines'])==14
    assert {z['key'] for z in result['civil']['capital_lines']}==old
    assert all(z['costs_iqd'][case]>0 for z in result['civil']['capital_lines'] for case in CASES)
    assert all(result[key] is result['civil'][key] is False for key in civil_supply.FLAGS)


def test_rail_profile_hold_and_landed_arithmetic(inputs):
    result=civil_supply.revalue(*inputs,'china-bulk-buy');rail=item(result,'finished-60E1-rail')
    assert rail['selected_route']=='buy-existing-mill'
    assert rail['comparison']['cases']['base']['make'] is None
    buy=rail['comparison']['cases']['base']['purchase']
    assert buy['per_unit']==pytest.approx((800+150)*1.005*1.05+15+30)
    assert buy['selected_tier']['source_class']=='C'
    assert buy['extra_bulk_discount_applied'] is False
    assert result['civil']['quantities']['rail_kg']==7225200
    assert result['assumptions']['rail_scope_hold_observation_id']=='cn-yongyang-gb43-rail'
    assert result['civil']['unit_rates']['base']['rail_factory_iqd_kg']==pytest.approx(buy['per_unit']/1000*1510)


@pytest.mark.parametrize('scenario',['china-bulk-buy','project-make-buy'])
def test_exact_whole_scope_accounting_fixed_factory_once(inputs,scenario):
    civil,spec=inputs;result=civil_supply.revalue(civil,spec,scenario);fx=spec['currency']['iqd_per_usd']
    beam=item(result,'structural-precast-beam');fast=item(result,'complete-fasteners');rail=item(result,'finished-60E1-rail')
    for i,case in enumerate(CASES):
        factory=next(z['costs_iqd'][case] for z in result['civil']['capital_lines'] if z['key']=='beam_factory')/fx
        # Buildings are included in the independent comparison and exported as
        # areas for the parent to price, rather than exported a second time.
        building=(result['precast_floor_m2'][i]*spec['capital']['factory_building_iqd_per_m2'][i]
            +result['precast_yard_m2'][i]*spec['capital']['precast_yard_iqd_per_m2'][i])/fx
        accounted=factory+result['owned_factory_capital_usd'][case]+building
        expected=rail['comparison']['cases'][case]['purchase']['total']
        for decision in (beam,fast):
            expected+=decision['comparison']['cases'][case]['make' if decision['selected_route']=='make' else 'purchase']['total']
        assert accounted==pytest.approx(expected,rel=1e-12)
        delta=result['assumptions']['replacement_accounting'][case]
        before=civil['unit_rates'][case]
        assert delta['original_rail_and_fasteners_removed_iqd']==pytest.approx(
            civil['quantities']['rail_kg']*before['rail_factory_iqd_kg']
            +civil['quantities']['fastener_sets']*before['complete_8kg_fastener_factory_iqd_set'])


def test_contracted_factory_is_in_purchase_price_not_free_or_second_capital(inputs):
    result=civil_supply.revalue(*inputs,'china-bulk-buy')
    assert result['owned_factory_capital_usd']==dict(low=0.,base=0.,high=0.)
    assert result['precast_floor_m2']==result['precast_yard_m2']==[0.,0.,0.]
    beam=item(result,'structural-precast-beam')['comparison']['cases']['base']
    assert beam['purchase']['per_unit']==pytest.approx(beam['make']['variable_total']/3000*1.25+750)
    assert beam['purchase']['per_unit']>beam['make']['variable_total']/3000


def test_owned_capacity_moulds_buildings_and_prestress_plant_nonzero(inputs):
    result=civil_supply.revalue(*inputs,'project-make-buy')
    assert item(result,'structural-precast-beam')['selected_route']=='make'
    a=result['assumptions'];assert a['mould_counts']==[11,27,54]
    assert a['mould_counts'][1]==ceil(3000*5/(3*250*.75))
    assert a['mould_steel_mass_kg'][1]==pytest.approx(20000,rel=.01)
    assert a['mould_price_usd_each'][1]>30000
    assert a['mould_price_usd_each'][1]<80000
    assert result['owned_factory_capital_usd']['base']>2e6
    assert result['precast_floor_m2'][1]==27*24*5
    own=item(result,'structural-precast-beam')['comparison']['cases']['base']['make']
    assert own['available_hours_per_cell_project']==9000
    assert own['available_project_cell_hours']>=own['required_cell_hours']
    assert all(v>0 for v in own['fixed_components'].values())


def test_owned_route_uses_cash_machine_rate_and_explicit_paid_idle(inputs):
    civil,spec=inputs;result=civil_supply.revalue(civil,spec,'project-make-buy')
    own=item(result,'structural-precast-beam')['comparison']['cases']['base']['make']
    assert own['machine_rate_basis']=='cash-operating-excluding-capital-recovery'
    assert own['effective_operations']['machine_rate_per_hour']==25
    assert own['charged_labour_hours']==pytest.approx(own['labour_hours']/.75)
    assert own['variable_components']['labour']==pytest.approx((3000*64+3000*4)/.75*11812.5/1510)
    assert own['variable_components']['machine']==pytest.approx(3000*(4+1)*25)
    rows={z['key']:z for z in result['civil']['capital_lines']};old={z['key']:z for z in civil['capital_lines']}
    assert rows['erection_labour']['costs_iqd']['base']==pytest.approx(old['erection_labour']['costs_iqd']['base']/.75)
    assert result['civil']['unit_rates']['base']['productive_two_shift_wage_iqd_h']==15750


def test_concrete_prestress_premium_and_purchase_yield_not_raw_rebar_substitution(inputs):
    civil,spec=inputs;result=civil_supply.revalue(civil,spec,'project-make-buy');a=result['assumptions'];b=civil['beam'];p=civil['process_assumptions'];fx=1510
    r=a['rebar_selected_usd_kg'][1]
    expected=(b['concrete_m3']*civil['unit_rates']['base']['concrete_ingredient_iqd_m3']/fx
        +b['reinforcement_kg']*r/.95+b['prestress_kg']*4000/fx/.98+b['prestress_anchorage_kg']*7000/fx)
    assert a['structural_material_kit_usd_per_beam'][1]==pytest.approx(expected)
    assert r==min(civil['statistical_rates_iqd']['rebar']/fx,a['raw_rebar_cn_landed_usd_kg'][1])
    assert civil['unit_rates']['base']['concrete_ingredient_iqd_m3']==result['civil']['unit_rates']['base']['concrete_ingredient_iqd_m3']
    assert a['raw_material_grade_equivalence_is_planning_hypothesis'] is True


def test_rebar_source_selected_at_base_retains_whole_source_sensitivity(inputs):
    civil,spec=inputs;result=civil_supply.revalue(civil,spec,'project-make-buy')
    a=result['assumptions'];local=civil['statistical_rates_iqd']['rebar']/spec['currency']['iqd_per_usd']
    # China is cheaper in the low case, but Iraq wins at baseline. A scenario
    # keeps that baseline supplier route instead of taking three different minima.
    assert a['raw_rebar_cn_landed_usd_kg'][0]<local<a['raw_rebar_cn_landed_usd_kg'][1]
    assert a['rebar_selected_base_source']=='Iraq CSO rebar benchmark'
    assert a['rebar_source_by_case']==['Iraq CSO rebar benchmark']*3
    assert a['rebar_selected_usd_kg']==[local]*3
    assert a['rebar_counterfactual_usd_kg']['China']==a['raw_rebar_cn_landed_usd_kg']
    assert a['rebar_counterfactual_usd_kg']['Iraq']==[local]*3


def test_china_rebar_base_choice_also_retains_full_vector(inputs):
    civil,spec=inputs;civil['statistical_rates_iqd']['rebar']=1450.;reseal(civil)
    result=civil_supply.revalue(civil,spec,'project-make-buy');a=result['assumptions']
    assert a['rebar_selected_base_source']=='China HRB400E compatible-grade pricing hypothesis'
    assert len(set(a['rebar_source_by_case']))==1
    assert a['rebar_selected_usd_kg']==a['raw_rebar_cn_landed_usd_kg']
    # Even the adverse China case remains on the selected route when Iraq
    # would be cheaper in that one case.
    assert a['rebar_selected_usd_kg'][2]>1450./spec['currency']['iqd_per_usd']


def test_base_route_retained_and_unfavourable_high_case_preserved(inputs):
    result=civil_supply.revalue(*inputs,'project-make-buy');fast=item(result,'complete-fasteners')
    assert fast['selected_route']=='make'
    assert fast['comparison']['cases']['high']['preferred']=='buy'
    high=fast['comparison']['cases']['high']['make']
    assert result['civil']['unit_rates']['high']['complete_8kg_fastener_factory_iqd_set']==pytest.approx(high['variable_total']/210000*1510)
    assert fast['comparison']['cases']['high']['preference_differs_from_base'] is True


def test_price_changes_leave_independent_erection_transport_bearing_holds(inputs):
    civil,spec=inputs;result=civil_supply.revalue(civil,spec,'project-make-buy')
    old={z['key']:z for z in civil['capital_lines']};new={z['key']:z for z in result['civil']['capital_lines']}
    for key in ('crane_shifts','all_span_stock_haul','bearing_pads','end_joint_drains_lifting_hardware','protected_nonstation_walkway','field_butt_welding'):
        assert new[key]==old[key]
    assert set(('crane at radius','foundations','deformation feedback to magnetic gap'))<=set(result['assumptions']['physical_holds'])


def test_source_and_evaluation_identities_cover_inputs_and_new_producer(inputs):
    result=civil_supply.revalue(*inputs,'project-make-buy')
    assert result['evaluation_id']==identity({k:v for k,v in result.items() if k!='evaluation_id'})
    assert result['civil']['evaluation_id']==identity({k:v for k,v in result['civil'].items() if k!='evaluation_id'})
    assert result['input_civil_evaluation_id']==inputs[0]['evaluation_id']
    for path,sha in result['source_sha256'].items(): assert digest(ROOT/path)==sha
    assert result['source_sha256'][civil_supply.DATA]==digest(ROOT/civil_supply.DATA)


def test_repeat_is_deterministic(inputs):
    assert civil_supply.revalue(*inputs,'project-make-buy')==civil_supply.revalue(*inputs,'project-make-buy')


def test_bad_scenario_rejected(inputs):
    with pytest.raises(ValueError,match='scenario'):civil_supply.revalue(*inputs,'generic-cheaper-China')


@pytest.mark.parametrize('field,value',[('production_shifts',1),('hours_per_production_shift',12),('production_days_per_year',365),('productive_utilisation',1.)])
def test_shift_or_capacity_contract_cannot_silently_change(inputs,field,value):
    civil,spec=inputs;spec['design'][field]=value
    with pytest.raises(ValueError,match='shifts'):civil_supply.revalue(civil,spec,'project-make-buy')


@pytest.mark.parametrize('field,value',[('production_years',0),('production_years',float('nan'))])
def test_invalid_numeric_definition_rejected(inputs,field,value):
    civil,spec=inputs;spec['design'][field]=value
    with pytest.raises(ValueError,match='Finite'):civil_supply.revalue(civil,spec,'project-make-buy')


def test_changed_civil_input_requires_correct_identity(inputs):
    civil,spec=inputs;civil['quantities']['rail_kg']*=.5
    with pytest.raises(ValueError,match='identity'):civil_supply.revalue(civil,spec,'project-make-buy')
    reseal(civil)
    with pytest.raises(ValueError,match='aggregate'):civil_supply.revalue(civil,spec,'project-make-buy')


def test_shared_support_saving_cannot_enter_supply_pricing(inputs):
    civil,spec=inputs;civil['quantities']['independent_supports']/=2;reseal(civil)
    with pytest.raises(ValueError,match='independent supports'):civil_supply.revalue(civil,spec,'project-make-buy')


def test_missing_scope_not_replaced_with_zero(inputs):
    civil,spec=inputs;civil['capital_lines'].pop();reseal(civil)
    with pytest.raises(ValueError,match='fourteen'):civil_supply.revalue(civil,spec,'project-make-buy')
