"""Generate and verify the lightweight Airport motion/DC benchmark receipt."""

import argparse
from hashlib import sha256
import json
from pathlib import Path

from cities.Baghdad.engineering.simulation import motion_adapters, motion_power
from engineering.outline.baghdad_system import _id

ROOT = Path(__file__).resolve().parents[4]
PACKET = Path(__file__).with_name("motion-evidence.json")
SOURCES = (
    "cities/Baghdad/airport_service.py",
    "cities/Baghdad/airport_supply.py",
    "cities/Baghdad/airport_opening.py",
    "cities/Baghdad/engineering/commissioning/feeder.py",
    "cities/Baghdad/engineering/mechanical/vehicle/section-trial.toml",
    "cities/Baghdad/engineering/prototype/airport-prototype.zip",
    "cities/Baghdad/engineering/prototype/sourcing-estimate.json",
    "cities/Baghdad/maps/corridor-review.geojson",
    "cities/Baghdad/service-diagrams.json",
    "cities/Baghdad/station-register.json",
    "cities/Baghdad/system-results.json",
    "cities/Baghdad/system.toml",
    "engineering/outline/baghdad_diagrams.py",
    "engineering/outline/baghdad_system.py",
    *(str(Path(__file__).with_name(name).relative_to(ROOT)) for name in (
        "motion_power.py", "motion_dc.py", "motion_adapters.py", "motion_evidence.py",
    )),
)


def source_digests():
    return {name: sha256((ROOT / name).read_bytes()).hexdigest() for name in SOURCES}


def crosscheck(inputs, result=None, output_dir=None):
    """Run both tools against the explicitly supplied motion scenario."""
    if result is None:
        result = motion_power.evaluate(inputs, output_dir)
    references = motion_power.reference()
    case = motion_power.normalize(inputs, references)
    expected = {k: v for k, v in case.items() if k not in ("hourly_od", "od_matrix")}
    if _id(expected) != _id(result["scenario"]):
        raise ValueError("External check needs the same coupled scenario")
    od = case["hourly_od"] or case["od_matrix"]
    if result["demand_basis"]["od_id"] != (_id(od) if od is not None else None):
        raise ValueError("External check needs the same coupled demand")
    return {
        "coupled_evaluation_id": result["evaluation_id"],
        "adapter_sha256": sha256(Path(motion_adapters.__file__).read_bytes()).hexdigest(),
        "sumo": motion_adapters.sumo_check(case, motion_power.service(case, references),
                                          result["events"], output_dir),
        "ac": motion_adapters.ac_check(result),
    }


def summarize(raw, sources=None):
    nominal = raw["selected_replay"]
    metric_keys = ("booked_passenger_trips", "completed_passenger_trips", "completed_yard_trips",
                   "fleet_sets_required", "terminal_B_phase_s", "normal_places_per_hour_direction",
                   "minimum_service_departure_gap_s", "maximum_arrival_delay_s", "nominal_timetable_conflicts",
                   "resource_wait_s", "protected_hold_train_s", "offered_passengers", "boarded_passengers", "unserved_passengers",
                   "gross_boardings", "unserved_capacity_at_close", "unserved_service_boundary",
                   "unserved_incomplete_trip", "demand_balance_residual_passengers",
                   "denied_boarding_attempts", "distance_km", "source_kwh", "loss_kwh",
                   "regen_potential_kwh", "regen_network_kwh", "regen_local_kwh", "regen_rejected_kwh",
                   "minimum_collector_v", "maximum_collector_v", "max_dc_residual_v",
                   "dc_balance_residual_kwh", "mechanical_balance_kwh", "peak_site_current_ka",
                   "max_branch_current_ka", "max_site_rms_current_ka", "unresolved_units")
    rows = []
    for result in raw["cases"]:
        item = {key: result[key] for key in (
            "candidate_id", "evaluation_id", "source_feeder_design_id", "scenario",
            "annual_train_km", "booked_annual_train_km", "energy_kwh_per_train_km",
            "peak_power_mw", "gates", "economic_ranking_eligible", "failure",
            "feeder_cost",
        )}
        item["metrics"] = {k: result["metrics"][k] for k in metric_keys if k in result["metrics"]}
        rows.append(item)
    receipt = {
        "schema": "baghdad-airport-motion-evidence/1", "source_sha256": sources or source_digests(),
        "retained_opening_candidate_id": nominal["source_publication_candidate_id"],
        "retained_opening_evaluation_id": nominal["source_opening_evaluation_id"],
        "retained_timetable_evaluation_id": nominal["source_timetable_id"],
        "nominal_evaluation_id": nominal["evaluation_id"], "cases": rows, "convergence": raw["convergence"],
        "equal_service_comparisons": raw["equal_service_comparisons"],
        "sumo": {key: {k: v for k, v in run.items() if k != "trace"} for key, run in raw["sumo"].items()},
        "ac": raw["ac"], "limits": nominal["limits"], "method_sources": nominal["method_sources"],
        "physical_accepted": False,
    }
    receipt["receipt_id"] = _id(receipt)
    return receipt


def verify(path=PACKET):
    receipt = json.loads(Path(path).read_text())
    closure = receipt.pop("receipt_id")
    if (receipt["schema"] != "baghdad-airport-motion-evidence/1"
            or _id(receipt) != closure or receipt["source_sha256"] != source_digests()):
        raise ValueError("Airport motion evidence is stale or its receipt was changed")
    return {**receipt, "receipt_id": closure}


def regenerate(path, output_dir=None):
    from engineering.performance import check_disk_reservation, disk_reservation

    path = Path(path).resolve()
    with disk_reservation(ROOT, path.parent, "Airport motion evidence receipt", 4 * 2**20) as lease:
        before = source_digests()
        result = summarize(motion_power.run(output_dir), before)
        if before != source_digests():
            raise ValueError("Source inputs changed during the Airport campaign")
        if any(row["status"] != "verified execution" or not row["stop_screen_passed"]
               or row["launch_controls"]["status"] != "passed"
               for row in result["sumo"].values()) or any(
                row["status"] != "verified execution" for row in result["ac"].values()):
            raise ValueError("Full evidence regeneration requires working SUMO/netconvert and pandapower")
        check_disk_reservation(lease)
        path.parent.mkdir(parents=True, exist_ok=True)
        pending = path.with_suffix(".pending")
        pending.write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n")
        pending.replace(path)
    return verify(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--regenerate", action="store_true")
    parser.add_argument("--trace-dir", type=Path)
    parser.add_argument("--receipt", type=Path, default=PACKET)
    args = parser.parse_args()
    result = regenerate(args.receipt, args.trace_dir) if args.regenerate else verify(args.receipt)
    print(json.dumps({"receipt_id": result["receipt_id"], "cases": len(result["cases"]),
                      "nominal_evaluation_id": result["nominal_evaluation_id"]}, indent=2))


if __name__ == "__main__":
    main()
