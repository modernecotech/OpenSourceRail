"""Reproduce a same-frame rapid manufacturing comparison and its envelopes."""
from __future__ import annotations

import argparse
import csv
from hashlib import sha256
import heapq
import io
import json
import math
from pathlib import Path
import tomllib
from zipfile import ZipFile

HERE = Path(__file__).resolve().parent
PROTOTYPE = HERE.parent
ORDERS = (36, 180, 360)
RATE_CASES = ("low", "base", "high")
STUDY_YEAR_DAYS = 250
SHIFT_HOURS = 8
AVAILABILITY = 0.8
# Vendor screen using the optional long-stock automatic loader. This is a
# comparison of published envelopes. A priced, demonstrated process is open.
LOADER = {"length_mm": 12500, "weight_kg": 370, "section_diagonal_mm": 290,
          "section_side_mm": 254, "weight_kg_m": 40, "unload_length_mm": 12500,
          "mild_steel_wall_mm": 10}
SOURCE_FILES = (
    "airport-prototype.zip", "factory-routes.json", "shop-rates.toml",
    "vehicle-factory/vehicle-resources.toml", "vehicle-factory/installed-ga.json",
    "cam/cam-manifest.json", "cam/saw-stock.csv", "cam/saw-cuts.csv",
    "cam/training/freecad-receipt.json", "cam/CAM.md",
)
METHODS = {
    "saw_fixture": {"title": "Guarded saw and modular manual fixtures", "laser": False,
                    "robots": False, "body_clock": 1.0, "bogie_clock": 1.0,
                    "arc_labour": 1.0, "rework": .09},
    "shared_cnc": {"title": "Shared CNC bookings and modular manual fixtures", "laser": True,
                   "robots": False, "body_clock": .85, "bogie_clock": .85,
                   "arc_labour": .85, "rework": .07},
    "dedicated": {"title": "Dedicated tube laser and guarded robot cells", "laser": True,
                  "robots": True, "body_clock": .62, "bogie_clock": .64,
                  "arc_labour": .47, "rework": .06},
}


def hash_bytes(value):
    return sha256(value).hexdigest()


def read_source(folder):
    sources = {name: (folder / name).read_bytes() for name in SOURCE_FILES}
    factory = json.loads(sources["factory-routes.json"])
    cam = json.loads(sources["cam/cam-manifest.json"])
    rates = tomllib.loads(sources["shop-rates.toml"].decode())
    ga = json.loads(sources["vehicle-factory/installed-ga.json"])
    if any(factory["candidate_id"] != source["candidate_id"]
           or factory["frame_revision"] != source["frame_revision"] for source in (cam, rates)):
        raise ValueError("Factory, CAM and pricing must describe one physical frame")
    if factory["source_sha256"]["vehicle-factory/vehicle-resources.toml"] != hash_bytes(
            sources["vehicle-factory/vehicle-resources.toml"]):
        raise ValueError("Vehicle routing source changed after the factory issue")
    if factory["opening_evaluation_id"] != cam["opening_evaluation_id"]:
        raise ValueError("Factory and CAM orders differ")
    if ga.get("candidate_id") != factory["candidate_id"]:
        raise ValueError("The installed geometry does not identify the quoted factory candidate")
    for name in ("saw-stock.csv", "saw-cuts.csv"):
        if cam["artifact_sha256"][name] != hash_bytes(sources[f"cam/{name}"]):
            raise ValueError(f"CAM {name} changed after issue")

    with ZipFile(io.BytesIO(sources["airport-prototype.zip"])) as archive:
        listed = {name: hash_bytes(archive.read(name)) for name in
                  ("opening.json", "opening-bom.csv", "revised-cuts.csv", "car-and-bogies.obj")}
        for register in (factory["drawing_member_sha256"], cam["source_sha256"]):
            for name in register.keys() & listed.keys():
                if listed[name] != register[name]:
                    raise ValueError(f"Factory/CAM archive mismatch for {name}")
        revised = read_csv(archive.read("revised-cuts.csv"))
    return sources, factory, cam, rates, revised, listed


def read_csv(raw):
    return list(csv.DictReader(io.StringIO(raw.decode())))


