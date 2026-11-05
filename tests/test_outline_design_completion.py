import gzip
import json
from copy import deepcopy
from pathlib import Path

import pytest

from engineering.outline import design_completion as completion
from engineering.station_rail.common import identity


def minimal_policy():
    return dict(policy_id='explicit-numerical-fixture',purchase_yield=[.5,.5,.5],
        material_iqd_per_kg={k:[2.,2.,2.] for k in ('aluminium','steel','composite','generic')},
        labour_h_per_kg=[.1,.1,.1],setup_h_per_part=[1.,1.,1.],
        productive_labour_iqd_per_h=[3.,3.,3.],machine_h_per_kg=[.2,.2,.2],
        machine_cash_iqd_per_h=[4.,4.,4.],consumables_iqd_per_kg=[.5,.5,.5],
        qa_iqd_per_kg=[.25,.25,.25],overhead_fraction=[.1,.1,.1])


def source_row():
    cost=dict(candidate_id='bundle-A',model_cost_complete_for_declared_case=True,model_cost_missing_scopes=[],
        evaluation_id=None,assumption_id='historical-assumption',
        provisional_manufacturing_plan=dict(routes=[dict(cost_line_id='stock-line',candidate_id='bundle-A',
            nominal_mass_kg_per_car=10.,material_id='aluminium_reference',
            labor_hours_per_car=dict(low=2.,base=3.,high=4.),provisional_process='candidate-cut-drill-join')]),
        cost_line_items=[dict(candidate_id='bundle-A',line_id='stock-line',line_key='vehicle-stock/x',
            quantity=dict(per_car_mass_kg=10.),scenario_iqd=dict(low=100.,base=100.,high=100.)),
            dict(candidate_id='bundle-A',line_key='bounded-equipment',scenario_iqd=dict(low=200.,base=200.,high=200.))],
        corridor_basis=dict(fleet_cars=12,cars_per_train=6,directional_route_m=6000,stations=3),
        model_based_installed_CAPEX_iqd=[1000.]*3,model_based_whole_life_NPV_iqd=[2000.]*3,
        scope_totals_iqd={'rolling-stock':[300.]*3,**{'scope'+str(i):[100.]*3 for i in range(13)}})
    cost.pop('evaluation_id');cost['evaluation_id']=identity(cost)
    return dict(candidate_id='bundle-A',body_candidate_id='body-A',economics=dict(model_cost=cost))


def test_stock_arithmetic_is_quantity_process_and_material_specific():
    p=minimal_policy();parts=[dict(mass_kg=10.,material_id='aluminium_reference')]
    result=completion._stock(parts,p,fleet=12)
    # Material20kg*2,labour2h*3,machine2h*4,consumables5,QA2.5,overhead10%.
    expected=(40+6+8+5+2.5)*1.1*12
    assert result['cost_iqd']==pytest.approx([expected]*3)
    assert result['net_stock_kg']==10 and result['material_mass_kg']=={'aluminium':10.}
    specified=completion._stock([dict(mass_kg=10.,material_id='steel',process_hours=dict(low=5.,base=6.,high=7.))],p)
    assert specified['process_hours']==[5.,6.,7.]
    assert specified['material_mass_kg']=={'steel':10.}


def test_railway_reprices_only_this_candidates_stock_and_retains_reserves():
    source=source_row();before=deepcopy(source);result=completion._railway(source,minimal_policy())
    assert source==before
    assert result['physical_candidate_id']=='bundle-A'
    assert result['quantity']['body_candidate_id']=='body-A'
    assert result['replaced_stock_line_count']==1 and result['retained_bounded_line_count']==1
    assert result['quantity']['stock']['process_hours']==[24.,36.,48.]
    for i,c in enumerate(completion.CASES):
        delta=result['quantity']['stock']['cost_iqd'][i]-100
        assert result['prices_iqd']['installed_capital'][c]==pytest.approx(1000+delta)
        assert result['prices_iqd']['whole_life_npv'][c]==pytest.approx(2000+delta)
        assert result['scope_totals_iqd']['scope0'][i]==100
    assert result['design_stage_cost_complete'] is True
    assert all(result[k] is False for k in completion.FLAGS)
    assert result['evaluation_id']==identity({k:v for k,v in result.items() if k!='evaluation_id'})


