"""Independent dimensional/equilibrium controls for queued civil investigations."""

import math

import pytest
from engineering.generative_design import civil_systems as c
from engineering.factory_examples.models import volume


@pytest.fixture(scope="module")
def report():
    return c.run()


def test_rational_rainfall_units_and_rectangular_hydraulic_radius():
    assert c.rational_runoff(10000, 36, 1) == pytest.approx(0.1)
    assert c.rational_runoff(10000, 36, 0.9) == pytest.approx(0.09)
    # 2m wide,1m deep: A=2m², wetted perimeter4m, R=.5m.
    assert c.channel_flow(2, 1, 0.01, 0.02) == pytest.approx(
        2 * 0.5 ** (2 / 3) * 0.1 / 0.02
    )
    with pytest.raises(ValueError):
        c.rational_runoff(1, 10, 1.1)
    with pytest.raises(ValueError):
        c.channel_flow(1, 0, 0.01, 0.02)


def test_local_strip_bending_and_displacement_match_closed_forms():
    r = c.beam_strip(1000, 2, 1, 0.2, 30e9)
    assert r["moment_nm"] == pytest.approx(500)
    assert r["nominal_bending_demand_pa"] == pytest.approx(75000)
    assert r["elastic_deflection_m"] == pytest.approx(
        1000 * 8 / (48 * 30e9 * (0.2**3 / 12))
    )
    assert c.beam_strip(1000, 2, 1, 0.4, 30e9)["elastic_deflection_m"] == pytest.approx(
        r["elastic_deflection_m"] / 8
    )


def test_pad_contact_equilibrium_and_uplift_domain_are_not_conflated():
    r = c.contact_pressure(120000, 20000, 2, 3)
    assert r["full_contact"]
    assert (
        r["minimum_pressure_pa"] + r["maximum_pressure_pa"]
    ) / 2 * 6 == pytest.approx(120000)
    # Integrate the linear pressure moment analytically.
    assert (
        r["maximum_pressure_pa"] - r["minimum_pressure_pa"]
    ) / 2 * 3 * 2**2 / 6 == pytest.approx(20000)
    failed = c.contact_pressure(120000, 100000, 2, 3)
    assert not failed["full_contact"]
    assert (
        failed["minimum_pressure_pa"] is None and failed["maximum_pressure_pa"] is None
    )
    assert failed["partial_contact_analysis_required"]


def find(report, work, id):
    package = next(p for p in report["packages"] if p["work_package_id"] == work)
    return next(i for i in package["investigations"] if i["id"] == id)


def test_all_station_civil_and_factory_queue_ids_have_specific_work_and_open_gates(
    report,
):
    expected = {f"STN-FRP-{n:03}" for n in range(10, 100, 10)} | {
        "CIV-FRP-100",
        "CIV-FRP-110",
        "CIV-FRP-120",
        "CIV-FRP-130",
        "CIV-INT-200",
        "CIV-INT-210",
        "FACTORY-PRECAST",
        "FACTORY-SITE",
        "FACTORY-BUILDINGS",
    }
    assert {p["work_package_id"] for p in report["packages"]} == expected
    assert report["work_package_count"] == 18
    for p in report["packages"]:
        assert p["investigations"] and p["unresolved_gates"]
        assert all(g["status"] == "unknown" for g in p["unresolved_gates"])
        assert not p["engineering_design_complete"] and not p["physical_release"]
        for i in p["investigations"]:
            assert i["source_paths"]
    assert not report["engineering_design_complete"] and not report["physical_release"]


def test_failed_clearance_tolerance_and_mould_variations_have_numerical_repairs(report):
    cases = [
        ("STN-FRP-020", "canopy-root-and-bay-repair"),
        ("CIV-FRP-120", "replacement-headroom-repair"),
        ("CIV-INT-200", "static-platform-tolerance-repair"),
        ("FACTORY-PRECAST", "jack-grip-access-repair"),
        ("FACTORY-PRECAST", "mould-steel-skin-repair"),
        ("FACTORY-PRECAST", "strongback-hole-strip-repair"),
    ]
    for work, id in cases:
        r = find(report, work, id)
        assert any(not x["conditional_local_pass"] for x in r["candidates"]), id
        assert any(x["conditional_local_pass"] for x in r["candidates"]), id
    endzone = find(report, "FACTORY-PRECAST", "endzone-average-bond-demand")
    assert all(
        x["checks"]["bond_and_transmission"]["status"] == "unknown"
        for x in endzone["candidates"]
    )
    assert not endzone["selected_candidate_ids"]


