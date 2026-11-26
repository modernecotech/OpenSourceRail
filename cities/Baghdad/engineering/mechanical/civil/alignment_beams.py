"""Translate a Baghdad route alignment into a conditional girder and hold register."""

from collections import defaultdict
from hashlib import sha256
from html import escape
from itertools import pairwise
from math import asin, atan2, ceil, cos, degrees, floor, hypot, pi, sin, sqrt, tan
from pathlib import Path

import numpy as np
from shapely import intersection, intersects, linestrings, prepare
from shapely.geometry import LineString

from cities.Baghdad import holistic_network, spaced_ring_geometry
from . import family_comparison as family, rail_fed_erection as erection

SPAN_M = erection.SPAN_M
PITCH_M = family.TRIALS["track_pitch_m"]
PLATFORM_M = 110.0  # Trial straight reservation for the 102 m reference train.
STATION_SNAP_M = 35.0
ALIGNMENT_SIMPLIFICATION_M = 0.25
MIN_TURN_DEG = 0.25
MIN_RADIUS_M = 120.0
PREFERRED_RADIUS_M = 400.0  # 72 km/h at 1 m/s² without cant.
TANGENT_SHARE = 0.45
MAX_SAGITTA_M = 0.20
MIN_SHORT_BAY_M = 8.0
WATER_APPROACH_M = 10.0
EPS = 1e-5
RATES = {
    "short_closure": (1500, 3500, 8000),
    "curved_ugirder": (5000, 12000, 28000),
    "short_curved_ugirder": (5500, 13500, 32000),
}
CHANGEOVER_H = {"short_closure": 2.0, "curved_ugirder": 6.0, "short_curved_ugirder": 6.0}
EXTRA_ASSEMBLY_H = {"short_closure": 0.75, "curved_ugirder": 1.0, "short_curved_ugirder": 1.25}
HOLD_ORDER = (
    "shared_alignment_hold", "river_crossing_hold", "water_crossing_hold", "junction_hold", "station_interface_hold",
    "sharp_or_constrained_turn_hold", "short_tangent_hold", "water_context_hold",
)


def _sources():
    paths = [Path(__file__), Path(family.__file__), Path(erection.__file__),
             Path(holistic_network.__file__), Path(spaced_ring_geometry.__file__),
             erection.ASSUMPTIONS, erection.HERE / "concept.toml"]
    return {path.relative_to(family.ROOT).as_posix(): sha256(path.read_bytes()).hexdigest() for path in paths}


def _standard_stock():
    result = family.evaluate_high_load(route_km=0.02, selected_family="U", selected_span_m=SPAN_M)
    row = next(item for item in result["rows"] if item["span_m"] == SPAN_M and item["shared_pier"]
               and item["section"]["shape"] == "U" and item["section"]["depth_m"] == 1.55)
    section = row["section"]
    return {
        "physical_id": row["physical_id"], "evaluation_id": result["evaluation_id"],
        "width_m": section["width_m"], "depth_m": section["depth_m"], "web_m": section["web_m"],
        "floor_m": section["floor_m"], "clear_channel_m": section["clear_channel_m"],
        "area_m2": section["area_m2"], "end_thickening_m3": section["local_thickening_m3"],
        "bare_mass_t": row["actions"]["mass_t"],
        "cast_m3": section["volume_m3"], "bearings_per_girder": row["quantities"]["standard_bearings"] // 2,
        "strand_count": row["actions"]["strand_count"], "strand_kg_m": row["strand_kg_m"],
        "rebar_planning_kg": row["quantities"]["standard_beam_bar_planning_kg"] / 2,
    }


def _zone(rows, lo, hi, length, label, source, closed=False):
    if closed and lo < 0:
        _zone(rows, lo + length, length, length, label, source)
    if closed and hi > length:
        _zone(rows, 0, hi - length, length, label, source)
    if min(length, hi) - max(0, lo) > EPS:
        rows.append((max(0, lo), min(length, hi), label, source))


def _linear_parts(geometry):
    if geometry.geom_type == "LineString" and not geometry.is_empty:
        yield geometry
    elif geometry.geom_type in ("MultiLineString", "GeometryCollection"):
        for part in geometry.geoms:
            yield from _linear_parts(part)


def _wet_intervals(track, water):
    if water is None or water.is_empty:
        return []
    segments = linestrings(np.stack((track.points[:-1], track.points[1:]), axis=1))
    wet = np.flatnonzero(intersects(water, segments))
    intervals = []
    for idx, clipped in zip(wet, intersection(segments[wet], water), strict=True):
        start = track.chainage[idx]
        segment = segments[idx]
        for part in _linear_parts(clipped):
            distances = [segment.project(point) for point in (part.boundary.geoms)]
            if len(distances) == 2 and max(distances) - min(distances) > EPS:
                intervals.append((float(start + min(distances)), float(start + max(distances))))
    merged = []
    for lo, hi in sorted(intervals):
        if merged and lo <= merged[-1][1] + EPS:
            merged[-1][1] = max(hi, merged[-1][1])
        else:
            merged.append([lo, hi])
    return merged


