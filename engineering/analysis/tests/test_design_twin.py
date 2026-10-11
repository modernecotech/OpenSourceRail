"""Design changes must reach geometry, physical identity, budgets and interfaces."""
from copy import deepcopy
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys
import numpy as np
import pytest

ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT),str(ROOT/'design/component-catalogue/src')]
from engineering.twin_design.compiler import compile_design,validate_research_graph
from engineering.twin_design.physics import precharge,closure_decision,thermal_study,rail_support
from engineering.twin_design.viewer import component_csv,netlist
from osr_mech.automated_geometry import from_source,primitive_volume
from osr_mech.engineering_definition import fingerprint,load_definition,validate


@pytest.fixture(scope='module')
def twin():return compile_design()


def test_design_instances_are_in_the_actual_shared_model_and_catalogue_allocations(twin):
    m=twin['model'];validate(m);r=twin['review']
    assert r['instance_count']==318 and r['added_instance_count']==126 and r['joint_count']==317
    assert r['interface_count']==449 and r['infrastructure_instance_count']==38
    assert r['explicit_reference_allocations']==204 and r['required_allocations']==1367
    assert r['remaining_allocations']==1163 and not r['contact_domain_issue_resolved']
    instances={row['id']:row for row in m['instances']}
    assert all(f['instance_id'] in instances for f in twin['features'])
    assert all(from_source(instances[f['instance_id']]['geometry'])==f['geometry'] for f in twin['features'])
    assert all(len([f for f in twin['features'] if f['instance_id'].startswith(c['id']+'/')])==21 for c in m['family_definition']['cars'])
    assert all(row['representation']=='partial-original-study-decomposition' for row in twin['coverage']['rows'] if row['part_id']=='LM3-TRC-P030')


def test_mass_is_reallocated_once_and_cg_inertia_reach_the_spatial_vehicle(twin):
    r=twin['review'];assert abs(r['mass_reallocation_residual_kg'])<1e-8
    assert abs(r['static_reaction_balance_n'])<1e-6 and r['minimum_static_contact_n']>0
    for row in r['residual_budget']:
        assert row['original_residual_kg']==pytest.approx(row['extracted_explicit_kg']+row['remaining_residual_kg'])
        explicit=sum(f['mass_kg'] for f in twin['features'] if f['instance_id'].startswith(row['car']+'/'))
        assert explicit==pytest.approx(row['extracted_explicit_kg']+row['additional_hvac_mass_kg'])
    assert all(row['cg_change_m'][2]>0 for row in r['carbody_dynamics'])
    assert all(np.linalg.eigvalsh(row['inertia_kg_m2']).min()>0 for row in r['carbody_dynamics'])
    assert all(row['properties']['supplier'] is None and row['properties']['measured'] is None for row in twin['model']['instances'])


def test_changed_sheet_thickness_changes_cad_mass_and_dynamics_without_double_counting(twin):
    inputs=deepcopy(twin['inputs']);inputs['hvac']['carrier_thickness_m']*=1.5
    changed=compile_design(inputs)
    original=next(f for f in twin['features'] if f['instance_id']=='car-1/hvac-carrier')
    revised=next(f for f in changed['features'] if f['instance_id']=='car-1/hvac-carrier')
    assert revised['geometry']!=original['geometry'] and revised['mass_kg']>original['mass_kg']
    assert changed['review']['configuration_sha256']!=twin['review']['configuration_sha256']
    assert changed['review']['total_train_mass_kg']==pytest.approx(twin['review']['total_train_mass_kg'])
    assert changed['review']['carbody_dynamics'][0]['cg_m']!=twin['review']['carbody_dynamics'][0]['cg_m']


def test_doors_are_supplied_from_the_isolated_lv_study_port(twin):
    interfaces={row['id']:row for row in twin['interfaces']['interfaces']}
    door=interfaces['car-1/door-1-1/power']
    assert door['endpoints'][0]['instance']=='car-1/isolated-lv-converter'
    assert door['limits']['voltage_v']==[20.,28.]
    converter=interfaces['car-1/isolated-lv-converter/input']
    assert converter['limits']['voltage_v']==[600.,900.]
    assert interfaces['car-1/battery/dc']['endpoints'][1]['instance']=='car-1/hv-service-panel'
    assert 'not established' in interfaces['car-1/hvac-module-1/power']['model_limits'][-1]


def test_hvac_and_door_candidate_data_do_not_become_supplier_measurements(twin):
    hvac=next(f for f in twin['features'] if f['role']=='replaceable-hvac-module')
    door=next(f for f in twin['features'] if f['role']=='replaceable-door-cassette')
    assert hvac['mass_kg']==pytest.approx(125) and hvac['geometry']['primitives'][0]['dimensions_m']==[1.0,1.6,.22]
    assert 'public nominal' in hvac['property_basis'] and 'assumed equipment' in door['property_basis']
    assert all(f['material_certificate'] is None and not f['production_released'] for f in twin['features'])


