from decimal import Decimal
from pathlib import Path

from engineering.sourcing import catalogue, inputs
from engineering.sourcing.iraq_cost_scenarios import (
    _make_2024_material_crosscheck, _make_2026_july_reference,
    _make_2026_september_reference, _make_packet,
    _write_regional_publication,
)


ROOT = Path(__file__).resolve().parents[3]
TAKEOFF = ROOT / "docs/design-engine/sourcing/material-takeoff/federated-v06-stock-takeoff.json.gz"


def test_regional_publication_writes_markdown_and_seals_its_exact_bytes(tmp_path):
    packet = {
        "candidate_id": "candidate",
        "source_input_id": "input",
        "takeoff_id": "takeoff",
        "source_epoch_id": "epoch",
        "source_ids": [],
        "unit_rate_estimates": [],
        "regional_concrete_takeoff_estimates": [],
        "candidate_mapped_aluminium_stock_scenarios": [],
        "packet_id": "packet",
        "basis": {"formula": "materials + labour + uplift"},
    }

    _write_regional_publication(tmp_path, packet)

    readme = (tmp_path / "README.md").read_text()
    manifest = inputs.read_json(tmp_path / "manifest.json")
    assert readme.startswith("# Iraqi domestic material + labour cost reference")
    assert not readme.startswith('"# ')
    assert manifest["file_sha256"]["README.md"] == inputs.digest(tmp_path / "README.md")


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


def test_2026_july_regional_cost_reference_maps_material_plus_labour_plus_20_percent():
    takeoff = inputs.read_json(TAKEOFF)
    packet, estimates = _make_2026_july_reference(catalogue.load_catalogue(), takeoff, TAKEOFF)

    assert packet["schema"] == "osr-iraq-domestic-cost-reference/2"
    assert packet["candidate_id"] == takeoff["candidate_id"]
    assert packet["source_input_id"] == takeoff["source_input_id"]
    assert packet["takeoff_id"] == takeoff["takeoff_id"]
    assert len(packet["unit_rate_estimates"]) == 90
    assert len(packet["material_origin_comparisons"]) == 16
    assert len(packet["regional_concrete_takeoff_estimates"]) == 6
    assert len(estimates) == 6
    assert {row["region"] for row in packet["regional_concrete_takeoff_estimates"]} == {
        "Baghdad", "Al-Muthanna"}
    assert {row["mapped_group_count"] for row in packet["regional_concrete_takeoff_estimates"]} == {81}
    assert {row["mapped_occurrence_count"] for row in packet["regional_concrete_takeoff_estimates"]} == {486}
    expected = {
        ("Baghdad", "2"): "99720", ("Baghdad", "4"): "122220", ("Baghdad", "8"): "167220",
        ("Al-Muthanna", "2"): "95220", ("Al-Muthanna", "4"): "113220", ("Al-Muthanna", "8"): "149220",
    }
    wages = {row["benchmark_key"].split(":")[1]: Decimal(row["unit_price"])
             for row in catalogue.load_catalogue() if row["kind"] == "benchmark"
             and row["benchmark_key"].startswith("iq-cso-2026-07:")
             and ":wage:skilled:" in row["benchmark_key"]}
    for row in packet["unit_rate_estimates"]:
        if row["family"] == "concrete batching":
            hours = Decimal(row["labour_hours_per_output"])
            wage = wages[row["region_slug"]]
            assert Decimal(row["process"]["estimated_unit_cost"]) == (
                (Decimal("64350") + hours * wage) * Decimal("1.20"))
            assert row["process"]["uplift_fraction"] == "0.2"
            assert row["process"]["candidate_takeoff_mapped"] is False
    assert {(region, str(hours)) for region, hours, _ in estimates} == set(expected)
    for region, hours, estimate_packet in estimates:
        assert estimate_packet["candidate_id"] == takeoff["candidate_id"]
        assert estimate_packet["takeoff_id"] == takeoff["takeoff_id"]
        assert estimate_packet["candidate_takeoff_mapped"] is True
        assert estimate_packet["complete_installed_cost"] is None
        assert estimate_packet["unknown_is_zero"] is False
        assert estimate_packet["estimate"]["uplift_fraction"] == "0.2"
    assert packet["takeoff_mapped_for_regional_concrete_estimates"] is True
    assert packet["complete_installed_cost"] is None
    assert packet["physical_qualification"] is None
    assert packet["engineering_accepted"] is False
    assert packet["unknown_is_zero"] is False


