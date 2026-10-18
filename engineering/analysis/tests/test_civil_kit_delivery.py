"""Independent/adverse controls for manufactured civil units and delivery policy."""
from copy import deepcopy
import json
from pathlib import Path
import shutil
import subprocess

import pytest

from engineering.continuous_design import (civil_kit,civil_kit_evaluation as evaluation,construction_stage as stages,
    delivery_simulation as delivery,qa_traveller as qa,operation_graph,objectives,research,tasks,worker,
    service,capabilities,ledger,eligibility,study_confirmation)
from engineering.twin_workflow import core


@pytest.fixture(scope='module')
def examples(tmp_path_factory):
    base=tmp_path_factory.mktemp('civil-kit-delivery');records={}
    for architecture in civil_kit.ARCHITECTURES:
        task=tasks.task('civil-kit-study',dict(context_id=civil_kit.CONTEXT,variables=civil_kit.defaults(architecture)))
        folder=base/architecture;result=worker.evaluate(dict(task=task,key=tasks.identity(task,'a'*64),baseline_sha256='a'*64),folder/'output')
        records[architecture]=dict(task=task,result=result,folder=folder,key=tasks.identity(task,'a'*64),
            kit=core.read(folder/'output/civil-kit.json',maximum=20_000_000),
            jobs=core.read(folder/'output/delivery-tasks.json'),schedule=core.read(folder/'output/delivery-schedule.json'))
    return records


def observation(example):
    r=example['result'];return dict(key=example['key'],kind='civil-kit-study',context=civil_kit.CONTEXT,
        mass=r['metrics']['mass_kg'],effort=r['metrics']['manufactured_unit_count'],
        objectives=json.dumps(dict(manufacturing_metrics=r['manufacturing_process']['metrics'])))


def test_three_complete_equal_scope_kits_preserve_geometry_units_and_allowances(examples):
    hashes=set()
    for e in examples.values():
        k=e['kit'];r=e['result'];assert r['study_pass'],r['failed_checks']
        hashes.add(core.digest(dict(train=k['study']['train'],ground=k['study']['ground_scenarios'],
            limits=k['study']['research_limits'],durability=k['basis']['durability'],basis=k['basis_sha256'])))
        assert k['study']['route_length_m']==20 and len(k['component_coverage']['foundation_caps'])==2
        assert all(civil_kit.validate_kit(k).values())
        assert abs(k['mass_ledger']['mass_balance_residual_kg'])<1e-6
        assert r['metrics']['mass_kg']==pytest.approx(sum(u['mass_kg'] for u in k['units']))
        assert r['metrics']['manufactured_unit_count']<len(k['physical_contract']['parts'])
        assert r['metrics']['scenario_cost_usd'] is None
        assert all(t['serial'] is None and t['records']==[] for t in k['travellers'])
        assert all(r[flag] is False for flag in core.FLAGS)
        assert (e['folder']/'output/manufacturing-units.csv').exists()
    assert len(hashes)==1


def test_segmentation_trades_smaller_lifts_for_more_connections_work_and_plant(examples):
    large=examples['large-span']['result']['metrics'];small=examples['segmental']['result']['metrics']
    assert small['maximum_lift_mass_kg']<large['maximum_lift_mass_kg']
    assert small['total_lifts']>large['total_lifts']
    assert small['scenario_onsite_person_hours']>large['scenario_onsite_person_hours']
    assert small['temporary_plant_mass_kg']>0 and large['temporary_plant_mass_kg']==0
    assert small['mass_kg']>large['mass_kg']
    k=examples['segmental']['kit'];h=core.read(examples['segmental']['folder']/'output/handling-stages.json')
    heaviest=max(h['units'],key=lambda r:r['suspended_mass_kg'])['unit_id']
    assert next(u['category'] for u in k['units'] if u['id']==heaviest)=='foundation-cap'


def remove_operation(graph,identifier):
    g=deepcopy(graph);g['operations']=[op for op in g['operations'] if op['id']!=identifier]
    for op in g['operations']:op['after']=[v for v in op['after'] if v!=identifier]
    return g


def test_install_inspect_release_cannot_replace_missing_fastening():
    g=operation_graph.simple([dict(id='module',mass_kg=10.,bounds_m=[[0.,0.,0.],[1.,1.,1.]])])
    assert all(operation_graph.evaluate(g)['checks'].values())
    missing=operation_graph.evaluate(remove_operation(g,'join-0'))
    assert not missing['checks']['all_required_joints_retained'] and not missing['checks']['release']
    untested=operation_graph.evaluate(remove_operation(g,'inspect'))
    assert not untested['checks']['required_inspection_coverage'] and not untested['checks']['release']
    wrong=deepcopy(g);wrong['joints'][0]['endpoints']=['module','absent']
    with pytest.raises(ValueError,match='endpoints'):operation_graph.evaluate(wrong)


