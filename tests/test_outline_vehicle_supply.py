from copy import deepcopy
from math import ceil, fsum
from pathlib import Path
import json

import pytest

from engineering.design_search.line_benchmark import VEHICLE_COST, fixed_mass_vehicle_price
from engineering.outline import vehicle_supply as supply
from engineering.station_rail import ROOT
from engineering.station_rail.common import identity


@pytest.fixture(scope='module')
def original():
    return json.loads((Path(ROOT)/VEHICLE_COST).read_bytes())


@pytest.fixture(scope='module')
def outputs(original):
    return {s:supply.revalue(original,dict(totalcars=312,total_trainsets=52),s)
        for s in ('china-bulk-buy','project-make-buy')}


def line(record,key):
    return next(r for r in record['lines'] if r['line_key']==key)


def test_pricing_preserves_exact_candidate_and_mass_without_mutating_source(original,outputs):
    before=deepcopy(original)
    for result in outputs.values():
        value=result['vehicle_cost']
        for k in ('candidate_id','body_candidate_id','support_component_id','propulsion_component_id',
                  'evaluation_id','selection_id','vehicle_account','mass_reserve_sensitivity','accounting_overlap'):
            assert value[k]==original[k]
        for old,new in zip(original['lines'],value['lines']):
            for k,v in old['quantity'].items():
                if 'mass' in k:assert new['quantity'][k]==v
        assert value['assumptions_id']==identity(value['assumption_values'])
        assert value['upstream_assumptions_id']==original['assumptions_id']
        assert value['cost_estimate_id']==identity({k:v for k,v in value.items() if k!='cost_estimate_id'})
        assert result['evaluation_id']==identity({k:v for k,v in result.items() if k!='evaluation_id'})
        assert all(result[k] is False for k in supply.FLAGS)
    assert original==before


def test_every_account_occurs_once_and_all_new_lines_are_sealed(original,outputs):
    for result in outputs.values():
        value=result['vehicle_cost']
        assert [r['line_key'] for r in value['lines']]==[r['line_key'] for r in original['lines']]
        assert len({r['source_line_id'] for r in result['decisions']})==len(original['lines'])
        for row in value['lines']:
            assert row['line_id']==identity({k:v for k,v in row.items() if k!='line_id'})
        for case in supply.CASES:
            assert value['total_vehicle_factory_delivery_assembly_iqd_per_train'][case]==pytest.approx(
                fsum(r['cost_iqd'][case] for r in value['lines']),abs=.011)


def test_residual_scaling_normalizes_to_same_nominal_mass(outputs):
    for result in outputs.values():
        vc=result['vehicle_cost'];fx=result['assumptions']['iqd_per_usd']
        decision=next(d for d in result['decisions'] if d['line_key']=='unlocated-account/retained-comfort/body')
        row=line(vc,decision['line_key']);route=decision['selected_route']
        for i,case in enumerate(supply.CASES):
            kernel=decision['comparison']['cases'][case]['make' if route=='make' else 'purchase']
            expected=(kernel['variable_total']*(1+(.1,.15,.25)[i]) if route=='make' else kernel['total'])/312*6*fx
            assert row['cost_iqd'][case]/vc['mass_reserve_sensitivity']['case_factors'][case]==pytest.approx(expected,abs=.02)
        fixed=fixed_mass_vehicle_price(vc)['fixed_mass_per_train_iqd']
        for case in supply.CASES:
            independent=fsum(r['cost_iqd'][case]/(vc['mass_reserve_sensitivity']['case_factors'][case]
                if r['line_key'].startswith('unlocated-account/') else 1) for r in vc['lines'])
            assert fixed[case]==pytest.approx(independent,abs=.02)


