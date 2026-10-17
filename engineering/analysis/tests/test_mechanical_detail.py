"""Independent equilibrium, beam, connection, geometry and feedback checks."""

from copy import deepcopy
import json
import math

import numpy as np
import pytest

from engineering.factory_examples.models import volume
from engineering.generative_design import mechanical_detail as m


@pytest.fixture(scope="module")
def contexts():
    return m.contexts()


@pytest.fixture(scope="module")
def campaign():
    return m.run()


def checks(candidate):
    return {row["id"]: row for row in candidate["checks"]}


def test_full_length_beam_matches_independent_finite_element_solution():
    # Independent Euler-Bernoulli FE assembly includes both physical overhangs.
    length, force, ei, elements = 10.0, 20000.0, 1.0e6, 100
    dx = length / elements
    stiffness = np.zeros((2 * (elements + 1), 2 * (elements + 1)))
    loads = np.zeros(2 * (elements + 1))
    local = (
        ei
        / dx**3
        * np.array(
            [
                [12, 6 * dx, -12, 6 * dx],
                [6 * dx, 4 * dx**2, -6 * dx, 2 * dx**2],
                [-12, -6 * dx, 12, -6 * dx],
                [6 * dx, 2 * dx**2, -6 * dx, 4 * dx**2],
            ]
        )
    )
    element_load = (
        force / length * np.array([-dx / 2, -(dx**2) / 12, -dx / 2, dx**2 / 12])
    )
    for i in range(elements):
        ids = np.arange(2 * i, 2 * i + 4)
        stiffness[np.ix_(ids, ids)] += local
        loads[ids] += element_load
    restrained = [40, 160]  # x = 2 and 8 m; rotations free
    free = np.array([j for j in range(len(loads)) if j not in restrained])
    displacement = np.zeros_like(loads)
    displacement[free] = np.linalg.solve(stiffness[np.ix_(free, free)], loads[free])
    reaction = stiffness @ displacement - loads
    actual = m.overhang_beam(length, [2.0, 8.0], force, ei)
    assert actual["reactions_n"] == pytest.approx(reaction[restrained], rel=1e-7)
    assert actual["maximum_abs_deflection_m"] == pytest.approx(
        max(abs(displacement[::2])), rel=1e-6
    )
    assert actual["deflection_at_supports_m"] == pytest.approx([0, 0], abs=1e-13)
    assert abs(actual["force_balance_error_n"]) < 1e-9
    assert abs(actual["first_moment_balance_error_nm"]) < 1e-9


def test_beam_reduces_to_closed_form_simple_span_and_rejects_asymmetry():
    beam = m.overhang_beam(4.0, [0.0, 4.0], 1000.0, 2e6)
    assert beam["maximum_abs_deflection_m"] == pytest.approx(
        5 * 250 * 4**4 / (384 * 2e6)
    )
    assert beam["maximum_abs_moment_nm"] == pytest.approx(250 * 4**2 / 8)
    with pytest.raises(ValueError, match="symmetric"):
        m.overhang_beam(4.0, [1.0, 3.5], 1000.0, 2e6)


def test_configuration_separation_loads_and_envelopes(contexts):
    lm3, six = contexts
    assert (lm3["body_count"], lm3["axle_count"]) == (3, 12)
    assert (six["body_count"], six["axle_count"]) == (6, 24)
    assert lm3["body_length_m"] == 16.5
    assert six["body_length_m"] == 18.5
    assert lm3["source_car_mass_kg"] == 35250
    assert six["source_car_mass_kg"] == 64000
    left = m.assess(m.seed(lm3), lm3)
    right = m.assess(m.seed(six), six)
    assert left["id"] != right["id"]
    assert checks(left)["source_side_depth_envelope"]["state"] == "pass"
    assert checks(right)["source_side_depth_envelope"]["state"] == "unknown"
    assert right["metrics"]["modeled_car_mass_kg"] > 64000
    assert "LM3-BDY-P010" not in right["component_ids"]