def test_source_web_line_pier_reactions_moments_and_cap_volume(report):
    row = find(report, "CIV-FRP-110", "four-beam-end-shared-pier")["candidates"][0]
    m = row["metrics"]
    R = m["one_beam_end_diagnostic_n"]
    assert m["total_support_diagnostic_n"] == pytest.approx(4 * R)
    assert m["one_side_cap_column_centreline_moment_nm"] == pytest.approx(
        R * (2.4675 + 1.0325)
    )
    assert m["one_side_cap_column_face_moment_nm"] == pytest.approx(
        R * ((2.4675 - 1) + (1.0325 - 1))
    )
    assert not m["support_reaction_basis"]["accepted"]
    model = c._pier_model()
    shell_volume = sum(volume(p) for p in model["parts"] if p["id"].startswith("cap-"))
    assert shell_volume == pytest.approx(2.5 * 7 * 1.2 - 2 * 6.5 * 0.8)
    assert sum(p["id"].startswith("bearing-") for p in model["parts"]) == 8
    bearings = [p for p in model["parts"] if p["id"].startswith("bearing-")]
    pads = [p for p in model["parts"] if p["id"].startswith("jack-pad-")]
    assert min(p["at_m"][2] + p["size_m"][2] for p in bearings) - max(
        p["at_m"][2] + p["size_m"][2] for p in pads
    ) == pytest.approx(0.3)


def test_artifacts_are_two_real_native_definitions_and_unreleased(report, tmp_path):
    artifacts = c.write_artifacts(report, tmp_path)
    assert len(artifacts) == 2
    model = c._mould_model(report)
    count = report["beam_candidate"]["variables"]["strand_count"]
    face = next(p for p in model["parts"] if p["id"] == f"{count}-hole-front-plate")
    assert count == 112 and len(face["holes"]) == count
    assert volume(face) == pytest.approx(
        0.08 * 4 * 1.5 - count * math.pi * 0.022**2 / 4 * 0.08
    )
    assert all(not a["physical_release"] for a in artifacts)
    assert (tmp_path / "report.json").is_file()


def test_provisional_six_car_reaction_propagates_to_pier_bearings_and_jacks(report):
    legacy = report["support_reaction_basis"]["maximum_live_reaction_n"]
    increment = 250000.0
    updated = c.run(provisional_six_car_support_reaction_n=legacy + increment)
    basis = updated["support_reaction_basis"]
    assert basis["mode"] == "provisional-six-car-sensitivity"
    assert basis["caller_supplied"] and not basis["accepted"]
    assert basis["legacy_three_car_maximum_live_reaction_n"] == legacy
    old = find(report, "CIV-FRP-110", "four-beam-end-shared-pier")["candidates"][0][
        "metrics"
    ]
    new = find(updated, "CIV-FRP-110", "four-beam-end-shared-pier")["candidates"][0][
        "metrics"
    ]
    assert new["total_support_diagnostic_n"] - old[
        "total_support_diagnostic_n"
    ] == pytest.approx(4 * increment)
    assert new["one_side_cap_column_face_moment_nm"] - old[
        "one_side_cap_column_face_moment_nm"
    ] == pytest.approx(1.5 * increment)
    oldb = find(report, "CIV-FRP-120", "movement-and-jack-demand")["candidates"][0][
        "metrics"
    ]
    newb = find(updated, "CIV-FRP-120", "movement-and-jack-demand")["candidates"][0][
        "metrics"
    ]
    assert newb["nominal_end_pressure_pa"] - oldb[
        "nominal_end_pressure_pa"
    ] == pytest.approx(increment / (2 * 0.6 * 0.5))
    assert newb["research_jack_load_each_n"] - oldb[
        "research_jack_load_each_n"
    ] == pytest.approx(0.55 * increment)
    j = find(updated, "CIV-FRP-120", "replacement-headroom-repair")["candidates"][-1][
        "metrics"
    ]
    assert j["temporary_web_reaction_n"] == pytest.approx(
        newb["research_jack_load_each_n"]
    )


def test_invalid_provisional_support_reactions_are_rejected():
    for force in (-1, True, float("nan"), float("inf"), "100"):
        with pytest.raises(ValueError, match="support reaction"):
            c.run(provisional_six_car_support_reaction_n=force)
