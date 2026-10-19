"""Actual cap cage, void-sensitive sections, stage equilibrium and invalidation."""
from copy import deepcopy
import math
from pathlib import Path
import shutil
import subprocess

import pytest

from engineering.assembly_design import civil_detail as detail,baseline
from engineering.continuous_design import civil_kit,study_confirmation
from engineering.design_consistency import contracts
from engineering.twin_workflow import core


@pytest.fixture(scope='module')
def specimen():return detail.snapshot()


def test_native_compatible_actual_cage_cut_schedule_and_source_budget(specimen):
    candidate=specimen['candidate'];assessment=specimen['assessment'];contracts.validate(candidate['contract'])
    bars=[p for p in candidate['contract']['parts'] if p['id'].startswith('cap-bar-')]
    links=[p for p in candidate['contract']['parts'] if p['id'].startswith('cap-closed-link-')]
    assert len(bars)==20 and len(links)==15 and len(candidate['contract']['parts'])==49
    expected=20*math.pi*.020**2/4*(3.5-.1)*7850
    assert sum(p['properties']['mass_kg'] for p in bars)==pytest.approx(expected)
    link_mass=15*.012*(2.4*1.02-(2.4-.024)*(1.02-.024))*7850
    assert sum(p['properties']['mass_kg'] for p in links)==pytest.approx(link_mass)
    assert len(candidate['bar_schedule'])==len(bars)+len(links)
    assert len(candidate['metadata']['lifting'])==4
    assert assessment['retained_source_unit_mass_kg']==pytest.approx(12052.)
    assert assessment['represented_detail_mass_kg']+assessment['retained_unresolved_allowance_kg']==pytest.approx(candidate['source_unit']['allocated_mass_kg'])
    assert assessment['no_mass_saving_claim'] and not assessment['net_manufactured_unit_mass_verified']
    assert candidate['metadata']['native_contains_concrete_matrix'] is False
    assert all(not candidate[k] and not assessment[k] for k in core.FLAGS)


def test_cage_outer_link_cover_and_spacing_follow_actual_geometry(specimen):
    candidate=specimen['candidate'];lo,hi=candidate['source_unit']['bounds_m'];ys=candidate['metadata']['link_positions_y_m']
    assert ys[0]-.006-lo[1]==pytest.approx(.05)
    assert hi[1]-ys[-1]-.006==pytest.approx(.05)
    assert max(b-a for a,b in zip(ys,ys[1:]))<=candidate['variables']['link_spacing_m']+1e-12
    for lift in candidate['metadata']['lifting']:
        assert min(abs(lift['point_m'][1]-y) for y in ys)>.075+.006
        assert lift['rated_capacity_n'] is None and lift['mating_device'] is None


def test_actual_hollow_cap_section_is_not_full_envelope(specimen):
    candidate=specimen['candidate'];section=specimen['assessment']['actual_concrete_section'];lo,hi=candidate['source_unit']['bounds_m']
    rectangles=candidate['metadata']['source_concrete_section']
    # Top0.12m/bottom0.20m flanges and two0.25m webs; no solid void fill.
    assert len(rectangles)==4
    expected_area=2.5*(.12+.20)+2*.25*.8
    assert section['area_m2']==pytest.approx(expected_area)
    assert section['area_m2']<(hi[0]-lo[0])*(hi[2]-lo[2])*.5
    assert section['centroid_z_m']<sum((lo[2],hi[2]))/2
    # Independent component-centroid/parallel-axis reference.
    pieces=[(2.5,.20,8.1),(2.5,.12,9.06),(.25,.8,8.6),(.25,.8,8.6)]
    cg=sum(w*h*z for w,h,z in pieces)/expected_area
    inertia=sum(w*h**3/12+w*h*(z-cg)**2 for w,h,z in pieces)
    assert section['inertia_x_m4']==pytest.approx(inertia)


def test_cracked_section_against_independent_transformed_neutral_axis_control():
    b=1.;h=1.;As=.003;d=.95;Ec=30e9;Es=200e9;n=Es/Ec;k=1e-8
    c=(-n*As+math.sqrt((n*As)**2+2*b*n*As*d))/b
    I=b*c**3/3+n*As*(d-c)**2
    rectangles=[dict(x_lower_m=-b/2,x_upper_m=b/2,z_lower_m=0.,z_upper_m=h)]
    bar=[dict(id='tension-steel',x_m=0.,z_m=h-d,area_m2=As)]
    fine=detail.fibre_response(rectangles,bar,k,concrete_modulus_pa=Ec,steel_modulus_pa=Es,divisions=240)
    assert fine['moment_nm']==pytest.approx(Ec*k*I,rel=.001)
    assert abs(fine['normal_force_residual_n'])<1e-5
    assert fine['maximum_concrete_compression_strain']/k==pytest.approx(c,rel=.002)
    reverse=detail.fibre_response(rectangles,[dict(bar[0],z_m=d)],-k,concrete_modulus_pa=Ec,steel_modulus_pa=Es,divisions=240)
    assert reverse['moment_nm']==pytest.approx(-fine['moment_nm'],rel=1e-6)


