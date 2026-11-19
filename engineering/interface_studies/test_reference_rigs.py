from math import hypot, isclose

from reference_rigs import brake_case, brake_schedule, datum_schedule


def test_door_symmetry_and_worn_wheel_heights():
    rig = datum_schedule()
    doors = rig["door_centres_train_x_m"]
    assert len(doors) == 12 and doors == [-x for x in reversed(doors)]
    new, worn, levelled = rig["vertical_setups"]
    assert worn["fin_bottom_z_m"] < 0 < levelled["fin_bottom_z_m"]
    assert isclose(new["floor_z_m"] - worn["floor_z_m"], 0.040)
    assert worn["axle_z_m"] == levelled["axle_z_m"]
    assert levelled["floor_z_m"] == new["floor_z_m"]


def test_delayed_downhill_braking_energy_conservation():
    grade = 0.02
    for row in brake_schedule()["cases"]:
        mass = row["analytical_mass_kg"]
        expected = mass * (20 ** 2 / 2 + row["stop_distance_m"] * 9.80665 * grade / hypot(1, grade))
        assert isclose(11 * row["interface_energy_J_per_active_module"], expected)
    level = brake_case(1000, 10, 0, 1, 2, 1)
    assert level["stop_distance_m"] == 70


def test_sideframe_corner_projection_against_sill():
    rows = datum_schedule()["sideframe_sweep"]
    for row in rows:
        radius = row["curve_radius_m"]
        sine = 6.4 / radius if radius else 0.
        gap = 1.01 - (1.25 * sine + (1 - sine*sine)**0.5)
        assert isclose(row["minimum_sideframe_to_sill_gap_m"], gap, abs_tol=1e-12)


def test_shifted_jig_trades_sill_clearance_for_hub_clearance():
    rig = datum_schedule()
    original = rig["sideframe_sweep"]
    moved = rig["adjustable_jig"]["sweep"]
    assert moved[2]["minimum_sideframe_to_sill_gap_m"] > 0
    assert moved[3]["minimum_sideframe_to_sill_gap_m"] < 0
    assert isclose(moved[0]["minimum_hub_to_sideframe_gap_m"], 0.0075)
    assert isclose(original[0]["minimum_hub_to_sideframe_gap_m"]
                   - moved[0]["minimum_hub_to_sideframe_gap_m"], 0.035)
