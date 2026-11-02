"""Small orchestrator contracts; transport stubs are not numerical evidence.

An isolated source worker may point OSR_TOPOLOGY_ORCHESTRATOR_ROOT at the
coordinator's current checkout. The temporary package path is restored afterward.
No baseline, campaign worker or native solver is invoked by these controls.
"""
from copy import deepcopy
import gzip
import importlib.util
import json
import os
from pathlib import Path
import sys

import numpy as np
import pytest

REPO=Path(__file__).resolve().parents[3]
SOURCE_ROOT=Path(os.environ.get('OSR_TOPOLOGY_ORCHESTRATOR_ROOT',REPO)).resolve()


@pytest.fixture(scope='module')
def h():
    import engineering
    import engineering.design_search
    packages=[engineering,engineering.design_search]
    saved=[p.__path__ for p in packages]
    old_path=list(sys.path)
    try:
        sys.path.insert(0,str(SOURCE_ROOT))
        for package,relative in zip(packages,('engineering','engineering/design_search')):
            package.__path__=[str(SOURCE_ROOT/relative),*package.__path__]
        spec=importlib.util.spec_from_file_location('engineering.design_search._civil_topology_contract_current',SOURCE_ROOT/'engineering/design_search/civil_topology.py')
        module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
        yield module
    finally:
        sys.path[:]=old_path
        for package,path in zip(packages,saved):package.__path__=path
        sys.modules.pop('engineering.design_search._civil_topology_contract_current',None)


@pytest.fixture(autouse=True)
def no_actual_campaign_or_system_baseline(h,monkeypatch):
    def forbidden(*args,**kwargs):raise AssertionError('Unit controls must not execute campaigns or system baselines')
    for name in ('run','plan','evaluate_trial','_worker','_baseline','make_baseline'):
        if hasattr(h,name):monkeypatch.setattr(h,name,forbidden)


def problem(h,nx=80,nz=4):
    return h.kernel.mesh(dict(nx=nx,nz=nz,length_m=20.,height_m=1.2,thickness_m=.04,E_Pa=200e9,poisson=.3))


@pytest.mark.parametrize('nx',[40,80,160])
def test_finite_patches_preserve_analytic_force_and_first_moment_across_meshes(h,nx):
    p=problem(h,nx);case=dict(offsets_m=[-.10,0.,1.37,20.,20.10],full_axle_force_N=1000.)
    patches=h._points(case,dict(translation_m=0.),20.,.25)
    # Exact overlap fractions: .1 + .5 +1 +.5 +.1; outside axle portions
    # remain on the neighbouring span instead of becoming whole span loads.
    assert sum(v['force_N'] for v in patches)==pytest.approx(2200.)
    assert all(v['x_m']==pytest.approx((v['x_min_m']+v['x_max_m'])/2) for v in patches)
    F=h.top_load(p,patches,distributed_N_m=3200.)
    expected=2200+3200*20
    moment=sum(v['force_N']*(v['x_min_m']+v['x_max_m'])/2 for v in patches)+3200*20**2/2
    assert -F[1::2].sum()==pytest.approx(expected,rel=1e-13)
    assert -(F[1::2]*p['nodes'][:,0]).sum()==pytest.approx(moment,rel=1e-13)
    assert np.all(F[0::2]==0) and np.all(F[1::2]<=0)
    w=h.line_weights(p,.013,.288)
    assert w.sum()==pytest.approx(.288-.013,rel=1e-12)
    assert w@p['nodes'][:nx+1,0]==pytest.approx((.288**2-.013**2)/2,rel=1e-12)


def test_three_mean_bearings_are_not_node_clamps_or_right_axial_restraint(h):
    p=problem(h,160);spec=h.specification(SOURCE_ROOT);C=h.support_constraints(p,spec);xy=p['nodes']
    assert C.shape==(3,p['ndof']) and h.fixed_dofs(p).size==0
    np.testing.assert_allclose(C.sum(axis=1),1.,atol=1e-14)
    assert all(np.count_nonzero(row)>1 for row in C)
    rigid=np.column_stack((np.tile([1.,0.],len(xy)),np.tile([0.,1.],len(xy)),np.c_[-xy[:,1],xy[:,0]].ravel()))
    assert np.linalg.matrix_rank(C@rigid)==3
    # A local linear rotation about the left bearing mean has nonzero nodal
    # vertical movements but zero constrained mean: the patch is not clamped.
    u=np.zeros(p['ndof']);bottom=np.flatnonzero((xy[:,1]==0)&(xy[:,0]<=spec['search']['bearing_patch_length_m']))
    u[2*bottom+1]=xy[bottom,0]-spec['search']['bearing_patch_length_m']/2
    assert np.max(np.abs(u))>0
    np.testing.assert_allclose(C@u,0.,atol=1e-14)
    expansion=np.zeros_like(u);right=np.flatnonzero(xy[:,0]>19.)
    expansion[2*right]=1.
    np.testing.assert_allclose(C@expansion,0.,atol=1e-14)


