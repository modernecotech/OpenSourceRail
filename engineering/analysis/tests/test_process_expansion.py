"""Independent/adverse qualification of process-aware research adapter scope."""
from copy import deepcopy
import json
from pathlib import Path
import shutil
import subprocess

import pytest

from engineering.continuous_design import expansion,operation_graph,processes,zone_thermal,tasks,worker,service,research,ledger,eligibility,capabilities,study_confirmation
from engineering.twin_workflow import core


@pytest.fixture(scope='module')
def examples(tmp_path_factory):
    root=tmp_path_factory.mktemp('process-expansion')
    records={}
    for index,task in enumerate(expansion.seeds()[:6]):
        output=root/str(index)/'output'
        result=worker.evaluate(dict(task=task,key=tasks.identity(task,'a'*64),baseline_sha256='a'*64),output)
        records[index]=dict(task=task,result=result,folder=str(output.parent),key=tasks.identity(task,'a'*64))
    return records


def test_structurally_passing_welded_cover_is_rejected_by_executable_replacement_path(examples):
    good,bad=examples[2]['result'],examples[4]['result']
    assert good['checks']['reference_carrier_deflection'] and bad['checks']['reference_carrier_deflection']
    assert good['study_pass'] and not bad['study_pass']
    assert 'manufacturing/operations/maintenance/equipment-payload' in bad['failed_checks']
    assert bad['manufacturing_process']['metrics']['blocked_replacement_count']==1


def test_distinct_shape_and_joining_architectures_regenerate_inventory_mass_and_stiffness(examples):
    rhs,folded=examples[2],examples[3]
    assert folded['result']['study_pass']
    first=core.read(Path(rhs['folder'])/'output/physical-contract.json',maximum=20_000_000)
    second=core.read(Path(folded['folder'])/'output/physical-contract.json',maximum=20_000_000)
    assert {p['id'] for p in first['parts']}!={p['id'] for p in second['parts']}
    assert rhs['result']['metrics']['mass_kg']!=folded['result']['metrics']['mass_kg']
    assert core.read(Path(rhs['folder'])/'output/physics.json')['beam']['ei_nm2']!=core.read(Path(folded['folder'])/'output/physics.json')['beam']['ei_nm2']
    nested=core.read(Path(folded['folder'])/'output/blank-nesting.json')
    assert any(p['part']=='developed-pan-blank' for p in nested['placements'])
    assert rhs['result']['manufacturing_process']['metrics']['destructive_joint_count']>folded['result']['manufacturing_process']['metrics']['destructive_joint_count']
    graph=core.read(Path(rhs['folder'])/'output/operation-graph.json')
    payload=next(op for op in graph['operations'] if op['parts']==['equipment-payload'] and op['id'].startswith('join-'))
    assert payload['kind']=='fasten'
    physics=core.read(Path(folded['folder'])/'output/physics.json',maximum=20_000_000)
    assert physics['unrepresented_bend_allowance_kg']>0.
    assert folded['result']['metrics']['mass_kg']==pytest.approx(physics['represented_material_mass_kg']+physics['unrepresented_bend_allowance_kg'])


def test_thermal_improvement_cannot_hide_electrical_capacity_penalty(examples):
    baseline,larger=examples[2],examples[5]
    physics=core.read(Path(larger['folder'])/'output/physics.json',maximum=20_000_000)
    assert physics['hvac_failed']['maximum_temperature_c']<=27.
    assert not larger['result']['study_pass'] and 'auxiliary_capacity' in larger['result']['failed_checks']
    assert larger['result']['metrics']['mass_kg']>baseline['result']['metrics']['mass_kg']
    assert physics['replacement_mass_credit_kg']==0.


