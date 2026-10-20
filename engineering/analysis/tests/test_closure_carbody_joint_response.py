"""Finite connections cannot be replaced by coincident-node merging or claims."""
from copy import deepcopy
import math
import numpy as np
import pytest

from engineering.twin_workflow import core
from engineering.assembly_design import baseline,carbody_assembly as body,carbody_frame as frame
from engineering.assembly_design import carbody_joint_response as joint


@pytest.fixture(scope='module')
def candidate():
    policy=core.read(baseline.DATA)
    return body.build(policy,list(body.candidates(policy))[4])


@pytest.fixture(scope='module')
def rigid(candidate):return frame.report(candidate)


@pytest.fixture(scope='module')
def result(candidate,rigid):return joint.report(candidate,rigid)


def test_independent_spring_cantilever_and_eccentric_rigid_body_controls():
    controls=joint.benchmarks()
    assert controls['passed']
    assert controls['beam_on_finite_spring_relative_error']<1e-9
    assert controls['separate_coincident_node_spring_relative_error']<1e-9
    assert controls['eccentric_rigid_body_motion_relative_components_m_rad']==pytest.approx([0]*6,abs=1e-14)


def test_coincident_parts_keep_independent_six_dof_nodes(candidate):
    system=joint.model(candidate);owners=system['node_ownership']
    assert len({(r['part_id'],r['rigid_model_node']) for r in owners})==len(owners)
    coincident=[]
    for connector in system['connectors']:
        a,b=connector['nodes']
        assert a!=b and owners[a]['part_id']!=owners[b]['part_id']
        if np.linalg.norm(np.asarray(system['nodes_m'][a])-system['nodes_m'][b])<1e-10:coincident.append(connector)
    assert len(coincident)>=4  # Physical butt splices, not a shared perfect node.
    assert {e['part_id'] for e in system['elements']}=={p['id'] for p in candidate['contract']['parts'] if p['analysis']['section']}


def test_reference_stiffness_is_dimensional_hypothesis_and_scales_with_modulus(candidate):
    part=next(p for p in candidate['contract']['parts'] if p['analysis']['section'])
    material=candidate['contract']['materials'][part['material']]
    C,record=joint.reference_compliance(part,material)
    stiffer=deepcopy(material);stiffer['young_pa']*=2
    doubled,_=joint.reference_compliance(part,stiffer)
    assert doubled==pytest.approx(C/2)
    assert np.min(np.linalg.eigvalsh(C))>0
    assert record['part_revision']==part['revision']
    assert 'no tested' in record['basis']
    assert record['characteristic_length_m']==pytest.approx(np.linalg.norm(frame._line(part)[1]-frame._line(part)[0]))


def test_joint_offset_rigid_body_rotation_and_action_reaction(candidate,result):
    system=joint.model(candidate)
    rotation=np.asarray([.01,-.02,.03]);translation=np.asarray([.2,-.1,.3])
    for connector in system['connectors']:
        a,b=connector['nodes'];pa=np.asarray(system['nodes_m'][a]);pb=np.asarray(system['nodes_m'][b])
        first=np.r_[translation+np.cross(rotation,pa),rotation]
        second=np.r_[translation+np.cross(rotation,pb),rotation]
        assert connector['second_arm']@second-connector['first_arm']@first==pytest.approx(np.zeros(6),abs=1e-14)
    definitions=result['connectors'];variant=result['variants'][1]
    for case in variant['cases'].values():
        for row in case['joints']:
            c=definitions[row['connector']];a=np.asarray(c['first_centroid_m']);b=np.asarray(c['second_centroid_m']);point=np.asarray(c['joint_point_m'])
            first=np.asarray(row['first_node_wrench_n_nm']);second=np.asarray(row['second_node_wrench_n_nm'])
            assert first[:3]+second[:3]==pytest.approx(np.zeros(3),abs=1e-6)
            moment=first[3:]+second[3:]+np.cross(a-point,first[:3])+np.cross(b-point,second[:3])
            assert moment==pytest.approx(np.zeros(3),abs=1e-5)
            assert max(row['action_reaction_force_relative'],row['action_reaction_moment_relative'])<1e-8