def _geometry(track, fixed, closed):
    # Remove GIS resampling noise while retaining route chainage on the original trace.
    points = np.asarray(LineString(track.points).simplify(ALIGNMENT_SIMPLIFICATION_M).coords)
    if len(points) < 2:
        raise ValueError("Alignment simplification left no route")
    # GEOS line simplification retains input vertices in order, including ring seam.
    retained = []
    for index, point in enumerate(track.points):
        if np.array_equal(point, points[len(retained)]):
            retained.append(index)
            if len(retained) == len(points):
                break
    if len(retained) != len(points):
        raise ValueError("Simplified vertices cannot be mapped in route order")
    turns = []
    for i in range(0 if closed else 1, len(points) - 1):
        previous, vertex, following = points[i - 1 if i else -2], points[i], points[i + 1]
        a, b = vertex - previous, following - vertex
        length_a, length_b = np.linalg.norm(a), np.linalg.norm(b)
        sweep = atan2(float(a[0] * b[1] - a[1] * b[0]), float(a @ b))
        if abs(degrees(sweep)) < MIN_TURN_DEG:
            continue
        chain = float(track.chainage[retained[i]])
        left = chain - track.chainage[retained[i - 1]] if i else track.chainage[-1] - track.chainage[retained[-2]]
        right = track.chainage[retained[i + 1]] - chain
        fit = TANGENT_SHARE * min(length_a, length_b)
        tangent_factor = tan(abs(sweep) / 2)
        capacity = fit / tangent_factor
        radius = min(capacity, PREFERRED_RADIUS_M)
        tangent = radius * tangent_factor
        lo, hi = float(chain - tangent * left / length_a), float(chain + tangent * right / length_b)
        reasons = sorted({label for start, end, label, _ in fixed if start < hi and end > lo})
        if not i and closed:
            # Keep the physical ring seam as a marked continuation interface.
            reasons.append("ring seam requires a continuous transition or relocated datum")
        inner_radius = radius - PITCH_M / 2
        status = "candidate"
        if inner_radius < MIN_RADIUS_M:
            reasons.append("inner track does not fit the trial minimum radius")
        if reasons:
            status = "held"
        centre = vertex - a / length_a * tangent
        inward = np.array([-a[1], a[0]]) / length_a * (1 if sweep > 0 else -1)
        centre += inward * radius
        turns.append({
            "vertex": int(retained[i]), "vertex_chainage_m": chain,
            "trace_start_m": lo, "trace_end_m": hi, "signed_sweep_deg": degrees(sweep),
            "fit_maximum_route_radius_m": float(capacity), "candidate_route_radius_m": float(radius),
            "candidate_inside_radius_m": float(inner_radius),
            "candidate_outside_radius_m": float(radius + PITCH_M / 2),
            "circle_centre_wgs84": (centre / holistic_network.LOCAL_METRES).tolist(),
            "start_wgs84": ((vertex - a / length_a * tangent) / holistic_network.LOCAL_METRES).tolist(),
            "end_wgs84": ((vertex + b / length_b * tangent) / holistic_network.LOCAL_METRES).tolist(),
            "unsigned_sweep_rad": abs(sweep), "status": status, "holds": reasons,
            "candidate_speed_kmh_at_1_m_s2_without_cant": 3.6 * sqrt(max(0, inner_radius)) if status == "candidate" else None,
        })
    return turns


def _allow_short_curves(turns, fixed, length):
    """Reserve tangent leads for a shallow short curve, within one girder."""
    endpoints = sorted({0.0, length} | {coord for zone in fixed for coord in zone[:2]}
                       | {turn[key] for turn in turns for key in ("trace_start_m", "trace_end_m")
                          if 0 <= turn[key] <= length})
    for turn in turns:
        if turn["status"] != "candidate":
            continue
        lo, hi = turn["trace_start_m"], turn["trace_end_m"]
        theta = turn["unsigned_sweep_rad"]
        available_length = turn["candidate_inside_radius_m"] * theta
        turn["bay_start_m"], turn["bay_end_m"] = lo, hi
        if available_length >= MIN_SHORT_BAY_M:
            continue
        left = max((point for point in endpoints if point < lo - EPS), default=0.0)
        right = min((point for point in endpoints if point > hi + EPS), default=length)
        # Half of each free gap can be allocated independently by its two neighbors.
        lead_room = (lo - left) / 2
        trail_room = (right - hi) / 2
        if any(abs(end - lo) < EPS for _, end, _, _ in fixed):
            lead_room = 0.0
        if any(abs(start - hi) < EPS for start, _, _, _ in fixed):
            trail_room = 0.0
        extra = MIN_SHORT_BAY_M - available_length
        if lead_room + trail_room < extra or extra + turn["candidate_outside_radius_m"] * theta > SPAN_M:
            continue
        lead = min(lead_room, max(extra / 2, extra - trail_room))
        trail = extra - lead
        turn["bay_start_m"], turn["bay_end_m"] = lo - lead, hi + trail
        turn["tangent_lead_m"], turn["tangent_trail_m"] = lead, trail


