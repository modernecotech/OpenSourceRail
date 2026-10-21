"""Independent material/load controls and cross-language no-authority evidence."""
from pathlib import Path
import gzip
import json
import math
import shutil
import sys
import pytest
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
from engineering.ferrite_maglev import system_development as system,geometry,model


def test_entry_voids_and_holes_are_not_solid_material_or_a_complete_chute():
    r=system.entry_geometry()
    assert len(r['parts'])==20 and len({p['id'] for p in r['parts']})==20
    shell=[p for p in r['parts'] if p['id'].startswith('cassette/')]
    a=system.load()['mechanical'];w=a['door_clear_width_m']+2*a['frame_section_m'];d=a['cassette_depth_m'];h=a['cassette_height_m'];t=a['cassette_panel_m']
    assert sum(p['volume_m3'] for p in shell)==pytest.approx(w*d*h-(w-2*t)*(d-2*t)*(h-2*t))
    assert sum(len(p.get('holes',[])) for p in r['parts'])==8
    assert r['complete_module_mass_kg'] is None and not r['deployable_mechanism_defined']
    assert not r['normal_travel_envelope_accepted'] and not r['manufacturing_release']


def test_entry_standoff_tradeoff_retains_collision_and_added_hardware_mass():
    r=system.study();v=r['mechanical_variants']
    assert len(v)==4 and not v[0]['chute_path_clear_of_modelled_structure']
    assert all(v[i]['partial_hardware_mass_kg']<v[i+1]['partial_hardware_mass_kg'] for i in range(3))
    assert all(c['complete_module_mass_kg'] is None and not c['accepted'] for c in v)


def test_interior_support_counts_two_half_spans_and_preserves_equilibrium():
    r=system.support_demands();cfg=system.load();_,c,_=model.load();g=9.81
    # Two directions of 25m tributary box/rail plus AW3 vehicle UDL; no duplicate full bays.
    native=geometry.civil_bay();beam=sum(p['modelled_mass_kg'] for p in native['parts'] if p['id'].startswith('beam-1/'))
    walk=sum(p['modelled_mass_kg'] for p in native['parts'] if p['id'].startswith('walkway-1-'))
    expected_track=(beam+walk+(14200+12000)*25/17)*g
    assert r['track_vertical_reactions_n']==pytest.approx([expected_track]*2)
    cap_mass=(1*5*.9+2*.5*1*.9)*2500
    assert r['column_top_axial_n']==pytest.approx(2*expected_track+cap_mass*g)
    assert r['transverse_eccentric_moment_nm']==0
    bare=system.support_demands(walkway=False)
    assert r['column_top_axial_n']-bare['column_top_axial_n']==pytest.approx(14940*g)
    assert r['soil_bearing_limit_pa'] is r['capacity_utilisation'] is r['approved_dimension_reduction'] is None


def test_asymmetric_construction_is_not_a_symmetric_empty_or_operating_case():
    r=system.support_demands(load_case='one-beam-erection')
    assert r['track_vertical_reactions_n'][1]==0
    assert abs(r['transverse_eccentric_moment_nm'])==pytest.approx(r['track_vertical_reactions_n'][0]*1.9)
    cases=system.study()['support_cases'];cfg=system.load()['civil']
    expected=math.prod(len(cfg[key]) for key in ('column_scales','foundation_scales','cap_scales'))*2*4*(len(cfg['additional_equipment_mass_screens_kg_per_car'])+1)
    assert len(cases)==expected
    assert {v['load_case'] for v in cases}=={'empty','both-trains','one-train','one-beam-erection'}
    assert any(not v['compression_only_linear_contact_admissible'] for v in cases)
    assert all(v['capacity_utilisation'] is None and not v['accepted'] for v in cases)


