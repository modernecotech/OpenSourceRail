"""Invented tiny fixtures; no retained terminal generator/adapter/local call."""
from copy import deepcopy
import math

import pytest

from engineering import terminal_hardware as h


VARIANTS = [(k, None) for k in h.FAMILIES if k != 'thread-guard']+[('thread-guard', 'M6'), ('thread-guard', 'M8')]


@pytest.mark.parametrize('family,size', VARIANTS)
def test_prototype_counts_stock_material_process_QA_and_positive_cost(family, size):
    p = h.prototype(family, size=size)
    assert p['manufactured_piece_count'] == len(p['parts'])
    assert len({r['id'] for r in p['parts']}) == len(p['parts'])
    assert p['candidate_id'] == h._hash(p['physical_definition'])
    assert not any(p['approvals'].values())
    assert p['mass_property_bounds']['exact_CG_m'] is None
    assert all(a<=b for a,b in p['mass_property_bounds']['first_moment_kg_m'])
    for r in p['parts']:
        assert 0 < r['net_volume_bounds_m3'][0] <= r['net_volume_bounds_m3'][1]
        assert r['gross_blank_volume_m3'] >= r['net_volume_bounds_m3'][1]
        assert min(r['person_process_h']) > 0 and min(r['person_QA_h']) > 0
        assert r['material'] in p['materials'] and r['source_quote'] is False
        for c in h.CASES:
            assert r['cost_USD'][c] == pytest.approx(sum(r['cost_breakdown_USD'][c].values()))
            assert 0 < r['mass_kg'][c] <= r['paid_stock_kg'][c]
        assert r['scrap_kg_bounds'][0] >= -1e-15


def test_washer_annulus_volume_bore_and_positive_paid_disc_scrap():
    r = h.prototype('M6-washer')['parts'][0]
    assert r['geometry']['inner_diameter_m'] == .0065
    assert r['net_volume_base_m3'] == pytest.approx(math.pi/4*(.012**2-.0065**2)*.002)
    assert r['scrap_kg_bounds'][0] > 0


def test_hex_nut_real_thread_void_bounds_and_no_supplier_grade_claim():
    p = h.prototype('M6-nut'); g = p['parts'][0]['geometry']
    assert g['thread']['major_diameter_m'] == .006 and g['thread']['pitch_m'] == .001
    assert g['minimum_material']['cuts'][0]['outer_diameter_m'] == .006
    assert g['maximum_material']['cuts'][0]['outer_diameter_m'] == .005
    assert p['parts'][0]['mass_kg']['low'] < p['parts'][0]['mass_kg']['high']


def test_locknut_counterbore_ring_and_owned_bond_are_disjoint_radial_layers():
    p = h.prototype('M8-locknut'); ps = {r['id']: r for r in p['parts']}
    assert set(ps) == {'nut', 'prevailing-ring', 'ring-retention-bond'}
    ring, bond = ps['prevailing-ring']['geometry'], ps['ring-retention-bond']['geometry']
    assert ring['outer_diameter_m'] == bond['inner_diameter_m']
    assert bond['outer_diameter_m'] == .010
    assert ring['at_m'][0] == .003 and ring['length_m'] == .002
    assert ps['nut']['geometry']['minimum_material']['cuts'][1]['outer_diameter_m'] == .010
    assert p['mating'][0]['locking_torque_Nm'] is None


def test_insert_both_threads_actual_fork_notches_and_compound_paid_once():
    p = h.prototype('M5-glazing-insert'); a, compound = p['parts']
    assert a['geometry']['external_thread']['major_m'] == .008
    assert a['geometry']['internal_thread']['major_m'] == .005
    assert len(a['geometry']['minimum_material']['cuts']) == 2
    assert compound['geometry']['exact_distribution'] is None
    assert compound['mass_kg']['low'] > 0 and p['manufactured_piece_count'] == 2