def _pieces(lo, hi, family_name, *, turn=None):
    length = hi - lo
    if turn is None and family_name == "tangent":
        count = floor((length + EPS) / SPAN_M)
        marks = [lo + SPAN_M * i for i in range(count + 1)]
        rows = [(a, b, "straight_20m") for a, b in zip(marks, marks[1:])]
        residual = hi - marks[-1]
        if residual >= MIN_SHORT_BAY_M - EPS:
            rows.append((marks[-1], hi, "short_closure"))
        elif residual > EPS and rows:
            # Lengthen neither beam beyond stock. Rebalance the final standard bay and remainder.
            start = rows.pop()[0]
            middle = (start + hi) / 2
            rows.extend(((start, middle, "short_closure"), (middle, hi, "short_closure")))
        elif residual > EPS:
            rows.append((lo, hi, "short_tangent_hold"))
        elif rows:
            rows[-1] = (rows[-1][0], hi, "straight_20m")
        return rows
    if turn is None:
        return [(lo, hi, family_name)]
    angle = turn["unsigned_sweep_rad"]
    radius = turn["candidate_outside_radius_m"]
    inside = turn["candidate_inside_radius_m"]
    limit = min(SPAN_M / radius, 4 * asin(sqrt(MAX_SAGITTA_M / (2 * radius))))
    count = max(1, ceil(angle / limit))
    padding = turn.get("tangent_lead_m", 0) + turn.get("tangent_trail_m", 0)
    if inside * angle / count + padding < MIN_SHORT_BAY_M - EPS:
        return [(lo, hi, "sharp_or_constrained_turn_hold")]
    marks = [lo + length * i / count for i in range(count + 1)]
    curved_family = ("short_curved_ugirder" if padding or count > ceil(angle * radius / SPAN_M)
                     else "curved_ugirder")
    return [(a, b, curved_family) for a, b in zip(marks, marks[1:])]


def _shared_edges(lines):
    """Reserve exact mapped edges, using the length register's direction-free definition."""
    occurrences = defaultdict(list)
    for code, line in sorted(lines.items()):
        for index, (start, end) in enumerate(pairwise(line["geometry"])):
            edge = tuple(sorted((tuple(start), tuple(end))))
            occurrences[edge].append((code, index))
    held, register = defaultdict(list), []
    for edge, traces in occurrences.items():
        if len(traces) < 2:
            continue
        key = f"shared-edge-{len(register) + 1:04}"
        start, end = edge
        metres = hypot(*((end[i] - start[i]) * holistic_network.LOCAL_METRES[i] for i in (0, 1)))
        register.append({"id": key, "wgs84": edge, "physical_edge_m": metres,
                         "mapped_service_trace_m_before_deduplication": metres * len(traces),
                         "traces": [{"line_id": code, "segment_index": i} for code, i in traces],
                         "fabrication_and_installation_cost_usd": None})
        for code, index in traces:
            held[code].append((index, key))
    return held, register