@pytest.mark.parametrize('parallel',[2,3,4])
def test_real_battery_bay_rejection_completes_without_retry_or_native_promotion(tmp_path,monkeypatch,parallel):
    monkeypatch.setattr(capabilities,'registered',lambda *_:True)
    task=deepcopy(expansion.seeds()[2]);task['parameters']['variables'].update(series_modules=32,parallel_strings=parallel)
    baseline='a'*64;key=tasks.identity(task,baseline);folder=tmp_path/'attempt'
    result=worker.evaluate(dict(task=task,key=key,baseline_sha256=baseline),folder/'output')
    assert result['study_pass'] is False and result['failed_checks']==['battery_installation_bay']
    assert result['metrics']['mass_kg'] is None
    assert not (folder/'output/physical-contract.json').exists()
    proof=core.read(folder/'output/candidate-rejection.json')
    assert proof['reason']==expansion.BATTERY_BAY_REJECTION
    assert proof['compiler_source_sha256']==core.sha(core.ROOT/proof['compiler_source'])
    assert len(result['repairs'])==1
    assert result['repairs'][0]['parameters']['variables']['series_modules']==28
    assert result['repairs'][0]['parameters']['variables']['parallel_strings']==parallel
    assert all(result[name] is False for name in core.FLAGS)
    store=service.Store(tmp_path/'ledger');assert store.enqueue(task,baseline)
    core.write(folder/'result.json',result)
    files={str(p.relative_to(folder)):core.sha(p) for p in folder.rglob('*') if p.is_file()}
    core.write(folder/'receipt.json',dict(key=key,baseline_sha256=baseline,task=task,files_sha256=files,**core.FLAGS))
    with store.db:store.db.execute('UPDATE jobs SET folder=? WHERE key=?',(str(folder),key))
    ledger.complete_job(store,key,core.sha(folder/'receipt.json'),result)
    ledger.dispatch(store,budget_seconds=None)
    assert store.db.execute('SELECT status FROM jobs WHERE key=?',(key,)).fetchone()[0]=='completed'
    assert store.db.execute('SELECT state FROM outbox').fetchone()[0]=='delivered'
    assert not store.db.execute('SELECT 1 FROM promotions WHERE child=?',(key,)).fetchone()
    assert not eligibility.Resolver(store,baseline).state(key)['eligible']
    assert store.db.execute('SELECT count(*) FROM jobs').fetchone()[0]==2
    store.db.close()


def test_unrelated_compiler_value_error_stays_an_execution_error(tmp_path,monkeypatch):
    from engineering.design_engine import design_alternatives
    def fail(*args,**kwargs):raise ValueError('internal compiler/configuration failure')
    monkeypatch.setattr(design_alternatives,'compile_vehicle',fail)
    task=expansion.seeds()[2]
    with pytest.raises(ValueError,match='internal compiler/configuration failure'):
        worker.evaluate(dict(task=task,key=tasks.identity(task,'a'*64),baseline_sha256='a'*64),tmp_path/'output')


def test_all_registered_roof_core_cards_are_rejected_without_lowering_temperature(examples):
    for index in (0,1):
        result=examples[index]['result']
        assert not result['study_pass'] and result['search_blocked']
        assert 'manufacturing/core_service_temperature' in result['failed_checks']
        assert result['needs'][0]['item_id']=='qualified-high-temperature-roof-material-system'
        assert not result['repairs']


def test_layup_order_is_present_in_geometry_and_changes_independent_stiffness(examples,tmp_path):
    task=deepcopy(examples[0]['task']);task['parameters']['variables']['layup']='cross-ply'
    result=expansion.evaluate(task['kind'],task['parameters'],tmp_path)
    first=core.read(Path(examples[0]['folder'])/'output/physics.json',maximum=20_000_000)
    second=core.read(tmp_path/'physics.json',maximum=20_000_000)
    assert first['abd']['D']!=second['abd']['D']
    model=core.read(tmp_path/'physical-contract.json',maximum=20_000_000)
    assert all(p['laminate_ply']['angle_deg'] in (0,90) for p in model['parts'] if 'laminate_ply' in p)
    checked=study_confirmation.numerical(task['kind'],second,task['parameters']['variables'],tmp_path)
    assert all(checked['checks'].values())
    assert not result['manufacturing_release']