def context_inputs(h):
    cases=[dict(name=name,offsets_m=[0.,2.9,14.1,17.5,20.,35.]) for name in ('empty','normal','crowd_control')]
    base=dict(context_id='base-context',vehicle_candidate_id='same-vehicle',vehicle_evaluation_id='same-evaluation',selection_id='same-selection',dynamic_factor_hypothesis=1.3,cases=cases,source_sha256={})
    reserve=dict(candidate_id='same-vehicle',selection_id='same-selection',result_id='reserve-result',source_sha256={},sensitivity_cases=[dict(name=name,scenario_tare_mass_kg_per_car=value) for name,value in [('low',18000.),('base',19000.),('high',21000.)]])
    selected=dict(candidate_id='same-vehicle',evaluation_id='same-evaluation',body_candidate_id='body',support_component_id='support',propulsion_component_id='propulsion')
    return base,reserve,dict(vehicle=selected,selection_id='same-selection')


def test_context_keeps_component_identities_and_replaces_vehicle_reserves_once(h,monkeypatch):
    base,reserve,selected=context_inputs(h)
    monkeypatch.setattr(h.civil_shape_mechanics,'load_context',lambda root:deepcopy(base));monkeypatch.setattr(h.mass_reserve_sensitivity,'plan',lambda root:deepcopy(reserve));monkeypatch.setattr(h.selection,'load',lambda root:deepcopy(selected))
    value=h.load_context(SOURCE_ROOT)
    assert value['context_id']==h.identity({k:v for k,v in value.items() if k!='context_id'})
    assert {k:value[k] for k in ('body_candidate_id','support_component_id','propulsion_component_id')}=={k:selected['vehicle'][k] for k in ('body_candidate_id','support_component_id','propulsion_component_id')}
    assert len(value['cases'])==9
    for case in value['cases']:
        people={'empty':0,'normal':46,'crowd_control':160}[case['name']]
        assert case['loaded_kg_per_car']==case['tare_kg_per_car']+75*people
        assert case['full_axle_force_N']==pytest.approx(case['loaded_kg_per_car']*h.civil.G/4*1.3)
    assert all(value[key] is False for key in h.FLAGS)
    assert base['source_sha256']=={} and reserve['source_sha256']=={}


@pytest.mark.parametrize('where,key',[('reserve','candidate_id'),('reserve','selection_id'),('selected','candidate_id'),('selected','evaluation_id')])
def test_mixed_context_ancestry_is_rejected(h,monkeypatch,where,key):
    base,reserve,selected=context_inputs(h)
    (reserve if where=='reserve' else selected['vehicle'])[key]='other'
    monkeypatch.setattr(h.civil_shape_mechanics,'load_context',lambda root:base);monkeypatch.setattr(h.mass_reserve_sensitivity,'plan',lambda root:reserve);monkeypatch.setattr(h.selection,'load',lambda root:selected)
    with pytest.raises(ValueError):h.load_context(SOURCE_ROOT)


def test_actual_gravity_handoff_keeps_all81_rhs_and_independent_physical_first_moment(h,monkeypatch):
    p=problem(h,40);spec=h.specification(SOURCE_ROOT);mask=np.ones((4,40),dtype=bool);mask[1:3,4:10]=False
    c=h.geometry.realize(mask,**spec['geometry']);q=h.geometry.quantities(c);captured={}
    cases=[dict(name=name,vehicle_mass_case=mass,full_axle_force_N=10000.+1000*j,offsets_m=[0.,2.9,14.1,17.5,20.,35.]) for j,(mass,name) in enumerate((m,n) for m in ('low','base','high') for n in ('empty','normal','crowd_control'))]
    poses=[h.critical_pose(20.,cases[0]['offsets_m'],name) for name in spec['search']['pose_controls']]
    def no_solver(problem,occupied,forces,fixed,**kwargs):
        captured.update(forces=forces,mask=occupied,constraints=kwargs['constraint_matrix']);return dict(execution='not-run',reason='test transport stub; no numerical evidence')
    monkeypatch.setattr(h.kernel,'solve_binary',no_solver)
    raw,summary=h.replay(p,mask,spec,dict(cases=cases),q,poses)
    assert captured['forces'].shape==(p['ndof'],81) and np.array_equal(captured['mask'],mask.ravel())
    assert raw['execution']==summary['execution']=='not-run'
    rail=h._rail_account(20.);column=0
    for vehicle in cases:
        for index in range(3):
            accounted=q['accounted_mass_kg_cases'][index]+rail['rail_kg']+rail['complete_fastener_account_kg']
            for pose in poses:
                points=h._points(vehicle,pose,20.,spec['search']['wheel_load_patch_length_m']);F=captured['forces'][:,column];column+=1
                assert -F[1::2].sum()==pytest.approx(accounted*h.civil.G+sum(v['force_N'] for v in points),rel=1e-12)
                nominal=q['quantities']['nominal_mass_kg'];cg=q['quantities']['nominal_CG_m'][0]
                expected=(nominal*cg+(accounted-nominal)*10)*h.civil.G+sum(v['force_N']*v['x_m'] for v in points)
                assert -(F[1::2]*p['nodes'][:,0]).sum()==pytest.approx(expected,rel=1e-12)


