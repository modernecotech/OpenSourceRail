"""Independent electrical, humid-air and assembly negative controls for WP04-06."""
from copy import deepcopy
from math import exp,pi

import pytest

from engineering.assembly_design import baseline,models,cassette_system as c
from engineering.twin_workflow import core


@pytest.fixture
def pair():
    p=core.read(baseline.DATA)
    variables={key:domain[0] for key,domain in p['pilots']['service-cassette']['domains'].items()}
    return p,models.build(p,'service-cassette',variables)


def test_nominal_awg_matches_independent_published_geometric_size():
    # Standard rounded diameters, independently frozen rather than copied formula.
    assert c.awg_area(14)==pytest.approx(2.081e-6,rel=.001)
    assert c.awg_area(12)==pytest.approx(3.309e-6,rel=.001)
    with pytest.raises(ValueError):c.awg_area(14.)


def test_model_corrects_solder_wire_size_and_eight_live_two_spare(pair):
    _,candidate=pair;net=candidate['metadata']['netlist']
    assert net['reference_wire_awg']==14 and net['reference_conductor_area_m2']==pytest.approx(c.awg_area(14))
    assert net['active_pins']==list(range(1,9)) and net['reserved_pins']==[9,10]
    assert net['termination_process']=='solder; not crimp'
    copper=next(p for p in candidate['contract']['parts'] if p['id']=='wire-0-conductor')
    assert copper['properties']['mass_kg']==pytest.approx(c.awg_area(14)*.8*8960.)


def test_both_mating_kits_and_included_contacts_no_double_purchase(pair):
    p,candidate=pair;h=c.harness(candidate['revision'])
    assert {row['part'] for row in h['bom'] if 'includes' in row}=={c.FEMALE,c.MALE}
    assert len(h['pins'])==10 and len(h['wires'])==16
    assert sum(w['awg']==14 for w in h['wires'])==8 and sum(w['awg']==12 for w in h['wires'])==8
    assert all(w['minimum_strip_length_m']==.005 and 'solder' in w['connector_termination'] for w in h['wires'])
    assert all(w['pin']<9 for w in h['wires'])
    assert sum(e['quantity'] for row in h['bom'] if 'includes' in row for e in row['includes'] if e['part'].startswith('M80-'))==20
    assert next(row for row in h['bom'] if row['id']=='unused-contact-control')['procurement_quantity']==0
    assert not h['complete_manufacturing_harness']


def test_source_documents_bound_to_exact_versions_and_parts():
    assert len(c.SOURCE_CARDS)==5
    assert any(s['exact_part']==c.MALE for s in c.SOURCE_CARDS)
    assert all(len(s['document_sha256'])==64 and set(s['document_sha256'])<=set('0123456789abcdef') for s in c.SOURCE_CARDS)
    assert all(s['publisher']=='Harwin' and s['retrieved']=='2026-10-19' and not s['approved'] for s in c.SOURCE_CARDS)
    assert any(s['revision']=='IS-52 issue 2, 2023-02-01' for s in c.SOURCE_CARDS)


@pytest.mark.parametrize('voltage',(18.,24.,30.))
@pytest.mark.parametrize('temperature',(50.,60.))
def test_independent_kirchhoff_and_thermal_power_controls(voltage,temperature):
    r=c.electrical_case(voltage_v=voltage,ambient_c=temperature)
    # Independently rounded cable areas give an independent engineering control.
    rho=1.724e-8*(1+.00393*(temperature-20))
    rw=2*rho*(.8/2.081e-6+1./3.309e-6)
    expected=voltage/(4.8+.05+.012+.004+rw)
    assert r['current_a']==pytest.approx(expected,rel=1e-5)
    assert r['load_voltage_v']==pytest.approx(expected*4.8,rel=1e-5)
    assert r['power_w']['source']==pytest.approx(sum(v for k,v in r['power_w'].items() if k!='source'))
    assert r['power_balance_residual_w']==pytest.approx(0,abs=1e-10)
    assert r['contact_temperature_hypothesis_c']>temperature
    assert r['checks']['simultaneous_derating'] is None
    assert r['checks']['protective_device_coordination'] is None


def test_voltage_temperature_and_length_sensitivity():
    base=c.electrical_case();hot=c.electrical_case(ambient_c=60.);long=c.electrical_case(female_length_m=1.6)
    assert hot['external_loop_resistance_ohm']>base['external_loop_resistance_ohm']
    assert hot['current_a']<base['current_a'] and long['current_a']<base['current_a']
    assert c.electrical_case(voltage_v=30.)['power_w']['load']>base['power_w']['load']


