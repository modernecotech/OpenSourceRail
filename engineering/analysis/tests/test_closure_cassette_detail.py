"""Actual detail, continuous motion/access and adverse manufacturing controls."""
from copy import deepcopy
from pathlib import Path
import math

import numpy as np
import pytest

from engineering.assembly_design import baseline,models,cassette_detail as d,cassette_system
from engineering.design_consistency import contracts
from engineering.twin_workflow import core


@pytest.fixture
def configured():
    p=core.read(baseline.DATA);variables={k:v[0]for k,v in p['pilots']['service-cassette']['domains'].items()};variables['duct_area_m2']=.02;base=models.build(p,'service-cassette',variables)
    return p,base,d.build(p,base)


def test_every_added_part_has_geometry_mass_revision_and_qa(configured):
    p,base,c=configured
    assert len(c['contract']['parts'])>180
    contracts.validate(c['contract'])
    assert {part['id']for part in c['contract']['parts']}==set(c['metadata']['ownership_groups'])
    assert all(part['revision']==c['revision'] for part in c['contract']['parts'])
    assert len(c['qa_plan'])==len(c['contract']['parts']) and all(not row['accepted'] for row in c['qa_plan'])
    report=d.evaluate(p,c)
    assert core.encoded(report)
    assert report['failed_checks']==[] and report['state']=='hold' and not report['digital_specification_complete']
    assert report['original_baseline_failed_checks']==cassette_system.report(p,base)['failed_checks']
    assert 'worst_case_guide_fit' in report['original_baseline_failed_checks']
    assert all(report[key] is False for key in core.FLAGS)


def test_native_routed_kit_bom_mass_no_doublecount_and_terminations(configured):
    _,_,c=configured;parts=c['contract']['parts'];masses={part['id']:part['properties']['mass_kg']for part in parts}
    female=masses['power-connector']+sum(v for k,v in masses.items()if k.startswith('female-solder-cup-'))
    male=masses['mating-power-connector']+sum(v for k,v in masses.items()if k.startswith('male-solder-cup-'))
    assert female==pytest.approx(.005722) and male==pytest.approx(.005449)
    routes=c['metadata']['harness_routes'];assert len(routes)==16
    assert sum(r['awg']==14 for r in routes)==8 and sum(r['awg']==12 for r in routes)==8
    assert {r['pin']for r in routes}==set(range(1,9))
    for r in routes:
        assert r['strip_length_m']==.005
        assert math.dist(*r['centreline_m'])==pytest.approx(r['cut_length_m'])
        assert 'solder' in r['termination']
    assert all(part['geometric_role']=='supplier-terminal-envelope'for part in parts if '-solder-cup-' in part['id'])


def test_host_pad_relocation_and_complete_bolt_stack(configured):
    _,_,c=configured;parts={p['id']:p for p in c['contract']['parts']}
    pad=parts['vehicle-interface-0'];bounds=d.primitive_bounds(pad,pad['manufacturing']['primitives'][0])
    assert bounds[0][2]==pytest.approx(-.066) and bounds[1][2]==pytest.approx(-.06)
    bolt=parts['mount-0-bolt'];assert bolt['manufacturing']['primitives'][0]['length_m']==.075
    support=parts['host-support--1']['manufacturing']['primitives'][0]
    assert support['hole_radius_m']==.0275 and support['dimensions_m'][1]==.08


def test_continuous_host_sweep_catches_hidden_intermediate_obstacle_and_overtravel(configured):
    _,_,c=configured
    assert d.path_check(c)['passed']
    obstacle=dict(id='unmodelled-rear-crossmember',bounds_m=[[-1.2,-.1,.02],[-1.19,.1,.13]])
    negative=d.path_check(c,extra_obstacles=[obstacle]);assert not negative['passed']
    assert any(hit['fixed_part']=='unmodelled-rear-crossmember'for hit in negative['potential_collisions'])
    assert not d.path_check(c,offset_m=(.005,0,0))['passed']
    assert not d.path_check(c,offset_m=(0,.015,0))['passed']
    assert not d.path_check(c)['actual_vehicle_verified']
    assert not d.path_check(c,travel_m=1.)['complete_withdrawal']
    with pytest.raises(ValueError):d.path_check(c,extra_obstacles=[dict(id='bad',bounds_m=[[0,0,0],[float('nan'),1,1]])])


def test_planned_socket_actually_engages_nut_and_real_support_bore_controls_access(configured):
    _,_,c=configured
    assert d.tool_check(c)['passed']
    assert not d.tool_check(c,cover_installed=True,approach='top-socket')['passed']
    broken=deepcopy(c)
    for p in broken['contract']['parts']:
        if p['id'].startswith('host-support-'):p['manufacturing']['primitives'][0]['hole_radius_m']=.01
    assert not d.tool_check(broken)['passed']
    # Moving the internal harness into the short holding wrench must be detected.
    broken=deepcopy(c)
    wire=next(p for p in broken['contract']['parts']if p['id']=='wire-0-jacket')
    wire['manufacturing']['primitives'][0]['centre_m'][2]=.013
    assert not d.tool_check(broken)['passed']


