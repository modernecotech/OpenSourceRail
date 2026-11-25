"""Select a Baghdad planning layout on repeatable housing-to-centre journeys."""

from pathlib import Path
import tomllib

from . import central_access, holistic_access, holistic_pathways, residential_delivery, residential_layouts, residential_systems


CITY = Path(__file__).resolve().parent
POLICY = CITY / "residential-access.toml"
CENTRAL = CITY / "central-access.json"
NAMES = {"grid_reference": "Earlier grid", "terminal-trims": "Low-impact terminal trims",
         "western-tail-trims": "Western and outer tail trims", "extended-feeder-trims": "Extended feeder trims",
         "open-orbital-short": "Shorter open orbital", "open-orbital-east": "East-facing orbital arc",
         "western-bypass-withdrawal": "Western bypass withdrawal"}


def study_points(policy, population):
    raw = central_access.read(CENTRAL)
    landmarks = {row["name"]: row for row in raw["landmark_access"]}
    stations = raw["central_study"]["stations"]
    destination_inputs = []
    for definition in policy["centres"]:
        if "landmark" in definition:
            source = landmarks[definition["landmark"]]
            locator = source.get("source_url") or "Retained landmark in central-access.json"
        else:
            source = stations[definition["station_source"]]
            locator = source["source"]
        destination_inputs.append({"id": definition["id"], "name": source["name"],
                                   "coordinates": source["coordinates"], "weight": definition["weight"],
                                   "source": locator})
    destinations = tuple(holistic_pathways.CentreDestination(row["id"], tuple(row["coordinates"]),
                         row["weight"], row["name"]) for row in destination_inputs)
    scope = policy["access"]
    origins = holistic_pathways.sample_origins(population, tile_m=scope["origin_tile_m"],
                                              exclude_bounds=scope["outside_centre_bounds_wsen"])
    return origins, destinations, destination_inputs


def changes(stats, reference, walking_pp, reference_walking_pp):
    trip, base = stats["journeys"], reference["journeys"]
    time, before = trip["elapsed_p90_min"], base["elapsed_p90_min"]
    centres = {key: reference["destinations"][key]["served_share_pct"] - value["served_share_pct"]
               for key, value in stats["destinations"].items()}
    return {"served_loss_pp": round(base["served_share_pct"] - trip["served_share_pct"], 6),
            "one_change_loss_pp": round(base["reachable_with_at_most_share_of_all_pct"]["1"]
                                        - trip["reachable_with_at_most_share_of_all_pct"]["1"], 6),
            "destination_loss_pp": round(max(centres.values()), 6),
            "most_affected_destination": max(sorted(centres), key=centres.get),
            "walking_loss_pp": round(reference_walking_pp - walking_pp, 6),
            "p90_increase_min": round(time - before, 6) if time is not None and before is not None else None}


def choose_layout(variants, journeys, walking, policy):
    reference = journeys["grid_reference"]
    evidence = {}
    for code, option in variants.items():
        comparison = changes(journeys[code], reference, walking[code], walking["grid_reference"])
        exceeded = [key for key in ("served_loss_pp", "one_change_loss_pp", "destination_loss_pp",
                                    "walking_loss_pp", "p90_increase_min")
                    if comparison[key] is None or comparison[key] > policy[key]]
        evidence[code] = {"name": option.get("name", NAMES.get(code, code)), "candidate_id": option["network"]["candidate_id"],
                          "topology": option["network"]["topology"], "walking_1200_pp": walking[code],
                          "equivalent_access_screen": not exceeded, "exceeded": exceeded, "impact": comparison,
                          "actions": option["actions"], "housing_access": option["housing_access"],
                          "removed_route_km": option["removed_route_km"]}
    eligible = [code for code, record in evidence.items() if record["equivalent_access_screen"]]
    return min(eligible, key=lambda code: (
        variants[code]["network"]["topology"]["route_km"],
        -journeys[code]["journeys"]["reachable_with_at_most_share_of_all_pct"]["1"], code)), evidence


def test_access_links(trimmed, source_options, reference, comparison, policy, graph, context, demand):
    """Test mapped planning links on the trimmed layout with the same housing pairs."""
    from . import holistic_network

    alternatives = {"trimmed": trimmed}
    rejected = {}
    for code, option in sorted(source_options.items()):
        if code in trimmed["lines"]:
            continue
        if trimmed["topology"]["route_km"] + option["one_way_km"] >= reference["topology"]["route_km"]:
            rejected[code] = "The added route would remove the net track-length saving"
            continue
        try:
            alternatives[code] = holistic_network.insert_through_lines(trimmed, [option], graph=graph, context=context,
                                                                      connect_through_lines=True)
        except ValueError as error:
            rejected[code] = str(error)
    tests = holistic_pathways.compare(alternatives, **demand)
    if tests["demand_sample"]["sample_id"] != comparison["demand_sample"]["sample_id"]:
        raise ValueError("Access link trials must use the earlier housing-to-centre sample")
    first = tests["variants"]["trimmed"]["journeys"]
    control = comparison["variants"]["grid_reference"]
    eligible, results = [], {}
    for code, item in tests["variants"].items():
        if code == "trimmed":
            continue
        trips = item["journeys"]
        gap = changes(item, control, 0, 0)
        passed = (trips["served_share_pct"] > first["served_share_pct"]
                  and trips["reachable_with_at_most_share_of_all_pct"]["1"] >= first["reachable_with_at_most_share_of_all_pct"]["1"]
                  and all(gap[key] is not None and gap[key] <= policy[key] for key in
                          ("served_loss_pp", "destination_loss_pp", "one_change_loss_pp", "p90_increase_min")))
        if passed:
            eligible.append(code)
        results[code] = {"within_access_bands": passed, "topology": alternatives[code]["topology"], "journeys": trips,
                         "destination_losses_and_time": gap}
    chosen = min(eligible, key=lambda code: (-results[code]["journeys"]["served_share_pct"],
                 -results[code]["journeys"]["reachable_with_at_most_share_of_all_pct"]["1"],
                 results[code]["topology"]["route_km"], code)) if eligible else None
    evidence = {"selected_line": chosen, "evaluated": results, "rejected_before_assignment": rejected,
                "route_rule": "The resulting layout must stay shorter than the earlier grid. The added link must improve "
                              "two-change reach, preserve one-change reach and stay within the destination and journey time bands."}
    return chosen, alternatives, tests["variants"], evidence