def screen_tubes(stock, revised):
    mass_by_profile = {}
    for row in revised:
        if row["nominal_stock_mm"].startswith("RHS "):
            profile, mass = row["nominal_stock_mm"], float(row["nominal_kg_per_m"])
            if profile in mass_by_profile and mass != mass_by_profile[profile]:
                raise ValueError(f"Inconsistent unit mass for {profile}")
            mass_by_profile[profile] = mass
    results = []
    for row in stock:
        profile, length = row["stock_section"], int(row["raw_length_mm"])
        bars = int(row["bars"])
        result = {"pattern": row["pattern"], "profile": profile, "bar_length_mm": length,
                  "bars": bars, "blank_pieces": bars * int(row["cuts_per_bar"])}
        if profile not in mass_by_profile:
            results.append({**result, "screen": "retain dedicated flat-stock saw/drill lane",
                            "automatic_tube_eligible": False})
            continue
        width, height, wall = map(float, profile.removeprefix("RHS ").split("x"))
        unit_mass = mass_by_profile[profile]
        mass = unit_mass * length / 1000
        exceeded = [name for name, value in (
            ("length_mm", length), ("weight_kg", mass), ("weight_kg_m", unit_mass),
            ("section_diagonal_mm", math.hypot(width, height)),
            ("section_side_mm", max(width, height)), ("mild_steel_wall_mm", wall)
        ) if value > LOADER[name]]
        results.append({**result, "bar_nominal_kg": round(mass, 2), "kg_per_m": unit_mass,
                        "automatic_tube_eligible": not exceeded,
                        "screen": exceeded or ["within quoted envelope for further review"]})
    return results


