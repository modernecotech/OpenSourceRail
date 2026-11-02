"""Small portable-publication controls; no campaign, baseline generation or FE."""
from copy import deepcopy
import importlib.util
from pathlib import Path
import signal
import sys
import xml.etree.ElementTree as ET

import numpy as np
import pytest

from engineering.design_search import portable_gzip
from engineering.station_rail.common import digest,encoded,identity

_spec=importlib.util.spec_from_file_location('engineering.design_search.topology_revision_publication',
    Path(__file__).resolve().parents[1]/'topology_revision_publication.py')
p=importlib.util.module_from_spec(_spec);sys.modules[_spec.name]=p;_spec.loader.exec_module(p)


@pytest.fixture(autouse=True)
def bounded_no_execution(monkeypatch):
    def forbidden(*args,**kwargs):raise AssertionError('Publication controls may not run models or campaigns')
    for module,names in ((p.parent,('run','_worker','mesh','replay','plan','_state')), (p.campaign,('run','_worker','plan','_state','_check_plan')),
            (p.topology_system_cost,('make_baseline','validate_baseline','compare'))):
        for name in names:monkeypatch.setattr(module,name,forbidden)
    old=signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('30-second control budget')));signal.alarm(30)
    yield
    signal.alarm(0);signal.signal(signal.SIGALRM,old)


def seal(record,key):record=deepcopy(record);record[key]=identity(record);return record


def spec():
    return dict(geometry=deepcopy(p.geometry.FIXED),elastic_hypotheses=dict(steel_density_kg_m3=7850.,concrete_density_kg_m3=2400.),
        search=dict(nx=6,nz=6),replay=dict(relative_linear_residual_tolerance=1e-7,relative_equilibrium_tolerance=1e-7,
            relative_energy_tolerance=1e-7,two_mesh_compliance_change_target=.1))


