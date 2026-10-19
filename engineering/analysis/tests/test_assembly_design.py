"""Source applicability, structural controls, fault propagation and durable evidence."""
from copy import deepcopy
import gzip
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess

import pytest

from engineering.assembly_design import baseline,models,evaluate,workflow,publication
from engineering.twin_workflow import core
from engineering.continuous_design import beam_confirmation


@pytest.fixture
def policy():return baseline.validate(core.read(baseline.DATA))


def recipe(policy,kind,**changes):
    variables={k:v[0] for k,v in policy['pilots'][kind]['domains'].items()}
    if kind=='bearing-seat':variables['bearing_family']='uk-spherical-candidate'
    variables.update(changes);return models.build(policy,kind,variables)


@pytest.mark.parametrize('failure',('duplicate','approved','null','source','part'))
def test_baseline_rejects_untraceable_or_misapplied_inputs(policy,failure):
    p=deepcopy(policy)
    if failure=='duplicate':p['facts'].append(deepcopy(p['facts'][0]))
    elif failure=='approved':p['facts'][0]['approved']=True
    elif failure=='null':p['facts'][0]['value']=None
    elif failure=='source':p['facts'][0]['source']='../outside'
    else:p['pilots']['bearing-seat']['requirement_ids']=['baghdad:missing']
    with pytest.raises(ValueError):baseline.validate(p)


def test_inventory_preserves_architecture_identities_and_actual_source_fields(policy):
    inventory=baseline.inventory(policy);legacy=[i for i in inventory['items'] if i['architecture']=='legacy-lm3'];baghdad=[i for i in inventory['items'] if i['architecture']=='baghdad-six-car']
    assert legacy and all(not i['adopted_fact_ids'] for i in legacy)
    assert len(baghdad)==69 and len({i['id'] for i in inventory['items']})==len(inventory['items'])
    assert next(i for i in baghdad if i['id']=='baghdad:ME-11')['adopted_fact_ids']==['climate.ambient','climate.baghdad_mean_july_max','climate.iraq_summer_max_context']
    assert all(i['source_records'] for i in inventory['items'])
    assert baseline.facts(policy)['train.mass_cases']==core.read(core.ROOT/'engineering/generative_design/data/architecture-feedback.json')['six_car_mass_cases_kg']
    assert baseline.facts(policy)['bolts.stress_areas']==core.read(core.ROOT/'engineering/generative_design/data/mechanical-detail-space.json')['bolt_request']['tensile_stress_area_m2']


def test_integrated_moment_field_matches_independent_fem_and_linear_scaling():
    for L,supports in ((4.,[0.,4.]),(3.,[.3,2.7]),(5.,[.4,4.2])):
        analytical=evaluate.overhang_beam(L,supports,4e6,1000.)
        fem=beam_confirmation.solve(L,supports,4e6,uniform=1000.,divisions=64)
        assert analytical['maximum_deflection_m']==pytest.approx(fem['maximum_nodal_deflection_m'],rel=.005)
        assert sum(analytical['reactions_n'])==pytest.approx(1000*L)
        assert evaluate.overhang_beam(L,supports,4e6,2000.)['maximum_deflection_m']==pytest.approx(2*analytical['maximum_deflection_m'])
    assert evaluate.overhang_beam(4.,[0.,4.],4e6,1000.)['maximum_deflection_m']==pytest.approx(5*1000*4**4/(384*4e6))
    with pytest.raises(ValueError):evaluate.overhang_beam(4.,[1.,1.],4e6,1000.)


def test_section_and_plate_changes_propagate_into_mass_and_response(policy):
    thin=evaluate.evaluate(policy,recipe(policy,'service-cassette',rail_wall_m=.002));thick=evaluate.evaluate(policy,recipe(policy,'service-cassette',rail_wall_m=.004))
    assert thick['measurements']['mass_kg']>thin['measurements']['mass_kg']
    assert thick['measurements']['beam_cases'][-1]['analytical']['maximum_deflection_m']<thin['measurements']['beam_cases'][-1]['analytical']['maximum_deflection_m']
    assert thin['measurements']['joint']['resultant_relative_error']<1e-10
    assert all(not thin[k] for k in core.FLAGS)
    small=evaluate.evaluate(policy,recipe(policy,'bearing-seat',plate_thickness_m=.02));large=evaluate.evaluate(policy,recipe(policy,'bearing-seat',plate_thickness_m=.04))
    assert large['measurements']['mass_kg']>small['measurements']['mass_kg']
    assert large['measurements']['seat_load_cases'][-1]['stress_pa']<small['measurements']['seat_load_cases'][-1]['stress_pa']*.27
    assert large['measurements']['seat_load_cases'][-1]['yield_reference_pa']==345e6


