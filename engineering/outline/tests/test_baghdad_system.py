"""The Baghdad public estimate must follow its route, car, civil and power inputs."""
from pathlib import Path
import shutil
import json

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


def test_metropolitan_route_and_economics_are_standalone(tmp_path: Path):
    cfg = load()
    map_path = ROOT / cfg["map_sources"]["metropolitan_path"]
    geo = json.loads(map_path.read_text())
    routes = [f for f in geo["features"] if f["geometry"]["type"] == "LineString"
              and f["properties"].get("map_layer") == "railway route"]
    ids = {f["properties"]["route_id"] for f in routes}
    assert len(cfg["networks"]["metropolitan"]["service_groups"]) == 14
    assert {"B-A01", "B-A02", "B-A03", "B-A04", "B-A05", "B-A06"} <= ids
    assert all(f["properties"].get("standalone_shuttle") is not True for f in routes)
    first = evaluate("metropolitan", "protected_conductor")
    local = first["local_delivery"]
    assert local["planning_local_contract_usd_m"] == pytest.approx(12599.029, abs=0.001)
    assert local["royalty_or_ip_savings_in_capital_usd_m"] is None
    assert local["actual_supplier_origin_established"] is False
    assert local["project_allowance_unassigned_usd_m"] > 0
    assert first["capital_usd_m"]["installed"] == pytest.approx(31017.748542)
    (tmp_path / CONFIG).parent.mkdir(parents=True)
    text = (ROOT / CONFIG).read_text().replace('first_sha256 = "923bbe3b158b85b20f63f2611d6be61659ec373a20303c34834e71e859037bb4"',
                                            'first_sha256 = "changed-first-plan"')
    (tmp_path / CONFIG).write_text(text)
    target = tmp_path / cfg["map_sources"]["metropolitan_path"]
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(map_path, target)
    for name in ("baghdad_power.py", "baghdad_viaduct.py"):
        source = ROOT / "engineering/outline" / name
        target = tmp_path / "engineering/outline" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    independent = evaluate("metropolitan", "protected_conductor", root=tmp_path)
    assert independent["physical_candidate_id"] == first["physical_candidate_id"]
    assert independent["evaluation_id"] == first["evaluation_id"]


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


def test_station_geometry_changes_physical_identity_and_rejects_clashes(tmp_path: Path):
    (tmp_path / CONFIG).parent.mkdir(parents=True)
    shutil.copyfile(ROOT / CONFIG, tmp_path / CONFIG)
    cfg = load()
    for key in ("first", "metropolitan", "waypoints"):
        source = ROOT / cfg["map_sources"][key + "_path"]
        target = tmp_path / cfg["map_sources"][key + "_path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    for name in ("baghdad_power.py", "baghdad_viaduct.py"):
        target = tmp_path / "engineering/outline" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / "engineering/outline" / name, target)
    original = evaluate("first", "protected_conductor", root=tmp_path)
    path = tmp_path / CONFIG
    path.write_text(path.read_text().replace("body_width_m = 2.7", "body_width_m = 2.72"))
    wider = evaluate("first", "protected_conductor", root=tmp_path)
    assert wider["physical_candidate_id"] != original["physical_candidate_id"]
    assert wider["station_interfaces"]["static_body_edge_gap_m"] < original["station_interfaces"]["static_body_edge_gap_m"]
    path.write_text(path.read_text().replace("body_width_m = 2.72", "body_width_m = 2.9"))
    with pytest.raises(ValueError, match="station or door geometry"):
        evaluate("first", "protected_conductor", root=tmp_path)


def test_independent_service_power_has_outage_and_price_headroom():
    row = evaluate("first", "protected_conductor")
    supply = row["service_power"]
    assert supply["declared_usable_kwh"] >= supply["required_usable_kwh_with_reserve"]
    assert supply["nominal_battery_kwh_per_train"] == 65
    assert supply["fleet_price_allocation_within_vehicles_usd_m"] == pytest.approx(24.2)
    assert (supply["fleet_price_allocation_within_vehicles_usd_m"]
            + row["control_electronics"]["allocation_within_capital_scopes_usd_m"]["vehicles"]
            < row["capital_usd_m"]["scope_rows"]["vehicles"])