def test_every_part_mass_increases_applied_force_and_no_original_mass_removed(contexts):
    ctx = contexts[0]
    row = m.assess(m.seed(ctx), ctx)
    total = sum(volume(p) * 7850 for p in row["geometry"]["parts"])
    assert row["objectives"]["mass_kg"] == pytest.approx(total)
    assert row["metrics"]["modeled_car_force_n"] == pytest.approx(
        ctx["source_car_force_n"] + total * 9.80665
    )
    assert row["metrics"]["modeled_car_mass_kg"] == pytest.approx(
        ctx["source_car_mass_kg"] + total
    )
    assert row["basis"]["no_original_structure_mass_subtracted"] is True
    thick = m.seed(ctx)
    thick["spine_wall_m"] = 0.016
    changed = m.assess(thick, ctx)
    assert changed["objectives"]["mass_kg"] > row["objectives"]["mass_kg"]
    assert (
        changed["connections"]["vertical_reactions_n"][0]
        > row["connections"]["vertical_reactions_n"][0]
    )
    assert (
        changed["connections"]["longitudinal_reaction_shares"]
        != row["connections"]["longitudinal_reaction_shares"]
    )


def test_vertical_pad_bearing_and_horizontal_bolt_group_are_distinct(contexts):
    ctx = contexts[0]
    v = m.seed(ctx)
    row = m.assess(v, ctx)
    horizontal = row["metrics"]["modeled_car_mass_kg"] * 2.943 / 2
    assert row["connections"]["bolt_shear_per_bolt_n"] == pytest.approx(horizontal / 4)
    assert row["connections"]["bolt_tension_per_bolt_n"] == pytest.approx(
        horizontal / (4 * 0.1)
    )
    before = checks(row)["support_bolt_combined_nominal_stress"]["value"]
    v["bolts_per_support"] = 8
    after = m.assess(v, ctx)
    assert checks(after)["support_bolt_combined_nominal_stress"][
        "value"
    ] == pytest.approx(before / 2, rel=2e-5)
    assert (
        checks(after)["socket_neighbour_access"]["limit"]
        < checks(row)["socket_neighbour_access"]["limit"]
    )
    assert after["connections"]["qualified"] is False


def test_hold_down_holes_continue_through_pad_and_bolster_flange(contexts):
    ctx = contexts[0]
    row = m.assess(m.seed(ctx), ctx)
    model = m.model_definition(row)
    ids = [p["id"] for p in model["parts"]]
    assert len(ids) == len(set(ids))
    assert all(volume(p) > 0 for p in model["parts"])
    for j in [1, 2]:
        pad = next(p for p in model["parts"] if p["id"] == f"bogie-interface-pad-{j}")
        flange = next(p for p in model["parts"] if p["id"] == f"bolster-{j}-lower")
        assert len(pad["holes"]) == len(flange["holes"]) == 4
        for ph, fh in zip(pad["holes"], flange["holes"]):
            assert [
                pad["at_m"][k] + ph[key] for k, key in enumerate(["x_m", "y_m"])
            ] == pytest.approx(
                [flange["at_m"][k] + fh[key] for k, key in enumerate(["x_m", "y_m"])]
            )
            assert ph["diameter_m"] == fh["diameter_m"]
        assert pad["at_m"][2] + pad["size_m"][2] == pytest.approx(flange["at_m"][2])
    assert any("end-closure" in p["id"] for p in model["parts"])
    assert model["physical_release"] is False


def test_machine_cutting_length_repair_adds_unqualified_splices(contexts):
    ctx = contexts[0]
    seed = m.seed(ctx)
    row = m.assess(seed, ctx)
    assert checks(row)["xp4000_plate_length"]["state"] == "fail"
    for stock in [7.8, 3.8]:
        seed["maximum_stock_piece_length_m"] = stock
        row = m.assess(seed, ctx)
    assert checks(row)["xp4000_plate_length"]["state"] == "pass"
    assert row["metrics"]["butt_interfaces_per_longitudinal_plate"] > 0
    assert checks(row)["qualified_plate_splices_and_welds"]["state"] == "unknown"
    assert checks(row)["machine_and_stock_order_configuration"]["state"] == "unknown"
    assert (
        row["manufacturing"]["tolerances"]["exact_machine_capability_demonstrated"]
        is False
    )


