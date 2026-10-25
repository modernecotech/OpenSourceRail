"""Independent quantity, beam-bound and replacement ownership regressions."""
from copy import deepcopy
import json
import math

import pytest

from engineering.vehicle_optimisation import equipment as e


@pytest.fixture(scope='module')
def chassis():return e.chassis_candidates()


@pytest.fixture(scope='module')
def equipment():return e.equipment_candidates()


def test_same_stiffness_can_reverse_density_saving():
    # At fixed outer dimensions, reducing E by~3 requires substantially thicker
    # Al walls. A density-only replacement would predict a false66% saving.
    steel=e.rhs_properties(.10,.20,.004)
    t=e.same_stiffness_wall(.10,.20,[200e9*steel['I_strong_m4'],200e9*steel['I_weak_m4']])
    aluminium=e.rhs_properties(.10,.20,t)
    assert 2700*steel['area_m2'] < 7850*steel['area_m2']
    assert 2700*aluminium['area_m2'] > 7850*steel['area_m2']
    assert 69e9*aluminium['I_strong_m4'] >= 200e9*steel['I_strong_m4']*(1-1e-9)
    assert 69e9*aluminium['I_weak_m4'] >= 200e9*steel['I_weak_m4']*(1-1e-9)


def test_rhs_integral_known_and_reject_impossible_section():
    s=e.rhs_properties(.10,.20,.005)
    assert s['area_m2']==pytest.approx(.1*.2-.09*.19)
    assert s['I_strong_m4']==pytest.approx((.1*.2**3-.09*.19**3)/12)
    with pytest.raises(ValueError):e.rhs_properties(.1,.2,.06)
    with pytest.raises(ValueError):e.same_stiffness_wall(.1,.2,[1e12,1e12])


def test_all65_members_and_joint_counts(chassis):
    for c in chassis:
        assert c['member_count']==65
        assert c['member_end_count']==130
        assert c['joint_bolt_count']==520
        stock={r['id']:r for r in c['stock_parts']}
        assert stock['joints/gusset']['quantity']==260
        assert stock['joints/crush-sleeve']['quantity']==520
        assert stock['joints/GFRP-isolation']['quantity']==130
        assert stock['hardpoints/roof-spreader']['quantity']==24
        assert len(c['removed_stock_ids'])==260
        assert len(set(c['removed_stock_ids']))==260
        assert all(m['stiffness_necessary_pass'] for m in c['members'])
        for q in c['stock_parts']:
            assert q['total_mass_kg']==pytest.approx(q['volume_m3_each']*q['density_kg_m3']*q['quantity'])
        assert c['counted_material_mass_kg']==pytest.approx(sum(q['total_mass_kg'] for q in c['stock_parts']))
        assert c['installed_mass_kg'] is None and c['installed_cg_m'] is None
        assert c['unknown_installed_inventory']


def test_retained_removal_matches_exact_roles_and_leaves_hardpoints(chassis):
    from engineering.ferrite_maglev import candidate_magnetics as canonical
    raw=json.loads((e.ROOT/'engineering/ferrite_maglev/data/candidate-retained-body-stock.json').read_text())
    expected={p['id']:p for p in raw['parts'] if p['role'] in ('primary-frame','provisional-replaced-stringers')}
    exact=sum(canonical._region_mass_properties(p)[0] for p in expected.values())
    assert exact==pytest.approx(1224.0216304494938)
    for c in chassis:
        assert set(c['removed_stock_ids'])==set(expected)
        assert c['removed_counted_frame_kg']==pytest.approx(exact)
        assert not any(p['id'] in c['removed_stock_ids'] for p in raw['parts'] if p['role'] in ('magnetic-load-path','hardpoints','fasteners','panel-floor'))


def test_same_stiffness_full_chassis_not_automatically_lighter(chassis):
    assert all(c['counted_material_mass_kg']>c['removed_counted_frame_kg'] for c in chassis)
    assert len({round(c['counted_material_mass_kg'],6) for c in chassis})==3