def quote(factory, rates, cam, tubes, cars, method, *, severe=False, fixed_capacity=None):
    route = METHODS[method]
    known = {row["id"]: row for row in factory["resources"] if row["shop"] == "Vehicle works"}
    original_cars = cam["cars"]
    drivers = factory["opening_drivers"]

    def hours(resource, keys=None):
        return sum((sum(drivers[item] for item in load["items"] if keys is None or item in keys)
                    * load["hours"]) / original_cars for load in known[resource]["load"])

    laser_pieces = sum(row["blank_pieces"] for row in tubes if row["automatic_tube_eligible"]) / original_cars
    laser_pieces = laser_pieces if route["laser"] else 0.0
    saw_pieces = cam["saw_blanks"] / original_cars - laser_pieces
    rework = route["rework"] * (2 if severe else 1)
    arc_body = hours("vehicle-arc-set", ("Braced steel body",))
    arc_bogie = hours("vehicle-arc-set", ("Removable powered bogie",))
    body_h = hours("vehicle-body-bed") * route["body_clock"]
    bogie_h = hours("vehicle-bogie-bed") * route["bogie_clock"]
    setup = lambda key: sum(load.get("setup_hours", 0) for load in known[key]["load"])
    rate = rates["rates"]
    operations = []

    def operation(key, task_h, crew_h, setup_h, predecessors, *, cost=None, min_cells=1, crew_setup=False):
        if not task_h:
            return
        loaded_h = task_h * (1 + rework)
        # Size against full resource occupation including one repeated setup per lane.
        usable = SHIFT_HOURS * AVAILABILITY
        cells = (fixed_capacity[key] if fixed_capacity is not None else
                 max(min_cells, math.ceil(cars * loaded_h / (STUDY_YEAR_DAYS * usable - setup_h))))
        operations.append(dict(key=key, h=loaded_h, crew_h=crew_h * (1 + rework), setup=setup_h,
                               cells=cells, predecessors=predecessors, cost=cost, crew_setup=crew_setup,
                               average_local_positions_per_lane=round(crew_h / task_h, 3),
                               indicative_local_roster_positions=cells * math.ceil(crew_h / task_h)))

    operation("saw", saw_pieces * .15, saw_pieces * .15, setup("vehicle-saw"), [],
              cost=rate["vehicle-saw"], crew_setup=True)
    operation("tube", laser_pieces * .045, laser_pieces * .015 if route["robots"] else 0,
              42, [], cost={"basis": "units" if route["robots"] else "hours",
                            "usd": [550000, 790000, 1150000] if route["robots"] else [85, 130, 215]},
              crew_setup=route["robots"])
    operation("plate", hours("vehicle-plate-contract"), 0, setup("vehicle-plate-contract"),
              [], cost=rate["vehicle-plate-contract"])
    chop = [row["key"] for row in operations]
    prep_h = hours("vehicle-prep") - (laser_pieces / (cam["saw_blanks"] / original_cars)) * 1.4
    operation("prep", prep_h, prep_h, setup("vehicle-prep"), chop,
              cost=rate["vehicle-prep"], crew_setup=True)
    # Fixtures contain welding activity. Their clock time is separate from
    # hands-on fit and arc time, which is charged once as local direct labour.
    operation("body", body_h, 24 * route["body_clock"] + arc_body * route["arc_labour"],
              setup("vehicle-body-bed"), ["prep"], cost=rate["vehicle-body-bed"], crew_setup=True)
    operation("bogies", bogie_h, 15 * route["bogie_clock"] + arc_bogie * route["arc_labour"],
              setup("vehicle-bogie-bed"), ["prep"], cost=rate["vehicle-bogie-bed"], crew_setup=True)
    operation("metrology", hours("vehicle-metrology", ("Braced steel body", "Removable powered bogie")),
              4, setup("vehicle-metrology"), ["body", "bogies"], cost=rate["vehicle-metrology"],
              crew_setup=True)
    operation("ndt", hours("vehicle-weld-ndt"), 0, setup("vehicle-weld-ndt"),
              ["metrology"], cost=rate["vehicle-weld-ndt"])
    operation("machining", hours("vehicle-bogie-machine"), 0, setup("vehicle-bogie-machine"),
              ["ndt"], cost=rate["vehicle-bogie-machine"])
    operation("coating", hours("vehicle-coat"), 0, setup("vehicle-coat"),
              ["machining"], cost=rate["vehicle-coat"])
    crane_h = hours("vehicle-shop-crane", ("Braced steel body", "Removable powered bogie"))
    operation("crane_handover", crane_h, 0, 24, ["coating"], cost=rate["vehicle-shop-crane"])

    # Identical dispatch order at each work centre (deterministic FIFO).
    # Time is measured in available production hours, then mapped to shifts.
    ready = {op["key"]: [op["setup"]] * op["cells"] for op in operations}
    first = end = 0
    for _ in range(cars):
        jobs = {}
        for op in operations:
            slots = ready[op["key"]]
            free = heapq.heappop(slots)
            start = max([free, *(jobs[parent] for parent in op["predecessors"])])
            jobs[op["key"]] = start + op["h"]
            heapq.heappush(slots, jobs[op["key"]])
        end = jobs["crane_handover"]
        first = first or end
    crew_hours = sum(cars * row["crew_h"] + (row["cells"] * row["setup"] if row["crew_setup"] else 0)
                     for row in operations)
    factors = (.06, .13, .23)
    wages = (5.5, 8.0, 12.0)
    fixed_extras = {}
    joining_lanes = sum(op["cells"] for op in operations if op["key"] in {"body", "bogies"})
    if route["robots"]:
        fixed_extras["guarded robot pair, two stations"] = [240000, 420000, 720000]
        fixed_extras["guarded spares and manual continuity"] = [16000, 32000, 76000]
        fixed_extras["qualification and trial programming allowance"] = [65000, 115000, 210000]
        # Assign one independently guarded robot station per occupied joining lane.
        robot_pairs = math.ceil(joining_lanes / 2)
        fixed_extras["guarded robot pair, two stations"] = [
            v * robot_pairs for v in fixed_extras["guarded robot pair, two stations"]
        ]
    else:
        arc_sets = max(3, joining_lanes)
        fixed_extras["manual welding and extraction sets"] = [v * arc_sets for v in rate["vehicle-arc-set"]["usd"]]
        fixed_extras["jig, qualification and first-off trial allowance"] = (
            [17000, 32000, 70000] if method == "shared_cnc" else [12000, 24000, 50000]
        )
    fixed_extras["controlled materials stores"] = rate["vehicle-stores"]["usd"]
    case_prices = {}
    for idx, case in enumerate(RATE_CASES):
        capital, services = sum(values[idx] for values in fixed_extras.values()), 0.0
        for op in operations:
            cost = op["cost"]
            occupied = op["h"] * cars + op["setup"] * op["cells"]
            if cost["basis"] == "units":
                capital += op["cells"] * cost["usd"][idx]
            else:
                booked = math.ceil(occupied / SHIFT_HOURS) if cost["basis"] == "shift" else occupied
                services += booked * cost["usd"][idx]
        upkeep = capital * factors[idx]
        wages_total = crew_hours * wages[idx]
        total = capital + services + wages_total + upkeep
        case_prices[case] = {"setup_tooling_usd": round(capital), "hours_and_shifts_hire_usd": round(services),
                            "direct_local_labour_usd": round(wages_total),
                            "consumables_upkeep_allowance_usd": round(upkeep),
                            "total_usd": round(total), "usd_per_car": round(total / cars)}
    return {"machine_counts": {op["key"]: op["cells"] for op in operations},
            "operations": operations, "separate_tooling": fixed_extras,
            "robot_pairs": robot_pairs if route["robots"] else 0,
            "saw_blanks_per_car": saw_pieces, "tube_laser_blanks_per_car": laser_pieces,
            "first_coated_frame_set_shift_days": round(first / (SHIFT_HOURS * AVAILABILITY), 1),
            "last_coated_frame_set_shift_days": round(end / (SHIFT_HOURS * AVAILABILITY), 1),
            "average_post_start_interval_shift_days": (
                round((end - first) / ((cars - 1) * SHIFT_HOURS * AVAILABILITY), 2) if cars > 1 else None
            ),
            "direct_local_crew_hours": round(crew_hours, 1), "rework_occupancy_fraction": rework,
            "indicative_roster_positions_all_local_lanes": sum(op["indicative_local_roster_positions"]
                                                                for op in operations),
            "price_cases": case_prices}


