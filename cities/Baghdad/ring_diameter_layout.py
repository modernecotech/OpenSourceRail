"""Test a pair of direct cross-city routes serving both Baghdad orbitals."""

from itertools import combinations
from pathlib import Path

from shapely.geometry import LineString

from . import central_access, holistic_access, holistic_network, rail_consolidation, ring_grid_spines, spaced_ring_layouts


RINGS = {"M09", "M15"}
EXCHANGE = {"G13", "G11", "T19"}
CHECKS_PER_DIRECTION = 16
PAIRS_TO_TEST = 36


def _served_rings(network, code):
    return {ring for ring in RINGS if set(network["lines"][ring]["station_ids"])
            & set(network["lines"][code]["station_ids"])}


def _insert(network, axes, graph, context, protected_stations):
    codes = [axis["id"] for axis in axes]
    revised = holistic_network.insert_through_lines(network, axes, graph=graph, context=context,
                                                    connect_through_lines=len(codes) == 2)
    revised, audit = spaced_ring_layouts._consolidate(revised, graph, context, set(protected_stations))
    if len(codes) == 2 and not ring_grid_spines._cross(revised, *codes):
        raise ValueError("The diameters lack a shared intermediate station with mapped access")
    if any(_served_rings(revised, code) != RINGS for code in codes):
        raise ValueError("Each diameter must serve both rings at shared stations")
    return revised, audit


def _record(revised, axes, actions, removed_walks, station_audit, parent, evidence):
    revised["ring_diameter_layout"] = {"parent_candidate_id": parent["candidate_id"], "routes": axes,
                                         "withdrawals": actions, "removed_walks": removed_walks}
    source = Path(__file__)
    revised["source_sha256"][source.relative_to(central_access.ROOT).as_posix()] = central_access.digest(source)
    return evidence | {"network": rail_consolidation.refresh_interchange_names(revised),
                       "name": "Cross-city diameter pair" if len(axes) == 2 else "Cross-city diameter",
                       "actions": [*actions, *({"action": "add_diameter", "line_id": row["id"],
                                               "route_km": row["one_way_km"]} for row in axes)],
                       "routes": axes, "station_audit": station_audit}


def compare(network, graph, context, *, population, protected_stations):
    """Exchange three routes for two intersecting diameters at the same guideway limit."""
    try:
        skeleton, actions, removed_walks = ring_grid_spines._withdraw(network, EXCHANGE, protected_stations)
    except ValueError as error:
        return {"rejection_reason": str(error)}
    route_budget = ring_grid_spines._route_km(network)
    available = route_budget - ring_grid_spines._route_km(skeleton)
    sites = {code: row["coordinates"] for code, row in skeleton["stations"].items()}
    walks = holistic_access.walk_to_station(sites, graph, population)[0]
    coverage = holistic_access.coverage_cells(population, walks)
    pool = ring_grid_spines._screen(skeleton, graph, context, coverage)
    admitted, rejected, checked = [], [], {}
    ring_traces = [LineString(network["lines"][code]["geometry"]) for code in sorted(RINGS)]
    for axis in pool:
        family = axis["family"]
        if checked.get(family, 0) == CHECKS_PER_DIRECTION:
            continue
        # Require each diameter to reach both rings. Check the cheaper geometric
        # condition before proposing intermediate platforms and transfer stations.
        trace = LineString(axis["geometry"])
        if not all(trace.intersects(ring) for ring in ring_traces):
            continue
        checked[family] = checked.get(family, 0) + 1
        row = ring_grid_spines._describe(skeleton, axis, graph, context)
        if row is not None:
            required = {entry["line_id"] for entry in row["required_interchanges"]}
            at_ends = {code for stop in row["terminal_ids"] for code in skeleton["stations"][stop]["lines"]}
            if RINGS <= (required | at_ends):
                admitted.append(row)
    pairs = sorted(
        (pair for pair in combinations(admitted, 2) if pair[0]["family"] != pair[1]["family"]
         and ring_grid_spines._bearing_delta(*pair) >= 45 and sum(row["one_way_km"] for row in pair) <= available),
        key=lambda pair: (-sum(row["screening"]["distance_proxy_score"] for row in pair),
                          tuple(row["id"] for row in pair)),
    )
    evidence = {"trials_by_direction": checked, "admitted_axes": [item["id"] for item in admitted],
                "paired_axes": len(pairs), "rejected_pairs": rejected}
    for pair in pairs[:PAIRS_TO_TEST]:
        codes = [row["id"] for row in pair]
        try:
            revised, station_audit = _insert(skeleton, pair, graph, context, protected_stations)
        except ValueError as error:
            rejected.append({"lines": codes, "reason": str(error)})
            continue
        return _record(revised, pair, actions, removed_walks, station_audit, network, evidence)
    evidence["pair_hold"] = "No pair passed the both-ring transfer, shared-interchange, angle and route-length screens"
    single_rejections = evidence["single_rejections"] = []
    for removed in ({"G13", "T19"}, {"G13", "G11"}):
        try:
            local, local_actions, walks_removed = ring_grid_spines._withdraw(network, removed, protected_stations)
        except ValueError as error:
            single_rejections.append({"withdrawn": sorted(removed), "reason": str(error)})
            continue
        available = route_budget - ring_grid_spines._route_km(local)
        for row in admitted:
            if row["one_way_km"] > available:
                continue
            option = ring_grid_spines._describe(local, row, graph, context)
            if option is None:
                continue
            try:
                revised, station_audit = _insert(local, [option], graph, context, protected_stations)
            except ValueError as error:
                single_rejections.append({"withdrawn": sorted(removed), "axis": row["id"], "reason": str(error)})
                continue
            return _record(revised, [option], local_actions, walks_removed, station_audit, network, evidence)
    return evidence | {"rejection_reason": "The bounded single and paired diameter proposals could not be installed"}