def test_lower_inspection_count_is_never_an_optimisation_reward():
    a=dict(mass=100.,effort=1,objectives=json.dumps(dict(manufacturing_metrics=dict(inspection_count=8))))
    b=dict(mass=100.,effort=1,objectives=json.dumps(dict(manufacturing_metrics=dict(inspection_count=1))))
    assert not research.dominates(b,a) and not research.dominates(a,b)


def test_heavier_smaller_lift_alternative_survives_and_can_earn_confirmation(examples):
    a=observation(examples['light-ribbed']);b=observation(examples['segmental'])
    assert b['mass']>a['mass']
    assert not research.dominates(a,b) and not research.dominates(b,a)
    assert objectives.useful_improvement(b,[a,a,a,a])
    roles=objectives.roles([a,b]);by_key={c['row']['key']:c['roles'] for c in roles}
    assert 'smallest-lift' in by_key[b['key']]
    assert objectives.primary_rank(a)<objectives.primary_rank(b)
    changed=deepcopy(b);v=json.loads(changed['objectives']);v['manufacturing_metrics']['comparison_basis_sha256']='different';changed['objectives']=json.dumps(v)
    assert not objectives.useful_improvement(changed,[a])


def test_heavier_candidate_gets_native_nomination_after_four_previous_nominations(tmp_path):
    # Scheduling counterexample only: copied numerical results isolate the
    # nomination policy. These are not new structural evaluations or CAD claims.
    from engineering.analysis.tests.test_continuous_planning import real_children,complete,FRAME
    store=service.Store(tmp_path);baseline='a'*64;deps=real_children(store,baseline)
    original=store.result(store.db.execute('SELECT * FROM jobs WHERE key=?',(deps[0]['key'],)).fetchone())
    first_result=deepcopy(original);first_result['manufacturing_process']['metrics']['operation_count']=100
    first=complete(store,tasks.task('mechanical-detail',dict(context_id='metro-6car-planning',variables=dict(FRAME,crossbearer_pitch_m=1.8))),baseline,first_result)
    with ledger.transaction(store.db):research.observe(store,first['key'])
    with store.db:
        store.db.execute("UPDATE jobs SET status='error' WHERE key IN (SELECT task_key FROM promotions)")
        for i in range(3):store.db.execute('INSERT INTO promotions VALUES(?,?,?,?,?,?)',(f'cost-history-{i}',baseline,'metro-6car-planning',f'done-{i}','test expenditure history',1))
    heavier=deepcopy(first_result);heavier['metrics']['mass_kg']*=1.1;heavier['manufacturing_process']['metrics']['operation_count']=50
    value=tasks.task('mechanical-detail',dict(context_id='metro-6car-planning',variables=dict(FRAME,crossbearer_pitch_m=1.2)))
    second=complete(store,value,baseline,heavier)
    with ledger.transaction(store.db):research.observe(store,second['key'])
    assert store.db.execute('SELECT 1 FROM promotions WHERE child=?',(second['key'],)).fetchone()
    assert any(second['key']==row['key'] for row in research.delivery_shortlist(store,baseline))
    store.db.close()


def test_mould_is_held_during_cure_while_labour_is_released():
    jobs=[]
    for uid in ('a','b'):
        jobs += [dict(id=uid+'-cast',hours=1.,after=[],resources={'crew':1},acquire={'mould':1},owner=uid,people=2),
            dict(id=uid+'-cure',hours=10.,after=[uid+'-cast'],resources={},release={'mould':1},owner=uid)]
    a=delivery.schedule(jobs,dict(crew=2,mould=1));b=delivery.schedule(jobs,dict(crew=2,mould=2))
    assert a['passed'] and a['makespan_h']==22 and b['makespan_h']==11
    assert a['factory_person_hours']==4 and a['resources']['crew']['busy_resource_hours']==2
    assert a['resources']['mould']['busy_resource_hours']==22
    assert delivery.bottlenecks(jobs,dict(crew=2,mould=1),a)[0]==dict(resource='mould',additional_capacity=1,scenario_hours_saved=11.)


def test_loaded_trailers_and_site_capacity_are_not_released_before_placement(examples):
    e=examples['large-span'];s=e['schedule'];timed={r['id']:r for r in s['tasks']}
    occupied=sum(timed[u['id']+'/place-and-temporary-lock']['end_h']-timed[u['id']+'/transport']['start_h'] for u in e['kit']['units'] if u['offsite'])
    assert s['resources']['truck']['busy_resource_hours']==pytest.approx(occupied)
    assert all(r['peak_occupied']<=r['capacity'] for r in s['resources'].values())
    assert e['result']['metrics']['site_bulk_concrete_deliveries']==16