def test_mixed_candidate_or_tampered_source_cannot_reprice():
    source=source_row();source['economics']['model_cost']['candidate_id']='other'
    with pytest.raises(ValueError,match='identity'):
        completion._railway(source,minimal_policy())
    source=source_row();cost=source['economics']['model_cost'];cost['cost_line_items'][0]['candidate_id']='other'
    cost.pop('evaluation_id');cost['evaluation_id']=identity(cost)
    with pytest.raises(ValueError,match='Mixed'):
        completion._railway(source,minimal_policy())


def test_missing_material_process_binding_is_not_zero():
    source=source_row();cost=source['economics']['model_cost'];cost['provisional_manufacturing_plan']['routes']=[]
    cost.pop('evaluation_id');cost['evaluation_id']=identity(cost)
    with pytest.raises(ValueError,match='Missing'):
        completion._railway(source,minimal_policy())
    with pytest.raises(ValueError,match='Positive'):
        completion._stock([dict(mass_kg=0.,material_id='steel')],minimal_policy())


def test_streaming_array_integrity(tmp_path):
    path=tmp_path/'records.json.gz'
    path.write_bytes(gzip.compress(json.dumps([{'a':1},{'b':2}]).encode()))
    assert list(completion._array(path))==[{'a':1},{'b':2}]
    path.write_bytes(gzip.compress(b'[{"a":1}] trailing'))
    with pytest.raises(ValueError,match='Trailing'):
        list(completion._array(path))
    path.write_bytes(gzip.compress(b'[{"a":1},'))
    with pytest.raises(ValueError,match='Truncated'):
        list(completion._array(path))


def test_current_rates_do_not_apply_bulk_discount_or_copy_selected_prices():
    p=completion.policy()
    assert p['extra_bulk_discount'] is False and p['paid_idle_factor']==pytest.approx(4/3)
    assert p['material_iqd_per_kg']['aluminium'][0]>23787.1/1000/6.718*1510
    assert p['productive_labour_iqd_per_h'][1]==11812.5/.75
    assert p['policy_id']==identity({k:v for k,v in p.items() if k!='policy_id'})


def test_quantified_reinforcement_changes_guideway_once_without_discounting_reserves():
    source=source_row();cost=source['economics']['model_cost']
    cost['scope_totals_iqd'].pop('scope0')
    cost['scope_totals_iqd']['guideway']=[1000.]*3
    cost['cost_line_items'].append(dict(candidate_id='bundle-A',line_id='reinforcement-line',
        line_key='precast-reinforcement',quantity=dict(reinforcement_kg=100.),
        scenario_iqd=dict(low=500.,base=500.,high=500.)))
    cost.pop('evaluation_id');cost['evaluation_id']=identity(cost)
    p=minimal_policy();p['rebar_iqd_per_kg']=[1.,2.,3.]
    result=completion._railway(source,p)
    assert len(result['other_quantified_price_adjustments'])==1
    for i,c in enumerate(completion.CASES):
        stock_delta=result['quantity']['stock']['cost_iqd'][i]-100
        rebar_delta=100*(i+1)-500
        assert result['prices_iqd']['installed_capital'][c]==pytest.approx(1000+stock_delta+rebar_delta)
        assert result['prices_iqd']['whole_life_npv'][c]==pytest.approx(2000+stock_delta+rebar_delta)
        assert result['scope_totals_iqd']['guideway'][i]==pytest.approx(1000+rebar_delta)


def test_streaming_reader_handles_record_exactly_at_initial_chunk_boundary(tmp_path):
    # Opening bracket plus the first record ends exactly at the first read limit.
    head=json.dumps({'x':'a'*((1<<20)-10)},separators=(',',':'))
    assert len(head)+1==(1<<20)-1
    # Adjust independently; json escaping overhead is fixed for this ASCII fixture.
    head=json.dumps({'x':'a'*((1<<20)-9)},separators=(',',':'))
    assert len(head)+1==(1<<20)
    p=tmp_path/'boundary.json.gz';p.write_bytes(gzip.compress(('['+head+',{"y":2}]').encode()))
    rows=list(completion._array(p));assert len(rows)==2 and rows[1]=={'y':2}


