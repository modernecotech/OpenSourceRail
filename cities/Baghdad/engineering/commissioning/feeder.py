"""Screen one restored Airport radial feed and the supplier's protection envelope."""

import argparse
from hashlib import sha256
import json
import tomllib
from math import ceil, isclose
from pathlib import Path

from cities.Baghdad import airport_supply, airport_service
from cities.Baghdad.airport_single_line import single_line_svg
from cities.Baghdad.engineering.mechanical.vehicle.power_interface import load_bus
from engineering.outline.baghdad_system import _id
from engineering.railway_completion import evidence
from engineering.railway_completion.evidence import number, parse

# These are explicit perturbations of the priced study for a buyer to investigate.
# They are neither probabilities nor mandatory clearance limits.
CASES = {
    "published hot circuit": (1.0, 1.0, 1.0),
    "1% lower source": (0.99, 1.0, 1.0),
    "5% higher peak demand": (1.0, 1.0, 1.05),
    "5% additional hot resistance": (1.0, 1.05, 1.0),
    "combined sensitivity": (0.99, 1.05, 1.05),
}

PATH = (
    "minimum_open_circuit_kv",
    "maximum_source_droop_ohm",
    "maximum_outward_ohm_per_km",
    "maximum_return_ohm_per_km",
    "maximum_additional_joint_and_shoe_ohm",
    "maximum_collector_demand_mw",
)
PROTECTION = (
    "maximum_healthy_current_ka",
    "pickup_min_ka",
    "pickup_max_ka",
    "minimum_sustained_fault_ka",
    "maximum_prospective_fault_ka",
    "rated_breaking_ka",
    "required_grading_ms",
    "maximum_cable_i2t_ka2s",
    "maximum_system_time_constant_ms",
    "rated_time_constant_ms",
    "maximum_recovery_voltage_kv",
    "rated_dc_voltage_kv",
)
BAND = ("from_ka", "through_ka", "primary_max_clear_ms", "backup_min_trip_ms", "backup_max_clear_ms")


def binding(opening):
    # Reuse all circuit, source, candidate and section-count checks used by the drawing.
    single_line_svg(opening)
    cfg = tomllib.loads((airport_supply.CITY / "system.toml").read_text())
    service = airport_service.build_service(cfg, opening["train"])
    f = opening["section_power"]
    expected = _id(
        {
            "bundle": opening["bundle"],
            "sources": opening["sources"],
            "service": service["evaluation_id"],
            "power": opening["power"]["evaluation_id"],
            "feeder": f["evaluation_id"],
        }
    )
    if f["service_id"] != _id(service) or opening["evaluation_id"] != expected:
        raise ValueError("Opening evaluation or bound train workings differ")
    return {
        "opening_candidate_id": opening["candidate_id"],
        "opening_evaluation_id": opening["evaluation_id"],
        "power_evaluation_id": opening["power"]["evaluation_id"],
        "feeder_design_id": opening["section_power"]["design_id"],
        "feeder_evaluation_id": opening["section_power"]["evaluation_id"],
    }


OPTIONS = ("priced_radial", "six_site_quotation", "six_site_parallel")
COMMON_HOT_OHM = 0.001
PRICE_ITEMS = (
    "site_conversions_including_civil_and_grid_tie_ins",
    "positive_and_return_circuit_including_bonds",
    "outgoing_breakers_and_midpoint_ties",
    "power_controls_earthing_and_commissioning",
)


