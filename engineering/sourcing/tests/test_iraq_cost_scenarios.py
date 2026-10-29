from decimal import Decimal
from pathlib import Path

from engineering.sourcing import catalogue, inputs
from engineering.sourcing.iraq_cost_scenarios import _make_packet


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