def test_each_member_preserves_its_own_attachment_datum_without_mutating_neighbour(chassis):
    raw=json.loads((e.ROOT/'engineering/ferrite_maglev/data/candidate-retained-body-stock.json').read_text())
    groups={}
    for p in raw['parts']:
        if p['role'] in ('primary-frame','provisional-replaced-stringers'):
            groups.setdefault(p['parent_member_id'],[]).append(p)
    for c in chassis:
        for q in c['stock_parts']:
            if not q['id'].startswith('extrusion/'):continue
            ps=groups[q['source_member']]
            low=[min(p['at_m'][i] for p in ps) for i in range(3)]
            high=[max(p['at_m'][i]+p['size_m'][i] for p in ps) for i in range(3)]
            name=q['source_member']
            if 'lower-stringer' in name or 'roof-longitudinal' in name:
                assert q['at_m'][2]+q['depth_m']==pytest.approx(high[2])
                assert q['at_m'][0]==pytest.approx(low[0])
            else:
                assert q['at_m']==pytest.approx(low)
            if 'roof-longitudinal' in name:
                if high[1]<0:assert q['at_m'][1]==pytest.approx(low[1])
                else:assert q['at_m'][1]+q['width_m']==pytest.approx(high[1])


def test_roof_support_and_joint_failure_are_distinct(chassis):
    for c in chassis:
        s=c['screens']
        assert s['roof_force_N_per_module']==pytest.approx(1.3*37618.591500334303*9.80665/24)
        assert s['roof_rail_elastic_pass']
        assert not s['full_length_buckling_pass']
        assert not s['bracing_qualified']
        assert s['euler_assumed_2m_braced_N']/s['euler_full_17m_N']==pytest.approx((17/2)**2)
        assert c['physical_accepted'] is False
    first,deep,_=chassis
    assert not first['screens']['spreader_plate_elastic_pass']
    assert deep['screens']['spreader_plate_elastic_pass']
    assert first['screens']['spreader_plate_stress_pa']/deep['screens']['spreader_plate_stress_pa']==pytest.approx((.018/.008)**2)


def test_unchanged_openings_and_no_glass_double_count(equipment):
    assert len(equipment)==4
    for r in equipment:
        d,g=r['door'],r['glazing']
        assert d['door_count']==4 and d['leaves_per_door']==2
        assert (d['door_width_m'],d['door_height_m'])==(1.4,2.1)
        assert g['fixed_area_m2']==8*2*1.5==24
        assert g['door_area_m2']==8*.5*1==4
        assert g['total_area_m2']==28
        assert r['hvac_interface']['open_area_m2']==pytest.approx(2*1.4*2.1)
        assert not r['hvac_interface']['recurrence_is_headway']
        assert not r['hvac_interface']['opening_window_cooling_credit']
        assert len({x['id'] for x in r['stock_parts']})==len(r['stock_parts'])
        assert not any('glass' in x['id'] for x in r['stock_parts'] if x['id'].startswith('doors/'))
        assert r['counted_material_mass_kg']==pytest.approx(d['physical_leaf_stock_mass_kg']+g['counted_material_mass_kg'])


def test_door_mechanism_is_not_leaf_or_complete_door(equipment):
    for r in equipment:
        d=r['door']
        assert d['mechanism_reference_count']==4
        assert d['mechanism_reference_mass_kg_each'] in (41.,46.)
        assert r['material_plus_reference_subtotal_kg']==pytest.approx(r['counted_material_mass_kg']+4*d['mechanism_reference_mass_kg_each'])
        assert d['complete_door_mass_kg'] is None
        assert d['mechanism_reference_width_m']!=d['proposed_clear_width_m']
        assert not d['fit_qualified']
        assert d['complete_BODE_LRV_reference_mass_kg_each']==120