def _route(code, line, stations, water, water_known, junctions, shared_edges):
    track = holistic_network.Track(line["geometry"])
    length = float(track.chainage[-1])
    closed = bool(np.array_equal(track.coordinates[0], track.coordinates[-1]))
    fixed, calls = [], []
    for index, key in shared_edges:
        _zone(fixed, track.chainage[index], track.chainage[index + 1], length,
              "shared_alignment_hold", key)
    for station_id in dict.fromkeys(line["station_ids"]):
        station = stations[station_id]
        km, offset, _ = track.locate(station["coordinates"])
        chain = km * 1000
        calls.append({"station_id": station_id, "reference_chainage_m": chain, "alignment_offset_m": offset})
        _zone(fixed, chain - PLATFORM_M / 2, chain + PLATFORM_M / 2, length,
              "station_interface_hold", station_id, closed)
        if offset > STATION_SNAP_M:
            calls[-1]["alignment_hold"] = "Mapped station is outside the alignment snap screen"
    for row in junctions:
        if code in row["line_ids"]:
            km, offset, _ = track.locate(row["coordinates"])
            if offset > STATION_SNAP_M:
                raise ValueError(f"Junction {row['id']} is outside alignment snap screen for {code}")
            chain = km * 1000
            _zone(fixed, chain - SPAN_M, chain + SPAN_M, length, "junction_hold", row["id"], closed)
    wet = []
    for index, (lo, hi) in enumerate(_wet_intervals(track, water)):
        key = f"{code}-water-{index + 1:03}"
        label = "river_crossing_hold" if hi - lo >= spaced_ring_geometry.MAIN_CHANNEL_MIN_M else "water_crossing_hold"
        wet.append(dict(id=key, wet_start_m=lo, wet_end_m=hi, wet_length_m=hi-lo, family=label))
        _zone(fixed, lo - WATER_APPROACH_M, hi + WATER_APPROACH_M, length, label, key, closed)
    turns = _geometry(track, fixed, closed)
    for turn in turns:
        start, end = turn["trace_start_m"], turn["trace_end_m"]
        if turn["status"] == "held":
            _zone(fixed, start, end, length, "sharp_or_constrained_turn_hold", turn["vertex"], closed)
    # Full water coverage belongs to the map source. Without it, preserve provisional
    # quantities but carry a route-wide geospatial hold.
    _allow_short_curves(turns, fixed, length)
    candidate_turns = {t["bay_start_m"]: t for t in turns if t["status"] == "candidate"}
    marks = sorted({0.0, length} | {v for row in fixed for v in row[:2]} |
                   {t[key] for t in candidate_turns.values() for key in ("bay_start_m", "bay_end_m")})
    intervals = []
    for lo, hi in zip(marks, marks[1:]):
        if hi - lo <= EPS:
            continue
        mid = (lo + hi) / 2
        flags = [(label, source) for start, end, label, source in fixed if start <= mid <= end]
        turn = candidate_turns.get(lo)
        name = min((label for label, _ in flags), key=HOLD_ORDER.index) if flags else "tangent"
        for start, end, final in _pieces(lo, hi, name, turn=turn):
            row = {
                "reference_start_m": start, "reference_end_m": end,
                "family": final, "hold_sources": sorted(str(source) for _, source in flags),
                "route_length_m": end - start,
            }
            if turn is not None:
                lead = turn.get("tangent_lead_m", 0.0)
                trail = turn.get("tangent_trail_m", 0.0)
                sweep = turn["unsigned_sweep_rad"] * (end-start)/(hi-lo)
                row.update(turn_vertex=turn["vertex"], sweep_deg=degrees(sweep), turn_direction="left" if turn["signed_sweep_deg"] > 0 else "right")
                if not final.endswith("_hold"):
                    radii = {"inside": turn["candidate_inside_radius_m"], "outside": turn["candidate_outside_radius_m"]}
                    row.update(route_length_m=turn["candidate_route_radius_m"]*sweep + lead + trail, track_pieces={
                        side: {"radius_m": radius, "arc_length_m": radius*sweep + lead + trail,
                               "circular_arc_m": radius*sweep, "tangent_lead_m": lead, "tangent_trail_m": trail,
                               "chord_m": 2*radius*sin(sweep/2), "sagitta_m": 2*radius*sin(sweep/4)**2}
                        for side, radius in radii.items()
                    })
                else:
                    turn["status"] = "held"
                    turn["candidate_speed_kmh_at_1_m_s2_without_cant"] = None
                    turn["holds"].append("curve would require a beam shorter than the trial short-bay limit")
            if not final.endswith("_hold") and "track_pieces" not in row:
                row["track_pieces"] = {side: {"arc_length_m": end-start} for side in ("left", "right")}
            if (final.endswith("_hold") and intervals and intervals[-1]["family"] == final
                    and abs(intervals[-1]["reference_end_m"] - start) < EPS):
                previous = intervals[-1]
                previous["reference_end_m"] = end
                previous["route_length_m"] += row["route_length_m"]
                previous["hold_sources"] = sorted(set(previous["hold_sources"] + row["hold_sources"]))
            else:
                row["id"] = f"{code}-B{len(intervals) + 1:05}"
                intervals.append(row)
    if abs(sum(row["reference_end_m"] - row["reference_start_m"] for row in intervals) - length) > 0.01:
        raise ValueError(f"{code} bay register does not conserve reference alignment")
    return {
        "route_id": code, "reference_length_m": length, "closed_ring": closed,
        "concept_length_with_candidate_fillets_m": sum(row["route_length_m"] for row in intervals),
        "water_screen": "mapped" if water_known else "held pending mapped water geometry",
        "wet_crossings": wet, "station_calls": sorted(calls, key=lambda row: row["reference_chainage_m"]),
        "turns": turns, "bays": intervals,
    }


