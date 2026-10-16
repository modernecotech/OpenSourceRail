"""Independent moving influence-line, overhang and rigging controls."""

import math
from copy import deepcopy
import numpy as np
import pytest
from engineering.design_engine import factory_beam as b


def test_single_axle_and_uniform_dead_load_have_exact_midspan_peak():
    r = b.continuous_peak(10, [0], [1000], [(0, 10, 200)])
    assert r["moment_nm"] == pytest.approx(1000 * 10 / 4 + 200 * 10**2 / 8)
    assert r["x_m"] == pytest.approx(5)
    assert r["train_origin_m"] == pytest.approx(5)


def test_two_equal_axles_match_independent_classical_moving_peak():
    r = b.continuous_peak(10, [0, 2], [1000, 1000], [])
    assert r["moment_nm"] == pytest.approx(1000 * (2 * 10 - 2) ** 2 / (8 * 10))
    assert r["x_m"] == pytest.approx(4.5) or r["x_m"] == pytest.approx(5.5)


def test_fixed_section_event_envelope_beats_dense_position_diagnostic():
    L = 12
    offsets = [0, 2, 5.3]
    forces = [700, 1100, 900]
    segments = [(0, L, 100), (0, 0.8, 200)]
    rows = b.section_envelope(L, [1, 4.3, 6, 10], offsets, forces, segments)
    for row in rows["stations"]:
        dense = max(
            b.moment_at(L, row["x_m"], float(t), offsets, forces, segments)
            for t in np.linspace(-6, 12, 1001)
        )
        assert row["maximum_total_moment_nm"] >= dense - 1e-7
        assert row["maximum_total_moment_nm"] - dense < 10
    global_dense = max(
        b.moment_at(L, float(x), float(t), offsets, forces, segments)
        for x in np.linspace(0, L, 81)
        for t in np.linspace(-6, L, 181)
    )
    assert rows["continuous_peak"]["moment_nm"] >= global_dense - 1e-7
    assert rows["continuous_peak"]["moment_nm"] - global_dense < 20


def test_support_reaction_entry_and_exit_events_cover_full_axle_pattern():
    r = b.section_envelope(10, [5], [0, 2], [1000, 2000], [])
    assert r["maximum_total_reaction_n"] == pytest.approx(2800)
    reverse = b.section_envelope(10, [5], [0, 2], [2000, 1000], [])
    assert reverse["maximum_total_reaction_n"] == r["maximum_total_reaction_n"]


def test_overhang_moments_match_uniform_load_closed_forms_and_balance():
    L = 10
    q = 1000
    a = 0.2 * L
    r = b.handling(L, [(0, L, q)], 0.2, 1, 0, 0, 30)
    assert r["station_vertical_reactions_n"] == pytest.approx([q * L / 2] * 2)
    assert r["minimum_bending_moment_nm"] == pytest.approx(-q * a * a / 2)
    assert r["maximum_bending_moment_nm"] == pytest.approx(q * L * (L - 4 * a) / 8)
    assert r["nominal_equalized_leg_tension_n"] == pytest.approx(q * L / 4)
    assert r["two_effective_leg_tension_n"] == pytest.approx(q * L / 2)
    assert r["geometric_headroom_above_longitudinal_end_units_m"] == pytest.approx(
        6 / (2 * math.tan(math.pi / 6))
    )


def test_lower_sling_angles_increase_tension_and_apply_horizontal_demand():
    vertical = b.handling(10, [(0, 10, 1000)], 0.2, 1.25, 100, 0, 30)
    angled = b.handling(10, [(0, 10, 1000)], 0.2, 1.25, 100, 45, 30)
    assert angled["nominal_equalized_leg_tension_n"] == pytest.approx(
        vertical["nominal_equalized_leg_tension_n"] * math.sqrt(2)
    )
    assert angled["nominal_equalized_insert_horizontal_force_n"] == pytest.approx(
        12500 / 4
    )
    assert angled["complete_rig_mass_kg"] is None
    assert angled["hook_equivalent_load_n"] == pytest.approx((10000 + 100 * b.G) * 1.25)


@pytest.mark.parametrize(
    "offsets,forces,segments",
    [([0, 0], [1, 1], []), ([0], [0], []), ([0], [1], [(0, 11, 1)])],
)
def test_invalid_loads_are_rejected(offsets, forces, segments):
    with pytest.raises(ValueError):
        b.continuous_peak(10, offsets, forces, segments)


def test_common_candidate_exposes_adverse_diagnostic_without_adopting_six_car_loads():
    from engineering.analysis.tests.test_design_factory import candidate

    c = candidate()
    s = c["definition"]["beam_demands"]
    assert s["diagnostic_load_case"]["body_count"] == 3
    assert s["diagnostic_load_case"]["current_six_car_axle_loads_n"] is None
    assert s["railway_loading_accepted"] is False
    assert s["minimum_sampled_service_compression_pa"] < 0
    assert c["checks"]["railway_demand_diagnostic"]["state"] == "failed"
    assert c["checks"]["handling_route"]["state"] == "unknown"
    assert s["concrete_compression_limit_pa"] is None
    assert s["handling"]["insert_resistance_n"] is None
    assert s["handling"]["known_beam_mass_kg"] == pytest.approx(
        c["metrics"]["beam_mass_lower_bound_kg"]
    )
    # A downward passage raises top compression. The top minimum occurs with
    # the train off span, while the soffit minimum occurs at maximum moment.
    for row, dead in zip(
        s["railway"]["stations"], c["definition"]["beam"]["stations"], strict=True
    ):
        assert row["top_compression_pa"] == dead["service_dead_only"]["top_pa"]
        assert row["top_maximum_compression_pa"] >= row["top_compression_pa"] - 1e-6
        assert (
            row["soffit_compression_pa"]
            <= dead["service_dead_only"]["soffit_pa"] + 1e-6
        )
    assert c["installed_cost"] is None and c["physical_release"] is False
