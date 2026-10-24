"""Planning revisions, real geographical constraints and resource/ERP controls."""
from copy import deepcopy
from pathlib import Path
import sqlite3
import pytest
from engineering.ferrite_maglev import delivery_platform as p

@pytest.fixture(scope='module')
def plan():return p.baseline(p.ROOT/'cities/catalogue/west-asia/Iraq/Baghdad')

def test_current_geography_and_proposed_stops_are_consistent(plan):
    assert p.validate(plan) is plan
    assert len(plan['lines'])==14 and sum(len(l['stops']) for l in plan['lines'])==273
    assert len(p.LAYERS)==16 and not plan['physical_release']
    assert any(i['state']=='spacing-exception' for i in p.issues(plan))

def test_revision_is_immutable_optimistic_and_replayable(plan,tmp_path):
    store=p.RevisionStore(tmp_path/'revisions.sqlite');assert store.append(plan);assert not store.append(plan)
    line=plan['lines'][-1];stop=line['stops'][1]
    edited=p.revise(plan,[dict(kind='move-stop',line=line['id'],stop=stop['id'],chainage_m=stop['chainage_m']+10)],expected_revision_sha256=plan['revision_sha256'],actor='planner-a')
    assert edited['revision']==2 and edited['parent_revision_sha256']==plan['revision_sha256']
    assert edited['lines'][-1]['stops'][1]['chainage_m']==stop['chainage_m']+10
    assert store.append(edited) and store.latest('baghdad')==edited
    with pytest.raises(ValueError,match='stale'):store.append(p.revise(plan,[dict(kind='set-service',line=line['id'],headway_s=250,dwell_s=60)],expected_revision_sha256=plan['revision_sha256'],actor='planner-b'))
    with sqlite3.connect(store.path) as db:
        with pytest.raises(sqlite3.IntegrityError,match='immutable'):db.execute('DELETE FROM revisions')
    assert p.RevisionStore(store.path).latest('baghdad')==edited

def test_edit_does_not_adopt_headway_or_reuse_stale_demand(plan):
    line=plan['lines'][-1]
    edited=p.revise(plan,[dict(kind='set-service',line=line['id'],headway_s=30,dwell_s=80)],expected_revision_sha256=plan['revision_sha256'],actor='planner')
    assert any(i['id']==line['id']+'/headway' and i['state']=='hold' for i in p.issues(edited))
    assert not edited['movement_authority'] and edited['od']==[]
    with pytest.raises(ValueError,match='stale'):p.revise(plan,[],expected_revision_sha256='f'*64,actor='planner')

def test_invalid_station_order_nan_and_unknown_edits_refused(plan):
    l=plan['lines'][-1]
    for edit in [dict(kind='move-stop',line=l['id'],stop=l['stops'][1]['id'],chainage_m=0),
                 dict(kind='set-service',line=l['id'],headway_s=float('nan'),dwell_s=60),dict(kind='send-motion-command',line=l['id'])]:
        with pytest.raises(ValueError):p.revise(plan,[edit],expected_revision_sha256=plan['revision_sha256'],actor='planner')
    altered=deepcopy(plan);altered['lines'][0]['coordinates'][0][0]+=.01
    altered=p.seal(altered)
    with pytest.raises(ValueError,match='length differs'):p.validate(altered)

def test_od_requires_existing_distinct_stops_and_declared_basis(plan):
    l=plan['lines'][-1];row=dict(origin=l['stops'][0]['id'],destination=l['stops'][1]['id'],trips_per_day=123,basis='synthetic')
    edited=p.revise(plan,[dict(kind='set-od',rows=[row])],expected_revision_sha256=plan['revision_sha256'],actor='planner')
    assert edited['od']==[row]
    for rows in ([row,row],[dict(row,basis='accepted')],[dict(row,destination='missing')],[dict(row,trips_per_day=-1)]):
        with pytest.raises(ValueError):p.revise(plan,[dict(kind='set-od',rows=rows)],expected_revision_sha256=plan['revision_sha256'],actor='planner')

def test_generic_resources_do_not_overlap_and_cycles_refuse():
    tasks=[dict(id='a',hours=8,depends=[],resource='crane'),dict(id='b',hours=8,depends=[],resource='crane'),dict(id='c',hours=1,depends=['a'],resource='survey')]
    one=p.resource_schedule(tasks,dict(crane=1,survey=1));two=p.resource_schedule(tasks,dict(crane=2,survey=1))
    a={r['id']:r for r in one};assert a['b']['start_h']>=a['a']['end_h'] and a['c']['start_h']>=a['a']['end_h']
    assert max(r['end_h'] for r in two)<max(r['end_h'] for r in one)
    tasks[0]['depends']=['c']
    with pytest.raises(ValueError,match='cyclic'):p.resource_schedule(tasks,dict(crane=1,survey=1))


