from copy import deepcopy
from pathlib import Path
import importlib.util
import pytest

FILE=Path(__file__).resolve().parents[1]/'engineering/outline/delivery_plan.py'
spec=importlib.util.spec_from_file_location('delivery_plan_under_test',FILE)
dp=importlib.util.module_from_spec(spec);spec.loader.exec_module(dp)


def reseal(value,key):value.pop(key,None);return dp.seal(value,key)


def city():
    flags={k:False for k in ('physical_accepted','engineering_accepted','manufacturing_release','operating_release','movement_authority')}
    refs=dict(candidate_id='a'*64,body_candidate_id='b'*64,support_component_id='c'*64,propulsion_component_id='d'*64)
    geo=dp.seal(dict(city=dict(slug='fixture',name='Fixture',country='XX'),lines=[dict(line_id='A')],source_sha256={}), 'input_id')
    cfg=dict(reference_candidate_ids=refs,city_input_id=geo['input_id'],line_research_configurations=[])
    services=dp.seal(dict(city_input_id=geo['input_id'],line_services=[dict(requirements=dict(operating_hours_per_day=18.,operating_days_per_year=365))]),'evaluation_id')
    vc=dp.seal(dict(candidate_id=refs['candidate_id'],mass_reserve_sensitivity=dict(case_factors=dict(low=.8,base=1.,high=1.2)),lines=[
        dict(line_key='located-stock/body/aluminium',line_id='part',quantity=dict(process_hours_per_car=[2.,3.,4.]),cost_iqd=dict(low=10000.,base=20000.,high=40000.)),
        dict(line_key='six-car-final-vehicle-assembly',line_id='assembly',quantity=dict(labour_hours_per_car=[8.,24.,80.]),cost_iqd=dict(low=1000.,base=2000.,high=4000.))]),'cost_estimate_id')
    def row(k,s,q):return dict(key=k,scope=s,quantity=q,costs_usd=dict(low=10000.,base=20000.,high=40000.),line_id='line-'+k)
    capital=[row('citywide-production-equipment-tools-buildings-yards','factory-tooling',dict(committed_cars=6,assembly_bays=[1,1,1],precast_floor_m2=[0.,0.,0.])),
        row('network-delivered-assembled-fleet','rolling-stock',{}),row('design-prototypes-independent-review','construction',{}),row('piers-and-foundations','construction',{}),row('transport-crane-erection-track-install','construction',{}),row('access-and-power','stations-power',{})]
    cost=dp.seal(dict(city_input_id=geo['input_id'],input_line_services_id=dp.identity(services['line_services']),
        production_supply=dict(vehicle_cost=vc,assumptions=dict(iqd_per_usd=1510),decisions=[]),resources=dict(total_trainsets=1,totalcars=6,production_positions_per_shift=[6,8,12],access_sites=2),
        capital_lines=capital,lifecycle_lines=[],installed_capital_usd=dict(low=60000.,base=120000.,high=240000.),whole_life_npv_usd=dict(low=90000.,base=180000.,high=360000.),
        civil=dict(quantities=dict(span_count=0,independent_supports=0),factory_decision=dict(selected_route='local-contractor',comparison={})),source_sha256={},**flags),'evaluation_id')
    return dp.seal(dict(city=geo['city'],input_id=geo['input_id'],cost=cost,geometry_and_service=geo,service_evaluation=services,reference_candidate_ids=refs,
        research_configuration=cfg,research_configuration_id=dp.identity(cfg),selection_id='e'*64,source_sha256={},**flags),'evaluation_id')


def test_sealed_complete_plan_unchanged_inputs_budget_and_two_shifts(tmp_path):
    c=city();before=deepcopy(c);p=dp.evaluate(c,root=tmp_path)
    assert c==before and p['plan_id']==dp.identity({k:v for k,v in p.items() if k!='plan_id'})
    assert p['cost_evaluation_id']==c['cost']['evaluation_id'] and p['research_configuration_id']==c['research_configuration_id']
    assert p['cost_reconciliation']['source_capital_usd']==c['cost']['installed_capital_usd']
    assert all(x==0 for x in p['cost_reconciliation']['additional_cost_usd'].values())
    assert all(p[k] is False for k in dp.FLAGS)
    assert p['items'] and p['boms'] and p['production_groups']
    shift=p['workforce']['shift_patterns'][0]
    assert (shift['shifts_per_day'],shift['hours_per_shift'],shift['days_per_year'])==(2,8.,250)
    assert shift['two_shift_distinct_people']['base']==16


