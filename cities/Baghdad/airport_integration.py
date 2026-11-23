"""Build the Baghdad opening operating plan and its offline supplier enquiry."""

import argparse
import csv
from hashlib import sha256
from html import escape
import io
import json
from math import isclose
from pathlib import Path
from tempfile import NamedTemporaryFile
import zipfile

from cities.Baghdad import airport_assembly, airport_finance, airport_opening, airport_service, airport_single_line, urban_opening
from cities.Baghdad.engineering.mechanical.compare_returns import verified_record
from cities.Baghdad.engineering.mechanical.vehicle import power_interface
from engineering.outline.baghdad_system import _id
from engineering.performance import check_disk_reservation, disk_reservation

CITY, ROOT = airport_opening.CITY, airport_opening.ROOT
GUIDE = CITY / "airport-integration.html"
ENQUIRY_RECORDS = [
    "engineering/mechanical/vehicle/braced-frame.obj",
    "engineering/mechanical/vehicle/frame-overview.svg",
    "engineering/mechanical/vehicle/stock.toml",
    "engineering/mechanical/vehicle/README.md",
    "engineering/mechanical/vehicle/cut-list.csv",
    "engineering/mechanical/bogie-interface.svg",
    "engineering/mechanical/civil/station-and-box.svg",
    "engineering/mechanical/civil/README.md",
    "engineering/mechanical/schedule.json",
    "engineering/mechanical/civil/section-results.json",
    "engineering/mechanical/vehicle/result.json",
    "engineering/mechanical/vehicle/SECTION-POWER.md",
    "engineering/mechanical/civil/concept.toml",
    "engineering/mechanical/quotation.toml",
    "engineering/controls/STATION-BENCH.md",
    "engineering/controls/README.md",
    "vehicle-layout.svg",
    "station-interface.svg",
    "engineering/mechanical/vehicle/section-trial.toml",
]


def build(mass_form=None, quote=None):
    inputs = airport_opening.opening_inputs()
    cfg, report, parent = inputs
    reference = airport_opening.calculate(inputs=inputs)
    service = airport_service.build_service(cfg, reference["train"])
    frame = verified_record(CITY / "engineering/mechanical/vehicle/result.json", ROOT)
    basis = {
        "first_network_id": parent["selected_candidate_id"],
        "braced_revision": frame["braced_revision_id"],
    }
    if frame["parent_train_id"] != basis["first_network_id"]:
        raise ValueError("The frame must belong to the declared first-network train")
    mass = power_interface.mass_return(
        mass_form if mass_form is not None else power_interface.mass_form(basis), basis
    )
    kg = mass["returned_crowd_train_kg"]
    if kg is not None:
        stock = frame["braced_body_and_two_bogie_cut_stock_kg_per_car"] * cfg["vehicle"]["cars_per_train"]
        if mass["weight_return"]["train_mass_groups"]["finished_body_bogie_frames"]["kg"] < stock:
            raise ValueError(
                "Finished structural group is lighter than the included trial stock; submit a revised geometry"
            )
    physical_mass_id = (
        _id({g: r["kg"] for g, r in mass["weight_return"]["train_mass_groups"].items()})
        if kg is not None
        else None
    )
    case = airport_opening.calculate(
        inputs=inputs,
        service=service,
        size_feeder=True,
        vehicle_revision=basis["braced_revision"],
        loaded_mass_t=None if kg is None else kg / 1000,
        mass_basis_id=physical_mass_id,
    )
    feeder = case["section_power"]
    regular = cfg["service_plan"]["departures_per_hour_direction"]
    finance = airport_finance.evaluate(case, cfg, regular, quote)
    assembly = airport_assembly.assembly(case, cfg, mass)
    if (
        case["bundle"]["feeder_design_id"] != feeder["design_id"]
        or feeder["power_evaluation_id"] != case["power"]["evaluation_id"]
        or case["bundle"]["active_sets"] != service["group"]["diagrammed_sets"]
        or not isclose(case["civil_load"]["candidate_crowd_train_t"], case["power"]["vehicle"]["mass_t"])
    ):
        raise ValueError("Inconsistent priced opening, load or power design")
    service_pass = service["terminal"]["schedule_screen_passed"]
    voltage_pass = feeder["selected"]["minimum_collector_kv"] >= feeder["floor_kv"]
    decision = {
        "purpose": "Standalone first-opening quotation and planning comparison",
        "physical_candidate_id": case["candidate_id"],
        "opening_evaluation_id": case["evaluation_id"],
        "service_evaluation_id": service["evaluation_id"],
        "supply_evaluation_id": feeder["evaluation_id"],
        "assembly_evaluation_id": assembly["evaluation_id"],
        "finance_evaluation_id": finance["evaluation_id"],
        "terminal_and_block_screen": service_pass,
        "voltage_screen": voltage_pass,
        "planning_configuration": service_pass and voltage_pass,
        "procurement_award": False,
        "physical_accepted": False,
        "operating_authorisation": False,
    }
    decision["selection_id"] = _id(decision)
    return {
        "opening": case,
        "service": service,
        "assembly": assembly,
        "finance": finance,
        "reference_finance": airport_finance.evaluate(reference, cfg, regular),
        "reference_train": reference["train"],
        "urban": urban_opening.urban_comparison(cfg, report),
        "selection": decision,
    }