def material_plan():
    points=[[44.,33.],[44.002,33.]]
    length=p.operating_plan.distance(*points)
    stops=[dict(id=f's{i}',chainage_m=at,lon=point[0],lat=point[1],dwell_s=60.,mandatory_junction_ids=[])
           for i,(at,point) in enumerate(((0.,points[0]),(length,points[1])))]
    return p.seal(dict(schema=p.SCHEMA,city='fixture',revision=1,parent_revision_sha256=None,
        actor='test',environment='planning',source_sha256={},interchanges=[],od=[],changes=[],
        lines=[dict(id='test/line',coordinates=points,length_m=length,stops=stops,
                    headway_s=180.,planning_minimum_headway_s=180.,cars=6)],**p.FLAGS))


def test_material_lead_times_precede_first_consumption_and_move_schedule_and_cash():
    plan=material_plan();rates=dict(guidebeam=100.,support=200.,station=300.)
    short=p.project_twin(plan,configuration_sha256='a'*64,unit_costs=rates,
                         procurement_lead_days=dict(guidebeam=1.,support=1.,station=1.))
    delayed=p.project_twin(plan,configuration_sha256='a'*64,unit_costs=rates,
                           procurement_lead_days=dict(guidebeam=400.,support=1.,station=1.))
    for twin in (short,delayed):
        by={task['id']:task for task in twin['tasks']}
        for purchase in twin['procurement']:
            assert purchase['order_by_day']>=0
            assert purchase['planned_arrival_day']==pytest.approx(purchase['order_by_day']+purchase['lead_days'])
            consumers=[by[need['consuming_task_id']] for need in twin['material_need_tasks']
                       if need['product']==purchase['product']]
            assert purchase['need_by_day']==min(task['start_h']/24 for task in consumers)
            assert all(task['start_h']>=purchase['planned_arrival_day']*24 for task in consumers)
            for need in twin['material_need_tasks']:
                assert need['availability_task_id'] in by[need['id']]['depends']
                assert need['id'] in by[need['consuming_task_id']]['depends']
            assert not purchase['actual_receipt_recorded']
        assert sum(row['cash_usd'] for row in twin['monthly_cash'])==pytest.approx(twin['priced_subtotal_usd'])
    cast=lambda twin:min(task['start_h'] for task in twin['tasks'] if task['id'].endswith('/cast'))
    assert cast(delayed)-cast(short)>350*24
    assert delayed['completion_calendar_days']>short['completion_calendar_days']+350
    assert delayed['monthly_cash']!=short['monthly_cash']


def test_selected_span_changes_whole_beam_support_quantities_and_bad_lead_refused():
    plan=material_plan()
    a=p.project_twin(plan,configuration_sha256='a'*64,beam_span_m=25.)
    b=p.project_twin(plan,configuration_sha256='a'*64,beam_span_m=15.)
    assert a['quantities'][0]['quantity']<b['quantities'][0]['quantity']
    assert a['quantities'][1]['quantity']<b['quantities'][1]['quantity']
    for bad in ({'guidebeam':-1},{'guidebeam':float('nan')},{'unknown':10}):
        with pytest.raises(ValueError):p.project_twin(plan,configuration_sha256='a'*64,procurement_lead_days=bad)

@pytest.mark.parametrize('relative',['east-africa/Kenya/Garissa','central-africa/DR Congo/Kisangani','west-asia/Iraq/Baghdad'])
def test_any_city_plan_compiles_through_retained_erp_adapter(relative):
    plan=p.baseline(p.ROOT/'cities/catalogue'/relative)
    # One line is sufficient to exercise the generic adapter without a whole
    # city's programme pretending to be a qualified engineering package.
    plan['lines']=plan['lines'][-1:];plan=p.seal(plan)
    twin=p.project_twin(plan,configuration_sha256='a'*64,unit_costs=dict(guidebeam=100,support=200,station=300))
    assert twin['planning_revision_sha256']==plan['revision_sha256'] and twin['configuration_sha256']=='a'*64
    assert twin['registered_scope_priced'] and not twin['complete_cost_known']
    assert sum(m['cash_usd'] for m in twin['monthly_cash'])==pytest.approx(twin['priced_subtotal_usd'])
    assert twin['planning_bundle']['project_twin']['city']==plan['city'] and not twin['actual_records']
    assert all(t['planned_only'] and not t['engineering_release'] for t in twin['tasks'])

def test_missing_rates_are_never_zero_cost_closure(plan):
    plan=deepcopy(plan);plan['lines']=plan['lines'][-1:];plan=p.seal(plan)
    twin=p.project_twin(plan,configuration_sha256='a'*64)
    assert len(twin['unpriced_scope'])==3 and not twin['registered_scope_priced'] and not twin['complete_cost_known']
    assert all(q['cost_usd'] is None for q in twin['quantities'])

def test_gis_aggregation_preserves_population_and_labels_display_samples(plan):
    layers=p.planning_layers(plan,p.ROOT/'cities/catalogue/west-asia/Iraq/Baghdad');by={l['id']:l for l in layers['layers']}
    assert len(by)==16 and by['boosters']['features'] and by['destinations']['features']
    for key in ('population-worldpop','population-ghsl'):
        r=by[key];assert r['available'] and r['source_population_total']==pytest.approx(sum(f['properties']['population'] for f in r['features']))
    assert by['walking-streets']['display_sampling'] and by['soil-samples']['source_sha256']
    assert not layers['physical_release']
