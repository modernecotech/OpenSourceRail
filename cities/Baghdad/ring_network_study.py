"""Compare cross-city route layouts and passenger use of Baghdad's wider rings."""

from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import tomllib

from . import (
    central_access, holistic_access, holistic_network, holistic_pathways,
    network_station_sites, residential_planning, residential_systems,
    ring_diameter_layout, ring_grid_journeys, ring_grid_spines, ring_radial_routes, ring_service_assignment,
    spaced_ring_comparison as compact, spaced_ring_layouts,
    wider_ring_comparison as wider,
)


CITY = wider.grid.CITY
REPORT = CITY / "RING-NETWORK.md"
RECORD = CITY / "ring-network.json"
FIGURE = CITY / "maps/baghdad-ring-network.png"
GEOJSON = CITY / "maps/baghdad-ring-network.geojson"
RINGS = ("M09", "M15")
BASE_NAMES = {"current": "Published city network", "wider": "Previous wider dual ring"}
WIDE_COHORT = ring_grid_journeys.WIDE_ANGLE_COHORT


def _retained(baseline, prior, graph, context, screen):
    outer, _ = wider.ring_corridors.evaluate_rings(baseline, graph, context, include_inner=False)
    # Rebuild the chosen physical network from the archived geometry and recipe,
    # then require the same identities as the public GIS.
    variants, _, rejected = wider._trials(outer, graph, context,
                                           prior["search"] | {"connectivity_alternative": None}, screen)
    key = prior["display_trial"]
    if key not in variants:
        raise ValueError(f"Previously published layout is unavailable: {rejected}")
    control = variants[key]
    public = central_access.read(wider.GEOJSON)
    if any(control[field] != public[field] for field in ("candidate_id", "evaluation_id")):
        raise ValueError("The reconstructed wider network does not match its publication")
    return control


def _direct_routes(network):
    ring_stations = {ring: set(network["lines"][ring]["station_ids"]) for ring in RINGS
                     if ring in network["lines"]}
    return [code for code, line in sorted(network["lines"].items()) if code not in RINGS
            and len(ring_stations) == 2
            and all(stops.intersection(line["station_ids"]) for stops in ring_stations.values())]


def _revision(control, trial):
    old, new = control["lines"], trial["lines"]
    added, removed = sorted(new.keys() - old.keys()), sorted(old.keys() - new.keys())
    aligned = sorted(code for code in old.keys() & new.keys() if old[code]["geometry"] != new[code]["geometry"])
    services = sorted(code for code in old.keys() & new.keys() if code not in RINGS
                      and code not in aligned and old[code]["station_ids"] != new[code]["station_ids"])
    return {"added_routes": added, "withdrawn_routes": removed, "realigned_routes": aligned,
            "changed_station_calls": services, "changed_alignment": bool(added or removed or aligned)}


def _check_layout(control, net):
    if holistic_network.validate(net) != net["topology"]:
        raise ValueError("Passenger topology and layout record disagree")
    if any(net["lines"][ring]["geometry"] != control["lines"][ring]["geometry"] for ring in RINGS):
        raise ValueError("A reworked route changed a retained ring alignment")
    if net["lines"]["C1"]["geometry"] != control["lines"]["C1"]["geometry"]:
        raise ValueError("A reworked route changed the Airport alignment")
    if set(wider.grid.PROTECTED) - net["stations"].keys():
        raise ValueError("A named destination no longer has a station")
    if len(_direct_routes(net)) < 2:
        raise ValueError("At least two direct through services between the rings are needed")
    if holistic_network._identity(dict(net))["evaluation_id"] != net["evaluation_id"]:
        raise ValueError("Candidate inputs do not match their sealed evaluation")


