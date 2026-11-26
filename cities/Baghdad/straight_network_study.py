"""Model cross-Tigris through routes and the matching Baghdad delivery quantities."""

from copy import deepcopy
from dataclasses import replace
from hashlib import sha256
from math import fsum, isclose
from pathlib import Path
import tomllib

from engineering.outline import network_policy

from . import (
    central_access, central_ring_study as central, holistic_access, holistic_network, holistic_pathways,
    residential_delivery, residential_planning, residential_systems, ring_corridors,
    ring_service_assignment, straight_through_layout,
)
from .engineering.mechanical.civil import alignment_beams


CITY = central.CITY
REPORT = CITY / "STRAIGHT-THROUGH-NETWORK.md"
DELIVERY = CITY / "STRAIGHT-THROUGH-DELIVERY.md"
RECORD = CITY / "straight-through-network.json"
MAP = CITY / "maps/baghdad-straight-through-network.png"
COMPARISON_MAP = CITY / "maps/baghdad-straight-through-comparison.png"
DETAIL_MAP = CITY / "maps/baghdad-through-interchanges.png"
GEOJSON = CITY / "maps/baghdad-straight-through-network.geojson"
BEAM_PLAN = CITY / "engineering/mechanical/civil/CURVED-BEAM-PROGRAMME.md"
BEAM_CSV = CITY / "engineering/mechanical/civil/curved-beam-register.csv"
BEAM_DRAWING = CITY / "engineering/mechanical/civil/curved-beam-families.svg"
BEAM_CAD = CITY / "engineering/mechanical/civil/curved-beam-families.dxf"
BEAM_DATA = CITY / "engineering/mechanical/civil/curved-beam-register.json.gz"
NAMES = {"current": "Published city network control", "central": "Earlier central-ring comparison"}


def _published_central():
    gis = central_access.read(central.GEOJSON)
    lines, stations, walking = {}, {}, []
    for feature in gis["features"]:
        props = feature["properties"]
        geometry = feature["geometry"]["coordinates"]
        kind = props["kind"]
        if kind == "line":
            lines[props["line_id"]] = {k: v for k, v in props.items() if k not in {"line_id", "kind"}} | {
                "geometry": geometry}
        elif kind in {"station", "interchange"}:
            stations[props["station_id"]] = {k: v for k, v in props.items() if k not in {"station_id", "kind"}} | {
                "coordinates": geometry}
        elif kind == "walking-interchange":
            walking.append({k: v for k, v in props.items() if k not in {"kind", "stroke"}} | {"geometry": geometry})
    record = {"lines": lines, "stations": stations, "station_site_links": walking, "transfers": [],
              "physical_accepted": False, "operating_timetable_validated": False,
              "imported_evaluation_id": gis["evaluation_id"],
              "source_sha256": {central.GEOJSON.relative_to(central_access.ROOT).as_posix(): central_access.digest(central.GEOJSON)}}
    ring_corridors._refresh_transfers(record)
    record["topology"] = holistic_network.validate(record)
    result = holistic_network._identity(record)
    if result["candidate_id"] != gis["candidate_id"]:
        raise ValueError("Earlier central GIS differs from the published physical layout")
    return result


def _verify_through(net, previous, item):
    central._check(net, previous)
    if net["lines"]["M15"]["geometry"] != previous["lines"]["M15"]["geometry"]:
        raise ValueError("The changed through layout must use the same central ring")
    proofs = item["certified_through"]
    if len(proofs) < 2 or len({row["id"] for row in proofs}) != len(proofs):
        raise ValueError("The candidate needs at least two independently mapped new through services")
    for row in proofs:
        code = row["id"]
        calls = set(net["lines"][code]["station_ids"])
        shares = {ring: calls & set(net["lines"][ring]["station_ids"]) for ring in central.RINGS}
        if not all(shares.values()) or any(set(row["ring_interchanges"][ring]) != share
                                            for ring, share in shares.items()):
            raise ValueError(f"{code} needs verified shared passenger stations on both rings")
        failures = network_policy.crossing_failures(
            detour_ratio=row["detour_ratio"], maximum_detour_ratio=network_policy.MAXIMUM_DETOUR_RATIO,
            water_required=True, water_crossings=row["tigris_crossing_count"] if row["mapped_bridge_approaches"] else 0,
            required_ring_ids=central.RINGS, ring_interchanges=shares)
        if failures:
            raise ValueError(f"{code}: {', '.join(failures)}")
    return proofs