def test_material_properties_and_processes_cannot_be_freely_mixed_or_disabled(examples):
    task=deepcopy(examples[0]['task'])
    task['parameters']['variables']['glass_modulus_pa']=1e20
    with pytest.raises(ValueError):tasks.validate(task)
    task=deepcopy(examples[0]['task']);task['parameters']['variables']['process_profile']='ignore-manufacturing'
    with pytest.raises(ValueError):tasks.validate(task)
    task=deepcopy(examples[0]['task']);task['parameters']['variables']['material_system']='unqualified-magic-resin'
    with pytest.raises(ValueError):tasks.validate(task)


def test_every_represented_part_has_a_profile_and_unknowns_are_not_acceptance(examples):
    for example in examples.values():
        result=example['result'];model=core.read(Path(example['folder'])/'output/physical-contract.json',maximum=20_000_000)
        profile=result['manufacturing_process']
        assert set(profile['part_profiles'])=={p['id'] for p in model['parts']}
        assert profile['unknown'] and profile['quoted_cost'] is None and profile['measured_cycle_time_s'] is None
        assert all(result[name] is False for name in core.FLAGS)
    parts=[dict(id='p',bounds_m=[[0,0,0],[1,1,1]],mass_kg=1.)]
    with pytest.raises(ValueError,match='every represented'):
        processes.evaluate('profile-cut-weld',parts=parts,part_profiles={'unknown':'profile-cut-weld'})


def test_packing_preserves_every_blank_and_detects_oversize_without_negative_scrap():
    rectangles=[dict(id=str(i),size_m=[1.,.5,.006]) for i in range(17)]
    packed=processes.nesting(rectangles)
    assert packed['passed'] and len(packed['placements'])==17
    for i,p in enumerate(packed['placements']):
        assert p['x_m']+p['size_m'][0]<=4. and p['y_m']+p['size_m'][1]<=2.
        for q in packed['placements'][i+1:]:
            if p['sheet']==q['sheet']:
                assert not (max(p['x_m'],q['x_m'])<min(p['x_m']+p['size_m'][0],q['x_m']+q['size_m'][0]) and
                    max(p['y_m'],q['y_m'])<min(p['y_m']+p['size_m'][1],q['y_m']+q['size_m'][1]))
    assert not processes.nesting([dict(id='oversize',size_m=[5.,3.,.006])])['passed']
    assert packed['rectangular_scrap_m2']>=0.


def test_assembly_cannot_skip_temporary_support_or_pass_a_blocked_tool():
    parts=[dict(id='base',bounds_m=[[0.,0.,0.],[1.,1.,.1]],mass_kg=10.),
        dict(id='obstacle',bounds_m=[[0.,0.,.2],[1.,1.,.3]],mass_kg=10.)]
    graph=operation_graph.simple(parts)
    graph['operations'][1]['after']=['install-1']
    graph['operations'][2]['after']=['install-0']
    graph['operations'][1]['tool_bounds_m']=[[.2,.2,.1],[.4,.4,.4]]
    result=operation_graph.evaluate(graph)
    assert not result['checks']['join-0']
    graph=operation_graph.simple(parts);graph['fixtures']=[]
    assert not operation_graph.evaluate(graph)['checks']['install-0']
    graph=operation_graph.simple(parts);graph['operations'][0]['after']=['release']
    with pytest.raises(ValueError,match='cyclic'):operation_graph.evaluate(graph)