def _summarize(networks, geometry, walks, housing, assignment):
    summary = {}
    for code, net in networks.items():
        route = geometry[code]
        passenger = assignment["variants"][code]
        wide = passenger["cohorts"][WIDE_COHORT]["journeys"]
        paired = passenger["paired_wide_angle_vs_reference"]
        summary[code] = {
            "lines": route["lines"], "stations": route["stations"], "route_km": route["route_km"],
            "parallel_pair_km": route["parallel_pair_km"], "rings": route["rings"],
            "candidate_id": net["candidate_id"], "evaluation_id": net["evaluation_id"],
            "close_site_pairs": len(network_station_sites._nearby(net["stations"], spaced_ring_layouts.CLOSE_SITE_M)),
            "direct_routes": _direct_routes(net),
            "walk_1200_pct": walks["worldpop-2026"]["metropolitan"]["cases"][code]["1200"]["share_pct"],
            "walk_1200_ghsl_pct": walks["ghsl-2025"]["metropolitan"]["cases"][code]["1200"]["share_pct"],
            "all_trips_pct": passenger["journeys"]["served_share_pct"],
            "wide_trips_pct": wide["served_share_pct"],
            "wide_two_changes_pct": wide["at_most_two_transfers_share_of_all_pct"],
            "wide_same_trip_p90_min": paired["candidate_elapsed_p90_min"],
            "wider_same_trip_p90_min": paired["reference_elapsed_p90_min"],
            "households_two_changes_pct": housing["variants"][code]["journeys"][
                "reachable_with_at_most_share_of_all_pct"]["2"],
            "using_ring_pct": passenger["ring_use"]["either"]["share_of_all_pct"],
            "inner_used_pct": passenger["ring_use"]["M15"]["share_of_served_pct"],
            "outer_used_pct": passenger["ring_use"]["M09"]["share_of_served_pct"],
            "both_used_pct": passenger["ring_use"]["both"]["share_of_served_pct"],
        }
    return summary


def _pick(summary, revisions):
    baseline = summary["wider"]
    changed = [code for code, row in revisions.items() if row["changed_alignment"]]
    if not changed:
        raise ValueError("A rings-and-lines redesign needs a physically changed route")
    comparable = [code for code in changed if summary[code]["route_km"] <= baseline["route_km"] * 1.02
                  and summary[code]["lines"] <= baseline["lines"]]
    balanced = [code for code in comparable if summary[code]["walk_1200_pct"] >= baseline["walk_1200_pct"] - .5
                and summary[code]["households_two_changes_pct"] >= baseline["households_two_changes_pct"] - .5
                and summary[code]["wide_trips_pct"] >= baseline["wide_trips_pct"] - .5]
    eligible = balanced or comparable or changed
    selected = max(eligible, key=lambda code: (
        summary[code]["households_two_changes_pct"], summary[code]["wide_trips_pct"],
        -summary[code]["parallel_pair_km"], len(summary[code]["direct_routes"]),
        summary[code]["wide_two_changes_pct"], summary[code]["walk_1200_pct"]))
    tier = ("matched kilometres, route count and access" if balanced else
            "matched kilometres and route count" if comparable else "physical redesign")
    return selected, {"basis": tier, "eligible_trials": eligible}


def _refine_diameter(proposal, graph, context):
    reference = proposal.get("network")
    if reference is None:
        return {}
    options = {}
    for key, label, edits in (
        ("diameter-turnback", "East–west diameter and G09 turnback", (ring_radial_routes._g09_terminal,)),
        ("diameter-walk-turnback", "East–west diameter with the G09 and M02 ring links",
         (ring_radial_routes._m02_access, ring_radial_routes._g09_terminal)),
    ):
        candidate = deepcopy(reference)
        try:
            actions = [edit(candidate, graph, context) for edit in edits]
            revised = ring_radial_routes._finish(candidate, reference, key, actions)
        except ValueError as error:
            options[key] = {"name": label, "rejection_reason": str(error)}
            continue
        options[key] = {"name": label, "network": revised, "actions": proposal["actions"] + actions,
                        "diameters": [row["id"] for row in proposal["routes"]]}
    return options


