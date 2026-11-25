"""Compare concentric rings and through lines with the published Baghdad network."""

import argparse
from hashlib import sha256
from pathlib import Path
import tomllib

import numpy as np

from engineering.performance import disk_reservation

from . import central_access, holistic_access, holistic_network, holistic_pathways, rail_duplication
from . import residential_delivery, residential_layouts, residential_planning, residential_systems


CITY = Path(__file__).resolve().parent
BASELINE = CITY / "baghdad-network.json"
REFERENCE_ID = "baghdad-network-4db07c3dba693eba"
REFERENCE_COMMIT = "9623c41c81aa51298918bebccc49884b3b29c90f"
REPORT = CITY / "RING-GRID.md"
RECORD = CITY / "ring-grid.json"
FIGURE = CITY / "maps/baghdad-ring-grid.png"
GEOJSON = CITY / "maps/baghdad-ring-grid.geojson"
PROTECTED = ("Tahrir", "Mansour", "Karkh", "Shorja", "University")
NAMES = {"current": "Published network", "overlay": "Both rings added to the published network",
         "inner-overlay": "Inner ring added to the published network",
         "grid": "Two rings and cross-city grid", "one-ring-grid": "Outer ring and the same grid",
         "grid-gap-retention": "Two rings, grid and northern gap links",
         "compact": "Two rings and compact set of through lines", "orthogonal": "Two rings and orthogonal spines",
         "diagonal": "Two rings and diagonal spines"}


def _route_km(network):
    return sum(line["one_way_km"] for line in network["lines"].values())


def _walk_access(networks, graph):
    stations = {key: {code: row["coordinates"] for code, row in network["stations"].items()}
                for key, network in networks.items()}
    summaries, populations = {}, {}
    for name in ("worldpop-2026", "ghsl-2025"):
        people = holistic_access.load_population(name, graph)
        distances = {key: holistic_access.walk_to_station(sites, graph, people)[0] for key, sites in stations.items()}
        summaries[name] = holistic_access.summarize(people, distances)
        populations[name] = people
    return summaries, populations["worldpop-2026"]


def _geometry(network, screen):
    overlaps = rail_duplication.screen(network["lines"], **screen)["runs"]
    axes = network.get("ring_grid_layout", {}).get("axes", [])
    return {**network["topology"], "candidate_id": network["candidate_id"], "new_through_axes": axes,
            "rings": {code: {"route_km": row["one_way_km"], "stations": len(row["station_ids"]),
                             "interchanges": sum(len(network["stations"][stop]["lines"]) > 1 for stop in row["station_ids"])}
                      for code, row in network["lines"].items() if row["loop"]},
            "parallel_pair_km": round(sum(row["length_m"] for row in overlaps if row["kind"] == "nearby_parallel") / 1000, 3),
            "coincident_pair_km": round(sum(row["length_m"] for row in overlaps if row["kind"] == "common_alignment") / 1000, 3),
            "parallel_runs": overlaps}


def _price(networks, service):
    answers = {}
    for key, network in networks.items():
        civil = residential_delivery.evaluate(network)
        costs = residential_systems.estimate(network, civil, service)
        quant, crew, programme = (civil[k] for k in ("quantities", "workforce", "programme"))
        answers[key] = {"candidate_id": network["candidate_id"], "unique_guideway_km": quant["unique_guideway_km"],
                        "track_km": quant["double_track_km"], "standard_bays": quant["standard_bays"],
                        "paid_casting_haul_and_erection_hours": crew["paid_deck_and_casting_hours"],
                        "standard_deck_handover_day": programme["last_standard_deck_day"],
                        "fleet_including_spares": costs["service"]["fleet_trainsets"],
                        "annual_running_train_km": costs["service"]["running_train_km_year"],
                        "cases": {case: {name: row[name] for name in ("installed_planning_usd_m",
                                  "annual_operations_total_usd_m", "whole_life_present_usd_m")}
                                  for case, row in costs["cost_cases"].items()}}
    return answers


