"""Real whole-frame load paths, centroid ties, counterexamples and native scope."""
from copy import deepcopy
import pytest
import numpy as np
from engineering.twin_workflow import core
from engineering.assembly_design import baseline, carbody_assembly as body, carbody_frame as frame
from engineering.design_consistency import contracts


@pytest.fixture(scope='module')
def policy():return core.read(baseline.DATA)


@pytest.fixture(scope='module')
def slender(policy):return body.build(policy)


@pytest.fixture(scope='module')
def strong(policy):return body.build(policy,list(body.candidates(policy))[4])


@pytest.fixture(scope='module')
def result(strong):return frame.report(strong)


def test_registered_spatial_element_independent_cantilever_axial_torsion_controls():
    control=frame.benchmarks()
    assert control['passed'] and control['cantilever_relative_error']<1e-9


def test_all_actual_rhs_parts_and_axes_bound_no_sheet_stiffness(strong):
    t=frame.topology(strong);parts={p['id']:p for p in strong['contract']['parts']}
    expected={p['id'] for p in parts.values() if p['analysis']['section']}
    assert {e['part_id'] for e in t['elements']}==expected
    assert set(t['stiffness_excluded'])==set(parts)-expected
    assert any('skin' in identity for identity in t['stiffness_excluded'])
    for e in t['elements']:
        p=parts[e['part_id']]
        assert e['part_revision']==strong['revision']==p['revision']
        assert e['section']==p['analysis']['section'] and e['section_rotation']==p['placement']['rotation']
    assert t['rigid_links'] and any(r['offset_length_m']>.1 for r in t['rigid_links'])
    for link in t['rigid_links']:
        assert 'Unqualified' in link['model']
        assert link['offset_m']==pytest.approx(np.asarray(link['second_point_m'])-link['first_point_m'])
    # No master merger silently loses an eccentricity.
    for n,m in enumerate(t['masters']):
        offset=np.asarray(t['nodes_m'][n])-t['master_coordinates_m'][m]
        assert t['transforms'][n][:3,3:]==pytest.approx(-frame.skew(offset))


def test_complete_mass_force_moment_and_equation_residuals(strong,result):
    own=result['cases']['represented_self_weight']
    assert own['applied_mass_kg']==pytest.approx(contracts.summary(strong['contract'])['mass_kg'],rel=1e-9)
    for case in result['cases'].values():
        assert max(case['force_balance_relative'],case['moment_balance_relative'],case['free_equation_residual_relative'])<1e-7
        assert np.asarray(case['support_force_n'])+case['applied_force_n']==pytest.approx([0,0,0],abs=1e-4)
        assert case['adopted_stress_allowable_pa'] is None and case['adopted_deflection_limit_m'] is None
        assert not case['physical_validation'] and not case['manufacturing_release']
    assert result['part_revisions']=={p['id']:p['revision'] for p in strong['contract']['parts']}


def test_refinement_double_load_lateral_braking_and_eccentricity_controls(result):
    cases=result['cases'];base=cases['refined_planning'];double=cases['double_vertical']
    assert result['refinement_relative_change']<.01
    assert double['maximum_vertical_displacement_m']==pytest.approx(2*base['maximum_vertical_displacement_m'])
    assert double['maximum_gross_elastic_fibre_stress_pa']==pytest.approx(2*base['maximum_gross_elastic_fibre_stress_pa'])
    assert cases['lateral_sensitivity']['maximum_lateral_displacement_m']>base['maximum_lateral_displacement_m']
    assert cases['braking_sensitivity']['maximum_longitudinal_displacement_m']>base['maximum_longitudinal_displacement_m']
    assert cases['eccentric_floor_sensitivity']['maximum_vertical_displacement_m']>base['maximum_vertical_displacement_m']


