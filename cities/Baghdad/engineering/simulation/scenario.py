"""Evaluate one Airport operating case, reusing only source-matched subsystem results."""
import argparse
from hashlib import sha256
import resource
from tempfile import TemporaryDirectory
import json
import math
from pathlib import Path
import platform
import sys
import time
from zipfile import ZipFile

from cities.Baghdad.airport_integration import write_atomic
from cities.Baghdad.engineering.prototype.review import archive
from cities.Baghdad.engineering.simulation import corridor, motion_power, passengers, production, vehicle_civil
from engineering.design_search.storage import atomic_immutable
from engineering.outline.baghdad_system import _id
from engineering.performance import disk_reservation

HERE = Path(__file__).resolve().parent
CITY = HERE.parents[1]
ROOT = CITY.parents[1]
PROTO = HERE.parent / "prototype"
PACKET = PROTO / "airport-prototype.zip"
CACHE = ROOT / "build/airport-scenario-cache"
CHOICES = dict(headway_min=(15, 20, 30), cars=(6, 3), material=("steel", "aluminium", "hybrid"),
               span_m=(10, 20, 25, 30), topology=("radial30", "paired6"),
               demand=("central", "downside", "upside"), ambient_c=(40, 32, 48),
               grade_pct=(0, 1, 2), condition=("normal", "hot", "site_out", "path_out", "combined"))


def encode(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=True, allow_nan=False, separators=(",", ":")).encode()


def sha(raw):
    return sha256(raw).hexdigest()


def selections(values):
    if not isinstance(values, dict) or values.keys() - CHOICES.keys():
        raise ValueError("Unknown Airport scenario input")
    result = {}
    for key, options in CHOICES.items():
        value = values.get(key, options[0])
        if type(value) is not type(options[0]) or value not in options:
            raise ValueError(f"Choose {key} from {options}")
        result[key] = value
    return result


def read_bound_sources():
    with ZipFile(PACKET) as packet:
        manifest = json.loads(packet.read("manifest.json"))
        public = {}
        for name in ("opening.json", "service.json", "mechanical.json", "civil-article.json", "revised-cuts.csv",
                     "fitout-interfaces.json", "returns/handover-logger.json"):
            raw = packet.read(name)
            if sha(raw) != manifest["sha256"][name]:
                raise ValueError(f"Airport prototype changed: {name}")
            if name.endswith(".json"):
                public[name] = json.loads(raw)
    opening = public["opening.json"]
    if manifest["candidate_id"] != opening["candidate_id"] or opening["bundle"]["stops"] != [s["id"] for s in public["service.json"]["patterns"][0]]:
        raise ValueError("Opening and service editions do not match")
    return manifest, public


def source_hashes(paths):
    return {p.relative_to(ROOT).as_posix(): sha(p.read_bytes()) for p in sorted(set(paths))}


