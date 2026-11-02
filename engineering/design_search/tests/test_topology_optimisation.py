"""Independent controls for the bounded Q4/SIMP method, not railway acceptance."""
import numpy as np
import pytest

from engineering.design_search import topology_optimisation as t


def problem(nx=12,nz=4,length=3.,height=1.):
    return t.mesh(dict(nx=nx,nz=nz,length_m=length,height_m=height,
        thickness_m=.04,E_Pa=200e9,poisson=.3))


def cantilever(p,cases=1):
    nodes=p['nodes'];left=np.flatnonzero(nodes[:,0]==0)
    fixed=np.sort(np.r_[2*left,2*left+1])
    F=np.zeros((p['ndof'],cases));end=np.flatnonzero(nodes[:,0]==nodes[:,0].max())
    F[2*end+1,0]=-1000/len(end)
    if cases>1:F[2*end,1]=500/len(end)
    return F,fixed


def test_q4_rigid_modes_jacobian_symmetry_and_exact_affine_strain_energy():
    xy=np.array([[0.,0.],[2.,0.],[2.,.7],[0.,.7]])
    E,nu,thickness=170e9,.27,.05
    k=t.q4_stiffness(xy,E,nu,thickness)
    assert np.array_equal(k,k.T)
    rigid=np.column_stack((np.tile([1.,0.],4),np.tile([0.,1.],4),np.c_[-xy[:,1],xy[:,0]].ravel()))
    assert np.max(np.abs(k@rigid)) < 1e-5
    eigen=np.linalg.eigvalsh(k)
    assert sum(eigen>eigen.max()*1e-10)==5
    a,b,c,d=.002,-.0004,.0006,.001
    u=np.c_[a*xy[:,0]+b*xy[:,1],c*xy[:,0]+d*xy[:,1]].ravel()
    strain=np.array([a,d,b+c])
    D=E/(1-nu**2)*np.array([[1.,nu,0.],[nu,1.,0.],[0.,0.,(1-nu)/2]])
    expected=float(strain@D@strain)*2*.7*thickness
    assert u@k@u==pytest.approx(expected,rel=1e-13)
    with pytest.raises(ValueError,match='Jacobians'):
        t.q4_stiffness(xy[[0,3,2,1]],E,nu,thickness)
    # A skew affine element independently exercises the Jacobian inverse,
    # including off-diagonal terms absent from the axis-aligned mesh controls.
    xy[:,0]+=.3*xy[:,1]
    u=np.c_[a*xy[:,0]+b*xy[:,1],c*xy[:,0]+d*xy[:,1]].ravel()
    assert u@t.q4_stiffness(xy,E,nu,thickness)@u==pytest.approx(expected,rel=1e-13)


def test_multi_element_affine_patch_has_no_interior_force():
    p=problem(5,3);xy=p['nodes']
    k=t.assemble_stiffness(p,np.ones(p['nelements']))
    u=np.c_[.001*xy[:,0]+.002*xy[:,1],-.0003*xy[:,0]+.0004*xy[:,1]].ravel()
    inside=np.flatnonzero((xy[:,0]>0)&(xy[:,0]<3)&(xy[:,1]>0)&(xy[:,1]<1))
    assert np.max(np.abs((k@u)[np.r_[2*inside,2*inside+1]]))<1e-6


def test_solid_beam_matches_independent_bending_and_shear_and_balances_multiple_rhs():
    p=problem(80,8,10.,1.);F,fixed=cantilever(p,2)
    result=t.solve(p,np.ones(p['nelements']),F,fixed)
    end=np.flatnonzero(p['nodes'][:,0]==10.)
    measured=-result['displacements'][2*end+1,0].mean()
    E=200e9;nu=.3;A=.04;I=.04/12;G=E/(2*(1+nu))
    expected=1000*10**3/(3*E*I)+1000*10/((5/6)*G*A)
    assert measured==pytest.approx(expected,rel=.025)
    np.testing.assert_allclose(result['force_equilibrium_residual_N'],0,atol=2e-6)
    np.testing.assert_allclose(result['moment_equilibrium_residual_Nm'],0,atol=2e-5)
    np.testing.assert_allclose(2*result['strain_energy_J'],result['compliances'],rtol=1e-9)
    assert result['objective']==pytest.approx(result['compliances'].sum())
    assert not result['physical_accepted']


