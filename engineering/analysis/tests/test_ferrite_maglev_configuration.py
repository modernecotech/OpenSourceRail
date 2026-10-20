"""Cross-path quantities, source invalidation and configuration regressions."""
from copy import deepcopy
from pathlib import Path
import sys
import pytest
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
from engineering.ferrite_maglev import model,geometry,cities,coupled,configuration,system_development as system,requirements


def test_rail_quantities_are_identical_and_density_change_propagates(monkeypatch):
    c=model.load()[1];q=geometry.guideway_quantities()
    assert q['magnetic_rail_line_mass_kg_m']==pytest.approx(300.23424)
    assert model.civil_case(c,.8,1.6,25)['magnetic_quantities']==q
    assert coupled.BeamAssumptions().line_mass_kg_m==q['total_line_mass_kg_m']
    old=system.support_demands(load_case='empty',walkway=False)['track_vertical_reactions_n'][0]
    monkeypatch.setitem(geometry.MATERIALS,'steel',2*7850.)
    new=geometry.guideway_quantities();r=model.civil_case(c,.8,1.6,25)
    assert new['magnetic_rail_mass_kg']==pytest.approx(2*q['magnetic_rail_mass_kg'])
    assert r['dead_line_mass_kg_m']==pytest.approx(new['total_line_mass_kg_m']+300)
    assert coupled.BeamAssumptions().line_mass_kg_m==new['total_line_mass_kg_m']
    assert system.support_demands(load_case='empty',walkway=False)['track_vertical_reactions_n'][0]-old==pytest.approx(q['magnetic_rail_mass_kg']*9.81)


def test_span_changes_native_mass_reactions_and_support_density():
    c=model.load()[1];d=deepcopy(c);d['civil']['reference_span_m']=30
    a=system.support_demands(load_case='empty',_context=(system.load(),c))
    b=system.support_demands(load_case='empty',_context=(system.load(),d))
    assert b['track_vertical_reactions_n'][0]/a['track_vertical_reactions_n'][0]==pytest.approx(1.2)
    for span in (25,30):
        native=geometry.civil_bay(span)
        beam=sum(p['modelled_mass_kg'] for p in native['parts'] if p['id'].startswith('beam-1/'))
        assert beam==pytest.approx(geometry.guideway_quantities(span)['total_line_mass_kg_m']*span)
        assert model.civil_case(c,.8,1.6,span)['shared_piers_per_route_km']==pytest.approx(1000/span)


def test_thickness_configuration_changes_mass_and_city_dependency(monkeypatch,tmp_path):
    old=geometry.guideway_quantities()
    p=tmp_path/'selected.toml';p.write_text(configuration.INPUT.read_text().replace('rail_thickness_m = 0.02','rail_thickness_m = 0.03'))
    monkeypatch.setattr(configuration,'INPUT',p)
    assert geometry.guideway_quantities()['magnetic_rail_mass_kg']==pytest.approx(1.5*old['magnetic_rail_mass_kg'])
    assert Path(geometry.__file__) in cities.calculation_dependencies() and p in cities.calculation_dependencies()


def test_city_package_geometry_hash_change_is_detected(monkeypatch):
    original=cities.digest
    geometry_name=Path(geometry.__file__).resolve()
    monkeypatch.setattr(cities,'digest',lambda path: '0'*64 if Path(path).resolve()==geometry_name else original(path))
    result=cities.verify_index()
    assert not result['current']
    assert any('geometry.py' in error for error in result['errors'])


def test_six_car_configuration_and_conditional_walkway_requirement():
    cfg=configuration.selected()
    assert cfg.formation.body_sum_m==102 and cfg.formation.devices==36
    with pytest.raises(ValueError):configuration.selected(cars=3)
    r=requirements.register();rows={v['id']:v for v in r['requirements']}
    assert len(rows)==79 and not r['walkway_removal_approved']
    assert not rows['CIV-004']['alternative_selected'] and not rows['CIV-004']['superseded_by']
    assert set(rows['CIV-004']['alternative_requirement_ids'])=={i for i in rows if i.startswith('EVAC-')}
    assert all(not row['accepted'] and not row['evidence_links'] for row in rows.values())