@pytest.mark.parametrize('size,projection', [('M6', .0095), ('M8', .012)])
def test_cap_closed_end_clearance_retention_and_finite_outward_sweep(size, projection):
    p = h.prototype('thread-guard', size=size); g = p['parts'][0]['geometry']
    bore = g['thread']['length_m']; cap = g['outer']['length_m']
    assert cap-bore == pytest.approx(.001)
    assert bore-projection >= .001-1e-12
    assert p['mating'][0]['retention_force_N'] is None
    s = h.finite_sweep_bounds(p, dict(at_m=[.1, 0, 0], rotation=h.REVERSE), [[0.,0.,0.],[.02,0.,0.],[.05,0.,0.]])
    assert s['min_m'][0] == pytest.approx(.1-.05-cap)
    assert s['max_m'][0] == pytest.approx(.1)
    assert s['finite_pose_count'] == 3 and s['corner_count'] == 24
    assert not s['continuous_sweep_verified'] and not s['installed_access_accepted']


def test_retainer_single_sheet_real_holes_clear_glass_edge_and_corner_weld_count_zero():
    p = h.prototype('glazing-retainer'); r = p['parts'][0];g=r['geometry']
    assert len(g['cuts']) == 13  # aperture + twelve separate bores
    assert len(h.glazing_axes()) == len(set(map(tuple,h.glazing_axes()))) == 12
    assert r['gross_blank_volume_m3'] == pytest.approx(.004*1.64*1.14)
    for y,z in h.glazing_axes():
        # point-to-fixed 1.6x1.1m rectangle distance: shank radius 2.5mm
        d = math.hypot(max(abs(y)-.8,0),max(abs(z)-.55,0))
        assert d-.0025 >= .0025-1e-12
    assert len(p['parts']) == 1


def test_cellular_seal_compression_preserves_material_mass_and_positive_waste():
    p = h.prototype('glazing-seal'); r=p['parts'][0]
    assert r['geometry']['outer']['size_m'][0] == .002
    assert r['free_shape']['outer']['size_m'][0] == .0025
    assert r['free_net_volume_m3'] == pytest.approx(r['net_volume_base_m3']*1.25)
    assert r['mass_kg']['base'] == pytest.approx(r['free_net_volume_m3']*h.MATERIALS['EPDM-cellular-unqualified']['density_kg_m3'][1])
    assert r['scrap_kg_bounds'][0] > 0


def test_bolt_fixed_glass_bond_seal_retainer_stack_has_no_hidden_length_source():
    p = h.prototype('M5-glazing-bolt'); g = p['parts'][0]['geometry']
    assert g['pieces'][0]['thread']['length_m'] == .038
    # U underhead76.5, tip38.5; source insert37.5..45.5, glass57.5..69.5
    assert .0765-.038 == pytest.approx(.0385)
    assert .0455-.0385 == pytest.approx(.007)
    assert .0515+.006 == pytest.approx(.0575)
    assert .0695+.002+.004+.001 == pytest.approx(.0765)
    assert p['mating'][0]['full_thread_after_runout_min_m'] == pytest.approx(.0057)


def synthetic_interfaces():
    """Invented nominal objects constructed here, never loaded from retained data."""
    es=[dict(id='legacy/retained-glass',exact_CSG_entity=dict(geometry=dict(kind='box',at_m=[.0635,0.,0.],size_m=[1.6,1.1,.012],rotation=[[0.,0.,1.],[1.,0.,0.],[0.,1.,0.]])))]
    holes=[]
    for n,(y,z) in enumerate(h.glazing_axes()):
        holes.append(dict(at_m=[.0455,y,z],axis=[1.,0.,0.],diameter_m=.0055,length_m=.006,kind='cylinder-cut',purpose='SYNTHETIC'))
        hp=dict(geometry=dict(kind='box',at_m=[.0395,y,z],size_m=[.012,.025,.025],rotation=deepcopy(h.I)),material='al5083',holes=[dict(kind='cylinder-cut',at_m=[.0335,y,z],axis=[1.,0.,0.],diameter_m=.006,length_m=.012,purpose='SYNTHETIC')],insert_pocket_max_depth_m=.009,insert_pocket_max_diameter_m=.010)
        es.append(dict(id='legacy/glazing-hardpoint/'+str(n),exact_CSG_entity=hp))
    ring=dict(material='al5083',geometry=dict(kind='difference',outer=dict(kind='box',at_m=[.0485,0.,0.],size_m=[.006,1.7,1.2],rotation=deepcopy(h.I)),void=dict(kind='box',at_m=[.0485,0.,0.],size_m=[.006,1.56,1.06],rotation=deepcopy(h.I))),holes=holes)
    es.append(dict(id='legacy/glazing-backing-ring',exact_CSG_entity=ring))
    return es


