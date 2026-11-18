"""Bounded quote input retains real interfaces and unknown supplier quantities."""
from pathlib import Path
import pytest

from engineering.design_search.station_module_schedule import encoded, schedule

ROOT=Path(__file__).resolve().parents[3]
OUTPUT=ROOT/'docs/design-engine/v07-demonstrator-propulsion/station-module.json'


def test_one_station_module_matches_selected_vehicle_and_research_booster():
    value=schedule(ROOT)
    assert encoded(value)==OUTPUT.read_bytes()
    assert value['parent_selected_vehicle_candidate_id']=='756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3'
    assert value['booster_railway_research_configuration_id']=='d1fec49310ae06beca16dd4fe4138b075f3b1c81476faae18c9df0877bdb7033'
    scope=value['module_scope']
    assert scope['full_train_length_m']==104.5
    assert scope['one_sided_passenger_doors_per_train']==12
    assert scope['launch_command_window_m']==[0,500]
    assert scope['booster_command_window_m']==[1000,1250]
    assert scope['actual_installed_primary_m'] is None
    minimum=scope['full_engagement_minimum_primary']
    assert minimum['research_configuration_id']==value['booster_railway_research_configuration_id']
    assert minimum['selected_vehicle_candidate_id']==value['parent_selected_vehicle_candidate_id']
    assert minimum['body_candidate_id']=='9489e4f2666fd3b3c73232c86df3f12adf42a5531eb27373834cf3fecb1a3117'
    assert [r['installed_length_m'] for r in minimum['sections']]==[596.5,346.5]
    assert [(r['start_m'],r['installed_end_m']) for r in minimum['sections']]==[(-100.5,496.0),(899.5,1246.0)]
    assert minimum['totals']['installed_length_m']==943.0
    assert minimum['totals']['module_pieces']==76
    assert minimum['totals']['stator_face_module_joints']==148
    assert minimum['totals']['independently_terminated_bank_ends']==4
    assert minimum['bare_stock_kg']['bare_primary_stock_kg']==pytest.approx(215179.0208)
    assert minimum['complete_installed_primary_mass_kg'] is None
    assert minimum['installed_price_usd'] is None
    assert minimum['available_moving_force_verified'] is False
    alternatives=scope['receiving_revision_candidates']
    assert [r['reserved_length_m'] for r in alternatives]==[350,400,450,550]
    assert len({r['receiving_research_configuration_id'] for r in alternatives})==4
    assert all(r['selected'] is False and r['civil_station_quantity_and_price_effect'] is None for r in alternatives)
    assert alternatives[0]['nose_stop_margin_with_illustrative_reaction_m']<0
    assert alternatives[1]['nose_stop_margin_with_illustrative_reaction_m']>0
    assert alternatives[2]['full_train_engagement_margin_m']<0
    assert 92 < alternatives[3]['full_train_engagement_margin_m'] < 93
    assert alternatives[3]['selected'] is False and alternatives[3]['installed_brake_length_m'] is None
    assert [r['nonnegative_full_train_geometric_screen'] for r in alternatives]==[False,False,False,True]
    assert [r['first_nonnegative_full_train_geometric_screen'] for r in alternatives]==[False,False,False,True]
    assert scope['first_nonnegative_full_train_geometric_research_reservation_m']==550
    assert value['independent_stop']['full_train_engagement_before_brake_minimum_m']>457
    assert value['independent_stop']['extra_berth_tail_position_and_uncertainty_clearance_m'] is None
    assert value['mechanical_interfaces']['nominal_airgap_each_side_m']==.015
    assert value['mechanical_interfaces']['primary_mounting_datum_and_tolerance'] is None
    assert value['quote_request']['single_installed_budgetary_price_usd'] is None
    assert all(item['installed_quantity'] is None and item['installed_price_usd'] is None for item in value['quote_items'])
    assert [item['minimum_quote_quantity'] for item in value['quote_items'][:2]]==[596.5,346.5]
    assert value['independent_stop']['illustrative_margin_m']<0
    assert value['physical_accepted'] is False and value['manufacturing_release'] is False
    assert set(value['protocols'])=={'T05','T07','T08'}


def test_changed_primary_source_cannot_keep_stock_evaluation(monkeypatch):
    source=ROOT/'engineering/station_rail/propulsion_layout.py'
    read=Path.read_bytes
    def changed(self):
        raw=read(self)
        return raw+b'\n# changed source\n' if self==source else raw
    monkeypatch.setattr(Path,'read_bytes',changed)
    with pytest.raises(ValueError,match='Loaded propulsion layout producer differs'):
        schedule(ROOT)
