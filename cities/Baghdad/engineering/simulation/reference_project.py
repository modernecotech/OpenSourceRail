"""Reconcile the selected Airport desktop demonstrator before exposing its evidence."""

import argparse
from math import isclose, isfinite
import json
from pathlib import Path

from engineering.performance import disk_reservation

from ..controls import airport_atp_replay
from . import airport_alignment, production, scenario, vehicle_audit


HERE = Path(__file__).resolve().parent
ROOT = scenario.ROOT
SITE = HERE / "site-study.json"
TRACK = HERE / "site-study.geojson"
REPLAY = HERE.parent / "controls/airport-atp-replay.json"
REFERENCE = HERE / "project-reference.json"
REPORT = HERE / "PROJECT-REFERENCE.md"
LAYOUT = "paired6"
REQUIRED_CASES = {"normal", "hot", "site_out", "path_out", "combined"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def only(records, **fields):
    matches = [row for row in records if all(row.get(key) == val for key, val in fields.items())]
    require(len(matches) == 1, f"Expected one scope row for {fields}")
    return matches[0]


def check_station_order(stops, points):
    index = -1
    for stop in stops:
        try:
            index = points.index(stop["longitude_latitude"], index + 1)
        except ValueError as error:
            raise ValueError("Stop order disagrees with the centreline") from error
        require(isclose(airport_alignment.length_km(points[:index + 1]), stop["chainage_km"], abs_tol=1e-8),
                "Stop chainage disagrees with the centreline")


def reconcile(site, track):
    """Validate handoffs independently of the site's serialized digest."""
    require(site["schema"] == "osr-baghdad-airport-gis-study/1" and site["physical_acceptance"] is False,
            "Expected a provisional Airport GIS and cash study")
    alignment = site["alignment_id"]
    rail = site["stops"]
    centreline = only(track["features"], properties={"kind": "study centreline"})["geometry"]
    require(track["alignment_id"] == alignment and centreline["type"] == "LineString"
            and len(rail) >= 2, "GIS layer belongs to a different alignment")
    points = centreline["coordinates"]
    chainages = [stop["chainage_km"] for stop in rail]
    route_km = site["route_km"]
    require(isfinite(route_km) and route_km > 0
            and isclose(airport_alignment.length_km(points), route_km, abs_tol=1e-8)
            and chainages[0] == 0 and isclose(chainages[-1], route_km, abs_tol=1e-8)
            and all(a < b for a, b in zip(chainages, chainages[1:]))
            and points[0] == rail[0]["longitude_latitude"] and points[-1] == rail[-1]["longitude_latitude"],
            "Stop order, route length and mapped geometry disagree")
    check_station_order(rail, points)

    service = site["working_day"]
    day = service["normal_by_layout"][LAYOUT]
    selection = site["design_screen"][LAYOUT]
    assemblies = selection["assemblies"]
    mass = site["vehicle_loaded_mass_kg"]
    require(set(mass) == {"low", "central", "high"}
            and 0 < mass["low"] <= mass["central"] <= mass["high"]
            and day["loaded_train_kg"] == mass["central"] and 0 < day["tare_train_kg"] < mass["central"],
            "Operating mass does not match the vehicle evidence")
    require(assemblies["alignment"] == day["feeder_physical"]["alignment_id"] == alignment
            and day["candidate_id"] == assemblies["feeder"]
            and day["topology"] == day["feeder_physical"]["feeder"]["name"] == LAYOUT
            and day["condition"] == "normal", "Operating and alignment candidate IDs disagree")
    feeder = day["feeder_physical"]["feeder"]
    require(day["site_chainages_m"] == feeder["sites"] and len(feeder["sites"]) == len(rail) == 6
            and all(isclose(site_m, km * 1000, abs_tol=1e-6)
                    for site_m, km in zip(feeder["sites"], chainages, strict=True)),
            "Feeder chainages or units disagree with the station-fed layout")

    cases = [case for case in service["all_cases"] if case["topology"] == LAYOUT]
    nominal = only(cases, condition="normal")
    require(len(cases) == len(REQUIRED_CASES) and {case["condition"] for case in cases} == REQUIRED_CASES
            and all(case["booked"] == day["booked"] and 0 <= case["completed"] <= case["booked"] for case in cases)
            and all(nominal[key] == day[key] for key in ("completed", "minimum_v", "numerical_valid", "failed_screens")),
            "The priced normal service and duty table do not reconcile")

    cash = site["cash"]
    price = cash["layouts"][LAYOUT]
    civil = site["civil"]
    # Civil uses the horizontal route and grade profile separately. The
    # operating adapter hashes the combined alignment.
    require(cash["alignment_id"] == price["alignment_id"] == alignment
            and civil["alignment_id"] == site["horizontal_parent_id"]
            and civil["site_profile_id"] == site["site_profile_id"]
            and cash["source_audit_evaluation_id"] == site["audit_evaluation_id"]
            and price["feeder_physical_id"] == day["feeder_physical_id"]
            and civil["civil_physical_id"] == assemblies["civil"]
            and price["operating_screen"] == selection["operating_screen"],
            "Civil, production or cost belongs to a different project evaluation")

    lots = price["lots"]
    opening = [row for row in lots if row["group"] == "opening-direct"]
    require(len({row["lot_id"] for row in lots}) == len(lots), "Duplicate cash lot")
    stock = site["civil_stock"]
    standard = only(opening, lot_id="audited-standard-viaduct")
    standard_placements = standard["quantity"]
    closure_lot = only(opening, lot_id="gis-end-closure-allowance")
    closure = closure_lot["quantity"]
    sites = len(day["site_chainages_m"])
    require(closure_lot["reference_site_cost_id"] == civil["evaluation_id"]
            and standard["current_unit"] == "standard placements"
            and closure_lot["source_unit"] == "double-track end closure"
            and stock["placements"] == standard_placements + 2 * closure
            and stock["supports"] == civil["quantities"]["physical_supports"]
            and civil["quantities"]["standard_supports"] + closure == stock["supports"]
            and stock["bearings"] == 4 * stock["placements"],
            "Standard civil placements and separately priced closure disagree")
    quantities = {"fleet": (day["fleet"], "trainsets"), "stations": (len(rail), "station sites"),
                  "track": (2 * route_km, "track-km"),
                  "revised-feeder-package": (sites, "site-count with attached line scope")}
    for name, (expected, unit) in quantities.items():
        lot = only(opening, lot_id=name)
        require(lot.get("current_unit", lot.get("source_unit")) == unit
                and isclose(lot["quantity"], expected, abs_tol=1e-8), f"{name} price quantity or unit differs")

    for lot in opening:
        scope = (lot.get("supplier_scope") or {}).get("context")
        if scope:
            require(scope["alignment_id"] == alignment and scope["vehicle_candidate_id"] == assemblies["train"]
                    and scope["motion_candidate_id"] == day["candidate_id"]
                    and scope["motion_evaluation_id"] == day["evaluation_id"]
                    and scope["civil_row_id"] == stock["audit_row_id"]
                    and scope["civil_physical_id"] == assemblies["civil"], f"Wrong candidate in lot {lot['lot_id']}")
        if "reference_site_cost_id" in lot:
            require(lot["reference_site_cost_id"] == civil["evaluation_id"], "Wrong GIS unit rate source")

    operations = price["operation_basis"]
    priced = [lot for lot in lots if lot["usd"] is not None]
    cash_replay = production.cash_profile(priced, price["cash"]["service_start_year"],
                                          operations["annual_paid_journeys_proxy"],
                                          operations["net_usd_per_paid_journey"], False)["profiles"]
    money_fields = ("capital_usd", "annual_opex_usd", "priced_30y_pv_usd")
    for case, values in cash_replay.items():
        require(all(isclose(price["cash"]["profiles"][case][name], values[name], abs_tol=.01, rel_tol=0)
                    for name in money_fields), f"{case} cash totals do not match the priced lots")
    return {
        "physical_candidate_id": selection["physical_candidate_id"],
        "assemblies": assemblies,
        "horizontal_parent_id": site["horizontal_parent_id"],
        "evaluations": {
            "site": site["evaluation_id"], "audit": site["audit_evaluation_id"],
            "rail_profile": site["site_profile_id"], "vehicle": site["vehicle_evaluation_id"],
            "normal_motion": day["evaluation_id"], "site_civil": civil["evaluation_id"],
            "production": price["production_evaluation_id"], "site_cash": cash["site_cash_id"],
        },
        "service": {"route_km": route_km, "stops": len(rail), "headway_min": service["headway_min"],
                    "dwell_s": service["dwell_s"], "trainsets": day["fleet"],
                    "loaded_train_kg": mass, "cases": cases,
                    "operating_screen": selection["operating_screen"]},
        "civil": {"family": stock["label"], "standard_placements": standard_placements,
                  "double_track_closures": closure, "support_positions": stock["supports"],
                  "bearing_allowance": stock["bearings"]},
        "cost": {**{name: cash_replay["base"][name] for name in money_fields},
                 "basis": cash["price_basis"], "scope_omissions": price["scope_omissions"],
                 "remaining_unpriced_lots": price["remaining_unpriced_lots"]},
        "decision": {"functional_screen": selection["functional_screen"],
                     "supplier_and_utility_checks": selection["supplier_and_utility_checks"],
                     "investment_rank": selection["investment_rank"],
                     "qualification": selection["qualification"], "physical_acceptance": False},
    }


def control_evidence(project, site, replay):
    expected = {
        "reference_candidate_id": project["physical_candidate_id"],
        "alignment_id": project["assemblies"]["alignment"],
        "alignment_record_id": site["alignment_record_id"],
        "vehicle_candidate_id": project["assemblies"]["train"],
        "vehicle_evaluation_id": project["evaluations"]["vehicle"],
        "site_evaluation_id": project["evaluations"]["site"],
    }
    require(replay["schema"] == "osr-baghdad-airport-atp-replay/1"
            and all(replay.get(key) == value for key, value in expected.items())
            and replay["physical_acceptance"] is False
            and replay["protection_layout_screen"] == "open", "ATP replay belongs to a different project or maturity")
    payload = {key: value for key, value in replay.items() if key != "evaluation_id"}
    require(replay["evaluation_id"] == scenario.sha(airport_atp_replay.encode(payload)),
            "ATP replay identity does not match its evidence")
    vehicle_sources = vehicle_audit.source_data()[-1]
    for name, checksum in replay["source_sha256"].items():
        if name in vehicle_sources:
            require(vehicle_sources[name] == checksum, f"Repeat the ATP replay after changing {name}")
            continue
        path = ROOT / name
        require(path.resolve().is_relative_to(ROOT) and scenario.sha(path.read_bytes()) == checksum,
                f"Repeat the ATP replay after changing {name}")
    return dict(status="candidate-bound software replay", evaluation_id=replay["evaluation_id"],
                protection_layout_screen=replay["protection_layout_screen"])


def evaluate():
    site = json.loads(SITE.read_bytes())
    require(site["evaluation_id"] == airport_alignment.identity({k: v for k, v in site.items() if k != "evaluation_id"}),
            "Published Airport GIS study identity does not match its data")
    for name, checksum in site["source_sha256"].items():
        require(Path(name).name == name and scenario.sha((HERE / name).read_bytes()) == checksum,
                f"Regenerate the Airport GIS study after changing {name}")
    reference = reconcile(site, json.loads(TRACK.read_bytes()))
    reference["schema"] = "osr-baghdad-airport-project-reference/1"
    reference["purpose"] = "Integration and verification of a provisional digital case"
    replay = json.loads(REPLAY.read_bytes())
    reference["controls"] = control_evidence(reference, site, replay)
    paths = (Path(__file__).resolve(), SITE, TRACK, REPLAY, Path(airport_alignment.__file__), Path(production.__file__))
    reference["source_sha256"] = {path.relative_to(ROOT).as_posix(): scenario.sha(path.read_bytes()) for path in paths}
    reference["reference_id"] = airport_alignment.identity(reference)
    return reference


def report(project):
    service, civil, cost = (project[key] for key in ("service", "civil", "cost"))
    functional = project["decision"]["functional_screen"]
    rows = [
        "# Baghdad Airport digital project reference", "",
        f"The integration reference is the {service['route_km']:.3f} km GIS-profiled Airport study with "
        f"{service['stops']} provisional stops, a {service['headway_min']}-minute service, "
        f"{service['dwell_s']:g} s dwell and six paired supply sites. The protected-conductor case "
        "carries six powered-wheel trainsets. This configuration is held for engineering qualification.", "",
        "| Interface | What reconciles | Evidence still needed |", "|---|---|---|",
        f"| Route and service | The grade profile, station order and timetable share one alignment. "
        f"The nominal operating mass is {service['loaded_train_kg']['central'] / 1000:.2f} t. | "
        "Survey the alignment, stop entrances, turnbacks and depot lead. Establish observed demand and dispatch limits. |",
        "| Traction and controls | Moving DC supplies the evaluated timetable. A source-bound Rust "
        "ATP replay exercises authority restrictions and the braking comparator. | Confirm approved protection "
        "limits, feeder duties, timing, localisation, interlocking, hardware isolation and measured braking. |",
        f"| Civil and stations | {civil['standard_placements']:,} standard placements and "
        f"{civil['double_track_closures']} separately priced double-track closure. "
        f"{civil['support_positions']:,} support positions and {civil['bearing_allowance']:,} bearings. | "
        "Check foundations, single-track loading, thermal effects, temporary deck loads and accessible evacuation. |",
        "| Production and maintenance | Costed lots carry the operating train and civil row IDs. | "
        "Reconcile the installed car and complete bogie, supplier assemblies, embedded harnesses, shop routes and upkeep. |",
        f"| Finance | Base priced scope is ${cost['capital_usd'] / 1e6:,.2f}m capital, "
        f"${cost['annual_opex_usd'] / 1e6:,.2f}m annual operation and "
        f"${cost['priced_30y_pv_usd'] / 1e6:,.2f}m in priced 30-year present value. | "
        "Price the excluded site, utility, owner and funding scope before comparing complete costs. |",
        "", "## Operating cases", "",
        "| Case | Trip completion | Minimum live collector voltage |",
        "|---|---:|---:|",
    ]
    for case in service["cases"]:
        volts = f"{case['minimum_v']:,.1f} V" if case["minimum_v"] is not None else "Open"
        rows.append(f"| {case['condition'].replace('_', ' ')} | {case['completed']} / {case['booked']} | {volts} |")
    rows.extend([
        "", "**Failed functional screens.** " + ", ".join(functional["failed"]) + ".",
        "", "**Open inputs.** " + ", ".join(functional["unknown"]) + ".",
        "", "**Electrical evidence due.** Utility connection, thermal ratings and protective coordination.", "",
        "Controls, cash and construction geometry each have their own evaluation identity. The horizontal "
        "supplier enquiry, 20 m deck-fed construction study and illustrated assembly ledger provide "
        "comparison evidence. Transfer of equipment, installed weights or prices requires a matched "
        "revision and recalculation.", "",
        "[GIS and cost study](GIS-SIMULATION.md) · [Candidate and evidence record](project-reference.json) · "
        "[Controls replay](../controls/AIRPORT-ATP.md) · [Engineering and release work](../../../../docs/ROADMAP.md)",
        "", "Reference `" + project["reference_id"] + "`.", "",
    ])
    return "\n".join(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_mutually_exclusive_group()
    actions.add_argument("--json", action="store_true")
    actions.add_argument("--publish", action="store_true")
    actions.add_argument("--check", action="store_true")
    args = parser.parse_args()
    project = evaluate()
    files = {REFERENCE: scenario.encode(project) + b"\n", REPORT: report(project).encode()}
    if args.publish:
        with disk_reservation(ROOT, HERE, "Airport digital project reference", 8 << 20):
            for path, content in files.items():
                scenario.write_atomic(path, content)
    if args.check:
        for path, content in files.items():
            require(path.read_bytes() == content, f"Refresh {path.name} for the current Airport inputs")
    if args.check or args.publish:
        print(project["reference_id"])
    else:
        print(files[REFERENCE if args.json else REPORT].decode(), end="")


if __name__ == "__main__":
    main()
