"""Source-bound Baghdad opening workshop and cash sensitivities."""

import copy
import csv
import hashlib
import heapq
import io
import json
import math
import zipfile
from collections import Counter, defaultdict, deque
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

PROTOTYPE = Path(__file__).resolve().parents[1] / "prototype"
PRICES = ("low", "base", "high")
SCENARIOS = {
    "normal": (0, 1, 0),
    "delayed-material": (30, 1, 0),
    "reduced-capacity": (0, 0.75, 0),
    "rejected-first-article": (0, 1, 1),
}
SUPPLY_BASIS = {
    "fleet": "sets", "elevated-civil": "beams", "stations": "station_sites",
    "track": "track_km", "traction-line": "track_km", "signalling": "track_km",
    "wayside-braking": "track_km", "traction-sites": "grid_sites", "offsite-feed": "grid_sites",
    "land-utilities": "track_km", "extra-haul": "beams", "opex-feeder": "grid_sites",
    "renewal-grid-site-power-electronics": "grid_sites",
    "renewal-fleet-major-renewal": "sets", "renewal-line-section-protection": "track_km",
    "renewal-line-power-equipment": "track_km", "renewal-common-signalling-and-brake": "track_km",
    "renewal-midpoint-tie-equipment": "track_km",
}
# Route loads inherited from factory-routes are occupied hours. Other entries
# are explicit planning assumptions where the predecessor route has a hold.
EXTRA_CAPACITY = {
    "civil-placement": 1, "civil-foundation": 2, "civil-panel-table": 4,
    "civil-panel-hook": 1, "wayside-power-test": 1, "vehicle-delivery": 2,
    "vehicle-staff": 8, "civil-staff": 18, "wayside-staff": 3,
}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def sources():
    names = ("factory-routes.json", "shop-costs.json", "sourcing-estimate.json", "cam/cam-manifest.json")
    raw = {name: (PROTOTYPE / name).read_bytes() for name in names}
    routes, shop, estimate, cam = (json.loads(raw[name]) for name in names)
    for key in ("candidate_id", "frame_revision", "opening_evaluation_id"):
        if len({doc[key] for doc in (routes, shop, estimate, cam)}) != 1:
            raise ValueError(f"Mixed production sources for {key}")
    if shop["factory_evaluation_id"] != routes["evaluation_id"] or any(
        doc["estimate_evaluation_id"] != estimate["evaluation_id"] for doc in (routes, shop)
    ):
        raise ValueError("Mixed workshop and buyer estimate revisions")
    cam_rows = {}
    for name in ("saw-stock.csv", "saw-cuts.csv", "sheet-schedule.csv", "sheet-placements.csv"):
        path = "cam/" + name
        raw[path] = (PROTOTYPE / path).read_bytes()
        if cam["artifact_sha256"][name] != digest(raw[path]):
            raise ValueError(f"Stale CAM file {path}")
        cam_rows[name] = list(csv.DictReader(io.StringIO(raw[path].decode())))
    plate_areas = {}
    for part in cam["blank_quantities"]:
        path = f"cam/parts/{part}.dxf"
        data = (PROTOTYPE / path).read_bytes()
        if digest(data) != cam["artifact_sha256"][f"parts/{part}.dxf"]:
            raise ValueError(f"Stale CAM profile {path}")
        raw[path] = data
        lines = data.decode().splitlines()
        tags = list(zip(lines[::2], lines[1::2]))
        xs = [float(value) for group, value in tags if group == "10"]
        ys = [float(value) for group, value in tags if group == "20"]
        xy = list(zip(xs, ys, strict=True))
        plate_areas[part] = abs(sum(a[0] * b[1] - a[1] * b[0] for a, b in zip(xy, xy[1:] + xy[:1]))) / 2
    cam_rows["plate_areas_mm2"] = plate_areas
    with zipfile.ZipFile(PROTOTYPE / "airport-prototype.zip") as packet:
        for name in ("opening.json", "civil-article.json"):
            data = packet.read(name)
            if digest(data) != routes["drawing_member_sha256"][name]:
                raise ValueError(f"Production archive member has changed: {name}")
            raw["airport-prototype.zip:" + name] = data
    opening = json.loads(raw["airport-prototype.zip:opening.json"])
    civil = json.loads(raw["airport-prototype.zip:civil-article.json"])
    return routes, shop, estimate, cam_rows, opening, civil, {key: digest(value) for key, value in raw.items()}