def test_density_filter_is_length_based_constant_preserving_and_boundary_normalised():
    p=problem(5,3);P=t.density_filter(p,.8)
    np.testing.assert_allclose(P@np.ones(p['nelements']),1.,atol=1e-15)
    centers=p['element_centres'];row=0
    weights=np.maximum(0.,.8-np.linalg.norm(centers-centers[row],axis=1))
    np.testing.assert_allclose(P.toarray()[row],weights/weights.sum(),atol=1e-15)


def test_full_filtered_gradient_includes_boundary_rows_and_passive_input_output_masks():
    p=problem(5,3);F,fixed=cantilever(p,2);P=t.density_filter(p,.85)
    passive=np.zeros(p['nelements'],dtype=bool);passive[[0,5,10]]=True
    x=np.linspace(.32,.7,p['nelements'])
    r=t.filtered_objective(p,x,F,fixed,P,passive)
    for index in (0,1,4,6,14):
        h=1e-6;minus=x.copy();plus=x.copy();minus[index]-=h;plus[index]+=h
        a=t.filtered_objective(p,minus,F,fixed,P,passive)
        b=t.filtered_objective(p,plus,F,fixed,P,passive)
        assert r['design_gradient'][index]==pytest.approx((b['objective']-a['objective'])/(2*h),rel=2e-5,abs=1e-9)
        assert r['volume_gradient'][index]==pytest.approx((b['volume_fraction']-a['volume_fraction'])/(2*h),rel=1e-7,abs=1e-10)
    assert np.all(r['design_gradient'][passive]==0)
    assert np.all(r['volume_gradient'][passive]==0)
    assert np.all(r['densities'][passive]==1)


def test_optimizer_progress_volume_passive_solids_and_last_state_replay():
    p=problem();F,fixed=cantilever(p)
    passive=np.zeros(p['nelements'],dtype=bool);passive[::12]=True
    result=t.optimise(p,F,fixed,passive,.55,.42,30,1e-5,15.)
    assert result['evaluated_iterations']<=30
    assert result['history'][-1]['objective']<.95*result['history'][0]['objective']
    assert all(row['volume_fraction']<=.55+1e-10 for row in result['history'])
    assert np.all(result['densities'][passive]==1)
    replay=t.solve(p,result['densities'],F,fixed)
    assert replay['objective']==pytest.approx(result['last_analysis']['objective'],rel=1e-13)
    assert not result['density_is_physical_geometry']


def test_iteration_and_time_exhaustion_are_explicit_and_never_claim_convergence():
    p=problem();F,fixed=cantilever(p);passive=np.zeros(p['nelements'],dtype=bool)
    r=t.optimise(p,F,fixed,passive,.5,.4,1,1e-12,10.)
    assert r['termination']=='iteration-budget' and not r['converged']
    assert r['evaluated_iterations']==1
    r=t.optimise(p,F,fixed,passive,.5,.4,10,1e-3,1e-12)
    assert r['termination']=='time-budget' and not r['converged']
    assert r['evaluated_iterations']==0 and r['last_analysis'] is None


def test_binary_solid_agrees_with_full_density_without_using_epsilon_voids():
    p=problem();F,fixed=cantilever(p,2)
    actual=t.solve_binary(p,np.ones(p['nelements'],dtype=bool),F,fixed)
    expected=t.solve(p,np.ones(p['nelements']),F,fixed)
    np.testing.assert_allclose(actual['displacements'],expected['displacements'],rtol=1e-12,atol=1e-15)
    assert actual['failure_reason'] is None
    assert actual['void_stiffness_used'] is False


