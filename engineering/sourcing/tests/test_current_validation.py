from engineering.sourcing.current_validation import build_validation


def test_current_index_includes_separately_bound_material_leads_and_logistics():
    packet = build_validation()
    leads = packet["domestic_fabrication"]["additional_local_material_leads"]
    logistics = packet["domestic_fabrication"]["iraq_span_logistics_sensitivity"]
    assert leads["source_count"] == 3
    assert leads["product_count"] == leads["offer_count"] == leads["benchmark_count"] == 0
    assert leads["candidate_product_matches"] == leads["priced_offers"] == 0
    assert logistics["candidate_id"] == packet["procurement_package_bom"]["candidate_id"]
    assert logistics["span_package_count"] == 81
    assert logistics["engineering_occurrence_count"] == 486
    assert logistics["scenario_count"] == 4
    assert logistics["one_trip_one_day_per_span_conditional_iqd"] == "133650000"
    assert logistics["complete_installed_cost"] is None
    assert packet["catalogue"]["offline_seed_record_count"] == 533