def html(data, *, offline=False):
    c, service, finance = (data[key] for key in ("opening", "service", "finance"))
    supply = c["section_power"]
    central = finance["market_scenarios"]["central"]
    ref = data["reference_finance"]["market_scenarios"]["central"]
    urban = data["urban"]
    q = supply["procurement"]
    t = service["terminal"]
    alternative = supply["station_sited_quote_variant"]
    svg = "time-distance.svg" if offline else "airport-time-distance.svg"
    single_line = "traction-single-line.svg" if offline else "airport-traction-single-line.svg"
    alternative_voltage = (
        f'{alternative["minimum_collector_kv"]:.4f} kV'
        if alternative["minimum_collector_kv"] is not None
        else "a failed voltage screen"
    )
    links = (
        '<a href="assembly.json">Assembly and ERP drafts</a> · <a href="finance.json">Annual cash and renewals</a> · '
        '<a href="supplier-return.json">Price return</a> · <a href="mass-return.json">Weight return</a> · '
        '<a href="sources/engineering/controls/STATION-BENCH.md">Bench procedure</a>'
        if offline
        else '<a href="airport-dossier.zip" download>Download supplier dossier</a> · '
        '<a href="engineering/controls/STATION-BENCH.md">Bench procedure</a> · <a href="AIRPORT-OPENING.md">Original Airport budget</a>'
    )

    def money(a):
        return f"${a:,.1f}m"

    def cellrow(values):
        return "<tr>" + "".join(f"<td>{escape(str(x))}</td>" for x in values) + "</tr>"

    scenario_table = "".join(
        cellrow(
            [
                name.title(),
                money(row["capital_usd_m"]),
                money(row["annual_opex_usd_m"]),
                money(row["annual_fares_usd_m"]),
                money(row["annual_support_usd_m"]),
                money(row["priced_whole_life_30y_usd_m"]),
            ]
        )
        for name, row in finance["market_scenarios"].items()
    )
    power_table = "".join(
        cellrow(
            [
                "One site isolated" if r["one_site_unavailable"] else "All sites live",
                r["accelerating_trains"],
                f'{r["collector_kv"]:.4f} kV',
                f'{r["current_ka"]:.2f} kA',
            ]
        )
        for r in supply["selected"]["independent_cases"]
    )
    spans = c["civil"]
    return f"""<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Baghdad Airport opening · Operating plan and supplier enquiry</title>
<link rel="stylesheet" href="{'airport.css' if offline else 'airport-integration.css'}">
<main><header><p>Baghdad · 12 km elevated railway · Six stops</p><h1>Airport opening</h1>
<p>Three six-car trains provide a departure every 15 minutes in each direction. With three spares the fleet totals six sets.
The central construction allowance is <strong>{money(central["capital_usd_m"])}</strong>. The largest design change is the protected-conductor supply needed during a site outage.</p>
<nav>{links}</nav></header>
<section><h2>Operating plan</h2>
<p>{len(service["trips"])} passenger trips, {len(service["positioning_trips"])} empty mainline trips and {len(t["yard_moves"])} depot moves run each day.
One working platform face and one exclusive throat per terminus accommodate the booked movements.
The tightest resource has {min(v for v in t["minimum_margin_s_by_resource"].values() if v is not None)} seconds clear.
The timetable provides {central["peak_places_hour_direction"]:,.0f} places per hour per direction.
The common demand profile implies {central["peak_hour_all_boardings_assumed"]:,.0f} boardings across both directions in the busiest hour. Hourly and within-hour counts, station movements and route survey remain open.</p>
<a href="{svg}">Open full-day time–distance diagram</a></section>
<section><h2>Traction, braking and isolation</h2>
<p>The {c["power"]["vehicle"]["mass_t"]:.3f} t planning load requests {c["power"]["traction"]["dc_input_rating_request_mw"]:.3f} MW of traction.
The replay covers {supply["replay"]["pulses"]} pulses. The radial feed study adds a ten percent resistance sensitivity, one failed site, two accelerating trains and auxiliary and cruise loads.</p>
<table><thead><tr><th>Supply state</th><th>Accelerating sets</th><th>Collector voltage</th><th>Path current</th></tr></thead><tbody>{power_table}</tbody></table>
<p>The costed topology has {supply["grid_sites"]} supply sites, {q["dc_outgoing_breaker_circuits"]} outgoing circuits and {q["normally_open_track_ties"]} normally open ties.
The minimum collector voltage is {supply["selected"]["minimum_collector_kv"]:.4f} kV against a 1.350 kV planning floor.
A six-site alternative with lower source droop and lower conductor and return resistance gives {alternative_voltage} under the same sensitivity. It needs supplier prices for the heavier circuit and source equipment.
The feeder sizing envelope assigns uphill cruise demand to every nonaccelerating working set. The annual electricity budget uses the separate train-kilometre consumption model. Validate both with a metered timetable. A train stopping from 72 km/h on level track carries {supply["braking_reception"]["kinetic_kwh"]:.2f} kWh of kinetic energy. Demonstrate independent stopping, repeated heat rejection, isolation and evacuation with the line unreceptive.</p>
<a href="{single_line}">Open the traction supply single-line diagram</a></section>
<section><h2>Production and procurement</h2>
<p>The fleet requires {6*(c["bundle"]["active_sets"]+c["bundle"]["spares"])} cars. The body, bogie, door, brake, HVAC and controls schedule uses the braced frame revision and records missing supplier quantities.
The civil order carries {spans["beam_count"]:,} ten-metre track beams and {spans["pier_foundation_count"]:,} support positions. The construction and vehicle routes, first-article inspections, mass form and matched price form are in the dossier.</p>
<p>A separate 1.8 km demonstrator enquiry covers a car, powered bogies, guideway, station interface and controlled stopping trials. Site engineering, approved tolerances, installed weights and witnessed tests remain open for production release.</p></section>
<section><h2>Opening budget and public support</h2><table><thead><tr><th>2026 USD</th><th>Capital</th><th>Annual operation</th><th>Annual net fares</th><th>Annual support</th><th>30-year priced cost, PV</th></tr></thead><tbody>{scenario_table}</tbody></table>
<p>The central case assumes {central["paid_journeys_day"]:,.0f} paid journeys a day and {central["passenger_km_year"]/1e6:.2f}m passenger-km a year, held constant across the Airport offers.
It needs ${central["operating_support_usd_per_paid_journey"]:.2f} in operating support per paid journey. The original 21-set, three-site case priced {money(ref["capital_usd_m"])} and {money(ref["annual_support_usd_m"])} annual support. Its terminal and outage restrictions prevent an equal-feasibility cost ranking.</p>
<p>The funding illustration draws 20%, 45% and 35% over three years, opens the full corridor halfway through the third year and borrows 50% at 4% real over 20 years.
Cash covers 30 operating years with fares, debt service and timed renewals. The costed layout allows one section-equipment unit price per midpoint tie and 1% annually on incremental site and switching equipment in the central case. Prices need site and maintenance quotations, utility connections and a funded opening agreement.
The year sequence is relative to authorisation. Construction prices and ridership are scenarios.</p></section>
<section><h2>Urban opening comparison</h2>
<p>{escape(urban["group_name"])} is the urban survey comparator because its named stops connect with the most other proposed corridors. At four trains an hour on both lines, the common-rate urban scope is {money(urban["urban"]["capital_usd_m"])} against {money(urban["airport"]["capital_usd_m"])} for Airport, before corridor-specific feeder correction and site work.
At the same net fare it would need {urban["extra_paid_journeys_day_to_match_airport_operating_support"]:,.0f} additional paid journeys a day to match Airport operating support under those common assumptions. Survey directional demand, road diversion and local infrastructure before selecting an investment.</p></section>
<footer><p>Quotation basis · {escape(data["selection"]["selection_id"])}</p>
<p>Reproduce with <code>./osr design railway airport --check</code>. Export with <code>./osr design railway airport --packet build/airport-dossier.zip</code>.</p></footer></main></html>
"""


