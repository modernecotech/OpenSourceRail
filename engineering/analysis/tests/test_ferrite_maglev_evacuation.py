"""Geometric counterexamples, no safety transfer and complete added-scope accounting."""
from pathlib import Path
import math
import sys
import pytest
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
from engineering.ferrite_maglev import evacuation,optimisation,model,geometry,cities


def test_eight_metre_slide_is_sixteen_metres_not_a_short_door_attachment():
    r=evacuation.slide_geometry(8,30)
    assert r['straight_slide_length_m']==pytest.approx(16)
    assert r['horizontal_run_m']==pytest.approx(8*math.sqrt(3))
    assert r['total_clear_run_with_landing_m']==pytest.approx(8*math.sqrt(3)+3)
    assert r['clear_width_with_margins_m']==2.5
    assert not r['supplier_device_selected'] and not r['physical_validation']


@pytest.mark.parametrize('surface',['live-road','roof','water','obstructed-land'])
def test_slide_cannot_be_selected_over_unsafe_landing(surface):
    r=evacuation.assess_landing(evacuation.slide_geometry(8,30),surface=surface,clear_run_m=100,clear_width_m=10,usable_exits=18)
    assert r['state']=='rejected' and not r['geometry_screen_pass']
    assert not r['safe_to_deploy'] and not r['walkway_removal_approved']


def test_clear_geometry_still_cannot_approve_accessibility_fire_or_device():
    r=evacuation.assess_landing(evacuation.slide_geometry(8,30),surface='controlled-safe-dry-ground',clear_run_m=30,clear_width_m=4,usable_exits=18)
    assert r['geometry_screen_pass'] and r['state']=='hold'
    assert not r['accepted'] and not r['safe_to_deploy']
    assert all(v['state']=='unknown' and not v['accepted'] for v in r['closure'])


@pytest.mark.parametrize('run,width,exits',[(5,4,18),(30,1,18),(30,4,0)])
def test_bad_clearance_or_missing_exit_rejects_the_path(run,width,exits):
    r=evacuation.assess_landing(evacuation.slide_geometry(8,30),surface='controlled-safe-dry-ground',clear_run_m=run,clear_width_m=width,usable_exits=exits)
    assert r['state']=='rejected' and r['known_failures']


def test_flow_is_only_an_optimistic_queue_bound_and_zero_exits_is_not_zero_time():
    a=evacuation.flow_lower_bound(960,18,.5,30);b=evacuation.flow_lower_bound(960,9,.5,30)
    assert a['optimistic_flow_time_lower_bound_s']==pytest.approx(30+960/9)
    assert b['optimistic_flow_time_lower_bound_s']-30==pytest.approx(2*(a['optimistic_flow_time_lower_bound_s']-30))
    assert not a['pedestrian_simulation_performed'] and a['validated_evacuation_time_s'] is None
    zero=evacuation.flow_lower_bound(960,0,1,30)
    assert zero['optimistic_flow_time_lower_bound_s'] is None and zero['state']=='rejected'


def test_beam_only_material_removal_keeps_necessary_reaction_faces_and_supports():
    before=geometry.civil_bay();bare=evacuation.beam_only_geometry()
    assert len(before['parts'])==74 and len(bare['parts'])==54
    assert len(bare['removed_reference_part_ids'])==20
    assert all(not p['id'].startswith('walkway-') for p in bare['parts'])
    assert {p['id'] for p in bare['parts']}=={p['id'] for p in before['parts'] if not p['id'].startswith('walkway-')}
    assert sum(p['material']=='steel' for p in bare['parts'])==40
    assert bare['removed_modelled_walkway_mass_kg']==pytest.approx(20*2.49*.12*2500)
    assert before['modelled_material_mass_kg']-bare['modelled_material_mass_kg']==pytest.approx(bare['removed_modelled_walkway_mass_kg'])
    assert not bare['evacuation_release'] and not bare['manufacturing_release']


def test_beam_only_savings_are_conditional_and_do_not_erase_equipment_or_foundations():
    _,c,k=model.load();a=optimisation.load();_,v=optimisation.vehicle(c,k,a['vehicle_profiles'][0])
    ref=optimisation.civil(c,k,v,.8,1.6,.15,.18,25,a)
    bare=optimisation.civil(c,k,v,.8,1.6,.15,.18,25,a,guideway_mode='onboard-evacuation-no-walkway')
    assert ref['concrete_m3_dual_km']-bare['concrete_m3_dual_km']==pytest.approx(240)
    assert ref['section']['dead_line_mass_kg_m']-bare['section']['dead_line_mass_kg_m']==pytest.approx(300)
    assert bare['indexed_rows_usd_dual_km']['walkway_brackets']==0
    for key in ['supports','passive_rail_supply','temporary','installation','night','qa','relocation','traffic']:
        assert bare['indexed_rows_usd_dual_km'][key]==ref['indexed_rows_usd_dual_km'][key]
    assert not bare['eligible_for_reference_research_champion'] and not bare['walkway_removal_approved']
    assert bare['new_onboard_evacuation_mass_kg_per_car'] is None
    assert bare['new_onboard_evacuation_lifetime_cost_usd'] is None
    assert bare['net_whole_system_saving_usd'] is None


