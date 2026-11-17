"""Regression checks for the bounded joined-car digital calculation."""
import json
from math import isclose
from pathlib import Path
import shutil

import pytest

from engineering.vehicle_parts import joined_digital_car as car


ROOT = Path(__file__).resolve().parents[3]


def test_published_packet_reproduces_and_keeps_uncertainty():
    result = car.build(ROOT)
    assert car.encoded(result) == (ROOT / car.OUTPUT).read_bytes()
    assert result["joined_physical_candidate_id"] == "osr-v07-joined-prototype-20261117"
    assert result["physical_accepted"] is False
    assert result["native_joined_FEA_executed"] is False
    assert result["complete_installed_mass_kg_per_car"] is None
    assert result["dynamic_max_axle_reaction_N"] is None
    assert result["method"]["geometry_occurrences_inherited"] > 2000
    assert sum(r["occurrences"] for r in result["component_handoff"]["inherited_modelled_geometry"]) == 2430
    assert sum(r["count_per_car"] for r in result["component_handoff"]["powered_equipment"] if r["nominal_centres_car_m"] is not None) == 10
    assert result["method"]["existing_account_without_CAD_placement_kg"] > 10000
    assert result["normal_analytical"]["mass_kg"][1] < result["conservative_normal_service_ceiling_kg_per_car"]
    assert result["crowd_160_structural_control"]["mass_kg"][1] < result["conservative_crowd_structural_ceiling_kg_per_car"]
    assert result["crowd_160_structural_control"]["mass_kg"][0] > result["normal_analytical"]["mass_kg"][0]


def test_two_support_statics_preserve_weight_and_moment():
    # One central 1000 kg part plus a 100 kg part whose x lies within ±2 m.
    bounded = car._bounds([(1000, [0, 0, 1])], [((100, 100), [[-2, 2], [0, 0], [1, 1]])])
    left = bounded["bogie_reaction_interval_N"]["left_bogie_N"]
    right = bounded["bogie_reaction_interval_N"]["right_bogie_N"]
    assert bounded["mass_kg"] == [1100, 1100]
    assert isclose(left[0] + right[1], 1100 * car.G)
    assert isclose(left[1] + right[0], 1100 * car.G)
    assert isclose(right[1] - left[0], car.G * 100 * 2 / 6.4)


def test_changed_source_is_rejected(tmp_path):
    inp = json.loads((ROOT / car.INPUT).read_bytes())
    for name in inp["source_sha256"]:
        target = tmp_path / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, target)
    target = tmp_path / car.INPUT
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ROOT / car.INPUT, target)
    source = tmp_path / "docs/design-engine/v07-powered-vehicle/plan.json"
    source.write_bytes(source.read_bytes() + b" ")
    with pytest.raises(ValueError, match="Pinned source differs"):
        car.build(tmp_path)
