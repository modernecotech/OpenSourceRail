"""Matched Baghdad power alternatives retain energy, mass and renewal scope."""

from dataclasses import replace
from math import isclose

import pytest

from engineering.outline.baghdad_power import PowerAssumptions, PowerNetwork, compare_power


FIRST = PowerNetwork(
    candidate_id="baghdad-148.2km-zero-tunnel-digital-screen",
    normal_places_per_train=700,
    route_km=148.2, station_count=64, line_count=7,
    active_trainsets=210, fleet_trainsets=242,
    annual_train_km=52_429_000, grid_site_count=30,
    train_mass_t=201.732, train_energy_kwh_per_km=20,
    peak_headway_s=150, dwell_s=35, speed_cap_m_s=20,
    service_hours_per_day=18, service_days_per_year=365,
)


def test_four_options_keep_identical_service_and_distinct_physical_candidates():
    cases = compare_power(FIRST)
    assert len(cases) == 4
    assert len({row["physical_candidate_id"] for row in cases.values()}) == 4
    assert len({row["evaluation_id"] for row in cases.values()}) == 4
    assert len({row["input_id"] for row in cases.values()}) == 1
    assert {row["common_service"]["normal_places_per_train"] for row in cases.values()} == {700}
    assert {row["common_service"]["annual_train_km"] for row in cases.values()} == {52_429_000}
    assert {row["vehicle"]["driven_axles"] for row in cases.values()} == {24}
    assert all(row["traction"]["adhesion_feasible"] is True for row in cases.values())
    assert all(row["traction"]["adhesion_available_kn"]
               >= row["traction"]["adhesion_required_with_margin_kn"] for row in cases.values())
    assert all(row["traction"]["independent_braking_modelled_here"] is False for row in cases.values())
    assert all(row["evidence_status"]["physical_accepted"] is False for row in cases.values())


def test_offwire_scope_energy_mass_and_charge_duty_reconcile():
    cases = compare_power(FIRST)
    a, b, c, d = (cases[key] for key in cases)
    assert all(row["supply"]["overhead_track_km"] == 0 for row in (a, b, c))
    assert isclose(d["supply"]["overhead_track_km"], 296.4)
    assert isclose(b["supply"]["protected_conductor_track_km"], 296.4)
    assert isclose(c["supply"]["protected_conductor_track_km"], 74.1)
    assert a["supply"]["station_charge_ports"] == 128
    assert a["supply"]["station_charge_port_mw"] > 5.9
    assert a["supply"]["stationary_buffer_mwh"] > 14
    assert a["supply"]["uncoordinated_all_ports_upper_mw"] > a["supply"]["provisional_grid_design_request_mw"]
    assert a["vehicle"]["traction_battery_kwh_per_train"] > c["vehicle"]["traction_battery_kwh_per_train"] > 0
    assert b["vehicle"]["traction_battery_kwh_per_train"] == d["vehicle"]["traction_battery_kwh_per_train"] == 0
    assert a["vehicle"]["mass_t"] > c["vehicle"]["mass_t"] > d["vehicle"]["mass_t"] > b["vehicle"]["mass_t"]
    for row in cases.values():
        assert isclose(row["energy"]["annual_onboard_gwh"],
                       row["energy"]["onboard_kwh_per_train_km"] * FIRST.annual_train_km / 1e6)
        assert isclose(row["energy"]["annual_grid_gwh"],
                       row["energy"]["annual_onboard_gwh"] / row["energy"]["grid_chain_efficiency"])