def build(folder=PROTOTYPE):
    sources, factory, cam, rates, revised, listed = read_source(folder)
    tubes = screen_tubes(read_csv(sources["cam/saw-stock.csv"]), revised)
    if sum(row["blank_pieces"] for row in tubes) != cam["saw_blanks"]:
        raise ValueError("Tube pattern counts do not match CAM order")
    def case(cars, method, **options):
        return quote(factory, rates, cam, tubes, cars, method, **options)

    orders = {str(cars): {method: case(cars, method) for method in METHODS} for cars in ORDERS}
    crossings = dict.fromkeys(RATE_CASES)
    for n in range(1, 361):
        dedicated = case(n, "dedicated")["price_cases"]
        shared = case(n, "shared_cnc")["price_cases"]
        for name in RATE_CASES:
            if crossings[name] is None and dedicated[name]["total_usd"] < shared[name]["total_usd"]:
                crossings[name] = n
        if all(crossings.values()):
            break
    result = {"schema": "osr.rapid-frame-manufacture.v1", "candidate_id": factory["candidate_id"],
              "frame_revision": factory["frame_revision"], "factory_evaluation_id": factory["evaluation_id"],
              "cam_evaluation_id": cam["evaluation_id"], "study_year_days": STUDY_YEAR_DAYS,
              "shift_hours": SHIFT_HOURS, "available_fraction": AVAILABILITY,
              "opening_cars": cam["cars"], "gross_blanks_per_car": (cam["saw_blanks"] + sum(cam["blank_quantities"].values())) // cam["cars"],
              "tube_loader_envelope": LOADER, "stock_profile_screen": tubes, "methods": METHODS,
              "orders": orders, "double_rework_180_cars": {
                  name: case(180, name, severe=True, fixed_capacity=orders["180"][name]["machine_counts"])
                  for name in METHODS
              },
              "first_dedicated_crossover_cars_from_1_to_360": crossings,
              "source_sha256": {name: hash_bytes(raw) for name, raw in sources.items()},
              "archive_member_sha256": listed, "method_sha256": hash_bytes(Path(__file__).read_bytes()),
              "production_release": False, "safety_acceptance": False}
    result["evaluation_id"] = hash_bytes(json.dumps(result, sort_keys=True).encode())
    return result


def markdown(result):
    lines = ["# Rapid manufacture comparison", "",
             "The order covers coated steel body structure and two coated, machined bogie frames per car.",
             "Prices use constant 2026 US dollars. Local crew hours exclude the hours of hired suppliers.", "",
             "| Cars | Workcell route | First / last shift day | Local crew hours | USD per car low / base / high |",
             "|---:|---|---:|---:|---:|"]
    for cars, order in result["orders"].items():
        for name, option in order.items():
            amounts = " / ".join(f"${option['price_cases'][case]['usd_per_car']:,}" for case in RATE_CASES)
            lines.append(f"| {cars} | {METHODS[name]['title']} | {option['first_coated_frame_set_shift_days']:.1f}"
                         f" / {option['last_coated_frame_set_shift_days']:.1f} | {option['direct_local_crew_hours']:,.1f} | {amounts} |")
    improved = sum(row["blank_pieces"] for row in result["stock_profile_screen"] if row["automatic_tube_eligible"])
    lines += ["", f"The tube loader screen admits {improved:,} nominal blanks in the source order for further process review.",
              "Heavy chords and flat liners retain the saw/preparation lane.", "",
              "The crossover search shows the first order size where dedicated investment costs less than shared CNC.",
              "Capacity changes occur at integer cell counts, so check the actual order.", "",
              "| Price case | First crossover in 1–360 cars |", "|---|---:|"]
    for case, cars in result["first_dedicated_crossover_cars_from_1_to_360"].items():
        lines.append(f"| {case.capitalize()} | {cars if cars is not None else 'Beyond the studied range'} |")
    lines += ["", f"Evaluation: `{result['evaluation_id']}`.",
              "[Model, provenance and individual workcell counts](comparison.json).", ""]
    return "\n".join(lines)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--check", action="store_true")
    args = p.parse_args()
    report = build()
    outputs = {"comparison.json": json.dumps(report, indent=2) + "\n",
               "comparison.md": markdown(report)}
    for name, content in outputs.items():
        file = HERE / name
        if args.check:
            if file.read_text() != content:
                raise SystemExit(f"Published manufacturing study differs: {name}")
        else:
            file.write_text(content)


if __name__ == "__main__":
    main()