def test_unknown_supplier_rating_and_known_temperature_failure_are_distinct(policy):
    unknown=evaluate.evaluate(policy,recipe(policy,'bearing-seat'))
    failed=evaluate.evaluate(policy,recipe(policy,'bearing-seat',bearing_family='elastomeric-reference'))
    assert unknown['state']=='hold' and unknown['checks']['bearing-continuous-temperature-applicability'] is None
    assert failed['state']=='failed' and 'bearing-continuous-temperature-applicability' in failed['failed_checks']
    assert not unknown['screen_pass'] and not failed['screen_pass']


def test_packaging_failure_and_stale_generated_geometry_are_rejected(policy):
    c=recipe(policy,'service-cassette',duct_area_m2=.03)
    r=evaluate.evaluate(policy,c);assert 'duct-packaging' in r['failed_checks']
    c['contract']['parts'][0]['properties']['mass_kg']+=10
    with pytest.raises(ValueError,match='controlled generator'):evaluate.evaluate(policy,c)


def test_bolt_stress_uses_thread_area_and_independent_sci_control(policy):
    r=evaluate.evaluate(policy,recipe(policy,'service-cassette',bolt_diameter_m=.02));m=r['measurements']
    assert m['bolt_stress_area_m2']==.000245
    expected=max((max(0,z)**2+3*(x*x+y*y))**.5/.000245 for x,y,z in m['joint']['bolt_forces_n'])
    assert m['peak_bolt_equivalent_stress_pa']==pytest.approx(expected)
    reference=.6*800e6*.000245/1.25
    assert reference==pytest.approx(baseline.facts(policy)['bolts.m20_benchmark'],abs=25)


@pytest.mark.parametrize('variant',('branch','bitmask'))
def test_executable_software_variants_propagate_faults_and_recover(variant):
    trial=evaluate.control_trial(variant);assert len(trial['cases'])==256 and all(trial['checks'].values())
    bad=evaluate.control_trial(source="def step(tripped,i):\n return {'tripped':False,'enabled':i['request']}\n")
    assert not bad['checks']['exhaustive_transition_oracle'] and not bad['checks']['disconnect_latch_moving_reset_and_stopped_recovery']


@pytest.fixture
def campaign(tmp_path,policy,monkeypatch):
    monkeypatch.setattr(workflow,'RESERVE',1024**2)  # /tmp is a small test tmpfs, not the production volume.
    workspace=tmp_path/'workspace';workspace.mkdir();qpath=workspace/'fixture-qualification.json'
    inv=baseline.inventory(policy);items=[i for i in inv['items'] if i['id'] in {'baghdad:ME-01','baghdad:ME-10','baghdad:ME-11','baghdad:CI-01'}]
    prepared=dict(policy=policy,inventory=dict(items=items,existing_items=0,baghdad_reference_items=4,packages=[]),source_sha256={'synthetic-fixture.py':'f'*64},**core.FLAGS)
    (workspace/'tests.log').write_text('Synthetic fixture only; not engineering qualification\n')
    q=dict(passed=True,sources=prepared['source_sha256'],runtime_identity={'fixture':True},log_sha256=core.sha(workspace/'tests.log'),**core.FLAGS);core.write(qpath,q)
    monkeypatch.setattr(baseline,'sources',lambda:prepared['source_sha256']);monkeypatch.setattr(baseline,'build',lambda:deepcopy(prepared));monkeypatch.setattr(workflow.runtime,'capture',lambda:{'fixture':True});monkeypatch.setattr(workflow,'qualification',lambda w:(qpath,q))
    with workflow.locked(workspace) as (w,db):epoch,prepared=workflow.initialise(w,db)
    return workspace,epoch,prepared


