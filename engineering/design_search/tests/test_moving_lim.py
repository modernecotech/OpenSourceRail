"""Independent manufactured moments and same-candidate moving-circuit guards."""
from copy import deepcopy
from math import pi
import numpy as np
import pytest
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import spsolve
from engineering.design_search import moving_lim as m, railway_bundle, design_grammar, transient_lim


@pytest.fixture(scope='module')
def bundle():return railway_bundle.materialize(design_grammar.initial_candidates()[0])


def test_clipped_linear_triangle_matches_independent_polynomial_integrals():
    vertices=np.array([[0.,0.],[1.,0.],[0.,1.]])
    a,b=.2,.7;area,first,second=m.clipped_moments(vertices,a,b)
    exact_area=(b-a)-(b*b-a*a)/2
    exact_x=(b*b-a*a)/2-(b**3-a**3)/3
    exact_x2=(b**3-a**3)/3-(b**4-a**4)/4
    assert area==pytest.approx(exact_area,abs=1e-14)
    assert first.sum()==pytest.approx(exact_area,abs=1e-14)
    assert first[1]==pytest.approx(exact_x,abs=1e-14)
    assert second[1,1]==pytest.approx(exact_x2,abs=1e-14)
    assert second.sum()==pytest.approx(area,abs=1e-14)
    assert np.linalg.eigvalsh(second).min()>0


def test_translated_finite_plate_has_exact_volume_centroid_and_manufactured_Joule_integral():
    xs=[-1.,4.,8.,12.];ys=[-.0075,0.,.0075]
    points=np.array([(x,y) for x in xs for y in ys]);tri=[]
    for i in range(3):
        for j in range(2):
            a=i*3+j;b=a+3;tri.extend([(a,b,b+1),(a,b+1,a+1)])
    tri=np.array(tri);area,_=transient_lim.geometry(points,tri);previous=None
    for start in (.2,.7):
        q0,q1,q2=m.conductor_moments(points,tri,area,start,9.,.015)
        assert q0.sum()==pytest.approx(9*.015,abs=1e-13)
        centroid=np.einsum('ti,ti->',q1,points[tri][:,:,0])/q0.sum()
        assert centroid==pytest.approx(start+4.5,abs=1e-12)
        # A manufactured linear electric drive, with floating closure removing
        # its mean: exact integral (x-x_center)^2 dx dy = width*length^3/12.
        D=points[tri][:,:,0]-centroid
        assert np.einsum('ti,ti->',q1,D)==pytest.approx(0.,abs=1e-13)
        assert np.einsum('ti,tij,tj->',D,q2,D)==pytest.approx(.015*9**3/12,rel=1e-12)
        assert m.net_secondary_current(20e6,q1,np.ones_like(D))==pytest.approx(-2.7e6,rel=1e-12)
        assert abs(m.net_secondary_current(20e6,q1,D))<1e-6
        if previous is not None:assert not np.array_equal(q2,previous)
        previous=q2


def test_exact_reference_winding_geometry_and_closed_branch_turns(bundle):
    r=m.request(bundle,steps=1);m.validate(r)
    points,tri,regions,boundary,branch,sign=m.mesh(r);area,_=transient_lim.geometry(points,tri)
    assert r['motor_component_id']==bundle['propulsion_component_id']
    assert r['motor_definition']==bundle['motor_definition']
    assert r['physical_geometry']['primary_length_m']==12.5
    assert r['physical_geometry']['secondary_length_m']==9.
    assert area[branch>=0].sum()==pytest.approx(300*.04*.055,rel=1e-10)
    for k in range(30):
        assert area[branch==k].sum()==pytest.approx(10*.04*.055,rel=1e-10)
        assert sum(area[branch==k]*sign[branch==k])==pytest.approx(0.,abs=1e-12)
    assert r['wiring']['actual_connection_verified'] is False
    assert r['actual_converter_loss_W'] is None and not r['repeated_thermal_duty_verified']


@pytest.mark.parametrize('key,value',[('steps',129),('dt_s',.1),('current_limit_A',141.),('voltage_peak_V',376.),
    ('frequency_Hz',0.),('frequency_Hz',1000.),('speed_m_s',21.),('mesh_m',.001),('temperature_C',50.),
    ('start_m',1e6),('available_operating_map',{'invented':True}),('repeated_thermal_duty_verified',True)])
def test_resealing_cannot_expand_declared_resource_or_electrical_domain(bundle,key,value):
    r=m.request(bundle);r[key]=value;r.pop('request_id');r['request_id']=m.identity(r)
    with pytest.raises(ValueError):m.validate(r)


def test_other_motor_or_bundle_cannot_inherit_the_reference_geometry(bundle):
    r=m.request(bundle);r['motor_component_id']='a'*64;r.pop('request_id');r['request_id']=m.identity(r)
    with pytest.raises(ValueError,match='mixed physical bundle'):m.validate(r)
    changed=deepcopy(bundle);changed['mass']['accounted_tare_kg_per_car']+=1
    with pytest.raises(ValueError,match='Modified'):m.request(changed)
    r=m.request(bundle);r['body_candidate_id']='a'*64;r.pop('request_id');r['request_id']=m.identity(r)
    with pytest.raises(ValueError,match='mixed physical bundle'):m.validate(r)


def test_component_output_is_not_an_available_operating_map(bundle):
    from engineering.design_search import system_motion
    r=m.request(bundle)
    case=system_motion.scenario(bundle)
    assert not system_motion.admit_map(bundle,r,case)['admitted']
    assert r['available_operating_map'] is None and not r['physical_accepted']