def test_feedback_public_api_recomputes_plain_bounded_variables(contexts):
    ctx = contexts[0]
    row = m.assess(m.seed(ctx), ctx)
    proposed = m.propose(row, ctx)
    assert len(proposed) > 1
    assert all(
        set(v) == set(row["variables"]) and v != row["variables"] for v in proposed
    )
    children = [m.assess(v, ctx) for v in proposed]
    assert len({x["id"] for x in children}) == len(children)
    assert any(
        x["metrics"]["modeled_car_force_n"] != row["metrics"]["modeled_car_force_n"]
        for x in children
    )
    assert any(
        x["variables"]["side_depth_m"] > 0.26
        and checks(x)["source_side_depth_envelope"]["state"] == "fail"
        for x in children
    )
    bad = deepcopy(proposed[0])
    bad["side_depth_m"] = float("nan")
    with pytest.raises(ValueError, match="bounded"):
        m.assess(bad, ctx)


def test_campaign_keeps_failed_parents_unknowns_and_bounded_termination(campaign):
    rows = campaign["candidates"]
    by_id = {r["id"]: r for r in rows}
    assert len(rows) > 20
    assert len(by_id) == len(rows)
    assert any(r["failed_check_ids"] for r in rows)
    for configuration in {r["configuration_id"] for r in rows}:
        family = [r for r in rows if r["configuration_id"] == configuration]
        initial = next(r for r in family if r["round"] == 0)
        # Progress must come from feedback, but a bounded budget must never
        # require the code to invent a passing physical design.
        assert min(len(r["failed_check_ids"]) for r in family) < len(
            initial["failed_check_ids"]
        )
    for row in rows:
        assert row["unknown_check_ids"]
        assert (
            row["physical_release"]
            is row["manufacturing_release"]
            is row["engineering_design_complete"]
            is False
        )
        if row["parent_id"]:
            parent = by_id[row["parent_id"]]
            assert parent["configuration_id"] == row["configuration_id"]
            assert parent["round"] < row["round"]
            assert parent["failed_check_ids"]
            assert row["variables"] != parent["variables"]
            assert row["repair_reason"]
    for history in campaign["iteration_history"]:
        assert history["evaluations"] <= 80
        assert history["full_cartesian_domain_exhausted"] is False
        assert history["completed_design"] is False
    assert all(
        not choice["accepted"] for choice in campaign["proposed_review_candidates"]
    )


def test_manufacturing_definition_and_supplier_origin_are_not_fabricated(contexts):
    row = m.assess(m.seed(contexts[0]), contexts[0])
    manufacturing = row["manufacturing"]
    assert {d["id"] for d in manufacturing["datums"]} == {"A", "B", "C"}
    assert len(manufacturing["bom"]) == len(row["geometry"]["parts"])
    assert manufacturing["released"] is False
    assert any("portable milling" in step for step in manufacturing["sequence"])
    lead = manufacturing["machine_leads"][0]
    assert lead["published_cutting_area_m"] == [4.0, 2.0]
    assert lead["published_maximum_thickness_m"] == 0.032
    assert "USA" in lead["origin_basis"] and "Germany" in lead["origin_basis"]
    assert "unconfirmed" in manufacturing["machine_leads"][1]["origin_class"]
    assert all(
        not lead["adopted_or_ordered"] for lead in manufacturing["machine_leads"]
    )


def test_run_writes_reproducible_native_definitions(tmp_path, campaign):
    written = m.run(tmp_path)
    assert written == campaign
    assert json.loads((tmp_path / "mechanical-detail.json").read_text()) == written
    assert len(list(tmp_path.glob("*-model.json"))) == 2


def test_assess_rejects_mutated_dimensions_loads_and_source_hashes(contexts):
    ctx = contexts[0]
    for key, value in [
        ("body_length_m", 10.0),
        ("source_car_force_n", 1.0),
        ("support_x_m", [1.0, 15.5]),
        ("configuration_id", "invented"),
    ]:
        changed = deepcopy(ctx)
        changed[key] = value
        with pytest.raises(ValueError, match="exact current mechanical context"):
            m.assess(m.seed(ctx), changed)
    changed = deepcopy(ctx)
    changed["source_sha256"][next(iter(changed["source_sha256"]))] = "0" * 64
    with pytest.raises(ValueError, match="exact current mechanical context"):
        m.assess(m.seed(ctx), changed)


