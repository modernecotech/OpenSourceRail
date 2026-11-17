"""Focused physical-identity and necessary-bound checks for the powered child."""
from pathlib import Path
import json
import shutil

import pytest

from engineering.vehicle_parts import powered_bogie_prototype as p


def test_separate_child_counts_and_mass_are_provisional():
    result = p.build()
    physical = result["physical_definition"]
    assert result["physical_candidate_id"] != result["selected_parent_candidate_id"]
    assert physical["driven_axles_per_train"] == 24
    assert result["provisional_quote_interface_counts_per_car"]["rail_shoes"] == 4
    assert result["rail_brake_catalogue_reference"]["bare_reference_shoe_mass_kg_per_train"] == 1800
    assert result["mass_budget"]["provisional_equipment_allocation_kg_per_car"] == [1345, 2670]
    assert result["mass_budget"]["installed_CG_m"] is None
    assert result["physical_accepted"] is False
    assert result["selected_reference_changed"] is False


def test_full_independent_stop_counts_one_failed_module():
    result = p.build()
    brake = result["independent_brake_demand"]
    assert brake["required_per_module_N_with_one_of_twelve_unavailable"] == pytest.approx(
        brake["required_total_rail_brake_force_N"] / 11)
    assert brake["required_per_module_N_with_one_of_twelve_unavailable"] > 10000
    assert brake["peak_thermal_power_per_active_module_W"] > 200000
    assert brake["verified_rail_compatibility"] is False
    assert result["rail_brake_catalogue_reference"]["longitudinal_braking_force_N"] is None


def test_parent_selection_change_invalidates_child(tmp_path):
    for relative in (p.PLAN, p.EVALUATION, p.MANIFEST):
        destination = tmp_path / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(p.ROOT / relative, destination)
    plan = tmp_path / p.PLAN
    value = json.loads(plan.read_text())
    value["selection_id"] = "changed-selection"
    plan.write_text(json.dumps(value))
    with pytest.raises(ValueError, match="Selected representative-car plan identity differs"):
        p.build(tmp_path)