def test_actual_stage_demands_use_complete_retained_mass_and_independent_beam(specimen):
    assessment=specimen['assessment'];candidate=specimen['candidate'];L=3.5;mass=candidate['source_unit']['mass_kg']
    for stage in assessment['construction_stages']:
        assert stage['complete_retained_unit_mass_kg']==mass
        assert sum(stage['analytical']['reactions_n'])==pytest.approx(mass*9.81*stage['dynamic_factor'])
        assert stage['numerical']['force_balance_relative_error']<1e-6
        assert stage['peak_lifting_core_tension_n']==pytest.approx(max(stage['analytical']['reactions_n'])/math.cos(math.pi/6))
        assert stage['analytical']['reactions_n'][0]>stage['analytical']['reactions_n'][1]
        assert sum(q*(b-a)*(a+b)/2 for a,b,q in stage['mass_line_patches_n_per_m'])==pytest.approx(sum(R*x for R,x in zip(stage['analytical']['reactions_n'],stage['picks_m'])))
        assert stage['required_early_tensile_strength_pa']>0
        assert assessment['checks'][stage['stage']+'/early-age-cracking-strength'] is None
        assert assessment['checks'][stage['stage']+'/qualified-insert-and-breakout'] is None
    assert assessment['checks']['section-equilibrium']
    assert assessment['checks']['section-mesh-sensitivity']
    assert assessment['monotonic_section']['bending_direction']=='top reinforcement tension'
    assert assessment['reverse_bending_section']['bending_direction']=='bottom reinforcement tension'


def test_patch_integral_agrees_with_existing_uniform_control_and_adverse_scaling():
    from engineering.assembly_design.evaluate import overhang_beam
    L=4.;supports=[.5,3.5];ei=4e6;q=1000.
    expected=overhang_beam(L,supports,ei,q)
    whole=detail.patch_beam(L,supports,ei,[(0.,L,q)])
    split=detail.patch_beam(L,supports,ei,[(0.,1.,q),(1.,2.5,q),(2.5,L,q)])
    assert whole['maximum_deflection_m']==pytest.approx(expected['maximum_deflection_m'])
    assert whole['maximum_moment_nm']==pytest.approx(expected['maximum_moment_nm'])
    assert split['maximum_deflection_m']==pytest.approx(whole['maximum_deflection_m'])
    adverse=detail.patch_beam(L,supports,ei,[(0.,1.,2*q),(1.,L,q)])
    assert adverse['reactions_n'][0]>adverse['reactions_n'][1]
    assert adverse['total_force_n']==5000.
    assert adverse['first_moment_n_m']==pytest.approx(8500.)
    scaled=detail.patch_beam(L,supports,ei,[(0.,1.,4*q),(1.,L,2*q)])
    assert scaled['maximum_deflection_m']==pytest.approx(2*adverse['maximum_deflection_m'])


def test_service_cut_reconciles_exact_bearing_forces_and_cap_self_weight(specimen):
    assessment=specimen['assessment'];envelope=specimen['reaction_envelope']
    for case in assessment['service_cases']:
        combination=next(c for c in envelope['combinations'] if c['id']==case['id'])
        rows=[r for r in combination['bearing_reactions'] if r['bearing_id'] in case['bearing_ids']]
        assert len(rows)==2
        own_force=own_moment=0.
        for row in specimen['candidate']['metadata']['mass_line_segments']:
            a,b=row['start_m'],min(2.5,row['end_m'])
            if b<=a:continue
            q=row['mass_kg']*9.81*combination['G']/(row['end_m']-row['start_m'])
            own_force+=q*(b-a);own_moment+=q*(b-a)*(2.5-(a+b)/2)
        assert case['shear_demand_n']==pytest.approx(sum(r['force_n'][2] for r in rows)+own_force)
        assert case['cantilever_moment_nm']==pytest.approx(sum(r['force_n'][2]*(-1-r['position_m'][1]) for r in rows)+own_moment)
        assert case['reaction_revision']==envelope['revision']