def assess(networks, graph, *, baseline_record, trials, ring_evidence):
    from . import ring_grid_journeys

    policy = tomllib.loads(residential_planning.POLICY.read_text())
    service = policy["planning_service"]
    assumptions = residential_systems.service_assumptions(service)
    coverage, population = _walk_access(networks, graph)
    origins, destinations, _ = residential_planning.study_points(policy, population)
    housing = holistic_pathways.compare(networks, graph=graph, assumptions=assumptions, origins=origins,
                                       destinations=destinations, origin_source=population.source, match_service_to="current")
    journeys = ring_grid_journeys.compare(networks, reference="current", graph=graph, population=population,
                                         assumptions=assumptions)
    geometry = {key: _geometry(network, policy["corridor_screen"]) for key, network in networks.items()}
    costs = _price(networks, service)
    reference_service = housing["variants"]["current"]["service"]["running_train_km_day"]
    for key, row in housing["variants"].items():
        if abs(row["service"]["running_train_km_day"] - reference_service) > .01:
            raise ValueError(f"{key} differs from the common train-km budget")
    return {"schema": "osr-baghdad-ring-grid-comparison/1", "reference_revision": REFERENCE_COMMIT,
            "reference_publication_id": baseline_record["publication_id"], "geometry": geometry,
            "same_train_km_housing": housing, "same_train_km_metropolitan": journeys, "coverage": coverage,
            "six_minute_delivery_and_cost": costs, "trial_metadata": trials, "ring_evidence": ring_evidence}


def _single_ring(network):
    """Use identical surviving routes to isolate the inner ring's contribution."""
    return residential_layouts.apply_edits(network, [residential_layouts.LineEdit(
        "M15", "Remove the inner ring for a paired one-ring comparison.")], protected_stations=PROTECTED)[0]


def layouts(current, graph, context, ring_corridors, ring_grid_spines):
    overlay, evidence = ring_corridors.evaluate_rings(current, graph, context)
    if any(not overlay["lines"].get(key, {}).get("loop") for key in ("M09", "M15")):
        raise ValueError("The ring study requires two independently closed mapped alignments")
    population = holistic_access.load_population("worldpop-2026", graph)
    sites = {key: row["coordinates"] for key, row in current["stations"].items()}
    walk = holistic_access.walk_to_station(sites, graph, population)[0]
    cells = holistic_access.coverage_cells(population, walk)
    results = ring_grid_spines.alternatives(overlay, graph, context, route_km_limit=_route_km(current),
                                           protected_stations=PROTECTED, coverage_cells=cells)
    networks = {"current": current, "overlay": overlay}
    inner, inner_evidence = ring_corridors.inner_only(current, graph, context)
    if inner["lines"].get("M15", {}).get("loop"):
        networks["inner-overlay"] = inner
    evidence = evidence | {"inner_overlay": inner_evidence}
    trials = {"proposals": {key: {"topology": row["network"]["topology"] if row.get("network") else None,
                                   **{name: val for name, val in row.items() if name != "network"}}
                            for key, row in results.items()}, "included_proposals": {}}
    selectors = {"grid": ("ring-grid", "ring-grid-skeleton"),
                 "grid-gap-retention": ("ring-grid-feeder-retention",),
                 "compact": ("pure-ring-grid", "pure-ring-grid-skeleton"),
                 "orthogonal": ("pure-ring-grid-orthogonal",), "diagonal": ("pure-ring-grid-diagonal",)}
    known = {item["candidate_id"] for item in networks.values()}
    for name, keys in selectors.items():
        for key in keys:
            net = results.get(key, {}).get("network")
            if net and net["candidate_id"] not in known:
                trials["included_proposals"][name] = key
                networks[name] = net
                known.add(net["candidate_id"])
                break
    if "grid" not in networks:
        raise ValueError("The ring-and-grid comparison requires a connected cross-city grid trial")
    paired = "grid-gap-retention" if "grid-gap-retention" in networks else "grid"
    trials["paired_ring_layout"] = paired
    networks["one-ring-grid"] = _single_ring(networks[paired])
    for name, network in networks.items():
        identity = holistic_network._identity(dict(network))
        if identity["evaluation_id"] != network["evaluation_id"]:
            raise ValueError(f"Network evaluation changed after preparing {name}")
    return networks, trials, evidence