def _quantities(routes, stock, params):
    delivery = params["delivery"]
    counts = defaultdict(lambda: {"bays_or_hold_intervals": 0, "girders": 0, "inside_girders": 0,
                                  "outside_girders": 0, "route_length_m": 0.0, "track_length_m": 0.0,
                                  "girder_concrete_m3": 0.0, "girder_bare_mass_t": 0.0, "bearings": 0,
                                  "rebar_planning_kg": 0.0, "strand_planning_kg": 0.0,
                                  "mould_changeovers": 0, "mould_changeover_h": 0.0,
                                  "mould_occupation_h": 0.0, "candidate_loaded_trips": 0,
                                  "flatbed_feed_equipment_h": 0.0, "assembly_operating_h": 0.0,
                                  "incremental_allowance_usd": dict.fromkeys(family.CASES, 0)})
    assemblies = []
    for route in routes.values():
        active = []
        support_interfaces = set()
        plain_supports = set()
        for row in route["bays"]:
            name, length = row["family"], row["route_length_m"]
            bucket = counts[name]
            bucket["bays_or_hold_intervals"] += 1
            bucket["route_length_m"] += length
            if "track_pieces" not in row:
                for mark in ("reference_start_m", "reference_end_m"):
                    support_interfaces.add(round(row[mark], 5))
                continue
            active.append(row)
            plain_supports.update(round(row[mark], 5) for mark in ("reference_start_m", "reference_end_m"))
            pieces = row["track_pieces"]
            bucket["inside_girders"] += int("inside" in pieces)
            bucket["outside_girders"] += int("outside" in pieces)
            bucket["girders"] += len(pieces)
            bucket["bearings"] += len(pieces) * stock["bearings_per_girder"]
            bucket["candidate_loaded_trips"] += len(pieces)
            chainage_km = (row["reference_start_m"] + row["reference_end_m"]) / 2000
            end_distance_km = min(chainage_km, route["reference_length_m"] / 1000 - chainage_km)
            feed_h = len(pieces) * erection.feed_hours(end_distance_km + delivery["yard_to_deck_rail_km_each"], delivery)
            bucket["flatbed_feed_equipment_h"] += feed_h
            assembly_h = (delivery["launcher_hours_per_standard_bay"]
                          + delivery["track_extension_and_ground_check_h_per_bay"]
                          + EXTRA_ASSEMBLY_H.get(name, 0.0))
            bucket["assembly_operating_h"] += assembly_h
            for piece in pieces.values():
                length = piece["arc_length_m"]
                volume = stock["end_thickening_m3"] + stock["area_m2"] * length
                bucket["track_length_m"] += length
                bucket["girder_concrete_m3"] += volume
                bucket["girder_bare_mass_t"] += volume * stock["bare_mass_t"] / stock["cast_m3"]
                bucket["rebar_planning_kg"] += volume * stock["rebar_planning_kg"] / stock["cast_m3"]
                bucket["strand_planning_kg"] += stock["strand_count"] * stock["strand_kg_m"] * length
                bucket["mould_occupation_h"] += delivery["mould_cycle_h"]
                if name in RATES:
                    change_h = CHANGEOVER_H[name]
                    bucket["mould_changeovers"] += 1
                    bucket["mould_changeover_h"] += change_h
                    bucket["mould_occupation_h"] += change_h
                    for case, increment in zip(family.CASES, RATES[name], strict=True):
                        bucket["incremental_allowance_usd"][case] += increment
            row["indicative_operations"] = {"flatbed_feed_equipment_h": feed_h,
                                            "launcher_and_track_h": assembly_h,
                                            "post_landing_release_h": delivery["after_landing_deck_release_h"]}
        if route["closed_ring"] and round(route["reference_length_m"], 5) in plain_supports and 0.0 in plain_supports:
            plain_supports.remove(round(route["reference_length_m"], 5))
        route["counted_support_positions"] = len(plain_supports - support_interfaces)
        route["support_interface_positions"] = len(plain_supports & support_interfaces)
        assemblies.append(active)

    schedule = []
    for route, bays in zip(routes.values(), assemblies, strict=True):
        yard_units = [0, 0]
        yard_occupation_h = [0.0, 0.0]
        elapsed_h = [0.0, 0.0]
        for bay in bays:
            end = int(bay["reference_start_m"] + bay["reference_end_m"] > route["reference_length_m"])
            n = len(bay["track_pieces"])
            yard_units[end] += n
            yard_occupation_h[end] += n * (delivery["mould_cycle_h"] + CHANGEOVER_H.get(bay["family"], 0.0))
            work = bay["indicative_operations"]
            elapsed_h[end] += (work["flatbed_feed_equipment_h"] + work["launcher_and_track_h"]
                               + work["post_landing_release_h"]) / delivery["launcher_front_availability"]
        yard_days = [max(ceil(units / delivery["cast_pieces_per_yard_day"]),
                        ceil(occupancy / delivery["moulds_per_yard"] / 24))
                     for units, occupancy in zip(yard_units, yard_occupation_h, strict=True)]
        front_shifts = [ceil(hours / erection.SHIFT_H) for hours in elapsed_h]
        schedule.append({
            "route_id": route["route_id"], "yard_units_by_end": yard_units,
            "yard_one_shift_days_by_end": yard_days,
            "yard_paid_crew_h": sum(yard_days) * erection.SHIFT_H * sum(params["yard_crew"].values()),
            "launcher_booked_8h_shifts_by_end": front_shifts,
            "launcher_paid_crew_h": sum(front_shifts) * erection.SHIFT_H * sum(params["rail_crew"].values()),
            "launcher_continuous_day_equivalents_by_end": [hours / 24 for hours in elapsed_h],
            "integrated_completion_day": None,
        })
    totals = {key: sum(bucket[key] for bucket in counts.values()) for key in next(iter(counts.values()))
              if key != "incremental_allowance_usd"}
    totals.update(
        incremental_allowance_usd={case: sum(bucket["incremental_allowance_usd"][case]
                                             for bucket in counts.values()) for case in family.CASES},
        held_route_length_m=sum(bucket["route_length_m"] for name, bucket in counts.items() if name.endswith("_hold")),
        held_reference_intervals=sum(bucket["bays_or_hold_intervals"] for name, bucket in counts.items()
                                     if name.endswith("_hold")),
        shared_support_positions=sum(route["counted_support_positions"] for route in routes.values()),
        support_interface_positions=sum(route["support_interface_positions"] for route in routes.values()),
        yard_paid_crew_h=sum(row["yard_paid_crew_h"] for row in schedule),
        launcher_paid_crew_h=sum(row["launcher_paid_crew_h"] for row in schedule),
        river_crossings=sum(row["family"] == "river_crossing_hold"
                            for route in routes.values() for row in route["wet_crossings"]),
        other_water_crossings=sum(row["family"] == "water_crossing_hold"
                                  for route in routes.values() for row in route["wet_crossings"]),
        held_turns=sum(row["status"] == "held" for route in routes.values() for row in route["turns"]),
        candidate_turns=sum(row["status"] == "candidate" for route in routes.values() for row in route["turns"]),
        held_cost_usd=None, integrated_completion_day=None,
    )
    return dict(sorted(counts.items())), totals, schedule


