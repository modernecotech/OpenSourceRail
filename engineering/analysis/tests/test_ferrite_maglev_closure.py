"""Manufactured-detail candidates: independent controls, infeasible baselines and no release."""
from hashlib import sha256
from pathlib import Path
import gzip
import json
import math
import sys

import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[3]))
from engineering.ferrite_maglev import closure as c, geometry, system_campaign


def test_body_floor_and_actual_rib_select_feasible_analytical_alternative():
    r=c.body_interfaces()
    assert not r['floor_cases'][0]['deflection']['screen_pass']
    assert r['floor_cases'][1]['deflection']['screen_pass']
    assert not r['floor_rib']['thin_80mm_rib_negative_control']['screen_pass']
    assert r['floor_rib']['bending']['screen_pass']
    assert r['floor_rib']['deflection']['screen_pass']
    assert r['hardpoint']['bolt_combined']['capacity_over_demand']==pytest.approx(1.4098740437793815)
    assert r['hardpoint']['laminate_bearing']['screen_pass']
    assert r['hardpoint']['local_pull_through']['screen_pass']
    assert r['longitudinal_members']['axial_strength']['screen_pass']
    assert not r['complete_body_mass_closed']
    assert not c.body_interfaces(load_multiplier=10)['hardpoint']['bolt_combined']['screen_pass']
    assert not c.body_interfaces(rib_span_m=4.)['floor_cases'][1]['deflection']['screen_pass']


def test_frame_family_and_growth_reserve_account_for_real_additions_once():
    r=c.primary_frame_families();families=r['families']
    assert len({x['id'] for x in families})==len(families)
    assert r['defined_member_piece_count']==63
    assert r['primary_family_mass_kg']==pytest.approx(1146.45536)
    assert r['opening_and_joint_family_mass_kg']==pytest.approx(94.888)
    assert r['frame_budget_overrun_kg']==pytest.approx(346.45536)
    reserve=r['reserve_allocation']
    assert reserve['existing_kg']==1800
    assert reserve['separately_proposed_emergency_kg']==pytest.approx(system_campaign.emergency_brake()['added_mass_kg_per_car'])
    assert reserve['remaining_before_other_system_growth_kg']==pytest.approx(1800-346.45536-system_campaign.emergency_brake()['added_mass_kg_per_car'])
    assert reserve['existing_kg']==pytest.approx(reserve['frame_overrun_kg']+reserve['separately_proposed_emergency_kg']+reserve['remaining_before_other_system_growth_kg'])
    assert not reserve['reserve_is_new_mass_credit']
    assert not r['complete_manufacturing_drawings']


