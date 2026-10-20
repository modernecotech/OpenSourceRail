"""Exact simultaneous splice-end demand and nominal weld-gap material ownership."""
from copy import deepcopy
import json
import math

import pytest
from engineering.assembly_design import baseline,carbody_assembly as body,carbody_frame as frame,carbody_splice as splice
from engineering.twin_workflow import core
from engineering.design_consistency import contracts


@pytest.fixture(scope='module')
def policy():return core.read(baseline.DATA)


@pytest.fixture(scope='module')
def source(policy):return body.build(policy,list(body.candidates(policy))[4])


@pytest.fixture(scope='module')
def frame_report(source):return frame.report(source)


@pytest.fixture(scope='module')
def demands(policy,source,frame_report):return splice.demand_register(source,frame_report,policy=policy)


def test_each_declared_primary_splice_has_both_exact_member_ends_in_every_retained_case(source,frame_report,demands):
    declared={j['id']:j for j in source['contract']['assembly_joints'] if j['id'].endswith('-butt-splice')}
    assert demands['joint_count']==4 and demands['case_count']==7
    assert {j['joint_id'] for j in demands['splices']}==set(declared)
    assert sum(len(c['sides']) for j in demands['splices'] for c in j['cases'])==56
    for joint in demands['splices']:
        assert joint['source_joint_sha256']==core.digest(declared[joint['joint_id']])
        assert {c['case_id'] for c in joint['cases']}==set(frame_report['cases'])
        for case in joint['cases']:
            raw=frame_report['cases'][case['case_id']]
            assert case['source_case_sha256']==core.digest(raw)
            assert {r['part_id'] for r in case['sides']}==set(joint['part_ids'])
            for side in case['sides']:
                assert side['exact_source_endpoint_m']==pytest.approx(joint['cut_point_world_m'],abs=1e-10)
                assert side['retained_frame_node_m']==pytest.approx(joint['cut_point_world_m'],abs=1e-10)
                row=next(r for r in raw['member_forces'] if r['part_id']==side['part_id'] and r['nodes']==side['element_nodes'])
                end=side['element_endpoint_index']
                assert side['raw_local_end_wrench_n_nm']==row['local_end_forces_n_nm'][end*6:end*6+6]
                assert side['common_positive_local_x_section_wrench_n_nm']==[side['common_convention_multiplier']*x for x in side['raw_local_end_wrench_n_nm']]
                assert len(side['raw_local_end_wrench_n_nm'])==6
    assert all(demands[k] is False for k in core.FLAGS)


def test_two_sides_are_retained_without_averaging_endpoint_load_ambiguity(demands):
    assert not demands['componentwise_envelope_used'] and not demands['side_average_used']
    assert not demands['adopted_joint_demands']
    sums=[]
    for joint in demands['splices']:
        for case in joint['cases']:
            for i in range(6):assert case['raw_endpoint_wrench_sum_n_nm'][i]==pytest.approx(sum(r['raw_local_end_wrench_n_nm'][i] for r in case['sides']))
            assert not case['resolved_joint_free_body']
            assert 'not a weld equilibrium failure' in case['endpoint_load_interpretation']
            sums.extend(case['raw_endpoint_wrench_sum_n_nm'])
    # Real lumped node loads/rigid transfers make some opposing endpoint values
    # unequal; the adapter must preserve this rather than forcing equal demand.
    assert max(abs(v) for v in sums)>1.


@pytest.mark.parametrize('mutation',('force','case-input','member-revision','missing-case'))
def test_resealed_frame_report_cannot_override_recomputed_source(policy,source,frame_report,mutation):
    broken=deepcopy(frame_report)
    if mutation=='force':broken['cases']['refined_planning']['member_forces'][0]['local_end_forces_n_nm'][0]+=1000.
    elif mutation=='case-input':broken['cases']['planning']['input']['vertical_scale']=.01
    elif mutation=='member-revision':broken['part_revisions'][next(iter(broken['part_revisions']))]='0'*64
    else:del broken['cases']['double_vertical']
    broken['revision']=core.digest({k:v for k,v in broken.items() if k!='revision'})
    with pytest.raises(ValueError,match='exact retained source frame report'):splice.demand_register(source,broken,policy=policy)