def change_setting(text,section,key,literal):
    current=None;lines=text.splitlines();found=False
    for i,line in enumerate(lines):
        if line.startswith('['):current=line.strip('[]')
        elif current==section and line.startswith(key+' ='):lines[i]=key+' = '+literal;found=True
    assert found;return '\n'.join(lines)+'\n'


@pytest.mark.parametrize('section,key,value',[(None,'reference_changes_allowed','true'),('geometry','span_m','21.0'),('resources','maximum_rhs','16'),('resources','maximum_address_space_bytes','0'),('resources','maximum_cpu_seconds','0'),('resources','workers','2'),('resources','native_jobs','1'),('search','nz','4'),('search','penalty','0.5'),('search','wheel_load_patch_length_m','-0.25'),('elastic_hypotheses','steel_density_kg_m3','1e300'),('replay','relative_linear_residual_tolerance','nan')])
def test_invalid_geometry_load_and_resource_contracts_fail_before_trial(h,tmp_path,section,key,value):
    text=(SOURCE_ROOT/h.CAMPAIGN).read_text();path=tmp_path/h.CAMPAIGN;path.parent.mkdir(parents=True)
    path.write_text(change_setting(text,section,key,value))
    with pytest.raises(ValueError):h.specification(tmp_path)


def fixture_package(h,tmp_path):
    spec=h.specification(SOURCE_ROOT);trial=h.trials(spec)[0]
    configured=dict(campaign_id='typed-campaign',specification=spec,load_context=dict(context_id='typed-context'),cost_specification={},source_sha256={'fixture':'a'*64},tool_context=dict(tool_context_id='typed-tools'),trials=[trial])
    request=h._request(configured,trial);out=tmp_path/'trials'/trial['trial_id'];out.mkdir(parents=True)
    mask=np.ones((2,4),dtype=bool);physical=h.geometry.realize(mask,**spec['geometry'])
    result=dict(schema='test-only-transport',execution='completed',request_id=request['request_id'],trial=trial,physical_geometry=physical,**h.FLAGS);result['evaluation_id']=h.identity(result)
    (out/'request.json').write_bytes(h.encoded(request));(out/'result.json.gz').write_bytes(gzip.compress(h.encoded(result),mtime=0));np.savez_compressed(out/'arrays.npz',density_field=mask.astype(float),binary_occupancy=mask)
    (out/'stdout.log').write_text('typed fixture, no worker executed\n');(out/'stderr.log').write_text('')
    receipt=dict(request_id=request['request_id'],tool_context=configured['tool_context'],source_sha256=configured['source_sha256'],files_sha256={name:h.digest(out/name) for name in ('result.json.gz','arrays.npz')},**h.FLAGS);receipt['receipt_id']=h.identity(receipt)
    (out/'worker.json').write_bytes(h.encoded(receipt));row=dict(trial_id=trial['trial_id'],request_id=request['request_id'],returncode=0,worker_receipt_id=receipt['receipt_id'])
    def reseal():
        receipt=json.loads((out/'worker.json').read_bytes());receipt['files_sha256']={name:h.digest(out/name) for name in ('result.json.gz','arrays.npz')};receipt.pop('receipt_id',None);receipt['receipt_id']=h.identity(receipt);(out/'worker.json').write_bytes(h.encoded(receipt));row['worker_receipt_id']=receipt['receipt_id'];row['files_sha256']={p.name:h.digest(p) for p in out.iterdir() if p.is_file() and p.name!='attempt.json'};row.pop('attempt_id',None);row['attempt_id']=h.identity(row);(out/'attempt.json').write_bytes(h.encoded(row))
    reseal();return configured,out,row,reseal


def test_completed_transport_fixture_is_read_without_actual_trial(h,tmp_path):
    configured,out,row,reseal=fixture_package(h,tmp_path)
    value=h._read_attempt(tmp_path,row,configured)
    assert value['execution']=='completed' and all(value[k] is False for k in h.FLAGS)


