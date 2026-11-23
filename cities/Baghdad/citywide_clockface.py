"""Book independent directional tracks, terminal resources and mapped interchanges on a periodic day."""

from collections import defaultdict
from itertools import combinations, pairwise
from math import ceil, sqrt

from engineering.outline import baghdad_diagrams as diagrams

# Trial route-lock and yard geometry. A terminal pocket connects to one throat on
# each line end; M09 instead has a pocket/throat for each direction at its lap stop.
LOCK_S = 15
YARD_KM = 0.25
THROAT_M = 100
YARD_SPEED_M_S = 10 / 3.6
PHASE_STEP_S = 15


def line_plan(name, base, cfg, headway, brake):
    vehicle = cfg["vehicle"]
    length = cfg["vehicle_geometry"]["train_length_m"]
    grade = cfg["power_assumptions"]["adverse_grade"]
    accel = cfg["power_assumptions"]["required_net_accel_m_s2"]
    # Acceleration is the required net acceleration uphill. Brake service effort is
    # the level-track trial. Allow downhill gravity with no resistance credit.
    decel = brake - 9.80665 * grade
    vmax = vehicle["speed_cap_kmh"] / 3.6
    dwell = vehicle["dwell_s"]
    turn = ceil(60 * cfg["service_plan"]["terminal_layover_min_each_end"])
    stops = base["outward_stops"]
    if name == "M05":
        close = [
            i
            for i, (a, b) in enumerate(pairwise(stops))
            if base["one_way_km"] * (b["fraction"] - a["fraction"]) * 1000
            < cfg["station_geometry"]["platform_clear_length_m"]
        ]
        if len(close) != 1 or [r["id"] for r in stops[close[0] : close[0] + 2]] != ["M-075", "M-076"]:
            raise ValueError("Review the M05 shared station site against the current chainages")
        stops = [s for s in stops if s["id"] != "M-075"]
    distances = [(b["fraction"] - a["fraction"]) * base["one_way_km"] * 1000 for a, b in pairwise(stops)]
    if min(distances) <= length or decel <= 0:
        raise ValueError("Review station spacing, stopping rate or train length before timing this line")
    reciprocals = 1 / accel + 1 / decel
    # Book a full stop at the clear side of each terminal throat. Traverse the
    # turnout zone in a separate 10 km/h rest-to-rest move. The mainline run
    # and the booked terminal occupation therefore use the same speed limit.
    zone_m = THROAT_M + length
    zone_s = ceil(zone_m / YARD_SPEED_M_S + YARD_SPEED_M_S * reciprocals / 2)
    moving = []
    main_lengths = []
    zones = []
    for i, whole_leg in enumerate(distances):
        zone_count = int(i == 0) + int(i == len(distances) - 1)
        dist = whole_leg - zone_count * zone_m
        if dist <= 0:
            raise ValueError("A terminal leg cannot contain its restricted throat zone")
        main_lengths.append(dist)
        zones.append(zone_count)

        peak = min(vmax, sqrt(2 * dist / reciprocals))
        moving.append(
            ceil(peak * reciprocals + (dist - peak**2 * reciprocals / 2) / peak) + zone_count * zone_s
        )
    dwell_total = dwell * (len(stops) - 2)
    # Retain at least the parent commercial journey time. Distribute additional
    # recovery over the moving legs. A line reverses after each trip, a ring after none.
    loop = base.get("operation") == "continuous_laps_each_direction"
    quantum = headway if loop else headway // 2
    run = (
        ceil((max(sum(moving) + dwell_total, base["one_way_s_including_dwell"]) + turn) / quantum) * quantum
        - turn
    )
    slack = run - dwell_total - sum(moving)
    extra = [round(slack * s["fraction"]) for s in stops]
    legs = []
    for i, (dist, seconds) in enumerate(zip(main_lengths, moving)):
        t = seconds + extra[i + 1] - extra[i]
        main_s = t - zones[i] * zone_s
        v = 2 * dist / (main_s + sqrt(max(0.0, main_s * main_s - 2 * dist * reciprocals)))
        if v > vmax + 1e-8:
            raise ValueError("Timed speed exceeds the line cap")
        to_cruise = v * v / (2 * accel)
        if length > dist - v * v / (2 * decel):
            raise ValueError("Tail still occupies the station on entering the next braking curve")
        tail = sqrt(2 * length / accel) if length <= to_cruise else v / accel + (length - to_cruise) / v
        legs.append((t, ceil(tail), ceil(v / decel), v))
    throat = zone_s + LOCK_S
    shunt = ceil((1000 * YARD_KM + length) / YARD_SPEED_M_S + YARD_SPEED_M_S * reciprocals / 2) + 2 * LOCK_S
    plan = dict(
        cfg["service_plan"],
        departures_per_hour_direction=[3600 // headway] * vehicle["service_hours_per_day"],
    )
    trips, sets = diagrams.workings(name, plan, run, turn, headway, loop=loop)
    side_phase = (run + turn) % headway
    patterns, templates = [], defaultdict(list)
    block_gaps = []
    for side in (0, 1):
        ordered_stops = stops[::-1] if side else stops
        ordered_legs = legs[::-1] if side else legs
        time, pattern = 0, []
        for i, stop in enumerate(ordered_stops):
            arr = time
            time += dwell if 0 < i < len(stops) - 1 else 0
            pattern.append([stop["id"], arr, time])
            offset = side * side_phase
            hint = stop.get("interchange_hint")
            if hint is not None:
                if i in (0, len(stops) - 1):
                    dep = offset + (0 if i == 0 else run + turn)
                    templates[hint].append((dep - turn - max(throat, shunt), dep + max(throat, shunt)))
                else:
                    approach = ordered_legs[i - 1][2] + LOCK_S
                    tail = ordered_legs[i][1] + LOCK_S
                    templates[hint].append((offset + arr - approach, offset + time + tail))
            if i < len(ordered_legs):
                duration = ordered_legs[i][0]
                # One directional block between stops, approach set before dispatch.
                # At a terminal the model places the stop clear of the turnout.
                clear = throat if i == len(ordered_legs) - 1 else dwell + ordered_legs[i + 1][1] + LOCK_S
                block_gaps.append(headway - duration - clear - LOCK_S)
                time += duration
        if time != run:
            raise ValueError("Leg times differ from booked trip")
        patterns.append(pattern)
    paths = defaultdict(list)
    for train, side, dep, arr in trips:
        paths[train].append((side, dep, arr))
    resources = defaultdict(list)
    stock_a, stock_b = [0, 0], [0, 0]
    for path in paths.values():
        for side, dep, arr in path:
            dest = side if loop else 1 - side
            resources["throat", side].append((dep - LOCK_S, dep + throat))
            resources["throat", dest].append((arr - throat, arr + LOCK_S))
        side, dep, _ = path[0]
        stock_a[side] += 1
        resources["throat", side].append((dep - turn - shunt, dep - turn))
        resources["berth", side].append((dep - turn - shunt, dep + throat))
        for (side, _, arr), (next_side, dep, _) in pairwise(path):
            dest = side if loop else 1 - side
            if next_side != dest or dep - arr != turn:
                raise ValueError("Set cannot make booked turn or lap")
            resources["berth", dest].append((arr - throat, dep + throat))
        side, _, arr = path[-1]
        dest = side if loop else 1 - side
        stock_b[dest] += 1
        resources["throat", dest].append((arr + turn, arr + turn + shunt))
        resources["berth", dest].append((arr - throat, arr + turn + shunt))
    if stock_a != stock_b:
        raise ValueError("Overnight stock is unbalanced")
    gaps = {k: min(b[0] - a[1] for a, b in pairwise(sorted(times))) for k, times in resources.items()}
    return (
        dict(
            group=name,
            loop=loop,
            one_way_km=base["one_way_km"],
            run_s=run,
            turn_s=turn,
            phase_at_second_origin_s=side_phase,
            sets=sets,
            departures=len(trips),
            start_and_end_sets_by_origin=stock_a,
            yard_moves=2 * sets,
            yard_km_day=2 * sets * YARD_KM,
            max_speed_kmh=max(x[3] for x in legs) * 3.6,
            block_margin_s=min(block_gaps),
            throat_margin_s=min(gaps["throat", i] for i in (0, 1)),
            berth_margin_s=min(gaps["berth", i] for i in (0, 1)),
            directional_blocks=len(block_gaps),
            terminal_zone_m=zone_m,
            terminal_zone_s=zone_s,
            patterns=patterns,
        ),
        templates,
        trips,
    )


def period_mask(windows, period):
    mask = 0
    for a, b in windows:
        if b - a >= period:
            return (1 << period) - 1
        # Wrapping intervals are split at the local clock origin.
        start, count = a % period, b - a
        within = min(count, period - start)
        mask |= ((1 << within) - 1) << start
        mask |= (1 << (count - within)) - 1
    return mask


def phases_for_interchanges(templates, period, *, search_limit=100_000):
    """Search 15-second departure phases; compare every occupied second modulo the headway."""
    by_hint = defaultdict(dict)
    for name, hints in templates.items():
        for hint, windows in hints.items():
            by_hint[hint][name] = period_mask(windows, period)
    shared = {hint: masks for hint, masks in by_hint.items() if len(masks) > 1}
    edges = defaultdict(list)
    for masks in shared.values():
        for a, b in combinations(sorted(masks), 2):
            edges[a, b].append((masks[a], masks[b]))
    steps = period // PHASE_STEP_S
    if period % PHASE_STEP_S:
        raise ValueError("Phase step does not divide headway")
    all_seconds = (1 << period) - 1

    def rotate(mask, shift):
        return ((mask << shift) & all_seconds) | (mask >> (period - shift))

    allowed = {}
    for (a, b), pairs in edges.items():
        shifts = {
            i
            for i in range(steps)
            if all(not (left & rotate(right, i * PHASE_STEP_S)) for left, right in pairs)
        }
        allowed[a, b] = shifts
        allowed[b, a] = {(-i) % steps for i in shifts}
    explored = 0

    def search(chosen, domains):
        nonlocal explored
        if not domains:
            return chosen
        var = min(domains, key=lambda v: (len(domains[v]), -sum((v, w) in allowed for w in domains), v))
        others = {k: d for k, d in domains.items() if k != var}
        for phase in sorted(domains[var]):
            explored += 1
            if explored > search_limit:
                return None
            reduced = {
                k: ({i for i in d if (i - phase) % steps in allowed[var, k]} if (var, k) in allowed else d)
                for k, d in others.items()
            }
            if all(reduced.values()):
                found = search({**chosen, var: phase}, reduced)
                if found is not None:
                    return found
        return None

    domains = {g: set(range(steps)) for g in templates}
    # The connecting group with the greatest degree fixes the arbitrary clock origin.
    anchor = max(sorted(domains), key=lambda v: sum((v, w) in allowed for w in domains))
    domains[anchor] = {0}
    answer = search({}, domains)
    phases = None if answer is None else {g: i * PHASE_STEP_S for g, i in sorted(answer.items())}
    if phases is not None:
        for masks in shared.values():
            occupied = 0
            for g, m in masks.items():
                shifted = rotate(m, phases[g])
                if occupied & shifted:
                    raise ValueError("Selected phases overlap at a mapped interchange")
                occupied |= shifted
    return phases, sorted(shared), explored


def evaluate(groups, cfg, brake, headway, *, include_workings=False):
    if headway < 1 or 3600 % headway:
        raise ValueError("Use a positive whole number of evenly spaced departures per hour")
    lines, templates, workings = {}, {}, {}
    for name, base in sorted(groups.items()):
        lines[name], templates[name], workings[name] = line_plan(name, base, cfg, headway, brake)
    phases, hints, explored = phases_for_interchanges(templates, headway)
    gaps = {
        k: min(x[k] for x in lines.values()) for k in ("berth_margin_s", "throat_margin_s", "block_margin_s")
    }
    result = dict(
        headway_s=headway,
        groups=lines,
        minimum_clearances_s=gaps,
        origin_phases_s=phases,
        shared_interchange_hints=hints,
        phase_trials=explored,
        phase_step_s=PHASE_STEP_S,
        resource_screen_passed=min(gaps.values()) >= 0 and phases is not None,
    )
    if phases is not None and include_workings:
        result["trips"] = {
            name: [[train, side, dep + phases[name], arr + phases[name]] for train, side, dep, arr in rows]
            for name, rows in workings.items()
        }
    return result