def _pick(summary, proposals, policy):
    reference = summary["central"]
    walk_loss = policy["access"]["walking_loss_pp"]
    housing_loss = policy["network_redesign"]["max_two_change_loss_pp"]
    outer_loss = policy["corridor_selection"]["served_loss_pp"]
    acceptable = [code for code in proposals if code in summary
                  and summary[code]["metro_walk_1300_pct"] >= reference["metro_walk_1300_pct"] - walk_loss
                  and summary[code]["central_walk_1300_pct"] >= reference["central_walk_1300_pct"] - walk_loss
                  and summary[code]["housing_two_changes_pct"] >= reference["housing_two_changes_pct"] - housing_loss
                  and summary[code]["wide_trips_pct"] >= reference["wide_trips_pct"] - outer_loss
                  and summary[code]["central_centres_via_connection"] == reference["central_centres_via_connection"]]
    through_both_ends = [code for code in acceptable
                         if all(row["terminals_outside_outer_ring"] == 2 for row in proposals[code])]
    feasible_new = [code for code in through_both_ends if summary[code]["candidate_id"] != reference["candidate_id"]]
    if not feasible_new:
        raise ValueError("No new through layout preserved the required pedestrian and passenger access")
    chosen = max(feasible_new, key=lambda code: (-summary[code]["parallel_pair_km"], -summary[code]["lines"],
                                                 summary[code]["housing_two_changes_pct"], summary[code]["wide_trips_pct"],
                                                 -summary[code]["route_km"]))
    return chosen, {"matched_access": acceptable, "both_terminals_outside_outer_ring": through_both_ends,
                    "displayed_clears_matched_access": chosen in acceptable, "walking_loss_pp": walk_loss,
                    "housing_loss_pp": housing_loss, "outer_loss_pp": outer_loss}


def integrate_curves(base, beams):
    """Add the special-form allowance once on the standard-stock price basis."""
    if base["candidate_id"] != beams["candidate_id"]:
        raise ValueError("The delivery and curved-stock layouts must match")
    overlap = base["quantities"]["service_overlap_km"] * 1000
    totals = beams["totals"]
    held_overlap = (totals["shared_alignment_mapped_service_trace_m_before_deduplication"]
                    - totals["shared_alignment_unique_physical_m"])
    if not isclose(overlap, held_overlap, abs_tol=1e-5):
        raise ValueError("Coincident beam edges and distinct civil quantities must reconcile")
    delivery = deepcopy(base)
    delivery["stock_reference_evaluation_id"] = delivery.pop("evaluation_id")
    delivery["beam_evaluation_id"] = beams["evaluation_id"]
    delivery["source_sha256"].update(beams["source_sha256"])
    for case, row in delivery["cost_cases"].items():
        extra = beams["totals"]["incremental_allowance_usd"][case] / 1e6
        row["scope_usd_m"]["special_beam_increment"] = extra
        row["direct_usd_m"] = fsum(row["scope_usd_m"].values())
        row["direct_iqd_trillion"] = row["direct_usd_m"] * delivery["assumptions"]["iqd_per_usd"] / 1e6
        row["matched_road_direct_usd_m"] += extra
    delivery["cost_scope"] += " The curved and short-stock premium is applied once to both matched methods."
    delivery["holds"].extend(beams["holds"])
    delivery["evaluation_id"] = sha256(central_access.encode(delivery)).hexdigest()
    return delivery


def _selected_resources(network, context, policy):
    base = residential_delivery.evaluate(network)
    beams = alignment_beams.evaluate(network, context=context)
    if beams["candidate_id"] != base["candidate_id"]:
        raise ValueError("Beam fabrication, passenger service and delivery need the same mapped configuration")
    mapped_beam_m = fsum(row["reference_length_m"] for row in beams["routes"].values())
    if not isclose(mapped_beam_m, base["quantities"]["service_route_km"] * 1000, abs_tol=1e-5):
        raise ValueError("Reference beam chainage and the costed service route must have equal lengths")
    delivery = integrate_curves(base, beams)
    system = residential_systems.estimate(network, delivery, policy["planning_service"])
    return beams, delivery, system


