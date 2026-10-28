from pathlib import Path
import json
import numpy as np
import pytest
from engineering.frame_refinement import model as f
from engineering.sourced_case import layered_structure as layer
from engineering.sourced_case import whole_contact as whole
from engineering.component_registry import validate_registry
ROOT=Path(__file__).resolve().parents[3]
from engineering.sourced_case.tests.portable_fixtures import published

@pytest.fixture(scope='module')
def parent():return published('bolstered-v4')
@pytest.fixture(scope='module')
def revised(parent):return f.revision(parent,root=ROOT)


def test_closed_section_independent_integrals_and_bound():
    s=f.section();assert s['area_m2']==pytest.approx(.0056)
    assert 18e6<2*s['EI_vertical_Nm2']<18.5e6
    b=f.necessary_bound(10000,600);assert b['domain_budget_from_this_bound'] and b['conditional_midspan_deflection_m']<.12
    assert b['approved_functional_deflection_limit_m'] is None


def test_actual_protected_envelopes_and_nominal_gauge(parent):
    p=f.preflight(parent);assert p['joining_envelope_outer_y_m']<p['declared_vehicle_half_width_m']
    assert not p['dynamic_gauge_proved'] and not p['door_bogie_suspension_sweeps_proved']
    brake=[r for r in p['close_static_envelopes'] if 'brake-control-and-energy' in r['occurrence_id']]
    assert brake and min(r['static_AABB_separation_m'] for r in brake)==pytest.approx(.01)


def test_counted_new_physical_identity_requirements_mass_and_access(parent,revised):
    validate_registry(revised['registry']);assert revised['candidate_id']!=parent['candidate_id']
    assert revised['registry']['parent_candidate_id']==parent['candidate_id']
    assert revised['requirements']==parent['requirements'] and revised['interfaces']==parent['interfaces']
    a=revised['frame_refinement'];assert 0<a['added_upper_mass_per_car_kg']<800 and a['necessary_bound']['domain_budget_from_this_bound']
    assert len(a['interfaces'])==4 and all(q['counted_M8_bolts']==4 for q in a['interfaces'])
    assert all(revised[k] is False for k in f.FLAGS);layer._vehicle(revised)


def test_new_stock_has_no_hidden_overlap_with_retained_structural_stock(revised):
    rows=layer._rows(revised);new=[r for r in rows if '/frame-' in r['occurrence']['occurrence_id'] and r['part']['geometry']['kind']=='box']
    retained=[r for r in rows if '/frame-' not in r['occurrence']['occurrence_id'] and r['part']['geometry']['kind']=='box' and set(r['part']['functions'])&{'primary-body','bogie-interfaces'}]
    for a in new:
        for b in retained:
            overlap=np.minimum(a['upper'],b['upper'])-np.maximum(a['lower'],b['lower'])
            assert not np.all(overlap>1e-8),(a['occurrence']['occurrence_id'],b['occurrence']['occurrence_id'],overlap)


def test_contact_graph_joint_rank_and_load_conservation(revised):
    model,rows,panels=whole.build(revised,1.5);assert len(model['components'])==1
    assert all(j['rank']==6 for j in model['joint_mechanical_rank'])
    cases,mass=whole.loads(revised,model,rows,panels);F=dict(cases)['crowd160-upper'].reshape(-1,6)
    assert F[:,:3].sum(axis=0)[2]==pytest.approx(-(mass['supported_upper_mass_kg']+160*75)*whole.G)
    assert np.isfinite(F).all()