def source_contract(manifest):
    member = manifest["sha256"]
    # Use separate recipe keys. Buying a machine cannot invalidate a timetable.
    def inputs(paths, members=()):
        return {**source_hashes(paths), **{"prototype:" + m: member[m] for m in members}}
    register = CITY / "station-register.json"
    map_files = [ROOT / p for p in json.loads(register.read_bytes())["map_source_sha256"]]
    review_path = CITY / "maps/corridor-review.geojson"
    review_files = [ROOT / name for name in json.loads(review_path.read_bytes())["source_sha256"]]
    blank_names = json.loads((PROTO / "cam/cam-manifest.json").read_bytes())["blank_quantities"]
    system = CITY / "system.toml"
    trial = CITY / "engineering/mechanical/vehicle/section-trial.toml"
    city_reports = [CITY / p for p in ("service-diagrams.json", "system-results.json")]
    report_files = set()
    for path in city_reports:
        report_files.update(ROOT / name for name in json.loads(path.read_bytes()).get("source_sha256", {}))
    return {
        "corridor": inputs([HERE / "corridor.py", register, *map_files], ("service.json", "opening.json")),
        "vehicle": inputs([HERE / "vehicle_civil.py", system, PROTO / "vehicle-factory/installed-ga.json",
                           PROTO / "weights.py", CITY / "engineering/mechanical/civil/concept.toml", CITY / "engineering/mechanical/civil/develop_civil.py"],
                          ("mechanical.json", "civil-article.json", "revised-cuts.csv")),
        "passengers": inputs([HERE / "passengers.py", passengers.SYSTEM, passengers.TRIAL, passengers.DOOR]),
        "motion": inputs([HERE / "motion_dc.py", HERE / "motion_power.py", system, trial, register,
                          *city_reports, *report_files, *map_files, review_path, *review_files,
                          HERE.parent / "mechanical/compare_returns.py", CITY / "airport_opening.py", CITY / "airport_service.py",
                          CITY / "engineering/commissioning/feeder.py", ROOT / "engineering/outline/baghdad_diagrams.py",
                          ROOT / "engineering/outline/baghdad_system.py"], ("opening.json", "service.json")),
        "production": inputs([HERE / "production.py", PROTO / "factory-routes.json", PROTO / "shop-costs.json",
                              PROTO / "sourcing-estimate.json", *(PROTO / "cam/parts" / (name + ".dxf") for name in blank_names),
                              *(PROTO / "cam" / n for n in
                              ("cam-manifest.json", "saw-stock.csv", "saw-cuts.csv", "sheet-schedule.csv", "sheet-placements.csv"))],
                             ("opening.json", "civil-article.json")),
    }


def stage(name, args, sources, engine, cache, runs):
    key = _id(dict(stage=name, recipe=3, python=platform.python_version(), inputs=args, sources=sources))
    path = None if cache is None else Path(cache) / name / (key + ".json")
    start = time.perf_counter()
    hit = path is not None and path.is_file()
    if hit:
        record = json.loads(path.read_bytes())
        if record["key"] != key or _id(record["value"]) != record["digest"]:
            raise ValueError("Damaged Airport cache entry " + str(path))
        value = record["value"]
    else:
        value = json.loads(encode(engine(args)))
        if path:
            path.parent.mkdir(parents=True, exist_ok=True)
            atomic_immutable(path, encode(dict(key=key, digest=_id(value), value=value)))
    runs[name] = dict(key=key, reused=hit, wall_s=round(time.perf_counter() - start, 5),
                      stored_bytes=path.stat().st_size if path else None)
    return value