def test_bores_precede_cages_and_partial_segments_precede_post_tension(examples):
    e=examples['segmental'];timed={r['id']:r for r in e['schedule']['tasks']}
    for u in e['kit']['units']:
        if u['category']=='pile-cage':
            assert timed[u['id'].removesuffix('-cage')+'/bore']['end_h']<=timed[u['id']+'/place-and-temporary-lock']['start_h']
    assert all(stages.verify_schedule(e['kit'],e['jobs'],e['schedule'])['checks'].values())
    for track in (1,2):
        assert all(timed[u+'/place-and-temporary-lock']['end_h']<=timed[f'T{track}/post-tension']['start_h'] for u in e['kit']['component_coverage']['decks'] if u.startswith(f'deck-T{track}-'))


def test_premature_cure_crane_release_or_missing_stage_cannot_pass(examples):
    e=examples['segmental'];jobs=deepcopy(e['jobs'])
    next(r for r in jobs if r['id'].endswith('/connection-strength-wait'))['hours']=.01
    s=delivery.schedule(jobs,e['kit']['basis']['capacities'])
    assert not all(stages.verify_schedule(e['kit'],jobs,s)['checks'].values())
    jobs=deepcopy(e['jobs']);next(r for r in jobs if r['id'].endswith('/place-and-temporary-lock'))['hours']=.01
    s=delivery.schedule(jobs,e['kit']['basis']['capacities'])
    assert not all(stages.verify_schedule(e['kit'],jobs,s)['checks'].values())
    s=deepcopy(e['schedule']);s['tasks']=[r for r in s['tasks'] if r['id']!='falsework/install']
    assert not stages.verify_schedule(e['kit'],e['jobs'],s)['checks']['all_required_stage_ids']


def test_crane_chart_uses_required_radius_and_no_extrapolation(examples):
    assert stages.crane_capacity([[8,125000],[14,80000],[20,40000]],15)==40000
    assert stages.crane_capacity([[8,125000],[14,80000]],30) is None
    k=deepcopy(examples['large-span']['kit']);k['basis']['lifting']['radius_m']=20
    assert not all(stages.handling(k)['checks'].values())
    with pytest.raises(ValueError):stages.crane_capacity([[8,100],[7,200]],8)


def test_removed_regions_routes_or_qa_cannot_be_hidden_as_savings(examples):
    k=deepcopy(examples['large-span']['kit']);k['units'].pop()
    assert not all(civil_kit.validate_kit(k).values())
    k=deepcopy(examples['large-span']['kit']);k['service_routes'].pop()
    assert not civil_kit.validate_kit(k)['required_service_routes']
    k=deepcopy(examples['large-span']['kit']);k['travellers'][0]['required']['factory'].pop()
    assert not civil_kit.validate_kit(k)['qa_identity_and_plan']
    k=deepcopy(examples['large-span']['kit']);k['physical_contract']['parts'][0]['manufacturing']['role']+=' changed'
    assert not all(civil_kit.validate_kit(k).values())


def test_serial_revision_and_interface_changes_request_the_affected_retests(examples):
    u=next(u for u in examples['large-span']['kit']['units'] if u.get('service_type')=='power');t=qa.template(u)
    assert qa.assess(u,t,interface_revision='old')['state']=='hold'
    t['serial']='test-fixture-only-001'
    for stage,tests in qa.requirements(u).items():
        for name in tests:t['records'].append(qa.event(dict(event_type='test',sequence=len(t['records'])+1,stage=stage,test=name,state='passed',serial=t['serial'],unit_revision=u['revision'],
            interface_revision='old',qualified_reviewer='synthetic test fixture',evidence_sha256='a'*64)))
    assert qa.assess(u,t,interface_revision='old')['state']=='passed-records'
    assert not qa.assess(u,t,interface_revision='old')['accepted']
    revised=deepcopy(u);revised['revision']='b'*64
    assert qa.assess(revised,t,interface_revision='old')['retest']==list(qa.STAGES)
    interface=qa.assess(u,t,interface_revision='changed')
    assert interface['coverage']['factory']['complete'] and not interface['coverage']['installed']['complete']


def test_cost_needs_every_revision_and_installation_scope_without_factory_double_charge(examples):
    e=examples['large-span'];k=e['kit'];s=e['schedule']
    q=dict(currency='USD',basis_reference='synthetic cost control; not a quotation',unit_supply_only={u['revision']:dict(unit_revision=u['revision'],usd=10.,basis_reference='test-only') for u in k['units']},
        site_person_hour_usd=1.,crane_hour_usd=0.,truck_hour_usd=0.,mixer_hour_usd=0.,concrete_pump_hour_usd=0.,excavator_hour_usd=0.,pile_rig_hour_usd=0.,falsework_hour_usd=0.,mobilisation_usd=0.,temporary_works_usd=0.,road_disruption_usd=0.,maintenance_present_value_usd=0.)
    assert evaluation.quoted_cost(k,s)['total_usd'] is None
    assert evaluation.quoted_cost(k,s,q)['total_usd']==pytest.approx(10*len(k['units'])+s['onsite_person_hours'])
    q.pop('maintenance_present_value_usd');assert evaluation.quoted_cost(k,s,q)['total_usd'] is None


