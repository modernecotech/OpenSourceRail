from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path

import numpy as np
import pytest

from engineering.trip_dynamics import flexible_body as f
from engineering.trip_dynamics.vehicle import identity


def signed(model):
    model['model_id'] = identity({k:v for k,v in model.items() if k!='model_id'})
    return model


@pytest.fixture
def exchange():
    # Independent four-point-mass mathematical fixture. Exactly4kg and8I
    # centroid inertia; deliberately unrelated to any actual body publication.
    xyz = [[1.,1.,1.],[1.,-1.,-1.],[-1.,1.,-1.],[-1.,-1.,1.]]
    ids = dict(candidate_id='1'*64, geometry_id='2'*64, material_id='3'*64)
    context = dict(boundary_case_id='synthetic-springs',equilibrium_id='4'*64,
                   external_load_id='5'*64,attachments={'centre':[0.,0.,0.]})
    vehicle = dict(**ids,scope='benchmark-coupon',complete_equipped_vehicle=True,
        unknown_installed_inventory=[],equipped_properties={'empty':dict(
            mass_kg_per_car=4.,cg_m=[0.,0.,0.],inertia_kg_m2=(8*np.eye(3)).tolist())},
        structural_context={'empty':context})
    scenario = dict(scenario_id=ids['candidate_id'],load_case='empty',cars=1,
                    car_length_m=2.,temperature_C=20.,mode='benchmark')
    K = np.diag((2*np.pi*np.arange(1,13))**2)
    model = dict(schema='osr-reduced-flexible-body/1', **ids,
        units=deepcopy(f.UNITS), scope='benchmark-coupon',mode_count=3,
        applicability=dict(cars=1,car_length_m=2.,load_case='empty',temperature_range_C=[20.,50.]),
        equilibrium={k:context[k]for k in ('boundary_case_id','equilibrium_id','external_load_id')},
        nodes=[dict(id='n'+str(i),xyz_m=x)for i,x in enumerate(xyz)],
        physical_mass_matrix_kg=np.eye(12).tolist(),physical_stiffness_matrix_N_m=K.tolist(),
        shapes_dof_by_mode=np.eye(12)[:,:3].tolist(),modal_stiffness_s2=K[:3,:3].tolist(),
        modal_damping_s1=np.diag([.1,.2,.3]).tolist(),frequencies_hz=[1.,2.,3.],
        attachments=[dict(id='centre',position_m=[0.,0.,0.],node_weights=[
            dict(node_id='n'+str(i),weight=.25)for i in range(4)])],
        source_sha256={'mesh.txt':sha256(b'synthetic four point masses\n').hexdigest()},
        configuration_adopted=False,physical_accepted=False,engineering_accepted=False)
    model['equilibrium'].update(prestress_included=True,residual_force_N=0.)
    return signed(model),vehicle,scenario


def test_equipped_rigid_mass_congruence_and_attachment_virtual_work(exchange):
    model,vehicle,scenario=exchange
    valid=f.validate_modal_model(model,vehicle,scenario)
    H=f.attachment_operator(valid,'centre')
    np.testing.assert_allclose(H,.25*np.eye(3))
    q=np.array([.2,-.4,.3]);F=np.array([5.,6.,-4.])
    assert F@(H@q)==pytest.approx((H.T@F)@q)
    assert '_numerically_validated' not in model


@pytest.mark.parametrize('key', ['candidate_id','geometry_id','material_id'])
def test_reidentified_foreign_model_refused(exchange,key):
    model,vehicle,scenario=exchange
    model[key]='f'*64
    with pytest.raises(ValueError,match=key):f.validate_modal_model(signed(model),vehicle,scenario)


@pytest.mark.parametrize('change,reason', [
    ('normalisation','mass normalisation'), ('inertia','rigid mass'),
    ('negative-mass','mass eigenvalue'), ('asymmetric','mass symmetry'),
    ('eigen','full eigen residual'), ('frequency','frequency/stiffness'),
    ('damping','damping eigenvalue'), ('units','SI units'),
    ('attachment','interpolated attachment'),('weights','partition-of-unity'),
    ('temperature','temperature applicability'),('load','load_case'),
    ('boundary','boundary_case_id'),('prestress','prestress'),('residual','residual')])
def test_semantic_corruption_even_after_rehash_refuses(exchange,change,reason):
    model,vehicle,scenario=exchange
    if change=='normalisation':model['shapes_dof_by_mode'][0][0]=2.
    if change=='inertia':vehicle['equipped_properties']['empty']['inertia_kg_m2'][0][0]=7.
    if change=='negative-mass':model['physical_mass_matrix_kg'][0][0]=-1.
    if change=='asymmetric':model['physical_mass_matrix_kg'][0][1]=.2
    if change=='eigen':
        # Projection still agrees, but an omitted DOF couples to a retained
        # vector: only a full eigen residual exposes this bad exchange.
        model['physical_stiffness_matrix_N_m'][0][3]=1.
        model['physical_stiffness_matrix_N_m'][3][0]=1.
    if change=='frequency':model['frequencies_hz'][0]=1.1
    if change=='damping':model['modal_damping_s1'][0][0]=-.1
    if change=='units':model['units']['position']='mm'
    if change=='attachment':model['attachments'][0]['position_m'][0]=.1
    if change=='weights':model['attachments'][0]['node_weights'][0]['weight']=.5
    if change=='temperature':scenario['temperature_C']=51.
    if change=='load':scenario['load_case']='AW3'
    if change=='boundary':model['equilibrium']['boundary_case_id']='unrelated'
    if change=='prestress':model['equilibrium']['prestress_included']=False
    if change=='residual':model['equilibrium']['residual_force_N']=1.
    with pytest.raises(ValueError,match=reason):f.validate_modal_model(signed(model),vehicle,scenario)