def evaluate(baseline_path):
    baseline = central_access.read(baseline_path)
    current = baseline["network"]
    prior = central_access.read(wider.RECORD)
    if central_access.digest(baseline_path) != prior["reference_packet_sha256"]:
        raise ValueError("Use the published city network from the wider-ring comparison")
    graph = central_access.walking_graph()
    context = central_access.original_cases()[3]
    policy = tomllib.loads(residential_planning.POLICY.read_text())
    screen = policy["corridor_screen"]
    control = _retained(current, prior, graph, context, screen)
    population = holistic_access.load_population("worldpop-2026", graph)
    proposals = ring_radial_routes.alternatives(control, graph, context)
    proposals["diameters"] = ring_diameter_layout.compare(
        control, graph, context, population=population, protected_stations=wider.grid.PROTECTED)
    proposals.update(_refine_diameter(proposals["diameters"], graph, context))
    networks = {"current": current, "wider": control}
    revisions, holds = {}, {}
    for name, proposal in proposals.items():
        candidate = proposal.get("network")
        if candidate is None:
            holds[name] = proposal.get("rejection_reason", "Layout construction failed")
            continue
        try:
            _check_layout(control, candidate)
        except ValueError as error:
            holds[name] = str(error)
            continue
        if candidate["candidate_id"] not in {net["candidate_id"] for net in networks.values()}:
            networks[name] = candidate
            revisions[name] = _revision(control, candidate)
    if not revisions:
        raise ValueError(f"No changed line layouts passed: {holds}")
    coverage, population = wider.grid._walk_access(networks, graph)
    assumptions = residential_systems.service_assumptions(policy["planning_service"])
    origins, destinations, _ = residential_planning.study_points(policy, population)
    housing = holistic_pathways.compare(networks, graph=graph, origins=origins, destinations=destinations,
                                       assumptions=assumptions, origin_source=population.source,
                                       match_service_to="current")
    use = ring_service_assignment.compare(networks, reference="current", paired_reference="wider",
                                          graph=graph, population=population, assumptions=assumptions, housing=housing)
    prior_housing = prior["same_train_km_housing"]["demand_sample"]["sample_id"]
    prior_metro = prior["same_train_km_metropolitan"]["demand_sample"]
    old_service = prior["same_train_km_metropolitan"]["variants"]["current"]["service"]["running_train_km_day"]
    if (housing["demand_sample"]["sample_id"] != prior_housing
            or use["demand_sample"]["coordinates_lon_lat_and_tile_people"] != prior_metro["coordinates_lon_lat_and_tile_people"]
            or use["variants"]["current"]["service"]["running_train_km_day"] != old_service
            or use["variants"]["wider"]["journeys"]
            != prior["same_train_km_metropolitan"]["variants"][prior["display_trial"]]["journeys"]):
        raise ValueError("Journey input or wider-layout control differs from the published comparison")

    geometry = {key: wider.grid._geometry(network, screen) for key, network in networks.items()}
    summary = _summarize(networks, geometry, coverage, housing, use)
    chosen, selection = _pick(summary, revisions)
    # The earlier allowances are bound to both identical control candidates.
    prior_cost = prior["six_minute_delivery_and_cost"]
    costs = {"current": prior_cost["current"], "wider": prior_cost[prior["display_trial"]]}
    priced = [chosen]
    stronger = [code for code in revisions if code != chosen and revisions[code]["changed_alignment"]
                and summary[code]["parallel_pair_km"] < summary[chosen]["parallel_pair_km"]]
    if stronger:
        priced.append(min(stronger, key=lambda code: summary[code]["parallel_pair_km"]))
    costs.update(wider.grid._price({key: networks[key] for key in priced}, policy["planning_service"]))
    if any(cost["candidate_id"] != summary[key]["candidate_id"] for key, cost in costs.items()):
        raise ValueError("The construction allowances and passenger layouts refer to different candidates")

    sources = prior["sources"] | baseline["sources"] | control["source_sha256"] | networks[chosen]["source_sha256"]
    for file in (Path(__file__), Path(ring_radial_routes.__file__), Path(ring_diameter_layout.__file__),
                 Path(ring_service_assignment.__file__), Path(ring_grid_journeys.__file__),
                 Path(ring_grid_spines.__file__), Path(wider.grid.__file__), Path(wider.__file__),
                 wider.RECORD, wider.GEOJSON, residential_planning.POLICY):
        sources[compact._file_id(file)] = central_access.digest(file)
    record = {"schema": "osr-baghdad-ring-network/1", "display_trial": chosen, "selection": selection, "summary": summary,
              "prior_wider_comparison_id": prior["comparison_id"], "reference_packet_sha256": central_access.digest(baseline_path),
              "proposals": {key: {field: value for field, value in entry.items() if field != "network"}
                            for key, entry in proposals.items()},
              "route_revisions": revisions, "held_trials": holds,
              "assumption_sources": sources, "geometry": geometry, "coverage": coverage,
              "household_journeys": housing, "ring_service": use, "six_minute_delivery_and_cost": costs,
              "ring_geometry": compact._screen_rings(networks[chosen])}
    record["comparison_id"] = sha256(central_access.encode(record)).hexdigest()
    return record, networks, context