def run_case(values=None, *, cache=CACHE, runs=None):
    cfg = selections({} if values is None else values)
    runs = {} if runs is None else runs
    manifest, data = read_bound_sources()
    opening = data["opening.json"]
    parent = opening["candidate_id"]
    bindings = source_contract(manifest)

    def get(name, args, engine):
        return stage(name, args, bindings[name], engine, cache, runs)

    def subset(*keys):
        return {key: cfg[key] for key in keys}

    route = get("corridor", subset("demand", "grade_pct", "cars", "headway_min"), corridor.evaluate)
    vehicle = get("vehicle", subset("cars", "material", "span_m"), vehicle_civil.evaluate)
    if route["parent_candidate_id"] != parent or vehicle["parent_candidate_id"] != parent:
        raise ValueError("Vehicle or corridor belongs to another Airport issue")
    climate = get("passengers", dict(**subset("cars", "headway_min", "ambient_c"),
                                busiest_departure_load=min(700 * cfg["cars"] // 6, math.ceil(route["busiest_departure_load"])),
                                platform_queue=math.ceil(route["platform_queue"])), passengers.evaluate)
    # All revenue movements include an assisted transfer allowance at intermediate stops.
    dwell = max(route["dwell_s"], math.ceil(climate["door_exchange"]["total_dwell_with_one_assisted_transfer_s"]))
    motion_inputs = dict(**subset("cars", "material", "topology", "condition", "headway_min", "grade_pct"),
                         loaded_train_kg=vehicle["loaded_train_kg"], tare_train_kg=vehicle["tare_train_kg"],
                         hourly_od=route["hourly_od"], chainages_km=route["chainages_km"],
                         dwell_s=dwell, auxiliary_kw=climate["auxiliary_kw"])
    motion = get("motion", motion_inputs, motion_power.evaluate)
    if motion["source_publication_candidate_id"] != parent or motion["source_opening_evaluation_id"] != opening["evaluation_id"]:
        raise ValueError("Motion solver returned a different Airport candidate or opening")
    # Annual accounts use the ordinary service day. An outage day is a separate operating test.
    ordinary = motion
    if cfg["condition"] != "normal":
        normal_run = {}
        ordinary = stage("motion", dict(motion_inputs, condition="normal"), bindings["motion"],
                         motion_power.evaluate, cache, normal_run)
        runs["ordinary-motion"] = normal_run["motion"]
    physical = dict(parent=parent, fleet_sets=ordinary["metrics"]["fleet_sets_required"], **subset("cars", "material", "span_m", "topology"), vehicle=vehicle["physical_id"])
    physical_id = _id(physical)
    normal_metrics = ordinary["metrics"]
    served_share = max(0., 1 - normal_metrics["unserved_passengers"] / (route["annual_all_journeys"] / 365))
    factory_args = dict(**subset("cars", "material", "span_m", "topology"), candidate_id=parent,
                        opening_evaluation_id=opening["evaluation_id"], scenario_id=physical_id,
                        sets=normal_metrics["fleet_sets_required"], loaded_train_kg=vehicle["loaded_train_kg"],
                        annual_train_km=ordinary["annual_train_km"], energy_kwh_per_train_km=ordinary["energy_kwh_per_train_km"],
                        annual_paid_journeys=route["annual_paid_journeys"] * served_share)
    factory = get("production", factory_args, production.evaluate)
    if factory["scenario_id"] != physical_id or factory["candidate_id"] != parent:
        raise ValueError("Factory/cash result differs from the active Airport configuration")
    controls = json.loads((HERE / "controls-replay.json").read_bytes())
    if (controls["physical"] != parent or controls["opening"] != opening["evaluation_id"] or
            source_hashes([ROOT / p for p in controls["source_sha256"]]) != controls["source_sha256"]):
        raise ValueError("Replay controls for this opening and software revision")
    holds = sorted(k for k, passed in motion["gates"].items() if not passed)
    if min(vehicle["selected_span"]["effective_strand_margin_kn_by_loss"].values()) < 0:
        holds.append("prestress service margin")
    if vehicle["interfaces"]["aged_80pct_capacity_margin_kwh"] < 0:
        holds.append("aged essential battery capacity")
    if vehicle["selected_span"]["eccentric_footing_max_kpa"] > 200:
        holds.append("foundation bearing pressure against trial 200 kPa")
    if climate["hvac"]["trial_thermal_margin_kw"] < 0:
        holds.append("trial cooling capacity at the selected outdoor temperature")
    if vehicle["interfaces"]["brake_adhesion_at_0p08_margin"] < 0:
        holds.append("braking at low adhesion on a two-percent downgrade")
    if cfg["cars"] != 6:
        holds.append("formation-specific Rust station replay")
    holds.extend(["surveyed alignment and entrances", "independently approved installed fits and braking limits",
                  "station evacuation and smoke tenability", "controlled first article and supplier returns"])
    costs = factory["decision_summary"]
    stages = dict(corridor=route, vehicle=vehicle, passengers=climate, motion=motion, production=factory)
    evidence = {k: _id(v) for k, v in stages.items()}
    identity = dict(parent_candidate_id=parent, physical_id=physical_id, selection="research comparison",
                    evaluation_id=_id(dict(cfg=cfg, evidence=evidence, controls=controls, integration=sha(Path(__file__).read_bytes()))))
    return dict(schema="osr-airport-simulation/1", inputs=cfg, identity=identity, stages=stages,
                decision=dict(capital_usd=costs["priced_capital_base_usd"], annual_opex_usd=costs["annual_opex_base_usd"],
                              annual_train_km=ordinary["annual_train_km"], minimum_voltage_v=motion["metrics"]["minimum_collector_v"],
                              peak_power_mw=motion["peak_power_mw"], eligible=not holds, holds=holds),
                provenance=dict(sources=bindings, stage_result_ids=evidence, physical=physical,
                                controls=controls, assisted_dwell_s=dwell, ordinary_motion_id=ordinary["evaluation_id"],
                                financial_basis="Annualised ordinary service; outage days tested separately. Paid share scaled by unserved physical journeys.",
                                physical_acceptance=False, fabrication_release=False, funded_opening_date=None))


def compact(result):
    """A small offline decision card includes actual samples, workdays and engineering margins."""
    s = result["stages"]
    m = s["motion"]
    return dict(inputs=result["inputs"], identity=result["identity"], decision=result["decision"],
                provenance={k: result["provenance"][k] for k in ("stage_result_ids", "assisted_dwell_s", "physical_acceptance")},
                engineering=dict(vehicle={k: s["vehicle"][k] for k in ("loaded_train_kg", "tare_train_kg", "selected_span", "interfaces")},
                                 passengers={k: s["passengers"][k] for k in ("hvac", "door_exchange", "auxiliary_kw")},
                                 corridor=dict(route_km=s["corridor"]["chainages_km"][-1]),
                                 motion=dict(metrics=m["metrics"], energy_kwh_per_train_km=m["energy_kwh_per_train_km"],
                                             trace=[dict(time_s=row["time_s"], source_mw=row["source_mw"],
                                                     trains=[{"chainage_m": t["chainage_m"]} for t in row["trains"]])
                                                    for row in m["trace"][::3]]),
                                 production=dict(decision_summary=s["production"]["decision_summary"],
                                      scenarios={k: {"last_completion_workday": v["last_completion_workday"]}
                                                 for k, v in s["production"]["scenarios"].items()})))


CAMPAIGN = [
    {"headway_min": h, "topology": t} for h in (15, 20, 30) for t in ("radial30", "paired6")
] + [
    {"condition": "combined", "topology": t} for t in ("radial30", "paired6")
] + [
    {"span_m": length} for length in (20, 25, 30)
] + [
    {"cars": 3, "headway_min": 20, "material": m, "topology": "paired6"} for m in ("steel", "aluminium", "hybrid")
] + [
    {"demand": "upside", "ambient_c": 48, "grade_pct": 2, "topology": "paired6"},
]


def publish_catalogue(check=False):
    cases = [compact(run_case(options)) for options in CAMPAIGN]
    outputs = {"baseline.json": encode(cases[0]) + b"\n",
               "scenario-data.js": b"window.AIRPORT_SIMULATION=" + encode(dict(cases=cases)) + b";\n"}
    for name, data in outputs.items():
        path = HERE / name
        if check:
            if data != path.read_bytes():
                raise ValueError(f"Regenerate the Airport scenario catalogue: {name}")
        else:
            write_atomic(path, data)
    return [c["identity"]["evaluation_id"] for c in cases]


def dossier(result):
    s = result["stages"]
    files = {"scenario.json": encode(result), "factory-and-cash.json": encode(s["production"]),
             "vehicle-and-civil.json": encode(s["vehicle"]), "train-events.json": encode(s["motion"]["events"]),
             "controls-replay.json": (HERE / "controls-replay.json").read_bytes(),
             "passenger-interfaces.json": encode(s["passengers"])}
    with TemporaryDirectory() as temp:
        feed = Path(temp) / "airport.gtfs.zip"
        exchange = corridor.gtfs({**s["corridor"], "dwell_s": result["provenance"]["assisted_dwell_s"]}, feed)
        files["transit/airport-planning.gtfs.zip"] = feed.read_bytes()
        files["transit/six-stop-service.json"] = encode(exchange)
    # Enclose the issued six-article enquiry as a labelled parent reference.
    # A derivative has its own quantities; it cannot reuse a steel joint or a radial feeder approval.
    files["parent-reference/airport-enquiries.zip"] = (PROTO / "airport-enquiries.zip").read_bytes()
    from cities.Baghdad.engineering.simulation import variant_exchange
    files.update(variant_exchange.artifacts(result))
    from cities.Baghdad.engineering.prototype.enquiries import portable_guide
    for name in ("index.html", "scenario.css", "scenario.js", "cam_compare.py", "freecad_interactive.py"):
        files[name] = (HERE / name).read_bytes()
    files["scenario-data.js"] = b"window.AIRPORT_SIMULATION=" + encode({"cases": [compact(result)]}) + b";\n"
    for name in ("SIMULATION.md", "PLAN.md", "MOTION-POWER.md", "production-guide.md", "passenger-guide.md",
                 "CAM-COMPARISON.md", "FREECAD-INTERACTIVE.md", "cam_compare_results.json", "freecad_interactive.json"):
        files[name] = (HERE / name).read_bytes()
    for name in ("span-benchmark.zip", "passenger-benchmark.json", "ifc-results.json", "motion-evidence.json"):
        files["comparison-evidence/" + name] = (HERE / name).read_bytes()
    if result["inputs"] == selections({}):
        proof = json.loads((HERE / "external-default.json").read_bytes())
        if (proof["coupled_evaluation_id"] != s["motion"]["evaluation_id"]
                or proof["adapter_sha256"] != sha((HERE / "motion_adapters.py").read_bytes())):
            raise ValueError("External checks do not match the default motion case")
        files["comparison-evidence/external-default.json"] = encode(proof)
    paths = {HERE / name: name for name in files if (HERE / name).is_file()}
    for name in tuple(files):
        if name.endswith(".md"):
            files[name] = portable_guide(HERE / name, name, paths)
    files["manifest.json"] = encode(dict(schema="osr-airport-scenario-export/1", identity=result["identity"],
                                   fabrication_released=False, physical_accepted=False,
                                   sha256={name: sha(raw) for name, raw in files.items()}))
    return archive(files)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name, options in CHOICES.items():
        parser.add_argument("--" + name.replace("_", "-"), choices=options, type=type(options[0]), default=options[0])
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--catalogue", action="store_true", help="publish the bounded offline Workbench cases")
    mode.add_argument("--check-catalogue", action="store_true")
    mode.add_argument("--export", type=Path)
    mode.add_argument("--json", action="store_true", help="print the full scenario and its evidence")
    args = parser.parse_args()
    inputs = {k: getattr(args, k) for k in CHOICES}
    target = args.export.parent.resolve() if args.export else ROOT
    target.mkdir(parents=True, exist_ok=True)
    with disk_reservation(ROOT, target, "Airport scenario and drawing issue", 64 << 20):
        if args.catalogue or args.check_catalogue:
            print(json.dumps(publish_catalogue(args.check_catalogue)))
            return
        runs = {}
        result = run_case(inputs, runs=runs)
        if args.check and (inputs != selections({}) or compact(result) != json.loads((HERE / "baseline.json").read_bytes())):
            raise ValueError("Default Airport result differs from the published case")
        if args.export:
            if args.export.suffix != ".zip":
                parser.error("Use a .zip output path")
            content = dossier(result)
            if args.export.exists() and args.export.read_bytes() != content:
                parser.error("The destination contains another issue. Choose a new filename.")
            write_atomic(args.export, content)
        print(json.dumps(result if args.json else dict(identity=result["identity"], decision=result["decision"],
              cache=runs, process_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss), indent=2))


if __name__ == "__main__":
    main()
