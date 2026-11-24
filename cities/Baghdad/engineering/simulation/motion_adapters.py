"""Independent route and upstream AC checks with explicit modelling boundaries."""

from contextlib import ExitStack
from hashlib import sha256
from itertools import pairwise
from math import sqrt
from pathlib import Path
from shutil import disk_usage, which
from statistics import median
from subprocess import TimeoutExpired, run
from tempfile import TemporaryDirectory
import xml.etree.ElementTree as ET


def _executable(name):
    root = Path(__file__).resolve().parents[4]
    local = root / ".venv/bin" / name
    return which(name) or (str(local) if local.is_file() else None)


def _xml(path, node):
    ET.ElementTree(node).write(path, encoding="utf-8", xml_declaration=True)


def matched_gtfs(alignment, case, scheduled, path, *, service_date="20261123"):
    """Export the booked route speed offer, retaining unmapped stop times in the receipt."""
    from cities.Baghdad.engineering.simulation import airport_alignment
    airport_alignment.validate(alignment)
    if case.get("alignment_id") != alignment["alignment_id"]:
        raise ValueError("GTFS and moving service need the same alignment")
    expected = min(case["speed_offer"]["parent_speed_cap_kmh"],
                   case["speed_offer"]["posted_minimum_kmh"])
    if case["speed_cap_kmh"] != expected:
        raise ValueError("GTFS service must use the effective posted route cap")
    group, trips, patterns, profiles, _, _ = scheduled
    stop_ids = [stop["id"] for stop in alignment["stops"]]
    if ([stop["id"] for stop in patterns[0]] != stop_ids
            or [stop["id"] for stop in patterns[1]] != stop_ids[::-1]
            or any(side not in (0, 1) or not isinstance(unit, str) or not unit
                   for unit, side, _, _ in trips)
            or len({(side, start) for _, side, start, _ in trips}) != len(trips)
            or any(arrival != start + group["one_way_s_including_dwell"]
                   for _, _, start, arrival in trips)):
        raise ValueError("GTFS trips must match the directional booked service and six route stops")
    if any(leg["cruise_m_s"] > case["speed_m_s"] + 1e-9 for side in profiles for leg in side):
        raise ValueError("GTFS booked legs exceed the posted route cap")
    from .corridor import write_booked_gtfs
    written = write_booked_gtfs(alignment["stops"], trips, patterns, path, service_date=service_date)
    return dict(alignment_id=alignment["alignment_id"], speed_offer=case["speed_offer"],
                service_date=service_date, trips=len(trips), **written,
                terminal_B_phase_s=group["terminal_B_phase_s"],
                gtfs_sha256=sha256(Path(path).read_bytes()).hexdigest(),
                scope="Planning timetable for the conservative whole-route cap; unmapped stops retained in receipt. Route survey and independent operation remain open.")


def train_curve(case, side, positioning=False):
    """Airport motor and rolling force at the selected full or empty case mass."""
    mass = case["tare_train_kg"] if positioning else case["loaded_train_kg"]
    slope = case["grade_pct"] / 100 * (1 if side == 0 else -1)
    gravity = 9.81 * slope / sqrt(1 + slope**2)
    drag_kn = mass * case["resistance_m_s2"] / 1000
    effort_kn = max(0., mass * (case["acceleration_m_s2"] + case["resistance_m_s2"] + gravity) / 1000)
    wheel_kw = case["traction_w"] * case["efficiency"] / 1000
    # Include the exact knee and samples above the operational speed ceiling,
    # so the electrical-power knee is explicit even when service never sees it.
    knee = wheel_kw / effort_kn if effort_kn else case["speed_m_s"]
    speeds = sorted(set([0., 5., 10., 15., case["speed_m_s"], knee, knee + 5, knee + 10]))
    traction = [min(effort_kn, wheel_kw / speed) if speed else effort_kn for speed in speeds]
    return dict(mass_kg=mass, train_length_m=case["length_m"], mass_factor=1.,
                speeds_m_s=speeds, tractive_effort_kn=traction, rolling_resistance_kn=[drag_kn] * len(speeds),
                grade_pct=100 * slope, grade_force_kn=mass * gravity / 1000, wheel_power_limit_kw=wheel_kw,
                tractive_effort_limit_kn=effort_kn, net_launch_accel_m_s2=(effort_kn-drag_kn)*1000/mass-gravity,
                brake_deceleration_m_s2=case["braking_m_s2"], speed_limit_m_s=case["speed_m_s"])