def test_renewal_quantities_and_driven_axle_sensitivity():
    cases = compare_power(FIRST)
    renewals_a = cases["station_battery"]["renewal_events"]
    assert [row["year"] for row in renewals_a if row["component"] == "onboard_traction_battery"] == [10, 20]
    assert [row["year"] for row in renewals_a if row["component"] == "station_buffer"] == [12, 24]
    assert any(row["component"] == "line_power_equipment" for row in cases["overhead"]["renewal_events"])
    higher_mu = compare_power(FIRST, replace(PowerAssumptions(), low_adhesion_mu=0.12))
    assert all(row["vehicle"]["driven_axles"] == 20 for row in higher_mu.values())
    assert all(row["vehicle"]["changed_motor_inverter_modules"] == -4 for row in higher_mu.values())
    assert higher_mu["station_battery"]["vehicle"]["mass_t"] < cases["station_battery"]["vehicle"]["mass_t"]
    with pytest.raises(ValueError, match="exceeds all available axles"):
        compare_power(FIRST, replace(PowerAssumptions(), low_adhesion_mu=0.08))


def test_metropolitan_network_uses_its_own_fleet_and_grid_counts():
    full = replace(FIRST, candidate_id="baghdad-605.652km-zero-tunnel-digital-screen",
                   route_km=605.652, station_count=280, line_count=14,
                   active_trainsets=812, fleet_trainsets=934,
                   annual_train_km=202_724_000, grid_site_count=100)
    cases = compare_power(full)
    assert isclose(cases["overhead"]["supply"]["overhead_track_km"], 1211.304)
    assert cases["station_battery"]["supply"]["station_charge_ports"] == 560
    assert cases["station_battery"]["vehicle"]["fleet_battery_mwh"] > 300
    assert all(row["supply"]["grid_sites"] == 100 for row in cases.values())
    assert all(row["common_service"]["mean_interstation_km"] < 2.3 for row in cases.values())


def test_electrical_current_and_loss_screen_does_not_select_installed_voltage():
    base = compare_power(FIRST)
    selected = base["protected_conductor"]
    screen = selected["traction"]["electrical_screen"]
    assert selected["traction"]["dc_input_rating_request_mw"] > 5.0
    assert screen["voltage_kv_not_selected"] == 1.5
    assert screen["one_train_constant_power_current_request_ka"] == pytest.approx(
        selected["supply"]["train_collection_request_mw"] / 1.5)
    assert screen["one_train_low_voltage_current_request_ka"] == pytest.approx(
        screen["one_train_constant_power_current_request_ka"] / 0.9)
    assert screen["two_coincident_trains_low_voltage_request_ka"] == pytest.approx(
        2 * screen["one_train_low_voltage_current_request_ka"])
    assert screen["section_current_rating_established"] is False
    assert screen["feeder_and_return_circuit_modelled"] is False
    assert selected["traction"]["traction_drive_loss_at_declared_duty_mw"] == pytest.approx(
        selected["traction"]["dc_input_at_declared_duty_mw"]
        - selected["traction"]["wheel_power_at_declared_duty_mw"])
    assert selected["energy"]["annual_grid_chain_loss_gwh"] == pytest.approx(
        selected["energy"]["annual_grid_gwh"] - selected["energy"]["annual_onboard_gwh"])
    assert base["station_battery"]["traction"]["electrical_screen"]["line_supply_applicable"] is False
    assert base["station_battery"]["traction"]["electrical_screen"][
        "one_train_constant_power_current_request_ka"] is None
    changed_voltage = compare_power(FIRST, replace(PowerAssumptions(), electrical_screen_voltage_kv=2.0))
    assert changed_voltage["protected_conductor"]["physical_candidate_id"] == selected["physical_candidate_id"]
    assert changed_voltage["protected_conductor"]["evaluation_id"] != selected["evaluation_id"]


def test_invalid_electrical_screen_is_rejected():
    with pytest.raises(ValueError, match="Inconsistent traction"):
        compare_power(FIRST, replace(PowerAssumptions(), electrical_screen_voltage_kv=0))
    with pytest.raises(ValueError, match="Inconsistent traction"):
        compare_power(FIRST, replace(PowerAssumptions(), electrical_screen_low_voltage_fraction=1.1))


def test_invalid_service_is_rejected_before_comparison():
    with pytest.raises(ValueError, match="Inconsistent station"):
        compare_power(replace(FIRST, station_count=7))
    with pytest.raises(ValueError, match="Inconsistent station"):
        compare_power(replace(FIRST, dwell_s=150))