def evaluate(baseline_path):
    from . import ring_corridors, ring_grid_spines

    baseline_record = central_access.read(baseline_path)
    current = baseline_record["network"]
    if current["candidate_id"] != REFERENCE_ID:
        raise ValueError(f"Use the published reference at {REFERENCE_COMMIT}")
    graph = central_access.walking_graph()
    context = central_access.original_cases()[3]
    networks, trials, ring_evidence = layouts(current, graph, context, ring_corridors, ring_grid_spines)
    record = assess(networks, graph, baseline_record=baseline_record, trials=trials, ring_evidence=ring_evidence)
    record["display_trial"] = choose_display(record)
    inputs = [Path(__file__), Path(ring_corridors.__file__), Path(ring_grid_spines.__file__),
              CITY / "ring_grid_journeys.py", residential_planning.POLICY]
    sources = baseline_record["sources"] | current["source_sha256"]
    sources.update({path.relative_to(central_access.ROOT).as_posix(): central_access.digest(path) for path in inputs})
    record["sources"] = sources
    record["reference_packet_sha256"] = central_access.digest(baseline_path)
    record["comparison_id"] = sha256(central_access.encode(record)).hexdigest()
    return record, networks, context


def choose_display(record):
    """Map the two-ring design closest to the distance and access of the current layout."""
    geometry = record["geometry"]
    housing = record["same_train_km_housing"]["variants"]
    reference = geometry["current"]["route_km"]
    trials = [key for key, row in geometry.items() if {"M09", "M15"} <= row["rings"].keys()]
    if not trials:
        raise ValueError("No tested design includes both complete rings")
    at_budget = [key for key in trials if geometry[key]["route_km"] <= reference + .01]
    near_budget = [key for key in at_budget if geometry[key]["route_km"] >= .9 * reference]
    return min(near_budget or at_budget or trials, key=lambda key: (geometry[key]["route_km"] > reference + .01,
               -housing[key]["journeys"]["reachable_with_at_most_share_of_all_pct"]["2"],
               abs(geometry[key]["route_km"] - reference), key))


def _fmt(value, places=2):
    return "—" if value is None else f"{value:,.{places}f}"