def test_worst_case_seal_stack_and_tolerance_variants_retain_rejections(configured):
    p,base,c=configured
    good=d.seal_stack(c);assert good['minimum_fraction']==pytest.approx(1-(.00225+.0001)/(.003-.00015))
    assert good['maximum_fraction']==pytest.approx(1-(.00225-.0001)/(.003+.00015))
    assert good['within_proposed_range']
    low=d.evaluate(p,d.build(p,base,seal_compression=.15));assert 'seal_compression_range'in low['failed_checks']
    high=d.evaluate(p,d.build(p,base,seal_compression=.35));assert 'seal_compression_range'in high['failed_checks']
    gap=d.evaluate(p,d.build(p,base,guide_clearance_m=.003));assert 'guide_tolerance'in gap['failed_checks']
    assert d.evaluate(p,d.build(p,base,connector_float_m=.001))['checks']['connector_float_tolerance'] is False


def test_retention_load_uses_all_defined_moving_mass_and_missing_pin_adverse_case(configured):
    _,_,c=configured;r=d.retention_screen(c)
    expected_mass=sum(p['properties']['mass_kg']for p in c['contract']['parts']if p['id']in c['metadata']['cassette_installed_part_ids'])
    assert r['suspended_cassette_mass_kg']==pytest.approx(expected_mass)
    assert r['single_shear_pa']==pytest.approx((expected_mass+100)*9.81*5/(4*math.pi*.008**2/4))
    adverse=d.retention_screen(c,missing_pin=True)
    assert adverse['single_shear_pa']==pytest.approx(r['single_shear_pa']*4/3)
    assert not adverse['checks']['all_required_pins'] and not adverse['pin_material_qualified']


def test_changed_owned_geometry_regenerates_revision_and_stale_definitions_rejected(configured):
    p,base,c=configured
    alternative=d.build(p,base,guide_clearance_m=.006)
    assert alternative['revision']!=c['revision']
    changed=deepcopy(c);changed['contract']['parts'][0]['properties']['mass_kg']+=.1
    with pytest.raises(ValueError):d.evaluate(p,changed)
    changed=deepcopy(base);changed['metadata']['netlist']['active_pins']=[1]
    with pytest.raises(ValueError):d.build(p,changed)


def test_duct_envelope_above_cover_remains_a_failed_geometry_case(configured):
    p,base,_=configured;v=dict(base['variables'],duct_area_m2=.03);bad=d.build(p,models.build(p,'service-cassette',v))
    cover=next(p for p in bad['contract']['parts']if p['id']=='inspection-cover')
    top=next(p for p in bad['contract']['parts']if p['id']=='duct-top')
    cover_z=d.primitive_bounds(cover,cover['manufacturing']['primitives'][0])[0][2]
    top_z=d.primitive_bounds(top,top['manufacturing']['primitives'][0])[1][2]
    assert top_z>cover_z
    assert d.evaluate(p,bad)['checks']['duct_below_inspection_cover'] is False


def test_updated_structure_uses_complete_installed_mass_thread_area_and_independent_beam(configured):
    p,base,c=configured;r=d.carrier_structure(p,c)
    expected=d.retention_screen(c)['suspended_cassette_mass_kg']
    assert r['cassette_installed_mass_kg']==pytest.approx(expected)
    assert 'inspection-cover'in r['included_part_ids'] and 'earth-conductor'in r['included_part_ids']
    assert 'mount-0-bolt'in r['included_part_ids']
    assert r['bolt_stress_area_m2']==pytest.approx(.000157)
    assert len(r['bolt_cases'])==8 and all(r['checks'].values())
    heavy=deepcopy(c);cover=next(x for x in heavy['contract']['parts']if x['id']=='inspection-cover')
    cover['properties']['mass_kg']+=1000.
    adverse=d.carrier_structure(p,heavy)
    assert adverse['beam_cases'][-1]['stress_pa']>r['beam_cases'][-1]['stress_pa']
    assert adverse['peak_mount_equivalent_stress_pa']>r['peak_mount_equivalent_stress_pa']
    assert any(not v for v in adverse['checks'].values())
    result=d.evaluate(p,c)
    assert 'qualified_frame_weld_local_buckling_fatigue'in result['held_checks']
    assert all(x['original_candidate_revision']==base['revision']and x['revised_candidate_revision']==c['revision']for x in result['baseline_constraint_replacements'])
    v=dict(base['variables'],duct_area_m2=.01);low=d.build(p,models.build(p,'service-cassette',v))
    assert 'inherited/nominal_duct_flow_target'in d.evaluate(p,low)['failed_checks']