def test_same_mass_and_load_wrenches_equilibrium_and_rigid_limit(result,rigid):
    assert not result['failed_checks']
    assert all(result['checks'][name] for name in ('all_equilibrium','joint_action_reaction','high_stiffness_recovers_rigid_limit','adverse_double_load_control'))
    for variant in result['variants']:
        for name,case in variant['cases'].items():
            source=rigid['cases'][name]
            assert case['input']==source['input']
            assert case['load']['applied_mass_kg']==pytest.approx(source['applied_mass_kg'])
            assert case['load']['applied_force_n']==pytest.approx(source['applied_force_n'],abs=1e-5)
            assert case['load']['applied_moment_nm']==pytest.approx(source['applied_moment_nm'],abs=1e-5)
            assert max(case['force_balance_relative'],case['moment_balance_relative'],case['free_equation_residual_relative'])<1e-6
    high=result['variants'][-1]
    assert max(r['nodewise_difference_from_rigid_relative'] for r in high['cases'].values())<.005
    assert high['cases']['double_vertical']['maximum_vertical_displacement_m']==pytest.approx(rigid['cases']['double_vertical']['maximum_vertical_displacement_m'],rel=.005)


def test_finite_hypothesis_can_fail_rigid_passing_frame_without_selecting_actual_stiffness(result,rigid):
    assert rigid['checks']['provisional_length_over_1000_vertical_target']
    weak,reference,high=result['variants']
    assert weak['maximum_vertical_displacement_m']>reference['maximum_vertical_displacement_m']>high['maximum_vertical_displacement_m']
    assert weak['maximum_joint_translation_m']>reference['maximum_joint_translation_m']>high['maximum_joint_translation_m']
    assert weak['research_failed_checks'] and reference['research_failed_checks']
    assert not high['research_failed_checks'] and high['research_state']=='hold'
    assert weak['cases']['double_vertical']['maximum_vertical_displacement_m']>1
    assert 'outside credible small-deformation' in weak['cases']['double_vertical']['linear_model_validity']
    assert result['selected_stiffness_factor'] is None and result['state']=='hold'
    assert result['checks']['actual_joint_calibration'] is None and result['checks']['connection_resistance_and_fatigue'] is None
    assert not result['digital_specification_complete']
    assert all(result[k] is False for k in core.FLAGS)
    assert all(v[k] is False for v in result['variants'] for k in core.FLAGS)


def test_joint_resultants_and_motion_are_simultaneous_and_scale_with_adverse_load(result):
    for variant in result['variants']:
        base=variant['cases']['refined_planning'];double=variant['cases']['double_vertical']
        assert double['maximum_vertical_displacement_m']==pytest.approx(2*base['maximum_vertical_displacement_m'],rel=1e-7)
        for first,second in zip(base['joints'],double['joints']):
            assert first['connector']==second['connector']
            assert np.asarray(second['relative_at_joint_m_rad'])==pytest.approx(2*np.asarray(first['relative_at_joint_m_rad']),rel=1e-7,abs=1e-10)
            assert np.asarray(second['resultant_on_second_at_joint_n_nm'])==pytest.approx(2*np.asarray(first['resultant_on_second_at_joint_n_nm']),rel=1e-7,abs=1e-5)
    assert all(row['part_revision']==revision for v in result['variants'] for c in v['cases'].values() for row in c['member_critical_segments'] for revision in [result['part_revisions'][row['part_id']]])


def test_portable_candidate_source_binding_and_forged_frame_rejection(candidate,rigid,result):
    assert result['candidate_revision']==candidate['revision']
    assert result['candidate_sha256']==core.digest(candidate)
    assert result['rigid_frame_revision']==rigid['revision']
    assert result['sources_sha256']==joint._sources()
    assert core.digest({k:v for k,v in result.items() if k!='revision'})==result['revision']
    assert core.encoded(result)
    bad=deepcopy(rigid);bad['cases']['refined_planning']['maximum_vertical_displacement_m']/=100
    bad['revision']=core.digest({k:v for k,v in bad.items() if k!='revision'})
    with pytest.raises(ValueError,match='stale or forged'):joint.report(candidate,bad)
    bad=deepcopy(candidate);bad['contract']['parts'][0]['properties']['mass_kg']+=1
    with pytest.raises(ValueError):joint.report(bad,rigid)


def test_cache_returns_deepcopy_and_invalid_stiffness_rejected(candidate,rigid,result):
    changed=joint.report(candidate,rigid);changed['variants'][0]['cases']['double_vertical']['maximum_vertical_displacement_m']=0
    assert joint.report(candidate,rigid)['variants'][0]['cases']['double_vertical']['maximum_vertical_displacement_m']>1
    system=joint.model(candidate)
    for bad in (0.,-1.,float('nan'),float('inf'),True):
        with pytest.raises(ValueError):joint._connector_matrix(system,bad)


def test_plot_uses_actual_calculated_sensitivity(result,tmp_path):
    path=tmp_path/'finite-joints.png';joint.plot(result,path)
    assert path.stat().st_size>10_000 and path.read_bytes().startswith(b'\x89PNG')
