"""Bounded equal-service traction-supply comparison for a Baghdad planning candidate.

This is an energy, adhesion, installed-mass and equipment-quantity screen. It is
not a circuit design, a thermal qualification or an electrical-safety approval.
The caller supplies the one network record used by every option; options never
inherit the v0.7.0 overhead candidate's physical identity or acceptance.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from math import ceil, isclose, isfinite
from pathlib import Path


OPTIONS = ("station_battery", "protected_conductor", "limited_conductor_battery", "overhead")
MODEL = "osr-baghdad-equal-service-power/1"


@dataclass(frozen=True)
class PowerNetwork:
    candidate_id: str
    normal_places_per_train: int
    route_km: float
    station_count: int
    line_count: int
    active_trainsets: int
    fleet_trainsets: int
    annual_train_km: float
    grid_site_count: int
    train_mass_t: float
    train_energy_kwh_per_km: float
    peak_headway_s: float
    dwell_s: float
    speed_cap_m_s: float
    service_hours_per_day: float
    service_days_per_year: int


@dataclass(frozen=True)
class PowerAssumptions:
    # Explicit digital-design controls. Replace with supplier/site records.
    adverse_grade: float = 0.02
    required_net_accel_m_s2: float = 0.6
    resistance_accel_m_s2: float = 0.02
    low_adhesion_mu: float = 0.10
    adhesion_force_margin: float = 1.15
    total_axles: int = 24
    driven_axle_pair_multiple: int = 2
    motor_inverter_mass_t_per_axle: float = 0.195
    reference_driven_axles: int = 24
    traction_efficiency: float = 0.82
    traction_rating_margin: float = 1.25
    # Evaluation voltage for a current request, not an installed supply choice.
    electrical_screen_voltage_kv: float = 1.5
    electrical_screen_low_voltage_fraction: float = 0.90
    roof_collector_mass_t: float = 0.96
    station_connector_mass_t: float = 0.20
    protected_shoes_mass_t: float = 0.32
    battery_pack_kwh_per_t: float = 120.0
    battery_cooling_t_per_mwh: float = 0.50
    battery_usable_fraction: float = 0.70
    battery_discharge_efficiency: float = 0.96
    battery_legs_between_effective_charges: int = 4
    battery_reserve_legs: int = 2
    limited_supply_offwire_legs: int = 2
    limited_supply_fraction_of_route: float = 0.25
    incremental_energy_kwh_per_km_per_t: float = 0.03
    station_charge_efficiency: float = 0.90
    limited_supply_charge_efficiency: float = 0.90
    conductor_grid_efficiency: float = 0.94
    overhead_grid_efficiency: float = 0.93
    grid_peak_over_service_mean: float = 1.50
    charge_buffer_pair_cycles_per_station: int = 2
    buffer_life_years: int = 12
    battery_life_years: int = 10
    power_electronics_renewal_fraction_year_15: float = 0.50
    line_equipment_renewal_fraction_year_25: float = 0.25
    design_years: int = 30


def _digest(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    return sha256(raw).hexdigest()


def _validate(n: PowerNetwork, a: PowerAssumptions) -> None:
    if not n.candidate_id or n.normal_places_per_train < 1 or any(not isfinite(v) or v <= 0 for v in (
        n.route_km, n.annual_train_km, n.train_mass_t, n.train_energy_kwh_per_km,
        n.peak_headway_s, n.dwell_s, n.speed_cap_m_s, n.service_hours_per_day)):
        raise ValueError("Positive, finite Baghdad service inputs required")
    if (n.station_count <= n.line_count or n.line_count < 1 or n.grid_site_count < 1
            or n.active_trainsets < 1 or n.fleet_trainsets < n.active_trainsets
            or n.dwell_s >= n.peak_headway_s or n.service_hours_per_day > 24
            or not 1 <= n.service_days_per_year <= 366):
        raise ValueError("Inconsistent station, fleet or timetable inputs")
    if (a.total_axles < 1 or a.total_axles % a.driven_axle_pair_multiple
            or a.reference_driven_axles > a.total_axles
            or a.low_adhesion_mu <= 0 or a.adhesion_force_margin < 1
            or not 0 < a.limited_supply_fraction_of_route < 1
            or not 0 < a.battery_usable_fraction <= 1
            or not 0 < a.battery_discharge_efficiency <= 1
            or not 0 < a.traction_efficiency <= 1
            or not isfinite(a.electrical_screen_voltage_kv)
            or a.electrical_screen_voltage_kv <= 0
            or not 0 < a.electrical_screen_low_voltage_fraction <= 1):
        raise ValueError("Inconsistent traction or storage controls")
    if (a.battery_legs_between_effective_charges < 1 or a.battery_reserve_legs < 1
            or a.limited_supply_offwire_legs < 1 or a.battery_pack_kwh_per_t <= 0
            or a.design_years < 1 or a.battery_life_years < 1 or a.buffer_life_years < 1):
        raise ValueError("Invalid storage life or reserve controls")
    if not all(0 < v <= 1 for v in (
        a.station_charge_efficiency, a.limited_supply_charge_efficiency,
        a.conductor_grid_efficiency, a.overhead_grid_efficiency)):
        raise ValueError("Grid efficiencies must be within (0, 1]")


def _storage_energy_and_mass(n: PowerNetwork, a: PowerAssumptions,
                             option: str, leg_km: float,
                             drive_delta_t: float) -> tuple[float, float, float, float]:
    """Solve the small mass-energy loop analytically, with no silent zero mass."""
    if option == "station_battery":
        legs = a.battery_legs_between_effective_charges + a.battery_reserve_legs
        fixed_delta_t = -a.roof_collector_mass_t + a.station_connector_mass_t
    elif option == "limited_conductor_battery":
        legs = a.limited_supply_offwire_legs + a.battery_reserve_legs
        fixed_delta_t = -a.roof_collector_mass_t + a.protected_shoes_mass_t
    elif option == "protected_conductor":
        legs = 0
        fixed_delta_t = -a.roof_collector_mass_t + a.protected_shoes_mass_t
    else:
        legs = 0
        fixed_delta_t = 0.0
    fixed_delta_t += drive_delta_t
    kwh_per_unit_energy = leg_km * legs / (a.battery_usable_fraction
                                            * a.battery_discharge_efficiency)
    added_t_per_kwh = 1 / a.battery_pack_kwh_per_t + a.battery_cooling_t_per_mwh / 1000
    coefficient = a.incremental_energy_kwh_per_km_per_t * kwh_per_unit_energy * added_t_per_kwh
    if coefficient >= 1:
        raise ValueError("Storage-mass energy loop has no finite solution")
    energy_kwh_per_km = (n.train_energy_kwh_per_km
                         + a.incremental_energy_kwh_per_km_per_t * fixed_delta_t) / (1 - coefficient)
    if energy_kwh_per_km <= 0:
        raise ValueError("Storage-mass energy loop returned nonpositive demand")
    battery_kwh = energy_kwh_per_km * kwh_per_unit_energy
    battery_mass_t = battery_kwh / a.battery_pack_kwh_per_t
    cooling_mass_t = battery_kwh / 1000 * a.battery_cooling_t_per_mwh
    delta_mass_t = fixed_delta_t + battery_mass_t + cooling_mass_t
    return energy_kwh_per_km, battery_kwh, cooling_mass_t, delta_mass_t


def _renewals(a: PowerAssumptions, fleet_battery_mwh: float,
              buffer_mwh: float, charger_ports: int, powered_track_km: float,
              grid_sites: int, energized_sections: int) -> list[dict]:
    events: list[dict] = []
    if fleet_battery_mwh:
        for year in range(a.battery_life_years, a.design_years, a.battery_life_years):
            events.append(dict(year=year, component="onboard_traction_battery", quantity=fleet_battery_mwh, unit="MWh"))
    if buffer_mwh:
        for year in range(a.buffer_life_years, a.design_years, a.buffer_life_years):
            events.append(dict(year=year, component="station_buffer", quantity=buffer_mwh, unit="MWh"))
    if charger_ports:
        events.append(dict(year=15, component="charger_power_electronics",
                           quantity=charger_ports * a.power_electronics_renewal_fraction_year_15, unit="ports"))
    events.append(dict(year=15, component="grid_site_power_electronics",
                       quantity=grid_sites * a.power_electronics_renewal_fraction_year_15,
                       unit="sites"))
    if energized_sections:
        events.append(dict(year=15, component="line_section_protection",
                           quantity=energized_sections * a.power_electronics_renewal_fraction_year_15,
                           unit="sections"))
    if powered_track_km:
        events.append(dict(year=25, component="line_power_equipment",
                           quantity=powered_track_km * a.line_equipment_renewal_fraction_year_25,
                           unit="track-km"))
    # Traction motors/inverters and common protection remain in the common vehicle
    # renewal scope. This module prices only differences between supply options.
    return events


def priced_protected_overhead_sensitivity(
    protected: dict, overhead: dict, *,
    conductor_price_usd_m_per_track_km: float,
    conductor_maintenance_usd_m_per_track_km_year: float,
    energy_tariff_usd_per_kwh: float,
    design_fraction: float, testing_fraction: float,
    project_allowance_fraction: float,
    line_renewal_fraction_year_25: float,
    discount_rate_real: float, years: int,
) -> dict:
    """Decompose priced 30-year costs and vary one conductor input at a time.

    All physical quantities remain those of the two supplied, fully priced
    equal-service options. This arithmetic screen does not model new equipment,
    procurement uncertainty distributions, feeder layouts or financing.
    """
    if (protected.get("supply") != "protected_conductor"
            or overhead.get("supply") != "overhead"):
        raise ValueError("Protected conductor and overhead priced cases required")
    if protected["parent_candidate_id"] != overhead["parent_candidate_id"]:
        raise ValueError("Power options must share a parent candidate")
    protected_track_km = protected["supply_quantities"]["protected_conductor_track_km"]
    overhead_track_km = overhead["supply_quantities"]["overhead_track_km"]
    if not isclose(protected_track_km, overhead_track_km, rel_tol=0, abs_tol=1e-6):
        raise ValueError("Power options must cover the same track length")
    numeric = (conductor_price_usd_m_per_track_km,
               conductor_maintenance_usd_m_per_track_km_year,
               energy_tariff_usd_per_kwh, design_fraction, testing_fraction,
               project_allowance_fraction, line_renewal_fraction_year_25,
               discount_rate_real)
    if (any(not isfinite(value) or value < 0 for value in numeric)
            or conductor_price_usd_m_per_track_km == 0
            or energy_tariff_usd_per_kwh == 0 or years < 1):
        raise ValueError("Finite, nonnegative sensitivity inputs required")
    annuity = sum((1 + discount_rate_real) ** -year for year in range(1, years + 1))
    capital = overhead["capital_usd_m"]["installed"] - protected["capital_usd_m"]["installed"]
    energy = ((overhead["operation_usd_m_year"]["energy"]
               - protected["operation_usd_m_year"]["energy"]) * annuity)
    maintenance = ((overhead["operation_usd_m_year"]["power_maintenance"]
                    - protected["operation_usd_m_year"]["power_maintenance"]) * annuity)
    other_operation = ((overhead["operation_usd_m_year"]["non_energy_and_station"]
                        - protected["operation_usd_m_year"]["non_energy_and_station"]) * annuity)
    renewal = (sum(row["usd_m"] / (1 + discount_rate_real) ** row["year"]
                   for row in overhead["renewals_usd_m"])
               - sum(row["usd_m"] / (1 + discount_rate_real) ** row["year"]
                     for row in protected["renewals_usd_m"]))
    advantage = (overhead["whole_life_30y_present_usd_m"]
                 - protected["whole_life_30y_present_usd_m"])
    if not isclose(capital + energy + maintenance + other_operation + renewal,
                   advantage, rel_tol=1e-10, abs_tol=1e-7):
        raise ValueError("Power cost components do not reconcile")
    installed_multiplier = ((1 + design_fraction + testing_fraction)
                            * (1 + project_allowance_fraction))
    line_price_slope = (protected_track_km * installed_multiplier
                        + protected_track_km * line_renewal_fraction_year_25
                        / (1 + discount_rate_real) ** 25)
    maintenance_slope = protected_track_km * annuity
    loss_slope = protected["energy"]["annual_grid_chain_loss_gwh"] * energy_tariff_usd_per_kwh * annuity
    renewal_slope = (protected_track_km * conductor_price_usd_m_per_track_km
                     / (1 + discount_rate_real) ** 25)
    variations = (
        ("conductor_equipment_plus_10_percent", line_price_slope * conductor_price_usd_m_per_track_km * 0.10),
        ("conductor_equipment_plus_20_percent", line_price_slope * conductor_price_usd_m_per_track_km * 0.20),
        ("conductor_maintenance_plus_50_percent", maintenance_slope * conductor_maintenance_usd_m_per_track_km_year * 0.50),
        ("conductor_maintenance_plus_100_percent", maintenance_slope * conductor_maintenance_usd_m_per_track_km_year),
        ("grid_chain_losses_plus_25_percent", loss_slope * 0.25),
        ("line_renewal_fraction_plus_25_percentage_points", renewal_slope * 0.25),
    )
    return {
        "basis": "One priced protected-conductor input varied against overhead; all physical quantities and other prices fixed",
        "protected_advantage_usd_m": advantage,
        "protected_advantage_fraction_of_overhead": advantage / overhead["whole_life_30y_present_usd_m"],
        "advantage_components_usd_m": {"installed_capital": capital, "energy": energy,
                                       "power_maintenance": maintenance,
                                       "other_operation": other_operation,
                                       "renewals": renewal},
        "conductor_equipment_break_even_usd_m_per_track_km":
            conductor_price_usd_m_per_track_km + advantage / line_price_slope,
        "one_at_a_time_screens": {
            name: {"added_protected_present_cost_usd_m": delta,
                   "remaining_protected_advantage_usd_m": advantage - delta,
                   "protected_lower_under_this_input": advantage > delta}
            for name, delta in variations},
        "limitations": "Single-input operating-energy sensitivities hold grid-site rating, equipment quantities and vehicle mass fixed; no supplier price range, financing or physical protection rating is established",
        "procurement_winner_established": False,
    }


def compare_power(network: PowerNetwork, assumptions: PowerAssumptions = PowerAssumptions()) -> dict[str, dict]:
    """Return matched option quantities for one explicit network candidate.

    The result is cost-ready, but carries no unit prices or architecture selection.
    A no-overhead preference can only be selected after matched 30-year pricing.
    """
    n, a = network, assumptions
    _validate(n, a)
    input_id = _digest(dict(network=asdict(n), assumptions=asdict(a), model=MODEL))
    producer_sha = sha256(Path(__file__).read_bytes()).hexdigest()
    leg_km = n.route_km / (n.station_count - n.line_count)
    service_hours_year = n.service_hours_per_day * n.service_days_per_year
    result: dict[str, dict] = {}
    acceleration_with_grade_m_s2 = (a.required_net_accel_m_s2
                                     + 9.81 * a.adverse_grade + a.resistance_accel_m_s2)
    raw_driven = ceil(acceleration_with_grade_m_s2 * a.adhesion_force_margin
                      * a.total_axles / (a.low_adhesion_mu * 9.81))
    driven = ceil(raw_driven / a.driven_axle_pair_multiple) * a.driven_axle_pair_multiple
    if driven > a.total_axles:
        raise ValueError("Declared low-adhesion/acceleration duty exceeds all available axles")
    drive_delta_t = (driven - a.reference_driven_axles) * a.motor_inverter_mass_t_per_axle
    for option in OPTIONS:
        energy_per_km, battery_kwh, cooling_t, delta_mass_t = _storage_energy_and_mass(
            n, a, option, leg_km, drive_delta_t)
        mass_t = n.train_mass_t + delta_mass_t
        if mass_t <= 0:
            raise ValueError("Installed train mass must remain positive")
        force_n = mass_t * 1000 * acceleration_with_grade_m_s2
        axle_adhesion_n = a.low_adhesion_mu * mass_t * 1000 * 9.81 / a.total_axles
        wheel_power_mw = force_n * n.speed_cap_m_s / 1e6
        traction_dc_duty_mw = wheel_power_mw / a.traction_efficiency
        traction_dc_request_mw = traction_dc_duty_mw * a.traction_rating_margin
        traction_duty_loss_mw = traction_dc_duty_mw - wheel_power_mw
        per_leg_kwh = energy_per_km * leg_km
        if option == "station_battery":
            efficiency = a.station_charge_efficiency
            charger_port_mw = per_leg_kwh / (n.dwell_s / 3600) / efficiency / 1000
            charger_ports = 2 * n.station_count
            buffer_mwh = (2 * a.charge_buffer_pair_cycles_per_station * per_leg_kwh
                          / efficiency / 1000) * n.station_count
            powered_track_km = 0.0
            protected_track_km = 0.0
            overhead_track_km = 0.0
            energized_sections = 0
            onboard_contact_sets = 2 * n.fleet_trainsets
        elif option == "limited_conductor_battery":
            efficiency = a.limited_supply_charge_efficiency
            powered_distance_km = leg_km * a.limited_supply_fraction_of_route
            charger_port_mw = per_leg_kwh / (powered_distance_km * 1000 / n.speed_cap_m_s / 3600) / efficiency / 1000
            charger_ports = 0
            buffer_mwh = 0.0
            powered_track_km = 2 * n.route_km * a.limited_supply_fraction_of_route
            protected_track_km = powered_track_km
            overhead_track_km = 0.0
            energized_sections = 2 * (n.station_count - n.line_count)
            onboard_contact_sets = 4 * n.fleet_trainsets
        elif option == "protected_conductor":
            efficiency = a.conductor_grid_efficiency
            charger_port_mw = 0.0
            charger_ports = 0
            buffer_mwh = 0.0
            powered_track_km = 2 * n.route_km
            protected_track_km = powered_track_km
            overhead_track_km = 0.0
            energized_sections = 2 * (n.station_count - n.line_count)
            onboard_contact_sets = 4 * n.fleet_trainsets
        else:
            efficiency = a.overhead_grid_efficiency
            charger_port_mw = 0.0
            charger_ports = 0
            buffer_mwh = 0.0
            powered_track_km = 2 * n.route_km
            protected_track_km = 0.0
            overhead_track_km = powered_track_km
            energized_sections = 2 * (n.station_count - n.line_count)
            onboard_contact_sets = 6 * n.fleet_trainsets
        collection_request_mw = (max(traction_dc_request_mw, charger_port_mw)
                                 if option != "station_battery" else 0.0)
        train_energy_gwh_year = n.annual_train_km * energy_per_km / 1e6
        grid_energy_gwh_year = train_energy_gwh_year / efficiency
        grid_chain_loss_gwh_year = grid_energy_gwh_year - train_energy_gwh_year
        mean_service_grid_mw = grid_energy_gwh_year * 1000 / service_hours_year
        design_grid_mw = mean_service_grid_mw * a.grid_peak_over_service_mean
        if option == "station_battery":
            expected_charge_ports = charger_ports * n.dwell_s / n.peak_headway_s
            # This is a timetable occupancy average, not a proven simultaneous peak.
            occupancy_grid_mw = expected_charge_ports * charger_port_mw
            design_grid_mw = max(design_grid_mw, occupancy_grid_mw)
            uncoordinated_grid_mw = charger_ports * charger_port_mw
        else:
            expected_charge_ports = 0.0
            occupancy_grid_mw = 0.0
            uncoordinated_grid_mw = 0.0
        fleet_battery_mwh = battery_kwh * n.fleet_trainsets / 1000
        renewal = _renewals(a, fleet_battery_mwh, buffer_mwh,
                            charger_ports, powered_track_km, n.grid_site_count,
                            energized_sections)
        physical = dict(parent=n.candidate_id, power_option=option,
                        train_mass_t=round(mass_t, 8), driven_axles=driven,
                        battery_kwh=round(battery_kwh, 8), line_track_km=round(powered_track_km, 8))
        row = dict(
            schema=MODEL, input_id=input_id, producer_sha256=producer_sha,
            parent_candidate_id=n.candidate_id, option=option,
            physical_candidate_id="osr-baghdad-power-" + _digest(physical)[:20],
            common_service=dict(route_km=n.route_km, stations=n.station_count, lines=n.line_count,
                                peak_headway_s=n.peak_headway_s, dwell_s=n.dwell_s,
                                normal_places_per_train=n.normal_places_per_train, mean_interstation_km=leg_km,
                                annual_train_km=n.annual_train_km,
                                active_trainsets=n.active_trainsets,
                                fleet_trainsets=n.fleet_trainsets,
                                service_hours_per_day=n.service_hours_per_day,
                                service_days_per_year=n.service_days_per_year),
            vehicle=dict(mass_t=mass_t, delta_from_overhead_comparator_t=delta_mass_t,
                         traction_battery_kwh_per_train=battery_kwh,
                         traction_battery_t_per_train=battery_kwh / a.battery_pack_kwh_per_t,
                         battery_cooling_t_per_train=cooling_t,
                         fleet_battery_mwh=fleet_battery_mwh,
                         driven_axles=driven, reference_driven_axles=a.reference_driven_axles,
                         changed_motor_inverter_modules=driven - a.reference_driven_axles,
                         onboard_contact_sets=onboard_contact_sets),
            traction=dict(required_force_kn=force_n / 1000,
                          low_adhesion_mu=a.low_adhesion_mu,
                          adhesion_available_kn=driven * axle_adhesion_n / 1000,
                          adhesion_required_with_margin_kn=force_n * a.adhesion_force_margin / 1000,
                          adhesion_feasible=(driven * axle_adhesion_n
                                             >= force_n * a.adhesion_force_margin),
                          raw_minimum_driven_axles=raw_driven,
                          dc_input_rating_request_mw=traction_dc_request_mw,
                          wheel_power_at_declared_duty_mw=wheel_power_mw,
                          dc_input_at_declared_duty_mw=traction_dc_duty_mw,
                          traction_drive_loss_at_declared_duty_mw=traction_duty_loss_mw,
                          electrical_screen={
                              "voltage_kv_not_selected": a.electrical_screen_voltage_kv,
                              "low_voltage_fraction": a.electrical_screen_low_voltage_fraction,
                              "line_supply_applicable": option != "station_battery",
                              "powered_section_count": energized_sections,
                              "mean_powered_section_length_km":
                                  powered_track_km / energized_sections if energized_sections else None,
                              "one_train_constant_power_current_request_ka":
                                  collection_request_mw / a.electrical_screen_voltage_kv
                                  if collection_request_mw else None,
                              "one_train_low_voltage_current_request_ka":
                                  collection_request_mw / (a.electrical_screen_voltage_kv
                                                           * a.electrical_screen_low_voltage_fraction)
                                  if collection_request_mw else None,
                              "two_coincident_trains_low_voltage_request_ka":
                                  2 * collection_request_mw / (a.electrical_screen_voltage_kv
                                                               * a.electrical_screen_low_voltage_fraction)
                                  if collection_request_mw else None,
                              "section_current_rating_established": False,
                              "feeder_and_return_circuit_modelled": False,
                              "receiving_regenerative_braking_modelled": False},
                          independent_braking_modelled_here=False),
            energy=dict(onboard_kwh_per_train_km=energy_per_km,
                        interstation_kwh_per_train=per_leg_kwh,
                        annual_onboard_gwh=train_energy_gwh_year,
                        annual_grid_gwh=grid_energy_gwh_year,
                        annual_grid_chain_loss_gwh=grid_chain_loss_gwh_year,
                        grid_chain_efficiency=efficiency),
            supply=dict(overhead_track_km=overhead_track_km,
                        protected_conductor_track_km=protected_track_km,
                        line_power_track_km=powered_track_km,
                        powered_section_count=energized_sections,
                        station_charge_ports=charger_ports,
                        station_charge_port_mw=charger_port_mw if charger_ports else 0.0,
                        limited_section_collection_request_mw=(
                            charger_port_mw if option == "limited_conductor_battery" else 0.0),
                        station_pair_max_pulse_mw=2 * charger_port_mw if charger_ports else 0.0,
                        timetable_mean_concurrent_charge_ports=expected_charge_ports,
                        timetable_mean_charge_mw=occupancy_grid_mw,
                        uncoordinated_all_ports_upper_mw=uncoordinated_grid_mw,
                        stationary_buffer_mwh=buffer_mwh,
                        grid_sites=n.grid_site_count,
                        mean_grid_mw_during_service=mean_service_grid_mw,
                        provisional_grid_design_request_mw=design_grid_mw,
                        provisional_grid_site_rating_mw=design_grid_mw / n.grid_site_count,
                        train_collection_request_mw=max(traction_dc_request_mw, charger_port_mw)),
            maintenance_quantities=dict(annual_train_km=n.annual_train_km,
                                        overhead_track_km=overhead_track_km,
                                        protected_conductor_track_km=protected_track_km,
                                        charger_ports=charger_ports,
                                        powered_section_count=energized_sections,
                                        onboard_contact_sets=onboard_contact_sets,
                                        fleet_traction_battery_mwh=fleet_battery_mwh,
                                        stationary_buffer_mwh=buffer_mwh,
                                        grid_sites=n.grid_site_count),
            renewal_events=renewal,
            evidence_status=dict(analytical_screen=True, route_profile_measured=False,
                                 hot_thermal_qualified=False, grid_connection_approved=False,
                                 protected_contact_approved=False,
                                 section_protection_selectivity_verified=False,
                                 return_current_and_touch_voltage_modelled=False,
                                 physical_accepted=False),
        )
        row["evaluation_id"] = _digest(row)
        result[option] = row
    return result
