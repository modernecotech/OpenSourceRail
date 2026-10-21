"""Fixed booster quantities and priced recovery alternatives, with failed controls."""
from hashlib import sha256
from pathlib import Path
import gzip
import json
import math
import sys

import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[3]))
from engineering.ferrite_maglev import booster_kit as b,booster_native,geometry
from engineering.factory_examples import models


def test_booster_counts_faces_sections_and_mount_stock_without_counting_passenger_stations():
    primary=b.takeoff()
    assert primary['face_cassettes']==600 and primary['mount_bolts']==2400 and primary['addressable_sections']==60
    r=b.takeoff(300.,2)
    assert r['face_cassettes']==480 and r['mount_bolts']==1920
    assert r['addressable_sections']==48 and r['face_metres']==1200
    assert r['material_quantities']['mount_plate_steel_kg']==pytest.approx(4*300*.12*.012*7850)
    assert r['material_quantities']['cabinet_pad_concrete_m3']==pytest.approx(3.6)
    assert r['passenger_station'] is False
    assert r['additional_ordinary_beams_credited']==0
    assert r['winding_core_cooling_and_power_hardware_mass_kg'] is None
    assert r['complete_installed_cost_usd'] is None
    partial=b.takeoff(301.,1)
    assert partial['face_cassettes']==2*math.ceil(301/2.5)
    assert sum(partial['cassette_lengths_per_face_m'])==301
    assert partial['cassette_lengths_per_face_m'][-1]==1
    assert not r['physical_release']


def test_spatial_reaction_allocation_and_signed_equilibrium_at_actual_span_boundaries():
    r=b.span_reactions([dict(chainage_m=0.,force_n=100.),dict(chainage_m=24.999,force_n=-25.),dict(chainage_m=25.,force_n=200.)])
    assert r['fixed_bearing_reactions_n']=={'0':-75.,'1':-200.}
    assert r['total_applied_force_n']==275 and r['equilibrium_residual_n']==0
    assert not r['connection_accepted']
    with pytest.raises(ValueError):b.span_reactions([dict(chainage_m=-.1,force_n=2.)])


def test_equivalent_heat_integrates_repeated_duty_without_fabricating_temperature():
    r=b.electrical_duty([dict(time_s=0.,current_a=100.,resistance_ohm=.1),dict(time_s=10.,current_a=100.,resistance_ohm=.1)],headway_s=100.)
    assert r['equivalent_copper_heat_j']==10000 and r['mean_repeated_copper_heat_w']==100
    assert r['winding_temperature_c'] is None and not r['thermal_acceptance']
    with pytest.raises(ValueError):b.electrical_duty([dict(time_s=1.,current_a=1.,resistance_ohm=1.)]*2,headway_s=100.)


def test_five_km_recovery_retains_failing_midpoint_only_and_calculates_feasible_alternatives():
    dense=b.recovery();mid=b.recovery(post_spacing_m=2500.)
    faster=b.recovery(post_spacing_m=2500.,speed_m_s=1.)
    bigger=b.recovery(post_spacing_m=2500.,pack_kwh=50.)
    assert dense['maximum_unobstructed_towing_reach_m']==500
    assert dense['rescue_node_count_including_endpoints']==6
    assert dense['battery_margin_kwh_per_car']==pytest.approx(2.4833333333333343)
    assert dense['numerical_feasible']
    assert mid['recovery_time_s']==3100 and not mid['battery_energy_screen_pass']
    assert mid['battery_margin_kwh_per_car']==pytest.approx(-3.7666666666666675)
    assert faster['numerical_feasible'] and bigger['numerical_feasible']
    assert faster['winch_candidate_input_rating_kw']>mid['winch_candidate_input_rating_kw']
    assert faster['listed_kit_target_usd']>mid['listed_kit_target_usd']
    assert bigger['pack_mass_increment_kg_per_car']==200
    assert bigger['gross_train_mass_if_other_allocations_held_kg']>mid['gross_train_mass_if_other_allocations_held_kg']
    assert bigger['working_line_pull_n']>mid['working_line_pull_n']
    assert len(b.recovery_cases())==12
    shorter=b.recovery(cars=3)
    assert shorter['cars']==3 and shorter['working_line_pull_n']<dense['working_line_pull_n']
    assert shorter['gross_train_mass_if_other_allocations_held_kg']*2==pytest.approx(dense['gross_train_mass_if_other_allocations_held_kg'])



def test_operational_incoming_energy_uses_actual_dwell_and_connected_fraction():
    r=b.recovery(distance_m=5000.,runtime_s=375.,dwell_s=96.,connected_fraction=.75)
    assert r['disconnected_dwell_s']==24
    assert r['incoming_hot_services_kwh_per_car']==pytest.approx(60*(375+24)/3600)
    assert r['battery_margin_kwh_per_car']==pytest.approx(14.4-6.65-15*(600+500/.5)/3600)
    with pytest.raises(ValueError):b.recovery(connected_fraction=1.1)