def test_heavier_operating_pack_flows_through_detail_gravity_brake_and_reserve_once():
    base=c.study()['retained_30kwh_benchmark'];r=c.study();mass=26400.;ratio=mass/26200.
    assert r['primary_mass_case']['car_mass_kg']==mass
    assert r['primary_mass_case']['train_mass_kg']==158400.
    assert r['primary_mass_case']['tare_kg_per_car']==14400.
    assert base['car_mass_kg']==26200.
    assert base['emergency_brake_case']['train_mass_kg']==157200.
    assert r['body_interfaces']['maximum_cartridge_interface_force_n']==pytest.approx(base['body_interfaces']['maximum_cartridge_interface_force_n']*ratio)
    assert r['stator_interfaces']['passive_support_local_vertical_force_n']==pytest.approx(base['stator_interfaces']['passive_support_local_vertical_force_n']*ratio)
    assert r['civil_stages']['load_cases']['live_line_n_m']==pytest.approx(mass/17.*9.81)
    assert r['civil_stages']['load_cases']['dead_line_n_m']==base['civil_stages']['load_cases']['dead_line_n_m']
    brake=r['emergency_brake_case'];old=base['emergency_brake_case']
    assert brake['braking_force_n']==pytest.approx(old['braking_force_n']*ratio)
    assert brake['brake_energy_j']==pytest.approx(old['brake_energy_j']*ratio)
    assert brake['thermal_mass_kg']==pytest.approx(old['thermal_mass_kg']*ratio)
    assert brake['added_mass_kg_per_car']==pytest.approx(brake['thermal_mass_kg']/6+60.)
    reserve=r['primary_frame_families']['reserve_allocation']
    assert reserve['additional_pack_mass_already_in_tare_kg']==200.
    assert reserve['nominal_tare_including_existing_reserve_kg']==14400.
    assert reserve['remaining_before_other_system_growth_kg']==pytest.approx(1800-reserve['frame_overrun_kg']-brake['added_mass_kg_per_car'])
    path=r['emergency_and_curve_load_path'];oldpath=base['emergency_and_curve_load_path']
    assert path['car_mass_kg']==mass and path['input_brake']['train_mass_kg']==158400.
    assert path['restraint_spec']['shared_support_two_lane_longitudinal_n']==pytest.approx(brake['braking_force_n']/2)
    # Two equally loaded 25m directions add this exact gravity, without changing concrete/iron quantities.
    assert path['support']['axial_n']-oldpath['support']['axial_n']==pytest.approx(2*(26400-26200)/17*25*9.81)
    assert path['curve_case']['shared_support_lateral_n']==pytest.approx(oldpath['curve_case']['shared_support_lateral_n']*ratio)
    assert path['restraint_spec']['bearing_average_vertical_pressure_pa']>oldpath['restraint_spec']['bearing_average_vertical_pressure_pa']
    assert r['foundation_cost_delta']['car_mass_kg']==mass
    assert not r['primary_mass_case']['physical_mass_accepted']
    with pytest.raises(ValueError,match='masses differ'):
        c.emergency_load_path(brake,car_mass_kg=26200.)


@pytest.mark.parametrize('mass',[0,-1,float('nan'),float('inf'),True])
def test_detail_and_brake_reject_invalid_explicit_gross_mass(mass):
    for call in (c.body_interfaces,c.stator_interfaces,c.civil_stages,c.emergency_load_path,system_campaign.emergency_brake):
        with pytest.raises(ValueError):call(car_mass_kg=mass)


def test_stator_takeoff_counts_both_faces_both_directions_and_unmeasured_normal_force():
    r=c.stator_interfaces()
    assert r['paired_cassette_design_thrust_n']==pytest.approx(4000*104.5/72*2.5*1.5)
    assert r['quantities_per_two_direction_station']['face_cassettes']==320
    assert r['quantities_per_two_direction_station']['mount_bolts']==1280
    assert r['quantities_per_two_direction_station']['addressable_sections']==32
    assert r['bolt_shear']['screen_pass'] and r['simple_mount_bending']['screen_pass']
    assert r['required_unmeasured_stator_normal_force_n'] is None
    assert r['local_vertical_anchor_and_concrete_capacity_n'] is None
    assert not r['connection_release']
    assert not c.stator_interfaces(thrust_multiplier=10)['simple_mount_bending']['screen_pass']


def test_prestress_stages_retain_failed_end_then_resolve_gross_stress_with_debond_candidate():
    r=c.civil_stages()
    assert r['prestress_spec']['bottom_strands']==22 and r['prestress_spec']['top_strands']==4
    assert r['prestress_spec']['straight_tendon_length_m']==650
    assert r['strand_layout']['cover_screen_pass']
    assert r['strand_layout']['concrete_flow_clearance_screen_pass']
    assert r['service']['compression']['screen_pass'] and r['service']['tension']['screen_pass']
    assert r['transfer_mid']['compression']['screen_pass']
    assert not r['unmodified_end_negative_control']['tension']['screen_pass']
    # The deeper current section resolves gross end compression, while its
    # unmodified end still fails tension; the authored shallow section retains
    # both failures as a distinct negative comparison.
    authored=c.civil_stages(depth=1.8)
    assert not authored['unmodified_end_negative_control']['compression']['screen_pass']
    assert not authored['unmodified_end_negative_control']['tension']['screen_pass']
    assert r['reduced_bonded_end_candidate']['tension']['screen_pass']
    assert r['reduced_bonded_end_candidate']['compression']['screen_pass']
    q=r['load_cases']['dead_line_n_m']*1.3
    assert r['load_cases']['per_lifting_point_vertical_n']==pytest.approx(q*25/2)
    assert r['load_cases']['demould_lift_overhang_moment_nm']==pytest.approx(-q*2.5**2/2)
    assert not r['handling_spec']['release_strength_measured']
    assert not c.civil_stages(load_multiplier=4)['service']['tension']['screen_pass']
    assert c.civil_stages(depth=1.9)['service']['tension']['screen_pass']