def test_unapproved_deletion_never_enters_reference_champion_selection():
    r=optimisation.study()
    assert r['candidate_count']==r['beam_only_candidate_count']==432
    assert not r['minimum_indexed_allowance_candidate']['id'].startswith('onboard-evacuation')
    assert len(r['beam_only_candidates'])==432
    assert all(not row['civil']['eligible_for_reference_research_champion'] for row in r['beam_only_candidates'])
    assert not r['beam_only_reference_champion_eligible'] and r['beam_only_net_system_saving_usd'] is None


def test_added_pack_mass_and_lifecycle_cost_cannot_be_silently_absorbed():
    r=evacuation.study()
    assert r['installed_door_pack_count_hypothesis']==36
    assert r['actual_door_configuration'] is None
    assert [v['added_kg_per_car'] for v in r['added_mass_sensitivities']]==[150,300,600]
    assert r['selected_added_mass_kg'] is r['procurement_and_lifetime_cost_usd'] is r['net_system_saving_usd'] is None
    assert not r['walkway_removal_approved'] and not r['operational_deployment_authorised']
    assert not r['supplier_lead']['exact_model_uk_manufacture_confirmed']
    assert all(r[k] is False for k in model.FLAGS)


def test_city_keeps_conditional_gross_credit_separate_from_existing_cost_scenarios(tmp_path):
    r=cities.generate(ROOT/'cities/catalogue/west-asia/Iraq/Baghdad',output_dir=tmp_path)
    option=r['costs']['beam_only_conditional_option']
    assert option['onboard_pack_count_hypothesis']==r['totals']['cars']*6
    assert option['net_system_saving_usd'] is option['procurement_and_lifetime_cost_usd'] is None
    assert not option['walkway_removal_approved']
    assert all(not v['scenario'].startswith('beam-only') for v in r['costs']['scenarios'])


@pytest.mark.parametrize('before,after',[
 ('walkway_removal_approved = false','walkway_removal_approved = true'),
 ('slide_is_universal_sole_means = false','slide_is_universal_sole_means = true'),
 ('concrete_alone_supports_current_attraction_maglev = false','concrete_alone_supports_current_attraction_maglev = true'),
 ('mobility_assistance_demonstrated = false','mobility_assistance_demonstrated = true'),
 ('flow_is_measured = false','flow_is_measured = true'),
 ('slide_slope_screens_degrees = [30.0, 40.0, 45.0]','slide_slope_screens_degrees = [90.0]'),
])
def test_unqualified_acceptance_and_invalid_inputs_fail_closed(monkeypatch,tmp_path,before,after):
    original=evacuation.INPUT.read_text();assert before in original
    p=tmp_path/'evac.toml';p.write_text(original.replace(before,after));monkeypatch.setattr(evacuation,'INPUT',p)
    with pytest.raises(ValueError):evacuation.load()


def test_actual_retained_beam_only_native_packet_matches_target():
    packet=evacuation.verify_native(ROOT/'docs/design-engine/ferrite-maglev/beam-only')
    assert not packet['evacuation_accepted'] and not packet['walkway_removal_approved']
    assert len(packet['files_sha256'])==8


def test_inward_door_slide_intersects_adjacent_beam_and_cannot_be_counted_as_clear():
    inner=evacuation.adjacent_guideway_path(towards_adjacent=True)
    outer=evacuation.adjacent_guideway_path(towards_adjacent=False)
    assert inner['intersected_box_part_ids']
    assert any('beam-1/web' in name for name in inner['intersected_box_part_ids'])
    assert inner['assessment']['state']=='rejected'
    assert outer['intersected_box_part_ids']==[]
    assert outer['assessment']['state']=='hold'
    assert not outer['assessment']['safe_to_deploy']


def test_vertical_chute_height_does_not_invent_horizontal_reach_or_descent_rating():
    short=evacuation.chute_geometry(8);high=evacuation.chute_geometry(30)
    assert short['total_clear_run_with_landing_m']==pytest.approx(5.1)
    assert short['clear_width_with_margins_m']==pytest.approx(2.2)
    assert high['total_clear_run_with_landing_m']==short['total_clear_run_with_landing_m']
    assert short['total_clear_run_with_landing_m']<evacuation.slide_geometry(8,30)['total_clear_run_with_landing_m']
    for r in (short,high):
        assert r['descent_time_s'] is r['descent_speed_m_s'] is r['maximum_operating_height_m'] is None
        assert not r['physical_validation'] and not r['supplier_device_selected']
    wider=evacuation.chute_geometry(30,assumed_sway_m=1.)
    assert wider['landing_area_rectangle_m2']>high['landing_area_rectangle_m2']


@pytest.mark.parametrize('surface',['live-road','roof','water','obstructed-land'])
def test_chute_still_rejects_unsafe_landing_despite_shorter_reach(surface):
    r=evacuation.assess_landing(evacuation.chute_geometry(30),surface=surface,clear_run_m=100,clear_width_m=10,usable_exits=18)
    assert r['state']=='rejected' and not r['safe_to_deploy']