@pytest.mark.parametrize('tamper',['payload','extra','symlink','acceptance','result-request','mask','physical','tools','checkpoint-request'])
def test_immutable_attempt_and_resealed_semantic_tampering_are_rejected(h,tmp_path,tamper):
    configured,out,row,reseal=fixture_package(h,tmp_path)
    if tamper=='payload':(out/'stdout.log').write_text('tampered')
    elif tamper=='extra':(out/'unexpected').write_text('extra')
    elif tamper=='symlink':(out/'linked').symlink_to(out/'request.json')
    elif tamper in ('acceptance','result-request'):
        value=json.loads(gzip.decompress((out/'result.json.gz').read_bytes()));value['physical_accepted' if tamper=='acceptance' else 'request_id']=True if tamper=='acceptance' else 'other';value.pop('evaluation_id');value['evaluation_id']=h.identity(value);(out/'result.json.gz').write_bytes(gzip.compress(h.encoded(value),mtime=0));reseal()
    elif tamper in ('mask','physical'):
        density=np.ones((2,4));mask=density.astype(bool);mask[0,0]=False
        if tamper=='physical':density[0,0]=0.
        np.savez_compressed(out/'arrays.npz',density_field=density,binary_occupancy=mask);reseal()
    elif tamper=='tools':
        value=json.loads((out/'worker.json').read_bytes());value['tool_context']={'tool_context_id':'other'};(out/'worker.json').write_bytes(h.encoded(value));reseal()
    else:
        checkpoint=dict(request_id='other',phase='typed',data={},**h.FLAGS);checkpoint['checkpoint_id']=h.identity(checkpoint);(out/'checkpoint-typed.json.gz').write_bytes(gzip.compress(h.encoded(checkpoint),mtime=0));reseal()
    with pytest.raises(ValueError):h._read_attempt(tmp_path,row,configured)


@pytest.mark.parametrize('relative,meets',[(1e-10,True),(2e-8,False)])
def test_constraint_relative_request_gate_rejects_tiny_absolute_but_bad_relative_error(h,relative,meets):
    p=problem(h,40);spec=h.specification(SOURCE_ROOT)
    errors=np.zeros((3,2));errors[2,1]=relative
    result=dict(execution='completed',numerical_validity='fixture-only-no-solve',displacements=np.full((p['ndof'],2),1e-12),compliances=np.ones(2),strain_energy_J=np.full(2,.5),free_residual_relative=np.full(2,1e-10),constraint_residual_relative=errors,force_equilibrium_residual_N=np.zeros((2,2)),moment_equilibrium_residual_Nm=np.zeros(2),energy_residual_J=np.zeros(2),constraint_residual=np.full((3,2),1e-20))
    value=h._summary_analysis(p,result,[dict(total_downward_force_N=1000.)]*2,spec)
    assert value['declared_residual_request_met'] is meets
    if not meets:assert value['numerical_validity']=='declared-numerical-residual-request-not-met'
    assert value['physical_accepted'] is False and value['engineering_accepted'] is False


def test_failed_partial_attempt_keeps_immutable_inputs_without_requiring_fake_result(h,tmp_path):
    configured,out,row,reseal=fixture_package(h,tmp_path)
    for name in ('arrays.npz','result.json.gz','worker.json'):(out/name).unlink()
    (out/'stderr.log').write_text('bounded worker failure; no physical failure inferred')
    row.update(returncode=1);row.pop('worker_receipt_id');row['files_sha256']={p.name:h.digest(p) for p in out.iterdir() if p.name!='attempt.json'};row.pop('attempt_id');row['attempt_id']=h.identity(row);(out/'attempt.json').write_bytes(h.encoded(row))
    assert h._read_attempt(tmp_path,row,configured) is None
    assert 'no physical failure inferred' in (out/'stderr.log').read_text()


def test_small_two_rhs_kernel_result_preserves_all_three_constraint_rows_in_summary(h):
    #54DOF unit method control, not a generated candidate or campaign trial.
    p=problem(h,8,2);spec=h.specification(SOURCE_ROOT)
    F=np.column_stack([h.top_load(p,[dict(x_m=x+.25,x_min_m=x,x_max_m=x+.5,force_N=force)]) for x,force in [(6.,1000.),(12.,1500.)]])
    raw=h.kernel.solve(p,np.ones(p['nelements']),F,h.fixed_dofs(p),constraint_matrix=h.support_constraints(p,spec))
    assert raw['constraint_residual_relative'].shape==(3,2)
    summary=h._summary_analysis(p,raw,[dict(total_downward_force_N=1000.),dict(total_downward_force_N=1500.)],spec)
    assert len(summary['cases'])==2 and summary['declared_residual_request_met']
    assert summary['physical_accepted'] is False
