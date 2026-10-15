"""Whole-passage coverage and real modal/mount conservation boundaries."""

from copy import deepcopy
import json
import gzip

import pytest

from engineering.design_engine.vehicle_confirmation import (
    passage_plan,
    assembly_diagnostics,
    joint_cycles,
    complete_coverage,
)


def simple_model():
    return dict(
        family_definition=dict(cars=[dict(start_x_m=0.0, length_m=10.0)]),
        bridge=dict(
            span_count=1, candidate=dict(definition=dict(deck=dict(span_m=20.0)))
        ),
    )


def motion(speed=10.0, acceleration=0.0):
    return dict(
        traffic=[
            dict(
                id="a",
                initial_advance_m=45.0,
                arrival_time_s=0.0,
                speed_m_s=speed,
                acceleration_m_s2=acceleration,
            )
        ]
    )


def test_whole_assembly_entry_and_constant_speed_exit_have_independent_solution():
    config = motion()
    plan = passage_plan(simple_model(), config)
    assert plan["configuration"]["traffic"][0]["initial_advance_m"] == -16.0
    assert plan["trains"][0]["required_travel_m"] == 42.0
    assert plan["duration_s"] == pytest.approx(4.2)
    assert plan["trains"][0]["front_at_arrival_m"] == -6.0
    assert config == motion()  # supplied reference scenario is never overwritten


@pytest.mark.parametrize(
    "speed,acceleration,expected",
    [(0.0, 2.0, 42.0**0.5), (10.0, -1.0, 10.0 - 16.0**0.5)],
)
def test_acceleration_and_braking_solve_exact_distance(speed, acceleration, expected):
    plan = passage_plan(simple_model(), motion(speed, acceleration))
    elapsed = plan["trains"][0]["elapsed_to_exit_s"]
    assert elapsed == pytest.approx(expected)
    assert speed * elapsed + acceleration * elapsed * elapsed / 2 == pytest.approx(42.0)
    assert expected <= plan["duration_s"] < expected + 0.002


def test_stopped_and_step_budget_cases_cannot_become_short_passages():
    stopped = passage_plan(simple_model(), motion(5.0, -1.0))
    assert stopped["state"] == "outside-domain"
    assert stopped["duration_s"] is None
    assert stopped["trains"][0]["stopping_distance_m"] == 12.5
    limited = passage_plan(simple_model(), motion(0.5), dt=0.0000625)
    assert limited["duration_s"] == 84.0
    assert limited["steps"] > 200000 and not limited["within_adapter_domain"]


def test_echoed_duration_cannot_claim_complete_native_coverage():
    from osr_mech.engineering_definition import fingerprint

    model = simple_model()
    plan = passage_plan(model, motion())
    configuration = plan["configuration"]
    result = dict(
        state="completed", duration_s=plan["duration_s"], within_adapter_domain=True
    )
    assert not complete_coverage(model, configuration, plan, result)
    result.update(
        configuration_sha256=fingerprint(configuration),
        hardware_definition_sha256=fingerprint(model),
        steps=plan["steps"],
        numerical_progress=dict(
            converged_steps=plan["steps"], last_converged_time_s=plan["duration_s"]
        ),
    )
    assert complete_coverage(model, configuration, plan, result)
    result["numerical_progress"]["last_converged_time_s"] -= 0.002
    assert not complete_coverage(model, configuration, plan, result)


def test_two_tracks_retain_relative_position_and_delayed_exit():
    config = motion()
    second = deepcopy(config["traffic"][0])
    second.update(id="b", initial_advance_m=50.0, arrival_time_s=3.0, speed_m_s=5.0)
    config["traffic"].append(second)
    plan = passage_plan(simple_model(), config)
    traffic = plan["configuration"]["traffic"]
    assert traffic[1]["initial_advance_m"] - traffic[0]["initial_advance_m"] == 5.0
    assert all(r["front_at_arrival_m"] <= -6 for r in plan["trains"])
    assert plan["duration_s"] == pytest.approx(11.4)
    config["traffic"][1].update(speed_m_s=0.0, acceleration_m_s2=2.0)
    with pytest.raises(ValueError, match="pre-arrival acceleration"):
        passage_plan(simple_model(), config)


def test_killed_writer_keeps_complete_prefix_and_truncated_suffix(tmp_path):
    from engineering.design_engine.passage import retained_history

    path = tmp_path / "converged-joints.jsonl"
    raw = b'{"time_s":0.002,"joints":[]}\n{"time_s":0.004,"joi'
    path.write_bytes(raw)
    history, warnings = retained_history(tmp_path)
    assert history == [dict(time_s=0.002, joints=[])]
    assert warnings[0]["line"] == 2
    assert path.read_bytes() == raw


def test_joint_cycles_keep_residual_half_cycles_without_fatigue_life():
    history = [
        dict(
            time_s=float(i),
            joints=[
                dict(train="a", joint="mount", force_moment_si=[value, 0, 0, 0, 0, 0])
            ],
        )
        for i, value in enumerate([0, 10, 0, 10, 0])
    ]
    result = joint_cycles(history, complete=False)
    assert sum(c["count"] for c in result["rows"][0]["cycles"]) == 2.0
    assert result["rows"][0]["unit"] == "N"
    assert result["rows"][3]["unit"] == "N m"
    assert all(row["damage"] is None for row in result["rows"])
    assert not result["full_passage_history"] and not result["physical_validation"]
    history[-1]["joints"] = []
    with pytest.raises(ValueError, match="every joint"):
        joint_cycles(history)