def encode(obj):
    return (json.dumps(obj, sort_keys=True, indent=2, allow_nan=False) + "\n").encode()


def make_packet(data):
    c = data["opening"]
    parts = data["assembly"]["parts"]
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=list(dict.fromkeys(k for row in parts for k in row)))
    writer.writeheader()
    writer.writerows(parts)
    members = {key + ".json": encode(value) for key, value in data.items()}
    members.update(
        {
            "START.html": html(data, offline=True).encode(),
            "airport.css": (CITY / "airport-integration.css").read_bytes(),
            "time-distance.svg": airport_service.time_distance_svg(data["service"]).encode(),
            "traction-single-line.svg": airport_single_line.single_line_svg(c).encode(),
            "bom.csv": output.getvalue().encode(),
            "supplier-return.json": encode(airport_finance.quote_form(c)),
            "mass-return.json": encode(
                power_interface.mass_form(data["assembly"]["mass_account"]["weight_return"]["basis"])
            ),
            "QUOTING.txt": QUOTING.encode(),
            "LICENSE.md": (ROOT / "LICENSE.md").read_bytes(),
        }
    )
    for filename in ENQUIRY_RECORDS:
        members["sources/" + filename] = (CITY / filename).read_bytes()
    members["manifest.json"] = encode(
        {
            "candidate_id": c["candidate_id"],
            "selection_id": data["selection"]["selection_id"],
            "sha256": {name: sha256(value).hexdigest() for name, value in members.items()},
        }
    )
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w") as archive:
        for name, value in sorted(members.items()):
            info = zipfile.ZipInfo(name)
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, value)
    return output.getvalue()