def test_chute_sway_can_hit_native_iron_faces_and_extension_only_clears_geometric_hold():
    outer=evacuation.chute_guideway_path(towards_adjacent=False)
    inner=evacuation.chute_guideway_path(towards_adjacent=True)
    assert any('lift-rail' in key for key in outer['intersected_box_part_ids'])
    assert any('beam-1/' in key for key in inner['intersected_box_part_ids'])
    assert outer['assessment']['state']==inner['assessment']['state']=='rejected'
    extended=evacuation.chute_guideway_path(towards_adjacent=False,standoff_m=2.)
    assert not extended['intersected_box_part_ids']
    assert extended['assessment']['state']=='hold' and not extended['assessment']['safe_to_deploy']


def test_chute_product_height_and_claimed_building_flow_are_never_rail_approval():
    r=evacuation.study()
    assert [v['height_m'] for v in r['chute_envelopes']]==[8,12,20,30]
    assert r['chute_operating_height_approved_m'] is None and not r['chute_descent_simulation_performed']
    assert all(not v['railway_accepted'] and not v['uk_manufacture_confirmed'] for v in r['chute_supplier_comparison'])
    assert r['chute_supplier_comparison'][0]['manufacturing_country']=='Germany'
    flows=r['chute_building_claim_flow_bounds']
    assert flows[0]['optimistic_flow_time_lower_bound_s'] is None
    assert flows[-1]['optimistic_flow_time_lower_bound_s']==pytest.approx(30+960/(18*.25))
    assert flows[-2]['optimistic_flow_time_lower_bound_s']==pytest.approx(30+960/(9*.25))
    assert all(not v['pedestrian_simulation_performed'] for v in flows)


@pytest.mark.parametrize('before,after',[
 ('chute_is_universal_sole_means = false','chute_is_universal_sole_means = true'),
 ('railway_device_selected = false','railway_device_selected = true'),
 ('wind_response_validated = false','wind_response_validated = true'),
 ('accessible_evacuation_demonstrated = false','accessible_evacuation_demonstrated = true'),
 ('outer_diameter_screen_m = 1.2','outer_diameter_screen_m = 0.0'),
])
def test_chute_evidence_and_envelope_inputs_fail_closed(monkeypatch,tmp_path,before,after):
    original=evacuation.INPUT.read_text();assert before in original
    p=tmp_path/'evac.toml';p.write_text(original.replace(before,after));monkeypatch.setattr(evacuation,'INPUT',p)
    with pytest.raises(ValueError):evacuation.load()


def test_zippered_exit_extremes_do_not_cover_intermediate_ground_height():
    r=evacuation.assess_exit_heights([8,10,12,20,30],[8,12,20,30])
    assert r['state']=='rejected' and not r['all_sampled_heights_match']
    gap=next(v for v in r['matches'] if v['door_sill_to_ground_m']==10)
    assert gap['outlet_height_above_ground_m']==2 and gap['state']=='rejected'
    covered=evacuation.assess_exit_heights([8,12],[8,12])
    assert covered['all_sampled_heights_match'] and covered['state']=='hold'
    assert not covered['continuous_route_height_coverage_proved']
    assert not covered['usable_exit_proved'] and not covered['driverless_operation_proved']
    empty=evacuation.assess_exit_heights([8],[])
    assert empty['state']=='rejected' and empty['matches'][0]['nearest_exit_drop_m'] is None


@pytest.mark.parametrize('required,ports',[([],[]),([0],[8]),([8],[-1]),([float('nan')],[8])])
def test_invalid_height_records_do_not_create_coverage(required,ports):
    with pytest.raises(ValueError):evacuation.assess_exit_heights(required,ports)


def test_manufacturer_application_claims_and_installation_requirements_do_not_approve_device():
    r=evacuation.study();supplier=r['chute_supplier_comparison'][0]
    assert supplier['transport_application_url']=='https://escape-chute.net/en/special-constructions/'
    assert supplier['manufacturer_stationary_height_claim']['upper_description']=='over 110 m'
    assert supplier['height_claim_m']==[4,120] # Separate retailer listing, not a merged approval range.
    assert not supplier['installed_transport_reference_verified'] and not supplier['unattended_operation_demonstrated']
    requirements=r['onboard_installation_requirements']
    assert len({v['id'] for v in requirements})==7
    assert all(v['state']=='open' and not v['accepted'] and v['evidence_required'] for v in requirements)
    assert any(v['id']=='EVAC-DRIVERLESS' and 'without assuming' in v['requirement'] for v in requirements)
    assert r['illustrative_20m_35degree_slide']['horizontal_run_m']==pytest.approx(20/math.tan(math.radians(35)))
    assert r['variable_height_research']['selected_exit_drops_m'] is None
    assert not r['walkway_removal_approved']


def test_unattended_operation_claim_is_rejected(monkeypatch,tmp_path):
    p=tmp_path/'evac.toml';p.write_text(evacuation.INPUT.read_text().replace('unattended_operation_demonstrated = false','unattended_operation_demonstrated = true'))
    monkeypatch.setattr(evacuation,'INPUT',p)
    with pytest.raises(ValueError):evacuation.load()
