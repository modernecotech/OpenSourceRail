"""Size the Airport factory resources against the issued opening bill of material."""

import argparse
import csv
from fractions import Fraction
from hashlib import sha256
import io
import json
from math import ceil
from pathlib import Path
import tomllib
from zipfile import ZipFile

from cities.Baghdad.airport_integration import write_atomic
from cities.Baghdad.engineering.prototype import sourcing_estimates
from engineering.outline.baghdad_system import _id
from engineering.performance import check_disk_reservation, disk_reservation

HERE = Path(__file__).resolve().parent
SHOPS = {
    "Vehicle works": "vehicle-factory/vehicle-resources.toml",
    "Civil yard and erection front": "infrastructure/civil-resources.toml",
    "Wayside electrical integrator": "infrastructure/electrical-resources.toml",
}
REPORT = "FACTORY-SPECIFICATION.md"
REGISTER = "factory-equipment.csv"
ROUTES = "factory-routes.json"


def number(value, *, zero=False):
    result = Fraction(str(value))
    if result < 0 or (not zero and result == 0):
        raise ValueError(f"Invalid capacity assumption {value}")
    return result


def drivers(bom):
    """Group repeated part names and expose mutually exclusive stock routes."""
    quantities = {}
    partitions = {"@rhs": 0, "@plate": 0, "jamb_liner": 0}
    for row in bom:
        item = row["item"]
        quantity = number(row["opening_quantity"], zero=True) if row["opening_quantity"] else None
        previous = quantities.get(item, 0)
        quantities[item] = None if quantity is None or previous is None else previous + quantity
        if row["scope"] == "cut material":
            if row["basis"].startswith("RHS "):
                family = "@rhs"
            elif item == "jamb_liner":
                family = item
            elif row["basis"].startswith(("plate ", "right triangle ")):
                family = "@plate"
            else:
                raise ValueError(f"No preparation route for {item}")
            if quantity is None:
                raise ValueError(f"Cut quantity missing for {item}")
            partitions[family] += quantity
    quantities["@rhs"] = partitions["@rhs"]
    quantities["@plate"] = partitions["@plate"]
    quantities["@saw"] = partitions["@rhs"] + partitions["jamb_liner"]
    quantities["@cut"] = quantities["@saw"] + partitions["@plate"]
    return quantities


def daily_capacity(resource, shop, quantities):
    days = number(shop["workdays"])
    hours = number(resource.get("hours_per_day", shop["hours_per_day"]))
    available = number(resource.get("utilisation", shop["utilisation"]))
    if hours > 24 or available > 1:
        raise ValueError(f"Invalid working day for {resource['id']}")
    minimum = resource["minimum"]
    if type(minimum) is not int or minimum < 0:
        raise ValueError(f"Invalid minimum for {resource['id']}")
    targets = shop.get("daily_targets", {})
    occupied = 0
    unknown = []
    for operation in resource.get("load", []):
        cycle = number(operation["hours"]) * number(operation.get("multiplier", 1))
        occupied += number(operation.get("setup_hours", 0), zero=True) / days
        for item in operation["items"]:
            quantity = quantities[item]
            if quantity is None:
                unknown.append(item)
            else:
                # A quoted peak is an additional capacity requirement. A low peak
                # cannot make the average programme demand disappear.
                rate = max(quantity / days, number(targets.get(item, 0), zero=True))
                occupied += rate * cycle
    lower = max(minimum, ceil(occupied / (hours * available)))
    no_basis = not resource.get("load") and minimum == 0
    return dict(required_units=None if unknown or no_basis else lower,
                minimum_units=lower if lower or not (unknown or no_basis) else None,
                unknown_demand=unknown, usable_hours_per_day=float(hours * available),
                known_resource_hours_per_day=round(float(occupied), 6))