def test_two_zone_energy_and_water_balance_and_adverse_distribution(examples):
    physics=core.read(Path(examples[2]['folder'])/'output/physics.json',maximum=20_000_000)
    config=physics['hvac_inputs'];a=zone_thermal.solve(config,module_count=4)
    b=zone_thermal.solve(config,module_count=4,layout='single-end')
    assert abs(a['sensible_energy_balance_residual_j'])<1e-5 and abs(a['moisture_balance_residual_kg'])<1e-8
    assert b['maximum_temperature_c']>a['maximum_temperature_c']+1.
    assert zone_thermal.solve(config,module_count=4,flow_m3_s=.16,duct_area_m2=.01)['duct_velocity_m_s']==16.


def test_civil_family_and_reusable_mould_choices_regenerate_same_function(tmp_path):
    task=expansion.seeds()[6]
    first=tmp_path/'first';first.mkdir()
    result=expansion.evaluate(task['kind'],task['parameters'],first)
    assert result['study_pass']
    task=deepcopy(task);task['parameters']['variables'].update(deck_family='hollow-box',mould_route='rigid-one-piece')
    second=tmp_path/'second';second.mkdir()
    other=expansion.evaluate(task['kind'],task['parameters'],second)
    assert not other['checks']['manufacturing/mould_withdrawal_layout']
    assert result['metrics']['mass_kg']!=other['metrics']['mass_kg']
    a=core.read(first/'physics.json',maximum=20_000_000);b=core.read(second/'physics.json',maximum=20_000_000)
    assert a['study']['route_length_m']==b['study']['route_length_m']==100
    assert a['study']['train']==b['study']['train']
    assert any(row['state']=='unresolved' for row in a['research_limits'])
    assert 'unresolved civil criterion/deck_displacement_m' in result['open_evidence']


def test_all_civil_family_seeds_compile_with_appropriate_material_processes(tmp_path):
    for index,task in enumerate(expansion.seeds()[6:]):
        output=tmp_path/str(index);output.mkdir()
        result=expansion.evaluate(task['kind'],task['parameters'],output)
        model=core.read(output/'physical-contract.json',maximum=20_000_000)
        profiles=result['manufacturing_process']['part_profiles']
        assert set(profiles)=={p['id'] for p in model['parts']}
        for part in model['parts']:
            if 'steel' in part['material'].lower():assert profiles[part['id']]=='profile-cut-weld'
        physics=core.read(output/'physics.json',maximum=20_000_000)
        assert abs(result['metrics']['mass_kg']-physics['defined_material_mass_kg']-physics['unresolved_allowance_mass_kg'])<1e-6


def test_new_adapters_are_not_advertised_or_admitted_without_exact_registration(tmp_path):
    store=service.Store(tmp_path);task=expansion.seeds()[2]
    assert task['kind'] not in service.registered_domains(store,'mechanical')
    with pytest.raises(ValueError,match='registration'):store.enqueue(task,'a'*64)


