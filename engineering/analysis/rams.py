"""Small, bounded RAMS screening models. No deployment limits or rates are inferred."""
from __future__ import annotations

import itertools
import math


def number(value, name: str, *, minimum: float = 0) -> float:
    if type(value) not in (int, float) or not math.isfinite(value) or value < minimum:
        raise ValueError(f"{name} must be finite and >= {minimum}")
    return float(value)


def interval(row: dict, name: str, *, minimum: float = 0, unit: str | None = None) -> tuple[float, float] | None:
    if unit is not None and row.get("unit") != unit:
        raise ValueError(f"{name}: expected unit {unit}")
    if row.get("basis") not in {"unknown", "illustrative-assumption", "supplier-data", "measured"}:
        raise ValueError(f"{name} requires an explicit evidence basis")
    if row.get("low") is None and row.get("high") is None:
        if row["basis"] != "unknown":
            raise ValueError(f"{name}: absent bounds must remain unknown")
        return None
    if row["basis"] == "unknown":
        raise ValueError(f"{name}: unknown input cannot carry invented numeric bounds")
    low, high = number(row.get("low"), name, minimum=minimum), number(row.get("high"), name, minimum=minimum)
    if low > high:
        raise ValueError(f"{name}: lower bound exceeds upper bound")
    if row["basis"] in {"supplier-data", "measured"} and not row.get("evidence_ids"):
        raise ValueError(f"{name}: evidence-based input requires evidence IDs")
    return low, high


def temperature(t_s: float, *, initial_c: float, ambient_c: float,
                heat_w: float, capacity_j_k: float, conductance_w_k: float) -> float:
    t = number(t_s, "time")
    capacity = number(capacity_j_k, "thermal capacity", minimum=1e-12)
    heat = number(heat_w, "heat input")
    conductance = number(conductance_w_k, "conductance")
    initial = number(initial_c, "initial temperature", minimum=-273.15)
    ambient = number(ambient_c, "ambient temperature", minimum=-273.15)
    if conductance == 0:
        result = initial + heat / capacity * t
    else:
        response = -math.expm1(-conductance * t / capacity)
        heat_response = heat / capacity * t if response == 0 else heat * (response / conductance)
        result = initial + (ambient - initial) * response + heat_response
    return number(result,"predicted temperature",minimum=-273.15)


def time_to_limit(*, initial_c: float, ambient_c: float, heat_w: float,
                  capacity_j_k: float, conductance_w_k: float, limit_c: float) -> float | None:
    # Validate the entire model even when the initial condition already exceeds the limit.
    temperature(0, initial_c=initial_c, ambient_c=ambient_c, heat_w=heat_w,
                capacity_j_k=capacity_j_k, conductance_w_k=conductance_w_k)
    limit = number(limit_c, "temperature limit", minimum=-273.15)
    if initial_c >= limit:
        return 0.0
    if conductance_w_k == 0:
        return number(capacity_j_k * ((limit-initial_c)/heat_w),"time to limit") if heat_w > 0 else None
    net_initial = heat_w + conductance_w_k * (ambient_c - initial_c)
    net_at_limit = heat_w + conductance_w_k * (ambient_c - limit)
    if net_initial <= 0 or net_at_limit <= 0:
        return None
    fraction = conductance_w_k * (limit - initial_c) / net_initial
    correction = -math.log1p(-fraction)/fraction if fraction else 1
    return number(capacity_j_k * ((limit-initial_c)/net_initial) * correction,"time to limit")


def thermal_screen(inputs: dict, sample_times_s: list[float]) -> dict:
    keys = ("initial_c", "ambient_c", "heat_w", "capacity_j_k", "conductance_w_k", "limit_c")
    units={"initial_c":"degC","ambient_c":"degC","heat_w":"W","capacity_j_k":"J/K","conductance_w_k":"W/K","limit_c":"degC"}
    ranges = {key: interval(inputs[key], key, minimum=-273.15 if key.endswith("_c") else 0,unit=units[key]) for key in keys}
    if any(value is None for value in ranges.values()):
        return {"state": "input-evidence-open", "time_to_limit_s": None, "predictions": []}
    corners = [dict(zip(keys, values)) for values in itertools.product(*(tuple(dict.fromkeys(ranges[key])) for key in keys))]
    durations = [time_to_limit(**corner) for corner in corners]
    finite = [value for value in durations if value is not None]
    predictions = []
    for time in sample_times_s:
        values = [temperature(time, **{key:value for key, value in corner.items() if key != "limit_c"}) for corner in corners]
        predictions.append({"time_s": time, "temperature_c": [min(values), max(values)]})
    return {"state": "screening-unvalidated", "time_to_limit_s": [min(finite), max(finite)] if finite else None,
            "some_cases_do_not_reach_limit": len(finite) != len(durations), "predictions": predictions,
            "uncertainty": "Parameter-corner sensitivity; no statistical confidence or validated hotspot bound.",
            "limitations": "Single lumped heat capacity and constant heat/conductance/ambient; no hydraulic, spatial, phase-change or runaway model."}