def topology(opening, option):
    if option not in OPTIONS:
        raise ValueError("Unknown Airport propulsion supply option")
    feeder = opening["section_power"]
    selected = feeder["selected"]
    if option == "priced_radial":
        sites = selected["site_chainage_km"]
        geometry = {
            k: selected[k]
            for k in (
                "feed_system",
                "route_km",
                "source_kv",
                "droop_ohm",
                "outward_ohm_per_km",
                "return_ohm_per_km",
            )
        }
    else:
        alt = feeder["station_sited_quote_variant"]
        sites = alt["site_chainage_km"]
        geometry = {
            "feed_system": selected["feed_system"],
            "route_km": selected["route_km"],
            "source_kv": selected["source_kv"],
            "droop_ohm": alt["nominal_source_droop_ohm"],
            **{k: alt["nominal_" + k] for k in ("outward_ohm_per_km", "return_ohm_per_km")},
        }
        if len(sites) != len(opening["bundle"]["stops"]) or len(sites) != alt["grid_sites"]:
            raise ValueError("Six-site return must address one group at each stop")
    if option == "six_site_parallel":
        geometry.update(
            parallel_positive_paths=2,
            parallel_return_paths=2,
            maximum_shared_hot_contact_and_joint_ohm=COMMON_HOT_OHM,
            switching="Two outbound branches downstream of each zone breaker. Both terminate inside the same section.",
        )
    count = len(sites)
    geometry.update(grid_sites=count, site_chainage_km=sites)
    design = _id(geometry)
    if option == "priced_radial" and design != selected["design_id"]:
        raise ValueError("Priced radial circuit identity differs")
    return {
        "option": option,
        "design_id": design,
        "design": geometry,
        "rectifier_sites": count,
        "outgoing_circuits": 4 * (count - 1),
        "midpoint_ties": 2 * (count - 1),
        "protected_track_km": feeder["procurement"]["protected_track_km"],
    }


def return_form(opening, option="priced_radial"):
    return {
        "schema": "baghdad-feeder-return/1",
        "binding": binding(opening),
        "scope": topology(opening, option),
        "record_kind": None,
        "document_revision": None,
        "coverage": None,
        "path": {key: None for key in PATH},
        "protection": {**dict.fromkeys(PROTECTION), "bands": []},
        "price_2026_usd": {
            "installed_direct": dict.fromkeys(PRICE_ITEMS),
            "annual_upkeep": None,
            "renewals_by_year": None,
        },
    }


def _price(value):
    # A completed empty renewal schedule or zero-cost scope requires an explicit return.
    if set(value) != {"installed_direct", "annual_upkeep", "renewals_by_year"} or set(
        value["installed_direct"]
    ) != set(PRICE_ITEMS):
        raise ValueError("Return the matched installed, maintenance and renewal scopes")
    direct = {k: _positive(v, k, True) for k, v in value["installed_direct"].items() if v is not None}
    annual = value["annual_upkeep"]
    if annual is not None:
        annual = _positive(annual, "annual_upkeep", True)
    renewal = value["renewals_by_year"]
    if renewal is not None:
        if not isinstance(renewal, dict) or not set(renewal) <= {str(i) for i in range(1, 31)}:
            raise ValueError("Return year 1 to 30 for renewals in constant 2026 USD")
        renewal = {int(k): _positive(v, k, True) for k, v in renewal.items()}
    installed = sum(direct.values()) if len(direct) == len(PRICE_ITEMS) else None
    pv = None
    if installed is not None and annual is not None and renewal is not None:
        pv = installed + sum((annual + renewal.get(year, 0)) / 1.04**year for year in range(1, 31))
    return {
        "installed_direct_usd": installed,
        "annual_upkeep_usd": annual,
        "renewals_by_year_usd": renewal,
        "priced_scope_pv_30y_usd": pv,
        "missing_installed_scopes": sorted(set(PRICE_ITEMS) - direct.keys()),
    }


def compare_returns(opening, radial_return, six_site_return):
    """Compare the same installed power scopes at the same 30-year, 4% real basis."""
    records = []
    other = six_site_return["scope"]["option"]
    if other not in ("six_site_quotation", "six_site_parallel"):
        raise ValueError("Compare the priced parent with one station-sited design")
    for expected, form in (("priced_radial", radial_return), (other, six_site_return)):
        if form["scope"] != topology(opening, expected):
            raise ValueError("Require a return for each correctly identified circuit")
        records.append(evaluate(opening, form)["return"])
    prices = [r["price"] for r in records]
    delta = {}
    for k in ("installed_direct_usd", "annual_upkeep_usd", "priced_scope_pv_30y_usd"):
        delta[k] = None if any(p[k] is None for p in prices) else prices[1][k] - prices[0][k]
    return {
        "opening_candidate_id": opening["candidate_id"],
        "returns": [r["return_id"] for r in records],
        "six_site_minus_priced_radial": delta,
        "price_basis": "2026 USD, 30 years, 4% real",
        "procurement_award": False,
    }


