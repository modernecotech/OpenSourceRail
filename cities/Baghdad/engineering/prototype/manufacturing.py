"""Compile first-article routes and opening takeoffs for the revised Airport design."""
import csv
import io
from collections import Counter, defaultdict
from hashlib import sha256
from math import isclose
from pathlib import Path

from cities.Baghdad import airport_assembly
from cities.Baghdad.engineering.prototype.car import identity


def _checked_sources(parent, article, cuts):
    opening, finance = article["opening"], article["finance"]
    b = opening["bundle"]
    assembly = parent["assembly"]
    original = parent["opening"]
    inherited = ("formation_cars", "active_sets", "spares", "stops", "terminal_layout", "span_m", "pier_family")
    for name, record in (("article", article), ("parent assembly", assembly), ("service", parent["service"])):
        if record["evaluation_id"] != identity({k: v for k, v in record.items() if k != "evaluation_id"}):
            raise ValueError(f"Stale manufacturing source: {name}")
    if (article["parent_candidate_id"] != original["candidate_id"]
            or assembly["candidate_id"] != original["candidate_id"]
            or assembly["opening_evaluation_id"] != original["evaluation_id"]
            or article["parent_evaluation_id"] != original["evaluation_id"]
            or article["parent_service_evaluation_id"] != parent["service"]["evaluation_id"]
            or any(b[k] != original["bundle"][k] for k in inherited)
            or b["vehicle_revision"] != article["frame_revision"]
            or identity(b) != opening["candidate_id"] or article["candidate_id"] != opening["candidate_id"]
            or article["artifact_sha256"]["revised-cuts.csv"] != sha256(cuts).hexdigest()):
        raise ValueError("Mismatched source drawing, service or opening for manufacturing")
    power = opening["power"]
    feeder = opening["section_power"]
    if (finance["candidate_id"] != opening["candidate_id"]
            or power["parent_candidate_id"] != opening["candidate_id"]
            or feeder["power_evaluation_id"] != power["evaluation_id"]
            or b["feeder_design_id"] != feeder["design_id"]
            or b["feeder_design_id"] != power["feeder_design_id"]
            or b["grid_sites"] != power["supply"]["grid_sites"]
            or power["vehicle"]["mass_t"] != article["planning_crowd_train_t"]):
        raise ValueError("Power and finance must use the revised priced Airport configuration")


def _cut_stock(article, cuts, cars, fleet, writer):
    counts = Counter()
    profiles = defaultdict(lambda: {"pieces": 0, "kg": 0.0, "m": 0.0})
    for row in csv.DictReader(io.StringIO(cuts.decode())):
        assemblies = ("bogie-A", "bogie-B") if row["assembly"] == "bogie" else ("body",)
        quantity = int(row["cuts_per_assembly"])
        for assembly in assemblies:
            counts[assembly, row["part"]] += quantity
        n = quantity * len(assemblies)
        material = profiles[row["nominal_stock_mm"]]
        material["pieces"] += n
        material["kg"] += len(assemblies) * float(row["gross_mass_kg"])
        if row["nominal_kg_per_m"]:
            material["m"] += n * float(row["cut_length_m"])
        else:
            material["m"] = None  # Gussets are plate shapes; the cut length is a side.
        writer.writerow(("cut material", row["part"], "piece", n, n*cars, n*cars*fleet,
                         f"{row['nominal_stock_mm']}, {row['cut_length_m']} m per cut"))
    if counts != Counter((p["assembly"], p["part"]) for p in article["pieces"]):
        raise ValueError("Cut list differs from the individual drawn body or bogie occurrences")
    if not isclose(sum(r["kg"] for r in profiles.values()), article["mass"]["cut_kg_per_car"], abs_tol=0.002):
        raise ValueError("Cut-list mass differs from the article drawing")
    return [{
        "nominal_stock_mm": name,
        "pieces_per_car": r["pieces"],
        "pieces_opening": r["pieces"] * cars * fleet,
        "cut_m_opening": None if r["m"] is None else round(r["m"] * cars * fleet, 4),
        "gross_cut_kg_opening": round(r["kg"] * cars * fleet, 4),
    } for name, r in sorted(profiles.items())]


