"""Baghdad Airport time-domain rolling stock, service and sectioned DC research."""

from bisect import bisect_left, bisect_right
from collections import defaultdict, deque
from dataclasses import asdict, dataclass, field
from hashlib import sha256
import csv
import json
from math import isfinite, sqrt
from pathlib import Path
import tomllib
from zipfile import ZipFile

from cities.Baghdad import airport_opening, airport_service
from cities.Baghdad.engineering.commissioning import feeder
from cities.Baghdad.engineering.simulation.motion_dc import Feeder, loadflow
from engineering.outline import baghdad_diagrams as diagrams
from engineering.outline.baghdad_system import _id

CONDITIONS = ("normal", "hot", "site_out", "path_out", "combined")
METHOD_SOURCES = [
    "https://scholarworks.aub.edu.lb/items/001f9c49-7a43-414d-bb8f-17e74d57ab98",
    "https://sumo.dlr.de/docs/Simulation/Railways.html",
    "https://sumo.dlr.de/userdoc/Simulation/Output/TripInfo.html",
    "https://pandapower.readthedocs.io/en/latest/powerflow/ac.html",
]


def reference():
    cfg, report, _ = airport_opening.opening_inputs()
    group = report["networks"]["first"]["groups"]["Airport"]
    archive = Path(airport_opening.CITY) / "engineering/prototype/airport-prototype.zip"
    with ZipFile(archive) as packet:
        opening_bytes = packet.read("opening.json")
        manifest = json.loads(packet.read("manifest.json"))
        parent = json.loads(opening_bytes)
        if (sha256(opening_bytes).hexdigest() != manifest["sha256"]["opening.json"]
                or manifest["candidate_id"] != parent["candidate_id"]
                or parent["timetable_id"] != report["evaluation_id"]):
            raise ValueError("Airport prototype opening receipt or timetable binding differs")
        scope = {}
        for name, source in (("radial30", "priced_radial"), ("paired6", "six_site_parallel")):
            scope[name] = feeder.topology(parent, source)
    feeder.binding(parent)
    study_bytes = airport_service.TRIAL.read_bytes()
    if sha256(study_bytes).hexdigest() != parent["sources"][str(airport_service.TRIAL.relative_to(diagrams.system.ROOT))]:
        raise ValueError("Airport section trial inputs differ from the retained feeder basis")
    study = tomllib.loads(study_bytes.decode())
    return cfg, group, parent, scope, study


def make_feeder(name, chainages, conductor_factor, references=None, *, alignment_id=None):
    _, _, _, scopes, _ = references or reference()
    if name in scopes:
        raw = scopes[name]["design"]
        sites = tuple(x * 1000 for x in raw["site_chainage_km"])
        if alignment_id is not None:
            # Re-site station feeds at the new stops and radial feeds at equal
            # distances. Equipment and working access still require local offers.
            sites = (tuple(chainages) if name == "paired6" else
                     tuple(i * chainages[-1] / (len(sites) - 1) for i in range(len(sites))))
    else:
        raw = scopes["paired6"]["design"]
        if name == "paired8":
            sites = tuple(index * chainages[-1] / 7 for index in range(8))
        elif name == "paired6_shifted":
            sites = (0., chainages[1] + 300, chainages[2] - 300,
                     chainages[3] + 300, chainages[4] - 300, chainages[-1])
        elif name == "paired6_heavy":
            sites = tuple(chainages)
            conductor_factor *= .75
        else:
            raise ValueError(f"Unknown DC topology {name}")
    return Feeder(name, sites, raw["droop_ohm"], raw["outward_ohm_per_km"],
                  raw["return_ohm_per_km"], raw.get("parallel_positive_paths", 1), conductor_factor)


