"""The Baghdad public estimate must follow its route, car, civil and power inputs."""
from pathlib import Path
import shutil

import pytest

from engineering.outline.baghdad_system import CONFIG, ROOT, compare, evaluate, load


def test_zero_tunnel_overhead_comparator_reconciles_civil_rebaseline():
    first = evaluate("first", "overhead")
    metro = evaluate("metropolitan", "overhead")
    assert first["service"]["route_km"] == 148.2
    assert first["service"]["stations"] == 64
    assert first["civil"]["quantities"]["beam_count"] == 29640
    assert first["civil"]["quantities"]["pier_foundation_count"] == 29654
    assert first["capital_usd_m"]["installed"] == pytest.approx(7926.88104)
    assert metro["capital_usd_m"]["installed"] == pytest.approx(31262.0602944)
    assert first["supply_quantities"]["overhead_track_km"] == pytest.approx(296.4)
    assert first["site_or_physical_accepted"] is False


def test_supply_changes_mass_civil_power_and_whole_life_on_same_service():
    rows = compare("first")["power_cases"]
    assert {row["service"]["offered_places_per_hour_direction"] for row in rows.values()} == {16800}
    assert {row["service"]["fleet_trainsets"] for row in rows.values()} == {242}
    assert len({row["physical_candidate_id"] for row in rows.values()}) == 4
    assert all(row["traction"]["adhesion_feasible"] for row in rows.values())
    assert rows["station_battery"]["vehicle"]["mass_t"] > rows["overhead"]["vehicle"]["mass_t"]
    assert rows["station_battery"]["civil"]["planning_prices"]["changed_elevated_scope_usd"] > rows["overhead"]["civil"]["planning_prices"]["changed_elevated_scope_usd"]
    assert rows["station_battery"]["supply_quantities"]["station_charge_ports"] == 128
    assert rows["station_battery"]["supply_quantities"]["station_charge_port_mw"] > 5.9
    assert rows["protected_conductor"]["supply_quantities"]["overhead_track_km"] == 0
    assert rows["protected_conductor"]["vehicle"]["traction_battery_kwh_per_train"] == 0
    assert rows["protected_conductor"]["whole_life_30y_present_usd_m"] < rows["overhead"]["whole_life_30y_present_usd_m"]
    for row in rows.values():
        assert sum(row["capital_usd_m"]["scope_rows"].values()) == pytest.approx(row["capital_usd_m"]["installed"])


def test_metropolitan_civil_scope_keeps_declared_length_and_no_underground():
    cfg = load()
    assert cfg["tunnel_km"] == cfg["underground_stations"] == 0
    assert cfg["revenue_guideway"] == "all elevated"
    rows = compare("metropolitan")
    assert rows["digital_cost_leader"] == "protected_conductor"
    assert rows["power_cases"]["protected_conductor"]["civil"]["quantities"]["beam_count"] > 120000
    assert len(rows["civil_cases"]) == 8
    assert all(not row["civil"]["physical_screen"]["pier_crosshead_and_foundation_verified"]
               for row in rows["civil_cases"].values())


def test_control_equipment_is_counted_and_fits_existing_scope_prices():
    first = evaluate("first", "protected_conductor")
    metro = evaluate("metropolitan", "protected_conductor")
    for row, fleet, stations, sites, centres in (
            (first, 242, 64, 30, 2), (metro, 934, 280, 100, 4)):
        controls = row["control_electronics"]
        q = controls["quantities"]
        assert q["atp_channels"] == 2 * fleet
        assert q["tcms_nodes"] == 6 * fleet
        assert q["door_controllers"] == 48 * fleet
        assert q["brake_controllers"] == 12 * fleet
        assert q["station_dispatch_controllers"] == stations
        assert q["grid_protection_gateways"] == sites
        assert q["occ_equipment_sets"] == centres
        assert q["section_control_gateways"] == row["supply_quantities"]["powered_section_count"]
        assert all(0 < amount < row["capital_usd_m"]["scope_rows"][scope]
                   for scope, amount in controls["allocation_within_capital_scopes_usd_m"].items())
        assert sum(row["capital_usd_m"]["scope_rows"].values()) == pytest.approx(
            row["capital_usd_m"]["installed"])


def test_changed_map_cannot_keep_the_same_candidate_input(tmp_path: Path):
    (tmp_path / CONFIG).parent.mkdir(parents=True)
    shutil.copyfile(ROOT / CONFIG, tmp_path / CONFIG)
    cfg = load()
    for key in ("first", "metropolitan", "waypoints"):
        source = ROOT / cfg["map_sources"][key + "_path"]
        target = tmp_path / cfg["map_sources"][key + "_path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    assert load(tmp_path)["candidate_id"] == cfg["candidate_id"]
    with (tmp_path / cfg["map_sources"]["first_path"]).open("ab") as stream:
        stream.write(b" ")
    with pytest.raises(ValueError, match="map source differs"):
        load(tmp_path)