def test_reducing_support_size_can_increase_demand_without_being_a_saving():
    large=system.support_demands(load_case='one-train');small=system.support_demands(column_scale=.6,foundation_scale=.7,load_case='one-train')
    assert small['support_modelled_concrete_mass_kg']<large['support_modelled_concrete_mass_kg']
    assert max(small['column_nominal_extreme_stress_pa'])>max(large['column_nominal_extreme_stress_pa'])
    assert max(small['rectangular_footing_linear_contact_pa'])>max(large['rectangular_footing_linear_contact_pa'])
    extra=system.support_demands(additional_equipment_kg_per_car=600)
    assert extra['column_top_axial_n']-system.support_demands()['column_top_axial_n']==pytest.approx(2*600/17*25*9.81)
    assert system.study()['erection_working_days_saved'] is None
    derived=system.study()['entry_partial_material_mass_kg_per_car']
    assert any(v['additional_equipment_mass_sensitivity_kg_per_car']==derived for v in system.study()['support_cases'])


@pytest.mark.parametrize('before,after',[
 ('mechanical_strength_verified = false','mechanical_strength_verified = true'),
 ('frame_wall_m = 0.004','frame_wall_m = 0.08'),
 ('column_scales = [1.0, 0.8, 0.6]','column_scales = [0.1]'),
])
def test_unproved_capacity_and_invalid_dimensions_are_rejected(monkeypatch,tmp_path,before,after):
    p=tmp_path/'system.toml';p.write_text(system.INPUT.read_text().replace(before,after));monkeypatch.setattr(system,'INPUT',p)
    with pytest.raises(ValueError):system.load()


def test_current_native_and_rust_packet_have_exact_identities_and_negative_controls():
    manifest=system.verify();assert not manifest['manufacturing_release']
    raw=json.loads((system.OUTPUT/'software-replay.json').read_text())
    cases={v['id']:v for v in raw['cases']}
    assert cases['outward-20m']['replay']['frames'][-1]['phase']=='CompleteHold'
    for key in ('inward-clash','height-gap-10m','road-landing'):
        assert all(v['phase'] not in {'Ready','DeploymentStudy','FlowStudy','CompleteHold'} for v in cases[key]['replay']['frames'])
    matched=json.loads((system.OUTPUT/'native-derived-coupling.json').read_text())
    assert matched['native_beam_line_mass_kg_m']==pytest.approx((.54+.72/25)*2500+300.23424)
    assert matched['replay']['beam_assumptions']['line_mass_kg_m']==matched['native_beam_line_mass_kg_m']
    assert matched['complete_egress_system_included'] is False
    assert matched['car_mass_kg']==pytest.approx(23200+system.study()['entry_partial_material_mass_kg_per_car'])
    assert matched['replay']['car_mass_kg']==matched['car_mass_kg']
    for folder in ('entry','compact-support'):
        r=json.loads((system.OUTPUT/folder/'native-cad.json').read_text())
        assert r['fcstd_reopened'] and r['step_reopened']
        mesh=json.loads(gzip.decompress((system.OUTPUT/folder/'native-mesh.json.gz').read_bytes()))
        definition=json.loads((system.OUTPUT/folder/'definition.json').read_text())
        mass=sum(p['volume_m3']*geometry.MATERIALS[p['material']] for p in mesh['parts'])
        assert mass==pytest.approx(definition['modelled_material_mass_kg'],rel=1e-8)


def test_system_packet_rejects_tampered_or_extra_files(tmp_path):
    output=tmp_path/'packet';shutil.copytree(system.OUTPUT,output)
    (output/'extra.json').write_text('{}')
    with pytest.raises(ValueError,match='inventory'):system.verify(output)
    (output/'extra.json').unlink();(output/'software-replay.json').write_text('{}')
    with pytest.raises(ValueError,match='file differs'):system.verify(output)


def test_rehashed_software_payload_cannot_claim_physical_authority(tmp_path):
    from hashlib import sha256
    output=tmp_path/'packet';shutil.copytree(system.OUTPUT,output)
    p=output/'software-replay.json';r=json.loads(p.read_text());r['cases'][0]['replay']['physical_output_authorised']=True
    p.write_bytes(system.encoded(r));m=json.loads((output/'manifest.json').read_text());m['files_sha256']['software-replay.json']=sha256(p.read_bytes()).hexdigest()
    (output/'manifest.json').write_bytes(system.encoded(m))
    with pytest.raises(ValueError,match='authority'):system.verify(output)