def test_source_cut_keeps_through_void_and_positive_new_machining_in_contained_stock():
    es=synthetic_interfaces();before=deepcopy(es);ops=h._source_volume_geometry(es)
    assert es == before and len(ops) == 13
    for op in ops[:12]:
        old,new=op['complete_void_union']['pieces']
        assert old['length_m'] == .012 and old['at_m'][0] == .0335 and old['axis'] == [1.,0.,0.]
        assert op['unchanged_original_through_void']
        assert new['at_m'][0] == .0455 and new['axis'] == [-1.,0.,0.]
        assert new['depth_m']+.0003 < .012
        assert new['depth_m']+.0003 <= op['maximum_pocket_depth_m']+1e-12
        assert op['minimum_annular_rear_web_m'] == pytest.approx(.003)
        assert op['source_credit_USD'] == 0 and op['original_paid_blank_retained']
        assert op['incremental_removed_volume_bounds_m3'][0] > 0
    ring=ops[-1]
    assert ring['blank_owner_count']==1 and ring['new_stock_purchase_count']==0 and ring['cut_count']==12
    assert len(ring['complete_void_union']['pieces'])==25
    assert ring['complete_void_union']['pieces'][0]==es[-1]['exact_CSG_entity']['geometry']['void']
    assert ring['complete_void_union']['pieces'][1:13]==es[-1]['exact_CSG_entity']['holes']
    assert all(x['diameter_m']==.012 for x in ring['complete_void_union']['pieces'][13:])


@pytest.mark.parametrize('mutation', [
    lambda e:e[0]['exact_CSG_entity']['geometry']['at_m'].__setitem__(0,.064),
    lambda e:e[1]['exact_CSG_entity'].update(insert_pocket_max_depth_m=.008),
    lambda e:e[1]['exact_CSG_entity']['holes'][0].update(diameter_m=.007),
    lambda e:e[1]['exact_CSG_entity'].update(material='SYNTHETIC-steel'),
])
def test_changed_fixed_source_interfaces_fail_before_any_builder_mutation(mutation):
    es=synthetic_interfaces();mutation(es);before=deepcopy(es)
    with pytest.raises(ValueError):h._source_volume_geometry(es)
    assert es == before


def test_cost_and_density_hypotheses_are_evaluations_not_physical_geometry():
    a=h.prototype('M6-nut');rates=deepcopy(h.RATES);rates['labour_USD_h']=[5.,10.,20.]
    b=h.prototype('M6-nut',rates=rates)
    mats=deepcopy(h.MATERIALS);mats['stainless-316L-hypothesis']['density_kg_m3']=[7800.,8050.,8300.]
    c=h.prototype('M6-nut',materials=mats)
    assert a['candidate_id'] == b['candidate_id'] == c['candidate_id']
    assert a['cost_USD'] != b['cost_USD'] and a['mass_kg'] != c['mass_kg']
    assert a['evaluation_id'] != b['evaluation_id'] != c['evaluation_id']