def report(record):
    geometry = record["geometry"]
    metro = record["same_train_km_metropolitan"]
    housing = record["same_train_km_housing"]
    costs = record["six_minute_delivery_and_cost"]
    walks = record["coverage"]["worldpop-2026"]["metropolitan"]["cases"]
    picked = record["display_trial"]
    wide = "wide-angle inter-district"
    b, n = (metro["variants"][label]["cohorts"][wide] for label in ("current", picked))
    old, new = (housing["variants"][label]["journeys"]["reachable_with_at_most_share_of_all_pct"]["2"]
                for label in ("current", picked))
    train_km = metro["variants"]["current"]["service"]["running_train_km_day"]
    out = ["# Baghdad ring-and-grid network comparison", "",
           "![Published and ring-and-grid routes drawn at the same scale](maps/baghdad-ring-grid.png)", "",
           f"The displayed two-ring plan has {geometry[picked]['route_km']:.2f} route-km. At the same daily running train-km, "
           f"it serves **{n['served_share_pct']:.2f}%** of the modelled wide-angle outer-district trips, compared with "
           f"**{b['served_share_pct']:.2f}%** on the published map. Housing-to-centre reach within two transfers changes "
           f"from **{old:.2f}% to {new:.2f}%**.", "",
           "The new map is a comparison against the published network. Both rings follow mapped corridors and interchanges. "
           "Their road and river constraints produce irregular nested loops with different geometric centres. "
           "The comparison includes straight or nearly straight cross-city lines and branches needed to keep the railway connected.", "",
           f"Published reference commit `{record['reference_revision']}`. "
           "[Current metropolitan map](maps/baghdad-network.png) · [Ring-grid GIS](maps/baghdad-ring-grid.geojson) · "
           "[Model inputs and results](ring-grid.json)", "",
           "## Route geometry and daily operating effort", "",
           f"Every passenger assignment uses the same **{train_km:,.0f} daily running train-km**, the same 18-hour operating day "
           "and street walks of up to 1.2 km at each end. Longer networks receive longer average intervals in this comparison. "
           "The separate delivery table prices a uniform six-minute interval for all layouts.", "",
           "| Layout | Routes / closed rings | Route km | Walk ≤1.2 km | Directional interval | Close parallel pair-km |",
           "|---|---:|---:|---:|---:|---:|"]
    for key, option in geometry.items():
        headway = metro["variants"][key]["service"]["directional_headway_s"] / 60
        out.append(f"| {NAMES[key]} | {option['lines']} / {len(option['rings'])} | {option['route_km']:.2f} | "
                   f"{walks[key]['1200']['share_pct']:.2f}% | {headway:.2f} min | {option['parallel_pair_km']:.2f} |")
    out.extend(["", "Parallel lengths count long runs for each line pair. The figure uses the displayed two-ring layout from the route-length-limited options, "
                "preferring candidates within 10% of the current route length before comparing housing-to-centre reach within two changes. "
                f"The one-ring control uses the other alignments from “{NAMES[record['trial_metadata']['paired_ring_layout']]}” and omits the inner ring. "
                "The overlay isolates the cost and performance of adding both rings to the current layout.", "",
                "| Ring in displayed plan | Route km | Station sites | Shared interchanges |",
                "|---|---:|---:|---:|"])
    for code, ring in geometry[picked]["rings"].items():
        out.append(f"| {code} | {ring['route_km']:.2f} | {ring['stations']} | {ring['interchanges']} |")
    if any(geometry[key]["new_through_axes"] for key in ("grid", picked)):
        out.extend(["", "The criss-cross paths include new through alignments that connect at a shared interchange. "
                    "Their mapped line lengths and transfer records are in the GIS and machine results."])
    flagged = record["ring_evidence"]["outer_gis_context"]["crossings_above_provisional_span_limit"]
    if flagged:
        out.extend(["", f"The restored outer ring includes {flagged} mapped wet reaches wider than the 550 m screening bound. "
                    "Its crossing design and any premium over the standard civil allowance remain open. The inner ring follows "
                    "mapped road corridors and named bridge reaches, with rail structures and clearances still to be designed."])
    out.extend(["", "## Trips between districts and to the centre", "",
                "The metropolitan model weights trips between populated 2 km tiles with distance decay. "
                "The wide-angle sample requires both ends outside the central study box, in different 8 km grid districts, "
                "with at least 45 degrees of angular separation around the central box. P90 compares the same wide-angle trips "
                "served by both the candidate and the published map. The transfer count for this sample describes the assigned route. "
                "The separate housing-to-centre model enforces a maximum of two transfers to six named destinations.", "",
                "| Layout | All metropolitan trips served | Wide-angle served | Wide-angle assigned ≤2 changes | Same-trip wide-angle P90, current → trial | Housing trips within 2 changes | Peak load per departure index |",
                "|---|---:|---:|---:|---:|---:|---:|"])
    for key, option in metro["variants"].items():
        cohort, pair = option["cohorts"][wide], option["paired_cohorts"][wide]
        reach = housing["variants"][key]["journeys"]["reachable_with_at_most_share_of_all_pct"]["2"]
        out.append(f"| {NAMES[key]} | {_fmt(option['journeys']['served_share_pct'])}% | {_fmt(cohort['served_share_pct'])}% | "
                   f"{_fmt(cohort['at_most_two_transfers_share_of_all_pct'])}% | "
                   f"{_fmt(pair['reference_elapsed_p90_min'],1)} → {_fmt(pair['candidate_elapsed_p90_min'],1)} min | "
                   f"{reach:.2f}% | {option['concentration']['peak_load_per_departure_index']:.3f} |")
    out.extend(["", "Peak load is a comparison of pressure on the busiest direction of a track segment per departure under the same synthetic demand. "
                "Timetables, depot work, passenger counts, signalling and crowding require further evidence. "
                "The [machine record](ring-grid.json) also includes centre-to-outer, local and all inter-district cohorts.", "",
                "## Installed and whole-life planning allowances", "",
                "Costs use identical 2026 US dollar rates and the same six-minute, 18-hour service specification. "
                "Track-km count both tracks. Special rail crossings, land requirements, accessible stations, turnouts and installation remain at planning maturity.", "",
                "| Layout | Track-km | Paid casting, haul and erection hours | Trainsets with spares | Installed, US$bn | Annual operation, US$bn | 30-year present cost, US$bn |",
                "|---|---:|---:|---:|---:|---:|---:|"])
    for key, option in costs.items():
        row = option["cases"]["base"]
        out.append(f"| {NAMES[key]} | {option['track_km']:.2f} | {option['paid_casting_haul_and_erection_hours']:,.0f} | "
                   f"{option['fleet_including_spares']} | {row['installed_planning_usd_m']/1000:.2f} | "
                   f"{row['annual_operations_total_usd_m']/1000:.2f} | {row['whole_life_present_usd_m']/1000:.2f} |")
    out.extend(["", "Run `tools/automation/osr-python -m cities.Baghdad.ring_grid_comparison --check` to verify this comparison.",
                "Supply `--baseline` with the reference packet from the pinned commit for historical reproduction.", "",
                f"Comparison `{record['comparison_id']}`.", ""])
    return "\n".join(out)