def test_catalogue_rope_reduction_termination_drum_and_structural_path_have_independent_controls():
    r=b.recovery();rope=r['rope'];drum=r['drum']
    assert rope['capacity_after_project_factors_n']==pytest.approx(1010000*.8/5)
    assert rope['screen_pass'] and not rope['negative_control_pass']
    assert rope['shorter_diameter_negative_control_capacity_n']==pytest.approx(721000*.8/5)
    assert not rope['assembly_accepted'] and not rope['uk_manufacture_confirmed']
    volume=math.pi*.038**2/4*r['quantities']['rope_m']/.75
    assert (drum['rope_pack_outer_diameter_m']**2-drum['core_diameter_m']**2)*math.pi/4*drum['width_m']==pytest.approx(volume)
    assert drum['shaft_shear_pa']==pytest.approx(16*drum['holding_design_torque_nm']/(math.pi*.22**3))
    assert drum['shaft_screen_pass'] and r['portal']['screen_pass'] and r['anchors']['steel_screen_pass']
    assert not r['anchors']['concrete_breakout_bond_and_pedestal_accepted']
    assert not r['foundation_cases'][0]['screen_pass']
    assert r['conditional_foundation']['screen_pass']
    assert r['conditional_foundation']['minimum_pressure_pa']>=0
    assert r['qualified_foundation_selection'] is None


def test_cost_and_mass_rows_count_complete_selected_standalone_quantities_without_free_colocation():
    r=b.recovery();q=r['quantities']
    assert q['rope_kg']==pytest.approx(q['rope_m']*6.16)
    assert q['reinforcing_kg']==pytest.approx(q['foundation_concrete_m3']*180)
    assert r['listed_kit_target_usd']==pytest.approx(sum(x['quantity']*x['rate'] for x in r['cost_rows']))
    assert all(not x['supplier_quote'] for x in r['cost_rows'])
    assert r['complete_installed_price_usd'] is None and not r['costs_are_quotes']
    assert not r['physical_rescue_accepted']


def test_partial_native_frame_drum_and_anchor_stock_reconcile_counted_materials():
    d=b.definition();r=b.recovery();parts=d['parts']
    assert len({p['id'] for p in parts})==len(parts)
    portal=[p for p in parts if p['id'].startswith(('rescue/portal-leg-','rescue/tie-','rescue/brace-cut-stock-'))]
    assert len(portal)==2+r['portal']['tie_count']+r['portal']['brace_count']
    assert sum(models.volume(p)*7850 for p in portal)==pytest.approx(r['quantities']['portal_structural_steel_kg'])
    drum=[p for p in parts if p['id'].startswith('rescue/drum-')]
    assert sum(models.volume(p)*7850 for p in drum)==pytest.approx(r['quantities']['drum_and_shaft_kg'])
    anchors=[p for p in parts if p['id'].startswith('rescue/anchor-')]
    assert len(anchors)==16
    assert all(models.volume(p)>0 for p in parts)
    assert not d['complete_kit_modelled'] and not d['interference_roles'] and d['modelled_cg_m'] is None
    actual=booster_native.definition()
    assert len(actual['parts'])==len(parts) and actual['complete_body_or_system_modelled'] is False
    assert 'closure.py' not in [p.name for p in b.source_paths()]


def test_packet_semantics_reject_rehashed_fabricated_recovery_acceptance(tmp_path):
    out=tmp_path/'kit';b.publish(out)
    r=json.loads(gzip.decompress((out/'result.json.gz').read_bytes()))
    failed=next(x for x in r['suburban_5km_300s_recovery_cases'] if not x['numerical_feasible'])
    failed['numerical_feasible']=True
    raw=gzip.compress(b._encoded(r),mtime=0);(out/'result.json.gz').write_bytes(raw)
    m=json.loads((out/'manifest.json').read_text());m['files_sha256']['result.json.gz']=sha256(raw).hexdigest();(out/'manifest.json').write_bytes(b._encoded(m))
    with pytest.raises(ValueError,match='calculation'):b.verify(out)


def test_inventory_and_unqualified_inputs_cannot_be_promoted(tmp_path,monkeypatch):
    with pytest.raises(ValueError):b.takeoff(-1)
    with pytest.raises(ValueError):b.recovery(post_spacing_m=10000)
    p=tmp_path/'kit.toml';p.write_text(b.INPUT.read_text().replace('magnetic_booster_map_accepted = false','magnetic_booster_map_accepted = true'))
    monkeypatch.setattr(b,'INPUT',p)
    with pytest.raises(ValueError,match='unaccepted'):b.load()