@pytest.mark.parametrize('bad', [[0.,1.,2.],[1.,float('nan'),3.],[1.,True,3.],[3.,2.,1.]])
def test_bad_rates_fail_before_mutating_inputs(bad):
    rates=deepcopy(h.RATES);rates['labour_USD_h']=bad;before=deepcopy(rates)
    with pytest.raises(ValueError):h.prototype('M6-washer',rates=rates)
    assert repr(rates) == repr(before)


def test_once_only_source_stock_replacement_and_no_old_price_in_new_subtotal(monkeypatch):
    monkeypatch.setattr(h,'FAMILIES',{'M6-washer':('SYNTHETIC/washer',1)})
    monkeypatch.setattr(h,'_source_volume_geometry',lambda es:[])
    e=dict(id='SYNTHETIC/front-washer',part_id='SYNTHETIC/washer',scope='installed',at_m=[0.,0.,0.],mass_kg=dict(low=.01,base=.02,high=.03),exact_CSG_entity=dict(geometry=None))
    owner=dict(id='SYNTHETIC/source-owner',entity_ids=[e['id']],direct_cost_usd=dict(low=100.,base=200.,high=300.))
    source=dict(component_proposal=dict(entities=[e],stock_groups=[owner],source_account_coverage={'SYNTHETIC-c999':'retained'}),source_accounting_retained={'SYNTHETIC-old-account':'retained'})
    before=deepcopy(source);out=h._compile(source,'b'*64,rates=h.RATES,materials=h.MATERIALS)
    assert source == before
    assert len(out['source_stock_owner_replacements']) == 1
    assert len(out['replacement_plan']) == 1 and out['replacement_plan'][0]['old_stock_group_id'] == owner['id']
    assert out['source_stock_owner_replacements'][0]['source_group'] == owner
    assert out['new_parts_cost_USD'] == out['prototypes']['M6-washer']['cost_USD']
    assert out['new_parts_cost_USD']['base'] < 200.
    assert not out['complete_installed_cost'] and not out['composition_admitted']
    assert out['workshop']['mass_kg'] is None
    assert out['occurrences'][0]['finite_swept_diagnostic']['finite_pose_count'] == 3


def test_unreviewed_actual_raw_and_missing_guard_variant_fail_without_producers():
    with pytest.raises(ValueError,match='retained'):h.propose_local(b'not retained',request_id='a'*64)
    with pytest.raises(ValueError,match='guard size'):h.prototype('thread-guard')
    with pytest.raises(ValueError):h.finite_sweep_bounds(h.prototype('M6-nut'),dict(at_m=[0,0,0],rotation=[[-1.,0,0],[0,1.,0],[0,0,1.]]),[[0,0,0],[1,0,0]])


def test_retained_h1_positive_material_witness_fails_old_ports_and_is_void_after_counted_enlargement():
    old=h.front_service_screen(access_diameter_m=.0055,diameter_tolerance_m=0.)
    new=h.front_service_screen()
    assert not old['necessary_port_screen_passed'] and new['necessary_port_screen_passed']
    assert old['radial_residuals_m']['insert_major_envelope']==pytest.approx(-.00235)
    assert old['radial_residuals_m']['retained_two_mm_fork_corner'] < -.0028
    for y,z in h.glazing_axes():
        p=[.0485,y+.00325,z]
        assert .0455 < p[0] < .0515 and abs(p[1]) < .85 and abs(p[2]) < .6
        assert not(abs(p[1])<.78 and abs(p[2])<.53)
        assert .00275+.0001 < .00325 < .0035-.0001  #0.1mm ball in both old materials
        assert .00325+.0001 < (.012-.00005)/2  #same entire ball now in an explicitly cut void
    assert new['inner_ligament_m']==pytest.approx(.018875)
    assert new['outer_ligament_m']==pytest.approx(.038875)
    assert new['radial_residuals_m']['own_hollow_fork_shaft_with_tolerance']==pytest.approx(.0001)
    assert all(v>0 for v in new['radial_residuals_m'].values())