def _rail_type(routes, name, curve):
    def series(values):
        return " ".join(f"{x:.10g}" for x in values)

    ET.SubElement(routes, "vType", id=name, vClass="rail_urban", carFollowModel="Rail", trainType="custom",
                  mass=f'{curve["mass_kg"]:.10g}', massFactor=str(curve["mass_factor"]),
                  length=str(curve["train_length_m"]), maxSpeed=str(curve["speed_limit_m_s"]),
                  decel=str(curve["brake_deceleration_m_s2"]), sigma="0",
                  speedTable=series(curve["speeds_m_s"]), tractionTable=series(curve["tractive_effort_kn"]),
                  resistanceTable=series(curve["rolling_resistance_kn"]))


def _startup_controls(case, path, network, sumo, checkpoint):
    """Observe native speed increments on the same first level Airport block."""
    routes = ET.Element("routes")
    rows = {}
    for cars in (3, 6):
        factor = cars / case["cars"]
        chosen = {**case, "cars": cars, "grade_pct": 0., "length_m": 17*cars + .5*(cars-1),
                  "loaded_train_kg": case["loaded_train_kg"] * factor, "traction_w": case["traction_w"] * factor}
        baseline = train_curve(chosen, 0)
        half_effort = {**baseline, "tractive_effort_kn": [x / 2 for x in baseline["tractive_effort_kn"]]}
        heavier = {**baseline, "mass_kg": 2 * baseline["mass_kg"]}
        for name, curve in (("normal", baseline), ("half_force", half_effort), ("double_mass", heavier)):
            key = f"cars{cars}_{name}"
            _rail_type(routes, key, curve)
            expected = (curve["tractive_effort_kn"][0] - curve["rolling_resistance_kn"][0]) * 1000 / curve["mass_kg"]
            rows[key] = {"expected_m_s2": expected}
    # Run each control serially on an edge with an arrival at 100 m so each
    # launch has an unoccupied block. FCD readback uses only its first five seconds.
    ET.SubElement(routes, "route", id="launch", edges="d0-0")
    for index, key in enumerate(rows):
        ET.SubElement(routes, "vehicle", id=key, type=key, route="launch", depart=str(90*index),
                      departPos="0", departSpeed="0", arrivalPos="100")
    _xml(path / "launch-routes.xml", routes)
    checkpoint()
    result = run([sumo, "--net-file", network, "--route-files", "launch-routes.xml",
                  "--step-length", "1", "--end", "540", "--no-step-log", "true",
                  "--fcd-output", "launch-fcd.xml", "--precision", "6"],
                 cwd=path, text=True, capture_output=True, timeout=30)
    checkpoint()
    if result.returncode:
        return {"status": "failed", "detail": result.stderr[-800:]}
    samples = {key: [] for key in rows}
    for tick in ET.parse(path / "launch-fcd.xml").getroot().findall("timestep"):
        for vehicle in tick.findall("vehicle"):
            series = samples[vehicle.get("id")]
            if len(series) < 6:
                series.append((float(tick.get("time")), float(vehicle.get("speed"))))
    for key, series in samples.items():
        if len(series) != 6:
            return {"status": "failed", "detail": f"no complete FCD launch sample for {key}"}
        t0, v0 = series[0]
        t1, v1 = series[-1]
        measured = (v1 - v0) / (t1 - t0)
        rows[key].update(observed_m_s2=measured, samples=series,
                         agrees=abs(measured - rows[key]["expected_m_s2"]) < .001)
    return {"status": "passed" if all(r["agrees"] for r in rows.values()) else "failed",
            "scaling": "reference case mass and wheel power scaled by car count; 3/6-car force and mass perturbations",
            "cases": rows}