def build(estimate=None, drawings=None):
    if estimate is None:
        estimate = sourcing_estimates.estimate_lots()
    lots = {r["lot_id"] for r in estimate["lots"]}
    names = ("opening-bom.csv", "opening.json", "civil-article.json")
    if drawings is None:
        with ZipFile(sourcing_estimates.PACKET) as z:
            drawings = {name: z.read(name) for name in (*names, "manifest.json")}
    manifest = json.loads(drawings["manifest.json"])
    members = {name: drawings[name] for name in names}
    digests = {name: sha256(raw).hexdigest() for name, raw in members.items()}
    if (any(manifest["sha256"][k] != v for k, v in digests.items())
            or manifest["candidate_id"] != estimate["candidate_id"]
            or manifest["evaluation_id"] != estimate["opening_packet_evaluation_id"]):
        raise ValueError("Airport estimate and factory input edition differ")
    opening = json.loads(members["opening.json"])
    civil = json.loads(members["civil-article.json"])
    quantities = drivers(csv.DictReader(io.StringIO(members["opening-bom.csv"].decode())))
    calendar, machines, routes, fixtures, sources = {}, [], [], [], {}
    for name, filename in SHOPS.items():
        raw = (HERE / filename).read_bytes()
        sources[filename] = sha256(raw).hexdigest()
        shop = tomllib.loads(raw.decode())
        calendar[name] = {k: shop[k] for k in ("workdays", "hours_per_day", "utilisation")}
        calendar[name]["daily_targets"] = shop.get("daily_targets", {})
        if not set(calendar[name]["daily_targets"]) <= quantities.keys():
            raise ValueError(f"Unknown daily demand driver in {filename}")
        if "source" in shop:
            expected = {"opening_bom_sha256": digests["opening-bom.csv"],
                        "opening_evaluation_id": opening["evaluation_id"],
                        "civil_evaluation_id": opening["civil_evaluation_id"],
                        "civil_article_evaluation_id": civil["evaluation_id"],
                        "civil_article_physical_id": civil["physical_id"]}
            if any(shop["source"][key] != value for key, value in expected.items()):
                raise ValueError(f"Revisit {filename} against the changed drawing edition")
        ids = {item["id"] for item in shop["resource"]}
        if len(ids) != len(shop["resource"]) or ids.intersection(m["id"] for m in machines):
            raise ValueError(f"Each physical factory resource must have one owner in {filename}")
        for resource in shop["resource"]:
            if resource["lot_id"] not in lots:
                raise ValueError(f"Unknown parent procurement lot for {resource['id']}")
            machines.append(dict(shop=name, **resource, **daily_capacity(resource, shop, quantities)))
        for product in shop["product"]:
            if not set(product["resources"]) <= ids:
                raise ValueError(f"Missing work centre for {product['name']}")
            count = number(product.get("multiplier", 1))
            amount = {k: None if quantities[k] is None else float(quantities[k] * count) for k in product["items"]}
            routes.append(dict(shop=name, **product, opening_quantities=amount))
        by_id = {r["id"]: r for r in machines if r["shop"] == name}
        for fixture in shop.get("fixture_item", []):
            parent = by_id[fixture["parent"]]
            if type(fixture["per_unit"]) is not int or fixture["per_unit"] <= 0:
                raise ValueError("Invalid number of tooling components per fixture")
            units = parent["required_units"]
            fixtures.append(dict(**fixture, shop=name, lot_id=parent["lot_id"],
                                 quantity=None if units is None else units * fixture["per_unit"]))
    delivery = opening["delivery"]
    monthly = delivery["monthly_delivery"]["months"]
    inventory = max(m["cast_beams_awaiting_release"] + m["released_beams_awaiting_erection"] for m in monthly)
    storage = next(m for m in machines if m["id"] == "civil-stock-position")
    if storage["minimum_units"] < inventory:
        raise ValueError("Planned beam storage falls below the monthly inventory")
    result = dict(candidate_id=estimate["candidate_id"], frame_revision=estimate["frame_revision"],
                  opening_evaluation_id=opening["evaluation_id"], estimate_evaluation_id=estimate["evaluation_id"],
                  source_sha256=sources, drawing_member_sha256=digests,
                  method_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                  opening_drivers={k: None if v is None else float(v) for k, v in quantities.items()},
                  work_calendars=calendar, resources=machines, product_routes=routes, fixture_items=fixtures,
                  peak_beam_inventory=inventory, fabrication_released=False, prices_confirmed=False)
    return {**result, "evaluation_id": _id(result)}