def test_binary_removes_inactive_dofs_and_preserves_disconnected_and_corner_only_failures():
    p=problem(3,2);F=np.zeros((p['ndof'],1));fixed=np.array([0,1,3])
    # Only the bottom row is occupied, hence the top row nodes never enter Kff.
    occupied=np.array([1,1,1,0,0,0],dtype=bool)
    F[2*3+1]=-1
    r=t.solve_binary(p,occupied,F,fixed)
    assert r['execution']=='completed'
    assert len(r['active_dof_ids'])<p['ndof']
    assert np.all(r['displacements'][np.setdiff1d(np.arange(p['ndof']),r['active_dof_ids'])]==0)
    for mask in ([1,0,1,0,0,0],[1,0,0,0,1,0]):
        r=t.solve_binary(p,np.array(mask,dtype=bool),F,fixed)
        assert r['execution']=='not-run' and r['material_component_count']==2
        assert r['failure_reason']=='disconnected-or-corner-only-material'
        assert np.array_equal(r['occupancy'],mask)
    F[-1]=-1
    assert t.solve_binary(p,occupied,F,fixed)['failure_reason']=='load-on-void-node'


def test_missing_supports_and_infeasible_passive_volume_are_rejected():
    p=problem();F,_=cantilever(p);rho=np.ones(p['nelements'])
    with pytest.raises(t.NumericalFailure,match='rigid-body'):
        t.solve(p,rho,F,np.array([0,1]))
    result=t.solve_binary(p,rho.astype(bool),F,np.array([0,1]))
    assert result['execution']=='not-run' and 'rigid-body' in result['failure_reason']
    with pytest.raises(ValueError,match='passive-solid/filter minimum'):
        t.optimise(p,F,np.array([0,1,3]),rho.astype(bool),.5,.4,10,.01,10.)


def test_explicit_move_budget_initial_volume_and_filter_minimum():
    p=problem();F,fixed=cantilever(p)
    passive=np.zeros(p['nelements'],dtype=bool);passive[::12]=True
    r=t.optimise(p,F,fixed,passive,.55,.4,1,1e-12,10.,move_limit=.07)
    assert np.max(np.abs(r['next_design_variables']-r['design_variables']))<=.07+1e-15
    assert all(np.all(r[key][passive]==1) for key in ('design_variables','densities','next_design_variables'))
    with pytest.raises(ValueError,match='Initial filtered density'):
        t.optimise(p,F,fixed,passive,.55,.4,1,.01,10.,initial_densities=np.ones(p['nelements']))
    P=t.density_filter(p,.4);empty=np.zeros(p['nelements']);empty[passive]=1
    _,rho=t._filtered(p,empty,P,passive)
    with pytest.raises(ValueError,match='passive-solid/filter minimum'):
        t.optimise(p,F,fixed,passive,float(rho.mean()-.01),.4,1,.01,10.)


def test_binary_empty_and_missing_support_nodes_are_retained_without_repair():
    p=problem(3,2);F=np.zeros((p['ndof'],1));fixed=np.array([0,1,3])
    r=t.solve_binary(p,np.zeros(p['nelements'],dtype=bool),F,fixed)
    assert r['failure_reason']=='empty-material-domain'
    occupied=np.array([1,1,1,0,0,0],dtype=bool)
    r=t.solve_binary(p,occupied,F,np.array([0,1,p['ndof']-1]))
    assert r['failure_reason']=='support-on-void-node' and not r['repaired_geometry']
    with pytest.raises(ValueError,match='boolean mask'):
        t.solve_binary(p,occupied.astype(float),F,fixed)


def test_invalid_numeric_inputs_fail_before_factorisation():
    p=problem();F,fixed=cantilever(p)
    with pytest.raises(ValueError,match='minimum stiffness'):
        t.solve(p,np.ones(p['nelements']),F,fixed,min_stiffness_ratio=0.)
    F[0,0]=np.nan
    with pytest.raises(ValueError,match='force matrix'):
        t.solve(p,np.ones(p['nelements']),F,fixed)
    with pytest.raises(ValueError,match='Young modulus'):
        t.q4_stiffness([[0,0],[1,0],[1,1],[0,1]],10**500,.3,.1)


