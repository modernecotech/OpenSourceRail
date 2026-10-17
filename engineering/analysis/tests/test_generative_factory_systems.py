"""Independent conservation, missing-data and exact-interface checks."""

from copy import deepcopy
import json
import math
from pathlib import Path
import xml.etree.ElementTree as ET

import pytest

from engineering.generative_design import factory_systems as f
from engineering.generative_design.evidence_store import read_json
from engineering.design_engine.factory_schedule import validate


@pytest.fixture(scope="module")
def report():
    civil = read_json(
        f.ROOT / "docs/design-engine/generative-campaign/civil/search.json"
    )
    return f.run(civil_report=civil)


def investigation(report, package, number=0):
    return next(p for p in report["packages"] if p["work_package_id"] == package)[
        "investigations"
    ][number]


def test_power_preserves_apparent_input_vs_motor_output_and_unknowns(report):
    power = investigation(report, "FACTORY-MEP")
    assert {r["id"] for r in power["published_inputs"]} == {
        "esprit-photon-3015",
        "ciject-1",
    }
    assert sum(r["kva"] for r in power["published_inputs"]) == pytest.approx(59.13)
    # No inference from the saw's3kW drive or CNC's18.5kW spindle.
    assert len(power["unresolved_utility_equipment_ids"]) == 14
    rows = power["candidates"]
    assert [r["planning_peak_kva"] for r in rows] == sorted(
        r["planning_peak_kva"] for r in rows
    )
    for r in rows:
        assert r["actual_peak_kva"] is None
        assert r["accepted_transformer_kva"] is None
        assert r["candidate_transformer_kva"] * 0.8 >= r["planning_peak_kva"]
        # S=sqrt(3)VI; main bus carries full transformer rating, not merely diversified peak.
        assert math.sqrt(3) * 415 * r[
            "transformer_full_load_current_a"
        ] / 1000 == pytest.approx(r["candidate_transformer_kva"])
        assert (
            r["candidate_bus_continuous_rating_a"]
            >= r["transformer_full_load_current_a"]
        )
        for short in r["transformer_only_terminal_fault_hypotheses_a"]:
            assert short["current_a"] * short["impedance_pu"] == pytest.approx(
                r["transformer_full_load_current_a"]
            )
        assert r["accepted_fault_duty_a"] is None


def test_single_bambi_cannot_supply_continuous_cmm_and_receiver_creates_no_air(report):
    air = investigation(report, "FACTORY-MEP", 1)
    assert sum(c["l_min"] for c in air["consumers"]) == 700
    single = [r for r in air["cmm_segregated_candidates"] if r["duty_units"] == 1]
    assert single and all(r["status"] == "failed-flow-hypothesis" for r in single)
    assert all(r["continuous_time_average_capacity_l_min"] == 63 for r in single)
    assert all(r["required_l_min"] > 100 for r in single)
    for r in air["candidates"]:
        assert r["published_fad_l_min_at10bar"] == 1450
        assert r["unknown_consumers_l_min"] is None
        assert r["accepted_delivered_flow_l_min"] is None
        for tank in r["receiver_isothermal_l"]:
            # One bar allowable drop at one bar free-air reference: tank litres
            # times pressure ratio equals supplied free-air litres over duration.
            assert tank["volume_l"] == pytest.approx(
                r["planning_free_air_required_l_min"] * tank["autonomy_s"] / 60
            )


def test_water_and_cooling_balance_do_not_qualify_mix_or_chiller(report):
    water = investigation(report, "FACTORY-MEP", 2)
    for r in water["candidates"]:
        assert r["minimum_process_makeup_m3_day"] == pytest.approx(
            r["mix_water_m3_day"] + r["washout_m3_day"]
        )
        assert r["accepted_mix_water_l_m3"] is None
    cooling = investigation(report, "FACTORY-MEP", 3)
    for r in cooling["candidates"]:
        # 1litre/s water =1kg/s; Q=m_dot*c_p*DeltaT.
        q = r["minimum_sensible_water_l_s"] * 4180 * r["water_delta_k"] / 1000
        assert q == pytest.approx(r["combined_sensible_kw"])
        assert r["combined_sensible_kw"] > r["process_heat_hypothesis_kw"]
        assert r["selected_chiller_capacity_kw"] is None
        assert r["latent_solar_product_cure_load_kw"] is None


def test_extraction_air_continuity_has_no_shared_hazard_stream_acceptance(report):
    lev = investigation(report, "FACTORY-MEP", 4)
    for r in lev["candidates"]:
        branch_area = math.pi * r["separate_branch_duct_diameter_m"] ** 2 / 4
        assert branch_area * r["assumed_branch_duct_velocity_m_s"] == pytest.approx(
            r["airflow_each_m3_s"]
        )
        assert not r["shared_dust_fume_header_permitted"]
        assert r["accepted_capture_velocity_m_s"] is None


def test_fire_reservations_retain_unaccepted_hazard_strategy(report):
    fire = investigation(report, "FACTORY-MEP", 5)
    assert len(fire["candidates"]) == 9
    for r in fire["candidates"]:
        assert (
            r["theoretical_water_reservation_m3"] * 1000 / r["flow_hypothesis_l_min"]
            == r["duration_hypothesis_min"]
        )
        assert not r["fire_compliance_established"]
        assert r["accepted_fire_water_reserve_m3"] is None