def test_sixcar_envelope_reuses_geometry_and_adds_all_gross_mass_once(contexts):
    ctx = contexts[1]
    row = m.assess(m.seed(ctx), ctx)
    baseline, envelope = row["metrics"]["load_case_responses"]
    assert baseline["original_train_mass_kg"] == 384000
    assert envelope["original_train_mass_kg"] == 460800
    assert (
        baseline["added_gross_steel_per_car_kg"]
        == envelope["added_gross_steel_per_car_kg"]
        == row["objectives"]["mass_kg"]
    )
    expected = (460800 / 6 + row["objectives"]["mass_kg"]) * 9.80665
    assert sum(envelope["beam"]["reactions_n"]) == pytest.approx(expected)
    assert (
        sum(envelope["beam"]["reactions_n"]) / sum(baseline["beam"]["reactions_n"])
        < 1.2
    )
    cc = checks(row)
    assert (
        cc["planning-six-car-460800kg/global_service_deflection"]["value"]
        > cc["global_service_deflection"]["value"]
    )
    assert (
        cc["planning-six-car-460800kg/support_bolt_combined_nominal_stress"]["value"]
        > cc["support_bolt_combined_nominal_stress"]["value"]
    )
    isolated = deepcopy(row)
    isolated["failed_check_ids"] = [
        "planning-six-car-460800kg/global_service_deflection"
    ]
    assert m.propose(isolated, ctx)


def test_short_native_members_do_not_close_full_body_stiffness_geometry(contexts):
    for ctx in contexts:
        row = m.assess(m.seed(ctx), ctx)
        gate = checks(row)["end_load_transfer_and_stiffness_geometry"]
        assert gate["state"] == "unknown"
        assert "not verified exact native geometry" in gate["basis"]
        assert ctx["side_member_length_m"] < ctx["body_length_m"]
        assert ctx["centre_member_length_m"] < ctx["body_length_m"]


def test_solid_envelope_upper_inertia_and_lower_deflection_bound(contexts):
    bound = m.stiffness_bound(contexts[0])
    # Independent integration about fixed z=.19m, with side solids at opposite
    # vertical extremes. Their combined centroid is exactly that fixed axis.
    rectangles = [(0.18, 0.0, 0.26), (0.22, 0.0, 0.38), (0.18, 0.12, 0.38)]
    expected = sum(
        width * ((upper - 0.19) ** 3 - (lower - 0.19) ** 3) / 3
        for width, lower, upper in rectangles
    )
    assert bound["inertia_upper_bound_m4"] == pytest.approx(expected)
    assert expected == pytest.approx(0.0018702266666666668)
    # An independent two-sided Macaulay integration at symmetry gives midspan
    # displacement; no call to the module's beam evaluator is used here.
    length, a, b, force = 16.5, 2.1, 14.4, 345802.5
    q = force / length
    reaction = force / 2
    ei = 200e9 * expected

    def raw(x):
        return (
            -q * x**4 / 24
            + reaction * max(0, x - a) ** 3 / 6
            + reaction * max(0, x - b) ** 3 / 6
        )

    c1 = (raw(a) - raw(b)) / (b - a)
    c2 = -raw(a) - c1 * a
    independent = abs((raw(length / 2) + c1 * length / 2 + c2) / ei)
    assert bound["deflection_lower_bound_within_constant_ei_family_m"] == pytest.approx(
        independent
    )
    assert independent == pytest.approx(0.014362157215472725)
    assert independent > bound["unaccepted_research_deflection_target_m"] == 0.0123
    assert bound["research_family_screen_incompatible"] is True
    assert bound["parallel_axis_terms_included"] is True
    assert bound["added_self_mass_for_bound_kg"] == 0
    assert "constant-EI research family" in bound["limitation"]
    assert m.stiffness_bound(contexts[1]) is None
    row = m.assess(m.seed(contexts[0]), contexts[0])
    assert row["basis"]["constant_ei_family_stiffness_bound"] == bound


