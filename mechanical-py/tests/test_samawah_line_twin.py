"""Regression checks for the complete Samawah Line 1 digital twin."""

from __future__ import annotations

from osr_mech.samawah_line_twin import (
    ANIMATED_TRAIN_COUNT,
    LM3_BODY_HEIGHT_M,
    LM3_DOOR_HEIGHT_M,
    LM3_DOOR_SILL_M,
    LM3_WINDOW_HEIGHT_M,
    LM3_WINDOW_SILL_M,
    S5_PLATFORM_HEIGHT_ABOVE_TOR_M,
    digital_twin_manifest,
    load_samawah_line_twin,
    point_at_chainage,
    representative_train_states,
    station_stop_motion,
    twin_checks,
)


def test_lm3_s5_render_datums_preserve_level_boarding_interface() -> None:
    assert LM3_BODY_HEIGHT_M == 3.450
    assert LM3_DOOR_SILL_M == S5_PLATFORM_HEIGHT_ABOVE_TOR_M == 0.350
    assert LM3_DOOR_HEIGHT_M == 2.000
    assert (LM3_WINDOW_SILL_M, LM3_WINDOW_HEIGHT_M) == (1.500, 0.900)


def test_samawah_line_twin_loads_the_complete_source_alignment() -> None:
    twin = load_samawah_line_twin()
    assert twin.line_id == "line-1"
    assert twin.length_m == 25_565.7
    assert len(twin.alignment) == 135
    assert len(twin.civil_segments) == 5
    assert len(twin.stations) == 9
    assert len(twin.energy_sites) == 8
    assert twin.fleet.trainset_count == 53
    assert twin.fleet.peak_headway_min == 3


def test_samawah_line_twin_source_checks_all_pass() -> None:
    checks = twin_checks(load_samawah_line_twin())
    assert len(checks) == 6
    assert all(item["passed"] for item in checks)


def test_chainage_interpolation_preserves_both_alignment_endpoints() -> None:
    twin = load_samawah_line_twin()
    start = point_at_chainage(twin, 0.0)
    end = point_at_chainage(twin, twin.length_m)
    assert start[:2] == (twin.alignment[0].easting_m, twin.alignment[0].northing_m)
    assert end[:2] == (twin.alignment[-1].easting_m, twin.alignment[-1].northing_m)


def test_representative_trains_cover_both_directions_and_valid_chainages() -> None:
    twin = load_samawah_line_twin()
    states = representative_train_states(twin, 0.2)
    assert len(states) == ANIMATED_TRAIN_COUNT
    assert {state.direction for state in states} == {"outbound", "inbound"}
    assert all(0.0 <= state.chainage_m <= twin.length_m for state in states)
    assert all(0.0 <= state.speed_kmh <= twin.fleet.max_speed_kmh for state in states)
    assert all(20.0 <= state.soc_percent <= 100.0 for state in states)


def test_manifest_registers_full_infrastructure_energy_signalling_and_fleet() -> None:
    twin = load_samawah_line_twin()
    manifest = digital_twin_manifest(twin)
    assert manifest["schema"] == "org.opensourcerail.city-line-operational-twin.v1"
    assert len(manifest["assets"]) == 94
    assert len(manifest["relationships"]) == 93
    classes = [asset["asset_class"] for asset in manifest["assets"]]
    assert classes.count("rolling-stock.light-metro-3car") == 53
    assert classes.count("signalling.movement-authority-block") == 16
    assert classes.count("energy.station-microgrid") == 8
    assert "track.double-running-line" in classes
    assert "depot.main-heavy" in classes


def test_station_stop_demonstrator_uses_real_time_kinematics() -> None:
    approach = station_stop_motion(0.0)
    braking = station_stop_motion(15.0)
    arrival = station_stop_motion(20.0)
    dwell = station_stop_motion(22.0)
    departure = station_stop_motion(30.0)
    cruise = station_stop_motion(45.0)

    assert (approach.offset_m, approach.speed_kmh) == (-150.0, 36.0)
    assert braking.acceleration_mps2 == -1.0
    assert braking.speed_kmh == 18.0
    assert arrival.offset_m == 0.0
    assert dwell.doors_open and dwell.speed_kmh == 0.0
    assert departure.acceleration_mps2 == 1.0
    assert departure.speed_kmh == 18.0
    assert (cruise.offset_m, cruise.speed_kmh) == (175.0, 0.0)