def reference_quantities(routes):
    d = routes["opening_drivers"]
    return {
        "sets": 6, "cars": int(d["Braced steel body"]), "bogies": int(d["Removable powered bogie"]),
        "beams": int(d["beam_count"]), "piers": int(d["pier_foundation_count"]),
        "bearings": int(d["bearing_unit_allowance"]), "station_sites": int(d["passenger station sites"]),
        "grid_sites": int(d["dc_source_groups"]), "track_km": d["protected_track_km"],
        "gateways": int(d["grid_protection_gateways"] + d["section_control_gateways"] + d["station_dispatch_controllers"]),
        "station_panels": None, "rectifier_cabinets": None,
    }


def cam_stock(rows, cars, reference_cars, reject):
    # Bars and sheets are rounded individually by pattern. Mixed-sheet jobs
    # must be counted once per sheet layout.
    bars = rows["saw-stock.csv"]
    patterns = {r["layout"]: r for r in rows["sheet-schedule.csv"]}
    ratio = (cars + reject) / reference_cars
    counts = {r["pattern"]: math.ceil(int(r["bars"]) * ratio) for r in bars}
    sheets = {name: math.ceil(int(r["sheets"]) * ratio) for name, r in patterns.items()}
    raw_mm = sum(counts[r["pattern"]] * int(r["raw_length_mm"]) for r in bars)
    cut_mm = sum(counts[r["pattern"]] * float(r["length_mm"]) for r in rows["saw-cuts.csv"])
    plate_gross = sum(sheets[name] * int(r["sheet_x_mm"]) * int(r["sheet_y_mm"])
                      for name, r in patterns.items())
    plate_net = sum(rows["plate_areas_mm2"][r["part"]] * sheets[r["layout"]] for r in rows["sheet-placements.csv"])
    return {
        "gross_saw_bars": sum(counts.values()), "gross_saw_stock_m": raw_mm / 1000,
        "saw_blank_length_yield": cut_mm / raw_mm,
        "gross_plate_sheets": sum(sheets.values()),
        "gross_plate_area_m2": plate_gross / 1e6, "plate_area_yield": plate_net / plate_gross,
        "plate_nesting_by_layout": [
            {"layout": name, "sheets": count,
             "parts_per_sheet": {r["part"]: int(r["blanks_per_sheet"]) for r in rows["sheet-schedule.csv"]
                                 if r["layout"] == name}}
            for name, count in sheets.items()
        ],
        "gross_stock_basis": "Rounded archived stock patterns, including first-article scrap replacement",
    }


@dataclass
class Step:
    label: str
    days: float
    needs: dict
    reserve: int = 0
    release: int = 0
    complete: tuple = ()
    hold: tuple = ()
    unhold: tuple = ()


