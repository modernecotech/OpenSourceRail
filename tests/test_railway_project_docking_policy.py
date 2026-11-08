"""Source/policy and scalar checks only; no native journey/CAD/FEM is called."""
from copy import deepcopy
import importlib.util
import os
from pathlib import Path
import sys

import pytest

# A sparse development worktree may use unchanged dependencies from its exact
# coordinator ancestry. A normal full checkout needs no environment variable.
SOURCE_ROOT = Path(os.environ.get('OSR_TEST_SOURCE_ROOT', Path(__file__).resolve().parents[1]))
sys.path.insert(0,str(SOURCE_ROOT))
sys.path.insert(0,str(SOURCE_ROOT/'tests'))
from engineering.station_rail.common import identity
from test_railway_project_frame import context
from test_railway_project_civil import seal

spec = importlib.util.spec_from_file_location('engineering.railway_project.docking_policy',
    Path(__file__).resolve().parents[1]/'engineering/railway_project/docking_policy.py')
docking = importlib.util.module_from_spec(spec)
spec.loader.exec_module(docking)


def proposal(args=None, **kwargs):
    return docking.propose(*(context() if args is None else args),root=SOURCE_ROOT,
        **dict(dict(origin_route_m=-2.,allowed_initial_route_interval_m=[-1.,1.],
            brake_floor_n=40000.,creep_speed_m_s=.2),**kwargs))


def test_geometry_is_new_counted_proposal_not_free_authority_or_a_case():
    args=context();before=deepcopy(args);p=proposal(args)
    assert args==before
    h=p['physical_definition']['design'];g=p['physical_definition']['geometry_changes']
    assert h['platform_modules_per_face']*h['platform_floor_module_length_m']==h['platform_length_m']==130.
    assert h['platform_length_m']+2*h['transition_length_m']==h['reserved_straight_m']==430.
    assert g['platform_floor_delta_m2']==90.  # three sites, two3m-wide faces
    assert (g['terminal_track_delta_m'],g['terminal_rail_delta_m'])==(10.,20.)
    assert p['physical_authority_extension_m']==0
    assert h['accepted_actual_arrival_interval_relative_to_station_m']==[-4.,0.]
    assert p['candidate_id']!=args[2]['candidate_id']
    assert p['candidate_id']==identity(p['physical_definition'])
    assert p['evaluation_id']==identity({k:v for k,v in p.items() if k!='evaluation_id'})
    assert not p['native_export_supported'] and not p['conditional_model_journey_admitted']
    assert not p['physical_accepted'] and not p['operating_release']
    assert 'case' not in p and p['parent_case_id']==args[0]['id']


def test_unknown_finished_envelope_never_borrows_positive_proxy_margin():
    p=docking.end_budget(proxy_half_extent_m=53.875)
    assert p['proxy_only_end_residual_m']==1.625
    assert p['finished_swept_end_residual_m'] is None
    assert p['provisional_geometric_inequality_met'] is None
    assert not p['physical_clearance_verified']
    assert docking.end_budget(finished_swept_half_extent_m=60.,independent_end_budget_m=.5)['finished_swept_end_residual_m']==-4.5


def test_hardware_is_positive_bounded_material_process_cost_and_power_not_zero_or_purchase_price():
    p=proposal();h=p['hardware_allowances']
    assert len(h['bridgeplate_x_about_body_x0_m'])==12
    assert [r['quantity'] for r in h['rows']]==[12,12,12,12,2]
    assert all(0<a<=b<=c for a,b,c in (h['proposed_gross_mass_kg'],h['direct_component_cost_usd'],h['simultaneously_active_peak_power_w']))
    assert not h['installed_BOM_counted'] and not h['installed_mass_or_cost_complete'] and not h['vendor_selected']
    assert len(h['exclusions'])==3
    row=h['rows'][0]
    assert row['mass_kg_each'][1]==pytest.approx(1.4*.35*.012*2700)


