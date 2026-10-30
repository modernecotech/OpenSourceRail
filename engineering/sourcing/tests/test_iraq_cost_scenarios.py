from decimal import Decimal
from pathlib import Path

from engineering.sourcing import catalogue, inputs
from engineering.sourcing.iraq_cost_scenarios import _make_2024_material_crosscheck, _make_packet


ROOT = Path(__file__).resolve().parents[3]
TAKEOFF = ROOT / "docs/design-engine/sourcing/material-takeoff/federated-v06-stock-takeoff.json.gz"


def test_ur_company_sheet_processing_scenarios_retain_source_candidate_and_uplift():
    takeoff = inputs.read_json(TAKEOFF)
    packet, _ = _make_packet(catalogue.load_catalogue(), takeoff, TAKEOFF)

    sheets = [row for row in packet["unit_rate_estimates"]
              if row["family"] == "aluminium sheet processing"]
    assert len(packet["unit_rate_estimates"]) == 102
    assert len(sheets) == 12
    assert {row["material_form"] for row in sheets} == {
        "Hard aluminium sheet, 0.6–0.9 mm",
        "Hard aluminium sheet, 1 mm and above",
        "Annealed aluminium sheet, 0.6–0.9 mm",
        "Annealed aluminium sheet, 1 mm and above",
    }
    assert {row["labour_hours_per_output"] for row in sheets} == {"8", "16", "32"}

    profiles = [row for row in packet["unit_rate_estimates"]
                if row["family"] == "aluminium profile processing"]
    assert len(profiles) == 9
    profile_prices = {
        "Non-oxidized aluminium profiles": Decimal("4600000"),
        "Oxidized aluminium profiles": Decimal("5200000"),
        "Spray-painted aluminium profiles": Decimal("5500000"),
    }
    assert {row["material_form"] for row in profiles} == set(profile_prices)
    for row in profiles:
        hours = Decimal(row["labour_hours_per_output"])
        expected = (profile_prices[row["material_form"]] + hours * Decimal("9375")) * Decimal("1.20")
        assert Decimal(row["process"]["estimated_unit_cost"]) == expected

    prices = {
        "Hard aluminium sheet, 0.6–0.9 mm": Decimal("5200000"),
        "Hard aluminium sheet, 1 mm and above": Decimal("5100000"),
        "Annealed aluminium sheet, 0.6–0.9 mm": Decimal("5300000"),
        "Annealed aluminium sheet, 1 mm and above": Decimal("5200000"),
    }
    for row in sheets:
        hours = Decimal(row["labour_hours_per_output"])
        expected = (prices[row["material_form"]] + hours * Decimal("9375")) * Decimal("1.20")
        assert Decimal(row["process"]["estimated_unit_cost"]) == expected
        assert row["process"]["candidate_id"] == takeoff["candidate_id"]
        assert row["process"]["input_id"] == takeoff["source_input_id"]
        assert row["process"]["uplift_fraction"] == "0.2"
        assert row["process"]["candidate_takeoff_mapped"] is False

    assert packet["candidate_takeoff_mapped_for_unit_rate_estimates"] is False
    assert packet["physical_qualification"] is None
    assert packet["unknown_is_zero"] is False


def test_2024_cso_material_crosscheck_prices_material_plus_labour_plus_20_percent():
    takeoff = inputs.read_json(TAKEOFF)
    packet = _make_2024_material_crosscheck(catalogue.load_catalogue(), takeoff, TAKEOFF)

    assert packet["schema"] == "osr-iraq-material-cost-history-crosscheck/1"
    assert packet["candidate_id"] == takeoff["candidate_id"]
    assert packet["source_input_id"] == takeoff["source_input_id"]
    assert packet["candidate_takeoff_mapped"] is False
    assert packet["basis"]["uplift_fraction"] == "0.20"
    assert len(packet["historical_2024_material_2025_wage_scenarios"]) == 3
    assert len(packet["current_2025_material_2025_wage_scenarios"]) == 3

    historical = {row["labour_hours_per_nominal_m3"]: row["process"]
                  for row in packet["historical_2024_material_2025_wage_scenarios"]}
    current = {row["labour_hours_per_nominal_m3"]: row["process"]
               for row in packet["current_2025_material_2025_wage_scenarios"]}
    assert {key: value["estimated_unit_cost"] for key, value in historical.items()} == {
        "2": "103200", "4": "125700", "8": "170700"}
    assert {key: value["estimated_unit_cost"] for key, value in current.items()} == {
        "2": "114720", "4": "137220", "8": "182220"}
    for process in [*historical.values(), *current.values()]:
        assert process["uplift_fraction"] == "0.2"
        assert process["candidate_takeoff_mapped"] is False
        assert process["complete_installed_cost"] is None
        assert process["unknown_is_zero"] is False

    grit = next(row for row in packet["material_rate_comparisons"]
                if row["material"].startswith("2024 normal grit"))
    assert "not established" in grit["annual_2025_baghdad"]["product_scope_correspondence"]
