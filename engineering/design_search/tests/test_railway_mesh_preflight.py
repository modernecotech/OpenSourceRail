"""Exact same-candidate mesh preflight; no native solver evidence."""
from engineering.design_search import railway_mesh_preflight as preflight


def test_current_nested_axis_profiles_have_exact_counts_and_keep_resource_hold():
    result = preflight.plan()
    rows = {row["name"]: row for row in result["profiles"]}
    assert [rows[name]["solid_cells"] for name in (
        "reference-0.10625-isotropic", "z-refined-only", "y-refined-only",
        "x-refined-only", "xy-refined", "xz-refined", "yz-refined",
        "uniform-0.053125")] == [128382, 152344, 168612, 190742,
                                   249084, 223728, 199168, 290660]
    assert all(all(row["nested_with_reference_axes"]) for row in rows.values())
    assert rows["z-refined-only"]["solid_cells"] == min(
        row["solid_cells"] for name, row in rows.items()
        if name != "reference-0.10625-isotropic")
    assert all(row["exceeds_previous_cell_budget"] for name, row in rows.items()
               if name != "reference-0.10625-isotropic")
    assert result["solver_invocations"] == 0
    assert result["native_deck_generated"] is False
    assert result["computational_resource_hold"] is True
    assert all(result[key] is False for key in (
        "physical_accepted", "engineering_accepted", "configuration_adopted",
        "manufacturing_release", "operating_release", "physical_journey_completed"))


def test_published_preflight_verifies_without_solver_invocation():
    verified = preflight.verify()
    assert verified["verified"] is True
    assert verified["least_refined_cell_count"] == 152344
    assert verified["solver_invocations"] == 0
    assert verified["computational_resource_hold"] is True