@pytest.mark.parametrize('fault',('open-supply','open-return','open-bond','short','reversed','mis-mate','unlock'))
def test_fault_injections_retain_risk_and_ideal_inhibit_scope(fault):
    r=c.electrical_case(fault=fault)
    assert r['current_a']==0 and not r['permission'] and r['known_fault_detected']
    assert r['checks']['physical_fault_detection'] is None
    assert all(value==0 for value in r['power_w'].values())
    if fault=='short':assert r['prospective_pretrip_current_a']>200
    if fault=='reversed':assert r['prospective_pretrip_current_a']<0
    if fault in {'open-supply','open-return'}:assert r['prospective_pretrip_current_a']==0


def test_contact_graph_detects_actual_opens_crosses_shorts_and_reverse():
    faults=c.connectivity_faults()
    assert faults['nominal']['passed']
    assert all(not state['passed'] for name,state in faults.items() if name!='nominal')
    assert faults['open']['open_or_misrouted_active_pins']==[1]
    assert [1,2] in faults['short']['unintended_cross_connections']
    assert [1,2] in faults['reversed']['unintended_cross_connections']
    with pytest.raises(ValueError):c.continuity_observation({1:11})


def test_rc_energy_against_independent_infinite_time_limit_and_initial_condition():
    start=c.precharge(time_s=0.);finish=c.precharge(time_s=20.)
    assert start['capacitor_voltage_v']==0 and start['current_a']==pytest.approx(2.4)
    assert finish['capacitor_energy_j']==pytest.approx(.5*.0047*24**2)
    assert finish['resistor_heat_j']==pytest.approx(.5*.0047*24**2)
    for t in (.001,.02,.1,1.):
        r=c.precharge(time_s=t)
        assert abs(r['energy_balance_residual_j'])<1e-12
        assert r['capacitor_voltage_v']==pytest.approx(24*(1-exp(-t/(10*.0047))))


@pytest.mark.parametrize('area',(.01,.02,.03))
def test_network_fan_intersection_and_independent_water_energy_balance(area):
    r=c.duct_case(area)
    assert abs(r['fan_curve_residual_pa'])<1e-9
    assert abs(r['branch_pressure_residual_pa'])<1e-9
    m=r['useful_flow_m3_s']*1.1
    expected=m*1005*(50-26)+m*.005*2.45e6
    assert r['conditioning_demand_w']==pytest.approx(expected)
    assert r['condensate_kg_s']==pytest.approx(m*.005)
    assert abs(r['mass_balance_residual_m3_s'])<1e-12
    assert abs(r['heat_balance_residual_w'])<1e-9
    assert abs(r['water_balance_residual_kg_s'])<1e-12
    assert r['fan_input_w']==pytest.approx(r['air_power_w']+r['fan_waste_heat_w'])


def test_blockage_leak_loaded_filter_and_fan_failure_degrade_useful_flow():
    normal=c.duct_case(.02)
    for fault in ('blockage','leak','loaded-filter','fan-fault'):
        r=c.duct_case(.02,fault=fault)
        assert r['useful_flow_m3_s']<normal['useful_flow_m3_s']
        assert r['checks']['conservation']
    leak=c.duct_case(.02,fault='leak')
    assert leak['leak_flow_m3_s']>0 and leak['flow_m3_s']>leak['useful_flow_m3_s']
    failed=c.duct_case(.02,fault='fan-fault')
    assert failed['flow_m3_s']==0 and failed['conditioning_demand_w']==0
    assert not failed['checks']['proposed_flow_target']


def test_reverse_humidity_gradient_requires_humidification_not_negative_condensate():
    r=c.duct_case(.02,humidity_in=.004,humidity_out=.010)
    assert r['condensate_kg_s']==0 and r['moisture_added_kg_s']>0
    assert abs(r['water_balance_residual_kg_s'])<1e-12
    assert abs(r['heat_balance_residual_w'])<1e-9


def test_whole_car_uses_declared_heat_moisture_inputs_and_not_hot_roof_air():
    r=c.whole_car_duty();a=r['assumptions'];m=1.1*.8
    sensible=100*75+7000+3000+(m*1005+250)*24
    latent=100*55+m*2.45e6*.005
    assert r['total_conditioning_w']==pytest.approx(sensible+latent)
    assert r['condensate_demand_kg_s']==pytest.approx(latent/2.45e6)
    assert r['roof_surface_temperature_used_as_air'] is False
    assert r['selected_refrigeration_module'] is None