def test_three_distinct_native_recipes_preserve_selected_parent_stock_and_actual_mass(policy,source,frame_report):
    candidates=[splice.build(policy,v,carbody=source,frame_report=frame_report) for v in splice.candidates(policy)]
    assert {c['kind'] for c in candidates}=={'carbody-splice-half','carbody-splice-three-quarter','carbody-splice-full'}
    assert len({c['revision'] for c in candidates})==3
    full=candidates[-1];source_parts={p['id']:p for p in source['contract']['parts']}
    masses=[]
    for c in candidates:
        contracts.validate(c['contract']);m=c['metadata'];parts={p['id']:p for p in c['contract']['parts']}
        assert len(parts)==6 and len(m['offcut_ids'])==2 and len(m['weld_metal_part_ids'])==4
        assert all(p['source_geometry_sha256']==source_parts[p['source_part_id']]['analysis']['geometry_sha256'] for p in parts.values() if p['id'] in m['offcut_ids'])
        assert all(parts[i]['analysis']['section']==m['parent_section'] for i in m['offcut_ids'])
        assert m['coupon_root_gap_m']==.003 and m['original_body_nominal_gap_m']==0.
        assert not m['installed_in_source_carbody'] and not m['source_body_stiffness_modified']
        assert not m['issued_manufacturing_detail'] and m['complete_installed_mass_kg'] is None
        assert all(not r['accepted'] and r['serial'] is None and r['records']==[] for r in c['qa_plan'])
        assert all(c[k] is False for k in core.FLAGS)
        rho=c['contract']['materials']['weld-metal-hypothesis']['density_kg_m3']
        assert m['weld_mass_kg']==pytest.approx(m['filler_section']['area_m2']*.003*rho)
        masses.append(m['weld_mass_kg'])
    assert masses==pytest.approx([.5*masses[-1],.75*masses[-1],masses[-1]])
    for key in ('area_m2','iy_m4','iz_m4'):
        assert full['metadata']['filler_section'][key]==pytest.approx(full['metadata']['parent_section'][key],rel=1e-12)


def test_partial_penetration_are_failed_defect_controls_and_full_remains_held(policy,source):
    for v in splice.candidates(policy):
        c=splice.build(policy,v,carbody=source);r=splice.evaluate(policy,json.loads(core.encoded(c)))
        if v['penetration_fraction']<1:
            assert r['failed_checks']==['nominal_complete_penetration']
            assert 'defect sensitivity' in c['metadata']['penetration_class']
        else:assert not r['failed_checks']
        assert len(r['held_checks'])==7 and not r['eligible_as_rail_connection']
        assert r['design_resistance_n_nm'] is None and r['adopted_allowable_pa'] is None
        assert len(r['measurements']['simultaneous_case_indices'])==7
        assert all(r[k] is False for k in core.FLAGS)


def test_linear_section_indices_keep_six_axis_case_and_leave_torsion_acceptance_open(policy,source):
    c=splice.build(policy,carbody=source);s=c['metadata']['filler_section']
    axial=splice.section_index(s,[1000.,0.,0.,0.,0.,0.])
    assert axial['maximum_absolute_normal_index_pa']==pytest.approx(1000/s['area_m2'])
    wrench=[1e4,2e3,-3e3,4e3,5e3,-6e3]
    a=splice.section_index(s,wrench);b=splice.section_index(s,[2*v for v in wrench])
    assert a['simultaneous_wrench_n_nm']==wrench
    assert b['maximum_absolute_normal_index_pa']==pytest.approx(2*a['maximum_absolute_normal_index_pa'])
    assert b['nominal_shear_average_z_pa']==pytest.approx(2*a['nominal_shear_average_z_pa'])
    assert a['torsion_demand_nm']==wrench[3] and a['torsional_stress_pa'] is None
    assert a['adopted_allowable_pa'] is None and a['combined_equivalent_stress_pa'] is None
    # Same axial force on half-gap material has twice its full-area index,
    # without inventing a reduced strength or changing source frame loads.
    partial=splice.build(policy,splice.candidates(policy)[0],carbody=source)
    assert splice.section_index(partial['metadata']['filler_section'],[1000.,0.,0.,0.,0.,0.])['maximum_absolute_normal_index_pa']==pytest.approx(2*axial['maximum_absolute_normal_index_pa'])