def sumo_check(case, scheduled, custom_events, output_dir=None):
    """Run the same directional track lengths, speed limits, stops and full schedule.

    SUMO independently computes interstop physics and following. It uses separate
    trips per working, with no turnback platform/throat coupling across directions.
    """
    if case.get("grade_profile") is not None:
        return {"status": "out of domain", "reason": "The SUMO adapter supports scalar grade only"}
    netconvert, sumo = _executable("netconvert"), _executable("sumo")
    if not netconvert or not sumo:
        return {"status": "held", "reason": "SUMO and netconvert executables unavailable"}
    _, trips, _, profiles, positioning, _ = scheduled
    root = Path(__file__).resolve().parents[4]
    temp_parent = Path(output_dir) if output_dir is not None else root / "build"
    temp_parent.mkdir(parents=True, exist_ok=True)
    if disk_usage(temp_parent).free < 20 * 2**30 + 64 * 2**20:
        return {"status": "held", "reason": "20 GiB disk floor plus 64 MiB XML budget"}
    from engineering.performance import DiskReservationHeld, check_disk_reservation, disk_reservation

    try:
        with ExitStack() as stack:
            lease = stack.enter_context(disk_reservation(root, temp_parent, "Airport SUMO rail XML", 64 * 2**20))
            if output_dir is None:
                path = Path(stack.enter_context(TemporaryDirectory(prefix="airport-sumo-", dir=temp_parent)))
            else:
                path = temp_parent / f'sumo-{case["headway_min"]}'
            path.mkdir(parents=True, exist_ok=True)
            return _sumo_run(path, case, trips, profiles, positioning, custom_events, netconvert, sumo,
                             lambda: check_disk_reservation(lease))
    except DiskReservationHeld as error:
        return {"status": "held", "reason": error.record["reason"]}
    except TimeoutExpired as error:
        return {"status": "interrupted", "reason": f"Tool timeout after {error.timeout} seconds"}