def count_label(resource):
    value = resource["required_units"]
    if value is not None:
        return str(value)
    lower = resource["minimum_units"]
    return f"≥{lower}, final open" if lower else "Open"


def report(record):
    counts = record["opening_drivers"]
    lines = [
        "# Baghdad Airport factory specification", "",
        f"The opening requires {counts['Braced steel body']:g} cars, {counts['Removable powered bogie']:g} powered bogies and {counts['beam_count']:,.0f} ten-metre beams. Use the tables to reserve shop capacity, quote locally made fixtures and contract specialist processes. Each count is a planning provision for the stated calendar. A contract service or a repair road is listed in its own unit.", "",
        "Download the [equipment and tooling price return](factory-equipment.csv) or the [production routes and sizing assumptions](factory-routes.json). Both identify the opening and the factory evaluation. Each machine line belongs inside its named procurement lot. Price owned equipment, hire, contracted throughput and ongoing maintenance on their respective terms before replacing any part of the existing allowance.", "",
        "## How quantities are calculated", "",
        "For each machine, sum the hours it occupies across all products during a working day. Use the higher of the programme average and any declared peak. Spread one-off setup hours across the production window. Divide by usable hours per machine per day, round up, then apply the minimum required for simultaneous work or dedicated provision. A blank product quantity keeps the final machine count open. Hours of mould occupancy continue while a crew is off shift.", "",
        "These are capacity screens for the identified operations. The supplier must return a feasible loading sequence, material handling and crew cover through changeovers, inspection, rework and outages. Parallel workloads on a shared crane, test bench or yard are booked once. Return power, air, extraction, floor and access requirements with the installed arrangement.", "",
    ]
    for shop, policy in record["work_calendars"].items():
        lines.extend([f"## {shop}", "",
                      f"The planning window has {policy['workdays']} effective workdays. The standard resource day has {policy['hours_per_day']} hours at {policy['utilisation']:.1%} availability within the shift. Equipment with a different occupation window has its own daily hours below.", "",
                      "| Machine, tooling or service | Planning count | Known occupied h/day | Usable h/unit/day | Provision and price scope |",
                      "|---|---:|---:|---:|---|"])
        for r in record["resources"]:
            if r["shop"] == shop:
                known = f"{r['known_resource_hours_per_day']:.2f}" if r.get("load") else "—"
                if r["unknown_demand"] and not r["known_resource_hours_per_day"]:
                    known = "Open"
                lines.append(f"| {r['name']} | {count_label(r)} ({r['unit']}) | {known} | {r['usable_hours_per_day']:.2f} | {r['disposition']} · `{r['lot_id']}` |")
        lines.extend(["", "| Manufactured or integrated item | Opening quantities by source item | Routing and inspection |", "|---|---|---|"])
        for product in record["product_routes"]:
            if product["shop"] == shop:
                labels = {"@saw": "RHS and liner blanks", "@plate": "nested plate pieces"}
                amounts = ", ".join(f"{labels.get(k, k)} × {v:g}" if v is not None else f"{k} open"
                                    for k, v in product["opening_quantities"].items())
                lines.append(f"| {product['name']} | {amounts} | {product['route']}. {product['inspection']}. |".replace("..", "."))
        lines.append("")
    lines.extend(["## Locally manufacturable tooling components", "",
                  "Include these repeatable components inside the parent fixture quote. Counts scale with the planned number of jigs or mould positions. Working-face tolerances, welds, fasteners, lift points, anchorages and materials require the tool designer’s drawing and inspection plan.", "",
                  "| Tooling component | Parent resource | Per unit | Opening tool quantity | Manufacture and inspection |",
                  "|---|---|---:|---:|---|"])
    for f in record["fixture_items"]:
        quantity = "Open" if f["quantity"] is None else f["quantity"]
        lines.append(f"| {f['name']} | {f['parent']} | {f['per_unit']} | {quantity} | {f['route']} |")
    lines.append("")
    lines.extend(["## Workshop trials and buying terms", "",
                  "Trial a quick-change body fixture and replaceable datum stops on a representative frame. Record setup time from the last accepted part to the next accepted part, first-pass yield and the reinspection time after changing the fixture. Compare the repeat run with a local subcontracted process using the same part and acceptance basis. [Vehicle workcells](vehicle-factory/VEHICLE-WORKCELLS.md) · [NIST shop improvement methods](https://www.nist.gov/mep/lean-and-process-improvement)", "",
                  f"The Airport monthly schedule reaches {record['peak_beam_inventory']} beams in storage before erection. Reserve stack and crane access by issue and release date. Compare a reusable mould and exchangeable end forms with an existing precaster's bed. Trial laser or tracker survey against surveyed targets and physical gauges at the actual inserts and bearing seats. Hidden reinforcement needs separate pre-pour inspection. A factory study on arch segments and panels provides a method to test locally. [Civil workcells](infrastructure/CIVIL-WORKCELLS.md) · [Published scan-to-IFC study](https://www.mdpi.com/2075-5309/16/12/2383)", "",
                  f"For wayside wiring, issue the connector list and revision before cutting a batch. Trial a labelled wire kit on a movable backplate fixture. Compare local manual cut, strip and crimp with outsourced digitally prepared terminals by first-pass continuity, rework, setup and ownership of the wire list. The proposed electrical shop counts {counts['grid_protection_gateways']:g} grid-protection gateways, {counts['section_control_gateways']:g} section gateways and {counts['station_dispatch_controllers']:g} station dispatch controllers as work drivers. The number of rectifier cabinets and actual terminations is still open. The vehicle harness bench is in a separate assumed shop. If one bidder co-locates the two, combine their load profiles and report the released equipment. [Electrical enquiry](infrastructure/ELECTRICAL-CONTROLS.md) · [Modular wiring workstation example](https://www.rittal.com/com-en/products/PG20231215RAS101/PG20240408RAS202/PG20240408RAS203/PRO114365?variantId=4051130)", "",
                  "Attach the completed equipment return to the matching ERPNext RFQ and submit the lot price through the buyer portal. The register covers first production, shared capacity and outsourced work. The existing $44.80m tooling allowance also covers route and recovery equipment. A machine subtotal cannot replace that whole allowance until the buyer matches the exclusions and gives credit for equipment included in a supplier's unit price. [Buyer procedure](PROCUREMENT-PLAN.md)", "",
                  f"Factory evaluation `{record['evaluation_id']}`. Rebuild with `python3 -m cities.Baghdad.engineering.prototype.factory --check`.", ""])
    return "\n".join(lines)