def evaluate(network, *, context=None):
    """Build a concept takeoff from the selected double-track physical network."""
    if not network["lines"]:
        raise ValueError("A beam takeoff requires at least one physical alignment")
    water_known = context is not None and "water" in context.get("layers", {})
    water = spaced_ring_geometry._water(context) if water_known else None
    if water_known:
        prepare(water)
    junctions = network.get("track_junctions", ())
    if isinstance(junctions, dict):
        junctions = list(junctions.values())
    stock = _standard_stock()
    params = erection.load_assumptions()
    shared, shared_register = _shared_edges(network["lines"])
    routes = {code: _route(code, line, network["stations"], water, water_known, junctions, shared.get(code, ()))
              for code, line in sorted(network["lines"].items())}
    by_family, totals, schedule = _quantities(routes, stock, params)
    totals["shared_alignment_unique_physical_m"] = sum(row["physical_edge_m"] for row in shared_register)
    totals["shared_alignment_mapped_service_trace_m_before_deduplication"] = sum(
        row["mapped_service_trace_m_before_deduplication"] for row in shared_register
    )
    sources = _sources()
    # The separately pinned geometry digest includes mappings which affect a takeoff
    # even when the upstream candidate uses a less detailed identity.
    input_sha256 = family.digest({
        "lines": {code: {key: line[key] for key in ("geometry", "station_ids")}
                  for code, line in sorted(network["lines"].items())},
        "stations": {code: row["coordinates"] for code, row in sorted(network["stations"].items())},
        "track_junctions": junctions,
        "water_features": context["layers"]["water"] if water_known else None,
    })
    representative = min(
        (row for route in routes.values() for row in route["bays"] if "inside" in row.get("track_pieces", {})),
        key=lambda row: (row["track_pieces"]["outside"]["tangent_lead_m"] > 0,
                         -row["sweep_deg"], row["id"]), default=None,
    )
    record = {
        "schema": "osr-baghdad-alignment-beams/1", "candidate_id": network["candidate_id"],
        "input_sha256": input_sha256, "source_sha256": sources,
        "physical_acceptance": False,
        "water_geometry_used": water_known, "stock_section": stock,
        "assumptions": {
            "stock_bay_m": SPAN_M, "track_pitch_m": PITCH_M, "station_zone_m": PLATFORM_M,
            "station_snap_m": STATION_SNAP_M, "simplification_m": ALIGNMENT_SIMPLIFICATION_M,
            "turn_resolution_deg": MIN_TURN_DEG, "minimum_inner_track_radius_m": MIN_RADIUS_M,
            "preferred_route_radius_m": PREFERRED_RADIUS_M, "maximum_used_share_of_neighboring_tangent": TANGENT_SHARE,
            "maximum_beam_plan_sagitta_m": MAX_SAGITTA_M, "minimum_short_bay_m": MIN_SHORT_BAY_M,
            "main_channel_threshold_m": spaced_ring_geometry.MAIN_CHANNEL_MIN_M, "water_approach_m": WATER_APPROACH_M,
            "mould_occupation_and_trial_cure_h": params["delivery"]["mould_cycle_h"],
            "mould_changeover_h_by_special_piece": CHANGEOVER_H,
            "additional_assembly_h_per_special_pair": EXTRA_ASSEMBLY_H,
            "incremental_allowance_per_special_piece_usd": {
                key: dict(zip(family.CASES, values, strict=True)) for key, values in RATES.items()},
            "inherited_delivery_parameters": params["delivery"],
            "yard_crew_per_shift": params["yard_crew"],
            "launcher_crew_per_shift": params["rail_crew"],
        },
        "routes": routes, "by_family": by_family, "totals": totals, "route_schedule": schedule,
        "shared_alignment_register": shared_register,
        "representative_curved_bay": representative,
        "holds": [
            "Route plans use mapped coordinates and horizontal circular fillets. Survey, grade, cant, transitions, vehicle and structural clearance, thermal movement and wheel-rail loads require design.",
            "Turn fits below the trial radius or within reserved station, junction or crossing interfaces remain held. The track junction register requires actual turnout or merge data. Passenger interchanges alone do not establish track junctions.",
            "Exact shared edges are reserved on every mapped service trace. Shared hold kilometres in the route totals are before deduplication. The separate edge register counts each physical edge once. Check shared running and structure at both interfaces before pricing girder stock.",
            "Mapped water lengths and approaches reserve a new rail structure envelope. Bridge type, navigational clearance, hydraulics, scour, geotechnics, approvals and cost remain open.",
            "Curve and short-bay quantities inherit the straight U section and end thickening. Reinforcement, stressing, anchorage, torsion, attachment and bearing design, and verified lifting mass await calculations and supplier information.",
            "Paid shifts use two nominal end yards and two fronts per route. Single flatbed trips and assembly are counted serially, at distance to the nearer terminal. Curved launcher travel, axle loads, cradle, temporary track, and every intervening work front require approval.",
            "Yard shift and continuous work equivalents describe quantified bays. Commissioned start dates, adequate release strength, piers, storage, starters, missing crossings, programme concurrency and integration require a separate delivery schedule.",
            "Special-piece costs are incremental planning allowances over equivalent priced stock. Treat held works and their delivery separately. Complete project direct cost and physical completion date require those prices and designs.",
        ],
    }
    return record | {"evaluation_id": family.digest(record)}