def test_owned_fixed_plant_counted_once_and_not_inside_vehicle_units(original):
    # Deliberately near-zero labour is a numerical boundary control to exercise
    # the make branch despite full premises costs, not an economic hypothesis
    # or a claim about current Iraqi wage evidence.
    hypothetical=deepcopy(original)
    hypothetical['assumption_values']['loaded_two_shift_skilled_wage_iqd_per_h']=[100.,150.,200.]
    hypothetical.pop('cost_estimate_id')
    hypothetical['cost_estimate_id']=identity(hypothetical)
    r=supply.revalue(hypothetical,dict(totalcars=312,total_trainsets=52),'project-make-buy')
    fx=r['assumptions']['iqd_per_usd']
    assert any(d.get('selected_route')=='make' for d in r['decisions'])
    for case in supply.CASES:
        expected=fsum(d['comparison']['cases'][case]['make']['fixed_total'] for d in r['decisions'] if d.get('selected_route')=='make')
        assert r['owned_factory_capital_usd'][case]==expected
        assert r['vehicle_cost']['separate_unamortized_factory_tooling_capital_iqd'][case]==pytest.approx(expected*fx,abs=.01)
    for d in r['decisions']:
        if d.get('selected_route')!='make':continue
        spec=d['comparison']['specification'];assert spec['committed_volume']==312 and spec['project_years']==3
        for case in supply.CASES:
            m=d['comparison']['cases'][case]['make']
            assert m['fixed_amortisation_volume']==312 and m['speculative_future_order_credit']==0
            assert m['cell_count']==max(1,ceil(m['required_cell_hours']/9000))
            assert m['fixed_components']['building']==0 and m['building_cost_reference']
            assert m['machine_rate_basis']=='cash-operating-excluding-capital-recovery'


def test_china_buy_never_charges_chinese_factory_hours_to_local_workplaces(outputs):
    r=outputs['china-bulk-buy'];assert all(v==0 for v in r['owned_factory_capital_usd'].values())
    assert r['cell_floor_m2']==[0,0,0]
    for d in r['decisions']:
        if d['disposition']!='revalued':continue
        assert d['selected_route']=='buy'
        assert not d['comparison']['cases']['base']['purchase']['extra_bulk_discount_applied']
        q=line(r['vehicle_cost'],d['line_key'])['quantity']
        hours=q.get('process_hours_per_car') or [h/6 for h in q['process_hours_per_train']]
        assert hours[1]<d['comparison']['cases']['base']['make']['labour_hours']/312


def test_bogie_only_frame_fraction_is_repriced_as_fabricated_stock(original,outputs):
    key='located-stock/passive-bogie-pair/steel'
    r=outputs['project-make-buy'];d=next(d for d in r['decisions'] if d['line_key']==key)
    original_mass=line(original,key)['quantity']['net_mass_kg_per_car']
    assert d['comparison']['specification']['make']['material']['net_quantity_per_unit']==pytest.approx(original_mass*.4)
    assert d['purchased_remaining_bogie_mass_fraction']==.6
    assert d['purchased_rolling_component_usd_per_kg']==dict(low=4.,base=8.,high=18.)
    assert line(r['vehicle_cost'],'unlocated-account/passive-bogie-pair')['cost_iqd']==line(original,'unlocated-account/passive-bogie-pair')['cost_iqd']
    assert all(v>0 for v in line(r['vehicle_cost'],key)['components_iqd']['purchased_precision_running_components'].values())


def test_no_cheap_hvac_or_battery_or_partial_seat_substitution(original,outputs):
    for r in outputs.values():
        for key in ('unlocated-account/services','unlocated-account/retained-comfort/HVAC',
                    'unlocated-account/retained-comfort/seating','located-stock/retained-comfort/seating/generic'):
            assert line(r['vehicle_cost'],key)['cost_iqd']==line(original,key)['cost_iqd']
        assert r['assumptions']['additional_bulk_discount'] is False
        # Aluminium is above current metal floor, even when catalogue advertisements are cheaper.
        assert r['assumptions']['raw_material_usd_per_kg']['aluminium']['low']>23787.1/1000/6.718


def test_decision_includes_local_indirects_before_base_choice(outputs):
    for d in outputs['project-make-buy']['decisions']:
        if d['disposition']!='revalued':continue
        make=d['make_total_including_production_indirects_usd']['base']
        buy=d['comparison']['cases']['base']['purchase']['total']
        assert d['selected_route']==('buy' if buy<=make else 'make')
        assert make==pytest.approx(d['comparison']['cases']['base']['make']['variable_total']*1.15+
            d['comparison']['cases']['base']['make']['fixed_total']+d['make_route_incremental_building_land_usd']['base'])