def artifacts(estimate=None, drawings=None):
    record = build(estimate, drawings)
    buf = io.StringIO()
    fields = ["id", "shop", "name", "unit", "required_units", "minimum_units", "disposition", "lot_id",
              "specification", "note", "known_resource_hours_per_day", "usable_hours_per_day"]
    returns = ["offered_quantity", "ownership_or_hire_period", "currency", "installed_or_service_price",
               "annual_upkeep", "shift_and_setup_basis", "utilities_and_floor", "evidence_and_exclusions"]
    writer = csv.DictWriter(buf, fieldnames=["candidate_id", "factory_evaluation_id", *fields, *returns], lineterminator="\n")
    writer.writeheader()
    for row in record["resources"]:
        writer.writerow(dict(candidate_id=record["candidate_id"], factory_evaluation_id=record["evaluation_id"],
                             **{k: row.get(k) for k in fields}))
    return {REPORT: report(record).encode(), REGISTER: buf.getvalue().encode(),
            ROUTES: (json.dumps(record, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--publish", action="store_true")
    args = parser.parse_args()
    files = artifacts()
    if args.publish:
        with disk_reservation(sourcing_estimates.ROOT, HERE, "Airport factory equipment files", 4 << 20) as lease:
            for name, raw in files.items():
                check_disk_reservation(lease)
                write_atomic(HERE / name, raw)
    elif any((HERE / name).read_bytes() != raw for name, raw in files.items()):
        raise SystemExit("Regenerate the Airport factory files for the changed source or capacity assumption")
    print(json.loads(files[ROUTES])["evaluation_id"])


if __name__ == "__main__":
    main()