def execute_examples(campaign):
    workspace,epoch,prepared=campaign
    with workflow.locked(workspace) as (w,db):
        for kind in ('service-cassette','bearing-seat','cassette-control'):
            for row in db.execute('SELECT * FROM jobs WHERE epoch=? AND kind=?',(epoch,kind)).fetchall():
                v=json.loads(row['variables'])
                if kind=='bearing-seat' and v['bearing_family']!='uk-spherical-candidate':continue
                if kind=='service-cassette' and v['duct_area_m2']!=.01:continue
                workflow.execute(w,db,epoch,prepared,row)
                if kind!='cassette-control':break
    return workspace


def test_run_is_durable_and_deduplicated_and_fair_across_four_families(campaign):
    w,epoch,_=campaign
    first=workflow.run(w,budget=4,native=False)
    assert first['counts']['completed_trials']==4
    assert {r['kind'] for r in first['trials'] if r['status']=='completed'}=={'service-cassette','bearing-seat','structural-bay','cassette-control'}
    second=workflow.run(w,budget=3,native=False);assert second['counts']['completed_trials']==7
    assert second['counts']['qualified_components']==0 and not second['design_complete']
    with workflow.locked(w) as (_,db):assert db.execute('SELECT COUNT(*) FROM jobs WHERE epoch=?',(epoch,)).fetchone()[0]==62


def test_recovery_uses_sealed_identity_and_preserves_interrupted_attempts(campaign):
    w=execute_examples(campaign);epoch=campaign[1]
    with workflow.locked(w) as (_,db):
        row=db.execute("SELECT * FROM jobs WHERE status='completed' LIMIT 1").fetchone()
        with db:db.execute("UPDATE jobs SET status='running' WHERE key=?",(row['key'],))
        workflow.recover(db,epoch)
        assert db.execute('SELECT status FROM jobs WHERE key=?',(row['key'],)).fetchone()[0]=='completed'
        (Path(row['folder'])/'unsealed.txt').write_text('interrupted or foreign bytes')
        with db:db.execute("UPDATE jobs SET status='running',attempts=2 WHERE key=?",(row['key'],))
        workflow.recover(db,epoch)
        assert db.execute('SELECT status FROM jobs WHERE key=?',(row['key'],)).fetchone()[0]=='error'
        assert (Path(row['folder'])/'unsealed.txt').exists()


def test_failed_native_receipt_never_recovers_as_passed(campaign):
    w=execute_examples(campaign);epoch=campaign[1]
    with workflow.locked(w) as (_,db):
        row=next(r for r in workflow.representatives(db,epoch) if r['kind']=='bearing-seat')
        folder=w/'epochs'/epoch/'native'/row['key'];folder.mkdir(parents=True)
        core.write(folder/'result.json',dict(child=row['key'],state='failed',**core.FLAGS));workflow.seal(folder,dict(key=row['key']+'-native',child=row['key'],epoch=epoch))
        workflow.confirm(w,db,epoch,row)
        assert db.execute('SELECT status FROM native WHERE child=?',(row['key'],)).fetchone()[0]=='failed'
        assert row['key'] not in {r['key'] for r in workflow.representatives(db,epoch)}


def reseal(path):
    m=core.read(path/'manifest.json',maximum=20_000_000);m['files_sha256']={p.relative_to(path).as_posix():core.sha(p) for p in path.rglob('*') if p.is_file() and p.name!='manifest.json'}
    m['progress_digest']=core.digest(core.read(path/'progress.json',maximum=20_000_000));core.write(path/'manifest.json',m)


def test_portable_evidence_survives_removal_of_private_workspace(campaign,tmp_path):
    w=execute_examples(campaign);output=tmp_path/'export';publication.export(w,output);shutil.rmtree(w)
    assert publication.verify(output)['verified']