def replay(gate=True,compliance=10.,displacement=17.65):
    rows=[]
    for i in range(81):
        rows.append(dict(load_case=('empty','normal','crowd_control')[i//27],vehicle_mass_case=('low','base','high')[(i//9)%3],
            span_mass_case=('low','base','high')[(i//3)%3],pose=str(i%3),compliance_J=compliance,strain_energy_J=compliance/2,
            maximum_absolute_displacement_m=displacement,maximum_vertical_displacement_m=displacement,
            free_residual_relative=1e-9 if gate else 1e-3,constraint_residual_relative=1e-9,
            relative_force_equilibrium_residual=1e-9,relative_moment_equilibrium_residual=1e-9,relative_energy_residual=1e-9))
    return dict(execution='completed',cases=rows,declared_residual_request_met=gate,
        maximum_free_residual_relative=1e-9 if gate else 1e-3,void_stiffness_credited=False,
        physical_acceptance_limit_available=False,contact_stiffness_and_load_sharing_qualified=False,**p.parent.FLAGS)


def system(host='old'):
    from engineering.design_search.model_cost import SCOPES
    return dict(candidate_id='7'*64,evaluation_id=host,replay_context=dict(host=host),comparison_to_corrected_canonical_baseline={},
        cases={name:dict(factory_gate_cost_iqd=[1,2,3],delivered_cost_iqd=[2,3,4],model_based_installed_CAPEX_iqd=[3,4,5],
            model_based_whole_life_NPV_iqd=[4,5,6],scope_totals_iqd={scope:[1,2,3] for scope in SCOPES},
            production_plan=dict(production_shifts=2,civil_shifts=2,operations_scenarios=[2,3])) for name in ('low','base','high')})


def inputs():
    mask=np.zeros((6,6),bool);mask[[0,-1],:]=True;mask[:,[0,-1]]=True;mask[2,2]=True
    passive=mask.copy();passive[2,2]=False;rho=np.full(mask.shape,.2);rho[mask]=.8;physical=p.geometry.realize(mask)
    binding=p.revisions.make_parent_input(physical,mask,rho,passive,parent_evaluation_id='a'*64,parent_request_id='b'*64,
        arrays_package_sha256='c'*64,required_passive_cell_ids=np.flatnonzero(passive).tolist())
    child=dict(parent_input=binding,strategy=p.revisions.STRATEGIES[0],parent_trial_id='d'*64,parent_request_id='b'*64,
        parent_evaluation_id='a'*64,parent_candidate_id=physical['candidate_id'])
    proposal=p.revisions.propose(binding,physical,mask,rho,passive,strategy=child['strategy']);candidate=proposal['proposed_geometry']
    cs=p.topology_cost.default_spec();quantity=p.geometry.quantities(candidate,dict(steel=7850.,concrete=2400.),reserves_kg=cs['reserve_mass_kg'],module_length_m=cs['module_length_m'])
    configured=dict(proposal_policy=dict(p.campaign.PROPOSAL_POLICY),parent_plan=dict(specification=spec(),cost_specification=cs))
    original=dict(physical_geometry=physical,representative_poses=[dict(name=str(i)) for i in range(3)])
    baseline=dict(baseline_id='e'*64,load_context_id='f'*64,assumptions={},selected=dict(selection_id='s'*64,candidate_id='v'*64,vehicle_evaluation_id='w'*64))
    result=dict(execution='completed',evaluation_id='0'*64,proposal=proposal,physical_geometry=candidate,composition_candidate_id='7'*64,
        candidate_id=candidate['candidate_id'],quantities=quantity,span_cost=dict(cases=[dict(case=x,scoped_installed_iqd=123.,total_factory_person_hours=42.) for x in ('low','base','high')]),
        system_cost=system(),support_demands={'area':1.},representative_poses=original['representative_poses'],load_context_id=baseline['load_context_id'],
        coarse_replay=replay(compliance=8.),fine_replay=replay(),compliance_relative_changes=[.2]*81,numerical_refinement_status='mesh-unresolved')
    return result,child,original,mask,rho,passive,configured,baseline


def algebra(monkeypatch,result):
    monkeypatch.setattr(p.topology_cost,'estimate',lambda *args:deepcopy(result['span_cost']))
    monkeypatch.setattr(p.parent,'support_demands',lambda *args:deepcopy(result['support_demands']))
    current=system('different-current-ci-host')
    def compare(*args,**kwargs):assert kwargs['require_current_tools'] is False;return deepcopy(current)
    monkeypatch.setattr(p.topology_system_cost,'compare',compare)
    return current


def test_algebraic_replay_preserves_tool_epoch_but_recomputes_physical_quantities_and_costs(monkeypatch,tmp_path):
    values=inputs();algebra(monkeypatch,values[0]);p._recalculate(*values,root=tmp_path)


@pytest.mark.parametrize('damage',('quantity','scope','cost','support','geometry','load','pose'))
def test_algebraic_replay_rejects_mixed_or_changed_inputs(monkeypatch,tmp_path,damage):
    values=inputs();result=values[0];current=algebra(monkeypatch,result)
    if damage=='quantity':result['quantities']['quantities']['steel_net_mass_kg']+=1
    elif damage=='scope':del current['cases']['base']['scope_totals_iqd']['guideway']
    elif damage=='cost':current['cases']['base']['model_based_whole_life_NPV_iqd'][1]+=1
    elif damage=='support':monkeypatch.setattr(p.parent,'support_demands',lambda *args:{'area':2.})
    elif damage=='geometry':result['physical_geometry']=p.geometry.realize([[1]])
    elif damage=='load':result['load_context_id']='changed'
    else:result['representative_poses']=[dict(name='different')]
    with pytest.raises(ValueError):p._recalculate(*values,root=tmp_path)


def test_all81_residuals_gate_archive_and_preserve_large_displacement_unresolved_mesh():
    values=inputs();result,child=values[:2];p._numerics(result,spec())
    attempt=dict(trial_id='1'*64,request_id='2'*64,attempt_id='3'*64,execution='worker-completed',runtime_seconds=1.)
    row,elite=p._row(attempt,result,child)
    assert row['fine_replay']['maximum_vertical_displacement_m']==17.65
    assert row['refinement_status']=='mesh-unresolved' and row['binary_replay_admitted_to_archive'] is True
    assert row['physical_model_or_material_strength_qualified'] is False and elite is not None
    result['fine_replay']=replay(gate=False);result['compliance_relative_changes']=None
    p._numerics(result,spec());row,elite=p._row(attempt,result,child)
    assert row['fine_replay']['residual_request_met'] is False and elite is None
    assert row['binary_replay_admitted_to_archive'] is False and row['fine_replay']['maximum_vertical_displacement_m']==17.65


@pytest.mark.parametrize('damage',('missing-case','gate','maximum','refinement','nonfinite','promotion'))
def test_numerical_summary_inconsistencies_cannot_be_promoted(damage):
    result=inputs()[0]
    if damage=='missing-case':result['fine_replay']['cases'].pop()
    elif damage=='gate':result['fine_replay']['cases'][-1]['relative_energy_residual']=.1
    elif damage=='maximum':result['fine_replay']['maximum_free_residual_relative']=.1
    elif damage=='refinement':result['numerical_refinement_status']='accepted'
    elif damage=='nonfinite':result['fine_replay']['cases'][0]['maximum_vertical_displacement_m']=float('inf')
    else:result['fine_replay']['physical_accepted']=True
    with pytest.raises(ValueError):p._numerics(result,spec())


def test_displacement_arrays_have_all81_rhs_and_reproduce_uncapped_maxima(tmp_path):
    result=inputs()[0];arrays={}
    for name,factor in (('coarse',1),('fine',2)):
        arrays[name+'_displacements']=np.full((2*(6*factor+1)**2,81),17.65)
    path=tmp_path/'arrays.npz';np.savez_compressed(path,**arrays);p._displacement_links(path,result,spec())
    arrays['fine_displacements'][1,0]=20.;np.savez_compressed(path,**arrays)
    with pytest.raises(ValueError,match='summary'):p._displacement_links(path,result,spec())


def test_failed_and_rejected_attempts_keep_ancestry_and_never_enter_archive():
    result,child,*_=inputs();attempt=dict(trial_id='1'*64,request_id='2'*64,attempt_id='3'*64,execution='wall-timeout',runtime_seconds=150.)
    row,elite=p._row(attempt,None,child)
    assert row['execution']=='wall-timeout' and row['candidate_id'] is None and elite is None
    assert row['parent_arrays_package_sha256']=='c'*64 and row['system_cost'] is None


def test_manifest_checks_every_file_and_rejects_links_promotions_and_extra_payload(tmp_path):
    folder=tmp_path/'packet';folder.mkdir();(folder/'payload').write_text('preserved')
    manifest=seal(dict(schema='osr-topology-revision-publication/1',files_sha256=p._payload(folder),**p.FLAGS),'manifest_id')
    (folder/'manifest.json').write_bytes(encoded(manifest));assert p._check(folder)==manifest
    (folder/'extra').write_text('unexpected')
    with pytest.raises(ValueError):p._check(folder)
    (folder/'extra').unlink();(folder/'linked').symlink_to(folder/'payload')
    with pytest.raises(ValueError):p._check(folder)
    (folder/'linked').unlink();manifest['physical_accepted']=True;manifest.pop('manifest_id');manifest=seal(manifest,'manifest_id');(folder/'manifest.json').write_bytes(encoded(manifest))
    with pytest.raises(ValueError):p._check(folder)


def test_readme_and_svg_show_uncapped_demands_mesh_status_and_qualification_limits():
    result,child,*_=inputs();attempt=dict(trial_id='1'*64,request_id='2'*64,attempt_id='3'*64,execution='worker-completed',runtime_seconds=1.)
    row,_=p._row(attempt,result,child)
    value=dict(trial_count=12,unique_realized_candidate_count=10,archive_eligible_candidate_count=4,attempts=[row])
    text=p._readme(value)
    assert '17650' in text and 'mesh-unresolved' in text and 'Unqualified' in text
    assert 'small-displacement' in text and 'fourteen' in text and 'two-to-three-shift' in text
    svg='<svg xmlns="http://www.w3.org/2000/svg">'+p._drawing(0,row,result)+'</svg>'
    ET.fromstring(svg);assert 'unqualified' in svg


def test_parent_context_uses_published_ancestry_and_accepts_preserved_tool_paths(tmp_path,monkeypatch):
    folder=tmp_path/p.parent.OUTPUT;folder.mkdir(parents=True)
    old_tools=seal(dict(host='/original/absent/python',binary_sha256='a'*64),'tool_context_id')
    current_tools=seal(dict(host='/different/ci/python',binary_sha256='b'*64),'tool_context_id')
    trials=[dict(trial_id=str(i)*64,kind='full-solid-reference' if i==0 else 'optimized-density') for i in range(7)]
    configured=seal(dict(tool_context=old_tools,trials=trials,load_context={'id':'load'},source_sha256={'old':'c'*64}),'campaign_id')
    current=deepcopy(configured);current['tool_context']=current_tools;current.pop('campaign_id');current=seal(current,'campaign_id')
    baseline=dict(baseline_id='base',load_context=configured['load_context'])
    (folder/'baseline.json.gz').write_bytes(portable_gzip.compress(encoded(baseline)))
    state=dict(schema='osr-civil-topology-state/1',plan=configured,baseline=dict(baseline_id='base',file_sha256=digest(folder/'baseline.json.gz')),
        pending_trial_ids=[],completed=[dict(trial_id=t['trial_id']) for t in trials]);(folder/'state.json').write_bytes(encoded(state));(folder/'manifest.json').write_text('{}')
    monkeypatch.setattr(p.previous,'_check',lambda folder:dict(manifest_id='manifest',source_sha256={'same':True}))
    monkeypatch.setattr(p.previous,'sources',lambda root:{'same':True});monkeypatch.setattr(p.parent,'plan',lambda root:current)
    calls=[]
    def validate(value,root,*,require_current_tools):calls.append(require_current_tools);assert value==baseline
    monkeypatch.setattr(p.topology_system_cost,'validate_baseline',validate)
    monkeypatch.setattr(p.parent,'_read_attempt',lambda *args:{'original':'reference'})
    def read(folder,row,*args):
        calls.append(row['trial_id']);return ({'physical_geometry':{},'representative_poses':[]},np.ones((1,1),bool),np.ones((1,1)),np.ones((1,1),bool),{'parent_trial_id':row['trial_id']})
    monkeypatch.setattr(p.campaign,'_parent_data',read)
    original,observed,records,binding=p._parent_context(tmp_path)
    assert original==state and observed==baseline and len(records)==6
    assert calls[0] is False and len(calls)==7 and binding['path']==p.parent.OUTPUT
    assert original['plan']['tool_context']!=current['tool_context']
    current['load_context']={'changed':True}
    with pytest.raises(ValueError,match='configuration'):p._parent_context(tmp_path)


def test_publish_performs_one_full_stage_verification_and_preserves_old_packet(tmp_path,monkeypatch):
    source=tmp_path/'state';source.mkdir();(source/'state.json').write_text('{}');(source/'baseline.json.gz').write_bytes(b'baseline');(source/'trials').mkdir()
    value=dict(portfolio_id='p',parent_publication={'manifest':'original'},trial_count=12,unique_realized_candidate_count=10,archive_eligible_candidate_count=4,attempts=[])
    calls=[]
    def reproduce(stage,root):calls.append(stage);assert stage!=source;return value,'<svg/>',{'source':'digest'}
    monkeypatch.setattr(p,'_reproduce',reproduce)
    out=tmp_path/'docs/result';report=p.publish(source,root=tmp_path,output=out)
    assert report['verified'] and len(calls)==1 and (out/'manifest.json').is_file()
    assert (source/'baseline.json.gz').read_bytes()==b'baseline'
    p.verify(root=tmp_path,output=out);assert len(calls)==2
    (out/'README.md').write_text('changed')
    with pytest.raises(ValueError):p.verify(root=tmp_path,output=out)


def portable_plan(tmp_path,monkeypatch):
    for name in (p.campaign.PRODUCER,p.revisions.PRODUCER):
        path=tmp_path/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_text('fixture producer '+name)
    epoch={'upstream.py':'a'*64};monkeypatch.setattr(p.parent,'sources',lambda root,context=None:deepcopy(epoch))
    metadata={str(i)*64:({'parent_trial_id':str(i)*64,'parent_arrays_package_sha256':str(i)*64},None,None,None,None) for i in range(6)}
    original=dict(plan=seal(dict(load_context={},tool_context=seal(dict(host='/missing/recorded-python'),'tool_context_id')),'campaign_id'),baseline={'baseline_id':'original'})
    binding={'state_sha256':'b'*64};children=[]
    for key in sorted(metadata):
        for strategy in p.revisions.STRATEGIES:children.append(seal(dict(metadata[key][0],strategy=strategy),'trial_id'))
    current={**epoch,**{name:digest(tmp_path/name) for name in (p.campaign.PRODUCER,p.revisions.PRODUCER)}}
    configured=seal(dict(schema='osr-topology-revision-plan/1',parent_state_path='/missing/historical/build-state',
        parent_state_sha256=binding['state_sha256'],parent_plan=original['plan'],parent_campaign_id=original['plan']['campaign_id'],
        baseline=original['baseline'],source_sha256=dict(sorted(current.items())),tool_context=original['plan']['tool_context'],
        resources=dict(p.campaign.RESOURCES),proposal_policy=dict(p.campaign.PROPOSAL_POLICY),children=children,
        parent_count=6,maximum_children=12,SIMP_reexecuted=False,selection_purpose='next-experiment',**p.FLAGS),'campaign_id')
    return configured,original,metadata,binding


def test_portable_plan_requires_published_hash_ancestry_but_never_opens_old_absolute_path(tmp_path,monkeypatch):
    values=portable_plan(tmp_path,monkeypatch);p._validate_plan(*values,root=tmp_path)
    assert not Path(values[0]['parent_state_path']).exists()


@pytest.mark.parametrize('damage',('producer','parent-arrays','parent-campaign','coverage','promotion'))
def test_portable_plan_rejects_current_source_or_original_parent_identity_changes(tmp_path,monkeypatch,damage):
    values=portable_plan(tmp_path,monkeypatch);configured,original,metadata,binding=values
    if damage=='producer':(tmp_path/p.campaign.PRODUCER).write_text('changed source')
    elif damage=='parent-arrays':configured['children'][0]['parent_arrays_package_sha256']='f'*64
    elif damage=='parent-campaign':configured['parent_campaign_id']='f'*64
    elif damage=='coverage':configured['children'][1]=deepcopy(configured['children'][0])
    else:configured['physical_accepted']=True
    configured.pop('campaign_id');configured.update(seal(configured,'campaign_id'))
    with pytest.raises(ValueError):p._validate_plan(*values,root=tmp_path)


def test_streamed_projection_keeps_twelve_evaluations_ten_geometries_eight_residual_failures(tmp_path,monkeypatch):
    base,child,original,mask,rho,passive,configured,baseline=inputs();rows=[];results={};children=[]
    for i in range(12):
        key=format(i,'064x');entry=dict(child,trial_id=key);children.append(entry)
        rows.append(dict(trial_id=key,request_id='2'*64,attempt_id='3'*64,execution='worker-completed',runtime_seconds=1.))
        result=deepcopy(base);physical=np.ones((2,12),bool);physical[1,(i%10)+1:]=False
        result['physical_geometry']=p.geometry.realize(physical);result['candidate_id']=result['physical_geometry']['candidate_id'];result['evaluation_id']=key
        cs=configured['parent_plan']['cost_specification'];result['quantities']=p.geometry.quantities(result['physical_geometry'],dict(steel=7850.,concrete=2400.),reserves_kg=cs['reserve_mass_kg'],module_length_m=cs['module_length_m'])
        if i>=4:result['fine_replay']=replay(gate=False);result['compliance_relative_changes']=None
        results[key]=result
    configured.update(children=children,campaign_id='campaign');configured['baseline']={'file_sha256':'baseline'}
    state=dict(schema='osr-topology-revision-state/1',plan=configured,baseline=configured['baseline'],pending_trial_ids=[],completed=rows)
    (tmp_path/'baseline.json.gz').write_bytes(b'baseline');configured['baseline']['file_sha256']=digest(tmp_path/'baseline.json.gz')
    p.campaign._write(tmp_path/'state.json',state);(tmp_path/'trials').mkdir()
    for entry in children:(tmp_path/'trials'/entry['trial_id']).mkdir()
    parents={child['parent_trial_id']:({},original,mask,rho,passive)}
    monkeypatch.setattr(p,'_parent_context',lambda root:({},baseline,parents,{'original':'published'}))
    monkeypatch.setattr(p,'_validate_plan',lambda *args:None);monkeypatch.setattr(p,'sources',lambda *args:{'unchanged':'source'})
    monkeypatch.setattr(p.campaign,'_read_attempt',lambda folder,attempt,plan:deepcopy(results[attempt['trial_id']]))
    monkeypatch.setattr(p,'_recalculate',lambda *args:None);monkeypatch.setattr(p,'_displacement_links',lambda *args:None)
    value,svg,_=p._reproduce(tmp_path,tmp_path)
    assert value['trial_count']==12 and value['unique_realized_candidate_count']==10
    assert value['archive_eligible_attempt_count']==value['archive_eligible_candidate_count']==4
    assert value['residual_gate_failed_attempt_count']==8 and value['mesh_unresolved_attempt_count']==12
    assert len({r['evaluation_id'] for r in value['attempts']})==12
    assert value['integrated_selection'] is None and all(value[k] is False for k in p.FLAGS)
    assert len(value['archive']['retained_candidate_ids'])<=4;ET.fromstring(svg)
