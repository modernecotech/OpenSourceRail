"""Reprice the selected Baghdad pathway layout at its explicit service offer."""

from dataclasses import replace
from itertools import pairwise
from math import ceil, isclose

from . import central_access, holistic_journeys, iraq_power


CASES = ("low", "base", "high")
SOURCES = ("system.toml", "system-results.json", "iraq-capital.toml", "iraq-market.toml",
           "iraq-power.toml", "iraq_power.py")


def service_assumptions(policy):
    return replace(holistic_journeys.JourneyAssumptions(), headway_s=policy["headway_s"],
                   operating_hours_day=policy["operating_hours_per_day"])


def service_quantities(network, policy, vehicle):
    assumptions = service_assumptions(policy)
    turnaround_s = 60 * policy["turnaround_min"]
    frequency_per_hour = 3600 / assumptions.headway_s
    rows = {}
    for code, line in network["lines"].items():
        positions = [line["station_chainage_km"][stop] for stop in line["station_ids"]]
        legs = [b - a for a, b in pairwise(positions)]
        if line["loop"]:
            legs.append(line["one_way_km"] - positions[-1])
        running_s = sum(holistic_journeys._running_time(km * 1000, assumptions) for km in legs)
        dwell_s = assumptions.dwell_s * (len(positions) if line["loop"] else len(positions) - 2)
        transit_s = running_s + dwell_s
        cycle_s = transit_s if line["loop"] else 2 * (transit_s + turnaround_s)
        sets = ceil(cycle_s / assumptions.headway_s) * (2 if line["loop"] else 1)
        train_km_day = 2 * line["one_way_km"] * frequency_per_hour * assumptions.operating_hours_day
        rows[code] = {"route_km": line["one_way_km"], "station_calls": len(positions),
                      "one_direction_running_and_dwell_s": transit_s, "circulation_s": cycle_s,
                      "active_trainsets": sets, "running_train_km_day": train_km_day}
    active = sum(line["active_trainsets"] for line in rows.values())
    fleet = ceil(active * (1 + policy["spare_fraction"]))
    depots = ceil(fleet / policy["nominal_sets_per_depot"])
    daily_km = sum(line["running_train_km_day"] for line in rows.values())
    return {"directional_headway_s": assumptions.headway_s, "operating_hours_day": assumptions.operating_hours_day,
            "terminal_turnback_s": turnaround_s, "rolling_stock_lines": rows, "active_trainsets": active,
            "reserve_trainsets": fleet - active, "fleet_trainsets": fleet,
            "cars": fleet * vehicle["cars_per_train"], "depot_allowances": depots,
            "control_centre_allowances": ceil(depots / policy["nominal_depots_per_control_centre"]),
            "running_train_km_day": daily_km, "running_train_km_year": daily_km * vehicle["service_days_per_year"],
            "nominal_places_per_hour_direction": vehicle["normal_places_per_train"] * frequency_per_hour}