def test_rear_and_captive_staging_are_not_claimed_repair_passes():
    c=h.support_topology_comparison()
    assert not c['rear_unmodified']['necessary_screen_passed']
    assert c['rear_unmodified']['radial_residual_including_1mm_m']==pytest.approx(-.002)
    assert not c['captive_pre_ring']['nondestructive_retained_ring_repair_demonstrated']
    assert c['front_enlarged_ports']['necessary_port_screen_passed']


def test_one_ring_owner_twelve_cuts_volume_bounds_and_original_void_union_retained():
    es=synthetic_interfaces();ops=h._source_volume_geometry(es);r=ops[-1]
    assert r['kind']=='ring-access-port-enlargement' and r['blank_owner_count']==1
    assert r['new_stock_purchase_count']==0 and r['cut_count']==12
    assert r['original_paid_blank_retained'] and r['unchanged_original_voids']
    for volume,D in zip(r['incremental_removed_volume_bounds_m3'],(.01195,.01205)):
        assert volume==pytest.approx(12*math.pi/4*(D**2-.0055**2)*.006)
    assert r['nominal_removed_centroid_m']==[.0485,0.,0.]
    for row,expected in zip(r['incremental_removed_centroid_box_m'],[[.0485,-.811125,-.561125],[.0485,.811125,.561125]]):
        assert row==pytest.approx(expected,abs=1e-12)
    assert len(r['complete_void_union']['pieces'][13:])==12
    assert min(r['person_process_h'])>0 and min(r['person_QA_h'])>0
    b=r['process_time_basis']
    assert r['person_process_h']==pytest.approx([a+12*c for a,c in zip(b['one_setup_h'],b['each_of_12_bores_h'])])
    assert r['person_QA_h']==pytest.approx([a+12*c for a,c in zip(b['one_QA_setup_h'],b['each_of_12_bores_QA_h'])])


def test_captured_service_tool_real_material_gross_net_and_staged_square_key_geometry():
    kit=h.front_service_toolkit();assert kit['piece_count']==12 and len(kit['parts'])==12
    assert kit['count_per_train']==1 and not kit['qualified']
    assert kit['tool_torque_capacity_Nm'] is None and kit['capture_capacity_N'] is None
    for p in kit['parts']:
        assert 0 < p['net_volume_bounds_m3'][0] <= p['net_volume_bounds_m3'][1] <= p['gross_blank_volume_m3']
        assert p['cost_USD']['low']>0 and p['mass_kg']['low']>0
    b=kit['necessary_mating_bounds'];g=kit['geometry']
    assert b['prong_root_inner_ligament_m']>0 and b['prong_root_outer_ligament_m']>0
    assert b['minimum_prong_root_inner_ligament_m']>0 and b['minimum_prong_root_outer_ligament_m']>0
    assert b['minimum_notch_side_clearance_m']>0 and b['minimum_notch_depth_clearance_m']>0
    assert b['collar_nearest_U_m']-b['ring_front_U_m']==pytest.approx(.019)
    assert b['capture_full_thread_minimum_hypothesis_m']==pytest.approx(.0051)
    assert g['key_square_AF_m']>g['square_AF_m']
    assert b['stud_square_to_bore_radial_clearance_bound_m']>0
    assert b['key_square_face_clearance_bound_m']>0 and b['M3_bottom_clearance_minimum_m']>0
    assert g['square_axial_span_X_m'][0] < g['key_axial_span_X_m'][0] < g['key_axial_span_X_m'][1] < g['square_axial_span_X_m'][1]
    assert b['nut_to_standoff_nominal_gap_m']>0
    assert g['headless_stud_tip_X_m']-.053==pytest.approx(g['square_axial_span_X_m'][1])
    assert g['M3_tip_X_m']-g['M3_pilot_bottom_X_m']==pytest.approx(-.001)


