import json
from decimal import Decimal

import pytest

from engineering.sourcing import cli
from engineering.sourcing.station_drive_rfq import (
    build_packet,
    publish_packet,
    verify_packet,
)


def test_packet_keeps_exact_candidate_bank_occurrences_and_unlocated_holds():
    packet = build_packet()

    assert packet["schema"] == "osr-station-drive-banked-rfq-scope/1"
    assert packet["candidate_id"] == "9c7d0942c9de6056e6afd051549273d0f34a72edf301fdd680ba37d12da7879f"
    assert packet["evaluation_id"] == "1491f90b02485e6ad9df63ac79b528e9c30e9e6d87041a3dc46b02efd364077b"
    assert packet["bank_scope_count"] == 5
    assert packet["total_located_primary_occurrence_count"] == 2430
    assert packet["non_additive_open_account_link_count"] == 20
    assert packet["supplier_quotes_received"] == 0
    assert packet["supplier_communications_sent"] == 0
    assert packet["selected_reference_changed"] is False
    assert packet["complete_drive_installed_cost"] is None
    assert packet["physical_accepted"] is False
    assert packet["unknown_is_zero"] is False
    assert "iraq.ms-cable-busbar" in {
        row["source_key"] for row in packet["additional_electrical_and_local_fabrication_leads"]}

    assert [row["scope_key"] for row in packet["bank_scopes"]] == [
        "bank/0", "bank/1", "bank/2", "bank/3", "bank/4"]
    for row in packet["bank_scopes"]:
        assert row["engineering_occurrence_count"] == 486
        assert len(row["engineering_occurrence_ids"]) == 486
        assert len(row["open_completion_accounts"]) == 4
        assert all(link["quantity"] is None for link in row["open_completion_accounts"])
        assert row["commercial_order_quantity"] is None
        assert row["complete_drive_installed_cost"] is None
        assert row["rfq_sent"] is False


def test_packet_carries_candidate_level_iqd_material_labour_uplift_sensitivity():
    packet = build_packet()
    rows = packet["existing_candidate_level_copper_material_labour_sensitivities"]

    assert [row["hours_per_gross_stock_tonne"] for row in rows] == [8, 16, 32]
    assert [row["estimated_total"] for row in rows] == [
        "90192658.13", "91034539.73", "92718302.93"]
    for row in rows:
        direct = Decimal(row["direct_material_cost"]) + Decimal(row["direct_labour_cost"])
        estimate = direct * (Decimal(1) + Decimal(row["uplift_fraction"]))
        assert estimate.quantize(Decimal("0.01")) == Decimal(row["estimated_total"])
        assert row["scope"].startswith("whole five-bank")
        assert row["supplier_quote"] is False
        assert row["commercial_order_quantity"] is None
        assert row["complete_installed_cost"] is None
        assert row["unknown_is_zero"] is False


def test_common_service_matrix_and_map_contract_name_unresolved_model_axes():
    packet = build_packet()

    matrix = packet["service_test_matrix"]
    assert matrix["scenario_count"] == 8
    assert matrix["route_distance_m"] == [1500.0, 2000.0]
    assert [row["case"] for row in matrix["load_cases"]] == [
        "empty", "normal", "crowd-control", "adverse-normal"]
    assert matrix["shared_service_context"]["headway_s"] == 120.0
    assert matrix["shared_service_context"]["normal_passengers_per_car"] == 46
    assert matrix["shared_service_context"]["fixed_seats_per_car"] == 44
    assert matrix["shared_service_context"]["wheelchair_places_per_car"] == 2
    assert matrix["load_cases"][2]["passengers_per_car"] == 160

    maps = packet["available_force_map_response_contract"]
    assert "air_gap_m" not in maps["required_axes_consumed_by_current_adapter"]
    assert "air_gap_m" in maps["required_axes_to_add_before_air_gap_sensitivity_can_be_admitted"]
    assert "electrical_frequency_hz" in maps["required_outputs_to_record_outside_current_map_schema"]


def test_publication_is_reproducible_and_rejects_tampering(tmp_path):
    result = publish_packet(output=tmp_path)
    assert result["verified"] is True
    assert result["bank_scope_count"] == 5
    assert result["primary_occurrence_count"] == 2430
    assert verify_packet(output=tmp_path)["verified"] is True

    packet_path = tmp_path / "station-drive-rfq-scope.json"
    packet = json.loads(packet_path.read_text())
    packet["supplier_communications_sent"] = 1
    packet_path.write_text(json.dumps(packet))
    with pytest.raises(ValueError, match="does not reproduce"):
        verify_packet(output=tmp_path)


def test_cli_builds_station_drive_scope_without_initialized_database(tmp_path, capsys):
    output = tmp_path / "rfq-scope"
    assert cli.main(["rfq", "station-drive-banks", "--output", str(output)]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["verified"] is True
    assert (output / "manifest.json").is_file()
    assert cli.main(["rfq", "station-drive-banks", "--output", str(output), "--check"]) == 0
    assert json.loads(capsys.readouterr().out)["verified"] is True
