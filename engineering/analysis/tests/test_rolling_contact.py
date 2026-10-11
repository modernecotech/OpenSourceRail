"""Renewal, frame transport, derivative and finite-domain contact checks."""
from pathlib import Path
import sys
import numpy as np
import pytest
ROOT=Path(__file__).resolve().parents[3];sys.path[:0]=[str(ROOT),str(ROOT/'design/component-catalogue/src')]
from engineering.civil_exploration.wheel_contact import TangentialContact,ProfilePair
from engineering.civil_exploration.spatial_vehicle import rolling_reference_velocity


def test_convected_brush_has_bounded_steady_force_and_exact_discrete_energy_balance():
    state=TangentialContact();B=np.array([[1.,0.],[0.,1.],[0.,0.]])
    for _ in range(100):
        r=state.rolling_trial([.01,.002],.005,40000.,1e7,.3,.001,B)
        assert abs(r['energy_residual_j'])<1e-10 and r['dissipation_j']>=0
        state.commit(r)
    assert r['force_n']==pytest.approx([-100.,-20.])
    assert np.linalg.norm(r['force_n'])<.3*40000.


def test_coulomb_return_and_frame_transport_remain_passive():
    state=TangentialContact(displacement=np.array([.02,.01]));B=np.array([[1.,0.],[0.,1.],[0.,0.]])
    r=state.rolling_trial([10.,2.],.005,40000.,1e7,.1,.001,B)
    assert np.linalg.norm(r['force_n'])==pytest.approx(4000.) and abs(r['energy_residual_j'])<1e-8
    state.commit(r);rotation=np.array([[0.,1.],[-1.,0.],[0.,0.]])
    rotated=state.rolling_trial([0.,0.],.005,40000.,1e7,.1,.001,rotation)
    assert abs(rotated['energy_residual_j'])<1e-8 and rotated['dissipation_j']>=0
    opened=state.rolling_trial([0.,0.],.005,0.,1e7,.1,.001,B)
    assert opened['stored_energy_j']==0 and opened['dissipation_j']>0


def test_rolling_velocity_tangent_matches_independent_finite_difference():
    state=TangentialContact();B=np.array([[1.,0.],[0.,1.],[0.,0.]])
    args=[.005,40000.,1e7,.3,.001,B];r=state.rolling_trial([.01,.002],*args);h=1e-7
    jac=np.column_stack([-(state.rolling_trial(np.array([.01,.002])+np.eye(2)[i]*h,*args)['force_n']-r['force_n'])/h for i in range(2)])
    assert jac==pytest.approx(r['restoring_tangent_n_m']*args[0],rel=1e-8)


def test_exact_quadratic_location_preserves_the_supplied_finite_profile_domain():
    y=np.linspace(-.06,.06,13);pair=ProfilePair([[v,.01*v+v*v/4] for v in y],[[v,-v*v/.6] for v in y],.38,115e9)
    result=pair.locate(.002,.001)
    expected=(.5*.002-.001-.01)/(.5+2/.6)
    assert result['contact_y_m']==pytest.approx(expected,abs=1e-12)
    with pytest.raises(ValueError):pair.locate(.3)


def test_yaw_steering_matches_independent_finite_rotation_and_spin_is_excluded():
    from scipy.spatial.transform import Rotation
    speed=15.;yaw=1e-5
    velocity,D=rolling_reference_velocity(speed,.38,.38,np.eye(3),[0.,100.,yaw])
    exact=Rotation.from_rotvec([0.,0.,yaw]).apply([-speed,0.,0.])
    assert velocity==pytest.approx(exact,abs=1e-9)
    assert velocity[1]==pytest.approx(-speed*yaw)
    assert np.linalg.norm(D[:,1])==0
    for i in (0,2):
        h=1e-7;plus=rolling_reference_velocity(speed,.38,.38,np.eye(3),np.eye(3)[i]*h)[0]
        base=rolling_reference_velocity(speed,.38,.38,np.eye(3),[0.,0.,0.])[0]
        assert (plus-base)/h==pytest.approx(D[:,i],abs=1e-8)