def test_transport_method_changes_only_evaluation_identity_and_keeps_galerkin_domain_guard(bundle):
    a=m.request(bundle);b=m.request(bundle,transport_method='supg-coth')
    assert a['request_id']!=b['request_id']
    assert a['bundle_id']==b['bundle_id'] and a['motor_component_id']==b['motor_component_id']
    assert a['evaluated_component_definition_id']==b['evaluated_component_definition_id']
    assert a['physical_geometry']==b['physical_geometry']
    m.validate(a);m.validate(b)
    b['transport_method']['source_and_time_terms_weighted']=False
    b.pop('request_id');b['request_id']=m.identity(b)
    with pytest.raises(ValueError,match='transport method differs'):m.validate(b)


def test_highspeed_galerkin_fails_before_allocating_any_field_mesh(bundle,monkeypatch):
    r=m.request(bundle,speed_m_s=20.);bounds=m.estimate(r)
    assert bounds['Peclet_max']>10 and bounds['unstabilized_domain_supported'] is False
    assert bounds['estimated_actual_RAM_bytes'] is None
    def forbidden(*args,**kwargs):pytest.fail('An unsupported Galerkin request allocated its field mesh')
    monkeypatch.setattr(m,'mesh',forbidden)
    with pytest.raises(ValueError,match='Peclet>1'):m.solve(r)


@pytest.mark.parametrize('frequency,dt',[(100.,.01),(50.,.01),(100.,.005)])
def test_time_sampling_cannot_alias_the_phase_supply_to_a_false_DC_limit(bundle,frequency,dt):
    with pytest.raises(ValueError,match='Nyquist sampling'):m.request(bundle,frequency_Hz=frequency,dt_s=dt)
    r=m.request(bundle);r['frequency_Hz']=frequency;r['dt_s']=dt
    r.pop('request_id');r['request_id']=m.identity(r)
    with pytest.raises(ValueError,match='Nyquist sampling'):m.validate(r)


def test_reciprocal_field_circuit_dynamics_converge_to_independent_closed_form_RL():
    # Independent manufactured magnetic circuit: K=1, winding kernels +1/-1,
    # two equal branches and floating neutral imply A=2I and L_branch=2*height.
    # Thus L dI/dt + R I=V, with I(0)=0, has a closed-form exponential response.
    R,V,height,T=3.,5.,.4,1.;errors=[]
    exact=V/R*(1-np.exp(-R*T/(2*height)))
    for steps in (20,40,80):
        dt=T/steps;A=0.;I=0.;energy=0.
        matrix=m.circuit_jacobian(csr_matrix([[1.]]),np.zeros(1),np.zeros(1),1.,
            csr_matrix([[1.,-1.]]),np.full(2,R),dt,height)
        for step in range(steps):
            result=spsolve(matrix,np.array([0.,0.,V+height*A/dt,-V-height*A/dt,0.]))
            newA,u,newI,otherI,neutral=result
            assert otherI==pytest.approx(-newI,abs=1e-12)
            assert newA==pytest.approx(2*newI,abs=1e-12)
            assert u==pytest.approx(0.,abs=1e-12) and neutral==pytest.approx(0.,abs=1e-12)
            stored=.5*height*newA*newA
            algorithmic=.5*height*(newA-A)**2/dt
            residual=2*V*newI-2*R*newI**2-(stored-energy)/dt-algorithmic
            assert abs(residual)<1e-10
            energy=stored;A=newA;I=newI
        errors.append(abs(I-exact))
    assert errors[2]<errors[1]<errors[0]
    assert errors[0]/errors[1]>1.8 and errors[1]/errors[2]>1.8


def test_resealing_unimplemented_wiring_cannot_change_the_solved_topology(bundle):
    r=m.request(bundle);r['wiring']['hypothesis']='all coils in one series path'
    r['wiring_hypothesis_id']=m.identity(r['wiring']);r.pop('request_id');r['request_id']=m.identity(r)
    with pytest.raises(ValueError,match='wiring hypothesis differs'):m.validate(r)


@pytest.mark.parametrize('field',['frequency_Hz','body_candidate_id','wiring','available_operating_map'])
def test_missing_domain_or_identity_field_is_an_explicit_hold(bundle,field):
    r=m.request(bundle);r.pop(field);r.pop('request_id');r['request_id']=m.identity(r)
    with pytest.raises(ValueError,match='schema fields'):m.validate(r)


def test_resealed_manifest_cannot_point_at_a_different_evaluation(bundle,tmp_path,monkeypatch):
    # A declared held-method fixture exercises package identities without a
    # numerical solve or any assertion of available motor performance.
    request=m.request(bundle);source={'fixture-producer':'a'*64}
    monkeypatch.setattr(m,'sources',lambda root=m.ROOT:source)
    data=dict(request=request,source_sha256=source)
    result=dict(execution='held',reason='method fixture',request_id=request['request_id'],
        bundle_id=request['bundle_id'],motor_component_id=request['motor_component_id'],
        source_sha256=source,operating_map_admitted=False,**m.FLAGS)
    result['evaluation_id']=m.identity(result)
    (tmp_path/'input.json').write_bytes(m.encoded(data));(tmp_path/'result.json').write_bytes(m.encoded(result))
    manifest=dict(evaluation_id=result['evaluation_id'],source_sha256=source,
        files_sha256={p.name:m.digest(p) for p in tmp_path.iterdir() if p.is_file()},**m.FLAGS)
    manifest['manifest_id']=m.identity(manifest);(tmp_path/'manifest.json').write_bytes(m.encoded(manifest))
    assert m.verify(tmp_path)['verified']
    manifest['evaluation_id']='b'*64;manifest.pop('manifest_id');manifest['manifest_id']=m.identity(manifest)
    (tmp_path/'manifest.json').write_bytes(m.encoded(manifest))
    with pytest.raises(ValueError,match='manifest/result evaluation identity'):m.verify(tmp_path)
