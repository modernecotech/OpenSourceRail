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
    from engineering.design_engine.passage import verify_case

    assert result["source_unchanged"] and result["toolchain_unchanged"]
    assert (
        verify_case(
            tmp_path / "short",
            result,
            model=assembly["model"],
            configuration=assembly["spatial_configuration"],
            parameters=dict(dt=0.005, duration_s=0.01, deck_mesh=2, rail_step=2.0),
        )["state"]
        == "completed"
    )


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


def retained_fixture_case(folder, model, configuration, parameters, **overrides):
    """Labelled protocol fixture; no native physics is executed or claimed."""
    from engineering.design_engine.contracts import canonical
    from engineering.design_engine.passage import seal_case
    from engineering.design_engine.publication import digest
    from engineering.design_engine.vehicle_confirmation import REFINEMENT_METRICS
    from osr_mech.engineering_definition import fingerprint

    folder.mkdir(parents=True, exist_ok=True)
    (folder / "input.json").write_bytes(
        canonical(dict(model=model, configuration=configuration, parameters=parameters))
        + b"\n"
    )
    (folder / "solver.log").write_text(
        "Labelled comparison fixture; not a solver execution\n"
    )
    history = folder / "native-history.json.gz"
    with gzip.open(history, "wt") as stream:
        json.dump([dict(fixture=True)], stream)
    steps = round(parameters["duration_s"] / parameters["dt"])
    result = dict(
        state="completed",
        within_adapter_domain=True,
        configuration_sha256=fingerprint(configuration),
        hardware_definition_sha256=fingerprint(model),
        steps=steps,
        time_step_s=parameters["dt"],
        duration_s=parameters["duration_s"],
        numerical_progress=dict(
            converged_steps=steps, last_converged_time_s=parameters["duration_s"]
        ),
        requested_parameters=deepcopy(parameters),
        source_unchanged=True,
        source_sha256={"labelled-fixture-not-native.py": "f" * 64},
        solver_toolchain=dict(
            python="fixture",
            numpy="fixture",
            scipy="fixture",
            executable_sha256="e" * 64,
        ),
        toolchain_unchanged=True,
        input_sha256=digest(folder / "input.json"),
        history_artifact=dict(path=history.name, sha256=digest(history), samples=1),
        physical_validation=False,
        **{key: 1.0 for key in REFINEMENT_METRICS},
    )
    result.update(overrides)
    (folder / "result.json").write_bytes(canonical(result) + b"\n")
    (folder / "case-manifest.json").unlink(missing_ok=True)
    return seal_case(folder)


@pytest.fixture
def retained_refinement(tmp_path):
    from engineering.design_engine.vehicle_confirmation import (
        independent_refinement_plan,
    )

    model = simple_model()
    config = motion()
    config["flexible_vehicle"] = dict(mode_count=2, ei_nm2=3e8, damping_ratio=0.02)
    plan = independent_refinement_plan(model, config)
    baseline = retained_fixture_case(
        tmp_path / "baseline", model, plan["configuration"], plan["baseline_parameters"]
    )
    results = {
        case["id"]: retained_fixture_case(
            tmp_path / case["id"],
            model,
            case.get("configuration", plan["configuration"]),
            case["parameters"],
        )
        for case in plan["cases"]
    }
    return model, plan, baseline, results, tmp_path


def compare_fixture(fixture):
    from engineering.design_engine.vehicle_confirmation import (
        compare_independent_refinements,
    )

    model, plan, baseline, results, root = fixture
    return compare_independent_refinements(
        model, plan, baseline, results, artifact_root=root
    )


