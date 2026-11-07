"""Bounded central-girder screening, explicit hardware and ancestry checks."""
from copy import deepcopy
from math import fsum,prod
from pathlib import Path
import gzip,json
import pytest
from engineering.vehicle_installation import model,underframe,export,FLAGS
from engineering.station_rail.common import identity

PARENT=Path('/home/hayder/.local/state/opensourcerail/runs/closure-installed-20261107/frozen02/analytical/installation.json.gz')


@pytest.fixture(scope='module')
def parent():
    # Ordinary CI can reproduce exactly the parent physical record without
    # depending on a developer's private numerical run directory.
    if PARENT.is_file():return underframe.load_parent(PARENT)
    r=model.build()
    assert r['candidate_id']==underframe.PARENT
    # CI tests use the same physical parent under its actual current-source
    # evaluation. Never substitute the historical evaluation seal.
    return r


@pytest.fixture(scope='module')
def result(parent):return underframe.build(parent)


def test_four_trials_keep_failure_and_pareto(result):
    s=result['structural_comparison'];assert len(s['trials'])==4
    by={r['family']['id']:r for r in s['trials']}
    assert by['steel-600x650x8']['passed_under_declared_hypotheses'] is False
    assert any(not c['screens']['local_flange_buckling'] for c in by['steel-600x650x8']['cases'])
    assert by['aluminium-650x650x16']['passed_under_declared_hypotheses'] is False
    assert any(not c['screens']['provisional_torsion_roll'] for c in by['aluminium-650x650x16']['cases'])
    assert set(s['selection']['nondominated_families'])=={'steel-650x650x10'}
    assert s['selection']['independently_selected_for_baseline'] is False
    assert all(r[k] is False for r in s['trials'] for k in FLAGS)


def test_physical_revision_and_zero_roof_credit(parent,result):
    assert result['parent_candidate_id']==parent['candidate_id']
    assert result['candidate_id']!=parent['candidate_id']
    assert identity(result['physical_definition'])==result['candidate_id']
    assert 'Central-girder-only' in ' '.join(result['assumptions'])
    assert all(result[k] is False for k in FLAGS)
    assert all(x['historical_comparison_passed'] is False for x in result['structural_comparison']['original_sill_control'])


def test_removed_secondary_and_mass_accounting(parent,result):
    assert len(result['removed_parts'])==9
    assert not any(p['assembly_id']=='services/secondary' for p in result['parts'])
    assert len({p['source_part_id'] for p in result['parts'] if p['source_part_id']}|{r['source_part_id'] for r in result['removed_parts']})==605
    old={p['id']:p for p in parent['parts']};new={p['id']:p for p in result['parts']}
    for c in model.CASES:
        expected=fsum(p['quantity_per_train']*p['mass_each_kg'][c] for p in new.values())
        assert expected==pytest.approx(result['nominal_part_mass_kg'][c])
    assert set(old)-set(new)=={r['old_part_id'] for r in result['revisions']}|{r['part_id'] for r in result['removed_parts']}
    for p in result['parts']:assert sum(v['count'] for v in result['patterns'] if v['part_id']==p['id'])==p['quantity_per_train']


def test_joint_parts_and_materials_are_real_counted_proposals(result):
    parts={p['id']:p for p in result['parts']}
    assert parts['underframe/crossmember-steel-backing']['quantity_per_train']==288
    assert parts['underframe/bolster-steel-backing']['quantity_per_train']==24
    assert parts['underframe/floor-joint-M16-stud']['quantity_per_train']==1152
    assert parts['underframe/bolster-joint-M20-stud']['quantity_per_train']==192
    assert {p['material_id'] for p in parts.values()}<={m['id'] for m in result['materials']}
    assert result['assembly_plans']['underframe_revision']['joins']['steel_to_aluminium_welds_prohibited']
    assert result['interface_screens']['central_girder']['pod_joint_gap_m']>=.020
    assert result['policy']['layout']['battery_y_m']==[-.975,-.575,.575,.975]
    assert parts['services/battery-module']['quantity_per_train']==450