def test_vertical_boarding_and_edge_protection_are_typed_open_positive_interfaces():
    p=proposal();b=p['boarding_protection_contract'];edge=b['platform_edge_protection']
    assert b['schema']=='osr-docking-boarding-protection-requirements/1'
    assert b['body_candidate_id']==p['physical_definition']['parent_body_candidate_id']
    assert all(v is None for v in b['vertical_variation_m'].values())
    for k in ('qualified_horizontal_reach_m','qualified_vertical_reach_m','permissible_slope',
              'design_and_proof_load_n','landing_overlap_m','ride_height_detection_and_interlock'):
        assert b['bridgeplate_capability'][k] is None
    assert edge['no_PSD_absence_waiver'] and edge['selected_PSD_or_equivalent_architecture'] is None
    assert edge['control_assemblies']==6 and edge['protected_edge_length_m']==780.
    for k in ('total_reserve_mass_kg','total_reserve_peak_power_w','total_reserve_installed_cost_usd'):
        assert all(v>0 for v in edge[k])
    assert len(b['door_enable_requires'])==5 and len(b['departure_enable_requires'])==4
    assert not b['conditional_boarding_admitted'] and not b['conditional_native_service_admitted']


def test_pricing_revision_changes_evaluation_not_physical_geometry(monkeypatch):
    args=context();a=proposal(args);original=docking.hardware_requirements
    def changed(body):
        p=original(body)
        p['rows'][0]['direct_cost_usd_each']=[v*2 for v in p['rows'][0]['direct_cost_usd_each']]
        p['direct_component_cost_usd']=[v+12*c for v,c in zip(p['direct_component_cost_usd'],original(body)['rows'][0]['direct_cost_usd_each'])]
        return p
    monkeypatch.setattr(docking,'hardware_requirements',changed)
    b=proposal(args)
    assert a['candidate_id']==b['candidate_id'] and a['evaluation_id']!=b['evaluation_id']


@pytest.mark.parametrize('scope,key,value',[
    ('hardware','installed_BOM_counted',True),
    ('hardware','installed_mass_or_cost_complete',True),
    ('hardware','vendor_selected',True),
    ('hardware','vendor_evidence',{'verified':True,'receipt':'synthetic-proof-only'}),
    ('row','qualification',{'test_passed':True,'source_id':'synthetic-control'}),
    ('row','vendor_evidence',{'datasheet_authenticated':True}),
    ('row','source_proof_status','reviewed'),
    ('row','test_resources',{'CPU_s':10.,'mesh_cells':1000}),
    ('design','bridgeplate_load_or_accessibility_qualification',{'passed':True}),
    ('design','vendor_selected',True),
    ('design','measured_performance_added',True),
    ('boarding','boarding_accessibility_verified',True),
    ('edge','reserve_installed_cost_usd_each',[20000.,50000.,120000.])])
def test_metadata_changes_only_evaluation_including_exact_review_counterexample(monkeypatch,scope,key,value):
    args=context();a=proposal(args)
    if scope in ('hardware','row'):
        original=docking.hardware_requirements
        def changed(body):
            h=original(body);target=h['rows'][0] if scope=='row' else h
            target[key]=deepcopy(value);return h
        monkeypatch.setattr(docking,'hardware_requirements',changed)
    elif scope=='design':
        original=docking.hypothesis
        def changed():
            h=original();h[key]=deepcopy(value);return h
        monkeypatch.setattr(docking,'hypothesis',changed)
    else:
        original=docking.boarding_requirements
        def changed(body,station):
            h=original(body,station);target=h['platform_edge_protection'] if scope=='edge' else h
            target[key]=deepcopy(value);return h
        monkeypatch.setattr(docking,'boarding_requirements',changed)
    b=proposal(args)
    assert a['physical_definition']==b['physical_definition']
    assert a['candidate_id']==b['candidate_id'] and a['evaluation_id']!=b['evaluation_id']
    assert not b['native_export_supported'] and not b['conditional_model_journey_admitted']