def voltage(source, resistance, load, floor):
    result = load_bus(source, resistance, load)
    v, i = result if result else (None, None)
    return {
        "source_kv": source,
        "loop_ohm": resistance,
        "collector_load_mw": load,
        "collector_kv": v,
        "current_ka": i,
        "margin_v": None if v is None else (v - floor) * 1000,
        "physical_screen": (
            "no equilibrium" if v is None else "above or at floor" if v >= floor else "below floor"
        ),
    }


def sensitivities(source, hot_r, load, floor):
    rows = {name: voltage(source * e, hot_r * r, load * p, floor) for name, (e, r, p) in CASES.items()}
    row = rows["published hot circuit"]
    return {
        "cases": rows,
        "additional_loop_resistance_to_floor_milliohm": 1000 * (floor * (source - floor) / load - hot_r),
        "additional_load_to_floor_kw": 1000 * (floor * (source - floor) / hot_r - load),
        "source_dip_to_floor_v": 1000 * (source - floor - hot_r * load / floor),
        "maximum_hot_loop_ohm_in_combined_sensitivity_before_5pct_increase": floor
        * (source * 0.99 - floor)
        / (load * 1.05 * 1.05),
        "published_hot_margin_v": row["margin_v"],
    }


def _positive(value, key, allow_zero=False):
    value = number(value, key, nonnegative=True)
    if not allow_zero and value == 0:
        raise ValueError(f"{key} must be positive")
    return value


def protection_screen(values, load_ka):
    """Worst-case interval grading. Currents across each band share a primary and backup path."""
    if set(values) != set(PROTECTION) | {"bands"}:
        raise ValueError("Return every protection field with its declared units")
    missing = [key for key in PROTECTION if values[key] is None]
    required = {key: _positive(values[key], key) for key in PROTECTION if values[key] is not None}
    bands = values["bands"]
    if not isinstance(bands, list) or len(bands) > 256:
        raise ValueError("Return up to 256 consecutive tolerance bands")
    if not bands:
        missing.append("signed manufacturer time-current tolerance bands")
    parsed = []
    for item in bands:
        if set(item) != set(BAND):
            raise ValueError("Each band needs inclusive current limits and three timing bounds")
        b = {k: _positive(item[k], k) for k in BAND}
        if (
            b["from_ka"] >= b["through_ka"]
            or b["backup_min_trip_ms"] > b["backup_max_clear_ms"]
            or (parsed and b["from_ka"] != parsed[-1]["through_ka"])
        ):
            raise ValueError("Time-current bands must adjoin and have ordered current and time limits")
        parsed.append(b)
    if missing:
        return {"status": "awaiting protection return", "missing": missing, "checks": {}, "bands": []}
    p = required
    if (
        p["pickup_min_ka"] > p["pickup_max_ka"]
        or p["minimum_sustained_fault_ka"] > p["maximum_prospective_fault_ka"]
    ):
        raise ValueError("Returned pickup and fault bounds are reversed")
    lo, hi = p["minimum_sustained_fault_ka"], p["maximum_prospective_fault_ka"]
    checks = {
        "healthy_envelope_covers_declared_duty": load_ka is not None
        and p["maximum_healthy_current_ka"] >= load_ka,
        "load_below_lowest_pickup": p["maximum_healthy_current_ka"] < p["pickup_min_ka"],
        "least_fault_above_highest_pickup": lo > p["pickup_max_ka"],
        "breaking_rating": hi <= p["rated_breaking_ka"],
        "time_constant_within_rating": p["maximum_system_time_constant_ms"] <= p["rated_time_constant_ms"],
        "recovery_voltage_within_rating": p["maximum_recovery_voltage_kv"] <= p["rated_dc_voltage_kv"],
        "curves_span_entire_fault_range": parsed[0]["from_ka"] <= lo and parsed[-1]["through_ka"] >= hi,
    }
    rows = []
    for b in parsed:
        if b["through_ka"] < lo or b["from_ka"] > hi:
            continue
        # A conservative rectangular upper current bound through primary clearing and through backup clearing.
        peak = min(hi, b["through_ka"])
        separation = b["backup_min_trip_ms"] - b["primary_max_clear_ms"]
        cable = peak**2 * max(b["primary_max_clear_ms"], b["backup_max_clear_ms"]) / 1000
        rows.append(
            {
                **b,
                "grading_margin_ms": separation - p["required_grading_ms"],
                "cable_i2t_bound_ka2s": cable,
                "cable_margin_ka2s": p["maximum_cable_i2t_ka2s"] - cable,
            }
        )
    checks["all_bands_selective"] = bool(rows) and all(row["grading_margin_ms"] >= 0 for row in rows)
    checks["all_bands_withstand_backup_clearing"] = bool(rows) and all(
        row["cable_margin_ka2s"] >= 0 for row in rows
    )
    return {
        "status": "returned envelope passes" if all(checks.values()) else "returned envelope fails",
        "missing": [],
        "checks": checks,
        "bands": rows,
    }


