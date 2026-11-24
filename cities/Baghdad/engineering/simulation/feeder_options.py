"""Compare source layouts with the existing train-day and DC network solvers."""
import argparse
from dataclasses import asdict, replace
from decimal import Decimal, InvalidOperation
from fractions import Fraction
from math import ceil, isfinite
from pathlib import Path
import json

from cities.Baghdad.engineering.simulation import motion_dc, motion_power, scenario
from engineering.performance import check_disk_reservation, disk_reservation


LAYOUTS = ("radial30", "paired6", "paired8", "paired6_shifted", "paired6_heavy")
DEFAULT_SNAPSHOT_SITES = 128


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--moving", choices=LAYOUTS, help="Run one full working day on this supported layout")
    mode.add_argument("--snapshot-spacing-km", metavar="KM",
                      help="Screen one train at fixed positions with at most this distance between paired supply sites")
    p.add_argument("--snapshot-site-budget", type=int, metavar="SITES",
                   help=f"Maximum number of sites to sample in a snapshot (default {DEFAULT_SNAPSHOT_SITES})")
    p.add_argument("--loop-resistance-factor", type=float, default=1., help="Multiply outward and return resistance (0.5 to 1.5)")
    for flag in ("cars", "headway_min", "grade_pct", "ambient_c"):
        options = scenario.CHOICES[flag]
        p.add_argument("--" + flag.replace("_", "-"), choices=options, type=int, default=options[0])
    for flag in ("material", "demand", "condition"):
        options = scenario.CHOICES[flag]
        p.add_argument("--" + flag, choices=options, default=options[0])
    p.add_argument("--failed-site", type=int, help="Zero-based source site for a site outage")
    p.add_argument("--failed-path", type=int, help="Zero-based intersite bay for a path outage")
    return p


def outage(args, count):
    site_out = args.condition in ("combined", "site_out")
    path_out = args.condition in ("combined", "path_out")
    site = count // 2 if args.failed_site is None else args.failed_site
    path = min(site, count - 2) if args.failed_path is None else args.failed_path
    if not 0 <= site < count or not 0 <= path < count - 1:
        raise ValueError(f"Outage indices exceed the {count} sites or {count-1} intersite bays")
    if (args.failed_site is not None and not site_out) or (args.failed_path is not None and not path_out):
        raise ValueError("Use a site or path index with its corresponding outage condition")
    return dict(failed_site=site if site_out else None, failed_path=path if path_out else None)


def spacing_sites(length_m, spacing_km, site_budget=DEFAULT_SNAPSHOT_SITES):
    try:
        spacing = Decimal(str(spacing_km))
    except InvalidOperation as error:
        raise ValueError("Maximum spacing must be a finite positive distance in km") from error
    if not spacing.is_finite() or spacing <= 0:
        raise ValueError("Maximum spacing must be a finite positive distance in km")
    if type(site_budget) is not int or site_budget < 2:
        raise ValueError("The snapshot site budget must allow at least two endpoints")
    route_km = Decimal(str(length_m)) / 1000
    if spacing >= route_km:
        bays = 1
    elif route_km.adjusted() - spacing.adjusted() > max(100, len(str(site_budget)) + 1):
        # Preserve the exact count expression without allocating a huge integer
        # merely to report a tiny-spacing request that exceeds the chosen budget.
        raise ValueError(f"Requested sites = ceil({route_km}/{spacing}) + 1, above the "
                         f"snapshot site budget of {site_budget}. Increase --snapshot-site-budget to evaluate.")
    else:
        bays = ceil(Fraction(route_km) / Fraction(spacing))
    if bays + 1 > site_budget:
        raise ValueError(f"Spacing requires {bays + 1} sites. The snapshot site budget is {site_budget}. "
                         "Increase --snapshot-site-budget to evaluate this layout.")
    return tuple(length_m * i / bays for i in range(bays + 1))


def snapshot(feeder, case, failure):
    circuit = feeder.circuit(case["condition"], **failure)
    # Sample both edges of each source section, including the section on
    # each side of an open tie. The two sides can have unequal resistances.
    positions = set(feeder.sites)
    for x in circuit.cuts_m:
        positions.update([max(0., x-.001), min(feeder.sites[-1], x+.001)])
    rated = case["traction_w"] + case["aux_w"]
    requested = rated * (1.05 if case["condition"] == "combined" else 1.)
    samples = []
    for x in sorted(positions):
        port = circuit.port(x, 0)
        if port is None:
            samples.append(dict(position_m=x, voltage_v=None, delivered_w=0., residual_v=None))
            continue
        volts, delivered, _, _, error, _ = motion_dc.loadflow(circuit, [port], [requested], rated/1350)
        samples.append(dict(position_m=x, voltage_v=volts[0], delivered_w=delivered[0], residual_v=error))
    live = [r for r in samples if r["voltage_v"] is not None]
    return dict(method="stationary one-train electrical snapshots", fixed_points=samples,
                requested_train_w=requested, minimum_live_voltage_v=min(r["voltage_v"] for r in live),
                minimum_delivered_fraction=min(r["delivered_w"] for r in samples)/requested,
                sampled_voltage_screen=len(live)==len(samples) and all(1350 <= r["voltage_v"] <= 1650 for r in live),
                numerical_screen=all(r["residual_v"] < .05 for r in live),
                moving_service_result=None, installed_price_usd=None)