@pytest.mark.parametrize('defect',('detail','kit','unit','reaction','column'))
def test_stale_detail_load_and_column_definitions_rejected(specimen,defect):
    candidate=deepcopy(specimen['candidate']);envelope=deepcopy(specimen['reaction_envelope'])
    if defect=='detail':candidate['metadata']['bars'][0]['area_m2']*=2
    elif defect=='kit':envelope['kit_revision']='0'*64
    elif defect=='unit':envelope['unit_revisions'][candidate['source_unit']['id']]='0'*64
    elif defect=='reaction':envelope['combinations'][-1]['bearing_reactions'][0]['force_n'][2]*=2
    else:
        envelope['unit_revisions'][candidate['metadata']['column_supports'][0]['id']]='0'*64
        envelope['revision']=core.digest({k:v for k,v in envelope.items() if k!='revision'})
    with pytest.raises(ValueError):detail.evaluate(candidate,envelope)


def test_controlled_variation_changes_steel_mass_and_nonlinear_response(specimen):
    policy=baseline.validate(core.read(baseline.DATA));kit=civil_kit.build(civil_kit.defaults());envelope=specimen['reaction_envelope']
    low=detail.build(policy,kit,variables=dict(bar_diameter_m=.016,bars_per_layer=8,link_spacing_m=.25))
    high=detail.build(policy,kit,variables=dict(bar_diameter_m=.025,bars_per_layer=12,link_spacing_m=.25))
    a=detail.evaluate(low,envelope);b=detail.evaluate(high,envelope)
    assert low['revision']!=high['revision']
    assert a['represented_detail_mass_kg']<b['represented_detail_mass_kg']
    assert a['proposed_sampled_section_moment_nm']<b['proposed_sampled_section_moment_nm']
    assert a['checks']['proposed-monotonic-flexure-only'] is False
    assert a['state']=='failed'
    assert b['held_checks'] and not b['physical_validation']


@pytest.mark.parametrize('value',(float('nan'),0.,-1.))
def test_nonfinite_or_nonphysical_section_properties_rejected(value):
    region=[dict(x_lower_m=-.5,x_upper_m=.5,z_lower_m=0.,z_upper_m=1.)]
    with pytest.raises(ValueError):detail.fibre_response(region,[dict(id='b',x_m=0.,z_m=.1,area_m2=.001)],1e-6,concrete_modulus_pa=value)


def test_process_graph_uses_open_leg_assembly_and_holds_real_release(specimen,tmp_path):
    from engineering.assembly_design import workflow
    candidate=specimen['candidate'];graph=candidate['process_graph'];seen=set();parts={p['id'] for p in candidate['contract']['parts']}
    for operation in graph['operations']:
        assert set(operation['after'])<=seen
        assert set(operation['part_ids'])<=parts
        assert operation['measured_duration_h'] is None and not operation['executed'] and not operation['accepted']
        seen.add(operation['id'])
    assert len(seen)==13
    assert next(o for o in graph['operations'] if o['id']=='place-main-bars')['access']['end_insertion_of_closed_links'] is False
    assert next(o for o in graph['operations'] if o['id']=='demould')['required_evidence']
    assert next(o for o in graph['operations'] if o['id']=='bearing-replacement')['required_evidence']
    assert len(candidate['qa_plan'])==len(parts) and all(q['unit_revision']==candidate['revision'] and q['records']==[] for q in candidate['qa_plan'])
    workflow.tables(candidate,tmp_path)
    assert (tmp_path/'manufacturing-bom.csv').is_file() and (tmp_path/'inspection.svg').is_file()


@pytest.mark.parametrize('defect',('negative-steel','void-steel','zero-area','nan-region'))
def test_section_rejects_unknown_or_invalid_material_locations(specimen,defect):
    candidate=specimen['candidate'];rectangles=deepcopy(candidate['metadata']['source_concrete_section']);bars=deepcopy(candidate['metadata']['bars'])
    if defect=='negative-steel':bars[0]['area_m2']=-.001
    elif defect=='void-steel':bars[0].update(x_m=0.,z_m=8.6)
    elif defect=='zero-area':rectangles[0]['x_upper_m']=rectangles[0]['x_lower_m']
    else:rectangles[0]['z_lower_m']=float('nan')
    with pytest.raises(ValueError):detail.fibre_response(rectangles,bars,.001)


def test_real_native_civil_cage_and_embedded_core_geometry(tmp_path,specimen):
    if not (shutil.which('FreeCADCmd') or shutil.which('freecadcmd')):
        if not shutil.which('flatpak') or subprocess.run(['flatpak','info','org.freecad.FreeCAD'],capture_output=True).returncode:pytest.skip('native FreeCAD unavailable')
    path=tmp_path/'physical-contract.json';core.write(path,specimen['candidate']['contract'])
    proof,state,error=study_confirmation.native(path,tmp_path/'cad')
    assert state=='passed',error
    assert proof['physical_ids_preserved'] and proof['native_reopened'] and proof['step_volume_reconciled']
    assert proof['manufacturing_unit_ids_preserved']