def test_glazing_volume_solar_and_retention(equipment):
    clear=equipment[0]['glazing'];solar=equipment[1]['glazing']
    assert clear['stock_parts'][0]['total_mass_kg']==pytest.approx(28*.008*2500)
    assert solar['stock_parts'][0]['total_mass_kg']==pytest.approx(28*.006*2500)
    assert solar['stock_parts'][1]['total_mass_kg']==pytest.approx(28*.00076*1070)
    assert solar['counted_material_mass_kg']<clear['counted_material_mass_kg']
    assert solar['solar_factor_g']<clear['solar_factor_g']
    assert solar['U_W_m2K']==clear['U_W_m2K']==5.7
    assert clear['retention_perimeter_m']==8*7+8*3
    assert not solar['impact_fire_scratch_retention_qualified']


def test_allocation_audit_and_ledger_close_without_body_budget(chassis,equipment):
    ledger=e.replacement_ledger(chassis[1],equipment[1])
    assert ledger['removed_allocation_kg']==1000
    assert ledger['HVAC_removal_kg']==0
    assert ledger['removed_counted_stock_kg']==pytest.approx(1224.0216304494938)
    assert ledger['retained_body_stock_kg']==pytest.approx(6113.666799604363-1224.0216304494938)
    assert ledger['conditional_AW3_subtotal_kg']==pytest.approx(ledger['original_AW3_kg']+ledger['added_counted_material_kg']+ledger['added_supplier_reference_kg']-1224.0216304494938-1000)
    assert ledger['remaining_unlocated_residual_kg']==pytest.approx(7378.253763406856-1000)
    assert ledger['installed_AW3_kg'] is None
    assert ledger['AW2_passengers']==120 and ledger['AW3_passengers']==160
    assert all(ledger['allocation_audit']['source_chain_sha_matches'].values())


def test_overlap_or_aggregate_budget_removal_refused(chassis,equipment):
    with pytest.raises(ValueError,match='double stock'):
        e.replacement_ledger(chassis[0],equipment[0],external_removed_stock_ids=[chassis[0]['removed_stock_ids'][0]])
    with pytest.raises(ValueError,match='double allocation'):
        e.replacement_ledger(chassis[0],equipment[0],external_removed_allocation_ids=['allocation/station-central/doors_kg'])
    with pytest.raises(ValueError,match='aggregate'):
        e.replacement_ledger(chassis[0],equipment[0],external_removed_allocation_ids=['structural_body_floor_doors_glazing_interior'])
    altered=deepcopy(chassis[0]);altered['removed_stock_ids'].append('nonexistent/body')
    with pytest.raises(ValueError,match='eligible'):
        e.replacement_ledger(altered,equipment[0])


def test_corrupted_proposal_mass_cannot_enter_composition(chassis,equipment):
    altered=deepcopy(chassis[0]);altered['counted_material_mass_kg']=1.
    with pytest.raises(ValueError,match='payload identity'):
        e.replacement_ledger(altered,equipment[0])


def test_allocation_source_chain_rejects_changed_budget(tmp_path):
    base='engineering/ferrite_maglev/'
    names=['data/candidate-parent-94ad.json','station-structure.toml','station_structure.py','closure.py']
    for name in names:
        dest=tmp_path/(base+name);dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_bytes((e.ROOT/(base+name)).read_bytes())
    e.allocation_audit(root=tmp_path)
    path=tmp_path/(base+'station-structure.toml')
    path.write_text(path.read_text().replace('doors_kg = 500.0','doors_kg = 501.0'))
    with pytest.raises(ValueError,match='source chain'):
        e.allocation_audit(root=tmp_path)


def test_finite_study12_samples_and_unadopted():
    r=e.study()
    assert len(r['chassis'])==3 and len(r['equipment'])==4
    assert len(r['combinations'])==r['combination_count']==12
    assert r['selected_integrated_candidate'] is None
    assert all(not x['installed_candidate_eligible'] for x in r['combinations'])
    assert r['sampled_not_global_optimum']


@pytest.mark.parametrize('mass',[True,0,-1,float('nan')])
def test_invalid_mass_refused(mass):
    with pytest.raises(ValueError):e.chassis_candidates(comparison_mass_kg_per_car=mass)