def test_current_civil_transfer_and_rigging_equilibrium(report):
    lift = investigation(report, "FACTORY-HANDLING")
    assert all(b["source_candidate_id"] for b in report["beam_cases"])
    beams = {b["id"]: b for b in report["beam_cases"]}
    for r in lift["candidates"]:
        assert r["hook_equivalent_kg"] == pytest.approx(
            beams[r["beam"]]["transferred_hook_equivalent_kg"]
        )
        total = r["known_beam_mass_kg"] * 9.80665 * 1.25
        theta = math.radians(r["lower_sling_degrees_from_vertical"])
        assert 4 * r["nominal_four_equalized_leg_tension_n"] * math.cos(
            theta
        ) == pytest.approx(total)
        assert r["two_effective_leg_tension_n"] == pytest.approx(
            2 * r["nominal_four_equalized_leg_tension_n"]
        )
        angle = math.radians(r["upper_sling_degrees_from_vertical"])
        assert 2 * r["upper_rig_geometric_headroom_m"] * math.tan(
            angle
        ) == pytest.approx(r["longitudinal_spreader_span_m"])
        assert r["accepted_lifting_insert_capacity_n"] is None
        assert r["accepted_crane_capacity_kg"] is None
    # More vertical upper legs need more headroom; the smaller height is not free capacity.
    first = [
        r
        for r in lift["candidates"]
        if r["beam"] == report["beam_cases"][0]["id"]
        and r["lower_sling_degrees_from_vertical"] == 0
    ]
    first.sort(key=lambda r: r["upper_sling_degrees_from_vertical"])
    assert (
        first[0]["upper_rig_geometric_headroom_m"]
        > first[1]["upper_rig_geometric_headroom_m"]
    )
    assert (
        first[0]["longitudinal_spreader_compression_n"]
        < first[1]["longitudinal_spreader_compression_n"]
    )


def test_bad_current_civil_hook_cannot_silently_transfer():
    civil = read_json(
        f.ROOT / "docs/design-engine/generative-campaign/civil/search.json"
    )
    selected = set(civil["selected_candidate_ids"])
    row = next(r for r in civil["candidates"] if r["id"] in selected)
    row["scenarios"][0]["hook_equivalent_kg"] += 1000
    beams = f.beam_cases(civil)
    with pytest.raises(ValueError, match="transfer disagrees"):
        f.handling(f.read(f.DATA), beams)


def test_finite_resource_calendars_are_verified_and_original_holds_open(report):
    process = investigation(report, "FACTORY-FLOW")
    assert len(process["finite_cases"]) == 8
    for c in process["finite_cases"]:
        assert validate(c["source_schedule"])
        assert not c["accepted_cycle_output"]
        assert c["source_schedule"]["beam_count"] == 16
    assert len(process["process_routes"]) == 14
    assert process["all_original_hold_points_open"]
    target54 = next(
        r
        for r in process["resource_bounds"]
        if r["target_accepted_beams_day_hypothesis"] == 54
    )
    assert target54["bed_positions_occupation_lower_bound"] == 134
    assert target54["crane_count_aggregate_work_lower_bound"] > 2
    assert (
        target54["storage_positions_at24h_dwell_lower_bound"]
        > target54["planned_layout_storage_positions"]
    )
    assert target54["accepted_throughput_beams_day"] is None


def test_supplier_routes_and_assurance_are_unequivocally_open(report):
    suppliers = investigation(report, "FACTORY-EQUIPMENT")["equipment_cases"]
    assert len(suppliers) == 4
    assert all(
        not s["supplier_contacted"]
        and all(u.startswith("https://") for u in s["sources"])
        for s in suppliers
    )
    airbench = next(s for s in suppliers if s["id"] == "airbench-fn126784")
    assert airbench["published"]["standard_surface_load_kg"] == 50
    assert "assembly" in airbench["origin_state"]
    for package in report["packages"]:
        assert package["unresolved_gates"]
        assert not package["engineering_design_complete"]
        assert not package["manufacturing_release"]
        assert not package["physical_release"]
    assert len(report["packages"]) == 7
    assert investigation(report, "SYSTEM-ASSURANCE")["tests_performed"] == 0


def test_written_schedules_diagram_and_package_artifact_links(report, tmp_path):
    copied = deepcopy(report)
    paths = f.write_artifacts(copied, tmp_path)
    assert len(paths) == 6 and all(p.is_file() for p in paths)
    assert len(ET.parse(tmp_path / "utility-process-interfaces.svg").getroot()) > 0
    retained = json.loads((tmp_path / "factory-systems.json").read_text())
    assert all(
        (tmp_path / name).is_file()
        for p in retained["packages"]
        for name in p["generated_artifacts"]
    )
    assert not retained["physical_release"]
    assert (tmp_path / "finite-process-tasks.csv").read_text().count("\n") > 100


def test_standalone_boundary_and_invalid_electric_domain():
    beams = f.beam_cases()
    assert len(beams) == 2
    assert all(b["source_candidate_id"] is None for b in beams)
    cfg = f.read(f.DATA)
    cfg["electric"]["assumed_power_factor"] = 1.1
    with pytest.raises(ValueError, match="exceed"):
        f.electrical(
            cfg,
            f.read(f.UTILITIES),
            {r["id"]: r for r in f.read(f.EQUIPMENT)["equipment"]},
        )