def test_2026_september_regional_cost_reference_uses_same_period_materials_and_wages():
    takeoff = inputs.read_json(TAKEOFF)
    records = catalogue.load_catalogue()
    packet, estimates = _make_2026_september_reference(records, takeoff, TAKEOFF)

    assert packet["schema"] == "osr-iraq-domestic-cost-reference/2"
    assert packet["candidate_id"] == takeoff["candidate_id"]
    assert packet["source_input_id"] == takeoff["source_input_id"]
    assert packet["takeoff_id"] == takeoff["takeoff_id"]
    assert packet["basis"]["uplift_fraction"] == "0.20"
    assert packet["basis"]["material_source_basis"].startswith("CSO 2026-09")
    assert packet["basis"]["wage_source_basis"].startswith("CSO 2026-09")
    assert len(packet["unit_rate_estimates"]) == 90
    assert len(packet["regional_concrete_takeoff_estimates"]) == 6
    assert {row["mapped_group_count"] for row in packet["regional_concrete_takeoff_estimates"]} == {81}
    assert {row["mapped_occurrence_count"] for row in packet["regional_concrete_takeoff_estimates"]} == {486}

    expected_takeoff = {
        ("baghdad", "2"): "113580", ("baghdad", "4"): "136080", ("baghdad", "8"): "181080",
        ("al-muthanna", "2"): "109080", ("al-muthanna", "4"): "127080", ("al-muthanna", "8"): "163080",
    }
    assert {(row["region_slug"], row["labour_hours_per_nominal_m3"]):
            row["estimated_unit_cost_iqd_per_nominal_m3"]
            for row in packet["regional_concrete_takeoff_estimates"]} == expected_takeoff

    indexes = {row["record_id"]: row for row in records if row["kind"] == "benchmark"}
    for row in packet["unit_rate_estimates"]:
        process = row["process"]
        assert process["uplift_fraction"] == "0.2"
        assert process["candidate_id"] == takeoff["candidate_id"]
        assert process["input_id"] == takeoff["source_input_id"]
        assert process["candidate_takeoff_mapped"] is False
        if row["family"] == "concrete batching":
            assert Decimal(process["direct_material_cost"]) == Decimal("75900")
            assert any("statistical base-wage observation" in text
                       for text in process["limitations"])
            wage = next(indexes[bench_id] for bench_id in process["benchmark_ids"]
                        if indexes[bench_id].get("labour_category") == "skilled")
            hours = Decimal(row["labour_hours_per_output"])
            expected = (Decimal("75900") + hours * Decimal(wage["unit_price"])) * Decimal("1.20")
            assert Decimal(process["estimated_unit_cost"]) == expected

    for _region, _hours, estimate_packet in estimates:
        assert estimate_packet["candidate_id"] == takeoff["candidate_id"]
        assert estimate_packet["takeoff_id"] == takeoff["takeoff_id"]
        assert estimate_packet["candidate_takeoff_mapped"] is True
        assert estimate_packet["complete_installed_cost"] is None
        assert estimate_packet["unknown_is_zero"] is False
        assert estimate_packet["estimate"]["uplift_fraction"] == "0.2"
    assert packet["complete_installed_cost"] is None
    assert packet["physical_qualification"] is None
    assert packet["engineering_accepted"] is False
    assert packet["unknown_is_zero"] is False


def test_september_ur_aluminium_prices_map_as_separate_mass_sensitivities():
    takeoff = inputs.read_json(TAKEOFF)
    records = catalogue.load_catalogue()
    packet, _ = _make_2026_september_reference(records, takeoff, TAKEOFF)
    scenarios = packet["candidate_mapped_aluminium_stock_scenarios"]

    assert len(scenarios) == 42  # two exact takeoff rollups x seven price forms x three hours/t cases
    assert {row["material"] for row in scenarios} == {"aluminium_reference", "6082-T6-proposed"}
    assert {row["labour_hours_per_stock_tonne"] for row in scenarios} == {"8", "16", "32"}
    assert {row["family"] for row in scenarios} == {"aluminium profile", "aluminium sheet"}
    assert packet["takeoff_mapped_for_aluminium_stock_scenarios"] is True

    benchmarks = {row["benchmark_key"]: row for row in records if row["kind"] == "benchmark"}
    for row in scenarios:
        process = row["process"]
        material = row["material"]
        expected_scope = (
            {"system": "vehicle/body", "material": "aluminium_reference", "stock_scope": "nominal-stock"}
            if material == "aluminium_reference" else
            {"system": "vehicle/passive-secondary", "material": "6082-T6-proposed", "stock_scope": "nominal-stock"}
        )
        assert process["candidate_id"] == takeoff["candidate_id"]
        assert process["input_id"] == takeoff["source_input_id"]
        assert process["candidate_takeoff_id"] == takeoff["takeoff_id"]
        assert process["candidate_takeoff_scope"] == expected_scope
        assert process["candidate_takeoff_mapped"] is True
        assert process["candidate_takeoff_group_count"] == (1164 if material == "aluminium_reference" else 312)
        assert process["candidate_takeoff_occurrence_count"] == (23286 if material == "aluminium_reference" else 312)
        assert process["candidate_takeoff_mass_reconciliation_residual_kg"] == "0"
        assert process["uplift_fraction"] == "0.2"
        assert process["complete_process_cost"] is None
        assert process["complete_installed_cost"] is None
        assert process["unknown_is_zero"] is False
        assert process["source_ids"] == packet["source_ids"] or set(process["source_ids"]).issubset(packet["source_ids"])
        assert any("alloy/temper" in limit for limit in process["limitations"])
        assert any("purchase yield" in limit for limit in process["limitations"])

        price_line = process["material_lines"][0]
        wage_line = process["labour_lines"][0]
        price = Decimal(price_line["unit_rate"])
        hours = Decimal(row["labour_hours_per_stock_tonne"])
        wage = Decimal(wage_line["unit_rate"])
        expected_unit = (price + hours * wage) * Decimal("1.20")
        assert Decimal(process["estimated_unit_cost"]) == expected_unit
        assert Decimal(row["estimated_unit_cost_iqd_per_tonne"]) == expected_unit
        assert Decimal(process["estimated_total"]) == (
            Decimal(row["input_stock_tonnes"]) * expected_unit)
        assert price_line["benchmark_id"] in {b["record_id"] for b in benchmarks.values()}

    # The 6082-T6 label remains a design proposal; none of these generic local
    # stock listings establishes an exact alloy/temper or accepted match.
    assert all("unverified" in row["process"]["material_lines"][0]["material_key"]
               or "unresolved" in row["process"]["material_lines"][0]["material_key"]
               for row in scenarios)
