"""Cross-module conservation and accounting contracts for the closure packet."""
from copy import deepcopy
from math import fsum
import pytest
from engineering.railway_closure.electrical import controlled_thermal
from engineering.railway_closure.installed import integrate, axle_packet
from engineering.railway_closure.motion import case
from engineering.railway_closure import ROOT
from engineering.vehicle_installation.model import build
from engineering.station_rail.common import identity


@pytest.fixture(scope='module')
def body():return build(ROOT)


@pytest.fixture(scope='module')
def installed(body):return integrate(body)


def test_explicit_drive_additions_and_static_reactions(body,installed):
    source={r['name']:r for r in body['mass_scenarios']}
    for row in installed['load_cases']:
        c=row['name'].split('-')[-1]
        additions=dict(low=12352.,base=14152.,high=18752.)[c]
        assert row['train_mass_kg']-source[row['name']]['train_mass_kg']==pytest.approx(additions)
        assert abs(row['force_residual_N'])<1e-7
        assert abs(row['moment_residual_Nm'])<1e-6
    assert installed['candidate_id']!=body['candidate_id']
    assert installed['physical_accepted'] is False
    assert installed['packaging_screen'].startswith('hold:')


def test_body_edit_cannot_reuse_mass_evidence(body):
    bad=deepcopy(body);bad['candidate_id']='0'*64
    with pytest.raises(ValueError,match='physical body'):integrate(bad)


def test_new_mass_controller_and_driven_adhesion_are_same_candidate(installed):
    q=case(installed)
    r=next(r for r in installed['load_cases'] if r['name']=='normal-base')
    assert q['candidate_id']==installed['candidate_id']
    assert q['mass_kg']==r['train_mass_kg']
    assert q['control']['mass_lower_kg']<q['mass_kg']<q['control']['mass_upper_kg']
    assert q['drive']['contact_force_cap_n']==pytest.approx(.12*r['driven_static_axle_force_N'])
    assert q['control']['end_of_authority_m']==1500.
    p=axle_packet(installed)
    assert p['mass_evaluation_id']==installed['evaluation_id']
    assert p['evaluation_id']==identity({k:v for k,v in p.items() if k!='evaluation_id'})


def test_cooler_modulates_instead_of_overcooling():
    r=controlled_thermal([dict(duration_s=36000.,heat_W=100.)],initial_C=35.,ambient_C=50.,
                         capacity_J_K=100000.,conductance_W_K=10.,cooling_capacity_W=3000.,target_C=35.)
    assert r['final_C']==35.
    assert r['active_cooling_heat_J']==pytest.approx(250*36000.)
    assert abs(r['balance_residual_J'])<1e-5


def test_thermostat_crossings_and_insufficient_capacity():
    kw=dict(ambient_C=50.,capacity_J_K=100000.,conductance_W_K=10.,cooling_capacity_W=1000.,target_C=35.)
    for initial in (30.,40.):
        r=controlled_thermal([dict(duration_s=100000.,heat_W=50.)],initial_C=initial,**kw)
        assert r['final_C']==pytest.approx(35.)
        assert abs(r['balance_residual_J'])<1e-5
    r=controlled_thermal([dict(duration_s=10000.,heat_W=5000.)],initial_C=35.,**kw)
    assert r['final_C']>35.
    assert abs(r['balance_residual_J'])<1e-5