@pytest.mark.parametrize('target',('closure-progress.json','prototype.json','registers.json','integration.json','family-crosswalk.json'))
def test_full_plan_export_cannot_disagree_with_frozen_source_after_reseal(campaign,tmp_path,target):
    from engineering.assembly_design import closure,contracts
    workspace,old_epoch,prepared=campaign
    prepared.update(closure_plan=closure.plan(),prototype=contracts.prototype_configuration(),
        family_crosswalk=contracts.crosswalk(prepared['inventory']),registers={'fixture':'synthetic, not qualification'},
        integration={'state':'hold','fixture':'synthetic'})
    workflow.run(workspace,budget=4,native=False)
    output=tmp_path/'plan-export';publication.export(workspace,output)
    assert publication.verify(output)['verified']
    value=core.read(output/target,maximum=20_000_000)
    value['falsified_completion']=True
    core.write(output/target,value);reseal(output)
    with pytest.raises(ValueError):publication.verify(output)


@pytest.mark.parametrize('target',('result','bom','drawing','metrics','counts','selection-scope','software','report','work-order'))
def test_export_cannot_disagree_with_original_after_checksum_reseal(campaign,tmp_path,target):
    w=execute_examples(campaign);output=tmp_path/'export';publication.export(w,output);folder=output/'diagnostics/service-cassette'
    if target=='result':
        r=core.read(folder/'result.json');r['screen_pass']=True;core.write(folder/'result.json',r)
    elif target=='bom':(folder/'manufacturing-bom.csv').write_text('invented BOM')
    elif target=='drawing':(folder/'inspection.svg').write_text('<svg/>')
    elif target in {'metrics','counts','selection-scope'}:
        data=core.read(output/'progress.json',maximum=20_000_000)
        if target=='metrics':next(t for t in data['trials'] if t['status']=='completed' and t['kind']=='service-cassette')['mass_kg']=0
        elif target=='counts':data['counts']['qualified_components']=1
        else:data['selected'][0]['scope']='Complete production design'
        core.write(output/'progress.json',data);(output/'index.html').write_text(publication.report(data,campaign[2]['policy']))
    elif target=='software':(output/'software/branch/controller.py').write_text('invented implementation')
    elif target=='work-order':core.write(output/'work-orders.json',[])
    else:(output/'index.html').write_text('Invented complete system')
    reseal(output)
    with pytest.raises(ValueError):publication.verify(output)


@pytest.mark.parametrize('kind',('service-cassette','bearing-seat'))
def test_real_native_owned_geometry_and_purchased_envelope_correspondence(campaign,kind):
    if not shutil.which('FreeCADCmd') and not shutil.which('freecadcmd'):
        if not shutil.which('flatpak') or subprocess.run(['flatpak','info','org.freecad.FreeCAD'],capture_output=True).returncode:pytest.skip('native FreeCAD unavailable')
    w=execute_examples(campaign);epoch=campaign[1]
    with workflow.locked(w) as (_,db):
        row=next(r for r in [*workflow.representatives(db,epoch),*workflow.diagnostics(db,epoch)] if r['kind']==kind);workflow.confirm(w,db,epoch,row)
        n=db.execute('SELECT * FROM native WHERE child=?',(row['key'],)).fetchone()
        assert n['status']=='completed',core.read(Path(n['folder'])/'result.json')
        native=core.read(Path(n['folder'])/'cad/native-cad.json',maximum=10_000_000)
        assert native['physical_ids_preserved'] and native['native_reopened'] and native['step_volume_reconciled'] and not native['drawing_issued']
        assert not core.read(Path(n['folder'])/'result.json')['physical_release']