@pytest.mark.parametrize('scope,key,value',[
    ('row','id','docking/revised-deck-part'),
    ('row','model_id','explicit-selected-model-B'),
    ('row','selected_hardware_id','explicit-hardware-choice-B'),
    ('row','vendor_id','explicit-selected-vendor-B'),
    ('row','stock_size_m',[1.5,.35,.012]),
    ('row','quantity',13),
    ('row','material','steel research plate'),
    ('row','manufacturing_method_id','cast-and-machined-aluminium'),
    ('row','installation',{'bracket_id':'revised-mount','coordinates_m':[1.,2.,3.]}),
    ('row','interfaces',{'bolt_pattern_m':[.1,.2]}),
    ('hardware','mounting_side','changed-body-side'),
    ('hardware','bridgeplate_x_about_body_x0_m',[4.1]),
    ('edge','selected_PSD_or_equivalent_architecture','explicit-selected-edge-design-B'),
    ('boarding','door_enable_requires',['revised-physical-interlock-interface']),
    ('design','platform_length_m',135.),
    ('design','finished_swept_envelope_m',[-54.,54.])])
def test_actual_hardware_geometry_installation_and_interface_choices_change_physical_identity(monkeypatch,scope,key,value):
    args=context();a=proposal(args)
    if scope in ('hardware','row'):
        original=docking.hardware_requirements
        def changed(body):
            h=original(body);target=h['rows'][0] if scope=='row' else h
            target[key]=deepcopy(value);return h
        monkeypatch.setattr(docking,'hardware_requirements',changed)
    elif scope=='design':
        original=docking.hypothesis
        def changed():
            h=original();h[key]=deepcopy(value);return h
        monkeypatch.setattr(docking,'hypothesis',changed)
    else:
        original=docking.boarding_requirements
        def changed(body,station):
            h=original(body,station);target=h['platform_edge_protection'] if scope=='edge' else h
            target[key]=deepcopy(value);return h
        monkeypatch.setattr(docking,'boarding_requirements',changed)
    b=proposal(args)
    assert a['physical_definition']!=b['physical_definition']
    assert a['candidate_id']!=b['candidate_id'] and a['evaluation_id']!=b['evaluation_id']
    assert not b['native_export_supported'] and not b['conditional_model_journey_admitted']


def test_original_sensor_and_redundant_ancestry_replay_guards_are_retained():
    args=list(context());q,m=args[:2]
    q['control']['position_error_bound_m']=.01
    q['id']=identity({k:v for k,v in q.items() if k!='id'})
    m['case_id']=q['id'];m['native_input_id']=identity(q);seal(m)
    with pytest.raises(ValueError,match='Unframed producer contract differs'):proposal(args)
    args=list(context());args[-1]['geometry_binding']=dict(args[-1]['geometry_binding'],body_evaluation_id='f'*64);seal(args[-1])
    with pytest.raises(ValueError,match='separately declared'):proposal(args)
    args=list(context());args[6]['station_candidate_id']='f'*64;seal(args[6])
    args[2]['station_track_evaluation_id']=args[6]['evaluation_id'];seal(args[2])
    args[1]['bundle_evaluation_id']=args[2]['evaluation_id'];seal(args[1])
    with pytest.raises(ValueError,match='Contradictory station-track ancestry'):proposal(args)


def test_no_clipped_entry_or_free_feed_coverage():
    with pytest.raises(ValueError,match='biased observation'):proposal(origin_route_m=-1.25)
    args=list(context());args[-1]['reference_interval_m'][0]=0.;seal(args[-1])
    with pytest.raises(ValueError,match='Coverage omits'):proposal(args)
    with pytest.raises(ValueError,match='berth tolerance'):proposal(allowed_initial_route_interval_m=[-4.,4.])