def test_station_tracks_six_bodies_full_arm_and_actual_lift_opening():
    from engineering.ferrite_maglev import reference_assembly as r
    s=r.station();assert len(s['cars'])==6 and len(s['door_interfaces'])==36
    assert s['nominal_body_length_m']==102 and s['platform_length_m']>s['assumed_overall_train_length_m']>102
    assert s['lift_centre_xy_m']==[0.,0.] and s['lift_threshold_step_m']==0
    assert s['clear_passage_each_lift_side_m']>1
    assert s['arm_to_platform_horizontal_clearance_m']==pytest.approx(.1)
    assert s['body_to_platform_horizontal_gap_m']>s['arm_to_platform_horizontal_clearance_m']
    assert s['passenger_bridge_plate_required'] and not s['normal_floor_gap_accepted']
    assert s['charging_kw_per_train']==3600
    assert s['beam_unit_length_m']<=configuration.selected().civil.span_m
    assert s['manufactured_bays_per_direction']*s['beam_unit_length_m']==pytest.approx(s['platform_length_m'])
    for p in s['parts']:
        if p['id'].startswith('platform/'):
            # No platform material occupies the lift opening.
            x,y,z=p['at_m'];dx,dy,dz=p['size_m']
            assert x+dx<=-1 or x>=1 or y+dy<=-1 or y>=1


def test_height_family_propagates_mass_loads_slenderness_and_descent_height():
    from engineering.ferrite_maglev import reference_assembly as r
    rows=r.study()['pier_height_families']
    assert [v['pier_height_m'] for v in rows]==[8,12,20,30]
    assert all(a['demands']['column_base_axial_n']<b['demands']['column_base_axial_n'] for a,b in zip(rows,rows[1:]))
    assert rows[-1]['demands']['column_geometric_slenderness'][0]>rows[0]['demands']['column_geometric_slenderness'][0]
    assert rows[-1]['door_sill_to_ground_m']==pytest.approx(33.1)
    assert all(not row['foundation_selected'] and row['installed_cost_usd'] is None for row in rows)


def test_emergency_energy_accounts_phases_and_missing_power_holds_reserve():
    from engineering.ferrite_maglev import reference_assembly as r
    a=r.emergency_energy({'stop':60,'flow':600},{'support':{'stop':30,'flow':30},'comms':{'stop':1,'flow':1}})
    assert a['calculated_total_kwh']==pytest.approx(31*660/3600)
    assert a['approved_reserve_kwh'] is None
    b=r.emergency_energy({'stop':60,'flow':600},{'support':{'stop':30,'flow':None}})
    assert b['calculated_total_kwh'] is None and b['known_energy_kwh']==.5
    assert b['missing_power_terms']==['support/flow']
    with pytest.raises(ValueError):r.emergency_energy({'bad':-1},{'support':{'bad':10}})


def test_reference_native_packet_reopens_and_keeps_unknown_costs():
    from engineering.ferrite_maglev import reference_assembly as r
    assert not r.verify()['manufacturing_release']
    s=r.study();assert s['station_installed_cost_usd'] is None
    assert s['chute_net_mass_ledger']['net_train_addition_kg'] is None


def test_optimisation_cache_includes_native_material_quantities(monkeypatch):
    from engineering.ferrite_maglev import optimisation
    _,c,k=model.load();old=optimisation.study(c,k)
    monkeypatch.setitem(geometry.MATERIALS,'steel',1.1*7850.)
    new=optimisation.study(c,k)
    assert old is not new
    for a,b in zip(old['candidates'],new['candidates']):
        assert b['civil']['native_passive_rail_line_mass_kg_m_per_direction']==pytest.approx(1.1*a['civil']['native_passive_rail_line_mass_kg_m_per_direction'])


def test_configuration_cache_observes_edits_and_does_not_share_mutable_records(monkeypatch,tmp_path):
    p=tmp_path/'reference.toml';p.write_text(configuration.INPUT.read_text());monkeypatch.setattr(configuration,'INPUT',p)
    first=configuration.selected();first.station['island_width_m']=99
    assert configuration.selected().station['island_width_m']==4.2
    p.write_text(p.read_text().replace('rail_thickness_m = 0.02','rail_thickness_m = 0.03'))
    assert configuration.selected().civil.rail_thickness_m==.03


def test_selected_configuration_cannot_approve_walkway_deletion(monkeypatch,tmp_path):
    p=tmp_path/'reference.toml';p.write_text(configuration.INPUT.read_text().replace('walkway_removal_approved = false','walkway_removal_approved = true'))
    monkeypatch.setattr(configuration,'INPUT',p)
    with pytest.raises(ValueError,match='approved alternative'):configuration.selected()


def test_city_replay_requires_geometry_binding_even_when_other_hashes_match():
    import json
    report=json.loads((ROOT/'cities/catalogue/west-asia/Iraq/Baghdad/engineering/maglev/summary.json').read_bytes())
    key=Path(geometry.__file__).relative_to(ROOT).as_posix();assert key in report['source_sha256']
    report['source_sha256'].pop(key)
    with pytest.raises(ValueError,match='sources'):cities.replay_city(report)
