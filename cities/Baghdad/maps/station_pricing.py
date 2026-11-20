"""Reconcile Baghdad station allowances, location evidence and matched station returns."""
import argparse
from collections import Counter, defaultdict
from hashlib import sha256
import json
import math
from pathlib import Path
import sys

DIR = Path(__file__).resolve().parent
CITY = DIR.parent
ROOT = CITY.parents[1]
sys.path.insert(0, str(ROOT))
from engineering.outline import baghdad_system as system
from engineering.performance import check_disk_reservation, disk_reservation

CLASSES = {
    "typical_elevated": "Through station with street access to a straight platform",
    "interchange": "Transfer between routes with passenger circulation and step-free connections",
    "terminal": "Passenger terminus with reversal and stabling interfaces",
    "airport": "Passenger terminal with airport circulation, security and access interfaces",
    "constrained": "Station with a crossing, unusual ground, restricted footprint or difficult access",
}
EVIDENCE = ("site_survey_and_chainage", "approved_station_identity", "step_free_access_and_egress",
            "structure_platform_and_equipment_scope", "budget_boundaries_and_exclusions", "priced_offer")
NETWORKS = ("first", "metropolitan")


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def same_source(points):
    """Group only a named source object at the same coordinates, preserving every occurrence."""
    grouped = defaultdict(list)
    for p in points:
        key = (p["source_url"], tuple(p["longitude_latitude"])) if p["source_url"] else (p["id"],)
        grouped[key].append(p["id"])
    return list(grouped.values())


def build():
    cfg = system.load()
    register = json.loads((CITY / "station-register.json").read_bytes())
    published = json.loads((CITY / "system-results.json").read_bytes())
    review = json.loads((DIR / "corridor-review.geojson").read_bytes())
    if (register != system.station_register(ROOT, cfg) or register["candidate_id"] != published["candidate_id"]
            or register["evaluation_id"] != published["station_register"]["evaluation_id"]):
        raise ValueError("Regenerate the station register and selected network ledger")
    for row in (published, review):
        for path, fingerprint in row["source_sha256"].items():
            if digest(ROOT / path) != fingerprint:
                raise ValueError(f"Station planning source changed: {path}")
    occurrences = [dict(route=f["properties"]["line"], order=f["properties"]["order"],
                        label=f["properties"]["rfi_name"], coordinates=f["geometry"]["coordinates"],
                        coordinate_scope=f["properties"]["coordinate_scope"], source_url=f["properties"].get("source_url"))
                   for f in review["features"] if f["geometry"]["type"] == "Point" and f["properties"]["kind"] == "rfi_named"]
    files = (Path(__file__).resolve(), CITY / "station-register.json", CITY / "system-results.json",
             DIR / "corridor-review.geojson", ROOT / "engineering/outline/baghdad_system.py")
    sources = {p.relative_to(ROOT).as_posix(): digest(p) for p in files}
    networks = {}
    for network in NETWORKS:
        rec, net = register["networks"][network], published["networks"][network]
        count = rec["budgeted_stations"]
        rate = cfg["capital_rates_usd_m"]["station"]
        total = net["selected_capital_scope_usd_m"]["stations_access"]
        if count != net["stations_planning_allowance"] or not math.isclose(count*rate, total):
            raise ValueError("Station count and price no longer reconcile")
        points = rec["mapped_points"]
        coord = Counter(tuple(p["longitude_latitude"]) for p in points)
        groups = same_source(points)
        slots = [f"{network}-station-{i:03d}" for i in range(1, count+1)]
        basis = dict(network=network, candidate=net["selected_candidate_id"], selected_cost_evaluation=net["selected_evaluation_id"],
                     station_register=register["evaluation_id"], price_year=cfg["price_year"], currency=cfg["currency"],
                     study=system._id(sources))
        networks[network] = dict(basis=basis, budget_slots=slots, unit_allowance_usd_m=rate, station_scope_usd_m=total,
                                 source_occurrences=points, same_source_groups=groups,
                                 coordinate_count=len(coord), multi_occurrence_coordinates=sum(v>1 for v in coord.values()),
                                 approved_sites=rec["station_sites_approved"], unassigned_class_and_cost_slots=count,
                                 raw_point_count_gap=count-len(points))
    return dict(networks=networks, source_sha256=sources, first_review_located=occurrences,
                first_review_unlocated=review["unlocated_named_occurrences"],
                review_population_anchors=sum(f["properties"]["kind"] == "proposed_population_anchor" for f in review["features"]))