def test_comparison_inertia_and_coupon_cannot_qualify_actual_vehicle(exchange):
    model,vehicle,scenario=exchange
    vehicle['complete_equipped_vehicle']=False
    vehicle['equipped_properties']={}
    vehicle['comparison_empty_kg_per_car']=4.
    vehicle['cg_m']=[0.,0.,0.]
    vehicle['inertia_kg_m2']=(8*np.eye(3)).tolist()
    with pytest.raises(ValueError,match='equipped'):f.validate_modal_model(model,vehicle,scenario)
    vehicle['complete_equipped_vehicle']=True
    scenario['mode']='evidence'
    with pytest.raises(ValueError,match='benchmark'):f.validate_modal_model(model,vehicle,scenario)


def test_unknown_installed_hardware_refuses_even_with_numeric_inertia(exchange):
    model,vehicle,scenario=exchange
    vehicle['unknown_installed_inventory']=['unweighed cooling package']
    with pytest.raises(ValueError,match='equipped'):f.validate_modal_model(model,vehicle,scenario)


def test_wrong_equipped_cg_refused_by_rigid_cross_terms(exchange):
    model,vehicle,scenario=exchange
    vehicle['equipped_properties']['empty']['cg_m']=[.1,0.,0.]
    with pytest.raises(ValueError,match='rigid mass/CG/inertia'):
        f.validate_modal_model(model,vehicle,scenario)


def test_source_mutation_and_unhashed_model_mutation_refuse(tmp_path,exchange):
    model,vehicle,scenario=exchange
    (tmp_path/'mesh.txt').write_bytes(b'synthetic four point masses\n')
    path=tmp_path/'model.json'
    path.write_text(json.dumps(model))
    assert f.load_modal(path,vehicle,scenario)['_numerically_validated']
    (tmp_path/'mesh.txt').write_bytes(b'changed mesh\n')
    with pytest.raises(ValueError,match='digest changed'):f.load_modal(path,vehicle,scenario)
    model['frequencies_hz'][0]=100.
    with pytest.raises(ValueError,match='content identity'):f.validate_modal_model(model,vehicle,scenario)


def test_unvalidated_or_unknown_attachment_refuses(exchange):
    model,vehicle,scenario=exchange
    with pytest.raises(ValueError,match='validate'):f.attachment_operator(model,'centre')
    model=f.validate_modal_model(model,vehicle,scenario)
    with pytest.raises(ValueError,match='unknown attachment'):f.attachment_operator(model,'absent')


def test_executed_laminate_fixture_against_independent_cantilever_formula():
    v=f.laminate_benchmark(24)
    assert v['material_mass_kg']==pytest.approx(.76)
    assert np.max(np.abs(v['B_N']))<1e-10 # symmetric laminate
    # Independent ply lever-arm integral, not a retained output constant.
    Q0=25e9/(1-.25**2*8/25)
    Q90=8e9/(1-.25**2*8/25)
    D11=2/3*(Q0*(.002**3-.001**3)+Q90*.001**3)
    EI=.1*D11
    assert v['EI_N_m2']==pytest.approx(EI)
    assert v['tip_deflection_FE_m']==pytest.approx(.1/(3*EI),rel=1e-8)
    assert v['frequencies_FE_hz'][0]==pytest.approx(v['first_frequency_analytical_hz'],rel=1e-6)
    coarse=f.laminate_benchmark(4)
    assert abs(v['frequencies_FE_hz'][0]-v['first_frequency_analytical_hz']) < abs(coarse['frequencies_FE_hz'][0]-coarse['first_frequency_analytical_hz'])
    assert v['executed'] and not v['code_aster_executed']
    assert not v['engineering_accepted']


def test_retained_coupon_receipt_and_template_honest_scope():
    folder=Path(f.__file__).parent/'fixtures/structures'
    v=json.loads((folder/'analytical-laminate.json').read_text())
    assert sha256(Path(f.__file__).read_bytes()).hexdigest()==v['source_sha256']['engineering/trip_dynamics/flexible_body.py']
    assert v['scope']=='benchmark-coupon' and not v['code_aster_executed']
    mesh=(folder/'laminate.mail').read_text().splitlines()
    assert sum(x.startswith('M')for x in mesh)==160
    assert sum(x.startswith('N') and len(x.split())==4 for x in mesh)==105
    assert 'P time_limit 300' in (folder/'laminate.export').read_text()
    assert not json.loads((folder/'tool-availability.json').read_text())['executed_code_aster']
