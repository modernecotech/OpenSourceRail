from copy import deepcopy
from pathlib import Path
import os
import pytest
from engineering.design_search import wheel_body as w
from engineering.station_rail import vehicle
ROOT=Path(os.environ.get('OSR_EVIDENCE_ROOT',str(vehicle.ROOT)))

def base():return vehicle.build(ROOT)

def test_materialized_children_count_floor_fit_and_derive_mass_without_reusing_body_id():
    b=base();children=[w.materialize(b,p,ROOT) for p in w.initial_parameters()]
    assert len({v['candidate_id'] for v in children})==2
    for v in children:
        assert v['body_candidate_id']!=b['body_candidate_id']
        delta=sum(p['mass_kg'] for p in v['geometry_parts'])-sum(p['mass_kg'] for p in b['geometry_parts'])
        assert v['mass']['accounted_tare_kg_per_car']==pytest.approx(b['mass']['accounted_tare_kg_per_car']+delta)
        assert v['wheel_body']['floor_fit_mass_delta_kg']==pytest.approx(77.15427156)
        assert not v['installed_mass_complete'] and v['mass']['CG_m'] is None
        assert v['support_component_id']==b['support_component_id']
        assert v['seating_layout']==b['seating_layout']
        assert v['physical_definition']['vehicle']==b['physical_definition']['vehicle']
        assert v['physical_definition']['support']==b['physical_definition']['support']
        assert v['physical_definition']['propulsion']==b['physical_definition']['propulsion']
    shell=children[1]
    assert shell['wheel_body']['shell_hardware_mass_kg']>0 and shell['wheel_body']['drilled_material_removed_kg']>0
    assert len(shell['wheel_body']['pads'])==40
    assert any('/nut' in p['id'] for p in shell['geometry_parts'])

def test_failed_generation_revises_physical_sill_stock_and_preserves_passenger_policy():
    p=w.default_parameters();q=w.revise(p,dict(engineering_screen='fail'),1)
    assert q['sill_depth_m']>p['sill_depth_m']
    b=base();a=w.materialize(b,p,ROOT);c=w.materialize(b,q,ROOT)
    assert a['candidate_id']!=c['candidate_id']
    assert c['mass']['accounted_tare_kg_per_car']>a['mass']['accounted_tare_kg_per_car']
    assert w.revise(p,dict(engineering_screen='unknown'),1)==p
    with pytest.raises(ValueError):w.materialize(a,p,ROOT)

def test_candidate_bound_evaluator_rejects_mutation_before_native_execution(tmp_path):
    p=w.default_parameters();v=w.materialize(base(),p,ROOT);v['body_physical_definition']['parameters']['sill_wall_m']=.01
    with pytest.raises(ValueError,match='identity'):w.evaluate(v,p,tmp_path/'bad',root=ROOT)

def test_frame_variant_restores_only_declared_hole_stiffness_upper_bound():
    p=w.initial_parameters()[1];v=w.materialize(base(),p,ROOT);a=w._analysis_variant(v)
    assert len(a['supported_member_indices'])>100
    raw,mesh=w.body_solid_frame.deck(a,v['mass']['accounted_cap_loaded_kg_per_car']-6730,.6)
    assert mesh['element_formulation']=='C3D20 full integration'
    assert 'TYPE=C3D20R' not in raw
    added,m=w._sandwich(raw,a,v,.6)
    assert m['actual_aperture_regions']>100 and m['ideal_fastener_equations']==240
    assert '*ELASTIC,TYPE=ENGINEERING CONSTANTS' in added
    assert m['holes_resolved'] is False


def test_balanced_crossply_extensional_property_and_evaluation_constants_do_not_change_physical_id(monkeypatch):
    q11=25e9/(1-.25*.08);q22=8e9/(1-.25*.08);q12=2e9/(1-.25*.08)
    assert w.SKIN_E==pytest.approx((q11+q22)/2-q12*q12/((q11+q22)/2))
    b=base();p=w.initial_parameters()[1];a=w.materialize(b,p,ROOT)
    monkeypatch.setitem(w.CONSTITUTIVE,'foam_E_Pa',100e6)
    other=w.materialize(b,p,ROOT)
    assert a['candidate_id']==other['candidate_id']


def test_diagnostic_lists_and_failure_reason_keys_do_not_force_spurious_revision():
    p=w.default_parameters()
    assert w.revise(p,[dict(state='unknown',failure_reason=None)],1)==p
    assert w.revise(p,[dict(state='fail')],1)['sill_depth_m']>.35
    assert w.revise(p,[dict(metrics=dict(normal_deflection_m=.04))],1)['sill_depth_m']>.35


def test_body_physical_projection_excludes_other_subsystems_and_evaluation_annotations():
    p=w.initial_parameters()[1];v=w.materialize(base(),p,ROOT)
    actual=w._physical_body_parts(v['geometry_parts'])
    assert actual==v['body_physical_definition']['geometry_parts']
    assert not any(q['id'].startswith(('bogie/','station-secondary/')) for q in actual)
    assert all(not any(k.startswith('analysis_') for k in q) for q in actual)
    changed=deepcopy(v['geometry_parts'])
    next(q for q in changed if q['id']=='station-secondary/active-fin')['size_m'][2]*=1.1
    assert w._physical_body_parts(changed)==actual