def evaluate(args):
    factor = args.loop_resistance_factor
    if not isfinite(factor) or not .5 <= factor <= 1.5:
        raise ValueError("The evaluator supports finite loop resistance factors from 0.5 to 1.5")
    if args.moving and args.snapshot_site_budget is not None:
        raise ValueError("Use --snapshot-site-budget with --snapshot-spacing-km")
    choices = {k: getattr(args, k) for k in ("cars", "headway_min", "grade_pct", "ambient_c", "material", "demand")}
    # The issued study supplies the actual assisted dwell, OD matrix, mass and auxiliary duty.
    # The new layout does not receive its parent's fleet price or protection approval.
    base = scenario.run_case(choices)
    stages = base["stages"]
    route, vehicle = stages["corridor"], stages["vehicle"]
    motion = dict(cars=args.cars, material=args.material, headway_min=args.headway_min, grade_pct=args.grade_pct,
                  chainages_km=route["chainages_km"], hourly_od=route["hourly_od"], condition=args.condition,
                  tare_train_kg=vehicle["tare_train_kg"], loaded_train_kg=vehicle["loaded_train_kg"],
                  dwell_s=base["provenance"]["assisted_dwell_s"], auxiliary_kw=stages["passengers"]["auxiliary_kw"],
                  topology=args.moving or "paired6", conductor_factor=factor, candidate_id=vehicle["physical_id"])
    refs = motion_power.reference()
    case = motion_power.normalize(motion, refs)
    feed = motion_power.make_feeder(motion["topology"], case["chainages_m"], factor, refs)
    if args.snapshot_spacing_km is not None:
        budget = DEFAULT_SNAPSHOT_SITES if args.snapshot_site_budget is None else args.snapshot_site_budget
        positions = spacing_sites(case["chainages_m"][-1], args.snapshot_spacing_km, budget)
        feed = replace(feed, name="equal-spaced-paired-snapshot", sites=positions)
    failure = outage(args, len(feed.sites))
    circuit = feed.circuit(case["condition"], **failure)
    if args.moving:
        result = motion_power.evaluate({**motion, **failure})
        if result["physical"]["upstream_candidate_id"] != vehicle["physical_id"] or tuple(result["physical"]["feeder"]["sites"]) != feed.sites:
            raise ValueError("Moving duty and requested installed scenario differ")
        metrics = result["metrics"]
        report = dict(method="full working day with moving train loads", moving_evaluation_id=result["evaluation_id"],
                      gates=result["gates"], metrics=metrics, failure=result["failure"],
                      electrical_enquiry=result["electrical_enquiry"], price_basis=motion_power.unit_cost_basis(result),
                      limits=result["limits"])
    else:
        report = snapshot(feed, case, failure)
        report.update(requested_max_spacing_km=str(args.snapshot_spacing_km),
                      snapshot_site_budget=budget, sampled_positions=len(report["fixed_points"]))
    bindings = base["provenance"]["sources"]
    sources = {k: bindings[k] for k in ("corridor", "vehicle", "passengers", "motion")}
    sources["adapter"] = scenario.source_hashes([Path(__file__).resolve(), Path(scenario.__file__).resolve()])
    report.update(source_sha256=sources, feeder=asdict(feed), site_count=len(feed.sites), outage=failure,
                  source_spacing_max_m=max(b-a for a,b in zip(feed.sites,feed.sites[1:])),
                  equipment_voltage_window_v=[1350,1650], physical_accepted=False, protection_approved=False,
                  service_brief=choices, conductor_condition=args.condition, train_traction_rating_w=case["traction_w"],
                  train_auxiliary_w=case["aux_w"], tare_train_kg=vehicle["tare_train_kg"],
                  loaded_train_kg=vehicle["loaded_train_kg"], normal_places_per_train=case["capacity"],
                  assisted_dwell_s=case["dwell_s"], od_id=stages["motion"]["demand_basis"]["od_id"],
                  vehicle_id=vehicle["physical_id"], corridor_id=route["candidate_id"])
    report.update(service_stations=len(route["stops"]), platform_clear_length_m=refs[0]["station_geometry"]["platform_clear_length_m"],
                  train_length_m=case["length_m"], terminal_open_platform_faces=[1,1],
                  live_source_sections=len(circuit.live), contact_supply="Continuous protected conductor",
                  section_boundaries_m=circuit.cuts_m, source_no_load_v=circuit.source_v,
                  source_resistance_ohm=circuit.source_ohm, loop_resistance_ohm_km=circuit.loop_ohm_m*1000)
    geometry = {k:v for k,v in asdict(feed).items() if k != "name"}
    report["physical_id"] = scenario.sha(scenario.encode([vehicle["physical_id"], route["chainages_km"], geometry]))
    report["evaluation_id"] = scenario.sha(scenario.encode(report))
    return report


def main(argv=None):
    p = parser()
    args = p.parse_args(argv)
    with disk_reservation(scenario.ROOT, scenario.ROOT, "Single traction feeder option", 128 << 20) as lease:
        try:
            result = evaluate(args)
        except ValueError as error:
            p.error(str(error))
        check_disk_reservation(lease)
        print(json.dumps(result, sort_keys=True, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
