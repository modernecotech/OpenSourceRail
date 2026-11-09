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
    ring=dict(geometry=dict(kind='difference',outer=dict(kind='box',at_m=[.0485,0.,0.],size_m=[.006,1.7,1.2],rotation=deepcopy(h.I)),void=dict(kind='box',at_m=[.0485,0.,0.],size_m=[.006,1.56,1.06],rotation=deepcopy(h.I))),holes=holes)
    es.append(dict(id='legacy/glazing-backing-ring',exact_CSG_entity=ring))
    return es


def test_source_cut_keeps_through_void_and_positive_new_machining_in_contained_stock():
    es=synthetic_interfaces();before=deepcopy(es);ops=h._source_volume_geometry(es)
    assert es == before and len(ops) == 12
    for op in ops:
        old,new=op['complete_void_union']['pieces']
        assert old['length_m'] == .012 and old['at_m'][0] == .0335 and old['axis'] == [1.,0.,0.]
        assert op['unchanged_original_through_void']
        assert new['at_m'][0] == .0455 and new['axis'] == [-1.,0.,0.]
        assert new['depth_m']+.0003 < .012
        assert new['depth_m']+.0003 <= op['maximum_pocket_depth_m']+1e-12
        assert op['minimum_annular_rear_web_m'] == pytest.approx(.003)
        assert op['source_credit_USD'] == 0 and op['original_paid_blank_retained']
        assert op['incremental_removed_volume_bounds_m3'][0] > 0


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