@pytest.fixture(scope="module")
def assembly():
    from engineering.civil_exploration.variant_compiler import compile_variant

    return compile_variant()


def test_actual_modal_and_separate_mount_coordinates_preserve_mass_and_reactions(
    assembly,
):
    for count in (2, 4):
        result = assembly_diagnostics(assembly, mode_count=count)
        assert result["mass_relative_error"] < 1e-12
        assert result["reaction_relative_error"] < 1e-12
        assert result["minimum_static_contact_n"] > 0
        assert result["modal_preload_residual_n"] < 1e-6
        assert len(result["equipment_instance_ids"]) == 6
        assert all(
            len(frequencies) == count
            for frequencies in result["modal_frequencies_hz"].values()
        )
        assert not result["physical_validation"]


def test_native_short_history_retains_every_sample_and_explicit_incomplete_scope(
    assembly, tmp_path
):
    from engineering.design_engine.passage import case

    result = case(
        assembly["model"],
        assembly["spatial_configuration"],
        dict(dt=0.005, duration_s=0.01, deck_mesh=2, rail_step=2.0),
        tmp_path / "short",
        timeout=60,
    )
    assert result["state"] == "completed"
    assert result["steps"] == 2
    with gzip.open(
        tmp_path / "short" / result["history_artifact"]["path"], "rt"
    ) as stream:
        history = json.load(stream)
    assert len(history) == 2
    assert result["numerical_progress"]["last_converged_time_s"] == 0.01
    # The subprocess only knows its requested duration. Full-passage planning
    # is a separate adapter check; this tiny native kernel test claims no trip.
    assert not result["physical_validation"]


def test_independent_refinement_changes_one_axis_and_preserves_whole_passage():
    from engineering.design_engine.vehicle_confirmation import (
        independent_refinement_plan,
    )

    model, configuration = simple_model(), motion()
    plan = independent_refinement_plan(model, configuration)
    assert plan["baseline_parameters"] == dict(
        dt=0.002, duration_s=4.2, deck_mesh=4, rail_step=1.0
    )
    assert [c["id"] for c in plan["cases"]] == ["time", "deck", "rail"]
    assert [c["expected_steps"] for c in plan["cases"]] == [4200, 2100, 2100]
    for case in plan["cases"]:
        changed = [
            k
            for k, v in case["parameters"].items()
            if v != plan["baseline_parameters"][k]
        ]
        assert changed == [case["varied_field"]]
        assert case["parameters"]["duration_s"] == 4.2
    assert configuration == motion()
    with pytest.raises(ValueError, match="bounded independent"):
        independent_refinement_plan(model, configuration, deck_mesh=24)


def test_incremental_demands_subtract_corresponding_actual_resultants():
    from engineering.design_engine.vehicle_confirmation import incremental_demands

    def sample(t, force, moment, acceleration):
        return dict(
            time_s=t,
            foundation_reactions_si=[[0, 0, force, 0, 0, 0]],
            structural_member_demands=[
                dict(kind="deck", station_start=0.0, track=0, moment_y_nm=moment)
            ],
            peak_structure_acceleration_m_s2=acceleration,
        )

    history = [sample(0.002, 100.0, 10.0, 0.0), sample(0.004, 130.0, 6.0, 2.0)]
    report = incremental_demands(history)
    assert report["peak_initial_sample_relative_foundation_force_n"] == 30.0
    assert report["peak_initial_sample_relative_deck_moment_nm"] == 4.0
    assert report["peak_structure_acceleration_m_s2"] == 2.0
    assert "displacement" not in {k for k in report if k.startswith("peak_")}
    history[-1]["structural_member_demands"][0]["track"] = 1
    with pytest.raises(ValueError, match="correspondence"):
        incremental_demands(history)


def test_refinement_comparison_requires_complete_independent_native_cases():
    from engineering.design_engine.vehicle_confirmation import (
        independent_refinement_plan,
        compare_independent_refinements,
        REFINEMENT_METRICS,
    )
    from osr_mech.engineering_definition import fingerprint

    model = simple_model()
    plan = independent_refinement_plan(model, motion())

    def completed(parameters):
        steps = round(parameters["duration_s"] / parameters["dt"])
        return dict(
            state="completed",
            within_adapter_domain=True,
            configuration_sha256=fingerprint(plan["configuration"]),
            hardware_definition_sha256=fingerprint(model),
            steps=steps,
            time_step_s=parameters["dt"],
            duration_s=parameters["duration_s"],
            numerical_progress=dict(
                converged_steps=steps, last_converged_time_s=parameters["duration_s"]
            ),
            requested_parameters=deepcopy(parameters),
            source_unchanged=True,
            **{key: 1.0 for key in REFINEMENT_METRICS}
        )

    baseline = completed(plan["baseline_parameters"])
    results = {case["id"]: completed(case["parameters"]) for case in plan["cases"]}
    assert (
        compare_independent_refinements(model, plan, baseline, results)["state"]
        == "passed"
    )
    results["time"]["state"] = "budget-exceeded"
    report = compare_independent_refinements(model, plan, baseline, results)
    assert (
        report["state"] == "unknown" and not report["cases"][0]["full_passage_coverage"]
    )
    results["time"] = completed(plan["cases"][0]["parameters"])
    results["deck"]["maximum_wheel_contact_n"] = 1.2
    assert (
        compare_independent_refinements(model, plan, baseline, results)["state"]
        == "failed"
    )
    plan["cases"][0]["parameters"]["deck_mesh"] = 8
    with pytest.raises(ValueError, match="plan/limits"):
        compare_independent_refinements(model, plan, baseline, results)
