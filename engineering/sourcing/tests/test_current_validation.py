from engineering.sourcing.current_validation import build_validation


def test_current_index_includes_separately_bound_material_leads_and_logistics():
    packet = build_validation()
    leads = packet["domestic_fabrication"]["additional_local_material_leads"]
    logistics = packet["domestic_fabrication"]["iraq_span_logistics_sensitivity"]
    local_gfrp = packet["domestic_fabrication"]["local_composite_retail_cost_screen"]
    historical_labour = packet["domestic_fabrication"]["historical_labour_earnings_reference"]
    wage_history_2024 = packet["domestic_fabrication"]["construction_wage_history_2024"]
    procurement = packet["procurement_package_bom"]
    concrete = procurement["concrete_material_input_takeoff"]
    assert leads["source_count"] == 11
    assert "iraq.regaasphalt.aggregate" in leads["source_ids"]
    assert "iraq.hewa.construction-materials" in leads["source_ids"]
    assert "iraq.lafarge-iraq.cement-products" in leads["source_ids"]
    assert "iraq.alpha-steel.rebar-range-2026" in leads["source_ids"]
    assert "iraq.al-kanz.precast-piling" in leads["source_ids"]
    assert "iraq.hadeediraq.rebar-marketplace" in leads["source_ids"]
    assert leads["product_count"] == leads["offer_count"] == leads["benchmark_count"] == 0
    assert leads["candidate_product_matches"] == leads["priced_offers"] == 0
    assert logistics["candidate_id"] == packet["procurement_package_bom"]["candidate_id"]
    assert logistics["procurement_bom_packet_id"] == procurement["packet_id"]
    assert logistics["path"].endswith("logistics-2026-september-v6/iraq-span-logistics-sensitivity.json")
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
    assert wage_history_2024["benchmark_count"] == 90
    assert wage_history_2024["governorate_count"] == 15
    assert wage_history_2024["worker_category_count"] == 6
    assert wage_history_2024["baghdad_skilled_daily_iqd_per_workday"] == 75000
    assert wage_history_2024["baghdad_skilled_hourly_iqd_per_hour"] == "9375"
    assert wage_history_2024["used_in_current_2025_2026_cost_scenarios"] is False
    assert wage_history_2024["employer_burden_included"] is False
    assert wage_history_2024["historical_only"] is True
    assert procurement["path"].endswith("federated-v06-research-packages-v21.json.gz")
    assert procurement["candidate_mapped_copper_sensitivity_scenario_count"] == 3
    copper = procurement["copper_imported_raw_stock_sensitivity"]
    assert copper["engineering_group_count"] == 5
    assert copper["engineering_occurrence_count"] == 10
    assert copper["scenario_totals_iqd"] == ["90192658.13", "91034539.73", "92718302.93"]
    assert copper["compatible_supplier_match"] is False
    assert copper["complete_installed_cost"] is None
    assert procurement["source_registry_record_count"] == 95
    assert procurement["domestic_source_lead_association_count"] == 45
    assert concrete["package_count"] == 81
    assert concrete["manufacturing_group_count"] == 81
    assert concrete["engineering_occurrence_count"] == 486
    assert concrete["ingredient_line_count"] == 243
    assert abs(float(concrete["nominal_output_volume_m3"]) - 1804.8096) < 1e-8
    assert all(abs(float(row["total_recipe_input_quantity"]) - expected) < 1e-8
               for row, expected in zip(concrete["material_inputs"],
                                        (631.68336, 902.4048, 1443.84768)))
    assert concrete["labour_hours_per_nominal_m3"] == ["2", "4", "8"]
    assert concrete["uplift_fraction_on_direct_material_plus_labour"] == "0.20"
    assert concrete["commercial_order_quantity_known"] is False
    assert concrete["mix_design_approved"] is False
    assert concrete["complete_installed_cost"] is None
    assert concrete["non_additive_to_output_concrete_stock"] is True
    assert packet["catalogue"]["offline_seed_record_count"] == 533