@pytest.mark.parametrize('value',(float('nan'),float('inf'),True,'1'))
def test_nonfinite_or_wrong_wrench_values_rejected(policy,source,value):
    c=splice.build(policy,carbody=source);wrench=[0.]*6;wrench[0]=value
    with pytest.raises(ValueError):splice.section_index(c['metadata']['filler_section'],wrench)


@pytest.mark.parametrize('mutation',('weld-dimension','offcut-mass','demand','source','qa','source-variables'))
def test_resealed_coupon_cannot_detach_geometry_qa_or_load_source(policy,source,mutation):
    c=splice.build(policy,carbody=source);broken=deepcopy(c)
    if mutation=='weld-dimension':broken['contract']['parts'][-1]['manufacturing']['primitives'][0]['dimensions_m'][0]*=2
    elif mutation=='offcut-mass':broken['contract']['parts'][0]['properties']['mass_kg']*=.5
    elif mutation=='demand':broken['metadata']['source_joint_demand']['cases'][0]['sides'][0]['raw_local_end_wrench_n_nm'][0]+=1.
    elif mutation=='source':broken['metadata']['source_sha256'][next(iter(broken['metadata']['source_sha256']))]='0'*64
    elif mutation=='qa':broken['qa_plan'][0]['accepted']=True
    else:broken['metadata']['source_body_variables']['frame_wall_m']=.006
    broken['definition_sha256']=core.digest({k:v for k,v in broken.items() if k!='definition_sha256'})
    with pytest.raises(ValueError):splice.evaluate(policy,broken)


def test_manufacturing_sequence_has_unique_owned_parts_but_unexecuted_ndt_and_qualified_wps_hold(policy,source):
    c=splice.build(policy,carbody=source);m=c['metadata'];ids={p['id'] for p in c['contract']['parts']};seen=[];done=set()
    for stage in m['assembly_sequence']:
        assert set(stage['requires'])<=done
        done.add(stage['id']);seen+=stage['part_ids']
    assert len(seen)==len(set(seen)) and set(seen)==ids
    assert all(not op['executed'] and op['hold'] for op in m['process_plan'])
    assert 'NDT' in m['process_plan'][-1]['instruction']
    assert any('WPS' in item for op in m['process_plan'] for item in op['hold'])


@pytest.mark.parametrize('index',(0,1,2))
def test_native_nominal_gap_solids_have_no_overlap_and_preserve_owned_materials(tmp_path,policy,source,index):
    from engineering.continuous_design import study_confirmation
    c=splice.build(policy,splice.candidates(policy)[index],carbody=source)
    path=tmp_path/'definition.json';core.write(path,c['contract'])
    proof,state,error=study_confirmation.native(path,tmp_path/'native')
    assert state=='passed',error
    assert len(proof['checks'])==6 and proof['physical_ids_preserved'] and proof['manufacturing_unit_ids_preserved']
    assert proof['step_volume_reconciled'] and proof['native_reopened']


def test_section_svg_uses_actual_regions_and_distinguishes_unfilled_defect_geometry(policy,source):
    import xml.etree.ElementTree as ET
    full=splice.build(policy,carbody=source)
    partial=splice.build(policy,splice.candidates(policy)[0],carbody=source)
    a=splice.section_svg(full);b=splice.section_svg(partial)
    assert a==splice.section_svg(json.loads(core.encoded(full)))
    ET.fromstring(a);ET.fromstring(b)
    assert a!=b and 'UNISSUED coupon research' in a and 'Unfilled source-wall region' in a
    assert 'parent wall 8.0 mm' in a and 'Nominal fill depth 8.0 mm' in a
    assert 'Nominal fill depth 4.0 mm' in b and 'axial gap 3.0 mm' in b
    assert full['metadata']['source_joint_id'] in a