def test_resource_precedence_and_material_flow(tmp_path):
    p=dp.evaluate(city(),root=tmp_path);tasks={t['task_id']:t for t in p['tasks']}
    for case,sc in p['schedule']['cases'].items():
        assert sc['capacity_pass'] is True
        rows={r['task_id']:r for r in sc['tasks']}
        for key,row in rows.items():assert all(rows[x]['finish_workday']<=row['start_workday']+1e-9 for x in tasks[key]['predecessors'])
    assert all(z['nonnegative_stock_by_precedence'] for z in p['material_flow']['checks'])


def test_bom_six_cars_and_assembly_workstation_vs_person_hours(tmp_path):
    p=dp.evaluate(city(),root=tmp_path);train=next(z for z in p['items'] if z['name']=='Six-car train account assembly')
    bom=next(z for z in p['boms'] if z['item_code']==train['item_code']);assert bom['items'][0]['qty']==6
    op=next(g for g in p['production_groups'] if g['item_code']==train['item_code'])['operations'][0]
    assert op['person_hours_per_unit']['base']==144 and op['hours_per_unit']['base']==24


def test_24hour_operation_uses_three_shifts(tmp_path):
    c=city();c['service_evaluation']['line_services'][0]['requirements']['operating_hours_per_day']=24
    reseal(c['service_evaluation'],'evaluation_id');c['cost']['input_line_services_id']=dp.identity(c['service_evaluation']['line_services']);reseal(c['cost'],'evaluation_id');reseal(c,'evaluation_id')
    op=dp.evaluate(c,root=tmp_path)['workforce']['shift_patterns'][-1]
    assert op['shifts_per_day']==3 and op['hours_per_shift']==8


def test_stale_or_mixed_service_identity_rejected(tmp_path):
    c=city();c['cost']['resources']['totalcars']=7
    with pytest.raises(ValueError,match='identity'):dp.evaluate(c,root=tmp_path)
    c=city();c['cost']['input_line_services_id']='wrong';reseal(c['cost'],'evaluation_id');reseal(c,'evaluation_id')
    with pytest.raises(ValueError,match='service/cost'):dp.evaluate(c,root=tmp_path)


def test_missing_local_labour_does_not_turn_zero(tmp_path):
    c=city();vc=c['cost']['production_supply']['vehicle_cost'];vc['lines'][0]['quantity']['process_hours_per_car']=[0.,0.,0.]
    reseal(vc,'cost_estimate_id');reseal(c['cost'],'evaluation_id');reseal(c,'evaluation_id')
    with pytest.raises(ValueError,match='labour'):dp.evaluate(c,root=tmp_path)


def test_scheduler_resource_nonoverlap_and_cycle_rejection():
    r=[dict(resource_id='R',capacity_by_case=dict(low=1,base=1,high=1))]
    def t(k,h,p=()):return dict(task_id=k,predecessors=list(p),duration_workdays=dict(low=h,base=h,high=h),resource_requests=[dict(resource_id='R',units=1)])
    s=dp._schedule([t('A',2),t('B',3),t('C',1,['B'])],r,'base')
    assert s['capacity_pass'] and s['finish_workday']==6
    with pytest.raises(ValueError,match='Cyclic'):dp._schedule([t('A',2,['B']),t('B',1,['A'])],r,'base')


def test_unsatisfied_capacity_is_explicit_no_free_units():
    r=[dict(resource_id='R',capacity_by_case=dict(low=1,base=1,high=1))]
    t=dict(task_id='T',predecessors=[],duration_workdays=dict(low=2,base=2,high=2),resource_requests=[dict(resource_id='R',units=2)])
    s=dp._schedule([t],r,'base');assert s['capacity_pass'] is False
    assert s['tasks'][0]['status']=='unpriced-resource-hold' and not s['tasks'][0]['resource_allocations']


@pytest.mark.parametrize('policy',[{'delivery':{'shifts_per_day':1}},{'delivery':{'utilisation':1}},{'delivery':{'maximum_batches':0}}])
def test_policy_cannot_invent_priced_capacity(policy,tmp_path):
    with pytest.raises(ValueError):dp.evaluate(city(),policy,root=tmp_path)


