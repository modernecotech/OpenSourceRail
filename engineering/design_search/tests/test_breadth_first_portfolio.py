from engineering.design_search import design_portfolio, model_cost, quality_diversity, shape_families


def test_shape_matrix_generates_54_distinct_candidates_in_18_cells():
    rows = shape_families.generate()
    assert len(rows) == 54
    assert len({row["candidate"]["candidate_id"] for row in rows}) == 54
    assert len({tuple(sorted(row["descriptor"].items())) for row in rows}) == 18
    assert {row["profile_id"] for row in rows} == {
        "reference", "long-bay-integrated", "dense-braced"}
    assert all(row["candidate"]["parameters"]["length_m"] == 17.0
        and row["candidate"]["parameters"]["cars"] == 6 for row in rows)
    assert len(shape_families.registry()) == 18


def test_candidate_cost_is_class_c_two_shift_body_stock_only():
    row = shape_families.generate()[0]
    spec = design_portfolio.specification()
    estimate = model_cost.assumptions()
    evaluation = design_portfolio._evaluate(row["candidate"], row["descriptor"],
        row["profile_id"], estimate, design_portfolio.ROOT)
    cost = evaluation["cost_estimate"]
    assert cost["production_shifts_per_day"] == 2
    assert cost["production_hours_per_shift"] == 8
    assert cost["estimate_class"] == "C"
    assert cost["scenarios_iqd"]["low"] <= cost["scenarios_iqd"]["base"] <= cost["scenarios_iqd"]["high"]
    assert cost["six_car_body_stock_scenarios_iqd"]["base"] == round(cost["scenarios_iqd"]["base"] * 6, 2)
    assert cost["scope"].startswith("Located nominal body stock factory gate only")
    assert evaluation["complete_installed_mass_kg"] is None
    assert evaluation["complete_installed_cost_iqd"] is None
    assert evaluation["physical_accepted"] is False
    assert spec["operations_scenarios"]["shifts_per_day"] == [2, 2, 3]


def test_quality_diversity_keeps_cell_fronts_and_records_exclusions():
    rows = [
        dict(candidate_id="a" * 64, descriptor=dict(frame="al", shell="skin", ribs="full"),
            metrics=dict(mass=10.0, cost=12.0)),
        dict(candidate_id="b" * 64, descriptor=dict(frame="al", shell="skin", ribs="full"),
            metrics=dict(mass=9.0, cost=15.0)),
        dict(candidate_id="c" * 64, descriptor=dict(frame="gfrp", shell="sandwich", ribs="sparse"),
            metrics=dict(mass=8.0, cost=8.0)),
    ]
    result = quality_diversity.archive(rows, ("mass", "cost"), ("frame", "shell", "ribs"))
    assert result["cell_count"] == 2
    assert set(result["retained_candidate_ids"]) == {"a" * 64, "b" * 64, "c" * 64}
    assert len(result["cross_cell_partial_quantity_pareto_candidate_ids"]) == 1
    assert result["integrated_selection"] is None