def test_actual_750mm_sixcar_feedback_repairs_m24_to_m27_with_same_limits(contexts):
    ctx = contexts[1]
    previous = dict(
        bolster_depth_m=0.45,
        bolt_diameter_m=0.024,
        bolts_per_support=8,
        crossbearer_pitch_m=1.8,
        diaphragm_thickness_m=0.012,
        maximum_stock_piece_length_m=3.8,
        plate_thickness_m=0.016,
        side_depth_m=0.75,
        spine_wall_m=0.016,
        web_thickness_m=0.016,
        weld_throat_m=0.004,
    )
    before = m.assess(previous, ctx)
    bc = checks(before)
    governing = "planning-six-car-460800kg/support_bolt_combined_nominal_stress"
    assert bc[governing]["state"] == "fail"
    assert bc[governing]["value"] == pytest.approx(458916592.9737184)
    proposed = m.propose(before, ctx)
    larger = next(v for v in proposed if v["bolt_diameter_m"] == 0.027)
    assert {key for key in previous if previous[key] != larger[key]} == {
        "bolt_diameter_m"
    }
    after = m.assess(larger, ctx)
    ac = checks(after)
    assert ac[governing]["value"] == pytest.approx(
        458916592.9737184 * 353 / 459, rel=1e-4
    )
    assert ac[governing]["limit"] == bc[governing]["limit"] == 400e6
    assert ac[governing]["state"] == "pass"
    assert after["failed_check_ids"] == []
    assert after["connections"]["bolt_coarse_pitch_m"] == 0.003
    assert (
        after["connections"]["requested_bolt_property_class"]
        == before["connections"]["requested_bolt_property_class"]
    )
    assert after["connections"]["bolt_tensile_area_m2"] == 459e-6
    for name in [
        "bolt_hole_edge_distance",
        "socket_neighbour_access",
        "support_pad_bearing",
        "planning-six-car-460800kg/support_pad_bearing",
        "xp4000_plate_length",
        "xp4000_plate_thickness",
    ]:
        assert ac[name]["state"] == "pass"
    assert ac["support_pad_bearing"]["value"] > bc["support_pad_bearing"]["value"]
    assert (
        ac["socket_neighbour_access"]["value"] > bc["socket_neighbour_access"]["value"]
    )
    assert (
        ac["bolt_hole_edge_distance"]["value"] > bc["bolt_hole_edge_distance"]["value"]
    )
    # Holes are actual geometry in both paired plates; changed diameters alter
    # net fabricated mass and all loadcases are re-evaluated on that new mass.
    assert after["objectives"]["mass_kg"] < before["objectives"]["mass_kg"]
    for name in [
        "bogie-interface-pad-1",
        "bogie-interface-pad-2",
        "bolster-1-lower",
        "bolster-2-lower",
    ]:
        pad = next(p for p in after["geometry"]["parts"] if p["id"] == name)
        assert len(pad["holes"]) == 8
        assert all(
            hole["diameter_m"] == pytest.approx(0.027 * 1.1) for hole in pad["holes"]
        )
    assert ac["bogie_mating_interface_and_bolt_qualification"]["state"] == "unknown"
    assert ac["complete_assembled_mass_and_fastener_origin"]["state"] == "unknown"
    lead = next(
        lead
        for lead in after["manufacturing"]["machine_leads"]
        if lead["id"] == "smith-bullough-fasteners"
    )
    assert lead["offered_m27_configuration"] is None
    assert lead["adopted_or_ordered"] is False
    assert after["manufacturing_release"] is after["physical_release"] is False


def test_plate_and_future_fastener_envelope_material_requests_are_distinct(contexts):
    row = m.assess(m.seed(contexts[0]), contexts[0])
    plate = row["materials"]["request"]
    bolt = row["materials"]["fastener_request"]["property_class_requested"]
    assert plate.startswith("S355")
    assert (
        bolt
        == row["connections"]["requested_bolt_property_class"]
        == "8.8 proposed-unaccepted"
    )
    assert all(
        p["material_request"] == plate and p["material_request_accepted"] is False
        for p in row["geometry"]["parts"]
    )
    assert all(
        p["material_request"] == plate and p["material_request_accepted"] is False
        for p in row["manufacturing"]["bom"]
    )
    # These representative future envelope records exercise metadata handling;
    # actual candidate geometry continues to omit bolts and heads explicitly.
    envelopes = [
        dict(id="plate-datum", role="provisional-fabricated-plate"),
        dict(id="bolt-shank-1", role="provisional-bolt-envelope"),
        dict(id="bolt-head-1", role="provisional-bolt-head-envelope"),
    ]
    m._assign_material_requests(envelopes, plate, bolt)
    assert [p["material_request"] for p in envelopes] == [plate, bolt, bolt]
    assert all(p["material_request_accepted"] is False for p in envelopes)
    assert row["materials"]["fastener_request"]["grade_and_origin_confirmed"] is False