def test_lot_coarsening_conserves_all_committed_trains_and_bom_rates(tmp_path):
    c=city();c['cost']['resources'].update(total_trainsets=137,totalcars=822)
    c['cost']['capital_lines'][0]['quantity']['committed_cars']=822
    reseal(c['cost'],'evaluation_id');reseal(c,'evaluation_id')
    p=dp.evaluate(c,{'delivery':{'maximum_batches':2}},root=tmp_path)
    assembled=[t for t in p['tasks'] if t['name']=='Final assembly, interfaces and test batch']
    assert len(assembled)==2 and sum(t['quantity'] for t in assembled)==137
    assert len(p['tasks'])<=5000
    items={x['item_code']:x for x in p['items']}
    for bom in p['boms']:
        for row in bom['items']:
            assert items[row['item_code']]['unit_cost_usd']['base']>0


def test_external_planning_revision_and_time_overhead_not_zero_or_double_capex(tmp_path):
    c=city();c['planning_revision_id']='explicit-edited-plan'
    # Force a clear commercial delay, without changing owned factory capacity.
    reseal(c,'evaluation_id')
    p=dp.evaluate(c,{'delivery':{'supplier_delivery_target_workdays':[1000.,1200.,1500.]}},root=tmp_path)
    assert p['planning_revision_id']=='explicit-edited-plan' and p['city_input_id']==c['input_id']
    r=p['cost_reconciliation'];assert r['overrun_overhead_estimate_usd']['base']>0
    assert r['uncovered_overrun_usd']['base']>0
    assert r['additional_cost_usd']['base']==0 and r['factory_capital_counted_again'] is False
    assert any(t['kind']=='uncovered-programme-overrun-budget' for t in p['next_tasks'])


def test_actual_330day_operations_roster_and_paid_relief_without_second_cost(tmp_path):
    c=city();c['service_evaluation']['line_services'][0]['requirements']['operating_days_per_year']=330
    reseal(c['service_evaluation'],'evaluation_id');c['cost']['input_line_services_id']=dp.identity(c['service_evaluation']['line_services']);reseal(c['cost'],'evaluation_id');reseal(c,'evaluation_id')
    p=dp.evaluate(c,root=tmp_path);ops=p['workforce']['shift_patterns'][-1]
    assert ops['days_per_year']==330 and ops['shifts_per_day']==2
    assert ops['positions_by_case']==ops['covered_positions_per_shift']
    covered=4+2*2
    assert ops['covered_positions_per_shift']['base']==covered
    assert ops['covered_shift_slots_per_day']['base']==covered*2
    assert ops['costed_relief_multiplier_by_case']['base']==1.25
    assert ops['budgeted_paid_hours_per_year_including_relief']['base']==covered*18*330*1.25
    assert ops['paid_fte_equivalent_by_case']['base']==covered*18*330*1.25/2000
    assert ops['relief_fte_equivalent_by_case']['base']==covered*18*330*.25/2000
    assert ops['relief_already_in_source_operations_cost'] is True
    assert ops['additional_workforce_cost_added'] is False
    assert p['cost_reconciliation']['additional_cost_usd']['base']==0


def test_default_365day_coverage_is_retained(tmp_path):
    ops=dp.evaluate(city(),root=tmp_path)['workforce']['shift_patterns'][-1]
    assert ops['days_per_year']==365
    assert ops['costed_relief_multiplier_by_case']==dict(low=1.1,base=1.25,high=1.5)


def test_exact_source_bound_relief_literals_are_read_not_overridden(tmp_path):
    name='engineering/design_search/model_cost.py';path=tmp_path/name;path.parent.mkdir(parents=True)
    path.write_text('def assumptions():\n return dict(controllers_per_shift=[3,5,9], station_staff_per_station_per_shift=[1,2,4], operations_reliever_multiplier=[1.2,1.4,1.8])\n')
    c=city();c['cost']['source_sha256'][name]=dp.digest(path);reseal(c['cost'],'evaluation_id');reseal(c,'evaluation_id')
    ops=dp.evaluate(c,root=tmp_path)['workforce']['shift_patterns'][-1]
    assert ops['costed_relief_multiplier_by_case']['base']==1.4
    assert ops['covered_positions_per_shift']['base']==9
    assert ops['costed_assumption_source_sha256']==dp.digest(path)