def render_svg(record):
    """Render a dimensioned, editable plan and cross-section of the retained concept."""
    stock = record["stock_section"]
    row = record["representative_curved_bay"]
    title = "Baghdad prefabricated U-girder concept"
    subtitle = f"{record['candidate_id']} · shared-pier stock section and horizontal alignment"
    scale = 86
    web, width, depth, slab = (stock[k] * scale for k in ("web_m", "width_m", "depth_m", "floor_m"))
    x, y = 210, 530
    profile = (f"M{x},{y} v{-depth} h{web} v{depth-slab} h{width-2*web} "
               f"v{slab-depth} h{web} v{depth} z")
    plan = []
    if row:
        theta = row["sweep_deg"] * pi / 180
        outer = row["track_pieces"]["outside"]["radius_m"]
        inner = row["track_pieces"]["inside"]["radius_m"]
        plan_scale = min(510 / (2 * outer * sin(theta / 2)), 122 / (PITCH_M + stock["width_m"]))
        direction = row["turn_direction"]
        plan.append(f'<text x="35" y="126" class="head">Turning bay {escape(row["id"])} · {row["sweep_deg"]:.2f}° {direction}</text>')
        for side, radius in (("outside", outer), ("inside", inner)):
            def at(arc_radius, fraction):
                angle = fraction * theta
                return f"{450+plan_scale*arc_radius*sin(angle):.3f},{208+plan_scale*((inner+outer)/2-arc_radius*cos(angle)):.3f}"

            for offset, css in ((-stock["width_m"]/2, "edge"), (0.0, "track"), (stock["width_m"]/2, "edge")):
                arc_radius = radius + offset
                value = arc_radius * plan_scale
                plan.append(f'<path class="{css}" d="M{at(arc_radius, -.5)} A{value:.3f},{value:.3f} 0 0 1 {at(arc_radius, .5)}"/>')
            piece = row["track_pieces"][side]
            y_text = 312 if side == "outside" else 337
            plan.append(f'<text x="35" y="{y_text}">{side.title()} · R {radius:.1f} m · arc {piece["circular_arc_m"]:.2f} m · chord {piece["chord_m"]:.2f} m · sagitta {piece["sagitta_m"]*1000:.0f} mm</text>')
        for fraction in (-.5, .5):
            plan.append(f'<path class="edge" d="M{at(inner-stock["width_m"]/2, fraction)} L{at(outer+stock["width_m"]/2, fraction)}"/>')
    else:
        plan.append('<text x="35" y="145" class="head">Pending a turning bay within the declared trial geometry</text>')
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 620" role="img" aria-labelledby="title">
<title id="title">{title}</title>
<style>
text{{font:16px sans-serif;fill:#182b3b}} .title{{font-size:27px;font-weight:bold}} .head{{font-size:19px;font-weight:bold}}
.edge,.track,.dim{{fill:none;stroke:#223c54;stroke-width:1.5}} .track{{stroke:#007c82;stroke-dasharray:8 4;stroke-width:2}}
</style>
<rect width="900" height="620" fill="#ffffff"/>
<text x="35" y="47" class="title">{title}</text><text x="35" y="76">{escape(subtitle)}</text>
{''.join(plan)}
<text x="35" y="376" class="head">Inherited U-girder section</text>
<path d="{profile}" fill="#d9e4ed" stroke="#223c54" stroke-width="2"/>
<path class="dim" d="M{x},{y+12}v16 m0,-8h{width} m0,-8v16 M{x-21},{y-depth}h12 m-6,0v{depth} m-6,0h12"/>
<text x="{x+width/2-24}" y="575">{stock['width_m']:.2f} m</text>
<text x="105" y="443">{stock['depth_m']:.2f} m</text>
<text x="586" y="415">Clear channel {stock['clear_channel_m']:.2f} m</text>
<text x="586" y="442">Webs {stock['web_m']*1000:.0f} mm · floor {stock['floor_m']*1000:.0f} mm</text>
<text x="586" y="469">Track pitch {PITCH_M:.2f} m</text>
<text x="35" y="592">Planning geometry · structural design, clearances and work fronts held for verification</text>
</svg>
"""


def render_dxf(record):
    """Render metre-unit R2000 CAD lines and true arcs for the plan and section."""
    data = []

    def add(*pairs):
        data.extend(f"{code}\n{value}" for code, value in pairs)

    def line(layer, start, end):
        add((0, "LINE"), (8, layer), (10, start[0]), (20, start[1]), (30, 0),
            (11, end[0]), (21, end[1]), (31, 0))

    def text(x, y, label):
        add((0, "TEXT"), (8, "LABELS"), (10, x), (20, y), (30, 0), (40, .35), (1, label))

    add((0, "SECTION"), (2, "HEADER"), (9, "$ACADVER"), (1, "AC1015"),
        (9, "$INSUNITS"), (70, 6), (0, "ENDSEC"))
    layers = {"STOCK_EDGE": 7, "TRACK_CENTRE": 4, "SECTION": 3, "LABELS": 2}
    add((0, "SECTION"), (2, "TABLES"), (0, "TABLE"), (2, "LAYER"), (70, len(layers)))
    for key, color in layers.items():
        add((0, "LAYER"), (2, key), (70, 0), (62, color), (6, "CONTINUOUS"))
    add((0, "ENDTAB"), (0, "ENDSEC"), (0, "SECTION"), (2, "ENTITIES"))

    stock = record["stock_section"]
    width, height = stock["width_m"], stock["depth_m"]
    web, floor_depth = stock["web_m"], stock["floor_m"]
    # Keep the section below the plan and draw both at model scale.
    profile = [(0, 0), (0, height), (web, height), (web, floor_depth),
               (width-web, floor_depth), (width-web, height), (width, height), (width, 0)]
    for start, end in zip(profile, profile[1:] + profile[:1], strict=True):
        line("SECTION", (start[0], start[1]-8), (end[0], end[1]-8))
    text(0, -9, f"U section {width:.2f} m wide, {height:.2f} m deep, {web:.2f} m web, {floor_depth:.2f} m floor")

    bay = record["representative_curved_bay"]
    if bay:
        sign = 1 if bay["turn_direction"] == "left" else -1
        orientation = 270 if sign > 0 else 90
        half = bay["sweep_deg"] / 2
        centre_y = sign * (bay["track_pieces"]["inside"]["radius_m"] + PITCH_M / 2)
        for side, piece in bay["track_pieces"].items():
            endpoints = [[], []]
            for offset, layer in ((-width/2, "STOCK_EDGE"), (0.0, "TRACK_CENTRE"), (width/2, "STOCK_EDGE")):
                radius = piece["radius_m"] + offset
                add((0, "ARC"), (8, layer), (10, 0), (20, centre_y), (30, 0),
                    (40, radius), (50, orientation-half), (51, orientation+half))
                for i, (end, lead) in enumerate(((-1, piece["tangent_lead_m"]), (1, piece["tangent_trail_m"]))):
                    angle = (orientation + sign * end * half) * pi / 180
                    x, y = radius * cos(angle), centre_y + radius * sin(angle)
                    tip = (x - sign * end * sin(angle) * lead, y + sign * end * cos(angle) * lead)
                    if lead:
                        line(layer, (x, y), tip)
                    if offset:
                        endpoints[i].append(tip)
            for ends in endpoints:
                line("STOCK_EDGE", *ends)
            text(13, 3 if side == "inside" else 2,
                 f"{side} R {piece['radius_m']:.3f} m / developed {piece['arc_length_m']:.3f} m")
        text(-10, 6, f"Bay {bay['id']}, {bay['sweep_deg']:.3f} deg {bay['turn_direction']}")
    text(-10, 7, f"Baghdad {record['candidate_id']} / metres / planning geometry")
    add((0, "ENDSEC"), (0, "EOF"))
    return "\n".join(data) + "\n"
