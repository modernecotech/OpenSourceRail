"""Independent local/modal/fatigue controls, adverse domains and manufacturing stack."""
from copy import deepcopy
import math
import pytest
from engineering.assembly_design import baseline,structural_bay as bay,structural_detail as d
from engineering.twin_workflow import core


@pytest.fixture
def policy():
    p=core.read(baseline.DATA);p['pilots']['structural-bay']=deepcopy(bay.PILOT);return p


def candidate(policy,thickness=.003):
    variables=next(bay.candidates(policy));variables['floor_thickness_m']=thickness
    return bay.build(policy,variables)


@pytest.mark.parametrize('floor',(.003,.004,.012,.016))
def test_actual_stack_has_bearing_contact_both_washers_and_engaged_thread_projection(policy,floor):
    c=candidate(policy,floor);stack=c['metadata']['fastener_stack'];parts={p['id']:p for p in c['contract']['parts']}
    assert all(stack['checks'].values())
    assert stack['lower_washer_z_m'][-1]==0.
    assert stack['floor_z_m'][-1]==stack['foot_z_m'][0]
    assert stack['foot_z_m'][-1]==stack['upper_washer_z_m'][0]
    assert stack['upper_washer_z_m'][-1]==stack['nut_z_m'][0]
    assert 2<=stack['projected_threads']<=4+1e-10
    shaft,head=parts['mount-bolt-0']['manufacturing']['primitives']
    lower=parts['mount-lower-washer-0']['manufacturing']['primitives'][0]
    assert head['centre_m'][2]+head['length_m']/2==pytest.approx(lower['centre_m'][2]-lower['length_m']/2)
    assert shaft['centre_m'][2]+shaft['length_m']/2==pytest.approx(stack['bolt_tip_z_m'])
    assert len(c['contract']['parts'])==30


def test_thread_area_and_joint_group_controls_are_independent():
    assert d.thread_area()*1e6==pytest.approx(58.0,rel=.002)
    positions=[[-.202,-.12,0.],[-.202,.12,0.],[.202,-.12,0.],[.202,.12,0.]]
    result=d.local_mount(positions_m=positions,mass_kg=40.,cg_height_m=.1,floor_m=.004)
    adverse=d.local_mount(positions_m=positions,mass_kg=40.,cg_height_m=.1,floor_m=.004,load_scale=2.)
    for row,doubled in zip(result['cases'],adverse['cases']):
        assert row['bolt_group']['resultant_relative_error']<1e-10
        assert doubled['equivalent_thread_stress_pa']==pytest.approx(2*row['equivalent_thread_stress_pa'])
        assert row['edge_tearout_shear_pa']==pytest.approx(row['peak_shear_n']/(2*(.018-.0055)*.004))
        assert row['foot_strip_bending_stress_pa']==pytest.approx(6*row['peak_tension_n']*.04/(.06*.006**2))
    missing=d.local_mount(positions_m=positions,mass_kg=40.,cg_height_m=.1,floor_m=.004,missing_bolt=0)
    assert missing['represented_bolt_count']==3
    assert max(r['peak_tension_n'] for r in missing['cases'])>max(r['peak_tension_n'] for r in result['cases'])


def test_floor_central_load_and_own_weight_both_contribute():
    p=d.floor_strip(force_n=100.,span_m=1.,width_m=.1,thickness_m=.01)
    total=d.floor_strip(force_n=100.,span_m=1.,width_m=.1,thickness_m=.01,uniform_n_m=100.)
    assert p['stress_pa']==pytest.approx(6*25/(.1*.01**2))
    assert total['stress_pa']/p['stress_pa']==pytest.approx(1.5)
    assert total['deflection_m']/p['deflection_m']==pytest.approx(1.625)
    doubled=d.floor_strip(force_n=200.,span_m=1.,width_m=.1,thickness_m=.01,uniform_n_m=200.)
    assert doubled['deflection_m']==pytest.approx(2*total['deflection_m'])


def test_independent_modal_formulation_refines_and_scales():
    coarse=d.modal_beam(1.2,200000.,50.,elements=8);fine=d.modal_beam(1.2,200000.,50.,elements=16)
    assert max(fine['relative_errors'])<max(coarse['relative_errors'])
    assert fine['frequencies_hz'][0]==pytest.approx(math.pi/(2*1.2**2)*math.sqrt(200000/50),rel=2e-6)
    stiff=d.modal_beam(1.2,800000.,50.,elements=16)
    heavy=d.modal_beam(1.2,200000.,200.,elements=16)
    assert stiff['frequencies_hz']==pytest.approx([2*f for f in fine['frequencies_hz']])
    assert heavy['frequencies_hz']==pytest.approx([f/2 for f in fine['frequencies_hz']])