def test_quantity_changes_only_project_economics_not_physical_mass(original):
    a=supply.revalue(original,dict(totalcars=198,total_trainsets=33),'project-make-buy')
    b=supply.revalue(original,dict(totalcars=312,total_trainsets=52),'project-make-buy')
    assert a['vehicle_cost']['vehicle_account']==b['vehicle_cost']['vehicle_account']
    assert a['evaluation_id']!=b['evaluation_id']
    assert a['vehicle_cost']['upstream_cost_estimate_id']==b['vehicle_cost']['upstream_cost_estimate_id']


@pytest.mark.parametrize('service',[dict(totalcars=0,total_trainsets=0),dict(totalcars=312,total_trainsets=33),dict(totalcars=312.,total_trainsets=52)])
def test_inconsistent_commitment_is_rejected(original,service):
    with pytest.raises(ValueError,match='fleet'):
        supply.revalue(original,service,'project-make-buy')


def test_tampered_source_or_invalid_scenario_rejected(original):
    bad=deepcopy(original);bad['vehicle_account']['accounted_tare_kg_per_car']-=1
    with pytest.raises(ValueError,match='sealed'):
        supply.revalue(bad,dict(totalcars=312,total_trainsets=52),'project-make-buy')
    with pytest.raises(ValueError,match='scenario'):
        supply.revalue(original,dict(totalcars=312,total_trainsets=52),'automatic-cheapest-certified')


def test_evidence_observation_tamper_is_rejected(tmp_path):
    p=tmp_path/supply.DATA;p.parent.mkdir(parents=True)
    data=json.loads((Path(ROOT)/supply.DATA).read_bytes())
    data['observations'][0]['advertised_price']['low']=0.01
    p.write_text(json.dumps(data))
    with pytest.raises(ValueError,match='dataset identity'):
        supply._dataset(tmp_path)


def test_local_paid_idle_factor_is_applied_exactly_once_and_foreign_rates_stay_final(original,outputs):
    """Independent arithmetic control: source base paid wage11812.5IQD/h,75% productive."""
    r=outputs['china-bulk-buy'];fx=1510.;paid_base=11812.5/fx
    productive_base=11812.5/(1510.*.75)
    assert r['assumptions']['local_loaded_wage_usd_per_paid_hour']['base']==pytest.approx(paid_base)
    assert r['assumptions']['labour_usd_per_productive_hour']['base']==pytest.approx(productive_base)
    assert r['assumptions']['local_paid_hours_per_productive_hour']==pytest.approx(4/3)
    assert r['assumptions']['supplier_factory_labour_usd_per_h']['base']==8.
    for d in r['decisions']:
        if d['disposition']!='revalued':continue
        spec=d['comparison']['specification'];make=d['comparison']['cases']['base']['make']
        expected_make_labour=make['labour_hours']*11812.5/(1510.*.75)
        assert make['variable_components']['labour']==pytest.approx(expected_make_labour)
        # These negative controls reject both the original omission and double loading.
        assert make['variable_components']['labour']!=pytest.approx(make['labour_hours']*paid_base)
        assert make['variable_components']['labour']!=pytest.approx(expected_make_labour/.75)
        assert make['labour_rate_basis']=='productive-hour-loaded'
        assert make['paid_hours_per_productive_hour']==1.
        mass=spec['make']['material']['net_quantity_per_unit']
        expected_receiving=312*(mass*.15+mass*.008*productive_base)
        actual=d['comparison']['cases']['base']['purchase']['components']['QA']
        assert actual==pytest.approx(expected_receiving)
        assert actual!=pytest.approx(312*(mass*.15+mass*.008*paid_base))
        assert actual!=pytest.approx(312*(mass*.15+mass*.008*productive_base/.75))
    bogie=line(r['vehicle_cost'],'located-stock/passive-bogie-pair/steel')
    mass=line(original,'located-stock/passive-bogie-pair/steel')['quantity']['net_mass_kg_per_car']
    assert bogie['components_iqd']['precision_component_local_fit_labour']['base']==pytest.approx(
        mass*.6*.02*11812.5/.75*6,abs=.01)