def test_span_pad_occupancy_exact_boundary_avoids_double_count_and_covers_translation():
    assert c._maximum_span_units([0,25,50],25)['maximum_units_per_span']==1
    assert c._maximum_span_units([24,26],25)['maximum_units_per_span']==2
    positions=[car*17.5+x for car in range(6) for x in (3.5,13.5)]
    r=c._maximum_span_units(positions,25)
    assert r['maximum_units_per_span']==3
    # Independent dense translation control, separate from the event search.
    observed=0
    for step in range(2500):
        bins={}
        for position in positions:
            i=math.floor((position+step/100)/25);bins[i]=bins.get(i,0)+1
        observed=max(observed,max(bins.values()))
    assert observed==r['maximum_units_per_span']


def test_repeatable_fixed_guided_bearing_path_and_larger_footing_are_conditional_feasible():
    r=c.emergency_load_path()
    assert r['restraint_spec']['fixed_bearings_per_beam']==1
    assert r['restraint_spec']['guided_bearings_per_beam']==1
    assert r['span_pad_occupancy']['maximum_units_per_span']==3
    assert r['restraint_spec']['fixed_bearing_design_longitudinal_n']==pytest.approx(system_campaign.emergency_brake()['braking_force_n']/4)
    assert r['restraint_spec']['shared_support_two_lane_longitudinal_n']==pytest.approx(system_campaign.emergency_brake()['braking_force_n']/2)
    assert r['restraint_spec']['bolt_shear_only']['screen_pass']
    assert r['support']['assumed_linear_interaction']['screen_pass']
    assert not r['single_support_full_train_negative_control']['pressure_screen_pass']
    assert not r['footing_cases'][0]['screen_pass']
    selected=r['conditional_foundation_candidate']
    assert selected['square_side_m']==6.5
    assert selected['minimum_pressure_pa']>=0 and selected['maximum_pressure_pa']<150000
    assert selected['sliding']['screen_pass']
    assert r['qualified_foundation_selection'] is None
    assert not selected['ground_or_structural_acceptance']
    assert r['support']['longitudinal_bar_length_m']==192
    assert r['support']['longitudinal_bar_mass_kg']>r['support']['net_mass_above_gross_concrete_assumption_kg']>0


def test_emergency_clamp_does_not_reuse_failed_thin_reaction_plate_or_claim_curve_clearance():
    r=c.emergency_load_path()
    for rail in r['clamp_rail_cases']:
        assert not rail['existing_unstiffened_iron_negative_control']['screen_pass']
        assert rail['dedicated_reaction_box']['screen_pass']
        assert rail['pad_bearing']['screen_pass']
        assert rail['local_concrete_anchor_capacity_n'] is None
        assert not rail['thermal_wear_magnetic_and_fault_qualification']
    curve=r['curve_case']
    assert curve['lateral_acceleration_m_s2']==pytest.approx((25/3.6)**2/100)
    assert curve['rigid_12m_chord_sagitta_m']==.18
    assert curve['car_chord_arc_index_difference_m']>.02
    assert curve['car_chord_arc_electrical_phase_degrees']>10
    assert not curve['rigid_array_clearance_accepted']
    huge=c.emergency_load_path({'braking_force_n':1e8})
    assert huge['conditional_foundation_candidate'] is None
    assert not huge['support']['assumed_linear_interaction']['screen_pass']