def test_timer_runs_bounded_qualified_work_and_keeps_data_local(tmp_path):
    path=core.ROOT/'tools/automation/design-assemblies.py';spec=importlib.util.spec_from_file_location('assembly_cli',path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    units=module.units(tmp_path/'100% workspace')
    assert 'OnUnitActiveSec=5min' in units['osr-assembly-design.timer']
    body=units['osr-assembly-design.service'];assert 'MemoryMax=2G' in body and 'TimeoutStartSec=15min' in body and '100%% workspace' in body
    assert '--budget' in body and '"cycle"' in body


def test_resource_hold_preserves_queued_work(campaign,monkeypatch):
    monkeypatch.setattr(workflow,'RESERVE',10**18)
    report=workflow.run(campaign[0],budget=3,native=False)
    assert report['controller_state']=='waiting-for-disk' and report['counts']['completed_trials']==0
    assert all(t['status']=='queued' for t in report['trials'])


def test_unit_revision_changes_when_generated_geometry_changes(policy,monkeypatch):
    original=recipe(policy,'service-cassette');box=models.contracts.box
    def changed(identity,length,width,height,centre):
        return box(identity,length+.01 if identity=='tray-floor' else length,width,height,centre)
    monkeypatch.setattr(models.contracts,'box',changed)
    revised=recipe(policy,'service-cassette')
    assert revised['revision']!=original['revision']
    assert all(p['revision']==revised['revision'] for p in revised['contract']['parts'])


def test_rotated_clamp_has_world_placement_in_manufacturing_information(policy,tmp_path):
    import csv
    candidate=recipe(policy,'service-cassette');workflow.tables(candidate,tmp_path)
    rows=list(csv.DictReader((tmp_path/'manufacturing-bom.csv').open()))
    row=next(r for r in rows if r['id']=='cable-clamp-0')
    assert json.loads(row['placement_json'])['translation_m']==[-.3,.138,.07]
    assert 'cable-clamp-0' in (tmp_path/'inspection.svg').read_text()


def test_automatic_development_scope_and_review_bind_exact_proposal_bytes(policy):
    from engineering.assembly_design import development
    inventory=baseline.inventory(policy);item=next(i for i in inventory['items'] if i['id']=='baghdad:ME-10')
    order=development.work_order(dict(policy=policy,source_sha256={}),item,'a'*64)
    candidate=recipe(policy,'service-cassette')
    proposal=dict(schema='osr-assembly-capability-proposal/1',item_id=item['id'],epoch='a'*64,contract=candidate['contract'],
        claimed_addressed=[order['known_gaps'][0]],research_checks={},unresolved=['Exact qualification remains open'],scope='Research geometry only',**core.FLAGS)
    assert development.validate_proposal(proposal,order)==proposal
    bad=deepcopy(proposal);bad['claimed_addressed']=['Invented unrelated completion']
    with pytest.raises(ValueError,match='scoped gap'):development.validate_proposal(bad,order)
    bad=deepcopy(proposal);bad['manufacturing_release']=True
    with pytest.raises(ValueError,match='release'):development.validate_proposal(bad,order)
    review=dict(decision='research-improvement',proposal_sha256='b'*64,proposed_source_sha256='c'*64,reasons=['Explicit geometry delta'],remaining_work=['Independent strength and physical validation'],**core.FLAGS)
    assert development.validate_review(review,'b'*64,'c'*64)==review
    with pytest.raises(ValueError,match='different'):development.validate_review(review,'d'*64,'c'*64)
    review['physical_release']=True
    with pytest.raises(ValueError,match='release'):development.validate_review(review,'b'*64,'c'*64)


def test_development_commands_use_existing_model_and_separate_writer_reviewer(tmp_path):
    from engineering.assembly_design import development
    config=dict(provider_executable='/existing/provider',provider_model='existing-configured-model')
    author=development.command(config,tmp_path,tmp_path/'author.txt');review=development.command(config,tmp_path,tmp_path/'review.txt',review_schema=tmp_path/'schema.json')
    assert 'workspace-write' in author and 'read-only' in review and '--ephemeral' in author
    assert author[author.index('--model')+1]=='existing-configured-model'
    assert '--output-schema' in review and author[-1]=='-' and review[-1]=='-'


def test_automatic_development_runs_writer_then_critic_without_promoting_unknown_native(campaign,tmp_path,monkeypatch):
    from engineering.assembly_design import development
    from types import SimpleNamespace
    w,epoch,prepared=campaign
    legacy=tmp_path/'legacy';legacy.mkdir();core.write(legacy/'config.json',dict(provider_enabled=True,provider_executable='/fixture-provider',provider_model='existing-model'))
    monkeypatch.setattr(development.service,'DEFAULT',legacy)
    original_sha=core.sha
    monkeypatch.setattr(core,'sha',lambda path:'f'*64 if Path(path).name=='synthetic-fixture.py' else original_sha(path))
    def git(*args,cwd=core.ROOT):
        if args[:2]==('worktree','add'):
            tree=Path(args[4]);tree.mkdir();(tree/'synthetic-fixture.py').write_text('fixture source');return ''
        if args[:2]==('worktree','remove'):shutil.rmtree(args[-1]);return ''
        if args[:2]==('ls-files','--others'):
            return '\n'.join(p.relative_to(cwd).as_posix() for p in Path(cwd).rglob('*') if p.is_file() and p.name!='synthetic-fixture.py')
        return ''
    monkeypatch.setattr(development,'git',git)
    monkeypatch.setattr(development.subprocess,'run',lambda *a,**k:SimpleNamespace(returncode=0,stdout=''))
    monkeypatch.setattr(development.study_confirmation,'native',lambda *a:(None,'hold','fixture unavailable native tool'))
    phases=[]
    def process(argv,folder,stdin,*limits):
        phases.append(folder.name);request=json.loads(stdin) if stdin else None
        tree=folder.parent/'worktree';private=tree/development.PRIVATE
        if folder.name=='author':(private/'proposed.py').write_text('# isolated fixture proposal\n')
        elif folder.name=='evaluate':
            proposal=dict(schema='osr-assembly-capability-proposal/1',item_id='baghdad:ME-10',epoch=epoch,
                contract=recipe(prepared['policy'],'service-cassette')['contract'],claimed_addressed=[development.ACTIONABLE['baghdad:ME-10'][0]],research_checks={},unresolved=['Fixture remaining qualification'],scope='Fixture geometry only',**core.FLAGS)
            core.write(private/'proposal.json',proposal)
        else:
            review=dict(decision='research-improvement',proposal_sha256=request['proposal_sha256'],proposed_source_sha256=request['proposed_source_sha256'],reasons=['Fixture concrete proposed detail'],remaining_work=['Native unavailable and qualification open'],**core.FLAGS)
            core.write(private/'review.json',review)
        return folder/'process.log'
    monkeypatch.setattr(core,'_process',process)
    result=development.run(w)
    assert phases==['author','evaluate','reviewer'] and result['state']=='hold' and not result['automatically_installed']
    folder=Path(result['folder']);assert not (folder/'worktree').exists() and (folder/'retained-private/proposed.py').is_file()
    assert workflow.verify_folder(folder)['decision']=='hold'
    assert development.run(w)['state']=='hourly-development-budget'


def test_mandatory_supplemental_failures_veto_research_selection_and_are_retained_as_diagnostics(campaign,tmp_path):
    w=execute_examples(campaign);epoch=campaign[1]
    with workflow.locked(w) as (_,db):
        assert 'service-cassette' not in {r['kind'] for r in workflow.representatives(db,epoch)}
        diagnostic=next(r for r in workflow.diagnostics(db,epoch) if r['kind']=='service-cassette')
        original=core.read(Path(diagnostic['folder'])/'result.json')
        chain=core.read(Path(diagnostic['folder'])/'cassette-system.json')
        assert original['state']=='failed' and original['failed_checks']
        assert original['supplemental_evidence']['cassette-system']==chain
        for name,value in chain['checks'].items():assert original['checks']['cassette-system/'+name] is value
        assert 'cassette-system/worst_case_guide_fit' in original['failed_checks']
        assert 'cassette-system/connector_derating' in original['held_checks']
    output=tmp_path/'diagnostic-export';publication.export(w,output)
    assert (output/'diagnostics/service-cassette/cassette-system.json').exists()
    assert not (output/'models/service-cassette').exists()
    data=core.read(output/'progress.json');entry=next(r for r in data['diagnostics'] if r['kind']=='service-cassette')
    assert not entry['selection_eligible'] and entry['key']==diagnostic['key']
    assert publication.verify(output)['verified']
    entry['selection_eligible']=True;core.write(output/'progress.json',data)
    (output/'index.html').write_text(publication.report(data,campaign[2]['policy']));reseal(output)
    with pytest.raises(ValueError,match='diagnostic'):publication.verify(output)
