from copy import deepcopy
import json

import pytest

from cities.Baghdad.airport_assembly import FRAME, assembly
from cities.Baghdad.airport_opening import calculate, opening_inputs
from cities.Baghdad.airport_service import build_service
from cities.Baghdad.engineering.mechanical.vehicle.power_interface import mass_form, mass_return


@pytest.fixture(scope="module")
def enquiry():
    inputs = opening_inputs()
    cfg, report, parent = inputs
    service = build_service(cfg, report["networks"]["first"]["groups"]["Airport"])
    revision = json.loads(FRAME.read_bytes())["braced_revision_id"]
    case = calculate(inputs=inputs, service=service, vehicle_revision=revision)
    basis = {"braced_revision": revision, "first_network_id": parent["selected_candidate_id"]}
    return case, cfg, mass_return(mass_form(basis), basis)


def test_opening_parts_use_ordered_fleet_and_traceable_cut_stock(enquiry):
    case, cfg, account = enquiry
    result = assembly(case, cfg, account)
    fleet = case["bundle"]["active_sets"] + case["bundle"]["spares"]
    parts = {r["item"]: r for r in result["parts"]}
    assert parts["Wheelset"]["fleet_quantity"] == 24 * fleet
    assert parts["Removable powered bogie"]["fleet_quantity"] == 12 * fleet
    assert parts["Door opening and controller"]["fleet_quantity"] == case["controls"]["door_controllers"]
    assert parts["Chord splice"]["per_car"] == 4
    assert sum(row["cut_count_per_car"] for row in result["cut_list"]) == 128
    assert sum(row["cut_stock_kg_per_car"] for row in result["cut_list"]) == pytest.approx(
        5196.181, abs=0.002
    )
    assert result["mass_account"]["returned_tare_kg"] is None
    assert result["geometric_budgets"]["bare_steel_doorway_widths_m"] == [1.3] * 8
    assert result["geometric_budgets"]["remaining_combined_intrusion_and_tolerance_m"] == 0
    assert result["civil"]["support_positions"] == 2402
    assert result["civil"]["bearing_allowance"] == 9600
    assert all(row["docstatus"] == 0 for row in result["production"]["draft_work_orders"])


def test_reject_mixed_frame_and_mass_basis(enquiry):
    case, cfg, account = enquiry
    foreign = deepcopy(account)
    foreign["weight_return"]["basis"]["braced_revision"] = "another car"
    with pytest.raises(ValueError, match="revisions"):
        assembly(case, cfg, foreign)
    changed = deepcopy(case)
    changed["controls"]["door_controllers"] -= 1
    with pytest.raises(ValueError, match="quantities"):
        assembly(changed, cfg, account)


def test_demonstrator_geometry_stop_screen_and_partial_price(enquiry):
    case, cfg, account = enquiry
    demo = assembly(case, cfg, account)["demonstrator"]
    assert demo["candidate_id"] != case["candidate_id"]
    assert demo["civil"]["beam_count"] == 360
    assert demo["civil"]["pier_foundation_count"] == 362
    assert demo["track_km"] == pytest.approx(3.6)
    assert sum(demo["isolatable_section_lengths_km"]) == pytest.approx(1.8)
    level, downhill = demo["kinematic_screen"]
    assert level["braking_distance_m"] == pytest.approx(20**2 / 1.2)
    assert downhill["brake_entry_m_s"] > level["brake_entry_m_s"]
    assert downhill["remaining_length_m"] < level["remaining_length_m"]
    assert demo["priced_direct_subtotal_usd"] == sum(demo["priced_direct_scopes_usd"].values())
    assert demo["complete_installed_usd"] is None
    assert demo["article_and_controls"]["test_car_weighed_mass_kg"] is None