def test_slender_failure_is_retained_and_strengthened_research_solution_passes(slender,result):
    failed=frame.report(slender)
    assert failed['state']=='failed'
    assert not failed['checks']['provisional_nominal_S355_elastic_guardrail']
    assert not failed['checks']['provisional_length_over_1000_vertical_target']
    assert failed['cases']['refined_planning']['maximum_gross_elastic_fibre_stress_pa']>900e6
    assert result['checks']['provisional_nominal_S355_elastic_guardrail']
    assert result['checks']['provisional_length_over_1000_vertical_target']
    assert not result['failed_checks'] and result['held_checks'] and result['state']=='hold'
    assert result['provisional_targets']['approved'] is False
    assert 'Unapproved' in result['provisional_targets']['deflection_basis']
    assert result['provisional_targets']['nominal_yield_pa']==355e6
    assert all(result[k] is False for k in core.FLAGS)


def test_stock_alternatives_change_real_geometry_without_closing_apertures(policy):
    originals=[body.build(policy,v) for v in list(body.candidates(policy))[:3]]
    strengthened=[body.build(policy,v) for v in list(body.candidates(policy))[3:]]
    clear=originals[0]['metadata']['openings']
    for c in strengthened:
        assert c['metadata']['openings']==clear and not body.opening_interferences(c)
        assert c['metadata']['dimensions_m']==originals[0]['metadata']['dimensions_m']
        jamb=next(p for p in c['contract']['parts'] if 'post-' in p['id'])
        assert jamb['analysis']['section']['height_m']>originals[0]['metadata']['portal_profile']['post_x']


def test_unknown_or_unbounded_frame_inputs_rejected(strong):
    with pytest.raises(ValueError):frame.topology(strong,refinement=8)
    with pytest.raises(ValueError):frame.solve(strong,vertical_scale=0.)
    with pytest.raises(ValueError):frame.solve(strong,lateral_fraction=float('nan'))
    with pytest.raises(ValueError):frame.solve(strong,left_share=1.01)
    altered=deepcopy(strong);altered['contract']['parts'][0]['properties']['mass_kg']+=1
    with pytest.raises(ValueError):frame.topology(altered)


def test_topology_does_not_turn_window_glass_retention_into_rigid_header_to_sill(strong):
    t=frame.topology(strong)
    assert all('glass' not in link['joint_id'] and 'retention' not in link['joint_id'] for link in t['rigid_links'])
    # All offsets come from controlled, explicitly primary-member joint rows.
    allowed={j['id'] for j in strong['contract']['assembly_joints'] if all(next(p for p in strong['contract']['parts'] if p['id']==i)['analysis']['section'] for i in j['endpoints'])}
    assert {r['joint_id'] for r in t['rigid_links']}<=allowed


def test_native_strengthened_control_has_no_material_intersection(tmp_path,strong):
    from engineering.continuous_design import study_confirmation
    import shutil,subprocess
    if not shutil.which('FreeCADCmd') and not shutil.which('freecadcmd'):
        if not shutil.which('flatpak') or subprocess.run(['flatpak','info','org.freecad.FreeCAD'],capture_output=True).returncode:
            pytest.skip('native FreeCAD unavailable')
    path=tmp_path/'definition.json';core.write(path,strong['contract'])
    proof,state,error=study_confirmation.native(path,tmp_path/'native')
    assert state=='passed',error
    assert len(proof['checks'])==len(strong['contract']['parts'])
    assert proof['native_reopened'] and proof['step_volume_reconciled']


def test_frame_plot_comes_from_exact_result_nodes(tmp_path,result):
    path=tmp_path/'frame.png';frame.plot(result,path)
    assert path.stat().st_size>10_000
    assert path.read_bytes().startswith(b'\x89PNG')


def test_cached_report_is_full_candidate_source_keyed_and_copy_isolated(strong,result):
    first=frame.report(strong);first['cases']['refined_planning']['maximum_vertical_displacement_m']=1e99
    assert frame.report(strong)['cases']['refined_planning']['maximum_vertical_displacement_m']<1.
    changed=deepcopy(strong);changed['contract']['parts'][0]['properties']['mass_kg']+=1.
    with pytest.raises(ValueError):frame.report(changed)
    changed=deepcopy(strong);changed['metadata']['prototype_revision']='0'*64
    with pytest.raises(ValueError,match='stale prototype'):frame.report(changed)