def draw(record, networks, context):
    from io import BytesIO
    from math import cos, radians

    import matplotlib
    matplotlib.use("Agg")
    from matplotlib import pyplot as plt
    from matplotlib.collections import LineCollection, PatchCollection
    from matplotlib.lines import Line2D
    from matplotlib.patches import Polygon

    from . import central_service_map

    picked = record["display_trial"]
    pair = [networks[key] for key in ("current", picked)]
    paper, ink = "#f7f5ef", "#16383e"
    fig, axes = plt.subplots(1, 2, figsize=(14.4, 8.7), sharex=True, sharey=True,
                             gridspec_kw={"left": .045, "right": .975, "top": .84, "bottom": .155, "wspace": .07})
    fig.patch.set_facecolor(paper)
    water, rivers, roads = central_service_map.source_geometry(context)
    color = {"M09": "#008179", "M15": "#a64e20"}
    points = np.concatenate([line["geometry"] for case in pair for line in case["lines"].values()])
    start, finish = points.min(axis=0) - .014, points.max(axis=0) + .014
    for ax, name, case in zip(axes, ("current", picked), pair, strict=True):
        ax.set_facecolor("#f4efe6")
        ax.add_collection(PatchCollection([Polygon(path, closed=True) for path in water], facecolor="#b9dce4",
                                           edgecolor="none", zorder=1))
        ax.add_collection(LineCollection(rivers, colors="#79b4be", linewidths=1.15, zorder=1.1))
        ax.add_collection(LineCollection(roads, colors="#b9ac9b", linewidths=.32, alpha=.44, zorder=2))
        for code, line in case["lines"].items():
            if code in color:
                continue
            fresh = code not in networks["current"]["lines"]
            style = "#566cb8" if fresh else "#718181"
            ax.plot(*np.asarray(line["geometry"]).T, color=style, linewidth=1.8 if fresh else .99,
                    alpha=.92 if fresh else .75, zorder=3)
        for code, marker_color in color.items():
            if code not in case["lines"]:
                continue
            line = case["lines"][code]
            xy = np.asarray(line["geometry"])
            ax.plot(*xy.T, color=paper, linewidth=4.2, zorder=4)
            ax.plot(*xy.T, color=marker_color, linewidth=2.65, zorder=4.25)
            sites = np.asarray([case["stations"][stop]["coordinates"] for stop in line["station_ids"]
                                if len(case["stations"][stop]["lines"]) > 1])
            if len(sites):
                ax.scatter(*sites.T, s=14, color=paper, edgecolors=marker_color, linewidths=.8, zorder=4.5)
        for key, name_text in (("Tahrir", "Tahrir Square"), ("Mansour", "Al Mansour")):
            if key in case["stations"]:
                ax.annotate(name_text, case["stations"][key]["coordinates"], xytext=(5, 5), textcoords="offset points",
                            fontsize=8.4, color=ink, weight="bold", zorder=6,
                            bbox={"boxstyle": "round,pad=.2", "fc": paper, "ec": "none", "alpha": .95})
        ax.set(xlim=(start[0], finish[0]), ylim=(start[1], finish[1]), xticks=[], yticks=[], aspect=1 / cos(radians(33.3)))
        for spine in ax.spines.values():
            spine.set_color("#d6cbb9")
        ax.set_title(f"{NAMES[name]}  ·  {_route_km(case):.0f} route-km", fontsize=13, weight="bold", color=ink, loc="left", pad=9)
    fig.text(.045, .941, "Baghdad  |  Rings and cross-city routes", fontsize=26, color=ink, weight="bold")
    fig.text(.046, .899, "The published layout and a modelled two-ring option at the same scale", fontsize=12, color="#40595a")
    keys = [Line2D([], [], lw=3, color=color["M09"], label="Outer corridor"),
            Line2D([], [], lw=3, color=color["M15"], label="Inner ring"),
            Line2D([], [], lw=2, color="#566cb8", label="New through lines"),
            Line2D([], [], lw=1.8, color="#718181", label="Retained railway"),
            Line2D([], [], marker="o", ls="None", markerfacecolor=paper, markeredgecolor=ink, label="Ring interchange")]
    fig.legend(handles=keys, loc="lower center", bbox_to_anchor=(.5, .076), ncol=5, frameon=False, fontsize=10, labelcolor=ink)
    fig.text(.045, .038, "Planning alignments  ·  Basemap © OpenStreetMap contributors", fontsize=9, color="#40595a")
    output = BytesIO()
    fig.savefig(output, format="png", dpi=150, facecolor=paper)
    plt.close(fig)
    return output.getvalue()


def outputs(record, networks, context):
    picked = record["display_trial"]
    gis = holistic_network.geojson(networks[picked]) | {"comparison_id": record["comparison_id"], "trial": picked}
    return {REPORT: report(record).encode(), RECORD: central_access.encode(record),
            FIGURE: draw(record, networks, context), GEOJSON: central_access.encode(gis)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--publish", action="store_true")
    action.add_argument("--check", action="store_true")
    action.add_argument("--output", type=Path)
    parser.add_argument("--baseline", type=Path, default=BASELINE)
    args = parser.parse_args()
    out = args.output or CITY
    with disk_reservation(central_access.ROOT, out, "Baghdad ring and grid comparison", 96 << 20):
        record, networks, context = evaluate(args.baseline)
        for path, content in outputs(record, networks, context).items():
            target = out / path.relative_to(CITY)
            if args.check:
                actual = target.read_bytes()
                equal = central_access.map_pixels_match(actual, content) if path == FIGURE else actual == content
                if not equal:
                    raise SystemExit(f"Run the ring-and-grid generator again. {target.name} differs.")
            else:
                from engineering.station_rail.publication import write
                write(target, content)
        print(record["comparison_id"])


if __name__ == "__main__":
    main()