def test_worst_case_stack_includes_thermal_and_known_failed_existing_fit():
    r=c.tolerance_stack()
    assert r['thermal_movement_m']==pytest.approx(1.2*12e-6*70)
    assert r['worst_case_offset_m']==pytest.approx(.0005+.0005+.001+.001+1.2*12e-6*70)
    assert r['guide_margin_m']<0 and r['connector_float_margin_m']<0
    assert r['statistical_yield'] is None
    improved=c.tolerance_stack(clearance_m=.006,connector_float_m=.006)
    assert all(improved['checks'].values())


def test_graph_rejects_omitted_fasteners_unbond_before_disconnect_and_impossible_order():
    graph=c.process_graph('r1');order=[o['id'] for o in graph]
    assert c.sequence_check(graph,order)['removal_reached']
    assert not c.sequence_check(graph,[o for o in order if o!='final-lock'])['passed']
    swap=order.copy();a=swap.index('unbond');b=swap.index('disconnect-services');swap[a],swap[b]=swap[b],swap[a]
    assert not c.sequence_check(graph,swap)['passed']
    assert not c.sequence_check(graph,['withdraw'])['passed']
    assert not c.sequence_check(graph,order+['identity'])['passed']
    assert all(o['unit_revision']=='r1' and not o['executed'] and o['duration_person_s'] is None for o in graph)


def test_swept_removal_envelope_detects_obstacle_even_if_final_pose_clear():
    r=c.swept_path(obstacles=[dict(id='rear-panel',bounds_m=[[-1.5,-.1,-.02],[-1.4,.1,.1]])])
    assert r['colliding_obstacles']==['rear-panel']
    assert not r['actual_vehicle_access_verified']
    clear=c.swept_path(obstacles=[dict(id='far-wall',bounds_m=[[1.,1.,1.],[2.,2.,2.]])])
    assert clear['clear_in_supplied_aabb_scene']
    empty=c.swept_path();assert not empty['installed_vehicle_scene_supplied']


def test_assembly_cost_and_yield_unranked_without_calibration():
    values=c.assembly_comparison(c.process_graph('r1'))
    assert len(values)==3
    assert all(v['installed_cost'] is None and v['factory_person_hours'] is None and v['first_pass_yield'] is None for v in values)
    assert all(not v['cost_calibrated'] for v in values)


def test_report_binds_exact_candidate_and_preserves_known_failures_holds(pair):
    p,candidate=pair;r=c.report(p,candidate)
    assert c.verify_report(p,candidate,r)
    assert 'worst_case_guide_fit' in r['failed_checks']
    assert 'connector_derating' in r['held_checks']
    assert r['cad_harness_correspondence']['conductor_count_matches']
    assert r['cad_harness_correspondence']['conductor_area_matches']
    assert not r['cad_harness_correspondence']['all_terminals_and_routes_in_native_geometry']
    assert not r['digital_specification_complete'] and not r['production_qualification']
    assert all(not r[flag] for flag in core.FLAGS)
    corrupt=deepcopy(r);corrupt['checks']['worst_case_guide_fit']=True
    with pytest.raises(ValueError):c.verify_report(p,candidate,corrupt)
    changed=deepcopy(candidate);changed['metadata']['netlist']['reference_wire_awg']=12
    with pytest.raises(ValueError):c.report(p,changed)


@pytest.mark.parametrize('kwargs',({'voltage_v':float('nan')},{'female_length_m':0},{'source_ohm':-1},{'ambient_c':float('nan')},{'fault':'unknown'}))
def test_invalid_electrical_inputs_fail(kwargs):
    with pytest.raises(ValueError):c.electrical_case(**kwargs)


def test_nominal_flow_failure_propagates_without_confusing_expected_fault_loss(pair):
    from engineering.assembly_design import evaluate
    policy,candidate=pair
    undersized=evaluate.evaluate(policy,candidate)
    key='cassette-system/nominal-duct/proposed_flow_target'
    assert key in undersized['failed_checks']
    assert undersized['supplemental_evidence']['cassette-system']['duct_cases'][0]['useful_flow_m3_s']<.08
    variables=dict(candidate['variables'],duct_area_m2=.02)
    larger=evaluate.evaluate(policy,models.build(policy,'service-cassette',variables))
    assert larger['checks'][key] is True
    # Increasing area repairs this implemented duty screen without erasing the
    # independent guide/connector failures or inventing a supplier fan map.
    assert larger['state']=='failed' and 'cassette-system/worst_case_guide_fit' in larger['failed_checks']
    assert 'cassette-system/nominal-duct/fan_supplier_map' in larger['held_checks']
    faults=larger['supplemental_evidence']['cassette-system']['duct_cases'][1:]
    assert any(not case['checks']['proposed_flow_target'] for case in faults)