def tree_events(tree: dict) -> set[str]:
    if not isinstance(tree, dict) or len(tree) != 1:
        raise ValueError("fault tree nodes require exactly one event/and/or key")
    if "event" in tree:
        if not isinstance(tree["event"], str) or not tree["event"]:
            raise ValueError("fault tree event requires an ID")
        return {tree["event"]}
    kind = next(iter(tree))
    if kind not in {"and", "or"} or not isinstance(tree[kind], list) or len(tree[kind]) < 2:
        raise ValueError("fault tree gates require at least two children")
    return set().union(*(tree_events(child) for child in tree[kind]))


def evaluate(tree: dict, failed: set[str]) -> bool:
    if "event" in tree:
        return tree["event"] in failed
    kind = next(iter(tree))
    values = (evaluate(child, failed) for child in tree[kind])
    return all(values) if kind == "and" else any(values)


def minimal_cut_sets(tree: dict) -> list[list[str]]:
    events = sorted(tree_events(tree))
    if len(events) > 16:
        raise ValueError("exact screening supports at most sixteen primitive events")
    cuts: list[set[str]] = []
    for size in range(1, len(events) + 1):
        for selected in itertools.combinations(events, size):
            candidate = set(selected)
            if not any(cut <= candidate for cut in cuts) and evaluate(tree, candidate):
                cuts.append(candidate)
    return [sorted(cut) for cut in cuts]


def exact_probability(tree: dict, probabilities: dict[str, float]) -> float:
    events = sorted(tree_events(tree))
    if len(events) > 16 or set(events) - set(probabilities):
        raise ValueError("missing probabilities or fault tree exceeds sixteen events")
    for identifier in events:
        probability = number(probabilities[identifier], identifier)
        if probability > 1:
            raise ValueError("event probability cannot exceed one")
    terms = []
    for states in itertools.product((False, True), repeat=len(events)):
        failed = {identifier for identifier, value in zip(events, states) if value}
        if evaluate(tree, failed):
            terms.append(math.prod(probabilities[identifier] if value else 1 - probabilities[identifier]
                                   for identifier, value in zip(events, states)))
    return min(1.0,max(0.0,math.fsum(terms)))


def fault_tree_screen(tree: dict, events: list[dict], mission_h: float, *, independence: bool) -> dict:
    mission = number(mission_h, "mission duration", minimum=1e-12)
    ids = [row["id"] for row in events]
    if len(ids) != len(set(ids)) or tree_events(tree) - set(ids):
        raise ValueError("duplicate or unknown fault tree events")
    cuts = minimal_cut_sets(tree)
    mission_bounds, down_bounds, unknown = {}, {}, []
    for row in events:
        if row["id"] not in tree_events(tree):
            continue
        rate = interval(row["failure_rate_per_h"], row["id"] + ".rate",unit="1/h")
        repair = interval(row["repair_h"], row["id"] + ".repair",unit="h")
        if row["event_class"] not in {"hardware-random", "software-systematic", "human-process"}:
            raise ValueError("unknown fault event class")
        if row["event_class"] != "hardware-random" and rate is not None:
            raise ValueError("systematic software/process defects cannot be assigned hardware random rates")
        if rate is None:
            unknown.append(row["id"])
            mission_bounds[row["id"]] = (0.0, 1.0)
        else:
            mission_bounds[row["id"]] = tuple(-math.expm1(-value * mission) for value in rate)
        if rate is None or repair is None:
            down_bounds[row["id"]] = (0.0, 1.0)
        else:
            products = [rate[i] * repair[i] for i in (0,1)]
            down_bounds[row["id"]] = tuple(value/(1+value) if math.isfinite(value) else 1.0 for value in products)
    if not independence:
        return {"state":"dependency-evidence-open", "minimal_cut_sets":cuts,
                "mission_top_event_probability":None, "steady_state_availability":None}
    mission_probability = [exact_probability(tree, {identifier:value[i] for identifier,value in mission_bounds.items()}) for i in (0, 1)]
    unavailability = [exact_probability(tree, {identifier:value[i] for identifier,value in down_bounds.items()}) for i in (0, 1)]
    return {"state":"unknown-event-inputs" if unknown else "screening-unvalidated", "minimal_cut_sets":cuts,
            "unknown_events":unknown, "mission_top_event_probability":mission_probability,
            "steady_state_availability":[1-unavailability[1], 1-unavailability[0]],
            "limitations":"Independent primitive event processes with explicit shared-cause events; exponential operating failure times and independent repairs. No repair-resource competition, coverage, wear-out or systematic-defect rate inference."}


