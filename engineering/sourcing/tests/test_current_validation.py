from engineering.sourcing.current_validation import build_validation


def test_current_index_includes_separately_bound_material_leads_and_logistics():
    packet = build_validation()
    leads = packet["domestic_fabrication"]["additional_local_material_leads"]
    logistics = packet["domestic_fabrication"]["iraq_span_logistics_sensitivity"]
    local_gfrp = packet["domestic_fabrication"]["local_composite_retail_cost_screen"]
    historical_labour = packet["domestic_fabrication"]["historical_labour_earnings_reference"]
    assert leads["source_count"] == 5
    assert leads["product_count"] == leads["offer_count"] == leads["benchmark_count"] == 0
    assert leads["candidate_product_matches"] == leads["priced_offers"] == 0
    assert logistics["candidate_id"] == packet["procurement_package_bom"]["candidate_id"]
    assert logistics["span_package_count"] == 81
    assert logistics["engineering_occurrence_count"] == 486
    assert logistics["scenario_count"] == 4
    assert logistics["one_trip_one_day_per_span_conditional_iqd"] == "133650000"
    assert logistics["complete_installed_cost"] is None
    assert local_gfrp["mass_equivalent_fabric_pack_count"] == 89
    assert local_gfrp["partial_cost_iqd_per_10m2"] == ["463800.00", "553800.00", "733800.00"]
    assert local_gfrp["resin_cost_included"] is False
    assert local_gfrp["complete_fabrication_cost_iqd"] is None
    assert historical_labour["benchmark_count"] == 4
    assert historical_labour["used_in_current_2025_2026_cost_scenarios"] is False
    assert packet["catalogue"]["offline_seed_record_count"] == 533