def service(case, references=None):
    cfg, parent, *_ = references or reference()
    chainages = case["chainages_m"]
    stops = [{**stop, "fraction": p / chainages[-1]}
             for stop, p in zip(parent["outward_stops"], chainages)]
    headway = case["headway_min"] * 60
    v = cfg["vehicle"]
    cfg = {**cfg, "vehicle": {**v, "peak_headway_s": headway, "dwell_s": case["dwell_s"],
                              "speed_cap_kmh": case.get("speed_cap_kmh", v["speed_cap_kmh"]),
                              "commercial_speed_kmh": case.get("commercial_speed_kmh", v["commercial_speed_kmh"])},
           "service_plan": {**cfg["service_plan"], "departures_per_hour_direction":
                            [3600 // headway] * v["service_hours_per_day"]},
           "vehicle_geometry": {**cfg["vehicle_geometry"], "train_length_m": case["length_m"]}}
    group, trips, patterns = diagrams.group_diagram("Airport", stops, chainages[-1] / 1000, cfg)
    profiles = airport_service.leg_profiles(patterns, chainages[-1] / 1000, cfg)
    phase = case["phase_s"]
    if phase is not None and phase != group["terminal_B_phase_s"]:
        phase_delta = phase - group["terminal_B_phase_s"]
        ready = [deque(), deque()]
        reworked = []
        count = 0
        for start, side in sorted((dep + side * phase_delta, side) for _, side, dep, _ in trips):
            if ready[side] and ready[side][0][0] <= start:
                _, unit = ready[side].popleft()
            else:
                count += 1
                unit = f"Airport-{count:03}"
            arrival = start + group["one_way_s_including_dwell"]
            ready[1 - side].append((arrival + group["minimum_turn_s"], unit))
            reworked.append((unit, side, start, arrival))
        trips = reworked
        group = {**group, "diagrammed_sets": count, "terminal_B_phase_s": phase}
    positioning = airport_service.positioning_trips(trips, group)
    slack = case.get("positioning_slack_s", 0)
    if slack:
        # Keep passenger slots and their minimum turn. Book extra terminal
        # waiting only around the first and last empty workings of each set.
        shifted = []
        for unit, side, dep, arr in positioning:
            offset = -slack if side == 0 else slack
            shifted.append((unit, side, dep + offset, arr + offset))
        positioning = sorted(shifted, key=lambda work: work[2])
    terminal = airport_service.terminal_screen(cfg, group, trips + positioning, patterns, profiles)
    return group, trips, patterns, profiles, positioning, terminal


def normalize(inputs, references=None):
    cfg, _, parent, _, trial = references or reference()
    case = {
        "headway_min": 15, "cars": 6, "material": "steel", "topology": "radial30",
        "loaded_train_kg": 201550., "tare_train_kg": 149050.,
        "grade_pct": 0., "demand_factor": 1., "conductor_factor": 1.,
        "condition": "normal", "dwell_s": cfg["vehicle"]["dwell_s"], "step_s": 2., "auxiliary_kw": None,
        "chainages_km": [0., 2.4, 4.8, 7.2, 9.6, 12.], "delay_s": 0., "phase_s": None,
        "od_matrix": None, "hourly_od": None, "failed_site": None, "failed_path": None, "places_per_train": None,
    }
    case.update({k: inputs[k] for k in case.keys() & inputs.keys() if inputs[k] is not None})
    if case["headway_min"] not in (15, 20, 30) or case["cars"] not in (3, 6):
        raise ValueError("Require a 15-, 20- or 30-minute service and a three- or six-car train")
    if case["phase_s"] is None and case["headway_min"] == 20:
        case["phase_s"] = 600
    if case["phase_s"] is not None and not 0 <= case["phase_s"] < 60 * case["headway_min"]:
        raise ValueError("Terminal phase falls outside the requested headway")
    if case["condition"] not in CONDITIONS or case["step_s"] not in (1, 2, 3, 4):
        raise ValueError("Unknown condition or step interval")
    if not 0 < case["tare_train_kg"] <= case["loaded_train_kg"] <= 400000:
        raise ValueError("Invalid train load")
    if not 0 <= case["delay_s"] <= 1800 or not 5 <= case["dwell_s"] <= 120:
        raise ValueError("Delay or dwell outside study domain")
    if not .5 <= case["conductor_factor"] <= 1.5:
        raise ValueError("Conductor resistance scaling outside study domain")
    if (not 0 <= case["demand_factor"] <= 2 or type(case["grade_pct"]) not in (int, float)
            or not isfinite(case["grade_pct"]) or abs(case["grade_pct"]) > 2):
        raise ValueError("Demand and constant grade must stay inside the stated planning domain")
    grade_basis = inputs.get("grade_basis")
    if grade_basis not in (None, "constant_sensitivity"):
        raise ValueError("Use grade_basis='constant_sensitivity' for a scalar grade override")
    if grade_basis is not None:
        case["grade_basis"] = grade_basis
    chainages = tuple(float(x) * 1000 for x in case.pop("chainages_km"))
    if inputs.get("alignment") is not None:
        from .airport_alignment import validate
        alignment = validate(inputs["alignment"])
        if (alignment["parent_candidate_id"] != parent["candidate_id"] or
                tuple(x * 1000 for x in alignment["chainages_km"]) != chainages):
            raise ValueError("Moving service and alignment must share the source candidate and stop chainages")
        from .airport_demand import speed_offer
        offered_speed = speed_offer(alignment, cfg)
        case["speed_cap_kmh"] = offered_speed["speed_cap_kmh"]
        case["commercial_speed_kmh"] = offered_speed["commercial_speed_kmh"]
        case["speed_offer"] = offered_speed
        if alignment.get("speed_profile") is not None:
            case["speed_profile"] = alignment["speed_profile"]
        from .airport_demand import validate as validate_demand
        demand = inputs.get("demand_record")
        if demand is None:
            raise ValueError("Revised alignment requires its candidate-bound demand record")
        validate_demand(demand, alignment)
        if (demand["service_offer"]["observation_context"]["speed_cap_kmh"] != case["speed_cap_kmh"]
                or not isfinite(case["commercial_speed_kmh"])
                or abs(demand["service_offer"]["observation_context"]["commercial_speed_kmh"]
                       - case["commercial_speed_kmh"]) > 1e-9):
            raise ValueError("Moving service and demand must share the restricted route speed offer")
        if (case["headway_min"] != demand["headway_min"] or case["dwell_s"] != demand["dwell_s"]
                or case["od_matrix"] is not None or case["demand_factor"] != 1
                or case["hourly_od"] is not None and case["hourly_od"] != demand["hourly_od"]):
            raise ValueError("Moving service and demand must share the same timetable and hourly OD")
        if (demand["mode"] == "observed" and
                case["cars"] != demand["service_offer"]["observation_context"]["formation_cars"]):
            raise ValueError("Moving service formation must match the observed demand service offer")
        case["hourly_od"] = demand["hourly_od"]
        case["demand_evaluation_id"] = demand["evaluation_id"]
        case["alignment_id"] = alignment["alignment_id"]
        profile = alignment["grade_profile"]
        if profile is not None and grade_basis is None:
            if case["grade_pct"] != 0:
                raise ValueError("A profiled alignment requires zero scalar grade or an explicit constant sensitivity")
            if any(not isfinite(grade) or abs(grade) > 2 for grade in profile["grades_pct"]):
                raise ValueError("Profiled grade exceeds the motion model's ±2% planning domain")
            case["grade_profile"] = profile
    elif chainages[-1:] != (12000.,):
        raise ValueError("Supply a source-bound alignment for a revised Airport route")
    if "positioning_slack_s" in inputs:
        slack = inputs["positioning_slack_s"]
        if "alignment_id" not in case or type(slack) is not int or not 0 <= slack <= 60 * case["headway_min"]:
            raise ValueError("Positioning slack requires a revised alignment and whole seconds up to one headway")
        case["positioning_slack_s"] = slack
    if len(chainages) != 6 or chainages[0] != 0 or sorted(set(chainages)) != list(chainages):
        raise ValueError("Six ordered Airport stops starting at zero are required")
    case["chainages_m"] = chainages
    case["length_m"] = case["cars"] * cfg["vehicle_geometry"]["car_body_length_m"] + (case["cars"] - 1) * .5
    case["acceleration_m_s2"] = cfg["power_assumptions"]["required_net_accel_m_s2"]
    case["braking_m_s2"] = trial["braking_deceleration_m_s2"]
    case["speed_m_s"] = case.get("speed_cap_kmh", cfg["vehicle"]["speed_cap_kmh"]) / 3.6
    case["efficiency"] = cfg["power_assumptions"]["traction_efficiency"]
    case["regen_efficiency"] = trial["braking_wheel_to_bus_efficiency"]
    if case["auxiliary_kw"] is not None and not 0 < case["auxiliary_kw"] <= 1500:
        raise ValueError("Full-train auxiliary power falls outside the 0–1500 kW study domain")
    case["aux_w"] = (case["auxiliary_kw"] * 1000 if case["auxiliary_kw"] is not None
                     else trial["auxiliaries_mw_per_train"] * 1e6 * case["cars"] / 6)
    case["traction_w"] = parent["section_power"]["assumptions"]["train_traction_rating_mw"] * 1e6 * case["cars"] / 6
    if case["places_per_train"] is not None and not 0 < case["places_per_train"] <= 700 * case["cars"] // 6:
        raise ValueError("Places per train outside the studied formation envelope")
    case["capacity"] = case["places_per_train"] or cfg["vehicle"]["normal_places_per_train"] * case["cars"] // 6
    if case["hourly_od"] is not None:
        if len(case["hourly_od"]) != 24:
            raise ValueError("hourly_od must contain one 6×6 matrix per local hour")
        for matrix in case["hourly_od"]:
            validate_od(matrix)
    if case["od_matrix"] is not None:
        validate_od(case["od_matrix"])
    case["resistance_m_s2"] = cfg["power_assumptions"]["resistance_accel_m_s2"]
    # Simulate forecast planning demand above a three-car physical capacity,
    # keeping denied boardings explicit. This does not infer new passenger load.
    return case


def grade_segment(profile, position_m, direction):
    """Select the segment ahead of the train at an exact vertical break."""
    breaks = profile["chainages_m"]
    index = (bisect_right if direction > 0 else bisect_left)(breaks, position_m) - 1
    return min(max(0, index), len(breaks) - 2)


def moving_grade(case, position_m, direction, yard):
    if yard:
        return 0.
    profile = case.get("grade_profile")
    local = case["grade_pct"] if profile is None else profile["grades_pct"][grade_segment(profile, position_m, direction)]
    return direction * local / 100


def profile_elevation(profile, position_m):
    index = grade_segment(profile, position_m, 1)
    return (profile["elevations_m"][index]
            + (position_m - profile["chainages_m"][index]) * profile["grades_pct"][index] / 100)


def validate_od(matrix):
    from math import isfinite

    if (len(matrix) != 6 or any(len(row) != 6 for row in matrix)
            or any(not isfinite(float(x)) or float(x) < 0 for row in matrix for x in row)):
        raise ValueError("OD requires a nonnegative finite 6×6 matrix in chainage order")


def default_od(hour, direction):
    # Explicit generated demand for code exercising only. Peak occupancy is
    # built up from demand by OD, rather than independently set on each leg.
    rush = 1.18 if 7 <= hour < 10 or 16 <= hour < 20 else .67 if 11 <= hour < 15 else .86
    if (direction == 0 and hour >= 15) or (direction == 1 and hour < 11):
        rush *= .85
    base = [(0, 2, 300), (0, 5, 480), (1, 3, 350), (1, 5, 270),
            (2, 4, 380), (2, 5, 310), (3, 5, 370), (4, 5, 250)]
    matrix = [[0.] * 6 for _ in range(6)]
    for i, j, rate in base:
        a, b = (i, j) if direction == 0 else (5-i, 5-j)
        matrix[a][b] = rate * rush
    return matrix


def riders_by_leg(case, clock_s, direction, empty, offsets, queue):
    if empty or case["hourly_od"] is not None:
        return [0.] * 5, 0., 0.
    order = list(range(6)) if direction == 0 else list(reversed(range(6)))
    onboard = defaultdict(float)
    riders = []
    boarded_total = denied = 0.
    for i, origin in enumerate(order[:-1]):
        onboard.pop(origin, None)
        booked_call = clock_s + offsets[i]
        t = booked_call - case["headway_min"] * 60
        while t < booked_call:
            hour = int(t // 3600) % 24
            end = min(booked_call, (t // 3600 + 1) * 3600)
            if case["od_matrix"] is not None:
                matrix = case["od_matrix"]
            else:
                matrix = default_od(hour, direction)
            for dest in order[i + 1:]:
                queue[(origin, dest)] += float(matrix[origin][dest]) * (end - t) / 3600 * case["demand_factor"]
            t = end
        available = max(0., case["capacity"] - sum(onboard.values()))
        waiting = sum(queue[(origin, dest)] for dest in order[i + 1:])
        ratio = min(1., available / waiting) if waiting else 0.
        for dest in order[i + 1:]:
            boarded = queue[(origin, dest)] * ratio
            onboard[dest] += boarded
            boarded_total += boarded
            queue[(origin, dest)] -= boarded
        denied += max(0., waiting - available)
        riders.append(sum(onboard.values()))
    return riders, denied, boarded_total


@dataclass
class Job:
    id: str
    unit: str
    side: int
    scheduled: float
    arrival: float
    kind: str
    points: tuple
    offsets: tuple
    speeds: tuple
    riders: list
    denied: float
    boarded: float


@dataclass
class Train:
    job: Job
    position: float
    speed: float = 0.
    leg: int = 0
    ready: float = 0.
    moving: bool = False
    old_block: tuple | None = None
    prior_terminal: int | None = None
    gain: float = 0.
    departed: float | None = None
    arrived: float | None = None
    onboard: dict = field(default_factory=dict)


class HourlyPassengerLedger:
    """Queue hourly OD against actual boarding calls on one local civil day."""

    def __init__(self, case):
        self.od = case["hourly_od"]
        self.factor = case["demand_factor"]
        self.capacity = case["capacity"]
        self.last_call = defaultdict(float)
        self.waiting = defaultdict(float)
        self.offered = self.factor * sum(float(flow) for matrix in self.od
                                         for a, row in enumerate(matrix) for b, flow in enumerate(row) if a != b)
        self.released = self.boarded = self.carried = self.denied = 0.

    def board(self, train, clock):
        job = train.job
        if job.kind != "passenger":
            return
        origin = train.leg if job.side == 0 else 5 - train.leg
        destinations = range(origin + 1, 6) if job.side == 0 else range(origin - 1, -1, -1)
        key = (origin, job.side)
        t = self.last_call[key]
        cutoff = max(t, min(clock, 86400))
        while t < cutoff:
            hour = int(t // 3600)
            stop = min(cutoff, (hour + 1) * 3600)
            for destination in destinations:
                flow = float(self.od[hour][origin][destination]) * (stop - t) / 3600 * self.factor
                self.waiting[origin, destination] += flow
                self.released += flow
            t = stop
        self.last_call[key] = cutoff
        demand = sum(self.waiting[origin, dest] for dest in destinations)
        available = max(0., self.capacity - sum(train.onboard.values()))
        fraction = min(1., available / demand) if demand else 0.
        for dest in destinations:
            boarding = self.waiting[origin, dest] * fraction
            self.waiting[origin, dest] -= boarding
            train.onboard[dest] = train.onboard.get(dest, 0.) + boarding
        allocated = fraction * demand
        denied = max(0., demand - available)
        self.boarded += allocated
        self.denied += denied
        job.boarded += allocated
        job.denied += denied
        job.riders[train.leg] = sum(train.onboard.values())

    def alight(self, train):
        if train.job.kind == "passenger":
            destination = train.leg + 1 if train.job.side == 0 else 4 - train.leg
            self.carried += train.onboard.pop(destination, 0.)

    def totals(self):
        queued = sum(self.waiting.values())
        outside = max(0., self.offered - self.released)
        interrupted = max(0., self.boarded - self.carried)
        unserved = queued + outside + interrupted
        residual = self.offered - self.carried - unserved
        if abs(residual) > 1e-6:
            raise ArithmeticError("Hourly passenger ledger does not conserve offered OD")
        return dict(offered_passengers=self.offered, boarded_passengers=self.carried,
                    gross_boardings=self.boarded, denied_boarding_attempts=self.denied, unserved_passengers=unserved,
                    unserved_capacity_at_close=queued, unserved_service_boundary=outside,
                    unserved_incomplete_trip=interrupted, demand_balance_residual_passengers=residual)


def build_jobs(case, group, trips, patterns, profiles, positioning, terminal):
    jobs = defaultdict(list)
    demand_queue = defaultdict(float)
    for n, (unit, side, start, arrival, empty) in enumerate(sorted(
            [(*x, False) for x in trips] + [(*x, True) for x in positioning], key=lambda row: row[2])):
        offsets = tuple(s["departure_s"] for s in patterns[side])
        riders, denied, boarded = riders_by_leg(case, start, side, empty, offsets, demand_queue)
        points = case["chainages_m"]
        jobs[unit].append(Job(f"trip-{n:03}", unit, side, start, arrival,
                            "positioning" if empty else "passenger", points if side == 0 else points[::-1],
                            offsets, tuple(p["cruise_m_s"] for p in profiles[side]), riders, denied, boarded))
    for n, row in enumerate(terminal["yard_moves"]):
        outward = row["kind"] == "depot to platform"
        points = (-250., 0.) if outward else (0., -250.)
        unit = row["train"]
        jobs[unit].append(Job(f"yard-{n:02}", unit, 0 if outward else 1, row["start_s"], row["end_s"],
                              "yard", points, (0.,), (10 / 3.6,), [0.], 0., 0.))
    return {k: deque(sorted(v, key=lambda job: job.scheduled)) for k, v in jobs.items()}, sum(demand_queue.values())


def open_csv(stack, directory, name, fields):
    if directory is None:
        return None
    file = stack.enter_context((directory / name).open("w", newline=""))
    writer = csv.DictWriter(file, fieldnames=fields)
    writer.writeheader()
    return writer


def drive_request(train, target, cap, resistance, mass, case, step):
    v = train.speed
    distance = abs(target - train.position)
    brake = case["braking_m_s2"]
    # Finish the current trapezoidal integration step with sufficient remaining
    # distance to stop under the declared service deceleration.
    next_v = max(0., sqrt(max(0., (brake * step / 2) ** 2 + 2 * brake * max(0., distance - v * step / 2)))
                 - brake * step / 2)
    accel = min(case["acceleration_m_s2"], (min(cap, next_v) - v) / step)
    accel = max(-brake, accel)
    wheel_force = mass * (accel + resistance)
    mean_speed = max(0., v + accel * step / 2)
    wheel_power = wheel_force * mean_speed
    if wheel_power >= 0:
        bus = min(case["traction_w"], wheel_power / case["efficiency"])
    else:
        bus = wheel_power * case["regen_efficiency"]
    return wheel_force, bus


def realize(train, force, bus_w, mass, resistance, case, step):
    if force > 0:
        # Solve wheel work over the same step used to integrate position.
        # P = F*(u + dt*(F/m - r)/2), including starts from rest.
        half = step / 2
        b = train.speed - resistance * half
        wheel_w = max(0., bus_w) * case["efficiency"]
        delivered = mass / (2 * half) * (sqrt(b * b + 4 * half * wheel_w / mass) - b) if wheel_w else 0.
        force = min(force, delivered)
    generated_accel = force / mass - resistance
    speed = max(0., train.speed + step * generated_accel)
    travel = (train.speed + speed) * step / 2
    return speed, travel, force

def evaluate(inputs, output_dir=None):
    """Run the entire working day for one explicitly identified configuration."""
    from contextlib import ExitStack
    from shutil import disk_usage

    references = reference()
    case = normalize(inputs, references)
    grade_profile = case.get("grade_profile")
    supply = make_feeder(case["topology"], case["chainages_m"], case["conductor_factor"], references,
                         alignment_id=case.get("alignment_id"))
    failed_site = case["failed_site"] if case["failed_site"] is not None else len(supply.sites) // 2
    failed_path = case["failed_path"] if case["failed_path"] is not None else min(failed_site, len(supply.sites) - 2)
    if not 0 <= failed_site < len(supply.sites) or not 0 <= failed_path < len(supply.sites) - 1:
        raise ValueError("Outage indices outside feeder topology")
    circuit = supply.circuit(case["condition"], failed_site, failed_path)
    cfg, _, parent, scopes, _ = references
    group, trips, patterns, profiles, positioning, terminal = service(case, references)
    queues, remaining_demand = build_jobs(case, group, trips, patterns, profiles, positioning, terminal)
    hourly = HourlyPassengerLedger(case) if case["hourly_od"] is not None else None
    total_boarded = sum(job.boarded for queue in queues.values() for job in queue)
    completed_boarded = 0.
    physical = {"parent": parent["candidate_id"], "formation": case["cars"], "material": case["material"],
                "upstream_candidate_id": inputs.get("candidate_id"),
                "feeder": asdict(supply), "chainages_m": case["chainages_m"]}
    if "alignment_id" in case:
        physical["alignment_id"] = case["alignment_id"]
    candidate_id = _id(physical)
    evaluation_id = _id({"candidate": candidate_id, "scenario": case,
                         "retained_opening_evaluation": parent["evaluation_id"],
                         "upstream_candidate": inputs.get("candidate_id"),
                         "motion_code": sha256(Path(__file__).read_bytes()).hexdigest(),
                         "dc_code": sha256(Path(__file__).with_name("motion_dc.py").read_bytes()).hexdigest()})
    directory = Path(output_dir).resolve() if output_dir is not None else None
    if directory is not None:
        directory.mkdir(parents=True, exist_ok=True)
        if disk_usage(directory).free < 20 * 2**30 + 150 * 2**20:
            raise RuntimeError("Insufficient disk space for motion and DC trace above 20 GiB floor")
    step = case["step_s"]
    resources = {}
    active = {}
    events = []
    summary_trace = []
    site_squares = defaultdict(float)
    site_peaks = defaultdict(float)
    branch_peaks = defaultdict(float)
    branch_squares = defaultdict(float)
    totals = defaultdict(float)
    dark_blocks = {(side, index) for side, points in enumerate((case["chainages_m"], case["chainages_m"][::-1]))
                   for index, (lo, hi) in enumerate(zip(points, points[1:]))
                   if circuit.failed_path is not None and circuit.paths == 1
                   and max(min(lo, hi), supply.sites[circuit.failed_path])
                   < min(max(lo, hi), supply.sites[circuit.failed_path + 1])}
    v_min, v_max = float("inf"), 0.
    max_residual = 0.
    clock = min(q[0].scheduled for q in queues.values())
    first = clock
    last_booked = max(q[-1].arrival for q in queues.values())
    next_snapshot = clock
    current_limit = (case["traction_w"] + case["aux_w"]) / 1350
    power_factor = 1.05 if case["condition"] == "combined" else 1.
    locked = float("inf")
    min_gap = float("inf")

    def free(resource, owner):
        occupancy = resources.get(resource)
        return occupancy is None or occupancy[0] == owner or occupancy[1] <= clock

    def claim(resource, owner):
        resources[resource] = (owner, locked)

    def release(resource, owner, at):
        if resources.get(resource, (None,))[0] == owner:
            resources[resource] = (owner, at)

    def next_job(unit, prior=None):
        if queues[unit]:
            job = queues[unit].popleft()
            ready = job.scheduled
            if prior is not None:
                turn = group["minimum_turn_s"] if "yard" not in (prior.job.kind, job.kind) else 0
                ready = max(ready, prior.arrived + turn)
            if job.kind == "passenger" and job.side == 0 and job.scheduled == trips[0][2]:
                ready += case["delay_s"]
            active[unit] = Train(job, job.points[0], ready=ready,
                                 prior_terminal=prior.prior_terminal if prior else None)
        else:
            active.pop(unit, None)

    for unit in queues:
        next_job(unit)

    with ExitStack() as stack:
        lease = None
        if directory is not None:
            from engineering.performance import check_disk_reservation, disk_reservation
            lease = stack.enter_context(disk_reservation(Path(__file__).resolve().parents[4], directory,
                                                         "Baghdad Airport motion DC traces", 150 * 2**20))
        trace_writer = open_csv(stack, directory, "motion-dc-trace.csv", [
            "time_s", "unit", "trip", "kind", "direction", "leg", "chainage_m",
            "speed_m_s", "next_chainage_m", "next_speed_m_s", "mass_kg", "passengers", "grade_pct", "effort_n", "collector_v",
            "collector_kw", "requested_kw", "regen_curtailed_kw", "site", "occupied_block",
        ])
        power_writer = open_csv(stack, directory, "motion-dc-sites.csv", [
            "time_s", "site", "current_a", "source_kw", "loss_kw", "residual_v", "branch_peak_a",
        ])
        while active and clock <= last_booked + 1800:
            if lease is not None and int(clock) % 300 < step:
                check_disk_reservation(lease)
            by_site = defaultdict(list)
            sample = clock >= next_snapshot
            sample_trains = []
            pending_arrivals = []
            for unit, train in active.items():
                job = train.job
                yard = job.kind == "yard"
                leg = train.leg
                start, target = job.points[leg:leg + 2]
                track = job.side
                block = ("block", track, leg)
                at_term = leg == 0
                final = leg == len(job.points) - 2
                across = 1 if target >= start else -1
                station = (job.side if at_term else None) if not yard else 0
                dest = 1 - job.side if final and not yard else 0 if final and job.side == 0 else None
                if not train.moving and clock >= train.ready:
                    needs = []
                    if yard or at_term:
                        needs.append(("throat", station))
                        if yard and job.side == 0:
                            needs.append(("face", station))
                    if not yard:
                        needs.append(block)
                    if dest is not None and not yard:
                        # A conservative overlap reservation protects a stopped
                        # train from entering the final block without a berth.
                        needs.extend([("face", dest), ("throat", dest)])
                    if not yard and (track, leg) in dark_blocks:
                        totals["protected_hold_train_s"] += step
                    elif all(free(key, unit) for key in needs):
                        for key in needs:
                            claim(key, unit)
                        depart_offset = clock - job.scheduled - job.offsets[leg]
                        train.gain = min(2., max(0., depart_offset - 3) * .04)
                        if train.departed is None:
                            train.departed = clock
                            if not yard:
                                lane = ("last_departure", track)
                                previous = resources.get(lane)
                                if previous and job.kind == "passenger":
                                    min_gap = min(min_gap, clock - previous[1])
                                if job.kind == "passenger":
                                    resources[lane] = (unit, clock)
                        train.moving = True
                        if hourly is not None:
                            hourly.board(train, clock)
                    else:
                        totals["resource_wait_s"] += step
                # Leading train clears the previous block only after its tail
                # and the route locking margin have passed its exit point.
                advanced = abs(train.position - start)
                if train.moving and train.old_block is not None and advanced >= case["length_m"]:
                    release(train.old_block, unit, clock + 15)
                    train.old_block = None
                if train.moving and train.prior_terminal is not None and advanced >= 100 + case["length_m"]:
                    for key in ("face", "throat"):
                        release((key, train.prior_terminal), unit, clock + 15)
                    train.prior_terminal = None
                if train.moving and at_term and not yard and advanced >= 100 + case["length_m"]:
                    release(("throat", station), unit, clock + 15)
                # Trains in the depot draw no line power until the yard path is
                # granted. Stationary trains on the line retain their aux load.
                if not train.moving and train.position < 0 and job.kind == "yard":
                    continue
                riders = job.riders[leg]
                mass = case["tare_train_kg"] + riders / case["capacity"] * (case["loaded_train_kg"] - case["tare_train_kg"])
                grade = moving_grade(case, train.position, across, yard)
                drag = 0. if yard else case["resistance_m_s2"]
                resistance = 9.81 * grade + drag
                effort = drive = 0.
                if train.moving:
                    cap = min(case["speed_m_s"], job.speeds[leg] + (0. if yard else train.gain))
                    effort, drive = drive_request(train, target, cap, resistance, mass, case, step)
                port = circuit.port(train.position, track)
                request = power_factor * (case["aux_w"] + max(0., drive)) + min(0., drive)
                row = (train, port, request, effort, drive, mass, resistance, grade, riders, target, across, block)
                by_site[port[0] if port else None].append(row)
            total_source_w = 0.
            site_snapshot = {}
            for site, rows in by_site.items():
                if site is None:
                    volts, accepted, source_current, losses, residual, branch = (
                        [0.] * len(rows), [0.] * len(rows), 0., 0., 0., 0.)
                else:
                    volts, accepted, source_current, losses, residual, branch = loadflow(
                        circuit, [r[1] for r in rows], [r[2] for r in rows], current_limit)
                    site_peaks[site] = max(site_peaks[site], source_current)
                    branch_peaks[site] = max(branch_peaks[site], branch)
                    site_squares[site] += source_current**2 * step
                    branch_squares[site] += branch**2 * step
                    max_residual = max(max_residual, residual)
                    if residual >= .05:
                        totals["unconverged_site_steps"] += 1
                source_w = source_current * circuit.source_v
                if site is not None:
                    site_snapshot[site] = source_w / 1e6
                total_source_w += source_w
                totals["source_ws"] += source_w * step
                totals["loss_ws"] += losses * step
                if power_writer:
                    power_writer.writerow(dict(time_s=clock, site=site, current_a=round(source_current, 3),
                                               source_kw=round(source_w / 1000, 3), loss_kw=round(losses / 1000, 3),
                                               residual_v=round(residual, 5), branch_peak_a=round(branch, 3)))
                for row, voltage, collector in zip(rows, volts, accepted):
                    (train, _, request, effort, drive, mass, resistance, grade, riders,
                     target, across, block) = row
                    job = train.job
                    yard = job.kind == "yard"
                    sold_traction = min(drive, max(0., collector / power_factor - case["aux_w"])) if drive > 0 else 0.
                    regen_bus = max(0., -drive)
                    regen_network = max(0., -collector)
                    regen_local = min(case["aux_w"] * power_factor, regen_bus)
                    if site is None:
                        totals["dark_train_s"] += step
                    if voltage < 1350:
                        totals["below_floor_train_s"] += step
                    if sold_traction < drive - 100:
                        totals["curtailed_traction_train_s"] += step
                    if (0 < voltage < 1350 or site is None) and train.moving:
                        totals["moving_below_floor_s"] += step
                    v_min, v_max = min(voltage, v_min), max(voltage, v_max)
                    totals["collector_ws"] += collector * step
                    totals["regen_potential_ws"] += regen_bus * step
                    totals["regen_network_ws"] += regen_network * step
                    totals["regen_local_ws"] += regen_local * step
                    rejected = max(0., regen_bus - regen_network - regen_local)
                    totals["regen_rejected_ws"] += rejected * step
                    old_position, old_speed = train.position, train.speed
                    was_moving = train.moving
                    if train.moving:
                        speed, travel, effort = realize(train, effort, sold_traction, mass, resistance, case, step)
                        remain = abs(target - train.position)
                        if travel >= remain:
                            if speed > case["braking_m_s2"] * step + .1:
                                totals["high_speed_stop_events"] += 1
                            speed, travel = 0., remain
                        totals["distance_m"] += travel
                        totals["traction_wheel_ws"] += max(0., effort * travel)
                        totals["braking_wheel_ws"] += max(0., -effort * travel)
                        totals["mechanical_balance_ws"] += (
                            (effort - mass * resistance) * travel - mass * (speed**2 - old_speed**2) / 2
                        )
                        if grade_profile is not None and not yard and travel:
                            new_position = old_position + across * travel
                            if grade_segment(grade_profile, old_position, across) != grade_segment(grade_profile, new_position, -across):
                                elevation_change = (profile_elevation(grade_profile, new_position)
                                                    - profile_elevation(grade_profile, old_position))
                                grade_error = mass * 9.81 * (grade * travel - elevation_change)
                                totals["mechanical_balance_ws"] += grade_error
                                totals["vertical_break_step_absolute_error_ws"] += abs(grade_error)
                        train.position += across * travel
                        train.speed = speed
                        if travel >= remain or (remain - travel < .12 and speed < .15):
                            train.position = target
                            train.speed = 0.
                            train.moving = False
                            final = train.leg == len(job.points) - 2
                            arrival = clock + step
                            if hourly is not None:
                                hourly.alight(train)
                            if not yard and final:
                                release(block, job.unit, arrival + 15)
                            elif not yard:
                                train.old_block = block
                            if final:
                                train.arrived = arrival
                                if yard:
                                    release(("throat", 0), job.unit, arrival + 15)
                                    if job.side == 1:
                                        release(("face", 0), job.unit, arrival + 15)
                                    train.prior_terminal = 0 if job.side == 0 else None
                                else:
                                    dest = 1 - job.side
                                    release(("throat", dest), job.unit, arrival + 15)
                                    train.prior_terminal = dest
                                pending_arrivals.append(job.unit)
                            else:
                                train.leg += 1
                                train.ready = max(arrival + case["dwell_s"], job.scheduled + job.offsets[train.leg])
                    if sample or trace_writer:
                        record = dict(
                            time_s=clock, unit=job.unit, trip=job.id, kind=job.kind, direction=job.side,
                            leg=block[-1], chainage_m=round(old_position, 2), speed_m_s=round(old_speed, 3),
                            next_chainage_m=round(train.position, 2), next_speed_m_s=round(train.speed, 3),
                            mass_kg=round(mass, 1), passengers=round(riders, 1), grade_pct=round(grade * 100, 3),
                            effort_n=round(effort, 1), collector_v=round(voltage, 2), collector_kw=round(collector / 1000, 3),
                            requested_kw=round(request / 1000, 3), regen_curtailed_kw=round(rejected / 1000, 3),
                            site=site, occupied_block=block if was_moving else None,
                        )
                        if trace_writer:
                            trace_writer.writerow(record)
                        if sample:
                            sample_trains.append(record)
            if total_source_w > totals["peak_source_w"]:
                totals["peak_source_w"] = total_source_w
                peak_snapshot = site_snapshot
            if sample:
                summary_trace.append({"time_s": clock, "source_mw": round(total_source_w / 1e6, 4),
                                      "trains": sample_trains})
                next_snapshot += 300
            for unit in pending_arrivals:
                train = active[unit]
                job = train.job
                events.append({"id": job.id, "unit": unit, "kind": job.kind, "direction": job.side,
                               "booked_departure_s": job.scheduled, "actual_departure_s": train.departed,
                               "booked_arrival_s": job.arrival, "actual_arrival_s": train.arrived,
                               "departure_delay_s": train.departed - job.scheduled,
                               "arrival_delay_s": train.arrived - job.arrival,
                               "maximum_onboard": round(max(job.riders), 1),
                               "denied_boarding_attempts": round(job.denied, 1),
                               "boarded_passengers": round(job.boarded, 3)})
                completed_boarded += job.boarded
                next_job(unit, train)
            clock += step

    completed = [event for event in events if event["kind"] == "passenger"]
    max_delay = max((ev["arrival_delay_s"] for ev in completed), default=None)
    denied = sum(event["denied_boarding_attempts"] for event in completed)
    offered = total_boarded + remaining_demand
    stranded = max(0., total_boarded - completed_boarded)
    demand = (hourly.totals() if hourly is not None else
              dict(offered_passengers=offered, boarded_passengers=completed_boarded,
                   gross_boardings=completed_boarded, denied_boarding_attempts=denied,
                   unserved_passengers=remaining_demand + stranded, unserved_capacity_at_close=remaining_demand,
                   unserved_service_boundary=0., unserved_incomplete_trip=stranded,
                   demand_balance_residual_passengers=0.))
    denied = demand["denied_boarding_attempts"]
    source_kwh = totals["source_ws"] / 3.6e6
    distance_km = totals["distance_m"] / 1000
    source_peak = totals["peak_source_w"] / 1e6
    peak_site = max(site_peaks, key=site_peaks.get, default=None)
    metrics = {key: round(value / 3.6e6, 4) if key.endswith("_ws") else value
               for key, value in totals.items() if key not in ("peak_source_w",)}
    metrics = {(k[:-3] + "_kwh" if k.endswith("_ws") else k): v for k, v in metrics.items()}
    if grade_profile is not None:
        metrics.setdefault("vertical_break_step_absolute_error_kwh", 0.)
    metrics.update(
        booked_passenger_trips=len(trips), completed_passenger_trips=len(completed),
        positioning_trips=len(positioning), completed_yard_trips=sum(e["kind"] == "yard" for e in events),
        diagrammed_sets=group["diagrammed_sets"], fleet_sets_required=group["diagrammed_sets"] + 3,
        terminal_B_phase_s=group["terminal_B_phase_s"],
        normal_places_per_hour_direction=case["capacity"] * (60 // case["headway_min"]),
        distance_km=distance_km, minimum_service_departure_gap_s=min_gap if min_gap != float("inf") else None,
        maximum_arrival_delay_s=max_delay, **{k: round(v, 6) for k, v in demand.items()},
        unserved_at_cutoff_or_incomplete_trips=True,
        minimum_collector_v=v_min if v_min != float("inf") else None,
        maximum_collector_v=v_max, max_dc_residual_v=max_residual,
        dc_balance_residual_kwh=(totals["source_ws"] - totals["collector_ws"] - totals["loss_ws"]) / 3.6e6,
        peak_site_index=peak_site,
        peak_site_current_ka=site_peaks.get(peak_site, 0.) / 1000,
        max_branch_current_ka=max(branch_peaks.values(), default=0.) / 1000,
        max_site_rms_current_ka=sqrt(max(site_squares.values(), default=0.) / (clock - first)) / 1000,
        bound_branch_rms_current_ka=sqrt(max(branch_squares.values(), default=0.) / (clock - first)) / 1000,
        rectifier_energy_balance_basis="sum IᵀRI independently of source and collector work",
        service_day_current_basis_seconds=clock - first,
        peak_snapshot_source_mw=peak_snapshot if source_peak else {},
        unresolved_units=sorted(active), nominal_timetable_conflicts=len(terminal["conflicts"]),
        max_early_arrival_s=max((-ev["arrival_delay_s"] for ev in completed), default=None),
    )
    passenger_km = len(trips) * case["chainages_m"][-1] / 1000
    positioning_km = len(positioning) * case["chainages_m"][-1] / 1000
    booked_km = passenger_km + positioning_km
    if "alignment_id" in case:
        yard_km = sum(move["distance_km"] for move in terminal["yard_moves"])
        booked_km += yard_km
        metrics.update(booked_positioning_trips=len(positioning),
                       completed_positioning_trips=sum(event["kind"] == "positioning" for event in events),
                       booked_yard_trips=len(terminal["yard_moves"]), booked_passenger_km=passenger_km,
                       booked_positioning_km=positioning_km, booked_yard_km=yard_km)
    gates = {
        "all_workings_complete": not active and len(completed) == len(trips),
        "service_within_arrival_envelope": max_delay is not None and max_delay <= 60,
        "capacity_screen": len(completed) == len(trips) and demand["unserved_capacity_at_close"] < .1 and denied < .1,
        "route_and_block_reservations": not terminal["conflicts"] and not totals["high_speed_stop_events"],
        "collector_voltage_screen": v_min >= 1350 and v_max <= 1650 and not totals["dark_train_s"],
        "dc_numerical_screen": max_residual < .05 and abs(metrics["dc_balance_residual_kwh"]) < .15,
        "motion_work_balance_screen": abs(metrics.get("mechanical_balance_kwh", 0.)) <=
            .002 * max(1., metrics.get("traction_wheel_kwh", 0.) + metrics.get("braking_wheel_kwh", 0.)),
        "electrical_isolation_screen": not dark_blocks,
        "protection_approved": False,
        "utility_connection_approved": False,
        "thermal_ratings_verified": False,
    }
    return {
        "schema": "baghdad-airport-motion-dc/1", "candidate_id": candidate_id, "evaluation_id": evaluation_id,
        "source_publication_candidate_id": parent["candidate_id"],
        "source_feeder_design_id": None if "alignment_id" in case else scopes.get(supply.name, {}).get("design_id"),
        "source_opening_evaluation_id": parent["evaluation_id"],
        "source_timetable_id": parent["timetable_id"],
        "physical": physical, "scenario": {k: v for k, v in case.items() if k not in ("hourly_od", "od_matrix")},
        "demand_basis": {"hourly_od": case["hourly_od"] is not None,
                         "od_id": _id(case["hourly_od"] or case["od_matrix"]) if case["hourly_od"] or case["od_matrix"] else None},
        "booked_annual_train_km": booked_km * cfg["vehicle"]["service_days_per_year"],
        "annual_train_km": distance_km * cfg["vehicle"]["service_days_per_year"],
        "energy_kwh_per_train_km": source_kwh / distance_km if distance_km else None,
        "peak_power_mw": source_peak, "gates": gates,
        "economic_ranking_eligible": all(gates.values()), "physical_accepted": False,
        "metrics": metrics, "events": events, "trace": summary_trace,
        "pending_workings": [{"unit": unit, "active_trip": train.job.id, "queued_trips": len(queues[unit]),
                              "position_m": round(train.position, 1), "leg": train.leg}
                             for unit, train in active.items()],
        "electrical_enquiry": electrical_enquiry(circuit, supply, metrics),
        "failure": {"site": failed_site if case["condition"] in ("site_out", "combined") else None,
                    "path_bay": circuit.failed_path,
                    "closed_service_blocks": sorted(dark_blocks)},
        "method_sources": METHOD_SOURCES,
        "limits": [
            "Steady resistive DC equivalent at each step. Return touch potential, intertrack leakage, harmonics, protection transients, converter duty and thermal ratings require separate evidence.",
            ("Signed local grade is evaluated at the start of each motion step. Vertical break crossing work error is tracked against the piecewise-linear profile. Yard grade is zero."
             if grade_profile is not None else
             "Illustrative constant signed elevation grade. The chainage and vertical datum await route survey and verified profile."),
            "Supplied hourly OD boards at actual departure calls. The generated benchmark demand uses booked station calls. Abandonment and transfers are outside the queue model.",
            "Train force includes declared constant resistance and grade. Brake recovery is capped by section demand with a conservative non-reversible rectifier. No field calibration.",
            "An isolated radial path blocks both affected directional interstation movements at their preceding stops. Combined paired-path run assumes the surviving branches are intact and open ties have been safely configured.",
            "One outage location per replay. The worst scheduled outage site or branch and restoration duration require their own campaign.",
        ],
    }


def unit_cost_basis(result):
    """Read matched scope lines; leave site, material and approval returns open."""
    name = result["physical"]["feeder"]["name"]
    if "alignment_id" in result["scenario"] or name not in ("radial30", "paired6") or result["physical"]["feeder"]["trunk_factor"] != 1.:
        return {"status": "held", "reason": "No scope-matched plant and conductor estimate for research layout"}
    file = Path(airport_opening.CITY) / "engineering/prototype/sourcing-estimate.json"
    lots = {r["lot_id"]: r for r in json.loads(file.read_text())["lots"]}
    if name == "paired6":
        direct = ("six-site-parallel",)
        upkeep = "six-site-parallel-upkeep"
        if lots[direct[0]]["design_id"] != result["source_feeder_design_id"]:
            raise ValueError("Paired feeder budget binds different physical infrastructure")
    else:
        direct = ("traction-line", "traction-sites", "offsite-feed")
        upkeep = "opex-feeder"
    cfg = airport_opening.system.load(network="first")
    power_cost = cfg["operation_rates"]["delivered_energy_usd_per_kwh"]
    efficiency = .96
    daily_grid_input = result["metrics"].get("source_kwh", 0.) / efficiency
    annual_energy = daily_grid_input * cfg["vehicle"]["service_days_per_year"] * power_cost
    return {
        "status": "planning estimate", "price_year": 2026, "direct_lots": direct, "upkeep_lot": upkeep,
        "source_sha256": sha256(file.read_bytes()).hexdigest(),
        "direct_usd": {k: sum(lots[lot][f"{k}_usd"] for lot in direct) for k in ("low", "base", "high")},
        "annual_upkeep_usd": {k: lots[upkeep][f"{k}_usd"] for k in ("low", "base", "high")},
        "annual_energy_if_completed_usd": annual_energy if result["gates"]["all_workings_complete"] else None,
        "rectifier_efficiency_for_energy_cost": efficiency,
        "installed_offer_usd": None, "renewal_price_usd": None,
    }


def electrical_enquiry(circuit, supply, metrics):
    """Retain branch and DC fault inputs for a protection/thermal return."""
    distances = [max(x - left, right - x) for (_, x), left, right in
                 zip(circuit.live, (0., *circuit.cuts_m), (*circuit.cuts_m, supply.sites[-1]))]
    longest = max(distances)
    lower_r = circuit.source_ohm + circuit.loop_ohm_m * longest + circuit.contact_ohm
    current = metrics["max_branch_current_ka"]
    return {
        "longest_restored_branch_m": longest,
        "observed_healthy_branch_peak_ka_no_sharing_credit": current,
        "upper_daily_branch_rms_ka_no_sharing_credit": metrics["bound_branch_rms_current_ka"],
        "ideal_bolted_near_bus_ka": circuit.source_v / circuit.source_ohm / 1000,
        "ideal_bolted_remote_single_path_ka": circuit.source_v / lower_r / 1000,
        "approval": "held",
        "limits": "Ideal DC Thévenin indicators exclude dynamic source current limiting, arcing, "
                  "contact resistance uncertainty and cable/bond temperature. Require utility fault "
                  "levels, protection pickup and clearing curves, thermal duty, isolation proof "
                  "and witness tests before equipment or operating approval.",
    }


def compact(result):
    return {k: v for k, v in result.items() if k not in ("trace", "events")}


def run(output_dir=None):
    """Bounded full-corridor benchmark with optional full CSV for the 15-minute radial case."""
    from concurrent.futures import ProcessPoolExecutor
    from cities.Baghdad.engineering.simulation.motion_adapters import ac_check, sumo_check

    base_cases = [
        {"topology": topology, "headway_min": headway, "condition": condition}
        for topology in ("radial30", "paired6")
        for headway in (15, 20, 30)
        for condition in CONDITIONS
    ]
    research = [
        {"topology": topology, "headway_min": 15, "condition": "combined", "grade_pct": 2,
         "demand_factor": 1.15, "delay_s": 120}
        for topology in ("radial30", "paired6", "paired8", "paired6_shifted", "paired6_heavy")
    ]
    research.extend([
        {"topology": "paired6", "headway_min": 15, "condition": "combined", "grade_pct": 2,
         "failed_site": 0, "failed_path": 0, "demand_factor": 1.15, "delay_s": 120},
        {"topology": "paired6", "headway_min": 15, "condition": "combined", "grade_pct": 2,
         "failed_site": 5, "failed_path": 4, "demand_factor": 1.15, "delay_s": 120},
        {"headway_min": 20, "phase_s": 117},
    ])
    fine_case = {"topology": "paired6", "headway_min": 15, "condition": "combined", "step_s": 1}
    nominal = evaluate(base_cases[0], output_dir)
    # Bounded independently evaluated samples. Workers write no shared result
    # files. This coordinator alone returns the ordered evaluation records.
    with ProcessPoolExecutor(max_workers=2) as pool:
        rows = [nominal, *pool.map(evaluate, base_cases[1:] + research + [fine_case])]
    nominal_by_topology = {r["scenario"]["topology"]: r for r in rows
                           if r["scenario"]["headway_min"] == 15 and r["scenario"]["condition"] == "normal"}
    for row in rows:
        row["feeder_cost"] = unit_cost_basis(row)
    equivalent = [
        {"headway_min": h,
         "booked_service_equal": len({r["metrics"]["booked_passenger_trips"] for r in rows[:len(base_cases)]
                                     if r["scenario"]["headway_min"] == h}) == 1,
         "eligible_evaluation_ids": [r["evaluation_id"] for r in rows[:len(base_cases)]
                                     if r["scenario"]["headway_min"] == h and r["economic_ranking_eligible"]],
         "ranking": "held pending approved protection, connection, thermal duty, renewal and comparable installed prices"}
        for h in (15, 20, 30)
    ]
    ac = {name: ac_check(row) for name, row in nominal_by_topology.items()}
    sumo = {}
    for h in (15, 20, 30):
        original = {"headway_min": h}
        row = next(r for r in rows if r["scenario"]["headway_min"] == h
                   and r["scenario"]["topology"] == "radial30" and r["scenario"]["condition"] == "normal")
        case = normalize(original)
        sumo[str(h)] = sumo_check(case, service(case), row["events"], output_dir)
    fine = rows[-1]
    coarse = next(r for r in rows if r["scenario"]["headway_min"] == 15
                  and r["scenario"]["topology"] == "paired6" and r["scenario"]["condition"] == "combined")
    comparison = {
        "fine_evaluation_id": fine["evaluation_id"], "coarse_evaluation_id": coarse["evaluation_id"],
        "daily_source_energy_difference_pct": (fine["metrics"]["source_kwh"] / coarse["metrics"]["source_kwh"] - 1) * 100,
        "minimum_collector_voltage_difference_v": fine["metrics"]["minimum_collector_v"] - coarse["metrics"]["minimum_collector_v"],
        "peak_source_power_difference_mw": fine["peak_power_mw"] - coarse["peak_power_mw"],
        "completed_passenger_trip_difference": fine["metrics"]["completed_passenger_trips"] - coarse["metrics"]["completed_passenger_trips"],
    }
    return {"schema": "baghdad-airport-motion-dc-benchmark/1",
            "selected_replay": nominal,
            "cases": [compact(row) for row in rows],
            "equal_service_comparisons": equivalent, "convergence": comparison,
            "sumo": sumo, "ac": ac, "physical_accepted": False}
