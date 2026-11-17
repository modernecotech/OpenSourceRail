"""Bounded quote input retains real interfaces and unknown supplier quantities."""
from pathlib import Path

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
    assert value['mechanical_interfaces']['nominal_airgap_each_side_m']==.015
    assert value['mechanical_interfaces']['primary_mounting_datum_and_tolerance'] is None
    assert value['quote_request']['single_installed_budgetary_price_usd'] is None
    assert all(item['installed_quantity'] is None and item['installed_price_usd'] is None for item in value['quote_items'])
    assert value['independent_stop']['illustrative_margin_m']<0
    assert value['physical_accepted'] is False and value['manufacturing_release'] is False
    assert set(value['protocols'])=={'T05','T07','T08'}