def estimate(network, delivery, policy):
    if delivery["candidate_id"] != network["candidate_id"]:
        raise ValueError("Budget and construction quantities refer to different passenger layouts")
    cfg = iraq_power.read_toml("system.toml")
    rates = iraq_power.read_toml("iraq-capital.toml")
    currency = iraq_power.read_toml("iraq-market.toml")["currency"]["iqd_per_usd"]
    grid_prices = iraq_power.site_estimates(iraq_power.read_toml("iraq-power.toml")["equipment"], currency)
    electricity = iraq_power.rates()
    reference = central_access.read(central_access.CITY / "system-results.json")["networks"]["metropolitan"]
    energy_per_km = (reference["power_cases"]["protected_conductor"]["annual_grid_gwh"] * 1e6
                     / reference["selected_service_allowance"]["annual_train_km"])
    service = service_quantities(network, policy, cfg["vehicle"])
    counts = delivery["quantities"]
    if not isclose(counts["service_route_km"], sum(line["route_km"] for line in service["rolling_stock_lines"].values()),
                   rel_tol=0, abs_tol=.001):
        raise ValueError("Service and civil accounts use different route lengths")
    mileage = counts["unique_guideway_km"]
    track_km = counts["double_track_km"]
    grid_sites = sum(ceil(row["route_km"] / policy["supply_site_spacing_km"]) for row in delivery["orders"])
    power_sections = ceil(track_km / policy["power_section_track_km"])
    yearly_grid_gwh = service["running_train_km_year"] * energy_per_km / 1e6
    annual_grid_mean_mw = yearly_grid_gwh * 1000 / (service["operating_hours_day"] * cfg["vehicle"]["service_days_per_year"])
    capital = cfg["capital_rates_usd_m"]
    op = cfg["operation_rates"]
    power = cfg["power_assumptions"]
    conductor = cfg["power_price_allowances_usd_m"]
    discount = cfg["discount_rate_real"]
    years = cfg["comparison_years"]
    annuity = sum((1 + discount)**-year for year in range(1, years + 1))
    rows = {}
    for i, case in enumerate(CASES):
        civil = delivery["cost_cases"][case]
        route = rates["route"]
        facilities = rates["facilities"]
        train = rates["trains"]
        trainset_price = (cfg["vehicle"]["cars_per_train"] * train["contract_eur_m"] / train["contract_cars"]
                          * train["award_usd_per_eur"] * train["delivered_price_factor"][i])
        direct = {**civil["scope_usd_m"],
                  "signalling_comms": mileage * route["signalling_usd_m_per_route_km"][i],
                  "brake_protection_recovery": mileage * route["brake_recovery_usd_m_per_route_km"][i],
                  "line_traction_supply": (track_km * conductor["protected_conductor_per_track_km"]
                      + power_sections * conductor["protected_section_switchgear_each"])
                      * route["line_traction_supply_factor_on_published_equipment"][i],
                  "grid_charging_buffers": grid_sites * grid_prices[case]["direct_usd_m"],
                  "vehicles": service["fleet_trainsets"] * trainset_price,
                  "depots_control": (service["depot_allowances"] * facilities["depot_usd_m_each"][i]
                      + service["control_centre_allowances"] * facilities["control_centre_usd_m_each"][i]),
                  "tooling_recovery": (facilities["tooling_fixed_usd_m"][i]
                      + mileage * facilities["tooling_usd_m_per_route_km"][i])}
        direct_total = sum(direct.values())
        design = direct_total * capital["design_fraction"]
        test = direct_total * capital["testing_fraction"]
        reserve = (direct_total + design + test) * capital["project_allowance_fraction"]
        installed = direct_total + design + test + reserve
        annual = {"vehicles_and_operations": service["running_train_km_year"] * op["non_energy_vehicle_operations_usd_per_train_km"] / 1e6,
                  "stations": counts["station_sites"] * op["station_operations_usd_m_per_year"],
                  "electricity": yearly_grid_gwh * electricity[case]["delivered_usd_per_kwh"],
                  "line_power_maintenance": track_km * cfg["annual_power_maintenance_usd_m"]["protected_conductor_per_track_km"],
                  "civil_inspection": civil["annual_civil_inspection_usd_m"]}
        renewals = [
            {"year": 15, "scope": "common signalling and brake systems",
             "usd_m": (direct["signalling_comms"] + direct["brake_protection_recovery"])
                      * op["year_15_common_systems_replacement_fraction"]},
            {"year": 15, "scope": "grid electronics",
             "usd_m": direct["grid_charging_buffers"] * power["power_electronics_renewal_fraction_year_15"]},
            {"year": 20, "scope": "standard bearings", "usd_m": civil["year20_bearing_renewal_usd_m"]},
            {"year": 25, "scope": "line traction equipment",
             "usd_m": direct["line_traction_supply"] * power["line_equipment_renewal_fraction_year_25"]},
            {"year": 25, "scope": "major fleet renewal", "usd_m": direct["vehicles"] * op["year_25_fleet_replacement_fraction"]},
        ]
        annual_total = sum(annual.values())
        renewal_pv = sum(row["usd_m"] / (1 + discount)**row["year"] for row in renewals)
        rows[case] = {"direct_scope_usd_m": direct, "direct_total_usd_m": direct_total,
                      "design_usd_m": design, "testing_usd_m": test, "allowance_usd_m": reserve,
                      "installed_planning_usd_m": installed, "annual_operations_usd_m": annual,
                      "annual_operations_total_usd_m": annual_total, "renewals": renewals,
                      "whole_life_present_usd_m": installed + annual_total * annuity + renewal_pv}
    return {"candidate_id": network["candidate_id"], "service": service,
            "power": {"grid_kwh_per_train_km_allowance": energy_per_km, "annual_grid_gwh": yearly_grid_gwh,
                      "nominal_supply_sites": grid_sites, "nominal_protection_sections": power_sections,
                      "operating_mean_grid_mw": annual_grid_mean_mw},
            "discount_rate": discount, "years": years, "cost_cases": rows,
            "basis": "Constant 2026 USD planning allowances. Fleet follows the 18-hour, six-minute service offer; "
                     "take-up and timetable capacity need operating evidence. Construction funding dates are open.",
            "open_scopes": ["Timetable conflicts, fleet rotations, depot connections and capacity",
                            "Utility connections, electrical protection and grid failure cases",
                            "Station and special civil designs, property access and coordinated systems labour"]}