def _returned(form, basis, scope, distance, load, floor):
    if (
        set(form)
        != {
            "schema",
            "binding",
            "record_kind",
            "document_revision",
            "coverage",
            "path",
            "protection",
            "scope",
            "price_2026_usd",
        }
        or form["schema"] != "baghdad-feeder-return/1"
        or form["binding"] != basis
        or form["scope"] != scope
    ):
        raise ValueError("Feeder return must identify this opening, power evaluation and circuit revision")
    path = form["path"]
    if set(path) != set(PATH):
        raise ValueError("Return the complete path field set and explicit nulls for missing values")
    filled = [key for key in PATH if path[key] is not None]
    has_values = (
        filled
        or any(form["protection"].get(k) is not None for k in PROTECTION)
        or form["protection"].get("bands")
    )
    price = _price(form["price_2026_usd"])
    has_values = (
        has_values
        or len(price["missing_installed_scopes"]) != len(PRICE_ITEMS)
        or price["annual_upkeep_usd"] is not None
        or price["renewals_by_year_usd"] is not None
    )
    if has_values and (
        form["record_kind"] not in ("supplier-envelope", "engineering-sensitivity")
        or any(not isinstance(form[k], str) or not form[k].strip() for k in ("document_revision", "coverage"))
    ):
        raise ValueError(
            "Identify envelope type, source revision, covered circuits and operating configurations"
        )
    vals = {k: _positive(path[k], k, k == "maximum_additional_joint_and_shoe_ohm") for k in filled}
    operating = None
    if len(filled) == len(PATH):
        if vals["maximum_collector_demand_mw"] < load:
            raise ValueError("Returned demand excludes part of the two-train outage duty")
        resistance = (
            vals["maximum_source_droop_ohm"]
            + vals["maximum_additional_joint_and_shoe_ohm"]
            + distance * (vals["maximum_outward_ohm_per_km"] + vals["maximum_return_ohm_per_km"])
        )
        operating = voltage(
            vals["minimum_open_circuit_kv"], resistance, vals["maximum_collector_demand_mw"], floor
        )
    grading = protection_screen(form["protection"], operating["current_ka"] if operating else None)
    return {
        "return_id": _id(form),
        "record_kind": form["record_kind"],
        "document_revision": form["document_revision"],
        "coverage": form["coverage"],
        "missing_path_inputs": [k for k in PATH if k not in filled],
        "operating_case": operating,
        "scope": scope,
        "protection": grading,
        "price": price,
        "authenticated": False,
    }


def _paired_replay(sites, windows, source, floor, droop, resistance_per_km, increment, background):
    """Use the timetable's nine-decimal km grid for inclusive source/footprint tests."""
    units_per_km = 10**9
    site_units = [round(km * units_per_km) for km in sites]
    # On this station-sited design all midpoints are on the same grid. Arithmetic
    # on these integer coordinates gives exact endpoints in the radial solver.
    if any((a + b) % 2 for a, b in zip(site_units, site_units[1:])):
        raise ValueError("Station midpoint falls between registered footprint coordinates")
    window_units = {
        tuple((round(lo * units_per_km), round(hi * units_per_km)) for lo, hi in group): window
        for group, window in windows.items()
    }
    outages = airport_supply._replay(
        site_units,
        window_units,
        source,
        floor,
        droop,
        resistance_per_km / units_per_km,
        increment,
        background,
    )
    for outage in outages:
        outage["worst"]["furthest_fed_km"] /= units_per_km
    return outages