def schedule(jobs, capacity, staged_limit, dependencies):
    """Dispatch FIFO within ready operations, skipping blocked operations."""
    clock = 0.0
    ready, events = defaultdict(deque), []
    ready_count = 0
    waiting = defaultdict(lambda: {"days_total": 0.0, "days_max": 0.0, "starts": 0})
    busy, peak, occupancy, completions, first = Counter(), Counter(), Counter(), Counter(), {}
    resource_days, resource_held_since, peak_backlog = Counter(), {}, Counter()
    staged = peak_staged = 0
    cursor = Counter()
    remaining = {index: len(required) for index, required in dependencies.items()}
    dependents = defaultdict(list)
    for index, required in dependencies.items():
        for prior in required:
            dependents[prior].append(index)
    for index, (release, _) in enumerate(jobs):
        if not remaining.get(index):
            heapq.heappush(events, (release, 0, index))
    while events or ready_count:
        while events and events[0][0] <= clock:
            when, phase, index = heapq.heappop(events)
            step = jobs[index][1][cursor[index]]
            if phase == 1:
                busy.subtract(step.needs)
                for name in step.unhold:
                    busy[name] -= 1
                    resource_days[name] += clock - resource_held_since.pop((index, name))
                if step.complete:
                    kind, units = step.complete
                    completions[kind] += units
                    first.setdefault(kind, clock)
                    occupancy[kind] = clock
                cursor[index] += 1
                if cursor[index] == len(jobs[index][1]):
                    for dependant in dependents[index]:
                        remaining[dependant] -= 1
                        if not remaining[dependant]:
                            heapq.heappush(events, (max(clock, jobs[dependant][0]), 0, dependant))
                    continue
            label = jobs[index][1][cursor[index]].label
            ready[label].append((when, index))
            peak_backlog[label] = max(peak_backlog[label], len(ready[label]))
            ready_count += 1
        for queue in sorted((q for q in ready.values() if q), key=lambda q: q[0]):
            while queue:
                queued, index = queue[0]
                step = jobs[index][1][cursor[index]]
                if staged + step.reserve > staged_limit or any(
                    busy[name] + units > capacity[name]
                    for name, units in (step.needs | dict.fromkeys(step.hold, 1)).items()
                ):
                    break
                queue.popleft()
                ready_count -= 1
                staged += step.reserve - step.release
                peak_staged = max(peak_staged, staged)
                for name, units in (step.needs | dict.fromkeys(step.hold, 1)).items():
                    busy[name] += units
                    peak[name] = max(peak[name], busy[name])
                for name, units in step.needs.items():
                    resource_days[name] += step.days * units
                for name in step.hold:
                    resource_held_since[index, name] = clock
                wait = waiting[step.label]
                wait["days_total"] += clock - queued
                wait["days_max"] = max(wait["days_max"], clock - queued)
                wait["starts"] += 1
                heapq.heappush(events, (clock + step.days, 1, index))
        if not events:
            if ready_count:
                raise ValueError("Production schedule deadlocked with unfinished operations")
            break
        clock = events[0][0]
    if any(remaining.values()):
        raise ValueError("Production schedule has unreleased dependencies")
    if staged or any(busy.values()) or resource_held_since:
        raise ValueError("Production staging inventory or resource bookings failed to reconcile")
    return {
        "last_completion_workday": clock, "first_by_output_workday": first,
        "last_by_output_workday": dict(occupancy), "completed_units": dict(completions),
        "queue_delay": dict(waiting), "peak_resource_occupation": dict(peak),
        "peak_ready_backlog_by_workcell": dict(peak_backlog),
        "occupied_resource_workdays": dict(resource_days),
        "peak_beam_staging_reserved": peak_staged,
    }


@lru_cache(maxsize=64)
def cached_simulation(routes_json, quantities, scenario, span, material):
    return simulate(json.loads(routes_json), dict(quantities), scenario, span, material)