def control_case(grade):
    """Explicit scalar control from retained P1 admission-plan constants.

    This is no CLI Case/request and cannot be sent to any native evaluator.
    Mass/force are old sizing declarations, not available installed equipment.
    """
    return dict(control=dict(mass_lower_kg=134148.2549373373,mass_upper_kg=175811.5712831871,
        rotating_mass_upper_kg=8102.6373447531,external_mass_upper_kg=0.,
        brake_force_lower_bound_n=70686.8739767186,grade_estimate_fraction=grade,grade_error_bound=.001,
        position_error_bound_m=.25,speed_error_bound_m_s=.1,reaction_time_bound_s=.7,
        brake_rise_time_bound_s=1.3,stopping_margin_m=.5,start_traction_lower_bound_n=47991.70588235294,
        rolling_resistance_upper_n=6896.490182097067,external_resistance_upper_n=0.,
        positive_acceleration_bound_m_s2=2.,end_of_authority_m=1500.),
        dt_s=.05,comfort_jerk_m_s3=.5,headwind_m_s=0.,speed_cap_m_s=55/3.6)


@pytest.mark.parametrize('grade,zero,preload',[(.02,1.2095363112077964,81976.64037314683),
    (-.02,3.156001272435086,45778.047826995324),(0.,1.2511332140434823,13027.698647771094)])
def test_retained_p1_scalar_controls_keep_force_holds_and_show_only_docking_room(grade,zero,preload):
    c=control_case(grade)
    # The least grade-holding floor is itself a finite real brake demand.
    slope=abs(grade)+.001
    floor=c['control']['mass_upper_kg']*docking.G*slope/(1+slope*slope)**.5
    old=docking.necessary_bounds(c,berth_tolerance_m=1.,brake_floor_n=floor,creep_speed_m_s=.2)
    new=docking.necessary_bounds(c,berth_tolerance_m=4.,brake_floor_n=floor,creep_speed_m_s=.2)
    assert old['zero_speed_bound_plus_position_m']==pytest.approx(zero,abs=1e-12)
    assert new['traction_preload_n']==pytest.approx(preload,abs=1e-8)
    assert old['checks']['zero_speed_room'] is False and new['checks']['zero_speed_room'] is True
    assert new['zero_speed_residual_m']==pytest.approx(3.75-zero)
    assert old['traction_preload_n']==new['traction_preload_n']
    if grade==.02:assert 'traction_preload' in new['failed_checks']
    if grade!=0:assert 'full_brake_preload_retention' in new['failed_checks']
    assert new['retained_floor_heat_j_per_m']>0 and not new['conditional_model_journey_admitted']


@pytest.mark.parametrize('bad',[-1.,float('inf'),float('nan'),True])
def test_invalid_floor_and_unknown_finished_limits_refuse(bad):
    with pytest.raises(ValueError):docking.necessary_bounds(control_case(0.),berth_tolerance_m=4.,brake_floor_n=bad,creep_speed_m_s=.2)
    with pytest.raises(ValueError):docking.end_budget(finished_swept_half_extent_m=bad)


def test_no_brake_force_or_adhesion_uplift_to_clear_domain():
    c=control_case(-.02);before=deepcopy(c)
    with pytest.raises(ValueError,match='Floor cannot exceed'):docking.necessary_bounds(c,berth_tolerance_m=4.,brake_floor_n=80000.,creep_speed_m_s=.2)
    with pytest.raises(ValueError,match='creep'):docking.necessary_bounds(c,berth_tolerance_m=4.,brake_floor_n=40000.,creep_speed_m_s=.5)
    c['control']['brake_force_lower_bound_n']=1000.
    r=docking.necessary_bounds(c,berth_tolerance_m=4.,brake_floor_n=900.,creep_speed_m_s=.2)
    assert r['zero_speed_bound_plus_position_m'] is None and not r['checks']['positive_braking']
    assert before['control']['brake_force_lower_bound_n']==70686.8739767186