def parallel_option(opening, service, distance, load, floor):
    """Replay a two-path purchase enquiry under the same timetable and combined envelope."""
    f = opening["section_power"]
    scope = topology(opening, "six_site_parallel")
    design = scope["design"]
    a = f["assumptions"]
    if service is None:
        cfg = tomllib.loads((airport_supply.CITY / "system.toml").read_text())
        service = airport_service.build_service(cfg, opening["train"])
    if _id(service) != f["service_id"]:
        raise ValueError("Parallel feeder replay requires the exact service used by the priced parent")
    windows, pulses = airport_supply._pulse_windows(
        service, design["route_km"], a["pulse_seconds"], a["speed_cap_m_s"]
    )
    hot = f["station_sited_quote_variant"]["impedance_sensitivity_multiplier"]
    source_r = hot * design["droop_ohm"]
    single_loop = hot * (design["outward_ohm_per_km"] + design["return_ohm_per_km"])
    droop = source_r + COMMON_HOT_OHM
    source = design["source_kv"]
    # R_parallel <= R_branch_bound/2 when BOTH branches satisfy that bound.
    # The heat/rating enquiry never assumes that the current divides in half.
    path = droop + distance * single_loop / 2
    envelope = sensitivities(source, path, load, floor)
    e, r, p = CASES["combined sensitivity"]
    cruise = a["uphill_cruise_bound_mw_per_nonaccelerating_set"]
    increment = a["train_traction_rating_mw"] - cruise
    base = load - 2 * increment
    outages = _paired_replay(
        design["site_chainage_km"],
        windows,
        e * source,
        floor,
        r * droop,
        r * single_loop / 2,
        p * increment,
        p * base,
    )
    stress = envelope["cases"]["combined sensitivity"]
    rows = [i["worst"] for i in outages] + [stress]
    if any(row["collector_kv"] is None for row in rows):
        raise ValueError("Outside stable parallel-feed sizing domain")
    i_peak = max(row["current_ka"] for row in rows)
    rms = max(row["site_rms_ka_upper"] for row in outages)
    total_track = scope["protected_track_km"]
    return {
        "scope": scope,
        "operating_envelopes": envelope,
        "outages": outages,
        "replayed_pulses": pulses,
        "minimum_combined_collector_kv": min(row["collector_kv"] for row in rows),
        "site_peak_current_ka": i_peak,
        "site_output_rating_request_mw_at_nominal_voltage": i_peak * source,
        "scheduled_site_rms_current_upper_ka": rms,
        "single_path_lost_with_site_out_combined": voltage(
            e * source, r * (droop + distance * single_loop), p * load, floor
        ),
        "quantity_enquiry": {
            "rectifier_and_transformer_groups": scope["rectifier_sites"],
            "main_outgoing_breakers": scope["outgoing_circuits"],
            "track_midpoint_ties": scope["midpoint_ties"],
            "positive_longitudinal_path_km": 2 * total_track,
            "return_longitudinal_path_km": 2 * total_track,
            "positive_branch_disconnect_points": 2 * scope["outgoing_circuits"],
            "return_branch_test_points": 2 * scope["outgoing_circuits"],
            "peak_ka_each_branch_with_unproved_sharing": i_peak,
            "scheduled_rms_ka_each_branch_with_unproved_sharing": rms,
            "source_nominal_droop_max_ohm": design["droop_ohm"],
            "hot_common_shoe_and_nonparallel_joint_allowance_ohm": COMMON_HOT_OHM,
            "required_parallel_branch_hot_ohm_per_km": {
                "outward": hot * design["outward_ohm_per_km"],
                "return": hot * design["return_ohm_per_km"],
            },
        },
        "installed_direct_2026_usd": None,
        "automatic_selection": False,
        "physical_accepted": False,
    }