def test_foundation_quantity_cost_delta_prices_larger_candidate_without_charging_original_twice():
    r=c.foundation_cost_delta()
    assert r['quantity_basis']['baseline_footing_concrete_m3']==16.2
    assert r['quantity_basis']['proposed_footing_concrete_m3']==pytest.approx(33.8)
    assert r['quantity_basis']['extra_reinforcement_kg']==pytest.approx(3168)
    assert r['quantity_basis']['extra_excavation_m3']==pytest.approx(31.2)
    assert r['incremental_support_allowance_usd']==pytest.approx(8911.2)
    assert r['proposed_support_allowance_usd']==pytest.approx(30911.2)
    assert r['incremental_ordinary_route_km_allowance_usd']==pytest.approx(356448)
    assert r['complete_installed_support_price_usd'] is None
    assert not r['costs_are_supplier_quotes']


def test_coupler_has_target_stiffness_at_force_with_compression_guides_and_explicit_material_gate():
    r=c.coupler_detail()
    assert r['rod_assembly_stiffness_n_m']==pytest.approx(2*200e9*(math.pi*.03**2/4)/2.8)
    assert 90e6<r['rod_assembly_stiffness_n_m']<110e6
    assert r['peak_elastic_extension_m']<.0011
    assert r['assumed_operating_force_envelope_n']==100000
    assert 'ASSUMED' in r['source_peak_note']
    assert r['design_force_n']==500000
    for key in ('rod_stress','end_thread_tension','double_shear_pin','double_fork_bearing','guided_compression'):
        assert r[key]['screen_pass']
    assert not r['unsupported_compression_negative_control']['screen_pass']
    assert not r['full_assembly_stiffness_qualified']
    assert not r['body_and_pin_compliance_included']
    assert not c.coupler_detail(peak_force_n=1e6)['rod_stress']['screen_pass']


def test_all_obligations_have_concrete_deliverables_with_current_evidence_or_explicit_gaps():
    r=c.obligations()
    assert r['requirement_count']==179 and r['system_count']==53
    assert len({row['id'] for row in r['requirements']})==179
    assert len([row for row in r['requirements'] if row['id'].startswith('SP-')])==100
    for row in r['requirements']:
        assert row['deliverable_ids'] and row['concrete_deliverables'] and row['missing_evaluators_or_external_tests']
        assert row['retained_evidence'] and not row['accepted']
        assert all(not evidence['engineering_acceptance'] for evidence in row['retained_evidence'])
    assert all(not row['complete_production_specification'] for row in r['systems'])


def test_native_frame_and_connection_stock_agree_with_counted_members():
    d=c.definition();frame=c.primary_frame_definition()
    assert len(frame['parts'])==63
    assert len({row['id'] for row in d['parts']})==len(d['parts'])
    native=sum(geometry.volume(p)*{'gfrp':1900,'aluminium':2700}[p['material']] for p in frame['parts'])
    mass=sum(row['total_mass_kg'] for row in c.primary_frame_families()['families'] if 'cut_length_m' in row)
    assert native==pytest.approx(mass)
    assert len([p for p in d['parts'] if p['id'].startswith('bearing/anchor-')])==8
    assert len([p for p in d['parts'] if p['id'].startswith('coupler/compression-guide-') and p['id']!='coupler/compression-guide-envelope'])==11
    assert all(geometry.volume(p)>0 for p in d['parts'])


def test_packet_semantic_verification_rejects_rehashed_false_completion(tmp_path):
    packet=tmp_path/'packet';assert c.publish(packet)['requirements']==179
    raw=json.loads(gzip.decompress((packet/'dossier.json.gz').read_bytes()))
    assert raw['complete_manufactured_system'] is False
    raw['closure']['accepted_requirements']=179
    data=gzip.compress(c._encoded(raw),mtime=0);(packet/'dossier.json.gz').write_bytes(data)
    manifest=json.loads((packet/'manifest.json').read_text())
    manifest['files_sha256']['dossier.json.gz']=sha256(data).hexdigest()
    (packet/'manifest.json').write_bytes(c._encoded(manifest))
    with pytest.raises(ValueError,match='calculated'):
        c.verify(packet)


