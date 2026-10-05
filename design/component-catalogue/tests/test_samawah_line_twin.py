"""Regression checks for the complete Samawah Line 1 digital twin."""

from __future__ import annotations

from dataclasses import replace
import tomllib

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
    design = tomllib.loads((twin.city_dir / 'design.toml').read_text())
    alignment = tomllib.loads((twin.city_dir / 'engineering/alignment/samawah-line1.aln.toml').read_text())
    line = next(line for line in design['lines'] if line['name'] == twin.line_id)
    fleet = next(f for f in design['fleets'] if f['line'] == twin.line_id)
    assert twin.length_m == line['length_m']
    assert len(twin.alignment) == len(alignment['horizontal'])
    assert len(twin.civil_segments) == len(alignment['civil'])
    assert len(twin.stations) == len(alignment['station'])
    assert twin.fleet.trainset_count == fleet['trainset_count']
    assert twin.fleet.peak_headway_min == 3


def test_samawah_line_twin_source_checks_all_pass() -> None:
    checks = twin_checks(load_samawah_line_twin())
    assert len(checks) == 6
    assert all(item["passed"] for item in checks)


def test_missing_assets_and_reduced_fleet_cannot_pass_current_source_checks() -> None:
    twin = load_samawah_line_twin()
    for changed, name in (
        (replace(twin, stations=twin.stations[:-1]), 'all-line-stations-present'),
        (replace(twin, energy_sites=twin.energy_sites[:-1]), 'energy-and-depot-assets-present'),
        (replace(twin, fleet=replace(twin.fleet, trainset_count=twin.fleet.trainset_count-1)), 'complete-line-fleet-register'),
    ):
        assert not next(c['passed'] for c in twin_checks(changed) if c['name'] == name)


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
    classes = [asset["asset_class"] for asset in manifest["assets"]]
    assert len(manifest['relationships']) == len(manifest['assets'])-1
    assert len({a['asset_id'] for a in manifest['assets']}) == len(manifest['assets'])
    assert classes.count("rolling-stock.light-metro-3car") == twin.fleet.trainset_count
    assert classes.count("signalling.movement-authority-block") == 2*(len(twin.stations)-1)
    blocks = [a['engineering'] for a in manifest['assets'] if a['asset_class'] == 'signalling.movement-authority-block']
    assert {(b['from_station'], b['to_station'], b['direction']) for b in blocks} == {
        (left.asset_id, right.asset_id, direction)
        for left, right in zip(twin.stations, twin.stations[1:])
        for direction in ('outbound', 'inbound')
    }
    assert classes.count("energy.station-microgrid") == len(twin.energy_sites)
    assert "track.double-running-line" in classes
    assert "depot.main-heavy" in classes
    depot = next(a for a in manifest['assets'] if a['asset_class'] == 'depot.main-heavy')['engineering']
    assert depot['storage_slots'] == twin.fleet.trainset_count
    assert depot['workshop_bays'] < depot['storage_slots']
    assert not depot['physical_release'] and not depot['site_accepted']


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