def _sumo_run(path, case, trips, profiles, positioning, custom_events, netconvert, sumo, checkpoint):
    nodes, edges, routes = ET.Element("nodes"), ET.Element("edges"), ET.Element("routes")
    traction_curves = {f"{label}{side}": train_curve(case, side, positioning=label == "positioning")
                       for label in ("passenger", "positioning") for side in (0, 1)}
    for name, curve in traction_curves.items():
        _rail_type(routes, name, curve)
    chainages = case["chainages_m"]
    for side in (0, 1):
        points = chainages if side == 0 else chainages[::-1]
        names = [f"t{side}s{i}" for i in range(6)]
        for name, pos in zip(names, points):
            ET.SubElement(nodes, "node", id=name, x=str(pos), y=str(side * 4), z=str(pos * case["grade_pct"] / 100), type="rail_signal" if name not in (names[0], names[-1]) else "priority")
        for i, (a, b) in enumerate(pairwise(names)):
            ET.SubElement(edges, "edge", {
                "id": f"d{side}-{i}", "from": a, "to": b, "allow": "rail_urban",
                "speed": str(profiles[side][i]["cruise_m_s"]), "numLanes": "1",
                "length": str(abs(points[i + 1] - points[i])),
            })
        ET.SubElement(routes, "route", id=f"d{side}", edges=" ".join(f"d{side}-{i}" for i in range(5)))

    booked = {}
    clock0 = min(x[2] for x in trips + positioning)
    empty = set(positioning)
    for n, (unit, side, start, arrival) in enumerate(sorted(trips + positioning, key=lambda x: x[2])):
        identity = f"trip-{n:03}"
        booked[identity] = (start, arrival)
        name = "positioning" if (unit, side, start, arrival) in empty else "passenger"
        vehicle = ET.SubElement(routes, "vehicle", id=identity, type=f"{name}{side}", route=f"d{side}",
                                depart=str(start - clock0), departPos="0", departSpeed="0", arrivalSpeed="0")
        for i in range(5):
            leg = profiles[side][i]
            end_pos = abs(leg["end_km"] - leg["start_km"]) * 1000 - .02
            ET.SubElement(vehicle, "stop", lane=f"d{side}-{i}_0", endPos=f"{end_pos:.3f}",
                          duration=str(case["dwell_s"] if i < 4 else 0))
    _xml(path / "nodes.xml", nodes)
    _xml(path / "edges.xml", edges)
    _xml(path / "routes.xml", routes)
    versions = {}
    for tool, binary in (("netconvert", netconvert), ("sumo", sumo)):
        versions[tool] = run([binary, "--version"], capture_output=True, text=True, timeout=10).stdout.splitlines()[0]
    commands = ([netconvert, "--node-files", "nodes.xml", "--edge-files", "edges.xml",
                 "--no-internal-links", "--output-file", "network.xml"],
                [sumo, "--net-file", "network.xml", "--route-files", "routes.xml", "--step-length", "1",
                 "--no-step-log", "true", "--tripinfo-output", "tripinfo.xml", "--stop-output", "stops.xml",
                 "--time-to-teleport", "-1", "--tripinfo-output.write-unfinished", "true",
                 "--end", str(max(x[3] for x in trips + positioning) - clock0 + 1800)])
    native_warnings = ""
    for command in commands:
        checkpoint()
        result = run(command, cwd=path, capture_output=True, text=True, timeout=55)
        checkpoint()
        (path / ("sumo.log" if command[0] == sumo else "netconvert.log")).write_text(result.stdout + result.stderr)
        if command[0] == sumo:
            native_warnings = result.stderr
        if result.returncode:
            return {"status": "failed", "returncode": result.returncode, "log_tail": result.stderr[-800:],
                    "versions": versions}
    rows = ET.parse(path / "tripinfo.xml").getroot().findall("tripinfo")
    finished = {row.get("id"): row.attrib for row in rows if float(row.get("arrival", -1)) >= 0}
    stops = ET.parse(path / "stops.xml").getroot().findall("stopinfo")
    own = {event["id"]: event for event in custom_events}
    durations = [float(row["duration"]) for row in finished.values()]
    differences = [float(row["duration"]) - (own[k]["actual_arrival_s"] - own[k]["actual_departure_s"])
                   for k, row in finished.items() if k in own]
    trace = [{"id": k, "booked_departure_s": booked[k][0], "booked_arrival_s": booked[k][1],
              "actual_departure_s": clock0 + float(row["depart"]),
              "actual_arrival_s": clock0 + float(row["arrival"]),
              "duration_s": float(row["duration"]), "depart_delay_s": float(row["departDelay"])}
             for k, row in sorted(finished.items())]
    # Read the serialized native model back independently of the numeric input
    # dictionary. The control moves below validate native parsing of weight and force.
    serialized = {row.get("id"): row.attrib for row in ET.parse(path / "routes.xml").getroot().findall("vType")}
    for name, curve in traction_curves.items():
        raw = serialized[name]
        assert raw["trainType"] == "custom" and abs(float(raw["mass"]) - curve["mass_kg"]) < .001
        for attr, key in (("speedTable", "speeds_m_s"), ("tractionTable", "tractive_effort_kn"),
                          ("resistanceTable", "rolling_resistance_kn")):
            assert all(abs(float(a) - b) < 1e-6
                       for a, b in zip(raw[attr].split(), curve[key], strict=True))
    controls = (_startup_controls(case, path, "network.xml", sumo, checkpoint) if case["grade_pct"] == 0 else
                {"status": "held", "detail": "The force/mass launch control uses a level corridor fixture."})
    return {"status": "verified execution", "versions": versions,
            "train_model": "custom", "traction_curves": traction_curves,
            "serialized_type_readback": serialized, "launch_controls": controls,
            "booked_route_trips": len(booked), "completed_route_trips": len(finished),
            "completed_stops": len(stops), "scheduled_stops": 5 * len(booked),
            "stop_screen_passed": len(stops) == 5 * len(booked) and not native_warnings.count("skips stop"),
            "native_warnings": {"skipped_stops": native_warnings.count("skips stop"),
                                "emergency_stops": native_warnings.count("performs emergency stop")},
            "median_running_time_s": median(durations) if durations else None,
            "median_difference_to_coupled_s": median(differences) if differences else None,
            "max_absolute_difference_to_coupled_s": max(map(abs, differences), default=None),
            "trace": trace,
            "limitations": "Separate directed tracks and trip vehicles. Fixed loaded mass for passenger trips and tare for positioning, with Airport wheel power, resistance and force per formation and direction. Shared turnback, yard, changing passenger load and DC are specific to the coupled model."}