def template(net):
    return dict(basis=net["basis"], stations=[])


def station_row():
    return dict(budget_slot=None, surveyed_station_id=None, station_class=None, mapped_point_ids=[],
                complete_station_scope_usd_m=None, evidence={k: None for k in EVIDENCE})


def price(net, form):
    if not isinstance(form, dict) or set(form) != {"basis","stations"} or form["basis"] != net["basis"] or not isinstance(form["stations"], list):
        raise ValueError("Use a station return for this network, register and price year")
    valid_slots = set(net["budget_slots"])
    valid_points = {p["id"] for p in net["source_occurrences"]}
    used_slots, sites, point_ids = set(), set(), set()
    classes = defaultdict(lambda: {"stations": 0, "direct_usd_m": 0})
    for row in form["stations"]:
        if not isinstance(row, dict) or set(row) != set(station_row()):
            raise ValueError("Each approved station needs a full return")
        slot, site, category, links = (row[k] for k in ("budget_slot","surveyed_station_id","station_class","mapped_point_ids"))
        evidence, amount = row["evidence"], row["complete_station_scope_usd_m"]
        if (not isinstance(slot, str) or slot not in valid_slots or slot in used_slots
                or not isinstance(site, str) or not site.strip() or site.strip().casefold() in sites
                or not isinstance(category, str) or category not in CLASSES):
            raise ValueError("Use a unique station, eligible allowance slot and declared station class")
        if (not isinstance(links, list) or not all(isinstance(x, str) and x in valid_points for x in links)
                or len(set(links)) != len(links) or point_ids.intersection(links)):
            raise ValueError("Check linked points against the network and previously matched stations")
        if (type(amount) not in (int, float) or not math.isfinite(amount) or amount <= 0
                or not isinstance(evidence, dict) or set(evidence) != set(EVIDENCE)
                or not all(isinstance(v, str) and v.strip() for v in evidence.values())):
            raise ValueError("Price the complete installed station and identify each evidence record")
        used_slots.add(slot)
        sites.add(site.strip().casefold())
        point_ids.update(links)
        classes[category]["stations"] += 1
        classes[category]["direct_usd_m"] += amount
    base = net["station_scope_usd_m"]
    displaced = len(used_slots) * net["unit_allowance_usd_m"]
    priced = sum(item["direct_usd_m"] for item in classes.values())
    return dict(basis=net["basis"], verified_by_independent_reviewer=False, matched_station_count=len(used_slots),
                unassigned_slots=sorted(valid_slots-used_slots), class_subtotals=classes, original_scope_usd_m=base,
                displaced_allowance_usd_m=displaced, priced_scope_usd_m=priced, retained_allowance_usd_m=base-displaced,
                comparative_station_scope_usd_m=base-displaced+priced, direct_difference_usd_m=priced-displaced)