def evaluate(baseline_path):
    baseline = central_access.read(baseline_path)
    archive = central_access.read(central.RECORD)
    if central_access.digest(baseline_path) != archive["reference_packet_sha256"]:
        raise ValueError("The through study and earlier networks require the same published reference")
    current, prior = baseline["network"], _published_central()
    graph = central_access.walking_graph()
    context = central_access.original_cases()[3]
    policy = tomllib.loads(residential_planning.POLICY.read_text())
    populations = {key: holistic_access.load_population(key, graph) for key in ("worldpop-2026", "ghsl-2025")}
    people = populations["worldpop-2026"]
    origins, centres, centre_sources = residential_planning.study_points(policy, people)
    proposals = straight_through_layout.alternatives(prior, graph, context, population=people,
                                                     protected_stations=central.previous.wider.grid.PROTECTED)
    networks, approved, held = {"current": current, "central": prior}, {}, {}
    for code, item in proposals.items():
        net = item.get("network")
        if net is None:
            held[code] = item.get("rejection_reason", "No qualifying physical layout")
            continue
        try:
            proofs = _verify_through(net, prior, item)
        except ValueError as error:
            held[code] = str(error)
            continue
        networks[code] = net
        approved[code] = proofs
    if not approved:
        raise ValueError(f"No through proposal passed the mapped both-ring checks: {held}")
    coverage = central._coverage(networks, graph, populations, centres)
    screen = policy["corridor_screen"]
    geometry = {key: central.previous.wider.grid._geometry(net, screen) for key, net in networks.items()}
    assumptions = replace(residential_systems.service_assumptions(policy["planning_service"]), walk_limit_m=central.WALK_NEW)
    housing = holistic_pathways.compare(networks, graph=graph, assumptions=assumptions, origins=origins,
                                       destinations=centres, origin_source=people.source, match_service_to="current")
    passenger = ring_service_assignment.compare(networks, reference="current", paired_reference="central",
                                                graph=graph, population=people, assumptions=assumptions, housing=housing)
    if (archive["household_journeys"]["demand_sample"]["sample_id"]
            != housing["demand_sample"]["sample_id"]
            or archive["ring_service"]["demand_sample"]["sample_id"] != passenger["demand_sample"]["sample_id"]):
        raise ValueError("The new geometry study changed the common passenger sample")
    summary = central._summary(networks, coverage, geometry, housing, passenger)
    chosen, selection = _pick(summary, approved, policy)
    net = networks[chosen]
    beam, delivery, system = _selected_resources(net, context, policy)
    sources = archive["assumption_sources"] | baseline["sources"] | net["source_sha256"] | delivery["source_sha256"]
    inputs = (Path(__file__), Path(__file__).with_name("straight_network_publication.py"),
              Path(straight_through_layout.__file__), Path(network_policy.__file__),
              Path(residential_systems.__file__), Path(central.__file__), Path(alignment_beams.__file__),
              residential_planning.POLICY, central.RECORD, central.GEOJSON)
    sources.update({path.relative_to(central_access.ROOT).as_posix(): central_access.digest(path) for path in inputs})
    record = {"schema": "osr-baghdad-straight-through/1", "display_trial": chosen, "selection": selection,
              "network": net, "summary": summary, "geometry": geometry, "coverage": coverage, "household_journeys": housing,
              "ring_service": passenger, "approved_through": approved, "held_trials": held,
              "layouts": {key: {field: value for field, value in item.items() if field != "network"}
                          for key, item in proposals.items()},
              "centre_sources": centre_sources, "previous_comparison_id": archive["comparison_id"],
              "previous_cost": archive["six_minute_delivery_and_cost"][archive["display_trial"]],
              "cost": system, "civil": delivery, "beam_schedule": beam, "source_sha256": sources}
    record["publication_id"] = sha256(central_access.encode(public_record(record))).hexdigest()
    return record, networks, context


def public_record(record):
    """Keep the route-by-route beam work orders in their own source-bound file."""
    beam = record["beam_schedule"]
    return dict(record) | {"beam_schedule": {key: value for key, value in beam.items() if key != "routes"},
                           "beam_register_path": BEAM_DATA.relative_to(CITY).as_posix()}