def routing(parent, article, cuts):
    _checked_sources(parent, article, cuts)
    opening = article["opening"]
    b = opening["bundle"]
    fleet = b["active_sets"] + b["spares"]
    cars = b["formation_cars"]
    civil, controls = opening["civil"], opening["controls"]
    procurement = opening["section_power"]["procurement"]
    scope = airport_assembly.production_lots(opening, civil)
    plans = {
        "Representative car": ("car-and-bogies.ifc", "revised-cuts.csv", "portal-detail.svg", "returns/weights.json"),
        "Powered bogie": ("car-and-bogies.ifc", "mechanical.json", "returns/weights.json"),
        "Viaduct beam": ("track-span.ifc", "pier.ifc", "mechanical.json"),
        "Accessible station bay": ("platform-bay.ifc", "portal-detail.svg", "workshop-guide.md"),
        "Traction and control module": ("electrical/priced-single-line.svg", "returns/priced_radial-feeder.json", "commissioning.md"),
    }
    for order in scope["draft_work_orders"]:
        order["documents"] = plans[order["article"]]
        order["frame_revision"] = article["frame_revision"]
    stream = io.StringIO()
    writer = csv.writer(stream, lineterminator="\n")
    writer.writerow(("scope", "item", "unit", "per_car", "per_train", "opening_quantity", "basis"))
    stock = _cut_stock(article, cuts, cars, fleet, writer)
    for row in parent["assembly"]["parts"]:
        writer.writerow(("installed allocation", row["item"], row["unit"], row["per_car"],
                         row["per_train"], row["fleet_quantity"], row["evidence_scope"]))
    per_car = article["proposed_service_inventory"]["per_car"]
    for key in ("sliding_leaves", "two_carriages_per_leaf", "two_guide_stops_per_leaf", "anti_drop_retention_points",
                "flush_liner_screws", "liner_threaded_receivers", "moving_leaf_harness_paths_if_powered_at_leaf"):
        n = per_car[key]
        writer.writerow(("door detail", key.replace("_", " "), "each", n, n*cars, n*cars*fleet,
                         "First-article proposal beneath the installed door allocation"))
    for source, fields, basis in (
        (civil, ("beam_count", "lift_count", "pier_foundation_count", "bearing_unit_allowance"), "opening.json civil"),
        (procurement, ("dc_source_groups", "dc_outgoing_breaker_circuits", "normally_open_track_ties",
                      "feed_half_bays", "protected_track_km"), "opening.json section_power.procurement"),
        (controls, ("grid_protection_gateways", "station_dispatch_controllers", "section_control_gateways",
                    "occ_equipment_sets"), "opening.json controls"),
        (opening["power"]["maintenance_quantities"], ("onboard_contact_sets", "charger_ports"),
         "opening.json power.maintenance_quantities"),
        (b, ("depots", "control_centres", "grid_sites"), "opening.json bundle"),
        (opening["delivery"], ("factory_yards_needed_at_declared_rate", "erection_fronts_needed_at_declared_rate"),
         "opening.json delivery; planning productivity"),
    ):
        for key in fields:
            unit = "track-km" if key == "protected_track_km" else "each"
            writer.writerow(("opening works and equipment", key, unit, None, None, source[key], basis))
    for item, count, basis in (
        ("passenger station sites", len(b["stops"]), "opening.json bundle.stops"),
        ("open terminal platform faces (both ends)", sum(b["terminal_layout"]["open_platform_faces_each_end"]),
         "opening.json bundle.terminal_layout; excludes intermediate stops"),
        ("station bay panels after plant and access openings", None, "platform-bay.ifc is one trial bay"),
        ("installed and tested rectifier cabinets", None, "supplier return per site power rating and redundancy"),
        ("wayside braking and recovery equipment", None, "priced system allowance; return rescue equipment schedule"),
    ):
        writer.writerow(("opening works and equipment", item, "each", None, None, count, basis))
    bom = stream.getvalue().encode()
    record = {
        **scope, "candidate_id": opening["candidate_id"], "frame_revision": article["frame_revision"],
        "source_bindings": {
            "article": article["evaluation_id"], "parent_assembly": parent["assembly"]["evaluation_id"],
            "service": parent["service"]["evaluation_id"], "opening": opening["evaluation_id"],
            "finance": article["finance"]["evaluation_id"], "power": opening["power"]["evaluation_id"],
            "feeder": opening["section_power"]["evaluation_id"], "civil": opening["civil_evaluation_id"],
            "cuts_sha256": sha256(cuts).hexdigest(), "bom_sha256": sha256(bom).hexdigest(),
            "compiler_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        },
        "fleet_cars": cars*fleet, "gross_stock_by_profile": stock,
        "scope": "Five pilot routes. Series quantities include operating and spare trains. Pilots require a separate allocation before adding a pilot to the series. Cut stock excludes kerf, trim, waste and finished hardware. Blank quantities require supplier or designer returns.",
        "fleet_purchase_allowance_usd_m": opening["scopes_usd_m"]["Fleet, including spare sets"],
        "revised_fleet_supplier_quote_usd_m": None,
        "fabrication_released": False,
    }
    record["evaluation_id"] = identity(record)
    return record, bom