def guide(d):
    lines = ["# Baghdad station sites and prices", "",
             "The seven-corridor and citywide options each carry an installed allowance for accessible stations. Compare offers against each network independently. A plotted place or entrance can support a site investigation. The budget carries one allowance per physical station.", "",
             "| Independent option | Budgeted stations | Point records | Budget less point count¹ | Unique map coordinates | Approved station sites | Direct station budget |",
             "|---|---:|---:|---:|---:|---:|---:|"]
    for key,title in (("first","Seven corridors"), ("metropolitan", "Citywide")):
        n=d["networks"][key]
        lines.append(f"| {title} | {len(n['budget_slots'])} | {len(n['source_occurrences'])} | {n['raw_point_count_gap']} | {n['coordinate_count']} | {n['approved_sites']} | ${n['station_scope_usd_m']:,.0f}m |")
    first, city = (d["networks"][k] for k in NETWORKS)
    missing = sum(len(v) for v in d["first_review_unlocated"].values())
    lines += ["",
        "¹ Subtraction shows the gap only if each mapped point eventually becomes one station. All budget slots currently have a generic price and unresolved site/class allocation. A surveyed station may have several entrances or serve several lines.",
        "",
        f"The seven-corridor register’s {len(first['source_occurrences'])} occurrences identify {len(first['same_source_groups'])} source groups when both the map object and coordinates match. The separate corridor review locates {len(d['first_review_located'])} named occurrences and records {missing} unresolved occurrences. It also proposes {d['review_population_anchors']} population-access anchors. These layers describe overlapping evidence. Their counts must be kept separate. In the citywide map, {city['multi_occurrence_coordinates']} coordinates occur more than once. Preserve every route and point ID until a surveyed transfer layout establishes whether they serve one station.",
        "",
        "## Survey and purchasing return", "",
        "Give each approved physical station one site reference and one generic allowance slot. Record all linked mapped point IDs, access routes, wheelchair approach, vertical circulation, platform width, emergency egress and interchange paths. A separately surveyed location can cite its own evidence and leave the point list empty. Consult landowners and the operator, and obtain a priced scope against the surveyed footprint.",
        "", "| Station class | Scope for comparison |", "|---|---|"]
    for key,value in CLASSES.items():
        lines.append(f"| `{key}` | {value} |")
    lines += ["",
        f"Each matched full station displaces one ${first['unit_allowance_usd_m']:g}m direct allowance. A return must include the survey and chainage, approved station identity, step-free access and egress, platform/structure/equipment scope, boundary reconciliation and a priced offer. Identify station controllers already included in the station price. Keep separately priced viaduct, line systems, land, utilities and train movements outside the matched scope unless the buyer documents an equivalent transfer. Record a shared interchange once, including all entrances and transfer passages in its agreed scope. Partial entrance or lift offers can inform design while the station keeps its full generic allowance.",
        "",
        "From the repository root, use the following commands. The inventory exports the individual location records, source groups, unresolved names and unallocated budget slots. The blank form makes no price substitutions. Add one station row per documented full-scope offer.", "",
        "```sh", "python3 cities/Baghdad/maps/station_pricing.py --inventory > build/baghdad-station-inventory.json",
        "python3 cities/Baghdad/maps/station_pricing.py --network first --template > build/station-return.json",
        "python3 cities/Baghdad/maps/station_pricing.py --row",
        "python3 cities/Baghdad/maps/station_pricing.py --network first --return-file build/station-return.json", "```", "",
        "Use `--network metropolitan` for the citywide option. Each result reports class totals, the replaced and retained direct allowances, and the change in station scope. A buyer must verify the supplied references and cost boundaries before accepting a return. [Station register](../station-register.json) · [Corridor review](corridor-review.geojson) · [City cost ledger](../COST-AND-DELIVERY.md)", ""]
    return "\n".join(lines)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--network", choices=NETWORKS)
    mode = parser.add_mutually_exclusive_group(required=True)
    for flag in ("inventory", "template", "row", "check", "write"):
        mode.add_argument("--"+flag, action="store_true")
    mode.add_argument("--return-file", type=Path)
    args=parser.parse_args()
    data=build()
    if args.check or args.write:
        path=DIR/"STATION-PRICING.md"
        contents=guide(data)
        if args.write:
            with disk_reservation(ROOT, DIR, "Baghdad station pricing sheet", 131072) as lease:
                check_disk_reservation(lease)
                path.write_text(contents)
        elif path.read_text()!=contents:
            raise SystemExit("Regenerate the station pricing sheet")
    else:
        if args.template or args.return_file:
            if not args.network:
                parser.error("Choose the independent network")
            net=data["networks"][args.network]
            result=template(net) if args.template else price(net, json.loads(args.return_file.read_text()))
        else:
            result=data if args.inventory else station_row()
        print(json.dumps(result, indent=2, allow_nan=False))