def test_twenty_proper_unthread_poses_then_free_extraction_not_engaged_linear_translation():
    s=h.front_service_screen();m=s['screw_motion']
    assert m['finite_pose_count']==len(m['proper_rotation_U'])==20
    for turns,d,R in zip(m['turns'],m['translation_m'],m['proper_rotation_U']):
        assert d==pytest.approx(turns*.001)
        for i in range(3):
            for j in range(3):
                assert sum(R[k][i]*R[k][j] for k in range(3))==pytest.approx(1. if i==j else 0.,abs=1e-12)
        assert R[1][1]*R[2][2]-R[1][2]*R[2][1]==pytest.approx(1.)
    assert m['translation_m'][-1]==pytest.approx(.009)
    assert not s['exact_thread_contact_verified'] and not s['complete_vehicle_sweep_verified']


def compile_tiny(monkeypatch,*,service_controls=None):
    monkeypatch.setattr(h,'FAMILIES',{'M6-washer':('SYNTHETIC/washer',1)})
    monkeypatch.setattr(h,'_source_volume_geometry',lambda es:[])
    e=dict(id='SYNTHETIC/front-washer',part_id='SYNTHETIC/washer',scope='installed',at_m=[0.,0.,0.],mass_kg=dict(low=.01,base=.02,high=.03),exact_CSG_entity=dict(geometry=None))
    owner=dict(id='SYNTHETIC/source-owner',entity_ids=[e['id']],direct_cost_usd=dict(low=100.,base=200.,high=300.))
    s=dict(component_proposal=dict(entities=[e],stock_groups=[owner],source_account_coverage={'SYNTHETIC-c999':'retained'}),source_accounting_retained={'SYNTHETIC-old-account':'retained'})
    return h._compile(s,'c'*64,rates=h.RATES,materials=h.MATERIALS,service_controls=service_controls)


def test_h2_tool_radius_clearance_and_motion_evidence_are_evaluation_only(monkeypatch):
    a=compile_tiny(monkeypatch)
    controls=deepcopy(h.SERVICE_CONTROLS);controls['tool_envelope_radius_m']=.016
    b=compile_tiny(monkeypatch,service_controls=controls)
    assert a['candidate_id']==b['candidate_id'] and a['physical_definition']==b['physical_definition']
    assert a['evaluation_id']!=b['evaluation_id']
    assert a['service_evaluation']['evaluation_id']!=b['service_evaluation']['evaluation_id']
    assert a['shared_workshop_service_kit']['lifecycle_definition_id']==b['shared_workshop_service_kit']['lifecycle_definition_id']
    controls.update(required_clearance_m=.0011,tool_insertion_m=.12)
    c=compile_tiny(monkeypatch,service_controls=controls)
    assert a['candidate_id']==c['candidate_id'] and a['evaluation_id']!=c['evaluation_id']
    assert all('tool_envelope' not in p and 'finite_motion_poses_part_m' not in p and 'required_clearance_m' not in p for p in a['physical_definition']['placements'])
    before=h._hash(a['physical_definition']);a['shared_workshop_service_kit']['parts'][0]['geometry']['cuts'].append({'kind':'SYNTHETIC-tool-only-cut'})
    assert h._hash(a['physical_definition'])==before