def simulate(routes, q, scenario, span, material):
    delay, availability, reject = SCENARIOS[scenario]
    resources = {r["id"]: r for r in routes["resources"]}
    capacity = {key: r["required_units"] for key, r in resources.items() if r["required_units"]}
    capacity.update(EXTRA_CAPACITY)
    if availability < 1:
        for key in ("vehicle-body-bed", "civil-beam-position", "civil-haul", "vehicle-staff", "civil-staff"):
            capacity[key] = max(1, int(capacity[key] * availability))
    loads = routes["opening_drivers"]
    ref = reference_quantities(routes)

    def task(key, quantities, staff, *, units=1, workers=1, known_hours=None, **effects):
        resource = resources.get(key, {})
        hours = sum(load["hours"] * load.get("multiplier", 1)
                    * sum(quantities.get(item, 0) for item in load["items"])
                    for load in resource.get("load", ())) if known_hours is None else known_hours
        if span != 10 and key in {
            "civil-cage", "civil-placement", "civil-pour-crew", "civil-stress", "civil-yard-hook", "civil-haul",
            "civil-erection",
        } and ("beam_count" in quantities or "lift_count" in quantities):
            hours *= (span / 10) ** 0.3
        if key in {"vehicle-saw", "vehicle-prep", "vehicle-plate-contract", "vehicle-body-bed", "vehicle-arc-set",
                   "vehicle-weld-ndt", "vehicle-metrology"}:
            hours *= {"steel": 1.0, "hybrid": 1.2, "aluminium": 1.35}[material]
        effective_day = resource.get("usable_hours_per_day") or (7 if key.startswith("civil") else 6.4)
        days = hours / (effective_day * availability * units)
        if key in ("civil-beam-position", "civil-panel-table"):
            days = hours / (24 * units * availability)
            workers = 0
        return Step(key, days, {key: units, **({staff: workers} if workers else {})}, **effects)

    def v(key, quantities, **kw):
        return task(key, quantities, "vehicle-staff", **kw)

    def c(key, quantities, **kw):
        return task(key, quantities, "civil-staff", **kw)

    # Allocate shared setups once, before first material release.
    jobs = []
    dependencies = {}
    setup_finish = {}
    for key, r in resources.items():
        hours = sum(row.get("setup_hours", 0) for row in r.get("load", ()))
        if hours:
            staff = "vehicle-staff" if key.startswith("vehicle") else "wayside-staff"
            setup = task(key, {}, staff, known_hours=hours)
            setup_finish[key] = setup.days
            jobs.append((0, [setup]))

    qtruck = {"lift_count": 1}
    for index in range(q["beams"]):
        quantity = {"beam_count": 1, "bearing_unit_allowance":
                    (index + 1) * q["bearings"] // q["beams"] - index * q["bearings"] // q["beams"]}
        prep = c("civil-placement", quantity, hold=("civil-beam-position",))
        cure = c("civil-beam-position", quantity)
        cure.needs = {}
        route = [c("civil-cage", quantity), prep, c("civil-pour-crew", quantity, workers=3),
                 cure, c("civil-stress", quantity),
                 c("civil-yard-hook", quantity, reserve=1, unhold=("civil-beam-position",)),
                 c("civil-haul", qtruck, release=1),
                 c("civil-bearing", quantity), c("civil-erection", qtruck, complete=("installed_beams", 1))]
        foundation_count = (index + 1) * q["piers"] // q["beams"] - index * q["piers"] // q["beams"]
        if foundation_count:
            route.insert(-1, c("civil-foundation", {}, known_hours=1.75 * foundation_count,
                               workers=3, complete=("pier_positions_assumed", foundation_count)))
        jobs.append((delay + index // 8, route))

    body = {item: amount / ref["cars"] for item, amount in loads.items() if amount is not None}
    body.update({"Braced steel body": 1, "Removable powered bogie": q["bogies"] / q["cars"]})
    car_jobs = []
    article_gate = len(jobs)
    for index in range(q["cars"]):
        car = dict(body)
        bogies = (index + 1) * q["bogies"] // q["cars"] - index * q["bogies"] // q["cars"]
        car["Removable powered bogie"] = bogies
        for item in ("Wheelset", "Axlebox bearing positions", "Axle drive module", "Brake controller",
                     "Primary spring interface", "Secondary spring interface"):
            car[item] = body[item] * bogies / (ref["bogies"] / ref["cars"])
        route = [v(key, car, workers=2 if key in ("vehicle-body-bed", "vehicle-bogie-bed", "vehicle-fit") else 1)
                 for key in ("vehicle-stores", "vehicle-saw", "vehicle-prep", "vehicle-plate-contract",
                             "vehicle-body-bed", "vehicle-bogie-bed", "vehicle-arc-set", "vehicle-weld-ndt",
                             "vehicle-metrology", "vehicle-bogie-machine", "vehicle-shop-crane", "vehicle-bearings",
                             "vehicle-bogie-fit", "vehicle-bogie-test", "vehicle-coat", "vehicle-door-fixture",
                             "vehicle-fit", "vehicle-electric", "vehicle-harness-test", "vehicle-collector-tools",
                             "vehicle-marriage", "vehicle-end-test")]
        release = max(setup_finish.values()) + delay + 5 * index
        if index == 0:
            # The first inspected article remains on the way to the first car
            # after approval. Rejection scraps that first article and runs
            # a second inspection sequence before serial release.
            article = route[:11]
            if reject:
                article = article + [v("vehicle-repair", car, known_hours=16, complete=("rejected_articles", 1))] + article
            jobs.append((release, article))
            route = route[11:]
        car_jobs.append(len(jobs))
        dependencies[len(jobs)] = [article_gate]
        jobs.append((release, route + [
            v("vehicle-delivery", car, known_hours=16, complete=("delivered_cars", 1)),
        ]))
    formation = q["cars"] // q["sets"]
    for start in range(0, q["cars"], formation):
        dependencies[len(jobs)] = car_jobs[start:start + formation]
        jobs.append((0, [v("vehicle-set-test", {"atp_channels": 2}, complete=("proved_sets", 1))]))

    for index in range(q["gateways"]):
        gateway = "station_dispatch_controllers" if index < q["station_sites"] else "section_control_gateways"
        stages = [task(key, {gateway: 1}, "wayside-staff", **effects) for key, effects in (
            ("wayside-assembly", {}), ("wayside-wire", {}), ("wayside-test", {"complete": ("tested_gateways", 1)}),
        )]
        jobs.append((max(setup_finish.values()) + delay + index // 4, stages))
    for index in range(q["station_panels"] or 0):
        panel = {"station bay panels after plant and access openings": 1}
        jobs.append((delay + index // 4, [c("civil-placement", panel), c("civil-panel-table", panel),
                                          c("civil-panel-hook", panel, complete=("station_panels", 1))]))
    for index in range(q["rectifier_cabinets"] or 0):
        cabinet = {"installed and tested rectifier cabinets": 1}
        jobs.append((delay + index // 2, [task("wayside-power-test", cabinet, "wayside-staff",
                                               complete=("tested_rectifier_cabinets", 1))]))
    output = schedule(jobs, capacity, capacity["civil-stock-position"], dependencies)
    return {"material_delay_workdays": delay, "availability_factor": availability,
            "capacity": capacity, "calendar_basis": "Effective resource workdays with concurrent shop calendars",
            "crew_and_cell_availability": "Resource capacities include assumed staffing, shifts and availability",
            "span_workload_factor": (span / 10) ** 0.3,
            "first_article_scrap_gate": bool(reject), **output}


def capital_and_operations(estimate, q, reference, inputs):
    lots = {row["lot_id"]: row for row in estimate["lots"]}
    topology = inputs.get("topology", "radial30")
    span = inputs.get("span_m", 10)
    material = inputs.get("material", "steel")
    paired = topology == "paired6"
    dropped = set()
    if paired:
        dropped.update(lots["six-site-parallel"]["alternative_to_lot_ids"])
        dropped.update(lots["six-site-parallel-upkeep"]["alternative_to_lot_ids"])
        dropped.update(("renewal-grid-site-power-electronics", "renewal-line-section-protection",
                        "renewal-line-power-equipment", "renewal-midpoint-tie-equipment"))
    allowed = {"opening-direct", "first-full-year-operations", "renewal-schedule"}
    rows = []
    for key, row in lots.items():
        replacement = paired and key in ("six-site-parallel", "six-site-parallel-upkeep")
        if key in dropped or (row["inclusion_group"] not in allowed and not replacement):
            continue
        group = row["inclusion_group"]
        factor = dict.fromkeys(PRICES, 1.0)
        driver = SUPPLY_BASIS.get(key)
        quantity = row["quantity"]
        if driver:
            quantity = q[driver]
            factor = dict.fromkeys(PRICES, quantity / reference[driver])
        if key in {"fleet", "renewal-fleet-major-renewal"}:
            # Planning proxy: 20% of set cost is fixed and the remaining work
            # follows cars per set. Material premium applies to 25% body scope.
            formation = q["cars"] / (q["sets"] * 6)
            premiums = {"steel": (1, 1, 1), "hybrid": (1.15, 1.4, 1.85), "aluminium": (1.3, 1.6, 2.2)}
            factor = {case: factor[case] * (0.2 + 0.8 * formation) * (0.75 + 0.25 * premium)
                      for case, premium in zip(PRICES, premiums[material])}
        if key == "elevated-civil" and span != 10:
            # Allocate 65% to superstructure per track-km and 35% to supports.
            # Longer span multipliers are analyst stress assumptions.
            factor = {case: 0.65 * q["track_km"] / reference["track_km"] * (span / 10) ** power
                            + 0.35 * q["piers"] / reference["piers"]
                      for case, power in zip(PRICES, (0.05, 0.20, 0.45))}
        if key == "opex-power" and "annual_train_km" in inputs and "energy_kwh_per_train_km" in inputs:
            quantity = inputs["annual_train_km"] * inputs["energy_kwh_per_train_km"] / 1e6
            factor = dict.fromkeys(PRICES, quantity / row["source_quantity"])
        if key == "opex-other" and "annual_train_km" in inputs:
            mileage = inputs["annual_train_km"] / 646488
            factor = {case: 1 + (mileage - 1) * share for case, share in zip(PRICES, (0.20, 0.10, 0.05))}
            factor = dict(zip(PRICES, sorted(factor.values()))) if mileage > 1 else factor
        if replacement:
            group = "opening-direct" if key == "six-site-parallel" else "first-full-year-operations"
        rows.append({
            "lot_id": key, "group": group, "quantity": quantity, "quantity_driver": driver,
            "source_quantity": row["quantity"], "source_unit": row["unit"],
            "year": row.get("operating_year"), "source": row["sources"],
            "factor": factor, "usd": {case: row[f"{case}_usd"] * factor[case] for case in PRICES},
        })
    return rows, sorted(dropped)


def cash_profile(rows, service_year, paid_journeys, fare, stress):
    """Cash timing uses relative years and 30 full years of operations."""
    import random
    from statistics import quantiles

    def sums(group, case):
        return sum(row["usd"][case] for row in rows if row["group"] == group)

    def annual(case):
        direct = sums("opening-direct", case)
        capital = direct * (1 + 0.08 + 0.025) * 1.2
        opex = sums("first-full-year-operations", case)
        receipts = paid_journeys * fare
        renewals = {
            y: sum(row["usd"][case] for row in rows if row["group"] == "renewal-schedule" and row["year"] == y)
            for y in range(1, 31)
        }
        out = []
        cap_draw = {1: 0.20, math.ceil(service_year / 2): 0.45, service_year - 1: 0.35}
        if service_year == 4:
            cap_draw = {1: 0.20, 2: 0.45, 3: 0.35}
        for year in range(1, service_year + 30):
            operating_year = year - service_year + 1
            out.append({
                "year": year, "capital_usd": capital * cap_draw.get(year, 0),
                "opex_usd": opex if operating_year >= 1 else 0,
                "fare_usd": receipts if operating_year >= 1 else 0,
                "renewals_usd": renewals.get(operating_year, 0),
            })
        pv = sum((r["capital_usd"] + r["opex_usd"] + r["renewals_usd"]) / 1.04 ** r["year"] for r in out)
        return {"capital_usd": capital, "annual_opex_usd": opex, "annual_fares_usd": receipts,
                "annual_operating_support_usd": opex - receipts,
                "annual_subsidy_per_paid_journey_usd": (opex - receipts) / paid_journeys if paid_journeys else None,
                "priced_30y_pv_usd": pv, "cash_by_year": out}

    profiles = {case: annual(case) for case in PRICES}
    rng = random.Random(80409)
    pv_samples, support_samples, starts = [], [], []
    # Shared draw correlates adverse equipment prices, operating inputs and
    # releases. Demand has an additional scenario-dependent residual.
    for _ in range(256):
        shared = rng.triangular(-1, 1, 0)
        demand_residual = rng.triangular(-0.1, 0.1, 0)
        tail = profiles["high" if shared >= 0 else "low"]
        amount = abs(shared)
        base = profiles["base"]
        slip = int(shared >= 0.55 and stress)
        starts.append(service_year + slip)
        shifted = 0
        for row, other in zip(base["cash_by_year"], tail["cash_by_year"]):
            capital = row["capital_usd"] + amount * (other["capital_usd"] - row["capital_usd"])
            future = sum(row[k] + amount * (other[k] - row[k]) for k in ("opex_usd", "renewals_usd"))
            shifted += capital / 1.04 ** row["year"] + future / 1.04 ** (row["year"] + slip)
        pv_samples.append(shifted)
        exposure = base["annual_opex_usd"] + amount * (tail["annual_opex_usd"] - base["annual_opex_usd"])
        support_samples.append(exposure - base["annual_fares_usd"] * (1 - shared * 0.2 + demand_residual))
    return {
        "constant_currency": "2026 USD", "discount_rate_real": 0.04, "service_start_year": service_year,
        "profiles": profiles, "sensitivity": {
            "seed": 80409, "samples": 256, "quantiles": [0.1, 0.5, 0.9],
            "priced_30y_pv_usd": quantiles(pv_samples, n=10)[::4],
            "annual_operating_support_usd": quantiles(support_samples, n=10)[::4],
            "service_start_year_counts": dict(Counter(starts)),
            "basis": "Illustrative correlated stress distribution, uncalibrated against offers or disruption histories",
        },
    }


def localisation(shop, q, reference):
    """Report addresses for local work and equipment spending within parent lots."""
    groups = defaultdict(list)
    for row in shop["resources"]:
        rate = row["extended_usd"]
        driver = ("cars" if row["id"].startswith("vehicle") else
                  "beams" if row["id"].startswith("civil") else "gateways")
        factor = 1 if row["basis"] == "units" else q[driver] / reference[driver]
        groups[row["period"]].append({
            "id": row["id"], "parent_lot": row["lot_id"], "quantity_status": row["quantity_status"],
            "addressable_planning_usd": {case: rate[case] * factor for case in PRICES} if rate else None,
            "candidate_quantity_factor": factor, "verified_domestic_origin_value_usd": None,
        })
    training = shop["cam_and_training_scenario"]
    return {
        "addressable_workshop_scope_by_period": dict(groups),
        "addressable_includes": ["workholding, machines and racks", "local labour, hire and plant service opportunities",
                                 "manufacturing programming, instruction and first-off skills"],
        "skills_and_cam_addressable_usd": training["period_subtotals_usd"],
        "verified_domestic_origin_value_usd": None, "verified_domestic_share": None,
        "proof_required": ["itemised supplier and subcontractor origin ledger", "local labour and overhead evidence",
                           "imported equipment and stock cost separation", "matched invoices and manufacturing records"],
        "scope_credits": {
            "approved_usd": None,
            "method": "Carry equipment, labour and services under the sourcing lots. Addressable workshop and training schedules are breakdowns and do not add to programme cash.",
            "open_parent_lot_allocations": shop["lot_allocations"],
            "first_article": "Qualification/pilot breakdowns are inside their parent allowances pending matched returns.",
        },
    }


def evaluate(inputs=None):
    """Return a deterministic planning receipt for one Baghdad Airport case."""
    inputs = dict(inputs or {})
    routes, shop, estimate, cam, opening, civil, hashes = sources()
    candidate_id = routes["candidate_id"]
    if inputs.get("candidate_id", candidate_id) != candidate_id or inputs.get(
        "opening_evaluation_id", routes["opening_evaluation_id"]
    ) != routes["opening_evaluation_id"]:
        raise ValueError("Production inputs must originate from the pinned Baghdad Airport candidate and evaluation")
    ref = reference_quantities(routes)
    supplied = dict(inputs.get("quantities", {}))
    if supplied.keys() - ref.keys():
        raise ValueError(f"Unknown production quantities: {sorted(supplied.keys() - ref.keys())}")
    q = {**ref, **supplied}
    if "sets" in inputs:
        if "sets" in supplied and supplied["sets"] != inputs["sets"]:
            raise ValueError("Fleet size conflicts with the supplied quantity bundle")
        q["sets"] = inputs["sets"]
    if "sets" in inputs or "cars" in inputs:
        total = inputs.get("cars", 6) * q["sets"]
        if "cars" in supplied and supplied["cars"] != total:
            raise ValueError("Formation conflicts with the supplied total cars")
        q["cars"] = total
        if "bogies" not in supplied:
            q["bogies"] = 2 * q["cars"]
    topology = inputs.get("topology", "radial30")
    if topology == "paired6":
        q["grid_sites"] = supplied.get("grid_sites", 6)
        q["gateways"] = supplied.get("gateways", 20 + 6 + q["station_sites"])
    span = inputs.get("span_m", 10)
    if span != 10:
        q["beams"] = supplied.get("beams", math.ceil(q["track_km"] * 1000 / span))
        q["piers"] = supplied.get("piers", q["beams"] + 2)
        q["bearings"] = supplied.get("bearings", q["beams"] * 4)
    if (inputs.get("material", "steel") not in {"steel", "aluminium", "hybrid"} or
        topology not in {"radial30", "paired6"} or span not in {10, 20, 25, 30}):
        raise ValueError("Production material, topology or span is outside the proxy domain")
    if any(type(n) not in (int, float) or not math.isfinite(n) or n <= 0
           or (key != "track_km" and type(n) is not int)
           for key, n in q.items() if key not in ("station_panels", "rectifier_cabinets") or n is not None):
        raise ValueError("Production requires positive integer counts and a positive track length")
    if (q["cars"] % q["sets"] or q["cars"] // q["sets"] not in (3, 6)
        or q["bogies"] != 2 * q["cars"] or q["grid_sites"] != (6 if topology == "paired6" else 30)):
        raise ValueError("Production quantities conflict with formation, running gear or feeder topology")
    if inputs.get("scenario_id") is None and (q != ref or span != 10 or inputs.get("material", "steel") != "steel"):
        raise ValueError("Alternative quantities require a distinct scenario_id")
    for key in ("annual_train_km", "energy_kwh_per_train_km", "loaded_train_kg"):
        if key in inputs and (type(inputs[key]) not in (int, float) or
                              not math.isfinite(inputs[key]) or inputs[key] < 0):
            raise ValueError(f"Production requires a finite nonnegative {key}")
    results = {}
    material = inputs.get("material", "steel")
    raw_routes = json.dumps(routes)
    for name, (_, _, reject) in SCENARIOS.items():
        result = copy.deepcopy(cached_simulation(raw_routes, tuple(sorted(q.items())), name, span, material))
        result["stock"] = cam_stock(cam, q["cars"], ref["cars"], reject)
        result["stock"]["design_status"] = ("steel-pattern analogue; material-specific CAM pending"
                                               if inputs.get("material", "steel") != "steel" else "archived steel stock")
        results[name] = result
    rows, omitted = capital_and_operations(estimate, q, ref, inputs)
    start = max(4, 1 + math.ceil(results["normal"]["last_completion_workday"] / 250))
    open_items = ["Installed supplier offers, importer origin and taxes", "Station panels and rectifier quantities and return rates",
                  "Independent acceptance, geotechnical work, approvals and funded opening cost"]
    if q != ref:
        open_items.append("Revised production quantities, work content, phasing and prices require independent returns")
    if span != 10:
        open_items.append("Span-specific reinforcement, lift/haul limits, mould occupancy, foundations and installation")
    if inputs.get("material", "steel") != "steel":
        open_items.append("Material-specific stock, labour, joining, assurance and installed body quantities")
    if topology == "paired6":
        open_items.append("Paired feeder renewal scope and maintenance boundary")
    historical_operation = opening["iraq_operations"]["cases"]["central"]
    paid = inputs.get("annual_paid_journeys", historical_operation["paid_journeys"])
    if paid is None:
        paid = 0
    if not math.isfinite(paid) or paid < 0:
        raise ValueError("Paid journeys require a finite nonnegative count")
    fare = historical_operation["net_farebox_usd_m"] * 1e6 / historical_operation["paid_journeys"]
    cash = cash_profile(rows, start, paid, fare, any(
        value["last_completion_workday"] > 250 * (start - 1) for value in results.values()))
    cash["disruption_phasing"] = {}
    for name, result in results.items():
        opening_year = max(4, 1 + math.ceil(result["last_completion_workday"] / 250))
        profile = cash["profiles"]["base"] if opening_year == start else cash_profile(
            rows, opening_year, paid, fare, False)["profiles"]["base"]
        cash["disruption_phasing"][name] = {
            "service_start_year": opening_year, "priced_30y_pv_usd": profile["priced_30y_pv_usd"],
            "cash_by_year": profile["cash_by_year"],
            "additional_disruption_cost_usd": None,
        }
    base = cash["profiles"]["base"]
    receipt = {
        "candidate_id": candidate_id, "opening_evaluation_id": routes["opening_evaluation_id"],
        "scenario_id": inputs.get("scenario_id", "airport-reference"), "source_sha256": hashes,
        "method_sha256": digest(Path(__file__).read_bytes()), "inputs": inputs, "quantities": q,
        "scenarios": results, "cash": cash, "priced_lots": rows,
        "civil_material_quantities": {
            "reinforcement_and_strand_reference_kg_per_10m_beam": civil["bar_and_strand_kg_per_beam"],
            "reinforcement_and_strand_planning_kg_range": [
                q["beams"] * civil["bar_and_strand_kg_per_beam"] * (span / 10) ** exponent
                for exponent in ((1, 1, 1) if span == 10 else (1, 1.4, 2))
            ],
            "station_panel_concrete_m3_if_reference_sections":
                None if q["station_panels"] is None else q["station_panels"] * civil["station_panels"]["concrete_m3_per_panel"],
            "basis": "Reference bar schedule only. Alternative span power laws are stock stress assumptions.",
        },
        "displaced_or_open_source_lots": omitted, "localisation": localisation(shop, q, ref),
        "acquisition_dependencies": [
            {"inputs": "steel bars and plates, wheels/axle drives, doors and electrical cases",
             "gate": "first article and serial fabrication", "signed_available_date": None},
            {"inputs": "bearing packages, moulds, cages and prestressing stock",
             "gate": "beam release, haul and site installation", "signed_available_date": None},
            {"inputs": "metered grid and controls packages",
             "gate": "cabinet integration and commissioning", "signed_available_date": None},
        ],
        "decision_summary": {
            "priced_capital_base_usd": base["capital_usd"], "annual_opex_base_usd": base["annual_opex_usd"],
            "annual_subsidy_per_paid_journey_base_usd": base["annual_subsidy_per_paid_journey_usd"],
            "priced_30y_pv_base_usd": base["priced_30y_pv_usd"],
            "normal_last_modelled_completion_workday": results["normal"]["last_completion_workday"],
            "open_components": open_items,
        },
        "physical_acceptance": "open", "complete_installed_price_usd": None,
    }
    receipt["evaluation_id"] = digest(json.dumps(receipt, sort_keys=True, allow_nan=False).encode())
    return receipt


if __name__ == "__main__":
    print(json.dumps(evaluate(), indent=2, sort_keys=True))