def test_joint_shear_tension_and_finite_compliance_are_reported(result):
    selected=next(t for t in result['structural_comparison']['trials'] if t['family']['id']=='steel-650x650x10')
    assert len(selected['cases'])==12
    for c in selected['cases']:
        assert c['passed_under_declared_hypotheses']
        assert c['bolt_interaction']>0 and c['floor_stud_interaction']>0
        assert c['beam']['vertical_support_settlement_m']>=.001
        assert all(x>0 for x in c['beam']['finite_splice_extra_rotation_rad'])
        assert c['minimum_dynamic_ground_allocation_m']>=.2
        assert c['engineering_accepted'] is False


def test_uniform_beam_independent_euler_limit():
    p=deepcopy(underframe.ASSUMPTIONS)
    try:
        underframe.ASSUMPTIONS['splice_local_EI_fraction']=1.
        q=12000.;EI=2e8;r=underframe.beam(q,EI)
        exact=(5*q*12.8**4/384-q*2.1**2*12.8**2/16)/EI
        assert r['midspan_relative_deflection_m']==pytest.approx(exact,rel=2e-5)
        with_splice=None
    finally:underframe.ASSUMPTIONS.clear();underframe.ASSUMPTIONS.update(p)
    with_splice=underframe.beam(q,EI)
    assert with_splice['midspan_relative_deflection_m']>r['midspan_relative_deflection_m']


def test_curvature_integration_refinement():
    a=underframe.beam(15000.,2e8,n=850);b=underframe.beam(15000.,2e8,n=1700)
    assert a['midspan_relative_deflection_m']==pytest.approx(b['midspan_relative_deflection_m'],rel=.003)


def test_new_static_loads_and_hardware_reserves_not_double_counted(result):
    plain={r['name']:r for r in result['mass_scenarios']};powered=result['powered_wheel_load_envelope']['load_cases']
    for r in plain.values():
        assert len(r['axles'])==24
        assert abs(r['force_residual_N'])<1e-6 and abs(r['moment_residual_Nm'])<1e-6
    for r in powered:
        expected=9552+underframe.ADDITIONS['drive_BOP_train_kg'][r['case']]+underframe.ADDITIONS['capture_interface_train_kg'][r['case']]
        assert r['train_mass_kg']-plain[r['name']]['train_mass_kg']==pytest.approx(expected)
        delta=[a['vertical_force_N']-b['vertical_force_N'] for a,b in zip(r['axles'],plain[r['name']]['axles'])]
        assert all(delta[i]>delta[i+1] for i in range(0,24,2))
        assert r['hardware_geometry_and_mounts_admitted'] is False


def test_stock_cad_has_split_stubs_and_no_supplier_fiction(result):
    c=underframe.cad_case(result)
    assert 50<len(c['entities'])<5000
    assert any('floor-crossmember-stub' in e['id'] for e in c['entities'])
    assert not any('motor' in e['id'] for e in c['entities'])
    assert fsum(prod(e['size_m']) if e['shape']=='box' else underframe.polygon(e['points_xz_m'])[0]*e['thickness_m'] for e in c['entities'])==pytest.approx(fsum(m['volume_m3'] for m in c['expected']['part_measures'].values()))
    assert c['candidate_id']==result['candidate_id'] and c['physical_accepted'] is False



def test_profiled_ends_clear_known_bogie_stock(result):
    c=result['interface_screens']['central_girder']
    assert c['outer_depth_m']==.34 and c['taper_local_x_m']==[4.4,5.2]
    assert c['bogie_secondary_clearance_after_jounce_m']>=.02
    assert c['inner_axle_clearance_after_jounce_m']>=.02
    assert result['structural_comparison']['selection']['selected_family']=='steel-650x650x10'
    stock=underframe.cad_case(result)
    assert any(e['shape']=='xz-profile-prism' for e in stock['entities'])
    assert underframe.cad_script(stock)['commands'][-1]['command']=='inspect.measure'


def test_parent_mismatch_and_failed_family_are_rejected(parent):
    corrupted=deepcopy(parent);corrupted['candidate_id']='0'*64
    with pytest.raises(ValueError,match='Sealed same-physical'):underframe.build(corrupted)
    with pytest.raises(ValueError,match='Only a screened'):underframe.build(parent,family_id='aluminium-650x650x16')



def test_target_success_does_not_assign_mandatory_acceptance(result):
    a=result['requirement_assessment']
    assert a['declared_hard_screen']=='unknown' and a['integrated_suitability']=='unknown'
    assert all(f['status']=='unknown' for f in a['findings'] if f['category']=='mandatory_obligation')
    assert a['physical_accepted'] is False and a['engineering_accepted'] is False
