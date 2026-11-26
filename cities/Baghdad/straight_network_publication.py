"""Publish the active Baghdad network, construction plan and curved-girder register."""

import argparse
import csv
import gzip
from io import BytesIO, StringIO
from pathlib import Path
import re

import numpy as np

from engineering.performance import disk_reservation
from engineering.station_rail.publication import write

from . import central_access, central_service_map, holistic_map, holistic_network, straight_network_study as study
from .engineering.mechanical.civil import alignment_beams


def _name(record, code):
    return study.NAMES.get(code) or record["layouts"][code]["name"]


def _sites(network, ids):
    return ", ".join(f"{network['stations'][stop]['name']} ({stop})" for stop in ids)


def report(record):
    chosen = record["display_trial"]
    network = record["network"]
    layout = record["layouts"][chosen]
    summary = record["summary"][chosen]
    common = record["ring_service"]["variants"]["current"]["service"]["running_train_km_day"]
    lines = ["# Baghdad metropolitan railway · Rings and Tigris through services", "",
             f"**{_name(record, chosen)}** is the current proposal. The {summary['route_km']:.2f} km passenger network "
             f"serves {summary['stations']} station sites on {summary['lines']} connected lines. The WorldPop street "
             f"model puts **{summary['metro_walk_1300_pct']:.2f}%** of the study population within 1.3 km of a "
             f"station. **{summary['housing_two_changes_pct']:.2f}%** of weighted housing-to-centre trips can be "
             "completed with up to two changes under the matched-service comparison.", "",
             "![Baghdad metropolitan network and highlighted cross-Tigris through services](maps/baghdad-straight-through-network.png)", "",
             "[Tigris crossings and ring interchanges](maps/baghdad-through-interchanges.png) · "
             "[Side-by-side comparison](maps/baghdad-straight-through-comparison.png) · [Proposal](PROPOSAL.md) · "
             "[Delivery and planning figures](STRAIGHT-THROUGH-DELIVERY.md) · "
             "[Routes, stations and transfers in GIS](maps/baghdad-straight-through-network.geojson) · "
             "[Machine results](straight-through-network.json)", "",
             "## How the layout works", "",
             f"The {summary['rings']['M15']['route_km']:.2f} km central ring (M15) distributes trips around the central districts. "
             f"The {summary['rings']['M09']['route_km']:.2f} km outer ring (M09) connects the outer corridors. "
             "The through services approach both rings from outside, cross the Tigris at mapped bridge approaches and "
             "share station sites with the rings. C1 keeps the Airport in the same passenger network.", "",
             "| Through service | End-to-end km | Length / terminal chord | Tigris approach | Inner ring shared stations | Outer ring shared stations |",
             "|---|---:|---:|---|---|---|"]
    for row in record["approved_through"][chosen]:
        bridges = " → ".join(f"{lon:.5f}° E, {lat:.5f}° N" for lon, lat in row["mapped_bridge_approaches"])
        calls = row["ring_interchanges"]
        lines.append(f"| {row['id']} | {row['route_km']:.2f} | {row['detour_ratio']:.4f} | {bridges} | "
                     f"{_sites(network, calls['M15'])} | {_sites(network, calls['M09'])} |")
    lines += ["", "The GIS checks bridge orientation, both river banks and actual shared station calls. Existing bridge "
              "approaches locate the railway corridors. Each new rail crossing needs its own structure and approvals.", "",
              "### Deterministic selection", "",
              "1. Retain both ring alignments and protect the Airport terminals. Use mapped roads, water and pedestrian paths.",
              "2. Search mapped bridge approaches, bearings and terminal locations. Check that the line enters and leaves "
              "each ring, uses an interchange on each, and has two terminals beyond the outer ring. Reject lines over 1.10 times the terminal chord.",
              "3. Compare retained, replacement and added corridors. Test parallel cuts and turnbacks against the same "
              "housing sample, station access and connected passenger graph. Keep a distinct transfer connection where platforms are separate.",
              "4. Apply the prior access tolerances and keep access to all previously reached central destinations. "
              "Among new layouts that pass, reduce parallel pair-km first, then line count, then favour housing and outer-district reach.",
              "5. Recalculate fleet, supply, civil quantities, routes and costs using the selected geometry. Run independent "
              "beam and construction-stage checks before procuring works.", "",
              "| Trial | Route-km | Lines / sites | Parallel pair-km | WorldPop 1.2 / 1.3 km | GHSL 1.3 km | Housing trips ≤2 changes | Outer trips served |",
              "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for code, row in record["summary"].items():
        ghsl = record["coverage"]["ghsl-2025"][code]["metro"]["1300"]["pct"]
        name = f"**{_name(record, code)}**" if code == chosen else _name(record, code)
        lines.append(f"| {name} | {row['route_km']:.2f} | {row['lines']} / {row['stations']} | {row['parallel_pair_km']:.2f} | "
                     f"{row['metro_walk_1200_pct']:.2f}% / {row['metro_walk_1300_pct']:.2f}% | {ghsl:.2f}% | "
                     f"{row['housing_two_changes_pct']:.2f}% | {row['wide_trips_pct']:.2f}% |")
    lines += ["", f"All passenger variants use **{common:,.0f} train-km/day**, common synthetic demand and up to 1.3 km "
              "walking at each end. Coverage estimates use WorldPop 2026 and GHSL 2025 population grids and mapped "
              "street connections. These model outputs describe geographic access and relative service. They do not supply "
              "observed origin–destination demand. Six-minute capital and operating allowances use a separate fixed-service offer.", "",
              "### Where the changes stop", ""]
    eligible = ", ".join(_name(record, key) for key in record["selection"]["both_terminals_outside_outer_ring"])
    lines += [f"Both terminals of each through service lie beyond the outer ring only in **{eligible}**. "
              "The retained and mixed comparisons include lines that end at a ring station.", ""]
    for action in layout["actions"]:
        route = action["line_id"]
        if action["action"] == "add_through":
            lines.append(f"- Add **{route}**, {action['route_km']:.2f} km.")
        else:
            lines.append(f"- Revise **{route}**, removing {action.get('removed_route_km', 0):.2f} route-km.")
    exceptions = layout["hierarchy"]["core_exceptions"]
    if exceptions:
        lines += ["", f"**{len(exceptions)} retained corridors** also enter the inner ring. They remain in the map to preserve "
                  "the passenger paths shown in the model. Their route-by-route dispositions are below.", "",
                  "| Retained service | Disposition |", "|---|---|"]
        lines.extend(f"| {row['line_id']} | {row['reason']} |" for row in exceptions)
    if record["held_trials"]:
        lines += ["", "Other tested layouts were held for the following reasons.", ""]
        lines.extend(f"- **{code}** · {reason.rstrip('.')}." for code, reason in record["held_trials"].items())
    lines += ["", "## Central destinations and remaining coverage gaps", "",
              "| Destination | Walk to M15 | Walk to a direct M15 connection |", "|---|---:|---:|"]
    access = record["coverage"]["worldpop-2026"][chosen]
    direct = access["destinations_on_foot_to_ring"]
    via = access["destinations_with_at_most_one_change_from_ring"]
    def walk(value):
        return f"{value:,.0f} m" if value is not None else "Open"
    for key, row in direct.items():
        lines.append(f"| {row['name']} | {walk(row['metres'])} | {walk(via[key]['metres'])} |")
    lines += ["", "| Central sector | Population with a ≤1.3 km walk to any station |", "|---|---:|"]
    for label, row in access["sectors"].items():
        lines.append(f"| {label} | {row['network']['1300']['pct']:.2f}% |")
    lines += ["", "## Development path", "",
              "| Stage | Work and accountable lead | Release evidence |", "|---|---|---|",
              "| Corridor | Baghdad planning and survey teams verify both river banks, land, streets, interchange entrances and terminal turnbacks | Controlled horizontal and vertical alignment plus route observations |",
              "| Structures | Civil and geotechnical teams use GIS screening, survey, hydraulic and borehole inputs to develop the river spans, curve radii, bearings, piers and grades | Checked geometry, design loads and worksite costs, including station and turnout interfaces |",
              "| Service | Operations, signalling and power teams test timetables, electric duty, station transfer loads and safe stopping | Peak and degraded-service simulation and scheme-specific limitations |",
              "| Work packages | Iraqi precasters, transporters and contractors price yard and form layouts, launch equipment, off-deck lifts and bridge access | Matched quantities, working method, crew shifts and mobilisation quotes |",
              "| First articles | Civil and rolling-stock teams build and inspect representative assemblies and temporary load interfaces | Test results and an independently reviewed procurement package |",
              "| Delivery and finance | Authority and funding team price common scope and agree the stage order, demand cases and financing | Cost and operating plan linked to approved design inputs |", "",
              "For new city studies, the shared OpenSourceRail workflow uses the same directness, river and shared-ring transfer checks "
              "where local GIS supports them. It keeps a source-linked earlier corridor as a bounded fallback when the evidence or comparison "
              "cannot support a new layout. Existing city dossiers retain their published inputs.", "",
              "Reproduce this record with `OPENBLAS_NUM_THREADS=1 ./osr design railway baghdad-network --check`.", "",
              f"Network candidate `{network['candidate_id']}` · publication `{record['publication_id']}`.", ""]
    return "\n".join(lines)


def delivery_report(record):
    civil, system, beam = (record[key] for key in ("civil", "cost", "beam_schedule"))
    q, programme, labour = (civil[key] for key in ("quantities", "programme", "workforce"))
    service, power = system["service"], system["power"]
    history = record["previous_cost"]
    yard = civil["assumptions"]["source_yard_layout"]
    lines = ["# Baghdad metropolitan railway · Quantities, work programme and costs", "",
             f"The active network has **{q['service_route_km']:,.2f} service-route km**, "
             f"**{q['unique_guideway_km']:,.2f} km of distinct guideway** and **{q['double_track_km']:,.2f} running-track km**. "
             f"The design allows {q['station_sites']} station sites, {q['station_line_platform_packages']} line platform packages "
             f"and {q['transfer_sites']} shared passenger stations. "
             f"Exactly coincident running accounts for {q['service_overlap_km']:.3f} service-route km.", "",
             "[Network study](STRAIGHT-THROUGH-NETWORK.md) · "
             "[Curved beam families and route work orders](engineering/mechanical/civil/CURVED-BEAM-PROGRAMME.md)", "",
             "## Compared quantities and costs", "",
             "| Scope | Earlier central ring | Active proposal |", "|---|---:|---:|",
             f"| Running track km | {history['track_km']:,.2f} | {q['double_track_km']:,.2f} |",
             f"| Standard-stock casting, haul and erection paid hours | {history['paid_casting_haul_and_erection_hours']:,.0f} | {labour['paid_deck_and_casting_hours']:,.0f} |",
             f"| Standard-deck handover day from mobilisation | {history['standard_deck_handover_day']:,.0f} | {programme['last_standard_deck_day']:,.0f} |",
             f"| Installed planning allowance, base US$bn | {history['cases']['base']['installed_planning_usd_m']/1000:.2f} | {system['cost_cases']['base']['installed_planning_usd_m']/1000:.2f} |", "",
             "| 2026 real prices | Low | Base | High |", "|---|---:|---:|---:|"]
    for field, title in (("direct_total_usd_m", "Direct scopes, US$bn"), ("installed_planning_usd_m", "Installed planning allowance, US$bn"),
                         ("annual_operations_total_usd_m", "Annual operation, US$bn"), ("whole_life_present_usd_m", "30-year present cost, US$bn")):
        values = " | ".join(f"{system['cost_cases'][case][field]/1000:.3f}" for case in ("low", "base", "high"))
        lines.append(f"| {title} | {values} |")
    lines += ["", "The common price basis adds design, tests and project allowance once. The curved and short-beam form premium "
              "is added once to both compared erection methods over equivalent stock. Bridge, station transitions, turnout structures, "
              "ground-specific changes and other held works require prices. The tables are planning cases in constant 2026 dollars.", "",
              "| Base direct scope | US$m |", "|---|---:|"]
    lines.extend(f"| {name.replace('_', ' ').capitalize()} | {value:,.2f} |"
                 for name, value in system["cost_cases"]["base"]["direct_scope_usd_m"].items())
    lines += ["", "## Service, electricity and workers", "",
              f"The fixed {service['directional_headway_s']/60:g}-minute offer over {service['operating_hours_day']:g} hours/day "
              f"uses {service['active_trainsets']:,} running trainsets and {service['reserve_trainsets']:,} reserve, "
              f"or {service['cars']:,} cars across {service['depot_allowances']} depot allowances. "
              f"The model produces {service['running_train_km_year']/1e6:.2f} million train-km/year, "
              f"{power['annual_grid_gwh']:,.1f} GWh/year and {power['nominal_supply_sites']} nominal grid supply sites. "
              f"Each line offers {service['nominal_places_per_hour_direction']:,} nominal places per hour in each direction.", "",
              f"The standard-stock comparison uses {programme['active_launcher_pairs']} active paired launcher crews, "
              f"{programme['active_road_day_teams']} road teams and {programme['concurrent_yard_sites']} concurrent yards. "
              f"Each nominal yard uses {yard['area_ha']:.2f} ha and {yard['mould_count']} mould positions. "
              f"There are {programme['concurrent_moulds']} concurrent moulds on "
              f"{programme['concurrent_yard_area_ha']:.1f} ha. Rail-fed jobs reserve a yard and a mobile front at each end. "
              "Loops, shared sections and sites without a proven continuous launch path retain road works in the stock comparison.", "",
              "| Standard recurring deck measure | Rail-fed planning case | Matched road benchmark |",
              "|---|---:|---:|",
              f"| Public-road loaded girder vehicle trips | {q['loaded_beam_trips']:,} | {q['road_day_loaded_beam_trips']:,} |",
              f"| Erection lane-hours | {q['erection_lane_hours']:,.0f} | {q['road_day_erection_lane_hours']:,.0f} |",
              f"| Direct civil and track scope, including special-beam increment (US$m) | {civil['cost_cases']['base']['direct_usd_m']:,.1f} | {civil['cost_cases']['base']['matched_road_direct_usd_m']:,.1f} |", "",
              "Foundation, column, road fallback and station work still require ground access. The reproduced beam work orders "
              "itemise the shifts for quantified straight and special pieces. Their paid hours overlap the standard-stock work "
              "envelope. The published programme leaves the full handover and opening dates open.", "",
              "| Stock comparison phase / role | Shift | Paid person-hours |", "|---|---|---:|"]
    for row in labour["crew_shifts"]:
        lines.append(f"| {row['phase']} / {row['role']} | {row['shift']} | {row['paid_hours']:,.0f} |")
    lines += ["", "## End-to-end routes", "",
              "| Service | Terminals | Route-km | Owned guideway km | Platform calls | Active sets | Recurring civil days |",
              "|---|---|---:|---:|---:|---:|---:|"]
    orders = {row["section"]: row for row in civil["orders"]}
    net = record["network"]
    for row in q["route_register"]:
        code = row["line"]
        line = net["lines"][code]
        termini = "Closed ring" if line["loop"] else _sites(net, (line["station_ids"][0], line["station_ids"][-1]))
        days = orders.get(code, {}).get("calendar_days")
        elapsed = f"{days:,.0f}" if days is not None else "Held"
        lines.append(f"| {code} | {termini} | {row['service_route_km']:.2f} | {row['unique_guideway_km']:.2f} | "
                     f"{row['station_line_platform_packages']} | {service['rolling_stock_lines'][code]['active_trainsets']} | {elapsed} |")
    lines += ["", f"The curved-girder inventory identifies {beam['totals']['held_route_length_m']/1000:.2f} "
              "service-route km in geometry or interface holds. It carries representative steel, strand, concrete and "
              "labour quantities for the assessed stock. Bulk purchase and final installation quantities depend on resolving those holds.", "",
              f"Construction evaluation `{civil['evaluation_id']}` · beam evaluation `{beam['evaluation_id']}`.", ""]
    return "\n".join(lines)


def beam_report(beam):
    t, p, s = (beam[key] for key in ("totals", "assumptions", "stock_section"))
    lines = ["# Baghdad · Curved and straight girder fabrication programme", "",
             "This chainage register divides the active double-track proposal into recurring 20 m straight U-girders, straight "
             "closures, curved inside/outside pairs and special interfaces. Each curve pair follows one circular fillet with "
             "a common centre, an inside radius and an outside radius. Where indicated, a short stock piece includes tangent leads. "
             "Part, bearing and mould quantities use the dimensions of each individual track piece.", "",
             "![Dimensioned inside and outside curved stock and U-girder section](curved-beam-families.svg)", "",
             "[Editable DXF plan and section](curved-beam-families.dxf) · [Filterable bay register](curved-beam-register.csv) · "
             "[Full work orders and source records](curved-beam-register.json.gz) · "
             "[Route and delivery study](../../../STRAIGHT-THROUGH-DELIVERY.md)", "",
             f"The reference paired bay is **{p['stock_bay_m']:g} m** with **{p['track_pitch_m']:g} m track pitch**. "
             f"The mapped fit uses **{p['minimum_inner_track_radius_m']:g} m** as its minimum inside radius, "
             f"a preferred route radius of **{p['preferred_route_radius_m']:g} m**, "
             f"and up to **{p['maximum_beam_plan_sagitta_m']*1000:g} mm** sweep from a track-piece chord to its arc. "
             "The two track pieces have different lengths and mould settings. The dimensions are the concept set-out for a "
             "family of variable radii.", "",
             "| Family | Paired bays / hold intervals | Pieces | Inside / outside | Route km | Concrete m³ | Bare mass t | Bearings |",
             "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for family, row in beam["by_family"].items():
        lines.append(f"| {family.replace('_', ' ')} | {row['bays_or_hold_intervals']:,} | {row['girders']:,} | "
                     f"{row['inside_girders']:,} / {row['outside_girders']:,} | {row['route_length_m']/1000:.2f} | "
                     f"{row['girder_concrete_m3']:,.0f} | {row['girder_bare_mass_t']:,.0f} | {row['bearings']:,} |")
    lines += ["", f"The quantified stock carries **{t['rebar_planning_kg']/1000:,.0f} t of bar allowance** and "
              f"**{t['strand_planning_kg']/1000:,.0f} t of strand allowance**. "
              f"Stock mould time is **{t['mould_occupation_h']:,.0f} mould-hours**, including "
              f"**{t['mould_changeover_h']:,.0f} form changeover hours**. "
              f"The register totals **{t['yard_paid_crew_h']:,.0f} paid yard hours** and "
              f"**{t['launcher_paid_crew_h']:,.0f} paid launcher crew hours** under the two-front concept work orders. "
              "The priced standard-stock programme and the indicative geometry work orders overlap. "
              "The ring and route service lengths retain mapped chainage. Concept fillets shorten individual "
              "beam runs while the source chainage intervals still cover every metre of each mapped route.",
              "", "## Fabrication and installation sequence", "",
              "| Operation | Work instruction basis |", "|---|---|",
              "| Set out the mould | Use piece chainage, inside/outside arc, chord, sweep and tangent leads. Set internal forms, end blocks, bearing seats and anchor positions. |",
              "| Assemble steel and stressing | Confirm bending, torsion, transfer and handling loads. Check curved tendon ducts, bar cages, cover, end-zone steel and stage stressing against shop design. |",
              f"| Cast, cure, inspect | Reserve {p['mould_occupation_and_trial_cure_h']:g} h in the planning mould cycle. Record release strength, dimensional survey and lift-point acceptance. |",
              "| Load and transport | Load each piece once onto a checked cradle. Verify transport wheel loads, curve clearances, route availability, starter spans and temporary deck continuity. |",
              "| Lift, set and release | Match lifting points, bearings, launcher positions and curve offsets. Check wet works, track extension and landing release before advancing. |", "",
              "| Family | Form changes | Extra mould h | Loaded trips | Flatbed h | Assembly and track h | Base special-stock increment US$m |",
              "|---|---:|---:|---:|---:|---:|---:|"]
    for family, row in beam["by_family"].items():
        if row["girders"]:
            lines.append(f"| {family.replace('_', ' ')} | {row['mould_changeovers']:,} | {row['mould_changeover_h']:,.1f} | "
                         f"{row['candidate_loaded_trips']:,} | {row['flatbed_feed_equipment_h']:,.1f} | {row['assembly_operating_h']:,.1f} | "
                         f"{row['incremental_allowance_usd']['base']/1e6:.2f} |")
    lines += ["", "## Recurring piece orders by route", "",
              "| Route | Straight 20 m | Straight closure | Curved | Short curved | Held mapped km |",
              "|---|---:|---:|---:|---:|---:|"]
    for code, route in beam["routes"].items():
        counts = dict.fromkeys(("straight_20m", "short_closure", "curved_ugirder", "short_curved_ugirder"), 0)
        held_km = 0.
        for bay in route["bays"]:
            if bay["family"] in counts:
                counts[bay["family"]] += len(bay["track_pieces"])
            else:
                held_km += (bay["reference_end_m"] - bay["reference_start_m"]) / 1000
        lines.append(f"| {code} | {' | '.join(f'{value:,}' for value in counts.values())} | {held_km:.2f} |")
    lines += ["", "## Yard and front work orders", "",
              "A / B denote the two nominal route ends. For a loop they are accounting halves of the numbered chainage. "
              "Use the priced route work plan for yard pooling, road fallback and phased resource availability.", "",
              "| Route | Girder pieces A / B | One-shift casting days A / B | Booked 8h launcher shifts A / B | Continuous front-day equivalent A / B |",
              "|---|---:|---:|---:|---:|"]
    for row in beam["route_schedule"]:
        pairs = [" / ".join(f"{n:,.1f}" if isinstance(n, float) else f"{n:,}" for n in row[key]) for key in (
            "yard_units_by_end", "yard_one_shift_days_by_end", "launcher_booked_8h_shifts_by_end", "launcher_continuous_day_equivalents_by_end")]
        lines.append(f"| {row['route_id']} | {' | '.join(pairs)} |")
    lines += ["", "## Held interfaces", "", *(f"- {item}" for item in beam["holds"]), "",
              f"Physical candidate `{beam['candidate_id']}` · beam evaluation `{beam['evaluation_id']}`.", ""]
    return "\n".join(lines)


def beam_csv(beam):
    fields = ("route", "bay", "family", "reference_start_m", "reference_end_m", "track_piece",
              "arc_length_m", "radius_m", "turn_direction", "sweep_deg", "tangent_lead_m", "tangent_trail_m",
              "chord_m", "sagitta_m", "hold_sources")
    out = StringIO(newline="")
    writer = csv.DictWriter(out, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    for code, route in beam["routes"].items():
        for row in route["bays"]:
            for side, piece in row.get("track_pieces", {"": {}}).items():
                writer.writerow({key: piece.get(key, row.get(key, "")) for key in fields} |
                                {"route": code, "bay": row["id"], "track_piece": side,
                                 "hold_sources": ", ".join(row["hold_sources"])})
    return out.getvalue().encode()


def _style(record):
    colors = {"M09": "#00837a", "M15": "#b54c2d", "C1": "#59728b"}
    selected = record["approved_through"][record["display_trial"]]
    colors.update((row["id"], color) for row, color in zip(selected, ("#1d58a6", "#713fa2"), strict=True))
    return colors


def draw(record, networks, context, *, compare=False, detail=False):
    import matplotlib
    matplotlib.use("Agg")
    from matplotlib import pyplot as plt
    from matplotlib.collections import LineCollection, PatchCollection
    from matplotlib.lines import Line2D
    from matplotlib.patches import Polygon
    from matplotlib.ticker import NullLocator

    code = record["display_trial"]
    previous, active = (networks[key] for key in ("central", code))
    proofs = record["approved_through"][code]
    calls = {site for row in proofs for stops in row["ring_interchanges"].values() for site in stops}
    names = _style(record)
    land, paper, ink = "#f0ebe1", "#faf7f1", "#163642"
    water, rivers, roads = central_service_map.source_geometry(context)
    focus = names.keys() - {"C1"}
    extent = np.concatenate([line["geometry"] for key, line in active["lines"].items() if not detail or key in focus])
    lo, hi = extent.min(axis=0) - .009, extent.max(axis=0) + .009
    views = [(previous, "central"), (active, code)] if compare else [(active, code)]
    fig, axes = plt.subplots(1, len(views), squeeze=False, figsize=(15.8, 8.1) if compare else (10.4, 9.1),
                             gridspec_kw={"left": .045, "right": .98, "bottom": .15, "top": .85, "wspace": .06})
    fig.patch.set_facecolor(paper)
    title = "Ring interchanges and Tigris crossings" if detail else "Baghdad metropolitan railway"
    fig.text(.045, .942, title, color=ink, fontsize=26, weight="bold")
    fig.text(.046, .898, "Two direct crossings connect the Tigris banks and both metropolitan rings",
             color="#486069", fontsize=13)
    landmarks = record["coverage"]["worldpop-2026"][code]["destinations_on_foot_to_ring"]
    for ax, (network, key) in zip(axes[0], views, strict=True):
        ax.set_facecolor(land)
        ax.add_collection(PatchCollection([Polygon(points, closed=True) for points in water],
                                           facecolor="#b4d7df", edgecolor="none", zorder=1))
        ax.add_collection(LineCollection(rivers, colors="#69a6b8", linewidths=1.0, zorder=1.2))
        ax.add_collection(LineCollection(roads, colors="#aba294", linewidths=.32, alpha=.36, zorder=2))
        for line_id, line in network["lines"].items():
            xy = np.array(line["geometry"]).T
            color = names.get(line_id, "#879090")
            on_focus = line_id in names
            if on_focus:
                ax.plot(*xy, color=paper, linewidth=5, zorder=4)
            ax.plot(*xy, color=color, linewidth=2.85 if on_focus else .88,
                    alpha=1 if on_focus else .68, zorder=5 if on_focus else 3)
        ordinary = [row["coordinates"] for site, row in network["stations"].items() if site not in calls]
        ax.scatter(*np.array(ordinary).T, s=2.2, color="#536768", alpha=.58, zorder=3.8)
        for i, trial in enumerate(proofs):
            if key == code:
                path = active["lines"][trial["id"]]["geometry"]
                for ring in ("M09", "M15"):
                    points = np.array([active["stations"][site]["coordinates"] for site in trial["ring_interchanges"][ring]])
                    ax.scatter(*points.T, s=48, linewidths=1.35, facecolors=paper, edgecolors=names[ring], zorder=7)
                crossing = np.mean(trial["mapped_bridge_approaches"], axis=0)
                ax.scatter(*crossing, s=75, linewidths=1.35, marker="D",
                           facecolors=names[trial["id"]], edgecolors=paper, zorder=8)
                end = min((path[0], path[-1]), key=lambda point: point[0])
                ax.annotate(trial["id"], end, xytext=(6, 5 + 6 * i), textcoords="offset points", color=names[trial["id"]],
                            fontsize=9, weight="bold", bbox={"fc": paper, "ec": "none", "pad": 1}, zorder=9)
        ax.scatter(*np.array([row["coordinates"] for row in landmarks.values()]).T,
                   s=22, marker="*", color=ink, alpha=.65, zorder=6)
        ax.set(xlim=(lo[0], hi[0]), ylim=(lo[1], hi[1]),
               aspect=holistic_network.LOCAL_METRES[1] / holistic_network.LOCAL_METRES[0])
        ax.xaxis.set_major_locator(NullLocator())
        ax.yaxis.set_major_locator(NullLocator())
        for spine in ax.spines.values():
            spine.set_color("#c9c3b7")
        stats = record["summary"][key]
        title = "Earlier central-ring comparison" if key == "central" else "Active through-route proposal"
        ax.set_title(f"{title}  ·  {stats['metro_walk_1300_pct']:.2f}% walk coverage",
                     loc="left", fontsize=12, weight="bold", color=ink, pad=9)
    handles = [Line2D([], [], color=names[key], lw=2.5, label=label) for key, label in (
        ("M09", "Outer ring"), ("M15", "Inner ring"), ("C1", "Airport"), *[(row["id"], row["id"]) for row in proofs])]
    handles += [Line2D([], [], color=ink, marker="D", lw=0, label="Tigris crossing"),
                Line2D([], [], color=ink, marker="o", markerfacecolor=paper, lw=0, label="Ring transfer")]
    fig.legend(handles=handles, loc="lower center", bbox_to_anchor=(.5, .102),
               frameon=False, ncol=len(handles), labelcolor=ink, fontsize=10)
    fig.text(.045, .061, ("Same scale in both views. " if compare else "") +
             "Walk coverage uses mapped streets, WorldPop and a 1.3 km limit.",
             color="#486069", fontsize=10)
    fig.text(.045, .035, "Basemap © OpenStreetMap contributors. Planning alignments and crossings are indicative.",
             color="#486069", fontsize=9)
    out = BytesIO()
    fig.savefig(out, dpi=165, format="png", facecolor=paper)
    plt.close(fig)
    return out.getvalue()


def _replace_block(content, marker, value):
    start, end = f"<!-- {marker} -->", f"<!-- end {marker} -->"
    pattern = re.compile(f"({re.escape(start)}).*?({re.escape(end)})", re.S)
    replaced, count = pattern.subn(lambda match: f"{match[1]}\n\n{value}\n\n{match[2]}", content)
    if count != 1:
        raise ValueError(f"Expected one {marker} block")
    return replaced


def readers(record):
    civil, system, beam = (record[key] for key in ("civil", "cost", "beam_schedule"))
    q, cost, service, power = civil["quantities"], system["cost_cases"], system["service"], system["power"]
    headline = (
        f"**Current metropolitan budget case.** {q['unique_guideway_km']:,.2f} km of distinct mapped guideway, "
        f"{q['double_track_km']:,.2f} running-track km and {q['station_sites']} station sites. "
        f"The base installed planning allowance is **US$\u00a0{cost['base']['installed_planning_usd_m']/1000:.2f}bn**, "
        f"with low and high cases of US$\u00a0{cost['low']['installed_planning_usd_m']/1000:.2f}bn and "
        f"US$\u00a0{cost['high']['installed_planning_usd_m']/1000:.2f}bn. The standard casting, haul and erection envelope "
        f"uses {civil['workforce']['paid_deck_and_casting_hours']/1e6:.2f} million paid hours. "
        "[Quantities, labour and costs](STRAIGHT-THROUGH-DELIVERY.md) · [Network study and map](STRAIGHT-THROUGH-NETWORK.md)"
    ).replace("\u00a0", "")
    cases = ("low", "base", "high")
    curves = sum(row["girders"] for name, row in beam["by_family"].items() if "curved_ugirder" in name)
    val = lambda field: " | ".join(f"US$ {cost[case][field]/1000:.2f}bn" for case in cases)
    proposal = (
        "The two screened through services cross the Tigris and run from beyond one side of the outer ring to "
        "beyond the other. Both connect to the inner and outer rings at shared passenger stations. "
        "The new railway bridges follow mapped road bridge approaches and require their own designs. "
        f"The two-track geometry inventory identifies **{curves:,} candidate curved girder pieces** and "
        f"{beam['totals']['held_route_length_m']/1000:.2f} service-route km of station, water, turnout, shared running "
        "or bend and closure interfaces needing further geometry.\n\n"
        "| 2026 planning scope | Low | Base | High |\n|---|---:|---:|---:|\n"
        f"| Installed allowance | {val('installed_planning_usd_m')} |\n"
        f"| Annual operation | {val('annual_operations_total_usd_m')} |\n"
        f"| 30-year present cost | {val('whole_life_present_usd_m')} |\n\n"
        f"The six-minute operating allowance needs {service['fleet_trainsets']:,} trainsets including reserves, "
        f"{power['nominal_supply_sites']} nominal supply sites and {power['annual_grid_gwh']:,.1f} GWh per year. "
        "The standard erection, special beam and full operating schedules show their own included work. "
        "The project opening date remains open pending the complete route and construction programme. "
        "[Delivery programme](STRAIGHT-THROUGH-DELIVERY.md) · [Beam designs and work orders]"
        "(engineering/mechanical/civil/CURVED-BEAM-PROGRAMME.md)"
    ).replace("\u00a0", "")
    files = {}
    for filename in ("README.md", "PROPOSAL.md"):
        path = study.CITY / filename
        content = _replace_block(path.read_text(), "current housing budget", headline)
        if filename == "PROPOSAL.md":
            content = _replace_block(content, "current route programme", proposal)
        files[path] = content.encode()
    return files


def outputs(record, networks, context):
    selected = record["display_trial"]
    data = holistic_network.geojson(networks[selected])
    data.update(publication_id=record["publication_id"], trial=selected, walking_threshold_m=study.central.WALK_NEW)
    style = _style(record)
    for feature in data["features"]:
        props = feature["properties"]
        if props["kind"] == "line":
            code = props["line_id"]
            props.update(stroke=style.get(code, "#879090"), route_role=next(
                (role for role, row in record["layouts"][selected]["hierarchy"].items()
                 if isinstance(row, dict) and code in row["line_ids"]), "retained"),)
    for row in record["approved_through"][selected]:
        data["features"].append({"type": "Feature", "geometry": {"type": "LineString",
                                                               "coordinates": row["mapped_bridge_approaches"]},
                                 "properties": {"kind": "mapped-tigris-approach", "line_id": row["id"]}})
    beam = record["beam_schedule"]
    return {study.REPORT: report(record).encode(), study.DELIVERY: delivery_report(record).encode(),
            study.RECORD: central_access.encode(study.public_record(record)), study.GEOJSON: central_access.encode(data),
            study.MAP: draw(record, networks, context), study.COMPARISON_MAP: draw(record, networks, context, compare=True),
            study.DETAIL_MAP: draw(record, networks, context, detail=True),
            study.BEAM_PLAN: beam_report(beam).encode(), study.BEAM_CSV: beam_csv(beam),
            study.BEAM_DRAWING: alignment_beams.render_svg(beam).encode(),
            study.BEAM_CAD: alignment_beams.render_dxf(beam).encode(),
            study.BEAM_DATA: gzip.compress(central_access.encode(beam), mtime=0)}


def _compare_or_write(generated, target, *, check, map_files):
    for path, data in generated.items():
        destination = target / path.relative_to(study.CITY)
        if check:
            current = destination.read_bytes()
            same = central_access.map_pixels_match(current, data) if path in map_files else current == data
            if not same:
                raise SystemExit(f"Regenerate the Baghdad network publication. {path.name} differs.")
        else:
            write(destination, data)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--publish", action="store_true")
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--output", type=Path)
    parser.add_argument("--legacy", action="store_true", help="Reproduce the historical costed housing network")
    args = parser.parse_args()
    target = args.output or study.CITY
    with disk_reservation(central_access.ROOT, target, "Baghdad network, beam work orders and engineering publication", 160 << 20):
        if args.legacy:
            record, context = holistic_map.evaluate()
            generated = holistic_map.outputs(record, context)
            map_files = {holistic_map.MAP_FILE}
        else:
            record, networks, context = study.evaluate(study.central.previous.wider.grid.BASELINE)
            generated = outputs(record, networks, context)
            if args.output is None:
                generated.update(readers(record))
            map_files = {study.MAP, study.COMPARISON_MAP, study.DETAIL_MAP}
        _compare_or_write(generated, target, check=args.check, map_files=map_files)
    print(record["publication_id"])


if __name__ == "__main__":
    main()