def same_packet(published, rebuilt):
    """Compare uncompressed member names, lengths and bytes across DEFLATE implementations."""
    with zipfile.ZipFile(published) as actual, zipfile.ZipFile(rebuilt) as expected:
        names = actual.namelist()
        if sorted(names) != sorted(expected.namelist()) or len(set(names)) != len(names):
            return False
        return all(
            actual.getinfo(info.filename).file_size == info.file_size
            and actual.read(info.filename) == expected.read(info.filename)
            for info in expected.infolist()
        )


QUOTING = """Open START.html for the proposed operating and construction quantities.
Use bom.csv, assembly.json, opening.json and the dimensioned source drawings together.
Reference drawings belong to the identified article and are supplied for first-article pricing.
Return a completed mass-return.json in kilograms for the whole six-car train, with an evidence reference for each group.
For a priced lot, replace its null entry in supplier-return.json with an object containing:
  review_reference (document, revision, scope review, currency and price basis);
  direct_price_usd_m (replacement installed direct price in millions of constant 2026 USD);
  annual_maintenance_change_usd_m (signed change relative to the quoted scope's existing upkeep);
  renewal_changes_usd_m (year-to-signed-change mapping against finance.json, e.g. {"15": 0.4}).
Leave unmatched lots null. Explicitly scope site ties, commissioning, spares and source impedance.
Line power covers railway-side grid sites and the conductor/switchgear line; offsite tie-ins stay in the local site ledger.
Run ./osr design railway airport --mass-return WEIGHTS.json --packet build/reweighed.zip for a changed mass.
Use the price form from that revision, then pass --supplier-return PRICES.json. The annual and capital adjustments appear in finance.json.
Independently confirm stated scope, evidence, compliance, installed mass and operating duty before purchasing.
"""


def write_atomic(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile(dir=path.parent, delete=False) as file:
        temp = Path(file.name)
        try:
            file.write(content)
            file.flush()
            temp.chmod(0o644)
            temp.replace(path)
        finally:
            temp.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--packet", type=Path)
    mode.add_argument("--json", action="store_true")
    mode.add_argument("--publish", action="store_true")
    mode.add_argument("--check", action="store_true")
    parser.add_argument("--mass-return", type=Path)
    parser.add_argument("--supplier-return", type=Path)
    args = parser.parse_args()
    if (args.publish or args.check) and (args.mass_return or args.supplier_return):
        parser.error("The published opening uses the registered planning inputs")
    data = build(
        *(json.loads(p.read_bytes()) if p else None for p in (args.mass_return, args.supplier_return))
    )
    if args.packet:
        with disk_reservation(ROOT, args.packet.parent, "Baghdad opening supplier packet", 8 << 20) as lease:
            content = make_packet(data)
            check_disk_reservation(lease)
            write_atomic(args.packet, content)
    elif args.json:
        print(encode(data).decode(), end="")
    elif args.publish or args.check:
        entries = {
            GUIDE: html(data).encode(),
            CITY / "airport-traction-single-line.svg": airport_single_line.single_line_svg(data["opening"]).encode(),
            CITY / "airport-time-distance.svg": airport_service.time_distance_svg(data["service"]).encode(),
        }
        entries[CITY / "airport-dossier.zip"] = make_packet(data)
        if args.check:
            for path, raw in entries.items():
                if path.suffix == ".zip":
                    matches = same_packet(path, io.BytesIO(raw))
                else:
                    matches = path.read_bytes() == raw
                if not matches:
                    raise SystemExit(f"Refresh {path.name}")
        else:
            with disk_reservation(ROOT, CITY, "Airport opening operating and cost sheets", 4 << 20) as lease:
                for path, raw in entries.items():
                    check_disk_reservation(lease)
                    write_atomic(path, raw)
    if not args.json:
        print(data["selection"]["selection_id"])


if __name__ == "__main__":
    main()
