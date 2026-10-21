"""New architecture, user requirements and coordinated configuration gates."""
from copy import deepcopy
import json
from pathlib import Path
import pytest
from engineering.ferrite_maglev import model,configuration,specification,station,manufacturing


def test_new_primary_architecture_has_no_onboard_main_traction():
    _,c,_=model.load()
    assert c['metadata']['schema']=='osr-ferrite-maglev-study/2'
    assert c['architecture']['route_powered_stator']
    assert c['architecture']['station_zone_powered_stator']
    assert not c['architecture']['onboard_main_traction']
    assert c['architecture']['interstation_powered_propulsion']
    assert not c['architecture']['interstation_continuous_powered_stator']
    assert c['architecture']['onboard_support_guidance_windings']
    for name,value in [('onboard_main_traction',True),('route_powered_stator',False),('onboard_support_guidance_windings',False)]:
        bad=deepcopy(c);bad['architecture'][name]=value
        with pytest.raises(ValueError):model.validate(bad)


def test_all_100_document_items_are_controlled_without_claiming_acceptance():
    data=specification.register()
    assert len(data['requirements'])==100
    assert len({r['id'] for r in data['requirements']})==100
    assert not any(r['accepted'] for r in data['requirements'])
    assert data['implemented_complete_system'] is False
    assert data['source_sha256']


def test_later_spacing_and_transfer_instructions_preserve_authored_requirements():
    data=specification.register();rows={r['number']:r for r in data['requirements']}
    original=json.loads(specification.INPUT.read_text())
    original_rows={r['number']:r for r in original['requirements']}
    for number in (1,4,25,56,57,70):
        assert rows[number]['source_requirement']==original_rows[number]['requirement']
        assert rows[number]['requirement']!=rows[number]['source_requirement']
        assert rows[number]['amendment_configuration']=='ferrite-maglev-study.toml [operating_strategy]'
        assert rows[number]['accepted'] is False
    assert '1 km' in rows[4]['source_requirement']
    assert '4–5 km' in rows[4]['requirement']
    assert 'passenger transfers' in rows[56]['requirement']
    assert rows[47]['requirement']==original_rows[47]['requirement']


def test_changed_user_document_invalidates_controlled_requirement_input(tmp_path,monkeypatch):
    data=specification.register();source=tmp_path/data['source'];source.write_text('changed')
    contract=tmp_path/'spec.json';contract.write_text(json.dumps(data))
    monkeypatch.setattr(specification,'INPUT',contract);monkeypatch.setattr(model,'ROOT',tmp_path)
    with pytest.raises(ValueError,match='specification changed'):specification.register()


def test_door_count_cannot_diverge_between_body_and_egress():
    _,c,_=model.load();f=configuration.selected(c).formation
    assert len(f.doors_per_side_x_m)==2 and f.devices==24
    c['vehicle']['passenger_doors_per_side']=3
    with pytest.raises(ValueError,match='door counts'):configuration.selected(c)


def test_old_mass_and_traction_evidence_are_only_a_named_comparison():
    prior=json.loads((model.ROOT/'engineering/ferrite_maglev/data/comparison-v051.json').read_text())
    assert prior['source_commit']=='2617b04e722ca24b7ad9120f94610fe869f27053'
    assert prior['role']=='historical-v0.5.1-onboard-drive-comparison-only'
    assert prior['inputs']['power']['gross_battery_matched_kwh_per_car']==225
    _,c,_=model.load();assert c['power']['services_battery_kwh_per_car']==30


def test_end_infill_and_itemised_support_targets_reconcile_primary_bill():
    _,c,k=model.load();bill=manufacturing.civil(c,k,walkway_area=0)
    box=c['civil']['narrow_box_screen'];span=c['civil']['reference_span_m']
    void=(box['outer_width_m']-2*box['web_thickness_m'])*(box['outer_depth_m']-2*box['flange_thickness_m'])
    area=box['outer_width_m']*box['outer_depth_m']-void
    assert bill['quantities']['concrete_m3_dual_km']==pytest.approx((area+2*.4*void/span)*2000)
    assert bill['support_total_usd']==sum(r['amount_usd'] for r in bill['support_components_per_unit'])==22000
    assert bill['qualified_foundation_selection'] is None
    assert not bill['costs_are_quotes']