def test_folded_door_carrier_has_a_light_material_section_and_real_mount_holes(twin):
    carrier=next(f for f in twin['features'] if f['role']=='surveyed-door-carrier')
    assert carrier['mass_kg']<60
    assert len([p for p in carrier['geometry']['primitives'] if p['id'].startswith('stile')])==6
    header=next(p for p in carrier['geometry']['primitives'] if p['kind']=='plate')
    assert len(header['holes_xy_m'])==4 and header['hole_radius_m']==.0065
    assert all(primitive_volume(p)>0 for p in carrier['geometry']['primitives'])


def test_precharge_charge_and_energy_balance_and_tolerance_corner(twin):
    p=twin['inputs']['electrical']['precharge'];study=twin['studies']['precharge']
    assert study['nominal_ready_time_s']==pytest.approx(-150*.006*math.log(.05))
    assert study['worst_tolerance_ready_time_s']>study['nominal_ready_time_s']
    assert study['required_resistor_pulse_energy_j']==pytest.approx(4009.5)
    assert max(abs(r['energy_residual_j']) for r in study['samples'])<1e-8
    assert not study['pulse_rating_verified']
    assert study['samples'][0]['link_voltage_v']==0
    assert study['samples'][-1]['link_voltage_v']==pytest.approx(twin['battery']['nominal_voltage_v']*.95)
    p=deepcopy(p);p['capacitance_f']*=5
    assert not precharge(p,800)['within_declared_timeout']


@pytest.mark.parametrize('key',['train_stopped','hvil_closed','insulation_ok','main_feedback_open','return_feedback_closed','precharge_feedback_closed'])
def test_each_critical_fault_blocks_the_offline_main_closure_request(twin,key):
    p=twin['inputs']['electrical']['precharge']
    signals=dict(train_stopped=True,hvil_closed=True,insulation_ok=True,main_feedback_open=True,
                 return_feedback_closed=True,precharge_feedback_closed=True,elapsed_s=3.5,link_voltage_ratio=.96)
    assert closure_decision(p,signals)['can_request_main_close']
    signals[key]=False;r=closure_decision(p,signals)
    assert r['critical_lockout'] and not r['can_request_main_close'] and key in r['faults']
    assert not r['physical_control_implemented']


def test_incomplete_timed_out_or_untyped_precharge_observations_are_rejected(twin):
    p=twin['inputs']['electrical']['precharge']
    with pytest.raises(ValueError):closure_decision(p,{})
    signals=dict(train_stopped=1,hvil_closed=True,insulation_ok=True,main_feedback_open=True,
                 return_feedback_closed=True,precharge_feedback_closed=True,elapsed_s=3.5,link_voltage_ratio=.96)
    with pytest.raises(ValueError,match='booleans'):closure_decision(p,signals)
    signals['train_stopped']=True;signals['elapsed_s']=6.
    assert closure_decision(p,signals)['critical_lockout']
    signals['elapsed_s']=3.;signals['link_voltage_ratio']=.5
    assert not closure_decision(p,signals)['can_request_main_close']


def test_one_module_out_failure_is_retained_and_energy_balance_is_independent(twin):
    nominal=twin['studies']['hvac_nominal'];failed=twin['studies']['hvac_three_module_baseline_one_out']
    assert nominal['within_declared_study_limit'] and not failed['within_declared_study_limit']
    assert twin['studies']['hvac_one_module_out']['within_declared_study_limit']
    assert twin['review']['additional_study_train_mass_kg']==750
    assert nominal['final_temperature_c']==26 and failed['final_temperature_c']==pytest.approx(29.1658,abs=1e-4)
    assert failed['maximum_energy_residual_j']<1e-6 and not failed['physical_validation']
    p=deepcopy(twin['inputs']['hvac']['thermal_assumptions']);p['step_s']=5.
    refined=thermal_study(p,2,8000.)
    assert refined['final_temperature_c']==pytest.approx(failed['final_temperature_c'],abs=1e-9)


def test_rail_seats_keep_pads_insulators_anchors_gauge_and_bearing_replaceability(twin):
    infra=twin['infrastructure'];assert infra['measured_surrogate_gauge_m']==pytest.approx(1.435)
    seats=[r for r in infra['items'] if r['role']=='replaceable-fastening-study'];assert len(seats)==20
    ids={p['id'] for p in seats[0]['geometry']['primitives']}
    assert {'under-pad','baseplate','rail-pad','toe-insulator--1','toe-insulator-1','isolator-1'}<=ids
    assert len([id for id in ids if id.startswith('anchor-')])==4
    assert infra['support_study']['series_stiffness_n_m']==pytest.approx(30e6)
    assert twin['model']['bridge']['track']['pad_stiffness_n_m']==pytest.approx(100e6)
    assert twin['review']['track_support_mapping']['two_rail_foundation_modulus_n_m2']==pytest.approx(100e6)
    assert not infra['support_study']['fastening_qualified'] and not infra['support_study']['electrical_insulation_verified']
    assert {r['details']['mode'] for r in infra['items'] if r['role']=='replaceable-bearing-interface'}=={'fixed','guided-x','guided-y','free'}
    assert len([r for r in infra['items'] if r['role']=='jacking-pad-reservation'])==8
    assert infra['thermal_movement_study']['approved_movement_capacity_m'] is None