def test_refinement_comparison_requires_complete_independent_retained_cases(
    retained_refinement,
):
    fixture = retained_refinement
    model, plan, baseline, results, root = fixture
    assert [row["id"] for row in plan["cases"]] == ["time", "deck", "rail", "modal"]
    modal = plan["cases"][-1]
    assert modal["parameters"] == plan["baseline_parameters"]
    expected = deepcopy(plan["configuration"])
    expected["flexible_vehicle"]["mode_count"] = 4
    assert modal["configuration"] == expected
    assert compare_fixture(fixture)["state"] == "passed"
    assert all(row["provenance_verified"] for row in compare_fixture(fixture)["cases"])
    # A retained timeout cannot pass even when all reported scalars match.
    results["time"] = retained_fixture_case(
        root / "time",
        model,
        plan["configuration"],
        plan["cases"][0]["parameters"],
        state="budget-exceeded",
    )
    report = compare_fixture(fixture)
    assert (
        report["state"] == "unknown" and not report["cases"][0]["full_passage_coverage"]
    )
    results["time"] = retained_fixture_case(
        root / "time", model, plan["configuration"], plan["cases"][0]["parameters"]
    )
    results["deck"] = retained_fixture_case(
        root / "deck",
        model,
        plan["configuration"],
        plan["cases"][1]["parameters"],
        maximum_wheel_contact_n=1.2,
    )
    assert compare_fixture(fixture)["state"] == "failed"
    plan["cases"][0]["parameters"]["deck_mesh"] = 8
    with pytest.raises(ValueError, match="plan/limits"):
        compare_fixture(fixture)


@pytest.mark.parametrize("name", ["baseline", "time", "modal"])
@pytest.mark.parametrize(
    "mutation",
    [
        "changed-source",
        "changed-toolchain",
        "different-source",
        "different-toolchain",
        "no-source",
        "no-toolchain",
    ],
)
def test_every_case_requires_unchanged_identical_provenance(
    retained_refinement, name, mutation
):
    fixture = retained_refinement
    model, plan, baseline, results, root = fixture
    case = next((row for row in plan["cases"] if row["id"] == name), None)
    parameters = case["parameters"] if case else plan["baseline_parameters"]
    configuration = (
        case.get("configuration", plan["configuration"])
        if case
        else plan["configuration"]
    )
    overrides = {
        "changed-source": dict(source_unchanged=False),
        "changed-toolchain": dict(toolchain_unchanged=False),
        "different-source": dict(
            source_sha256={"labelled-fixture-not-native.py": "a" * 64}
        ),
        "different-toolchain": dict(
            solver_toolchain=dict(baseline["solver_toolchain"], scipy="another-fixture")
        ),
        "no-source": dict(source_sha256={}),
        "no-toolchain": dict(solver_toolchain={}),
    }[mutation]
    altered = retained_fixture_case(
        root / name, model, configuration, parameters, **overrides
    )
    if name == "baseline":
        baseline.clear()
        baseline.update(altered)
    else:
        results[name] = altered
    report = compare_fixture(fixture)
    assert report["state"] == "unknown"
    assert any(row["provenance_issues"] for row in report["cases"])
    if name == "baseline":
        assert not any(row["state"] == "passed" for row in report["cases"])


@pytest.mark.parametrize(
    "artifact",
    [
        "input.json",
        "result.json",
        "case-manifest.json",
        "native-history.json.gz",
        "solver.log",
    ],
)
@pytest.mark.parametrize("case_name", ["baseline", "rail"])
def test_comparison_rejects_changed_retained_artifacts(
    retained_refinement, artifact, case_name
):
    root = retained_refinement[-1]
    path = root / case_name / artifact
    path.write_bytes(path.read_bytes() + b"changed")
    report = compare_fixture(retained_refinement)
    assert report["state"] == "unknown"
    assert any(row["provenance_issues"] for row in report["cases"])


def test_in_memory_metrics_and_unretained_results_cannot_qualify(retained_refinement):
    from engineering.design_engine.vehicle_confirmation import (
        compare_independent_refinements,
    )

    model, plan, baseline, results, root = retained_refinement
    results["deck"]["maximum_wheel_contact_n"] = 1.001
    report = compare_fixture(retained_refinement)
    assert report["state"] == "unknown"
    assert "differs from retained" in " ".join(report["cases"][1]["provenance_issues"])
    assert (
        compare_independent_refinements(model, plan, baseline, results)["state"]
        == "unknown"
    )


def test_missing_and_extra_artifacts_invalidate_the_case_closure(retained_refinement):
    root = retained_refinement[-1]
    (root / "baseline/extra.txt").write_text("unsealed")
    assert compare_fixture(retained_refinement)["state"] == "unknown"
    (root / "baseline/extra.txt").unlink()
    (root / "rail/solver.log").unlink()
    assert compare_fixture(retained_refinement)["state"] == "unknown"