def body_fixture():
    return dict(parameters=dict(length_m=17.,width_m=2.65),parts=[
        dict(id='member',kind='oriented-RHS',mass_kg=10.,material_id='aluminium_reference',manufacturing_occurrence_id='member'),
        dict(id='skin',kind='box',mass_kg=5.,material_id='gfrp',size_m=[2.,1.,.002],manufacturing_occurrence_id='panel'),
        dict(id='core',kind='box',mass_kg=2.,material_id='foam',size_m=[2.,1.,.025],manufacturing_occurrence_id='panel')],
        joins=[dict(id='joint',part_ids=['member'],net_hardware_mass_kg=None)],
        connections=[dict(id='member/end',**{'from':['member','end'],'to':['joint','load']})],
        components=[dict(occurrence_id='joint',inventory_status='unknown'),dict(occurrence_id='support',inventory_status='unknown')])


def test_body_scope_prices_missing_hardware_assembly_handling_inspection_and_tooling_once():
    body=body_fixture();before=deepcopy(body);p=completion.policy()
    stock=completion._stock(body['parts'],p);outline=completion._body_outline(body,stock,p)
    q=outline['quantity']
    assert body==before and outline['installed_mass_qualified'] is False
    # One explicit joint + one other declared unknown + two unrepresented parts.
    assert q['priced_joint_locations']==4
    assert q['unrepresented_part_ids']==['core','skin']
    # Shared sandwich skins/core have one6m boundary, not two seams.
    assert q['panel_manufacturing_group_count']==1 and q['attachment_boundary_m']==6
    assert q['fastener_units']['base']==16
    assert q['connector_hardware_mass_reserve_kg']['base']==pytest.approx(4*1.2)
    assert q['adhesive_mass_reserve_kg']['base']==pytest.approx(6*.08)
    assert q['total_added_hardware_mass_reserve_kg']['base']==pytest.approx(4*1.2+16*.08+6*.08)
    for i,case in enumerate(completion.CASES):
        additions=sum(v[i] for v in outline['additional_repeat_components_iqd'].values())
        assert all(v[i]>0 for v in outline['additional_repeat_components_iqd'].values())
        assert outline['repeat_factory_gate_iqd'][i]==pytest.approx(stock['cost_iqd'][i]+additions)
        assert outline['one_time_tooling_setup_iqd'][i]>0
        assert outline['first_body_total_iqd'][i]==pytest.approx(outline['repeat_factory_gate_iqd'][i]+outline['one_time_tooling_setup_iqd'][i])
    assert outline['body_outline_cost_complete'] is True


def test_body_unknown_attachment_is_a_positive_named_reserve_not_free():
    body=body_fixture();body.update(joins=[],connections=[],components=[])
    p=completion.policy();stock=completion._stock(body['parts'],p)
    outline=completion._body_outline(body,stock,p)
    assert outline['quantity']['unrepresented_part_attachment_reserve_count']==3
    assert outline['quantity']['total_added_hardware_mass_reserve_kg']['low']>0
    body['parts']=[body['parts'][0]]
    outline=completion._body_outline(body,completion._stock(body['parts'],p),p)
    assert outline['quantity']['attachment_boundary_m']==2*(17+2.65)
    assert 'reserve' in outline['quantity']['attachment_boundary_basis']


def test_resume_source_inventory_includes_every_design_packet_and_rate_source():
    bound=completion.sources()
    for name in ('coupled-railway/comparison.json.gz','breadth-first-shape-portfolio/result.json',
                 'breadth-first-shape-portfolio/candidates.json.gz','civil-shape-portfolio/result.json',
                 'civil-shape-portfolio/candidates.json.gz'):
        assert completion.BASE+name in bound
    assert completion.VEHICLE_RATE_SOURCE in bound
    assert completion.vehicle_supply.DATA in bound
    assert completion.PRODUCER in bound
    for name in completion.PACKETS:
        assert completion.BASE+name+'/manifest.json' in bound