def test_anchor_edge_and_pad_stiffness_failures_cannot_be_hidden(twin):
    p=deepcopy(twin['inputs']['infrastructure']);p['minimum_edge_distance_ratio']=4.
    assert not rail_support(p)['within_declared_edge_policy']
    p['rail_pad_stiffness_n_m']=0
    with pytest.raises(ValueError):rail_support(p)


def test_research_recursion_has_real_publisher_links_and_cannot_be_cyclic():
    graph=load_definition(ROOT/'engineering/twin_design/data/research-graph.json')
    sources=load_definition(ROOT/'engineering/best_practice/data/sources.json');r=validate_research_graph(graph,sources)
    assert r==dict(reviewed_nodes=31,followed_publisher_links=12,maximum_observed_depth=2)
    changed=deepcopy(graph);changed['edges'].append(dict(parent='liebherr-macs-data',child='liebherr-modules'))
    with pytest.raises(ValueError,match='cycle'):validate_research_graph(changed,sources)
    changed=deepcopy(graph);changed['nodes'][0]['url']='https://unreviewed.example/'
    with pytest.raises(ValueError,match='identity'):validate_research_graph(changed,sources)


def test_open_circuit_and_bom_link_to_the_configuration_and_preserve_missing_ratings(twin):
    circuit=netlist(twin);assert circuit['configuration_sha256']==fingerprint(twin['model'])
    parts={p['id']:p for p in circuit['components']}
    assert parts['KPRE']['nodes']==['FUSED+','PRE+'] and parts['RPRE']['nodes']==['PRE+','DC+']
    assert all(p['qualified_rating'] is None for p in parts.values())
    assert not circuit['bleeder_discharge_time_verified'] and not circuit['production_released']
    assert 'public nominal candidate' in component_csv(twin)


def test_published_twin_and_native_artifacts_are_bound_to_the_design(twin):
    path=ROOT/'tools/automation/design-best-practice-twin.py'
    spec=importlib.util.spec_from_file_location('design_cli',path);cli=importlib.util.module_from_spec(spec);spec.loader.exec_module(cli)
    cli.check_public(twin)
    folder=cli.PUBLIC;native=load_definition(folder/'reference-twin.native.json')
    assert native['configuration_sha256']==fingerprint(twin['model'])
    assert native['native_train_instance_count']==318 and native['new_train_design_instance_count']==126
    assert native['infrastructure_instance_count']==38
    assert native['native_solver_result']=='0' and native['reopened_solver_result']==0
    assert native['new_car_component_collisions']==native['intra_component_collisions']==[]
    assert native['maximum_relative_primitive_inertia_error']<1e-8
    assert native['step_roundtrip_relative_volume_error']<1e-8
    assert native['generator_sha256']==hashlib.sha256((ROOT/'tools/automation/design-twin-freecad.py').read_bytes()).hexdigest()
    assert native['fcstd_sha256']==hashlib.sha256((folder/'reference-twin.FCStd').read_bytes()).hexdigest()
    assert native['step_sha256']==hashlib.sha256((folder/'reference-twin.step').read_bytes()).hexdigest()
    assert not native['context_body_fit_qualified'] and not native['drawing_issued'] and not native['physical_validation']
    execution=load_definition(folder/'execution.json')
    assert execution['published_twin_sha256']==hashlib.sha256((folder/'reference-twin.json').read_bytes()).hexdigest()
    assert execution['published_review_sha256']==hashlib.sha256((folder/'review.json').read_bytes()).hexdigest()
    assert execution['producer_sha256']==hashlib.sha256((ROOT/'tools/automation/publish-design-twin-evidence.py').read_bytes()).hexdigest()
    for name,digest in execution['artifact_sha256'].items():
        assert digest==hashlib.sha256((folder/name).read_bytes()).hexdigest()
    smoke=load_definition(folder/'spatial-smoke.json')
    assert smoke['hardware_definition_sha256']==fingerprint(twin['model']) and smoke['steps']==4
    assert smoke['within_adapter_domain'] and not smoke['complete_passage_qualified']
    assert smoke['producer_sha256']==hashlib.sha256((ROOT/'tools/automation/design-twin-smoke.py').read_bytes()).hexdigest()