def ac_check(result):
    """Balanced illustrative AC topology at the actual peak DC snapshot."""
    try:
        import pandapower as pp
    except ImportError:
        return {"status": "held", "reason": "Run with the project .venv Python containing pandapower"}

    sites = result["physical"]["feeder"]["sites"]
    failed = result["failure"]["site"]
    peak = result["metrics"]["peak_snapshot_source_mw"]
    assumptions = {
        "upstream_kv": 33., "rectifier_ac_kv": 1.1, "transformer_mva": 8.,
        "line_r_ohm_per_km": .22, "line_x_ohm_per_km": .12, "line_max_ka": .30,
        "station_lateral_km": .35, "transformer_vk_percent": 6., "transformer_vkr_percent": .7,
        "rectifier_efficiency": .96, "power_factor": .95, "weak_grid_multiplier": 2.,
    }

    def solve(stress):
        a = assumptions
        net = pp.create_empty_network()
        supply_kv = a["upstream_kv"]
        supply = pp.create_bus(net, vn_kv=supply_kv, name="Illustrative 33 kV source")
        pp.create_ext_grid(net, supply, vm_pu=.97 if stress else 1.)
        for i, position in enumerate(sites):
            if i == failed:
                continue
            origin = pp.create_bus(net, vn_kv=supply_kv, name=f"Site {i} intake")
            secondary = pp.create_bus(net, vn_kv=a["rectifier_ac_kv"], name=f"Site {i} rectifier")
            lines = a["weak_grid_multiplier"] if stress else 1.
            length = a["station_lateral_km"] + abs(position - sites[-1] / 2) / 1000
            pp.create_line_from_parameters(net, supply, origin, length_km=length,
                                           r_ohm_per_km=a["line_r_ohm_per_km"] * lines,
                                           x_ohm_per_km=a["line_x_ohm_per_km"] * lines,
                                           c_nf_per_km=0., max_i_ka=a["line_max_ka"])
            pp.create_transformer_from_parameters(
                net, origin, secondary, sn_mva=a["transformer_mva"], vn_hv_kv=supply_kv,
                vn_lv_kv=a["rectifier_ac_kv"], vk_percent=a["transformer_vk_percent"],
                vkr_percent=a["transformer_vkr_percent"], pfe_kw=0., i0_percent=0.)
            active = float(peak.get(i, peak.get(str(i), 0.))) / a["rectifier_efficiency"]
            pp.create_load(net, secondary, p_mw=active, q_mvar=active * sqrt(1 / a["power_factor"]**2 - 1))
        try:
            pp.runpp(net, algorithm="nr", numba=False, tolerance_mva=1e-7)
        except pp.LoadflowNotConverged:
            return {"converged": False}
        vm = float(net.res_bus.vm_pu.min())
        line = float(net.res_line.loading_percent.max())
        xfmr = float(net.res_trafo.loading_percent.max())
        return {"converged": bool(net.converged), "minimum_bus_pu": vm,
                "max_line_loading_pct": line, "max_transformer_loading_pct": xfmr,
                "grid_mw": float(net.res_ext_grid.p_mw.iloc[0]),
                "grid_mvar": float(net.res_ext_grid.q_mvar.iloc[0]),
                "illustrative_screen_passed": vm >= .95 and max(line, xfmr) <= 100}

    return {"status": "verified execution", "tool": f"pandapower {pp.__version__}",
            "dc_evaluation_id": result["evaluation_id"], "assumptions": assumptions,
            "nominal": solve(False), "weak_grid": solve(True),
            "limitations": "Synthetic 33 kV source and separate site laterals from its midpoint. One-way DC peak to AC, balanced fundamental frequency only. Utility topology, impedance, harmonics and fault duties require authenticated utility data.",
            "utility_approved": False}