def evaluate(opening, supplier_return=None, *, service=None):
    basis = binding(opening)
    feeder = opening["section_power"]
    selected, alt = feeder["selected"], feeder["station_sited_quote_variant"]
    e, floor = selected["source_kv"], feeder["floor_kv"]
    load = feeder["assumptions"]["design_two_pulse_load_plus_all_working_auxiliaries_mw"]
    distance = max(b - a for a, b in zip(selected["site_chainage_km"], selected["site_chainage_km"][1:]))
    hot_r = selected["impedance_sensitivity_multiplier"] * (
        selected["droop_ohm"] + distance * (selected["outward_ohm_per_km"] + selected["return_ohm_per_km"])
    )
    alt_distance = max(b - a for a, b in zip(alt["site_chainage_km"], alt["site_chainage_km"][1:]))
    alt_r = alt["impedance_sensitivity_multiplier"] * (
        alt["nominal_source_droop_ohm"]
        + alt_distance * (alt["nominal_outward_ohm_per_km"] + alt["nominal_return_ohm_per_km"])
    )
    main, quote = (sensitivities(e, r, load, floor) for r in (hot_r, alt_r))
    for result, record in ((main, selected), (quote, alt)):
        stress = next(
            r
            for r in record["independent_cases"]
            if r["one_site_unavailable"] and r["accelerating_trains"] == 2
        )
        if not isclose(
            result["cases"]["published hot circuit"]["collector_kv"], stress["collector_kv"], abs_tol=1e-9
        ):
            raise ValueError("Outage case differs from the bound collector calculation")
    # At the floor the elementary constant-power equilibrium sets an upper bound on total loop R.
    # Solve source count for the same conductor under the combined sensitivity, without transferring its price.
    limit = main["maximum_hot_loop_ohm_in_combined_sensitivity_before_5pct_increase"]
    factor = selected["impedance_sensitivity_multiplier"]
    spacing = (limit / factor - selected["droop_ohm"]) / (
        selected["outward_ohm_per_km"] + selected["return_ohm_per_km"]
    )
    n = None if spacing <= 0 else max(3, 1 + ceil(selected["route_km"] / spacing))
    form = return_form(opening) if supplier_return is None else supplier_return
    scope = topology(opening, form["scope"]["option"])
    return_distance = distance if scope["option"] == "priced_radial" else alt_distance
    parallel = parallel_option(opening, service, alt_distance, load, floor)
    report = {
        "schema": "baghdad-feeder-commissioning/1",
        "binding": basis,
        "source_sha256": {
            "feeder.py": sha256(Path(__file__).read_bytes()).hexdigest(),
            "airport_supply.py": sha256(Path(airport_supply.__file__).read_bytes()).hexdigest(),
            "engineering/railway_completion/evidence.py": sha256(
                Path(evidence.__file__).read_bytes()
            ).hexdigest(),
        },
        "floor_kv": floor,
        "single_site_outage_distance_km": distance,
        "priced_radial": main,
        "six_site_quotation": quote,
        "six_site_installed_price_usd": alt["installed_price_usd"],
        "six_site_quotation_scope": topology(opening, "six_site_quotation"),
        "six_site_combined_sensitivity_target": {
            "maximum_total_hot_loop_ohm": limit,
            "maximum_hot_conductor_and_return_ohm_per_km_if_source_droop_unchanged": (
                limit - alt["nominal_source_droop_ohm"] * alt["impedance_sensitivity_multiplier"]
            )
            / alt_distance,
            "worst_restored_path_km": alt_distance,
        },
        "same_impedance_site_count_bound": {
            "maximum_spacing_km": max(0, spacing),
            "sites": n,
            "outgoing_circuits": 4 * (n - 1) if n else None,
            "midpoint_ties": 2 * (n - 1) if n else None,
            "purpose": "Necessary uniform-spacing bound under the combined sensitivity. Outage replay, site availability and costing are open.",
        },
        "parallel_quotation": parallel,
        "equipment": feeder["procurement"],
        "return": _returned(form, basis, scope, return_distance, load, floor),
        "physical_accepted": False,
        "energisation_authorised": False,
    }
    report["evaluation_id"] = _id(report)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("opening", type=Path, help="opening.json from the candidate dossier")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--form", choices=OPTIONS, nargs="?", const="priced_radial")
    mode.add_argument("--return-file", type=Path)
    mode.add_argument("--compare", nargs=2, type=Path, metavar=("PRICED_RADIAL", "STATION_SITED"))
    args = parser.parse_args()
    opening = parse(args.opening.read_bytes())
    record = parse(args.return_file.read_bytes()) if args.return_file else None
    if args.compare:
        value = compare_returns(opening, *(parse(p.read_bytes()) for p in args.compare))
    else:
        value = return_form(opening, args.form) if args.form else evaluate(opening, record)
    print(json.dumps(value, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