def test_optimizer_snapshots_fixed_loads_and_passive_mask(monkeypatch):
    p=problem();F,fixed=cantilever(p);original_forces=F.copy()
    passive=np.zeros(p['nelements'],dtype=bool);passive[::12]=True
    original=t.filtered_objective
    def mutate_caller_arrays(*args,**kwargs):
        F[:]=0.;passive[:]=True
        return original(*args,**kwargs)
    monkeypatch.setattr(t,'filtered_objective',mutate_caller_arrays)
    result=t.optimise(p,F,fixed,passive,.55,.4,3,1e-5,10.)
    assert not F.any() and passive.all()
    assert result['last_analysis']['objective']>0
    assert np.any(result['densities']<1.)
    replay=t.solve(p,result['densities'],original_forces,fixed)
    assert replay['objective']==pytest.approx(result['last_analysis']['objective'],rel=1e-13)


def test_binary_rejects_local_corner_contact_even_with_global_edge_connected_route():
    p=problem(3,3);F=np.zeros((p['ndof'],1));fixed=np.array([0,1,3])
    # The two diagonal cells in the upper-left block also connect around the
    # bottom/right route. Global connectivity alone would admit a point tie.
    occupied=np.array([[1,1,1],[1,0,1],[0,1,1]],dtype=bool).ravel()
    result=t.solve_binary(p,occupied,F,fixed)
    assert result['material_component_count']==1
    assert result['failure_reason']=='corner-only-contact'
    assert result['execution']=='not-run' and result['repaired_geometry'] is False
    assert result['corner_contact_element_blocks']==[[3,4,6,7]]
    assert np.array_equal(result['occupancy'],occupied)


def edge_average(p,node_ids,direction):
    # Consistent integral of linear shape functions over a straight edge.
    ids=np.asarray(node_ids);xy=p['nodes'][ids]
    order=np.argsort(xy[:,1] if np.ptp(xy[:,1]) else xy[:,0]);ids=ids[order]
    lengths=np.linalg.norm(np.diff(p['nodes'][ids],axis=0),axis=1)
    weights=np.zeros(len(ids));weights[:-1]+=lengths/2;weights[1:]+=lengths/2
    weights/=weights.sum();row=np.zeros(p['ndof']);row[2*ids+direction]=weights
    return row


def axial_average_fixture():
    p=problem(8,4,2.,1.);xy=p['nodes']
    left=np.flatnonzero(xy[:,0]==0);right=np.flatnonzero(xy[:,0]==2)
    C=np.array([edge_average(p,left,0),edge_average(p,left,1),edge_average(p,right,1)])
    F=1000*edge_average(p,right,0)[:,None]
    return p,F,C


def test_finite_average_constraints_reproduce_exact_axial_patch_and_distributed_reactions():
    p,F,C=axial_average_fixture()
    r=t.solve(p,np.ones(p['nelements']),F,[],constraint_matrix=C)
    eps=1000/(200e9*.04)
    expected=np.c_[eps*p['nodes'][:,0],-.3*eps*(p['nodes'][:,1]-.5)].reshape(-1,1)
    np.testing.assert_allclose(r['displacements'],expected,rtol=2e-11,atol=1e-17)
    assert r['compliances'][0]==pytest.approx(1000**2*2/(200e9*.04),rel=1e-12)
    np.testing.assert_allclose(C@r['displacements'],0,atol=1e-17)
    np.testing.assert_allclose(r['constraint_work_J'],0,atol=1e-15)
    np.testing.assert_allclose(r['reactions'][:,0],-1000*C[0],atol=1e-8)
    assert np.count_nonzero(np.abs(r['constraint_reactions'][:,0])>1e-6)>1
    np.testing.assert_allclose(r['reactions'],-C.T@r['constraint_multipliers'],atol=1e-12)
    np.testing.assert_allclose(r['force_equilibrium_residual_N'],0,atol=1e-8)
    np.testing.assert_allclose(r['moment_equilibrium_residual_Nm'],0,atol=1e-8)