def test_packet_inventory_and_unqualified_materials_cannot_be_bypassed(tmp_path,monkeypatch):
    packet=tmp_path/'packet';c.publish(packet);(packet/'foreign').write_text('keep')
    with pytest.raises(ValueError,match='owned'):
        c.publish(packet)
    inputs=tmp_path/'closure.toml';inputs.write_text(c.INPUT.read_text().replace('material_properties_qualified = false','material_properties_qualified = true'))
    monkeypatch.setattr(c,'INPUT',inputs)
    with pytest.raises(ValueError,match='no qualified'):
        c.load()


def _native_evidence_fixture(tmp_path,monkeypatch):
    root=tmp_path/'repository';folder=root/'docs/design-engine/ferrite-maglev/native';folder.mkdir(parents=True)
    sources={
        'ferrite-maglev-study.toml':'primary configuration',
        'engineering/ferrite_maglev/geometry.py':'geometry generator',
        'engineering/factory_examples/native.py':'native exporter',
    }
    for name,text in sources.items():
        path=root/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text)
    (folder/'model.FCStd').write_bytes(b'bounded retained native payload')
    digest=lambda name:sha256((root/name).read_bytes()).hexdigest()
    value=dict(schema='osr-maglev-native-packet/1',
        geometry_sources_sha256={'ferrite-maglev-study.toml':digest('ferrite-maglev-study.toml')},
        geometry_sha256=digest('engineering/ferrite_maglev/geometry.py'),
        exporter_sha256=digest('engineering/factory_examples/native.py'),
        files_sha256={'model.FCStd':sha256((folder/'model.FCStd').read_bytes()).hexdigest()},
        physical_release=False,manufacturing_release=False)
    receipt=folder/'manifest.json';receipt.write_text(json.dumps(value))
    monkeypatch.setattr(c,'ROOT',root)
    return root,receipt,value


def test_native_evidence_reads_geometry_and_exporter_schema_without_recursive_verifier(tmp_path,monkeypatch):
    _native_evidence_fixture(tmp_path,monkeypatch)
    row=c._evidence()['native']
    assert row['state']=='current-retained-digital-records'
    assert row['source_and_payload_consistent']
    assert row['engineering_acceptance'] is False


@pytest.mark.parametrize('changed',['ferrite-maglev-study.toml','engineering/ferrite_maglev/geometry.py','engineering/factory_examples/native.py'])
def test_native_evidence_rejects_configuration_geometry_or_exporter_source_change(tmp_path,monkeypatch,changed):
    root,_,_=_native_evidence_fixture(tmp_path,monkeypatch)
    (root/changed).write_text('changed source')
    row=c._evidence()['native']
    assert row['state']=='stale-or-incomplete'
    assert not row['source_and_payload_consistent']


def test_unknown_evidence_schema_holds_despite_matching_payload_receipts(tmp_path,monkeypatch):
    _,receipt,value=_native_evidence_fixture(tmp_path,monkeypatch)
    value['schema']='unrecognised-evidence/99';receipt.write_text(json.dumps(value))
    row=c._evidence()['native']
    assert row['state']=='hold-unknown-receipt-schema'
    assert not row['source_and_payload_consistent']
    assert not row['engineering_acceptance']


def test_exact_executed_coupler_force_is_distinct_from_assumed_design_envelope(monkeypatch):
    monkeypatch.setattr(c,'_corridor_force_reference',lambda:dict(maximum_peak_force_n=80688.54,state='current-executed-corridor-reference'))
    r=c.coupler_detail()
    assert r['exact_executed_peak_pair_force_n']==80688.54
    assert r['assumed_operating_force_envelope_n']==100000
    assert r['operating_force_envelope_screen_pass']
    assert r['design_force_n']==500000
    monkeypatch.setattr(c,'_corridor_force_reference',lambda:dict(maximum_peak_force_n=100001.,state='current-executed-corridor-reference'))
    r=c.coupler_detail()
    assert not r['operating_force_envelope_screen_pass']
    assert r['operating_force_evidence_state']=='hold-exact-force-exceeds-assumed-envelope'
    assert not r['manufacturing_release']
