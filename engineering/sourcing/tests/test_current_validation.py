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
    fabrication_sources = packet["domestic_fabrication"]["additional_manufacturing_discovery_leads"]
    station_rfq = packet["station_drive_rfq_scope"]
    assert leads["source_count"] == 18
    assert "iraq.regaasphalt.aggregate" in leads["source_ids"]
    assert "iraq.hewa.construction-materials" in leads["source_ids"]
    assert "iraq.lafarge-iraq.cement-products" in leads["source_ids"]
    assert "iraq.alpha-steel.rebar-range-2026" in leads["source_ids"]
    assert "iraq.al-kanz.precast-piling" in leads["source_ids"]
    assert "iraq.hadeediraq.rebar-marketplace" in leads["source_ids"]
    assert "iraq.diwan-electrical-industries" in leads["source_ids"]
    assert "iraq.erbil-copper-cable" in leads["source_ids"]
    assert leads["feeder_cable_quantity_unmapped_source_leads"] == ["iraq.alrowad-cables"]
    assert "iraq.rs-alnajaf-electrical-factory" in leads["source_ids"]
    assert "iraq.ibn-majid-heavy-engineering" in leads["source_ids"]
    assert "iraq.haidar-ahmed-mousa.pur-pir-panels" in leads["source_ids"]
    assert "iraq.kanza-iq.sandwich-panel-lines" in leads["source_ids"]
    assert leads["product_count"] == leads["offer_count"] == leads["benchmark_count"] == 0
    assert leads["candidate_product_matches"] == leads["priced_offers"] == 0
    assert fabrication_sources["source_count"] == 3
    assert set(fabrication_sources["source_ids"]) == {
        "iraq.ms-cable-busbar", "iraq.asas-global-aluminium", "iraq.nubin-grp-facade"}
    assert fabrication_sources["product_count"] == fabrication_sources["offer_count"] == 0
    assert fabrication_sources["supplier_quotes"] == fabrication_sources["compatible_products"] == 0
    assert fabrication_sources["engineering_approval"] is False
    assert station_rfq["candidate_id"] == procurement["candidate_id"]
    assert station_rfq["evaluation_id"] == procurement["evaluation_id"]
    assert station_rfq["bank_scope_count"] == 5
    assert station_rfq["located_primary_occurrence_count"] == 2430
    assert station_rfq["non_additive_open_account_link_count"] == 20
    assert station_rfq["service_scenario_count"] == 8
    assert station_rfq["candidate_level_copper_material_labour_plus_20_iqd"] == [
        "90192658.13", "91034539.73", "92718302.93"]
    assert station_rfq["air_gap_adapter_extension_required"] is True
    assert station_rfq["frequency_map_field_required"] is True
    assert station_rfq["supplier_offers"] == station_rfq["supplier_communications_sent"] == 0
    assert station_rfq["complete_drive_installed_cost"] is None
    assert station_rfq["physical_accepted"] is False
    assert station_rfq["selected_reference_changed"] is False
    assert logistics["candidate_id"] == packet["procurement_package_bom"]["candidate_id"]
    assert logistics["procurement_bom_packet_id"] == procurement["packet_id"]
    assert logistics["path"].endswith("logistics-2026-september-v9/iraq-span-logistics-sensitivity.json")
    assert logistics["span_package_count"] == 81
    assert logistics["engineering_occurrence_count"] == 486
    assert logistics["scenario_count"] == 4
    assert logistics["one_trip_one_day_per_span_conditional_iqd"] == "133650000"
    assert logistics["complete_installed_cost"] is None
    assert local_gfrp["mass_equivalent_fabric_pack_count"] == 89
    assert local_gfrp["partial_cost_iqd_per_10m2"] == ["463800.00", "553800.00", "733800.00"]
    assert local_gfrp["resin_cost_included"] is False
    assert local_gfrp["conditional_resin_scenario_count"] == 9
    assert local_gfrp["conditional_resin_costs_are_compatible_quotes"] is False
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
    assert procurement["path"].endswith("federated-v06-research-packages-v24.json.gz")
    assert procurement["candidate_mapped_copper_sensitivity_scenario_count"] == 3
    copper = procurement["copper_imported_raw_stock_sensitivity"]
    assert copper["engineering_group_count"] == 5
    assert copper["engineering_occurrence_count"] == 10
    assert copper["scenario_totals_iqd"] == ["90192658.13", "91034539.73", "92718302.93"]
    assert copper["compatible_supplier_match"] is False
    assert copper["complete_installed_cost"] is None
    assert procurement["source_registry_record_count"] == 101
    assert procurement["domestic_source_lead_association_count"] == 52
    copper_scope = next(row for row in packet["candidate_sourcing_sensitivity"]["ranked_partial_scenario_exposures"]
                        if (row["system"], row["material"]) == ("wayside/primary", "copper-conductor"))
    assert "iraq.erbil-copper-cable" in copper_scope["source_lead_keys"]
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
    mass_priority = packet["selected_reference_mass_reconciliation_priority"]
    assert mass_priority["candidate_id"] != procurement["candidate_id"]
    assert mass_priority["mass_uncertainty_bounds_available"] is False
    assert mass_priority["numeric_mass_sensitivity_rank_count"] == 0
    assert mass_priority["research_candidate_cost_ranks_combined"] is False
    assert mass_priority["account_reconciliation_investigation_queue"][0]["account_id"] == "retained-comfort/body"
    assert mass_priority["account_reconciliation_investigation_queue"][0]["accounting_residual_kg"] == "4873.076704474921"
    assert mass_priority["summary"]["complete_installed_mass_kg"] is None