def test_point_constraint_rows_match_unchanged_fixed_dof_interface():
    p=problem();F,fixed=cantilever(p,2)
    C=np.eye(p['ndof'])[fixed]
    before=t.solve(p,np.ones(p['nelements']),F,fixed)
    after=t.solve(p,np.ones(p['nelements']),F,[],constraint_matrix=C)
    np.testing.assert_allclose(after['displacements'],before['displacements'],rtol=1e-10,atol=1e-15)
    np.testing.assert_allclose(after['reactions'],before['reactions'],rtol=1e-9,atol=1e-8)


def test_finite_bearing_mean_constraints_match_centered_point_support_beam_control():
    p=problem(80,8,10.,1.);xy=p['nodes'];bottom=np.flatnonzero(xy[:,1]==0)
    left=bottom[xy[bottom,0]<=.25];right=bottom[xy[bottom,0]>=9.75]
    C=np.array([edge_average(p,left,0),edge_average(p,left,1),edge_average(p,right,1)])
    F=np.zeros((p['ndof'],1));F[2*np.argmin(np.linalg.norm(xy-[5.,1.],axis=1))+1]=-1000
    means=t.solve(p,np.ones(p['nelements']),F,[],constraint_matrix=C)
    pin=np.argmin(np.linalg.norm(xy-[.125,0.],axis=1));roller=np.argmin(np.linalg.norm(xy-[9.875,0.],axis=1))
    points=t.solve(p,np.ones(p['nelements']),F,np.array([2*pin,2*pin+1,2*roller+1]))
    assert means['objective']==pytest.approx(points['objective'],rel=.01)
    np.testing.assert_allclose(C@means['displacements'],0,atol=1e-14)
    assert np.count_nonzero(np.abs(means['reactions'][:,0])>1e-5)>3


def test_all_81_rhs_are_solved_linearly_with_energy_and_no_case_dropping():
    p,F,C=axial_average_fixture();factors=np.linspace(-2.,2.,81)
    base=t.solve(p,np.ones(p['nelements']),F,[],constraint_matrix=C)
    actual=t.solve(p,np.ones(p['nelements']),F*factors[None,:],[],constraint_matrix=C)
    binary=t.solve_binary(p,np.ones(p['nelements'],dtype=bool),F*factors[None,:],[],constraint_matrix=C)
    for r in (actual,binary):
        assert r['displacements'].shape==(p['ndof'],81)
        np.testing.assert_allclose(r['displacements'],base['displacements']*factors[None,:],rtol=1e-11,atol=1e-17)
        np.testing.assert_allclose(r['compliances'],base['compliances'][0]*factors**2,rtol=1e-11,atol=1e-17)
        np.testing.assert_allclose(2*r['strain_energy_J'],r['compliances'],rtol=1e-11,atol=1e-17)
        np.testing.assert_allclose(r['constraint_work_J'],0,atol=1e-15)
    with pytest.raises(ValueError,match='1..128'):
        t.solve(p,np.ones(p['nelements']),np.zeros((p['ndof'],129)),[],constraint_matrix=C)


def test_constraint_rigid_rank_dependence_and_binary_void_constraints_fail_explicitly():
    p,F,C=axial_average_fixture()
    with pytest.raises(t.NumericalFailure,match='rigid-body'):
        t.solve(p,np.ones(p['nelements']),F,[],constraint_matrix=C[:2])
    with pytest.raises(t.NumericalFailure,match='Dependent'):
        t.solve(p,np.ones(p['nelements']),F,[],constraint_matrix=np.vstack((C,C[:1])))
    p=problem(3,2);F=np.zeros((p['ndof'],1));mask=np.array([1,1,1,0,0,0],dtype=bool)
    C=np.eye(p['ndof'])[[0,1,p['ndof']-1]]
    r=t.solve_binary(p,mask,F,[],constraint_matrix=C)
    assert r['failure_reason']=='constraint-on-void-node' and r['execution']=='not-run'
    with pytest.raises(ValueError,match='constraint matrix'):
        t.solve(p,mask.astype(float),F,[],constraint_matrix=np.zeros((17,p['ndof'])))