def evaluate(network, population, baseline_walk, graph, context, *, build_reference, enforce_reference=True):
    config = tomllib.loads(POLICY.read_text())
    policy = config["access"]
    service = config["planning_service"]
    previous, previous_meta, _ = build_reference(network, population, baseline_walk, graph, context)
    if enforce_reference and previous["candidate_id"] != policy["reference_candidate_id"]:
        raise ValueError("Residential layout changes must start from the reconstructed grid reference")
    origins, destinations, centre_inputs = study_points(config, population)
    protected = {key: previous["stations"][key] for key in ("Tahrir", "Mansour", "Karkh", "Shorja", "University")}
    candidates = residential_layouts.alternatives(previous, population, graph, centres=protected)
    candidates = {"grid_reference": {"network": previous, "actions": [], "housing_access": {},
                                    "removed_route_km": 0}, **candidates}
    layouts = {key: option["network"] for key, option in candidates.items()}
    demand = dict(origins=origins, destinations=destinations, graph=graph,
                  assumptions=residential_systems.service_assumptions(service), origin_source=population.source)
    assignments = holistic_pathways.compare(layouts, **demand)
    walking = {key: 100 * option["housing_access"]["1200"]["estimated_residents_within_walk"] / float(population.counts.sum())
               for key, option in candidates.items() if key != "grid_reference"}
    previous_sites = {key: row["coordinates"] for key, row in previous["stations"].items()}
    previous_walk = holistic_access.walk_to_station(previous_sites, graph, population)[0]
    walking["grid_reference"] = 100 * float(population.counts[previous_walk <= 1200].sum() / population.counts.sum())
    selected, options = choose_layout(candidates, assignments["variants"], walking, policy)
    trim_code = selected
    extra, trials, trial_journeys, link_evidence = test_access_links(
        layouts[selected], previous_meta["comparisons"], previous, assignments, policy, graph, context, demand)
    if extra is not None:
        trial = trials[extra]
        positions = {key: row["coordinates"] for key, row in trial["stations"].items()}
        walk = holistic_access.walk_to_station(positions, graph, population)[0]
        selected = f"housing-link-{extra}"
        walking[selected] = 100 * float(population.counts[walk <= 1200].sum() / population.counts.sum())
        layouts[selected] = trial
        assignments["variants"][selected] = trial_journeys[extra]
        candidates[selected] = {"name": f"{options[trim_code]['name']} with {extra}", "network": trial,
                                "actions": options[trim_code]["actions"],
                                "removed_route_km": round(previous["topology"]["route_km"] - trial["topology"]["route_km"], 2),
                                "housing_access": residential_layouts._housing_access(population, previous_walk, walk)}
        _, options = choose_layout(candidates, assignments["variants"], walking, policy)
    revised = layouts[selected]
    matched = holistic_pathways.compare({key: layouts[key] for key in dict.fromkeys(("grid_reference", selected))},
                                        match_service_to="grid_reference", **demand)
    if matched["demand_sample"]["sample_id"] != assignments["demand_sample"]["sample_id"]:
        raise ValueError("The matched service check must use the same journeys")
    estimates = {}
    for key in dict.fromkeys(("grid_reference", selected)):
        construct = residential_delivery.evaluate(layouts[key])
        estimate = residential_systems.estimate(layouts[key], construct, service)
        if abs(estimate["service"]["running_train_km_day"] - assignments["variants"][key]["service"]["running_train_km_day"]) > .1:
            raise ValueError("Priced service must match the tested housing-to-centre service")
        estimates[key] = {"construction": construct, "systems": estimate}
    new_spine = [extra] if extra else []
    tags = {"selected": [code for code in [*previous_meta["selected"], *new_spine] if code in revised["lines"]],
            "spines": [code for code in [*previous_meta["spines"], *new_spine] if code in revised["lines"]],
            "local_links": [code for code in previous_meta["local_links"] if code in revised["lines"]],
            "comparisons": {code: {"screening": row["screening"]} for code, row in previous_meta["comparisons"].items()
                            if code in revised["lines"]},
            "residential": {"selection": selected, "policy": config, "destinations": centre_inputs,
                            "candidates": options, "common_service": assignments, "access_link_tests": link_evidence,
                            "equal_train_km": matched["variants"], "delivery": estimates}}
    return revised, tags, {"grid_reference": previous["stations"]}