def test_station_is_a_separate_function_with_own_foundations_and_mass(examples):
    values=dict(civil_kit.defaults(),station_package=True)
    with pytest.raises(ValueError,match='separate'):civil_kit.validate(dict(context_id=civil_kit.CONTEXT,variables=values))
    civil_kit.validate(dict(context_id=civil_kit.STATION_CONTEXT,variables=values))
    k=civil_kit.build(values);assert all(civil_kit.validate_kit(k).values())
    assert k['component_coverage']['station'] and k['mass_ledger']['installed_study_mass_kg']>examples['large-span']['result']['metrics']['mass_kg']
    assert any(u['category']=='station-foundation' for u in k['units'])


def test_foundation_and_pier_variations_rebuild_the_complete_kit(examples):
    values=dict(civil_kit.defaults(),foundation_family='bored-six',foundation_cap_segments=2,pier_family='hollow-prismatic',pier_segments=4)
    civil_kit.validate(dict(context_id=civil_kit.CONTEXT,variables=values));k=civil_kit.build(values)
    assert all(civil_kit.validate_kit(k).values())
    assert len(k['component_coverage']['piles'])==12 and len(k['component_coverage']['foundation_caps'])==4
    assert len(k['component_coverage']['piers'])==8
    assert k['mass_ledger']['installed_study_mass_kg']!=examples['large-span']['result']['metrics']['mass_kg']
    wrong=dict(values,foundation_route='precast-driven')
    with pytest.raises(ValueError,match='compatible bundle'):civil_kit.validate(dict(context_id=civil_kit.CONTEXT,variables=wrong))


def test_engineering_data_is_source_bound_and_registration_detects_changes(tmp_path,monkeypatch):
    from types import SimpleNamespace
    assert 'engineering/continuous_design/data/civil-kit-basis.json' in service.source_snapshot()
    original_root=core.ROOT;monkeypatch.setattr(core,'ROOT',tmp_path)
    data=tmp_path/'basis.json';core.write(data,dict(crane='test only'))
    folder=tmp_path/'workspace/capabilities/example';folder.mkdir(parents=True)
    core.write(folder/'registration.json',dict(item_id='test-data-binding',source_sha256={'basis.json':core.sha(data)}))
    store=SimpleNamespace(workspace=tmp_path/'workspace')
    assert capabilities.registered(store,'test-data-binding')
    core.write(data,dict(crane='changed'))
    assert not capabilities.registered(store,'test-data-binding')


def test_station_package_native_geometry_preserves_unit_identity(tmp_path):
    if not shutil.which('FreeCADCmd') and not shutil.which('freecadcmd'):
        if not shutil.which('flatpak') or subprocess.run(['flatpak','info','org.freecad.FreeCAD'],capture_output=True).returncode:pytest.skip('native FreeCAD unavailable')
    k=civil_kit.build(dict(civil_kit.defaults(),station_package=True));core.write(tmp_path/'definition.json',k['physical_contract'])
    proof,state,error=study_confirmation.native(tmp_path/'definition.json',tmp_path/'cad')
    assert state=='passed',error
    assert proof['manufacturing_unit_ids_preserved']


@pytest.mark.parametrize('architecture',list(civil_kit.ARCHITECTURES))
def test_native_unit_ids_and_scoped_numerical_confirmation(examples,tmp_path,architecture):
    if not shutil.which('FreeCADCmd') and not shutil.which('freecadcmd'):
        if not shutil.which('flatpak') or subprocess.run(['flatpak','info','org.freecad.FreeCAD'],capture_output=True).returncode:pytest.skip('native FreeCAD unavailable')
    e=examples[architecture];output=tmp_path/'confirmation';output.mkdir()
    child=dict(key=e['key'],task=e['task'],folder=str(e['folder']),result=e['result'])
    r=study_confirmation.evaluate({},output,[child]);assert r['study_pass'],r.get('errors')
    proof=core.read(output/'cad/native-cad.json');assert proof['manufacturing_unit_ids_preserved']
    assert all(core.sha(output/'cad'/name)==digest for name,digest in proof['files_sha256'].items())
    assert r['verification']['levels']['physical_correlation']['state']=='not_run'
    assert all(r[flag] is False for flag in core.FLAGS)