def test_incremental_owned_premises_influence_selection_but_are_not_charged_twice(outputs):
    r=outputs['project-make-buy']
    for d in r['decisions']:
        if d['disposition']!='revalued':continue
        recipe=supply._RECIPES[line(r['vehicle_cost'],d['line_key'])['supply_scenario']['recipe']]
        for i,case in enumerate(supply.CASES):
            # Independently declared campaign rates: building and purchased land,
            # including the same1.5storage factor used by parent factory allocation.
            per_m2=(250000.,600000.,1500000.)[i]+(25000.,75000.,250000.)[i]
            expected=d['comparison']['cases'][case]['make']['cell_count']*recipe['floor']*1.5*per_m2/1510.
            assert d['make_route_incremental_building_land_usd'][case]==pytest.approx(expected)
            assert d['comparison']['cases'][case]['make']['fixed_components']['building']==0
    assert 'global optimum not established' in r['assumptions']['route_selection']


def test_final_local_assembly_also_recovers_paid_idle_once(original,outputs):
    for r in outputs.values():
        row=line(r['vehicle_cost'],'six-car-final-vehicle-assembly')
        for i,case in enumerate(supply.CASES):
            hours=(8.,24.,80.)[i]*6
            expected=hours*(9375.,11812.5,16500.)[i]/.75
            assert row['components_iqd']['labour'][case]==pytest.approx(expected,abs=.01)
            assert row['components_iqd']['equipment'][case]==line(original,row['line_key'])['components_iqd']['equipment'][case]
        assert r['vehicle_cost']['final_vehicle_assembly_cost_iqd_per_train']==row['cost_iqd']


def test_long_import_transport_scope_is_counted_once_before_route_selection(outputs):
    expected={
        'located-stock/wheel-underframe/aluminium':(2000.,5000.,12000.),
        'located-stock/retained-comfort/body/generic':(1500.,5000.,18000.),
        'unlocated-account/retained-comfort/body':(1500.,5000.,18000.),
    }
    r=outputs['project-make-buy'];observed={c:0. for c in supply.CASES}
    for d in r['decisions']:
        if d['disposition']!='revalued':continue
        spec=d['comparison']['specification'];mass=spec['make']['material']['net_quantity_per_unit']
        for i,case in enumerate(supply.CASES):
            increment=expected.get(d['line_key'],(0.,0.,0.))[i]
            freight=mass*(.18,.35,.65)[i]+increment
            assert spec['purchase']['landed']['freight_per_unit'][case]==pytest.approx(freight)
            assert spec['purchase']['long_load_packing_volumetric_increment_usd_per_unit'][case]==increment
            assert d['comparison']['cases'][case]['purchase']['components']['freight']==pytest.approx(312*freight)
            observed[case]+=increment
        # The base choice is held for every uncertainty case; a cheap low-case\n        # alternative does not silently replace the selected physical supply route.
        selected=line(r['vehicle_cost'],d['line_key'])['supply_scenario']['selected_route']
        assert selected==d['selected_route']
        assert selected==('buy' if d['comparison']['cases']['base']['purchase']['total']<=
            d['make_total_including_production_indirects_usd']['base'] else 'make')
        if d['line_key'] in expected:
            actual=line(r['vehicle_cost'],d['line_key'])
            for i,case in enumerate(supply.CASES):
                kernel=d['comparison']['cases'][case]['make' if selected=='make' else 'purchase']
                variable=kernel['variable_total']*(1+(.10,.15,.25)[i]) if selected=='make' else kernel['total']
                factor=(.8,1.,1.2)[i] if d['line_key'].startswith('unlocated-account/') else 1.
                assert actual['cost_iqd'][case]==pytest.approx(variable/312*6*1510.*factor,abs=.011)
    assert observed==dict(low=5000.,base=15000.,high=48000.)