def latent_exposure(rate_per_h: float, inspection_h: float) -> float:
    x = number(rate_per_h, "latent failure rate") * number(inspection_h, "inspection interval")
    if x < 1e-5:
        return x / 2 - x*x / 6 + x*x*x / 24
    return 1 + math.expm1(-x) / x


def inspection_interval(rate_per_h: float, maximum_exposure: float) -> float | None:
    rate = number(rate_per_h, "latent failure rate")
    target = number(maximum_exposure, "exposure budget", minimum=1e-12)
    if target >= 1:
        raise ValueError("exposure budget must be below one")
    if rate == 0:
        return None
    low, high = 0.0, 1 / rate
    while latent_exposure(rate, high) < target:
        high *= 2
    for _ in range(80):
        middle = (low + high) / 2
        if latent_exposure(rate, middle) <= target:
            low = middle
        else:
            high = middle
    return low


def braking_screen(distance_m: float, reaction_s: float, deceleration_m_s2: float) -> dict:
    distance = number(distance_m, "available stopping distance")
    reaction = number(reaction_s, "reaction delay")
    deceleration = number(deceleration_m_s2, "effective deceleration", minimum=1e-12)
    numerator = 2 * deceleration * distance
    root = math.hypot(deceleration*reaction,math.sqrt(numerator))
    speed = number(numerator/(root+deceleration*reaction),"restricted speed") if distance else 0.0
    return {"maximum_speed_m_s":speed, "maximum_speed_km_h":speed * 3.6,
            "state":"illustrative-restriction-screen", "limitations":"Constant effective deceleration and fixed delay/distance; grade, adhesion, target brake timing, uncertainty and operating authority need deployment substantiation."}


def maintenance_screen(fleet: int, rate_per_h: float, repair_h: float, turnaround_h: float,
                       max_wait_h: float, max_stockout: float) -> dict:
    if type(fleet) is not int or not 1 <= fleet <= 100000:
        raise ValueError("fleet must be an integer from 1 to 100000")
    arrival = fleet * number(rate_per_h, "failure rate")
    repair = number(repair_h, "hands-on repair", minimum=1e-12)
    turnaround = number(turnaround_h, "replacement replenishment turnaround", minimum=1e-12)
    waiting_target = number(max_wait_h, "maximum queue wait",minimum=1e-12)
    stockout_target = number(max_stockout, "stockout budget", minimum=1e-12)
    if stockout_target >= 1:
        raise ValueError("stockout budget must be below one")
    offered = arrival * repair
    if offered > 500:
        raise ValueError("maintenance screen exceeds supported offered load")
    crews, waiting = 0, 0.0
    if arrival:
        for crews in range(max(1, math.floor(offered) + 1), 1001):
            terms = [1.0]
            for k in range(1, crews):
                terms.append(terms[-1] * offered / k)
            tail = terms[-1] * offered / crews / (1 - offered / crews)
            wait_probability = tail / (math.fsum(terms) + tail)
            waiting = wait_probability / (crews / repair - arrival)
            if waiting <= waiting_target:
                break
        else:
            raise ValueError("no staffing solution within screening cap")
    mean_pipeline = arrival * turnaround
    if mean_pipeline > 500:
        raise ValueError("spares screen exceeds supported pipeline mean")
    probability = math.exp(-mean_pipeline)
    cumulative, spares = probability, 0
    while max(0, 1 - cumulative) > stockout_target:
        spares += 1
        probability *= mean_pipeline / spares
        cumulative += probability
        if spares > 2000:
            raise ValueError("spares screen did not converge")
    return {"repair_crews":crews, "mean_queue_wait_h":waiting, "minimum_spares":spares,
            "pipeline_stockout_probability":max(0, 1-cumulative), "state":"planning-screen",
            "limitations":"M/M/c mean queue wait and independent Poisson replenishment pipeline with fixed mean turnaround. Crews are concurrent service teams, not roster headcount; correlated fleet outages, shifts, skills and logistics require separate modelling."}