def test_elastic_plate_buckling_has_correct_thickness_width_scaling():
    stress=d.plate_buckling(width_m=.1,thickness_m=.003)
    assert d.plate_buckling(width_m=.1,thickness_m=.006)==pytest.approx(4*stress)
    assert d.plate_buckling(width_m=.2,thickness_m=.003)==pytest.approx(stress/4)


def test_explicit_synthetic_fatigue_control_and_adverse_scaling():
    # Synthetic S-N control only; not a railway material/weld classification.
    args=dict(reference_range_pa=100e6,reference_cycles=2e6,slope=3.)
    full=d.fatigue_damage([100e6],[2e6],**args)
    assert full['damage']==pytest.approx(1.)
    bins=d.fatigue_damage([100e6,50e6,0.],[1e6,4e6,1e9],**args)
    assert bins['damage']==pytest.approx(.75)
    doubled=d.fatigue_damage([200e6],[2e6],**args)
    assert doubled['damage']==pytest.approx(8.)
    with pytest.raises(ValueError):d.fatigue_damage([float('nan')],[1.],**args)
    with pytest.raises(ValueError):d.fatigue_damage([1.],[-1.],**args)


def test_real_floor_failures_retained_and_thick_floor_remains_held_not_qualified(policy):
    results={t:bay.evaluate(policy,candidate(policy,t)) for t in (.003,.004,.012,.016)}
    assert all(results[t]['state']=='failed' for t in (.003,.004,.012))
    assert results[.016]['state']=='hold' and results[.016]['implemented_checks_pass']
    detail=results[.016]['supplemental_evidence']['structural-detail']
    assert detail['floor_strip']['uniform_n_m']>0
    assert detail['fatigue']['damage'] is None and detail['fatigue']['SN_curve'] is None
    assert detail['checks']['actual-modal-transfer-acceptance'] is None
    assert detail['checks']['qualified-preload-locking-and-WPS'] is None
    assert results[.016]['measurements']['mass_kg']>2*results[.003]['measurements']['mass_kg']
    assert all(not results[.016][flag] for flag in core.FLAGS)


def test_manufacturing_pack_is_revision_linked_and_never_issues_unqualified_welds(policy):
    c=candidate(policy);pack=d.manufacturing_pack(c)
    assert pack['candidate_revision']==c['revision']
    assert {p['id'] for p in pack['parts']}=={p['id'] for p in c['contract']['parts']}
    seen=set()
    for operation in pack['operations']:
        assert set(operation['after'])<=seen;seen.add(operation['id'])
    assert pack['mass_ledger']['proposed_weld_allowance_kg']>0
    assert pack['mass_ledger']['complete_installed_mass_kg'] is None
    assert all(w['WPS'] is None and w['detail_category'] is None for w in pack['welds'])
    assert all(w['effective_throat_m']==pytest.approx(w['weld_leg_m']/math.sqrt(2)) for w in pack['welds'])
    assert not pack['tool_access']['demonstrated']


def test_changed_material_regenerates_modal_floor_and_mass_data(policy):
    original=candidate(policy,.016);old=bay.evaluate(policy,original)['supplemental_evidence']['structural-detail']
    softer=deepcopy(policy)
    next(f for f in softer['facts'] if f['id']=='steel.elastic_modulus')['value']*=.5
    changed=candidate(softer,.016);new=bay.evaluate(softer,changed)['supplemental_evidence']['structural-detail']
    assert changed['revision']!=original['revision']
    assert new['floor_strip']['deflection_m']==pytest.approx(2*old['floor_strip']['deflection_m'])
    assert new['modal'][1]['frequencies_hz']==pytest.approx([f/math.sqrt(2) for f in old['modal'][1]['frequencies_hz']])
    assert new['rail_web_elastic_buckling_stress_pa']==pytest.approx(old['rail_web_elastic_buckling_stress_pa']/2)


def test_longitudinal_weld_stitches_have_actual_accessible_floor_overhang(policy):
    c=candidate(policy);pack=d.manufacturing_pack(c)
    floor=next(p for p in c['contract']['parts'] if p['id']=='floor-panel')['manufacturing']['primitives'][0]
    assert floor['dimensions_m'][1]==pytest.approx(1.08)
    assert c['metadata']['floor_edge_overhang_m']==.01
    rows=[w for w in pack['welds'] if w['joint_id'].startswith('floor-rail-')]
    assert len(rows)==2
    for weld in rows:
        assert len(weld['proposed_segments'])==6
        length=sum(math.dist(s['start_m'],s['end_m']) for s in weld['proposed_segments'])
        assert length==pytest.approx(weld['total_proposed_length_m'])
        assert abs(weld['proposed_segments'][0]['start_m'][1])==pytest.approx(.53)