def test_installed_ring_cut_revision_changes_physical_identity_and_keeps_one_paid_owner(monkeypatch):
    monkeypatch.setattr(h,'FAMILIES',{'M6-washer':('SYNTHETIC/washer',1)})
    es=synthetic_interfaces()
    for e in es:e['part_id']='SYNTHETIC/context/'+e['id']
    es.append(dict(id='SYNTHETIC/front-washer',part_id='SYNTHETIC/washer',scope='installed',at_m=[0.,0.,0.],mass_kg=dict(low=.01,base=.02,high=.03),exact_CSG_entity=dict(geometry=None)))
    groups=[dict(id='SYNTHETIC/paid/'+e['id'],entity_ids=[e['id']],direct_cost_usd=dict(low=1.,base=2.,high=3.)) for e in es]
    source=dict(component_proposal=dict(entities=es,stock_groups=groups,source_account_coverage={}),source_accounting_retained={})
    a=h._compile(source,'e'*64,rates=h.RATES,materials=h.MATERIALS)
    monkeypatch.setattr(h,'RING_ACCESS_DIAMETER_M',.013)
    b=h._compile(source,'e'*64,rates=h.RATES,materials=h.MATERIALS)
    assert a['candidate_id']!=b['candidate_id']
    ring=[o for o in a['source_machining'] if o['kind']=='ring-access-port-enlargement']
    assert len(ring)==1 and ring[0]['source_stock_owner_id']=='SYNTHETIC/paid/legacy/glazing-backing-ring'
    assert ring[0]['blank_owner_count']==1 and ring[0]['new_stock_purchase_count']==0
    assert len(ring[0]['complete_void_union']['pieces'][13:])==12
    assert ring[0]['source_stock_owner_id'] in a['source_machining_stock_owners']
    assert all(o['cost_USD']['low']>0 for o in a['source_machining'])
    assert ring[0]['incremental_removed_first_moment_bounds_kg_m'][1][0]<0<ring[0]['incremental_removed_first_moment_bounds_kg_m'][1][1]
    assert a['source_machining_stock_owners'][ring[0]['source_stock_owner_id']]['id']==ring[0]['source_stock_owner_id']


def test_fork_service_tool_fields_are_not_installed_prototype_material():
    p=h.prototype('M5-glazing-insert')
    assert 'fork_driver' in p['mating'][0] and 'fork_driver' not in p['physical_definition']['mating'][0]


def test_tolerance_or_clearance_failure_is_not_relabelled_a_screen_pass():
    assert not h.front_service_screen(required_clearance_m=.002)['necessary_port_screen_passed']
    assert not h.front_service_screen(coaxial_offset_bound_m=.001)['necessary_port_screen_passed']
    with pytest.raises(ValueError):h.front_service_screen(access_diameter_m=.012,diameter_tolerance_m=.013)


def test_initial_keyed_head_trap_preserved_and_headless_staged_setup_has_clearance():
    #Oldhead enters fixed key whenunderheadX=-50mm;47.5mm shaft still
    #ends2.5mm before insert. At first thread engagement,2.5mm of head
    #is already keyed, contradicting required independent bolt rotation.
    assert -.050+.0475<0
    first_thread_underhead=-.0475
    assert first_thread_underhead-(-.050)==pytest.approx(.0025)
    kit=h.front_service_toolkit();g=kit['geometry'];b=kit['necessary_mating_bounds']
    assert (g['square_AF_m']+.000025)*math.sqrt(2)<g['through_bore_m']-.00005
    assert b['stud_square_to_bore_radial_clearance_bound_m']>0
    assert g['key_axial_span_X_m'][0]>g['square_axial_span_X_m'][0]
    assert g['key_axial_span_X_m'][1]<g['square_axial_span_X_m'][1]
    assert b['square_clocking_axial_allowance_m']==pytest.approx(.0008*.125)
    #Rear key is fitted only after stud/nutclocking, so no early fixedkey.
    assert kit['assembly'][1].startswith('Seat unkeyed fork body')
    assert kit['assembly'][3].startswith('Slide rear3.6mm square-key plate')


def test_a1_duplicate_stock_owner_ids_and_rosters_fail_before_any_emission(monkeypatch):
    monkeypatch.setattr(h,'_source_volume_geometry',lambda es:(_ for _ in ()).throw(AssertionError('must preflight before geometry')))
    e=lambda name:dict(id=name)
    for groups in ([dict(id='duplicate',entity_ids=['a']),dict(id='duplicate',entity_ids=['b'])],
                   [dict(id='one',entity_ids=['a']),dict(id='two',entity_ids=['a','b'])]):
        s=dict(component_proposal=dict(entities=[e('a'),e('b')],stock_groups=groups))
        with pytest.raises(ValueError,match='stock owner'):h._compile(s,'d'*64,rates=h.RATES,materials=h.MATERIALS)