def test_fixed_constraint_filtered_gradient_and_optimizer_interface():
    p,F,C=axial_average_fixture();P=t.density_filter(p,.4)
    passive=np.zeros(p['nelements'],dtype=bool);passive[0]=True
    x=np.linspace(.4,.7,p['nelements'])
    r=t.filtered_objective(p,x,F,[],P,passive,constraint_matrix=C)
    for i in (1,7,15):
        a=x.copy();b=x.copy();a[i]-=1e-6;b[i]+=1e-6
        ra=t.filtered_objective(p,a,F,[],P,passive,constraint_matrix=C)
        rb=t.filtered_objective(p,b,F,[],P,passive,constraint_matrix=C)
        assert r['design_gradient'][i]==pytest.approx((rb['objective']-ra['objective'])/2e-6,rel=1e-5)
    out=t.optimise(p,F,[],passive,.6,.4,3,1e-5,10.,constraint_matrix=C)
    assert out['evaluated_iterations']==3
    replay=t.solve(p,out['densities'],F,[],constraint_matrix=C)
    assert replay['objective']==pytest.approx(out['last_analysis']['objective'],rel=1e-12)


def test_mixed_fixed_and_average_constraints_keep_total_reactions_correct():
    p=problem();F,fixed=cantilever(p,2);C=np.zeros((1,p['ndof']))
    C[0,fixed[-1]]=1.;C[0,fixed[0]]=.5
    baseline=t.solve(p,np.ones(p['nelements']),F,fixed)
    mixed=t.solve(p,np.ones(p['nelements']),F,fixed[:-1],constraint_matrix=C)
    np.testing.assert_allclose(mixed['displacements'],baseline['displacements'],rtol=1e-10,atol=1e-15)
    np.testing.assert_allclose(mixed['reactions'],baseline['reactions'],rtol=1e-9,atol=1e-8)


def test_iteration_callback_gets_independent_last_successful_state(monkeypatch):
    p=problem();F,fixed=cantilever(p);C=np.eye(p['ndof'])[fixed]
    passive=np.zeros(p['nelements'],dtype=bool)
    observed=[]
    def callback(item):
        observed.append(dict(item,design_variables=item['design_variables'].copy(),densities=item['densities'].copy()))
        item['design_variables'][:]=0.;item['densities'][:]=0.;item['objective']=-1
    baseline=t.optimise(p,F,[],passive,.6,.4,3,1e-5,10.,constraint_matrix=C)
    actual=t.optimise(p,F,[],passive,.6,.4,3,1e-5,10.,constraint_matrix=C,iteration_callback=callback)
    assert len(observed)==actual['evaluated_iterations']==3
    np.testing.assert_array_equal(actual['densities'],baseline['densities'])
    np.testing.assert_array_equal(observed[-1]['densities'],actual['densities'])
    assert observed[-1]['objective']==actual['last_analysis']['objective']
    first_success=observed[0]['densities'].copy()
    observed.clear();original=t.filtered_objective;calls=[]
    def fail_second(*args,**kwargs):
        calls.append(1)
        if len(calls)==2:raise t.NumericalFailure('declared later failure')
        return original(*args,**kwargs)
    monkeypatch.setattr(t,'filtered_objective',fail_second)
    with pytest.raises(t.NumericalFailure,match='declared later failure'):
        t.optimise(p,F,[],passive,.6,.4,3,1e-5,10.,constraint_matrix=C,iteration_callback=callback)
    assert len(observed)==1
    np.testing.assert_array_equal(observed[0]['densities'],first_success)