def test_long_leg_pure_trajectory_cannot_clear_the_installed_winding_gate():
    _,c,_=model.load();c=deepcopy(c);c['power']['station_spacing_study_m']=3000.
    r=model.cycle(c,26200.,hot=True)
    assert r['pure_trajectory_screen_pass']
    assert not r['station_zone_screen_pass'] and not r['kinematic_screen_pass']
    assert r['station_zone']['zero_overlap_with_nonzero_force']
    assert 'zero magnetic overlap' in r['kinematic_hold']
    assert r['station_zone']['intermediate_station_credit_applied'] is False
    assert r['achieved_speed_kmh'] is None
    assert not r['route_acceptance']


def test_fixed_zone_force_screen_matches_independent_full_consist_overlap():
    _,c,_=model.load();pure=station.trajectory(record_trace=False)
    expected=station.magnetic_overlap(pure)
    actual=model.station_zone_screen(c,pure,cars=6)
    assert actual['study_pass']==expected['study_pass']
    assert actual['minimum_force_reserve_fraction']==pytest.approx(expected['minimum_force_reserve_fraction'])
    assert actual['magnetic_bands_relative_to_front_m']==expected['magnetic_bands_relative_to_front_m']
    one=model.station_zone_screen(c,pure,cars=1)
    assert one['cars']==1 and len(one['magnetic_bands_relative_to_front_m'])==1
    assert one['train_length_assumption_m']==17.


def test_fixed_zone_cache_is_input_bound_and_caller_results_are_independent(monkeypatch):
    _,c,_=model.load();pure=station.trajectory(record_trace=False)
    model._station_zone_cached.cache_clear()
    first=model.station_zone_screen(c,pure)
    hits=model._station_zone_cached.cache_info().hits
    first['minimum_force_reserve_fraction']['launch']=-99
    repeat=model.station_zone_screen(c,pure)
    assert model._station_zone_cached.cache_info().hits==hits+1
    assert repeat['minimum_force_reserve_fraction']['launch']>0
    original=station.load
    def changed():
        a=original();a['station']['winding_end_m']=25.
        return a
    monkeypatch.setattr(station,'load',changed)
    changed_result=model.station_zone_screen(c,pure)
    assert changed_result['winding_end_m']==25
    assert not changed_result['study_pass']


def test_city_force_hold_survives_unlocated_intermediate_zone_hints():
    from engineering.ferrite_maglev import cities
    import tomllib
    _,c,_=model.load();a=tomllib.loads(cities.ASSUMPTIONS.read_text())
    f=cities.formation(c,dict(passenger_capacity=720,crush_capacity=960),[])
    stops=[dict(id=f's{i}',s_m=s,lat=33.,lon=44.,platform_length_m=115.) for i,s in enumerate((0.,3000.))]
    r=cities.line_plan(c,a,f,dict(name='fixture',shape='ring',length_m=6000.),
        stops,dict(schedule=[dict(headway_min=3.)]),cities.duty_evaluator(c))
    assert r['pure_trajectory_screen_pass']
    assert not r['fixed_station_zone_screen_pass']
    assert not r['station_powered_kinematic_screen_pass']
    assert not r['fleet']['kinematic_profile_closed']
    assert r['kinematic_holds'] and all(h['stage']=='fixed-station-zone' for h in r['kinematic_holds'])
    assert all('zero magnetic overlap' in h['reason'] for h in r['kinematic_holds'])
    assert r['intermediate_station_zone_options']
    assert all(not option['located'] and not option['priced'] for option in r['intermediate_station_zone_options'])


def test_city_duty_uses_the_actual_formation_in_its_fixed_zone_screen():
    from engineering.ferrite_maglev import cities
    _,c,_=model.load();evaluate=cities.duty_evaluator(c)
    one=evaluate.for_formation(1)(1000.,True,False)
    six=evaluate.for_formation(6)(1000.,True,False)
    assert len(one['station_zone']['magnetic_bands_relative_to_front_m'])==1
    assert len(six['station_zone']['magnetic_bands_relative_to_front_m'])==6
    assert one['station_zone']['train_length_assumption_m']==17
    assert six['station_zone']['train_length_assumption_m']==104.5