def test_live_registration_observation_confirmation_and_failure_veto_path(examples,tmp_path,monkeypatch):
    monkeypatch.setattr(capabilities,'registered',lambda *_:True)
    store=service.Store(tmp_path);baseline='a'*64;example=examples[2];task=example['task']
    assert store.enqueue(task,baseline)
    key=tasks.identity(task,baseline);folder=tmp_path/'epochs'/baseline/'attempts'/key/'001'
    shutil.copytree(example['folder'],folder)
    core.write(folder/'result.json',example['result'])
    files={str(p.relative_to(folder)):core.sha(p) for p in folder.rglob('*') if p.is_file()}
    core.write(folder/'receipt.json',dict(key=key,baseline_sha256=baseline,task=task,files_sha256=files,**core.FLAGS))
    with store.db:store.db.execute('UPDATE jobs SET folder=? WHERE key=?',(str(folder),key))
    ledger.complete_job(store,key,core.sha(folder/'receipt.json'),example['result'])
    ledger.dispatch(store,budget_seconds=None)
    promotion=store.db.execute('SELECT * FROM promotions WHERE child=?',(key,)).fetchone()
    assert promotion
    row=store.db.execute('SELECT * FROM jobs WHERE key=?',(promotion['task_key'],)).fetchone()
    assert json.loads(row['task'])['kind']=='mechanical-study-confirmation'
    assert key in {c['key'] for c in research.summary(store,baseline)['champions']}
    failed=dict(study_pass=False,checks=dict(native_exact_child=False),failed_checks=['native_exact_child'],
        verification=dict(evaluated_level='native_geometry',levels={level:dict(state='failed' if level=='native_geometry' else 'passed') for level in eligibility.MANDATORY}),**core.FLAGS)
    output=tmp_path/'failed-confirmation';output.mkdir();core.write(output/'result.json',failed)
    core.write(output/'receipt.json',dict(key=row['key'],baseline_sha256=baseline,files_sha256={'result.json':core.sha(output/'result.json')}))
    with store.db:store.db.execute('UPDATE jobs SET folder=? WHERE key=?',(str(output),row['key']))
    ledger.complete_job(store,row['key'],core.sha(output/'receipt.json'),failed)
    assert not eligibility.Resolver(store,baseline).state(key)['eligible']
    assert key not in {c['key'] for c in research.summary(store,baseline)['champions']}
    assert core.read(folder/'result.json')['study_pass']


def test_novel_neighbors_reach_electrical_variables_after_earlier_geometry_choices_are_known(examples,tmp_path,monkeypatch):
    monkeypatch.setattr(capabilities,'registered',lambda *_:True)
    store=service.Store(tmp_path);baseline='a'*64;task=examples[2]['task'];result=examples[2]['result']
    for parameters in expansion.neighbors(task['kind'],task['parameters'],result)[:4]:
        store.enqueue(tasks.task(task['kind'],parameters),baseline)
    envelope=dict(key=tasks.identity(task,baseline),baseline_sha256=baseline,evidence_workspace=str(tmp_path))
    repairs=expansion.repair_tasks(task['kind'],task['parameters'],result,envelope)
    assert any(p['parameters']['variables']['series_modules']!=task['parameters']['variables']['series_modules'] for p in repairs)


def test_pareto_retains_heavier_candidate_with_lower_manufacturing_waste():
    a=dict(mass=100.,effort=5,objectives=json.dumps(dict(manufacturing_metrics=dict(rectangular_scrap_m2=8.,operation_count=10))))
    b=dict(mass=101.,effort=5,objectives=json.dumps(dict(manufacturing_metrics=dict(rectangular_scrap_m2=2.,operation_count=10))))
    assert not research.dominates(a,b) and not research.dominates(b,a)


@pytest.mark.parametrize('kind,index',[('mechanical-equipment-study',2),('mechanical-equipment-study',3),('civil-architecture-study',6)])
def test_real_native_and_scoped_numerical_confirmations(examples,tmp_path,kind,index):
    if not shutil.which('FreeCADCmd') and not shutil.which('freecadcmd'):
        if not shutil.which('flatpak') or subprocess.run(['flatpak','info','org.freecad.FreeCAD'],capture_output=True).returncode:
            pytest.skip('actual native FreeCAD unavailable')
    if kind=='mechanical-equipment-study':
        child=examples[index]
    else:
        task=expansion.seeds()[6];folder=tmp_path/'child';folder.mkdir()
        output=folder/'output';output.mkdir()
        result=expansion.evaluate(kind,task['parameters'],output)
        child=dict(task=task,folder=str(folder),result=result,key=tasks.identity(task,'a'*64))
    output=tmp_path/'confirmation';output.mkdir()
    result=study_confirmation.evaluate({},output,[child])
    assert result['study_pass'],result.get('errors')
    assert result['verification']['levels']['native_geometry']['state']=='passed'
    assert result['verification']['levels']['physical_correlation']['state']=='not_run'
    assert (output/'cad/candidate.FCStd').exists()
    assert all(result[name] is False for name in core.FLAGS)
